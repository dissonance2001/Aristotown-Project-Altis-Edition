from panda3d.core import Shader, AuxBitplaneAttrib, Vec4

from toontown.shader.Filter import Filter

# Screen-space local reflection (SSLR) shader.
#
# Original implementation by ninth on the Panda3D forums. One-pass blur adapted from suggestion by wezu.
#
# Original thread: 
#
# http://www.panda3d.org/forums/viewtopic.php?f=8&t=15742
#
# This is based on ssr_base.sha in SSLR_v2.zip, which seems to produce
# better results than ssr_zfar.sha at least on AMD cards.
#
# This shader generates the reflections, rendering them into an intermediate texture.
# Note that if the ray misses, the pixel will be colored with RGBA = (0,0,0,0).
#
# The alpha channel of the color texture is accounted for, allowing this filter
# to use the glow map (with ABOGlow) as a reflectivity map.
#
SSLR0_SHADER="""//Cg
//
//Cg profile glslv glslf

#define USE_GLOWMAP %(use_glowmap)d

// --------------------- Vertex program ----------------------------

void vshader(float4 vtx_position    : POSITION, 
             out float4 l_position  : POSITION,
             out float2 l_texcoord0 : TEXCOORD0,
             out float2 l_texcoord1 : TEXCOORD1,
             uniform float4 texpad_color,
             uniform float4x4 mat_modelproj)
{
    l_position  = mul(mat_modelproj, vtx_position);
    l_texcoord0 = (vtx_position.xz * texpad_color.xy) + texpad_color.xy;
    l_texcoord1 = vtx_position.xz;
}

// --------------------- Helper routines for fragment program ----------------------------

inline float linearizeDepth(float depth, float zNear, float zFar)
{
    return (2.0 * zNear) / (zFar + zNear - depth * (zFar - zNear));
}

float4 raytrace(in float3 startPos, 
                in float3 endPos, 
                uniform float4x4 mat_proj,
                uniform sampler2D k_color : TEXUNIT0,
                uniform sampler2D k_depth : TEXUNIT1,
                in float4 texpad_color,
                uniform float4 k_params1,
                uniform float4 k_params2)
{
    const float zNear    = k_params1.x;
    const float zFar     = k_params1.y;
    const float stepSize = k_params2.x;
    const float maxDelta = k_params2.y;
    const float strength = k_params2.z;

    // Convert start and end positions of reflect vector from the
    // camera space to the screen space
    float4 startPosSS = mul(mat_proj, float4(startPos,1));
    startPosSS /= startPosSS.w;
    startPosSS.xy = startPosSS.xy * texpad_color.xy + texpad_color.xy;
    float4 endPosSS = mul(mat_proj, float4(endPos,1));
    endPosSS /= endPosSS.w;
    endPosSS.xy = endPosSS.xy * texpad_color.xy + texpad_color.xy;
    // Reflection vector in the screen space
    float3 vectorSS = normalize(endPosSS.xyz - startPosSS.xyz)*stepSize;

    // Init vars for cycle
    float2 samplePos    = 0;  // texcoord for the depth and color
    float  sampleDepth  = 0;  // depth from texture
    float  currentDepth = 0;  // current depth calculated with reflection vector
    float  deltaD       = 0;
    float4 outputColor  = 0;
    for (int i = 1; i < %(maxsteps)d; i++)
    {
        samplePos    = (startPosSS.xy + vectorSS.xy*i);
        currentDepth = linearizeDepth( startPosSS.z + vectorSS.z*i, zNear, zFar );        
        sampleDepth  = linearizeDepth( f1tex2D(k_depth, samplePos), zNear, zFar );
        deltaD = currentDepth - sampleDepth;
        if ( deltaD > 0 && deltaD < maxDelta)
        {
            // Here we set outputColor.a to the reflection strength *assuming full reflectivity*.
            // If the glow map is used as a reflectivity map (with ABOGlow), we must account for
            // the alpha value of the point *where the ray originally bounced* (because that is the
            // fragment that we are coloring here).
            //
            // If we wanted to account for multiple bounces, then we would use also the alpha value
            // of the point where the ray ended up.
            //
            outputColor   = tex2D(k_color, samplePos);
            outputColor.a = strength / i;
            break;
        }
    }
    return outputColor;
}

// --------------------- Fragment program ----------------------------

void fshader(out float4 o_color : COLOR,
             uniform float4 k_params1,
             uniform float4 k_params2,
             float2 l_texcoord0 : TEXCOORD0,
             float2 l_texcoord1 : TEXCOORD1,
             uniform sampler2D k_color  : TEXUNIT0,
             uniform sampler2D k_depth  : TEXUNIT1,
             uniform sampler2D k_normal : TEXUNIT2,
             uniform float4x4 trans_clip_of_mcamera_to_view_of_mcamera,
             uniform float4x4 trans_view_of_mcamera_to_clip_of_mcamera,
             uniform float4 texpad_color)
{
    float4 N =   tex2D(k_normal, l_texcoord0);
    float  D = f1tex2D(k_depth,  l_texcoord0);

    // Camera Space position reconstruct
    float4 P;
    P.xy = l_texcoord1.xy;
    P.z  = D;
    P.w  = 1;
    P    = mul(trans_clip_of_mcamera_to_view_of_mcamera, P);
    P   /= P.w;

    // Ray direction vector (from camera origin to current fragment)
    float3 V = normalize(P.xyz);

    // Unbias fragment normal
    N.xyz = (N.xyz - 0.5) * 2.0;

    // Reflection vector in camera space
    float3 R = normalize(reflect(V.xyz, N.xyz));

    // Note that if the ray does not hit anything, the pixel will be colored with RGBA = (0,0,0,0).
    float4 C = raytrace(P.xyz, P.xyz + R, 
                        trans_view_of_mcamera_to_clip_of_mcamera, 
                        k_color, k_depth, texpad_color, k_params1, k_params2);

#if USE_GLOWMAP == 1
    // Account for glow map *at fragment being rendered* as reflectivity map,
    // modulating the reflection strength returned by raytrace() (which accounts
    // only for the fade-out of the ray as it travels).
    //
    C.a *= tex2D(k_color, l_texcoord0).a;
#endif

    o_color = C;
}
"""


