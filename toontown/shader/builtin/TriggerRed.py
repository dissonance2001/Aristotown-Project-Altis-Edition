import math

from panda3d.core import Vec3

from toontown.shader.Filter import Filter


def rgb2hsl(R, G, B, mode):
    """Convert RGB color tuple to HSL.

    Parameters:

        R,G,B = RGB values as double-precision floats, with each component in [0,1].

        mode  = string, one of:

                "hexagon" = use piecewise hexagon definition of hue (exact)

                "circle"  = use cartesian-to-polar transformation to determine hue
                            (approximate, but branch-free)

    Return value:

        (H,S,L) tuple.

        The hue of a gray color is here defined to be zero (for convenience).

    For more information:
        https://en.wikipedia.org/wiki/HSL_and_HSV

    """
    if R < 0.0  or  R > 1.0:
        raise ValueError("R component = %g out of range [0,1]" % R)
    if G < 0.0  or  G > 1.0:
        raise ValueError("G component = %g out of range [0,1]" % G)
    if B < 0.0  or  B > 1.0:
        raise ValueError("B component = %g out of range [0,1]" % B)

    M = max( (R, G, B) )
    m = min( (R, G, B) )
    C = M - m  # chroma (exact)

    # hue
    if C == 0.0:
        H = 0.0  # hue undefined for grays; use zero for convenience
    else:
        if mode == "hexagon":  # exact
            if M == R:
                H = (G - B)/C
                if H < 0.0:
                    H += 6.0
            elif M == G:
                H = (B - R) + 2.0
            elif M == B:
                H = (R - G) + 4.0
            else:
                raise ValueError("Cannot happen")
            H *= (60./360.)
        elif mode == "circle":  # cartesian-to-polar transformation; approximate, but can be computed in a branch-free manner
            alpha = 0.5 * (2.0 * R - G - B)
            beta  = math.sqrt(3.0)/2.0 * (G - B)
            H = math.atan2(beta, alpha) / (2.0*math.pi)  # hue
            if H < 0.0:
                H += 1.0
#            Chr = math.sqrt(a**2 + b**2)  # chroma consistent with mode == "circle"
        else:
            raise ValueError("Unknown mode '%s'; valid: hexagon, circle")

    # HSL lightness
    L = 0.5 * (M + m)

    # saturation
    if L == 0.0 or L == 1.0:
        S = 0.0
    else:
        S = C / (1.0 - abs(2.0*L - 1.0))

    return (H, S, L)


# Unused; given for reference only.
#
def hsl2rgb(H, S, L):
    """Convert HSL color tuple to RGB.

    Implements only the conversion corresponding to the "hexagon" mode of rgb2hsl().

    Parameters:

        H,S,L = HSL values as double-precision floats, with each component in [0,1].

    Return value:

        (R,G,B) tuple

    For more information:
        https://en.wikipedia.org/wiki/HSL_and_HSV#From_HSL

    """
    if H < 0.0  or  H > 1.0:
        raise ValueError("H component = %g out of range [0,1]" % H)
    if S < 0.0  or  S > 1.0:
        raise ValueError("S component = %g out of range [0,1]" % S)
    if L < 0.0  or  L > 1.0:
        raise ValueError("L component = %g out of range [0,1]" % L)

    # hue chunk
    Hpf = H / (60./360.) # "H prime, float" (H', float)
    Hp = int(Hpf)  # "H prime" (H', int)
    if Hp >= 6:  # catch special case 360deg = 0deg
        Hp = 0

    C = (1.0 - math.fabs(2.0*L - 1.0))*S  # HSL chroma
    X = C * (1.0 - math.fabs( math.modf(Hpf / 2.0)[0] - 1.0 ))

    if S == 0.0:  # H undefined if S == 0
        R1, G1, B1 = (0.0, 0.0, 0.0)
    elif Hp == 0:
        R1, G1, B1 = (C,   X,   0.0)
    elif Hp == 1:
        R1, G1, B1 = (X,   C,   0.0)
    elif Hp == 2:
        R1, G1, B1 = (0.0, C,   X  )
    elif Hp == 3:
        R1, G1, B1 = (0.0, X,   C  )
    elif Hp == 4:
        R1, G1, B1 = (X,   0.0, C  )
    elif Hp == 5:
        R1, G1, B1 = (C,   0.0, X  )

    # match the HSL Lightness
    #
    m = L - 0.5*C
    R, G, B = (R1 + m, G1 + m, B1 + m)

    return (R, G, B)


