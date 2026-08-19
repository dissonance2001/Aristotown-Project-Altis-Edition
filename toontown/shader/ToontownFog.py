"""
ToontownFog
@author: Loonatic
@date: 5/30/2022

Wrapper module for Panda's Fog with a few convenience adjustments to make fog easier to manage.
This should be used over Panda's actual fog module.

ToontownFog is automatically instantiated in Street, Playground, and CogHQLoader.
By default, it tries to find fog attributes a la zoneId (FogGlobals) and tries to apply it to the ToontownFog object

"""
# possible problem: attaching fog A to node, then attaching fog B to node
# node is still in fog A's attachedNodes set even though it was removed
# this is not too much of a direct issue with removeFog since itll clear either way

from panda3d.core import Fog, NodePath, NodePathCollection
from toontown.shader.FogGlobals import WANT_FOG


class ToontownFog(Fog):
    def __init__(self, fogattr, name = "Toontown_Fog"):
        # Just in case our fogattr is None, we want to ensure whether we're really configured before applying.
        self.created = False
        super(ToontownFog, self).__init__(name=name)
        self.makeFog(fogattr)
        self.attachedNodes = set()

    def makeFog(self, fogattr):
        """
        Configures the color, mode, and attributes of the fog.
        Can be called after init.

        :param list[Vec4 | Vec3, int, set] fogattr: Required fog attributes. Refer to FogGlobals for presets.
        """
        if fogattr is None:
            # We already made our generic fog node
            return
        self.setColor(fogattr[0])
        mode = fogattr[1]
        self.setMode(mode)
        if mode == Fog.M_linear:
            self.setLinearRange(fogattr[2][0], fogattr[2][1])
            # todo: add if fogattr[3] is not None then adjust linearFallback with fogattr[3] values
        else:  # M_Exponential or M_ExponentialSquared
            self.setExpDensity(fogattr[2])
        self.created = True

    def attachFog(self, childNodes = None):
        """
        Apply this fog to a list of nodepaths, clearing any pre-existing fog if any.

        :param list childNodes: list of child nodepaths fog will be applied to
        """
        if not WANT_FOG or not self.created:
            return
        if not childNodes:
            childNodes = [render]
        if type(childNodes) is NodePath:
            childNodes = [childNodes]
        for node in childNodes:
            if not node.isEmpty() and node is not None:
                node.clearFog()
                node.setFog(self)
                self.attachedNodes.add(node)

    def detachFog(self, childNodes):
        """
        Remove this fog from a list of nodepaths, removing them out of the attachNodes set as well.

        :param list childNodes: list of child nodepaths that fog will be detached from.
        """
        if type(childNodes) is NodePath:
            childNodes = [childNodes]
        for node in childNodes:
            if not node.isEmpty() and node is not None:
                node.clearFog()
                self.attachedNodes.discard(node)

    def removeFog(self):
        """
        Resets the fog.
        Removes the fog from all attached nodes & remove them from the attachedNodes set.
        """
        for node in self.attachedNodes:
            if not node.isEmpty() and node is not None:
                node.clearFog()
        self.attachedNodes = set()
        self.created = False

