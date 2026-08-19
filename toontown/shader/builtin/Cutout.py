from panda3d.core import Vec2, Vec4

from toontown.shader.Filter import Filter

CUTOUT_BODY="""#define SHAPE %(cutoutShape)d
#define WHICH %(maskAwayWhich)d
#define BLENDMODE %(blendMode)d

const float effectStrength  = %(k_cutout_params)s.x;
const float smoothingRadius = %(k_cutout_params)s.y;

// In the area to be *masked out* this is 1.0; inside the area to be *preserved* this is 0.0;
// with intermediate values at the smoothed boundary.
//
float maskstrength;


#if SHAPE == 0

// rectangle
// bbox = xmin, xmax, ymin, ymax

float strengthL =       smoothstep( %(k_cutout_bbox)s.x - smoothingRadius, %(k_cutout_bbox)s.x + smoothingRadius, %(texcoord_txcolor)s.x );
float strengthR = 1.0 - smoothstep( %(k_cutout_bbox)s.y - smoothingRadius, %(k_cutout_bbox)s.y + smoothingRadius, %(texcoord_txcolor)s.x );
float strengthX = strengthL*strengthR;

float strengthD =       smoothstep( %(k_cutout_bbox)s.z - smoothingRadius, %(k_cutout_bbox)s.z + smoothingRadius, %(texcoord_txcolor)s.y );
float strengthU = 1.0 - smoothstep( %(k_cutout_bbox)s.w - smoothingRadius, %(k_cutout_bbox)s.w + smoothingRadius, %(texcoord_txcolor)s.y );
float strengthY = strengthU*strengthD;

// The strengthX*strengthY (instead of max(strengthX,strengthY)) gives rounded corners.
maskstrength = 1.0 - strengthX*strengthY;


#else

// ellipse
// bbox = xmin, xmax, ymin, ymax

const float2 ellipseCenter = float2(  (%(k_cutout_bbox)s.x + %(k_cutout_bbox)s.y )/2.0,
                                      (%(k_cutout_bbox)s.z + %(k_cutout_bbox)s.w )/2.0  );
const float2 ellipsePaxes  = float2(  ellipseCenter.x - %(k_cutout_bbox)s.x,
                                      ellipseCenter.y - %(k_cutout_bbox)s.z  );

const float2 dist = %(texcoord_txcolor)s - ellipseCenter;

// The ellipse boundary is located at
//
// ( (x - x0)/rx )**2 + ( (y - y0)/ry )**2 = 1
//
// Here rx and ry are the lengths of the principal axes.
//
const float2 temp = dist / ellipsePaxes;
const float  val  = dot(temp, temp);

// Hence replacing rx -> A*rx, ry -> A*ry (where A is a scaling factor), the new boundary is at val = A**2.
//
float v1 = 1.0 - smoothingRadius;
v1 *= v1;
float v2 = 1.0 + smoothingRadius;
v2 *= v2;
maskstrength = smoothstep( v1, v2, val );

#endif


#if WHICH == 0
  // mask away inside; invert mask
  maskstrength = 1.0 - maskstrength;
#endif


// We want a parameter that goes from 0 at full passthrough (maskstrength = 0.0)
// to effectStrength at fully matted away (maskstrength = 1.0).
//
const float t = effectStrength * maskstrength;

#if BLENDMODE == 0
// rgba
pixcolor = lerp(pixcolor, %(k_cutoutcolor)s, t);

#elif BLENDMODE == 1
pixcolor.rgb = lerp(pixcolor.rgb, %(k_cutoutcolor)s.rgb, t);

#else
pixcolor.a = lerp(pixcolor.a, %(k_cutoutcolor)s.a, t);

#endif
"""


