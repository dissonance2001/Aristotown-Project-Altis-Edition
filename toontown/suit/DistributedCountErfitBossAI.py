from __future__ import absolute_import
from direct.directnotify import DirectNotifyGlobal

from toontown.suit import DistributedMinibossAI
from toontown.suit.DistributedCountErclaimBossAI import DistributedCountErclaimBossAI
from toontown.battle import BattleExperienceAI
from toontown.toonbase import ToontownGlobals


class DistributedCountErfitBossAI(DistributedCountErclaimBossAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedCountErfitBossAI')

    def __init__(self, air):
        DistributedCountErclaimBossAI.__init__(self, air)

    def getHoodId(self):
        return ToontownGlobals.TheBrrrgh

    def _clearCogDisguises(self):
        for toonId in self.involvedToons:
            toon = self.air.doId2do.get(toonId)
            if toon:
                toon.b_setCogIndex(-1)

    def enterElevator(self):
        self._clearCogDisguises()
        DistributedMinibossAI.DistributedMinibossAI.enterElevator(self)

    def enterIntroduction(self):
        self._clearCogDisguises()
        DistributedMinibossAI.DistributedMinibossAI.enterIntroduction(self)

    def exitIntroduction(self):
        DistributedMinibossAI.DistributedMinibossAI.exitIntroduction(self)
        self._clearCogDisguises()

    def makeBattleOneBattles(self):
        self.postBattleState = 'Victory'
        self.initializeBattles(1, ToontownGlobals.CountErclaimBattleAPosHpr)

    def enterVictory(self):
        self.resetBattles()
        self._clearCogDisguises()
        self.barrier = self.beginBarrier('Victory', self.involvedToons, 30, self._doneErfitVictory)

    def _doneErfitVictory(self, avIds):
        self.d_setBattleExperience()
        BattleExperienceAI.assignRewards(
            self.involvedToons,
            self.toonSkillPtsGained,
            self.suitsKilled,
            ToontownGlobals.PolarPlace,
            self.helpfulToons)
        self.b_setState('Reward')

    def exitVictory(self):
        self._clearCogDisguises()
