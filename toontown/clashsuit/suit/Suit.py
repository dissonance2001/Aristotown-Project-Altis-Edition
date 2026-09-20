print(">>> EDITING THIS SUIT.PY <<<")
"""
Suit module: contains Suit class
"""
from direct.actor.Actor import Actor
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from otp.avatar import Avatar
from toontown.chat.enums.ChatChannel import ChatChannel
from toontown.chat.enums.ChatContentType import ChatContentType
from toontown.chat.enums.ChatNpcPreset import ChatNpcPreset
from toontown.clashsuit.suit import SuitDNA
from toontown.clashsuit.suit import SuitVoice
from toontown.clashsuit.suit.SuitDefinitionsBase import suitDefinitionObjects, ALL_SKELE_HEADS, suitGetNameWordwraps, \
    BodyModelTypeToPath, BodyModelTypeToUnemployedPath
from toontown.clashsuit.suit.heads.classes import *  # Instantiate all special suit heads
from toontown.clashsuit.suit.heads.AnimatedSuitHeadRepository import getAnimatedSuitHead
from toontown.toonbase import ToontownGlobals
from panda3d.core import *
from toontown.clashbattle.battle import SuitBattleGlobals
from toontown.nametag.NametagGroup import *
from toontown.clashsuit.suit.SuitAnimationIndex import *
from toontown.clashsuit.suit import SuitHealthMeter
from toontown.toonbase import TTLocalizer
from panda3d.core import Filename
from direct.interval.IntervalGlobal import ActorInterval, Sequence, Func
from toontown.clashsuit.suit import SuitGlobals

"""
Suit Types & Tracks

BossBot (Corporate): 'c'
 Flunky:          f
 PencilPusher:    p
 YesMan:          ym
 MicroManager:    mm
 DownSizer:       ds
 HeadHunter:      hh
 CorporateRaider: cr
 BigCheese:       bc

LawBot (Legal): 'l'
 BottomFeeder:    bf
 BloodSucker:     b
 DoubleTalker:    dt
 AmbulanceChaser: ac
 BackStabber:     bs
 SpinDoctor:      sd
 LegalEagle:      le
 BigWig:          bw

Boardbot: 'g'
 Bagholder:       bgh
 Paper Hands:     pph
 Insider:         ins
 Circuit Breaker: cbr
 Deadlock         dl
 Shark Watcher    shw
 Magnate          mg
 Head Honcho      hho

CashBot (Money): 'm'
 ShortChange:     sc
 PennyPincher:    pp
 TightWad:        tw
 BeanCounter:     bc
 NumberCruncher:  nc
 MoneyBags:       mb
 LoanShark:       ls
 RobberBaron:     rb

SellBot (Sales): 's'
 ColdCaller:      cc
 Telemarketer:    tm
 NameDropper:     nd
 GladHander:      gh
 Mover&Shaker:    ms
 TwoFaced:        tf
 TheMingler:      m
 Mr.Hollywood:    mh

Playground bosses:
 Derrick Man:                        derrman
 Land Acquisition Architect:         dlao
 Public Relations Representative:    dopr
 Derrick Hand:                       derrhand
 Director of Land Development:       dold
 Director of Public Affairs:         dopa

Facility bosses:
 Factory Foreman:                 foreman
 Mint Supervisor:                 supervis
 Head Attorney:                   clerk
 Club President:                  clubpres
 Autocaddie:                      autocad

Event bosses:
 Count Erclaim:                   count
 Redd 'Heir' Wing:                redd
 Witness Standin:                 standin

Etc.
 Chairman:                        chairman
 Ottoman:                         ottoman
 
LBHQ Hardmode Minibosses:
 Stenographer:                    stenog
 Scapegoat:                       sgoat
 Litigator:                       lgator
 Case Manager:                    caseman
"""

aSize = 6.06
bSize = 5.29
cSize = 4.14

dept2phase = {'g': 14,
              'c': 12,
              'l': 11,
              'm': 10,
              's': 9}

CustomSkelecogHeads = [suitDef.name for suitDef in suitDefinitionObjects() if suitDef.skeleHeadModel[0] not in ALL_SKELE_HEADS]

# Any Cogs that should do animation blending to reach their neutral
# (Usually used with custom neutral animations)
# Dict: {name: blend time}
AnimBlendNeutral = {
    'mplayer': {'time': 0.1},
    'chainsaw': {'time': 0.07},
}
for suitDef in suitDefinitionObjects():
    # Add all other cogs to the dict, if they're not already in it
    if suitDef.name not in AnimBlendNeutral:
        AnimBlendNeutral[suitDef.name] = {'time': 0.03}

ModelDict = {'a': ('/models/char/suitA-', 4),
    'b': ('/models/char/suitB-', 4),
    'c': ('/models/char/suitC-', 3.5)}
TutorialModelDict = {'a': ('/models/char/suitA-', 4),
    'b': ('/models/char/suitB-', 4),
    'c': ('/models/char/suitC-', 3.5)}

SuitNameWordwraps = suitGetNameWordwraps()


GenericSuitVoice = None
GenericSuitVoiceF = None
SuitVoiceCache = {}


def __getSuitVoiceFromCache(suit):
    return SuitVoiceCache.get(suit.style.name, None)


def __addSuitVoiceToCache(suit, suitVoice: SuitVoice):
    if __getSuitVoiceFromCache(suit):
        return False
    SuitVoiceCache[suit.style.name] = suitVoice
    return True


