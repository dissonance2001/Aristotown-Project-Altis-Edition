from toontown.clashbattle.battle.SuitBattleGlobals import *
from toontown.clashbattle.battle.distributed.DistributedBattleBaseAI import DistributedBattleBaseAI
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from toontown.toon.gui.ToonTipGlobals import TTE


# Attack properties table
@DirectNotifyCategory()
class DistributedBattleAI(DistributedBattleBaseAI):
    def __init__(self, air, battleMgr, pos, suit, toonId, zoneId, finishCallback = None, maxSuits = 4, tutorialFlag = 0, levelFlag = 0, interactivePropTrackBonus = -1):
        DistributedBattleBaseAI.__init__(self, air,
                zoneId, finishCallback, maxSuits=maxSuits,
                tutorialFlag=tutorialFlag, interactivePropTrackBonus=interactivePropTrackBonus)

        self.battleMgr = battleMgr
        self.pos = pos

        # Store the initial position of the suit when contact occurred
        self.initialSuitPos = suit.getConfrontPosHpr()[0]
        # CCC for now use the suit position as the toonposition as they
        # should be fairly close anyways
        self.initialToonPos = suit.getConfrontPosHpr()[0]
        self.addSuit(suit)
        # For levels, we need to initialize exp lists before we add the
        # toon
        self.avId = toonId
        
        if levelFlag == 0:
            self.addToon(toonId)

        self.faceOffToon = toonId
        self.request('FaceOff')

    def generate(self):
        DistributedBattleBaseAI.generate(self)
        toon = simbase.air.doId2do.get(self.avId)
        if toon:
            if hasattr(self, 'doId'):
                toon.b_setBattleId(self.doId)
            else:
                toon.b_setBattleId(-1)
        self.avId = None

    def faceOffDone(self):
        toonId = self.air.getAvatarIdFromSender()
        if self.ignoreFaceOffDone == 1:
            self.notify.debug('faceOffDone() - ignoring toon: %d' % toonId)
            return
        elif self.getCurrentOrNextState() != 'FaceOff':
            self.notify.warning('faceOffDone() - in state: %s' % self.getCurrentOrNextState())
            return
        elif self.toons.count(toonId) == 0:
            self.notify.warning('faceOffDone() - toon: %d not in toon list' % toonId)
            return
        self.notify.debug('toon: %d done facing off' % toonId)
        self.handleFaceOffDone()
        
    # Each state will have an enter function, an exit function,
    # and a datagram handler, which will be set during each enter function.

    # Specific State functions

    ##### Off state #####

    ##### FaceOff state #####

    # Original suit and toon face off and then walk to positions,
    # other toons or suits walk directly to wait positions

    def enterFaceOff(self):
        self.notify.debug('enterFaceOff()')
        self.joinable = True
        self.runable = False
        # From here on out DistributedBattleAI only controls DistributedSuitAI
        # DistributedBattle controls DistributedSuit
        self.suits[0].releaseControl()
        timeForFaceoff = self.calcFaceoffTime(self.pos, self.initialSuitPos) + FACEOFF_TAUNT_T + SERVER_BUFFER_TIME
        if self.interactivePropTrackBonus >= 0:
            timeForFaceoff += FACEOFF_LOOK_AT_PROP_T
        self.timer.startCallback(timeForFaceoff, self.__serverFaceOffDone)

    def __serverFaceOffDone(self):
        self.notify.debug('faceoff timed out on server')
        self.ignoreFaceOffDone = 1
        self.handleFaceOffDone()

    def exitFaceOff(self):
        self.timer.stop()

    def handleFaceOffDone(self):
        self.timer.stop()
        self.addActiveSuit(self.suits[0])
        # The face off toon might have disconnected, so we need to check
        # that self.toons[0] is the face off toon. 
        if len(self.toons) == 0:
            self.b_setState('Resume')
        elif self.faceOffToon == self.toons[0]:
            toon = self.air.doId2do.get(self.toons[0])
            if toon:
                toon.setBattleState(BattleStateEnum.ACTIVE)
            # Clear out the toon's earned experience so far.
            self.sendEarnedExperience(self.toons[0])
        # Set our initial battle avatars on the face off.
        self.updateBattleAvatars()
        self.d_setMembers()
        self.b_setState('WaitForInput')
        
    ##### WaitForJoin state #####

    ##### WaitForInput state #####

    ##### PlayMovie state #####

    def localMovieDone(self, needUpdate, deadToons, deadSuits, lastActiveSuitDied):
        if len(self.toons) == 0:
            # Toons lost - tell all the suits to start walking again
            self.d_setMembers()
            self.b_setState('Resume')
        elif len(self.suits) == 0:
            # Toons won - award experience, etc.
            for toonId in self.activeToons:
                if toonId in self.npcToons:
                    continue
                toon = self.getToon(toonId)
                if toon:
                    # First Victory Tip
                    toon.showToonTip(TTE.TIP_FIRST_VICTORY)
                    if toonId in self.helpfulToons:
                        self.toonMerits[toonId] = self.air.promotionMgr.recoverMerits(toon, self.suitsKilled, self.zoneId)
                    else:
                        self.notify.debug('toon %d not helpful, skipping merits' % toonId)

            self.d_setMembers()
            self.prepareReward()
        else:
            # Continue with the battle
            if needUpdate == 1:
                self.d_setMembers()
                if len(deadSuits) > 0 and lastActiveSuitDied == 0 or len(deadToons) > 0:
                    self.needAdjust = 1
                # Wait for input will call __requestAdjust()
            self.determineWaitState()
            
    ##### Reward state #####

    # Toons won - distribute rewards

    def enterReward(self):
        self.notify.debug('enterReward()')
        self.joinable = False
        self.runable = False
        self.resetPlayerResponses()
        self.startRewardTimer()

    def startRewardTimer(self):
        # Set an upper timeout for the reward movie.  If no toons
        # report back by this time, call it done anyway.
        self.timer.startCallback(REWARD_TIMEOUT, self.serverRewardDone)

    def exitReward(self):
        pass
        
    ##### Resume state #####

    # Any remaining suits resume their assignment or fly away

    def enterResume(self):
        self.notify.debug('enterResume()')
        self.joinable = False
        self.runable = False
        DistributedBattleBaseAI.enterResume(self)
        if self.finishCallback:
            self.finishCallback(self.zoneId)
        self.battleMgr.destroy(self)
