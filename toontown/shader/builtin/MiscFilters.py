"""A collection of short, simple filters for FilterPipeline.

More complex filters each have their own module.

"""

from panda3d.core import AuxBitplaneAttrib, Vec4

from toontown.shader.Filter import Filter



###################################################
# Actual regular MiscFilters
###################################################

class Tint(Filter):
    """Color tint / fade-to-color filter.

    Introduced in Panda 1.9.0.

    In "multiply" mode [default]:

      The color of each pixel is multiplied by the specified constant color.
      The result is saturated to [0,1] in each component.

      The tinted pixel then is blended with the original one with the strength
      specified by "strength".

    In "add" mode:

      The specified constant color is added to the color of each pixel.

      Note that it is valid for one or more of the components of the constant color
      to be negative; negative components are effectively subtracted.

      The result is saturated to [0,1] in each component.

      The tinted pixel then is blended with the original one with the strength
      specified by "strength".

    In "fade" mode:

      Each pixel is blended toward the specified constant color.
      The parameter "strength" controls the strength.

    This filter can be used e.g. to fade the screen to black (color=(0,0,0,1))
    by dynamically updating the "strength" parameter in your own update task
    so that it gradually goes from 0 to 1. (Make your task sort 48 or earlier
    to ensure it runs before filter reconfigure/update and frame redraw (igLoop).)

    The fade mode also allows fading toward colors other than black
    (e.g. color=(1,1,1,1) to fade to white).

    In tint mode, fading the color to (255,255,255,1) gives another kind of
    fade to white (using the fact that there are 8 bits per color channel).

    Parameters:

      mode  = string, one of:
                "multiply" = tint (multiply) by the specified color.
                "add"      = add the specified color.
                "fade"     = fade to the specified color.

      color = (R,G,B,A) tuple; tint color. How exactly this is used depends on "mode"; see above.

              Usually setting the alpha component to 1 is a good idea in
              "multiply" and "fade" modes; in "add" mode, alpha should usually be 0.

      strenth = strength of blending between the original and processed color.
                1.0 means fully processed, 0.0 does nothing.
                Behaves linearly.

    """
    def __init__(self, **kwargs):
        super(Tint, self).__init__(**kwargs)

    def onReset(self):
        super(Tint, self).onReset()  # reset inherited properties
        self.sort  = 90  # late within the pipeline stage
        self.stageName = "Postprocess"

        self.color = (0.5, 0.5, 0.5, 1)  # default is darken by 50%
        self.strength = 1.0
        self.mode  = "multiply"  # compile-time parameter

    def onAttachPipeline(self):
        # We do not need to register the "color" texture, as our code does not access it explicitly,
        # and we do not need texture coordinates, either.
        #
        # The StageInitializer sets up the initial value of pixcolor automatically.
        # It is thus better to refer to pixcolor for the original color of the pixel being processed,
        # to save one texture lookup (and unnecessary parameters to our Cg function generated
        # in synthesize()).
        #
        self.registerCustomInput(inputType="float4", inputName="k_tint_color")
        self.registerCustomInput(inputType="float",  inputName="k_tint_strength")

    def onSynthesizeCompositor(self):
        code = ""
        if self.mode == "multiply":
            code += "// Compile-time mode: multiply\n"
            code += "float4 tinted_color = saturate(pixcolor * %(k_tint_color)s);\n" % { "k_tint_color" : self.getMangledName("k_tint_color") }
            code += "pixcolor = lerp(pixcolor, tinted_color, %(k_tint_strength)s);\n" % { "k_tint_strength" : self.getMangledName("k_tint_strength") }
        elif self.mode == "add":
            code += "// Compile-time mode: add\n"
            code += "float4 tinted_color = saturate(pixcolor + %(k_tint_color)s);\n" % { "k_tint_color" : self.getMangledName("k_tint_color") }
            code += "pixcolor = lerp(pixcolor, tinted_color, %(k_tint_strength)s);\n" % { "k_tint_strength" : self.getMangledName("k_tint_strength") }
        elif self.mode == "fade":
            code += "// Compile-time mode: fade\n"
            code += "pixcolor = lerp(pixcolor, %(k_tint_color)s, %(k_tint_strength)s);\n" % \
                        { "k_tint_color" : self.getMangledName("k_tint_color"),
                          "k_tint_strength" : self.getMangledName("k_tint_strength") }
        else:
            raise ValueError("Tint: invalid mode '%s'; valid: 'multiply', 'add', 'fade'" % self.mode)
        return ("tint", code, "// Color tint / fade-to-color filter\n")


    @property
    def color(self):
        """Tint color as (R,G,B,A) float tuple, each component in [0,1]."""
        return self._color
    @color.setter
    def color(self, value):
        self._color = value
        if self.finalQuad is not None:
            self.finalQuad.setShaderInput( self.getMangledName("tint_color"), value )

    @property
    def strength(self):
        """Effect strength, float. 1 is full strength, 0 is off."""
        return self._strength
    @strength.setter
    def strength(self, value):
        self._strength = value
        if self.finalQuad is not None:
            self.finalQuad.setShaderInput( self.getMangledName("tint_strength"), value )

    @property
    def mode(self):
        """Effect mode, one of 'multiply' (default), 'add' or 'fade'."""
        return self._mode
    @mode.setter
    def mode(self, value):
        if (not hasattr(self, "_mode")  or  value != self._mode)  and  self.pipeline is not None:
            self.pipeline._needsCompile = True
        self._mode = value


