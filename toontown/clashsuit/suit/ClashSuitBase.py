"""ClashSuit module: contains the ClashSuit class"""

from direct.controls.ControlManager import CollisionHandlerRayStart
from direct.distributed.ClockDelta import *
from direct.interval.IntervalGlobal import *
from direct.task import Task
from panda3d.core import *
from toontown.clashbattle.battle import BattleBase
from toontown.clashbattle.battle import SuitBattleGlobals
from toontown.clashbattle.battle import PassiveAttributeDefs
from toontown.clashbattle.battle.attacks.base.AttackEnum import AttackEnum
from toontown.clashsuit.suit import Suit, SuitDNA
from toontown.clashsuit.suit import SuitBase
from toontown.clashsuit.suit import SuitDialog
from toontown.clashsuit.suit import SuitTimings
from toontown.clashsuit.suit import SuitHealthMeter
from otp.avatar import DistributedAvatar
from toontown.toonbase import ToontownGlobals
from toontown.clashbattle.battle import BattleProps
from otp import *

from toontown.clashsuit.suit.SuitDefinitionsBase import SuitDefinitions
from toontown.toonbase import TTLocalizer
from toontown.clashbattle.battle import BattleGlobals
from toontown.toonbase import ToontownGlobals
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory

from typing import List


