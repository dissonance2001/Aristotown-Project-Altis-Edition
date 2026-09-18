from panda3d.core import *
from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectGui import *
from toontown.gui.hover.HoverFrame import HoverFrame
from toontown.gui.hover.HoverFrameTypes import HoverFrameTypes
from toontown.utils.DirectNotifyCategory import *

from typing import Any


@DirectNotifyCategory()
class HoverFrameManager(DirectObject):
    HoverFrameScale = 0.7

    def __init__(self) -> None:
        super().__init__()
        self.itemHover = HoverFrame(
            parent=aspect2d, pos=(0, 0, 0)
        )
        self.itemHover.hide()
        self.itemHover.setScale(0.7)
        self.__itemHoverTaskName = f'HoverFrameManager-HoverPlacement-{id(self)}'
        self.__hoveredFrame: DirectFrame | None = None
        self.__hoveredFrameOffset = None
        self.__hoveredItem = None

    def cleanup(self) -> None:
        self.removeAllTasks()
        self.itemHover.destroy()
        self.itemHover = None
        self.__hoveredFrame = None
        self.__hoveredFrameOffset = None
        self.__hoveredItem = None

    def hoverObject(self, frame: DirectFrame, item: Any, itemType: HoverFrameTypes, frameDir: str = 'left',
                    frameWidth: int = 0.475, descAlign=TextNode.ALeft, frameScale: float = 1.0,
                    fitToTextWidth: bool = False) -> None:
        if self.__hoveredFrame is not None:
            if self.__hoveredFrame is frame and self.__hoveredItem is item:
                return
            self.unhoverObject()
        self.__hoveredFrame = frame
        self.__hoveredItem = item
        self.itemHover.setScale(0.7*frameScale)
        self.itemHover.setHoverDataStyle(frameWidth, descAlign, fitToTextWidth=fitToTextWidth)
        self.itemHover.setItem(item, itemType)
        bounds = self.itemHover['frameSize']
        self.__hoveredFrameOffset = [frameScale * 0.8 * (-1.0 if frameDir == 'left' else 1.15) * (abs(bounds[0]) + abs(bounds[1])) / 2, 0, 0]
        self.addTask(self.__hoverTask, name=self.__itemHoverTaskName)

    def unhoverObject(self) -> None:
        self.itemHover.hide()
        self.removeTask(self.__itemHoverTaskName)
        self.__hoveredFrame = None
        self.__hoveredItem = None
        self.itemHover.setItem(None)

    def __hoverTask(self, task):
        if not self.__hoveredFrame:
            return task.cont
        if not base.mouseWatcherNode.hasMouse():
            return task.cont

        # Convert raw mouse coords (-1..1 on both axes) into aspect2d space,
        # where the horizontal range is actually -aspectRatio..aspectRatio,
        # not -1..1. Skipping the aspect-ratio multiply here is what made
        # the tooltip drift far to the left on wide (16:9) windows.
        mpos = base.mouseWatcherNode.getMouse()
        aspectRatio = base.getAspectRatio()
        mouseX = mpos.getX() * aspectRatio
        mouseZ = mpos.getY()

        zmin = -1.0 - (self.itemHover['frameSize'][2] * self.HoverFrameScale - 0.05)
        zmax = 1.0 + self.itemHover['frameSize'][2] * self.HoverFrameScale - 0.05
        mouseZ = max(zmin, min(zmax, mouseZ))

        newPos = Point3(mouseX + self.__hoveredFrameOffset[0], 0, mouseZ + self.__hoveredFrameOffset[2])
        self.itemHover.setPos(newPos)
        if self.itemHover.isHidden():
            self.itemHover.show()

        return task.cont
