from toontown.shader.FilterPipeline import FilterPipeline
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class ToontownShaders:
    def __init__(self):
        # we should check if ToontownShaders breaks with
        # textures-power-2 set to false
        self.filterPipeline = FilterPipeline(base.win, base.cam)
        self.desaturation = None
        self.cutout = None
        self.filmNoise = None
        self.vignette = None
        self.lensdistortion = None
        self.scanlines = None
        self.posterization = None
        self.pixelization = None
        self.viewglow = None
        self.lut = None

        self.blackAndWhite = False
        self.triggered = False
        self.triggeredActive = False
        self.scanlinesActive = False
        self.posterizationActive = False
        self.pixelizationActive = False
        self.viewglowActive = False
        self.lensdistortionActive = False
        self.cutoutActive = False

        self.notify.debug("Initialized ToontownShaders")

    def toggleBlackAndWhite(self):
        if not self.blackAndWhite:
            self.setDesaturation(1)
            # self.setFilmNoise(1)  # Disabled for now due to community request
            self.setVignette(1)
            self.blackAndWhite = True
        else:
            self.setDesaturation(0)
            # self.setFilmNoise(0)  # Disabled for now due to community request
            self.setVignette(0)
            self.blackAndWhite = False

    def setBlackAndWhite(self, option):
        if option and not self.blackAndWhite:
            self.setDesaturation(1)
            # self.setFilmNoise(1)  # Disabled for now due to community request
            self.setVignette(1)
            self.blackAndWhite = True
        elif not option and self.blackAndWhite:
            self.setDesaturation(0)
            # self.setFilmNoise(0)  # Disabled for now due to community request
            self.setVignette(0)
            self.blackAndWhite = False
            
    def toggleTrigger(self):
        if not self.triggeredActive:
            self.setTriggered(1)
            self.triggeredActive = True
        else:
            self.setTriggered(0)
            self.triggeredActive = False

    def toggleScanLines(self):
        self.setScanLines(not self.scanlinesActive)

    def togglePosterization(self):
        self.setPosterization(not self.posterizationActive)

    def togglePixelization(self):
        self.setPixelization(not self.pixelizationActive)

    def toggleViewGlow(self):
        self.setViewGlow(not self.viewglowActive)

    def toggleLensDistortion(self):
        self.setLensDistortion(not self.lensdistortionActive)

    def toggleCutout(self):
        self.setCutoutFilter(not self.cutoutActive)

    def setDesaturation(self, enabled = False):
        if enabled:
            from toontown.shader.builtin.Desaturation import Desaturation
            self.desaturation = Desaturation()
            self.filterPipeline.addFilterInstance(self.desaturation)
            base.activeEffects.append('desaturate')
        else:
            self.filterPipeline.removeFilterInstance(self.desaturation)
            self.desaturation = None
            if 'desaturate' in base.activeEffects:
                base.activeEffects.remove('desaturate')


    def setFilmNoise(self, enabled = False, mode = "monochrome", strength = 0.05, dynamic = True):
        if enabled:
            if not self.scanlinesActive:
                from toontown.shader.builtin.FilmNoise import FilmNoise
                self.filmNoise = FilmNoise()
                self.filterPipeline.addFilterInstance(self.filmNoise)
                base.activeEffects.append('filmNoise')
            self.filmNoise.mode = mode
            self.filmNoise.strength = strength
            self.filmNoise.dynamic = dynamic
        else:
            self.filterPipeline.removeFilterInstance(self.filmNoise)
            self.filmNoise = None
            if 'filmNoise' in base.activeEffects:
                base.activeEffects.remove('filmNoise')

    def setVignette(self, enabled = False):
        if enabled:
            from toontown.shader.builtin.MiscFilters import Vignetting
            self.vignette = Vignetting()
            self.filterPipeline.addFilterInstance(self.vignette)
            base.activeEffects.append('vignette')
        else:
            self.filterPipeline.removeFilterInstance(self.vignette)
            self.vignette = None
            if 'vignette' in base.activeEffects:
                base.activeEffects.remove('vignette')
                
    def setTriggered(self, enabled = False):
        if enabled:
            from toontown.shader.builtin.TriggerRed import TriggerRed
            self.triggered = TriggerRed()
            self.filterPipeline.addFilterInstance(self.triggered)
            base.activeEffects.append('triggered')
        else:
            self.filterPipeline.removeFilterInstance(self.triggered)
            self.triggered = None
            if 'triggered' in base.activeEffects:
                base.activeEffects.remove('triggered')

    def setScanLines(self, enabled = False, strength=0.5, lineThickness=1, dynamicFlip=False, bandStrength=0.1, bandSpeed=0.75, bandSize=1.0, enableTint=False):
        if enabled:
            if not self.scanlinesActive:
                from toontown.shader.builtin.Scanlines import Scanlines
                self.scanlines = Scanlines()
                self.filterPipeline.addFilterInstance(self.scanlines)
                base.activeEffects.append('scanlines')
                self.scanlinesActive = True
            self.scanlines.strength = strength
            self.scanlines.lineThickness = lineThickness
            self.scanlines.dynamicFlip = dynamicFlip
            self.scanlines.bandStrength = bandStrength
            self.scanlines.bandSpeed = bandSpeed
            self.scanlines.bandSize = bandSize
            self.scanlines.enableTint = enableTint
        else:
            self.filterPipeline.removeFilterInstance(self.scanlines)
            self.scanlines = None
            if 'scanlines' in base.activeEffects:
                base.activeEffects.remove('scanlines')
            self.scanlinesActive = False

    def setPosterization(self, enabled = False, quantization=8, gamma=2.2):
        if enabled:
            if not self.posterizationActive:
                from toontown.shader.builtin.MiscFilters import Posterization
                self.posterization = Posterization()
                self.filterPipeline.addFilterInstance(self.posterization)
                base.activeEffects.append('posterization')
                self.posterizationActive = True
            self.posterization.quantization = quantization
            self.posterization.gamma = gamma
        else:
            self.filterPipeline.removeFilterInstance(self.posterization)
            self.posterization = None
            if 'posterization' in base.activeEffects:
                base.activeEffects.remove('posterization')
            self.posterizationActive = False

    def setPixelization(self, enabled = False, sizex=4, sizey=4):
        if enabled:
            if not self.pixelizationActive:
                from toontown.shader.builtin.MiscFilters import Pixelization
                self.pixelization = Pixelization()
                self.filterPipeline.addFilterInstance(self.pixelization)
                base.activeEffects.append('pixelization')
                self.pixelizationActive = True
            self.pixelization.sizex = sizex
            self.pixelization.sizey = sizey
        else:
            self.filterPipeline.removeFilterInstance(self.pixelization)
            self.pixelization = None
            if 'pixelization' in base.activeEffects:
                base.activeEffects.remove('pixelization')
            self.pixelizationActive = False

    def setViewGlow(self, enabled = False):
        if enabled and not self.viewglowActive:
            from toontown.shader.builtin.MiscFilters import ViewGlow
            self.viewglow = ViewGlow()
            self.filterPipeline.addFilterInstance(self.viewglow)
            base.activeEffects.append('viewglow')
            self.viewglowActive = True
        else:
            self.filterPipeline.removeFilterInstance(self.viewglow)
            self.viewglow = None
            if 'viewglow' in base.activeEffects:
                base.activeEffects.remove('viewglow')
            self.viewglowActive = False

    def setLensDistortion(self, enabled = False, barrelFuzzy=False, barrelDistort=0.05, useChromaDistort=True, chromaDistort=(0.01, -0.005, -0.02), numsamples=16):
        # todo: ability to retain previous config settings for feasibility when toggling on/off
        if enabled:
            if not self.lensdistortionActive:
                from toontown.shader.builtin.LensDistortion import LensDistortion
                self.lensdistortion = LensDistortion()
                self.filterPipeline.addFilterInstance(self.lensdistortion)
                base.activeEffects.append('lensdistortion')
                self.lensdistortionActive = True
            self.lensdistortion.barrelFuzzy = barrelFuzzy
            self.lensdistortion.barrelDistort = barrelDistort
            self.lensdistortion.useChromaDistort = useChromaDistort
            if useChromaDistort:
                self.lensdistortion.chromaDistort = chromaDistort
            self.lensdistortion.numsamples = numsamples
        else:
            self.filterPipeline.removeFilterInstance(self.lensdistortion)
            self.lensdistortion = None
            if 'lensdistortion' in base.activeEffects:
                base.activeEffects.remove('lensdistortion')
            self.lensdistortionActive = False

    def setChromaDistort(self, r, g, b):
        if not self.lensdistortionActive:
            return
        self.lensdistortion.chromaDistort = (r, g, b)


    def setCutoutFilter(self, enabled=False, bbox=(0.0, 1.0, 0.0, 1.0), shape="rectangle", maskAwayWhich = "outside", maskColor=(0.0, 0.0, 0.0, 1.0), blendMode = "rgba", strength=1.0, smoothingRadius=0.02):
        if enabled:
            if not self.cutoutActive:
                from toontown.shader.builtin.Cutout import Cutout
                self.cutout = Cutout()
                self.filterPipeline.addFilterInstance(self.cutout)
                base.activeEffects.append('cutout')
                self.cutoutActive = True
            self.cutout.bbox = bbox
            self.cutout.shape = shape
            self.cutout.maskAwayWhich = maskAwayWhich
            self.cutout.maskColor = maskColor
            self.cutout.blendMode = blendMode
            self.cutout.strength = strength
            self.cutout.smoothingRadius = smoothingRadius
        else:
            self.filterPipeline.removeFilterInstance(self.cutout)
            self.cutout = None
            if 'cutout' in base.activeEffects:
                base.activeEffects.remove('cutout')
            self.cutoutActive = False

    def test(self):
        from toontown.shader.builtin.MiscFilters import LookupTest
        self.lut = LookupTest()
        self.filterPipeline.addFilterInstance(self.lut)
        base.activeEffects.append('lut')
        # base.effectMgr.test()

