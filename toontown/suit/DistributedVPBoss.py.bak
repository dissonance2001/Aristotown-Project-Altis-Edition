import random

from direct.distributed.ClockDelta import *
from direct.interval.IntervalGlobal import *
from panda3d.core import *

from otp.nametag.NametagConstants import *
from toontown.battle import BattleProps, BattleParticles
from toontown.duckhuntbossbattle import FourBossBattleGlobals
from toontown.duckhuntbossbattle.DistributedRebornBossCog import DistributedRebornBossCog
from toontown.toonbase import ToontownGlobals


class DistributedVPBoss(DistributedRebornBossCog):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedVPBoss')

    def __init__(self, cr):
        self.notify.debug('----- __init___')
        DistributedRebornBossCog.__init__(self, cr)
        self.bossDamage = 0
        self.bossMaxDamage = 65
        self.attackCode = None
        self.recoverRate = 0
        self.recoverStartTime = 0
        self.bossDamageMovie = None
        self.insidesANodePath = None
        self.insidesBNodePath = None
        self.largeAttackSfx = loader.loadSfx('phase_5/audio/sfx/SA_brainstorm.ogg')
        self.largeAttackSeq = None
        self.bossIndex = 0
        self.deathSeq = None
        self.cloudTracks = []
        self.cloudWaitTracks = []
        self.shadowTracks = []
        self.shadowWaitTracks = []

    def announceGenerate(self):
        DistributedRebornBossCog.announceGenerate(self)
        insidesA = CollisionPolygon(Point3(4.0, -6.0, 5.0), Point3(-4.0, -6.0, 5.0), Point3(-4.0, -6.0, 0.5),
                                    Point3(4.0, -6.0, 0.5))
        insidesANode = CollisionNode('VPInsidesA')
        insidesANode.addSolid(insidesA)
        insidesANode.setCollideMask(ToontownGlobals.PieBitmask | ToontownGlobals.WallBitmask)
        self.insidesANodePath = self.axle.attachNewNode(insidesANode)
        self.insidesANodePath.stash()
        insidesB = CollisionPolygon(Point3(-4.0, 2.0, 5.0), Point3(4.0, 2.0, 5.0), Point3(4.0, 2.0, 0.5),
                                    Point3(-4.0, 2.0, 0.5))
        insidesBNode = CollisionNode('VPInsidesB')
        insidesBNode.addSolid(insidesB)
        insidesBNode.setCollideMask(ToontownGlobals.PieBitmask | ToontownGlobals.WallBitmask)
        self.insidesBNodePath = self.axle.attachNewNode(insidesBNode)
        self.insidesBNodePath.stash()
        target = CollisionTube(0, -1, 4, 0, -1, 9, 3.5)
        targetNode = CollisionNode('VPTarget')
        targetNode.addSolid(target)
        targetNode.setCollideMask(ToontownGlobals.PieBitmask)
        self.targetNodePath = self.pelvis.attachNewNode(targetNode)
        shield = CollisionTube(0, 1, 4, 0, 1, 7, 3.5)
        shieldNode = CollisionNode('VPShield')
        shieldNode.addSolid(shield)
        shieldNode.setCollideMask(ToontownGlobals.PieBitmask | ToontownGlobals.CameraBitmask)
        shieldNodePath = self.pelvis.attachNewNode(shieldNode)
        disk = loader.loadModel('phase_9/models/char/bossCog-gearCollide')
        disk.find('**/+CollisionNode').setName('VPDisk')
        disk.reparentTo(self.pelvis)
        disk.setZ(0.8)

    def disable(self):
        DistributedRebornBossCog.disable(self)
        render.clearTag('pieCode')
        self.targetNodePath.detachNode()
        if self.bossDamageMovie:
            self.bossDamageMovie.finish()
        self.bossDamageMovie = None
        if self.deathSeq:
            self.deathSeq.finish()
        self.deathSeq = None
        if self.largeAttackSeq:
            self.largeAttackSeq.finish()
        self.largeAttackSeq = None
        if self.canAttackTrack:
            self.canAttackTrack.finish()
        self.canAttackTrack = None
        for cloudTrack in self.cloudTracks:
            if cloudTrack:
                cloudTrack.finish()
        self.cloudTracks = []
        for cloudWaitTrack in self.cloudWaitTracks:
            if cloudWaitTrack:
                cloudWaitTrack.finish()
        self.cloudWaitTracks = []
        for shadowTrack in self.shadowTracks:
            if shadowTrack:
                shadowTrack.finish()
        self.shadowTracks = []
        for shadowWaitTrack in self.shadowWaitTracks:
            if shadowWaitTrack:
                shadowWaitTrack.finish()
        self.shadowWaitTracks = []
        self.ignoreAll()
        self.removeAllTasks()
        return

    def doorACallback(self, isOpen):
        if self.insidesANodePath:
            if isOpen:
                self.insidesANodePath.unstash()
            else:
                self.insidesANodePath.stash()

    def doorBCallback(self, isOpen):
        if self.insidesBNodePath:
            if isOpen:
                self.insidesBNodePath.unstash()
            else:
                self.insidesBNodePath.stash()

    def d_hitBoss(self, bossDamage):
        self.sendUpdate('hitBoss', [bossDamage])

    def d_hitBossInsides(self):
        self.sendUpdate('hitBossInsides', [])

    def setBossDamage(self, bossDamage, recoverRate, timestamp):
        recoverStartTime = globalClockDelta.networkToLocalTime(timestamp)
        self.bossDamage = bossDamage
        self.recoverRate = recoverRate
        self.recoverStartTime = recoverStartTime
        taskName = 'RecoverBossDamage'
        taskMgr.remove(taskName)
        self.updateHealthBar()
        if self.bossDamageMovie:
            if self.bossDamage >= self.bossMaxDamage:
                self.bossDamageMovie.resumeUntil(self.bossDamageMovie.getDuration())
            else:
                self.bossDamageMovie.resumeUntil(self.bossDamage * self.bossDamageToMovie)
                if self.recoverRate:
                    taskMgr.add(self.__recoverBossDamage, taskName)

    def getBossDamage(self):
        now = globalClock.getFrameTime()
        elapsed = now - self.recoverStartTime
        return max(self.bossDamage - self.recoverRate * elapsed / 60.0, 0)

    def __recoverBossDamage(self, task):
        self.bossDamageMovie.setT(self.getBossDamage() * self.bossDamageToMovie)
        self.updateHealthBar()
        return task.cont

    def __makeBossDamageMovie(self):
        startPos = Point3(*self.getPos())
        startHpr = Point3(*self.getHpr())
        deathPos = Point3(self.getPos()[0], self.getPos()[1] + 62, self.getPos()[2])
        self.setPosHpr(startPos, startHpr)
        bossTrack = Sequence()
        bossTrack.append(Func(self.loop, 'Fb_neutral'))
        track, hpr = self.rollBossToPoint(startPos, startHpr, deathPos, startHpr, 1)
        bossTrack.append(track)
        return bossTrack

    def beginBattleTwo(self):
        self.wrtReparentTo(render)
        self.bossDamageMovie = self.__makeBossDamageMovie()
        bossDoneEventName = self.uniqueName('DestroyedBoss')
        self.bossDamageMovie.setDoneEvent(bossDoneEventName)
        self.acceptOnce(bossDoneEventName, self.__doneBattleTwo)
        self.bossDamageToMovie = self.bossDamageMovie.getDuration() / self.bossMaxDamage
        self.bossDamageMovie.setT(self.bossDamage * self.bossDamageToMovie)
        self.generateHealthBar()
        self.updateHealthBar()
        self.healthBar.hide()

    def __doneBattleTwo(self):
        self.endBattleTwo()

    def endBattleTwo(self):
        bossDoneEventName = self.uniqueName('DestroyedBoss')
        self.ignore(bossDoneEventName)
        self.bossDamageMovie.finish()
        self.bossDamageMovie = None
        taskName = 'RecoverBossDamage'
        taskMgr.remove(taskName)

    def setIsDead(self, isDead):
        DistributedRebornBossCog.setIsDead(self, isDead)
        if isDead:
            self.__handleVPDeath()

    def __handleVPDeath(self):
        self.setDizzy(0)
        self.cleanupIntervals()
        self.clearChat()
        self.happy = 0
        self.raised = 0
        self.forward = 1
        self.doAnimate('Fb_fall', now=1)
        self.setChatAbsolute("No! The markets will crash as I do!", CFSpeech | CFTimeout)
        window = render.find('**/glass')
        podiumNode = render.find('**/VPStand')
        self.deathSeq = Sequence(
            window.posHprInterval(0.25, (0, 1, 0), (0, -1, 0)),
            Wait(0.75),
            window.posHprInterval(0.25, (0, 2, 0), (0, -2, 0)),
            Wait(3.5),
            window.posHprInterval(0.75, (0, 12, 0), (0, -45, 0)),
            Func(base.playSfx, self.podiumSfx, node=podiumNode),
            podiumNode.posInterval(1.0, (-52.7158, 39.1657, -25.8715)),
            Func(render.find('**/SPodium_shadow').removeNode)
        )
        self.deathSeq.start()
        self.acceptOnce(self.animDoneEvent, self.__handleDeathDone)

    def __handleDeathDone(self):
        self.cleanupIntervals()
        self.clearChat()
        self.stash()
        self.stopAnimate()

    def cloudTask(self, toggle, cloud, shadow, toon, avId):
        if toggle:
            taskMgr.add(self.cloudFollow, 'cloudFollow' + str(avId), extraArgs=[cloud, shadow, toon], appendTask=True)
        else:
            taskMgr.remove('cloudFollow' + str(avId))

    def cloudFollow(self, cloud, shadow, toon, task):
        if toon:
            cloudTrack = cloud.posInterval(1, (toon.getX(render), toon.getY(render), 15))
            cloudWaitTrack = Sequence(Wait(globalClock.getDt()), Func(cloudTrack.pause))
            cloudWaitTrack.start()
            self.cloudWaitTracks.append(cloudWaitTrack)
            cloudTrack.start()
            self.cloudTracks.append(cloudTrack)
            shadowTrack = shadow.posInterval(1, (toon.getX(render), toon.getY(render), 0.1))
            shadowWaitTrack = Sequence(Wait(globalClock.getDt()), Func(shadowTrack.pause))
            shadowWaitTrack.start()
            self.shadowWaitTracks.append(shadowWaitTrack)
            shadowTrack.start()
            self.shadowTracks.append(shadowTrack)
            return task.again

    def doLargeAttack(self, avId):
        self.setChatAbsolute(random.choice(FourBossBattleGlobals.LargeAttackVPPhrases), CFSpeech | CFTimeout)
        toon = base.cr.doId2do.get(avId)
        if not toon:
            return

        stormcloud = BattleProps.globalPropPool.getProp('stormcloud')
        stormcloud.reparentTo(self)
        stormcloud.setScale(0)
        stormcloud.setZ(2.5)

        dropShadow = loader.loadModel('phase_3/models/props/drop_shadow')
        dropShadow.setColor(0, 0, 0, 0.69)
        dropShadow.setPos(0, 0, -1.35)
        dropShadow.reparentTo(stormcloud)

        gears = BattleParticles.loadParticleFile('gearRain.ptf')
        gears.setDepthWrite(False)

        def __checkNearCloud(task):
            if stormcloud:
                try:
                    if Vec3(base.localAvatar.getPos(stormcloud)).length() <= 1.5:
                        self.zapLocalToon(ToontownGlobals.BossCogLargeAttack)
                except:
                    return task.done

            return task.done

        self.largeAttackSeq = Sequence(
            self.doRecover(),
            Wait(3),
            Parallel(
                ActorInterval(self, 'Bb_point'),
                Parallel(
                    Func(self.doorA.request, 'open'),
                    LerpPosInterval(stormcloud, duration=4, pos=(0, -17, 7)),
                    stormcloud.scaleInterval(4, (15.4, 15.4, 11))
                )
            ),
            Func(self.loop, 'Fb_neutral'),
            Parallel(
                Func(self.doorA.request, 'close'),
                Sequence(
                    Func(dropShadow.reparentTo, render),
                    Func(dropShadow.setPos, stormcloud.getX(render), stormcloud.getY(render), 0.1),
                    dropShadow.scaleInterval(4, 3.08, startScale=Vec3(0.01, 0.01, 1.0))
                ),
                Func(stormcloud.wrtReparentTo, render),
                Sequence(
                    Func(self.cloudTask, True, stormcloud, dropShadow, toon, avId),
                    Wait(4),
                    Func(stormcloud.setZ, 2.5),
                    Func(self.cloudTask, False, stormcloud, dropShadow, toon, avId)
                )
            ),
            Parallel(
                Func(base.playSfx, self.largeAttackSfx),
                ParticleInterval(gears, stormcloud, worldRelative=0, duration=4.3, cleanup=True)
            ),
            Wait(1),
            Parallel(
                dropShadow.scaleInterval(1, Vec3(0.01, 0.01, 1.0), startScale=3.08),
                stormcloud.scaleInterval(1, (0.0, 0.0, 0.0))
            ),
            Func(dropShadow.removeNode)
        )
        taskMgr.doMethodLater(12, __checkNearCloud, self.uniqueName('CheckNearStormcloud'))
        return self.largeAttackSeq

    def cleanupAttacks(self):
        if self.canAttackTrack:
            self.canAttackTrack.finish()
        self.canAttackTrack = None
