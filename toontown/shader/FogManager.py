"""
Underwhelming wrapper of Panda's Fog class. Used for internal development/testing to make things easier.

@author: Loonatic
"""
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory

"""
from panda3d.core import Fog
render.clearFog()
myFog = Fog("Fog Name")
myFog.setColor(0.05, 0.05, 0.05)
myFog.setExpDensity(0.01)
render.setFog(myFog)

https://docs.panda3d.org/1.10/python/programming/render-attributes/fog
https://docs.panda3d.org/1.10/python/reference/panda3d.core.Fog#panda3d.core.Fog

From reading the API page for the Fog class, it sounds as if beyond this opaque point there is no fog
(rather than continuing opaque fog up to the location of the fog node as you might expect):
"the fog will be rendered as if it extended along the vector from the onset point to the opaque point."
"""

from panda3d.core import Fog


@DirectNotifyCategory()
class FogManager:
    def __init__(self, name = "ActiveFog"):
        self.notify.debug(f"__init__(name = {name})")
        self.fog = None
        self.fogMode = None

        self.fog = Fog(name)
        self.fog.setColor(1, 1, 1)

        self.fogTypes = {
            0: Fog.MExponential,
            1: Fog.MExponentialSquared,
            2: Fog.MLinear
        }

    def setFog(self, np):
        np.setFog(self.fog)
        # np.attachNewNode(self.fog)

    def setColor(self, r, g, b):
        self.fog.setColor(r, g, b)

    def getColor(self):
        return self.fog.getColor()

    def clearFog(self):
        # todo: get child of self.fog (np) and clearFog
        # np.clearFog()
        return render.clearFog()

    def getFogMode(self):
        return self.fogMode

    def setFogMode(self, id):
        self.fog.setMode(self.fogTypes[id])
        self.fogMode = id

    """
    ## Exponential Fog ##
    
    Generally more useful than linear fog.
    """

    def setDensity(self, density):
        """
        Determines the density value used for exponential fog calculations.

        :param float density: Value between [0-1]
        """
        self.fog.setExpDensity(density)

    def getDensity(self):
        return self.fog.getExpDensity()

    """
    ## Linear Fog ##
    
    In linear mode, the onset and opaque distances of the fog are defined as offsets along the local forward (+Y)
    axis of the fog node.

    Commonly used in places like caves.
    """

    def setLinearRange(self, range, opacity):
        """
        Specifies the effects of the fog in linear distance units.
        This is only used if the mode is M_linear.

        This specifies a fog that begins at distance onset units from the origin,
        and becomes totally opaque at distance opaque units from the origin, along the forward axis (usually Y).

        This function also implicitly sets the mode the M_linear, if it is not already set.

        :type range: float
        :type opacity: float
        """
        self.fog.setLinearRange(range, opacity)

    def getLinearOnset(self):
        return self.fog.getLinearOnsetPoint()

    def getLinearOpacity(self):
        return self.fog.getLinearOpaquePoint()

    def setLinearFallback(self, angle, onset, opaque):
        """
        Defines how the fog should be rendered when the fog effect is diminished in this way.

        The linear fallback workaround will only look good in certain situations, for example when the fog is deep
        inside a dark cave.

        :param float angle: minimum viewing angle(angle between the camera direction and fog direction) at which the
                            fallback effect will be employed.
        :param float onset: camera-relative distance from the fog node at which the fog will begin to have effect
        :param float opaque: camera-relative distance from the fog node at which the fog will be completely opaque.
        """
        self.fog.setLinearFallback(angle, onset, opaque)

    def getLinearFallback(self):
        return self.fog.getLinearFallback()

    ## Extra
