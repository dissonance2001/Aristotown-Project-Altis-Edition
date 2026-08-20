from __future__ import absolute_import
from panda3d.core import LVector4f
from six.moves import range

def dgiExtractString8(dgi):
    return dgi.getString()

def dgiExtractColor(dgi):
    return LVector4f(*(dgi.getUint8() / 255.0 for _ in range(4)))