import math

from panda3d.core import *
from toontown.level import BasicEntities
from toontown.level.editor import EditorGlobals


class TextEntity(BasicEntities.NodePathEntity):
    """
    TextEntity(BasicEntities.NodePathEntity)

    A simple TextNode entity, usable for making text objects
    or for building signs.
    """

    def __init__(self, level, entId):
        BasicEntities.NodePathEntity.__init__(self, level, entId)
        self.np = None
        self.initText()

    def destroy(self):
        self.destroyText()
        BasicEntities.NodePathEntity.destroy(self)

    def initText(self):
        x = 0
        textNodes = []
        try:
            font = loader.loadFont(self.font)  # TODO: Cache fonts? Might already do this.
        except:
            self.notify.warning(f'Invalid font path: {self.font}. Please try again.')
            font = loader.loadFont('phase_3/fonts/Humanist.ttf')
        for i in range(len(self.text)):
            # Create text, letter by letter
            textNode = TextNode("text")
            textNode.setText(self.text[i])
            textNode.setFont(font)
            textNode.setTextColor(self.color)
            textNode.setSmallCaps(self.smallCaps)

            if self.dropShadow:
                self.notify.warning("WARNING! Drop shadows are experimental! They will only work with Vec4(1, 1, 1, 1) font color.")
                textNode.setShadow(0.05, 0.05)
                textNode.setShadowColor(0, 0, 0, 1)

            # Create a NP for the letter to attach to
            np = NodePath(textNode.generate())
            np.setDepthWrite(0)

            # Stumble
            if i % 2:
                np.setPos(x + self.stumble, 0, self.stomp)
                np.setR(-self.wiggle)
            else:
                np.setPos(x - self.stumble, 0, self.stomp)
                np.setR(self.wiggle)

            x += textNode.getWidth() * np.getSx() + self.kern
            textNodes.append(np)

        for i in textNodes:
            i.setX(i.getX() - x / 2.0)

        if self.width and self.height:
            for node in textNodes:
                A = (node.getX() / (self.height / 2.0))
                B = (self.indent * math.pi / 180.0)

                theta = A + B
                d = node.getY()
                x = math.sin(theta) * (self.height / 2.0)
                y = (math.cos(theta) - 1) * (self.height / 2.0)
                radius = math.hypot(x, y)

                if radius != 0:
                    j = (radius + d) / radius
                    x *= j
                    y *= j
                node.setPos(x, 0, y)
                node.setR(node, (theta * 180.0) / math.pi)

        _np = self.attachNewNode('textNodeFinal')

        for node in textNodes:
            node.reparentTo(_np)

        _np.setDepthOffset(50)
        _np.flattenStrong()
        self.np = _np

    def destroyText(self):
        if self.np:
            self.np.removeNode()
            self.np = None


    if EditorGlobals.wantLevelEditor():
        def attribChanged(self, attrib, value):
            """
            :param attrib:
            :param value:
            """
            self.destroyText()
            self.initText()

