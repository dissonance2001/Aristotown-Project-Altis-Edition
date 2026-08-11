from direct.gui.DirectGui import *
from panda3d.core import *
from panda3d.direct import *
from toontown.toonbase.ToontownBattleGlobals import *
from toontown.toon import InventoryBase
from toontown.toonbase import TTLocalizer
from toontown.toon import IOURegistry
from toontown.battle import BattleGlobals
from toontown.quest import BlinkingArrows
from direct.interval.IntervalGlobal import *
from toontown.battle.BattleBase import HEAL
from panda3d.core import TextureStage, CardMaker
from direct.interval.IntervalGlobal import *
from direct.directnotify import DirectNotifyGlobal
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import ToontownBattleGlobals
from otp.otpbase import OTPGlobals
from toontown.toontowngui import TTDialog

# Corporate Clash inventory reward text colours.
_rewardTextPropertiesManager = TextPropertiesManager.getGlobalPtr()
_deepBlueRewardText = TextProperties()
_deepBlueRewardText.setTextColor(0, 0, 0.25, 1)
_rewardTextPropertiesManager.setProperties('deepBlue', _deepBlueRewardText)
_deepRedRewardText = TextProperties()
_deepRedRewardText.setTextColor(0.45, 0, 0, 1)
_rewardTextPropertiesManager.setProperties('deepRed', _deepRedRewardText)

DISPLAY_CONTENT_SYNC_ORDERS = {
    'contentSync1': [DROP_TRACK, SQUIRT_TRACK, ZAP_TRACK, TRAP_TRACK, THROW_TRACK, LURE_TRACK, SOUND_TRACK, HEAL_TRACK],
    'contentSync2': [SOUND_TRACK, DROP_TRACK, SQUIRT_TRACK, HEAL_TRACK, ZAP_TRACK, TRAP_TRACK, LURE_TRACK, THROW_TRACK],
    'contentSync3': [SQUIRT_TRACK, SOUND_TRACK, HEAL_TRACK, TRAP_TRACK, THROW_TRACK, ZAP_TRACK, LURE_TRACK, DROP_TRACK],
    'contentSync4': [SQUIRT_TRACK, TRAP_TRACK, LURE_TRACK, DROP_TRACK, HEAL_TRACK, ZAP_TRACK, SOUND_TRACK, THROW_TRACK],
    'contentSync5': [THROW_TRACK, SOUND_TRACK, DROP_TRACK, TRAP_TRACK, SQUIRT_TRACK, HEAL_TRACK, LURE_TRACK, ZAP_TRACK],
    'contentSync6': [THROW_TRACK, SQUIRT_TRACK, ZAP_TRACK, SOUND_TRACK, TRAP_TRACK, LURE_TRACK, DROP_TRACK, HEAL_TRACK],
    'contentSync7': [TRAP_TRACK, DROP_TRACK, SQUIRT_TRACK, SOUND_TRACK, THROW_TRACK, ZAP_TRACK, LURE_TRACK, HEAL_TRACK],
    'contentSync8': [TRAP_TRACK, SQUIRT_TRACK, DROP_TRACK, THROW_TRACK, ZAP_TRACK, LURE_TRACK, HEAL_TRACK, SOUND_TRACK],
}

