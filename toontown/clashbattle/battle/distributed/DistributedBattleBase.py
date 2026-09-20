from typing import List

from direct.actor import Actor
from direct.distributed.ClockDelta import *
from direct.distributed.DistributedNode import DistributedNode
from direct.fsm import ClassicFSM
from direct.fsm import State
from direct.fsm.FSM import FSM
from direct.interval.IntervalGlobal import *
from direct.task.Task import Task

from toontown.clashbattle.battle import BattleGlobals
from toontown.clashbattle.battle import BattleParticles
from toontown.clashbattle.battle import BattleProps
from toontown.clashbattle.battle import Movie
from toontown.clashbattle.battle import MovieUtil
from toontown.clashbattle.battle.BattleBase import *
from toontown.clashbattle.battle.BattleCamera import BattleCamera
from toontown.clashbattle.battle.SuitBattleGlobals import ITERATIVE_CHAT, SuitAttributes
from toontown.clashbattle.battle.attacks.base.AttackEnum import AttackEnum
from toontown.clashbattle.battle.movielistener.BattleMovieListener import BattleMovieListener
from toontown.clashbattle.battle.statuses import SEE
from toontown.clashbattle.battle.statuses.StatusEffects import GagTracksDisabled, GagLevelsDisabled, MixedGagTracksLevelsDisabled
from toontown.clashbattle.battle.statuses.StatusEffects import UnitesDisabledStatusEffect, \
    UseGagLevelSenderStatusEffect, UseGagLevelsWithTrackSenderStatusEffect, UntouchableStatusEffect
from toontown.clashbattle.battle.visuals.VisualEffectEnums import VisualEffectEnum
from toontown.clashbattle.battle.visuals.VisualEffects import VisualEffectRemoved
from toontown.chat.constants import ChatEvents
from toontown.chat.ui.speedchat.TTSCUniteTerminal import TTSCUniteStateChangedEvent
from toontown.distributed import DelayDelete
from toontown.hood import ZoneUtil
from toontown.inventory.registry.IOURegistry import IOURegistry
from toontown.clashsuit.suit import Suit, SuitDNA, SuitGlobals
from toontown.clashsuit.suit.DistributedSuit import DistributedSuit
from toontown.clashsuit.suit.DistributedSuitBase import DistributedSuitBase
from toontown.toon import GagInventory
from toontown.toon import TTEmote
from toontown.toon.DistributedToonBase import DistributedToonBase
from toontown.toonbase.MarginManagerCell import ScreenCellFlag
from toontown.toonbase.ToonBase import *


