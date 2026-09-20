from toontown.clashbattle.battle.distributed.DistributedBattleBaseAI import DistributedBattleBaseAI
from toontown.clashbattle.battle.SuitBattleGlobals import *
from direct.distributed.ClockDelta import *
from toontown.ai.AIBase import *
from toontown.clashbattle.battle.BattleGlobals import *
from direct.showbase.PythonUtil import addListsByValue
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class DistributedBattleBldgAI(DistributedBattleBaseAI):
    # Add a new reward state to the battle FSM
    defaultTransitions = DistributedBattleBaseAI.defaultTransitions.copy()
    defaultTransitions.update({
        "BuildingReward": ["Resume"],
    })
    for state in ("PlayMovie",):
        defaultTransitions[state].append("BuildingReward")

    def __init__(self, air, zoneId, roundCallback=None, finishCallback=None, maxSuits=4, bossBattle=0, floor=None, maxFloor=None):
        self.streetBattle = 0
        self.floor = floor
        self.maxFloor = maxFloor
        self.roundCallback = roundCallback
        DistributedBattleBaseAI.__init__(self, air, zoneId, finishCallback, maxSuits, bossBattle)

        self.elevatorPos = Point3(0, -30, 0)
        self.resumeNeedUpdate = 0

    def announceGenerate(self):
        DistributedBattleBaseAI.announceGenerate(self)
        self.registerToons()

    def setInitialMembers(self, toonIds, suits):
        for suit in suits:
            self.addSuit(suit)
        for toonId in toonIds:
            self.addToon(toonId)
        self.request('FaceOff')

    def registerToons(self):
        for toonId in self.toons:
            toon = simbase.air.doId2do.get(toonId)
            toon.b_setBattleId(self.doId)

    def delete(self):
        del self.roundCallback
        DistributedBattleBaseAI.delete(self)

    def faceOffDone(self):
        toonId = self.air.getAvatarIdFromSender()
        if self.ignoreResponses == 1:
            self.notify.debug('faceOffDone() - ignoring toon: %d' % toonId)
            return
        elif self.getCurrentOrNextState() != 'FaceOff':
            self.notify.warning('faceOffDone() - in state: %s' % self.getCurrentOrNextState())
            return
        elif self.toons.count(toonId) == 0:
            self.notify.warning('faceOffDone() - toon: %d not in toon list' % toonId)
            return
        self.responses[toonId] += 1
        self.notify.debug('toon: %d done facing off' % toonId)
        if not self.ignoreFaceOffDone:
            if self.allToonsResponded():
                self.handleFaceOffDone()
            else:
                # Reset the timer to give the slowpokes a few seconds
                # longer than the first (or most recent) toon to reply.
                self.timer.stop()
                self.timer.startCallback(TIMEOUT_PER_USER, self.__serverFaceOffDone)
                
    # Each state will have an enter function, an exit function,
    # and a datagram handler, which will be set during each enter function.

    # Specific State functions

    ##### Off state #####

    ##### FaceOff state #####

    # original suit and toon face off and then walk to positions,
    # other toons or suits walk directly to wait positions

    def enterFaceOff(self):
        self.notify.debug('enterFaceOff()')
        self.joinable = True
        self.runable = False
        # From here on out DistributedBattleAI only controls DistributedSuitAI
        # DistributedBattle controls DistributedSuit
        self.timer.startCallback(self.calcToonMoveTime(self.pos, self.elevatorPos) + FACEOFF_TAUNT_T + SERVER_BUFFER_TIME, self.__serverFaceOffDone)

    def __serverFaceOffDone(self):
        self.notify.debug('faceoff timed out on server')
        self.ignoreFaceOffDone = 1
        self.handleFaceOffDone()

    def exitFaceOff(self):
        self.timer.stop()
        self.resetPlayerResponses()

    def handleFaceOffDone(self):
        for suit in self.suits:
            self.addActiveSuit(suit)
        for t in self.toons:
            toon = self.air.doId2do.get(t)
            if toon:
                toon.setBattleState(BattleStateEnum.ACTIVE)
                self.sendEarnedExperience(t)
        # Set our initial battle avatars on the face off.
        self.updateBattleAvatars()
        self.d_setMembers()
        if self.needAdjust:
            self.b_setState('WaitForInput')
            
    ##### WaitForJoin state #####

    ##### WaitForInput state #####

    ##### PlayMovie state #####

    def localMovieDone(self, needUpdate, deadToons, deadSuits, lastActiveSuitDied):
        self.timer.stop()
        self.resumeNeedUpdate = needUpdate
        self.resumeDeadToons = deadToons
        self.resumeDeadSuits = deadSuits
        self.resumeLastActiveSuitDied = lastActiveSuitDied
        if len(self.toons) == 0:
            self.d_setMembers()
            self.b_setState('Resume')
        else:
            # Calculate the total hp of all the suits to see if any 
            # reserves need to join
            totalHp = 0
            for suit in self.suits:
                if suit.hp > 0:
                    totalHp += suit.hp
                    continue
            # Signal the suit interior that the round is over and wait to
            # hear what to do next
            self.roundCallback(self.activeToons, totalHp, deadSuits)

    def __goToResumeState(self, task):
        self.b_setState('Resume')

    def resume(self, currentFloor=0, topFloor=0):
        if len(self.suits) == 0:
            # Toons won - award experience, etc.
            self.d_setMembers()
            self.suitsKilledPerFloor.append(self.suitsKilledThisBattle)
            if topFloor == 0:
                self.b_setState('Reward')
            else:
                # calculate and assign the merits and item recoveries by floor
                for floorNum, cogsThisFloor in enumerate(self.suitsKilledPerFloor):
                    for toonId in self.activeToons:
                        if toonId in self.npcToons:
                            continue
                        toon = self.getToon(toonId)
                        if toon:
                            # the new merit list must be added by value to the cumulative list
                            meritArray = self.air.promotionMgr.recoverMerits(toon, cogsThisFloor, self.zoneId, getBuildingCreditMultiplier(self.maxFloor), respectInvasionBonus=False)

                            if toonId in self.helpfulToons:
                                self.toonMerits[toonId] = addListsByValue(self.toonMerits[toonId], meritArray)
                            else:
                                self.notify.debug('toon %d not helpful, skipping merits' % toonId)

                self.prepareReward('BuildingReward')
        else:
            if self.resumeNeedUpdate == 1:
                # Continue with the battle
                self.d_setMembers()
                # if ( (a suit died or got resumed) and theres active suits in battle) or toons got resumed or theres pending suits to join
                if ((len(self.resumeDeadSuits) > 0 or self.resumeLastActiveSuitDied == 0) and len(self.activeSuits) > 0) or len(self.resumeDeadToons) > 0 or len(self.pendingSuits) > 0:
                    self.needAdjust = 1

            # Wait for input will call __requestAdjust()
            self.determineWaitState()

        self.resumeNeedUpdate = 0
        self.resumeDeadToons = []
        self.resumeDeadSuits = []
        self.resumeLastActiveSuitDied = 0
        
    ##### ReservesJoining state #####

    ##### Reward state #####
        
    def enterReward(self):
        # In the building battles, we don't expect any toons to send a
        # done message before this (short) timer expires.  This is
        # just the between-floor reward dance, very brief.
        self.timer.startCallback(FLOOR_REWARD_TIMEOUT, self.serverRewardDone)

    def exitReward(self):
        self.timer.stop()
        
    ##### BuildingReward state #####

    def enterBuildingReward(self):
        self.resetPlayerResponses()
        self.assignRewards()
        
        # Set an upper timeout for the reward movie.  If no toons
        # report back by this time, call it done anyway.
        self.timer.startCallback(BUILDING_REWARD_TIMEOUT, self.serverRewardDone)

    def exitBuildingReward(self):
        self.exitResume()
        
    ##### Resume state #####

    def enterResume(self):
        activeToons = self.activeToons
        DistributedBattleBaseAI.enterResume(self)
        self.finishCallback(self.zoneId, activeToons)

    def exitResume(self):
        DistributedBattleBaseAI.exitResume(self)
        taskName = self.taskName('finish')
        taskMgr.remove(taskName)