# Compositing fshader snippet.
#
# Note that the reflection texture alpha channel already contains information about
# reflection strength, based on how far the ray travelled before hitting the second surface.
# Longer distance = dimmer reflection = smaller alpha value.
#
# It also factors in the original alpha value from the color texture, allowing the filter
# to use the glow map (with ABOGlow) as a reflectivity map.


# This version uses the reflection texture as-is without blurring.
#
# This is also used in the two-pass blur mode, where the input to the compositor
# is already blurred.
#
SSLR_BODY_SIMPLE="""float4 reflectionColor = tex2D( %(k_txsslr)s, %(texcoord_txsslr)s.xy );
pixcolor.rgb = lerp( pixcolor.rgb, reflectionColor.rgb, reflectionColor.a );"""


# This version applies a single-pass blur.
#
SSLR_BODY_ONEPASS="""// Hardcoded fast gaussian blur.
//
// Pixels where the ray did not hit anything have RGBA = (0,0,0,0). If we simply apply blur
// to all RGBA components, the black color from these zero-alpha pixels will (in the RGB components)
// mix with the actual reflection color.
//
// Thus, in the RGB components we weight the contributions by alpha, and adjust the scaling factor
// to match. This produces a weighted sum where the missed rays do not contribute.
//
const float2 samples[12] = {
    -0.326212, -0.405805,
    -0.840144, -0.073580,
    -0.695914,  0.457137,
    -0.203345,  0.620716,
     0.962340, -0.194983,
     0.473434, -0.480026,
     0.519456,  0.767022,
     0.185461, -0.893124,
     0.507431,  0.064425,
     0.896420,  0.412458,
    -0.321940, -0.932615,
    -0.791559, -0.597705
    };
const float radius = %(blur_radius)f;  // fraction of texture size (good values: 0.005, 0.01, 0.015)
float4 R = float4(0,0,0,1);
for(int i = 0 ; i < 12 ; ++i)
{
    float4 sample = tex2D(%(k_txsslr)s, %(texcoord_txsslr)s.xy + radius*samples[i]);
    R.rgb += sample.a*sample.rgb;
    R.a   += sample.a;
}

R.rgb /= R.a; // If alpha is 1.0 at all stencil positions, the divisor becomes 13
              // (the original scaling factor for this stencil).
              // 
              // The divisor is always at least 1.
R.a   /= 13;  // The alpha component is simply blurred in the usual way.

pixcolor.rgb = lerp( pixcolor.rgb, R.rgb, R.a );"""


