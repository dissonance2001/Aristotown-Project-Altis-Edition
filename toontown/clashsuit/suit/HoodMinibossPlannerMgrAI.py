from direct.showbase import PythonUtil, DirectObject
from panda3d.core import *
from direct.task import Task
from toontown.suit import HoodMinibossGlobals
from toontown.suit.SuitDefinitionsBase import SuitDefinitions
import random

from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class HoodMinibossPlannerMgrAI(DirectObject.DirectObject):
    CheckSpawnTime = 20

    def __init__(self, air, hoodId, hoodPlanners):
        self.air = air
        self.spawnDict = HoodMinibossGlobals.BossSpawnDict.get(hoodId, None)
        self.hoodId = hoodId
        self.hoodPlanners = hoodPlanners
        if not self.spawnDict:
            return

        # Start the initial task that will keep running
        for bossName in self.spawnDict.keys():
            self.doMethodLater(self.CheckSpawnTime, self.__spawnMiniboss, f'spawnMiniboss-{bossName}-{hoodId}', extraArgs=[bossName])
        
    def __spawnMiniboss(self, bossName):
        # Go through our current minibosses to check if we need to spawn a new one
        bossDef = self.spawnDict.get(bossName)
        suitDef = SuitDefinitions[bossName]

        # Check for what planners currently don't have minibosses on them
        openPlanners = self.getOpenMinibossPlanners(bossName)
        occupiedPlanners = self.getOccupiedMinibossPlanners(bossName)
        # Also check for what planners currently have battles on them
        occupiedBattlePlanners = self.getOccupiedMinibossBattleBranches(bossName)

        # We wanted limited spawns
        if bossDef[HoodMinibossGlobals.SPAWN_LIMITED]:
            # No open planners, die immediately
            if len(openPlanners) <= 0:
                self.notify.debug(f'No open planners for {self.hoodId}, doing nothing.')
                return Task.again

            # How many spawns we need based on the occupied battle planners
            # This will be the number of branches that have battles on them, plus 1,
            # capped to the total number of branches in this playground
            numSpawnsNeeded = min(len(occupiedBattlePlanners) + 1, len(self.hoodPlanners))
            self.notify.debug(f'Num spawns needed: {numSpawnsNeeded}. Hood Id: {self.hoodId}')
            # How many we have, both on the street or in battle
            numSpawnsWeHave = len(PythonUtil.union(occupiedPlanners, occupiedBattlePlanners))
            self.notify.debug(f'Num spawns we have: {numSpawnsWeHave}')
            # We have more spawns than we need so Die
            if numSpawnsWeHave >= numSpawnsNeeded:
                self.notify.debug('Had more or equal spawns than wanted, doing nothing.')
                return Task.again

            # We have less spawns than we need, so we can go ahead and choose from the open planners.
            chosenPlanner = random.choice(openPlanners)
            self.notify.debug(f'Chosen Planner: {chosenPlanner}.')
        else:
            # No spawn limit, pick a random branch
            chosenPlanner = random.choice(self.hoodPlanners)
            self.notify.debug(f'Random planner (No spawn limit), chose {chosenPlanner}.')
         
        pointmap = chosenPlanner.streetPointList[:]
        chosenPlanner.createNewSuit([], pointmap, suitName=bossName, suitLevel=list(suitDef.forceHp.keys())[0], summoned=True)
        self.notify.debug(f'Successfully spawned miniboss for planner {chosenPlanner} in Hood ID {self.hoodId}.')

        # Keep running the task!!
        return Task.again

    @property
    def totalHoodPlanners(self):
        return len(self.hoodPlanners)

    def getOpenMinibossPlanners(self, bossName):
        openPlanners = []
        for planner in self.hoodPlanners:
            # Planner is not occupied, add to open planners
            if not planner.countSuitsInPlanner(bossName):
                openPlanners.append(planner)

        return openPlanners

    def getOccupiedMinibossPlanners(self, bossName):
        return [planner for planner in self.hoodPlanners if planner not in self.getOpenMinibossPlanners(bossName)]

    def getOccupiedMinibossBattleBranches(self, bossName):
        plannersWithBattle = []
        for planner in self.hoodPlanners:
            # Check each battlecell for minibosses in battle
            for cellId in planner.battleMgr.cellId2battle.keys():
                # We found a miniboss in battle, add it to the list
                foundMiniboss = planner.battleMgr.countSuitsInBattle(cellId, bossName)
                if foundMiniboss and planner not in plannersWithBattle:
                    plannersWithBattle.append(planner)

        # Go ahead and return the battle planners
        return plannersWithBattle

    def getOpenMinibossBattleBranches(self, bossName):
        return [planner for planner in self.hoodPlanners if planner not in self.getOpenMinibossBattleBranches(bossName)]

    def cleanup(self):
        # Cleanup any spawn tasks
        self.removeAllTasks()
        self.spawnDict = {}
        self.hoodPlanners = []
