from panda3d.core import AuxBitplaneAttrib, Vec4, Shader

from toontown.shader.Filter import Filter

# This first pass is a modified version of the Panda 1.8.1 inker with some bugfixes and new features.
#
# New features:
#  - "mult" and "cutoff" are now parameters.
#  - The depth buffer is supported as a data source for detecting discontinuities.
#  - Option for depth-sensitive separation has been added.
#
# Bugfixes:
#  - All three (xyz) components of the fragment normal are accounted for in the default "mult".
#  - This pass no longer attempts to fade the ink. Instead, the result is hard-thresholded.
#    It was found that the fading approach does not always produce the expected fade,
#    but for some scenes may actually "shade in reverse" producing additional "jags".
#    It is better to smooth the ink in a second render pass (as CartoonInkThick does),
#    or to use an area-based voting algorithm (see CartoonInkThin).
#
CARTOONINK0_SHADER="""//Cg
//
//Cg profile arbvp1 arbfp1

#define USE_DEPTH_MODSEP %(depth_modsep)d
#define USE_DEPTH_DETECTION %(depth_detect)d
#define USE_NORMALS_DETECTION %(normals_detect)d

void vshader(float4 vtx_position : POSITION,
             out float4 l_position : POSITION,
#if USE_NORMALS_DETECTION == 1
             uniform float4 texpad_txaux,
             uniform float4 texpix_txaux,
             out float2 l_texcoord_txaux   : TEXCOORD0,
#endif
#if USE_DEPTH_DETECTION == 1  ||  USE_DEPTH_MODSEP == 1
             uniform float4 texpad_txdepth,
             uniform float4 texpix_txdepth,
             out float2 l_texcoord_txdepth : TEXCOORD1,
#endif
             uniform float4x4 mat_modelproj)
{
    l_position = mul(mat_modelproj, vtx_position);

#if USE_NORMALS_DETECTION == 1
    l_texcoord_txaux   = (vtx_position.xz * texpad_txaux.xy)   + texpad_txaux.xy;
#endif

#if USE_DEPTH_DETECTION == 1  ||  USE_DEPTH_MODSEP == 1
    l_texcoord_txdepth = (vtx_position.xz * texpad_txdepth.xy) + texpad_txdepth.xy;
#endif
}

void fshader(out float4 o_color : COLOR,
#if USE_NORMALS_DETECTION == 1
             float2 l_texcoord_txaux   : TEXCOORD0,
             uniform float4 texpix_txaux,
             uniform sampler2D k_txaux,
#endif
#if USE_DEPTH_DETECTION == 1  ||  USE_DEPTH_MODSEP == 1
             float2 l_texcoord_txdepth : TEXCOORD1,
             uniform float4 texpix_txdepth,
             uniform sampler2D k_txdepth,
#endif
             uniform float4 k_cartoonseparation,
             uniform float4 k_cartooncolor,
             uniform float  k_cutoff_normals,
             uniform float  k_cutoff_depth,
             uniform float4 k_mult)
{
#if USE_DEPTH_MODSEP == 1
  // Depth-enabled inking (thicker line near camera).
  //
  // depth is always in the range 0.0 ... 1.0, corresponding to the camera's near and far distances.
  //
  // (Note that the depth buffer interpolates 1/z linearly, not z itself. But this is exactly what we want:
  //  the line thickness on the screen should depend on the perspective transformation, not on the actual
  //  value of the z coordinate.)
  //
  float cartoon_depth = tex2D(k_txdepth, l_texcoord_txdepth);
  float cartoon_depth_coeff = 0.5 + 1.5*smoothstep(0.0, 1.0, 1.0 - cartoon_depth*cartoon_depth*cartoon_depth);
#else
  float cartoon_depth_coeff = 1.0;
#endif


#if USE_NORMALS_DETECTION == 1
  // Detect edges from normal map.
  //
  float4 cartoondeltaN = cartoon_depth_coeff * k_cartoonseparation * texpix_txaux.xwyw;
  float4 cartoon_c0N = tex2D(k_txaux, l_texcoord_txaux + cartoondeltaN.xy);
  float4 cartoon_c1N = tex2D(k_txaux, l_texcoord_txaux - cartoondeltaN.xy);
  float4 cartoon_c2N = tex2D(k_txaux, l_texcoord_txaux + cartoondeltaN.wz);
  float4 cartoon_c3N = tex2D(k_txaux, l_texcoord_txaux - cartoondeltaN.wz);
  float4 cartoon_mxN = max(cartoon_c0N, max(cartoon_c1N, max(cartoon_c2N, cartoon_c3N)));
  float4 cartoon_mnN = min(cartoon_c0N, min(cartoon_c1N, min(cartoon_c2N, cartoon_c3N)));
  float inkN = step(k_cutoff_normals, dot(cartoon_mxN - cartoon_mnN, k_mult));
#endif

#if USE_DEPTH_DETECTION == 1
  // Detect edges from depth buffer.
  //
  float4 cartoondeltaD = cartoon_depth_coeff * k_cartoonseparation * texpix_txdepth.xwyw;
  float4 cartoon_c0D = tex2D(k_txdepth, l_texcoord_txdepth + cartoondeltaD.xy);
  float4 cartoon_c1D = tex2D(k_txdepth, l_texcoord_txdepth - cartoondeltaD.xy);
  float4 cartoon_c2D = tex2D(k_txdepth, l_texcoord_txdepth + cartoondeltaD.wz);
  float4 cartoon_c3D = tex2D(k_txdepth, l_texcoord_txdepth - cartoondeltaD.wz);
  float4 cartoon_mxD = max(cartoon_c0D, max(cartoon_c1D, max(cartoon_c2D, cartoon_c3D)));
  float4 cartoon_mnD = min(cartoon_c0D, min(cartoon_c1D, min(cartoon_c2D, cartoon_c3D)));
  float inkD = step(k_cutoff_depth, cartoon_mxD - cartoon_mnD);
#endif


  // Determine inking result.
  //
#if USE_NORMALS_DETECTION == 1  &&  USE_DEPTH_DETECTION == 1
  float ink = max(inkN, inkD);
#elif USE_NORMALS_DETECTION == 1
  float ink = inkN;
#elif USE_DEPTH_DETECTION == 1
  float ink = inkD;
#else
  float ink = 0.0;  // no detector enabled - no ink
#endif


  // In the ink texture, we use a zero-alpha placeholder color for non-inked pixels.
  //
  // This makes an outlines-only picture visible in Panda's BufferViewer (it ignores the alpha component).
  //
  // Note that we use only the alpha channel from this ink texture when we blend the ink in the second pass,
  // so it doesn't matter what ends up in the RGB components in the ink texture.
  //
  // It is important to use k_cartooncolor, though, because its alpha might not be 1.0.
  // This also makes the intermediate result look clearer in the buffer viewer, as it shows
  // that the inker is using the color that was specified by the user.
  //
  o_color = lerp(float4(0.5, 0.5, 0.5, 0.0), k_cartooncolor, ink);
}
"""