class ViewGlow(Filter):
    """View the glow map by overwriting the red color channel with the glow data. This may help in debugging your scene."""

    def __init__(self, **kwargs):
        super(ViewGlow, self).__init__(**kwargs)

    def onReset(self):
        super(ViewGlow, self).onReset()
        self.stageName = "DebugHelpers"  # this is a debug helper filter which should go last
        self.sort = 99  # last thing in the stage

    def onAttachPipeline(self):
        self.requireAuxBits(bitmask=AuxBitplaneAttrib.ABOGlow)

    def onSynthesizeCompositor(self):
        return ("viewGlow",
                "pixcolor.r = pixcolor.a;\n",
                "// show the glow map by overwriting the red channel (debugging helper filter)\n")


class GammaAdjust(Filter):
    """Apply additional gamma correction to the image.

    Introduced in Panda 1.9.0.

    """

    def __init__(self, **kwargs):
        super(GammaAdjust, self).__init__(**kwargs)

    def onReset(self):
        super(GammaAdjust, self).onReset()
        self.stageName = "DisplayDevice"
        self.sort = 90

        self.gamma = 2.2

    def onAttachPipeline(self):
        # This filter needs no textures, custom inputs, aux bits, or internal stages,
        # but this method is abstract in the Filter base class, because almost all filters do.
        #
        # Thus, we just provide a blank implementation to fulfill the interface and acknowledge
        # the very exceptional case that this filter doesn't need to do anything here.
        #
        pass

    def onSynthesizeCompositor(self):
        if self.gamma == 0.5:
            code  = "// gamma = 0.5\n"
            code += "pixcolor.rgb = sqrt(pixcolor.rgb);\n"
        elif self.gamma == 2.0:
            code  = "// gamma = 2.0\n"
            code += "pixcolor.rgb *= pixcolor.rgb;\n"
        elif self.gamma != 1.0:
            code  = "// gamma = %g\n" % self.gamma
            code += "pixcolor.rgb = pow(pixcolor.rgb, %ff);\n" % self.gamma
        else: # self.gamma == 1.0:  # no-op
            code  = "// gamma = 1.0, no-op\n"

        return ("gammaAdjust",
                code,
                "// gamma correction\n")

    @property
    def gamma(self):
        """Amount of gamma correction. 1.0 = no correction."""
        return self._gamma
    @gamma.setter
    def gamma(self, value):
        if (not hasattr(self, "_gamma")  or  value != self._gamma)  and  self.pipeline is not None:
            self.pipeline._needsCompile = True
        self._gamma = value


class ColorInversion(Filter):
    """Invert the colors, like a film negative."""

    def __init__(self, **kwargs):
        super(ColorInversion, self).__init__(**kwargs)

    def onReset(self):
        super(ColorInversion, self).onReset()
        self.stageName = "FilmOrDetector"
        self.sort = 90

    def onAttachPipeline(self):
        pass

    def onSynthesizeCompositor(self):
        return ("colorInversion",
                "pixcolor = float4(1.0, 1.0, 1.0, 1.0) - pixcolor;\n",
                "// invert colors\n")


