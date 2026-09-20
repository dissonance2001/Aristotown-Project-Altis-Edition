import math
import random

from panda3d.core import *
from otp import *

from toontown.gui.game.condition import ConditionGlobals
from toontown.clashsuit.suit import BossCogGlobals
from toontown.clashsuit.suit.DistributedSuitBase import DistributedSuitBase
from toontown.toonbase.GlobalCacheData import GlobalCacheKey
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from direct.distributed.ClockDelta import globalClockDelta
from direct.fsm import FSM
from direct.interval.IntervalGlobal import *
from direct.showbase import PythonUtil
from direct.task import Task
from toontown.chat.constants.ChatGlobals import CFSpeech
from toontown.clashbattle.battle import MovieToonVictory
from toontown.clashbattle.battle import RewardPanel
from toontown.building import ElevatorConstants, ElevatorUtils
from toontown.coghq import CogDisguiseGlobals
from toontown.distributed import DelayDelete
from toontown.effects import DustCloud
from toontown.clashsuit.suit.DistributedBossCog import DistributedBossCog
from toontown.clashsuit.suit import Suit
from toontown.clashsuit.suit import SuitDNA
from toontown.clashsuit.suit import SuitHealthMeter
# from toontown.toon import Toon
# from toontown.toon import ToonDNA
from toontown.toon.npc import NPCToons
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import ToontownTimer
from toontown.gui import DepartmentExperienceBar
from toontown.toon import TTEmote

OneBossCog = None
TTL = TTLocalizer


