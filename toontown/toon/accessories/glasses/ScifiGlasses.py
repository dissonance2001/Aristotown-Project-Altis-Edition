from math import pow
from panda3d.core import Vec4
from toontown.toon.accessories.glasses.GlassesHideLashes import GlassesHideLashes


class ScifiGlasses(GlassesHideLashes):
    """
    The Scifi Glasses. Modifies certain nodes' colorscales to be Toon-colored.
    Also hides the eyes.
    """

    def fixupAccessoryGeom(self):
        # Determine what color to set the visor lights to.
        # We're taking the toon's head color, and raising each RGBA value
        # to the power of 0.75. This brings each value to be a little bit
        # closer to 1.0, so everything is a little bit brighter in a good,
        # non-linear way.
        lightColor = list(map(lambda x: pow(x, 0.75), self.toon.style.headColor))
        visorColor = lightColor

        # Find the nodes to set the color of.
        lightNode = self.accessoryGeom.find('**/lights')
        visorNode = self.accessoryGeom.find('**/glass')

        # Set these nodes to be the colors we have in mind for em.
        lightNode.setColorScale(Vec4(*lightColor))
        visorNode.setColorScale(Vec4(*visorColor))