# Shaders for two-pass blur.
#
# We cannot use filter-copy.sha, filter-blurx.sha and filter-blury.sha as-is,
# because they would mix in black from the pixels with RGBA = (0,0,0,0),
# where the ray did not hit anything.
#
# In the RGB components we must weight the contribution of each pixel by its fraction of total alpha
# contained in the stencil.

# Downscaler. Based on filter-copy4.sha, but with the special alpha processing.
#
SSLR_DOWNSCALE_SHADER="""//Cg
//
//Cg profile arbvp1 arbfp1

void vshader(float4 vtx_position     : POSITION,
             out float4 l_position   : POSITION,
             out float2 l_texcoordNW : TEXCOORD0,
             out float2 l_texcoordNE : TEXCOORD1,
             out float2 l_texcoordSW : TEXCOORD2,
             out float2 l_texcoordSE : TEXCOORD3,
             uniform float4 texpad_src,
             uniform float4 texpix_src,
             uniform float4x4 mat_modelproj)
{
    // We assume:
    //  - input at full resolution
    //  - output at quarter resolution

    l_position = mul(mat_modelproj, vtx_position);

    // Pixel center in output texture. In the input texture, with the assumed input/output resolutions,
    // this is exactly at the midway point between two pixels both in x and y directions.
    //
    // (Of course, strictly speaking, since this is a vshader, it will not process fragments.
    //  The result is that when the vertices of the fullscreen quad have been processed, 
    //  the comments made here on "pixel centers" are accurate for the linearly interpolated
    //  coordinate values that the fshader receives.)
    //
    float2 c = (vtx_position.xz * texpad_src.xy) + texpad_src.xy;

    // Participating pixel centers in input texture
    //
    float2 s = 0.5*texpix_src.xy;
    l_texcoordNW = c + float2( s.x, -s.y);
    l_texcoordNE = c + float2( s.x,  s.y);
    l_texcoordSW = c + float2(-s.x, -s.y);
    l_texcoordSE = c + float2(-s.x,  s.y);
}

void fshader(float2 l_texcoordNW : TEXCOORD0,
             float2 l_texcoordNE : TEXCOORD1,
             float2 l_texcoordSW : TEXCOORD2,
             float2 l_texcoordSE : TEXCOORD3,
             uniform sampler2D k_src : TEXUNIT0,
             out float4 o_color : COLOR)
{
    float4 colorNW = tex2D(k_src, l_texcoordNW);
    float4 colorNE = tex2D(k_src, l_texcoordNE);
    float4 colorSW = tex2D(k_src, l_texcoordSW);
    float4 colorSE = tex2D(k_src, l_texcoordSE);

    float3 rgb_sum = colorNW.a*colorNW.rgb + colorNE.a*colorNE.rgb
                   + colorSW.a*colorSW.rgb + colorSE.a*colorSE.rgb;
    float  a_sum   = colorNW.a + colorNE.a + colorSW.a + colorSE.a;

    if(a_sum < 1./255.)  // avoid division by zero
        o_color = float4(0,0,0,0);
    else
        o_color = float4(rgb_sum/a_sum, a_sum/4.0);  // normalize rgb, average the alpha
}
"""

### Equivalent, but with texture coordinates calculated in the fshader.
### (This is provided just for comparison, to show that the above version works correctly.)
###
##SSLR_DOWNSCALE_SHADER="""//Cg
##//
##//Cg profile arbvp1 arbfp1

##void vshader(float4 vtx_position   : POSITION,
##             out float4 l_position : POSITION,
##             out float2 l_texcoord : TEXCOORD0,
##             uniform float4 texpad_src,
##             uniform float4 texpix_src,
##             uniform float4x4 mat_modelproj)
##{
##    l_position = mul(mat_modelproj, vtx_position);
##    l_texcoord = (vtx_position.xz * texpad_src.xy) + texpad_src.xy;
##}

