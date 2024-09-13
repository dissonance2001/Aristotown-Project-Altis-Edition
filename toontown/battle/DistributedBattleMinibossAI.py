from direct.directnotify import DirectNotifyGlobal
from toontown.battle import DistributedBattleFinalAI
from toontown.toonbase import ToontownBattleGlobals
from otp.ai.AIBase import *
from toontown.battle.BattleBase import *
from toontown.battle.BattleCalculatorAI import *
from toontown.toonbase.ToontownBattleGlobals import *
from toontown.battle.SuitBattleGlobals import *
from toontown.battle import DistributedBattleBaseAI
from direct.task import Task
from direct.directnotify import DirectNotifyGlobal
from direct.fsm import State
from toontown.toonbase.ToonPythonUtil import addListsByValue
import random
import types

class DistributedBattleMinibossAI(DistributedBattleFinalAI.DistributedBattleFinalAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedBattleMinibossAI')

    def __init__(self, air, bossCog, roundCallback, finishCallback, battleSide):
        DistributedBattleFinalAI.DistributedBattleFinalAI.__init__(self, air, bossCog, roundCallback, finishCallback, battleSide)
        self.bossCogId = bossCog.doId
        self.battleNumber = bossCog.battleNumber
        self.battleSide = battleSide
        self.streetBattle = 0
        self.roundCallback = roundCallback
        self.elevatorPos = Point3(0, 0, 0)
        self.pos = Point3(0, 30, 0)
        self.resumeNeedUpdate = 0
        self.fsm.addState(
            State.State('ReservesJoining', self.enterReservesJoining, self.exitReservesJoining, ['WaitForJoin']))
        offState = self.fsm.getStateNamed('Off')
        offState.addTransition('ReservesJoining')
        waitForJoinState = self.fsm.getStateNamed('WaitForJoin')
        waitForJoinState.addTransition('ReservesJoining')
        playMovieState = self.fsm.getStateNamed('PlayMovie')
        playMovieState.addTransition('ReservesJoining')


    def getBossCogId(self):
        return self.bossCogId

    def getBattleNumber(self):
        return self.battleNumber

    def getBattleSide(self):
        return self.battleSide

    def startBattle(self, toonIds, suits):
        self.joinableFsm.request('Joinable')
        for toonId in toonIds:
            if self.addToon(toonId):
                self.activeToons.append(toonId)

        self.d_setMembers()
        for suit in suits:
            joined = self.suitRequestJoin(suit)

        self.d_setMembers()
        self.b_setState('ReservesJoining')


    def resume(self, joinedReserves):
        if len(joinedReserves) != 0:
            for info in joinedReserves:
                joined = self.suitRequestJoin(info)

            self.d_setMembers()
            self.b_setState('ReservesJoining')
        elif len(self.suits) == 0:
            battleMultiplier = ToontownBattleGlobals.getBossBattleCreditMultiplier(self.battleNumber)
            for toonId in self.activeToons:
                toon = self.getToon(toonId)
                if toon:
                    recovered, notRecovered = self.air.questManager.recoverItems(toon, self.suitsKilledThisBattle,
                                                                                 self.zoneId)
                    self.toonItems[toonId][0].extend(recovered)
                    self.toonItems[toonId][1].extend(notRecovered)

            self.d_setMembers()
            self.d_setBattleExperience()
            self.b_setState('Reward')
        else:
            if self.resumeNeedUpdate == 1:
                self.d_setMembers()
                if len(self.resumeDeadSuits) > 0 and self.resumeLastActiveSuitDied == 0 or len(
                        self.resumeDeadToons) > 0:
                    self.needAdjust = 1
            self.setState('WaitForJoin')
        self.resumeNeedUpdate = 0
        self.resumeDeadToons = []
        self.resumeDeadSuits = []
        self.resumeLastActiveSuitDied = 0