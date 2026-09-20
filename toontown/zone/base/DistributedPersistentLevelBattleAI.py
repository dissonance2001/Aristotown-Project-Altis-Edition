from toontown.battle.distributed.DistributedBattleBaseAI import DistributedBattleBaseAI
from toontown.battle.BattleBase import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from toontown.ai.ToontownAIRepository import ToontownAIRepository


@DirectNotifyCategory()
class DistributedPersistentLevelBattleAI(DistributedBattleBaseAI):
    """
    DistributedPersistentLevelBattleAI(DistributedBattleAI)
    """
    defaultTransitions = DistributedBattleBaseAI.defaultTransitions.copy()

    def __init__(self, air, battleMgr, pos, suit, toonId, zoneId, level, battleCellId,
                 roundCallback=None, finishCallback=None, maxSuits=4):
        """
        :type air: ToontownAIRepository
        :type maxSuits: int
        """
        self.notify.debug("init")
        self.level = level
        self.battleCellId = battleCellId
        self.roundCallback = roundCallback
        self.suitTrack = suit.dna.dept
        self.battleMgr = battleMgr
        self.pos = pos

        super().__init__(air, zoneId, finishCallback, maxSuits)

        # Store the initial position of the suit when contact occurred
        self.initialSuitPos = suit.getConfrontPosHpr()[0]
        # CCC for now use the suit position as the toonposition as they
        # should be fairly close anyways
        self.initialToonPos = suit.getConfrontPosHpr()[0]
        self.addSuit(suit)
        self.avId = toonId
        # self.addToon(self.avId)

        self.faceOffToon = toonId
        return

    def generate(self):
        super().generate()
        toon = simbase.air.doId2do.get(self.avId)
        if toon:
            if hasattr(self, 'doId'):
                toon.b_setBattleId(self.doId)
            else:
                toon.b_setBattleId(-1)
        self.avId = None

    def getLevelDoId(self):
        return self.level.doId

    def getBattleCellId(self):
        return self.battleCellId

    def getTaskZoneId(self):
        return self.zoneId

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
            totalHp = 0
            for suit in self.suits:
                if suit.hp > 0:
                    totalHp += suit.hp

            self.roundCallback(self.battleCellId, self.activeToons, totalHp, deadSuits)

    def resume(self, topFloor=0):
        if len(self.suits) == 0:
            avList = []
            for toonId in self.activeToons:
                toon = self.getToon(toonId)
                if toon:
                    avList.append(toon)

            self.d_setMembers()
            self.b_setState('Reward')
        else:
            if self.resumeNeedUpdate == 1:
                self.d_setMembers()
                if len(self.resumeDeadSuits) > 0 and self.resumeLastActiveSuitDied == 0 or len(
                    self.resumeDeadToons) > 0:
                    self.needAdjust = 1
            self.determineWaitState()
        self.resumeNeedUpdate = 0
        self.resumeDeadToons = []
        self.resumeDeadSuits = []
        self.resumeLastActiveSuitDied = 0

    def handleToonsWon(self, toons):
        pass

    def enterFaceOff(self):
        self.notify.debug('enterFaceOff()')
        self.joinable = True
        self.runable = False
        # From here on out DistributedBattleAI only controls DistributedSuitAI
        # DistributedBattle controls DistributedSuit
        faceOffTime = self.calcSuitMoveTime(self.pos, self.initialSuitPos) + FACEOFF_TAUNT_T + 0.7 + SERVER_BUFFER_TIME
        self.timer.startCallback(faceOffTime, self.__serverFaceOffDone)

    def __serverFaceOffDone(self):
        self.notify.debug('faceoff timed out on server')
        self.ignoreFaceOffDone = 1
        self.handleFaceOffDone()

    def exitFaceOff(self):
        self.timer.stop()
        self.resetPlayerResponses()

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
        self.notify.debug('toon: %d done facing off' % toonId)
        self.handleFaceOffDone()

    def suitRequestJoin(self, suit):
        self.notify.debug('DistributedLevelBattleAI.suitRequestJoin(%d)' % suit.getDoId())
        if suit in self.suits:
            self.notify.warning('suit %s already in this battle' % suit.getDoId())
            return 0
        return super().suitRequestJoin(suit)

    def enterReward(self):
        self.joinable = False
        self.runable = False
        self.timer.startCallback(FLOOR_REWARD_TIMEOUT, self.serverRewardDone)
        return None

    def exitReward(self):
        self.timer.stop()
        return None

    def handleFaceOffDone(self):
        for suit in self.suits:
            self.addActiveSuit(suit)
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

    def enterResume(self):
        self.notify.debug('enterResume()')
        self.joinable = False
        self.runable = False
        super().enterResume()
        if self.finishCallback:
            self.finishCallback(self.zoneId)
        self.battleMgr.destroy(self)

    def addSuit(self, suit):
        super().addSuit(suit)
        suit.setInLevelBattle(True, self.battleCellId)
