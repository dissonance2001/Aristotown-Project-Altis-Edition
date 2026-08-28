from functools import cmp_to_key
from direct.directnotify import DirectNotifyGlobal
from direct.fsm import FSM
from direct.interval.IntervalGlobal import *
from direct.task.Task import Task
from direct.task.TaskManagerGlobal import *
import math
from pandac.PandaModules import *
import random
from direct.gui.DirectGui import *

from toontown.battle import BattleProps
from direct.showutil import Effects
from direct.distributed import DistributedObject
from direct.directnotify import DirectNotifyGlobal
from direct.interval.IntervalGlobal import *
from direct.particles import ParticleEffect
from toontown.battle import BattleParticles
from direct.particles import ParticleEffect
from toontown.suit import SuitDNA
from toontown.suit import BossCutsceneSkip
from toontown.battle.BattleProps import *
from otp.otpbase import OTPGlobals
from toontown.battle import MovieToonVictory
from toontown.battle import BattleExperience
from toontown.battle import BattleBase
from toontown.battle import MovieUtil
from toontown.friends import FriendsListManager
from toontown.hood import ZoneUtil
from toontown.battle import RewardPanel
from toontown.suit import DistributedSuitBase
from toontown.suit import Suit
from toontown.battle import SuitBattleGlobals
from toontown.building import ElevatorConstants
from toontown.building import ElevatorUtils
from toontown.chat.ChatGlobals import *
from toontown.coghq import CogDisguiseGlobals
from toontown.distributed import DelayDelete
from toontown.nametag import NametagGlobals
from toontown.nametag.NametagGlobals import *
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import ToontownBattleGlobals

OneVideographerController = None
TTL = TTLocalizer