##void fshader(float2 l_texcoord : TEXCOORD0,
##             uniform float4 texpix_src,
##             uniform sampler2D k_src : TEXUNIT0,
##             out float4 o_color : COLOR)
##{
##    // We assume:
##    //  - input at full resolution
##    //  - output at quarter resolution

##    const float2 offs1 = 0.5*texpix_src.xy*float2(1,1);
##    const float2 offs2 = 0.5*texpix_src.xy*float2(1,-1);

##    float4 colorNW = tex2D(k_src, l_texcoord - offs2);
##    float4 colorNE = tex2D(k_src, l_texcoord + offs1);
##    float4 colorSW = tex2D(k_src, l_texcoord - offs1);
##    float4 colorSE = tex2D(k_src, l_texcoord + offs2);

##    float3 rgb_sum = colorNW.a*colorNW.rgb + colorNE.a*colorNE.rgb
##                   + colorSW.a*colorSW.rgb + colorSE.a*colorSE.rgb;
##    float  a_sum   = colorNW.a + colorNE.a + colorSW.a + colorSE.a;

##    if(a_sum < 1./255.)  // avoid division by zero
##        o_color = float4(0,0,0,0);
##    else
##        o_color = float4(rgb_sum/a_sum, a_sum/4.0);  // normalize rgb, average the alpha
##}
##"""


# Rectangular blur, x pass (3, 5 or 7 taps).
#
# We cannot use the optimized approach (which would need only 4 texture lookups for 7 taps),
# because the alpha values may be different in each pixel. Hence it would not be correct
# to directly retrieve linear combinations of pixels (since each pixel must have its
# rgb weighted by *its own* alpha).
#
SSLR_BLURX_SHADER="""//Cg
//
//Cg profile arbvp1 arbfp1

#define N %(ntaps)d

void vshader(float4 vtx_position    : POSITION, 
             float2 vtx_texcoord0   : TEXCOORD0,
             out float4 l_position  : POSITION,
               out float2 l_texcoord0 : TEXCOORD0,
             uniform float4 texpad_src,
             uniform float4x4 mat_modelproj)
{
    l_position  = mul(mat_modelproj, vtx_position);
    l_texcoord0 = (vtx_position.xz * texpad_src.xy) + texpad_src.xy;
}

void fshader(float2 l_texcoord0 : TEXCOORD0,
             out float4 o_color : COLOR,
             uniform float2 texpix_src,
             uniform sampler2D k_src : TEXUNIT0)
{
//    o_color = tex2D( k_src, l_texcoord0.xy );

#if N == 3
    const float offsets[N] = { -1.0, 0.0, 1.0 };
#elif N == 5
    const float offsets[N] = { -2.0, -1.0, 0.0, 1.0, 2.0 };
#elif N == 7
    const float offsets[N] = { -3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0 };
#endif

    float4 R = float4(0,0,0,0);
    for(int i = 0 ; i < N ; ++i)
    {
        float4 sample = tex2D( k_src, float2(l_texcoord0.x + offsets[i]*texpix_src.x, l_texcoord0.y) );
        R.rgb += sample.a*sample.rgb;
        R.a   += sample.a;
    }

    if(R.a < 1./255.)  // avoid division by zero
        o_color = float4(0,0,0,0);
    else
        o_color = float4(R.rgb/R.a, R.a/float(N));  // normalize rgb, average the alpha
}
"""

