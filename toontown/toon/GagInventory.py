from direct.gui.DirectGui import *
from toontown.clashbattle.battle import BattleGUI, BattleGlobals, BattleGUIGlobals
from toontown.clashbattle.battle.statuses import StatusEffects
from toontown.clashbattle.battle.BattleGlobals import *
from toontown.chat.ui.speedchat.TTSCUniteTerminal import TTSCUniteStateChangedEvent
from toontown.instances import HighRollerGlobals
from toontown.inventory.enums.ItemEnums import BoosterItemType
from toontown.modifiers.ModifierEnums import ModifierType
from toontown.modifiers.classes.GagsContentSyncModifier import GagsContentSyncModifier
from toontown.clashsuit.suit import SuitHoodGlobals
from toontown.toon import GagInventoryBase
from toontown.toon.QuickShopper import QuickShopper
from toontown.toonbase import TTLocalizer
from toontown.quest import BlinkingArrows
from direct.interval.IntervalGlobal import *
from toontown.chat.ChatGlobals import WTSystem

from toontown.utils import text
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from toontown.toonbase import ToontownGlobals
from toontown.gui.TTGui import ScalingButton
from toontown.toonbase import ToontownGlobals
from toontown.gui import TTDialog
from direct.showbase.MessengerGlobal import messenger
from otp import *
from toontown.utils.DGGEventIgnorer import ignore_event
import math
from toontown.hood import ZoneUtil

INV_MOD_NONE = 0
INV_MOD_PUNISHMENT = 1
INV_MOD_DISABLED = 2
INV_MOD_TUT_DISABLED = 3
INV_MOD_PROP_BONUS = 4
InventoryScalingChangedEvent = 'inventory-scaling-changed'