# Inking algorithm from Panda 1.8.1, with a bugfix: the screen-space normal in the aux texture
# has three components, not two. Changed the weighting float4(3,3,0,0) to float4(2,2,2,0).
#
CARTOONINK_BODY="""float4 cartoondelta = %(k_cartoonseparation)s * %(texpix_txaux)s.xwyw;
float4 cartoon_c0 = tex2D(%(k_txaux)s, %(texcoord_txaux)s + cartoondelta.xy);
float4 cartoon_c1 = tex2D(%(k_txaux)s, %(texcoord_txaux)s - cartoondelta.xy);
float4 cartoon_c2 = tex2D(%(k_txaux)s, %(texcoord_txaux)s + cartoondelta.wz);
float4 cartoon_c3 = tex2D(%(k_txaux)s, %(texcoord_txaux)s - cartoondelta.wz);
float4 cartoon_mx = max(cartoon_c0, max(cartoon_c1, max(cartoon_c2, cartoon_c3)));
float4 cartoon_mn = min(cartoon_c0, min(cartoon_c1, min(cartoon_c2, cartoon_c3)));
float cartoon_thresh = saturate(dot(cartoon_mx - cartoon_mn, float4(2,2,2,0)) - 0.5);
pixcolor = lerp(pixcolor, %(k_cartooncolor)s, cartoon_thresh);
"""

class CartoonInkClassic(Filter):
    """A cartoon outline inking filter.

    The inking is based on examining discontinuities in the normal map, as viewed from the camera.

    Classic algorithm, as in Panda 1.8.1.

    """
    def __init__(self, **kwargs):
        super(CartoonInkClassic, self).__init__(**kwargs)

    def onReset(self):
        super(CartoonInkClassic, self).onReset()
        # Inking must come before pretty much everything else, to simulate a completely drawn cel.
        self.stageName  = "Preprocess"
        self.sort       = 50
        self.separation = 1.0
        self.color      = (0.0, 0.0, 0.0, 1.0)

    def onAttachPipeline(self):
        self.registerInputTexture(texName="aux")
        self.requireAuxBits(bitmask=AuxBitplaneAttrib.ABOAuxNormal)

        self.registerCustomInput(inputType="float",  inputName="k_cartoonseparation")
        self.registerCustomInput(inputType="float4", inputName="k_cartooncolor")

    def onSynthesizeCompositor(self):
        txaux = self.getTextureInfo("aux")
        code = CARTOONINK_BODY % { "k_cartoonseparation" : self.getMangledName("k_cartoonseparation"),
                                   "k_cartooncolor"      : self.getMangledName("k_cartooncolor"),
                                   "k_txaux"             : txaux.get('varname'),
                                   "texcoord_txaux"      : txaux.get('texcoord'),
                                   "texpix_txaux"        : txaux.get('texpix') }

        return ("cartoonInkClassic",
                code,
                "// cartoon ink (outlines), classic algorithm\n")


    @property
    def separation(self):
        """Stencil size for examining discontinuities, in pixels.

        Float, default 1.0.

        Pixels in the +x, -x, +y and -y directions from the current pixel
        will be examined, with the distance for each check set to 'separation'.

        Float. Values in the range 0.6 ... 1.0 are usually good. Some scenes may tolerate
        larger values; try it on your scene to see.

        """
        return self._separation
    @separation.setter
    def separation(self, value):
        self._separation = value
        if self.finalQuad is not None:
            self.finalQuad.setShaderInput( self.getMangledName("cartoonseparation"), value )


    @property
    def color(self):
        """Color to use for ink, as (R,G,B,A) tuple. [introduced in 1.8.0]

        Default (0.0, 0.0, 0.0, 1.0).

        The alpha component gives the _maximum_ alpha value that corresponds
        to a fully inked pixel.

        """
        return self._color
    @color.setter
    def color(self, value):
        self._color = value
        if self.finalQuad is not None:
            self.finalQuad.setShaderInput( self.getMangledName("cartooncolor"), Vec4(value) )


