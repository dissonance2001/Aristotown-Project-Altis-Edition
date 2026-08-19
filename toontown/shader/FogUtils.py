"""
FogUtils
Contains a few functions intended to be used by a Fog or ToontownFog object

@author: Loonatic
@date: 5/30/2022
"""

from toontown.shader.FogGlobals import *

# def zoneId2Fog(zoneId, name="Fog"):
#     """
#     Makes a new Fog object
#     """
#     # Assuming that our zoneId only has one type of fog, like for playgrounds or streets
#     fogattrs = zoneId2FogAttrs.get(zoneId)
#     if fogattrs is None:
#         return None
#     fog = Fog(name)
#     fog.setColor(fogattrs[0])
#     mode = fogattrs[1]
#     fog.setMode(mode)
#     if mode == Fog.M_linear:
#         fog.setLinearRange(fogattrs[3])
#     else:
#         fog.setExpDensity(fogattrs[3])
#     return fog

# def configFogAttrs(fog, fogattr):
#     """
#     Modifies a given Fog object
#     """
#     if fogattr is None:
#         return None
#     fog.setColor(fogattr[0])
#     mode = fogattr[1]
#     fog.setMode(mode)
#     if mode == Fog.M_linear:
#         fog.setLinearRange(fogattr[2][0], fogattr[2][1])
#     else:
#         fog.setExpDensity(fogattr[2])
#     return fog
#


def applyFog(fogNode, childNodes = None):
    """
    Apply a given fog to a list of nodepaths, clearing any pre-existing fog if any.

    :param Fog fogNode: Configured Fog node.
    :param list childNodes: list of child nodepaths fog will be applied to
    """
    if not WANT_FOG:
        return
    if not childNodes:
        childNodes = [render]
    for node in childNodes:
        if not node.isEmpty():
            # First let's clean out any leftover attached fog
            node.clearFog()
            node.setFog(fogNode)

def removeFog(childNodes = None):
    """
    Removes the Fog attribute from a list of nodes.
    :param list childNodes: list of child nodepaths fog will be removed
    """
    # Don't check for WANT_FOG if we're removing fog, since we don't want it anyway.
    if not childNodes:
        childNodes = [render]
    for node in childNodes:
        if not node.isEmpty():
            node.clearFog()

def cleanupFog(childNodes):
    """
    Removes nodes from the list that don't have any fog applied.
    Good for re-syncing if things get desynced from ToontownFog.

    :param list childNodes: list of child nodepaths that will be checked & possibly removed
    :return: Updated childNodes list
    """
    for node in childNodes:
        if node.getFog() is None:
            childNodes.remove(node)
    return childNodes

def addFogDensity(fog, change):
    """
    Changes the fog density by the amount passed into it. Only applies for fog modes 1 and 2.
    """
    # The min() statement makes sure the density is never over 1
    # The max() statement makes sure the density is never below 0
    fog.setExpDensity(
        min(1, max(0, fog.getExpDensity() + change))
    )

