from panda3d.core import *
from direct.interval.IntervalGlobal import *
from direct.gui.DirectGui import *

from toontown.gui.ScaledFrame import ScaledFrame
from toontown.gui.TTGui import kwargsToOptionDefs
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownGlobals
from direct.task.Task import Task
from toontown.toon import NPCToons
from toontown.toon.gui import ToonTipGlobals, GuiBinGlobals
from toontown.toon import ToonHead
from toontown.menu import MainMenuGui
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory

TTL = TTLocalizer


@DirectNotifyCategory()
class ToonTipPanel(DirectFrame):
    startPos = (-1.4, 0, 0.435)
    # 0.617 x
    endPos = (0.717, 0, 0.435)
    tipOutFor = 10
    quickCloseTime = 0.4
    normalCloseTime = 1.0
    NPCHeadDim = 0.53575
    xSize = 0.64
    zSize = 0.15
    normalFrameSize = (-xSize, xSize, -zSize, zSize)
    smallFrameSize = (-0.60, -0.40, -0.10, 0.10)

    def __init__(self, parent=aspect2d, clipInterior=True, **kwargs):
        optiondefs = (
            ('relief', None, None),
        )
        self.defineoptions(kwargs, optiondefs)
        DirectFrame.__init__(self, parent)
        self.initialiseoptions(ToonTipPanel)
        self.setBin('sorted-gui-popup', GuiBinGlobals.ToonTipBin)
        # This is set to 50 so that it is still clickable under some circumstances with certain GUI elements.
        self.activeTip = None
        self.npcHead = None
        tipsGui = loader.loadModel('phase_3/models/gui/ttcc_tips')
        self.exclamationPoint = tipsGui.find('**/tipExclaim')
        tipsGui.removeNode()
        gui = loader.loadModel('phase_3/models/gui/tt_m_gui_mat_mainGui')

        self.tipFrame = ScaledFrame(
            parent=self,
            sortOrder=DGG.FADE_SORT_INDEX + 5,
            scaledTexture='phase_3/maps/gui/ttcc_gui_scaledFrame_toonTips.png',
            frameSize=self.normalFrameSize,
            borderScale=0.04,
            # image_scale=(1.485, 1.0, 0.735),
            # image=self.bgImage,
            image_pos=(0.0, 0.0, 0.025),
            # scale=(1.0, 1.0, 0.5),
            relief=None,
            text=''
        )
        self.excFrame = DirectFrame(
            parent=self.tipFrame,
            sortOrder=DGG.FADE_SORT_INDEX + 10,
            pos=(-0.495, 0.5, 0.02),
            image=self.exclamationPoint,
            scale=(0.2, 1.0, 0.2),
            relief=None
        )
        self.frameText = DirectLabel(
            parent=self.tipFrame,
            sortOrder=DGG.FADE_SORT_INDEX + 10,
            pos=(-0.37, 0.5, 0.05),
            scale=(0.05, 1.0, 0.05),
            text='',
            text_wordwrap=20.0,
            text_align=TextNode.ALeft,
            relief=None,
            textMayChange=1
        )
        self.frameTitle = DirectLabel(
            parent=self.tipFrame,
            sortOrder=DGG.FADE_SORT_INDEX + 10,
            pos=(0.115, 0.5, 0.11),
            scale=(0.08, 1.0, 0.08),
            text_font=ToontownGlobals.getSignFont(),
            text='',
            text_fg=(0.0, 0.55, 1.0, 1.0),
            relief=None,
            text_align=TextNode.ACenter
        )
        gui.removeNode()
        self.excFrame.setTransparency(1)
        self.tipFrame.setTransparency(1)
        if clipInterior:
            for guiPiece in (self.frameTitle, self.frameText):
                self.tipFrame.clipWithinFrame(guiPiece)

    def updateTip(self, num):
        attributes = ToonTipGlobals.ToonTipAttributes.get(num, None)
        if attributes:
            self.frameTitle['text_align'] = TextNode.ACenter
            self.frameText['text_align'] = TextNode.ALeft
            npc = attributes[2]
            if npc:
                self.createNpcToonHead(npc, self.NPCHeadDim)
                self.frameTitle['text'] = TTLocalizer.NPCToonNames[npc]
            else:
                self.destroyNpcToonHead()
                self.excFrame.show()
                self.frameTitle['text'] = TTLocalizer.ToonTipPanelTips[num][0]
            self.frameText['text'] = TTLocalizer.ToonTipPanelTips[num][1].format(
                primary=base.PRIMARY_KEY.upper(), secondary=base.SECONDARY_KEY.upper(), jump=base.JUMP.upper()
            )
            self.activeTip = num
        else:
            self.notify.debug('ToonTipPanel: Invalid Tip ID was sent. Num: %s' % num)

    def setSizeMode(self, open=True):
        frameSize = self.normalFrameSize if open else self.smallFrameSize
        self.tipFrame['frameSize'] = frameSize

    def lerpFrameSize(self, value):
        l = lerp(self.normalFrameSize[0], self.smallFrameSize[0], value)
        r = lerp(self.normalFrameSize[1], self.smallFrameSize[1], value)
        d = lerp(self.normalFrameSize[2], self.smallFrameSize[2], value)
        u = lerp(self.normalFrameSize[3], self.smallFrameSize[3], value)
        self.tipFrame['frameSize'] = (l, r, d, u)

    def getTransitionSeq(self, duration=0.5, toOpen=True):
        startSize = self.smallFrameSize if toOpen else self.normalFrameSize
        goalSize = self.normalFrameSize if toOpen else self.smallFrameSize

        def popinScale(t, side):
            if side == 0:
                delta_a = 0
                delta_b = t
            else:
                delta_a = t
                delta_b = 1

            horizDelta = delta_a if toOpen else delta_b
            vertDelta = delta_b if toOpen else delta_a
            l = lerp(startSize[0], goalSize[0], horizDelta)
            r = lerp(startSize[1], goalSize[1], horizDelta)
            d = lerp(startSize[2], goalSize[2], vertDelta)
            u = lerp(startSize[3], goalSize[3], vertDelta)

            self.tipFrame['frameSize'] = (l, r, d, u)

        seq = Sequence(
            LerpFunctionInterval(popinScale, duration=duration / 2, blendType='easeIn',
                                 fromData=0.0, toData=1.0, extraArgs=[0]),
            LerpFunctionInterval(popinScale, duration=duration / 2, blendType='easeIn',
                                 fromData=0.0, toData=1.0, extraArgs=[1]),
        )

        return seq

    def resetTipPanel(self):
        self.frameText['text'] = ''

    def destroyNpcToonHead(self):
        if self.npcHead:
            self.npcHead.detachNode()
            self.npcHead.delete()
            self.npcHead = None

    def createNpcToonHead(self, NPCID, dimension = 0.5):
        self.destroyNpcToonHead()
        npcToon = NPCToons.NPCToonDict.get(NPCID)
        head = ToonHead.ToonHead()
        head.setupHead(npcToon.getToonDNA(), forGui = 1)
        self.fitGeometry(head, fFlip = 1, dimension = dimension)
        self.npcHead = head
        self.npcHead.reparentTo(self.tipFrame)
        self.npcHead.setPos(-0.5, 0.5, 0.02)
        self.npcHead.setScale(0.4, 1.0, 0.38)
        self.excFrame.hide()

    def fitGeometry(self, geom, fFlip = 0, dimension = 0.5):
        p1 = Point3()
        p2 = Point3()
        geom.calcTightBounds(p1, p2)
        if fFlip:
            t = p1[0]
            p1.setX(-p2[0])
            p2.setX(-t)
        d = p2 - p1
        biggest = max(d[0], d[2])
        s = dimension / biggest
        mid = (p1 + d / 2.0) * s
        geomXform = hidden.attachNewNode('geomXform')
        for child in geom.getChildren():
            child.reparentTo(geomXform)

        geomXform.setPosHprScale(-mid[0], -mid[1] + 1, -mid[2], 180, 0, 0, s, s, s)
        geomXform.reparentTo(geom)

    def cleanup(self):
        self.resetTipPanel()
        self.excFrame.destroy()
        self.frameText.destroy()
        self.frameTitle.destroy()
        self.tipFrame.destroy()
        self.destroyNpcToonHead()
        self.tipFrame = None
        self.excFrame = None
        self.frameTitle = None
        self.frameText = None
        super().destroy()


