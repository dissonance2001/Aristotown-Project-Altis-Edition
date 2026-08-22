from toontown.shader.LUTShaderDefinition import LUTShaderDefinition
from toontown.shader.ShaderDefinition import ShaderDefinition
from toontown.shader.ShaderEnums import ShaderType
import sys


class __ShaderDefinitions(object):
    """
    The container class for shader definitions.
    """

    def __init__(self, definitions):
        self.definitions = definitions

    def getShaderDef(self, shaderType=ShaderType.Passthrough):
        return self.definitions.get(shaderType, self.definitions.get(ShaderType.Passthrough))


ShaderDefinitions = __ShaderDefinitions({
    ShaderType.Passthrough: ShaderDefinition(),
    ShaderType.Wobble:      ShaderDefinition(
        vertexFilename='wobble',
        uniformDefinitions={
            'speed': 1.0,
            'waves': 8.0,
            'power': 0.25,
        },
    ),
    ShaderType.LowPoly:     ShaderDefinition(
        vertexFilename='lowpoly',
        uniformDefinitions={
            'amt': 8,
        },
    ),
    ShaderType.Waterfall: ShaderDefinition(
        fragmentFilename='waterfall',
        uniformDefinitions={
            'hscroll': 0.0,
            'vscroll': 0.4,
            'frequency': 80,
            'amplitude': 0.006,
        }
    ),
    ShaderType.Ripple: ShaderDefinition(
        fragmentFilename='ripple',
        uniformDefinitions={
            'vscroll': 0.2,
            'chevron_depth': 0.4,
            'uv_xoffset': 0.5,
        }
    ),

    ShaderType.LUT_Default:       LUTShaderDefinition(lutFilename='def_lut.png'),
    ShaderType.LUT_Augusta:       LUTShaderDefinition(lutFilename='augusta_lut.png'),
    ShaderType.LUT_Bloomy:        LUTShaderDefinition(lutFilename='bloomy_lut.png'),
    ShaderType.LUT_Dark:          LUTShaderDefinition(lutFilename='dark_lut.png'),
    ShaderType.LUT_Dramatic:      LUTShaderDefinition(lutFilename='dramatic_lut.png'),
    ShaderType.LUT_Contrast:      LUTShaderDefinition(lutFilename='enhanced_contrast_lut.png'),
    ShaderType.LUT_Monochrome:    LUTShaderDefinition(lutFilename='monochrome_lut.png'),
    ShaderType.LUT_StrongMono:    LUTShaderDefinition(lutFilename='monochrome_strong_lut.png'),
    ShaderType.LUT_Moody:         LUTShaderDefinition(lutFilename='moody_lut.png'),
    ShaderType.LUT_Pop:           LUTShaderDefinition(lutFilename='pop_lut.png'),
    ShaderType.LUT_RedBlack:      LUTShaderDefinition(lutFilename='rednblack_lut.png'),
    ShaderType.LUT_Sunset:        LUTShaderDefinition(lutFilename='sunset_lut.png'),

    ShaderType.LUT_Monochromacy:  LUTShaderDefinition(lutFilename='achromatopsia_monochromacy_lut.png'),
    ShaderType.LUT_Deuteranomaly: LUTShaderDefinition(lutFilename='anomalous_trichromacy_deuteranomaly_lut.png'),
    ShaderType.LUT_Protanomaly:   LUTShaderDefinition(lutFilename='anomalous_trichromacy_protanomaly_lut.png'),
    ShaderType.LUT_Tritanomaly:   LUTShaderDefinition(lutFilename='anomalous_trichromacy_tritanomaly_lut.png'),
    ShaderType.LUT_BlueCone:      LUTShaderDefinition(lutFilename='blue_cone_monochromacy_lut.png'),
    ShaderType.LUT_Deuteranopia:  LUTShaderDefinition(lutFilename='dichromatic_view_deuteranopia_lut.png'),
    ShaderType.LUT_Protanopia:    LUTShaderDefinition(lutFilename='dichromatic_view_protanopia_lut.png'),
    ShaderType.LUT_Tritanopia:    LUTShaderDefinition(lutFilename='dichromatic_view_tritanopia_lut.png'),

})


ColorblindShaders = [
    ('Disabled',    None),
    ('Augusta',     ShaderType.LUT_Augusta),
    ('Bloomy',      ShaderType.LUT_Bloomy),
    ('Dark',        ShaderType.LUT_Dark),
    ('Dramatic',    ShaderType.LUT_Dramatic),
    ('Contrast',    ShaderType.LUT_Contrast),
    ('Monochrome',  ShaderType.LUT_Monochrome),
    ('Moody',       ShaderType.LUT_Moody),
    ('Pop',         ShaderType.LUT_Pop),
]


def canUseShaders():
    return sys.platform == 'win32'