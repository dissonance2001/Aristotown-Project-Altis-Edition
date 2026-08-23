"""Backward compatibility layer for the postprocessing filter system.

For documentation on the filters (what they do and their parameters), see the individual filter modules,
and MiscFilters for a collection of short, simple filters.

To list all existing filters, which file they are defined in, and their default render order,
see the developer tool ListAllFilters.py.

For scripts targeted at Panda 1.9.0 or later, FilterPipeline is the recommended API for applying postprocessing.

The FilterPipeline API is more flexible, and makes it possible to code custom filters that
plug into the pipeline (working together with the filters already provided in Panda).

If you want to apply existing postprocessing filters to your scene, see FilterPipeline.

If you want to implement new filters of your own, see Filter (and the various existing filters for working examples).

"""

from __future__ import print_function

import sys
from functools import wraps

from toontown.shader.FilterPipeline import FilterPipeline

from .AmbientOcclusion import AmbientOcclusion
from .Bloom import Bloom
from .BlurSharpen import BlurSharpen
from .CartoonInkThick import CartoonInkThick
from .CartoonInkThin import CartoonInkThin
from .Cutout import Cutout
from .Desaturation import Desaturation
from .FilmNoise import FilmNoise
from .LensDistortion import LensDistortion
from .LensFlare import LensFlare
from .LocalReflection import LocalReflection
from .Scanlines import Scanlines
from .VolumetricLightingCompositor import VolumetricLightingCompositor
from .VolumetricLighting import VolumetricLighting

from .MiscFilters import ViewGlow, ColorInversion, GammaAdjust, Tint, CartoonInkClassic, AntialiasFXAA, Vignetting, \
    Pixelization, Posterization

from toontown.shader import FilterUtils


# Decorator functions to implement exception catching for the old API stubs.
#
# The old API did not raise exceptions. The set***() methods returned True on success, False on error.
# The del***() methods always returned True. This is emulated here.
#
# On error, we dump the exception message and a traceback to stderr,
# to provide the user at least some way of seeing the error message.
#
def oldSetFilter(func):
    """Exception-catching decorator function for old API set***() methods. Internal."""

    @wraps(func)
    def compatibilityGlue(*args, **kwargs):  # this function name can be seen in the exception stack trace.
        try:
            func(*args, **kwargs)
            # Apply the reconfigure immediately so that we can catch exceptions, if any occur.
            #
            # func will add a filter, or change filter parameters.
            #
            # Adding a filter will always flag the pipeline as needing a reconfigure.
            #
            # Changing parameters will flag a pipeline reconfigure, if the filter property setters
            # determine it is necessary. Also filter reconfigures might get flagged.
            #
            # When the pipeline reconfigure runs, also the filters will get their reconfigures called,
            # if needed. (There is a hack in FilterPipeline.reconfigure() to make sure this happens;
            # we cannot wait until the deferred filter reconfigures run, because we must process any
            # errors immediately - this is important to avoid introducing crashes in old apps,
            # which expect that CommonFilters raises no exceptions.)
            #
            args[0].reconfigure()  # args[0] = self (CommonFilters)
        except:
            print("\nCaught exception while setting filter; details follow.", file = sys.stderr)
            FilterUtils.dumpExceptionTrace(file = sys.stderr)
            print("Continuing.\n", file = sys.stderr)
            return False
        return True

    return compatibilityGlue


def oldDelFilter(func):
    """Exception-catching decorator function for old API del***() methods. Internal."""

    @wraps(func)
    def compatibilityGlue(*args, **kwargs):  # this function name can be seen in the exception stack trace.
        try:
            func(*args, **kwargs)
            # Apply the reconfigure immediately so that we can catch exceptions, if any occur.
            #
            # func will remove a filter, which will flag the pipeline as needing a reconfigure.
            # In the case where the filter has already been removed (self.appropriateFilterInstance is None),
            # no _needsCompile flag will be set, and reconfigure() skips the recompile.
            #
            args[0].reconfigure()  # args[0] = self (CommonFilters)
        except:
            print("\nCaught exception while removing filter; details follow.", file = sys.stderr)
            FilterUtils.dumpExceptionTrace(file = sys.stderr)
            print("Continuing.\n", file = sys.stderr)
        return True

    return compatibilityGlue


