import random

from direct.directnotify import DirectNotifyGlobal
from direct.interval.IntervalGlobal import *
from panda3d.core import *

from otp.nametag.NametagConstants import *
from otp.otpbase import PythonUtil
from toontown.duckhuntbossbattle import FourBossBattleGlobals
from toontown.duckhuntbossbattle.DistributedRebornBossCog import DistributedRebornBossCog
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownGlobals


class DoorBool:
    doorBool = False


class DistributedCEOBoss(DistributedRebornBossCog):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedCEOBoss')
    BallLaunchOffset = Point3(10.5, 8.5, -5)

    def __init__(self, cr):
        self.notify.debug('----- __init___')
        DistributedRebornBossCog.__init__(self, cr)
        self.goons = []
        self.goonType = 'pg'
        self.rightDoorOpen = DoorBool()
        self.leftDoorOpen = DoorBool()
        self.ceoDialogueSeq = None
        self.bossIndex = 3
        self.moveTrack = None
        self.speedDamage = 0
        self.maxSpeedDamage = ToontownGlobals.BossbotMaxSpeedDamage
        self.speedRecoverRate = 0
        self.speedRecoverStartTime = 0
        self.numAttacks = 0
        self.chandelierIndex = 0
        self.bossDamage = 0
        self.bossMaxDamage = 2652
        self.openPodiumDoorsIval = None
        self.targetNodePath = None
        self.bossClub = None
        self.rightHandJoint = None
        self.closeBubbleNode = None
        self.closeBubbleNodePath = None
        self.closeHandler = None
        self.treads = None
        self.moveBossTaskName = None
        self.swingClubSfx = None
        self.attackCode = None
        self.attackAvId = None
        self.ballLaunch = None
        self.distanceToTravel = None
        self.toPos = None
        self.fromPos = None
        self.dirVector = None

    def announceGenerate(self):
        DistributedRebornBossCog.announceGenerate(self)
        target = CollisionTube(0, -1, 4, 0, -1, 9, 3.5)
        targetNode = CollisionNode('CEOTarget')
        targetNode.addSolid(target)
        targetNode.setCollideMask(ToontownGlobals.PieBitmask)
        self.targetNodePath = self.pelvis.attachNewNode(targetNode)
        self.bossClub = loader.loadModel('phase_12/models/char/bossbotBoss-golfclub')
        self.rightHandJoint = self.find('**/joint17')
        closeBubble = CollisionSphere(0, 0, 0, 10)
        closeBubble.setTangible(0)
        closeTop = CollisionSphere(0, 0, 25, 4)
        closeTop.setTangible(0)
        closeBubbleNode = CollisionNode('CloseBoss')
        closeBubbleNode.setIntoCollideMask(BitMask32(0))
        closeBubbleNode.setFromCollideMask(ToontownGlobals.BanquetTableBitmask)
        closeBubbleNode.addSolid(closeBubble)
        closeBubbleNode.addSolid(closeTop)
        self.closeBubbleNode = closeBubbleNode
        self.closeHandler = CollisionHandlerEvent()
        self.closeHandler.addInPattern('closeEnter')
        self.closeHandler.addOutPattern('closeExit')
        self.closeBubbleNodePath = self.attachNewNode(closeBubbleNode)
        base.cTrav.addCollider(self.closeBubbleNodePath, self.closeHandler)
        self.accept('closeEnter', self.closeEnter)
        self.accept('closeExit', self.closeExit)
        self.treads = self.find('**/treads')
        self.moveBossTaskName = 'CEOMoveTask'
        self.warningSfx = loader.loadSfx('phase_9/audio/sfx/Boss_COG_VO_grunt.ogg')
        self.swingClubSfx = loader.loadSfx('phase_5/audio/sfx/SA_hardball.ogg')

    def disable(self):
        DistributedRebornBossCog.disable(self)
        render.clearTag('pieCode')
        self.targetNodePath.detachNode()
        if self.bossClub:
            self.bossClub.removeNode()
        self.bossClub = None
        if self.closeBubbleNodePath:
            base.cTrav.removeCollider(self.closeBubbleNodePath)
        self.closeHandler = None
        if self.openPodiumDoorsIval:
            self.openPodiumDoorsIval.finish()
        self.openPodiumDoorsIval = None
        if self.ceoDialogueSeq:
            self.ceoDialogueSeq.finish()
        self.ceoDialogueSeq = None
        self.ignoreAll()
        self.removeAllTasks()
        return

    def setAttackCode(self, attackCode, avId=0):
        DistributedRebornBossCog.setAttackCode(self, attackCode, avId)
        self.numAttacks += 1
        self.notify.debug('numAttacks=%d' % self.numAttacks)
        self.attackCode = attackCode
        self.attackAvId = avId
        if attackCode == ToontownGlobals.BossCogMoveAttack:
            self.interruptMove()
            self.doMoveAttack(avId)
        elif attackCode == ToontownGlobals.BossCogGolfAttack:
            self.interruptMove()
            self.cleanupAttacks()
            self.doGolfAttack(avId, attackCode)
        elif attackCode == ToontownGlobals.BossCogDirectedAttack or attackCode == ToontownGlobals.BossCogSlowDirectedAttack or attackCode == ToontownGlobals.BossCogGearDirectedAttack:
            self.interruptMove()
            self.setDizzy(0)
            self.doDirectedAttack(avId, attackCode)
        elif attackCode == ToontownGlobals.BossCogGolfAreaAttack:
            self.interruptMove()
            self.setDizzy(0)
            self.doGolfAreaAttack()
        return

    def getGolfBall(self):
        golfRoot = NodePath('golfRoot')
        golfBall = loader.loadModel('phase_6/models/golf/golf_ball')
        golfBall.setColorScale(0.75, 0.75, 0.75, 0.5)
        golfBall.setTransparency(1)
        ballScale = 5
        golfBall.setScale(ballScale)
        golfBall.reparentTo(golfRoot)
        cs = CollisionSphere(0, 0, 0, ballScale * 0.25)
        cs.setTangible(0)
        cn = CollisionNode('BossZap')
        cn.addSolid(cs)
        cn.setIntoCollideMask(ToontownGlobals.WallBitmask)
        golfRoot.attachNewNode(cn)
        return golfRoot

    def doGolfAttack(self, avId, attackCode):
        toon = base.cr.doId2do.get(avId)
        if toon:
            distance = toon.getDistance(self)
            self.notify.debug('distance = %s' % distance)
            gearRoot = self.rotateNode.attachNewNode('gearRoot-atk%d' % self.numAttacks)
            gearRoot.setZ(10)
            gearRoot.setTag('attackCode', str(attackCode))
            gearModel = self.getGolfBall()
            self.ballLaunch = NodePath('ballLaunch')
            self.ballLaunch.reparentTo(gearRoot)
            self.ballLaunch.setPos(self.BallLaunchOffset)
            gearRoot.headsUp(toon)
            toToonH = PythonUtil.fitDestAngle2Src(0, gearRoot.getH() + 180)
            gearRoot.lookAt(toon)
            neutral = 'Fb_neutral'
            if not self.twoFaced:
                neutral = 'Ff_neutral'
            gearTrack = Parallel()
            for i in range(5):
                nodeName = '%s-%s' % (str(i), globalClock.getFrameTime())
                node = gearRoot.attachNewNode(nodeName)
                node.hide()
                node.reparentTo(self.ballLaunch)
                node.wrtReparentTo(gearRoot)
                distance = toon.getDistance(node)
                gearModel.instanceTo(node)
                x = random.uniform(-5, 5)
                z = random.uniform(-3, 3)
                p = random.uniform(-720, -90)
                y = distance + random.uniform(5, 15)
                if i == 2:
                    x = 0
                    z = 0
                    y = distance + 10

                def detachNode(node):
                    if not node.isEmpty():
                        node.detachNode()

                def detachNodeLater(node=node):
                    if node.isEmpty():
                        return
                    node.node().setBounds(BoundingSphere(Point3(0, 0, 0), distance * 1.5))
                    node.node().setFinal(1)
                    self.doMethodLater(0.005, detachNode, 'detach-%s-%s' % (gearRoot.getName(), node.getName()),
                                       extraArgs=[node])

                gearTrack.append(Sequence(Wait(26.0 / 24.0), Wait(i * 0.15), Func(node.show),
                                          Parallel(node.posInterval(1, Point3(x, y, z), fluid=1),
                                                   node.hprInterval(1, VBase3(0, p, 0), fluid=1)),
                                          Func(detachNodeLater)))

            if not self.raised:
                neutral1Anim = self.getAnim('down2Up')
                self.raised = 1
            else:
                neutral1Anim = ActorInterval(self, neutral, startFrame=48)
            throwAnim = self.getAnim('golf_swing')
            neutral2Anim = ActorInterval(self, neutral)
            extraAnim = Sequence()
            if attackCode == ToontownGlobals.BossCogSlowDirectedAttack:
                extraAnim = ActorInterval(self, neutral)

            def detachGearRoot(task, gearRoot=gearRoot):
                if not gearRoot.isEmpty():
                    gearRoot.detachNode()
                return task.done

            def detachGearRootLater(gearRoot=gearRoot):
                self.doMethodLater(0.01, detachGearRoot, 'detach-%s' % gearRoot.getName())

            seq = Sequence(ParallelEndTogether(self.pelvis.hprInterval(1, VBase3(toToonH, 0, 0)), neutral1Anim),
                           extraAnim, Parallel(Sequence(Wait(0.19), gearTrack, Func(detachGearRootLater),
                                                        self.pelvis.hprInterval(0.2, VBase3(0, 0, 0))),
                                               Sequence(throwAnim, neutral2Anim), Sequence(Wait(0.85), SoundInterval(
                        self.swingClubSfx, node=self, duration=0.45, cutOff=300, listenerNode=base.localAvatar))))
            self.doAnimate(seq, now=1, raised=1)

    def doGolfAreaAttack(self):
        toons = []
        for toonId in self.bossBattle.involvedToons:
            toon = base.cr.doId2do.get(toonId)
            if toon:
                toons.append(toon)

        if not toons:
            return
        neutral = 'Fb_neutral'
        if not self.twoFaced:
            neutral = 'Ff_neutral'
        if not self.raised:
            neutral1Anim = self.getAnim('down2Up')
            self.raised = 1
        else:
            neutral1Anim = ActorInterval(self, neutral, startFrame=48)
        throwAnim = self.getAnim('golf_swing')
        neutral2Anim = ActorInterval(self, neutral)
        extraAnim = Sequence()
        if False:
            extraAnim = ActorInterval(self, neutral)
        gearModel = self.getGolfBall()
        toToonH = self.rotateNode.getH() + 360
        self.notify.debug('toToonH = %s' % toToonH)
        gearRoots = []
        allGearTracks = Parallel()
        for toon in toons:
            gearRoot = self.rotateNode.attachNewNode('gearRoot-atk%d-%d' % (self.numAttacks, toons.index(toon)))
            gearRoot.setZ(10)
            gearRoot.setTag('attackCode', str(ToontownGlobals.BossCogGolfAreaAttack))
            gearRoot.lookAt(toon)
            ballLaunch = NodePath('ballLaunch')
            ballLaunch.reparentTo(gearRoot)
            ballLaunch.setPos(self.BallLaunchOffset)
            gearTrack = Parallel()
            for i in range(5):
                nodeName = '%s-%s' % (str(i), globalClock.getFrameTime())
                node = gearRoot.attachNewNode(nodeName)
                node.hide()
                node.reparentTo(ballLaunch)
                node.wrtReparentTo(gearRoot)
                distance = toon.getDistance(node)
                gearModel.instanceTo(node)
                x = random.uniform(-5, 5)
                z = random.uniform(-3, 3)
                p = random.uniform(-720, -90)
                y = distance + random.uniform(5, 15)
                if i == 2:
                    x = 0
                    z = 0
                    y = distance + 10

                def detachNode(node):
                    if not node.isEmpty():
                        node.detachNode()

                def detachNodeLater(node=node):
                    if node.isEmpty():
                        return
                    node.node().setBounds(BoundingSphere(Point3(0, 0, 0), distance * 1.5))
                    node.node().setFinal(1)
                    self.doMethodLater(0.005, detachNode, 'detach-%s-%s' % (gearRoot.getName(), node.getName()),
                                       extraArgs=[node])

                gearTrack.append(Sequence(Wait(26.0 / 24.0), Wait(i * 0.15), Func(node.show),
                                          Parallel(node.posInterval(1, Point3(x, y, z), fluid=1),
                                                   node.hprInterval(1, VBase3(0, p, 0), fluid=1)),
                                          Func(detachNodeLater)))

            allGearTracks.append(gearTrack)

        def detachGearRoots(gearRoots=gearRoots):
            for gearRoot in gearRoots:

                def detachGearRoot(task, gearRoot=gearRoot):
                    if not gearRoot.isEmpty():
                        gearRoot.detachNode()
                    return task.done

                if gearRoot.isEmpty():
                    continue
                self.doMethodLater(0.01, detachGearRoot, 'detach-%s' % gearRoot.getName())

        rotateFire = Parallel(self.pelvis.hprInterval(2, VBase3(toToonH + 1440, 0, 0)), allGearTracks)
        seq = Sequence(Func(base.playSfx, self.warningSfx), Func(self.saySomething, TTLocalizer.GolfAreaAttackTaunt),
                       ParallelEndTogether(self.pelvis.hprInterval(2, VBase3(toToonH, 0, 0)), neutral1Anim), extraAnim,
                       Parallel(Sequence(rotateFire, Func(detachGearRoots), Func(self.pelvis.setHpr, VBase3(0, 0, 0))),
                                Sequence(throwAnim, neutral2Anim), Sequence(Wait(0.85),
                                                                            SoundInterval(self.swingClubSfx, node=self,
                                                                                          duration=0.45, cutOff=300,
                                                                                          listenerNode=base.localAvatar))))
        self.doAnimate(seq, now=1, raised=1)

    def saySomething(self, chatString):
        intervalName = 'CEOTaunt'
        seq = Sequence(name=intervalName)
        seq.append(Func(self.setChatAbsolute, chatString, CFSpeech))
        seq.append(Wait(4.0))
        seq.append(Func(self.clearChat))
        oldSeq = self.activeIntervals.get(intervalName)
        if oldSeq:
            oldSeq.finish()
        seq.start()
        self.activeIntervals[intervalName] = seq

    def togglePodiumDoors(self, state, side):
        if side == 'right':
            currentDoor = self.rightDoorOpen
        elif side == 'left':
            currentDoor = self.leftDoorOpen

        if state:
            if not currentDoor.doorBool:
                self.openPodiumDoors(side)
        currentDoor.doorBool = state

    def openPodiumDoors(self, side):
        podiumHatches = render.find('**/CEOdoor_%s' % side)
        self.openPodiumDoorsIval = Sequence(
            podiumHatches.posInterval(2, (0, 0, 7.5)),
            Wait(2),
            podiumHatches.posInterval(2, (0, 0, 0)),
            Func(self.togglePodiumDoors, False, side)
        )
        self.openPodiumDoorsIval.start()

    def announceRandomDialogue(self):
        self.setChatAbsolute(random.choice(FourBossBattleGlobals.GeneralCEOPhrases), CFSpeech | CFTimeout)

    def beginBattleTwo(self):
        self.ceoDialogueSeq = Sequence(Wait(3), Func(self.announceRandomDialogue), Wait(9))
        self.ceoDialogueSeq.loop()

    def beginFinalBattle(self):
        self.generateHealthBar()
        self.updateHealthBar()

    def interruptMove(self):
        if self.moveTrack and self.moveTrack.isPlaying():
            self.moveTrack.pause()
        self.stopMoveTask()

    def stopMoveTask(self):
        taskMgr.remove(self.moveBossTaskName)

    def doMoveAttack(self, chandelierIndex):
        self.chandelierIndex = chandelierIndex
        chandelier = self.bossBattle.chandeliers[chandelierIndex]
        fromPos = self.getPos()
        fromHpr = self.getHpr()
        toPos = chandelier.trampoline.getPos()
        foo = render.attachNewNode('foo')
        foo.setPos(self.getPos())
        foo.setHpr(self.getHpr())
        foo.lookAt(chandelier.getLocator())
        toHpr = foo.getHpr()
        toHpr.setX(toHpr.getX() - 180)
        foo.removeNode()
        moveTrack, hpr = self.moveBossToPoint(fromPos, fromHpr, toPos, toHpr)
        self.moveTrack = moveTrack
        self.moveTrack.start()
        self.storeInterval(self.moveTrack, 'moveTrack')

    def getSpeedDamage(self):
        now = globalClock.getFrameTime()
        elapsed = now - self.speedRecoverStartTime
        return max(self.speedDamage - self.speedRecoverRate * elapsed / 60.0, 0)

    def getFractionalSpeedDamage(self):
        result = self.getSpeedDamage() / self.maxSpeedDamage
        return result

    def moveBossToPoint(self, fromPos, fromHpr, toPos, toHpr):
        vector = Vec3(toPos - fromPos)
        distance = vector.length()
        self.distanceToTravel = distance
        self.notify.debug('self.distanceToTravel = %s' % self.distanceToTravel)
        if toHpr is None:
            mat = Mat3(0, 0, 0, 0, 0, 0, 0, 0, 0)
            headsUp(mat, vector, CSDefault)
            scale = VBase3(0, 0, 0)
            shear = VBase3(0, 0, 0)
            toHpr = VBase3(0, 0, 0)
            decomposeMatrix(mat, scale, shear, toHpr, CSDefault)
        if fromHpr:
            newH = PythonUtil.fitDestAngle2Src(fromHpr[0], toHpr[0])
            toHpr = VBase3(newH, 0, 0)
        else:
            fromHpr = toHpr
        turnTime = abs(toHpr[0] - fromHpr[0]) / self.getCurTurnSpeed()
        if toHpr[0] < fromHpr[0]:
            leftRate = ToontownGlobals.BossCogTreadSpeed
        else:
            leftRate = -ToontownGlobals.BossCogTreadSpeed
        self.toPos = toPos
        self.fromPos = fromPos
        self.dirVector = self.toPos - self.fromPos
        self.dirVector.normalize()
        track = Sequence(Func(self.setPos, fromPos), Func(self.headsUp, toPos),
                         Parallel(self.hprInterval(turnTime, toHpr, fromHpr), self.rollLeftTreads(turnTime, leftRate),
                                  self.rollRightTreads(turnTime, -leftRate)), Func(self.startMoveTask))
        return track, toHpr

    def getCurTurnSpeed(self):
        result = ToontownGlobals.BossbotTurnSpeedMax - (
                ToontownGlobals.BossbotTurnSpeedMax - ToontownGlobals.BossbotTurnSpeedMin) * self.getFractionalSpeedDamage()
        return result

    def getCurRollSpeed(self):
        result = ToontownGlobals.BossbotRollSpeedMax - (
                ToontownGlobals.BossbotRollSpeedMax - ToontownGlobals.BossbotRollSpeedMin) * self.getFractionalSpeedDamage()
        return result

    def getCurTreadSpeed(self):
        result = ToontownGlobals.BossbotTreadSpeedMax - (
                ToontownGlobals.BossbotTreadSpeedMax - ToontownGlobals.BossbotTreadSpeedMin) * self.getFractionalSpeedDamage()
        return result

    def startMoveTask(self):
        taskMgr.add(self.moveBossTask, self.moveBossTaskName)

    def moveBossTask(self, task):
        dt = globalClock.getDt()
        distanceTravelledThisFrame = dt * self.getCurRollSpeed()
        diff = self.toPos - self.getPos()
        distanceLeft = diff.length()

        def rollTexMatrix(t, object=object):
            object.setTexOffset(TextureStage.getDefault(), t, 0)

        self.treadsLeftPos += dt * self.getCurTreadSpeed()
        self.treadsRightPos += dt * self.getCurTreadSpeed()
        rollTexMatrix(self.treadsLeftPos, self.treadsLeft)
        rollTexMatrix(self.treadsRightPos, self.treadsRight)
        if distanceTravelledThisFrame >= distanceLeft:
            self.setPos(self.toPos)
            self.signalAtChandelier()
            return task.done
        else:
            newPos = self.getPos() + self.dirVector * dt * self.getCurRollSpeed()
            self.setPos(newPos)
            return task.cont

    def signalAtChandelier(self):
        self.sendUpdate('reachedChandelier', [self.chandelierIndex])

    def closeEnter(self, colEntry):
        chandelierStr = colEntry.getIntoNodePath().getNetTag('chandelierIndex')
        if chandelierStr:
            chandelierIndex = int(chandelierStr)
            self.sendUpdate('hitChandelier', [chandelierIndex])

        chandelierHitStr = colEntry.getIntoNodePath().getNetTag('chandelierHit')
        if chandelierHitStr:
            chandelierIndex = int(chandelierHitStr)
            chandelier = self.bossBattle.chandeliers[chandelierIndex]
            if chandelier.avId == localAvatar.doId:
                self.sendUpdate('hitByChandelier', [chandelierIndex])

    def closeExit(self, colEntry):
        chandelierStr = colEntry.getIntoNodePath().getNetTag('chandelierIndex')
        if chandelierStr:
            chandelierIndex = int(chandelierStr)
            if self.chandelierIndex != chandelierIndex:
                self.sendUpdate('awayFromChandelier', [chandelierIndex])

    def setBossDamage(self, bossDamage):
        self.flashRed()
        self.showHpText(-(bossDamage - self.bossDamage), scale=5)
        self.bossDamage = bossDamage
        self.updateHealthBar()