# Rectangular blur, y pass (3, 5 or 7 taps).
#
SSLR_BLURY_SHADER="""//Cg
//
//Cg profile arbvp1 arbfp1

#define N %(ntaps)d

void vshader(float4 vtx_position    : POSITION, 
             float2 vtx_texcoord0   : TEXCOORD0,
             out float4 l_position  : POSITION,
               out float2 l_texcoord0 : TEXCOORD0,
             uniform float4 texpad_src,
             uniform float4x4 mat_modelproj)
{
    l_position  = mul(mat_modelproj, vtx_position);
    l_texcoord0 = (vtx_position.xz * texpad_src.xy) + texpad_src.xy;
}

void fshader(float2 l_texcoord0 : TEXCOORD0,
             out float4 o_color : COLOR,
             uniform float2 texpix_src,
             uniform sampler2D k_src : TEXUNIT0)
{
//    o_color = tex2D( k_src, l_texcoord0.xy );

#if N == 3
    const float offsets[N] = { -1.0, 0.0, 1.0 };
#elif N == 5
    const float offsets[N] = { -2.0, -1.0, 0.0, 1.0, 2.0 };
#elif N == 7
    const float offsets[N] = { -3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0 };
#endif

    float4 R = float4(0,0,0,0);
    for(int i = 0 ; i < N ; ++i)
    {
        float4 sample = tex2D( k_src, float2(l_texcoord0.x, l_texcoord0.y + offsets[i]*texpix_src.y) );
        R.rgb += sample.a*sample.rgb;
        R.a   += sample.a;
    }

    if(R.a < 1./255.)  // avoid division by zero
        o_color = float4(0,0,0,0);
    else
        o_color = float4(R.rgb/R.a, R.a/float(N));  // normalize rgb, average the alpha
}
"""


