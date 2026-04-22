import copy
import math
import random
from toontown.suit import DistributedSuitBase
from toontown.suit import DistributedSuitPlanner
from toontown.suit import Suit
from toontown.suit import SuitBase
from toontown.suit import SuitDialog
from toontown.suit import SuitTimings
from toontown.battle import SuitBattleGlobals
from toontown.battle import MovieUtil
from toontown.battle import PlayByPlayText
from direct.directnotify import DirectNotifyGlobal
from direct.directtools.DirectGeometry import CLAMP
from direct.distributed.ClockDelta import *
from otp.otpbase import OTPLocalizerEnglish
from direct.fsm import ClassicFSM, State
from direct.fsm import State
from direct.interval.IntervalGlobal import *
from direct.task import Task
from pandac.PandaModules import *
from panda3d.core import TextureStage
from otp.avatar import DistributedAvatar
from otp.otpbase import OTPLocalizer
from toontown.battle import BattleProps
from toontown.battle import DistributedBattle
from toontown.chat.ChatGlobals import *
from toontown.distributed.DelayDeletable import DelayDeletable
from toontown.nametag import NametagGlobals
from toontown.nametag.NametagGlobals import *
from toontown.suit.SuitLegList import *
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import ToontownBattleGlobals

STAND_OUTSIDE_DOOR = 2.5
BATTLE_IGNORE_TIME = 6
BATTLE_WAIT_TIME = 3
CATCHUP_SPEED_MULTIPLIER = 3
ALLOW_BATTLE_DETECT = 1

