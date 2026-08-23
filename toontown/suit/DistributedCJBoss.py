import random

from direct.distributed.ClockDelta import *
from direct.interval.IntervalGlobal import *
from panda3d.core import *

from otp.nametag.NametagConstants import *
from toontown.battle import BattleProps
from toontown.duckhuntbossbattle import FourBossBattleGlobals
from toontown.duckhuntbossbattle.DistributedRebornBossCog import DistributedRebornBossCog
from toontown.toonbase import ToontownGlobals


class DistributedCJBoss(DistributedRebornBossCog):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedCJBoss')

    def __init__(self, cr):
        self.notify.debug('----- __init___')
        DistributedRebornBossCog.__init__(self, cr)
        self.bossDamage = 0
        self.bossMaxDamage = 2652
        self.av = None
        self.largeAttackSeq = None
        self.roamAttackSeq = None
        self.roamHitSeq = None
        self.handler = None
        self.collided = False
        self.track = None
        self.treadsSeq = None
        self.bossIndex = 2
        self.battleTwoSeq = None
        self.dizzyIval = None
        self.dizzySeq = None
        self.rollTrack = None
        self.centerTrack = None
        self.leaveTrack = None
        self.leaveSeq = None
        self.deathIval = None
        self.bounceBackSeq = None

    def announceGenerate(self):
        DistributedRebornBossCog.announceGenerate(self)
        target = CollisionTube(0, -1, 4, 0, -1, 9, 3.5)
        targetNode = CollisionNode('CJTarget')
        targetNode.addSolid(target)
        targetNode.setCollideMask(ToontownGlobals.PieBitmask)
        self.targetNodePath = self.pelvis.attachNewNode(targetNode)
        box = CollisionBox(Point3(0, 0, 2.9), 4.4, 6.9, 2.9)
        self.collNode.addSolid(box)

    def beginBattleTwo(self):
        self.generateHealthBar()
        self.updateHealthBar()
        podiumNode = render.find('**/CJStand')
        node = render.attachNewNode('returnNode')
        node.reparentTo(render)
        node.setPos(16.99, -22, 0.025)
        time = self.getDistance(node) / 20
        track, _ = self.rollBossToPoint(Point3(16.99, 77.8887, 1.1285), None, Point3(node.getX(), node.getY(), 0),
                                        Point3(0, 0, 0), False, False, None, time)
        self.battleTwoSeq = Sequence(
            Func(base.playSfx, self.podiumSfx, node=podiumNode),
            podiumNode.posInterval(3.0, (16.99, 77.8887, -20.8715)),
            Func(self.wrtReparentTo, render),
            track,
            Func(self.setH, 0),
            Func(node.removeNode),
            Func(self.startCollisionHandler)
        )
        self.battleTwoSeq.start()

    def generateHealthBar(self):
        self.removeHealthBar()
        chestNull = self.find('**/joint_lifeMeter')
        if chestNull.isEmpty():
            return
        model = loader.loadModel('phase_3.5/models/gui/matching_game_gui')
        button = model.find('**/minnieCircle')
        button.setScale(6.0)
        button.setY(1.75)
        button.setP(-20)
        button.setColor(self.healthColors[0])
        button.reparentTo(chestNull)
        self.healthBar = button
        glow = BattleProps.globalPropPool.getProp('glow')
        glow.reparentTo(self.healthBar)
        glow.setScale(0.28)
        glow.setPos(-0.005, 0.01, 0.015)
        glow.setColor(self.healthGlowColors[0])
        button.flattenLight()
        self.healthBarGlow = glow
        self.healthCondition = 0

    def startCollisionHandler(self):
        if not (hasattr(self, 'collNodePath') and self.collNodePath):
            # cack
            return

        self.handler = CollisionHandlerEvent()
        self.handler.setInPattern(self.uniqueName('cjInCollision'))
        self.handler.setOutPattern(self.uniqueName('cjOutCollision'))
        base.cTrav.addCollider(self.collNodePath, self.handler)
        self.accept(self.uniqueName('cjInCollision'), self.__handleInCollision)
        self.accept(self.uniqueName('cjOutCollision'), self.__handleOutCollision)

    def stopCollisionHandler(self):
        self.ignore(self.uniqueName('cjInCollision'))
        self.ignore(self.uniqueName('cjOutCollision'))
        if hasattr(self, 'collNodePath') and self.collNodePath:
            base.cTrav.removeCollider(self.collNodePath)

        self.handler = None

    def __handleInCollision(self, collisionEntry):
        hitNode = collisionEntry.getIntoNode().getName()

        goonCollisions = ['goon', 'toonSphere-', 'GoonTrigger', 'goonCollSphere']
        for goonCollision in goonCollisions:
            if goonCollision in hitNode:
                if self.av == base.localAvatar:
                    goonDoId = collisionEntry.getIntoNodePath().getNetTag('doId')
                    if goonDoId == '':
                        self.notify.warning('Goon %s has no doId tag.' % repr(collisionEntry.getIntoNodePath()))
                        return
                    doId = int(goonDoId)
                    if doId != localAvatar.doId:
                        self.bossBattle.d_hitGoon(doId)

        if 'CannonSphere' in hitNode:
            cannonDoId = collisionEntry.getIntoNodePath().getNetTag('doIdCannon')
            if cannonDoId == '':
                return
            doId = int(cannonDoId)
            if doId != localAvatar.doId:
                cannon = self.cr.doId2do.get(doId)
                cannon.enterFlat()

        if self.collided:
            return

        if self.getIsDead():
            return  # no cack beyond this point

        generalCollisions = ['wall_collision', 'side', 'top', 'sides', 'MoneyStacksPallet2Collision', 'collision',
                             'collision1', 'collision2', 'wall', 'floor', 'shelf_collision']
        if hitNode in generalCollisions:
            destPos = self.getPos()
            destHpr = self.getHpr()
            if self.roamAttackSeq:
                self.roamAttackSeq.finish()
            self.roamAttackSeq = None
            self.roamHitSeq = Sequence()
            self.roamHitSeq.append(Func(self.setCollided, True))
            self.roamHitSeq.append(Func(self.setPos, destPos))
            self.roamHitSeq.append(Func(self.setHpr, destHpr))
            if self.track.getT() >= 1.5:
                damage = int(self.track.getT() * 75)  # We're doing 75 damage for every second the CJ had been running
                if damage > 300:
                    damage = 300
                if self.av == base.localAvatar:
                    self.roamHitSeq.append(Func(self.d_hitBoss, damage, destPos, destHpr))
            else:
                damage = int(self.track.getT() * 25)
                if self.av == base.localAvatar:
                    self.roamHitSeq.append(Func(self.d_hitBoss, damage, destPos, destHpr))
            self.roamHitSeq.start()
            self.track.pause()
            self.track = Sequence()
            self.treadsSeq.pause()
            self.treadsSeq = Sequence()
            self.av = None

    def __handleOutCollision(self, collisionEntry):
        cannonDoId = collisionEntry.getIntoNodePath().getNetTag('doIdCannon')
        if not cannonDoId:
            return
        doId = int(cannonDoId)
        if doId != localAvatar.doId:
            cannon = self.cr.doId2do.get(doId)
            cannon.exitFlat()

    def setIsDizzy(self, bossDamage):
        if bossDamage >= 50:
            self.happy = 1
            node = render.attachNewNode('bounceBackNode')
            node.reparentTo(self)
            node.setPos(0.0, 10.0, 0.0)
            node.wrtReparentTo(render)
            track, _ = self.rollBossToPoint(self.getPos(), None, Point3(node.getX(), node.getY(), 0),
                                            self.getHpr(), False, False, None, 0.3)
            self.dizzyIval = Sequence(Func(self.setDizzy, 1),
                                      Parallel(SoundInterval(self.reelSfx, node=self), Func(self.reverseHead),
                                               ActorInterval(self, 'Fb_firstHit'), track),
                                      Func(self.loop, 'Fb_downNeutral'),
                                      Wait(2),
                                      Func(self.setDizzy, 0),
                                      Parallel(SoundInterval(self.upSfx, node=self), ActorInterval(self, 'Fb_down2Up')),
                                      Func(self.forwardHead),
                                      Func(self.loop, 'Ff_neutral'),
                                      Func(node.removeNode))
            self.dizzyIval.start()
        elif bossDamage <= 50:
            self.happy = 1
            self.dizzyIval = Sequence(Parallel(SoundInterval(self.reelSfx, node=self), Func(self.reverseHead),
                                               ActorInterval(self, 'Fb_firstHit')),
                                      Parallel(SoundInterval(self.upSfx, node=self), ActorInterval(self, 'Fb_down2Up')),
                                      Func(self.forwardHead),
                                      Func(self.loop, 'Ff_neutral'))
            node = render.attachNewNode('returnNode')
            node.reparentTo(render)
            node.setPos(0, -22, 0.025)
            time = self.getDistance(node) / 20
            self.dizzySeq = Sequence()
            self.dizzySeq.append(
                Func(self.setChatAbsolute, "Hmmmph! Where have you Toons gone?!", CFSpeech | CFTimeout))
            self.dizzySeq.append(self.dizzyIval)
            self.dizzySeq.append(
                Func(self.rollBossToPoint, self.getPos(), self.getHpr(), Point3(node.getX(), node.getY(), 0),
                     Point3(node.getH(), 0, 0), False, True, 1, time))
            self.dizzySeq.append(Func(node.removeNode))
            self.dizzySeq.start()

    def disable(self):
        DistributedRebornBossCog.disable(self)
        render.clearTag('pieCode')
        self.targetNodePath.detachNode()
        self.stopCollisionHandler()
        if self.track:
            self.track.finish()
        self.track = None
        if self.treadsSeq:
            self.treadsSeq.finish()
        self.treadsSeq = None
        if self.largeAttackSeq:
            self.largeAttackSeq.finish()
        self.largeAttackSeq = None
        if self.roamAttackSeq:
            self.roamAttackSeq.finish()
        self.roamAttackSeq = None
        if self.roamHitSeq:
            self.roamHitSeq.finish()
        self.roamHitSeq = None
        if self.battleTwoSeq:
            self.battleTwoSeq.finish()
        self.battleTwoSeq = None
        if self.dizzyIval:
            self.dizzyIval.finish()
        self.dizzyIval = None
        if self.dizzySeq:
            self.dizzySeq.finish()
        self.dizzySeq = None
        if self.rollTrack:
            self.rollTrack.finish()
        self.rollTrack = None
        if self.centerTrack:
            self.centerTrack.finish()
        self.centerTrack = None
        if self.leaveTrack:
            self.leaveTrack.finish()
        self.leaveTrack = None
        if self.leaveSeq:
            self.leaveSeq.finish()
        self.leaveSeq = None
        if self.deathIval:
            self.deathIval.finish()
        self.deathIval = None
        if self.bounceBackSeq:
            self.bounceBackSeq.finish()
        self.bounceBackSeq = None
        self.ignoreAll()
        self.removeAllTasks()

    def getGearFrisbee(self):
        return loader.loadModel('phase_5/models/props/lawbook')

    def doLargeAttack(self, _):
        self.largeAttackSeq = Sequence()
        self.largeAttackSeq.append(
            Func(self.setChatAbsolute, random.choice(FourBossBattleGlobals.LargeAttackCJPhrases),
                 CFSpeech | CFTimeout)
        )
        return self.largeAttackSeq

    def doRoamAttack(self, avId):
        if not avId:
            node = render.attachNewNode('returnNode')
            node.reparentTo(render)
            node.setPos(0, -22, 0.025)
            time = self.getDistance(node) / 20
            self.roamAttackSeq = Sequence()
            self.roamAttackSeq.append(
                Func(self.setChatAbsolute, "Wow! You suck ass, C.F.O.! How come you let the Toons kill you?!",
                     CFSpeech | CFTimeout))
            self.roamAttackSeq.append(
                Func(self.rollBossToPoint, self.getPos(), self.getHpr(), Point3(node.getX(), node.getY(), 0),
                     Point3(node.getH(), 0, 0), False, True, 1, time))
            self.roamAttackSeq.append(Func(node.removeNode))
            self.roamAttackSeq.start()
            return

        self.av = self.cr.doId2do.get(avId)
        if not self.av:
            return

        self.track = Sequence()

        self.roamAttackSeq = Sequence()
        self.roamAttackSeq.append(
            Func(self.setChatAbsolute, random.choice(FourBossBattleGlobals.RoamAttackCJPhrases) % self.av.getName(),
                 CFSpeech | CFTimeout))
        self.roamAttackSeq.append(
            Parallel(
                ActorInterval(self, 'charge'),
                Sequence(
                    Wait(1), Func(self.makeTrack, self.av), Wait(0.75), Func(self.setCollided, False)
                )
            )
        )
        self.roamAttackSeq.append(Func(self.loop, 'Ff_neutral'))
        self.roamAttackSeq.start()

    def makeTrack(self, av):
        if av:
            cjInitialH = self.getH()
            self.headsUp(av)
            cjEndH = self.getH() + 180
            self.setH(cjInitialH)

            dist = int(self.getDistance(av))
            if dist == 0:
                dist = 1
            self.track = Sequence(
                Parallel(
                    Func(self.turnBossWheels, self, (cjEndH, 0, 0), (cjInitialH, 0, 0), 0.5),
                    self.quatInterval(0.5, hpr=Vec3(cjEndH, 0, 0))
                )
            )
            for move in range(dist + 10):
                y = -(move / dist + 1)
                self.track.append(
                    Sequence(
                        Wait(0.35 / 12), Func(self.setY, self, y)
                    )
                )
            turnDuration = self.track.getDuration() - 0.5
            self.track.insert(
                2, Func(self.turnBossWheels, self, None, None, turnDuration, 'back')
            )
            self.track.append(
                self.cjBounceBack()
            )
            self.track.start()

    def cjBounceBack(self):
        return Func(self.cjBounceBackSeq)

    def cjBounceBackSeq(self):
        node = render.attachNewNode('bounceBackNode')
        node.reparentTo(self)
        node.setPos(0.0, 5.0, 0.0)
        node.wrtReparentTo(render)
        self.bounceBackSeq, _ = self.rollBossToPoint(self.getPos(), None, Point3(node.getX(), node.getY(), 0),
                                                     self.getHpr(), False, False, None, 1.0)
        self.bounceBackSeq.append(Func(node.removeNode))
        self.bounceBackSeq.start()

    def turnBossWheels(self, actor, toHpr, fromHpr, length, direction=None):
        speed = length * 4
        if direction is None:
            if toHpr[0] < fromHpr[0]:
                direction = 'left'
            else:
                direction = 'right'
        RTread = actor.find('**/right_tread')
        LTread = actor.find('**/left_tread')
        Rspin = NodePath('Rspin')
        Lspin = NodePath('Lspin')
        RTread.setTexProjector(TextureStage.getDefault(), NodePath(), Rspin)
        LTread.setTexProjector(TextureStage.getDefault(), NodePath(), Lspin)
        if direction == 'left':
            self.treadsSeq = Parallel(
                Rspin.posInterval(length, VBase3(speed, 0, 0)),
                Lspin.posInterval(length, VBase3(-speed, 0, 0))
            )
        elif direction == 'right':
            self.treadsSeq = Parallel(
                Rspin.posInterval(length, VBase3(-speed, 0, 0)),
                Lspin.posInterval(length, VBase3(speed, 0, 0))
            )
        elif direction == 'back':
            self.treadsSeq = Parallel(
                Rspin.posInterval(length, VBase3(-speed, 0, 0)),
                Lspin.posInterval(length, VBase3(-speed, 0, 0))
            )
        elif direction == 'front':
            self.treadsSeq = Parallel(
                Rspin.posInterval(length, VBase3(speed, 0, 0)),
                Lspin.posInterval(length, VBase3(speed, 0, 0))
            )
        self.treadsSeq.start()

    def cleanupTrack(self):
        self.av = None

    def setCollided(self, collided):
        self.collided = collided

    def d_hitBoss(self, bossDamage, destPos, destHpr):
        x, y, z = destPos
        h, p, r = destHpr
        self.sendUpdate('hitBoss', [bossDamage, x, y, z, h, p, r])

    def setBossDamage(self, bossDamage):
        self.flashRed()
        self.showHpText(-(bossDamage - self.bossDamage), scale=5)
        self.bossDamage = bossDamage
        self.updateHealthBar()

    def rollBossToPoint(self, fromPos, fromHpr, toPos, toHpr, reverse, autoStart=False, turnTime=None, rollTime=None,
                        customToHpr=False):
        vector = Vec3(toPos - fromPos)
        distance = vector.length()
        if toHpr == None:
            mat = Mat3(0, 0, 0, 0, 0, 0, 0, 0, 0)
            headsUp(mat, vector, CSDefault)
            scale = VBase3(0, 0, 0)
            shear = VBase3(0, 0, 0)
            toHpr = VBase3(0, 0, 0)
            decomposeMatrix(mat, scale, shear, toHpr, CSDefault)
        if fromHpr and not customToHpr:
            self.headsUp(toPos)
            self.setH(self.getH() + 180)
            toHpr = self.getHpr()
        elif not customToHpr:
            fromHpr = toHpr
        if not turnTime:
            turnTime = abs(toHpr[0] - fromHpr[0]) / ToontownGlobals.BossCogTurnSpeed
        if toHpr[0] < fromHpr[0]:
            leftRate = ToontownGlobals.BossCogTreadSpeed
        else:
            leftRate = -ToontownGlobals.BossCogTreadSpeed
        if reverse:
            rollTreadRate = -ToontownGlobals.BossCogTreadSpeed
        else:
            rollTreadRate = ToontownGlobals.BossCogTreadSpeed
        if not rollTime:
            rollTime = distance / ToontownGlobals.BossCogRollSpeed
        deltaPos = toPos - fromPos
        self.rollTrack = Sequence(Func(self.setPos, fromPos),
                                  Parallel(self.hprInterval(turnTime, toHpr, fromHpr),
                                           self.rollLeftTreads(turnTime, leftRate),
                                           self.rollRightTreads(turnTime, -leftRate)),
                                  Parallel(LerpFunctionInterval(self.rollBoss, duration=rollTime,
                                                                extraArgs=[fromPos, deltaPos]),
                                           self.rollLeftTreads(rollTime, rollTreadRate),
                                           self.rollRightTreads(rollTime, rollTreadRate)))
        if autoStart:
            self.rollTrack.start()
        else:
            return (self.rollTrack, toHpr)

    def setIsDead(self, isDead):
        DistributedRebornBossCog.setIsDead(self, isDead)
        if isDead:
            self.__handleCJDeath()

    def __handleCJDeath(self):
        self.setDizzy(0)
        self.cleanupIntervals()
        self.clearChat()
        self.happy = 0
        self.raised = 0
        self.forward = 1
        rightDoors = render.findAllMatches('**/rightDoor')
        leftDoors = render.findAllMatches('**/leftDoor')
        openDoorSfx = loader.loadSfx('phase_9/audio/sfx/CHQ_SOS_cage_land.ogg')
        podiumNode = render.find('**/CJStand')
        node = render.attachNewNode('bounceBackNode')
        node.reparentTo(self)
        node.setPos(0.0, 10.0, 0.0)
        node.wrtReparentTo(render)
        returnNode = render.attachNewNode('returnNode')
        returnNode.reparentTo(render)
        returnNode.setPos(self.getX(), 0, 0.025)
        time = self.getDistance(returnNode) / 20
        track, _ = self.rollBossToPoint(self.getPos(), None, Point3(node.getX(), node.getY(), 0.025),
                                        self.getHpr(), False, False, None, 0.3)
        centerHpr = Point3(180, 0, 0)
        leaveHpr = Point3(180, 0, 0)
        if self.getY() > 0:
            centerHpr = Point3(0, 0, 0)
            leaveHpr = Point3(0, 0, 0)
        leaveHprTime = 1
        if self.getX() >= 160 or -10 <= self.getY() <= 10:
            self.centerTrack = Sequence()
            leaveHpr = self.getHpr()
            leaveHprTime = None
        else:
            self.centerTrack, _ = self.rollBossToPoint(node.getPos(), self.getHpr(),
                                                       Point3(node.getX(), returnNode.getY(), 0.025),
                                                       centerHpr, False, False, 1, time, True)
        self.leaveSeq = Sequence()
        self.leaveTrack, _ = self.rollBossToPoint(Point3(node.getX(), returnNode.getY(), 0.025), leaveHpr,
                                                  Point3(210, 0, 0.025),
                                                  Point3(90, 0, 0), False, False, leaveHprTime, 10, True)
        self.leaveSeq.append(
            Sequence(
                self.leaveTrack,
                Parallel(
                    rightDoors[0].hprInterval(2.0, (0, 0, 0)),
                    leftDoors[0].hprInterval(2.0, (0, 0, 0)),
                    Sequence(Wait(2.0), Func(base.playSfx, openDoorSfx))
                ),
                Func(node.removeNode),
                Func(returnNode.removeNode),
                Func(self.stopCollisionHandler),
                Func(base.playSfx, self.podiumSfx, node=podiumNode),
                podiumNode.posInterval(1.0, (16.99, 77.8887, -25.8715)),
                Func(render.find('**/LPodium_shadow').removeNode)
            )
        )

        if self.track:
            self.track.pause()
        self.track = Sequence()
        if self.treadsSeq:
            self.treadsSeq.pause()
        self.treadsSeq = Sequence()

        self.deathIval = Sequence(
            Parallel(
                SoundInterval(self.reelSfx, node=self), Func(self.reverseHead),
                ActorInterval(self, 'Fb_firstHit'), track
            ),
            Parallel(
                SoundInterval(self.upSfx, node=self),
                ActorInterval(self, 'Fb_down2Up')
            ),
            Func(self.setChatAbsolute, "Hrrmpphh. While I am blind, I can clearly see this isn't going to end well!",
                 CFSpeech | CFTimeout),
            Func(self.forwardHead),
            Func(self.loop, 'Ff_neutral'),
            self.centerTrack,
            Func(self.setChatAbsolute, "I suggest we reschedule this meeting, C.E.O.!", CFSpeech | CFTimeout),
            Parallel(
                self.leaveSeq,
                rightDoors[0].hprInterval(2.0, (90, 0, 0)),
                leftDoors[0].hprInterval(2.0, (-90, 0, 0)),
                Sequence(Wait(2.0), Func(base.playSfx, openDoorSfx))
            )
        )
        self.deathIval.start()
