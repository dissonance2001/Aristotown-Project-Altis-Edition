"""
A utils file with several functions dedicated
for dealing with Panda3D's color funnies.
"""
from direct.showbase.PythonUtil import lerp
import colorsys
import random

"""
Number Constants
"""
c_black = (0, 0, 0, 1)
c_white = (1, 1, 1, 1)
c_empty = (0, 0, 0, 0)

"""
Number Operations
"""
def lerpColor(a, b, t=0.50):
    color = []
    for valA, valB in zip(a, b):
        color.append(lerp(valA, valB, t))
    return tuple(color)

def lerpPColSmart(a, b, t=0.50):
    return hsvToPCol(
        *lerpColor(
            pcolToHsv(a),
            pcolToHsv(b),
            t,
        )
    )

def dimColor(col, t=0.0):
    return lerpColor(col, (0, 0, 0, col[3]), t)

def undimColor(col, t=0.0):
    return lerpColor(col, (1, 1, 1, col[3]), t)

"""
RGB Conversion Methods
"""
def rgbToPCol(r, g, b, a=255):
    """
    Converts a 0-255 RGBA value to a Panda3D 0-1 value.
    :param r: Red 0-255
    :param g: Green 0-255
    :param b: Blue 0-255
    :param a: (optional) Alpha 0-255
    :return: Tuple, with Panda3D rgba values
    """
    return r / 255.0, g / 255.0, b / 255.0, a / 255.0

def hexToPCol(hexString, a=255):
    """
    Converts a hex string into a Panda3D 0-1 value.
    :param hexString: A 6-character hex string.
    :return: Tuple, with Panda3D rgba values
    """
    hexString = hexString.replace("#", "")
    assert len(hexString) == 6
    assert all(letter in "0123456789ABCDEFabcdef" for letter in hexString)
    return tuple([int(hexString[i:i+2], 16) / 255.0 for i in (0, 2, 4)] + [a / 255.0])

def hexToRGB(hexString, a=255):
    """
    Converts a hex string into 0 to 255 RGB.
    :param hexString: A 6-character hex string.
    :return: Tuple, with rgba values
    """
    hexString = hexString.replace("#", "")
    assert len(hexString) == 6
    assert all(letter in "0123456789ABCDEFabcdef" for letter in hexString)
    return tuple([int(hexString[i:i+2], 16) for i in (0, 2, 4)] + [a])

def hexToHSV(hexString, a=255):
    r, g, b, _ = hexToRGB(hexString)
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    return h, s, v, a / 255.0

def rgbToHex(r, g, b):
    """
    Converts 0-255 RGB into a hex string.
    """
    return "{:02x}{:02x}{:02x}".format(r, g, b)

"""
HSV Conversion Methods
"""
def hsvToPCol(hue, sat, val, a=255):
    rgb = colorsys.hsv_to_rgb(hue, sat, val)
    return rgbToPCol(*tuple([int(round(x * 255)) for x in rgb]), a=a)

def pcolToHsv(pcol):
    r, g, b, a = pcol
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    return h, s, v, a * 255

"""
Useful class transformers
"""
def dict_hexToRGB(d, a=255):
    """
    Converts the keys within a passed dictionary
    into RGB format.
    """
    return {hexToRGB(key, a=a): value for key, value in list(d.items())}

"""
Random color generation
"""
def randomNormalizedColor(a=1.0):
    return random.random(), random.random(), random.random(), a