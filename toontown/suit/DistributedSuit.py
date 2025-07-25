import copy
import math
import random
from toontown.suit import DistributedSuitBase
from toontown.suit import DistributedSuitPlanner
from toontown.suit import Suit
from toontown.suit import SuitBase
from toontown.suit import SuitDialog
from toontown.suit import SuitTimings
from toontown.battle import MovieUtil
from direct.directnotify import DirectNotifyGlobal
from direct.directtools.DirectGeometry import CLAMP
from direct.distributed.ClockDelta import *
from direct.fsm import ClassicFSM, State
from direct.fsm import State
from direct.interval.IntervalGlobal import *
from direct.task import Task
from pandac.PandaModules import *
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
        self.legList = None
        self.initState = None
        self.finalState = None
        self.buildingSuit = 0
        self.battleConditions = {}
        self.deadSuits = []
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
        elif type == 'question':
            sfxIndex = 3
        elif type == 'exclamation':
            sfxIndex = 4
        elif type == 'special':
            sfxIndex = 1
        else:
            notify.error('unrecognized dialogue type: ', type)
        if sfxIndex != None and sfxIndex < len(dialogueArray) and dialogueArray[sfxIndex] != None:
            soundSequence = Sequence(Wait(delay), SoundInterval(dialogueArray[sfxIndex], node=None, listenerNode=base.localAvatar, loop=0, volume=1.0))
            self.soundSequenceList.append(soundSequence)
            soundSequence.start()
            self.cleanUpSoundList()

    def checkCogLured(self, battle):
        if self.getDizzy():
            ival = self.__createSuitResetPosTrack(battle)
            ival.start()
        else:
            pass

    def __createSuitResetPosTrack(self, battle):
        resetPos, resetHpr = battle.getActorPosHpr(self)
        moveDist = Vec3(self.getPos(battle) - resetPos).length()
        moveDuration = 0
        neutralTrack = Func(self.setNeutralAnimation)
        unluredTrack = Func(battle.unlureSuit, self)
        unlureSuit = Func(self.makeUnLured)
        updateTrack = Parallel(Func(self.setChatAbsolute,
                                    '',
                                    CFSpeech | CFTimeout))
        walkTrack = Sequence(Func(self.setHpr, battle, resetHpr),
                             neutralTrack)
        moveTrack = LerpPosInterval(self, moveDuration, resetPos, other=battle)
        return Parallel(unluredTrack, unlureSuit, walkTrack, moveTrack)

    def checkCogHP(self, battle):
        if self.getHP() <= 0:
            ival = Sequence(MovieUtil.createSuitDeathTrack(self, battle), Func(battle.unlureSuit, self))
            ival.start()
            #ival.setPlayRate(2)
        else:
            pass

    def checkCogDeath(self, battle):
        if self.getHP() <= 0:
            self.deadSuits.append(self)
        else:
            pass

    def checkCogHPDrop(self, battle):
        if self.getHP() <= 0:
            ival = Sequence(MovieUtil.createSuitCrashTrack(self, battle))
            ival.start()
        else:
            pass

    def checkAbsorbHP(self, battle):
        if self.getHP() <= 0:
            ival = Sequence(Func(self.makeDead))
            ival.start()
        else:
            pass

    def checkCogHPBomb(self, battle):
        if self.getHP() <= 0:
            ival = Sequence(MovieUtil.shortCircuitTrack(self, battle), Func(battle.unlureSuit, self))
            ival.start()
        else:
            pass

    def checkCogHPZap(self, battle):
        if self.getHP() <= 0:
            ival = Sequence(MovieUtil.shortCircuitTrack(self, battle), Func(battle.unlureSuit, self))
            ival.start()
        else:
            pass

    def checkCogHPLaserRevive(self, battle):
        if self.getHP() <= 0:
            ival = Sequence(MovieUtil.createSuitReviveTrackVirtual(self, battle), Func(battle.unlureSuit, self))
            ival.start()
            ival.setPlayRate(2)
        else:
            pass

    def checkCogHPLaser(self, battle):
        if self.getHP() <= 0:
            ival = Sequence(MovieUtil.createVirtualSuitDeathTrack(self, battle), Func(battle.unlureSuit, self))
            ival.start()
        else:
            pass

    def checkCogHPRevive(self, battle):
        if self.getHP() <= 0:
            ival = Sequence(MovieUtil.createSuitReviveTrack(self, battle), Func(battle.unlureSuit, self))
            ival.start()
            ival.setPlayRate(2)
        else:
            pass

    def checkCogOvercharge(self):
        if float(self.currHP) > float(self.maxHP * 1.5):
            self.isOvercharged = 1
        else:
            self.isOvercharged = 0

    def setNeutralAnimationHead(self):
        if self.getDizzy():
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
            Sequence(Func(self.setPlayRate, self.getPlayRate2(), 'lured'), Func(self.setPlayRate, self.getPlayRate2(), 'lured2'), Func(self.loop, 'lured')
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
            Sequence(Func(self.setPlayRate, self.getPlayRate2(), 'neutral%s' % ('-hurt' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',)), Func(self.loop, 'neutral%s' % ('-hurt' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',))
            ).start()

    def setNeutralAnimation(self):
        if self.getDizzy():
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
            Sequence(Func(self.setPlayRate, self.getPlayRate2(), 'lured'), Func(self.setPlayRate, self.getPlayRate2(), 'lured2'), Func(self.loop, 'lured')
                     ).start()
        elif self.dna.name == 'jur' and self.getActualLevel() == 24:
            Sequence(Func(self.setPlayRate, self.getPlayRate2(), 'pace'), Func(self.loop, 'pace')
                     ).start()
        elif self.dna.name == 'mdr' and self.getActualLevel() == 23:
            Sequence(Func(self.setPlayRate, self.getPlayRate2(), 'rolled'), Func(self.loop, 'rolled')
                     ).start()
        elif self.isChainsawPhase2:
            Sequence(
                Func(self.setPlayRate, self.getPlayRate2(), 'neutral-override%s' % ('-glitched' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',)), Func(self.loop, 'neutral-override%s' % ('-glitched' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',))
                ).start()
        elif self.isOttomanPhase2:
            Sequence(Func(self.setPlayRate, self.getPlayRate2(), 'pace'), Func(self.loop, 'pace')
                     ).start()
        elif self.isAngry:
            Sequence(Func(self.setPlayRate, self.getPlayRate2(), 'neutral-enraged'), Func(self.loop, 'neutral-enraged')
                     ).start()
        elif self.isImmortal and not self.dna.name == 'hroller' and not self.dna.name == 'videog':
            Sequence(Func(self.loop, 'highroller-neutral-levitate-loop')
                     ).start()
        elif self.isDanceSession:
            Sequence(Func(self.loop, 'rolled')
                     ).start()
        elif self.isVulnerable and self.dna.name == 'hroller2':
            Sequence(Func(self.loop, 'neutral2%s' % ('-hurt' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',))
                     ).start()
        elif float(self.currHP) > float(self.maxHP * 1.5):
            Sequence(Func(self.loop, 'neutral-unstable', fromFrame=60, toFrame=100)
                     ).start()
        else:
            self.setNeutralAnimationHead()
            Sequence(Func(self.setPlayRate, self.getPlayRate2(), 'neutral%s' % ('-hurt' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',)), Func(self.loop, 'neutral%s' % ('-hurt' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',))
            ).start()

    def setNeutralAnimationDrop(self):
        if self.getDizzy():
            Sequence(Func(self.setPlayRate, self.getPlayRate2(), 'lured'),
                     Func(self.setPlayRate, self.getPlayRate2(), 'lured2'), Func(self.loop, 'lured')
                     ).start()
        elif self.dna.name == 'jur' and self.getActualLevel() == 24:
            Sequence(Func(self.setPlayRate, self.getPlayRate2(), 'pace'), Func(self.loop, 'pace')
                     ).start()
        elif self.dna.name == 'mdr' and self.getActualLevel() == 23:
            Sequence(Func(self.setPlayRate, self.getPlayRate2(), 'rolled'), Func(self.loop, 'rolled')
                     ).start()
        elif self.isChainsawPhase2:
            Sequence(
                Func(self.setPlayRate, self.getPlayRate2(),
                     'neutral-override%s' % ('-glitched' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',)),
                Func(self.loop,
                     'neutral-override%s' % ('-glitched' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',))
            ).start()
        elif self.isOttomanPhase2:
            Sequence(Func(self.setPlayRate, self.getPlayRate2(), 'pace'), Func(self.loop, 'pace')
                     ).start()
        elif self.isAngry:
            Sequence(Func(self.setPlayRate, self.getPlayRate2(), 'neutral-enraged'), Func(self.loop, 'neutral-enraged')
                     ).start()
        elif self.isImmortal and not self.dna.name == 'hroller' and not self.dna.name == 'videog':
            Sequence(Func(self.loop, 'highroller-neutral-levitate-loop')
                     ).start()
        elif self.isVulnerable and self.dna.name == 'hroller2':
            Sequence(
                Func(self.loop, 'neutral2%s' % ('-hurt' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',))
                ).start()
        elif float(self.currHP) > float(self.maxHP * 1.5):
            Sequence(Func(self.loop, 'neutral-unstable', fromFrame=60, toFrame=100)
                     ).start()
        else:
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
            Sequence(Func(self.setPlayRate, self.getPlayRate2(),
                          'neutral%s' % ('-hurt' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',)),
                     Func(self.loop, 'neutral%s' % ('-hurt' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',))
                     ).start()

    def setNeutralAnimationRolled(self):
        if self.getDizzy():
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
            Sequence(Func(self.setPlayRate, self.getPlayRate2(), 'lured'), Func(self.setPlayRate, self.getPlayRate2(), 'lured2'), Func(self.loop, 'lured')
                     ).start()
        else:
            for headPart in self.animatedHeadParts: Sequence(
                Func(headPart.loop, 'neutral%s' % ('-hurt' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',))
            ).start()
            Sequence(Func(self.setPlayRate, self.getPlayRate2(), 'rolled'), Func(self.loop, 'rolled')
            ).start()

    def setNeutralAnimationTrap(self):
        if self.isAngry:
            for headPart in self.animatedHeadParts: Sequence(
                Func(headPart.loop, 'neutral%s' % ('-hurt' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',))
            ).start()
            Sequence(Func(self.loop, 'neutral-enraged')
                     ).start()
        elif self.isChainsawPhase2:
            for headPart in self.animatedHeadParts: Sequence(
                Func(headPart.loop, 'neutral%s' % ('-hurt' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',))
            ).start()
            Sequence(
                Func(self.loop, 'neutral-overide%s' % ('-glitched' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',))
                ).start()
        elif self.isImmortal and not self.dna.name == 'hroller' and not self.dna.name == 'videog':
            for headPart in self.animatedHeadParts: Sequence(
                Func(headPart.loop, 'neutral%s' % ('-hurt' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',))
            ).start()
            Sequence(Func(self.loop, 'highroller-neutral-levitate-loop')
                     ).start()
        elif self.isVulnerable and self.dna.name == 'hroller2':
            for headPart in self.animatedHeadParts: Sequence(
                Func(headPart.loop, 'neutral%s' % ('-hurt' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',))
            ).start()
            Sequence(Func(self.loop, 'neutral2%s' % ('-hurt' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',))
                     ).start()
        elif float(self.currHP) > float(self.maxHP * 1.5):
            for headPart in self.animatedHeadParts: Sequence(
                Func(headPart.loop, 'neutral%s' % ('-hurt' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',))
            ).start()
            Sequence(Func(self.loop, 'neutral-unstable')
                     ).start()
        else:
            for headPart in self.animatedHeadParts: Sequence(
                Func(headPart.loop, 'neutral%s' % ('-hurt' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',))
            ).start()
            Sequence(Func(self.loop, 'neutral%s' % ('-hurt' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',))
            ).start()

    def setChatAbsoluteTrap(self, chatString, chatFlags, dialogue=None, interrupt=True):
        searchString = chatString.lower()
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
        for headPart in self.animatedHeadParts: Sequence(
            Func(headPart.loop, 'neutral%s' % ('-hurt' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',))
                ).start()

    def setChatAbsolute(self, chatString, chatFlags, dialogue=None, interrupt=True):
        searchString = chatString.lower()
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
        if self.animHead == None and self.getDizzy():
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
        elif self.getDizzy():
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
            elif self.dna.name == 'bcaster':
                for headPart in self.animatedHeadParts: Sequence(ActorInterval(headPart, self.animHead),
                    Func(headPart.loop, 'stun')
                    ).start()
            else:
                for headPart in self.animatedHeadParts: Sequence(ActorInterval(headPart, self.animHead),
                    Func(headPart.loop, 'neutral%s' % ('-hurt' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',))
                    ).start()

    def setChatAbsoluteSpecial(self, chatString, chatFlags, dialogue=None, interrupt=True):
        searchString = chatString.lower()
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