from toontown.clashsuit.suit import BossCogGlobals
from otp.ai.AIBaseGlobal import *
from toontown.inventory.base.Inventory import Inventory
from toontown.inventory.enums.ItemEnums import ClothingTopItemType
from toontown.clashsuit.suit import DistributedBossCogAI
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from direct.fsm import FSM
from toontown.toonbase import ToontownGlobals
from toontown.building import ClashSuitBuildingGlobals
import random
from toontown.groups.GroupEnums import GroupType


@DirectNotifyCategory()
class DistributedBoardbotBossAI(DistributedBossCogAI.DistributedBossCogAI, FSM.FSM):

    groupType = GroupType.COO
    
    limitHitCount = 6
    hitCountDamage = 35
    numPies = 10
    maxToonLevels = 77

    def __init__(self, air):
        DistributedBossCogAI.DistributedBossCogAI.__init__(self, air, 'g')
        FSM.FSM.__init__(self, 'DistributedBoardbotBossAI')
        self.lawyers = []
        self.cannons = None
        self.chairs = None
        self.gavels = None
        self.cagedToonNpcId = 90001
        self.bossMaxDamage = BossCogGlobals.LawbotBossMaxDamage
        self.battleOnePlanner = ClashSuitBuildingGlobals.SPE.CLO
        self.recoverRate = 0
        self.recoverStartTime = 0
        self.bossDamage = 0
        self.useCannons = 1
        self.numToonJurorsSeated = 0
        self.cannonBallsLeft = {}
        self.toonLevels = 0
        if 'Defeat' not in self.keyStates:
            self.keyStates.append('Defeat')
        self.toonupValue = 1
        self.bonusState = False
        self.bonusTimeStarted = 0
        self.numBonusStates = 0
        self.battleThreeTimeStarted = 0
        self.battleThreeTimeInMin = 0
        self.numAreaAttacks = 0
        self.lastAreaAttackTime = 0
        self.weightPerToon = {}
        self.cannonIndexPerToon = {}
        self.battleDifficulty = 0
        self.lawyersStunnedDict = {}
        self.toonDamagesDict = {}
        self.numStuns = 0

    def getHoodId(self):
        return ToontownGlobals.BoardbotHQ

    def doNextStrafe(self, task):
        if self.attackCode != BossCogGlobals.BossCogDizzyNow:
            side = random.choice([0, 1])
            direction = random.choice([0, 1])
            self.sendUpdate('doStrafe', [side, direction])
        delayTime = 9
        self.waitForNextStrafe(delayTime)
        
    def enterIntroduction(self):
        self.resetBattles()
        self.arenaSide = None
        self.barrier = self.beginBarrier('Introduction', self.involvedToons, 1460, self.doneIntroduction) # Wait 30 minutes in elevator
        for avId in self.involvedToons:
            av = simbase.air.doId2do.get(avId)
            if av:
                suits = [{'type': 'ottoman'}]
                av.initializeGalleryStatus(suits)

    def exitIntroduction(self):
        self.notify.debug('exitIntroduction')
        DistributedBossCogAI.DistributedBossCogAI.exitIntroduction(self)
        
    def doneIntroduction(self, avIds):
        self.b_setState('Epilogue')
        self.__doneVictory(avIds)

    def enterVictory(self):
        self.barrier = self.beginBarrier('Victory', self.involvedToons, 30, self.__doneVictory)
        
    def __doneVictory(self, avIds):
        # In Memoriam to this Return Statement
        # That Sketched Graciously Introduced In 2021
        # That Was Forgotten To Be Removed In 2022
        # Casuing Immense Pain And Torment For Tubby
        # return
        # ^^ R.I.P. to a real one - Madi, circa 2023
        # Hay Guys - Main, late 2023

        rewards = [ClothingTopItemType.RejectedSweater]
        for toonId in self.involvedToons:
            toon = simbase.air.doId2do.get(toonId)
            if not toon:
                continue
            inv: Inventory = toon.getHammerspace()
            if not inv:
                continue
            for reward in rewards:
                if inv.cache.getItemsOfSubtype(reward):
                    continue
                inv.addItem(reward)
