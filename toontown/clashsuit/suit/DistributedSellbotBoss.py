import math

from direct.directutil import Mopath
from direct.distributed.ClockDelta import *
from direct.fsm.FSM import FSM
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *
from direct.showbase.PythonUtil import Functor
from direct.showutil import Rope
from direct.task import Task
from otp import *
from toontown.chat.constants.ChatGlobals import CFSpeech, CFTimeout
from toontown.suit import BossCogGlobals
from toontown.battle import BattleBase, MovieToonVictory, RewardPanel
from toontown.battle.BattleProps import *
from toontown.coghq import CogDisguiseGlobals
from toontown.coghq.sellbothq.HQRamp import HQRamp
from toontown.distributed import DelayDelete
from toontown.gui.game.condition import ConditionGlobals
from toontown.inventory.enums.ItemEnums import IOUItemType
from toontown.inventory.registry.IOURegistry import IOURegistry
from toontown.shader import FogGlobals
from toontown.shader.ToontownFog import ToontownFog
from toontown.suit import (DistributedBossCog, SuitDNA,
                           SuitHealthMeter)
from toontown.gui import DepartmentExperienceBar
from toontown.toon.npc import NPCToons
# from toontown.toonbase import BattleGlobals
from toontown.toonbase import ToontownGlobals, TTLocalizer
from toontown.toonbase.GlobalCacheData import GlobalCacheKey
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory

# This pointer keeps track of the one DistributedSellbotBoss that should appear within avatar's current visibility zones
# If there is more than one DistributedSellbotBoss visible to a client at any given time, something is wrong.
OneBossCog = None