@DirectNotifyCategory()
class GagInventory(GagInventoryBase.GagInventoryBase, DirectFrame):
    PressableTextColor = Vec4(1, 1, 1, 1)
    PressableGeomColor = Vec4(1, 1, 1, 1)
    PressableImageColor = Vec4(0, 0.6, 1, 1)
    PressableImageColorBonus = Vec4(0, 0.2, 0.6, 1)

    PropBonusPressableImageColor = Vec4(1.0, 0.6, 0.0, 1)
    NoncreditPressableImageColor = Vec4(0.3, 0.6, 0.6, 1)
    NoncreditPressableImageColorBonus = Vec4(0, 0.4, 0.6, 1)
    PropBonusNoncreditPressableImageColor = Vec4(0.6, 0.6, 0.3, 1)
    DeletePressableImageColor = Vec4(0.7, 0.1, 0.1, 1)
    CounterfeitPressableImageColor = Vec4(0.25, 0.85, 0.25, 1)
    CounterfeitPressableImageColorBonus = Vec4(0.05, 0.55, 0.05, 1)
    CounterfeitTextColor = Vec4(1.0, 1.0, 1.0, 1.0)

    UnpressableTextColor = Vec4(1, 1, 1, 0.3)
    UnpressableGeomColor = Vec4(1, 1, 1, 0.3)
    UnpressableImageColor = Vec4(0.3, 0.3, 0.3, 0.8)
    UnpressableImageColorBonus = Vec4(0, 0.1, 0.3, 0.8)

    BookUnpressableTextColor = Vec4(1, 1, 1, 1)
    BookUnpressableGeomColor = Vec4(1, 1, 1, 1)
    BookUnpressableImage0Color = Vec4(0, 0.6, 1, 1)
    BookUnpressableImage0ColorBonus = Vec4(0, 0.2, 0.6, 1)
    BookUnpressableImage2Color = Vec4(0.1, 0.7, 1, 1)
    BookUnpressableImage2ColorBonus = Vec4(0.1, 0.3, 0.6, 1)

    ShadowColor = Vec4(0, 0, 0, 0)
    ShadowBuffedColor = Vec4(1, 1, 1, 1)
    UnpressableShadowBuffedColor = Vec4(1, 1, 1, 0.3)

    TrackYOffset = 0.061
    TrackYSpacing = -0.12
    ButtonXOffset = -0.40
    ButtonXSpacing = 0.18

    def __init__(self, toon, invStr=None, ShowSuperGags=1):
        GagInventoryBase.GagInventoryBase.__init__(self, toon, invStr)
        self.toon = toon
        DirectFrame.__init__(self, relief=None)
        self.initialiseoptions(GagInventory)
        self.battleCreditLevel = None
        self.battleCreditMult = 1

        self.liveCreditMult = 0
        self.countInvasions = True
        self.interactivePropTrackBonus = -1
        self.tutorialFlag = 0
        self.gagTutMode = 0
        self.canHeal = 0
        self.canTrap = 0
        self.canLure = 0
        self.canSue = 0
        self.tutorialFrame = None

        self.showSuperGags = ShowSuperGags
        self.clickSuperGags = 1

        self.battle = None

        self.counterfeitBackSeq = None
        self.surrenderSeq = None
        self.lastSurrenderNum = 0
        self.surrenderIncSfx = None
        self.surrenderDecSfx = None

        self.propAndOrganicBonusStack = ConfigVariableBool('prop-and-organic-bonus-stack', False).getValue()
        self.propBonusIval = Parallel()
        self.activateMode = 'book'
        self.needUpdateInventory = False
        self.buttonModifierFuncs = {
            INV_MOD_PUNISHMENT: self.makeDeletePressable,
            INV_MOD_DISABLED: self.makeUnpressable,
            INV_MOD_TUT_DISABLED: self.makeUnpressable,
            INV_MOD_PROP_BONUS: self.makePropBonusPressable,
        }
        self.activeButtonModifiers = {}
        self.quickShopper = QuickShopper(isIncrement=False)
        self.load()

        self.accept('zoneChange', lambda _: self.setLiveCreditMult())

        # Hide until we need it
        self.hide()

    # Set battle credit multiplier...
    def setBattleCreditMult(self, mult=1, countInvasions=False):
        self.countInvasions = countInvasions
        self.setLiveCreditMult()
        self.battleCreditMult = mult

    def getGagCreditMult(self):
        return self.battleCreditMult

    def setInteractivePropTrackBonus(self, trackBonus):
        """Handle the battle telling us it has a prop bonus."""
        self.interactivePropTrackBonus = trackBonus

    def getInteractivePropTrackBonus(self):
        """Return if we're in a battle with a prop bonus."""
        return self.interactivePropTrackBonus

    def setLiveCreditMult(self):
        if self.activateMode == 'battle':
            return
        mult = 0
        # only update gag credit outside of battle bc xp is only calculated at start of battle
        if base.cr.newsManager:
            # If invasion
            if self.countInvasions and SuitHoodGlobals.isZoneInvasionableClient():
                mult += getInvasionMultiplier() - 1
            self.liveCreditMult = mult

    def getTownBattle(self):
        if self.battle and self.battle.townBattle:
            return self.battle.townBattle
        return None

    def show(self):
        self.enablePresetButtons()
        if self.tutorialFlag and self.tutorialFrame:
            self.tutorialFrame.show()
        DirectFrame.show(self)

    def uberGagToggle(self, showSuperGags=1):
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

    def enableUberGags(self, enableSG=-1):
        if enableSG != -1:
            self.clickSuperGags = enableSG
        for buttonList in self.buttons:
            for buttonIndex in range(LAST_REGULAR_GAG_LEVEL + 1, MAX_LEVEL_INDEX + 1):
                if self.clickSuperGags:
                    pass
                else:
                    self.makeUnpressable(buttonList[buttonIndex], self.buttons.index(buttonList), buttonIndex)

    def hide(self):
        # Stop associated tasks when hiding this object.
        if hasattr(self, 'presetDialog'):
            self.presetDialog.cleanup()
            del self.presetDialog
        if self.tutorialFlag and self.tutorialFrame:
            self.tutorialFrame.hide()
        DirectFrame.hide(self)

    def updateTotalPropsText(self):
        # Keeps track of what to set the Z of totalLabel to at the end.
        finalZ = -0.08
        # Offset per Line beyond the starting 2 lines.
        zOffsetPerLine = 0.03

        # Perform any overrides if they exist.
        if self.overrideTotalPropsText():
            return

        textTotal = str(self.totalProps) + ' / ' + str(self.toon.getMaxCarry())
        if BattleGUI.TOTAL_GAGS_NUMBER_LABEL in self.guiElements:
            self.guiElements[BattleGUI.TOTAL_GAGS_NUMBER_LABEL]['text'] = textTotal
            if self.guiElements[BattleGUI.TOTAL_GAGS_NUMBER_LABEL].isHidden():
                textTotal = TTLocalizer.InventoryTotalGags + '\n' + textTotal + '\n'
            else:
                textTotal = TTLocalizer.InventoryHoveroverTip + '\n'
        else:
            textTotal = TTLocalizer.InventoryTotalGags + '\n' + textTotal + '\n'

        counterfeits, ceases, fires = base.localAvatar.getCounterfeits(), base.localAvatar.getCeaseDesists(), base.localAvatar.getPinkSlips()
        rewardList = [counterfeits, ceases, fires]
        rewardsWithAmount = [rewardType for rewardType in range(3) if rewardList[rewardType] > 0]
        for rewardType, rewardAmt in enumerate([counterfeits, ceases, fires]):
            if rewardAmt > 0:
                if rewardType != rewardsWithAmount[-1]:
                    finalZ += zOffsetPerLine * 2

                textTotal = textTotal + '\n'
                textTotal = textTotal + TTLocalizer.InventoryRewardStrings[rewardType] % rewardAmt

        self.totalLabel['text'] = textTotal
        self.totalLabel.setZ(finalZ)

    def overrideTotalPropsText(self) -> bool:
        """
        Attempt to override the total props text.
        """
        # Be careful out there. Monsters are lurking.
        if not self.toon:
            return False

        if self.activateMode == 'counterfeit':
            self.totalLabel['text'] = TTLocalizer.InventoryCounterfeitTip % base.localAvatar.getCounterfeits()
            self.totalLabel.setZ(-0.08 + (0.03 * 1))
            return True

        # Check for Pips
        pipsqueak = self.toon.getStatusEffectOfId(SEE.EFFECT_PIP_COUNTER)
        if pipsqueak:
            pointCount = pipsqueak.getPointCount()
            labelText = f'You have {pointCount} Pip{text.plural(pointCount)}.\n\n(Gags cost Pips!)'
            if not self.toon.getStatusEffectOfId(SEE.EFFECT_HR_TOON_GAGS_UNLOCKED):
                labelText += '\n\n\1deepRed\1\1TextSmaller\1Purchase the\n\1white\1\5icon_goldDice\5\2  Golden Dice\nto unlock your Gags!\2\2'
            self.totalLabel['text'] = labelText
            self.totalLabel.setZ(-0.08 + (0.03 * 2))
            return True

        # No override exists.
        return False

    def unload(self):
        self.notify.debug('Unloading Inventory for %d' % self.toon.doId)

        self.quickShopper.unload()
        self.stopAndClearPropBonusIval()

        self.propBonusIval.finish()
        self.propBonusIval = None
        del self.guiElements
        del self.invModels

        self.finishCounterfeitBackSeq()
        self.finishSurrenderSeq()

        if self.surrenderIncSfx:
            self.surrenderIncSfx.stop()
            self.surrenderIncSfx = None
        if self.surrenderDecSfx:
            self.surrenderDecSfx.stop()
            self.surrenderDecSfx = None

        self.gagSelectGui.removeNode()
        del self.gagSelectGui

        self.buttonModels.removeNode()
        del self.buttonModels

        del self.upButton
        del self.downButton
        del self.rolloverButton
        del self.flatButton

        del self.invFrame
        del self.battleFrame
        del self.purchaseFrame
        del self.storePurchaseFrame

        self.savePresetButton.destroy()
        del self.savePresetButton
        self.loadPresetButton.destroy()
        del self.loadPresetButton
        self.deleteEnterButton.destroy()
        del self.deleteEnterButton
        self.deleteExitButton.destroy()
        del self.deleteExitButton

        del self.detailFrame
        del self.detailEmblem
        del self.detailNameLabel
        del self.detailAmountLabel
        del self.detailDataLabel
        del self.totalLabel

        self.cleanupDialog()

        for row in self.trackRows.values():
            row.destroy()

        del self.trackRows
        del self.trackNameLabels
        del self.trackBars
        for buttonList in self.buttons.values():
            for buttonIndex in range(MAX_LEVEL_INDEX + 1):
                buttonList[buttonIndex].destroy()

        del self.buttons
        del self.trackHovers
        GagInventoryBase.GagInventoryBase.unload(self)
        DirectFrame.destroy(self)
        self.ignoreAll()
        return

    def cleanupDialog(self):
        if self.dialog:
            self.dialog.cleanup()
            self.dialog = None

    def load(self):
        self.gagSelectGui = base.loader.loadModel('phase_3.5/models/gui/battlegui/gag_selection_panels')

        self.notify.debug('Loading Inventory for %d' % self.toon.doId)
        invModel = loader.loadModel('phase_3.5/models/gui/inventory_icons')

        # Find all the inventory models and cache them
        self.invModels = []
        for track in range(len(AvPropsNew)):
            itemList = []
            for item in range(len(AvPropsNew[track])):
                itemList.append(invModel.find('**/' + AvPropsNew[track][item]))
            self.invModels.append(itemList)

        invModel.removeNode()
        del invModel

        self.buttonModels = loader.loadModel('phase_3.5/models/gui/inventory_gui')
        self.upButton = self.buttonModels.find('**/InventoryButtonUp')
        self.downButton = self.buttonModels.find('**/InventoryButtonDown')
        self.rolloverButton = self.buttonModels.find('**/InventoryButtonRollover')
        self.flatButton = self.buttonModels.find('**/InventoryButtonFlat')

        # Mode Frames
        self.invFrame = DirectFrame(
            parent=self,
            relief=None
        )
        self.battleFrame = None
        self.purchaseFrame = None
        self.storePurchaseFrame = None

        # Dictionary to store all elements returned from BattleGUI generation functions.
        self.guiElements = {}

        # Generate Gag Tracks
        self.guiElements.update(BattleGUI.generateGagTracks(self))
        # Assign new elements to self
        self.tracksFrame = self.guiElements[BattleGUI.TRACKS_FRAME]
        self.tracksFrame.reparentTo(self.invFrame)
        self.trackRows = self.guiElements[BattleGUI.TRACKS_ROWS]
        self.trackNameLabels = self.guiElements[BattleGUI.TRACKS_NAME_LABELS]
        self.trackBars = self.guiElements[BattleGUI.TRACKS_EXPERIENCE_BARS]
        self.prestigeStars = self.guiElements[BattleGUI.TRACKS_PRESTIGE_STARS]
        self.buttons = self.guiElements[BattleGUI.TRACKS_GAG_BUTTONS]
        self.trackHovers = self.guiElements[BattleGUI.TRACKS_TRACK_HOVERS]
        self.trackSubframes = self.guiElements[BattleGUI.TRACKS_SUBFRAMES]

        # Set Bindings for Gag Tracks
        for track in self.getGagOrder():
            trackFrame = self.trackRows[track]
            trackFrame.bind(DGG.WITHIN, self.enterTrackFrame, extraArgs=[track])
            trackFrame.bind(DGG.WITHOUT, self.exitTrackFrame, extraArgs=[track])
            trackHover = self.trackHovers[track]
            trackHover.bind(DGG.ENTER, self.enterTrackFrame, extraArgs=[track])
            trackHover.bind(DGG.EXIT, self.exitTrackFrame, extraArgs=[track])
            trackButtons = self.buttons[track]
            for item in range(len(Levels[track])):
                button = trackButtons[item]
                button.bind(DGG.B1PRESS, self.__handleSelection, extraArgs=[track, item, False])
                button.bind(DGG.B3PRESS, self.__handleSelection, extraArgs=[track, item, True])
                button.guiItem.setSound(DGG.B3PRESS + button.guiId, button['clickSound'])
                button.bind(DGG.ENTER, self.showDetail, extraArgs=[track, item])
                button.bind(DGG.EXIT, self.hideDetail)

        # Generate Detail Panel
        self.guiElements.update(BattleGUI.generateDetailPanel())
        # Assign new elements to self
        self.detailFrame = self.guiElements[BattleGUI.DETAILS_FRAME]
        self.detailFrame.reparentTo(self.tracksFrame)
        self.detailEmblem = self.guiElements[BattleGUI.DETAILS_EMBLEM]
        self.detailNameLabel = self.guiElements[BattleGUI.DETAILS_NAME_LABEL]
        self.detailAmountLabel = self.guiElements[BattleGUI.DETAILS_AMOUNT_LABEL]
        self.detailDataLabel = self.guiElements[BattleGUI.DETAILS_DATA_LABEL]

        # The delete buttons
        trashcanGui = loader.loadModel('phase_3/models/gui/trashcan_gui')
        presetGui = loader.loadModel('phase_4/models/gui/presetsGUI')
        self.deleteEnterButton = DirectButton(
            parent=self.invFrame,
            image=(
                trashcanGui.find('**/TrashCan_CLSD'),
                trashcanGui.find('**/TrashCan_OPEN'),
                trashcanGui.find('**/TrashCan_RLVR')
            ),
            text=('', TTLocalizer.InventoryDelete, TTLocalizer.InventoryDelete),
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            text_scale=0.1,
            text_pos=(0, -0.1),
            text_font=getInterfaceFont(),
            textMayChange=0,
            relief=None,
            pos=(-1.3, 0, -0.35),
            scale=0.62
        )

        # Save Preset button
        self.savePresetButton = DirectButton(
            parent=self.invFrame,
            image=(
                presetGui.find('**/preset_save_normal'),
                presetGui.find('**/preset_save_press'),
                presetGui.find('**/preset_save_hover')
            ),
            text=(
                '', TTLocalizer.InventorySavePreset, TTLocalizer.InventorySavePreset), text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            text_scale=0.22,
            text_pos=(-0.15, -0.7),
            text_font=getInterfaceFont(),
            relief=None,
            pos=(-0.605, 0, -0.1),
            scale=0.12,
            command=self.__savePresetConfirm
        )

        # Load Preset button
        self.loadPresetButton = DirectButton(
            parent=self.invFrame,
            image=(
                presetGui.find('**/preset_load_normal'),
                presetGui.find('**/preset_load_press'),
                presetGui.find('**/preset_load_hover')
            ),
            text=(
                '', TTLocalizer.InventoryLoadPreset, TTLocalizer.InventoryLoadPreset), text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            text_scale=0.22,
            text_pos=(0.12, -0.7),
            text_font=getInterfaceFont(),
            relief=None,
            pos=(-0.735, 0, -0.1),
            scale=0.12,
            command=self.__loadPresetAndUpdate
        )
        self.deleteExitButton = DirectButton(
            parent=self.invFrame, image=(
                trashcanGui.find('**/TrashCan_OPEN'),
                trashcanGui.find('**/TrashCan_CLSD'),
                trashcanGui.find('**/TrashCan_RLVR')
            ),
            text=('', TTLocalizer.InventoryDone, TTLocalizer.InventoryDone),
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            text_scale=0.1,
            text_pos=(0, -0.1),
            text_font=getInterfaceFont(),
            textMayChange=0,
            relief=None,
            pos=(-1, 0, -0.35),
            scale=1.0
        )
        trashcanGui.removeNode()
        presetGui.removeNode()
        self.deleteHelpText = DirectLabel(
            parent=self.invFrame,
            relief=None,
            pos=(0.272, 0.3, -0.907),
            text=TTLocalizer.InventoryDeleteHelp,
            text_fg=(0, 0, 0, 1),
            text_scale=0.08,
            textMayChange=0
        )
        self.deleteHelpText.hide()

        # Total Gags & Pink slips
        self.totalLabel = DirectLabel(
            text='',
            parent=self.detailFrame,
            pos=(0.02, 0, -0.08),
            scale=0.07,
            text_font=getInterfaceFont(),
            relief=None
        )
        self.dialog = None
        self.updateTotalPropsText()
        self.quickShopper.load()

    def numItem(self, track, level):
        pipsqueak = self.toon.getStatusEffectOfId(SEE.EFFECT_PIP_COUNTER)
        if pipsqueak:
            if track != AttackEnum.TOON_DICE and not self.toon.getStatusEffectOfId(SEE.EFFECT_HR_TOON_GAGS_UNLOCKED):
                # They haven't gotten the gag unlocker. No items!!!
                return 0
            pointCount = pipsqueak.getPointCount()
            canAfford = pointCount >= HighRollerGlobals.getPipCost(base.localAvatar, track, level)
            return int(canAfford)
        return super().numItem(track, level)

    @ignore_event
    def __handleSelection(self, track, level, alt):
        if self.activateMode == 'purchaseDelete' or self.activateMode == 'bookDelete' or self.activateMode == 'storePurchaseDelete':
            self.handleDelete(track, level, alt)
        elif self.activateMode == 'counterfeit':
            self.handleCounterfeit(track, level, alt)
        # elif self.gagTutMode:
            # pass
        else:
            messenger.send('inventory-selection' + ('-alt' if alt else ''), [track, level])

    @ignore_event
    def __handleRun(self):
        messenger.send('inventory-run')

    @ignore_event
    def __handleFire(self, alt):
        messenger.send('inventory-fire' + ('-alt' if alt else ''))

    @ignore_event
    def __handleSue(self, alt):
        messenger.send('inventory-sue' + ('-alt' if alt else ''))

    @ignore_event
    def __handleCounterfeit(self, alt):
        if self.activateMode == 'counterfeit':
            # Tell the inventory UI to just go back instead of doing anything
            messenger.send('counterfeit-done', [dict(mode='Back')])
        else:
            messenger.send('inventory-counterfeit' + ('-alt' if alt else ''))

    @ignore_event
    def __handleSOS(self):
        messenger.send('inventory-sos')

    @ignore_event
    def __handlePass(self, alt):
        messenger.send('inventory-pass' + ('-alt' if alt else ''))

    @ignore_event
    def __handleSurrender(self):
        messenger.send('inventory-surrender')

    def __handleBackToPlayground(self):
        messenger.send('inventory-back-to-playground')

    def __zeroInvConfirm(self):
        self.cleanupDialog()
        self.dialog = TTDialog.TTDialog(
            style=TTDialog.YesNo,
            text=TTLocalizer.InventoryDeleteConfirm,
            command=self.__zeroInvAndUpdate
        )
        self.dialog.show()

    def __zeroInvAndUpdate(self, value):
        self.cleanupDialog()

        if value > 0:
            self.zeroInv()
            self.updateGUI()

    def disablePresetButtons(self):
        self.savePresetButton['text'] = ''
        self.loadPresetButton['text'] = ''
        self.savePresetButton['state'] = DGG.DISABLED
        self.loadPresetButton['state'] = DGG.DISABLED
        for tracks in base.localAvatar.inventory.buttons.values():
            for g in tracks:
                g['state'] = DGG.DISABLED

    def enablePresetButtons(self):
        self.savePresetButton['state'] = DGG.NORMAL
        self.loadPresetButton['state'] = DGG.NORMAL
        self.savePresetButton['text'] = ('', TTLocalizer.InventorySavePreset, TTLocalizer.InventorySavePreset)
        self.loadPresetButton['text'] = ('', TTLocalizer.InventoryLoadPreset, TTLocalizer.InventoryLoadPreset)
        for tracks in base.localAvatar.inventory.buttons.values():
            for g in tracks:
                g['state'] = DGG.NORMAL

    def __savePresetConfirm(self):
        if hasattr(self, 'presetDialog') and self.presetDialog:
            self.presetDialog.cleanup()
        self.disablePresetButtons()

        def handleConfirmResponse(value):
            if not hasattr(self, 'presetDialog') or not self.presetDialog:
                return
            self.presetDialog.cleanup()
            del self.presetDialog
            if value == 1:
                self.saveGagPreset()
                self.updateGUI()
                base.localAvatar.setSystemMessage(0, TTLocalizer.GagShopPresetSaved, WTSystem)
            self.enablePresetButtons()

        self.presetDialog = TTDialog.TTDialog(
            parent=aspect2d,
            text=TTLocalizer.InventorySavePresetConfirm,
            text_scale=0.06,
            text_align=TextNode.ACenter,
            text_wordwrap=15,
            command=handleConfirmResponse,
            fadeScreen=0.5,
            style=TTDialog.YesNo,
            buttonPadSF=4,
            sortOrder=NO_FADE_SORT_INDEX
        )
        self.presetDialog.show()
        print('dialog bin:', self.presetDialog.getBinName(), self.presetDialog.getBinDrawOrder())
        print('parent:', self.presetDialog.getParent())

    def __loadPresetAndUpdate(self):
        if hasattr(self, 'presetDialog') and self.presetDialog:
            self.presetDialog.cleanup()
        self.disablePresetButtons()
        allowedToLoad = self.canToonLoadPreset()
        if allowedToLoad[0]:  # Toon has enough money
            def handleConfirmResponse(value):
                if hasattr(self, 'presetDialog'):
                    self.presetDialog.cleanup()
                    del self.presetDialog
                if value == 1:
                    self.loadGagPreset()
                    self.updateGUI()
                    base.localAvatar.setSystemMessage(0, TTLocalizer.GagShopRestocked, WTSystem)
                self.enablePresetButtons()

            self.presetDialog = TTDialog.TTDialog(
                parent=aspect2d,
                text=TTLocalizer.InventoryLoadConfirm % {
                    'cost': allowedToLoad[1],
                    'money': self.toon.getMoney()
                },
                text_scale=0.06,
                text_align=TextNode.ACenter,
                text_wordwrap=20,
                command=handleConfirmResponse,
                fadeScreen=0.5,
                style=TTDialog.YesNo,
                buttonPadSF=4,
                sortOrder=NO_FADE_SORT_INDEX
            )
            self.presetDialog.show()
        else:
            def handleConfirmResponse(value):
                self.presetDialog.cleanup()
                del self.presetDialog
                self.enablePresetButtons()

            self.presetDialog = TTDialog.TTDialog(
                parent=aspect2d,
                text=TTLocalizer.InventoryLoadPresetFail % {
                    'cost': allowedToLoad[1],
                    'money': self.toon.getMoney()
                },
                text_scale=0.06,
                text_align=TextNode.ACenter,
                text_wordwrap=20,
                command=handleConfirmResponse,
                fadeScreen=0.5,
                style=TTDialog.Acknowledge,
                buttonPadSF=4,
                sortOrder=NO_FADE_SORT_INDEX
            )
            self.presetDialog.show()

    def handleDelete(self, track, level, alt):
        if alt:
            self.quickShopper.activate(lambda: self.deleteItem(track, level))
        else:
            self.deleteItem(track, level)

    def deleteItem(self, track, level):
        returnCode = self.numItem(track, level)
        if returnCode > 0:
            self.useItem(track, level)
            self.updateGUI(track, level)
            self.showDetail(track, level)
        return returnCode

    def handleCounterfeit(self, track, level, alt):
        messenger.send('counterfeit-done', [dict(mode='CopyGag', gagTrack=track, gagLevel=level)])

    def showDetail(self, track, level, event=None):
        self.totalLabel.hide()
        self.detailNameLabel.show()
        self.detailAmountLabel.show()
        self.detailDataLabel.show()

        self.detailEmblem.setValues(track, level, self.toon, townBattle=self.getTownBattle())

        if not (0 <= track < len(Tracks)):
            # Normal pills
            if track == AttackEnum.TOON_DICE:
                self.detailNameLabel.configure(text=HighRollerGlobals.InventoryDiceName.get(level))
                self.detailDataLabel.configure(text=HighRollerGlobals.InventoryDiceDescription.get(level) + self.getSkillCreditSubtitleOverride(AttackEnum.TOON_DICE, level))
                self.detailAmountLabel.configure(text=self.getInventoryDetailAmountText(track, level))
        else:
            self.detailNameLabel.configure(text=AvPropStrings[track][level])  # Detail Panel - Gag Name
            self.detailAmountLabel.configure(text=self.getInventoryDetailAmountText(track, level))

            if self.activateMode == 'counterfeit':
                counterfeitUsageEffect = self.toon.getStatusEffectOfId(SEE.EFFECT_COUNTERFEIT_USAGE_CONTAINER)
                if counterfeitUsageEffect and counterfeitUsageEffect.getGagTrackLevel(track, level):
                    self.detailDataLabel.configure(
                        text=TTLocalizer.InventoryCounterfeitAlreadyUsedHover.format(gagName=TTLocalizer.BattleGlobalAvPropStringsSingular[track][level])
                    )
                else:
                    maxLevel = BattleGlobals.MAX_LEVEL_INDEX
                    for gagModifier in base.localAvatar.getModifiersOfType(ModifierType.GagsContentSync):
                        maxLevel = min(maxLevel, gagModifier.getMaxGagLevel())

                    retDict = BattleGlobals.getCounterfeitCooldownsForMaxLevel(maxLevel)
                    gagCd = retDict.get(level, 0)
                    gagCdStr = f'\n\1TextSmaller\1\n\2 \1white\1\5battle_reward_cooldownIcon_counterfeit\5\2  \1deepBlue\1Rounds\2: {gagCd}' if gagCd else ''

                    notEnoughStr = TTLocalizer.InventoryCounterfeitNotEnoughHover if base.localAvatar.getCounterfeits() < level+1 else ''

                    self.detailDataLabel.configure(
                        text=f'\1TextSubtitle\1\n \1white\1\5battle_counterfeitIcon_counterfeit\5\2  \1deepGreen\1Cost\2: {level+1}{gagCdStr}{notEnoughStr}\2'
                    )
                return

            bonus = self.toon.checkGagBonus(track, level) or self.checkPropBonus(track)
            if track == AttackEnum.TOON_LURE:
                damage = NumRoundsLured[level]
            else:
                damage = getAvPropDamage(track, level, self.getToonExperience(track))
            damageBonusStr = ''
            damageBonus = 0
            if bonus:
                damageBonus = getDamageBonus(damage, level, track)
            if track == AttackEnum.TOON_HEAL:
                bonus = math.ceil(damage * ToonupSelfHealAmt[bonus])
                damageBonusStr = TTLocalizer.InventoryDamageBonusString % TTLocalizer.HealExtraText % {
                    'heal': bonus
                }

            if damageBonus:
                damageBonusStr = TTLocalizer.InventoryDamageBonus % damageBonus

            if track == AttackEnum.TOON_TRAP:
                acc = 100
            else:
                acc = AvPropAccuracy[track][level]

            localString = calculateAccuracyString(acc, track=track)
            accString = f'{acc}% ({localString})'

            if track in (AttackEnum.TOON_LURE, AttackEnum.TOON_SOUND) or (track in (AttackEnum.TOON_THROW,) and bonus):
                self.detailDataLabel.configure(
                    text=TTLocalizer.InventoryDetailDataExtra % {
                        'hitStr': TTLocalizer.InventoryDetailBaseHitStr,
                        'accuracy': accString,
                        'damageString': self.getDmgStr(track, level),
                        'damage': f'{damage}',
                        'bonus': damageBonusStr if track != AttackEnum.TOON_LURE else '',
                        'singleOrGroup': self.getSingleGroupStr(track, level),
                        'extra': self.getExtraText(track, level, bonus, damage)
                    }
                )  # Gag Details Text
            elif track == AttackEnum.TOON_SQUIRT:
                self.detailDataLabel.configure(
                    text=TTLocalizer.InventoryDetailDataExtra % {
                        'hitStr': TTLocalizer.InventoryDetailBaseHitStr,
                        'accuracy': accString,
                        'damageString': self.getDmgStr(track, level),
                        'damage': f'{damage}',
                        'bonus': damageBonusStr,
                        # Swapped so that splash damage shows right below damage.
                        'singleOrGroup': TTLocalizer.SquirtExtraText % math.ceil(damage * SplashDamageAmt[bonus]),
                        'extra': self.getSingleGroupStr(track, level) + f'\n{self.getExtraText(track, level, bonus, damage)}'
                    }
                )  # Gag Details Text
            elif track == AttackEnum.TOON_TRAP:
                eliteDamage = math.ceil(damage * TrapEliteBonus)
                eliteBonus = (TTLocalizer.InventoryDamageBonus % getDamageBonus(eliteDamage, level, track=track)) if bonus else ''
                self.detailDataLabel.configure(
                    text=TTLocalizer.InventoryDetailDataExtra % {
                        'hitStr': TTLocalizer.InventoryDetailBaseHitStr,
                        'accuracy': accString,
                        'damageString': self.getDmgStr(track, level),
                        'damage': f'{damage}',
                        'bonus': damageBonusStr,
                        # Swapped so that exec damage shows right below damage.
                        'singleOrGroup': f"{self.getExtraText(track, level, bonus, eliteDamage)}{eliteBonus}",
                        'extra': self.getSingleGroupStr(track, level)
                    }
                )  # Gag Details Text
            elif track == AttackEnum.TOON_ZAP:
                self.detailDataLabel.configure(
                    text=TTLocalizer.InventoryDetailDataExtra % {
                        'hitStr': TTLocalizer.InventoryDetailHitStr,
                        'accuracy': accString,
                        'damageString': self.getDmgStr(track, level),
                        'damage': f'{damage}',
                        'bonus': damageBonusStr,
                        # These are swapped so that damage falloff shows right below damage.
                        'singleOrGroup': self.getExtraText(track, level, bonus, damage),
                        'extra': self.getSingleGroupStr(track, level)
                    }
                )  # Gag Details Text
            else:
                # Gag Details Text
                self.detailDataLabel.configure(
                    text=TTLocalizer.InventoryDetailData % {
                        'hitStr': TTLocalizer.InventoryDetailBaseHitStr,
                        'accuracy': accString,
                        'damageString': self.getDmgStr(track, level),
                        'damage': f'{damage}',
                        'bonus': damageBonusStr,
                        'singleOrGroup': self.getSingleGroupStr(track, level)
                    }
                )

            # Calculate gag xp display if outside of battle
            gagExpMult = self.battleCreditMult + self.liveCreditMult
            gagExpMult = base.localAvatar.applyBoosters([BoosterItemType.Exp_Gags_Support,
                                                         BoosterItemType.Exp_Gags_Power,
                                                         BoosterItemType.Exp_Gags_Global], gagExpMult, track)

            # Apply any playground gag bonuses.
            zoneId = ZoneUtil.getHoodId(base.localAvatar.zoneId)
            gagExpMult += base.localAvatar.getPlaygroundGagMultiplier(zoneId)

            if self.itemIsCredit(track, level):
                self.setDetailCredit(track, (level + 1) * gagExpMult, level)
            else:
                self.setDetailCredit(track, None, level)

    def getInventoryDetailAmountText(self, track, level) -> str:
        """
        Gets the gag quantity for the inventory detail amount text.
        (This is on the detail panel.)
        """
        # Be careful out there. Monsters are lurking.
        if not self.toon:
            return TTLocalizer.InventoryDetailAmount % {
                'numItems': self.numItem(track, level),
                'maxItems': self.getMax(track, level)
            }

        # Check for Pips
        pipsqueak = self.toon.getStatusEffectOfId(SEE.EFFECT_PIP_COUNTER)
        if pipsqueak:
            pointCount = pipsqueak.getPointCount()
            usedPointCount = pointCount - HighRollerGlobals.getPipCost(base.localAvatar, track, level)
            if usedPointCount >= 0:
                return f'{pointCount} Pip{text.plural(pointCount)} -> {usedPointCount} Pip{text.plural(usedPointCount)}'
            else:
                return f'\1deepRed\1{pointCount} Pip{text.plural(pointCount)} -> {usedPointCount} Pip{text.plural(usedPointCount)}\2'

        elif track == AttackEnum.TOON_DICE:
            # If it is a raw dice, just return its cost.
            # This probably won't exist ever, but good for debugging
            cost = HighRollerGlobals.getPipCost(base.localAvatar, track, level)
            return f'{cost} Pip{text.plural(cost)}'

        # No override exists.
        numItemText = self.numItem(track, level)
        counterfeit = self.toon.getStatusEffectOfId(SEE.EFFECT_COUNTERFEIT_CONTAINER)
        if counterfeit and counterfeit.getGagTrackLevel(track, level):
            numItemText = f'\1deepGreen\1{numItemText}+1\2'
        return TTLocalizer.InventoryDetailAmount % {
                'numItems': numItemText,
                'maxItems': self.getMax(track, level)
            }

    def setDetailCredit(self, track, credit, level):
        if credit is not None:
            credit = credit * InherentTrackExpMult.get(track, 1)
            if self.toon.earnedExperience:
                maxCredit = ExperienceCap - self.toon.earnedExperience[track]
                credit = min(credit, maxCredit)
            credit = int(credit * 10 + 0.5)
            if credit % 10 == 0:
                credit //= 10
            else:
                credit //= 10.0

        skillCreditSubtitle = self.getSkillCreditSubtitleOverride(track, level)

        if not skillCreditSubtitle:
            if credit is not None:
                skillCreditSubtitle = '\n\n' + TTLocalizer.InventorySkillCredit % credit
            else:
                skillCreditSubtitle = '\n\n\1TextRed\1' + TTLocalizer.InventorySkillCreditNone + '\2'

        self.detailDataLabel['text'] = self.detailDataLabel['text'] + skillCreditSubtitle

    def getSkillCreditSubtitleOverride(self, track, level) -> str:
        # Be careful out there. Monsters are lurking.
        if not self.toon:
            return ''

        if self.activateMode == 'counterfeit':
            # We need this to go away while in counterfeit mode
            # Singular space so it's actually empty
            return ' '

        # Check for Pips
        pipsqueak = self.toon.getStatusEffectOfId(SEE.EFFECT_PIP_COUNTER)
        if pipsqueak:
            return f'\n\nPip cost: {HighRollerGlobals.getPipCost(base.localAvatar, track, level)}'

        # No override exists.
        return ''

    def hideDetail(self, event=None):
        self.detailEmblem.clearValues()
        self.totalLabel.show()
        self.detailNameLabel.hide()
        self.detailAmountLabel.hide()
        self.detailDataLabel.hide()

    def noDetail(self):
        self.totalLabel.hide()
        self.detailNameLabel.hide()
        self.detailAmountLabel.hide()
        self.detailDataLabel.hide()

    def setActivateMode(self, mode, heal=1, trap=1, lure=1, sue=1, isStreet=False, creditLevel=None, tutorialFlag=0,
                        allSuitsUntouchable=False, allSuitsUntouchableNoTrap=False):
        self.notify.debug(f'setActivateMode() mode:{mode} heal:{heal} trap:{trap} lure:{lure} sue{sue} isStreet:{isStreet}')
        self.previousActivateMode = self.activateMode
        self.activateMode = mode
        self.deactivateButtons()
        self.canHeal = heal
        self.canTrap = trap
        self.canLure = lure
        self.canSue = sue
        self.allSuitsUntouchable = allSuitsUntouchable
        self.allSuitsUntouchableNoTrap = allSuitsUntouchableNoTrap
        self.isStreet = isStreet
        if mode == "battle":
            self.countInvasions = False
        elif mode != "battle" and isStreet:
            self.countInvasions = True
        self.battleCreditLevel = creditLevel
        self.tutorialFlag = tutorialFlag
        self.__activateButtons()
        self.enableUberGags()

    def setActivateModeBroke(self):
        if self.activateMode == 'storePurchase':
            self.setActivateMode('storePurchaseBroke')
        elif self.activateMode == 'purchase':
            self.setActivateMode('purchaseBroke')
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
        elif self.previousActivateMode == 'battle':
            self.battleDeactivateButtons()
        elif self.previousActivateMode == 'counterfeit':
            self.counterfeitDeactivateButtons()
        elif self.previousActivateMode == 'storePurchaseDelete':
            self.storePurchaseDeleteDeactivateButtons()
        elif self.previousActivateMode == 'storePurchase':
            self.storePurchaseDeactivateButtons()
        elif self.previousActivateMode == 'storePurchaseBroke':
            self.storePurchaseBrokeDeactivateButtons()
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
            elif self.activateMode == 'battle':
                self.battleActivateButtons()
            elif self.activateMode == 'counterfeit':
                self.counterfeitActivateButtons()
            elif self.activateMode == 'storePurchaseDelete':
                self.storePurchaseDeleteActivateButtons()
            elif self.activateMode == 'storePurchase':
                self.storePurchaseActivateButtons()
            elif self.activateMode == 'storePurchaseBroke':
                self.storePurchaseBrokeActivateButtons()
            else:
                self.notify.error('No such mode as %s' % self.activateMode)
        return None

    def bookActivateButtons(self):
        self.setPos(0, 0, 0.52)
        self.setScale(1.0)

        self.detailFrame.setPos(0.073, 0, -0.375)
        self.detailFrame.setScale(0.26)

        self.savePresetButton.hide()
        self.loadPresetButton.hide()

        self.deleteEnterButton.show()
        self.deleteEnterButton.setPos(-0.37, 0, -0.32)
        self.deleteEnterButton.setScale(0.25)
        self.deleteExitButton.hide()
        self.deleteEnterButton.setPos(-0.37, 0, -0.32)
        self.deleteEnterButton.setScale(0.25)

        self.invFrame.reparentTo(self)
        self.invFrame.setPos(-0.05, 0, -0.34)
        self.invFrame.setScale(1.9)

        self.deleteEnterButton['command'] = self.setActivateMode
        self.deleteEnterButton['extraArgs'] = ['bookDelete']

        for track in self.getGagOrder():
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
        return

    def bookDeleteActivateButtons(self):
        messenger.send('enterBookDelete')

        self.deleteEnterButton.hide()
        self.deleteEnterButton.setPos(-0.37, 0, -0.32)
        self.deleteEnterButton.setScale(0.25)

        self.deleteExitButton.show()
        self.deleteExitButton.setPos(-0.37, 0, -0.32)
        self.deleteExitButton.setScale(0.25)

        self.deleteHelpText.hide()

        self.invFrame.reparentTo(self)
        self.invFrame.setPos(-0.05, 0, -0.34)
        self.invFrame.setScale(1.9)

        self.deleteExitButton['command'] = self.setActivateMode
        self.deleteExitButton['extraArgs'] = [self.previousActivateMode]

        self.needUpdateInventory = True

        for track in self.getGagOrder():
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
        self.deleteEnterButton.setScale(0.5)
        self.deleteEnterButton.show()
        self.deleteDeactivateButtons()

    def purchaseDeleteActivateButtons(self):
        self.reparentTo(aspect2d)
        self.setPos(0, 0, 0.2)
        self.setScale(1)
        messenger.send(InventoryScalingChangedEvent)

        if self.purchaseFrame is None:
            self.loadPurchaseFrame()
        self.purchaseFrame.show()

        self.invFrame.reparentTo(self.purchaseFrame)
        self.invFrame.setPos(-0.02, 0, 0)
        self.invFrame.setScale(1.48)

        self.detailFrame.setPos(0.669, 0, 0.285)
        self.detailFrame.setScale(0.5)

        self.deleteEnterButton.hide()
        self.deleteEnterButton.setPos(-0.67, 0, -0.21)
        self.deleteEnterButton.setScale(0.3)

        self.deleteExitButton.show()
        self.deleteExitButton.setPos(-0.67, 0, -0.21)
        self.deleteExitButton.setScale(0.3)
        self.deleteExitButton['command'] = self.setActivateMode
        self.deleteExitButton['extraArgs'] = [self.previousActivateMode]

        for track in self.getGagOrder():
            if self.toon.hasTrackAccess(track):
                self.showTrack(track)
                for level in range(len(Levels[track])):
                    button = self.buttons[track][level]
                    if self.itemIsUsable(track, level):
                        button.show()
                        if self.numItem(track, level) <= 0 or level > LAST_REGULAR_GAG_LEVEL:
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
        for track in self.getGagOrder():
            if self.toon.hasTrackAccess(track):
                self.showTrack(track)
                for level in range(len(Levels[track])):
                    button = self.buttons[track][level]
                    if self.itemIsUsable(track, level):
                        button.show()
                        if self.numItem(track, level) <= 0 or level >= LAST_REGULAR_GAG_LEVEL:
                            self.makeUnpressable(button, track, level)
                        else:
                            self.makeDeletePressable(button, track, level)
                    else:
                        button.hide()
            else:
                self.hideTrack(track)

    def storePurchaseDeleteActivateButtons(self):
        self.reparentTo(aspect2d)
        self.setPos(0, 0, 0)
        self.setScale(1)
        messenger.send(InventoryScalingChangedEvent)

        if self.storePurchaseFrame is None:
            self.loadStorePurchaseFrame()
        self.storePurchaseFrame.show()

        self.invFrame.reparentTo(self.storePurchaseFrame)
        self.invFrame.setPos(-0.02, 0, 0)
        self.invFrame.setScale(1.48)

        self.detailFrame.setPos(0.669, 0, 0.12)
        self.detailFrame.setScale(0.5)

        self.deleteEnterButton.hide()
        self.deleteEnterButton.setPos(-0.67, 0, -0.21)
        self.deleteEnterButton.setScale(0.3)

        self.deleteExitButton.show()
        self.deleteExitButton.setPos(-0.67, 0, -0.21)
        self.deleteExitButton.setScale(0.3)
        self.deleteExitButton['command'] = self.setActivateMode
        self.deleteExitButton['extraArgs'] = [self.previousActivateMode]

        for track in self.getGagOrder():
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
        return

    def storePurchaseDeleteDeactivateButtons(self):
        self.invFrame.reparentTo(self)
        self.storePurchaseFrame.hide()
        self.deleteDeactivateButtons()

    def storePurchaseBrokeActivateButtons(self):
        self.reparentTo(aspect2d)
        self.setPos(0, 0, 0)
        self.setScale(1)

        if self.storePurchaseFrame is None:
            self.loadStorePurchaseFrame()
        self.storePurchaseFrame.show()

        self.invFrame.reparentTo(self.storePurchaseFrame)
        self.invFrame.setPos(-0.02, 0, 0)
        self.invFrame.setScale(1.48)

        self.detailFrame.setPos(0.669, 0, 0.12)
        self.detailFrame.setScale(0.5)

        self.deleteEnterButton.show()
        self.deleteEnterButton.setPos(-0.67, 0, -0.21)
        self.deleteEnterButton.setScale(0.3)

        self.deleteExitButton.hide()
        self.deleteExitButton.setPos(-0.67, 0, -0.21)
        self.deleteExitButton.setScale(0.3)

        self.savePresetButton.show()
        self.loadPresetButton.show()

        for track in self.getGagOrder():
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

        for track in self.getGagOrder():
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
        self.setPos(0, 0, 0.2)
        self.setScale(1)
        messenger.send(InventoryScalingChangedEvent)

        if self.purchaseFrame is None:
            self.loadPurchaseFrame()
        self.purchaseFrame.show()

        self.invFrame.reparentTo(self.purchaseFrame)
        self.invFrame.setPos(-0.02, 0, 0)
        self.invFrame.setScale(1.48)

        self.detailFrame.setPos(0.669, 0, 0.285)
        self.detailFrame.setScale(0.5)

        self.deleteEnterButton.show()
        self.deleteEnterButton.setPos(-0.67, 0, -0.21)
        self.deleteEnterButton.setScale(0.3)

        self.deleteExitButton.hide()
        self.deleteExitButton.setPos(-0.67, 0, -0.21)
        self.deleteExitButton.setScale(0.3)

        self.savePresetButton.show()
        self.loadPresetButton.show()

        self.deleteEnterButton['command'] = self.setActivateMode
        self.deleteEnterButton['extraArgs'] = ['purchaseDelete']
        totalProps = self.totalProps
        maxProps = self.toon.getMaxCarry()

        for track in self.getGagOrder():
            if self.toon.hasTrackAccess(track):
                self.showTrack(track)
                for level in range(len(Levels[track])):
                    button = self.buttons[track][level]
                    if self.itemIsUsable(track, level):
                        button.show()
                        if self.numItem(track, level) >= self.getMax(track, level) or \
                                totalProps >= maxProps or level > LAST_REGULAR_GAG_LEVEL:
                            self.makeUnpressable(button, track, level)
                        elif base.localAvatar.getMoney() < (level + 1):
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
        self.setPos(0, 0, 0)
        self.setScale(1)
        messenger.send(InventoryScalingChangedEvent)

        if self.storePurchaseFrame is None:
            self.loadStorePurchaseFrame()
        self.storePurchaseFrame.show()

        self.invFrame.reparentTo(self.storePurchaseFrame)
        self.invFrame.setPos(-0.02, 0, 0)
        self.invFrame.setScale(1.48)

        self.detailFrame.setPos(0.669, 0, 0.12)
        self.detailFrame.setScale(0.5)

        self.deleteEnterButton.show()
        self.deleteEnterButton.setPos(-0.67, 0, -0.21)
        self.deleteEnterButton.setScale(0.3)

        self.deleteExitButton.hide()
        self.deleteExitButton.setPos(-0.67, 0, -0.21)
        self.deleteExitButton.setScale(0.3)

        self.savePresetButton.show()
        self.loadPresetButton.show()

        self.deleteEnterButton['command'] = self.setActivateMode
        self.deleteEnterButton['extraArgs'] = ['storePurchaseDelete']
        totalProps = self.totalProps
        maxProps = self.toon.getMaxCarry()
        for track in self.getGagOrder():
            if self.toon.hasTrackAccess(track):
                self.showTrack(track)
                for level in range(len(Levels[track])):
                    button = self.buttons[track][level]
                    if self.itemIsUsable(track, level):
                        button.show()
                        if self.numItem(track, level) >= self.getMax(track, level) or \
                                totalProps >= maxProps or level > LAST_REGULAR_GAG_LEVEL:
                            self.makeUnpressable(button, track, level)
                        elif base.localAvatar.getMoney() < (level + 1):
                            self.makeUnpressable(button, track, level)
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
        self.setPos(0, 0, 0.2)
        self.setScale(1)
        messenger.send(InventoryScalingChangedEvent)

        if self.purchaseFrame is None:
            self.loadPurchaseFrame()
        self.purchaseFrame.show()

        self.invFrame.reparentTo(self.purchaseFrame)
        self.invFrame.setPos(-0.02, 0, 0)
        self.invFrame.setScale(1.48)

        self.detailFrame.setPos(0.669, 0, 0.285)
        self.detailFrame.setScale(0.5)

        self.deleteEnterButton.show()
        self.deleteEnterButton.setPos(-0.67, 0, -0.21)
        self.deleteEnterButton.setScale(0.3)

        self.deleteExitButton.hide()
        self.deleteExitButton.setPos(-0.67, 0, -0.21)
        self.deleteExitButton.setScale(0.3)

        self.savePresetButton.show()
        self.loadPresetButton.show()

        # if self.gagTutMode:
        #     self.deleteEnterButton.hide()
        for track in self.getGagOrder():
            if self.toon.hasTrackAccess(track):
                self.showTrack(track)
                for level in range(len(Levels[track])):
                    button = self.buttons[track][level]
                    if self.itemIsUsable(track, level):
                        button.show()
                        # if not self.gagTutMode:
                        self.makeUnpressable(button, track, level)
                    else:
                        button.hide()
            else:
                self.hideTrack(track)
        return

    def purchaseBrokeDeactivateButtons(self):
        self.invFrame.reparentTo(self)
        self.purchaseFrame.hide()

    def battleActivateButtons(self):
        self.stopAndClearPropBonusIval()
        self.reparentTo(aspect2d)
        self.setPos(0, 0, 0)
        self.setScale(1)

        messenger.send(InventoryScalingChangedEvent)
        if self.battleFrame is None:
            self.loadBattleFrame()
        self.battleFrame.show()
        self.battleFrame.setPos(-0.7, 0, 0)
        self.battleFrame.setScale(0.9)

        self.invFrame.reparentTo(self.guiElements[BattleGUI.TRACK_HOLDER_FRAME])
        self.invFrame.setPos(0.67, 0, 0)
        self.invFrame.setScale(1.85)

        self.detailFrame.setPos(0.61, 0, 0.019)  # Battle thing
        self.detailFrame.setScale(0.4)

        self.guiElements[BattleGUI.TOTAL_GAGS_FRAME].hide()  # Hiding this. Remove this if we end up not using it.

        self.savePresetButton.hide()
        self.loadPresetButton.hide()

        self.deleteEnterButton.hide()
        self.deleteExitButton.hide()

        # Tutorial
        if self.tutorialFlag:
            self.runButton.hide()
            self.surrenderButton.hide()
            self.sosButton.hide()
            self.passButton.hide()
            self.fireButton.hide()
            self.sueButton.hide()
            self.counterfeitButton.hide()
        # If inside bldg, facility, boss
        elif self.isStreet is False:
            self.runButton.hide()
            self.surrenderButton.show()
            self.runButton['text'] = ('', '', '')
            if self.surrenderButtonFlag.surrenderActive:
                self.surrenderButton['text'] = ('', '', '')
            else:
                self.surrenderButton['text'] = ('', TTLocalizer.InventorySurrender, TTLocalizer.InventorySurrender)
            self.surrenderButton['state'] = DGG.NORMAL
            self.passButton.show()
            self.sosButton.show()
            self.fireButton.show()
            self.sueButton.show()
            self.counterfeitButton.show()
        # street battle
        else:
            self.runButton.show()
            self.surrenderButton.hide()
            self.runButton['state'] = DGG.NORMAL
            self.runButton['text'] = ('', TTLocalizer.InventoryRun, TTLocalizer.InventoryRun)
            self.surrenderButton['text'] = ('', '', '')
            self.runButton['image_color'] = Vec4(1, 1, 1, 1)
            self.sosButton.show()
            self.passButton.show()
            self.fireButton.show()
            self.sueButton.show()
            self.counterfeitButton.show()

        # Update counts
        self.updateTotalPropsText()

        self.updateRewardButtons()

        self.updateInventoryButtonsForModifiers()

        self.ignore(TTSCUniteStateChangedEvent)
        self.accept(TTSCUniteStateChangedEvent, self.updateRewardButtons)
        return

    def updateRewardButtons(self):
        rewardsDisabled = bool(base.localAvatar.getStatusEffectsOfType(StatusEffects.RewardCooldownStatusEffect))

        # Pink slip
        if base.localAvatar.getPinkSlips() > 0 and not self.allSuitsUntouchable and not rewardsDisabled:
            self.fireButton['state'] = DGG.NORMAL
            self.fireButton['image_color'] = Vec4(1, 1, 1, 1)
        else:
            self.fireButton['state'] = DGG.DISABLED
            self.fireButton['image_color'] = Vec4(0.4, 0.4, 0.4, 1)

        # C&D
        if base.localAvatar.getCeaseDesists() > 0 and self.canSue and not rewardsDisabled:
            self.sueButton['state'] = DGG.NORMAL
            self.sueButton['image_color'] = Vec4(1, 1, 1, 1)
        else:
            self.sueButton['state'] = DGG.DISABLED
            self.sueButton['image_color'] = Vec4(0.4, 0.4, 0.4, 1)

        # Counterfeit
        if base.localAvatar.getCounterfeits() > 0 and not rewardsDisabled:
            self.counterfeitButton['state'] = DGG.NORMAL
            self.counterfeitButton['image_color'] = Vec4(1, 1, 1, 1)
        else:
            self.counterfeitButton['state'] = DGG.DISABLED
            self.counterfeitButton['image_color'] = Vec4(0.4, 0.4, 0.4, 1)

    def battleDeactivateButtons(self):
        self.invFrame.reparentTo(self)
        self.battleFrame.hide()
        self.stopAndClearPropBonusIval()
        self.ignore(TTSCUniteStateChangedEvent)

    def counterfeitActivateButtons(self):
        self.stopAndClearPropBonusIval()
        self.reparentTo(aspect2d)
        self.setPos(0, 0, 0)
        self.setScale(1)

        messenger.send(InventoryScalingChangedEvent)
        if self.battleFrame is None:
            self.loadBattleFrame()
        self.battleFrame.show()
        self.battleFrame.setPos(-0.7, 0, 0)
        self.battleFrame.setScale(0.9)

        self.invFrame.reparentTo(self.guiElements[BattleGUI.TRACK_HOLDER_FRAME])
        self.invFrame.setPos(0.67, 0, 0)
        self.invFrame.setScale(1.85)

        self.detailFrame.setPos(0.61, 0, 0.019)  # Battle thing
        self.detailFrame.setScale(0.4)

        self.guiElements[BattleGUI.TOTAL_GAGS_FRAME].hide()  # Hiding this. Remove this if we end up not using it.

        self.savePresetButton.hide()
        self.loadPresetButton.hide()

        self.deleteEnterButton.hide()
        self.deleteExitButton.hide()

        # Tutorial
        if self.tutorialFlag:
            self.runButton.hide()
            self.sosButton.hide()
            self.passButton.hide()
            self.fireButton.hide()
            self.sueButton.hide()
            self.counterfeitButton.hide()
        # If inside bldg, facility, boss
        elif self.isStreet is False:
            self.runButton.show()
            self.runButton['text'] = ('', '', '')
            self.runButton['state'] = DGG.DISABLED
            self.runButton['image_color'] = Vec4(0.4, 0.4, 0.4, 1)
            self.sosButton.show()
            self.passButton.show()
            self.fireButton.show()
            self.sueButton.show()
            self.counterfeitButton.show()
        # street battle
        else:
            self.runButton.show()
            self.runButton['state'] = DGG.NORMAL
            self.runButton['text'] = ('', TTLocalizer.InventoryRun, TTLocalizer.InventoryRun)
            self.runButton['image_color'] = Vec4(1, 1, 1, 1)
            self.sosButton.show()
            self.passButton.show()
            self.fireButton.show()
            self.sueButton.show()
            self.counterfeitButton.show()

        # Update counts
        self.updateTotalPropsText()

        self.updateRewardButtons()

        self.__counterfeitColorButtons()

        self.ignore(TTSCUniteStateChangedEvent)
        self.accept(TTSCUniteStateChangedEvent, self.updateRewardButtons)

        self.finishCounterfeitBackSeq()

        self.counterfeitBackSeq = Parallel(
            Sequence(
                Func(self.counterfeitBackButton.show),
                LerpPosInterval(self.counterfeitBackButton, 0.2, (-0.125, 0, -0.95), blendType='easeOut'),
            ),
            Sequence(
                LerpPosInterval(self.counterfeitButton, 0.2, (1.0, 0, -0.55), blendType='easeIn'),
                Func(self.counterfeitButton.hide),
            ),
            Sequence(
                LerpPosInterval(self.sueButton, 0.2, (1.0, 0, -0.95), blendType='easeIn'),
                Func(self.sueButton.hide),
            ),
            Sequence(
                LerpPosInterval(self.fireButton, 0.2, (1.0, 0, -1.35), blendType='easeIn'),
                Func(self.fireButton.hide),
            ),
        )
        self.counterfeitBackSeq.start()

    def __counterfeitColorButtons(self):
        # Need to separate this so we can also check for it within updateButtonsForBattle
        counterfeitUsageEffect = self.toon.getStatusEffectOfId(SEE.EFFECT_COUNTERFEIT_USAGE_CONTAINER)

        for track in self.getGagOrder():
            if self.toon.hasTrackAccess(track):
                self.showTrack(track)
                for level in range(len(Levels[track])):
                    button = self.buttons[track][level]
                    if self.itemIsUsable(track, level):
                        button.show()
                        canAfford = base.localAvatar.getCounterfeits() >= (level + 1)
                        if canAfford and ((not counterfeitUsageEffect) or (
                            counterfeitUsageEffect and not counterfeitUsageEffect.getGagTrackLevel(track, level))):
                            self.makeColoredPressable(button, track, level, color=self.CounterfeitPressableImageColor)
                        else:
                            self.makeUnpressable(button, track, level)
                    else:
                        button.hide()
            else:
                self.hideTrack(track)

    def counterfeitDeactivateButtons(self):
        self.invFrame.reparentTo(self)
        self.battleFrame.hide()
        self.stopAndClearPropBonusIval()
        self.ignore(TTSCUniteStateChangedEvent)

        self.finishCounterfeitBackSeq()

        self.counterfeitBackSeq = Parallel(
            Sequence(
                LerpPosInterval(self.counterfeitBackButton, 0.2, (1.0, 0, -0.95), blendType='easeIn'),
                Func(self.counterfeitBackButton.hide),
            ),
            Sequence(
                Func(self.counterfeitButton.show),
                LerpPosInterval(self.counterfeitButton, 0.2, (0.0, 0, -0.55), blendType='easeOut'),
            ),
            Sequence(
                Func(self.sueButton.show),
                LerpPosInterval(self.sueButton, 0.2, (0.0, 0, -0.95), blendType='easeOut'),
            ),
            Sequence(
                Func(self.fireButton.show),
                LerpPosInterval(self.fireButton, 0.2, (0.0, 0, -1.35), blendType='easeOut'),
            ),
        )
        self.counterfeitBackSeq.start()

    def finishCounterfeitBackSeq(self):
        if self.counterfeitBackSeq:
            self.counterfeitBackSeq.finish()
            self.counterfeitBackSeq = None

    def finishSurrenderSeq(self):
        if self.surrenderSeq:
            self.surrenderSeq.finish()
            self.surrenderSeq = None

    def fixRewardButtonPos(self):
        self.finishCounterfeitBackSeq()

        if hasattr(self, 'counterfeitBackButton'):
            self.counterfeitBackButton.hide()
            for btn, zPos in zip((self.counterfeitButton, self.sueButton, self.fireButton), (-0.55, -0.95, -1.35)):
                btn.setPos(0, 0, zPos)

        self.lastSurrenderNum = 0

    def itemIsUsable(self, track, level):
        """
        :returns: true if the toon may use this item, false if not.

        Toons may use an item if their experience is greater than or equal to the required points for the item.
        """
        maxLevel = GagsContentSyncModifier.capGagLevel(do=self.toon)
        if level > maxLevel:
            return 0

        forceHas = any(
            gagModifier.getForceMaxed()
            for gagModifier in self.toon.getModifiersOfType(ModifierType.GagsContentSync)
        )
        if forceHas:
            return 1

        curSkill = self.getToonExperience(track)
        if curSkill < Levels[track][level]:
            return 0
        else:
            return 1

    def itemIsCredit(self, track, level):
        """
        :type track: int
        :type level: int
        :returns: true if the toon will gain credit for using this item in this particular battle, false otherwise.

        This is based on the credit level supplied to setActivateMode(), which represents the highest-level item
        (1-based) that may be used for credit.
        """

        # If the toon has an earnedExperience indication, an entire track will become unavailable if he
        # exceeds the experience cap.
        if self.toon.earnedExperience:
            if self.toon.earnedExperience[track]:
                if self.toon.earnedExperience[track] >= ExperienceCap:
                    return 0
        if self.battleCreditLevel is None:
            # No credit restrictions.
            return 1
        else:
            return level < self.battleCreditLevel
        return

    def getMax(self, track, level):
        """
        :type track: int
        :type level: int
        """
        return GagInventoryBase.GagInventoryBase.getMax(self, track, level)

    def getCurAndNextExpValues(self, track):
        """
        :return: the number of total experience to get to the next track.
         If the current experience equals or exceeds the highest next value, the highest next value is returned.
        """
        curSkill = self.getToonExperience(track)
        # MaxSkill is the default
        retVal = MaxSkill
        for amount in Levels[track]:
            if curSkill < amount:
                retVal = amount
                return (curSkill, retVal)

        return (curSkill, retVal)

    def makePressable(self, button, track, level):
        """
        special text color

        :type button: DirectButton
        :type track: int
        :type level: int
        """
        organicBonus = self.toon.checkGagBonus(track, level)
        propBonus = self.checkPropBonus(track)
        bonus = organicBonus or propBonus
        if hasattr(button, 'invState') and button.invState == (0, organicBonus, propBonus):
            return
        setattr(button, 'invState', (0, organicBonus, propBonus))
        if bonus:
            shadowColor = self.ShadowBuffedColor
        else:
            shadowColor = self.ShadowColor
        button.configure(
            image0_image=self.upButton,
            image2_image=self.rolloverButton,
            text_shadow=shadowColor,
            geom_color=self.PressableGeomColor,
            commandButtons=(DGG.LMB,)
        )
        button.bind(DGG.B1PRESS, self.__handleSelection, extraArgs=[track, level, False])
        button.bind(DGG.B3PRESS, self.__handleSelection, extraArgs=[track, level, True])

        # This must come after the first configure because we need to set the color after setting the actual image.
        # There are no ordering guarantees in the configure paramaters
        if self.interactivePropTrackBonus == track:
            button.configure(image_color=self.PropBonusPressableImageColor)
            self.addToPropBonusIval(button)
        elif bonus:
            button.configure(image_color=self.PressableImageColorBonus)
        else:
            button.configure(image_color=self.PressableImageColor)

    def makeNoncreditPressable(self, button, track, level):
        """
        special text color

        :type button: DirectButton
        :type track: int
        :type level: int
        """
        organicBonus = self.toon.checkGagBonus(track, level)
        propBonus = self.checkPropBonus(track)
        bonus = organicBonus or propBonus
        if hasattr(button, 'invState') and button.invState == (1, organicBonus, propBonus):
            return
        setattr(button, 'invState', (1, organicBonus, propBonus))
        if bonus:
            shadowColor = self.ShadowBuffedColor
        else:
            shadowColor = self.ShadowColor
        button.configure(
            image0_image=self.upButton,
            image2_image=self.rolloverButton,
            text_shadow=shadowColor,
            geom_color=self.PressableGeomColor,
            commandButtons=(DGG.LMB,)
        )
        button.bind(DGG.B1PRESS, self.__handleSelection, extraArgs=[track, level, False])
        button.bind(DGG.B3PRESS, self.__handleSelection, extraArgs=[track, level, True])
        # This must come after the first configure because we need to set the color after setting the actual image.
        # There are no ordering guarantees in the configure paramaters
        if self.interactivePropTrackBonus == track:
            button.configure(image_color=self.PropBonusNoncreditPressableImageColor)
            self.addToPropBonusIval(button)
        elif bonus:
            button.configure(image_color=self.NoncreditPressableImageColorBonus)
        else:
            button.configure(image_color=self.NoncreditPressableImageColor)

    def makeDeletePressable(self, button: DirectButton, track: int, level: int):
        self.makeColoredPressable(button, track, level, self.DeletePressableImageColor)

    def makePropBonusPressable(self, button: DirectButton, track: int, level: int):
        self.makeColoredPressable(button, track, level, self.PropBonusPressableImageColor)

    def makeColoredPressable(self, button: DirectButton, track: int, level: int, color: Vec4):
        """
        Sets a button to a special text color. Used for delete and prop bonus!!
        """
        organicBonus = self.toon.checkGagBonus(track, level)
        propBonus = self.checkPropBonus(track)
        bonus = organicBonus or propBonus
        if hasattr(button, 'invState') and button.invState == (2, organicBonus, propBonus):
            return
        setattr(button, 'invState', (2, organicBonus, propBonus))
        if bonus:
            shadowColor = self.ShadowBuffedColor
        else:
            shadowColor = self.ShadowColor
        button.configure(
            image0_image=self.upButton,
            image2_image=self.rolloverButton,
            text_shadow=shadowColor,
            geom_color=self.PressableGeomColor,
            commandButtons=(DGG.LMB,)
        )
        button.bind(DGG.B1PRESS, self.__handleSelection, extraArgs=[track, level, False])
        button.bind(DGG.B3PRESS, self.__handleSelection, extraArgs=[track, level, True])
        # This must come after the first configure because we need to set the color after setting the actual image.
        # There are no ordering guarantees in the configure paramaters
        button.configure(image_color=color)

    def makeUnpressable(self, button, track, level):
        """
        makes the button unpressable

        :type button: DirectButton
        :type track: int
        :type level: int
        """
        organicBonus = self.toon.checkGagBonus(track, level)
        propBonus = self.checkPropBonus(track)
        bonus = organicBonus or propBonus
        if hasattr(button, 'invState') and button.invState == (3, organicBonus, propBonus):
            return
        setattr(button, 'invState', (3, organicBonus, propBonus))
        if bonus:
            shadowColor = self.UnpressableShadowBuffedColor
        else:
            shadowColor = self.ShadowColor
        button.configure(
            text_shadow=shadowColor,
            geom_color=self.UnpressableGeomColor,
            image_image=self.flatButton,
            commandButtons=()
        )
        button.unbind(DGG.B1PRESS)
        button.unbind(DGG.B3PRESS)
        if bonus:
            imageColor = self.UnpressableImageColorBonus
        else:
            imageColor = self.UnpressableImageColor
        # This must come after the first configure because we need to set the color after setting the actual image.
        # There are no ordering guarantees in the configure paramaters
        button.configure(image_color=imageColor)

    def makeBookUnpressable(self, button, track, level):
        """
        makes the button unpressable

        :type button: DirectButton
        :type track: int
        :type level: int
        """
        organicBonus = self.toon.checkGagBonus(track, level)
        propBonus = self.checkPropBonus(track)
        bonus = organicBonus or propBonus
        if hasattr(button, 'invState') and button.invState == (4, organicBonus, propBonus):
            return
        setattr(button, 'invState', (4, organicBonus, propBonus))
        if bonus:
            shadowColor = self.ShadowBuffedColor
        else:
            shadowColor = self.ShadowColor
        button.configure(
            text_shadow=shadowColor,
            geom_color=self.BookUnpressableGeomColor,
            image_image=self.flatButton,
            commandButtons=()
        )
        button.unbind(DGG.B1PRESS)
        button.unbind(DGG.B3PRESS)
        if bonus:
            image0Color = self.BookUnpressableImage0ColorBonus
            image2Color = self.BookUnpressableImage2ColorBonus
        else:
            image0Color = self.BookUnpressableImage0Color
            image2Color = self.BookUnpressableImage2Color
        # This must come after the first configure because we need to set the color after setting the actual image.
        # There are no ordering guarantees in the configure paramaters
        button.configure(image0_color=image0Color, image2_color=image2Color)

    def hideTrack(self, track):
        self.trackNameLabels[track].show()
        self.trackBars[track].hide()
        self.prestigeStars[track].hide()
        for levelIndex in range(0, len(Levels[track])):
            self.buttons[track][levelIndex].hide()
        self.trackNameLabels[track].setZ(BattleGUIGlobals.TrackTitleZOffsetNoBar)
        self.trackNameLabels[track].setScale(BattleGUIGlobals.getTrackTitleScale(track, False))

    def showTrack(self, track):
        self.trackNameLabels[track].show()
        self.trackBars[track].show()
        if self.toon.checkGagBonus(track, 0):
            self.prestigeStars[track].show()
        else:
            self.prestigeStars[track].hide()
        for levelIndex in range(0, len(Levels[track])):
            self.buttons[track][levelIndex].show()
        self.trackRows[track]['image_color'] = (1, 1, 1, 1)

        # Put the next label in the right spot
        curExp, nextExp = self.getCurAndNextExpValues(track)
        if curExp >= regMaxSkill:
            self.trackBars[track].hide()
            self.trackNameLabels[track].setZ(BattleGUIGlobals.TrackTitleZOffsetNoBar)
            self.trackNameLabels[track].setScale(BattleGUIGlobals.getTrackTitleScale(track, False))
        else:
            self.trackBars[track]['range'] = nextExp
            self.trackBars[track]['text'] = TTLocalizer.InventoryTrackExp % {
                'curExp': curExp,
                'nextExp': nextExp
            }
            self.trackNameLabels[track].setZ(BattleGUIGlobals.TrackTitleZOffset)
            self.trackNameLabels[track].setScale(BattleGUIGlobals.getTrackTitleScale(track, True))

    def updateInvString(self, invString):
        GagInventoryBase.GagInventoryBase.updateInvString(self, invString)
        self.needUpdateInventory = False
        self.updateGUI()
        return

    def updateButton(self, track, level, counterfeitEffect=None):
        if self.handleButtonUpdateOverride(track, level):
            return

        button = self.buttons[track][level]
        numItem = str(self.numItem(track, level))
        if counterfeitEffect and counterfeitEffect.getGagTrackLevel(track, level):
            numItem = f'{numItem}+1'

        button['text'] = numItem
        organicBonus = self.toon.checkGagBonus(track, level)
        propBonus = self.checkPropBonus(track)
        bonus = organicBonus or propBonus
        if bonus:
            textScale = 0.075
        else:
            textScale = 0.07
        button.configure(text_scale=textScale)

    def handleButtonUpdateOverride(self, track, level) -> bool:
        """
        Attempt to override the configuration for each gag button.
        """
        # Be careful out there. Monsters are lurking.
        if not self.toon:
            return False

        # Check for Pips
        pipsqueak = self.toon.getStatusEffectOfId(SEE.EFFECT_PIP_COUNTER)
        if pipsqueak:
            # Good boy
            itemCost = HighRollerGlobals.getPipCost(base.localAvatar, track, level)
            button = self.buttons[track][level]
            button['text'] = str(itemCost)
            button.configure(text_scale=0.07)
            return True

        # No override exists.
        return False

    def buttonBoing(self, track, level):
        button = self.buttons[track][level]
        oldScale = button.getScale()
        s = Sequence(
            button.scaleInterval(0.1, oldScale * 1.333, blendType='easeOut'),
            button.scaleInterval(0.1, oldScale, blendType='easeIn'),
            name='inventoryButtonBoing-' + str(self.this)
        )
        s.start()

    def updateGUI(self, track=None, level=None):
        """
        Update the gui display and assumes the inventory item at [track][level] has changed.

        :type track: int
        :type level: int
        """
        # Update the text telling the total number of props
        self.updateTotalPropsText()
        counterfeitEffect = self.toon.getStatusEffectOfId(SEE.EFFECT_COUNTERFEIT_CONTAINER)
        if track is None and level is None:
            for track in self.getGagOrder():
                # Update the number of experience points per track
                curExp, nextExp = self.getCurAndNextExpValues(track)
                if curExp >= regMaxSkill:
                    self.trackBars[track].hide()
                    self.trackNameLabels[track].setZ(BattleGUIGlobals.TrackTitleZOffsetNoBar)
                    self.trackNameLabels[track].setScale(BattleGUIGlobals.getTrackTitleScale(track, False))
                else:
                    self.trackBars[track]['text'] = TTLocalizer.InventoryTrackExp % {
                        'curExp': curExp,
                        'nextExp': nextExp
                    }
                    self.trackBars[track]['value'] = curExp
                    self.trackNameLabels[track].setZ(BattleGUIGlobals.TrackTitleZOffset)
                    self.trackNameLabels[track].setScale(BattleGUIGlobals.getTrackTitleScale(track, True))

                # Update the text for each button
                for level in range(0, len(Levels[track])):
                    self.updateButton(track, level, counterfeitEffect=counterfeitEffect)

        elif track is not None and level is not None:
            self.updateButton(track, level, counterfeitEffect=counterfeitEffect)
        else:
            self.notify.error('Invalid use of updateGUI')
        # Since max props can affect what buttons are active
        self.__activateButtons()
        return

    def getSingleGroupStr(self, track, level):
        if track == AttackEnum.TOON_HEAL:
            if isGroup(track, level):
                return TTLocalizer.InventoryTargets % TTLocalizer.InventoryAffectsAll % TTLocalizer.Toons
            else:
                return TTLocalizer.InventoryTargets % TTLocalizer.InventoryAffectsOne % TTLocalizer.Toon
        elif isGroup(track, level):
            return TTLocalizer.InventoryTargets % TTLocalizer.InventoryAffectsAll % TTLocalizer.Cogs
        elif track in (AttackEnum.TOON_ZAP, AttackEnum.TOON_SQUIRT):
            return TTLocalizer.InventoryTargets % TTLocalizer.InventoryAffectsThree % TTLocalizer.Cogs
        else:
            return TTLocalizer.InventoryTargets % TTLocalizer.InventoryAffectsOne % TTLocalizer.Cog

    def getExtraText(self, track, level, organicBonus, damage=0):
        if track == AttackEnum.TOON_TRAP:
            return TTLocalizer.TrapExtraText % damage
        elif track == AttackEnum.TOON_SQUIRT:
            return TTLocalizer.InventorySquirtRoundsString % str(NumRoundsSoaked[level])
        elif track == AttackEnum.TOON_LURE:
            kbDamage = getAvPropDamage(track, level, self.getToonExperience(track))
            if organicBonus:
                if attackAffectsGroup(track, level):
                    kbBonus = math.ceil(kbDamage * LurePrestigeGroupBonus)
                else:
                    kbBonus = math.ceil(kbDamage * LurePrestigeSingleBonus)
            else:
                kbBonus = 0
            return TTLocalizer.LureExtraText % kbDamage + (
                TTLocalizer.InventoryDamageBonus % kbBonus if organicBonus else '')
        elif track == AttackEnum.TOON_SOUND:
            return TTLocalizer.SoundExtraText % str(round((SoundAtkBonus[organicBonus] - 1) * 100))
        elif track == AttackEnum.TOON_ZAP:
            text = TTLocalizer.ZapExtraText % getZapJumpDamage(damage, organicBonus)
            return text
        elif track == AttackEnum.TOON_THROW:
            return TTLocalizer.ThrowExtraText % math.ceil(getAvPropDamage(track, level, self.getToonExperience(track), organicBonus) * \
                ThrowPresHealPercent)

    def getToonExperience(self, track):
        if self.toon.getStatusEffectOfId(SEE.EFFECT_PIP_COUNTER):
            return MaxSkill
        return self.toon.getExperience()[track]

    def getDmgStr(self, track, level):
        if track == AttackEnum.TOON_HEAL:
            return TTLocalizer.InventoryHealString
        elif track == AttackEnum.TOON_LURE:
            return TTLocalizer.InventoryLureString
        else:
            return TTLocalizer.InventoryDamageString

    def loadBattleFrame(self):
        self.guiElements.update(BattleGUI.generateBattlePanel())

        self.battleFrame = self.guiElements[BattleGUI.BATTLE_FRAME]
        self.battleFrame.reparentTo(self)

        self.passButton = self.guiElements[BattleGUI.TABS_PASS]
        self.passButton.bind(DGG.B1PRESS, self.__handlePass, extraArgs=[False])
        self.passButton.bind(DGG.B3PRESS, self.__handlePass, extraArgs=[True])
        self.passButton.guiItem.setSound(DGG.B3PRESS + self.passButton.guiId, self.passButton['clickSound'])

        self.runButton = self.guiElements[BattleGUI.TABS_RUN]
        self.runButton.bind(DGG.B1PRESS, self.__handleRun)

        self.sosButton = self.guiElements[BattleGUI.TABS_SOS]
        self.sosButton.bind(DGG.B1PRESS, self.__handleSOS)
        self.sueButton = self.guiElements[BattleGUI.TABS_SUE]
        self.sueButton.bind(DGG.B1PRESS, self.__handleSue, extraArgs=[False])
        self.sueButton.bind(DGG.B3PRESS, self.__handleSue, extraArgs=[True])
        self.sueButton.guiItem.setSound(DGG.B3PRESS + self.sueButton.guiId, self.sueButton['clickSound'])

        self.sueButton = self.guiElements[BattleGUI.TABS_SUE]
        self.sueButton.bind(DGG.B1PRESS, self.__handleSue, extraArgs=[False])
        self.sueButton.bind(DGG.B3PRESS, self.__handleSue, extraArgs=[True])
        self.sueButton.guiItem.setSound(DGG.B3PRESS + self.sueButton.guiId, self.sueButton['clickSound'])

        self.fireButton = self.guiElements[BattleGUI.TABS_FIRE]
        self.fireButton.bind(DGG.B1PRESS, self.__handleFire, extraArgs=[False])
        self.fireButton.bind(DGG.B3PRESS, self.__handleFire, extraArgs=[True])
        self.fireButton.guiItem.setSound(DGG.B3PRESS + self.fireButton.guiId, self.fireButton['clickSound'])

        self.counterfeitButton = self.guiElements[BattleGUI.TABS_COUNTERFEIT]
        self.counterfeitButton.bind(DGG.B1PRESS, self.__handleCounterfeit, extraArgs=[False])
        self.counterfeitButton.bind(DGG.B3PRESS, self.__handleCounterfeit, extraArgs=[True])
        self.counterfeitButton.guiItem.setSound(DGG.B3PRESS + self.counterfeitButton.guiId,
                                                self.counterfeitButton['clickSound'])

        self.counterfeitBackButton = self.guiElements[BattleGUI.TABS_COUNTERFEIT_BACK]
        self.counterfeitBackButton.bind(DGG.B1PRESS, self.__handleCounterfeit, extraArgs=[False])
        self.counterfeitBackButton.bind(DGG.B3PRESS, self.__handleCounterfeit, extraArgs=[True])
        self.counterfeitBackButton.guiItem.setSound(DGG.B3PRESS + self.counterfeitBackButton.guiId,
                                                    self.counterfeitBackButton['clickSound'])
        self.counterfeitBackButton.hide()

        self.surrenderButton = self.guiElements[BattleGUI.TABS_SURRENDER]
        self.surrenderButton.bind(DGG.B1PRESS, self.__handleSurrender)

        self.surrenderButtonFlag = self.guiElements[BattleGUI.TABS_SURRENDER_FLAG]
        self.surrenderButtonFlag.hide()
        self.surrenderButtonFlag.surrenderActive = False

        self.surrenderIncSfx = loader.loadSfx('phase_3.5/audio/sfx/UI_social_group_join.ogg')
        self.surrenderDecSfx = loader.loadSfx('phase_3.5/audio/sfx/UI_social_group_leave.ogg')

    def loadPurchaseFrame(self):
        gagSelectionGui = base.loader.loadModel('phase_3.5/models/gui/battlegui/gag_selection_panels')

        self.purchaseFrame = DirectFrame(
            parent=self,
            relief=None,
            image=gagSelectionGui.find('**/purchase_main'),
            image_scale=(2.5, 1, 1.25)
        )
        # Play Again Button Background
        DirectFrame(
            parent=self.purchaseFrame,
            relief=None,
            image=gagSelectionGui.find('**/purchase_button_panel'),
            image_scale=(1, 1, 0.5),
            pos=(0.972, 0, -0.052),
            scale=0.625
        )

        gagSelectionGui.removeNode()
        self.purchaseFrame.hide()

    def loadStorePurchaseFrame(self):
        gagSelectionGui = base.loader.loadModel('phase_3.5/models/gui/battlegui/gag_selection_panels')

        self.storePurchaseFrame = DirectFrame(
            parent=self,
            relief=None,
            image=gagSelectionGui.find('**/purchase_main'),
            image_scale=(2.5, 1, 1.25)
        )

        gagSelectionGui.removeNode()

        self.storePurchaseFrame.hide()

    def buttonLookup(self, track, level):
        return self.invModels[track][level]

    def enterTrackFrame(self, track, guiItem):
        messenger.send('enterTrackFrame', [track])

    def exitTrackFrame(self, track, guiItem):
        messenger.send('exitTrackFrame', [track])

    def checkPropBonus(self, track):
        """
        :return: true if this track gag is being buffed by a prop.
        """
        if self.toon and self.toon.getStatusEffectOfId(SEE.EFFECT_PIP_COUNTER):
            return True
        return track == self.interactivePropTrackBonus

    def stopAndClearPropBonusIval(self):
        """If we have a propBonusIval, stop it and reset it to empty Parallel."""
        if self.propBonusIval and self.propBonusIval.isPlaying():
            self.propBonusIval.finish()
        self.propBonusIval = Parallel(name='dummyPropBonusIval')

    def addToPropBonusIval(self, button):
        """We have a button, make it flash and add it to propBonusIval."""
        flashObject = button
        try:
            flashObject = button.component('image0')
        except Exception:
            pass

        goDark = LerpColorScaleInterval(
            flashObject, 0.5, Point4(0.1, 0.1, 0.1, 1.0), Point4(1, 1, 1, 1), blendType='easeIn'
        )
        goBright = LerpColorScaleInterval(
            flashObject, 0.5, Point4(1, 1, 1, 1), Point4(0.1, 0.1, 0.1, 1.0), blendType='easeOut'
        )
        newSeq = Sequence(goDark, goBright, Wait(0.2))
        self.propBonusIval.append(newSeq)

    def checkUpdateInventory(self):
        if self.needUpdateInventory:
            messenger.send("deleteItems", [self.makeNetString()])
            self.needUpdateInventory = False

    def isGagDisabled(self, track, level):
        if INV_MOD_DISABLED in self.activeButtonModifiers:
            if track in self.activeButtonModifiers[INV_MOD_DISABLED]:
                if level in self.activeButtonModifiers[INV_MOD_DISABLED][track]:
                    return True

        return False

    def applyInventoryButtonModifier(self, modType=INV_MOD_NONE, levels=None, tracks=None):
        levels = levels or []
        tracks = tracks or []
        self.activeButtonModifiers.setdefault(modType, {})
        tracksToAdd = tracks or list(range(len(BattleGlobals.Tracks)))
        levelsToApply = levels or list(range(8))

        for track in tracksToAdd:
            self.activeButtonModifiers[modType].setdefault(track, [])
            for lvl in levelsToApply:
                self.activeButtonModifiers[modType][track].append(lvl)

    def setButtonCounterfeitState(self, button, counterfeitEffect, track, level, usable):
        organicBonus = self.toon.checkGagBonus(track, level)
        propBonus = self.checkPropBonus(track)
        bonus = organicBonus or propBonus
        wantState = counterfeitEffect.getGagTrackLevel(track, level)

        textFg = self.CounterfeitTextColor if wantState else (1.0, 1.0, 1.0, 1.0)
        textScale = 0.06 if wantState else (0.075 if bonus else 0.07)
        if not usable:
            imageColor = self.UnpressableImageColorBonus if bonus else self.UnpressableImageColor
        elif wantState:
            imageColor = self.CounterfeitPressableImageColorBonus if bonus else self.CounterfeitPressableImageColor
        elif self.itemIsCredit(track, level):
            imageColor = self.PressableImageColorBonus if bonus else self.PressableImageColor
        else:
            imageColor = self.NoncreditPressableImageColorBonus if bonus else self.NoncreditPressableImageColor

        self.updateButton(track, level, counterfeitEffect=counterfeitEffect)

        button.configure(image_color=imageColor, text_fg=textFg, text_scale=textScale)

    def updateButtonsForBattle(self):
        if self.activateMode == 'counterfeit':
            # We don't need to do all this other modifier stuff if we're in the counterfeit state
            self.__counterfeitColorButtons()
            return

        counterfeitEffect = self.toon.getStatusEffectOfId(SEE.EFFECT_COUNTERFEIT_CONTAINER)

        for track in self.getGagOrder():
            if self.toon.hasTrackAccess(track):
                self.showTrack(track)
                for level in range(len(Levels[track])):
                    button = self.buttons[track][level]
                    if self.itemIsUsable(track, level):
                        if button.isHidden():
                            button.show()
                        usable = True
                        itemNum = self.numItem(track, level)
                        if counterfeitEffect and counterfeitEffect.getGagTrackLevel(track, level):
                            itemNum += 1
                        if (
                            itemNum <= 0
                            or (track == AttackEnum.TOON_HEAL and not self.canHeal)
                            or (track == AttackEnum.TOON_TRAP and not self.canTrap)
                            or (track == AttackEnum.TOON_LURE and not self.canLure)
                            or (track not in (AttackEnum.TOON_HEAL,) and self.allSuitsUntouchable)
                            or (track != AttackEnum.TOON_TRAP and self.allSuitsUntouchableNoTrap)
                        ):
                            self.makeUnpressable(button, track, level)
                            usable = False
                        elif self.itemIsCredit(track, level):
                            self.makePressable(button, track, level)
                        else:
                            self.makeNoncreditPressable(button, track, level)
                        if counterfeitEffect:
                            self.setButtonCounterfeitState(button, counterfeitEffect, track, level, usable)
                    else:
                        button.hide()
            else:
                self.hideTrack(track)

        self.propBonusIval.loop()

    def updateInventoryButtonsForModifiers(self, updateBattleButtons=True):
        if updateBattleButtons:
            self.updateButtonsForBattle()
        for track in self.getGagOrder():
            # Apply restrictions to each track.
            if not self.toon.hasTrackAccess(track):
                continue
            if track == AttackEnum.TOON_HEAL and not self.canHeal:
                continue
            if track == AttackEnum.TOON_TRAP and not self.canTrap:
                continue
            if track == AttackEnum.TOON_LURE and not self.canLure:
                continue
            if track not in (AttackEnum.TOON_HEAL,) and self.allSuitsUntouchable:
                continue
            if track != AttackEnum.TOON_TRAP and self.allSuitsUntouchableNoTrap:
                continue

            # OK, apply restrictions to each level.
            for level in range(NUM_GAG_TRACKS):
                # Can this item be used?
                if not self.itemIsUsable(track, level):
                    continue
                if not self.numItem(track, level):
                    continue

                # Apply all active button modifiers we have.
                for modType, currModData in self.activeButtonModifiers.items():
                    if level in self.activeButtonModifiers[modType].get(track, []):
                        button = self.buttons[track][level]
                        self.buttonModifierFuncs[modType](button, track, level)

    def clearButtonModifier(self, modType):
        if modType in self.activeButtonModifiers:
            del self.activeButtonModifiers[modType]

    def clearAllButtonModifiers(self):
        self.activeButtonModifiers = {}

    def getGagOrder(self, includeBattle: bool = False):
        if self.battle is not None and includeBattle:
            return self.battle.getGagOrder()
        return GAG_TRACK_ORDER

    def updateBattle(self, battle=None):
        self.battle = battle
        self.refreshGagOrder()
        self.updateGUI()

    def refreshGagOrder(self):
        battleGagOrder = self.getGagOrder(True)
        for index, trackIndex in enumerate(battleGagOrder):
            subframe = self.trackSubframes[trackIndex]
            x, y, z = subframe.getPos()
            subframe.setPos(x, y, BattleGUI.calculateTrackZPos(index))

    def adjustSurrenderedToons(self, numSur=0, maxSur=0):
        self.surrenderButtonFlag.hide()

        if numSur == 0:
            self.surrenderButton.setText(('', TTLocalizer.InventorySurrender, TTLocalizer.InventorySurrender)),
        else:
            self.surrenderButtonFlag['text'] = f'{numSur}/{maxSur}'
            self.surrenderButton.setText(('', '', ''))

        surIncreased = numSur > self.lastSurrenderNum

        if numSur != self.lastSurrenderNum and maxSur > 0:
            base.playSfx(self.surrenderIncSfx if surIncreased else self.surrenderDecSfx)
        self.lastSurrenderNum = numSur

        self.finishSurrenderSeq()

        if numSur > 0:
            if self.surrenderButtonFlag.surrenderActive:
                self.surrenderButtonFlag.show()
                self.surrenderSeq = Sequence(
                    Func(self.surrenderButtonFlag.setPos, (-0.7, 0, 0.6)),
                    Func(self.surrenderButtonFlag.setScale, 1.0),
                    LerpScaleInterval(self.surrenderButtonFlag, 0.12, 1.25 if surIncreased else 0.75, blendType='easeOut'),
                    LerpScaleInterval(self.surrenderButtonFlag, 0.12, 1.0, blendType='easeIn'),
                )
            else:
                self.surrenderButtonFlag.setScale(0.1)
                self.surrenderButtonFlag.setPos(0.0, 0, 0.6)
                self.surrenderSeq = Parallel(
                    Func(self.surrenderButtonFlag.show),
                    LerpScaleInterval(self.surrenderButtonFlag, 0.2, 1.0, blendType='easeOut'),
                    LerpPosInterval(self.surrenderButtonFlag, 0.2, (-0.7, 0, 0.6), blendType='easeOut'),
                )

            self.surrenderButtonFlag.surrenderActive = True
        else:
            if self.surrenderButtonFlag.surrenderActive:
                self.surrenderButtonFlag.show()
                self.surrenderSeq = Sequence(
                    Func(self.surrenderButtonFlag.setPos, (-0.7, 0, 0.6)),
                    Func(self.surrenderButtonFlag.setScale, 1.0),
                    Parallel(
                        LerpScaleInterval(self.surrenderButtonFlag, 0.2, 0.1, blendType='easeIn'),
                        LerpPosInterval(self.surrenderButtonFlag, 0.2, (0.0, 0, 0.6), blendType='easeIn'),
                    ),
                    Func(self.surrenderButtonFlag.hide),
                )
            else:
                self.surrenderSeq = Sequence()

            self.surrenderButtonFlag.surrenderActive = False

        self.surrenderSeq.start()
