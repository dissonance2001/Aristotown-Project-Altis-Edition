from panda3d.core import Shader, Vec4

from toontown.shader.Filter import Filter

# Threshold, invert and radial blur.
#
LENSFLARE0_SHADER="""//Cg
//
//Cg profile arbvp1 arbfp1

void vshader(
    float4 vtx_position : POSITION,
    out float4 l_position : POSITION,
    out float2 l_texcoord : TEXCOORD0,
    uniform float4 texpad_src,
    uniform float4x4 mat_modelproj)
{
    l_position = mul(mat_modelproj, vtx_position);

    // invert texture coord
    l_texcoord = - (vtx_position.xz * texpad_src.xy*2);
}


void fshader(float2 l_texcoord : TEXCOORD0,
             out float4 o_color : COLOR,
             uniform float4 texpad_src,
             uniform sampler2D k_src : TEXUNIT0,
             uniform float4 k_threshold)
{
    const int NSAMPLES = %(numsamples)d;
    const float BlurStart = 0.5;
    const float BlurWidth = 0.1;
    float BRIGHTNESS = k_threshold.w;
    float3 THRESHOLD = k_threshold.xyz;

    // threshold + radial blur
    float4 c = 0;
    float3 tmp = 0;
    for(int i = 0; i < NSAMPLES; ++i) {
        float scale = BlurStart - BlurWidth*(i/(float) (NSAMPLES-1));
        tmp = tex2D(k_src, l_texcoord * scale + texpad_src.xy ).xyz;
        tmp = saturate((((tmp - THRESHOLD)/(float3(1.0) - THRESHOLD))) * BRIGHTNESS);
        c += float4(tmp, 1.0);
    }
    c /= NSAMPLES;
    
    o_color = c;
}
"""


# Blend pass.
#
LENSFLARE_BODY = """const float FLARE_HALO_WIDTH = %(haloWidth)f;
const float FLARE_DISPERSAL = %(dispersal)f;
const float3 CHROMA_DISTORT = float3(%(chromaDistortR)f, %(chromaDistortG)f, %(chromaDistortB)f);

float2 lf_sample_vector = (%(texpad_txlensflare1)s.xy - %(texcoord_txlensflare1)s) * FLARE_DISPERSAL;
float2 lf_halo_vector = normalize(lf_sample_vector) * FLARE_HALO_WIDTH;
float3 lf_tmp = float3(0.0);
float3 lf_result = 0.0;
lf_result.x = tex2D(%(k_txlensflare1)s, %(texcoord_txlensflare1)s + lf_halo_vector + lf_halo_vector * CHROMA_DISTORT.x).x;
lf_result.y = tex2D(%(k_txlensflare1)s, %(texcoord_txlensflare1)s + lf_halo_vector + lf_halo_vector * CHROMA_DISTORT.y).y;
lf_result.z = tex2D(%(k_txlensflare1)s, %(texcoord_txlensflare1)s + lf_halo_vector + lf_halo_vector * CHROMA_DISTORT.z).z;
for (int i = 0; i < %(numsamples)d; ++i) {
  float2 offset = lf_sample_vector * float(i);
  lf_tmp.x = tex2D(%(k_txlensflare1)s, %(texcoord_txlensflare1)s + offset + offset * CHROMA_DISTORT.x).x;
  lf_tmp.y = tex2D(%(k_txlensflare1)s, %(texcoord_txlensflare1)s + offset + offset * CHROMA_DISTORT.y).y;
  lf_tmp.z = tex2D(%(k_txlensflare1)s, %(texcoord_txlensflare1)s + offset + offset * CHROMA_DISTORT.z).z;
  lf_result += lf_tmp;
}

lf_result /= float(%(numsamples)d);

pixcolor.rgb += lf_result.rgb;
"""


