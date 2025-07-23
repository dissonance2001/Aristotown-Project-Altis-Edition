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
from toontown.suit import DistributedBossCog
from direct.directnotify import DirectNotifyGlobal
from direct.interval.IntervalGlobal import *
from direct.particles import ParticleEffect
from toontown.suit import DistributedCashbotBossGoon
from toontown.suit import SuitDNA
from toontown.battle.BattleProps import *
from otp.otpbase import OTPGlobals
from toontown.battle import MovieToonVictory
from toontown.friends import FriendsListManager
from toontown.battle import RewardPanel
from toontown.suit import DistributedSuitBase
from toontown.suit import Suit
from toontown.battle import SuitBattleGlobals
from toontown.building import ElevatorConstants
from toontown.building import ElevatorUtils
from toontown.chat import ResistanceChat
from toontown.chat.ChatGlobals import *
from toontown.coghq import CogDisguiseGlobals
from toontown.distributed import DelayDelete
from toontown.nametag import NametagGlobals
from toontown.nametag.NametagGlobals import *
from toontown.toon import Toon
from toontown.toon import ToonDNA
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownGlobals


OneBossCog = None
TTL = TTLocalizer


class DistributedCashbotBoss(DistributedBossCog.DistributedBossCog, FSM.FSM):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedCashbotBoss')
    numFakeGoons = 3

    def __init__(self, cr):
        DistributedBossCog.DistributedBossCog.__init__(self, cr)
        FSM.FSM.__init__(self, 'DistributedCashbotBoss')
        self.resistanceToon = None
        self.resistanceToonOnstage = 0
        self.cranes = {}
        self.safes = {}
        self.goons = []
        self.latency = 0.5
        self.battleDifficulty = 0
        self.geomFlashInterval = None
        self.bonusUnites = 0
        self.bossMaxDamage = ToontownGlobals.CashbotBossMaxDamage
        self.elevatorType = ElevatorConstants.ELEVATOR_CFO
        base.boss = self
        self.currHP = 0
        self.maxHP = self.bossMaxDamage

        self.highroller = DistributedSuitBase.DistributedSuitBase(cr)
        suitDNA = SuitDNA.SuitDNA()
        suitDNA.newSuit('hroller')
        self.highroller.setDNA(suitDNA)
        self.highroller.setPickable(0)
        self.highroller.setDisplayName('High Roller\nCashbot\nLevel 100.mgr')
        self.highroller.doId = 0
        self.highroller.loop('neutral')

        self.stenographer = DistributedSuitBase.DistributedSuitBase(cr)
        suitDNA = SuitDNA.SuitDNA()
        suitDNA.newSuit('stenog')
        self.stenographer.setDNA(suitDNA)
        self.stenographer.setPickable(0)
        self.stenographer.hideName()
        self.stenographer.doId = 0
        self.stenographer.loop('neutral')
        self.litigator = DistributedSuitBase.DistributedSuitBase(cr)
        suitDNA = SuitDNA.SuitDNA()
        suitDNA.newSuit('lgator')
        self.litigator.setDNA(suitDNA)
        self.litigator.setPickable(0)
        self.litigator.hideName()
        self.litigator.doId = 0
        self.litigator.loop('neutral')
        self.casemanager = DistributedSuitBase.DistributedSuitBase(cr)
        suitDNA = SuitDNA.SuitDNA()
        suitDNA.newSuit('caseman')
        self.casemanager.setDNA(suitDNA)
        self.casemanager.setPickable(0)
        self.casemanager.hideName()
        self.casemanager.doId = 0
        self.casemanager.loop('neutral')
        self.scapegoat = DistributedSuitBase.DistributedSuitBase(cr)
        suitDNA = SuitDNA.SuitDNA()
        suitDNA.newSuit('sgoat')
        self.scapegoat.setDNA(suitDNA)
        self.scapegoat.setPickable(0)
        self.scapegoat.hideName()
        self.scapegoat.doId = 0
        self.scapegoat.loop('neutral')
        self.wsi = DistributedSuitBase.DistributedSuitBase(cr)
        suitDNA = SuitDNA.SuitDNA()
        suitDNA.newSuit('redd')
        self.wsi.setDNA(suitDNA)
        self.wsi.setPickable(0)
        self.wsi.hideName()
        self.wsi.doId = 0
        self.wsi.loop('neutral')
        self.chainsaw = DistributedSuitBase.DistributedSuitBase(cr)
        suitDNA = SuitDNA.SuitDNA()
        suitDNA.newSuit('chainsaw')
        self.chainsaw.setDNA(suitDNA)
        self.chainsaw.setPickable(0)
        self.chainsaw.hideName()
        self.chainsaw.doId = 0
        self.chainsaw.loop('neutral')
        self.firestarter = DistributedSuitBase.DistributedSuitBase(cr)
        suitDNA = SuitDNA.SuitDNA()
        suitDNA.newSuit('fires')
        self.firestarter.setDNA(suitDNA)
        self.firestarter.setPickable(0)
        self.firestarter.hideName()
        self.firestarter.doId = 0
        self.firestarter.loop('neutral')
        self.pacesetter = DistributedSuitBase.DistributedSuitBase(cr)
        suitDNA = SuitDNA.SuitDNA()
        suitDNA.newSuit('psetter')
        self.pacesetter.setDNA(suitDNA)
        self.pacesetter.setPickable(0)
        self.pacesetter.hideName()
        self.pacesetter.doId = 0
        self.pacesetter.loop('neutral2')
        self.treekiller = DistributedSuitBase.DistributedSuitBase(cr)
        suitDNA = SuitDNA.SuitDNA()
        suitDNA.newSuit('treek')
        self.treekiller.setDNA(suitDNA)
        self.treekiller.setPickable(0)
        self.treekiller.hideName()
        self.treekiller.doId = 0
        self.treekiller.loop('neutral')
        self.majorplayer = DistributedSuitBase.DistributedSuitBase(cr)
        suitDNA = SuitDNA.SuitDNA()
        suitDNA.newSuit('mplayer')
        self.majorplayer.setDNA(suitDNA)
        self.majorplayer.setPickable(0)
        self.majorplayer.hideName()
        self.majorplayer.doId = 0
        self.majorplayer.loop('neutral')
        self.dopa = DistributedSuitBase.DistributedSuitBase(cr)
        suitDNA = SuitDNA.SuitDNA()
        suitDNA.newSuit('dopa')
        self.dopa.setDNA(suitDNA)
        self.dopa.setPickable(0)
        self.dopa.hideName()
        self.dopa.doId = 0
        self.dopa.loop('neutral')
        self.dold = DistributedSuitBase.DistributedSuitBase(cr)
        suitDNA = SuitDNA.SuitDNA()
        suitDNA.newSuit('dold')
        self.dold.setDNA(suitDNA)
        self.dold.setPickable(0)
        self.dold.hideName()
        self.dold.doId = 0
        self.dold.loop('neutral')
        self.dola = DistributedSuitBase.DistributedSuitBase(cr)
        suitDNA = SuitDNA.SuitDNA()
        suitDNA.newSuit('dola')
        self.dola.setDNA(suitDNA)
        self.dola.setPickable(0)
        self.dola.hideName()
        self.dola.doId = 0
        self.dola.loop('neutral')
        self.derrman = DistributedSuitBase.DistributedSuitBase(cr)
        suitDNA = SuitDNA.SuitDNA()
        suitDNA.newSuit('derrman')
        self.derrman.setDNA(suitDNA)
        self.derrman.setPickable(0)
        self.derrman.hideName()
        self.derrman.doId = 0
        self.derrman.loop('neutral')
        self.dopr = DistributedSuitBase.DistributedSuitBase(cr)
        suitDNA = SuitDNA.SuitDNA()
        suitDNA.newSuit('dopr')
        self.dopr.setDNA(suitDNA)
        self.dopr.setPickable(0)
        self.dopr.hideName()
        self.dopr.doId = 0
        self.dopr.loop('neutral')
        self.derrhand = DistributedSuitBase.DistributedSuitBase(cr)
        suitDNA = SuitDNA.SuitDNA()
        suitDNA.newSuit('derrhand')
        self.derrhand.setDNA(suitDNA)
        self.derrhand.setPickable(0)
        self.derrhand.hideName()
        self.derrhand.doId = 0
        self.derrhand.loop('neutral')
        self.duckshuffler = DistributedSuitBase.DistributedSuitBase(cr)
        suitDNA = SuitDNA.SuitDNA()
        suitDNA.newSuit('duckshfl')
        self.duckshuffler.setDNA(suitDNA)
        self.duckshuffler.setPickable(0)
        self.duckshuffler.hideName()
        self.duckshuffler.doId = 0
        self.duckshuffler.loop('sit-dock')
        self.rainmaker = DistributedSuitBase.DistributedSuitBase(cr)
        suitDNA = SuitDNA.SuitDNA()
        suitDNA.newSuit('rainmake')
        self.rainmaker.setDNA(suitDNA)
        self.rainmaker.setPickable(0)
        self.rainmaker.hideName()
        self.rainmaker.doId = 0
        self.rainmaker.loop('sit-dock')
        self.ambassador = DistributedSuitBase.DistributedSuitBase(cr)
        suitDNA = SuitDNA.SuitDNA()
        suitDNA.newSuit('ambass')
        self.ambassador.setDNA(suitDNA)
        self.ambassador.setPickable(0)
        self.ambassador.hideName()
        self.ambassador.doId = 0
        self.ambassador.loop('neutral')
        self.wiretapper = DistributedSuitBase.DistributedSuitBase(cr)
        suitDNA = SuitDNA.SuitDNA()
        suitDNA.newSuit('wtapper')
        self.wiretapper.setDNA(suitDNA)
        self.wiretapper.setPickable(0)
        self.wiretapper.hideName()
        self.wiretapper.doId = 0
        self.wiretapper.loop('neutral')
        self.bookkeeper = DistributedSuitBase.DistributedSuitBase(cr)
        suitDNA = SuitDNA.SuitDNA()
        suitDNA.newSuit('bkeeper')
        self.bookkeeper.setDNA(suitDNA)
        self.bookkeeper.setPickable(0)
        self.bookkeeper.hideName()
        self.bookkeeper.doId = 0
        self.bookkeeper.loop('neutral')
        self.powerhouse = DistributedSuitBase.DistributedSuitBase(cr)
        suitDNA = SuitDNA.SuitDNA()
        suitDNA.newSuit('phouse')
        self.powerhouse.setDNA(suitDNA)
        self.powerhouse.setPickable(0)
        self.powerhouse.hideName()
        self.powerhouse.doId = 0
        self.powerhouse.loop('neutral')
        self.radiographer = DistributedSuitBase.DistributedSuitBase(cr)
        suitDNA = SuitDNA.SuitDNA()
        suitDNA.newSuit('radiog')
        self.radiographer.setDNA(suitDNA)
        self.radiographer.setPickable(0)
        self.radiographer.hideName()
        self.radiographer.doId = 0
        self.radiographer.loop('neutral')
        self.unionbuster = DistributedSuitBase.DistributedSuitBase(cr)
        suitDNA = SuitDNA.SuitDNA()
        suitDNA.newSuit('ubuster')
        self.unionbuster.setDNA(suitDNA)
        self.unionbuster.setPickable(0)
        self.unionbuster.hideName()
        self.unionbuster.doId = 0
        self.unionbuster.loop('neutral')
        self.racketeer = DistributedSuitBase.DistributedSuitBase(cr)
        suitDNA = SuitDNA.SuitDNA()
        suitDNA.newSuit('racket')
        self.racketeer.setDNA(suitDNA)
        self.racketeer.setPickable(0)
        self.racketeer.hideName()
        self.racketeer.doId = 0
        self.racketeer.loop('neutral')
        self.safesupervisor = DistributedSuitBase.DistributedSuitBase(cr)
        suitDNA = SuitDNA.SuitDNA()
        suitDNA.newSuit('safesupervis')
        self.safesupervisor.setDNA(suitDNA)
        self.safesupervisor.setPickable(0)
        self.safesupervisor.hideName()
        self.safesupervisor.doId = 0
        self.safesupervisor.loop('neutral')
        self.featherbedder = DistributedSuitBase.DistributedSuitBase(cr)
        suitDNA = SuitDNA.SuitDNA()
        suitDNA.newSuit('clubpres')
        self.featherbedder.setDNA(suitDNA)
        self.featherbedder.setPickable(0)
        self.featherbedder.hideName()
        self.featherbedder.doId = 0
        self.featherbedder.loop('neutral')
        self.witchhunter = DistributedSuitBase.DistributedSuitBase(cr)
        suitDNA = SuitDNA.SuitDNA()
        suitDNA.newSuit('ottoman')
        self.witchhunter.setDNA(suitDNA)
        self.witchhunter.setPickable(0)
        self.witchhunter.hideName()
        self.witchhunter.doId = 0
        self.witchhunter.loop('neutral')
        self.plutocrat = DistributedSuitBase.DistributedSuitBase(cr)
        suitDNA = SuitDNA.SuitDNA()
        suitDNA.newSuit('chairman')
        self.plutocrat.setDNA(suitDNA)
        self.plutocrat.setPickable(0)
        self.plutocrat.hideName()
        self.plutocrat.doId = 0
        self.plutocrat.loop('neutral')
        self.mrhollywood = DistributedSuitBase.DistributedSuitBase(cr)
        suitDNA = SuitDNA.SuitDNA()
        suitDNA.newSuit('mh2')
        self.mrhollywood.setDNA(suitDNA)
        self.mrhollywood.setPickable(0)
        self.mrhollywood.setDisplayName('Mr. Hollywood\nSellbot\nLevel 25.exe')
        self.mrhollywood.doId = 0
        self.mrhollywood.loop('neutral')
        self.videographer = DistributedSuitBase.DistributedSuitBase(cr)
        suitDNA = SuitDNA.SuitDNA()
        suitDNA.newSuit('videog')
        self.videographer.setDNA(suitDNA)
        self.videographer.setPickable(0)
        self.videographer.setDisplayName('Videographer\nSellbot\nLevel 99.mgr')
        self.videographer.doId = 0
        self.videographer.loop('neutral')
        self.director = DistributedSuitBase.DistributedSuitBase(cr)
        suitDNA = SuitDNA.SuitDNA()
        suitDNA.newSuit('mh2')
        self.director.setDNA(suitDNA)
        self.director.setPickable(0)
        self.director.setDisplayName('Mr. Hollywood\nSellbot\nLevel 25.exe')
        self.director.doId = 0
        self.director.loop('neutral')
        self.filmmaker = DistributedSuitBase.DistributedSuitBase(cr)
        suitDNA = SuitDNA.SuitDNA()
        suitDNA.newSuit('std2')
        self.filmmaker.setDNA(suitDNA)
        self.filmmaker.setPickable(0)
        self.filmmaker.setDisplayName('Stunt Double\nPressbot\nLevel 18.exe')
        self.filmmaker.doId = 0
        self.filmmaker.loop('neutral')
        self.majorplayer2 = DistributedSuitBase.DistributedSuitBase(cr)
        suitDNA = SuitDNA.SuitDNA()
        suitDNA.newSuit('mplayer')
        self.majorplayer2.setDNA(suitDNA)
        self.majorplayer2.setPickable(0)
        self.majorplayer2.setDisplayName('Major Player\nBossbot\nLevel 28.mgr')
        self.majorplayer2.doId = 0
        self.majorplayer2.loop('neutral')
        self.duckshuffler2 = DistributedSuitBase.DistributedSuitBase(cr)
        suitDNA = SuitDNA.SuitDNA()
        suitDNA.newSuit('duckshfl')
        self.duckshuffler2.setDNA(suitDNA)
        self.duckshuffler2.setPickable(0)
        self.duckshuffler2.setDisplayName('Duck Shuffler\nCashbot\nLevel 5.mgr')
        self.duckshuffler2.doId = 0
        self.duckshuffler2.loop('neutral')
        return

    def announceGenerate(self):
        DistributedBossCog.DistributedBossCog.announceGenerate(self)
        base.cr.forbidCheesyEffects(1)
        nameInfo = TTLocalizer.BossCogNameWithDept % {'name': TTLocalizer.CashbotBossName,
         'dept': SuitDNA.getDeptFullname(self.style.dept)}
        self.setName(nameInfo)
        self.setDisplayName(nameInfo)
        target = CollisionSphere(2, 0, 0, 3)
        targetNode = CollisionNode('headTarget')
        targetNode.addSolid(target)
        targetNode.setCollideMask(ToontownGlobals.PieBitmask)
        for headPart in self.animatedHeadParts:
            self.headTarget = headPart.attachNewNode(targetNode)
        shield = CollisionSphere(0, 0, 0.8, 7)
        shieldNode = CollisionNode('shield')
        shieldNode.addSolid(shield)
        shieldNode.setCollideMask(ToontownGlobals.PieBitmask)
        shieldNodePath = self.pelvis.attachNewNode(shieldNode)
        self.heldObject = None
        self.bossDamage = 0
        self.currHP = self.bossDamage
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
        base.localAvatar.chatMgr.chatInputSpeedChat.addCFOMenu()
        self.titleText = OnscreenText('Cashbot Vault\nThe High Roller', fg=(1, 1, 1, 1), shadow=(0, 0, 0, 1), font=ToontownGlobals.getSuitFont(), pos=(0, -0.5), scale=0.16, drawOrder=0, mayChange=1)
        self.titleText.hide()
        global OneBossCog
        if OneBossCog != None:
            self.notify.warning('Multiple BossCogs visible.')
        OneBossCog = self
        return

    def disable(self):
        global OneBossCog
        DistributedBossCog.DistributedBossCog.disable(self)
        base.cr.forbidCheesyEffects(0)
        self.demand('Off')
        self.unloadEnvironment()
        self.__cleanupResistanceToon()
        self.fnp.removeNode()
        self.physicsMgr.clearLinearForces()
        self.battleThreeMusic.stop()
        removeTint = Sequence(LerpColorScaleInterval(render, 0.1, Vec4(1, 1, 1, 1)))
        removeTint.start()
        self.epilogueMusic.stop()
        base.localAvatar.chatMgr.chatInputSpeedChat.removeCFOMenu()
        if OneBossCog == self:
            OneBossCog = None
        return
		
    def setBonusUnites(self, unites):
        self.bonusUnites = unites

    def __makeResistanceToon(self):
        if self.resistanceToon:
            return
        npc = Toon.Toon()
        npc.setPickable(0)
        npc.setPlayerType(NametagGlobals.CCNonPlayer)
        dna = ToonDNA.ToonDNA()
        dna.newToonRandom(11237, 'f', 1)
        dna.head = 'pls'
        npc.setDNAString(dna.makeNetString())
        npc.animFSM.request('neutral')
        self.resistanceToon = npc
        self.resistanceToon.setPosHpr(*ToontownGlobals.CashbotRTBattleOneStartPosHpr)
        state = random.getstate()
        random.seed(self.doId)
        self.resistanceToon.suitType = SuitDNA.getRandomSuitByDept('m')
        self.resistanceToon.setName(TTLocalizer.ResistanceToonName)
        self.resistanceToon.setDisplayName(TTLocalizer.ResistanceToonName)
        random.setstate(state)
        self.fakeGoons = []
        for i in xrange(self.numFakeGoons):
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
            for i in xrange(self.numFakeGoons):
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
        self.highRollerArena = loader.loadModel('phase_13/models/events/apriltoons/highroller/cc_m_ara_int_highroller.bam')
        self.highRollerTV = loader.loadModel('phase_13/models/events/apriltoons/highroller/cc_m_ara_hr_prp_tv_base.bam')
        self.highRollerWheel = globalPropPool.getProp('wheel')
        self.highRollerWheel.loop('wheel')
        self.highRollerWheel.setScale(6)
        self.midVault = loader.loadModel('phase_10/models/cogHQ/MidVault.bam')
        self.endVault = loader.loadModel('phase_10/models/cogHQ/EndVault.bam')
        self.lightning = loader.loadModel('phase_10/models/cogHQ/CBLightning.bam')
        self.magnet = loader.loadModel('phase_10/models/cogHQ/CBMagnet.bam')
        self.magnet = loader.loadModel('phase_10/models/cogHQ/CBMagnetBlue.bam')
        self.sideMagnet = loader.loadModel('phase_10/models/cogHQ/CBMagnetRed.bam')
        self.craneArm = loader.loadModel('phase_10/models/cogHQ/CBCraneArm.bam')
        self.controls = loader.loadModel('phase_10/models/cogHQ/CBCraneControls.bam')
        self.stick = loader.loadModel('phase_10/models/cogHQ/CBCraneStick.bam')
        self.safe = loader.loadModel('phase_10/models/cogHQ/CBSafe.bam')
        self.safe2 = loader.loadModel('phase_10/models/cogHQ/CBSafe.bam')
        self.eyes = loader.loadModel('phase_10/models/cogHQ/CashBotBossEyes.bam')
        self.cableTex = self.craneArm.findTexture('MagnetControl')
        self.eyes.setPosHprScale(4.5, 0, -2.5, 90, 90, 0, 0.4, 0.4, 0.4)
        self.safe2.setPosHprScale(0, 0, 0, -90, -90, 0, 1, 1, 1)
        for headPart in self.animatedHeadParts:
            self.eyes.reparentTo(headPart)
            self.safe2.reparentTo(headPart)
        self.eyes.hide()
        self.safe2.hide()
        self.midVault.setPos(10, -222, -70.7)
        self.highRollerArena.setPos(0, -222, -4.05)
        self.endVault.setPos(84, -201, -6)
        self.geom = NodePath('geom')
        self.midVault.reparentTo(self.geom)
        self.highRollerArena.reparentTo(self.geom)
        self.endVault.reparentTo(self.geom)
        self.ambassador.reparentTo(self.geom)
        self.ambassador.setPosHpr(-37.5, -252.5, 11.75, -20, 0, 0)
        self.wiretapper.reparentTo(self.geom)
        self.wiretapper.setPosHpr(-32.5, -254.5, 11.75, -20, 0, 0)
        self.bookkeeper.reparentTo(self.geom)
        self.bookkeeper.setPosHpr(-27.5, -256.5, 11.75, -20, 0, 0)
        self.powerhouse.reparentTo(self.geom)
        self.powerhouse.setPosHpr(-22.5, -258.5, 11.75, -20, 0, 0)
        self.safesupervisor.reparentTo(self.geom)
        self.safesupervisor.setPosHpr(-37.5, -240.5, 4.75, -20, 0, 0)
        self.unionbuster.reparentTo(self.geom)
        self.unionbuster.setPosHpr(-32.5, -242.5, 4.75, -20, 0, 0)
        self.radiographer.reparentTo(self.geom)
        self.radiographer.setPosHpr(-27.5, -244.5, 4.75, -20, 0, 0)
        self.racketeer.reparentTo(self.geom)
        self.racketeer.setPosHpr(-22.5, -246.5, 4.75, -20, 0, 0)
        self.stenographer.reparentTo(self.geom)
        self.stenographer.setPosHpr(-25, -252.5, 7.75, -20, 0, 0)
        self.litigator.reparentTo(self.geom)
        self.litigator.setPosHpr(-30, -250.5, 7.75, -20, 0, 0)
        self.duckshuffler.reparentTo(self.geom)
        self.duckshuffler.setPosHpr(-4, -247.5, 15.75, -180, 0, 0)
        self.rainmaker.reparentTo(self.geom)
        self.rainmaker.setPosHpr(4, -247.5, 15.75, -180, 0, 0)
        self.scapegoat.reparentTo(self.geom)
        self.scapegoat.setPosHpr(-35, -248.5, 7.75, -20, 0, 0)
        self.wsi.reparentTo(self.geom)
        self.wsi.setPosHpr(-40, -246.5, 7.75, -20, 0, 0)
        self.casemanager.reparentTo(self.geom)
        self.casemanager.setPosHpr(-20, -254.5, 7.75, -20, 0, 0)
        self.derrman.reparentTo(self.geom)
        self.derrman.setPosHpr(17.5, -256.5, 7.75, 20, 0, 0)
        self.derrhand.reparentTo(self.geom)
        self.derrhand.setPosHpr(25, -252.5, 7.75, 20, 0, 0)
        self.dold.reparentTo(self.geom)
        self.dold.setPosHpr(30, -250.5, 7.75, 20, 0, 0)
        self.dopa.reparentTo(self.geom)
        self.dopa.setPosHpr(35, -248.5, 7.75, 20, 0, 0)
        self.dopr.reparentTo(self.geom)
        self.dopr.setPosHpr(40, -246.5, 7.75, 20, 0, 0)
        self.dola.reparentTo(self.geom)
        self.highroller.reparentTo(self.geom)
        self.highroller.setPosHpr(0, -200, 0, 180, 0, 0)
        self.highroller.hide()
        self.mrhollywood.reparentTo(self.geom)
        self.mrhollywood.setPosHpr(5, -200, 0, 180, 0, 0)
        self.mrhollywood.hide()
        self.videographer.reparentTo(self.geom)
        self.videographer.setPosHpr(-5, -200, 0, 180, 0, 0)
        self.videographer.hide()
        self.majorplayer2.reparentTo(self.geom)
        self.majorplayer2.setPosHpr(5, -200, 0, 180, 0, 0)
        self.duckshuffler2.reparentTo(self.geom)
        self.duckshuffler2.setPosHpr(-5, -200, 0, 180, 0, 0)
        self.duckshuffler2.hide()
        self.director.reparentTo(self.geom)
        self.director.setPosHpr(-10, -200, 0, 180, 0, 0)
        self.director.hide()
        self.filmmaker.reparentTo(self.geom)
        self.filmmaker.setPosHpr(10, -200, 0, 180, 0, 0)
        self.filmmaker.hide()
        self.dola.setPosHpr(20, -254.5, 7.75, 20, 0, 0)
        self.featherbedder.reparentTo(self.geom)
        self.featherbedder.setPosHpr(20, -246.5, 4.75, 20, 0, 0)
        self.witchhunter.reparentTo(self.geom)
        self.witchhunter.setPosHpr(35, -240.5, 4.75, 20, 0, 0)
        self.plutocrat.reparentTo(self.geom)
        self.plutocrat.setPosHpr(30, -242.5, 1.75, 20, 0, 0)
        self.majorplayer.reparentTo(self.geom)
        self.majorplayer.setPosHpr(-42.5, -250.5, 11.75, -20, 0, 0)
        self.chainsaw.reparentTo(self.geom)
        self.chainsaw.setPosHpr(42.5, -250.5, 11.75, 20, 0, 0)
        self.treekiller.reparentTo(self.geom)
        self.treekiller.setPosHpr(37.5, -252.5, 11.75, 20, 0, 0)
        self.firestarter.reparentTo(self.geom)
        self.firestarter.setPosHpr(27.5, -256.5, 11.75, 20, 0, 0)
        self.pacesetter.reparentTo(self.geom)
        self.pacesetter.setPosHpr(22.5, -258.5, 11.75, 20, 0, 0)
        self.highRollerWheel.reparentTo(self.geom)
        self.highRollerWheel.setPosHpr(0, -170, 0, 180, 0, 0)
        self.highRollerTV.reparentTo(self.geom)
        self.highRollerTV.setPosHpr(-25, -185, 21.75, -10, 0, 0)
        self.endVault.findAllMatches('**/MagnetArms').detach()
        self.endVault.findAllMatches('**/Safes').detach()
        self.endVault.findAllMatches('**/MagnetControlsAll').detach()
        cn = self.endVault.find('**/wallsCollision').node()
        cn.setIntoCollideMask(OTPGlobals.WallBitmask | ToontownGlobals.PieBitmask)
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
        self.elevatorMusic = base.loader.loadMusic('phase_10/audio/bgm/cb_elevator.ogg')
        self.battleTwoMusic = base.loadMusic('phase_7/audio/bgm/encntr_suit_winning_indoor.ogg')
        self.midCutsceneMusic = base.loadMusic('phase_10/audio/bgm/CB_boss_cutscene.ogg')
        self.battleThreeMusic = base.loadMusic('phase_10/audio/bgm/encntr_cfo_crane.ogg')

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
            for i in xrange(cn.getNumSolids()):
                solid = cn.getSolid(i)
                if isinstance(solid, CollisionPolygon):
                    plane = Plane(solid.getPlane())
                    planes.append(plane)
                else:
                    self.notify.warning('Unexpected collision solid: %s' % repr(solid))
                    newCollisionNode.addSolid(plane)

        newCollisionNode.setIntoCollideMask(newCollideMask)
        threshold = 0.1
        planes.sort(lambda p1, p2: p1.compareTo(p2, threshold))
        lastPlane = None
        for plane in planes:
            if lastPlane == None or plane.compareTo(lastPlane, threshold) != 0:
                cp = CollisionPlane(plane)
                newCollisionNode.addSolid(cp)
                lastPlane = plane

        return NodePath(newCollisionNode)

    def __makeGoonMovieForIntro(self):
        goonTrack = Parallel()
        goon = self.fakeGoons[0]
        goonTrack.append(Sequence(
            goon.posHprInterval(0, Point3(111, -287, 0), VBase3(165, 0, 0)),
            goon.posHprInterval(9, Point3(101, -323, 0), VBase3(165, 0, 0)),
            goon.hprInterval(1, VBase3(345, 0, 0)),
            goon.posHprInterval(9, Point3(111, -287, 0), VBase3(345, 0, 0)),
            goon.hprInterval(1, VBase3(165, 0, 0)),
            goon.posHprInterval(9.5, Point3(104, -316, 0), VBase3(165, 0, 0)),
            Func(goon.request, 'Stunned'),
            Wait(1)))
        goon = self.fakeGoons[1]
        goonTrack.append(Sequence(
            goon.posHprInterval(0, Point3(119, -315, 0), VBase3(357, 0, 0)),
            goon.posHprInterval(9, Point3(121, -280, 0), VBase3(357, 0, 0)),
            goon.hprInterval(.5, VBase3(-345, 145, 345)),
            goon.hprInterval(1, VBase3(177, 0, 0)),
            goon.posHprInterval(9, Point3(119, -315, 0), VBase3(177, 0, 0)),
            goon.hprInterval(1, VBase3(357, 0, 0)),
            goon.posHprInterval(9, Point3(121, -280, 0), VBase3(357, 0, 0))))
        goon = self.fakeGoons[2]
        goonTrack.append(Sequence(
            goon.posHprInterval(0, Point3(102, -320, 0), VBase3(231, 0, 0)),
            goon.posHprInterval(9, Point3(127, -337, 0), VBase3(231, 0, 0)),
            goon.hprInterval(1, VBase3(51, 0, 0)),
            goon.posHprInterval(9, Point3(102, -320, 0), VBase3(51, 0, 0)),
            goon.hprInterval(1, VBase3(231, 0, 0)),
            goon.posHprInterval(9, Point3(127, -337, 0), VBase3(231, 0, 0))))
        return Sequence(Func(self.__showFakeGoons, 'Walk'), goonTrack, Func(self.__hideFakeGoons))

    def makeIntroductionMovie(self, delayDeletes):
        for toonId in self.involvedToons:
            toon = self.cr.doId2do.get(toonId)
            if toon:
                delayDeletes.append(DelayDelete.DelayDelete(toon, 'CashbotBoss.makeIntroductionMovie'))

        rtTrack = Sequence()
        startPos = Point3(ToontownGlobals.CashbotBossOffstagePosHpr[0], ToontownGlobals.CashbotBossOffstagePosHpr[1], ToontownGlobals.CashbotBossOffstagePosHpr[2])
        battlePos = Point3(ToontownGlobals.CashbotBossBattleOnePosHpr[0], ToontownGlobals.CashbotBossBattleOnePosHpr[1], ToontownGlobals.CashbotBossBattleOnePosHpr[2])
        battleHpr = VBase3(ToontownGlobals.CashbotBossBattleOnePosHpr[3], ToontownGlobals.CashbotBossBattleOnePosHpr[4], ToontownGlobals.CashbotBossBattleOnePosHpr[5])
        bossTrack = Sequence()
        bossTrack.append(Func(self.reparentTo, render))
        bossTrack.append(Func(self.getGeomNode().setH, 180))
        bossTrack.append(Func(self.pelvis.setHpr, self.pelvisForwardHpr))
        bossTrack.append(Func(self.loop, 'Ff_neutral'))
        track, hpr = self.rollBossToPoint(battlePos, None, battlePos, None, 0)
        bossTrack.append(track)
        track, hpr = self.rollBossToPoint(battlePos, hpr, battlePos, battleHpr, 0)
        bossTrack.append(track)
        bossTrack.append(Func(self.getGeomNode().setH, 0))
        bossTrack.append(Func(self.pelvis.setHpr, self.pelvisReversedHpr))
        goonTrack = self.__makeGoonMovieForIntro()
        attackToons = TTL.CashbotBossCogAttack
        self.titleSeq = Sequence(Func(self.titleText.show), Wait(5), LerpColorScaleInterval(self.titleText, 1, VBase4(1, 1, 1, 0)))  


        rToon = self.resistanceToon
        rToon.setPosHpr(*ToontownGlobals.CashbotRTBattleOneStartPosHpr)
        track = Sequence(
            #Func(base.camera.setPosHpr, 82, -219, 5, 267, 0, 0),
                        Func(base.camera.reparentTo, render),
                        Func(base.camera.setPosHpr, 0, - 240, 10, 0, 0, 0),
                        Parallel(
                            bossTrack,
                            Sequence(Func(self.majorplayer2.setChatAbsolute, "How's the hoop skip out there toe-taps, can't thank ya enough for these claps!", CFSpeech),
                             Wait(4),
                                     Func(self.majorplayer2.setChatAbsolute,
                                          "Takes two to tango, babe, and I am proud and poppin' to introduce today's special guest!",
                                          CFSpeech),
                                     Wait(3),
                                     Func(self.duckshuffler2.show), ActorInterval(self.duckshuffler2, 'slip-forward'), Func(self.duckshuffler2.loop, 'neutral'),
                                     Func(self.majorplayer2.setChatAbsolute,
                                          "Buck Ruffler: The Duck Shuffler!",
                                          CFSpeech), Func(self.duckshuffler2.setChatAbsolute,
                                          "Oh my Cogth thath me",
                                          CFSpeech), Wait(1.5), Func(self.duckshuffler2.setChatAbsolute,
                                                          "Waith I needth to thay it too",
                                          CFSpeech), Wait(1.5), Func(self.duckshuffler2.setChatAbsolute,
                                                          "Buck Ruffler: The Duck Thuffler!",
                                          CFSpeech),
                                     Wait(3),
                                    Func(self.majorplayer2.setChatAbsolute,
                                          "Oooh, but that's no high class brass, looks like we got some surprise guests! Baby Blue, ya knew my words were true-I told ya we'd meet again!",
                                          CFSpeech),
                                     Wait(3),
                                     Func(self.duckshuffler2.setChatAbsolute,
                                          "I gueth we'll have to give em tha thpecial thow though! Come on mic thpam!",
                                          CFSpeech),
                                     Wait(2),
                                     Func(self.majorplayer2.setChatAbsolute,
                                          "Hachahoo hooi-didibadoo! Here's a special shabaadoopdaa-show from we to you!",
                                          CFSpeech),
                                     Wait(3),
                                     Func(self.majorplayer2.removeNode), Func(self.duckshuffler2.removeNode),
                                Func(rToon.clearChat),
                            #base.camera.posHprInterval(1, Point3(93.3, -230, 0.7), VBase3(268.9, 39.7, 8.3), blendType='easeInOut'),
                            Func(self.titleSeq.start),
                                Func(self.highroller.show),
                            Func(self.highroller.setChatAbsolute, "Welcome back to the Tooniverffe'ff favorite ffhow!", CFSpeech),
                             Wait(4),
                            Func(self.highroller.setChatAbsolute, "What'ya waitin' for, babe? Hop on fftage! let'ff get hoppin' and boppin', jumpin' and jinglin', ffingin' and ffwingin'!", CFSpeech),
                            Wait(4),
                            Func(self.highroller.setChatAbsolute, "Ohoho-no-no, takeff a party to partiffipate and play, and I ffay play!!", CFSpeech),
                            self.loseCogSuits(self.toonsA + self.toonsB, render, (113, -228, 10, 90, 0, 0)),
                            Wait(1),
                            Func(rToon.setHpr, 0, 0, 0),
                            self.loseCogSuits([rToon], render, (133, -243, 5, 143, 0, 0), True),
                            Wait(1),
                                    self.toonNormalEyes(self.involvedToons),
                                    self.toonNormalEyes([self.resistanceToon], True),
                                    Func(rToon.clearChat),
            Func(base.camera.reparentTo, render),
            Func(base.camera.setPosHpr, 0, - 240, 10, 0, 0, 0),
                                    #Func(base.camera.setPosHpr, 93.3, -230, 0.7, -92.9, 39.7, 8.3),
                                   # base.camera.posHprInterval(2, Point3(93.3, -230, 0.7), VBase3(268.9, 39.7, 8.3), blendType='easeInOut'),
            Func(self.highroller.setChatAbsolute,
                 "Here'ff a ffpinnin wheel I know ya can get behaHAHAHA-hind!", CFSpeech),
            Wait(4), Func(self.highroller.hide),
            Func(self.highroller.setChatAbsolute, '', CFSpeech))))
        return Sequence(Func(base.camera.reparentTo, render), track)

    def makePrepareBattleTwoMovie(self, delayDeletes):
        startPos = Point3(ToontownGlobals.CashbotBossBattleOnePosHpr[0], ToontownGlobals.CashbotBossBattleOnePosHpr[1], ToontownGlobals.CashbotBossBattleOnePosHpr[2])
        battlePos = Point3(ToontownGlobals.CashbotBossBattleThreePosHpr[0], ToontownGlobals.CashbotBossBattleThreePosHpr[1], ToontownGlobals.CashbotBossBattleThreePosHpr[2])
        startHpr = Point3(ToontownGlobals.CashbotBossBattleOnePosHpr[3], ToontownGlobals.CashbotBossBattleOnePosHpr[4], ToontownGlobals.CashbotBossBattleOnePosHpr[5])
        battleHpr = VBase3(ToontownGlobals.CashbotBossBattleThreePosHpr[3], ToontownGlobals.CashbotBossBattleThreePosHpr[4], ToontownGlobals.CashbotBossBattleThreePosHpr[5])
        finalHpr = VBase3(135, 0, 0)
        toonPosHpr = ToontownGlobals.CashbotRTBattleTwoEndPosHpr
        bossTrack = Sequence()
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
        rToon.setPosHpr(*ToontownGlobals.CashbotRTBattleTwoStartPosHpr)
        self.__arrangeToonsAroundResistanceToon()
        base.playMusic(self.midCutsceneMusic, looping=1, volume=0.9)
        track = Sequence(
            # Func(base.camera.setPosHpr, 82, -219, 5, 267, 0, 0),
            Func(base.camera.reparentTo, render),
            Func(base.camera.setPosHpr, 0, - 240, 10, 0, 0, 0),
            Parallel(Func(self.highroller.show),
                bossTrack,
                Sequence(
                    Wait(3),
                    Func(rToon.clearChat),
            # base.camera.posHprInterval(1, Point3(93.3, -230, 0.7), VBase3(268.9, 39.7, 8.3), blendType='easeInOut'),
            Func(self.highroller.setChatAbsolute, "WhAHAHAHAt a ffhow!", CFSpeech),
            Wait(5),
            Func(self.highroller.setChatAbsolute,
                 "Oooo-hooo-hooo, ratingff are ffkyrocketing! Line goeff up, head turner! Keep thoffe cameraff rollin'!", CFSpeech),
            Wait(5),
            Func(self.highroller.setChatAbsolute,
                 "Let'ff ffee the nefft big play for today!", CFSpeech),
            Wait(5),
            Func(base.camera.reparentTo, render),
            Func(base.camera.setPosHpr, 0, - 240, 10, 0, 0, 0),
            # Func(base.camera.setPosHpr, 93.3, -230, 0.7, -92.9, 39.7, 8.3),
            # base.camera.posHprInterval(2, Point3(93.3, -230, 0.7), VBase3(268.9, 39.7, 8.3), blendType='easeInOut'),
            Func(self.highroller.setChatAbsolute,
                 "WHAT A TWIFFT, BUTTERCUP BLUE!", CFSpeech),
            Wait(5),
            Func(self.highroller.loop, 'rolled'), Func(self.mrhollywood.loop, 'rolled'), Func(self.director.loop, 'rolled'), Func(self.filmmaker.loop, 'rolled'), Func(self.videographer.loop, 'rolled'),
                    Func(self.mrhollywood.show),  Func(self.filmmaker.show),  Func(self.director.show), Func(self.videographer.show),
            Func(self.highroller.setChatAbsolute,
                 "Give a warm, hot on the oven, flaff fire, round of applauffe for my ffecond favorite ffet of...", CFSpeech),
            Wait(5),
            Func(self.highroller.setChatAbsolute,
                 "Ffcallywagff, clownff, quipffterff, harlequinff, buffoonff, wiffecrackerff, raffcalff, ne'er-do-wellff, lollyggaggerff, tomfoolerff, jokerff, hoaxerff, trickffterff, jokeffmithff, humoriftfth, rabbelroufferff, ffhenaiganifferff, goofffterff, merrymakerff, ruffianff, ffkylarkff, gooberff,", CFSpeech),
            Wait(5),
            Func(self.highroller.setChatAbsolute,
                 "Have fun with thiff one, ffweetie pie!",
                 CFSpeech),
            Wait(5),
            Func(self.highroller.setChatAbsolute, '', CFSpeech),
                    Func(self.__showToons),
        Func(self.mrhollywood.removeNode), Func(self.highroller.removeNode),  Func(self.videographer.removeNode), Func(self.director.removeNode),  Func(self.filmmaker.removeNode))))
        return Sequence(Func(base.camera.reparentTo, self), base.camera.posHprInterval(1, Point3(0, -27, 25), VBase3(0, -18, 0), blendType='easeInOut'), track, Func(base.camera.reparentTo, render))
		
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

            retval.append(Sequence(Wait(delay), Func(toon.wrtReparentTo, render), Func(toWalk, toon), Func(toon.headsUp, destPos), LerpPosInterval(toon, 2, destPos), Func(toon.headsUp, self), Func(toNeutral, toon)))
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
        for i in xrange(1, self.numFakeGoons):
            goon = self.fakeGoons[i]
            goonLoop.append(Sequence(goon.posHprInterval(8, goonPosHprs[i][0], goonPosHprs[i][1]), goon.posHprInterval(8, goonPosHprs[i][2], goonPosHprs[i][3])))

        goonTrack = Sequence(Func(self.__showFakeGoons, 'Walk'), Func(mainGoon.request, 'Stunned'), Func(goonLoop.loop), Wait(20))
        return goonTrack

    def makePrepareBattleThreeMovie(self, delayDeletes, crane, safe):
        for toonId in self.involvedToons:
            toon = self.cr.doId2do.get(toonId)
            if toon:
                delayDeletes.append(DelayDelete.DelayDelete(toon, 'CashbotBoss.makePrepareBattleThreeMovie'))

        startPos = Point3(ToontownGlobals.CashbotBossBattleOnePosHpr[0], ToontownGlobals.CashbotBossBattleOnePosHpr[1], ToontownGlobals.CashbotBossBattleOnePosHpr[2])
        battlePos = Point3(ToontownGlobals.CashbotBossBattleThreePosHpr[0], ToontownGlobals.CashbotBossBattleThreePosHpr[1], ToontownGlobals.CashbotBossBattleThreePosHpr[2])
        startHpr = Point3(ToontownGlobals.CashbotBossBattleOnePosHpr[3], ToontownGlobals.CashbotBossBattleOnePosHpr[4], ToontownGlobals.CashbotBossBattleOnePosHpr[5])
        battleHpr = VBase3(ToontownGlobals.CashbotBossBattleThreePosHpr[3], ToontownGlobals.CashbotBossBattleThreePosHpr[4], ToontownGlobals.CashbotBossBattleThreePosHpr[5])
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
        return Sequence(Func(base.camera.reparentTo, self), base.camera.posHprInterval(1, Point3(0, -27, 25), VBase3(0, -18, 0), blendType='easeInOut'), track) #Func(base.camera.setPosHpr, 0, -27, 25, 0, -18, 0)

    def moveToonsToBattleThreePos(self, toons):
        track = Parallel()
        for i in xrange(len(toons)):
            toon = base.cr.doId2do.get(toons[i])
            if toon:
                posHpr = ToontownGlobals.CashbotToonsBattleThreeStartPosHpr[i]
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
        trainPassingSfx = base.loadSfx('phase_10/audio/sfx/CBHQ_TRAIN_pass.ogg')
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
                Func(self.setPosHpr, *ToontownGlobals.CashbotBossBattleThreePosHpr),
                ActorInterval(self, 'Fb_firstHit'),
                ActorInterval(self, 'Fb_down2Up'))),
            (1.0, Func(self.setChatAbsolute, hadEnough, CFSpeech)),
            (5.5, Parallel(
                Func(base.camera.setPosHpr, 100, -315, 16, -20, 0, 0),
                #base.camera.posHprInterval(1, Point3(100, -315, 16), VBase3(-20, 0, 0), blendType='easeInOut'),
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
        for crane in self.cranes.values():
            crane.demand('Free')

    def hideBattleThreeObjects(self):
        for goon in self.goons:
            goon.demand('Off')

        for safe in self.safes.values():
            safe.demand('Off')

        for crane in self.cranes.values():
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
        for i in xrange(numToons):
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
        base.playMusic(self.midCutsceneMusic, looping=1, volume=0.9)
        DistributedBossCog.DistributedBossCog.enterIntroduction(self)

    def exitIntroduction(self):
        DistributedBossCog.DistributedBossCog.exitIntroduction(self)
        self.midCutsceneMusic.stop()

    def enterBattleOne(self):
        DistributedBossCog.DistributedBossCog.enterBattleOne(self)
        self.reparentTo(render)
        self.setPosHpr(*ToontownGlobals.CashbotBossBattleOnePosHpr)
        self.show()
        self.pelvis.setHpr(self.pelvisReversedHpr)
        self.doAnimate()
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
        base.playMusic(self.battleOneMusic, looping=1, volume=0.9)

    def exitBattleOne(self):
        DistributedBossCog.DistributedBossCog.exitBattleOne(self)
        
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
        ElevatorUtils.closeDoors(self.leftDoor, self.rightDoor, ElevatorConstants.ELEVATOR_CFO)
    
    def enterBattleTwo(self):
        self.reparentTo(render)
        self.evWalls.unstash()
        self.setPosHpr(*ToontownGlobals.CashbotBossBattleOnePosHpr)
        self.show()
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
        self.controlToons()
        NametagGlobals.setWant2dNametags(True)
        NametagGlobals.setWantActiveNametags(True)
        base.localAvatar.setFriendsListButtonActive(1)
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
        taskMgr.add(self.__doPhysics, self.uniqueName('physics'), priority=50)

    def __beginBattleThree(self):
        intervalName = 'PrepareBattleThreeMovie'
        self.clearInterval(intervalName)
        self.doneBarrier('PrepareBattleThree')

    def exitPrepareBattleThree(self):
        intervalName = 'PrepareBattleThreeMovie'
        self.clearInterval(intervalName)
        self.unstickToons()
        self.releaseToons()
        if self.newState == 'BattleThree':
            self.movieCrane.request('Free')
            self.movieSafe.request('Initial')
        NametagGlobals.setWant2dNametags(True)
        ElevatorUtils.closeDoors(self.leftDoor, self.rightDoor, ElevatorConstants.ELEVATOR_CFO)
        taskMgr.remove(self.uniqueName('physics'))
		
    def setBattleDifficulty(self, diff):
        self.notify.debug('battleDifficulty = %d' % diff)
        self.battleDifficulty = diff

    def enterBattleThree(self):
        DistributedBossCog.DistributedBossCog.enterBattleThree(self)
        self.clearChat()
        self.resistanceToon.clearChat()
        self.reparentTo(render)
        self.setPosHpr(*ToontownGlobals.CashbotBossBattleThreePosHpr)
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
        base.playMusic(self.battleThreeMusic, looping=1, volume=0.9)
        taskMgr.add(self.__doPhysics, self.uniqueName('physics'), priority=25)

    def exitBattleThree(self):
        DistributedBossCog.DistributedBossCog.exitBattleThree(self)
        bossDoneEventName = self.uniqueName('DestroyedBoss')
        self.ignore(bossDoneEventName)
        self.stopAnimate()
        self.cleanupAttacks()
        self.setDizzy(0)
        self.removeHealthBar()
        localAvatar.setCameraFov(ToontownGlobals.CogHQCameraFov)
        if self.newState != 'Victory':
            self.battleThreeMusic.stop()
        taskMgr.remove(self.uniqueName('physics'))

    def enterVictory(self):
        self.cleanupIntervals()
        self.reparentTo(render)
        self.setPosHpr(*ToontownGlobals.CashbotBossBattleThreePosHpr)
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
        intervalName = 'VictoryMovie'
        seq = Sequence(self.makeBossFleeMovie(), Func(self.__continueVictory), name=intervalName)
        seq.start()
        self.storeInterval(seq, intervalName)
        if self.oldState != 'BattleThree':
            base.playMusic(self.battleThreeMusic, looping=1, volume=0.9)

    def __continueVictory(self):
        self.doneBarrier('Victory')

    def exitVictory(self):
        self.cleanupIntervals()
        if self.newState != 'Reward':
            if self.hasLocalToon():
                self.toWalkMode()
        self.__showToons()
        self.door3.setPos(0, 0, 0)
        if self.newState != 'Reward':
            self.battleThreeMusic.stop()

    def enterReward(self):
        self.cleanupIntervals()
        self.clearChat()
        self.resistanceToon.clearChat()
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
        if self.oldState != 'Victory':
            base.playMusic(self.battleThreeMusic, looping=1, volume=0.9)

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
        self.battleThreeMusic.stop()

    def setAttackCode(self, attackCode, avId=0):
        DistributedBossCog.DistributedBossCog.setAttackCode(self, attackCode, avId)
        if attackCode == ToontownGlobals.BossCogDizzy:
            self.setDizzy(1)
            self.cleanupAttacks()
            self.doAnimate(None, raised=0, happy=1)
        elif attackCode == ToontownGlobals.BossCogAreaAttack:
            self.doAnimate('areaAttack', now=1)
            siren = base.loadSfx('phase_9/audio/sfx/CHQ_GOON_tractor_beam_alarmed.ogg')
            seq = Sequence(Func(self.setChatAbsolute, 'I told you Toons to get away from those cranes!', CFSpeech),
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
        self.resistanceToon.clearChat()
        self.stash()
        self.stopAnimate()
        self.controlToons()
        self.__showResistanceToon(False)
        self.resistanceToon.setPosHpr(*ToontownGlobals.CashbotBossBattleThreePosHpr)
        self.resistanceToon.loop('neutral')
        self.__arrangeToonsAroundResistanceToon()
        base.camera.reparentTo(render)
        base.camera.setPos(self.resistanceToon, -9, 12, 6)
        base.camera.lookAt(self.resistanceToon, 0, 0, 3)
        intervalName = 'EpilogueMovie'
        text = ResistanceChat.getChatText(self.rewardId)
        menuIndex, itemIndex = ResistanceChat.decodeId(self.rewardId)
        value = ResistanceChat.getItemValue(self.rewardId)
        if menuIndex == ResistanceChat.RESISTANCE_TOONUP:
            if value == -1:
                instructions = TTLocalizer.ResistanceToonToonupAllInstructions
            else:
                instructions = TTLocalizer.ResistanceToonToonupInstructions % value
        elif menuIndex == ResistanceChat.RESISTANCE_MONEY:
            if value == -1:
                instructions = TTLocalizer.ResistanceToonMoneyAllInstructions
            else:
                instructions = TTLocalizer.ResistanceToonMoneyInstructions % value
        elif menuIndex == ResistanceChat.RESISTANCE_RESTOCK:
            if value == -1:
                instructions = TTLocalizer.ResistanceToonRestockAllInstructions
            else:
                trackName = TTLocalizer.BattleGlobalTracks[value]
                instructions = TTLocalizer.ResistanceToonRestockInstructions % trackName
        speech = TTLocalizer.ResistanceToonCongratulations % (text, instructions)
        speech = self.__talkAboutPromotion(speech)
        self.resistanceToon.setLocalPageChat(speech, 0)
        self.accept('nextChatPage', self.__epilogueChatNext)
        self.accept('doneChatPage', self.__epilogueChatDone)
        base.playMusic(self.epilogueMusic, looping=1, volume=0.9)

    def __epilogueChatNext(self, pageNumber, elapsed):
        if pageNumber == 1:
            toon = self.resistanceToon
            playRate = 0.75
            track = Sequence(ActorInterval(toon, 'victory', playRate=playRate, startFrame=0, endFrame=9), ActorInterval(toon, 'victory', playRate=playRate, startFrame=9, endFrame=0), Func(self.resistanceToon.loop, 'neutral'))
            intervalName = 'EpilogueMovieToonAnim'
            self.storeInterval(track, intervalName)
            track.start()
        elif pageNumber == 3:
            self.d_applyReward()
            ResistanceChat.doEffect(self.rewardId, self.resistanceToon, self.involvedToons)

    def __epilogueChatDone(self, elapsed):
        self.resistanceToon.setChatAbsolute(TTLocalizer.CagedToonGoodbye, CFSpeech)
        self.ignore('nextChatPage')
        self.ignore('doneChatPage')
        intervalName = 'EpilogueMovieToonAnim'
        self.clearInterval(intervalName)
        track = Parallel(Sequence(ActorInterval(self.resistanceToon, 'wave'), Func(self.resistanceToon.loop, 'neutral')), Sequence(Wait(0.5), Func(self.localToonToSafeZone)))
        self.storeInterval(track, intervalName)
        track.start()

    def exitEpilogue(self):
        self.clearInterval('EpilogueMovieToonAnim')
        self.unstash()
        self.epilogueMusic.stop()

    def enterFrolic(self):
        DistributedBossCog.DistributedBossCog.enterFrolic(self)
        self.setPosHpr(*ToontownGlobals.CashbotBossBattleOnePosHpr)
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