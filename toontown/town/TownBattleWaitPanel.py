import time

from direct.fsm import StateData
from direct.gui import DirectGuiGlobals as DGG
from toontown.clashbattle.battle import BattleGUIGlobals
from toontown.clashbattle.battle.BattleGUI import TargetingGUI
from toontown.battle.attacks.base.AttackEnum import AttackEnum
from toontown.toonbase.ToontownBattleGlobals import AvPropsNew, TrackColors


class TownBattleWaitPanel(StateData.StateData):
    def __init__(self, doneEvent, lockInEvent=None, gagChangeEvent=None, townBattle=None):
        StateData.StateData.__init__(self, doneEvent)
        self.lockInEvent = lockInEvent
        self.gagChangeEvent = gagChangeEvent
        self.townBattle = townBattle
        self.track = None
        self.level = None
        self.mode = 'Inventory'
        self.lockedInTimestamp = 0
        self.gui = None
        self.status = None
        self.sosIcon = None

    def load(self):
        self.gui = TargetingGUI(townBattle=self.townBattle)
        self.gui.setScale(BattleGUIGlobals.TargetingGuiScale)
        self.gui.hide()
        self.gui.backButton.configure(command=self.__handleBack)
        self.gui.lockInButton.configure(command=self.__handleLockIn)
        self.gui.setGagChangeCallback(self.__handleGagChange)
        self.gui.emblem.legacyIOURegistry = True
        self.gui.emblem.bind(DGG.B3PRESS, self.__handleGagRightClick)
        self.status = loader.loadModel('phase_3.5/models/gui/status_effects')
        self.sosIcon = self.status.find('**/energized_icon')

    def unload(self):
        self.ignoreAll()
        if self.gui is not None:
            self.gui.destroy()
            self.gui = None
        if self.status is not None and not self.status.isEmpty():
            self.status.removeNode()
        self.status = None
        self.sosIcon = None
        self.townBattle = None

    def enter(self, numParticipants, track=None, level=None, mode='Inventory'):
        self.setValues(track, level, mode)
        self.gui.lock.show()
        self.gui.lockInButton.show()
        self.gui.setLockIn(bool(getattr(self.townBattle, 'lockIn', False)))
        self.gui.show()

    def exit(self):
        self.gui.hide()
        self.track = None
        self.level = None
        self.ignoreAll()

    def setLockIn(self, lockedIn):
        if self.gui is not None:
            self.gui.setLockIn(bool(lockedIn))

    def setValues(self, track, level, mode='Inventory'):
        self.track = track
        self.level = level
        self.mode = mode
        avatar = base.localAvatar

        if mode == 'Inventory' and isinstance(track, int) and 0 <= track < len(TrackColors) and isinstance(level, int) and 0 <= level < len(AvPropsNew[track]):
            self.gui.emblem.setValues(track, level, avatar=avatar, townBattle=self.townBattle)
            color = TrackColors[track]
            self.gui.emblem['image_color'] = (color[0], color[1], color[2], 1)
        elif mode == 'IOU':
            self.gui.emblem.setValues(AttackEnum.TOON_NPC, level, avatar=avatar, townBattle=self.townBattle)
            from toontown.toon import IOURegistry as LegacyIOURegistry
            definition = LegacyIOURegistry.IOURegistry.get(level)
            gagTrack = definition.getGagTrack() if definition is not None else -1
            color = TrackColors[gagTrack] if isinstance(gagTrack, int) and 0 <= gagTrack < len(TrackColors) else (1, 1, 1)
            self.gui.emblem['image_color'] = (color[0], color[1], color[2], 1)
        elif mode == 'Pass':
            self.gui.emblem.setValues(AttackEnum.TOON_PASS, None, avatar=avatar, townBattle=self.townBattle)
        elif mode == 'Fire':
            self.gui.emblem.setValues(AttackEnum.TOON_FIRE, None, avatar=avatar, townBattle=self.townBattle)
        elif mode == 'Sue':
            self.gui.emblem.setValues(AttackEnum.TOON_SUE, None, avatar=avatar, townBattle=self.townBattle)
        elif mode == 'SOS':
            self.gui.emblem.setValues(AttackEnum.TOON_NO_ATTACK, None, avatar=avatar, townBattle=self.townBattle)
            if self.sosIcon is not None and not self.sosIcon.isEmpty():
                self.gui.emblem.emblem['geom'] = self.sosIcon
                self.gui.emblem.emblem['geom_scale'] = 0.5
                self.gui.emblem['image_color'] = (0, 1, 0.031, 1)
        else:
            self.gui.emblem.setValues(AttackEnum.TOON_NO_ATTACK, None, avatar=avatar, townBattle=self.townBattle)

        self.gui.update()

    def __handleBack(self):
        messenger.send(self.doneEvent, [{'mode': 'Back'}])

    def __sendLockIn(self, lockedIn):
        if self.lockInEvent is not None:
            messenger.send(self.lockInEvent, [{'mode': 'LockIn', 'lockIn': bool(lockedIn)}])

    def __handleLockIn(self):
        currTime = time.time()
        if currTime - self.lockedInTimestamp < 0.5:
            return
        self.lockedInTimestamp = currTime
        lockedIn = not self.gui.lockedIn
        self.gui.setLockIn(lockedIn)
        self.__sendLockIn(lockedIn)

    def __handleGagRightClick(self, guiEvent=None):
        if self.gui is None:
            return
        self.gui.setLockIn(False)
        if self.townBattle is not None:
            self.townBattle.lockIn = False
            self.townBattle.manualUnlock = True
        self.__sendLockIn(False)

    def __handleGagChange(self, track, level):
        if self.gui.lockedIn or bool(getattr(self.townBattle, 'lockIn', False)):
            self.gui.setLockIn(False)
            self.__sendLockIn(False)
        if self.townBattle is not None:
            self.townBattle.lockIn = False
        self.track = track
        self.level = level
        self.mode = 'Inventory'
        if isinstance(track, int) and 0 <= track < len(TrackColors):
            color = TrackColors[track]
            self.gui.emblem['image_color'] = (color[0], color[1], color[2], 1)
        if self.gagChangeEvent is not None:
            messenger.send(self.gagChangeEvent, [{'mode': 'GagChange', 'track': track, 'level': level}])
