"""
A module containing several helper files for nodes.
"""
import math

from toontown.utils.ColorHelper import hexToPCol
from panda3d.core import *


def findHeadingBetweenNodes(startNode, endNode):
    """
    Calculates the heading between two nodes.
    Relative to render.
    """
    # Make a temp node.
    tempNode = render.attachNewNode('temp')

    # Line it up with the start node.
    tempNode.setPos(startNode.getPos(render))

    # Heads up!
    tempNode.headsUp(render, endNode.getPos(render))

    # Get our heading.
    h = tempNode.getHpr()[0]

    # Clean up the temp node.
    tempNode.removeNode()

    # Return heading.
    return h


class CrazyGeometricShapes(NodePath):

    def __init__(self, radius=1.0, segments=16, direction=(1, 0, 0)):
        NodePath.__init__(self, 'CrazyGeometricShapes')
        self.radius = radius
        self.segments = segments
        self.direction = direction
        self.clippingPlaneNPs = []
        self._createPlanes()

    def removeNode(self):
        super(CrazyGeometricShapes, self).removeNode()
        del self.radius
        del self.segments
        del self.direction
        del self.clippingPlaneNPs

    def setRadius(self, radius):
        self.radius = radius
        self._createPlanes()

    def setSegments(self, segments):
        self.segments = segments
        self._createPlanes()

    def setDirection(self, direction):
        self.direction = direction
        self._createPlanes()

    def attachNodeToPlanes(self, node):
        for np in self.clippingPlaneNPs:
            node.setClipPlane(np)

    def getClippingPlanes(self):
        return self.clippingPlaneNPs

    """
    Clipping Plane Building
    """

    def _createPlanes(self):
        # Cleanup first just in case.
        self._cleanupPlanes()

        # Then, start creating them based on parameters.
        for i in range(self.segments):
            # Calculate the position.
            degrees = 360 * (i / float(self.segments))

            # Make the clip plane.
            planeNode = PlaneNode('clippingPlane')
            planeNode.setPlane(Plane(Vec3(self.direction), (self.radius, 0, self.radius)))
            planeNP = self.attachNewNode(planeNode)
            planeNP.setP(degrees)
            planeNP.show()
            planeNP.setColorScale(1, 0, 0, 1)
            self.setClipPlane(planeNP)
            self.clippingPlaneNPs.append(planeNP)

    def _cleanupPlanes(self):
        for np in self.clippingPlaneNPs:
            np.removeNode()
        self.clippingPlaneNPs = []


class SemicircleClippingPlane(NodePath):
    """
    Creates a semicircle of clipping planes.
    A node can only have 8 active clipping planes.
    """

    maxPlanes = 8
    colors = (
        hexToPCol('FF0000'),
        hexToPCol('FFFF00'),
        hexToPCol('00FF00'),
    )

    def __init__(self, radius=100.0, segments=16, visible=False):
        NodePath.__init__(self, 'CircleClippingPlane')
        self.radius = radius
        self.segments = segments
        self.visible = visible
        self.clippingPlaneNPs = []
        self._createPlanes()

    def removeNode(self):
        super(SemicircleClippingPlane, self).removeNode()
        del self.radius
        del self.segments
        del self.clippingPlaneNPs

    def setRadius(self, radius):
        self.radius = radius
        self._createPlanes()

    def setSegments(self, segments):
        self.segments = segments
        self._createPlanes()

    def attachNodeToPlanes(self, node):
        for np in self.clippingPlaneNPs:
            node.setClipPlane(np)

    def getClippingPlanes(self):
        return self.clippingPlaneNPs

    """
    Clipping Plane Building
    """

    def _createPlanes(self):
        # Cleanup first just in case.
        self._cleanupPlanes()

        # Then, start creating them based on parameters.
        for i in range(min(self.segments, self.maxPlanes)):
            # Calculate the position.
            degrees = 360 * ((i + 0) / float(self.segments))
            radians = (degrees / 180.0) * math.pi
            xpos = math.sin(radians) * self.radius
            zpos = -math.cos(radians) * self.radius

            # Make the clip plane.
            planeNode = PlaneNode('clippingPlane')
            planeNode.setPlane(Plane(Vec3(0, 0, 1), Vec3(0, 0, 0)))
            planeNP = self.attachNewNode(planeNode)
            planeNP.setPos(xpos, 0, zpos)
            planeNP.setHpr(0, 0, -degrees)
            if self.visible:
                planeNP.show()
            planeNP.setColorScale(self.colors[i % len(self.colors)])
            self.setClipPlane(planeNP)
            self.clippingPlaneNPs.append(planeNP)

    def _cleanupPlanes(self):
        for np in self.clippingPlaneNPs:
            np.removeNode()
        self.clippingPlaneNPs = []


def makeClippingPlane(parent,
                      direction,
                      offset=(0, 0, 0),
                      visible=False):
    cplane = PlaneNode('clippingPlane')
    cplane.setPlane(Plane(Vec3(*direction), Point3(*offset)))
    clipNP = parent.attachNewNode(cplane)
    if visible:
        clipNP.show()
    return clipNP