class DistributedBattleBase(DistributedNode, FSM, BattleBase):
    defaultTransitions = {
        "Off": ["FaceOff", "WaitForInput", "WaitForJoin", "MakeMovie", "PlayMovie", "Reward", "Resume"],
        "FaceOff": ["WaitForInput"],
        "WaitForJoin": ["WaitForInput", "Resume"],
        "WaitForInput": ["MakeMovie", "PlayMovie", "Resume"],
        "MakeMovie": ["PlayMovie", "Resume"],
        "PlayMovie": ["WaitForInput", "WaitForJoin", "Reward", "Resume"],
        "Reward": ["Resume", "WaitForJoin"],
        "Resume": [],
    }

    CAMERA_CLASS = BattleCamera
    FLY_IN_CUTOFF_DUR = 6
    MAX_SUIT_WIDTH = 18
    camFov = BattleGlobals.BattleCamDefaultFov
    camJoinPos = BattleGlobals.BattleCamJoinPos
    camJoinHpr = BattleGlobals.BattleCamJoinHpr
    id = 0

    def __init__(self, cr, townBattle):
        DistributedNode.__init__(self, cr)
        FSM.__init__(self, self.__class__.__name__)

        # DistributedNode inherits from NodePath, but doesn't call
        # NodePath's constructor to avoid multiple calls to it that
        # result from multiple inheritance along the Actor tree
        NodePath.__init__(self)
        self.assign(render.attachNewNode(self.uniqueBattleName('distributed-battle')))

        BattleBase.__init__(self)

        self.bossBattle = 0
        self.townBattle = townBattle
        self.__battleCleanedUp = 0

        self.camera = self.CAMERA_CLASS(self)

        self.activeIntervals = {}
        self.localToonJustJoined = 0
        self.choseAttackAlready = 0
        self.toons = []
        self.suitTraps = ''
        self.membersKeep = None

        self.targetId = -1
        self.lockIn = 0

        # Create unique event/task names
        self.faceOffName = self.uniqueBattleName('faceoff')
        self.localToonBattleEvent = self.uniqueBattleName('localtoon-battle-event')
        self.adjustName = self.uniqueBattleName('adjust')
        self.timerCountdownTaskName = self.uniqueBattleName('timer-countdown')

        self.movie = Movie.Movie(self)
        self.timer = Timer()

        self.needAdjustTownBattle = 0

        self.streetBattle = 1
        self.levelBattle = 0
        self.isInstance = 0

        self.movieActive = False
        self.suitIndices = {}
        self.luredSuits = []
        self.suedSuits = []
        self.untouchableSuits = []
        self.untouchableByTrapSuits = []
        self.afkToons = []
        self.removedVisualEffects = []  # type: List[VisualEffectRemoved]
        self.localBattleToon = None

        self.uniteDisabledFlags = set()

        self.timescale = 1.0  # overall battle speed
        self.runoutTime = TTLocalizer.BBbattleInputTimeout
        self.clientInputTimeout = CLIENT_INPUT_TIMEOUT

        self.gameoverDict = {}

        self.localToonFsm = ClassicFSM.ClassicFSM('LocalToon', [
            State.State('HasLocalToon', self.enterHasLocalToon, self.exitHasLocalToon,
                        ['NoLocalToon', 'WaitForServer']),
            State.State('NoLocalToon', self.enterNoLocalToon, self.exitNoLocalToon, ['HasLocalToon', 'WaitForServer']),
            State.State('WaitForServer', self.enterWaitForServer, self.exitWaitForServer,
                        ['HasLocalToon', 'NoLocalToon'])], 'WaitForServer', 'WaitForServer')
        self.localToonFsm.enterInitialState()

        self.request("Off")

        self.adjustFsm = ClassicFSM.ClassicFSM('Adjust', [
            State.State('Adjusting', self.enterAdjusting, self.exitAdjusting, ['NotAdjusting']),
            State.State('NotAdjusting', self.enterNotAdjusting, self.exitNotAdjusting, ['Adjusting'])], 'NotAdjusting',
                                               'NotAdjusting')
        self.adjustFsm.enterInitialState()
        self.currRound = 0

        self.gagOrder = BattleGlobals.GAG_TRACK_ORDER[:]

        self.numSurrendered = 0
        self.maxSurrendered = 0
        self.surrenderedToons = []
        self.battleMovieListener = BattleMovieListener(battle=self)

    def uniqueBattleName(self, name):
        DistributedBattleBase.id += 1
        return name + '-%d' % DistributedBattleBase.id

    def generate(self):
        self.notify.debug('generate(%s)' % self.doId)
        DistributedNode.generate(self)
        self.__battleCleanedUp = 0
        self.reparentTo(render)
        self._skippingRewardMovie = False

    def announceGenerate(self):
        super().announceGenerate()
        self.movie.announceGenerate()

    def storeInterval(self, interval, name):
        if name in self.activeIntervals:
            ival = self.activeIntervals[name]
            # If the interval has a delayDelete, finish it now and destroy the delayDeletes
            # otherwise, preserve the original behavior of letting the old interval continue
            # to run if it's running
            if hasattr(ival, 'delayDelete') or hasattr(ival, 'delayDeletes'):
                self.clearInterval(name, finish=1)
        self.activeIntervals[name] = interval

    def __cleanupIntervals(self):
        for interval in list(self.activeIntervals.values()):
            interval.finish()
            DelayDelete.cleanupDelayDeletes(interval)

        self.activeIntervals = {}

    def clearInterval(self, name, finish = 0):
        if name in self.activeIntervals:
            ival = self.activeIntervals[name]
            if finish:
                ival.finish()
            else:
                ival.pause()
            if name in self.activeIntervals:
                DelayDelete.cleanupDelayDeletes(ival)
                # cleanupDelayDeletes might cause the involved avatar to be deleted,
                # which would clear the interval out of self.activeIntervals. Check
                # again to see if it's still in the dict
                if name in self.activeIntervals:
                    del self.activeIntervals[name]
        else:
            self.notify.debug('interval: %s already cleared' % name)

    def finishInterval(self, name):
        if name in self.activeIntervals:
            interval = self.activeIntervals[name]
            interval.finish()

    def disable(self):
        self.notify.debug('disable(%s)' % self.doId)
        self.cleanupBattle()
        DistributedNode.disable(self)

    def battleCleanedUp(self):
        return self.__battleCleanedUp

    def _cleanupLocalToon(self):
        self.removeLocalToon()
        base.camLens.setMinFov(settings['fieldofview'] / (4. / 3.))
        base.localAvatar.cameraFSM.request('Off')
        camera.wrtReparentTo(base.localAvatar)
        base.localAvatar.cameraFSM.request('Orbit')
        self.townBattle.battle = None

    def cleanupBattle(self):
        # Undo all the battle stuff as if it has been disabled.  This
        # can be called on the client when we need the battle to get
        # out of the way now, without waiting for a disable message
        # from the AI.

        if self.__battleCleanedUp:
            return
        self.notify.debug('cleanupBattle(%s)' % self.doId)

        self.__battleCleanedUp = 1

        FSM.cleanup(self)

        self.__cleanupIntervals()
        self.battleMovieListener.cleanup()
        self.battleMovieListener = None

        for battleAv in self.activeToons + self.activeSuits:
            battleAv.cleanupBattle()
            battleAv.setBattleState(BattleStateEnum.INACTIVE)

        # RequestFinalState(), above, may set the camera back to
        # camFov, the default fov for battles, but removeLocalToon,
        # below, should restore it to the DefaultCameraFov for
        # non-battle gameplay.
        if self.hasLocalToon():
            self._cleanupLocalToon()
        self.localToonFsm.request('WaitForServer')

        self.ignoreAll()

        for suit in self.suits:
            if suit.battleTrap != NO_TRAP:
                self.notify.debug('250 calling self.removeTrap, suit=%d' % suit.doId)
                self.removeTrap(suit)
            suit.battleTrap = NO_TRAP
            suit.battleTrapProp = None
            self.notify.debug('253 suit.battleTrapProp = None')
            suit.battleTrapIsFresh = 0

        self.suits = []
        self.suitTraps = ''

        self.toons = []

        self.__stopTimer()

        # It's important to clean up the intervals before we reset
        # membersKeep, since some of the intervals might reference
        # objects protected by membersKeep.
        self.__cleanupIntervals()
        self._removeMembersKeep()

        taskMgr.doMethodLater(1.0, self.doSuitGameover, self.uniqueName('gameover-call'), extraArgs=[self.gameoverDict])

    def delete(self):
        self.notify.debug('delete(%s)' % self.doId)
        self.__cleanupIntervals()
        self._removeMembersKeep()
        # Eliminate a circular reference
        self.movie.cleanup()
        del self.townBattle
        self.removeNode()
        FSM.cleanup(self)
        self.localToonFsm = None
        self.adjustFsm = None
        self.__stopTimer()
        self.timer = None
        self.camera.cleanup()
        del self.camera
        # Clean up battle avatars.
        for battleAv in self.activeToons + self.activeSuits:
            battleAv.cleanupBattle()
            battleAv.setBattleState(BattleStateEnum.INACTIVE)
        del self.localBattleToon
        super().delete()

    def loadTrap(self, suit, trapid):
        self.notify.debug('loadTrap() trap: %d suit: %d' % (trapid, suit.doId))
        trapName = AvProps[AttackEnum.TOON_TRAP][trapid]
        trap = BattleProps.globalPropPool.getProp(trapName)
        suit.battleTrap = trapid
        suit.battleTrapIsFresh = 0
        suit.battleTrapProp = trap
        self.notify.debug('suit.battleTrapProp = trap %s' % trap)
        if trap.getName() == 'traintrack':
            # the train track's parent is battle, no reparent needed.
            pass
        else:
            trap.wrtReparentTo(suit)
        distance = MovieUtil.SUIT_TRAP_DISTANCE
        if trapName == 'rake':
            distance = MovieUtil.SUIT_TRAP_RAKE_DISTANCE
            distance += MovieUtil.getSuitRakeOffset(suit)
            trap.setH(180)
            trap.setScale(0.7)
        elif trapName == 'trapdoor' or trapName == 'quicksand':
            trap.setScale(1.7)
        elif trapName == 'marbles':
            distance = MovieUtil.SUIT_TRAP_MARBLES_DISTANCE
            trap.setH(94)
        elif trapName == 'tnt':
            trap.setP(90)
            # Start particle effect if there isn't one already
            tip = trap.find('**/joint_attachEmitter')
            particleNode = tip.attachNewNode('tnt-particle-node')
            particleNode.setPos(0, 0, 0.5)
            sparks = BattleParticles.createParticleEffect(file='tnt')
            trap.sparksEffect = sparks
            sparks.start(particleNode)
        trap.setPos(0, distance, 0)
        if isinstance(trap, Actor.Actor):
            frame = trap.getNumFrames(trapName) - 1
            trap.pose(trapName, frame)

    def removeTrap(self, suit, removeTrainTrack = False):
        self.notify.debug('removeTrap() from suit: %d, removeTrainTrack=%s' % (suit.doId, removeTrainTrack))
        if suit.battleTrapProp is None:
            self.notify.debug('suit.battleTrapProp is None, suit.battleTrap=%s setting to NO_TRAP, returning' % suit.battleTrap)
            suit.battleTrap = NO_TRAP
            return
        if suit.battleTrap == UBER_GAG_LEVEL_INDEX:
            if removeTrainTrack:
                self.notify.debug('doing removeProp on traintrack')
                MovieUtil.removeProp(suit.battleTrapProp)
                for otherSuit in self.suits:
                    if not otherSuit == suit:
                        otherSuit.battleTrapProp = None
                        self.notify.debug('351 otherSuit=%d otherSuit.battleTrapProp = None' % otherSuit.doId)
                        otherSuit.battleTrap = NO_TRAP
                        otherSuit.battleTrapIsFresh = 0

            else:
                self.notify.debug('deliberately not doing removeProp on traintrack')
        else:
            self.notify.debug('suit.battleTrap != UBER_GAG_LEVEL_INDEX')
            MovieUtil.removeProp(suit.battleTrapProp)

        suit.battleTrapProp = None
        self.notify.debug('360 suit.battleTrapProp = None')
        suit.battleTrap = NO_TRAP
        suit.battleTrapIsFresh = 0

    ##### Convenience Functions #####

    def pause(self):
        self.timer.stop()

    def unpause(self):
        self.timer.resume()

    def findSuit(self, id):
        for s in self.suits:
            if s.doId == id:
                return s

        return None

    def findToon(self, id, warn=True):
        toon = self.getToon(id, warn)
        if toon is None:
            return
        for t in self.toons:
            if t == toon:
                return t

    def isSuitLured(self, suit):
        return suit in self.luredSuits

    def unlureSuit(self, suit: DistributedSuitBase):
        ve = suit.getVisualEffectOfId(VisualEffectEnum.LURED)
        if ve:
            ve.forceDestroy()

        if suit.specialHead:
            suit.specialHead.loopNeutral()
        if suit.stunStars:
            suit.cleanupStunStars()

    def setAfkToons(self, toons):
        self.afkToons = toons
        self.needAdjustTownBattle = 1

    def neutralSuits(self):
        for suit in self.activeSuits:
            suit.neutralAvatar()

    def updateInvMods(self):
        if self.localBattleToon:
            self.handleInvMods(self.localBattleToon)
            base.localAvatar.inventory.updateInventoryButtonsForModifiers()

    def setLocalBattleToon(self, battleToon):
        self.localBattleToon = battleToon
        # Handle unites
        self.updateLocalToonUniteStatus()

        base.localAvatar.inventory.allSuitsUntouchable = True if len(self.untouchableSuits) == len(self.activeSuits) else False
        base.localAvatar.inventory.allSuitsUntouchableNoTrap = len(self.untouchableByTrapSuits) == len(self.activeSuits)
        base.localAvatar.inventory.updateBattle(self)

    def handleInvMods(self, battleToon):
        # Handle inventory modifiers (done on a case by case basis instead of clearing all to not mess with tutorial)
        base.localAvatar.inventory.clearButtonModifier(GagInventory.INV_MOD_PUNISHMENT)
        base.localAvatar.inventory.clearButtonModifier(GagInventory.INV_MOD_PROP_BONUS)

        # First handle effect that affects all levels
        gagLevelPunishment = battleToon.getStatusEffectsOfSpecificType(UseGagLevelSenderStatusEffect)
        if gagLevelPunishment:
            for effect in gagLevelPunishment:
                base.localAvatar.inventory.applyInventoryButtonModifier(GagInventory.INV_MOD_PUNISHMENT,
                                                                        levels=[int(effect.gagLevel),
                                                                                int(effect.gagLevel2)])

        from toontown.clashbattle.battle.statuses.StatusEffects import PuzzleShowEffect
        puzzleEffects: List[List[PuzzleShowEffect]] = [suit.getStatusEffectsOfSpecificType(PuzzleShowEffect) for suit in self.activeSuits]
        # puzzleEffects will start off as a list of lists which sucks. Anyway.
        for effectList in puzzleEffects:
            for effect in effectList:
                base.localAvatar.inventory.applyInventoryButtonModifier(GagInventory.INV_MOD_PROP_BONUS,
                                                                        tracks=[effect.getTrack()])

        # Now handle effect that affects each track individually
        gagLevelTrackPunishment = battleToon.getStatusEffectsOfSpecificType(UseGagLevelsWithTrackSenderStatusEffect)
        if gagLevelTrackPunishment:
            for effect in gagLevelTrackPunishment:
                for track in range(len(BattleGlobals.Tracks)):
                    gagLevel = int(effect.getGagLevel(track))
                    if gagLevel == -1:
                        continue
                    base.localAvatar.inventory.applyInventoryButtonModifier(GagInventory.INV_MOD_PUNISHMENT,
                                                                            tracks=[track], levels=[gagLevel])

        # Disable certain gags
        base.localAvatar.inventory.clearButtonModifier(GagInventory.INV_MOD_DISABLED)
        isMonsoon = battleToon.getStatusEffectOfId(SEE.EFFECT_MONSOON)
        if isMonsoon:
            base.localAvatar.inventory.applyInventoryButtonModifier(GagInventory.INV_MOD_DISABLED,
                                                                    tracks=[AttackEnum.TOON_HEAL,
                                                                            AttackEnum.TOON_SOUND])

        trackDisabledEffects = battleToon.getStatusEffectsOfType(GagTracksDisabled)
        for effect in trackDisabledEffects:
            disabledTracks = effect.getAllDisabledTracks()
            if disabledTracks:
                base.localAvatar.inventory.applyInventoryButtonModifier(GagInventory.INV_MOD_DISABLED,
                                                                        tracks=disabledTracks)

        levelDisabledEffects = battleToon.getStatusEffectsOfType(GagLevelsDisabled)
        for effect in levelDisabledEffects:
            disabledLevels = effect.getAllDisabledLevels()
            if disabledLevels:
                base.localAvatar.inventory.applyInventoryButtonModifier(GagInventory.INV_MOD_DISABLED,
                                                                        levels=disabledLevels)

        mixedTrackLevelDisabledEffects = battleToon.getStatusEffectsOfType(MixedGagTracksLevelsDisabled)
        for effect in mixedTrackLevelDisabledEffects:
            disabledTracksLevels = effect.getAllDisabledTracksLevels()
            if disabledTracksLevels:
                track2Levels = {AttackEnum(track): [] for track in range(len(BattleGlobals.Tracks))}
                for track in range(len(BattleGlobals.Tracks)):
                    for level in range(BattleGlobals.MAX_LEVEL_INDEX + 1):
                        if effect.getGagTrackLevelDisabled(track, level):
                            track2Levels[track].append(level)

                    if track2Levels.get(track, []):
                        base.localAvatar.inventory.applyInventoryButtonModifier(GagInventory.INV_MOD_DISABLED,
                                                                                levels=track2Levels.get(track, []),
                                                                                tracks=[track])

    def addUniteDisabledFlag(self, flag):
        """Adds a flag marking a user's inability to use unites."""
        self.uniteDisabledFlags.add(flag)
        self.updateLocalToonUniteStatus()

    def removeUniteDisabledFlag(self, flag):
        """Removes a flag marking a user's inability to use unites."""
        if flag in self.uniteDisabledFlags:
            self.uniteDisabledFlags.remove(flag)
        self.updateLocalToonUniteStatus()

    def updateLocalToonUniteStatus(self):
        """Updates the ability for the local toon to use unites."""
        unitesDisabled = False

        # Does our battleToon have a unites disabled flag?
        if self.localBattleToon:
            effects = self.localBattleToon.getStatusEffectsOfType(UnitesDisabledStatusEffect)
            for effect in effects:
                if effect.rounds != 1:
                    unitesDisabled = True
                    break

        # Do we have any flags suggesting we should disable unites?
        if self.uniteDisabledFlags:
            unitesDisabled = True

        # Update the localAvatar's unite status accordingly.
        base.localAvatar.unitesDisabled['battle'] = unitesDisabled
        messenger.send(TTSCUniteStateChangedEvent)

    def uniteUsed(self, avId):
        av = self.cr.doId2do.get(avId)
        if not av:
            return

        # Distributed method called when a toon uses a unite to add the unite cooldown visual effect to them
        MovieUtil.applyVisualEffect(av, VisualEffectEnum.UNITE_COOLDOWN)

    def informVisualEffectsEnding(self, verList):
        self.removedVisualEffects = VisualEffectRemoved.fromStructList(verList)

    def resetRemovedVisualEffects(self):
        self.removedVisualEffects = []

    def unsplatSuit(self, suit):
        suit.clearSplats()

    def getActorPosHpr(self, actor, actorList = [], **kwargs):
        if isinstance(actor, Suit.Suit):
            if actorList == []:
                actorList = self.activeSuits
            if actor in actorList:
                return self.getSuitBattlePosHpr(actor, actorList)
            else:
                self.notify.warning('getActorPosHpr() - suit not active')
        else:
            if actorList == []:
                actorList = self.activeToons
            if actor in actorList:
                numToons = len(actorList) - 1
                index = actorList.index(actor)
                point = self.getToonPoint(numToons, index, **kwargs)
                return (Point3(point[0]), VBase3(point[1], 0.0, 0.0))
            else:
                self.notify.warning('getActorPosHpr() - toon not active')

    def correctToonPosition(self, **kwargs):
        for toon in self.activeToons:
            toon.setPosHpr(self, *self.getActorPosHpr(toon, **kwargs))

    def correctSuitPosition(self, **kwargs):
        for suit in self.activeSuits:
            if suit.isEmpty():
                continue
            suit.setPosHpr(self, *self.getActorPosHpr(suit, **kwargs))

    def getSuitWidth(self, suit):
        if suit is None or suit.getGeomNode() is None:
            return 0
        width = suit.getGeomNode().getScale()[0] * SuitGlobals.SUIT_BODY_TYPE_WIDTH[
            SuitDNA.getSuitBodyType(suit.dna.name)] * SuitAttributes[suit.dna.name]["extraPadding"]
        # Enforce a minimum width.
        return max(width, 4)

    def getSuitBattlePosHpr(self, suit, actorList: list):
        index = actorList.index(suit)
        numSuits = len(actorList) - 1
        point = self.getSuitPoint(numSuits, index)
        if len(point) > 2 and point[2]:
            return (Point3(point[0]), VBase3(point[1], 0.0, 0.0))
        pos = Point3(point[0])
        if len(actorList) == 1:
            suitX = 0
            h = 180
        else:
            # Get the width of each suit in the actor list.
            width = [self.getSuitWidth(s) for s in actorList]

            # Calculate the total sum of the suit widths.
            widthSum = sum(width)

            # Get the ratio of the maximum suit width allowed to the
            # width sum.
            widthRatio = max(widthSum / self.MAX_SUIT_WIDTH, 1)

            # Set the width factor to apply to any values which
            # rely on the width sum.
            widthFactor = 1

            # If the ratio wasn't capped, it can be applied to the
            # width sum.
            if widthRatio > 1:
                oldWidthSum = widthSum
                widthSum -= ((10 * widthRatio) - 10)
                widthFactor = widthSum / oldWidthSum

            # All of the prerequisite calculations have been complete, let's
            # start calculating the placement of the suit.
            # Start off to the far right using half of the total sum.
            startX = (widthSum / 2)

            # How much to push the suit's position to the left by.
            offset = sum(width[:index])

            # Get the width of the suit in question.
            suitWidth = self.getSuitWidth(suit)

            # Update the offset using the width factor.
            if widthFactor < 1:
                offset *= widthFactor
                # And do the same for the suit width.
                suitWidth *= widthFactor

            # Finally, calculate the suit's X position by taking the difference
            # between the start x and the offset and adding the width of the suit
            # divided in half.
            suitX = startX - (offset + (suitWidth / 2))

            # Handle setting their hpr based on how far away from the middle
            # they are.
            h = max(min(180 - (suitX * 3), 180 + 30), 180 - 30)

        pos.setX(suitX)

        return Point3(pos), Vec3(h, 0, 0)

    ##### Messages From The Server #####

    # These are dummy setters for non-level battles. See toon.dc for
    # more info.

    def setLevelDoId(self, levelDoId):
        pass

    def setBattleCellId(self, battleCellId):
        pass

    def setInteractivePropTrackBonus(self, trackBonus):
        # Greater than or equal to zero if this battle has a prop giving a bonus.
        self.interactivePropTrackBonus = trackBonus

    def getInteractivePropTrackBonus(self):
        # Greater than or equal to zero if this battle has a prop giving a bonus.
        return self.interactivePropTrackBonus

    def setPosition(self, x, y, z):
        self.notify.debug('setPosition() - %d %d %d' % (x, y, z))
        pos = Point3(x, y, z)
        self.setPos(pos)

    def setInitialSuitPos(self, x, y, z):
        self.initialSuitPos = Point3(x, y, z)
        # The initial suit position determines the orientation of the battle
        self.headsUp(self.initialSuitPos)

    def setZoneId(self, zoneId):
        self.zoneId = zoneId

    def setBossBattle(self, value):
        self.bossBattle = value

    def setState(self, state, timestamp):
        if self.__battleCleanedUp or state == self.getCurrentOrNextState():
            return
        self.notify.debug('setState(%s)' % state)
        self.request(state, globalClockDelta.localElapsedTime(timestamp))

    def setMembers(self, suits, suitTraps, toons, timestamp):
        if self.__battleCleanedUp:
            return

        ts = globalClockDelta.localElapsedTime(timestamp)

        ##### Update Collision Radius #####
        if hasattr(self, 'lockoutNodePath'):
            if self.lockoutNodePath:
                # Scale up the collision node by 25% for extra suits in battle past 4
                self.lockoutNodePath.setScale(1 + (max(0, (len(suits) - 4)) * 0.25))

        inPlayMovie = self.getCurrentOrNextState() == 'PlayMovie'

        ##### Update Suits #####

        # Save all of the old suit lists.
        oldsuits, oldpending, oldjoining, oldSuitsActive, oldjoiningNotPending = \
            self.suits, self.pendingSuits, self.joiningSuits, self.activeSuits, self.joiningNotPendingSuits

        # Reset the suit list.
        self.suits = []
        self.suitIndices = {}

        for suitId, state, index in suits:
            suit: DistributedSuitBase = self.cr.doId2do.get(suitId)
            if not suit:
                self.notify.warning('setMembers() - no suit in repository: %d' % suitId)
                continue

            suit.setState('Battle')
            self.suits.append(suit)
            suit.interactivePropTrackBonus = self.interactivePropTrackBonus
            try:
                suit.battleTrap
            except Exception:
                suit.battleTrap = NO_TRAP
                suit.battleTrapProp = None
                self.notify.debug('496 suit.battleTrapProp = None')
                suit.battleTrapIsFresh = 0

            suit.setBattleState(state)

            self.suitIndices[suit] = index

            # See if any new suits have joined
            if state == BattleStateEnum.JOINING:
                if suit not in oldjoining:
                    self.makeSuitJoin(suit, oldpending, oldjoining, ts)
            # See if any suits need to move from joining to pending
            elif state == BattleStateEnum.PENDING:
                if suit not in oldpending:
                    self.__makeSuitPending(suit)

        for suit in self.activeSuits:
            if suit not in oldSuitsActive:
                self.makeSuitActive(suit)
            elif self.getCurrentOrNextState() == "WaitForInput" and \
                self.adjustFsm.getCurrentState().getName() != 'Adjusting':
                self.correctActiveSuitPos(suit)

        for suit in self.joiningNotPendingSuits:
            if suit not in oldjoiningNotPending:
                self.moveSuitToActivePos(suit, ts)

        # Clear out any suits that have died
        for suit in oldsuits:
            if suit not in self.suits:
                self.needAdjustTownBattle = 1
                self.__removeSuit(suit)

        # See if any suits have traps in front of them
        index = 0
        oldSuitTraps = self.suitTraps
        self.suitTraps = suitTraps
        # Remove existing traps and load new traps
        for s in suitTraps:
            if index >= len(self.suits):
                break
            trapid = int(s)
            if trapid == 9:
                trapid = -1
            suit = self.suits[index]
            index += 1
            if (trapid == NO_TRAP or trapid != suit.battleTrap) and suit.battleTrapProp is not None:
                self.notify.debug('569 calling self.removeTrap, suit=%d' % suit.doId)
                self.removeTrap(suit)
            if trapid != NO_TRAP and suit.battleTrapProp is None and not inPlayMovie:
                self.loadTrap(suit, trapid)

        # If an old trap is gone or a new trap has appeared, adjust
        if len(oldSuitTraps) != len(self.suitTraps):
            self.needAdjustTownBattle = 1
        else:
            for i in range(len(oldSuitTraps)):
                if i >= len(self.suitTraps):
                    break
                if oldSuitTraps[i] == '9' and self.suitTraps[i] != '9' or oldSuitTraps[i] != '9' and self.suitTraps[i] == '9':
                    self.needAdjustTownBattle = 1
                    break

        ##### Update Toons #####
        currStateName = self.localToonFsm.getCurrentState().getName()

        # Save all of the old toon lists.
        oldtoons, oldjoining, oldpending, oldToonsActive, oldrunning = \
            self.toons, self.joiningToons, self.pendingToons, self.activeToons, self.runningToons

        # Reset the toon list.
        self.toons = []

        for toonId, state, _ in toons:
            toon: DistributedToonBase = self.getToon(toonId)
            if toon is None:
                self.notify.warning('setMembers() - toon not in cr!')
                continue

            self.toons.append(toon)
            if toon not in oldtoons:
                self.notify.debug('setMembers() - add toon: %d' % toon.doId)
                self.__listenForUnexpectedExit(toon)
                toon.stopLookAround()
                toon.stopSmooth()

            toon.setBattleState(state)

            # See if any new toons have joined
            if state == BattleStateEnum.JOINING:
                if toon not in oldjoining:
                    self.__makeToonJoin(toon, oldpending, oldjoining, ts)
            # See if any toons need to move from joining to pending
            elif state == BattleStateEnum.PENDING:
                if toon not in oldpending:
                    self.__makeToonPending(toon, oldpending, ts)
            # See if any toons are running
            elif state == BattleStateEnum.RUNNING:
                if toon not in oldrunning:
                    self.__makeToonRun(toon, ts)
            elif state == BattleStateEnum.JOINING_NOT_PENDING:
                if toon not in oldjoiningNotPending:
                    toon.setBattle(self)

        # Clear out any toons that have run away or died
        for toon in oldtoons:
            if toon not in self.toons:
                if self.__removeToon(toon):
                    self.notify.debug('setMembers() - local toon left battle')
                    return []

        for toon in self.activeToons:
            if toon not in oldToonsActive:
                self.makeToonActive(toon)
            # Update our local battle toon if we have it.
            if toon.isLocal():
                self.setLocalBattleToon(toon)

        # Update the town battle
        if self.activeToons != oldToonsActive or self.activeSuits != oldSuitsActive:
            self.__requestAdjustTownBattle()

        # Set the correct local toon state
        currStateName = self.localToonFsm.getCurrentState().getName()
        if self.hasLocalToon():
            self.camera.updateMembers(self.toons, self.suits)
            if base.localAvatar not in oldtoons:
                self.notify.debug('setMembers() - local toon just joined')
                messenger.send(ChatEvents.Battle_LocalToon_Joined, [self])
                if self.streetBattle == 1:
                    # Make sure the toon is in the same zone as the battle
                    base.cr.playGame.getPlace().enterZone(self.zoneId)
                self.localToonJustJoined = 1
            # Make sure we're in 'HasLocalToon'
            if currStateName != 'HasLocalToon':
                self.localToonFsm.request('HasLocalToon')
        else:
            if base.localAvatar in oldtoons:
                # Make sure the collision sphere goes away so the toon can run
                self.notify.debug('setMembers() - local toon just ran')
                # if this is a level battle, be sure to unlock the visibility
                if self.levelBattle:
                    self.unlockLevelViz()
            # Make sure we're in 'NoLocalToon'
            if currStateName != 'NoLocalToon':
                self.localToonFsm.request('NoLocalToon')

        return oldtoons

    def adjust(self, timestamp):
        if self.__battleCleanedUp:
            return
        self.notify.debug('adjust(%f) from server' % globalClockDelta.localElapsedTime(timestamp))
        self.adjustFsm.request('Adjusting', [globalClockDelta.localElapsedTime(timestamp)])

    def setMovie(self, active, toons, suits, attacks, currRound):
        if self.__battleCleanedUp:
            return
        if int(active) == 1:
            self.currRound = currRound
            self.movie.genAttackDicts(toons, suits, attacks)

    def setChosenToonAttacks(self, ids, tracks, levels, targets):
        if self.__battleCleanedUp:
            return
        self.notify.debug('setChosenToonAttacks() - (%s), (%s), (%s), (%s)' % (ids, tracks, levels, targets))
        toonIndices = []
        targetIndices = []
        sosNpcIndices = []
        unAttack = 0
        localToonInList = 0
        for i in range(len(ids)):
            track = tracks[i]
            level = levels[i]
            toon = self.findToon(ids[i])
            if toon is None or toon.getBattleState() != BattleStateEnum.ACTIVE:
                self.notify.warning('setChosenToonAttacks() - toon gone or not in battle: %d!' % ids[i])
                toonIndices.append(-1)
                tracks.append(-1)
                levels.append(-1)
                targetIndices.append(-1)
                sosNpcIndices.append(-1)
                continue
            if toon is base.localAvatar:
                localToonInList = 1
            toonIndices.append(self.activeToons.index(toon))
            if track == AttackEnum.TOON_NPC:
                sosNpcIndices.append(level)
                iou = IOURegistry[level]
                targetIndex = []
                target = self.findToon(targets[i])
                if target is not None and target.getBattleState() == BattleStateEnum.ACTIVE:
                    targetIndex.append(self.activeToons.index(target))
                else:
                    targetIndex.append(-1)

                if toon in self.activeToons and (iou.getGagTrack() == -1
                                                 or (toon and toon.hasTrackAccess(iou.getGagTrack()))):
                    index = self.activeToons.index(toon)
                    if index not in targetIndex:
                        targetIndex.append(index)
            else:
                sosNpcIndices.append(-1)
                if track == AttackEnum.TOON_PASS:
                    targetIndex = -1
                    tracks[i] = AttackEnum.TOON_PASS
                elif attackAffectsGroup(track, level):
                    # We don't specify targets for group attacks
                    targetIndex = -1
                elif track == AttackEnum.TOON_HEAL:
                    target = self.findToon(targets[i])
                    if target is not None and target.getBattleState() == BattleStateEnum.ACTIVE:
                        targetIndex = self.activeToons.index(target)
                    else:
                        targetIndex = -1
                elif track == AttackEnum.TOON_UN_ATTACK:
                    targetIndex = -1
                    tracks[i] = AttackEnum.TOON_NO_ATTACK
                    if toon is base.localAvatar:
                        unAttack = 1
                        self.choseAttackAlready = 0
                elif track == AttackEnum.TOON_NO_ATTACK:
                    targetIndex = -1
                else:
                    target = self.findSuit(targets[i])
                    if target is not None and target.getBattleState() == BattleStateEnum.ACTIVE:
                        targetIndex = self.activeSuits.index(target)
                    else:
                        targetIndex = -1
            targetIndices.append(targetIndex)

        for i in range(4 - len(ids)):
            toonIndices.append(-1)
            tracks.append(-1)
            levels.append(-1)
            targetIndices.append(-1)
            sosNpcIndices.append(-1)

        self.townBattleAttacks = (
            toonIndices,
            tracks,
            levels,
            targetIndices,
            sosNpcIndices
        )

        # Update the gui if local toon is in the battle
        if self.localToonActive() and localToonInList == 1:
            if unAttack == 1 and self.getCurrentOrNextState() == 'WaitForInput':
                # Send back to main attack panel if attack was zeroed out
                if self.townBattle.fsm.getCurrentState().getName() != 'Attack':
                    self.townBattle.setState('Attack')
            self.townBattle.updateChosenAttacks(self.townBattleAttacks[0], self.townBattleAttacks[1],
                                                self.townBattleAttacks[2], self.townBattleAttacks[3])

    def setLockIns(self, ids, lockIns):
        if self.__battleCleanedUp:
            return
        toonIndices = []
        localToonInList = 0
        for i in range(len(ids)):
            toon = self.findToon(ids[i])
            if toon is None or toon.getBattleState() != BattleStateEnum.ACTIVE:
                toonIndices.append(-1)
                continue
            if toon.isLocal():
                localToonInList = 1
            toonIndices.append(self.activeToons.index(toon))

        for i in range(4 - len(ids)):
            toonIndices.append(-1)

        for i in range(4 - len(lockIns)):
            lockIns.append(False)

        self.lockIns = (toonIndices, lockIns)

        # Update the gui if local toon is in the battle
        if self.localToonActive() and localToonInList == 1:
            self.townBattle.updateLockIns(self.lockIns[0], self.lockIns[1])

    def setTimescale(self, timescale):
        self.timescale = timescale
        for suit in self.suits:
            suit.setTimescale(timescale)
        messenger.send(self.uniqueName("battle_timescaleUpdated"), [timescale])

    def setBattleExperience(self, toonBattleExp, updatedQuests):
        if self.__battleCleanedUp:
            return
        self.movie.genRewardDicts(toonBattleExp, updatedQuests)

    def setSuitGameoverString(self, suitId, string):
        # Makes a cog speak a gameover string.
        # Called under several circumstances from the AI.
        # The cog may be removed by now, so we take a roundabout approach to find it.
        suit = base.cr.doId2do.get(suitId)
        if not suit:
            return

        self.gameoverDict[suit] = string
        taskMgr.doMethodLater(
            1.0, self.doSuitGameover,
            self.uniqueName('gameover-call'),
            extraArgs=[self.gameoverDict]
        )

    def doSuitGameover(self, checkDict):
        # Calls the gameoverDict.
        # Checks for self's attribute several times,
        # since it may be deleted by now.
        if hasattr(self, 'gameoverDict'):
            checkDict = self.gameoverDict
        for av in list(checkDict.keys()):
            if av:
                if av.dna.type != 'b' and av.dna.name in ITERATIVE_CHAT:
                    av.setChatIterative(checkDict[av], CFSpeech | CFTimeout)
                else:
                    av.setChatAbsolute(checkDict[av], CFSpeech | CFTimeout)
        if hasattr(self, 'gameoverDict'):
            self.gameoverDict = {}
        return Task.done

    ##### Functions used by setMembers() #####

    def __listenForUnexpectedExit(self, toon):
        self.accept(toon.uniqueName('disable'), self.handleUnexpectedExit, extraArgs=[toon])
        self.accept(toon.uniqueName('died'), self.__handleDied, extraArgs=[toon])

    def handleUnexpectedExit(self, toon):
        self.notify.warning('handleUnexpectedExit() - toon: %d' % toon.doId)
        self.__removeToon(toon, unexpected=1)

    def __handleDied(self, toon):
        self.notify.warning('handleDied() - toon: %d' % toon.doId)
        if toon.isLocal():
            base.localAvatar.unitesDisabled['realtime'] = True
            messenger.send(TTSCUniteStateChangedEvent)
            self.d_toonDied()
            self.cleanupBattle()

    def delayDeleteMembers(self):

        # Prevent the accidental deletion of any toons or suits by
        # storing a list of DelayDelete objects, one for each member.
        # The members may be allowed to be deleted later by clearing
        # the self.membersKeep member.

        membersKeep = []
        for t in self.toons:
            membersKeep.append(DelayDelete.DelayDelete(t, 'delayDeleteMembers'))

        for s in self.suits:
            membersKeep.append(DelayDelete.DelayDelete(s, 'delayDeleteMembers'))

        self._removeMembersKeep()
        self.membersKeep = membersKeep

    def _removeMembersKeep(self):
        if self.membersKeep:
            for delayDelete in self.membersKeep:
                delayDelete.destroy()

        self.membersKeep = None

    def __removeSuit(self, suit):
        self.notify.debug('__removeSuit(%d)' % suit.doId)
        self.suitGone = 1
        if suit.battleTrap != NO_TRAP:
            self.notify.debug('882 calling self.removeTrap, suit=%d' % suit.doId)
            self.removeTrap(suit)
        suit.battleTrap = NO_TRAP
        suit.battleTrapProp = None
        self.notify.debug('883 suit.battleTrapProp = None')
        suit.battleTrapIsFresh = 0

    def __removeToon(self, toon: DistributedToonBase, unexpected = 0):
        self.notify.debug('__removeToon(%d)' % toon.doId)
        if toon in self.toons:
            self.toons.remove(toon)

        if toon.getBattleState() == BattleStateEnum.JOINING:
            self.clearInterval(self.taskName('to-pending-toon-%d' % toon.doId))
        elif toon.getBattleState() == BattleStateEnum.RUNNING:
            self.clearInterval(self.taskName('running-%d' % toon.doId), finish=1)

        # Turn off handleUnexpectedExit()
        self.ignore(toon.uniqueName('disable'))
        self.ignore(toon.uniqueName('died'))
        self.ignore(toon.uniqueName("avatarUpdated"))
        self.toonGone = 1

        toon.cleanupBattle()
        toon.setBattleState(BattleStateEnum.INACTIVE)
        if toon.isLocal():
            self.removeLocalToon()
            self._teleportToSafeZone(toon)
            return 1
        return 0

    def removeLocalToon(self):
        self.notify.debug('removeLocalToon')
        if self._skippingRewardMovie:
            return

        messenger.send(ChatEvents.Battle_LocalToon_Left)
        if base.cr.playGame.getPlace() is not None:
            base.cr.playGame.getPlace().setState('Walk')
            camera.wrtReparentTo(base.localAvatar)
            base.localAvatar.cameraFSM.request('Orbit')
        base.localAvatar.earnedExperience = None
        self.localToonFsm.request('NoLocalToon')
        # Earlier we went and got rid of bottom chat messages, so go ahead and re-enable these.
        base.unflagScreenCells(ScreenCellFlag.inBattle, base.bottomCells)
        self.cleanupLocalBattleToon()

    def removeInactiveLocalToon(self, toon):
        self.notify.debug('removeInactiveLocalToon(%d)' % toon.doId)
        messenger.send(ChatEvents.Battle_LocalToon_Left)
        if toon in self.toons:
            self.toons.remove(toon)
        if toon.getBattleState() == BattleStateEnum.JOINING:
            self.clearInterval(self.taskName('to-pending-toon-%d' % toon.doId), finish=1)
        self.ignore(toon.uniqueName('disable'))
        self.ignore(toon.uniqueName('died'))
        base.cr.playGame.getPlace().setState('Walk')
        self.localToonFsm.request('WaitForServer')

    def __createJoinInterval(self, av, destPos, destHpr, name, ts, callback, toon = 0):
        joinTrack = Sequence()
        joinTrack.append(Func(TTEmote.globalEmote.disableAll, av, 'dbattlebase, createJoinInterval'))
        avPos = av.getPos(self)

        # Pop the avatar to the same height as the battle.
        avPos = Point3(avPos[0], avPos[1], 0.0)
        av.setShadowHeight(0)

        plist = self.buildJoinPointList(avPos, destPos, toon)
        if len(plist) == 0:
            # destPos is the closest point - just go straight there
            joinTrack.append(Func(av.headsUp, self, destPos))
            if toon == 0:
                timeToDest = self.calcSuitMoveTime(avPos, destPos)
                joinTrack.append(Func(av.loop, 'walk'))
            else:
                timeToDest = self.calcToonMoveTime(avPos, destPos)
                joinTrack.append(Func(av.loop, 'run'))
            if timeToDest > BATTLE_SMALL_VALUE:
                joinTrack.append(LerpPosInterval(av, timeToDest, destPos, other=self))
                totalTime = timeToDest
            else:
                totalTime = 0
        else:
            # Calculate the time required
            timeToPerimeter = 0
            if toon == 0:
                timeToPerimeter = self.calcSuitMoveTime(plist[0], avPos)
                timePerSegment = 10.0 / BattleBase.suitSpeed
                timeToDest = self.calcSuitMoveTime(BattleBase.posA, destPos)
            else:
                timeToPerimeter = self.calcToonMoveTime(plist[0], avPos)
                timePerSegment = 10.0 / BattleBase.toonSpeed
                timeToDest = self.calcToonMoveTime(BattleBase.posE, destPos)
            totalTime = timeToPerimeter + (len(plist) - 1) * timePerSegment + timeToDest
            if totalTime > MAX_JOIN_T:
                self.notify.warning('__createJoinInterval() - time: %f' % totalTime)

            # Create a track to move to destPos
            joinTrack.append(Func(av.headsUp, self, plist[0]))
            if toon == 0:
                joinTrack.append(Func(av.loop, 'walk'))
            else:
                joinTrack.append(Func(av.getGeomNode().setH, 0))
                joinTrack.append(Func(av.loop, 'run'))
            joinTrack.append(LerpPosInterval(av, timeToPerimeter, plist[0], other=self))
            for p in plist[1:]:
                joinTrack.append(Func(av.headsUp, self, p))
                joinTrack.append(LerpPosInterval(av, timePerSegment, p, other=self))

            joinTrack.append(Func(av.headsUp, self, destPos))
            joinTrack.append(LerpPosInterval(av, timeToDest, destPos, other=self))

        joinTrack.append(Func(av.neutralAvatar))
        joinTrack.append(Func(av.headsUp, self, Point3(0, 0, 0)))
        tval = totalTime - ts
        if tval < 0:
            tval = totalTime
        joinTrack.append(Func(TTEmote.globalEmote.releaseAll, av, 'dbattlebase, createJoinInterval'))
        joinTrack.append(Func(callback, av, tval))

        # Position the camera if local toon is the one joining the battle
        if av.isLocal():
            camTrack = Sequence()

            def setCamFov(fov):
                base.camLens.setMinFov(fov / (4. / 3.))

            camTrack.append(Func(setCamFov, self.camFov))
            camTrack.append(Func(camera.wrtReparentTo, self))
            interval = camera.posHprInterval(0.6, self.camJoinPos, self.camJoinHpr)
            camTrack.append(interval)
            return Parallel(joinTrack, camTrack, name=name)
        else:
            return Sequence(joinTrack, name=name)

    def makeSuitJoin(self, suit, pendingSuits, joiningSuits, ts):
        self.notify.debug('makeSuitJoin(%d)' % suit.doId)
        # This method is overridden in DistributedBattleFinal.py.

        # A "joining" suit has decided to join the battle, and is in
        # the process of walking to his waiting place outside the
        # battle.  When he gets there, he gets moved to the pending
        # list by the AI.

        # Pick an open pending spot
        # Building battles can have 3 pendingSuits
        spotIndex = len(pendingSuits) + len(joiningSuits)
        suit.setState('Battle')
        openSpot = self.suitPendingPoints[spotIndex]
        pos = openSpot[0]
        hpr = VBase3(openSpot[1], 0.0, 0.0)
        trackName = self.taskName('to-pending-suit-%d' % suit.doId)
        track = self.__createJoinInterval(suit, pos, hpr, trackName, ts, self._handleSuitJoinDone)
        playRate = self.timescale
        track.start(ts, playRate=playRate)

        # We can't use the membersKeep object here, because we could
        # get this message in any state.
        track.delayDelete = DelayDelete.DelayDelete(suit, 'makeSuitJoin')

        self.storeInterval(track, trackName)

    def moveSuitToActivePos(self, suit, ts):
        trackName = self.taskName('to-pending-suit-%d' % suit.doId)
        destPos, destHpr = self.getActorPosHpr(suit, self.suits)
        track = Sequence(
            self.createAdjustInterval(suit, destPos, destHpr),
            Func(self._handleSuitJoinDone, suit, ts, False),
            name=trackName
        )
        playRate = self.timescale
        track.start(ts, playRate=playRate)

        track.delayDelete = DelayDelete.DelayDelete(suit, 'moveSuitToActivePos')

        self.storeInterval(track, trackName)

    def _handleSuitJoinDone(self, suit, ts, makePending: bool = True):
        self.notify.info('suit: %d is now pending' % suit.doId)
        if self.hasLocalToon():
            self.d_joinDone(suit.doId, makePending)

    def __makeSuitPending(self, suit):
        self.notify.debug('__makeSuitPending(%d)' % suit.doId)
        self.clearInterval(self.taskName('to-pending-suit-%d' % suit.doId), finish=1)

        # A "pending" suit has walked to its correct place outside the
        # battle, and is standing there patiently waiting for the
        # round to finish.

    def _teleportToSafeZone(self, toon):
        self.notify.debug('teleportToSafeZone(%d)' % toon.doId)
        # If the toon has been to the nearest safezone before, go there
        # Otherwise teleport to the last safezone the toon visited
        hoodId = ZoneUtil.getCanonicalHoodId(self.zoneId)

        if hoodId in base.localAvatar.hoodsVisited:
            target_sz = ZoneUtil.getSafeZoneId(self.zoneId)
        else:
            target_sz = ZoneUtil.getSafeZoneId(base.localAvatar.defaultZone)

        shardId = None
        if getattr(base.cr, 'districtMgr', None):
            shardId = base.cr.districtMgr.getDrainTarget(checkDelayDeletes=True)

        base.cr.playGame.getPlace().request('TeleportOut', {'loader': ZoneUtil.getLoaderName(target_sz),
          'where': ZoneUtil.getWhereName(target_sz, 1),
          'how': 'TeleportIn',
          'hoodId': target_sz,
          'zoneId': target_sz,
          'shardId': shardId,
          'avId': -1,
          'battle': 1})

    def __makeToonJoin(self, toon, pendingToons, joiningToons, ts):
        self.notify.debug('__makeToonJoin(%d)' % toon.doId)
        # Move toon into the wait position
        # Add toon to pending list
        # Pick an open pending spot
        spotIndex = len(pendingToons) + len(joiningToons)
        openSpot = self.toonPendingPoints[spotIndex]
        pos = openSpot[0]
        hpr = VBase3(openSpot[1], 0.0, 0.0)
        trackName = self.taskName('to-pending-toon-%d' % toon.doId)
        track = self.__createJoinInterval(toon, pos, hpr, trackName, ts, self.__handleToonJoinDone, toon=1)

        if not toon.isLocal():
            # Ensure the anim state for the toon is off so it doesn't
            # get set to off mid-interval
            toon.request('Off')

        playRate = self.timescale
        track.start(ts, playRate=playRate)

        # We can't use the membersKeep object here, because we could
        # get this message in any state.
        track.delayDelete = DelayDelete.DelayDelete(toon, '__makeToonJoin')
        self.storeInterval(track, trackName)

    def __handleToonJoinDone(self, toon, ts):
        self.notify.debug('__handleToonJoinDone() - pending: %d' % toon.doId)
        if self.hasLocalToon():
            self.d_joinDone(toon.doId)

    def __makeToonPending(self, toon, pendingToons, ts):
        self.notify.debug('__makeToonPending(%d)' % toon.doId)
        self.clearInterval(self.taskName('to-pending-toon-%d' % toon.doId), finish=1)

        # We might have recently joined, so joiningToons would be empty
        spotIndex = len(pendingToons)

        openSpot = self.toonPendingPoints[spotIndex]
        pos = openSpot[0]
        hpr = VBase3(openSpot[1], 0.0, 0.0)
        toon.neutralAvatar()
        toon.setPosHpr(self, pos, hpr)
        toon.setGeomNodeH(0)

        # Start playing the cinematic version of the movie
        # if base.localAvatar == toon:
        #     currStateName = self.fsm.getCurrentState().getName()

    def correctActiveSuitPos(self, suit: DistributedSuitBase) -> None:
        suitPos, suitHpr = self.getActorPosHpr(suit, self.activeSuits)
        if not suit.isLured:
            suit.setPosHpr(self, suitPos, suitHpr)
        else:
            spos = Point3(suitPos[0], suitPos[1] - MovieUtil.SUIT_LURE_DISTANCE, suitPos[2])
            suit.setPosHpr(self, spos, suitHpr)

    def getActiveSuitPosHpr(self, suit: DistributedSuitBase, overrideLureStatus: bool = None, suits: list = None):
        suitPos, suitHpr = self.getActorPosHpr(suit, suits or self.activeSuits)
        suitLured = suit.isLured
        if overrideLureStatus is not None:
            suitLured = overrideLureStatus
        if not suitLured:
            return suitPos, suitHpr
        else:
            spos = Point3(suitPos[0], suitPos[1] - MovieUtil.SUIT_LURE_DISTANCE, suitPos[2])
            return spos, suitHpr

    def makeSuitActive(self, suit: DistributedSuitBase) -> None:
        self.correctActiveSuitPos(suit)

        suit.resetBattle()
        suit.setBattle(self)
        suit.requestApplyAllVisualEffects()

        self.accept(suit.uniqueName("avatarUpdated"), self.__requestAdjustTownBattle, extraArgs=[True])

    def makeToonActive(self, toon: DistributedToonBase) -> None:
        toonPos, toonHpr = self.getActorPosHpr(toon)
        toon.setPosHpr(self, toonPos, toonHpr)
        toon.neutralAvatar()
        toon.setGeomNodeH(0)

        toon.resetBattle()
        toon.setBattle(self)
        toon.requestApplyAllVisualEffects()
        # Local toon might just have become active, so we need to pop up GUIs
        if toon.isLocal():
            if self.getCurrentOrNextState() == 'WaitForInput' and self.localToonJustJoined == 1:
                self.notify.debug('makeAvsActive() - local toon just joined')
                self.__enterLocalToonWaitForInput()
                self.localToonJustJoined = 0
                self.startTimer()

        self.accept(toon.uniqueName("avatarUpdated"), self.__toonAvatarUpdated, extraArgs=[toon])

    def __toonAvatarUpdated(self, toon):
        self.__requestAdjustTownBattle(True)
        if toon.isLocal():
            self.updateInvMods()

    def __makeToonRun(self, toon: DistributedToonBase, ts):
        self.notify.debug('__makeToonRun(%d)' % toon.doId)
        # Clean up their battle avatar, since they are gone gone
        toon.cleanupBattle()
        toon.setBattleState(BattleStateEnum.RUNNING)

        # We need to trigger adjust
        self.toonGone = 1
        self.__stopTimer()
        if self.localToonRunning():
            self.townBattle.setState('Off')

        # We can't use the membersKeep object here, because we could
        # get this message in any state.
        runMTrack = MovieUtil.getToonTeleportOutInterval(toon)
        runName = self.taskName('running-%d' % toon.doId)
        self.notify.debug('duration: %f' % runMTrack.getDuration())
        runMTrack.start(ts)
        runMTrack.delayDelete = DelayDelete.DelayDelete(toon, '__makeToonRun')
        self.storeInterval(runMTrack, runName)

    def getToon(self, toonId, warn=True):
        if toonId in self.cr.doId2do:
            return self.cr.doId2do[toonId]
        elif warn:
            self.notify.warning(f'getToon() - toon: {toonId} not in repository!')
        return None

    def getToonIndex(self, toon):
        if toon.getBattleState() == BattleStateEnum.ACTIVE:
            return self.activeToons.index(toon)
        else:
            self.notify.warning(f'Toon {toon} was not in the battle. Could not find index.')
            return None

    def getSuit(self, suitId):
        if suitId in self.cr.doId2do:
            return self.cr.doId2do[suitId]
        return None

    ##### Messages To The Server #####

    def d_toonRequestJoin(self, toonId, pos):
        self.notify.debug('network:toonRequestJoin()')
        self.sendUpdate('toonRequestJoin', [pos[0], pos[1], pos[2]])

    def d_toonRequestRun(self):
        self.notify.debug('network:toonRequestRun()')
        self.sendUpdate('toonRequestRun', [])

    def d_toonDied(self):
        self.notify.debug('network:toonDied()')
        self.sendUpdate('toonDied', [])

    def d_faceOffDone(self, toonId):
        self.notify.debug('network:faceOffDone()')
        self.sendUpdate('faceOffDone', [])

    def d_adjustDone(self):
        self.notify.debug('network:adjustDone()')
        self.sendUpdate('adjustDone', [])

    def d_timeout(self):
        self.notify.debug('network:timeout()')
        self.sendUpdate('timeout', [])

    def d_movieDone(self):
        self.notify.debug('network:movieDone()')
        self.sendUpdate('movieDone', [])

    def d_rewardDone(self, toonId):
        self.notify.debug('network:rewardDone()')
        self.sendUpdate('rewardDone', [])

    def d_joinDone(self, avId, makePending: bool = True):
        self.notify.debug('network:joinDone(%d)' % avId)
        self.sendUpdate('joinDone', [avId, makePending])

    def d_requestAttack(self, track, level, av, lockIn=False):
        # Check auto lock in settings; lockIn is True usually means to
        # insta-lock, but if toons already have auto-lock then do the opposite.
        if settings['auto-lock-in'] == 2:
            lockIn = not lockIn
        elif settings['auto-lock-in'] == 1 and len(self.toons) == 1:
            lockIn = not lockIn

        self.notify.debug('network:requestAttack(%d, %d, %d, %s)' % (track, level, av, lockIn))
        self.sendUpdate('requestAttack', [track, level, av, lockIn])

    def d_requestLockIn(self, lockIn):
        self.notify.debug('network:requestLockIn(%d)' % lockIn)
        self.sendUpdate('requestLockIn', [lockIn])

    def d_requestCounterfeit(self, gagTrack, gagLevel):
        self.notify.debug('network:requestCounterfeit(%d, %d)' % (gagTrack, gagLevel))
        self.sendUpdate('requestCounterfeit', [gagTrack, gagLevel])

    def d_toonRequestSurrender(self):
        self.notify.debug('network:toonRequestSurrender()')
        self.sendUpdate('toonRequestSurrender', [])

    def toonUsedCounterfeit(self, avId, track, level):
        if not self.localToonActive():
            return

        toon = self.getToon(avId)
        if not toon:
            return
        if toon not in self.toons:
            return
        if not self.townBattle:
            return

        self.townBattle.playCounterfeitAnimation(toon, track, level)

    # Each state will have an enter function, an exit function,
    # and a datagram handler, which will be set during each enter function.

    # Specific State functions

    ##### Off state #####

    def enterOff(self, ts=0):
        self.localToonFsm.requestFinalState()

    def exitOff(self):
        pass

    ##### FaceOff state #####

    def enterFaceOff(self, ts=0):
        pass

    def exitFaceOff(self):
        pass

    ##### WaitForJoin state #####

    def enterWaitForJoin(self, ts=0):
        self.notify.debug('enterWaitForJoin()')

    def exitWaitForJoin(self):
        pass

    ##### WaitForInput state #####

    def __enterLocalToonWaitForInput(self):
        self.notify.debug('enterLocalToonWaitForInput()')
        messenger.send('DistributedBattleBase-enterLocalToonWaitForInput', [self])
        # Move the camera into position
        # (assumes the camera is a child of the battle)
        self.camera.updateMembers(self.toons, self.suits)
        self.camera.enterWaitForInput()
        # No arrows - they just get in the way
        NametagGlobals.setMasterArrowsOn(0)
        # Toon panels will cover up the entire bottom of the screen, so disallow those chat messages.
        base.flagScreenCells(ScreenCellFlag.inBattle, base.bottomCells)
        base.cr.gameGui.expBar.hide()
        # Put local toon into 'Attack' state
        if self.townBattle.fsm.getCurrentState().getName() == 'Off':
            self.townBattle.setState('Attack')
        # Tell town battle to accept window resize events for scaling purposes.
        self.townBattle.updatePanelsForAspectRatio()
        self.townBattle.accept(
            self.townBattle.resizeEvent, self.townBattle.updatePanelsForAspectRatio, extraArgs=[])
        self.townBattle.accept(
            GagInventory.InventoryScalingChangedEvent, self.townBattle.updatePanelsForAspectRatio, extraArgs=[])
        # Begin listening for 'Attack' responses
        self.accept(self.localToonBattleEvent, self.__handleLocalToonBattleEvent)

    def startTimer(self, ts=0):
        self.notify.debug('startTimer()')
        # Don't run timer on tutorial
        if self.townBattle.tutorialFlag:
            return

        TURN_DURATION = self.clientInputTimeout / self.timescale
        if ts >= TURN_DURATION:
            self.notify.warning('startTimer() - ts: %f timeout: %f' % (ts, TURN_DURATION))
            self.__timedOut()
            return
        # Start the timer
        self.timer.startCallback(TURN_DURATION - ts, self.__timedOut)
        # Clean up our local time running out track if it exists
        if self.townBattle.timeRunningOutTrack:
            self.townBattle.timeRunningOutTrack.finish()
        # Start a task that sends out the timer values ten times a second
        # I know it is a one second timer, but by supersampling, it appears
        # to be smooth.
        timeTask = Task.loop(Task(self.__countdown), Task.pause(0.1))
        taskMgr.add(timeTask, self.timerCountdownTaskName)

    def __stopTimer(self):
        self.notify.debug('__stopTimer()')
        self.timer.stop()
        taskMgr.remove(self.timerCountdownTaskName)

    def __countdown(self, task):
        if hasattr(self.townBattle, 'timer'):
            self.townBattle.updateTimer(self.timescale, int(self.timescale * self.timer.getT()), self.runoutTime)
        else:
            self.notify.warning('__countdown has tried to update a timer that has been deleted. Stopping timer')
            self.__stopTimer()
        return Task.done

    def enterWaitForInput(self, ts=0):
        self.notify.debug('enterWaitForInput()')
        self.choseAttackAlready = 0
        if self.localToonActive():
            self.__enterLocalToonWaitForInput()
            self.startTimer(ts)
        if self.needAdjustTownBattle == 1:
            self.__adjustTownBattle()

    def exitWaitForInput(self):
        self.notify.debug('exitWaitForInput()')
        if self.localToonActive():
            messenger.send('DistributedBattleBase-exitLocalToonWaitForInput')
            self.townBattle.setState('Off')
            base.camLens.setMinFov(self.camFov / (4. / 3.))
            self.ignore(self.localToonBattleEvent)
            self.__stopTimer()
            self.camera.finishSequence()

    def __handleLocalToonBattleEvent(self, response):
        mode = response['mode']
        noAttack = 0
        lockIn = response.get('lockIn', False)
        if mode == 'Attack':
            self.notify.debug('got an attack')
            track = response['track']
            level = response['level']
            target = response['target']
            targetId = target
            if track == AttackEnum.TOON_HEAL and not levelAffectsGroup(AttackEnum.TOON_HEAL, level):
                if 0 <= target < len(self.activeToons):
                    targetId = self.activeToons[target].doId
                else:
                    self.notify.warning('invalid toon target: %d' % target)
                    track = -1
                    level = -1
                    targetId = -1
            elif track == AttackEnum.TOON_HEAL and len(self.activeToons) == 1:
                self.notify.warning('invalid group target for heal')
                track = -1
                level = -1
            elif not attackAffectsGroup(track, level):
                # Maybe we haven't chosen a target yet, but we still
                # want to notify the other members of the battle which
                # track we're choosing.
                if 0 <= target < len(self.activeSuits):
                    targetId = self.activeSuits[target].doId
                else:
                    target = -1
            if len(self.luredSuits) > 0:
                if (
                    track == AttackEnum.TOON_TRAP
                    or track == AttackEnum.TOON_LURE
                    and not levelAffectsGroup(AttackEnum.TOON_LURE, level)
                ):
                    if target != -1:
                        suit = self.findSuit(targetId)
                        if suit in self.luredSuits:
                            self.notify.warning('Suit: %d was lured!' % targetId)
                            track = -1
                            level = -1
                            targetId = -1
                elif track == AttackEnum.TOON_LURE:
                    if levelAffectsGroup(AttackEnum.TOON_LURE, level) and len(self.activeSuits) == len(self.luredSuits):
                        self.notify.warning('All suits are lured!')
                        track = -1
                        level = -1
                        targetId = -1
            if track == AttackEnum.TOON_TRAP:
                if target != -1:
                    if attackAffectsGroup(track, level):
                        pass
                    else:
                        suit = self.findSuit(targetId)
                        if suit.battleTrap != NO_TRAP:
                            self.notify.warning('Suit: %d was already trapped!' % targetId)
                            track = -1
                            level = -1
                            targetId = -1
            self.targetId = targetId
            self.lockIn = lockIn
            self.d_requestAttack(track, level, targetId, lockIn)
        elif mode == 'Run':
            self.notify.debug('got a run')
            self.d_toonRequestRun()
        elif mode == 'NPCSOS':
            targetId = response['target']
            level = response['level']
            self.notify.debug('got an NPCSOS for friend: %d' % targetId)
            self.d_requestAttack(AttackEnum.TOON_NPC, level, targetId, lockIn)
        elif mode == 'Pass':
            targetId = response['id']
            self.notify.debug('got a Pass')
            self.d_requestAttack(AttackEnum.TOON_PASS, -1, -1, lockIn)
        elif mode == 'UnAttack':
            self.d_requestAttack(AttackEnum.TOON_UN_ATTACK, -1, -1)
            noAttack = 1
        elif mode == 'Fire':
            target = response['target']
            if 0 <= target < len(self.activeSuits):
                targetId = self.activeSuits[target].doId
            else:
                self.notify.warning('invalid suit target: %d' % target)
                targetId = -1
            self.d_requestAttack(AttackEnum.TOON_FIRE, -1, targetId, lockIn)
        elif mode == 'Sue':
            target = response['target']
            if 0 <= target < len(self.activeSuits):
                targetId = self.activeSuits[target].doId
            else:
                self.notify.warning('invalid suit target: %d' % target)
                targetId = -1
            self.d_requestAttack(AttackEnum.TOON_SUE, -1, targetId, lockIn)
        elif mode == 'Counterfeit':
            gagTrack, gagLevel = response['gagTrack'], response['gagLevel']
            self.d_requestCounterfeit(gagTrack, gagLevel)
            noAttack = 1
        elif mode == 'LockIn':
            lockIn = response['lockIn']
            self.d_requestLockIn(lockIn)
        elif mode == 'GagChange':
            track = response['track']
            level = response['level']
            self.d_requestAttack(track, level, self.targetId, self.lockIn)
        elif mode == 'Surrender':
            self.d_toonRequestSurrender()
        else:
            self.notify.warning('unknown battle response')
            return
        if noAttack == 1:
            self.choseAttackAlready = 0
        else:
            self.choseAttackAlready = 1

    def __timedOut(self):
        if self.choseAttackAlready == 1:
            return
        self.notify.debug('WaitForInput timed out')
        if self.localToonActive():
            self.notify.debug('battle timed out')
            self.d_timeout()

    ##### MakeMovie state #####

    def enterMakeMovie(self, ts = 0):
        self.notify.debug('enterMakeMovie()')

    def exitMakeMovie(self):
        pass

    ##### PlayMovie state #####

    def enterPlayMovie(self, ts):
        self.notify.debug('enterPlayMovie()')
        self.delayDeleteMembers()
        if self.hasLocalToon():
            NametagGlobals.setMasterArrowsOn(0)
            if self.townBattle.timeRunningOutTrack and self.townBattle.timeRunningOutTrack.isPlaying():
                self.townBattle.timeRunningOutTrack.finish()
            self.townBattle.ignore(self.townBattle.resizeEvent)
            self.townBattle.ignore(GagInventory.InventoryScalingChangedEvent)

        self.movieActive = True
        self.movie.play(ts, self.__handleMovieDone, timescale=self.timescale)

    def checkLocalToonSad(self):
        if not self.hasLocalToon():
            return False

        if base.localAvatar.getHp() < 0:
            self.cleanupBattle()

    def __handleMovieDone(self):
        self.notify.debug('__handleMovieDone()')
        if self.hasLocalToon():
            self.d_movieDone()
        self.movieActive = False
        self.movie.reset()

    def exitPlayMovie(self):
        self.notify.debug('exitPlayMovie()')
        self.movie.reset(finish=1)
        self._removeMembersKeep()
        self.townBattleAttacks = ([-1, -1, -1, -1],
                                  [-1, -1, -1, -1],
                                  [-1, -1, -1, -1],
                                  [0,  0,  0,  0])

    ##### Reward state #####

    ##### Resume state #####

    #########################
    ##### LocalToon ClassicFSM #####
    #########################

    def hasLocalToon(self):
        return base.localAvatar in self.toons

    def localToonPendingOrActive(self):
        return self.hasLocalToon() and \
            base.localAvatar.getBattleState() in (BattleStateEnum.PENDING, BattleStateEnum.ACTIVE)

    def localToonActive(self):
        return self.hasLocalToon() and \
            base.localAvatar.getBattleState() == BattleStateEnum.ACTIVE

    def localToonActiveOrRunning(self):
        return self.hasLocalToon() and \
            base.localAvatar.getBattleState() in (BattleStateEnum.ACTIVE, BattleStateEnum.RUNNING)

    def localToonRunning(self):
        return self.hasLocalToon() and \
            base.localAvatar.getBattleState() == BattleStateEnum.RUNNING

    def enterHasLocalToon(self):
        self.notify.debug('enterHasLocalToon()')
        # Put local toon into battle mode
        if base.cr.playGame.getPlace() is not None:
            if localAvatar and hasattr(localAvatar, 'inventory') and localAvatar.inventory:
                localAvatar.inventory.setInteractivePropTrackBonus(self.interactivePropTrackBonus)
            base.cr.playGame.getPlace().setState('Battle', self.localToonBattleEvent)

    def exitHasLocalToon(self):
        self.notify.debug('exitHasLocalToon()')
        # Ignore any responses from the battle interface
        self.ignore(self.localToonBattleEvent)
        self.__stopTimer()

        # restore the inventory to not having a prop bonus
        if localAvatar and hasattr(localAvatar, 'inventory') and localAvatar.inventory:
            localAvatar.inventory.setInteractivePropTrackBonus(-1)

        # Restore the camera parameters
        stateName = None
        place = base.cr.playGame.getPlace()
        print("place:", type(place).__name__)
        print("place state:",
              place.getCurrentOrNextState() if hasattr(place, 'getCurrentOrNextState') else getattr(place, 'state',
                                                                                                    '?'))
        print("has enterBattle:", hasattr(place, 'enterBattle'))
        print("controlManager enabled:",
              base.localAvatar.controlManager.isEnabled if hasattr(base.localAvatar, 'controlManager') else '?')
        if place:
            stateName = place.getCurrentOrNextState()
        if stateName == 'died':
            # If we died in the middle of the round, stop the battle
            # animation and put the camera somewhere good for watching
            # myself go sad.
            self.movie.reset()
            camera.reparentTo(render)
            camera.setPosHpr(localAvatar, 5.2, 5.45, localAvatar.getHeight() * 0.66, 131.5, 3.6, 0)
        else:
            # Otherwise, reparent the camera back to the toon where it
            # belongs (most of the time).
            base.localAvatar.cameraFSM.request('Off')
            camera.wrtReparentTo(base.localAvatar)
            base.localAvatar.cameraFSM.request('Orbit')
            messenger.send('localToonLeftBattle')
        base.camLens.setMinFov(settings['fieldofview'] / (4. / 3.))

    ##### NoLocalToon state #####

    def enterNoLocalToon(self):
        self.notify.debug('enterNoLocalToon()')

    def exitNoLocalToon(self):
        pass

    def setSkippingRewardMovie(self):
        self._skippingRewardMovie = True

    ##### WaitForServer state #####

    def enterWaitForServer(self):
        self.notify.debug('enterWaitForServer()')

    def exitWaitForServer(self):
        pass

    ######################
    ##### Adjust ClassicFSM #####
    ######################

    def createAdjustInterval(self, av, destPos, destHpr, toon = 0, run = 0):
        # Just do everything at suit speed since toons are walking
        if run == 1:
            adjustTime = self.calcToonMoveTime(destPos, av.getPos(self))
        else:
            adjustTime = self.calcSuitMoveTime(destPos, av.getPos(self))
        self.notify.debug('creating adjust interval for: %d' % av.doId)
        adjustTrack = Sequence()
        if run == 1:
            adjustTrack.append(Func(av.loop, 'run'))
        else:
            adjustTrack.append(Func(av.loop, 'walk'))
        adjustTrack.append(Func(av.headsUp, self, destPos))
        adjustTrack.append(LerpPosInterval(av, adjustTime, destPos, other=self))
        adjustTrack.append(Func(av.setHpr, self, destHpr))
        adjustTrack.append(Func(av.neutralAvatar))
        return adjustTrack

    def __adjust(self, ts, callback):
        self.notify.info(f'__adjust({ts})')
        adjustTrack = Parallel()
        # See if we need to adjust suits
        if len(self.pendingSuits) > 0 or self.suitGone == 1:
            self.suitGone = 0
            index = 0
            activeSuits = self.activeSuits
            pendingSuits = self.pendingSuits
            allSuits = sorted(activeSuits + pendingSuits, key=lambda suit: self.suitIndices.get(suit, 0))

            for suit in activeSuits:
                # See if already in the right position
                # We might move sideways if someone died next to us
                point = self.getSuitBattlePosHpr(suit, allSuits)
                pos = suit.getPos(self)
                destPos = point[0]
                if suit.isLured:
                    destPos = Point3(destPos[0], destPos[1] - MovieUtil.SUIT_LURE_DISTANCE, destPos[2])
                if pos != destPos:
                    destHpr = point[1]
                    adjustTrack.append(self.createAdjustInterval(suit, destPos, destHpr))
                index += 1

            for suit in pendingSuits:
                point = self.getSuitBattlePosHpr(suit, allSuits)
                destPos, destHpr = point
                adjustTrack.append(self.createAdjustInterval(suit, destPos, destHpr))
                index += 1

        # See if we need to adjust toons
        if len(self.pendingToons) > 0 or self.toonGone == 1:
            self.toonGone = 0
            numToons = len(self.pendingToons) + len(self.activeToons) - 1
            index = 0
            for toon in self.activeToons:
                # See if already in the right position
                # We might move sideways if someone died next to us
                point = self.toonPoints[numToons][index]
                pos = toon.getPos(self)
                destPos = point[0]
                if pos != destPos:
                    destHpr = VBase3(point[1], 0.0, 0.0)
                    adjustTrack.append(self.createAdjustInterval(toon, destPos, destHpr))
                index += 1

            for toon in self.pendingToons:
                point = self.toonPoints[numToons][index]
                destPos = point[0]
                destHpr = VBase3(point[1], 0.0, 0.0)
                adjustTrack.append(self.createAdjustInterval(toon, destPos, destHpr))
                index += 1

        if len(adjustTrack) > 0:
            self.notify.debug('creating adjust multitrack')
            e = Func(self.__handleAdjustDone)
            track = Sequence(adjustTrack, e, name=self.adjustName)
            self.storeInterval(track, self.adjustName)
            playRate = self.timescale
            track.start(ts, playRate=playRate)
        else:
            self.notify.warning('adjust() - nobody needed adjusting')
            self.__adjustDone()

    def __handleAdjustDone(self):
        self.notify.debug('__handleAdjustDone() - client adjust finished')
        self.clearInterval(self.adjustName)
        self.__adjustDone()

    def __stopAdjusting(self):
        self.notify.debug('__stopAdjusting()')
        self.clearInterval(self.adjustName)
        if self.adjustFsm.getCurrentState().getName() == 'Adjusting':
            self.adjustFsm.request('NotAdjusting')

    def __requestAdjustTownBattle(self, forceUpdate=False):
        self.notify.debug('__requestAdjustTownBattle() curstate = %s' % self.getCurrentOrNextState())
        if self.getCurrentOrNextState() == 'WaitForInput':
            self.__adjustTownBattle(forceUpdate)
        elif forceUpdate:
            self.needAdjustTownBattle = 2
        else:
            self.needAdjustTownBattle = 1

    def __adjustTownBattle(self, forceUpdate=False):
        self.notify.debug('__adjustTownBattle()')
        forceUpdate = forceUpdate or self.needAdjustTownBattle == 2

        if self.localToonActive() and len(self.activeSuits) > 0:
            self.notify.debug('__adjustTownBattle() - adjusting town battle')
            luredIndices = []
            trappedIndices = []
            suedIndices = []
            untouchableToonIndices = []
            untouchableSuitIndices = []
            untouchableByTrapSuitIndices = []

            # Update lured and sued vars
            self.luredSuits = []
            self.suedSuits = []
            self.untouchableSuits = []
            self.untouchableByTrapSuits = []

            for i, suit in enumerate(self.activeSuits):
                suit: DistributedSuit
                if suit.getStatusEffectOfId(SEE.EFFECT_SUIT_LURED):
                    self.luredSuits.append(suit)

                    # Save the lured indices.
                    luredIndices.append(i)
                if suit.getStatusEffectOfId(SEE.EFFECT_SUIT_SUED):
                    self.suedSuits.append(suit)

                    # Save the sued indices.
                    suedIndices.append(i)
                untouchableEffect = suit.getStatusEffectOfType(UntouchableStatusEffect)
                if untouchableEffect:
                    self.untouchableSuits.append(suit)

                    # Save the untouchable indices.
                    untouchableSuitIndices.append(i)
                    if not untouchableEffect.canBeTrapped():
                        self.untouchableByTrapSuits.append(suit)
                        untouchableByTrapSuitIndices.append(i)
                    suit.isUntouchable = True
                else:
                    suit.isUntouchable = False

                # Save the trapped indices.
                if suit.battleTrap != NO_TRAP:
                    trappedIndices.append(i)

            # Determine the indices of untouchable toons
            for i, toon in enumerate(self.activeToons):
                if toon.getStatusEffectOfType(UntouchableStatusEffect):
                    untouchableToonIndices.append(i)

            self.townBattle.adjustCogsAndToons(
                self.activeSuits, luredIndices, trappedIndices, suedIndices,
                self.activeToons, self.afkToons, self, untouchableToonIndices,
                untouchableSuitIndices, untouchableByTrapSuitIndices, forceUpdate
            )

            # It is possible that townBattleAttacks hasn't been set yet, if
            # we haven't finished an attack round.
            if hasattr(self, 'townBattleAttacks'):
                self.townBattle.updateChosenAttacks(self.townBattleAttacks[0], self.townBattleAttacks[1],
                                                    self.townBattleAttacks[2], self.townBattleAttacks[3])
            # We won't have lock ins if no one has locked in or haven't finished a round
            if hasattr(self, 'lockIns'):
                self.townBattle.updateLockIns(self.lockIns[0], self.lockIns[1])

            self.neutralSuits()

        self.needAdjustTownBattle = 0

    def __adjustDone(self):
        self.notify.debug('__adjustDone()')
        # Tell the server we're done adjusting
        if self.hasLocalToon():
            self.d_adjustDone()

        self.adjustFsm.request('NotAdjusting')

    ##### Adjusting state #####

    def enterAdjusting(self, ts):
        self.notify.debug('enterAdjusting()')
        if self.localToonActive():
            self.__stopTimer()

        self.delayDeleteMembers()
        self.__adjust(ts, self.__handleAdjustDone)

    def exitAdjusting(self):
        self.notify.debug('exitAdjusting()')
        self.finishInterval(self.adjustName)
        self._removeMembersKeep()
        currStateName = self.getCurrentOrNextState()
        if currStateName == 'WaitForInput' and self.localToonActive():
            self.startTimer()

    ##### NotAdjusting state #####

    def enterNotAdjusting(self):
        self.notify.debug('enterNotAdjusting()')

    def exitNotAdjusting(self):
        pass

    # Misc

    def visualize(self):
        try:
            self.isVisualized
        except Exception:
            self.isVisualized = 0

        if self.isVisualized:
            self.vis.removeNode()
            del self.vis
            self.detachNode()
            self.isVisualized = 0
        else:
            lsegs = LineSegs()
            lsegs.setColor(0.5, 0.5, 1, 1)
            lsegs.moveTo(0, 0, 0)
            for p in BattleBase.allPoints:
                lsegs.drawTo(p[0], p[1], p[2])

            p = BattleBase.allPoints[0]
            lsegs.drawTo(p[0], p[1], p[2])
            self.vis = self.attachNewNode(lsegs.create())
            self.reparentTo(render)
            self.isVisualized = 1

    ##### Battle Trigger / Lockout collisions--not used in building battles #####

    def setupCollisions(self, name):
        self.lockout = CollisionTube(0, 0, 0, 0, 0, 9, 9)
        lockoutNode = CollisionNode(name)
        lockoutNode.addSolid(self.lockout)
        lockoutNode.setCollideMask(ToontownGlobals.WallBitmask)
        self.lockoutNodePath = self.attachNewNode(lockoutNode)
        # By default don't activate collision sphere
        self.lockoutNodePath.detachNode()

        # The lockout bubble should always be tangible; we never want
        # Toons walking around inside the battle.

        # Tubby's note: you really screwed that one up, didn't you guys.

    def removeCollisionData(self):
        del self.lockout
        self.lockoutNodePath.removeNode()
        del self.lockoutNodePath

    def enableCollision(self):
        self.lockoutNodePath.reparentTo(self)
        if len(self.toons) < 4:
            self.accept(self.getCollisionName(), self.__handleLocalToonCollision)

    def __handleLocalToonCollision(self, collEntry):
        self.notify.debug('localToonCollision')
        if self.getCurrentOrNextState() == 'Off':
            self.notify.debug('ignoring collision in Off state')
            return
        if not base.localAvatar.wantBattles:
            return
        if self.townBattle and self.townBattle.isStreet and base.localAvatar.isStunned:
            # Local avatar may be "stunned" as they receive i-frames after exiting a cog building
            return
        if self._skippingRewardMovie:
            return
        base.cr.playGame.getPlace().setState('WaitForBattle')
        toon = base.localAvatar
        self.d_toonRequestJoin(toon.doId, toon.getPos(self))
        base.localAvatar.preBattleHpr = base.localAvatar.getHpr(render)
        self.localToonFsm.request('WaitForServer')
        self.onWaitingForJoin()

    def onWaitingForJoin(self):
        # This is here for level battle to override.
        pass

    def denyLocalToonJoin(self):
        self.notify.debug('denyLocalToonJoin()')

        place = self.cr.playGame.getPlace()
        if place.getCurrentOrNextState() == 'WaitForBattle':
            place.setState('walk')

        self.localToonFsm.request('NoLocalToon')

    def disableCollision(self):
        self.ignore(self.getCollisionName())
        self.lockoutNodePath.detachNode()

    def openBattleCollision(self):
        if not self.hasLocalToon():
            self.enableCollision()

    def closeBattleCollision(self):
        self.ignore(self.getCollisionName())

    def getCollisionName(self):
        return 'enter' + self.lockoutNodePath.getName()

    def cleanupLocalBattleToon(self):
        base.localAvatar.inventory.clearAllButtonModifiers()
        # Clear out our battle unite disable.
        base.localAvatar.unitesDisabled['battle'] = False
        base.localAvatar.inventory.updateBattle(None)
        base.localAvatar.inventory.adjustSurrenderedToons()
        messenger.send(TTSCUniteStateChangedEvent)

    def beginInteractiveCutscene(self):
        raise Exception("Called to create an interactive cutscene in the base class.")

    def setGagOrder(self, gagOrder: List[AttackEnum]):
        self.gagOrder = gagOrder
        if self.localToonActive():
            base.localAvatar.inventory.refreshGagOrder()

    def getGagOrder(self):
        return self.gagOrder

    def setNumSurrendered(self, numSurrendered, maxSurrendered, surrenderedToons):
        self.numSurrendered = numSurrendered
        self.maxSurrendered = maxSurrendered
        self.surrenderedToons = surrenderedToons
        if self.localToonActive():
            base.localAvatar.inventory.adjustSurrenderedToons(self.numSurrendered, self.maxSurrendered)
            if self.townBattle:
                self.townBattle.setSurrenderedToons(surrenderedToons)

    def sendMovieEvent(self, eventId, sequence=None, **eventKwargs):
        self.battleMovieListener.sendEvent(eventId, sequence=sequence, **eventKwargs)

    def addMovieHook(self, eventObj, eventId, eventFunc, lastsOnce=False):
        self.battleMovieListener.addHook(eventObj, eventId, eventFunc, lastsOnce=lastsOnce)

    def removeMovieHooks(self, eventObj):
        if self.battleMovieListener:
            self.battleMovieListener.removeHooks(eventObj)

    """
    Local messenger
    """

    @property
    def msg_updateTimescale(self):
        return self.uniqueName('updateTimescale')

    """
    Properties
    """

    @property
    def activeToons(self):
        return [toon for toon in self.toons if toon.getBattleState() == BattleStateEnum.ACTIVE]

    @property
    def pendingToons(self):
        return [toon for toon in self.toons if toon.getBattleState() == BattleStateEnum.PENDING]

    @property
    def joiningToons(self):
        return [toon for toon in self.toons if toon.getBattleState() == BattleStateEnum.JOINING]

    @property
    def runningToons(self):
        return [toon for toon in self.toons if toon.getBattleState() == BattleStateEnum.RUNNING]
