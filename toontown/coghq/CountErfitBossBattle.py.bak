from toontown.battle import BattlePlace
from toontown.building import CountErfitInstanceGlobals
from toontown.coghq import CogHQBossBattle
from toontown.suit import DistributedCountErfitBoss
from toontown.suit import Suit

class CountErfitBossBattle(CogHQBossBattle.CogHQBossBattle):
    notify = directNotify.newCategory('CountErfitBossBattle')
    ParentStateName = CountErfitInstanceGlobals.BOSS_BATTLE_STATE

    def __init__(self, loader, parentFSM, doneEvent):
        CogHQBossBattle.CogHQBossBattle.__init__(self, loader, parentFSM, doneEvent)
        self.teleportInPosHpr = (0, 0, 0, 180, 0, 0)

    def load(self):
        BattlePlace.BattlePlace.load(self)
        self.parentFSM.getStateNamed(self.ParentStateName).addChild(self.fsm)
        self.townBattle = self.loader.townBattle
        for i in xrange(1, 3):
            Suit.loadSuits(i)

    def unload(self):
        BattlePlace.BattlePlace.unload(self)
        self.parentFSM.getStateNamed(self.ParentStateName).removeChild(self.fsm)
        del self.parentFSM
        del self.fsm
        self.ignoreAll()
        for i in xrange(1, 3):
            Suit.unloadSuits(i)

    def _setArenaTeleportPosition(self, controller):
        if not controller:
            return
        entrance = getattr(controller, 'elevatorEntrance', None)
        if entrance is None or entrance.isEmpty():
            arena = getattr(controller, 'geom', None)
            if arena is not None and not arena.isEmpty():
                entrance = arena.find('**/elevator_origin')
        if entrance is None or entrance.isEmpty():
            return
        pos = entrance.getPos(render)
        hpr = entrance.getHpr(render)
        self.teleportInPosHpr = (
            pos[0], pos[1], pos[2] + 0.05,
            hpr[0], hpr[1], hpr[2])

    def enter(self, requestStatus):
        controller = DistributedCountErfitBoss.OneBossCog
        self._setArenaTeleportPosition(controller)
        try:
            base.transitions.fadeOut(0.0)
        except:
            pass
        try:
            base.localAvatar.setPosHpr(render, *self.teleportInPosHpr)
        except:
            try:
                base.localAvatar.setPosHpr(*self.teleportInPosHpr)
            except:
                pass
        instanceStatus = requestStatus.copy()
        instanceStatus['how'] = 'walk'
        CogHQBossBattle.CogHQBossBattle.enter(self, instanceStatus, controller)

    def exit(self):
        CogHQBossBattle.CogHQBossBattle.exit(self)
