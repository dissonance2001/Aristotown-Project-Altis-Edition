import math
import random
import sys


__all__ = ["describeException", "cmp", "quantize", "legacyRandInt", "chunks",
           "angleDifference", "angleLerp", "inverseLerp", "getSignOfNum"]

from typing import Union


def describeException(backTrace = 4):
    # When called in an exception handler, returns a string describing
    # the current exception.

    def byteOffsetToLineno(code, byte):
        # Returns the source line number corresponding to the given byte
        # offset into the indicated Python code module.

        import array
        lnotab = array.array('B', code.co_lnotab)

        line = code.co_firstlineno
        for i in range(0, len(lnotab), 2):
            byte -= lnotab[i]
            if byte <= 0:
                return line
            line += lnotab[i+1]

        return line

    infoArr = sys.exc_info()
    exception = infoArr[0]
    exceptionName = getattr(exception, '__name__', None)
    extraInfo = infoArr[1]
    trace = infoArr[2]

    stack = []
    while trace.tb_next:
        # We need to call byteOffsetToLineno to determine the true
        # line number at which the exception occurred, even though we
        # have both trace.tb_lineno and frame.f_lineno, which return
        # the correct line number only in non-optimized mode.
        frame = trace.tb_frame
        module = frame.f_globals.get('__name__', None)
        lineno = byteOffsetToLineno(frame.f_code, frame.f_lasti)
        stack.append("%s:%s, " % (module, lineno))
        trace = trace.tb_next

    frame = trace.tb_frame
    module = frame.f_globals.get('__name__', None)
    lineno = byteOffsetToLineno(frame.f_code, frame.f_lasti)
    stack.append("%s:%s, " % (module, lineno))

    description = ""
    for i in range(len(stack) - 1, max(len(stack) - backTrace, 0) - 1, -1):
        description += stack[i]

    description += "%s: %s" % (exceptionName, extraInfo)
    return description


def quantize(value, divisor):
    return float(int(value * int(divisor))) / int(divisor)


def cmp(a, b):
    return (a > b) - (a < b)


def legacyRandInt(randomInstance, low, high):
    """
    Because in Py3, the randint method was changed, we sometimes need to use the old method.
    This function emulates it.
    For this to work you need to pass in an instance of the random.Random() class.
    If you set a seed, be sure to use seed(..., version=1) as this uses the python 2 methods instead.
    """
    assert isinstance(randomInstance, random.Random)
    return low + int(randomInstance.random() * (high + 1 - low))


def chunks(l: list, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def angleDifference(a1: float, a2: float) -> float:
    """
    Calculates the difference between two angles.
    Returns within the range of [-180, 180].
    """
    return ((a2 - a1) + 180) % 360 - 180


def angleLerp(a1: float, a2: float, t: float) -> float:
    """
    Returns a lerp between two angles.
    """
    def shortAngleDist(b1: float, b2: float):
        maximum = 360
        da = (b2 - b1) % maximum
        return ((2 * da) % maximum) - da

    return a1 + shortAngleDist(a1, a2) * t


def inverseLerp(a: float, b: float, v: float) -> float:
    """
    Inverse lerp, get the fraction between a and b on which v resides.
        0.5 == inverseLerp(0, 100, 50)
        0.8 == inverseLerp(1, 5, 4.2)
    """
    return (v - a) / (b - a)


def getSignOfNum(num: Union[int, float]) -> int:
    """Get the sign of a number."""
    if num > 0:
        return 1
    elif num < 0:
        return -1
    return 0
