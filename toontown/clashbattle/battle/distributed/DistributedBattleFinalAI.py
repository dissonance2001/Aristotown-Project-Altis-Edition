from toontown.battle.SuitBattleGlobals import *
from toontown.battle.distributed.DistributedBattleBaseAI import DistributedBattleBaseAI


@DirectNotifyCategory()
class DistributedBattleFinalAI(DistributedBattleBaseAI):
    # Add a state for reserve suits to join to the battle FSM
    defaultTransitions = DistributedBattleBaseAI.defaultTransitions.copy()
    defaultTransitions.update({
        "ReservesJoining": ["WaitForJoin", "WaitForInput", "Resume"],
    })
    for state in ("Off", "WaitForJoin", "PlayMovie"):
        defaultTransitions[state].append("ReservesJoining")
    postResumeState = 'Reward'

    def __init__(self, air, bossCog, roundCallback, finishCallback, battleSide):
        self.bossCogId = bossCog.doId
        self.battleNumber = bossCog.battleNumber
        self.battleSide = battleSide
        self.streetBattle = 0
        self.roundCallback = roundCallback
        self.elevatorPos = Point3(0, 0, 0)
        self.pos = Point3(0, 30, 0)
        self.resumeNeedUpdate = 0
        DistributedBattleBaseAI.__init__(self, air, bossCog.zoneId, finishCallback)

    def delete(self):
        del self.roundCallback      # we don't need a reference to this anymore (possibly was causing leaks anyways)
        DistributedBattleBaseAI.delete(self)

    def getBossCogId(self):
        return self.bossCogId

    def getBattleNumber(self):
        return self.battleNumber

    def getBattleSide(self):
        return self.battleSide

    def startBattle(self, toonIds, suits):
        self.joinable = True
        for toonId in toonIds:
            toon = self.air.doId2do.get(toonId)
            if self.addToon(toonId) and toon:
                toon.setBattleState(BattleStateEnum.ACTIVE)

        # We have to be sure to tell the players that they're active
        # before we start adding suits.
        self.d_setMembers()

        for suit in suits:
            self.addSuit(suit)
            self.joinSuitNoPending(suit)

        self.d_setMembers()
        self.b_setState('ReservesJoining')
        self.waitForReservesJoining()
        
    # Each state will have an enter function, an exit function,
    # and a datagram handler, which will be set during each enter function.

    # Specific State functions

    ##### Off state #####

    ##### WaitForJoin state #####

    ##### WaitForInput state #####

    ##### PlayMovie state #####

    def localMovieDone(self, needUpdate, deadToons, deadSuits, lastActiveSuitDied):
        # Stop the server timeout for the movie
        self.timer.stop()

        self.resumeNeedUpdate = needUpdate
        self.resumeDeadToons = deadToons
        self.resumeDeadSuits = deadSuits
        self.resumeLastActiveSuitDied = lastActiveSuitDied

        if len(self.toons) == 0:
            # Toons lost - close up shop
            self.d_setMembers()
            self.b_setState('Resume')
        else:
            # Calculate the total hp of all the suits to see if any 
            # reserves need to join
            totalHp = 0
            for suit in self.suits:
                if suit.hp > 0:
                    totalHp += suit.hp

            # Signal the suit interior that the round is over and wait to
            # hear what to do next
            self.roundCallback(self.activeToons, totalHp, deadSuits)

    def resume(self, joinedReserves):
        if len(joinedReserves) != 0:
            for info in joinedReserves:
                self.addSuit(info[0])
                self.joinSuitNoPending(info[0])

            self.d_setMembers()
            self.b_setState('ReservesJoining')
            self.waitForReservesJoining()
        elif len(self.suits) == 0:
            # Toons won - award experience, etc.
            # battleMultiplier = getBossBattleCreditMultiplier(self.battleNumber)

            self.d_setMembers()
            self.d_setBattleExperience(self.getBattleExperience())
            self.b_setState(self.postResumeState)
        else:
            # Continue with the battle
            if self.resumeNeedUpdate == 1:
                self.d_setMembers()
            if ((len(self.resumeDeadSuits) > 0 or self.resumeLastActiveSuitDied == 0) and len(self.activeSuits) > 0) or len(self.resumeDeadToons) > 0 or len(self.pendingSuits) > 0:
                self.needAdjust = 1
            # Wait for input will call __requestAdjust()
            self.determineWaitState()

        self.resumeNeedUpdate = 0
        self.resumeDeadToons = []
        self.resumeDeadSuits = []
        self.resumeLastActiveSuitDied = 0
        
    ##### ReservesJoining state #####

    def waitForReservesJoining(self):
        self.beginBarrier('ReservesJoining', self.toons, 15, self._doneReservesJoining)

    def _doneReservesJoining(self, avIds):
        self.determineWaitState(fromReserves=True)

    def determineWaitState(self, fromReserves=False) -> None:
        """Determine which wait state to go into.

        For Cog Bosses and instances, if we have reserves, we always want to go to WaitForJoin.
        """
        if fromReserves:
            self.b_setState('WaitForJoin')
        else:
            super().determineWaitState()

    ##### Reward state #####

    def enterReward(self):
        messenger.send(self.uniqueName("battleFinalFinished"), [True])
        # In the building battles, we don't expect any toons to send a
        # done message before this (short) timer expires.  This is
        # just the between-floor reward dance, very brief.

        bossId = self.getBossCogId()
        boss = self.air.doId2do.get(bossId)
        if not boss:
            return

        for toon in self.toons:  # Clear out any surrenders at the end of the battle
            if toon in boss.surrenderRequests.keys():
                del boss.surrenderRequests[toon]

        self.timer.startCallback(FLOOR_REWARD_TIMEOUT + 5, self.serverRewardDone)

    def exitReward(self):
        self.timer.stop()
        
    ##### Resume state #####

    def enterResume(self):
        messenger.send(self.uniqueName("battleFinalFinished"), [False])
        self.joinable = False
        self.runable = False
        super().enterResume()
        self.finishCallback(self.zoneId, self.activeToons)

    ##### Messages from DistributedBattleFinal #####
    def toonRequestSurrender(self):
        toonId = self.air.getAvatarIdFromSender()
        if self.ignoreResponses == 1:
            self.notify.debug('ignoring response from toon: %d' % toonId)
            return
        self.notify.debug('toonRequestSurrender(%d)' % toonId)

        toon = self.air.doId2do.get(toonId)
        if not toon:
            return

        if toon.getBattleState() != BattleStateEnum.ACTIVE:
            self.notify.warning('toon tried to surrender, but not found in activeToons: %d' % toonId)
            return

        bossId = self.getBossCogId()
        boss = self.air.doId2do.get(bossId)
        if not boss:
            self.notify.warning('toon tried to surrender in boss, but no boss was found with doId: %d' % bossId)
            return

        # Register their surrender request
        # Toggle it to false if they surrender again
        if toonId in boss.surrenderRequests:
            boss.surrenderRequests[toonId] = not boss.surrenderRequests[toonId]
        else:
            boss.surrenderRequests[toonId] = True

        self.adjustSurrendered()

    def adjustSurrendered(self):
        bossId = self.getBossCogId()
        boss = self.air.doId2do.get(bossId)
        if not boss:
            self.notify.warning('tried to adjust surrender requests, but no boss was found with doId: %d' % bossId)
            return

        boss.adjustSurrendered()

    def finishSurrender(self):
        super().finishSurrender()
        bossId = self.getBossCogId()
        boss = self.air.doId2do.get(bossId)
        if not boss:
            self.notify.warning('tried to finish a boss surrender, but no boss was found with doId: %d' % bossId)
            return
        boss.setSurrender(True)

    def clearSurrenderRequests(self):
        bossId = self.getBossCogId()
        boss = self.air.doId2do.get(bossId)
        if boss:
            boss.clearSurrenderRequests()
