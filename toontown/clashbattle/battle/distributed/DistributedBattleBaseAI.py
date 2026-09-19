import json
import random
import time

from panda3d.core import *
from direct.distributed.ClockDelta import *
from direct.distributed.DistributedObjectAI import DistributedObjectAI
from direct.fsm import ClassicFSM, State
from toontown.utils.SafeFSM import SafeFSM
from direct.task import Task

from toontown.ai.AIBaseGlobal import *
from toontown.battle.BattleEventGlobals import BEG
from toontown.battle import BattleExperienceAI
from toontown.battle.statuses import SEE
from toontown.battle.statuses.StatusEffects import *
from toontown.inventory.registry.IOURegistry import IOURegistry
from toontown.toon.gui.ToonTipGlobals import TTE
from toontown.battle.BattleAvatar import BattleAvatar
from toontown.battle.BattleBase import *
from toontown.battle.BattleCalculatorAI import *
from toontown.battle.BattleEventGlobals import BEG
from toontown.battle.BattleEventDefinitionClasses import BattleObjectEventDefinition, SuitEventDefinition
from toontown.battle.SuitBattleGlobals import *
from toontown.battle import SuitBattleGlobals
from toontown.battle.visuals.VisualEffects import VisualEffectRemoved
from toontown.hood import ZoneUtil
from toontown.inventory.enums.ItemEnums import MaterialItemType
from toontown.modifiers import ModifierEnums
from toontown.modifiers.ModifierEnums import ModifierType
from toontown.modifiers.contentsync.ContentSyncDefinitions import SuitToContentSyncType
from toontown.notifications.notificationData.GenericTextNotification import GenericTextNotification, GenericTextId
from toontown.quest3.base.QuestReference import QuestReference
from toontown.suit import SuitHoodGlobals
from toontown.suit.SuitDNA import suitDeptFullnames
from toontown.toon.DistributedToonAI import DistributedToonAI
from toontown.toon.ToonStatsGlobals import ToonStats
from toontown.battle.BattleGlobals import *
from toontown.utils.RateLimiter import IdRateLimiter


