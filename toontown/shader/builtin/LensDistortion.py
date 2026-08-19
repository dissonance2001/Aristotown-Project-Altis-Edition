from panda3d.core import Vec3

from toontown.shader.Filter import Filter

LENS_DISTORT_BODY="""
// This doesn't need to be accurate, so we just improvise a formula giving qualitatively a barrel type of distortion. See
//   http://stackoverflow.com/questions/6199636/formulas-for-barrel-pincushion-distortion
//   http://sprg.massey.ac.nz/pdfs/2003_IVCNZ_408.pdf
// The important part is being radially nonlinear, so that the magnification changes as we approach the edges (and especially corners).

// Optional simulation of a low-quality lens producing a fuzzy image. 1 = on, 0 = off.
#define BARREL_FUZZY %(barrel_fuzzy)d

// negative input = barrel, positive input = pincushion
const float BARREL_DISTORT = %(k_lensdistort_barrel)s;

// Optional chromatic aberration, applied to the whole image. 1 = on, 0 = off.
#define USE_CHROMA_DISTORT %(use_chroma_distort)d

// Magnitude of chromatic aberration in each color component.
const float3 CHROMA_DISTORT = %(k_lensdistort_chroma)s;


// Compute the radius, in x and y directions, of the actually used area of the texture as measured
// from the "texture center" point specified by texpad. This is in texture coordinate units.
//
// This is usually (0.5, 0.5), but if the texture is padded, it may be less.
//
// TODO/FIXME: this could be precomputed to save some computation here, but doing that requires either
//                - modifying the FilterStage vshader to do that (maybe provide an option to register the filter as needing texradii?)
//                - access to texpad values from the Python interface, so that the filter could fill in a shader input
//                  when the shader is compiled. (May be brittle - doesn't account for window size changes, which might affect texpad.)
//
// TODO/FIXME: is texpad always < 0.5? In that case we don't need the min(), and can use texpad directly.
//
const float2 texradii = min( %(texpad_txcolor)s.xy, 1.0 - %(texpad_txcolor)s.xy );

// Vector from current pixel toward screen center.
//
// Observe that the each component of sample_vector is in -1.0 ... 1.0.
//
const float2 sample_vector = (%(texpad_txcolor)s.xy - %(texcoord_txcolor)s.xy)/texradii.xy;

const float  sample_normsq = dot(sample_vector, sample_vector);  // this is in 0...2 (and quadratic)
const float2 sample_dir    = normalize(sample_vector);

// Because this is a postprocess filter and cannot "see" the scene outside the original image,
// we zoom (linearly) to remove the need to render more data near the image edges.
//
// This is needed because the barrel distortion and chromatic aberration may push the texture lookups
// toward the edges of the image; we must have data to "push into" also at the corners.
//
// Pincushion distortion (positive values of BARREL_DISTORT) does not need the zoom, because it pushes
// the texture lookups toward the center of the image.
//
// Note that the zoom factor must reduce to 1.0 if all distortions are zero.
//
#if USE_CHROMA_DISTORT == 1
const float m = min(BARREL_DISTORT, 0.0) + min(min(min(CHROMA_DISTORT.r, CHROMA_DISTORT.g), CHROMA_DISTORT.b), 0.0);
#else
const float m = min(BARREL_DISTORT, 0.0);
#endif

const float zoom_r = (1.0 + sqrt(2.0)*m);
const float2 zoomed_texcoord = %(texpad_txcolor)s.xy + zoom_r*(%(texcoord_txcolor)s.xy - %(texpad_txcolor)s.xy);

// magnitude of maxvec is basically radius**2 (from view center), normalized so that it is 1.0 at the corners
const float2 maxvec = 0.5*sample_normsq*sample_dir;


// Apply the distortions.

#if USE_CHROMA_DISTORT == 0  &&  BARREL_FUZZY == 0

// No fuzzy barrel and no chromatic aberration. In this case we just map the pixel
// through the barrel distortion (no need to blur).
//
float4 result = tex2D( %(k_txcolor)s, zoomed_texcoord + maxvec*BARREL_DISTORT );

#else

// Distortion smoother - scan along the radial direction and blur.
//
// We weight the contributions so that objects will "spread out" radially without generating sharp edges
// in the fuzzy distortion.
//
const float2 incvec = maxvec / %(numsamples)f;  // increment vector
const float  inc    = 1.0    / %(numsamples)f;  // increment in weight profile function input

#if USE_CHROMA_DISTORT == 1  &&  BARREL_FUZZY == 0
// In this case we can compute this outside the loop.
const float2 basepos = zoomed_texcoord + maxvec*BARREL_DISTORT;
#endif

float4 result    = float4(0,0,0,1);
float  weightsum = 0.0;
for (int i = 0; i < %(numsamples)d; ++i) {
  const float s = float(i) + 0.5;
  const float2 offsetvec = incvec * s;

  // Weight profile. (Note that the summed result is automatically normalized,
  // so this defines just the shape.)
  //
  // With the above definition of s, this is symmetric when i goes from 0 to numsamples-1.
  //
  const float weight = 0.5 + sin(inc * s * 3.1415926535);

#if USE_CHROMA_DISTORT == 1  &&  BARREL_FUZZY == 1
  // fuzzy barrel effect - the image spreads out near the edges (low-quality lens, misaligned optics)
  //
  // with chromatic aberration
  //
  result.r += weight*tex2D( %(k_txcolor)s, zoomed_texcoord + offsetvec * (BARREL_DISTORT + CHROMA_DISTORT.r) ).r;
  result.g += weight*tex2D( %(k_txcolor)s, zoomed_texcoord + offsetvec * (BARREL_DISTORT + CHROMA_DISTORT.g) ).g;
  result.b += weight*tex2D( %(k_txcolor)s, zoomed_texcoord + offsetvec * (BARREL_DISTORT + CHROMA_DISTORT.b) ).b;

#elif BARREL_FUZZY == 1
  // fuzzy barrel, no chromatic aberration
  //
  result   += weight*tex2D( %(k_txcolor)s, zoomed_texcoord + offsetvec * BARREL_DISTORT );

#elif USE_CHROMA_DISTORT == 1
  // no spread in barrel effect (good-quality lens, physically correct);
  // straight lines on the view plane are radially distorted outwards
  //
  // with chromatic aberration
  //
  // In the chromatic aberration, we blur radially to make each color component simulate a wavelength *range*;
  // without the blur, we would get just 3 discrete shifted copies of the original image.
  //
  // Note that this will still produce a sharp image for any color component that has zero chromatic aberration.
  // (Thus, it is recommended for all aberration components to be nonzero when this feature is used.)
  //
  result.r += weight*tex2D( %(k_txcolor)s, basepos + offsetvec * CHROMA_DISTORT.r ).r;
  result.g += weight*tex2D( %(k_txcolor)s, basepos + offsetvec * CHROMA_DISTORT.g ).g;
  result.b += weight*tex2D( %(k_txcolor)s, basepos + offsetvec * CHROMA_DISTORT.b ).b;
#endif

  weightsum += weight;
}
result /= weightsum;

#endif

pixcolor = result;

"""


