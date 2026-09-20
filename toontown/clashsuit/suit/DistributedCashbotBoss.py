from toontown.gui.game.condition import ConditionGlobals
from toontown.toonbase.GlobalCacheData import GlobalCacheKey
from toontown.clashsuit.suit import BossCogGlobals
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from direct.fsm import FSM
from direct.interval.IntervalGlobal import *
from direct.task.Task import Task
from direct.task.TaskManagerGlobal import *
import math
from panda3d.core import *
from panda3d.direct import *
from panda3d.physics import *
import random
from direct.gui.DirectGui import *
from toontown.chat.constants.ChatGlobals import CFSpeech
from toontown.nametag import NametagGlobals

from toontown.clashsuit.suit import DistributedBossCog
from toontown.clashsuit.suit import DistributedCashbotBossGoon
from toontown.clashsuit.suit import SuitDNA
from toontown.clashsuit.suit import SuitHealthMeter
from toontown.clashbattle.battle import MovieToonVictory, BattleGlobals
from toontown.clashbattle.battle import RewardPanel
from toontown.building import ElevatorConstants
from toontown.building import ElevatorUtils
from toontown.coghq import CogDisguiseGlobals
from toontown.distributed import DelayDelete
from otp import *
from toontown.toon.npc import NPCToons
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownGlobals
from toontown.gui import DepartmentExperienceBar
from functools import cmp_to_key

OneBossCog = None
TTL = TTLocalizer


