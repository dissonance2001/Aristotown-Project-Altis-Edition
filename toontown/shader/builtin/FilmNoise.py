from panda3d.core import Vec2

from toontown.shader.Filter import Filter

### These helper functions are given for future GLSL compatibility.
###
### Helper functions by Spatial, 05 July 2013, from
### http://stackoverflow.com/questions/4200224/random-noise-functions-for-glsl
###
##FILMNOISE_HELPERFUNC_HASH="""// A single iteration of Bob Jenkins' One-At-A-Time hashing algorithm.
##uint %(hashFuncName)s( uint x ) {
##    x += ( x << 10u );
##    x ^= ( x >>  6u );
##    x += ( x <<  3u );
##    x ^= ( x >> 11u );
##    x += ( x << 15u );
##    return x;
##}
##"""
##
##FILMNOISE_HELPERFUNC_FLOATCONSTRUCT="""// Construct a float with half-open range [0:1] using low 23 bits.
##// All zeroes yields 0.0, all ones yields the next smallest representable value below 1.0.
##float %(floatConstructFuncName)s( uint m ) {
##    const uint ieeeMantissa = 0x007FFFFFu; // binary32 mantissa bitmask
##    const uint ieeeOne      = 0x3F800000u; // 1.0 in IEEE binary32
##
##    m &= ieeeMantissa;                     // Keep only mantissa bits (fractional part)
##    m |= ieeeOne;                          // Add fractional part to 1.0
##
##    float  f = uintBitsToFloat( m );       // Range [1:2]
##    return f - 1.0;                        // Range [0:1]
##}
##"""
##
##FILMNOISE_HELPERFUNC_RANDOM3="""// Pseudo-random value in half-open range [0:1].
##float %(random3FuncName)s( vec3 v ) { return %(floatConstructFuncName)s(%(hashFuncName)s(floatBitsToUint(v))); }
##"""


## hash based 3d value noise
## function taken from https://www.shadertoy.com/view/XslGRr
## Created by inigo quilez - iq/2013
## License Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License.
##
## Ported to Cg for Panda, based on the HLSL version posted at StackOverflow.
##
## Incompatible license, so at best this works as a proof of concept.
##
##FILMNOISE_HELPERFUNC_HASH="""float %(hashFuncName)s( float n )
##{
##    return frac(sin(n)*43758.5453);
##}
##"""
##
##FILMNOISE_HELPERFUNC_RANDOM3="""float %(random3FuncName)s( float3 x )
##{
##    // This returns a value in the range -1.0f -> 1.0f
##
##    float3 p = floor(x);
##    float3 f = frac(x);
##
##    f       = f*f*(3.0-2.0*f);
##    float n = p.x + p.y*57.0 + 113.0*p.z;
##
##    return lerp(lerp(lerp( %(hashFuncName)s(n+0.0), %(hashFuncName)s(n+1.0),f.x),
##                   lerp( %(hashFuncName)s(n+57.0), %(hashFuncName)s(n+58.0),f.x),f.y),
##               lerp(lerp( %(hashFuncName)s(n+113.0), %(hashFuncName)s(n+114.0),f.x),
##                   lerp( %(hashFuncName)s(n+170.0), %(hashFuncName)s(n+171.0),f.x),f.y),f.z);
##}
##"""


# Yet another one, based on the (supposedly public domain) 2D one-liner given e.g. on StackOverflow:
#
# http://stackoverflow.com/questions/4200224/random-noise-functions-for-glsl
#
FILMNOISE_HELPERFUNC_HASH="""float %(hashFuncName)s(float n)
{
    return frac(sin(n) * 43758.5453);
}
"""

FILMNOISE_HELPERFUNC_RANDOM3="""float %(random3FuncName)s(float3 x)
{
    return %(hashFuncName)s( dot(x, vec3(12.9898, 78.233, 172.12387)) );
}
"""

FILMNOISE_BODY="""#define MODE %(mode)d

const float time     = %(k_filmnoise_params)s.x;
const float strength = %(k_filmnoise_params)s.y;

// scaling by texsize gives a more random looking result
//
const float2 texsize = 1.0 / %(texpix_txcolor)s.xy;
const float2 xyscale = 91.83*texsize;  // suitable arbitrary multiplier (17.28 is good for the one by inigo quilez)

#if MODE == 1

// monochrome mode
//
float random = %(random3FuncName)s( float3( xyscale*%(texcoord_txcolor)s.xy, time ) );
pixcolor.rgb += strength*(random - 0.5);

#else

// color mode
//
float random1 = %(random3FuncName)s( float3( xyscale*%(texcoord_txcolor)s.xy, time-1.0 ) );
float random2 = %(random3FuncName)s( float3( xyscale*%(texcoord_txcolor)s.xy, time ) );
float random3 = %(random3FuncName)s( float3( xyscale*%(texcoord_txcolor)s.xy, time+1.0 ) );
pixcolor.r += strength*(random1 - 0.5);
pixcolor.g += strength*(random2 - 0.5);
pixcolor.b += strength*(random3 - 0.5);

#endif
"""