class DistributedVideographerBoss(DistributedObject.DistributedObject, FSM.FSM):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedVideographerBoss')
    numFakeGoons = 0

     # Some constants
    ballSpinDuration = 6.0

    # Names of Nodes
    discofloorNames = ['**/discofloor_%d' % i for i in range(6)]
    discoballNames = ['**/discoball_%d' % i for i in range(3)]
    stagelightNames = ['**/stagelight_%d' % i for i in range(5)]
    tableLocatorNames = ['**/tables_locator_%d' % (i + 1) for i in range(6)]

    # Stagelight ranges
    stagelightRanges = (
        (Vec3(-20, -20, -20), Vec3(20, 20, 20)),
        (Vec3(-20, -20, -20), Vec3(20, 20, 20)),
        (Vec3(-20, -20, -20), Vec3(20, 20, 20)),
        (Vec3(-20, -20, -20), Vec3(20, 20, 20)),
        (Vec3(-20, -20, -20), Vec3(20, 20, 20)),
    )

    # Chair Locator Node positions and headings
    chairLocatorPosH = (
        (Point3(8.2, 2.86, 0), 90),
        (Point3(8.2, -2.46, 0), 90),
        (Point3(3.06, -8.05, 0), 0),
        (Point3(-2.46, -8.05, 0), 0),
        (Point3(-8.2, -2.46, 0), -90),
        (Point3(-8.2, 2.86, 0), -90),
        (Point3(-2.46, 8.05, 0), 180),
        (Point3(3.06, 8.05, 0), 180),
    )

    # Index 0: Base position
    # Index 1: Scale Offset
    sitLocatorPos = {
        'a': (Point3(0.3, 1.5, 0.4), Point3(-0.3, -0.8, 2.5)),
        'b': (Point3(-0.2, 1.5, 0.5), Point3(0.0, -0.3, 2.0)),
        'c': (Point3(0.4, 2.08, 0.3), Point3(-0.5, -2.8, 2.2)),
    }

    # Indexes for random audience members that talk during intro
    # Index 0: Table Index
    # Index 1: Chair Index
    talkingAudienceIndices = (
        (5, 6),
        (5, 7)
    )

    suitCount = 48

    SUIT_TINT = (0.76, 0.76, 0.76, 1.0)

    def __init__(self, cr):
        DistributedObject.DistributedObject.__init__(self, cr)
        FSM.FSM.__init__(self, 'DistributedVideographerBoss')
        self.gotAllToons = 0
        self.toons = []
        self.toonsA = []
        self.toonsB = []
        self.involvedToons = []
        self.toonRequest = None
        self.battleNumber = 0
        self.battleId = 0
        self.battleAId = 0
        self.battleBId = 0
        self.battle = None
        self.battleA = None
        self.battleB = None
        self.battleRequest = None
        self.arenaSide = 0
        self.activeIntervals = {}
        self.cutsceneSkip = BossCutsceneSkip.BossCutsceneSkip(self)
        self.allowClickedNameTag = True
        self.battleANode = NodePath('videographerBattleA')
        self.battleBNode = NodePath('videographerBattleB')
        self.battleANode.setPosHpr(*ToontownGlobals.VideographerBossCogBattleAPosHpr)
        self.battleBNode.setPosHpr(*ToontownGlobals.VideographerBossCogBattleBPosHpr)
        self._controllerNode = NodePath('videographerInstanceController')
        self.pelvis = self._controllerNode.attachNewNode('pelvis')
        self.neck = self._controllerNode.attachNewNode('neck')
        self.pelvisForwardHpr = VBase3(0, 0, 0)
        self.pelvisReversedHpr = VBase3(-180, 0, 0)
        self.animatedHeadParts = []
        self.resistanceToon = None
        self.resistanceToonOnstage = 0
        self.fakeGoons = []
        self.cranes = {}
        self.safes = {}
        self.goons = []
        self.latency = 0.5
        self.battleDifficulty = 0
        self.geomFlashInterval = None
        self.bonusUnites = 0
        self.bossMaxDamage = ToontownGlobals.CashbotBossMaxDamage
        self.elevatorType = ElevatorConstants.ELEVATOR_ERCLAIM
        base.boss = self
        self.currHP = 0
        self.maxHP = self.bossMaxDamage
        self.bossDamage = 0
        self.rewardId = 0
        self.attackCode = ToontownGlobals.BossCogNoAttack
        self.attackAvId = 0
        self.__sequences = []
        self._highRollerIntroSetup = None
        self.toonRewardDicts = []
        self.toonRewardIds = []
        self.deathList = []
        self.uberList = []
        self.helpfulToons = []
        self.rewardPanel = None
        self.physicsMgr = None
        self.fnp = None
        self.titleText = None
        self.videographer = DistributedSuitBase.DistributedSuitBase(cr)
        suitDNA = SuitDNA.SuitDNA()
        suitDNA.newSuit('videog')
        self.style = suitDNA
        self.videographer.setDNA(suitDNA)
        self.videographer.setPickable(0)
        self.videographer.setDisplayName('Videographer\nTechbot\nLevel 99.mgr')
        self.videographer.doId = 0
        self.videographer.loop('sit-exec')
        self.videographer.setPosHpr(0, -133.5, -1.25, 180, 0, 0)
        self.videographer.reparentTo(render)

    def announceGenerate(self):
        global OneVideographerController
        DistributedObject.DistributedObject.announceGenerate(self)
        base.cr.forbidCheesyEffects(1)
        try:
            deptIndex = CogDisguiseGlobals.dept2deptIndex(self.style.dept)
            self.prevCogSuitLevel = localAvatar.getCogLevels()[deptIndex]
            self.prevCogSuitReviveLevel = localAvatar.getCogReviveLevels()[deptIndex]
        except:
            self.prevCogSuitLevel = 0
            self.prevCogSuitReviveLevel = 0
        self.heldObject = None
        self.bossDamage = 0
        self.currHP = 0
        self.loadEnvironment()
        self.physicsMgr = PhysicsManager()
        integrator = LinearEulerIntegrator()
        self.physicsMgr.attachLinearIntegrator(integrator)
        fn = ForceNode('gravity')
        self.fnp = self.geom.attachNewNode(fn)
        gravity = LinearVectorForce(0, 0, -32)
        fn.addForce(gravity)
        self.physicsMgr.addLinearForce(gravity)
        self.titleText = OnscreenText('Major Player Place\nThe High Roller', fg=(1, 1, 1, 1), shadow=(0, 0, 0, 1), font=ToontownGlobals.getSuitFont(), pos=(0, -0.5), scale=0.16, drawOrder=0, mayChange=1)
        self.titleText.hide()
        if OneVideographerController is not None and OneVideographerController is not self:
            self.notify.warning('Multiple High Roller instance controllers are visible.')
        OneVideographerController = self

    def disable(self):
        global OneVideographerController
        taskMgr.remove(self.uniqueName('highRollerInstanceReady'))
        taskMgr.remove(self.uniqueName('physics'))
        if self.toonRequest is not None:
            self.cr.relatedObjectMgr.abortRequest(self.toonRequest)
            self.toonRequest = None
        if self.battleRequest is not None:
            self.cr.relatedObjectMgr.abortRequest(self.battleRequest)
            self.battleRequest = None
        if self.cutsceneSkip:
            self.cutsceneSkip.cleanup()
        self.cleanupIntervals()
        self.cleanupBattles()
        base.cr.forbidCheesyEffects(0)
        self.__stopHighRollerMusic()
        self.unloadEnvironment()
        self.__cleanupResistanceToon()
        if self.fnp is not None and not self.fnp.isEmpty():
            self.fnp.removeNode()
        self.fnp = None
        if self.physicsMgr is not None:
            self.physicsMgr.clearLinearForces()
        self.physicsMgr = None
        if self.titleText is not None:
            self.titleText.destroy()
            self.titleText = None
        removeTint = Sequence(LerpColorScaleInterval(render, 0.1, Vec4(1, 1, 1, 1)))
        removeTint.start()
        if OneVideographerController is self:
            OneVideographerController = None
        if getattr(base, 'boss', None) is self:
            base.boss = None
        self.ignoreAll()
        DistributedObject.DistributedObject.disable(self)

    def delete(self):
        if self.cutsceneSkip:
            self.cutsceneSkip.delete()
            self.cutsceneSkip = None
        for actorName in ('highroller', 'majorplayer2', 'duckshuffler2'):
            actor = getattr(self, actorName, None)
            if actor is not None:
                try:
                    actor.cleanup()
                except:
                    pass
                setattr(self, actorName, None)
        for nodeName in ('battleANode', 'battleBNode', '_controllerNode'):
            node = getattr(self, nodeName, None)
            if node is not None and not node.isEmpty():
                node.removeNode()
        DistributedObject.DistributedObject.delete(self)

    def setBonusUnites(self, unites):
        self.bonusUnites = unites

    def setState(self, state):
        if self.cutsceneSkip:
            self.cutsceneSkip.stateChanged(state)
        self.request(state)

    def requestCutsceneSkipVote(self):
        self.sendUpdate('requestSkip', [])

    def setVoteSkips(self, voteTotal, playerTotal):
        if self.cutsceneSkip:
            self.cutsceneSkip.setVoteSkips(voteTotal, playerTotal)

    def setCutsceneSkip(self):
        if self.cutsceneSkip:
            self.cutsceneSkip.setCutsceneSkip()

    def setToonIds(self, involvedToons, toons, unused):
        self.involvedToons = involvedToons
        # Discord Rich Presence
        if localAvatar.doId in self.involvedToons:
            base.discord.applyPreset('videographer')
        self.toons = toons
        self.toonsA = toons
        self.toonsB = []
        if self.toonRequest is not None:
            self.cr.relatedObjectMgr.abortRequest(self.toonRequest)
        self.gotAllToons = 0
        if not self.involvedToons:
            self.toonRequest = None
            self.gotAllToons = 1
            messenger.send('gotAllToons')
            return
        self.toonRequest = self.cr.relatedObjectMgr.requestObjects(
            self.involvedToons,
            allCallback=self.__gotAllToons,
            eachCallback=self.gotToon)

    def gotToon(self, toon):
        return

    def __gotAllToons(self, toons):
        self.toonRequest = None
        self.gotAllToons = 1
        messenger.send('gotAllToons')

    def setBattleIds(self, battleNumber, battleId, unused):
        self.battleNumber = battleNumber
        self.battleId = battleId
        self.battleAId = battleId
        self.battleBId = 0
        if self.battleRequest is not None:
            self.cr.relatedObjectMgr.abortRequest(self.battleRequest)
            self.battleRequest = None
        if not battleId:
            self.battle = None
            self.battleA = None
            self.battleB = None
            return
        self.battleRequest = self.cr.relatedObjectMgr.requestObjects(
            [battleId], allCallback=self.__gotBattle)

    def __gotBattle(self, battles):
        self.battleRequest = None
        if not battles:
            self.battle = None
            self.battleA = None
            self.battleB = None
            return
        if self.battle and self.battle is not battles[0]:
            try:
                self.battle.cleanupBattle()
            except:
                pass
        self.battle = battles[0]
        self.battleA = self.battle
        self.battleB = None

    def setArenaSide(self, arenaSide):
        self.arenaSide = arenaSide

    def setBattleExperience(self, *args):
        if len(args) < 75:
            self.notify.warning('Invalid High Roller battle experience payload: %s' % (len(args),))
            return
        entries = []
        for index in range(8):
            start = index * 9
            entries.append(tuple(args[start:start + 9]))
        self.deathList = args[72]
        self.uberList = args[73]
        self.helpfulToons = args[74]
        self.toonRewardDicts = BattleExperience.genRewardDicts(tuple(entries))
        self.toonRewardIds = [entry[0] for entry in entries]

    def d_avatarEnter(self):
        self.sendUpdate('avatarEnter', [])

    def d_avatarExit(self):
        self.sendUpdate('avatarExit', [])

    def toonDied(self, avId):
        if avId == localAvatar.doId:
            self.localToonDied()

    def localToonDied(self):
        targetZone = ZoneUtil.getSafeZoneId(localAvatar.defaultZone)
        place = self.cr.playGame.getPlace()
        if place and hasattr(place, 'fsm'):
            place.fsm.request('died', [{
                'loader': ZoneUtil.getLoaderName(targetZone),
                'where': ZoneUtil.getWhereName(targetZone, 1),
                'how': 'teleportIn',
                'hoodId': targetZone,
                'zoneId': targetZone,
                'shardId': None,
                'avId': -1,
                'battle': 1,
            }])

    def storeInterval(self, interval, name):
        if name in self.activeIntervals:
            self.clearInterval(name, finish=1)
        self.activeIntervals[name] = interval
        if self.cutsceneSkip:
            self.cutsceneSkip.intervalStored(name, interval)

    def cleanupIntervals(self):
        if self.cutsceneSkip:
            self.cutsceneSkip.intervalsCleaned()
        for interval in list(self.activeIntervals.values()):
            try:
                interval.finish()
            except:
                pass
            DelayDelete.cleanupDelayDeletes(interval)
        self.activeIntervals = {}

    def clearInterval(self, name, finish=1):
        if name not in self.activeIntervals:
            return
        interval = self.activeIntervals[name]
        try:
            if finish:
                interval.finish()
            else:
                interval.pause()
        except:
            pass
        DelayDelete.cleanupDelayDeletes(interval)
        if name in self.activeIntervals:
            del self.activeIntervals[name]
        if self.cutsceneSkip:
            self.cutsceneSkip.intervalCleared(name)

    def cleanupBattles(self):
        if self.battle:
            try:
                self.battle.cleanupBattle()
            except:
                pass

    def hasLocalToon(self):
        return localAvatar.doId in self.involvedToons

    def controlToons(self):
        for toonId in self.involvedToons:
            toon = self.cr.doId2do.get(toonId)
            if toon:
                toon.stopLookAround()
                toon.stopSmooth()
        if self.hasLocalToon():
            self.toMovieMode()

    def releaseToons(self, finalBattle=0):
        for toonId in self.involvedToons:
            toon = self.cr.doId2do.get(toonId)
            if not toon:
                continue
            if self.battle and hasattr(self.battle, 'toons') and toon in self.battle.toons:
                continue
            toon.startLookAround()
            toon.startSmooth()
            toon.wrtReparentTo(render)
            if toon == localAvatar:
                if finalBattle:
                    self.toFinalBattleMode()
                else:
                    self.toWalkMode()

    def toMovieMode(self):
        place = self.cr.playGame.getPlace() if self.cr and self.cr.playGame else None
        if place and hasattr(place, 'fsm'):
            place.setState('movie')

    def toWalkMode(self):
        place = self.cr.playGame.getPlace() if self.cr and self.cr.playGame else None
        if place and hasattr(place, 'fsm'):
            place.setState('walk')

    def toFinalBattleMode(self):
        place = self.cr.playGame.getPlace() if self.cr and self.cr.playGame else None
        if place and hasattr(place, 'fsm'):
            place.setState('finalBattle')

    def toonsToBattlePosition(self, toonIds, battleNode):
        if not toonIds:
            return
        points = BattleBase.BattleBase.toonPoints[len(toonIds) - 1]
        for index in range(len(toonIds)):
            toon = base.cr.doId2do.get(toonIds[index])
            if toon:
                pos, h = points[index]
                toon.reparentTo(render)
                toon.setPosHpr(battleNode, pos[0], pos[1], pos[2], h, 0, 0)

    def hide(self):
        self._controllerNode.hide()

    def show(self):
        self._controllerNode.show()

    def stash(self):
        if not self._controllerNode.isEmpty():
            self._controllerNode.hide()

    def unstash(self):
        if not self._controllerNode.isEmpty():
            self._controllerNode.show()

    def detachNode(self):
        self._controllerNode.detachNode()

    def reparentTo(self, parent):
        self._controllerNode.reparentTo(parent)

    def setPosHpr(self, *args):
        self._controllerNode.setPosHpr(*args)

    def getGeomNode(self):
        return self._controllerNode

    def loop(self, *args, **kwargs):
        return

    def pose(self, *args, **kwargs):
        return

    def stopAnimate(self):
        return

    def doAnimate(self, *args, **kwargs):
        return

    def setDizzy(self, dizzy):
        return

    def cleanupAttacks(self):
        return

    def showHpText(self, *args, **kwargs):
        if self.highroller and hasattr(self.highroller, 'showHpText'):
            return self.highroller.showHpText(*args, **kwargs)

    def clearChat(self):
        if self.highroller and hasattr(self.highroller, 'clearChat'):
            self.highroller.clearChat()

    def setChatAbsolute(self, *args, **kwargs):
        if self.highroller and hasattr(self.highroller, 'setChatAbsolute'):
            return self.highroller.setChatAbsolute(*args, **kwargs)

    def unstickToons(self):
        return

    def stashBoss(self):
        if not self._controllerNode.isEmpty():
            self._controllerNode.hide()

    def unstashBoss(self, task=None):
        if not self._controllerNode.isEmpty():
            self._controllerNode.show()
        if task is not None:
            return Task.done

    def rollBossToPoint(self, fromPos, fromHpr, toPos, toHpr, reverse):
        return Sequence(), VBase3(0, 0, 0)

    def showZapToon(self, avId, x, y, z, h, p, r, attackCode, timestamp):
        return

    def setHealthTag(self, tag):
        return

    def scaleInterval(self, *args, **kwargs):
        return self._controllerNode.scaleInterval(*args, **kwargs)

    def stickBossToFloor(self):
        return

    def __makeRollToBattleTwoMovie(self):
        return Sequence()

    def __onToPrepareBattleTwo(self):
        self.doneBarrier('RollToBattleTwo')

    def flashRed(self):
        return

    def updateHealthBar(self):
        return

    def __makeResistanceToon(self):

        self.resistanceToon = None
        self.resistanceToonOnstage = 0
        self.fakeGoons = []

    def __cleanupResistanceToon(self):

        toon = self.resistanceToon
        self.resistanceToon = None
        self.resistanceToonOnstage = 0
        if toon:
            try:
                toon.removeActive()
            except:
                pass
            try:
                toon.detachNode()
            except:
                pass
            try:
                toon.delete()
            except:
                pass
        for goon in getattr(self, 'fakeGoons', []):
            try:
                goon.disable()
                goon.delete()
            except:
                pass
        self.fakeGoons = []

    def __showResistanceToon(self, withSuit):

        self.resistanceToonOnstage = 0

    def __hideResistanceToon(self):
        toon = self.resistanceToon
        self.resistanceToonOnstage = 0
        if toon:
            try:
                toon.removeActive()
            except:
                pass
            try:
                toon.detachNode()
            except:
                pass
            try:
                toon.hide()
            except:
                pass

    def __hideFakeGoons(self):
        self.fakeGoons = []

    def __showFakeGoons(self, state):
        self.fakeGoons = []

    def startPhase2Particles(self):
        self.__playHighRollerMusic(self.phaseTwoMusic, looping=1, volume=1)
        self.battleOneMusic.stop()
        self.highRollerArena.setColor(0.161, 0.161, 0.161, 1)
        self.stopHighRollerParticles()

        BattleParticles.loadParticles()

        self.hrParticles = []

        lights = BattleParticles.createParticleEffect(file='videog_stagelights')
        lights.start(render, render)
        self.hrParticles.append((lights, None))

    def startPhase3Particles(self):
        self.__playHighRollerMusic(self.phaseThreeMusic, looping=1, volume=1)
        self.stopHighRollerParticles()
        self.phaseTwoMusic.stop()
        BattleParticles.loadParticles()

        self.hrParticles = []

        smokeRender = render.attachNewNode('HRSmokeRender')
        smokeRender.setDepthWrite(False)
        smokeRender.setBin('fixed', 1)

        smoke = BattleParticles.createParticleEffect(file='videog_wallsmoke')
        smoke.start(smokeRender)
        self.hrParticles.append((smoke, smokeRender))

        ground = BattleParticles.createParticleEffect(file='videog_starground')
        ground.start(render, render)
        self.hrParticles.append((ground, None))

        sky = BattleParticles.createParticleEffect(file='videog_skystars')
        sky.start(render, render)
        self.hrParticles.append((sky, None))

        lights = BattleParticles.createParticleEffect(file='videog_stagelights')
        lights.start(render, render)
        self.hrParticles.append((lights, None))

    def stopHighRollerParticles(self):
        if not hasattr(self, 'hrParticles'):
            return

        for effect, node in self.hrParticles:
            try:
                effect.softStop()
            except:
                pass

            try:
                effect.cleanup()
            except:
                pass

            if node:
                node.removeNode()

        self.hrParticles = []

    def makeHighRollerWheelSpin(self, duration=3.0, spinCount=3):
        wheel = self.highRollerWheel

        startR = wheel.getR()
        endR = startR - (360 * spinCount) - random.choice((36, 108, 180, 252, 324))

        pullbackR = startR + ((endR - startR) * -0.02)
        sendR = startR + ((endR - startR) * 0.10)

        return Sequence(
            Func(wheel.show),
            LerpHprInterval(
                wheel,
                duration * 0.15,
                hpr=(wheel.getH(), wheel.getP(), pullbackR),
                startHpr=(wheel.getH(), wheel.getP(), startR),
                blendType='easeInOut'
            ),
            LerpHprInterval(
                wheel,
                duration * 0.10,
                hpr=(wheel.getH(), wheel.getP(), sendR),
                startHpr=(wheel.getH(), wheel.getP(), pullbackR),
                blendType='easeIn'
            ),
            LerpHprInterval(
                wheel,
                duration * 0.75,
                hpr=(wheel.getH(), wheel.getP(), endR),
                startHpr=(wheel.getH(), wheel.getP(), sendR),
                blendType='easeOut'
            )
        )

    def colorScaleOffAllNodes(self):
        for colorNode in self.colorScaleOffNodes:
            colorNode.setColorScaleOff()

    def turnLightsBackOn(self):
        for lightBeam in self.highRollerArena.findAllMatches("**/stagelight_light"):
            lightBeam.show()

    def _makeStandaloneArenaPlaceholders(self):
        """Create invisible compatibility nodes for old CFO-derived movies.

        The High Roller fight still uses parts of Altis's boss FSM, whose
        cutscene/state methods expect the old vault and door attributes to
        exist.  These empty nodes preserve those method calls without loading
        or displaying any CFO room geometry.
        """
        self.midVault = self.geom.attachNewNode('highRoller-midVault-placeholder')
        self.endVault = self.geom.attachNewNode('highRoller-endVault-placeholder')
        self.midVault.hide()
        self.endVault.hide()

        self.door1 = self.midVault.attachNewNode('SlidingDoor1-placeholder')
        self.door2 = self.midVault.attachNewNode('SlidingDoor-placeholder')
        self.door3 = self.endVault.attachNewNode('SlidingDoor-placeholder')

        self.elevatorModel = self.geom.attachNewNode(
            'highRoller-elevator-placeholder')
        #self.elevatorModel.hide()
        self.leftDoor = self.elevatorModel.attachNewNode(
            'left-door-placeholder')
        self.rightDoor = self.elevatorModel.attachNewNode(
            'right-door-placeholder')
        self.openDoors = Sequence()
        self.closeDoors = Sequence()

        self.evWalls = self.endVault.attachNewNode('highRoller-wall-placeholder')
        self.evFloor = self.endVault.attachNewNode('highRoller-floor-placeholder')
        self.evWalls.stash()
        self.evFloor.setName('floor')

    def loadEnvironment(self):

        self.geom = NodePath('highRollerInstanceGeom')
        self.highRollerArena = loader.loadModel(
            'phase_6/models/areas/ttcc_int_mplayer_boss.bam')
        self.highRollerArena.setPos(0, -222, -4.05)
        self.highRollerArena.reparentTo(self.geom)

        self.highRollerEntrance = self.highRollerArena.find('**/elevator_origin')
        self.elevatorModel2 = loader.loadModel('phase_5/models/cogdominium/tt_m_ara_csa_elevatorB')
        self.elevatorModel2.reparentTo(self.highRollerEntrance)
        self.elevatorModel2.setH(180)
        self.elevatorModel2.show()
        ElevatorUtils.closeDoors(self.elevatorModel2.find('**/left_door'), self.elevatorModel2.find('**/right_door'), self.elevatorType)
        # if not self.highRollerEntrance.isEmpty():
        #     self.highRollerEntrance.getChildren().detach()
        #     self.highRollerEntrance.setScale(1)
        #     self.highRollerEntrance.setH(180)
        self.__bossRoom = self.highRollerArena
        self.discofloors = [self.highRollerArena.find(name) for name in self.discofloorNames]
        self.discoballs = [self.highRollerArena.find(name) for name in self.discoballNames]
        self.stagelights = [
            MajorPlayerStagelight(self.highRollerArena.find(name), self.stagelightRanges[i])
            for i, name in enumerate(self.stagelightNames)
        ]
        # self.startHighRollerParticles()
        # self.highRollerArena.setColor(0.161, 0.161, 0.161, 1)
        # Init tables
        self.tableLocators = [self.highRollerArena.find(name) for name in self.tableLocatorNames]

        tables = loader.loadModel("phase_12/models/bossbotHQ/BanquetTableChairs")
        # The dropshadows from the interior model look better than the ones on this model
        tables.find("**/shadow").removeNode()
        # We don't need to render collision nodes out
        tables.find("**/Collision").removeNode()
        # Workaround to make the lamps glow.
        tableLamp = tables.find("**/lamp_med_5")
        #tables.find("**/cloth").wrtReparentTo(tableLamp)
        tableLamp.setColorScaleOff()
        # Optimize the tables before we instance them
        for node in ("table", "chairs"):
            tables.find("**/%s" % node).flattenStrong()
        for node in self.tableLocators:
            tables.instanceTo(node)

        # Disable color scale changes on these nodes to make 'em glow in the dark
        # Alternatively, define them as their own variables and have them do their own
        # color scale changes during cutscenes.
        lightGeometry = [
            # "rainbow_backdrop",
            # "crossbeams_rainbow",
            "discofloor_base",
            "wall_lights",
             "stage_floorlights",
            # "stage_background",
            # "ground_stage",
            # "stage_curtains",
            # "stage_ceiling",
            "discoball_beams",
        ]
        for geom in lightGeometry:
            self.highRollerArena.find("**/%s" % geom).setColorScaleOff()

        # Various variables.
        # Includes all parts, including the glow on the floor.
        # self.ceilingLight = self.__bossRoom.find("**/ceiling_light_group")
        # For now it's gonna be glowing but feel free to mess around with its colorscale.
        # self.ceilingLight.setColorScaleOff()
        self.discofloor = MajorPlayerDiscoFloor(self.discofloors)
        self.ballSpeen = []
        # Placeholder none value for each chair position
        self.sitLocators = [[None] * len(self.chairLocatorPosH) for _ in range(len(self.tableLocators))]
        self.sittingSuits = [[None] * len(self.chairLocatorPosH) for _ in range(len(self.tableLocators))]
        self.talkingAudience = []

        # Initialize the dumb things.
        self.initializeDiscoBalls()
        self.suitList = []
        self.initializeAudience()

        # self.highRollerTV = loader.loadModel(
        #     'phase_13/models/events/apriltoons/highroller/cc_m_ara_hr_prp_tv_base.bam')
        # self.highRollerWheel = globalPropPool.getProp('wheel')
        # self.highRollerWheel.loop('wheel')
        # self.highRollerWheel.setScale(6)
        # self.highRollerWheel2 = globalPropPool.getProp('wheel2')
        # self.highRollerWheel2.setScale(6)

        compatibilityProps = self.geom.attachNewNode(
            'highRoller-disabled-legacy-props')
        compatibilityProps.hide()
        self.lightning = compatibilityProps.attachNewNode('lightning-disabled')
        self.magnet = compatibilityProps.attachNewNode('magnet-disabled')
        self.sideMagnet = compatibilityProps.attachNewNode('side-magnet-disabled')
        self.craneArm = compatibilityProps.attachNewNode('crane-arm-disabled')
        self.controls = compatibilityProps.attachNewNode('controls-disabled')
        self.stick = compatibilityProps.attachNewNode('stick-disabled')
        self.safe = compatibilityProps.attachNewNode('safe-disabled')
        self.safe2 = compatibilityProps.attachNewNode('safe2-disabled')
        self.eyes = compatibilityProps.attachNewNode('eyes-disabled')
        self.cableTex = None

        # self.__setupStagelights()

        # self.colorScaleOffNodes = []
        self.hide()
        self._makeStandaloneArenaPlaceholders()

        # self.highroller.reparentTo(self.geom)
        # self.highroller.setPosHpr(0, -200, 0, 180, 0, 0)
        # self.highroller.hide()
        # self.majorplayer2.reparentTo(self.geom)
        # self.majorplayer2.setPosHpr(5, -200, 0, 180, 0, 0)
        # self.duckshuffler2.reparentTo(self.geom)
        # self.duckshuffler2.setPosHpr(-5, -200, 0, 180, 0, 0)
        # self.duckshuffler2.hide()

        # self.highRollerWheel.reparentTo(self.geom)
        # self.highRollerWheel.setPosHpr(0, -170, 0, 180, 0, 0)
        # self.highRollerWheel.hide()
        # self.highRollerWheel2.reparentTo(self.geom)
        # self.highRollerWheel2.setPosHpr(0, -170, 0, 180, 0, 0)
        # self.highRollerWheel2.hide()

        self.__suits = []
        #self.__initializeAudience()
        # for light in self.highRollerArena.find('**/stage_lights_grp').getChildren():
        #     self.colorScaleOffNodes.append(light)
        # for lightBeam in self.highRollerArena.findAllMatches('**/stagelight_light'):
        #     lightBeam.hide()
        # for discoBall in self.highRollerArena.findAllMatches('**/disco_ball_*_geom'):
        #     self.colorScaleOffNodes.append(discoBall)
        # for curtain in self.highRollerArena.findAllMatches('**/curtains_*_geom'):
        #     self.colorScaleOffNodes.append(curtain)
        # for ceilLight in self.highRollerArena.findAllMatches('**/ceiling_lights_*_grp'):
        #     self.colorScaleOffNodes.append(ceilLight)
        # for geomNode in (self.highRollerArena.find('**/ceiling_stage'),
        #                  self.highRollerArena.find('**/stage_curtains_back')):
        #     self.colorScaleOffNodes.append(geomNode)

        # self.highRollerTV.reparentTo(self.geom)
        # self.highRollerTV.setPosHpr(-25, -185, 21.75, -10, 0, 0)
        # self.__graphic = self.highRollerTV.find('**/screen_graphic_full')
        # self.__static = self.highRollerTV.find('**/screen_graphic_static_seq')
        # self.__light1 = self.highRollerTV.find('**/light_group_1_glow')
        # self.__light2 = self.highRollerTV.find('**/light_group_2_glow')
        # self.__stars = self.highRollerTV.find('**/stars')
        # self.__marks = self.highRollerTV.find('**/exclamation_marks')

        plane = CollisionPlane(Plane(Vec3(0, 0, 1), Point3(0, 0, -50)))
        planeNode = CollisionNode('highRollerDropPlane')
        planeNode.addSolid(plane)
        planeNode.setCollideMask(ToontownGlobals.PieBitmask)
        self.geom.attachNewNode(planeNode)

        self.geom.reparentTo(render)
        # self.__setupExclaim()
        # self.__startAnimations()

        self.introduction = base.loadMusic(
            'phase_12/audio/bgm/merc/instance_majorplayer_ctscn.ogg')

        self.elevatorMusic = self.introduction
        self.battleOneMusic = base.loader.loadMusic(
            'phase_13/audio/bgm/april_toons/highroller/cc_s_bgm_ara_hroller_int_battle_3.ogg')
        self.battleTwoMusic = base.loadMusic('phase_7/audio/bgm/encntr_suit_winning_indoor.ogg')
        self.betweenBattleMusic = self.battleOneMusic
        self.epilogueMusic = base.loader.loadMusic('phase_9/audio/bgm/encntr_hall_of_fame.ogg')
        self.midCutsceneMusic = self.battleOneMusic
        self.battleThreeMusic = self.battleOneMusic
        self.phaseOneMusic = loader.loadMusic(
            'phase_13/audio/bgm/april_toons/highroller/cc_s_bgm_ara_hroller_int_battle_3.ogg')
        self.shuffleMusic = loader.loadMusic(
            'phase_13/audio/bgm/april_toons/highroller/cc_s_bgm_ara_hroller_int_shuffle.ogg')
        self.puzzleMusic = loader.loadMusic(
            'phase_13/audio/bgm/april_toons/highroller/cc_s_bgm_ara_hroller_int_puzzle.ogg')
        self.triviaMusic = loader.loadMusic(
            'phase_13/audio/bgm/april_toons/highroller/cc_s_bgm_ara_hroller_int_trivia.ogg')
        self.stingerMusic = loader.loadMusic(
            'phase_13/audio/bgm/april_toons/highroller/cc_s_bgm_ara_hroller_int_stinger.ogg')
        self.phaseTwoCutsceneMusic = loader.loadMusic(
            'phase_13/audio/bgm/april_toons/highroller/cc_s_bgm_ara_hroller_int_ctscn_2.ogg')
        self.phaseTwoMusic = loader.loadMusic(
            'phase_12/audio/bgm/merc/instance_majorplayer_battle_2.ogg')
        self.phaseThreeCutsceneMusic = loader.loadMusic(
            'phase_13/audio/bgm/april_toons/highroller/cc_s_bgm_ara_hroller_int_ctscn_3.ogg')
        self.phaseThreeMusic = loader.loadMusic(
            'phase_13/audio/bgm/april_toons/highroller/BONUSROUND.ogg')

    def __stopHighRollerMusic(self, exceptMusic=None):

        musicNames = (
            'introduction', 'elevatorMusic', 'battleOneMusic',
            'battleTwoMusic', 'battleThreeMusic', 'midCutsceneMusic',
            'betweenBattleMusic', 'phaseOneMusic', 'shuffleMusic',
            'puzzleMusic', 'triviaMusic', 'stingerMusic',
            'phaseTwoCutsceneMusic', 'phaseTwoMusic',
            'phaseThreeCutsceneMusic', 'phaseThreeMusic',
            'epilogueMusic')
        for musicName in musicNames:
            music = getattr(self, musicName, None)
            if music is not None and music is not exceptMusic:
                music.stop()

    def __playHighRollerMusic(self, music, looping=1, volume=0.9):
        if music is None:
            self.notify.warning('Tried to play a missing High Roller music track.')
            return
        self.__stopHighRollerMusic(exceptMusic=music)
        base.playMusic(music, looping=looping, volume=volume)

    def puzzle(self):
        self.puzzleMusic.setLoop(True)
        self.puzzleMusic.play()
        self.__static.hide()
        self.battleOneMusic.stop()
        self.phaseOneMusic.stop()

    def shuffle(self):
        self.shuffleMusic.setLoop(True)
        self.shuffleMusic.play()
        self.__static.hide()
        self.battleOneMusic.stop()
        self.phaseOneMusic.stop()

    def trivia(self):
        self.triviaMusic.setLoop(True)
        self.triviaMusic.play()
        self.__static.hide()
        self.battleOneMusic.stop()
        self.phaseOneMusic.stop()

    def stinger(self):
        self.stingerMusic.play()
        self.battleOneMusic.stop()
        self.phaseOneMusic.stop()
        self.__static.hide()
        self.shuffleMusic.stop()
        self.triviaMusic.stop()
        self.puzzleMusic.stop()
        taskMgr.doMethodLater(
            self.stingerMusic.length(),
            self.__startBattleOneLoop,
            'startBattleOneLoop'
        )

    def __setupStagelights(self):

        stagelights = self.highRollerArena.findAllMatches('**/ceiling_lights_back_stagelight_*')
        for stagelight in stagelights:
            stagelight.setColorScaleOff(1)
            stagelight.setColor(1, 1, 1, 0.3)

    def __startBattleOneLoop(self, task):
        self.phaseOneMusic.setLoop(True)
        self.phaseOneMusic.play()
        self.__static.show()
        return task.done

    def phase2Intro(self):
        self.__static.hide()
        self.__playHighRollerMusic(
            self.phaseTwoCutsceneMusic, looping=0, volume=0.9)

    def startPhase2Music(self):
        #self.startHighRollerParticles()
       # self.turnLightsBackOn()
        #self.__static.show()
       # self.colorScaleOffAllNodes()
        #self.highRollerArena.setColor(0.161, 0.161, 0.161, 1)
        self.__playHighRollerMusic(
            self.phaseTwoMusic, looping=1, volume=0.9)

    def phase3Intro(self):
        self.__static.hide()
        self.__playHighRollerMusic(
            self.phaseThreeCutsceneMusic, looping=0, volume=0.9)

    def startPhase3Music(self):
        self.__playHighRollerMusic(
            self.phaseThreeMusic, looping=1, volume=0.9)

    def __setupExclaim(self):
        """
        The exclaimation marks need to be set up in a specific way.
        """
        self.__marksNode = NodePath('marksNode')

        self.__marksNode.reparentTo(self.__marks)
        self.__marksNode.setHpr(0, 47.0589, 0)
        self.__marksNode.setPos(0, 0.2 + 4, - 4)
        self.__marksNode.wrtReparentTo(self.highRollerTV)
        self.__marks.wrtReparentTo(self.__marksNode)

    def __startAnimations(self):
        self.marks_pitch_start = 47.0589
        self.marks_pitch_dist = 0.7
        self.marks_pitch_duration = 3.0

        self.star_bob_dist = 0.35
        self.star_bob_duration = 4.0

        self.light_flash_duration = 0.4

        self.text_displacement_scale = 0.33
        self.text_z_offset = -0.5

        markSequence = Sequence(
            LerpHprInterval(self.__marksNode, self.marks_pitch_duration / 2.0, hpr=(0, self.marks_pitch_start + self.star_bob_dist, 0), startHpr=(0, self.marks_pitch_start - self.star_bob_dist, 0), blendType='easeInOut'),
            LerpHprInterval(self.__marksNode, self.marks_pitch_duration / 2.0, hpr=(0, self.marks_pitch_start - self.star_bob_dist, 0), startHpr=(0, self.marks_pitch_start + self.star_bob_dist, 0), blendType='easeInOut')
        )
        markSequence.loop()
        self.__sequences.append(markSequence)

        starSequence = Sequence(
            LerpHprInterval(self.__stars, self.star_bob_duration / 2.0, hpr=(0, self.star_bob_dist, 0), startHpr=(0, -self.star_bob_dist, 0), blendType='easeInOut'),
            LerpHprInterval(self.__stars, self.star_bob_duration / 2.0, hpr=(0, -self.star_bob_dist, 0), startHpr=(0, self.star_bob_dist, 0), blendType='easeInOut')
        )
        starSequence.loop()
        self.__sequences.append(starSequence)

        lightSequence = Sequence(
            Func(self.__light1.show),
            Func(self.__light2.hide),
            Wait(self.light_flash_duration),
            Func(self.__light1.hide),
            Func(self.__light2.show),
            Wait(self.light_flash_duration),
        )
        lightSequence.loop()
        self.__sequences.append(lightSequence)

    def __setupExclaim(self):
        """
        The exclaimation marks need to be set up in a specific way.
        """
        self.__marksNode = NodePath('marksNode')

        self.__marksNode.reparentTo(self.__marks)
        self.__marksNode.setHpr(0, 47.0589, 0)
        self.__marksNode.setPos(0, 0.2 + 4, - 4)
        self.__marksNode.wrtReparentTo(self.highRollerTV)
        self.__marks.wrtReparentTo(self.__marksNode)

    def initializeAudience(self):
        dept = None
        # Make talkingAudience first, must always be made
        for indices in self.talkingAudienceIndices:
            # Generate a suit for that seat

            suit = self.createSuitRandom()
            self.seatSuit(suit, indices[0], indices[1])
            self.suitList.append(suit)
        # Make random suits now
        for tableIndex in range(len(self.tableLocators)):
            for chairIndex in range(len(self.chairLocatorPosH)):
                # Don't make a second suit in an occupied suit
                if self.sittingSuits[tableIndex][chairIndex]:
                    continue
                # Generate a suit for that seat
                suit = self.createSuitRandom()
                self.seatSuit(suit, tableIndex, chairIndex)
                self.suitList.append(suit)
        self.loopAudience()

    def loopAudience(self):
        for tableIndex, table in enumerate(self.sittingSuits):
            for chairIndex, suit in enumerate(table):
                if suit:
                    fromFrame = tableIndex + chairIndex
                    for control in suit.getAnimControls('sit', None):
                        toFrame = fromFrame + control.getNumFrames() - 1
                        control.loop(1, fromFrame, toFrame)

    def seatSuit(self, suit, tableIndex=0, chairIndex=0):
        """
        Takes a suit and seats them based on table and chair index given.
        Creates chair and sit locator nodes in the process.
        :param suit:
        :param tableIndex:
        :param chairIndex:
        :return:
        """
        # Make locator nodes for chair and sitting positions
        chairLocator = self.tableLocators[tableIndex].attachNewNode('chairLocator-{chairIndex}')
        chairLocator.setPos(self.chairLocatorPosH[chairIndex][0])
        chairLocator.setH(self.chairLocatorPosH[chairIndex][1])
        sitLocator = chairLocator.attachNewNode('sitLocator')

        # Position sit locator based on suit body type and scale
        suitScale = suit.getGeomNode().getScale()[0]

        # Scale adjustment to prevent them from being too big
        maxScale = 1.4
        if suitScale > maxScale:
            suit.getGeomNode().setScale(maxScale)
            suitScale = maxScale

        # Adjust sit position based on suit's scale
        sitLocator.setPos(self.sitLocatorPos['a'][0]
                          + (self.sitLocatorPos['a'][1] * (1 - suitScale)))
        suit.reparentTo(sitLocator)
        self.sitLocators[tableIndex][chairIndex] = sitLocator

        # Remove shadows and nametags
        suit.setActiveShadow(0)  # Disable drop shadow calculations
        suit.hideShadow()  # And then hide it from rendering
        suit.removeActive()  # Unmanage the nametag from the margin manager
        self.sittingSuits[tableIndex][chairIndex] = suit

    """
    Environmental effects
    """

    def initializeDiscoBalls(self):
        for index, ball in enumerate(self.discoballs):
            ballStartH = random.randint(0, 360)
            seq = LerpHprInterval(ball, self.ballSpinDuration,
                                  (360 + ballStartH, 0, 0), startHpr=(ballStartH, 0, 0))
            seq.loop()
            self.ballSpeen.append(seq)
            # make sure ball doesnt get affected by room dimming
            ball.setColorScaleOff()
            ball.find('**/discolights_*').setColor(1, 1, 1, 0.3)
            ball.find('**/').setColor(1, 1, 1, 1)
            ball.setColor(1, 1, 1, 1)

    def hideCentralBall(self):
        self.discoballs[1].hide()

    def showCentralBall(self):
        self.discoballs[1].show()

    """
    Getters
    """

    def getGeom(self):
        return self.__bossRoom

    def createSuitRandom(self):
        diner = Suit.Suit()
        diner.dna = SuitDNA.SuitDNA()
        level = random.choice([7, 8])
        diner.dna.newSuitRandom('s', name=random.choice(('mh2', 'cnd2', 'std2')))
        diner.setDNA(diner.dna)
        diner.makeExecutive()
        diner.loop('sit')
        diner.nametag.setNametag2d(None)
        diner.nametag.setNametag3d(None)
        return diner

    def getNextAudienceSuit(self):
        # Gets the next relevant audience suit.
        if not self.suitList:
            return None
        suit = self.suitList.pop(0)
        # If they're not part of the talking audience, we will need to allow them to speak.
        if suit not in self.talkingAudience:
            # Init their nametag so they can talk.
            suit.initName()
            # Hide their nametag, because they're talking during cutscenes.
            suit.hideNametag2d()
            suit.nametag3d.hide()
        return suit

    def unloadEnvironment(self):
        for suit in self.__suits:
            suit.cleanup()
        del self.__suits
        self.colorScaleOffNodes = []
        self.geom.removeNode()
        for seq in self.ballSpeen:
            seq.finish()
        for light in self.stagelights:
            light.cleanup()
        for suit in self.suitList:
            suit.delete()
        self.talkingAudience = []
        self.suitList = []
        self.discofloors = []
        self.discoballs = []
        self.stagelights = []
        self.discofloors = []


    @staticmethod
    def __createSuit(name):
        suit = Suit.Suit()
        d = SuitDNA.SuitDNA()
        d.newSuit(name)
        suit.setDNA(d)
        suit.loop('neutral')
        suit.setPlayRate(rate=random.uniform(0.95, 1.05), animName='neutral')
        suit.setColorScale(0.76, 0.76, 0.76, 1.0)
        setattr(suit, 'dna', d)
        setattr(suit, 'getLevel', lambda: 0)
        setattr(suit, 'getStyleName', lambda: d.name)
        setattr(suit, 'battleTrapProp', None)
        suit.hideNametag2d()
        suit.hideNametag3d()
        suit.setActiveShadow(0)
        suit.hideShadow()
        suit.removeActive()

        return suit

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
            if lastPlane == None or plane.compareTo(lastPlane, threshold) != 0:
                cp = CollisionPlane(plane)
                newCollisionNode.addSolid(cp)
                lastPlane = plane

        return NodePath(newCollisionNode)

    def __makeGoonMovieForIntro(self):
        return Sequence()

    def makeIntroductionMovie(self, delayDeletes):
        base.playMusic(self.introduction, looping=1, volume=0.9)
        base.camera.wrtReparentTo(self.videographer)
        base.camera.setPosHpr(0, 135.0, 7, 180, 0, 0.0)
        track = Sequence(Func(self.videographer.nametag3d.setZ, 10), Func(self.videographer.setChatAbsolute, "Well, well, well...", CFSpeech | CFTimeout), 
                         LerpPosHprInterval(base.camera, 2, (-7.0, 10.0, 7), (210, 0, 0.0), blendType='easeInOut'), 
        LerpPosHprInterval(base.camera, 2, (0, 15.0, 8), (180, 0, 0.0), blendType='easeInOut'), Func(self.videographer.nametag3d.setZ, 10),
        Func(self.videographer.setChatAbsolute, "Toons...", CFSpeech | CFTimeout),
        Wait(4.0),
                         Func(self.videographer.setChatAbsolute, "I'm afraid the Cog you came all this way to see is currently...", CFSpeech | CFTimeout), 
                         Wait(4.0), Parallel(Func(self.videographer.setChatAbsolute, "...away.", CFSpeech | CFTimeout), 
                                             LerpPosHprInterval(base.camera, .5, (0, 10.0, 9), (180, 0, 0.0), blendType='easeInOut')),
                        Wait(3.0),
                        Func(self.videographer.setChatAbsolute, "The Suit you Toons know as the 'Major Player' is taking a little break.", CFSpeech | CFTimeout), 
                        Wait(4.0),
                        Parallel(LerpPosHprInterval(base.camera, 3, (0, 15, 9), (180, 0, 0.0), blendType='easeInOut'), Sequence(ActorInterval(self.videographer, 'sit-lose'), Func(self.videographer.loop, 'neutral2'), 
                                                                                                           Func(self.videographer.setPos, (0, -130, 1.25))), 
                                 Func(self.videographer.setChatAbsolute, "But, I suppose the show must go on shouldn't it? Somebody has to keep the cameras rolling.", CFSpeech | CFTimeout)),
                                 Wait(3.0),
                        Parallel(Func(self.videographer.setChatAbsolute, "Fortunately, he left a professional in charge.", CFSpeech | CFTimeout), ActorInterval(self.videographer, 'finger-wag')), 
                        Parallel(Func(base.camera.setPos, (5, -15, 12.5)), Func(base.camera.setH, 0), Sequence(LerpPosInterval(base.camera, 4, (-5, -15, 12.5)), Func(self.videographer.loop, 'speak')), 
                                 Func(self.videographer.setChatAbsolute, "I've spent plenty of time behind the cameras.", CFSpeech | CFTimeout)),
                                 Parallel(LerpPosHprInterval(base.camera, 0, (25, 50, 35), (150, -30, 0.0)), Func(self.videographer.nametag3d.setScale, 2.5),
                                 Func(self.videographer.setChatAbsolute, "Finding the right angles.", CFSpeech | CFTimeout)),
                                 Wait(4.0),
                                 Parallel(LerpPosHprInterval(base.camera, 4, (-25, 50, 35), (210, -30, 0.0), blendType='easeInOut'), Func(self.videographer.nametag3d.setScale, 2.5),
                                 Func(self.videographer.setChatAbsolute, "Setting the scene.", CFSpeech | CFTimeout)),
                                 Parallel(LerpPosHprInterval(base.camera, 1, (0, 12, 9), (180, 0, 0.0), blendType='easeInOut'), Func(self.videographer.nametag3d.setScale, 1.0), 
                                          Sequence(ActorInterval(self.videographer, 'song-and-dance'), Func(self.videographer.loop, 'neutral2')),
                                 Func(self.videographer.setChatAbsolute, "Making sure every performance looks its best!", CFSpeech | CFTimeout)),
                                 Parallel(LerpPosHprInterval(base.camera, .25, (0, 10, 9), (180, 0, 0.0)), 
                                 Func(self.videographer.setChatAbsolute, "But tonight...", CFSpeech | CFTimeout)),
                                 Wait(2.0),
                                  Parallel(Sequence(ActorInterval(self.videographer, 'bust'), Func(self.videographer.loop, 'neutral2')), 
                                           Sequence(Func(self.videographer.setChatAbsolute, "I get to try something a little different.", CFSpeech | CFTimeout), Wait(3.0),
                                                    Func(self.videographer.setChatAbsolute, "He makes this look so easy.", CFSpeech | CFTimeout), Wait(3.0),
                                                    Func(self.videographer.setChatAbsolute, "So let's see how I look in the spotlight!", CFSpeech | CFTimeout))),
                            Parallel(Func(base.camera.setPos, (5, -15, 5)), Func(base.camera.setH, 0), Sequence(LerpPosInterval(base.camera, 4, (-5, -15, 5)), Func(self.videographer.loop, 'rolled')), 
                                 Func(self.videographer.nametag3d.setZ, 3), Func(self.videographer.setChatAbsolute, "Don't worry, I know exactly what makes a performance good.", CFSpeech | CFTimeout)),
                                 Parallel(LerpPosHprInterval(base.camera, 0, (25, 50, 15), (150, 0, 0.0)), Func(self.videographer.nametag3d.setScale, 2.5), Func(self.videographer.nametag3d.setZ, 10),
                                 Func(self.videographer.setChatAbsolute, "A little action.", CFSpeech | CFTimeout)),
                                 Wait(3.0),
                                 Parallel(LerpPosHprInterval(base.camera, 3, (-25, 50, 15), (210, 0, 0.0), blendType='easeInOut'), Func(self.videographer.nametag3d.setScale, 2.5),
                                 Func(self.videographer.setChatAbsolute, "A little drama.", CFSpeech | CFTimeout)),
                                  Parallel(LerpPosHprInterval(base.camera, 1, (0, 10, 9), (180, 0, 0.0), blendType='easeInOut'), Func(self.videographer.nametag3d.setScale, 2.5),
                                 Sequence(Func(self.videographer.nametag3d.setScale, 1.0), Func(self.videographer.setChatAbsolute, "And, of course...", CFSpeech | CFTimeout), Wait(3.0), 
                                          Func(self.videographer.nametag3d.setScale, 1.0), Func(self.videographer.setChatAbsolute, "...a convincing defeat!", CFSpeech | CFTimeout))),
                                          Wait(3.0),
                                          Parallel(LerpPosHprInterval(base.camera, 1, (0, 15, 9), (180, 0, 0.0)), Func(self.videographer.nametag3d.setScale, 1.0), 
                                                   Sequence(Func(self.videographer.setChatAbsolute, "Places, Toons!", CFSpeech | CFTimeout), Func(self.videographer.loop, 'walk'), 
                                                            LerpHprInterval(self.videographer, .5, (0, 0, 0.0)), LerpPosInterval(self.videographer, 3, (0, -115, 1.25), blendType='easeInOut'),
                                                            Func(self.videographer.loop, 'neutral2'))),
                                                            Wait(2.0),
                                          Parallel(LerpPosHprInterval(base.camera, 1, (0, 15, 9), (180, 0, 0.0)), 
                                          Sequence(Func(self.videographer.setChatAbsolute, "Try to make this look good.", CFSpeech | CFTimeout), LerpHprInterval(self.videographer, 0, (180, 0, 0.0)),
                                                   ActorInterval(self.videographer, 'turn-into'), Func(self.videographer.loop, 'turn-loop'),
                                                   Wait(3.0), Func(self.videographer.setChatAbsolute, "And...", CFSpeech | CFTimeout))),
                                 Wait(1.0),
                                 Sequence(ActorInterval(self.videographer, 'turn-out'), LerpHprInterval(self.videographer, 0, (0, 0, 0.0)), Func(self.videographer.loop, 'rolled')),
                                 Parallel(LerpPosHprInterval(base.camera, .25, (0, 10, 9), (180, 0, 0.0)), Func(self.videographer.setChatAbsolute, "ACTION!", CFSpeech | CFTimeout)),
                         Wait(5), Func(self.videographer.hide))
        return track

    def makePrepareBattleTwoMovie(self, delayDeletes):
        self.hide()
        startPos = Point3(ToontownGlobals.HighRollerBossBattleOnePosHpr[0], ToontownGlobals.HighRollerBossBattleOnePosHpr[1], ToontownGlobals.HighRollerBossBattleOnePosHpr[2])
        battlePos = Point3(ToontownGlobals.HighRollerBossBattleThreePosHpr[0], ToontownGlobals.HighRollerBossBattleThreePosHpr[1], ToontownGlobals.HighRollerBossBattleThreePosHpr[2])
        startHpr = Point3(ToontownGlobals.HighRollerBossBattleOnePosHpr[3], ToontownGlobals.HighRollerBossBattleOnePosHpr[4], ToontownGlobals.HighRollerBossBattleOnePosHpr[5])
        battleHpr = VBase3(ToontownGlobals.HighRollerBossBattleThreePosHpr[3], ToontownGlobals.HighRollerBossBattleThreePosHpr[4], ToontownGlobals.HighRollerBossBattleThreePosHpr[5])
        finalHpr = VBase3(135, 0, 0)
        toonPosHpr = ToontownGlobals.HighRollerRTBattleTwoEndPosHpr
        bossTrack = Sequence()
        self.phaseThreeMusic.play()
        track2 = Sequence()
        bossTrack.append(Func(self.reparentTo, render))
        bossTrack.append(Func(self.getGeomNode().setH, 180))
        bossTrack.append(Func(self.pelvis.setHpr, self.pelvisForwardHpr))
        bossTrack.append(Func(self.loop, 'Ff_neutral'))
        track, hpr = self.rollBossToPoint(battlePos, startHpr, battlePos, battleHpr, 0)
        bossTrack.append(track)
        track, hpr = self.rollBossToPoint(battlePos, None, battlePos, None, 0)
        bossTrack.append(track)
        track, hpr = self.rollBossToPoint(battlePos, battleHpr, battlePos, finalHpr, 0)
        bossTrack.append(track)
        rToon = self.resistanceToon
        rToon.setPosHpr(*ToontownGlobals.HighRollerRTBattleTwoStartPosHpr)
        self.__arrangeToonsAroundResistanceToon()
        base.playMusic(self.midCutsceneMusic, looping=1, volume=0)
        self.phaseThreeMusic.stop()
        track = Sequence()
        return track2

    def createWalkInInterval(self):
        retval = Parallel()
        delay = 0
        index = 0
        for toonId in self.involvedToons:
            toon = base.cr.doId2do.get(toonId)
            if not toon:
                continue
            destPos = Point3(132 - index * 2, -285, 0)

            def toWalk(toon):
                toon.animFSM.request('run')

            def toNeutral(toon):
                toon.animFSM.request('neutral')

            retval.append(Sequence(Wait(delay), Func(toon.wrtReparentTo, render), Func(toWalk, toon), Func(toon.headsUp, destPos), LerpPosInterval(toon, 2, destPos), Func(toon.headsUp, self._controllerNode), Func(toNeutral, toon)))
            if toon == base.localAvatar:
                retval.append(Sequence(Wait(delay), Func(base.camera.reparentTo, toon), Func(base.camera.setPos, toon.cameraPositions[0][0]), Func(base.camera.setHpr, 0, 0, 0)))
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

        startPos = Point3(ToontownGlobals.HighRollerBossBattleOnePosHpr[0], ToontownGlobals.HighRollerBossBattleOnePosHpr[1], ToontownGlobals.HighRollerBossBattleOnePosHpr[2])
        battlePos = Point3(ToontownGlobals.HighRollerBossBattleThreePosHpr[0], ToontownGlobals.HighRollerBossBattleThreePosHpr[1], ToontownGlobals.HighRollerBossBattleThreePosHpr[2])
        startHpr = Point3(ToontownGlobals.HighRollerBossBattleOnePosHpr[3], ToontownGlobals.HighRollerBossBattleOnePosHpr[4], ToontownGlobals.HighRollerBossBattleOnePosHpr[5])
        battleHpr = VBase3(ToontownGlobals.HighRollerBossBattleThreePosHpr[3], ToontownGlobals.HighRollerBossBattleThreePosHpr[4], ToontownGlobals.HighRollerBossBattleThreePosHpr[5])
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
        base.playMusic(self.midCutsceneMusic, looping=1, volume=0.9)
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
            Func(rToon.setChatAbsolute, TTL.ResistanceToonCraneInstructions2, CFSpeech),
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
            Func(rToon.animFSM.request, 'jump'),
            Wait(1.8),
            Func(rToon.clearChat),
            base.camera.posHprInterval(1, Point3(109.1, -300.7, 13.9), VBase3(-15.6, -13.6, 0), blendType='easeInOut'),
            Func(rToon.animFSM.request, 'run'),
            Func(goon.request, 'Walk'),
            Parallel(
                self.door3.posInterval(3, VBase3(0, 0, 0)),
                rToon.posHprInterval(3, Point3(136, -212.9, 0), VBase3(-14, 0, 0), startPos=Point3(110.8, -292.7, 0), startHpr=VBase3(-14, 0, 0)),
                goon.posHprInterval(3, Point3(125.2, -243.5, 0), VBase3(-14, 0, 0), startPos=Point3(104.8, -309.5, 0), startHpr=VBase3(-14, 0, 0))),
            Func(self.__hideFakeGoons),
            Func(crane.request, 'Free'),
            Func(self.getGeomNode().setH, 0),
            self.moveToonsToBattleThreePos(self.involvedToons),
            Func(self.midCutsceneMusic.stop),
            Func(self.__showToons),
            Wait(2))
        return Sequence(Func(base.camera.reparentTo, self), base.camera.posHprInterval(1, Point3(0, -27, 25), VBase3(0, -18, 0), blendType='easeInOut'), track)

    def moveToonsToBattleThreePos(self, toons):
        track = Parallel()
        for i in range(len(toons)):
            toon = base.cr.doId2do.get(toons[i])
            if toon:
                posHpr = ToontownGlobals.HighRollerToonsBattleThreeStartPosHpr[i]
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
                Func(self.setChatAbsolute, '', CFSpeech),
                Func(self.setPosHpr, *ToontownGlobals.HighRollerBossBattleThreePosHpr),
                ActorInterval(self, 'Fb_firstHit'),
                ActorInterval(self, 'Fb_down2Up'))),
            (1.0, Func(self.setChatAbsolute, hadEnough, CFSpeech)),
            (5.5, Parallel(
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

    def enterRollToBattleTwo(self):
        self.notify.debug('----- enterRollToBattleTwo')
        self.releaseToons(finalBattle=1)
        self.stashBoss()
        self.toonsToBattlePosition(self.involvedToons, self.battleANode)
        self.stickBossToFloor()
        intervalName = 'RollToBattleTwo'
        seq = Sequence(self.__makeRollToBattleTwoMovie(), Func(self.__onToPrepareBattleTwo), name=intervalName)
        seq.start()
        self.storeInterval(seq, intervalName)
        base.playMusic(self.betweenBattleMusic, looping=1, volume=0.9)
        taskMgr.doMethodLater(0.01, self.unstashBoss, 'unstashBoss')

    def __clickedNameTag(self, avatar):
        self.notify.debug('__clickedNameTag')
        if self.cr:
            place = self.cr.playGame.getPlace()
            if place and hasattr(place, 'fsm'):
                FriendsListManager.FriendsListManager._FriendsListManager__handleClickedNametag(place, avatar)

    def __handleFriendAvatar(self, avId, avName, avDisableName):
        self.notify.debug('__handleFriendAvatar')
        if self.cr:
            place = self.cr.playGame.getPlace()
            if place and hasattr(place, 'fsm'):
                FriendsListManager.FriendsListManager._FriendsListManager__handleFriendAvatar(place, avId, avName, avDisableName)

    def __handleAvatarDetails(self, avId, avName, playerId = None):
        self.notify.debug('__handleAvatarDetails')
        if self.cr:
            place = self.cr.playGame.getPlace()
            if place and hasattr(place, 'fsm'):
                FriendsListManager.FriendsListManager._FriendsListManager__handleAvatarDetails(place, avId, avName, playerId)

    def grabObject(self, obj):
        obj.wrtReparentTo(self.neck)
        obj.hideShadows()
        obj.stashCollisions()
        if obj.lerpInterval:
            obj.lerpInterval.finish()
        obj.lerpInterval = Parallel(obj.posInterval(ToontownGlobals.CashbotBossToMagnetTime, Point3(-1, 0, 0.2)), obj.quatInterval(ToontownGlobals.CashbotBossToMagnetTime, VBase3(0, -90, 90)), Sequence(Wait(ToontownGlobals.CashbotBossToMagnetTime), ShowInterval(self.eyes), ShowInterval(self.safe2)), obj.toMagnetSoundInterval)
        obj.lerpInterval.start()
        self.heldObject = obj

    def dropObject(self, obj):
        if obj.lerpInterval:
            obj.lerpInterval.finish()
            obj.lerpInterval = None
        obj = self.heldObject
        obj.wrtReparentTo(render)
        obj.setHpr(obj.getH(), 0, 0)
        self.eyes.hide()
        self.safe2.hide()
        obj.showShadows()
        obj.unstashCollisions()
        self.heldObject = None
        return

    def setBossDamage(self, bossDamage):
        if bossDamage > self.bossDamage:
            delta = bossDamage - self.bossDamage
            self.flashRed()
            self.doAnimate('hit', now=1)
            self.showHpText(-delta, scale=5)
        self.bossDamage = bossDamage
        self.updateHealthBar()

    def setMaxHp(self, hp):
        self.bossMaxDamage = hp

    def setRewardId(self, rewardId):
        self.rewardId = rewardId

    def d_applyReward(self):
        self.sendUpdate('applyReward', [])

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
                toon.loop('neutral')
                toon.show()

    def __talkAboutPromotion(self, speech):
        if self.bonusUnites:
            speech += TTLocalizer.ResistanceToonBonusUnites % self.bonusUnites
        if self.prevCogSuitLevel < ToontownGlobals.MaxCogSuitLevel:
            newCogSuitLevel = localAvatar.getCogLevels()[CogDisguiseGlobals.dept2deptIndex(self.style.dept)]
            newCogSuitReviveLevel = localAvatar.getCogReviveLevels()[CogDisguiseGlobals.dept2deptIndex(self.style.dept)]
            if newCogSuitLevel == ToontownGlobals.MaxCogSuitLevel:
                speech += TTLocalizer.ResistanceToonLastPromotion % (ToontownGlobals.MaxCogSuitLevel + 1)
            if newCogSuitReviveLevel == ToontownGlobals.MaxCogSuitLevel:
                speech += TTLocalizer.ResistanceToonLastRevivePromotion % (ToontownGlobals.MaxCogSuitLevel + 1)
            if newCogSuitLevel in ToontownGlobals.CogSuitHPLevels:
                speech += TTLocalizer.ResistanceToonHPBoost
            if newCogSuitReviveLevel in ToontownGlobals.CogReviveSuitHPLevels and newCogSuitReviveLevel != self.prevCogSuitReviveLevel:
                speech += TTLocalizer.ResistanceToonHPBoost
        else:
            speech += TTLocalizer.ResistanceToonMaxed % (ToontownGlobals.MaxCogSuitLevel + 1)
        return speech

    def enterOff(self):
        self.cleanupIntervals()
        self.hide()
        self.clearChat()
        self.toWalkMode()

    def exitOff(self):
        self.show()

    def enterWaitForToons(self):
        self.cleanupIntervals()
        taskMgr.remove(self.uniqueName('highRollerInstanceReady'))
        taskMgr.add(self.__waitForHighRollerInstanceReady,
                    self.uniqueName('highRollerInstanceReady'))
        if self.geom:
            self.geom.hide()

    def __waitForHighRollerInstanceReady(self, task):
        if not self.gotAllToons:
            return Task.cont

        place = None
        try:
            playGame = base.cr.playGame
            if playGame:
                place = playGame.getPlace()
        except:
            place = None

        if not place or not hasattr(place, 'fsm'):
            return Task.cont

        state = place.fsm.getCurrentState()
        if not state or state.getName() != 'walk':
            return Task.cont

        self.doneBarrier('WaitForToons')
        return Task.done

    def exitWaitForToons(self):
        taskMgr.remove(self.uniqueName('highRollerInstanceReady'))
        if self.geom:
            self.geom.show()

    def enterElevator(self):
        self.doneBarrier('Elevator')

    def exitElevator(self):
        pass

    def enterIntroduction(self):
        self.detachNode()
        self.stopAnimate()
        self.endVault.unstash()
        self.evWalls.stash()
        self.midVault.unstash()

        self.introduction.stop()

        self.controlToons()
        NametagGlobals.setWant2dNametags(False)
        NametagGlobals.setWantActiveNametags(True)
        base.localAvatar.setFriendsListButtonActive(1)
        self.accept('clickedNametag', self.__clickedNameTag)
        self.accept('friendAvatar', self.__handleFriendAvatar)
        self.accept('avatarDetails', self.__handleAvatarDetails)
        messenger.send(self.uniqueName('IntroductionStarted'))
        intervalName = 'IntroductionMovie'
        delayDeletes = []
        seq = Sequence(self.makeIntroductionMovie(delayDeletes),
            Func(self.__finishHighRollerIntroduction),
            name=intervalName)
        seq.delayDeletes = delayDeletes
        seq.start()
        self.storeInterval(seq, intervalName)

    def __finishHighRollerIntroduction(self):
        intervalName = 'IntroductionMovie'
        self.clearInterval(intervalName)
        setup = getattr(self, '_highRollerIntroSetup', None)
        if setup:
            setup.cleanup()
        self.doneBarrier('Introduction')
        NametagGlobals.setWant2dNametags(False)
        NametagGlobals.setWantActiveNametags(True)
        base.localAvatar.setFriendsListButtonActive(1)
        self.accept('clickedNametag', self.__clickedNameTag)
        self.accept('friendAvatar', self.__handleFriendAvatar)
        self.accept('avatarDetails', self.__handleAvatarDetails)

    def exitIntroduction(self):
        intervalName = 'IntroductionMovie'
        self.clearInterval(intervalName)
        setup = getattr(self, '_highRollerIntroSetup', None)
        if setup:
            setup.cleanup()
        self.unstickToons()
        self.releaseToons()
        NametagGlobals.setWant2dNametags(False)
        NametagGlobals.setWantActiveNametags(True)
        base.localAvatar.setFriendsListButtonActive(1)
        self.accept('clickedNametag', self.__clickedNameTag)
        self.accept('friendAvatar', self.__handleFriendAvatar)
        self.accept('avatarDetails', self.__handleAvatarDetails)
        self.introduction.stop()

    def enterBattleOne(self):
        self.cleanupIntervals()
        mult = ToontownBattleGlobals.getBossBattleCreditMultiplier(1)
        localAvatar.inventory.setBattleCreditMultiplier(mult)
        self.toonsToBattlePosition(self.toons, self.battleANode)
        self.releaseToons()
        # self.highRollerWheel.show()
        self.endVault.unstash()
        self.evWalls.stash()
        self.midVault.unstash()
        self.__hideResistanceToon()
        NametagGlobals.setWant2dNametags(True)
        NametagGlobals.setWantActiveNametags(True)
        base.localAvatar.setFriendsListButtonActive(1)
        self.accept('clickedNametag', self.__clickedNameTag)
        self.accept('friendAvatar', self.__handleFriendAvatar)
        self.accept('avatarDetails', self.__handleAvatarDetails)
        self.introduction.stop()
        base.playMusic(self.battleOneMusic, looping=1, volume=0.9)

    def exitBattleOne(self):
        self.cleanupBattles()
        self.battleOneMusic.stop()
        localAvatar.inventory.setBattleCreditMultiplier(1)

    def enterRollToBattleTwo(self):
        pass

    def exitRollToBattleTwo(self):
        self.battleOneMusic.stop()

    def enterPrepareBattleTwo(self):
        self.controlToons()
        self.highRollerArena.setColor(0.161, 0.161, 0.161, 1)
        NametagGlobals.setWant2dNametags(True)
        NametagGlobals.setWantActiveNametags(True)
        base.localAvatar.setFriendsListButtonActive(1)
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

    def exitPrepareBattleTwo(self):
        intervalName = 'PrepareBattleTwoMovie'
        self.clearInterval(intervalName)
        self.unstickToons()
        self.releaseToons()
        NametagGlobals.setWant2dNametags(True)
        ElevatorUtils.closeDoors(self.leftDoor, self.rightDoor, ElevatorConstants.ELEVATOR_SIGIL)

    def enterBattleTwo(self):
        self.reparentTo(render)
        self.evWalls.unstash()
        self.setPosHpr(*ToontownGlobals.HighRollerBossBattleOnePosHpr)
        self.show()
        self.battleThreeMusic.stop()
        NametagGlobals.setWant2dNametags(True)
        NametagGlobals.setWantActiveNametags(True)
        base.localAvatar.setFriendsListButtonActive(1)
        self.pelvis.setHpr(self.pelvisReversedHpr)
        self.doAnimate()
        self.__hideResistanceToon()
        base.playMusic(self.battleTwoMusic, looping=1, volume=0.9)

    def exitBattleTwo(self):
        self.battleTwoMusic.stop()

    def __beginBattleTwo(self):
        intervalName = 'PrepareBattleTwoMovie'
        self.clearInterval(intervalName)
        self.doneBarrier('PrepareBattleTwo')

    def enterPrepareBattleThree(self):
        self.cleanupIntervals()
        self.__hideResistanceToon()
        self.stash()

    def __beginBattleThree(self):
        intervalName = 'PrepareBattleThreeMovie'
        self.clearInterval(intervalName)
        self.doneBarrier('PrepareBattleThree')

    def exitPrepareBattleThree(self):
        self.cleanupIntervals()

    def setBattleDifficulty(self, diff):
        self.notify.debug('battleDifficulty = %d' % diff)
        self.battleDifficulty = diff

    def enterBattleThree(self):
        self.cleanupIntervals()
        self.__hideResistanceToon()
        self.stash()

    def exitBattleThree(self):
        self.cleanupIntervals()

    def enterVictory(self):
        self.cleanupIntervals()
        self.__hideResistanceToon()
        self.stash()
        self.doneBarrier('Victory')

    def __continueVictory(self):
        self.doneBarrier('Victory')

    def exitVictory(self):
        self.cleanupIntervals()

    def enterReward(self):
        self.cleanupIntervals()
        self.clearChat()
        self.stash()
        self.stopAnimate()
        self.controlToons()
        panelName = self.uniqueName('reward')
        self.rewardPanel = RewardPanel.RewardPanel(panelName)
        victory, camVictory, skipper = MovieToonVictory.doToonVictory(1, self.involvedToons, self.toonRewardIds, self.toonRewardDicts, self.deathList, self.rewardPanel, allowGroupShot=0, uberList=self.uberList, noSkip=True)
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

    def __doneReward(self):

        self.doneBarrier('Reward')

    def exitReward(self):
        intervalName = 'RewardMovie'
        self.clearInterval(intervalName)
        if self.newState != 'Epilogue':
            self.releaseToons()
        self.unstash()
        self.rewardPanel.destroy()
        del self.rewardPanel
        self.phaseThreeMusic.stop()

    def setAttackCode(self, attackCode, avId=0):
        self.attackCode = attackCode
        self.attackAvId = avId
        if attackCode == ToontownGlobals.BossCogDizzy:
            self.setDizzy(1)
            self.cleanupAttacks()
            self.doAnimate(None, raised=0, happy=1)
        elif attackCode == ToontownGlobals.BossCogAreaAttack:
            self.doAnimate('areaAttack', now=1)
            siren = base.loader.loadSfx('phase_9/audio/sfx/CHQ_GOON_tractor_beam_alarmed.ogg')
            seq = Sequence(Func(self.setChatAbsolute, 'Back away, Toons!', CFSpeech),
                           Parallel(SoundInterval(siren), Func(self.geomFlashRed, self.geom)), Wait(1),
                           Parallel(SoundInterval(siren), Func(self.geomFlashRed, self.geom)), Wait(1),
                           Parallel(SoundInterval(siren), Func(self.geomFlashRed, self.geom)))
            seq.start()
        elif attackCode == ToontownGlobals.BossCogFrontAttack:
            self.setDizzy(0)
            self.doAnimate('frontAttack', now=1)
        elif attackCode == ToontownGlobals.BossCogRecoverDizzyAttack:
            self.setDizzy(0)
            self.doAnimate('frontAttack', now=1)

    def saySomething(self, chatString):
        intervalName = 'ChiefJusticeTaunt'
        seq = Sequence(name=intervalName)
        seq.append(Func(self.setChatAbsolute, chatString, CFSpeech))

    def geomFlashRed(self, geom):
        self.cleanupGeomFlash()
        geom.setColorScale(1, 1, 1, 1)
        i = Sequence(geom.colorScaleInterval(0.1, colorScale=VBase4(1, 0, 0, 1)),
                     geom.colorScaleInterval(0.3, colorScale=VBase4(1, 1, 1, 1)))
        self.geomFlashInterval = i
        i.start()

    def cleanupGeomFlash(self):
        if self.geomFlashInterval:
            self.geomFlashInterval.finish()
            self.geomFlashInterval = None
        return

    def enterEpilogue(self):

        self.cleanupIntervals()
        self.clearChat()
        if self.resistanceToon:
            self.__hideResistanceToon()
        self.stash()
        self.stopAnimate()
        self.controlToons()
        taskMgr.remove(self.uniqueName('returnToMezzoMelodyland'))
        taskMgr.doMethodLater(0.1, self.__returnToMezzoMelodyland,
                              self.uniqueName('returnToMezzoMelodyland'))

    def __returnToMezzoMelodyland(self, task):
        if not self.hasLocalToon():
            return Task.done

        targetZone = ToontownGlobals.MinniesMelodyland
        place = self.cr.playGame.getPlace()
        if place and hasattr(place, 'fsm'):
            place.fsm.request('teleportOut', [{
                'loader': ZoneUtil.getLoaderName(targetZone),
                'where': ZoneUtil.getWhereName(targetZone, 1),
                'how': 'teleportIn',
                'hoodId': targetZone,
                'zoneId': targetZone,
                'shardId': None,
                'avId': -1,
                'battle': 1
            }])
        return Task.done

    def exitEpilogue(self):
        taskMgr.remove(self.uniqueName('returnToMezzoMelodyland'))
        self.clearInterval('EpilogueMovieToonAnim')
        self.unstash()
        self.epilogueMusic.stop()

    def enterFrolic(self):
        self.cleanupIntervals()
        self.clearChat()
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

class MajorPlayerStagelight:
    """
    Hierarchy of a stagelight:

    stagelight_x [M]
        -> spotlight_x [M]
            -> spotlight_beam_x [TS]

    where [M] = ModelNode, [TS] = transparency bit.

    To modify color, do setColor on spotlight_x, but change light transparency with setAlphaScale on spotlight_beam_x.
    """

    durationToMove = (4.0, 6.0)
    delay = (1.0, 1.5)

    def __init__(self, stagelight, ranges):
        self.stagelightGeom = stagelight
        self.start, self.end = ranges
        self.cleaningUp = False

        # Initialize stagelight color.
        for spotlightGeom in self.stagelightGeom.getChildren():
            # Remove any pre-applied vertex colors on the stagelight nodes.
            spotlightGeom.setColor(1, 1, 1, 1)
        spotlight = self.stagelightGeom.find('spotlight_*')  # This includes the bulb (opaque) and beam (transparent)
        spotlight.setColorScaleOff()  # Make sure it doesn't get affected by color dimming
        spotlight.setColor(0.953, 0.878, 0.612, 1)  # Color of the spotlight, have a=1 so bulb isn't semi-transparent
        spotlight.find('spotlight_beam_*').setAlphaScale(0.4)  # Alpha value of the spotlight beam

        # Start at a random position in our range.
        self.stagelightGeom.setHpr(self.getValidAngle())

        # Start our movement task.
        self.moveIval = None
        self.startMoveIvalLoop()

    def cleanup(self):
        self.cleaningUp = True
        if self.moveIval:
            self.moveIval.finish()
        # we dont need to remove the stagelightGeom since it gets cleaned up with the model
        self.stagelightGeom = None

    """
    Various accessors
    """

    def getValidAngle(self):
        a, b, c = self.start
        x, y, z = self.end
        return Vec3(random.randint(a, x), random.randint(b, y), random.randint(c, z))

    def getDuration(self):
        start, end = self.durationToMove
        return start + ((end - start) * random.random())

    def getDelay(self):
        start, end = self.delay
        return start + ((end - start) * random.random())

    """
    Stagelight movement
    """

    def startMoveIvalLoop(self):
        if self.cleaningUp:
            return
        if self.moveIval:
            self.moveIval.finish()
            self.moveIval = None
        self.moveIval = Sequence(
            LerpHprInterval(self.stagelightGeom, self.getDuration(), self.getValidAngle(), blendType='easeInOut'),
            Wait(self.getDelay()),
            Func(self.startMoveIvalLoop),
        ).start()


class MajorPlayerDiscoFloor:
    """
    A Object representing a set of color-changing disco floor tiles.
    """

    colorChangeDuration = 4.0
    colorChangeDelay = 0.5

    tileColors = (
        Vec4(0.443, 0.522, 0.863, 1.0),
        Vec4(1, 0.302, 0.267, 1.0),
        Vec4(1, 0.851, 0.094, 1.0),
        Vec4(1, 0.635, 0.176, 1.0),
        Vec4(0.271, 0.984, 0.227, 1.0),
        Vec4(1, 0.431, 1, 1.0),
    )

    def __init__(self, discotiles):
        self.discotiles = discotiles
        # for tile in discotiles:
        #     tile.setColorScaleOff()

        # Initiate the painting on the disco tiles.
        self.setAllTileColor(0.992, 0.82, 0.431, 1.0)

        # Start our movement task.
        self.cleaningUp = False
        self.mainIval = None
        self.colorChangeIvals = [None] * len(self.discotiles)
        self.startColorChanges()

    def cleanup(self):
        self.cleaningUp = True
        if self.mainIval:
            self.mainIval.finish()
        for ival in self.colorChangeIvals:
            if ival:
                ival.finish()
        self.discotiles = []

    """
    Floor effects
    """

    def setAllTileColor(self, *color):
        for tile in self.discotiles:
            tile.setColor(color)

    def setTileColorsToList(self, colors):
        for i, tile in enumerate(self.discotiles):
            tile.setColor(colors[i])

    """
    Color operation
    """

    def getRandomTileColor(self):
        return random.choice(self.tileColors)

    def getShuffledTileColors(self):
        colorList = list(self.tileColors)
        random.shuffle(colorList)
        return colorList

    """
    Disco floor loop
    """

    def lerpTileBetweenColors(self, t, tile, oldColor, newColor):
        lerpedColor = oldColor + ((newColor - oldColor) * t)
        tile.setColor(lerpedColor)

    def getFloorRgbChangeSequence(self, tile, newColor):
        # Makes the sequence of this floor transposing to a new tile type.
        oldColor = tile.getColor()
        return LerpFunctionInterval(
            self.lerpTileBetweenColors, self.colorChangeDuration, blendType='easeInOut',
            extraArgs=[tile, oldColor, newColor]
        )

    def startColorChanges(self):
        self.mainIval = Track()
        for i in range(len(self.discotiles)):
            self.mainIval.append(
                (
                    self.colorChangeDuration * (i / len(self.discotiles)),
                    Func(self.doColorChange, i)
                )
            )
        self.mainIval.start()

    def doColorChange(self, i):
        if self.cleaningUp:
            return
        if self.colorChangeIvals[i]:
            self.colorChangeIvals[i].finish()
            self.colorChangeIvals[i] = None

        # Build the color change ival.
        self.colorChangeIvals[i] = Sequence(
            self.getFloorRgbChangeSequence(self.discotiles[i], self.getRandomTileColor()),
            Wait(self.colorChangeDelay),
            Func(self.doColorChange, i),
        ).start()
