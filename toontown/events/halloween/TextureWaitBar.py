from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectGui import DGG
from direct.gui.OnscreenImage import OnscreenImage

from panda3d.core import Plane, PlaneNode, Vec3, Point3

from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class TextureWaitBar(DirectFrame):
    # A custom wait bar currently for the halloween pass GUI (since P3D's is limiting)
    # Might make this something more generic if required in the future
    #
    # edit: okay, maybe not? idk, this is a mess, even if it somehow works >_>

    def __init__(self, background, fillIn, parent=None, updateRate=0.05, backgroundScale=(1, 1, 0.125),
                 fillInScale=(1, 1, 0.125), fillInStartOffset=0, fillInClipLeft=True, fillInClipBounds=(-0.308, 0.304),
                 noClip=False, **kwargs):
        """
        A custom wait bar that uses a background and fillIn geom's instead of a background and a simple boring color
        for fillIn. Any other args will go to DirectFrame itself.

        :param background:  the background image/geom to use
        :param fillIn:      the image/geom to fill in the progress bar
        :param parent:      the GUI's parent (like any other Direct* object)
        :param updateRate:  <currently unused; todo>
        :param backgroundScale:  the scale to use for the background image
        :param fillInScale:    the scale to use for the fillIn image
        :param fillInStartOffset:   the X offset for the starting bit of the fillIn image
        :param fillInClipLeft:  if True, start clipping from -1, else, starts at 1
        :param fillInClipBounds: the start and end bounds (-1 to 1) for the clipping (might want to mess with this)
        :param noClip:  disables the fillIn clipper (basically for testing out your background + fillIn stuff)
        :param kwargs: any other keyword arguments to pass to DirectFrame
        """
        option_defs = (
            ('frameSize', (-1, 1, -0.08, 0.08), None),
            ('frameColor', (0, 0, 0, 0), self.setFrameColor),
            ('sortOrder', DGG.NO_FADE_SORT_INDEX, None),
            ('relief', None, self.setRelief),
        )
        self.defineoptions(kwargs, option_defs)
        DirectFrame.__init__(self, parent=parent)
        self.initialiseoptions(TextureWaitBar)

        # probably allow these to be customizable in the future
        self._value = 0
        self._range = 100

        # don't necessarily need this in HalloweenPass, but might be useful in the future?
        self._lastUpdateTime = 0
        self._updateRate = updateRate

        self._background = OnscreenImage(
            parent=self,
            image=background,
            scale=backgroundScale
        )
        self._fillIn = OnscreenImage(
            parent=self,
            image=fillIn,
            scale=fillInScale
        )
        self._fillInClipStart = -1 if fillInClipLeft else 1
        self._fillInClipBounds = fillInClipBounds
        self._fillInStartOffset = fillInStartOffset
        self._fillIn.setX(fillInStartOffset)
        # got this bit from MainMenuGui.SliderOption
        # might need to modify this a bit
        if noClip:
            self._clippingPlane = None
        else:
            self._clippingPlane = PlaneNode('TextureWaitBar-clipper')
            self._clippingPlane.setPlane(Plane(Vec3(self._fillInClipStart, 0, 0),
                                               Point3(self._fillInClipBounds[1] if fillInClipLeft else
                                                      self._fillInClipBounds[0], 0, 0)))
            clipNP = self._fillIn.attachNewNode(self._clippingPlane)
            self._fillIn.setClipPlane(clipNP)
        # set up the initial bar
        self._onChange()

    # Helper functions

    def _onChange(self):
        if self._clippingPlane:
            def lerp(x, y, lerpAmount):
                """
                Returns a float linearly interpolated from 0 to 1
                For lerpAmount, 0 = x and 1 = y. 0.5 would be the midpoint.
                """
                # Le borrowed this from MainMenuGui.SliderOption
                return x - lerpAmount * (x - y)

            val = self.value / self._range
            # err, determine if this bit works if -1 is ever needed I guess
            # can't be bothered to maths, and don't have a current use case to test this out rn
            lerpAmt = lerp(self._fillInClipBounds[0], self._fillInClipBounds[1], val)
            startX = lerp(self._fillInClipBounds[1] - self._fillInStartOffset, self._fillInStartOffset, val)

            self._clippingPlane.setPlane(Plane(Vec3(self._fillInClipStart, 0, 0),
                                               Point3(lerpAmt, 0, 0)))
            self.notify.debug(f"value/range={val}, lerpAmt={lerpAmt}, startX={startX}")
            self._fillIn.setX(startX)

    # properties

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        if not isinstance(val, (int, float)):
            raise TypeError('Value must be an integer or float!')
        # make sure val is in range of 0 and 100
        val = max(val, 0)
        val = min(val, self._range)
        # set the value
        self._value = val
        # update the bar
        self._onChange()