class CommonFilters(FilterPipeline):
    """This class adds a backward-compatible API (1.8.x) on top of the FilterPipeline API (introduced in 1.9.0)."""

    # TODO: add deprecation warning to __init__()?
    def __init__(self, win, cam):
        """Constructor.

        win and cam like in FilterManager; see also FilterPipeline, which uses the same parameters.

        """
        name = "(CommonFilters) instance at 0x%x" % id(self)
        super(CommonFilters, self).__init__(win, cam, name)

        self.ambientOcclusion = None
        self.bloom = None
        self.blurSharpen = None
        self.cartoonInk = None
        self.colorInversion = None
        self.gammaAdjust = None  # added in CVS between 1.8.1 and 1.9.0
        self.viewGlow = None
        self.volumetricLighting = None
        #        self.vlBloomPreproc     = None  # preprocess filter for VolumetricLighting

        # new filters in 1.9.0, not in old CommonFilters
        self.antialias = None
        self.cutout = None
        self.desaturation = None
        self.filmNoise = None
        self.lensDistortion = None
        self.lensFlare = None
        self.localReflection = None
        self.scanlines = None
        self.tint = None
        self.vignetting = None
        self.pixelization = None
        self.posterization = None

    # Here we create the filter instances using their default stageName and sort.
    #
    # This old API emulation supports only one instance of each type.
    # For more general setups, the new API should be used.

    # HalfPixelShift is not an fshader function like the other filters, so it has no corresponding
    # Filter object to represent it. Instead, it is a FilterPipeline option that modifies the
    # generated vshader of the first FilterStage in the pipeline.
    #
    @oldSetFilter
    def setHalfPixelShift(self):
        self.halfPixelShift = True

    @oldDelFilter
    def delHalfPixelShift(self):
        self.halfPixelShift = False

    # All the other filters are fshader functions with corresponding Filter objects.

    @oldSetFilter
    def setAmbientOcclusion(self, numsamples = 16, radius = 0.05, amount = 2.0, strength = 0.01, falloff = 0.000002):
        if self.ambientOcclusion is None:
            self.ambientOcclusion = AmbientOcclusion()
            self.addFilterInstance(self.ambientOcclusion)
        self.ambientOcclusion.numsamples = numsamples
        self.ambientOcclusion.radius = radius
        self.ambientOcclusion.amount = amount
        self.ambientOcclusion.strength = strength
        self.ambientOcclusion.falloff = falloff

    @oldDelFilter
    def delAmbientOcclusion(self):
        if self.ambientOcclusion is not None:
            self.removeFilterInstance(self.ambientOcclusion)
            self.ambientOcclusion = None

    @oldSetFilter
    def setBloom(self, blend = (0.3, 0.4, 0.3, 0.0), mintrigger = 0.6, maxtrigger = 1.0, desat = 0.6, intensity = 1.0,
                 size = "medium"):
        if self.bloom is None:
            self.bloom = Bloom()
            self.addFilterInstance(self.bloom)
        self.bloom.blend = blend
        self.bloom.mintrigger = mintrigger
        self.bloom.maxtrigger = maxtrigger
        self.bloom.desat = desat
        self.bloom.intensity = intensity
        self.bloom.size = size

    @oldDelFilter
    def delBloom(self):
        if self.bloom is not None:
            self.removeFilterInstance(self.bloom)
            self.bloom = None

    @oldSetFilter
    def setBlurSharpen(self, amount = 0.0, size = "medium", source = "color"):
        if self.blurSharpen is None:
            self.blurSharpen = BlurSharpen()
            self.addFilterInstance(self.blurSharpen)
        self.blurSharpen.amount = amount
        self.blurSharpen.size = size
        self.blurSharpen.source = source

    @oldDelFilter
    def delBlurSharpen(self):
        if self.blurSharpen is not None:
            self.removeFilterInstance(self.blurSharpen)
            self.blurSharpen = None

    @oldSetFilter
    def setCartoonInk(self, separation = 1.0, color = (0.0, 0.0, 0.0, 1.0)):
        """This uses the classic inker for backward compatibility."""
        # These filters are alternatives.
        if isinstance(self.cartoonInk, CartoonInkThin) or isinstance(self.cartoonInk, CartoonInkThick):
            self.removeFilterInstance(self.cartoonInk)
            self.cartoonInk = None
        if self.cartoonInk is None:
            self.cartoonInk = CartoonInkClassic()
            self.addFilterInstance(self.cartoonInk)
        self.cartoonInk.separation = separation
        self.cartoonInk.color = color

    @oldDelFilter
    def delCartoonInk(self):
        if self.cartoonInk is not None:
            self.removeFilterInstance(self.cartoonInk)
            self.cartoonInk = None

    # The gamma adjust filter was introduced in the development tree between releases 1.8.1 and 1.9.0.
    @oldSetFilter
    def setGammaAdjust(self, gamma = 2.0):
        if self.gammaAdjust is None:
            self.gammaAdjust = GammaAdjust()
            self.addFilterInstance(self.gammaAdjust)
        self.gammaAdjust.gamma = gamma

    @oldDelFilter
    def delGammaAdjust(self):
        if self.gammaAdjust is not None:
            self.removeFilterInstance(self.gammaAdjust)
            self.gammaAdjust = None

    @oldSetFilter
    def setInverted(self):
        if self.colorInversion is None:
            self.colorInversion = ColorInversion()
            self.addFilterInstance(self.colorInversion)

    @oldDelFilter
    def delInverted(self):
        if self.colorInversion is not None:
            self.removeFilterInstance(self.colorInversion)
            self.colorInversion = None

    @oldSetFilter
    def setViewGlow(self):
        if self.viewGlow is None:
            self.viewGlow = ViewGlow()
            self.addFilterInstance(self.viewGlow)

    @oldDelFilter
    def delViewGlow(self):
        if self.viewGlow is not None:
            self.removeFilterInstance(self.viewGlow)
            self.viewGlow = None

    @oldSetFilter
    def setVolumetricLighting(self, caster, numsamples = 32, density = 5.0, decay = 0.1, exposure = 0.1,
                              source = "color"):
        """This sets only VolumetricLightingCompositor; see setVolumetricLightingAllInOne() for an all-in-one solution.

        The texture name referred by the "source" parameter, if it is not "color", must be made available
        by another filter placed earlier in the same logical stage. (E.g. a Bloom instance provides
        a "bloomOutput" texture which can be used here.)

        The default source "color" just radially blurs the image, with the blur centered on the
        caster's screen position.

        """
        # These filters are alternatives.
        if isinstance(self.volumetricLighting, VolumetricLighting):
            self.removeFilterInstance(self.volumetricLighting)
            self.volumetricLighting = None
        if self.volumetricLighting is None:
            self.volumetricLighting = VolumetricLightingCompositor()
            self.addFilterInstance(self.volumetricLighting)

        #        if source == "bloomOutput":
        #            if self.vlBloomPreproc is None:
        #                self.vlBloomPreproc = Bloom()  # TODO good default settings
        #                self.addFilterInstance(self.vlBloomPreproc)
        #                self.vlBloomPreproc.stageName    = self.volumetricLighting.stageName  # same render pass
        #                self.vlBloomPreproc.sort         = self.volumetricLighting.sort - 1   # hope this slot is free
        #                self.vlBloomPreproc.enableRender = False

        self.volumetricLighting.caster = caster
        self.volumetricLighting.source = source
        self.volumetricLighting.numsamples = numsamples
        self.volumetricLighting.density = density
        self.volumetricLighting.decay = decay
        self.volumetricLighting.exposure = exposure

    @oldDelFilter
    def delVolumetricLighting(self):
        if self.volumetricLighting is not None:
            self.removeFilterInstance(self.volumetricLighting)
            self.volumetricLighting = None

    #        if self.vlBloomPreproc is not None:
    #            self.removeFilterInstance(self.vlBloomPreproc)
    #            self.vlBloomPreproc = None

    # The following filters didn't exist in the old CommonFilters.
    #
    # We provide these functions to facilitate easily using them in old scripts (with very minor modifications
    # to existing script code), although the recommended way is to use the more flexible FilterPipeline API.

    @oldSetFilter
    def setVolumetricLightingAllInOne(self, caster, numsamples = 32, density = 5.0, decay = 0.1, exposure = 0.1,
                                      bloomBlend = (0.3, 0.4, 0.3, 0.0), mintrigger = 0.6, maxtrigger = 1.0,
                                      desat = 0.6, intensity = 1.0, bloomSize = "medium"):
        """This sets an all-in-one VolumetricLighting filter.

        This filter generates its own glow texture via its own instance of bloom; it does not publish
        a "source" parameter.

        Note that the default parameter values are still bad; for good ones, see
        the docstrings of VolumetricLightingCompositor.

        """
        # These filters are alternatives.
        if isinstance(self.volumetricLighting, VolumetricLightingCompositor):
            self.removeFilterInstance(self.volumetricLighting)
            self.volumetricLighting = None
        if self.volumetricLighting is None:
            self.volumetricLighting = VolumetricLighting()
            self.addFilterInstance(self.volumetricLighting)

        self.volumetricLighting.bloomBlend = bloomBlend
        self.volumetricLighting.mintrigger = mintrigger
        self.volumetricLighting.maxtrigger = maxtrigger
        self.volumetricLighting.desat = desat
        self.volumetricLighting.intensity = intensity
        self.volumetricLighting.bloomSize = bloomSize
        self.volumetricLighting.caster = caster
        self.volumetricLighting.numsamples = numsamples
        self.volumetricLighting.density = density
        self.volumetricLighting.decay = decay
        self.volumetricLighting.exposure = exposure

    @oldDelFilter
    def delVolumetricLightingAllInOne(self):
        if self.volumetricLighting is not None:
            self.removeFilterInstance(self.volumetricLighting)
            self.volumetricLighting = None

    @oldSetFilter
    def setScanlines(self, strength = 0.5, lineThickness = 1, dynamicFlip = False, top = True, bandStrength = 0.1,
                     bandSpeed = 0.75, bandSize = 1.0, enableTint = False):
        if self.scanlines is None:
            self.scanlines = Scanlines()
            self.addFilterInstance(self.scanlines)
        field = Scanlines.FIELD_TOP if top == True else Scanlines.FIELD_BOTTOM
        self.scanlines.strength = strength
        self.scanlines.lineThickness = lineThickness
        self.scanlines.dynamicFlip = dynamicFlip
        self.scanlines.field = field
        self.scanlines.bandStrength = bandStrength
        self.scanlines.bandSpeed = bandSpeed
        self.scanlines.bandSize = bandSize
        self.scanlines.enableTint = enableTint

    @oldDelFilter
    def delScanlines(self):
        if self.scanlines is not None:
            self.removeFilterInstance(self.scanlines)
            self.scanlines = None

    @oldSetFilter
    def setTint(self, mode = "fade", color = (1, 1, 1, 1), strength = 1.0):
        if self.tint is None:
            self.tint = Tint()
            self.addFilterInstance(self.tint)
        self.tint.mode = mode
        self.tint.color = color
        self.tint.strength = strength

    @oldDelFilter
    def delTint(self):
        if self.tint is not None:
            self.removeFilterInstance(self.tint)
            self.tint = None

    @oldSetFilter
    def setLensDistortion(self, barrelDistort = 0.05, barrelFuzzy = False, useChromaDistort = True,
                          chromaDistort = (0.01, -0.005, -0.02), numsamples = 16):
        if self.lensDistortion is None:
            self.lensDistortion = LensDistortion()
            self.addFilterInstance(self.lensDistortion)
        self.lensDistortion.barrelDistort = barrelDistort
        self.lensDistortion.barrelFuzzy = barrelFuzzy
        self.lensDistortion.useChromaDistort = useChromaDistort
        self.lensDistortion.chromaDistort = chromaDistort
        self.lensDistortion.numsamples = numsamples

    @oldDelFilter
    def delLensDistortion(self):
        if self.lensDistortion is not None:
            self.removeFilterInstance(self.lensDistortion)
            self.lensDistortion = None

    @oldSetFilter
    def setLensFlare(self, threshold = (0.7, 0.7, 0.7), brightness = 1.0, numsamples = 5, haloWidth = 0.3,
                     dispersal = 0.35, chromaDistort = (0.005, -0.005, 0)):
        if self.lensFlare is None:
            self.lensFlare = LensFlare()
            self.addFilterInstance(self.lensFlare)
        self.lensFlare.threshold = threshold
        self.lensFlare.brightness = brightness
        self.lensFlare.numsamples = numsamples
        self.lensFlare.haloWidth = haloWidth
        self.lensFlare.dispersal = dispersal
        self.lensFlare.chromaDistort = chromaDistort

    @oldDelFilter
    def delLensFlare(self):
        if self.lensFlare is not None:
            self.removeFilterInstance(self.lensFlare)
            self.lensFlare = None

    @oldSetFilter
    def setDesaturation(self, mode = "basic", luma = "HDTV", strength = 1.0, tintColor = (1.0, 1.0, 1.0),
                        bandpassColor = (1.0, 0.0, 0.0), bandpassQ = 0.25):
        if self.desaturation is None:
            self.desaturation = Desaturation()
            self.addFilterInstance(self.desaturation)
        self.desaturation.mode = mode
        self.desaturation.luma = luma
        self.desaturation.strength = strength
        self.desaturation.tintColor = tintColor
        self.desaturation.bandpassColor = bandpassColor
        self.desaturation.bandpassQ = bandpassQ

    @oldDelFilter
    def delDesaturation(self):
        if self.desaturation is not None:
            self.removeFilterInstance(self.desaturation)
            self.desaturation = None

    @oldSetFilter
    def setCartoonInkThin(self, color = (0.0, 0.0, 0.0, 1.0), numsamples = 12, detectDepth = True, cutoffDepth = 0.0001,
                          detectNormals = True, cutoffNormals = 0.02, voteThreshold = 1.0, weightPower = 2):
        # These filters are alternatives.
        if isinstance(self.cartoonInk, CartoonInkClassic) or isinstance(self.cartoonInk, CartoonInkThick):
            self.removeFilterInstance(self.cartoonInk)
            self.cartoonInk = None
        if self.cartoonInk is None:
            self.cartoonInk = CartoonInkThin()
            self.addFilterInstance(self.cartoonInk)
        self.cartoonInk.color = color
        self.cartoonInk.numsamples = numsamples
        self.cartoonInk.detectDepth = detectDepth
        self.cartoonInk.cutoffDepth = cutoffDepth
        self.cartoonInk.detectNormals = detectNormals
        self.cartoonInk.cutoffNormals = cutoffNormals
        self.cartoonInk.voteThreshold = voteThreshold
        self.cartoonInk.weightPower = weightPower

    @oldDelFilter
    def delCartoonInkThin(self):
        if self.cartoonInk is not None:
            self.removeFilterInstance(self.cartoonInk)
            self.cartoonInk = None

    @oldSetFilter
    def setCartoonInkThick(self, color = (0.0, 0.0, 0.0, 1.0), detectDepth = True, cutoffDepth = 0.01,
                           detectNormals = True, cutoffNormals = 0.6, separation = 1.0,
                           depthSensitiveSeparation = False, mult = (2.0, 2.0, 2.0, 0.0)):
        # These filters are alternatives.
        if isinstance(self.cartoonInk, CartoonInkClassic) or isinstance(self.cartoonInk, CartoonInkThin):
            self.removeFilterInstance(self.cartoonInk)
            self.cartoonInk = None
        if self.cartoonInk is None:
            self.cartoonInk = CartoonInkThick()
            self.addFilterInstance(self.cartoonInk)
        self.cartoonInk.color = color
        self.cartoonInk.detectDepth = detectDepth
        self.cartoonInk.cutoffDepth = cutoffDepth
        self.cartoonInk.detectNormals = detectNormals
        self.cartoonInk.cutoffNormals = cutoffNormals
        self.cartoonInk.separation = separation
        self.cartoonInk.depthSensitiveSeparation = depthSensitiveSeparation
        self.cartoonInk.mult = mult

    @oldDelFilter
    def delCartoonInkThin(self):
        if self.cartoonInk is not None:
            self.removeFilterInstance(self.cartoonInk)
            self.cartoonInk = None

    @oldSetFilter
    def setAntialiasFXAA(self):
        if self.antialias is None:
            self.antialias = AntialiasFXAA()
            self.addFilterInstance(self.antialias)

    @oldDelFilter
    def delAntialiasFXAA(self):
        if self.antialias is not None:
            self.removeFilterInstance(self.antialias)
            self.antialias = None

    @oldSetFilter
    def setVignetting(self, strength = 0.6):
        if self.vignetting is None:
            self.vignetting = Vignetting()
            self.addFilterInstance(self.vignetting)
        self.vignetting.strength = strength

    @oldDelFilter
    def delVignetting(self):
        if self.vignetting is not None:
            self.removeFilterInstance(self.vignetting)
            self.vignetting = None

    @oldSetFilter
    def setFilmNoise(self, mode = "monochrome", strength = 0.05):
        if self.filmNoise is None:
            self.filmNoise = FilmNoise()
            self.addFilterInstance(self.filmNoise)
        self.filmNoise.mode = mode
        self.filmNoise.strength = strength

    @oldDelFilter
    def delFilmNoise(self):
        if self.filmNoise is not None:
            self.removeFilterInstance(self.filmNoise)
            self.filmNoise = None

    @oldSetFilter
    def setCutout(self, boundingBox = (0.0, 1.0, 0.0, 1.0), shape = "ellipse", maskAwayWhich = "outside",
                  maskColor = (0.0, 0.0, 0.0, 1.0), blendMode = "rgba", strength = 1.0, smoothingRadius = 0.02):
        if self.cutout is None:
            self.cutout = Cutout()
            self.addFilterInstance(self.cutout)
        self.cutout.boundingBox = boundingBox
        self.cutout.shape = shape
        self.cutout.maskAwayWhich = maskAwayWhich
        self.cutout.maskColor = maskColor
        self.cutout.blendMode = blendMode
        self.cutout.strength = strength
        self.cutout.smoothingRadius = smoothingRadius

    @oldDelFilter
    def delCutout(self):
        if self.cutout is not None:
            self.removeFilterInstance(self.cutout)
            self.cutout = None

    @oldSetFilter
    def setLocalReflection(self, maxSteps = 30, stepSize = 0.005, maxDelta = 0.001, strength = 5.0,
                           blurType = "twopass", blurSize = "medium", useGlowMap = False):
        if self.localReflection is None:
            self.localReflection = LocalReflection()
            self.addFilterInstance(self.localReflection)
        self.localReflection.maxSteps = maxSteps
        self.localReflection.stepSize = stepSize
        self.localReflection.maxDelta = maxDelta
        self.localReflection.strength = strength
        self.localReflection.blurType = blurType
        self.localReflection.blurSize = blurSize
        self.localReflection.useGlowMap = useGlowMap

    @oldDelFilter
    def delLocalReflection(self):
        if self.localReflection is not None:
            self.removeFilterInstance(self.localReflection)
            self.localReflection = None

    @oldSetFilter
    def setPixelization(self, sizex = 4, sizey = 4):
        if self.pixelization is None:
            self.pixelization = Pixelization()
            self.addFilterInstance(self.pixelization)
        self.pixelization.sizex = sizex
        self.pixelization.sizey = sizey

    @oldDelFilter
    def delPixelization(self):
        if self.pixelization is not None:
            self.removeFilterInstance(self.pixelization)
            self.pixelization = None

    @oldSetFilter
    def setPosterization(self, quantization = 8, gamma = 2.2):
        if self.posterization is None:
            self.posterization = Posterization()
            self.addFilterInstance(self.posterization)
        self.posterization.quantization = quantization
        self.posterization.gamma = gamma

    @oldDelFilter
    def delPosterization(self):
        if self.posterization is not None:
            self.removeFilterInstance(self.posterization)
            self.posterization = None
