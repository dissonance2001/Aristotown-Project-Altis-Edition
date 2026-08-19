from panda3d.core import Shader, AuxBitplaneAttrib, Vec4

from toontown.shader.Filter import Filter

# Some GPUs do not support variable-length loops (and neither do the arbvp1/arbfp1 profiles,
# which are the only ones which Cg reliably compiles for non-NVIDIA GPUs).
#
# We fill in the actual value of numsamples in the loop limit when the shader is configured.
#
SSAO0_SHADER="""//Cg
//
//Cg profile arbvp1 arbfp1

void vshader(float4 vtx_position    : POSITION,
             out float4 l_position  : POSITION,
             out float2 l_texcoord  : TEXCOORD0,
             out float2 l_texcoordD : TEXCOORD1,
             out float2 l_texcoordN : TEXCOORD2,
             uniform float4 texpad_depth,
             uniform float4 texpad_normal,
             uniform float4x4 mat_modelproj)
{
  l_position = mul(mat_modelproj, vtx_position);
  l_texcoord = vtx_position.xz;
  l_texcoordD = (vtx_position.xz * texpad_depth.xy) + texpad_depth.xy;
  l_texcoordN = (vtx_position.xz * texpad_normal.xy) + texpad_normal.xy;
}

const float3 sphere[16] = float3[]( float3( 0.53812504,   0.18565957,   -0.43192),
                                    float3( 0.13790712,   0.24864247,    0.44301823),
                                    float3( 0.33715037,   0.56794053,   -0.005789503),
                                    float3(-0.6999805,   -0.04511441,   -0.0019965635),
                                    float3( 0.06896307,  -0.15983082,   -0.85477847),
                                    float3( 0.056099437,  0.006954967,  -0.1843352),
                                    float3(-0.014653638,  0.14027752,    0.0762037),
                                    float3( 0.010019933, -0.1924225,    -0.034443386),
                                    float3(-0.35775623,  -0.5301969,    -0.43581226),
                                    float3(-0.3169221,    0.106360726,   0.015860917),
                                    float3( 0.010350345, -0.58698344,    0.0046293875),
                                    float3(-0.08972908,  -0.49408212,    0.3287904),
                                    float3( 0.7119986,   -0.0154690035, -0.09183723),
                                    float3(-0.053382345,  0.059675813,  -0.5411899),
                                    float3( 0.035267662, -0.063188605,   0.54602677),
                                    float3(-0.47761092,   0.2847911,    -0.0271716));

void fshader(out float4 o_color : COLOR,
             uniform float4 k_params1,
             uniform float4 k_params2,
             float2 l_texcoord  : TEXCOORD0,
             float2 l_texcoordD : TEXCOORD1,
             float2 l_texcoordN : TEXCOORD2,
             uniform sampler2D k_random : TEXUNIT0,
             uniform sampler2D k_depth  : TEXUNIT1,
             uniform sampler2D k_normal : TEXUNIT2)
{
  float pixel_depth = tex2D(k_depth, l_texcoordD).a;
  float3 pixel_normal = (tex2D(k_normal, l_texcoordN).xyz * 2.0 - 1.0);
  float3 random_vector = normalize((tex2D(k_random, l_texcoord * 18.0 + pixel_depth + pixel_normal.xy).xyz * 2.0) - float3(1.0)).xyz;
  float occlusion = 0.0;
  float radius = k_params1.z / pixel_depth;
  float depth_difference;
  float3 sample_normal;
  float3 ray;
  for(int i = 0; i < %(numsamples)d; ++i) {
   ray = radius * reflect(sphere[i], random_vector);
   sample_normal = (tex2D(k_normal, l_texcoordN + ray.xy).xyz * 2.0 - 1.0);
   depth_difference = (pixel_depth - tex2D(k_depth,l_texcoordD + ray.xy).r);
   occlusion += step(k_params2.y, depth_difference) * (1.0 - dot(sample_normal.xyz, pixel_normal)) * (1.0 - smoothstep(k_params2.y, k_params2.x, depth_difference));
  }
  o_color.rgb = 1.0 + (occlusion * k_params1.y);
  o_color.a = 1.0;
}
"""