class FilmNoise(Filter):
    """A simple film noise filter.

    Introduced in Panda 1.9.0.

    Monochrome (film-like) and color (bad analog TV signal or CCD detector noise in digital video camera)
    modes available.

    """

    def __init__(self, **kwargs):
        super(FilmNoise, self).__init__(**kwargs)

    def onReset(self):
        super(FilmNoise, self).onReset()
        self.stageName   = "FilmOrDetector"
        self.sort        = 80
        self.isMergeable = True

        self._time        = 0.0  # update() will overwrite this, but we need some value during connectOutput(),
                                 # which might try to set strength first (which calls _computeParamsInput(),
                                 # which requires _time).

        self.mode        = "monochrome"
        self.strength    = 0.05
        self.dynamic     = True

    def onAttachPipeline(self):
        self.registerInputTexture(texName="color")
        self.registerCustomInput(inputType="float2", inputName="k_filmnoise_params")
        self.registerUpdatable()

    def onSynthesizeCompositor(self):
        modeInt = 1 if self._mode == "monochrome" else 2

        # Helper function names must be mangled manually to make them unique to this filter instance.
        #
        hashFuncName           = self.getMangledName("hash")
        random3FuncName        = self.getMangledName("random3")

        txcolor = self.getTextureInfo("color")
        code = FILMNOISE_BODY % { "mode"               : modeInt,
                                  "texcoord_txcolor"   : txcolor.get('texcoord'),
                                  "texpix_txcolor"     : txcolor.get('texpix'),
                                  "k_filmnoise_params" : self.getMangledName("k_filmnoise_params"),
                                  "random3FuncName"    : random3FuncName }

        # Because random3 calls hash, it needs to know the mangled names of both itself (for its own definition)
        # and the function it needs to call (to be able to perform the function call).
        #
        hashCode           = FILMNOISE_HELPERFUNC_HASH % { "hashFuncName" : hashFuncName }
        random3Code        = FILMNOISE_HELPERFUNC_RANDOM3 % { "random3FuncName" : random3FuncName,
                                                              "hashFuncName"    : hashFuncName }

        # Here we use the extended return format: tuple
        #
        #   (funcname, code, comment, ...)
        #
        # where "..." are one or more optional custom functions for this filter.
        # The custom function names must be mangled *by the filter*.
        #
        return ("filmNoise",
                code,
                "// film noise filter\n",
                hashCode,
                random3Code)


    def onUpdate(self):
        if self.dynamic:
            # We use a time parameter to get different random numbers each frame.
            self._time += 1.0
            if self._time > 1000000.0:
                self._time = 0
            if self.finalQuad is not None:
                self.finalQuad.setShaderInput( self.getMangledName("filmnoise_params"), self._computeParamsInput() )


    # This private method packs the "time" and "strength" parameters into one shader input.
    def _computeParamsInput(self):
        return Vec2(self._time, self._strength)


    @property
    def mode(self):
        """Operation mode.

        String, one of:

            "monochrome" (default) = monochrome noise, like film.

            "rgb"                  = independent noise in each color component,
                                     like a bad analog TV signal or noise in the
                                     CCD detector of a digital video camera.

        """
        return self._mode
    @mode.setter
    def mode(self, value):
        if value not in ["monochrome", "rgb"]:
            raise ValueError("In %s %s: unknown mode '%s', valid: 'monochrome', 'rgb'" % (self.__class__.__name__, self.name, value))
        if (not hasattr(self, "_mode")  or  value != self._mode)  and  self.pipeline is not None:
            self.pipeline._needsCompile = True
        self._mode = value


    @property
    def strength(self):
        """Strength of the noise (float, default 0.05)."""
        return self._strength
    @strength.setter
    def strength(self, value):
        self._strength = value
        if self.finalQuad is not None:
            self.finalQuad.setShaderInput( self.getMangledName("filmnoise_params"), self._computeParamsInput() )


    @property
    def dynamic(self):
        """Whether the effect is dynamic (noise changes at each frame) or static (same noise each frame).

        Bool, default True.

        Freezing the noise (setting dynamic=False) can be useful for generating a freeze-frame
        (e.g. in game pause situations).

        """
        return self._dynamic
    @dynamic.setter
    def dynamic(self, value):
        # This is queried by update() so we only need to store the value here. 
        self._dynamic = value

