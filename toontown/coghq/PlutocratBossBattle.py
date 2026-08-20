from __future__ import absolute_import
from toontown.battle import BattlePlace
from toontown.building import PlutocratInstanceGlobals
from toontown.coghq import CogHQBossBattle
from toontown.suit import DistributedPlutocratBoss


class PlutocratBossBattle(CogHQBossBattle.CogHQBossBattle):
    notify = directNotify.newCategory('PlutocratBossBattle')
    ParentStateName = PlutocratInstanceGlobals.BOSS_BATTLE_STATE

    def __init__(self, loader, parentFSM, doneEvent):
        CogHQBossBattle.CogHQBossBattle.__init__(self, loader, parentFSM, doneEvent)
        self.teleportInPosHpr = PlutocratInstanceGlobals.TELEPORT_IN_POS_HPR

    def load(self):
        BattlePlace.BattlePlace.load(self)
        self.parentFSM.getStateNamed(self.ParentStateName).addChild(self.fsm)
        self.townBattle = self.loader.townBattle

    def unload(self):
        BattlePlace.BattlePlace.unload(self)
        self.parentFSM.getStateNamed(self.ParentStateName).removeChild(self.fsm)
        del self.parentFSM
        del self.fsm
        self.ignoreAll()

    def enter(self, requestStatus):
        controller = DistributedPlutocratBoss.OnePlutocratController
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