class LocalReflection(Filter):
    """Raytracing filter, which simulates reflection.

    The glow map can be used to control the reflectivity.

    The implementation is based on SSLR (screen-space local reflection), which is a screen-space
    realtime approximation of reflection. SSLR works by raytracing, but using only the information
    available in the fragment normals, depth buffer and color texture (image on screen).

    SSLR has screen-space complexity, i.e. its render time is independent of the complexity
    of the scene being rendered.

    The drawback is that because SSLR works in the screen space, it can only reflect pixels
    actually already on the screen; it has no access to occluded parts of objects. It is not intended
    to replace environment mapping and reflections using auxiliary cameras, but instead offer
    an alternative technique that can produce good results in some cases (e.g. shiny floors).

    The reflections are "local" in the sense that the raytracing of the reflected ray is terminated
    after a (configurable) maximum distance, if the ray has not hit anything.

    It is important that the viewing frustum's near and far values fit the scene as tightly as possible,
    in order to get as much precision as possible from the depth buffer data which is needed to determine
    ray collisions in SSLR.

    (If the fit is not tight, a part of the representable data range will be wasted, leading to
     lower precision in the sub-range that is actually used, which may impact the rendering
     quality of SSLR. If you see banding artifacts in the reflections, it is most likely due to this.)

    Note that you may need to tweak the parameters to get this filter to work for your
    particular situation. 

    This filter is computationally intensive; at least a semi-recent GPU is recommended.

    """

    def __init__(self, **kwargs):
        super(LocalReflection, self).__init__(**kwargs)

        # super's init will call cleanup(), which will call detach(), which triggers setdown(),
        # so we don't need to set self._compositor here.


    def onReset(self):
        super(LocalReflection, self).onReset()

        # dummy values for initialization, will be overridden by onUpdate()
        self._zNear =  1.0
        self._zFar  = 10.0

        self.isMergeable = False
        self.stageName = "SceneOptics"
        self.sort = 40  # SSLR needs to render before AmbientOcclusion and VolumetricLighting

        self.maxSteps = 30

        self.stepSize = 0.005
        self.maxDelta = 0.001
        self.strength = 5.0

        self.blurType = "twopass"  # "off", "onepass", "twopass"
        self.blurSize = "medium"   # "small", "medium", "large"

        self.useGlowMap = False


    def onAttachPipeline(self):
        # SSLR needs the scene textures depth and aux, but only in its internal stages;
        # the compositing pass does not need them.
        #
        # (The same applies to the color scene texture, because the compositing pass
        #  only needs pixcolor, which is always available.)
        #
        # Hence, these textures must be made available in the stage input,
        # but the SSLR function call in the compositing shader does not need them.
        #
        # We request this by using requireSceneTexture().
        #
        self.requireSceneTexture(texName="color")
        self.requireSceneTexture(texName="depth")
        self.requireSceneTexture(texName="aux")

        auxbits = AuxBitplaneAttrib.ABOAuxNormal
        if self.useGlowMap:  # this allows use of glow map as reflectivity map
            auxbits |= AuxBitplaneAttrib.ABOGlow
        self.requireAuxBits(bitmask=auxbits)

        # Note that we do *not* need to register any internally created textures
        # that are used only by the internal stages.
        #
        # "sslrOutput" is registered because the blend pass in the compositing shader uses it.
        #
        self.registerInputTexture(texName="sslrOutput")

        # Filters defining onUpdate() must register themselves as "updatable", which means
        # onUpdate() will actually get called.
        #
        self.registerUpdatable()


    def onAttachStage(self):
        # Sanity check
        #
        if self.blurType not in ["off", "onepass", "twopass"]:
            raise ValueError("In %s %s: unknown blur type '%s'; valid: 'off', 'onepass', 'twopass'." % (self.__class__.__name__, self.name, self.blurType))

        # Set up internal stages
        #
        if self.blurType == "twopass":
            self.createInternalTextures( "sslr0", "sslr1", "sslr2", "sslrOutput" )
            self._compositor = SSLR_BODY_SIMPLE

            self.interQuads.append(self.pipeline.manager.renderQuadInto(colortex=self.get('texture')["sslr0"]))
            self.interQuads[0].setShaderInput("color",  self.getTextureInfo("color").get('texture'))
            self.interQuads[0].setShaderInput("depth",  self.getTextureInfo("depth").get('texture'))
            self.interQuads[0].setShaderInput("normal", self.getTextureInfo("aux").get('texture'))

            # Apply a medium-size blur to the SSLR result.
            #
            # Here we render at quarter resolution. Three passes implies that the total number of fshader
            # calls = 75% of one full-resolution pass.
            #
            self.interQuads.append(self.pipeline.manager.renderQuadInto(colortex=self.get('texture')["sslr1"], div=2, align=2))
            self.interQuads[1].setShaderInput("src", self.getTextureInfo("sslr0").get('texture'))

            self.interQuads.append(self.pipeline.manager.renderQuadInto(colortex=self.get('texture')["sslr2"], div=2, align=2))
            self.interQuads[2].setShaderInput("src", self.getTextureInfo("sslr1").get('texture'))

            self.interQuads.append(self.pipeline.manager.renderQuadInto(colortex=self.get('texture')["sslrOutput"], div=2, align=2))
            self.interQuads[3].setShaderInput("src", self.getTextureInfo("sslr2").get('texture'))

        else:
            self.createInternalTextures( "sslrOutput" )
            if self.blurType == "onepass":
                self._compositor = SSLR_BODY_ONEPASS
            else: # self.blurType == "off":
                self._compositor = SSLR_BODY_SIMPLE

            self.interQuads.append(self.pipeline.manager.renderQuadInto(colortex=self.get('texture')["sslrOutput"]))
            self.interQuads[0].setShaderInput("color",  self.getTextureInfo("color").get('texture'))
            self.interQuads[0].setShaderInput("depth",  self.getTextureInfo("depth").get('texture'))
            self.interQuads[0].setShaderInput("normal", self.getTextureInfo("aux").get('texture'))


    def onDetachStage(self):
        # self.interQuads and self.get('texture') are cleaned up by detachStage() automatically.
        #
        self._compositor = None


    def onCompileInternalStages(self):
        if self.maxSteps < 1:
            raise ValueError("maxSteps = %d out of range; valid: >= 1" % self.maxSteps)
        if self.blurType == "twopass"  and  self.blurSize not in ["small", "medium", "large"]:
            raise ValueError("In %s %s: unknown blur size '%s'; valid: 'small', 'medium', 'large'." % (self.__class__.__name__, self.name, self.blurSize))

        # maxSteps affects code generation of the SSAO0 internal stage; we apply it here.
        # (It is used to circumvent the arbfp1 constant loop limit restriction.)
        #
        self.interQuads[0].setShader(Shader.make(SSLR0_SHADER % {"maxsteps" : self.maxSteps,
                                                                 "use_glowmap" : self.useGlowMap}))

        if self.blurType == "twopass":
            blurTaps = { "small" : 3, "medium" : 5, "large" : 7 }

            self.interQuads[1].setShader(Shader.make(SSLR_DOWNSCALE_SHADER))
            self.interQuads[2].setShader(Shader.make(SSLR_BLURX_SHADER % {"ntaps" : blurTaps[self.blurSize]}))
            self.interQuads[3].setShader(Shader.make(SSLR_BLURY_SHADER % {"ntaps" : blurTaps[self.blurSize]}))


    def onSynthesizeCompositor(self):
        assert( self._compositor is not None )

        if self.blurSize not in ["small", "medium", "large"]:
            raise ValueError("In %s %s: unknown blur size '%s'; valid: 'small', 'medium', 'large'." % (self.__class__.__name__, self.name, self.blurSize))

        # This is needed only in onepass blur mode.
        blurRadii = { "small" : 0.005, "medium" : 0.010, "large" : 0.015 }

        txsslr = self.getTextureInfo("sslrOutput")
        return ("localReflection",
                self._compositor % { "k_txsslr"        : txsslr.get('varname'),
                                     "texcoord_txsslr" : txsslr.get('texcoord'),
                                     "blur_radius"     : blurRadii[self.blurSize] },
                "// LocalReflection blend pass (blur mode: %s)\n" % (self.blurType))


    def onUpdate(self):
        # Update shader inputs that need to be updated each frame.
        #
        # This only gets called while the filter is running
        # (so self.pipeline and self.finalQuad are always valid here).

        # Send the camera reference (to supply the magic coordinate space conversion matrices)
        # and the camera's near/far distances to the internal shader.
        #
        # self.pipeline.manager.camera gives the actual camera NodePath (like base.win.cam)
        # to which the FilterManager (controlled by FilterPipeline) has been applied.
        #
        cam  = self.pipeline.manager.camera
        lens = cam.node().getLens()
        self._zNear = lens.getNear()
        self._zFar  = lens.getFar()
        if len(self.interQuads)  and  self.interQuads[0] is not None:
            self.interQuads[0].setShaderInput( "mcamera", cam )
            self.interQuads[0].setShaderInput( "params1", self._computeParams1() )


    # The internal shader parameter "params1" and "params2" do not map directly to the user-given
    # parameter values, but several parameters are packed into each input. Also, params1.y contains
    # a pre-computed step value, which saves an instruction in the fshader.
    #
    # The parameter packing and computation is implemented in the _compute*() private methods.
    #
    def _computeParams1(self):
        return Vec4(self._zNear, self._zFar, 0.0, 0.0)
    def _computeParams2(self):
        return Vec4(self._stepSize, self._maxDelta, self._strength, 0.0)


    @property
    def maxSteps(self):
        """Maximum number of steps taken in raytracing [default: 30].

        Maximum total distance travelled by one ray is maxSteps*stepSize. The tracing is terminated
        at the maximum distance, or at a surface hit by the ray, whichever comes first.

        Note that at a large majority of pixels nothing will be reflected, so for most pixels the
        maximum number of steps is calculated.

        Significantly affects rendering speed.

        Setting this to a value that is too large may fail on non-NVIDIA cards due to limitations
        of the Cg compiler, regardless of the actual capabilities of the hardware. (When this happens,
        the Cg compiler prints the error "Cg program too complex for driver" into the terminal window
        where Panda3D is being run. If it happens, try a smaller value for maxSteps.)

        """
        return self._maxSteps
    @maxSteps.setter
    def maxSteps(self, value):
        # This requires a recompile, but only at the filter level, as maxSteps affects the code
        # of the shaders in the internal stages (i.e. does not affect the code of the blend pass).
        #
        if (not hasattr(self, "_maxSteps")  or  value != self._maxSteps):
            self._needsCompile = True
        self._maxSteps = value

    @property
    def stepSize(self):
        """Length of one raytracing step [default: 0.005].

        Up to maxSteps steps are taken for each pixel.

        """
        return self._stepSize
    @stepSize.setter
    def stepSize(self, value):
        self._stepSize = value
        if len(self.interQuads)  and  self.interQuads[0] is not None:
            self.interQuads[0].setShaderInput( "params2", self._computeParams2() )

    @property
    def maxDelta(self):
        """Depth delta threshold for collision checking in the raytracer [default: 0.001].

        The reflecting point is considered found and the raytracing terminates before maxSteps if

          z_ray > z_sample  and  (z_ray - z_sample) < maxDelta

        where z_ray is the linear depth coordinate of the current point on the ray (in camera space),
        and z_sample is the linear depth coordinate of the fragment being tested.

        In other words, to find a reflection, the ray must penetrate into a surface,
        but "not too much".

        """
        return self._maxDelta
    @maxDelta.setter
    def maxDelta(self, value):
        self._maxDelta = value
        if len(self.interQuads)  and  self.interQuads[0] is not None:
            self.interQuads[0].setShaderInput( "params2", self._computeParams2() )

    @property
    def strength(self):
        """Strength of the reflection [default: 5.0].

        This parameter scales the reflection intensity by a constant factor,
        causing reflections to carry a larger distance before fading out.

        However, if strength is too large, the reflection may become abruptly clipped
        when the maximum distance (maxSteps*stepSize) is reached.

        """
        return self._strength
    @strength.setter
    def strength(self, value):
        self._strength = value
        if len(self.interQuads)  and  self.interQuads[0] is not None:
            self.interQuads[0].setShaderInput( "params2", self._computeParams2() )

    @property
    def blurType(self):
        """Type of postprocessing blur applied to the reflections [default: "twopass"].

        String, one of:

            off     = No blurring. Reflections will be shown as-is;
                      at this setting, there may be visible artifacts.

            onepass = A single-pass blur is applied.

            twopass = A two-pass blur is applied.

        """
        return self._blurType
    @blurType.setter
    def blurType(self, value):
        if value not in ["off", "onepass", "twopass"]:
            raise ValueError("In %s %s: unknown blur type '%s'; valid: 'off', 'onepass', 'twopass'." % (self.__class__.__name__, self.name, value))
        # This requires a re-setup of internal stages, so a pipeline compile is needed.
        if (not hasattr(self, "_maxSteps")  or  value != self._maxSteps)  and  self.pipeline is not None:
            self.pipeline._needsCompile = True
        self._blurType = value

    @property
    def blurSize(self):
        """Size of blurring of reflections, if enabled.

        If blurType is set to "off", this setting is ignored.

        String, one of "small", "medium" [default] or "large".

        This works differently in onepass and twopass modes:

            onepass: controls the radius of the blur kernel.
                     The number of taps is constant; hence smaller blurs
                     tend to look better.

            twopass: controls the number of taps in the blur kernel,
                     thereby affecting also its radius. Larger blurs
                     sample more; visual quality is constant across
                     the different values of this setting.

        """
        return self._blurSize
    @blurSize.setter
    def blurSize(self, value):
        if value not in ["small", "medium", "large"]:
            raise ValueError("In %s %s: unknown blur size '%s'; valid: 'small', 'medium', 'large'." % (self.__class__.__name__, self.name, value))

        # In twopass mode, this requires a recompile at the filter level.
        #
        # In onepass mode, the blur size configuration is in the compositor, and hence
        # if we recompile, we must recompile the whole pipeline.
        #
        # We could add a shader input to support blur size changes in onepass mode without recompiling,
        # but it is much simpler to just always recompile the pipeline.
        #
        if (not hasattr(self, "_blurSize")  or  value != self._blurSize)  and  self.pipeline is not None:
            self.pipeline._needsCompile = True
        self._blurSize = value

    @property
    def useGlowMap(self):
        """Enable/disable use of the glow map as a reflectivity map.

        Boolean.

        If True, the glow map is interpreted (by this filter, independent of how other filters
        in the same pipeline may interpret it!) as the reflectivity of the material.

        If False [default], all surfaces are assumed to have reflectivity of 1.0 (maximally reflective).

        Note that in either case, the overall strength of the reflection effect can be controlled
        via the "strength" parameter.

        """
        return self._useGlowMap
    @useGlowMap.setter
    def useGlowMap(self, value):
        # Changing this setting means that the filter has to require new auxbits.
        # Hence this really needs a rebuild of the whole pipeline.
        #
        # It also requires a filter recompile due to the compile option change
        # in SSLR0_SHADER, but a pipeline compile automatically invokes also
        # filter recompiles.
        #
        if (not hasattr(self, "_useGlowMap")  or  value != self._useGlowMap)  and  self.pipeline is not None:
            self.pipeline._needsCompile = True
        self._useGlowMap = value

