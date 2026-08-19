from panda3d.core import AuxBitplaneAttrib, Vec4

from toontown.shader.Filter import Filter

# This filter uses an area-based voting algorithm to produce smoothed ink in a single render pass.
# It makes thin outlines. It does not support varying line thickness, because the algorithm
# requires using a stencil spacing of exactly one pixel (separation = 1.0).
#
# Supported numbers of num_samples (voting stencil size):
#  4, 8, 12 [recommended], 20, 24, 28.
#
# Pixels in the stencil vote to decide ink strength. Linear, quadratic and cubic ink strength profiles
# (WEIGHT_POW = 1, 2, 3) are supported. The curves are flipped such that higher-power profiles produce
# relatively stronger ink at the *low* end, when compared to the linear profile.
#
# Additionally, a special value of WEIGHT_POW = 0 behaves as follows:
# if votes exceed k_cartoon_voting_threshold, the pixel is fully inked.
#
CARTOONINK_BODY="""#define NUM_SAMPLES %(numsamples)d

#define USE_NORMALS_DETECTION %(normals_detect)d
#define USE_DEPTH_DETECTION %(depth_detect)d
#define WEIGHT_POW %(weight_pow)d

// Set up edge detection stencil

#if NUM_SAMPLES == 4
// NOTE: this stencil accounts for too few neighbours to work well.
const float2 cartoon_samplepos[4] = float2[](                float2(0,-1),
                                              float2(-1, 0),               float2(1, 0),
                                                             float2(0, 1) );
const float  stencil_weights[4]   = float[](                 1.0,
                                              1.0,                         1.0,
                                                             1.0 );
const float  stencil_sum = 4*1.0;

#elif NUM_SAMPLES == 8
// This stencil works decently well.
const float2 cartoon_samplepos[8] = float2[]( float2(-1,-1), float2(0,-1), float2(1,-1),
                                              float2(-1, 0),               float2(1, 0),
                                              float2(-1, 1), float2(0, 1), float2(1, 1) );

// weight votes by 1/distance (euclidean) from center pixel
const float  stencil_weights[8]   = float[](  0.7,           1.0,          0.7,
                                              1.0,                         1.0,
                                              0.7,           1.0,          0.7 );
// maximum possible value from votes if all pixels in the stencil agree
const float  stencil_sum = 4*0.7 + 4*1.0;

#elif NUM_SAMPLES == 12
// This stencil is the best one for general-purpose use.
const float2 cartoon_samplepos[12] = float2[](
                                  float2( 0,-2),
                   float2(-1,-1), float2( 0,-1), float2( 1,-1),
    float2(-2, 0), float2(-1, 0),                float2( 1, 0), float2( 2, 0),
                   float2(-1, 1), float2( 0, 1), float2( 1, 1),
                                  float2( 0, 2) );

const float  stencil_weights[12]   = float[](
                                  0.5,
                   0.7,           1.0,           0.7,
    0.5,           1.0,                          1.0,           0.5,
                   0.7,           1.0,           0.7,
                                  0.5 );
const float  stencil_sum = 4*0.7 + 4*1.0 + 4*0.5;

#elif NUM_SAMPLES == 20
// This stencil causes darkening when the object covers only a very small part of the screen.
// Maybe this would require adjusting the voting threshold.
const float2 cartoon_samplepos[20] = float2[](
                   float2(-1,-2), float2( 0,-2), float2( 1,-2),
    float2(-2,-1), float2(-1,-1), float2( 0,-1), float2( 1,-1), float2( 2,-1),
    float2(-2, 0), float2(-1, 0),                float2( 1, 0), float2( 2, 0),
    float2(-2, 1), float2(-1, 1), float2( 0, 1), float2( 1, 1), float2( 2, 1),
                   float2(-1, 2), float2( 0, 2), float2( 1, 2) );

const float  stencil_weights[20]   = float[](
                   0.44,          0.5,           0.44,
    0.44,          0.7,           1.0,           0.7,           0.44,
    0.5,           1.0,                          1.0,           0.5,
    0.44,          0.7,           1.0,           0.7,           0.44,
                   0.44,          0.5,           0.44 );
const float  stencil_sum = 4*0.7 + 4*1.0 + 4*0.5 + 8*0.44;

#elif NUM_SAMPLES == 24
// This stencil causes darkening when the object covers only a very small part of the screen.
// Maybe this would require adjusting the voting threshold.
const float2 cartoon_samplepos[24] = float2[](
    float2(-2,-2), float2(-1,-2), float2( 0,-2), float2( 1,-2), float2( 2,-2),
    float2(-2,-1), float2(-1,-1), float2( 0,-1), float2( 1,-1), float2( 2,-1),
    float2(-2, 0), float2(-1, 0),                float2( 1, 0), float2( 2, 0),
    float2(-2, 1), float2(-1, 1), float2( 0, 1), float2( 1, 1), float2( 2, 1),
    float2(-2, 2), float2(-1, 2), float2( 0, 2), float2( 1, 2), float2( 2, 2) );

const float  stencil_weights[24]   = float[](
    0.35,          0.44,          0.5,           0.44,          0.35,
    0.44,          0.7,           1.0,           0.7,           0.44,
    0.5,           1.0,                          1.0,           0.5,
    0.44,          0.7,           1.0,           0.7,           0.44,
    0.35,          0.44,          0.5,           0.44,          0.35 );
const float  stencil_sum = 4*0.7 + 4*1.0 + 4*0.5 + 8*0.44 + 4*0.35;

#elif NUM_SAMPLES == 28
// This stencil causes darkening when the object covers only a very small part of the screen.
// Maybe this would require adjusting the voting threshold.
const float2 cartoon_samplepos[28] = float2[](
                                            float2( 0,-3),
              float2(-2,-2), float2(-1,-2), float2( 0,-2), float2( 1,-2), float2( 2,-2),
              float2(-2,-1), float2(-1,-1), float2( 0,-1), float2( 1,-1), float2( 2,-1),
float2(-3,0), float2(-2, 0), float2(-1, 0),                float2( 1, 0), float2( 2, 0), float2(3,0),
              float2(-2, 1), float2(-1, 1), float2( 0, 1), float2( 1, 1), float2( 2, 1),
              float2(-2, 2), float2(-1, 2), float2( 0, 2), float2( 1, 2), float2( 2, 2),
                                            float2( 0, 3) );

const float  stencil_weights[28]   = float[](
                                            0.33,
              0.35,          0.44,          0.5,           0.44,           0.35,
              0.44,          0.7,           1.0,           0.7,            0.44,
0.33,         0.5,           1.0,                          1.0,            0.5,          0.33,
              0.44,          0.7,           1.0,           0.7,            0.44,
              0.35,          0.44,          0.5,           0.44,           0.35,
                                            0.33 );
const float  stencil_sum = 4*0.7 + 4*1.0 + 4*0.5 + 8*0.44 + 4*0.35 + 4*0.33;
#endif


// Detect edges.
//
// We compare the data of the center pixel to its neighbours, hard-thresholding for each neighbour.
//
// The weighted votes of the neighbours that agree that the pixel should be inked
// determines the ink strength.
//
// This counts *weighted* votes.
//
float count = 0;

#if USE_NORMALS_DETECTION == 1
float4 cartoon_caux0   = tex2D(%(k_txaux)s,   %(texcoord_txaux)s.xy);
#endif

#if USE_DEPTH_DETECTION == 1
float  cartoon_cdepth0 = tex2D(%(k_txdepth)s, %(texcoord_txdepth)s.xy);
#endif

for(int i = 0; i < NUM_SAMPLES; ++i) {

#if USE_NORMALS_DETECTION == 1
  float2 cartoon_paux = %(texcoord_txaux)s.xy + cartoon_samplepos[i] * %(texpix_txaux)s.xy;
  float4 cartoon_caux = tex2D(%(k_txaux)s, cartoon_paux);
  float3 diff = (cartoon_caux - cartoon_caux0).xyz;
  float vote_aux = step(%(k_cartoon_cutoff_normals)s, dot(diff,diff));  // 0.02 is a good default cutoff for this
                                                                        // (note we compare diff**2, not diff itself)
#endif

#if USE_DEPTH_DETECTION == 1
  float2 cartoon_pdepth = %(texcoord_txdepth)s.xy + cartoon_samplepos[i] * %(texpix_txdepth)s.xy;
  float  cartoon_cdepth = tex2D(%(k_txdepth)s, cartoon_pdepth);
  float  diff2 = cartoon_cdepth - cartoon_cdepth0;
  float vote_depth = step(%(k_cartoon_cutoff_depth)s, diff2*diff2);  // 0.0001 is a good default (again, diff squared!)
#endif

#if USE_NORMALS_DETECTION == 1  &&  USE_DEPTH_DETECTION == 0
  count += stencil_weights[i]*vote_aux;
#elif USE_NORMALS_DETECTION == 0  &&  USE_DEPTH_DETECTION == 1
  count += stencil_weights[i]*vote_depth;
#else
  // Two detectors. If either detector matches, vote "yes".
  count += stencil_weights[i]*max(vote_aux, vote_depth);
#endif
}

// If enough votes, ink the pixel.
//
// The shape of the ink strength profile can be adjusted using WEIGHT_POW.
//
// For WEIGHT_POW >= 1, just above the threshold, we have slight inking; at the maximum, full inking.
//
//
// k_cartoon_voting_threshold is a cutoff parameter for noise reduction.
//
// More than k_cartoon_voting_threshold weighted votes in the stencil (doesn't matter which ones) must decide to ink
// the center pixel before any ink is applied. This reduces noise (by rejecting single "mistaken" samples),
// and applies smoothing (by detecting cases where the edge covers only a part of the stencil).
//
// For NUM_SAMPLES = 8 or NUM_SAMPLES = 12, a good threshold seems to be 1.0.
//
if( count > %(k_cartoon_voting_threshold)s ) {
#if WEIGHT_POW == 0
  // Thresholding mode (WEIGHT_POW = 0); ink fully.
  pixcolor = %(k_cartooncolor)s;
#else
  float f = 1.0 - (count - %(k_cartoon_voting_threshold)s) / (stencil_sum - %(k_cartoon_voting_threshold)s);
#if WEIGHT_POW == 2
  f *= f;  // quadratic weighting (emphasizes low end slightly)
#elif WEIGHT_POW == 3
  f *= f*f;  // cubic weighting (emphasizes low end significantly)
#endif
  pixcolor = lerp(%(k_cartooncolor)s, pixcolor, f);
#endif
}
"""