# Basic desaturation (monochrome)
#
DESAT_BASIC_BODY = """#define TV_STANDARD %(tvStandard)d

#if TV_STANDARD == 709
const float3 desat_rgb_weights = float3(0.21, 0.72, 0.07); // ITU-R Rec. 709 (HDTV)
#else
const float3 desat_rgb_weights = float3(0.30, 0.59, 0.11); // ITU-R Rec. 601 (NTSC SDTV)
#endif

// compute luma (fully desaturated pixel)
float desat_luma = dot(pixcolor.rgb, desat_rgb_weights);

// apply tint to the fully desaturated pixel
float3 desat_color = %(k_desat_tint)s.rgb * desat_luma.xxx;

// blend the desaturated and tinted result with the original pixel
pixcolor.rgb = lerp(pixcolor.rgb, desat_color.rgb, %(k_desat_strength)s);
"""


# TriggerRed with hue bandpass (e.g. keep only red things)
#
DESAT_BANDPASS_BODY = """#define TV_STANDARD %(tvStandard)d

// Calculate hue of this pixel (cartesian-to-polar approximation)
//
// (Alpha and beta are cartesian coordinates of the color in the chroma plane,
//  having nothing to do with the alpha channel.)
//
float desat_alpha = 0.5 * (2.0 * pixcolor.r - pixcolor.g - pixcolor.b);
float desat_beta  = sqrt(3.0)/2.0 * (pixcolor.g - pixcolor.b);
float desat_h = atan2(desat_beta,desat_alpha) / (2.0 * 3.141592654); // let's hope atan2(0,0) = 0 for this implementation
if(desat_h < 0.0)  // atan2 usually gives results in [-pi,pi), so desat_h will be in [-0.5, 0.5)
    desat_h += 1.0;  // we want desat_h in [0, 1)

// Calculate distance from reference hue, accounting for wrap-around at both ends.
//
//   - Case 1 of 3: plain distance, no wrap
//
float desat_temp1 = abs(desat_h - %(k_desat_bandpass_h)s);

//   - Case 2 of 3: this is the smallest distance if desat_h near left end, reference near right end
//
float desat_temp2 = abs((desat_h+1.0) - %(k_desat_bandpass_h)s);

//   - Case 3 of 3: this is the smallest distance if desat_h near right end, reference near left end
//
float desat_temp3 = abs(desat_h - (%(k_desat_bandpass_h)s+1.0));

// Smallest distance, normalized to [0, 1)
//
float desat_hue_distance = 2.0 * min(min(desat_temp1, desat_temp2), desat_temp3);

// Compute bandpass blend strength.
//
// - pixels with their hue further away than k_desat_bandpass_q are fully desaturated
// - as distance falls below k_desat_bandpass_q, a blend starts very gradually
// - as the hue difference approaches zero, the pixel is fully passed through
// - the 1.0 - ... acrobatics together with the squaring make a sharp spike at the reference hue
//
float desat_diff  = 1.0 - min(desat_hue_distance/%(k_desat_bandpass_q)s, 1.0);
float desat_diff2 = desat_diff*desat_diff;
float desat_mult = (1.0 - desat_diff2);

#if TV_STANDARD == 709
const float3 desat_rgb_weights = float3(0.21, 0.72, 0.07); // ITU-R Rec. 709 (HDTV)
#else
const float3 desat_rgb_weights = float3(0.30, 0.59, 0.11); // ITU-R Rec. 601 (NTSC SDTV)
#endif

// Tint must be applied uniformly to the whole monochrome picture, regardless of the
// local strength of the bandpassing, so we must be careful here.
//
// (Also, desat_mult may behave wildly near gray areas, which have no well-defined hue.
//  In these areas the filter effectively does nothing, but this does mean that desat_mult
//  cannot be relied on for anything except its original purpose.)
//
// Correct ordering:
//   - compute luma (fully desaturated pixel, ignoring the bandpass)
//
float desat_luma = dot(pixcolor.rgb, desat_rgb_weights);

//   - compute fully desaturated pixel, with the bandpass taken into account.
//     This is done by blending between the original and the fully desaturated pixel,
//     using desat_mult as blend strength.
//   - apply tint *to the result*. This applies it uniformly, regardless of desat_mult.
//
float3 desat_color = lerp(pixcolor.rgb, desat_luma.xxx, desat_mult) * %(k_desat_tint)s;

//   - blend the desaturated and tinted result with the original pixel.
//
pixcolor.rgb = lerp(pixcolor.rgb, desat_color.rgb, %(k_desat_strength)s);
"""