# Algorithm by Timothy Lottes of NVIDIA; implementation based on
# http://horde3d.org/wiki/index.php5?title=Shading_Technique_-_FXAA
#
FXAA_BODY="""float FXAA_SPAN_MAX = 8.0;
float FXAA_REDUCE_MUL = 1.0/8.0;
float FXAA_REDUCE_MIN = 1.0/128.0;

float3 rgbNW = tex2D(%(k_txcolor)s, %(texcoord_txcolor)s + float2(-1.0, -1.0) * %(texpix_txcolor)s).rgb;
float3 rgbNE = tex2D(%(k_txcolor)s, %(texcoord_txcolor)s + float2( 1.0, -1.0) * %(texpix_txcolor)s).rgb;
float3 rgbSW = tex2D(%(k_txcolor)s, %(texcoord_txcolor)s + float2(-1.0,  1.0) * %(texpix_txcolor)s).rgb;
float3 rgbSE = tex2D(%(k_txcolor)s, %(texcoord_txcolor)s + float2( 1.0,  1.0) * %(texpix_txcolor)s).rgb;
float3 rgbM  = pixcolor;  // reuse existing center tap

vec3 luma = vec3(0.299, 0.587, 0.114);
float lumaNW = dot(rgbNW, luma);
float lumaNE = dot(rgbNE, luma);
float lumaSW = dot(rgbSW, luma);
float lumaSE = dot(rgbSE, luma);
float lumaM  = dot(rgbM,  luma);

float lumaMin = min(lumaM, min(min(lumaNW, lumaNE), min(lumaSW, lumaSE)));
float lumaMax = max(lumaM, max(max(lumaNW, lumaNE), max(lumaSW, lumaSE)));

float2 dir;
dir.x = -( (lumaNW + lumaNE) - (lumaSW + lumaSE) );
dir.y =  ( (lumaNW + lumaSW) - (lumaNE + lumaSE) );

float dirReduce = max(
        (lumaNW + lumaNE + lumaSW + lumaSE) * (0.25 * FXAA_REDUCE_MUL),
        FXAA_REDUCE_MIN);

float rcpDirMin = 1.0 / ( min(abs(dir.x), abs(dir.y)) + dirReduce );

dir = min(     float2( FXAA_SPAN_MAX,  FXAA_SPAN_MAX),
           max(float2(-FXAA_SPAN_MAX, -FXAA_SPAN_MAX), dir * rcpDirMin)
         ) * %(texpix_txcolor)s;

vec3 rgbA = (1.0/2.0) * (
        tex2D( %(k_txcolor)s, %(texcoord_txcolor)s + dir * (1.0/3.0 - 0.5) ).rgb +
        tex2D( %(k_txcolor)s, %(texcoord_txcolor)s + dir * (2.0/3.0 - 0.5) ).rgb
      );
vec3 rgbB = rgbA * (1.0/2.0) + (1.0/4.0) * (
        tex2D( %(k_txcolor)s, %(texcoord_txcolor)s + dir * (0.0/3.0 - 0.5) ).rgb +
        tex2D( %(k_txcolor)s, %(texcoord_txcolor)s + dir * (3.0/3.0 - 0.5) ).rgb
      );
float lumaB = dot(rgbB, luma);

if( (lumaB < lumaMin) || (lumaB > lumaMax) )
    pixcolor.rgb = rgbA;
else
    pixcolor.rgb = rgbB;
"""

class AntialiasFXAA(Filter):
    """Fast approximate antialiasing (FXAA).

    This is a fast postprocess full-screen antialiasing filter based on Timothy Lottes's FXAA algorithm.

    This smooths jaggy edges, but also blurs sharp edges and high-frequency components in textures;
    this should be applied before drawing any UI elements.

    Introduced in Panda 1.9.0.

    """
    def __init__(self, **kwargs):
        super(AntialiasFXAA, self).__init__(**kwargs)

    def onReset(self):
        super(AntialiasFXAA, self).onReset()
        self.stageName   = "Preprocess"
        # FXAA must come first in whichever stage it is in, because it overwrites pixcolor
        # (and will thus erase any earlier processing performed in the same stage).
        self.sort        = 0
        self.isMergeable = False

    def onAttachPipeline(self):
        self.registerInputTexture(texName="color")

    def onSynthesizeCompositor(self):
        txcolor = self.getTextureInfo("color")
        code = FXAA_BODY % { "k_txcolor"        : txcolor.get('varname'),
                             "texcoord_txcolor" : txcolor.get('texcoord'),
                             "texpix_txcolor"   : txcolor.get('texpix') }

        return ("antialiasFXAA",
                code,
                "// fast approximate antialiasing\n")


