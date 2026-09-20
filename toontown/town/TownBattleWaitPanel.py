from direct.fsm import StateData
from toontown.clashbattle.battle.BattleGUI import TargetingGUI
from toontown.clashbattle.battle import BattleGUIGlobals
import time

from toontown.clashbattle.battle.attacks.base.AttackEnum import AttackEnum
from toontown.clashbattle.battle.statuses import StatusEffects
from toontown.chat.ui.speedchat.TTSCUniteTerminal import TTSCUniteStateChangedEvent


class TownBattleWaitPanel(StateData.StateData):

    def __init__(self, doneEvent, lockInEvent, gagChangeEvent, townBattle):
        StateData.StateData.__init__(self, doneEvent)
        self.lockInEvent = lockInEvent
        self.gagChangeEvent = gagChangeEvent
        self.lockedInTimestamp = 0
        self.townBattle = townBattle
        self.track = None

    def load(self):
        self.gui = TargetingGUI(townBattle=self.townBattle)
        self.gui.setScale(BattleGUIGlobals.TargetingGuiScale)
        self.gui.hide()

        # Configure buttons
        self.gui.backButton.configure(command=self.__handleBack)
        self.gui.lockInButton.configure(command=self.__handleLockIn)
        self.gui.setGagChangeCallback(self.__handleGagChange)

    def unload(self):
        del self.townBattle
        self.gui.destroy()
        del self.gui
        self.ignoreAll()

    def enter(self):
        self.gui.activateLockInMode()
        self.gui.show()
        self.accept(TTSCUniteStateChangedEvent, self.onUniteUsed)

    def exit(self):
        self.gui.hide()
        self.track = None
        self.ignoreAll()

    def setLockIn(self, lockIn):
        self.gui.setLockIn(lockIn)

    def onUniteUsed(self):
        rewardsDisabled = bool(base.localAvatar.getStatusEffectsOfType(StatusEffects.RewardCooldownStatusEffect))
        if rewardsDisabled and self.track in [AttackEnum.TOON_FIRE, AttackEnum.TOON_SUE, AttackEnum.TOON_NPC]:
            self.__handleBack()

    def setValues(self, track, level):
        self.track = track
        self.gui.emblem.setValues(track, level, base.localAvatar, townBattle=self.townBattle)
        self.gui.update()

    def requestBack(self):
        self.__handleBack()

    def __handleBack(self):
        doneStatus = {'mode': 'Back'}
        messenger.send(self.doneEvent, [doneStatus])

    def __handleLockIn(self):
        # No spamming the lock in!
        currTime = time.time()
        if currTime - self.lockedInTimestamp < 0.5:
            return

        self.lockedInTimestamp = currTime

        # This is a toggle button, so request the opposite of the current state.
        lockIn = not self.gui.lockedIn
        lockInInfo = {
            'mode': 'LockIn',
            'lockIn': lockIn
        }
        messenger.send(self.lockInEvent, [lockInInfo])

    def __handleGagChange(self, track: int, level: int):
        lockInInfo = {
            'mode': 'GagChange',
            'track': track,
            'level': level,
        }
        messenger.send(self.gagChangeEvent, [lockInInfo])
