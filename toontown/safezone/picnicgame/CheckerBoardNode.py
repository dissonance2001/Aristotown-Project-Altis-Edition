from typing import Optional

from panda3d.core import CollisionRay, CollisionNode, CollisionHandlerQueue, NodePath, CollisionSphere, Point3
from direct.interval.IntervalGlobal import *
from direct.showbase.DirectObject import DirectObject
from direct.showbase.MessengerGlobal import messenger

from toontown.safezone.picnicgame.BoardGameGlobals import BOARD_SIZE
from toontown.toonbase import ToontownGlobals


SQUARE_SIZE = 0.53
B_OFFSET = 1.85


def getBoardPosFromIndex(index: int) -> Point3:
    """
    Calculate the position of the given index relative to the board node.
    :param index:
    :return:
    """
    col = index // 8
    row = index - col * 8

    y = (SQUARE_SIZE * col + SQUARE_SIZE // 2) - B_OFFSET
    x = (SQUARE_SIZE * row + SQUARE_SIZE // 2) - B_OFFSET

    return Point3(x, y, 0.283)


class CheckerBoardNode(NodePath, DirectObject):

    def __init__(self, clickCallback: callable) -> None:
        super().__init__("CheckerBoard")

        self.clickCallback = clickCallback

        self.boardNode = base.loader.loadModel("phase_6/models/golf/regular_checker_game.bam")
        self.boardNode.reparentTo(self)

        self.locators = []

        for i in range(BOARD_SIZE):
            lc = NodePath(f"Locator-{i}")
            lc.reparentTo(self.boardNode)
            lc.setTag("PieceLocator", str(i))
            lc.setCollideMask(ToontownGlobals.PickerBitmask)
            lc.setPos(getBoardPosFromIndex(i))

            np = lc.attachNewNode(CollisionNode(f"picker{i}"))
            np.node().addSolid(CollisionSphere(0, 0, 0, .39))

            self.locators.append(lc)

        # Set up collisions for mouse picking.
        self.pickerRay = CollisionRay()
        self.pickerNode = CollisionNode('mouseRay')
        self.pickerNode.setFromCollideMask(ToontownGlobals.PickerBitmask)
        self.pickerNode.setIntoCollideMask(0)
        self.pickerNode.addSolid(self.pickerRay)
        self.pickerNP = base.camera.attachNewNode(self.pickerNode)

        self.cTravQueue = CollisionHandlerQueue()
        base.cTrav.addCollider(self.pickerNP, self.cTravQueue)

        self.__seq: Optional[Sequence] = None

    def cleanup(self) -> None:
        self.disableMouseCollisions()

        self.boardNode.removeNode()

        for locator in self.locators:
            locator.removeNode()

        self.locators = []

        self.removeNode()

    def enableMouseCollisions(self) -> None:
        """Enable the mouse collisions."""
        self.accept("mouse1", self.onMouseClick)

    def disableMouseCollisions(self) -> None:
        """Disable the mouse collisions."""
        self.ignore("mouse1")

    def onMouseClick(self) -> None:
        """
        If mouse collisions are enabled, this function will be called upon
        the mouse clicking one of the existing collisions.
        :return: None
        """
        messenger.send("wakeup")
        m_pos = base.mouseWatcherNode.getMouse()
        self.pickerRay.setFromLens(base.camNode, m_pos.getX(), m_pos.getY())

        base.cTrav.traverse(render)

        if not self.cTravQueue.getNumEntries():
            return

        self.cTravQueue.sortEntries()

        pickedNP = self.cTravQueue.getEntry(0).getIntoNodePath()
        pieceIndex = pickedNP.getNetTag("PieceLocator")

        if pieceIndex:
            self.clickCallback(int(pieceIndex))

    def popUpStart(self) -> None:
        boardScale = self.boardNode.getScale()

        self.__seq = Sequence(
            Func(self.boardNode.show),
            self.boardNode.scaleInterval(.5, boardScale * 1.1, startScale=0.01, blendType="easeIn"),
            self.boardNode.scaleInterval(.5, boardScale, blendType="easeIn")
        )
        self.__seq.start()

    def popUpStop(self) -> None:
        if self.__seq is not None:
            self.__seq.finish()
            self.__seq = None