VIGNETTING_BODY="""// TODO/FIXME: is texpad always < 0.5? In that case we don't need the min(), and can use texpad directly.
const float2 texradii = min( %(texpad_txcolor)s.xy, 1.0 - %(texpad_txcolor)s.xy );
const float2 sample_vector = (%(texpad_txcolor)s.xy - %(texcoord_txcolor)s.xy)/texradii.xy; // in -1 ... 1
const float  sample_normsq = dot(sample_vector, sample_vector);  // in 0...2, quadratic
pixcolor *= (1.0 - %(k_vignetting_strength)s*(0.5*sample_normsq));
"""

class Vignetting(Filter):
    """Filter that simulates vignetting (darkening of image periphery compared to the center).

    Introduced in Panda 1.9.0.

    """

    def __init__(self, **kwargs):
        super(Vignetting, self).__init__(**kwargs)

    def onReset(self):
        super(Vignetting, self).onReset()  # reset inherited properties

        self.sort = 70
        self.stageName   = "FilmOrDetector"
        self.isMergeable = True

        self.strength = 0.6

    def onAttachPipeline(self):
        self.registerInputTexture(texName="color")
        self.registerCustomInput(inputType="float",  inputName="k_vignetting_strength")

    def onSynthesizeCompositor(self):
        txcolor = self.getTextureInfo("color")
        code = VIGNETTING_BODY % { "k_vignetting_strength" : self.getMangledName("k_vignetting_strength"),
                                   "texcoord_txcolor"      : txcolor.get('texcoord'),
                                   "texpad_txcolor"        : txcolor.get('texpad') }
        return ("vignetting", code, "// vignetting filter\n")


    @property
    def strength(self):
        """Strength of the effect.

        Float, Default 0.6.

        For most cases, useful values are in the interval [0, 1].

        A value of 1.0 means the pixels at exactly the corners of the view will become completely black,
        while a value of 0.0 means no vignetting.

        Values over 1.0 make a larger part of the edge of the view black; e.g. 2.0 will make the pixels
        exactly at the halfway points of view edges completely black.

        """
        return self._strength
    @strength.setter
    def strength(self, value):
        self._strength = value
        if self.finalQuad is not None:
            self.finalQuad.setShaderInput( self.getMangledName("vignetting_strength"), value )


PIXELIZATION_BODY="""const float dx = %(k_params)s.x * %(texpix_txcolor)s.x;
const float dy = %(k_params)s.y * %(texpix_txcolor)s.y;

float2 coord = float2( dx*floor(%(texcoord_txcolor)s.x/dx), dy*floor(%(texcoord_txcolor)s.y/dy) );

pixcolor = tex2D( %(k_txcolor)s, coord );
"""

class Pixelization(Filter):
    """Filter that pixelates (subsamples) the image, producing a mosaic.

    Introduced in Panda 1.9.0.

    """
    def __init__(self, **kwargs):
        super(Pixelization, self).__init__(**kwargs)

    def onReset(self):
        super(Pixelization, self).onReset()  # reset inherited properties

        # This filter needs to read its input texture at an arbitrary location,
        # and it overwrites pixcolor, so it is not mergeable, and must come first
        # in the stage it is placed in.
        #
        self.sort = 0
        self.stageName   = "DisplayDevice"
        self.isMergeable = False

        self.sizex = 4
        self.sizey = 4

    def onAttachPipeline(self):
        self.registerInputTexture(texName="color")
        self.registerCustomInput(inputType="float4", inputName="k_params")

    def onSynthesizeCompositor(self):
        txcolor = self.getTextureInfo("color")
        code = PIXELIZATION_BODY % { "k_params"         : self.getMangledName("k_params"),
                                     "k_txcolor"        : txcolor.get('varname'),
                                     "texcoord_txcolor" : txcolor.get('texcoord'),
                                     "texpix_txcolor"   : txcolor.get('texpix') }
        return ("pixelization", code, "// pixelization (mosaic) filter\n")

    # Combine sizex and sizey into one shader input.
    def _computeParams(self):
        return Vec4(self._sizex, self._sizey, 0.0, 0.0)

    @property
    def sizex(self):
        """Size of pixelization in the x direction.

        Integer, >= 1. Default 4.

        """
        return self._sizex
    @sizex.setter
    def sizex(self, value):
        self._sizex = int(value)
        if self.finalQuad is not None:
            self.finalQuad.setShaderInput( self.getMangledName("params"), self._computeParams() )

    @property
    def sizey(self):
        """Size of pixelization in the y direction.

        Integer, >= 1. Default 4.

        """
        return self._sizey
    @sizey.setter
    def sizey(self, value):
        self._sizey = int(value)
        if self.finalQuad is not None:
            self.finalQuad.setShaderInput( self.getMangledName("params"), self._computeParams() )


