from __future__ import absolute_import
from toontown.battle import BattlePlace
from toontown.building import ChainsawInstanceGlobals
from toontown.coghq import CogHQBossBattle
from toontown.suit import DistributedChainsawBoss


class ChainsawBossBattle(CogHQBossBattle.CogHQBossBattle):
    notify = directNotify.newCategory('ChainsawBossBattle')
    ParentStateName = ChainsawInstanceGlobals.BOSS_BATTLE_STATE

    def __init__(self, loader, parentFSM, doneEvent):
        CogHQBossBattle.CogHQBossBattle.__init__(
            self, loader, parentFSM, doneEvent)
        self.teleportInPosHpr = ChainsawInstanceGlobals.TELEPORT_IN_POS_HPR

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

    def _setArenaTeleportPosition(self, controller):
        if not controller:
            return
        geom = getattr(controller, 'geom', None)
        if geom is None or geom.isEmpty():
            return
        entrance = geom.find('**/door_origin_0')
        if entrance.isEmpty():
            self.notify.warning(
                'Chainsaw room has no door_origin_0; using fallback.')
            return
        marker = entrance.attachNewNode('chainsawTeleportMarker')
        marker.setPos(0, -5.5, 0)
        pos = marker.getPos(render)
        hpr = entrance.getHpr(render)
        marker.removeNode()
        self.teleportInPosHpr = (
            pos[0], pos[1], pos[2] + 0.05,
            hpr[0], hpr[1], hpr[2])

    def enter(self, requestStatus):
        controller = DistributedChainsawBoss.OneChainsawController
        if controller is None:
            self.notify.warning(
                'Entering Chainsaw place before controller generated.')
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
        CogHQBossBattle.CogHQBossBattle.enter(
            self, instanceStatus, controller)

    def exit(self):
        CogHQBossBattle.CogHQBossBattle.exit(self)