@DirectNotifyCategory()
class DistributedBossbotBoss(DistributedBossCog, FSM.FSM):
    BallLaunchOffset = Point3(10.5, 8.5, -5)

    def __init__(self, cr):
        DistributedBossCog.__init__(self, cr)
        FSM.FSM.__init__(self, 'DistributedBossbotBoss')
        self.bossDamage = 0
        self.bossMaxDamage = BossCogGlobals.BossbotBossMaxDamage[0]
        self.elevatorType = ElevatorConstants.ELEVATOR_CEO
        self.resistanceToon = None
        self.resistanceToonOnstage = 0
        self.battleANode.setPosHpr(*BossCogGlobals.WaiterBattleAPosHpr)
        self.battleBNode.setPosHpr(*BossCogGlobals.WaiterBattleBPosHpr)
        self.toonFoodStatus = {}
        self.belts = [None, None]
        self.tables = {}
        self.golfSpots = {}
        self.servingTimer = None
        self.notDeadList = None
        self.desperationState = -1
        self.localAvSawAdvice = False
        self.currSpeedDamage = 0
        self.maxPlayrate = 1.0
        self.maxSpeedDamage = BossCogGlobals.BossbotMaxSpeedDamage
        self.speedRecoverRate = 0
        self.speedRecoverStartTime = 0
        self.ballLaunch = None
        self.moveTrack = None
        self.numAttacks = 0
        self.attackThreshold = 1.0
        self.attackTime = ClockObject()
        self.departmentExpBar = None
        self.numPinkSlipsEarned = 0
        self.battleTwoEmoteDisableBody = False
        self.finalBattleState = 'BattleFour'

    def announceGenerate(self):
        base.globalCache.swapToKey(GlobalCacheKey.BossbotBoss)

        global OneBossCog
        DistributedBossCog.announceGenerate(self)
        nameInfo = TTLocalizer.BossCogNameWithDept % {'name': TTLocalizer.BossbotBossName,
         'dept': SuitDNA.getDeptFullname(self.style.dept)}
        self.setName(TTLocalizer.BossbotBossName)
        self.healthGui.setBossName(TTLocalizer.BossbotBossName)
        self.setDisplayName(nameInfo)
        self.loadEnvironment()
        self.__makeResistanceToon()
        base.localAvatar.chatContainer.speedChatMenu.addCEOMenu()
        if OneBossCog is not None:
            self.notify.warning('Multiple BossCogs visible.')

        OneBossCog = self
        render.setTag('pieCode', str(ToontownGlobals.PieCodeNotBossCog))
        self.setTag('attackCode', str(BossCogGlobals.BossCogGolfAttack))
        target = CollisionTube(0, -2, -2, 0, -1, 9, 4.0)
        targetNode = CollisionNode('BossZap')
        targetNode.addSolid(target)
        targetNode.setCollideMask(ToontownGlobals.PieBitmask)
        self.targetNodePath = self.pelvis.attachNewNode(targetNode)
        self.targetNodePath.setTag('pieCode', str(ToontownGlobals.PieCodeBossCog))
        self.axle.getParent().setTag('pieCode', str(ToontownGlobals.PieCodeBossCog))
        disk = loader.loadModel('phase_9/models/char/bossCog-gearCollide')
        disk.find('**/+CollisionNode').setName('BossZap')
        disk.reparentTo(self.pelvis)
        disk.setZ(0.8)

        self.treads = self.find('**/treads')
        demotedCeo = Suit.Suit()
        demotedCeo.dna = SuitDNA.SuitDNA()
        demotedCeo.dna.newSuit('f')
        demotedCeo.setDNA(demotedCeo.dna)
        demotedCeo.reparentTo(self.geom)
        demotedCeo.loop('neutral')
        demotedCeo.stash()
        self.demotedCeo = demotedCeo
        self.bossClub = loader.loadModel('phase_12/models/char/bossbotBoss-golfclub')
        overtimeOneClubSequence = Sequence(self.bossClub.colorScaleInterval(0.1, colorScale=VBase4(0, 1, 0, 1)), self.bossClub.colorScaleInterval(0.3, colorScale=VBase4(1, 1, 1, 1)))
        overtimeTwoClubSequence = Sequence(self.bossClub.colorScaleInterval(0.1, colorScale=VBase4(1, 0, 0, 1)), self.bossClub.colorScaleInterval(0.3, colorScale=VBase4(1, 1, 1, 1)))
        self.bossClubIntervals = [overtimeOneClubSequence, overtimeTwoClubSequence]
        self.rightHandJoint = self.find('**/joint17')
        self.setPosHpr(*BossCogGlobals.BossbotBossBattleOnePosHpr)
        self.reparentTo(render)
        self.toonUpSfx = loader.loadSfx('phase_11/audio/sfx/LB_toonup.ogg')
        self.warningSfx = loader.loadSfx('phase_5/audio/sfx/Skel_COG_VO_grunt.ogg')
        self.swingClubSfx = loader.loadSfx('phase_5/audio/sfx/SA_hardball.ogg')
        self.moveBossTaskName = 'CEOMoveTask'

    def disable(self):
        """
        Called when the DistributedObject is removed from active duty and stored in a cache.
        """
        global OneBossCog
        DistributedBossCog.disable(self)
        self.demotedCeo.delete()
        taskMgr.remove('RecoverSpeedDamage')
        self.request('Off')
        self.unloadEnvironment()
        self.__cleanupResistanceToon()
        if self.servingTimer:
            self.servingTimer.destroy()
            del self.servingTimer
        base.localAvatar.chatContainer.speedChatMenu.removeCEOMenu()
        if OneBossCog == self:
            OneBossCog = None

        base.musicMgr.stopMusic()
        self.stopMove()
        for ival in self.bossClubIntervals:
            ival.finish()

        base.localAvatar.setCanSprint(True)

        self.belts = []
        self.tables = {}
        self.ignoreAll()
        self.removeAllTasks()

    def loadEnvironment(self):
        self.notify.debug('----- loadEnvironment')
        DistributedBossCog.loadEnvironment(self)
        self.geom = loader.loadModel('phase_12/models/bossbotHQ/BanquetInterior_1')
        self.elevatorEntrance = self.geom.find('**/elevator_origin')
        elevatorModel = loader.loadModel('phase_12/models/bossbotHQ/BB_Inside_Elevator')
        if not elevatorModel:
            elevatorModel = loader.loadModel('phase_12/models/bossbotHQ/BB_Elevator')

        elevatorModel.reparentTo(self.elevatorEntrance)
        self.setupElevator(elevatorModel)
        self.banquetDoor = self.geom.find('**/door3')
        plane = CollisionPlane(Plane(Vec3(0, 0, 1), Point3(0, 0, -50)))
        planeNode = CollisionNode('dropPlane')
        planeNode.addSolid(plane)
        planeNode.setCollideMask(ToontownGlobals.PieBitmask)
        self.geom.attachNewNode(planeNode)
        self.geom.reparentTo(render)
        self.elevatorMusic = 'ceo_elevator'
        self.promotionMusic = 'ceo_intro_cutscene'
        self.battleOneMusic = 'ceo_battle_one'
        self.waiterCtscMusic = 'ceo_waiters_cutscene'
        self.battleTwoMusic = 'ceo_battle_two'
        self.battleThreeMusic = 'ceo_battle_three'
        self.battleFourMusic = 'ceo_battle_four'
        self.battleFourDizzyMusic = 'ceo_battle_four_stunned'
        self.killMusic = 'ceo_battle_stinger'
        self.victoryMusic = 'ceo_victory'
        self.epilogueMusic = 'ceo_epilogue'
        self.victoryAndBattleFourMatch = base.musicMgr.getMusicFilepath(self.victoryMusic) == base.musicMgr.getMusicFilepath(self.battleFourMusic)
        self.pickupFoodSfx = loader.loadSfx('phase_6/audio/sfx/SZ_MM_gliss.ogg')
        self.explodeSfx = loader.loadSfx('phase_4/audio/sfx/firework_distance_02.ogg')
        self.preloadFinalBattleMusic()

    def unloadEnvironment(self):
        for belt in self.belts:
            if belt:
                belt.cleanup()

        for spot in list(self.golfSpots.values()):
            if spot:
                spot.cleanup()

        self.golfSpots = {}
        self.geom.removeNode()
        del self.geom
        DistributedBossCog.unloadEnvironment(self)

    def setupElevator(self, elevatorModel):
        self.elevatorModel = elevatorModel
        self.leftDoor = self.elevatorModel.find('**/left-door')
        if self.leftDoor.isEmpty():
            self.leftDoor = self.elevatorModel.find('**/left_door')
        self.rightDoor = self.elevatorModel.find('**/right-door')
        if self.rightDoor.isEmpty():
            self.rightDoor = self.elevatorModel.find('**/right_door')
        self.openSfx = base.loader.loadSfx('phase_12/audio/sfx/cc_s_sfx_ara_bbhq_elevator.ogg')
        self.finalOpenSfx = None
        self.closeSfx = base.loader.loadSfx('phase_12/audio/sfx/cc_s_sfx_ara_bbhq_elevator.ogg')
        self.finalCloseSfx = None
        self.openDoors = ElevatorUtils.getOpenInterval(self, self.leftDoor, self.rightDoor, self.openSfx, None, self.elevatorType)
        self.closeDoors = ElevatorUtils.getCloseInterval(self, self.leftDoor, self.rightDoor, self.closeSfx, None, self.elevatorType)
        self.closeDoors.start()
        self.closeDoors.finish()

    def __makeResistanceToon(self):
        if self.resistanceToon:
            return
        self.resistanceToon = NPCToons.createLocalNPC(2010)
        self.resistanceToon.setPosHpr(*BossCogGlobals.BossbotRTIntroStartPosHpr)
        state = random.getstate()
        random.seed(self.doId)
        self.resistanceToon.suitType = SuitDNA.getRandomSuitByDept('c')
        self.resistanceToon.setName(TTLocalizer.BossbotResistanceToonName)
        self.resistanceToon.setDisplayName(TTLocalizer.BossbotResistanceToonName)
        random.setstate(state)

    def __cleanupResistanceToon(self):
        self.__hideResistanceToon()
        if self.resistanceToon:
            self.resistanceToon.takeOffSuit()
            self.resistanceToon.removeActive()
            self.resistanceToon.delete()
            self.resistanceToon = None

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

    def enterElevator(self):
        base.discord.applyPreset('boss-c-1')
        DistributedBossCog.enterElevator(self)
        self.resistanceToon.removeActive()
        self.__showResistanceToon(True)
        self.resistanceToon.suit.loop('neutral')
        base.camera.setPos(0, 21, 7)
        self.reparentTo(render)
        self.setPosHpr(*BossCogGlobals.BossbotBossBattleOnePosHpr)
        self.loop('Ff_neutral')
        self.show()
        base.camLens.setMinFov(ToontownGlobals.CEOElevatorFov/(4./3.))

    def enterIntroduction(self):
        if not self.resistanceToonOnstage:
            self.__showResistanceToon(True)
        DistributedBossCog.enterIntroduction(self)
        base.musicMgr.playMusic(self.promotionMusic, looping=1, volume=0.9)
        self.acceptOnce('skipCutscene', self.__beginBattleOne)

    def __beginBattleOne(self):
        intervalName = 'IntroductionMovie'
        self.clearInterval(intervalName)
        self.doneBarrier('Introduction')

    def exitIntroduction(self):
        self.ignore('skipCutscene')
        DistributedBossCog.exitIntroduction(self)

    def makeIntroductionMovie(self, delayDeletes):
        rToon = self.resistanceToon
        rToonStartPos = Point3(BossCogGlobals.BossbotRTIntroStartPosHpr[0], BossCogGlobals.BossbotRTIntroStartPosHpr[1], BossCogGlobals.BossbotRTIntroStartPosHpr[2])
        rToonEndPos = rToonStartPos + Point3(40, 0, 0)
        elevCamPosHpr = BossCogGlobals.BossbotElevCamPosHpr
        closeUpRTCamPos = Point3(elevCamPosHpr[0], elevCamPosHpr[1], elevCamPosHpr[2])
        closeUpRTCamHpr = Point3(elevCamPosHpr[3], elevCamPosHpr[4], elevCamPosHpr[5])
        closeUpRTCamPos.setY(closeUpRTCamPos.getY() + 20)
        closeUpRTCamPos.setZ(closeUpRTCamPos.getZ() + -2)
        closeUpRTCamHpr = Point3(0, 5, 0)
        loseSuitCamPos = Point3(rToonStartPos)
        loseSuitCamPos += Point3(0, -5, 4)
        loseSuitCamHpr = Point3(180, 0, 0)
        waiterCamPos = Point3(rToonStartPos)
        waiterCamPos += Point3(-5, -10, 5)
        # waiterCamHpr = Point3(-30, 0, 0)
        track = Sequence(Func(camera.reparentTo, render), Func(camera.setPosHpr, *elevCamPosHpr), Func(rToon.setChatAbsolute, TTL.BossbotRTWelcome, CFSpeech), LerpPosHprInterval(camera, 3, closeUpRTCamPos, closeUpRTCamHpr), Func(rToon.setChatAbsolute, TTL.BossbotRTRemoveSuit, CFSpeech), Wait(3), Func(self.clearChat), self.loseCogSuits(self.toonsA + self.toonsB, render, (loseSuitCamPos[0],
            loseSuitCamPos[1],
            loseSuitCamPos[2],
            loseSuitCamHpr[0],
            loseSuitCamHpr[1],
            loseSuitCamHpr[2])), self.toonNormalEyes(self.involvedToons), Wait(2), Func(camera.setPosHpr, closeUpRTCamPos, closeUpRTCamHpr), Func(rToon.setChatAbsolute, TTL.BossbotRTFightWaiter, CFSpeech), Wait(1), LerpHprInterval(camera, 2, Point3(-15, 5, 0)), Sequence(Func(rToon.suit.loop, 'walk'), rToon.hprInterval(1, VBase3(270, 0, 0)), rToon.posInterval(2.5, rToonEndPos), Func(rToon.suit.loop, 'neutral')), Wait(3), Func(rToon.clearChat), Func(self.__hideResistanceToon))

        return track

    def enterBattleOne(self):
        base.discord.applyPreset('boss-c-2')
        DistributedBossCog.enterBattleOne(self)

    def enterFrolic(self):
        self.setPosHpr(*BossCogGlobals.BossbotBossBattleOnePosHpr)
        DistributedBossCog.enterFrolic(self)
        self.show()

    def enterPrepareBattleTwo(self):
        self.controlToons()
        self.setToonsToNeutral(self.involvedToons)
        for toonId in self.involvedToons:
            toon = self.cr.doId2do.get(toonId)
            if toon:
                toon.takeOffSuit()

        self.__showResistanceToon(True)
        self.resistanceToon.setPosHpr(*BossCogGlobals.BossbotRTPreTwoPosHpr)
        self.__arrangeToonsAroundResistanceToon()
        intervalName = 'PrepareBattleTwoMovie'
        delayDeletes = []
        seq = Sequence(self.makePrepareBattleTwoMovie(delayDeletes), Func(self.__onToBattleTwo), name=intervalName)
        seq.delayDeletes = delayDeletes
        seq.start()
        self.storeInterval(seq, intervalName)
        base.musicMgr.playMusic(self.waiterCtscMusic, looping=1, volume=0.9)
        self.acceptOnce('skipCutscene', self.__onToBattleTwo)

    def makePrepareBattleTwoMovie(self, delayDeletes):
        for toonId in self.involvedToons:
            toon = self.cr.doId2do.get(toonId)
            if toon:
                delayDeletes.append(DelayDelete.DelayDelete(toon, 'BossbotBoss.makePrepareBattleTwoMovie'))

        rToon = self.resistanceToon
        rToonStartPos = Point3(BossCogGlobals.BossbotRTPreTwoPosHpr[0], BossCogGlobals.BossbotRTPreTwoPosHpr[1], BossCogGlobals.BossbotRTPreTwoPosHpr[2])
        rToonEndPos = rToonStartPos + Point3(-40, 0, 0)
        bossPos = Point3(BossCogGlobals.BossbotBossPreTwoPosHpr[0], BossCogGlobals.BossbotBossPreTwoPosHpr[1], BossCogGlobals.BossbotBossPreTwoPosHpr[2])
        bossEndPos = Point3(BossCogGlobals.BossbotBossBattleOnePosHpr[0], BossCogGlobals.BossbotBossBattleOnePosHpr[1], BossCogGlobals.BossbotBossBattleOnePosHpr[2])
        tempNode = self.attachNewNode('temp')
        tempNode.setPos(0, -40, 18)

        def getCamBossPos(tempNode = tempNode):
            return tempNode.getPos(render)

        rNode = rToon.attachNewNode('temp2')
        rNode.setPos(-5, 25, 12)

        def getCamRTPos(rNode = rNode):
            return rNode.getPos(render)

        track = Sequence(
            Func(camera.reparentTo, render),
            Func(camera.setPos, rToon, 0, 22, 6),
            Func(camera.setHpr, 0, 0, 0),
            Func(rToon.setChatAbsolute, TTL.BossbotRTWearWaiter, CFSpeech),
            Wait(3.0),
            self.wearCogSuits(self.toonsA + self.toonsB, render, None, waiter=True),
            Func(rToon.clearChat),
            Func(self.setPosHpr, bossPos, Point3(0, 0, 0)),
            Parallel(LerpHprInterval(self.banquetDoor, 2, Point3(90, 0, 0)),
                     LerpPosInterval(camera, 2, getCamBossPos)),
            Func(self.setChatAbsolute, TTL.BossbotBossPreTwo1, CFSpeech),
            Wait(3.0),
            Func(self.setChatAbsolute, TTL.BossbotBossPreTwo2, CFSpeech),
            Wait(3.0),
            Parallel(
                LerpHprInterval(self.banquetDoor, 2, Point3(0, 0, 0)),
                LerpPosHprInterval(camera, 2, getCamRTPos, Point3(10, -8, 0))),
            Func(self.setPos, bossEndPos),
            Func(self.clearChat),
            Func(rToon.setChatAbsolute, TTL.BossbotRTServeFood1, CFSpeech),
            Wait(3.0),
            Func(rToon.setChatAbsolute, TTL.BossbotRTServeFood2, CFSpeech),
            Wait(1.0),
            LerpHprInterval(self.banquetDoor, 2, Point3(120, 0, 0)),
            Sequence(
                Func(rToon.suit.loop, 'walk'),
                rToon.hprInterval(1, VBase3(90, 0, 0)),
                rToon.posInterval(2.5, rToonEndPos),
                Func(rToon.suit.loop, 'neutral')),
            self.createWalkInInterval(),
            Func(self.banquetDoor.setH, 0),
            Func(rToon.clearChat),
            Func(self.__hideResistanceToon))
        return track

    def createWalkInInterval(self):
        retval = Parallel()
        delay = 0
        index = 0
        for toonId in self.involvedToons:
            toon = base.cr.doId2do.get(toonId)
            if not toon:
                continue
            destPos = Point3(-14 + index * 4, 25, 0)

            def toWalk(toon):
                if hasattr(toon, 'suit') and toon.suit:
                    toon.suit.loop('walk')

            def toNeutral(toon):
                if hasattr(toon, 'suit') and toon.suit:
                    toon.suit.loop('neutral')

            retval.append(Sequence(Wait(delay), Func(toon.wrtReparentTo, render), Func(toWalk, toon), Func(toon.headsUp, 0, 0, 0), LerpPosInterval(toon, 3, Point3(0, 0, 0)), Func(toon.headsUp, destPos), LerpPosInterval(toon, 3, destPos), LerpHprInterval(toon, 1, Point3(0, 0, 0)), Func(toNeutral, toon)))
            if toon == base.localAvatar:
                retval.append(Sequence(Wait(delay), Func(camera.reparentTo, toon), Func(camera.setPos, 0.0, -9.0 * base.localAvatar.getClampedAvatarHeight() * 0.3333333333, base.localAvatar.getClampedAvatarHeight()), Func(camera.setHpr, 0, 0, 0)))
            delay += 1.0
            index += 1

        return retval

    def __onToBattleTwo(self, elapsedTime = 0):
        self.doneBarrier('PrepareBattleTwo')

    def exitPrepareBattleTwo(self):
        self.ignore('skipCutscene')
        self.clearInterval('PrepareBattleTwoMovie')

    def __arrangeToonsAroundResistanceToon(self):
        radius = 9
        numToons = len(self.involvedToons)
        center = (numToons - 1) / 2.0
        for i in range(numToons):
            toon = self.cr.doId2do.get(self.involvedToons[i])
            if toon:
                angle = 90 - 25 * (i - center)
                radians = angle * math.pi / 180.0
                x = math.cos(radians) * radius
                y = math.sin(radians) * radius
                toon.reparentTo(render)
                toon.setPos(self.resistanceToon, x, y, 0)
                toon.headsUp(self.resistanceToon)
                toon.setGeomNodeH(0)
                toon.loop('neutral')
                toon.show()

    def enterBattleTwo(self):
        base.discord.applyPreset('boss-c-3')
        # No sprinting in this round!
        base.localAvatar.setCanSprint(False)
        self.releaseToons(finalBattle=1)
        for toonId in self.involvedToons:
            toon = self.cr.doId2do.get(toonId)
            if toon:
                self.putToonInCogSuit(toon)

        self.servingTimer = ToontownTimer.ToontownTimer()
        self.servingTimer.posInTopRightCorner()
        self.servingTimer.countdown(BossCogGlobals.BossbotBossServingDuration)
        base.musicMgr.playMusic(self.battleTwoMusic, looping=1, volume=0.9)
        base.cr.gameGui.expBar.hide()
        self.departmentExpBar = DepartmentExperienceBar.DepartmentExperienceBar(base.localAvatar.departmentExp[ToontownGlobals.DEPARTMENT_BOSSBOT], base.localAvatar.departmentLevels[ToontownGlobals.DEPARTMENT_BOSSBOT], ToontownGlobals.DEPARTMENT_BOSSBOT, base.localAvatar.style)
        self.departmentExpBar.setAvatar(base.localAvatar)
        self.departmentExpBar.setScale(0.075)
        self.departmentExpBar.reparentTo(base.a2dBottomLeft)
        self.departmentExpBar.start()

    def exitBattleTwo(self):
        if self.servingTimer:
            self.servingTimer.destroy()
            del self.servingTimer
            self.servingTimer = None
        for toonId in self.involvedToons:
            self.removeFoodFromToon(toonId)

        # They can now sprint again.
        base.localAvatar.setCanSprint(True)

    def setBelt(self, belt, beltIndex):
        if beltIndex < len(self.belts):
            self.belts[beltIndex] = belt

    def localToonTouchedBeltFood(self, beltIndex, foodIndex, foodNum):
        avId = base.localAvatar.doId
        doRequest = False
        if avId not in self.toonFoodStatus:
            doRequest = True
        elif not self.toonFoodStatus[avId]:
            doRequest = True

        if doRequest:
            self.sendUpdate('requestGetFood', [beltIndex, foodIndex, foodNum])

    def toonGotFood(self, avId, beltIndex, foodIndex, foodNum):
        if self.belts[beltIndex]:
            self.belts[beltIndex].removeFood(foodIndex)
            self.putFoodOnToon(avId, beltIndex, foodNum)

    def putFoodOnToon(self, avId, beltIndex, foodNum):
        self.toonFoodStatus[avId] = (beltIndex, foodNum)
        av = base.cr.doId2do.get(avId)
        if av:
            if hasattr(av, 'suit'):
                # If local av, disable stickers here
                if av.isLocal():
                    self.battleTwoEmoteDisableBody = True
                    TTEmote.globalEmote.disableBody(base.localAvatar, 'DistributedBossbotBoss.putFoodOnToon')
                intervalName = self.uniqueName('loadFoodSoundIval-%d' % avId)
                seq = SoundInterval(self.pickupFoodSfx, node=av, name=intervalName)
                oldSeq = self.activeIntervals.get(intervalName)
                if oldSeq:
                    oldSeq.finish()
                seq.start()
                self.activeIntervals[intervalName] = seq
                foodModel = loader.loadModel('phase_12/models/bossbotHQ/canoffood')
                foodModel.setName('cogFood')
                foodModel.setScale(BossCogGlobals.BossbotFoodModelScale)
                foodModel.reparentTo(av.suit.getRightHand())
                foodModel.setHpr(52.1961, 180.4983, -4.2882)
                curAnim = av.suit.getCurrentAnim()
                self.notify.debug('curAnim=%s' % curAnim)
                if curAnim in ('walk', 'run'):
                    av.suit.loop('tray-walk')
                elif curAnim == 'neutral':
                    self.notify.debug('looping tray-netural')
                    av.suit.loop('tray-neutral')
                else:
                    self.notify.warning("don't know what to do with anim=%s" % curAnim)

    def removeFoodFromToon(self, avId):
        self.toonFoodStatus[avId] = None
        av = base.cr.doId2do.get(avId)
        if av:
            # If local av, enable stickers here
            if av.isLocal() and self.battleTwoEmoteDisableBody:
                self.battleTwoEmoteDisableBody = False
                TTEmote.globalEmote.releaseBody(base.localAvatar, 'DistributedBossbotBoss.removeFoodFromToon')
            cogFood = av.find('**/cogFood')
            if not cogFood.isEmpty():
                cogFood.removeNode()

    def detachFoodFromToon(self, avId):
        cogFood = None
        self.toonFoodStatus[avId] = None
        av = base.cr.doId2do.get(avId)
        if av:
            # If local av, enable stickers here
            if av.isLocal() and self.battleTwoEmoteDisableBody:
                self.battleTwoEmoteDisableBody = False
                TTEmote.globalEmote.releaseBody(base.localAvatar, 'DistributedBossbotBoss.detachFoodFromToon')
            cogFood = av.find('**/cogFood')
            if not cogFood.isEmpty():
                # retval = cogFood
                cogFood.wrtReparentTo(render)
            curAnim = av.suit.getCurrentAnim()
            self.notify.debug('curAnim=%s' % curAnim)
            if curAnim == 'tray-walk':
                av.suit.loop('run')
            elif curAnim == 'tray-neutral':
                av.suit.loop('neutral')
            else:
                self.notify.warning("don't know what to do with anim=%s" % curAnim)

        return cogFood

    def setTable(self, table, tableIndex):
        self.tables[tableIndex] = table

    def localToonTouchedChair(self, tableIndex, chairIndex):
        avId = base.localAvatar.doId
        if avId in self.toonFoodStatus and self.toonFoodStatus[avId] is not None:
            self.sendUpdate('requestServeFood', [tableIndex, chairIndex])

    def toonServeFood(self, avId, tableIndex, chairIndex):
        food = self.detachFoodFromToon(avId)
        table = self.tables[tableIndex]
        table.serveFood(food, chairIndex)

    def enterPrepareBattleThree(self):
        self.calcNotDeadList()
        self.battleANode.setPosHpr(*BossCogGlobals.DinerBattleAPosHpr)
        self.battleBNode.setPosHpr(*BossCogGlobals.DinerBattleBPosHpr)
        self.cleanupIntervals()
        self.controlToons()
        self.setToonsToNeutral(self.involvedToons)
        for toonId in self.involvedToons:
            toon = self.cr.doId2do.get(toonId)
            if toon:
                self.putToonInCogSuit(toon)

        intervalName = 'PrepareBattleThreeMovie'
        seq = Sequence(self.makePrepareBattleThreeMovie(), Func(self.__onToBattleThree), name=intervalName)
        seq.start()
        self.storeInterval(seq, intervalName)
        self.acceptOnce('skipCutscene', self.__onToBattleThree)

    def calcNotDeadList(self):
        if not self.notDeadList:
            self.notDeadList = []
            for tableIndex in range(len(self.tables)):
                table = self.tables[tableIndex]
                tableInfo = table.getNotDeadInfo()
                self.notDeadList += tableInfo

    def exitPrepareBattleThree(self):
        self.ignore('skipCutscene')
        self.clearInterval('PrepareBattleThreeMovie')

    def __onToBattleThree(self, elapsedTime = 0):
        self.doneBarrier('PrepareBattleThree')

    def makePrepareBattleThreeMovie(self):
        loseSuitCamAngle = (0, 19, 6, -180, -5, 0)

        def slowMusic(speed):
            base.musicMgr.setPlayRate(self.battleTwoMusic, speed)

        track = Sequence(
            Func(camera.reparentTo, self),
            Func(camera.setPos, Point3(0, -45, 5)),
            Func(camera.setHpr, Point3(0, 14, 0)),
            Func(self.setChatAbsolute, TTL.BossbotPhase3Speech1, CFSpeech),
            Wait(3.0),
            Parallel(Func(self.setChatAbsolute, TTL.BossbotPhase3Speech2, CFSpeech), LerpFunctionInterval(slowMusic, fromData=1.0, toData=0.0, duration=2.0)),
            Wait(3.0),
            Func(camera.setPosHpr, base.localAvatar, *loseSuitCamAngle),
            Wait(1.0),
            self.loseCogSuits(self.toonsA + self.toonsB, base.localAvatar, loseSuitCamAngle),
            self.toonNormalEyes(self.involvedToons),
            Wait(2),
            Func(camera.reparentTo, self),
            Func(camera.setPos, Point3(0, -45, 5)),
            Func(camera.setHpr, Point3(0, 14, 0)),
            Func(self.setChatAbsolute, TTL.BossbotPhase3Speech3, CFSpeech),
            Wait(3.0),
            Func(self.clearChat))

        return track

    def enterBattleThree(self):
        base.discord.applyPreset('boss-c-4')
        self.cleanupIntervals()
        self.calcNotDeadList()
        for table in list(self.tables.values()):
            table.setAllDinersToSitNeutral()

        self.battleANode.setPosHpr(*BossCogGlobals.DinerBattleAPosHpr)
        self.battleBNode.setPosHpr(*BossCogGlobals.DinerBattleBPosHpr)
        self.setToonsToNeutral(self.involvedToons)
        for toonId in self.involvedToons:
            toon = self.cr.doId2do.get(toonId)
            if toon:
                toon.takeOffSuit()

        # mult = 1
        # localAvatar.inventory.setBattleCreditMult(mult)
        self.setBattleCreditMult(2)
        self.toonsToBattlePosition(self.toonsA, self.battleANode)
        self.toonsToBattlePosition(self.toonsB, self.battleBNode)
        self.releaseToons()

        #Readjust camera in case of cutscene skip
        for toonId in self.involvedToons:
            toon = self.cr.doId2do.get(toonId)
            if toon and toon == localAvatar:
                if toonId in self.toonsA:
                    base.camera.reparentTo(self.battleANode)
                else:
                    base.camera.reparentTo(self.battleBNode)

        base.musicMgr.playMusic(self.battleThreeMusic, looping=1, volume=0.9)
        if self.departmentExpBar:
            self.departmentExpBar.hide()
            self.departmentExpBar.stop()
            self.departmentExpBar.destroy()
        base.cr.gameGui.expBar.show()

    def exitBattleThree(self):
        self.cleanupBattles()
        # localAvatar.inventory.setBattleCreditMult(1)

    def claimOneChair(self, suit: DistributedSuitBase):
        if self.notDeadList:
            suitChair = [ci for ci in self.notDeadList if suit in ci]
            if suitChair:
                suitChair = suitChair[0]
                self.notDeadList.remove(suitChair)
                return suitChair

    def enterPrepareBattleFour(self):
        self.releaseToons(finalBattle=1)
        self.controlToons()
        intervalName = 'PrepareBattleFourMovie'
        seq = Sequence(self.makePrepareBattleFourMovie(), Func(self.__onToBattleFour), name=intervalName)
        seq.start()
        self.storeInterval(seq, intervalName)
        base.musicMgr.playMusic(self.battleFourMusic, looping=1, volume=0.9)
        self.acceptOnce('skipCutscene', self.__onToBattleFour)

    def exitPrepareBattleFour(self):
        self.ignore('skipCutscene')
        self.clearInterval('PrepareBattleFourMovie')

    def makePrepareBattleFourMovie(self):
        rToon = self.resistanceToon
        offsetZ = rToon.suit.getHeight() / 2.0
        track = Sequence(
            Func(self.__showResistanceToon, True),
            Func(rToon.setPos, Point3(0, -5, 0)),
            Func(rToon.setHpr, Point3(0, 0, 0)),
            Func(camera.reparentTo, rToon),
            Func(camera.setPos, Point3(0, 13, 3 + offsetZ)),
            Func(camera.setHpr, Point3(-180, 0, 0)),
            Func(self.banquetDoor.setH, 90),
            Func(rToon.setChatAbsolute, TTL.BossbotRTPhase4Speech1, CFSpeech),
            Wait(4.0),
            Func(rToon.setChatAbsolute, TTL.BossbotRTPhase4Speech2, CFSpeech),
            Wait(4.0),
            Func(rToon.setChatAbsolute, TTL.BossbotRTPhase4Speech3, CFSpeech),
            Wait(4.0),
            Func(self.__hideResistanceToon),
            Func(camera.reparentTo, self),
            Func(camera.setPos, Point3(0, -45, 5)),
            Func(camera.setHpr, Point3(0, 14, 0)),
            Func(self.setChatAbsolute, TTL.BossbotPhase4Speech1, CFSpeech),
            Func(self.banquetDoor.setH, 0),
            Wait(3.0),
            Func(self.setChatAbsolute, TTL.BossbotPhase4Speech2, CFSpeech),
            Func(self.bossClub.setScale, 0.01),
            Func(self.bossClub.reparentTo, self.rightHandJoint),
            LerpScaleInterval(self.bossClub, 3, Point3(1, 1, 1)),
            Func(self.clearChat))

        return track

    def __onToBattleFour(self, elapsedTime = 0):
        self.doneBarrier('PrepareBattleFour')

    def enterBattleFour(self):
        base.discord.applyPreset('boss-c-5')
        base.cr.gameGui.expBar.hide()
        self.departmentExpBar = DepartmentExperienceBar.DepartmentExperienceBar(base.localAvatar.departmentExp[ToontownGlobals.DEPARTMENT_BOSSBOT], base.localAvatar.departmentLevels[ToontownGlobals.DEPARTMENT_BOSSBOT], ToontownGlobals.DEPARTMENT_BOSSBOT, base.localAvatar.style)
        self.departmentExpBar.setAvatar(base.localAvatar)
        self.departmentExpBar.setScale(0.075)
        self.departmentExpBar.reparentTo(base.a2dBottomLeft)
        self.departmentExpBar.start()
        DistributedBossCog.enterBattleFour(self)
        self.releaseToons(finalBattle=1)
        for toonId in self.involvedToons:
            toon = self.cr.doId2do.get(toonId)
            if toon:
                toon.startLookAround()
                toon.startSmooth()
                toon.wrtReparentTo(render)
                toon.setupToonNodes()
        self.setToonsToNeutral(self.involvedToons)
        for toonId in self.involvedToons:
            toon = self.cr.doId2do.get(toonId)
            if toon:
                toon.takeOffSuit()

        self.bossClub.reparentTo(self.rightHandJoint)
        self.generateHealthBar()
        self.updateHealthBar()
        self.healthGui.createBossCogHead()
        self.healthGui.moveInInitial()
        if not base.musicMgr.isMusicPlaying(self.battleFourMusic):
            base.musicMgr.playMusic(self.battleFourMusic, looping=1, volume=0.9)

        # Tell condition manager to pull up dept bars/table or golf state
        stateArgs = ConditionGlobals.ConditionStateArgs()
        stateArgs[ConditionGlobals.ConditionStateArg.BOSS] = self
        messenger.send(ConditionGlobals.SetStateMsg, [ConditionGlobals.ConditionState.BOSS_CEO, stateArgs])

    def exitBattleFour(self):
        DistributedBossCog.exitBattleFour(self)
        base.musicMgr.stopMusic(self.battleFourMusic)
        self.stopMove()

    def d_hitBoss(self, bossDamage):
        self.sendUpdate('hitBoss', [bossDamage])

    def d_ballHitBoss(self, bossDamage):
        self.sendUpdate('ballHitBoss', [bossDamage])

    @property
    def dizzyMusic(self):
        return self.battleFourDizzyMusic

    @property
    def unDizzyMusic(self):
        return self.battleFourMusic

    def setBossDamage(self, bossDamage, recoverRate, recoverStartTime):
        if bossDamage > self.bossDamage:
            delta = bossDamage - self.bossDamage
            self.flashRed()
            self.showHpText(-delta, scale=5)

        self.bossDamage = bossDamage
        self.healthGui.updateHealth(self.bossMaxDamage - self.bossDamage)
        self.updateHealthBar()
        messenger.send(ConditionGlobals.RefreshMsg)

    def updateDamageDealt(self, avId, damageDealt):
        self.healthGui.updateDamageDealt(avId, damageDealt)

    def updateSpeedDamageDealt(self, avId, speedDamageDealt):
        self.healthGui.updateSpeedDamageDealt(avId, speedDamageDealt)

    def updateStunCount(self, avId):
        self.healthGui.updateStunCount(avId)

    def setMaxHp(self, hp):
        self.bossMaxDamage = hp
        self.healthGui.setMaxHp(self.bossMaxDamage)
        messenger.send(ConditionGlobals.RefreshMsg)

    def setGolfSpot(self, golfSpot, golfSpotIndex):
        self.golfSpots[golfSpotIndex] = golfSpot

    def enterVictory(self):
        self.cleanupIntervals()
        self.cleanupAttacks()
        self.doAnimate('Ff_neutral', now=1)
        if hasattr(self, 'tableIndex'):
            table = self.tables[self.tableIndex]
            table.tableGroup.hide()
        self.loop('neutral')
        localAvatar.setCameraFov(ToontownGlobals.BossBattleCameraFov)
        self.clearChat()
        self.controlToons()
        base.localAvatar.setFriendsListButtonActive(0)
        self.setToonsToNeutral(self.involvedToons)
        self.happy = 1
        self.raised = 1
        self.forward = 1
        if self.dizzy:
            self.setDizzy(0)
        intervalName = 'VictoryMovie'
        seq = Sequence(self.makeVictoryMovie(), Func(self.__continueVictory), name=intervalName)
        seq.start()
        self.storeInterval(seq, intervalName)
        base.musicMgr.playMusic(self.killMusic, looping=1, volume=0.9)
        if self.departmentExpBar:
            self.departmentExpBar.hide()
            self.departmentExpBar.stop()
            self.departmentExpBar.destroy()
        base.cr.gameGui.expBar.show()

    def __continueVictory(self):
        self.stopAnimate()
        if self.healthGui:
            self.healthGui.moveOutEnd()
        self.doneBarrier('Victory')

    def exitVictory(self):
        self.stopAnimate()
        self.unstash()
        localAvatar.setCameraFov(settings['fieldofview'] + 8)
        if not self.victoryAndBattleFourMatch:
            base.musicMgr.stopMusic(self.battleFourMusic)

    def makeVictoryMovie(self):
        self.show()
        dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
        dustCloud.reparentTo(self)
        dustCloud.setPos(0, -10, 3)
        dustCloud.setScale(4)
        dustCloud.wrtReparentTo(self.geom)
        dustCloud.createTrack(12)
        newHpr = self.getHpr()
        newHpr.setX(newHpr.getX() + 180)
        bossTrack = Sequence(
            Func(self.show),
            Func(camera.reparentTo, self),
            Func(camera.setPos, Point3(0, -35, 25)),
            Func(camera.setHpr, Point3(0, -20, 0)),
            Func(self.setChatAbsolute, TTL.BossbotRewardSpeech1, CFSpeech),
            Wait(3.0),
            Func(self.setChatAbsolute, TTL.BossbotRewardSpeech2, CFSpeech),
            Wait(2.0),
            Func(self.clearChat),
            Parallel(
                Sequence(
                    Wait(0.5),
                    Func(self.demotedCeo.setPos, self.getPos()),
                    Func(self.demotedCeo.setHpr, newHpr),
                    Func(self.hide),
                    Wait(0.5),
                    Func(self.demotedCeo.reparentTo, self.geom),
                    Func(self.demotedCeo.unstash)),
                Sequence(dustCloud.track)),
            Wait(2.0),
            Func(dustCloud.destroy))

        return bossTrack

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
                delayDeletes.append(DelayDelete.DelayDelete(toon, 'BossbotBoss.enterReward'))

        ival.delayDeletes = delayDeletes
        ival.start()
        self.storeInterval(ival, intervalName)
        if not self.victoryAndBattleFourMatch:
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
        self.resistanceToon.reparentTo(render)
        self.resistanceToon.setPosHpr(*BossCogGlobals.BossbotRTEpiloguePosHpr)
        self.resistanceToon.loop('Sit')
        self.__arrangeToonsAroundResistanceToonForReward()
        camera.reparentTo(render)
        camera.setPos(self.resistanceToon, -9, 12, 6)
        camera.lookAt(self.resistanceToon, 0, 0, 3)
        intervalName = 'EpilogueMovie'
        seq = Sequence(self.makeEpilogueMovie(), name=intervalName)
        seq.start()
        self.storeInterval(seq, intervalName)
        self.accept('nextChatPage', self.__epilogueChatNext)
        self.accept('doneChatPage', self.__doneEpilogue)
        base.musicMgr.playMusic(self.epilogueMusic, looping=1, volume=0.9)

    def __epilogueChatNext(self, pageNumber, elapsed):
        if pageNumber == self.localUniteEffectPageNumber:
            self.handleLocalUniteEffect()

    def __doneEpilogue(self, elapsedTime = 0):
        intervalName = 'EpilogueMovieToonAnim'
        self.ignore('nextChatPage')
        self.ignore('doneChatPage')
        self.clearInterval(intervalName)
        track = Parallel(Sequence(Wait(0.5), Func(self.localToonToSafeZone)))
        self.storeInterval(track, intervalName)
        track.start()

    def exitEpilogue(self):
        self.clearInterval('EpilogueMovieToonAnim')
        self.unstash()
        base.musicMgr.stopMusic(self.epilogueMusic)

    def makeEpilogueMovie(self):
        epSpeech = TTLocalizer.BossbotRTCongratulations
        epSpeech = self.__talkAboutPromotion(epSpeech)
        bossTrack = Sequence(Func(self.resistanceToon.request, 'Neutral'), Func(self.resistanceToon.setLocalPageChat, epSpeech, 0))
        return bossTrack

    def __talkAboutPromotion(self, speech):
        if (self.prevCogSuitLevel < ToontownGlobals.MaxCogSuitLevel) or (self.prevCogSuitReviveLevel > -1 and self.prevCogSuitLevel < 49):
            newCogSuitLevel = localAvatar.getCogLevels()[CogDisguiseGlobals.dept2deptIndex(self.style.dept)]
            newCogSuitReviveLevel = localAvatar.getCogReviveLevels()[CogDisguiseGlobals.dept2deptIndex(self.style.dept)]
            newCogSuitType = localAvatar.getCogTypes()[CogDisguiseGlobals.dept2deptIndex(self.style.dept)]
            if newCogSuitLevel == ToontownGlobals.MaxCogSuitLevel:
                speech += TTLocalizer.BossbotRTLastPromotion % (ToontownGlobals.MaxCogSuitLevel + 1)
            if newCogSuitLevel in ToontownGlobals.CogSuitHPLevels and newCogSuitType != 6:
                speech += TTLocalizer.BossbotRTHPBoost
            if newCogSuitReviveLevel == ToontownGlobals.MaxCogSuitLevel:
                speech += TTLocalizer.BossbotRTLastRevivePromotion % (ToontownGlobals.MaxCogSuitLevel + 1)
            if newCogSuitReviveLevel in ToontownGlobals.CogReviveSuitHPLevels and newCogSuitReviveLevel != self.prevCogSuitReviveLevel:
                speech += TTLocalizer.BossbotRTHPBoost
            if self.prevCogSuitType != 4 and newCogSuitType == 4:
                speech += TTLocalizer.BossbotRTTeleportAccess
        else:
            speech += TTLocalizer.BossbotRTMaxed % (ToontownGlobals.MaxCogSuitLevel + 1)
        if self.numPinkSlipsEarned == 1:
            speech += TTLocalizer.BossbotRTPinkSlipsRewardS.format(self.numPinkSlipsEarned)
        else:
            speech += TTLocalizer.BossbotRTPinkSlipsReward.format(self.numPinkSlipsEarned)
        speech = self.handleUniteSpeech(speech)
        return speech

    def __arrangeToonsAroundResistanceToonForReward(self):
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
                toon.loop('neutral')
                toon.show()

    def doDirectedAttack(self, avId, attackCode):
        toon = base.cr.doId2do.get(avId)
        if toon:
            distance = toon.getDistance(self)
            gearRoot = self.rotateNode.attachNewNode('gearRoot-atk%d' % self.numAttacks)
            gearRoot.setZ(10)
            gearRoot.setTag('attackCode', str(attackCode))
            gearModel = self.getGearFrisbee()
            gearModel.setScale(0.2)
            gearRoot.headsUp(toon)
            toToonH = PythonUtil.fitDestAngle2Src(0, gearRoot.getH() + 180)
            gearRoot.lookAt(toon)
            neutral = 'Fb_neutral'
            if not self.twoFaced:
                neutral = 'Ff_neutral'
            gearTrack = Parallel()
            for i in range(4):
                nodeName = '%s-%s' % (str(i), globalClock.getFrameTime())
                node = gearRoot.attachNewNode(nodeName)
                node.hide()
                node.setPos(0, 5.85, 4.0)
                gearModel.instanceTo(node)
                x = random.uniform(-5, 5)
                z = random.uniform(-3, 3)
                h = random.uniform(-720, 720)
                if i == 2:
                    x = 0
                    z = 0

                def detachNode(node):
                    if not node.isEmpty():
                        node.detachNode()
                    return Task.done

                def detachNodeLater(node = node):
                    if node.isEmpty():
                        return
                    center = node.node().getBounds().getCenter()
                    node.node().setBounds(BoundingSphere(center, distance * 1.5))
                    node.node().setFinal(1)
                    self.doMethodLater(0.005, detachNode, 'detach-%s-%s' % (gearRoot.getName(), node.getName()), extraArgs=[node])

                gearTrack.append(Sequence(Wait(i * 0.15), Func(node.show), Parallel(node.posInterval(1, Point3(x, distance, z), fluid=1), node.hprInterval(1, VBase3(h, 0, 0), fluid=1)), Func(detachNodeLater)))

            if not self.raised:
                neutral1Anim = self.getAnim('down2Up')
                self.raised = 1
            else:
                neutral1Anim = ActorInterval(self, neutral, startFrame=48)

            throwAnim = self.getAnim('throw')
            neutral2Anim = ActorInterval(self, neutral)
            extraAnim = Sequence()

            def detachGearRoot(task, gearRoot = gearRoot):
                if not gearRoot.isEmpty():
                    gearRoot.detachNode()

                return task.done

            def detachGearRootLater(gearRoot = gearRoot):
                if gearRoot.isEmpty():
                    return
                self.doMethodLater(0.01, detachGearRoot, 'detach-%s' % gearRoot.getName())

            seq = Sequence(ParallelEndTogether(self.pelvis.hprInterval(1, VBase3(toToonH, 0, 0)), neutral1Anim), extraAnim, Parallel(Sequence(Wait(0.19), gearTrack, Func(detachGearRootLater), self.pelvis.hprInterval(0.2, VBase3(0, 0, 0))), Sequence(throwAnim, neutral2Anim)))
            self.doAnimate(seq, now=1, raised=1)

    def stopMove(self):
        if self.moveTrack:
            self.moveTrack.pause()
            self.moveTrack = None

    def setAttackCode(self, attackCode, avId = 0):
        if self.state != 'BattleFour':
            return

        self.numAttacks += 1
        self.notify.debug('numAttacks=%d' % self.numAttacks)
        self.attackCode = attackCode
        self.attackAvId = avId
        if attackCode == BossCogGlobals.BossCogMoveAttack:
            self.setDizzy(0)
        elif attackCode == BossCogGlobals.BossCogGolfAttack:
            self.setDizzy(0)
            self.cleanupAttacks()
            self.attackTime.tick()
            self.doGolfAttack(avId, attackCode)
        elif attackCode == BossCogGlobals.BossCogDizzyNow:
            self.setDizzy(1)
            self.cleanupAttacks()
            self.doAnimate('hit', happy=1, now=1)
        elif attackCode == BossCogGlobals.BossCogSwatLeft:
            self.setDizzy(0)
            self.doAnimate('ltSwing', now=1)
        elif attackCode == BossCogGlobals.BossCogSwatRight:
            self.setDizzy(0)
            self.doAnimate('rtSwing', now=1)
        elif attackCode == BossCogGlobals.BossCogAreaAttack:
            self.setDizzy(0)
            self.doAnimate('areaAttack', now=1)
        elif attackCode == BossCogGlobals.BossCogFrontAttack:
            self.setDizzy(0)
            self.doAnimate('frontAttack', now=1)
        elif attackCode == BossCogGlobals.BossCogRecoverDizzyAttack:
            self.setDizzy(0)
            self.doAnimate('frontAttack', now=1)
        elif attackCode in (BossCogGlobals.BossCogDirectedAttack,
                            BossCogGlobals.BossCogGearDirectedAttack):
            self.setDizzy(0)
            self.attackTime.tick()
            self.doDirectedAttack(avId, attackCode)
        elif attackCode == BossCogGlobals.BossCogGolfAreaAttack:
            self.setDizzy(0)
            self.attackTime.tick()
            self.doGolfAreaAttack()
        elif attackCode == BossCogGlobals.BossCogNoAttack:
            self.setDizzy(0)
            self.doAnimate(None, raised=1)
        elif attackCode == BossCogGlobals.BossCogOvertimeAttack:
            self.setDizzy(0)
            self.cleanupAttacks()
            self.doOvertimeAttack(avId)

    def setSpeedDamage(self, currSpeedDamage, recoverRate, timestamp):
        recoverStartTime = globalClockDelta.networkToLocalTime(timestamp)
        self.currSpeedDamage = currSpeedDamage
        self.speedRecoverRate = recoverRate
        self.speedRecoverStartTime = recoverStartTime
        speedFraction = max(1 - currSpeedDamage / self.maxSpeedDamage, 0)
        self.treads.setColorScale(1, speedFraction, speedFraction, 1)
        self.calcPlayrate()
        taskName = 'RecoverSpeedDamage'
        taskMgr.remove(taskName)
        if self.speedRecoverRate:
            taskMgr.add(self.__recoverSpeedDamage, taskName)

    def calcPlayrate(self):
        playrate = float(max(1 - self.currSpeedDamage / self.maxSpeedDamage, 0) * self.maxPlayrate)
        if playrate < 1.0:
            self.ANIM_PLAYRATE = 1.0
        else:
            self.ANIM_PLAYRATE = playrate

    def __recoverSpeedDamage(self, task):
        currSpeedDamage = self.speed_damage
        speedFraction = max(1 - currSpeedDamage / self.maxSpeedDamage, 0)
        self.treads.setColorScale(1, speedFraction, speedFraction, 1)
        return task.cont

    def doMoveAttack(self, tableIndex: int, x: float, y: float, arrivalTime: int) -> None:
        """General interval to roll the CEO to his target by the specified time.
        """
        self.stopMove()

        self.tableIndex = tableIndex
        self.target = Point3(x, y, 0)

        table = self.tables[tableIndex]
        foo = render.attachNewNode('foo')
        foo.setPos(self.getPos())
        foo.setHpr(self.getHpr())
        foo.lookAt(table.getLocator())
        to_hpr = foo.getHpr()
        to_hpr.setX(to_hpr.getX() - 180)
        foo.removeNode()

        self.target_h = to_hpr[0]

        now = globalClock.getFrameTime()
        self.arrivalTime = globalClockDelta.networkToLocalTime(arrivalTime, now)

        available_time = self.arrivalTime - now

        if available_time > 0:
            turn_speed = self.currentTurnSpeed
            roll_speed = self.currentRollSpeed

            # How long will it take to rotate to position?
            curr_h = self.getH()
            curr_pos = self.getPos()

            table_h = PythonUtil.reduceAngle(self.target_h)
            table_h = PythonUtil.fitDestAngle2Src(curr_h, table_h)

            turn_time = abs(table_h - curr_h) / turn_speed

            # And how long will it take to roll to position?
            distance = Vec3(self.target - curr_pos).length()
            roll_time = distance / roll_speed

            denom = turn_time + roll_time

            if denom != 0:
                # Fit that within our available time.
                time_compress = min(available_time / denom, 1)

                turn_time_compressed = turn_time * time_compress
                roll_time_compressed = roll_time * time_compress

                tread_speed = self.currentTreadSpeed

                if table_h < curr_h:
                    tread_speed_turn = tread_speed
                else:
                    tread_speed_turn = -tread_speed

                delta_pos = self.target - curr_pos

                self.moveTrack = Sequence(
                    Func(self.headsUp, self.target),
                    Parallel(
                        self.hprInterval(turn_time_compressed, Vec3(table_h, 0, 0), self.getHpr()),
                        self.rollLeftTreads(turn_time_compressed, tread_speed_turn),
                        self.rollRightTreads(turn_time_compressed, -tread_speed_turn)
                    ),
                    Parallel(
                        LerpFunctionInterval(self.rollBoss, duration=roll_time_compressed, extraArgs=[curr_pos, delta_pos]),
                        self.rollLeftTreads(roll_time_compressed, tread_speed),
                        self.rollRightTreads(roll_time_compressed, tread_speed)
                    ),
                )
                self.moveTrack.start()
        else:
            self.setPos(self.target)
            self.setH(self.target_h)

    @property
    def speed_damage(self):
        now = globalClock.getFrameTime()
        elapsed = now - self.speedRecoverStartTime
        return max(self.currSpeedDamage - self.speedRecoverRate * elapsed / 60.0, 0)

    @property
    def fractionalSpeedDamage(self) -> float:
        result = self.speed_damage / self.maxSpeedDamage
        return result

    @property
    def currentTurnSpeed(self) -> float:
        min_speed = BossCogGlobals.BossbotTurnSpeedMin
        max_speed = BossCogGlobals.BossbotTurnSpeedMax * self.tierSpeedMult
        result = (max_speed - (max_speed - min_speed) * self.fractionalSpeedDamage) * self.overtimeSpeedMult
        return result

    @property
    def currentRollSpeed(self) -> float:
        min_speed = BossCogGlobals.BossbotRollSpeedMin
        max_speed = BossCogGlobals.BossbotRollSpeedMax * self.tierSpeedMult
        result = (max_speed - (max_speed - min_speed) * self.fractionalSpeedDamage) * self.overtimeSpeedMult
        return result

    @property
    def currentTreadSpeed(self) -> float:
        min_speed = BossCogGlobals.BossbotTreadSpeedMin
        max_speed = BossCogGlobals.BossbotTreadSpeedMax * self.tierSpeedMult
        result = (max_speed - (max_speed - min_speed) * self.fractionalSpeedDamage) * self.overtimeSpeedMult
        return result

    @property
    def overtimeSpeedMult(self) -> float:
        if self.desperationState == 1:
            return 1.5
        elif self.desperationState == 0:
            return 1.2
        return 1.0

    @property
    def tierSpeedMult(self) -> float:
        return 1.0

    def doZapToon(self, toon, pos = None, hpr = None, ts = 0, fling = 1, shake = 1):
        zapName = toon.uniqueName('zap')
        self.clearInterval(zapName)
        zapTrack = Sequence(name=zapName)
        if toon == localAvatar:
            self.toOuchMode()
            localAvatar.stunToon()
            messenger.send('interrupt-pie')
            self.enableLocalToonSimpleCollisions()
        else:
            zapTrack.append(Func(toon.stopSmooth))

        def getSlideToPos(toon = toon):
            return render.getRelativePoint(toon, Point3(0, -5, 0))

        if pos is not None and hpr is not None:
            (zapTrack.append(Func(toon.setPosHpr, pos, hpr)),)

        toonTrack = Parallel()
        if shake and toon == localAvatar:
            toonTrack.append(Sequence(Func(camera.setZ, camera, 1), Wait(0.15), Func(camera.setZ, camera, -2), Wait(0.15), Func(camera.setZ, camera, 1)))

        animName = 'slip-backward' if fling else 'slip-forward'
        slipInterval = Parallel(ActorInterval(toon, animName))
        if toon.isDisguised and toon.suit:
            slipInterval.append(ActorInterval(toon.suit, animName))
            slipInterval.append(Sequence(
                Wait(0.5),
                SoundInterval(loader.loadSfx('phase_5/audio/sfx/Toon_bodyfall_synergy.ogg'), node=toon)
            ))

        if fling:
            if self.isToonRoaming(toon.doId):
                toonTrack += [slipInterval]
                toonTrack += [toon.posInterval(0.5, getSlideToPos, fluid=1)]
        else:
            toonTrack += [slipInterval]

        zapTrack.append(toonTrack)
        if toon == localAvatar:
            zapTrack.append(Func(self.disableLocalToonSimpleCollisions))
            currentState = self.state
            if currentState in ('BattleFour', 'BattleTwo'):
                zapTrack.append(Func(self.toFinalBattleMode))
            else:
                self.notify.warning('doZapToon going to walkMode, how did this happen?')
                zapTrack.append(Func(self.toWalkMode))
        else:
            zapTrack.append(Func(toon.startSmooth))
        if ts > 0:
            startTime = ts
        else:
            zapTrack = Sequence(Wait(-ts), zapTrack)
            startTime = 0

        zapTrack.append(Func(self.clearInterval, zapName))
        zapTrack.delayDelete = DelayDelete.DelayDelete(toon, 'BossbotBoss.doZapToon')
        zapTrack.start(startTime)
        self.storeInterval(zapTrack, zapName)

    def zapLocalToon(self, attackCode, origin = None):
        if self.localToonIsSafe or localAvatar.ghostMode or localAvatar.isStunned:
            return
        if globalClock.getFrameTime() < self.lastZapLocalTime + 1.0:
            return
        else:
            self.lastZapLocalTime = globalClock.getFrameTime()

        if attackCode in (BossCogGlobals.BossCogGolfAttack, BossCogGlobals.BossCogGolfAreaAttack,
                          BossCogGlobals.BossCogGearDirectedAttack) and self.dizzy:
            return

        self.notify.debug('zapLocalToon frameTime=%s' % globalClock.getFrameTime())
        messenger.send('interrupt-pie')
        place = self.cr.playGame.getPlace()
        currentState = None
        if place:
            currentState = place.getCurrentOrNextState()

        if currentState != 'walk' and currentState != 'finalBattle' and currentState != 'crane':
            return

        toon = localAvatar
        fling = 1
        shake = 0
        if attackCode == BossCogGlobals.BossCogAreaAttack:
            fling = 0
            shake = 1
        if fling:
            if origin is None:
                origin = self
            if self.isToonRoaming(toon.doId):
                camera.wrtReparentTo(render)
                toon.headsUp(origin)
                camera.wrtReparentTo(toon)
        bossRelativePos = toon.getPos(self.getGeomNode())
        bp2d = Vec2(bossRelativePos[0], bossRelativePos[1])
        bp2d.normalize()
        pos = toon.getPos()
        hpr = toon.getHpr()
        timestamp = globalClockDelta.getFrameNetworkTime()
        self.sendUpdate('zapToon', [pos[0],
            pos[1],
            pos[2],
            hpr[0],
            hpr[1],
            hpr[2],
            bp2d[0],
            bp2d[1],
            attackCode,
            timestamp])

        self.doZapToon(toon, fling=fling, shake=shake)

    def getToonTableIndex(self, toonId):
        tableIndex = -1
        for table in list(self.tables.values()):
            if table.avId == toonId:
                tableIndex = table.index
                break

        return tableIndex

    def getToonGolfSpotIndex(self, toonId):
        golfSpotIndex = -1
        for golfSpot in list(self.golfSpots.values()):
            if golfSpot.avId == toonId:
                golfSpotIndex = golfSpot.index
                break

        return golfSpotIndex

    def isToonOnTable(self, toonId):
        result = self.getToonTableIndex(toonId) != -1
        return result

    def isToonOnGolfSpot(self, toonId):
        result = self.getToonGolfSpotIndex(toonId) != -1
        return result

    def isToonRoaming(self, toonId):
        result = not self.isToonOnTable(toonId) and not self.isToonOnGolfSpot(toonId)
        return result

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
        cnp = golfRoot.attachNewNode(cn)
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
            self.ballLaunch = NodePath('')
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
                    return Task.done

                def detachNodeLater(node = node):
                    if node.isEmpty():
                        return
                    node.node().setBounds(BoundingSphere(Point3(0, 0, 0), distance * 1.5))
                    node.node().setFinal(1)
                    self.doMethodLater(0.005, detachNode, 'detach-%s-%s' % (gearRoot.getName(), node.getName()), extraArgs=[node])

                gearTrack.append(Sequence(Wait(26.0 / 24.0), Wait(i * 0.15), Func(node.show), Parallel(node.posInterval(1, Point3(x, y, z), fluid=1), node.hprInterval(1, VBase3(0, p, 0), fluid=1)), Func(detachNodeLater)))

            if not self.raised:
                neutral1Anim = self.getAnim('down2Up')
                self.raised = 1
            else:
                neutral1Anim = ActorInterval(self, neutral, startFrame=48)
            throwAnim = self.getAnim('golf_swing')
            neutral2Anim = ActorInterval(self, neutral)
            extraAnim = Sequence()

            def detachGearRoot(task, gearRoot = gearRoot):
                if not gearRoot.isEmpty():
                    gearRoot.detachNode()

                return task.done

            def detachGearRootLater(gearRoot = gearRoot):
                self.doMethodLater(0.01, detachGearRoot, 'detach-%s' % gearRoot.getName())

            seq = Sequence(ParallelEndTogether(self.pelvis.hprInterval(1, VBase3(toToonH, 0, 0)), neutral1Anim), extraAnim, Parallel(Sequence(Wait(0.19), gearTrack, Func(detachGearRootLater), self.pelvis.hprInterval(0.2, VBase3(0, 0, 0))), Sequence(throwAnim, neutral2Anim), Sequence(Wait(0.85), SoundInterval(self.swingClubSfx, node=self, duration=0.45, cutOff=300, listenerNode=base.localAvatar))))
            self.doAnimate(seq, now=1, raised=1)

    def doGolfAreaAttack(self):
        toons = []
        for toonId in self.involvedToons:
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

        gearModel = self.getGolfBall()
        toToonH = self.rotateNode.getH() + 360
        self.notify.debug('toToonH = %s' % toToonH)
        gearRoots = []
        allGearTracks = Parallel()
        for toon in toons:
            gearRoot = self.rotateNode.attachNewNode('gearRoot-atk%d-%d' % (self.numAttacks, toons.index(toon)))
            gearRoot.setZ(10)
            gearRoot.setTag('attackCode', str(BossCogGlobals.BossCogGolfAreaAttack))
            gearRoot.lookAt(toon)
            ballLaunch = NodePath('')
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
                # toonPos = toon.getPos(render)
                # nodePos = node.getPos(render)
                # vector = toonPos - nodePos
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
                    return Task.done

                def detachNodeLater(node = node):
                    if node.isEmpty():
                        return
                    node.node().setBounds(BoundingSphere(Point3(0, 0, 0), distance * 1.5))
                    node.node().setFinal(1)
                    self.doMethodLater(0.005, detachNode, 'detach-%s-%s' % (gearRoot.getName(), node.getName()), extraArgs=[node])

                gearTrack.append(Sequence(Wait(26.0 / 24.0), Wait(i * 0.15), Func(node.show), Parallel(node.posInterval(1, Point3(x, y, z), fluid=1), node.hprInterval(1, VBase3(0, p, 0), fluid=1)), Func(detachNodeLater)))

            allGearTracks.append(gearTrack)

        def detachGearRoots(gearRoots = gearRoots):
            for gearRoot in gearRoots:

                def detachGearRoot(task, gearRoot = gearRoot):
                    if not gearRoot.isEmpty():
                        gearRoot.detachNode()
                    return task.done

                if gearRoot.isEmpty():
                    continue
                self.doMethodLater(0.01, detachGearRoot, 'detach-%s' % gearRoot.getName())

            gearRoots = []

        rotateFire = Parallel(self.pelvis.hprInterval(2, VBase3(toToonH + 1440, 0, 0)), allGearTracks)
        seq = Sequence(Func(base.playSfx, self.warningSfx), Func(self.saySomething, TTLocalizer.GolfAreaAttackTaunt), ParallelEndTogether(self.pelvis.hprInterval(2, VBase3(toToonH, 0, 0)), neutral1Anim), extraAnim, Parallel(Sequence(rotateFire, Func(detachGearRoots), Func(self.pelvis.setHpr, VBase3(0, 0, 0))), Sequence(throwAnim, neutral2Anim), Sequence(Wait(0.85), SoundInterval(self.swingClubSfx, node=self, duration=0.45, cutOff=300, listenerNode=base.localAvatar))))
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

    def d_hitToon(self, toonId):
        self.sendUpdate('hitToon', [toonId])

    def toonGotHealed(self, toonId):
        toon = base.cr.doId2do.get(toonId)
        if toon:
            base.playSfx(self.toonUpSfx, node=toon)

    def toonDied(self, avId):
        DistributedBossCog.toonDied(self, avId)

        # If our toon died, get rid of the dept exp bar
        if avId == base.localAvatar.doId:
            if self.departmentExpBar:
                self.departmentExpBar.hide()
                self.departmentExpBar.stop()
                self.departmentExpBar.destroy()
            base.cr.gameGui.expBar.show()

    def localToonTouchedBeltToonup(self, beltIndex, toonupIndex, toonupNum):
        self.sendUpdate('requestGetToonup', [beltIndex, toonupIndex, toonupNum])

    def toonGotToonup(self, avId, beltIndex, toonupIndex, toonupNum):
        if self.belts[beltIndex]:
            self.belts[beltIndex].removeToonup(toonupIndex)
        toon = base.cr.doId2do.get(avId)
        if toon:
            base.playSfx(self.toonUpSfx, node=toon)

    def doOvertimeAttack(self, index):
        attackCode = BossCogGlobals.BossCogOvertimeAttack
        attackBelts = Sequence()
        self.desperationState = index
        if index < len(self.belts):
            belt = self.belts[index]
            self.saySomething(TTLocalizer.OvertimeAttackTaunts[index])
            if index:
                self.bossClubIntervals[0].finish()
                self.bossClubIntervals[1].loop()
            else:
                self.bossClubIntervals[1].finish()
                self.bossClubIntervals[0].loop()

            distance = belt.beltModel.getDistance(self)
            gearRoot = self.rotateNode.attachNewNode('gearRoot')
            gearRoot.setZ(10)
            gearRoot.setTag('attackCode', str(attackCode))
            gearModel = self.getGearFrisbee()
            gearModel.setScale(0.2)
            gearRoot.headsUp(belt.beltModel)
            toToonH = PythonUtil.fitDestAngle2Src(0, gearRoot.getH() + 180)
            gearRoot.lookAt(belt.beltModel)
            neutral = 'Fb_neutral'
            if not self.twoFaced:
                neutral = 'Ff_neutral'

            gearTrack = Parallel()
            for i in range(4):
                node = gearRoot.attachNewNode(str(i))
                node.hide()
                node.setPos(0, 5.85, 4.0)
                gearModel.instanceTo(node)
                x = random.uniform(-5, 5)
                z = random.uniform(-3, 3)
                h = random.uniform(-720, 720)
                gearTrack.append(Sequence(
                    Wait(i * 0.15), Func(node.show),
                    Parallel(
                        node.posInterval(1, Point3(x, distance, z), fluid=1),
                        node.hprInterval(1, VBase3(h, 0, 0), fluid=1)
                    ),
                    Func(node.detachNode)
                ))

            if not self.raised:
                neutral1Anim = self.getAnim('down2Up')
                self.raised = 1
            else:
                neutral1Anim = ActorInterval(self, neutral, startFrame=48)

            throwAnim = self.getAnim('throw')
            neutral2Anim = ActorInterval(self, neutral)

            seq = Sequence(
                ParallelEndTogether(self.pelvis.hprInterval(1, VBase3(toToonH, 0, 0)), neutral1Anim),
                Parallel(
                    Sequence(
                        Wait(0.19),
                        gearTrack,
                        Func(gearRoot.detachNode),
                        Func(self.explodeSfx.play),
                        self.pelvis.hprInterval(0.2, VBase3(0, 0, 0))
                    ),
                    Sequence(throwAnim, neutral2Anim)
                ),
                Func(belt.enterDesperation)
            )
            attackBelts.append(seq)

        self.notify.debug('attackBelts duration= %.2f' % attackBelts.getDuration())
        if index:
            self.maxPlayrate = 1.5
            self.calcPlayrate()
        else:
            self.maxPlayrate = 1.25
            self.calcPlayrate()
        self.doAnimate(attackBelts, now=1, raised=1)

    def setNumPinkSlipsEarned(self, slips):
        self.numPinkSlipsEarned = slips

    @property
    def uniteResistanceToon(self):
        return self.resistanceToon