class InventoryNewOLD(InventoryBase.InventoryBase, DirectFrame):
    notify = DirectNotifyGlobal.directNotify.newCategory('InventoryNew')
    PressableTextColor = Vec4(1, 1, 1, 1)
    PressableGeomColor = Vec4(1, 1, 1, 1)
    PressableImageColor = Vec4(0, 0.6, 1, 1)
    PressableOrganicColor = Vec4(0, .2, .9, 1)
    PropBonusPressableImageColor = Vec4(0, 0.9, 1, 1)
    NoncreditPressableImageColor = Vec4(0.3, 0.6, 0.6, 1)
    PropBonusNoncreditPressableImageColor = Vec4(0, 0.196, 1, 1)
    DeletePressableImageColor = Vec4(0.7, 0.1, 0.1, 1)
    UnpressableTextColor = Vec4(1, 1, 1, 0.3)
    UnpressableGeomColor = Vec4(1, 1, 1, 0.3)
    UnpressableImageColor = Vec4(0.3, 0.3, 0.3, 0.8)
    BookUnpressableTextColor = Vec4(1, 1, 1, 1)
    BookUnpressableGeomColor = Vec4(1, 1, 1, 1)
    BookUnpressableImage0Color = Vec4(0, 0.6, 1, 1)
    BookUnpressableImage2Color = Vec4(0.1, 0.7, 1, 1)
    ShadowColor = Vec4(0, 0, 0, 0)
    ShadowBuffedColor = Vec4(1, 1, 1, 1)
    UnpressableShadowBuffedColor = Vec4(1, 1, 1, 0.3)
    TrackYOffset = 0.095
    TrackYSpacing = -0.13
    ButtonXOffset = -0.411
    ButtonXSpacing = 0.178

    def __init__(self, toon, invStr = None, ShowSuperGags = 1):
        InventoryBase.InventoryBase.__init__(self, toon, invStr)
        DirectFrame.__init__(self, relief=None)
        self.initialiseoptions(InventoryNewOLD)
        self.battleCreditLevel = None
        self.detailCredit = None
        self.__battleCreditMultiplier = 1
        self.__invasionCreditMultiplier = 1
        self.__respectInvasions = 1
        self.interactivePropTrackBonus = -1
        self.tutorialFlag = 0
        self.gagTutMode = 0
        self.showSuperGags = ShowSuperGags
        self.clickSuperGags = 1
        self.propAndOrganicBonusStack = config.GetBool('prop-and-organic-bonus-stack', 0)
        self.propBonusIval = Parallel()
        self.activateMode = 'book'
        self.load()
        self.hide()
        return

    def setBattleCreditMultiplier(self, mult):
        self.__battleCreditMultiplier = mult

    def getBattleCreditMultiplier(self):
        return self.__battleCreditMultiplier

    def setInteractivePropTrackBonus(self, trackBonus):
        self.interactivePropTrackBonus = trackBonus

    def getInteractivePropTrackBonus(self):
        return self.interactivePropTrackBonus

    def setInvasionCreditMultiplier(self, mult):
        self.__invasionCreditMultiplier = mult

    def getInvasionCreditMultiplier(self):
        return self.__invasionCreditMultiplier

    def setRespectInvasions(self, flag):
        self.__respectInvasions = flag

    def getRespectInvasions(self):
        return self.__respectInvasions

    def show(self):
        self.applyDisplayTrackOrder()
        self.updateTotalPropsText()
        if self.tutorialFlag:
            self.tutArrows.arrowsOn(-0.43, -0.12, 180, -0.43, -0.24, 180, onTime=1.0, offTime=0.2)
            if self.numItem(THROW_TRACK, 0) == 0:
                self.tutArrows.arrow1.reparentTo(hidden)
            else:
                self.tutArrows.arrow1.reparentTo(self.battleFrame, 1)
            if self.numItem(SQUIRT_TRACK, 0) == 0:
                self.tutArrows.arrow2.reparentTo(hidden)
            else:
                self.tutArrows.arrow2.reparentTo(self.battleFrame, 1)
            self.tutText.show()
            self.tutText.reparentTo(self.battleFrame, 1)
        DirectFrame.show(self)

    def uberGagToggle(self, showSuperGags = 1):
        self.showSuperGags = showSuperGags
        for itemList in self.invModels:
            for itemIndex in range(MAX_LEVEL_INDEX + 1):
                if itemIndex <= LAST_REGULAR_GAG_LEVEL + 1 or self.showSuperGags:
                    itemList[itemIndex].show()
                else:
                    itemList[itemIndex].hide()

        for buttonList in self.buttons:
            for buttonIndex in range(MAX_LEVEL_INDEX + 1):
                if buttonIndex <= LAST_REGULAR_GAG_LEVEL or self.showSuperGags:
                    buttonList[buttonIndex].show()
                else:
                    buttonList[buttonIndex].hide()

    def enableUberGags(self, enableSG = -1):
        if enableSG != -1:
            self.clickSuperGags = enableSG
        for buttonList in self.buttons:
            for buttonIndex in range(LAST_REGULAR_GAG_LEVEL + 1, MAX_LEVEL_INDEX + 1):
                if self.clickSuperGags:
                    pass
                else:
                    self.makeUnpressable(buttonList[buttonIndex], self.buttons.index(buttonList), buttonIndex)

    def hide(self):
        if self.tutorialFlag:
            self.tutArrows.arrowsOff()
            self.tutText.hide()
        DirectFrame.hide(self)

    def updateTotalPropsText(self):
        # Use Clash's reward order and colours, while letting the active
        # Altis layout choose the correct position and scale.
        textTotal = TTLocalizer.InventoryTotalGags % (self.totalProps, self.toon.getMaxCarry())
        rewardLines = []

        ceaseAndDesists = localAvatar.getCeaseAndDesists()
        pinkSlips = localAvatar.getPinkSlips()

        if ceaseAndDesists > 0:
            rewardLines.append(TTLocalizer.InventoryRewardStrings[0] % ceaseAndDesists)
        if pinkSlips > 0:
            rewardLines.append(TTLocalizer.InventoryRewardStrings[1] % pinkSlips)

        if rewardLines:
            textTotal += '\n\n' + '\n'.join(rewardLines)

        self.totalLabel['text'] = textTotal

    def makeGagEmblemScroll(self):
        tex = loader.loadTexture('phase_3.5/maps/battlegui/pres_scroll_bg.png')
        tex.setWrapU(Texture.WMRepeat)
        tex.setWrapV(Texture.WMRepeat)

        cm = CardMaker('gag-emblem-scroll')
        cm.setFrame(-1, 1, -1, 1)

        self.gagEmblemScroll = self.gagEmblem.attachNewNode(cm.generate())
        self.gagEmblemScroll.setTransparency(1)
        self.gagEmblemScroll.setColorScale(1, 1, 1, 0.35)
        self.gagEmblemScroll.setScale(1.0)
        self.gagEmblemScroll.setPos(0, -0.01, 0)

        self.gagEmblemScrollStage = TextureStage('gag-emblem-scroll-stage')
        self.gagEmblemScroll.setTexture(self.gagEmblemScrollStage, tex, 1)
        self.gagEmblemScroll.setTexScale(self.gagEmblemScrollStage, 2.0, 2.0)

        self.gagEmblemScrollIval = LerpFunctionInterval(
            self._updateGagEmblemScroll,
            duration=2.0,
            fromData=0.0,
            toData=1.0
        )
        self.gagEmblemScrollIval.loop()

    def _updateGagEmblemScroll(self, t):
        self.gagEmblemScroll.setTexOffset(
            self.gagEmblemScrollStage,
            t,
            -t
        )

    def unload(self):
        if getattr(self, 'gagEmblemScrollIval', None):
            self.gagEmblemScrollIval.finish()
            self.gagEmblemScrollIval = None

        if getattr(self, 'gagEmblemScroll', None):
            self.gagEmblemScroll.removeNode()
            self.gagEmblemScroll = None

        self.gagEmblemScrollStage = None
        self.gagEmblemOrganicTex = None
        self.notify.debug('Unloading Inventory for %d' % self.toon.doId)
        self.stopAndClearPropBonusIval()
        self.propBonusIval.finish()
        self.propBonusIval = None
        del self.invModels
        self.buttonModels.removeNode()
        self.rowModels.removeNode()
        del self.rowModels
        del self.buttonModels
        del self.upButton
        del self.downButton
        del self.rolloverButton
        del self.flatButton
        del self.invFrame
        del self.levelsButton
        del self.battleFrame
        del self.purchaseFrame
        del self.storePurchaseFrame
        self.deleteAllButton.destroy()
        del self.deleteAllButton
        self.deleteEnterButton.destroy()
        del self.deleteEnterButton
        self.deleteExitButton.destroy()
        del self.deleteExitButton
        del self.detailFrame
        del self.detailNameLabel
        del self.detailAmountLabel
        del self.detailDataLabel
        del self.totalLabel
        self.cleanupDialog()

        for row in self.trackRows:
            row.destroy()

        del self.trackRows
        del self.trackNameLabels
        del self.trackBars
        for buttonList in self.buttons:
            for button in buttonList:
                button.destroy()

        del self.buttons
        InventoryBase.InventoryBase.unload(self)
        DirectFrame.destroy(self)
        return

    def cleanupDialog(self):
        if self.dialog:
            self.dialog.cleanup()
            self.dialog = None

    def setGagEmblemOrganic(self, organic):
        if not hasattr(self, 'gagEmblemScrollStage') or self.gagEmblemScrollStage is None:
            self.setupGagEmblemOrganicTexture()

        imageNode = self.gagEmblem.component('image0')

        if organic:
            imageNode.setTexture(self.gagEmblemScrollStage, self.gagEmblemOrganicTex, 1)
            imageNode.setTexScale(self.gagEmblemScrollStage, 6, 6)
            imageNode.setTransparency(1)
        else:
            imageNode.clearTexture(self.gagEmblemScrollStage)

    def updateGagEmblemTextureScroll(self, t):
        if not hasattr(self, 'gagEmblemScrollStage'):
            return

        imageNode = self.gagEmblem.component('image0')
        imageNode.setTexOffset(self.gagEmblemScrollStage, t, -t)

    def setupGagEmblemOrganicTexture(self):
        self.gagEmblemOrganicTex = loader.loadTexture('phase_3.5/maps/battlegui/pres_scroll_bg.png')
        self.gagEmblemOrganicTex.setWrapU(Texture.WMRepeat)
        self.gagEmblemOrganicTex.setWrapV(Texture.WMRepeat)

        self.gagEmblemScrollStage = TextureStage('gag-emblem-scroll-stage')

        self.gagEmblemScrollIval = LerpFunctionInterval(
            self.updateGagEmblemTextureScroll,
            duration=3.0,
            fromData=0.0,
            toData=1.0
        )
        self.gagEmblemScrollIval.loop()

    def load(self):
        self.gagEmblemScrollStage = None
        self.notify.debug('Loading Inventory for %d' % self.toon.doId)
        invModel = loader.loadModel('phase_3.5/models/gui/inventory_icons')
        self.invModels = []
        for track in range(len(AvPropsNew)):
            itemList = []
            for item in range(len(AvPropsNew[track])):
                itemList.append(invModel.find('**/' + AvPropsNew[track][item]))

            self.invModels.append(itemList)

        invModel.removeNode()
        del invModel
        self.buttonModels = loader.loadModel('phase_3.5/models/gui/inventory_gui')
        self.rowModels = loader.loadModel('phase_3.5/models/gui/battlegui/gag_selection_panels')
        self.prestigeStar = self.rowModels.find('**/prestige_star_empty')
                                          
        hasOrganic = False

        for item in range(0, len(Levels[track])):
            if self.toon.checkGagBonus(track, item):
                hasOrganic = True
                break

        if hasOrganic:
            starGeom = self.rowModels.find('**/prestige_star')
        else:
            starGeom = self.rowModels.find('**/prestige_star_empty')
        for track in range(0, len(Tracks)):
            if track == 0:
                self.rowModel = self.rowModels.find('**/track_toon-up')
            elif track == 1:
                self.rowModel = self.rowModels.find('**/track_trap')
            elif track == 2:
                self.rowModel = self.rowModels.find('**/track_lure')
            elif track == 3:
                self.rowModel = self.rowModels.find('**/track_throw')
            elif track == 4:
                self.rowModel = self.rowModels.find('**/track_squirt')
            elif track == 5:
                self.rowModel = self.rowModels.find('**/track_zap')
            elif track == 6:
                self.rowModel = self.rowModels.find('**/track_sound')
            elif track == 7:
                self.rowModel = self.rowModels.find('**/track_drop')
            else:
                self.rowModel = self.rowModels.find('**/track_toon-up')
        self.upButton = self.buttonModels.find('**/InventoryButtonUp')
        self.downButton = self.buttonModels.find('**/InventoryButtonDown')
        self.rolloverButton = self.buttonModels.find('**/InventoryButtonRollover')
        self.flatButton = self.buttonModels.find('**/InventoryButtonFlat')
        self.invFrame = DirectFrame(relief=None, parent=self, pos=(0, 0, 0.2))
        self.levelsButton = None
        self.battleFrame = None
        self.gagIconPanel = None
        self.purchaseFrame = None
        self.storePurchaseFrame = None
        self.questionEmblem = None
        self.gagEmblem = None
        trashcanGui = loader.loadModel('phase_3/models/gui/trashcan_gui')
        self.deleteEnterButton = DirectButton(parent=self.invFrame, image=(trashcanGui.find('**/TrashCan_CLSD'), trashcanGui.find('**/TrashCan_OPEN'), trashcanGui.find('**/TrashCan_RLVR')), text=('', TTLocalizer.InventoryDelete, TTLocalizer.InventoryDelete), text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1), text_scale=0.1, text_pos=(0, -0.1), text_font=getInterfaceFont(), textMayChange=0, relief=None, pos=(-1.3, 0, -0.35), scale=0.70)
        self.deleteAllButton = DirectButton(parent=self.invFrame, image=(trashcanGui.find('**/TrashCan_CLSD'), trashcanGui.find('**/TrashCan_OPEN'), trashcanGui.find('**/TrashCan_RLVR')), text=('', TTLocalizer.InventoryDeleteAll, TTLocalizer.InventoryDeleteAll), text_fg=(1, 0, 0, 1), text_shadow=(1, 1, 1, 1), text_scale=0.1, text_pos=(0, -0.1), text_font=getInterfaceFont(), textMayChange=0, relief=None, pos=(-0.3, 0, -0.91), scale=0.75, command=self.__zeroInvConfirm)
        self.deleteExitButton = DirectButton(parent=self.invFrame, image=(trashcanGui.find('**/TrashCan_OPEN'), trashcanGui.find('**/TrashCan_CLSD'), trashcanGui.find('**/TrashCan_RLVR')), text=('', TTLocalizer.InventoryDone, TTLocalizer.InventoryDone), text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1), text_scale=0.1, text_pos=(0, -0.1), text_font=getInterfaceFont(), textMayChange=0, relief=None, pos=(-1, 0, -0.35), scale=1.0)
        trashcanGui.removeNode()
        self.deleteHelpText = DirectLabel(parent=self.invFrame, relief=None, pos=(0.272, 0.3, -0.907), text=TTLocalizer.InventoryDeleteHelp, text_fg=(0, 0, 0, 1), text_scale=0.08, textMayChange=0)
        self.deleteHelpText.hide()
        self.detailFrame = DirectFrame(parent=self.invFrame, relief=None, pos=(0, 0, 0))
        emblemModel = self.rowModels

        self.questionEmblem = DirectFrame(
            parent=self.detailFrame,
            image=emblemModel.find('**/emblem_question'),
            pos=(0.0, 0, 0.18),
            scale=.88,
            relief=None
        )
        self.questionEmblem.show()

        self.gagEmblem = DirectFrame(
            parent=self.detailFrame,
            image=emblemModel.find('**/emblem_gag'),
            pos=(-.0475, 0, 0.012),
            scale=.88,
            relief=None
        )
        self.gagEmblemScrollStage = None
        self.gagEmblemOrganicTex = None
        self.gagEmblemScrollIval = None
        self.gagEmblem.hide()
                                                                                
                                                                                
                                                                        
        self.detailNameLabel = DirectLabel(
            parent=self.detailFrame,
            text='',
            text_scale=TTLocalizer.INdetailNameLabel,
            text_fg=(0, 0, 0, 1),
            text_pos=(0, -3.6),
            scale=0.105,
            pos=(0, 0, 0.105),
            text_font=getInterfaceFont(),
            text_align=TextNode.ACenter,
            relief=None,
            image=self.invModels[0][0]
        )
        self.detailAmountLabel = DirectLabel(
            parent=self.detailFrame,
            text='',
            text_fg=(0, 0, 0, 1),
            scale=0.082,
            pos=(0, 0, -0.13),
            text_font=getInterfaceFont(),
            text_align=TextNode.ACenter,
            relief=None
        )
        self.detailDataLabel = DirectLabel(
            parent=self.detailFrame,
            text='',
            text_fg=(0, 0, 0, 1),
            scale=0.068,
            pos=(0, 0, -0.21),
            text_font=getInterfaceFont(),
            text_align=TextNode.ACenter,
            text_wordwrap=15,
            relief=None
        )
        self.detailCreditLabel = DirectLabel(
            parent=self.detailFrame,
            text=TTLocalizer.InventorySkillCreditNone,
            text_fg=(0, 0, 0, 1),
            scale=0.064,
            pos=(0, 0, -0.49),
            text_font=getInterfaceFont(),
            text_align=TextNode.ACenter,
            text_wordwrap=15,
            relief=None
        )
        self.detailCreditLabel.hide()
        self.totalLabel = DirectLabel(text='', parent=self.detailFrame, pos=(0.0, 0, -0.08), scale=0.07, text_align=TextNode.ACenter, text_wordwrap=0, text_font=getInterfaceFont(), relief=None)
        self.dialog = None
        self.updateTotalPropsText()
        self.trackRows = []
        self.trackNameLabels = []
        self.trackBars = []

        self.buttons = []
        for track in range(0, len(Tracks)):
            if track == 0:
                rowModel = self.rowModels.find('**/track_toon-up')
            elif track == 1:
                rowModel = self.rowModels.find('**/track_trap')
            elif track == 2:
                rowModel = self.rowModels.find('**/track_lure')
            elif track == 3:
                rowModel = self.rowModels.find('**/track_throw')
            elif track == 4:
                rowModel = self.rowModels.find('**/track_squirt')
            elif track == 5:
                rowModel = self.rowModels.find('**/track_zap')
            elif track == 6:
                rowModel = self.rowModels.find('**/track_sound')
            elif track == 7:
                rowModel = self.rowModels.find('**/track_drop')
            else:
                rowModel = self.rowModels.find('**/track_toon-up')

            trackFrame = DirectFrame(
                parent=self.invFrame,
                image=rowModel,
                image_scale=(2.12, .5, .13),
                scale=(1.0, 1.0, 1.1),
                image_pos=(-0.01, 0, 0),
                pos=(-.25, 0, self.TrackYOffset + track * self.TrackYSpacing),
                image_color=(1, 1, 1, 1),
                state=DGG.NORMAL,
                relief=None
            )
            trackNameNodes = {
                0: '**/track_toon-up_title',
                1: '**/track_trap_title',
                2: '**/track_lure_title',
                3: '**/track_throw_title',
                4: '**/track_squirt_title',
                5: '**/track_zap_title',
                6: '**/track_sound_title',
                7: '**/track_drop_title',
            }
            trackFrame.bind(DGG.WITHIN, self.enterTrackFrame, extraArgs=[track])
            trackFrame.bind(DGG.WITHOUT, self.exitTrackFrame, extraArgs=[track])
            self.trackRows.append(trackFrame)
            adjustLeft = -0.065
            nameNode = self.rowModels.find(trackNameNodes.get(track, '**/track_name_toon-up'))
            scaleByTrack = {
                0: (.4, .1, .1),           
            }

            defaultScale = (.225, .1, .1)

            nameScale = scaleByTrack.get(track, defaultScale)
            self.trackNameLabels.append(
                DirectFrame(
                    parent=self.trackRows[track],
                    image=nameNode,
                    pos=(-0.77 + adjustLeft, 0, 0.025),
                    scale=nameScale,
                    relief=None
                )
            )
            self.trackBars.append(DirectWaitBar(parent=self.trackRows[track], pos=(-0.77 + adjustLeft, -0.1, -0.025), relief=DGG.SUNKEN, frameSize=(-0.6,
             0.6,
             -0.1,
             0.1), borderWidth=(0.02, 0.02), scale=0.25, frameColor=(TrackColors[track][0] * 0.6,
             TrackColors[track][1] * 0.6,
             TrackColors[track][2] * 0.6,
             1), barColor=(TrackColors[track][0] * 0.9,
             TrackColors[track][1] * 0.9,
             TrackColors[track][2] * 0.9,
             1), text='0 / 0', text_scale=0.16, text_fg=(0, 0, 0, 0.8), text_align=TextNode.ACenter, text_pos=(0, -0.05)))
            self.buttons.append([])
            for item in range(0, len(Levels[track])):
                button = DirectButton(parent=self.trackRows[track], image=(self.upButton,
                                                                           self.downButton,
                                                                           self.rolloverButton,
                                                                           self.flatButton),
                                      geom=self.invModels[track][item], text='50', text_scale=0.06,
                                      text_align=TextNode.ARight, geom_scale=0.7, geom_pos=(-0.01, -0.1, 0),
                                      text_fg=Vec4(1, 1, 1, 1), text_font=getSignFont(), text_pos=(0.08, -0.045),
                                      textMayChange=1, relief=None, image_color=self.PressableImageColor, image_scale=1.02,
                                      pos=(self.ButtonXOffset + item * self.ButtonXSpacing + adjustLeft, -0.1, 0),
                                      command=self.__handleSelection, extraArgs=[track, item])

                button.bind(DGG.ENTER, self.showDetail, extraArgs=[track, item])
                button.bind(DGG.EXIT, self.hideDetail)
                self.buttons[track].append(button)
                                               
            starItem = len(Levels[track])

            hasOrganic = False

            for item in range(0, len(Levels[track])):
                if self.toon.checkGagBonus(track, item):
                    hasOrganic = True
                    break

            starGeom = self.rowModels.find(
                '**/prestige_star' if hasOrganic else '**/prestige_star_empty'
            )


            starButton = DirectButton(
                parent=self.trackRows[track],
                image=starGeom,
                text='',
                relief=None,
                image_color=(1, 1, 1, 1),
                image_scale=.075,
                pos=(self.ButtonXOffset + starItem * self.ButtonXSpacing + -0.095, -0.1, 0)
            )

                                
                                   

            self.buttons[track].append(starButton)
        return

    def __handleSelection(self, track, level):
        if self.activateMode == 'purchaseDelete' or self.activateMode == 'bookDelete' or self.activateMode == 'storePurchaseDelete':
            if self.numItem(track, level):
                self.useItem(track, level)
                self.updateGUI(track, level)
                messenger.send('inventory-deletion', [track, level])
                self.showDetail(track, level)
        elif self.activateMode == 'purchase' or self.activateMode == 'storePurchase':
            messenger.send('inventory-selection', [track, level])
            self.showDetail(track, level)
        elif self.gagTutMode:
            pass
        else:
            messenger.send('inventory-selection', [track, level])

    def __handleRun(self):
        messenger.send('inventory-run')

    def __handleFire(self):
        messenger.send('inventory-fire')
    
    def __handleSue(self):
        messenger.send('inventory-sue')

    def __handleSOS(self):
        messenger.send('inventory-sos')

    def __handlePass(self):
        messenger.send('inventory-pass')

    def __handleLevels(self):
        if settings.get('show-cog-levels', True):
            settings['show-cog-levels'] = False
            self.levelsButton['text'] = TTLocalizer.InventoryLevelsShow
        else:
            settings['show-cog-levels'] = True
            self.levelsButton['text'] = TTLocalizer.InventoryLevelsHide
        messenger.send('inventory-levels')

    def __handleBackToPlayground(self):
        messenger.send('inventory-back-to-playground')

    def __zeroInvConfirm(self):
        self.cleanupDialog()
        self.dialog = TTDialog.TTDialog(style=TTDialog.YesNo, text=TTLocalizer.InventoryDeleteConfirm, command=self.__zeroInvAndUpdate)
        self.dialog.show()
    
    def __zeroInvAndUpdate(self, value):
        self.cleanupDialog()
        
        if value > 0:
            self.zeroInv()
            self.updateGUI()

    def showDetail(self, track, level, event = None):
        trackColor = Vec4(
            TrackColors[track][0],
            TrackColors[track][1],
            TrackColors[track][2],
            1
        )

        self.gagEmblem['image_color'] = trackColor

        self.questionEmblem.hide()
        self.gagEmblem.show()
        self.totalLabel.hide()
        self.detailNameLabel.show()
        self.detailNameLabel.configure(text=AvPropStrings[track][level], image_image=self.invModels[track][level])
        if self.activateMode == 'book':
            self.detailNameLabel.configure(image_scale=18.0, image_pos=(0.0, 0, 1.08))
        else:
            self.detailNameLabel.configure(image_scale=20, image_pos=(0, 0, 2.75))
        self.detailAmountLabel.show()
        organicBonus = self.toon.checkGagBonus(track, level)
        self.setGagEmblemOrganic(organicBonus)
        self.detailAmountLabel.configure(text=TTLocalizer.InventoryDetailAmount % {'numItems': self.numItem(track, level),
         'maxItems': self.getMax(track, level)})
        self.detailDataLabel.show()
        organicBonus = self.toon.checkGagBonus(track, level)
        propBonus = self.checkPropBonus(track)
        if track == LURE_TRACK:
            damage = ToontownBattleGlobals.AvLureRounds[level]
        else:
            damage = getAvPropDamage(track, level, self.toon.experience.getExp(track))
        damageBonusStr = ''
        damageBonus = 0

        damageAppendStr = ''
        accString = AvTrackAccStrings[track]

        iouBoosts = {}
        for condition, conditionData in base.localAvatar.battleConditions.items():
            parsedIOU = IOURegistry.parseConditionName(condition)
            if parsedIOU is None:
                continue
            iouTrack, iouBoost = parsedIOU
            if iouTrack not in (track, -1):
                continue
            currentBoost = iouBoosts.get(iouTrack, 0)
            if iouBoost > currentBoost:
                iouBoosts[iouTrack] = iouBoost
        iouFlatBoost = sum(iouBoosts.values())
        if track != LURE_TRACK:
            damage += iouFlatBoost

        allGagBoost = False
        if 'allGagBoost' in base.localAvatar.battleConditions:
            allGagBoost = True

        viralSensation = False
        if 'viralSensation' in base.localAvatar.battleConditions:
            viralSensation = True

        energized = False
        if 'energized' in base.localAvatar.battleConditions:
            energized = True

        allGagBoost2 = False
        if 'allGagBoost2' in base.localAvatar.battleConditions:
            allGagBoost2 = True

        raisedAnte = False
        if 'raisedAnte' in base.localAvatar.battleConditions:
            raisedAnte = True

        governaughtBoost = False
        if 'governaughtBoost' in base.localAvatar.battleConditions:
            governaughtBoost = True

        groupDamageDown = False
        if 'groupDamageDown' in base.localAvatar.battleConditions:
            groupDamageDown = True

        encore = False
        if 'encore' in base.localAvatar.battleConditions:
            encore = True

        winded = False
        if 'winded' in base.localAvatar.battleConditions:
            winded = True

        def labelColorize(damage, param):
            button = self.buttons[track][level]
            val = base.localAvatar.battleConditions[param][0]
            if allGagBoost and not track == LURE_TRACK:
                val = base.localAvatar.battleConditions[param][0] + base.localAvatar.battleConditions['allGagBoost'][0]
            if allGagBoost2 and not track == LURE_TRACK:
                val = base.localAvatar.battleConditions[param][0] + base.localAvatar.battleConditions['allGagBoost2'][0]
            if viralSensation:
                val = base.localAvatar.battleConditions[param][0] + base.localAvatar.battleConditions['viralSensation'][0]
            if energized:
                val = base.localAvatar.battleConditions[param][0] + base.localAvatar.battleConditions['energized'][0]
            if governaughtBoost:
                val = base.localAvatar.battleConditions[param][0] + base.localAvatar.battleConditions['governaughtBoost'][0]
            if raisedAnte and not track == LURE_TRACK:
                val = base.localAvatar.battleConditions[param][0] + base.localAvatar.battleConditions['raisedAnte'][0]
            if base.localAvatar.battleConditions[param][0] > 0.0:
                self.detailDataLabel['text_fg'] = (0, 0.392, 1, 1.0)
                return " (+{}%)".format(val)
            elif base.localAvatar.battleConditions[param][0] < 0.0:
                self.detailDataLabel['text_fg'] = (1, 0, 0, 1.0)
                return " ({}%)".format(val)
            else:
                self.detailDataLabel['text_fg'] = (0, 0, 0, 1)
                return ""

        def labelColorizeJustAll(damage, param):
            if base.localAvatar.battleConditions[param][0] > 0.0:
                self.detailDataLabel['text_fg'] = (0, 0.392, 1, 1.0)
                return " (+{}%)".format(base.localAvatar.battleConditions[param][0])
            elif base.localAvatar.battleConditions[param][0] < 0.0:
                self.detailDataLabel['text_fg'] = (1, 0, 0, 1.0)
                return " ({}%)".format(base.localAvatar.battleConditions[param][0])
            else:
                self.detailDataLabel['text_fg'] = (0, 0, 0, 1)
                return ""

        self.detailDataLabel['text_fg'] = (0, 0, 0, 1)
        if track == THROW_TRACK and 'throwBoost' in base.localAvatar.battleConditions:
            damage = int(math.ceil(damage * ((base.localAvatar.battleConditions['throwBoost'][0] * 0.01) + 1.0)))
            damageAppendStr = labelColorize(damage, 'throwBoost')
        if track == SQUIRT_TRACK and 'squirtBoost' in base.localAvatar.battleConditions:
            damage = int(math.ceil(damage * ((base.localAvatar.battleConditions['squirtBoost'][0] * 0.01) + 1.0)))
            damageAppendStr = labelColorize(damage, 'squirtBoost')
        if track == ZAP_TRACK and 'zapBoost' in base.localAvatar.battleConditions:
            damage = int(math.ceil(damage * ((base.localAvatar.battleConditions['zapBoost'][0] * 0.01) + 1.0)))
            damageAppendStr = labelColorize(damage, 'zapBoost')
        if track == DROP_TRACK and 'dropBoost' in base.localAvatar.battleConditions:
            damage = int(math.ceil(damage * ((base.localAvatar.battleConditions['dropBoost'][0] * 0.01) + 1.0)))
            damageAppendStr = labelColorize(damage, 'dropBoost')
        if track == SOUND_TRACK and 'soundBoost' in base.localAvatar.battleConditions:
            damage = int(math.ceil(damage * ((base.localAvatar.battleConditions['soundBoost'][0] * 0.01) + 1.0)))
            damageAppendStr = labelColorize(damage, 'soundBoost')
        if track == HEAL_TRACK and 'healBoost' in base.localAvatar.battleConditions:
            damage = int(math.ceil(damage * ((base.localAvatar.battleConditions['healBoost'][0] * 0.01) + 1.0)))
            damageAppendStr = labelColorize(damage, 'healBoost')
        if track == TRAP_TRACK and 'trapBoost' in base.localAvatar.battleConditions:
            damage = int(math.ceil(damage * ((base.localAvatar.battleConditions['trapBoost'][0] * 0.01) + 1.0)))
            damageAppendStr = labelColorize(damage, 'trapBoost')
        if track == LURE_TRACK and 'lureBoost' in base.localAvatar.battleConditions:
            lureValue = int(math.ceil(
                ((ToontownBattleGlobals.AvLureKnockback[level] * 100) + base.localAvatar.battleConditions['lureBoost'][
                    0]) / 2))
            damageAppendStr = labelColorize(lureValue, 'lureBoost')
        if track == LURE_TRACK and 'lureBoost2' in base.localAvatar.battleConditions:
            lureValue = int(math.ceil(
                ((ToontownBattleGlobals.AvLureKnockback[level] * 100) + base.localAvatar.battleConditions['lureBoost2'][
                    0]) / 2))
            damageAppendStr = labelColorize(lureValue, 'lureBoost2')
        if track == HEAL_TRACK and 'encore' in base.localAvatar.battleConditions:
            damage = int(math.ceil(damage * ((base.localAvatar.battleConditions['encore'][0] * 0.01) + 1.0)))
            damageAppendStr = labelColorize(damage, 'encore')
        if track == HEAL_TRACK and 'encore2' in base.localAvatar.battleConditions:
            damage = int(math.ceil(damage * ((base.localAvatar.battleConditions['encore2'][0] * 0.01) + 1.0)))
            damageAppendStr = labelColorize(damage, 'encore2')
        if track == SOUND_TRACK and 'encore' in base.localAvatar.battleConditions:
            damage = int(math.ceil(damage * ((base.localAvatar.battleConditions['encore'][0] * 0.01) + 1.0)))
            damageAppendStr = labelColorize(damage, 'encore')
        if track == TRAP_TRACK and 'encore' in base.localAvatar.battleConditions:
            damage = int(math.ceil(damage * ((base.localAvatar.battleConditions['encore'][0] * 0.01) + 1.0)))
            damageAppendStr = labelColorize(damage, 'encore')
        if track == THROW_TRACK and 'encore' in base.localAvatar.battleConditions:
            damage = int(math.ceil(damage * ((base.localAvatar.battleConditions['encore'][0] * 0.01) + 1.0)))
            damageAppendStr = labelColorize(damage, 'encore')
        if track == SQUIRT_TRACK and 'encore' in base.localAvatar.battleConditions:
            damage = int(math.ceil(damage * ((base.localAvatar.battleConditions['encore'][0] * 0.01) + 1.0)))
            damageAppendStr = labelColorize(damage, 'encore')
        if track == ZAP_TRACK and 'encore' in base.localAvatar.battleConditions:
            damage = int(math.ceil(damage * ((base.localAvatar.battleConditions['encore'][0] * 0.01) + 1.0)))
            damageAppendStr = labelColorize(damage, 'encore')
        if track == DROP_TRACK and 'encore' in base.localAvatar.battleConditions:
            damage = int(math.ceil(damage * ((base.localAvatar.battleConditions['encore'][0] * 0.01) + 1.0)))
            damageAppendStr = labelColorize(damage, 'encore')
        if track == LURE_TRACK and 'encore' in base.localAvatar.battleConditions:
            lureValue = int(math.ceil(
                ((ToontownBattleGlobals.AvLureKnockback[level] * 100) + base.localAvatar.battleConditions['encore'][
                    0]) / 2))
            damageAppendStr = labelColorize(lureValue, 'encore')
        if track == SOUND_TRACK and 'encore2' in base.localAvatar.battleConditions:
            damage = int(math.ceil(damage * ((base.localAvatar.battleConditions['encore2'][0] * 0.01) + 1.0)))
            damageAppendStr = labelColorize(damage, 'encore2')
        if track == TRAP_TRACK and 'encore2' in base.localAvatar.battleConditions:
            damage = int(math.ceil(damage * ((base.localAvatar.battleConditions['encore2'][0] * 0.01) + 1.0)))
            damageAppendStr = labelColorize(damage, 'encore2')
        if track == THROW_TRACK and 'encore2' in base.localAvatar.battleConditions:
            damage = int(math.ceil(damage * ((base.localAvatar.battleConditions['encore2'][0] * 0.01) + 1.0)))
            damageAppendStr = labelColorize(damage, 'encore2')
        if track == SQUIRT_TRACK and 'encore2' in base.localAvatar.battleConditions:
            damage = int(math.ceil(damage * ((base.localAvatar.battleConditions['encore2'][0] * 0.01) + 1.0)))
            damageAppendStr = labelColorize(damage, 'encore2')
        if track == ZAP_TRACK and 'encore2' in base.localAvatar.battleConditions:
            damage = int(math.ceil(damage * ((base.localAvatar.battleConditions['encore2'][0] * 0.01) + 1.0)))
            damageAppendStr = labelColorize(damage, 'encore2')
        if track == DROP_TRACK and 'encore2' in base.localAvatar.battleConditions:
            damage = int(math.ceil(damage * ((base.localAvatar.battleConditions['encore2'][0] * 0.01) + 1.0)))
            damageAppendStr = labelColorize(damage, 'encore2')
        if track == LURE_TRACK and 'encore2' in base.localAvatar.battleConditions:
            lureValue = int(math.ceil(
                ((ToontownBattleGlobals.AvLureKnockback[level] * 100) + base.localAvatar.battleConditions['encore2'][
                    0]) / 2))
            damageAppendStr = labelColorize(lureValue, 'encore2')
        if allGagBoost and not track == LURE_TRACK:
            damage = int(math.ceil(damage * ((base.localAvatar.battleConditions['allGagBoost'][0] * 0.01) + 1.0)))
            damageAppendStr = labelColorizeJustAll(damage, 'allGagBoost')
        if allGagBoost2 and not track == LURE_TRACK:
            damage = int(math.ceil(damage * ((base.localAvatar.battleConditions['allGagBoost2'][0] * 0.01) + 1.0)))
            damageAppendStr = labelColorizeJustAll(damage, 'allGagBoost2')
        if viralSensation and not track == LURE_TRACK:
            damage = int(math.ceil(damage * ((base.localAvatar.battleConditions['viralSensation'][0] * 0.01) + 1.0)))
            damageAppendStr = labelColorizeJustAll(damage, 'viralSensation')
        if energized and not track == LURE_TRACK:
            damage = int(math.ceil(damage * ((base.localAvatar.battleConditions['energized'][0] * 0.01) + 1.0)))
            damageAppendStr = labelColorizeJustAll(damage, 'energized')
        if governaughtBoost and track == LURE_TRACK:
            lureValue = int(math.ceil(
                ((ToontownBattleGlobals.AvLureKnockback[level] * 100) + base.localAvatar.battleConditions['governaughtBoost'][
                    0]) / 2))
            damageAppendStr = labelColorize(lureValue, 'governaughtBoost')
        if governaughtBoost and not track == LURE_TRACK:
            damage = int(math.ceil(damage * ((base.localAvatar.battleConditions['governaughtBoost'][0] * 0.01) + 1.0)))
            damageAppendStr = labelColorizeJustAll(damage, 'governaughtBoost')
        if raisedAnte and not track == LURE_TRACK:
            damage = int(math.ceil(damage * ((base.localAvatar.battleConditions['raisedAnte'][0] * 0.01) + 1.0)))
            damageAppendStr = labelColorizeJustAll(damage, 'raisedAnte')
        if track == SOUND_TRACK and 'winded' in base.localAvatar.battleConditions:
            damage = int(math.ceil(damage * ((base.localAvatar.battleConditions['winded'][0] * 0.01) + 1.0)))
            damageAppendStr = labelColorize(damage, 'winded')
        if track == SOUND_TRACK and 'groupDamageDown' in base.localAvatar.battleConditions:
            damage = int(math.ceil(damage * ((base.localAvatar.battleConditions['groupDamageDown'][0] * 0.01) + 1.0)))
            damageAppendStr = labelColorize(damage, 'groupDamageDown')
        if track == SQUIRT_TRACK and 'groupDamageDown' in base.localAvatar.battleConditions:
            damage = int(math.ceil(damage * ((base.localAvatar.battleConditions['groupDamageDown'][0] * 0.01) + 1.0)))
            damageAppendStr = labelColorize(damage, 'groupDamageDown')
        if track == ZAP_TRACK and 'groupDamageDown' in base.localAvatar.battleConditions:
            damage = int(math.ceil(damage * ((base.localAvatar.battleConditions['groupDamageDown'][0] * 0.01) + 1.0)))
            damageAppendStr = labelColorize(damage, 'groupDamageDown')
        if track == HEAL_TRACK and 'groupDamageDown' in base.localAvatar.battleConditions and level == 7:
            damage = int(math.ceil(damage * ((base.localAvatar.battleConditions['groupDamageDown'][0] * 0.01) + 1.0)))
            damageAppendStr = labelColorize(damage, 'groupDamageDown')
        if track == HEAL_TRACK and 'groupDamageDown' in base.localAvatar.battleConditions and level == 5:
            damage = int(math.ceil(damage * ((base.localAvatar.battleConditions['groupDamageDown'][0] * 0.01) + 1.0)))
            damageAppendStr = labelColorize(damage, 'groupDamageDown')
        if track == HEAL_TRACK and 'groupDamageDown' in base.localAvatar.battleConditions and level == 3:
            damage = int(math.ceil(damage * ((base.localAvatar.battleConditions['groupDamageDown'][0] * 0.01) + 1.0)))
            damageAppendStr = labelColorize(damage, 'groupDamageDown')
        if track == HEAL_TRACK and 'groupDamageDown' in base.localAvatar.battleConditions and level == 1:
            damage = int(math.ceil(damage * ((base.localAvatar.battleConditions['groupDamageDown'][0] * 0.01) + 1.0)))
            damageAppendStr = labelColorize(damage, 'groupDamageDown')
        lureValue = int(math.ceil(
            ((ToontownBattleGlobals.AvLureKnockback[level] * 100 + iouFlatBoost) / 2)))
        if track == LURE_TRACK and 'groupDamageDown' in base.localAvatar.battleConditions and level == 7:
            lureValue = int(math.ceil(lureValue * ((base.localAvatar.battleConditions['groupDamageDown'][0] * 0.01) + 1.0)))
            damageAppendStr = labelColorize(lureValue, 'groupDamageDown')
        elif track == LURE_TRACK and 'groupDamageDown' in base.localAvatar.battleConditions and level == 5:
            lureValue = int(math.ceil(lureValue * ((base.localAvatar.battleConditions['groupDamageDown'][0] * 0.01) + 1.0)))
            damageAppendStr = labelColorize(lureValue, 'groupDamageDown')
        elif track == LURE_TRACK and 'groupDamageDown' in base.localAvatar.battleConditions and level == 3:
            lureValue = int(math.ceil(lureValue * ((base.localAvatar.battleConditions['groupDamageDown'][0] * 0.01) + 1.0)))
            damageAppendStr = labelColorize(lureValue, 'groupDamageDown')
        elif track == LURE_TRACK and 'groupDamageDown' in base.localAvatar.battleConditions and level == 1:
            lureValue = int(math.ceil(lureValue * ((base.localAvatar.battleConditions['groupDamageDown'][0] * 0.01) + 1.0)))
            damageAppendStr = labelColorize(lureValue, 'groupDamageDown')

        damage = math.ceil(damage)
        organicBonus = self.toon.checkGagBonus(track, level)
        if track == TRAP_TRACK and organicBonus:
            self.detailDataLabel.configure(text=TTLocalizer.InventoryDetailData % {'accuracy': accString,
                                                                                   'damageString': self.getToonupDmgStr(
                                                                                       track, level),
                                                                                   'damage': str(
                                                                                       int(math.ceil(damage * 1.15))) + damageAppendStr,
                                                                                   'bonus': '\nExe./Gov./Mgr.: %s%s\nDaze Rounds: %i' % (
                                                                                  str(int(math.ceil(math.ceil(damage * 1.15) * 1.3))),
                                                                                   damageAppendStr, ToontownBattleGlobals.AvDazeRounds[level]),
                                                                                   'singleOrGroup': self.getSingleGroupStr(
                                                                                       track, level)})
                                                              
        elif track == TRAP_TRACK:
            self.detailDataLabel.configure(text=TTLocalizer.InventoryDetailData % {'accuracy': accString,
                                                                                   'damageString': self.getToonupDmgStr(
                                                                                       track, level),
                                                                                   'damage': str(
                                                                                       int(damage)) + damageAppendStr,
                                                                                   'bonus': '\nExe./Gov./Mgr.: %s%s\nDaze Rounds: %i' % (
                                                                                   str(int(math.ceil(damage * 1.3))),
                                                                                   damageAppendStr, ToontownBattleGlobals.AvDazeRounds[level]),
                                                                                   'singleOrGroup': self.getSingleGroupStr(
                                                                                       track, level)})
                                                              
        elif track == LURE_TRACK and organicBonus:
            self.detailDataLabel.configure(text=TTLocalizer.InventoryDetailData % {'accuracy': accString,
                                                                                   'damageString': "Rounds",
                                                                                   'damage':
                                                                                       ToontownBattleGlobals.AvLureRounds[
                                                                                           level] + 1,
                                                                                   'bonus': '\nKnockback: %s' %
                                                                                       int(math.ceil(lureValue * 1.2))+'%' + damageAppendStr,
                                                                                   'singleOrGroup': self.getSingleGroupStr(
                                                                                       track, level)})
                                                              
        elif track == LURE_TRACK:
            self.detailDataLabel.configure(text=TTLocalizer.InventoryDetailData % {'accuracy': accString,
                                                                                   'damageString': "Rounds",
                                                                                   'damage':
                                                                                       ToontownBattleGlobals.AvLureRounds[
                                                                                           level] + 1,
                                                                                   'bonus': '\nKnockback: %s' %
                                                                                       str(int(lureValue))+'%' + damageAppendStr,
                                                                                   'singleOrGroup': self.getSingleGroupStr(
                                                                                       track, level)})
                                                              
        elif track == THROW_TRACK and organicBonus:
            self.detailDataLabel.configure(text=TTLocalizer.InventoryDetailData % {'accuracy': accString,
                                                                                   'damageString': self.getToonupDmgStr(
                                                                                       track, level),
                                                                                   'damage': str(
                                                                                       int(damage)) + damageAppendStr,
                                                                                   'bonus': '\nMark Rounds: %i\nMarked Damage: %i%%\nSelf Heal: %i' % (
                                                                                       2, +ToontownBattleGlobals.AvMarkBoost, int(math.ceil(damage / 4))) + damageBonusStr,
                                                                                   'singleOrGroup': self.getSingleGroupStr(
                                                                                       track, level)})
                                                              
        elif track == THROW_TRACK:
            self.detailDataLabel.configure(text=TTLocalizer.InventoryDetailData % {'accuracy': accString,
                                                                                   'damageString': self.getToonupDmgStr(
                                                                                       track, level),
                                                                                   'damage': str(
                                                                                       int(damage)) + damageAppendStr,
                                                                                   'bonus': '\nMark Rounds: %i\nMarked Damage: %i%%\nSelf Heal: %i' % (
                                                                                       1, +ToontownBattleGlobals.AvMarkBoost, int(math.ceil(damage / 5))),
                                                                                   'singleOrGroup': self.getSingleGroupStr(
                                                                                       track, level)})
                                                              
        elif track == SOUND_TRACK and organicBonus:
            self.detailDataLabel.configure(text=TTLocalizer.InventoryDetailData % {'accuracy': accString,
                                                                                   'damageString': self.getToonupDmgStr(
                                                                                       track, level),
                                                                                   'damage': str(int(damage)) + damageAppendStr,
                                                                                   'bonus': '\nEncore Gag Bonus: 20%',
                                                                                   'singleOrGroup': self.getSingleGroupStr(
                                                                                       track, level)})
                                                              
        elif track == SOUND_TRACK:
            self.detailDataLabel.configure(text=TTLocalizer.InventoryDetailData % {'accuracy': accString,
                                                                                   'damageString': self.getToonupDmgStr(
                                                                                       track, level),
                                                                                   'damage': str(int(damage)) + damageAppendStr,
                                                                                   'bonus': '\nEncore Gag Bonus: 10%',
                                                                                   'singleOrGroup': self.getSingleGroupStr(
                                                                                       track, level)})
                                                              
        elif track == ZAP_TRACK and organicBonus:
            self.detailDataLabel.configure(text=TTLocalizer.InventoryDetailData % {'accuracy': accString,
                                                                                   'damageString': self.getToonupDmgStr(
                                                                                       track, level),
                                                                                   'damage': str(
                                                                                       int(damage)) + damageAppendStr,
                                                                                   'bonus': "\nAftershock Damage: %i" % 
                                                                                       int(math.ceil(damage * .25)),
                                                                                   'singleOrGroup': self.getSingleGroupStr(
                                                                                       track, level)})
                                                              
        elif track == ZAP_TRACK:
            self.detailDataLabel.configure(text=TTLocalizer.InventoryDetailData % {'accuracy': accString,
                                                                                   'damageString': self.getToonupDmgStr(
                                                                                       track, level),
                                                                                   'damage': str(
                                                                                       int(damage)) + damageAppendStr,
                                                                                   'bonus': "\nAftershock Damage: %i" % 
                                                                                       int(math.ceil(damage * .25)),
                                                                                   'singleOrGroup': self.getSingleGroupStr(
                                                                                       track, level)})
                                                              
        elif track == HEAL_TRACK and organicBonus:
            self.detailDataLabel.configure(text=TTLocalizer.InventoryDetailData % {'accuracy': accString,
                                                                                   'damageString': self.getToonupDmgStr(
                                                                                       track, level),
                                                                                   'damage': str(
                                                                                       int(damage)) + damageAppendStr,
                                                                                   'bonus': '\nSelf Heal: %i%s' % (
                                                                                   int(math.ceil(damage / 2.22)),
                                                                                   damageAppendStr) + damageBonusStr,
                                                                                   'singleOrGroup': self.getSingleGroupStr(
                                                                                       track, level)})
                                                              
        elif track == HEAL_TRACK:
            self.detailDataLabel.configure(text=TTLocalizer.InventoryDetailData % {'accuracy': accString,
                                                                                   'damageString': self.getToonupDmgStr(
                                                                                       track, level),
                                                                                   'damage': str(
                                                                                       int(damage)) + damageAppendStr,
                                                                                   'bonus': '\nSelf Heal: %i%s' % (
                                                                                   int(math.ceil(damage / 4)),
                                                                                   damageAppendStr) + damageBonusStr,
                                                                                   'singleOrGroup': self.getSingleGroupStr(
                                                                                       track, level)})
                                                              
        elif track == SQUIRT_TRACK and organicBonus:
            self.detailDataLabel.configure(text=TTLocalizer.InventoryDetailData % {'accuracy': accString,
                                                                                   'damageString': self.getToonupDmgStr(
                                                                                       track, level),
                                                                                   'damage': str(
                                                                                       int(damage)) + damageAppendStr,
                                                                                   'bonus': '\nDrench Rounds: 4\nSplash Damage: %i' % 
                                                                                       int(math.ceil(damage * .75)),
                                                                                   'singleOrGroup': self.getSingleGroupStr(
                                                                                       track, level)})
                                                             
        elif track == SQUIRT_TRACK:
            self.detailDataLabel.configure(text=TTLocalizer.InventoryDetailData % {'accuracy': accString,
                                                                                   'damageString': self.getToonupDmgStr(
                                                                                       track, level),
                                                                                   'damage': str(
                                                                                       int(damage)) + damageAppendStr,
                                                                                   'bonus': '\nSoak Rounds: 4\nSplash Damage: %i' % 
                                                                                       int(math.ceil(damage * .33)),
                                                                                   'singleOrGroup': self.getSingleGroupStr(
                                                                                       track, level)})
                                                             
        elif track == DROP_TRACK and organicBonus:
            self.detailDataLabel.configure(text=TTLocalizer.InventoryDetailData % {'accuracy': accString,
                                                                                   'damageString': self.getToonupDmgStr(
                                                                                       track, level),
                                                                                   'damage': str(
                                                                                       int(damage)) + damageAppendStr,
                                                                                   'bonus': '\nBonus Damage: Varies',
                                                                                   'singleOrGroup': self.getSingleGroupStr(
                                                                                       track, level)})
                                                              
        elif track == DROP_TRACK:
            self.detailDataLabel.configure(text=TTLocalizer.InventoryDetailData % {'accuracy': accString,
                                                                                   'damageString': self.getToonupDmgStr(
                                                                                       track, level),
                                                                                   'damage': str(
                                                                                       int(damage)) + damageAppendStr,
                                                                                   'bonus': '',
                                                                                   'singleOrGroup': self.getSingleGroupStr(
                                                                                       track, level)})
                                                              
        else:
            self.detailDataLabel.configure(text=TTLocalizer.InventoryDetailData % {'accuracy': accString,
             'damageString': self.getToonupDmgStr(track, level),
             'damage': str(damage) + damageAppendStr + '(Varies)',
             'bonus': damageBonusStr,
             'singleOrGroup': self.getSingleGroupStr(track, level)})
                                                            
                                                                           
                                                                              
                                        
        if self.activateMode == 'book':
            if track == THROW_TRACK:
                self.detailDataLabel.setPos(0, 0, -0.225)
                self.detailDataLabel.setScale(0.059)
                self.detailCreditLabel.setPos(0, 0, -0.585)
            elif track == TRAP_TRACK or track == SQUIRT_TRACK:
                self.detailDataLabel.setPos(0, 0, -0.235)
                self.detailDataLabel.setScale(0.060)
                self.detailCreditLabel.setPos(0, 0, -0.575)
            else:
                self.detailDataLabel.setPos(0, 0, -0.265)
                self.detailDataLabel.setScale(0.064)
                self.detailCreditLabel.setPos(0, 0, -0.525)

        if self.itemIsCredit(track, level):
            mult = self.__battleCreditMultiplier
            if self.__respectInvasions:
                mult *= self.__invasionCreditMultiplier
            self.setDetailCredit(track, (level + 1) * mult)
        else:
            self.setDetailCredit(track, None)
        self.detailCreditLabel.show()
        return

    def setDetailCredit(self, track, credit):
        if credit != None:
            if self.toon.earnedExperience:
                maxCredit = ExperienceCap - self.toon.earnedExperience[track]
                credit = min(credit, maxCredit)
            credit = int(credit * 10 + 0.5)
            if credit % 10 == 0:
                credit /= 10
            else:
                credit /= 10.0
        if self.detailCredit == credit:
            return
        if credit != None:
            self.detailCreditLabel['text'] = TTLocalizer.InventorySkillCredit % credit
            if self.detailCredit == None:
                self.detailCreditLabel['text_fg'] = (0, 0, 0, 1)
        else:
            self.detailCreditLabel['text'] = TTLocalizer.InventorySkillCreditNone
            self.detailCreditLabel['text_fg'] = (1, 0.0, 0.0, 1.0)
        self.detailCredit = credit
        return

    def hideDetail(self, event = None):
        self.totalLabel.show()
        self.questionEmblem.show()
        self.gagEmblem.hide()
        self.detailNameLabel.hide()
        self.detailAmountLabel.hide()
        self.detailDataLabel.hide()
        self.detailCreditLabel.hide()

    def noDetail(self):
        self.totalLabel.hide()
        self.gagEmblem.hide()
        self.questionEmblem.hide()
        self.detailNameLabel.hide()
        self.detailAmountLabel.hide()
        self.detailDataLabel.hide()
        self.detailCreditLabel.hide()

    def setActivateMode(self, mode, heal = 1, trap = 1, lure = 1, bldg = 0, creditLevel = None, tutorialFlag = 0, gagTutMode = 0):
        self.notify.debug('setActivateMode() mode:%s heal:%s trap:%s lure:%s bldg:%s' % (mode,
         heal,
         trap,
         lure,
         bldg))
        self.previousActivateMode = self.activateMode
        self.activateMode = mode
        self.deactivateButtons()
        self.heal = heal
        self.trap = trap
        self.lure = lure
        self.bldg = bldg
        self.battleCreditLevel = creditLevel
        self.tutorialFlag = tutorialFlag
        self.gagTutMode = gagTutMode
        self.__activateButtons()
        self.enableUberGags()
        return None

    def setActivateModeBroke(self):
        if self.activateMode == 'storePurchase':
            self.setActivateMode('storePurchaseBroke')
        elif self.activateMode == 'purchase':
            self.setActivateMode('purchaseBroke', gagTutMode=self.gagTutMode)
        else:
            self.notify.error('Unexpected mode in setActivateModeBroke(): %s' % self.activateMode)
        self.enableUberGags()

    def deactivateButtons(self):
        self.cleanupDialog()
        if self.previousActivateMode == 'book':
            self.bookDeactivateButtons()
        elif self.previousActivateMode == 'bookDelete':
            self.bookDeleteDeactivateButtons()
        elif self.previousActivateMode == 'purchaseDelete':
            self.purchaseDeleteDeactivateButtons()
        elif self.previousActivateMode == 'purchase':
            self.purchaseDeactivateButtons()
        elif self.previousActivateMode == 'purchaseBroke':
            self.purchaseBrokeDeactivateButtons()
        elif self.previousActivateMode == 'gagTutDisabled':
            self.gagTutDisabledDeactivateButtons()
        elif self.previousActivateMode == 'battle':
            self.battleDeactivateButtons()
        elif self.previousActivateMode == 'storePurchaseDelete':
            self.storePurchaseDeleteDeactivateButtons()
        elif self.previousActivateMode == 'storePurchase':
            self.storePurchaseDeactivateButtons()
        elif self.previousActivateMode == 'storePurchaseBroke':
            self.storePurchaseBrokeDeactivateButtons()
        elif self.previousActivateMode == 'plantTree':
            self.plantTreeDeactivateButtons()
        else:
            self.notify.error('No such mode as %s' % self.previousActivateMode)
        return None

    def __activateButtons(self):
        self.cleanupDialog()
        if hasattr(self, 'activateMode'):
            if self.activateMode == 'book':
                self.bookActivateButtons()
            elif self.activateMode == 'bookDelete':
                self.bookDeleteActivateButtons()
            elif self.activateMode == 'purchaseDelete':
                self.purchaseDeleteActivateButtons()
            elif self.activateMode == 'purchase':
                self.purchaseActivateButtons()
            elif self.activateMode == 'purchaseBroke':
                self.purchaseBrokeActivateButtons()
            elif self.activateMode == 'gagTutDisabled':
                self.gagTutDisabledActivateButtons()
            elif self.activateMode == 'battle':
                self.battleActivateButtons()
            elif self.activateMode == 'storePurchaseDelete':
                self.storePurchaseDeleteActivateButtons()
            elif self.activateMode == 'storePurchase':
                self.storePurchaseActivateButtons()
            elif self.activateMode == 'storePurchaseBroke':
                self.storePurchaseBrokeActivateButtons()
            elif self.activateMode == 'plantTree':
                self.plantTreeActivateButtons()
            else:
                self.notify.error('No such mode as %s' % self.activateMode)
        return None

    def __applyBookDetailLayout(self):
                                                                      
                                                                    
        self.questionEmblem.setPos(0.0, 0, 0.26)
        self.questionEmblem.setScale(.82)
        self.gagEmblem.setPos(0.0, 0, 0.26)
        self.gagEmblem.setScale(.82)

                                                                           
                                                         
        self.detailNameLabel.setPos(0, 0, 0.12)
        self.detailNameLabel.setScale(0.085)
        self.detailNameLabel['text_pos'] = (0, -3.35)
        self.detailNameLabel['text_align'] = TextNode.ACenter

        self.detailAmountLabel.setPos(0, 0, -0.055)
        self.detailAmountLabel.setScale(0.064)
        self.detailAmountLabel['text_align'] = TextNode.ACenter

        self.detailDataLabel.setPos(0, 0, -0.265)
        self.detailDataLabel.setScale(0.064)
        self.detailDataLabel['text_align'] = TextNode.ACenter
        self.detailDataLabel['text_wordwrap'] = 18

        self.detailCreditLabel.setPos(0, 0, -0.525)
        self.detailCreditLabel.setScale(0.062)
        self.detailCreditLabel['text_align'] = TextNode.ACenter
        self.detailCreditLabel['text_wordwrap'] = 18

        self.totalLabel.setPos(0.0, 0, -0.12)
        self.totalLabel.setScale(0.09)
        self.totalLabel['text_align'] = TextNode.ACenter
        self.totalLabel['text_wordwrap'] = 0

    def __applyBattleDetailLayout(self):
                                                                          
        self.questionEmblem.setPos(-.0475, 0, 0.015)
        self.questionEmblem.setScale(.45)
        self.gagEmblem.setPos(-.0475, 0, 0.015)
        self.gagEmblem.setScale(.45)

        self.detailNameLabel.setPos(-.0475, 0, -.15)
        self.detailNameLabel.setScale(0.06)
        self.detailNameLabel['text_pos'] = (0, -0.25)
        self.detailNameLabel['text_align'] = TextNode.ACenter

        self.detailAmountLabel.setPos(-.0475, 0, -.25)
        self.detailAmountLabel.setScale(0.05)
        self.detailAmountLabel['text_align'] = TextNode.ACenter

        self.detailDataLabel.setPos(-.3175, 0, -.325)
        self.detailDataLabel.setScale(0.045)
        self.detailDataLabel['text_align'] = TextNode.ALeft
        self.detailDataLabel['text_wordwrap'] = 0

        self.detailCreditLabel.setPos(-.3175, 0, -.6)
        self.detailCreditLabel.setScale(0.045)
        self.detailCreditLabel['text_align'] = TextNode.ALeft
        self.detailCreditLabel['text_wordwrap'] = 0

        self.totalLabel.setPos(-.0475, 0, -0.23)
        self.totalLabel.setScale(0.07)
        self.totalLabel['text_align'] = TextNode.ACenter
        self.totalLabel['text_wordwrap'] = 0

    def bookActivateButtons(self):
        self.__applyBookDetailLayout()
        self.updateTotalPropsText()
        self.setPos(0.1, 0, 0.52)
        self.setScale(0.8)

                                                                               
                                                                            
                                                                             
                                                                    
        invPage = getattr(base.localAvatar, 'invPage', None)
        gagFrame = getattr(invPage, 'gagFrame', None)
        if gagFrame:
            self.detailFrame.reparentTo(gagFrame)
            self.detailFrame.setPos(0, 0, 0)
            self.detailFrame.setScale(0.92)
            self.detailFrame.setBin('gui-popup', 20)
        else:
                                                
            self.detailFrame.reparentTo(self.invFrame)
            self.detailFrame.setPos(0.1, 0, -0.355)
            self.detailFrame.setScale(0.75)
        self.deleteEnterButton.hide()
        self.deleteAllButton.hide()
        self.deleteExitButton.hide()
        self.invFrame.reparentTo(self)
        self.invFrame.setPos(0, 0, 0)
        self.invFrame.setScale(1)
        for track in range(len(Tracks)):
            if self.toon.hasTrackAccess(track):
                self.showTrack(track)
                for level in range(len(Levels[track])):
                    button = self.buttons[track][level]
                    if self.itemIsUsable(track, level):
                        button.show()
                        self.makeBookUnpressable(button, track, level)
                    else:
                        button.hide()

            else:
                self.hideTrack(track)

        return None

    def bookDeactivateButtons(self):
        self.deleteEnterButton['command'] = None

                                                                               
        self.detailFrame.reparentTo(self.invFrame)
        self.detailFrame.setBin('unsorted', 0)
        return

    def bookDeleteActivateButtons(self):
        messenger.send('enterBookDelete')
        self.setPos(-0.2, 0, 0.4)
        self.setScale(0.8)
        self.deleteEnterButton.hide()
        self.deleteEnterButton.setPos(1.00, 0, -0.639)
        self.deleteEnterButton.setScale(0.75)
        self.deleteExitButton.show()
        self.deleteExitButton.setPos(1.00, 0, -0.639)
        self.deleteExitButton.setScale(0.75)
        self.deleteHelpText.show()
        self.invFrame.reparentTo(self)
        self.invFrame.setPos(0, 0, 0)
        self.invFrame.setScale(1)
        self.deleteExitButton['command'] = self.setActivateMode
        self.deleteExitButton['extraArgs'] = [self.previousActivateMode]
        for track in range(len(Tracks)):
            if self.toon.hasTrackAccess(track):
                self.showTrack(track)
                for level in range(len(Levels[track])):
                    button = self.buttons[track][level]
                    if self.itemIsUsable(track, level):
                        button.show()
                        if self.numItem(track, level) <= 0:
                            self.makeUnpressable(button, track, level)
                        else:
                            self.makeDeletePressable(button, track, level)
                    else:
                        button.hide()

            else:
                self.hideTrack(track)

    def bookDeleteDeactivateButtons(self):
        messenger.send('exitBookDelete')
        self.deleteHelpText.hide()
        self.deleteDeactivateButtons()

    def purchaseDeleteActivateButtons(self):
        self.reparentTo(aspect2d)
        self.setPos(0.2, 0, -0.04)
        self.setScale(1)
        if self.purchaseFrame == None:
            self.loadPurchaseFrame()
        self.purchaseFrame.show()
        self.invFrame.reparentTo(self.purchaseFrame)
        self.invFrame.setPos(-0.235, 0, 0.52)
        self.invFrame.setScale(0.81)
        self.detailFrame.setPos(1.17, 0, -0.02)
        self.detailFrame.setScale(1.25)
        self.deleteEnterButton.hide()
        self.deleteEnterButton.setPos(-0.55, 0, -0.917)
        self.deleteEnterButton.setScale(0.75)
        self.deleteExitButton.show()
        self.deleteExitButton.setPos(-0.55, 0, -0.917)
        self.deleteExitButton.setScale(0.75)
        self.deleteExitButton['command'] = self.setActivateMode
        self.deleteExitButton['extraArgs'] = [self.previousActivateMode]
        for track in range(len(Tracks)):
            if self.toon.hasTrackAccess(track):
                self.showTrack(track)
                for level in range(len(Levels[track])):
                    button = self.buttons[track][level]
                    if self.itemIsUsable(track, level):
                        button.show()
                        if self.numItem(track, level) <= 0 or level >= UBER_GAG_LEVEL_INDEX:
                            self.makeUnpressable(button, track, level)
                        else:
                            self.makeDeletePressable(button, track, level)
                    else:
                        button.hide()

            else:
                self.hideTrack(track)

        return

    def purchaseDeleteDeactivateButtons(self):
        self.invFrame.reparentTo(self)
        self.purchaseFrame.hide()
        self.deleteDeactivateButtons()
        for track in range(len(Tracks)):
            if self.toon.hasTrackAccess(track):
                self.showTrack(track)
                for level in range(len(Levels[track])):
                    button = self.buttons[track][level]
                    if self.itemIsUsable(track, level):
                        button.show()
                        if self.numItem(track, level) <= 0 or level >= UBER_GAG_LEVEL_INDEX:
                            self.makeUnpressable(button, track, level)
                        else:
                            self.makeDeletePressable(button, track, level)
                    else:
                        button.hide()

            else:
                self.hideTrack(track)

    def storePurchaseDeleteActivateButtons(self):
        self.reparentTo(aspect2d)
        self.setPos(0.2, 0, -0.04)
        self.setScale(1)
        if self.storePurchaseFrame == None:
            self.loadStorePurchaseFrame()
        self.storePurchaseFrame.show()
        self.invFrame.reparentTo(self.storePurchaseFrame)
        self.invFrame.setPos(-0.23, 0, 0.505)
        self.invFrame.setScale(0.81)
        self.detailFrame.setPos(1.175, 0, 0)
        self.detailFrame.setScale(1.25)
        self.deleteEnterButton.hide()
        self.deleteEnterButton.setPos(-0.55, 0, -0.91)
        self.deleteEnterButton.setScale(0.75)
        self.deleteExitButton.show()
        self.deleteExitButton.setPos(-0.55, 0, -0.91)
        self.deleteExitButton.setScale(0.75)
        self.deleteExitButton['command'] = self.setActivateMode
        self.deleteExitButton['extraArgs'] = [self.previousActivateMode]
        for track in range(len(Tracks)):
            if self.toon.hasTrackAccess(track):
                self.showTrack(track)
                for level in range(len(Levels[track])):
                    button = self.buttons[track][level]
                    if self.itemIsUsable(track, level):
                        button.show()
                        if self.numItem(track, level) <= 0 or level >= UBER_GAG_LEVEL_INDEX:
                            self.makeUnpressable(button, track, level)
                        else:
                            self.makeDeletePressable(button, track, level)
                    else:
                        button.hide()

            else:
                self.hideTrack(track)

        return

    def storePurchaseDeleteDeactivateButtons(self):
        self.invFrame.reparentTo(self)
        self.storePurchaseFrame.hide()
        self.deleteDeactivateButtons()

    def storePurchaseBrokeActivateButtons(self):
        self.reparentTo(aspect2d)
        self.setPos(0.2, 0, -0.04)
        self.setScale(1)
        if self.storePurchaseFrame == None:
            self.loadStorePurchaseFrame()
        self.storePurchaseFrame.show()
        self.invFrame.reparentTo(self.storePurchaseFrame)
        self.invFrame.setPos(-0.23, 0, 0.505)
        self.invFrame.setScale(0.81)
        self.detailFrame.setPos(1.175, 0, 0)
        self.detailFrame.setScale(1.25)
        self.deleteAllButton.show()
        self.deleteEnterButton.show()
        self.deleteEnterButton.setPos(-0.55, 0, -0.91)
        self.deleteEnterButton.setScale(0.75)
        self.deleteExitButton.hide()
        self.deleteExitButton.setPos(-0.55, 0, -0.91)
        self.deleteExitButton.setScale(0.75)
        for track in range(len(Tracks)):
            if self.toon.hasTrackAccess(track):
                self.showTrack(track)
                for level in range(len(Levels[track])):
                    button = self.buttons[track][level]
                    if self.itemIsUsable(track, level):
                        button.show()
                        self.makeUnpressable(button, track, level)
                    else:
                        button.hide()

            else:
                self.hideTrack(track)

        return

    def storePurchaseBrokeDeactivateButtons(self):
        self.invFrame.reparentTo(self)
        self.storePurchaseFrame.hide()

    def deleteActivateButtons(self):
        self.reparentTo(aspect2d)
        self.setPos(0, 0, 0)
        self.setScale(1)
        self.deleteEnterButton.hide()
        self.deleteExitButton.show()
        self.deleteExitButton['command'] = self.setActivateMode
        self.deleteExitButton['extraArgs'] = [self.previousActivateMode]
        for track in range(len(Tracks)):
            if self.toon.hasTrackAccess(track):
                self.showTrack(track)
                for level in range(len(Levels[track])):
                    button = self.buttons[track][level]
                    if self.itemIsUsable(track, level):
                        button.show()
                        if self.numItem(track, level) <= 0:
                            self.makeUnpressable(button, track, level)
                        else:
                            self.makePressable(button, track, level)
                    else:
                        button.hide()

            else:
                self.hideTrack(track)

        return None

    def deleteDeactivateButtons(self):
        self.deleteExitButton['command'] = None
        return

    def purchaseActivateButtons(self):
        self.reparentTo(aspect2d)
        self.setPos(0.2, 0, -0.04)
        self.setScale(1)
        if self.purchaseFrame == None:
            self.loadPurchaseFrame()
        self.purchaseFrame.show()
        self.invFrame.reparentTo(self.purchaseFrame)
        self.invFrame.setPos(-0.235, 0, 0.52)
        self.invFrame.setScale(0.81)
        self.detailFrame.setPos(1.17, 0, -0.02)
        self.detailFrame.setScale(1.25)
        totalProps = self.totalProps
        maxProps = self.toon.getMaxCarry()
        self.deleteAllButton.show()
        self.deleteEnterButton.show()
        self.deleteEnterButton.setPos(-0.55, 0, -0.917)
        self.deleteEnterButton.setScale(0.75)
        self.deleteExitButton.hide()
        self.deleteExitButton.setPos(-0.55, 0, -0.917)
        self.deleteExitButton.setScale(0.75)
        if self.gagTutMode:
            self.deleteAllButton.hide()
            self.deleteEnterButton.hide()
        self.deleteEnterButton['command'] = self.setActivateMode
        self.deleteEnterButton['extraArgs'] = ['purchaseDelete']
        for track in range(len(Tracks)):
            if self.toon.hasTrackAccess(track):
                self.showTrack(track)
                for level in range(len(Levels[track])):
                    button = self.buttons[track][level]
                    if self.itemIsUsable(track, level):
                        button.show()
                        unpaid = not base.cr.isPaid()
                        if self.numItem(track, level) >= self.getMax(track, level) or totalProps == maxProps or unpaid and gagIsPaidOnly(track, level) or level > LAST_REGULAR_GAG_LEVEL:
                            if gagIsPaidOnly(track, level):
                                self.makeUnpressable(button, track, level)
                            elif unpaid and gagIsVelvetRoped(track, level):
                                self.makeUnpressable(button, track, level)
                            else:
                                self.makeUnpressable(button, track, level)
                        elif base.localAvatar.getMoney() < (level + 1):
                            self.makeUnpressable(button, track, level)
                        elif unpaid and gagIsVelvetRoped(track, level):
                            self.makeUnpressable(button, track, level)
                        else:
                            self.makePressable(button, track, level)
                    else:
                        button.hide()

            else:
                self.hideTrack(track)

        return

    def purchaseDeactivateButtons(self):
        self.invFrame.reparentTo(self)
        self.purchaseFrame.hide()

    def storePurchaseActivateButtons(self):
        self.reparentTo(aspect2d)
        self.setPos(0.2, 0, -0.04)
        self.setScale(1)
        if self.storePurchaseFrame == None:
            self.loadStorePurchaseFrame()
        self.storePurchaseFrame.show()
        self.invFrame.reparentTo(self.storePurchaseFrame)
        self.invFrame.setPos(-0.23, 0, 0.505)
        self.invFrame.setScale(0.81)
        self.detailFrame.setPos(1.175, 0, 0)
        self.detailFrame.setScale(1.25)
        totalProps = self.totalProps
        maxProps = self.toon.getMaxCarry()
        self.deleteAllButton.show()
        self.deleteEnterButton.show()
        self.deleteEnterButton.setPos(-0.55, 0, -0.91)
        self.deleteEnterButton.setScale(0.75)
        self.deleteExitButton.hide()
        self.deleteExitButton.setPos(-0.55, 0, -0.91)
        self.deleteExitButton.setScale(0.75)
        self.deleteEnterButton['command'] = self.setActivateMode
        self.deleteEnterButton['extraArgs'] = ['storePurchaseDelete']
        for track in range(len(Tracks)):
            if self.toon.hasTrackAccess(track):
                self.showTrack(track)
                for level in range(len(Levels[track])):
                    button = self.buttons[track][level]
                    if self.itemIsUsable(track, level):
                        button.show()
                        unpaid = not base.cr.isPaid()
                        if self.numItem(track, level) >= self.getMax(track, level) or totalProps == maxProps or unpaid and gagIsPaidOnly(track, level) or level > LAST_REGULAR_GAG_LEVEL:
                            if gagIsPaidOnly(track, level):
                                self.makeDisabledPressable(button, track, level)
                            elif unpaid and gagIsVelvetRoped(track, level):
                                self.makeDisabledPressable(button, track, level)
                            else:
                                self.makeUnpressable(button, track, level)
                        elif base.localAvatar.getMoney() < (level + 1):
                            self.makeUnpressable(button, track, level)
                        elif unpaid and gagIsVelvetRoped(track, level):
                            self.makeDisabledPressable(button, track, level)
                        else:
                            self.makePressable(button, track, level)
                    else:
                        button.hide()

            else:
                self.hideTrack(track)

        return

    def storePurchaseDeactivateButtons(self):
        self.invFrame.reparentTo(self)
        self.storePurchaseFrame.hide()

    def purchaseBrokeActivateButtons(self):
        self.reparentTo(aspect2d)
        self.setPos(0.2, 0, -0.04)
        self.setScale(1)
        if self.purchaseFrame == None:
            self.loadPurchaseFrame()
        self.purchaseFrame.show()
        self.invFrame.reparentTo(self.purchaseFrame)
        self.invFrame.setPos(-0.235, 0, 0.52)
        self.invFrame.setScale(0.81)
        self.detailFrame.setPos(1.17, 0, -0.02)
        self.detailFrame.setScale(1.25)
        self.deleteAllButton.show()
        self.deleteEnterButton.show()
        self.deleteEnterButton.setPos(-0.55, 0, -0.917)
        self.deleteEnterButton.setScale(0.75)
        self.deleteExitButton.hide()
        self.deleteExitButton.setPos(-0.55, 0, -0.917)
        self.deleteExitButton.setScale(0.75)
        if self.gagTutMode:
            self.deleteEnterButton.hide()
        for track in range(len(Tracks)):
            if self.toon.hasTrackAccess(track):
                self.showTrack(track)
                for level in range(len(Levels[track])):
                    button = self.buttons[track][level]
                    if self.itemIsUsable(track, level):
                        button.show()
                        if not self.gagTutMode:
                            self.makeUnpressable(button, track, level)
                    else:
                        button.hide()

            else:
                self.hideTrack(track)

        return

    def purchaseBrokeDeactivateButtons(self):
        self.invFrame.reparentTo(self)
        self.purchaseFrame.hide()

    def gagTutDisabledActivateButtons(self):
        self.reparentTo(aspect2d)
        self.setPos(0.2, 0, -0.04)
        self.setScale(1)
        if self.purchaseFrame == None:
            self.loadPurchaseFrame()
        self.purchaseFrame.show()
        self.invFrame.reparentTo(self.purchaseFrame)
        self.invFrame.setPos(-0.235, 0, 0.52)
        self.invFrame.setScale(0.81)
        self.detailFrame.setPos(1.17, 0, -0.02)
        self.detailFrame.setScale(1.25)
        self.deleteExitButton.hide()
        self.deleteEnterButton.hide()
        self.deleteAllButton.hide()

    def gagTutDisabledDeactivateButtons(self):
        self.invFrame.reparentTo(self)
        self.purchaseFrame.hide()

    def isSpecificGagBanned(self, track, level):
        return 'noGag_%s_%s' % (track, level) in base.localAvatar.battleConditions

    def battleActivateButtons(self):
        self.__applyBattleDetailLayout()
        self.applyDisplayTrackOrder()
        self.updateTotalPropsText()
        self.stopAndClearPropBonusIval()
        self.reparentTo(aspect2d)
        self.setPos(0.1, 0, 0)
        self.setScale(0.9)
        if self.battleFrame == None:
            self.loadBattleFrame()
        self.battleFrame.show()
        self.battleFrame.setScale(0.9)
        self.invFrame.reparentTo(self.battleFrame)
        self.invFrame.setPos(-0.26, 0, 0.35)
        self.invFrame.setScale(1)
        self.detailFrame.setPos(1.125, 0, -0.08)
        self.detailFrame.setScale(1)
        self.deleteAllButton.hide()
        self.deleteEnterButton.hide()
        self.deleteExitButton.hide()
        if self.bldg == 1:
            self.runButton.hide()
            self.sosButton.show()
            self.passButton.show()
            self.levelsButton.show()
        elif self.tutorialFlag == 1:
            self.runButton.hide()
            self.sosButton.hide()
            self.passButton.hide()
            self.fireButton.hide()
            self.levelsButton.hide()
        else:
            self.runButton.show()
            self.sosButton.show()
            self.passButton.show()
            self.fireButton.show()
            self.sueButton.show()
            self.levelsButton.show()
            if localAvatar.getPinkSlips() > 0:
                self.fireButton['state'] = DGG.NORMAL
            else:
                self.fireButton['state'] = DGG.DISABLED
            if localAvatar.getCeaseAndDesists() > 0:
                self.sueButton['state'] = DGG.NORMAL
            else:
                self.sueButton['state'] = DGG.DISABLED
                                                                                                                    
        if not 'noSues' in base.localAvatar.battleConditions:
            self.sueButton['state'] = DGG.NORMAL
        if not 'noFires' in base.localAvatar.battleConditions:
            self.fireButton['state'] = DGG.NORMAL
        if not 'noSOS' in base.localAvatar.battleConditions:
            self.sosButton['state'] = DGG.NORMAL
        if 'noFires' in base.localAvatar.battleConditions or localAvatar.cooldown:
            self.fireButton['state'] = DGG.DISABLED
        if 'noSues' in base.localAvatar.battleConditions or localAvatar.cooldown:
            self.sueButton['state'] = DGG.DISABLED
        if 'noSOS' in base.localAvatar.battleConditions or localAvatar.cooldown:
            self.sosButton['state'] = DGG.DISABLED
        if settings.get('show-cog-levels', True):
            self.levelsButton['text'] = TTLocalizer.InventoryLevelsHide
        else:
            self.levelsButton['text'] = TTLocalizer.InventoryLevelsShow
        for track in range(len(Tracks)):
            if self.toon.hasTrackAccess(track):
                self.showTrack(track)
                for level in range(len(Levels[track])):
                    button = self.buttons[track][level]
                    if self.itemIsUsable(track, level):
                        unpaid = not base.cr.isPaid()
                        button.show()
                        if self.itemIsCredit(track, level):
                            self.makePressable(button, track, level)
                        else:
                            self.makeNoncreditPressable(button, track, level)

                        if 'raisedAnte' in base.localAvatar.battleConditions and not self.numItem(
                                track, level) <= 0:
                            if base.localAvatar.battleConditions['raisedAnte'][0] > 0.0:
                                if not self.numItem(track, level) <= 0:
                                    self.makeDamageUpPressable(button, track, level)
                        if 'raisedAnte' in base.localAvatar.battleConditions and not self.numItem(
                                track, level) <= 0:
                            if base.localAvatar.battleConditions['raisedAnte'][0] < 0.0:
                                if not self.numItem(track, level) <= 0:
                                    self.makeDamageDownPressable(button, track, level)
                        if 'governaughtBoost' in base.localAvatar.battleConditions and not self.numItem(
                                track, level) <= 0:
                            if base.localAvatar.battleConditions['governaughtBoost'][0] > 0.0:
                                if not self.numItem(track, level) <= 0:
                                    self.makeDamageUpPressable(button, track, level)
                        if 'governaughtBoost' in base.localAvatar.battleConditions and not self.numItem(
                                track, level) <= 0:
                            if base.localAvatar.battleConditions['governaughtBoost'][0] < 0.0:
                                if not self.numItem(track, level) <= 0:
                                    self.makeDamageDownPressable(button, track, level)
                        if 'allGagBoost' in base.localAvatar.battleConditions and not self.numItem(
                                track, level) <= 0:
                            if base.localAvatar.battleConditions['allGagBoost'][0] > 0.0:
                                if not self.numItem(track, level) <= 0:
                                    self.makeDamageUpPressable(button, track, level)
                        if 'viralSensation' in base.localAvatar.battleConditions and not self.numItem(
                                track, level) <= 0:
                            if base.localAvatar.battleConditions['viralSensation'][0] > 0.0:
                                if not self.numItem(track, level) <= 0:
                                    self.makeDamageUpPressable(button, track, level)
                        if 'energized' in base.localAvatar.battleConditions and not self.numItem(
                                track, level) <= 0:
                            if base.localAvatar.battleConditions['energized'][0] > 0.0:
                                if not self.numItem(track, level) <= 0:
                                    self.makeDamageUpPressable(button, track, level)
                        if 'allGagBoost' in base.localAvatar.battleConditions and not self.numItem(
                                track, level) <= 0:
                            if base.localAvatar.battleConditions['allGagBoost'][0] < 0.0:
                                if not self.numItem(track, level) <= 0:
                                    self.makeDamageDownPressable(button, track, level)
                        if 'lureBoost' in base.localAvatar.battleConditions and not self.numItem(
                                track, level) <= 0 and track == LURE_TRACK:
                            if base.localAvatar.battleConditions['lureBoost'][0] > 0.0:
                                if not self.numItem(track, level) <= 0:
                                    self.makeDamageUpPressable(button, track, level)
                        if 'lureBoost' in base.localAvatar.battleConditions and not self.numItem(
                                track, level) <= 0:
                            if base.localAvatar.battleConditions['lureBoost'][0] < 0.0:
                                if not self.numItem(track, level) <= 0 and track == LURE_TRACK:
                                    self.makeDamageDownPressable(button, track, level)
                        if 'allGagBoost2' in base.localAvatar.battleConditions and not self.numItem(
                                track, level) <= 0:
                            if base.localAvatar.battleConditions['allGagBoost2'][0] > 0.0:
                                if not self.numItem(track, level) <= 0:
                                    self.makeDamageUpPressable(button, track, level)
                        if 'allGagBoost2' in base.localAvatar.battleConditions and not self.numItem(
                                track, level) <= 0:
                            if base.localAvatar.battleConditions['allGagBoost2'][0] < 0.0:
                                if not self.numItem(track, level) <= 0:
                                    self.makeDamageDownPressable(button, track, level)
                        if 'lureBoost2' in base.localAvatar.battleConditions and not self.numItem(
                                track, level) <= 0 and track == LURE_TRACK:
                            if base.localAvatar.battleConditions['lureBoost2'][0] > 0.0:
                                if not self.numItem(track, level) <= 0:
                                    self.makeDamageUpPressable(button, track, level)
                        if 'lureBoost2' in base.localAvatar.battleConditions and not self.numItem(
                                track, level) <= 0:
                            if base.localAvatar.battleConditions['lureBoost2'][0] < 0.0:
                                if not self.numItem(track, level) <= 0 and track == LURE_TRACK:
                                    self.makeDamageDownPressable(button, track, level)
                        if 'healBoost' in base.localAvatar.battleConditions and not self.numItem(
                                track, level) <= 0:
                            if base.localAvatar.battleConditions['healBoost'][0] > 0.0:
                                if not self.numItem(track, level) <= 0 and track == HEAL_TRACK:
                                    self.makeDamageUpPressable(button, track, level)
                        if 'healBoost' in base.localAvatar.battleConditions and not self.numItem(
                                track, level) <= 0:
                            if base.localAvatar.battleConditions['healBoost'][0] < 0.0:
                                if not self.numItem(track, level) <= 0 and track == HEAL_TRACK:
                                    self.makeDamageDownPressable(button, track, level)
                        if 'trapBoost' in base.localAvatar.battleConditions and not self.numItem(
                                track, level) <= 0:
                            if base.localAvatar.battleConditions['trapBoost'][0] > 0.0:
                                if not self.numItem(track, level) <= 0 and track == TRAP_TRACK:
                                    self.makeDamageUpPressable(button, track, level)
                        if 'trapBoost' in base.localAvatar.battleConditions and not self.numItem(
                                track, level) <= 0:
                            if base.localAvatar.battleConditions['trapBoost'][0] < 0.0:
                                if not self.numItem(track, level) <= 0 and track == TRAP_TRACK:
                                    self.makeDamageDownPressable(button, track, level)
                        if 'throwBoost' in base.localAvatar.battleConditions and not self.numItem(
                                track, level) <= 0:
                            if base.localAvatar.battleConditions['throwBoost'][0] > 0.0:
                                if not self.numItem(track, level) <= 0 and track == THROW_TRACK:
                                    self.makeDamageUpPressable(button, track, level)
                        if 'throwBoost' in base.localAvatar.battleConditions and not self.numItem(
                                track, level) <= 0:
                            if base.localAvatar.battleConditions['throwBoost'][0] < 0.0:
                                if not self.numItem(track, level) <= 0 and track == THROW_TRACK:
                                    self.makeDamageDownPressable(button, track, level)
                        if 'squirtBoost' in base.localAvatar.battleConditions and not self.numItem(
                                track, level) <= 0:
                            if base.localAvatar.battleConditions['squirtBoost'][0] > 0.0:
                                if not self.numItem(track, level) <= 0 and track == SQUIRT_TRACK:
                                    self.makeDamageUpPressable(button, track, level)
                        if 'squirtBoost' in base.localAvatar.battleConditions and not self.numItem(
                                track, level) <= 0:
                            if base.localAvatar.battleConditions['squirtBoost'][0] < 0.0:
                                if not self.numItem(track, level) <= 0 and track == SQUIRT_TRACK:
                                    self.makeDamageDownPressable(button, track, level)
                        if 'dropBoost' in base.localAvatar.battleConditions and not self.numItem(
                                track, level) <= 0:
                            if base.localAvatar.battleConditions['dropBoost'][0] > 0.0:
                                if not self.numItem(track, level) <= 0 and track == DROP_TRACK:
                                    self.makeDamageUpPressable(button, track, level)
                        if 'dropBoost' in base.localAvatar.battleConditions and not self.numItem(
                                track, level) <= 0:
                            if base.localAvatar.battleConditions['dropBoost'][0] < 0.0:
                                if not self.numItem(track, level) <= 0 and track == DROP_TRACK:
                                    self.makeDamageDownPressable(button, track, level)
                        if 'soundBoost' in base.localAvatar.battleConditions and not self.numItem(
                                track, level) <= 0:
                            if base.localAvatar.battleConditions['soundBoost'][0] > 0.0:
                                if not self.numItem(track, level) <= 0 and track == SOUND_TRACK:
                                    self.makeDamageUpPressable(button, track, level)
                        if 'soundBoost' in base.localAvatar.battleConditions and not self.numItem(
                                track, level) <= 0:
                            if base.localAvatar.battleConditions['soundBoost'][0] < 0.0:
                                if not self.numItem(track, level) <= 0 and track == SOUND_TRACK:
                                    self.makeDamageDownPressable(button, track, level)
                        if 'zapBoost' in base.localAvatar.battleConditions and not self.numItem(
                                track, level) <= 0:
                            if base.localAvatar.battleConditions['zapBoost'][0] > 0.0:
                                if not self.numItem(track, level) <= 0 and track == ZAP_TRACK:
                                    self.makeDamageUpPressable(button, track, level)
                        if 'zapBoost' in base.localAvatar.battleConditions and not self.numItem(
                                track, level) <= 0:
                            if base.localAvatar.battleConditions['zapBoost'][0] < 0.0:
                                if not self.numItem(track, level) <= 0 and track == ZAP_TRACK:
                                    self.makeDamageDownPressable(button, track, level)
                        if 'encore2' in base.localAvatar.battleConditions and not self.numItem(
                                track, level) <= 0:
                            self.makeDamageUpPressable(button, track, level)
                        if 'encore' in base.localAvatar.battleConditions and not self.numItem(
                                track, level) <= 0:
                            self.makeDamageUpPressable(button, track, level)
                        if track == SOUND_TRACK and 'winded' in base.localAvatar.battleConditions and not self.numItem(
                                track, level) <= 0:
                            self.makeDamageDownPressable(button, track, level)
                        if track == SOUND_TRACK and 'groupDamageDown' in base.localAvatar.battleConditions and not self.numItem(
                                track, level) <= 0:
                            self.makeDamageDownPressable(button, track, level)
                        if track == SQUIRT_TRACK and 'groupDamageDown' in base.localAvatar.battleConditions and not self.numItem(
                                track, level) <= 0:
                            self.makeDamageDownPressable(button, track, level)
                        if track == ZAP_TRACK and 'groupDamageDown' in base.localAvatar.battleConditions and not self.numItem(
                                track, level) <= 0:
                            self.makeDamageDownPressable(button, track, level)
                        if track == HEAL_TRACK and 'groupDamageDown' in base.localAvatar.battleConditions and level == 7 and not self.numItem(
                                track, level) <= 0:
                            self.makeDamageDownPressable(button, track, level)
                        if track == HEAL_TRACK and 'groupDamageDown' in base.localAvatar.battleConditions and level == 5 and not self.numItem(
                                track, level) <= 0:
                            self.makeDamageDownPressable(button, track, level)
                        if track == HEAL_TRACK and 'groupDamageDown' in base.localAvatar.battleConditions and level == 3 and not self.numItem(
                                track, level) <= 0:
                            self.makeDamageDownPressable(button, track, level)
                        if track == HEAL_TRACK and 'groupDamageDown' in base.localAvatar.battleConditions and level == 1 and not self.numItem(
                                track, level) <= 0:
                            self.makeDamageDownPressable(button, track, level)
                        if track == LURE_TRACK and 'groupDamageDown' in base.localAvatar.battleConditions and level == 7 and not self.numItem(
                                track, level) <= 0:
                            self.makeDamageDownPressable(button, track, level)
                        if track == LURE_TRACK and 'groupDamageDown' in base.localAvatar.battleConditions and level == 5 and not self.numItem(
                                track, level) <= 0:
                            self.makeDamageDownPressable(button, track, level)
                        if track == LURE_TRACK and 'groupDamageDown' in base.localAvatar.battleConditions and level == 3 and not self.numItem(
                                track, level) <= 0:
                            self.makeDamageDownPressable(button, track, level)
                        if track == LURE_TRACK and 'groupDamageDown' in base.localAvatar.battleConditions and level == 1 and not self.numItem(
                                track, level) <= 0:
                            self.makeDamageDownPressable(button, track, level)
                        if 'noGags' in base.localAvatar.battleConditions and not (self.numItem(track, level) <= 0):
                            self.makeBannablePressable(button, track, level)
                        if track == DROP_TRACK and 'noDropGags' in base.localAvatar.battleConditions and not \
                                (self.numItem(track,
                                              level) <= 0 or track == HEAL_TRACK and not self.heal or track == TRAP_TRACK and not self.trap or track == LURE_TRACK and not self.lure):
                            self.makeBannablePressable(button, track, level)
                        if track == HEAL_TRACK and 'useToonUp' in base.localAvatar.battleConditions and not \
                                (self.numItem(track, level) <= 0 or track == HEAL_TRACK and not self.heal or track == TRAP_TRACK and not self.trap or track == LURE_TRACK and not self.lure):
                            self.makeRushJobPressable(button, track, level)
                        if track == TRAP_TRACK and 'useTrap' in base.localAvatar.battleConditions and not \
                                (self.numItem(track, level) <= 0 or track == HEAL_TRACK and not self.heal or track == TRAP_TRACK and not self.trap or track == LURE_TRACK and not self.lure):
                            self.makeRushJobPressable(button, track, level)
                        if track == LURE_TRACK and 'useLure' in base.localAvatar.battleConditions and not \
                                (self.numItem(track, level) <= 0 or track == HEAL_TRACK and not self.heal or track == TRAP_TRACK and not self.trap or track == LURE_TRACK and not self.lure):
                            self.makeRushJobPressable(button, track, level)
                        if track == SOUND_TRACK and 'useSound' in base.localAvatar.battleConditions and not \
                                (self.numItem(track, level) <= 0 or track == HEAL_TRACK and not self.heal or track == TRAP_TRACK and not self.trap or track == LURE_TRACK and not self.lure):
                            self.makeRushJobPressable(button, track, level)
                        if track == THROW_TRACK and 'useThrow' in base.localAvatar.battleConditions and not \
                                (self.numItem(track, level) <= 0 or track == HEAL_TRACK and not self.heal or track == TRAP_TRACK and not self.trap or track == LURE_TRACK and not self.lure):
                            self.makeRushJobPressable(button, track, level)
                        if track == SQUIRT_TRACK and 'useSquirt' in base.localAvatar.battleConditions and not \
                                (self.numItem(track, level) <= 0 or track == HEAL_TRACK and not self.heal or track == TRAP_TRACK and not self.trap or track == LURE_TRACK and not self.lure):
                            self.makeRushJobPressable(button, track, level)
                        if track == ZAP_TRACK and 'useZap' in base.localAvatar.battleConditions and not \
                                (self.numItem(track, level) <= 0 or track == HEAL_TRACK and not self.heal or track == TRAP_TRACK and not self.trap or track == LURE_TRACK and not self.lure):
                            self.makeRushJobPressable(button, track, level)
                        if track == DROP_TRACK and 'useDrop' in base.localAvatar.battleConditions and not \
                                (self.numItem(track,
                                              level) <= 0 or track == HEAL_TRACK and not self.heal or track == TRAP_TRACK and not self.trap or track == LURE_TRACK and not self.lure):
                            self.makeRushJobPressable(button, track, level)
                        if self.isSpecificGagBanned(track, level):
                            self.makeBannablePressable(button, track, level)
                        if track == HEAL_TRACK and 'noToonUpGags' in base.localAvatar.battleConditions and not \
                                (self.numItem(track, level) <= 0 or track == HEAL_TRACK and not self.heal or track == TRAP_TRACK and not self.trap or track == LURE_TRACK and not self.lure):
                            self.makeBannablePressable(button, track, level)
                        if track == TRAP_TRACK and 'noTrapGags' in base.localAvatar.battleConditions and not \
                                (self.numItem(track, level) <= 0 or track == HEAL_TRACK and not self.heal or track == TRAP_TRACK and not self.trap or track == LURE_TRACK and not self.lure):
                            self.makeBannablePressable(button, track, level)
                        if track == LURE_TRACK and 'noLureGags' in base.localAvatar.battleConditions and not \
                                (self.numItem(track, level) <= 0 or track == HEAL_TRACK and not self.heal or track == TRAP_TRACK and not self.trap or track == LURE_TRACK and not self.lure):
                            self.makeBannablePressable(button, track, level)
                        if track == SOUND_TRACK and 'noSoundGags' in base.localAvatar.battleConditions and not \
                                (self.numItem(track, level) <= 0 or track == HEAL_TRACK and not self.heal or track == TRAP_TRACK and not self.trap or track == LURE_TRACK and not self.lure):
                            self.makeBannablePressable(button, track, level)
                        if track == THROW_TRACK and 'noThrowGags' in base.localAvatar.battleConditions and not \
                                (self.numItem(track, level) <= 0 or track == HEAL_TRACK and not self.heal or track == TRAP_TRACK and not self.trap or track == LURE_TRACK and not self.lure):
                            self.makeBannablePressable(button, track, level)
                        if track == SQUIRT_TRACK and 'noSquirtGags' in base.localAvatar.battleConditions and not \
                                (self.numItem(track, level) <= 0 or track == HEAL_TRACK and not self.heal or track == TRAP_TRACK and not self.trap or track == LURE_TRACK and not self.lure):
                            self.makeBannablePressable(button, track, level)
                        if track == ZAP_TRACK and 'noZapGags' in base.localAvatar.battleConditions and not \
                                (self.numItem(track, level) <= 0 or track == HEAL_TRACK and not self.heal or track == TRAP_TRACK and not self.trap or track == LURE_TRACK and not self.lure):
                            self.makeBannablePressable(button, track, level)
                        if level == 7 and 'nolevel8s' in base.localAvatar.battleConditions and not \
                                (self.numItem(track, level) <= 0 or track == HEAL_TRACK and not self.heal or track == TRAP_TRACK and not self.trap or track == LURE_TRACK and not self.lure):
                            self.makeBannablePressable(button, track, level)
                        if level == 3 and 'nolevel4s' in base.localAvatar.battleConditions and not \
                                (self.numItem(track, level) <= 0 or track == HEAL_TRACK and not self.heal or track == TRAP_TRACK and not self.trap or track == LURE_TRACK and not self.lure):
                            self.makeBannablePressable(button, track, level)
                        if level == 4 and 'nolevel5s' in base.localAvatar.battleConditions and not \
                                (self.numItem(track, level) <= 0 or track == HEAL_TRACK and not self.heal or track == TRAP_TRACK and not self.trap or track == LURE_TRACK and not self.lure):
                            self.makeBannablePressable(button, track, level)
                        if level == 5 and 'nolevel6s' in base.localAvatar.battleConditions and not \
                                (self.numItem(track, level) <= 0 or track == HEAL_TRACK and not self.heal or track == TRAP_TRACK and not self.trap or track == LURE_TRACK and not self.lure):
                            self.makeBannablePressable(button, track, level)
                        if level == 6 and 'nolevel7s' in base.localAvatar.battleConditions and not \
                                (self.numItem(track, level) <= 0 or track == HEAL_TRACK and not self.heal or track == TRAP_TRACK and not self.trap or track == LURE_TRACK and not self.lure):
                            self.makeBannablePressable(button, track, level)
                        if track == DROP_TRACK and 'noDropGags' in base.localAvatar.battleConditions and not \
                                (self.numItem(track,
                                              level) <= 0 or track == HEAL_TRACK and not self.heal or track == TRAP_TRACK and not self.trap or track == LURE_TRACK and not self.lure):
                            self.makeBannablePressable(button, track, level)
                        if track == SOUND_TRACK and 'confused' in base.localAvatar.battleConditions and not self.numItem(
                                track, level) <= 0:
                            self.makeUnpressable(button, track, level)
                        if track == ZAP_TRACK and 'confused' in base.localAvatar.battleConditions and not self.numItem(
                                track, level) <= 0:
                            self.makeUnpressable(button, track, level)
                        if track == HEAL_TRACK and 'confused' in base.localAvatar.battleConditions and level == 7 and not self.numItem(
                                track, level) <= 0:
                            self.makeUnpressable(button, track, level)
                        if track == HEAL_TRACK and 'confused' in base.localAvatar.battleConditions and level == 5 and not self.numItem(
                                track, level) <= 0:
                            self.makeUnpressable(button, track, level)
                        if track == HEAL_TRACK and 'confused' in base.localAvatar.battleConditions and level == 3 and not self.numItem(
                                track, level) <= 0:
                            self.makeUnpressable(button, track, level)
                        if track == HEAL_TRACK and 'confused' in base.localAvatar.battleConditions and level == 1 and not self.numItem(
                                track, level) <= 0:
                            self.makeUnpressable(button, track, level)
                        if track == LURE_TRACK and 'confused' in base.localAvatar.battleConditions and level == 7 and not self.numItem(
                                track, level) <= 0:
                            self.makeUnpressable(button, track, level)
                        if track == LURE_TRACK and 'confused' in base.localAvatar.battleConditions and level == 5 and not self.numItem(
                                track, level) <= 0:
                            self.makeUnpressable(button, track, level)
                        if track == LURE_TRACK and 'confused' in base.localAvatar.battleConditions and level == 3 and not self.numItem(
                                track, level) <= 0:
                            self.makeUnpressable(button, track, level)
                        if track == LURE_TRACK and 'confused' in base.localAvatar.battleConditions and level == 1 and not self.numItem(
                                track, level) <= 0:
                            self.makeUnpressable(button, track, level)
                        if track == HEAL_TRACK and 'disableToonUp' in base.localAvatar.battleConditions and not \
                                (self.numItem(track, level) <= 0 or track == HEAL_TRACK and not self.heal or track == TRAP_TRACK and not self.trap or track == LURE_TRACK and not self.lure):
                            self.makeUnpressable(button, track, level)
                        if track == TRAP_TRACK and 'disableTrap' in base.localAvatar.battleConditions and not \
                                (self.numItem(track, level) <= 0 or track == HEAL_TRACK and not self.heal or track == TRAP_TRACK and not self.trap or track == LURE_TRACK and not self.lure):
                            self.makeUnpressable(button, track, level)
                        if track == LURE_TRACK and 'disableLure' in base.localAvatar.battleConditions and not \
                                (self.numItem(track, level) <= 0 or track == HEAL_TRACK and not self.heal or track == TRAP_TRACK and not self.trap or track == LURE_TRACK and not self.lure):
                            self.makeUnpressable(button, track, level)
                        if track == SOUND_TRACK and 'disableSound' in base.localAvatar.battleConditions and not \
                                (self.numItem(track, level) <= 0 or track == HEAL_TRACK and not self.heal or track == TRAP_TRACK and not self.trap or track == LURE_TRACK and not self.lure):
                            self.makeUnpressable(button, track, level)
                        if track == THROW_TRACK and 'disableThrow' in base.localAvatar.battleConditions and not \
                                (self.numItem(track, level) <= 0 or track == HEAL_TRACK and not self.heal or track == TRAP_TRACK and not self.trap or track == LURE_TRACK and not self.lure):
                            self.makeUnpressable(button, track, level)
                        if track == DROP_TRACK and 'disableDrop' in base.localAvatar.battleConditions and not \
                                (self.numItem(track, level) <= 0 or track == HEAL_TRACK and not self.heal or track == TRAP_TRACK and not self.trap or track == LURE_TRACK and not self.lure):
                            self.makeUnpressable(button, track, level)
                        if track == SQUIRT_TRACK and 'disableSquirt' in base.localAvatar.battleConditions and not \
                                (self.numItem(track, level) <= 0 or track == HEAL_TRACK and not self.heal or track == TRAP_TRACK and not self.trap or track == LURE_TRACK and not self.lure):
                            self.makeUnpressable(button, track, level)
                        if track == ZAP_TRACK and 'disableZap' in base.localAvatar.battleConditions and not \
                                (self.numItem(track, level) <= 0 or track == HEAL_TRACK and not self.heal or track == TRAP_TRACK and not self.trap or track == LURE_TRACK and not self.lure):
                            self.makeUnpressable(button, track, level)
                        if level == 7 and 'disable8s' in base.localAvatar.battleConditions and not \
                                (self.numItem(track, level) <= 0 or track == HEAL_TRACK and not self.heal or track == TRAP_TRACK and not self.trap or track == LURE_TRACK and not self.lure):
                            self.makeUnpressable(button, track, level)
                        if level == 3 and 'disable4s' in base.localAvatar.battleConditions and not \
                                (self.numItem(track, level) <= 0 or track == HEAL_TRACK and not self.heal or track == TRAP_TRACK and not self.trap or track == LURE_TRACK and not self.lure):
                            self.makeUnpressable(button, track, level)
                        if level == 4 and 'disable5s' in base.localAvatar.battleConditions and not \
                                (self.numItem(track, level) <= 0 or track == HEAL_TRACK and not self.heal or track == TRAP_TRACK and not self.trap or track == LURE_TRACK and not self.lure):
                            self.makeUnpressable(button, track, level)
                        if level == 5 and 'disable6s' in base.localAvatar.battleConditions and not \
                                (self.numItem(track, level) <= 0 or track == HEAL_TRACK and not self.heal or track == TRAP_TRACK and not self.trap or track == LURE_TRACK and not self.lure):
                            self.makeUnpressable(button, track, level)
                        if level == 6 and 'disable7s' in base.localAvatar.battleConditions and not \
                                (self.numItem(track, level) <= 0 or track == HEAL_TRACK and not self.heal or track == TRAP_TRACK and not self.trap or track == LURE_TRACK and not self.lure):
                            self.makeUnpressable(button, track, level)
                        if 'noDamage' in base.localAvatar.battleConditions and not (self.numItem(track, level) <= 0):
                            self.makeUnpressable(button, track, level)
                        if self.toon.hasToonStatusEffect('highRollerTurn1') and not level == 0:
                            self.makeUnpressable(button, track, level)
                        if self.numItem(track, level) <= 0 or track == HEAL_TRACK and not self.heal or track == TRAP_TRACK and not self.trap or track == LURE_TRACK and not self.lure:
                            self.makeUnpressable(button, track, level)
                        if track == THROW_TRACK and 'disableSingleGags' in base.localAvatar.battleConditions and not self.numItem(
                                track, level) <= 0:
                            self.makeUnpressable(button, track, level)
                        if track == DROP_TRACK and 'disableSingleGags' in base.localAvatar.battleConditions and not self.numItem(
                                track, level) <= 0:
                            self.makeUnpressable(button, track, level)
                        if track == TRAP_TRACK and 'disableSingleGags' in base.localAvatar.battleConditions and not self.numItem(
                                track, level) <= 0:
                            self.makeUnpressable(button, track, level)
                        if track == HEAL_TRACK and 'disableSingleGags' in base.localAvatar.battleConditions and level == 0 and not self.numItem(
                                track, level) <= 0:
                            self.makeUnpressable(button, track, level)
                        if track == HEAL_TRACK and 'disableSingleGags' in base.localAvatar.battleConditions and level == 2 and not self.numItem(
                                track, level) <= 0:
                            self.makeUnpressable(button, track, level)
                        if track == HEAL_TRACK and 'disableSingleGags' in base.localAvatar.battleConditions and level == 4 and not self.numItem(
                                track, level) <= 0:
                            self.makeUnpressable(button, track, level)
                        if track == HEAL_TRACK and 'disableSingleGags' in base.localAvatar.battleConditions and level == 6 and not self.numItem(
                                track, level) <= 0:
                            self.makeUnpressable(button, track, level)
                        if track == LURE_TRACK and 'disableSingleGags' in base.localAvatar.battleConditions and level == 0 and not self.numItem(
                                track, level) <= 0:
                            self.makeUnpressable(button, track, level)
                        if track == LURE_TRACK and 'disableSingleGags' in base.localAvatar.battleConditions and level == 2 and not self.numItem(
                                track, level) <= 0:
                            self.makeUnpressable(button, track, level)
                        if track == LURE_TRACK and 'disableSingleGags' in base.localAvatar.battleConditions and level == 4 and not self.numItem(
                                track, level) <= 0:
                            self.makeUnpressable(button, track, level)
                        if track == LURE_TRACK and 'disableSingleGags' in base.localAvatar.battleConditions and level == 6 and not self.numItem(
                                track, level) <= 0:
                            self.makeUnpressable(button, track, level)
                        if track == SQUIRT_TRACK and 'disableGroupGags' in base.localAvatar.battleConditions and not self.numItem(
                                track, level) <= 0:
                            self.makeUnpressable(button, track, level)
                        if track == SOUND_TRACK and 'disableGroupGags' in base.localAvatar.battleConditions and not self.numItem(
                                track, level) <= 0:
                            self.makeUnpressable(button, track, level)
                        if track == ZAP_TRACK and 'disableGroupGags' in base.localAvatar.battleConditions and not self.numItem(
                                track, level) <= 0:
                            self.makeUnpressable(button, track, level)
                        if track == HEAL_TRACK and 'disableGroupGags' in base.localAvatar.battleConditions and level == 7 and not self.numItem(
                                track, level) <= 0:
                            self.makeUnpressable(button, track, level)
                        if track == HEAL_TRACK and 'disableGroupGags' in base.localAvatar.battleConditions and level == 5 and not self.numItem(
                                track, level) <= 0:
                            self.makeUnpressable(button, track, level)
                        if track == HEAL_TRACK and 'disableGroupGags' in base.localAvatar.battleConditions and level == 3 and not self.numItem(
                                track, level) <= 0:
                            self.makeUnpressable(button, track, level)
                        if track == HEAL_TRACK and 'disableGroupGags' in base.localAvatar.battleConditions and level == 1 and not self.numItem(
                                track, level) <= 0:
                            self.makeUnpressable(button, track, level)
                        if track == LURE_TRACK and 'disableGroupGags' in base.localAvatar.battleConditions and level == 7 and not self.numItem(
                                track, level) <= 0:
                            self.makeUnpressable(button, track, level)
                        if track == LURE_TRACK and 'disableGroupGags' in base.localAvatar.battleConditions and level == 5 and not self.numItem(
                                track, level) <= 0:
                            self.makeUnpressable(button, track, level)
                        if track == LURE_TRACK and 'disableGroupGags' in base.localAvatar.battleConditions and level == 3 and not self.numItem(
                                track, level) <= 0:
                            self.makeUnpressable(button, track, level)
                        if track == LURE_TRACK and 'disableGroupGags' in base.localAvatar.battleConditions and level == 1 and not self.numItem(
                                track, level) <= 0:
                            self.makeUnpressable(button, track, level)

                    else:
                        button.hide()

            else:
                self.hideTrack(track)

        self.propBonusIval.loop()
        return
    
    def getDisplayTrackOrder(self):
        defaultOrder = range(len(Tracks))

        if hasattr(base.localAvatar, 'battleConditions'):
            for cond, order in DISPLAY_CONTENT_SYNC_ORDERS.items():
                if cond in base.localAvatar.battleConditions:
                    return order

        return defaultOrder


    def applyDisplayTrackOrder(self):
        order = self.getDisplayTrackOrder()

        for displayIndex, track in enumerate(order):
            self.trackRows[track].setZ(
                self.TrackYOffset + displayIndex * self.TrackYSpacing
            )

    def battleDeactivateButtons(self):
        self.invFrame.reparentTo(self)
        self.levelsButton.hide()
        self.battleFrame.hide()
        self.stopAndClearPropBonusIval()

    def plantTreeActivateButtons(self):
        self.reparentTo(aspect2d)
        self.setPos(0, 0, 0.1)
        self.setScale(1)
        if self.battleFrame == None:
            self.loadBattleFrame()
        self.battleFrame.show()
        self.battleFrame.setScale(0.9)
        self.invFrame.reparentTo(self.battleFrame)
        self.invFrame.setPos(-0.25, 0, 0.35)
        self.invFrame.setScale(1)
        self.detailFrame.setPos(1.125, 0, -0.08)
        self.detailFrame.setScale(1)
        self.deleteAllButton.hide()
        self.deleteEnterButton.hide()
        self.deleteExitButton.hide()
        self.runButton.hide()
        self.sosButton.hide()
        self.levelsButton.hide()
        self.passButton['text'] = TTLocalizer.lCancel
        self.passButton.show()
        for track in range(len(Tracks)):
            if self.toon.hasTrackAccess(track):
                self.showTrack(track)
                for level in range(len(Levels[track])):
                    button = self.buttons[track][level]
                    if self.itemIsUsable(track, level) and (level == 0 or self.toon.doIHaveRequiredTrees(track, level)):
                        button.show()
                        self.makeUnpressable(button, track, level)
                        if self.numItem(track, level) > 0:
                            if not self.toon.isTreePlanted(track, level):
                                self.makePressable(button, track, level)
                    else:
                        button.hide()

            else:
                self.hideTrack(track)

        return

    def plantTreeDeactivateButtons(self):
        self.passButton['text'] = TTLocalizer.InventoryPass
        self.invFrame.reparentTo(self)
        self.levelsButton.hide()
        self.battleFrame.hide()

    def itemIsUsable(self, track, level):
        if self.gagTutMode:
            trackAccess = self.toon.getTrackAccess()
            return trackAccess[track] >= level + 1
        curSkill = self.toon.experience.getExp(track)
        if curSkill < Levels[track][level]:
            return 0
        else:
            return 1

    def itemIsCredit(self, track, level):
        if self.toon.earnedExperience:
            if self.toon.earnedExperience[track]:
                if self.toon.earnedExperience[track] >= ExperienceCap:
                    return 0
        if self.battleCreditLevel == None:
            return 1
        else:
            return level < self.battleCreditLevel
        return

    def getMax(self, track, level):
        if self.gagTutMode and (track not in (4, 5) or level > 0):
            return 1
        return InventoryBase.InventoryBase.getMax(self, track, level)

    def getCurAndNextExpValues(self, track):
        curSkill = self.toon.experience.getExp(track)
        retVal = MaxSkill
        for amount in Levels[track]:
            if curSkill < amount:
                retVal = amount
                return (curSkill, retVal)

        return (curSkill, retVal)

    def makePressable(self, button, track, level):
        organicBonus = self.toon.checkGagBonus(track, level)
        propBonus = self.checkPropBonus(track)
        bonus = organicBonus or propBonus
        if bonus:
            shadowColor = self.ShadowBuffedColor
        else:
            shadowColor = self.ShadowColor
        button.configure(image0_image=self.upButton, image2_image=self.rolloverButton, text_shadow=shadowColor, geom_color=self.PressableGeomColor, commandButtons=(DGG.LMB,))
        if self.interactivePropTrackBonus == track:
            button.configure(image_color=self.PropBonusPressableImageColor)
            self.addToPropBonusIval(button)
        elif organicBonus:
            button.configure(image_color=self.PressableOrganicColor)
        else:
            button.configure(image_color=self.PressableImageColor)

    def makeDisabledPressable(self, button, track, level):
        organicBonus = self.toon.checkGagBonus(track, level)
        propBonus = self.checkPropBonus(track)
        bonus = organicBonus or propBonus
        if bonus:
            shadowColor = self.UnpressableShadowBuffedColor
        else:
            shadowColor = self.ShadowColor
        button.configure(text_shadow=shadowColor, geom_color=self.UnpressableGeomColor, image_image=self.flatButton, commandButtons=(DGG.LMB,))
        button.configure(image_color=self.UnpressableImageColor)

    def makeNoncreditPressable(self, button, track, level):
        organicBonus = self.toon.checkGagBonus(track, level)
        propBonus = self.checkPropBonus(track)
        bonus = organicBonus or propBonus
        if bonus:
            shadowColor = self.ShadowBuffedColor
        else:
            shadowColor = self.ShadowColor
        button.configure(image0_image=self.upButton, image2_image=self.rolloverButton, text_shadow=shadowColor, geom_color=self.PressableGeomColor, commandButtons=(DGG.LMB,))
        if self.interactivePropTrackBonus == track:
            button.configure(image_color=self.PropBonusNoncreditPressableImageColor)
            self.addToPropBonusIval(button)
        else:
            button.configure(image_color=self.NoncreditPressableImageColor)

    def makeBannablePressable(self, button, track, level):
        organicBonus = self.toon.checkGagBonus(track, level)
        propBonus = self.checkPropBonus(track)
        bonus = organicBonus or propBonus
        if bonus:
            shadowColor = self.ShadowBuffedColor
        else:
            shadowColor = self.ShadowColor
        button.configure(image0_image=self.upButton, image2_image=self.rolloverButton, text_shadow=shadowColor, geom_color=self.PressableGeomColor, commandButtons=(DGG.LMB,))
        button.configure(image_color=(1, 0, 0, 1))
        self.addToPropBonusIval(button)

    def makeDamageUpPressable(self, button, track, level):
        organicBonus = self.toon.checkGagBonus(track, level)
        propBonus = self.checkPropBonus(track)
        bonus = organicBonus or propBonus
        if bonus:
            shadowColor = self.ShadowBuffedColor
        else:
            shadowColor = self.ShadowColor
        button.configure(image0_image=self.upButton, image2_image=self.rolloverButton, text_shadow=shadowColor, geom_color=self.PressableGeomColor, commandButtons=(DGG.LMB,))
        button.configure(image_color=(1, 1, 1, 1))
        if bonus:
            self.addToPropBonusIvalDamageUpBonus(button)
        else:
            self.addToPropBonusIvalDamageUp(button)

    def makeDamageDownPressable(self, button, track, level):
        organicBonus = self.toon.checkGagBonus(track, level)
        propBonus = self.checkPropBonus(track)
        bonus = organicBonus or propBonus
        if bonus:
            shadowColor = self.ShadowBuffedColor
        else:
            shadowColor = self.ShadowColor
        button.configure(image0_image=self.upButton, image2_image=self.rolloverButton, text_shadow=shadowColor, geom_color=self.PressableGeomColor, commandButtons=(DGG.LMB,))
        button.configure(image_color=(1, 1, 1, 1))
        if bonus:
            self.addToPropBonusIvalDamageDownBonus(button)
        else:
            self.addToPropBonusIvalDamageDown(button)

    def makeRushJobPressable(self, button, track, level):
        organicBonus = self.toon.checkGagBonus(track, level)
        propBonus = self.checkPropBonus(track)
        bonus = organicBonus or propBonus
        if bonus:
            shadowColor = self.ShadowBuffedColor
        else:
            shadowColor = self.ShadowColor
        button.configure(image0_image=self.upButton, image2_image=self.rolloverButton, text_shadow=shadowColor, geom_color=self.PressableGeomColor, commandButtons=(DGG.LMB,))
        button.configure(image_color=(0, 1, 0.047, 1))
        self.addToPropBonusIval(button)

    def makeDeletePressable(self, button, track, level):
        organicBonus = self.toon.checkGagBonus(track, level)
        propBonus = self.checkPropBonus(track)
        bonus = organicBonus or propBonus
        if bonus:
            shadowColor = self.ShadowBuffedColor
        else:
            shadowColor = self.ShadowColor
        button.configure(image0_image=self.upButton, image2_image=self.rolloverButton, text_shadow=shadowColor, geom_color=self.PressableGeomColor, commandButtons=(DGG.LMB,))
        button.configure(image_color=self.DeletePressableImageColor)

    def makeUnpressable(self, button, track, level):
        organicBonus = self.toon.checkGagBonus(track, level)
        propBonus = self.checkPropBonus(track)
        bonus = organicBonus or propBonus
        if bonus:
            shadowColor = self.UnpressableShadowBuffedColor
        else:
            shadowColor = self.ShadowColor
        button.configure(text_shadow=shadowColor, geom_color=self.UnpressableGeomColor, image_image=self.flatButton, commandButtons=())
        button.configure(image_color=self.UnpressableImageColor)

    def makeBookUnpressable(self, button, track, level):
        organicBonus = self.toon.checkGagBonus(track, level)
        propBonus = self.checkPropBonus(track)
        bonus = organicBonus or propBonus
        if bonus:
            shadowColor = self.ShadowBuffedColor
        else:
            shadowColor = self.ShadowColor
        button.configure(text_shadow=shadowColor, geom_color=self.BookUnpressableGeomColor, image_image=self.flatButton, commandButtons=())
        color = self.BookUnpressableImage0Color
        if organicBonus:
            color = self.PressableOrganicColor
        button.configure(image0_color=color, image2_color=self.BookUnpressableImage2Color)

    def hideTrack(self, trackIndex):
        self.trackNameLabels[trackIndex].show()
        self.trackBars[trackIndex].hide()
        for levelIndex in range(0, len(Levels[trackIndex])):
            self.buttons[trackIndex][levelIndex].hide()

    def showTrack(self, trackIndex):
        self.trackNameLabels[trackIndex].show()
        self.trackBars[trackIndex].show()
        for levelIndex in range(0, len(Levels[trackIndex])):
            self.buttons[trackIndex][levelIndex].show()

        curExp, nextExp = self.getCurAndNextExpValues(trackIndex)
        if curExp >= UnpaidMaxSkills[trackIndex] and self.toon.getGameAccess() != OTPGlobals.AccessFull:
            self.trackBars[trackIndex]['range'] = nextExp
            self.trackBars[trackIndex]['text'] = TTLocalizer.InventoryGuestExp
        elif curExp >= regMaxSkill:
            self.trackBars[trackIndex]['range'] = UberSkill
            self.trackBars[trackIndex]['text'] = TTLocalizer.InventoryUberTrackExp % {'nextExp': MaxSkill - curExp}
        else:
            self.trackBars[trackIndex]['range'] = nextExp
            self.trackBars[trackIndex]['text'] = TTLocalizer.InventoryTrackExp % {'curExp': curExp,
             'nextExp': nextExp}

    def updateInvString(self, invString):
        InventoryBase.InventoryBase.updateInvString(self, invString)
        self.updateGUI()
        return None

    def updateButton(self, track, level):
        button = self.buttons[track][level]
        button['text'] = str(self.numItem(track, level))
        organicBonus = self.toon.checkGagBonus(track, level)
        propBonus = self.checkPropBonus(track)
        bonus = organicBonus or propBonus
        if bonus:
            imageColor = self.PressableOrganicColor
        else:
            imageColor = self.PressableImageColor
        button.configure(image_color=imageColor)

    def buttonBoing(self, track, level):
        button = self.buttons[track][level]
        oldScale = button.getScale()
        s = Sequence(button.scaleInterval(0.1, oldScale * 1.333, blendType='easeOut'), button.scaleInterval(0.1, oldScale, blendType='easeIn'), name='inventoryButtonBoing-' + str(self.this))
        s.start()

    def updateGUI(self, track = None, level = None):
        self.updateTotalPropsText()
        if track == None and level == None:
            for track in range(len(Tracks)):
                curExp, nextExp = self.getCurAndNextExpValues(track)
                if curExp >= UnpaidMaxSkills[track] and self.toon.getGameAccess() != OTPGlobals.AccessFull:
                    self.trackBars[track]['range'] = nextExp
                    self.trackBars[track]['text'] = TTLocalizer.InventoryGuestExp
                elif curExp >= regMaxSkill:
                    self.trackBars[track]['text'] = TTLocalizer.InventoryUberTrackExp % {'nextExp': MaxSkill - curExp}
                    self.trackBars[track]['value'] = curExp - regMaxSkill
                else:
                    self.trackBars[track]['text'] = TTLocalizer.InventoryTrackExp % {'curExp': curExp,
                     'nextExp': nextExp}
                    self.trackBars[track]['value'] = curExp
                for level in range(0, len(Levels[track])):
                    self.updateButton(track, level)

        elif track != None and level != None:
            self.updateButton(track, level)
        else:
            self.notify.error('Invalid use of updateGUI')
        self.__activateButtons()
        return

    def getSingleGroupStr(self, track, level):
        if track == HEAL_TRACK:
            if isGroup(track, level):
                return TTLocalizer.InventoryAffectsAllToons
            else:
                return TTLocalizer.InventoryAffectsOneToon
        elif track == TRAP_TRACK:
            return TTLocalizer.InventoryAffectsOneCog
        elif track == THROW_TRACK:
            return TTLocalizer.InventoryAffectsOneCog
        elif track == SQUIRT_TRACK:
            return TTLocalizer.InventoryAffectsThreeCogs
        elif track == ZAP_TRACK:
            return TTLocalizer.InventoryAffectsSoakedCogs
        elif track == SOUND_TRACK:
            return TTLocalizer.InventoryAffectsOneCog
        elif track == DROP_TRACK:
            return TTLocalizer.InventoryAffectsOneCog
        elif isGroup(track, level):
            return TTLocalizer.InventoryAffectsAllCogs
        else:
            return TTLocalizer.InventoryAffectsOneCog
   
    def getExtraText(self, track, level, organicBonus):
        if track == SQUIRT_TRACK:
           if organicBonus:
               bonusRounds = 1
           else:
               bonusRounds = 0
           if bonusRounds:
               text = TTLocalizer.InventorySquirtRoundsString % str(BattleGlobals.NumRoundsWet[level]) + ' (+1)'
           else:
               text = TTLocalizer.InventorySquirtRoundsString % str(BattleGlobals.NumRoundsWet[level])
           return text
        elif track == TRAP_TRACK:
            return TTLocalizer.TrapExtraText
        elif track == ZAP_TRACK:
            bonus = 0
            if organicBonus:
                bonus = int(InstaKillChance[level] * 0.5)
            if bonus:
                text = TTLocalizer.ZapExtraText % str(InstaKillChance[level]) + ' (+%d)' % bonus
            else:
                text = TTLocalizer.ZapExtraText % str(InstaKillChance[level])
            return text
                

    def getToonupDmgStr(self, track, level):
        if track == HEAL_TRACK:
            return TTLocalizer.InventoryHealString
        elif track == LURE_TRACK:
            return TTLocalizer.InventoryLureString
        else:
            return TTLocalizer.InventoryDamageString

    def deleteItem(self, track, level):
        if self.numItem(track, level) > 0:
            self.useItem(track, level)
            self.updateGUI(track, level)

    def loadBattleFrame(self):
        buttonGui = loader.loadModel('phase_3.5/models/gui/battlegui/gag_selection_panels')

        runUp = buttonGui.find('**/tab_run')
        runDown = buttonGui.find('**/tab_run_press')
        runHover = buttonGui.find('**/tab_run_hover')

        
        passUp = buttonGui.find('**/tab_pass')
        passDown = buttonGui.find('**/tab_pass_press')
        passHover = buttonGui.find('**/tab_pass_hover')

        sosUp = buttonGui.find('**/tab_sos')
        sosDown = buttonGui.find('**/tab_sos_press')
        sosHover = buttonGui.find('**/tab_sos_hover')

        fireUp = buttonGui.find('**/tab_fire')
        fireDown = buttonGui.find('**/tab_fire_press')
        fireHover = buttonGui.find('**/tab_fire_hover')

        sueUp = buttonGui.find('**/tab_sue')
        sueDown = buttonGui.find('**/tab_sue_press')
        sueHover = buttonGui.find('**/tab_sue_hover')

        battleModels = loader.loadModel('phase_3.5/models/gui/battlegui/gag_selection_panels')
        self.levelsButton = DirectButton(self, relief=None, pos=(0, 0, 0.35), text='', text_scale=TTLocalizer.INlevelsButton, text_pos=(0, 0.02), text_fg=Vec4(1, 1, 1, 1), textMayChange=1, image=(self.upButton, self.downButton, self.rolloverButton), image_scale=(3.0, 1.0, 1.5), image_color=(1, 0.6, 0, 1), command=self.__handleLevels)
        self.battleFrame = DirectFrame(relief=None, pos=(.25, 0, -.1), image=battleModels.find('**/gag_selection_main'), image_pos=(-1.275, 0, -0.01), image_scale=(1.175, 1.175, 1.175), parent=self)
        self.gagIconPanel = DirectFrame(relief=None, pos=(.8, 0, 0), image=battleModels.find('**/gag_info_main'), image_scale=(.9, .9, .9), parent=self.battleFrame)
        self.runButton = DirectButton(parent=self, relief=None, pos=(-1.3, 0, .05), image=(runUp, runDown, runHover), image_scale=0.3, image_color=(1, 1, 1, 1), command=self.__handleRun)
        self.sosButton = DirectButton(parent=self, relief=None, pos=(-1.3, 0, -.15), image=(sosUp, sosDown, sosHover), image_scale=0.3, image_color=(1, 1, 1, 1), command=self.__handleSOS)
        self.passButton = DirectButton(parent=self, relief=None, pos=(-1.3, 0, .25), image=(passUp, passDown, passHover), image_scale=0.3, image_color=(1, 1, 1, 1),  command=self.__handlePass)
        self.fireButton = DirectButton(parent=self, relief=None, pos=(-1.3, 0, -.325), image=(fireUp, fireDown, fireHover), image_scale=(.5, .15, .125), image_color=(1, 1, 1, 1), command=self.__handleFire)
        self.sueButton = DirectButton(parent=self, relief=None, pos=(-1.3, 0, -.475), image=(sueUp, sueDown, sueHover), image_scale=(.5, .15, .125), image_color=(1, 1, 1, 1), command=self.__handleSue)
        self.tutText = DirectFrame(parent=self.battleFrame, relief=None, pos=(0.05, 0, -0.1133), scale=0.143, image=DGG.getDefaultDialogGeom(), image_scale=5.125, image_pos=(0, 0, -0.65), image_color=ToontownGlobals.GlobalDialogColor, text_scale=TTLocalizer.INclickToAttack, text=TTLocalizer.InventoryClickToAttack, textMayChange=0)
        self.tutText.hide()
        self.passButton.setBin('fixed', 0) 
        self.runButton.setBin('fixed', 0) 
        self.sosButton.setBin('fixed', 0) 
        self.fireButton.setBin('fixed', 0) 
        self.sueButton.setBin('fixed', 0) 
        self.tutArrows = BlinkingArrows.BlinkingArrows(parent=self.battleFrame)
        battleModels.removeNode()
        self.levelsButton.hide()
        self.battleFrame.hide()
        return

    def loadPurchaseFrame(self):
        purchaseModels = loader.loadModel('phase_4/models/gui/purchase_gui')
        self.purchaseFrame = DirectFrame(relief=None, image=purchaseModels.find('**/PurchasePanel'), image_pos=(-0.21, 0, 0.08), parent=self)
        self.purchaseFrame.setX(-.06)
        self.purchaseFrame.hide()
        purchaseModels.removeNode()
        return

    def loadStorePurchaseFrame(self):
        storePurchaseModels = loader.loadModel('phase_4/models/gui/gag_shop_purchase_gui')
        self.storePurchaseFrame = DirectFrame(relief=None, image=storePurchaseModels.find('**/gagShopPanel'), image_pos=(-0.21, 0, 0.18), parent=self)
        self.storePurchaseFrame.hide()
        storePurchaseModels.removeNode()
        return

    def buttonLookup(self, track, level):
        return self.invModels[track][level]

    def enterTrackFrame(self, track, guiItem):
        messenger.send('enterTrackFrame', [track])

    def exitTrackFrame(self, track, guiItem):
        messenger.send('exitTrackFrame', [track])

    def checkPropBonus(self, track):
        return track == self.interactivePropTrackBonus

    def stopAndClearPropBonusIval(self):
        if self.propBonusIval and self.propBonusIval.isPlaying():
            self.propBonusIval.finish()
        self.propBonusIval = Parallel(name='dummyPropBonusIval')

    def addToPropBonusIval(self, button):
        flashObject = button
        try:
            flashObject = button.component('image0')
        except:
            pass

        goDark = LerpColorScaleInterval(flashObject, 0.5, Point4(0.1, 0.1, 0.1, 1.0), Point4(1, 1, 1, 1), blendType='easeIn')
        goBright = LerpColorScaleInterval(flashObject, 0.5, Point4(1, 1, 1, 1), Point4(0.1, 0.1, 0.1, 1.0), blendType='easeOut')
        newSeq = Sequence(goDark, goBright, Wait(0.2))
        self.propBonusIval.append(newSeq)

    def addToPropBonusIvalRed(self, button):
        flashObject = button
        try:
            flashObject = button.component('image0')
        except:
            pass

        goDark = LerpColorScaleInterval(flashObject, 0.5, Point4(0.1, 0.1, 0.1, 1.0), Point4(1, 1, 1, 1), blendType='easeIn')
        goBright = LerpColorScaleInterval(flashObject, 0.5, Point4(1, 1, 1, 1), Point4(0.1, 0.1, 0.1, 1.0), blendType='easeOut')
        newSeq = Sequence(goDark, goBright, Wait(0.2))
        self.propBonusIval.append(newSeq)

    def addToPropBonusIvalDamageUp(self, button):
        flashObject = button
        try:
            flashObject = button.component('image0')
        except:
            pass

        goDark = LerpColorScaleInterval(flashObject, 0.5, Point4(0, 0.6, 1, 1), Point4(0, 1, 0.949, 1), blendType='easeIn')
        goBright = LerpColorScaleInterval(flashObject, 0.5, Point4(0, 1, 0.949, 1), Point4(0, 0.6, 1, 1), blendType='easeOut')
        newSeq = Sequence(goDark, Wait(0.2), goBright)
        self.propBonusIval.append(newSeq)

    def addToPropBonusIvalDamageUpBonus(self, button):
        flashObject = button
        try:
            flashObject = button.component('image0')
        except:
            pass

        goDark = LerpColorScaleInterval(flashObject, 0.5, Point4(0, .2, .9, 1), Point4(0, 1, 0.949, 1), blendType='easeIn')
        goBright = LerpColorScaleInterval(flashObject, 0.5, Point4(0, 1, 0.949, 1), Point4(0, .2, .9, 1), blendType='easeOut')
        newSeq = Sequence(goDark, Wait(0.2), goBright)
        self.propBonusIval.append(newSeq)

    def addToPropBonusIvalDamageDown(self, button):
        flashObject = button
        try:
            flashObject = button.component('image0')
        except:
            pass

        goDark = LerpColorScaleInterval(flashObject, 0.5, Point4(0, 0.6, 1, 1), Point4(1, 0.984, 0, 1), blendType='easeIn')
        goBright = LerpColorScaleInterval(flashObject, 0.5, Point4(1, 0.984, 0, 1), Point4(0, 0.6, 1, 1), blendType='easeOut')
        newSeq = Sequence(goDark, Wait(0.2), goBright)
        self.propBonusIval.append(newSeq)

    def addToPropBonusIvalDamageDownBonus(self, button):
        flashObject = button
        try:
            flashObject = button.component('image0')
        except:
            pass

        goDark = LerpColorScaleInterval(flashObject, 0.5, Point4(0, .2, .9, 1), Point4(1, 0.984, 0, 1), blendType='easeIn')
        goBright = LerpColorScaleInterval(flashObject, 0.5, Point4(1, 0.984, 0, 1), Point4(0, .2, .9, 1), blendType='easeOut')
        newSeq = Sequence(goDark, Wait(0.2), goBright)
        self.propBonusIval.append(newSeq)

    def addToPropBonusIvalRushJob(self, button):
        flashObject = button
        try:
            flashObject = button.component('image0')
        except:
            pass

        goDark = LerpColorScaleInterval(flashObject, 0.5, Point4(1.0, 1.0, 1.0, 1.0), Point4(0, 1, 0.047, 1), blendType='easeIn')
        goBright = LerpColorScaleInterval(flashObject, 0.5, Point4(0, 1, 0.047, 1), Point4(1.0, 1.0, 1.0, 1.0), blendType='easeOut')
        newSeq = Sequence(goDark, goBright, Wait(0.2))
        self.propBonusIval.append(newSeq)