POSTERIZATION_BODY="""float nColors = %(k_params)s.x;
float gamma = %(k_params)s.y;
float invgamma = %(k_params)s.z;

float3 c = pixcolor.rgb;
c = pow(c, gamma);
c *= nColors;
c = floor(c);
c /= nColors;
pixcolor.rgb = pow(c, invgamma);
"""

class Posterization(Filter):
    """Filter that posterizes the image (reduces colors).

    Introduced in Panda 1.9.0.

    """
    def __init__(self, **kwargs):
        super(Posterization, self).__init__(**kwargs)

    def onReset(self):
        super(Posterization, self).onReset()  # reset inherited properties

        self.sort = 70
        self.stageName   = "DisplayDevice"
        self.isMergeable = True

        self.quantization = 8
        self.gamma        = 2.2

    def onAttachPipeline(self):
        self.registerCustomInput(inputType="float4",  inputName="k_params")

    def onSynthesizeCompositor(self):
        code = POSTERIZATION_BODY % { "k_params" : self.getMangledName("k_params") }
        return ("posterization", code, "// posterization (color reduction) filter\n")

    # Combine quantization and gamma into one shader input.
    def _computeParams(self):
        # We save a division in the fshader by precomputing the inverse of gamma.
        return Vec4(self._quantization, self._gamma, 1.0/self.gamma, 0.0)

    @property
    def quantization(self):
        """Number of intensity levels preserved in posterization.

        The same value is used in all color components (R,G,B) independently.

        Integer, >= 1. Default 8.

        """
        return self._quantization
    @quantization.setter
    def quantization(self, value):
        self._quantization = int(value)
        if self.finalQuad is not None:
            self.finalQuad.setShaderInput( self.getMangledName("params"), self._computeParams() )

    @property
    def gamma(self):
        """Amount of gamma correction.

        In order to posterize the colors in a perceptually linear way, this filter
        needs to know the gamma correction value.

        The gamma-corrected space is only used during the processing; both the
        input and output are "gamma-uncorrected".

        If you need to apply gamma correction to the final image, see the GammaAdjust filter.

        Float, default 2.2. Use the value 1.0 for no-op.

        """
        return self._gamma
    @gamma.setter
    def gamma(self, value):
        self._gamma = int(value)
        if self.finalQuad is not None:
            self.finalQuad.setShaderInput( self.getMangledName("params"), self._computeParams() )

LOOKUP_BODY="""float LUT_Size = 32.0;

float red = ( pixcolor.r * (LUT_Size - 1.0) + 0.4999 ) / (LUT_Size * LUT_Size);
float green = ( pixcolor.g * (LUT_Size - 1.0) + 0.4999 ) / LUT_Size;
float blue1 = (floor( pixcolor.b  * (LUT_Size - 1.0) ) / LUT_Size) + red;
float blue2 = (ceil( pixcolor.b  * (LUT_Size - 1.0) ) / LUT_Size) + red;
float2 texcXY = float2(pixcolor.r * 1.0 / LUT_Size, 1.0 - pixcolor.g);
//float mixer = clamp(max((pixcolor.b - blue1) / (blue2 - blue1), 0.0), 0.0, 64.0);
float mixer = frac(pixcolor.b * LUT_Size);
int frameZ = int(pixcolor.b * LUT_Size);

float4 color1 = tex2D(%(lutTex)s, texcXY + float2((frameZ) / LUT_Size));
float4 color2 = tex2D(%(lutTex)s, texcXY + float2((frameZ + 1) / LUT_Size));

pixcolor.rgb = mix(color1, color2, mixer);
"""

