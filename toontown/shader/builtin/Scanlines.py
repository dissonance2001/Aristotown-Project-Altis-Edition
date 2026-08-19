import math
import time

from panda3d.core import Vec4

from toontown.shader.Filter import Filter

# Compositor Cg code snippet.
#
SCANLINES_BODY="""// Bright/dark band artifact that results from temporal aliasing (due to nearly same framerates)
// when a CRT screen is filmed with a video camera (like sometimes seen in the background in old news broadcasts).
//
const float bandStrength = %(k_scanlines_bandparams)s.x;
const float bandSpeed    = %(k_scanlines_bandparams)s.y;
const float bandSize     = %(k_scanlines_bandparams)s.z;
const float time         = %(k_scanlines_bandparams)s.w;

// sin() has a period of 2*pi, and we want bandSpeed to be expressed in complete cycles per second
// and bandSize as the fraction of view height that one complete band takes up.
//
// Hence we multiply both by 2.0.
//
float arg  = ((1.0 - %(texcoord_txcolor)s.y) / (2.0*bandSize)) - (2.0*bandSpeed)*time;
float trig = max(sin(arg*3.1415926535), 0.0);  // use only the positive half-wave to have a "pause" of half a period
float bandValue = bandStrength * trig*trig;  // sin**2 looks better for this than just sin
pixcolor += bandValue;  // additive blend for this looks natural


// Darkening of alternating lines + tinting by CRT pixel matrix.
//
const float lineThickness = %(k_scanlines_darkparams)s.x;
const float field         = %(k_scanlines_darkparams)s.y;
const float strength      = %(k_scanlines_darkparams)s.z;

// Pixel x,y indices (note: we flip y to have zero at the upper edge)
int x = int( %(texcoord_txcolor)s.x / %(texpix_txcolor)s.x );
int y = int( (1.0 - %(texcoord_txcolor)s.y) / %(texpix_txcolor)s.y );

// Pixel brightness modifier
float3 mult = float3(1.0);

#define TINT_ENABLED %(enable_tint)d
#if TINT_ENABLED == 1

// Tint by CRT pixel matrix.
//
// We must use a switch to choose the mask vector since the arbfp1 profile does not allow
// indexing an array with an arbitrary int.
//
const float3 crt[] = float3[]( float3(1.0,0.5,0.5), float3(0.5,1.0,0.5), float3(0.5,0.5,1.0) );
int xmod3 = x %% 3;
switch(xmod3)
{
    case 0:
        mult *= crt[0];
        break;
    case 1:
        mult *= crt[1];
        break;
    case 2:
        mult *= crt[2];
        break;
    default:
        break;
}

#endif

// Darken.
//
if ( int( y/lineThickness ) %% 2 != field )
    mult *= (1.0 - strength);

pixcolor.rgb *= mult;

"""