class AmbientOcclusion(Filter):
    """Ambient occlusion simulates how nearby surfaces block each other's access to ambient light,
    darkening corners in the scene geometry and making the rendering look more realistic.
    SSAO, which this filter implements, is a screen-space (SS) realtime approximation of ambient occlusion (AO).

    It is important that the viewing frustum's near and far values fit the scene as tightly as possible,
    in order to get as much precision as possible from the depth buffer data which is needed to compute SSAO.

    (If the fit is not tight, a part of the representable data range will be wasted, leading to lower precision
     in the sub-range that is actually used, which may severely impact the rendering quality of SSAO, for which
     small differences in depth are crucial.)

    Note that you need to do lots of tweaking to the parameters to get this filter to work for your
    particular situation. 

    This filter is computationally intensive; at least a semi-recent GPU is recommended.

    """

    def __init__(self, **kwargs):
        super(AmbientOcclusion, self).__init__(**kwargs)


    def onReset(self):
        super(AmbientOcclusion, self).onReset()

        self.isMergeable = False
        self.stageName = "SceneOptics"
        self.sort = 50

        self.numsamples = 16
        self.amount     =  2.0
        self.radius     =  0.05
        self.strength   =  0.01
        self.falloff    =  0.000002


    def onAttachPipeline(self):
        # SSAO needs the scene textures depth and aux, but only in its internal stages;
        # the compositing pass does not need them.
        #
        # Hence, these textures must be made available in the stage input,
        # but the SSAO function call in the compositing shader does not need them.
        #
        # We request this by using requireSceneTexture().
        #
        self.requireSceneTexture(texName="depth")
        self.requireSceneTexture(texName="aux")
        self.requireAuxBits(bitmask=AuxBitplaneAttrib.ABOAuxNormal)

        # Note that we do *not* need to register any internally created textures
        # that are used only by the internal stages.
        #
        # "ssaoOutput" is registered because the blend pass in the compositing shader uses it.
        #
        self.registerInputTexture(texName="ssaoOutput")

    def onAttachStage(self):
        self.createInternalTextures( "ssao0", "ssao1", "ssao2", "ssaoOutput" )

        self.interQuads.append(self.pipeline.manager.renderQuadInto(colortex=self.get('texture')["ssao0"]))
        self.interQuads[0].setShaderInput("depth",  self.getTextureInfo("depth").get('texture'))
        self.interQuads[0].setShaderInput("normal", self.getTextureInfo("aux").get('texture'))
        self.interQuads[0].setShaderInput("random", loader.loadTexture("maps/random.rgb"))

        # Apply a medium-size blur to the SSAO result (see BlurSharpen for explanation of details)
        #
        # Here we render at quarter resolution. Three passes implies that the total number of fshader
        # calls = 75% of one full-resolution pass.
        #
        self.interQuads.append(self.pipeline.manager.renderQuadInto(colortex=self.get('texture')["ssao1"], div=2, align=2))
        self.interQuads[1].setShaderInput("src", self.getTextureInfo("ssao0").get('texture'))
        self.interQuads.append(self.pipeline.manager.renderQuadInto(colortex=self.get('texture')["ssao2"], div=2, align=2))
        self.interQuads[2].setShaderInput("src", self.getTextureInfo("ssao1").get('texture'))
        self.interQuads.append(self.pipeline.manager.renderQuadInto(colortex=self.get('texture')["ssaoOutput"], div=2, align=2))
        self.interQuads[3].setShaderInput("src", self.getTextureInfo("ssao2").get('texture'))


    def onCompileInternalStages(self):
        if self.numsamples < 1  or  self.numsamples > 16:
            raise ValueError("numsamples = %d out of range; valid: 1 ... 16" % self.numsamples)

        # numsamples affects code generation of the SSAO0 internal stage; we apply it here.
        # (It is used to circumvent the arbfp1 constant loop limit restriction.)
        #
        self.interQuads[0].setShader(Shader.make(SSAO0_SHADER % {"numsamples" : self.numsamples}))
        self.interQuads[1].setShader(self.loadShader("filter-copy.sha"))  # downscale to quarter resolution
        self.interQuads[2].setShader(self.loadShader("filter-blurx.sha"))
        self.interQuads[3].setShader(self.loadShader("filter-blury.sha"))


    def onSynthesizeCompositor(self):
        txssao = self.getTextureInfo("ssaoOutput")
        return ("ambientOcclusion",
                "pixcolor.rgb *= tex2D(%(k_txssao)s, %(texcoord_txssao)s).r;\n" % { "k_txssao"        : txssao.get('varname'),
                                                                                    "texcoord_txssao" : txssao.get('texcoord') },
                "// AmbientOcclusion blend pass\n")


    # The internal shader parameters "params1" and "params2" do not map directly to the user-given
    # parameter values, but several parameters are packed into each input. Also, params1.y contains
    # a pre-computed step value, which saves an instruction in the fshader.
    #
    # The parameter packing and computation is implemented in the _compute*() private methods.
    #
    def _computeParams1(self):
        return Vec4(self._numsamples, -float(self._amount) / self._numsamples, self._radius, 0.0)
    def _computeParams2(self):
        return Vec4(self._strength, self._falloff, 0.0, 0.0)


    @property
    def numsamples(self):
        """Number of samples used (maximum 16).

        Controls the rendering quality/speed tradeoff; the more samples are used, the more accurately
        it is possible to determine the appropriate amount of ambient occlusion at each pixel,
        but the rendering will be slower.

        """
        return self._numsamples
    @numsamples.setter
    def numsamples(self, value):
        # This requires a recompile, but only at the filter level, as numsamples affects the code
        # of the shaders in the internal stages (i.e. does not affect the code of the blend pass).
        #
        if (not hasattr(self, "_numsamples")  or  value != self._numsamples):
            self._needsCompile = True
        self._numsamples = value

        # Beside code generation, numsamples affects also the "params1" shader input,
        # because params1.y contains a pre-computed step parameter that depends on numsamples.
        #
        if len(self.interQuads)  and  self.interQuads[0] is not None:
            # Shader input names to internal stages are not mangled, because there
            # no name conflicts can occur (each Filter has its own internal stages).
            #
            self.interQuads[0].setShaderInput( "params1", self._computeParams1() )

    @property
    def amount(self):
        """Sets the strength at which the occlusion effect is blended onto the scene.

        The number of samples is automatically taken into account; the maximum occlusion amount
        is the same for the same numeric value of "amount" regardless how many "numsamples" are in use.

        """
        return self._amount
    @amount.setter
    def amount(self, value):
        self._amount = value
        if len(self.interQuads)  and  self.interQuads[0] is not None:
            self.interQuads[0].setShaderInput( "params1", self._computeParams1() )

    @property
    def radius(self):
        """The sampling radius of the rotating kernel.

        Controls how far from the original pixel the sampler looks (for each sample)
        when determining the occlusion contributions.

        The value set here is automatically scaled, accounting for the depth (along the view axis)
        of the original pixel.

        The numeric value of "radius" is the lookup distance, in texture coordinate units, for a pixel
        at the maximum representable distance from the camera (i.e. at the camera's "far" distance).

        """
        return self._radius
    @radius.setter
    def radius(self, value):
        self._radius = value
        if len(self.interQuads)  and  self.interQuads[0] is not None:
            self.interQuads[0].setShaderInput( "params1", self._computeParams1() )

    @property
    def strength(self):
        """Depth buffer difference (original_pixel - current_sample) at which the occlusion contribution
        of the each sample attains full intensity.
        
        See also "falloff".

        """
        return self._strength
    @strength.setter
    def strength(self, value):
        self._strength = value
        if len(self.interQuads)  and  self.interQuads[0] is not None:
            self.interQuads[0].setShaderInput( "params2", self._computeParams2() )

    @property
    def falloff(self):
        """Minimum depth buffer difference (original_pixel - current_sample) at which each sample
        triggers an occlusion contribution.

        Observe that this difference being positive means that original_pixel is deeper
        along the view axis than the potentially ambient-occluding pixel at current_sample.
        Hence, what this value means is "by how much" the sampled pixel must be closer to the camera
        to trigger any occlusion for the original pixel.

        (Note that the depth buffer is scaled so that 0.0 corresponds to the near distance and 1.0 corresponds
         to the far distance. The intermediate values are nonlinear with respect to the depth coordinate,
         as the depth buffer interpolates the perspective transformation (1/z) linearly.)

        Additionally, the surface normals at the two pixels are compared; the occlusion contribution
        is the stronger the closer the angle between the normals is to a right angle. If the surface normals
        are parallel, the sampled pixel causes no occlusion regardless of the depth criterion.

        (These checks combine to make a corner detection criterion.)

        See also "strength".

        """
        return self._falloff
    @falloff.setter
    def falloff(self, value):
        self._falloff = value
        if len(self.interQuads)  and  self.interQuads[0] is not None:
            self.interQuads[0].setShaderInput( "params2", self._computeParams2() )

