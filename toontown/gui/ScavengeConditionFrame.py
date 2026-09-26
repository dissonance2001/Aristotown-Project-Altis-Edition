from panda3d.core import TextNode
from direct.gui import DirectGuiGlobals as DGG
from direct.gui.DirectGui import DirectFrame
from direct.interval.IntervalGlobal import Func, LerpFunctionInterval, Sequence, Wait

from toontown.gui.TilingScaledFrame import TilingScaledFrame
from toontown.gui.hover.HoverFrameTypes import HoverFrameTypes
from toontown.inventory.enums import RarityEnums
from toontown.toon.gui import GuiBinGlobals
from toontown.toonbase import ToontownGlobals
from toontown.utils import ColorHelper
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class ScavengeConditionFrame(DirectFrame):
    SLIDE_IN_SPEED = 0.27
    SLIDE_OUT_SPEED = 0.27

    def __init__(self, parent=None, obj=None, index=0, removeCallback=None, **kw):
        super().__init__(parent=parent, relief=None, pos=(0, 0, 0), **kw)
        self.obj = obj
        self.index = index
        self.removeCallback = removeCallback
        self.slideSeq = None
        self.destroyed = False

        rarityColor = RarityEnums.RarityColors[self.obj.getRarity()]
        patternColor = ColorHelper.lerpColor(rarityColor, (1, 1, 1, 1), 0.3)
        patternColor = (patternColor[0], patternColor[1], patternColor[2], 0.6)

        self.frame = TilingScaledFrame(
            parent=self,
            frameSize=(-1, 0, -0.20635, 0),
            borderScale=0.02662,
            frameBin=GuiBinGlobals.ConditionFrame,
            scaledTexture='phase_3/maps/gui/ttcc_gui_tiledFrame_generic_border.png',
            scaledColor=rarityColor,
            patternTexture='core/gui/maps/cc_t_gui_sframe_pat_testgrayscale.png',
            patternSpeed=(0.02, -0.02),
            patternScale=0.14,
        )
        self.frame.patternNode.setColorScale(patternColor)
        self.frame['state'] = DGG.NORMAL
        self.frame.bind(DGG.WITHIN, self.__mouseWithin)
        self.frame.bind(DGG.WITHOUT, self.__mouseWithout)

        self.iconHolder = self.frame.attachNewNode('scavenge-icon')
        self.icon = None
        try:
            self.icon = self.obj.getItemDefinition().getGuiItemModel(parent=self.iconHolder)
        except (AssertionError, OSError, KeyError, AttributeError):
            self.notify.warning(
                'Unable to create inventory popup icon for item type %s, subtype %s.' %
                (self.obj.getItemType(), self.obj.getItemSubtype())
            )

        if self.icon and not self.icon.isEmpty():
            self.icon.setScale(0.85)
            self.iconHolder.setPos(-0.10246, 0, 0)

        self.show()
        self.setX(self.getSlideDistance())

    def getSlideDistance(self):
        left, right, _, _ = self.frame.getDefinedBounds()
        return abs(right - left) * 1.1

    def __mouseWithin(self, _=None):
        hoverMgr = getattr(base, 'hoverMgr', None)
        if hoverMgr:
            hoverMgr.hoverObject(
                self.frame,
                item=self.obj,
                itemType=HoverFrameTypes.Scavenge,
                frameDir='right',
            )

    def __mouseWithout(self, _=None):
        hoverMgr = getattr(base, 'hoverMgr', None)
        if hoverMgr:
            hoverMgr.unhoverObject()

    def showPopup(self):
        if self.destroyed:
            return
        startX = self.getSlideDistance()

        def ival(t):
            self.setX(startX + (0 - startX) * t)

        self.slideSeq = Sequence(
            Wait(self.index * 0.12),
            LerpFunctionInterval(ival, duration=self.SLIDE_IN_SPEED, blendType='easeOut'),
        )
        self.slideSeq.start()

    def hidePopup(self):
        if self.destroyed:
            return
        if self.slideSeq:
            self.slideSeq.pause()
            self.slideSeq = None

        def ival(t):
            self.setX(0 + self.getSlideDistance() * t)

        self.slideSeq = Sequence(
            LerpFunctionInterval(ival, duration=self.SLIDE_OUT_SPEED, blendType='easeIn'),
            Func(self.destroy),
        )
        self.slideSeq.start()

    def destroy(self):
        if self.destroyed:
            return
        self.destroyed = True
        if self.slideSeq:
            self.slideSeq.pause()
            self.slideSeq = None
        hoverMgr = getattr(base, 'hoverMgr', None)
        if hoverMgr:
            hoverMgr.unhoverObject()
        if self.icon and not self.icon.isEmpty():
            try:
                self.obj.getItemDefinition().cleanupGuiItemModel(self.icon, self.obj)
            except Exception:
                self.icon.removeNode()
        self.ignoreAll()
        self.frame.destroy()
        DirectFrame.destroy(self)