def loadDialog(suit):
    if suit.voice:
        return suit.voice
    else:
        # check cache
        cachedVoice = __getSuitVoiceFromCache(suit)
        if cachedVoice:
            return cachedVoice

        # get voice data
        suitName = suit.style.name
        phase = dept2phase.get(suit.style.dept)
        
        filePrefix = f'phase_{phase}/audio/dial/ttcc_ene_{suitName}'
        testFileName = Filename(filePrefix + '_grunt.ogg')
        skeleTestFileName = Filename(filePrefix + '_grunt_skel.ogg')
        testDeathFileName = Filename(filePrefix + '_death.ogg')
        skeleTestDeathFileName = Filename(filePrefix + '_death_skel.ogg')

        # is this voice generic?
        hasUniqueDialogue = vfs.resolveFilename(testFileName, getModelPath().getValue())
        hasUniqueSkelDialogue = vfs.resolveFilename(skeleTestFileName, getModelPath().getValue())
        hasUniqueDeath = vfs.resolveFilename(testDeathFileName, getModelPath().getValue())
        hasUniqueDeathSkel = vfs.resolveFilename(skeleTestDeathFileName, getModelPath().getValue())
        hasAnyUniqueDialogue = hasUniqueDialogue or hasUniqueSkelDialogue or \
                               hasUniqueDeath or hasUniqueDeathSkel

        if not hasAnyUniqueDialogue:
            global GenericSuitVoice
            global GenericSuitVoiceF
            # first, ensure that we have a generic cog voice for this suit.
            if (GenericSuitVoice and not suit.style.isFemale()) or (GenericSuitVoiceF and suit.style.isFemale()):
                # cache it as the generic one and use that.
                if not suit.style.isFemale():
                    __addSuitVoiceToCache(suit, GenericSuitVoice)
                    return GenericSuitVoice
                else:
                    __addSuitVoiceToCache(suit, GenericSuitVoiceF)
                    return GenericSuitVoiceF

        ext = '.ogg' if not suit.style.isFemale() else '_f.ogg'

        # try to load regular cog voice
        if hasUniqueDialogue:  # Search for custom voice files for this cog type first.
            grunt = loader.loadSfxRaw(f'{filePrefix}_grunt.ogg')
            murmur = loader.loadSfxRaw(f'{filePrefix}_murmur.ogg')
            statement = loader.loadSfxRaw(f'{filePrefix}_statement.ogg')
            question = loader.loadSfxRaw(f'{filePrefix}_question.ogg')
        else:
            grunt = loader.loadSfxRaw(f'phase_3.5/audio/dial/COG_VO_grunt{ext}')
            murmur = loader.loadSfxRaw(f'phase_3.5/audio/dial/COG_VO_murmur{ext}')
            statement = loader.loadSfxRaw(f'phase_3.5/audio/dial/COG_VO_statement{ext}')
            question = loader.loadSfxRaw(f'phase_3.5/audio/dial/COG_VO_question_1{ext}')

        # try to load skelecog cog voice
        if hasUniqueSkelDialogue:  # Search for skelecog voices if possible
            skelGrunt = loader.loadSfxRaw(f'{filePrefix}_grunt_skel.ogg')
            skelMurmur = loader.loadSfxRaw(f'{filePrefix}_murmur_skel.ogg')
            skelStatement = loader.loadSfxRaw(f'{filePrefix}_statement_skel.ogg')
            skelQuestion = loader.loadSfxRaw(f'{filePrefix}_question_skel.ogg')
        else:
            skelGrunt = loader.loadSfxRaw(f'phase_5/audio/dial/COG_VO_grunt_skel{ext}')
            skelMurmur = loader.loadSfxRaw(f'phase_5/audio/dial/COG_VO_murmur_skel{ext}')
            skelStatement = loader.loadSfxRaw(f'phase_5/audio/dial/COG_VO_statement_skel{ext}')
            skelQuestion = loader.loadSfxRaw(f'phase_5/audio/dial/COG_VO_question_skel{ext}')

        # try to load death sound
        if hasUniqueDeath:
            death = f'{filePrefix}_death.ogg'
        else:
            death = f'phase_3.5/audio/sfx/Cog_Death{ext}'

        # try to load death sound
        if hasUniqueDeathSkel:
            skelDeath = f'{filePrefix}_death_skel.ogg'
        else:
            skelDeath = f'phase_3.5/audio/sfx/Skel_Cog_Death{ext}'

        # put together suit voice
        array = (grunt, murmur, statement, question, grunt, murmur, statement)
        skelArray = (skelGrunt, skelMurmur, skelStatement, skelQuestion, skelGrunt, skelMurmur, skelStatement)

        voice = SuitVoice.SuitVoice(array, skelArray, death, skelDeath)

        # cache it
        __addSuitVoiceToCache(suit, voice)

        # set this as the generic one, in case it IS a generic one
        if not hasAnyUniqueDialogue:
            if not suit.style.isFemale():
                GenericSuitVoice = voice
            else:
                GenericSuitVoiceF = voice

        # return it
        return voice


def attachSuitHead(node, suitName, suitIndex=None):
    """ gets a suit head whose scale and vertical pos has been
    normalized to all the suit heads
    NOTE:  calling class is responsible for cleaning this up!
    (eg. self.head = None)
    """
    if suitIndex is None:
        suitIndex = SuitDNA.suitHeadTypes.index(suitName)
    suitDNA = SuitDNA.SuitDNA()
    suitDNA.newSuit(suitName)
    suit = Suit()
    suit.setDNA(suitDNA)
    headParts = suit.getHeadParts()
    head = node.attachNewNode('head')
    for part in headParts:
        copyPart = part.copyTo(head)
        # turn on depth write and test.
        copyPart.setDepthTest(1)
        copyPart.setDepthWrite(1)

    suit.delete()
    suit = None
    p1 = Point3()
    p2 = Point3()
    head.calcTightBounds(p1, p2)
    d = p2 - p1
    biggest = max(d[0], d[2])
    # make them ramp up slightly in size as we go down the row
    column = suitIndex % SuitDNA.suitsPerDept
    s = (0.2 + column / 100.0) / biggest
    # also make them move down slightly as we go across
    pos = -0.14 + (SuitDNA.suitsPerDept - column - 1) / 135.0
    head.setPosHprScale(0, 0, pos, 180, 0, 0, s, s, s)
    return head