LOOKUP_BODY2="""
float LUT_Size = 32.0;
pixcolor = clamp(pixcolor, 0.5 / LUT_Size, 1.0 - 0.5 / LUT_Size);
float2 texcXY = float2(pixcolor.r * (1.0 / LUT_Size), 1.0 - pixcolor.g);
int frameZ = int(pixcolor.b * LUT_Size);
float offsZ = frac(pixcolor.b * LUT_Size);


float4 sample1 = tex2D(%(lutTex)s, texcXY + float2((frameZ) / LUT_Size));
float4 sample2 = tex2D(%(lutTex)s, texcXY + float2((frameZ + 1) / LUT_Size));
pixcolor.rgb = lerp(sample1, sample2, offsZ);

"""
LOOKUP_BODY3="""
float LUT_Size = 32.0;

int frameZ = (LUT_Size - 1.0) / LUT_Size;
float offsZ = 1.0 / (2.0 * LUT_Size);
pixcolor.rgb = tex2D(%(lutTex)s);

"""

LOOKUP_BODY4 = """
float LUT_Size = 32.0;

float red = pixcolor.r;
float green = pixcolor.g;
float blue = pixcolor.b;
float blue1 = (floor( pixcolor.b  * (LUT_Size - 1.0) ) / LUT_Size) + red;
float blue2 = (ceil( pixcolor.b  * (LUT_Size - 1.0) ) / LUT_Size) + red;
float2 texcXY = float2(pixcolor.r * 1.0 / LUT_Size, 1.0 - pixcolor.g);
//float mixer = clamp(max((pixcolor.b - blue1) / (blue2 - blue1), 0.0), 0.0, 64.0);
float mixer = frac(pixcolor.b * LUT_Size);
int frameZ = int(pixcolor.b * LUT_Size);

float4 color1 = tex2D(%(lutTex)s, texcXY + float2((frameZ) / LUT_Size));
float4 color2 = tex2D(%(lutTex)s, texcXY + float2((frameZ + 1) / LUT_Size));

pixcolor.rgb = lerp(red, green, blue);

"""


"""
float4 color1 = tex2D( %(lutTex)s, float2( blue1, green ));
float4 color2 = tex2D( %(lutTex)s, float2( blue2, green ));
pixcolor.rgb = mix(color1, color2, mixer);


"""
"""
 void main(in float2 sUV : TEXCOORD0,
           out half4 cOut : COLOR,
           const uniform float4 pixcolor,
           const uniform sampler2D lut,
           const uniform float3 lutSize)  {
           // Get the image color
           half2 rawColor = texRECT(imagePlane, sUV).rgb;
           // Compute the 3D LUT lookup scale/offset factor
           half2 scale = (lutSize - 1.0) / lutSize;
           half2 offset = 1.0 / (2.0 * lutSize);
           / ****** Apply 3D LUT color transform! **************
           // This is our dependent texture read; The 3D texture's
           // lookup coordinates are dependent on the
           // previous texture read's result
           cOut.rgb = tex2D(lut);  } 
"""



class LookupTest(Filter):
    """Filter that posterizes the image (reduces colors).

    Introduced in Panda 1.9.0.

    """
    def __init__(self, **kwargs):
        super(LookupTest, self).__init__(**kwargs)

    def onReset(self):
        super(LookupTest, self).onReset()  # reset inherited properties

        self.sort = 70
        self.stageName   = "DisplayDevice"
        self.isMergeable = True
        self._lutImg = "phase_3/luts/32.png"

    def onAttachPipeline(self):
        self.registerCustomInput(inputType="sampler2D",  inputName="lutTex")

    def onSynthesizeCompositor(self):
        code = LOOKUP_BODY2 % { "lutTex" : self.getMangledName("lutTex") }
        return ("lookup", code, "// lut test\n")

    @property
    def lutImg(self):
        return self._lutImg
    @lutImg.setter
    def lutImg(self, texPath):
        if self.finalQuad is not None:
            self._lutImg = texPath
            self.finalQuad.setShaderInput( self.getMangledName("lutTex"), loader.loadTexture(texPath) )

