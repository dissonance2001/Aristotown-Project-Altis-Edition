from direct.fsm import StateData
from direct.gui.DirectGui import *

from toontown.clashbattle.battle import BattleGUIGlobals, BattleGUI
from toontown.clashbattle.battle.attacks.base.AttackEnum import AttackEnum
from toontown.clashbattle.battle.statuses import StatusEffects
from toontown.chat.ui.speedchat.TTSCUniteTerminal import TTSCUniteStateChangedEvent
from toontown.clashbattle.battle import BattleGlobals
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class SueCogPanel(StateData.StateData):
    def __init__(self, doneEvent, townBattle):
        self.notify.debug('Init choose panel...')
        StateData.StateData.__init__(self, doneEvent)
        self.numAvatars = 0
        self.chosenAvatar = 0
        self.toon = 0
        self.loaded = 0
        self.townBattle = townBattle

    def load(self):
        self.frame = DirectFrame(relief=None)
        self.frame.hide()

        self.gui = BattleGUI.TargetingGUI(parent=self.frame, townBattle=self.townBattle)
        self.gui.setScale(BattleGUIGlobals.TargetingGuiScale)
        self.gui.activateTargetingMode()

        self.gui.backButton.configure(command=self.__handleBack)

        self.gui.applySueText(base.localAvatar.getCeaseDesists(), True)
        self.gui.emblem.setValues(AttackEnum.TOON_SUE)
        self.gui.update()

        self.avatarButtons = []
        for i in range(BattleGlobals.MaxBattleAvatars):
            button = BattleGUI.generateTargetingArrow()
            button.reparentTo(self.frame)
            button.configure(command=self.__handleAvatar, extraArgs=[i])
            button.setScale(BattleGUIGlobals.TargetingArrowScale)
            button.setPos(0, 0, BattleGUIGlobals.TargetingArrowHeight)
            self.avatarButtons.append(button)

        self.loaded = 1

    def unload(self):
        del self.townBattle
        if self.loaded:
            self.frame.destroy()
            del self.frame
            del self.gui
            del self.avatarButtons
        self.loaded = 0
        self.ignoreAll()

    def onUniteUsed(self):
        rewardsDisabled = bool(base.localAvatar.getStatusEffectsOfType(StatusEffects.RewardCooldownStatusEffect))
        if self.loaded and rewardsDisabled:
            self.__handleBack()

    def enter(self, numAvatars, localNum = None, suedIndices = None, sueCosts = None):
        if not self.loaded:
            self.load()
        self.frame.show()
        invalidTargets = []
        if not self.toon:
            if len(suedIndices) > 0:
                invalidTargets += suedIndices

        self.__placeButtons(numAvatars, invalidTargets, localNum, sueCosts)
        self.accept(TTSCUniteStateChangedEvent, self.onUniteUsed)

    def exit(self):
        self.frame.hide()

    def __handleBack(self):
        doneStatus = {'mode': 'Back'}
        messenger.send(self.doneEvent, [doneStatus])

    def __handleAvatar(self, avatar):
        doneStatus = {'mode': 'Avatar',
         'avatar': avatar}
        messenger.send(self.doneEvent, [doneStatus])

    def adjustToons(self, numToons, localNum):
        self.__placeButtons(numToons, [], localNum)

    def __placeButtons(self, numAvatars, invalidTargets, localNum, sueCosts):
        cansue = 0
        for i in range(BattleGlobals.MaxBattleAvatars):
            if numAvatars > i and i not in invalidTargets and i != localNum:
                self.avatarButtons[i].show()
                self.avatarButtons[i]['text'] = str(sueCosts[i])
                if sueCosts[i] <= localAvatar.getCeaseDesists():
                    self.avatarButtons[i]['state'] = DGG.NORMAL
                    self.avatarButtons[i]['text_fg'] = (0, 0, 0, 1)
                    cansue = 1
                else:
                    self.avatarButtons[i]['state'] = DGG.DISABLED
                    self.avatarButtons[i]['text_fg'] = (1.0, 0, 0, 1)
            else:
                self.avatarButtons[i].hide()

        self.gui.applySueText(base.localAvatar.getCeaseDesists(), cansue)

        xSeparation = BattleGUIGlobals.SuitPanelXSpacing
        startingX = (0.5 * (numAvatars - 1)) * xSeparation

        for i in range(numAvatars):
            self.avatarButtons[i].setX(startingX - (i * xSeparation))
