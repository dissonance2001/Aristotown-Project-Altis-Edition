from functools import cmp_to_key
from panda3d.core import *
from direct.directnotify import DirectNotifyGlobal
from toontown.toonbase import ToontownGlobals
from toontown.coghq import DistributedCashbotBossCraneAI
from toontown.coghq import DistributedCashbotBossSafeAI
from toontown.suit import DistributedCashbotBossGoonAI
from toontown.coghq import DistributedCashbotBossTreasureAI
from toontown.battle import BattleExperienceAI
from toontown.chat import ResistanceChat
from direct.fsm import FSM
from . import DistributedMinibossAI
from . import SuitDNA
import random
import math

class DistributedCashbotBossMiniAI(DistributedMinibossAI.DistributedMinibossAI, FSM.FSM):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedCashbotBossMiniAI')

    def __init__(self, air):
        DistributedMinibossAI.DistributedMinibossAI.__init__(self, air, 'm')
        FSM.FSM.__init__(self, 'DistributedCashbotBossAI')
        self.rewardId = ResistanceChat.getRandomId()
        self.rewardedToons = []
        self.scene = NodePath('scene')
        self.reparentTo(self.scene)
        cn = CollisionNode('walls')
        cs = CollisionSphere(0, 0, 0, 13)
        cn.addSolid(cs)
        cs = CollisionInvSphere(0, 0, 0, 42)
        cn.addSolid(cs)
        self.attachNewNode(cn)
        return

    def generate(self):
        DistributedMinibossAI.DistributedMinibossAI.generate(self)
        if __dev__:
            self.scene.reparentTo(self.getRender())

    def getHoodId(self):
        return ToontownGlobals.CashbotHQ

    def formatReward(self):
        return str(self.rewardId)

    def makeBattleOneBattles(self):
        self.postBattleState = 'Victory'
        self.initializeBattles(1, ToontownGlobals.CashbotBossBattleOnePosHpr)

    def generateSuits(self, battleNumber):
        cogs = self.invokeEmptyPlanner(11, 'crf')
        activeSuits = cogs['activeSuits']
        reserveSuits = cogs['reserveSuits']
        random.shuffle(activeSuits)
        while len(activeSuits) > 6:
            suit = activeSuits.pop()
            reserveSuits.append((suit, 100))

        def compareJoinChance(a, b):
            return cmp(a[1], b[1])

        reserveSuits.sort(key=cmp_to_key(compareJoinChance))
        return {'activeSuits': activeSuits,
         'reserveSuits': reserveSuits}

    def generateNewReserves(self, battleNumber):
        cogs = self.invokeReservesPlanner(11, 'crf')
        reserveSuits = cogs['reserveSuits']
        return {'reserveSuits': reserveSuits}

    def removeToon(self, avId):
        DistributedMinibossAI.DistributedMinibossAI.removeToon(self, avId)

    def d_setRewardId(self, rewardId):
        self.sendUpdate('setRewardId', [rewardId])

    def applyReward(self):
        avId = self.air.getAvatarIdFromSender()
        if avId in self.involvedToons and avId not in self.rewardedToons:
            self.rewardedToons.append(avId)
            toon = self.air.doId2do.get(avId)
            if toon:
                toon.doResistanceEffect(self.rewardId)

    def enterOff(self):
        DistributedMinibossAI.DistributedMinibossAI.enterOff(self)
        self.rewardedToons = []

    def exitOff(self):
        DistributedMinibossAI.DistributedMinibossAI.exitOff(self)

    def enterIntroduction(self):
        DistributedMinibossAI.DistributedMinibossAI.enterIntroduction(self)

    def exitIntroduction(self):
        DistributedMinibossAI.DistributedMinibossAI.exitIntroduction(self)

    def enterVictory(self):
        self.resetBattles()
        self.suitsKilled.append({'type': None,
         'level': None,
         'track': self.dna.dept,
         'isSkelecog': 0,
         'isForeman': 0,
         'isVP': 0,
         'isCFO': 1,
         'isSupervisor': 0,
         'isVirtual': 0,
         'activeToons': self.involvedToons[:]})
        self.barrier = self.beginBarrier('Victory', self.involvedToons, 30, self.__doneVictory)
        return

    def __doneVictory(self, avIds):
        self.d_setBattleExperience()
        self.b_setState('Reward')
        BattleExperienceAI.assignRewards(self.involvedToons, self.toonSkillPtsGained, self.suitsKilled, ToontownGlobals.dept2cogHQ(self.dept), self.helpfulToons)
        for toonId in self.involvedToons:
            toon = self.air.doId2do.get(toonId)
            if toon:
                toon.addResistanceMessage(self.rewardId)
                toon.b_promote(self.deptIndex)

    def exitVictory(self):
        pass

    def enterEpilogue(self):
        DistributedMinibossAI.DistributedMinibossAI.enterEpilogue(self)
        self.d_setRewardId(self.rewardId)
