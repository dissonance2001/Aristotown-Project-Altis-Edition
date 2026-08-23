"""Module for common functions needed by components of the postprocessing filter system."""

from __future__ import print_function

# legacy API error reporting
import sys
import traceback
import inspect

from panda3d.core import Texture

def indent(s, n):
    """Helper function to indent each line of a string.

    Supports single-line (no terminating linefeed), single-line (with terminating linefeed)
    and multi-line strings. Linefeeds will be preserved.

    Parameters:
      s = string to indent
      n = number of spaces to indent by

    Return value:
      indented string

    """
    hadTermLF = (len(s) > 0) and (s[-1] == "\n")

    # TODO: if the input contains any blank lines, leave those blank (do not generate trailing whitespace)

    # This unfortunately strips one terminating linefeed if the string has any...
    temp = "\n".join((n * " ") + line for line in s.splitlines())
    # ...so we add it back.
    if hadTermLF:
        return temp + "\n"
    else:
        return temp


def makeFilterTexture(texName):
    """Helper function to create fullscreen filter textures, setting some appropriate parameters automatically."""
    tex = Texture("scene-"+texName)
    tex.setWrapU(Texture.WMClamp)
    tex.setWrapV(Texture.WMClamp)
    return tex


def dumpExceptionTrace(file=sys.stderr):
    """Dump an exception and stack trace, emulating the format used by the Python interpreter.

    Parameters:

      file = file where to dump; this is passed to the "file" argument of print().

    Currently used in the CommonFilters legacy API, where stderr is the only way
    to alert the programmer of what exactly went wrong.

    Call this from inside an "except" block. If no exception is currently being handled, this does nothing.

    """
    # - extract_tb() traceback terminates at the level that is handling the except clause.
    #   While it is potentially useful extra information to see how the exception was raised
    #   inside the postprocessing filter system, what the caller would really like to know
    #   is where the problem occurred in the application.
    #
    # - extract_stack() gives us the "caller side" of the stack trace.
    #
    exc_type, exc_value, exc_traceback = sys.exc_info()

    # If no exception is being handled, do nothing.
    if exc_type is None:
        del exc_traceback
        return

    try:
        frames = inspect.stack()

        print("Traceback (most recent call last):", file=file)
        if len(frames) >= 3:
            # We start tracing the stack from two frames up, because:
            #   - current frame here points to the line calling extract_stack()
            #   - parent frame points to the line calling dumpExceptionTrace() in our caller
            #   - grandparent frame points to our caller's caller - which is the line in the application
            #     that caused the exception in our caller.
            #
            # The "inner frames" (our caller and any inner levels) we get from the exception traceback.
            #
            st = traceback.extract_stack(f=frames[2][0])
        else:
            st = []

        tb = traceback.extract_tb(exc_traceback)
        fullTrace = st + tb
        lines = traceback.format_list(fullTrace)
        for text in lines:
            print(text, file=file, end="")

        lines = traceback.format_exception_only(exc_type, exc_value)
        for text in lines:
            print(text, file=file, end="")

    finally:
        # See warnings in the Python manual about storing tracebacks and frame objects;
        # explicit deletion is recommended.
        #
        del exc_traceback
        del frames