class TriggerRed(Filter):
    """TriggerRed (monochrome) filter with tinting and adjustable strength.

    Introduced in Panda 1.9.0.

    Optionally, a hue bandpass is available. This can be used to retain only
    e.g. red objects in color (with bandpassColor=(1,0,0)), while making the
    rest of the picture into monochrome.

    """

    def __init__(self, **kwargs):
        super(TriggerRed, self).__init__(**kwargs)

    def onReset(self):
        super(TriggerRed, self).onReset()  # reset inherited properties

        self.sort = 50
        self.stageName   = "FilmOrDetector"
        self.isMergeable = True

        self.mode          = "basic"
        self.luma          = "HDTV"
        self.strength      = 1.0
        self.tintColor     = (1.0, 0.0, 0.0)
        self.bandpassColor = (1.0, 0.0, 0.0)
        self.bandpassQ     = 0.25

    def onAttachPipeline(self):
        self.registerCustomInput(inputType="float3", inputName="k_desat_tint")
        self.registerCustomInput(inputType="float",  inputName="k_desat_strength")
        self.registerCustomInput(inputType="float",  inputName="k_desat_bandpass_h")
        self.registerCustomInput(inputType="float",  inputName="k_desat_bandpass_q")

    def onSynthesizeCompositor(self):
        tvStandard = 709 if self.luma == "HDTV" else 601

        if self.mode == "basic":
            code = DESAT_BASIC_BODY % { "tvStandard" : tvStandard,
                                        "k_desat_tint"     : self.getMangledName("k_desat_tint"),
                                        "k_desat_strength" : self.getMangledName("k_desat_strength") }
            comment = "// TriggerRed filter (compile-time mode: basic)\n"
        elif self.mode == "bandpass":
            code = DESAT_BANDPASS_BODY % { "tvStandard": tvStandard,
                                           "k_desat_tint": self.getMangledName("k_desat_tint"),
                                           "k_desat_strength": self.getMangledName("k_desat_strength"),
                                           "k_desat_bandpass_h": self.getMangledName("k_desat_bandpass_h"),
                                           "k_desat_bandpass_q": self.getMangledName("k_desat_bandpass_q"), }
            comment = "// TriggerRed filter (compile-time mode: bandpass)\n"
        else:
            raise ValueError("Tint: invalid mode '%s'; valid: 'basic', 'bandpass'" % self.mode)
        return ("desaturation", code, comment)


    @property
    def mode(self):
        """TriggerRed mode.

        String, one of:

          "basic"    = Basic desaturation. Default.

          "bandpass" = TriggerRed with hue bandpass (e.g. keep only red things).
                       This enables the additional parameters bandpassColor and bandpassQ.

        """
        return self._mode
    @mode.setter
    def mode(self, value):
        if (not hasattr(self, "_mode")  or  value != self._mode)  and  self.pipeline is not None:
            self.pipeline._needsCompile = True
        self._mode = value


    @property
    def luma(self):
        """Luma calculation mode (default "HDTV").

        This selects the TV standard from which the R,G,B weights are taken when calculating luma.
        This is intended to produce perceptually correct luma.

        String, one of:

          "HDTV" = ITU-R Rec. 709, colloquially known as HDTV.

          "SDTV" = ITU-R Rec. 601, colloquially known as NTSC SDTV.

        """
        return self._luma
    @luma.setter
    def luma(self, value):
        if (not hasattr(self, "_luma")  or  value != self._luma)  and  self.pipeline is not None:
            self.pipeline._needsCompile = True
        self._luma = value


    @property
    def strength(self):
        """Effect strength, float. 1 is fully desaturated, 0 is off.

        Default 1.0.

        """
        return self._strength
    @strength.setter
    def strength(self, value):
        self._strength = value
        if self.finalQuad is not None:
            self.finalQuad.setShaderInput( self.getMangledName("desat_strength"), value )


    @property
    def tintColor(self):
        """Tint color, (R,G,B) tuple of floats, each component in interval [0, 1].

        After converting to monochrome, the result is modulated (multiplied) by this color.
        This can be used for sepia toning; try e.g. tintColor=(0.88, 0.75, 0.57).

        Default is no tinting (1.0, 1.0, 1.0).

        This differs from the separate tint filter in that this tint is applied after
        conversion to monochrome, but before blending the result onto the scene;
        only the monochrome picture is tinted.

        The desaturation filter supports only multiplicative tinting (as in mode="multiply" of Tint filter)
        in its internal tinter, and the alpha value in the tint color is not supported.

        """
        return self._tintColor
    @tintColor.setter
    def tintColor(self, value):
        self._tintColor = value
        if self.finalQuad is not None:
            self.finalQuad.setShaderInput( self.getMangledName("desat_tint"), Vec3(value) )


    @property
    def bandpassColor(self):
        """Reference color for hue bandpass (default bright red (1.0, 0.0, 0.0)).

        Optional, used only when mode="bandpass".

        Pixels whose hue matches this color will not be desaturated, while everything else will.
        The sensitivity of the matching can be controlled with bandpassQ.

        (R,G,B) tuple of floats, each component in interval [0, 1].

        Note that passing a grayscale color here makes no sense, as it does not have a hue.

        The HSL hue is automatically extracted out of the RGB color specified.
        Saturation and lightness of the reference color are ignored.

        """
        return self._bandpassColor
    @bandpassColor.setter
    def bandpassColor(self, value):
        self._bandpassColor = value
        if self.finalQuad is not None:
            # We must use the same hue calculation algorithm both here and in the shader.
            # The shader uses the branch-free approximate algorithm.
            H, S, L = rgb2hsl(R=value[0], G=value[1], B=value[2], mode="circle")
            self.finalQuad.setShaderInput( self.getMangledName("desat_bandpass_h"), H )


    @property
    def bandpassQ(self):
        """Falloff parameter for hue bandpass (float, default 0.25).

        Optional, used only when mode="bandpass".

        At bandpassQ = 0.01 (minimum), the hue must match exactly for the pixel to be passed through,
        whereas at bandpassQ = 1 a large range of hues passes the test (for Q = 1, the exact opposite
        color is exactly at the cutoff point).

        The effect strength is modulated by how much the hue of each pixel differs from the
        hue extracted from bandpassColor.

        The modulation is quadratic, with its slowly changing end at the hues that are far away
        from the reference. The profile is a spike centered on the reference hue.

        """
        return self._bandpassQ
    @bandpassQ.setter
    def bandpassQ(self, value):
        self._bandpassQ = value
        if self.finalQuad is not None:
            self.finalQuad.setShaderInput( self.getMangledName("desat_bandpass_q"), value )