# This is a second-pass code that performs antialiasing and blends the ink onto the scene.
#
# The input to this should be fully inked (thresholded) with no smoothing; this algorithm
# tends to cause a fuzzy look when it smooths out already antialiased pixels from the original input.
#
CARTOONINK_BODY="""
// This postproc can be understood as a specialized anisotropic blur filter.
//
// The idea is to look for "runs" of pixels (in the ink texture) representing a line,
// and partially ink pixels (with a suitable strength) if a line stepping onto the
// current pixel row/column is detected.
//
// However, because we are running in an fshader, we must work in a local manner.
// We must look at the neighbours of the pixel being rendered; run lengths cannot be computed globally.
//
//
// Locally speaking, we want to detect ink patterns like this
// (o = current pixel, # = fully inked pixel):
//
//  #     ##     ##
// #o    #o     # o
// 0.5   0.66   0.33   <- desired ink amount at 'o'
//
// plus all 90 degree mirrorings and flips. (Observe that also the "upper side" will be handled
// similarly when those pixels are processed.)
//
// To do this, we build a 5x5 stencil. Numbering (x = not used):
//
//  x  x  8  x  x
//  x  0  1  2  x
//  9  3  x  4 10 
//  x  5  6  7  x
//  x  x 11  x  x
//
// If we only wanted to check
//
//  #
// #o
// 0.5   <- desired ink amount at 'o'
//
// we would only need this subset:
//
//  x  1  x
//  3  x  4
//  x  6  x
//
// This needs 4 texture lookups, so we see that expanding the stencil to 5x5
// has added 8 more texture lookups.

const float4 ink_delta1 = %(texpix_txink0)s.xwyw;     // any coordinate axis aligned element
const float2 ink_delta2 = %(texpix_txink0)s.xy;       // corners 0, 7
const float2 ink_delta3 = float2(1,-1) * ink_delta2;  // corners 2, 5

const float2 ink0_p00 = %(texcoord_txink0)s - ink_delta2;
const float2 ink0_p01 = %(texcoord_txink0)s - ink_delta1.wz;
const float2 ink0_p02 = %(texcoord_txink0)s + ink_delta3;
const float2 ink0_p03 = %(texcoord_txink0)s - ink_delta1.xy;
const float2 ink0_p04 = %(texcoord_txink0)s + ink_delta1.xy;
const float2 ink0_p05 = %(texcoord_txink0)s - ink_delta3;
const float2 ink0_p06 = %(texcoord_txink0)s + ink_delta1.wz;
const float2 ink0_p07 = %(texcoord_txink0)s + ink_delta2;
const float2 ink0_p08 = %(texcoord_txink0)s - 2.0*ink_delta1.wz;
const float2 ink0_p09 = %(texcoord_txink0)s - 2.0*ink_delta1.xy;
const float2 ink0_p10 = %(texcoord_txink0)s + 2.0*ink_delta1.xy;
const float2 ink0_p11 = %(texcoord_txink0)s + 2.0*ink_delta1.wz;

// To expand the detection to deal with this:
//
//  #     ##     ##     ###     ###     ###
// #o    #o     # o    #o      # o     #  o
// 0.5   0.66   0.33   0.75    0.50    0.25   <- desired ink amount at 'o'
// A     B      C      D       E       F      <- pattern name (for note below)
//
// we can go one pixel further, using a 7x7 stencil:
//
//  x  x  x 12  x  x  x
//  x  x 13  8 14  x  x
//  x 15  0  1  2 16  x
// 17  9  3  x  4 10 18
//  x 19  5  6  7 20  x
//  x  x 21 11 22  x  x
//  x  x  x 23  x  x  x
//
// This needs 12 more texture lookups, because now there are no overlaps between the
// different 90 degree rotated patterns. This is the general case; adding one more pixel of
// checking distance requires adding a "V" shape of 3 pixels in each cardinal direction.
//
// We see that the local approach quickly becomes expensive, so it is not really sensible to
// extend it beyond 7x7 (which already needs 24 texture lookups in total).
//
// Note that the desired ink strengths for the overlapping patterns (A, B, D; C, E) are ordered
// in the following manner:
//
//  D > B > A
//  E > C
//
// Hence, if we use the maximum of the ink strengths of the matching patterns,
// "a longer line wins", and this behaves as expected.

const float2 ink_delta4 = float2( 1, 2) * ink_delta2;  // 13, 22
const float2 ink_delta5 = float2(-1, 2) * ink_delta2;  // 14, 21
const float2 ink_delta6 = float2( 2, 1) * ink_delta2;  // 15, 20
const float2 ink_delta7 = float2(-2, 1) * ink_delta2;  // 16, 19

const float2 ink0_p12 = %(texcoord_txink0)s - 3.0*ink_delta1.wz;
const float2 ink0_p13 = %(texcoord_txink0)s - ink_delta4;
const float2 ink0_p14 = %(texcoord_txink0)s - ink_delta5;
const float2 ink0_p15 = %(texcoord_txink0)s - ink_delta6;
const float2 ink0_p16 = %(texcoord_txink0)s - ink_delta7;
const float2 ink0_p17 = %(texcoord_txink0)s - 3.0*ink_delta1.xy;
const float2 ink0_p18 = %(texcoord_txink0)s + 3.0*ink_delta1.xy;
const float2 ink0_p19 = %(texcoord_txink0)s + ink_delta7;
const float2 ink0_p20 = %(texcoord_txink0)s + ink_delta6;
const float2 ink0_p21 = %(texcoord_txink0)s + ink_delta5;
const float2 ink0_p22 = %(texcoord_txink0)s + ink_delta4;
const float2 ink0_p23 = %(texcoord_txink0)s + 3.0*ink_delta1.wz;


// ink presence testing
//
// The ink texture uses a placeholder color; only the alpha value is meaningful.
//
// Although the first pass applies ink fully or not at all, the threshold here is needed
// because k_cartooncolor might have alpha less than 1.0.
//
#define CARTOON_THRESHOLD 1.0/200.0
const float ink0_b00 = step(CARTOON_THRESHOLD, tex2D(%(k_txink0)s, ink0_p00).a);
const float ink0_b01 = step(CARTOON_THRESHOLD, tex2D(%(k_txink0)s, ink0_p01).a);
const float ink0_b02 = step(CARTOON_THRESHOLD, tex2D(%(k_txink0)s, ink0_p02).a);
const float ink0_b03 = step(CARTOON_THRESHOLD, tex2D(%(k_txink0)s, ink0_p03).a);
const float ink0_b04 = step(CARTOON_THRESHOLD, tex2D(%(k_txink0)s, ink0_p04).a);
const float ink0_b05 = step(CARTOON_THRESHOLD, tex2D(%(k_txink0)s, ink0_p05).a);
const float ink0_b06 = step(CARTOON_THRESHOLD, tex2D(%(k_txink0)s, ink0_p06).a);
const float ink0_b07 = step(CARTOON_THRESHOLD, tex2D(%(k_txink0)s, ink0_p07).a);
const float ink0_b08 = step(CARTOON_THRESHOLD, tex2D(%(k_txink0)s, ink0_p08).a);
const float ink0_b09 = step(CARTOON_THRESHOLD, tex2D(%(k_txink0)s, ink0_p09).a);
const float ink0_b10 = step(CARTOON_THRESHOLD, tex2D(%(k_txink0)s, ink0_p10).a);
const float ink0_b11 = step(CARTOON_THRESHOLD, tex2D(%(k_txink0)s, ink0_p11).a);

const float ink0_b12 = step(CARTOON_THRESHOLD, tex2D(%(k_txink0)s, ink0_p12).a);
const float ink0_b13 = step(CARTOON_THRESHOLD, tex2D(%(k_txink0)s, ink0_p13).a);
const float ink0_b14 = step(CARTOON_THRESHOLD, tex2D(%(k_txink0)s, ink0_p14).a);
const float ink0_b15 = step(CARTOON_THRESHOLD, tex2D(%(k_txink0)s, ink0_p15).a);
const float ink0_b16 = step(CARTOON_THRESHOLD, tex2D(%(k_txink0)s, ink0_p16).a);
const float ink0_b17 = step(CARTOON_THRESHOLD, tex2D(%(k_txink0)s, ink0_p17).a);
const float ink0_b18 = step(CARTOON_THRESHOLD, tex2D(%(k_txink0)s, ink0_p18).a);
const float ink0_b19 = step(CARTOON_THRESHOLD, tex2D(%(k_txink0)s, ink0_p19).a);
const float ink0_b20 = step(CARTOON_THRESHOLD, tex2D(%(k_txink0)s, ink0_p20).a);
const float ink0_b21 = step(CARTOON_THRESHOLD, tex2D(%(k_txink0)s, ink0_p21).a);
const float ink0_b22 = step(CARTOON_THRESHOLD, tex2D(%(k_txink0)s, ink0_p22).a);
const float ink0_b23 = step(CARTOON_THRESHOLD, tex2D(%(k_txink0)s, ink0_p23).a);


// Test presence of short line segments (up to 4 pixels).
//
// Here:
//   - u = up, d = down, l = left, r = right
//   - the first part of the number suffix indicates distance (in pixels) of the outermost pixel tested,
//     from center pixel
//   - the second part of the number suffix indicates distance from the "step" in the line
//
// E.g.: For ink0_u2_2, pixel 8 must have ink, and in addition 0 and 3, or 2 and 4, must have ink.
//       For ink0_u2_1, pixel 1 must have ink, and in addition 3 and 5, or 4 and 7, must have ink.
//
// Diagram repeated for convenience:
//
//  x  x  x 12  x  x  x
//  x  x 13  8 14  x  x
//  x 15  0  1  2 16  x
// 17  9  3  x  4 10 18
//  x 19  5  6  7 20  x
//  x  x 21 11 22  x  x
//  x  x  x 23  x  x  x

// Lines stepping onto this row/column three pixels away
//
// Note each result is 0, 1, 2 depending on number of matching lines detected.
//
//  ###
// #  o
// 0.25
//
const float  ink0_u3_3 = ink0_b12 * (ink0_b13*ink0_b00*ink0_b03 + ink0_b14*ink0_b02*ink0_b04);
const float  ink0_d3_3 = ink0_b23 * (ink0_b03*ink0_b05*ink0_b21 + ink0_b04*ink0_b07*ink0_b22);
const float  ink0_l3_3 = ink0_b17 * (ink0_b15*ink0_b00*ink0_b01 + ink0_b19*ink0_b05*ink0_b06);
const float  ink0_r3_3 = ink0_b18 * (ink0_b01*ink0_b02*ink0_b16 + ink0_b06*ink0_b07*ink0_b20);
const float  result_3_3 = 0.25*step(1.0, ink0_u3_3 + ink0_d3_3 + ink0_l3_3 + ink0_r3_3);

//  ###
// # o
// 0.50
//
const float  ink0_u3_2 = ink0_b08 * (ink0_b00*ink0_b03*ink0_b05 + ink0_b02*ink0_b04*ink0_b07);
const float  ink0_d3_2 = ink0_b11 * (ink0_b00*ink0_b03*ink0_b05 + ink0_b02*ink0_b04*ink0_b07);
const float  ink0_l3_2 = ink0_b09 * (ink0_b00*ink0_b01*ink0_b02 + ink0_b05*ink0_b06*ink0_b07);
const float  ink0_r3_2 = ink0_b10 * (ink0_b00*ink0_b01*ink0_b02 + ink0_b05*ink0_b06*ink0_b07);
const float  result_3_2 = 0.5*step(1.0, ink0_u3_2 + ink0_d3_2 + ink0_l3_2 + ink0_r3_2);

//   ###
//  #o
//  0.75
//
const float  ink0_u3_1 = ink0_b01 * (ink0_b03*ink0_b05*ink0_b21 + ink0_b04*ink0_b07*ink0_b22);
const float  ink0_d3_1 = ink0_b06 * (ink0_b13*ink0_b00*ink0_b03 + ink0_b14*ink0_b02*ink0_b04);
const float  ink0_l3_1 = ink0_b03 * (ink0_b01*ink0_b02*ink0_b16 + ink0_b06*ink0_b07*ink0_b20);
const float  ink0_r3_1 = ink0_b04 * (ink0_b15*ink0_b00*ink0_b01 + ink0_b19*ink0_b05*ink0_b06);
const float  result_3_1 = 0.75*step(1.0, ink0_u3_1 + ink0_d3_1 + ink0_l3_1 + ink0_r3_1);


// Lines stepping onto this row/column two pixels away
//
//  ##
// # o
// 0.33
//
const float  ink0_u2_2 = ink0_b08 * (ink0_b00*ink0_b03 + ink0_b02*ink0_b04);
const float  ink0_d2_2 = ink0_b11 * (ink0_b03*ink0_b05 + ink0_b04*ink0_b07);
const float  ink0_l2_2 = ink0_b09 * (ink0_b00*ink0_b01 + ink0_b05*ink0_b06);
const float  ink0_r2_2 = ink0_b10 * (ink0_b01*ink0_b02 + ink0_b06*ink0_b07);
const float  result_2_2 = 0.33333*step(1.0, ink0_u2_2 + ink0_d2_2 + ink0_l2_2 + ink0_r2_2);

//  ##
// #o
// 0.66
//
const float  ink0_u2_1 = ink0_b01 * (ink0_b03*ink0_b05 + ink0_b04*ink0_b07);
const float  ink0_d2_1 = ink0_b06 * (ink0_b00*ink0_b03 + ink0_b02*ink0_b04);
const float  ink0_l2_1 = ink0_b03 * (ink0_b01*ink0_b02 + ink0_b06*ink0_b07);
const float  ink0_r2_1 = ink0_b04 * (ink0_b00*ink0_b01 + ink0_b05*ink0_b06);
const float  result_2_1 = 0.66666*step(1.0, ink0_u2_1 + ink0_d2_1 + ink0_l2_1 + ink0_r2_1);

// Corners at this pixel
//
//  #
// #o
// 0.5
//
const float  ink0_ul1_1 = ink0_b01*ink0_b03;
const float  ink0_dl1_1 = ink0_b03*ink0_b06;
const float  ink0_ur1_1 = ink0_b01*ink0_b04;
const float  ink0_dr1_1 = ink0_b04*ink0_b06;
const float  result_1_1 = 0.5*step(1.0, ink0_ul1_1 + ink0_dl1_1 + ink0_ur1_1 + ink0_dr1_1);


// Compute ink strength for this pixel.
//
const float  postproc_ink_strength = max( max(result_1_1, max(result_2_2, result_2_1)),
                                          max(max(result_3_3, result_3_2), result_3_1) );

// original ink strength is always full (1.0) or none (0.0)
// (we threshold to get rid of the debug visualization that uses %(k_cartooncolor)s)
//
const float  original_ink_strength = step(CARTOON_THRESHOLD, tex2D(%(k_txink0)s, %(texcoord_txink0)s).a);

// The final ink alpha is the "darker" (more ink) result of first-pass ink and smoother-added ink.
// This ensures that the smoother does not remove lines that already exist in the ink texture.
//
pixcolor = lerp(pixcolor, %(k_cartooncolor)s, max(postproc_ink_strength, original_ink_strength));
"""