@DirectNotifyCategory()
class DistributedCashbotBoss(DistributedBossCog.DistributedBossCog, FSM.FSM):
    numFakeGoons = 3

    def __init__(self, cr):
        DistributedBossCog.DistributedBossCog.__init__(self, cr)
        FSM.FSM.__init__(self, 'DistributedCashbotBoss')
        self.resistanceToon = None
        self.resistanceToonOnstage = 0
        self.cranes = {}
        self.safes = {}
        self.goons = []
        self.bossMaxDamage = BossCogGlobals.CashbotBossMaxDamage[0]
        self.elevatorType = ElevatorConstants.ELEVATOR_CFO
        self.departmentExpBar = None
        self.numCounterfeitsEarned = {}

    def announceGenerate(self):
        """
        Handle all required fields having been filled in.
        """
        base.globalCache.swapToKey(GlobalCacheKey.CashbotBoss)

        DistributedBossCog.DistributedBossCog.announceGenerate(self)
        base.cr.forbidCheesyEffects(1)
        nameInfo = TTLocalizer.BossCogNameWithDept % {'name': TTLocalizer.CashbotBossName,
         'dept': SuitDNA.getDeptFullname(self.style.dept)}
        self.setName(TTLocalizer.CashbotBossName,)
        self.healthGui.setBossName(TTLocalizer.CashbotBossName)
        self.setDisplayName(nameInfo)
        target = CollisionSphere(2, 0, 0, 3)
        targetNode = CollisionNode('headTarget')
        targetNode.addSolid(target)
        targetNode.setCollideMask(ToontownGlobals.PieBitmask)
        self.headTarget = self.neck.attachNewNode(targetNode)
        shield = CollisionSphere(0, 0, 0.8, 7)
        shieldNode = CollisionNode('shield')
        shieldNode.addSolid(shield)
        shieldNode.setCollideMask(ToontownGlobals.PieBitmask)
        self.pelvis.attachNewNode(shieldNode)
        self.heldObject = None
        self.bossDamage = 0
        self.attackThreshold = 0.25
        self.loadEnvironment()
        self.__makeResistanceToon()
        self.physicsMgr = PhysicsManager()
        integrator = LinearEulerIntegrator()
        self.physicsMgr.attachLinearIntegrator(integrator)
        fn = ForceNode('gravity')
        self.fnp = self.geom.attachNewNode(fn)
        gravity = LinearVectorForce(0, 0, -32)
        fn.addForce(gravity)
        self.physicsMgr.addLinearForce(gravity)
        base.localAvatar.chatContainer.speedChatMenu.addCFOMenu()
        global OneBossCog
        if OneBossCog is not None:
            self.notify.warning('Multiple BossCogs visible.')
        OneBossCog = self
        return

    # override collision setup to prevent the MacOS crash triggered by a CashbotBossObject colliding with a CollisionPolygon
    def setupDoorA(self, jointName, name, callback, openedHpr, closedHpr):
        cSolid = CollisionBox(Point3(5, -4, 0.32), Point3(0, 4, 0))
        return self.setupDoor(jointName, name, callback, openedHpr, closedHpr, cSolid)

    def setupDoorB(self, jointName, name, callback, openedHpr, closedHpr):
        cSolid = CollisionBox(Point3(-5, 4, 0.84), Point3(0, -4, 0))
        return self.setupDoor(jointName, name, callback, openedHpr, closedHpr, cSolid)

    def setupCollisions(self):
        self.collNode.removeSolid(0)
        capsule1 = CollisionCapsule(6.5, -7.5, 2, 6.5, 7.5, 2, 2.5)
        capsule2 = CollisionCapsule(-6.5, -7.5, 2, -6.5, 7.5, 2, 2.5)
        box = CollisionBox(Point3(0, 0, 0), 4.4, 7.1, 5.5)
        self.collNode.addSolid(capsule1)
        self.collNode.addSolid(capsule2)
        self.collNode.addSolid(box)
        self.collNodePath.reparentTo(self.axle)
        self.collNode.setCollideMask(ToontownGlobals.PieBitmask | ToontownGlobals.WallBitmask | ToontownGlobals.CameraBitmask)
        self.collNode.setName('BossZap')

    def disable(self):
        """
        Called when the DistributedObject is removed from active duty and stored in a cache.
        """
        global OneBossCog
        DistributedBossCog.DistributedBossCog.disable(self)
        base.cr.forbidCheesyEffects(0)
        self.demand('Off')
        self.unloadEnvironment()
        self.__cleanupResistanceToon()
        self.fnp.removeNode()
        self.physicsMgr.clearLinearForces()
        base.musicMgr.stopMusic()
        base.localAvatar.chatContainer.speedChatMenu.removeCFOMenu()
        if OneBossCog == self:
            OneBossCog = None

    def __makeResistanceToon(self):
        if self.resistanceToon:
            return
        self.resistanceToon = NPCToons.createLocalNPC(2008)
        self.resistanceToon.addActive()
        self.resistanceToon.request('Neutral')
        self.resistanceToon.setPosHpr(*BossCogGlobals.CashbotRTBattleOneStartPosHpr)
        state = random.getstate()
        random.seed(self.doId)
        self.resistanceToon.suitType = SuitDNA.getRandomSuitByDept('m')
        self.resistanceToon.setName(TTLocalizer.ResistanceToonName)
        self.resistanceToon.setDisplayName(TTLocalizer.ResistanceToonName)
        random.setstate(state)
        self.fakeGoons = []
        for i in range(self.numFakeGoons):
            goon = DistributedCashbotBossGoon.DistributedCashbotBossGoon(base.cr)
            goon.doId = -1 - i
            goon.setBossCogId(self.doId)
            goon.generate()
            goon.announceGenerate()
            self.fakeGoons.append(goon)

        self.__hideFakeGoons()

    def __cleanupResistanceToon(self):
        self.__hideResistanceToon()
        if self.resistanceToon:
            self.resistanceToon.removeActive()
            self.resistanceToon.delete()
            self.resistanceToon = None
            for i in range(self.numFakeGoons):
                self.fakeGoons[i].disable()
                self.fakeGoons[i].delete()
                self.fakeGoons[i] = None

        return

    def __showResistanceToon(self, withSuit):
        if not self.resistanceToonOnstage:
            self.resistanceToon.addActive()
            self.resistanceToon.reparentTo(self.geom)
            self.resistanceToonOnstage = 1
        if withSuit:
            suit = self.resistanceToon.suitType
            self.resistanceToon.putOnSuit(suit, False)
        else:
            self.resistanceToon.takeOffSuit()

    def __hideResistanceToon(self):
        if self.resistanceToonOnstage:
            self.resistanceToon.removeActive()
            self.resistanceToon.detachNode()
            self.resistanceToonOnstage = 0

    def __hideFakeGoons(self):
        if self.fakeGoons:
            for goon in self.fakeGoons:
                goon.request('Off')

    def __showFakeGoons(self, state):
        if self.fakeGoons:
            for goon in self.fakeGoons:
                goon.request(state)

    def loadEnvironment(self):
        DistributedBossCog.DistributedBossCog.loadEnvironment(self)
        self.midVault = loader.loadModel('phase_10/models/cogHQ/MidVault.bam')
        self.endVault = loader.loadModel('phase_10/models/cogHQ/EndVault.bam')
        self.lightning = loader.loadModel('phase_10/models/cogHQ/CBLightning.bam')
        self.craneArm = loader.loadModel('phase_10/models/cogHQ/CBCraneArm.bam')
        self.controls = loader.loadModel('phase_10/models/cogHQ/CBCraneControls.bam')
        self.stick = loader.loadModel('phase_10/models/cogHQ/CBCraneStick.bam')
        self.safe = loader.loadModel('phase_10/models/cogHQ/CBSafe.bam')
        self.eyes = loader.loadModel('phase_10/models/cogHQ/CashBotBossEyes.bam')
        self.cableTex = self.craneArm.findTexture('MagnetControl')
        self.eyes.setPosHprScale(4.5, 0, -2.5, 90, 90, 0, 0.4, 0.4, 0.4)
        self.eyes.reparentTo(self.neck)
        self.eyes.hide()
        self.midVault.setPos(0, -222, -70.7)
        self.endVault.setPos(84, -201, -6)
        self.geom = NodePath('geom')
        self.midVault.reparentTo(self.geom)
        self.endVault.reparentTo(self.geom)
        self.endVault.findAllMatches('**/MagnetArms').detach()
        self.endVault.findAllMatches('**/Safes').detach()
        self.endVault.findAllMatches('**/MagnetControlsAll').detach()
        cn = self.endVault.find('**/wallsCollision').node()
        cn.setIntoCollideMask(ToontownGlobals.WallBitmask | ToontownGlobals.PieBitmask)
        self.door1 = self.midVault.find('**/SlidingDoor1/')
        self.door2 = self.midVault.find('**/SlidingDoor/')
        self.door3 = self.endVault.find('**/SlidingDoor/')
        elevatorModel = loader.loadModel('phase_10/models/cogHQ/CFOElevator')
        elevatorOrigin = self.midVault.find('**/elevator_origin')
        elevatorOrigin.setScale(1)
        elevatorModel.reparentTo(elevatorOrigin)
        leftDoor = elevatorModel.find('**/left_door')
        leftDoor.setName('left-door')
        rightDoor = elevatorModel.find('**/right_door')
        rightDoor.setName('right-door')
        self.setupElevator(elevatorOrigin)
        ElevatorUtils.closeDoors(leftDoor, rightDoor, ElevatorConstants.ELEVATOR_CFO)
        walls = self.endVault.find('**/RollUpFrameCillison')
        walls.detachNode()
        self.evWalls = self.replaceCollisionPolysWithPlanes(walls)
        self.evWalls.reparentTo(self.endVault)
        self.evWalls.stash()
        floor = self.endVault.find('**/EndVaultFloorCollision')
        floor.detachNode()
        self.evFloor = self.replaceCollisionPolysWithPlanes(floor)
        self.evFloor.reparentTo(self.endVault)
        self.evFloor.setName('floor')
        plane = CollisionPlane(Plane(Vec3(0, 0, 1), Point3(0, 0, -50)))
        planeNode = CollisionNode('dropPlane')
        planeNode.addSolid(plane)
        planeNode.setCollideMask(ToontownGlobals.PieBitmask)
        self.geom.attachNewNode(planeNode)
        self.geom.reparentTo(render)
        self.elevatorMusic = 'cfo_elevator'
        self.battleOneMusic = 'cfo_battle_one'
        self.battleTwoMusic = 'cfo_battle_two'
        self.battleThreeMusic = 'cfo_battle_three'
        self.battleThreeDizzyMusic = 'cfo_battle_three_stunned'
        self.killMusic = 'cfo_battle_stinger'
        self.victoryMusic = 'cfo_victory'
        self.epilogueMusic = 'cfo_epilogue'
        self.introCutsceneMusic = 'cfo_intro_cutscene'
        self.midCutsceneMusic = 'cfo_flee_cutscene'
        self.finalCutsceneMusic = 'cfo_crane_cutscene'
        self.preloadFinalBattleMusic()

    def unloadEnvironment(self):
        DistributedBossCog.DistributedBossCog.unloadEnvironment(self)
        self.geom.removeNode()

    def replaceCollisionPolysWithPlanes(self, model):
        newCollisionNode = CollisionNode('collisions')
        newCollideMask = BitMask32(0)
        planes = []
        collList = model.findAllMatches('**/+CollisionNode')
        if not collList:
            collList = [model]
        for cnp in collList:
            cn = cnp.node()
            if not isinstance(cn, CollisionNode):
                self.notify.warning('Not a collision node: %s' % repr(cnp))
                break
            newCollideMask = newCollideMask | cn.getIntoCollideMask()
            for i in range(cn.getNumSolids()):
                solid = cn.getSolid(i)
                if isinstance(solid, CollisionPolygon):
                    plane = Plane(solid.getPlane())
                    planes.append(plane)
                else:
                    self.notify.warning('Unexpected collision solid: %s' % repr(solid))
                    newCollisionNode.addSolid(plane)

        newCollisionNode.setIntoCollideMask(newCollideMask)
        threshold = 0.1
        planes.sort(key=cmp_to_key(lambda p1, p2: p1.compareTo(p2, threshold)))
        lastPlane = None
        for plane in planes:
            if lastPlane is None or plane.compareTo(lastPlane, threshold) != 0:
                cp = CollisionPlane(plane)
                newCollisionNode.addSolid(cp)
                lastPlane = plane

        return NodePath(newCollisionNode)

    def __makeGoonMovieForIntro(self):
        goonTrack = Parallel()
        goon = self.fakeGoons[0]
        goonTrack.append(Sequence(
            goon.posHprInterval(0, Point3(111, -287, 0), VBase3(165, 0, 0)),
            goon.posHprInterval(10, Point3(101, -323, 0), VBase3(165, 0, 0)),
            goon.hprInterval(1, VBase3(345, 0, 0)),
            goon.posHprInterval(10, Point3(111, -287, 0), VBase3(345, 0, 0)),
            goon.hprInterval(1, VBase3(165, 0, 0)),
            goon.posHprInterval(11.5, Point3(104, -316, 0), VBase3(165, 0, 0)),
            Func(goon.request, 'Stunned'),
            Wait(0.6)))
        goon = self.fakeGoons[1]
        goonTrack.append(Sequence(
            goon.posHprInterval(0, Point3(119, -315, 0), VBase3(357, 0, 0)),
            goon.posHprInterval(10, Point3(121, -280, 0), VBase3(357, 0, 0)),
            goon.hprInterval(.5, VBase3(-345, 145, 345)),
            goon.hprInterval(1, VBase3(177, 0, 0)),
            goon.posHprInterval(10, Point3(119, -315, 0), VBase3(177, 0, 0)),
            goon.hprInterval(1, VBase3(357, 0, 0)),
            goon.posHprInterval(9, Point3(121, -280, 0), VBase3(357, 0, 0)),
            goon.hprInterval(1.7, VBase3(210, 0, 0)),
            goon.posHprInterval(1, Point3(122, -285, 0), VBase3(210, 0, 0)),
        ))
        goon = self.fakeGoons[2]
        goonTrack.append(Sequence(
            goon.posHprInterval(0, Point3(102, -320, 0), VBase3(231, 0, 0)),
            goon.posHprInterval(10, Point3(127, -337, 0), VBase3(231, 0, 0)),
            goon.hprInterval(1, VBase3(51, 0, 0)),
            goon.posHprInterval(10, Point3(102, -320, 0), VBase3(51, 0, 0)),
            goon.hprInterval(1, VBase3(231, 0, 0)),
            goon.posHprInterval(11, Point3(127, -337, 0), VBase3(231, 0, 0))))
        return Sequence(Func(self.__showFakeGoons, 'Walk'), goonTrack, Func(self.__hideFakeGoons))

    def makeIntroductionMovie(self, delayDeletes):
        for toonId in self.involvedToons:
            toon = self.cr.doId2do.get(toonId)
            if toon:
                delayDeletes.append(DelayDelete.DelayDelete(toon, 'CashbotBoss.makeIntroductionMovie'))

        # rtTrack = Sequence()
        startPos = Point3(BossCogGlobals.CashbotBossOffstagePosHpr[0], BossCogGlobals.CashbotBossOffstagePosHpr[1], BossCogGlobals.CashbotBossOffstagePosHpr[2])
        battlePos = Point3(BossCogGlobals.CashbotBossBattleOnePosHpr[0], BossCogGlobals.CashbotBossBattleOnePosHpr[1], BossCogGlobals.CashbotBossBattleOnePosHpr[2])
        battleHpr = VBase3(BossCogGlobals.CashbotBossBattleOnePosHpr[3], BossCogGlobals.CashbotBossBattleOnePosHpr[4], BossCogGlobals.CashbotBossBattleOnePosHpr[5])
        bossTrack = Sequence()
        bossTrack.append(Func(self.reparentTo, render))
        bossTrack.append(Func(self.getGeomNode().setH, 180))
        bossTrack.append(Func(self.pelvis.setHpr, self.pelvisForwardHpr))
        bossTrack.append(Func(self.loop, 'Ff_neutral'))
        track, hpr = self.rollBossToPoint(startPos, None, battlePos, None, 0)
        bossTrack.append(track)
        track, hpr = self.rollBossToPoint(battlePos, hpr, battlePos, battleHpr, 0)
        bossTrack.append(track)
        bossTrack.append(Func(self.getGeomNode().setH, 0))
        bossTrack.append(Func(self.pelvis.setHpr, self.pelvisReversedHpr))
        goonTrack = self.__makeGoonMovieForIntro()
        attackToons = TTL.CashbotBossCogAttack

        rToon = self.resistanceToon
        rToon.setPosHpr(*BossCogGlobals.CashbotRTBattleOneStartPosHpr)
        self.notify.debug(f"Resistance Toon height: {rToon.getHeight()}")
        track = Sequence(
            #Func(base.camera.setPosHpr, 82, -219, 5, 267, 0, 0),
            base.camera.posHprInterval(1, Point3(82, -219, max(rToon.getHeight() + 0.5, 4)), VBase3(267, 0, 0)),    # set the height part to the rToon's suit height + a bit extra, or 5 if less than 5
            Func(rToon.setChatAbsolute, TTL.ResistanceToonWelcome, CFSpeech),
            Wait(3),
            Sequence(goonTrack, duration=0),
            Parallel(
                base.camera.posHprInterval(4, Point3(108, -241, max(rToon.getHeight() + 0.5, 4)), VBase3(211.5, 0, 0), blendType = 'easeInOut'),    # set the height part to the rToon's suit height + a bit extra, or 4 if less than 4
                Sequence(
                    Func(rToon.suit.setPlayRate, 1.4, 'walk'),
                    Func(rToon.suit.loop, 'walk'),
                    Parallel(
                        rToon.hprInterval(1, VBase3(180, 0, 0)),
                        rToon.posInterval(3, VBase3(120, -251, 0)),
                        Sequence(
                            Wait(2),
                            Func(rToon.clearChat))),
                    Func(rToon.suit.loop, 'neutral'),
                    self.door2.posInterval(3, VBase3(0, 0, 30)))),
            Func(rToon.setHpr, 0, 0, 0),
            Func(rToon.setChatAbsolute, TTL.ResistanceToonTooLate, CFSpeech),
            Func(base.camera.reparentTo, render),
            Func(base.camera.setPosHpr, 61.1, -228.8, 10.2, 270, 0, 0),
            self.door1.posInterval(2, VBase3(0, 0, 30)),
            Parallel(
                bossTrack,
                Sequence(
                    Wait(3),
                    Func(rToon.clearChat),
                    self.door1.posInterval(3, VBase3(0, 0, 0)))),
            base.camera.posHprInterval(1, Point3(93.3, -230, 0.7), VBase3(268.9, 39.7, 8.3), blendType='easeInOut'),
            Func(self.setChatAbsolute, TTL.CashbotBossDiscoverToons1, CFSpeech),
            Wait(1.5),
            Func(self.setChatAbsolute, TTL.CashbotBossDiscoverToons2, CFSpeech),
            Wait(4),
            Func(self.clearChat),
            self.loseCogSuits(self.toonsA + self.toonsB, render, (113, -228, 10, 90, 0, 0)),
            Wait(1),
            Func(rToon.setHpr, 0, 0, 0),
            self.loseCogSuits([rToon], render, (133, -239, 5, 143, 0, 0), True),
            Func(rToon.setChatAbsolute, TTL.ResistanceToonKeepHimBusy, CFSpeech),
            Wait(1),
            Func(self.__showResistanceToon, False),
            Sequence(
                Func(rToon.request, 'Run'),
                rToon.hprInterval(1, VBase3(180, 0, 0)),
                Parallel(
                    Sequence(
                        rToon.posInterval(1.5, VBase3(109, -294, 0)),
                        Parallel(Func(rToon.request, 'Jump')),
                        rToon.posInterval(1.5, VBase3(93.935, -341.065, 2))),
                    self.door2.posInterval(3, VBase3(0, 0, 0))),
                Func(rToon.request, 'Neutral')),
            self.toonNormalEyes(self.involvedToons),
            self.toonNormalEyes([self.resistanceToon], True),
            Func(rToon.clearChat),
            #Func(base.camera.setPosHpr, 93.3, -230, 0.7, -92.9, 39.7, 8.3),
            base.camera.posHprInterval(2, Point3(93.3, -230, 0.7), VBase3(268.9, 39.7, 8.3), blendType='easeInOut'),
            Func(self.setChatAbsolute, attackToons, CFSpeech),
            Wait(2),
            Func(self.clearChat))
        return Sequence(Func(base.camera.reparentTo, render), track)

    def makePrepareBattleTwoMovie(self, delayDeletes):
        for toonId in self.involvedToons:
            toon = self.cr.doId2do.get(toonId)
            if toon:
                delayDeletes.append(DelayDelete.DelayDelete(toon, 'CashbotBoss.makePrepareBattleTwoMovie'))

        startPos = Point3(BossCogGlobals.CashbotBossBattleOnePosHpr[0], BossCogGlobals.CashbotBossBattleOnePosHpr[1], BossCogGlobals.CashbotBossBattleOnePosHpr[2])
        battlePos = Point3(BossCogGlobals.CashbotBossBattleThreePosHpr[0], BossCogGlobals.CashbotBossBattleThreePosHpr[1], BossCogGlobals.CashbotBossBattleThreePosHpr[2])
        startHpr = Point3(BossCogGlobals.CashbotBossBattleOnePosHpr[3], BossCogGlobals.CashbotBossBattleOnePosHpr[4], BossCogGlobals.CashbotBossBattleOnePosHpr[5])
        battleHpr = VBase3(BossCogGlobals.CashbotBossBattleThreePosHpr[3], BossCogGlobals.CashbotBossBattleThreePosHpr[4], BossCogGlobals.CashbotBossBattleThreePosHpr[5])
        finalHpr = VBase3(135, 0, 0)
        toonPosHpr = BossCogGlobals.CashbotRTBattleTwoEndPosHpr
        bossTrack = Sequence()
        bossTrack.append(Func(self.reparentTo, render))
        bossTrack.append(Func(self.getGeomNode().setH, 180))
        bossTrack.append(Func(self.pelvis.setHpr, self.pelvisForwardHpr))
        bossTrack.append(Func(self.loop, 'Ff_neutral'))
        track, hpr = self.rollBossToPoint(startPos, startHpr, startPos, battleHpr, 0)
        bossTrack.append(track)
        track, hpr = self.rollBossToPoint(startPos, None, battlePos, None, 0)
        bossTrack.append(track)
        track, hpr = self.rollBossToPoint(battlePos, battleHpr, battlePos, finalHpr, 0)
        bossTrack.append(track)
        rToon = self.resistanceToon
        rToon.setPosHpr(*BossCogGlobals.CashbotRTBattleTwoStartPosHpr)
        self.__arrangeToonsAroundResistanceToon()
        base.musicMgr.playMusic(self.midCutsceneMusic, looping=1, volume=0.9)
        track = Sequence(
            Parallel(
                self.door2.posInterval(4.5, VBase3(0, 0, 30)),
                self.door3.posInterval(4.5, VBase3(0, 0, 30)),
                bossTrack),
            Func(self.__showResistanceToon, False),
            Func(self.__showToons),
            Wait(1),
            Func(base.camera.wrtReparentTo, render),
            Func(base.camera.setPos, Point3(120, -280, 1)),
            Func(base.camera.setHpr, Point3(0, 0, 0)),
            Func(rToon.setChatAbsolute, TTL.ResistanceToonFollowHim, CFSpeech),
            Wait(2),
            Func(rToon.setHpr, Point3(180, 0, 0)),
            Func(rToon.request, 'Run'),
            rToon.posInterval(2, Point3(toonPosHpr[0], toonPosHpr[1], toonPosHpr[2])),
            Func(rToon.request, 'Neutral'),
            self.createWalkInInterval(),
            Wait(1),
            Func(rToon.clearChat),
            Func(base.camera.wrtReparentTo, self.geom),
            base.camera.posHprInterval(1, Point3(105, -326, 20), VBase3(-45.3, 15, 0), blendType='easeInOut'),
            Parallel(
                self.door2.posInterval(4.5, VBase3(0, 0, 0)),
                self.door3.posInterval(4.5, VBase3(0, 0, 0)),
                Sequence(
                    Func(self.setChatAbsolute, TTL.CashbotBossTrapped, CFSpeech),
                    Wait(4),
                    Func(self.clearChat),
                    Func(self.setChatAbsolute, TTL.CashbotBossCogAttack, CFSpeech),
                    Wait(2),
                    Func(self.setChatAbsolute, TTL.CashbotBossCogAgain, CFSpeech),
                    Wait(2),
                    Func(self.clearChat),
                    Func(self.getGeomNode().setH, 0))))
        return Sequence(Func(base.camera.reparentTo, self), base.camera.posHprInterval(1, Point3(0, -27, 25), VBase3(0, -18, 0), blendType='easeInOut'), track, Func(base.camera.reparentTo, render))

    def createWalkInInterval(self):
        retval = Parallel()
        delay = 0
        index = 0
        for toonId in self.involvedToons[::-1]:
            toon = base.cr.doId2do.get(toonId)
            if not toon:
                continue
            destPos = Point3(132 - index * 2, -285, 0)

            def toWalk(toon):
                toon.loop('run')

            def toNeutral(toon):
                toon.loop('neutral')

            retval.append(Sequence(Wait(delay), Func(toon.wrtReparentTo, render), Func(toWalk, toon), Func(toon.headsUp, destPos), LerpPosInterval(toon, 2, destPos), Func(toon.headsUp, self), Func(toNeutral, toon)))
            if toon == base.localAvatar:
                retval.append(Sequence(Wait(delay), Func(base.camera.reparentTo, toon), Func(base.camera.setPos, 0.0, -9.0 * base.localAvatar.getClampedAvatarHeight() * 0.3333333333, base.localAvatar.getClampedAvatarHeight()), Func(base.camera.setHpr, 0, 0, 0)))
            index += 1

        return retval

    def __makeGoonMovieForBattleThree(self):
        goonPosHprs = [[Point3(111, -287, 0),
          VBase3(165, 0, 0),
          Point3(101, -323, 0),
          VBase3(165, 0, 0)], [Point3(119, -315, 0),
          VBase3(357, 0, 0),
          Point3(121, -280, 0),
          VBase3(357, 0, 0)], [Point3(102, -320, 0),
          VBase3(231, 0, 0),
          Point3(127, -337, 0),
          VBase3(231, 0, 0)]]
        mainGoon = self.fakeGoons[0]
        goonLoop = Parallel()
        for i in range(1, self.numFakeGoons):
            goon = self.fakeGoons[i]
            goonLoop.append(Sequence(goon.posHprInterval(8, goonPosHprs[i][0], goonPosHprs[i][1]), goon.posHprInterval(8, goonPosHprs[i][2], goonPosHprs[i][3])))

        goonTrack = Sequence(Func(self.__showFakeGoons, 'Walk'), Func(mainGoon.request, 'Stunned'), Func(goonLoop.loop), Wait(20))
        return goonTrack

    def makePrepareBattleThreeMovie(self, delayDeletes, crane, safe):
        for toonId in self.involvedToons:
            toon = self.cr.doId2do.get(toonId)
            if toon:
                delayDeletes.append(DelayDelete.DelayDelete(toon, 'CashbotBoss.makePrepareBattleThreeMovie'))

        startPos = Point3(BossCogGlobals.CashbotBossBattleOnePosHpr[0], BossCogGlobals.CashbotBossBattleOnePosHpr[1], BossCogGlobals.CashbotBossBattleOnePosHpr[2])
        battlePos = Point3(BossCogGlobals.CashbotBossBattleThreePosHpr[0], BossCogGlobals.CashbotBossBattleThreePosHpr[1], BossCogGlobals.CashbotBossBattleThreePosHpr[2])
        startHpr = Point3(BossCogGlobals.CashbotBossBattleOnePosHpr[3], BossCogGlobals.CashbotBossBattleOnePosHpr[4], BossCogGlobals.CashbotBossBattleOnePosHpr[5])
        battleHpr = VBase3(BossCogGlobals.CashbotBossBattleThreePosHpr[3], BossCogGlobals.CashbotBossBattleThreePosHpr[4], BossCogGlobals.CashbotBossBattleThreePosHpr[5])
        finalHpr = VBase3(135, 0, 0)
        bossTrack = Sequence()
        bossTrack.append(Func(self.reparentTo, render))
        bossTrack.append(Func(self.getGeomNode().setH, 180))
        bossTrack.append(Func(self.pelvis.setHpr, self.pelvisForwardHpr))
        bossTrack.append(Func(self.loop, 'Ff_neutral'))
        track, hpr = self.rollBossToPoint(startPos, startHpr, startPos, battleHpr, 0)
        bossTrack.append(track)
        track, hpr = self.rollBossToPoint(startPos, None, battlePos, None, 0)
        bossTrack.append(track)
        track, hpr = self.rollBossToPoint(battlePos, battleHpr, battlePos, finalHpr, 0)
        bossTrack.append(track)
        rToon = self.resistanceToon
        rToon.setPosHpr(93.935, -341.065, 0, -45, 0, 0)
        goon = self.fakeGoons[0]
        crane = self.cranes[0]
        base.musicMgr.playMusic(self.finalCutsceneMusic, looping=1, volume=0.9)
        track = Sequence(
            Func(self.__hideToons),
            Func(crane.request, 'Movie'),
            Func(crane.accomodateToon, rToon),
            Func(goon.request, 'Stunned'),
            Func(goon.setPosHpr, 104, -316, 0, 165, 0, 0),
            Func(rToon.loop, 'leverNeutral'),
            Func(base.camera.wrtReparentTo, self.geom),
            base.camera.posHprInterval(1.5, Point3(105, -326, 5), Point3(136.3, 0, 0), blendType='easeInOut'),
            Func(rToon.setChatAbsolute, TTL.ResistanceToonCraneInstructions1, CFSpeech),
            Wait(4),
            Func(rToon.setChatAbsolute, TTL.ResistanceToonCraneInstructions2 % base.JUMP.upper(), CFSpeech),
            Wait(4),
            Func(rToon.setChatAbsolute, TTL.ResistanceToonCraneInstructions3, CFSpeech),
            Wait(4),
            Func(rToon.setChatAbsolute, TTL.ResistanceToonCraneInstructions4, CFSpeech),
            Wait(4),
            Func(rToon.clearChat),
            base.camera.posHprInterval(1, Point3(102, -323.6, 0.9), VBase3(-10.6, 14, 0), blendType='easeInOut'),
            Func(goon.request, 'Recovery'),
            Wait(2),
            base.camera.posHprInterval(1, Point3(95.4, -332.6, 4.2), VBase3(167.1, -13.2, 0), blendType='easeInOut'),
            Func(rToon.setChatAbsolute, TTL.ResistanceToonGetaway, CFSpeech),
            Func(rToon.request, 'Jump'),
            Wait(1.8),
            Func(rToon.clearChat),
            base.camera.posHprInterval(1, Point3(109.1, -300.7, 13.9), VBase3(-15.6, -13.6, 0), blendType='easeInOut'),
            Func(rToon.request, 'Run'),
            Func(goon.request, 'Walk'),
            Parallel(
                Sequence(self.door3.posInterval(2, VBase3(0, 0, 30)), self.door3.posInterval(1.75, Point3(0, 0, 0))),
                rToon.posHprInterval(3, Point3(136, -212.9, 0), VBase3(-14, 0, 0), startPos=Point3(110.8, -292.7, 0), startHpr=VBase3(-14, 0, 0)),
                goon.posHprInterval(3, Point3(125.2, -243.5, 0), VBase3(-14, 0, 0), startPos=Point3(104.8, -309.5, 0), startHpr=VBase3(-14, 0, 0))),
            Func(self.__hideFakeGoons),
            Func(crane.request, 'Free'),
            Func(self.getGeomNode().setH, 0),
            self.moveToonsToBattleThreePos(self.involvedToons),
            Func(self.__showToons),
            Wait(2))
        return Sequence(Func(base.camera.reparentTo, self), base.camera.posHprInterval(1, Point3(0, -27, 25), VBase3(0, -18, 0), blendType='easeInOut'), track) #Func(base.camera.setPosHpr, 0, -27, 25, 0, -18, 0)

    def moveToonsToBattleThreePos(self, toons):
        track = Parallel()
        for i in range(len(toons)):
            toon = base.cr.doId2do.get(toons[i])
            if toon:
                posHpr = BossCogGlobals.CashbotToonsBattleThreeStartPosHpr[i]
                pos = Point3(*posHpr[0:3])
                hpr = VBase3(*posHpr[3:6])
                track.append(toon.posHprInterval(0.2, pos, hpr))

        return track

    def makeBossFleeMovie(self):
        hadEnough = TTLocalizer.CashbotBossHadEnough
        outtaHere = TTLocalizer.CashbotBossOuttaHere
        loco = loader.loadModel('phase_10/models/cogHQ/CashBotLocomotive')
        car1 = loader.loadModel('phase_10/models/cogHQ/CashBotBoxCar')
        car2 = loader.loadModel('phase_10/models/cogHQ/CashBotTankCar')
        trainPassingSfx = base.loader.loadSfx('phase_10/audio/sfx/CBHQ_TRAIN_pass.ogg')
        flattenSfx = loader.loadSfx('phase_9/audio/sfx/toon_decompress.ogg')
        rollThroughDoor = self.rollBossToPoint(fromPos=Point3(120, -280, 0), fromHpr=None, toPos=Point3(120, -250, 0), toHpr=None, reverse=0)
        rollTrack = Sequence(Func(self.getGeomNode().setH, 180), rollThroughDoor[0], Func(self.getGeomNode().setH, 0))
        g = 80.0 / 300.0
        trainTrack = Track(
            (0 * g, loco.posInterval(0.5, Point3(0, -242, 0), startPos=Point3(150, -242, 0))),
            (1 * g, car2.posInterval(0.5, Point3(0, -242, 0), startPos=Point3(150, -242, 0))),
            (2 * g, car1.posInterval(0.5, Point3(0, -242, 0), startPos=Point3(150, -242, 0))),
            (3 * g, car2.posInterval(0.5, Point3(0, -242, 0), startPos=Point3(150, -242, 0))),
            (4 * g, car1.posInterval(0.5, Point3(0, -242, 0), startPos=Point3(150, -242, 0))),
            (5 * g, car2.posInterval(0.5, Point3(0, -242, 0), startPos=Point3(150, -242, 0))),
            (6 * g, car1.posInterval(0.5, Point3(0, -242, 0), startPos=Point3(150, -242, 0))),
            (7 * g, car2.posInterval(0.5, Point3(0, -242, 0), startPos=Point3(150, -242, 0))),
            (8 * g, car1.posInterval(0.5, Point3(0, -242, 0), startPos=Point3(150, -242, 0))),
            (9 * g, car2.posInterval(0.5, Point3(0, -242, 0), startPos=Point3(150, -242, 0))),
            (10 * g, car1.posInterval(0.5, Point3(0, -242, 0), startPos=Point3(150, -242, 0))),
            (11 * g, car2.posInterval(0.5, Point3(0, -242, 0), startPos=Point3(150, -242, 0))),
            (12 * g, car1.posInterval(0.5, Point3(0, -242, 0), startPos=Point3(150, -242, 0))),
            (13 * g, car2.posInterval(0.5, Point3(0, -242, 0), startPos=Point3(150, -242, 0))),
            (14 * g, car1.posInterval(0.5, Point3(0, -242, 0), startPos=Point3(150, -242, 0))))
        bossTrack = Track(
            (0.0, Sequence(
                Func(base.camera.reparentTo, render),
                Func(base.camera.setPosHpr, 105, -280, 20, -158, -3, 0),
                Func(self.reparentTo, render),
                Func(self.show),
                Func(self.clearChat),
                Func(self.setPosHpr, *BossCogGlobals.CashbotBossBattleFleePosHpr),
                Func(self.reverseBody),
                Func(self.reverseHead),
                ActorInterval(self, 'Fb_firstHit'),
                ActorInterval(self, 'Fb_down2Up'))),
            (1.0, Func(self.setChatAbsolute, hadEnough, CFSpeech)),
            (5.5, Parallel(
                Func(self.forwardHead),
                Func(self.forwardBody),
                Func(base.camera.setPosHpr, 100, -315, 16, -20, 0, 0),
                Func(self.hideBattleThreeObjects),
                Func(self.loop, 'Ff_neutral'),
                rollTrack,
                self.door3.posInterval(2.5, Point3(0, 0, 25), startPos=Point3(0, 0, 18)))),
            (5.5, Func(self.setChatAbsolute, outtaHere, CFSpeech)),
            (5.5, SoundInterval(trainPassingSfx)),
            (8.1, Func(self.clearChat)),
            (9.4, Sequence(
                Func(loco.reparentTo, render),
                Func(car1.reparentTo, render),
                Func(car2.reparentTo, render),
                trainTrack,
                Func(loco.detachNode),
                Func(car1.detachNode),
                Func(car2.detachNode),
                Wait(2))),
            (9.5, SoundInterval(flattenSfx)),
            (9.5, Sequence(
                self.scaleInterval(0.1, Point3(2, 2, 0.025)),
                Func(self.pose, 'Ff_neutral', 0))))
        return bossTrack

    def grabObject(self, obj):
        obj.wrtReparentTo(self.neck)
        obj.hideShadows()
        obj.stashCollisions()
        if obj.lerpInterval:
            obj.lerpInterval.finish()
        obj.lerpInterval = Parallel(
            obj.posInterval(BossCogGlobals.CashbotBossToMagnetTime, Point3(-1, 0, 0.2)),
            obj.quatInterval(BossCogGlobals.CashbotBossToMagnetTime, VBase3(0, -90, 90)),
            Sequence(
                Wait(BossCogGlobals.CashbotBossToMagnetTime),
                ShowInterval(self.eyes)
            ),
            obj.toMagnetSoundInterval
        )
        obj.lerpInterval.start()
        self.heldObject = obj
        messenger.send(ConditionGlobals.RefreshMsg)

    def dropObject(self, obj):
        if obj.lerpInterval:
            obj.lerpInterval.finish()
            obj.lerpInterval = None
        obj = self.heldObject
        obj.wrtReparentTo(render)
        obj.setHpr(obj.getH(), 0, 0)
        self.eyes.hide()
        obj.showShadows()
        obj.unstashCollisions()
        self.heldObject = None
        messenger.send(ConditionGlobals.RefreshMsg)

    @property
    def dizzyMusic(self):
        return self.battleThreeDizzyMusic

    @property
    def unDizzyMusic(self):
        return self.battleThreeMusic

    def setBossDamage(self, bossDamage):
        if bossDamage > self.bossDamage:
            delta = bossDamage - self.bossDamage
            self.flashRed()
            self.doAnimate('hit', now=1)
            self.showHpText(-delta, scale=5)
        self.bossDamage = bossDamage
        self.healthGui.updateHealth(self.bossMaxDamage - self.bossDamage)
        self.updateHealthBar()
        messenger.send(ConditionGlobals.RefreshMsg)

    def setMaxHp(self, hp):
        self.bossMaxDamage = hp
        self.healthGui.setMaxHp(hp)
        messenger.send(ConditionGlobals.RefreshMsg)

    def updateDamageDealt(self, avId, damageDealt):
        self.healthGui.updateDamageDealt(avId, damageDealt)

    def updateStunCount(self, avId):
        self.healthGui.updateStunCount(avId)

    def updateGoonsStomped(self, avId):
        self.healthGui.updateGoonsStomped(avId)

    def stunAllGoons(self):
        for goon in self.goons:
            if goon.state == 'Walk' or goon.state == 'Battle':
                goon.demand('Stunned')
                goon.sendUpdate('requestStunned', [0])

    def destroyAllGoons(self):
        for goon in self.goons:
            if goon.state != 'Off' and not goon.isDead:
                goon.b_destroyGoon()

    def deactivateCranes(self):
        for crane in list(self.cranes.values()):
            crane.demand('Free')

    def hideBattleThreeObjects(self):
        for goon in self.goons:
            goon.demand('Off')

        for safe in list(self.safes.values()):
            safe.demand('Off')

        for crane in list(self.cranes.values()):
            crane.demand('Off')

    def __doPhysics(self, task):
        dt = globalClock.getDt()
        self.physicsMgr.doPhysics(dt)
        return Task.cont

    def __hideToons(self):
        for toonId in self.involvedToons:
            toon = self.cr.doId2do.get(toonId)
            if toon:
                toon.hide()

    def __showToons(self):
        for toonId in self.involvedToons:
            toon = self.cr.doId2do.get(toonId)
            if toon:
                toon.show()

    def __arrangeToonsAroundResistanceToon(self):
        radius = 7
        numToons = len(self.involvedToons)
        center = (numToons - 1) / 2.0
        for i in range(numToons):
            toon = self.cr.doId2do.get(self.involvedToons[i])
            if toon:
                angle = 90 - 15 * (i - center)
                radians = angle * math.pi / 180.0
                x = math.cos(radians) * radius
                y = math.sin(radians) * radius
                toon.setPos(self.resistanceToon, x, y, 0)
                toon.headsUp(self.resistanceToon)
                toon.setGeomNodeH(0)
                toon.loop('neutral')
                toon.show()

    def __talkAboutPromotion(self, speech):
        if (self.prevCogSuitLevel < ToontownGlobals.MaxCogSuitLevel) or (self.prevCogSuitReviveLevel > -1 and self.prevCogSuitLevel < 49):
            newCogSuitLevel = localAvatar.getCogLevels()[CogDisguiseGlobals.dept2deptIndex(self.style.dept)]
            newCogSuitReviveLevel = localAvatar.getCogReviveLevels()[CogDisguiseGlobals.dept2deptIndex(self.style.dept)]
            newCogSuitType = localAvatar.getCogTypes()[CogDisguiseGlobals.dept2deptIndex(self.style.dept)]
            if newCogSuitLevel == ToontownGlobals.MaxCogSuitLevel:
                speech += TTLocalizer.ResistanceToonLastPromotion % (ToontownGlobals.MaxCogSuitLevel + 1)
            if newCogSuitReviveLevel == ToontownGlobals.MaxCogSuitLevel:
                speech += TTLocalizer.ResistanceToonLastRevivePromotion % (ToontownGlobals.MaxCogSuitLevel + 1)
            if newCogSuitLevel in ToontownGlobals.CogSuitHPLevels and newCogSuitType != 6:
                speech += TTLocalizer.ResistanceToonHPBoost
            if newCogSuitReviveLevel in ToontownGlobals.CogReviveSuitHPLevels and newCogSuitReviveLevel != self.prevCogSuitReviveLevel:
                speech += TTLocalizer.ResistanceToonHPBoost
            if self.prevCogSuitType != 4 and newCogSuitType == 4:
                speech += TTLocalizer.ResistanceToonTeleportAccess
        else:
            speech += TTLocalizer.ResistanceToonMaxed % (ToontownGlobals.MaxCogSuitLevel + 1)

        numCounterfeitsEarned = self.numCounterfeitsEarned.get(localAvatar.doId)
        if not numCounterfeitsEarned:
            numCounterfeitsEarned = TTLocalizer.CeaseDesistsNotFoundVal
        speech += TTLocalizer.ResistanceToonCounterfeitsReward % numCounterfeitsEarned
        speech = self.handleUniteSpeech(speech)

        return speech

    def enterOff(self):
        DistributedBossCog.DistributedBossCog.enterOff(self)
        if self.resistanceToon:
            self.resistanceToon.clearChat()

    def enterWaitForToons(self):
        DistributedBossCog.DistributedBossCog.enterWaitForToons(self)
        self.detachNode()
        self.geom.hide()
        self.resistanceToon.removeActive()

    def exitWaitForToons(self):
        DistributedBossCog.DistributedBossCog.exitWaitForToons(self)
        self.geom.show()
        self.resistanceToon.addActive()

    def enterElevator(self):
        base.discord.applyPreset('boss-m-1')
        DistributedBossCog.DistributedBossCog.enterElevator(self)
        self.detachNode()
        self.resistanceToon.removeActive()
        self.endVault.stash()
        self.midVault.unstash()
        self.__showResistanceToon(True)
        base.camLens.setMinFov(ToontownGlobals.CFOElevatorFov/(4./3.))

    def exitElevator(self):
        DistributedBossCog.DistributedBossCog.exitElevator(self)
        self.resistanceToon.addActive()

    def enterIntroduction(self):
        self.detachNode()
        self.stopAnimate()
        self.endVault.unstash()
        self.evWalls.stash()
        self.midVault.unstash()
        self.__showResistanceToon(True)
        base.musicMgr.playMusic(self.introCutsceneMusic, looping=1, volume=0.9)
        DistributedBossCog.DistributedBossCog.enterIntroduction(self)
        self.acceptOnce('skipCutscene', self.__beginBattleOne)

    def __beginBattleOne(self):
        intervalName = 'IntroductionMovie'
        self.clearInterval(intervalName)
        self.doneBarrier('Introduction')

    def exitIntroduction(self):
        self.ignore('skipCutscene')
        DistributedBossCog.DistributedBossCog.exitIntroduction(self)

    def enterBattleOne(self):
        base.discord.applyPreset('boss-m-2')
        DistributedBossCog.DistributedBossCog.enterBattleOne(self)
        self.reparentTo(render)
        self.setPosHpr(*BossCogGlobals.CashbotBossBattleOnePosHpr)
        self.show()
        self.pelvis.setHpr(self.pelvisReversedHpr)
        self.doAnimate()
        self.endVault.unstash()
        self.evWalls.stash()
        self.midVault.unstash()
        self.__hideResistanceToon()

    def exitBattleOne(self):
        DistributedBossCog.DistributedBossCog.exitBattleOne(self)

    def enterRollToBattleTwo(self):
        pass

    def exitRollToBattleTwo(self):
        pass

    def enterPrepareBattleTwo(self):
        base.discord.applyPreset('boss-m-3')
        self.controlToons()
        NametagGlobals.setMasterArrowsOn(0)
        intervalName = 'PrepareBattleTwoMovie'
        delayDeletes = []
        seq = Sequence(self.makePrepareBattleTwoMovie(delayDeletes), Func(self.__beginBattleTwo), name=intervalName)
        seq.delayDeletes = delayDeletes
        seq.start()
        self.storeInterval(seq, intervalName)
        self.endVault.unstash()
        self.evWalls.stash()
        self.midVault.unstash()
        self.__hideToons()
        self.__hideResistanceToon()
        taskMgr.add(self.__doPhysics, self.uniqueName('physics'), priority=25)
        self.acceptOnce('skipCutscene', self.__beginBattleTwo)

    def exitPrepareBattleTwo(self):
        self.ignore('skipCutscene')
        intervalName = 'PrepareBattleTwoMovie'
        self.clearInterval(intervalName)
        self.unstickToons()
        self.releaseToons()
        NametagGlobals.setMasterArrowsOn(1)
        ElevatorUtils.closeDoors(self.leftDoor, self.rightDoor, ElevatorConstants.ELEVATOR_CFO)

    def enterBattleTwo(self):
        base.discord.applyPreset('boss-m-4')
        self.reparentTo(render)
        self.evWalls.unstash()
        self.setPosHpr(*BossCogGlobals.CashbotBossBattleTwoPosHpr)
        self.show()
        self.pelvis.setHpr(self.pelvisReversedHpr)
        self.toonsToBattlePosition(self.toonsA, self.battleANode)
        self.toonsToBattlePosition(self.toonsB, self.battleBNode)
        self.doAnimate()
        self.__hideResistanceToon()
        DistributedBossCog.DistributedBossCog.enterBattleTwo(self)


    def exitBattleTwo(self):
        # self.battleTwoMusic.stop()
        DistributedBossCog.DistributedBossCog.exitBattleTwo(self)

    def __beginBattleTwo(self):
        intervalName = 'PrepareBattleTwoMovie'
        self.clearInterval(intervalName)
        self.doneBarrier('PrepareBattleTwo')

    def enterPrepareBattleThree(self):
        self.controlToons()
        NametagGlobals.setMasterArrowsOn(0)
        intervalName = 'PrepareBattleThreeMovie'
        delayDeletes = []
        self.movieCrane = self.cranes[0]
        self.movieSafe = self.safes[1]
        self.movieCrane.request('Movie')
        seq = Sequence(self.makePrepareBattleThreeMovie(delayDeletes, self.movieCrane, self.movieSafe), Func(self.__beginBattleThree), name=intervalName)
        seq.delayDeletes = delayDeletes
        seq.start()
        self.storeInterval(seq, intervalName)
        self.__showResistanceToon(False)
        taskMgr.add(self.__doPhysics, self.uniqueName('physics'), priority=25)
        self.acceptOnce('skipCutscene', self.__beginBattleThree)

    def __beginBattleThree(self):
        intervalName = 'PrepareBattleThreeMovie'
        self.clearInterval(intervalName)
        self.doneBarrier('PrepareBattleThree')

    def exitPrepareBattleThree(self):
        self.ignore('skipCutscene')
        intervalName = 'PrepareBattleThreeMovie'
        self.clearInterval(intervalName)
        self.unstickToons()
        self.releaseToons()
        if self.newState == 'BattleThree':
            self.movieCrane.request('Free')
            self.movieSafe.request('Initial')
        NametagGlobals.setMasterArrowsOn(1)
        ElevatorUtils.closeDoors(self.leftDoor, self.rightDoor, ElevatorConstants.ELEVATOR_CFO)
        taskMgr.remove(self.uniqueName('physics'))

    def enterBattleThree(self):
        base.discord.applyPreset('boss-m-5')
        DistributedBossCog.DistributedBossCog.enterBattleThree(self)
        self.clearChat()
        self.resistanceToon.clearChat()
        self.reparentTo(render)
        self.setPosHpr(*BossCogGlobals.CashbotBossBattleThreePosHpr)
        self.happy = 1
        self.raised = 1
        self.forward = 1
        self.doAnimate()
        self.endVault.unstash()
        self.evWalls.unstash()
        self.midVault.stash()
        self.__hideResistanceToon()
        localAvatar.setCameraFov(ToontownGlobals.BossBattleCameraFov)
        self.generateHealthBar()
        self.updateHealthBar()
        self.healthGui.createBossCogHead()
        self.healthGui.moveInInitial()
        base.musicMgr.playMusic(self.battleThreeMusic, looping=1, volume=0.9)
        taskMgr.add(self.__doPhysics, self.uniqueName('physics'), priority=25)

        base.cr.gameGui.expBar.hide()
        self.departmentExpBar = DepartmentExperienceBar.DepartmentExperienceBar(base.localAvatar.departmentExp[ToontownGlobals.DEPARTMENT_CASHBOT], base.localAvatar.departmentLevels[ToontownGlobals.DEPARTMENT_CASHBOT], ToontownGlobals.DEPARTMENT_CASHBOT, base.localAvatar.style)
        self.departmentExpBar.setAvatar(base.localAvatar)
        self.departmentExpBar.setScale(0.075)
        self.departmentExpBar.reparentTo(base.a2dBottomLeft)
        self.departmentExpBar.start()

        # Tell condition manager to pull up dept bars/crane state
        stateArgs = ConditionGlobals.ConditionStateArgs()
        stateArgs[ConditionGlobals.ConditionStateArg.BOSS] = self
        messenger.send(ConditionGlobals.SetStateMsg, [ConditionGlobals.ConditionState.BOSS_CFO, stateArgs])

    def exitBattleThree(self):
        DistributedBossCog.DistributedBossCog.exitBattleThree(self)
        bossDoneEventName = self.uniqueName('DestroyedBoss')
        self.ignore(bossDoneEventName)
        self.stopAnimate()
        self.cleanupAttacks()
        self.setDizzy(0)
        localAvatar.setCameraFov(ToontownGlobals.CogHQCameraFov)
        taskMgr.remove(self.uniqueName('physics'))

    def toonDied(self, avId):
        DistributedBossCog.DistributedBossCog.toonDied(self, avId)

        # If our toon died, get rid of the dept exp bar
        if avId == base.localAvatar.doId:
            if self.departmentExpBar:
                self.departmentExpBar.hide()
                self.departmentExpBar.stop()
                self.departmentExpBar.destroy()
            base.cr.gameGui.expBar.show()

    def enterVictory(self):
        self.cleanupIntervals()
        self.reparentTo(render)
        self.setPosHpr(*BossCogGlobals.CashbotBossBattleThreePosHpr)
        self.stopAnimate()
        self.endVault.unstash()
        self.evWalls.unstash()
        self.midVault.unstash()
        self.__hideResistanceToon()
        self.__hideToons()
        self.clearChat()
        self.resistanceToon.clearChat()
        self.deactivateCranes()
        if self.cranes:
            self.cranes[1].demand('Off')
        self.releaseToons(finalBattle=1)
        if self.hasLocalToon():
            self.toMovieMode()
            base.localAvatar.setFriendsListButtonActive(0)
        intervalName = 'VictoryMovie'
        seq = Sequence(self.makeBossFleeMovie(), Func(self.__continueVictory), name=intervalName)
        seq.start()
        base.musicMgr.playMusic(self.killMusic, looping=1, volume=0.9)
        self.storeInterval(seq, intervalName)
        if self.departmentExpBar:
            self.departmentExpBar.hide()
            self.departmentExpBar.stop()
            self.departmentExpBar.destroy()
        base.cr.gameGui.expBar.show()

    def __continueVictory(self):
        self.doneBarrier('Victory')
        if self.healthGui:
            self.healthGui.moveOutEnd()
        self.removeHealthBar()

    def exitVictory(self):
        self.cleanupIntervals()
        if self.newState != 'Reward':
            if self.hasLocalToon():
                self.toWalkMode()
        self.__showToons()
        self.door3.setPos(0, 0, 0)

    def enterReward(self):
        self.cleanupIntervals()
        self.clearChat()
        self.resistanceToon.clearChat()
        self.stash()
        self.stopAnimate()
        self.controlToons()
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
                delayDeletes.append(DelayDelete.DelayDelete(toon, 'CashbotBoss.enterReward'))

        ival.delayDeletes = delayDeletes
        ival.start()
        self.storeInterval(ival, intervalName)
        if base.musicMgr.getMusicFilepath(self.victoryMusic) != base.musicMgr.getMusicFilepath(self.battleThreeMusic): # We have a custom victory theme loaded
            base.musicMgr.playMusic(self.victoryMusic, interrupt=1, looping=1, volume=0.9)

        # Have condition manager go back to normal
        messenger.send(ConditionGlobals.SetStateMsg, [ConditionGlobals.ConditionState.GLOBAL])

    def __doneReward(self):
        self.doneBarrier('Reward')
        self.toWalkMode()

    def exitReward(self):
        intervalName = 'RewardMovie'
        self.clearInterval(intervalName)
        if self.newState != 'Epilogue':
            self.releaseToons()
        self.unstash()
        self.rewardPanel.destroy()
        del self.rewardPanel
        base.musicMgr.stopMusic()

    def enterEpilogue(self):
        self.cleanupIntervals()
        self.clearChat()
        self.resistanceToon.clearChat()
        self.stash()
        self.stopAnimate()
        self.controlToons()
        self.hideToonsMeters()
        self.__showResistanceToon(False)
        self.resistanceToon.setPosHpr(*BossCogGlobals.CashbotBossBattleThreePosHpr)
        self.resistanceToon.loop('neutral')
        self.__arrangeToonsAroundResistanceToon()
        base.camera.reparentTo(render)
        base.camera.setPos(self.resistanceToon, -9, 12, 6)
        base.camera.lookAt(self.resistanceToon, 0, 0, 3)
        # intervalName = 'EpilogueMovie'

        speech = TTLocalizer.ResistanceToonCongratulations
        speech = self.__talkAboutPromotion(speech)
        self.resistanceToon.setLocalPageChat(speech, 0)
        self.accept('nextChatPage', self.__epilogueChatNext)
        self.accept('doneChatPage', self.__epilogueChatDone)
        base.musicMgr.playMusic(self.epilogueMusic, looping=1, volume=0.9)

    def __epilogueChatNext(self, pageNumber, elapsed):
        if pageNumber == 1:
            toon = self.resistanceToon
            playRate = 0.75
            track = Sequence(
                ActorInterval(toon, 'victory', playRate=playRate, startFrame=0, endFrame=9),
                ActorInterval(toon, 'victory', playRate=playRate, startFrame=9, endFrame=0),
                Func(self.resistanceToon.loop, 'neutral')
            )
            intervalName = 'EpilogueMovieToonAnim'
            self.storeInterval(track, intervalName)
            track.start()
        elif pageNumber == self.localUniteEffectPageNumber:
            self.handleLocalUniteEffect()

    def __epilogueChatDone(self, elapsed):
        self.resistanceToon.setChatAbsolute(TTLocalizer.ResistanceToonGoodbye, CFSpeech)
        self.ignore('nextChatPage')
        self.ignore('doneChatPage')
        intervalName = 'EpilogueMovieToonAnim'
        self.clearInterval(intervalName)
        track = Parallel(
            Sequence(
                ActorInterval(self.resistanceToon, 'wave'),
                Func(self.resistanceToon.loop, 'neutral')
            ),
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

    def setNumCounterfeitsEarned(self, toonId, numCounterfeits):
        if toonId not in self.numCounterfeitsEarned:
            self.numCounterfeitsEarned[toonId] = numCounterfeits

    def enterFrolic(self):
        DistributedBossCog.DistributedBossCog.enterFrolic(self)
        self.setPosHpr(*BossCogGlobals.CashbotBossBattleOnePosHpr)
        self.releaseToons()
        if self.hasLocalToon():
            self.toWalkMode()
        self.door3.setZ(25)
        self.door2.setZ(25)
        self.endVault.unstash()
        self.evWalls.stash()
        self.midVault.unstash()
        self.__hideResistanceToon()

    def exitFrolic(self):
        self.door3.setZ(0)
        self.door2.setZ(0)

    @property
    def uniteResistanceToon(self):
        return self.resistanceToon
