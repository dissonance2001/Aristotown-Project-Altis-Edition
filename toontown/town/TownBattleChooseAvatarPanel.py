from direct.fsm import StateData
from toontown.clashbattle.battle import BattleGlobals
from direct.gui.DirectGui import *
from toontown.clashbattle.battle.attacks.base.AttackEnum import AttackEnum
from toontown.clashbattle.battle.statuses import StatusEffects
from toontown.chat.ui.speedchat.TTSCUniteTerminal import TTSCUniteMsgEvent
from toontown.inventory.registry.IOURegistry import IOURegistry
from toontown.clashbattle.battle import BattleGUIGlobals, BattleGUI
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class TownBattleChooseAvatarPanel(StateData.StateData):
    def __init__(self, doneEvent, toon, gagChangeEvent, townBattle):
        self.notify.debug('Init choose panel...')
        StateData.StateData.__init__(self, doneEvent)
        self.gagChangeEvent = gagChangeEvent
        self.numAvatars = 0
        self.chosenAvatar = 0
        self.toon = toon
        self.townBattle = townBattle
        self.spacingModifier = 1.0
        self.npcId = 0
        self.allowPickLocal = False
        self.loaded = 0

    def load(self):
        self.frame = DirectFrame(relief=None)
        self.frame.hide()

        self.gui = BattleGUI.TargetingGUI(parent=self.frame, townBattle=self.townBattle)
        self.gui.setScale(BattleGUIGlobals.TargetingGuiScale)
        self.gui.activateTargetingMode()

        self.gui.backButton.configure(command=self.__handleBack)
        self.gui.setGagChangeCallback(self.__handleGagChange)

        if self.toon:
            self.gui.applyToonText()
        else:
            self.gui.applySuitText()

        self.avatarButtons = []
        for i in range(BattleGlobals.MaxBattleAvatars):
            button = BattleGUI.generateTargetingArrow()
            button.reparentTo(self.frame)
            button.configure(command=self.__handleAvatar, extraArgs=[i])
            if self.toon:
                button.setScale(BattleGUIGlobals.TargetingArrowScale, BattleGUIGlobals.TargetingArrowScale, -BattleGUIGlobals.TargetingArrowScale)
                button.setPos(0, 0, -BattleGUIGlobals.TargetingArrowHeight)
            else:
                button.setScale(BattleGUIGlobals.TargetingArrowScale)
                button.setPos(0, 0, BattleGUIGlobals.TargetingArrowHeight)
            self.avatarButtons.append(button)

    def unload(self):
        del self.townBattle
        self.frame.destroy()
        del self.frame
        del self.gui
        del self.avatarButtons
        self.ignoreAll()

    def onUniteUsed(self):
        rewardsDisabled = bool(base.localAvatar.getStatusEffectsOfType(StatusEffects.RewardCooldownStatusEffect))
        if self.loaded and rewardsDisabled:
            self.__handleBack()

    def enter(self, numAvatars, toons: list, localNum=None, luredIndices=None, trappedIndices=None,
              track=None, untouchableIndices=None, untouchableByTrapIndices=None, npcId=0, allowPickLocal=False):
        self.frame.show()
        self.npcId = npcId
        self.allowPickLocal = allowPickLocal
        invalidTargets = []
        if not self.toon:
            if len(luredIndices) > 0:
                if track in (AttackEnum.TOON_TRAP, AttackEnum.TOON_LURE):
                    invalidTargets += luredIndices
            if len(trappedIndices) > 0:
                if track == AttackEnum.TOON_TRAP:
                    invalidTargets += trappedIndices
        if untouchableIndices is not None and track != AttackEnum.TOON_TRAP:
            invalidTargets += untouchableIndices
        if untouchableByTrapIndices is not None and track == AttackEnum.TOON_TRAP:
            invalidTargets += untouchableByTrapIndices
        if self.npcId:
            iou = IOURegistry[self.npcId]
            npcTrack = iou.getGagTrack()
            for i, toon in enumerate(toons):
                if npcTrack != -1 and not toon.hasTrackAccess(npcTrack):
                    invalidTargets.append(i)
        self.__placeButtons(numAvatars, invalidTargets, localNum)
        self.accept(TTSCUniteMsgEvent, self.onUniteUsed)
        self.loaded = 1

    def exit(self):
        self.loaded = 0
        self.frame.hide()

    def setValues(self, track, level):
        self.gui.emblem.setValues(track, level, base.localAvatar, townBattle=self.townBattle)
        self.gui.update()

    def __handleBack(self):
        doneStatus = {'mode': 'Back'}
        messenger.send(self.doneEvent, [doneStatus])

    def __handleAvatar(self, avatar):
        doneStatus = {'mode': 'Avatar',
                      'avatar': avatar,
                      'attackType': 'NPCSOS' if self.npcId else 'Attack',
                      'level': self.npcId}
        messenger.send(self.doneEvent, [doneStatus])

    def __handleGagChange(self, track: int, level: int):
        # If we're choosing a target, and this is a heal, we don't want a battle event, just a GUI update.
        softChange = track == AttackEnum.TOON_HEAL
        lockInInfo = {
            'mode': 'GagChange',
            'track': track,
            'level': level,
            'target': -1,
            'softChange': softChange
        }
        self.townBattle.level = level
        messenger.send(self.gagChangeEvent, [lockInInfo])

    def adjustCogs(self, numAvatars, luredIndices, trappedIndices, track, untouchableIndices=None):
        invalidTargets = []
        if len(luredIndices) > 0:
            if track in (AttackEnum.TOON_TRAP, AttackEnum.TOON_LURE):
                invalidTargets += luredIndices
        if len(trappedIndices) > 0:
            if track == AttackEnum.TOON_TRAP:
                invalidTargets += trappedIndices
        if untouchableIndices is not None and track != AttackEnum.TOON_LURE:
            invalidTargets += untouchableIndices
        self.__placeButtons(numAvatars, invalidTargets, None)

    def adjustToons(self, numToons, toons, localNum, untouchableIndices=None):
        invalidTargets = []
        if untouchableIndices is not None:
            invalidTargets += untouchableIndices
        if self.npcId:
            iou = IOURegistry[self.npcId]
            npcTrack = iou.getGagTrack()
            for i, toon in enumerate(toons):
                if npcTrack != -1 and not toon.hasTrackAccess(npcTrack):
                    invalidTargets.append(i)
        self.__placeButtons(numToons, invalidTargets, localNum)

    def __placeButtons(self, numAvatars, invalidTargets, localNum):
        for i in range(BattleGlobals.MaxBattleAvatars):
            if numAvatars > i and i not in invalidTargets and (self.allowPickLocal or i != localNum):
                self.avatarButtons[i].show()
            else:
                self.avatarButtons[i].hide()

        if self.toon:
            xSeparation = BattleGUIGlobals.ToonPanelXSpacing * self.spacingModifier
        else:
            xSeparation = BattleGUIGlobals.SuitPanelXSpacing * self.spacingModifier
        startingX = (0.5 * (numAvatars - 1)) * xSeparation

        for i in range(numAvatars):
            self.avatarButtons[i].setX(startingX - (i * xSeparation))