class CartoonInkThick(Filter):
    """A cartoon outline inking filter.

    The inking is based on examining discontinuities in the normal and depth maps, as viewed from the camera.

    Two-pass algorithm that produces thick lines. The first pass works somewhat similarly to the classic
    (Panda 1.8.1) inker, while the second pass adds antialiasing.

    This algorithm introduced in Panda 1.9.0.

    """
    def __init__(self, **kwargs):
        super(CartoonInkThick, self).__init__(**kwargs)

    def onReset(self):
        super(CartoonInkThick, self).onReset()
        # Inking must come before pretty much everything else, to simulate a completely drawn cel.
        self.stageName  = "Preprocess"
        self.sort       = 50  # This is an alternative to CartoonInkClassic, so they can have the same default sort
                              # (in order to trigger an error if both are enabled).
        self.isMergeable = False  # requires access to up-to-date aux and depth textures (outside current pixel);
                                  # also, has an internal stage.

        self.color      = (0.0, 0.0, 0.0, 1.0)

        # Data sources.
        #
        self.detectDepth   = True
        self.cutoffDepth   = 0.01

        self.detectNormals = True
        self.cutoffNormals = 0.6

        self.separation               = 1.0
        self.depthSensitiveSeparation = False
        self.mult                     = Vec4(2.0, 2.0, 2.0, 0.0)


    def onAttachPipeline(self):
        if self.detectNormals:
            self.requireSceneTexture(texName="aux")
            self.requireAuxBits(bitmask=AuxBitplaneAttrib.ABOAuxNormal)
        if self.detectDepth  or  self.depthSensitiveSeparation:
            self.requireSceneTexture(texName="depth")

        self.registerInputTexture("ink0")
        self.registerCustomInput(inputType="float4", inputName="k_cartooncolor")


    def onAttachStage(self):
        self.createInternalTextures( "ink0" )
        self.interQuads.append(self.pipeline.manager.renderQuadInto(colortex=self.get('texture')["ink0"]))
        self.interQuads[0].setShaderInput("txdepth", self.getTextureInfo("depth").get('texture'))
        self.interQuads[0].setShaderInput("txaux",   self.getTextureInfo("aux").get('texture'))


    def onCompileInternalStages(self):
        self.interQuads[0].setShader(Shader.make(CARTOONINK0_SHADER % {"depth_modsep"   : self.depthSensitiveSeparation,
                                                                       "depth_detect"   : self.detectDepth,
                                                                       "normals_detect" : self.detectNormals}))

    def onSynthesizeCompositor(self):
        txink0 = self.getTextureInfo("ink0")
        code = CARTOONINK_BODY % { "k_cartooncolor"  : self.getMangledName("k_cartooncolor"),
                                   "k_txink0"        : txink0.get('varname'),
                                   "texpix_txink0"   : txink0.get('texpix'),
                                   "texcoord_txink0" : txink0.get('texcoord') }

        return ("cartoonInkThick",
                code,
                "// cartoon ink (outlines), 'thick' algorithm antialias/blend pass\n")


    @property
    def color(self):
        """Color to use for ink, as (R,G,B,A) tuple.

        Default (0.0, 0.0, 0.0, 1.0).

        The alpha component gives the _maximum_ alpha value that corresponds
        to a fully inked pixel.

        """
        return self._color
    @color.setter
    def color(self, value):
        self._color = value
        # This parameter is needed by both render passes.
        if self.finalQuad is not None:
            self.finalQuad.setShaderInput( self.getMangledName("cartooncolor"), Vec4(value) )
        if len(self.interQuads)  and  self.interQuads[0] is not None:
            self.interQuads[0].setShaderInput( "cartooncolor", Vec4(value) )


    @property
    def detectDepth(self):
        """Whether to ink depth discontinuities.

        This enables/disables the depth buffer as a data source.

        Bool, default True.

        """
        return self._detectDepth
    @detectDepth.setter
    def detectDepth(self, value):
        if not hasattr(self, "_detectDepth")  or  bool(value) != self._detectDepth:
            self._needsCompile = True
        self._detectDepth = bool(value)


    @property
    def cutoffDepth(self):
        """Cutoff for detecting depth buffer discontinuities (default: 0.01).

        Used when detectDepth=True.

        A discontinuity is detected if

          max - min >= cutoffDepth

        where "max" and "min" are the maximum and minimum values of the depth
        in the pixels used for detection.

        Note that the depth buffer (z-buffer) stores nonlinear depth values, originally meant for
        interpolating 1/z linearly, so this threshold does NOT map linearly to a fraction of
        (far - near) of the camera.

        """
        return self._cutoffDepth
    @cutoffDepth.setter
    def cutoffDepth(self, value):
        self._cutoffDepth = value
        if len(self.interQuads)  and  self.interQuads[0] is not None:
            self.interQuads[0].setShaderInput( "cutoff_depth", value )


    @property
    def detectNormals(self):
        """Whether to ink surface normal discontinuities.

        This enables/disables the (screen-space) normals buffer as a data source.

        Bool, default True.

        """
        return self._detectNormals
    @detectNormals.setter
    def detectNormals(self, value):
        if not hasattr(self, "_detectNormals")  or  bool(value) != self._detectNormals:
            self._needsCompile = True
        self._detectNormals = bool(value)


    @property
    def cutoffNormals(self):
        """Cutoff for detecting normal map discontinuities (default: 0.6).

        Used when detectNormals=True.

        A discontinuity is detected if

          dot(max - min, mult) >= cutoffNormals

        where "max" and "min" are the componentwise maximum and minimum values of the
        surface normal vector in the pixels used for detection.

        """
        return self._cutoffNormals
    @cutoffNormals.setter
    def cutoffNormals(self, value):
        self._cutoffNormals = value
        if len(self.interQuads)  and  self.interQuads[0] is not None:
            self.interQuads[0].setShaderInput( "cutoff_normals", value )


    @property
    def separation(self):
        """Stencil size for examining discontinuities, in pixels.

        Float, default 1.0.

        Pixels in the +x, -x, +y and -y directions from the current pixel
        will be examined, with the distance for each check set to 'separation'.

        Float. Values in the range 0.6 ... 1.0 are usually good. Some scenes may tolerate
        larger values; try it on your scene to see.

        Note that using non-integer values will lead to the use of interpolated normals,
        which may or may not have the expected result.

        """
        return self._separation
    @separation.setter
    def separation(self, value):
        self._separation = value
        if len(self.interQuads)  and  self.interQuads[0] is not None:
            self.interQuads[0].setShaderInput( "cartoonseparation", Vec4(value, value, value, value) )


    @property
    def depthSensitiveSeparation(self):
        """Whether to vary the separation parameter depending on depth (distance from camera plane).

        Bool, default False.

        This makes the ink line width depth-sensitive.

        If enabled, the separation will vary between 0.5 and 2.0 times the value set as "separation",
        depending on the depth value of each pixel (pixels further away from the camera get smaller
        separation values, while those very near to the camera get larger separation values).

        """
        return self._depthSensitiveSeparation
    @depthSensitiveSeparation.setter
    def depthSensitiveSeparation(self, value):
        if not hasattr(self, "_depthSensitiveSeparation")  or  bool(value) != self._depthSensitiveSeparation:
            self._needsCompile = True
        self._depthSensitiveSeparation = bool(value)


    @property
    def mult(self):
        """Weight vector used in detecting normal map discontinuities.

        Tuple of 4 floats, default (2.0, 2.0, 2.0, 0.0).

        R, G, B map to the x, y and z components of the normal vector.

        The A component in the normal map is currently meaningless; the fourth weight should
        always be set to zero.

        """
        return self._mult
    @mult.setter
    def mult(self, value):
        self._mult = value
        if len(self.interQuads)  and  self.interQuads[0] is not None:
            self.interQuads[0].setShaderInput( "mult", Vec4(value) )

