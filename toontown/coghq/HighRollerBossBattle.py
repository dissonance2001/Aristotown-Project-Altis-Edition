from pandac.PandaModules import *
from direct.directnotify import DirectNotifyGlobal
from toontown.battle import BattlePlace
from toontown.battle import InstanceBossBattle
from toontown.suit import DistributedHighRollerBoss
from toontown.suit import DistributedVideographerBoss


class HighRollerBossBattle(InstanceBossBattle.InstanceBossBattle):
    notify = DirectNotifyGlobal.directNotify.newCategory('HighRollerBossBattle')

    ParentStateName = 'majorPlayerBossBattle'

    def __init__(self, loader, parentFSM, doneEvent):
        InstanceBossBattle.InstanceBossBattle.__init__(self, loader, parentFSM, doneEvent)
        self.teleportInPosHpr = (0, -214, 0, 180, 0, 0)
        self._introRevealEvent = None

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
        arena = getattr(controller, 'highRollerArena', None)
        if arena is None or arena.isEmpty():
            return
        entrance = arena.find('**/elevator_origin')
        if entrance.isEmpty():
            self.notify.warning('High Roller arena has no elevator_origin; using fallback.')
            return
        pos = entrance.getPos(render)
        hpr = entrance.getHpr(render)
        self.teleportInPosHpr = (pos[0], pos[1], pos[2] + 0.05, hpr[0], hpr[1], hpr[2])

    def _getInstanceController(self, zoneId):
        for obj in base.cr.doId2do.values():
            if not isinstance(obj, (DistributedHighRollerBoss.DistributedHighRollerBoss, DistributedVideographerBoss.DistributedVideographerBoss)):
                continue
            try:
                if obj.getLocation()[1] == zoneId:
                    return obj
            except:
                pass
            if getattr(obj, 'zoneId', None) == zoneId:
                return obj
        return None

    def enter(self, requestStatus):
        controller = self._getInstanceController(requestStatus.get('zoneId'))
        if controller is None:
            self.notify.warning('Entering High Roller place before instance controller generated.')
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
        self._introRevealEvent = None
        if controller is not None:
            self._introRevealEvent = controller.uniqueName('IntroductionStarted')
            self.acceptOnce(self._introRevealEvent, self.__revealIntroduction)
        instanceStatus = requestStatus.copy()
        instanceStatus['how'] = 'walk'
        InstanceBossBattle.InstanceBossBattle.enter(self, instanceStatus, controller)

    def __revealIntroduction(self):
        try:
            base.transitions.fadeIn(0.5)
        except:
            pass
        self._introRevealEvent = None

    def exit(self):
        if self._introRevealEvent:
            self.ignore(self._introRevealEvent)
            self._introRevealEvent = None
        InstanceBossBattle.InstanceBossBattle.exit(self)

    def exitCrane(self):
        InstanceBossBattle.InstanceBossBattle.exitCrane(self)
        messenger.send('exitCrane')