class DistributedSuit(DistributedSuitBase.DistributedSuitBase, DelayDeletable):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedSuit')
    ENABLE_EXPANDED_NAME = 0

    def __init__(self, cr):
        try:
            self.DistributedSuit_initialized
            return
        except:
            self.DistributedSuit_initialized = 1

        DistributedSuitBase.DistributedSuitBase.__init__(self, cr)
        self.spDoId = None
        self.pathEndpointStart = 0
        self.pathEndpointEnd = 0
        self.minPathLen = 0
        self.maxPathLen = 0
        self.pathPositionIndex = 0
        self.pathPositionTimestamp = 0.0
        self.pathState = 0
        self.path = None
        self.localPathState = 0
        self.currentLeg = -1
        self.pathStartTime = 0.0
        self.absorbDamage = 0
        self.fraudulentDamage = 0
        self.levelDamage = 0
        self.syphonHP = 0
        self._pendingQueuedDamage = 0
        self._pendingQueuedDeath = False
        self._pendingQueuedHealing = 0
        self.rpmIncrease2 = 0
        self.splashInterval = None
        self.legList = None
        self.initState = None
        self.finalState = None
        self.headInterval = None
        self.neutralInterval = None
        self.deathInterval = None
        self.luredInterval = None
        self.headInterval2 = None
        self.healInterval = None
        self.absorbInterval = None
        self.buildingSuit = 0
        self.battleConditions = {}
        self.deadSuits = []
        self.playByPlayInterval = None
        self.damageInterval = None
        self.fsm = ClassicFSM.ClassicFSM('DistributedSuit', [
            State.State('Off',
                        self.enterOff,
                        self.exitOff, [
                            'FromSky',
                            'FromSuitBuilding',
                            'Walk',
                            'Battle',
                            'neutral',
                            'ToToonBuilding',
                            'ToSuitBuilding',
                            'ToCogHQ',
                            'FromCogHQ',
                            'ToSky',
                            'FlyAway',
                            'DanceThenFlyAway',
                            'WalkToStreet',
                            'WalkFromStreet']),
         State.State('FromSky',
                     self.enterFromSky,
                     self.exitFromSky, [
                         'Walk',
                         'Battle',
                         'neutral',
                         'ToSky',
                         'WalkFromStreet']),
         State.State('FromSuitBuilding',
                     self.enterFromSuitBuilding,
                     self.exitFromSuitBuilding, [
                         'WalkToStreet',
                         'Walk',
                         'Battle',
                         'neutral',
                         'ToSky']),
         State.State('WalkToStreet',
                     self.enterWalkToStreet,
                     self.exitWalkToStreet, [
                         'Walk',
                         'Battle',
                         'neutral',
                         'ToSky',
                         'ToToonBuilding',
                         'ToSuitBuilding',
                         'ToCogHQ',
                         'WalkFromStreet']),
         State.State('WalkFromStreet',
                     self.enterWalkFromStreet,
                     self.exitWalkFromStreet, [
                         'ToToonBuilding',
                         'ToSuitBuilding',
                         'ToCogHQ',
                         'Battle',
                         'neutral',
                         'ToSky']),
         State.State('Walk',
                     self.enterWalk,
                     self.exitWalk, [
                         'WaitForBattle',
                         'Battle',
                         'neutral',
                         'WalkFromStreet',
                         'ToSky',
                         'ToCogHQ',
                         'Walk']),
         State.State('Battle',
                     self.enterBattle,
                     self.exitBattle, [
                         'Walk',
                         'ToToonBuilding',
                         'ToCogHQ',
                         'ToSuitBuilding',
                         'ToSky']),
         State.State('neutral',
                     self.enterNeutral,
                     self.exitNeutral, []),
         State.State('WaitForBattle',
                     self.enterWaitForBattle,
                     self.exitWaitForBattle, [
                         'Battle',
                         'neutral',
                         'Walk',
                         'WalkToStreet',
                         'WalkFromStreet',
                         'ToToonBuilding',
                         'ToCogHQ',
                         'ToSuitBuilding',
                         'ToSky']),
         State.State('ToToonBuilding',
                     self.enterToToonBuilding,
                     self.exitToToonBuilding, [
                         'neutral',
                         'Battle']),
         State.State('ToSuitBuilding',
                     self.enterToSuitBuilding,
                     self.exitToSuitBuilding, [
                         'neutral',
                         'Battle']),
         State.State('ToCogHQ',
                     self.enterToCogHQ,
                     self.exitToCogHQ, [
                         'neutral',
                         'Battle']),
         State.State('FromCogHQ',
                     self.enterFromCogHQ,
                     self.exitFromCogHQ, [
                         'neutral',
                         'Battle',
                         'Walk']),
         State.State('ToSky',
                     self.enterToSky,
                     self.exitToSky, [
                         'Battle']),
         State.State('FlyAway',
                     self.enterFlyAway,
                     self.exitFlyAway,
                     []),
         State.State('DanceThenFlyAway',
                     self.enterDanceThenFlyAway,
                     self.exitDanceThenFlyAway,
                     [])],
         'Off', 'Off')
        self.fsm.enterInitialState()
        self.soundSequenceList = []
        self.__currentDialogue = None

    def generate(self):
        DistributedSuitBase.DistributedSuitBase.generate(self)

    def disable(self):
        for soundSequence in self.soundSequenceList:
            soundSequence.finish()

        self.soundSequenceList = []
        self.notify.debug('DistributedSuit %d: disabling' % self.getDoId())
        self.resumePath(0)
        self.stopPathNow()
        self.setState('Off')
        DistributedSuitBase.DistributedSuitBase.disable(self)

    def delete(self):
        try:
            self.DistributedSuit_deleted
            return
        except:
            self.DistributedSuit_deleted = 1
        
        self.notify.debug('DistributedSuit %d: deleting' % self.getDoId())
        del self.fsm
        DistributedSuitBase.DistributedSuitBase.delete(self)

    def setPathEndpoints(self, start, end, minPathLen, maxPathLen):
        if self.pathEndpointStart == start and self.pathEndpointEnd == end and self.minPathLen == minPathLen and self.maxPathLen == maxPathLen and self.path != None:
            return
        
        self.pathEndpointStart = start
        self.pathEndpointEnd = end
        self.minPathLen = minPathLen
        self.maxPathLen = maxPathLen
        self.path = None
        self.pathLength = 0
        self.currentLeg = -1
        self.legList = None
        if self.maxPathLen == 0:
            return
        
        if not self.verifySuitPlanner():
            return
        
        self.startPoint = self.sp.pointIndexes[self.pathEndpointStart]
        self.endPoint = self.sp.pointIndexes[self.pathEndpointEnd]
        path = self.sp.genPath(self.startPoint, self.endPoint, self.minPathLen, self.maxPathLen)
        self.setPath(path)
        self.makeLegList()

    def verifySuitPlanner(self):
        if self.sp == None and self.spDoId != 0:
            self.notify.warning('Suit %d does not have a suit planner!  Expected SP doId %s.' % (self.doId, self.spDoId))
            self.sp = self.cr.doId2do.get(self.spDoId, None)
        if self.sp == None:
            return 0
        return 1

    def setPathPosition(self, index, timestamp):
        if not self.verifySuitPlanner():
            return
        if self.path == None:
            self.setPathEndpoints(self.pathEndpointStart, self.pathEndpointEnd, self.minPathLen, self.maxPathLen)
        self.pathPositionIndex = index
        self.pathPositionTimestamp = globalClockDelta.networkToLocalTime(timestamp)
        if self.legList != None:
            self.pathStartTime = self.pathPositionTimestamp - self.legList.getStartTime(self.pathPositionIndex)

    def setPathState(self, state):
        self.pathState = state
        self.resumePath(state)

    def debugSuitPosition(self, elapsed, currentLeg, x, y, timestamp):
        now = globalClock.getFrameTime()
        chug = globalClock.getRealTime() - now
        messageAge = now - globalClockDelta.networkToLocalTime(timestamp, now)
        if messageAge < -(chug + 0.5) or messageAge > chug + 1.0:
            print 'Apparently out of sync with AI by %0.2f seconds.  Suggest resync!' % messageAge
            return
        localElapsed = now - self.pathStartTime
        timeDiff = localElapsed - (elapsed + messageAge)
        if abs(timeDiff) > 0.2:
            print "%s (%d) appears to be %0.2f seconds out of sync along its path.  Suggest '~cogs sync'." % (self.getName(), self.getDoId(), timeDiff)
            return
        if self.legList == None:
            print "%s (%d) doesn't have a legList yet." % (self.getName(), self.getDoId())
            return
        netPos = Point3(x, y, 0.0)
        leg = self.legList.getLeg(currentLeg)
        calcPos = leg.getPosAtTime(elapsed - leg.getStartTime())
        calcPos.setZ(0.0)
        calcDelta = Vec3(netPos - calcPos)
        diff = calcDelta.length()
        if diff > 4.0:
            print '%s (%d) is %0.2f feet from the AI computed path!' % (self.getName(), self.getDoId(), diff)
            print 'Probably your DNA files are out of sync.'
            return
        localPos = Point3(self.getX(), self.getY(), 0.0)
        localDelta = Vec3(netPos - localPos)
        diff = localDelta.length()
        if diff > 10.0:
            print '%s (%d) in state %s is %0.2f feet from its correct position!' % (self.getName(),
             self.getDoId(),
             self.fsm.getCurrentState().getName(),
             diff)
            print 'Should be at (%0.2f, %0.2f), but is at (%0.2f, %0.2f).' % (x,
             y,
             localPos[0],
             localPos[1])
            return
        print '%s (%d) is in the correct position.' % (self.getName(), self.getDoId())

    def denyBattle(self):
        DistributedSuitBase.DistributedSuitBase.denyBattle(self)
        self.disableBattleDetect()

    def resumePath(self, state):
        if self.localPathState != state:
            self.localPathState = state
            if state == 0:
                self.stopPathNow()
            elif state == 1:
                self.moveToNextLeg(None)
            elif state == 2:
                self.stopPathNow()
                if self.sp != None:
                    self.setState('Off')
                    self.setState('FlyAway')
            elif state == 3:
                pass
            elif state == 4:
                self.stopPathNow()
                if self.sp != None:
                    self.setState('Off')
                    self.setState('DanceThenFlyAway')
            else:
                self.notify.error('No such state as: ' + str(state))

    def moveToNextLeg(self, task):
        if self.legList == None:
            self.notify.warning('Suit %d does not have a path!' % self.getDoId())
            return Task.done
        now = globalClock.getFrameTime()
        elapsed = now - self.pathStartTime
        nextLeg = self.legList.getLegIndexAtTime(elapsed, self.currentLeg)
        numLegs = self.legList.getNumLegs()
        if self.currentLeg != nextLeg:
            self.currentLeg = nextLeg
            self.doPathLeg(self.legList.getLeg(nextLeg), elapsed - self.legList.getStartTime(nextLeg))
        nextLeg += 1
        if nextLeg < numLegs:
            nextTime = self.legList.getStartTime(nextLeg)
            delay = nextTime - elapsed
            name = self.taskName('move')
            taskMgr.remove(name)
            taskMgr.doMethodLater(delay, self.moveToNextLeg, name)
        return Task.done

    def doPathLeg(self, leg, time):
        self.fsm.request(leg.getTypeName(), [leg, time])
        return 0

    def stopPathNow(self):
        name = self.taskName('move')
        taskMgr.remove(name)
        self.currentLeg = -1

    def calculateHeading(self, a, b):
        xdelta = b[0] - a[0]
        ydelta = b[1] - a[1]
        if ydelta == 0:
            if xdelta > 0:
                return -90
            else:
                return 90
        elif xdelta == 0:
            if ydelta > 0:
                return 0
            else:
                return 180
        else:
            angle = math.atan2(ydelta, xdelta)
            return rad2Deg(angle) - 90

    def beginBuildingMove(self, moveIn, doneEvent, suit = 0):
        doorPt = Point3(0)
        buildingPt = Point3(0)
        streetPt = Point3(0)
        if self.virtualPos:
            doorPt.assign(self.virtualPos)
        else:
            doorPt.assign(self.getPos())
        if moveIn:
            streetPt = self.prevPointPos()
        else:
            streetPt = self.currPointPos()
        dx = doorPt[0] - streetPt[0]
        dy = doorPt[1] - streetPt[1]
        buildingPt = Point3(doorPt[0] + dx, doorPt[1] + dy, doorPt[2])
        if moveIn:
            if suit:
                moveTime = SuitTimings.toSuitBuilding
            else:
                moveTime = SuitTimings.toToonBuilding
            return self.beginMove(doneEvent, buildingPt, time=moveTime)
        else:
            return self.beginMove(doneEvent, doorPt, buildingPt, time=SuitTimings.fromSuitBuilding)
        
        return None

    def setSPDoId(self, doId):
        self.spDoId = doId
        self.sp = self.cr.doId2do.get(doId, None)
        if self.sp == None and self.spDoId != 0:
            self.notify.warning('Suit %s created before its suit planner, %d' % (self.doId, self.spDoId))
        return

    def d_requestBattle(self, pos, hpr):
        self.cr.playGame.getPlace().setState('WaitForBattle')
        self.sendUpdate('requestBattle', [pos[0],
         pos[1],
         pos[2],
         hpr[0],
         hpr[1],
         hpr[2]])

    def __handleToonCollision(self, collEntry):
        if not base.localAvatar.wantBattles:
            return
        toonId = base.localAvatar.getDoId()
        self.notify.debug('Distributed suit: requesting a Battle with ' + 'toon: %d' % toonId)
        self.d_requestBattle(self.getPos(), self.getHpr())
        self.setState('WaitForBattle')

    def setAnimState(self, state):
        self.setState(state)

    def enterFromSky(self, leg, time):
        self.enableBattleDetect('fromSky', self.__handleToonCollision)
        self.loop('neutral', 0)
        if not self.verifySuitPlanner():
            return
        a = leg.getPosA()
        b = leg.getPosB()
        h = self.calculateHeading(a, b)
        self.setPosHprScale(a[0], a[1], a[2], h, 0.0, 0.0, 1.0, 1.0, 1.0)
        self.mtrack = self.beginSupaFlyMove(a, 1, 'fromSky')
        self.mtrack.start(time)

    def exitFromSky(self):
        self.disableBattleDetect()
        self.mtrack.finish()
        del self.mtrack
        self.detachPropeller()

    def enterWalkToStreet(self, leg, time):
        self.enableBattleDetect('walkToStreet', self.__handleToonCollision)
        self.loop('walk', 0)
        a = leg.getPosA()
        b = leg.getPosB()
        delta = Vec3(b - a)
        length = delta.length()
        delta *= (length - STAND_OUTSIDE_DOOR) / length
        a1 = Point3(b - delta)
        self.enableRaycast(1)
        h = self.calculateHeading(a, b)
        self.setHprScale(h, 0.0, 0.0, 1.0, 1.0, 1.0)
        self.mtrack = Sequence(LerpPosInterval(self, leg.getLegTime(), b, startPos=a1), name=self.taskName('walkToStreet'))
        self.mtrack.start(time)

    def exitWalkToStreet(self):
        self.disableBattleDetect()
        self.enableRaycast(0)
        self.mtrack.finish()
        del self.mtrack

    def enterWalkFromStreet(self, leg, time):
        self.enableBattleDetect('walkFromStreet', self.__handleToonCollision)
        self.loop('walk', 0)
        a = leg.getPosA()
        b = leg.getPosB()
        delta = Vec3(b - a)
        length = delta.length()
        delta *= (length - STAND_OUTSIDE_DOOR) / length
        b1 = Point3(a + delta)
        self.enableRaycast(1)
        h = self.calculateHeading(a, b)
        self.hprScaleInterval(.3, Vec3(h, 0, 0), Vec3(1, 1, 1)).start()
        self.mtrack = Sequence(LerpPosInterval(self, leg.getLegTime(), b1, startPos=a), name=self.taskName('walkFromStreet'))
        self.mtrack.start(time)

    def exitWalkFromStreet(self):
        self.disableBattleDetect()
        self.enableRaycast(0)
        self.mtrack.finish()
        del self.mtrack

    def enterWalk(self, leg, time):
        self.enableBattleDetect('bellicose', self.__handleToonCollision)
        self.loop('walk', 0)
        a = leg.getPosA()
        b = leg.getPosB()
        h = self.calculateHeading(a, b)
        pos = leg.getPosAtTime(time)
        fullpos = (pos[0], pos[1], pos[2])
        self.posQuatScaleInterval(.3, Point3(fullpos), Vec3(h, 0, 0), Vec3(1, 1, 1)).start()
        self.mtrack = Sequence(LerpPosInterval(self, leg.getLegTime(), b, startPos=a), name=self.taskName('bellicose'))
        self.mtrack.start(time)

    def exitWalk(self):
        self.disableBattleDetect()
        self.mtrack.pause()
        del self.mtrack

    def enterToSky(self, leg, time):
        self.enableBattleDetect('toSky', self.__handleToonCollision)
        if not self.verifySuitPlanner():
            return
        a = leg.getPosA()
        b = leg.getPosB()
        h = self.calculateHeading(a, b)
        self.setPosHprScale(b[0], b[1], b[2], h, 0.0, 0.0, 1.0, 1.0, 1.0)
        self.mtrack = self.beginSupaFlyMove(b, 0, 'toSky')
        self.mtrack.start(time)

    def exitToSky(self):
        self.disableBattleDetect()
        self.mtrack.finish()
        del self.mtrack
        self.detachPropeller()

    def enterFromSuitBuilding(self, leg, time):
        self.enableBattleDetect('fromSuitBuilding', self.__handleToonCollision)
        self.loop('walk', 0)
        if not self.verifySuitPlanner():
            return
        a = leg.getPosA()
        b = leg.getPosB()
        delta = Vec3(b - a)
        length = delta.length()
        delta2 = delta * (self.sp.suitWalkSpeed * leg.getLegTime()) / length
        delta *= (length - STAND_OUTSIDE_DOOR) / length
        b1 = Point3(b - delta)
        a1 = Point3(b1 - delta2)
        self.enableRaycast(1)
        h = self.calculateHeading(a, b)
        self.setHprScale(h, 0.0, 0.0, 1.0, 1.0, 1.0)
        self.mtrack = Sequence(LerpPosInterval(self, leg.getLegTime(), b1, startPos=a1), name=self.taskName('fromSuitBuilding'))
        self.mtrack.start(time)

    def exitFromSuitBuilding(self):
        self.disableBattleDetect()
        self.mtrack.finish()
        del self.mtrack

    def enterToToonBuilding(self, leg, time):
        self.loop('neutral', 0)

    def exitToToonBuilding(self):
        pass

    def enterToSuitBuilding(self, leg, time):
        self.loop('walk', 0)
        if not self.verifySuitPlanner():
            return
        a = leg.getPosA()
        b = leg.getPosB()
        delta = Vec3(b - a)
        length = delta.length()
        delta2 = delta * (self.sp.suitWalkSpeed * leg.getLegTime()) / length
        delta *= (length - STAND_OUTSIDE_DOOR) / length
        a1 = Point3(a + delta)
        b1 = Point3(a1 + delta2)
        self.enableRaycast(1)
        h = self.calculateHeading(a, b)
        self.setHprScale(h, 0.0, 0.0, 1.0, 1.0, 1.0)
        self.mtrack = Sequence(LerpPosInterval(self, leg.getLegTime(), b1, startPos=a1), name=self.taskName('toSuitBuilding'))
        self.mtrack.start(time)

    def exitToSuitBuilding(self):
        self.mtrack.finish()
        del self.mtrack

    def enterToCogHQ(self, leg, time):
        self.loop('neutral', 0)

    def exitToCogHQ(self):
        pass

    def enterFromCogHQ(self, leg, time):
        self.loop('neutral', 0)
        self.detachNode()

    def exitFromCogHQ(self):
        self.reparentTo(render)

    def enterBattle(self):
        DistributedSuitBase.DistributedSuitBase.enterBattle(self)
        self.resumePath(0)

    def enterNeutral(self):
        self.notify.debug('DistributedSuit: Neutral (entering a Door)')
        self.resumePath(0)
        self.loop('neutral%s' % ('-hurt' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',), 0)

    def exitNeutral(self):
        pass

    def enterWaitForBattle(self):
        DistributedSuitBase.DistributedSuitBase.enterWaitForBattle(self)
        self.resumePath(0)

    def enterFlyAway(self):
        self.enableBattleDetect('flyAway', self.__handleToonCollision)
        if not self.verifySuitPlanner():
            return
        b = Point3(self.getPos())
        self.mtrack = self.beginSupaFlyMove(b, 0, 'flyAway')
        self.mtrack.start()

    def exitFlyAway(self):
        self.disableBattleDetect()
        self.mtrack.finish()
        del self.mtrack
        self.detachPropeller()

    def enterDanceThenFlyAway(self):
        self.enableBattleDetect('danceThenFlyAway', self.__handleToonCollision)
        if not self.verifySuitPlanner():
            return
        danceTrack = self.actorInterval('victory')
        b = Point3(self.getPos())
        flyMtrack = self.beginSupaFlyMove(b, 0, 'flyAway')
        self.mtrack = Sequence(danceTrack, flyMtrack, name=self.taskName('danceThenFlyAway'))
        self.mtrack.start()

    def exitDanceThenFlyAway(self):
        self.disableBattleDetect()
        self.mtrack.finish()
        del self.mtrack
        self.detachPropeller()

    def generateHeadAnims(self, path, cActor, additionalAnims=[]):
        anims = ['bellow', 'neutral', 'death', 'grunt', 'murmur', 'question', 'statement', 'neutral-hurt', 'neutral-lured', 'bust',
                 'fusiondance-shot1', 'fusiondance-shot2', 'fusiondance-shot3', 'fusiondance-shot4', 'fusiondance-shot5',
                 'stun', 'enraged', 'insurance', 'ace-in-the-hole', 'wheelspin', 'healing-bell', 'revvedup', 'scabbard', 'sparkplug', 'throttle', 'gsnap', 'throttle2', 'mouthdrop', 'dive',
                 'emergeHead', 'exitWater', 'underwaterHit', 'gamble', 'cigar-smoke', 'overclocked', 'come-on', 'zero']
        for anim in additionalAnims:
            anims.append(anim)
        animList = {}
        for anim in anims:
            animList[anim] = path + anim + '.bam'
        cActor.loadAnims(animList)


    def playCurrentDialogue(self, dialogue, chatFlags, interrupt = 1):
        if interrupt and self.__currentDialogue is not None:
            self.__currentDialogue.stop()
        self.__currentDialogue = dialogue
        if dialogue:
            base.playSfx(dialogue, node=self)
        elif chatFlags & CFSpeech != 0:
            if self.nametag.getNumChatPages() > 0:
                self.playDialogueForString(self.nametag.getChatText())
                if self.soundChatBubble != None:
                    base.playSfx(self.soundChatBubble, node=self)
            elif self.nametag.getStompChatText():
                self.playDialogueForString(self.nametag.getStompChatText(), 0)
            #if hasattr(base.cr, 'chatLog'):
              #  base.cr.chatLog.addToLog("\1cogGray\1%s\2: %s" %(self.name, self.nametag.getChatText()))

    def playDialogueForString(self, chatString, delay = 0.0):
        if len(chatString) == 0:
            return
        searchString = chatString.lower()
        if searchString.find(OTPLocalizer.DialogSpecial) >= 0:
            type = 'special'
        elif searchString.find(OTPLocalizer.DialogExclamation) >= 0:
            type = 'exclamation'
        elif searchString.find(OTPLocalizer.DialogQuestion) >= 0:
            type = 'question'
        elif random.randint(0, 1):
            type = 'statementA'
        else:
            type = 'statementB'
        stringLength = len(chatString)
        if stringLength <= OTPLocalizer.DialogLength1:
            length = 1
        elif stringLength <= OTPLocalizer.DialogLength2:
            length = 2
        elif stringLength <= OTPLocalizer.DialogLength3:
            length = 3
        else:
            length = 4
        self.playDialogue(type, length, delay)

    def playDialogue(self, type, length, delay = 0.0):
        dialogueArray = self.getDialogueArray()
        if dialogueArray == None:
            return
        sfxIndex = None
        if type == 'statementA' or type == 'statementB':
            if length == 1:
                sfxIndex = 0
            elif length == 2:
                sfxIndex = 1
            elif length >= 3:
                sfxIndex = 2
        elif type == 'exclamation':
            sfxIndex = 4
        elif type == 'question':
            sfxIndex = 3
        elif type == 'special':
            sfxIndex = 1
        else:
            notify.error('unrecognized dialogue type: ', type)
        if sfxIndex != None and sfxIndex < len(dialogueArray) and dialogueArray[sfxIndex] != None:
            soundSequence = Sequence(Wait(delay), SoundInterval(dialogueArray[sfxIndex], node=None, listenerNode=base.localAvatar, loop=0, volume=1.0))
            self.soundSequenceList.append(soundSequence)
            soundSequence.start()
            self.cleanUpSoundList()

    def addPendingQueuedHealing(self, amount):
        if not hasattr(self, '_pendingQueuedHealing'):
            self._pendingQueuedHealing = 0
        self._pendingQueuedHealing += int(amount)

    def clearPendingQueuedHealing(self, amount):
        if not hasattr(self, '_pendingQueuedHealing'):
            self._pendingQueuedHealing = 0
        self._pendingQueuedHealing -= int(amount)
        if self._pendingQueuedHealing < 0:
            self._pendingQueuedHealing = 0

    def getQueuedProjectedHPFull(self):
        damage = getattr(self, '_pendingQueuedDamage', 0)
        healing = getattr(self, '_pendingQueuedHealing', 0)
        return self.currHP - (damage + healing)

    def clearPendingQueuedHealingAll(self):
        self._pendingQueuedHealing = 0
        self._pendingQueuedDeath = False

    def setPendingQueuedDesperation(self, value):
        self._pendingQueuedDesperation = bool(value)

    def getProjectedDesperation(self):
        return getattr(self, '_pendingQueuedDesperation', False) or self.isDesperation

    def clearPendingQueuedDesperation(self):
        self._pendingQueuedDesperation = False

    def makePlayByPlayTextInterval(self, pbpText, displayName, attackDuration):
        pending = getattr(self, '_pendingQueuedDamage', 0)
        projectedHP = float(self.getQueuedProjectedHPFull())

        if projectedHP > float(self.maxHP * 1.5):
            playByPlayInterval = pbpText.getShowIntervalOvercharged(displayName, attackDuration)
        elif projectedHP > float(self.maxHP):
            playByPlayInterval = pbpText.getShowIntervalOverhealed(displayName, attackDuration)
        else:
            playByPlayInterval = pbpText.getShowInterval(displayName, attackDuration)

        return playByPlayInterval

    def makePlayByPlayTextCheatInterval(self, pbpText, displayName, attackDuration):
        pending = getattr(self, '_pendingQueuedDamage', 0)
        projectedHP = float(self.getQueuedProjectedHPFull())

        if projectedHP > float(self.maxHP * 1.5):
            playByPlayInterval = pbpText.getShowIntervalCheatOvercharged(displayName, attackDuration)
        elif projectedHP > float(self.maxHP):
            playByPlayInterval = pbpText.getShowIntervalCheatOverhealed(displayName, attackDuration)
        else:
            playByPlayInterval = pbpText.getShowIntervalCheatRed(displayName, attackDuration)

        return playByPlayInterval

    def makePlayByPlayTextLegallyBoundInterval(self, pbpText, attackDuration):
        if self.getProjectedDesperation():
            playByPlayInterval = pbpText.getShowIntervalDesc(
                "Legally Bound Toons take 28 damage per round!", attackDuration)
        else:
            playByPlayInterval = pbpText.getShowIntervalDesc(
                "Legally Bound Toons take 20 damage per round!", attackDuration)

        return playByPlayInterval

    def makePlayByPlayTextLiquidationEventInterval(self, pbpText, attackDuration):
        if self.getProjectedDesperation():
            playByPlayInterval = pbpText.getShowIntervalDesc(
                "Liquidated Toons take 42 extra damage per round!", attackDuration)
        else:
            playByPlayInterval = pbpText.getShowIntervalDesc(
                "Liquidated Toons take 30 extra damage per round!", attackDuration)

        return playByPlayInterval

    def makePlayByPlayTextCourtRecordInterval(self, pbpText, attackDuration):
        if self.getProjectedDesperation():
            playByPlayInterval = pbpText.getShowIntervalDesc(
                'Due to an illegal action, this toon takes 70 damage!',
                attackDuration
            )
        else:
            playByPlayInterval = pbpText.getShowIntervalDesc(
                'Due to an illegal action, this toon takes 50 damage!',
                attackDuration
            )

        return playByPlayInterval

    def makePlayByPlayTextBurnedInterval(self, pbpText, attackDuration):
        if self.getProjectedDesperation():
            playByPlayInterval = pbpText.getShowIntervalDesc(
                'Burned Toons take 42 extra damage per round!',
                attackDuration
            )
        else:
            playByPlayInterval = pbpText.getShowIntervalDesc(
                'Burned Toons take 30 extra damage per round!',
                attackDuration
            )

        return playByPlayInterval

    def makePlayByPlayTextInflationInterval(self, pbpText, attackDuration):
        if self.getProjectedDesperation():
            playByPlayInterval = pbpText.getShowIntervalDesc(
                'Due to an overinflated budget this toon takes 70 damage!',
                attackDuration
            )
        else:
            playByPlayInterval = pbpText.getShowIntervalDesc(
                'Due to an overinflated budget this toon takes 50 damage!',
                attackDuration
            )

        return playByPlayInterval

    def makePlayByPlayTextBustedInterval(self, pbpText, attackDuration):
        if self.getProjectedDesperation():
            playByPlayInterval = pbpText.getShowIntervalDesc(
                'Employed Toons are forced to take 35 damage every round!',
                attackDuration
            )
        else:
            playByPlayInterval = pbpText.getShowIntervalDesc(
                'Employed Toons are forced to take 25 damage every round!',
                attackDuration
            )

        return playByPlayInterval

    def setPendingQueuedLured(self, value):
        self._pendingQueuedLured = bool(value)

    def getProjectedLured(self):
        return getattr(self, '_pendingQueuedLured', False)

    def clearPendingQueuedLured(self):
        self._pendingQueuedLured = False

    def makeCogStepBackInterval(self, battle):
        if self.getProjectedLured():
            return self.__createSuitResetPosTrack(battle)
        else:
            return Sequence(Func(self.setNeutralAnimationTrap))

    def makeCogStepBackDeathInterval(self, battle):
        if self.getProjectedLured():
            return self.__createSuitResetPosTrack(battle)
        else:
            return Sequence()

    def checkCogLured(self, battle):
        if self.luredInterval != None:
            self.luredInterval.finish()
           # del self.playByPlayInterval
        if self.getDizzy():
            self.luredInterval = self.__createSuitResetPosTrack(battle)
            self.luredInterval.start()
        else:
            self.luredInterval = Func(self.setNeutralAnimationTrap)
            self.luredInterval.start()

    def checkCogLuredDeath(self, battle):
        if self.luredInterval != None:
            self.luredInterval.finish()
         #   del self.playByPlayInterval
        if self.getDizzy():
            self.luredInterval = self.__createSuitResetPosTrack(battle)
            self.luredInterval.start()
        else:
            pass

    def makeCogLuredDeathInterval(self, battle):
        if self.luredInterval is not None:
            self.luredInterval.finish()
            self.luredInterval = None

        if self.getDizzy():
            self.luredInterval = self.__createSuitResetPosTrack(battle)
        else:
            self.luredInterval = Sequence()

        return self.luredInterval

    def checkCogThrowPos(self, item, battle, duration):
        hitPoint = self.getPos(battle)
        hitPoint.setZ(self.height + 2)
        hitPoint.setY(hitPoint.getY() + 0.5)
        Sequence(LerpPosInterval(item, duration, VBase3(hitPoint.getX(), hitPoint.getY() + 0.5, hitPoint.getZ() - 10))).start()

    def __createSuitResetPosTrack(self, battle):
        self.clearPendingQueuedLured()
        resetPos, resetHpr = battle.getActorPosHpr(self)
        moveDist = Vec3(self.getPos(battle) - resetPos).length()
        moveDuration = 0.5
        neutralTrack = Func(self.setNeutralAnimationTrap)
        unluredTrack = Func(battle.unlureSuit, self)
        unlureSuit = Func(self.makeUnLured)
        updateTrack = Parallel(Func(self.setChatAbsolute,
                                    '',
                                    CFSpeech | CFTimeout))
        walkTrack = Sequence(Func(self.setHpr, battle, resetHpr), ActorInterval(self, 'walk', startTime=1, duration=moveDuration, endTime=0.0001), Func(self.setNeutralAnimationTrap))
        moveTrack = LerpPosInterval(self, moveDuration, resetPos, other=battle)
        return Parallel(unluredTrack, unlureSuit, walkTrack, moveTrack)

    def checkPlayByPlayText(self, pbpText, displayName, attackDuration):
        if self.playByPlayInterval != None:
            self.playByPlayInterval.finish()
          #  del self.playByPlayInterval
        pbpText = pbpText
        if float(self.currHP) > float(self.maxHP * 1.5):
            self.playByPlayInterval = pbpText.getShowIntervalOvercharged(displayName, attackDuration)
            self.playByPlayInterval.start()
        elif float(self.currHP) > float(self.maxHP):
            self.playByPlayInterval = pbpText.getShowIntervalOverhealed(displayName, attackDuration)
            self.playByPlayInterval.start()
        else:
            self.playByPlayInterval = pbpText.getShowInterval(displayName, attackDuration)
            self.playByPlayInterval.start()

    def checkPlayByPlayTextCheat(self, pbpText, displayName, attackDuration):
        if self.playByPlayInterval != None:
            self.playByPlayInterval.finish()
           # del self.playByPlayInterval
        pbpText = pbpText
        if float(self.currHP) > float(self.maxHP * 1.5):
            self.playByPlayInterval = pbpText.getShowIntervalCheatOvercharged(displayName, attackDuration)
            self.playByPlayInterval.start()
        elif float(self.currHP) > float(self.maxHP):
            self.playByPlayInterval = pbpText.getShowIntervalCheatOverhealed(displayName, attackDuration)
            self.playByPlayInterval.start()
        else:
            self.playByPlayInterval = pbpText.getShowIntervalCheatRed(displayName, attackDuration)
            self.playByPlayInterval.start()

    def checkPlayByPlayTextLegallyBound(self, pbpText, attackDuration):
        if self.playByPlayInterval != None:
            self.playByPlayInterval.finish()
            #del self.playByPlayInterval
        pbpText = pbpText
        if self.isDesperation:
            self.playByPlayInterval = pbpText.getShowIntervalDesc("Legally Bound Toons take 28 damage per round!", attackDuration)
            self.playByPlayInterval.start()
        else:
            self.playByPlayInterval = pbpText.getShowIntervalDesc("Legally Bound Toons take 20 damage per round!", attackDuration)
            self.playByPlayInterval.start()

    def checkPlayByPlayTextLiquidationEvent(self, pbpText, attackDuration):
        if self.playByPlayInterval != None:
            self.playByPlayInterval.finish()
           # del self.playByPlayInterval
        pbpText = pbpText
        if self.isDesperation:
            self.playByPlayInterval = pbpText.getShowIntervalDesc("Liquidated Toons take 42 extra damage per round!", attackDuration)
            self.playByPlayInterval.start()
        else:
            self.playByPlayInterval = pbpText.getShowIntervalDesc("Liquidated Toons take 30 extra damage per round!", attackDuration)
            self.playByPlayInterval.start()

    def checkPlayByPlayTextCourtRecord(self, pbpText, attackDuration):
        if self.playByPlayInterval != None:
            self.playByPlayInterval.finish()
            #del self.playByPlayInterval
        pbpText = pbpText
        if self.isDesperation:
            self.playByPlayInterval = pbpText.getShowIntervalDesc('Due to an illegal action, this toon takes 70 damage!', attackDuration)
            self.playByPlayInterval.start()
        else:
            self.playByPlayInterval = pbpText.getShowIntervalDesc('Due to an illegal action, this toon takes 50 damage!', attackDuration)
            self.playByPlayInterval.start()

    def checkPlayByPlayTextBurned(self, pbpText, attackDuration):
        if self.playByPlayInterval != None:
            self.playByPlayInterval.finish()
           # del self.playByPlayInterval
        pbpText = pbpText
        if self.isDesperation:
            self.playByPlayInterval = pbpText.getShowIntervalDesc('Burned Toons take 42 extra damage per round!', attackDuration)
            self.playByPlayInterval.start()
        else:
            self.playByPlayInterval = pbpText.getShowIntervalDesc('Burned Toons take 30 extra damage per round!', attackDuration)
            self.playByPlayInterval.start()

    def checkPlayByPlayTextInflation(self, pbpText, attackDuration):
        if self.playByPlayInterval != None:
            self.playByPlayInterval.finish()
            #del self.playByPlayInterval
        pbpText = pbpText
        if self.isDesperation:
            self.playByPlayInterval = pbpText.getShowIntervalDesc("Due to an overinflated budget this toon takes 70 damage!", attackDuration)
            self.playByPlayInterval.start()
        else:
            self.playByPlayInterval = pbpText.getShowIntervalDesc("Due to an overinflated budget this toon takes 50 damage!", attackDuration)
            self.playByPlayInterval.start()

    def checkPlayByPlayTextBusted(self, pbpText, attackDuration):
        if self.playByPlayInterval != None:
            self.playByPlayInterval.finish()
           # del self.playByPlayInterval
        pbpText = pbpText
        if self.isDesperation:
            self.playByPlayInterval = pbpText.getShowIntervalDesc('Employed Toons are forced to take 35 damage every round!', attackDuration)
            self.playByPlayInterval.start()
        else:
            self.playByPlayInterval = pbpText.getShowIntervalDesc('Employed Toons are forced to take 25 damage every round!', attackDuration)
            self.playByPlayInterval.start()

    def checkCogHP(self, battle):
        if self.deathInterval != None:
            self.deathInterval = None
        elif self.getHP() <= 0 and self.deathInterval == None:
            self.deathInterval = Sequence(MovieUtil.createSuitDeathTrack(self, battle), Func(battle.unlureSuit, self))
            self.deathInterval.start()
        else:
            pass

    def checkCogDeath(self, battle):
        if self.deathInterval != None:
            self.deathInterval.finish()
          #  del self.deathInterval
        if self.getHP() <= 0:
            self.deadSuits.append(self)
        else:
            pass

    def checkHealingPhrases(self, num):
        if self.deathInterval != None:
            self.deathInterval = None
        if self.getHP() > 0 and num == 0:
            self.deathInterval = Sequence(Func(self.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitHealingPhrases), CFSpeech | CFTimeout))
            self.deathInterval.start()
        elif self.getHP() > 0 and num == 1:
            self.deathInterval = Sequence(Func(self.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitMarkedPhrases), CFSpeech | CFTimeout))
            self.deathInterval.start()
        elif self.getHP() > 0 and num == 2:
            self.deathInterval = Sequence(Func(self.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitContractedPhrases), CFSpeech | CFTimeout))
            self.deathInterval.start()
        else:
            pass

    def checkCogHPDrop(self, battle):
        if self.deathInterval != None:
            self.deathInterval = None
        elif self.getHP() <= 0 and self.deathInterval == None:
            self.deathInterval = Sequence(MovieUtil.createSuitCrashTrack(self, battle))
            self.deathInterval.start()
        else:
            pass

    def checkAbsorbHP(self, battle):
        if self.deathInterval != None:
            self.deathInterval = None
        elif self.getHP() <= 0:
            self.deathInterval = Sequence(Func(self.makeDead))
            self.deathInterval.start()
        else:
            pass

    def checkCogHPBomb(self, battle):
        if self.deathInterval != None:
            self.deathInterval = None
        elif self.getHP() <= 0 and self.deathInterval == None and not self.isDead:
            self.deathInterval = Sequence(MovieUtil.shortCircuitTrack(self, battle), Func(battle.unlureSuit, self))
            self.deathInterval.start()
        else:
            pass

    def checkCogHPZap(self, battle):
        if self.getHP() <= 0:
            self.deathInterval = Sequence(MovieUtil.shortCircuitTrack(self, battle), Func(battle.unlureSuit, self))
            self.deathInterval.start()
        else:
            pass

    def checkCogHPLaserRevive(self, battle):
        if self.deathInterval != None:
            self.deathInterval = None
        elif self.getHP() <= 0 and self.deathInterval == None:
            self.deathInterval = Sequence(MovieUtil.createSuitReviveTrackVirtual(self, battle), Func(battle.unlureSuit, self))
            self.deathInterval.start()
        else:
            pass

    def checkCogHPLaser(self, battle):
        if self.deathInterval != None:
            self.deathInterval = None
        elif self.getHP() <= 0 and self.deathInterval == None:
            self.deathInterval = Sequence(MovieUtil.createVirtualSuitDeathTrack(self, battle), Func(battle.unlureSuit, self))
            self.deathInterval.start()
        else:
            pass

    def checkCogHPRevive(self, battle):
        if self.deathInterval != None:
            self.deathInterval = None
        elif self.getHP() <= 0 and self.deathInterval == None:
            self.deathInterval = Sequence(MovieUtil.createSuitReviveTrack(self, battle), Func(battle.unlureSuit, self))
            self.deathInterval.start()
        else:
            pass

    def addAbsorbDamage(self, absorbingCog, damage):
        absorbingCog.absorbDamage += damage

    def removeAbsorbDamage(self):
        self.absorbDamage  = 0

    def addFraudulentDamage(self, absorbingCog, damage):
        absorbingCog.fraudulentDamage += damage

    def removeFraudulentDamage(self):
        self.fraudulentDamage  = 0

    def addSyphonHP(self, absorbingCog, damage):
        absorbingCog.syphonHP += damage

    def removeSyphonHP(self):
        self.syphonHP  = 0

    def checkSyphonHP(self, syphonHp):
        x = int((self.maxHP * self.hardMaxHP) - self.currHP)
        if self.currHP >= (self.maxHP * self.hardMaxHP):
            self.absorbInterval = Sequence(
                Parallel(Func(self.showHpTextNew, 0, text="SYPHONED!", colorCode=1),
                         Func(self.setHealthForMe, + 0),
                         Func(self.updateHealthBar, 0))).start()
        elif self.currHP + syphonHp > (self.maxHP * self.hardMaxHP):
            self.absorbInterval = Sequence(
                Parallel(Func(self.showHpTextNew, + x, text="SYPHONED!", colorCode=1),
                         Func(self.setHealthForMe, + x),
                         Func(self.updateHealthBar, 0))).start()
            self.addPendingQueuedHealing(x)
        else:
            self.absorbInterval = Sequence(
                Parallel(Func(self.showHpTextNew, + syphonHp, text="SYPHONED!", colorCode=1),
                         Func(self.setHealthForMe, + syphonHp),
                         Func(self.updateHealthBar, 0))).start()
            self.addPendingQueuedHealing(syphonHp)

    def addLevelDamage(self, absorbingCog, damage):
        absorbingCog.levelDamage += damage

    def removeLevelDamage(self):
        self.levelDamage = 0

    def addRPMIncrease(self, damage):
        self.rpmIncrease2 += damage

    def addRPM(self, dmg):
        self.damageInterval = Parallel(Func(self.setRPM, self.getRPM() + self.getRPMIncrease() + dmg)).start()

    def addRPMWhipsaw(self):
        self.damageInterval = Parallel(Func(self.setRPM, self.getRPM() + (self.getRPMIncrease() + 4))).start()

    def removeRPM(self, damage):
        self.damageInterval = Parallel(Func(self.setRPM, self.getRPM() - damage)).start()

    def addRageBuilding(self, damage):
        self.damageInterval = Parallel(Func(self.setRageBuilding, self.getRageBuilding() + int(damage * .1))).start()

    def removeRageBuilding(self):
        self.damageInterval = Parallel(Func(self.setRageBuilding, 0)).start()

    def addPowerhouseRotation(self, damage):
        self.damageInterval = Parallel(Func(self.setPowerhouseRotation, self.getPowerhouseRotation() + int(damage * .1))).start()

    def addStormCellDamage(self):
        self.damageInterval = Parallel(Func(self.removeStormCellDamage, self.getStormCellDamage() - 6)).start()

    def addStormCellDamageReverse(self):
        self.damageInterval = Parallel(Func(self.removeStormCellDamage, 60)).start()

    def addHeavyRainDamage(self, damage):
        self.damageInterval = Parallel(Func(self.addHeavyRainDamageReal, self.getHeavyRainDamage() + int(damage))).start()

    def removeHeavyRainDamage(self):
        self.damageInterval = Parallel(Func(self.addHeavyRainDamage, 0)).start()

    def removePowerhouseRotation(self):
        self.damageInterval = Parallel(Func(self.setPowerhouseRotation, 0)).start()


    def checkAbsorbDamage(self, absorbDamage):
        if self.dna.name == 'sgoat':
            self.absorbInterval = Sequence(Parallel(ActorInterval(self, 'pie-small-react'), MovieUtil.createSuitStunInterval(self, 0, 2.0),
                                         Func(self.showHpTextNew, - absorbDamage, text="ABSORBED!", colorCode=1), Func(self.setHealthForMe, - absorbDamage),
                                         Func(self.updateHealthBar, 0)), Func(self.setNeutralAnimation), Func(self.addRageBuilding, int(absorbDamage)),
                                           Func(self.removeAbsorbDamage)).start()
        else:
            self.absorbInterval = Sequence(
                Parallel(ActorInterval(self, 'pie-small-react'), MovieUtil.createSuitStunInterval(self, 0, 2.0),
                         Func(self.showHpTextNew, - absorbDamage, text="ABSORBED!", colorCode=1),
                         Func(self.setHealthForMe, - absorbDamage),
                         Func(self.updateHealthBar, 0)), Func(self.setNeutralAnimation),
                Func(self.removeAbsorbDamage)).start()

    def checkFraudulentDamage(self):
        self.absorbInterval = Sequence(
                Parallel(ActorInterval(self, 'pie-small-react'), MovieUtil.createSuitStunInterval(self, 0, 2.0),
                         Func(self.showHpTextNew, - 158),
                         Func(self.setHealthForMe, - 158),
                         Func(self.updateHealthBar, 0)), Func(self.setNeutralAnimation)).start()

    def checkLevelDamage(self, levelDamage):
        if self.dna.name == 'hroller':
            if float(self.currHP) < levelDamage:
                x = int(self.currHP - 1)
                self.absorbInterval = Sequence(Parallel(ActorInterval(self, 'pie-small-react'), MovieUtil.createSuitStunInterval(self, 0, 2.0),
                                         Func(self.showHpText, - x), Func(self.setHealthForMe, - x),
                                         Func(self.updateHealthBar, 0)), Func(self.setNeutralAnimation),
                                           Func(self.removeLevelDamage)).start()
            else:
                self.absorbInterval = Sequence(Parallel(ActorInterval(self, 'pie-small-react'), MovieUtil.createSuitStunInterval(self, 0, 2.0),
                                                        Func(self.showHpText, - levelDamage), Func(self.setHealthForMe, - levelDamage),
                                                        Func(self.updateHealthBar, 0)), Func(self.setNeutralAnimation),
                                               Func(self.removeLevelDamage)).start()
        else:
            self.absorbInterval = Sequence(Parallel(ActorInterval(self, 'pie-small-react'), MovieUtil.createSuitStunInterval(self, 0, 2.0),
                                                    Func(self.showHpText, - levelDamage), Func(self.setHealthForMe, - levelDamage),
                                                    Func(self.updateHealthBar, 0)), Func(self.setNeutralAnimation),
                                           Func(self.removeLevelDamage)).start()

    def checkDamage(self, levelDamage):
        if self.dna.name == 'safesupervis':
            self.absorbInterval = Sequence(Parallel(ActorInterval(self, 'pie-small-react'), MovieUtil.createSuitStunInterval(self, 0, 2.0),
                                         Func(self.showHpTextNew, - levelDamage, text="OVERHEATED!", colorCode=5), Func(self.setHealthForMe, - levelDamage),
                                         Func(self.updateHealthBar, 0)), Func(self.setNeutralAnimation),
                                           Func(self.removeLevelDamage)).start()
        else:
            self.absorbInterval = Sequence(Parallel(ActorInterval(self, 'pie-small-react'), MovieUtil.createSuitStunInterval(self, 0, 2.0),
                                                    Func(self.showHpText, - levelDamage), Func(self.setHealthForMe, - levelDamage),
                                                    Func(self.updateHealthBar, 0)), Func(self.setNeutralAnimation),
                                           Func(self.removeLevelDamage)).start()

    def checkDamage2(self, levelDamage):
        self.absorbInterval = Sequence(Parallel(ActorInterval(self, 'pie-small-react'), MovieUtil.createSuitStunInterval(self, 0, 2.0),
                                                    Func(self.showHpText, - levelDamage), Func(self.setHealthForMe, - levelDamage),
                                                    Func(self.updateHealthBar, 0)), Func(self.setNeutralAnimation),
                                           Func(self.removeLevelDamage)).start()

    def checkCogOvercharge(self):
        if float(self.currHP) > float(self.maxHP * 1.5):
            self.isOvercharged = 1
        else:
            self.isOvercharged = 0

    def checkAutoRepair(self):
        x = int((self.maxHP * self.hardMaxHP) - self.currHP)
        if self.currHP >= (self.maxHP * self.hardMaxHP):
            self.healInterval = Parallel(Func(self.showHpTextNew, 0, text="REPAIRED!", colorCode=1),
                                         Func(self.updateHealthBar, 0)).start()
        elif self.currHP + (self.maxHP * 0.35) > (self.maxHP * self.hardMaxHP):
            self.healInterval = Parallel(Func(self.showHpTextNew, x, text="REPAIRED!", colorCode=1),
                                         Func(self.setHealthForMe, x), Func(self.updateHealthBar, 0)).start()
        else:
            self.healInterval = Parallel(Func(self.showHpTextNew, int(self.maxHP * 0.35), text="REPAIRED!", colorCode=1),
                                         Func(self.setHealthForMe, int(self.maxHP * 0.35)), Func(self.updateHealthBar, 0)).start()

    def __soakRemoval(self, remove=0):
        if remove:
            if self.style.name == 'hydra':
                color = Point4((0.729, 0.729, 0.729, 1))
            elif self.style.name == 'charon':
                color = Point4((0.51, 0.49, 0.467, 1))
            elif self.style.name == 'nix':
                color = Point4((0.6, 0.6, 0.6, 1))
            elif self.style.name == 'styx':
                color = Point4((0.671, 0.671, 0.671, 1))
            elif self.style.name == 'kerberos':
                color = Point4((0.62, 0.659, 0.624, 1))
            elif self.style.name == 'cbutcher':
                color = Point4((0, 0, 0, 1))
            else:
                color = Point4(1.0, 1.0, 1.0, 1.0)
        else:
            color = SoakColor
        suitInterval = Parallel()
        actorNode = self.find('**/__Actor_modelRoot')
        actorCollection = actorNode.findAllMatches('*')
        texture = loader.loadTexture('phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
        parts = ()
        for thingIndex in xrange(0, actorCollection.getNumPaths()):
            thing = actorCollection[thingIndex]
            if thing.getName() not in ('joint_attachMeter', 'joint_shadow', 'joint_nameTag', 'def_nameTag'):
                if not self.dna.name == 'cbutcher' and not self.isShadow:
                    suitInterval.append(Func(thing.setColor, Point4(1.0, 1.0, 1.0, 1.0)))
        if not self.isSkeleton and not self.isShadow:
            hands = self.find('**/hands')
            suitInterval.append(Func(hands.setColorScale, self.handColor))
        if self.dna.name == 'lgator' and not self.isSkeleton:
            suitInterval.append(Func(self.makeDryLitigator))
        if self.dna.name == 'treasure' and not self.isSkeleton:
            suitInterval.append(Func(self.makeDryTreasurer))
        if self.style.name == 'safesupervis' and not self.isSkeleton:
            suitInterval.append(Func(self.makeDryFirestarter))
        if self.style.name == 'fires' and not self.isSkeleton:
            suitInterval.append(Func(self.makeDryFirestarter))
        self.healInterval =  Parallel(suitInterval).start()

    def addPendingQueuedDamage(self, dmg):
        if not hasattr(self, '_pendingQueuedDamage'):
            self._pendingQueuedDamage = 0
        self._pendingQueuedDamage += int(dmg)
        if self._pendingQueuedDamage < 0:
            self._pendingQueuedDamage = 0

    def clearPendingQueuedDamageAll(self):
        self._pendingQueuedDamage = 0
        self._pendingQueuedDeath = False

    def clearPendingQueuedDamage(self, dmg):
        if not hasattr(self, '_pendingQueuedDamage'):
            self._pendingQueuedDamage = 0
        self._pendingQueuedDamage -= int(dmg)
        if self._pendingQueuedDamage < 0:
            self._pendingQueuedDamage = 0

    def getQueuedProjectedHP(self):
        pending = getattr(self, '_pendingQueuedDamage', 0)
        return self.currHP - pending

    def getPendingQueuedDeath(self):
        return getattr(self, '_pendingQueuedDeath', False)

    def setPendingQueuedDeath(self, value):
        self._pendingQueuedDeath = bool(value)

    def _appendQueuedDeathOrRevive(self, suitTrack, projectedHP, battle):
        if projectedHP > 0 or self.isDead:
            return

        revives = self.getSkeleRevives()
        suitTrack.append(self.makeCogStepBackDeathInterval(battle))

        if self.dna.name == 'redd' and not self.isVirtual:
            suitTrack.append(MovieUtil.createSuitReviveRedd(self, battle))
            suitTrack.append(Func(self.makeDead))
        elif self.isVirtual:
            suitTrack.append(MovieUtil.createVirtualSuitDeathTrack(self, battle))
            suitTrack.append(Func(self.makeDead))
        elif not self.isSkeleton and revives >= 2:
            suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
        elif self.isSkeleton and revives >= 2:
            suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
        elif self.isSkeleton and revives >= 1 and not self.isRevive:
            suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
        elif not self.isSkeleton and revives >= 1:
            suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
        elif not self.isVirtual:
            suitTrack.append(MovieUtil.createSuitDeathTrack(self, battle))
            suitTrack.append(Func(self.makeDead))

    def makeHighPressureDeathMovie(self, hp, battle):
        suitTrack = Sequence()

        if self.currHP <= 0 or self.isDead:
            return suitTrack

        dmg = int(math.ceil(hp))
        if dmg <= 0:
            return suitTrack

        # Build-time pending splash state
        if not hasattr(self, '_pendingQueuedDamage'):
            self._pendingQueuedDamage = 0
        if not hasattr(self, '_pendingQueuedDeath'):
            self._pendingQueuedDeath = False

        oldPending = self._pendingQueuedDamage
        newPending = oldPending + dmg

        hpBeforeThisCall = self.currHP - oldPending
        hpAfterThisCall = self.currHP - newPending

        self._pendingQueuedDamage = newPending
        crossedZeroThisCall = hpBeforeThisCall > 0 and hpAfterThisCall <= 0

        if crossedZeroThisCall and not self._pendingQueuedDeath and not self.isDead:
            self._pendingQueuedDeath = True
            suitTrack.append(MovieUtil.shortCircuitTrack(self, battle))
            suitTrack.append(Func(self.makeDead))
        return suitTrack

    def makeSplashAndDeathInterval(self, tContact, hp, battle, bonus, attackTrack, level,
                                   reactName='squirt-small-react'):
        suitTrack = Sequence()

        if self.currHP <= 0 or self.isDead:
            return suitTrack

        dmg = int(math.ceil(hp))
        if dmg <= 0:
            return suitTrack

        # Build-time pending splash state
        if not hasattr(self, '_pendingQueuedDamage'):
            self._pendingQueuedDamage = 0
        if not hasattr(self, '_pendingQueuedDeath'):
            self._pendingQueuedDeath = False

        oldPending = self._pendingQueuedDamage
        newPending = oldPending + dmg

        hpBeforeThisCall = self.currHP - oldPending
        hpAfterThisCall = self.currHP - newPending

        self._pendingQueuedDamage = newPending

        if self.dna.name == 'redd':
            soakText = "SOAKED 1 ROUND"
            soakRounds = 1
        elif self.isVirtual:
            soakText = "SOAKED 2 ROUNDS"
            soakRounds = 1
        elif self.isSkeleton:
            soakText = "SOAKED 3 ROUNDS"
            soakRounds = 2
        else:
            soakText = "SOAKED 4 ROUNDS"
            soakRounds = 3

        showDamage = Parallel(
            Func(self.showHpTextNew, -dmg, text=soakText, attackTrack=attackTrack, colorCode=1),
            Func(self.setHealthForMe, -dmg),
            Func(self.updateHealthBar, 0),
            Func(self.setSoaked, 1),
            Func(self.makeSoaked, soakRounds)
        )

        reactTrack = Parallel(
            ActorInterval(self, reactName),
        )

        suitTrack.append(showDamage)
        suitTrack.append(reactTrack)
        suitTrack.append(Func(self.setNeutralAnimationDrop))

        if self.dna.name == 'sgoat' and self.isShielding:
            suitTrack.append(Func(self.addRageBuilding, dmg + 150))
        if self.dna.name == 'phouse':
            suitTrack.append(Func(self.addPowerhouseRotation, dmg + 150))
        if self.isSued:
            suitTrack.append(Func(self.makeSued, 3))

        crossedZeroThisCall = hpBeforeThisCall > 0 and hpAfterThisCall <= 0

        if crossedZeroThisCall and not self._pendingQueuedDeath and not self.isDead:
            self._pendingQueuedDeath = True
            revives = self.getSkeleRevives()
            suitTrack.append(self.makeCogStepBackDeathInterval(battle))

            if self.dna.name == 'redd' and not self.isVirtual:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveRedd(self, battle))
            elif self.isVirtual:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createVirtualSuitDeathTrack(self, battle))
            elif not self.isSkeleton and revives >= 2:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif self.isSkeleton and revives >= 2:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif self.isSkeleton and revives >= 1 and not self.isRevive:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif not self.isSkeleton and revives >= 1:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif not self.isVirtual:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitDeathTrack(self, battle))

        def _clearPendingSplash():
            if hasattr(self, '_pendingSplashDamage'):
                self._pendingSplashDamage -= dmg
                if self._pendingSplashDamage < 0:
                    self._pendingSplashDamage = 0

                if self._pendingSplashDamage == 0:
                    self._pendingSplashDeathQueued = False

        suitTrack.append(Func(_clearPendingSplash))

        return suitTrack

    def checkSplashDamage(self, tContact, hp, battle, bonus, attackTrack, level):
        if self.currHP > 0:
            if self.splashInterval:
                self.splashInterval.finish()
                self.splashInterval = None

            dmg = int(math.floor(hp))
            suitTrack = Sequence()
            updateHealthBar = Func(self.updateHealthBar, dmg)

            if self.dna.name == 'redd':
                showDamage = Parallel(
                    Func(self.showHpTextNew, -dmg, text="SOAKED 1 ROUND", attackTrack=attackTrack, colorCode=1),
                    Func(self.setHealthForMe, -dmg),
                    updateHealthBar
                )
                soakSuit = Func(self.makeSoaked, 1)
            elif self.isVirtual:
                showDamage = Parallel(
                    Func(self.showHpTextNew, -dmg, text="SOAKED 2 ROUNDS", attackTrack=attackTrack, colorCode=1),
                    Func(self.setHealthForMe, -dmg),
                    updateHealthBar
                )
                soakSuit = Func(self.makeSoaked, 1)
            elif self.isSkeleton:
                showDamage = Parallel(
                    Func(self.showHpTextNew, -dmg, text="SOAKED 3 ROUNDS", attackTrack=attackTrack, colorCode=1),
                    Func(self.setHealthForMe, -dmg),
                    updateHealthBar
                )
                soakSuit = Func(self.makeSoaked, 2)
            else:
                showDamage = Parallel(
                    Func(self.showHpTextNew, -dmg, text="SOAKED 4 ROUNDS", attackTrack=attackTrack, colorCode=1),
                    Func(self.setHealthForMe, -dmg),
                    updateHealthBar
                )
                soakSuit = Func(self.makeSoaked, 3)

            suitTrack.append(Func(self.setSoaked, 1))
            suitTrack.append(Parallel(showDamage, soakSuit))
            suitTrack.append(Func(self.setNeutralAnimationDrop))

            if self.dna.name == 'sgoat' and self.isShielding:
                suitTrack.append(Func(self.addRageBuilding, dmg + 150))
            if self.dna.name == 'phouse':
                suitTrack.append(Func(self.addPowerhouseRotation, dmg + 150))
            if self.isSued:
                suitTrack.append(Func(self.makeSued, 3))

            self.splashInterval = Sequence(suitTrack).start()

    def createSuitBellInterval(self):
        if self.style.name == 'liquid':
            for headPart in self.animatedHeadParts:
                headInterval = Sequence(ActorInterval(headPart, 'healing-bell'), Func(self.setNeutralAnimationHead))
                hasAnimatedHead = True
                Parallel(headInterval).start()

    def createSuitBellowInterval(self):
        if self.style.name == 'lgator' or self.style.name == 'treasure':
            suitInterval = Sequence(ActorInterval(self, 'bellow'), Func(self.setNeutralAnimation))
            for headPart in self.animatedHeadParts:
                headInterval = Sequence(ActorInterval(headPart, 'bellow'), Func(self.setNeutralAnimation))
                hasAnimatedHead = True
                Parallel(headInterval, suitInterval).start()

    def createSuitStunInterval(self):
        hasAnimatedHead = False
        # if self.headInterval:
        #     self.headInterval.finish()
        #     self.headInterval = None
        if self.style.name == 'hroller2':
            for headPart in self.animatedHeadParts:
                self.headInterval = Func(headPart.loop, 'stun', fromFrame=0, toFrame=22)
                hasAnimatedHead = True
        elif self.style.name == 'hrollers':
            for headPart in self.animatedHeadParts:
                self.headInterval = Func(headPart.loop, 'stun', fromFrame=0, toFrame=22)
                hasAnimatedHead = True
        elif self.style.name == 'hroller':
            for headPart in self.animatedHeadParts:
                self.headInterval = Func(headPart.loop, 'stun', fromFrame=0, toFrame=22)
                hasAnimatedHead = True
        else:
            for headPart in self.animatedHeadParts:
                self.headInterval = Func(headPart.loop, 'stun')
                hasAnimatedHead = True
        if hasAnimatedHead:
            self.headInterval.start()
        else:
            pass

    def createSuitRevvingUpInterval(self):
        if self.style.name == 'cbutcher':
            suitInterval = Sequence(ActorInterval(self, 'revvedup'), Func(self.setNeutralAnimation))
            for headPart in self.animatedHeadParts:
                headInterval = Sequence(ActorInterval(headPart, 'revvedup'), Func(self.setNeutralAnimation))
                hasAnimatedHead = True
                Parallel(headInterval, suitInterval).start()

    def createSuitSparkPlugInterval(self):
        if self.style.name == 'cbutcher':
            suitInterval = Sequence(ActorInterval(self, 'sparkplug', Func(self.setNeutralAnimation)))
            for headPart in self.animatedHeadParts:
                headInterval = Sequence(ActorInterval(headPart, 'sparkplug'), Func(self.setNeutralAnimation))
                hasAnimatedHead = True
                Parallel(headInterval, suitInterval).start()

    def createSuitScabbardInterval(self):
        if self.style.name == 'cbutcher':
            suitInterval = Sequence(ActorInterval(self, 'scabbard'), Func(self.setNeutralAnimation))
            for headPart in self.animatedHeadParts:
                headInterval = Sequence(ActorInterval(headPart, 'scabbard'), Func(self.setNeutralAnimation))
                hasAnimatedHead = True
                Parallel(headInterval, suitInterval).start()

    def createSuitSnapInterval(self):
        if self.style.name == 'lgator' or self.style.name == 'treasure':
            suitInterval = Sequence(ActorInterval(self, 'snap2'), Func(self.setNeutralAnimationDrop))
            for headPart in self.animatedHeadParts:
                headInterval = Sequence(ActorInterval(headPart, 'gsnap'), Func(self.setNeutralAnimationHead))
                hasAnimatedHead = True
                Parallel(headInterval, suitInterval).start()

    def checkSoakRounds(self):
        if self.splashInterval:
            self.splashInterval.finish()
            self.splashInterval = None
        if (self.isSoaked == 0 and self.actuallySoaked and not self.isDead) or self.dna.name == 'phouse' and self.currHP > 0:
            if self.dna.name == 'safesupervis':
                self.splashInterval = Sequence(Parallel(Func(self.makeUnDamageDown), Func(self.checkDamageDown, - 25), ActorInterval(self, 'soak', startTime=3.5), Sequence(Wait(1.0), Func(self.__soakRemoval, 1))), Func(self.makeUnSoaked), Func(self.setNeutralAnimationDrop)).start()
            else:
                self.splashInterval = Sequence(Parallel(ActorInterval(self, 'soak', startTime=3.5),  Sequence(Wait(1.0), Func(self.__soakRemoval, 1))), Func(self.makeUnSoaked), Func(self.setNeutralAnimationDrop)).start()

    def checkMarkRounds(self):
        if self.splashInterval:
            self.splashInterval.finish()
            self.splashInterval = None
        if self.isMarked == 0 and self.actuallyMarked and not self.isDead and self.currHP > 0:
            self.splashInterval = Sequence(Parallel(ActorInterval(self, 'squirt-small-react', startTime=2.25), Sequence(Wait(1.0), Func(self.splatSuit, 0, 1)), Func(self.makeUnMarked)), Func(self.setNeutralAnimationDrop)).start()

    def checkContractEnforcement(self):
        x = int((self.maxHP * self.hardMaxHP) - self.currHP)
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        if self.currHP >= (self.maxHP * self.hardMaxHP):
            self.healInterval = Parallel(Func(self.showHpTextNew, 0, text="CONTRACTED!", colorCode=1),
                                         Func(self.updateHealthBar, 0)).start()
        elif self.currHP + 95 > (self.maxHP * self.hardMaxHP):
            self.healInterval = Parallel(Func(self.showHpTextNew, x, text="CONTRACTED!", colorCode=1),
                                         Func(self.setHealthForMe, x), Func(self.updateHealthBar, 0)).start()
        else:
            self.healInterval = Parallel(Func(self.showHpTextNew, 95, text="CONTRACTED!", colorCode=1),
                                         Func(self.setHealthForMe, 95), Func(self.updateHealthBar, 0)).start()

    def checkPerformanceReview(self):
        x = int((self.maxHP * self.hardMaxHP) - self.currHP)
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        if not self.isManager:
            self.healInterval = Parallel(Func(self.showHpTextNew, x, text="OVERCHARGED!", colorCode=5),
                                         Func(self.setHealthForMe, x), Func(self.updateHealthBar, 0)).start()
        else:
            self.healInterval = Parallel(Func(self.showHpTextNew, 750, text="HEALED!", colorCode=1),
                                         Func(self.setHealthForMe, 750), Func(self.updateHealthBar, 0)).start()

    def checkContractEnforcementSafety(self):
        x = int((self.maxHP * self.hardMaxHP) - self.currHP)
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        if self.currHP >= (self.maxHP * self.hardMaxHP):
            self.healInterval = Parallel(Func(self.showHpTextNew, 0, text="CONTRACTED!", colorCode=1),
                                         Func(self.updateHealthBar, 0)).start()
        elif self.currHP + 200 > (self.maxHP * self.hardMaxHP):
            self.healInterval = Parallel(Func(self.showHpTextNew, x, text="CONTRACTED!", colorCode=1),
                                         Func(self.setHealthForMe, x), Func(self.updateHealthBar, 0)).start()
        else:
            self.healInterval = Parallel(Func(self.showHpTextNew, 200, text="CONTRACTED!", colorCode=1),
                                         Func(self.setHealthForMe, 200), Func(self.updateHealthBar, 0)).start()

    def checkRefinement(self):
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        if self.getManager():
            if self.currHP > 0:
                x = int((self.maxHP * self.hardMaxHP) - self.currHP)
                if self.currHP >= (self.maxHP * self.hardMaxHP):
                    self.healInterval = Parallel(Func(self.showHpTextNew, 0, text="REFINED!", colorCode=1),
                                                 Func(self.updateHealthBar, 0)).start()
                elif self.currHP + 200 > (self.maxHP * self.hardMaxHP):
                    self.healInterval = Parallel(Func(self.showHpTextNew, x, text="REFINED!", colorCode=1),
                                                 Func(self.setHealthForMe, x), Func(self.updateHealthBar, 0)).start()
                else:
                    self.healInterval = Parallel(Func(self.showHpTextNew, 200, text="REFINED!", colorCode=1),
                                                 Func(self.setHealthForMe, 200), Func(self.updateHealthBar, 0)).start()
        else:
            if self.currHP > 0:
                x = int((self.maxHP * self.hardMaxHP) - self.currHP)
                if self.currHP >= (self.maxHP * self.hardMaxHP):
                    self.healInterval = Parallel(Func(self.showHpTextNew, 0, text="REFINED!", colorCode=1),
                                                 Func(self.updateHealthBar, 0)).start()
                elif self.currHP + 175 > (self.maxHP * self.hardMaxHP):
                    self.healInterval = Parallel(Func(self.showHpTextNew, x, text="REFINED!", colorCode=1),
                                                 Func(self.setHealthForMe, x), Func(self.updateHealthBar, 0)).start()
                else:
                    self.healInterval = Parallel(Func(self.showHpTextNew, 175, text="REFINED!", colorCode=1),
                                                 Func(self.setHealthForMe, 175), Func(self.updateHealthBar, 0)).start()

    def checkRefinementManager(self):
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        x = int((self.maxHP * self.hardMaxHP) - self.currHP)
        if self.currHP >= (self.maxHP * self.hardMaxHP):
            self.healInterval = Parallel(Func(self.showHpTextNew, 0, text="REFINED!", colorCode=1),
                                         Func(self.updateHealthBar, 0)).start()
        elif self.currHP + 200 > (self.maxHP * self.hardMaxHP):
            self.healInterval = Parallel(Func(self.showHpTextNew, x, text="REFINED!", colorCode=1),
                                         Func(self.setHealthForMe, x), Func(self.updateHealthBar, 0)).start()
        else:
            self.healInterval = Parallel(Func(self.showHpTextNew, 200, text="REFINED!", colorCode=1),
                                         Func(self.setHealthForMe, 200), Func(self.updateHealthBar, 0)).start()

    def checkRefinementDerrickMan(self):
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        x = int((self.maxHP * self.hardMaxHP) - self.currHP)
        if self.currHP >= (self.maxHP * self.hardMaxHP):
            self.healInterval = Parallel(Func(self.showHpTextNew, 0, text="REFINED!", colorCode=1),
                                         Func(self.updateHealthBar, 0)).start()
        elif self.currHP + (self.maxHP * 0.4) > (self.maxHP * self.hardMaxHP):
            self.healInterval = Parallel(Func(self.showHpTextNew, x, text="REFINED!", colorCode=1),
                                         Func(self.setHealthForMe, x), Func(self.updateHealthBar, 0)).start()
        else:
            self.healInterval = Parallel(Func(self.showHpTextNew, int(math.ceil(self.maxHP * 0.4)), text="REFINED!", colorCode=1),
                                         Func(self.setHealthForMe, int(math.ceil(self.maxHP * 0.4))), Func(self.updateHealthBar, 0)).start()

    def checkRefinementPowerhouseManager(self):
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        x = int((self.maxHP * self.hardMaxHP) - self.currHP)
        if self.currHP >= (self.maxHP * self.hardMaxHP):
            self.healInterval = Parallel(Func(self.showHpTextNew, 0, text="REFINED!", colorCode=1),
                                         Func(self.updateHealthBar, 0)).start()
        elif self.currHP + 350 > (self.maxHP * self.hardMaxHP):
            self.healInterval = Parallel(Func(self.showHpTextNew, x, text="REFINED!", colorCode=1),
                                         Func(self.setHealthForMe, x), Func(self.updateHealthBar, 0)).start()
        else:
            self.healInterval = Parallel(Func(self.showHpTextNew, 350, text="REFINED!", colorCode=1),
                                         Func(self.setHealthForMe, 350), Func(self.updateHealthBar, 0)).start()

    def checkCameraRewind(self):
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        x = int((self.maxHP * self.hardMaxHP) - self.currHP)
        if self.currHP < self.maxHP and not self.currHP <= 0:
            if self.currHP >= (self.maxHP * self.hardMaxHP):
                self.healInterval = Parallel(Func(self.showHpTextNew, 0, text="REWIND!", colorCode=1),
                                             Func(self.updateHealthBar, 0)).start()
            elif self.currHP + 125 > (self.maxHP * self.hardMaxHP):
                self.healInterval = Parallel(Func(self.showHpTextNew, x, text="REWIND!", colorCode=1),
                                             Func(self.setHealthForMe, x), Func(self.updateHealthBar, 0)).start()
            else:
                self.healInterval = Parallel(Func(self.showHpTextNew, 125, text="REWIND!", colorCode=1),
                                             Func(self.setHealthForMe, 125), Func(self.updateHealthBar, 0)).start()
        else:
            self.healInterval = Sequence(Parallel(Func(self.showHpString, "+10% Damage!"), Func(self.makeDamageUp), Func(self.checkDamageUp, + 10))).start()

    def checkRefinementPowerhouse(self):
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        if self.getManager():
            if self.healInterval:
                self.healInterval.finish()
                self.healInterval = None
            x = int((self.maxHP * self.hardMaxHP) - self.currHP)
            if self.currHP >= (self.maxHP * self.hardMaxHP):
                self.healInterval = Parallel(Func(self.showHpTextNew, 0, text="REFINED!", colorCode=1),
                                             Func(self.updateHealthBar, 0)).start()
            elif self.currHP + 350 > (self.maxHP * self.hardMaxHP):
                self.healInterval = Parallel(Func(self.showHpTextNew, x, text="REFINED!", colorCode=1),
                                             Func(self.setHealthForMe, x), Func(self.updateHealthBar, 0)).start()
            else:
                self.healInterval = Parallel(Func(self.showHpTextNew, 350, text="REFINED!", colorCode=1),
                                             Func(self.setHealthForMe, 350), Func(self.updateHealthBar, 0)).start()
        else:
            x = int((self.maxHP * self.hardMaxHP) - self.currHP)
            if self.currHP >= (self.maxHP * self.hardMaxHP):
                self.healInterval = Parallel(Func(self.showHpTextNew, 0, text="REFINED!", colorCode=1),
                                             Func(self.updateHealthBar, 0)).start()
            elif self.currHP + 275 > (self.maxHP * self.hardMaxHP):
                self.healInterval = Parallel(Func(self.showHpTextNew, x, text="REFINED!", colorCode=1),
                                             Func(self.setHealthForMe, x), Func(self.updateHealthBar, 0)).start()
            else:
                self.healInterval = Parallel(Func(self.showHpTextNew, 275, text="REFINED!", colorCode=1),
                                             Func(self.setHealthForMe, 275), Func(self.updateHealthBar, 0)).start()

    def checkProfiteering(self, racketeer, battle):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None
        x = int(self.currHP)
        if self.currHP < (self.maxHP / 4):
            self.damageInterval = Sequence(Parallel(ActorInterval(self, 'pie-small-react'),
                                                   Func(self.showHpTextNew, x, text="-5% Damage!", colorCode=1),
                                                   Func(self.setHealthForMe, -x),
                                                   Func(self.updateHealthBar, 0)),
                               Func(self.setNeutralAnimationDrop)).start()
            self.healInterval = Sequence(Parallel(Func(racketeer.showHpTextNew, +x, text="+5% Damage!", colorCode=1), Func(racketeer.makeDamageUp), Func(racketeer.checkDamageUp, + 5),
                                                  Func(racketeer.setHealthForMe, +x),
                                                  Func(racketeer.updateHealthBar, 0)),
                                         Func(racketeer.setNeutralAnimationDrop)).start()
        else:
            self.damageInterval = Sequence(Parallel(ActorInterval(self, 'pie-small-react'),
                                                    Func(self.showHpTextNew, -(self.maxHP / 4), text="-5% Damage!", colorCode=1),
                                                  Func(self.setHealthForMe, -(self.maxHP / 4)),
                                                  Func(self.updateHealthBar, 0)),
                                         Func(self.setNeutralAnimationDrop)).start()
            self.healInterval = Sequence(Parallel(Func(racketeer.showHpTextNew, +(self.maxHP / 4), text="+5% Damage!", colorCode=1), Func(racketeer.makeDamageUp), Func(racketeer.checkDamageUp, + 5),
                                                   Func(racketeer.setHealthForMe, +(self.maxHP / 4)),
                                                   Func(racketeer.updateHealthBar, 0)),
                               Func(racketeer.setNeutralAnimationDrop)).start()

    def makeProfiteeringInterval(self, racketeer, battle):
        suitTrack = Sequence()

        if self.currHP <= 0 or self.isDead:
            return suitTrack

        x = int(self.currHP)
        dmg = int(self.maxHP / 4)

        if self.currHP < dmg:
            dmg = x

        if dmg <= 0:
            return suitTrack

        if not hasattr(self, '_pendingQueuedDamage'):
            self._pendingQueuedDamage = 0
        if not hasattr(self, '_pendingQueuedDeath'):
            self._pendingQueuedDeath = False

        oldPending = self._pendingQueuedDamage
        newPending = oldPending + dmg

        hpBeforeThisCall = self.currHP - oldPending
        hpAfterThisCall = self.currHP - newPending

        self._pendingQueuedDamage = newPending

        damageTrack = Sequence(
            Parallel(
                ActorInterval(self, 'pie-small-react'),
                Func(self.showHpTextNew, -dmg),
                Func(self.setHealthForMe, -dmg),
                Func(self.updateHealthBar, 0)
            ),
            Func(self.setNeutralAnimationDrop)
        )

        healTrack = Sequence(
            Parallel(
                Func(racketeer.showHpTextNew, +dmg, text="SYPHONED!", colorCode=1),
                Func(racketeer.makeDamageUp),
                Func(racketeer.checkDamageUp, +5),
                Func(racketeer.setHealthForMe, +dmg),
                Func(racketeer.updateHealthBar, 0)
            ),
            Func(racketeer.setNeutralAnimationDrop)
        )
        self.addPendingQueuedHealing(dmg)

        suitTrack.append(Parallel(damageTrack, healTrack))

        crossedZeroThisCall = hpBeforeThisCall > 0 and hpAfterThisCall <= 0

        if crossedZeroThisCall and not self._pendingQueuedDeath and not self.isDead:
            self._pendingQueuedDeath = True
            revives = self.getSkeleRevives()
            suitTrack.append(self.makeCogStepBackDeathInterval(battle))
            if self.dna.name == 'redd' and not self.isVirtual:
                suitTrack.append(MovieUtil.createSuitReviveRedd(self, battle))
                suitTrack.append(Func(self.makeDead))
            elif self.isVirtual:
                suitTrack.append(MovieUtil.createVirtualSuitDeathTrack(self, battle))
                suitTrack.append(Func(self.makeDead))
            elif not self.isSkeleton and revives >= 2:
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif self.isSkeleton and revives >= 2:
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif self.isSkeleton and revives >= 1 and not self.isRevive:
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif not self.isSkeleton and revives >= 1:
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif not self.isVirtual:
                suitTrack.append(MovieUtil.createSuitDeathTrack(self, battle))
                suitTrack.append(Func(self.makeDead))

        return suitTrack

    def makeUnionBustInterval(self, battle):
        suitTrack = Sequence()

        if self.currHP <= 0 or self.isDead:
            return suitTrack

        if not hasattr(self, '_pendingQueuedDamage'):
            self._pendingQueuedDamage = 0
        if not hasattr(self, '_pendingQueuedDeath'):
            self._pendingQueuedDeath = False

        oldPending = self._pendingQueuedDamage

        projectedCurrentHP = self.currHP - oldPending

        if projectedCurrentHP <= 0:
            return suitTrack

        dmg = int(projectedCurrentHP)

        newPending = oldPending + dmg

        self._pendingQueuedDamage = newPending

        showDamage = Sequence(Wait(2), Parallel(ActorInterval(self, 'flatten', duration = .55), MovieUtil.createSuitCrashTrack(self, battle), Func(self.showHpTextNew, -dmg, text="BUSTED!", colorCode=3),
                                   Func(self.setHealthForMe, - self.currHP),
                                   Func(self.updateHealthBar, 0)))

        suitTrack.append(showDamage)
        return suitTrack

    def makeHeadRollerInterval(self, battle):
        suitTrack = Sequence()

        if self.currHP <= 0 or self.isDead:
            return suitTrack

        if not hasattr(self, '_pendingQueuedDamage'):
            self._pendingQueuedDamage = 0
        if not hasattr(self, '_pendingQueuedDeath'):
            self._pendingQueuedDeath = False

        oldPending = self._pendingQueuedDamage

        # HP this suit effectively has left after already-queued damage
        projectedCurrentHP = self.currHP - oldPending

        # If queued damage already reduces it to 0 or below, do not sacrifice it again
        if projectedCurrentHP <= 0:
            return suitTrack

        dmg = int(projectedCurrentHP)
        if dmg <= 0:
            return suitTrack

        newPending = oldPending + dmg

        hpBeforeThisCall = projectedCurrentHP
        hpAfterThisCall = self.currHP - newPending

        self._pendingQueuedDamage = newPending

        showDamage = Sequence(
            ActorInterval(self, 'soak', duration=2.0),
            Parallel(
                Func(self.makeUnTarget),
                Sequence(
                    Func(self.setChatAbsolute, "Ouch.", CFSpeech | CFTimeout),
                    ActorInterval(self, 'pie-small-react'),
                    Func(self.setNeutralAnimationDrop)
                ),
                MovieUtil.spawnHeadExplosion(self, battle),
                Func(self.showHpTextNew, -dmg, text="TERMINATED!", colorCode=4),
                Func(self.setHealthForMe, -dmg),
                Func(self.updateHealthBar, 0)
            )
        )

        suitTrack.append(showDamage)

        crossedZeroThisCall = hpBeforeThisCall > 0 and hpAfterThisCall <= 0

        if crossedZeroThisCall and not self._pendingQueuedDeath and not self.isDead:
            self._pendingQueuedDeath = True
            suitTrack.append(MovieUtil.createSuitHeadlessDeathTrack(self, battle))
            suitTrack.append(Func(self.makeDead))

        return suitTrack

    def checkHeadRoller(self, battle):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None
        x = int(self.currHP)
        if self.currHP > 0 and not self.isDead:
            self.damageInterval = Sequence(ActorInterval(self, 'soak', duration = 2.0), Sequence(Parallel(Func(self.makeUnTarget), MovieUtil.spawnHeadExplosion(self, battle), Func(self.showHpTextNew, -self.currHP, text="TERMINATED!", colorCode=4),
                                            Func(self.setHealthForMe, - self.currHP),
                               Func(self.updateHealthBar, 0)),
                                           Func(self.setChatAbsolute, "Ouch.", CFSpeech | CFTimeout), Wait(1.0), MovieUtil.createSuitHeadlessDeathTrack(self, battle),
                                          )).start()

    def checkBalanceOfTheLedger(self, battle, hp):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None
        x = int(self.currHP)
        if (self.currHP > 0) and (self.currHP < self.maxHP) and not self.getManager():
            self.damageInterval = Sequence(Wait(1.5), Sequence(Parallel(ActorInterval(self, 'pie-small-react'), MovieUtil.spawnHeadExplosion(self, battle), Func(self.showHpTextNew, -self.currHP),
                                            Func(self.setHealthForMe, - self.currHP),
                               Func(self.updateHealthBar, 0)), MovieUtil.createSuitHeadlessDeathTrack(self, battle),
                                          )).start()
        if self.getManager() and self.currHP > 0:
            self.damageInterval = Sequence(Wait(1.5), Parallel(Func(self.showHpTextNew, + hp),
                                                             Func(self.setHealthForMe, + hp),
                                                             Func(self.updateHealthBar, 0))).start()
            self.addPendingQueuedHealing(hp)

    def makeBalanceTheLedgerInterval(self, hp, battle):
        suitTrack = Sequence()

        if self.currHP <= 0 or self.isDead:
            return suitTrack

        if not hasattr(self, '_pendingQueuedDamage'):
            self._pendingQueuedDamage = 0
        if not hasattr(self, '_pendingQueuedDeath'):
            self._pendingQueuedDeath = False

        oldPending = self._pendingQueuedDamage

        # HP this suit effectively has left after already-queued damage
        projectedCurrentHP = self.currHP - oldPending

        # If queued damage already reduces it to 0 or below, do not sacrifice it again
        if projectedCurrentHP <= 0:
            return suitTrack

        hpBeforeThisCall = projectedCurrentHP

        showDamage = Sequence(Wait(1.5), Sequence(Parallel(ActorInterval(self, 'pie-small-react'), MovieUtil.spawnHeadExplosion(self, battle), Func(self.showHpTextNew, -self.currHP),
                                            Func(self.setHealthForMe, - self.currHP),
                               Func(self.updateHealthBar, 0)), MovieUtil.createSuitHeadlessDeathTrack(self, battle),
                                          ))
        managerHealTrack = Sequence(Wait(1.5), Parallel(Func(self.showHpTextNew, + hp),
                                                             Func(self.setHealthForMe, + hp),
                                                             Func(self.updateHealthBar, 0)))
        if hpBeforeThisCall < self.maxHP and not self.getManager():
            suitTrack.append(showDamage)
        if self.getManager():
            self.addPendingQueuedHealing(hp)
            suitTrack.append(managerHealTrack)
        # crossedZeroThisCall = hpBeforeThisCall > 0 and hpAfterThisCall <= 0

        # if crossedZeroThisCall and not self._pendingQueuedDeath and not self.isDead:
        #     self._pendingQueuedDeath = True
            # revives = self.getSkeleRevives()
            # suitTrack.append(self.makeCogStepBackDeathInterval(battle))
            # if self.dna.name == 'redd' and not self.isVirtual:
            #     suitTrack.append(Func(self.makeDead))
            #     suitTrack.append(MovieUtil.createSuitReviveRedd(self, battle))
            # elif self.isVirtual:
            #     suitTrack.append(Func(self.makeDead))
            #     suitTrack.append(MovieUtil.createVirtualSuitDeathTrack(self, battle))
            # elif not self.isSkeleton and revives >= 2:
            #     suitTrack.append(Func(self.makeDead))
            #     suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            # elif self.isSkeleton and revives >= 2:
            #     suitTrack.append(Func(self.makeDead))
            #     suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            # elif self.isSkeleton and revives >= 1 and not self.isRevive:
            #     suitTrack.append(Func(self.makeDead))
            #     suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            # elif not self.isSkeleton and revives >= 1:
            #     suitTrack.append(Func(self.makeDead))
            #     suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            # elif not self.isVirtual:
            #     suitTrack.append(Func(self.makeDead))
            #     suitTrack.append(MovieUtil.createSuitDeathTrack(self, battle))
        return suitTrack

    def checkUnionBust(self, battle):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None
        x = int(self.currHP)
        if self.currHP > 0 and not self.getManager() and not self.isDead and not self.isContracted and not self.isContracted2 and not self.isOverpressured:
            self.damageInterval = Sequence(Wait(2), Parallel(ActorInterval(self, 'flatten', duration = .55), MovieUtil.createSuitCrashTrack(self, battle), Func(self.showHpTextNew, -self.currHP, text="BUSTED!", colorCode=3),
                                   Func(self.setHealthForMe, - self.currHP),
                                   Func(self.updateHealthBar, 0))).start()

    def checkSkelecogHP(self):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None
        x = int(self.currHP)
        self.damageInterval = Sequence(Func(self.setHealthForMe, 0), Func(self.updateHealthBar, 0)).start()

    def checkHeadRoller2(self, ambassador, battle):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        x = int(self.currHP)
        self.damageInterval = Sequence(Func(self.showHpTextNew, -self.currHP, text="GUILTY!", colorCode=4), Func(self.setHealthForMe, - self.currHP),
                               Func(self.updateHealthBar, 0)).start()
        ambassador.addPendingQueuedHealing(self.currHP)
        self.healInterval = Sequence(Parallel(Func(ambassador.showHpTextNew, +self.currHP, text="SYPHONED!", colorCode=1),
                                                   Func(ambassador.setHealthForMe, +self.currHP),
                                                   Func(ambassador.updateHealthBar, 0)),
                               Func(ambassador.setNeutralAnimation)).start()

    def checkHeadRollerChairman(self, ambassador, battle):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        x = int(self.currHP)
        self.damageInterval = Sequence(Func(self.showHpTextNew, -self.currHP, text="TERMINATED!", colorCode=4), Func(self.setHealthForMe, - self.currHP),
                               Func(self.updateHealthBar, 0)).start()
        self.healInterval = Sequence(Parallel(Func(ambassador.showHpTextNew, +self.currHP, text="SYPHONED!", colorCode=1),
                                                   Func(ambassador.setHealthForMe, +self.currHP),
                                                   Func(ambassador.updateHealthBar, 0)),
                               Func(ambassador.setNeutralAnimation)).start()
        ambassador.addPendingQueuedHealing(self.currHP)

    def _getSplatFilename2(self, level):
        splatDict = {
            0: 'tiny_splat_cake',
            1: 'tiny_splat_fruit',
            2: 'tiny_splat_cream',
            3: 'tiny_splat_cake',
            4: 'tiny_splat_fruit',
            5: 'tiny_splat_cream',
            6: 'tiny_splat_cake',
            7: 'tiny_splat_wedding'
        }
        return 'phase_5/maps/%s.png' % (
            splatDict[level]
        )

    def _getSplatFilename(self, level):
        splatDict = {
            0: 'splat_cake',
            1: 'splat_fruit',
            2: 'splat_cream',
            3: 'splat_cake',
            4: 'splat_fruit',
            5: 'splat_cream',
            6: 'splat_cake',
            7: 'splat_wedding'
        }
        return 'phase_5/maps/%s_%s.png' % (
            splatDict[level],
            random.choice((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12))
        )

    def _getSplatParts(self):
        if hasattr(self, '_splatParts'):
            return self._splatParts

        actorNode = self.find('**/__Actor_modelRoot')
        actorCollection = actorNode.findAllMatches('*')
        self._splatParts = []

        for i in xrange(actorCollection.getNumPaths()):
            thing = actorCollection[i]
            if thing.getName() not in ('joint_attachMeter', 'joint_shadow', 'joint_nameTag', 'def_nameTag'):
                self._splatParts.append(thing)

        return self._splatParts

    def _initCompositeSplat(self, sampleFilename):
        if hasattr(self, '_splatImage'):
            return

        sampleTex = loader.loadTexture(sampleFilename)
        if not sampleTex:
            print
            'Failed to load sample splat texture:', sampleFilename
            return

        sampleImage = PNMImage()
        sampleTex.store(sampleImage)

        if sampleImage.getNumChannels() < 1:
            print
            'Sample splat image invalid:', sampleFilename
            return

        x = sampleImage.getXSize()
        y = sampleImage.getYSize()

        self._splatImage = PNMImage(x, y, 4)

        # White RGB + zero alpha works well for decal-style overlays
        self._splatImage.fill(1.0, 1.0, 1.0)
        self._splatImage.alphaFill(0.0)

        self._splatTexture = Texture('composite-splat')
        self._splatTexture.load(self._splatImage)
        self._splatTexture.setWrapU(Texture.WMBorderColor)
        self._splatTexture.setWrapV(Texture.WMBorderColor)
        self._splatTexture.setBorderColor((0, 0, 0, 0))
        self._splatTexture.setMinfilter(Texture.FTLinear)
        self._splatTexture.setMagfilter(Texture.FTLinear)

        self._splatStage = TextureStage('compositeSplat')
        self._splatStage.setMode(TextureStage.MDecal)
        self._splatStage.setSavedResult(True)

        for thing in self._getSplatParts():
            #thing.setTransparency(TransparencyAttrib.MAlpha)
            thing.setTexture(self._splatStage, self._splatTexture, 1)

    def _addSplatToComposite(self, filename):
        self._initCompositeSplat(filename)

        if not hasattr(self, '_splatImage'):
            return

        splatTex = loader.loadTexture(filename)
        if not splatTex:
            print
            'Failed to load splat texture:', filename
            return

        splatImage = PNMImage()
        splatTex.store(splatImage)

        if splatImage.getNumChannels() < 1:
            print
            'Invalid splat image:', filename
            return

        if splatImage.getXSize() != self._splatImage.getXSize() or splatImage.getYSize() != self._splatImage.getYSize():
            print
            'Splat size mismatch:', filename
            return

        # Blend the new splat over the old composite
        self._splatImage.blendSubImage(splatImage, 0, 0, 0, 0)

        # Push updated pixels back into the same texture
        self._splatTexture.load(self._splatImage)

    def _clearCompositeSplat(self):
        if not hasattr(self, '_splatImage'):
            return

        self._splatImage.fill(1.0, 1.0, 1.0)
        self._splatImage.alphaFill(0.0)
        self._splatTexture.load(self._splatImage)

    def splatSuit(self, level, clear):
        if clear:
            self._clearCompositeSplat()
            return

        filename = self._getSplatFilename(level)
        self._addSplatToComposite(filename)

    def splatClear(self):
        stages = self.findAllTextureStages()
        for stage in stages:
            actorNode = self.find('**/__Actor_modelRoot')
            actorCollection = actorNode.findAllMatches('*')
            parts = ()
            for thingIndex in xrange(0, actorCollection.getNumPaths()):
                thing = actorCollection[thingIndex]
                if thing.getName() not in ('joint_attachMeter', 'joint_nameTag', 'joint_shadow', 'def_nameTag'):
                    if stage.getName().startswith('splat_wedding'):
                        thing.clearTexture(stage)
                    if stage.getName().startswith('splat_cream'):
                        thing.clearTexture(stage)
                    if stage.getName().startswith('splat_fruit'):
                        thing.clearTexture(stage)
                    if stage.getName().startswith('splat_cake'):
                        thing.clearTexture(stage)
          #  for headPart in self.headParts:
               # if stage.getName().startswith('splat_wedding'):
                #    headPart.clearTexture(stage)
              #  if stage.getName().startswith('splat_cream'):
                #    headPart.clearTexture(stage)
               # if stage.getName().startswith('splat_fruit'):
                 #   headPart.clearTexture(stage)
               # if stage.getName().startswith('splat_cake'):
                  #  headPart.clearTexture(stage)

    def checkAmbassadorPhase2(self):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None
        self.damageInterval = Parallel(Func(self.setHP, self.currHP)).start()

    def checkDamageUp(self, num):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None
        self.damageInterval = Parallel(Func(self.setDamageUp, self.getDamageUp() + num)).start()

    def checkCollectCall(self, num):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None
        self.damageInterval = Parallel(Func(self.setCollectCall, num), Func(self.makeCollectCall, num)).start()

    def checkDesperation(self, num):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None
        self.damageInterval = Parallel(Func(self.setDesperation, self.getDesperation() + num)).start()

    def checkExtraAttacks(self, num):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None
        self.damageInterval = Parallel(Func(self.makeExtraAttacks, self.getExtraAttacks() + num)).start()

    def checkExtraAbilities(self, num):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None
        self.damageInterval = Parallel(Func(self.makeExtraAbilities, self.getExtraAbilities() + num)).start()

    def checkDamageDown(self, num):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None
        self.damageInterval = Parallel(Func(self.setDamageDown, self.getDamageDown() + num)).start()

    def checkVulnerabilityUp(self, num):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None
        self.damageInterval = Parallel(Func(self.setVulnerability, self.getVulnerability() + num)).start()

    def checkDamageReduction(self, num):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None
        self.damageInterval = Parallel(Func(self.setDamageReduction, self.getDamageReduction() + num)).start()

    def makeDeathCheckInterval(self, battle):
        suitTrack = Sequence()

        if self.currHP <= 0 and not self.isDead:
            revives = self.getSkeleRevives()
            suitTrack.append(self.makeCogStepBackDeathInterval(battle))
            if self.dna.name == 'redd' and not self.isVirtual:
                suitTrack.append(MovieUtil.createSuitReviveRedd(self, battle))
                suitTrack.append(Func(self.makeDead))
            elif self.isVirtual:
                suitTrack.append(MovieUtil.createVirtualSuitDeathTrack(self, battle))
                suitTrack.append(Func(self.makeDead))
            elif not self.isSkeleton and revives >= 2:
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif self.isSkeleton and revives >= 2:
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif self.isSkeleton and revives >= 1 and not self.isRevive:
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif not self.isSkeleton and revives >= 1:
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif not self.isVirtual:
                suitTrack.append(MovieUtil.createSuitDeathTrack(self, battle))
                suitTrack.append(Func(self.makeDead))

        return suitTrack

    def checkDeathCheck(self, battle):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None
        if self.currHP <= 0 and not self.isDead:
            revives = self.getSkeleRevives()
            suitTrack = Sequence()
            if self.dna.name == 'redd' and not self.isVirtual:
                suitTrack.append(MovieUtil.createSuitReviveRedd(self, battle))
                suitTrack.append(Func(self.makeDead))
            elif self.isVirtual:
                suitTrack.append(MovieUtil.createVirtualSuitDeathTrack(self, battle))
                suitTrack.append(Func(self.makeDead))
            elif not self.isSkeleton and revives >= 2:
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif self.isSkeleton and revives >= 2:
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif self.isSkeleton and revives >= 1 and not self.isRevive:
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif not self.isSkeleton and revives >= 1:
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif not self.isVirtual:
                suitTrack.append(MovieUtil.createSuitDeathTrack(self, battle))
                suitTrack.append(Func(self.makeDead))
            self.damageInterval = Sequence(suitTrack).start()

    def checkDeathCheck2(self, suit, battle):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None
        if self.currHP <= 0 and not self.isDead:
            revives = self.getSkeleRevives()
            suitTrack = Sequence()
            if self.dna.name == 'redd' and not self.isVirtual:
                suitTrack.append(MovieUtil.createSuitReviveRedd(self, battle))
            elif self.isVirtual:
                suitTrack.append(MovieUtil.createVirtualSuitDeathTrack(self, battle))
            elif not self.isSkeleton and revives >= 2:
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif self.isSkeleton and revives >= 2:
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif self.isSkeleton and revives >= 1 and not self.isRevive:
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif not self.isSkeleton and revives >= 1:
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif not self.isVirtual:
                suitTrack.append(MovieUtil.createSuitDeathTrack(self, battle))
            self.damageInterval = Sequence(suitTrack).start()

    def checkSueDamage(self, battle):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None
        x = int(self.currHP)
        if self.currHP > 0 and self.isSued:
            if self.currHP < (self.maxHP / 4):
                self.damageInterval = Sequence(Parallel(ActorInterval(self, 'pie-small-react'),
                                                        Func(self.showHpTextNew, -x, text="SUED!", colorCode=1),
                                                        Func(self.setHealthForMe, -x),
                                                        Func(self.updateHealthBar, 0)), Func(self.setDizzy, 0),
                                               Func(self.setNeutralAnimation)).start()
            else:
                self.damageInterval = Sequence(Parallel(ActorInterval(self, 'pie-small-react'),
                                                        Func(self.showHpTextNew, -(self.maxHP / 4), text="SUED!", colorCode=1),
                                                        Func(self.setHealthForMe, -(self.maxHP / 4)), Func(self.setDizzy, 0),
                                                        Func(self.updateHealthBar, 0)), Func(self.setNeutralAnimation)
                                              ).start()

    def checkHeavyRainDamage(self, battle):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None
        x = int(self.currHP)
        if self.currHP > 0 and self.isHeavyRain:
            if self.currHP < self.getHeavyRainDamage():
                self.damageInterval = Sequence(Parallel(Func(self.showHpTextNew, -x),
                                                        Func(self.setHealthForMe, -x),
                                                        Func(self.updateHealthBar, 0),  MovieUtil.shortCircuitTrack(self, battle), Func(self.removeHeavyRainDamage))).start()
            else:
                self.damageInterval = Sequence(Parallel(Func(self.showHpTextNew, -self.getHeavyRainDamage()),
                                                        Func(self.setHealthForMe, -self.getHeavyRainDamage()),
                                                        Func(self.updateHealthBar, 0)), Func(self.removeHeavyRainDamage)).start()

    def checkSueDamage2(self, suit, battle):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None
        x = int(self.currHP)
        if self.currHP > 0 and not suit and self.isSued:
            if self.currHP < (self.maxHP / 4):
                self.damageInterval = Sequence(Parallel(ActorInterval(self, 'pie-small-react'),
                                                        Func(self.showHpTextNew, -x, text="SUED!", colorCode=1),
                                                        Func(self.setHealthForMe, -x),
                                                        Func(self.updateHealthBar, 0)),
                                               Func(self.setNeutralAnimation)).start()
            else:
                self.damageInterval = Sequence(Parallel(ActorInterval(self, 'pie-small-react'),
                                                        Func(self.showHpTextNew, -(self.maxHP / 4), text="SUED!", colorCode=1),
                                                        Func(self.setHealthForMe, -(self.maxHP / 4)),
                                                        Func(self.updateHealthBar, 0)), Func(self.setNeutralAnimation)
                                              ).start()

    def makeDamageLevelInterval(self, battle, levelDamage):
        suitTrack = Sequence()

        if self.currHP <= 0 or self.isDead:
            return suitTrack

        dmg = int(levelDamage)
        if dmg <= 0:
            return suitTrack
        if self.currHP < dmg:
            dmg = int(self.currHP)

        if not hasattr(self, '_pendingQueuedDamage'):
            self._pendingQueuedDamage = 0
        if not hasattr(self, '_pendingQueuedDeath'):
            self._pendingQueuedDeath = False

        oldPending = self._pendingQueuedDamage
        newPending = oldPending + dmg

        hpBeforeThisCall = self.currHP - oldPending
        hpAfterThisCall = self.currHP - newPending

        self._pendingQueuedDamage = newPending

        showDamage = Sequence(
            Parallel(
                ActorInterval(self, 'pie-small-react'),
                MovieUtil.createSuitStunInterval(self, 0, 2.0),
                Func(self.showHpTextNew, -dmg),
                Func(self.setHealthForMe, -dmg),
                Func(self.updateHealthBar, 0)
            ),
            Func(self.setNeutralAnimation)
        )

        suitTrack.append(showDamage)
        crossedZeroThisCall = hpBeforeThisCall > 0 and hpAfterThisCall <= 0

        if crossedZeroThisCall and not self._pendingQueuedDeath and not self.isDead:
            self._pendingQueuedDeath = True
            revives = self.getSkeleRevives()
            suitTrack.append(self.makeCogStepBackDeathInterval(battle))
            if self.dna.name == 'redd' and not self.isVirtual:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveRedd(self, battle))
            elif self.isVirtual:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createVirtualSuitDeathTrack(self, battle))
            elif not self.isSkeleton and revives >= 2:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif self.isSkeleton and revives >= 2:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif self.isSkeleton and revives >= 1 and not self.isRevive:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif not self.isSkeleton and revives >= 1:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif not self.isVirtual:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitDeathTrack(self, battle))
        return suitTrack

    def makeDamageInterval(self, battle, absorbDamage):
        suitTrack = Sequence()

        if self.currHP <= 0 or self.isDead:
            return suitTrack

        dmg = int(absorbDamage)
        if dmg <= 0:
            return suitTrack
        if self.currHP < dmg:
            dmg = int(self.currHP)

        if not hasattr(self, '_pendingQueuedDamage'):
            self._pendingQueuedDamage = 0
        if not hasattr(self, '_pendingQueuedDeath'):
            self._pendingQueuedDeath = False

        oldPending = self._pendingQueuedDamage
        newPending = oldPending + dmg

        hpBeforeThisCall = self.currHP - oldPending
        hpAfterThisCall = self.currHP - newPending

        self._pendingQueuedDamage = newPending

        if self.dna.name == 'safesupervis':
            showDamage = Sequence(
                Parallel(
                    ActorInterval(self, 'pie-small-react'),
                    MovieUtil.createSuitStunInterval(self, 0, 2.0),
                    Func(self.showHpTextNew, -dmg, text="OVERHEATED!", colorCode=5),
                    Func(self.setHealthForMe, -dmg),
                    Func(self.updateHealthBar, 0)
                ),
                Func(self.setNeutralAnimation)
            )
        else:
            showDamage = Sequence(
                Parallel(
                    ActorInterval(self, 'pie-small-react'),
                    MovieUtil.createSuitStunInterval(self, 0, 2.0),
                    Func(self.showHpText, -dmg),
                    Func(self.setHealthForMe, -dmg),
                    Func(self.updateHealthBar, 0)
                ),
                Func(self.setNeutralAnimation)
            )

        suitTrack.append(showDamage)
        crossedZeroThisCall = hpBeforeThisCall > 0 and hpAfterThisCall <= 0

        if crossedZeroThisCall and not self._pendingQueuedDeath and not self.isDead:
            self._pendingQueuedDeath = True
            revives = self.getSkeleRevives()
            suitTrack.append(self.makeCogStepBackDeathInterval(battle))
            if self.dna.name == 'redd' and not self.isVirtual:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveRedd(self, battle))
            elif self.isVirtual:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createVirtualSuitDeathTrack(self, battle))
            elif not self.isSkeleton and revives >= 2:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif self.isSkeleton and revives >= 2:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif self.isSkeleton and revives >= 1 and not self.isRevive:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif not self.isSkeleton and revives >= 1:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif not self.isVirtual:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitDeathTrack(self, battle))
        return suitTrack

    def makeDamageInterval2(self, battle, absorbDamage):
        suitTrack = Sequence()

        if self.currHP <= 0 or self.isDead:
            return suitTrack

        dmg = int(absorbDamage)
        if dmg <= 0:
            return suitTrack
        if self.currHP < dmg:
            dmg = int(self.currHP)

        if not hasattr(self, '_pendingQueuedDamage'):
            self._pendingQueuedDamage = 0
        if not hasattr(self, '_pendingQueuedDeath'):
            self._pendingQueuedDeath = False

        oldPending = self._pendingQueuedDamage
        newPending = oldPending + dmg

        hpBeforeThisCall = self.currHP - oldPending
        hpAfterThisCall = self.currHP - newPending

        self._pendingQueuedDamage = newPending

        showDamage = Sequence(
                Parallel(
                    ActorInterval(self, 'pie-small-react'),
                    MovieUtil.createSuitStunInterval(self, 0, 2.0),
                    Func(self.showHpText, -dmg),
                    Func(self.setHealthForMe, -dmg),
                    Func(self.updateHealthBar, 0)
                ),
                Func(self.setNeutralAnimation)
            )

        suitTrack.append(showDamage)
        crossedZeroThisCall = hpBeforeThisCall > 0 and hpAfterThisCall <= 0

        if crossedZeroThisCall and not self._pendingQueuedDeath and not self.isDead:
            self._pendingQueuedDeath = True
            revives = self.getSkeleRevives()
            suitTrack.append(self.makeCogStepBackDeathInterval(battle))
            if self.dna.name == 'redd' and not self.isVirtual:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveRedd(self, battle))
            elif self.isVirtual:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createVirtualSuitDeathTrack(self, battle))
            elif not self.isSkeleton and revives >= 2:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif self.isSkeleton and revives >= 2:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif self.isSkeleton and revives >= 1 and not self.isRevive:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif not self.isSkeleton and revives >= 1:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif not self.isVirtual:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitDeathTrack(self, battle))
        return suitTrack

    def makeAbsorbDamageInterval(self, battle, absorbDamage):
        suitTrack = Sequence()

        if self.currHP <= 0 or self.isDead:
            return suitTrack

        dmg = int(absorbDamage)
        if dmg <= 0:
            return suitTrack
        if self.currHP < dmg:
            dmg = int(self.currHP)

        if not hasattr(self, '_pendingQueuedDamage'):
            self._pendingQueuedDamage = 0
        if not hasattr(self, '_pendingQueuedDeath'):
            self._pendingQueuedDeath = False

        oldPending = self._pendingQueuedDamage
        newPending = oldPending + dmg

        hpBeforeThisCall = self.currHP - oldPending
        hpAfterThisCall = self.currHP - newPending

        self._pendingQueuedDamage = newPending

        if self.dna.name == 'sgoat':
            showDamage = Sequence(
                Parallel(
                    ActorInterval(self, 'pie-small-react'),
                    MovieUtil.createSuitStunInterval(self, 0, 2.0),
                    Func(self.showHpTextNew, -dmg, text="ABSORBED!", colorCode=1),
                    Func(self.setHealthForMe, -dmg),
                    Func(self.updateHealthBar, 0)
                ),
                Func(self.setNeutralAnimation),
                Func(self.addRageBuilding, int(dmg))
            )
        else:
            showDamage = Sequence(
                Parallel(
                    ActorInterval(self, 'pie-small-react'),
                    MovieUtil.createSuitStunInterval(self, 0, 2.0),
                    Func(self.showHpTextNew, -dmg, text="ABSORBED!", colorCode=1),
                    Func(self.setHealthForMe, -dmg),
                    Func(self.updateHealthBar, 0)
                ),
                Func(self.setNeutralAnimation)
            )

        suitTrack.append(showDamage)
        crossedZeroThisCall = hpBeforeThisCall > 0 and hpAfterThisCall <= 0

        if crossedZeroThisCall and not self._pendingQueuedDeath and not self.isDead:
            self._pendingQueuedDeath = True
            revives = self.getSkeleRevives()
            suitTrack.append(self.makeCogStepBackDeathInterval(battle))
            if self.dna.name == 'redd' and not self.isVirtual:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveRedd(self, battle))
            elif self.isVirtual:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createVirtualSuitDeathTrack(self, battle))
            elif not self.isSkeleton and revives >= 2:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif self.isSkeleton and revives >= 2:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif self.isSkeleton and revives >= 1 and not self.isRevive:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif not self.isSkeleton and revives >= 1:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif not self.isVirtual:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitDeathTrack(self, battle))
        return suitTrack

    def makeBarInterval(self, battle, damage):
        suitTrack = Sequence()

        if self.currHP <= 0 or self.isDead:
            return suitTrack

        if not hasattr(self, '_pendingQueuedDamage'):
            self._pendingQueuedDamage = 0
        if not hasattr(self, '_pendingQueuedDeath'):
            self._pendingQueuedDeath = False

        oldPending = self._pendingQueuedDamage

        # HP this suit effectively has left after already-queued damage
        projectedCurrentHP = self.currHP - oldPending

        # If queued damage already reduces it to 0 or below, do not sacrifice it again
        if projectedCurrentHP <= 0:
            return suitTrack

        dmg = damage
        if dmg <= 0:
            return suitTrack

        newPending = oldPending + dmg

        hpBeforeThisCall = projectedCurrentHP
        hpAfterThisCall = self.currHP - newPending

        self._pendingQueuedDamage = newPending

        showDamage = Sequence(
            Parallel(
                ActorInterval(self, 'flatten'),
                Func(self.showHpTextNew, -dmg),
                Func(self.setHealthForMe, -dmg),
                Func(self.updateHealthBar, 0)
            ),
            Func(self.setNeutralAnimationDrop)
        )

        suitTrack.append(showDamage)
        crossedZeroThisCall = hpBeforeThisCall > 0 and hpAfterThisCall <= 0

        if crossedZeroThisCall and not self._pendingQueuedDeath and not self.isDead:
            self._pendingQueuedDeath = True
            revives = self.getSkeleRevives()
            suitTrack.append(self.makeCogStepBackDeathInterval(battle))
            if self.dna.name == 'redd' and not self.isVirtual:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveRedd(self, battle))
            elif self.isVirtual:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createVirtualSuitDeathTrack(self, battle))
            elif not self.isSkeleton and revives >= 2:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif self.isSkeleton and revives >= 2:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif self.isSkeleton and revives >= 1 and not self.isRevive:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif not self.isSkeleton and revives >= 1:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif not self.isVirtual:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitDeathTrack(self, battle))
        return suitTrack

    def makeSueDamageInterval(self, battle):
        suitTrack = Sequence()

        if self.currHP <= 0 or self.isDead:
            return suitTrack
        if not self.isSued:
            return suitTrack

        if not hasattr(self, '_pendingQueuedDamage'):
            self._pendingQueuedDamage = 0
        if not hasattr(self, '_pendingQueuedDeath'):
            self._pendingQueuedDeath = False

        oldPending = self._pendingQueuedDamage

        # HP this suit effectively has left after already-queued damage
        projectedCurrentHP = self.currHP - oldPending

        # If queued damage already reduces it to 0 or below, do not sacrifice it again
        if projectedCurrentHP <= 0:
            return suitTrack

        dmg = int(self.maxHP / 4)
        if dmg <= 0:
            return suitTrack
        if self.currHP < dmg:
            dmg = int(self.currHP)

        newPending = oldPending + dmg

        hpBeforeThisCall = projectedCurrentHP
        hpAfterThisCall = self.currHP - newPending

        self._pendingQueuedDamage = newPending

        showDamage = Sequence(
            Parallel(
                ActorInterval(self, 'pie-small-react'),
                Func(self.showHpTextNew, -dmg, text="SUED!", colorCode=1),
                Func(self.setHealthForMe, -dmg),
                Func(self.setDizzy, 0),
                Func(self.updateHealthBar, 0)
            ),
            Func(self.setNeutralAnimationDrop)
        )

        suitTrack.append(showDamage)
        crossedZeroThisCall = hpBeforeThisCall > 0 and hpAfterThisCall <= 0

        if crossedZeroThisCall and not self._pendingQueuedDeath and not self.isDead:
            self._pendingQueuedDeath = True
            revives = self.getSkeleRevives()
            suitTrack.append(self.makeCogStepBackDeathInterval(battle))
            if self.dna.name == 'redd' and not self.isVirtual:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveRedd(self, battle))
            elif self.isVirtual:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createVirtualSuitDeathTrack(self, battle))
            elif not self.isSkeleton and revives >= 2:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif self.isSkeleton and revives >= 2:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif self.isSkeleton and revives >= 1 and not self.isRevive:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif not self.isSkeleton and revives >= 1:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif not self.isVirtual:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitDeathTrack(self, battle))
        return suitTrack

    def makeZapDamageInterval(self, battle):
        suitTrack = Sequence()

        if self.currHP <= 0 or self.isDead:
            return suitTrack
        if not self.isZapped or self.freshlyZapped:
            return suitTrack

        if not hasattr(self, '_pendingQueuedDamage'):
            self._pendingQueuedDamage = 0
        if not hasattr(self, '_pendingQueuedDeath'):
            self._pendingQueuedDeath = False

        oldPending = self._pendingQueuedDamage

        # HP this suit effectively has left after already-queued damage
        projectedCurrentHP = self.currHP - oldPending

        # If queued damage already reduces it to 0 or below, do not sacrifice it again
        if projectedCurrentHP <= 0:
            return suitTrack

        dmg = int(self.getZapCondition())
        if dmg <= 0:
            return suitTrack
        if self.currHP < dmg:
            dmg = int(self.currHP)

        newPending = oldPending + dmg

        hpBeforeThisCall = projectedCurrentHP
        hpAfterThisCall = self.currHP - newPending

        self._pendingQueuedDamage = newPending

        showDamage = Parallel(
            ActorInterval(self, 'small-zap'),
            MovieUtil.createSuitStunInterval(self, 0, 2.0),
            Func(self.showHpTextNew, -dmg, text="AFTERSHOCK!", colorCode=3),
            Func(self.setHealthForMe, -dmg),
            Func(self.updateHealthBar, 0)
        )

        suitTrack.append(showDamage)
        suitTrack.append(Func(self.makeUnZapped))
        suitTrack.append(Func(self.setNeutralAnimation))

        crossedZeroThisCall = hpBeforeThisCall > 0 and hpAfterThisCall <= 0

        if crossedZeroThisCall and not self._pendingQueuedDeath and not self.isDead:
            self._pendingQueuedDeath = True
            revives = self.getSkeleRevives()

            if self.dna.name == 'redd' and not self.isVirtual:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveRedd(self, battle))
            elif self.isVirtual:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitHeadlessDeathTrack(self, battle))
            elif not self.isSkeleton and revives >= 2:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif self.isSkeleton and revives >= 2:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif self.isSkeleton and revives >= 1 and not self.isRevive:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif not self.isSkeleton and revives >= 1:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif not self.isVirtual:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitHeadlessDeathTrack(self, battle))
        return suitTrack

    def checkZapDamage(self, battle):
        suitTrack = Sequence()
        x = int(self.currHP)
        if self.currHP > 0 and self.isZapped:
            if self.currHP < self.getZapCondition():
                damageInterval = Sequence(Parallel(ActorInterval(self, 'small-zap'), MovieUtil.createSuitStunInterval(self, 0, 2.0),
                                                        Func(self.showHpTextNew, -x, text="AFTERSHOCK!", colorCode=3),
                                                        Func(self.setHealthForMe, -x),
                                                        Func(self.updateHealthBar, 0)), Func(self.makeUnZapped),
                                               Func(self.setNeutralAnimation))
                suitTrack.append(damageInterval)
            else:
                damageInterval = Sequence(Parallel(ActorInterval(self, 'small-zap'), MovieUtil.createSuitStunInterval(self, 0, 2.0),
                                                        Func(self.showHpTextNew, -self.getZapCondition(), text="AFTERSHOCK!", colorCode=3),
                                                        Func(self.setHealthForMe, -self.getZapCondition()), Func(self.makeUnZapped),
                                                        Func(self.updateHealthBar, 0)), Func(self.setNeutralAnimation),
                                              )
                suitTrack.append(damageInterval)
        return suitTrack

    def checkZapDamage2(self, suit, battle):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None
        x = int(self.currHP)
        if self.currHP > 0 and not suit and self.isZapped:
            if self.currHP < self.getZapCondition():
                self.damageInterval = Sequence(Parallel(ActorInterval(self, 'small-zap'), MovieUtil.createSuitStunInterval(self, 0, 2.0),
                                                        Func(self.showHpTextNew, -x, text="AFTERSHOCK!", colorCode=3),
                                                        Func(self.setHealthForMe, -x),
                                                        Func(self.updateHealthBar, 0)),
                                               Func(self.setNeutralAnimation)).start()
            else:
                self.damageInterval = Sequence(Parallel(ActorInterval(self, 'small-zap'), MovieUtil.createSuitStunInterval(self, 0, 2.0),
                                                        Func(self.showHpTextNew, -self.getZapCondition(), text="AFTERSHOCK!", colorCode=3),
                                                        Func(self.setHealthForMe, -self.getZapCondition()),
                                                        Func(self.updateHealthBar, 0)), Func(self.setNeutralAnimation)
                                              ).start()

    def checkPhantomEntrySacrifice(self, videog):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        x = int(self.currHP)
        self.damageInterval = Sequence(Func(self.showHpText, -x),
                                           Func(self.setHealthForMe, -x),
                                           Func(self.updateHealthBar, 0),
                                           Func(self.setNeutralAnimationDrop)).start()
        self.healInterval = Sequence(Func(videog.showHpText, +x),
                                         Func(videog.setHealthForMe, +x),
                                         Func(videog.updateHealthBar, 0),
                                         Func(videog.setNeutralAnimationDrop)).start()
        videog.addPendingQueuedHealing(x)

    def checkBroadcasterDonation(self, videog, battle):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        x = int(self.currHP)
        if self.currHP < 1111:
            self.damageInterval = Sequence(ActorInterval(self, 'mob-mentality', endTime=1), Wait(5.0),
                                                   Func(self.showHpText, -x),
                                                   Func(self.setHealthForMe, -x),
                                                   Func(self.updateHealthBar, 0), ActorInterval(self, 'mob-mentality', startTime=1, endTime=0),
                               Func(self.setNeutralAnimation)).start()
            self.healInterval = Sequence(ActorInterval(videog, 'mob-mentality', endTime=1), Wait(5.0),
                                                  Func(videog.showHpText, +x),
                                                  Func(videog.setHealthForMe, +x),
                                                  Func(videog.updateHealthBar, 0), ActorInterval(videog, 'mob-mentality', startTime=1, endTime=0),
                                         Func(videog.setNeutralAnimation)).start()
            videog.addPendingQueuedHealing(x)
        else:
            self.damageInterval = Sequence(ActorInterval(self, 'mob-mentality', endTime=1), Wait(5.0),
                                                  Func(self.showHpText, -(self.maxHP / 3)),
                                                  Func(self.setHealthForMe, -(self.maxHP / 3)),
                                                  Func(self.updateHealthBar, 0), ActorInterval(self, 'mob-mentality', startTime=1, endTime=0),
                                         Func(self.setNeutralAnimation)).start()
            self.healInterval = Sequence(ActorInterval(videog, 'mob-mentality', endTime=1), Wait(5.0), Func(videog.showHpText, +(self.maxHP / 3)),
                                                   Func(videog.setHealthForMe, +(self.maxHP / 3)),
                                                   Func(videog.updateHealthBar, 0), ActorInterval(videog, 'mob-mentality', startTime=1, endTime=0),
                               Func(videog.setNeutralAnimation)).start()
            videog.addPendingQueuedHealing((self.maxHP / 3))

    def checkBroadcasterDonation2(self, videog, battle):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        x = int(self.currHP)
        if self.currHP < 111:
            self.damageInterval = Sequence(ActorInterval(self, 'mob-mentality', endTime=1),
                                                   Func(self.showHpText, -x),
                                                   Func(self.setHealthForMe, -x),
                                                   Func(self.updateHealthBar, 0), ActorInterval(self, 'slip-forward'),
                               Func(self.setNeutralAnimation)).start()
            self.healInterval = Sequence(ActorInterval(videog, 'mob-mentality', endTime=1),
                                                  Func(videog.showHpText, +x),
                                                  Func(videog.setHealthForMe, +x),
                                                  Func(videog.updateHealthBar, 0), ActorInterval(videog, 'pie-small-react'),
                                         Func(videog.setNeutralAnimation)).start()
            videog.addPendingQueuedHealing(x)
        else:
            self.damageInterval = Sequence(ActorInterval(self, 'mob-mentality', endTime=1),
                                                  Func(self.showHpText, -111),
                                                  Func(self.setHealthForMe, -111),
                                                  Func(self.updateHealthBar, 0), ActorInterval(self, 'slip-forward'),
                                         Func(self.setNeutralAnimation)).start()
            self.healInterval = Sequence(ActorInterval(videog, 'mob-mentality', endTime=1), Func(videog.showHpText, +111),
                                                   Func(videog.setHealthForMe, +111),
                                                   Func(videog.updateHealthBar, 0), ActorInterval(videog, 'pie-small-react'),
                               Func(videog.setNeutralAnimation)).start()
            videog.addPendingQueuedHealing(111)

    def makeBroadcasterDonationInterval(self, videog, battle):
        suitTrack = Sequence()

        if self.currHP <= 0 or self.isDead:
            return suitTrack

        x = int(self.currHP)
        dmg = int(self.maxHP / 3)

        if self.currHP < 1111:
            dmg = x

        if dmg <= 0:
            return suitTrack

        if not hasattr(self, '_pendingQueuedDamage'):
            self._pendingQueuedDamage = 0
        if not hasattr(self, '_pendingQueuedDeath'):
            self._pendingQueuedDeath = False

        oldPending = self._pendingQueuedDamage
        newPending = oldPending + dmg

        hpBeforeThisCall = self.currHP - oldPending
        hpAfterThisCall = self.currHP - newPending

        self._pendingQueuedDamage = newPending

        damageTrack = Sequence(
            ActorInterval(self, 'mob-mentality', endTime=1),
            Wait(5.0),
            Func(self.showHpText, -dmg),
            Func(self.setHealthForMe, -dmg),
            Func(self.updateHealthBar, 0),
            ActorInterval(self, 'mob-mentality', startTime=1, endTime=0),
            Func(self.setNeutralAnimationDrop)
        )

        healTrack = Sequence(
            ActorInterval(videog, 'mob-mentality', endTime=1),
            Wait(5.0),
            Func(videog.showHpText, +dmg),
            Func(videog.setHealthForMe, +dmg),
            Func(videog.updateHealthBar, 0),
            ActorInterval(videog, 'mob-mentality', startTime=1, endTime=0),
            Func(videog.setNeutralAnimationDrop)
        )
        videog.addPendingQueuedHealing(dmg)

        suitTrack.append(Parallel(damageTrack, healTrack))

        crossedZeroThisCall = hpBeforeThisCall > 0 and hpAfterThisCall <= 0

        if crossedZeroThisCall and not self._pendingQueuedDeath and not self.isDead:
            self._pendingQueuedDeath = True
            revives = self.getSkeleRevives()
            suitTrack.append(self.makeCogStepBackDeathInterval(battle))
            if self.dna.name == 'redd' and not self.isVirtual:
                suitTrack.append(MovieUtil.createSuitReviveRedd(self, battle))
                suitTrack.append(Func(self.makeDead))
            elif self.isVirtual:
                suitTrack.append(MovieUtil.createVirtualSuitDeathTrack(self, battle))
                suitTrack.append(Func(self.makeDead))
            elif not self.isSkeleton and revives >= 2:
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif self.isSkeleton and revives >= 2:
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif self.isSkeleton and revives >= 1 and not self.isRevive:
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif not self.isSkeleton and revives >= 1:
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif not self.isVirtual:
                suitTrack.append(MovieUtil.createSuitDeathTrack(self, battle))
                suitTrack.append(Func(self.makeDead))

        return suitTrack

    def makeSilhouetteDonation(self, videog, battle):
        suitTrack = Sequence()

        if self.currHP <= 0 or self.isDead:
            return suitTrack

        x = int(self.currHP)
        dmg = 3000

        if self.currHP < 3000:
            dmg = x

        if dmg <= 0:
            return suitTrack

        if not hasattr(self, '_pendingQueuedDamage'):
            self._pendingQueuedDamage = 0
        if not hasattr(self, '_pendingQueuedDeath'):
            self._pendingQueuedDeath = False

        oldPending = self._pendingQueuedDamage
        newPending = oldPending + dmg

        hpBeforeThisCall = self.currHP - oldPending
        hpAfterThisCall = self.currHP - newPending

        self._pendingQueuedDamage = newPending

        damageTrack = Sequence(Func(self.showHpText, -dmg),
            Func(self.setHealthForMe, -dmg),
            Func(self.updateHealthBar, 0), Func(self.setNeutralAnimationDrop)
        )

        healTrack = Sequence(Func(videog.showHpText, +dmg),
            Func(videog.setHealthForMe, +dmg),
            Func(videog.updateHealthBar, 0),
            Func(videog.setNeutralAnimationDrop)
        )
        videog.addPendingQueuedHealing(dmg)

        suitTrack.append(Parallel(damageTrack, healTrack))

        crossedZeroThisCall = hpBeforeThisCall > 0 and hpAfterThisCall <= 0

        if crossedZeroThisCall and not self._pendingQueuedDeath and not self.isDead:
            self._pendingQueuedDeath = True
            revives = self.getSkeleRevives()
            suitTrack.append(self.makeCogStepBackDeathInterval(battle))
            if self.dna.name == 'redd' and not self.isVirtual:
                suitTrack.append(MovieUtil.createSuitReviveRedd(self, battle))
                suitTrack.append(Func(self.makeDead))
            elif self.isVirtual:
                suitTrack.append(MovieUtil.createVirtualSuitDeathTrack(self, battle))
                suitTrack.append(Func(self.makeDead))
            elif not self.isSkeleton and revives >= 2:
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif self.isSkeleton and revives >= 2:
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif self.isSkeleton and revives >= 1 and not self.isRevive:
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif not self.isSkeleton and revives >= 1:
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif not self.isVirtual:
                suitTrack.append(MovieUtil.createSuitDeathTrack(self, battle))
                suitTrack.append(Func(self.makeDead))

        return suitTrack

    def makeRedundantAuthorityInterval(self, battle):
        suitTrack = Sequence()

        if self.currHP <= 0 or self.isDead:
            return suitTrack

        dmg = 375
        if dmg <= 0:
            return suitTrack
        if self.currHP < dmg:
            dmg = int(self.currHP)

        if not hasattr(self, '_pendingQueuedDamage'):
            self._pendingQueuedDamage = 0
        if not hasattr(self, '_pendingQueuedDeath'):
            self._pendingQueuedDeath = False

        oldPending = self._pendingQueuedDamage
        newPending = oldPending + dmg

        hpBeforeThisCall = self.currHP - oldPending
        hpAfterThisCall = self.currHP - newPending

        self._pendingQueuedDamage = newPending

        suitTrack.append(Func(self.setNeutralAnimationDrop))

        crossedZeroThisCall = hpBeforeThisCall > 0 and hpAfterThisCall <= 0

        if crossedZeroThisCall and not self._pendingQueuedDeath and not self.isDead:
            self._pendingQueuedDeath = True
            revives = self.getSkeleRevives()

            if self.dna.name == 'redd' and not self.isVirtual:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveRedd(self, battle))
            elif self.isVirtual:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createVirtualSuitDeathTrack(self, battle))
            elif not self.isSkeleton and revives >= 2:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif self.isSkeleton and revives >= 2:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif self.isSkeleton and revives >= 1 and not self.isRevive:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif not self.isSkeleton and revives >= 1:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif not self.isVirtual:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitHeadlessDeathTrack(self, battle))
        return suitTrack

    def makeBroadcasterDonation2Interval(self, videog, battle):
        suitTrack = Sequence()

        if self.currHP <= 0 or self.isDead:
            return suitTrack

        x = int(self.currHP)
        dmg = 111

        if self.currHP < 111:
            dmg = x

        if dmg <= 0:
            return suitTrack

        if not hasattr(self, '_pendingQueuedDamage'):
            self._pendingQueuedDamage = 0
        if not hasattr(self, '_pendingQueuedDeath'):
            self._pendingQueuedDeath = False

        oldPending = self._pendingQueuedDamage
        newPending = oldPending + dmg

        hpBeforeThisCall = self.currHP - oldPending
        hpAfterThisCall = self.currHP - newPending

        self._pendingQueuedDamage = newPending

        damageTrack = Sequence(
            ActorInterval(self, 'mob-mentality', endTime=1),
            Func(self.showHpText, -dmg),
            Func(self.setHealthForMe, -dmg),
            Func(self.updateHealthBar, 0),
            ActorInterval(self, 'slip-forward'),
            Func(self.setNeutralAnimationDrop)
        )

        healTrack = Sequence(
            ActorInterval(videog, 'mob-mentality', endTime=1),
            Func(videog.showHpText, +dmg),
            Func(videog.setHealthForMe, +dmg),
            Func(videog.updateHealthBar, 0),
            ActorInterval(videog, 'pie-small-react'),
            Func(videog.setNeutralAnimationDrop)
        )
        videog.addPendingQueuedHealing(dmg)

        suitTrack.append(Parallel(damageTrack, healTrack))

        crossedZeroThisCall = hpBeforeThisCall > 0 and hpAfterThisCall <= 0

        if crossedZeroThisCall and not self._pendingQueuedDeath and not self.isDead:
            self._pendingQueuedDeath = True
            revives = self.getSkeleRevives()
            suitTrack.append(self.makeCogStepBackDeathInterval(battle))
            if self.dna.name == 'redd' and not self.isVirtual:
                suitTrack.append(MovieUtil.createSuitReviveRedd(self, battle))
                suitTrack.append(Func(self.makeDead))
            elif self.isVirtual:
                suitTrack.append(MovieUtil.createVirtualSuitDeathTrack(self, battle))
                suitTrack.append(Func(self.makeDead))
            elif not self.isSkeleton and revives >= 2:
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif self.isSkeleton and revives >= 2:
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif self.isSkeleton and revives >= 1 and not self.isRevive:
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif not self.isSkeleton and revives >= 1:
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif not self.isVirtual:
                suitTrack.append(MovieUtil.createSuitDeathTrack(self, battle))
                suitTrack.append(Func(self.makeDead))

        return suitTrack

    def checkAmbassadorDamageUp(self, videog, battle):
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        destroyedSuits = []
        for suit in battle.activeSuits:
            if not suit.dna.name in SuitBattleGlobals.SpecialCogDict and suit.isTarget and suit.currHP > 0:
                destroyedSuits.append(suit)
        videog.addPendingQueuedHealing((100 * len(destroyedSuits)))
        self.healInterval = Sequence(Func(videog.makeDamageUp), Func(videog.checkDamageUp, + (5 * len(destroyedSuits))),
                                     Func(videog.showHpTextNew, +(100 * len(destroyedSuits)), text="+%s" % (5 * len(destroyedSuits)) + "%" + " Damage!", colorCode=3),
                                     Func(videog.setHealthForMe, + (100 * len(destroyedSuits))), Func(videog.updateHealthBar, 0)).start()

    def checkHighRollerDonation(self, videog, battle):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        x = int(self.currHP)
        if self.currHP < 3000:
            self.damageInterval = Sequence(Parallel(Func(self.showHpText, -x),
                                                   Func(self.setHealthForMe, -x),
                                                   Func(self.updateHealthBar, 0)),
                               Func(self.setNeutralAnimation)).start()
            self.healInterval = Sequence(Parallel(Func(videog.showHpText, +x),
                                                  Func(videog.setHealthForMe, +x),
                                                  Func(videog.updateHealthBar, 0)),
                                         Func(videog.setNeutralAnimation)).start()
            videog.addPendingQueuedHealing(x)
        else:
            self.damageInterval = Sequence(Parallel(Func(self.showHpText, -3000),
                                                  Func(self.setHealthForMe, -3000),
                                                  Func(self.updateHealthBar, 0)),
                                         Func(self.setNeutralAnimation)).start()
            self.healInterval = Sequence(Parallel(Func(videog.showHpText, +3000),
                                                   Func(videog.setHealthForMe, +3000),
                                                   Func(videog.updateHealthBar, 0)),
                               Func(videog.setNeutralAnimation)).start()
            videog.addPendingQueuedHealing(3000)

    def makeCompensationInterval(self):
        suitTrack = Sequence()

        if self.currHP <= 0 or self.isDead:
            return suitTrack

        if not hasattr(self, '_pendingQueuedDamage'):
            self._pendingQueuedDamage = 0
        if not hasattr(self, '_pendingQueuedDeath'):
            self._pendingQueuedDeath = False

        oldPending = self._pendingQueuedDamage

        # HP this suit effectively has left after already-queued damage
        projectedCurrentHP = self.currHP - oldPending

        # If queued damage already reduces it to 0 or below, do not sacrifice it again
        if projectedCurrentHP <= 0:
            return suitTrack

        hpBeforeThisCall = projectedCurrentHP

        showDamage = Sequence(Parallel(Sequence(ActorInterval(self, 'effort', startTime=self.getDuration('effort'), endTime=max(0, self.getDuration('effort') - 1.0), playRate=-1.0),
                                                           ActorInterval(self, 'effort', startTime=max(0, self.getDuration('effort') - 1.0))),
                                                  Func(self.showHpString, "+5% Damage!"), Func(self.makeDamageUp), Func(self.makeLureResist), Func(self.checkDamageUp, + 5)), Func(self.setNeutralAnimationDrop))
        if hpBeforeThisCall < self.maxHP and not self.dna.name == 'racket':
            suitTrack.append(showDamage)
        return suitTrack


    def checkCompensation(self):
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        if self.currHP < self.maxHP and not self.currHP <= 0:
            self.healInterval = Sequence(Parallel(Sequence(ActorInterval(self, 'effort', startTime=self.getDuration('effort'), endTime=max(0, self.getDuration('effort') - 1.0), playRate=-1.0),
                                                           ActorInterval(self, 'effort', startTime=max(0, self.getDuration('effort') - 1.0))),
                                                  Func(self.showHpString, "+5% Damage!"), Func(self.makeDamageUp), Func(self.makeLureResist), Func(self.checkDamageUp, + 5)), Func(self.setNeutralAnimation)).start()
        else:
            pass

    def checkCompensation2(self):
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        if self.currHP < self.maxHP and not self.currHP <= 0:
            self.healInterval = Sequence(Parallel(ActorInterval(self, 'mob-mentality'), Func(self.showHpString, "+15% Damage!"), Func(self.makeDamageUp), Func(self.makeLureResist), Func(self.checkDamageUp, + 15)), Func(self.setNeutralAnimation)).start()
        else:
            pass

    def checkScabbard(self):
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        x = int((self.maxHP * self.hardMaxHP) - self.currHP)
        if self.currHP > 0:
            if not self.getManager():
                if self.currHP >= (self.maxHP * self.hardMaxHP):
                    self.healInterval = Parallel(Func(self.showHpTextNew, 0, text="CHARGED!", colorCode=5),
                                                 Func(self.updateHealthBar, 0)).start()
                elif self.currHP > self.maxHP:
                    self.healInterval = Parallel(Func(self.showHpTextNew, x, text="CHARGED!", colorCode=5),
                                                 Func(self.setHealthForMe, x), Func(self.updateHealthBar, 0)).start()
                    self.addPendingQueuedHealing(x)
                else:
                    self.healInterval = Parallel(Func(self.showHpTextNew, self.maxHP, text="CHARGED!", colorCode=5),
                                                 Func(self.setHealthForMe, self.maxHP), Func(self.updateHealthBar, 0)).start()
                    self.addPendingQueuedHealing(self.maxHP)
            else:
                if self.currHP >= (self.maxHP * self.hardMaxHP):
                    self.healInterval = Parallel(Func(self.showHpTextNew, 0, text="CHARGED!", colorCode=5),
                                                 Func(self.updateHealthBar, 0)).start()
                elif self.currHP + 200 > (self.maxHP * self.hardMaxHP):
                    self.healInterval = Parallel(Func(self.showHpTextNew, x, text="CHARGED!", colorCode=5),
                                                 Func(self.setHealthForMe, x), Func(self.updateHealthBar, 0)).start()
                    self.addPendingQueuedHealing(x)
                else:
                    self.healInterval = Parallel(Func(self.showHpTextNew, 200, text="CHARGED!", colorCode=5),
                                                 Func(self.setHealthForMe, 200), Func(self.updateHealthBar, 0)).start()
                    self.addPendingQueuedHealing(200)

    def checkInsuranceRounds(self, num):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None
        self.damageInterval = Parallel(Func(self.addInsuranceRounds, self.getInsuranceRounds() + num)).start()

    def checkContractedRounds(self, num):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None
        self.damageInterval = Parallel(Func(self.addContractedRounds, self.getContractedRounds() + num)).start()

    def checkLayoffs(self):
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        self.healInterval = Parallel(Func(self.showHpTextNew, -self.currHP, text="FIRED!", colorCode=4),
                                         Func(self.setHealthForMe, -self.currHP), Func(self.updateHealthBar, 0)).start()

    def checkContracted(self):
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        x = int((self.maxHP * self.hardMaxHP) - self.currHP)
        if self.currHP > 0:
            if self.currHP >= (self.maxHP * self.hardMaxHP):
                self.healInterval = Parallel(Func(self.showHpTextNew, 0),
                                             Func(self.updateHealthBar, 0)).start()
            elif self.currHP + 95 > (self.maxHP * self.hardMaxHP):
                self.healInterval = Parallel(Func(self.showHpTextNew, x),
                                             Func(self.setHealthForMe, x), Func(self.updateHealthBar, 0)).start()
                self.addPendingQueuedHealing(x)
            else:
                self.healInterval = Parallel(Func(self.showHpTextNew, 95),
                                             Func(self.setHealthForMe, 95), Func(self.updateHealthBar, 0)).start()
                self.addPendingQueuedHealing(95)

    def checkContracted2(self):
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        x = int((self.maxHP * self.hardMaxHP) - self.currHP)
        if self.currHP >= (self.maxHP * self.hardMaxHP):
            self.healInterval = Parallel(Func(self.showHpTextNew, 0),
                                         Func(self.updateHealthBar, 0)).start()
        elif self.currHP + 95 > (self.maxHP * self.hardMaxHP):
            self.healInterval = Parallel(Func(self.showHpTextNew, x),
                                         Func(self.setHealthForMe, x), Func(self.updateHealthBar, 0)).start()
            self.addPendingQueuedHealing(x)
        else:
            self.healInterval = Parallel(Func(self.showHpTextNew, 95),
                                         Func(self.setHealthForMe, 95), Func(self.updateHealthBar, 0)).start()
            self.addPendingQueuedHealing(95)

    def checkInsuranceScapegoatHP(self):
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        x = int((self.maxHP * self.hardMaxHP) - self.currHP)
        if self.currHP >= (self.maxHP * self.hardMaxHP):
            self.healInterval = Parallel(Func(self.showHpTextNew, 0),
                                         Func(self.updateHealthBar, 0)).start()
        elif self.currHP + 85 > (self.maxHP * self.hardMaxHP):
            self.healInterval = Parallel(Func(self.showHpTextNew, x),
                                         Func(self.setHealthForMe, x), Func(self.updateHealthBar, 0)).start()
            self.addPendingQueuedHealing(x)
        else:
            self.healInterval = Parallel(Func(self.showHpTextNew, 85),
                                         Func(self.setHealthForMe, 85), Func(self.updateHealthBar, 0)).start()
            self.addPendingQueuedHealing(85)

    def checkRedundant(self):
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        x = int((self.maxHP * self.hardMaxHP) - self.currHP)
        if self.currHP > 0:
            if self.currHP >= (self.maxHP * self.hardMaxHP):
                self.healInterval = Parallel(Func(self.showHpTextNew, 0, colorCode=1),
                                             Func(self.updateHealthBar, 0)).start()
            elif self.currHP + 95 > (self.maxHP * self.hardMaxHP):
                self.healInterval = Parallel(Func(self.showHpTextNew, x),
                                             Func(self.setHealthForMe, x), Func(self.updateHealthBar, 0)).start()
                self.addPendingQueuedHealing(x)
            else:
                self.healInterval = Parallel(Func(self.showHpTextNew, 95),
                                             Func(self.setHealthForMe, 95), Func(self.updateHealthBar, 0)).start()
                self.addPendingQueuedHealing(95)

    def checkOilRain(self):
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        x = int((self.maxHP * self.hardMaxHP) - self.currHP)
        if self.currHP > 0:
            if self.currHP >= (self.maxHP * self.hardMaxHP):
                self.healInterval = Parallel(Func(self.showHpTextNew, 0, colorCode=1),
                                             Func(self.updateHealthBar, 0)).start()
            elif self.currHP + 100 > (self.maxHP * self.hardMaxHP):
                self.healInterval = Parallel(Func(self.showHpTextNew, x),
                                             Func(self.setHealthForMe, x), Func(self.updateHealthBar, 0)).start()
                self.addPendingQueuedHealing(x)
            else:
                self.healInterval = Parallel(Func(self.showHpTextNew, 100),
                                             Func(self.setHealthForMe, 100), Func(self.updateHealthBar, 0)).start()
                self.addPendingQueuedHealing(100)

    def checkInsuranceHP(self):
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        x = int((self.maxHP * self.hardMaxHP) - self.currHP)
        if self.currHP > 0:
            if self.currHP >= (self.maxHP * self.hardMaxHP):
                self.healInterval = Parallel(Func(self.showHpTextNew, 0), Func(self.updateHealthBar, 0)).start()
            elif self.currHP + 50 > (self.maxHP * self.hardMaxHP):
                self.healInterval = Parallel(Func(self.showHpTextNew, x), Func(self.setHealthForMe, x), Func(self.updateHealthBar, 0)).start()
                self.addPendingQueuedHealing(x)
            else:
                self.healInterval = Parallel(Func(self.showHpTextNew, 50), Func(self.setHealthForMe, 50), Func(self.updateHealthBar, 0)).start()
                self.addPendingQueuedHealing(50)

    def checkExtraTip(self):
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        x = int((self.maxHP * self.hardMaxHP) - self.currHP)
        if self.currHP > 0:
            if self.currHP >= (self.maxHP * self.hardMaxHP):
                self.healInterval = Parallel(Func(self.showHpTextNew, 0, text="+10% Damage!", colorCode=1), Func(self.updateHealthBar, 0)).start()
            elif self.currHP + 225 > (self.maxHP * self.hardMaxHP) and not self.dna.name == 'supervis' and not self.dna.name == 'clubpres' and not self.dna.name == 'foreman' and not self.dna.name == 'attorney':
                self.healInterval = Parallel(Func(self.showHpTextNew, x, text="+10% Damage!", colorCode=1), Func(self.setHealthForMe, x), Func(self.updateHealthBar, 0)).start()
                self.addPendingQueuedHealing(x)
            else:
                self.healInterval = Parallel(Func(self.showHpTextNew, 225, text="+10% Damage!", colorCode=1), Func(self.setHealthForMe, 225), Func(self.updateHealthBar, 0)).start()
                self.addPendingQueuedHealing(225)


    def checkLifeInsurance(self):
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        x = int(self.maxHP - self.currHP)
        if self.getActualLevel() == 25:
            if self.currHP >= (self.maxHP * self.hardMaxHP):
                self.healInterval = Parallel(Func(self.showHpTextNew, 0, text="+10% Damage!", colorCode=1), Func(self.makeDamageUp), Func(self.checkDamageUp, + 10), Func(self.updateHealthBar, 0)).start()
            elif self.currHP + 225 > self.maxHP:
                self.healInterval = Parallel(Func(self.showHpTextNew, x, text="+10% Damage!", colorCode=1), Func(self.makeDamageUp), Func(self.checkDamageUp, + 10), Func(self.setHealthForMe, x), Func(self.updateHealthBar, 0)).start()
                self.addPendingQueuedHealing(x)
            else:
                self.healInterval = Parallel(Func(self.showHpTextNew, 225, text="+10% Damage!", colorCode=1), Func(self.makeDamageUp), Func(self.checkDamageUp, + 10), Func(self.setHealthForMe, 225), Func(self.updateHealthBar, 0)).start()
                self.addPendingQueuedHealing(225)
        else:
            if self.currHP >= (self.maxHP * self.hardMaxHP):
                self.healInterval = Parallel(Func(self.showHpTextNew, 0, text="+5% Damage!", colorCode=1), Func(self.makeDamageUp), Func(self.checkDamageUp, + 5), Func(self.updateHealthBar, 0)).start()
            elif self.currHP + 225 > self.maxHP:
                self.healInterval = Parallel(Func(self.showHpTextNew, x, text="+5% Damage!", colorCode=1), Func(self.makeDamageUp), Func(self.checkDamageUp, + 5), Func(self.setHealthForMe, x),
                                             Func(self.updateHealthBar, 0)).start()
                self.addPendingQueuedHealing(x)
            else:
                self.healInterval = Parallel(Func(self.showHpTextNew, 225, text="+5% Damage!", colorCode=1), Func(self.makeDamageUp), Func(self.checkDamageUp, + 5), Func(self.setHealthForMe, 225),
                                             Func(self.updateHealthBar, 0)).start()
                self.addPendingQueuedHealing(225)

    def checkCompensationForeman(self):
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        self.healInterval = Parallel(Func(self.showHpTextNew, 225, text="+35% Damage!", colorCode=1), Func(self.makeDamageUp), Func(self.checkDamageUp, + 35), Func(self.setHealthForMe, 225), Func(self.updateHealthBar, 0)).start()
        self.addPendingQueuedHealing(225)

    def checkCompensation2(self):
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        self.healInterval = Parallel(Func(self.showHpTextNew, 450, text="+70% Damage!", colorCode=1), Func(self.makeDamageUp), Func(self.checkDamageUp, + 70), Func(self.setHealthForMe, 450), Func(self.updateHealthBar, 0)).start()
        self.addPendingQueuedHealing(450)

    def checkCompensation3(self):
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        self.healInterval = Parallel(Func(self.showHpTextNew, 675, text="+105% Damage!", colorCode=1), Func(self.makeDamageUp), Func(self.checkDamageUp, + 105), Func(self.setHealthForMe, 675), Func(self.updateHealthBar, 0)).start()
        self.addPendingQueuedHealing(675)

    def checkCompensation4(self):
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        self.healInterval = Parallel(Func(self.showHpTextNew, 900, text="+140% Damage!", colorCode=1), Func(self.setHealthForMe, 900), Func(self.makeDamageUp), Func(self.checkDamageUp, + 140), Func(self.updateHealthBar, 0)).start()
        self.addPendingQueuedHealing(900)

    def checkCompensation5(self):
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        self.healInterval = Parallel(Func(self.showHpTextNew, 1125, text="+175% Damage!", colorCode=1), Func(self.makeDamageUp), Func(self.checkDamageUp, + 175), Func(self.setHealthForMe, 1125), Func(self.updateHealthBar, 0)).start()
        self.addPendingQueuedHealing(1125)

    def checkCompensationDividend(self):
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        self.healInterval = Parallel(Func(self.showHpTextNew, 200, text="+5% Damage!", colorCode=1), Func(self.makeDamageUp), Func(self.checkDamageUp, + 5), Func(self.setHealthForMe, 200), Func(self.updateHealthBar, 0)).start()
        self.addPendingQueuedHealing(200)

    def checkCompensationDividend2(self):
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        self.healInterval = Parallel(Func(self.showHpTextNew, 400, text="+10% Damage!", colorCode=1), Func(self.makeDamageUp), Func(self.checkDamageUp, + 10), Func(self.setHealthForMe, 400), Func(self.updateHealthBar, 0)).start()
        self.addPendingQueuedHealing(400)

    def checkCompensationDividend3(self):
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        self.healInterval = Parallel(Func(self.showHpTextNew, 600, text="+15% Damage!", colorCode=1), Func(self.makeDamageUp), Func(self.checkDamageUp, + 15), Func(self.setHealthForMe, 600), Func(self.updateHealthBar, 0)).start()
        self.addPendingQueuedHealing(600)

    def checkCompensationDividend4(self):
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        self.healInterval = Parallel(Func(self.showHpTextNew, 800, text="+20% Damage!", colorCode=1), Func(self.setHealthForMe, 800), Func(self.makeDamageUp), Func(self.checkDamageUp, + 20), Func(self.updateHealthBar, 0)).start()
        self.addPendingQueuedHealing(800)

    def checkCompensationDividend5(self):
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        self.healInterval = Parallel(Func(self.showHpTextNew, 1000, text="+25% Damage!", colorCode=1), Func(self.makeDamageUp), Func(self.checkDamageUp, + 25), Func(self.setHealthForMe, 1000), Func(self.updateHealthBar, 0)).start()
        self.addPendingQueuedHealing(1000)

    def checkInsuranceCountdown(self):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None
        if self.getInsuranceRounds() - 1 == 0:
            self.damageInterval = Parallel(Func(self.removeInsured))
        elif self.getInsuranceRounds() > 0:
            self.damageInterval = Parallel(Func(self.addInsuranceRounds, self.getInsuranceRounds() - 1)).start()
        else:
            pass

    def checkContractedCountdown(self):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None
        if self.getContractedRounds() - 1 == 0:
            self.damageInterval = Parallel(Func(self.removeContracted))
        elif self.getContractedRounds() > 0:
            self.damageInterval = Parallel(Func(self.addContractedRounds, self.getContractedRounds() - 1)).start()
        else:
            pass

    def setNeutralAnimationHead(self):
        if self.getDizzy() or self.isSleepy or self.isSued:
            if self.dna.name == 'hroller':
                for headPart in self.animatedHeadParts: Sequence(
                    Func(headPart.loop, 'neutral-lured', fromFrame=0, toFrame=22)
                    ).start()
            elif self.dna.name == 'hrollers':
                for headPart in self.animatedHeadParts: Sequence(
                    Func(headPart.loop, 'neutral-lured', fromFrame=0, toFrame=22)
                    ).start()
            elif self.dna.name == 'hroller2':
                for headPart in self.animatedHeadParts: Sequence(
                    Func(headPart.loop, 'neutral-lured', fromFrame=0, toFrame=22)
                    ).start()
            elif self.isSleepy:
                Func(self.setChatAbsoluteSpecial, '. . . Z Z Z . . .', CFThought).start()
                for headPart in self.animatedHeadParts: Sequence(
                    Func(headPart.loop, 'neutral-lured')
                    ).start()
            else:
                for headPart in self.animatedHeadParts: Sequence(
                    Func(headPart.loop, 'neutral-lured')
                    ).start()
        else:
            if self.dna.name == 'hroller' and (float(self.currHP) / float(self.maxHP) <= 0.25):
                for headPart in self.animatedHeadParts: Sequence(Func(headPart.loop, 'neutral-hurt', fromFrame=0,
                                                                      toFrame=22)
                                                                 ).start()
            elif self.dna.name == 'hroller2' and (float(self.currHP) / float(self.maxHP) <= 0.25):
                for headPart in self.animatedHeadParts: Sequence(Func(headPart.loop, 'neutral-hurt', fromFrame=0,
                                                                      toFrame=22)
                                                                 ).start()
            elif self.dna.name == 'hrollers' and (float(self.currHP) / float(self.maxHP) <= 0.25):
                for headPart in self.animatedHeadParts: Sequence(Func(headPart.loop, 'neutral-hurt', fromFrame=0,
                                                                      toFrame=22)
                                                                 ).start()
            else:
                for headPart in self.animatedHeadParts: Sequence(Func(headPart.loop, 'neutral%s' % (
                                                                 '-hurt' if float(self.currHP) / float(
                                                                     self.maxHP) <= 0.25 else '',))
                                                                 ).start()
            if self.dna.name == 'videog':
                for headPart in self.animatedHeadParts:
                    if float(self.currHP) / float(self.maxHP) <= 0.25:
                        texture = loader.loadTexture('phase_9/maps/ttcc_ene_videographer3.png')
                        Sequence(Func(headPart.setTexture, texture, 1)).start()
            if self.dna.name == 'bcaster':
                for headPart in self.animatedHeadParts:
                    if float(self.currHP) / float(self.maxHP) <= 0.25:
                        texture = loader.loadTexture('phase_9/maps/ttcc_ene_videographer3.png')
                        Sequence(Func(headPart.setTexture, texture, 1)).start()
            for headPart in self.animatedHeadParts: Sequence(
                Func(headPart.loop, 'neutral%s' % ('-hurt' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',))
            ).start()

    def setNeutralAnimationHeadTrap(self):
        if self.isSleepy or self.isSued:
            if self.isSleepy:
                Func(self.setChatAbsoluteSpecial, '. . . Z Z Z . . .', CFThought).start()
                for headPart in self.animatedHeadParts: Sequence(
                    Func(headPart.loop, 'neutral-lured')
                    ).start()
            else:
                for headPart in self.animatedHeadParts: Sequence(
                    Func(headPart.loop, 'neutral-lured')
                ).start()
        elif self.dna.name == 'hroller' and (float(self.currHP) / float(self.maxHP) <= 0.25):
            for headPart in self.animatedHeadParts: Sequence(Func(headPart.loop, 'neutral-hurt', fromFrame=0,
                                                                      toFrame=22)
                                                                 ).start()
        elif self.dna.name == 'hroller2' and (float(self.currHP) / float(self.maxHP) <= 0.25):
            for headPart in self.animatedHeadParts: Sequence(Func(headPart.loop, 'neutral-hurt', fromFrame=0,
                                                                      toFrame=22)
                                                                 ).start()
        elif self.dna.name == 'hrollers' and (float(self.currHP) / float(self.maxHP) <= 0.25):
            for headPart in self.animatedHeadParts: Sequence(Func(headPart.loop, 'neutral-hurt', fromFrame=0,
                                                                      toFrame=22)
                                                                 ).start()
        else:
            for headPart in self.animatedHeadParts: Sequence(Func(headPart.loop, 'neutral%s' % (
                                                                 '-hurt' if float(self.currHP) / float(
                                                                     self.maxHP) <= 0.25 else '',))
                                                                 ).start()
        if self.dna.name == 'videog':
            for headPart in self.animatedHeadParts:
                if float(self.currHP) / float(self.maxHP) <= 0.25:
                        texture = loader.loadTexture('phase_9/maps/ttcc_ene_videographer3.png')
                        Sequence(Func(headPart.setTexture, texture, 1)).start()
        if self.dna.name == 'bcaster':
            for headPart in self.animatedHeadParts:
                    if float(self.currHP) / float(self.maxHP) <= 0.25:
                        texture = loader.loadTexture('phase_9/maps/ttcc_ene_videographer3.png')
                        Sequence(Func(headPart.setTexture, texture, 1)).start()
        for headPart in self.animatedHeadParts: Sequence(
                Func(headPart.loop, 'neutral%s' % ('-hurt' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',))
            ).start()
        Sequence(Func(self.setPlayRate, self.getPlayRate2(), 'neutral%s' % ('-hurt' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',)), Func(self.loop, 'neutral%s' % ('-hurt' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',))
            ).start()

    def setNeutralAnimationAttack(self):
        if self.isAngry and self.dna.name == 'sgoat':
            Sequence(Func(self.loop, 'neutral-enraged')
                     ).start()
        elif self.dna.name == 'cbutcher' and self.isChainsawPhase2:
            Sequence(
                Func(self.loop, 'neutral-override')
            ).start()
        elif self.isImmortal and not self.dna.name == 'hroller' and not self.dna.name == 'wtapper' and not self.dna.name == 'videog' and self.isPhase3:
            Sequence(Func(self.loop, 'highroller-neutral-levitate-loop')
                     ).start()
        elif self.isVulnerable and self.dna.name == 'hroller2':
            Sequence(Func(self.loop, 'neutral2%s' % ('-hurt' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',))
                     ).start()
        elif self.dna.name == 'hrollers':
            Sequence(Func(self.loop, 'neutral%s' % ('-hurt' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',))
                     ).start()
        elif self.dna.name == 'hroller':
            Sequence(Func(self.loop, 'neutral%s' % ('-hurt' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',))
                     ).start()
        elif float(self.currHP) > float(self.maxHP * 1.5):
            Sequence(Func(self.loop, 'neutral-unstable', fromFrame=70, toFrame=80)
                     ).start()
        else:
            Sequence(Func(self.loop, 'neutral%s' % ('-hurt' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',))
                     ).start()
        self.setNeutralAnimationHeadTrap()

    def setNeutralAnimation(self):
        if self.getDizzy():
            Sequence(Func(self.setPlayRate, self.getPlayRate2(), 'lured'), Func(self.setPlayRate, self.getPlayRate2(), 'lured2'), Func(self.loop, 'lured')
                     ).start()
        elif self.dna.name == 'clerk' and (self.getActualLevel() == 24 or self.getActualLevel() == 25):
            Sequence(Func(self.setPlayRate, self.getPlayRate2(), 'pace'), Func(self.loop, 'pace')
                     ).start()
        elif self.dna.name == 'foreman' and self.getActualLevel() == 23:
            Sequence(Func(self.setPlayRate, self.getPlayRate2(), 'rolled'), Func(self.loop, 'rolled')
                     ).start()
        elif self.dna.name == 'cbutcher' and self.isChainsawPhase2:
            Sequence(
                Func(self.loop, 'neutral-override')
            ).start()
        elif self.isOttomanPhase2:
            Sequence(Func(self.setPlayRate, self.getPlayRate2(), 'pace'), Func(self.loop, 'pace')
                     ).start()
        elif self.isAngry and self.dna.name == 'sgoat':
            Sequence(ActorInterval(self, 'neutral-enraged-return', startTime=self.getDuration('neutral-enraged-return'), endTime=0), Func(self.setPlayRate, self.getPlayRate2(), 'neutral-enraged'), Func(self.loop, 'neutral-enraged')
                     ).start()
        elif self.isImmortal and not self.dna.name == 'hroller' and not self.dna.name == 'wtapper' and not self.dna.name == 'videog' and self.isPhase3:
            Sequence(Func(self.loop, 'highroller-neutral-levitate-loop')
                     ).start()
        elif self.isDanceSession:
            Sequence(Func(self.loop, 'rolled')
                     ).start()
        elif self.isVulnerable and self.dna.name == 'hroller2':
            Sequence(Func(self.loop, 'neutral2%s' % ('-hurt' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',))
                     ).start()
        elif self.isZapped:
            Sequence(Func(self.loop, 'neutral-unstable')
                     ).start()
        elif float(self.currHP) > float(self.maxHP * 1.5):
            Sequence(Func(self.loop, 'neutral-unstable', fromFrame=70, toFrame=80)
                     ).start()
        else:
            Sequence(Func(self.setPlayRate, self.getPlayRate2(), 'neutral%s' % ('-hurt' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',)), Func(self.loop, 'neutral%s' % ('-hurt' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',))
            ).start()
        self.setNeutralAnimationHead()

    def setNeutralAnimationAdjustInterval(self):
        if self.getDizzy():
            Sequence(Func(self.setPlayRate, self.getPlayRate2(), 'lured'), Func(self.setPlayRate, self.getPlayRate2(), 'lured2'), Func(self.loop, 'lured')
                     ).start()
        elif self.style.name == 'mh2':
            Sequence(Func(self.setPlayRate, self.getPlayRate2(), 'rolled'), Func(self.loop, 'rolled')
                     ).start()
        elif self.style.name == 'std2':
            Sequence(Func(self.setPlayRate, self.getPlayRate2(), 'rolled'), Func(self.loop, 'rolled')
                     ).start()
        elif self.style.name == 'hrollers':
            Sequence(Func(self.setPlayRate, self.getPlayRate2(), 'rolled'), Func(self.loop, 'rolled')
                     ).start()
        elif self.style.name == 'cinema':
            Sequence(Func(self.setPlayRate, self.getPlayRate2(), 'rolled'), Func(self.loop, 'rolled')
                     ).start()
        elif self.style.name == 'choreo':
            Sequence(Func(self.setPlayRate, self.getPlayRate2(), 'rolled'), Func(self.loop, 'rolled')
                     ).start()
        elif self.style.name == 'videog':
            Sequence(Func(self.setPlayRate, self.getPlayRate2(), 'rolled'), Func(self.loop, 'rolled')
                     ).start()
        elif self.style.name == 'bcaster':
            Sequence(Func(self.setPlayRate, self.getPlayRate2(), 'rolled'), Func(self.loop, 'rolled')
                     ).start()
        elif self.style.name == 'director':
            Sequence(Func(self.setPlayRate, self.getPlayRate2(), 'rolled'), Func(self.loop, 'rolled')
                     ).start()
        elif self.style.name == 'fmaker':
            Sequence(Func(self.setPlayRate, self.getPlayRate2(), 'rolled'), Func(self.loop, 'rolled')
                     ).start()
        elif self.dna.name == 'clerk' and (self.getActualLevel() == 24 or self.getActualLevel() == 25):
            Sequence(Func(self.setPlayRate, self.getPlayRate2(), 'pace'), Func(self.loop, 'pace')
                     ).start()
        elif self.dna.name == 'foreman' and self.getActualLevel() == 23:
            Sequence(Func(self.setPlayRate, self.getPlayRate2(), 'rolled'), Func(self.loop, 'rolled')
                     ).start()
        elif self.dna.name == 'cbutcher' and self.isChainsawPhase2:
            Sequence(
                Func(self.loop, 'neutral-override')
            ).start()
        elif self.isOttomanPhase2:
            Sequence(Func(self.setPlayRate, self.getPlayRate2(), 'pace'), Func(self.loop, 'pace')
                     ).start()
        elif self.isAngry and self.dna.name == 'sgoat':
            Sequence(ActorInterval(self, 'neutral-enraged-return', startTime=self.getDuration('neutral-enraged-return'), endTime=0), Func(self.setPlayRate, self.getPlayRate2(), 'neutral-enraged'), Func(self.loop, 'neutral-enraged')
                     ).start()
        elif self.isImmortal and not self.dna.name == 'hroller' and not self.dna.name == 'wtapper' and not self.dna.name == 'videog' and self.isPhase3:
            Sequence(Func(self.loop, 'highroller-neutral-levitate-loop')
                     ).start()
        elif self.isDanceSession:
            Sequence(Func(self.loop, 'rolled')
                     ).start()
        elif self.isVulnerable and self.dna.name == 'hroller2':
            Sequence(Func(self.loop, 'neutral2%s' % ('-hurt' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',))
                     ).start()
        elif self.isZapped:
            Sequence(Func(self.loop, 'neutral-unstable')
                     ).start()
        elif float(self.currHP) > float(self.maxHP * 1.5):
            Sequence(Func(self.loop, 'neutral-unstable', fromFrame=70, toFrame=80)
                     ).start()
        else:
            Sequence(Func(self.setPlayRate, self.getPlayRate2(), 'neutral%s' % ('-hurt' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',)), Func(self.loop, 'neutral%s' % ('-hurt' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',))
            ).start()
        self.setNeutralAnimationHead()

    def setNeutralAnimationDrop(self):
        if self.isSleepy:
            Func(self.setChatAbsoluteSpecial, '. . . Z Z Z . . .', CFThought).start()
            Sequence(Func(self.setPlayRate, self.getPlayRate2(), 'neutral%s' % ('-hurt' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',)),
                     Func(self.loop, 'neutral%s' % ('-hurt' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',))
                     ).start()
            self.setNeutralAnimationHead()
        elif self.getDizzy():
            Sequence(Func(self.setPlayRate, self.getPlayRate2(), 'lured'),
                     Func(self.setPlayRate, self.getPlayRate2(), 'lured2'), Func(self.loop, 'lured')
                     ).start()
            self.setNeutralAnimationHead()
        elif self.dna.name == 'clerk' and (self.getActualLevel() == 24 or self.getActualLevel() == 25):
            Sequence(Func(self.setPlayRate, self.getPlayRate2(), 'pace'), Func(self.loop, 'pace')
                     ).start()
        elif self.dna.name == 'foreman' and self.getActualLevel() == 23:
            Sequence(Func(self.setPlayRate, self.getPlayRate2(), 'rolled'), Func(self.loop, 'rolled')
                     ).start()
        elif self.dna.name == 'cbutcher' and self.isChainsawPhase2:
            Sequence(
                Func(self.loop, 'neutral-override')
            ).start()
        elif self.isOttomanPhase2:
            Sequence(Func(self.setPlayRate, self.getPlayRate2(), 'pace'), Func(self.loop, 'pace')
                     ).start()
        elif self.isAngry and self.dna.name == 'sgoat':
            Sequence(ActorInterval(self, 'neutral-enraged-return', startTime=self.getDuration('neutral-enraged-return'), endTime=0), Func(self.setPlayRate, self.getPlayRate2(), 'neutral-enraged'), Func(self.loop, 'neutral-enraged')
                     ).start()
        elif self.isImmortal and not self.dna.name == 'hroller' and not self.dna.name == 'wtapper' and not self.dna.name == 'videog'and self.isPhase3:
            Sequence(Func(self.loop, 'highroller-neutral-levitate-loop')
                     ).start()
        elif self.isVulnerable and self.dna.name == 'hroller2':
            Sequence(
                Func(self.loop, 'neutral2%s' % ('-hurt' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',))
                ).start()
        elif float(self.currHP) > float(self.maxHP * 1.5):
            Sequence(Func(self.loop, 'neutral-unstable', fromFrame=70, toFrame=80)
                     ).start()
        else:
            Sequence(Func(self.setPlayRate, self.getPlayRate2(), 'neutral%s' % ('-hurt' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',)),
                     Func(self.loop, 'neutral%s' % ('-hurt' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',))
                     ).start()

    def setNeutralAnimationRolled(self):
        if self.getDizzy():
            Sequence(Func(self.setPlayRate, self.getPlayRate2(), 'lured'), Func(self.setPlayRate, self.getPlayRate2(), 'lured2'), Func(self.loop, 'lured')
                     ).start()
        else:
            Sequence(Func(self.setPlayRate, self.getPlayRate2(), 'rolled'), Func(self.loop, 'rolled')
            ).start()
        self.setNeutralAnimationHead()

    def setNeutralAnimationTrap(self):
        if self.isAngry and self.dna.name == 'sgoat':
            Sequence(ActorInterval(self, 'neutral-enraged-return', startTime=self.getDuration('neutral-enraged-return'), endTime=0), Func(self.loop, 'neutral-enraged')
                     ).start()
        elif self.dna.name == 'cbutcher' and self.isChainsawPhase2:
            Sequence(
                Func(self.loop, 'neutral-override')
            ).start()
        elif self.isImmortal and not self.dna.name == 'hroller' and not self.dna.name == 'wtapper' and not self.dna.name == 'videog'and self.isPhase3:
            Sequence(Func(self.loop, 'highroller-neutral-levitate-loop')
                     ).start()
        elif self.isVulnerable and self.dna.name == 'hroller2':
            Sequence(Func(self.loop, 'neutral2%s' % ('-hurt' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',))
                     ).start()
        elif self.isZapped:
            Sequence(Func(self.loop, 'neutral-unstable')
                     ).start()
        elif float(self.currHP) > float(self.maxHP * 1.5):
            Sequence(Func(self.loop, 'neutral-unstable', fromFrame=70, toFrame=80)
                     ).start()
        else:
            Sequence(Func(self.loop, 'neutral%s' % ('-hurt' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',))
            ).start()
        self.setNeutralAnimationHeadTrap()

    def setChatAbsoluteTrap(self, chatString, chatFlags, dialogue=None, interrupt=True):
        searchString = chatString.lower()
        if searchString.find(OTPLocalizer.DialogSpecial) >= 0:
            self.animHead = 'murmur'
        elif searchString.find(OTPLocalizer.DialogQuestion) >= 0:
            self.animHead = 'question'
        elif searchString.find(OTPLocalizer.DialogExclamation) >= 0:
            self.animHead = 'grunt'
        else:
            stringLength = len(chatString)
            if stringLength <= 1:
                self.animHead = None
            elif stringLength <= OTPLocalizer.DialogLength1:
                self.animHead = 'grunt'
            elif stringLength <= OTPLocalizer.DialogLength2:
                self.animHead = 'murmur'
            elif stringLength <= OTPLocalizer.DialogLength3:
                self.animHead = 'statement'
            else:
                self.animHead = 'statement'
        self.nametag.setChatText(chatString, chatFlags)
        self.playCurrentDialogue(dialogue, chatFlags, interrupt)
        for headPart in self.animatedHeadParts: Sequence(
            Func(headPart.loop, 'neutral%s' % ('-hurt' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',))
                ).start()

    def setChatAbsolute(self, chatString, chatFlags, dialogue=None, interrupt=True):
        searchString = chatString.lower()
        if chatFlags & CFQuicktalker:
            self.nametag.setChatType(NametagGlobals.SPEEDCHAT)
        else:
            self.nametag.setChatType(NametagGlobals.CHAT)

        if chatFlags & CFThought:
            self.nametag.setChatBalloonType(NametagGlobals.THOUGHT_BALLOON)
        else:
            self.nametag.setChatBalloonType(NametagGlobals.CHAT_BALLOON)

        if chatFlags & CFPageButton:
            self.nametag.setChatButton(NametagGlobals.pageButton)
        else:
            self.nametag.setChatButton(NametagGlobals.noButton)

        if chatFlags & CFReversed:
            self.nametag.setChatReversed(True)
        else:
            self.nametag.setChatReversed(False)
        if searchString.find(OTPLocalizer.DialogSpecial) >= 0:
            self.animHead = 'murmur'
        elif searchString.find(OTPLocalizer.DialogExclamation) >= 0:
            self.animHead = 'grunt'
        elif searchString.find(OTPLocalizer.DialogQuestion) >= 0:
            self.animHead = 'question'
        else:
            stringLength = len(chatString)
            if stringLength <= 1:
                self.animHead = None
            elif stringLength <= OTPLocalizer.DialogLength1:
                self.animHead = 'grunt'
            elif stringLength <= OTPLocalizer.DialogLength2:
                self.animHead = 'murmur'
            elif stringLength <= OTPLocalizer.DialogLength3:
                self.animHead = 'statement'
            else:
                self.animHead = 'statement'
        self.nametag.setChatText(chatString, chatFlags)
        self.playCurrentDialogue(dialogue, chatFlags, interrupt)
        if self.animHead == None and (self.getDizzy() or self.isSleepy or self.isSued):
            if self.dna.name == 'hroller':
                for headPart in self.animatedHeadParts: Sequence(
                    Func(headPart.loop, 'neutral-lured', fromFrame=0, toFrame=22)
                    ).start()
            elif self.dna.name == 'hrollers':
                for headPart in self.animatedHeadParts: Sequence(
                    Func(headPart.loop, 'neutral-lured', fromFrame=0, toFrame=22)
                    ).start()
            elif self.dna.name == 'hroller2':
                for headPart in self.animatedHeadParts: Sequence(
                    Func(headPart.loop, 'neutral-lured', fromFrame=0, toFrame=22)
                    ).start()
            else:
                for headPart in self.animatedHeadParts: Sequence(
                    Func(headPart.loop, 'neutral-lured')
                    ).start()
        elif self.animHead == None:
            if self.dna.name == 'hroller' and (float(self.currHP) / float(self.maxHP) <= 0.25):
                for headPart in self.animatedHeadParts: Sequence(
                    Func(headPart.loop, 'neutral-hurt', fromFrame=0, toFrame=22)
                    ).start()
            elif self.dna.name == 'hrollers' and (float(self.currHP) / float(self.maxHP) <= 0.25):
                for headPart in self.animatedHeadParts: Sequence(
                    Func(headPart.loop, 'neutral-hurt', fromFrame=0, toFrame=22)
                    ).start()
            elif self.dna.name == 'hroller2' and (float(self.currHP) / float(self.maxHP) <= 0.25):
                for headPart in self.animatedHeadParts: Sequence(
                    Func(headPart.loop, 'neutral-hurt', fromFrame=0, toFrame=22)
                    ).start()
            else:
                for headPart in self.animatedHeadParts: Sequence(
                    Func(headPart.loop, 'neutral%s' % ('-hurt' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',))
                    ).start()
        elif self.getDizzy() or self.isSleepy or self.isSued:
            if self.dna.name == 'hroller':
                for headPart in self.animatedHeadParts: Sequence(ActorInterval(headPart, self.animHead),
                    Func(headPart.loop, 'neutral-lured', fromFrame=0, toFrame=22)
                ).start()
            elif self.dna.name == 'hroller2':
                for headPart in self.animatedHeadParts: Sequence(ActorInterval(headPart, self.animHead),
                    Func(headPart.loop, 'neutral-lured', fromFrame=0, toFrame=22)
                ).start()
            elif self.dna.name == 'hrollers':
                for headPart in self.animatedHeadParts: Sequence(ActorInterval(headPart, self.animHead),
                    Func(headPart.loop, 'neutral-lured', fromFrame=0, toFrame=22)
                ).start()
            else:
                for headPart in self.animatedHeadParts: Sequence(ActorInterval(headPart, self.animHead),
                    Func(headPart.loop, 'neutral-lured')
                ).start()
        else:
            if self.dna.name == 'hroller' and (float(self.currHP) / float(self.maxHP) <= 0.25):
                for headPart in self.animatedHeadParts: Sequence(ActorInterval(headPart, self.animHead),
                    Func(headPart.loop, 'neutral-hurt', fromFrame=0, toFrame=22)
                    ).start()
            elif self.dna.name == 'hroller2' and (float(self.currHP) / float(self.maxHP) <= 0.25):
                for headPart in self.animatedHeadParts: Sequence(ActorInterval(headPart, self.animHead),
                    Func(headPart.loop, 'neutral-hurt', fromFrame=0, toFrame=22)
                    ).start()
            elif self.dna.name == 'hrollers' and (float(self.currHP) / float(self.maxHP) <= 0.25):
                for headPart in self.animatedHeadParts: Sequence(ActorInterval(headPart, self.animHead),
                    Func(headPart.loop, 'neutral-hurt', fromFrame=0, toFrame=22)
                    ).start()
            else:
                for headPart in self.animatedHeadParts: Sequence(ActorInterval(headPart, self.animHead),
                    Func(headPart.loop, 'neutral%s' % ('-hurt' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',))
                    ).start()

    def setChatAbsoluteSpecial(self, chatString, chatFlags, dialogue=None, interrupt=True):
        searchString = chatString.lower()
        if chatFlags & CFQuicktalker:
            self.nametag.setChatType(NametagGlobals.SPEEDCHAT)
        else:
            self.nametag.setChatType(NametagGlobals.CHAT)

        if chatFlags & CFThought:
            self.nametag.setChatBalloonType(NametagGlobals.THOUGHT_BALLOON)
        else:
            self.nametag.setChatBalloonType(NametagGlobals.CHAT_BALLOON)

        if chatFlags & CFPageButton:
            self.nametag.setChatButton(NametagGlobals.pageButton)
        else:
            self.nametag.setChatButton(NametagGlobals.noButton)

        if chatFlags & CFReversed:
            self.nametag.setChatReversed(True)
        else:
            self.nametag.setChatReversed(False)
        if searchString.find(OTPLocalizer.DialogSpecial) >= 0:
            self.animHead = 'murmur'
        elif searchString.find(OTPLocalizer.DialogExclamation) >= 0:
            self.animHead = 'grunt'
        elif searchString.find(OTPLocalizer.DialogQuestion) >= 0:
            self.animHead = 'question'
        else:
            stringLength = len(chatString)
            if stringLength <= 1:
                self.animHead = None
            elif stringLength <= OTPLocalizer.DialogLength1:
                self.animHead = 'grunt'
            elif stringLength <= OTPLocalizer.DialogLength2:
                self.animHead = 'murmur'
            elif stringLength <= OTPLocalizer.DialogLength3:
                self.animHead = 'statement'
            else:
                self.animHead = 'statement'
        self.nametag.setChatText(chatString, chatFlags)
        self.playCurrentDialogue(dialogue, chatFlags, interrupt)

    def cleanUpSoundList(self):
        removeList = []
        for soundSequence in self.soundSequenceList:
            if soundSequence.isStopped():
                removeList.append(soundSequence)

        for soundSequence in removeList:
            self.soundSequenceList.remove(soundSequence)