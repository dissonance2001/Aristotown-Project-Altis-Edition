from toontown.coghq.CogHQBossBattle import CogHQBossBattle
from toontown.battle import BattlePlace
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class InstanceBattle(CogHQBossBattle):
    WantTelemetryLimiter = False
    BattleFSMName = 'InstanceBattle'

    def load(self):
        BattlePlace.BattlePlace.load(self, self.getGagMultiplier())
        self.townBattle = self.loader.townBattle

    def unload(self):
        BattlePlace.BattlePlace.unload(self)
        del self.parentFSM
        self.ignoreAll()