@DirectNotifyCategory()
class DistributedSellbotBoss(DistributedBossCog.DistributedBossCog, FSM):
    # The cage slowly drops from the ceiling to the floor as the battle progresses.
    cageHeights = [100, 81, 63, 44, 25, 18]

    def __init__(self, cr):
        DistributedBossCog.DistributedBossCog.__init__(self, cr)
        FSM.__init__(self, 'DistributedSellbotBoss')
        self.cagedToonNpcId = None
        self.doobers = []
        self.dooberRequest = None
        self.bossDamage = 0
        self.attackCode = None
        self.attackAvId = 0
        self.recoverRate = 0
        self.recoverStartTime = 0
        self.bossDamageMovie = None
        self.cagedToon = None
        self.cageShadow = None
        self.cageIndex = 0
        self.everThrownPie = 0
        self.battleThreeMusicTime = 0

        self.insidesANodePath = None
        self.insidesBNodePath = None

        self.rampA = None
        self.rampB = None
        self.rampC = None

        self.strafeInterval = None
        self.onscreenMessage = None

        self.toonMopathInterval = []
        self.localToonPromoted = True
        self.resetMaxDamage()
        self.departmentExpBar = None
        self.rewards = None
        self.skipClickDialogue = False

        self.fogList = []

    def announceGenerate(self):
        """
        Handle all required fields having been filled in.
        """
        base.globalCache.swapToKey(GlobalCacheKey.SellbotBoss)

        global OneBossCog
        DistributedBossCog.DistributedBossCog.announceGenerate(self)
        self.setName(TTLocalizer.SellbotBossName)
        nameInfo = TTLocalizer.BossCogNameWithDept % {
            'name': self.getName(),
            'dept': SuitDNA.getDeptFullname(self.style.dept)
        }
        self.setDisplayName(nameInfo)

        self.healthGui.setBossName(TTLocalizer.SellbotBossName)
        self.healthGui.setMaxHp(self.bossMaxDamage)

        self.cageDoorSfx = loader.loadSfx('phase_5/audio/sfx/CHQ_SOS_cage_door.ogg')
        self.cageLandSfx = loader.loadSfx('phase_9/audio/sfx/CHQ_SOS_cage_land.ogg')
        self.cageLowerSfx = loader.loadSfx('phase_5/audio/sfx/CHQ_SOS_cage_lower.ogg')
        self.piesRestockSfx = loader.loadSfx('phase_9/audio/sfx/CHQ_SOS_pies_restock.ogg')
        self.rampSlideSfx = loader.loadSfx('phase_9/audio/sfx/CHQ_VP_ramp_slide.ogg')
        # We need a different copy of the sfx for each strafe disk.
        self.strafeSfx = []
        for i in range(10):
            self.strafeSfx.append(loader.loadSfx('phase_3.5/audio/sfx/SA_shred.ogg'))

        # Anything in the world we hit that's *not* the BossCog inherits this global pieCode, so the splat will
        # be colored gray.
        render.setTag('pieCode', str(ToontownGlobals.PieCodeNotBossCog))

        # Put some polys inside the boss to detect when a pie gets inside.
        # That will make the boss dizzy.
        insidesA = CollisionPolygon(
            Point3(4.0, -2.0, 5.0), Point3(-4.0, -2.0, 5.0),
            Point3(-4.0, -2.0, 0.5), Point3(4.0, -2.0, 0.5)
        )
        insidesANode = CollisionNode('BossZap')
        insidesANode.addSolid(insidesA)
        insidesANode.setCollideMask(ToontownGlobals.PieBitmask | ToontownGlobals.WallBitmask)
        self.insidesANodePath = self.axle.attachNewNode(insidesANode)
        self.insidesANodePath.setTag('pieCode', str(ToontownGlobals.PieCodeBossInsides))
        self.insidesANodePath.stash()

        insidesB = CollisionPolygon(
            Point3(-4.0, 2.0, 5.0), Point3(4.0, 2.0, 5.0),
            Point3(4.0, 2.0, 0.5), Point3(-4.0, 2.0, 0.5)
        )
        insidesBNode = CollisionNode('BossZap')
        insidesBNode.addSolid(insidesB)
        insidesBNode.setCollideMask(ToontownGlobals.PieBitmask | ToontownGlobals.WallBitmask)
        self.insidesBNodePath = self.axle.attachNewNode(insidesBNode)
        self.insidesBNodePath.setTag('pieCode', str(ToontownGlobals.PieCodeBossInsides))
        self.insidesBNodePath.stash()

        # Make another bubble--a tube--to serve as a target in battle three.
        target = CollisionTube(0, -1, 4, 0, -1, 9, 3.5)
        targetNode = CollisionNode('BossZap')
        targetNode.addSolid(target)
        targetNode.setCollideMask(ToontownGlobals.PieBitmask)
        self.targetNodePath = self.pelvis.attachNewNode(targetNode)
        self.targetNodePath.setTag('pieCode', str(ToontownGlobals.PieCodeBossCog))

        # A similar tube, offset slightly backward, forms a shield from behind.
        # We only want to count hits from the front.
        shield = CollisionTube(0, 1, 4, 0, 1, 7, 3.5)
        shieldNode = CollisionNode('BossZap')
        shieldNode.addSolid(shield)
        shieldNode.setCollideMask(ToontownGlobals.PieBitmask | ToontownGlobals.CameraBitmask)
        self.pelvis.attachNewNode(shieldNode)

        # He also gets a disk-shaped shield around his little cog hula hoop.
        disk = loader.loadModel('phase_9/models/char/bossCog-gearCollide')
        disk.find('**/+CollisionNode').setName('BossZap')
        disk.reparentTo(self.pelvis)
        disk.setZ(0.8)

        self.fogList = [
            ToontownFog(FogGlobals.SellbotVPBossRoomFogAttrs, "VPBossRoom_MainFog"),  # BossRoom
            ToontownFog(FogGlobals.SellbotVPBossSkyFogAttrs, "VPBossRoom_SkyFog"),  # BossSky
            ToontownFog(FogGlobals.SellbotVPBossBuildingFogAttrs, "VPBossRoom_LowerFog"),  # BossTower (lower)
        ]

        # The BossCog actually owns the environment geometry.
        # This is mainly so we can move the ramps in and out under control of the FSM here.
        self.loadEnvironment()

        # Set up the caged toon.
        self.__makeCagedToon()

        self.__loadMopaths()

        if OneBossCog is not None:
            self.notify.warning('Multiple BossCogs visible.')
        OneBossCog = self

    def disable(self):
        """
        Called when the DistributedObject is removed from active duty and stored in a cache.
        """
        global OneBossCog
        DistributedBossCog.DistributedBossCog.disable(self)
        self.request('Off')
        self.unloadEnvironment()
        self.__unloadMopaths()
        self.__cleanupCagedToon()
        self.__clearOnscreenMessage()
        taskMgr.remove(self.uniqueName('PieAdvice'))
        self.__cleanupStrafe()

        render.clearTag('pieCode')

        self.targetNodePath.detachNode()

        self.cr.relatedObjectMgr.abortRequest(self.dooberRequest)
        self.dooberRequest = None

        base.musicMgr.stopMusic()

        while len(self.toonMopathInterval):
            toonMopath = self.toonMopathInterval[0]
            toonMopath.finish()
            toonMopath.destroy()
            self.toonMopathInterval.remove(toonMopath)

        if OneBossCog == self:
            OneBossCog = None

    def resetMaxDamage(self):
        self.bossMaxDamage = BossCogGlobals.SellbotBossMaxDamage

    def d_hitBoss(self, bossDamage):
        self.sendUpdate('hitBoss', [bossDamage])

    def d_hitBossInsides(self):
        self.sendUpdate('hitBossInsides', [])

    def d_hitToon(self, toonId):
        self.sendUpdate('hitToon', [toonId])

    def setCagedToonNpcId(self, npcId):
        self.cagedToonNpcId = npcId

    def gotToon(self, toon):
        """
        A new Toon has arrived. Put him in the right spot, if we know what that is yet.

        Normally, we will only see this message in the WaitForToons state, or in the Off state if they came in early
        (but someone might arrive to the battle very late and see everything already advanced to the next state).
        """
        stateName = self.state
        self.notify.debug("gotToon(%s) in state %s" % (toon.doId, stateName))

        if stateName == 'Elevator':
            # If the toon arrives late while we're playing the elevator movie, try to pop him into place.

            # Actually, this doesn't work, because we haven't yet received the "setParent" and "setPos" distributed
            # messages, and we're about to.
            # Do something about this later.
            self.placeToonInElevator(toon)

    def setDooberIds(self, dooberIds):
        self.doobers = []
        self.cr.relatedObjectMgr.abortRequest(self.dooberRequest)
        self.dooberRequest = self.cr.relatedObjectMgr.requestObjects(dooberIds, allCallback=self.__gotDoobers)

    def __gotDoobers(self, doobers):
        self.dooberRequest = None
        self.doobers = doobers

    def setBossDamage(self, bossDamage, recoverRate, timestamp):
        recoverStartTime = globalClockDelta.networkToLocalTime(timestamp)
        delta = self.bossDamage - bossDamage
        if delta < 0:
            self.flashRed()
            self.showHpText(delta, scale=5)
        self.bossDamage = bossDamage
        self.healthGui.updateHealth(self.bossMaxDamage - self.bossDamage)
        self.updateHealthBar()

        self.recoverRate = recoverRate
        self.recoverStartTime = recoverStartTime
        taskName = 'RecoverBossDamage'
        taskMgr.remove(taskName)

        if self.bossDamageMovie:
            if self.bossDamage >= self.bossMaxDamage:
                # We did it!  Finish the movie, then transition to NearVictory state.
                self.bossDamageMovie.resumeUntil(self.bossDamageMovie.getDuration())
            else:
                # Push him up to the indicated point and he stops.
                self.bossDamageMovie.resumeUntil(self.bossDamage * self.bossDamageToMovie)

                if self.recoverRate:
                    taskMgr.add(self.__recoverBossDamage, taskName)

        messenger.send(ConditionGlobals.RefreshMsg)

    def updateDamageDealt(self, avId):
        self.healthGui.updateDamageDealt(avId, BossCogGlobals.SellbotBossPieDamage)

    def updateStunCount(self, avId):
        self.healthGui.updateStunCount(avId)

    def getBossDamage(self):
        now = globalClock.getFrameTime()
        elapsed = now - self.recoverStartTime

        # Although the AI side computes and transmits getBossDamage() as an integer value, on the client side we
        # return it as a floating-point value, so we can get the smooth transition effect as the boss slowly starts to
        # roll back up.
        return max(self.bossDamage - self.recoverRate * elapsed / 60.0, 0)

    def __recoverBossDamage(self, task):
        self.bossDamageMovie.setT(self.getBossDamage() * self.bossDamageToMovie)
        return Task.cont

    def __makeCagedToon(self):
        """
        Generates a Toon for putting in the cage during the movies, that we are supposedly rescuing.
        """
        if self.cagedToon:
            return

        self.cagedToon = NPCToons.createLocalNPC(self.cagedToonNpcId)
        self.cagedToon.addActive()
        self.cagedToon.reparentTo(self.cage)
        self.cagedToon.setPosHpr(0, -2, 0, 180, 0, 0)
        self.cagedToon.loop('neutral')
        self.cagedToon.setActiveShadow(0)

        # Also make a polygon to register when we jump up (in battle three) and touch the bottom of the cage.
        touch = CollisionPolygon(
            Point3(-3.0382, 3.0382, -1), Point3(3.0382, 3.0382, -1),
            Point3(3.0382, -3.0382, -1), Point3(-3.0382, -3.0382, -1)
        )
        touch.setTangible(0)
        touchNode = CollisionNode('Cage')
        touchNode.setCollideMask(ToontownGlobals.WallBitmask)
        touchNode.addSolid(touch)
        self.cage.attachNewNode(touchNode)

    def __cleanupCagedToon(self):
        if self.cagedToon:
            self.cagedToon.removeActive()
            self.cagedToon.delete()
            self.cagedToon = None

    def __walkToonToPromotion(self, toonId, delay, mopath, track, delayDeletes):
        """
        Generates an interval to walk the toon along the mopath towards destination (which is the toon's current pos).
        """

        toon = base.cr.doId2do.get(toonId)
        if toon:
            destPos = toon.getPos()

            # Start the toon off at his position within the elevator.
            self.placeToonInElevator(toon)
            toon.wrtReparentTo(render)
            walkMopath = MopathInterval(mopath, toon)

            # We cleverly combine the MopathInterval with a LerpPosInterval so that the toon walks off of his mopath
            # to his final destination, in the last few seconds of the interval.
            # Note that the LerpPos completely replaces the position computed by the Mopath once it kicks in.
            ival = Sequence(
                Wait(delay),
                Func(toon.suit.setPlayRate, 1, 'walk'),
                Func(toon.suit.loop, 'walk'),
                toon.posInterval(1, Point3(0, 90, 20)),
                ParallelEndTogether(walkMopath, toon.posInterval(2, destPos, blendType='noBlend')),
                Func(toon.suit.loop, 'neutral')
            )
            self.toonMopathInterval.append(walkMopath)
            track.append(ival)
            delayDeletes.append(DelayDelete.DelayDelete(toon, 'SellbotBoss.__walkToonToPromotion'))

    def __walkDoober(self, suit, delay, turnPos, track, delayDeletes):
        """
        Generates an interval to walk the doober around the Boss Cog and out to the platform to fly away.
        """
        turnPos = Point3(*turnPos)
        turnPosDown = Point3(*BossCogGlobals.SellbotBossDooberTurnPosDown)
        flyPos = Point3(*BossCogGlobals.SellbotBossDooberFlyPos)

        seq = Sequence(
            Func(suit.headsUp, turnPos),
            Wait(delay),
            Func(suit.loop, 'walk', 0),
            self.__walkSuitToPoint(suit, suit.getPos(), turnPos),
            self.__walkSuitToPoint(suit, turnPos, turnPosDown),
            self.__walkSuitToPoint(suit, turnPosDown, flyPos),
            suit.beginSupaFlyMove(flyPos, 0, 'flyAway'),
            Func(suit.request, 'Off')
        )
        track.append(seq)
        delayDeletes.append(DelayDelete.DelayDelete(suit, 'SellbotBoss.__walkDoober'))

    def __walkSuitToPoint(self, node, fromPos, toPos):
        vector = Vec3(toPos - fromPos)
        distance = vector.length()

        # These suits walk a little faster than most.  (They're still young.)
        time = distance / (ToontownGlobals.SuitWalkSpeed * 1.8)
        return Sequence(Func(node.setPos, fromPos), Func(node.headsUp, toPos), node.posInterval(time, toPos))

    def makeIntroductionMovie(self, delayDeletes):
        """
        Generate an interval which shows the toons emerging from the elevator, walking down to face the Boss Cog, who is
        currently busy promoting a group of new Cogs and sending them on their way.

        The Boss Cog then begins to promote the Toons, but then discovers the dupe and engages them in battle instead.
        """
        track = Parallel()

        # camTrack animates the camera for the first part of the sequence.

        # First, the camera will start off aiming at the elevators, so we'll see the toons emerge and start to split off.
        # Then we'll pull back to look at the room and watch the Boss Cog promote the previous Cogs, while our Toons
        # walk around the perimeter.

        # After that, the camera will be animated by the dialogTrack in cuts synchronized with the boss's dialog.

        camera.reparentTo(render)
        localAvatar.setCameraFov(ToontownGlobals.CogHQCameraFov)

        # dooberTrack includes the doobers walking down the platform and flying away.
        # Instead of adding directly into the movie, we call it with an IndirectInterval, so we can jump around in time.
        dooberTrack = Parallel()
        if self.doobers:
            self.__doobersToPromotionPosition(self.doobers[:4], self.battleANode)
            self.__doobersToPromotionPosition(self.doobers[4:], self.battleBNode)
            turnPosA = BossCogGlobals.SellbotBossDooberTurnPosA
            turnPosB = BossCogGlobals.SellbotBossDooberTurnPosB
            self.__walkDoober(self.doobers[0], 0, turnPosA, dooberTrack, delayDeletes)
            self.__walkDoober(self.doobers[1], 4, turnPosA, dooberTrack, delayDeletes)
            self.__walkDoober(self.doobers[2], 8, turnPosA, dooberTrack, delayDeletes)
            self.__walkDoober(self.doobers[3], 12, turnPosA, dooberTrack, delayDeletes)
            self.__walkDoober(self.doobers[7], 2, turnPosB, dooberTrack, delayDeletes)
            self.__walkDoober(self.doobers[6], 6, turnPosB, dooberTrack, delayDeletes)
            self.__walkDoober(self.doobers[5], 10, turnPosB, dooberTrack, delayDeletes)
            self.__walkDoober(self.doobers[4], 14, turnPosB, dooberTrack, delayDeletes)

        # toonTrack shows the toons walking out of the elevator and down to face the Boss Cog.
        # As above, this is played with an IndirectInterval.
        toonTrack = Parallel()

        # Temporarily put toons in their final position for the movie, just so we can see what it is and lerp them there
        self.__toonsToPromotionPosition(self.toonsA, self.battleANode)
        self.__toonsToPromotionPosition(self.toonsB, self.battleBNode)

        delay = 0
        for toonId in self.toonsA:
            self.__walkToonToPromotion(toonId, delay, self.toonsEnterA, toonTrack, delayDeletes)
            delay += 1

        for toonId in self.toonsB:
            self.__walkToonToPromotion(toonId, delay, self.toonsEnterB, toonTrack, delayDeletes)
            delay += 1

        # And the elevator doors close behind the last toon.
        toonTrack.append(Sequence(Wait(delay), self.closeDoors))

        self.rampA.request('Extended')
        self.rampB.request('Extended')
        self.rampC.request('Retracted')
        self.clearChat()
        self.cagedToon.clearChat()

        # bossTrack shows the Boss's dialog and animations, and the later camera cuts.
        promoteDoobers = TTLocalizer.BossCogPromoteDoobers % SuitDNA.getDeptFullnameP(self.style.dept)
        doobersAway = TTLocalizer.BossCogDoobersAway[self.style.dept]
        welcomeToons = TTLocalizer.BossCogWelcomeToons
        promoteToons = TTLocalizer.BossCogPromoteToons % SuitDNA.getDeptFullnameP(self.style.dept)
        discoverToons = TTLocalizer.BossCogDiscoverToons
        attackToons = TTLocalizer.BossCogAttackToons
        interruptBoss = TTLocalizer.CagedToonInterruptBoss
        rescueQuery = TTLocalizer.CagedToonRescueQuery
        bossAnimTrack = Sequence(
            ActorInterval(self, 'Ff_speech', startTime = 2, duration = 10, loop = 1),
            # 10
            ActorInterval(self, 'ltTurn2Wave', duration = 2),
            # 12
            ActorInterval(self, 'wave', duration = 4, loop = 1),
            # 16
            ActorInterval(self, 'ltTurn2Wave', startTime = 2, endTime = 0),
            # 18
            ActorInterval(self, 'Ff_speech', duration = 7, loop = 1)
            # 25

            # remaining animations mixed in with camera cuts in dialogTrack.
        )
        track.append(bossAnimTrack)
        dialogTrack = Track(
            (0, Parallel(
                camera.posHprInterval(8, Point3(-22, -100, 35), Point3(-10, -13, 0), blendType = 'easeInOut'),
                IndirectInterval(toonTrack, 0, 18)
            )),

            (5.6, Func(self.setChatAbsolute, promoteDoobers, CFSpeech)),

            (9, IndirectInterval(dooberTrack, 0, 9)),

            # Cut to over-the-shoulder shot of Boss Cog waving goodbye to doobers.
            (10, Sequence(
                Func(self.clearChat),
                base.camera.posHprInterval(
                    5, Point3(-23.1, 15.7, 17.2), Point3(-160, -2.4, 0), blendType = 'easeInOut')
            )),

            (12, Func(self.setChatAbsolute, doobersAway, CFSpeech)),

            # Cut to wide shot of Boss Cog and Toons and caged toon in background.
            (16, Parallel(
                Func(self.clearChat),
                base.camera.posHprInterval(3, Point3(-25, -99, 10), Point3(-14, 10, 0), blendType = 'easeInOut'),
                IndirectInterval(dooberTrack, 14),
                IndirectInterval(toonTrack, 30)
            )),

            (18, Func(self.setChatAbsolute, welcomeToons, CFSpeech)),

            (22, Func(self.setChatAbsolute, promoteToons, CFSpeech)),

            (22.2, Sequence(
                Func(self.cagedToon.nametag3d.setScale, 2),
                Func(self.cagedToon.setChatAbsolute, interruptBoss, CFSpeech),
                ActorInterval(self.cagedToon, 'wave'),
                Func(self.cagedToon.loop, 'neutral'))),

            # Cut to head-and-shoulders shot of Boss Cog looking up at source of interruption.
            (25, Sequence(
                Func(self.clearChat),
                Func(self.cagedToon.clearChat),
                ActorInterval(self, 'Ff_lookRt'))),

            # Cut to closeup of caged toon.
            (27, Sequence(
                Func(self.cagedToon.setChatAbsolute, rescueQuery, CFSpeech),
                base.camera.posHprInterval(2, Point3(-12, 48, 94), Point3(-26, 20, 0), blendType = 'easeInOut'),
                ActorInterval(self.cagedToon, 'wave'),
                Func(self.cagedToon.loop, 'neutral')
            )),

            # Cut to shot of Boss Cog looking back at Toons from Toons' eye view.
            (31, Sequence(
                base.camera.posHprInterval(2, Point3(-20, -35, 10), Point3(-88, 25, 0), blendType = 'easeInOut'),
                Func(self.setChatAbsolute, discoverToons, CFSpeech),
                Func(self.cagedToon.nametag3d.setScale, 1),
                Func(self.cagedToon.clearChat),
                ActorInterval(self, 'turn2Fb')
            )),

            # Cut to toons losing their cog suits.
            (34, Sequence(
                Func(self.clearChat),
                self.loseCogSuits(self.toonsA, self.battleANode, (0, 18, 5, -180, 0, 0)),
                self.loseCogSuits(self.toonsB, self.battleBNode, (0, 18, 5, -180, 0, 0))
            )),

            # Cut to wide shot of battle arena. Toons back up and ramps retract.
            (37, Sequence(
                self.toonNormalEyes(self.involvedToons),
                base.camera.posHprInterval(
                    2, Point3(-23.4, -145.6, 44.0), Point3(-10.0, -12.5, 0), blendType = 'easeInOut'
                ),
                Func(self.loop, 'Fb_neutral'),
                Func(self.rampA.request, 'Retract'),
                Func(self.rampB.request, 'Retract'),
                Parallel(
                    self.backupToonsToBattlePosition(self.toonsA, self.battleANode),
                    self.backupToonsToBattlePosition(self.toonsB, self.battleBNode),
                    Sequence(
                        Wait(2),
                        Func(self.setChatAbsolute, attackToons, CFSpeech)
                    )
                )
            )),
        )
        track.append(dialogTrack)
        return Sequence(
            Func(self.stickToonsToFloor), track, Func(self.unstickToons), name=self.uniqueName('Introduction')
        )

    def __makeRollToBattleTwoMovie(self):
        """
        Generate an interval which shows the Boss Cog rolling to the battle 2 position.
        """
        startPos = Point3(
            BossCogGlobals.SellbotBossBattleOnePosHpr[0],
            BossCogGlobals.SellbotBossBattleOnePosHpr[1],
            BossCogGlobals.SellbotBossBattleOnePosHpr[2]
        )
        if self.arenaSide:
            topRampPos = Point3(*BossCogGlobals.SellbotBossTopRampPosB)
            topRampTurnPos = Point3(*BossCogGlobals.SellbotBossTopRampTurnPosB)
            p3Pos = Point3(*BossCogGlobals.SellbotBossP3PosB)
        else:
            topRampPos = Point3(*BossCogGlobals.SellbotBossTopRampPosA)
            topRampTurnPos = Point3(*BossCogGlobals.SellbotBossTopRampTurnPosA)
            p3Pos = Point3(*BossCogGlobals.SellbotBossP3PosA)

        battlePos = Point3(
            BossCogGlobals.SellbotBossBattleTwoPosHpr[0],
            BossCogGlobals.SellbotBossBattleTwoPosHpr[1],
            BossCogGlobals.SellbotBossBattleTwoPosHpr[2]
        )
        # battleHpr = VBase3(BossCogGlobals.SellbotBossBattleTwoPosHpr[3], ToontownGlobals.SellbotBossBattleTwoPosHpr[4], ToontownGlobals.SellbotBossBattleTwoPosHpr[5])
        bossTrack = Sequence()

        # Turn the boss model around so he rolls forward.
        bossTrack.append(Func(self.getGeomNode().setH, 180))
        bossTrack.append(Func(self.loop, 'Fb_neutral'))

        track, hpr = self.rollBossToPoint(startPos, None, topRampPos, None, 0)
        bossTrack.append(track)
        track, hpr = self.rollBossToPoint(topRampPos, hpr, topRampTurnPos, None, 0)
        bossTrack.append(track)
        track, hpr = self.rollBossToPoint(topRampTurnPos, hpr, p3Pos, None, 0)
        bossTrack.append(track)
        track, hpr = self.rollBossToPoint(p3Pos, hpr, battlePos, None, 0)
        bossTrack.append(track)

        return Sequence(
            bossTrack,
            Func(self.getGeomNode().setH, 0), name=self.uniqueName('BattleTwo')
        )

    def cagedToonMovieFunction(self, instruct, cageIndex):
        self.notify.debug('cagedToonMovieFunction()')
        if not (hasattr(self, 'cagedToon') and hasattr(self.cagedToon, 'nametag') and hasattr(self.cagedToon, 'nametag3d')):
            return
        if instruct == 1:
            self.cagedToon.nametag3d.setScale(2)
        elif instruct == 2:
            self.cagedToon.setChatAbsolute(TTLocalizer.CagedToonDrop[cageIndex], CFSpeech)
        elif instruct == 3:
            self.cagedToon.nametag3d.setScale(1)
        elif instruct == 4:
            self.cagedToon.clearChat()

    def makeEndOfBattleMovie(self, hasLocalToon):
        """
        Generate an interval which shows the cage dropping a bit further.
        This one is called from DistributedBattleFinal.
        """
        self.notify.debug("makeEndOfBattleMovie(%s)" % (hasLocalToon))

        name = self.uniqueName('CageDrop')
        seq = Sequence(name=name)
        seq.append(Func(self.cage.setPos, self.cagePos[self.cageIndex]))
        if hasLocalToon:
            seq += [Func(camera.wrtReparentTo, render),
             base.camera.posHprInterval(1, Point3(0, -50, 0), Point3(0, 0, 0), blendType = 'easeInOut', other = self.cage),
             Func(localAvatar.setCameraFov, ToontownGlobals.CogHQCameraFov),
             Func(self.hide)]

        seq += [
            Wait(0.5),
            Parallel(
                self.cage.posInterval(1, self.cagePos[self.cageIndex + 1], blendType = 'easeInOut'),
                SoundInterval(self.cageLowerSfx, duration = 1)
            ),
            Func(self.cagedToonMovieFunction, 1, self.cageIndex),
            Func(self.cagedToonMovieFunction, 2, self.cageIndex),
            Wait(3),
            Func(self.cagedToonMovieFunction, 3, self.cageIndex),
            Func(self.cagedToonMovieFunction, 4, self.cageIndex)]

        if hasLocalToon:
            seq += [
                Func(self.show),
                Func(camera.wrtReparentTo, localAvatar),
                base.camera.posHprInterval(
                    1,
                    Point3(
                        0.0,
                        -9.0 * base.localAvatar.getClampedAvatarHeight() * 0.3333333333,
                        base.localAvatar.getClampedAvatarHeight()
                    ),
                    Point3(0, 0, 0),
                    blendType = 'easeInOut'
                )
            ]
        self.cageIndex += 1
        return seq

    def __makeBossDamageMovie(self):
        startPos = Point3(
            BossCogGlobals.SellbotBossBattleTwoPosHpr[0],
            BossCogGlobals.SellbotBossBattleTwoPosHpr[1],
            BossCogGlobals.SellbotBossBattleTwoPosHpr[2]
        )
        startHpr = Point3(*BossCogGlobals.SellbotBossBattleThreeHpr)
        bottomPos = Point3(*BossCogGlobals.SellbotBossBottomPos)
        deathPos = Point3(*BossCogGlobals.SellbotBossDeathPos)
        self.setPosHpr(startPos, startHpr)
        bossTrack = Sequence()
        bossTrack.append(Func(self.loop, 'Fb_neutral'))
        track, hpr = self.rollBossToPoint(startPos, startHpr, bottomPos, None, 1)
        bossTrack.append(track)
        track, hpr = self.rollBossToPoint(bottomPos, startHpr, deathPos, None, 1)
        bossTrack.append(track)
        # duration = bossTrack.getDuration()
        return bossTrack

    def __talkAboutPromotion(self, speech):
        speech = self.handleUniteSpeech(speech)
        if not self.localToonPromoted:
            pass
        elif (self.prevCogSuitLevel < ToontownGlobals.MaxCogSuitLevel) or (self.prevCogSuitReviveLevel > -1 and self.prevCogSuitLevel < 49):
            newCogSuitLevel = localAvatar.getCogLevels()[CogDisguiseGlobals.dept2deptIndex(self.style.dept)]
            newCogSuitReviveLevel = localAvatar.getCogReviveLevels()[CogDisguiseGlobals.dept2deptIndex(self.style.dept)]
            newCogSuitType = localAvatar.getCogTypes()[CogDisguiseGlobals.dept2deptIndex(self.style.dept)]
            if newCogSuitLevel == ToontownGlobals.MaxCogSuitLevel:
                speech += TTLocalizer.CagedToonLastPromotion % (ToontownGlobals.MaxCogSuitLevel + 1)
            if newCogSuitReviveLevel == ToontownGlobals.MaxCogSuitLevel:
                speech += TTLocalizer.CagedToonLastRevivePromotion % (ToontownGlobals.MaxCogSuitLevel + 1)
            if newCogSuitLevel in ToontownGlobals.CogSuitHPLevels and newCogSuitLevel != self.prevCogSuitLevel and newCogSuitType != 6:
                speech += TTLocalizer.CagedToonHPBoost
            if newCogSuitReviveLevel in ToontownGlobals.CogReviveSuitHPLevels and newCogSuitReviveLevel != self.prevCogSuitReviveLevel:
                speech += TTLocalizer.CagedToonHPBoost
            if self.prevCogSuitType != 4 and newCogSuitType == 4:
                speech += TTLocalizer.CagedToonTeleportAccess
        else:
            speech += TTLocalizer.CagedToonMaxed % (ToontownGlobals.MaxCogSuitLevel + 1)

        return speech

    def __makeCageOpenMovie(self):
        # NOTE: TEMPORARY; Using chat to list the obtained NPC's, until I fix the GUI issue I'm currently having (at
        #       time of writing, that would be nametag issues)
        rewardsList = []    # create a list of unique npc IDs from self.rewards (which *may contain* dupe IDs)
        for iouId in self.rewards:
            # Skip Rain, they're always here
            if iouId == IOUItemType.AllBoost:
                continue
            iou = IOURegistry[iouId]
            if iou.getNpcId() not in rewardsList:
                rewardsList.append(iou.getNpcId())
        if len(rewardsList) == 1:
            speech = TTLocalizer.CagedToonThankYouTemp['one'].format(npc=NPCToons.getNPCName(rewardsList[0]))
        else:
            npcFirst = ""
            npcLast = ""
            for idx, npcId in enumerate(rewardsList):
                if idx == 0:
                    npcFirst = NPCToons.getNPCName(npcId)
                elif idx + 1 == len(rewardsList):
                    npcLast = NPCToons.getNPCName(npcId)
                else:
                    npcFirst += f", {NPCToons.getNPCName(npcId)}"
            speech = TTLocalizer.CagedToonThankYouTemp['many'].format(npcFirst=npcFirst, npcLast=npcLast)
        # speech = TTLocalizer.CagedToonThankYou
        speech = self.__talkAboutPromotion(speech)
        name = self.uniqueName('CageOpen')
        seq = Sequence(
            Func(self.cage.setPos, self.cagePos[4]),
            Func(self.cageDoor.setHpr, VBase3(0, 0, 0)),
            Func(self.cagedToon.setPos, Point3(0, -2, 0)),
            Parallel(
                self.cage.posInterval(0.5, self.cagePos[5], blendType = 'easeOut'),
                SoundInterval(self.cageLowerSfx, duration = 0.5)),
            Parallel(
                self.cageDoor.hprInterval(0.5, VBase3(0, 90, 0), blendType = 'easeOut'),
                Sequence(
                    SoundInterval(self.cageDoorSfx),
                    duration = 0
                )
            ),
            Wait(0.2),
            Func(self.cagedToon.loop, 'walk'),
            self.cagedToon.posInterval(0.8, Point3(0, -6, 0)),
            Func(self.cagedToon.setChatAbsolute, TTLocalizer.CagedToonYippee % localAvatar.getName(), CFSpeech),
            ActorInterval(self.cagedToon, 'jump'),
            Func(self.cagedToon.loop, 'neutral'),
            Func(self.cagedToon.headsUp, localAvatar),
            Func(self.cagedToon.setLocalPageChat, speech, 0),
            Func(camera.reparentTo, localAvatar),
            Func(camera.setPos, 0, -9, 9),
            Func(camera.lookAt, self.cagedToon, Point3(0, 0, 2)),
            name = name
        )
        return seq

    def __showOnscreenMessage(self, text):
        if self.onscreenMessage:
            self.onscreenMessage.destroy()
            self.onscreenMessage = None
        self.onscreenMessage = DirectLabel(
            text=text,
            text_fg=VBase4(1, 1, 1, 1),
            text_align=TextNode.ACenter,
            relief=None,
            pos=(0, 0, 0.35),
            scale=0.1
        )

    def __clearOnscreenMessage(self):
        if self.onscreenMessage:
            self.onscreenMessage.destroy()
            self.onscreenMessage = None

    def __showWaitingMessage(self, task):
        self.__showOnscreenMessage(TTLocalizer.BuildingWaitingForVictors)

    def __placeCageShadow(self):
        if self.cageShadow is None:
            self.cageShadow = loader.loadModel('phase_3/models/props/drop_shadow')
            self.cageShadow.setPos(0, 77.9, 18)
            self.cageShadow.setColorScale(1, 1, 1, 0.6)
        self.cageShadow.reparentTo(render)

    def __removeCageShadow(self):
        if self.cageShadow is not None:
            self.cageShadow.detachNode()

    def setCageIndex(self, cageIndex):
        self.cageIndex = cageIndex
        self.cage.setPos(self.cagePos[self.cageIndex])
        if self.cageIndex >= 4:
            self.__placeCageShadow()
        else:
            self.__removeCageShadow()

    def loadEnvironment(self):
        DistributedBossCog.DistributedBossCog.loadEnvironment(self)
        self.geom = loader.loadModel('phase_9/models/cogHQ/BossRoomHQ')
        self.rampA = self.__findRamp('rampA', '**/west_ramp')
        self.rampB = self.__findRamp('rampB', '**/east_ramp')
        self.rampC = self.__findRamp('rampC', '**/north_ramp')
        self.ramps = (self.rampA, self.rampB, self.rampC)
        self.cage = self.geom.find('**/cage')

        # Configure for elevator placement
        elevatorEntrance = self.geom.find('**/elevator_locator')
        elevatorEntrance.setZ(elevatorEntrance.getZ() + 0.04)  # hack
        elevatorModel = loader.loadModel('phase_9/models/cogHQ/cogHQ_elevator')
        elevatorModel.reparentTo(elevatorEntrance)
        elevatorModel.find("**/frame").hide()
        elevatorModel.find("**/flashing").hide()
        elevatorModel.find("**/corners").hide()
        self.setupElevator(elevatorModel)

        pos = self.cage.getPos()
        self.cagePos = []
        for height in self.cageHeights:
            self.cagePos.append(Point3(pos[0], pos[1], height))

        # Make the cage be scale 1.0, to fit the Toon inside better.
        self.cageDoor = self.geom.find('**/cage_door')
        self.cage.setScale(1)

        # Draw a chain from the top of the cage support to the bottom of the I-beam.
        self.rope = Rope.Rope(name='supportChain')
        self.rope.reparentTo(self.cage)
        self.rope.setup(
            2,
            ((self.cage, (0.15, 0.13, 16)),
             (self.geom, (0.23, 78, 120)))
        )
        self.rope.ropeNode.setRenderMode(RopeNode.RMBillboard)
        self.rope.ropeNode.setUvMode(RopeNode.UVDistance)
        self.rope.ropeNode.setUvDirection(0)
        self.rope.ropeNode.setUvScale(0.8)
        self.rope.setTexture(self.cage.findTexture('ttcc_sellbotHQ_boss_chain'))
        self.rope.setTransparency(1)

        self.elevatorMusic = 'vp_elevator'
        self.stingMusic = 'vp_cage_toon_skelecogs'
        self.battleOneMusic = 'vp_battle_one'
        self.battleTwoMusic = 'vp_battle_two'
        self.battleThreeMusic = 'vp_battle_three'
        self.battleThreeDizzyMusic = 'vp_battle_three_stunned'
        self.killMusic = 'vp_battle_stinger'
        self.victoryMusic = 'vp_victory'
        self.epilogueMusic = 'vp_epilogue'
        self.promotionMusic = 'vp_intro_cutscene'
        self.fleeingBattleOneMusic = 'vp_flee_cutscene'
        self.battleThreePrepMusic = 'vp_cage_toon_final'
        self.victoryAndBattleThreeMatch = base.musicMgr.getMusicFilepath(self.victoryMusic) == base.musicMgr.getMusicFilepath(self.battleThreeMusic)
        self.preloadFinalBattleMusic()

        self.geom.reparentTo(render)
        # Start Fog
        self.fogList[0].attachFog([self.geom.find("**/tower_top"), self.geom.find("**/cage")])
        self.fogList[1].attachFog([base.cr.playGame.hood.sky])
        self.fogList[2].attachFog([self.geom.find("**/tower_body")])

    def unloadEnvironment(self):
        DistributedBossCog.DistributedBossCog.unloadEnvironment(self)
        for fogNode in self.fogList:
            fogNode.removeFog()
        del self.fogList

        self.geom.removeNode()
        del self.geom
        del self.cage
        for ramp in self.ramps:
            ramp.cleanup()
        del self.ramps
        del self.rampA
        del self.rampB
        del self.rampC

    def __loadMopaths(self):
        self.toonsEnterA = Mopath.Mopath()
        self.toonsEnterA.loadFile('phase_9/paths/bossBattle-toonsEnterA')
        self.toonsEnterA.fFaceForward = 1
        self.toonsEnterA.timeScale = 35
        self.toonsEnterB = Mopath.Mopath()
        self.toonsEnterB.loadFile('phase_9/paths/bossBattle-toonsEnterB')
        self.toonsEnterB.fFaceForward = 1
        self.toonsEnterB.timeScale = 35

    def __unloadMopaths(self):
        self.toonsEnterA.reset()
        self.toonsEnterB.reset()

    def __findRamp(self, name, path):
        """
        Find the ramp in the geom and sets it up for animation.
        """
        ramp = self.geom.find(path)

        # The transform on the ramp node represents the coordinate system in which the ramp can move.
        # That means we need to animate a child of the ramp node itself in order to remain within this coordinate system
        # Since there are multiple children (visible polygons + coll. nodes), we create our own node for this purpose.
        children = ramp.getChildren()
        animate = ramp.attachNewNode(name)
        children.reparentTo(animate)
        return HQRamp(name, animate)

    @property
    def dizzyMusic(self):
        return self.battleThreeDizzyMusic

    @property
    def unDizzyMusic(self):
        return self.battleThreeMusic

    ##### Off state #####

    def enterOff(self):
        DistributedBossCog.DistributedBossCog.enterOff(self)
        if self.cagedToon:
            self.cagedToon.clearChat()
        for ramp in self.ramps:
            ramp.request("Off")

    ##### WaitForToons state #####

    def enterWaitForToons(self):
        DistributedBossCog.DistributedBossCog.enterWaitForToons(self)
        self.geom.hide()
        # Disable the caged toon's nametag while we're here in space waiting.
        self.cagedToon.removeActive()

    def exitWaitForToons(self):
        DistributedBossCog.DistributedBossCog.exitWaitForToons(self)
        self.geom.show()
        self.cagedToon.addActive()

    ##### Elevator state #####

    def enterElevator(self):
        base.discord.applyPreset('boss-s-1')
        DistributedBossCog.DistributedBossCog.enterElevator(self)
        # Make sure the side ramps are extended and the back ramp is retracted.
        self.rampA.request('Extended')
        self.rampB.request('Extended')
        self.rampC.request('Retracted')

        # And the cage is up in the original position.
        self.setCageIndex(0)

        # Set the boss up in the middle of the floor, so we can see him when the doors open.
        self.reparentTo(render)
        self.setPosHpr(*BossCogGlobals.SellbotBossBattleOnePosHpr)

        self.happy = 1
        self.raised = 1
        self.forward = 1
        self.doAnimate()

        # Disable the caged toon's nametag while we're in the elevator.
        self.cagedToon.removeActive()
        base.camLens.setMinFov(ToontownGlobals.VPElevatorFov/(4./3.))

    def exitElevator(self):
        DistributedBossCog.DistributedBossCog.exitElevator(self)
        self.cagedToon.addActive()

    ##### Introduction state #####

    def enterIntroduction(self):
        # Set the boss up in the middle of the floor, actively promoting some doobers.
        self.reparentTo(render)
        self.setPosHpr(*BossCogGlobals.SellbotBossBattleOnePosHpr)
        self.stopAnimate()

        DistributedBossCog.DistributedBossCog.enterIntroduction(self)

        # Make sure the side ramps are extended and the back ramp is retracted.
        self.rampA.request('Extended')
        self.rampB.request('Extended')
        self.rampC.request('Retracted')

        # And the cage is up in the original position.
        self.setCageIndex(0)
        base.musicMgr.playMusic(self.promotionMusic, looping=1, volume=0.9)
        self.acceptOnce('skipCutscene', self.__beginBattleOne)

    def exitIntroduction(self):
        self.ignore('skipCutscene')
        DistributedBossCog.DistributedBossCog.exitIntroduction(self)
        base.musicMgr.stopMusic(self.promotionMusic)

    ##### BattleOne state #####

    def __beginBattleOne(self):
        intervalName = 'IntroductionMovie'
        self.clearInterval(intervalName)
        self.doneBarrier('Introduction')

    def exitIntroduction(self):
        self.ignore('skipCutscene')
        DistributedBossCog.DistributedBossCog.exitIntroduction(self)

    def enterBattleOne(self):
        base.discord.applyPreset('boss-s-2')

        # Boss Cog is still in the middle of the floor.
        DistributedBossCog.DistributedBossCog.enterBattleOne(self)
        self.reparentTo(render)
        self.setPosHpr(*BossCogGlobals.SellbotBossBattleOnePosHpr)
        self.clearChat()
        self.cagedToon.clearChat()
        if self.battleA is None or self.battleB is None:
            cageIndex = 1
        else:
            cageIndex = 0
        self.setCageIndex(cageIndex)

    def exitBattleOne(self):
        DistributedBossCog.DistributedBossCog.exitBattleOne(self)

    ##### RollToBattleTwo state #####

    def enterRollToBattleTwo(self):
        base.discord.applyPreset('boss-s-3')
        # Disable collision on the toon, there is a collision issue where the boss was
        # hitting the toons right after the first battle, so we turn off their collision briefly
        # until this issue can be addressed in Panda.
        self.disableToonCollision()
        self.releaseToons()

        # Retract most of the ramps.
        if self.arenaSide:
            self.rampA.request('Retract')
            self.rampB.request('Extend')
        else:
            self.rampA.request('Extend')
            self.rampB.request('Retract')
        self.reparentTo(render)

        # By now, the cage has dropped somewhat.
        self.setCageIndex(2)

        # The Boss Cog rolls up the ramp into position for battle two,
        # while the Toons are free to run around for a few seconds.
        self.stickBossToFloor()

        # Now generate the interval that plays the movie.
        intervalName = 'RollToBattleTwo'
        seq = Sequence(
            self.__makeRollToBattleTwoMovie(),
            Func(self.__onToPrepareBattleTwo),
            name = intervalName
        )
        seq.start()
        self.storeInterval(seq, intervalName)

        base.musicMgr.playMusic(self.fleeingBattleOneMusic, looping = 1, volume = 0.9)

        # re-enable the collision a little bit later, after the boss has started moving
        taskMgr.doMethodLater(0.5, self.enableToonCollision, 'enableToonCollision')
        self.acceptOnce('skipCutscene', self.__onToPrepareBattleTwoSkip)

    def __onToPrepareBattleTwoSkip(self):
        self.skipClickDialogue = True
        self.__onToPrepareBattleTwo()

    def __onToPrepareBattleTwo(self):
        # Make sure the boss ends up in his battle position.
        self.disableToonCollision()
        self.unstickBoss()
        self.setPosHpr(*BossCogGlobals.SellbotBossBattleTwoPosHpr)
        self.doneBarrier('RollToBattleTwo')

    def exitRollToBattleTwo(self):
        self.ignore('skipCutscene')
        self.unstickBoss()
        intervalName = 'RollToBattleTwo'
        self.clearInterval(intervalName)

    def disableToonCollision(self):
        base.localAvatar.collisionsOff()

    def enableToonCollision(self, task):
        base.localAvatar.collisionsOn()

    ##### PrepareBattleTwo state #####

    def enterPrepareBattleTwo(self):
        self.cleanupIntervals()
        self.controlToons()
        self.clearChat()
        self.cagedToon.clearChat()
        self.reparentTo(render)
        if self.arenaSide:
            self.rampA.request('Retract')
            self.rampB.request('Extend')
        else:
            self.rampA.request('Extend')
            self.rampB.request('Retract')
        self.reparentTo(render)
        self.setCageIndex(2)
        if not self.skipClickDialogue:
            camera.reparentTo(render)
            camera.setPosHpr(self.cage, 0, -17, 3.3, 0, 0, 0)
            (localAvatar.setCameraFov(ToontownGlobals.CogHQCameraFov),)
            self.hide()
            self.acceptOnce('doneChatPage', self.__onToBattleTwo)
            self.cagedToon.setLocalPageChat(TTLocalizer.CagedToonPrepareBattleTwo, 1)
            base.musicMgr.playMusic(self.stingMusic, looping=1, volume=1.0)
            taskMgr.doMethodLater(0.5, self.enableToonCollision, 'enableToonCollision')
        else:
            self.skipClickDialogue = False
            taskMgr.doMethodLater(0.5, self.enableToonCollision, 'enableToonCollision')
            self.doneBarrier('PrepareBattleTwo')

    def __onToBattleTwo(self, elapsed):
        self.doneBarrier('PrepareBattleTwo')
        taskMgr.doMethodLater(1, self.__showWaitingMessage, self.uniqueName('WaitingMessage'))

    def exitPrepareBattleTwo(self):
        self.show()
        taskMgr.remove(self.uniqueName('WaitingMessage'))
        self.ignore('doneChatPage')
        self.__clearOnscreenMessage()

    def enterBattleTwo(self):
        base.discord.applyPreset('boss-s-4')
        DistributedBossCog.DistributedBossCog.enterBattleTwo(self)
        # self.setBattleCreditMult()
        # self.cleanupIntervals()
        self.reparentTo(render)
        self.setPosHpr(*BossCogGlobals.SellbotBossBattleTwoPosHpr)
        self.clearChat()
        self.cagedToon.clearChat()
        for ramp in self.ramps:
            if ramp.getCurrentOrNextState() in ("Off", "Extend", "Extended"):
                ramp.request("Retract")
        self.releaseToons()
        self.toonsToBattlePosition(self.toonsA, self.battleANode)
        self.toonsToBattlePosition(self.toonsB, self.battleBNode)
        if self.battleA is None or self.battleB is None:
            cageIndex = 3
        else:
            cageIndex = 2
        self.setCageIndex(cageIndex)

    def exitBattleTwo(self):
        intervalName = self.uniqueName('cageDrop')
        self.clearInterval(intervalName)
        DistributedBossCog.DistributedBossCog.exitBattleTwo(self)
        # self.cleanupBattles()
        # localAvatar.inventory.setBattleCreditMult(1)

    def enterPrepareBattleThree(self):
        self.cleanupIntervals()
        self.controlToons()
        self.clearChat()
        self.cagedToon.clearChat()
        self.reparentTo(render)
        self.rampA.request('Retract')
        self.rampB.request('Retract')
        self.rampC.request('Extend')
        self.setCageIndex(4)
        camera.reparentTo(render)
        camera.setPosHpr(self.cage, 0, -17, 3.3, 0, 0, 0)
        (localAvatar.setCameraFov(ToontownGlobals.CogHQCameraFov),)
        self.hide()
        self.acceptOnce('doneChatPage', self.__onToBattleThree)
        self.cagedToon.setLocalPageChat(TTLocalizer.CagedToonPrepareBattleThree % base.PRIMARY_KEY.upper(), 1)
        base.musicMgr.playMusic(self.battleThreePrepMusic, looping=1, volume=0.9)

    def __onToBattleThree(self, elapsed):
        self.doneBarrier('PrepareBattleThree')
        taskMgr.doMethodLater(1, self.__showWaitingMessage, self.uniqueName('WaitingMessage'))

    def exitPrepareBattleThree(self):
        self.show()
        taskMgr.remove(self.uniqueName('WaitingMessage'))
        self.ignore('doneChatPage')
        intervalName = 'PrepareBattleThree'
        self.clearInterval(intervalName)
        self.__clearOnscreenMessage()

    def enterBattleThree(self):
        base.discord.applyPreset('boss-s-5')
        DistributedBossCog.DistributedBossCog.enterBattleThree(self)
        self.clearChat()
        self.cagedToon.clearChat()
        self.reparentTo(render)
        self.rampA.request('Retract')
        self.rampB.request('Retract')
        self.rampC.request('Extend')
        self.setCageIndex(4)
        self.happy = 0
        self.raised = 1
        self.forward = 1
        self.doAnimate()
        self.accept('enterCage', self.__touchedCage)
        self.accept('pieSplat', self.__pieSplat)
        self.accept('localPieSplat', self.__localPieSplat)
        self.accept('outOfPies', self.__outOfPies)
        self.accept('begin-pie', self.__foundPieButton)
        localAvatar.setCameraFov(ToontownGlobals.BossBattleCameraFov)
        taskMgr.doMethodLater(30, self.__howToGetPies, self.uniqueName('PieAdvice'))
        self.stickBossToFloor()
        self.doorA.request('close')
        self.doorB.request('close')
        self.bossDamageMovie = self.__makeBossDamageMovie()
        bossDoneEventName = self.uniqueName('DestroyedBoss')
        self.bossDamageMovie.setDoneEvent(bossDoneEventName)
        self.acceptOnce(bossDoneEventName, self.__doneBattleThree)
        self.resetMaxDamage()
        self.healthGui.createBossCogHead()
        self.healthGui.moveInInitial()
        self.bossDamageToMovie = self.bossDamageMovie.getDuration() / self.bossMaxDamage
        self.bossDamageMovie.setT(self.bossDamage * self.bossDamageToMovie)
        self.generateHealthBar()
        base.musicMgr.playMusic(self.battleThreeMusic, looping=1, volume=0.9)

        base.cr.gameGui.expBar.hide()
        self.departmentExpBar = DepartmentExperienceBar.DepartmentExperienceBar(
            base.localAvatar.departmentExp[ToontownGlobals.DEPARTMENT_SELLBOT],
            base.localAvatar.departmentLevels[ToontownGlobals.DEPARTMENT_SELLBOT],
            ToontownGlobals.DEPARTMENT_SELLBOT,
            base.localAvatar.style
        )
        self.departmentExpBar.setAvatar(base.localAvatar)
        self.departmentExpBar.setScale(0.075)
        self.departmentExpBar.reparentTo(base.a2dBottomLeft)
        self.departmentExpBar.start()

        # Tell condition manager to pull up dept bars/pie count
        stateArgs = ConditionGlobals.ConditionStateArgs()
        stateArgs[ConditionGlobals.ConditionStateArg.BOSS] = self
        messenger.send(ConditionGlobals.SetStateMsg, [ConditionGlobals.ConditionState.BOSS_VP, stateArgs])

    def __doneBattleThree(self):
        self.setState('NearVictory')
        self.unstickBoss()

    def exitBattleThree(self):
        DistributedBossCog.DistributedBossCog.exitBattleThree(self)
        bossDoneEventName = self.uniqueName('DestroyedBoss')
        self.ignore(bossDoneEventName)
        taskMgr.remove(self.uniqueName('StandUp'))
        self.ignore('enterCage')
        self.ignore('pieSplat')
        self.ignore('localPieSplat')
        self.ignore('outOfPies')
        self.ignore('begin-pie')
        self.__clearOnscreenMessage()
        taskMgr.remove(self.uniqueName('PieAdvice'))
        localAvatar.setCameraFov(ToontownGlobals.CogHQCameraFov)
        self.__removeCageShadow()
        self.bossDamageMovie.finish()
        self.bossDamageMovie = None
        self.unstickBoss()
        taskName = 'RecoverBossDamage'
        taskMgr.remove(taskName)
        self.battleThreeMusicTime = base.musicMgr.getMusicTime(self.battleThreeMusic)

    def toonDied(self, avId):
        DistributedBossCog.DistributedBossCog.toonDied(self, avId)

        # If our toon died, get rid of the dept exp bar
        if avId == base.localAvatar.doId:
            if self.departmentExpBar:
                self.departmentExpBar.hide()
                self.departmentExpBar.stop()
                self.departmentExpBar.destroy()
            base.cr.gameGui.expBar.show()

    def enterNearVictory(self):
        self.cleanupIntervals()
        self.reparentTo(render)
        self.setPos(*BossCogGlobals.SellbotBossDeathPos)
        self.setHpr(*BossCogGlobals.SellbotBossBattleThreeHpr)
        self.clearChat()
        self.cagedToon.clearChat()
        self.setCageIndex(4)
        self.releaseToons(finalBattle=1)
        self.rampA.request('Retract')
        self.rampB.request('Retract')
        self.rampC.request('Extend')
        self.accept('enterCage', self.__touchedCage)
        self.accept('pieSplat', self.__finalPieSplat)
        self.accept('localPieSplat', self.__localPieSplat)
        self.accept('outOfPies', self.__outOfPies)
        localAvatar.setCameraFov(ToontownGlobals.BossBattleCameraFov)
        self.happy = 0
        self.raised = 0
        self.forward = 1
        self.doAnimate()
        self.setDizzy(1)
        base.musicMgr.playMusic(self.battleThreeMusic, looping=1, volume=0.9, time=self.battleThreeMusicTime)

    def exitNearVictory(self):
        self.ignore('enterCage')
        self.ignore('pieSplat')
        self.ignore('localPieSplat')
        self.ignore('outOfPies')
        self.__clearOnscreenMessage()
        taskMgr.remove(self.uniqueName('PieAdvice'))
        localAvatar.setCameraFov(ToontownGlobals.CogHQCameraFov)
        self.__removeCageShadow()
        self.setDizzy(0)
        self.battleThreeMusicTime = base.musicMgr.getMusicTime(self.battleThreeMusic)

    def enterVictory(self):
        self.cleanupIntervals()
        localAvatar.setCameraFov(ToontownGlobals.BossBattleCameraFov)
        self.reparentTo(render)
        self.setPos(*BossCogGlobals.SellbotBossDeathPos)
        self.setHpr(*BossCogGlobals.SellbotBossBattleThreeHpr)
        self.clearChat()
        self.cagedToon.clearChat()
        self.setCageIndex(4)
        self.releaseToons(finalBattle=1)
        self.rampA.request('Retract')
        self.rampB.request('Retract')
        self.rampC.request('Extend')
        self.happy = 0
        self.raised = 0
        self.forward = 1
        self.doAnimate('Fb_fall', now=1)
        self.acceptOnce(self.animDoneEvent, self.__continueVictory)
        base.musicMgr.playMusic(self.killMusic, looping=1, volume=0.9)
        if self.departmentExpBar:
            self.departmentExpBar.hide()
            self.departmentExpBar.stop()
            self.departmentExpBar.destroy()
        base.cr.gameGui.expBar.show()

    def __continueVictory(self):
        self.stopAnimate()
        self.stash()
        if self.healthGui:
            self.healthGui.moveOutEnd()
        self.doneBarrier('Victory')

    def exitVictory(self):
        self.stopAnimate()
        self.unstash()
        self.__removeCageShadow()
        localAvatar.setCameraFov(settings['fieldofview'] + 8)
        if self.victoryAndBattleThreeMatch:
            self.battleThreeMusicTime = base.musicMgr.getMusicTime(self.battleThreeMusic)
        else:
            self.battleThreeMusicTime = 0

    def enterReward(self):
        self.cleanupIntervals()
        self.clearChat()
        self.cagedToon.clearChat()
        self.stash()
        self.stopAnimate()
        self.setCageIndex(4)
        self.releaseToons(finalBattle=1)
        self.toMovieMode()
        self.rampA.request('Retract')
        self.rampB.request('Retract')
        self.rampC.request('Extend')
        panelName = self.uniqueName('reward')
        self.rewardPanel = RewardPanel.RewardPanel(panelName)
        victory, camVictory, skipper = MovieToonVictory.doToonVictory(
            1, self.involvedToons, self.toonRewardIds, self.toonRewardDicts,
            self.rewardPanel, 0, self.updatedQuests, noSkip=True
        )
        ival = Sequence(Parallel(victory, camVictory), Func(self.__doneReward))
        intervalName = 'RewardMovie'
        delayDeletes = []
        for toonId in self.involvedToons:
            toon = self.cr.doId2do.get(toonId)
            if toon:
                delayDeletes.append(DelayDelete.DelayDelete(toon, 'SellbotBoss.enterReward'))
                toon.setGeomNodeH(0)

        ival.delayDeletes = delayDeletes
        ival.start()
        self.storeInterval(ival, intervalName)
        if self.victoryAndBattleThreeMatch:
            base.musicMgr.playMusic(self.battleThreeMusic, looping=1, volume=0.9, time=self.battleThreeMusicTime)
        else:
            base.musicMgr.playMusic(self.victoryMusic, looping=1, volume=0.9)

        # Have condition manager go back to normal
        messenger.send(ConditionGlobals.SetStateMsg, [ConditionGlobals.ConditionState.GLOBAL])

    def __doneReward(self):
        self.doneBarrier('Reward')
        self.toWalkMode()

    def exitReward(self):
        intervalName = 'RewardMovie'
        self.clearInterval(intervalName)
        self.unstash()
        self.rewardPanel.destroy()
        del self.rewardPanel
        self.__removeCageShadow()
        self.battleThreeMusicTime = 0
        base.musicMgr.stopMusic()

    def setRewards(self, rewards):
        self.rewards = rewards

    def enterEpilogue(self):
        self.cleanupIntervals()
        self.clearChat()
        self.cagedToon.clearChat()
        self.stash()
        self.stopAnimate()
        self.setCageIndex(4)
        self.controlToons()
        self.rampA.request('Retract')
        self.rampB.request('Retract')
        self.rampC.request('Extend')
        self.__arrangeToonsAroundCage()
        self.hideToonsMeters()
        base.camera.wrtReparentTo(render)
        base.camera.posHprInterval(1, Point3(-25, 52, 27.5), Point3(-53, -13, 0), blendType = 'easeInOut').start()
        intervalName = 'EpilogueMovie'
        seq = Sequence(self.__makeCageOpenMovie(), name=intervalName)
        seq.start()
        self.storeInterval(seq, intervalName)
        self.accept('nextChatPage', self.__epilogueChatNext)
        self.accept('doneChatPage', self.__epilogueChatDone)
        base.musicMgr.playMusic(self.epilogueMusic, looping=1, volume=0.9)

    def __epilogueChatNext(self, pageNumber, elapsed):
        if pageNumber == 2:
            if self.cagedToon.style.torso[1] == 'd':
                track = ActorInterval(self.cagedToon, 'curtsy')
            else:
                track = ActorInterval(self.cagedToon, 'bow')
            track = Sequence(track, Func(self.cagedToon.loop, 'neutral'))
            intervalName = 'EpilogueMovieToonAnim'
            self.storeInterval(track, intervalName)
            track.start()
        elif pageNumber == self.localUniteEffectPageNumber:
            self.handleLocalUniteEffect()

    def __epilogueChatDone(self, elapsed):
        self.cagedToon.setChatAbsolute(TTLocalizer.CagedToonGoodbye, CFSpeech)
        self.ignore('nextChatPage')
        self.ignore('doneChatPage')
        intervalName = 'EpilogueMovieToonAnim'
        self.clearInterval(intervalName)
        track = Parallel(
            Sequence(
                ActorInterval(self.cagedToon, 'wave'),
                Func(self.cagedToon.loop, 'neutral')),
            Sequence(
                Wait(0.5),
                Func(self.localToonToSafeZone)
            )
        )
        self.storeInterval(track, intervalName)
        track.start()

    def exitEpilogue(self):
        self.clearInterval('EpilogueMovieToonAnim')
        self.unstash()
        self.__removeCageShadow()
        base.musicMgr.stopMusic(self.epilogueMusic)

    def __arrangeToonsAroundCage(self):
        radius = 15
        numToons = len(self.involvedToons)
        center = (numToons - 1) / 2.0
        for i in range(numToons):
            toon = base.cr.doId2do.get(self.involvedToons[i])
            if toon:
                angle = 270 - 15 * (i - center)
                radians = angle * math.pi / 180.0
                x = math.cos(radians) * radius
                y = math.sin(radians) * radius
                toon.setPos(self.cage, x, y, 0)
                toon.setZ(18.0)
                toon.headsUp(self.cage)

    ##### Frolic state #####

    def enterFrolic(self):
        # This state is probably only useful for debugging.
        # The toons are all free to run around the world.
        DistributedBossCog.DistributedBossCog.enterFrolic(self)
        self.setPosHpr(*BossCogGlobals.SellbotBossBattleOnePosHpr)

    ##### Misc. utility functions #####

    def doorACallback(self, isOpen):
        # Called whenever doorA opens or closes.
        if self.insidesANodePath:
            if isOpen:
                self.insidesANodePath.unstash()
            else:
                self.insidesANodePath.stash()

    def doorBCallback(self, isOpen):
        # Called whenever doorB opens or closes.
        if self.insidesBNodePath:
            if isOpen:
                self.insidesBNodePath.unstash()
            else:
                self.insidesBNodePath.stash()

    def __toonsToPromotionPosition(self, toonIds, battleNode):
        # At first, the toons walk down the ramp and stand close to the Boss Cog to receive a promotion.
        # They don't back up to battle position until a little bit later.
        points = BattleBase.BattleBase.toonPoints[len(toonIds) - 1]
        for i in range(len(toonIds)):
            toon = base.cr.doId2do.get(toonIds[i])
            if toon:
                toon.reparentTo(render)
                pos, h = points[i]
                toon.setPosHpr(battleNode, pos[0], pos[1] + 10, pos[2], h, 0, 0)

    def __doobersToPromotionPosition(self, doobers, battleNode):
        # The doobers start out facing the Boss Cog.
        points = BattleBase.BattleBase.toonPoints[len(doobers) - 1]
        for i in range(len(doobers)):
            suit = doobers[i]
            suit.request('Neutral')
            suit.loop('neutral')
            pos, h = points[i]
            suit.setPosHpr(battleNode, pos[0], pos[1] + 10, pos[2], h, 0, 0)

    def __touchedCage(self, entry):
        # The avatar has jumped up to touch the cage; he should be given pies now.
        self.notify.debug("__touchedCage()")
        self.sendUpdate('touchCage', [])
        self.__clearOnscreenMessage()
        taskMgr.remove(self.uniqueName('PieAdvice'))

        if not self.everThrownPie:
            taskMgr.doMethodLater(30, self.__howToThrowPies, self.uniqueName('PieAdvice'))

    def __outOfPies(self):
        self.__showOnscreenMessage(TTLocalizer.BossBattleNeedMorePies)
        taskMgr.doMethodLater(20, self.__howToGetPies, self.uniqueName('PieAdvice'))

    def __howToGetPies(self, task):
        self.__showOnscreenMessage(TTLocalizer.BossBattleHowToGetPies)

    def __howToThrowPies(self, task):
        self.__showOnscreenMessage(TTLocalizer.BossBattleHowToThrowPies % base.PRIMARY_KEY.upper())

    def __foundPieButton(self):
        self.everThrownPie = 1
        self.__clearOnscreenMessage()
        taskMgr.remove(self.uniqueName('PieAdvice'))

    def __pieSplat(self, toon, pieCode):
        self.notify.debug("__pieSplat()")
        # A pie thrown by localToon or some other toon hit something;
        # show a visible reaction if that something is the boss.
        if ConfigVariableBool('easy-vp', False).getValue():
            if not self.dizzy:
                pieCode = ToontownGlobals.PieCodeBossInsides
        if pieCode == ToontownGlobals.PieCodeBossInsides:
            if toon == localAvatar:
                self.d_hitBossInsides()
            self.flashRed()

        elif pieCode == ToontownGlobals.PieCodeBossCog:
            if toon == localAvatar:
                self.d_hitBoss(BossCogGlobals.SellbotBossPieDamage)
            if self.dizzy:
                self.doAnimate('hit', now=1)

    def __localPieSplat(self, pieCode, entry):
        self.notify.debug("__localPieSplat()")
        # A pie thrown by localToon toon hit something; tell the AI if we hit another toon.
        if pieCode != ToontownGlobals.PieCodeToon:
            return

        avatarDoId = entry.getIntoNodePath().getNetTag('avatarDoId')
        if avatarDoId == '':
            self.notify.warning('Toon %s has no avatarDoId tag.' % repr(entry.getIntoNodePath()))
            return

        doId = int(avatarDoId)
        if doId != localAvatar.doId:
            self.d_hitToon(doId)

    def __finalPieSplat(self, toon, pieCode):
        self.notify.debug("__finalPieSplat()")
        # This is the final pie toss that starts the boss's fall.
        # It's really just a formality, since we're already in the
        # Victory state.
        if pieCode != ToontownGlobals.PieCodeBossCog:
            return

        # Tell the AI; the AI will then immediately transition to Victory state.
        self.sendUpdate('finalPieSplat', [])

        # We don't care to hear any more about pies hitting the boss.
        self.ignore('pieSplat')

    def cagedToonBattleThree(self, index, avId):
        self.notify.debug('cagedToonBattleThree(%s, %s)' % (index, avId))

        if avId == base.localAvatar.doId and index < 100:  # Only play sound when restocking pies
            base.playSfx(self.piesRestockSfx)

        # The caged toon says something during battle three.
        str = TTLocalizer.CagedToonBattleThree.get(index)
        if str:
            toonName = ''
            if avId:
                toon = self.cr.doId2do.get(avId)
                if not toon:
                    self.cagedToon.clearChat()
                    return
                toonName = toon.getName()
            text = str % {'toon': toonName, 'primary': base.PRIMARY_KEY, 'jump': base.JUMP}
            self.cagedToon.setChatAbsolute(text, CFSpeech | CFTimeout)
        else:
            self.cagedToon.clearChat()

    def cleanupAttacks(self):
        # Stops any attack currently running.
        self.__cleanupStrafe()

    def __cleanupStrafe(self):
        if self.strafeInterval:
            self.strafeInterval.finish()
            self.strafeInterval = None

    def doStrafe(self, side, direction):
        self.notify.debug('doStrafe(%s, %s)' % (side, direction))
        # Spit a stream of gears out either the front or the back
        # door, from left to right (or from right to left).
        gearRoot = self.rotateNode.attachNewNode('gearRoot')
        if side == 0:
            gearRoot.setPos(0, -7, 3)
            gearRoot.setHpr(180, 0, 0)
            door = self.doorA
        else:
            gearRoot.setPos(0, 7, 3)
            door = self.doorB

        gearRoot.setTag('attackCode', str(BossCogGlobals.BossCogStrafeAttack))
        gearModel = self.getGearFrisbee()
        gearModel.setScale(0.1)

        t = self.getBossDamage() / (self.bossMaxDamage * 1.0)

        gearTrack = Parallel()

        # numGears ranges from 4 to 10
        numGears = min(len(self.strafeSfx), int(4 + 6 * t + 0.5))
        # time ranges from 5 to 1
        time = 5.0 - 4.0 * t

        spread = 60 * math.pi / 180.0
        if direction == 1:
            spread = -spread

        dist = 50
        rate = time / numGears
        for i in range(numGears):
            node = gearRoot.attachNewNode(str(i))
            node.hide()
            node.setPos(0, 0, 0)
            gearModel.instanceTo(node)
            angle = (float(i) / (numGears - 1) - 0.5) * spread
            x = dist * math.sin(angle)
            y = dist * math.cos(angle)
            h = random.uniform(-720, 720)
            gearTrack.append(Sequence(
                Wait(i * rate),
                Func(node.show),
                Parallel(
                    node.posInterval(1, Point3(x, y, 0), fluid = 1),
                    node.hprInterval(1, VBase3(h, 0, 0), fluid = 1),
                    Sequence(
                        SoundInterval(self.strafeSfx[i], volume = 0.2, node = self), duration = 0)
                ),
                Func(node.detachNode)
            ))

        seq = Sequence(
            Func(door.request, 'open'),
            Wait(0.7), gearTrack, Func(door.request, 'close')
        )
        self.__cleanupStrafe()
        self.strafeInterval = seq
        seq.start()

    def toonPromoted(self, promoted):
        self.localToonPromoted = promoted

    @property
    def uniteResistanceToon(self):
        return self.cagedToon