class DistributedBattleBaseAI(DistributedObjectAI, SafeFSM, BattleBase, BattleListenerObject):
    defaultTransitions = {
        "Off": ["FaceOff", "WaitForJoin"],
        "FaceOff": ["WaitForInput", "Resume"],
        "WaitForJoin": ["WaitForInput", "Resume"],
        "WaitForInput": ["MakeMovie", "Resume"],
        "MakeMovie": ["PlayMovie", "Resume"],
        "PlayMovie": ["WaitForJoin", "WaitForInput", "Reward", "Resume"],
        "Reward": ["Resume"],
        "Resume": [],
    }

    CALCULATOR_CLASS = BattleCalculatorAI
    INTERACTIVE_CUTSCENE_DELAY = 0
    # Toon reservations run out after 60 seconds
    ReserveToonTimeout = 60

    def __init__(self, air, zoneId, finishCallback=None, maxSuits=4, bossBattle=0, tutorialFlag=0,
                 interactivePropTrackBonus=-1):
        DistributedObjectAI.__init__(self, air)
        SafeFSM.__init__(self, self.__class__.__name__)

        self.serialNum = 0

        self.zoneId = zoneId
        self.maxSuits = maxSuits
        self.bossBattle = bossBattle
        self.tutorialFlag = tutorialFlag
        self.interactivePropTrackBonus = interactivePropTrackBonus if WantInteractivePropBuffs else -1
        self.timescale = 1.0
        self.serverInputTimeout = SERVER_INPUT_TIMEOUT

        # function to call when this battle is about to be destroyed
        self.finishCallback = finishCallback

        self.avatarExitEvents = []
        self.responses = {}
        self.adjustingResponses = {}
        self.joinResponses = {}
        self.adjustingSuits = []
        self.adjustingToons = []

        # Track the number of suits that have ever joined this battle.
        self.numSuitsEver = 0

        BattleBase.__init__(self)

        # self.streetBattle = 1
        self.pos = Point3(0, 0, 0)
        self.initialSuitPos = Point3(0, 0, 0)

        self.toonExp = {}
        self.toonOrigQuests = {}
        self.toonOrigMerits = {}
        self.toonMerits = {}
        self.toonParts = {}
        self.afkToons = {}
        self.lockIns = {}
        self.avIdsWithUnattacks = set()

        self.battleCalc = self.CALCULATOR_CLASS(self, interactivePropTrackBonus)
        self.addListenerObject(self, BattleObjectEventDefinition)

        self.calculateSkillCreditMultiplier()

        self.ignoreFaceOffDone = 0
        self.needAdjust = 1
        self.movieHasBeenMade = 0
        self.movieHasPlayed = 0
        self.rewardHasPlayed = 0
        self.movieRequested = 0

        self.ignoreResponses = 0
        self.ignoreAdjustingResponses = 0

        self.taskNames = []

        self.visualEffectsExpiring = []

        self.gameoverGroupOverride = None
        self.trueSolo = True  # Becomes false when the battle has 2+ player toons
        self.suitAttackAIExceptions = []
        self.isLevelBattle = False

        # Maintain a list of all the suits killed in the battle
        # for the quest system and the suit page
        self.suitsKilled = []
        self.suitsKilledThisBattle = []
        self.suitsKilledPerFloor = []

        # Maintain a list of all the suits encountered in the battle
        # for the suit page
        self.suitsEncountered = []
        # Lists of player and non-player toons in battle
        self.playerToons = []
        self.npcToons = []
        # These will help
        self.newToons = []
        self.newSuits = []

        self.joinable = False
        self.runable = False
        self.surrenderRequests = {}

        self.adjustFsm = ClassicFSM.ClassicFSM('Adjust', [
            State.State('Adjusting', self.enterAdjusting, self.exitAdjusting, ['NotAdjusting', 'Adjusting']),
            State.State('NotAdjusting', self.enterNotAdjusting, self.exitNotAdjusting, ['Adjusting'])], 'NotAdjusting',
                                               'NotAdjusting')
        self.adjustFsm.enterInitialState()
        self.request("Off")
        self.startTime = globalClock.getRealTime()
        self.realStartTime = int(time.time())
        self.adjustingTimer = Timer()

        self.__suitsWantPendingDict = {}

        # Flag for the interactive cutscene.
        self.interactiveCutsceneQueued = False

        # Store reserved avids and their "timeout" timestamps
        # After a minute has passed, they will no longer be considered reserved
        self.__reservedAvIds = {}
        # Some groups may become "attached" to this battle once a toon encounters their desired cog
        # If the battle dies, we will force disband the related groups here.
        self.attachedGroupAvIds = []

        self.gagupExtendRounds = 0

        self.gagOrder = BattleGlobals.GAG_TRACK_ORDER[:]

        # Rate limit certain actions
        self.ratelimiter = IdRateLimiter(3, 1)

        self.npcAttacks = []
    
    def getBattleListener(self):
        return self.battleCalc.getBattleListener()

    def calculateSkillCreditMultiplier(self, mult = 1):
        """
        Calculates gag skill multiplier
        """
        # If CogHQ
        if self.zoneId and ZoneUtil.isCogHQZone(self.zoneId):
            mult += getCogHQMultiplier() - 1

        # If inside building, floor can equal 0 and 0 is falsy so
        if hasattr(self, "maxFloor") and self.maxFloor is not None:
            mult += getBuildingCreditMultiplier(self.maxFloor)

        # If boss battle
        elif hasattr(self, "battleNumber") and self.battleNumber:
            mult += (getBossBattleCreditMultiplier(self.battleNumber))

        # If facility
        elif hasattr(self, "level") and self.level:
            mult += (self.level.getBattleCreditMultiplier() - 1)

        # bosses and cog buildings not effected by invasion
        elif SuitHoodGlobals.isZoneInvasionableAI(self.zoneId):
            if (ZoneUtil.getBranchZone(self.zoneId) - ZoneUtil.getHoodId(self.zoneId)) < 500:
                mult += (getInvasionMultiplier() - 1)

        self.battleCalc.setSkillCreditMultiplier(mult)

    def checkAllToonsAfk(self):
        # We need to make sure that we don't afk force all toons, otherwise they would be softlocked til sadness.
        numAfkToons = len([toon for toon in self.activeToons if self.isToonAfk(toon)])
        if numAfkToons == len(self.activeToons):
            self.notify.debug(f'All toons ({self.afkToons}) are afk.... Resetting afk values.')
            for toon in list(self.afkToons.keys()):
                self.afkToons[toon] = 0
            return True
        return False

    def checkAfkAttacks(self):
        # Make sure not all of our toons are afk.
        if self.checkAllToonsAfk():
            return

        # If other checks passed and there are afk toons, make them force pass.
        for toonId in self.activeToons:
            if self.afkToons[toonId] >= AV_AFK_ROUNDS:
                toon = self.getToon(toonId)
                if not toon:
                    self.notify.warning(f'toon {toonId} was afk and in our activeToons but doesnt exist???')
                    continue
                self.battleCalc.createToonAttack(AttackEnum.TOON_PASS, toon)
                self.responses[toonId] += 1
                self.lockIns[toonId] = 1

        self.sendAttacksAndLockInsToClient()

    def requestDelete(self):
        if hasattr(self, 'fsm'):
            # We want to make sure the battle is no longer active once
            # we start deleting it.  If we don't do this, it may
            # continue to fire off tasks until the delete message
            # comes back from the server.
            self.request('Off')
        self.__removeTaskName(self.uniqueName('make-movie'))
        DistributedObjectAI.requestDelete(self)

    def delete(self):
        self.notify.debug('deleting battle')
        self.ignoreAll()
        self.__removeAllTasks()
        SafeFSM.cleanup(self)
        del self.adjustFsm
        self.__cleanupJoinResponses()
        self.timer.stop()
        del self.timer
        self.adjustingTimer.stop()
        del self.adjustingTimer
        self.battleCalc.cleanup()
        del self.battleCalc
        for suit in self.suits:
            del suit.battleTrap
        del self.suitAttackAIExceptions
        del self.finishCallback
        del self.newToons
        del self.newSuits
        del self.playerToons
        del self.npcToons
        self.__suitsWantPendingDict = {}
        self.__reservedAvIds = {}
        self.attachedGroupAvIds = []
        for av in self.toons + self.suits:
            if isinstance(av, int):
                av = simbase.air.doId2do.get(av)
                if av is None:
                    continue
            av.cleanupBattle()
            av.setBattleState(BattleStateEnum.INACTIVE)
            av.sendStatusEffects()
            # Ensure that they don't have a battle id.
            if isinstance(av, DistributedToonAI):
                av.b_setBattleId(0)

        DistributedObjectAI.delete(self)

    def pause(self):
        self.timer.stop()
        self.adjustingTimer.stop()

    def unpause(self):
        self.timer.resume()
        self.adjustingTimer.resume()

    def beginBarrier(self, name, avIds, timeout, callback):
        # Don't apply barriers to npc toons
        playerAvIds = [avId for avId in avIds if avId not in self.npcToons]
        DistributedObjectAI.beginBarrier(self, name, playerAvIds, timeout, callback)

    def abortBattle(self):

        """ Call this function to stop the battle in the middle, no
        matter what; the toons are sent back to the playground and the
        suits will fly away (or do whatever is appropriate for this
        kind of battle).  This is normally called only in response to
        a magic word. """

        self.notify.debug('%s.abortBattle() called.' % self.doId)

        toonsCopy = self.toons[:]
        for toonId in toonsCopy:
            self.removeToon(toonId)

        # Of course, the last toon is gone now.
        self.d_setMembers()

        self.b_setState('Resume')
        self.__removeAllTasks()
        self.timer.stop()
        self.adjustingTimer.stop()

    def __removeSuit(self, suit: DistributedSuitBaseAI):
        self.notify.debug('__removeSuit(%d)' % suit.doId)
        self.suits.remove(suit)
        self.suitGone = 1
        del suit.battleTrap
        self.battleCalc.removeListenerObject(suit)
        suit.cleanupBattle()
        suit.setBattleState(BattleStateEnum.INACTIVE)
        suit.sendStatusEffects()

    def findSuit(self, id):
        for s in self.suits:
            if s.doId == id:
                return s
        return None

    def __removeTaskName(self, name):
        if self.taskNames.count(name):
            self.taskNames.remove(name)
            self.notify.debug('removeTaskName() - %s' % name)
            taskMgr.remove(name)

    def __removeAllTasks(self):
        for n in self.taskNames:
            self.notify.debug('removeAllTasks() - %s' % n)
            taskMgr.remove(n)

        self.taskNames = []

    def __removeToonTasks(self, toonId):
        name = self.taskName('running-toon-%d' % toonId)
        self.__removeTaskName(name)
        name = self.taskName('to-pending-av-%d' % toonId)
        self.__removeTaskName(name)

    def addExpiredVisualEffect(self, visualEffect):
        """If a visual effect has expired, it gets added to this list."""
        avId = visualEffect.av.doId
        ver = VisualEffectRemoved(avId, visualEffect.effectEnum)
        self.visualEffectsExpiring.append(ver)

    def informVisualEffectsEnding(self):
        """Let the client battle know what visual effects end this round."""
        deadAvIds = []

        for battleAvatar in self.activeSuits + AttackAI.getObjectsFromIds(self.activeToons):
            # Go through every single battle avatar,
            battleAvatar: BattleAvatar

            # and attempt to kill each of their visual effects.
            for visualEffect in battleAvatar.getVisualEffects():
                visualEffect.requestDestroy()

            # If this battle avatar is dead, put it in the list.
            if battleAvatar.getHp() <= 0:
                avId = battleAvatar.doId
                deadAvIds.append(avId)

        # In addition, we need to NOT send any visual effects on Dead Suits.
        for expiringVisualEffect in self.visualEffectsExpiring[:]:
            if expiringVisualEffect.avId in deadAvIds:
                self.visualEffectsExpiring.remove(expiringVisualEffect)

        # OK, we're safe to send the update out now.
        self.sendUpdate('informVisualEffectsEnding', [VisualEffectRemoved.toStructList(self.visualEffectsExpiring)])
        self.visualEffectsExpiring = []

    # These are dummy getters for non-level battles. See toon.dc for
    # more info.
    def getLevelDoId(self):
        return 0

    def getBattleCellId(self):
        return 0

    # setPosition()

    def getPosition(self):
        self.notify.debug('getPosition() - %s' % self.pos)
        return [self.pos[0], self.pos[1], self.pos[2]]

    # setInitialSuitPos()

    def getInitialSuitPos(self):
        p = []
        p.append(self.initialSuitPos[0])
        p.append(self.initialSuitPos[1])
        p.append(self.initialSuitPos[2])
        return p

    # setBossBattle

    def setBossBattle(self, bossBattle):
        # Call this BEFORE generate
        self.bossBattle = bossBattle

    def getBossBattle(self):
        return self.bossBattle

    # setState()

    def b_setState(self, state, demand=False):
        self.notify.debug('network:setState(%s)' % state)
        if self.getCurrentOrNextState() == "Resume":
            # Don't allow any new state changes as we're in the final
            # state of the battle.
            return
        stime = globalClock.getRealTime() + SERVER_BUFFER_TIME
        self.getBattleListener().sendEvent(BEG.EVENT_BATTLE_STATE, [state])
        self.sendUpdate('setState', [state, globalClockDelta.localToNetworkTime(stime)])
        self.setState(state, demand)

    def setState(self, state: str, demand: bool = False):
        if demand:
            # If the demand flag is passed, it means that something
            # unexpected has happened, and we want to force a new
            # state to occur. (most likely 'Resume' in this case)
            return self.forceTransition(state)
        self.request(state)

    def getState(self):
        return [self.getCurrentOrNextState(), globalClockDelta.getRealNetworkTime()]

    # setMembers()

    def d_setMembers(self):
        self.notify.debug('network:setMembers()')
        self.sendUpdate('setMembers', self.getMembers())

    def getMembers(self):
        suitTraps = ''
        suits = []
        for i, s in enumerate(self.suits):
            if s.battleTrap == NO_TRAP:
                suitTraps += '9'
            else:
                suitTraps += str(s.battleTrap)

            suits.append((s.doId, s.getBattleState(), i))

        toons = []
        for i, t in enumerate(self.toons):
            toon = self.air.doId2do.get(t)
            if not toon:
                continue

            toons.append((t, toon.getBattleState(), i))

        return [suits, suitTraps, toons, globalClockDelta.getRealNetworkTime()]

    # adjust()

    def d_adjust(self):
        self.notify.debug('network:adjust()')
        self.sendUpdate('adjust', [globalClockDelta.getRealNetworkTime()])

    # setInteractivePropTrackBonus

    def getInteractivePropTrackBonus(self):
        return self.interactivePropTrackBonus

    # setZoneId

    def getZoneId(self):
        """
        :returns: the current zone ID.
        :rtype: int
        """
        return self.zoneId

    def getTaskZoneId(self):
        # This function is here to allow subclasses override the zoneId
        # that's used to determine task progress.
        return self.zoneId

    # setMovie

    def d_setMovie(self):
        self.notify.debug('network:setMovie()')
        self.suitAttackAIExceptions = []
        self.sendUpdate('setMovie', self.getMovie())
        # This seems as good a place as any to update the suit encountered array
        # (we have to make sure the adjusting is all finished and activeToons us updated)
        self.__updateEncounteredCogs()

    def getMovie(self):
        suitIds = [suit.getDoId() for suit in self.activeSuits]

        p = [self.movieHasBeenMade, self.activeToons, suitIds]

        attacks = []

        for attack in self.battleCalc.getAttackOrder():
            # The attack's index was set, meaning that
            # it occurred without a hitch and should be
            # displayed on the client.
            if attack.attackIndex != -1:
                attacks.append(attack)

        attacks = AttackAI.toStructList(attacks)

        p.append(attacks)
        p.append(self.battleCalc.rounds)
        return p

    def sendAttacksAndLockInsToClient(self):
        self.d_setChosenToonAttacks()
        self.d_setLockIns()

    # setChosenToonAttacks
    def d_setChosenToonAttacks(self):
        self.notify.debug('network:setChosenToonAttacks()')
        self.sendUpdate('setChosenToonAttacks', self.getChosenToonAttacks())

    def getChosenToonAttacks(self):
        ids = []
        tracks = []
        levels = []
        targets = []
        for t in self.activeToons:
            if t in self.battleCalc.toonAttacks:
                ta = self.battleCalc.toonAttacks[t]
            else:
                ta = self.battleCalc.createToonAttack(AttackEnum.TOON_NO_ATTACK, self.getToon(t))
            ids.append(t)
            tracks.append(ta.attackType)
            levels.append(ta.level)
            targets.append(ta.target)

        return [ids, tracks, levels, targets]

    # setLockIns
    def d_setLockIns(self):
        self.notify.debug('network:setLockIns()')
        self.sendUpdate('setLockIns', self.getLockIns())

    def getLockIns(self):
        ids = []
        lockIns = []
        for t in self.activeToons:
            ids.append(t)
            lockIns.append(self.lockIns.get(t, False))

        return [ids, lockIns]

    # setBattleExperience

    def d_setBattleExperience(self, battleExperience):
        self.notify.debug('network:setBattleExperience()')
        self.sendUpdate('setBattleExperience', battleExperience)

    def getBattleExperience(self):
        return BattleExperienceAI.getBattleExperience(
            4,
            self.activeToons,
            self.toonExp,
            self.battleCalc.toonSkillPtsGained,
            self.toonOrigQuests,
            self.toonOrigMerits,
            self.toonMerits,
            self.toonParts,
        )

    def isToonAfk(self, toon):
        return toon in self.afkToons and self.afkToons[toon] >= AV_AFK_ROUNDS

    def d_setAfkToons(self):
        # Before we send over the afk toons, make sure not all of ours are afk.
        self.checkAllToonsAfk()
        self.sendUpdate('setAfkToons', [[toon for toon in self.activeToons if self.isToonAfk(toon)]])

    def updateBattleAvatars(self):
        for avatar in self.activeSuits + AttackAI.getObjectsFromIds(self.activeToons):
            # Get info for each of our avatars and send it to the client.
            avatar.sendStatusEffects()

    def d_uniteUsed(self, avId):
        self.sendUpdate('uniteUsed', [avId])

    # Add suit
    def addSuit(self, suit: DistributedSuitBaseAI):
        self.notify.debug('addSuit(%d)' % suit.doId)
        self.newSuits.append(suit)

        # Get a list of the indices of the beginning/middle/end desiring suits.
        beginningSuits = []
        middleSuits = []
        endSuits = []
        for i, s in enumerate(self.suits):
            priority = s.getBattleOrderPriority()
            if priority == BOP.BEGINNING:
                beginningSuits.append(i)
            elif priority == BOP.MIDDLE:
                middleSuits.append(i)
            elif priority == BOP.END:
                endSuits.append(i)

        # If the suit wants to be in the middle, force them into
        # the middle.
        priority = suit.getBattleOrderPriority()
        if priority == BOP.MIDDLE:
            insertIndex = clampScalar((len(self.suits) // 2) + len(beginningSuits) - len(endSuits), 0, len(self.suits))
            self.suits.insert(insertIndex, suit)
        else:
            if middleSuits and priority not in (BOP.BEGINNING, BOP.END):
                distA = middleSuits[0]
                distB = len(self.suits) - middleSuits[-1] - 1
                if distA < distB:
                    self.suits.insert(len(beginningSuits), suit)
                else:
                    self.suits.insert(len(self.suits) - len(endSuits), suit)
            else:
                if beginningSuits and priority != BOP.BEGINNING:
                    self.suits.insert(len(beginningSuits), suit)
                elif endSuits and priority != BOP.END:
                    self.suits.insert(len(self.suits) - len(endSuits), suit)
                elif priority == BOP.BEGINNING:
                    self.suits.insert(0, suit)
                else:
                    self.suits.append(suit)

        # Apply any starting status effects on the suit.
        self.addBattleAvatar(suit)
        self.battleCalc.addListenerObject(suit, SuitEventDefinition)
        suit.applyStartingStatusEffects()

        # Initialize the suit trap
        suit.battleTrap = NO_TRAP
        self.numSuitsEver += 1

        if suit.isElite:
            # Executive Cog Tip
            for avId in self.playerToons:
                toon = self.getToon(avId)
                if toon:
                    toon.showToonTip(TTE.TIP_EXE_COG)

        # Content Sync, if necessary.
        syncType = SuitToContentSyncType.get(suit.dna.name)
        if syncType:
            self.battleCalc.createEnvironmental(
                environmentalType=ENV_ENUM.CONTENT_SYNC,
                contentSyncType=syncType,
            )

    def __joinSuit(self, suit: DistributedSuitBaseAI):
        # Calculate the time it will take for the suit to go from
        # its current position to its pending position in the battle
        # and create a task to call a function when that time has
        # passed

        # Building battles can have 3 pending suits
        suit.setBattleState(BattleStateEnum.JOINING)
        toPendingTime = MAX_JOIN_T + SERVER_BUFFER_TIME
        taskName = self.taskName('to-pending-av-%d' % suit.doId)
        self.__addJoinResponse(suit.doId, taskName)
        self.taskNames.append(taskName)
        taskMgr.doMethodLater(toPendingTime, self.__serverJoinDone, taskName, extraArgs=(suit.doId, taskName))

    def joinSuitNoPending(self, suit: DistributedSuitBaseAI):
        suit.setBattleState(BattleStateEnum.JOINING_NOT_PENDING)
        toPendingTime = MAX_JOIN_T + SERVER_BUFFER_TIME
        taskName = self.taskName('to-pending-av-%d' % suit.doId)
        self.__suitsWantPendingDict[suit.doId] = False
        self.__addJoinResponse(suit.doId, taskName)
        self.taskNames.append(taskName)
        taskMgr.doMethodLater(toPendingTime, self.__serverJoinDone, taskName, extraArgs=(suit.doId, taskName))

    def __serverJoinDone(self, avId, taskName):
        self.notify.debug('join for av: %d timed out on server' % avId)
        self.__removeTaskName(taskName)
        self.__makeAvPending(avId, makePending=self.__suitsWantPendingDict.get(avId, True))
        return Task.done

    def __makeAvPending(self, avId, makePending: bool = True):
        self.notify.debug('__makeAvPending(%d)' % avId)
        av = simbase.air.getDo(avId)
        if av.doId in self.__suitsWantPendingDict:
            del self.__suitsWantPendingDict[av.doId]

        if not makePending and av and isinstance(av, DistributedSuitBaseAI):
            for suit in self.suits:
                suit: DistributedSuitBaseAI
                if suit.getBattleState() == BattleStateEnum.JOINING_NOT_PENDING:
                    self.addActiveSuit(suit)
            self.__removeJoinResponse(avId)
            self.__removeTaskName(self.taskName('to-pending-av-%d' % avId))

            self.d_setMembers()
            self.needAdjust = 1
            self.__requestAdjust()
            return

        self.__removeJoinResponse(avId)
        self.__removeTaskName(self.taskName('to-pending-av-%d' % avId))
        toon = self.getToon(avId)
        if toon:
            toon.setBattleState(BattleStateEnum.PENDING)
        else:
            suit = self.findSuit(avId)
            if suit is not None:
                suit: DistributedSuitBaseAI
                if not suit.isEmpty():
                    if suit.getBattleState != BattleStateEnum.JOINING:
                        self.notify.warning(f'__makeAvPending({avId}) in zone: {self.zoneId}, ' \
                                            f'battleState: {suit.getBattleState()}')
                    suit.setBattleState(BattleStateEnum.PENDING)
            else:
                self.notify.warning('makeAvPending() %d not in toons or suits' % avId)
                return
        self.d_setMembers()
        self.needAdjust = 1
        self.__requestAdjust()

    def suitRequestJoin(self, suit):
        self.notify.debug('suitRequestJoin(%d)' % suit.getDoId())
        # Make sure we're not trying to add a suit that's
        # already in this battle
        if self.suitCanJoin():
            self.addSuit(suit)
            self.__joinSuit(suit)
            self.d_setMembers()
            suit.prepareToJoinBattle()
            return 1
        else:
            self.notify.warning('suitRequestJoin() - not joinable - joinable state: %s max suits: %d' % (self.isJoinable(), self.maxSuits))
            return 0

    # Add/Remove toon

    def addToon(self, avId):
        self.notify.debug('addToon(%d)' % avId)
        toon = self.getToon(avId)
        if toon is None:
            return 0

        self.addBattleAvatar(toon)

        # Make sure the playground (or estate) toon-up task isn't
        # still running on this Toon.  It shouldn't be, but if it is
        # we'll get very mysterious effects during the battle movie.
        toon.stopToonUp()

        # Prepare to handle an unexpected exit by the avatar
        event = simbase.air.getAvatarExitEvent(avId)
        self.avatarExitEvents.append(event)
        self.accept(event, self.handleUnexpectedExit, extraArgs=[avId])

        # Also handle avatars that manage to escape to the safezone
        # somehow.
        event = 'inSafezone-%s' % avId
        self.avatarExitEvents.append(event)
        self.accept(event, self.__handleSuddenExit, extraArgs=[avId, 0])

        self.newToons.append(avId)
        self.playerToons.append(avId)
        self.toons.append(avId)

        if len(self.playerToons) >= 2 and self.trueSolo:
            self.trueSolo = False

        if hasattr(self, 'doId'):
            toon.b_setBattleId(self.doId)
        else:
            toon.b_setBattleId(-1)
        messageToonAdded = 'Battle adding toon %s' % avId
        messenger.send(messageToonAdded, [avId])

        # Check group stuff
        self.handleToonAddedGroupInfo(avId)

        # First Battle Tip
        toon.showToonTip(TTE.TIP_FIRST_BATTLE)
        # Executive Cog Tip
        for suit in self.suits:
            if suit.isElite:
                toon.showToonTip(TTE.TIP_EXE_COG)
                break

        if self.getCurrentOrNextState() == 'PlayMovie':
            self.responses[avId] = 1
        else:
            self.responses[avId] = 0
        self.adjustingResponses[avId] = 0
        self.afkToons[avId] = 0
        self.lockIns[avId] = 0

        # Initialize experience per track
        if avId not in self.toonExp:
            p = []
            for t, _ in enumerate(Tracks):
                p.append(toon.getExperience()[t])

            self.toonExp[avId] = p

        # Initialize original merits
        if avId not in self.toonOrigMerits:
            self.toonOrigMerits[avId] = toon.cogMerits[:]

        # Initialize merits earned
        if avId not in self.toonMerits:
            self.toonMerits[avId] = [0, 0, 0, 0, 0]

        # Initialize quests
        if avId not in self.toonOrigQuests:
            flattenedQuests = []
            for questReference in toon.getVisibleQuests():
                questReference: QuestReference
                flattenedQuests.append(questReference.toStruct())

            self.toonOrigQuests[avId] = flattenedQuests

        return 1

    def handleZoneChange(self, avId, newZone, oldZone):
        return False

    def handleToonAddedGroupInfo(self, avId):
        toonGroup = self.air.groupManager.getGroupOfAvId(avId)
        # They have a group, and its the type we're looking for. Yippee!!!
        if toonGroup and toonGroup.groupDefinition.suitName is not None:
            suitNames = [suit.dna.name for suit in self.suits]
            # The suit our group wants is in this battle and we haven't told people yet
            if toonGroup.groupDefinition.suitName in suitNames and not toonGroup.announcedBattle:
                # Go tell people!!!
                self.air.groupManager.announceGroupMemberEncounteredSuit(avId)
                # Mark our group members as reserved
                # More or less, this should be safe to do because of the checks inside of self.toonCanJoin()
                for toon in toonGroup.avatarList:
                    # Checking self.reservedAvIds here, not self.__reservedAvIds, because we
                    # want to include if their timeout has ran out as well
                    if toon.avId != avId and toon.avId not in self.reservedAvIds and not toon.reserved:
                        self.__reservedAvIds[toon.avId] = time.time() + self.ReserveToonTimeout
                self.attachedGroupAvIds.append(avId)

            # Now we need to check if all of our members of the group have entered the battle.
            if all([groupMember.avId in self.toons for groupMember in toonGroup.avatarList]):
                # All toons are in the battle, we can go ahead and disband the group and clear us from reserved Avs.
                messenger.send('GroupManager-DisbandToonGroup', [toonGroup.owner])
                for groupMember in toonGroup.avatarList:
                    toon = self.air.doId2do.get(groupMember.avId)
                    if toon:
                        toon.addNotification(GenericTextNotification(
                            textId=GenericTextId.BattleFullGroupDisbanded,
                            title='Group Disbanded',
                            subtitle='Your Group has been disbanded because your Group\'s battle has filled.',
                        ))
                    # Remove all group members from listed reserves
                    if groupMember.avId in self.__reservedAvIds:
                        del self.__reservedAvIds[groupMember.avId]
                    # Remove original group member from attached group ids so that we don't double disband
                    if groupMember.avId in self.attachedGroupAvIds:
                        self.attachedGroupAvIds.remove(groupMember.avId)

    @property
    def reservedAvIds(self):
        # All reserved avids who have not passed the timeout threshold
        return [avId for avId, timeout in self.__reservedAvIds.items() if time.time() < timeout]

    def addNPCToon(self, avId):
        self.notify.debug('addToon(%d)' % avId)
        toon = self.getToon(avId)
        if toon is None:
            return 0

        self.addBattleAvatar(toon)

        self.newToons.append(avId)
        self.npcToons.append(avId)
        self.toons.append(avId)

        if hasattr(self, 'doId'):
            toon.b_setBattleId(self.doId)
        else:
            toon.b_setBattleId(-1)
        messageToonAdded = 'Battle adding toon %s' % avId
        messenger.send(messageToonAdded, [avId])

        if self.getCurrentOrNextState() == 'PlayMovie':
            self.responses[avId] = 1
        else:
            self.responses[avId] = 0
        self.adjustingResponses[avId] = 1
        self.afkToons[avId] = 0
        self.lockIns[avId] = 0

        return 1

    def addBattleAvatar(self, av):
        if isinstance(av, DistributedToonBaseAI):
            av.resetBattle()
            av.setBattle(self)
            av.setBattleListener(self.battleCalc.battleListener)
            event = BEG.EVENT_TOON_ADDED_TO_BATTLE
        elif isinstance(av, DistributedSuitBaseAI):
            av.resetBattle()
            av.setBattle(self)
            av.setBattleListener(self.battleCalc.battleListener)
            event = BEG.EVENT_SUIT_ADDED_TO_BATTLE
        else:
            return

        self.battleCalc.sendEvent(event, [av])

    def __joinToon(self, avId, pos):
        # Calculate the time it will take for the toon to go from
        # its current position to its position in the battle and
        # create a task to call a function when that time has passed
        toon = self.air.doId2do.get(avId)
        if toon:
            toon.setBattleState(BattleStateEnum.JOINING)
        toPendingTime = MAX_JOIN_T + SERVER_BUFFER_TIME
        taskName = self.taskName('to-pending-av-%d' % avId)
        self.__addJoinResponse(avId, taskName, toon=1)
        taskMgr.doMethodLater(toPendingTime, self.__serverJoinDone, taskName, extraArgs=(avId, taskName))
        self.taskNames.append(taskName)

    def __updateEncounteredCogs(self):
        # If there is a new toon, add all the active suits to the encounter list.
        for toon in self.activeToons:
            if toon in self.newToons:
                # Add any suits present to the suits encountered list
                for suit in self.activeSuits:
                    if hasattr(suit, 'dna'):
                        self.suitsEncountered.append({'type': suit.dna.name,
                                                      # Put a copy of active toons in the dict
                                                      # Only they get credit for seeing this suit
                                                      'activeToons': self.activeToons[:]})
                    else:
                        self.notify.warning('Suit has no DNA in zone %s: toons involved = %s' % (self.zoneId, self.activeToons))
                        # fail hard
                        return

                self.newToons.remove(toon)

        # If there is a new suit, add it to all active toons encounter list.
        for suit in self.activeSuits:
            if suit in self.newSuits:
                if hasattr(suit, 'dna'):
                    # add any new suits to all active toons encounter list
                    self.suitsEncountered.append({'type': suit.dna.name,
                                                  # Put a copy of active toons in the dict
                                                  # Only they get credit for seeing this suit
                                                  'activeToons': self.activeToons[:]})
                else:
                    self.notify.warning('Suit has no DNA in zone %s: toons involved = %s' % (self.zoneId, self.activeToons))
                    # fail hard
                    return
                self.newSuits.remove(suit)

    def __makeToonRun(self, toonId, updateAttacks):
        self.notify.info("LogStats ToonRanFromBattle toonid %s" % toonId)
        # Gotta remove their battle avatar NOW!
        # Otherwise, the battle will adjust while their battle av is still present,
        # and that causes BUGS with VISUAL EFFECTS!
        toon = simbase.air.doId2do.get(toonId)
        if toon:
            toon.cleanupBattle()
            toon.sendStatusEffects()
            toon.setBattleState(BattleStateEnum.RUNNING)

        # We want adjusting to occur
        self.toonGone = 1
        taskName = self.taskName('running-toon-%d' % toonId)
        taskMgr.doMethodLater(TOON_RUN_T, self.__serverRunDone, taskName, extraArgs=(toonId, updateAttacks, taskName))
        self.taskNames.append(taskName)

    def __serverRunDone(self, toonId, updateAttacks, taskName):
        self.notify.debug('run for toon: %d timed out on server' % toonId)
        self.__removeTaskName(taskName)
        self.removeToon(toonId, run=True)
        self.d_setMembers()
        if len(self.toons) == 0:
            self.notify.debug('last toon is gone - battle is finished')
            self.b_setState('Resume')
        else:
            if updateAttacks == 1:
                self.sendAttacksAndLockInsToClient()
            self.needAdjust = 1
            self.__requestAdjust()
        return Task.done

    def __requestAdjust(self):
        """ Only the server can initiate an adjust
        """
        cstate = self.getCurrentOrNextState()
        if cstate not in ('WaitForInput', 'WaitForJoin'):
            self.notify.debug('requestAdjust() - in state: %s' % cstate)
            return

        # Update our battle avatars any time an adjustment is requested by the server.
        self.updateBattleAvatars()

        if self.adjustFsm.getCurrentState().getName() != 'NotAdjusting':
            self.notify.debug('requestAdjust() - already adjusting')
            return
        if self.needAdjust != 1:
            self.notify.debug('requestAdjust() - dont need to')
            return

        self.d_adjust()

        self.adjustingSuits = []
        for s in self.pendingSuits:
            self.adjustingSuits.append(s)

        self.adjustingToons = []
        for t in self.pendingToons:
            self.adjustingToons.append(t)

        self.adjustFsm.request('Adjusting')

    def handleUnexpectedExit(self, avId):
        # TODO: fixme
        # disconnectCode = self.air.getAvatarDisconnectReason(avId)
        disconnectCode = "placeHolder dc code, need self.air.getAvatarDisconnectReason(avId)"
        self.notify.warning('toon: %d exited unexpectedly, reason %s' % (avId, disconnectCode))

        # We consider the user to have disconnected unfairly if he
        # exited because of a window closure.  For any other reason,
        # we give him the benefit of a doubt (maybe an internet
        # hiccup, maybe a client crash).

        # userAborted = disconnectCode == ToontownGlobals.DisconnectCloseWindow
        # TODO: fixme
        userAborted = False

        self.__handleSuddenExit(avId, userAborted)

    def __handleSuddenExit(self, avId, userAborted):
        self.notify.info("LogStats ToonSuddenExitBattle toonid %s" % avId)
        self.removeToon(avId, userAborted=userAborted)
        # See if the last toon is gone
        self.d_setMembers()
        if len(self.toons) == 0:
            self.notify.debug('last toon is gone - battle is finished')
            self.__removeAllTasks()
            self.timer.stop()
            self.adjustingTimer.stop()
            self.b_setState('Resume', demand=True)
        else:
            self.needAdjust = 1
            self.__requestAdjust()

    def removeToon(self, toonId, userAborted=0, run=False):
        """Remove a toon before victory is achieved (run away, get sad,
        disconnect)"""
        self.notify.debug('__removeToon(%d)' % toonId)
        if self.toons.count(toonId) == 0:
            return

        updateAttacks = 0
        if self.getCurrentOrNextState() == "WaitForInput":
            # See if anyone else is trying to heal/IOU the leaving toon
            for attack in list(self.battleCalc.toonAttacks.values()):
                track = attack.attackType
                level = attack.level
                # Revoke their attack if their target id is a match
                # or if it's a group heal and the invoker is now alone.
                if (
                    attack.target == toonId
                    or (track == AttackEnum.TOON_HEAL
                        and attackAffectsGroup(track, level)
                        and len(self.activeToons) < 2)
                ):
                    invoker = attack.invoker
                    self.battleCalc.createToonAttack(AttackEnum.TOON_UN_ATTACK, invoker)
                    self.responses[invoker.doId] = 0
                    updateAttacks = 1

        if updateAttacks == 1:
            self.sendAttacksAndLockInsToClient()

        # Inform the battleCalculator that the toon is leaving the battle
        # WARNING: this will delete any accumulated experience in the
        # calc's toonSkillPtsGained dict; for parts of the game that
        # accumulate experience over multiple battles, this will destroy
        # the toon's accumulated experience. It seems like a safe assumption
        # that running away, getting sad, or disconnecting should void a
        # toon's accumulated experience.
        self.battleCalc.toonLeftBattle(toonId)
        self.__removeToonTasks(toonId)
        self.toons.remove(toonId)
        if toonId in self.playerToons:
            self.playerToons.remove(toonId)
        elif toonId in self.npcToons:
            self.npcToons.remove(toonId)
        self.toonGone = 1

        # Trigger all the necessary client responses
        self.__removeResponse(toonId)
        self.__removeLockIn(toonId)
        self.__removeAdjustingResponse(toonId)
        self.__removeJoinResponses(toonId)

        # Fully refresh surrender requests if someone is gone
        self.clearSurrenderRequests()

        # Ignore future avatar exit events
        event = simbase.air.getAvatarExitEvent(toonId)
        if event in self.avatarExitEvents:
            self.avatarExitEvents.remove(event)
        self.ignore(event)

        # And also stop listening for "avatar escaped" events.
        event = 'inSafezone-%s' % toonId
        if event in self.avatarExitEvents:
            self.avatarExitEvents.remove(event)
        self.ignore(event)

        toon = simbase.air.doId2do.get(toonId)
        if not toon:
            return

        self.ignore(toon.getZoneChangeEvent())

        messageToonReleased = 'Battle releasing toon %s' % toon.doId
        messenger.send(messageToonReleased, [toon.doId])

        # The toon exited the battle, but he may still be in the
        # game.  In case he is, make sure he knows his current HP
        # and inventory.  (He might have crashed out and left the
        # game, but that's ok too.)
        toon.hpOwnedByBattle = 0
        toon.hpAdjustBattle = 0
        toon.d_setHp(toon.hp)
        toon.d_setInventory(toon.inventory.makeNetString())
        # Tell the cog page manager about the cogs this toon encountered
        self.air.cogPageManager.toonEncounteredCogs(toonId, self.suitsEncountered, self.getTaskZoneId())
        self.notify.debug('Sending gameover string, toon perished')
        self.sendUpdateGameover(toonId, run)

        if toon.getBattleState() == BattleStateEnum.ACTIVE:
            # Update suitAttack HP indices, which need to match activeToon list.
            for attack in self.battleCalc.getAttackOrder():
                for result in attack.results:
                    if result.avId == toonId:
                        attack.results.remove(result)

        toon.cleanupBattle()
        toon.setBattleState(BattleStateEnum.INACTIVE)
        toon.sendStatusEffects()
        toon.b_setBattleId(0)

    def getToon(self, toonId):
        if toonId in self.air.doId2do:
            return self.air.doId2do[toonId]
        else:
            self.notify.warning('getToon() - toon: %d not in repository!' % toonId)

    def getSuit(self, suitId):
        # Exists for parity, but functionality is the same
        return self.getToon(suitId)

    # Messages from DistributedBattle

    def toonRequestRun(self):
        toonId = self.air.getAvatarIdFromSender()
        if self.ignoreResponses == 1:
            self.notify.debug('ignoring response from toon: %d' % toonId)
            return
        self.notify.debug('toonRequestRun(%d)' % toonId)
        if not self.isRunable():
            self.notify.warning('toonRequestRun() - not runable')
            return
        updateAttacks = 0
        toon = simbase.air.doId2do.get(toonId)
        if not toon:
            return

        if toon.getBattleState() != BattleStateEnum.ACTIVE:
            self.notify.warning('toon tried to run, but not found in activeToons: %d' % toonId)
            return

        self.__makeToonRun(toonId, updateAttacks)
        self.d_setMembers()
        self.needAdjust = 1
        self.__requestAdjust()

    def toonRequestJoin(self, x, y, z):
        toonId = self.air.getAvatarIdFromSender()
        self.notify.debug('toonRequestJoin(%d)' % toonId)
        self.signupToon(toonId, x, y, z)

    def toonDied(self):
        toonId = self.air.getAvatarIdFromSender()
        self.notify.info("LogStats ToonDiedInBattle toonid %s" % toonId)
        self.notify.debug('toonDied(%d)' % toonId)
        if toonId in self.toons:
            toon = self.getToon(toonId)
            if toon:
                toon.hp = -1
                toon.addStat(ToonStats.GONE_SAD)
                toon.inventory.zeroInv(1)
                toon.handleGoSadQuest()
                messenger.send(toon.getGoneSadMessage())
                self.__handleSuddenExit(toonId, 0)

    def signupToon(self, toonId, x, y, z):
        """ signupToon(toonId, x, y, z)
        Adds the toon to the battle.  This can be requested directly
        by the toon (via toonRequestJoin) or by the AI.
        """
        self.notify.info("LogStats ToonRequestJoin toonid %s" % toonId)
        if self.toons.count(toonId):
            # If the toon is already part of this battle, ignore the
            # message completely.  Don't even send back a deny
            # message, which would just confuse the client.
            return
        toon = self.air.doId2do.get(toonId)
        if toon and toon.hp > 0 and self.toonCanJoin(toonId):
            if self.addToon(toonId):
                self.__joinToon(toonId, Point3(x, y, z))
                self.d_setMembers()
        else:
            self.notify.warning('toonRequestJoin() - not joinable')
            self.d_denyLocalToonJoin(toonId)

    def d_denyLocalToonJoin(self, toonId):
        self.notify.debug('network: denyLocalToonJoin(%d)' % toonId)
        self.sendUpdateToAvatarId(toonId, 'denyLocalToonJoin', [])

    def toonRequestSurrender(self):
        toonId = self.air.getAvatarIdFromSender()
        if self.ignoreResponses == 1:
            self.notify.debug('ignoring response from toon: %d' % toonId)
            return
        if self.ratelimiter.userBlocked(toonId):
            self.notify.debug('ignoring response from toon: %d, they are ratelimited' % toonId)
            return
        self.notify.debug('toonRequestSurrender(%d)' % toonId)
        toon = self.air.doId2do.get(toonId)
        if not toon:
            return

        if toon.getBattleState() != BattleStateEnum.ACTIVE:
            self.notify.warning('toon tried to surrender, but not found in activeToons: %d' % toonId)
            return

        # Register their surrender request
        # Toggle it to false if they surrender again
        if toonId in self.surrenderRequests:
            self.surrenderRequests[toonId] = not self.surrenderRequests[toonId]
        else:
            self.surrenderRequests[toonId] = True

        self.adjustSurrendered()

    def adjustSurrendered(self):
        numSurrendered = 0
        numToons = len(self.toons)
        requiredSurrenderVotes = BattleGlobals.getSurrenderVotes(numToons)

        for toonId in self.toons:
            if toonId in self.surrenderRequests:
                # Get the value of their surrender request, it would be 0/False if they toggled off
                numSurrendered += int(self.surrenderRequests[toonId])

        self.b_setNumSurrendered(numSurrendered, requiredSurrenderVotes,
                                 [toonId for toonId in self.surrenderRequests.keys() if self.surrenderRequests[toonId]])

        # Check if the number of surrender votes meets requirements.
        if numSurrendered >= requiredSurrenderVotes:
            self.finishSurrender()

    def finishSurrender(self):
        for toonId in self.toons:
            self.notify.info("LogStats ToonSurrenderedBattle toonid %s" % toonId)
            self.__makeToonRun(toonId, False)
            self.d_setMembers()
            self.needAdjust = 1
            self.__requestAdjust()

            toon = simbase.air.doId2do.get(toonId)
            if toon:
                # Very minor punishment for surrendering
                toon.b_setHp(1)

        if len(self.toons) and len(self.activeSuits):
            # Make a cog say an on-defeat phrase
            # Cogs with custom phrases take priority, otherwise pick a random one.
            toonId = self.toons[0]
            specialSuits = []
            for suit in self.activeSuits:
                if suit.dna.name in SuitBattleGlobals.SuitSurrenderTauntIds.keys():
                    specialSuits.append(suit)

            if len(specialSuits):
                suit = random.choice(specialSuits)
            else:
                # No special cogs, pick a random one
                suit = random.choice(self.activeSuits)
            suitIndex, suitContext = suit.doId, suit.dna.name

            self.sendUpdateGameover(toonId, run=False, suitIndex=suitIndex, suitContext=suitContext, forceUber=False,
                                    surrender=True)

    def clearSurrenderRequests(self):
        self.surrenderRequests = {}
        self.b_setNumSurrendered(0, len(self.toons), [])

    ##### WaitForInput Responses #####

    def resetPlayerResponses(self):
        self.responses = {}
        for t in self.toons:
            if t in self.npcToons:
                self.responses[t] = 1
            else:
                self.responses[t] = 0

        self.ignoreResponses = 0

    def resetAllResponses(self):
        self.responses = {}
        for t in self.toons:
            self.responses[t] = 0

        self.ignoreResponses = 0

    def resetLockIns(self):
        self.lockIns = {}
        for t in self.toons:
            self.lockIns[t] = 0

        # Send the updated info to the client
        self.d_setLockIns()

    def allToonsResponded(self):
        for t in self.toons:
            if self.responses[t] == 0:
                return 0

        self.ignoreResponses = 1
        return 1

    def __allPendingActiveToonsResponded(self):
        for t in self.pendingToons + self.activeToons:
            if self.responses[t] == 0:
                return 0

        self.ignoreResponses = 1
        return 1

    def __allActiveToonsResponded(self):
        for t in self.activeToons:
            if self.responses[t] == 0:
                return 0

        self.ignoreResponses = 1
        return 1

    def __allActiveToonsRespondedAndLockedIn(self):
        for t in self.activeToons:
            if self.responses[t] == 0 or self.lockIns[t] == 0:
                return 0

        self.ignoreResponses = 1
        return 1

    def __removeResponse(self, toonId):
        del self.responses[toonId]
        if self.ignoreResponses == 0 and len(self.toons) > 0:
            currStateName = self.getCurrentOrNextState()
            if currStateName == 'WaitForInput':
                if self.__allActiveToonsRespondedAndLockedIn():
                    self.notify.debug('removeResponse() - dont wait for movie')
                    self.__requestMovie()
            elif currStateName == 'PlayMovie':
                if self.__allPendingActiveToonsResponded():
                    self.notify.debug('removeResponse() - surprise movie done')
                    self.__movieDone()
            elif currStateName == 'Reward' or currStateName == 'BuildingReward':
                if self.__allActiveToonsResponded():
                    self.notify.debug('removeResponse() - surprise reward done')
                    self.handleRewardDone()

    def __removeLockIn(self, toonId):
        if toonId in self.lockIns:
            del self.lockIns[toonId]

        if self.ignoreResponses == 0 and len(self.toons) > 0:
            currStateName = self.getCurrentOrNextState()
            if currStateName == 'WaitForInput':
                if self.__allActiveToonsRespondedAndLockedIn():
                    self.notify.debug('removeResponse() - dont wait for movie')
                    self.__requestMovie()

    ##### Adjust Responses #####

    def __resetAdjustingResponses(self):
        self.adjustingResponses = {}
        for t in self.playerToons:
            self.adjustingResponses[t] = 0

        self.ignoreAdjustingResponses = 0

    def __allAdjustingToonsResponded(self):
        for t in self.playerToons:
            if self.adjustingResponses[t] == 0:
                return 0

        self.ignoreAdjustingResponses = 1
        return 1

    def __removeAdjustingResponse(self, toonId):
        if toonId in self.adjustingResponses:
            del self.adjustingResponses[toonId]
            if self.ignoreAdjustingResponses == 0 and len(self.toons) > 0:
                if self.__allAdjustingToonsResponded():
                    self.__adjustDone()

    ##### Join Responses #####

    def __addJoinResponse(self, avId, taskName, toon = 0):
        """ Add self as a responder to any other avatar that is joining
            the battle if it's a toon, then create a response dictionary
            for self to join the battle
        """
        if toon == 1:
            for jr in list(self.joinResponses.values()):
                jr[avId] = 0

        self.joinResponses[avId] = {}
        for t in self.playerToons:
            self.joinResponses[avId][t] = 0

        self.joinResponses[avId]['taskName'] = taskName

    def __removeJoinResponses(self, avId):
        """ Remove a response dictionary for self joining the battle (if
            one exists), and remove self from any other existing response
            dictionaries
        """
        self.__removeJoinResponse(avId)
        removedOne = 0
        for j in list(self.joinResponses.values()):
            if avId in j:
                del j[avId]
                removedOne = 1

        if removedOne == 1:
            # Check if we have any toons that need to go
            for t in self.joiningToons:
                if self.__allToonsRespondedJoin(t):
                    self.__makeAvPending(t)
            # Check if we have any suits that need to go
            for s in self.joiningNotPendingSuits:
                if self.__allToonsRespondedJoin(s.doId):
                    # Only put them in pending state if they were in joiningSuits, not joiningNotPendingSuits.
                    self.__makeAvPending(s.doId, makePending=self.__suitsWantPendingDict.get(s.doId, True))

    def __removeJoinResponse(self, avId):
        """ Remove a response dictionary for self joining the battle (if
            one exists)
        """
        if avId in self.joinResponses:
            taskMgr.remove(self.joinResponses[avId]['taskName'])
            del self.joinResponses[avId]

    def __allToonsRespondedJoin(self, avId):
        """ Return 1 if all toons in battle have responded that avId has
            successfully joined and is in the pending list
        """
        jr = self.joinResponses[avId]
        for t in self.playerToons:
            if jr[t] == 0:
                return 0

        return 1

    def __allAvatarsRespondedJoin(self):
        return all([self.__allToonsRespondedJoin(avId) for avId in self.joinResponses])

    def __cleanupJoinResponses(self):
        for jr in list(self.joinResponses.values()):
            taskMgr.remove(jr['taskName'])
            del jr

    ##### Client Response Messages #####

    def adjustDone(self):
        toonId = self.air.getAvatarIdFromSender()
        if self.ignoreAdjustingResponses == 1:
            self.notify.debug('adjustDone() - ignoring toon: %d' % toonId)
            return
        elif self.adjustFsm.getCurrentState().getName() != 'Adjusting':
            self.notify.warning('adjustDone() - in state %s' % self.getCurrentOrNextState())
            return
        elif self.toons.count(toonId) == 0:
            self.notify.warning('adjustDone() - toon: %d not in toon list' % toonId)
            return
        self.adjustingResponses[toonId] += 1
        self.notify.debug('toon: %d done adjusting' % toonId)
        if self.__allAdjustingToonsResponded():
            self.__adjustDone()

    def timeout(self):
        toonId = self.air.getAvatarIdFromSender()
        currState = self.getCurrentOrNextState()

        if self.ignoreResponses == 1:
            return
        elif currState != 'WaitForInput':
            self.notify.warning(f'timeout() - in state: {currState}')
            return
        elif self.toons.count(toonId) == 0:
            self.notify.warning('timeout() - toon: %d not in toon list' % toonId)
            return

        self.battleCalc.createToonAttack(AttackEnum.TOON_NO_ATTACK, self.getToon(toonId))
        self.sendAttacksAndLockInsToClient()
        self.responses[toonId] += 1
        self.afkToons[toonId] += 1
        if self.__allActiveToonsRespondedAndLockedIn():
            self.__requestMovie(timeout=1)

    def movieDone(self):
        toonId = self.air.getAvatarIdFromSender()
        if self.ignoreResponses == 1:
            self.notify.debug('movieDone() - ignoring toon: %d' % toonId)
            return
        elif self.getCurrentOrNextState() != 'PlayMovie':
            self.notify.warning('movieDone() - in state %s' % self.getCurrentOrNextState())
            return
        elif self.toons.count(toonId) == 0:
            self.notify.warning('movieDone() - toon: %d not in toon list' % toonId)
            return
        self.responses[toonId] += 1
        self.notify.debug('toon: %d done with movie' % toonId)
        if self.__allPendingActiveToonsResponded():
            self.__movieDone()
        # If the majority of our toons have responded, then start a 5 second timer until the movie is forced done.
        elif len([response for response in list(self.responses.values()) if response > 0]) >= (len(self.responses) - 1):
            self.timer.stop()
            self.timer.startCallback(TIMEOUT_PER_USER, self.serverMovieDone)

    def rewardDone(self):
        """ rewardDone()
        """
        toonId = self.air.getAvatarIdFromSender()
        stateName = self.getCurrentOrNextState()
        if self.ignoreResponses == 1:
            self.notify.debug('rewardDone() - ignoring toon: %d' % toonId)
            return
        elif stateName not in ('Reward', 'BuildingReward', 'FactoryReward', 'MintReward', 'StageReward', 'CountryClubReward', 'BoardOfficeReward'):
            self.notify.warning('State %s is not in DistributedBattleBaseAI!' % stateName)
            return
        elif self.toons.count(toonId) == 0:
            self.notify.warning('rewardDone() - toon: %d not in toon list' % toonId)
            return
        self.responses[toonId] += 1
        self.notify.debug('toon: %d done with reward' % toonId)
        if self.__allActiveToonsResponded():
            self.handleRewardDone()
        else:
            # Reset the timer to give the slowpokes a few seconds
            # longer than the first (or most recent) toon to reply.
            self.timer.stop()
            self.timer.startCallback(TIMEOUT_PER_USER, self.serverRewardDone)

    def assignRewards(self):
        if self.rewardHasPlayed == 1:
            self.notify.debug('handleRewardDone() - reward has already played')
            return
        self.rewardHasPlayed = 1
        return BattleExperienceAI.assignRewards(
            self.activeToons, self.battleCalc.toonSkillPtsGained, self.suitsKilled,
            self.getTaskZoneId(), self.helpfulToons, self.toonRoundParticipation,
        )

    def joinDone(self, avId, makePending: bool):
        """ joinDone(avId)
        """
        toonId = self.air.getAvatarIdFromSender()
        if self.toons.count(toonId) == 0:
            self.notify.warning('joinDone() - toon: %d not in toon list' % toonId)
            return
        av = simbase.air.doId2do.get(avId)
        if not av:
            self.notify.warning(f'joinDone() - avatar {avId} does not exist!')
            return
        if avId not in self.joinResponses:
            self.notify.info('joinDone() - no entry for: %d - ignoring: %d' % (avId, toonId))
            return
        jr = self.joinResponses[avId]
        if toonId in jr:
            jr[toonId] += 1
        self.notify.info('client with localToon: %d done joining av: %d' % (toonId, avId))
        if self.__allToonsRespondedJoin(avId):
            wantPending = self.__suitsWantPendingDict.get(avId, True)
            self.notify.info(f"all toons responded with pending mode: {makePending}")
            self.__makeAvPending(avId, makePending=makePending)

    def requestAttack(self, track, level, av, autoLockIn):
        """ requestAttack(track, level, av, autoLockIn)
        """
        toonId = self.air.getAvatarIdFromSender()
        toon = self.air.doId2do.get(toonId)
        currState = self.getCurrentOrNextState()
        self.notify.debug(f'client with localToon: {toonId} requestAttack {av}')

        if self.ignoreResponses == 1:
            return
        elif currState != 'WaitForInput':
            self.notify.warning(f'requestAttack() - in state: {currState}')
            return
        elif toon.getBattleState() != BattleStateEnum.ACTIVE:
            self.notify.warning('requestAttack() - toon: %d not in toon list' % toonId)
            return

        self.parseToonAttackRequest(toonId, track, level, av, autoLockIn)

    def parseToonAttackRequest(self, toonId, track, level, av, autoLockIn):
        toon = self.getToon(toonId)
        if toon is None:
            self.notify.warning('requestAttack() - no toon: %d' % toonId)
            return

        validResponse = 1
        doneUnAttack = False
        if track == AttackEnum.TOON_NPC:
            self.air.writeServerEvent('NPCSOS', toonId, '%s' % av)

            # Make sure the toon has the IOU
            if sum(item.getItemSubtype() == level for item in toon.getIOUs()):
                npcCollision = 0
                if level in self.npcAttacks:
                    if toon.getBattleState() == BattleStateEnum.ACTIVE:
                        self.battleCalc.createToonAttack(AttackEnum.TOON_PASS, toon)
                    npcCollision = 1

                if level not in IOURegistry:
                    # TODO: should we write server event (maybe?) and return immediately instead?
                    self.notify.warning(f"Rejecting NPCSOS ID {level} for toonId {toonId}; "
                                        "reason: battleCalc deemed this SOS NPC is invalid for this round.")
                    validResponse = 0
                    npcCollision = 1  # NOTE: remove this if we decide to just return immediately instead, otherwise this is a cheap way to make sure we don't add the npc below

                if npcCollision == 0:
                    # Convert the target index into a target id if possible.
                    if 0 <= av < len(self.activeToons):
                        targetId = self.activeToons[av]
                    else:
                        targetId = av
                    self.battleCalc.createToonAttack(track, toon, level=level, target=targetId)
                    if av == -1:
                        validResponse = 0
                    else:
                        self.npcAttacks.append(level)
        elif track == AttackEnum.TOON_UN_ATTACK:
            if toonId in self.battleCalc.toonAttacks:
                npcId = self.battleCalc.toonAttacks[toonId].level
                if npcId in self.npcAttacks:
                    self.npcAttacks.remove(npcId)

            self.battleCalc.createToonAttack(AttackEnum.TOON_UN_ATTACK, toon)

            if toonId in self.responses:
                self.responses[toonId] = 0

            if toonId in self.lockIns:
                self.lockIns[toonId] = 0

            doneUnAttack = True
            validResponse = 0
        elif track == AttackEnum.TOON_PASS:
            self.battleCalc.createToonAttack(AttackEnum.TOON_PASS, toon)
        elif track == AttackEnum.TOON_FIRE:
            self.battleCalc.createToonAttack(AttackEnum.TOON_FIRE, toon, target=av)
        elif track == AttackEnum.TOON_SUE:
            self.battleCalc.createToonAttack(AttackEnum.TOON_SUE, toon, target=av)
        else:
            # If the track is not one of the above special values, it
            # must be one of the valid tracks in
            # BattleGlobals.
            if not self.validate(toonId, track in ATTACK_TRACKS, 'requestAttack: invalid track %s' % track):
                return

            if not self.validate(toonId, MIN_LEVEL_INDEX <= level <= MAX_LEVEL_INDEX, 'requestAttack: invalid level %s' % level):
                return

            trackDisabledEffects = toon.getStatusEffectsOfSpecificType(GagTracksDisabled)
            for effect in trackDisabledEffects:
                disabledTracks = effect.getAllDisabledTracks()
                if disabledTracks:
                    if track in disabledTracks:
                        self.battleCalc.createToonAttack(AttackEnum.TOON_NO_ATTACK, toon)
                        return

            levelDisabledEffects = toon.getStatusEffectsOfSpecificType(GagLevelsDisabled)
            for effect in levelDisabledEffects:
                disabledLevels = effect.getAllDisabledLevels()
                if disabledLevels:
                    if level in disabledLevels:
                        self.battleCalc.createToonAttack(AttackEnum.TOON_NO_ATTACK, toon)
                        return

            mixedTrackLevelDisabledEffects = toon.getStatusEffectsOfType(MixedGagTracksLevelsDisabled)
            for effect in mixedTrackLevelDisabledEffects:
                disabledTracksLevels = effect.getAllDisabledTracksLevels()
                if disabledTracksLevels:
                    if (track, level) in disabledTracksLevels:
                        self.battleCalc.createToonAttack(AttackEnum.TOON_NO_ATTACK, toon)
                        return

            # For now, we assume that the avId is being correctly
            # validated downstream of here.
            if toon.inventory.numItem(track, level) == 0:
                # Ignore if we can afford it through Illegal Means.
                pipsqueak = toon.getStatusEffectOfId(SEE.EFFECT_PIP_COUNTER)
                # Also check if we can afford it via a counterfeit
                counterfeit = toon.getStatusEffectOfId(SEE.EFFECT_COUNTERFEIT_CONTAINER)
                if not (pipsqueak or (counterfeit and counterfeit.getGagTrackLevel(track, level))):
                    self.notify.warning('requestAttack() - toon has no item track: %d level: %d' % (track, level))
                    self.battleCalc.createToonAttack(AttackEnum.TOON_NO_ATTACK, toon)
                    return

            if track == AttackEnum.TOON_HEAL:
                # See if the target for the heal is running away
                avObj = self.air.doId2do.get(av)
                if avObj and avObj.getBattleState() == BattleStateEnum.RUNNING or \
                    attackAffectsGroup(track, level) and len(self.activeToons) < 2:
                    self.battleCalc.createToonAttack(AttackEnum.TOON_UN_ATTACK, toon)
                    validResponse = 0
                    doneUnAttack = True
                else:
                    self.battleCalc.createToonAttack(track, toon, level=level, target=av)
            else:
                self.battleCalc.createToonAttack(track, toon, level=level, target=av)
                if av == -1 and not attackAffectsGroup(track, level):
                    # No target yet; it's not yet a complete attack.
                    validResponse = 0

        if validResponse == 1:
            self.responses[toonId] += 1
            self.lockIns[toonId] = autoLockIn

        self.sendAttacksAndLockInsToClient()

        # If the Toon did an un-attack, properly set it to a no-attack
        # to prevent the client from thinking the client is constantly
        # backing out from an attack that it had just set.
        if doneUnAttack:
            self.avIdsWithUnattacks.add(toonId)
            self.battleCalc.createToonAttack(AttackEnum.TOON_NO_ATTACK, toon)

        if self.__allActiveToonsRespondedAndLockedIn():
            self.__requestMovie()

    def requestLockIn(self, value):
        toonId = self.air.getAvatarIdFromSender()
        toon = self.air.doId2do.get(toonId)
        if self.ignoreResponses == 1:
            self.notify.debug('requestLockIn() - ignoring toon: %d' % toonId)
            return
        elif self.getCurrentOrNextState() != 'WaitForInput':
            self.notify.warning('requestLockIn() - in state: %s' % self.getCurrentOrNextState())
            return
        elif toon and toon.getBattleState() != BattleStateEnum.ACTIVE:
            self.notify.warning('requestLockIn() - toon: %d not in toon list' % toonId)
            return
        self.notify.debug('requestLockIn(%s)' % (toonId))

        # A player can only change their lock in if they have provided a response for their action choice already
        if toonId in self.responses and self.responses[toonId] > 0:
            self.lockIns[toonId] = value

            # Check if we can play the movie now.
            if self.__allActiveToonsRespondedAndLockedIn():
                self.__requestMovie()
            # Otherwise, send the updated info to the client.
            else:
                self.d_setLockIns()

    def requestCounterfeit(self, gagTrack, gagLevel):
        toonId = self.air.getAvatarIdFromSender()
        toon = self.air.doId2do.get(toonId)
        if self.ignoreResponses == 1:
            self.notify.debug('requestCounterfeit() - ignoring toon: %d' % toonId)
            return
        elif self.getCurrentOrNextState() != 'WaitForInput':
            self.notify.warning('requestCounterfeit() - in state: %s' % self.getCurrentOrNextState())
            return
        elif toon and toon.getBattleState() != BattleStateEnum.ACTIVE:
            self.notify.warning('requestCounterfeit() - toon: %d not in toon list' % toonId)
            return
        self.notify.debug('requestCounterfeit(%s)' % toonId)

        copyCost = gagLevel + 1

        existingUsageEffect = toon.getStatusEffectOfId(SEE.EFFECT_COUNTERFEIT_USAGE_CONTAINER)
        if existingUsageEffect and existingUsageEffect.getGagTrackLevel(gagTrack, gagLevel):
            # Can't counterfeit a gag that we have already counterfeited once
            return

        counterfeits = toon.getCounterfeits()
        if counterfeits < 0:
            return

        # Counterfeits cannot be used on reward cooldown
        if toon.getStatusEffectOfType(StatusEffects.RewardCooldownStatusEffect):
            return

        # No counterfeits when prevented in sync.
        for rewardModifier in toon.getModifiersOfType(*ModifierEnums.REWARD_MODIFIERS):
            if not rewardModifier.canUseCounterfeits():
                return

        # It's pretty sus when a Toon tries to counterfeit
        # with more counterfeits than they actually have...
        if copyCost > counterfeits:
            simbase.air.writeServerEvent('suspicious', avId=toonId,
                                         issue=f'Toon attempting to counterfeit a {copyCost} cost gag with {counterfeits} counterfeits')
            self.notify.warning(
                f'Toon {toonId} attempting to counterfeit a {copyCost} cost gag with {counterfeits} counterfeits')
            return False

        toon.getHammerspace().removeItemQuantity(MaterialItemType.Counterfeits, copyCost)
        toon.addStat(ToonStats.COUNTERFEITS, amount=copyCost)

        # Fully add the counterfeit effect to the Toon, allowing them to use a gag for free
        existingEffect = toon.getStatusEffectOfId(SEE.EFFECT_COUNTERFEIT_CONTAINER)
        if existingEffect:
            existingEffect.setGagTrackLevel(gagTrack, gagLevel, 1)
        else:
            effect, _ = toon.addStatusEffect(SEE.EFFECT_COUNTERFEIT_CONTAINER)
            effect.setGagTrackLevel(gagTrack, gagLevel, 1)

        # Mark the counterfeit as being used, which will prevent them from being able to do it in the future this battle
        if existingUsageEffect:
            existingUsageEffect.setGagTrackLevel(gagTrack, gagLevel, existingUsageEffect.getGagTrackLevel(gagTrack, gagLevel) + 1)
        else:
            usageEffect, _ = toon.addStatusEffect(SEE.EFFECT_COUNTERFEIT_USAGE_CONTAINER)
            usageEffect.setGagTrackLevel(gagTrack, gagLevel, 1)

        # Add a reward cooldown to them
        # Round time is based on level of gag used

        maxLevel = BattleGlobals.MAX_LEVEL_INDEX
        for gagModifier in toon.getModifiersOfType(ModifierType.GagsContentSync):
            maxLevel = min(maxLevel, gagModifier.getMaxGagLevel())

        retDict = BattleGlobals.getCounterfeitCooldownsForMaxLevel(maxLevel)
        gagCd = retDict.get(gagLevel, 0)

        if gagCd:
            cooldownEffect, _ = toon.addStatusEffect(SEE.EFFECT_REWARD_COOLDOWN)
            cooldownEffect.setRounds(gagCd, adjust=False)

        # Finally, send the new counterfeit info over to this toon
        toon.sendStatusEffects()
        self.sendUpdate('toonUsedCounterfeit', [toon.doId, gagTrack, gagLevel])

    @property
    def maxSuitsIncludingOverrides(self):
        if not self.suits:
            return self.maxSuits
        maxOverrideSuitNum = max([SuitBattleGlobals.STREET_BATTLE_COG_CAP.get(suit.dna.name, 0) for suit in self.suits])
        return max(self.maxSuits, maxOverrideSuitNum)

    # Misc
    def lessSuitsThanMax(self):
        return len(self.suits) < self.maxSuitsIncludingOverrides

    def suitCanJoin(self):
        return self.lessSuitsThanMax() and self.isJoinable()

    def toonCanJoin(self, toonId):
        def denyJoinWithNotif(toon, title, subtitle):
            toon.addNotification(GenericTextNotification(
                textId=GenericTextId.DeniedBattle,
                title=title,
                subtitle=subtitle,
            ))

        av = self.air.doId2do.get(toonId)

        standardCanJoin = len(self.toons) < 4 and self.isJoinable()
        groupCanJoin = True

        totalToonList = []
        for existingBattleMemberId in self.toons + self.reservedAvIds:
            if existingBattleMemberId not in totalToonList:
                totalToonList.append(existingBattleMemberId)

        # We gotta be locked out if we can't fit in with the reserved toons
        if self.reservedAvIds and len(totalToonList) >= 4 and toonId not in self.reservedAvIds:
            if av:
                denyJoinWithNotif(av, title='Reserved Toons',
                                  subtitle=f'This battle has too many reserved Toons for you to join.')
            return False

        toonGroup = self.air.groupManager.getGroupOfAvId(toonId)
        # Special case for groups that have a battle announced
        if toonGroup:
            if toonGroup.announcedBattle:
                # A group battle already exists, we can only join this one if we're reserved for it
                # The battle will reserve us after the initial member engages with the cog we want
                # If there's no reservation, we can just join the battle straight up.
                groupCanJoin = toonId in self.reservedAvIds or len(self.reservedAvIds) <= 0
                if not groupCanJoin:
                    if av:
                        denyJoinWithNotif(av, title='Wrong Battle',
                                          subtitle='You cannot join this battle because your Group has an active battle.')
                    return False
            else:
                groupCanJoin = len(totalToonList) + len(toonGroup.avatarList) <= 4
                if not groupCanJoin:
                    if av:
                        denyJoinWithNotif(av, title='Reserved Toons',
                                          subtitle='This battle has too many reserved Toons for your group to join.')
                    return False

        return standardCanJoin and groupCanJoin

    def determineWaitState(self) -> None:
        """Determine which wait state to go into.

        If we have active suits available, go to input.
        Otherwise, wait for the new suits to join.
        """
        if self.activeSuits:
            self.b_setState('WaitForInput')
            return

        self.b_setState('WaitForJoin')

    def __requestMovie(self, timeout=0):
        if self.adjustFsm.getCurrentState().getName() == 'Adjusting':
            self.notify.debug('__requestMovie() - in Adjusting')
            self.movieRequested = 1
            return

        if len(self.activeToons) == 0:
            self.notify.warning('only pending toons left in battle %s, toons = %s' % (self.doId, self.toons))
            self.movieRequested = 1
            return
        elif len(self.activeSuits) == 0:
            self.notify.warning('only pending suits left in battle %s, suits = %s' % (self.doId, self.suits))
            self.movieRequested = 1
            return

        movieDelay = 0
        if len(self.activeToons) - len([npc for npc in self.npcToons if npc in self.activeToons]) > 1 and not timeout:
            # If there are multiple player toons involved in the battle,
            # pad the start of the movie by 1 second so other
            # toons can see what the last toon chose as his attack
            movieDelay = 1

        # An interactive cutscene has been queued to occur.
        # Delay the attack calculations (attack movie creation)
        # to after the cutscene is finished.
        if self.interactiveCutsceneQueued:
            # Enter the MakeMovie state on both processes.
            self.b_setState('MakeMovie')

            # Prepare the interactive cutscene.
            self.prepareInteractiveCutscene()
            # Start up a barrier for the cutscene if there was a
            # timeout delay time specified.
            if self.INTERACTIVE_CUTSCENE_DELAY is not None:
                self.beginBarrier(
                    "InteractiveCutscene",
                    self.activeToons,
                    self.INTERACTIVE_CUTSCENE_DELAY,
                    self.finishInteractiveCutscene
                )
            return

        # Enter the MakeMovie state on the server.
        self.request('MakeMovie')

        if movieDelay:
            taskMgr.doMethodLater(0.8, self.__makeMovie, self.uniqueName('make-movie'))
            self.taskNames.append(self.uniqueName('make-movie'))
        else:
            self.__makeMovie()

    def __makeMovie(self, task = None):
        if self._DOAI_requestedDelete:
            self.notify.warning('battle %s requested delete, then __makeMovie was called!' % self.doId)
            if hasattr(self, 'levelDoId'):
                self.notify.warning('battle %s in level %s' % (self.doId, self.levelDoId))
            return

        self.__removeTaskName(self.uniqueName('make-movie'))

        if self.movieHasBeenMade == 1:
            self.notify.debug('__makeMovie() - movie has already been made')
            return

        self.movieRequested = 0
        self.movieHasBeenMade = 1
        self.movieHasPlayed = 0
        self.rewardHasPlayed = 0

        roundLog = dict(
            battle_id=self.doId,
            start_time=int(self.realStartTime),
            round_time=int(time.time()),
            district_id=self.air.districtId,
            district_name=self.air.districtName,
            zone_id=self.zoneId,
            toons=[],
            involved_toons=[],
            suits=[],
        )

        # Make sure all toons have an attack entry (even if it's a no-attack)
        for t in self.activeToons:
            if t not in self.battleCalc.toonAttacks:
                self.battleCalc.createToonAttack(AttackEnum.TOON_NO_ATTACK, self.getToon(t))

            attack = self.battleCalc.toonAttacks[t]
            toon = self.getToon(t)
            roundLog['involved_toons'].append(t)

            # If it was a NO_ATTACK, and the toon is guilty of an unattack,
            # set the toon to be properly an unattack.
            if t in self.avIdsWithUnattacks and attack.attackType == AttackEnum.TOON_NO_ATTACK:
                attack.attackType = AttackEnum.TOON_UN_ATTACK

            if toon:
                roundLog['toons'].append(dict(
                    name=toon.getName(),
                    id=toon.doId,
                    hp=toon.getHp(),
                    max_hp=toon.getMaxHp(),
                    track=repr(attack.attackType),
                    level=attack.level,
                    target=attack.target,
                    status_effects=self.makeBattleLogStatusEffectList(toon),
                ))

            # Replace any PASS or UN_ATTACK with a NO_ATTACK
            if attack.attackType in (AttackEnum.TOON_PASS, AttackEnum.TOON_UN_ATTACK):
                self.battleCalc.createToonAttack(AttackEnum.TOON_NO_ATTACK, toon)

            # If toon isn't AFK, increment their rounds participating.
            if attack.attackType not in (AttackEnum.TOON_NO_ATTACK, AttackEnum.TOON_PASS):
                # So they didn't pass or un attack, they must have done something useful
                self.afkToons[t] = 0
                self.addHelpfulToon(t)
                self.incrementToonParticipation(t)

        # Reset unattacks
        self.avIdsWithUnattacks = set()

        # Set each suit's HP on the client.
        for suit in self.activeSuits:
            suit: DistributedSuitBaseAI

            # If the suit is generated, set the suit's HP on the server/client.
            if suit.isGenerated():
                suit.b_setHp(suit.getHp())

            # If any removed suits are still active, return.
            if not hasattr(suit, "dna"):
                self.notify.warning("a removed suit is in this battle!")
                return Task.done

            # Let's make ourselves a nice pretty list of status effects before we proceed
            seList = []
            for e in suit.getStatusEffects():
                if e.effectId in TTLocalizer.StatusEffectDescriptions:
                    seList.append(f"{TTLocalizer.StatusEffectDescriptions[e.effectId][0]}{f': {e.rounds} rounds' if e.rounds > 0 else ''}")

            roundLog['suits'].append(dict(
                name=suit.dna.name,
                dept=suit.dna.dept,
                exe=bool(suit.isElite),
                id=suit.doId,
                hp=suit.getHp(),
                max_hp=suit.getMaxHp(),
                level=suit.getActualLevel(),
                status_effects=self.makeBattleLogStatusEffectList(suit),
            ))

        activeToons = self.activeToons
        activeSuits = self.activeSuits
        if not activeToons or not activeSuits:
            return Task.done

        self.air.netMessenger.send('sendBattleLog', [json.dumps(roundLog)])

        # Turn the hpOwnedByBattle flag on for each active toon.
        for toonId in activeToons:
            toon = self.getToon(toonId)
            if not toon:
                continue

            toon.hpOwnedByBattle = 1
            if toon.immortalMode:
                # A free toonup first, to guarantee the battle
                # round won't kill this immortal toon.
                toon.toonUp(toon.getMaxHp())

        self.battleCalc.setParticipants(activeToons, activeSuits)
        self.battleCalc.calculateRound()

        # Only sort suits if the list of active
        # suits was modified by the battle.
        if activeSuits != self.activeSuits:
            self.sortSuits(activeSuits)

        # We'll be going ahead and letting know each client
        # about what visual effects will NOT be present
        # at the end of this turn.
        self.informVisualEffectsEnding()

        # Tell the toons how much experience they will earn so far.
        # Also, from this point on until the end of the movie, the
        # toons will be allowed to accumulate more than their maxHp,
        # since we'll fix it up at the end of the movie.
        for t in self.activeToons:
            self.sendEarnedExperience(t)

        self.d_setAfkToons()
        self.d_setMovie()
        self.b_setState('PlayMovie')
        return Task.done

    def makeBattleLogStatusEffectList(self, battleAv):
        if not hasattr(battleAv, "getStatusEffects"):
            return []  # What the heck are you doing
        seList = []
        for effect in battleAv.getStatusEffects():
            if effect.effectId in TTLocalizer.StatusEffectDescriptions:
                seList.append(self.getStatusEffectExtraInfo(effect))

        return seList

    def getStatusEffectExtraInfo(self, effect):
        eid = effect.effectId
        title = TTLocalizer.StatusEffectDescriptions[eid][0]
        rounds = f": {effect.rounds} round{'s' if effect.rounds > 1 else ''}" if effect.rounds > 0 else ''
        extraInfo = ""
        # Here we'll start determining per-status effect what extra info to add. Some effects won't have extra info which is fine.
        if eid == SEE.EFFECT_SUIT_LURED:
            extraInfo = f" (-{effect.knockback})"
        if eid == SEE.EFFECT_SUIT_TRAPPED:
            title = "Trapped"  # Need to do this bc it usually fills in the name for us w/ whatever gag is used
            extraInfo = f" (-{effect.trapDamage})"
        if eid in [SEE.EFFECT_ENCORE, SEE.EFFECT_SUIT_DAMAGE_BOOST]:
            extraInfo = f" (+{int((effect.multiplier - 1) * 100)}%)"
        if eid in [SEE.EFFECT_SUIT_ADDITIVE_DAMAGE_BOOST, SEE.EFFECT_RIPPED]:
            extraInfo = f" (+{effect.multiplier})"
        if eid == SEE.EFFECT_LURE_RESISTANCE:
            extraInfo = f" ({effect.getAmount()} rounds)"
        if eid == SEE.EFFECT_COURT_RECORD:
            extraInfo = f" (Level {effect.gagLevel}{f'& {effect.gagLevel2}' if effect.gagLevel2 >= 0 else ''})"
        if eid == SEE.EFFECT_TOON_DAMAGE_UP:
            title = f"{TTLocalizer.BattleGlobalTracksUpper[int(effect.getGagTrack())]} IOU"
        return f"{title}{extraInfo}{rounds}"

    def sendEarnedExperience(self, toonId):
        # Sends the experience earned so far to the toon, so he can
        # update his display to show which gags are clipped by the
        # experience cap.
        toon = self.getToon(toonId)
        if toon is not None:
            expList = self.battleCalc.toonSkillPtsGained.get(toonId, None)
            if expList is None:
                toon.d_setEarnedExperience([])
            else:
                roundList = []
                for exp in expList:
                    roundList.append(int(exp + 0.5))

                toon.d_setEarnedExperience(roundList)

    def sendUpdateGameover(self, toonId, run, suitIndex=None, suitContext=None, forceUber=None, surrender=False):
        message = 'TAUNT_GENERAL'
        if not (suitIndex and suitContext):
            suitIndex, suitContext = self.getSuitIndexWhoKilled(toonId)
        if run and len(self.toons) == 0 and len(self.suits):
            message = 'TAUNT_RUN'
            suitIndex = self.suits[0].doId
        toon = self.getToon(toonId)
        uber = forceUber if forceUber is not None else toon.uber
        self.sendUpdate('setSuitGameoverString', [
            suitIndex, self.makeSuitGameoverMessage(message, context=suitContext, uber=uber, surrender=surrender)
        ])

    def getSuitIndexWhoKilled(self, toonId):
        # Peeks into the battle calculator's attack order,
        # and gets the index of the suit who killed the given toon Id.
        checkSuit = 0
        suitContext = 0
        for attack in self.battleCalc.getAttackOrder():
            if isinstance(attack, ToonAttackAI) or attack in self.suitAttackAIExceptions:
                continue

            attack: AttackAI

            if attack.invoker is None or attack.invoker.isToon():
                continue

            result = attack.findResult(toonId)
            if not result:
                continue

            if attack.invoker.dna.name in SuitBattleGlobals.SuitGameoverTauntIds:
                suitContext = attack.invoker.dna.name
            elif attack.invoker.getActualLevel() == 1:
                suitContext = 2
            elif result.died:
                suitContext = 1

            if len(attack.getDeadTargets()) == 1:  # check for only one toon
                checkSuit = attack.invoker  # (in cases of group attack)
                self.suitAttackAIExceptions.append(attack)
                break

        if checkSuit:
            return (checkSuit.doId, suitContext)
        return (0, suitContext)

    def makeSuitGameoverMessage(self, messageGroup, context=False, highPriority=False, uber=False, surrender=False):
        # Make a pool of potential game over taunts, then return one.
        # First, set the taunt list base.
        gameoverTaunts = SuitBattleGlobals.SuitGameoverTaunts
        tauntList = gameoverTaunts['TAUNT_GENERAL']
        if surrender:
            tauntList = gameoverTaunts['TAUNT_SURRENDER']
        elif highPriority:
            tauntList = gameoverTaunts[messageGroup]
        else:
            # Check which message group we're setting, and make sure it makes sense.
            messageAdd = messageGroup
            if self.gameoverGroupOverride is not None:
                messageAdd = self.gameoverGroupOverride
            if messageAdd not in gameoverTaunts:
                self.notify.warning("invalid gameover taunt " + str(messageAdd) + " was called")
            else:
                # Actually set the message group.
                tauntList = gameoverTaunts[messageAdd]
        if isinstance(context, str):
            # The taunt is already defined for this cog.
            tauntIds = SuitBattleGlobals.SuitSurrenderTauntIds if surrender else SuitBattleGlobals.SuitGameoverTauntIds
            if tauntIds:
                if context in tauntIds:
                    tauntList = []
                    for taunt in tauntIds[context]:
                        if type(taunt) == str:  # Regular taunt that does not have any special conditions
                            tauntList.append(taunt)
                        elif type(taunt) == dict:  # Conditional taunts such as an uber
                            if uber:
                                if uberTaunts := taunt.get("uber"):
                                    for uberTaunt in uberTaunts:
                                        tauntList.append(uberTaunt)
        else:
            if messageGroup not in ('TAUNT_RUN', 'TAUNT_SURRENDER'):
                # Check our zone, update our message group to reflect.
                zoneName = ZoneUtil.getWhereName(self.zoneId, False)
                if hasattr(self, 'bossCogId'):
                    tauntList = gameoverTaunts['TAUNT_BOSS']
                elif zoneName == 'street':
                    tauntList = tauntList + gameoverTaunts['TAUNT_STREET']
                elif self.isLevelBattle:
                    tauntList = gameoverTaunts['TAUNT_FACILITY']
                if self.trueSolo and zoneName != 'street':
                    # Solo gameover taunts get added into the above pool.
                    tauntList = tauntList + gameoverTaunts['TAUNT_SOLO']
            if context == 1:  # Group
                tauntList = gameoverTaunts['TAUNT_GROUP']
            elif context == 2:  # Killed by level 1
                tauntList = gameoverTaunts['TAUNT_WEAK']
        if len(tauntList) == 1:
            return tauntList[0]
        return random.choice(tauntList)

    def updateTimescale(self):
        self.sendUpdate('setTimescale', [round(self.timescale, 2)])

    # Each state will have an enter function, an exit function,
    # and a datagram handler, which will be set during each enter function.

    # Specific State functions

    ##### Off state #####

    def enterOff(self):
        return

    def exitOff(self):
        return

    ##### FaceOff state #####

    def enterFaceOff(self):
        return

    def exitFaceOff(self):
        return

    ##### WaitForJoin state #####

    def enterWaitForJoin(self):
        self.notify.debug('enterWaitForJoin() - no active suits')
        self.runable = True
        self.resetPlayerResponses()
        self.__requestAdjust()

    def exitWaitForJoin(self):
        pass

    ##### WaitForInput state #####

    def enterWaitForInput(self):
        self.notify.debug('enterWaitForInput()')
        self.joinable = True
        self.runable = True
        self.npcAttacks = []
        self.resetAllResponses()
        self.resetLockIns()
        self.__requestAdjust()
        self.checkAfkAttacks()
        self.updateTimescale()
        self.timer.startCallback(self.serverInputTimeout / self.timescale, self._serverTimedOut)

        # handle autoRestock
        removedToons = []
        for toonId in self.toons:
            toon = self.air.doId2do.get(toonId)
            if toon is not None:
                self.notify.debug(f"Toon: {toon.getName()} in zone {toon.zoneId}. My zone is {self.zoneId}.")
                toonBranchZone = ZoneUtil.getBranchZone(toon.zoneId)
                battleBranchZone = ZoneUtil.getBranchZone(self.zoneId)
                if toonBranchZone != battleBranchZone and not ZoneUtil.isDynamicZone(self.zoneId):
                    self.notify.info(f"Toon: {toon.getName()} zone mismatch, theirs: {toonBranchZone}, " \
                                     f"ours: {battleBranchZone}, triggering __handleSuddenExit(toonId, True)")
                    self.__handleSuddenExit(toonId, False)
                if bboard.get('autoRestock-%s' % toonId, False):
                    toon.doRestock(0)
            else:
                removedToons.append(toonId)
        for toonId in removedToons:
            self.__handleSuddenExit(toonId, False)

    def exitWaitForInput(self):
        self.npcAttacks = []
        self.timer.stop()

    def _serverTimedOut(self):
        self.notify.debug('wait for input timed out on server')
        self.ignoreResponses = 1
        self.__requestMovie(timeout=1)

    ##### MakeMovie state #####

    def enterMakeMovie(self):
        self.notify.debug('enterMakeMovie()')
        self.runable = False
        self.resetPlayerResponses()

    def exitMakeMovie(self):
        pass

    ##### PlayMovie state #####

    def enterPlayMovie(self):
        self.notify.debug('enterPlayMovie()')
        self.joinable = True
        self.runable = False
        self.resetPlayerResponses()

        # Estimate an upper bound for the length of the movie
        movieTime = self.getMovieTime()

        self.notify.debug('estimated upper bound of movie time: %f' % movieTime)
        self.timer.startCallback(movieTime, self.serverMovieDone)

    def getMovieTime(self) -> float:
        baseTime = ATTACK_TIME * len(self.battleCalc.getAttackOrder()) + SERVER_BUFFER_TIME
        return baseTime + self.getAdditionalMovieTime()

    def getAdditionalMovieTime(self) -> float:
        additionalMovieTime = 0.0

        # Run through each attack, determine what cogs died, and if we should count them for
        # additional Special Movie Time. Yippee!!
        for attack in self.battleCalc.getAttackOrder():
            additionalMovieTime += attack.ADDITIONAL_BARRIER_LENGTH
            for target in attack.getDeadTargets():
                suit = self.getSuit(target.avId)
                if suit and isinstance(suit, DistributedSuitBaseAI) and suit.dna.name in SuitBattleGlobals.DEATH_EXTEND_MOVIE_TIME:
                    additionalMovieTime += SuitBattleGlobals.DEATH_EXTEND_MOVIE_TIME[suit.dna.name]

        return additionalMovieTime

    def serverMovieDone(self):
        self.notify.debug('movie timed out on server')
        self.ignoreResponses = 1
        self.__movieDone()

    def serverRewardDone(self):
        self.notify.debug('reward timed out on server')
        self.ignoreResponses = 1
        self.handleRewardDone()

    def handleRewardDone(self):
        self.b_setState('Resume')

    def exitPlayMovie(self):
        self.timer.stop()

    def appendSuitsKilled(self, encounter):
        self.suitsKilled.append(encounter)

    def __movieDone(self):
        self.notify.info('__movieDone() - movie is finished')
        if self.movieHasPlayed == 1:
            self.notify.warning('__movieDone() - movie had already finished')
            return
        self.movieHasBeenMade = 0
        self.movieHasPlayed = 1
        self.ignoreResponses = 1
        needUpdate = False

        # Calculate toon experience and remove any dead suits
        deadSuits = []
        for attack in self.battleCalc.getAttackOrder():
            ds, nu = attack.postprocess()
            deadSuits.extend(ds)
            needUpdate = nu or needUpdate

        deadSuits = set(deadSuits)

        currLuredSuits = self.battleCalc.getLuredSuits()
        if len(self.luredSuits) == len(currLuredSuits):
            for suit in self.luredSuits:
                if suit not in currLuredSuits:
                    needUpdate = True
                    break
        else:
            needUpdate = True

        self.luredSuits = currLuredSuits.copy()

        for suit in deadSuits:
            suit: DistributedSuitBaseAI
            self.notify.info("LogStats CogWasDefeated")
            self.notify.debug('removing dead suit: %d' % suit.doId)
            if suit.isDeleted():
                self.notify.debug('whoops, suit %d is deleted.' % suit.doId)
            else:
                self.notify.debug('suit had revives? %d' % suit.getSkeleRevives())
                encounter = {'type': suit.dna.name,
                             'level': suit.getActualLevel(),
                             'track': suit.dna.dept,
                             'isSkelecog': suit.getSkelecog(),
                             'isForeman': suit.isForeman(),
                             'isBoss': 0,
                             'isSupervisor': suit.isSupervisor(),
                             'isVirtual': suit.isVirtual(),
                             'hasRevives': suit.getSkeleRevives(),
                             'isElite': suit.getElite(),
                             'activeToons': self.activeToons[:]}
                self.notify.info("LogStats CogWithSuitWasDefeated suit %s" % suitDeptFullnames[suit.dna.dept])
                encounter = self.addSpecialEncounterInfo(suit, encounter)
                self.appendSuitsKilled(encounter)
                self.suitsKilledThisBattle.append(encounter)
                self.air.suitInvasionManager.handleSuitDefeated()
            self.__removeSuit(suit)
            needUpdate = True
            if not suit.getPersistent():
                suit.resume()

        if len(self.activeSuits) == 0 and len(self.pendingSuits) == 0:
            lastActiveSuitDied = 1
        else:
            lastActiveSuitDied = 0

        deadToons = []
        for activeToon in self.activeToons:
            toon: DistributedToonBaseAI = self.getToon(activeToon)
            if toon is not None:
                toon.hpOwnedByBattle = 0
                hp = toon.hpAdjustBattle
                self.notify.debug(f"Active Toon {activeToon}: HP Adjust={hp}, Unadjusted Toon HP={toon.hp}")
                toon.hpAdjustBattle = 0

                if hp >= 0:
                    toon.toonUp(hp, quietly=1)
                else:
                    toon.takeDamage(-hp, quietly=1)

                if toon.hp <= 0:
                    toon.inventory.zeroInv(1)
                    deadToons.append(activeToon)
                # Remove them from the battle if they have the dead effect.
                elif toon.getStatusEffectOfId(SEE.EFFECT_DEAD):
                    deadToons.append(activeToon)

                if toon.unlimitedGags:
                    toon.doRestock(noUber=0)

        for deadToon in deadToons:
            self.removeToon(deadToon)
            needUpdate = True

        # Update the HP of the cogs once the movie is done
        for suit in self.activeSuits:
            suit.d_setMaxHp(suit.getMaxHp())
            suit.d_setHp(suit.getHp())
            # Update their skelecogness
            if suit.isSkelecog:
                suit.d_setSkelecog(1)

        self.battleCalc.clearAttacks()
        self.d_setMovie()
        self.d_setMembers()
        self.sendAttacksAndLockInsToClient()
        self.battleCalc.sendEvent(BEG.EVENT_MOVIE_DONE)
        self.updateTimescale()
        self.localMovieDone(needUpdate, deadToons, list(deadSuits), lastActiveSuitDied)
        self.updateBattleAvatars()
        self.battleCalc.checkForSkillPoints()
        self.battleCalc.attackOrder.cleanup()

    def addSpecialEncounterInfo(self, suit, encounter: dict):
        """
        Extends an encounter dict with more information should we desire.
        """
        if hasattr(suit, 'forceForemanFlag'):
            encounter['forceForemanFlag'] = 1
        return encounter

    ##### Reward state #####

    def prepareReward(self, rewardState: str = "Reward") -> None:
        exp = self.getBattleExperience()
        exp[-1] = self.assignRewards()
        self.d_setBattleExperience(exp)
        self.b_setState(rewardState)

    ##### Resume state #####

    def enterResume(self):
        self.getBattleListener().sendEvent(eventId=BEG.EVENT_BATTLE_END)
        # Disband any groups that may be lingering and attached to this battle now that its dead.
        for groupAvId in self.attachedGroupAvIds:
            toonGroup = self.air.groupManager.getGroupOfAvId(groupAvId)
            if toonGroup:
                for avatar in toonGroup.avatarList:
                    groupToon = self.air.doId2do.get(avatar.avId)
                    if groupToon:
                        groupToon.addNotification(GenericTextNotification(
                            textId=GenericTextId.BattleFullGroupDisbanded,
                            title='Group Disbanded',
                            subtitle='Your Group has been disbanded because your Group\'s battle has ended.',
                        ))
            messenger.send('GroupManager-DisbandToonGroup', [groupAvId])

        for suit in self.suits:
            suit: DistributedSuitBaseAI
            self.notify.info('battle done, resuming suit: %d' % suit.doId)
            if suit.isDeleted():
                self.notify.info('whoops, suit %d is deleted.' % suit.doId)
            else:
                suit.cleanupBattle()
                suit.setBattleState(BattleStateEnum.INACTIVE)
                suit.sendStatusEffects()
                if not suit.getPersistent():
                    suit.resume()

        self.suits = []
        self.luredSuits = []

        for toonId in self.toons:
            toon = simbase.air.doId2do.get(toonId)
            if toon:
                toon.cleanupBattle()
                toon.setBattleState(BattleStateEnum.INACTIVE)
                toon.sendStatusEffects()
                toon.b_setBattleId(0)
                messageToonReleased = 'Battle releasing toon %s' % toon.doId
                messenger.send(messageToonReleased, [toon.doId])

        # Stop responding to avatar exit events
        for exitEvent in self.avatarExitEvents:
            self.ignore(exitEvent)

        # Log the suits killed for this battle only, just for
        # marketing purposes.
        eventMsg = {}
        for encounter in self.suitsKilledThisBattle:
            cog = encounter['type']
            level = encounter['level']
            msgName = '%s%s' % (cog, level)
            if encounter['isSkelecog']:
                msgName += '+'
            if msgName in eventMsg:
                eventMsg[msgName] += 1
            else:
                eventMsg[msgName] = 1

        # Now format the message for the AI.
        msgText = ''
        for msgName, count in list(eventMsg.items()):
            if msgText != '':
                msgText += ','
            msgText += '%s%s' % (count, msgName)

        self.air.writeServerEvent('battleCogsDefeated', self.doId, '%s|%s' % (msgText, self.getTaskZoneId()))

    def exitResume(self):
        pass

    ##################################
    ##### Joinable/Runable Flags #####
    ##################################

    def isJoinable(self):
        return self.joinable

    def isRunable(self):
        return self.runable

    ######################
    ##### Adjust ClassicFSM #####
    ######################

    ##### Adjusting state #####

    def __estimateAdjustTime(self):
        adjustTime = 0
        if len(self.pendingSuits) > 0 or self.suitGone == 1:
            self.suitGone = 0
            pos0 = self.suitPendingPoints[0][0]
            pos1 = self.suitPoints[0][0][0]
            adjustTime = self.calcSuitMoveTime(pos0, pos1)
        if len(self.pendingToons) > 0 or self.toonGone == 1:
            self.toonGone = 0
            if adjustTime == 0:
                pos0 = self.toonPendingPoints[0][0]
                pos1 = self.toonPoints[0][0][0]
                adjustTime = self.calcToonMoveTime(pos0, pos1)
        return adjustTime

    def enterAdjusting(self):
        # raise Exception
        self.notify.info('enterAdjusting()')
        if not self.needAdjust:
            self.notify.info('enterAdjusting() - does not need adjust')
            return
        self.needAdjust = 0
        self.timer.stop()
        self.__resetAdjustingResponses()
        self.adjustingTimer.startCallback(self.__estimateAdjustTime() + SERVER_BUFFER_TIME, self.__serverAdjustingDone)

    def __serverAdjustingDone(self):
        if self.needAdjust == 1:
            self.adjustFsm.request('NotAdjusting')
            self.__requestAdjust()
        else:
            self.notify.debug('adjusting timed out on the server')
            self.ignoreAdjustingResponses = 1
            self.__adjustDone()

    def exitAdjusting(self):
        currStateName = self.getCurrentOrNextState()
        self.notify.info(f'exitAdjusting()')
        if currStateName == 'WaitForInput':
            self.timer.restart()
        elif currStateName == 'WaitForJoin':
            self.b_setState('WaitForInput')
        self.adjustingTimer.stop()

    def __adjustDone(self):
        for s in self.adjustingSuits:
            self.addActiveSuit(s)

        self.adjustingSuits = []
        for t in self.adjustingToons:
            toon = self.air.doId2do.get(t)
            if not toon:
                continue

            if toon.getBattleState() != BattleStateEnum.ACTIVE:
                toon.setBattleState(BattleStateEnum.ACTIVE)
                # In case ignoreResponses was set to 1 during adjusting,
                # we need to clear it because a new toon is now active
                self.ignoreResponses = 0
                # Welcome, toon!  Here's your experience earned so far.
                self.sendEarnedExperience(toon.doId)
            else:
                self.notify.warning('adjustDone() - toon: %d already active!' % toon.doId)

        self.adjustingToons = []
        self.d_setMembers()
        self.updateBattleAvatars()
        self.adjustFsm.request('NotAdjusting')
        if self.needAdjust == 1:
            self.notify.debug('__adjustDone() - need to adjust again')
            self.__requestAdjust()

    ##### NotAdjusting state #####

    def enterNotAdjusting(self):
        self.notify.debug('enterNotAdjusting()')
        if self.movieRequested == 1:
            # Make sure last toon didn't just run and adjusting may have
            # resulted in a new active toon who needs to choose an attack
            if len(self.activeToons) > 0 and self.__allActiveToonsRespondedAndLockedIn():
                self.__requestMovie()

    def exitNotAdjusting(self):
        pass

    def _getNextSerialNum(self):
        num = self.serialNum
        self.serialNum += 1
        return num

    def showToonTipAll(self, tipId: int) -> None:
        for avId in self.activeToons:
            toon = self.getToon(avId)
            if toon:
                toon.showToonTip(tipId)

    def sortSuits(self, suitList: list):
        # Create a shallow copy of the suits.
        suitsCopy = self.suits.copy()

        def findSuitInActive(suit):
            if suit in suitList:
                return suitList.index(suit)
            return suitsCopy.index(suit)

        # Sort the copy based on its index in
        # the active suits list.
        suitsCopy = sorted(suitsCopy, key=findSuitInActive)

        # Append any suits that may have been
        # added to the suits list.
        for suit in self.suits:
            if suit not in suitsCopy:
                suitsCopy.append(suit)

        # Finally, reset the list of suits.
        self.suits = suitsCopy

    def prepareInteractiveCutscene(self):
        # Send an update to all of the clients to begin the cutscene.
        self.sendUpdate("beginInteractiveCutscene")

    def finishInteractiveCutscene(self, _=None):
        self.interactiveCutsceneQueued = False
        self.__makeMovie()

    def addActiveSuit(self, suit: DistributedSuitBaseAI) -> None:
        suit.setBattleState(BattleStateEnum.ACTIVE)
        self.addBattleAvatar(suit)

    def b_setGagOrder(self, gagOrder: List[AttackEnum]):
        assert all((attack in BattleGlobals.GAG_TRACK_ORDER) for attack in gagOrder)
        self.gagOrder = gagOrder
        self.sendUpdate('setGagOrder', [gagOrder])

    def b_setNumSurrendered(self, numSurrendered, maxSurrendered, surrenderedToons):
        self.numSurrendered = numSurrendered
        self.maxSurrendered = maxSurrendered
        self.surrenderedToons = surrenderedToons
        self.sendUpdate('setNumSurrendered', [numSurrendered, maxSurrendered, surrenderedToons])

    """
    Properties
    """

    @property
    def activeToonObjs(self):
        return [self.getToon(toon) for toon in self.activeToons if self.getToon(toon)]

    @property
    def activeToons(self):
        return [toonId for toonId in self.toons if getattr(self.getToon(toonId), "getBattleState", lambda: None)() \
                == BattleStateEnum.ACTIVE]

    @property
    def pendingToons(self):
        return [toonId for toonId in self.toons if getattr(self.getToon(toonId), "getBattleState", lambda: None)() \
                == BattleStateEnum.PENDING]

    @property
    def joiningToons(self):
        return [toonId for toonId in self.toons if getattr(self.getToon(toonId), "getBattleState", lambda: None)() \
                == BattleStateEnum.JOINING]

    @property
    def runningToons(self):
        return [toonId for toonId in self.toons if getattr(self.getToon(toonId), "getBattleState", lambda: None)() \
                == BattleStateEnum.RUNNING]