@DirectNotifyCategory()
class ToonTipsSeenPanel(ScaledFrame):
    NPCHeadDim = 0.53575
    tipsWanted = 4
    startPosZ = 0.255
    startPosX = -0.09
    zPerIndex = -0.27
    tipScale = 0.69
    catButtonPos = (
        (-0.45, 0, 0.475),
        (-0.15, 0, 0.475),
        (0.15, 0, 0.475),
        (0.45, 0, 0.475)
    )
    doneEvent = 'ToonTipsSeenPanelDone'
    tipsGui = loader.loadModel('phase_3/models/gui/ttcc_tips')
    exclamationPoint = tipsGui.find('**/tipExclaim')
    bgImage = tipsGui.find('**/tipPanel')
    tipsGui.removeNode()
    attributes = ToonTipGlobals.ToonTipAttributes

    def __init__(self, toon):
        ScaledFrame.__init__(
            self,
            parent=aspect2d,
            pos=(0, 0, -0.05),
            relief=None,
            frameSize=(-0.6, 0.6, -0.663, 0.663),
            scaledTexture='phase_3/maps/gui/ttcc_gui_scaledFrame_toonTips.png',
            text=TTL.TTPSeenTipsTitle,
            textMayChange=1,
            text_scale=0.1,
            text_pos=(0, 0.575),
            sortOrder=DGG.NO_FADE_SORT_INDEX
        )
        self.initialiseoptions(ToonTipsSeenPanel)
        self['shadowStrength'] = 0.04
        self.setBin('sorted-gui-popup', GuiBinGlobals.TTDialogBin)
        self.setTransparency(1)
        self.tips = []
        self.tipCategory = 0
        self.tipIndex = 0
        self.isLoaded = 0
        self.isEntered = 0
        self.categoryButtons = []
        self.toon = toon
        # Get the toon's toontip history in order of newest to oldest.
        self.seenTips = self.toon.toonTipsSeen[::-1]
        self.activeTipsList = []
        self.notify.setInfo(True)

    def unload(self):
        if self.isLoaded == 0:
            return
        self.isLoaded = 0
        self.exit()
        for tip in self.tips:
            tip.destroy()
        for button in self.categoryButtons:
            button.destroy()
        self.categoryButtons = None
        self.tips = None
        self.seenTips = None
        self.activeTipsList = None
        ScaledFrame.destroy(self)

    def load(self):
        if self.isLoaded == 1:
            return
        self.isLoaded = 1
        gui = loader.loadModel('phase_3/models/gui/tt_m_gui_mat_mainGui')
        arrowGui = loader.loadModel('phase_4/models/gui/itemsPage')
        guiCancelUp = gui.find('**/tt_t_gui_mat_closeUp')
        guiCancelDown = gui.find('**/tt_t_gui_mat_closeDown')
        guiArrowUp = arrowGui.find('**/arrow')
        guiArrowDown = arrowGui.find('**/arrowHover')
        self.cancel = DirectButton(
            parent=self,
            relief=None,
            image_scale=(0.345),
            image=(
                guiCancelUp,
                guiCancelDown,
                guiCancelUp,
                guiCancelDown
            ),
            pos=(0.5725, 0, 0.635),
            command=self.__cancel
        )
        self.upArrow = DirectButton(
            parent=self,
            relief=None,
            image=(
                guiArrowUp,
                guiArrowDown,
                guiArrowDown,
                guiArrowUp
            ),
            image_hpr=(0, 0, 270), image_scale = 0.15,
            command=self.scrollUp,
            pos=(0.50, 0, -0.041)
        )
        self.downArrow = DirectButton(
            parent=self,
            relief=None,
            image=(
                guiArrowUp,
                guiArrowDown,
                guiArrowDown,
                guiArrowUp
            ),
            image_hpr=(0, 0, 90),
            image_scale=0.15,
            command=self.scrollDown,
            pos=(0.50, 0, -0.226)
        )
        gui.removeNode()
        arrowGui.removeNode()
        self.createCategoryButtons()
        self.updateActiveCategory(ToonTipGlobals.CATEGORY_GEN)
        self.accept('updateTipsHistory', self.updateHistory)
        for element in (self.upArrow, self.downArrow, *self.categoryButtons):
            self.clipWithinFrame(element)
        self.hide()

    def enter(self):
        if self.isEntered == 1:
            return None
        self.isEntered = 1
        if self.isLoaded == 0:
            self.load()
        base.transitions.fadeScreen(0.5)
        self.updateActiveCategory(ToonTipGlobals.CATEGORY_GEN)
        self.show()

    def exit(self):
        if self.isEntered == 0:
            return None
        self.isEntered = 0
        base.transitions.noTransitions()
        self.ignoreAll()
        self.hide()
        messenger.send(self.doneEvent, [])

    def updateHistory(self):
        self.seenTips = self.toon.toonTipsSeen[::-1]

    def createCategoryButtons(self):
        gui = loader.loadModel("phase_3/models/gui/ttcc_menu_buttons")
        scale = 0.8
        for i in range(len(ToonTipGlobals.ToonTipCategories)):
            pos = self.catButtonPos[i]
            button = MainMenuGui.MainMenuButton(
                parent = self,
                pos = pos,
                text = TTL.ToonTipCategories[i],
                scale = scale,
                command = self.updateActiveCategory,
                extraArgs = [i]
            )
            button.bind(DGG.ENTER, MainMenuGui.hoverButton, [button, scale * 1.1])
            button.bind(DGG.EXIT, MainMenuGui.hoverButton, [button, scale])
            self.categoryButtons.append(button)
        gui.removeNode()

    def updateActiveCategory(self, category):
        for button in self.categoryButtons:
            button['state'] = DGG.NORMAL
        self.tipCategory = category
        self.tipIndex = 0
        self.updateActiveTipList(category)
        self.loadInitialTips()
        self.categoryButtons[category]['state'] = DGG.DISABLED
        self.checkDisableArrows()
        messenger.send('wakeup')

    def updateActiveTipList(self, category):
        # Update the currently used active tips for the given category.
        if self.activeTipsList:
            self.activeTipsList = []
        for i in range(len(self.seenTips)):
            tipId = self.seenTips[i]
            # Only load the tips that are set to be shown in the book.
            wantShow = self.attributes[tipId][1]
            if not wantShow:
                continue
            if category == self.attributes[tipId][3]:
                self.activeTipsList.append(tipId)

    def loadInitialTips(self):
        # If there are any current tips, get rid of them.
        if self.tips:
            for tip in self.tips:
                tip.destroy()
            self.tips = []
        # Load as many toon tips as possible up to the defined maximum.
        if len(self.activeTipsList):
            for i in range(len(self.activeTipsList)):
                if i >= self.tipsWanted:
                    break
                tipId = self.activeTipsList[i]
                self.createNewTip(tipId, i)
        else:
            # Load a dummy tip telling players that they haven't found any toon tips.
            # This tip should never be sent to the client in normal circumstances.
            self.createNewTip(0, 0)

    def createNewTip(self, tipId, num):
        tip = ToonTipPanel(parent=self, scale=self.tipScale)
        tip.setBin('sorted-gui-popup', GuiBinGlobals.TTDialogBin + 1)
        tip.updateTip(tipId)
        pos = (self.startPosX, 0, self.startPosZ + num * self.zPerIndex)
        tip.setPos(pos)

        self.tips.append(tip)

    def scrollUp(self):
        if len(self.activeTipsList) <= self.tipsWanted:
            return
        index = self.tipIndex - 1
        if index <= 0:
            index = 0
        self.updateTipIndex(index)
        self.checkDisableArrows()
        messenger.send('wakeup')

    def scrollDown(self):
        if len(self.activeTipsList) <= self.tipsWanted:
            return
        index = self.tipIndex + 1
        if index >= len(self.activeTipsList) - self.tipsWanted:
            index = len(self.activeTipsList) - self.tipsWanted
        self.updateTipIndex(index)
        self.checkDisableArrows()
        messenger.send('wakeup')

    def checkDisableArrows(self):
        if self.tipIndex == 0:
            self.upArrow['state'] = DGG.DISABLED
            self.upArrow.setColor(0.55, 0.55, 0.55, 1.0)
        else:
            self.upArrow['state'] = DGG.NORMAL
            self.upArrow.setColor(1.0, 1.0, 1.0, 1.0)
        if len(self.activeTipsList) - self.tipIndex <= self.tipsWanted:
            self.downArrow['state'] = DGG.DISABLED
            self.downArrow.setColor(0.55, 0.55, 0.55, 1.0)
        else:
            self.downArrow['state'] = DGG.NORMAL
            self.downArrow.setColor(1.0, 1.0, 1.0, 1.0)

    def updateTipIndex(self, index):
        self.tipIndex = index
        self.updateTipTexts()

    def updateTipTexts(self):
        for tip in self.tips:
            localIndex = self.activeTipsList[self.tips.index(tip) + self.tipIndex]
            tip.updateTip(localIndex)

    def __cancel(self):
        self.exit()