class CartoonInkThin(Filter):
    """A cartoon outline inking filter.

    The inking is based on examining discontinuities in the normal and depth maps, as viewed from the camera.

    Fast algorithm based on comparing the neighbouring pixels to the center pixel.
    Produces thin, antialiased ink lines.

    This algorithm introduced in Panda 1.9.0.

    """
    def __init__(self, **kwargs):
        super(CartoonInkThin, self).__init__(**kwargs)

    def onReset(self):
        super(CartoonInkThin, self).onReset()
        # Inking must come before pretty much everything else, to simulate a completely drawn cel.
        self.stageName  = "Preprocess"
        self.sort       = 50  # This is an alternative to CartoonInkClassic, so they can have the same default sort
                              # (in order to trigger an error if both are enabled).
        self.isMergeable = False  # requires access to up-to-date aux and depth textures (outside current pixel)

        self.color      = (0.0, 0.0, 0.0, 1.0)

        # Stencil size (only certain sizes are supported).
        #
        self.numsamples    = 12

        # Data sources.
        #
        # Each data source requires numsamples texture lookups, so the more sources are enabled,
        # the slower the inker is, but the outlines will be of higher quality, as more types of
        # discontinuities are caught.
        #
        self.detectDepth   = True
        self.cutoffDepth   = 0.0001

        self.detectNormals = True
        self.cutoffNormals = 0.02

        # Stencil voting parameters.
        #
        self.voteThreshold = 1.0
        self.weightPower   = 2

    def onAttachPipeline(self):
        if self.detectNormals:
            self.registerInputTexture(texName="aux")
            self.requireAuxBits(bitmask=AuxBitplaneAttrib.ABOAuxNormal)
        if self.detectDepth:
            self.registerInputTexture(texName="depth")

        self.registerCustomInput(inputType="float4", inputName="k_cartooncolor")
        self.registerCustomInput(inputType="float",  inputName="k_cartoon_voting_threshold")
        self.registerCustomInput(inputType="float",  inputName="k_cartoon_cutoff_normals")
        self.registerCustomInput(inputType="float",  inputName="k_cartoon_cutoff_depth")


    def onSynthesizeCompositor(self):
        paramsDict = { "k_cartooncolor"             : self.getMangledName("k_cartooncolor"),
                       "k_cartoon_voting_threshold" : self.getMangledName("k_cartoon_voting_threshold"),
                       "k_cartoon_cutoff_normals"   : self.getMangledName("k_cartoon_cutoff_normals"),
                       "k_cartoon_cutoff_depth"     : self.getMangledName("k_cartoon_cutoff_depth"),
                       "numsamples"                 : self.numsamples,
                       "normals_detect"             : self.detectNormals,
                       "depth_detect"               : self.detectDepth,
                       "weight_pow"                 : self.weightPower }

        if self.detectNormals:
            txaux = self.getTextureInfo("aux")
            paramsDict.update( { "k_txaux"        : txaux.get('varname'),
                                 "texcoord_txaux" : txaux.get('texcoord'),
                                 "texpix_txaux"   : txaux.get('texpix') } )

        if self.detectDepth:
            txdepth = self.getTextureInfo("depth")
            paramsDict.update( { "k_txdepth"        : txdepth.get('varname'),
                                 "texcoord_txdepth" : txdepth.get('texcoord'),
                                 "texpix_txdepth"   : txdepth.get('texpix') } )

        code = CARTOONINK_BODY % paramsDict

        return ("cartoonInkThin",
                code,
                "// cartoon ink (outlines), 'thin' algorithm\n")


    @property
    def color(self):
        """Color to use for ink, as (R,G,B,A) tuple.

        The alpha component gives the _maximum_ alpha value that corresponds
        to a fully inked pixel.

        """
        return self._color
    @color.setter
    def color(self, value):
        self._color = value
        if self.finalQuad is not None:
            self.finalQuad.setShaderInput( self.getMangledName("cartooncolor"), Vec4(value) )


    @property
    def numsamples(self):
        """Number of samples. Chooses the ink voting stencil.

        Integer, one of:

            4, 8, 12 [default, recommended], 20, 24, 28.

        The smallest stencil (4) tends to miss pixels that should be inked, whereas values of 20 or larger
        may cause unintended darkening in parts of the scene that are not edges (at least if the default
        value of voteThreshold is used).

        Also, each enabled data source requires numsamples texture lookups, so larger values mean slower inking.

        Recommended values for general use are 8 and 12, with 12 giving a slight edge in quality
        and 8 in speed.

        """
        return self._numsamples
    @numsamples.setter
    def numsamples(self, value):
        if value not in [4, 8, 12, 20, 24, 28]:
            raise ValueError("In %s %s: unknown numsamples %d; valid: 4, 8, 12, 20, 24, 28" % (self.__class__.__name__, self.name, value))
        if (not hasattr(self, "_numsamples")  or  value != self._numsamples)  and  self.pipeline is not None:
            self.pipeline._needsCompile = True
        self._numsamples = value


    @property
    def detectDepth(self):
        """Whether to ink depth discontinuities.

        This enables/disables the depth buffer as a data source.

        Bool, default True.

        """
        return self._detectDepth
    @detectDepth.setter
    def detectDepth(self, value):
        if (not hasattr(self, "_detectDepth")  or  bool(value) != self._detectDepth)  and  self.pipeline is not None:
            self.pipeline._needsCompile = True
        self._detectDepth = bool(value)


    @property
    def cutoffDepth(self):
        """Cutoff for detecting depth buffer discontinuities (default: 0.0001).

        Used when detectDepth=True.

        A discontinuity is detected if

          (this - other)**2  >=  cutoff

        where "this" and "other" are the depth buffer values of the center pixel (in the stencil)
        and the other pixel (in the stencil) being compared, respectively.

        Note the squaring. Note also that the depth buffer (z-buffer) stores nonlinear depth values,
        originally meant for interpolating 1/z linearly, so this threshold does NOT map linearly
        to a fraction of (far - near) of the camera.

        """
        return self._cutoffDepth
    @cutoffDepth.setter
    def cutoffDepth(self, value):
        self._cutoffDepth = value
        if self.finalQuad is not None:
            self.finalQuad.setShaderInput( self.getMangledName("cartoon_cutoff_depth"), value )


    @property
    def detectNormals(self):
        """Whether to ink surface normal discontinuities.

        This enables/disables the (screen-space) normals buffer as a data source.

        Bool, default True.

        """
        return self._detectNormals
    @detectNormals.setter
    def detectNormals(self, value):
        if (not hasattr(self, "_detectNormals")  or  bool(value) != self._detectNormals)  and  self.pipeline is not None:
            self.pipeline._needsCompile = True
        self._detectNormals = bool(value)


    @property
    def cutoffNormals(self):
        """Cutoff for detecting normal map discontinuities (default: 0.02).

        Used when detectNormals=True.

        A discontinuity is detected if

          dot(this.xyz, other.xyz)**2  >=  cutoff

        where "this" and "other" are the normal vectors of the center pixel (in the stencil)
        and the other pixel (in the stencil) being compared, respectively.

        Note the squaring.

        """
        return self._cutoffNormals
    @cutoffNormals.setter
    def cutoffNormals(self, value):
        self._cutoffNormals = value
        if self.finalQuad is not None:
            self.finalQuad.setShaderInput( self.getMangledName("cartoon_cutoff_normals"), value )


    @property
    def voteThreshold(self):
        """Inking threshold in stencil voting.

        Float. At least voteThreshold weighted votes in the stencil must agree that the pixel should be inked
        before the pixel is inked at all.

        The voting weight of a pixel is 1/r, where r is the euclidean distance (in pixels) from the center of
        the stencil. Each pixel votes either yes (1.0) or no (0.0), and this is multiplied by the voting weight.
        The votes are summed, and this is compared against the threshold to decide whether to vote the
        pixel at the center of the stencil.

        For numsamples (stencil sizes) 8 and 12, voteThreshold=1.0 (default) is usually a good choice.

        """
        return self._voteThreshold
    @voteThreshold.setter
    def voteThreshold(self, value):
        self._voteThreshold = value
        if self.finalQuad is not None:
            self.finalQuad.setShaderInput( self.getMangledName("cartoon_voting_threshold"), value )


    @property
    def weightPower(self):
        """Ink strength profile shape parameter.

        The strength is determined by considering how much the voting result exceeds voteThreshold,
        and applying the strength profile to that.

        Integer, one of:

            0, 1, 2 [default], 3.

        The values 1, 2 and 3 correspond to linear, quadratic and cubic weighting, respectively.
        Roughly speaking, a larger value means stronger ink.

        The value 0 uses plain thresholding: if the voting passes voteThreshold, then the pixel is fully inked.
        This may lead to jagginess of the outline; for most use cases, the other values are recommended.

        The curves for 1,2,3 are flipped such that higher-power profiles produce relatively stronger ink
        at the *low* end, when compared to the linear profile. Mathematically, if x in the interval [0, 1]
        represents the score range that passes voting, the mapping is  inkstrength = 1 - (1 - x)**weightPower.

        To visualize the profile curves in pylab (ipython --pylab):

          x = linspace(0, 1, 201)
          y1 = 1 - (1 - x)
          y2 = 1 - (1 - x)**2
          y3 = 1 - (1 - x)**3
          clf()
          plot(array([x,x,x]).T, array([y1,y2,y3]).T)
          grid(b=True, which="both")
          xlabel("Score (in range that passes voting)")
          ylabel("Ink strength")
          legend(["1", "2", "3"], loc="best")
          savefig("inkstrength.pdf")
          savefig("inkstrength.png")

        (use the %paste magic command to paste this snippet into ipython from the clipboard)

        """
        return self._weightPower
    @weightPower.setter
    def weightPower(self, value):
        if value not in [0, 1, 2, 3]:
            raise ValueError("In %s %s: unknown weightPower %d: valid: 0, 1, 2 or 3" % (self.__class__.__name__, self.name, value))
        if (not hasattr(self, "_weightPower")  or  value != self._weightPower)  and  self.pipeline is not None:
            self.pipeline._needsCompile = True
        self._weightPower = value