class LensDistortion(Filter):
    """Filter that simulates simple lens imperfections.

    Introduced in Panda 1.9.0.

    Supports barrel distortion and chromatic aberration.

    See also MiscFilters.Vignetting, which implements a vignetting imperfection.

    """

    def __init__(self, **kwargs):
        super(LensDistortion, self).__init__(**kwargs)

    def onReset(self):
        super(LensDistortion, self).onReset()  # reset inherited properties

        self.sort = 0  # This filter overwrites pixcolor, so it should go first in whichever stage it is in.
        self.stageName   = "LensOpticsEarly"
        self.isMergeable = False  # No internal stages, but overwriting pixcolor implies non-mergeable.

        self.barrelFuzzy        = False
        self.barrelDistort      = 0.05
        self.useChromaDistort   = True
        self.chromaDistort      = (0.01, -0.005, -0.02)
        self.numsamples         = 16

    def onAttachPipeline(self):
        self.registerInputTexture(texName="color")

        self.registerCustomInput(inputType="float",  inputName="k_lensdistort_barrel")
        self.registerCustomInput(inputType="float3", inputName="k_lensdistort_chroma")

    def onSynthesizeCompositor(self):
        txcolor = self.getTextureInfo("color")
        code = LENS_DISTORT_BODY % { "barrel_fuzzy"         : self.barrelFuzzy,
                                     "use_chroma_distort"   : self.useChromaDistort,
                                     "numsamples"           : self.numsamples,
                                     "k_lensdistort_barrel" : self.getMangledName("k_lensdistort_barrel"),
                                     "k_lensdistort_chroma" : self.getMangledName("k_lensdistort_chroma"),
                                     "k_txcolor"            : txcolor.get('varname'),
                                     "texcoord_txcolor"     : txcolor.get('texcoord'),
                                     "texpad_txcolor"       : txcolor.get('texpad') }
        return ("lensDistortion", code, "// Barrel distortion / chromatic aberration filter\n")


    @property
    def barrelFuzzy(self):
        """Whether to simulate a low-quality lens, which produces a fuzzy (radially blurred) image.

        This applies a radial blur to the image.

        Bool, default False.

        """
        return self._barrelFuzzy
    @barrelFuzzy.setter
    def barrelFuzzy(self, value):
        if (not hasattr(self, "_barrelFuzzy")  or  bool(value) != self._barrelFuzzy)  and  self.pipeline is not None:
            self.pipeline._needsCompile = True
        self._barrelFuzzy = bool(value)


    @property
    def barrelDistort(self):
        """Barrel distortion strength, float (default 0.05).

        Positive values make a barrel distortion, negative values a pincushion distortion.

        Zero means no distortion.

        """
        return self._barrelDistort
    @barrelDistort.setter
    def barrelDistort(self, value):
        self._barrelDistort = value
        if self.finalQuad is not None:
            # Convenience: we want positive values to represent barrel distortion
            # and negative values pincushion distortion, although the math in the shader
            # works the other way around. Flip the sign.
            #
            self.finalQuad.setShaderInput( self.getMangledName("lensdistort_barrel"), -value )


    @property
    def useChromaDistort(self):
        """Whether to simulate chromatic aberration.

        Bool, default True.

        """
        return self._useChromaDistort
    @useChromaDistort.setter
    def useChromaDistort(self, value):
        if (not hasattr(self, "_useChromaDistort")  or  bool(value) != self._useChromaDistort)  and  self.pipeline is not None:
            self.pipeline._needsCompile = True
        self._useChromaDistort = bool(value)


    @property
    def chromaDistort(self):
        """Strength of chromatic aberration.

        Tuple of (R,G,B) component shifts; default (0.01, -0.005, -0.02).

        Applies to the whole image.

        A positive number shifts the color component outward (toward view edges),
        while a negative number shifts inward (toward view center).

        A radial blur is applied. If the aberration strength for some color component is zero,
        that component will not receive any blurring in the chromatic aberration. Generally,
        a small nonzero value is better, to avoid leaving the picture sharp in one color component
        while the others are blurred.

        Note also that the chromatic aberrations need to be rather small, so that the three
        blurred images will overlap even for small features in the scene; otherwise the illusion
        of a continuous color spectrum breaks down. For large aberrations, it may help
        to set barrelFuzzy=True (which applies an additional radial blur uniformly to
        all color components).

        """
        return self._chromaDistort
    @chromaDistort.setter
    def chromaDistort(self, value):
        self._chromaDistort = value
        if self.finalQuad is not None:
            self.finalQuad.setShaderInput( self.getMangledName("lensdistort_chroma"), Vec3(value) )


    @property
    def numsamples(self):
        """Number of samples used for radial blur.

        Used in chromatic aberration (when useChromaDistort=True)
        and in fuzzy barrel distortion (when barrelFuzzy=True).

        """
        return self._numsamples
    @numsamples.setter
    def numsamples(self, value):
        if (not hasattr(self, "_numsamples")  or  value != self._numsamples)  and  self.pipeline is not None:
            self.pipeline._needsCompile = True
        self._numsamples = value

