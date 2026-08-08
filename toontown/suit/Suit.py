from direct.actor import Actor
import random
import math
from direct.directnotify import DirectNotifyGlobal
from otp.avatar import Avatar
from direct.interval.IntervalGlobal import *
from toontown.suit import SuitDNA
from toontown.battle import MovieUtil
from toontown.toonbase import ToontownGlobals
from pandac.PandaModules import *
from direct.interval.IntervalGlobal import *
from toontown.battle import BattleParticles
from direct.particles import ParticleEffect
from direct.showutil import Effects
from direct.showutil import Effects
from toontown.battle.BattleProps import *
from toontown.battle import SuitBattleGlobals
from toontown.nametag import NametagGlobals
from panda3d.core import TransparencyAttrib
from direct.interval.IntervalGlobal import Sequence, Func, LerpColorScaleInterval
from direct.task.Task import Task
from toontown.battle import BattleProps
from toontown.toonbase import TTLocalizer
from pandac.PandaModules import VirtualFileMountHTTP, VirtualFileSystem, Filename, DSearchPath
from direct.showbase import AppRunnerGlobal
from toontown.nametag import NametagGroup
from toontown.suit.SuitGenerator import SuitGenerator
from toontown.suit import SuitVoices
from toontown.suit import SuitAnimations
import string
import os
from toontown.suit import SuitGlobals
FreakoutTaskName = 'headPartFreakout'

HeadFreakoutWaitRange = (0.4, 2.0)
HeadFreakoutTwitchTimeRange = (0.07, 0.12)
HeadFreakoutAngleRange = [10, 25]

HeadFreakoutRepeatTimes = [1, 2, 3]
HeadFreakoutRepeatWeights = [6, 9, 7]
SUIT_STATUS_EFFECT_VISUALS = {
     'drenched': {
        'start': 'makeDrenched',
        'stop': 'cleanupDrenched',
    },
     'unionBusterNoAttack': {
          'start': 'makeNoAttack',
        'stop': 'makeUnNoAttack',
        'passModifier': True,
    },
    'soaked': {
        'start': 'makeSoaked',
        'stop': 'cleanupSoaked',
    },
    'overclocked': {
        'start': 'makeAfterImages',
        'stop': 'removeAfterImages',
        'passModifier': True,
    },
    'marketMeltdown': {
        'start': 'makeFireEffect',
        'stop': 'makeUnAngry',
        'passModifier': True,
    },
    'silhouetteImmune': {
        'start': 'makeImmortal',
        'stop': 'makeNonImmortal',
    },
    'zapped': {
        'start': 'makeZapped',
        'stop': 'cleanupShockAura',
    },
    'ambassadorTarget': {
        'start': 'makeTarget',
        'stop': 'makeUnTarget',
        'passModifier': True,
    },
    'immune': {
        'start': 'makeImmortal',
        'stop': 'makeNonImmortal',
        'passModifier': True,
    },
    'rushJob': {
        'start': 'makeRushJobArrow',
        'stop': 'cleanupRushJobArrow',
    },
     'vulnerable': {
        'start': 'makeVulnerable',
        'stop': 'makeUnVulnerable',
        'passModifier': True,
    },
     'brokenConnection': {
        'start': 'makeVulnerable',
        'stop': 'makeUnVulnerable',
        'passModifier': True,
    },
     'greenLight': {
        'start': 'makeGreenLight',
        'stop': 'makeUnGreenLight',
    },
     'redLight': {
        'start': 'makeRedLight',
        'stop': 'makeUnRedLight',
    },
     'enraged': {
        'start': 'makeFireEffect',
        'stop': 'makeUnAngry',
        'passModifier': True,
    },
     'protectionRacket': {
        'start': 'makeCollectCall',
    },
     'insured': {
        'start': 'makeInsured',
        'stop': 'removeInsured',
        'passModifier': True,
    },
     'insured2': {
        'start': 'makeInsured2',
        'stop': 'removeInsured',
        'passModifier': True,
    },
     'afterImage': {
        'start': 'makeAfterImages',
        'stop': 'removeAfterImages',
        'passModifier': True,
    },
     'oilRain': {
        'start': 'makeOilRain',
        'stop': 'cleanupOilRain',
        'passModifier': True,
    },
     'closedSession': {
        'start': 'makeBookkeeping',
        'stop': 'removeBookkeeping',
        'passModifier': True,
    },
    'extraAttacks': {
        'start': 'makeExtraAttacks',
        'stop': 'removeExtraAttacks',
    },
     'powerhouseGeneration': {
        'start': 'setVulnerability',
        'stop': 'makeUnVulnerable',
    },
}


if not base.config.GetBool('want-new-cogs', 0):
    ModelDict = {'a': ('/models/char/suitA-', 4),
     'b': ('/models/char/suitB-', 4),
     'c': ('/models/char/suitC-', 3.5)}
    TutorialModelDict = {'a': ('/models/char/suitA-', 4),
     'b': ('/models/char/suitB-', 4),
     'c': ('/models/char/suitC-', 3.5)}
else:
    ModelDict = {'a': ('/models/char/tt_a_ene_cga_', 4),
     'b': ('/models/char/tt_a_ene_cgb_', 4),
     'c': ('/models/char/tt_a_ene_cgc_', 3.5)}
    TutorialModelDict = {'a': ('/models/char/tt_a_ene_cga_', 4),
     'b': ('/models/char/tt_a_ene_cgb_', 4),
     'c': ('/models/char/tt_a_ene_cgc_', 3.5)}
HeadModelDict = {'a': ('/models/char/suitA-', 4),
 'b': ('/models/char/suitB-', 4),
 'c': ('/models/char/suitC-', 3.5)}

SuitParts = ['phase_3.5/models/char/suitA-mod',
            'phase_3.5/models/char/suitB-mod',
            'phase_3.5/models/char/suitC-mod',
            'phase_4/models/char/suitA-heads',
            'phase_4/models/char/suitB-heads',
            'phase_3.5/models/char/suitC-heads']

Preloaded = {}

def loadModels():
    global Preloaded
    if not Preloaded:
        print 'Preloading suits...'

        def preload(task):
            for filepath in SuitParts:
                Preloaded[filepath] = loader.loadModel(filepath)
                Preloaded[filepath].flattenMedium()

            return task.done

        taskMgr.add(preload, 'preload-suit')

def loadTutorialSuit():
    loader.loadModel('phase_3.5/models/char/suitC-mod')
    SuitVoices.loadDialog(1)

def loadSkelDialog():
    return SuitVoices.loadSkelDialog()

def unloadSkelDialog():
    return SuitVoices.unloadSkelDialog()

def loadSuits(level):
    SuitVoices.loadDialog(level)

def unloadSuits(level):
    loadSuitModelsAndAnims(level, flag=0)
    SuitVoices.unloadDialog(level)

def loadSuitModelsAndAnims(level, flag = 0):
    for key in ModelDict.keys():
        model, phase = ModelDict[key]
        if flag:
            filepath = 'phase_3.5' + model + 'mod'
            Preloaded[filepath] = loader.loadModel(filepath)
            filepath = 'phase_' + str(phase) + model + 'heads'
            Preloaded[filepath] = loader.loadModel(filepath)

def cogExists(filePrefix):
    searchPath = DSearchPath()
    if AppRunnerGlobal.appRunner:
        searchPath.appendDirectory(Filename.expandFrom('$TT_3_5_ROOT/phase_3.5'))
    else:
        basePath = os.path.expandvars('$TTMODELS') or './ttmodels'
        searchPath.appendDirectory(Filename.fromOsSpecific(basePath + '/built/phase_3.5'))
    filePrefix = filePrefix.strip('/')
    pfile = Filename(filePrefix)
    found = vfs.resolveFilename(pfile, searchPath)
    if not found:
        return False
    return True


def loadSuitAnims(suit, flag=1):
    return SuitAnimations.loadSuitAnims(
        suit,
        ModelDict,
        flag
    )

def attachSuitHead(node, suitName):
    suitIndex = SuitDNA.suitHeadTypes.index(suitName)
    suitDNA = SuitDNA.SuitDNA()
    suitDNA.newSuit(suitName)
    suit = Suit()
    suit.setDNA(suitDNA)
    headParts = suit.getHeadParts()
    animatedHeadParts = suit.getAnimatedHeadParts()
    head = node.attachNewNode('head')
    for part in headParts:
        copyPart = part.copyTo(head)
        copyPart.setDepthTest(1)
        copyPart.setDepthWrite(1)


    suit = None
    p1 = Point3()
    p2 = Point3()
    head.calcTightBounds(p1, p2)
    d = p2 - p1
    biggest = max(d[0], d[2])
    column = suitIndex % SuitDNA.suitsPerDept
    s = (0.2 + column / 100.0) / biggest
    pos = -0.14 + (SuitDNA.suitsPerDept - column - 1) / 135.0
    head.setPosHprScale(0, 0, pos, 180, 0, 0, s, s, s)
    return head


class Suit(Avatar.Avatar):
    notify = DirectNotifyGlobal.directNotify.newCategory('Suit')
    __module__ = __name__
    healthColors = (Vec4(0, 1, 0.078, 1),
                    Vec4(0.388, 1, 0, 1),
                    Vec4(0.686, 1, 0, 1),
                    Vec4(0.882, 1, 0, 1),
                    Vec4(0.988, 1, 0, 1),
                    Vec4(1, 0.831, 0, 1),
                    Vec4(1, 0.714, 0, 1),
                    Vec4(1, 0.533, 0, 1.0),
                    Vec4(1, 0, 0, 1),
                    Vec4(1, 0, 0, 1),
                    Vec4(0.3, 0.3, 0.3, 1), #out
                    Vec4(1, 0, 0, 1), #12
                    Vec4(0.0, 1.0, 1.0, 1),  # overheal
                    Vec4(0.553, 0, 1, 1),  # overcharge
                    Vec4(1, 0.6, 0.89, 1),  # 14 pink silhouette
                    Vec4(0, 0.361, 1, 1),
                    Vec4(1, 1, 1, 1),  # 15 blue silhouette
                    Vec4(186 / 255, 82 / 255, 1, 1),
                    Vec4(0.702, 0, 1, 1),
                    Vec4(1, 1, 1, 1),
                    Vec4(1, 0, 0.906, 1), #18
                    Vec4(0, 0.502, 0.502, 1), #19 teal
                    Vec4(0.827, 0.686, 0.216, 1)) # 20 gold
    healthGlowColors = (Vec4(0, 1, 0.078, 1),
                    Vec4(0.388, 1, 0, 1),
                    Vec4(0.686, 1, 0, 1),
                    Vec4(0.882, 1, 0, 1),
                    Vec4(0.988, 1, 0, 1),
                    Vec4(1, 0.831, 0, 1),
                    Vec4(1, 0.714, 0, 1),
                    Vec4(1, 0.533, 0, 1.0),
                    Vec4(1, 0, 0, 1),
                    Vec4(1, 0, 0, 1),
                    Vec4(0, 0, 0, 0), #out
                    Vec4(1, 0, 0, 1),
                    Vec4(0.0, 1.0, 1.0, 1),  # overheal
                    Vec4(0.553, 0, 1, 1),  # overcharge
                    Vec4(1, 0.6, 0.89, 1),  # 14 pink silhouette
                    Vec4(0, 0.361, 1, 1),
                    Vec4(1, 1, 1, 1),  # 15 blue silhouette
                    Vec4(186 / 255, 82 / 255, 1, 1),
                        Vec4(0.702, 0, 1, 1),
                        Vec4(1, 1, 1, 1),
                        Vec4(1, 0, 0.906, 1), 
                   Vec4(0, 0.502, 0.502, 1), #19 teal
                    Vec4(0.827, 0.686, 0.216, 1)
                        ) #18 white
    medallionColors = {'c': Vec4(0.863, 0.776, 0.769, 1.0),
     's': Vec4(0.843, 0.745, 0.745, 1.0),
     'l': Vec4(0.749, 0.776, 0.824, 1.0),
     'm': Vec4(0.749, 0.769, 0.749, 1.0),
     'g': Vec4(0.706, 0.773, 0.812, 1.0),
     't': Vec4(0.847, 0.792, 0.851, 1.0),
     'p': Vec4(0.643, 0.51, 0.525, 1.0)
                       }

    def __init__(self):
        try:
            self.Suit_initialized
            return
        except:
            self.Suit_initialized = 1

        Avatar.Avatar.__init__(self)
        self.setFont(ToontownGlobals.getSuitFont())
        self.setPlayerType(NametagGlobals.CCSuit)
        self.setPickable(1)
        self.leftHand = None
        self.rightHand = None
        self.shadowJoint = None
        self.splatCount = 0
        self.nametagJoint = None
        # self.headParts = []
        # self.animatedHeadParts = []
        self.healthBar = None
        self.healthBarDisplay = None
        self.healthCondition = 0
        self.isTrapped = 0
        self.isOverseer = 0
        self.overseerRounds = 0
        self.rpm = 10
        self.rpmIncrease = 0
        self.brain = None
        self.brainSeq = None
        self.battleSpeed = 0
        self.isKickback = 0
        self.isDisguised = 0
        self.isWaiter = 0
        self.isGovernaught = 0
        self.isInsured = 0
        self.insuranceRounds = 0
        self.isInsured2 = 0
        self.contractedRounds = 0
        self.isAmbassadorPhase3 = 0
        self.isContracted = 0
        self.isContracted2 = 0
        self.isExecutive = 0
        self.isSued = 0
        self.isAngry = 0
        self.isAlreadySleepy = 0
        self.isAlreadyExplosive = 0
        self.isRevived = 0
        self.isLaserRevived = 0
        self.isDanceSession = 0
        self.isImmortal = 0
        self.isSoakImmune = 0
        self.isMarkImmune = 0
        self.isSoundImmune = 0
        self.isZapImmune = 0
        self.isDropImmune = 0
        self.isShielding = 0
        self.trapRushJob = 0
        self.lureRushJob = 0
        self.throwRushJob = 0
        self.squirtRushJob = 0
        self.zapRushJob = 0
        self.soundRushJob = 0
        self.dropRushJob = 0
        self.isManager = 0
        self.isHeavyRain = 0
        self.isFreezingRain = 0
        self.isStormCell = 0
        self.oilRainRounds = 0
        self.isOilRain = 0
        self.isMonsoon = 0
        self.stormCellDamage = 60
        self.heavyRainDamage = 0
        self.isFrozen = 0
        self.isDeepFrozen = 0
        self.deepFrozenRounds = 0
        self.isSkelecogDialogue = 0
        self.isImmune = 0
        self.ripped = 0
        self.rippedMult = 0
        self.isDamageUp = 0
        self.damageDownMult = 0
        self.isDamageReduction = 0
        self.isDamageDown = 0
        self.isCollectCall = 0
        self.collectCallMult = 0
        self.isSoaked = 0
        self.isZapped = 0
        self.freshlyZapped = 0
        self.actuallySoaked = 0
        self.actuallyMarked = 0
        self.isSyphon = 0
        self.isVulnerable = 0
        self.isEnraged = 0
        self.isAbsorbing = 0
        self.isRental = 0
        self.isSleepy = 0
        self.isExplosive = 0
        self.isLureResist = 0
        self.isTarget = 0
        self.isGreenLight = 0
        self.isRedLight = 0
        self.suitStatusEffects = {}
        self.splats = set()

    def getModelDict(self):
        return ModelDict

    def delete(self):
        try:
            self.Suit_deleted
            return
        except:
            self.Suit_deleted = 1

        if self.leftHand:
            self.leftHand.removeNode()
            self.leftHand = None

        if self.rightHand:
            self.rightHand.removeNode()
            self.rightHand = None

        if self.shadowJoint:
            self.shadowJoint.removeNode()
            self.shadowJoint = None

        if self.nametagJoint:
            self.nametagJoint.removeNode()
            self.nametagJoint = None

        #for part in self.headParts:
            #part.removeNode()

        self.headParts = []
        self.animatedHeadParts = []
        self.removeHealthBar()
        self.removeHealthBarDisplay()
        Avatar.Avatar.delete(self)

    def getDialogueArray(self):
        return SuitVoices.getDialogueArray(self)

    def setHeight(self, height):
        Avatar.Avatar.setHeight(self, height)
        self.nametag3d.setPos(0, 0, height + 1.0)

    def getRadius(self):
        return 2

    def setDNAString(self, dnaString):
        self.dna = SuitDNA.SuitDNA()
        self.dna.makeFromNetString(dnaString)
        self.setDNA(self.dna)

    def setDNA(self, dna):
        if self.style:
            pass
        else:
            self.style = dna
            self.generateSuit()
            self.initializeDropShadow()
            self.initializeNametag3d()

    def generateSuit(self):
        SuitGenerator.generateSuit(self)

    def generateBody(self):
        animDict = self.generateAnimDict()
        filePrefix, bodyPhase = ModelDict[self.style.body]
        if base.config.GetBool('want-new-cogs', 0):
            if cogExists(filePrefix + 'zero.bam'):
                self.loadModel('phase_3.5' + filePrefix + 'zero')
            else:
                self.loadModel('phase_3.5' + filePrefix + 'mod')
        else:
            self.loadModel('phase_3.5' + filePrefix + 'mod')
        self.loadAnims(animDict)
        self.setSuitClothes()
        #if self.style.name == 'dsk' and not self.isSkeleton:
            #self.generateHead2('skeleskull_A')
            #self.generateSkeletonHands()
        #if self.style.name == 'blr' and not self.isSkeleton:
            #self.generateHead2('skeleskull_A')
            #self.generateSkeletonHands()
        self.setBlend(frameBlend=base.wantSmoothAnims)
        self.setLODAnimation(base.lodMaxRange, base.lodMinRange, base.lodDelayFactor)

    def generateSkeletonHands(self):
        animDict = self.generateAnimDict()
        filePrefix, bodyPhase = ModelDict[self.style.body]
        if base.config.GetBool('want-new-cogs', 0):
            if cogExists(filePrefix + 'zero.bam'):
                self.loadModel('phase_3.5/models/char/suitA_skeleton_hands-zero')
            else:
                self.loadModel('phase_3.5/models/char/suitA_skeleton_hands-zero')
        else:
            self.loadModel('phase_3.5/models/char/suitA_skeleton_hands-zero')
        self.loadAnims(animDict)
        self.setHandTexture()
        self.setBlend(frameBlend=base.wantSmoothAnims)
        self.setLODAnimation(base.lodMaxRange, base.lodMinRange, base.lodDelayFactor)

    def generateBodyHybrid(self):
        animDict = self.generateAnimDict()
        filePrefix, bodyPhase = ModelDict[self.style.body]
        if base.config.GetBool('want-new-cogs', 0):
            if cogExists(filePrefix + 'zero.bam'):
                self.loadModel('phase_3.5' + filePrefix + 'zero')
                self.loadModel('phase_5/models/char/cog' + string.upper(self.style.body) + '_robot-zero', 'skelehands')
            else:
                self.loadModel('phase_3.5' + filePrefix + 'mod')
                self.loadModel('phase_5/models/char/cog' + string.upper(self.style.body) + '_robot-zero', 'skelehands')
        else:
            self.loadModel('phase_3.5' + filePrefix + 'mod')
            self.loadModel('phase_5/models/char/cog' + string.upper(self.style.body) + '_robot-zero', 'skelehands')
        self.loadAnims(animDict)
        self.loadAnims(animDict, 'skelehands')
        self.setSuitClothesHybrid()
        self.find('**/hands').hide()
        self.setBlend(frameBlend=base.wantSmoothAnims)
        self.setLODAnimation(base.lodMaxRange, base.lodMinRange, base.lodDelayFactor)

    def generateSkeletonBody(self):
        animDict = self.generateAnimDict()
        filePrefix, bodyPhase = ModelDict[self.style.body]
        dept = self.style.dept
        for headPart in self.headParts:
            headPart.removeNode()
        self.headParts = []
        if base.config.GetBool('want-new-cogs', 0):
            if cogExists(filePrefix + 'zero.bam'):
                self.loadModel('phase_5/models/char/cog' + string.upper(self.style.body) + '_robot-zero')
            else:
                self.loadModel('phase_5/models/char/cog' + string.upper(self.style.body) + '_robot-zero')
        else:
            self.loadModel('phase_5/models/char/cog' + string.upper(self.style.body) + '_robot-zero')
        if self.style.body == 'a' and self.style.name == 'derrhand':
            self.generateHead3('derrickhand_skele', animated=True)
            texture = loader.loadTexture('phase_12/maps/ttcc_ene_derrickhand_skelecog.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
                headPart.setZ(0)
                headPart.setY(0)
                headPart.setX(0)
                headPart.setR(0)
                headPart.setH(0)
                headPart.setScale(1)
        if self.style.body == 'a' and self.style.name == 'dold':
            #self.generateDOLDHead()
            self.headParts = []
            self.generateHead3('dold', animated=True)
            texture = loader.loadTexture('phase_14/maps/ttcc_ene_dold_skelecog.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
            self.headParts = []
            self.generateHead3('skullA', animated=True)
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_dold.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
                headPart.setZ(0)
                headPart.setY(0)
                headPart.setX(0)
                headPart.setR(0)
                headPart.setH(0)
                headPart.setScale(1)
        if self.style.body == 'a' and self.style.name == 'radiog':
            self.generateHead3('dopa', animated=True)
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_radiog.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
                headPart.setZ(0)
                headPart.setY(0)
                headPart.setX(0)
                headPart.setR(0)
                headPart.setH(0)
                headPart.setScale(1.2)
        if self.style.body == 'a' and self.style.name == 'cdirector':
            self.generateHead3('chainsaw_c', animated=True)
            texture = loader.loadTexture('phase_12/maps/ttcc_ene_chainsaw_boardbot.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
                headPart.setZ(0)
                headPart.setY(0)
                headPart.setX(0)
                headPart.setR(0)
                headPart.setH(0)
                headPart.find('**/Hat').hide()
        if self.style.body == 'a' and self.style.name == 'autocad':
            self.generateHead3('autocaddie', animated=True)
            for headPart in self.headParts:
                headPart.setZ(0)
                headPart.setY(0)
                headPart.setX(0)
                headPart.setR(0)
                headPart.setH(0)
                headPart.setScale(1)
        if self.style.body == 'a' and self.style.name == 'clubpres':
            self.generateHead3('autocaddie', animated=True)
            #texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_c_exe.png')
            for headPart in self.headParts:
                headPart.setZ(0)
                headPart.setY(0)
                headPart.setX(0)
                headPart.setR(0)
                headPart.setH(0)
                headPart.setScale(1)
                #headModel.find('**/head').setTexture(texture, 1)
        if self.style.body == 'a' and self.style.name == 'ubuster':
            self.generateHead3('dopr', animated=True)
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_ubuster.png')
            for headPart in self.headParts:
                headPart.setZ(0)
                headPart.setTexture(texture, 1)
                headPart.setY(0)
                headPart.setX(0)
                headPart.setR(0)
                headPart.setH(0)
                headPart.setScale(1.3)
        if self.style.body == 'a' and self.style.name == 'ambass':
            self.generateHead3('prethinker2', animated=True)
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_ambassador.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
        if self.style.body == 'a' and not self.style.name == 'autocad' and not self.style.name == 'dold' and not self.style.name == 'ubuster' and not self.style.name == 'derrhand' and not self.style.name == 'ambass' and not self.style.name == 'cdirector' and not self.style.name == 'clubpres' and not self.style.name == 'radiog':
            self.generateHead3('skullA', animated=True)
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s.png' %
                                         self.style.dept)
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
                headPart.setZ(0)
                headPart.setY(0)
                headPart.setX(0)
                headPart.setR(0)
                headPart.setH(0)
                headPart.setScale(1)
        if self.style.body == 'b':
            self.generateHead3('skullB', animated=True)
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s.png' %
                                         self.style.dept)
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
                headPart.setZ(0)
                headPart.setY(0)
                headPart.setX(0)
                headPart.setR(0)
                headPart.setH(0)
                headPart.setScale(1)
        if self.style.body == 'c' and self.style.name == 'dopa':
            self.generateHead3('dopa', animated=True)
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_dopa.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
                headPart.setZ(0)
                headPart.setY(0)
                headPart.setX(0)
                headPart.setR(0)
                headPart.setH(0)
                headPart.setScale(1)
        if self.style.body == 'c' and self.style.name == 'dopr':
            self.generateHead3('dopr', animated=True)
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_dopr.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
                headPart.setZ(0)
                headPart.setY(0)
                headPart.setX(0)
                headPart.setR(0)
                headPart.setH(0)
                headPart.setScale(1)
        if self.style.body == 'c' and not self.style.name == 'dopa' and not self.style.name == 'dopr':
            self.generateHead3('skullC', animated=True)
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s.png' %
                self.style.dept)
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
                headPart.setZ(0)
                headPart.setY(0)
                headPart.setX(0)
                headPart.setR(0)
                headPart.setH(0)
                headPart.setScale(1)
        self.loadAnims(animDict)
        self.setSuitClothesSkeleton()
        self.setBlend(frameBlend=base.wantSmoothAnims)
        self.setLODAnimation(base.lodMaxRange, base.lodMinRange, base.lodDelayFactor)
        self.isSkeleton = 1

    def generateFemaleBody(self):
        animDict = self.generateAnimDict()
        filePrefix, bodyPhase = ModelDict[self.style.body]
        if base.config.GetBool('want-new-cogs', 0):
            if cogExists(filePrefix + 'zero.bam'):
                self.loadModel('phase_3.5' + filePrefix + 'zero')
            else:
                self.loadModel('phase_3.5' + filePrefix + 'f-mod')
        else:
            self.loadModel('phase_3.5' + filePrefix + 'f-mod')
        self.loadAnims(animDict)
        self.setSuitClothes()
        self.isFemale = 1
        self.isFemaleSkelecog = 1
        self.setLODAnimation(base.lodMaxRange, base.lodMinRange, base.lodDelayFactor)
        self.setBlend(frameBlend=base.wantSmoothAnims)

    def generateHighCollarBody(self):
        animDict = self.generateAnimDict()
        filePrefix, bodyPhase = ModelDict[self.style.body]
        if base.config.GetBool('want-new-cogs', 0):
            if cogExists(filePrefix + 'zero.bam'):
                self.loadModel('phase_3.5' + filePrefix + 'zero')
            else:
                self.loadModel('phase_3.5' + filePrefix + 'highcollar-mod')
        else:
            self.loadModel('phase_3.5' + filePrefix + 'highcollar-mod')
        self.loadAnims(animDict)
        self.setSuitClothes()
        self.setLODAnimation(base.lodMaxRange, base.lodMinRange, base.lodDelayFactor)
        self.setBlend(frameBlend=base.wantSmoothAnims)

    def generateCounterFitBody(self):
        animDict = self.generateAnimDict()
        filePrefix, bodyPhase = ModelDict[self.style.body]
        if base.config.GetBool('want-new-cogs', 0):
            if cogExists(filePrefix + 'zero.bam'):
                self.loadModel('phase_3.5' + filePrefix + 'zero')
            else:
                self.loadModel('phase_3.5' + filePrefix + 'erfit-mod')
        else:
            self.loadModel('phase_3.5' + filePrefix + 'erfit-mod')
        self.loadAnims(animDict)
        #self.setSuitClothes()
        self.find('**/hands').setColor(self.handColor)
        self.shadowJoint = self.find('**/joint_shadow')
        self.nametagJoint = self.find('**/joint_nameTag')
        self.leftHand = self.find('**/joint_Lhold')
        self.rightHand = self.find('**/joint_Rhold')
        self.isBuff = 1
        self.setLODAnimation(base.lodMaxRange, base.lodMinRange, base.lodDelayFactor)
        self.setBlend(frameBlend=base.wantSmoothAnims)

    def generateLongcoatBody(self):
        animDict = self.generateAnimDict()
        filePrefix, bodyPhase = ModelDict[self.style.body]
        if base.config.GetBool('want-new-cogs', 0):
            if cogExists(filePrefix + 'zero.bam'):
                self.loadModel('phase_3.5' + filePrefix + 'zero')
            else:
                self.loadModel('phase_3.5' + filePrefix + 'longcoat-mod')
        else:
            self.loadModel('phase_3.5' + filePrefix + 'longcoat-mod')
        self.loadAnims(animDict)
        self.setSuitClothesRaincoat()
        self.setLODAnimation(base.lodMaxRange, base.lodMinRange, base.lodDelayFactor)
        self.setBlend(frameBlend=base.wantSmoothAnims)

    def generateHighRollerBody(self):
        animDict = self.generateAnimDict()
        filePrefix, bodyPhase = ModelDict[self.style.body]
        if base.config.GetBool('want-new-cogs', 0):
            if cogExists(filePrefix + 'zero.bam'):
                self.loadModel('phase_3.5' + filePrefix + 'zero')
            else:
                self.loadModel('phase_3.5' + filePrefix + 'hroller-mod')
        else:
            self.loadModel('phase_3.5' + filePrefix + 'hroller-mod')
        self.loadAnims(animDict)
        self.setSuitClothesHighRoller()
        self.setLODAnimation(base.lodMaxRange, base.lodMinRange, base.lodDelayFactor)
        self.setBlend(frameBlend=base.wantSmoothAnims)

    def generateHighRollerBodyWhite(self):
        animDict = self.generateAnimDict()
        filePrefix, bodyPhase = ModelDict[self.style.body]
        if base.config.GetBool('want-new-cogs', 0):
            if cogExists(filePrefix + 'zero.bam'):
                self.loadModel('phase_3.5' + filePrefix + 'zero')
            else:
                self.loadModel('phase_3.5' + filePrefix + 'hroller-mod')
        else:
            self.loadModel('phase_3.5' + filePrefix + 'hroller-mod')
        self.loadAnims(animDict)
        self.setSuitClothesHighRollerWhite()
        self.setLODAnimation(base.lodMaxRange, base.lodMinRange, base.lodDelayFactor)
        self.setBlend(frameBlend=base.wantSmoothAnims)

    def generatePaceBody(self):
        animDict = self.generateAnimDict()
        filePrefix, bodyPhase = ModelDict[self.style.body]
        if base.config.GetBool('want-new-cogs', 0):
            if cogExists(filePrefix + 'zero.bam'):
                self.loadModel('phase_3.5' + filePrefix + 'zero')
            else:
                self.loadModel('phase_3.5' + filePrefix + 'open-mod')
        else:
            self.loadModel('phase_3.5' + filePrefix + 'open-mod')
        self.loadAnims(animDict)
        self.setSuitClothes()
        self.setLODAnimation(base.lodMaxRange, base.lodMinRange, base.lodDelayFactor)
        self.setBlend(frameBlend=base.wantSmoothAnims)

    def generateChainsawBody(self):
        animDict = self.generateAnimDict()
        filePrefix, bodyPhase = ModelDict[self.style.body]
        if base.config.GetBool('want-new-cogs', 0):
            if cogExists(filePrefix + 'zero.bam'):
                self.loadModel('phase_3.5' + filePrefix + 'zero')
            else:
                self.loadModel('phase_3.5' + filePrefix + 'chainsaw_hw-mod')
        else:
            self.loadModel('phase_3.5' + filePrefix + 'chainsaw_hw-mod')
        self.loadAnims(animDict)
        self.setSuitClothes()
        self.setLODAnimation(base.lodMaxRange, base.lodMinRange, base.lodDelayFactor)
        self.setBlend(frameBlend=base.wantSmoothAnims)

    def generateMajorPlayerBody(self):
        animDict = self.generateAnimDict()
        filePrefix, bodyPhase = ModelDict[self.style.body]
        if base.config.GetBool('want-new-cogs', 0):
            if cogExists(filePrefix + 'zero.bam'):
                self.loadModel('phase_3.5' + filePrefix + 'zero')
            else:
                self.loadModel('phase_3.5' + filePrefix + 'open-mod')
        else:
            self.loadModel('phase_3.5' + filePrefix + 'open-mod')
        self.loadAnims(animDict)
        self.setSuitClothes()
        self.setLODAnimation(base.lodMaxRange, base.lodMinRange, base.lodDelayFactor)
        self.setBlend(frameBlend=base.wantSmoothAnims)

    def generateAnimDict(self):
        animDict = {}

        filePrefix, bodyPhase = ModelDict[self.style.body]

        for anim in SuitAnimations.AllSuits:
            if anim[0] == 'sticker':
                animDict[anim[0]] = (
                    'phase_5/models/char/suit%s-sticker'
                    % self.style.body.upper()
                )
            else:
                animDict[anim[0]] = (
                    'phase_' + str(bodyPhase) +
                    filePrefix + anim[1]
                )

        for anim in SuitAnimations.AllSuitsMinigame:
            animDict[anim[0]] = (
                'phase_4' + filePrefix + anim[1]
            )

        # Use a separate prefix here so you do not overwrite
        # the normal model prefix used below.
        tutorialPrefix, tutorialBodyPhase = (
            TutorialModelDict[self.style.body]
        )

        for anim in SuitAnimations.AllSuitsTutorialBattle:
            animDict[anim[0]] = (
                'phase_' + str(tutorialBodyPhase) +
                tutorialPrefix + anim[1]
            )

        for anim in SuitAnimations.AllSuitsBattle:
            animDict[anim[0]] = (
                'phase_5' + filePrefix + anim[1]
            )

        if self.style.body == 'a':
            animDict['neutral'] = (
                'phase_4/models/char/suitA-neutral'
            )

            for anim in SuitAnimations.SuitsCEOBattle:
                animDict[anim[0]] = (
                    'phase_12/models/char/suitA-' + anim[1]
                )

        elif self.style.body == 'b':
            animDict['neutral'] = (
                'phase_4/models/char/suitB-neutral'
            )

            for anim in SuitAnimations.SuitsCEOBattle:
                animDict[anim[0]] = (
                    'phase_12/models/char/suitB-' + anim[1]
                )

        elif self.style.body == 'c':
            animDict['neutral'] = (
                'phase_3.5/models/char/suitC-neutral'
            )

            for anim in SuitAnimations.SuitsCEOBattle:
                animDict[anim[0]] = (
                    'phase_12/models/char/suitC-' + anim[1]
                )

        animList = SuitAnimations.getSuitAnimList(
            self.style.name
        )

        if not animList:
            self.notify.warning(
                'No custom animation list for suit %s'
                % self.style.name
            )

        for anim in animList:
            animName = anim[0]
            animFile = anim[1]

            # Most custom entries have a phase as item 2.
            if len(anim) >= 3:
                phase = 'phase_' + str(anim[2])
            else:
                phase = 'phase_' + str(bodyPhase)

            animDict[animName] = (
                phase + filePrefix + animFile
            )

        return animDict

    def initializeBodyCollisions(self, collIdStr):
        Avatar.Avatar.initializeBodyCollisions(self, collIdStr)
        if not self.ghostMode:
            self.collNode.setCollideMask(self.collNode.getIntoCollideMask() | ToontownGlobals.PieBitmask)

    def updateNametag(self):
        nameInfo = TTLocalizer.SuitBaseNameWithLevelHP % {'name': self.name,
                                                          'dept': self.getStyleDept(),
                                                          'level': self.getActualLevel(),
                                                          'currHP': self.currHP,
                                                          'maxHP': self.maxHP}
        self.setDisplayName(nameInfo)

    def setSuitClothes(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        dept = self.style.dept
        phase = 3.5
        texture3 = loader.loadTexture('phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
        texture2 = loader.loadTexture('phase_3.5/maps/ttcc_ene_suittex_%s.png' % self.style.dept)
        texture = loader.loadTexture('phase_3.5/maps/ttcc_ene_suittex_%s.png' % self.style.dept)
        if self.isExecutive and not self.style.name == 'ins' and not self.style.name == 'hroller' and not self.style.name == 'djockey':
            texture = loader.loadTexture('phase_3.5/maps/ttcc_ene_suittex_%s_e.png' % self.style.dept)
        elif self.isManager and not self.style.name == 'hroller2':
            texture = loader.loadTexture('phase_3.5/maps/ttcc_ene_suittex_%s_e.png' % self.style.dept)
        elif self.isExecutive and self.style.name == 'hroller':
            texture = loader.loadTexture('phase_12/maps/cc_t_ene_highroller_suit.png')
        elif self.isExecutive and self.style.name == 'djockey':
            texture = loader.loadTexture('phase_4/maps/schoolhouse/dummy/ttcc_ene_suittex_ptjockey_e.png')
        elif self.isGovernaught and not self.style.name == 'ins':
            texture = loader.loadTexture('phase_3.5/maps/ttcc_ene_suittex_%s_gov.png' % self.style.dept)
        elif not self.isGovernaught and not self.isExecutive and self.style.name == 'ins':
            texture = loader.loadTexture('phase_3.5/maps/ttcc_ene_suittex_highcollar_%s.png' % self.style.dept)
        elif self.isGovernaught and self.style.name == 'ins':
            texture = loader.loadTexture('phase_3.5/maps/ttcc_ene_suittex_highcollar_%s_gov.png' % self.style.dept)
        elif self.isExecutive and self.style.name == 'ins':
            texture = loader.loadTexture('phase_3.5/maps/ttcc_ene_suittex_highcollar_%s_e.png' % self.style.dept)
        #modelRoot.setTransparency(1)
        modelRoot.find('**/hands').setColor(self.handColor)
        modelRoot.find('**/necktie-s').hide()
        modelRoot.find('**/necktie-w').hide()
        modelRoot.find('**/bowtie').hide()
        modelRoot.find('**/necktie-s').setTexture(texture, 1)
        modelRoot.find('**/necktie-w').setTexture(texture, 1)
        if self.style.name == 'wsi':
            modelRoot.find('**/necktie-w').show()
            textureWSI = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s.png' % self.style.dept)
            modelRoot.find('**/necktie-w').setTexture(textureWSI, 1)
        if self.style.name == 'ovt':
            modelRoot.find('**/bowtie').show()
        modelRoot.find('**/bowtie').setTexture(texture, 1)
        if self.style.dept == 'l' and not self.style.name == 'wsi':
            modelRoot.find('**/bowtie').show()
        elif self.style.name == 'videog':
            texture2 = loader.loadTexture('phase_12/maps/ttcc_ene_suittex_videog.png')
            modelRoot.find('**/highroller_body').setTexture(texture2, 1)
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'mh2':
            texture2 = loader.loadTexture('phase_12/maps/ttcc_ene_suittex_hollywood.png')
            modelRoot.find('**/highroller_body').setTexture(texture2, 1)
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'std2':
            texture2 = loader.loadTexture('phase_12/maps/ttcc_ene_suittex_hollywood.png')
            modelRoot.find('**/highroller_body').setTexture(texture2, 1)
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'cnd2':
            texture2 = loader.loadTexture('phase_12/maps/ttcc_ene_suittex_candidate.png')
            modelRoot.find('**/highroller_body').setTexture(texture2, 1)
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'bcaster':
            texture2 = loader.loadTexture('phase_12/maps/ttcc_ene_suittex_bcaster.png')
            modelRoot.find('**/highroller_body').setTexture(texture2, 1)
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'fmaker':
            texture2 = loader.loadTexture('phase_12/maps/ttcc_ene_suittex_fmaker.png')
            modelRoot.find('**/highroller_body').setTexture(texture2, 1)
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'director':
            texture2 = loader.loadTexture('phase_12/maps/ttcc_ene_suittex_director.png')
            modelRoot.find('**/highroller_body').setTexture(texture2, 1)
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'cinema':
            texture2 = loader.loadTexture('phase_12/maps/ttcc_ene_suittex_cinema.png')
            modelRoot.find('**/highroller_body').setTexture(texture2, 1)
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'radiog':
            texture2 = loader.loadTexture('phase_12/maps/ttcc_ene_suittex_radiog.png')
            modelRoot.find('**/highroller_body').setTexture(texture2, 1)
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'choreo':
            texture2 = loader.loadTexture('phase_12/maps/ttcc_ene_suittex_choreo.png')
            modelRoot.find('**/highroller_body').setTexture(texture2, 1)
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'key':
            modelRoot.find('**/necktie-s').show()
        elif self.style.dept == 's':
            modelRoot.find('**/necktie-s').show()
        elif self.style.name == 'psetter' or self.style.name == 'hustle':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'hroller2':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'ins':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'redd':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'erclaim':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'hroller':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'mplayer':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'erfit':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'dking':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'ddiver':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'gatekeep' or self.style.name == 'liquidr':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'racket':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'wsi':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/bowtie').hide()
        elif self.style.name == 'ovt':
            modelRoot.find('**/bowtie').show()
        else:
            modelRoot.find('**/necktie-w').show()
        modelRoot.find('**/body').setTexture(texture, 1)
        self.shadowJoint = self.find('**/joint_shadow')
        self.nametagJoint = self.find('**/joint_nameTag')
        self.leftHand = self.find('**/joint_Lhold')
        self.rightHand = self.find('**/joint_Rhold')

    def setSuitClothesHybrid(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        dept = self.style.dept
        phase = 3.5
        texture = loader.loadTexture('phase_3.5/maps/ttcc_ene_suittex_%s.png' % self.style.dept)
        if self.isExecutive:
            texture = loader.loadTexture('phase_3.5/maps/ttcc_ene_suittex_%s_e.png' % self.style.dept)
        elif self.isGovernaught:
            texture = loader.loadTexture('phase_3.5/maps/ttcc_ene_suittex_%s_gov.png' % self.style.dept)
        modelRoot.find('**/hands').hide()
        modelRoot.find('**/necktie-s').hide()
        modelRoot.find('**/necktie-w').hide()
        modelRoot.find('**/bowtie').hide()
        modelRoot.find('**/necktie-s').setTexture(texture, 1)
        modelRoot.find('**/necktie-w').setTexture(texture, 1)
        modelRoot.find('**/bowtie').setTexture(texture, 1)
        if self.style.dept == 'l':
            modelRoot.find('**/bowtie').show()
        elif self.style.dept == 's':
            modelRoot.find('**/necktie-s').show()
        else:
            modelRoot.find('**/necktie-w').show()
        modelRoot.find('**/body').setTexture(texture, 1)
        self.shadowJoint = self.find('**/joint_shadow')
        self.nametagJoint = self.find('**/joint_nameTag')
        self.leftHand = self.find('**/joint_Lhold')
        self.rightHand = self.find('**/joint_Rhold')

    def setHandTexture(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        dept = self.style.dept
        phase = 3.5
        self.shadowJoint = self.find('**/joint_shadow')
        self.nametagJoint = self.find('**/joint_nameTag')
        self.leftHand = self.find('**/joint_Lhold')
        self.rightHand = self.find('**/joint_Rhold')

    def setSuitClothesHighRoller(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        dept = self.style.dept
        phase = 3.5
        texture = loader.loadTexture('phase_12/maps/cc_t_ene_highroller_suit_black.png')
        textureHighRollerBody = loader.loadTexture('phase_12/maps/cc_t_ene_highroller_body_black.png')
        modelRoot.find('**/hands').setColor(self.handColor)
        modelRoot.find('**/necktie-s').hide()
        modelRoot.find('**/necktie-w').hide()
        modelRoot.find('**/bowtie').hide()
        modelRoot.find('**/necktie-s').setTexture(texture, 1)
        modelRoot.find('**/necktie-w').setTexture(texture, 1)
        modelRoot.find('**/bowtie').setTexture(texture, 1)
        modelRoot.find('**/highroller_body').setTexture(textureHighRollerBody, 1)
        if self.style.dept == 'l':
            modelRoot.find('**/bowtie').show()
        elif self.style.dept == 's':
            modelRoot.find('**/necktie-s').show()
        elif self.style.name == 'psetter' or self.style.name == 'hustle':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'videog':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'bcaster':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'hroller':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'hroller2':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'hrollers':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'ins':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'erfit':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        else:
            modelRoot.find('**/necktie-w').show()
        modelRoot.find('**/body').setTexture(texture, 1)
        self.shadowJoint = self.find('**/joint_shadow')
        self.nametagJoint = self.find('**/joint_nameTag')
        self.leftHand = self.find('**/joint_Lhold')
        self.rightHand = self.find('**/joint_Rhold')

    def setSuitClothesRaincoat(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        dept = self.style.dept
        phase = 3.5
        texture = loader.loadTexture('phase_11/maps/ttcc_ene_suittex_rainmake.png')
        modelRoot.find('**/hands').setColor(self.handColor)
        modelRoot.find('**/necktie-s').hide()
        modelRoot.find('**/necktie-w').hide()
        modelRoot.find('**/bowtie').hide()
        modelRoot.find('**/necktie-s').setTexture(texture, 1)
        modelRoot.find('**/necktie-w').setTexture(texture, 1)
        modelRoot.find('**/bowtie').setTexture(texture, 1)
        if self.style.dept == 'l':
            modelRoot.find('**/bowtie').show()
        elif self.style.dept == 's' and not self.style.name == 'racket':
            modelRoot.find('**/necktie-s').show()
        # elif self.style.name == 'liquid':
        #     modelRoot.find('**/necktie-w').hide()
        #     modelRoot.find('**/bowtie').hide()
        #     modelRoot.find('**/necktie-s').hide()
        elif self.style.name == 'psetter' or self.style.name == 'hustle':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'videog':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'bcaster':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'hroller':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'hrollers':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'ins':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'ghd':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'racket':
            modelRoot.find('**/necktie-s').hide()
            modelRoot.find('**/necktie-w').hide()
        else:
            modelRoot.find('**/necktie-w').show()
        modelRoot.find('**/body').setTexture(texture, 1)
        self.shadowJoint = self.find('**/joint_shadow')
        self.nametagJoint = self.find('**/joint_nameTag')
        self.leftHand = self.find('**/joint_Lhold')
        self.rightHand = self.find('**/joint_Rhold')

    def setSuitClothesHighRollerWhite(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        dept = self.style.dept
        phase = 3.5
        texture = loader.loadTexture('phase_12/maps/cc_t_ene_highroller_suit.png')
        texture2 = loader.loadTexture('phase_12/maps/cc_t_ene_highroller_body.png')
        texture3 = loader.loadTexture('phase_12/maps/cc_t_ene_highroller_body3.png')
        texture4 = loader.loadTexture('phase_12/maps/cc_t_ene_highroller_body3.png')
        modelRoot.find('**/hands').setColor(self.handColor)
        modelRoot.find('**/necktie-s').hide()
        modelRoot.find('**/necktie-w').hide()
        modelRoot.find('**/bowtie').hide()
        modelRoot.find('**/necktie-s').setTexture(texture, 1)
        modelRoot.find('**/necktie-w').setTexture(texture, 1)
        modelRoot.find('**/bowtie').setTexture(texture, 1)
        if self.style.dept == 'l':
            modelRoot.find('**/bowtie').show()
        elif self.style.dept == 's':
            modelRoot.find('**/necktie-s').show()
        elif self.style.name == 'psetter' or self.style.name == 'hustle':
            modelRoot.find('**/necktie-s').hide()
        elif self.style.name == 'hrollers':
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'hroller':
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'hroller2':
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'erfit':
            modelRoot.find('**/necktie-w').hide()
        else:
            modelRoot.find('**/necktie-w').show()
        modelRoot.find('**/body').setTexture(texture, 1)
        modelRoot.find('**/highroller_body').setTexture(texture2, 1)
        self.shadowJoint = self.find('**/joint_shadow')
        self.nametagJoint = self.find('**/joint_nameTag')
        self.leftHand = self.find('**/joint_Lhold')
        self.rightHand = self.find('**/joint_Rhold')


    def setSuitClothesSkeleton(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        dept = self.style.dept
        phase = 3.5
        texture3 = loader.loadTexture('phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
        texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s.png' % self.style.dept)
        if self.isWaiter:
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_waiter.png')
        elif self.style.dept == 'c' and not self.isExecutive and not self.isManager and not self.isGovernaught and not self.isWaiter:
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s.png' % self.style.dept)
        elif self.isExecutive and not self.isWaiter or self.isManager:
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_exe.png' % self.style.dept)
        elif self.isManager and not self.style.name == 'charon' and not self.style.name == 'hydra'\
                and not self.style.name == 'radiog' and not self.style.name == 'kerberos' and not self.style.name == 'nix' and not self.style.name == 'ubuster' and not self.style.name == 'styx' and not self.isWaiter and not self.style.name == 'cdirector':
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_exe.png' % self.style.dept)
        elif self.isGovernaught and not self.isWaiter:
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_gov.png' % self.style.dept)
        modelRoot.find('**/necktie-s').hide()
        modelRoot.find('**/necktie-w').hide()
        modelRoot.find('**/bowtie').hide()
        modelRoot.find('**/necktie-s').setTexture(texture, 1)
        modelRoot.find('**/bowtie').setTexture(texture, 1)
        if self.style.name == 'wsi':
            textureWSI = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s.png' % self.style.dept)
            modelRoot.find('**/necktie-w').setTexture(textureWSI, 1)
        else:
            modelRoot.find('**/necktie-w').setTexture(texture, 1)
        if self.isWaiter:
            modelRoot.find('**/bowtie').show()
        elif self.style.dept == 'l' and not self.style.name == 'wsi':
            modelRoot.find('**/bowtie').show()
        elif self.style.dept == 's':
            modelRoot.find('**/necktie-s').show()
        elif self.style.name == 'wsi':
            modelRoot.find('**/bowtie').hide()
            modelRoot.find('**/necktie-w').show()
            textureWSI = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s.png' % self.style.dept)
            modelRoot.find('**/necktie-w').setTexture(textureWSI, 1)
        elif self.style.name == 'hydra':
            modelRoot.find('**/bowtie').show()
            modelRoot.setColor((0.729, 0.729, 0.729, 1))
            modelRoot.find('**/bowtie').setColor((0.741, 0.82, 0.769, 1))
        elif self.style.name == 'charon':
            modelRoot.find('**/necktie-w').hide()
            modelRoot.find('**/necktie-s').show()
            modelRoot.setColor((0.51, 0.49, 0.467, 1))
            modelRoot.find('**/necktie-s').setColor((0.741, 0.82, 0.769, 1))
        elif self.style.name == 'nix':
            modelRoot.find('**/necktie-w').show()
            modelRoot.setColor((0.6, 0.6, 0.6, 1))
            modelRoot.find('**/necktie-w').setColor((0.741, 0.82, 0.769, 1))
        elif self.style.name == 'styx':
            modelRoot.find('**/necktie-w').show()
            modelRoot.setColor((0.671, 0.671, 0.671, 1))
            modelRoot.find('**/necktie-w').setColor((0.741, 0.82, 0.769, 1))
        elif self.style.name == 'kerberos':
            modelRoot.find('**/necktie-w').show()
            modelRoot.setColor((0.62, 0.659, 0.624, 1))
            modelRoot.find('**/necktie-w').setColor((0.741, 0.82, 0.769, 1))
        elif self.style.name == 'rainmake':
            modelRoot.find('**/necktie-w').hide()
            modelRoot.find('**/bowtie').hide()
            modelRoot.find('**/necktie-s').hide()
        # elif self.style.name == 'liquid':
        #     modelRoot.find('**/necktie-w').hide()
        #     modelRoot.find('**/bowtie').hide()
        #     modelRoot.find('**/necktie-s').hide()
        elif self.style.name == 'racket':
            modelRoot.find('**/necktie-w').hide()
            modelRoot.find('**/bowtie').hide()
            modelRoot.find('**/necktie-s').hide()
        elif self.style.name == 'erfit':
            modelRoot.find('**/necktie-w').hide()
            modelRoot.find('**/bowtie').hide()
            modelRoot.find('**/necktie-s').hide()
        elif self.style.name == 'erclaim':
            modelRoot.find('**/necktie-w').hide()
            modelRoot.find('**/bowtie').hide()
            modelRoot.find('**/necktie-s').hide()
        elif self.style.name == 'hrollers':
            modelRoot.find('**/necktie-w').hide()
            modelRoot.find('**/bowtie').hide()
            modelRoot.find('**/necktie-s').hide()
        elif self.style.name == 'hroller2':
            modelRoot.find('**/necktie-w').hide()
            modelRoot.find('**/bowtie').hide()
            modelRoot.find('**/necktie-s').hide()
        elif self.style.name == 'hroller':
            modelRoot.find('**/necktie-w').hide()
            modelRoot.find('**/bowtie').hide()
            modelRoot.find('**/necktie-s').hide()
        elif self.style.name == 'bellring':
            modelRoot.find('**/necktie-w').hide()
            modelRoot.find('**/bowtie').hide()
            modelRoot.find('**/necktie-s').hide()
        elif self.style.name == 'psetter' or self.style.name == 'hustle':
            modelRoot.find('**/necktie-w').hide()
            modelRoot.find('**/bowtie').hide()
            modelRoot.find('**/necktie-s').hide()
        elif self.style.name == 'ins':
            modelRoot.find('**/necktie-w').hide()
            modelRoot.find('**/bowtie').hide()
            modelRoot.find('**/necktie-s').hide()
        elif self.style.name == 'dking':
            modelRoot.find('**/necktie-w').hide()
            modelRoot.find('**/bowtie').hide()
            modelRoot.find('**/necktie-s').hide()
        elif self.style.name == 'ddiver':
            modelRoot.find('**/necktie-w').hide()
            modelRoot.find('**/bowtie').hide()
            modelRoot.find('**/necktie-s').hide()
        elif self.style.name == 'gatekeep':
            modelRoot.find('**/necktie-w').hide()
            modelRoot.find('**/bowtie').hide()
            modelRoot.find('**/necktie-s').hide()
        elif self.style.name == 'wsi':
            modelRoot.find('**/bowtie').hide()
            modelRoot.find('**/necktie-s').hide()
        elif self.style.name == 'ovt':
            modelRoot.find('**/bowtie').show()
        else:
            modelRoot.find('**/necktie-w').show()
        modelRoot.find('**/body').setTexture(texture, 1)
        self.shadowJoint = self.find('**/joint_shadow')
        self.nametagJoint = self.find('**/joint_nameTag')
        self.leftHand = self.find('**/joint_Lhold')
        self.rightHand = self.find('**/joint_Rhold')

    def makeWaiter(self, modelRoot = None):
        if not modelRoot:
            modelRoot = self
        self.isWaiter = 1
        texture = loader.loadTexture('phase_12/maps/ttcc_ene_suittex_waiter.png')
        if self.isSkeleton:
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_waiter.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
        elif self.isExecutive:
            texture = loader.loadTexture('phase_12/maps/ttcc_ene_suittex_waiter_e.png')
        elif self.isGovernaught:
            texture = loader.loadTexture('phase_12/maps/ttcc_ene_suittex_waiter_gov.png')
        elif self.isManager:
            texture = loader.loadTexture('phase_3.5/maps/ttcc_ene_suittex_%s_e.png' % self.style.dept)
        if self.style.name == 'hho' and not self.isSkeleton and not self.isExecutive:
            texture2 = loader.loadTexture('phase_14/maps/cc_t_ene_headhoncho_waiter.png')
            for headPart in self.headParts:
                headPart.setTexture(texture2, 1)
        modelRoot.find('**/body').setTexture(texture, 1)
        modelRoot.find('**/necktie-s').hide()
        modelRoot.find('**/necktie-w').hide()
        modelRoot.find('**/bowtie').show()
        modelRoot.find('**/bowtie').setTexture(texture, 1)
        modelRoot.find('**/hands').setColor(0.835, 0.843, 0.847, 1)
        name = self.name
        dept = self.getStyleDept()
        level = str(self.getActualLevel())
        if self.getExecutive():
            level += TTLocalizer.ExecutivePostFix
        if self.getManager():
            level += TTLocalizer.ManagerPostFix
        if self.getGovernaught():
            level += TTLocalizer.GovernaughtPostFix
        if self.getSkeleRevives() > 0:
            level += TTLocalizer.SkeleRevivePostFix % (self.getSkeleRevives() + 1)
        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': name,
                                                        'dept': dept,
                                                        'level': level}
        self.setDisplayName(nameInfo)

    def makeWaiter2(self, modelRoot = None):
        if not modelRoot:
            modelRoot = self
        self.isWaiter = 1
        texture = loader.loadTexture('phase_12/maps/ttcc_ene_suittex_waiter.png')
        if self.isSkeleton:
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_waiter.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
        elif self.isExecutive:
            texture = loader.loadTexture('phase_12/maps/ttcc_ene_suittex_waiter_e.png')
        elif self.isGovernaught:
            texture = loader.loadTexture('phase_12/maps/ttcc_ene_suittex_waiter_gov.png')
        elif self.isManager:
            texture = loader.loadTexture('phase_12/maps/ttcc_ene_suittex_waiter_e.png')
        if self.style.name == 'hho' and not self.isSkeleton and not self.isExecutive:
            texture2 = loader.loadTexture('phase_14/maps/cc_t_ene_headhoncho_waiter.png')
            for headPart in self.headParts:
                headPart.setTexture(texture2, 1)
        modelRoot.find('**/body').setTexture(texture, 1)
        modelRoot.find('**/necktie-s').hide()
        modelRoot.find('**/necktie-w').hide()
        modelRoot.find('**/bowtie').show()
        modelRoot.find('**/bowtie').setTexture(texture, 1)
        modelRoot.find('**/hands').setColor(0.835, 0.843, 0.847, 1)

    def makeManagerSuit(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        texture = loader.loadTexture('phase_3.5/maps/ttcc_ene_suittex_%s_e.png' % self.style.dept)
        modelRoot.find('**/hands').setColor(self.handColor)
        modelRoot.find('**/necktie-s').hide()
        modelRoot.find('**/necktie-w').hide()
        modelRoot.find('**/bowtie').hide()
        modelRoot.find('**/necktie-s').setTexture(texture, 1)
        modelRoot.find('**/necktie-w').setTexture(texture, 1)
        modelRoot.find('**/bowtie').setTexture(texture, 1)
        if self.style.dept == 'l' and not self.style.name == 'redd' and not self.style.name == 'erclaim':
            modelRoot.find('**/bowtie').show()
        elif self.style.dept == 's' and not self.style.name == 'racket':
            modelRoot.find('**/necktie-s').show()
        elif self.style.name == 'psetter' or self.style.name == 'hustle':
            modelRoot.find('**/necktie-s').hide()
        elif self.style.name == 'redd':
            modelRoot.find('**/bowtie').hide()
        elif self.style.name == 'erclaim':
            modelRoot.find('**/bowtie').hide()
        elif self.style.name == 'hroller2':
            modelRoot.find('**/necktie-w').hide()
        elif self.style.name == 'racket':
            modelRoot.find('**/necktie-w').hide()
            modelRoot.find('**/necktie-s').hide()
        elif self.style.name == 'erfit':
            modelRoot.find('**/necktie-w').hide()
        else:
            modelRoot.find('**/necktie-w').show()
        modelRoot.find('**/body').setTexture(texture, 1)

    def makeRentalSuit(self, suitType, modelRoot = None):
        if not modelRoot:
            modelRoot = self.getGeomNode()
        if suitType == 's':
            torsoTex = loader.loadTexture('phase_3.5/maps/tt_t_ene_sellbotRental_blazer.jpg')
            legTex = loader.loadTexture('phase_3.5/maps/tt_t_ene_sellbotRental_leg.jpg')
            armTex = loader.loadTexture('phase_3.5/maps/tt_t_ene_sellbotRental_sleeve.jpg')
            handTex = loader.loadTexture('phase_3.5/maps/tt_t_ene_sellbotRental_hand.jpg')
        else:
            self.notify.warning('No rental suit for cog type %s' % suitType)
            return

        self.isRental = 1
        modelRoot.find('**/torso').setTexture(torsoTex, 1)
        modelRoot.find('**/arms').setTexture(armTex, 1)
        modelRoot.find('**/legs').setTexture(legTex, 1)
        modelRoot.find('**/hands').setTexture(handTex, 1)

    def generateHead3(self, headType, headColor=None, headTexture=None, modelOverride=None, pathOverride=None,
                     extraArgs={}, animated=False, additionalAnims=[]):
        if base.config.GetBool('want-new-cogs', False):
            filePrefix, phase = HeadModelDict[self.style.body]
        else:
            filePrefix, phase = ModelDict[self.style.body]
        '''if modelOverride:
            headModel = loader.loadModel(modelOverride)
        else:
            headModel = loader.loadModel('phase_' + str(phase) + filePrefix + 'heads')'''
        if animated:
            animDict = self.generateAnimDict()
            self.loadAnims(animDict)
            if headType == 'skelecog' or headType == 'overwhelmingauthorizer' or headType == 'executioner':
                if headType == 'overwhelmingauthorizer':
                    headModel = Actor.Actor('phase_14/models/char/ttcc_ene_%s%s-zero' % (
                    headType, '_exe' if self.isExecutive or self.isManager else ''))
                elif headType == 'executioner':
                    headModel = Actor.Actor('phase_14/models/char/ttcc_ene_executioner-zero')
                else:
                    headModel = Actor.Actor(
                        'phase_14/models/char/cog' + string.upper(self.style.body) + '_robot_head-zero')
                self.generateHeadAnims(
                    'phase_14/models/char/cog' + string.upper(self.style.body) + '_robot_head-',
                    headModel, additionalAnims)
                self.animatedHeadParts.append(headModel)
                if headType != 'overwhelmingauthorizer':
                    if headTexture:
                        try:
                            texture = loader.loadTexture('phase_5/maps/' + headTexture)
                        except:
                            texture = loader.loadTexture('phase_14/maps/' + headTexture)
                    else:
                        if self.style.dept == None:
                            texture = loader.loadTexture('phase_14/maps/ttcc_ene_skelecog_unemployed.png')
                        else:
                            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s%s.png' % (
                            self.style.dept, '_exe' if self.isExecutive or self.isManager else '',))
                    for headPart in self.animatedHeadParts:
                        headPart.setTexture(texture, 1)
            else:
                headModel = Actor.Actor('phase_14/models/char/ttcc_ene_' + headType + '-zero')
                self.generateHeadAnims('phase_14/models/char/ttcc_ene_' + headType + '-', headModel,
                                           additionalAnims)
                self.animatedHeadParts.append(headModel)
            headModel.reparentTo(self.find('**/joint_head'))
            headModel.setBlend(frameBlend=base.wantSmoothAnims)
            if self.headInterval != None:
                self.headInterval.finish()
                del self.headInterval
            self.headInterval = Sequence(Parallel(ActorInterval(headModel, 'neutral-hurt', endTime=0), ActorInterval(headModel, 'stun', endTime=0),
                                         ActorInterval(headModel, 'neutral-lured', endTime=0)
                                         , ActorInterval(headModel, 'murmur', endTime=0), ActorInterval(headModel, 'question', endTime=0),
                                         ActorInterval(headModel, 'statement', endTime=0),
                                         ActorInterval(headModel, 'grunt', endTime=0),
                                         ActorInterval(headModel, 'death', endTime=0)), Func(headModel.loop, 'neutral')).start()
            if 'x' in extraArgs:
                if extraArgs['x'] != None:
                    headModel.setX(extraArgs['x'])
            if 'y' in extraArgs:
                if extraArgs['y'] != None:
                    headModel.setY(extraArgs['y'])
            if 'z' in extraArgs:
                if extraArgs['z'] != None:
                    headModel.setZ(extraArgs['z'])
            if 'h' in extraArgs:
                if extraArgs['h'] != None:
                    headModel.setH(extraArgs['h'])
            if 'p' in extraArgs:
                if extraArgs['p'] != None:
                    headModel.setP(extraArgs['p'])
            if 'r' in extraArgs:
                if extraArgs['r'] != None:
                    headModel.setR(extraArgs['r'])
            if 'scale' in extraArgs:
                if extraArgs['scale'] != None:
                    headModel.setScale(*extraArgs['scale'])
            self.headParts.append(headModel)
            if headType == 'prethinker' and self.style.name == 'ambass':
                textureGlass = loader.loadTexture('phase_9/maps/ttcc_ene_prethinker_glass.png')
                headModel.find('**/glass').setTexture(textureGlass, 1)
                headModel.setScale(1)
                headModel.setZ(-.1)
                headModel.setY(-.1)
                self.brain = headModel.find('**/brain')
                self.setBrainPulseSpeed(1)
            if headType == 'prethinker' and self.style.name == 'prethink':
                self.brain = headModel.find('**/brain')
                self.setBrainPulseSpeed(1)
            if headType == 'prethinker2' and self.style.name == 'ambass':
                textureGlass = loader.loadTexture('phase_9/maps/ttcc_ene_prethinker_glass.png')
                headModel.find('**/glass').setTexture(textureGlass, 1)
                texture = loader.loadTexture('phase_9/maps/ttcc_ene_ambassador.png')
                headModel.setTexture(texture, 1)
                headModel.setScale(1)
                headModel.setZ(-.3)
                self.brain = headModel.find('**/brain')
                self.setBrainPulseSpeed(2)
            elif headType == 'molder':
                headModel.reparentTo(self.find('**/joint_head'))
                headModel.setScale(.7)
                headModel.setZ(-.4)
                headModel.setH(180)
            elif headType == 'shyster' and self.style.name == 'ang':
                textureGlass = loader.loadTexture('phase_11/maps/ttcc_ene_angelinvestor.png')
                headModel.setTexture(textureGlass, 1)
            elif headType == 'firestarter' and self.style.name == 'safesupervis':
                textureFire = loader.loadTexture('phase_12/maps/ttcc_ene_firestarter_fire_2.png')
                headModel.find('**/fire0').setTexture(textureFire, 1)
                headModel.find('**/fire1').setTexture(textureFire, 1)
                headModel.find('**/fire2').setTexture(textureFire, 1)
                headModel.find('**/fire3').setTexture(textureFire, 1)
                headModel.find('**/fire4').setTexture(textureFire, 1)
                headModel.find('**/fire5').setTexture(textureFire, 1)
                headModel.setScale(1)
                headModel.setZ(-.1)
            elif headType == 'firestarter':
                textureFire = loader.loadTexture('phase_12/maps/ttcc_ene_firestarter_fire.png')
                headModel.find('**/fire0').setTexture(textureFire, 1)
                headModel.find('**/fire1').setTexture(textureFire, 1)
                headModel.find('**/fire2').setTexture(textureFire, 1)
                headModel.find('**/fire3').setTexture(textureFire, 1)
                headModel.find('**/fire4').setTexture(textureFire, 1)
                headModel.find('**/fire5').setTexture(textureFire, 1)
                headModel.setScale(1)
                headModel.setZ(-.1)
            # elif headType == 'chairman-a' and not self.style.name == 'bookkeep':
            #     headModel.setScale(.7)
            #     headModel.setY(-.2)
            elif headType == 'magnate':
                headModel.setZ(-.1)
            elif headType == 'bagholder' and self.style.name == 'bgh' :
                headModel.setZ(.5)
            elif headType == 'paperhands' and self.style.name == 'pph' :
                headModel.setScale(.6)
            elif headType == 'paperhands' and self.style.name == 'bkeeper' :
                headModel.setScale(.7)
                headModel.setY(-.2)
                headModel.setZ(-.1)
            elif headType == 'deadlock' and self.style.name == 'dl':
                headModel.setZ(-.1)
            # elif headType == 'chairman' and not self.style.name == 'bookkeep':
            #     headModel.setScale(.7)
            #     headModel.setY(-.2)
            elif headType == 'chairman' and self.style.name == 'bookkeep':
                headModel.setScale(.85)
            elif headType == 'chairman-a' and self.style.name == 'bookkeep':
                headModel.setScale(.85)
            elif headType == 'highroller':
                headModel.setScale(1.2)
            elif self.style.name == 'director':
                #headModel.setZ(-.05)
                headModel.setY(-.2)
            elif self.style.name == 'mplayer':
                #headModel.setZ(-.05)
                headModel.setY(-.2)
            elif self.style.name == 'erclaim':
                #headModel.setZ(-.05)
                headModel.setZ(0.075)
            elif self.style.name == 'sgoat':
                headModel.setTwoSided(True)
            elif headType == 'clo':
                headModel.setZ(0)
                headModel.setY(.1)
                headModel.setX(0)
                headModel.setR(-90)
                headModel.setH(90)
                headModel.setScale(.4175)
            elif self.style.name == 'videog':
                headModel.setY(-.2)
            elif self.style.name == 'bcaster':
                headModel.setY(-.2)
            elif self.style.name == 'derrman':
                headModel.setY(-.1)
                headModel.setZ(-.2)
            elif headType == 'clubpresident' and not self.style.name == 'fmaker' and not self.style.name == 'director' and not self.style.name == 'choreo' and not self.style.name == 'cinema':
                headModel.setZ(-.1)
                headModel.setY(-.2)
            elif headType == 'mouthpiece' and self.style.name == 'wtapper':
                headModel.setScale(1.2)
                headModel.setZ(-.15)
                headModel.setY(-.15)
            elif headType == 'rainmaker':
                hair = None
                for stage in headModel.findAllTextureStages("*hair"):
                    headModel.setTexOffset(stage, 0, 0)
                    # 0 - inversion, 0.2 - heavy rain, 0.4 - oil rain, 0.6 - storm cell, 0.8 - fog
            elif headType == 'rainmaker2':
                hair = None
                for stage in headModel.findAllTextureStages("*hair"):
                    headModel.setTexOffset(stage, 0, 0.2)
                    # 0 - inversion, 0.2 - heavy rain, 0.4 - oil rain, 0.6 - storm cell, 0.8 - fog
            elif headType == 'rainmaker3':
                hair = None
                for stage in headModel.findAllTextureStages("*hair"):
                    headModel.setTexOffset(stage, 0, 0.8)
                    # 0 - inversion, 0.2 - heavy rain, 0.4 - oil rain, 0.6 - storm cell, 0.8 - fog
            elif headType == 'rainmaker4':
                hair = None
                for stage in headModel.findAllTextureStages("*hair"):
                    headModel.setTexOffset(stage, 0, 0.4)
                    # 0 - inversion, 0.2 - heavy rain, 0.4 - oil rain, 0.6 - storm cell, 0.8 - fog
            elif headType == 'rainmaker5':
                hair = None
                for stage in headModel.findAllTextureStages("*hair"):
                    headModel.setTexOffset(stage, 0, 0.6)
                    # 0 - inversion, 0.2 - heavy rain, 0.4 - oil rain, 0.6 - storm cell, 0.8 - fog
            elif headType == 'ceo':
                headModel.setZ(-.2)
                headModel.setY(-.2)
                headModel.setX(0)
                headModel.setR(-90)
                headModel.setH(90)
                headModel.setScale(.3)
            elif headType == 'ceo-a':
                headModel.setZ(-.2)
                headModel.setY(-.2)
                headModel.setX(0)
                headModel.setR(-90)
                headModel.setH(90)
                headModel.setScale(.3)
            elif headType == 'cfo':
                headModel.setZ(-.2)
                headModel.setY(-.2)
                headModel.setX(0)
                headModel.setR(-90)
                headModel.setH(90)
                headModel.setScale(.35)
                headModel.setTwoSided(True)
            elif headType == 'vp':
                headModel.setZ(-.2)
                headModel.setY(-.2)
                headModel.setX(0)
                headModel.setR(-90)
                headModel.setH(90)
                headModel.setScale(.35)
            elif headType == 'redd':
                headModel.setScale(.8)
            elif headType == 'witchhunter':
                headModel.setScale(1.3)
            elif headType == 'dola' and self.style.name == 'hustle':
                headModel.setZ(-.1)
                headModel.setY(-.1)
                headModel.setScale(1.1)
            elif headType == 'dopr' and self.style.name == 'ubuster' and not self.isSkeleton:
                headModel.setScale(1.3)
                headModel.setZ(.25)
                headModel.setY(-.2)
                texture = loader.loadTexture('phase_9/maps/ttcc_ene_ubuster.png')
                headModel.setTexture(texture, 1)
            elif headType == 'dopa' and self.style.name == 'radiog' and not self.isSkeleton:
                headModel.setScale(1.2)
                headModel.setZ(.25)
                headModel.setY(-.2)
                texture = loader.loadTexture('phase_9/maps/ttcc_ene_radiog.png')
                headModel.setTexture(texture, 1)
            elif headType == 'bellringer' and self.style.name == 'liquid':
                headModel.setScale(1.05)
                headModel.setZ(-0.15)
                headModel.setY(-.125)
            elif headType == 'boiler':
                headModel.setScale(.09)
                headModel.setZ(-.3)
                headModel.setY(-.2)
                headModel.setH(180)
            elif headType == 'animatronicStenographer':
                headModel.setH(180)
            elif headType == 'featherbedder':
                headModel.setScale(1)
                headModel.setZ(-.1)
            elif headType == 'treekiller':
                headModel.setZ(-.2)
            elif headType == 'derrickman':
                headModel.setScale(1)
                headModel.setZ(-.1)
                headModel.setY(-.1)
            elif headType == 'duckshuffler':
                headModel.setScale(1)
                headModel.setZ(-.1)
                headModel.setY(-.1)
            elif headType == 'chainsaw':
                #for stage in headModel.findAllTextureStages("*Chain"):
                    #headModel.setTexOffset(stage, 2, 2)
                headModel.find('**/Chain').setTwoSided(True)
                if self.isChainsawPhase3:
                    headModel.find('**/bulbLeft').hide()
            elif headType == 'prethinker':
                textureGlass = loader.loadTexture('phase_9/maps/ttcc_ene_prethinker_glass.png')
                headModel.find('**/glass').setTexture(textureGlass, 1)
            elif headType == 'autocaddie' and self.style.name == 'director':
                headModel.setZ(.25)
                headModel.setY(-.2)
                headModel.setColor(1, 1, 1, 1)
                textureGlass = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_p_exe.png')
                textureGlass2 = loader.loadTexture('phase_12/maps/cc_t_ene_ceo.png')
                headModel.find('**/head').setTexture(textureGlass, 1)
                headModel.setTexture(textureGlass2, 1)
            elif headType == 'autocaddie' and self.style.name == 'payman':
                headModel.setZ(.25)
                headModel.setY(-.2)
                headModel.setColor(1, 1, 1, 1)
                textureGlass = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_m_exe.png')
                textureGlass2 = loader.loadTexture('phase_12/maps/cc_t_ene_ceo.png')
                headModel.find('**/head').setTexture(textureGlass, 1)
                headModel.setTexture(textureGlass2, 1)
            elif headType == 'autocaddie' and self.style.name == 'fmaker':
                headModel.setZ(.25)
                headModel.setY(-.2)
                headModel.setColor(1, 1, 1, 1)
                textureGlass = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_g_exe.png')
                textureGlass2 = loader.loadTexture('phase_12/maps/cc_t_ene_ceo.png')
                headModel.find('**/head').setTexture(textureGlass, 1)
                headModel.setTexture(textureGlass2, 1)
            elif headType == 'autocaddie' and self.style.name == 'choreo':
                headModel.setZ(.25)
                headModel.setY(-.2)
                headModel.setColor(1, 1, 1, 1)
                textureGlass = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_c_exe.png')
                textureGlass2 = loader.loadTexture('phase_12/maps/cc_t_ene_ceo.png')
                headModel.find('**/head').setTexture(textureGlass, 1)
                headModel.setTexture(textureGlass2, 1)
            elif headType == 'autocaddie' and self.style.name == 'clubpres' and not self.isSkeleton:
                headModel.setZ(.25)
                headModel.setY(-.2)
            elif headType == 'plutocrat' and self.style.name == 'payman':
                headModel.setZ(-.1)
                headModel.setScale(0.85)
            elif headType == 'autocaddie' and self.style.name == 'cinema':
                headModel.setZ(.25)
                headModel.setY(-.2)
                headModel.setColor(1, 1, 1, 1)
                textureGlass = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_s_exe.png')
                textureGlass2 = loader.loadTexture('phase_12/maps/cc_t_ene_ceo.png')
                headModel.find('**/head').setTexture(textureGlass, 1)
                headModel.setTexture(textureGlass2, 1)
            elif headType == 'chainsaw_b':
                headModel.find('**/Chain').setTwoSided(True)
            elif headType == 'chainsaw_c':
                headModel.find('**/Chain').setTwoSided(True)
        else:
            if headType == 'skelecog':
                if base.config.GetBool('want-clash-assets', False):
                    headModel = loader.loadModel(
                        'phase_14/models/char/cog' + string.upper(self.style.body) + '_robot_head-zero')
                    headReferences = headModel.findAllMatches('**/skeleskull_' + string.upper(self.style.body))
                else:
                    headModel = loader.loadModel(
                        'phase_5/models/char/cog' + string.upper(self.style.body) + '_robot-head')
                    headReferences = headModel.findAllMatches('**/suit' + string.upper(self.style.body))
            else:
                if pathOverride:
                    headModel = loader.loadModel(pathOverride + headType)
                else:
                    if modelOverride:
                        headModel = loader.loadModel(modelOverride)
                        headReferences = headModel.findAllMatches('**/' + headType)
                    else:
                        try:
                            headModel = loader.loadModel('phase_' + str(phase) + '/models/char/' + headType)
                            headReferences = headModel.findAllMatches('**/' + headType + '.egg')
                        except:
                            headModel = loader.loadModel('phase_' + str(phase) + filePrefix + 'heads')
                            headReferences = headModel.findAllMatches('**/' + headType)
            if pathOverride:
                if headTexture:
                    pass
                if headColor:
                    headModel.setColor(headColor)
                if 'x' in extraArgs:
                    if extraArgs['x'] != None:
                        headModel.setX(extraArgs['x'])
                if 'y' in extraArgs:
                    if extraArgs['y'] != None:
                        headModel.setY(extraArgs['y'])
                if 'z' in extraArgs:
                    if extraArgs['z'] != None:
                        headModel.setZ(extraArgs['z'])
                if 'h' in extraArgs:
                    if extraArgs['h'] != None:
                        headModel.setH(extraArgs['h'])
                if 'p' in extraArgs:
                    if extraArgs['p'] != None:
                        headModel.setP(extraArgs['p'])
                if 'r' in extraArgs:
                    if extraArgs['r'] != None:
                        headModel.setR(extraArgs['r'])
                if 'scale' in extraArgs:
                    if extraArgs['scale'] != None:
                        headModel.setScale(*extraArgs['scale'])
                self.headParts.append(headModel)
            else:
                for i in range(0, headReferences.getNumPaths()):
                    if self.style.body == 'a' or self.style.body == 'b':
                        headPart = self.instance(headReferences.getPath(i), 'modelRoot', 'to_head')
                    else:
                        headPart = self.instance(headReferences.getPath(i), 'modelRoot', 'joint_head')
                    if headTexture:
                        try:
                            headTex = loader.loadTexture('phase_' + str(phase) + '/maps/' + headTexture)
                        except:
                            try:  # Will work on a more viable replacement for specific phases later.
                                headTex = loader.loadTexture('phase_5/maps/' + headTexture)
                            except:
                                try:
                                    headTex = loader.loadTexture('phase_11/maps/' + headTexture)
                                except:
                                    headTex = loader.loadTexture('phase_14/maps/' + headTexture)
                        headPart.setTexture(headTex, 1)
                    if headColor:
                        headPart.setColor(headColor)
                    if 'x' in extraArgs:
                        if extraArgs['x'] != None:
                            headPart.setX(extraArgs['x'])
                    if 'y' in extraArgs:
                        if extraArgs['y'] != None:
                            headPart.setY(extraArgs['y'])
                    if 'z' in extraArgs:
                        if extraArgs['z'] != None:
                            headPart.setZ(extraArgs['z'])
                    if 'h' in extraArgs:
                        if extraArgs['h'] != None:
                            headPart.setH(extraArgs['h'])
                    if 'p' in extraArgs:
                        if extraArgs['p'] != None:
                            headPart.setP(extraArgs['p'])
                    if 'r' in extraArgs:
                        if extraArgs['r'] != None:
                            headPart.setR(extraArgs['r'])
                    if 'scale' in extraArgs:
                        if extraArgs['scale'] != None:
                            headPart.setScale(*extraArgs['scale'])
                    if headType == 'suitA' or headType == 'suitB' or headType == 'suitC':
                        headPart.setZ(headPart.getZ() + {
                            'suitA': -6.05,
                            'suitB': -5.09477996826172,
                            'suitC': -4.15
                        }[headType])
                        if self.isExecutive or self.isManager:
                            if self.style.name == 'mbr':
                                headPart.setColor(VBase4(0.825, 0.6, 0.425, 1.0))
                            else:
                                if headColor == None:
                                    headPart.setColor({
                                                          'c': SuitDNA.corpPolyColor,
                                                          'l': SuitDNA.legalPolyColor,
                                                          'm': SuitDNA.moneyPolyColor,
                                                          's': SuitDNA.salesPolyColor,
                                                          'g': SuitDNA.boardPolyColor,
                                                          None: VBase4(0.5, 0.5, 0.5, 1.0)
                                                      }[SuitDNA.getSuitDept(self.style.name)])
                        else:
                            if self.style.name == 'mbr':
                                headPart.setColor(VBase4(1.0, 0.25, 0.0, 1.0))
                    self.headParts.append(headPart)
                headModel.removeNode()

    def setBrainPulseSpeed(self, speed=1.0):
        durationA = 0.8
        durationB = 0.3
        scaleTop = 1.00
        scaleLow = 0.96
    
        scaleShrink = 0.14
        durationShrink = 4.0
        self.cleanupBrainSeq()
        speedMultiplier = 1.0 / float(speed)
        self.brainSeq = Sequence(
            LerpScaleInterval(self.brain, durationB * speedMultiplier, startScale=scaleTop, scale=scaleLow, blendType='easeOut'),
            LerpScaleInterval(self.brain, durationB * speedMultiplier, startScale=scaleTop, scale=scaleLow, blendType='easeOut'),
            Wait(durationA * speedMultiplier))
        
        self.brainSeq.loop()

    def cleanupBrainSeq(self):
        if self.brainSeq:
            self.brainSeq.finish()
            self.brainSeq = None

    def generateHead(self, headType, headColor=None, headTexture=None, modelOverride=None, pathOverride=None,
                     extraArgs={}, animated=False, additionalAnims=[]):
        self.isSkeleton = 0
        self.isGovernaught = 0
        self.isManager = 0
        self.isExecutive = 0
        if base.config.GetBool('want-new-cogs', False):
            filePrefix, phase = HeadModelDict[self.style.body]
        else:
            filePrefix, phase = ModelDict[self.style.body]
        '''if modelOverride:
            headModel = loader.loadModel(modelOverride)
        else:
            headModel = loader.loadModel('phase_' + str(phase) + filePrefix + 'heads')'''
        if animated:
            if headType == 'skullA' or headType == 'skullB' or headType == 'skullC':
                if headType == 'skullC' or headType == 'skullA' or headType == 'skullB':
                    headModel = Actor.Actor('phase_14/models/char/ttcc_ene_%s-zero.bam' %
                        headType)
                else:
                    headModel = Actor.Actor(
                        'phase_14/models/char/' + string.upper(self.style.body) + '-zero')
                self.generateHeadAnims(
                    'phase_14/models/char/ttcc_ene_skull' + string.upper(self.style.body) + '-',
                    headModel, additionalAnims)
                self.headParts.append(headModel)
                if headTexture:
                    try:
                        texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s%s.png' % (
                                self.style.dept, '_exe' if self.isExecutive or self.isManager else '',))
                    except:
                        texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_unemployed.png')
                else:
                    if self.style.dept == None:
                        texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_unemployed.png')
                    else:
                        texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s%s.png' % (
                                self.style.dept, '_exe' if self.isExecutive or self.isManager else '',))
                for headPart in self.headParts:
                    #texture.setMinfilter(Texture.FTNearestMipmapLinear)
                    #texture.setMagfilter(Texture.FTNearest)
                    headPart.setTexture(texture, 1)
            elif headType == 'insider':
                if headTexture:
                    try:
                        texture = loader.loadTexture('phase_14/maps/cc_t_ene_insider%s.png' % ('_exe' if self.isExecutive or self.isGovernaught else '',))
                    except:
                        texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_unemployed.png')
                else:
                    try:
                        texture = loader.loadTexture('phase_14/maps/cc_t_ene_insider%s.png' % ('_exe' if self.isExecutive or self.isGovernaught else '',))
                    except:
                        texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_unemployed.png')
                for headPart in self.headParts:
                    headPart.setTexture(texture, 1)

            else:
                headModel = Actor.Actor('phase_14/models/char/ttcc_ene_' + headType + '-zero')
                self.generateHeadAnims('phase_14/models/char/ttcc_ene_' + headType + '-', headModel,
                                       additionalAnims)
                self.headParts.append(headModel)
            headModel.reparentTo(self.find('**/joint_head'))
            headModel.setBlend(frameBlend=base.wantSmoothAnims)
            headModel.loop('neutral')
            if 'x' in extraArgs:
                if extraArgs['x'] != None:
                    headModel.setX(extraArgs['x'])
            if 'y' in extraArgs:
                if extraArgs['y'] != None:
                    headModel.setY(extraArgs['y'])
            if 'z' in extraArgs:
                if extraArgs['z'] != None:
                    headModel.setZ(extraArgs['z'])
            if 'h' in extraArgs:
                if extraArgs['h'] != None:
                    headModel.setH(extraArgs['h'])
            if 'p' in extraArgs:
                if extraArgs['p'] != None:
                    headModel.setP(extraArgs['p'])
            if 'r' in extraArgs:
                if extraArgs['r'] != None:
                    headModel.setR(extraArgs['r'])
            if 'scale' in extraArgs:
                if extraArgs['scale'] != None:
                    headModel.setScale(*extraArgs['scale'])
            self.headParts.append(headModel)
            if headType == 'prethinker' and self.style.name == 'gtk':
                headModel.setScale(1)
                headModel.setZ(-.1)
            elif headType == 'molder':
                headModel.reparentTo(self.find('**/joint_head'))
                headModel.setScale(.7)
                headModel.setZ(-.4)
                headModel.setH(180)
            elif headType == 'chairman-a':
                headModel.setScale(.7)
                headModel.setY(-.2)
            elif headType == 'magnate' and self.style.name == 'rng' :
                headModel.setZ(-.1)
            elif headType == 'magnate' and self.style.name == 'jgd' :
                headModel.setZ(-.1)
            elif headType == 'magnate' and self.style.name == 'tlr' :
                headModel.setZ(-.1)
            elif headType == 'bagholder' and self.style.name == 'ca' :
                headModel.setZ(.5)
            elif headType == 'paperhands' and self.style.name == 'cn' :
                headModel.setScale(.6)
            elif headType == 'paperhands' and self.style.name == 'bkeeper' :
                headModel.setScale(.7)
                headModel.setY(-.2)
                headModel.setZ(-.1)
            elif headType == 'deadlock' and self.style.name == 'hho':
                headModel.setZ(-.1)
            elif headType == 'sharkwatcher' and self.style.name == 'ffm':
                headModel.setY(-.1)
            elif headType == 'chairman':
                headModel.setScale(.7)
                headModel.setY(-.2)
            elif headType == 'highroller':
                headModel.setScale(1.2)
            elif self.style.name == 'tb':
                headModel.setZ(-.05)
                headModel.setY(-.3)
            elif self.style.name == 'ts':
                headModel.setZ(-.05)
                headModel.setY(-.3)
            elif headType == 'clo':
                headModel.setZ(-.05)
                headModel.setY(-.05)
                headModel.setX(0)
                headModel.setR(-90)
                headModel.setH(90)
                headModel.setScale(.325)
            elif headType == 'ceo':
                headModel.setZ(-.1)
                headModel.setY(-.1)
                headModel.setX(0)
                headModel.setR(-90)
                headModel.setH(90)
                headModel.setScale(.4)
            elif headType == 'ceo-a':
                headModel.setZ(-.1)
                headModel.setY(-.1)
                headModel.setX(0)
                headModel.setR(-90)
                headModel.setH(90)
                headModel.setScale(.4)
            elif headType == 'cfo':
                headModel.setZ(-.1)
                headModel.setY(-.1)
                headModel.setX(0)
                headModel.setR(-90)
                headModel.setH(90)
                headModel.setScale(.4)
            elif headType == 'vp':
                headModel.setZ(-.1)
                headModel.setY(-.1)
                headModel.setX(0)
                headModel.setR(-90)
                headModel.setH(90)
                headModel.setScale(.4)
            elif self.style.name == 'prr':
                headModel.setY(-.2)
            elif headType == 'clubpresident':
                headModel.setZ(-.1)
                headModel.setY(-.2)
            elif headType == 'mouthpiece' and self.style.name == 'frs':
                headModel.setScale(1.2)
                headModel.setZ(-.15)
                headModel.setY(-.15)
            elif headType == 'plutocrat' and self.style.name == 'auh':
                headModel.setScale(.85)
                headModel.setZ(-.1)
                headModel.setY(-.1)
            elif headType == 'advocate' and self.style.name == 'bdb':
                headModel.setScale(1.05)
                headModel.setZ(-.1)
                headModel.setY(-.2)
                headModel.setY(0)
            elif headType == 'redd':
                headModel.setScale(.8)
            elif headType == 'witchhunter':
                headModel.setScale(1.3)
            elif headType == 'multislacker' and self.style.name == 'blr':
                headModel.setZ(-.1)
                headModel.setY(-.1)
            elif headType == 'dola' and self.style.name == 'cp':
                headModel.setZ(-.1)
                headModel.setY(-.1)
            elif headType == 'judy':
                headModel.setScale(1.05)
                headModel.setZ(-.1)
                headModel.setY(-.1)
            elif headType == 'dopr' and self.style.name == 'dsk' and not self.isSkeleton:
                headModel.setScale(1.3)
            elif headType == 'dopa' and self.style.name == 'blr' and not self.isSkeleton:
                headModel.setScale(1.2)
            elif headType == 'boiler':
                headModel.setScale(.09)
                headModel.setZ(-.3)
                headModel.setY(-.2)
                headModel.setH(180)
            elif headType == 'needlenose' and self.style.name == 'dfh':
                headModel.setScale(1.05)
                headModel.setZ(-.1)
                headModel.setY(-.1)
            elif headType == 'featherbedder':
                headModel.setScale(1)
                headModel.setZ(-.1)
            elif headType == 'treekiller':
                headModel.setZ(-.2)
            elif headType == 'derrickman':
                headModel.setScale(1)
                headModel.setZ(-.1)
                headModel.setY(-.1)
            elif headType == 'backstabber':
                headModel.setScale(1.1)
                headModel.setZ(-.1)
                headModel.setY(-.1)
            elif headType == 'duckshuffler':
                headModel.setScale(1)
                headModel.setZ(-.1)
                headModel.setY(-.1)
            elif headType == 'chainsaw':
                headModel.find('**/Chain').setTwoSided(True)
            elif headType == 'chainsaw_b':
                headModel.find('**/Chain').setTwoSided(True)
            elif headType == 'chainsaw_c':
                headModel.find('**/Chain').setTwoSided(True)
        else:
            if headType == 'skelecog':
                if base.config.GetBool('want-clash-assets', True):
                    headModel = loader.loadModel(
                        'phase_14/models/char/' + string.upper(self.style.body) + '_robot_head-zero')
                    headReferences = headModel.findAllMatches('**/skeleskull_' + string.upper(self.style.body))
                else:
                    headModel = loader.loadModel(
                        'phase_5/models/char/cog' + string.upper(self.style.body) + '_robot-head')
                    headReferences = headModel.findAllMatches('**/suit' + string.upper(self.style.body))
            else:
                if pathOverride:
                    headModel = loader.loadModel(pathOverride + headType)
                else:
                    if modelOverride:
                        headModel = loader.loadModel(modelOverride)
                        headReferences = headModel.findAllMatches('**/' + headType)
                    else:
                        try:
                            headModel = loader.loadModel('phase_' + str(phase) + '/models/char/' + headType)
                            headReferences = headModel.findAllMatches('**/' + headType + '.bam')
                        except:
                            headModel = loader.loadModel('phase_' + str(phase) + filePrefix + 'heads')
                            headReferences = headModel.findAllMatches('**/' + headType)
            if pathOverride:
                if headTexture:
                    pass
                if headColor:
                    headModel.setColor(headColor)
                if 'x' in extraArgs:
                    if extraArgs['x'] != None:
                        headModel.setX(extraArgs['x'])
                if 'y' in extraArgs:
                    if extraArgs['y'] != None:
                        headModel.setY(extraArgs['y'])
                if 'z' in extraArgs:
                    if extraArgs['z'] != None:
                        headModel.setZ(extraArgs['z'])
                if 'h' in extraArgs:
                    if extraArgs['h'] != None:
                        headModel.setH(extraArgs['h'])
                if 'p' in extraArgs:
                    if extraArgs['p'] != None:
                        headModel.setP(extraArgs['p'])
                if 'r' in extraArgs:
                    if extraArgs['r'] != None:
                        headModel.setR(extraArgs['r'])
                if 'scale' in extraArgs:
                    if extraArgs['scale'] != None:
                        headModel.setScale(*extraArgs['scale'])
                self.headParts.append(headModel)
            else:
                for i in range(0, headReferences.getNumPaths()):
                    if self.style.body == 'a' or self.style.body == 'b':
                        headPart = self.instance(headReferences.getPath(i), 'modelRoot', 'joint_head')
                    else:
                        headPart = self.instance(headReferences.getPath(i), 'modelRoot', 'joint_head')
                    if self.headTexture:
                        try:
                            headTex = loader.loadTexture('phase_' + str(phase) + '/maps/' + headTexture)
                        except:
                            try:  # Will work on a more viable replacement for specific phases later.
                                headTex = loader.loadTexture('phase_5/maps/' + headTexture)
                            except:
                                try:
                                    headTex = loader.loadTexture('phase_11/maps/' + headTexture)
                                except:
                                    headTex = loader.loadTexture('phase_14/maps/' + headTexture)
                        #headTex.setMinfilter(Texture.FTLinearMipmapLinear)
                        #headTex.setMagfilter(Texture.FTLinear)
                        headPart.setTexture(headTex, 1)
                    if headColor:
                        headPart.setColor(headColor)
                    if 'x' in extraArgs:
                        if extraArgs['x'] != None:
                            headPart.setX(extraArgs['x'])
                    if 'y' in extraArgs:
                        if extraArgs['y'] != None:
                            headPart.setY(extraArgs['y'])
                    if 'z' in extraArgs:
                        if extraArgs['z'] != None:
                            headPart.setZ(extraArgs['z'])
                    if 'h' in extraArgs:
                        if extraArgs['h'] != None:
                            headPart.setH(extraArgs['h'])
                    if 'p' in extraArgs:
                        if extraArgs['p'] != None:
                            headPart.setP(extraArgs['p'])
                    if 'r' in extraArgs:
                        if extraArgs['r'] != None:
                            headPart.setR(extraArgs['r'])
                    if 'scale' in extraArgs:
                        if extraArgs['scale'] != None:
                            headPart.setScale(*extraArgs['scale'])
                    if headType == 'suitA' or headType == 'suitB' or headType == 'suitC':
                        headPart.setZ(headPart.getZ() + {
                            'suitA': -6.05,
                            'suitB': -5.09477996826172,
                            'suitC': -4.15
                        }[headType])
                        if self.isExecutive or self.isManager:
                            if self.style.name == 'mbr':
                                headPart.setColor(VBase4(0.825, 0.6, 0.425, 1.0))
                            else:
                                if headColor == None:
                                    headPart.setColor({
                                                          'c': SuitDNA.corpPolyColor,
                                                          'l': SuitDNA.legalPolyColor,
                                                          'm': SuitDNA.moneyPolyColor,
                                                          's': SuitDNA.salesPolyColor,
                                                          'g': SuitDNA.boardPolyColor,
                                                          None: VBase4(0.5, 0.5, 0.5, 1.0)
                                                      }[SuitDNA.getSuitDept(self.style.name)])
                        else:
                            if self.style.name == 'mbr':
                                headPart.setColor(VBase4(1.0, 0.25, 0.0, 1.0)
                                                  )
                    self.headParts.append(headPart)
                headModel.removeNode()

    def makeMouthDrop(self):
        for headPart in self.animatedHeadParts:
            headPart.play('bellow')

    def generateHead2(self, headType):
        filePrefix, phase = ModelDict[self.style.body]
        headModel = loader.loadModel('phase_' + str(phase) + filePrefix + 'heads')
        if headType == 'barrister' and self.style.body == 'a':
                headModel = loader.loadModel('phase_4/models/char/suitB-heads')
        if headType == 'loanshark' and self.style.body == 'a':
                headModel = loader.loadModel('phase_4/models/char/suitB-heads')
        if headType == 'beancounter' and self.style.body == 'a':
                headModel = loader.loadModel('phase_4/models/char/suitB-heads')
        if headType == 'telemarketer' and self.style.body == 'a':
                headModel = loader.loadModel('phase_4/models/char/suitB-heads')
        if headType == 'scopejp187187' and self.style.body == 'a':
                headModel = loader.loadModel('phase_4/models/char/suitB-heads')
        if headType == 'bandjp187187' and self.style.body == 'a':
                headModel = loader.loadModel('phase_4/models/char/suitB-heads')
        if headType == 'hatjp187187' and self.style.body == 'a':
                headModel = loader.loadModel('phase_4/models/char/suitB-heads')
        if headType == 'bigfish' and self.style.name == 'bfh2':
                headModel = loader.loadModel('phase_14/models/char/ttcc_ene_bigfish-zero')
        if headType == 'flunky' and self.style.body == 'a':
                headModel = loader.loadModel('phase_3.5/models/char/suitC-heads')
        if headType == 'beret' and self.style.body == 'a':
                headModel = loader.loadModel('phase_3.5/models/char/suitC-heads')
        if headType == 'pushover' and self.style.name == 'psh':
            headModel = loader.loadModel('phase_3.5/models/char/bricks-pushover')
        if headType == 'goldbricks':
            headModel = loader.loadModel('phase_3.5/models/char/bricks-pushover')
        if headType == 'root' and self.style.name == 'oilg':
            headModel = loader.loadModel('phase_14/models/char/yesman')
        if headType == 'Change Agent head':
            headModel = loader.loadModel('phase_14/models/char/change-agent')
        if headType == 'root_user':
            headModel = loader.loadModel('phase_14/models/char/root-user_head')
        if headType == 'voodoo':
            headModel = loader.loadModel('phase_14/models/char/voodoo-programmer_head')
        if headType == 'root' and self.style.name == 'whistleb':
            headModel = loader.loadModel('phase_14/models/char/whistleblower')
        if headType == 'root' and self.style.name == 'ksp':
            headModel = loader.loadModel('phase_14/models/char/mingler')
        if headType == 'root' and self.style.name == 'ppl':
            headModel = loader.loadModel('phase_14/models/char/tf_new')
        if headType == 'root' and self.style.name == 'stck':
            headModel = loader.loadModel('phase_14/models/char/stickler')
        if headType == 'root' and self.style.name == 'lvw':
            headModel = loader.loadModel('phase_3.5/models/char/livewire')
        if headType == 'bamboozler':
            headModel = loader.loadModel('phase_3.5/models/char/sales-bldg-heads')
        if headType == 'pawnbroker':
            headModel = loader.loadModel('phase_3.5/models/char/money-bldg-heads')
        if headType in ['magister', 'ratifier', 'rat_glasses', 'doublecross', 'backseat']:
            headModel = loader.loadModel('phase_3.5/models/char/legal-bldg-heads')
        if headType == 'root' and self.style.name == 'mad':
            headModel = loader.loadModel('phase_3.5/models/char/madhander')
        if headType == 'root' and self.style.name == 'ppg':
            headModel = loader.loadModel('phase_3.5/models/char/propagandist')
        if headType == 'sellbotBoss-head-zero' and self.style.name == 'hocn':
            headModel = loader.loadModel('phase_14/models/char/pressbotBoss-head-zero')
        if headType == 'Vert' and self.style.name == 'cio':
            headModel = loader.loadModel('phase_14/models/char/cio-techbot-new')
        if headType == 'bossCog-head' and self.style.name == 'cj':
            headModel = loader.loadModel('phase_14/models/char/pressbot2Boss-head-zero')
        if headType == 'root' and self.style.name == 'dc':
            headModel = loader.loadModel('phase_14/models/char/doublecross')
        if headType == 'root' and self.style.name == 'fct':
            headModel = loader.loadModel('phase_14/models/char/fatcat')
        if headType == 'root' and self.style.name == 'fcs':
            headModel = loader.loadModel('phase_14/models/char/forecaster')
        if headType == 'root' and self.style.name == 'stg':
            headModel = loader.loadModel('phase_14/models/char/stooge')
        if headType == 'root' and self.style.name == 'ath':
            headModel = loader.loadModel('phase_14/models/char/pencilpusher')
        if headType == 'root' and self.style.name == 'surg':
            headModel = loader.loadModel('phase_14/models/char/telemarketer')
        if headType == 'root' and self.style.name == 'bsd':
            headModel = loader.loadModel('phase_14/models/char/backseat')
        if headType == 'root' and self.style.name == 'gld':
            headModel = loader.loadModel('phase_14/models/char/GoldenGoose')
        if headType == 'root' and self.style.name == 'vul':
            headModel = loader.loadModel('phase_14/models/char/GoldenGoose')
        if headType == 'root' and self.style.name == 'bck':
            headModel = loader.loadModel('phase_14/models/char/backstabber')
        if headType == 'root' and self.style.name == 'wnk':
            headModel = loader.loadModel('phase_14/models/char/whiteknight')
        if headType == 'root' and self.style.name == 'drk':
            headModel = loader.loadModel('phase_14/models/char/whiteknight')
        if headType == 'root' and self.style.name == 'std':
            headModel = loader.loadModel('phase_14/models/char/yesman')
        if headType == 'root' and self.style.name == 'std2':
            headModel = loader.loadModel('phase_14/models/char/yesman')
        if headType == 'root' and self.style.name == 'sbg':
            headModel = loader.loadModel('phase_14/models/char/sandbagger')
        if headType == 'root' and self.style.name == 'key':
            headModel = loader.loadModel('phase_14/models/char/keyboard-warrior')
        if headType == 'root' and self.style.name == 'pyc':
            headModel = loader.loadModel('phase_14/models/char/python-charmer_head')
        if headType == 'root' and self.style.name == 'sdb':
            headModel = loader.loadModel('phase_14/models/char/shotgun-debugger_head')
        if headType == 'magnate' and self.style.name == 'rng':
            headModel = loader.loadModel('phase_14/models/char/ttcc_ene_magnate')
        if headType == 'root' and self.style.name == 'shy':
            headModel = loader.loadModel('phase_14/models/char/shylock')
        if headType == 'root' and self.style.name == 'cow':
            headModel = loader.loadModel('phase_14/models/char/CashCow')
        if headType == 'root' and self.style.name == 'aud':
            headModel = loader.loadModel('phase_14/models/char/bookkeeper')
        if headType == 'Blowhard' and self.style.name == 'blh':
                headModel = loader.loadModel('phase_3.5/models/char/ttrm_m_ene_head_blowhard')
        if headType == 'industryTitan':
                headModel = loader.loadModel('phase_3.5/models/char/ttrpg_tech-heads')
        if headType == 'pointDexter':
                headModel = loader.loadModel('phase_3.5/models/char/ttrpg_tech-heads')
        if headType == 'scriptKiddie':
                headModel = loader.loadModel('phase_3.5/models/char/ttrpg_tech-heads')
        if headType == 'blackHat':
                headModel = loader.loadModel('phase_3.5/models/char/ttrpg_tech-heads')
        if headType == 'dataHoarder':
            headModel = loader.loadModel('phase_3.5/models/char/ttrpg_tech-heads')
        if headType == 'codeMonkey':
            headModel = loader.loadModel('phase_3.5/models/char/ttrpg_tech-heads')
        if headType == 'brainiac':
            headModel = loader.loadModel('phase_3.5/models/char/ttrpg_tech-heads')
        if headType == 'computerWizard':
            headModel = loader.loadModel('phase_3.5/models/char/ttrpg_tech-heads')
        if headType == 'installer-wizard':
            headModel = loader.loadModel('phase_14/models/char/installer-wizard_head')
        if headType == 'connoisseur_hat' and self.style.name == 'cn':
                headModel = loader.loadModel('phase_14/models/char/ttcc_ene_connoisseur')
        if headType == 'connoisseur_head' and self.style.name == 'cn':
                headModel = loader.loadModel('phase_14/models/char/ttcc_ene_connoisseur')
        if headType == 'connoisseur_monocle' and self.style.name == 'cn':
                headModel = loader.loadModel('phase_14/models/char/ttcc_ene_connoisseur')
        if headType == 'movershaker' and self.style.body == 'c':
                headModel = loader.loadModel('phase_4/models/char/suitB-heads')
        if headType == 'conveyancer_belt' and self.style.body == 'a':
                headModel = loader.loadModel('phase_14/models/char/ttcc_ene_conveyancer_belt')
        if headType == 'bigfish' and self.style.body == 'a':
                headModel = loader.loadModel('phase_3.5/models/char/suitC-heads')
        if headType == 'overtime' and self.style.body == 'a':
                headModel = loader.loadModel('phase_3.5/models/char/ttoff_m_ene_overtime')
        if headType == 'ambulancechaser' and self.style.body == 'a':
                headModel = loader.loadModel('phase_4/models/char/suitB-heads')
        if headType == 'gumshoe':
            headModel = loader.loadModel('phase_4/models/char/pressbot-heads')
            headModel.setH(180)
        if headType == 'hackette':
            headModel = loader.loadModel('phase_4/models/char/pressbot-heads')
            headModel.setH(180)
        if headType == 'newshound':
            headModel = loader.loadModel('phase_4/models/char/pressbot-heads')
            headModel.setH(180)
        if headType == 'anchorman':
            headModel = loader.loadModel('phase_4/models/char/pressbot-heads')
            headModel.setH(180)
        if headType == 'paperboy':
            headModel = loader.loadModel('phase_4/models/char/pressbot-heads')
            headModel.setH(180)
        if headType == 'shutterbug':
            headModel = loader.loadModel('phase_4/models/char/pressbot-heads')
            headModel.setH(180)
        if headType == 'ghostwriter':
            headModel = loader.loadModel('phase_4/models/char/pressbot-heads')
            headModel.setH(180)
        if headType == 'gazetteer':
            headModel = loader.loadModel('phase_4/models/char/pressbot-heads')
            headModel.setH(180)
        if headType == 'ttr_m_ene_lawbotClerk' and self.style.body == 'b':
            headModel = loader.loadModel('phase_14/models/char/ttr_m_ene_lawbotClerk')
        if headType == 'ttr_m_ene_cashbotAuditor' and self.style.body == 'c':
            headModel = loader.loadModel('phase_14/models/char/ttr_m_ene_cashbotAuditor')
        if headType == 'bossbotClubPresidentEarrings' and self.style.body == 'a':
            headModel = loader.loadModel('phase_14/models/char/ttr_m_ene_bossbotClubPresident')
        if headType == 'bossbotClubPresidentHead' and self.style.body == 'a':
            headModel = loader.loadModel('phase_14/models/char/ttr_m_ene_bossbotClubPresident')
        if headType == 'bossbotClubPresidentHair' and self.style.body == 'a':
            headModel = loader.loadModel('phase_14/models/char/ttr_m_ene_bossbotClubPresident')
        if headType == 'sellbotForemanHead' and self.style.body == 'b':
            headModel = loader.loadModel('phase_14/models/char/ttr_m_ene_sellbotForeman')
        if headType == 'sellbotForemanGlasses' and self.style.body == 'b':
            headModel = loader.loadModel('phase_14/models/char/ttr_m_ene_sellbotForeman')
        if headType == 'sellbotForemanEyebrows' and self.style.body == 'b':
            headModel = loader.loadModel('phase_14/models/char/ttr_m_ene_sellbotForeman')
        if headType == 'sellbotForemanHat' and self.style.body == 'b':
            headModel = loader.loadModel('phase_14/models/char/ttr_m_ene_sellbotForeman')
        if headType == 'skeleskull_A' and self.style.name == 'ubuster':
            headModel = loader.loadModel('phase_5/models/char/skullbase')
            headModel.setZ(-.1)
            headModel.setY(-.2)
            textureGlass = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_s_exe.png')
            headModel.setTexture(textureGlass, 1)
        if headType == 'skeleskull_A' and self.style.name == 'radiog':
            headModel = loader.loadModel('phase_5/models/char/skullbase')
            headModel.setZ(-.1)
            headModel.setY(-.2)
            textureGlass = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_s_exe.png')
            headModel.setTexture(textureGlass, 1)
        if headType == 'skeleskull_A' and self.style.name == 'fmaker':
            headModel = loader.loadModel('phase_5/models/char/skullbase')
            headModel.setZ(-.1)
            headModel.setY(-.2)
            textureGlass = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_g_exe.png')
            headModel.setTexture(textureGlass, 1)
        if headType == 'skeleskull_A' and self.style.name == 'director':
            headModel = loader.loadModel('phase_5/models/char/skullbase')
            headModel.setZ(-.1)
            headModel.setY(-.2)
            textureGlass = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_p_exe.png')
            headModel.setTexture(textureGlass, 1)
        if headType == 'skeleskull_A' and self.style.name == 'payman':
            headModel = loader.loadModel('phase_5/models/char/skullbase')
            headModel.setZ(-.1)
            headModel.setY(-.2)
            textureGlass = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_m_exe.png')
            headModel.setTexture(textureGlass, 1)
        if headType == 'skeleskull_A' and self.style.name == 'cinema':
            headModel = loader.loadModel('phase_5/models/char/skullbase')
            headModel.setZ(-.1)
            headModel.setY(-.2)
            textureGlass = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_s_exe.png')
            headModel.setTexture(textureGlass, 1)
        if headType == 'skeleskull_A' and self.style.name == 'choreo':
            headModel = loader.loadModel('phase_5/models/char/skullbase')
            headModel.setZ(-.1)
            headModel.setY(-.2)
            textureGlass = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_g_exe.png')
            headModel.setTexture(textureGlass, 1)
        if headType == 'skeleskull_A' and self.style.name == 'clubpres':
            headModel = loader.loadModel('phase_5/models/char/skullbase')
            headModel.setZ(-.1)
            headModel.setY(-.2)
            textureGlass = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_c_exe.png')
            headModel.setTexture(textureGlass, 1)
        if headType == 'ear01':
            headModel = loader.loadModel('phase_4/models/char/mole_cog')
            headModel.setZ(-.4)
            headModel.setScale(.7)
            headModel.setH(180)
        if headType == 'head':
            headModel = loader.loadModel('phase_4/models/char/mole_cog')
            headModel.setZ(-.4)
            headModel.setScale(.7)
            headModel.setH(180)
        if headType == 'ear03':
            headModel = loader.loadModel('phase_4/models/char/mole_cog')
            headModel.setZ(-.4)
            headModel.setScale(.7)
            headModel.setH(180)
        if headType == 'ear04':
            headModel = loader.loadModel('phase_4/models/char/mole_cog')
            headModel.setZ(-.4)
            headModel.setScale(.7)
            headModel.setH(180)
        if headType == 'ear02':
            headModel = loader.loadModel('phase_4/models/char/mole_cog')
            headModel.setZ(-.4)
            headModel.setScale(.7)
            headModel.setH(180)
        if headType == 'angel_wings':
            headModel = loader.loadModel('phase_13/models/props/angel_wings')
            headModel.setZ(1)
            headModel.setScale(1.5)
        if headType == 'telemarketer' and self.style.name == 'ppg':
            headModel = loader.loadModel('phase_9/models/char/suits/ttcc_ene_telemarketer')
        if headType == 'angel_halo':
            headModel = loader.loadModel('phase_13/models/props/angel_halo')
            headModel.setZ(1)
            headModel.setScale(1.5)
        if headType == 'goon_hat_patrol':
            headModel = loader.loadModel('phase_4/models/accessories/apriltoons/cc_m_acc_hat_goon_patrol')
            textureGlass = loader.loadTexture('phase_4/maps/apriltoons/accessories/cc_t_acc_hat_goon_patrol_purple.png')
            headModel.setTexture(textureGlass, 1)
            headModel.setZ(1)
            headModel.setScale(0.25)
        if headType == 'goon_hat_security':
            headModel = loader.loadModel('phase_4/models/accessories/apriltoons/cc_m_acc_hat_goon_security')
            textureGlass = loader.loadTexture('phase_4/maps/apriltoons/accessories/cc_t_acc_hat_goon_security.png')
            headModel.setTexture(textureGlass, 1)
            headModel.setZ(1)
            headModel.setScale(0.25)
        if headType == 'antenna_stick':
            headModel = loader.loadModel('phase_4/models/char/mole_cog')
            headModel.setZ(-.4)
            headModel.setScale(.7)
            headModel.setH(180)
        if headType == 'antenna_ball':
            headModel = loader.loadModel('phase_4/models/char/mole_cog')
            headModel.setZ(-.4)
            headModel.setScale(.7)
            headModel.setH(180)
        if headType == 'eye_mouth':
            headModel = loader.loadModel('phase_4/models/char/mole_cog')
            headModel.setZ(-.4)
            headModel.setScale(.7)
            headModel.setH(180)
        if headType == 'pupils':
            headModel = loader.loadModel('phase_4/models/char/mole_cog')
            headModel.setZ(-.4)
            headModel.setScale(.7)
            headModel.setH(180)
        if self.style.name in ['cj', 'hocn']:
            headModel.setZ(-.2)
            headModel.setY(-.2)
            headModel.setX(0)
            headModel.setR(-90)
            headModel.setH(90)
            headModel.setScale(.35)
            headModel.setTwoSided(True)
        if headType == 'tightwad' and self.style.body == 'b':
            headModel = loader.loadModel('phase_3.5/models/char/suitC-heads')
        if headType == 'numbercruncher' and self.style.body == 'c':
            headModel = loader.loadModel('phase_4/models/char/suitA-heads')
        headReferences = headModel.findAllMatches('**/' + headType)
        for i in xrange(0, headReferences.getNumPaths()):
            headPart = self.instance(headReferences.getPath(i), 'modelRoot', 'joint_head')
            headPart.setTwoSided(True)
            if self.style.name == 'ang' and headType == 'angel_wings':
                headPart.setZ(1.25)
                headPart.setScale(1.25)
            if self.style.name == 'ang' and headType == 'angel_halo':
                headPart.setZ(1.25)
                headPart.setScale(.75)
            if headType == 'goon_hat_patrol':
                headPart.setZ(1.25)
                headPart.setH(180)
                headPart.setY(1.5)
                headPart.setScale(.01)
                textureGlass = loader.loadTexture(
                    'phase_4/maps/apriltoons/accessories/cc_t_acc_hat_goon_patrol_purple.png')
                headPart.setTexture(textureGlass, 1)
            if headType == 'goon_hat_security':
                headPart.setZ(1.25)
                headPart.setY(1.5)
                headPart.setH(180)
                headPart.setScale(.01)
                textureGlass = loader.loadTexture(
                    'phase_4/maps/apriltoons/accessories/cc_t_acc_hat_goon_patrol_purple.png')
                headPart.setTexture(textureGlass, 1)
            if self.style.name in ['cj', 'hocn']:
                headPart.setZ(-.2)
                headPart.setY(-.2)
                headPart.setX(0)
                headPart.setR(-90)
                headPart.setH(90)
                headPart.setScale(.35)
                headPart.setTwoSided(True)
            if headType == 'skeleskull_A':
                headPart.setY(-.2)
                headPart.setZ(-.1)
            if self.style.name == 'cow':
                headPart.setScale(.009)
                headPart.setY(.15)
                headPart.setZ(-.05)
            if self.style.name == 'key':
                headPart.setH(180)
            if self.style.name == 'mldr':
                headPart.setZ(-.4)
                headPart.setScale(.7)
                headPart.setH(180)
                headPart.setTwoSided(True)
            if self.style.name == 'bfh2':
                headPart.setX(-.03)
                headPart.setZ(.1)
                headPart.setY(.1)
            if self.style.name == 'p':
                headPart.setX(.03)
            if self.style.name == 'dc':
                headPart.setZ(-.01)
            if self.style.name == 'ath':
                headPart.setX(.03)
            if self.style.name == 'blh':
                headPart.setY(.1)
                headPart.setH(180)
            if self.style.name == 'ppl':
                headPart.setZ(0.9)
                headPart.setY(1)
                headPart.setX(-0.05)
                headPart.setScale(4)
            if self.style.name == 'lvw':
                #headPart.setZ(0.9)
                #headPart.setY(1)
                headPart.setX(0.025)
                headPart.setScale(.01)
            if self.style.name == 'fct':
                headPart.setH(180)
                headPart.setScale(1.15)
            if self.style.name == 'fcs':
                headPart.setH(180)
                headPart.setX(.03)
                headPart.setY(-.1)
            if self.style.name == 'ovt':
                headPart.setY(-.2)
                headPart.setScale(1.05)
            if self.style.name == 'gld':
                headPart.setScale(0.8)
            if self.style.name == 'vul':
                headPart.setScale(0.8)
            if self.style.name == 'timer':
                headPart.setY(-.2)
                headPart.setScale(1.05)
            if self.style.name == 'blk':
                headPart.setY(.1)
                headPart.setZ(-.1)
            if headType == 'root' and self.style.name == 'whistleb': #whistleblower
                headPart.setH(90)
                headPart.setP(90)
                headPart.setR(-90)
                headPart.setScale(1.1)
                headPart.setZ(-.1)
            if headType == 'root': #whistleblower
                headPart.setH(90)
                headPart.setP(90)
                headPart.setR(-90)
                headPart.setX(0.025)
                #headPart.setZ(-.1)
            if headType == 'shades' and self.style.name == 'cnd2': 
                headPart.setZ(-.25)
                headPart.setY(.075)
            if headType == 'shades' and self.style.name == 'cnd': 
                headPart.setZ(-.25)
                headPart.setY(.075)
            if self.style.name == 'gms':
                headPart.setH(180)
                headPart.setZ(-.1)
            if self.style.name == 'anc':
                headPart.setH(180)
                headPart.setZ(-.1)
                headPart.setY(-.2)
            if self.style.name == 'gzt':
                headPart.setH(180)
                headPart.setZ(-.1)
                headPart.setY(-.1)
            if self.style.name == 'hck':
                headPart.setH(180)
                headPart.setZ(-.1)
                headPart.setY(-.1)
            if self.style.name == 'ppb':
                headPart.setH(180)
                headPart.setZ(-.1)
            if self.style.name == 'ghw':
                headPart.setH(180)
                headPart.setZ(-.1)
                headPart.setY(-.2)
            if self.style.name == 'shb':
                headPart.setH(180)
                headPart.setZ(-.1)
            if self.style.name == 'nsh':
                headPart.setH(180)
                headPart.setZ(-.1)
                headPart.setY(-.2)
            if self.style.name == 'rus':
                headPart.setZ(-.1)
                headPart.setY(-.1)
                headPart.setScale(1.05)
                headPart.setH(0)
            if self.style.name == 'chg':
                headPart.setScale(0.75)
            if self.headTexture:
                headTex = loader.loadTexture('phase_' + str(phase) + '/maps/' + self.headTexture)
                headPart.setTexture(headTex, 1)
            if self.headColor:
                headPart.setColor(self.headColor)
            self.headParts.append(headPart)



    def generateHeadAnims(self, path, cActor, additionalAnims=[]):
        anims = ['neutral', 'death', 'grunt', 'murmur', 'question', 'statement', 'neutral-hurt', 'neutral-lured',
                 'fusiondance-shot1', 'fusiondance-shot2', 'fusiondance-shot3', 'fusiondance-shot4', 'fusiondance-shot5',
                 'stun', 'enraged', 'sacrifice-cog', 'summon-cog', 'insurance', 'bellow', 'ace-in-the-hole', 'wheelspin', 'healing-bell', 'revvedup',
                 'scabbard', 'sparkplug', 'throttle', 'throttle2', 'mouthdrop', 'dive', 'bust', 
                 'emergeHead', 'exitWater', 'underwaterHit', 'gamble', 'cigar-smoke', 'gsnap', 'overclocked',
                 'come-on', 'zero' ]
        for anim in additionalAnims:
            anims.append(anim)
        animList = {}
        for anim in anims:
            animList[anim] = path + anim + '.bam'
        cActor.loadAnims(animList)

    def generateCorporateMedallion2(self):
        icons = loader.loadModel('phase_3.5/models/char/ttcc_ene_insignias')
        icons2 = loader.loadModel('phase_3.5/models/gui/cog_icons')
        dept = self.style.dept
        if base.config.GetBool('want-new-cogs', 0):
            chestNull = self.find('**/def_joint_attachMeter')
            if chestNull.isEmpty():
                chestNull = self.find('**/joint_attachMeter')
        else:
            chestNull = self.find('**/joint_attachMeter')
        if dept == 'c':
            self.corpMedallion = icons.find('**/emblem_corp').copyTo(chestNull)
        elif dept == 's':
            self.corpMedallion = icons.find('**/emblem_sales').copyTo(chestNull)
        elif dept == 'l':
            self.corpMedallion = icons.find('**/emblem_legal').copyTo(chestNull)
        elif dept == 'm':
            self.corpMedallion = icons.find('**/emblem_money').copyTo(chestNull)
        elif dept == 'g':
            self.corpMedallion = icons.find('**/emblem_legal').copyTo(chestNull)
            texture = loader.loadTexture('phase_3/maps/ttcc_suit_insignias_palette4.png')
            self.corpMedallion.setTexture(texture, 1)
        elif dept == 't':
            self.corpMedallion = icons.find('**/emblem_legal').copyTo(chestNull)
            texture = loader.loadTexture('phase_3/maps/ttcc_suit_insignias_palette2.png')
            self.corpMedallion.setTexture(texture, 1)
        elif dept == 'p':
            self.corpMedallion = icons.find('**/emblem_legal').copyTo(chestNull)
            texture = loader.loadTexture('phase_3/maps/ttcc_suit_insignias_palette3.png')
            self.corpMedallion.setTexture(texture, 1)

        self.corpMedallion.setPosHprScale(0, -1, 0, 180.0, 0.0, 0.0, 0, 0, 0)
        #self.corpMedallion.setColor(self.medallionColors[dept])
        if self.style.name == 'fhj':
            self.corpMedallion.setScale(0)
        elif self.style.name == 'hrollers':
            self.corpMedallion.setScale(0)
        elif self.style.name == 'bcaster':
            self.corpMedallion.setScale(0)
        elif self.style.name == 'hroller':
            self.corpMedallion.setScale(0)
        elif self.style.name == 'hroller':
            self.corpMedallion.setScale(0)
        elif self.isBuff:
            self.corpMedallion.setY(.05)
            self.corpMedallion.setZ(-.2)
        elif self.isFemale and (self.style.body == 'c' or self.style.body == 'b'):
            self.corpMedallion.setZ(.2)
            self.corpMedallion.setZ(.2)
        icons.removeNode()

    def generateCorporateMedallion3(self):
        icons = loader.loadModel('phase_3.5/models/char/ttcc_ene_insignias')
        icons2 = loader.loadModel('phase_3.5/models/gui/cog_icons')
        dept = self.style.dept
        if base.config.GetBool('want-new-cogs', 0):
            chestNull = self.find('**/def_joint_attachMeter')
            if chestNull.isEmpty():
                chestNull = self.find('**/joint_attachMeter')
        else:
            chestNull = self.find('**/joint_attachMeter')
        if dept == 'c':
            self.corpMedallion = icons.find('**/emblem_corp').copyTo(chestNull)
        elif dept == 's':
            self.corpMedallion = icons.find('**/emblem_sales').copyTo(chestNull)
        elif dept == 'l':
            self.corpMedallion = icons.find('**/emblem_legal').copyTo(chestNull)
        elif dept == 'm':
            self.corpMedallion = icons.find('**/emblem_money').copyTo(chestNull)
        elif dept == 'g':
            self.corpMedallion = icons.find('**/emblem_legal').copyTo(chestNull)
            texture = loader.loadTexture('phase_3/maps/ttcc_suit_insignias_palette4.png')
            self.corpMedallion.setTexture(texture, 1)
        elif dept == 't':
            self.corpMedallion = icons.find('**/emblem_legal').copyTo(chestNull)
            texture = loader.loadTexture('phase_3/maps/ttcc_suit_insignias_palette2.png')
            self.corpMedallion.setTexture(texture, 1)
        elif dept == 'p':
            self.corpMedallion = icons.find('**/emblem_legal').copyTo(chestNull)
            texture = loader.loadTexture('phase_3/maps/ttcc_suit_insignias_palette3.png')
            self.corpMedallion.setTexture(texture, 1)

        self.corpMedallion.setPosHprScale(0, -1, 0, 180.0, 0.0, 0.0, 0, 0, 0)
        #self.corpMedallion.setColor(self.medallionColors[dept])
        if self.style.name == 'fhj':
            self.corpMedallion.setScale(0)
        elif self.style.name == 'hrollers':
            self.corpMedallion.setScale(0)
        elif self.style.name == 'bcaster':
            self.corpMedallion.setScale(0)
        elif self.style.name == 'hroller':
            self.corpMedallion.setScale(0)
        elif self.style.name == 'hroller':
            self.corpMedallion.setScale(0)
        elif self.isBuff:
            self.corpMedallion.setY(.05)
            self.corpMedallion.setZ(-.2)
        elif self.isFemale and (self.style.body == 'c' or self.style.body == 'b'):
            self.corpMedallion.setZ(.2)
            self.corpMedallion.setZ(.2)
        icons.removeNode()


    def generateCorporateTie(self, modelPath = None):
        if not modelPath:
            modelPath = self
        dept = self.style.dept
        tie = modelPath.find('**/tie')
        if tie.isEmpty():
            self.notify.warning('skelecog has no tie model!!!')
            return

        if dept == 'c':
            tieTex = loader.loadTexture('phase_5/maps/cog_robot_tie_boss.jpg')
        elif dept == 's':
            tieTex = loader.loadTexture('phase_5/maps/cog_robot_tie_sales.jpg')
        elif dept == 'l':
            tieTex = loader.loadTexture('phase_5/maps/cog_robot_tie_legal.jpg')
        elif dept == 'm':
            tieTex = loader.loadTexture('phase_5/maps/cog_robot_tie_money.jpg')
        elif dept == 'g':
            tieTex = loader.loadTexture('phase_5/maps/cog_robot_tie_board.jpg')
        elif dept == 't':
            tieTex = loader.loadTexture('phase_5/maps/cog_robot_tie_sales.jpg')
        elif dept == 'p':
            tieTex = loader.loadTexture('phase_5/maps/cog_robot_tie_sales.jpg')
        #tieTex.setMinfilter(Texture.FTLinearMipmapLinear)
        #tieTex.setMagfilter(Texture.FTLinear)
        tie.setTexture(tieTex, 1)

    def generateCorporateMedallion(self):
        icons = loader.loadModel('phase_3.5/models/char/ttcc_ene_insignias')
        icons2 = loader.loadModel('phase_3.5/models/gui/cog_icons')
        dept = self.style.dept
        if base.config.GetBool('want-new-cogs', 0):
            chestNull = self.find('**/def_joint_attachMeter')
            if chestNull.isEmpty():
                chestNull = self.find('**/joint_attachMeter')
        else:
            chestNull = self.find('**/joint_attachMeter')
        if dept == 'c':
            self.corpMedallion = icons.find('**/emblem_corp').copyTo(chestNull)
        elif dept == 's':
            self.corpMedallion = icons.find('**/emblem_sales').copyTo(chestNull)
        elif dept == 'l':
            self.corpMedallion = icons.find('**/emblem_legal').copyTo(chestNull)
        elif dept == 'm':
            self.corpMedallion = icons.find('**/emblem_money').copyTo(chestNull)
        elif dept == 'g':
            self.corpMedallion = icons.find('**/emblem_legal').copyTo(chestNull)
            texture = loader.loadTexture('phase_3/maps/ttcc_suit_insignias_palette4.png')
            self.corpMedallion.setTexture(texture, 1)
        elif dept == 't':
            self.corpMedallion = icons.find('**/emblem_legal').copyTo(chestNull)
            texture = loader.loadTexture('phase_3/maps/ttcc_suit_insignias_palette2.png')
            self.corpMedallion.setTexture(texture, 1)
        elif dept == 'p':
            self.corpMedallion = icons.find('**/emblem_legal').copyTo(chestNull)
            texture = loader.loadTexture('phase_3/maps/ttcc_suit_insignias_palette3.png')
            self.corpMedallion.setTexture(texture, 1)
        self.corpMedallion.setH(180.0)
       # self.corpMedallion.setColor(self.medallionColors[dept])
        if self.style.body == 'a' and not self.isFemale and not self.isBuff:
            self.corpMedallion.setY(-.1125)
            self.corpMedallion.setZ(-.1)
        if self.isBuff:
            self.corpMedallion.setY(.05)
            self.corpMedallion.setZ(-.2)
        if self.style.body == 'a' and self.isFemale:
            self.corpMedallion.setY(-0.075)
            self.corpMedallion.setZ(-.1)
        if self.style.body == 'b':
            self.corpMedallion.setY(-.025)
        if self.style.body == 'c' and not self.isFemale:
            self.corpMedallion.setY(.05)
       # if self.style.body == 'a':
          #  self.corpMedallion.setY(-.1)
          #  self.corpMedallion.setZ(-.1)
        self.corpMedallion.setScale(1.175)
        if self.style.name == 'fhj':
            self.corpMedallion.setScale(0)
        elif self.style.name == 'hroller2':
            self.corpMedallion.setScale(0)
        elif self.style.name == 'bcaster':
            self.corpMedallion.setScale(0)
        elif self.style.name == 'hroller':
            self.corpMedallion.setScale(0)
        elif self.style.name == 'hrollers':
            self.corpMedallion.setScale(0)
        elif self.style.name == 'videog':
            self.corpMedallion.setScale(0)
        elif self.style.name == 'fmaker':
            self.corpMedallion.setScale(0)
        elif self.style.name == 'cinema':
            self.corpMedallion.setScale(0)
        elif self.style.name == 'choreo':
            self.corpMedallion.setScale(0)
        elif self.style.name == 'director':
            self.corpMedallion.setScale(0)
        elif self.isBuff:
            self.corpMedallion.setY(.05)
            self.corpMedallion.setZ(-.2)
        elif self.isFemale and (self.style.body == 'c' or self.style.body == 'b'):
            self.corpMedallion.setZ(.2)
            self.corpMedallion.setZ(.2)
        icons.removeNode()
        icons2.removeNode()

    def generateHPBase(self):
        model = loader.loadModel('phase_3.5/models/char/ttcc_ene_insignias')
        icons = loader.loadModel('phase_3/models/gui/cog_icons')
        dept = self.style.dept
        if base.config.GetBool('want-new-cogs', 0):
            chestNull = self.find('**/def_joint_attachMeter')
            if chestNull.isEmpty():
                chestNull = self.find('**/joint_attachMeter')
        else:
            chestNull = self.find('**/joint_attachMeter')
        if dept == 'c':
            self.hpBase = model.find('**/emblem_base').copyTo(chestNull)
        elif dept == 's':
            self.hpBase = model.find('**/emblem_base').copyTo(chestNull)
        elif dept == 'l':
            self.hpBase = model.find('**/emblem_base').copyTo(chestNull)
        elif dept == 'm':
            self.hpBase = model.find('**/emblem_base').copyTo(chestNull)
        elif dept == 'g':
            self.hpBase = model.find('**/emblem_base').copyTo(chestNull)
        elif dept == 't':
            self.hpBase = model.find('**/emblem_base').copyTo(chestNull)
        elif dept == 'p':
            self.hpBase = model.find('**/emblem_base').copyTo(chestNull)
        self.hpBase.setH(180.0)
       # self.hpBase.setColor(self.medallionColors[dept])
        if self.style.name == 'fhj':
            self.hpBase.setScale(0)
        elif self.style.name == 'hroller2':
            self.hpBase.setScale(0)
        elif self.style.name == 'hroller':
            self.hpBase.setScale(0)
        elif self.style.name == 'hrollers':
            self.hpBase.setScale(0)
        elif self.style.name == 'bcaster':
            self.hpBase.setScale(0)
        elif self.style.name == 'videog':
            self.hpBase.setScale(0)
        elif self.style.name == 'fmaker':
            self.hpBase.setScale(0)
        elif self.style.name == 'cinema':
            self.hpBase.setScale(0)
        elif self.style.name == 'choreo':
            self.hpBase.setScale(0)
        elif self.style.name == 'director':
            self.hpBase.setScale(0)
        else:
            self.hpBase.setScale(1.175)
        if self.isFemale and (self.style.body == 'c' or self.style.body == 'b'):
            self.hpBase.setZ(.2)
            self.hpBase.setZ(.2)
        if self.isBuff:
            self.hpBase.setY(.05)
            self.hpBase.setZ(-.2)
        if self.style.body == 'c' and not self.isFemale:
            self.hpBase.setY(.05)
       # if self.style.body == 'c':
            #self.hpBase.setY()
        if self.style.body == 'a' and not self.isFemale and not self.isBuff:
            self.hpBase.setY(-.1125)
            self.hpBase.setZ(-.1)
        if self.style.body == 'a' and self.isFemale:
            self.hpBase.setY(-0.075)
            self.hpBase.setZ(-.1)
        if self.style.body == 'b':
            self.hpBase.setY(-.025)
        model.removeNode()
        icons.removeNode()

    def generateHealthBar(self):
        self.removeHealthBar()
        model = loader.loadModel('phase_3.5/models/char/ttcc_ene_insignias')
        button = model.find('**/emblem_hp')
        if self.style.name == 'fhj':
            button.setScale(0)
        elif self.style.name == 'hrollers':
            button.setScale(0)
        elif self.style.name == 'bcaster':
            button.setScale(0)
        elif self.style.name == 'hroller':
            button.setScale(0)
        elif self.style.name == 'hroller2':
            button.setScale(0)
        elif self.style.name == 'videog':
            button.setScale(0)
        elif self.style.name == 'fmaker':
            button.setScale(0)
        elif self.style.name == 'cinema':
            button.setScale(0)
        elif self.style.name == 'choreo':
            button.setScale(0)
        elif self.style.name == 'director':
            button.setScale(0)
        else:
            button.setScale(1.175)
        button.setH(180.0)
        button.setColor(self.healthColors[0])
        chestNull = self.find('**/joint_attachMeter')
        button.reparentTo(chestNull)
        self.healthBar = button
        glow = button.find('**/glow')
        glow.reparentTo(self.healthBar)
       # glow.setTransparency(1)
       # glow.setTwoSided(True)
        if self.style.name == 'fhj':
            glow.setScale(0)
        elif self.style.name == 'hrollers':
            glow.setScale(0)
        elif self.style.name == 'videog':
            glow.setScale(0)
        elif self.style.name == 'fmaker':
            glow.setScale(0)
        elif self.style.name == 'cinema':
            glow.setScale(0)
        elif self.style.name == 'choreo':
            glow.setScale(0)
        elif self.style.name == 'director':
            glow.setScale(0)
        elif self.style.name == 'bcaster':
            glow.setScale(0)
        elif self.style.name == 'hroller':
            glow.setScale(0)
        elif self.style.name == 'hroller2':
            glow.setScale(0)
        else:
            glow.setScale(1)
        glow.setPos(0, 0, 0)
        glow.setColor(self.healthGlowColors[0])
        self.healthBarGlow = glow
        self.healthCondition = 0
        self.healthBar.hide()
        #self.healthBarGlow.hide()
        if self.style.body == 'a' and not self.isFemale and not self.isBuff:
            self.healthBar.setY(-.1125)
            self.healthBar.setZ(-.1)
        if self.style.body == 'a' and self.isFemale:
            self.healthBar.setY(-0.075)
            self.healthBar.setZ(-.1)
        if self.style.body == 'b':
            self.healthBar.setY(-.025)
        if self.style.body == 'c' and not self.isFemale:
            self.healthBar.setY(.05)
        if self.isBuff:
            self.healthBar.setY(.05)
            self.healthBar.setZ(-.2)
       # if self.style.body == 'c':
            #self.healthBar.setY(.05)
       # if self.style.body == 'a':
           # self.healthBar.setY(-.1)
           # self.healthBar.setZ(-.1)
        if self.isFemale and (self.style.body == 'c' or self.style.body == 'b'):
            self.healthBar.setZ(.2)
            self.healthBar.setZ(.2)

    def generateSkeletonHealthBar(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        button = modelRoot.find('**/emblem_healthmeter')
        self.removeHealthBar()
        button.setScale(1)
        button.setColor(self.healthColors[0])
        self.healthBar = button
        glow = modelRoot.find('**/glow')
        glow.reparentTo(self.healthBar)
        glow.setScale(1)
        glow.setPos(0, 0, 0)
        glow.setColor(self.healthGlowColors[0])
        self.healthBarGlow = glow
        self.healthCondition = 0
        self.healthBar.hide()
        #self.healthBarGlow.hide()

    def generateSkeletonHealthBarDisplay(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        button = modelRoot.find('**/emblem_healthmeter')
        button.setScale(1)
        button.setColor(self.healthColors[16])
        self.healthBarDisplay = button
        glow = modelRoot.find('**/glow')
        glow.reparentTo(self.healthBarDisplay)
        glow.setScale(1)
        glow.setPos(0, 0, 0)
        glow.setColor(self.healthGlowColors[16])
        self.healthBarGlowDisplay = glow
        self.healthCondition = 0
        #self.healthBar.hide()
        #self.healthBarGlow.hide()

    def generateSkeletonHealthBarDisplay2(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        button = modelRoot.find('**/emblem_healthmeter')
        button.setScale(1)
        button.setColor(self.healthColors[0])
        self.healthBarDisplay = button
        glow = modelRoot.find('**/glow')
        glow.reparentTo(self.healthBarDisplay)
        glow.setScale(1)
        glow.setPos(0, 0, 0)
        glow.setColor(self.healthGlowColors[0])
        self.healthBarGlowDisplay = glow
        self.healthCondition = 0
        #self.healthBar.hide()
        #self.healthBarGlow.hide()

    def resetHealthBarForSkele(self):
        self.healthBar.setPos(0.0, 0.0, 0.0)

    def cleanupHealthPulseTasks(self):
        taskMgr.remove(self.uniqueName('pulse-task'))
        taskMgr.remove(self.uniqueName('blink-task'))

        if hasattr(self, 'interval') and self.interval:
            self.interval.finish()
            self.interval = None

        if hasattr(self, 'glowInterval') and self.glowInterval:
            self.glowInterval.finish()
            self.glowInterval = None

        if hasattr(self, 'virtualizeIntervals'):
            for ival in self.virtualizeIntervals:
                if ival:
                    ival.finish()
            self.virtualizeIntervals = []

    def updateHealthBar(self, hp, forceUpdate = 0):
        self.currHP -= hp
        messenger.send(self.uniqueName('suitHpUpdate'), [self.currHP, self.maxHP, hp])
        health = float(self.currHP) / float(self.maxHP)
        taskMgr.remove(self.uniqueName('pulse-task'))
        if self.isVirtual and not self.isSkeleton:
            self.healthBar.hide()
            self.healthBarGlow.hide()
            self.hpBase.hide()
            self.corpMedallion.hide()
        if health > 1.5:
            condition = 13
        elif health > 1.25:
            condition = 12
        elif health > 1.0:
            condition = 12
        elif health > 0.95:
            condition = 0
        elif health > 0.9:
            condition = 1
        elif health > 0.8:
            condition = 2
        elif health > 0.7:
            condition = 3
        elif health > 0.6:
            condition = 4
        elif health > 0.5:
            condition = 5
        elif health > 0.4:
            condition = 6
        elif health > 0.25:
            condition = 7
        elif health > 0.2:
            condition = 8
        elif health > 0.1:
            condition = 9
        elif health > 0.0:
            condition = 10
        else:
            condition = 11
        self.condition = condition
        if self.style.name == 'hrollers':
            if self.getActualLevel() == 36: #36
                self.setDisplayName(self.createNameInfoGold())
                if condition == 10:
                    taskMgr.remove(self.uniqueName('blink-task'))
                    blinkTask = Task.loop(Task(self.__pulseRed), Task.pause(0.75), Task(self.__pulseGray),
                                          Task.pause(0.1))
                    taskMgr.add(blinkTask, self.uniqueName('blink-task'))
                elif condition == 11:
                    taskMgr.remove(self.uniqueName('blink-task'))
                    if self.healthCondition == 10:
                        taskMgr.remove(self.uniqueName('blink-task'))
                    blinkTask = Task.loop(Task(self.__pulseRed), Task.pause(0.25), Task(self.__pulseGray),
                                          Task.pause(0.1))
                    taskMgr.add(blinkTask, self.uniqueName('blink-task'))
                else:
                    self.virtualize(22)
            elif self.getActualLevel() == 35: #36
                self.setDisplayName(self.createNameInfoTeal())
                if condition == 10:
                    taskMgr.remove(self.uniqueName('blink-task'))
                    blinkTask = Task.loop(Task(self.__pulseRed), Task.pause(0.75), Task(self.__pulseGray),
                                          Task.pause(0.1))
                    taskMgr.add(blinkTask, self.uniqueName('blink-task'))
                elif condition == 11:
                    taskMgr.remove(self.uniqueName('blink-task'))
                    if self.healthCondition == 10:
                        taskMgr.remove(self.uniqueName('blink-task'))
                    blinkTask = Task.loop(Task(self.__pulseRed), Task.pause(0.25), Task(self.__pulseGray),
                                          Task.pause(0.1))
                    taskMgr.add(blinkTask, self.uniqueName('blink-task'))
                else:
                    self.virtualize(21)
            elif self.getActualLevel() == 34: #36
                self.setDisplayName(self.createNameInfoMagenta())
                if condition == 10:
                    taskMgr.remove(self.uniqueName('blink-task'))
                    blinkTask = Task.loop(Task(self.__pulseRed), Task.pause(0.75), Task(self.__pulseGray),
                                          Task.pause(0.1))
                    taskMgr.add(blinkTask, self.uniqueName('blink-task'))
                elif condition == 11:
                    taskMgr.remove(self.uniqueName('blink-task'))
                    if self.healthCondition == 10:
                        taskMgr.remove(self.uniqueName('blink-task'))
                    blinkTask = Task.loop(Task(self.__pulseRed), Task.pause(0.25), Task(self.__pulseGray),
                                          Task.pause(0.1))
                    taskMgr.add(blinkTask, self.uniqueName('blink-task'))
                else:
                    self.virtualize(20)
            elif self.getActualLevel() == 33:
                self.setDisplayName(self.createNameInfoWhite())
                if condition == 10:
                    taskMgr.remove(self.uniqueName('blink-task'))
                    blinkTask = Task.loop(Task(self.__pulseRed), Task.pause(0.75), Task(self.__pulseGray),
                                          Task.pause(0.1))
                    taskMgr.add(blinkTask, self.uniqueName('blink-task'))
                elif condition == 11:
                    taskMgr.remove(self.uniqueName('blink-task'))
                    if self.healthCondition == 10:
                        taskMgr.remove(self.uniqueName('blink-task'))
                    blinkTask = Task.loop(Task(self.__pulseRed), Task.pause(0.25), Task(self.__pulseGray),
                                          Task.pause(0.1))
                    taskMgr.add(blinkTask, self.uniqueName('blink-task'))
                else:
                    self.virtualize(19)
            elif self.getActualLevel() == 32:
                self.setDisplayName(self.createNameInfoPurple())
                if condition == 10:
                    taskMgr.remove(self.uniqueName('blink-task'))
                    blinkTask = Task.loop(Task(self.__pulseRed), Task.pause(0.75), Task(self.__pulseGray),
                                          Task.pause(0.1))
                    taskMgr.add(blinkTask, self.uniqueName('blink-task'))
                elif condition == 11:
                    taskMgr.remove(self.uniqueName('blink-task'))
                    if self.healthCondition == 10:
                        taskMgr.remove(self.uniqueName('blink-task'))
                    blinkTask = Task.loop(Task(self.__pulseRed), Task.pause(0.25), Task(self.__pulseGray),
                                          Task.pause(0.1))
                    taskMgr.add(blinkTask, self.uniqueName('blink-task'))
                else:
                    self.virtualize(13)
            elif self.getActualLevel() == 31:
                self.setDisplayName(self.createNameInfoLightBlue())
                if condition == 10:
                    taskMgr.remove(self.uniqueName('blink-task'))
                    blinkTask = Task.loop(Task(self.__pulseRed), Task.pause(0.75), Task(self.__pulseGray),
                                          Task.pause(0.1))
                    taskMgr.add(blinkTask, self.uniqueName('blink-task'))
                elif condition == 11:
                    taskMgr.remove(self.uniqueName('blink-task'))
                    if self.healthCondition == 10:
                        taskMgr.remove(self.uniqueName('blink-task'))
                    blinkTask = Task.loop(Task(self.__pulseRed), Task.pause(0.25), Task(self.__pulseGray),
                                          Task.pause(0.1))
                    taskMgr.add(blinkTask, self.uniqueName('blink-task'))
                else:
                    self.virtualize(12)
            elif self.getActualLevel() == 30:
                self.setDisplayName(self.createNameInfoPink())
                if condition == 10:
                    taskMgr.remove(self.uniqueName('blink-task'))
                    blinkTask = Task.loop(Task(self.__pulseRed), Task.pause(0.75), Task(self.__pulseGray),
                                          Task.pause(0.1))
                    taskMgr.add(blinkTask, self.uniqueName('blink-task'))
                elif condition == 11:
                    taskMgr.remove(self.uniqueName('blink-task'))
                    if self.healthCondition == 10:
                        taskMgr.remove(self.uniqueName('blink-task'))
                    blinkTask = Task.loop(Task(self.__pulseRed), Task.pause(0.25), Task(self.__pulseGray),
                                          Task.pause(0.1))
                    taskMgr.add(blinkTask, self.uniqueName('blink-task'))
                else:
                    self.virtualize(14)
            elif self.getActualLevel() == 29:
                self.setDisplayName(self.createNameInfoRed())
                if condition == 10:
                    taskMgr.remove(self.uniqueName('blink-task'))
                    blinkTask = Task.loop(Task(self.__pulseRed), Task.pause(0.75), Task(self.__pulseGray),
                                          Task.pause(0.1))
                    taskMgr.add(blinkTask, self.uniqueName('blink-task'))
                elif condition == 11:
                    taskMgr.remove(self.uniqueName('blink-task'))
                    if self.healthCondition == 10:
                        taskMgr.remove(self.uniqueName('blink-task'))
                    blinkTask = Task.loop(Task(self.__pulseRed), Task.pause(0.25), Task(self.__pulseGray),
                                          Task.pause(0.1))
                    taskMgr.add(blinkTask, self.uniqueName('blink-task'))
                else:
                    self.virtualize(8)
            elif self.getActualLevel() == 28:
                self.setDisplayName(self.createNameInfoBlue())
                if condition == 10:
                    taskMgr.remove(self.uniqueName('blink-task'))
                    blinkTask = Task.loop(Task(self.__pulseRed), Task.pause(0.75), Task(self.__pulseGray),
                                          Task.pause(0.1))
                    taskMgr.add(blinkTask, self.uniqueName('blink-task'))
                elif condition == 11:
                    taskMgr.remove(self.uniqueName('blink-task'))
                    if self.healthCondition == 10:
                        taskMgr.remove(self.uniqueName('blink-task'))
                    blinkTask = Task.loop(Task(self.__pulseRed), Task.pause(0.25), Task(self.__pulseGray),
                                          Task.pause(0.1))
                    taskMgr.add(blinkTask, self.uniqueName('blink-task'))
                else:
                    self.virtualize(15)
            elif self.getActualLevel() == 27:
                self.setDisplayName(self.createNameInfoYellow())
                if condition == 10:
                    taskMgr.remove(self.uniqueName('blink-task'))
                    blinkTask = Task.loop(Task(self.__pulseRed), Task.pause(0.75), Task(self.__pulseGray),
                                          Task.pause(0.1))
                    taskMgr.add(blinkTask, self.uniqueName('blink-task'))
                elif condition == 11:
                    taskMgr.remove(self.uniqueName('blink-task'))
                    if self.healthCondition == 10:
                        taskMgr.remove(self.uniqueName('blink-task'))
                    blinkTask = Task.loop(Task(self.__pulseRed), Task.pause(0.25), Task(self.__pulseGray),
                                          Task.pause(0.1))
                    taskMgr.add(blinkTask, self.uniqueName('blink-task'))
                else:
                    self.virtualize(3)
            elif self.getActualLevel() == 26:
                self.setDisplayName(self.createNameInfoOrange())
                if condition == 10:
                    taskMgr.remove(self.uniqueName('blink-task'))
                    blinkTask = Task.loop(Task(self.__pulseRed), Task.pause(0.75), Task(self.__pulseGray),
                                          Task.pause(0.1))
                    taskMgr.add(blinkTask, self.uniqueName('blink-task'))
                elif condition == 11:
                    taskMgr.remove(self.uniqueName('blink-task'))
                    if self.healthCondition == 10:
                        taskMgr.remove(self.uniqueName('blink-task'))
                    blinkTask = Task.loop(Task(self.__pulseRed), Task.pause(0.25), Task(self.__pulseGray),
                                          Task.pause(0.1))
                    taskMgr.add(blinkTask, self.uniqueName('blink-task'))
                else:
                    self.virtualize(7)
            else:
                self.setDisplayName(self.createNameInfoGreen())
                if condition == 10:
                    taskMgr.remove(self.uniqueName('blink-task'))
                    blinkTask = Task.loop(Task(self.__pulseRed), Task.pause(0.75), Task(self.__pulseGray),
                                          Task.pause(0.1))
                    taskMgr.add(blinkTask, self.uniqueName('blink-task'))
                elif condition == 11:
                    taskMgr.remove(self.uniqueName('blink-task'))
                    if self.healthCondition == 10:
                        taskMgr.remove(self.uniqueName('blink-task'))
                    blinkTask = Task.loop(Task(self.__pulseRed), Task.pause(0.25), Task(self.__pulseGray),
                                          Task.pause(0.1))
                    taskMgr.add(blinkTask, self.uniqueName('blink-task'))
                else:
                    self.virtualize(0)
        if self.style.name == 'clubpres':
            if self.getActualLevel() == 20:
                self.setDisplayName(self.createNameInfoHighStakes())
            elif self.getActualLevel() == 21:
                self.setDisplayName(self.createNameInfoMulligan())
            elif self.getActualLevel() == 22:
                self.setDisplayName(self.createNameInfoAncient())
            elif self.getActualLevel() == 23:
                self.setDisplayName(self.createNameInfoChipFan())
            elif self.getActualLevel() == 24:
                self.setDisplayName(self.createNameInfoPuzzling())
            elif self.getActualLevel() == 25:
                self.setDisplayName(self.createNameInfoShivering())
            elif self.getActualLevel() == 26:
                self.setDisplayName(self.createNameInfoSensational())
            elif self.getActualLevel() == 27:
                self.setDisplayName(self.createNameInfoCommissioning())
            else:
                pass
        if self.style.name == 'ovt':
            self.setDisplayName(self.createNameInfoConfusedReal())
        if self.style.name == 'supervis':
            if self.getActualLevel() == 20:
                self.setDisplayName(self.createNameInfoAbacus())
            elif self.getActualLevel() == 21:
                self.setDisplayName(self.createNameInfoControlling())
            elif self.getActualLevel() == 22:
                self.setDisplayName(self.createNameInfoConfused())
            elif self.getActualLevel() == 23:
                self.setDisplayName(self.createNameInfoAccountant())
            elif self.getActualLevel() == 24:
                self.setDisplayName(self.createNameInfoSpongy())
                #self.makeShielding()
                self.setSuitStatusEffect('absorbing')
            elif self.getActualLevel() == 25:
                self.setDisplayName(self.createNameInfoFraudulent())
            elif self.getActualLevel() == 26:
                self.setDisplayName(self.createNameInfoImmovable())
            elif self.getActualLevel() == 27:
                self.setDisplayName(self.createNameInfoLedgering())
            elif self.getActualLevel() == 28:
                self.setDisplayName(self.createNameInfoAuditing())
            elif self.getActualLevel() == 29:
                self.setDisplayName(self.createNameInfoUsurer())
            elif self.getActualLevel() == 30:
                self.setDisplayName(self.createNameInfoScheming())
            else:
                pass
        if self.style.name == 'clerk':
            if self.getActualLevel() == 20:
                self.setDisplayName(self.createNameInfoSneaky())
            elif self.getActualLevel() == 21:
                self.setDisplayName(self.createNameInfoOmnipotent())
            elif self.getActualLevel() == 22:
                self.setDisplayName(self.createNameInfoOverseer())
            elif self.getActualLevel() == 23:
                self.setDisplayName(self.createNameInfoMonolithic())
            elif self.getActualLevel() == 24:
                self.setDisplayName(self.createNameInfoChrono())
            elif self.getActualLevel() == 25:
                self.setDisplayName(self.createNameInfoLaborious())
            elif self.getActualLevel() == 26:
                self.setDisplayName(self.createNameInfoDraining())
            elif self.getActualLevel() == 27:
                self.setDisplayName(self.createNameInfoShaking())
            elif self.getActualLevel() == 28:
                self.setDisplayName(self.createNameInfoDizzy())
            else:
                pass
        if self.style.name == 'foreman':
            if self.getActualLevel() == 20:
                self.setDisplayName(self.createNameInfoSleepy())
                if not self.isAlreadySleepy:
                    self.makeSleepy(3)
                    self.setSuitStatusEffect('sleepy', turns=3)
            elif self.getActualLevel() == 21:
                self.setDisplayName(self.createNameInfoBurning())
            elif self.getActualLevel() == 22:
                self.setDisplayName(self.createNameInfoExplosive())
                if not self.isAlreadyExplosive:
                    self.makeExplosive(3)
                    self.setSuitStatusEffect('explosive', turns=3)
            elif self.getActualLevel() == 23:
                self.setDisplayName(self.createNameInfoContractor())
            elif self.getActualLevel() == 24:
                self.setDisplayName(self.createNameInfoRedTape())
            elif self.getActualLevel() == 25:
                self.setDisplayName(self.createNameInfoSniper())
            elif self.getActualLevel() == 26:
                self.setDisplayName(self.createNameInfoUnionized())
            elif self.getActualLevel() == 27:
                self.setDisplayName(self.createNameInfoContributing())
            elif self.getActualLevel() == 28:
                self.setDisplayName(self.createNameInfoPolishing())
            elif self.getActualLevel() == 29:
                self.setDisplayName(self.createNameInfoExtortionist())
            else:
                pass
        #self.healthCondition = condition
        #print('UpdateHealthBar - condition is %i' % condition)

        if self.healthCondition != condition or forceUpdate:
            if condition <= 9:
                taskMgr.remove(self.uniqueName('pulse-task'))
                taskMgr.remove(self.uniqueName('blink-task'))
                if not self.virtual:
                    self.healthBar.setColor(1, 1, 1, 1)
                    self.healthBarGlow.setColor(1, 1, 1, 1)
                else:
                    self.healthBarGlow.setColor(0, 0, 0, 0)
                    if not self.style.name == 'hrollers':
                        self.virtualize(condition)
                self.__changeColor()
            elif condition == 10:
                taskMgr.remove(self.uniqueName('pulse-task'))
                taskMgr.remove(self.uniqueName('blink-task'))
                if not self.virtual:
                    self.healthBar.setColor(1, 1, 1, 1)
                    self.healthBarGlow.setColor(1, 1, 1, 1)
                blinkTask = Task.loop(Task(self.__pulseRed), Task.pause(0.75), Task(self.__pulseGray), Task.pause(0.1))
                taskMgr.add(blinkTask, self.uniqueName('blink-task'))
            elif condition == 11:
                taskMgr.remove(self.uniqueName('pulse-task'))
                taskMgr.remove(self.uniqueName('blink-task'))
                if not self.virtual:
                    self.healthBar.setColor(1, 1, 1, 1)
                    self.healthBarGlow.setColor(1, 1, 1, 1)
                blinkTask = Task.loop(Task(self.__pulseRed), Task.pause(0.25), Task(self.__pulseGray), Task.pause(0.1))
                taskMgr.add(blinkTask, self.uniqueName('blink-task'))
            elif condition == 13:
                taskMgr.remove(self.uniqueName('blink-task'))
                taskMgr.remove(self.uniqueName('pulse-task'))
                if not self.virtual:
                    self.healthBar.setColor(1, 1, 1, 1)
                    self.healthBarGlow.setColor(1, 1, 1, 1)
                blinkTask = Task.loop(Task(self.__pulsePurple), Task.pause(1), Task(self.__pulsePurpleColor), Task.pause(3))
                taskMgr.add(blinkTask, self.uniqueName('pulse-task'))
            else:
                taskMgr.remove(self.uniqueName('pulse-task'))
                taskMgr.remove(self.uniqueName('blink-task'))
                if not self.virtual:
                    self.healthBar.setColor(1, 1, 1, 1)
                    self.healthBarGlow.setColor(1, 1, 1, 1)
                else:
                    self.healthBarGlow.setColor(0, 0, 0, 0)
                    if not self.style.name == 'hrollers':
                        self.virtualize(condition)
                self.__changeColor()
            self.healthCondition = condition

    def checkDeath(self):
        if self.healthCondition == 11:
            return 1
        else:
            return 0

    def __blinkRed(self, task):
        if not self.virtual:
            self.healthBar.setColor(self.healthColors[9], 1)
            self.healthBarGlow.setColor(self.healthGlowColors[9], 1)
        elif not self.style.name == 'hrollers':
            self.healthBarGlow.setColor(0, 0, 0, 0)
            self.virtualize(9)
        else:
            self.virtualize(9)

    def __blinkGray(self, task):
        if not self.virtual:
            self.healthBar.setColor(self.healthColors[10], 1)
            self.healthBarGlow.setColor(self.healthGlowColors[10], 1)
        elif not self.style.name == 'hrollers':
            self.healthBarGlow.setColor(0, 0, 0, 0)
            self.virtualize(10)
        else:
            self.virtualize(10)

    def __pulseRed(self, task):
        if not self.virtual:
            self.interval = Parallel(LerpColorScaleInterval(self.healthBar, duration=0, colorScale=(1, 0, 0, 1),
                                   blendType='easeInOut'))
            self.glowInterval = Parallel(LerpColorScaleInterval(self.healthBarGlow, duration=0, colorScale=(1, 0, 0, 1),
                                   blendType='easeInOut'))
            self.interval.start()
            self.glowInterval.start()
        else:
            self.healthBarGlow.setColor(0, 0, 0, 0)
            if self.style.name == 'hrollers':
                if self.getActualLevel() == 36:
                    self.virtualize(22)
                elif self.getActualLevel() == 35:
                    self.virtualize(21)
                elif self.getActualLevel() == 34:
                    self.virtualize(20)
                elif self.getActualLevel() == 33:
                    self.virtualize(19)
                elif self.getActualLevel() == 32:
                    self.virtualize(13)
                elif self.getActualLevel() == 31:
                    self.virtualize(12)
                elif self.getActualLevel() == 30:
                    self.virtualize(14)
                elif self.getActualLevel() == 29:
                    self.virtualize(8)
                elif self.getActualLevel() == 28:
                    self.virtualize(15)
                elif self.getActualLevel() == 27:
                    self.virtualize(3)
                elif self.getActualLevel() == 26:
                    self.virtualize(7)
                else:
                    self.virtualize(0)
            else:
                self.virtualizeRed(9)

    def __pulseWhite(self):
        if not self.virtual:
            self.interval = Parallel(LerpColorScaleInterval(self.healthBar, duration=0, colorScale=(1, 1, 1, 1),
                                   blendType='easeInOut'))
            self.glowInterval = Parallel(LerpColorScaleInterval(self.healthBarGlow, duration=0, colorScale=(1, 1, 1, 1),
                                   blendType='easeInOut'))
            self.interval.start()
            self.glowInterval.start()
        else:
            self.healthBarGlow.setColor(0, 0, 0, 0)
            if not self.style.name == 'hrollers':
                self.virtualizeRed(9)

    def __pulseGray(self, task):
        if not self.virtual:
            self.interval = Parallel(LerpColorScaleInterval(self.healthBar, duration=0, colorScale=(0.3, 0.3, 0.3, 1),
                                   blendType='easeInOut'))
            self.glowInterval = Parallel(LerpColorScaleInterval(self.healthBarGlow, duration=0, colorScale=(0, 0, 0, 0),
                                   blendType='easeInOut'))
            self.interval.start()
            self.glowInterval.start()
        else:
            self.healthBarGlow.setColor(0, 0, 0, 0)
            self.virtualizeGray(10)

    def __pulsePurple(self, task):
        if not self.virtual:
            self.interval = Parallel(LerpColorScaleInterval(self.healthBar, duration=1, colorScale=Vec4(0.729, 0.322, 1, 1.0),
                                   blendType='easeInOut'))
            self.glowInterval = Parallel(LerpColorScaleInterval(self.healthBarGlow, duration=1, colorScale=Vec4(0.729, 0.322, 1, 1.0),
                                   blendType='easeInOut'))
            self.interval.start()
            self.glowInterval.start()
        else:
            self.healthBarGlow.setColor(0, 0, 0, 0)
            if not self.style.name == 'hrollers':
                self.virtualizePurple(17)

    def __changeColor(self):
        if self.isImmortal and not self.style.name == 'hroller' and not self.style.name == 'hroller2':
            self.interval = Parallel(LerpColorScaleInterval(self.healthBar, duration=1, colorScale=(1, 1, 1, 1),
                                   blendType='easeInOut'))
            self.glowInterval = Parallel(LerpColorScaleInterval(self.healthBarGlow, duration=1, colorScale=(1, 1, 1, 1),
                                   blendType='easeInOut'))
            self.interval.start()
            self.glowInterval.start()
        elif not self.virtual:
            self.interval = Parallel(LerpColorScaleInterval(self.healthBar, duration=1, colorScale=(self.healthColors[self.condition]),
                                   blendType='easeInOut'))
            self.glowInterval = Parallel(LerpColorScaleInterval(self.healthBarGlow, duration=1, colorScale=(self.healthColors[self.condition]),
                                   blendType='easeInOut'))
            self.interval.start()
            self.glowInterval.start()
        else:
            self.healthBarGlow.setColor(0, 0, 0, 0)
            if not self.style.name == 'hrollers':
                self.virtualize(self.condition)

    def __pulsePurpleColor(self, task):
        if not self.virtual:
            self.interval = Parallel(LerpColorScaleInterval(self.healthBar, duration=1, colorScale=(self.healthColors[13]),
                                   blendType='easeInOut'))
            self.glowInterval = Parallel(LerpColorScaleInterval(self.healthBarGlow, duration=1, colorScale=(self.healthGlowColors[13]),
                                   blendType='easeInOut'))
            self.interval.start()
            self.glowInterval.start()
        else:
            self.healthBarGlow.setColor(0, 0, 0, 0)
            if not self.style.name == 'hrollers':
                self.virtualizePurpleColor(13)

    def removeHealthBar(self):
        if self.healthBar:
            self.healthBar.removeNode()
            self.healthBar = None

        if self.healthCondition == 10 or self.healthCondition == 11:
            taskMgr.remove(self.uniqueName('blink-task'))

        self.healthCondition = 0

    def removeHealthBarDisplay(self):
        if self.healthBarDisplay:
            self.healthBarDisplay.removeNode()
            self.healthBarDisplay = None

        self.healthCondition = 0

    def virtualize(self, condition):
        #self.healthCondition = 0
        actorNode = self.find('**/__Actor_modelRoot')
        actorCollection = actorNode.findAllMatches('*')
        parts = ()
        for thingIndex in range(0, actorCollection.getNumPaths()):
            thing = actorCollection[thingIndex]
            if thing.getName() not in ('joint_attachMeter', 'joint_shadow', 'joint_nameTag', 'def_nameTag'):
                thing.setColor(1, 1, 1, 1)
                self.interval = Parallel(
                    LerpColorScaleInterval(thing, duration=0, colorScale=(self.healthColors[condition]),
                                           blendType='easeInOut'))
                self.interval.start()
                thing.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd))
                thing.setDepthWrite(False)
                thing.setBin('fixed', 1)

    def virtualize3(self, condition):
        #self.healthCondition = 0
        actorNode = self.find('**/__Actor_modelRoot')
        actorCollection = actorNode.findAllMatches('*')
        parts = ()
        for thingIndex in range(0, actorCollection.getNumPaths()):
            thing = actorCollection[thingIndex]
            if thing.getName() not in ('joint_attachMeter', 'joint_shadow', 'joint_nameTag', 'def_nameTag'):
                thing.setColor(1, 1, 1, 1)
                self.interval = Parallel(
                    LerpColorScaleInterval(thing, duration=0, colorScale=(self.healthColors[condition]),
                                           blendType='easeInOut'))
                self.interval.start()
                thing.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd))
                thing.setDepthWrite(False)
                thing.setBin('fixed', 1)

    def virtualizePurple(self, condition):
        #self.healthCondition = 0
        actorNode = self.find('**/__Actor_modelRoot')
        actorCollection = actorNode.findAllMatches('*')
        parts = ()
        for thingIndex in range(0, actorCollection.getNumPaths()):
            thing = actorCollection[thingIndex]
            if thing.getName() not in ('joint_attachMeter', 'joint_shadow', 'joint_nameTag', 'def_nameTag'):
                thing.setColor(1, 1, 1, 1)
                self.interval = Parallel(
                    LerpColorScaleInterval(thing, duration=2, colorScale=(0.702, 0, 1, 1),
                                           blendType='easeInOut'))
                self.interval.start()
                thing.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd))
                thing.setDepthWrite(False)
                thing.setBin('fixed', 1)

    def virtualizePurpleColor(self, condition):
        #self.healthCondition = 0
        actorNode = self.find('**/__Actor_modelRoot')
        actorCollection = actorNode.findAllMatches('*')
        parts = ()
        for thingIndex in range(0, actorCollection.getNumPaths()):
            thing = actorCollection[thingIndex]
            if thing.getName() not in ('joint_attachMeter', 'joint_shadow', 'joint_nameTag', 'def_nameTag'):
                thing.setColor(1, 1, 1, 1)
                self.interval = Parallel(
                    LerpColorScaleInterval(thing, duration=2, colorScale=(self.healthColors[13]),
                                           blendType='easeInOut'))
                self.interval.start()
                thing.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd))
                thing.setDepthWrite(False)
                thing.setBin('fixed', 1)

    def virtualizeGray(self, condition):
        #self.healthCondition = 0
        actorNode = self.find('**/__Actor_modelRoot')
        actorCollection = actorNode.findAllMatches('*')
        parts = ()
        for thingIndex in range(0, actorCollection.getNumPaths()):
            thing = actorCollection[thingIndex]
            if thing.getName() not in ('joint_attachMeter', 'joint_shadow', 'joint_nameTag', 'def_nameTag'):
                thing.setColor(1, 1, 1, 1)
                self.interval = Parallel(
                    LerpColorScaleInterval(thing, duration=0, colorScale=(0.3, 0.3, 0.3, 1),
                                           blendType='easeInOut'))
                self.interval.start()
                thing.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd))
                thing.setDepthWrite(False)
                thing.setBin('fixed', 1)

    def virtualizeRed(self, condition):
        #self.healthCondition = 0
        actorNode = self.find('**/__Actor_modelRoot')
        actorCollection = actorNode.findAllMatches('*')
        parts = ()
        for thingIndex in range(0, actorCollection.getNumPaths()):
            thing = actorCollection[thingIndex]
            if thing.getName() not in ('joint_attachMeter', 'joint_shadow', 'joint_nameTag', 'def_nameTag'):
                thing.setColor(1, 1, 1, 1)
                self.interval = Parallel(
                    LerpColorScaleInterval(thing, duration=0, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'))
                self.interval.start()
                thing.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd))
                thing.setDepthWrite(False)
                thing.setBin('fixed', 1)

    def virtualize2(self, condition):
        #self.healthCondition = 0
        actorNode = self.find('**/__Actor_modelRoot')
        actorCollection = actorNode.findAllMatches('*')
        parts = ()
        for thingIndex in range(0, actorCollection.getNumPaths()):
            thing = actorCollection[thingIndex]
            if thing.getName() not in ('joint_attachMeter', 'joint_shadow', 'joint_nameTag', 'def_nameTag'):
                thing.setColor(0, 1, 0.063, 1)
                thing.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd))
                thing.setDepthWrite(False)
                thing.setBin('fixed', 1)

    def makeVirtual(self, isVirtual = 1):
        self.removeHealthBar()
        self.isVirtual = 1
        self.virtual = isVirtual
        if self.virtual:
            self.virtualize2(0)

    def makeVirtual2(self, isVirtual = 1):
        self.removeHealthBar()
        self.isVirtual = 1
        self.virtual = isVirtual
        if self.virtual:
            self.virtualize2(0)

    def getLoseActor(self, headless=False):
        model = 'phase_5/models/char/cog' + string.upper(self.style.body) + '_robot-zero'
        anims = self.generateAnimDict()
        anim = self.getCurrentAnim()
        dept = self.style.dept
        self.removePart('modelRoot')
        self.removePart('head')
        self.generateSkeletonBody()
        self.loadAnims(anims)
        self.generateSkeletonHealthBar()
        # self.generateHPBase()
        # self.generateCorporateMedallion()
        self.generateCorporateMedallion3()
        # self.generateCorporateTie()
        self.setSuitClothesSkeleton()
        self.setHeight(self.height)
        self.setBlend(frameBlend=base.wantSmoothAnims)
        self.setLODAnimation(base.lodMaxRange, base.lodMinRange, base.lodDelayFactor)
        parts = self.findAllMatches('**/pPlane*')
        for partNum in xrange(0, parts.getNumPaths()):
            bb = parts.getPath(partNum)
            bb.setTwoSided(1)

        # self.setName(TTLocalizer.SuitBaseNameWithLevelMgr)
        self.leftHand = self.find('**/joint_Lhold')
        self.rightHand = self.find('**/joint_Rhold')
        self.shadowJoint = self.find('**/joint_shadow')
        self.nametagNull = self.find('**/joint_nameTag')

        self.isSkeleton = 1

    def cleanupLoseActor(self):
        self.notify.debug('cleanupLoseActor()')
        if self.loseActor != None:
            self.notify.debug('cleanupLoseActor() - got one')
            self.loseActor.cleanup()

        self.loseActor = None


    def cleanupZapActor(self):
        self.notify.debug('cleanupLoseActor()')
        if self.zapActor != None:
            self.notify.debug('cleanupLoseActor() - got one')
            self.zapActor.cleanup()

        self.zapActor = None

    def getZapActor(self):
        model = 'phase_5/models/char/cog%s_robot-zero' % string.upper(self.style.body)
        anims = self.generateAnimDict()
        self.zapActor = Actor.Actor(model, anims)

        self.zapActor.setBlend(frameBlend=base.wantSmoothAnims)
        self.zapActor.setLODAnimation(base.lodMaxRange, base.lodMinRange, base.lodDelayFactor)
        if self.style.body == 'a' and self.style.name == 'derrhand':
            self.zapActorHeadParts = []
            self.generateHeadZap('derrickhand_skele', animated=True, targetActor=self.zapActor)
            texture = loader.loadTexture('phase_12/maps/ttcc_ene_derrickhand_skelecog.png')
            for headPart in self.zapActorHeadParts:
                headPart.setTexture(texture, 1)
                headPart.setZ(0)
                headPart.setY(0)
                headPart.setX(0)
                headPart.setR(0)
                headPart.setH(0)
                headPart.setScale(1)
        if self.style.body == 'a' and self.style.name == 'dold':
            #self.generateDOLDHead()
            self.zapActorHeadParts = []
            self.generateHeadZap('dold', animated=True, targetActor=self.zapActor)
            texture = loader.loadTexture('phase_14/maps/ttcc_ene_dold_skelecog.png')
            for headPart in self.zapActorHeadParts:
                headPart.setTexture(texture, 1)
            self.zapActorHeadParts = []
            self.generateHeadZap('skullA', animated=True, targetActor=self.zapActor)
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_dold.png')
            for headPart in self.zapActorHeadParts:
                headPart.setTexture(texture, 1)
                headPart.setZ(0)
                headPart.setY(0)
                headPart.setX(0)
                headPart.setR(0)
                headPart.setH(0)
                headPart.setScale(1)
        if self.style.body == 'a' and self.style.name == 'radiog':
            self.zapActorHeadParts = []
            self.generateHeadZap('dopa', animated=True, targetActor=self.zapActor)
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_radiog.png')
            for headPart in self.zapActorHeadParts:
                headPart.setTexture(texture, 1)
                headPart.setZ(0)
                headPart.setY(0)
                headPart.setX(0)
                headPart.setR(0)
                headPart.setH(0)
                headPart.setScale(1.2)
        if self.style.body == 'a' and self.style.name == 'cdirector':
            self.generateHeadZap('chainsaw_c', animated=True, targetActor=self.zapActor)
            texture = loader.loadTexture('phase_12/maps/ttcc_ene_chainsaw_boardbot.png')
            for headPart in self.zapActorHeadParts:
                headPart.setTexture(texture, 1)
                headPart.setZ(0)
                headPart.setY(0)
                headPart.setX(0)
                headPart.setR(0)
                headPart.setH(0)
                headPart.find('**/Hat').hide()
        if self.style.body == 'a' and self.style.name == 'autocad':
            self.zapActorHeadParts = []
            self.generateHeadZap('autocaddie', animated=True, targetActor=self.zapActor)
            for headPart in self.zapActorHeadParts:
                headPart.setZ(0)
                headPart.setY(0)
                headPart.setX(0)
                headPart.setR(0)
                headPart.setH(0)
                headPart.setScale(1)
        if self.style.body == 'a' and self.style.name == 'clubpres':
            self.zapActorHeadParts = []
            self.generateHeadZap('autocaddie', animated=True, targetActor=self.zapActor)
            #texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_c_exe.png')
            for headPart in self.zapActorHeadParts:
                headPart.setZ(0)
                headPart.setY(0)
                headPart.setX(0)
                headPart.setR(0)
                headPart.setH(0)
                headPart.setScale(1)
                #headModel.find('**/head').setTexture(texture, 1)
        if self.style.body == 'a' and self.style.name == 'ubuster':
            self.zapActorHeadParts = []
            self.generateHeadZap('dopr', animated=True, targetActor=self.zapActor)
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_ubuster.png')
            for headPart in self.zapActorHeadParts:
                headPart.setZ(0)
                headPart.setTexture(texture, 1)
                headPart.setY(0)
                headPart.setX(0)
                headPart.setR(0)
                headPart.setH(0)
                headPart.setScale(1.3)
        if self.style.body == 'a' and self.style.name == 'ambass':
            self.zapActorHeadParts = []
            self.generateHeadZap('prethinker2', animated=True, targetActor=self.zapActor)
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_ambassador.png')
            for headPart in self.zapActorHeadParts:
                headPart.setTexture(texture, 1)
                textureGlass = loader.loadTexture('phase_9/maps/ttcc_ene_prethinker_glass.png')
                headPart.find('**/glass').setTexture(textureGlass, 1)
                headPart.find('**/brain').hide()
                headPart.setScale(1)
                headPart.setZ(-.3)
        if self.style.body == 'a' and not self.style.name == 'autocad' and not self.style.name == 'ubuster' and not self.style.name == 'dold' and not self.style.name == 'derrhand' and not self.style.name == 'ambass' and not self.style.name == 'cdirector' and not self.style.name == 'clubpres' and not self.style.name == 'radiog':
            self.zapActorHeadParts = []
            self.generateHeadZap('skullA', animated=True, targetActor=self.zapActor)
            if self.isExecutive or self.isManager:
                texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_exe.png' %
                                             self.style.dept)
            elif self.isGovernaught:
                texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_gov.png' %
                                        self.style.dept)
            else:
                texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s.png' %
                                        self.style.dept)
            for headPart in self.zapActorHeadParts:
                headPart.setTexture(texture, 1)
                headPart.setZ(0)
                headPart.setY(0)
                headPart.setX(0)
                headPart.setR(0)
                headPart.setH(0)
                headPart.setScale(1)
        if self.style.body == 'b':
            self.zapActorHeadParts = []
            self.generateHeadZap('skullB', animated=True, targetActor=self.zapActor)
            if self.isExecutive or self.isManager:
                texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_exe.png' %
                                             self.style.dept)
            elif self.isGovernaught:
                texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_gov.png' %
                                        self.style.dept)
            else:
                texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s.png' %
                                        self.style.dept)
            for headPart in self.zapActorHeadParts:
                headPart.setTexture(texture, 1)
                headPart.setZ(0)
                headPart.setY(0)
                headPart.setX(0)
                headPart.setR(0)
                headPart.setH(0)
                headPart.setScale(1)
        if self.style.body == 'c' and self.style.name == 'dopa':
            self.zapActorHeadParts = []
            self.generateHeadZap('dopa', animated=True, targetActor=self.zapActor)
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_dopa.png')
            for headPart in self.zapActorHeadParts:
                headPart.setTexture(texture, 1)
                headPart.setZ(0)
                headPart.setY(0)
                headPart.setX(0)
                headPart.setR(0)
                headPart.setH(0)
                headPart.setScale(1)
        if self.style.body == 'c' and self.style.name == 'dopr':
            self.zapActorHeadParts = []
            self.generateHeadZap('dopr', animated=True, targetActor=self.zapActor)
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_dopr.png')
            for headPart in self.zapActorHeadParts:
                headPart.setTexture(texture, 1)
                headPart.setZ(0)
                headPart.setY(0)
                headPart.setX(0)
                headPart.setR(0)
                headPart.setH(0)
                headPart.setScale(1)
        if self.style.body == 'c' and not self.style.name == 'dopa' and not self.style.name == 'dopr':
            self.zapActorHeadParts = []
            self.generateHeadZap('skullC', animated=True, targetActor=self.zapActor)
            if self.isExecutive or self.isManager:
                texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_exe.png' %
                                             self.style.dept)
            elif self.isGovernaught:
                texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_gov.png' %
                                        self.style.dept)
            else:
                texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s.png' %
                                        self.style.dept)
            for headPart in self.zapActorHeadParts:
                headPart.setTexture(texture, 1)
                headPart.setZ(0)
                headPart.setY(0)
                headPart.setX(0)
                headPart.setR(0)
                headPart.setH(0)
                headPart.setScale(1)

        parts = self.zapActor.findAllMatches('**/pPlane*')
        for partNum in xrange(parts.getNumPaths()):
            parts.getPath(partNum).setTwoSided(1)

        # Hands / joints on zap actor
        self.zapActor.leftHand = self.zapActor.find('**/joint_Lhold')
        self.zapActor.rightHand = self.zapActor.find('**/joint_Rhold')
        self.zapActor.shadowJoint = self.zapActor.find('**/joint_shadow')
        self.zapActor.nametagNull = self.zapActor.find('**/joint_nameTag')

        # Shadow
        dropShadow = loader.loadModel('phase_3/models/props/drop_shadow')
        dropShadow.setScale(0.45)
        dropShadow.setColor(0.0, 0.0, 0.0, 0.5)
        dropShadow.reparentTo(self.zapActor.shadowJoint)

        # Body texture
        texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s.png' % self.style.dept)

        if self.isWaiter:
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_waiter.png')
        elif self.style.dept == 'c' and not self.getExecutive() and not self.isManager and not self.getGovernaught() and not self.isWaiter:
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s.png' % self.style.dept)
        elif self.isExecutive and not self.isWaiter or self.isManager or self.getExecutive():
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_exe.png' % self.style.dept)
        elif self.getGovernaught() and not self.isWaiter:
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_gov.png' % self.style.dept)
        elif self.isManager and not self.isWaiter and self.style.name != 'dold':
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_exe.png' % self.style.dept)
        elif self.style.name == 'dold':
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_dold.png')

        body = self.zapActor.find('**/body')
        if not body.isEmpty():
            body.setTexture(texture, 1)

        meter = self.zapActor.find('**/emblem_healthmeter')
        if not meter.isEmpty():
            meter.show()

        modelRoot = self.zapActor
        modelRoot.find('**/necktie-s').hide()
        modelRoot.find('**/necktie-w').hide()
        modelRoot.find('**/bowtie').hide()
        modelRoot.find('**/necktie-s').setTexture(texture, 1)
        modelRoot.find('**/bowtie').setTexture(texture, 1)
        if self.style.name == 'wsi':
            textureWSI = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s.png' % self.style.dept)
            modelRoot.find('**/necktie-w').setTexture(textureWSI, 1)
        else:
            modelRoot.find('**/necktie-w').setTexture(texture, 1)
        if self.isWaiter:
            modelRoot.find('**/bowtie').show()
        elif self.style.dept == 'l' and not self.style.name == 'wsi':
            modelRoot.find('**/bowtie').show()
        elif self.style.dept == 's':
            modelRoot.find('**/necktie-s').show()
        elif self.style.name == 'wsi':
            modelRoot.find('**/bowtie').hide()
            modelRoot.find('**/necktie-w').show()
            textureWSI = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s.png' % self.style.dept)
            modelRoot.find('**/necktie-w').setTexture(textureWSI, 1)
        elif self.style.name == 'hydra':
            modelRoot.find('**/bowtie').show()
            modelRoot.setColor((0.729, 0.729, 0.729, 1))
            modelRoot.find('**/bowtie').setColor((0.741, 0.82, 0.769, 1))
        elif self.style.name == 'charon':
            modelRoot.find('**/necktie-w').hide()
            modelRoot.find('**/necktie-s').show()
            modelRoot.setColor((0.51, 0.49, 0.467, 1))
            modelRoot.find('**/necktie-s').setColor((0.741, 0.82, 0.769, 1))
        elif self.style.name == 'nix':
            modelRoot.find('**/necktie-w').show()
            modelRoot.setColor((0.6, 0.6, 0.6, 1))
            modelRoot.find('**/necktie-w').setColor((0.741, 0.82, 0.769, 1))
        elif self.style.name == 'styx':
            modelRoot.find('**/necktie-w').show()
            modelRoot.setColor((0.671, 0.671, 0.671, 1))
            modelRoot.find('**/necktie-w').setColor((0.741, 0.82, 0.769, 1))
        elif self.style.name == 'kerberos':
            modelRoot.find('**/necktie-w').show()
            modelRoot.setColor((0.62, 0.659, 0.624, 1))
            modelRoot.find('**/necktie-w').setColor((0.741, 0.82, 0.769, 1))
        elif self.style.name == 'rainmake':
            modelRoot.find('**/necktie-w').hide()
            modelRoot.find('**/bowtie').hide()
            modelRoot.find('**/necktie-s').hide()
        # elif self.style.name == 'liquid':
        #     modelRoot.find('**/necktie-w').hide()
        #     modelRoot.find('**/bowtie').hide()
        #     modelRoot.find('**/necktie-s').hide()
        elif self.style.name == 'racket':
            modelRoot.find('**/necktie-w').hide()
            modelRoot.find('**/bowtie').hide()
            modelRoot.find('**/necktie-s').hide()
        elif self.style.name == 'erfit':
            modelRoot.find('**/necktie-w').hide()
            modelRoot.find('**/bowtie').hide()
            modelRoot.find('**/necktie-s').hide()
        elif self.style.name == 'erclaim':
            modelRoot.find('**/necktie-w').hide()
            modelRoot.find('**/bowtie').hide()
            modelRoot.find('**/necktie-s').hide()
        elif self.style.name == 'hrollers':
            modelRoot.find('**/necktie-w').hide()
            modelRoot.find('**/bowtie').hide()
            modelRoot.find('**/necktie-s').hide()
        elif self.style.name == 'hroller2':
            modelRoot.find('**/necktie-w').hide()
            modelRoot.find('**/bowtie').hide()
            modelRoot.find('**/necktie-s').hide()
        elif self.style.name == 'hroller':
            modelRoot.find('**/necktie-w').hide()
            modelRoot.find('**/bowtie').hide()
            modelRoot.find('**/necktie-s').hide()
        elif self.style.name == 'bellring':
            modelRoot.find('**/necktie-w').hide()
            modelRoot.find('**/bowtie').hide()
            modelRoot.find('**/necktie-s').hide()
        elif self.style.name == 'psetter' or self.style.name == 'hustle':
            modelRoot.find('**/necktie-w').hide()
            modelRoot.find('**/bowtie').hide()
            modelRoot.find('**/necktie-s').hide()
        elif self.style.name == 'ins':
            modelRoot.find('**/necktie-w').hide()
            modelRoot.find('**/bowtie').hide()
            modelRoot.find('**/necktie-s').hide()
        elif self.style.name == 'dking':
            modelRoot.find('**/necktie-w').hide()
            modelRoot.find('**/bowtie').hide()
            modelRoot.find('**/necktie-s').hide()
        elif self.style.name == 'ddiver':
            modelRoot.find('**/necktie-w').hide()
            modelRoot.find('**/bowtie').hide()
            modelRoot.find('**/necktie-s').hide()
        elif self.style.name == 'gatekeep':
            modelRoot.find('**/necktie-w').hide()
            modelRoot.find('**/bowtie').hide()
            modelRoot.find('**/necktie-s').hide()
        elif self.style.name == 'wsi':
            modelRoot.find('**/bowtie').hide()
            modelRoot.find('**/necktie-s').hide()
        elif self.style.name == 'ovt':
            modelRoot.find('**/bowtie').show()
        else:
            modelRoot.find('**/necktie-w').show()
        # Head textures
        textureDerrick = loader.loadTexture('phase_12/maps/ttcc_ene_derrickhand_skelecog.png')
        textureDopa = loader.loadTexture('phase_9/maps/ttcc_ene_dopa.png')
        textureDold = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_dold.png')
        textureRadio = loader.loadTexture('phase_9/maps/ttcc_ene_radiog.png')
        textureUnion = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_dold.png')
        textureDopr = loader.loadTexture('phase_9/maps/ttcc_ene_ubuster.png')
        textureAmbassador = loader.loadTexture('phase_9/maps/ttcc_ene_ambassador.png')
        textureDirector = loader.loadTexture('phase_12/maps/ttcc_ene_chainsaw_boardbot.png')

        headParts = self.zapActor.findAllMatches('**/joint_head*')
        for i in xrange(headParts.getNumPaths()):
            headPart = headParts.getPath(i)

            if self.style.name == 'derrhand':
                headPart.setTexture(textureDerrick, 1)
            elif self.style.name == 'ubuster':
                headPart.setTexture(textureUnion, 1)
            elif self.style.name == 'dold':
                headPart.setTexture(textureDold, 1)
            elif self.style.name == 'radiog':
                headPart.setTexture(textureRadio, 1)
            elif self.style.name == 'cdirector':
                headPart.setTexture(textureDirector, 1)
            elif self.style.name == 'dopa':
                headPart.setTexture(textureDopa, 1)
            elif self.style.name == 'ambass':
                headPart.setTexture(textureAmbassador, 1)
            else:
                headPart.setTexture(texture, 1)

        # Clothes / tie if needed
        try:
            self.generateCorporateTie(self.zapActor)
        except:
            pass

        # Display name
        dept = self.getStyleDept()
        level = str(self.getActualLevel())

        if self.getExecutive():
            level += TTLocalizer.ExecutivePostFix
        if self.getManager():
            level += TTLocalizer.ManagerPostFix
        if self.getGovernaught():
            level += TTLocalizer.GovernaughtPostFix

        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {
            'name': self.name,
            'dept': dept,
            'level': level
        }

        try:
            self.zapActor.setDisplayName(nameInfo)
        except:
            pass

        self.zapActor.setScale(self.scale)
        self.zapActor.setPos(self.getPos())
        self.zapActor.setHpr(self.getHpr())

        return self.zapActor
    
    def cleanupZapActorPowerhouse(self):
        self.notify.debug('cleanupLoseActor()')
        if self.zapActorPowerhouse != None:
            self.notify.debug('cleanupLoseActor() - got one')
            self.zapActorPowerhouse.cleanup()

        self.zapActorPowerhouse = None

    def getZapActorPowerhouse(self):
        model = 'phase_5/models/char/cog%s_robot-zero' % string.upper(self.style.body)
        anims = self.generateAnimDict()

        self.zapActorPowerhouse = Actor.Actor(model, anims)

        self.zapActorPowerhouse.setBlend(frameBlend=base.wantSmoothAnims)
        self.zapActorPowerhouse.setLODAnimation(
            base.lodMaxRange,
            base.lodMinRange,
            base.lodDelayFactor
        )

        def resetPowerhouseHeadParts():
            self.zapActorHeadParts = []

        def applyHeadPartDefaults(scale=1):
            for headPart in self.zapActorHeadParts:
                headPart.setZ(0)
                headPart.setY(0)
                headPart.setX(0)
                headPart.setR(0)
                headPart.setH(0)
                headPart.setScale(scale)

        if self.style.body == 'a' and self.style.name == 'derrhand':
            resetPowerhouseHeadParts()
            self.generateHeadZap('derrickhand_skele', animated=True, targetActor=self.zapActorPowerhouse)
            texture = loader.loadTexture('phase_12/maps/ttcc_ene_derrickhand_skelecog.png')
            for headPart in self.zapActorHeadParts:
                headPart.setTexture(texture, 1)
            applyHeadPartDefaults()

        if self.style.body == 'a' and self.style.name == 'dold':
            resetPowerhouseHeadParts()
            self.generateHeadZap('dold', animated=True, targetActor=self.zapActorPowerhouse)
            texture = loader.loadTexture('phase_14/maps/ttcc_ene_dold_skelecog.png')
            for headPart in self.zapActorHeadParts:
                headPart.setTexture(texture, 1)

            resetPowerhouseHeadParts()
            self.generateHeadZap('skullA', animated=True, targetActor=self.zapActorPowerhouse)
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_dold.png')
            for headPart in self.zapActorHeadParts:
                headPart.setTexture(texture, 1)
            applyHeadPartDefaults()

        if self.style.body == 'a' and self.style.name == 'radiog':
            resetPowerhouseHeadParts()
            self.generateHeadZap('dopa', animated=True, targetActor=self.zapActorPowerhouse)
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_dopa.png')
            for headPart in self.zapActorHeadParts:
                headPart.setTexture(texture, 1)
            applyHeadPartDefaults(scale=1.2)

        if self.style.body == 'a' and self.style.name == 'cdirector':
            resetPowerhouseHeadParts()
            self.generateHeadZap('chainsaw_c', animated=True, targetActor=self.zapActorPowerhouse)
            texture = loader.loadTexture('phase_12/maps/ttcc_ene_chainsaw_boardbot.png')
            for headPart in self.zapActorHeadParts:
                headPart.setTexture(texture, 1)
                headPart.find('**/Hat').hide()
            applyHeadPartDefaults(scale=1.0)

        if self.style.body == 'a' and self.style.name == 'autocad':
            resetPowerhouseHeadParts()
            self.generateHeadZap('autocaddie', animated=True, targetActor=self.zapActorPowerhouse)
            applyHeadPartDefaults()

        if self.style.body == 'a' and self.style.name == 'clubpres':
            resetPowerhouseHeadParts()
            self.generateHeadZap('autocaddie', animated=True, targetActor=self.zapActorPowerhouse)
            applyHeadPartDefaults()

        if self.style.body == 'a' and self.style.name == 'ubuster':
            resetPowerhouseHeadParts()
            self.generateHeadZap('dopr', animated=True, targetActor=self.zapActorPowerhouse)
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_dopr.png')
            for headPart in self.zapActorHeadParts:
                headPart.setTexture(texture, 1)
            applyHeadPartDefaults(scale=1.3)

        if self.style.body == 'a' and self.style.name == 'ambass':
            resetPowerhouseHeadParts()
            self.generateHeadZap('prethinker2', animated=True, targetActor=self.zapActorPowerhouse)
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_ambassador.png')
            textureGlass = loader.loadTexture('phase_9/maps/ttcc_ene_prethinker_glass.png')

            for headPart in self.zapActorHeadParts:
                headPart.setTexture(texture, 1)
                headPart.find('**/glass').setTexture(textureGlass, 1)
                headPart.find('**/brain').hide()
                headPart.setScale(1)
                headPart.setZ(-0.3)

        if (
            self.style.body == 'a' and
            self.style.name not in ('autocad', 'ubuster', 'dold', 'derrhand', 'ambass', 'clubpres', 'radiog', 'cdirector')
        ):
            resetPowerhouseHeadParts()
            self.generateHeadZap('skullA', animated=True, targetActor=self.zapActorPowerhouse)

            if self.isExecutive or self.isManager:
                texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_exe.png' % self.style.dept)
            elif self.isGovernaught:
                texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_gov.png' % self.style.dept)
            else:
                texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s.png' % self.style.dept)

            for headPart in self.zapActorHeadParts:
                headPart.setTexture(texture, 1)
            applyHeadPartDefaults()

        if self.style.body == 'b':
            resetPowerhouseHeadParts()
            self.generateHeadZap('skullB', animated=True, targetActor=self.zapActorPowerhouse)

            if self.isExecutive or self.isManager:
                texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_exe.png' % self.style.dept)
            elif self.isGovernaught:
                texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_gov.png' % self.style.dept)
            else:
                texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s.png' % self.style.dept)

            for headPart in self.zapActorHeadParts:
                headPart.setTexture(texture, 1)
            applyHeadPartDefaults()

        if self.style.body == 'c' and self.style.name == 'dopa':
            resetPowerhouseHeadParts()
            self.generateHeadZap('dopa', animated=True, targetActor=self.zapActorPowerhouse)
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_dopa.png')

            for headPart in self.zapActorHeadParts:
                headPart.setTexture(texture, 1)
            applyHeadPartDefaults()

        if self.style.body == 'c' and self.style.name == 'dopr':
            resetPowerhouseHeadParts()
            self.generateHeadZap('dopr', animated=True, targetActor=self.zapActorPowerhouse)
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_dopr.png')

            for headPart in self.zapActorHeadParts:
                headPart.setTexture(texture, 1)
            applyHeadPartDefaults()

        if self.style.body == 'c' and self.style.name not in ('dopa', 'dopr'):
            resetPowerhouseHeadParts()
            self.generateHeadZap('skullC', animated=True, targetActor=self.zapActorPowerhouse)

            if self.isExecutive or self.isManager:
                texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_exe.png' % self.style.dept)
            elif self.isGovernaught:
                texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_gov.png' % self.style.dept)
            else:
                texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s.png' % self.style.dept)

            for headPart in self.zapActorHeadParts:
                headPart.setTexture(texture, 1)
            applyHeadPartDefaults()

        parts = self.zapActorPowerhouse.findAllMatches('**/pPlane*')
        for partNum in xrange(parts.getNumPaths()):
            parts.getPath(partNum).setTwoSided(1)

        self.zapActorPowerhouse.leftHand = self.zapActorPowerhouse.find('**/joint_Lhold')
        self.zapActorPowerhouse.rightHand = self.zapActorPowerhouse.find('**/joint_Rhold')
        self.zapActorPowerhouse.shadowJoint = self.zapActorPowerhouse.find('**/joint_shadow')
        self.zapActorPowerhouse.nametagNull = self.zapActorPowerhouse.find('**/joint_nameTag')

        dropShadow = loader.loadModel('phase_3/models/props/drop_shadow')
        dropShadow.setScale(0.45)
        dropShadow.setColor(0.0, 0.0, 0.0, 0.5)
        dropShadow.reparentTo(self.zapActorPowerhouse.shadowJoint)

        texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s.png' % self.style.dept)

        if self.isWaiter:
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_waiter.png')
        elif self.style.dept == 'c' and not self.getExecutive() and not self.getManager() and not self.getGovernaught() and not self.isWaiter:
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s.png' % self.style.dept)
        elif self.isExecutive and not self.isWaiter or self.getManager() or self.getExecutive():
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_exe.png' % self.style.dept)
        elif self.getManager() and not self.isWaiter and self.style.name != 'dold':
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_exe.png' % self.style.dept)
        elif self.style.name == 'dold':
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_dold.png')
        elif self.getGovernaught() and not self.isWaiter:
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_gov.png' % self.style.dept)

        body = self.zapActorPowerhouse.find('**/body')
        if not body.isEmpty():
            body.setTexture(texture, 1)

        meter = self.zapActorPowerhouse.find('**/emblem_healthmeter')
        if not meter.isEmpty():
            meter.show()

        modelRoot = self.zapActorPowerhouse

        modelRoot.find('**/necktie-s').hide()
        modelRoot.find('**/necktie-w').hide()
        modelRoot.find('**/bowtie').hide()

        modelRoot.find('**/necktie-s').setTexture(texture, 1)
        modelRoot.find('**/bowtie').setTexture(texture, 1)
        if self.style.name == 'wsi':
            textureWSI = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s.png' % self.style.dept)
            modelRoot.find('**/necktie-w').setTexture(textureWSI, 1)
        else:
            modelRoot.find('**/necktie-w').setTexture(texture, 1)

        if self.isWaiter:
            modelRoot.find('**/bowtie').show()
        elif self.style.dept == 'l' and self.style.name != 'wsi':
            modelRoot.find('**/bowtie').show()
        elif self.style.dept == 's':
            modelRoot.find('**/necktie-s').show()
        elif self.style.name == 'wsi':
            modelRoot.find('**/bowtie').hide()
            modelRoot.find('**/necktie-w').show()
            textureWSI = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s.png' % self.style.dept)
            modelRoot.find('**/necktie-w').setTexture(textureWSI, 1)
        elif self.style.name == 'hydra':
            modelRoot.find('**/bowtie').show()
            modelRoot.setColor((0.729, 0.729, 0.729, 1))
            modelRoot.find('**/bowtie').setColor((0.741, 0.82, 0.769, 1))
        elif self.style.name == 'charon':
            modelRoot.find('**/necktie-w').hide()
            modelRoot.find('**/necktie-s').show()
            modelRoot.setColor((0.51, 0.49, 0.467, 1))
            modelRoot.find('**/necktie-s').setColor((0.741, 0.82, 0.769, 1))
        elif self.style.name == 'nix':
            modelRoot.find('**/necktie-w').show()
            modelRoot.setColor((0.6, 0.6, 0.6, 1))
            modelRoot.find('**/necktie-w').setColor((0.741, 0.82, 0.769, 1))
        elif self.style.name == 'styx':
            modelRoot.find('**/necktie-w').show()
            modelRoot.setColor((0.671, 0.671, 0.671, 1))
            modelRoot.find('**/necktie-w').setColor((0.741, 0.82, 0.769, 1))
        elif self.style.name == 'kerberos':
            modelRoot.find('**/necktie-w').show()
            modelRoot.setColor((0.62, 0.659, 0.624, 1))
            modelRoot.find('**/necktie-w').setColor((0.741, 0.82, 0.769, 1))
        elif self.style.name == 'rainmake':
            pass
        elif self.style.name in (
            'racket', 'erfit', 'erclaim', 'hrollers', 'hroller2', 'hroller',
            'bellring', 'psetter', 'hustle', 'ins', 'dking', 'ddiver',
            'gatekeep'
        ):
            pass
        elif self.style.name == 'ovt':
            modelRoot.find('**/bowtie').show()
        else:
            modelRoot.find('**/necktie-w').show()

        textureDerrick = loader.loadTexture('phase_12/maps/ttcc_ene_derrickhand_skelecog.png')
        textureDopa = loader.loadTexture('phase_9/maps/ttcc_ene_dopa.png')
        textureDold = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_dold.png')
        textureDopr = loader.loadTexture('phase_9/maps/ttcc_ene_dopr.png')
        textureAmbassador = loader.loadTexture('phase_9/maps/ttcc_ene_ambassador.png')
        textureDirector = loader.loadTexture('phase_12/maps/ttcc_ene_chainsaw_boardbot.png')

        headParts = self.zapActorPowerhouse.findAllMatches('**/joint_head*')
        for i in xrange(headParts.getNumPaths()):
            headPart = headParts.getPath(i)

            if self.style.name == 'derrhand':
                headPart.setTexture(textureDerrick, 1)
            elif self.style.name == 'ubuster':
                headPart.setTexture(textureDopr, 1)
            elif self.style.name == 'dold':
                headPart.setTexture(textureDold, 1)
            elif self.style.name == 'radiog':
                headPart.setTexture(textureDopa, 1)
            elif self.style.name == 'cdirector':
                headPart.setTexture(textureDirector, 1)
            elif self.style.name == 'dopa':
                headPart.setTexture(textureDopa, 1)
            elif self.style.name == 'ambass':
                headPart.setTexture(textureAmbassador, 1)
            else:
                headPart.setTexture(texture, 1)

        try:
            self.generateCorporateTie(self.zapActorPowerhouse)
        except:
            pass

        dept = self.getStyleDept()
        level = str(self.getActualLevel())

        if self.getExecutive():
            level += TTLocalizer.ExecutivePostFix
        if self.getManager():
            level += TTLocalizer.ManagerPostFix
        if self.getGovernaught():
            level += TTLocalizer.GovernaughtPostFix

        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {
            'name': self.name,
            'dept': dept,
            'level': level
        }

        try:
            self.zapActorPowerhouse.setDisplayName(nameInfo)
        except:
            pass

        self.zapActorPowerhouse.setScale(self.scale)
        self.zapActorPowerhouse.setPos(self.getPos())
        self.zapActorPowerhouse.setHpr(self.getHpr())

        return self.zapActorPowerhouse

    def cleanupZapActorPowerhouseSquirt(self):
        self.notify.debug('cleanupZapActorPowerhouseSquirt()')
        if hasattr(self, 'zapActorPowerhouseSquirt') and self.zapActorPowerhouseSquirt:
            try:
                self.zapActorPowerhouseSquirt.cleanup()
                self.zapActorPowerhouseSquirt.removeNode()
            except:
                pass
        self.zapActorPowerhouseSquirt = None


    def cleanupZapActorPowerhouseZap(self):
        self.notify.debug('cleanupZapActorPowerhouseZap()')
        if hasattr(self, 'zapActorPowerhouseZap') and self.zapActorPowerhouseZap:
            try:
                self.zapActorPowerhouseZap.cleanup()
                self.zapActorPowerhouseZap.removeNode()
            except:
                pass
        self.zapActorPowerhouseZap = None


    def __makeZapActorPowerhouseVariant(self, attrName):
        model = 'phase_5/models/char/cog%s_robot-zero' % string.upper(self.style.body)
        anims = self.generateAnimDict()

        zapActor = Actor.Actor(model, anims)
        setattr(self, attrName, zapActor)

        zapActor.setBlend(frameBlend=base.wantSmoothAnims)
        zapActor.setLODAnimation(base.lodMaxRange, base.lodMinRange, base.lodDelayFactor)

        def resetPowerhouseHeadParts():
            self.zapActorHeadParts = []

        def applyHeadPartDefaults(scale=1):
            for headPart in self.zapActorHeadParts:
                headPart.setZ(0)
                headPart.setY(0)
                headPart.setX(0)
                headPart.setR(0)
                headPart.setH(0)
                headPart.setScale(scale)

        if self.style.body == 'a' and self.style.name == 'derrhand':
            resetPowerhouseHeadParts()
            self.generateHeadZap('derrickhand_skele', animated=True, targetActor=zapActor)
            texture = loader.loadTexture('phase_12/maps/ttcc_ene_derrickhand_skelecog.png')
            for headPart in self.zapActorHeadParts:
                headPart.setTexture(texture, 1)
            applyHeadPartDefaults()

        if self.style.body == 'a' and self.style.name == 'dold':
            resetPowerhouseHeadParts()
            self.generateHeadZap('dold', animated=True, targetActor=zapActor)
            texture = loader.loadTexture('phase_14/maps/ttcc_ene_dold_skelecog.png')
            for headPart in self.zapActorHeadParts:
                headPart.setTexture(texture, 1)

            resetPowerhouseHeadParts()
            self.generateHeadZap('skullA', animated=True, targetActor=zapActor)
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_dold.png')
            for headPart in self.zapActorHeadParts:
                headPart.setTexture(texture, 1)
            applyHeadPartDefaults()

        if self.style.body == 'a' and self.style.name == 'radiog':
            resetPowerhouseHeadParts()
            self.generateHeadZap('dopa', animated=True, targetActor=zapActor)
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_dopa.png')
            for headPart in self.zapActorHeadParts:
                headPart.setTexture(texture, 1)
            applyHeadPartDefaults(scale=1.2)

        if self.style.body == 'a' and self.style.name == 'cdirector':
            resetPowerhouseHeadParts()
            self.generateHeadZap('chainsaw_c', animated=True, targetActor=zapActor)
            texture = loader.loadTexture('phase_12/maps/ttcc_ene_chainsaw_boardbot.png')
            for headPart in self.zapActorHeadParts:
                headPart.setTexture(texture, 1)
                headPart.find('**/Hat').hide()
            applyHeadPartDefaults(scale=1.2)

        if self.style.body == 'a' and self.style.name == 'autocad':
            resetPowerhouseHeadParts()
            self.generateHeadZap('autocaddie', animated=True, targetActor=zapActor)
            applyHeadPartDefaults()

        if self.style.body == 'a' and self.style.name == 'clubpres':
            resetPowerhouseHeadParts()
            self.generateHeadZap('autocaddie', animated=True, targetActor=zapActor)
            applyHeadPartDefaults()

        if self.style.body == 'a' and self.style.name == 'ubuster':
            resetPowerhouseHeadParts()
            self.generateHeadZap('dopr', animated=True, targetActor=zapActor)
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_dopr.png')
            for headPart in self.zapActorHeadParts:
                headPart.setTexture(texture, 1)
            applyHeadPartDefaults(scale=1.3)

        if self.style.body == 'a' and self.style.name == 'ambass':
            resetPowerhouseHeadParts()
            self.generateHeadZap('prethinker2', animated=True, targetActor=zapActor)
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_ambassador.png')
            textureGlass = loader.loadTexture('phase_9/maps/ttcc_ene_prethinker_glass.png')

            for headPart in self.zapActorHeadParts:
                headPart.setTexture(texture, 1)
                headPart.find('**/glass').setTexture(textureGlass, 1)
                headPart.find('**/brain').hide()
                headPart.setScale(1)
                headPart.setZ(-0.3)

        if (
            self.style.body == 'a' and
            self.style.name not in ('autocad', 'dold', 'ubuster', 'derrhand', 'ambass', 'clubpres', 'radiog', 'cdirector')
        ):
            resetPowerhouseHeadParts()
            self.generateHeadZap('skullA', animated=True, targetActor=zapActor)

            if self.isExecutive or self.isManager:
                texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_exe.png' % self.style.dept)
            elif self.isGovernaught:
                texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_gov.png' % self.style.dept)
            else:
                texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s.png' % self.style.dept)

            for headPart in self.zapActorHeadParts:
                headPart.setTexture(texture, 1)
            applyHeadPartDefaults()

        if self.style.body == 'b':
            resetPowerhouseHeadParts()
            self.generateHeadZap('skullB', animated=True, targetActor=zapActor)

            if self.isExecutive or self.isManager:
                texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_exe.png' % self.style.dept)
            elif self.isGovernaught:
                texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_gov.png' % self.style.dept)
            else:
                texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s.png' % self.style.dept)

            for headPart in self.zapActorHeadParts:
                headPart.setTexture(texture, 1)
            applyHeadPartDefaults()

        if self.style.body == 'c' and self.style.name == 'dopa':
            resetPowerhouseHeadParts()
            self.generateHeadZap('dopa', animated=True, targetActor=zapActor)
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_dopa.png')

            for headPart in self.zapActorHeadParts:
                headPart.setTexture(texture, 1)
            applyHeadPartDefaults()

        if self.style.body == 'c' and self.style.name == 'dopr':
            resetPowerhouseHeadParts()
            self.generateHeadZap('dopr', animated=True, targetActor=zapActor)
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_dopr.png')

            for headPart in self.zapActorHeadParts:
                headPart.setTexture(texture, 1)
            applyHeadPartDefaults()

        if self.style.body == 'c' and self.style.name not in ('dopa', 'dopr'):
            resetPowerhouseHeadParts()
            self.generateHeadZap('skullC', animated=True, targetActor=zapActor)

            if self.isExecutive or self.isManager:
                texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_exe.png' % self.style.dept)
            elif self.isGovernaught:
                texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_gov.png' % self.style.dept)
            else:
                texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s.png' % self.style.dept)

            for headPart in self.zapActorHeadParts:
                headPart.setTexture(texture, 1)
            applyHeadPartDefaults()

        parts = zapActor.findAllMatches('**/pPlane*')
        for partNum in xrange(parts.getNumPaths()):
            parts.getPath(partNum).setTwoSided(1)

        zapActor.leftHand = zapActor.find('**/joint_Lhold')
        zapActor.rightHand = zapActor.find('**/joint_Rhold')
        zapActor.shadowJoint = zapActor.find('**/joint_shadow')
        zapActor.nametagNull = zapActor.find('**/joint_nameTag')

        dropShadow = loader.loadModel('phase_3/models/props/drop_shadow')
        dropShadow.setScale(0.45)
        dropShadow.setColor(0.0, 0.0, 0.0, 0.5)
        dropShadow.reparentTo(zapActor.shadowJoint)

        texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s.png' % self.style.dept)

        if self.isWaiter:
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_waiter.png')
        elif self.style.dept == 'c' and not self.getExecutive() and not self.getManager() and not self.getGovernaught() and not self.isWaiter:
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s.png' % self.style.dept)
        elif self.isExecutive and not self.isWaiter or self.getManager() or self.getExecutive():
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_exe.png' % self.style.dept)
        elif self.getManager() and not self.isWaiter and self.style.name != 'dold':
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_exe.png' % self.style.dept)
        elif self.style.name == 'dold':
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_dold.png')
        elif self.getGovernaught() and not self.isWaiter:
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_gov.png' % self.style.dept)

        body = zapActor.find('**/body')
        if not body.isEmpty():
            body.setTexture(texture, 1)

        meter = zapActor.find('**/emblem_healthmeter')
        if not meter.isEmpty():
            meter.show()

        modelRoot = zapActor

        modelRoot.find('**/necktie-s').hide()
        modelRoot.find('**/necktie-w').hide()
        modelRoot.find('**/bowtie').hide()

        modelRoot.find('**/necktie-s').setTexture(texture, 1)
        modelRoot.find('**/bowtie').setTexture(texture, 1)
        if self.style.name == 'wsi':
            textureWSI = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s.png' % self.style.dept)
            modelRoot.find('**/necktie-w').setTexture(textureWSI, 1)
        else:
            modelRoot.find('**/necktie-w').setTexture(texture, 1)

        if self.isWaiter:
            modelRoot.find('**/bowtie').show()
        elif self.style.dept == 'l' and self.style.name != 'wsi':
            modelRoot.find('**/bowtie').show()
        elif self.style.dept == 's':
            modelRoot.find('**/necktie-s').show()
        elif self.style.name == 'wsi':
            modelRoot.find('**/bowtie').hide()
            modelRoot.find('**/necktie-w').show()
            textureWSI = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s.png' % self.style.dept)
            modelRoot.find('**/necktie-w').setTexture(textureWSI, 1)
        elif self.style.name == 'hydra':
            modelRoot.find('**/bowtie').show()
            modelRoot.setColor((0.729, 0.729, 0.729, 1))
            modelRoot.find('**/bowtie').setColor((0.741, 0.82, 0.769, 1))
        elif self.style.name == 'charon':
            modelRoot.find('**/necktie-w').hide()
            modelRoot.find('**/necktie-s').show()
            modelRoot.setColor((0.51, 0.49, 0.467, 1))
            modelRoot.find('**/necktie-s').setColor((0.741, 0.82, 0.769, 1))
        elif self.style.name == 'nix':
            modelRoot.find('**/necktie-w').show()
            modelRoot.setColor((0.6, 0.6, 0.6, 1))
            modelRoot.find('**/necktie-w').setColor((0.741, 0.82, 0.769, 1))
        elif self.style.name == 'styx':
            modelRoot.find('**/necktie-w').show()
            modelRoot.setColor((0.671, 0.671, 0.671, 1))
            modelRoot.find('**/necktie-w').setColor((0.741, 0.82, 0.769, 1))
        elif self.style.name == 'kerberos':
            modelRoot.find('**/necktie-w').show()
            modelRoot.setColor((0.62, 0.659, 0.624, 1))
            modelRoot.find('**/necktie-w').setColor((0.741, 0.82, 0.769, 1))
        elif self.style.name == 'rainmake':
            pass
        elif self.style.name in (
            'racket', 'erfit', 'erclaim', 'hrollers', 'hroller2', 'hroller',
            'bellring', 'psetter', 'hustle', 'ins', 'dking', 'ddiver',
            'gatekeep'
        ):
            pass
        elif self.style.name == 'ovt':
            modelRoot.find('**/bowtie').show()
        else:
            modelRoot.find('**/necktie-w').show()

        textureDerrick = loader.loadTexture('phase_12/maps/ttcc_ene_derrickhand_skelecog.png')
        textureDopa = loader.loadTexture('phase_9/maps/ttcc_ene_dopa.png')
        textureDold = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_dold.png')
        textureDopr = loader.loadTexture('phase_9/maps/ttcc_ene_dopr.png')
        textureAmbassador = loader.loadTexture('phase_9/maps/ttcc_ene_ambassador.png')
        textureDirector = loader.loadTexture('phase_12/maps/ttcc_ene_chainsaw_boardbot.png')

        headParts = zapActor.findAllMatches('**/joint_head*')
        for i in xrange(headParts.getNumPaths()):
            headPart = headParts.getPath(i)

            if self.style.name == 'derrhand':
                headPart.setTexture(textureDerrick, 1)
            elif self.style.name == 'ubuster':
                headPart.setTexture(textureDopr, 1)
            elif self.style.name == 'dold':
                headPart.setTexture(textureDold, 1)
            elif self.style.name == 'radiog':
                headPart.setTexture(textureDopa, 1)
            elif self.style.name == 'cdirector':
                headPart.setTexture(textureDirector, 1)
            elif self.style.name == 'dopa':
                headPart.setTexture(textureDopa, 1)
            elif self.style.name == 'ambass':
                headPart.setTexture(textureAmbassador, 1)
            else:
                headPart.setTexture(texture, 1)

        try:
            self.generateCorporateTie(zapActor)
        except:
            pass

        dept = self.getStyleDept()
        level = str(self.getActualLevel())

        if self.getExecutive():
            level += TTLocalizer.ExecutivePostFix
        if self.getManager():
            level += TTLocalizer.ManagerPostFix
        if self.getGovernaught():
            level += TTLocalizer.GovernaughtPostFix

        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {
            'name': self.name,
            'dept': dept,
            'level': level
        }

        try:
            zapActor.setDisplayName(nameInfo)
        except:
            pass

        zapActor.setScale(self.scale)
        zapActor.setPos(self.getPos())
        zapActor.setHpr(self.getHpr())

        return zapActor


    def getZapActorPowerhouseSquirt(self):
        return self.__makeZapActorPowerhouseVariant('zapActorPowerhouseSquirt')


    def getZapActorPowerhouseZap(self):
        return self.__makeZapActorPowerhouseVariant('zapActorPowerhouseZap')

    def makeSkeleton(self, elite=False):
        model = 'phase_5/models/char/cog' + string.upper(self.style.body) + '_robot-zero'
        anims = self.generateAnimDict()
        anim = self.getCurrentAnim()
        dept = self.style.dept
        self.headParts = []
        self.removePart('modelRoot')
        self.generateSkeletonBody()
        self.loadAnims(anims)
        self.removeHealthBar()
        self.generateSkeletonHealthBar()
        self.generateSkeletonHealthBarDisplay()
        #self.generateHPBase()
        #self.generateCorporateMedallion()
        self.generateCorporateMedallion3()
        #self.generateCorporateTie()
        self.setSuitClothesSkeleton()
        self.setHeight(self.height)
        self.setBlend(frameBlend=base.wantSmoothAnims)
        self.setLODAnimation(base.lodMaxRange, base.lodMinRange, base.lodDelayFactor)
        parts = self.findAllMatches('**/pPlane*')
        for partNum in xrange(0, parts.getNumPaths()):
            bb = parts.getPath(partNum)
            bb.setTwoSided(1)

        #self.setName(TTLocalizer.SuitBaseNameWithLevelMgr)
        self.leftHand = self.find('**/joint_Lhold')
        self.rightHand = self.find('**/joint_Rhold')
        self.shadowJoint = self.find('**/joint_shadow')
        dropShadow = loader.loadModel('phase_3/models/props/drop_shadow')
        dropShadow.setScale(0.45)
        dropShadow.setColor(0.0, 0.0, 0.0, 0.5)
        dropShadow.reparentTo(self.shadowJoint)
        self.nametagNull = self.find('**/joint_nameTag')
        texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s.png' % self.style.dept)
        if self.isWaiter:
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_waiter.png')
        elif self.style.dept == 'c' and not self.getExecutive() and not self.isManager and not self.getGovernaught() and not self.isWaiter:
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s.png' % self.style.dept)
        elif self.isExecutive and not self.isWaiter or self.isManager or self.getExecutive():
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_exe.png' % self.style.dept)
        elif self.isManager and not self.isWaiter and not self.style.name == 'dold':
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_exe.png' % self.style.dept)
        elif self.style.name == 'dold':
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_dold.png')
        elif self.getGovernaught() and not self.isWaiter:
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_gov.png' % self.style.dept)
        self.find('**/body').setTexture(texture, 1)
        self.find('**/emblem_healthmeter').show()
        textureDerrick = loader.loadTexture('phase_12/maps/ttcc_ene_derrickhand_skelecog.png')
        textureDopa = loader.loadTexture('phase_9/maps/ttcc_ene_dopa.png')
        textureDold = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_dold.png')
        textureDopr = loader.loadTexture('phase_9/maps/ttcc_ene_dopr.png')
        textureAmbassador = loader.loadTexture('phase_9/maps/ttcc_ene_ambassador.png')
        textureDirector = loader.loadTexture('phase_12/maps/ttcc_ene_chainsaw_boardbot.png')

        for headPart in self.headParts:
            if self.style.name == 'derrhand':
                headPart.setTexture(textureDerrick, 1)
            elif self.style.name == 'ubuster':
                headPart.setTexture(textureDopr, 1)
            elif self.style.name == 'dold':
                headPart.setTexture(textureDold, 1)
            elif self.style.name == 'radiog':
                headPart.setTexture(textureDopa, 1)
            elif self.style.name == 'cdirector':
                headPart.setTexture(textureDirector, 1)
            elif self.style.name == 'dopa':
                headPart.setTexture(textureDopa, 1)
            elif self.style.name == 'ambass':
                headPart.setTexture(textureAmbassador, 1)
            else:
                headPart.setTexture(texture, 1)
        dept = self.getStyleDept()
        level = str(self.getActualLevel())
        if self.getExecutive():
            level += TTLocalizer.ExecutivePostFix
        if self.getManager():
            level += TTLocalizer.ManagerPostFix
        if self.getGovernaught():
            level += TTLocalizer.GovernaughtPostFix
        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': self.name,
                                                        'dept': dept,
                                                        'level': level}
        self.setDisplayName(nameInfo)

        self.isSkeleton = 1

    def makeSkeletonManager(self, elite=False):
        anims = self.generateAnimDict()
        self.headParts = []
        self.removePart('modelRoot')
        self.generateSkeletonBody()
        self.loadAnims(anims)
        self.removeHealthBar()
        self.generateSkeletonHealthBar()
        self.generateSkeletonHealthBarDisplay()
        #self.generateHPBase()
        #self.generateCorporateMedallion()
        self.generateCorporateMedallion3()
        #self.generateCorporateTie()
        self.setSuitClothesSkeleton()
        self.setHeight(self.height)
        self.setBlend(frameBlend=base.wantSmoothAnims)
        self.setLODAnimation(base.lodMaxRange, base.lodMinRange, base.lodDelayFactor)
        parts = self.findAllMatches('**/pPlane*')
        for partNum in xrange(0, parts.getNumPaths()):
            bb = parts.getPath(partNum)
            bb.setTwoSided(1)

        #self.setName(TTLocalizer.SuitBaseNameWithLevelMgr)
        self.leftHand = self.find('**/joint_Lhold')
        self.rightHand = self.find('**/joint_Rhold')
        self.shadowJoint = self.find('**/joint_shadow')
        self.nametagNull = self.find('**/joint_nameTag')
        dropShadow = loader.loadModel('phase_3/models/props/drop_shadow')
        dropShadow.setScale(0.45)
        dropShadow.setColor(0.0, 0.0, 0.0, 0.5)
        dropShadow.reparentTo(self.shadowJoint)
        self.find('**/emblem_healthmeter').show()
        self.isSkeleton = 1

    def makeSkeleton2(self, elite=False):
        model = 'phase_5/models/char/cog' + string.upper(self.style.body) + '_robot-zero'
        anims = self.generateAnimDict()
        anim = self.getCurrentAnim()
        dept = self.style.dept
        self.headParts = []
        self.removePart('modelRoot')
        self.generateSkeletonBody()
        self.loadAnims(anims)
        self.removeHealthBar()
        self.generateSkeletonHealthBar()
        self.generateSkeletonHealthBarDisplay2()
        #self.generateHPBase()
        #self.generateCorporateMedallion()
        #self.generateCorporateMedallion3()
        #self.generateCorporateTie()
        self.setSuitClothesSkeleton()
        self.setHeight(self.height)
        self.setBlend(frameBlend=base.wantSmoothAnims)
        self.setLODAnimation(base.lodMaxRange, base.lodMinRange, base.lodDelayFactor)
        parts = self.findAllMatches('**/pPlane*')
        for partNum in xrange(0, parts.getNumPaths()):
            bb = parts.getPath(partNum)
            bb.setTwoSided(1)

        #self.setName(TTLocalizer.SuitBaseNameWithLevelMgr)
        self.leftHand = self.find('**/joint_Lhold')
        self.rightHand = self.find('**/joint_Rhold')
        self.shadowJoint = self.find('**/joint_shadow')
        self.nametagNull = self.find('**/joint_nameTag')
        dropShadow = loader.loadModel('phase_3/models/props/drop_shadow')
        dropShadow.setScale(0.45)
        dropShadow.setColor(0.0, 0.0, 0.0, 0.5)
        dropShadow.reparentTo(self.shadowJoint)
        texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s.png' % self.style.dept)
        if self.isWaiter:
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_waiter.png')
        elif self.style.dept == 'c' and not self.getExecutive() and not self.isManager and not self.getGovernaught() and not self.isWaiter:
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s.png' % self.style.dept)
        elif self.isExecutive and not self.isWaiter or self.isManager or self.getExecutive():
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_exe.png' % self.style.dept)
        elif self.isManager and not self.isWaiter and not self.style.name == 'dold':
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_exe.png' % self.style.dept)
        elif self.style.name == 'dold':
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_dold.png')
        elif self.getGovernaught() and not self.isWaiter:
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_gov.png' % self.style.dept)
        self.find('**/body').setTexture(texture, 1)
        self.find('**/emblem_healthmeter').show()
        textureDerrick = loader.loadTexture('phase_12/maps/ttcc_ene_derrickhand_skelecog.png')
        textureDopa = loader.loadTexture('phase_9/maps/ttcc_ene_dopa.png')
        textureDold = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_dold.png')
        textureDopr = loader.loadTexture('phase_9/maps/ttcc_ene_dopr.png')
        textureAmbassador = loader.loadTexture('phase_9/maps/ttcc_ene_ambassador.png')
        textureDirector = loader.loadTexture('phase_12/maps/ttcc_ene_chainsaw_boardbot.png')

        for headPart in self.headParts:
            if self.style.name == 'derrhand':
                headPart.setTexture(textureDerrick, 1)
            elif self.style.name == 'ubuster':
                headPart.setTexture(textureDopr, 1)
            elif self.style.name == 'dold':
                headPart.setTexture(textureDold, 1)
            elif self.style.name == 'radiog':
                headPart.setTexture(textureDopa, 1)
            elif self.style.name == 'cdirector':
                headPart.setTexture(textureDirector, 1)
            elif self.style.name == 'dopa':
                headPart.setTexture(textureDopa, 1)
            elif self.style.name == 'ambass':
                headPart.setTexture(textureAmbassador, 1)
            else:
                headPart.setTexture(texture, 1)
        dept = self.getStyleDept()
        level = str(self.getActualLevel())
        revives = self.getSkeleRevives()
        if self.getExecutive():
            level += TTLocalizer.ExecutivePostFix
        if self.getManager():
            level += TTLocalizer.ManagerPostFix
        if self.getGovernaught():
            level += TTLocalizer.GovernaughtPostFix
        if self.isSkeleton and revives >=2:
            level += ' v2.0'
        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': self.name,
                                                        'dept': dept,
                                                        'level': level}
        self.setDisplayName(nameInfo)

        self.isSkeleton = 1
        self.isRevive = 1

    def makeFired(self, elite=False):
        anims = self.generateAnimDict()
        self.setName(self.createNameInfoFired())
        self.corpMedallion.hide()
        texture = loader.loadTexture('phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
        textureSkele = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_unemployed.png')
        if self.isSkeleton:
            self.find('**/necktie-s').setTexture(textureSkele, 1)
            self.find('**/necktie-w').setTexture(textureSkele, 1)
            self.find('**/bowtie').setTexture(textureSkele, 1)
            self.find('**/body').setTexture(textureSkele, 1)
            for headPart in self.headParts:
                headPart.setTexture(textureSkele, 1)
        else:
            self.find('**/necktie-s').setTexture(texture, 1)
            self.find('**/necktie-w').setTexture(texture, 1)
            self.find('**/bowtie').setTexture(texture, 1)
            self.find('**/body').setTexture(texture, 1)
        if self.style.name == 'bgh' and not self.isSkeleton:
            texture2 = loader.loadTexture('phase_14/maps/cc_t_ene_bagholder_unemployed.png')
            for headPart in self.headParts:
                headPart.setTexture(texture2, 1)
        if self.style.name == 'ins' and not self.isSkeleton:
            texture2 = loader.loadTexture('phase_14/maps/cc_t_ene_insider_unemployed.png')
            for headPart in self.headParts:
                headPart.setTexture(texture2, 1)
        if self.style.name == 'hho' and not self.isSkeleton:
            texture2 = loader.loadTexture('phase_14/maps/cc_t_ene_headhoncho_unemployed.png')
            for headPart in self.headParts:
                headPart.setTexture(texture2, 1)

        self.isFired = 1

    def makeDesperation(self, elite=False):
        self.isDesperation = 1

    def setDesperation(self, num):
        self.desperationMult = num

    def getDesperation(self):
        return self.desperationMult

    def getSoakRounds(self):
        return self.isSoaked
    
    def makeOverseer(self, num):
        self.isOverseer = num

    def makeUnOverseer(self):
        self.isOverseer = 0
    
    def getOverseerRounds(self):
        return self.isOverseer

    def getMarkRounds(self):
        return self.isMarked

    def getZapCondition(self):
        return self.isZapped

    def makeSleepy(self, num):
        self.isSleepy = num
        self.isAlreadySleepy = 1

    def getSleepyCondition(self):
        return self.isSleepy

    def makeUnSleepy(self):
        self.isSleepy = 0

    def makeExplosive(self, num):
        self.isExplosive = num
        self.isAlreadyExplosive = 1

    def getExplosiveCondition(self):
        return self.isExplosive
    
    def makeUnDrenched(self, elite=False):
        self.actuallySoaked = 0
        self.isSoaked = 0

        self.cleanupSoaked()

    def makeNoAttack(self):
        self.setDizzy3(1)

    def makeUnNoAttack(self):
        self.setDizzy3(0)

    def makeDrenched(self, num):

        self.cleanupDrenched()

        if num <= 0 or self.currHP <= 0:
            return


        self.liquidEffect2 = BattleParticles.createParticleEffect(file='wet3')

        self.liquidEffect2.reparentTo(self)
        self.liquidEffect2.setPos(0, 0, self.height - 2.5)

        self.liquidEffect2.start(parent=self, renderParent=self)

    def cleanupDrenched(self):
        if hasattr(self, 'liquidTrack2') and self.liquidTrack2:
            try:
                self.liquidTrack2.pause()
            except:
                pass
            try:
                self.liquidTrack2.finish()
            except:
                pass
            self.liquidTrack2 = None

        if hasattr(self, 'liquidEffect2') and self.liquidEffect2:
            effect = self.liquidEffect2
            self.liquidEffect2 = None

            try:
                effect.softStop()
            except:
                pass

            try:
                effect.disable()
            except:
                pass

            try:
                effect.cleanup()
            except:
                pass

            try:
                effect.removeNode()
            except:
                try:
                    effect.detachNode()
                except:
                    pass

    def makeUnSoaked(self, elite=False):
        self.actuallySoaked = 0
        self.isSoaked = 0

        self.cleanupSoaked()

    def makeSoaked(self, num):
        self.actuallySoaked = 1
        self.isSoaked = num

        self.cleanupSoaked()

        if num <= 0 or self.currHP <= 0:
            return


        self.liquidEffect = BattleParticles.createParticleEffect(file='wet2')

        self.liquidEffect.reparentTo(self)
        self.liquidEffect.setPos(0, 0, self.height - 2.5)

        self.liquidEffect.start(parent=self, renderParent=self)

    def cleanupSoaked(self):
        if hasattr(self, 'liquidTrack') and self.liquidTrack:
            try:
                self.liquidTrack.pause()
            except:
                pass
            try:
                self.liquidTrack.finish()
            except:
                pass
            self.liquidTrack = None

        if hasattr(self, 'liquidEffect') and self.liquidEffect:
            effect = self.liquidEffect
            self.liquidEffect = None

            try:
                effect.softStop()
            except:
                pass

            try:
                effect.disable()
            except:
                pass

            try:
                effect.cleanup()
            except:
                pass

            try:
                effect.removeNode()
            except:
                try:
                    effect.detachNode()
                except:
                    pass

    def createAfterImage(self, battle, fadeTime=0.4):
        # Find the actor root
        actorNode = self.find('**/__Actor_modelRoot')
        actorCollection = actorNode.findAllMatches('*')

        # Create a container node for the ghost
        ghostRoot = battle.attachNewNode('afterimage')
        ghostRoot.setPos(self.getPos(battle))
        ghostRoot.setHpr(self.getHpr(battle))

        # Copy visible geometry
        for thingIndex in range(actorCollection.getNumPaths()):
            thing = actorCollection[thingIndex]

            if thing.getName() not in (
                    'joint_attachMeter',
                    'joint_shadow',
                    'joint_nameTag',
                    'def_nameTag'
            ):
                if not thing.isEmpty() and thing.node().isGeomNode():
                    ghostPart = thing.copyTo(ghostRoot)
                    ghostPart.setTransparency(TransparencyAttrib.MAlpha)
                    ghostPart.setColorScale(1, 1, 1, 0.6)  # semi-transparent

        # Fade out and remove
        fadeTrack = Sequence(
            LerpColorScaleInterval(
                ghostRoot,
                fadeTime,
                (1, 1, 1, 0),
                startColorScale=(1, 1, 1, 0.6)
            ),
            Func(ghostRoot.removeNode)
        )

        fadeTrack.start()

    def makeLoopingShockAura(self):
        import random

        self.cleanupShockAura()

        auraNode = self.attachNewNode('shockAuraNode')

        sparks = []
        partTrack = Parallel()

        def resetSpark(spark):
            if not spark or spark.isEmpty():
                return

            x = random.uniform(-2.0, 2.0)
            y = random.uniform(-1.7, 1.7)
            z = random.uniform(0.8, max(1.0, self.height - 2))

            spark.show()
            spark.setPos(x, y, z)
            spark.setHpr(
                random.uniform(0, 360),
                random.uniform(-20, 20),
                random.uniform(0, 360)
            )
            spark.setScale(random.uniform(1.0, 3.0))
            spark.setAlphaScale(1)
            spark.setColor(1, 0.988, 0.408, 1.0)

        for i in xrange(12):
            spark = loader.loadModel(
                'phase_3.5/models/gui/matching_game_gui'
            ).find('**/minnieArrow').copyTo(auraNode)
            texture = loader.loadTexture('phase_3.5/maps/phase_3.5_palette_2tlla_12.png')
            spark.setTexture(texture, 1)
            spark.setBillboardPointEye()
           # spark.setTransparency(1)
            spark.setTwoSided(True)
            spark.setLightOff(1)
            spark.setDepthWrite(False)
            spark.hide()
            spark.setR(270)

            oneSparkTrack = Sequence(
                Wait(random.uniform(0.0, 0.5) + i * 0.05),
                Func(resetSpark, spark),

                Parallel(
                    # Spin in place only
                    LerpHprInterval(
                        spark,
                        0.35,
                        Vec3(0, 0, 90),
                        startHpr=Vec3(0, 0, 270)
                    ),

                    # tiny twitch in place
                    # Sequence(
                    #     LerpScaleInterval(spark, 0.15, random.uniform(1.5, 3.5)),
                    #     LerpScaleInterval(spark, 0.15, random.uniform(1.0, 3.0)),
                    #     LerpScaleInterval(spark, 0.15, random.uniform(1.5, 3.5))
                    # ),

                    # fade out
                    Sequence(
                        LerpFunctionInterval(
                            spark.setAlphaScale,
                            0.35,
                            fromData=1,
                            toData=0
                        )
                    )
                ),

                Func(spark.hide)
            )

            partTrack.append(oneSparkTrack)
            sparks.append(spark)

        loopTrack = Sequence(partTrack)
        loopTrack.sparks = sparks
        return loopTrack

    def makeZapped(self, num):
        self.isZapped += num

        if getattr(self, 'isDead', False) or self.isEmpty():
            return

        if getattr(self, 'shockAuraTrack', None):
            return

        self.shockAuraTrack = self.makeLoopingShockAura()
        self.shockAuraTrack.loop()

    def makeUnZapped(self):
        self.isZapped = 0
        self.cleanupShockAura()
        
    def cleanupShockAura(self):
        track = getattr(self, 'shockAuraTrack', None)

        if track:
            auraNode = getattr(track, 'auraNode', None)

            try:
                track.pause()
                track.finish()
            except:
                pass

            self.shockAuraTrack = None

            try:
                if auraNode and not auraNode.isEmpty():
                    auraNode.removeNode()
            except:
                pass

    def makeFreshlyZapped(self):
        self.freshlyZapped = 1

    def makeUnFreshlyZapped(self):
        self.freshlyZapped = 0

    def makeMarked(self, num):
        self.actuallyMarked = 1
        self.isMarked = num

    def applySplat(self, splat, actor=None):
        if actor is None:
            actor = self
        if type(splat[0]) == TextureStage:
            splat = splat[1]
        pieName = splat[0]
        partName = splat[1]
        u = splat[2]
        v = splat[3]
        if pieName == 'cupcake' or pieName == 'wedding-cake':
            torsoTex = loader.loadTexture('phase_5/maps/splat_wedding.png')
            armTex = loader.loadTexture('phase_5/maps/tiny_splat_wedding.png')
        elif pieName == 'birthday-cake-slice' or pieName == 'birthday-cake':
            torsoTex = loader.loadTexture('phase_5/maps/splat_cake.png')
            armTex = loader.loadTexture('phase_5/maps/tiny_splat_cake.png')
        elif pieName == 'fruitpie-slice' or pieName == 'fruitpie':
            torsoTex = loader.loadTexture('phase_5/maps/splat_fruit.png')
            armTex = loader.loadTexture('phase_5/maps/tiny_splat_fruit.png')
        elif pieName == 'creampie-slice' or pieName == 'creampie':
            torsoTex = loader.loadTexture('phase_5/maps/splat_cream.png')
            armTex = loader.loadTexture('phase_5/maps/tiny_splat_cream.png')
        else:
            torsoTex = loader.loadTexture('phase_5/maps/splat_cream.png')
            armTex = loader.loadTexture('phase_5/maps/tiny_splat_cream.png')
        ts = TextureStage('pieSplat')
        ts.setMode(TextureStage.MDecal)
        ts.setSort(3)
        self.splats.append((ts, splat))
        try:
            actor.find('**/' + partName).setTexOffset(ts, u, v)
            if partName != 'arms':
                actor.find('**/' + partName).setTexture(ts, torsoTex)
            else:
                actor.find('**/' + partName).setTexture(ts, armTex)
        except:  # Can't find torso? It's a skelecog
            actorNode = actor.find('**/__Actor_modelRoot')
            actorCollection = actorNode.findAllMatches('*')
            for thing in actorCollection:
                if thing.getName() not in ('joint_attachMeter', 'joint_nameTag', 'def_nameTag', 'joint_Rhold', 'joint_Lhold', 'joint_shadow'):
                    thing.setTexOffset(ts, u, v)
                    thing.setTexture(ts, torsoTex)

    def clearSplats(self, actor=None):
        if actor is None:
            actor = self
        for splat in self.splats:
            partName = splat[1][1]
            ts = splat[0]
            try:
                actor.find('**/' + partName).clearTexture(ts)
            except:  # Can't find torso? It's a skelecog
                try:
                    actorNode = actor.find('**/__Actor_modelRoot')
                    actorCollection = actorNode.findAllMatches('*')
                    for thing in actorCollection:
                        if thing.getName() not in ('joint_attachMeter', 'joint_nameTag', 'def_nameTag', 'joint_Rhold', 'joint_Lhold', 'joint_shadow'):
                            thing.clearTexture(ts)
                except AssertionError:
                    # Can't find ACTOR AGAIN??? Bruh.
                    break
        self.splats = []
        self.splatCount = 0

    def hasSplats(self):
        return bool(self.splats)

    def makeUnMarked(self, elite=False):
        self.actuallyMarked = 0
        self.isMarked = 0

    def makeTarget(self):
        self.isTarget = 1
        # ---- CLEANUP ----
        if hasattr(self, "knifeTrack") and self.knifeTrack:
            self.knifeTrack.pause()
            self.knifeTrack.finish()
            self.knifeTrack = None

        if hasattr(self, "knifePivot") and not self.knifePivot.isEmpty():
            self.knifePivot.removeNode()

        from math import pi, cos, sin

        totalKnives = 5

        radius = 1.5
        height = self.height - 1

        # Shared pivot (orbit axis)
        self.knifePivot = self.attachNewNode("knifePivot")
        self.knifePivot.setZ(height)

        knifeIntervals = []

        for i in range(totalKnives):

            # Load correct model
            knife = globalPropPool.getProp('tnt')
            knife.setScale(0.5)
            tip = knife.find('**/joint_attachEmitter')
            sparks = BattleParticles.createParticleEffect(file='tnt')
            knife.sparksEffect = sparks
            sparks.start(tip)

            knife.reparentTo(self.knifePivot)

            # Even spacing
            angle = (2 * pi / totalKnives) * i
            knife.setPos(cos(angle) * radius,
                         sin(angle) * radius,
                         0)

            # Match original orientation
            knife.lookAt(self.knifePivot)
            knife.setP(90)
            knife.setR(90)

            # Individual knife spin (same as your first knife)
            # spin = LerpHprInterval(
            #     knife,
            #     4.0,
            #     VBase3(360.0, 270.0, 0.0),
            #     startHpr=VBase3(0.0, 270.0, 0.0)
            # )
            #
            # knifeIntervals.append(spin)

        # Pivot rotation (orbit)
        orbit = LerpHprInterval(
            self.knifePivot,
            4.0,
            VBase3(360, 0, 0),
            startHpr=VBase3(0, 0, 0)
        )

        # Run everything together
        self.knifeTrack = Parallel(
            orbit,
            *knifeIntervals
        )

        self.knifeTrack.loop()

    def makeUnTarget(self):
        self.isTarget = 0
        # ---- CLEANUP ----
        if hasattr(self, "knifeTrack") and self.knifeTrack:
            self.knifeTrack.pause()
            self.knifeTrack.finish()
            self.knifeTrack = None

        if getattr(self, "knifePivot", None) is not None and not self.knifePivot.isEmpty():
            self.knifePivot.removeNode()

    def makeImmortal(self, elite=False):
        #self.healthBar.setColor(1, 1, 1, 1)
       # self.healthBarGlow.setColor(1, 1, 1, 1)
        #taskMgr.remove(self.uniqueName('blink-task'))
        #self.__pulseWhite()
        self.isImmortal = 1
        if hasattr(self, 'cheerEffect') and self.cheerEffect:
            self.cheerEffect.softStop()
            self.cheerEffect.cleanup()
            self.cheerEffect = None
        self.cheerEffect = BattleParticles.createParticleEffect(file='hr_rainbowfeet')

        self.cheerEffect.reparentTo(self)
        self.cheerEffect.setPos(0, 0, 0)
        # self.cooldownEffect.setHpr(180, 0, 0)

        self.cheerTrack = Sequence(ParticleInterval(self.cheerEffect, self, duration=3, softStopT=1))
        if self.hasSuitStatusEffect('highRollerPhase3') and self.style.name == 'hroller2':
            self.cheerEffect.start()

    def makeNonImmortal(self, elite=False):
      #  self.healthBar.setColor(1, 1, 1, 1)
       # self.healthBarGlow.setColor(1, 1, 1, 1)
       # taskMgr.remove(self.uniqueName('blink-task'))
       # self.__changeColor()
        self.isImmortal = 0
        if hasattr(self, 'cheerEffect') and self.cheerEffect:
            self.cheerEffect.softStop()
            self.cheerEffect.cleanup()
            self.cheerEffect = None

    def makeRushJobArrow(self, track):
        self.cleanupRushJobArrow()

        trackColors = {
            1:   Vec4(1, 0, 0, 1),
            2:   Vec4(0, 1, 0.016, 1),
            3:  Vec4(1, 0.682, 0, 1),
            4: Vec4(1, 0, 0.969, 1),
            5:    Vec4(1, 0.996, 0, 1),
            6:  Vec4(0.102, 0, 1, 1),
            7:   Vec4(0, 0.976, 1, 1),
        }

        color = trackColors.get(track, Vec4(1, 1, 1, 1))

        auraNode = self.attachNewNode('rushJobArrowNode')
        auraNode.setPos(0, 0, self.getHeight() + 2.5)
        auraNode.setScale(10)
        auraNode.setBillboardPointEye()

        arrowModel = loader.loadModel('phase_3.5/models/gui/matching_game_gui')
        arrow = arrowModel.find('**/minnieArrow').copyTo(auraNode)
        arrowModel.removeNode()

        arrow.setColor(color)
        arrow.setTransparency(TransparencyAttrib.MAlpha)
        arrow.setTwoSided(True)
        arrow.setHpr(0, 0, 90)

        self.rushJobArrowNode = auraNode
        self.rushJobArrow = arrow

        self.rushJobArrowTrack = Sequence(
            LerpPosInterval(auraNode, 2.5, Point3(0, 0, self.getHeight() + 3.0),
                            startPos=Point3(0, 0, self.getHeight() + 2.4),
                            blendType='easeInOut'),
            LerpPosInterval(auraNode, 2.5, Point3(0, 0, self.getHeight() + 2.4),
                            startPos=Point3(0, 0, self.getHeight() + 3.0),
                            blendType='easeInOut')
        )
        self.rushJobArrowTrack.loop()

    def cleanupRushJobArrow(self):
        if hasattr(self, 'rushJobArrowTrack') and self.rushJobArrowTrack:
            try:
                self.rushJobArrowTrack.finish()
            except:
                pass
            self.rushJobArrowTrack = None

        if hasattr(self, 'rushJobArrowNode') and self.rushJobArrowNode:
            try:
                if not self.rushJobArrowNode.isEmpty():
                    self.rushJobArrowNode.removeNode()
            except:
                pass
            self.rushJobArrowNode = None

        self.rushJobArrow = None

    def makeTrapRushJob(self):
        self.trapRushJob = 1
        self.makeRushJobArrow(1)

    def makeUnTrapRushJob(self):
        self.trapRushJob = 0
        self.cleanupRushJobArrow()

    def makeLureRushJob(self):
        self.lureRushJob = 1
        self.makeRushJobArrow(2)

    def makeUnLureRushJob(self):
        self.lureRushJob = 0
        self.cleanupRushJobArrow()

    def makeThrowRushJob(self):
        self.throwRushJob = 1
        self.makeRushJobArrow(3)

    def makeUnThrowRushJob(self):
        self.throwRushJob = 0
        self.cleanupRushJobArrow()

    def makeSquirtRushJob(self):
        self.squirtRushJob = 1
        self.makeRushJobArrow(4)

    def makeUnSquirtRushJob(self):
        self.squirtRushJob = 0
        self.cleanupRushJobArrow()

    def makeZapRushJob(self):
        self.zapRushJob = 1
        self.makeRushJobArrow(5)

    def makeUnZapRushJob(self):
        self.zapRushJob = 0
        self.cleanupRushJobArrow()

    def makeSoundRushJob(self):
        self.soundRushJob = 1
        self.makeRushJobArrow(6)

    def makeUnSoundRushJob(self):
        self.soundRushJob = 0
        self.cleanupRushJobArrow()

    def makeDropRushJob(self):
        self.dropRushJob = 1
        self.makeRushJobArrow(7)

    def makeUnDropRushJob(self):
        self.dropRushJob = 0
        self.cleanupRushJobArrow()

    def makeLured(self, prestige):
        self.isLured = prestige

    def makeTrapped(self, level):
        self.isTrapped = level

    def makeUnTrapped(self):
        self.isTrapped = 0

    def addLuredRounds(self, num):
        self.lureRounds = num

    def getLuredRounds(self):
        return self.lureRounds

    def makeUnLured(self, elite=False):
        self.isLured = 0

    def makeLureImmune(self, elite=False):
        self.isLureImmune = 1

    def makeUnLureImmune(self, elite=False):
        self.isLureImmune = 0

    def makeMarkImmune(self, elite=False):
        self.isMarkImmune = 1

    def makeUnMarkImmune(self, elite=False):
        self.isMarkImmune = 0
        
    def makeSoundImmune(self, elite=False):
        self.isSoundImmune = 1

    def makeUnSoundImmune(self, elite=False):
        self.isSoundImmune = 0    

    def makeSoakResistant(self, elite=False):
        self.isSoakImmune = 1

    def makeUnSoakResistant(self, elite=False):
        self.isSoakImmune = 0

    def makeZapResistant(self, elite=False):
        self.isZapImmune = 1

    def makeUnZapResistant(self, elite=False):
        self.isZapImmune = 0

    def makeDropResistant(self, elite=False):
        self.isDropImmune = 1

    def makeUnDropResistant(self, elite=False):
        self.isDropImmune = 0

    def makeSyphon(self, battle):
        self.isSyphon = 1

    def removeStormCellDamage(self, num):
        self.stormCellDamage = num

    def getStormCellDamage(self):
        return self.stormCellDamage

    def addHeavyRainDamageReal(self, num):
        self.heavyRainDamage = num

    def getHeavyRainDamage(self):
        return self.heavyRainDamage

    def makeUnHeavyRain(self, elite=False):
        self.isHeavyRain = 0
        self.heavyRainDamage = 0

    def makeInversion(self, elite=False):
        self.isHeavyRain = 0
        self.isFreezingRain = 0
        self.isStormCell = 0
        self.isMonsoon = 0
        self.isOilRain = 0

    def makeHeavyRain(self, elite=False):
        self.isHeavyRain = 1
        self.isFreezingRain = 0
        self.isStormCell = 0
        self.isOilRain = 0
        self.stormCellDamage = 60
        self.isMonsoon = 0

    def makeFreezingRain(self, elite=False):
        self.isHeavyRain = 0
        self.isFreezingRain = 1
        self.isStormCell = 0
        self.isOilRain = 0
        self.isMonsoon = 0

    def makeOilRainOLD(self, elite=False):
        self.isHeavyRain = 0
        self.isFreezingRain = 0
        self.isStormCell = 0
        self.isOilRain = 1
        self.isMonsoon = 0

    def makeMonsoon(self, elite=False):
        self.isHeavyRain = 0
        self.isFreezingRain = 0
        self.isStormCell = 0
        self.isOilRain = 0
        self.isMonsoon = 1

    def makeStormCell(self, elite=False):
        self.isHeavyRain = 0
        self.isFreezingRain = 0
        self.isStormCell = 1
        self.isOilRain = 0
        self.isMonsoon = 0

    def makePhase3(self):
        self.isPhase3 = 1

    def makeAmbassadorPhase3(self, elite=False):
        for headPart in self.headParts:
            headPart.removeNode()
        self.headParts = []
        self.generateHead3('prethinker2', animated=True)
        texture = loader.loadTexture('phase_9/maps/ttcc_ene_ambassador.png')
        for headPart in self.headParts:
            headPart.setTexture(texture, 1)

    def makeUnSyphon(self):
        self.isSyphon = 0

    def makeVulnerable(self):
        if self.suitColorTrack != None:
            self.suitColorTrack.finish()
        node = self.getGeomNode().getChild(0)
        self.suitColorTrack = Sequence(
                    LerpColorScaleInterval(node, duration=1, colorScale=(0.89, 0.608, 0.608, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(node, duration=1, colorScale=(1, 1, 1, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(node, duration=1, colorScale=(0.89, 0.608, 0.608, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(node, duration=1, colorScale=(1, 1, 1, 1)))
        self.suitColorTrack2 = Sequence(
                    LerpColorScaleInterval(node, duration=1, colorScale=(0.671, 0, 1, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(node, duration=1, colorScale=(1, 1, 1, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(node, duration=1, colorScale=(0.671, 0, 1, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(node, duration=1, colorScale=(1, 1, 1, 1)))
        self.isVulnerable = 1
        if not self.style.name in ['bcaster', 'cbutcher', 'hroller', 'hroller2', 'cdirector', 'phouse', 'dking', 'liquid', 'rkeeper'] and not self.isOverpressured:
            self.suitColorTrack.loop()
        if self.isOverpressured:
            self.suitColorTrack2.loop()

    def setVulnerability(self, num):
        if self.style.name == 'phouse':
        # ---- CLEANUP ----
            if hasattr(self, "knifeTrack") and self.knifeTrack:
                self.knifeTrack.pause()
                self.knifeTrack.finish()
                self.knifeTrack = None

            if hasattr(self, "knifePivot") and not self.knifePivot.isEmpty():
                self.knifePivot.removeNode()

            from math import pi, cos, sin

            self.vulnerability = max(1, num)
            totalKnives = (self.vulnerability / 5)

            radius = 1.5
            height = self.height

            # Shared pivot (orbit axis)
            self.knifePivot = self.attachNewNode("knifePivot")
            self.knifePivot.setZ(height - 1)

            knifeIntervals = []

            for i in range(totalKnives):
                # Load correct model
                knife = loader.loadModel('phase_5/models/props/lightning')
                knife.setScale(Point3(0.05, 0.05, 0.1))

                knife.reparentTo(self.knifePivot)

                # Even spacing
                angle = (2 * pi / totalKnives) * i
                knife.setPos(cos(angle) * radius,
                             sin(angle) * radius,
                             0)

                # Match original orientation
                knife.setHpr(0, 0, 0)

                # Individual knife spin (same as your first knife)
                spin = LerpHprInterval(
                    knife,
                    4.0,
                    VBase3(360.0, 0.0, 0.0),
                    startHpr=VBase3(0.0, 0.0, 0.0)
                )

                knifeIntervals.append(spin)

            # Pivot rotation (orbit)
            orbit = LerpHprInterval(
                self.knifePivot,
                4.0,
                VBase3(360, 0, 0),
                startHpr=VBase3(0, 0, 0)
            )

            # Run everything together
            self.knifeTrack = Parallel(
                orbit,
                *knifeIntervals
            )

            self.knifeTrack.loop()
        else:
            self.vulnerability = num

    def getVulnerability(self):
        return self.vulnerability

    def setRageBuilding(self, num):
        self.rageBuilding = num

    def getRageBuilding(self):
        return self.rageBuilding

    def makeKickback(self):
        self.isKickback = 1

    def makeUnKickback(self):
        self.isKickback = 0

    def setRPM(self, num):
        self.rpm = num

    def getRPM(self):
        return self.rpm

    def setRPMIncrease(self, num):
        self.rpmIncrease = num

    def getRPMIncrease(self):
        return self.rpmIncrease

    def setPowerhouseRotation(self, num):
        self.powerhouseRotation = num

    def getPowerhouseRotation(self):
        return self.powerhouseRotation

    def setDamageUp(self, num):
        self.damageMult = num

    def setRippedUp(self, num):
        self.rippedMult = num

    def getRippedUp(self):
        return self.rippedMult
    
    def makeRippedUp(self):
        self.ripped = 1

    def makeUnRippedUp(self, elite=False):
        self.ripped = 0

    def makeLureResist(self):
        self.isLureResist = 1

    def getDamageUp(self):
        return self.damageMult

    def setDamageDown(self, num):
        self.damageDownMult = num

    def getDamageDown(self):
        return self.damageDownMult

    def makeUnVulnerable(self):
        self.isVulnerable = 0
        self.vulnerability = 0
        if self.suitColorTrack != None:
            self.suitColorTrack.finish()

    def makeDead(self, elite=False):
        self.isDead = 1
        self.removeInsured()
        self.removeContracted()
        self.removeSoaked()
        self.removeSued()
        self.makeUnMarked()
        self.makeUnDazed()

    def makeUnDead(self, elite=False):
        self.isDead = 0

    def makeDazed(self):
        self.isDazed = 1

    def makeUnDazed(self):
        self.isDazed = 0

    def makeRevive(self, elite=False):
        self.isRevived = 1

    def makeLaserRevive(self, elite=False):
        self.isLaserRevived = 1

    def makeDamageUp(self):
        self.isDamageUp = 1

    def makeUnDamageUp(self, elite=False):
        self.isDamageUp = 0

    def makeDamageDown(self):
        self.isDamageDown = 1

    def makeUnDamageDown(self, elite=False):
        self.isDamageDown = 0

    def makeDamageReduction(self, elite=False):
        self.isDamageReduction = 1

    def makeUnDamageReduction(self, elite=False):
        self.isDamageReduction = 0

    def setDamageReduction(self, num):
        self.damageReduction = num

    def getDamageReduction(self):
        return self.damageReduction

    def makeFireEffect(self):
        self.makeUnAngry()
        BattleParticles.loadParticles()
        self.flameEffect = BattleParticles.createParticleEffect('FiredFlame3')
        BattleParticles.setEffectTexture(self.flameEffect, 'fire')

        self.flameEffect.reparentTo(self)
        self.flameEffect.setPos(0, 0, 0)

        self.flameTrack = ParticleInterval(self.flameEffect, self, duration=5)
        self.flameTrack.loop()

    def makeGreenLight(self, num):
        self.isGreenLight = num
        node = self.getGeomNode().getChild(0)
        self.suitColorTrack = Sequence(LerpColorScaleInterval(node, duration=1, colorScale=(0.537, 0.878, 0.533, 1),
                                                         blendType='easeInOut'),
                                  LerpColorScaleInterval(node, duration=1, colorScale=(1, 1, 1, 1),
                                                         blendType='easeInOut'),
                                  LerpColorScaleInterval(node, duration=1, colorScale=(0.537, 0.878, 0.533, 1),
                                                         blendType='easeInOut'),
                                  LerpColorScaleInterval(node, duration=1, colorScale=(1, 1, 1, 1)))
        self.suitColorTrack.loop()

    def makeRedLight(self, num):
        self.isRedLight = num
        node = self.getGeomNode().getChild(0)
        self.suitColorTrack = Sequence(LerpColorScaleInterval(node, duration=1, colorScale=(1, 0, 0, 1),
                                                         blendType='easeInOut'),
                                  LerpColorScaleInterval(node, duration=1, colorScale=(1, 1, 1, 1),
                                                         blendType='easeInOut'),
                                  LerpColorScaleInterval(node, duration=1, colorScale=(1, 0, 0, 1),
                                                         blendType='easeInOut'),
                                  LerpColorScaleInterval(node, duration=1, colorScale=(1, 1, 1, 1)))
        self.suitColorTrack.loop()

    def setChainsawTexRollContingency(self, abilityCount=0):
        # Clamp between 0 and 8
        abilityCount = max(0, min(abilityCount, 8))

        # 0 abilities = 2.0 sec
        # 8 abilities = 0.5 sec
        slowDuration = 2.0
        fastDuration = 0.5

        duration = slowDuration - (
            abilityCount / 8.0
        ) * (slowDuration - fastDuration)

        if self.texRollIval:
            self.texRollIval.pause()

        for headPart in self.headParts:
            self.texRollIval = self.chainsawMoveInterval(
                headPart.find('**/Chain'),
                duration=duration
            )
            self.texRollIval.loop()

    def setChainsawTexRoll(self, duration=1.6):
        # Can also be called in cutscene to make the chainsaw roll faster or slower.
        if self.texRollIval:
            self.texRollIval.pause()
        if duration <= 0:
            self.texRollIval = None
            return

        for headPart in self.headParts:
            self.texRollIval = self.chainsawMoveInterval(headPart.find('**/Chain'), duration=duration)
            self.texRollIval.loop()

    @staticmethod
    def chainsawMoveInterval(obj, duration=2.0):
        def rollTexMatrix(t, obj=obj):
            obj.setTexOffset(TextureStage.getDefault(), t, 0)

        return LerpFunctionInterval(rollTexMatrix, fromData=1, toData=0, duration=duration)

    def makeUnGreenLight(self):
        self.isGreenLight = 0
        if self.suitColorTrack != None:
            self.suitColorTrack.finish()

    def makeUnRedLight(self):
        self.isRedLight = 0
        if self.suitColorTrack != None:
            self.suitColorTrack.finish()

    def makeAngry(self, num):
        self.isAngry = num

    def makeUnAngry(self):
        self.isAngry = 0

        if hasattr(self, "flameTrack") and self.flameTrack:
            try:
                self.flameTrack.pause()
            except:
                pass
            try:
                self.flameTrack.finish()
            except:
                pass
            self.flameTrack = None

        if hasattr(self, "flameEffect") and self.flameEffect:
            effect = self.flameEffect
            self.flameEffect = None

            try:
                effect.disable()
            except:
                pass

            try:
                if hasattr(effect, 'renderParent'):
                    effect.cleanup()
            except:
                pass

            try:
                effect.detachNode()
            except:
                pass

    def makeCollectCall(self, num):
        self.isCollectCall = num
        # ---- CLEANUP ----
        if hasattr(self, "knifeTrack") and self.knifeTrack:
            self.knifeTrack.pause()
            self.knifeTrack.finish()
            self.knifeTrack = None

        if hasattr(self, "knifePivot") and not self.knifePivot.isEmpty():
            self.knifePivot.removeNode()

        from math import pi, cos, sin
        totalKnives = self.isCollectCall

        radius = 1.5
        height = self.height + 3

        # Shared pivot (orbit axis)
        self.knifePivot = self.attachNewNode("knifePivot")
        self.knifePivot.setZ(height)

        knifeIntervals = []

        for i in range(totalKnives):
            # Load correct model
            knife = globalPropPool.getProp(random.choice(('10dollar', '1dollar', '5dollar', '50dollar')))
            knife.setTwoSided(True)
            knife.setScale(1)

            knife.reparentTo(self.knifePivot)

            # Even spacing
            angle = (2 * pi / totalKnives) * i
            knife.setPos(cos(angle) * radius,
                         sin(angle) * radius,
                         0)

            # Match original orientation
            knife.lookAt(self.knifePivot)
            knife.setP(270)

            # Individual knife spin (same as your first knife)
            # spin = LerpHprInterval(
            #     knife,
            #     4.0,
            #     VBase3(360.0, 270.0, 0.0),
            #     startHpr=VBase3(0.0, 270.0, 0.0)
            # )
            #
            # knifeIntervals.append(spin)

        # Pivot rotation (orbit)
        orbit = LerpHprInterval(
            self.knifePivot,
            4.0,
            VBase3(360, 0, 0),
            startHpr=VBase3(0, 0, 0)
        )

        # Run everything together
        self.knifeTrack = Parallel(
            orbit,
            *knifeIntervals
        )

        self.knifeTrack.loop()

    def setCollectCall(self, num):
        self.collectCallMult = num

    def getCollectCall(self):
        return self.collectCallMult

    def getEnrageCounter(self):
        return self.isAngry

    def makeUnShielding(self, elite=False):
        self.isShielding = 0

    def makeShielding(self):
        self.isShielding = 1
        self.isAngry = 0

    def makeWetFirestarter(self, elite=False):
        anims = self.generateAnimDict()
        for headPart in self.headParts:
            if not self.isSkeleton:
                headPart.find('**/fire0').hide()
                headPart.find('**/fire1').hide()
                headPart.find('**/fire2').hide()
                headPart.find('**/fire3').hide()
                headPart.find('**/fire4').hide()
                headPart.find('**/fire5').hide()

    def makeDryFirestarter(self, elite=False):
        anims = self.generateAnimDict()
        for headPart in self.headParts:
            if not self.isSkeleton:
                headPart.find('**/fire0').show()
                headPart.find('**/fire1').show()
                headPart.find('**/fire2').show()
                headPart.find('**/fire3').show()
                headPart.find('**/fire4').show()
                headPart.find('**/fire5').show()

    def generateHeadLitigator(self, headType, headColor=None, headTexture=None, modelOverride=None, pathOverride=None,
                     extraArgs={}, animated=False, additionalAnims=[]):
        if base.config.GetBool('want-new-cogs', False):
            filePrefix, phase = HeadModelDict[self.style.body]
        else:
            filePrefix, phase = ModelDict[self.style.body]
        '''if modelOverride:
            headModel = loader.loadModel(modelOverride)
        else:
            headModel = loader.loadModel('phase_' + str(phase) + filePrefix + 'heads')'''
        if animated:
            animDict = self.generateAnimDict()
            self.loadAnims(animDict)
            if headType == 'skelecog' or headType == 'overwhelmingauthorizer' or headType == 'executioner':
                if headType == 'overwhelmingauthorizer':
                    headModel = Actor.Actor('phase_14/models/char/ttcc_ene_%s%s-zero' % (
                    headType, '_exe' if self.isExecutive or self.isManager else ''))
                elif headType == 'executioner':
                    headModel = Actor.Actor('phase_14/models/char/ttcc_ene_executioner-zero')
                else:
                    headModel = Actor.Actor(
                        'phase_14/models/char/cog' + string.upper(self.style.body) + '_robot_head-zero')
                self.generateHeadAnims(
                    'phase_14/models/char/cog' + string.upper(self.style.body) + '_robot_head-',
                    headModel, additionalAnims)
                self.animatedHeadParts.append(headModel)
                if headType != 'overwhelmingauthorizer':
                    if headTexture:
                        try:
                            texture = loader.loadTexture('phase_5/maps/' + headTexture)
                        except:
                            texture = loader.loadTexture('phase_14/maps/' + headTexture)
                    else:
                        if self.style.dept == None:
                            texture = loader.loadTexture('phase_14/maps/ttcc_ene_skelecog_unemployed.png')
                        else:
                            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s%s.png' % (
                            self.style.dept, '_exe' if self.isExecutive or self.isManager else '',))
                    for headPart in self.animatedHeadParts:
                        headPart.setTexture(texture, 1)
            else:
                headModel = Actor.Actor('phase_14/models/char/ttcc_ene_' + headType + '-zero')
                self.generateHeadAnims('phase_14/models/char/ttcc_ene_' + headType + '-', headModel,
                                           additionalAnims)
                self.animatedHeadParts.append(headModel)
            headModel.reparentTo(self.find('**/joint_head'))
            headModel.setBlend(frameBlend=base.wantSmoothAnims)
            if 'x' in extraArgs:
                if extraArgs['x'] != None:
                    headModel.setX(extraArgs['x'])
            if 'y' in extraArgs:
                if extraArgs['y'] != None:
                    headModel.setY(extraArgs['y'])
            if 'z' in extraArgs:
                if extraArgs['z'] != None:
                    headModel.setZ(extraArgs['z'])
            if 'h' in extraArgs:
                if extraArgs['h'] != None:
                    headModel.setH(extraArgs['h'])
            if 'p' in extraArgs:
                if extraArgs['p'] != None:
                    headModel.setP(extraArgs['p'])
            if 'r' in extraArgs:
                if extraArgs['r'] != None:
                    headModel.setR(extraArgs['r'])
            if 'scale' in extraArgs:
                if extraArgs['scale'] != None:
                    headModel.setScale(*extraArgs['scale'])
            self.headParts.append(headModel)
        else:
            if headType == 'skelecog':
                if base.config.GetBool('want-clash-assets', False):
                    headModel = loader.loadModel(
                        'phase_14/models/char/cog' + string.upper(self.style.body) + '_robot_head-zero')
                    headReferences = headModel.findAllMatches('**/skeleskull_' + string.upper(self.style.body))
                else:
                    headModel = loader.loadModel(
                        'phase_5/models/char/cog' + string.upper(self.style.body) + '_robot-head')
                    headReferences = headModel.findAllMatches('**/suit' + string.upper(self.style.body))
            else:
                if pathOverride:
                    headModel = loader.loadModel(pathOverride + headType)
                else:
                    if modelOverride:
                        headModel = loader.loadModel(modelOverride)
                        headReferences = headModel.findAllMatches('**/' + headType)
                    else:
                        try:
                            headModel = loader.loadModel('phase_' + str(phase) + '/models/char/' + headType)
                            headReferences = headModel.findAllMatches('**/' + headType + '.egg')
                        except:
                            headModel = loader.loadModel('phase_' + str(phase) + filePrefix + 'heads')
                            headReferences = headModel.findAllMatches('**/' + headType)
            if pathOverride:
                if headTexture:
                    pass
                if headColor:
                    headModel.setColor(headColor)
                if 'x' in extraArgs:
                    if extraArgs['x'] != None:
                        headModel.setX(extraArgs['x'])
                if 'y' in extraArgs:
                    if extraArgs['y'] != None:
                        headModel.setY(extraArgs['y'])
                if 'z' in extraArgs:
                    if extraArgs['z'] != None:
                        headModel.setZ(extraArgs['z'])
                if 'h' in extraArgs:
                    if extraArgs['h'] != None:
                        headModel.setH(extraArgs['h'])
                if 'p' in extraArgs:
                    if extraArgs['p'] != None:
                        headModel.setP(extraArgs['p'])
                if 'r' in extraArgs:
                    if extraArgs['r'] != None:
                        headModel.setR(extraArgs['r'])
                if 'scale' in extraArgs:
                    if extraArgs['scale'] != None:
                        headModel.setScale(*extraArgs['scale'])
                self.headParts.append(headModel)
            else:
                for i in range(0, headReferences.getNumPaths()):
                    if self.style.body == 'a' or self.style.body == 'b':
                        headPart = self.instance(headReferences.getPath(i), 'modelRoot', 'to_head')
                    else:
                        headPart = self.instance(headReferences.getPath(i), 'modelRoot', 'joint_head')
                    if headTexture:
                        try:
                            headTex = loader.loadTexture('phase_' + str(phase) + '/maps/' + headTexture)
                        except:
                            try:  # Will work on a more viable replacement for specific phases later.
                                headTex = loader.loadTexture('phase_5/maps/' + headTexture)
                            except:
                                try:
                                    headTex = loader.loadTexture('phase_11/maps/' + headTexture)
                                except:
                                    headTex = loader.loadTexture('phase_14/maps/' + headTexture)
                        headPart.setTexture(headTex, 1)
                    if headColor:
                        headPart.setColor(headColor)
                    if 'x' in extraArgs:
                        if extraArgs['x'] != None:
                            headPart.setX(extraArgs['x'])
                    if 'y' in extraArgs:
                        if extraArgs['y'] != None:
                            headPart.setY(extraArgs['y'])
                    if 'z' in extraArgs:
                        if extraArgs['z'] != None:
                            headPart.setZ(extraArgs['z'])
                    if 'h' in extraArgs:
                        if extraArgs['h'] != None:
                            headPart.setH(extraArgs['h'])
                    if 'p' in extraArgs:
                        if extraArgs['p'] != None:
                            headPart.setP(extraArgs['p'])
                    if 'r' in extraArgs:
                        if extraArgs['r'] != None:
                            headPart.setR(extraArgs['r'])
                    if 'scale' in extraArgs:
                        if extraArgs['scale'] != None:
                            headPart.setScale(*extraArgs['scale'])
                    if headType == 'suitA' or headType == 'suitB' or headType == 'suitC':
                        headPart.setZ(headPart.getZ() + {
                            'suitA': -6.05,
                            'suitB': -5.09477996826172,
                            'suitC': -4.15
                        }[headType])
                        if self.isExecutive or self.isManager:
                            if self.style.name == 'mbr':
                                headPart.setColor(VBase4(0.825, 0.6, 0.425, 1.0))
                            else:
                                if headColor == None:
                                    headPart.setColor({
                                                          'c': SuitDNA.corpPolyColor,
                                                          'l': SuitDNA.legalPolyColor,
                                                          'm': SuitDNA.moneyPolyColor,
                                                          's': SuitDNA.salesPolyColor,
                                                          'g': SuitDNA.boardPolyColor,
                                                          None: VBase4(0.5, 0.5, 0.5, 1.0)
                                                      }[SuitDNA.getSuitDept(self.style.name)])
                        else:
                            if self.style.name == 'mbr':
                                headPart.setColor(VBase4(1.0, 0.25, 0.0, 1.0))
                    self.headParts.append(headPart)
                headModel.removeNode()

    def generateHeadZap(self, headType, headColor=None, headTexture=None,
                        modelOverride=None, pathOverride=None, extraArgs={},
                        animated=False, additionalAnims=[], targetActor=None):

        if targetActor is None:
            targetActor = self

        if not hasattr(self, 'zapActorHeadParts'):
            self.zapActorHeadParts = []

        if base.config.GetBool('want-new-cogs', False):
            filePrefix, phase = HeadModelDict[self.style.body]
        else:
            filePrefix, phase = ModelDict[self.style.body]

        def applyExtraArgs(node):
            if 'x' in extraArgs and extraArgs['x'] is not None:
                node.setX(extraArgs['x'])
            if 'y' in extraArgs and extraArgs['y'] is not None:
                node.setY(extraArgs['y'])
            if 'z' in extraArgs and extraArgs['z'] is not None:
                node.setZ(extraArgs['z'])
            if 'h' in extraArgs and extraArgs['h'] is not None:
                node.setH(extraArgs['h'])
            if 'p' in extraArgs and extraArgs['p'] is not None:
                node.setP(extraArgs['p'])
            if 'r' in extraArgs and extraArgs['r'] is not None:
                node.setR(extraArgs['r'])
            if 'scale' in extraArgs and extraArgs['scale'] is not None:
                node.setScale(*extraArgs['scale'])

        def getHeadJoint():
            if self.style.body == 'a' or self.style.body == 'b':
                joint = targetActor.find('**/to_head')
                if joint.isEmpty():
                    joint = targetActor.find('**/joint_head')
            else:
                joint = targetActor.find('**/joint_head')

            if joint.isEmpty():
                joint = targetActor.find('**/joint_headFront')

            return joint

        if animated:
            if headType == 'skelecog' or headType == 'overwhelmingauthorizer' or headType == 'executioner':
                if headType == 'overwhelmingauthorizer':
                    headModel = Actor.Actor(
                        'phase_14/models/char/ttcc_ene_%s%s-zero' %
                        (headType, '_exe' if self.isExecutive or self.isManager else '')
                    )
                elif headType == 'executioner':
                    headModel = Actor.Actor('phase_14/models/char/ttcc_ene_executioner-zero')
                else:
                    headModel = Actor.Actor(
                        'phase_14/models/char/cog%s_robot_head-zero' %
                        string.upper(self.style.body)
                    )

                self.generateHeadAnims(
                    'phase_14/models/char/cog%s_robot_head-' %
                    string.upper(self.style.body),
                    headModel,
                    additionalAnims
                )

                if headType != 'overwhelmingauthorizer':
                    if headTexture:
                        try:
                            texture = loader.loadTexture('phase_5/maps/' + headTexture)
                        except:
                            texture = loader.loadTexture('phase_14/maps/' + headTexture)
                    else:
                        if self.style.dept is None:
                            texture = loader.loadTexture('phase_14/maps/ttcc_ene_skelecog_unemployed.png')
                        else:
                            texture = loader.loadTexture(
                                'phase_5/maps/ttcc_ene_skelecog_%s%s.png' %
                                (self.style.dept, '_exe' if self.isExecutive or self.isManager else '')
                            )
                    headModel.setTexture(texture, 1)

            else:
                headModel = Actor.Actor('phase_14/models/char/ttcc_ene_' + headType + '-zero')
                self.generateHeadAnims(
                    'phase_14/models/char/ttcc_ene_' + headType + '-',
                    headModel,
                    additionalAnims
                )

            joint = getHeadJoint()
            if not joint.isEmpty():
                headModel.reparentTo(joint)
            else:
                headModel.reparentTo(targetActor)

            headModel.setBlend(frameBlend=base.wantSmoothAnims)

            try:
                #headModel.loop('stun')
                headModel.pose('stun', 5)
            except:
                pass

            applyExtraArgs(headModel)

            self.zapActorHeadParts.append(headModel)
            return [headModel]

        # non-animated path
        if headType == 'skelecog':
            if base.config.GetBool('want-clash-assets', False):
                headModel = loader.loadModel(
                    'phase_14/models/char/cog%s_robot_head-zero' %
                    string.upper(self.style.body)
                )
                headReferences = headModel.findAllMatches('**/skeleskull_' + string.upper(self.style.body))
            else:
                headModel = loader.loadModel(
                    'phase_5/models/char/cog%s_robot-head' %
                    string.upper(self.style.body)
                )
                headReferences = headModel.findAllMatches('**/suit' + string.upper(self.style.body))
        else:
            if pathOverride:
                headModel = loader.loadModel(pathOverride + headType)
                headReferences = None
            elif modelOverride:
                headModel = loader.loadModel(modelOverride)
                headReferences = headModel.findAllMatches('**/' + headType)
            else:
                try:
                    headModel = loader.loadModel('phase_' + str(phase) + '/models/char/' + headType)
                    headReferences = headModel.findAllMatches('**/' + headType + '.egg')
                except:
                    headModel = loader.loadModel('phase_' + str(phase) + filePrefix + 'heads')
                    headReferences = headModel.findAllMatches('**/' + headType)

        createdParts = []

        if pathOverride:
            headPart = headModel
            joint = getHeadJoint()

            if not joint.isEmpty():
                headPart.reparentTo(joint)
            else:
                headPart.reparentTo(targetActor)

            if headColor:
                headPart.setColor(headColor)

            applyExtraArgs(headPart)

            self.zapActorHeadParts.append(headPart)
            createdParts.append(headPart)
            return createdParts

        for i in xrange(headReferences.getNumPaths()):
            src = headReferences.getPath(i)

            # IMPORTANT: do NOT use self.instance here.
            # self.instance attaches to self. We copy to the target actor's head joint instead.
            joint = getHeadJoint()

            if not joint.isEmpty():
                headPart = src.copyTo(joint)
            else:
                headPart = src.copyTo(targetActor)

            if headTexture:
                try:
                    headTex = loader.loadTexture('phase_' + str(phase) + '/maps/' + headTexture)
                except:
                    try:
                        headTex = loader.loadTexture('phase_5/maps/' + headTexture)
                    except:
                        try:
                            headTex = loader.loadTexture('phase_11/maps/' + headTexture)
                        except:
                            headTex = loader.loadTexture('phase_14/maps/' + headTexture)

                headPart.setTexture(headTex, 1)

            if headColor:
                headPart.setColor(headColor)

            applyExtraArgs(headPart)

            if headType == 'suitA' or headType == 'suitB' or headType == 'suitC':
                headPart.setZ(headPart.getZ() + {
                    'suitA': -6.05,
                    'suitB': -5.09477996826172,
                    'suitC': -4.15
                }[headType])

                if self.isExecutive or self.isManager:
                    if self.style.name == 'mbr':
                        headPart.setColor(VBase4(0.825, 0.6, 0.425, 1.0))
                    elif headColor is None:
                        headPart.setColor({
                            'c': SuitDNA.corpPolyColor,
                            'l': SuitDNA.legalPolyColor,
                            'm': SuitDNA.moneyPolyColor,
                            's': SuitDNA.salesPolyColor,
                            'g': SuitDNA.boardPolyColor,
                            None: VBase4(0.5, 0.5, 0.5, 1.0)
                        }[SuitDNA.getSuitDept(self.style.name)])
                else:
                    if self.style.name == 'mbr':
                        headPart.setColor(VBase4(1.0, 0.25, 0.0, 1.0))

            self.zapActorHeadParts.append(headPart)
            createdParts.append(headPart)

        headModel.removeNode()
        return createdParts

    def makeWetLitigator(self, elite=False):
        anims = self.generateAnimDict()
        for headPart in self.headParts:
            headPart.removeNode()
        self.headParts = []
        self.generateHeadLitigator('litigator-nf', animated=True)
        texture = loader.loadTexture('phase_11/maps/ttcc_ene_litigator.png')
        for headPart in self.headParts:
            headPart.setTexture(texture, 1)

    def makeDryLitigator(self, elite=False):
        anims = self.generateAnimDict()
        for headPart in self.headParts:
            headPart.removeNode()
        self.headParts = []
        self.generateHeadLitigator('litigator', animated=True)
        texture = loader.loadTexture('phase_11/maps/ttcc_ene_litigator.png')
        for headPart in self.headParts:
            headPart.setTexture(texture, 1)

    def makeWetTreasurer(self, elite=False):
        anims = self.generateAnimDict()
        for headPart in self.headParts:
            headPart.removeNode()
        self.headParts = []
        self.generateHeadLitigator('litigator-nf', animated=True)
        texture = loader.loadTexture('phase_11/maps/ttcc_ene_treasurer.png')
        for headPart in self.headParts:
            headPart.setTexture(texture, 1)

    def makeDryTreasurer(self, elite=False):
        anims = self.generateAnimDict()
        for headPart in self.headParts:
            headPart.removeNode()
        self.headParts = []
        self.generateHeadLitigator('litigator', animated=True)
        texture = loader.loadTexture('phase_11/maps/ttcc_ene_treasurer.png')
        for headPart in self.headParts:
            headPart.setTexture(texture, 1)

    def makeContingencyOverride(self, elite=False):
        self.isChainsawPhase2 = 1
        anims = self.generateAnimDict()
        for headPart in self.headParts:
            headPart.removeNode()
        self.headParts = []
        self.generateHead3('chainsaw_b', animated=True)
        self.setSuitStatusEffect('contingencyOverride')
        texture2 = loader.loadTexture('phase_12/maps/ttcc_ene_chainsaw_b_boardbot.png')
        for headPart in self.headParts:
            headPart.setTexture(texture2, 1)
        self.setChainsawTexRollContingency(self.getSuitStatusModifier('contingencyAbilities'))

    def removeContingencyOverride(self, elite=False):
        self.isChainsawPhase2 = 1
        anims = self.generateAnimDict()
        for headPart in self.headParts:
            headPart.removeNode()
        self.headParts = []
        self.generateHead3('chainsaw', animated=True)
        self.clearSuitStatusEffect('contingencyOverride')
        self.setSuitStatusEffect('contingencyOverrideBroken')
        texture2 = loader.loadTexture('phase_12/maps/ttcc_ene_chainsaw_boardbot.png')
        for headPart in self.headParts:
            headPart.setTexture(texture2, 1)
            headPart.find('**/bulbLeft').hide()
            headPart.find('**/bulbRight').hide()
            self.setupHeadFreakout(headPart, normalTexture=loader.loadTexture('phase_12/maps/ttcc_ene_chainsaw_boardbot.png'), hurtTexture=loader.loadTexture('phase_12/maps/ttcc_ene_chainsaw_boardbot.png'), glitchTexture=loader.loadTexture('phase_12/maps/ttcc_ene_chainsaw_b_boardbot.png'))
            self.startHeadFreakout()
        self.setChainsawTexRollContingency(self.getSuitStatusModifier('contingencyAbilities'))

    def makeChairmanPhase2(self, elite=False):
        anims = self.generateAnimDict()
        for headPart in self.headParts:
            headPart.removeNode()
        self.headParts = []
        self.generateHead3('chairman-a', animated=True)
        self.generateHeadLitigator = 1
        texture2 = loader.loadTexture('phase_14/maps/ttcc_ene_chairman.png')
        for headPart in self.headParts:
            headPart.setTexture(texture2, 1)

    def makeOttomanPhase2(self, elite=False):
        self.isOttomanPhase2 = 1

    def makeChainsawPhase3(self, elite=False):
        self.isChainsawPhase2 = 0
        self.isChainsawPhase3 = 1
        anims = self.generateAnimDict()
        for headPart in self.headParts:
            headPart.removeNode()
        self.headParts = []
        self.generateHead3('chainsaw', animated=True)
        texture2 = loader.loadTexture('phase_12/maps/ttcc_ene_chainsaw_boardbot.png')
        for headPart in self.headParts:
            headPart.setTexture(texture2, 1)
            headPart.find('**/bulbLeft').hide()

    def makeExecutive(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isExecutive = 1
        if self.isSkeleton:
            self.setSuitClothesSkeleton()
            if self.style.body == 'a' and not self.style.name == 'clubpres' and not self.style.name == 'autocad':
                texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_exe.png' %
                                             self.style.dept)
                for headPart in self.headParts:
                    headPart.setTexture(texture, 1)
            if self.style.body == 'b':
                texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_exe.png' %
                                             self.style.dept)
                for headPart in self.headParts:
                    headPart.setTexture(texture, 1)
            if self.style.body == 'c' and not self.style.name == 'dopa' and not self.style.name == 'dopr':
                texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_exe.png' %
                                             self.style.dept)
                for headPart in self.headParts:
                    headPart.setTexture(texture, 1)
        elif self.style.name == 'ins':
            self.setSuitClothes()
            texture = loader.loadTexture('phase_14/maps/cc_t_ene_insider%s.png' % (
                '_exe' if self.isExecutive or self.isGovernaught else '',))
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
        elif self.style.name == 'hho':
            self.setSuitClothes()
            texture = loader.loadTexture('phase_14/maps/cc_t_ene_headhoncho%s.png' % (
                '_exe' if self.isExecutive or self.isGovernaught else '',))
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
        elif self.style.name == 'bgh':
            self.setSuitClothes()
            texture = loader.loadTexture('phase_14/maps/cc_t_ene_bagholder%s.png' % (
                '_exe' if self.isExecutive or self.isGovernaught else '',))
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
        else:
            self.setSuitClothes()

    def makeManager(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        if self.isSkeleton:
            self.setSuitClothesSkeleton()
            if self.style.body == 'a' and self.style.name == 'radiog':
                texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_exe.png' %
                                             self.style.dept)
                modelRoot.find('**/necktie-w').setTexture(texture, 1)
            if self.style.body == 'a' and self.style.name == 'cdirector':
                texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_exe.png' %
                                             self.style.dept)
                modelRoot.find('**/necktie-w').setTexture(texture, 1)
            if self.style.body == 'a' and self.style.name == 'laa':
                texture2 = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s.png' %
                                             self.style.dept)
                modelRoot.find('**/necktie-w').setTexture(texture2, 1)
                modelRoot.find('**/necktie-w').show()
                modelRoot.find('**/bowtie').hide()
            if self.style.body == 'a' and not self.style.name == 'derrhand' and not self.style.name == 'dold' and not self.style.name == 'cdirector' and not self.style.name == 'radiog' \
                and not self.style.name == 'charon' and not self.style.name == 'autocad' and not self.style.name == 'clubpres' and not self.style.name == 'hydra' and not self.style.name == 'kerberos' and not self.style.name == 'nix' and not self.style.name == 'styx':
                texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_exe.png' %
                                             self.style.dept)
                for headPart in self.headParts:
                    headPart.setTexture(texture, 1)
                modelRoot.find('**/body').setTexture(texture, 1)
                modelRoot.find('**/necktie-s').setTexture(texture, 1)
                textureWSI = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s.png' % self.style.dept)
                if self.style.name == 'wsi':
                    modelRoot.find('**/necktie-w').setTexture(textureWSI, 1)
                else:
                    modelRoot.find('**/necktie-w').setTexture(texture, 1)
                modelRoot.find('**/bowtie').setTexture(texture, 1)
            if self.style.body == 'b' and not self.style.name == 'charon' and not self.style.name == 'hydra' and not self.style.name == 'kerberos' and not self.style.name == 'nix' and not self.style.name == 'styx':
                texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_exe.png' %
                                             self.style.dept)
                for headPart in self.headParts:
                    headPart.setTexture(texture, 1)
                modelRoot.find('**/body').setTexture(texture, 1)
                modelRoot.find('**/necktie-s').setTexture(texture, 1)
                modelRoot.find('**/necktie-w').setTexture(texture, 1)
                modelRoot.find('**/bowtie').setTexture(texture, 1)
            if self.style.body == 'c' and self.style.name == 'dopa' or self.style.name == 'dopr':
                texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_exe.png' %
                                             self.style.dept)
                modelRoot.find('**/body').setTexture(texture, 1)
                modelRoot.find('**/necktie-s').setTexture(texture, 1)
                modelRoot.find('**/necktie-w').setTexture(texture, 1)
                modelRoot.find('**/bowtie').setTexture(texture, 1)
            if self.style.body == 'c' and not self.style.name == 'dopr' and not self.style.name == 'dopa' and not self.style.name == 'charon' and not self.style.name == 'hydra' and not self.style.name == 'kerberos' and not self.style.name == 'nix' and not self.style.name == 'styx':
                texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_exe.png' %
                                             self.style.dept)
                for headPart in self.headParts:
                    headPart.setTexture(texture, 1)
                modelRoot.find('**/body').setTexture(texture, 1)
                modelRoot.find('**/necktie-s').setTexture(texture, 1)
                modelRoot.find('**/necktie-w').setTexture(texture, 1)
                modelRoot.find('**/bowtie').setTexture(texture, 1)
        else:
            self.isManager = 1

    def makeHighRoller(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        try:
            texture = loader.loadTexture('phase_12/maps/cc_t_ene_highroller_suit_black.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
        modelRoot.find('**/body').setTexture(texture, 1)


    def makeDuckShuffler(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        try:
            texture = loader.loadTexture('phase_10/maps/ttcc_ene_suittex_duckshfl.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
        modelRoot.find('**/body').setTexture(texture, 1)

    def makeHighRollerWhite(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        try:
            texture = loader.loadTexture('phase_12/maps/cc_t_ene_highroller_suit.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
        modelRoot.find('**/body').setTexture(texture, 1)

    def makeBoardbotManager(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        try:
            texture = loader.loadTexture('phase_3.5/maps/ttcc_ene_suittex_g_e.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
        modelRoot.find('**/body').setTexture(texture, 1)

    def makeBoardbotManager2(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        try:
            texture = loader.loadTexture('phase_3.5/maps/ttcc_ene_suittex_g_e2.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
        modelRoot.find('**/body').setTexture(texture, 1)

    def makePrethinker(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        try:
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_suittex_prethink.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
        modelRoot.find('**/body').setTexture(texture, 1)

    def makeMultislacker(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        try:
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_suittex_mslacker.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
        modelRoot.find('**/body').setTexture(texture, 1)

    def makePacesetter(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        try:
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_suittex_pacesetter.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
        modelRoot.find('**/body').setTexture(texture, 1)
        modelRoot.find('**/necktie-s').hide()
        modelRoot.find('**/necktie-w').hide()

    def makeHustler(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        try:
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_suittex_hustler.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
        modelRoot.find('**/body').setTexture(texture, 1)
        modelRoot.find('**/necktie-s').hide()
        modelRoot.find('**/necktie-w').hide()

    def makeCountErclaim(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        try:
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_suittex_count.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
        modelRoot.find('**/body').setTexture(texture, 1)
        modelRoot.find('**/bowtie').hide()
        modelRoot.find('**/necktie-s').hide()
        modelRoot.find('**/necktie-w').hide()

    def makeRedd(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        try:
            texture = loader.loadTexture('phase_3.5/maps/ttcc_ene_suittex_l_e.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
        modelRoot.find('**/body').setTexture(texture, 1)
        modelRoot.find('**/bowtie').hide()

    def makePlutocrat(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        try:
            texture = loader.loadTexture('phase_10/maps/ttcc_ene_suittex_pcrat.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
        modelRoot.find('**/body').setTexture(texture, 1)

    def makeMouthpiece(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        try:
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_suittex_mouthp.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
        modelRoot.find('**/body').setTexture(texture, 1)

    def makeMajorPlayer(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        try:
            texture = loader.loadTexture('phase_12/maps/ttcc_ene_suittex_mplayer.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
        modelRoot.find('**/body').setTexture(texture, 1)

    def makeFeatherbedder(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        try:
            texture = loader.loadTexture('phase_12/maps/ttcc_ene_suittex_fbed.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
        modelRoot.find('**/body').setTexture(texture, 1)

    def makeFirestarter(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        try:
            texture = loader.loadTexture('phase_12/maps/ttcc_ene_suittex_fires.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
        modelRoot.find('**/body').setTexture(texture, 1)

    def makeChainsaw(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        try:
            texture = loader.loadTexture('phase_12/maps/ttcc_ene_suittex_chainsaw.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
        modelRoot.find('**/body').setTexture(texture, 1)

    def makeVideographer(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        try:
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_suittex_videographer.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
        modelRoot.find('**/body').setTexture(texture, 1)

    def makeVideographer2(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        try:
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_suittex_videographer2.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
        modelRoot.find('**/body').setTexture(texture, 1)

    def makeDeepDiver(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        try:
            texture = loader.loadTexture('phase_14/maps/ttcc_ene_suittex_ddiver.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
        modelRoot.find('**/body').setTexture(texture, 1)
        modelRoot.find('**/necktie-s').hide()
        modelRoot.find('**/necktie-w').hide()

    def makeGatekeeper(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        try:
            texture = loader.loadTexture('phase_14/maps/ttcc_ene_suittex_gatekeep.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
        modelRoot.find('**/body').setTexture(texture, 1)
        modelRoot.find('**/necktie-s').hide()
        modelRoot.find('**/necktie-w').hide()

    def makeWSI(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        try:
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_l_exe.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
        modelRoot.find('**/body').setTexture(texture, 1)

    def makeBellringer(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        try:
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_suittex_bellring.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
        modelRoot.find('**/body').setTexture(texture, 1)
        modelRoot.find('**/necktie-s').hide()
        modelRoot.find('**/necktie-w').hide()

    def makeTreekiller(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        try:
            texture = loader.loadTexture('phase_10/maps/ttcc_ene_suittex_treek.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
        modelRoot.find('**/body').setTexture(texture, 1)

    def makeAutocaddie(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        try:
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_c_exe.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
        modelRoot.find('**/body').setTexture(texture, 1)

    def makeDOPA(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isManager = 1
        try:
            texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_s_exe.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
        modelRoot.find('**/body').setTexture(texture, 1)

    def makeCountErfit(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isGovernaught = 1
        try:
            texture = loader.loadTexture('phase_10/maps/ttcc_ene_suittex_erfit.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
        modelRoot.find('**/body').setTexture(texture, 1)

    def makeRacketeer(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isGovernaught = 1
        try:
            texture = loader.loadTexture('phase_3.5/maps/ttcc_ene_suittex_racket_cash.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
        modelRoot.find('**/body').setTexture(texture, 1)

    def makeBuffHighRoller(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isGovernaught = 1
        try:
            texture = loader.loadTexture('phase_12/maps/ttcc_ene_suittex_hroller_buff.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
        modelRoot.find('**/body').setTexture(texture, 1)

    def makeBuffLitigator(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isGovernaught = 1
        try:
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_suittex_lgator_buff.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
        modelRoot.find('**/body').setTexture(texture, 1)

    def makeBuffCaseManager(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isGovernaught = 1
        try:
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_suittex_caseman_buff.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
        modelRoot.find('**/body').setTexture(texture, 1)

    def makeCountErfitTrainer(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isGovernaught = 1
        try:
            texture = loader.loadTexture('phase_11/maps/ttcc_ene_suittex_counterfit2.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
        modelRoot.find('**/body').setTexture(texture, 1)

    def makeDummy(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isGovernaught = 1
        try:
            texture = loader.loadTexture('phase_4/maps/schoolhouse/dummy/ttcc_ene_suittex_djockey.png')
        except:  # Not sure when or if you'll need this, but just in case the above fails, this should work as a fail-safe.
            texture = loader.loadTexture(
                'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
        modelRoot.find('**/body').setTexture(texture, 1)

    def makeGovernaught(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        self.isGovernaught = 1
        if self.isSkeleton:
            self.setSuitClothesSkeleton()
            if self.style.body == 'a' and not self.dna.name in ['mh2', 'cnd2', 'std2']:
                texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_gov.png' % self.style.dept)
                for headPart in self.headParts:
                    headPart.setTexture(texture, 1)
            if self.style.body == 'b':
                texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_gov.png' % self.style.dept)
                for headPart in self.headParts:
                    headPart.setTexture(texture, 1)
            if self.style.body == 'c':
                texture = loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_%s_gov.png' % self.style.dept)
                for headPart in self.headParts:
                    headPart.setTexture(texture, 1)
        elif self.style.name == 'ins':
            self.setSuitClothes()
            texture = loader.loadTexture('phase_14/maps/cc_t_ene_insider%s.png' % (
                '_gov' if self.isExecutive or self.isGovernaught else '',))
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
        elif self.style.name == 'hho':
            self.setSuitClothes()
            texture = loader.loadTexture('phase_14/maps/cc_t_ene_headhoncho%s.png' % (
                '_gov' if self.isExecutive or self.isGovernaught else '',))
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
        elif self.style.name == 'bgh':
            self.setSuitClothes()
            texture = loader.loadTexture('phase_14/maps/cc_t_ene_bagholder%s.png' % (
                '_gov' if self.isExecutive or self.isGovernaught else '',))
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
        else:
            self.setSuitClothes()

    def makeIntoImmune(self):
        self.healthBar.setColor(1, 1, 1, 1)
        self.healthBarGlow.setColor(1, 1, 1, 1)
        taskMgr.remove(self.uniqueName('blink-task'))
        self.__pulseWhite()
        self.isImmune = 1

    def removeImmune(self):
        self.healthBar.setColor(1, 1, 1, 1)
        self.healthBarGlow.setColor(1, 1, 1, 1)
        taskMgr.remove(self.uniqueName('blink-task'))
        self.__changeColor()
        self.isImmune = 0

    def makeIntoCTSManager(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        if self.style.name == 'hho':
            texture = loader.loadTexture('phase_14/maps/cc_t_ene_headhoncho_exe.png')
            for headPart in self.headParts:
                headPart.setTexture(texture, 1)
        texture = loader.loadTexture('phase_3.5/maps/ttcc_ene_suittex_%s_e.png' % self.style.dept)
        if not self.isSkeleton:
            modelRoot.find('**/body').setTexture(texture, 1)

    def getPartTrack(self, particleEffect, startDelay, durationDelay, partExtraArgs, softStop=0):
        particleEffect = partExtraArgs[0]
        parent = partExtraArgs[1]
        if len(partExtraArgs) > 2:
            worldRelative = partExtraArgs[2]
        else:
            worldRelative = 1
        return Sequence(Wait(startDelay),
                        ParticleInterval(particleEffect, parent, worldRelative, duration=durationDelay, cleanup=True,
                                         softStopT=softStop))

    def makeInsured(self):
        self.isInsured = 1
        effectColor = Vec4(0, 1, 0.137, 1.00)
        if hasattr(self, 'cheerEffect') and self.cheerEffect:
            self.cheerEffect.softStop()
            self.cheerEffect.cleanup()
            self.cheerEffect = None
        self.cheerEffect = BattleParticles.createParticleEffect(file='pixieRise')
        self.cheerEffect.setColor(effectColor)

        self.cheerEffect.reparentTo(self)
        self.cheerEffect.setPos(0, 0, 0)
        # self.cooldownEffect.setHpr(180, 0, 0)

        self.cheerTrack = Sequence(ParticleInterval(self.cheerEffect, self, duration=2, softStopT=1))
        if self.currHP > 0:
            self.cheerEffect.start()

    def makeAfterImages(self, numImages=5, rate=0.1):
        self.removeAfterImages()

        self.afterImageNodes = []
        self.afterImageSuits = [None] * numImages
        self.afterImageSeqs = []

        def updateAfterImage(index):
            if index >= len(self.afterImageSuits):
                return

            old = self.afterImageSuits[index]

            if old:
                try:
                    old.detachNode()
                except:
                    pass

                try:
                    old.removeNode()
                except:
                    pass

            self.afterImageSuits[index] = None

            node = self.afterImageNodes[index]
            geom = self.getGeomNode()
            if geom and not geom.isEmpty():
                self.afterImageSuits[index] = geom.copyTo(node)
            else:
                return

            copy = self.afterImageSuits[index]
            if copy is None or copy.isEmpty():
                return

            for removePart in ('**/joint_attachMeter', '**/to_head', '**/joint_shadow'):
                part = copy.find(removePart)
                if not part.isEmpty():
                    part.removeNode()

            node.setPos(self.getPos(render))
            node.setHpr(self.getHpr(render))
            node.setScale(self.getScale(render) * 0.999)
            node.setColorScale(1, 1, 1, 0.6)

        for i in xrange(numImages):
            node = render.attachNewNode('%s-afterImage-%d' % (self.uniqueName('erfit'), i))
            node.setTransparency(TransparencyAttrib.MDual)
            node.setDepthWrite(False)
            node.setBin('fixed', 1)
            self.afterImageNodes.append(node)

            seq = Sequence(
                Func(updateAfterImage, i),
                LerpColorScaleInterval(
                    node,
                    numImages * rate,
                    (1, 1, 1, 0),
                    blendType='easeOut'
                )
            )

            seq.loop()
            seq.setT(rate * i)
            self.afterImageSeqs.append(seq)

    def removeAfterImages(self):
        if hasattr(self, 'afterImageSeqs'):
            for seq in self.afterImageSeqs:
                try:
                    seq.pause()
                except:
                    pass
            self.afterImageSeqs = []

        if hasattr(self, 'afterImageSuits'):
            for suit in self.afterImageSuits:
                if suit:
                    try:
                        suit.removeNode()
                    except:
                        pass
            self.afterImageSuits = []

        if hasattr(self, 'afterImageNodes'):
            for node in self.afterImageNodes:
                try:
                    node.removeNode()
                except:
                    pass
            self.afterImageNodes = []

    def setupHeadFreakout(self, headPart, normalTexture=None, hurtTexture=None, glitchTexture=None):
        """
        headPart:
            The NodePath that should twitch and receive the glitch texture.

        normalTexture:
            The normal texture object, usually loaded with loader.loadTexture().

        glitchTexture:
            The glitch texture object.
        """
        self.headFreakoutPart = headPart
        self.headFreakoutNormalTex = normalTexture
        self.headFreakoutNormalTexHurt = hurtTexture
        self.headFreakoutGlitchTex = glitchTexture

        self.headFreakoutPaused = False
        self.headFreakoutSeq = None
        self.headFreakoutOriginalHpr = headPart.getHpr()


    def startHeadFreakout(self):
        self.stopHeadFreakout()

        if not getattr(self, 'headFreakoutPart', None):
            return

        taskMgr.doMethodLater(
            0,
            self.__doHeadFreakout,
            self.uniqueName(FreakoutTaskName)
        )

    def pauseHeadFreakout(self):
        self.headFreakoutPaused = True

        self.__finishHeadFreakoutSequence()

        if getattr(self, 'headFreakoutPart', None):
            self.headFreakoutPart.setHpr(
                self.headFreakoutOriginalHpr
            )

            self.__setHeadFreakoutTexture(
                self.headFreakoutNormalTex
            )


    def resumeHeadFreakout(self):
        self.headFreakoutPaused = False


    def stopHeadFreakout(self):
        taskMgr.remove(self.uniqueName(FreakoutTaskName))
        self.__finishHeadFreakoutSequence()

        headPart = getattr(self, 'headFreakoutPart', None)
        if not headPart or headPart.isEmpty():
            return
        
        if float(self.currHP) / float(self.maxHP) <= 0.25:
            normalTex = getattr(self, 'headFreakoutNormalTexHurt', None)
        else:
            normalTex = getattr(self, 'headFreakoutNormalTex', None)
        if normalTex:
            headPart.setTexture(normalTex, 1)

        originalHpr = getattr(self, 'headFreakoutOriginalHpr', Vec3(0, 0, 0))
        headPart.setHpr(originalHpr)


    def __finishHeadFreakoutSequence(self):
        if getattr(self, 'headFreakoutSeq', None):
            self.headFreakoutSeq.finish()
            self.headFreakoutSeq = None


    def __weightedRandomChoice(self, choices, weights):
        """
        Python 2.7 replacement for random.choices().
        """
        totalWeight = float(sum(weights))
        roll = random.uniform(0.0, totalWeight)
        currentWeight = 0.0

        for choice, weight in zip(choices, weights):
            currentWeight += weight
            if roll <= currentWeight:
                return choice

        return choices[-1]


    def __setHeadFreakoutTexture(self, texture):
        headPart = getattr(self, 'headFreakoutPart', None)

        if not headPart or headPart.isEmpty():
            return

        if texture:
            headPart.setTexture(texture, 1)


    def __doHeadFreakout(self, task):
        if self.headFreakoutPaused:
            task.delayTime = 0.1
            return task.again
        self.__finishHeadFreakoutSequence()

        for headPart in self.animatedHeadParts:
            headPart = headPart

        if not headPart or headPart.isEmpty():
            return task.done

        waitForNextTime = random.uniform(
            HeadFreakoutWaitRange[0],
            HeadFreakoutWaitRange[1]
        )

        twitchRepeatAmount = self.__weightedRandomChoice(
            HeadFreakoutRepeatTimes,
            HeadFreakoutRepeatWeights
        )

        originalHpr = getattr(
            self,
            'headFreakoutOriginalHpr',
            headPart.getHpr()
        )

        self.headFreakoutSeq = Sequence()

        for i in xrange(twitchRepeatAmount):
            lastTwitch = i == twitchRepeatAmount - 1

            twitchTime = random.uniform(
                HeadFreakoutTwitchTimeRange[0],
                HeadFreakoutTwitchTimeRange[1]
            )

            useHeading = random.random() < 0.5

            if useHeading:
                minimumAngle = HeadFreakoutAngleRange[0]
                maximumAngle = HeadFreakoutAngleRange[1]
            else:
                minimumAngle = HeadFreakoutAngleRange[0] * (2.0 / 3.0)
                maximumAngle = HeadFreakoutAngleRange[1] * (2.0 / 3.0)

            angle = random.uniform(minimumAngle, maximumAngle)
            angle *= random.choice((-1, 1))

            if useHeading:
                finalHpr = Vec3(
                    originalHpr.getX() + angle,
                    originalHpr.getY(),
                    originalHpr.getZ()
                )
            else:
                finalHpr = Vec3(
                    originalHpr.getX(),
                    originalHpr.getY(),
                    originalHpr.getZ() + angle
                )

            self.headFreakoutSeq.append(
                Sequence(
                    Func(
                        self.__setHeadFreakoutTexture,
                        self.headFreakoutGlitchTex
                    ),
                    LerpHprInterval(
                        headPart,
                        twitchTime,
                        finalHpr,
                        startHpr=originalHpr
                    )
                )
            )
            if float(self.currHP) / float(self.maxHP) <= 0.25:
                if lastTwitch:
                    self.headFreakoutSeq.append(
                        Func(
                            self.__setHeadFreakoutTexture,
                            self.headFreakoutNormalTexHurt
                        )
                    )

                    self.headFreakoutSeq.append(
                        LerpHprInterval(
                            headPart,
                            twitchTime * 2.0,
                            originalHpr,
                            blendType='easeOut'
                        )
                    )
            else:
                if lastTwitch:
                    self.headFreakoutSeq.append(
                        Func(
                            self.__setHeadFreakoutTexture,
                            self.headFreakoutNormalTex
                        )
                    )

                    self.headFreakoutSeq.append(
                        LerpHprInterval(
                            headPart,
                            twitchTime * 2.0,
                            originalHpr,
                            blendType='easeOut'
                        )
                    )
                

        self.headFreakoutSeq.start()

        task.delayTime = (
            waitForNextTime +
            self.headFreakoutSeq.getDuration()
        )

        return task.again

    def makeSwole(self):
        self.makeAfterImages()
        self.isSwole = 1

    def makeUnSwole(self):
        self.removeAfterImages()
        self.isSwole = 0

    def removeInsured(self):
        self.isInsured = 0
        self.isInsured2 = 0
        if hasattr(self, 'cheerEffect') and self.cheerEffect:
            self.cheerEffect.softStop()
            self.cheerEffect.cleanup()
            self.cheerEffect = None

    def makeInsured2(self):
        self.isInsured2 = 1
        effectColor = Vec4(0, 1, 0.137, 1.00)
        if hasattr(self, 'cheerEffect') and self.cheerEffect:
            self.cheerEffect.softStop()
            self.cheerEffect.cleanup()
            self.cheerEffect = None
        self.cheerEffect = BattleParticles.createParticleEffect(file='pixieRise')
        self.cheerEffect.setColor(effectColor)

        self.cheerEffect.reparentTo(self)
        self.cheerEffect.setPos(0, 0, 0)
        # self.cooldownEffect.setHpr(180, 0, 0)

        self.cheerTrack = Sequence(ParticleInterval(self.cheerEffect, self, duration=2, softStopT=1))
        if self.currHP > 0:
            self.cheerEffect.start()

    def addInsuranceRounds(self, num):
        self.insuranceRounds = num

    def getInsuranceRounds(self):
        return self.insuranceRounds

    def cleanupOilRain(self):
        if hasattr(self, 'oilTrack') and self.oilTrack:
            try:
                self.oilTrack.pause()
            except:
                pass
            try:
                self.oilTrack.finish()
            except:
                pass
            self.oilTrack = None

        if hasattr(self, 'oilEffect') and self.oilEffect:
            effect = self.oilEffect
            self.oilEffect = None

            try:
                effect.softStop()
            except:
                pass

            try:
                effect.disable()
            except:
                pass

            try:
                effect.cleanup()
            except:
                pass

            try:
                effect.removeNode()
            except:
                try:
                    effect.detachNode()
                except:
                    pass


    def removeOilRain(self):
        self.isOilRain = 0
        self.cleanupOilRain()


    def makeOilRain(self):
        self.isOilRain = 1

        self.cleanupOilRain()

        self.oilEffect = BattleParticles.createParticleEffect(file='oil')
        self.oilEffect.reparentTo(self)
        self.oilEffect.setPos(0, 0, self.height - 2.5)

        if self.currHP > 0:
            self.oilEffect.start(parent=self, renderParent=self)

    def addOilRainRounds(self, num):
        self.oilRainRounds = num

    def getOilRainRounds(self):
        return self.oilRainRounds

    def makeContracted(self):
        if not self.getManager() and self.currHP > 0 and not self.isShadow and not self.getGovernaught():
            self.setDisplayName(self.createNameInfoContracted())
        self.isContracted = 1
        if hasattr(self, "cheerTrack2") and self.cheerTrack2:
            self.cheerTrack2.pause()
            if self.cheerEffect2:
                self.cheerEffect2.disable()
                if hasattr(self.cheerEffect2, 'renderParent'):
                    self.cheerEffect2.cleanup()
        effectColor = Vec4(0, 1, 0.137, 1.00)
        self.cheerEffect2 = BattleParticles.createParticleEffect(file='pixieRise')
        self.cheerEffect2.setColor(effectColor)

        self.cheerEffect2.reparentTo(self)
        self.cheerEffect2.setPos(0, 0, 0)
        #self.cooldownEffect.setHpr(180, 0, 0)

        self.cheerTrack2 = Sequence(ParticleInterval(self.cheerEffect2, self, duration=5))
        if self.currHP > 0:
            self.cheerTrack2.loop()

    def makeContracted2(self):
        if not self.getManager() and self.currHP > 0 and not self.isShadow and not self.getGovernaught():
            self.setDisplayName(self.createNameInfoContracted())
        self.isContracted2 = 1
        if hasattr(self, "cheerTrack2") and self.cheerTrack2:
            self.cheerTrack2.pause()
            if self.cheerEffect2:
                self.cheerEffect2.disable()
                if hasattr(self.cheerEffect2, 'renderParent'):
                    self.cheerEffect2.cleanup()
        effectColor = Vec4(0, 1, 0.137, 1.00)
        self.cheerEffect2 = BattleParticles.createParticleEffect(file='pixieRise')
        self.cheerEffect2.setColor(effectColor)

        self.cheerEffect2.reparentTo(self)
        self.cheerEffect2.setPos(0, 0, 0)
        #self.cooldownEffect.setHpr(180, 0, 0)

        self.cheerTrack2 = Sequence(ParticleInterval(self.cheerEffect2, self, duration=5))
        if self.currHP > 0:
            self.cheerTrack2.loop()

    def removeContracted(self):
        self.isContracted = 0
        self.isContracted2 = 0
        if hasattr(self, "cheerTrack2") and self.cheerTrack2:
            self.cheerTrack2.pause()
            if self.cheerEffect2:
                self.cheerEffect2.disable()
                if hasattr(self.cheerEffect2, 'renderParent'):
                    self.cheerEffect2.cleanup()

    def addContractedRounds(self, num):
        self.contractedRounds = num

    def getContractedRounds(self):
        return self.contractedRounds

    def leaveAfterimageTask(self, task):
        """Create a faded clone of the Cog as an afterimage."""
        ghost = NodePath("afterimage")
        self.copyTo(ghost)  # duplicate suit into ghost node
        ghost.reparentTo(render)
        ghost.setPos(self.getPos(render))
        ghost.setHpr(self.getHpr(render))
        ghost.setScale(self.getScale())

        # Make ghost transparent + tinted
        ghost.setTransparency(TransparencyAttrib.MAlpha)
        ghost.setColorScale(1, 1, 1, 0.5)  # semi-transparent

        # Fade out + remove
        fade = Sequence(
            LerpColorScaleInterval(ghost, 0.4, (1, 1, 1, 0)),  # fade to invisible
            Func(ghost.hide)
        )
        fade.start()

        return task.again  # repeat every 0.1 sec

    def leaveAfterimageTask2(self, task):
        """Create a faded clone of the Cog as an afterimage."""
        ghost = NodePath("afterimage")
        self.copyTo(ghost)  # duplicate suit into ghost node
        ghost.reparentTo(render)
        ghost.setPos(self.getPos(render))
        ghost.setHpr(self.getHpr(render))
        ghost.setScale(self.getScale())

        # Make ghost transparent + tinted
        ghost.setTransparency(TransparencyAttrib.MAlpha)
        ghost.setColorScale(1, 1, 1, 0.5)  # semi-transparent

        # Fade out + remove
        fade = Sequence(
            LerpColorScaleInterval(ghost, 0.4, (1, 1, 1, 0)),  # fade to invisible
            Func(ghost.hide)
        )
        fade.start()

        return task.again  # repeat every 0.1 sec

    def leaveAfterimageTask3(self, task):
        """Create a faded clone of the Cog as an afterimage."""
        ghost = NodePath("afterimage")
        self.copyTo(ghost)  # duplicate suit into ghost node
        ghost.reparentTo(self)

        # Make ghost transparent + tinted
        ghost.setTransparency(TransparencyAttrib.MAlpha)
        ghost.setColorScale(1, 1, 1, 0.5)  # semi-transparent

        # Fade out + remove
        fade = Sequence(
            LerpColorScaleInterval(ghost, 0.4, (1, 1, 1, 0)),  # fade to invisible
            Func(ghost.hide)
        )
        fade.start()

        return task.again  # repeat every 0.1 sec

    def makeExtraAbilities(self, num):

        # # ---- CLEANUP ----
        # if hasattr(self, "knifeTrack") and self.knifeTrack:
        #     self.knifeTrack.pause()
        #     self.knifeTrack.finish()
        #     self.knifeTrack = None

        # if hasattr(self, "knifePivot") and not self.knifePivot.isEmpty():
        #     self.knifePivot.removeNode()

        # from math import pi, cos, sin

        self.extraAbility = max(1, num)
        # totalKnives = self.extraAbility

        # radius = 1.5
        # height = self.height

        # # Shared pivot (orbit axis)
        # self.knifePivot = self.attachNewNode("knifePivot")
        # self.knifePivot.setZ(height)

        # knifeIntervals = []

        # for i in range(totalKnives):

        #     # Load correct model
        #     knife = loader.loadModel('phase_5/models/props/ttr_m_prp_bat_dagger')
        #     knife.setScale(0.5)

        #     knife.reparentTo(self.knifePivot)

        #     # Even spacing
        #     angle = (2 * pi / totalKnives) * i
        #     knife.setPos(cos(angle) * radius,
        #                  sin(angle) * radius,
        #                  0)

        #     # Match original orientation
        #     knife.lookAt(self.knifePivot)
        #     knife.setP(270)
        #     knife.setR(90)

        #     # Individual knife spin (same as your first knife)
        #     # spin = LerpHprInterval(
        #     #     knife,
        #     #     4.0,
        #     #     VBase3(360.0, 270.0, 0.0),
        #     #     startHpr=VBase3(0.0, 270.0, 0.0)
        #     # )
        #     #
        #     # knifeIntervals.append(spin)

        # # Pivot rotation (orbit)
        # orbit = LerpHprInterval(
        #     self.knifePivot,
        #     4.0,
        #     VBase3(360, 0, 0),
        #     startHpr=VBase3(0, 0, 0)
        # )

        # # Run everything together
        # self.knifeTrack = Parallel(
        #     orbit,
        #     *knifeIntervals
        # )

        # self.knifeTrack.loop()


    def getExtraAbilities(self):
        return self.extraAbility

    def removeExtraAbilities(self):
        self.extraAbility = 0
        if self.knifeTrack != None:
            self.knifeTrack.finish()

    def makeExtraAttacks(self, num):
        # ---- CLEANUP ----
        if hasattr(self, "knifeTrack") and self.knifeTrack:
            self.knifeTrack.pause()
            self.knifeTrack.finish()
            self.knifeTrack = None

        if hasattr(self, "knifePivot") and not self.knifePivot.isEmpty():
            self.knifePivot.removeNode()

        from math import pi, cos, sin

        self.extraAttack = max(1, num)
        if self.style.name == 'clubpres':
            totalKnives = self.extraAttack
        else:
            totalKnives = self.extraAttack

        radius = 1.5
        height = self.height

        # Shared pivot (orbit axis)
        self.knifePivot = self.attachNewNode("knifePivot")
        self.knifePivot.setZ(height)

        knifeIntervals = []

        for i in range(totalKnives):

            # Load correct model
            if self.style.name == 'clubpres':
                knife = loader.loadModel('phase_6/models/golf/golf_ball')
                knife.setScale(1)
            else:
                knife = loader.loadModel('phase_5/models/props/ttr_m_prp_bat_dagger')
                knife.setScale(0.5)

            knife.reparentTo(self.knifePivot)

            # Even spacing
            angle = (2 * pi / totalKnives) * i
            knife.setPos(cos(angle) * radius,
                         sin(angle) * radius,
                         0)

            # Match original orientation
            knife.lookAt(self.knifePivot)
            knife.setP(270)
            knife.setR(90)

            # Individual knife spin (same as your first knife)
            # spin = LerpHprInterval(
            #     knife,
            #     4.0,
            #     VBase3(360.0, 270.0, 0.0),
            #     startHpr=VBase3(0.0, 270.0, 0.0)
            # )
            #
            # knifeIntervals.append(spin)

        # Pivot rotation (orbit)
        orbit = LerpHprInterval(
            self.knifePivot,
            4.0,
            VBase3(360, 0, 0),
            startHpr=VBase3(0, 0, 0)
        )

        # Run everything together
        self.knifeTrack = Parallel(
            orbit,
            *knifeIntervals
        )

        self.knifeTrack.loop()

    # def makeExtraAttacks(self, num):
    #     self.extraAttack = num
    #     if self.extraAttack == 1:
    #         if self.style.name == 'clubpres':
    #             knife = loader.loadModel('phase_6/models/golf/golf_ball')
    #             knife.setScale(1)
    #         else:
    #             knife = loader.loadModel('phase_5/models/props/ttr_m_prp_bat_dagger')
    #             knife.setScale(0.5)
    #         knife.reparentTo(self)
    #         knife.setZ(self.height)
    #         self.knifeTrack = Parallel(
    #         Sequence(
    #             Parallel(
    #                 LerpFunctionInterval(knife.setX, 1.0, fromData=1.5, toData=0.0, blendType='easeIn'),
    #                 LerpFunctionInterval(knife.setY, 1.0, fromData=0.0, toData=1.5, blendType='easeOut')
    #             ),
    #             Parallel(
    #                 LerpFunctionInterval(knife.setX, 1.0, fromData=0.0, toData=-1.5, blendType='easeOut'),
    #                 LerpFunctionInterval(knife.setY, 1.0, fromData=1.5, toData=0.0, blendType='easeIn')
    #             ),
    #             Parallel(
    #                 LerpFunctionInterval(knife.setX, 1.0, fromData=-1.5, toData=0.0, blendType='easeIn'),
    #                 LerpFunctionInterval(knife.setY, 1.0, fromData=0.0, toData=-1.5, blendType='easeOut')
    #             ),
    #             Parallel(
    #                 LerpFunctionInterval(knife.setX, 1.0, fromData=0.0, toData=1.5, blendType='easeOut'),
    #                 LerpFunctionInterval(knife.setY, 1.0, fromData=-1.5, toData=0.0, blendType='easeIn')
    #             )
    #         ),
    #         LerpHprInterval(knife, 4.0, VBase3(360.0, 270.0, 0.0), startHpr=VBase3(0.0, 270.0, 0.0))
    #     )
    #         self.knifeTrack.loop()
    #     if self.extraAttack == 2:
    #         if self.style.name == 'clubpres':
    #             knife = loader.loadModel('phase_6/models/golf/golf_ball')
    #             knife.setScale(1)
    #         else:
    #             knife = loader.loadModel('phase_5/models/props/ttr_m_prp_bat_dagger')
    #             knife.setScale(0.5)
    #         knife.reparentTo(self)
    #         knife.setZ(self.height)
    #         self.knifeTrack2 = Parallel(
    #         Sequence(
    #             Parallel(
    #                 LerpFunctionInterval(knife.setX, 1.0, fromData=1.5, toData=0.0, blendType='easeIn'),
    #                 LerpFunctionInterval(knife.setY, 1.0, fromData=0.0, toData=1.5, blendType='easeOut')
    #             ),
    #             Parallel(
    #                 LerpFunctionInterval(knife.setX, 1.0, fromData=0.0, toData=-1.5, blendType='easeOut'),
    #                 LerpFunctionInterval(knife.setY, 1.0, fromData=1.5, toData=0.0, blendType='easeIn')
    #             ),
    #             Parallel(
    #                 LerpFunctionInterval(knife.setX, 1.0, fromData=-1.5, toData=0.0, blendType='easeIn'),
    #                 LerpFunctionInterval(knife.setY, 1.0, fromData=0.0, toData=-1.5, blendType='easeOut')
    #             ),
    #             Parallel(
    #                 LerpFunctionInterval(knife.setX, 1.0, fromData=0.0, toData=1.5, blendType='easeOut'),
    #                 LerpFunctionInterval(knife.setY, 1.0, fromData=-1.5, toData=0.0, blendType='easeIn')
    #             )
    #         ),
    #         LerpHprInterval(knife, 4.0, VBase3(360.0, 270.0, 0.0), startHpr=VBase3(0.0, 270.0, 0.0))
    #     )
    #         self.knifeTrack2.loop()
    #     if self.extraAttack == 3:
    #         if self.style.name == 'clubpres':
    #             knife = loader.loadModel('phase_6/models/golf/golf_ball')
    #             knife.setScale(1)
    #         else:
    #             knife = loader.loadModel('phase_5/models/props/ttr_m_prp_bat_dagger')
    #             knife.setScale(0.5)
    #         knife.reparentTo(self)
    #         knife.setZ(self.height)
    #         self.knifeTrack3 = Parallel(
    #         Sequence(
    #             Parallel(
    #                 LerpFunctionInterval(knife.setX, 1.0, fromData=1.5, toData=0.0, blendType='easeIn'),
    #                 LerpFunctionInterval(knife.setY, 1.0, fromData=0.0, toData=1.5, blendType='easeOut')
    #             ),
    #             Parallel(
    #                 LerpFunctionInterval(knife.setX, 1.0, fromData=0.0, toData=-1.5, blendType='easeOut'),
    #                 LerpFunctionInterval(knife.setY, 1.0, fromData=1.5, toData=0.0, blendType='easeIn')
    #             ),
    #             Parallel(
    #                 LerpFunctionInterval(knife.setX, 1.0, fromData=-1.5, toData=0.0, blendType='easeIn'),
    #                 LerpFunctionInterval(knife.setY, 1.0, fromData=0.0, toData=-1.5, blendType='easeOut')
    #             ),
    #             Parallel(
    #                 LerpFunctionInterval(knife.setX, 1.0, fromData=0.0, toData=1.5, blendType='easeOut'),
    #                 LerpFunctionInterval(knife.setY, 1.0, fromData=-1.5, toData=0.0, blendType='easeIn')
    #             )
    #         ),
    #         LerpHprInterval(knife, 4.0, VBase3(360.0, 270.0, 0.0), startHpr=VBase3(0.0, 270.0, 0.0))
    #     )
    #         self.knifeTrack3.loop()
    #     if self.extraAttack == 4:
    #         if self.style.name == 'clubpres':
    #             knife = loader.loadModel('phase_6/models/golf/golf_ball')
    #             knife.setScale(1)
    #         else:
    #             knife = loader.loadModel('phase_5/models/props/ttr_m_prp_bat_dagger')
    #             knife.setScale(0.5)
    #         knife.reparentTo(self)
    #         knife.setZ(self.height)
    #         self.knifeTrack4 = Parallel(
    #         Sequence(
    #             Parallel(
    #                 LerpFunctionInterval(knife.setX, 1.0, fromData=1.5, toData=0.0, blendType='easeIn'),
    #                 LerpFunctionInterval(knife.setY, 1.0, fromData=0.0, toData=1.5, blendType='easeOut')
    #             ),
    #             Parallel(
    #                 LerpFunctionInterval(knife.setX, 1.0, fromData=0.0, toData=-1.5, blendType='easeOut'),
    #                 LerpFunctionInterval(knife.setY, 1.0, fromData=1.5, toData=0.0, blendType='easeIn')
    #             ),
    #             Parallel(
    #                 LerpFunctionInterval(knife.setX, 1.0, fromData=-1.5, toData=0.0, blendType='easeIn'),
    #                 LerpFunctionInterval(knife.setY, 1.0, fromData=0.0, toData=-1.5, blendType='easeOut')
    #             ),
    #             Parallel(
    #                 LerpFunctionInterval(knife.setX, 1.0, fromData=0.0, toData=1.5, blendType='easeOut'),
    #                 LerpFunctionInterval(knife.setY, 1.0, fromData=-1.5, toData=0.0, blendType='easeIn')
    #             )
    #         ),
    #         LerpHprInterval(knife, 4.0, VBase3(360.0, 270.0, 0.0), startHpr=VBase3(0.0, 270.0, 0.0))
    #     )
    #         self.knifeTrack4.loop()
    #     if self.extraAttack == 5:
    #         if self.style.name == 'clubpres':
    #             knife = loader.loadModel('phase_6/models/golf/golf_ball')
    #             knife.setScale(1)
    #         else:
    #             knife = loader.loadModel('phase_5/models/props/ttr_m_prp_bat_dagger')
    #             knife.setScale(0.5)
    #         knife.reparentTo(self)
    #         knife.setZ(self.height)
    #         self.knifeTrack5 = Parallel(
    #         Sequence(
    #             Parallel(
    #                 LerpFunctionInterval(knife.setX, 1.0, fromData=1.5, toData=0.0, blendType='easeIn'),
    #                 LerpFunctionInterval(knife.setY, 1.0, fromData=0.0, toData=1.5, blendType='easeOut')
    #             ),
    #             Parallel(
    #                 LerpFunctionInterval(knife.setX, 1.0, fromData=0.0, toData=-1.5, blendType='easeOut'),
    #                 LerpFunctionInterval(knife.setY, 1.0, fromData=1.5, toData=0.0, blendType='easeIn')
    #             ),
    #             Parallel(
    #                 LerpFunctionInterval(knife.setX, 1.0, fromData=-1.5, toData=0.0, blendType='easeIn'),
    #                 LerpFunctionInterval(knife.setY, 1.0, fromData=0.0, toData=-1.5, blendType='easeOut')
    #             ),
    #             Parallel(
    #                 LerpFunctionInterval(knife.setX, 1.0, fromData=0.0, toData=1.5, blendType='easeOut'),
    #                 LerpFunctionInterval(knife.setY, 1.0, fromData=-1.5, toData=0.0, blendType='easeIn')
    #             )
    #         ),
    #         LerpHprInterval(knife, 4.0, VBase3(360.0, 270.0, 0.0), startHpr=VBase3(0.0, 270.0, 0.0))
    #     )
    #         self.knifeTrack5.loop()
    #     if self.extraAttack == 6:
    #         if self.style.name == 'clubpres':
    #             knife = loader.loadModel('phase_6/models/golf/golf_ball')
    #             knife.setScale(1)
    #         else:
    #             knife = loader.loadModel('phase_5/models/props/ttr_m_prp_bat_dagger')
    #             knife.setScale(0.5)
    #         knife.reparentTo(self)
    #         knife.setZ(self.height)
    #         self.knifeTrack6 = Parallel(
    #         Sequence(
    #             Parallel(
    #                 LerpFunctionInterval(knife.setX, 1.0, fromData=1.5, toData=0.0, blendType='easeIn'),
    #                 LerpFunctionInterval(knife.setY, 1.0, fromData=0.0, toData=1.5, blendType='easeOut')
    #             ),
    #             Parallel(
    #                 LerpFunctionInterval(knife.setX, 1.0, fromData=0.0, toData=-1.5, blendType='easeOut'),
    #                 LerpFunctionInterval(knife.setY, 1.0, fromData=1.5, toData=0.0, blendType='easeIn')
    #             ),
    #             Parallel(
    #                 LerpFunctionInterval(knife.setX, 1.0, fromData=-1.5, toData=0.0, blendType='easeIn'),
    #                 LerpFunctionInterval(knife.setY, 1.0, fromData=0.0, toData=-1.5, blendType='easeOut')
    #             ),
    #             Parallel(
    #                 LerpFunctionInterval(knife.setX, 1.0, fromData=0.0, toData=1.5, blendType='easeOut'),
    #                 LerpFunctionInterval(knife.setY, 1.0, fromData=-1.5, toData=0.0, blendType='easeIn')
    #             )
    #         ),
    #         LerpHprInterval(knife, 4.0, VBase3(360.0, 270.0, 0.0), startHpr=VBase3(0.0, 270.0, 0.0))
    #     )
    #         self.knifeTrack6.loop()
    #     if self.extraAttack == 7:
    #         if self.style.name == 'clubpres':
    #             knife = loader.loadModel('phase_6/models/golf/golf_ball')
    #             knife.setScale(1)
    #         else:
    #             knife = loader.loadModel('phase_5/models/props/ttr_m_prp_bat_dagger')
    #             knife.setScale(0.5)
    #         knife.reparentTo(self)
    #         knife.setZ(self.height)
    #         self.knifeTrack7 = Parallel(
    #         Sequence(
    #             Parallel(
    #                 LerpFunctionInterval(knife.setX, 1.0, fromData=1.5, toData=0.0, blendType='easeIn'),
    #                 LerpFunctionInterval(knife.setY, 1.0, fromData=0.0, toData=1.5, blendType='easeOut')
    #             ),
    #             Parallel(
    #                 LerpFunctionInterval(knife.setX, 1.0, fromData=0.0, toData=-1.5, blendType='easeOut'),
    #                 LerpFunctionInterval(knife.setY, 1.0, fromData=1.5, toData=0.0, blendType='easeIn')
    #             ),
    #             Parallel(
    #                 LerpFunctionInterval(knife.setX, 1.0, fromData=-1.5, toData=0.0, blendType='easeIn'),
    #                 LerpFunctionInterval(knife.setY, 1.0, fromData=0.0, toData=-1.5, blendType='easeOut')
    #             ),
    #             Parallel(
    #                 LerpFunctionInterval(knife.setX, 1.0, fromData=0.0, toData=1.5, blendType='easeOut'),
    #                 LerpFunctionInterval(knife.setY, 1.0, fromData=-1.5, toData=0.0, blendType='easeIn')
    #             )
    #         ),
    #         LerpHprInterval(knife, 4.0, VBase3(360.0, 270.0, 0.0), startHpr=VBase3(0.0, 270.0, 0.0))
    #     )
    #         self.knifeTrack7.loop()
    #     if self.extraAttack == 8:
    #         if self.style.name == 'clubpres':
    #             knife = loader.loadModel('phase_6/models/golf/golf_ball')
    #             knife.setScale(1)
    #         else:
    #             knife = loader.loadModel('phase_5/models/props/ttr_m_prp_bat_dagger')
    #             knife.setScale(0.5)
    #         knife.reparentTo(self)
    #         knife.setZ(self.height)
    #         self.knifeTrack8 = Parallel(
    #         Sequence(
    #             Parallel(
    #                 LerpFunctionInterval(knife.setX, 1.0, fromData=1.5, toData=0.0, blendType='easeIn'),
    #                 LerpFunctionInterval(knife.setY, 1.0, fromData=0.0, toData=1.5, blendType='easeOut')
    #             ),
    #             Parallel(
    #                 LerpFunctionInterval(knife.setX, 1.0, fromData=0.0, toData=-1.5, blendType='easeOut'),
    #                 LerpFunctionInterval(knife.setY, 1.0, fromData=1.5, toData=0.0, blendType='easeIn')
    #             ),
    #             Parallel(
    #                 LerpFunctionInterval(knife.setX, 1.0, fromData=-1.5, toData=0.0, blendType='easeIn'),
    #                 LerpFunctionInterval(knife.setY, 1.0, fromData=0.0, toData=-1.5, blendType='easeOut')
    #             ),
    #             Parallel(
    #                 LerpFunctionInterval(knife.setX, 1.0, fromData=0.0, toData=1.5, blendType='easeOut'),
    #                 LerpFunctionInterval(knife.setY, 1.0, fromData=-1.5, toData=0.0, blendType='easeIn')
    #             )
    #         ),
    #         LerpHprInterval(knife, 4.0, VBase3(360.0, 270.0, 0.0), startHpr=VBase3(0.0, 270.0, 0.0))
    #     )
    #         self.knifeTrack8.loop()
    #     if self.extraAttack == 9:
    #         if self.style.name == 'clubpres':
    #             knife = loader.loadModel('phase_6/models/golf/golf_ball')
    #             knife.setScale(1)
    #         else:
    #             knife = loader.loadModel('phase_5/models/props/ttr_m_prp_bat_dagger')
    #             knife.setScale(0.5)
    #         knife.reparentTo(self)
    #         knife.setZ(self.height)
    #         self.knifeTrack9 = Parallel(
    #         Sequence(
    #             Parallel(
    #                 LerpFunctionInterval(knife.setX, 1.0, fromData=1.5, toData=0.0, blendType='easeIn'),
    #                 LerpFunctionInterval(knife.setY, 1.0, fromData=0.0, toData=1.5, blendType='easeOut')
    #             ),
    #             Parallel(
    #                 LerpFunctionInterval(knife.setX, 1.0, fromData=0.0, toData=-1.5, blendType='easeOut'),
    #                 LerpFunctionInterval(knife.setY, 1.0, fromData=1.5, toData=0.0, blendType='easeIn')
    #             ),
    #             Parallel(
    #                 LerpFunctionInterval(knife.setX, 1.0, fromData=-1.5, toData=0.0, blendType='easeIn'),
    #                 LerpFunctionInterval(knife.setY, 1.0, fromData=0.0, toData=-1.5, blendType='easeOut')
    #             ),
    #             Parallel(
    #                 LerpFunctionInterval(knife.setX, 1.0, fromData=0.0, toData=1.5, blendType='easeOut'),
    #                 LerpFunctionInterval(knife.setY, 1.0, fromData=-1.5, toData=0.0, blendType='easeIn')
    #             )
    #         ),
    #         LerpHprInterval(knife, 4.0, VBase3(360.0, 270.0, 0.0), startHpr=VBase3(0.0, 270.0, 0.0))
    #     )
    #         self.knifeTrack9.loop()
    #     if self.extraAttack == 10:
    #         if self.style.name == 'clubpres':
    #             knife = loader.loadModel('phase_6/models/golf/golf_ball')
    #             knife.setScale(1)
    #         else:
    #             knife = loader.loadModel('phase_5/models/props/ttr_m_prp_bat_dagger')
    #             knife.setScale(0.5)
    #         knife.reparentTo(self)
    #         knife.setZ(self.height)
    #         self.knifeTrack10 = Parallel(
    #         Sequence(
    #             Parallel(
    #                 LerpFunctionInterval(knife.setX, 1.0, fromData=1.5, toData=0.0, blendType='easeIn'),
    #                 LerpFunctionInterval(knife.setY, 1.0, fromData=0.0, toData=1.5, blendType='easeOut')
    #             ),
    #             Parallel(
    #                 LerpFunctionInterval(knife.setX, 1.0, fromData=0.0, toData=-1.5, blendType='easeOut'),
    #                 LerpFunctionInterval(knife.setY, 1.0, fromData=1.5, toData=0.0, blendType='easeIn')
    #             ),
    #             Parallel(
    #                 LerpFunctionInterval(knife.setX, 1.0, fromData=-1.5, toData=0.0, blendType='easeIn'),
    #                 LerpFunctionInterval(knife.setY, 1.0, fromData=0.0, toData=-1.5, blendType='easeOut')
    #             ),
    #             Parallel(
    #                 LerpFunctionInterval(knife.setX, 1.0, fromData=0.0, toData=1.5, blendType='easeOut'),
    #                 LerpFunctionInterval(knife.setY, 1.0, fromData=-1.5, toData=0.0, blendType='easeIn')
    #             )
    #         ),
    #         LerpHprInterval(knife, 4.0, VBase3(360.0, 270.0, 0.0), startHpr=VBase3(0.0, 270.0, 0.0))
    #     )
    #         self.knifeTrack10.loop()
    #     if self.extraAttack == 11:
    #         if self.style.name == 'clubpres':
    #             knife = loader.loadModel('phase_6/models/golf/golf_ball')
    #             knife.setScale(1)
    #         else:
    #             knife = loader.loadModel('phase_5/models/props/ttr_m_prp_bat_dagger')
    #             knife.setScale(0.5)
    #         knife.reparentTo(self)
    #         knife.setZ(self.height)
    #         self.knifeTrack11 = Parallel(
    #         Sequence(
    #             Parallel(
    #                 LerpFunctionInterval(knife.setX, 1.0, fromData=1.5, toData=0.0, blendType='easeIn'),
    #                 LerpFunctionInterval(knife.setY, 1.0, fromData=0.0, toData=1.5, blendType='easeOut')
    #             ),
    #             Parallel(
    #                 LerpFunctionInterval(knife.setX, 1.0, fromData=0.0, toData=-1.5, blendType='easeOut'),
    #                 LerpFunctionInterval(knife.setY, 1.0, fromData=1.5, toData=0.0, blendType='easeIn')
    #             ),
    #             Parallel(
    #                 LerpFunctionInterval(knife.setX, 1.0, fromData=-1.5, toData=0.0, blendType='easeIn'),
    #                 LerpFunctionInterval(knife.setY, 1.0, fromData=0.0, toData=-1.5, blendType='easeOut')
    #             ),
    #             Parallel(
    #                 LerpFunctionInterval(knife.setX, 1.0, fromData=0.0, toData=1.5, blendType='easeOut'),
    #                 LerpFunctionInterval(knife.setY, 1.0, fromData=-1.5, toData=0.0, blendType='easeIn')
    #             )
    #         ),
    #         LerpHprInterval(knife, 4.0, VBase3(360.0, 270.0, 0.0), startHpr=VBase3(0.0, 270.0, 0.0))
    #     )
    #         self.knifeTrack11.loop()


    def getExtraAttacks(self):
        return self.extraAttack

    def makeOverpressured(self):
        self.isOverpressured = 1

    def makeShadow(self):
        self.isShadow = 1

    def removeExtraAttacks(self):
        self.extraAttack = 0
        if self.knifeTrack != None:
            self.knifeTrack.finish()

    def makeBookkeeping(self):
        self.isBookkeeping= 1
        node = self.getGeomNode().getChild(0)
        self.suitColorTrack = Sequence(LerpColorScaleInterval(node, duration=1, colorScale=(1, 0, 0, 1),
                                                         blendType='easeInOut'),
                                  LerpColorScaleInterval(node, duration=1, colorScale=(1, 1, 1, 1),
                                                         blendType='easeInOut'),
                                  LerpColorScaleInterval(node, duration=1, colorScale=(1, 0, 0, 1),
                                                         blendType='easeInOut'),
                                  LerpColorScaleInterval(node, duration=1, colorScale=(1, 1, 1, 1)))
        self.suitColorTrack.loop()

    def removeBookkeeping(self):
        self.isBookkeeping = 0
        if self.suitColorTrack != None:
            self.suitColorTrack.finish()

    def makeDanceSession(self):
        self.isDanceSession = 1

    def removeDanceSession(self):
        self.isDanceSession = 0

    def makeSued(self, num):
        self.isSued = num

    def getSuedRounds(self):
        return self.isSued

    def removeSued(self):
        self.isSued = 0

    def makeIntoPhase3(self):
        self.isPhase3 = 1

    def removePhase3(self):
        self.isPhase3 = 0

    def makeLitigationManager(self):
        self.isLitigationManager = 1

    def makeIntoEnraged(self):
        BattleParticles.loadParticles()
        self.isEnraged = 1
        baseFlameEffect = BattleParticles.createParticleEffect(file='firedBaseFlame')
        flameEffect = BattleParticles.createParticleEffect('FiredFlame')
        flecksEffect = BattleParticles.createParticleEffect('SpriteFiredFlecks')
        BattleParticles.setEffectTexture(baseFlameEffect, 'fire')
        BattleParticles.setEffectTexture(flameEffect, 'fire')
        BattleParticles.setEffectTexture(flecksEffect, 'roll-o-dex', color=Vec4(0.95, 0.95, 0.0, 1))
        self.baseFlameTrack = self.getPartTrack(baseFlameEffect, 0, 5.5, [baseFlameEffect, self, 0])
        self.flameTrack = self.getPartTrack(flameEffect, 0, 5.5, [flameEffect, self, 0])
        self.flecksTrack = self.getPartTrack(flecksEffect, 0, 5.5, [flecksEffect, self, 0])
        self.baseFlameTrack.loop()
        self.flameTrack.loop()
        self.flecksTrack.loop()

    def removeEnraged(self):
        self.isEnraged = 0
        if self.baseFlameTrack != None:
            self.baseFlameTrack.finish()
        if self.flameTrack != None:
            self.flameTrack.finish()
        if self.flecksTrack != None:
            self.flecksTrack.finish()

    def makeIntoAbsorbing(self):
        self.isAbsorbing = 1

    def removeAbsorbing(self):
        self.isAbsorbing = 0

    def makeFrozen(self):
        self.isFrozen = 1

    def makeUnFrozen(self):
        self.isFrozen = 0

    def getDeepFrozenRounds(self):
        return self.isDeepFrozen

    def makeBattleSpeed(self, num):
        self.battleSpeed = num

    def makeUnBattleSpeed(self):
        self.battleSpeed = 0

    def getBattleSpeed(self):
        return self.battleSpeed

    def makeDeepFrozen(self, num):
        self.isDeepFrozen = num

    def makeUnDeepFrozen(self):
        self.isDeepFrozen = 0

    def makeIntoSoaked(self):
        self.isSoaked = 1

    def removeSoaked(self):
        self.isSoaked = 0

    def getHeadParts(self):
        return self.headParts

    def getAnimatedHeadParts(self):
        return self.animatedHeadParts

    def getRightHand(self):
        return self.rightHand

    def getLeftHand(self):
        return self.leftHand

    def getShadowJoint(self):
        return self.shadowJoint

    def getNametagJoints(self):
        return []


    def cleanupAllBattleEffects(suit):
        # -------------------------
        # suit-owned intervals
        # -------------------------
        intervalAttrs = [
            'mtrack',
            'splashInterval',
            'headInterval',
            'neutralInterval',
            'deathInterval',
            'headInterval2',
            'healInterval',
            'absorbInterval',
            'damageInterval',
            'hpTextInterval',
            'hpTextInterval2',

            # custom suit effect intervals
            'knifeTrack',
            'cheerTrack2',
            'bombTrack',
            'flameTrack',
            'liquidTrack',
            'oilTrack',
            'cheerTrack',
        ]

        for attr in intervalAttrs:
            interval = getattr(suit, attr, None)
            if interval:
                try:
                    interval.pause()
                except:
                    pass
                try:
                    interval.finish()
                except:
                    pass
                setattr(suit, attr, None)

        # -------------------------
        # suit sound sequences
        # -------------------------
        soundSequenceList = getattr(suit, 'soundSequenceList', None)
        if soundSequenceList:
            for seq in soundSequenceList:
                try:
                    seq.finish()
                except:
                    pass
            suit.soundSequenceList = []

        # -------------------------
        # suit particle effects
        # -------------------------
        particleAttrs = [
            'cheerEffect2',
            'flameEffect',
            'liquidEffect',
            'oilEffect',
            'cheerEffect',
        ]

        for attr in particleAttrs:
            effect = getattr(suit, attr, None)
            if effect:
                try:
                    effect.disable()
                except:
                    pass
                try:
                    if hasattr(effect, 'renderParent'):
                        effect.cleanup()
                except:
                    pass
                try:
                    effect.detachNode()
                except:
                    pass
                try:
                    if not effect.isEmpty():
                        effect.removeNode()
                except:
                    pass
                setattr(suit, attr, None)

        # -------------------------
        # suit nodepaths / pivots
        # -------------------------
        nodeAttrs = [
            'knifePivot',
            'bombPivot',
        ]

        for attr in nodeAttrs:
            node = getattr(suit, attr, None)
            if node:
                try:
                    if not node.isEmpty():
                        node.removeNode()
                except:
                    pass
                setattr(suit, attr, None)

        # -------------------------
        # suit prop lists
        # -------------------------
        listAttrs = [
            'bombProps',
        ]

        for attr in listAttrs:
            props = getattr(suit, attr, None)
            if props:
                for prop in props:
                    if prop:
                        if hasattr(prop, 'sparksEffect') and prop.sparksEffect:
                            effect = prop.sparksEffect
                            prop.sparksEffect = None

                            try:
                                effect.disable()
                            except:
                                pass
                            try:
                                if hasattr(effect, 'renderParent'):
                                    effect.cleanup()
                            except:
                                pass
                            try:
                                effect.detachNode()
                            except:
                                pass

                        try:
                            if not prop.isEmpty():
                                MovieUtil.removeProp(prop)
                        except:
                            pass

                setattr(suit, attr, [])

        # -------------------------
        # stock status props on suits
        # -------------------------
        for attr in ('stars', 'suedstars'):
            prop = getattr(suit, attr, None)
            if prop:
                try:
                    prop.stop()
                except:
                    pass
                try:
                    prop.detachNode()
                except:
                    pass

    def setSuitStatusEffect(self, name, modifier=0, turns=None, mode='setBoth'):
        if turns == 0:
            self.clearSuitStatusEffect(name)
            return

        if name == 'soaked' and self.hasSuitStatusEffect('drenched'):
            self.clearSuitStatusEffect('soaked')

            self.setSuitStatusEffect(
                'drenched',
                modifier=modifier,
                turns=turns,
                mode=mode
            )
            return
        
        if name == 'drenched' and self.hasSuitStatusEffect('soaked'):
            self.clearSuitStatusEffect('soaked')

        if name not in self.suitStatusEffects:
            self.suitStatusEffects[name] = {'modifier': modifier, 'turns': turns}
        else:
            if mode == 'setBoth':
                self.suitStatusEffects[name]['modifier'] = modifier
                self.suitStatusEffects[name]['turns'] = turns
            elif mode == 'refreshTurns':
                self.suitStatusEffects[name]['turns'] += turns
            elif mode == 'refreshModifier':
                self.suitStatusEffects[name]['modifier'] += modifier
            elif mode == 'refreshBoth':
                self.suitStatusEffects[name]['modifier'] += modifier
                self.suitStatusEffects[name]['turns'] += turns

        self.__startSuitStatusVisual(name, self.suitStatusEffects[name]['modifier'])

    def hasSuitStatusEffect(self, name):
        return name in self.suitStatusEffects

    def getSuitStatusModifier(self, name):
        if name not in self.suitStatusEffects:
            return 0
        return self.suitStatusEffects[name].get('modifier', 0)

    def getSuitStatusTurns(self, name):
        if name not in self.suitStatusEffects:
            return 0

        return self.suitStatusEffects[name].get('turns')

    def getSuitStatusEffects(self):
        return self.suitStatusEffects

    def decrementStatusEffects(self):
        for name in self.suitStatusEffects.keys():
            turns = self.suitStatusEffects[name].get('turns')

            # Permanent effect
            if turns is None:
                continue

            decrement = 1

            # Drenched loses an extra turn while zapped
            if name == 'drenched' and self.hasSuitStatusEffect('zapped'):
                decrement = 2

            if turns > 0:
                self.suitStatusEffects[name]['turns'] -= decrement

            if self.suitStatusEffects[name]['turns'] <= 0:
                self.clearSuitStatusEffect(name)

    def clearSuitStatusEffect(self, name):
        if name in self.suitStatusEffects:
            del self.suitStatusEffects[name]

        self.__stopSuitStatusVisual(name)

    def __startSuitStatusVisual(self, name, modifier):
        info = SUIT_STATUS_EFFECT_VISUALS.get(name)
        if not info:
            return

        startFunc = getattr(self, info.get('start'), None)
        if not startFunc:
            return

        if info.get('passModifier', False):
            startFunc()
        else:
            startFunc(modifier)

    def __stopSuitStatusVisual(self, name):
        info = SUIT_STATUS_EFFECT_VISUALS.get(name)
        if not info:
            return

        stopFunc = getattr(self, info.get('stop'), None)
        if stopFunc:
            stopFunc()

    def clearAllSuitStatusEffects(self):
        for name in list(self.suitStatusEffects.keys()):
            self.clearSuitStatusEffect(name)