@DirectNotifyCategory()
class Suit(Avatar.Avatar):
    """Suit class:"""
    
    __module__ = __name__

    def __init__(self):
        try:
            self.Suit_initialized
            return
        except:
            self.Suit_initialized = 1

        Avatar.Avatar.__init__(self)
        self.setFont(ToontownGlobals.getSuitFont())
        self.nametag.setSpeechFont(ToontownGlobals.getSuitFont())
        self.setPlayerType(NametagGroup.CCSuit)
        for tag in self.nametag.nametags:
            tag.setChatWordwrap(10.0)
        self.setPickable(1)
        self.leftHand = None
        self.rightHand = None
        self.shadowJoint = None
        self.nametagJoint = None
        self.headParts = []
        self.specialHead = None
        self.healthBar = None
        self.isDisguised = 0
        self.isWaiter = 0
        self.isElite = 0
        self.isVirtual = 0
        self.healthColored = False
        self.fired = False  # Used to track if the suit is unemployed via MovieFire or other battle movie
        self.headless = False
        self.crushed = False
        self.nametag.setNameWordwrap(8.0)
        self.isLured = False
        self.isSoaked = False
        self.isUntouchable = False
        self.splats = []
        self.voice = None
        self.splatCount = 0
        self.tintList = []
        self.tintSeq = None
        self.scaleList = []
        self.useAllSuitAnims = False  # for debugging
        # Dict containing blendNeutral related data for this cog
        self.blendNeutral = None

    def delete(self):
        try:
            self.Suit_deleted
            return
        except:
            self.Suit_deleted = 1

        if self.tintSeq:
            self.tintSeq.finish()
            self.tintSeq = None

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

        for part in self.headParts:
            if isinstance(part, Actor):
                part.cleanup()
                part.delete()
            else:
                part.removeNode()

        self.headParts = []
        self.removeHealthBar()
        if self.specialHead:
            self.specialHead.cleanup()
            self.specialHead.destroy()
            del self.specialHead

        Avatar.Avatar.delete(self)

    def setHeight(self, height):
        Avatar.Avatar.setHeight(self, height)
        # Put our name tag higher, since it has three lines...
        self.nametag3d.setPos(0, 0, height + 1.0)

    def getRadius(self):
        # Suits have a fatter collision volume than toons.
        return 2

    def setDNAString(self, dnaString):
        self.dna = SuitDNA.SuitDNA()
        self.dna.makeFromNetString(dnaString)
        self.setDNA(self.dna)

    def setDNA(self, dna):
        if self.style:
            return

        # store the DNA
        self.style = dna
        self.generateSuit()
        self.initializeDropShadow()
        self.initializeNametag3d()
        self.setShaderAuto()

    def generateSuit(self):
        """
        Create a suit from dna (an array of strings)
        """
        dna = self.style
        self.headParts = []

        self.headTexture = None
        self.skeleHeadTexture = None
        self.tieType = 0
        self.bodyTexture = ''
        self.skeleBodyTexture = ''
        self.bodyTint = None

        # For suit zap animation
        self.zapHeadActor = None
        self.zapActor = None

        # Have we become a skelecog?
        self.isSkeleton = 0

        if dna.name in SuitGlobals.suitProperties:
            self.scale = SuitGlobals.suitProperties[dna.name][SuitGlobals.SCALE_INDEX]
            self.handColor = SuitGlobals.suitProperties[dna.name][SuitGlobals.HAND_COLOR_INDEX]
            self.tieType = SuitGlobals.suitProperties[dna.name][SuitGlobals.TIE_INDEX]

            if SuitGlobals.suitProperties[dna.name][SuitGlobals.BODY_TEXTURE_INDEX]:
                self.bodyTexture = SuitGlobals.suitProperties[dna.name][SuitGlobals.BODY_TEXTURE_INDEX]
            if SuitGlobals.suitProperties[dna.name][SuitGlobals.SKELE_BODY_TEXTURE_INDEX]:
                self.skeleBodyTexture = SuitGlobals.suitProperties[dna.name][SuitGlobals.SKELE_BODY_TEXTURE_INDEX]
            if SuitGlobals.suitProperties[dna.name][SuitGlobals.BODY_TINT_INDEX]:
                self.bodyTint = SuitGlobals.suitProperties[dna.name][SuitGlobals.BODY_TINT_INDEX]

            self.generateBody()

            if SuitGlobals.suitProperties[dna.name][SuitGlobals.HEAD_TEXTURE_INDEX]:
                self.headTexture = SuitGlobals.suitProperties[dna.name][SuitGlobals.HEAD_TEXTURE_INDEX]
            if SuitGlobals.suitProperties[dna.name][SuitGlobals.SKELE_HEAD_TEXTURE_INDEX]:
                self.skeleHeadTexture = SuitGlobals.suitProperties[dna.name][SuitGlobals.SKELE_HEAD_TEXTURE_INDEX]

            self.voice = loadDialog(self)

            for head in SuitGlobals.suitProperties[dna.name][SuitGlobals.HEADS_INDEX]:
                self.generateHead(head)

            self.setHeight(SuitGlobals.suitProperties[dna.name][SuitGlobals.HEIGHT_INDEX])

        self.setName(SuitBattleGlobals.SuitAttributes[dna.name]['name'])
        self.getGeomNode().setScale(self.scale)
        self.generateCorporateMedallion()

    def initializeNametag3d(self):
        super().initializeNametag3d()
        # Set nametag wordwrap based on the specific suit
        self.nametag.setNameWordwrap(SuitNameWordwraps.get(self.style.name, 8.0))

    def generateBody(self):
        """
        Load the appropriate suit body and anims
        """
        # get the anims
        animDict = self.generateAnimDict()

        bodyModelType = SuitGlobals.suitProperties[self.style.name][SuitGlobals.BODY_MODEL_INDEX]
        filepath = BodyModelTypeToPath[bodyModelType].format(suitType=self.style.body.upper())
        self.loadModel(loader.loadModel(filepath), copy=True)
        self.loadAnims(animDict)
        if self.style.name == 'mm':
            self.setPlayRate(1.5, 'walk')
            self.setPlayRate(1.5, 'run')
        self.setSuitClothes()
        self.setBlend(frameBlend=base.wantSmoothAnims)
        self.setLODAnimation(base.lodMaxRange, base.lodMinRange, base.lodDelayFactor)
        if self.bodyTint:
            self.addTint(self.bodyTint)

        if self.style.name in AnimBlendNeutral:
            self.blendNeutral = AnimBlendNeutral[self.style.name]

    def generateAnimDict(self, skeleton=False):
        # compile a dictionary of all anims for this suit in the format
        # { "animName" : "animFilePath", ... }
        animDict = {}

        filePrefix, bodyPhase = ModelDict[self.style.body]

        # load all shared anims
        for anim in AllSuits:
            # a=4, b=4, c=3.5
            animDict[anim[0]] = 'phase_' + str(bodyPhase) + filePrefix + anim[1]

        for anim in AllSuitsMinigame:
            # a=4, b=4, c=4
            animDict[anim[0]] = 'phase_4' + filePrefix + anim[1]

        for anim in AllSuitsTutorialBattle:
            # a = 4, b = 4, c = 3.5
            filePrefix, bodyPhase = TutorialModelDict[self.style.body]
            animDict[anim[0]] = 'phase_' + str(bodyPhase) + filePrefix + anim[1]

        for anim in AllSuitsBattle:
            # a=5, b=5, c=5
            animDict[anim[0]] = 'phase_5' + filePrefix + anim[1]

        if self.style.body == 'a':
            animDict['neutral'] = 'phase_4/models/char/suitA-neutral'
            for anim in SuitsCEOBattle:
                animDict[anim[0]] = 'phase_12/models/char/suitA-' + anim[1]
        elif self.style.body == 'b':
            animDict['neutral'] = 'phase_4/models/char/suitB-neutral'
            if self.style.name in ('count', 'btto'):
                animDict['count-neutral'] = 'phase_4/models/char/suitB-count-neutral'
            for anim in SuitsCEOBattle:
                animDict[anim[0]] = 'phase_12/models/char/suitB-' + anim[1]
        elif self.style.body == 'c':
            animDict['neutral'] = 'phase_3.5/models/char/suitC-neutral'
            for anim in SuitsCEOBattle:
                animDict[anim[0]] = 'phase_12/models/char/suitC-' + anim[1]

        # load the suit specific anims
        if self.useAllSuitAnims:
            animList = {
                'a': AllSuitAAnims,
                'b': AllSuitBAnims,
                'c': AllSuitCAnims,
            }.get(self.style.body)
        else:
            animList = {
                'a': SuitAAnims,
                'b': SuitBAnims,
                'c': SuitCAnims,
            }.get(self.style.body)

        # any additional anims?
        additionalAnims = AdditionalSuitAnims.get(self.style.name, [])
        for anim in animList + additionalAnims:
            phase = 'phase_' + str(anim[2])
            animDict[anim[0]] = phase + filePrefix + anim[1]

        # Override lose animation for skelecog actors
        if skeleton:
            animDict['lose'] = f'phase_5/models/char/suit{self.style.body.upper()}-skeleton-lose'

        return animDict

    """
    Animation helper functions
    """

    def initializeBodyCollisions(self, collIdStr):
        Avatar.Avatar.initializeBodyCollisions(self, collIdStr)
        if not self.ghostMode:
            self.collNode.setCollideMask(self.collNode.getIntoCollideMask() | ToontownGlobals.PieBitmask)

    def setSuitClothes(self, modelRoot=None, texOverride=None):
        """
        Set the appropriate textures for this suit dept.
        """
        if not modelRoot:
            modelRoot = self

        bodyTexturePath = texOverride if texOverride else self.bodyTexture
        if bodyTexturePath.find('**/') != -1:
            clothesModel = loader.loadModel('char/suit/models/cc_m_texcard_ene_suit_body_common')
            bodyTex = clothesModel.find(bodyTexturePath).findTexture('*')
            clothesModel.removeNode()
        else:
            bodyTex = loader.loadTexture(bodyTexturePath)

        bodyTex.setMinfilter(Texture.FTLinearMipmapLinear)
        bodyTex.setMagfilter(Texture.FTLinear)

        modelRoot.find('**/body').setTexture(bodyTex, 1)
        modelRoot.find('**/hands').setTexture(bodyTex, 1)

        tieSkinny = modelRoot.find('**/necktie-s')
        tieBroad = modelRoot.find('**/necktie-w')
        tieBow = modelRoot.find('**/bowtie')

        if self.tieType == -1:
            tieBroad.hide()
            tieSkinny.hide()
            tieBow.hide()
        if self.tieType == 0:
            tieBroad.setTexture(bodyTex, 1)
            tieSkinny.hide()
            tieBow.hide()
        elif self.tieType == 1:
            tieBroad.hide()
            tieSkinny.setTexture(bodyTex, 1)
            tieBow.hide()
        else:
            tieBroad.hide()
            tieSkinny.hide()
            tieBow.setTexture(bodyTex, 1)

        # set hand color
        modelRoot.find('**/hands').setColorScale(self.handColor)

        # find the useful nulls
        self.leftHand = self.find('**/joint_Lhold')
        self.rightHand = self.find('**/joint_Rhold')
        self.shadowJoint = self.find('**/joint_shadow')
        self.nametagJoint = self.find('**/joint_nameTag')

        self.isWaiter = False

    def setSkeleClothes(self, modelRoot=None, elite=False, texOverride=None):
        """
        Set the appropriate textures for this suit dept.
        """
        if not modelRoot:
            modelRoot = self

        if texOverride:
            bodyTexturePath = texOverride
        elif self.skeleBodyTexture:
            bodyTexturePath = self.skeleBodyTexture
        else:
            bodyTexturePath = f"**/skel_body_{SuitGlobals.DeptCharToTexShorthand[self.style.dept]}_{'exe' if elite else 'gen'}"

        if bodyTexturePath.find('**/') != -1:
            clothesModel = loader.loadModel('char/suit/models/cc_m_texcard_ene_skel_body_common')
            bodyTex = clothesModel.find(bodyTexturePath).findTexture('*')
            clothesModel.removeNode()
        else:
            bodyTex = loader.loadTexture(bodyTexturePath)

        bodyTex.setMinfilter(Texture.FTLinearMipmapLinear)
        bodyTex.setMagfilter(Texture.FTLinear)

        modelRoot.find('**/body').setTexture(bodyTex, 1)
        # Don't override the texture if there is any sort of custom skelecog head,
        # OR if we are passing in our own modelRoot for zap actors and whatnot
        if not (modelRoot != self or self.skeleHeadTexture or SuitGlobals.suitProperties[self.style.name][SuitGlobals.SKELE_HEADS_INDEX][0] not in ALL_SKELE_HEADS):
            self.headParts[0].setTexture(bodyTex, 1)

        if elite and self.specialHead:
            self.specialHead.makeExecutive(isSkeleton=True)

        tieSkinny = modelRoot.find('**/necktie-s')
        tieBroad = modelRoot.find('**/necktie-w')
        tieBow = modelRoot.find('**/bowtie')

        if self.tieType == -1:
            tieBroad.hide()
            tieSkinny.hide()
            tieBow.hide()
        if self.tieType == 0:
            tieBroad.setTexture(bodyTex, 1)
            tieSkinny.hide()
            tieBow.hide()
        elif self.tieType == 1:
            tieBroad.hide()
            tieSkinny.setTexture(bodyTex, 1)
            tieBow.hide()
        else:
            tieBroad.hide()
            tieSkinny.hide()
            tieBow.setTexture(bodyTex, 1)

    def makeWaiter(self, modelRoot=None):
        """
        Set the appropriate textures for a bosscog battle waiter
        """
        if self.isSkeleton:
            # Stinky skelecogs don't need to be waiters >:(
            return
        if not modelRoot:
            modelRoot = self

        clothesModel = loader.loadModel('char/suit/models/cc_m_texcard_ene_suit_body_common')
        bodyTex = clothesModel.find(f"**/suit_body_waiter_{'exe' if self.isElite else 'gen'}").findTexture('*')
        clothesModel.removeNode()

        bodyTex.setMinfilter(Texture.FTLinearMipmapLinear)
        bodyTex.setMagfilter(Texture.FTLinear)

        modelRoot.find('**/body').setTexture(bodyTex, 1)
        modelRoot.find('**/hands').setTexture(bodyTex, 1)
        modelRoot.find('**/necktie-s').hide()
        modelRoot.find('**/necktie-w').hide()
        if self.style.name in SuitBattleGlobals.NO_TIE_SUITS:
            modelRoot.find('**/bowtie').hide()
        else:
            bowtie = modelRoot.find('**/bowtie')
            bowtie.setTexture(bodyTex, 1)
            bowtie.show()

        self.isWaiter = True

    def makeVirtual(self, modelRoot = None, healthColored=False, deathSuit=False):
        if not modelRoot:
            modelRoot = self
        actorNode = modelRoot.find('**/__Actor_modelRoot')
        actorCollection = actorNode.findAllMatches('*')
        self.isVirtual = 1
        for part in self.headParts:
            part.setTwoSided(False)

        color = (0.0, 1.0, 0.0, 1.0) if healthColored and not deathSuit else (1.0, 0.0, 0.0, 1.0)
        self.healthColored = healthColored

        for thing in actorCollection:
            if thing.getName() not in ('joint_attachMeter', 'joint_nameTag', 'def_nameTag'):
                thing.setColorScale(color)
                thing.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd))
                thing.setDepthWrite(False)
                thing.setBin('fixed', 1)
        if hasattr(self, 'healthBar'):
            for part in self.healthBar.getParts():
                part.stash()

    def makeExecutive(self, modelRoot=None):
        if not modelRoot:
            modelRoot = self
        dept = self.style.dept
        if self.isSkeleton:
            return

        self.isElite = 1
        if self.specialHead:
            self.specialHead.makeExecutive()

        bodyTex = None
        if self.bodyTexture.find('**/') != -1:
            clothesModel = loader.loadModel('char/suit/models/cc_m_texcard_ene_suit_body_common')
            bodyTex = clothesModel.find(f"**/suit_body_{SuitGlobals.DeptCharToTexShorthand[dept]}_exe").findTexture('*')
            clothesModel.removeNode()
        else:
            texName = self.bodyTexture[:-4]
            fileExt = self.bodyTexture[-4:]
            texFileName = Filename(texName + '_e' + fileExt)
            if vfs.resolveFilename(texFileName, getModelPath().getValue()):
                bodyTex = loader.loadTexture(texName + '_e' + fileExt)

        if bodyTex is not None:
            bodyTex.setMinfilter(Texture.FTLinearMipmapLinear)
            bodyTex.setMagfilter(Texture.FTLinear)

            modelRoot.find('**/body').setTexture(bodyTex, 1)
            modelRoot.find('**/hands').setTexture(bodyTex, 1)
            modelRoot.find('**/necktie-s').setTexture(bodyTex, 1)
            modelRoot.find('**/necktie-w').setTexture(bodyTex, 1)
            modelRoot.find('**/bowtie').setTexture(bodyTex, 1)

    def makeUnemployed(self):
        if self.isSkeleton:
            self.setSkeleClothes(texOverride='phase_5/maps/ttcc_ene_skelecog_unemployed.png')
        else:
            bodyModelType = SuitGlobals.suitProperties[self.style.name][SuitGlobals.BODY_MODEL_INDEX]
            unemployedTexPath = BodyModelTypeToUnemployedPath.get(bodyModelType, 'phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
            self.setSuitClothes(texOverride=unemployedTexPath)

        if self.specialHead:
            self.specialHead.makeUnemployed(isSkeleton=self.isSkeleton)

    def generateHead(self, headType, skeleton=False):
        """generateHead(self, string)
        Manipulate the head model to display only the appropriate head
        """
        # Check if we're using custom/Non-TTO-standard cog heads
        if "phase_" in headType:
            # Is it an animated suit head?
            if "-zero" in headType:
                # All suit actors have a -zero base model
                self.generateCustomHead(headType, skeleton=skeleton)
                return
            # Looks like it's a non-animated custom cog head then.
            headModel = loader.loadModel(headType)
            headReferences = headModel.findAllMatches("*")
        else:
            filePrefix, phase = ModelDict[self.style.body]
            headModel = loader.loadModel('phase_' + str(phase) + filePrefix + 'heads')
            headReferences = headModel.findAllMatches('**/' + headType)
        for hp in headReferences:
            headPart = self.instance(hp, 'modelRoot', 'joint_head')
            headPart.setTwoSided(True)
            self.headParts.append(headPart)

        headModel.removeNode()

    def generateCustomHead(self, headType, skeleton=False):
        headTexture = self.headTexture if not skeleton else self.skeleHeadTexture
        # Grab suit head from repostitory
        suitHead = getAnimatedSuitHead(self.style.name)
        # Instantiate class
        suitHead(self, headType, headTexture, isSkeleton=skeleton)

    def getDialogTypeName(self, chatString):
        searchString = chatString.lower()
        stringLength = len(chatString)
        if stringLength <= TTLocalizer.DialogLength1:
            length = 1
        elif stringLength <= TTLocalizer.DialogLength2:
            length = 2
        elif stringLength <= TTLocalizer.DialogLength3:
            length = 3
        else:
            length = 4
        if searchString.find(TTLocalizer.DialogSpecial) >= 0:
            type = 'murmur'
        elif searchString.find(TTLocalizer.DialogExclamation) >= 0:
            type = 'grunt'
        elif searchString.find(TTLocalizer.DialogQuestion) >= 0:
            type = 'question'
        elif searchString.find(TTLocalizer.DialogIndifferent) >= 0:
            type = 'statement'
            return type
        else:
            type = 'statement'
        if type == 'statement':
            if length == 1:
                type = 'grunt'
            elif length == 2:
                type = 'murmur'
            elif length >= 3:
                type = 'statement'
        return type

    def setChatAbsolute(self, chatString, chatFlags, dialogue=None, interrupt=1, wantBalloonAnim=True, wantHeadAnim=True, wantSound=True):
        Avatar.Avatar.setChatAbsolute(self, chatString, chatFlags, dialogue, interrupt, wantBalloonAnim, wantSound=wantSound)
        senderId = 0 if not hasattr(self, 'doId') else self.doId
        if base.cr:
            base.cr.chatManager.receiveChatMessage(ChatChannel.NPC, ChatNpcPreset.Cog, ChatContentType.Text, chatString, senderId, self.getName())

        if self.specialHead and wantHeadAnim:
            type = self.getDialogTypeName(chatString)
            animation = type if type in self.specialHead.getAnimNames() else 'talk'
            seq = Sequence(ActorInterval(self.specialHead, animation), Func(self.specialHead.loopNeutral))
            seq.start()

    def clearChat(self):
        Avatar.Avatar.clearChat(self)
        if self.specialHead:
            self.specialHead.loopNeutral()

    def getHealthPercentage(self):
        try:
            health = self.getHp() / self.getMaxHp()
        except:
            health = 0.96
        return health

    def generateCorporateMedallion(self, skeleton=False, generateNew=False):
        if not self.healthBar or generateNew:
            if self.healthBar:
                self.removeHealthBar()
            self.healthBar = SuitHealthMeter.SuitHealthMeter(self)
            self.healthBar.generate(skeleton=skeleton, startMode=SuitHealthMeter.MODE_ROAM)
        else:
            self.healthBar.updateMeterMode(SuitHealthMeter.MODE_ROAM)

    def removeHealthBar(self):
        if self.healthBar:
            self.healthBar.delete()
            self.healthBar = None

    def updateHealthBar(self, hp, forceUpdate = 0):
        if self.hp is not None:
            self.hp = max(self.hp + hp, 0)

        if self.healthBar:
            self.healthBar.updateHealthBar(forceUpdate)

        from toontown.gui.game.condition.ConditionGlobals import RefreshMsg
        messenger.send(RefreshMsg)

    def updateHealthMeterMode(self, newMode):
        if self.healthBar:
            self.healthBar.updateMeterMode(newMode)

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

    def getZapActor(self):
        if self.zapHeadActor is None:
            # We are faking an animated head here, not generating a whole custom class for it
            hName = SuitGlobals.suitProperties[self.style.name][SuitGlobals.SKELE_HEADS_INDEX][0][:-4]
            self.zapHeadActor = Actor(hName + 'zero', {'stun': hName + 'stun'})
            self.zapHeadActor.pose('stun', 5)
            # Modify the geom of the zap head actor if we need to, based on what head class this guy uses
            if self.specialHead:
                self.specialHead.modifyZapHeadActor(self.zapHeadActor)
            # Make sure to show the elite skelecog texture if they are elite
            if self.isElite and self.style.name not in CustomSkelecogHeads:
                clothesModel = loader.loadModel('char/suit/models/cc_m_texcard_ene_skel_body_common')
                eliteTex = clothesModel.find(f'**/skel_body_{SuitGlobals.DeptCharToTexShorthand[self.style.dept]}_exe').findTexture('*')
                clothesModel.removeNode()
                eliteTex.setMinfilter(Texture.FTLinearMipmapLinear)
                eliteTex.setMagfilter(Texture.FTLinear)
                self.zapHeadActor.setTexture(eliteTex, 1)
            if self.specialHead and self.isElite:
                self.specialHead.makeExecutive(headGeom=self.zapHeadActor, isSkeleton=True)

        if self.zapActor is None:
            actorModel = f'phase_5/models/char/suit{self.style.body.upper()}_skeleton-zero'
            filePrefix, phase = TutorialModelDict[self.style.body]
            
            animPrefix = 'phase_5' + filePrefix
            anims = {'small-zap': animPrefix + 'small-zap',
                     'large-zap': animPrefix + 'large-zap'}
            self.zapActor = Actor(actorModel, anims)
            self.setSkeleClothes(self.zapActor, elite=self.isElite)

        self.zapActor.setScale(self.getCombinedScale() * self.scale)
        self.zapActor.setPos(self.getPos())
        self.zapActor.setHpr(self.getHpr())
        self.zapHeadActor.reparentTo(self.zapActor.find('**/joint_head'))
        shadowJoint = self.zapActor.find('**/joint_shadow')
        dropShadow = loader.loadModel('phase_3/models/props/drop_shadow')
        dropShadow.setScale(0.45)
        dropShadow.setColor(0.0, 0.0, 0.0, 0.5)
        dropShadow.reparentTo(shadowJoint)
        return self.zapActor

    def cleanupZapActor(self):
        self.notify.debug('cleanupZapActor()')
        if self.zapActor is not None:
            self.notify.debug('cleanupZapActor() - got one')
            self.zapActor.cleanup()
        if self.zapHeadActor is not None:
            self.notify.debug('cleanupZapActor() - got their head')
            self.zapHeadActor.cleanup()

        self.zapActor = None
        self.zapHeadActor = None

    """
    Size Setting
    """

    def addScale(self, scale: float, stack=True):
        """
        Adds a Scale to the Suit.
        :param scale: The scale to add.
        :param stack: Should this scale be added several times?
        :return: True, or False if unsuccessful.
        """
        if scale in self.scaleList and not stack:
            return False

        self.scaleList.append(scale)

        # update the cog's scale
        self.updateScale()
        return True

    def removeScale(self, scale, wantAll=False):
        """
        Removes a scale from the Suit.
        :param scale: The scale to remove.
        :param wantAll: Remove all of the scales of this value.
        :return: True, or False if unsuccessful.
        """
        if scale not in self.scaleList:
            return False

        # remove the scale
        self.scaleList.remove(scale)

        # check if we want More
        if wantAll:
            while scale in self.scaleList:
                self.scaleList.remove(scale)

        # update the cog's scale
        self.updateScale()
        return True

    def getCombinedScale(self):
        """
        Gets the combined scale of this Suit.
        :return: None.
        """
        retScale = 1.0
        for scale in self.scaleList:
            retScale *= scale
        return retScale

    def updateScale(self):
        """
        Updates the scale of this Suit.
        :return: None.
        """
        self.setScale(self.getCombinedScale())

    """
    Clothes Tinting
    """

    def addTint(self, rgbaTint, stack=False):
        """
        Adds a Tint to the Suit's clothes.
        :param rgbaTint: An RGBA tuple of the tint to add.
        :param stack: Should this tint be added several times?
        :return: True, or False if unsuccessful.
        """
        if rgbaTint in self.tintList and not stack:
            return False
        assert len(rgbaTint) == 4
        self.tintList.append(rgbaTint)

        # update the cog's tint
        self.tintCogClothes()
        return True

    def lerpAddTint(self, rgbaTint, stack=False, duration=1.0, blendType='noBlend', startSeq=False):
        """
        Adds a Tint to the Suit's clothes, and returns a seq lerping to the new tint.
        :param rgbaTint: An RGBA tuple of the tint to add.
        :param stack: Should this tint be added several times?
        :return: A Sequence if successful, or None if not
        """
        startTint = self.getTint()
        success = self.addTint(rgbaTint, stack=stack)
        if not success:
            return Sequence()

        newTint = self.getTint()

        def updateTint(value, oldColor, newColor):
            newColor = (oldColor * (1 - value)) + (newColor * value)
            self.tintCogClothes(forceColor=newColor)

        if self.tintSeq:
            self.tintSeq.finish()

        from direct.interval.IntervalGlobal import LerpFunctionInterval
        self.tintSeq = LerpFunctionInterval(updateTint, duration, extraArgs=[startTint, newTint], blendType=blendType)
        if startSeq:
            self.tintSeq.start()
        return self.tintSeq

    def removeTint(self, rgbaTint, wantAll=True):
        """
        Removes a Tint from the Suit's clothes.
        :param rgbaTint: An RGBA tuple of the tint to remove.
        :param wantAll: Remove all of the tints of this value.
        :return: True, or False if unsuccessful.
        """
        if rgbaTint not in self.tintList:
            return False

        # remove the tint
        self.tintList.remove(rgbaTint)

        # check if we want More
        if wantAll:
            while rgbaTint in self.tintList:
                self.tintList.remove(rgbaTint)

        # update the cog's tint
        self.tintCogClothes()
        return True

    def getTint(self):
        """
        Gets the combined tint off this Suit.
        :return: None.
        """
        retTint = [1.0, 1.0, 1.0, 1.0]
        for tint in self.tintList:
            r, g, b, a = tint
            retTint[0] *= r
            retTint[1] *= g
            retTint[2] *= b
            retTint[3] *= a
        return Vec4(*retTint)

    def hasTints(self):
        """
        Returns if this Suit has any tints on it.
        :return: True or False.
        """
        return bool(self.tintList)

    def tintCogClothes(self, modelRoot=None, forceColor=None):
        # get the color's tint and then do magic
        color = forceColor or self.getTint()
        actorNode = self.find('**/__Actor_modelRoot') if not modelRoot else modelRoot
        actorCollection = actorNode.findAllMatches('*')
        for thing in actorCollection:
            if thing.getName() == 'body' or (thing.getName() == 'joint_head' and self.isSkeleton):
                thing.setColorScale(color)

    # the load seperate cog geometry for cogs that become cog skeletons
    def makeSkeleton(self, elite=False, wantName=True):
        """
        Convert to skeleton geometry.
        """
        model = f'phase_5/models/char/suit{self.style.body.upper()}_skeleton-zero'
        anims = self.generateAnimDict(skeleton=True)

        # remember the current anim
        anim = self.getCurrentAnim()

        # grab the drop shadow
        dropShadow = self.dropShadow
        if not dropShadow.isEmpty():
            dropShadow.reparentTo(hidden)

        # remove the old geometry
        self.removePart('modelRoot')

        # load the skeleton geometry
        self.loadModel(model, copy=True)
        self.loadAnims(anims)

        if self.style.name == 'mm':
            self.setPlayRate(1.5, 'walk')
            self.setPlayRate(1.5, 'run')

        for part in self.headParts:
            if isinstance(part, Actor):
                part.cleanup()
                part.delete()
            else:
                part.removeNode()
        self.headParts = []

        # Generate our skelecog head(s)
        for head in SuitGlobals.suitProperties[self.style.name][SuitGlobals.SKELE_HEADS_INDEX]:
            self.generateHead(head, skeleton=True)

        # set the scale on the skeleton actor (plus a little extra to make it look right)
        # self.getGeomNode().setScale(self.scale * 1.0173) # Remnant from the past? Leaving it commented out in case we revisit. May not apply with new models
        self.generateCorporateMedallion(skeleton=True, generateNew=True)
        # set the appropriate tie texture
        self.setSkeleClothes(elite=elite)
        self.setHeight(self.height)
        self.setBlend(frameBlend = base.wantSmoothAnims)
        self.setLODAnimation(base.lodMaxRange, base.lodMinRange, base.lodDelayFactor)

        # redo the nametag and drop shadow
        if (self.style.name in SuitDNA.suitHeadTypes or SuitDNA.isAlternate(self.style.name)) and wantName:
            nameInfo = self.createNameInfo()
            self.setDisplayName(nameInfo)

        # re-find the useful nulls
        self.leftHand = self.find('**/joint_Lhold')
        self.rightHand = self.find('**/joint_Rhold')
        self.shadowJoint = self.find('**/joint_shadow')
        self.nametagNull = self.find('**/joint_nameTag')

        if not dropShadow.isEmpty():
            dropShadow.setScale(0.75)
            if not self.shadowJoint.isEmpty():
                dropShadow.reparentTo(self.shadowJoint)

        # start the animation again
        self.loop(anim)

        # set the flag
        self.isSkeleton = 1

        # confirm tint
        self.tintCogClothes()

    # getters and setters
    def getHeadParts(self):
        """
        Return the list of stored head parts
        """
        return self.headParts

    def getRightHand(self):
        """
        Return the null in the right hand
        """
        return self.rightHand

    def getLeftHand(self):
        """
        Return the null in the left hand
        """
        return self.leftHand

    def getShadowJoint(self):
        """
        Return the node for attaching the shadow
        """
        return self.shadowJoint

    def getNametagJoints(self):
        """
        Return the CharacterJoint that animates the nametag, in a list.
        """
        # Not sure what the name is right now.
        return []

    def getDialogueArray(self):
        if self.isSkeleton or self.style.name == 'clubpres':
            return self.voice.getSkelVoiceArray()
        else:
            return self.voice.getVoiceArray()

    def isMiniboss(self):
        return self.dna.name in SuitBattleGlobals.COG_MINIBOSSES

    def createNameInfo(self, wantDept=True):
        nameName = self._name
        if self.isSkeleton and self.style.name in SuitDNA.suitHeadTypes or SuitDNA.isAlternate(self.style.name):
            nameName = TTLocalizer.Skeleton
        nameDept = self.getStyleDept()
        nameLevel = str(self.getActualLevel())
        if self.isElite and not self.isMiniboss():
            nameLevel += TTLocalizer.AvatarSuitPanelExecutive
        elif self.isMiniboss():
            nameLevel += TTLocalizer.AvatarSuitPanelManager
        if wantDept:
            nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': nameName,
                                                            'dept': nameDept,
                                                            'level': nameLevel}
        else:
            nameInfo = TTLocalizer.SuitBaseNameWithNoDept % {'name': nameName,
                                                             'level': nameLevel}
        return nameInfo
    
    def initName(self):
        self.addActive()
        self.setPickable(0)

        nameInfo = self.createNameInfo()
        self.setName(nameInfo)
        self.setDisplayName(nameInfo)
        self.showNametag3d()
        self.hideNametag2d()

    def getStyleDept(self):
        if getattr(self, 'dna', None):
            return SuitDNA.getDeptFullname(self.dna.dept)
        self.notify.error('called getStyleDept() before dna was set!')
        return 'unknown'

    def getAnimBlendNeutralData(self):
        """
        Returns the data that this suit should use to blend to neutral.
        """
        for ve in self.getVisualEffects()[::-1]:
            blendNeutralData = ve.animBlendNeutralData
            if blendNeutralData is not None:
                return blendNeutralData
        return self.blendNeutral

    def getPreAttackSeq(self):
        """
        Returns a potential sequence that this suit should use before an attack animation goes off.
        """
        newSeq = Sequence()
        for ve in self.getVisualEffects()[::-1]:
            seq = ve.getPreAttackSequence()
            if seq:
                newSeq.append(seq)

        return newSeq

    def getPostAttackSeq(self):
        """
        Returns a potential sequence that this suit should use after an attack animation goes off.
        """
        newSeq = Sequence()
        for ve in self.getVisualEffects()[::-1]:
            seq = ve.getPostAttackSequence()
            if seq:
                newSeq.append(seq)

        return newSeq

    def getWantBeginAttackNeutral(self):
        """
        Returns a bool if this suit wants the neutral at the beginning of attacks
        """
        for ve in self.getVisualEffects()[::-1]:
            wantAttack = ve.wantBeginAttackNeutral
            if wantAttack is not None:
                return wantAttack

        return True

    def getWantEndAttackNeutral(self):
        """
        Returns a bool if this suit wants the neutral at the end of attacks
        """
        for ve in self.getVisualEffects()[::-1]:
            wantAttack = ve.wantEndAttackNeutral
            if wantAttack is not None:
                return wantAttack

        return True