class Cutout(Filter):
    """A simple geometric cutout/masking filter.

    Introduced in Panda 1.9.0.

    Rectangle and ellipse shapes. Can mask either the inside or the outside of the shape.
    Smoothed boundary. Configurable strength and mask color (RGBA). RGBA, RGB and A (alpha only) blending.

    Can be used for various effects:

      - black bands effect (e.g. game pausing, cutscenes)
      - rudimentary flashlight
      - classic cartoon sequence finish (circle shrinking onto character, hiding the rest of the scene)
      - film burning through in projector (each hole one instance of this filter)
      - with the help of two scene graphs blended on top of each other, and blendMode="a" to mask
        only in the alpha channel, with this filter applied to the "topmost" scene in the blend:
          - a lens revealing "invisible" objects
          - see-through walls around character

    """

    def __init__(self, **kwargs):
        super(Cutout, self).__init__(**kwargs)

    def onReset(self):
        super(Cutout, self).onReset()  # reset inherited properties

        self.sort = 50
        self.stageName   = "Postprocess"
        self.isMergeable = True

        self.boundingBox     = (0.0, 1.0, 0.0, 1.0)  # xmin, xmax, ymin, ymax
        self.shape           = "ellipse"
        self.maskAwayWhich   = "outside"
        self.maskColor       = (0.0, 0.0, 0.0, 1.0)
        self.blendMode       = "rgba"
        self.strength        = 1.0
        self.smoothingRadius = 0.02

    def onAttachPipeline(self):
        self.registerInputTexture(texName="color")
        self.registerCustomInput(inputType="float4", inputName="k_cutoutcolor")
        self.registerCustomInput(inputType="float2", inputName="k_cutout_params")
        self.registerCustomInput(inputType="float4", inputName="k_cutout_bbox")

    def onSynthesizeCompositor(self):
        txcolor = self.getTextureInfo("color")

        shape = 0 if self.shape == "rectangle" else 1
        maskAwayWhich = 0 if self.maskAwayWhich == "inside" else 1
        modemap = { "rgba" : 0, "rgb" : 1, "a" : 2 }
        blendMode = modemap[self.blendMode]

        code = CUTOUT_BODY % { "texcoord_txcolor"      : txcolor.get('texcoord'),
                               "cutoutShape"           : shape,
                               "maskAwayWhich"         : maskAwayWhich,
                               "blendMode"             : blendMode,
                               "k_cutoutcolor"         : self.getMangledName("k_cutoutcolor"),
                               "k_cutout_params"       : self.getMangledName("k_cutout_params"),
                               "k_cutout_bbox"         : self.getMangledName("k_cutout_bbox") }
        return ("cutout", code, "// cutout/masking filter\n")


    # This private method packs parameters into one shader input to save on the number of inputs needed.
    def _computeParamsInput(self):
        return Vec2(self._strength, self._smoothingRadius)


    @property
    def boundingBox(self):
        """Bounding box of the mask.

        Sets the mask location in the view.

        Default (0.0, 1.0, 0.0, 1.0).

        Tuple (xmin, xmax, ymin, ymax), each value a float (typically in interval [0,1], representing the view limits).
        Must have  xmin <= xmax,  ymin <= ymax.

        """
        return self._boundingBox
    @boundingBox.setter
    def boundingBox(self, value):
        if len(value) != 4:
            raise ValueError("In %s %s: bounding box must be a tuple of length 4." % (self.__class__.__name__, self.name))
        if value[1] - value[0] < 0.0:
            raise ValueError("In %s %s: bounding box must have xmin <= xmax, but xmin = %g, xmax = %g." % (self.__class__.__name__, self.name, value[0], value[1]))
        if value[3] - value[2] < 0.0:
            raise ValueError("In %s %s: bounding box must have ymin <= ymax, but ymin = %g, ymax = %g." % (self.__class__.__name__, self.name, value[2], value[3]))

        self._boundingBox = value
        if self.finalQuad is not None:
            self.finalQuad.setShaderInput( self.getMangledName("cutout_bbox"), Vec4(value) )


    @property
    def shape(self):
        """Shape of the mask.

        String, one of: "ellipse" (default), "rectangle".

        """
        return self._shape
    @shape.setter
    def shape(self, value):
        if value not in ["ellipse", "rectangle"]:
            raise ValueError("In %s %s: unknown shape '%s', valid: 'ellipse', 'rectangle'" % (self.__class__.__name__, self.name, value))
        if (not hasattr(self, "_shape")  or  value != self._shape)  and  self.pipeline is not None:
            self.pipeline._needsCompile = True
        self._shape = value


    @property
    def maskAwayWhich(self):
        """Whether to mask away the inside or the outside.

        String, one of: "inside", "outside" (default).

        """
        return self._maskAwayWhich
    @maskAwayWhich.setter
    def maskAwayWhich(self, value):
        if value not in ["inside", "outside"]:
            raise ValueError("In %s %s: unknown maskAwayWhich '%s', valid: 'inside', 'outside'" % (self.__class__.__name__, self.name, value))
        if (not hasattr(self, "_maskAwayWhich")  or  value != self._maskAwayWhich)  and  self.pipeline is not None:
            self.pipeline._needsCompile = True
        self._maskAwayWhich = value


    @property
    def maskColor(self):
        """Mask color as (R,G,B,A) float tuple, each component in [0,1].

        Which components are actually used depends on the blending mode.

        """
        return self._maskColor
    @maskColor.setter
    def maskColor(self, value):
        self._maskColor = value
        if self.finalQuad is not None:
            self.finalQuad.setShaderInput( self.getMangledName("cutoutcolor"), value )


    @property
    def blendMode(self):
        """Blend mode.

        String, one of: "rgba" [default], "rgb" (color components only), "a" (alpha component only).

        The filter interpolates between the current pixel and maskColor,
        affecting either rgba, rgb or just the alpha, depending on what is chosen here.

        """
        return self._blendMode
    @blendMode.setter
    def blendMode(self, value):
        if value not in ["rgba", "rgb", "a"]:
            raise ValueError("In %s %s: unknown blendMode '%s', valid: 'rgba', 'rgb', 'a'" % (self.__class__.__name__, self.name, value))
        if (not hasattr(self, "_blendMode")  or  value != self._blendMode)  and  self.pipeline is not None:
            self.pipeline._needsCompile = True
        self._blendMode = value


    @property
    def strength(self):
        """Strength of the effect.

        Float in interval [0, 1]. Default 1.0.

        """
        return self._strength
    @strength.setter
    def strength(self, value):
        self._strength = value
        if self.finalQuad is not None:
            self.finalQuad.setShaderInput( self.getMangledName("cutout_params"), self._computeParamsInput() )


    @property
    def smoothingRadius(self):
        """Smoothing radius at the boundary of the mask, in texture coordinate units.

        Float in interval [0, 1]. Default 0.02.

        """
        return self._smoothingRadius
    @smoothingRadius.setter
    def smoothingRadius(self, value):
        self._smoothingRadius = value
        if self.finalQuad is not None:
            self.finalQuad.setShaderInput( self.getMangledName("cutout_params"), self._computeParamsInput() )

