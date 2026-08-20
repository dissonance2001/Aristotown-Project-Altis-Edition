from __future__ import absolute_import
from toontown.battle import BattlePlace
from toontown.building import PacesetterInstanceGlobals
from toontown.coghq import CogHQBossBattle
from toontown.suit import DistributedPacesetterBoss


class PacesetterBossBattle(CogHQBossBattle.CogHQBossBattle):
    """Client place for the standalone Pacesetter dynamic instance."""

    notify = directNotify.newCategory('PacesetterBossBattle')

    ParentStateName = PacesetterInstanceGlobals.BOSS_BATTLE_STATE

    def __init__(self, loader, parentFSM, doneEvent):
        CogHQBossBattle.CogHQBossBattle.__init__(
            self, loader, parentFSM, doneEvent)

        # Used only when the Pacesetter room's elevator locator cannot be found.
        self.teleportInPosHpr = (0, 0, 0, 180, 0, 0)

    def load(self):
        # CogHQBossBattle.load() always attaches to the normal
        # 'cogHQBossBattle' state.  Pacesetter instead owns a dedicated state
        # inside DLTownLoader, so no VP/CFO/CJ loader is involved.
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

        entrance = getattr(controller, 'elevatorEntrance', None)
        if entrance is None or entrance.isEmpty():
            arena = getattr(controller, 'geom', None)
            if arena is not None and not arena.isEmpty():
                entrance = arena.find('**/elevator_origin')

        if entrance is None or entrance.isEmpty():
            self.notify.warning(
                'Pacesetter arena has no elevator_origin; using fallback.')
            return

        pos = entrance.getPos(render)
        hpr = entrance.getHpr(render)
        self.teleportInPosHpr = (
            pos[0], pos[1], pos[2] + 0.05,
            hpr[0], hpr[1], hpr[2])

    def enter(self, requestStatus):
        controller = DistributedPacesetterBoss.OnePacesetterController
        if controller is None:
            self.notify.warning(
                'Entering Pacesetter place before boss object generated.')

        self._setArenaTeleportPosition(controller)

        # The lobby elevator has already faded the screen out.  Do not run
        # Place.teleportIn here: its irisIn reveals the newly-loaded arena for
        # a moment before Pacesetter's real elevator movie takes control.
        # Enter walk under the existing black cover so the v7 readiness gate
        # can advance immediately to walk -> movie; enterElevator() will fade
        # back in only after its camera is mounted inside the cabin.
        try:
            base.transitions.fadeOut(0.0)
        except:
            pass
        try:
            base.localAvatar.setPosHpr(
                render, *self.teleportInPosHpr)
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

    def exitCrane(self):
        CogHQBossBattle.CogHQBossBattle.exitCrane(self)
        messenger.send('exitCrane')
