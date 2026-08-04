from pandac.PandaModules import *
from direct.interval.IntervalGlobal import *
from direct.directnotify import DirectNotifyGlobal
from toontown.battle import BattlePlace
from toontown.coghq import CogHQBossBattle
from toontown.suit import DistributedHighRollerBoss


class HighRollerBossBattle(CogHQBossBattle.CogHQBossBattle):
    """High Roller place hosted by the generic Major Player state."""

    notify = DirectNotifyGlobal.directNotify.newCategory(
        'HighRollerBossBattle')

    ParentStateName = 'majorPlayerBossBattle'

    def __init__(self, loader, parentFSM, doneEvent):
        CogHQBossBattle.CogHQBossBattle.__init__(
            self, loader, parentFSM, doneEvent)
        # Only used if the arena's elevator_origin is unexpectedly absent.
        self.teleportInPosHpr = (0, -214, 0, 180, 0, 0)

    def load(self):
        # CogHQBossBattle.load() hardcodes the regular Cog HQ state.
        # Major Player minibosses instead share one lightweight state inside
        # MMTownLoader; no separate hood or HQ loader is constructed.
        BattlePlace.BattlePlace.load(self)
        self.parentFSM.getStateNamed(self.ParentStateName).addChild(self.fsm)
        self.townBattle = self.loader.townBattle

    def unload(self):
        BattlePlace.BattlePlace.unload(self)
        self.parentFSM.getStateNamed(self.ParentStateName).removeChild(self.fsm)
        del self.parentFSM
        del self.fsm
        self.ignoreAll()

    def _setArenaTeleportPosition(self, bossCog):
        if not bossCog:
            return
        arena = getattr(bossCog, 'highRollerArena', None)
        if arena is None or arena.isEmpty():
            return
        entrance = arena.find('**/elevator_origin')
        if entrance.isEmpty():
            self.notify.warning(
                'High Roller arena has no elevator_origin; using fallback.')
            return

        # The locator is part of the High Roller BAM, so this remains correct
        # even if the arena is moved later.  It replaces the old CFO-specific
        # hardcoded position at x=88.
        pos = entrance.getPos(render)
        hpr = entrance.getHpr(render)
        self.teleportInPosHpr = (
            pos[0], pos[1], pos[2] + 0.05,
            hpr[0], hpr[1], hpr[2])

    def enter(self, requestStatus):
        bossCog = DistributedHighRollerBoss.OneBossCog
        if bossCog is None:
            self.notify.warning(
                'Entering High Roller place before boss object generated.')
        self._setArenaTeleportPosition(bossCog)
        CogHQBossBattle.CogHQBossBattle.enter(
            self, requestStatus, bossCog)

    def exit(self):
        CogHQBossBattle.CogHQBossBattle.exit(self)

    def exitCrane(self):
        CogHQBossBattle.CogHQBossBattle.exitCrane(self)
        messenger.send('exitCrane')