@DirectNotifyCategory()
class ClashSuitBase(DistributedAvatar.DistributedAvatar, Suit.Suit, SuitBase.SuitBase):
    """
    ClashSuit class:  a 'bad guy' which exists on each client's
     machine and helps direct the Suits which exist on the server.  This
     is the object that each individual player interacts with when
     initiating combat.  This guy has all of the attributes of a
     ClashSuitAI object, plus some more such as collision info

    Attributes:
       Derived plus...
       DistributedSuit_initialized (integer), flag indicating if this
           suit has been properly initialized
       fsm, the state machine that this client suit will use, this
           includes states of detecting collisions with toons and
           entering battles
       dna, dna created for the suit, sent to us from the server
    """

    def __init__(self, cr):
        try:
            self.DistributedSuitBase_initialized
            return
        except:
            self.DistributedSuitBase_initialized = 1

        DistributedAvatar.DistributedAvatar.__init__(self, cr)
        Suit.Suit.__init__(self)
        SuitBase.SuitBase.__init__(self)
        self.activeShadow = 0
        self.virtual = 0
        # collision junk
        self.battleDetectName = None
        self.cRay = None
        self.cRayNode = None
        self.cRayNodePath = None
        self.cRayBitMask = None
        self.lifter = None
        self.cTrav = None
        # our reference to the local hood's suit planner, the doId of
        # it is sent to us from the server side suit
        self.sp = None

        # propellers for flying into and out of the streets
        self.prop = None
        self.propInSound = base.loader.loadSfx('phase_5/audio/sfx/ENC_propeller_in.ogg')
        self.propOutSound = base.loader.loadSfx('phase_5/audio/sfx/ENC_propeller_out.ogg')
        self.lockProp = False

        # number of times to reanimate into a skeleCog
        self.skeleRevives = 0
        # keep track of how many times we have reanimated
        self.maxSkeleRevives = 0
        # Tracked after-revive damage in a track, hp lost/maxhp
        self.afterReviveDamage = [0, 0]  # type: List[int, int]
        self.maxHp = 10
        self.hp = 10
        self.healthInitialized = False
        # Use this for displaying hp bonus text
        self.interactivePropTrackBonus = -1
        # Timescale setting for battle speed cheats
        self.timescale = 1.0
        self.stunStars = None
        self.suedEffect = None
        self.stashed = False

        # NOTE: keep this stuff at the bottom of __init__
        # make sure to hide the suit when first created, it is not yet
        # placed in the right location, so if its current location happens
        # to be on the street, we don't want it visible
        self.reparentTo(hidden)
        self.loop('neutral')

    def setPersistent(self, flag: bool) -> None:
        self.persistent = flag

    def getPersistent(self) -> bool:
        return self.persistent

    def setVirtual(self, virtual):
        self.virtual = virtual

    def getVirtual(self):
        return 0

    def setSkeleRevives(self, num):
        if num is None:
            num = 0
        self.skeleRevives = num
        nameInfo = self.createNameInfo()
        self.setDisplayName(nameInfo)

    def getSkeleRevives(self):
        return self.skeleRevives

    def setMaxSkeleRevives(self, num):
        if num is None:
            num = 0
        self.maxSkeleRevives = num

    def getMaxSkeleRevives(self):
        return self.maxSkeleRevives

    def setAfterReviveDamage(self, afterReviveDamage):
        self.afterReviveDamage = afterReviveDamage

    def setStashed(self, mode):
        self.stashed = mode
        try:
            if mode:
                self.stash()
            else:
                self.unstash()
        except AssertionError:
            # We don't exist yet :(
            pass

    def getStashed(self):
        return self.isStashed()

    def generate(self):
        """
        Called when the DistributedObject is reintroduced to the world, either for the first time or from the cache.
        """
        DistributedAvatar.DistributedAvatar.generate(self)

    def announceGenerate(self):
        super().announceGenerate()
        if self.stashed:
            self.stash()

        self.doMethodLater(5.0, self.fixBoundsTask, name=self.uniqueName('fixBoundsTask'))

    def fixBoundsTask(self, task):
        self.fixBounds()
        return task.done

    def disable(self):
        """
        This method is called when the DistributedObject
        is removed from active duty and stored in a cache.
        """
        self.notify.debug('ClashSuit %d: disabling' % self.getDoId())
        self.ignoreAll()
        self.__removeCollisionData()
        self.stop()
        if self.propInSound:
            self.propInSound.stop()
        if self.propOutSound:
            self.propOutSound.stop()
        taskMgr.remove(self.uniqueName('blink-task'))
        self.removeAllTasks()
        DistributedAvatar.DistributedAvatar.disable(self)

    def delete(self):
        """
        This method is called when the DistributedObject is
        permanently removed from the world and deleted from
        the cache.
        """
        try:
            self.DistributedSuitBase_deleted
            return
        except:
            self.DistributedSuitBase_deleted = 1

        self.notify.debug('ClashSuit %d: deleting' % self.getDoId())
        # Get rid of sounds
        if self.propInSound:
            self.propInSound.stop()
            self.propInSound = None
        if self.propOutSound:
            self.propOutSound.stop()
            self.propOutSound = None
        del self.dna
        del self.sp
        DistributedAvatar.DistributedAvatar.delete(self)
        Suit.Suit.delete(self)
        SuitBase.SuitBase.delete(self)

    # We need to force the Suit version of these to be called, otherwise
    # we get the generic Avatar version which is undefined
    def setDNAString(self, dnaString):
        Suit.Suit.setDNAString(self, dnaString)

    def setDNA(self, dna):
        Suit.Suit.setDNA(self, dna)

    def getHp(self):
        return self.hp

    def getMaxHp(self):
        return self.maxHp

    def setHp(self, hp):
        """
        Function:    set the current health of this suit, this can
                     be called during battle and at initialization
        Parameters:  hp, value to set health to
        """
        oldHP = self.hp
        self.hp = hp
        if oldHP != self.hp:
            self.updateHealthBar(0, 1)
        # Disabled for april toons overhealed cog fight, let cogs have over their max hp
        # if hp > self.maxHp:
        #     self.hp = self.maxHp
        # else:
        #     self.hp = hp
        if self.specialHead:
            if self.getCurrentAnim() == 'lured':
                pass
            else:
                self.specialHead.loopNeutral()

    def toonUp(self, hpGained):
        return  # NO

    def takeDamage(self, hpLost, bonus=0):
        return  # NO

    def updateHealthBar(self, hp, forceUpdate=0):
        Suit.Suit.updateHealthBar(self, hp, forceUpdate)
        messenger.send(f'suitHpChanged-{self.doId}')

    def getDialogueArray(self, *args):
        # Force the right inheritance chain to be called
        return Suit.Suit.getDialogueArray(self, *args)

    def __removeCollisionData(self):
        """
        clean up the suit's various collision data such
        as the battle detection sphere, the ground collision
        ray, and the lifter
        """
        # make sure to remove any raycast information
        self.enableRaycast(0)

        self.cRay = None
        self.cRayNode = None
        self.cRayNodePath = None

        self.lifter = None

        self.cTrav = None

    def setHeight(self, height):
        # We want to make sure we get the specialized one.
        Suit.Suit.setHeight(self, height)

    def getRadius(self):
        # We want to make sure we get the specialized one.
        return Suit.Suit.getRadius(self)

    def setLevelDist(self, level, hpMultIndex=0):
        """
        level is the new level (int) of the suit.

        The distributed function to be called when the
        server side suit changes level
        """
        if self.notify.getDebug():
            self.notify.debug('Got level %d from server for suit %d' % (level, self.getDoId()))
        self.setLevel(level, hpMultIndex=hpMultIndex)

    def attachPropeller(self):
        """
        attach a propeller to this suit, used when the suit
        is going into it's flying animation
        """
        if self.prop is None:
            self.prop = BattleProps.globalPropPool.getProp('propeller')
        head = self.find('**/to_head')
        if head.isEmpty():
            head = self.find('**/joint_head')

        self.prop.reparentTo(head)

    def setPropellerLocked(self, locked=False):
        self.lockProp = locked
        if not locked:
            self.detachPropeller()

    def detachPropeller(self):
        """
        remove the propeller from a suit if it has one, this
        is used after a suit is done with its flying anim
        """
        if self.lockProp:
            if self.prop:
                self.prop.hide()
            return

        if self.prop:
            self.prop.cleanup()
            self.prop.removeNode()
            self.prop = None

    def beginSupaFlyMove(self, pos, moveIn, trackName, walkAfterLanding=True, speed=1.0, soundSpeed=1.0, flyOutBasedOnCurrentPos=False):
        """
        beginSupaFlyMove(self, Point3 pos, bool moveIn, string trackName)
        Returns an interval that will animate the suit either up into
        the sky or back down to the ground, based on moveIn.
        pos is the point on the street over which the animation takes
        place.
        """

        skyPos = Point3(pos)
        initialZ = 0 if flyOutBasedOnCurrentPos else pos.getZ()
        # calculate a point in the sky based on how fast a suit walks
        # and how long it has been determined that flying away should take
        if moveIn == 1:
            skyPos.setZ(initialZ + SuitTimings.fromSky * ToontownGlobals.SuitWalkSpeed)
        elif moveIn == 2:
            skyPos.setZ(initialZ + (SuitTimings.fromSky - 4.5) * ToontownGlobals.SuitWalkSpeed)
        else:
            skyPos.setZ(initialZ + SuitTimings.toSky * ToontownGlobals.SuitWalkSpeed)

        # calculate some times used to manipulate the suit's landing
        # animation
        groundF = 28
        dur = self.getDuration('landing')
        fr = self.getFrameRate('landing')
        # length of time in animation spent in the air
        if fr:
            animTimeInAir = groundF / fr
        else:
            animTimeInAir = groundF
        animTimeInAir /= speed
        # length of time in animation spent impacting and reacting to
        # the ground
        impactLength = dur - animTimeInAir
        # the frame at which the suit touches the ground
        timeTillLanding = SuitTimings.fromSky - impactLength
        # time suit spends playing the flying portion of the landing anim
        if moveIn == 2:
            timeTillLanding = SuitTimings.fromSky - impactLength - 3
        waitTime = timeTillLanding - animTimeInAir

        # now create info for the propeller's animation
        if self.prop is None:
            self.prop = BattleProps.globalPropPool.getProp('propeller')
        propDur = self.prop.getDuration('propeller')
        lastSpinFrame = 8
        fr = self.prop.getFrameRate('propeller')
        # time from beginning of anim at which propeller plays its spin
        spinTime = lastSpinFrame / fr
        # time from beginning of anim at which propeller starts to close
        openTime = (lastSpinFrame + 1) / fr

        if moveIn:
            # if we are moving into the neighborhood from the sky, move
            # down from above (skyPos) the first waypoint in the suit's
            # current path (pos), first create an interval that will
            # move the suit over time, then create a function interval
            # to set the suit's animation to a single frame (the first)
            # of the landing animation, then create a wait interval to
            # wait for the suit to get closer to the ground, then create
            # an actor interval to play the landing animation so it ends
            # when the suit touches the ground, and lastly create a
            # function interval to make sure the suit goes into it's
            # walk animation once it lands

            # create the lerp intervals that will go in the first track,
            # also reparent the suit's shadow to render and set the
            # position of it below the suit on the ground
            lerpPosTrack = Sequence(self.posInterval(timeTillLanding, pos, startPos=skyPos), Wait(impactLength))
            # create a scale interval for the suit's shadow so it scales
            # up as the suit gets closer to the ground

            # keep Z scale at 1. so that lifter doesn't go crazy-go-nuts and set Z to infinity
            shadowParent = self.getParent()
            if shadowParent is hidden:
                shadowParent = render
            firstShadowScale = self.dropShadow.getScale(shadowParent)
            secondShadowScale = self.dropShadow.getScale()
            for scale in (firstShadowScale, secondShadowScale):
                scale[2] = 1.0
            shadowTrack = Sequence(Func(self.dropShadow.reparentTo, render),
                                   Func(self.dropShadow.setPos, shadowParent, pos),
                                   self.dropShadow.scaleInterval(timeTillLanding, firstShadowScale, startScale=Vec3(0.01, 0.01, 1.0)),
                                   Func(self.dropShadow.reparentTo, self.getShadowJoint()),
                                   Func(self.dropShadow.setPos, 0, 0, 0),
                                   Func(self.dropShadow.setHpr, 0, 0, 0),
                                   Func(self.dropShadow.setScale, secondShadowScale))
            fadeInTrack = Sequence(Func(self.setTransparency, 1),
                                   self.colorScaleInterval(1, colorScale=VBase4(1, 1, 1, 1), startColorScale=VBase4(1, 1, 1, 0)),
                                   Func(self.clearColorScale),
                                   Func(self.clearTransparency))

            # now create the suit animation intervals that will go in the
            # second track
            animTrack = Sequence(Func(self.pose, 'landing', 0),
                                 Wait(waitTime),
                                 ActorInterval(self, 'landing', duration=dur))
            if walkAfterLanding:
                animTrack.append(Func(self.loop, 'walk'))

            # now create the propeller animation intervals that will go in
            # the third and final track
            self.attachPropeller()
            self.propInSound.setPlayRate(speed * soundSpeed)
            propTrack = Parallel(SoundInterval(self.propInSound, duration=waitTime + dur, node=self),
                                 Sequence(Func(self.prop.show),
                                          ActorInterval(self.prop, 'propeller', constrainedLoop=1, duration=waitTime + spinTime, startTime=0.0, endTime=spinTime),
                                          ActorInterval(self.prop, 'propeller', startTime=openTime, playRate=1.2),
                                          Func(self.detachPropeller)))
            return Parallel(lerpPosTrack,
                            shadowTrack,
                            fadeInTrack,
                            animTrack,
                            propTrack,
                            name=self.taskName('trackName'))
        else:
            # move to the sky, move vertically from the current
            # position to some location in the sky, also reparent the
            # suit's shadow to render and set the position of it below
            # the suit on the ground
            if flyOutBasedOnCurrentPos:
                referenceNode = render.attachNewNode(self.uniqueName("flyOutReferenceNode"))

                lerpPosTrack = Sequence(
                    Wait(impactLength),
                    Func(referenceNode.setPos, self, 0, 0, 0),
                    LerpPosInterval(self, timeTillLanding, skyPos, startPos=pos, other=referenceNode),
                    Func(referenceNode.removeNode)
                )
            else:
                lerpPosTrack = Sequence(
                    Wait(impactLength),
                    LerpPosInterval(self, timeTillLanding, skyPos, startPos=pos)
                )
            # create a scale interval for the suit's shadow so it scales
            # down as the suit gets further from the ground

            # keep Z scale at 1. so that lifter doesn't go crazy-go-nuts and set Z to infinity
            shadowTrack = Sequence(Func(self.dropShadow.reparentTo, render),
                                   Func(self.dropShadow.setPos, self, pos) if flyOutBasedOnCurrentPos else Func(self.dropShadow.setPos, pos),
                                   self.dropShadow.scaleInterval(timeTillLanding, Vec3(0.01, 0.01, 1.0), startScale=self.scale),
                                   Func(self.dropShadow.reparentTo, self.getShadowJoint()),
                                   Func(self.dropShadow.setPos, 0, 0, 0))
            fadeOutTrack = Sequence(Func(self.setTransparency, 1),
                                    self.colorScaleInterval(1, colorScale=VBase4(1, 1, 1, 0), startColorScale=VBase4(1, 1, 1, 1)),
                                    Func(self.clearColorScale),
                                    Func(self.clearTransparency),
                                    Func(self.reparentTo, hidden))
            actInt = ActorInterval(self, 'landing', loop=0, startTime=dur, endTime=0.0)
            # now create the propeller animation intervals that will go in
            # the third and final track
            self.attachPropeller()
            self.prop.hide()
            propTrack = Parallel(SoundInterval(self.propOutSound, duration=waitTime + dur, node=self),
                                 Sequence(Func(self.prop.show),
                                          ActorInterval(self.prop, 'propeller', endTime=openTime, startTime=propDur),
                                          ActorInterval(self.prop, 'propeller', constrainedLoop=1, duration=propDur - openTime, startTime=spinTime, endTime=0.0),
                                          Func(self.detachPropeller)))
            return Parallel(ParallelEndTogether(lerpPosTrack,
                                                shadowTrack,
                                                fadeOutTrack),
                            actInt,
                            propTrack,
                            name=self.taskName('trackName'))

    def enableBattleDetect(self, name, handler):
        if self.collTube:
            # We recreate the sphere node every time we switch states
            # to force the collision event to be regenerated even if
            # the avatar was already within the suit's bubble.
            self.battleDetectName = self.taskName(name)
            self.collNode = CollisionNode(self.battleDetectName)
            self.collNode.addSolid(self.collTube)
            self.collNodePath = self.attachNewNode(self.collNode)
            self.collNode.setCollideMask(ToontownGlobals.WallBitmask | ToontownGlobals.PieBitmask)
            self.collNode.setTag('pieCode', str(ToontownGlobals.PieCodeNotBossCog))
            self.collNode.setTag('pieBattleDetect', str(self.doId))
            self.accept('enter' + self.battleDetectName, handler)

        return Task.done

    def disableBattleDetect(self):
        if self.battleDetectName:
            self.ignore('enter' + self.battleDetectName)
            self.battleDetectName = None
        if self.collNodePath:
            self.collNodePath.removeNode()
            self.collNodePath = None

    def enableRaycast(self, enable = 1):
        """
        enable/disable raycast, useful for when we know
        when the suit will change elevations
        """
        if not self.cTrav or not hasattr(self, 'cRayNode') or not self.cRayNode:
            return

        self.cTrav.removeCollider(self.cRayNodePath)
        if enable:
            if self.notify.getDebug():
                self.notify.debug('enabling raycast')
            self.cTrav.addCollider(self.cRayNodePath, self.lifter)
        elif self.notify.getDebug():
            self.notify.debug('disabling raycast')

    def b_setBrushOff(self, index):
        # Local
        self.setBrushOff(index)
        # Distributed
        self.d_setBrushOff(index)

    def d_setBrushOff(self, index):
        self.sendUpdate('setBrushOff', [index])

    def setBrushOff(self, index):
        seq = Sequence(Func(self.setChatAbsolute, SuitDialog.getBrushOffText(self.getStyleName(), index), CFSpeech | CFTimeout), Wait(1.5), Func(self.clearChat))
        seq.start()

    def initializeBodyCollisions(self, collIdStr):
        """
        set up collision information for this cog,
        only do once when creating the cog
        """
        DistributedAvatar.DistributedAvatar.initializeBodyCollisions(self, collIdStr)

        if not self.ghostMode:
            self.collNode.setCollideMask(self.collNode.getIntoCollideMask() | ToontownGlobals.PieBitmask)

        # Set up the collison ray
        # This is a ray cast from your head down to detect floor polygons
        # and is only turned on during specific parts of the suit's path
        self.cRay = CollisionRay(0.0, 0.0, CollisionHandlerRayStart, 0.0, 0.0, -1.0)
        self.cRayNode = CollisionNode(self.taskName('cRay'))
        self.cRayNode.addSolid(self.cRay)
        self.cRayNodePath = self.attachNewNode(self.cRayNode)
        self.cRayNodePath.hide()
        self.cRayBitMask = ToontownGlobals.FloorBitmask
        self.cRayNode.setFromCollideMask(self.cRayBitMask)
        self.cRayNode.setIntoCollideMask(BitMask32.allOff())

        # set up floor collision mechanism
        self.lifter = CollisionHandlerFloor()
        self.lifter.setOffset(ToontownGlobals.FloorOffset)
        self.lifter.setReach(6.0)

        # Limit our rate-of-fall with the lifter.
        self.lifter.setMaxVelocity(8.0)
        self.lifter.addCollider(self.cRayNodePath, self)

        # now use the standard collision traverser to handle updating
        # collision info
        self.cTrav = base.cTrav

    def disableBodyCollisions(self):
        self.disableBattleDetect()
        self.enableRaycast(0)
        if self.cRayNodePath:
            self.cRayNodePath.removeNode()
        del self.cRayNode
        del self.cRay
        del self.lifter

    def loop(self, animName, restart=1, partName=None, fromFrame=None, toFrame=None):
        animName = self.getAnim(animName)

        # Any special head animations associated with
        # the animation names.
        if self.specialHead:
            if animName == 'lured':
                self.specialHead.loop('neutral-lured')

        self.setPlayRate(math.pow(self.timescale, 0.2), animName)
        super().loop(animName, restart=restart, partName=partName, fromFrame=fromFrame, toFrame=toFrame)

    def actorInterval(self, animName, loop=0, constrainedLoop=0, duration=None, startTime=None, endTime=None,
                      startFrame=None, endFrame=None, playRate=1.0, name=None, forceUpdate=0, partName=None,
                      lodName=None):
        # Fill in animation override
        animName = self.getAnim(animName)
        return ActorInterval(self, animName, loop=loop, constrainedLoop=constrainedLoop, duration=duration,
                             startTime=startTime, endTime=endTime, startFrame=startFrame, endFrame=endFrame,
                             playRate=playRate, name=name, forceUpdate=forceUpdate, partName=partName, lodName=lodName)

    def updateSoundSpeed(self, sound):
        # is accurate to the timescale modifier in PickUpThePace.py
        newSpeed = math.pow(self.timescale, 0.16)
        if self.timescale < 1:
            newSpeed = self.timescale
        sound.setPlayRate(newSpeed)

    def setTimescale(self, timescale):
        """sets the suit's timescale (for local loops)"""
        self.timescale = timescale

    def denyBattle(self):
        self.notify.debug('denyBattle()')

        # Deny the local toon's request for battle.  This is only sent
        # directly to a toon who requested the battle; other toons in
        # the zone don't see this message.

        place = self.cr.playGame.getPlace()
        if place.getCurrentOrNextState() == 'WaitForBattle':
            place.setState('walk')
        self.resumePath(self.pathState)

    def makePathTrack(self, nodePath, posPoints, velocity, name):
        track = Sequence(name=name)
        nodePath.setPos(posPoints[0])
        for pointIndex in range(len(posPoints) - 1):
            startPoint = posPoints[pointIndex]
            endPoint = posPoints[pointIndex + 1]
            # Face the endpoint
            track.append(Func(nodePath.headsUp, endPoint[0], endPoint[1], endPoint[2]))
            # Calculate the amount of time we should spend walking
            distance = Vec3(endPoint - startPoint).length()
            duration = distance / velocity
            # Walk to the end point
            track.append(LerpPosInterval(nodePath, duration=duration, pos=Point3(endPoint), startPos=Point3(startPoint)))

        return track

    def setState(self, state):
        # check to make sure we aren't going into the state we are already
        # in, this is useful so we don't go into the Off state when already
        # in the off state, which will result in the stopping of a currently
        # playing track
        if self.getCurrentOrNextState() == state:
            return 0

        return self.request(state)

    # Specific State functions

    ##### Off state #####

    def subclassManagesParent(self):
        # factory suits are parented under other nodes, and the
        # parent info doesn't need to be distributed
        return 0

    def enterOff(self, *args):
        self.hideNametag3d()
        self.hideNametag2d()
        if not self.subclassManagesParent():
            self.setParent(ToontownGlobals.SPHidden)

    def exitOff(self):
        if not self.subclassManagesParent():
            self.setParent(ToontownGlobals.SPRender)
        self.showNametag3d()
        self.showNametag2d()
        self.loop('neutral', 0)

    ##### Battle state #####

    def enterBattle(self):
        # Join a battle object and let it take over control of the suit
        self.loop('neutral', 0)
        self.disableBattleDetect()
        self.healthBar.updateMeterMode(SuitHealthMeter.MODE_BATTLE)

        # make sure health bar updates current suit condition
        if self.getHp() <= self.getMaxHp():
            self.updateHealthBar(0, 1)

    def exitBattle(self):
        self.healthBar.updateMeterMode(SuitHealthMeter.MODE_ROAM)
        self.hp = self.getMaxHp()
        self.interactivePropTrackBonus = -1

    ##### WaitForBattle state #####

    def enterWaitForBattle(self):
        self.loop('neutral', 0)

    def exitWaitForBattle(self):
        pass

    def setSkelecog(self, flag):
        alreadySkelecog = self.getSkelecog()
        super().setSkelecog(flag)
        if flag:
            if not alreadySkelecog:
                super().makeSkeleton(self.getElite())
            elif self.style.name in SuitDNA.suitHeadTypes or SuitDNA.isAlternate(self.style.name):
                nameInfo = self.createNameInfo()
                self.setDisplayName(nameInfo)

    def setWaiter(self, flag):
        SuitBase.SuitBase.setWaiter(self, flag)
        if flag:
            Suit.Suit.makeWaiter(self)

    def setElite(self, flag):
        SuitBase.SuitBase.setElite(self, flag)
        if flag:
            Suit.Suit.makeExecutive(self)
            nameInfo = self.createNameInfo()
            self.setDisplayName(nameInfo)
            if self.isSkeleton:
                Suit.Suit.setSkeleClothes(self, elite=True)

            self.healthBar.updateMeterMode(SuitHealthMeter.MODE_ROAM)

    def setMaxHp(self, hp):
        self.healthInitialized = True
        oldMaxHp = self.maxHp
        self.maxHp = int(hp)
        self.hp = int(hp)
        if oldMaxHp != self.maxHp:
            self.updateHealthBar(0, forceUpdate=1)
        if self.healthBar.mode != SuitHealthMeter.MODE_BATTLE:
            self.healthBar.updateMeterMode(SuitHealthMeter.MODE_ROAM)

    def showHpText(self, number, bonus=0, scale=1, attackTrack=-1, rounds=-1, extraText='', rttIndex=None, fromVisual=False):
        if not fromVisual:
            hpTextOverride = self.getHpTextOverride(number, bonus=bonus, scale=scale, attackTrack=attackTrack,
                                                    rounds=rounds, extraText=extraText, rttIndex=rttIndex)
            if hpTextOverride:
                # This means that a visual effect is overriding our hp text. Let's just let that handle it instead.
                return

        if self.HpTextEnabled and not self.ghostMode:
            # Get rid of the number if it is already there.
            if self.hpText:
                self.hideHpText()
            # Set the font
            self.HpTextGenerator.setFont(ToontownGlobals.getSignFont())

            if number < 0 or attackTrack == AttackEnum.TOON_LURE:
                self.HpTextGenerator.setText(str(number))

                rtt = TTLocalizer.RoundTrackTerms.get(attackTrack)
                if isinstance(rtt, (tuple, list)):
                    if rttIndex is not None:
                        rtt = rtt[rttIndex]
                    else:
                        rtt = None

                # Do not display the -1 rounds text if the
                # cog isn't drenched.
                if attackTrack == AttackEnum.TOON_ZAP:
                    if rttIndex is None:
                        rtt = None

                if rtt is not None:
                    if attackTrack == AttackEnum.TOON_LURE:
                        if rounds == -2:
                            trackTerm = TTLocalizer.LuredImmune
                        elif rounds == -3:
                            trackTerm = TTLocalizer.LuredTrappedCog
                        elif rounds == 1:
                            trackTerm = TTLocalizer.LuredOneRound
                        else:
                            trackTerm = rtt.format(rounds)
                        self.HpTextGenerator.setText(trackTerm)
                    else:
                        self.HpTextGenerator.setText(str(number) + '\n' + rtt.format(rounds))

            elif attackTrack == AttackEnum.TOON_SUE:
                self.HpTextGenerator.setText(TTLocalizer.CeaseAndDesist)
            elif number == 0:
                self.HpTextGenerator.setText('-' + str(number))
            else:
                self.HpTextGenerator.setText('+' + str(number))
            if extraText:
                self.HpTextGenerator.setText(self.HpTextGenerator.getText() + f'\n{extraText}')
            # No shadow
            self.HpTextGenerator.clearShadow()
            # Center the number
            self.HpTextGenerator.setAlign(TextNode.ACenter)
            # Red for negative, green for positive, yellow for bonus, orange for kb
            if bonus == 1:
                r = 1.0
                g = 1.0
                b = 0
                a = 1
            elif bonus == 2:
                r = 1.0
                g = 0.5
                b = 0
                a = 1
            elif attackTrack == AttackEnum.TOON_LURE:
                if rounds == -3:
                    # Trapped
                    r = 1.0
                    g = 0.0
                    b = 0
                    a = 1
                else:
                    # Regular lured
                    r = 0.31
                    g = 0.75
                    b = 0.31
                    a = 1.0
            elif attackTrack == AttackEnum.TOON_SUE:
                r = 0.9
                g = 0.9
                b = 0.9
                a = 1.0
            elif number <= 0:
                # if we have a track bonus, for now make it blue
                if self.interactivePropTrackBonus > -1 and self.interactivePropTrackBonus == attackTrack:
                    r = 0
                    g = 0
                    b = 1
                    a = 1
                else:
                    r = 0.9
                    g = 0
                    b = 0
                    a = 1
            else:
                r = 0
                g = 0.9
                b = 0
                a = 1

            self.HpTextGenerator.setTextColor(r, g, b, a)

            self.hpTextNode = self.HpTextGenerator.generate()

            # Put the hpText over the head of the avatar
            self.hpText = self.attachNewNode(self.hpTextNode)
            self.hpText.setScale(scale)
            self.hpText.setColorScaleOff(1)
            # Make sure it is a billboard
            self.hpText.setBillboardPointEye()
            # Render it after other things in the scene.
            self.hpText.setBin('fixed', 100)
            # Initial position ... Center of the body... the "tan tien"
            self.hpText.setPos(0, 0, self.height / 2)
            extraHeight = 2.15 if self.HpTextGenerator.getText().find('\n') != -1 else 1.5
            # Fly the number out of the character

            def setAlphaScale(value):
                if self.hpText:
                    self.hpText.setAlphaScale(value)

            self.hpTextInterval = Sequence(
                self.hpText.posInterval(1.0, Point3(0, 0, self.height + extraHeight), blendType='easeOut'),
                Wait(0.85),
                LerpFunctionInterval(setAlphaScale, 0.5, fromData=1.0, toData=0.0),
                Func(self.hideHpText))
            self.hpTextInterval.start()

    def hideHpText(self):
        try:
            DistributedAvatar.DistributedAvatar.hideHpText(self)
        except:
            pass

    def getAvIdName(self):
        try:
            level = self.getActualLevel()
        except:
            level = '???'

        return '%s\n%s\nLevel %s' % (self.getName(), self.doId, level)

    def cleanupStunStars(self):
        if self.stunStars:
            self.stunStars.cleanup()
            self.stunStars.removeNode()
            self.stunStars = None

    def createNameInfo(self, wantDept=True):
        nameName = self._name
        if self.isSkeleton and (self.style.name in SuitDNA.suitHeadTypes or SuitDNA.isAlternate(self.style.name)):
            nameName = TTLocalizer.Skeleton
        nameDept = SuitDefinitions[self.style.name].departmentOverride or self.getStyleDept()
        nameLevel = str(self.getActualLevel())
        if self.isElite and not self.isMiniboss():
            nameLevel += TTLocalizer.AvatarSuitPanelExecutive
        elif self.isMiniboss():
            nameLevel += TTLocalizer.AvatarSuitPanelManager
        if self.getSkeleRevives() > 0:
            nameLevel += TTLocalizer.SkeleRevivePostFix
        if wantDept and not SuitDefinitions[self.style.name].hideDepartment:
            nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': nameName,
                                                            'dept': nameDept,
                                                            'level': nameLevel}
        else:
            nameInfo = TTLocalizer.SuitBaseNameWithNoDept % {'name': nameName,
                                                            'level': nameLevel}
        return nameInfo

    def neutralAvatar(self):
        super().neutralAvatar()
        if self.specialHead:
            self.specialHead.loopNeutral()

    def onSuitAttackBegin(self):
        # Run through all visual effects and call this
        for ve in self.getVisualEffects():
            ve.onSuitAttackBegin()

    def onSuitAttackEnd(self):
        # Run through all visual effects and call this
        for ve in self.getVisualEffects():
            ve.onSuitAttackEnd()