class Scanlines(Filter):
    """Filter that simulates CRT TV scanlines by darkening alternating rows of the picture.

    Optionally, this also simulates a traveling bright/dark band that results from temporal aliasing
    (due to nearly same framerates) when a CRT screen is filmed with a video camera
    (like sometimes seen in the background in old news broadcasts).

    Introduced in Panda 1.9.0.

    """

    FIELD_TOP    = 0
    FIELD_BOTTOM = 1

    def __init__(self, **kwargs):
        super(Scanlines, self).__init__(**kwargs)

    def onReset(self):
        super(Scanlines, self).onReset()
        self.sort  = 80
        self.stageName = "DisplayDevice"

        self._time = 0.0  # update() will overwrite this, but we need some value during connectOutput(),
                          # which nudges the parameter setters; this requires also _time due to parameter packing.
        self._prevtime = time.time()

        self.field         = Scanlines.FIELD_TOP
        self.strength      = 0.5
        self.lineThickness = 1
        self.dynamicFlip   = False

        self.bandStrength  = 0.1
        self.bandSpeed     = 0.75
        self.bandSize      = 1.0

        self.enableTint    = False

    def onAttachPipeline(self):
        self.registerInputTexture(texName="color")
        self.registerCustomInput(inputType="float4", inputName="k_scanlines_bandparams")
        self.registerCustomInput(inputType="float4", inputName="k_scanlines_darkparams")

        # This filter, when in dynamicFlip mode, requires updating the "field" input at each frame.
        #
        # We always add the task so that "dynamicFlip" will behave as expected if switched on/off
        # on the fly.
        #
        self.registerUpdatable()

    def onSynthesizeCompositor(self):
        txcolor = self.getTextureInfo("color")
        code = SCANLINES_BODY % { "texcoord_txcolor" : txcolor.get('texcoord'),
                                  "texpix_txcolor"   : txcolor.get('texpix'),
                                  "k_scanlines_bandparams" : self.getMangledName("k_scanlines_bandparams"),
                                  "k_scanlines_darkparams" : self.getMangledName("k_scanlines_darkparams"),
                                  "enable_tint" : self.enableTint }
        return ("scanlines", code, "// CRT TV scanlines and bright/dark banding filter\n")

    def onUpdate(self):
        if self.dynamicFlip:
            self.field = 1 - self.field

        # Update time counter.
        #
        if self.bandSpeed != 0.0:
            now = time.time()
            self._time += (now - self._prevtime)
            self._prevtime = now

            # Prevent float accuracy issues by discarding complete periods.
            #
            # (We can't just subtract once, because the user might freeze the band movement
            #  by temporarily setting the speed to zero - potentially for a long time - and resume later.)
            #
            fullperiod = 1.0/self.bandSpeed
            if self._time >= fullperiod:
                f, i = math.modf(self._time / fullperiod)
                self._time -= i*fullperiod
        else:
            self._time = 0.0
        if self.finalQuad is not None:
            self.finalQuad.setShaderInput( self.getMangledName("scanlines_bandparams"), self._computeBandParamsInput() )


    # These private methods pack parameters into shader inputs to save on the number of inputs needed.
    def _computeBandParamsInput(self):
        return Vec4(self._bandStrength, self._bandSpeed, self._bandSize, self._time)

    def _computeDarkParamsInput(self):
        return Vec4(self._lineThickness, self._field, self._strength, 0.0)

    @property
    def field(self):
        """Which field to keep, either Scanlines.FIELD_TOP or Scanlines.FIELD_BOTTOM."""
        return self._field
    @field.setter
    def field(self, value):
        self._field = value
        if self.finalQuad is not None:
            self.finalQuad.setShaderInput( self.getMangledName("scanlines_darkparams"), self._computeDarkParamsInput() )

    @property
    def strength(self):
        """Darkening effect strength (float). 1 is fully scanlined, 0 does nothing."""
        return self._strength
    @strength.setter
    def strength(self, value):
        self._strength = value
        if self.finalQuad is not None:
            self.finalQuad.setShaderInput( self.getMangledName("scanlines_darkparams"), self._computeDarkParamsInput() )

    @property
    def lineThickness(self):
        """Thickness of each scanline in pixels (integer)."""
        return self._lineThickness
    @lineThickness.setter
    def lineThickness(self, value):
        self._lineThickness = value
        if self.finalQuad is not None:
            self.finalQuad.setShaderInput( self.getMangledName("scanlines_darkparams"), self._computeDarkParamsInput() )

    @property
    def dynamicFlip(self):
        """Whether to enable dynamic flip mode.

        Bool, default False.

        When enabled, the 'field' parameter is toggled at each frame rendered. With a steady refresh rate
        synced to display refresh, this creates a very faithful old CRT TV appearance, but the effect is
        very sensitive to even small unevenness in the framerate; if even one display refresh is missed,
        it shows immediately.

        """
        return self._dynamicFlip
    @dynamicFlip.setter
    def dynamicFlip(self, value):
        # This parameter is queried in update(); no need to do anything here except store the new value.
        self._dynamicFlip = value


    @property
    def bandStrength(self):
        """Strength of bright/dark band artifact.

        Float. Positive values make a bright band, negative values a dark band.

        Set this to 0.0 to disable the band effect.

        """
        return self._bandStrength
    @bandStrength.setter
    def bandStrength(self, value):
        self._bandStrength = value
        if self.finalQuad is not None:
            self.finalQuad.setShaderInput( self.getMangledName("scanlines_bandparams"), self._computeBandParamsInput() )


    @property
    def bandSpeed(self):
        """Movement speed of bright/dark band artifact.

        Float, in complete cycles per second. (The current rendering framerate is accounted for automatically.)

        """
        return self._bandSpeed
    @bandSpeed.setter
    def bandSpeed(self, value):
        self._bandSpeed = value
        if self.finalQuad is not None:
            self.finalQuad.setShaderInput( self.getMangledName("scanlines_bandparams"), self._computeBandParamsInput() )


    @property
    def bandSize(self):
        """Size of a single bright/dark band artifact, as fraction of view height.

        Float, default 1.0 = 100% of view height.

        """
        return self._bandSize
    @bandSize.setter
    def bandSize(self, value):
        if value == 0.0:
            raise ValueError("In %s %s: bandSize must be nonzero." % (self.__class__.__name__, self.name))
        self._bandSize = value
        if self.finalQuad is not None:
            self.finalQuad.setShaderInput( self.getMangledName("scanlines_bandparams"), self._computeBandParamsInput() )


    @property
    def enableTint(self):
        """Enable/disable tinting by CRT pixel matrix.

        Boolean, default False.

        The pixel matrix is currently hardcoded as horizontal, with adjacent pixel columns
        in the order R, G, B.

        """
        return self._enableTint
    @enableTint.setter
    def enableTint(self, value):
        # This option affects the compositor code, so we must rebuild the pipeline.
        if (not hasattr(self, "_enableTint")  or  value != self._enableTint)  and  self.pipeline is not None:
            self.pipeline._needsCompile = True
        self._enableTint = value