class LensFlare(Filter):
    """Fast, approximate lens flare effect, based on John Chapman's algorithm.

    Introduced in Panda 1.9.0.

    The filter is procedural, requiring no textures other than the rendered scene.

    Each bright pixel in the scene automatically "flares", causing blurred ghost images
    to be scattered along the axis that connects the bright pixel to the center point of the view.

    When bright pixels are near the center of the view, also a halo ring is generated.

    As of this writing, the explanation of the algorithm can be found at

    http://www.john-chapman.net/content.php?id=18

    """

    def __init__(self, **kwargs):
        super(LensFlare, self).__init__(**kwargs)

    def onReset(self):
        super(LensFlare, self).onReset()
        self.sort = 60
        self.stageName   = "LensOpticsLate"
        self.isMergeable = False

        self.threshold     = (0.7, 0.7, 0.7)
        self.brightness    = 1.0
        self.numsamples    = 5
        self.haloWidth     = 0.3
        self.dispersal     = 0.35
        self.chromaDistort = (0.005, -0.005, 0)

    def onAttachPipeline(self):
        self.registerInputTexture(texName="lensflare1")

    def onAttachStage(self):
        self.createInternalTextures( "lensflare0", "lensflare1" )

        self.interQuads.append(self.pipeline.manager.renderQuadInto(colortex=self.get('texture')["lensflare0"]))
        self.interQuads[0].setShaderInput("src", self.getTextureInfo("color").get('texture'))

        self.interQuads.append(self.pipeline.manager.renderQuadInto(colortex=self.get('texture')["lensflare1"]))
        self.interQuads[1].setShaderInput("src", self.getTextureInfo("lensflare0").get('texture'))

    def onCompileInternalStages(self):
        self.interQuads[0].setShader(Shader.make(LENSFLARE0_SHADER % {"numsamples" : self.numsamples}))
        self.interQuads[1].setShader(self.loadShader("filter-gaussian_blur.sha"))

    def onSynthesizeCompositor(self):
        txlensflare1  = self.getTextureInfo("lensflare1")
        chromaDistort = self.chromaDistort
        code = LENSFLARE_BODY % { "k_txlensflare1" : txlensflare1.get('varname'),
                                  "texcoord_txlensflare1" : txlensflare1.get('texcoord'),
                                  "texpad_txlensflare1" : txlensflare1.get('texpad'),
                                  "haloWidth"  : self.haloWidth,
                                  "dispersal"  : self.dispersal,
                                  "numsamples" : self.numsamples,
                                  "chromaDistortR" : chromaDistort[0],
                                  "chromaDistortG" : chromaDistort[1],
                                  "chromaDistortB" : chromaDistort[2] }
        return ("lensFlare", code, "// Lens flare blend pass\n")


    # The k_threshold parameter of LENSFLARE0_SHADER packs together threshold and brightness.
    #
    def _computeThresholdParam(self):
        return Vec4( self._threshold[0], self._threshold[1], self._threshold[2], self._brightness )


    @property
    def threshold(self):
        """Tuple (R,G,B): R,G,B = color component thresholds to trigger "flaring".

        Default (0.7, 0.7, 0.7).

        If a pixel has its R, G or B component >= threshold, it participates
        in the lens flare.

        The color components flare independently; e.g. (0.2, 1.0, 1.0) generates
        a red lens flare, since the red threshold is much lower than the others.
        (This may be useful if e.g. a laser shines at the camera; however note that
         this is a global postprocessing effect, so it will affect all light sources equally).

        A threshold of 1 means that the color component will not flare.

        """
        return self._threshold
    @threshold.setter
    def threshold(self, value):
        self._threshold = value
        if len(self.interQuads)  and  self.interQuads[0] is not None:
            self.interQuads[0].setShaderInput( "threshold", self._computeThresholdParam() )


    @property
    def brightness(self):
        """Flare brightness (default 1.0)."""
        return self._brightness
    @brightness.setter
    def brightness(self, value):
        self._brightness = value
        if len(self.interQuads)  and  self.interQuads[0] is not None:
            self.interQuads[0].setShaderInput( "threshold", self._computeThresholdParam() )


    @property
    def numsamples(self):
        """Number of samples used for blurring (default 5).

        More samples allows using larger values for haloWidth and chromaDistort
        before the effect breaks down.

        """
        return self._numsamples
    @numsamples.setter
    def numsamples(self, value):
        if not hasattr(self, "_numsamples")  or  value != self._numsamples:
            # This affects code generation of both LENSFLARE0_SHADER and the compositing shader.
            self._needsCompile = True
            if self.pipeline is not None:
                self.pipeline._needsCompile = True
        self._numsamples = value


    @property
    def haloWidth(self):
        """How far from the view center the halo ring is (default 0.3).

        Values over 0.5 cause only part of the ring to be shown in the
        corners of the view (try e.g. 0.6). Values over 0.65 (approximately)
        make the halo disappear altogether.

        """
        return self._haloWidth
    @haloWidth.setter
    def haloWidth(self, value):
        if (not hasattr(self, "_haloWidth")  or  value != self._haloWidth)  and  self.pipeline is not None:
            self.pipeline._needsCompile = True
        self._haloWidth = value


    @property
    def dispersal(self):
        """Controls ghost crowding.

        Default 0.35.

        Dispersal affects the spacing of adjacent ghosts from the same source.

        When dispersal is low (0.1), the ghosts will "crowd" near the point
        which is the mirror image of their source with respect to the view center.

        When dispersal is high (0.8), the ghosts will be spread out all over their axis.

        """
        return self._dispersal
    @dispersal.setter
    def dispersal(self, value):
        if (not hasattr(self, "_dispersal")  or  value != self._dispersal)  and  self.pipeline is not None:
            self.pipeline._needsCompile = True
        self._dispersal = value


    @property
    def chromaDistort(self):
        """Strength of chromatic aberration in the lens flare.

        Tuple of (R,G,B) component shifts; default (0.005, -0.005, 0).

        Applies to the lens flare only. Affects both the ghosts and the halo.

        A positive number shifts the color component outward (toward view edges),
        while a negative number shifts inward (toward view center).

        """
        return self._chromaDistort
    @chromaDistort.setter
    def chromaDistort(self, value):
        if (not hasattr(self, "_chromaDistort")  or  value != self._chromaDistort)  and  self.pipeline is not None:
            self.pipeline._needsCompile = True
        self._chromaDistort = value

