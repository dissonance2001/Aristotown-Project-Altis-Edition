import random
import types
import json
import os
import math
from toontown.toon import AccessoryGlobals
from toontown.battle import BattleParticles
from toontown.toon import Motion
from toontown.toon import TTEmote
from toontown.toon import ToonDNA
from direct.actor import Actor
from direct.directnotify import DirectNotifyGlobal
from direct.interval.IntervalGlobal import *
from toontown.battle import MovieUtil
from toontown.toonbase.ToonPythonUtil import Functor
from direct.task.Task import Task
from panda3d.core import *
from toontown.battle.BattleProps import *
from toontown.toon.LaffMeter import LaffMeter
from direct.particles import ParticleEffect
from toontown.toon.ToonHead import *
from otp.avatar import Avatar
from otp.avatar import Emote
from otp.avatar.Avatar import teleportNotify
from otp.otpbase import OTPGlobals
from otp.otpbase import OTPLocalizer
from toontown.battle import SuitBattleGlobals
from toontown.chat.ChatGlobals import *
from toontown.distributed import DelayDelete
from toontown.effects import DustCloud
from toontown.effects import Wake
from toontown.hood import ZoneUtil
from toontown.nametag.NametagGlobals import *
from toontown.suit import SuitDNA
from toontown.suit import Suit
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownGlobals


def _getAccessoryPlacementOverride(accessoryType, accessoryId, dnaKey):
    relativePath = os.path.join(
        'resources',
        'phase_14',
        'accessories',
        'accessory_placements.json'
    )

    roots = []
    currentDirectory = os.path.abspath(os.getcwd())

    while True:
        if currentDirectory not in roots:
            roots.append(currentDirectory)
        parentDirectory = os.path.dirname(currentDirectory)
        if parentDirectory == currentDirectory:
            break
        currentDirectory = parentDirectory

    try:
        currentDirectory = os.path.dirname(os.path.abspath(__file__))
        while True:
            if currentDirectory not in roots:
                roots.append(currentDirectory)
            parentDirectory = os.path.dirname(currentDirectory)
            if parentDirectory == currentDirectory:
                break
            currentDirectory = parentDirectory
    except:
        pass

    placementPath = None
    for root in roots:
        candidate = os.path.join(root, relativePath)
        if os.path.isfile(candidate):
            placementPath = candidate
            break

    if placementPath is None:
        return None

    try:
        placementFile = open(placementPath, 'r')
        try:
            placementData = json.load(placementFile)
        finally:
            placementFile.close()
    except Exception as error:
        print 'Accessory placement override read failed:', error
        return None

    try:
        saved = placementData.get(accessoryType, {}).get(
            str(accessoryId), {}
        ).get(dnaKey)
    except Exception:
        return None

    if not isinstance(saved, dict):
        return None

    pos = saved.get('pos')
    hpr = saved.get('hpr')
    scale = saved.get('scale')

    if pos is None or hpr is None or scale is None:
        return None

    result = (
        tuple(pos),
        tuple(hpr),
        tuple(scale)
    )

    print 'APPLYING ACCESSORY OVERRIDE:', accessoryType, accessoryId, dnaKey, result
    return result

TOON_STATUS_EFFECT_VISUALS = {
    'zapped': {
        'start': 'makeZapped',
        'stop': 'makeUnZapped',
        'passModifier': False,
    },
    'bound': {
        'start': 'makeBound',
        'stop': 'cleanupBound',
        'passModifier': True,
    },

    'liquidated': {
        'start': 'makeLiquidated',
        'stop': 'makeUnLiquidated',
        'passModifier': True,
    },

    'toonupBoost': {
        'start': 'makeToonupGagBoost',
        'stop': 'makeUnToonupGagBoost',
        'passModifier': False,
    },
     'trapBoost': {
        'start': 'makeTrapGagBoost',
        'stop': 'makeUnTrapGagBoost',
        'passModifier': False,
    },
     'lureBoost': {
        'start': 'makeLureGagBoost',
        'stop': 'makeUnLureGagBoost',
        'passModifier': False,
    },
     'throwBoost': {
        'start': 'makeThrowGagBoost',
        'stop': 'makeUnThrowGagBoost',
        'passModifier': False,
    },
     'squirtBoost': {
        'start': 'makeSquirtGagBoost',
        'stop': 'makeUnSquirtGagBoost',
        'passModifier': False,
    },
     'zapBoost': {
        'start': 'makeZapGagBoost',
        'stop': 'makeUnZapGagBoost',
        'passModifier': False,
    },
     'soundBoost': {
        'start': 'makeSoundGagBoost',
        'stop': 'makeUnSoundGagBoost',
        'passModifier': False,
    },
     'dropBoost': {
        'start': 'makeDropGagBoost',
        'stop': 'makeUnDropGagBoost',
        'passModifier': False,
    },
     'gagBoost': {
        'start': 'makeGagBoost',
        'stop': 'makeUnGagBoost',
        'passModifier': False,
    },
    'hydrated': {
        'start': 'makeHydration',
        'stop': 'makeUnHydration',
        'passModifier': True,
    },
    'cooldown': {
        'start': 'makeCooldown',
        'stop': 'makeUnCooldown',
        'passModifier': True,
    },
    'confused': {
        'start': 'makeConfusedStars',
        'stop': 'cleanupConfusedStars',
        'passModifier': True,
    },
    'mandatoryToll': {
        'start': 'setMandatoryToll',
        'stop': 'clearMandatoryToll',
        'passModifier': False,
    },
    'cheer': {
        'start': 'makeCheer',
        'stop': 'makeUnCheer',
        'passModifier': True,
    },
    'damageUp': {
        'start': 'makeDamageUp',
        'stop': 'makeUnDamageUp',
        'passModifier': True,
    },
    'damageUpGov': {
        'start': 'makeDamageUpGovernaught',
        'stop': 'makeUnDamageUpGovernaught',
        'passModifier': True,
    },
    'raisedAnte': {
        'start': 'makeRaisedAnte',
        'stop': 'makeUnRaisedAnte',
        'passModifier': True,
    },
    'damageDown': {
        'start': 'makeDamageDown',
        'stop': 'makeUnDamageDown',
        'passModifier': True,
    },
    'phantomEntry': {
        'start': 'makeDamageDown',
        'stop': 'makeUnDamageDown',
        'passModifier': True,
    },
    'sanctioned': {
        'start': 'makeDamageDown',
        'stop': 'makeUnDamageDown',
        'passModifier': True,
    },
    'breached': {
        'start': 'makeDamageDown',
        'stop': 'makeUnDamageDown',
        'passModifier': True,
    },
    'contingencyMarked': {
        'start': 'makeMarkedWood',
        'stop': 'makeUnMarkedWood',
        'passModifier': True,
    },
    'encore': {
        'start': 'setEncore',
        'stop': 'makeUnEncore',
        'passModifier': False,
    },
    'winded': {
        'start': 'makeWinded',
        'stop': 'makeUnWinded',
        'passModifier': True,
    },
    'burned': {
        'start': 'makeBurned',
        'stop': 'makeUnBurned',
        'passModifier': True,
    },
    'hotShot': {
        'start': 'makeBurned',
        'stop': 'makeUnBurned',
        'passModifier': True,
    },
     'marketMeltdown': {
        'start': 'makeBurned',
        'stop': 'makeUnBurned',
        'passModifier': True,
    },
    'bombed': {
        'start': 'makeBombed',
        'stop': 'makeUnBombed',
        'passModifier': True,
    },
    'snapped': {
        'start': 'makeSnapped',
        'stop': 'makeUnSnapped',
        'passModifier': True,
    },
    'hemmorage': {
        'start': 'makeVulnerable',
        'stop': 'makeUnVulnerable',
        'passModifier': True,
    },

}

def teleportDebug(requestStatus, msg, onlyIfToAv = True):
    if teleportNotify.getDebug():
        teleport = 'teleport'
        if 'how' in requestStatus and requestStatus['how'][:len(teleport)] == teleport:
            if not onlyIfToAv or 'avId' in requestStatus and requestStatus['avId'] > 0:
                teleportNotify.debug(msg)

SLEEP_STRING = TTLocalizer.ToonSleepString
DogDialogueArray = []
CatDialogueArray = []
HorseDialogueArray = []
RabbitDialogueArray = []
MouseDialogueArray = []
DuckDialogueArray = []
MonkeyDialogueArray = []
BearDialogueArray = []
PigDialogueArray = []
DeerDialogueArray = []
BeaverDialogueArray = []
AlligatorDialogueArray = []
ArmadilloDialogueArray = []
BatDialogueArray = []
FoxDialogueArray = []
KangarooDialogueArray = []
KiwiDialogueArray = []
KoalaDialogueArray = []
RaccoonDialogueArray = []
TurkeyDialogueArray = []

LegsAnimDict = {}
TorsoAnimDict = {}
HeadAnimDict = {}
Preloaded = {}
Phase3AnimList = (('neutral', 'neutral'), ('run', 'run'))
Phase3_5AnimList = (('walk', 'walk'),
 ('teleport', 'teleport'),
 ('book', 'book'),
 ('jump', 'jump'),
 ('running-jump', 'running-jump'),
 ('jump-squat', 'jump-zstart'),
 ('jump-idle', 'jump-zhang'),
 ('jump-land', 'jump-zend'),
 ('running-jump-squat', 'leap_zstart'),
 ('running-jump-idle', 'leap_zhang'),
 ('running-jump-land', 'leap_zend'),
 ('pushbutton', 'press-button'),
 ('throw', 'pie-throw'),
 ('victory', 'victory-dance'),
 ('sidestep-left', 'sidestep-left'),
 ('conked', 'conked'),
 ('cringe', 'cringe'),
 ('wave', 'wave'),
 ('shrug', 'shrug'),
 ('angry', 'angry'),
 ('tutorial-neutral', 'tutorial-neutral'),
 ('left-point', 'left-point'),
 ('right-point', 'right-point'),
 ('right-point-start', 'right-point-start'),
 ('give-props', 'give-props'),
 ('give-props-start', 'give-props-start'),
 ('right-hand', 'right-hand'),
 ('right-hand-start', 'right-hand-start'),
 ('duck', 'duck'),
 ('sidestep-right', 'jump-back-right'),
 ('periscope', 'periscope'))
Phase4AnimList = (('sit', 'sit'),
 ('sit-start', 'intoSit'),
 ('swim', 'swim'),
                  ('lynn-sit', 'lynn-sit'),
 ('tug-o-war', 'tug-o-war'),
 ('sad-walk', 'losewalk'),
 ('sad-neutral', 'sad-neutral'),
 ('up', 'up'),
 ('down', 'down'),
 ('left', 'left'),
 ('right', 'right'),
 ('applause', 'applause'),
 ('confused', 'confused'),
 ('bow', 'bow'),
 ('curtsy', 'curtsy'),
 ('bored', 'bored'),
 ('think', 'think'),
 ('battlecast', 'fish'),
 ('cast', 'cast'),
 ('castlong', 'castlong'),
 ('fish-end', 'fishEND'),
 ('fish-neutral', 'fishneutral'),
 ('fish-again', 'fishAGAIN'),
 ('reel', 'reel'),
 ('reel-H', 'reelH'),
 ('reel-neutral', 'reelneutral'),
 ('pole', 'pole'),
 ('pole-neutral', 'poleneutral'),
 ('slip-forward', 'slip-forward'),
 ('slip-backward', 'slip-backward'),
 ('catch-neutral', 'gameneutral'),
 ('catch-run', 'gamerun'),
 ('catch-eatneutral', 'eat_neutral'),
 ('catch-eatnrun', 'eatnrun'),
 ('catch-intro-throw', 'gameThrow'),
 ('swing', 'swing'),
 ('pet-start', 'petin'),
 ('pet-loop', 'petloop'),
 ('pet-end', 'petend'),
 ('scientistJealous', 'scientistJealous'),
 ('scientistEmcee', 'scientistEmcee'),
 ('scientistWork', 'scientistWork'),
 ('scientistGame', 'scientistGame'),
 ('taunt', 'taunt'))
Phase5AnimList = (('water-gun', 'water-gun'),
 ('hold-bottle', 'hold-bottle'),
 ('firehose', 'firehose'),
 ('spit', 'spit'),
 ('tickle', 'tickle'),
 ('smooch', 'smooch'),
 ('happy-dance', 'happy-dance'),
 ('sprinkle-dust', 'sprinkle-dust'),
 ('juggle', 'juggle'),
 ('climb', 'climb'),
 ('sound', 'shout'),
 ('toss', 'toss'),
 ('hold-magnet', 'hold-magnet'),
 ('hypnotize', 'hypnotize'),
 ('struggle', 'struggle'),
 ('lose', 'lose'),
 ('melt', 'melt'))
Phase5_5AnimList = (('takePhone', 'takePhone'),
 ('phoneNeutral', 'phoneNeutral'),
 ('phoneBack', 'phoneBack'),
 ('bank', 'jellybeanJar'),
 ('callPet', 'callPet'),
 ('feedPet', 'feedPet'),
 ('start-dig', 'into_dig'),
 ('loop-dig', 'loop_dig'),
 ('water', 'water'))
Phase6AnimList = (('headdown-putt', 'headdown-putt'),
 ('into-putt', 'into-putt'),
 ('loop-putt', 'loop-putt'),
 ('rotateL-putt', 'rotateL-putt'),
 ('rotateR-putt', 'rotateR-putt'),
 ('swing-putt', 'swing-putt'),
 ('look-putt', 'look-putt'),
 ('lookloop-putt', 'lookloop-putt'),
 ('bad-putt', 'bad-putt'),
 ('badloop-putt', 'badloop-putt'),
 ('good-putt', 'good-putt'))
Phase9AnimList = (('push', 'push'),)
Phase10AnimList = (('leverReach', 'leverReach'), ('leverPull', 'leverPull'), ('leverNeutral', 'leverNeutral'))
Phase12AnimList = ()
LegDict = {'s': '/models/char/tt_a_chr_dgs_shorts_legs_',
           'm': '/models/char/tt_a_chr_dgm_shorts_legs_',
           'l': '/models/char/tt_a_chr_dgl_shorts_legs_'}
TorsoDict = {
    'ss': '/models/char/tt_a_chr_dgs_shorts_torso_',
    'ms': '/models/char/tt_a_chr_dgm_shorts_torso_',
    'ls': '/models/char/tt_a_chr_dgl_shorts_torso_',
    'sd': '/models/char/tt_a_chr_dgs_skirt_torso_',
    'md': '/models/char/tt_a_chr_dgm_skirt_torso_',
    'ld': '/models/char/tt_a_chr_dgl_skirt_torso_'}

def loadModels():
    global Preloaded
    if not Preloaded:
        print 'Preloading avatars...'

        def preload(task):
            for key in LegDict.keys():
                fileRoot = LegDict[key]

                Preloaded[fileRoot+'-1000'] = loader.loadModel('phase_3' + fileRoot + '1000')
                Preloaded[fileRoot+'-500'] = loader.loadModel('phase_3' + fileRoot + '500')
                Preloaded[fileRoot+'-250'] = loader.loadModel('phase_3' + fileRoot + '250')

            for key in TorsoDict.keys():
                fileRoot = TorsoDict[key]

                Preloaded[fileRoot+'-1000'] = loader.loadModel('phase_3' + fileRoot + '1000')

                if len(key) > 1:
                    Preloaded[fileRoot+'-500'] = loader.loadModel('phase_3' + fileRoot + '500')
                    Preloaded[fileRoot+'-250'] = loader.loadModel('phase_3' + fileRoot + '250')

            return task.done

        taskMgr.add(preload, 'preload-avatar')

def loadBasicAnims():
    loadPhaseAnims()

def unloadBasicAnims():
    loadPhaseAnims(0)

def loadTutorialBattleAnims():
    loadPhaseAnims('phase_3.5')

def unloadTutorialBattleAnims():
    loadPhaseAnims('phase_3.5', 0)

def loadMinigameAnims():
    loadPhaseAnims('phase_4')

def unloadMinigameAnims():
    loadPhaseAnims('phase_4', 0)

def loadBattleAnims():
    loadPhaseAnims('phase_5')

def unloadBattleAnims():
    loadPhaseAnims('phase_5', 0)

def loadSellbotHQAnims():
    loadPhaseAnims('phase_9')

def unloadSellbotHQAnims():
    loadPhaseAnims('phase_9', 0)

def loadCashbotHQAnims():
    loadPhaseAnims('phase_10')

def unloadCashbotHQAnims():
    loadPhaseAnims('phase_10', 0)

def loadBossbotHQAnims():
    loadPhaseAnims('phase_12')

def unloadBossbotHQAnims():
    loadPhaseAnims('phase_12', 0)

def loadPhaseAnims(phaseStr = 'phase_3', loadFlag = 1):
    if phaseStr == 'phase_3':
        animList = Phase3AnimList
    elif phaseStr == 'phase_3.5':
        animList = Phase3_5AnimList
    elif phaseStr == 'phase_4':
        animList = Phase4AnimList
    elif phaseStr == 'phase_5':
        animList = Phase5AnimList
    elif phaseStr == 'phase_5.5':
        animList = Phase5_5AnimList
    elif phaseStr == 'phase_6':
        animList = Phase6AnimList
    elif phaseStr == 'phase_9':
        animList = Phase9AnimList
    elif phaseStr == 'phase_10':
        animList = Phase10AnimList
    elif phaseStr == 'phase_12':
        animList = Phase12AnimList
    else:
        self.notify.error('Unknown phase string %s' % phaseStr)
    for key in LegDict.keys():
        for anim in animList:
            if loadFlag:
                pass
            elif anim[0] in LegsAnimDict[key]:
                if base.localAvatar.style.legs == key:
                    base.localAvatar.unloadAnims([anim[0]], 'legs', None)

    for key in TorsoDict.keys():
        for anim in animList:
            if loadFlag:
                pass
            elif anim[0] in TorsoAnimDict[key]:
                if base.localAvatar.style.torso == key:
                    base.localAvatar.unloadAnims([anim[0]], 'torso', None)

    for key in HeadDict.keys():
        if key.find('d') >= 0:
            for anim in animList:
                if loadFlag:
                    pass
                elif anim[0] in HeadAnimDict[key]:
                    if base.localAvatar.style.head == key:
                        base.localAvatar.unloadAnims([anim[0]], 'head', None)

def compileGlobalAnimList():
    phaseList = [Phase3AnimList,
     Phase3_5AnimList,
     Phase4AnimList,
     Phase5AnimList,
     Phase5_5AnimList,
     Phase6AnimList,
     Phase9AnimList,
     Phase10AnimList,
     Phase12AnimList]
    phaseStrList = ['phase_3',
     'phase_3.5',
     'phase_4',
     'phase_5',
     'phase_5.5',
     'phase_6',
     'phase_9',
     'phase_10',
     'phase_12']
    for animList in phaseList:
        phaseStr = phaseStrList[phaseList.index(animList)]
        for key in LegDict.keys():
            LegsAnimDict.setdefault(key, {})
            for anim in animList:
                file = phaseStr + LegDict[key] + anim[1]
                LegsAnimDict[key][anim[0]] = file

        for key in TorsoDict.keys():
            TorsoAnimDict.setdefault(key, {})
            for anim in animList:
                file = phaseStr + TorsoDict[key] + anim[1]
                TorsoAnimDict[key][anim[0]] = file

        for key in HeadDict.keys():
            if key.find('d') >= 0:
                HeadAnimDict.setdefault(key, {})
                for anim in animList:
                    file = phaseStr + HeadDict[key] + anim[1]
                    HeadAnimDict[key][anim[0]] = file


def loadDialog():
    loadPath = 'phase_3.5/audio/dial/'

    DogDialogueFiles = ('AV_dog_short', 'AV_dog_med', 'AV_dog_long', 'AV_dog_question', 'AV_dog_exclaim', 'AV_dog_howl', 'AV_dog_indifferent')
    global DogDialogueArray
    for file in DogDialogueFiles:
        DogDialogueArray.append(base.loader.loadSfx(loadPath + file + '.ogg'))

    catDialogueFiles = ('AV_cat_short', 'AV_cat_med', 'AV_cat_long', 'AV_cat_question', 'AV_cat_exclaim', 'AV_cat_howl', 'AV_cat_indifferent')
    global CatDialogueArray
    for file in catDialogueFiles:
        CatDialogueArray.append(base.loader.loadSfx(loadPath + file + '.ogg'))

    armadilloDialogueFiles = (
    'AV_armadillo_short', 'AV_armadillo_med', 'AV_armadillo_long', 'AV_armadillo_question', 'AV_armadillo_exclaim',
    'AV_armadillo_howl', 'AV_armadillo_indifferent')
    global ArmadilloDialogueArray
    for file in armadilloDialogueFiles:
        ArmadilloDialogueArray.append(base.loader.loadSfx(loadPath + file + '.ogg'))

    beaverDialogueFiles = (
    'AV_beaver_short', 'AV_beaver_med', 'AV_beaver_long', 'AV_beaver_question', 'AV_beaver_exclaim', 'AV_beaver_howl', 'AV_beaver_indifferent')
    global BeaverDialogueArray
    for file in beaverDialogueFiles:
        BeaverDialogueArray.append(base.loader.loadSfx(loadPath + file + '.ogg'))

    horseDialogueFiles = ('AV_horse_short', 'AV_horse_med', 'AV_horse_long', 'AV_horse_question', 'AV_horse_exclaim', 'AV_horse_howl', 'AV_horse_indifferent')
    global HorseDialogueArray
    for file in horseDialogueFiles:
        HorseDialogueArray.append(base.loader.loadSfx(loadPath + file + '.ogg'))

    kangarooDialogueFiles = (
        'AV_kangaroo_short', 'AV_kangaroo_med', 'AV_kangaroo_long', 'AV_kangaroo_question', 'AV_kangaroo_exclaim',
        'AV_kangaroo_howl', 'AV_kangaroo_indifferent')
    global KangarooDialogueArray
    for file in kangarooDialogueFiles:
        KangarooDialogueArray.append(base.loader.loadSfx(loadPath + file + '.ogg'))

    kiwiDialogueFiles = (
        'AV_kiwi_short', 'AV_kiwi_med', 'AV_kiwi_long', 'AV_kiwi_question', 'AV_kiwi_exclaim', 'AV_kiwi_howl', 'AV_kiwi_indifferent')
    global KiwiDialogueArray
    for file in kiwiDialogueFiles:
        KiwiDialogueArray.append(base.loader.loadSfx(loadPath + file + '.ogg'))

    koalaDialogueFiles = (
        'AV_koala_short', 'AV_koala_med', 'AV_koala_long', 'AV_koala_question', 'AV_koala_exclaim', 'AV_koala_howl', 'AV_koala_indifferent')
    global KoalaDialogueArray
    for file in koalaDialogueFiles:
        KoalaDialogueArray.append(base.loader.loadSfx(loadPath + file + '.ogg'))

    turkeyDialogueFiles = (
        'AV_turkey_short', 'AV_turkey_med', 'AV_turkey_long', 'AV_turkey_question', 'AV_turkey_exclaim',
        'AV_turkey_howl', 'AV_turkey_indifferent')
    global TurkeyDialogueArray
    for file in turkeyDialogueFiles:
        TurkeyDialogueArray.append(base.loader.loadSfx(loadPath + file + '.ogg'))

    rabbitDialogueFiles = ('AV_rabbit_short', 'AV_rabbit_med', 'AV_rabbit_long', 'AV_rabbit_question', 'AV_rabbit_exclaim', 'AV_rabbit_howl', 'AV_rabbit_indifferent')
    global RabbitDialogueArray
    for file in rabbitDialogueFiles:
        RabbitDialogueArray.append(base.loader.loadSfx(loadPath + file + '.ogg'))

    mouseDialogueFiles = ('AV_mouse_short', 'AV_mouse_med', 'AV_mouse_long', 'AV_mouse_question', 'AV_mouse_exclaim', 'AV_mouse_howl', 'AV_mouse_indifferent')
    global MouseDialogueArray
    for file in mouseDialogueFiles:
        MouseDialogueArray.append(base.loader.loadSfx(loadPath + file + '.ogg'))

    duckDialogueFiles = ('AV_duck_short', 'AV_duck_med', 'AV_duck_long', 'AV_duck_question', 'AV_duck_exclaim', 'AV_duck_howl', 'AV_duck_indifferent')
    global DuckDialogueArray
    for file in duckDialogueFiles:
        DuckDialogueArray.append(base.loader.loadSfx(loadPath + file + '.ogg'))

    monkeyDialogueFiles = ('AV_monkey_short', 'AV_monkey_med', 'AV_monkey_long', 'AV_monkey_question', 'AV_monkey_exclaim', 'AV_monkey_howl', 'AV_monkey_indifferent')
    global MonkeyDialogueArray
    for file in monkeyDialogueFiles:
        MonkeyDialogueArray.append(base.loader.loadSfx(loadPath + file + '.ogg'))

    bearDialogueFiles = ('AV_bear_short', 'AV_bear_med', 'AV_bear_long', 'AV_bear_question', 'AV_bear_exclaim', 'AV_bear_howl', 'AV_bear_indifferent')
    global BearDialogueArray
    for file in bearDialogueFiles:
        BearDialogueArray.append(base.loader.loadSfx(loadPath + file + '.ogg'))

    pigDialogueFiles = ('AV_pig_short', 'AV_pig_med', 'AV_pig_long', 'AV_pig_question', 'AV_pig_exclaim', 'AV_pig_howl', 'AV_pig_indifferent')
    global PigDialogueArray
    for file in pigDialogueFiles:
        PigDialogueArray.append(base.loader.loadSfx(loadPath + file + '.ogg'))

    deerDialogueFiles = ('AV_deer_short', 'AV_deer_med', 'AV_deer_long', 'AV_deer_question', 'AV_deer_exclaim', 'AV_deer_howl', 'AV_deer_indifferent')
    global DeerDialogueArray
    for file in deerDialogueFiles:
        DeerDialogueArray.append(base.loader.loadSfx(loadPath + file + '.ogg'))
		
    beaverDialogFiles = ('AV_beaver_short', 'AV_beaver_med', 'AV_beaver_long', 'AV_beaver_question', 'AV_beaver_exclaim', 'AV_beaver_howl', 'AV_beaver_indifferent')
    global BeaverDialogueArray
    for file in beaverDialogFiles:
        BeaverDialogueArray.append(base.loader.loadSfx(loadPath + file + '.ogg'))
		
    gatorDialogFiles = ('AV_gator_short', 'AV_gator_med', 'AV_gator_long', 'AV_gator_question', 'AV_gator_exclaim', 'AV_gator_howl', 'AV_gator_indifferent')
    global AlligatorDialogueArray
    for file in gatorDialogFiles:
        AlligatorDialogueArray.append(base.loader.loadSfx(loadPath + file + '.ogg'))
		
    foxDialogFiles = ('AV_fox_short', 'AV_fox_med', 'AV_fox_long', 'AV_fox_question', 'AV_fox_exclaim', 'AV_fox_howl', 'AV_fox_indifferent')
    global FoxDialogueArray
    for file in foxDialogFiles:
        FoxDialogueArray.append(base.loader.loadSfx(loadPath + file + '.ogg'))

    batDialogFiles = ('AV_bat_short', 'AV_bat_med', 'AV_bat_long', 'AV_bat_question', 'AV_bat_exclaim', 'AV_bat_howl', 'AV_bat_indifferent')
    global BatDialogueArray
    for file in batDialogFiles:
        BatDialogueArray.append(base.loader.loadSfx(loadPath + file + '.ogg'))
		
    raccoonDialogFiles = ('AV_raccoon_short', 'AV_raccoon_med', 'AV_raccoon_long', 'AV_raccoon_question', 'AV_raccoon_exclaim', 'AV_raccoon_howl', 'AV_raccoon_indifferent')
    global RaccoonDialogueArray
    for file in raccoonDialogFiles:
        RaccoonDialogueArray.append(base.loader.loadSfx(loadPath + file + '.ogg'))

def unloadDialog():
    global CatDialogueArray
    global PigDialogueArray
    global BearDialogueArray
    global DuckDialogueArray
    global RabbitDialogueArray
    global MouseDialogueArray
    global DogDialogueArray
    global HorseDialogueArray
    global MonkeyDialogueArray
    global DeerDialogueArray
    global BeaverDialogueArray
    global AlligatorDialogueArray
    global BatDialogueArray
    global ArmadilloDialogueArray
    global DeerDialogueArray
    global FoxDialogueArray
    global KangarooDialogueArray
    global KiwiDialogueArray
    global KoalaDialogueArray
    global RaccoonDialogueArray
    global TurkeyDialogueArray
    DogDialogueArray = []
    CatDialogueArray = []
    HorseDialogueArray = []
    RabbitDialogueArray = []
    MouseDialogueArray = []
    DuckDialogueArray = []
    MonkeyDialogueArray = []
    BearDialogueArray = []
    PigDialogueArray = []
    DeerDialogueArray = []
    BeaverDialogueArray = []
    AlligatorDialogueArray = []
    ArmadilloDialogueArray = []
    KangarooDialogueArray = []
    KiwiDialogueArray = []
    KoalaDialogueArray = []
    FoxDialogueArray = []
    BatDialogueArray = []
    RaccoonDialogueArray = []
    TurkeyDialogueArray = []

class Toon(Avatar.Avatar, ToonHead):
    notify = DirectNotifyGlobal.directNotify.newCategory('Toon')
    afkTimeout = base.config.GetInt('afk-timeout', 600)

    def __init__(self):
        try:
            self.Toon_initialized
            return
        except:
            self.Toon_initialized = 1

        Avatar.Avatar.__init__(self)
        ToonHead.__init__(self)
        self.forwardSpeed = 0.0
        self.rotateSpeed = 0.0
        self.strafeSpeed = 0.0
        self.avatarType = 'toon'
        self.motion = Motion.Motion(self)
        self.standWalkRunReverse = None
        self.playingAnim = None
        self.soundTeleport = None
        self.cheesyEffect = ToontownGlobals.CENormal
        self.effectTrack = None
        self.emoteTrack = None
        self.emote = None
        self.stunTrack = None
        self.__bookActors = []
        self.__holeActors = []
        self.holeClipPath = None
        self.wake = None
        self.lastWakeTime = 0
        self.forceJumpIdle = False
        self.gagBoost = 0
        self.gagBoostRounds = 0
        self.gagBoostNumber = 0
        self.liquidated = 0
        self.liquidatedRounds = 0
        self.energized = 0
        self.energizedRounds = 0
        self.driedOut = 0
        self.driedOutRounds = 0
        self.encore = 0
        self.encoreNumber = 0
        self.winded = 0
        self.windedNumber = 0
        self.encoreRounds = 0
        self.windedRounds = 0
        self.damageDown = 0
        self.damageUpNumberGovernaught = 0
        self.damageDownRounds = 0
        self.damageDownNumber = 0
        self.damageUp = 0
        self.governaughtDamageUp = 0
        self.raisedAnte = 0
        self.raisedAnteNumber = 0
        self.damageUpRounds = 0
        self.damageUpNumber = 0
        self.confused = 0
        self.confusedRounds = 0
        self.collectCalled = 0
        self.collectCalledRounds = 0
        self.mandatoryToll = 0
        self.mandatoryTollNumber = 0
        self.hidden = 0
        self.hiddenRounds = 0
        self.markedWood = 0
        self.markedWoodRounds = 0
        self.markedWoodNumber  = 0
        self.damageOvertime = 0
        self.damageOvertimeRounds = 0
        self.isVulnerable = 0
        self.isGagBan = 0
        self.cooldown = 0
        self.cooldownRounds = 0
        self.bombedRounds = 0
        self.hydrated = 0
        self.hydrationRounds = 0
        self.vulnerability = 0
        self.vulnerabilityRounds = 0
        self.bombed = 0
        self.isBombed = 0
        self.noDodge = 0
        self.noDodgeRounds = 0
        self.groupDamageDown = 0
        self.groupDamageDownRounds = 0
        self.isSnapped = 0
        self.frozen = 0
        self.frozenRounds = 0
        self.isBurned = 0
        self.isViralSensation = 0
        self.viralSensationRounds = 0
        self.viralSensationBoost = 0
        self.isDancePartner = 0
        self.burnedRounds = 0
        self.contentSync = 0
        self.isZapped = 0
        self.zappedRounds = 0
        self.snapped = 0
        self.snappedRounds = 0
        self.inkDrain = 0
        self.inkDrainNumber = 0
        self.inkDrainRounds = 0
        self.toonupArrowAuraTrack = None
        self.trapArrowAuraTrack = None
        self.lureArrowAuraTrack = None
        self.throwArrowAuraTrack = None
        self.squirtArrowAuraTrack = None
        self.zapArrowAuraTrack = None
        self.soundArrowAuraTrack = None
        self.dropArrowAuraTrack = None
        # Toon-Up
        self.toonupGagBoost = 0
        self.toonupGagBoostRounds = 0
        self.toonupGagBoostNumber = 0

        # Trap
        self.trapGagBoost = 0
        self.trapGagBoostRounds = 0
        self.trapGagBoostNumber = 0

        # Lure
        self.lureGagBoost = 0
        self.lureGagBoostRounds = 0
        self.lureGagBoostNumber = 0

        # Throw
        self.throwGagBoost = 0
        self.throwGagBoostRounds = 0
        self.throwGagBoostNumber = 0

        # Squirt
        self.squirtGagBoost = 0
        self.squirtGagBoostRounds = 0
        self.squirtGagBoostNumber = 0

        # Zap
        self.zapGagBoost = 0
        self.zapGagBoostRounds = 0
        self.zapGagBoostNumber = 0

        # Sound
        self.soundGagBoost = 0
        self.soundGagBoostRounds = 0
        self.soundGagBoostNumber = 0

        # Drop
        self.dropGagBoost = 0
        self.dropGagBoostRounds = 0
        self.dropGagBoostNumber = 0
        self.headParts = []
        self.animatedHeadParts = []
        self.numPies = 0
        self.pieType = 0
        self.pieThrowType = ToontownGlobals.PieThrowArc
        self.pieModel = None
        self.__pieModelType = None
        self.pieScale = 1.0
        self.hatNodes = []
        self._highRollerHatActors = []
        self._highRollerDuckOrbits = []
        self.glassesNodes = []
        self.backpackNodes = []
        self.shoesNodes = []
        self.hat = (0, 0, 0)
        self.glasses = (0, 0, 0)
        self.backpack = (0, 0, 0)
        self.shoes = (0, 0, 0)
        self.oldStyle = None
        self.oldDNA = None
        self.oldEffect = None
        self.oldHat = None
        self.oldShoes = None
        self.isStunned = 0
        self.isDisguised = 0
        self.cheer = 0
        self.cheerRounds = 0
        self.cogHead = 0
        self.cogLevels = [] 
        self.uberType = 0
        self.startingPg = 0
        self.choiceAlpha = 2
        self.choiceBeta = 3
        self.toonStatusEffects = {}
        self.defaultColorScale = None
        self.jar = None
        self.setBlend(frameBlend = base.wantSmoothAnims)
        self.setLODAnimation(base.lodMaxRange, base.lodMinRange, base.lodDelayFactor)
        self.setTag('pieCode', str(ToontownGlobals.PieCodeToon))
        self.setFont(ToontownGlobals.getToonFont())
        self.soundChatBubble = base.loader.loadSfx('phase_3/audio/sfx/GUI_balloon_popup.ogg')
        self.swimRunSfx = base.loader.loadSfx('phase_4/audio/sfx/AV_footstep_runloop_water.ogg')
        self.swimRunLooping = False
        self.animFSM = ClassicFSM('Toon', [State('off', self.enterOff, self.exitOff),
         State('neutral', self.enterNeutral, self.exitNeutral),
         State('victory', self.enterVictory, self.exitVictory),
         State('Happy', self.enterHappy, self.exitHappy),
         State('Sad', self.enterSad, self.exitSad),
         State('Catching', self.enterCatching, self.exitCatching),
         State('CatchEating', self.enterCatchEating, self.exitCatchEating),
         State('Sleep', self.enterSleep, self.exitSleep),
         State('walk', self.enterWalk, self.exitWalk),
         State('jumpSquat', self.enterJumpSquat, self.exitJumpSquat),
         State('jump', self.enterJump, self.exitJump),
         State('jumpAirborne', self.enterJumpAirborne, self.exitJumpAirborne),
         State('jumpLand', self.enterJumpLand, self.exitJumpLand),
         State('run', self.enterRun, self.exitRun),
         State('swim', self.enterSwim, self.exitSwim),
         State('swimhold', self.enterSwimHold, self.exitSwimHold),
         State('dive', self.enterDive, self.exitDive),
         State('cringe', self.enterCringe, self.exitCringe),
         State('OpenBook', self.enterOpenBook, self.exitOpenBook, ['ReadBook', 'CloseBook']),
         State('ReadBook', self.enterReadBook, self.exitReadBook),
         State('CloseBook', self.enterCloseBook, self.exitCloseBook),
         State('TeleportOut', self.enterTeleportOut, self.exitTeleportOut),
         State('Died', self.enterDied, self.exitDied),
         State('PlaygroundDied', self.enterPlaygroundDied, self.exitPlaygroundDied),
         State('TeleportedOut', self.enterTeleportedOut, self.exitTeleportedOut),
         State('TeleportIn', self.enterTeleportIn, self.exitTeleportIn),
         State('Emote', self.enterEmote, self.exitEmote),
         State('SitStart', self.enterSitStart, self.exitSitStart),
         State('Sit', self.enterSit, self.exitSit),
         State('Push', self.enterPush, self.exitPush),
         State('Squish', self.enterSquish, self.exitSquish),
         State('FallDown', self.enterFallDown, self.exitFallDown),
         State('GolfPuttLoop', self.enterGolfPuttLoop, self.exitGolfPuttLoop),
         State('GolfRotateLeft', self.enterGolfRotateLeft, self.exitGolfRotateLeft),
         State('GolfRotateRight', self.enterGolfRotateRight, self.exitGolfRotateRight),
         State('GolfPuttSwing', self.enterGolfPuttSwing, self.exitGolfPuttSwing),
         State('GolfGoodPutt', self.enterGolfGoodPutt, self.exitGolfGoodPutt),
         State('GolfBadPutt', self.enterGolfBadPutt, self.exitGolfBadPutt),
         State('Flattened', self.enterFlattened, self.exitFlattened),
         State('CogThiefRunning', self.enterCogThiefRunning, self.exitCogThiefRunning),
         State('ScientistJealous', self.enterScientistJealous, self.exitScientistJealous),
         State('ScientistEmcee', self.enterScientistEmcee, self.exitScientistEmcee),
         State('ScientistWork', self.enterScientistWork, self.exitScientistWork),
         State('ScientistLessWork', self.enterScientistLessWork, self.exitScientistLessWork),
         State('ScientistPlay', self.enterScientistPlay, self.enterScientistPlay)], 'off', 'off')
        animStateList = self.animFSM.getStates()
        self.animFSM.enterInitialState()

    def setToonStatusEffect(self, name, modifier=1, turns=None, mode='setBoth'):
        # Dried Out + Hydrated becomes Energized instead.
        if name == 'driedOut' and self.hasToonStatusEffect('hydrated'):
            self.clearToonStatusEffect('driedOut')

            self.setToonStatusEffect(
                'energized',
                modifier=50,
                turns=turns,
                mode=mode
            )
            return

        if turns == 0:
            self.clearToonStatusEffect(name)
            return

        if name not in self.toonStatusEffects:
            self.toonStatusEffects[name] = {
                'modifier': modifier,
                'turns': turns
            }
        else:
            effect = self.toonStatusEffects[name]

            if mode == 'setBoth':
                effect['modifier'] = modifier
                effect['turns'] = turns

            elif mode == 'refreshTurns':
                if effect['turns'] is None or turns is None:
                    effect['turns'] = None
                else:
                    effect['turns'] += turns

            elif mode == 'refreshModifier':
                effect['modifier'] += modifier

            elif mode == 'refreshBoth':
                effect['modifier'] += modifier

                if effect['turns'] is None or turns is None:
                    effect['turns'] = None
                else:
                    effect['turns'] += turns

            elif mode == 'keepHighest':
                effect['modifier'] = max(effect['modifier'], modifier)

                if effect['turns'] is None or turns is None:
                    effect['turns'] = None
                else:
                    effect['turns'] = turns

        self.__startToonStatusVisual(
            name,
            self.toonStatusEffects[name]['modifier']
        )


    def hasToonStatusEffect(self, name):
        return name in self.toonStatusEffects


    def getToonStatusModifier(self, name):
        if name not in self.toonStatusEffects:
            return 0

        return self.toonStatusEffects[name].get('modifier', 0)


    def getToonStatusTurns(self, name):
        if name not in self.toonStatusEffects:
            return 0

        return self.toonStatusEffects[name].get('turns')


    def getToonStatusEffects(self):
        return self.toonStatusEffects


    def decrementToonStatusEffects(self):
        for name in list(self.toonStatusEffects.keys()):
            effect = self.toonStatusEffects.get(name)

            if effect is None:
                continue

            turns = effect.get('turns')

            # None means permanent.
            if turns is None:
                continue

            if turns > 0:
                effect['turns'] -= 1

            if effect['turns'] <= 0:
                self.clearToonStatusEffect(name)


    def clearToonStatusEffect(self, name):
        if name in self.toonStatusEffects:
            del self.toonStatusEffects[name]

        self.__stopToonStatusVisual(name)


    def __startToonStatusVisual(self, name, modifier):
        info = TOON_STATUS_EFFECT_VISUALS.get(name)

        if not info:
            return

        startFuncName = info.get('start')

        if not startFuncName:
            return

        startFunc = getattr(self, startFuncName, None)

        if not startFunc:
            return

        if info.get('passModifier', False):
            startFunc()
        else:
            startFunc(modifier)


    def __stopToonStatusVisual(self, name):
        info = TOON_STATUS_EFFECT_VISUALS.get(name)

        if not info:
            return

        stopFuncName = info.get('stop')

        if not stopFuncName:
            return

        stopFunc = getattr(self, stopFuncName, None)

        if stopFunc:
            stopFunc()


    def clearAllToonStatusEffects(self):
        for name in list(self.toonStatusEffects.keys()):
            self.clearToonStatusEffect(name)

    def makeDamageOvertime(self):
        self.damageOvertime = 1

    def makeUnDamageOvertime(self):
        self.damageOvertime = 0

    def addDamageOvertimeRounds(self, num):
        self.damageOvertimeRounds = num

    def getDamageOvertimeRounds(self):
        return self.damageOvertimeRounds

    def cleanupWoodAura(self):
        if getattr(self, 'woodAuraTrack', None):
            try:
                self.woodAuraTrack.pause()
                self.woodAuraTrack.finish()
            except:
                pass
            self.woodAuraTrack = None

        if getattr(self, 'woodAuraNode', None):
            try:
                if not self.woodAuraNode.isEmpty():
                    self.woodAuraNode.removeNode()
            except:
                pass
            self.woodAuraNode = None

    def cleanupShockAura(self):
        if getattr(self, 'shockAuraTrack', None):
            try:
                self.shockAuraTrack.pause()
                self.shockAuraTrack.finish()
            except:
                pass
            self.shockAuraTrack = None

        if getattr(self, 'shockAuraNode', None):
            try:
                if not self.shockAuraNode.isEmpty():
                    self.shockAuraNode.removeNode()
            except:
                pass
            self.shockAuraNode = None

    def makeShockDamageBurstTrack(self, duration=1.0, sparkCount=28):
        import random

        burstNode = self.attachNewNode('shockDamageBurstNode')

        toonHeight = 4.0
        try:
            toonHeight = self.getHeight()
        except:
            if hasattr(self, 'height'):
                toonHeight = self.height

        sparks = []
        burstTrack = Parallel()

        def resetBurstSpark(spark):
            if not spark or spark.isEmpty():
                return

            x = random.uniform(-1.6, 1.6)
            y = random.uniform(-1.3, 1.3)
            z = random.uniform(0.4, max(1.0, toonHeight + 0.8))

            spark.show()
            spark.setPos(x, y, z)
            spark.setHpr(
                random.uniform(0, 360),
                random.uniform(-25, 25),
                random.uniform(0, 360)
            )
            spark.setScale(random.uniform(1.4, 2.8))
            spark.setAlphaScale(1)
            spark.setColor(1, 0.988, 0.408, 1.0)

        for i in xrange(sparkCount):
            spark = loader.loadModel(
                'phase_3.5/models/gui/matching_game_gui'
            ).find('**/minnieArrow').copyTo(burstNode)

            texture = loader.loadTexture('phase_3.5/maps/phase_3.5_palette_2tlla_12.png')
            spark.setTexture(texture, 1)
            spark.setBillboardPointEye()
            spark.setTransparency(1)
            spark.setTwoSided(True)
            spark.setLightOff(1)
            spark.setDepthWrite(False)
            spark.hide()
            spark.setR(270)

            oneSparkTrack = Sequence(
                Wait(random.uniform(0.0, duration * 0.45)),
                Func(resetBurstSpark, spark),

                Parallel(
                    LerpHprInterval(
                        spark,
                        random.uniform(0.18, 0.35),
                        Vec3(0, 0, random.choice((90, -90, 180))),
                        startHpr=Vec3(0, 0, 270)
                    ),

                    Sequence(
                        LerpScaleInterval(
                            spark,
                            random.uniform(0.15, 0.3),
                            random.uniform(2.5, 4.0)
                        ),
                        LerpScaleInterval(
                            spark,
                            random.uniform(0.15, 0.3),
                            random.uniform(0.8, 1.4)
                        )
                    ),

                    LerpFunctionInterval(
                        spark.setAlphaScale,
                        random.uniform(0.25, 0.45),
                        fromData=1,
                        toData=0
                    )
                ),

                Func(spark.hide)
            )

            burstTrack.append(oneSparkTrack)
            sparks.append(spark)

        return Sequence(
            burstTrack,
            Func(burstNode.removeNode)
        )


    def makeLoopingShockAura(self):
        import random

        self.cleanupShockAura()

        self.shockAuraNode = self.attachNewNode('shockAuraNode')

        toonHeight = 4.0
        try:
            toonHeight = self.getHeight()
        except:
            if hasattr(self, 'height'):
                toonHeight = self.height

        sparks = []
        partTrack = Parallel()

        def resetSpark(spark):
            if not spark or spark.isEmpty():
                return

            x = random.uniform(-1.2, 1.2)
            y = random.uniform(-1.0, 1.0)
            z = random.uniform(0.5, max(1.0, toonHeight + 0.5))

            spark.show()
            spark.setPos(x, y, z)
            spark.setHpr(
                random.uniform(0, 360),
                random.uniform(-20, 20),
                random.uniform(0, 360)
            )
            spark.setScale(random.uniform(0.6, 1.6))
            spark.setAlphaScale(1)
            spark.setColor(1, 0.988, 0.408, 1.0)

        for i in xrange(12):
            spark = loader.loadModel(
                'phase_3.5/models/gui/matching_game_gui'
            ).find('**/minnieArrow').copyTo(self.shockAuraNode)

            texture = loader.loadTexture('phase_3.5/maps/phase_3.5_palette_2tlla_12.png')
            spark.setTexture(texture, 1)
            spark.setBillboardPointEye()
            spark.setTransparency(1)
            spark.setTwoSided(True)
            spark.setLightOff(1)
            spark.setDepthWrite(False)
            spark.hide()
            spark.setR(270)

            oneSparkTrack = Sequence(
                Wait(random.uniform(0.0, 0.5) + i * 0.05),
                Func(resetSpark, spark),

                Parallel(
                    LerpHprInterval(
                        spark,
                        0.35,
                        Vec3(0, 0, 90),
                        startHpr=Vec3(0, 0, 270)
                    ),

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
    
    def makeLoopingWoodAura(self):
        import random

        self.cleanupWoodAura()

        self.woodAuraNode = self.attachNewNode('woodAuraNode')

        toonHeight = 4.0
        try:
            toonHeight = self.getHeight()
        except:
            if hasattr(self, 'height'):
                toonHeight = self.height

        sparks = []
        partTrack = Parallel()

        def resetSpark(spark):
            if not spark or spark.isEmpty():
                return

            x = random.uniform(-1.2, 1.2)
            y = random.uniform(-1.0, 1.0)
            z = random.uniform(0.5, max(1.0, toonHeight + 0.5))

            spark.show()
            spark.setPos(x, y, z)
            spark.setHpr(
                random.uniform(0, 360),
                random.uniform(-20, 20),
                random.uniform(0, 360)
            )
            spark.setScale(random.uniform(0.6, 1.6))
            spark.setAlphaScale(1)
            spark.setColor(1, 0.988, 0.408, 1.0)

        for i in xrange(12):
            spark = loader.loadModel(
                'phase_3.5/models/gui/matching_game_gui'
            ).find('**/minnieArrow').copyTo(self.woodAuraNode)

            texture = loader.loadTexture('phase_12/maps/woodchips.png')
            spark.setTexture(texture, 1)
            spark.setBillboardPointEye()
            spark.setTransparency(1)
            spark.setTwoSided(True)
            spark.setLightOff(1)
            spark.setDepthWrite(False)
            spark.hide()
            spark.setR(270)

            oneSparkTrack = Sequence(
                Wait(random.uniform(0.0, 0.5) + i * 0.05),
                Func(resetSpark, spark),

                Parallel(
                    LerpHprInterval(
                        spark,
                        0.35,
                        Vec3(0, 0, 90),
                        startHpr=Vec3(0, 0, 270)
                    ),

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


    def makeZapped(self, num=1):
        if not hasattr(self, 'isZapped'):
            self.isZapped = 0

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


    def addZappedRounds(self, num):
        self.zappedRounds = num


    def getZappedRounds(self):
        if not hasattr(self, 'zappedRounds'):
            self.zappedRounds = 0

        return self.zappedRounds

    def makeLiquidated(self):
        self.liquidated = 1
        self.cleanupSoaked()

        # if num <= 0 or self.currHP <= 0:
        #     return


        self.liquidEffect = BattleParticles.createParticleEffect(file='wet2')

        self.liquidEffect.reparentTo(self)
        self.liquidEffect.setPos(0, 0, self.height)

        self.liquidEffect.start(parent=self, renderParent=self)

    def makeUnLiquidated(self):
        self.liquidated = 0
        self.cleanupSoaked()

    def addLiquidatedRounds(self, num):
        self.liquidatedRounds = num

    def getLiquidatedRounds(self):
        return self.liquidatedRounds

    def makeGroupDamageDown(self):
        self.groupDamageDown = 1

    def makeUnGroupDamageDown(self):
        self.groupDamageDown = 0

    def addGroupDamageDownRounds(self, num):
        self.groupDamageDownRounds = num

    def getGroupDamageDownRounds(self):
        return self.groupDamageDownRounds
    
    def startArrowAuraTrack(self, trackName, makerFunc):
        self.cleanupArrowAuraTrack(trackName)

        if self.hp > 0:
            track = makerFunc()
            setattr(self, trackName, track)
            track.loop()

    def makeToonupGagBoost(self, level):
        self.toonupGagBoost = level
        self.startArrowAuraTrack(
            'toonupArrowAuraTrack',
            lambda: self.makeLoopingArrowAuraColored(color=(0.776, 0, 1, 1))
        )

    def makeUnToonupGagBoost(self):
        self.toonupGagBoost = 0
        self.cleanupArrowAuraTrack('toonupArrowAuraTrack')

    def addToonupGagBoostRounds(self, num):
        self.toonupGagBoostRounds = num

    def getToonupGagBoostRounds(self):
        return self.toonupGagBoostRounds

    def setToonupGagBoost(self, num):
        self.toonupGagBoostNumber = num

    def getToonupGagBoost(self):
        return self.toonupGagBoostNumber

    def makeTrapGagBoost(self, level):
        self.trapGagBoost = level
        self.startArrowAuraTrack(
            'trapArrowAuraTrack',
            lambda: self.makeLoopingArrowAuraColored(color=(1, 0, 0, 1))
        )

    def makeUnTrapGagBoost(self):
        self.trapGagBoost = 0
        self.cleanupArrowAuraTrack('trapArrowAuraTrack')

    def addTrapGagBoostRounds(self, num):
        self.trapGagBoostRounds = num

    def getTrapGagBoostRounds(self):
        return self.trapGagBoostRounds

    def setTrapGagBoost(self, num):
        self.trapGagBoostNumber = num

    def getTrapGagBoost(self):
        return self.trapGagBoostNumber

    def makeLureGagBoost(self, level):
        self.lureGagBoost = level
        self.startArrowAuraTrack(
            'lureArrowAuraTrack',
            lambda: self.makeLoopingArrowAuraColored(color=(0, 1, 0.047, 1))
        )

    def makeUnLureGagBoost(self):
        self.lureGagBoost = 0
        self.cleanupArrowAuraTrack('lureArrowAuraTrack')

    def addLureGagBoostRounds(self, num):
        self.lureGagBoostRounds = num

    def getLureGagBoostRounds(self):
        return self.lureGagBoostRounds

    def setLureGagBoost(self, num):
        self.lureGagBoostNumber = num

    def getLureGagBoost(self):
        return self.lureGagBoostNumber
    
    def makeThrowGagBoost(self, level):
        self.throwGagBoost = level
        self.startArrowAuraTrack(
            'throwArrowAuraTrack',
            lambda: self.makeLoopingArrowAuraColored(color=(1, 0.651, 0, 1))
        )

    def makeUnThrowGagBoost(self):
        self.throwGagBoost = 0
        self.cleanupArrowAuraTrack('throwArrowAuraTrack')

    def addThrowGagBoostRounds(self, num):
        self.throwGagBoostRounds = num

    def getThrowGagBoostRounds(self):
        return self.throwGagBoostRounds

    def setThrowGagBoost(self, num):
        self.throwGagBoostNumber = num

    def getThrowGagBoost(self):
        return self.throwGagBoostNumber

    def makeSquirtGagBoost(self, level):
        self.squirtGagBoost = level
        self.startArrowAuraTrack(
            'squirtArrowAuraTrack',
            lambda: self.makeLoopingArrowAuraColored(color=(0.988, 0, 1, 1))
        )

    def makeUnSquirtGagBoost(self):
        self.squirtGagBoost = 0
        self.cleanupArrowAuraTrack('squirtArrowAuraTrack')

    def addSquirtGagBoostRounds(self, num):
        self.squirtGagBoostRounds = num

    def getSquirtGagBoostRounds(self):
        return self.squirtGagBoostRounds

    def setSquirtGagBoost(self, num):
        self.squirtGagBoostNumber = num

    def getSquirtGagBoost(self):
        return self.squirtGagBoostNumber

    def makeZapGagBoost(self, level):
        self.zapGagBoost = level
        self.startArrowAuraTrack(
            'zapArrowAuraTrack',
            lambda: self.makeLoopingArrowAuraColored(color=(1, 0.996, 0, 1))
        )

    def makeUnZapGagBoost(self):
        self.zapGagBoost = 0
        self.cleanupArrowAuraTrack('zapArrowAuraTrack')

    def addZapGagBoostRounds(self, num):
        self.zapGagBoostRounds = num

    def getZapGagBoostRounds(self):
        return self.zapGagBoostRounds

    def setZapGagBoost(self, num):
        self.zapGagBoostNumber = num

    def getZapGagBoost(self):
        return self.zapGagBoostNumber

    def makeSoundGagBoost(self, level):
        self.soundGagBoost = level
        self.startArrowAuraTrack(
            'soundArrowAuraTrack',
            lambda: self.makeLoopingArrowAuraColored(color=(0.161, 0, 1, 1))
        )

    def makeUnSoundGagBoost(self):
        self.soundGagBoost = 0
        self.cleanupArrowAuraTrack('soundArrowAuraTrack')

    def addSoundGagBoostRounds(self, num):
        self.soundGagBoostRounds = num

    def getSoundGagBoostRounds(self):
        return self.soundGagBoostRounds

    def setSoundGagBoost(self, num):
        self.soundGagBoostNumber = num

    def getSoundGagBoost(self):
        return self.soundGagBoostNumber

    def makeDropGagBoost(self, level):
        self.dropGagBoost = level
        self.startArrowAuraTrack(
            'dropArrowAuraTrack',
            lambda: self.makeLoopingArrowAuraColored(color=(0, 0.933, 1, 1))
        )

    def makeUnDropGagBoost(self):
        self.dropGagBoost = 0
        self.cleanupArrowAuraTrack('dropArrowAuraTrack')

    def addDropGagBoostRounds(self, num):
        self.dropGagBoostRounds = num

    def getDropGagBoostRounds(self):
        return self.dropGagBoostRounds

    def setDropGagBoost(self, num):
        self.dropGagBoostNumber = num

    def getDropGagBoost(self):
        return self.dropGagBoostNumber

    def makeGagBoost(self, level):
        self.gagBoost = level
        self.startArrowAuraTrack('arrowAuraTrack', self.makeLoopingArrowAura)

    def makeUnGagBoost(self):
        self.gagBoost = 0
        self.cleanupArrowAuraTrack('arrowAuraTrack')

    def addGagBoostRounds(self, num):
        self.gagBoostRounds = num

    def getGagBoostRounds(self):
        return self.gagBoostRounds

    def setGagBoost(self, num):
        self.gagBoostNumber = num

    def getGagBoost(self):
        return self.gagBoostNumber

    def cleanupArrowAuraTrack(self, trackName):
        track = getattr(self, trackName, None)
        if not track:
            return

        arrows = []
        arrows.extend(getattr(track, 'arrows', []))
        arrows.extend(getattr(track, 'fallingArrowProps', []))

        auraNode = getattr(track, 'auraNode', None)

        try:
            track.pause()
        except:
            pass

        setattr(self, trackName, None)

        try:
            if auraNode and not auraNode.isEmpty():
                auraNode.removeNode()
        except:
            pass

        for arrow in arrows:
            try:
                if arrow and not arrow.isEmpty():
                    arrow.removeNode()
            except:
                pass

    def makeDriedOut(self):
        if self.hydrated > 0:
            self.energized = 1
        else:
            self.driedOut = 1

    def makeUnDriedOut(self):
        self.driedOut = 0

    def addDriedOutRounds(self, num):
        if self.hydrated > 0:
            self.energizedRounds = num
        else:
            self.driedOutRounds = num

    def getDriedOutRounds(self):
        return self.driedOutRounds
    
    def makeEnergized(self):
        self.energized = 1

    def makeUnEnergized(self):
        self.energized = 0

    def addEnergizedRounds(self, num):
        self.energizedRounds = num

    def getEnergizedRounds(self):
        return self.energizedRounds
    
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

    def makeHydration(self):
        self.hydrated = 1
        self.cleanupSoaked()

        # if num <= 0 or self.currHP <= 0:
        #     return


        self.liquidEffect = BattleParticles.createParticleEffect(file='wet2')

        self.liquidEffect.reparentTo(self)
        self.liquidEffect.setPos(0, 0, self.height)

        self.liquidEffect.start(parent=self, renderParent=self)

    def makeUnHydration(self):
        self.hydrated = 0
        self.cleanupSoaked()

    def addHydrationRounds(self, num):
        self.hydrationRounds = num

    def getHydrationRounds(self):
        return self.hydrationRounds

    def makeCooldown(self):
        self.cooldown = 1
        if self.hp > 0:
            if hasattr(self, "cooldownTrack") and self.cooldownTrack:
                self.cooldownTrack.pause()
                if self.cooldownEffect:
                    self.cooldownEffect.disable()
                    if hasattr(self.cooldownEffect, 'renderParent'):
                        self.cooldownEffect.cleanup()
            self.cooldownEffect = BattleParticles.createParticleEffect(file='uniteCooldown')

            self.cooldownEffect.reparentTo(self)
            self.cooldownEffect.setPos(0, 0, self.height)
            #self.cooldownEffect.setHpr(180, 0, 0)

            self.cooldownTrack = Sequence(ParticleInterval(self.cooldownEffect, self, duration=2, softStopT=1)
            )

            self.cooldownEffect.start()

    def makeUnCooldown(self):
        self.cooldown = 0
        if self.hp > 0:
            if hasattr(self, 'cooldownEffect') and self.cooldownEffect:
                self.cooldownEffect.softStop()
                self.cooldownEffect.cleanup()
                self.cooldownEffect = None

    def addCooldownRounds(self, num):
        self.cooldownRounds = num

    def getCooldownRounds(self):
        return self.cooldownRounds

    def makeMarkedWood(self):
        self.markedWood = 1
        if getattr(self, 'isDead', False) or self.isEmpty():
            return

        if getattr(self, 'shockAuraTrack', None):
            return

        self.woodAuraTrack = self.makeLoopingWoodAura()
        self.woodAuraTrack.loop()

    def makeUnMarkedWood(self):
        self.markedWood = 0
        self.markedWoodNumber = 0
        self.cleanupWoodAura()

    def setMarkedWood(self, num):
        self.markedWoodNumber = num

    def getMarkedWood(self):
        return self.markedWoodNumber

    def addMarkedWoodRounds(self, num):
        self.markedWoodRounds = num

    def getMarkedWoodRounds(self):
        return self.markedWoodRounds

    def makeInkDrain(self):
        self.inkDrain = 1

    def makeUnInkDrain(self):
        self.inkDrain = 0
        self.inkDrainNumber = 0

    def setInkDrain(self, num):
        self.inkDrainNumber = num

    def getInkDrain(self):
        return self.inkDrainNumber

    def addInkDrainRounds(self, num):
        self.inkDrainRounds = num

    def getInkDrainRounds(self):
        return self.inkDrainRounds

    def makeHidden(self):
        self.hidden = 1

    def makeUnHidden(self):
        self.hidden = 0

    def addHiddenRounds(self, num):
        self.hiddenRounds = num

    def getHiddenRounds(self):
        return self.hiddenRounds
    
    def makeFrozen(self):
        self.frozen = 1

    def makeUnFrozen(self):
        self.frozen = 0

    def addFrozenRounds(self, num):
        self.frozenRounds = num

    def getFrozenRounds(self):
        return self.frozenRounds
    
    def makeViralSensation(self):
        self.isViralSensation = 1

    def makeUnViralSensation(self):
        self.isViralSensation = 0

    def addViralSensationRounds(self, num):
        self.viralSensationRounds = num

    def getViralSensationRounds(self):
        return self.viralSensationRounds

    def setViralSensationBoost(self, num):
        self.viralSensationBoost = num

    def getViralSensationBoost(self):
        return self.viralSensationBoost
    
    def makeDancePartner(self):
        self.isDancePartner = 1

    def makeUnDancePartner(self):
        self.isDancePartner = 0

    def makeCollectCalled(self):
        self.collectCalled = 1

    def makeUnCollectCalled(self):
        self.collectCalled = 0

    def addCollectCallRounds(self, num):
        self.collectCalledRounds = num

    def getCollectCallRounds(self):
        return self.collectCalledRounds

    def makeNoDodge(self):
        self.noDodge = 1

    def makeUnNoDodge(self):
        self.noDodge = 0

    def addNoDodgeRounds(self, num):
        self.noDodgeRounds = num

    def getNoDodgeRounds(self):
        return self.noDodgeRounds

    def makeConfusedStars(self):
        # Clean up any existing stars first
        self.confused = 1
        if self.hp > 0:
            self.cleanupConfusedStars()

            self.confusedStars = globalPropPool.getProp('stun')
            self.confusedStars.reparentTo(self)
            self.confusedStars.setPosHprScale(0, 0, self.height - .5, 0, 0, 0, 1, 1, 1)
            self.confusedStars.setBlend(frameBlend=base.wantSmoothAnims)
            self.confusedStars.adjustAllPriorities(100)

            # Loop the stun animation if the prop is an actor
            try:
                self.confusedStars.loop('stun')
            except:
                pass

    def cleanupConfusedStars(self):
        self.confused = 0
        if hasattr(self, 'confusedStars') and self.confusedStars:
            try:
                self.confusedStars.stop()
            except:
                pass

            try:
                if not self.confusedStars.isEmpty():
                    MovieUtil.removeProp(self.confusedStars)
            except:
                pass

            self.confusedStars = None

    def makeConfused(self):
        self.confused = 1
        self.makeConfusedStars()

    def makeUnConfused(self):
        self.confused = 0
        self.cleanupConfusedStars()

    def addConfusedRounds(self, num):
        self.confusedRounds = num

    def getConfusedRounds(self):
        return self.confusedRounds

    def makeMandatoryToll(self):
        self.mandatoryToll = 1

    def makeUnMandatoryToll(self):
        self.mandatoryToll = 0
        self.clearMandatoryToll()

    def clearMandatoryToll(self):
        if self.hp > 0:
            if hasattr(self, "tollTrack") and self.tollTrack:
                self.tollTrack.pause()
                self.tollTrack.finish()
                self.tollTrack = None

            if hasattr(self, "tollProps") and self.tollProps:
                for bill in self.tollProps:
                    if bill and not bill.isEmpty():
                        MovieUtil.removeProp(bill)
                self.tollProps = []

            if hasattr(self, "tollPivot") and self.tollPivot and not self.tollPivot.isEmpty():
                self.tollPivot.removeNode()
                self.tollPivot = None

        self.mandatoryToll = 0

    def setMandatoryToll(self, num):
        self.mandatoryTollNumber = num
        if self.hp > 0:
            if hasattr(self, "tollTrack") and self.tollTrack:
                self.tollTrack.pause()
                self.tollTrack.finish()
                self.tollTrack = None

            if hasattr(self, "tollPivot") and self.tollPivot and not self.tollPivot.isEmpty():
                self.tollPivot.removeNode()
                self.tollPivot = None

            from math import pi, cos, sin

            totalBills = max(1, (self.mandatoryTollNumber / 8))
            radius = 1.5
            height = self.height - 1.25

            self.tollProps = []

            # Shared pivot
            self.tollPivot = self.attachNewNode("tollPivot")
            self.tollPivot.setZ(height)

            tollIntervals = []

            for i in range(totalBills):
                bill = globalPropPool.getProp(random.choice(('10dollar', '1dollar', '5dollar', '50dollar')))
                bill.setTwoSided(True)
                bill.setScale(.75)
                bill.reparentTo(self.tollPivot)

                angle = (2 * pi / totalBills) * i
                bill.setPos(cos(angle) * radius,
                            sin(angle) * radius,
                            0)

                bill.lookAt(self.tollPivot)
                bill.setP(270)

            # Orbit pivot a little slower so the individual spins stand out
            orbit = LerpHprInterval(
                self.tollPivot,
                3.0,
                VBase3(360, 0, 0),
                startHpr=VBase3(0, 0, 0)
            )

            self.tollTrack = Parallel(
                orbit,
                *tollIntervals
            )

            self.tollTrack.loop()

    def getMandatoryToll(self):
        return self.mandatoryTollNumber

    def makeCheerHands(self):
        if self.hp > 0:
            from panda3d.core import Vec4

            if hasattr(self, 'cheerHandsTrack') and self.cheerHandsTrack:
                self.cheerHandsTrack.pause()
                self.cheerHandsTrack.finish()
                self.cheerHandsTrack = None

            gloveColor = self.style.getGloveColor()
            green = Vec4(0, 1, 0, 1)

            glovePieces = self.getPieces(('torso', '*hands*'))
            handTracks = []

            for piece in glovePieces:
                pieceTrack = Sequence(
                    LerpColorScaleInterval(
                        piece,
                        1.0,
                        green,
                        startColorScale=gloveColor
                    ),
                    LerpColorScaleInterval(
                        piece,
                        1.0,
                        gloveColor,
                        startColorScale=green
                    ),
                    Wait(1.0)
                )
                handTracks.append(pieceTrack)

            self.cheerHandsTrack = Parallel(*handTracks)
            self.cheerHandsTrack.loop()

    def cleanupCheerHands(self):
        if hasattr(self, 'cheerHandsTrack') and self.cheerHandsTrack:
            self.cheerHandsTrack.pause()
            self.cheerHandsTrack.finish()
            self.cheerHandsTrack = None

        try:
            gloveColor = self.style.getGloveColor()
            glovePieces = self.getPieces(('torso', '*hands*'))
            for piece in glovePieces:
                piece.clearColorScale()
                piece.setColorScale(gloveColor)
        except:
            pass

    def makeCheer(self):
        if self.hp > 0:
            self.cheer = 1
            self.cleanupCheerHands()
            if hasattr(self, "cheerTrack") and self.cheerTrack:
                self.cheerTrack.pause()
                if self.cheerEffect:
                    self.cheerEffect.disable()
                    if hasattr(self.cheerEffect, 'renderParent'):
                        self.cheerEffect.cleanup()
            effectColor = Vec4(0, 1, 0.137, 1.00)
            self.cheerEffect = BattleParticles.createParticleEffect(file='pixieRise')
            self.cheerEffect.setColor(effectColor)

            self.cheerEffect.reparentTo(self)
            self.cheerEffect.setPos(0, 0, 0)
            self.makeCheerHands()
            #self.cooldownEffect.setHpr(180, 0, 0)

            self.cheerTrack = Sequence(ParticleInterval(self.cheerEffect, self, duration=4, softStopT=2))

            self.cheerTrack.loop()

    def makeUnCheer(self):
        self.cheer = 0
        if self.hp > 0:
            self.cleanupCheerHands()
            if hasattr(self, "cheerTrack") and self.cheerTrack:
                self.cheerTrack.pause()
                if self.cheerEffect:
                    self.cheerEffect.disable()
                    if hasattr(self.cheerEffect, 'renderParent'):
                        self.cheerEffect.cleanup()

    def addCheerRounds(self, num):
        self.cheerRounds = num

    def getCheerRounds(self):
        return self.cheerRounds

    def makeDamageUp(self):
        self.damageUp = 1
        self.startArrowAuraTrack('arrowAuraTrackUp', self.makeLoopingArrowAura)

    def makeUnDamageUp(self):
        self.damageUp = 0
        self.damageUpNumber = 0
        self.cleanupArrowAuraTrack('arrowAuraTrackUp')

    def makeDamageUpGovernaught(self):
        self.governaughtDamageUp = 1
        self.startArrowAuraTrack('arrowAuraTrackGov', self.makeLoopingArrowAura)

    def makeUnDamageUpGovernaught(self):
        self.governaughtDamageUp = 0
        self.cleanupArrowAuraTrack('arrowAuraTrackGov')

    def makeRaisedAnte(self):
        self.raisedAnte = 1
        self.startArrowAuraTrack('arrowAuraTrackAnte', self.makeLoopingArrowAuraAnte)

    def makeUnRaisedAnte(self):
        self.raisedAnte = 0
        self.cleanupArrowAuraTrack('arrowAuraTrackAnte')

    def setRaisedAnte(self, num):
        self.raisedAnteNumber = num

    def getRaisedAnte(self):
        return self.raisedAnteNumber

    def addDamageUpRounds(self, num):
        self.damageUpRounds = num

    def getDamageUpRounds(self):
        return self.damageUpRounds

    def makeDamageDown(self):
        self.damageDown = 1
        self.startArrowAuraTrack('arrowAuraTrackDown', self.makeLoopingArrowAuraDown)

    def makeUnDamageDown(self):
        self.damageDown = 0
        self.damageDownNumber = 0
        self.cleanupArrowAuraTrack('arrowAuraTrackDown')

    def addDamageDownRounds(self, num):
        self.damageDownRounds = num

    def getDamageDownRounds(self):
        return self.damageDownRounds

    def setDamageDown(self, num):
        self.damageDownNumber = num

    def getDamageDown(self):
        return self.damageDownNumber

    def setDamageUp(self, num):
        self.damageUpNumber = num

    def getDamageUp(self):
        return self.damageUpNumber

    def setDamageUpGovernaught(self, num):
        self.damageUpNumberGovernaught = num

    def getDamageUpGovernaught(self):
        return self.damageUpNumberGovernaught

    def makeEncore(self):
        self.encore = 1

    def makeUnEncore(self):
        self.encore = 0
        if self.hp > 0:
            if hasattr(self, "knifeTrack") and self.knifeTrack:
                self.knifeTrack.pause()
                self.knifeTrack.finish()
                self.knifeTrack = None

            if hasattr(self, "knifePivot") and self.knifePivot and not self.knifePivot.isEmpty():
                self.knifePivot.removeNode()
                self.knifePivot = None

    def cleanupAllAuraTracks(self):
        for trackName in (
            'toonupArrowAuraTrack',
            'trapArrowAuraTrack',
            'lureArrowAuraTrack',
            'throwArrowAuraTrack',
            'squirtArrowAuraTrack',
            'zapArrowAuraTrack',
            'soundArrowAuraTrack',
            'dropArrowAuraTrack',
            'arrowAuraTrack',
            'arrowAuraTrackUp',
            'arrowAuraTrackGov',
            'arrowAuraTrackAnte',
            'arrowAuraTrackDown'
        ):
            self.cleanupArrowAuraTrack(trackName)

        self.cleanupConfusedStars()
        self.cleanupCheerHands()

    def makeLoopingArrowAuraDown(self):
        import random
        import math

        fallingArrowProps = []
        partTrack = Parallel()

        auraNode = self.attachNewNode('fallingArrowAuraNode')

        def resetFallingArrow(fallingArrow):
            if fallingArrow.isEmpty():
                return

            angle = random.random() * 2.0 * math.pi
            x = 1.0 * math.cos(angle)
            y = 1.0 * math.sin(angle)

            fallingArrow.show()
            fallingArrow.setColor(1, 0.984, 0, 1)
            fallingArrow.setPos(x, y, 3)
            fallingArrow.setAlphaScale(1)

        for i in xrange(30):
            fallingArrow = loader.loadModel(
                'phase_3.5/models/gui/matching_game_gui'
            ).find('**/minnieArrow').copyTo(auraNode)

            fallingArrow.setScale(1.5)
            fallingArrow.setBillboardPointEye()
            fallingArrow.setR(90)
            fallingArrow.setTransparency(1)
            fallingArrow.hide()

            oneArrowTrack = Sequence(
                Wait(0.9 + i * 0.25),
                Func(resetFallingArrow, fallingArrow),
                Parallel(
                    LerpFunctionInterval(
                        fallingArrow.setZ,
                        1.0,
                        fromData=3,
                        toData=0,
                        blendType='easeIn'
                    ),
                    Sequence(
                        Wait(0.3),
                        LerpFunctionInterval(
                            fallingArrow.setAlphaScale,
                            0.25,
                            fromData=1,
                            toData=0
                        )
                    )
                ),
                Func(fallingArrow.hide)
            )

            partTrack.append(oneArrowTrack)
            fallingArrowProps.append(fallingArrow)

        loopTrack = Sequence(partTrack)
        loopTrack.fallingArrowProps = fallingArrowProps
        loopTrack.auraNode = auraNode
        return loopTrack

    def makeLoopingArrowAuraColored(self, color=(0, 0.918, 1, 1)):
        import random
        import math

        arrows = []
        partTrack = Parallel()

        auraNode = self.attachNewNode('arrowAuraNode')

        def resetArrow(arrow):
            if arrow.isEmpty():
                return

            angle = random.random() * 2.0 * math.pi
            x = 1.0 * math.cos(angle)
            y = 1.0 * math.sin(angle)

            arrow.show()
            arrow.setColor(*color)
            arrow.setPos(x, y, 0)
            arrow.setAlphaScale(1)

        for i in xrange(30):
            arrow = loader.loadModel(
                'phase_3.5/models/gui/matching_game_gui'
            ).find('**/minnieArrow').copyTo(auraNode)

            arrow.setScale(1.5)
            arrow.setBillboardPointEye()
            arrow.setR(270)
            arrow.setTransparency(1)
            arrow.hide()

            oneArrowTrack = Sequence(
                Wait(0.9 + i * 0.25),
                Func(resetArrow, arrow),
                Parallel(
                    LerpFunctionInterval(
                        arrow.setZ,
                        1.0,
                        fromData=0,
                        toData=3,
                        blendType='easeOut'
                    ),
                    Sequence(
                        Wait(0.5),
                        LerpFunctionInterval(
                            arrow.setAlphaScale,
                            0.25,
                            fromData=1,
                            toData=0
                        )
                    )
                ),
                Func(arrow.hide)
            )

            partTrack.append(oneArrowTrack)
            arrows.append(arrow)

        loopTrack = Sequence(partTrack)
        loopTrack.arrows = arrows
        loopTrack.auraNode = auraNode
        return loopTrack

    def makeLoopingArrowAura(self):
        return self.makeLoopingArrowAuraColored(color=(0, 0.918, 1, 1))

    def makeLoopingArrowAuraAnte(self):
        import random
        import math

        arrows = []
        partTrack = Parallel()

        def resetArrow(arrow):
            angle = random.random() * 2.0 * math.pi

            x = 1.0 * math.cos(angle)
            y = 1.0 * math.sin(angle)

            arrow.setColor(random.random(), random.random(), random.random(), 1)
            arrow.setPos(x, y, 0)
            arrow.setAlphaScale(1)

        for i in xrange(30):
            arrow = loader.loadModel(
                'phase_3.5/models/gui/matching_game_gui'
            ).find('**/minnieArrow').copyTo(hidden)

            arrow.setScale(1.5)
            arrow.setBillboardPointEye()
            arrow.setR(270)
            arrow.setTransparency(1)

            oneArrowTrack = Sequence(
                Wait(0.9 + i * 0.25),

                Func(arrow.reparentTo, self),
                Func(resetArrow, arrow),

                Parallel(
                    LerpFunctionInterval(
                        arrow.setZ,
                        1.0,
                        fromData=0,
                        toData=3,
                        blendType='easeOut'
                    ),

                    Sequence(
                        Wait(0.5),
                        LerpFunctionInterval(
                            arrow.setAlphaScale,
                            0.25,
                            fromData=1,
                            toData=0
                        )
                    )
                ),

                Func(arrow.reparentTo, hidden)
            )

            partTrack.append(oneArrowTrack)
            arrows.append(arrow)

        loopTrack = Sequence(
            partTrack
        )

        loopTrack.arrows = arrows
        return loopTrack
    
    def makeContentSync(self, num):
        self.contentSync = num

    def makeBurned(self):
        self.isBurned = 1
        if self.hp > 0:
            if hasattr(self, "flameTrack") and self.flameTrack:
                self.flameTrack.pause()
                if self.flameEffect:
                    self.flameEffect.disable()
                    if hasattr(self.flameEffect, 'renderParent'):
                        self.flameEffect.cleanup()
            self.flameEffect = BattleParticles.createParticleEffect('FiredFlame3')
            BattleParticles.setEffectTexture(self.flameEffect, 'fire')

            self.flameEffect.reparentTo(self)
            self.flameEffect.setPos(0, 0, 0)

            self.flameTrack = Sequence(ParticleInterval(self.flameEffect, self, duration=5)
            )
            self.flameTrack.loop()

    def makeUnBurned(self):
        self.isBurned = 0
        if self.hp > 0:
            if hasattr(self, "flameTrack") and self.flameTrack:
                self.flameTrack.pause()
                if self.flameEffect:
                    self.flameEffect.disable()
                    if hasattr(self.flameEffect, 'renderParent'):
                        self.flameEffect.cleanup()

    def addBurnedRounds(self, num):
        self.burnedRounds = num

    def getBurnedRounds(self):
        return self.burnedRounds

    def setEncore(self, num):
        self.encoreNumber = num
        if self.hp > 0:
            if hasattr(self, "knifeTrack") and self.knifeTrack:
                self.knifeTrack.pause()
                self.knifeTrack.finish()
                self.knifeTrack = None

            if hasattr(self, "knifePivot") and self.knifePivot and not self.knifePivot.isEmpty():
                self.knifePivot.removeNode()
                self.knifePivot = None

            from math import pi, cos, sin
            from panda3d.core import VBase3

            totalKnives = max(1, int(self.encoreNumber / 10))
            radius = 2.0
            height = self.height - 2

            parent = self.getParent()
            self.knifePivot = parent.attachNewNode("knifePivot")
            self.knifePivot.setPos(self.getPos(parent))
            self.knifePivot.setZ(self.knifePivot.getZ() + height)

            self.encoreKnives = []
            knifeIntervals = []

            for i in range(totalKnives):
                # holder = orbit point
                knifeHolder = self.knifePivot.attachNewNode("knifeHolder-%d" % i)

                angle = (2 * pi / totalKnives) * i
                knifeHolder.setPos(cos(angle) * radius,
                                sin(angle) * radius,
                                0)

                # actual model
                knife = globalPropPool.getProp('bugle')
                knife.setTwoSided(True)
                knife.setScale(0.2)
                knife.reparentTo(knifeHolder)

                # --- center the model on its own bounds ---
                minb, maxb = knife.getTightBounds()
                center = (minb + maxb) * 0.5
                knife.setPos(-center)

                # optional extra push outward if it still feels too close
                knife.setY(knife, -0.5)

                # face outward from the circle
                knifeHolder.lookAt(knifeHolder.getPos() * 2)
                knifeHolder.setP(0)
                knifeHolder.setH(180)
                if i % 2 == 1:
                    knife.setH(knife.getH() - 180)
                    knife.setY(1)

                self.encoreKnives.append((knifeHolder, knife))

            orbit = LerpHprInterval(
                self.knifePivot,
                4.0,
                VBase3(-360, 0, 0),
                startHpr=VBase3(0, 0, 0)
            )

            self.knifeTrack = orbit
            self.knifeTrack.loop()

    def getEncore(self):
        return self.encoreNumber

    def setWinded(self, num):
        self.windedNumber = num

    def getWinded(self):
        return self.windedNumber

    def addEncoreRounds(self, num):
        self.encoreRounds = num

    def getEncoreRounds(self):
        return self.encoreRounds

    def makeWinded(self):
        self.winded = 1
        self.encore = 0
        if self.hp > 0:
            if hasattr(self, "knifeTrack") and self.knifeTrack:
                self.knifeTrack.pause()
                self.knifeTrack.finish()
                self.knifeTrack = None

            if hasattr(self, "knifePivot") and self.knifePivot and not self.knifePivot.isEmpty():
                self.knifePivot.removeNode()
                self.knifePivot = None

    def makeUnWinded(self):
        self.winded = 0

    def addWindedRounds(self, num):
        self.windedRounds = num

    def getWindedRounds(self):
        return self.windedRounds

    def makeBombed(self):
        if self.hp > 0:
            # ---- CLEANUP ----
            self.cleanupBombed()

            from math import pi, cos, sin

            totalBombs = 1
            radius = 1.5
            height = self.height - 2

            self.bombProps = []

            # Shared pivot (orbit axis)
            self.bombPivot = self.attachNewNode("bombPivot")
            self.bombPivot.setZ(height)

            bombIntervals = []

            for i in range(totalBombs):
                bomb = globalPropPool.getProp('tnt')
                bomb.setScale(0.5)

                tip = bomb.find('**/joint_attachEmitter')
                sparks = BattleParticles.createParticleEffect(file='tnt')
                bomb.sparksEffect = sparks
                sparks.start(tip)

                bomb.reparentTo(self.bombPivot)

                angle = (2 * pi / totalBombs) * i
                bomb.setPos(cos(angle) * radius,
                            sin(angle) * radius,
                            0)

                bomb.lookAt(self.bombPivot)
                bomb.setP(90)
                bomb.setR(90)

                self.bombProps.append(bomb)

            orbit = LerpHprInterval(
                self.bombPivot,
                4.0,
                VBase3(360, 0, 0),
                startHpr=VBase3(0, 0, 0)
            )

            self.bombTrack = Parallel(
                orbit,
                *bombIntervals
            )

            self.bombTrack.loop()
            self.isBombed = 1

    def cleanupBombed(self):
        if hasattr(self, "bombTrack") and self.bombTrack:
            try:
                self.bombTrack.pause()
            except:
                pass
            try:
                self.bombTrack.finish()
            except:
                pass
            self.bombTrack = None

        if hasattr(self, "bombProps") and self.bombProps:
            for bomb in self.bombProps:
                if bomb:
                    if hasattr(bomb, "sparksEffect") and bomb.sparksEffect:
                        effect = bomb.sparksEffect
                        bomb.sparksEffect = None

                        try:
                            effect.disable()
                        except:
                            pass

                        try:
                            if hasattr(effect, "renderParent"):
                                effect.cleanup()
                        except:
                            pass

                        try:
                            effect.detachNode()
                        except:
                            pass

                    try:
                        if not bomb.isEmpty():
                            MovieUtil.removeProp(bomb)
                    except:
                        pass

            self.bombProps = []

        if hasattr(self, "bombPivot") and self.bombPivot and not self.bombPivot.isEmpty():
            self.bombPivot.removeNode()
            self.bombPivot = None

        self.isBombed = 0

    def makeUnBombed(self):
        self.isBombed = 0
        self.bombed = 0
        if self.hp > 0:
            self.cleanupBombed()

    def addBombedRounds(self, num):
        self.bombedRounds = num

    def getBombedRounds(self):
        return self.bombedRounds

    def setBombed(self, num):
        self.bombed = num

    def getBombed(self):
        return self.bombed

    def makeVulnerable(self):
        self.isVulnerable = 1
        if self.hp > 0:
            self.makeTeethProp()

    def makeUnVulnerable(self):
        self.isVulnerable = 0
        self.vulnerability = 0
        if self.hp > 0:
            self.cleanupTeeth()

    def makeGagBan(self):
        self.isGagBan = 1

    def makeUnGagBan(self):
        self.isGagBan = 0

    def addVulnerabilityRounds(self, num):
        self.vulnerabilityRounds = num

    def getVulnerabilityRounds(self):
        return self.vulnerabilityRounds

    def setVulnerability(self, num):
        self.vulnerability = num

    def getVulnerability(self):
        return self.vulnerability

    def makeBound(self):
        # Clean up any existing teeth first
        self.cleanupBound()

        self.tube = globalPropPool.getProp('redtape-tube')
        self.tube.setColorScale(0.25, 0.25, 1.0, 1.0)
        self.tube.reparentTo(self.rightHand)
        self.tube.setPos(0.3, 0.04, 0)
        self.tube.setHpr(0, 100, 90)
        self.tube.setScale(0.3, 0.3, 0.09)

    def cleanupBound(self):
        if hasattr(self, 'tube') and self.tube:

            try:
                if not self.tube.isEmpty():
                    MovieUtil.removeProp(self.tube)
            except:
                pass

            self.tube = None

    def makeTeethProp(self):
        # Clean up any existing teeth first
        self.cleanupTeeth()

        self.teeth = globalPropPool.getProp('teeth')
        self.teeth.reparentTo(self.leftHand)

        self.teeth.setScale(5)
        self.teeth.setH(90)
        self.teeth.setR(180)
        self.teeth.setZ(.375)

    def cleanupTeeth(self):
        if hasattr(self, 'teeth') and self.teeth:

            try:
                if not self.teeth.isEmpty():
                    MovieUtil.removeProp(self.teeth)
            except:
                pass

            self.teeth = None

    def makeSnapProp(self):
        # Clean up any existing stars first
        self.cleanupSnap()

        self.snap = globalPropPool.getProp('litigator-teeth')
        self.snap.reparentTo(self.leftHand)
        self.snap.setScale(5)
        self.snap.setH(90)
        self.snap.setR(180)
        self.snap.setZ(.375)

    def cleanupSnap(self):
        if hasattr(self, 'snap') and self.snap:

            try:
                if not self.snap.isEmpty():
                    MovieUtil.removeProp(self.snap)
            except:
                pass

            self.snap = None

    def makeSnapped(self):
        self.isSnapped = 1
        if self.hp > 0:
            self.makeSnapProp()

    def makeUnSnapped(self):
        self.isSnapped = 0
        self.snapped = 0
        if self.hp > 0:
            self.cleanupSnap()

    def setSnapped(self, num):
        self.snapped = num

    def getSnapped(self):
        return self.snapped

    def addSnappedRounds(self, num):
        self.snappedRounds = num

    def getSnappedRounds(self):
        return self.snappedRounds

    def stopAnimations(self):
        if hasattr(self, 'animFSM'):
            if not self.animFSM.isInternalStateInFlux():
                self.animFSM.request('off')
            else:
                self.notify.warning('animFSM in flux, state=%s, not requesting off' % self.animFSM.getCurrentState().getName())
        else:
            self.notify.warning('animFSM has been deleted')
        if self.effectTrack != None:
            self.effectTrack.finish()
            self.effectTrack = None
        if self.emoteTrack != None:
            self.emoteTrack.finish()
            self.emoteTrack = None
        if self.stunTrack != None:
            self.stunTrack.finish()
            self.stunTrack = None
        if self.wake:
            self.wake.stop()
            self.wake.destroy()
            self.wake = None
        
        self.cleanupPieModel()

    def delete(self):
        try:
            self.Toon_deleted
            return
        except:
            self.Toon_deleted = 1
            
        self.stopAnimations()
        self._cleanupHighRollerDuckOrbit()
        self.rightHands = None
        self.rightHand = None
        self.leftHands = None
        self.leftHand = None
        self.headParts = None
        self.torsoParts = None
        self.hipsParts = None
        self.legsParts = None
        self.oldStyle = None
        self.oldDNA = None
        self.oldEffect = None
        self.oldHat = None
        self.oldShoes = None
        del self.animFSM
        for bookActor in self.__bookActors:
            bookActor.cleanup()

        del self.__bookActors
        for holeActor in self.__holeActors:
            holeActor.cleanup()

        del self.__holeActors
        self.soundTeleport = None
        self.motion.delete()
        self.motion = None
        Avatar.Avatar.cleanup(self)
        ToonHead.cleanup(self)
        Avatar.Avatar.delete(self)
        ToonHead.delete(self)

    def updateToonDNA(self, newDNA, fForce = 0):
        self.style.gender = newDNA.getGender()
        oldDNA = self.style
        if fForce or newDNA.head != oldDNA.head:
            self.swapToonHead(newDNA.head)
        
        if fForce or newDNA.torso != oldDNA.torso:
            self.swapToonTorso(newDNA.torso, genClothes=0)
            self.loop('neutral')
        
        if fForce or newDNA.legs != oldDNA.legs:
            self.swapToonLegs(newDNA.legs)
        
        self.swapToonColor(newDNA)
        self.__swapToonClothes(newDNA)

    def setDNAString(self, dnaString):
        newDNA = ToonDNA.ToonDNA()
        newDNA.makeFromNetString(dnaString)
        if len(newDNA.torso) < 2:
            self.sendLogSuspiciousEvent('nakedToonDNA %s was requested' % newDNA.torso)
            newDNA.torso = newDNA.torso + 's'
        self.setDNA(newDNA)
        self.setBlend(frameBlend = base.wantSmoothAnims)
        self.setLODAnimation(base.lodMaxRange, base.lodMinRange, base.lodDelayFactor)

    def setDNA(self, dna):
        if hasattr(self, 'isDisguised'):
            if self.isDisguised:
                return
        
        if self.style:
            self.updateToonDNA(dna)
        else:
            self.style = dna
            self.generateToon()
            self.initializeDropShadow()
            self.initializeNametag3d()

    def parentToonParts(self):
        if self.hasLOD():
            for lodName in self.getLODNames():
                if base.config.GetBool('want-new-anims', 1):
                    if not self.getPart('torso', lodName).find('**/def_head').isEmpty():
                        self.attach('head', 'torso', 'def_head', lodName)
                    else:
                        self.attach('head', 'torso', 'joint_head', lodName)
                else:
                    self.attach('head', 'torso', 'joint_head', lodName)
                self.attach('torso', 'legs', 'joint_hips', lodName)

        else:
            self.attach('head', 'torso', 'joint_head')
            self.attach('torso', 'legs', 'joint_hips')

    def unparentToonParts(self):
        if self.hasLOD():
            for lodName in self.getLODNames():
                self.getPart('head', lodName).reparentTo(self.getLOD(lodName))
                self.getPart('torso', lodName).reparentTo(self.getLOD(lodName))
                self.getPart('legs', lodName).reparentTo(self.getLOD(lodName))

        else:
            self.getPart('head').reparentTo(self.getGeomNode())
            self.getPart('torso').reparentTo(self.getGeomNode())
            self.getPart('legs').reparentTo(self.getGeomNode())

    def setLODs(self):
        self.setLODNode()
        levelOneIn = base.config.GetInt('lod1-in', 20)
        levelOneOut = base.config.GetInt('lod1-out', 0)
        levelTwoIn = base.config.GetInt('lod2-in', 80)
        levelTwoOut = base.config.GetInt('lod2-out', 20)
        levelThreeIn = base.config.GetInt('lod3-in', 280)
        levelThreeOut = base.config.GetInt('lod3-out', 80)
        self.addLOD(1000, levelOneIn, levelOneOut)
        self.addLOD(500, levelTwoIn, levelTwoOut)
        self.addLOD(250, levelThreeIn, levelThreeOut)

    def generateToon(self):
        self.setLODs()
        self.generateToonLegs()
        self.generateToonHead()
        self.generateToonTorso()
        self.generateToonColor()
        self.parentToonParts()
        self.rescaleToon()
        self.resetHeight()
        self.setupToonNodes()
        self.setBlend(frameBlend = base.wantSmoothAnims)
        self.setLODAnimation(base.lodMaxRange, base.lodMinRange, base.lodDelayFactor)

    def setupToonNodes(self):
        rightHand = NodePath('rightHand')
        self.rightHand = None
        self.rightHands = []
        leftHand = NodePath('leftHand')
        self.leftHands = []
        self.leftHand = None
        for lodName in self.getLODNames():
            hand = self.getPart('torso', lodName).find('**/joint_Rhold')
            if base.config.GetBool('want-new-anims', 1):
                if not self.getPart('torso', lodName).find('**/def_joint_right_hold').isEmpty():
                    hand = self.getPart('torso', lodName).find('**/def_joint_right_hold')
            else:
                hand = self.getPart('torso', lodName).find('**/joint_Rhold')
            self.rightHands.append(hand)
            rightHand = rightHand.instanceTo(hand)
            if base.config.GetBool('want-new-anims', 1):
                if not self.getPart('torso', lodName).find('**/def_joint_left_hold').isEmpty():
                    hand = self.getPart('torso', lodName).find('**/def_joint_left_hold')
            else:
                hand = self.getPart('torso', lodName).find('**/joint_Lhold')
            self.leftHands.append(hand)
            leftHand = leftHand.instanceTo(hand)
            if self.rightHand == None:
                self.rightHand = rightHand
            if self.leftHand == None:
                self.leftHand = leftHand

        self.headParts = self.findAllMatches('**/__Actor_head')
        self.legsParts = self.findAllMatches('**/__Actor_legs')
        self.hipsParts = self.legsParts.findAllMatches('**/joint_hips')
        self.torsoParts = self.hipsParts.findAllMatches('**/__Actor_torso')

    def initializeBodyCollisions(self, collIdStr):
        Avatar.Avatar.initializeBodyCollisions(self, collIdStr)
        if not self.ghostMode:
            self.collNode.setCollideMask(self.collNode.getIntoCollideMask() | ToontownGlobals.PieBitmask)

    def getBookActors(self):
        if self.__bookActors:
            return self.__bookActors
        bookActor = Actor.Actor('phase_3.5/models/props/book-mod', {'book': 'phase_3.5/models/props/book-chan'})
        bookActor2 = Actor.Actor(other=bookActor)
        bookActor3 = Actor.Actor(other=bookActor)
        self.__bookActors = [bookActor, bookActor2, bookActor3]
        hands = self.getRightHands()
        for bookActor, hand in zip(self.__bookActors, hands):
            bookActor.reparentTo(hand)
            bookActor.hide()

        return self.__bookActors

    def getHoleActors(self):
        if self.__holeActors:
            return self.__holeActors
        holeActor = Actor.Actor('phase_3.5/models/props/portal-mod', {'hole': 'phase_3.5/models/props/portal-chan'})
        holeActor2 = Actor.Actor(other=holeActor)
        holeActor3 = Actor.Actor(other=holeActor)
        self.__holeActors = [holeActor, holeActor2, holeActor3]
        for ha in self.__holeActors:
            if hasattr(self, 'uniqueName'):
                holeName = self.uniqueName('toon-portal')
            else:
                holeName = 'toon-portal'
            ha.setName(holeName)

        return self.__holeActors

    def rescaleToon(self):
        animalStyle = self.style.getAnimal()
        bodyScale = ToontownGlobals.toonBodyScales[animalStyle]
        headScale = ToontownGlobals.toonHeadScales[animalStyle]
        self.setAvatarScale(bodyScale)
        for lod in self.getLODNames():
            self.getPart('head', lod).setScale(headScale)

    def getBodyScale(self):
        animalStyle = self.style.getAnimal()
        bodyScale = ToontownGlobals.toonBodyScales[animalStyle]
        return bodyScale

    def resetHeight(self):
        if hasattr(self, 'style') and self.style:
            animal = self.style.getAnimal()
            bodyScale = ToontownGlobals.toonBodyScales[animal]
            headScale = ToontownGlobals.toonHeadScales[animal][2]
            shoulderHeight = ToontownGlobals.legHeightDict[self.style.legs] * bodyScale + ToontownGlobals.torsoHeightDict[self.style.torso] * bodyScale
            height = shoulderHeight + ToontownGlobals.headHeightDict[self.style.head] * headScale
            self.shoulderHeight = shoulderHeight
            if self.cheesyEffect == ToontownGlobals.CEBigToon or self.cheesyEffect == ToontownGlobals.CEBigWhite:
                height *= ToontownGlobals.BigToonScale
            elif self.cheesyEffect == ToontownGlobals.CESmallToon:
                height *= ToontownGlobals.SmallToonScale
            self.setHeight(height)

    def generateToonLegs(self, copy = 1):
        global Preloaded
        legStyle = self.style.legs
        filePrefix = LegDict.get(legStyle)
        if filePrefix is None:
            self.notify.error('unknown leg style: %s' % legStyle)
        self.loadModel(Preloaded[filePrefix+'-1000'], 'legs', '1000', True)
        self.loadModel(Preloaded[filePrefix+'-500'], 'legs', '500', True)
        self.loadModel(Preloaded[filePrefix+'-250'], 'legs', '250', True)
        if not copy:
            self.showPart('legs', '1000')
            self.showPart('legs', '500')
            self.showPart('legs', '250')
        self.loadAnims(LegsAnimDict[legStyle], 'legs', '1000')
        self.loadAnims(LegsAnimDict[legStyle], 'legs', '500')
        self.loadAnims(LegsAnimDict[legStyle], 'legs', '250')
        self.findAllMatches('**/boots_short').stash()
        self.findAllMatches('**/boots_long').stash()
        self.findAllMatches('**/shoes').stash()

    def swapToonLegs(self, legStyle, copy = 1):
        self.unparentToonParts()
        self.removePart('legs', '1000')
        self.removePart('legs', '500')
        self.removePart('legs', '250')
        # Bugfix: Until upstream Panda3D includes this, we have to do it here.
        if 'legs' in self._Actor__commonBundleHandles:
            del self._Actor__commonBundleHandles['legs']
        self.style.legs = legStyle
        self.generateToonLegs(copy)
        self.generateToonColor()
        self.parentToonParts()
        self.rescaleToon()
        self.resetHeight()
        del self.shadowJoint
        self.initializeDropShadow()
        self.initializeNametag3d()

    def generateToonTorso(self, copy = 1, genClothes = 1):
        global Preloaded
        torsoStyle = self.style.torso
        filePrefix = TorsoDict.get(torsoStyle)
        if filePrefix is None:
            self.notify.error('unknown torso style: %s' % torsoStyle)
        self.loadModel(Preloaded[filePrefix+'-1000'], 'torso', '1000', True)
        if len(torsoStyle) == 1:
            self.loadModel(Preloaded[filePrefix+'-1000'], 'torso', '500', True)
            self.loadModel(Preloaded[filePrefix+'-1000'], 'torso', '250', True)
        else:
            self.loadModel(Preloaded[filePrefix+'-500'], 'torso', '500', True)
            self.loadModel(Preloaded[filePrefix+'-250'], 'torso', '250', True)
        if not copy:
            self.showPart('torso', '1000')
            self.showPart('torso', '500')
            self.showPart('torso', '250')
        self.loadAnims(TorsoAnimDict[torsoStyle], 'torso', '1000')
        self.loadAnims(TorsoAnimDict[torsoStyle], 'torso', '500')
        self.loadAnims(TorsoAnimDict[torsoStyle], 'torso', '250')
        if genClothes == 1 and not len(torsoStyle) == 1:
            self.generateToonClothes()

    def swapToonTorso(self, torsoStyle, copy = 1, genClothes = 1):
        self.unparentToonParts()
        self.removePart('torso', '1000')
        self.removePart('torso', '500')
        self.removePart('torso', '250')
        # Bugfix: Until upstream Panda3D includes this, we have to do it here.
        if 'torso' in self._Actor__commonBundleHandles:
            del self._Actor__commonBundleHandles['torso']
        self.style.torso = torsoStyle
        self.generateToonTorso(copy, genClothes)
        self.generateToonColor()
        self.parentToonParts()
        self.rescaleToon()
        self.resetHeight()
        self.setupToonNodes()
        self.generateBackpack()

    def generateToonHead(self, copy = 1):
        headHeight = ToonHead.generateToonHead(self, copy, self.style, ('1000', '500', '250'))
        if self.style.getAnimal() == 'dog':
            self.loadAnims(HeadAnimDict[self.style.head], 'head', '1000')
            self.loadAnims(HeadAnimDict[self.style.head], 'head', '500')
            self.loadAnims(HeadAnimDict[self.style.head], 'head', '250')

    def swapToonHead(self, headStyle, copy = 1):
        self.stopLookAroundNow()
        self.eyelids.request('open')
        self.unparentToonParts()
        self.removePart('head', '1000')
        self.removePart('head', '500')
        self.removePart('head', '250')
        # Bugfix: Until upstream Panda3D includes this, we have to do it here.
        if 'head' in self._Actor__commonBundleHandles:
            del self._Actor__commonBundleHandles['head']
        self.style.head = headStyle
        self.generateToonHead(copy)
        self.generateToonColor()
        self.parentToonParts()
        self.rescaleToon()
        self.resetHeight()
        self.eyelids.request('open')
        self.startLookAround()

    def generateToonColor(self):
        ToonHead.generateToonColor(self, self.style)
        armColor = self.style.getArmColor()
        gloveColor = self.style.getGloveColor()
        legColor = self.style.getLegColor()
        for lodName in self.getLODNames():
            torso = self.getPart('torso', lodName)
            if len(self.style.torso) == 1:
                parts = torso.findAllMatches('**/torso*')
                parts.setColor(*armColor)
            for pieceName in ('arms', 'neck'):
                piece = torso.find('**/' + pieceName)
                piece.setColor(*armColor)

            if self.style.getAnimal() == 'kiwi':
                torso.find('**/arms').hide()
            else:
                torso.find('**/arms').show()

            hands = torso.find('**/hands')
            hands.setColor(*gloveColor)
            legs = self.getPart('legs', lodName)
            for pieceName in ('legs', 'feet'):
                piece = legs.find('**/%s;+s' % pieceName)
                piece.setColor(*legColor)

        if self.cheesyEffect == ToontownGlobals.CEGreenToon:
            self.reapplyCheesyEffect()

    def swapToonColor(self, dna):
        self.setStyle(dna)
        self.generateToonColor()

    def __swapToonClothes(self, dna):
        self.setStyle(dna)
        self.generateToonClothes(fromNet=1)

    def sendLogSuspiciousEvent(self, msg):
        pass

    def generateToonClothes(self, fromNet = 0):
        swappedTorso = 0
        if self.hasLOD():
            if self.style.getGender() == 'f' and fromNet == 0:
                try:
                    bottomPair = ToonDNA.GirlBottoms[self.style.botTex]
                except:
                    bottomPair = ToonDNA.GirlBottoms[0]

                if len(self.style.torso) < 2:
                    self.sendLogSuspiciousEvent('nakedToonDNA %s was requested' % self.style.torso)
                    return 0
                elif self.style.torso[1] == 's' and bottomPair[1] == ToonDNA.SKIRT:
                    self.swapToonTorso(self.style.torso[0] + 'd', genClothes=0)
                    swappedTorso = 1
                elif self.style.torso[1] == 'd' and bottomPair[1] == ToonDNA.SHORTS:
                    self.swapToonTorso(self.style.torso[0] + 's', genClothes=0)
                    swappedTorso = 1
            try:
                texName = ToonDNA.Shirts[self.style.topTex]
            except:
                texName = ToonDNA.Shirts[0]

            shirtTex = loader.loadTexture(texName, okMissing=True)
            if shirtTex is None:
                self.sendLogSuspiciousEvent('failed to load texture %s' % texName)
                shirtTex = loader.loadTexture(ToonDNA.Shirts[0])
            shirtTex.setMinfilter(Texture.FTLinearMipmapLinear)
            shirtTex.setMagfilter(Texture.FTLinear)
            try:
                shirtColor = ToonDNA.ClothesColors[self.style.topTexColor]
            except:
                shirtColor = ToonDNA.ClothesColors[0]

            try:
                texName = ToonDNA.Sleeves[self.style.sleeveTex]
            except:
                texName = ToonDNA.Sleeves[0]

            sleeveTex = loader.loadTexture(texName, okMissing=True)
            if sleeveTex is None:
                self.sendLogSuspiciousEvent('failed to load texture %s' % texName)
                sleeveTex = loader.loadTexture(ToonDNA.Sleeves[0])
            sleeveTex.setMinfilter(Texture.FTLinearMipmapLinear)
            sleeveTex.setMagfilter(Texture.FTLinear)
            try:
                sleeveColor = ToonDNA.ClothesColors[self.style.sleeveTexColor]
            except:
                sleeveColor = ToonDNA.ClothesColors[0]

            if self.style.getGender() == 'm':
                try:
                    texName = ToonDNA.BoyShorts[self.style.botTex]
                except:
                    texName = ToonDNA.BoyShorts[0]

            else:
                try:
                    texName = ToonDNA.GirlBottoms[self.style.botTex][0]
                except:
                    texName = ToonDNA.GirlBottoms[0][0]

            bottomTex = loader.loadTexture(texName, okMissing=True)
            if bottomTex is None:
                self.sendLogSuspiciousEvent('failed to load texture %s' % texName)
                if self.style.getGender() == 'm':
                    bottomTex = loader.loadTexture(ToonDNA.BoyShorts[0])
                else:
                    bottomTex = loader.loadTexture(ToonDNA.GirlBottoms[0][0])
            bottomTex.setMinfilter(Texture.FTLinearMipmapLinear)
            bottomTex.setMagfilter(Texture.FTLinear)
            try:
                bottomColor = ToonDNA.ClothesColors[self.style.botTexColor]
            except:
                bottomColor = ToonDNA.ClothesColors[0]

            darkBottomColor = bottomColor * 0.5
            darkBottomColor.setW(1.0)
            for lodName in self.getLODNames():
                thisPart = self.getPart('torso', lodName)
                top = thisPart.find('**/torso-top')
                top.setTexture(shirtTex, 1)
                top.setColor(shirtColor)
                sleeves = thisPart.find('**/sleeves')
                sleeves.setTexture(sleeveTex, 1)
                sleeves.setColor(sleeveColor)
                bottoms = thisPart.findAllMatches('**/torso-bot')
                for bottomNum in xrange(0, bottoms.getNumPaths()):
                    bottom = bottoms.getPath(bottomNum)
                    bottom.setTexture(bottomTex, 1)
                    bottom.setColor(bottomColor)

                caps = thisPart.findAllMatches('**/torso-bot-cap')
                caps.setColor(darkBottomColor)

        return swappedTorso

    def _getCustomAccessoryData(self, accessoryType, accessoryId):
        registryPaths = []
        relativePath = os.path.join('resources', 'phase_14', 'accessories', 'accessories_registry.json')

        currentDirectory = os.path.abspath(os.getcwd())
        while True:
            registryPaths.append(os.path.join(currentDirectory, relativePath))
            parentDirectory = os.path.dirname(currentDirectory)
            if parentDirectory == currentDirectory:
                break
            currentDirectory = parentDirectory

        try:
            currentDirectory = os.path.dirname(os.path.abspath(__file__))
            while True:
                registryPath = os.path.join(currentDirectory, relativePath)
                if registryPath not in registryPaths:
                    registryPaths.append(registryPath)
                parentDirectory = os.path.dirname(currentDirectory)
                if parentDirectory == currentDirectory:
                    break
                currentDirectory = parentDirectory
        except Exception:
            pass

        registry = None
        for registryPath in registryPaths:
            if not os.path.isfile(registryPath):
                continue
            try:
                registryFile = open(registryPath, 'r')
                try:
                    registry = json.load(registryFile)
                finally:
                    registryFile.close()
                break
            except Exception:
                registry = None

        if not isinstance(registry, dict):
            return None

        accessories = registry.get('accessories', {})
        if not isinstance(accessories, dict):
            return None

        for accessoryData in accessories.values():
            if not isinstance(accessoryData, dict):
                continue
            if accessoryData.get('type') != accessoryType:
                continue
            if accessoryData.get('id') == accessoryId:
                return accessoryData

        return None

    def _clearCustomAccessoryNodes(self, nodeListName):
        nodeList = getattr(self, nodeListName, [])
        for node in nodeList:
            try:
                node.removeNode()
            except Exception:
                pass
        setattr(self, nodeListName, [])

    def _generateCustomAccessory(self, accessoryType, accessoryId):
        accessoryData = self._getCustomAccessoryData(accessoryType, accessoryId)
        if accessoryData is None:
            return False

        modelPath = accessoryData.get('model')
        if not modelPath:
            return False

        modelCandidates = [modelPath]

        normalizedModelPath = modelPath.replace('\\\\', '/')
        if normalizedModelPath.startswith('resources/'):
            normalizedModelPath = normalizedModelPath[len('resources/'):]

        relativeResourcePath = os.path.join('resources', normalizedModelPath)
        currentDirectory = os.path.abspath(os.getcwd())

        while True:
            absoluteCandidate = os.path.join(currentDirectory, relativeResourcePath)
            if absoluteCandidate not in modelCandidates:
                modelCandidates.append(absoluteCandidate)

            parentDirectory = os.path.dirname(currentDirectory)
            if parentDirectory == currentDirectory:
                break
            currentDirectory = parentDirectory

        try:
            currentDirectory = os.path.dirname(os.path.abspath(__file__))
            while True:
                absoluteCandidate = os.path.join(currentDirectory, relativeResourcePath)
                if absoluteCandidate not in modelCandidates:
                    modelCandidates.append(absoluteCandidate)

                parentDirectory = os.path.dirname(currentDirectory)
                if parentDirectory == currentDirectory:
                    break
                currentDirectory = parentDirectory
        except Exception:
            pass

        geom = None
        loadedModelPath = None

        for modelCandidate in modelCandidates:
            try:
                candidateGeom = loader.loadModel(modelCandidate, okMissing=True)
            except Exception:
                candidateGeom = None

            if candidateGeom and not candidateGeom.isEmpty():
                geom = candidateGeom
                loadedModelPath = modelCandidate
                break

        if geom is None or geom.isEmpty():
            print 'CUSTOM ACCESSORY MODEL FAILED:', modelPath
            print 'CUSTOM ACCESSORY MODEL CANDIDATES:', modelCandidates
            self.sendLogSuspiciousEvent(
                'failed to load custom accessory model %s' % modelPath
            )
            return True

        print 'CUSTOM ACCESSORY MODEL LOADED:', loadedModelPath

        if accessoryType == 'hat':
            self._clearCustomAccessoryNodes('hatNodes')
            placementKey = self.style.head[:2]
            transOffset = AccessoryGlobals.HatTransTable.get(placementKey)
            if transOffset is None:
                return True

            geom.unstash()
            geom.show()
            for child in geom.findAllMatches('**'):
                child.unstash()
                child.show()

            geom.setPos(*transOffset[0])
            geom.setHpr(*transOffset[1])
            geom.setScale(*transOffset[2])
            geom.setTwoSided(True)

            for headNode in self.findAllMatches('**/__Actor_head'):
                accessoryNode = headNode.attachNewNode('hatNode')
                geom.instanceTo(accessoryNode)
                self.hatNodes.append(accessoryNode)

        elif accessoryType == 'glasses':
            self._clearCustomAccessoryNodes('glassesNodes')
            placementKey = self.style.head[:2]
            transOffset = AccessoryGlobals.GlassesTransTable.get(placementKey)
            if transOffset is None:
                return True

            geom.unstash()
            geom.show()
            for child in geom.findAllMatches('**'):
                child.unstash()
                child.show()

            geom.setPos(*transOffset[0])
            geom.setHpr(*transOffset[1])
            geom.setScale(*transOffset[2])
            geom.setTwoSided(True)

            for headNode in self.findAllMatches('**/__Actor_head'):
                accessoryNode = headNode.attachNewNode('glassesNode')
                geom.instanceTo(accessoryNode)
                self.glassesNodes.append(accessoryNode)

        elif accessoryType == 'backpack':
            self._clearCustomAccessoryNodes('backpackNodes')
            placementKey = self.style.torso[:1]
            transOffset = _getAccessoryPlacementOverride('backpack', accessoryId, placementKey)
            if transOffset is None and AccessoryGlobals.ExtendedBackpackTransTable.get(accessoryId):
                transOffset = AccessoryGlobals.ExtendedBackpackTransTable[accessoryId].get(placementKey)
            if transOffset is None:
                transOffset = AccessoryGlobals.BackpackTransTable.get(placementKey)
            if transOffset is None:
                return True
            geom.setPos(*transOffset[0])
            geom.setHpr(*transOffset[1])
            geom.setScale(*transOffset[2])
            for attachNode in self.findAllMatches('**/def_joint_attachFlower'):
                accessoryNode = attachNode.attachNewNode('backpackNode')
                self.backpackNodes.append(accessoryNode)
                geom.instanceTo(accessoryNode)

        elif accessoryType == 'shoes':
            self._clearCustomAccessoryNodes('shoesNodes')
            accessoryNode = self.attachNewNode('customShoesNode')
            self.shoesNodes.append(accessoryNode)
            geom.reparentTo(accessoryNode)

        return True

    def _spinCakeHatTask(self, task):
        nodes = getattr(self, '_cakeHatSpinNodes', [])
        validNodes = []
        heading = (task.time * 90.0) % 360.0
        for node in nodes:
            if node and not node.isEmpty():
                node.setH(heading)
                validNodes.append(node)
        self._cakeHatSpinNodes = validNodes
        if not validNodes:
            return Task.done
        return Task.cont

    def _getSafeAccessoryTextureName(self, accessoryType, modelIdx,
                                         textureIdx, colorIdx):
        if textureIdx == 0:
            return None

        textureTables = {
            'hat': (ToonDNA.HatTextures, ToonDNA.HatStyles),
            'glasses': (ToonDNA.GlassesTextures, ToonDNA.GlassesStyles),
            'backpack': (ToonDNA.BackpackTextures, ToonDNA.BackpackStyles),
            'shoes': (ToonDNA.ShoesTextures, ToonDNA.ShoesStyles)
        }
        textureList, styleDict = textureTables[accessoryType]

        if (not isinstance(textureIdx, int) or textureIdx < 0 or
                textureIdx >= len(textureList)):
            self.notify.warning(
                'Ignoring stale %s texture ID %s for model %s; '
                'the registry no longer contains that ID.' %
                (accessoryType, textureIdx, modelIdx)
            )
            return None

        textureName = textureList[textureIdx]
        if not isinstance(textureName, basestring) or not textureName:
            self.notify.warning(
                'Ignoring empty %s texture ID %s for model %s.' %
                (accessoryType, textureIdx, modelIdx)
            )
            return None

        # A texture ID is only safe when the currently loaded style tables
        # explicitly associate it with this model. This prevents a stale ID
        # from applying an unrelated texture after a registry rebuild.
        compatible = False
        for style in styleDict.values():
            if (isinstance(style, (list, tuple)) and len(style) >= 2 and
                    style[0] == modelIdx and style[1] == textureIdx):
                compatible = True
                break

        if not compatible:
            self.notify.warning(
                'Ignoring incompatible %s texture ID %s for model %s.' %
                (accessoryType, textureIdx, modelIdx)
            )
            return None

        return textureName

    def _cleanupHighRollerDuckOrbit(self):
        taskMgr.remove('highRollerDuckOrbit-%s' % id(self))

        for hatActor in getattr(self, '_highRollerHatActors', []):
            try:
                hatActor.stop()
            except Exception:
                pass
            try:
                hatActor.cleanup()
            except Exception:
                try:
                    hatActor.removeNode()
                except Exception:
                    pass

        self._highRollerHatActors = []
        self._highRollerDuckOrbits = []

    def _setupHighRollerDuckOrbit(self, hatActor):
        # Capture the authored joint transforms before controlJoint takes
        # ownership of DucksALL.
        rootJoint = hatActor.exposeJoint(None, 'modelRoot', 'Root')
        ducksJoint = hatActor.exposeJoint(None, 'modelRoot', 'DucksALL')

        if (rootJoint is None or rootJoint.isEmpty() or
                ducksJoint is None or ducksJoint.isEmpty()):
            self.notify.warning(
                'High Roller hat is missing Root or DucksALL.'
            )
            return False

        rootModelMat = rootJoint.getMat(hatActor)
        ducksModelMat = ducksJoint.getMat(hatActor)

        ducksControl = hatActor.controlJoint(
            None,
            'modelRoot',
            'DucksALL'
        )
        if ducksControl is None or ducksControl.isEmpty():
            self.notify.warning(
                'Could not control the High Roller DucksALL joint.'
            )
            return False

        # rootReference stores Root's authored transform in model space.
        # orbitPivot rotates around the model's vertical Z axis.
        # orbitMarker stores DucksALL's authored model-space transform.
        rootReference = hatActor.attachNewNode(
            'highRollerRootReference'
        )
        rootReference.setMat(rootModelMat)

        orbitPivot = hatActor.attachNewNode(
            'highRollerDuckOrbitPivot'
        )
        orbitMarker = orbitPivot.attachNewNode(
            'highRollerDuckOrbitMarker'
        )
        orbitMarker.setMat(ducksModelMat)

        # At zero degrees this reproduces the exact authored local
        # DucksALL transform relative to Root.
        ducksControl.setMat(
            orbitMarker.getMat(rootReference)
        )

        self._highRollerDuckOrbits.append((
            hatActor,
            ducksControl,
            rootReference,
            orbitPivot,
            orbitMarker
        ))
        return True

    def _highRollerDuckOrbitTask(self, task):
        validOrbits = []
        heading = (task.time * 120.0) % 360.0

        for orbitData in self._highRollerDuckOrbits:
            try:
                hatActor, ducksControl, rootReference, orbitPivot, orbitMarker = orbitData
            except Exception:
                continue

            if (hatActor is None or hatActor.isEmpty() or
                    ducksControl is None or ducksControl.isEmpty() or
                    rootReference is None or rootReference.isEmpty() or
                    orbitPivot is None or orbitPivot.isEmpty() or
                    orbitMarker is None or orbitMarker.isEmpty()):
                continue

            # Rotate the complete authored DucksALL transform horizontally
            # in model space, then convert it back into the local transform
            # expected beneath the authored Root joint.
            orbitPivot.setH(heading)
            ducksControl.setMat(
                orbitMarker.getMat(rootReference)
            )
            validOrbits.append(orbitData)

        self._highRollerDuckOrbits = validOrbits
        if not validOrbits:
            return Task.done
        return Task.cont

    def generateHat(self, fromRTM = False):
        self._cleanupHighRollerDuckOrbit()
        taskMgr.remove('cakeHatSpin-%s' % id(self))
        self._cakeHatSpinNodes = []
        hat = self.getHat()
        if (hat[0] < 0 or hat[0] >= len(ToonDNA.HatModels) or
                ToonDNA.HatModels[hat[0]] is None):
            self.sendLogSuspiciousEvent('tried to put a wrong hat idx %d' % hat[0])
            return
        if len(self.hatNodes) > 0:
            for hatNode in self.hatNodes:
                hatNode.removeNode()

            self.hatNodes = []
        self.showEars()
        if hat[0] != 0:
            hatGeom = loader.loadModel(ToonDNA.HatModels[hat[0]], okMissing=True)
            if hatGeom:
                hatTexture = None
                if hat[0] == 54:
                    self.hideEars()
                if hat[1] != 0:
                    texName = self._getSafeAccessoryTextureName(
                        'hat', hat[0], hat[1], hat[2]
                    )
                    if texName is not None:
                        tex = loader.loadTexture(texName, okMissing=True)
                        if tex is None:
                            self.sendLogSuspiciousEvent('failed to load texture %s' % texName)
                        else:
                            tex.setMinfilter(Texture.FTLinearMipmapLinear)
                            tex.setMagfilter(Texture.FTLinear)
                            hatTexture = tex
                            hatGeom.setTexture(tex, 1)
                if fromRTM:
                    reload(AccessoryGlobals)
                headKey = self.style.head[:2]
                transOffset = _getAccessoryPlacementOverride(
                    'hat',
                    hat[0],
                    headKey
                )

                if transOffset is None:
                    hatModelPath = ToonDNA.HatModels[hat[0]]
                    if isinstance(hatModelPath, basestring) and hatModelPath.startswith('phase_14/accessories/'):
                        transOffset = ((0, 0, 0), (0, 0, 0), (1, 1, 1))

                if transOffset is None:
                    if AccessoryGlobals.ExtendedHatTransTable.get(hat[0]):
                        transOffset = AccessoryGlobals.ExtendedHatTransTable[hat[0]].get(headKey)

                if transOffset is None:
                    transOffset = AccessoryGlobals.HatTransTable.get(headKey)
                    if transOffset is None:
                        return
                headNodes = self.findAllMatches('**/__Actor_head')
                if hat[0] == 63:
                    hatGeom.setPos(0, 0, 0)
                    hatGeom.setHpr(0, 0, 0)
                    hatGeom.setScale(1, 1, 1)
                    for headNode in headNodes:
                        hatNode = headNode.attachNewNode('hatNode')
                        hatNode.setPos(transOffset[0][0], transOffset[0][1], transOffset[0][2])
                        hatNode.setHpr(transOffset[1][0], transOffset[1][1], transOffset[1][2])
                        hatNode.setScale(transOffset[2][0], transOffset[2][1], transOffset[2][2])
                        spinNode = hatNode.attachNewNode('cakeHatSpinNode')
                        hatGeom.instanceTo(spinNode)
                        self._cakeHatSpinNodes.append(spinNode)
                        self.hatNodes.append(hatNode)
                    if self._cakeHatSpinNodes:
                        taskMgr.add(self._spinCakeHatTask, 'cakeHatSpin-%s' % id(self))
                else:
                    if hat[0] == 154:
                        for headNode in headNodes:
                            hatNode = headNode.attachNewNode('hatNode')
                            hatNode.setPos(
                                transOffset[0][0],
                                transOffset[0][1],
                                transOffset[0][2]
                            )
                            hatNode.setHpr(
                                transOffset[1][0],
                                transOffset[1][1],
                                transOffset[1][2]
                            )
                            hatNode.setScale(
                                transOffset[2][0],
                                transOffset[2][1],
                                transOffset[2][2]
                            )

                            highRollerActor = Actor.Actor(
                                ToonDNA.HatModels[hat[0]]
                            )
                            highRollerActor.reparentTo(hatNode)
                            highRollerActor.setPos(0, 0, 0)
                            highRollerActor.setHpr(0, 0, 0)
                            highRollerActor.setScale(1, 1, 1)

                            if hatTexture is not None:
                                highRollerActor.setTexture(
                                    hatTexture,
                                    1
                                )

                            self._highRollerHatActors.append(
                                highRollerActor
                            )
                            self._setupHighRollerDuckOrbit(
                                highRollerActor
                            )
                            self.hatNodes.append(hatNode)

                        if self._highRollerDuckOrbits:
                            taskMgr.add(
                                self._highRollerDuckOrbitTask,
                                'highRollerDuckOrbit-%s' % id(self)
                            )
                    else:
                        hatGeom.setPos(transOffset[0][0], transOffset[0][1], transOffset[0][2])
                        hatGeom.setHpr(transOffset[1][0], transOffset[1][1], transOffset[1][2])
                        hatGeom.setScale(transOffset[2][0], transOffset[2][1], transOffset[2][2])
                        for headNode in headNodes:
                            hatNode = headNode.attachNewNode('hatNode')
                            self.hatNodes.append(hatNode)
                            hatGeom.instanceTo(hatNode)

    def generateGlasses(self, fromRTM = False):
        glasses = self.getGlasses()
        if (glasses[0] < 0 or glasses[0] >= len(ToonDNA.GlassesModels) or
                ToonDNA.GlassesModels[glasses[0]] is None):
            self.sendLogSuspiciousEvent('tried to put a wrong glasses idx %d' % glasses[0])
            return
        if len(self.glassesNodes) > 0:
            for glassesNode in self.glassesNodes:
                glassesNode.removeNode()

            self.glassesNodes = []
        self.showEyelashes()
        if glasses[0] != 0:
            glassesGeom = loader.loadModel(ToonDNA.GlassesModels[glasses[0]], okMissing=True)
            if glassesGeom:
                if glasses[0] in [15, 16]:
                    self.hideEyelashes()
                if glasses[1] != 0:
                    texName = self._getSafeAccessoryTextureName(
                        'glasses', glasses[0], glasses[1], glasses[2]
                    )
                    if texName is not None:
                        tex = loader.loadTexture(texName, okMissing=True)
                        if tex is None:
                            self.sendLogSuspiciousEvent('failed to load texture %s' % texName)
                        else:
                            tex.setMinfilter(Texture.FTLinearMipmapLinear)
                            tex.setMagfilter(Texture.FTLinear)
                            glassesGeom.setTexture(tex, 1)
                if fromRTM:
                    reload(AccessoryGlobals)
                headKey = self.style.head[:2]
                transOffset = _getAccessoryPlacementOverride(
                    'glasses',
                    glasses[0],
                    headKey
                )

                if transOffset is None:
                    glassesModelPath = ToonDNA.GlassesModels[glasses[0]]
                    if isinstance(glassesModelPath, basestring) and glassesModelPath.startswith('phase_14/accessories/'):
                        transOffset = ((0, 0, 0), (0, 0, 0), (1, 1, 1))

                if transOffset is None:
                    if AccessoryGlobals.ExtendedGlassesTransTable.get(glasses[0]):
                        transOffset = AccessoryGlobals.ExtendedGlassesTransTable[glasses[0]].get(headKey)

                if transOffset is None:
                    transOffset = AccessoryGlobals.GlassesTransTable.get(headKey)
                    if transOffset is None:
                        return
                glassesGeom.setPos(transOffset[0][0], transOffset[0][1], transOffset[0][2])
                glassesGeom.setHpr(transOffset[1][0], transOffset[1][1], transOffset[1][2])
                glassesGeom.setScale(transOffset[2][0], transOffset[2][1], transOffset[2][2])
                headNodes = self.findAllMatches('**/__Actor_head')
                for headNode in headNodes:
                    glassesNode = headNode.attachNewNode('glassesNode')
                    self.glassesNodes.append(glassesNode)
                    glassesGeom.instanceTo(glassesNode)

    def generateBackpack(self, fromRTM = False):
        backpack = self.getBackpack()
        if self._generateCustomAccessory('backpack', backpack[0]):
            return
        if (backpack[0] < 0 or backpack[0] >= len(ToonDNA.BackpackModels) or
                ToonDNA.BackpackModels[backpack[0]] is None):
            self.sendLogSuspiciousEvent('tried to put a wrong backpack idx %d' % backpack[0])
            return
        if len(self.backpackNodes) > 0:
            for backpackNode in self.backpackNodes:
                backpackNode.removeNode()

            self.backpackNodes = []
        if backpack[0] != 0:
            geom = loader.loadModel(ToonDNA.BackpackModels[backpack[0]], okMissing=True)
            if geom:
                if backpack[1] != 0:
                    texName = self._getSafeAccessoryTextureName(
                        'backpack', backpack[0], backpack[1], backpack[2]
                    )
                    if texName is not None:
                        tex = loader.loadTexture(texName, okMissing=True)
                        if tex is None:
                            self.sendLogSuspiciousEvent('failed to load texture %s' % texName)
                        else:
                            tex.setMinfilter(Texture.FTLinearMipmapLinear)
                            tex.setMagfilter(Texture.FTLinear)
                            geom.setTexture(tex, 1)
                if fromRTM:
                    reload(AccessoryGlobals)
                transOffset = None
                if AccessoryGlobals.ExtendedBackpackTransTable.get(backpack[0]):
                    transOffset = AccessoryGlobals.ExtendedBackpackTransTable[backpack[0]].get(self.style.torso[:1])
                if transOffset is None:
                    transOffset = AccessoryGlobals.BackpackTransTable.get(self.style.torso[:1])
                    if transOffset is None:
                        return
                geom.setPos(transOffset[0][0], transOffset[0][1], transOffset[0][2])
                geom.setHpr(transOffset[1][0], transOffset[1][1], transOffset[1][2])
                geom.setScale(transOffset[2][0], transOffset[2][1], transOffset[2][2])
                nodes = self.findAllMatches('**/def_joint_attachFlower')
                for node in nodes:
                    theNode = node.attachNewNode('backpackNode')
                    self.backpackNodes.append(theNode)
                    geom.instanceTo(theNode)

    def generateShoes(self):
        shoes = self.getShoes()
        if self._generateCustomAccessory('shoes', shoes[0]):
            return
        self._clearCustomAccessoryNodes('shoesNodes')
        if (shoes[0] < 0 or shoes[0] >= len(ToonDNA.ShoesModels) or
                ToonDNA.ShoesModels[shoes[0]] is None):
            self.sendLogSuspiciousEvent('tried to put a wrong shoes idx %d' % shoes[0])
            return
        self.findAllMatches('**/feet;+s').stash()
        self.findAllMatches('**/boots_short;+s').stash()
        self.findAllMatches('**/boots_long;+s').stash()
        self.findAllMatches('**/shoes;+s').stash()
        geoms = self.findAllMatches('**/%s;+s' % ToonDNA.ShoesModels[shoes[0]])
        for geom in geoms:
            geom.unstash()

        if shoes[0] != 0:
            texName = self._getSafeAccessoryTextureName(
                'shoes', shoes[0], shoes[1], shoes[2]
            )
            if texName is not None:
                if self.style.legs == 'l' and shoes[0] == 3:
                    texName = texName[:-4] + 'LL.jpg'
                for geom in geoms:
                    tex = loader.loadTexture(texName, okMissing=True)
                    if tex is None:
                        self.sendLogSuspiciousEvent('failed to load texture %s' % texName)
                    else:
                        tex.setMinfilter(Texture.FTLinearMipmapLinear)
                        tex.setMagfilter(Texture.FTLinear)
                        geom.setTexture(tex, 1)

    def generateToonAccessories(self):
        self.generateHat()
        self.generateGlasses()
        self.generateBackpack()
        self.generateShoes()

    def setHat(self, hatIdx, textureIdx, colorIdx, fromRTM = False):
        self.hat = (hatIdx, textureIdx, colorIdx)
        self.generateHat(fromRTM=fromRTM)

    def getHat(self):
        return self.hat

    def setGlasses(self, glassesIdx, textureIdx, colorIdx, fromRTM = False):
        self.glasses = (glassesIdx, textureIdx, colorIdx)
        self.generateGlasses(fromRTM=fromRTM)

    def getGlasses(self):
        return self.glasses

    def setBackpack(self, backpackIdx, textureIdx, colorIdx, fromRTM = False):
        self.backpack = (backpackIdx, textureIdx, colorIdx)
        self.generateBackpack(fromRTM=fromRTM)

    def getBackpack(self):
        return self.backpack

    def setShoes(self, shoesIdx, textureIdx, colorIdx):
        self.shoes = (shoesIdx, textureIdx, colorIdx)
        self.generateShoes()

    def getShoes(self):
        return self.shoes

    def getDialogueArray(self):
        animalType = self.style.getType()
        if self.isDisguised or self.cogHead:
            dialogueArray = Suit.SuitDialogArray
        else:
            if animalType == 'dog':
                dialogueArray = DogDialogueArray
            elif animalType == 'cat':
                dialogueArray = CatDialogueArray
            elif animalType == 'horse':
                dialogueArray = HorseDialogueArray
            elif animalType == 'mouse':
                dialogueArray = MouseDialogueArray
            elif animalType == 'rabbit':
                dialogueArray = RabbitDialogueArray
            elif animalType == 'duck':
                dialogueArray = DuckDialogueArray
            elif animalType == 'monkey':
                dialogueArray = MonkeyDialogueArray
            elif animalType == 'bear':
                dialogueArray = BearDialogueArray
            elif animalType == 'pig':
                dialogueArray = PigDialogueArray
            elif animalType == 'deer':
                dialogueArray = DeerDialogueArray
            elif animalType == 'beaver':
                dialogueArray = BeaverDialogueArray
            elif animalType == 'alligator':
                dialogueArray = AlligatorDialogueArray
            elif animalType == 'fox':
                dialogueArray = FoxDialogueArray
            elif animalType == 'bat':
                dialogueArray = BatDialogueArray
            elif animalType == 'raccoon':
                dialogueArray = RaccoonDialogueArray
            elif animalType == 'armadillo':
                dialogueArray = ArmadilloDialogueArray
            elif animalType == 'kangaroo':
                dialogueArray = KangarooDialogueArray
            elif animalType == 'kiwi':
                dialogueArray = KiwiDialogueArray
            elif animalType == 'koala':
                dialogueArray = KoalaDialogueArray
            elif animalType == 'turkey':
                dialogueArray = TurkeyDialogueArray
            else:
                dialogueArray = None
        return dialogueArray

    def getShadowJoint(self):
        if hasattr(self, 'shadowJoint'):
            return self.shadowJoint
        shadowJoint = NodePath('shadowJoint')
        for lodName in self.getLODNames():
            joint = self.getPart('legs', lodName).find('**/joint_shadow')
            shadowJoint = shadowJoint.instanceTo(joint)

        self.shadowJoint = shadowJoint
        return shadowJoint

    def getNametagJoints(self):
        joints = []
        for lodName in self.getLODNames():
            bundle = self.getPartBundle('legs', lodName)
            joint = bundle.findChild('joint_nameTag')
            if joint:
                joints.append(joint)

        return joints

    def getRightHands(self):
        return self.rightHands

    def getLeftHands(self):
        return self.leftHands

    def getHeadParts(self):
        return self.headParts

    def getHipsParts(self):
        return self.hipsParts

    def getTorsoParts(self):
        return self.torsoParts

    def getLegsParts(self):
        return self.legsParts

    def findSomethingToLookAt(self):
        if self.randGen.random() < 0.1 or not hasattr(self, 'cr'):
            x = self.randGen.choice((-0.8,
             -0.5,
             0,
             0.5,
             0.8))
            y = self.randGen.choice((-0.5,
             0,
             0.5,
             0.8))
            self.lerpLookAt(Point3(x, 1.5, y), blink=1)
            return
        nodePathList = []
        for id, obj in self.cr.doId2do.items():
            if hasattr(obj, 'getStareAtNodeAndOffset') and obj != self:
                node, offset = obj.getStareAtNodeAndOffset()
                if node.getY(self) > 0.0:
                    nodePathList.append((node, offset))

        if nodePathList:
            nodePathList.sort(lambda x, y: cmp(x[0].getDistance(self), y[0].getDistance(self)))
            if len(nodePathList) >= 2:
                if self.randGen.random() < 0.9:
                    chosenNodePath = nodePathList[0]
                else:
                    chosenNodePath = nodePathList[1]
            else:
                chosenNodePath = nodePathList[0]
            self.lerpLookAt(chosenNodePath[0].getPos(self), blink=1)
        else:
            ToonHead.findSomethingToLookAt(self)

    def setForceJumpIdle(self, value):
        self.forceJumpIdle = value

    def setupPickTrigger(self):
        Avatar.Avatar.setupPickTrigger(self)
        torso = self.getPart('torso', '1000')
        if torso == None:
            return 0
        self.pickTriggerNp.reparentTo(torso)
        size = self.style.getTorsoSize()
        if size == 'short':
            self.pickTriggerNp.setPosHprScale(0, 0, 0.5, 0, 0, 0, 1.5, 1.5, 2)
        elif size == 'medium':
            self.pickTriggerNp.setPosHprScale(0, 0, 0.5, 0, 0, 0, 1, 1, 2)
        else:
            self.pickTriggerNp.setPosHprScale(0, 0, 1, 0, 0, 0, 1, 1, 2)
        return 1

    def showBooks(self):
        for bookActor in self.getBookActors():
            bookActor.show()

    def hideBooks(self):
        for bookActor in self.getBookActors():
            bookActor.hide()

    def getWake(self):
        if not self.wake:
            self.wake = Wake.Wake(render, self)
        return self.wake

    def getJar(self):
        if not self.jar:
            self.jar = loader.loadModel('phase_5.5/models/estate/jellybeanJar')
            self.jar.setP(290.0)
            self.jar.setY(0.5)
            self.jar.setZ(0.5)
            self.jar.setScale(0.0)
        return self.jar

    def removeJar(self):
        if self.jar:
            self.jar.removeNode()
            self.jar = None

    def _movementHeadingIsAirborne(self):
        # Only the local Toon owns movement controls. Remote Toons keep the
        # original immediate heading behavior used by network animation.
        try:
            controls = self.controlManager.currentControls
            if controls is None:
                return False

            try:
                return bool(controls.getIsAirborne())
            except:
                return bool(controls.isAirborne)
        except:
            return False

    def _applyMovementGeomHeading(self, node, heading, smooth):
        if node is None or node.isEmpty():
            return

        if not smooth:
            node.setH(heading)
            return

        # Airborne direction keys can change the desired heading by 45, 90,
        # or 180 degrees in one frame. Turn through the shortest angle at a
        # limited rate instead of visibly snapping the Toon in mid-jump.
        currentHeading = node.getH()
        targetHeading = fitDestAngle2Src(currentHeading, heading)
        headingDelta = targetHeading - currentHeading

        dt = globalClock.getDt()
        if dt < 0.0:
            dt = 0.0
        elif dt > 0.05:
            dt = 0.05

        maxHeadingStep = 720.0 * dt

        if abs(headingDelta) <= maxHeadingStep:
            newHeading = targetHeading
        elif headingDelta > 0.0:
            newHeading = currentHeading + maxHeadingStep
        else:
            newHeading = currentHeading - maxHeadingStep

        node.setH(newHeading)

    def _setMovementGeomHeading(self, heading):
        # Rotate only the visible Toon geometry. The avatar node itself
        # remains aligned with the orbital camera and movement controls.
        smooth = self._movementHeadingIsAirborne()

        try:
            self._applyMovementGeomHeading(
                self.getGeomNode(),
                heading,
                smooth
            )
        except:
            pass

        if self.isDisguised:
            try:
                self._applyMovementGeomHeading(
                    self.suit.getGeomNode(),
                    heading,
                    smooth
                )
            except:
                pass

    def setSpeed(self, forwardSpeed, rotateSpeed, slideSpeed = None):
        # The legacy LocalToon animation task calls this with only forward
        # and rotation speed. GravityWalker publishes the current strafe
        # speed directly on the Toon, so both call signatures still work.
        if slideSpeed is None:
            slideSpeed = getattr(self, 'strafeSpeed', 0.0)
        else:
            self.strafeSpeed = slideSpeed

        self.forwardSpeed = forwardSpeed
        self.rotateSpeed = rotateSpeed

        # Face the visible Toon in the real movement direction. This gives
        # pure strafing a 90-degree heading and diagonal strafing a natural
        # 45-degree heading without rotating the camera anchor.
        if abs(slideSpeed) > ToontownGlobals.WalkCutOff and forwardSpeed >= -ToontownGlobals.WalkCutOff:
            movementHeading = math.degrees(math.atan2(-slideSpeed, forwardSpeed))
            self._setMovementGeomHeading(movementHeading)
        else:
            # Preserve the normal backwards-walk behavior instead of
            # turning the visible Toon around by 180 degrees.
            self._setMovementGeomHeading(0.0)

        # Pure strafe movement has a forward speed of zero. Use the slide
        # magnitude only for selecting a walk/run animation; physics still
        # moves the Toon sideways through GravityWalker.
        animationSpeed = forwardSpeed
        if abs(animationSpeed) <= ToontownGlobals.WalkCutOff and abs(slideSpeed) > ToontownGlobals.WalkCutOff:
            animationSpeed = abs(slideSpeed)

        action = None
        if self.standWalkRunReverse != None:
            if animationSpeed >= ToontownGlobals.RunCutOff:
                action = OTPGlobals.RUN_INDEX
            elif animationSpeed > ToontownGlobals.WalkCutOff:
                action = OTPGlobals.WALK_INDEX
            elif animationSpeed < -ToontownGlobals.WalkCutOff:
                action = OTPGlobals.REVERSE_INDEX
            elif rotateSpeed != 0.0:
                action = OTPGlobals.WALK_INDEX
            else:
                action = OTPGlobals.STAND_INDEX
            anim, rate = self.standWalkRunReverse[action]
            self.motion.enter()
            self.motion.setState(anim, rate)
            if anim != self.playingAnim:
                self.playingAnim = anim
                self.playingRate = rate
                self.stop()
                self.loop(anim)
                self.setPlayRate(rate, anim)
                if self.isDisguised:
                    rightHand = self.suit.rightHand
                    numChildren = rightHand.getNumChildren()
                    if numChildren > 0:
                        anim = 'tray-' + anim
                        if anim == 'tray-run':
                            anim = 'tray-walk'
                    self.suit.stop()
                    self.suit.loop(anim)
                    self.suit.setPlayRate(rate, anim)
            elif rate != self.playingRate:
                self.playingRate = rate
                if not self.isDisguised:
                    self.setPlayRate(rate, anim)
                else:
                    self.suit.setPlayRate(rate, anim)
            showWake, wakeWaterHeight = ZoneUtil.getWakeInfo()
            movementMagnitude = max(abs(forwardSpeed), abs(slideSpeed))
            if showWake and self.getZ(render) < wakeWaterHeight and movementMagnitude > ToontownGlobals.WalkCutOff:
                currT = globalClock.getFrameTime()
                deltaT = currT - self.lastWakeTime
                if action == OTPGlobals.RUN_INDEX and deltaT > ToontownGlobals.WakeRunDelta or deltaT > ToontownGlobals.WakeWalkDelta:
                    self.getWake().createRipple(wakeWaterHeight, rate=1, startFrame=4)
                    self.lastWakeTime = currT
                    self.lastWakeTime = currT
        return action

    def enterOff(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = []):
        self.setActiveShadow(0)
        self.playingAnim = None

    def exitOff(self):
        pass

    def enterNeutral(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = []):
        anim = 'neutral'
        self.pose(anim, int(self.getNumFrames(anim) * self.randGen.random()))
        self.loop(anim, restart=0)
        self.setPlayRate(animMultiplier, anim)
        self.playingAnim = anim
        self.setActiveShadow(1)

    def exitNeutral(self):
        self.stop()

    def enterVictory(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = []):
        anim = 'victory'
        frame = int(ts * self.getFrameRate(anim) * animMultiplier)
        self.pose(anim, frame)
        self.loop('victory', restart=0)
        self.setPlayRate(animMultiplier, 'victory')
        self.playingAnim = anim
        self.setActiveShadow(0)

    def exitVictory(self):
        self.cleanupAllAuraTracks()
        self.makeContentSync(0)
        self.clearAllToonStatusEffects()
        self.stop()

    def enterHappy(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = []):
        self.playingAnim = None
        self.playingRate = None
        self.standWalkRunReverse = (('neutral', 1.0),
         ('walk', 1.0),
         ('run', 1.0),
         ('walk', -1.0))
        self.setSpeed(self.forwardSpeed, self.rotateSpeed)
        self.setActiveShadow(1)

    def exitHappy(self):
        self.standWalkRunReverse = None
        self.stop()
        self.motion.exit()

    def enterSad(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = []):
        self.playingAnim = 'sad'
        self.playingRate = None
        self.standWalkRunReverse = (('sad-neutral', 1.0),
         ('sad-walk', 1.2),
         ('sad-walk', 1.2),
         ('sad-walk', -1.0))
        self.setSpeed(0, 0)
        Emote.globalEmote.disableBody(self, 'toon, enterSad')
        self.setActiveShadow(1)
        if self.isLocal():
            self.controlManager.disableAvatarJump()

    def exitSad(self):
        self.cleanupAllAuraTracks()
        self.makeContentSync(0)
        self.clearAllToonStatusEffects()
        self.standWalkRunReverse = None
        self.stop()
        self.motion.exit()
        Emote.globalEmote.releaseBody(self, 'toon, exitSad')
        if self.isLocal():
            self.controlManager.enableAvatarJump()

    def enterCatching(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = []):
        self.playingAnim = None
        self.playingRate = None
        self.standWalkRunReverse = (('catch-neutral', 1.0),
         ('catch-run', 1.0),
         ('catch-run', 1.0),
         ('catch-run', -1.0))
        self.setSpeed(self.forwardSpeed, self.rotateSpeed)
        self.setActiveShadow(1)

    def exitCatching(self):
        self.standWalkRunReverse = None
        self.stop()
        self.motion.exit()

    def enterCatchEating(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = []):
        self.playingAnim = None
        self.playingRate = None
        self.standWalkRunReverse = (('catch-eatneutral', 1.0),
         ('catch-eatnrun', 1.0),
         ('catch-eatnrun', 1.0),
         ('catch-eatnrun', -1.0))
        self.setSpeed(self.forwardSpeed, self.rotateSpeed)
        self.setActiveShadow(0)

    def exitCatchEating(self):
        self.standWalkRunReverse = None
        self.stop()
        self.motion.exit()

    def enterWalk(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = []):
        self.loop('walk')
        self.setPlayRate(animMultiplier, 'walk')
        self.setActiveShadow(1)

    def exitWalk(self):
        self.stop()

    def getJumpDuration(self):
        if self.playingAnim == 'neutral':
            return self.getDuration('jump', 'legs')
        else:
            return self.getDuration('running-jump', 'legs')

    def enterJump(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = []):
        if self.playingAnim == 'neutral':
            anim = 'jump'
        else:
            anim = 'running-jump'
        self.playingAnim = anim
        self.setPlayRate(animMultiplier, anim)
        self.play(anim)
        self.setActiveShadow(1)

    def exitJump(self):
        self.stop()
        self.playingAnim = 'neutral'

    def enterJumpSquat(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = []):
        if self.playingAnim == 'neutral':
            anim = 'jump-squat'
        else:
            anim = 'running-jump-squat'
        self.playingAnim = anim
        self.setPlayRate(animMultiplier, anim)
        self.play(anim)
        self.setActiveShadow(1)

    def exitJumpSquat(self):
        self.stop()
        self.playingAnim = 'neutral'

    def enterJumpAirborne(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = []):
        if self.playingAnim == 'neutral' or self.forceJumpIdle:
            anim = 'jump-idle'
        else:
            anim = 'running-jump-idle'
        self.playingAnim = anim
        self.setPlayRate(animMultiplier, anim)
        self.loop(anim)
        self.setActiveShadow(1)

    def exitJumpAirborne(self):
        self.stop()
        self.playingAnim = 'neutral'

    def enterJumpLand(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = []):
        if self.playingAnim == 'running-jump-idle':
            anim = 'running-jump-land'
            skipStart = 0.2
        else:
            anim = 'jump-land'
            skipStart = 0.0
        self.playingAnim = anim
        self.setPlayRate(animMultiplier, anim)
        self.play(anim)
        self.setActiveShadow(1)

    def exitJumpLand(self):
        self.stop()
        self.playingAnim = 'neutral'

    def enterRun(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = []):
        self.loop('run')
        self.setPlayRate(animMultiplier, 'run')
        Emote.globalEmote.disableBody(self, 'toon, enterRun')
        self.setActiveShadow(1)

    def exitRun(self):
        self.stop()
        Emote.globalEmote.releaseBody(self, 'toon, exitRun')

    def enterSwim(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = []):
        Emote.globalEmote.disableAll(self, 'enterSwim')
        self.playingAnim = 'swim'
        self.loop('swim')
        self.setPlayRate(animMultiplier, 'swim')
        self.getGeomNode().setP(-89.0)
        self.dropShadow.hide()
        if self.isLocal():
            self.book.obscureButton(1) #this hides stickerbook when in water
            self.useSwimControls()
        self.nametag3d.setPos(0, -2, 1)
        self.startBobSwimTask()
        self.setActiveShadow(0)

    def enterCringe(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = []):
        self.loop('cringe')
        self.getGeomNode().setPos(0, 0, -2)
        self.setPlayRate(animMultiplier, 'swim')

    def exitCringe(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = []):
        self.stop()
        self.getGeomNode().setPos(0, 0, 0)
        self.playingAnim = 'neutral'
        self.setPlayRate(animMultiplier, 'swim')

    def enterDive(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = []):
        self.loop('swim')
        if hasattr(self.getGeomNode(), 'setPos'):
            self.getGeomNode().setPos(0, 0, -2)
            self.setPlayRate(animMultiplier, 'swim')
            self.setActiveShadow(0)
            self.dropShadow.hide()
            self.nametag3d.setPos(0, -2, 1)

    def exitDive(self):
        self.stop()
        self.getGeomNode().setPos(0, 0, 0)
        self.playingAnim = 'neutral'
        self.dropShadow.show()
        self.nametag3d.setPos(0, 0, self.height + 0.5)

    def enterSwimHold(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = []):
        self.getGeomNode().setPos(0, 0, -2)
        self.nametag3d.setPos(0, -2, 1)
        self.pose('swim', 55)

    def exitSwimHold(self):
        self.stop()
        self.getGeomNode().setPos(0, 0, 0)
        self.playingAnim = 'neutral'
        self.dropShadow.show()
        self.nametag3d.setPos(0, 0, self.height + 0.5)

    def exitSwim(self):
        self.stop()
        self.playingAnim = 'neutral'
        self.stopBobSwimTask()
        self.getGeomNode().setPosHpr(0, 0, 0, 0, 0, 0)
        self.dropShadow.show()
        if self.isLocal():
            self.useWalkControls()
            self.book.obscureButton(False) #this unhides stickerbook
        self.nametag3d.setPos(0, 0, self.height + 0.5)
        Emote.globalEmote.releaseAll(self, 'exitSwim')

    def startBobSwimTask(self):
        if getattr(self, 'swimBob', None):
            self.swimBob.finish()
            self.swimBob = None
        self.nametag3d.setZ(5.0)
        geomNode = self.getGeomNode()
        geomNode.setZ(4.0)
        self.swimBob = Sequence(
            geomNode.posInterval(1, Point3(0, -3, 3), startPos=Point3(0, -3, 4), blendType='easeInOut'),
            geomNode.posInterval(1, Point3(0, -3, 4), startPos=Point3(0, -3, 3), blendType='easeInOut'))
        self.swimBob.loop()

    def stopBobSwimTask(self):
        swimBob = getattr(self, 'swimBob', None)
        if swimBob:
            swimBob.finish()
        self.getGeomNode().setPos(0, 0, 0)
        self.nametag3d.setZ(1.0)

    def enterOpenBook(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = []):
        Emote.globalEmote.disableAll(self, 'enterOpenBook')
        self.playingAnim = 'openBook'
        self.stopLookAround()
        self.lerpLookAt(Point3(0, 1, -2))
        bookTracks = Parallel()
        for bookActor in self.getBookActors():
            bookTracks.append(ActorInterval(bookActor, 'book', startTime=1.2, endTime=1.5))

        bookTracks.append(ActorInterval(self, 'book', startTime=1.2, endTime=1.5))
        if hasattr(self, 'uniqueName'):
            trackName = self.uniqueName('openBook')
        else:
            trackName = 'openBook'
        self.track = Sequence(Func(self.showBooks), bookTracks, Wait(0.1), name=trackName)
        if callback:
            self.track.setDoneEvent(self.track.getName())
            self.acceptOnce(self.track.getName(), callback, extraArgs)
        self.track.start(ts)
        self.setActiveShadow(0)

    def exitOpenBook(self):
        self.playingAnim = 'neutralob'
        if self.track != None:
            self.ignore(self.track.getName())
            self.track.finish()
            DelayDelete.cleanupDelayDeletes(self.track)
            self.track = None
        
        self.hideBooks()
        self.startLookAround()
        Emote.globalEmote.releaseAll(self, 'exitOpenBook')

    def enterReadBook(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = []):
        Emote.globalEmote.disableBody(self, 'enterReadBook')
        self.playingAnim = 'readBook'
        self.stopLookAround()
        self.lerpLookAt(Point3(0, 1, -2))
        self.showBooks()
        for bookActor in self.getBookActors():
            bookActor.pingpong('book', fromFrame=38, toFrame=118)

        self.pingpong('book', fromFrame=38, toFrame=118)
        self.setActiveShadow(0)

    def exitReadBook(self):
        self.playingAnim = 'neutralrb'
        self.hideBooks()
        for bookActor in self.getBookActors():
            bookActor.stop()

        self.startLookAround()
        Emote.globalEmote.releaseBody(self, 'exitReadBook')

    def enterCloseBook(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = []):
        Emote.globalEmote.disableAll(self, 'enterCloseBook')
        self.playingAnim = 'closeBook'
        bookTracks = Parallel()
        for bookActor in self.getBookActors():
            bookTracks.append(ActorInterval(bookActor, 'book', startTime=4.96, endTime=6.5))

        bookTracks.append(ActorInterval(self, 'book', startTime=4.96, endTime=6.5))
        if hasattr(self, 'uniqueName'):
            trackName = self.uniqueName('closeBook')
        else:
            trackName = 'closeBook'
        self.track = Sequence(Func(self.showBooks), bookTracks, Func(self.hideBooks), name=trackName)
        if callback:
            self.track.setDoneEvent(self.track.getName())
            self.acceptOnce(self.track.getName(), callback, extraArgs)
        self.track.start(ts)
        self.setActiveShadow(0)

    def exitCloseBook(self):
        self.playingAnim = 'neutralcb'
        if self.track != None:
            self.ignore(self.track.getName())
            self.track.finish()
            DelayDelete.cleanupDelayDeletes(self.track)
            self.track = None
        
        Emote.globalEmote.releaseAll(self, 'exitCloseBook')
        
    def getSoundTeleport(self):
        if not self.soundTeleport:
            self.soundTeleport = base.loader.loadSfx('phase_3.5/audio/sfx/AV_teleport.ogg')
        return self.soundTeleport

    def getTeleportOutTrack(self, autoFinishTrack = 1):

        def showHoles(holes, hands):
            for hole, hand in zip(holes, hands):
                hole.reparentTo(hand)

        def reparentHoles(holes, toon):
            holes[0].reparentTo(toon)
            holes[1].detachNode()
            holes[2].detachNode()
            holes[0].setBin('shadow', 0)
            holes[0].setDepthTest(0)
            holes[0].setDepthWrite(0)

        def cleanupHoles(holes):
            holes[0].detachNode()
            holes[0].clearBin()
            holes[0].clearDepthTest()
            holes[0].clearDepthWrite()

        holes = self.getHoleActors()
        hands = self.getRightHands()
        holeTrack = Track((0.0, Func(showHoles, holes, hands)), (0.5, SoundInterval(self.getSoundTeleport(), node=self)), (1.708, Func(reparentHoles, holes, self)), (3.4, Func(cleanupHoles, holes)))
        if hasattr(self, 'uniqueName'):
            trackName = self.uniqueName('teleportOut')
        else:
            trackName = 'teleportOut'
        track = Parallel(holeTrack, name=trackName, autoFinish=autoFinishTrack)
        for hole in holes:
            track.append(ActorInterval(hole, 'hole', duration=3.4))

        track.append(ActorInterval(self, 'teleport', duration=3.4))
        return track

    def startQuestMap(self):
        pass

    def stopQuestMap(self):
        pass

    def enterTeleportOut(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = []):
        name = self.name
        if hasattr(self, 'doId'):
            name += '-' + str(self.doId)
        self.notify.debug('enterTeleportOut %s' % name)
        if self.ghostMode or self.isDisguised:
            if callback:
                callback(*extraArgs)
            return
        self.playingAnim = 'teleport'
        Emote.globalEmote.disableAll(self, 'enterTeleportOut')
        if self.isLocal():
            autoFinishTrack = 0
        else:
            autoFinishTrack = 1
        self.track = self.getTeleportOutTrack(autoFinishTrack)
        self.track.setDoneEvent(self.track.getName())
        self.acceptOnce(self.track.getName(), self.finishTeleportOut, [callback, extraArgs])
        holeClip = PlaneNode('holeClip')
        self.holeClipPath = self.attachNewNode(holeClip)
        self.getGeomNode().setClipPlane(self.holeClipPath)
        self.nametag3d.setClipPlane(self.holeClipPath)
        self.track.start(ts)
        self.setActiveShadow(0)

    def finishTeleportOut(self, callback = None, extraArgs = []):
        name = self.name
        if hasattr(self, 'doId'):
            name += '-' + str(self.doId)
        self.notify.debug('finishTeleportOut %s' % name)
        if self.track != None:
            self.ignore(self.track.getName())
            self.track.finish()
            DelayDelete.cleanupDelayDeletes(self.track)
            self.track = None
        if hasattr(self, 'animFSM'):
            self.animFSM.request('TeleportedOut')
        if callback:
            callback(*extraArgs)

    def exitTeleportOut(self):
        name = self.name
        if hasattr(self, 'doId'):
            name += '-' + str(self.doId)
       
        self.notify.debug('exitTeleportOut %s' % name)
        if self.track != None:
            self.ignore(self.track.getName())
            self.track.finish()
            self.track = None
        
        geomNode = self.getGeomNode()
        if geomNode and not geomNode.isEmpty():
            self.getGeomNode().clearClipPlane()
       
        if self.nametag3d and not self.nametag3d.isEmpty():
            self.nametag3d.clearClipPlane()
        
        if self.holeClipPath:
            self.holeClipPath.removeNode()
            self.holeClipPath = None
        
        Emote.globalEmote.releaseAll(self, 'exitTeleportOut')
        if self and not self.isEmpty():
            self.show()

    def enterTeleportedOut(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = []):
        self.setActiveShadow(0)

    def exitTeleportedOut(self):
        pass

    def getDiedInterval(self, autoFinishTrack = 1):
        sound = loader.loadSfx('phase_5/audio/sfx/ENC_Lose.ogg')
        if hasattr(self, 'uniqueName'):
            trackName = self.uniqueName('died')
        else:
            trackName = 'died'
        ival = Sequence(Func(Emote.globalEmote.disableBody, self), Func(self.sadEyes), Func(self.blinkEyes), Track((0, ActorInterval(self, 'lose')), (2, SoundInterval(sound, node=self)), (5.333, self.scaleInterval(1.5, VBase3(0.01, 0.01, 0.01), blendType='easeInOut'))), Func(self.detachNode), Func(self.setScale, 1, 1, 1), Func(self.normalEyes), Func(self.blinkEyes), Func(Emote.globalEmote.releaseBody, self), name=trackName, autoFinish=autoFinishTrack)
        return ival

    def enterDied(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = []):
        if self.ghostMode:
            if callback:
                callback(*extraArgs)
        if self.isDisguised:
            self.takeOffSuit()
        self.playingAnim = 'lose'
        Emote.globalEmote.disableAll(self, 'enterDied')
        if self.isLocal():
            autoFinishTrack = 0
        else:
            autoFinishTrack = 1
        if hasattr(self, 'jumpLandAnimFixTask') and self.jumpLandAnimFixTask:
            self.jumpLandAnimFixTask.remove()
            self.jumpLandAnimFixTask = None
        self.track = self.getDiedInterval(autoFinishTrack)
        if callback:
            self.track = Sequence(self.track, Func(callback, *extraArgs), autoFinish=autoFinishTrack)
        self.track.start(ts)
        self.setActiveShadow(0)

    def finishDied(self, callback = None, extraArgs = []):
        if self.track != None:
            self.ignore(self.track.getName())
            self.track.finish()
            DelayDelete.cleanupDelayDeletes(self.track)
            self.track = None
        if hasattr(self, 'animFSM'):
            self.animFSM.request('TeleportedOut')
        if callback:
            callback(*extraArgs)

    def exitDied(self):
        if self.track != None:
            self.ignore(self.track.getName())
            self.track.finish()
            DelayDelete.cleanupDelayDeletes(self.track)
            self.track = None
        Emote.globalEmote.releaseAll(self, 'exitDied')
        self.show()

    def getPlaygroundDiedInterval(self, autoFinishTrack = 1):
        sound = loader.loadSfx('phase_5/audio/sfx/ENC_Lose.ogg')
        if hasattr(self, 'uniqueName'):
            trackName = self.uniqueName('playgroundDied')
        else:
            trackName = 'playgroundDied'
        ival = Sequence(Func(self.sadEyes), Func(self.blinkEyes), Track((0, ActorInterval(self, 'lose', startFrame=0, endFrame=89)), (2, Func(base.playSfx, sound, node=self))), Func(self.blinkEyes), Func(self.normalEyes), name=trackName, autoFinish=autoFinishTrack)
        return ival

    def enterPlaygroundDied(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = []):
        if self.ghostMode:
            if callback:
                callback(*extraArgs)
            return
        if self.isDisguised:
            self.takeOffSuit()
        self.playingAnim = 'lose'
        Emote.globalEmote.disableAll(self, 'enterPlaygroundDied')
        if self.isLocal():
            autoFinishTrack = 0
        else:
            autoFinishTrack = 1
        if hasattr(self, 'jumpLandAnimFixTask') and self.jumpLandAnimFixTask:
            self.jumpLandAnimFixTask.remove()
            self.jumpLandAnimFixTask = None
        self.track = self.getPlaygroundDiedInterval(autoFinishTrack)
        if callback:
            self.track = Sequence(self.track, Func(callback, *extraArgs), autoFinish=autoFinishTrack)
        self.track.start(ts)
        self.setActiveShadow(0)

    def finishPlaygroundDied(self, callback = None, extraArgs = []):
        if self.track != None:
            self.ignore(self.track.getName())
            self.track.finish()
            DelayDelete.cleanupDelayDeletes(self.track)
            self.track = None
        if callback:
            callback(*extraArgs)

    def exitPlaygroundDied(self):
        if self.track != None:
            self.ignore(self.track.getName())
            self.track.finish()
            DelayDelete.cleanupDelayDeletes(self.track)
            self.track = None
        Emote.globalEmote.releaseAll(self, 'exitPlaygroundDied')

    def getTeleportInTrack(self):
        hole = self.getHoleActors()[0]
        hole.setBin('shadow', 0)
        hole.setDepthTest(0)
        hole.setDepthWrite(0)
        holeTrack = Sequence()
        holeTrack.append(Func(hole.reparentTo, self))
        pos = Point3(0, -2.4, 0)
        holeTrack.append(Func(hole.setPos, self, pos))
        holeTrack.append(ActorInterval(hole, 'hole', startTime=3.4, endTime=3.1))
        holeTrack.append(Wait(0.6))
        holeTrack.append(ActorInterval(hole, 'hole', startTime=3.1, endTime=3.4))

        def restoreHole(hole):
            hole.setPos(0, 0, 0)
            hole.detachNode()
            hole.clearBin()
            hole.clearDepthTest()
            hole.clearDepthWrite()

        holeTrack.append(Func(restoreHole, hole))
        toonTrack = Sequence(Wait(0.3), Func(self.getGeomNode().show), Func(self.nametag3d.show), ActorInterval(self, 'jump', startTime=0.45))
        if hasattr(self, 'uniqueName'):
            trackName = self.uniqueName('teleportIn')
        else:
            trackName = 'teleportIn'
        return Parallel(holeTrack, toonTrack, name=trackName)

    def enterTeleportIn(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = []):
        if self.ghostMode or self.isDisguised:
            if callback:
                callback(*extraArgs)
            return
        self.show()
        self.playingAnim = 'teleport'
        Emote.globalEmote.disableAll(self, 'enterTeleportIn')
        self.pose('teleport', self.getNumFrames('teleport') - 1)
        self.getGeomNode().hide()
        self.nametag3d.hide()
        self.track = self.getTeleportInTrack()
        if callback:
            self.track.setDoneEvent(self.track.getName())
            self.acceptOnce(self.track.getName(), callback, extraArgs)
        self.track.start(ts)
        self.setActiveShadow(0)

    def exitTeleportIn(self):
        self.playingAnim = None
        if self.track != None:
            self.ignore(self.track.getName())
            self.track.finish()
            DelayDelete.cleanupDelayDeletes(self.track)
            self.track = None
        if not self.ghostMode and not self.isDisguised:
            self.getGeomNode().show()
            self.nametag3d.show()
        Emote.globalEmote.releaseAll(self, 'exitTeleportIn')

    def enterSitStart(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = []):
        Emote.globalEmote.disableBody(self)
        self.playingAnim = 'sit-start'
        if self.isLocal():
            self.track = Sequence(ActorInterval(self, 'sit-start'), Func(self.b_setAnimState, 'Sit', animMultiplier))
        else:
            self.track = Sequence(ActorInterval(self, 'sit-start'))
        self.track.start(ts)
        self.setActiveShadow(0)

    def exitSitStart(self):
        self.playingAnim = 'neutral'
        if self.track != None:
            self.track.finish()
            DelayDelete.cleanupDelayDeletes(self.track)
            self.track = None
        Emote.globalEmote.releaseBody(self)

    def enterSit(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = []):
        Emote.globalEmote.disableBody(self)
        self.playingAnim = 'sit'
        self.loop('sit')
        self.setActiveShadow(0)

    def exitSit(self):
        self.playingAnim = 'neutral'
        Emote.globalEmote.releaseBody(self)

    def enterSleep(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = []):
        self.stopLookAround()
        self.stopBlink()
        self.closeEyes()
        self.lerpLookAt(Point3(0, 1, -4))
        self.loop('neutral')
        self.setPlayRate(animMultiplier * 0.4, 'neutral')
        self.setChatAbsolute(SLEEP_STRING, CFThought)
        if self == base.localAvatar:
            self.notify.debug('Adding timeout task to Toon.')
            taskMgr.doMethodLater(self.afkTimeout, self.__handleAfkTimeout, self.uniqueName('afkTimeout'))
        self.setActiveShadow(0)

    def __handleAfkTimeout(self, task):
        self.notify.debug('Handling timeout task on Toon.')
        self.ignore('wakeup')
        self.takeOffSuit()
        base.cr.playGame.getPlace().fsm.request('final')
        self.b_setAnimState('TeleportOut', 1, self.__handleAfkExitTeleport, [0])
        return Task.done

    def __handleAfkExitTeleport(self, requestStatus):
        self.notify.info('closing shard...')
        base.cr.gameFSM.request('closeShard', ['afkTimeout'])

    def exitSleep(self):
        taskMgr.remove(self.uniqueName('afkTimeout'))
        self.startLookAround()
        self.openEyes()
        self.startBlink()
        if config.GetBool('stuck-sleep-fix', 1):
            doClear = SLEEP_STRING in (self.nametag.getChatText(), self.nametag.getStompChatText())
        else:
            doClear = self.nametag.getChatText() == SLEEP_STRING
        if doClear:
            self.setChatAbsolute('', CFThought)
        self.lerpLookAt(Point3(0, 1, 0), time=0.25)
        self.stop()

    def enterPush(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = []):
        Emote.globalEmote.disableBody(self)
        self.playingAnim = 'push'
        self.track = Sequence(ActorInterval(self, 'push'))
        self.track.loop()
        self.setActiveShadow(1)

    def exitPush(self):
        self.playingAnim = 'neutral'
        if self.track != None:
            self.track.finish()
            DelayDelete.cleanupDelayDeletes(self.track)
            self.track = None
        Emote.globalEmote.releaseBody(self)

    def enterEmote(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = []):
        if len(extraArgs) > 0:
            emoteIndex = extraArgs[0]
        else:
            return
        self.playingAnim = None
        self.playingRate = None
        self.standWalkRunReverse = (('neutral', 1.0),
         ('walk', 1.0),
         ('run', 1.0),
         ('walk', -1.0))
        self.setSpeed(self.forwardSpeed, self.rotateSpeed)
        if self.isLocal() and emoteIndex != Emote.globalEmote.EmoteSleepIndex:
            if self.sleepFlag:
                self.b_setAnimState('Happy', self.animMultiplier)
            self.wakeUp()
        duration = 0
        self.emoteTrack, duration = Emote.globalEmote.doEmote(self, emoteIndex, ts)
        self.setActiveShadow(1)

    def doEmote(self, emoteIndex, animMultiplier = 1, ts = 0, callback = None, extraArgs = []):
        if not self.isLocal():
            if base.cr.avatarFriendsManager.checkIgnored(self.doId):
                return
        duration = 0
        if self.isLocal():
            self.wakeUp()
            if self.hasTrackAnimToSpeed():
                self.trackAnimToSpeed(None)
        self.emoteTrack, duration = Emote.globalEmote.doEmote(self, emoteIndex, ts)

    def __returnToLastAnim(self, task):
        if self.playingAnim:
            self.loop(self.playingAnim)
        elif self.hp > 0:
            self.loop('neutral')
        else:
            self.loop('sad-neutral')
        return Task.done

    def __finishEmote(self, task):
        if self.isLocal():
            if self.hp > 0:
                self.b_setAnimState('Happy')
            else:
                self.b_setAnimState('Sad')
        return Task.done

    def exitEmote(self):
        self.stop()
        if self.emoteTrack != None:
            self.emoteTrack.finish()
            self.emoteTrack = None
        taskMgr.remove(self.taskName('finishEmote'))

    def enterSquish(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = []):
        Emote.globalEmote.disableAll(self)
        sound = loader.loadSfx('phase_9/audio/sfx/toon_decompress.ogg')
        lerpTime = 0.1
        node = self.getGeomNode().getChild(0)
        origScale = node.getScale()
        self.track = Sequence(LerpScaleInterval(node, lerpTime, VBase3(2, 2, 0.025), blendType='easeInOut'), Wait(1.0), Parallel(Sequence(Wait(0.4), LerpScaleInterval(node, lerpTime, VBase3(1.4, 1.4, 1.4), blendType='easeInOut'), LerpScaleInterval(node, lerpTime / 2.0, VBase3(0.8, 0.8, 0.8), blendType='easeInOut'), LerpScaleInterval(node, lerpTime / 3.0, origScale, blendType='easeInOut')), ActorInterval(self, 'jump', startTime=0.2), SoundInterval(sound)))
        self.track.start(ts)
        self.setActiveShadow(1)

    def exitSquish(self):
        self.playingAnim = 'neutral'
        if self.track != None:
            self.track.finish()
            DelayDelete.cleanupDelayDeletes(self.track)
            self.track = None
        Emote.globalEmote.releaseAll(self)

    def enterFallDown(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = []):
        self.playingAnim = 'fallDown'
        Emote.globalEmote.disableAll(self)
        self.track = Sequence(ActorInterval(self, 'slip-backward'), name='fallTrack')
        if callback:
            self.track.setDoneEvent(self.track.getName())
            self.acceptOnce(self.track.getName(), callback, extraArgs)
        self.track.start(ts)

    def exitFallDown(self):
        self.playingAnim = 'neutral'
        if self.track != None:
            self.ignore(self.track.getName())
            self.track.finish()
            DelayDelete.cleanupDelayDeletes(self.track)
            self.track = None
        Emote.globalEmote.releaseAll(self)

    def stunToon(self, ts = 0, callback = None, knockdown = 0):
        if not self.isStunned:
            if self.stunTrack:
                self.stunTrack.finish()
                self.stunTrack = None

            def setStunned(stunned):
                self.isStunned = stunned
                if self == base.localAvatar:
                    messenger.send('toonStunned-' + str(self.doId), [self.isStunned])

            node = self.getGeomNode()
            lerpTime = 0.5
            down = self.doToonColorScale(VBase4(1, 1, 1, 0.6), lerpTime)
            up = self.doToonColorScale(VBase4(1, 1, 1, 0.9), lerpTime)
            clear = self.doToonColorScale(self.defaultColorScale, lerpTime)
            track = Sequence(Func(setStunned, 1), down, up, down, up, down, up, down, clear, Func(self.restoreDefaultColorScale), Func(setStunned, 0))
            if knockdown:
                self.stunTrack = Parallel(ActorInterval(self, animName='slip-backward'), track)
            else:
                self.stunTrack = track
            self.stunTrack.start()

    def getPieces(self, *pieces):
        results = []
        for lodName in self.getLODNames():
            for partName, pieceNames in pieces:
                part = self.getPart(partName, lodName)
                if part:
                    if type(pieceNames) == types.StringType:
                        pieceNames = (pieceNames,)
                    for pieceName in pieceNames:
                        npc = part.findAllMatches('**/%s;+s' % pieceName)
                        for i in xrange(npc.getNumPaths()):
                            results.append(npc[i])

        return results

    def applyCheesyEffect(self, effect, lerpTime = 0):
        try:
            if self.effectTrack != None:
                self.effectTrack.finish()
                self.effectTrack = None
            if self.cheesyEffect != effect:
                oldEffect = self.cheesyEffect
                self.cheesyEffect = effect
                if oldEffect == ToontownGlobals.CENormal:
                    self.effectTrack = self.__doCheesyEffect(effect, lerpTime)
                elif effect == ToontownGlobals.CENormal:
                    self.effectTrack = self.__undoCheesyEffect(oldEffect, lerpTime)
                else:
                    self.effectTrack = Sequence(self.__undoCheesyEffect(oldEffect, lerpTime / 2.0), self.__doCheesyEffect(effect, lerpTime / 2.0))
                if self.effectTrack:
                    self.effectTrack.start()
        except:
            pass

    def reapplyCheesyEffect(self, lerpTime = 0):
        try:
            if self.effectTrack != None:
                self.effectTrack.finish()
                self.effectTrack = None
            effect = self.cheesyEffect
            self.effectTrack = Sequence(self.__undoCheesyEffect(effect, 0), self.__doCheesyEffect(effect, lerpTime))
            self.effectTrack.start()
        except:
            pass

    def clearCheesyEffect(self, lerpTime = 0):
        self.applyCheesyEffect(ToontownGlobals.CENormal, lerpTime=lerpTime)
        if self.effectTrack != None:
            self.effectTrack.finish()
            self.effectTrack = None

    def __doHeadScale(self, scale, lerpTime):
        if scale == None:
            scale = ToontownGlobals.toonHeadScales[self.style.getAnimal()]
        
        track = Parallel()
        if not self.getGeomNode():
            self.notify.warning("A error has occured when attempting to scale Toon!")
            return track
        if not self.headParts:
            return track
        
        for hi in xrange(self.headParts.getNumPaths()):
            head = self.headParts[hi]
            track.append(LerpScaleInterval(head, lerpTime, scale, blendType='easeInOut'))

        return track

    def __doLegsScale(self, scale, lerpTime):
        if scale == None:
            scale = 1
            invScale = 1
        else:
            invScale = 1.0 / scale
        track = Parallel()
        if not self.getGeomNode():
            self.notify.warning("A error has occured when attempting to scale Toon!")
            return track
        if not self.legsParts:
            return track
        for li in xrange(self.legsParts.getNumPaths()):
            legs = self.legsParts[li]
            torso = self.torsoParts[li]
            track.append(LerpScaleInterval(legs, lerpTime, scale, blendType='easeInOut'))
            track.append(LerpScaleInterval(torso, lerpTime, invScale, blendType='easeInOut'))

        return track

    def __doToonScale(self, scale, lerpTime):
        if scale == None:
            scale = 1
        if not self.getGeomNode():
            self.notify.warning("A error has occured when attempting to scale Toon!")
            return
        node = self.getGeomNode().getChild(0)
        track = Sequence(Parallel(LerpHprInterval(node, lerpTime, Vec3(0.0, 0.0, 0.0), blendType='easeInOut'), LerpScaleInterval(node, lerpTime, scale, blendType='easeInOut')), Func(self.resetHeight))
        return track

    def doToonColorScale(self, scale, lerpTime, keepDefault = 0):
        if keepDefault:
            self.defaultColorScale = scale
        if scale == None:
            scale = VBase4(1, 1, 1, 1)
        if not self.getGeomNode():
            self.notify.warning("A error has occured when attempting to colorscale Toon!")
            return
        node = self.getGeomNode()
        caps = self.getPieces(('torso', 'torso-bot-cap'))
        track = Sequence()
        track.append(Func(node.setTransparency, 1))
        if scale[3] != 1:
            for cap in caps:
                track.append(HideInterval(cap))

        track.append(LerpColorScaleInterval(node, lerpTime, scale, blendType='easeInOut'))
        if scale[3] == 1:
            track.append(Func(node.clearTransparency))
            for cap in caps:
                track.append(ShowInterval(cap))

        elif scale[3] == 0:
            track.append(Func(node.clearTransparency))
        return track

    def __doPumpkinHeadSwitch(self, lerpTime, toPumpkin):
        node = self.getGeomNode()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        dust = getDustCloudIval()
        track = Sequence()
        if toPumpkin:
            track.append(Func(self.stopBlink))
            track.append(Func(self.closeEyes))
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            def hideParts():
                self.notify.debug('hideParts')
                for head in self.headParts:
                    for p in head.getChildren():
                        if hasattr(self, 'pumpkins') and not self.pumpkins.hasPath(p):
                            p.hide()
                            p.setTag('pumpkin', 'enabled')

            track.append(Func(hideParts))
            track.append(Func(self.enablePumpkins, True))
        else:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            def showHiddenParts():
                self.notify.debug('showHiddenParts')
                for head in self.headParts:
                    for p in head.getChildren():
                        if not self.pumpkins.hasPath(p) and p.getTag('pumpkin') == 'enabled':
                            p.show()
                            p.setTag('pumpkin', 'disabled')

            track.append(Func(showHiddenParts))
            track.append(Func(self.enablePumpkins, False))
            track.append(Func(self.startBlink))
        return track
		
    def __doWireFrame(self):
        if not self.getGeomNode():
            self.notify.warning("A error has occured when attempting to wireframe Toon!")
            return
        node = self.getGeomNode()
        track = Sequence()
        track.append(Func(node.setRenderModeWireframe))
        return track
		
    def __doUnWireFrame(self):
        if not self.getGeomNode():
            self.notify.warning("A error has occured when attempting to unwireframe Toon!")
            return
        node = self.getGeomNode()
        track = Sequence()
        track.append(Func(node.setRenderModeFilled))
        return track

    def __doSnowManHeadSwitch(self, lerpTime, toSnowMan):
        node = self.getGeomNode()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=0)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        dust = getDustCloudIval()
        track = Sequence()
        if toSnowMan:
            track.append(Func(self.stopBlink))
            track.append(Func(self.closeEyes))
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            def hideParts():
                self.notify.debug('HidePaths')
                for hi in xrange(self.headParts.getNumPaths()):
                    head = self.headParts[hi]
                    parts = head.getChildren()
                    for pi in xrange(parts.getNumPaths()):
                        p = parts[pi]
                        if not p.isHidden():
                            p.hide()
                            p.setTag('snowman', 'enabled')

            track.append(Func(hideParts))
            track.append(Func(self.enableSnowMen, True))
        else:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            def showHiddenParts():
                self.notify.debug('ShowHiddenPaths')
                for hi in xrange(self.headParts.getNumPaths()):
                    head = self.headParts[hi]
                    parts = head.getChildren()
                    for pi in xrange(parts.getNumPaths()):
                        p = parts[pi]
                        if not self.snowMen.hasPath(p) and p.getTag('snowman') == 'enabled':
                            p.show()
                            p.setTag('snowman', 'disabled')

            track.append(Func(showHiddenParts))
            track.append(Func(self.enableSnowMen, False))
            track.append(Func(self.startBlink))
        return track

    def __doYesMan(self, lerpTime, toYesMan):
        node = self.getGeomNode()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=0)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        dust = getDustCloudIval()
        track = Sequence()
        if toYesMan:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.putOnSuit('ym')
        else:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.takeOffSuit()
        return track

    def __doDownsizer(self, lerpTime, toDownsizer):
        node = self.getGeomNode()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=0)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        dust = getDustCloudIval()
        track = Sequence()
        if toDownsizer:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.putOnSuit('ds')
        else:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.takeOffSuit()
        return track

    def __doMoverShaker(self, lerpTime, toMoverShaker):
        node = self.getGeomNode()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=0)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        dust = getDustCloudIval()
        track = Sequence()
        if toMoverShaker:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.putOnSuit('ms')
        else:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.takeOffSuit()
        return track

    def __doBigCheese(self, lerpTime, toBigCheese):
        node = self.getGeomNode()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=0)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        dust = getDustCloudIval()
        track = Sequence()
        if toBigCheese:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.putOnSuit('tbc')
        else:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.takeOffSuit()
        return track

    def __doGladHander(self, lerpTime, toGladHander):
        node = self.getGeomNode()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=0)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        dust = getDustCloudIval()
        track = Sequence()
        if toGladHander:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.putOnSuit('gh')
        else:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.takeOffSuit()
        return track

    def __doMingler(self, lerpTime, toMingler):
        node = self.getGeomNode()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=0)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        dust = getDustCloudIval()
        track = Sequence()
        if toMingler:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.putOnSuit('m')
        else:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.takeOffSuit()
        return track

    def __doFlunky(self, lerpTime, toFlunky):
        node = self.getGeomNode()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=0)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        dust = getDustCloudIval()
        track = Sequence()
        if toFlunky:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.putOnSuit('f')
        else:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.takeOffSuit()
        return track

    def __doTelemarketer(self, lerpTime, toTelemarketer):
        node = self.getGeomNode()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=0)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        dust = getDustCloudIval()
        track = Sequence()
        if toTelemarketer:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.putOnSuit('tm')
        else:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.takeOffSuit()
        return track

    def __doLoanShark(self, lerpTime, toLoanShark):
        node = self.getGeomNode()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=0)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        dust = getDustCloudIval()
        track = Sequence()
        if toLoanShark:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.putOnSuit('ls')
        else:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.takeOffSuit()
        return track

    def __doBigWig(self, lerpTime, toBigWig):
        node = self.getGeomNode()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=0)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        dust = getDustCloudIval()
        track = Sequence()
        if toBigWig:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.putOnSuit('bw')
        else:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.takeOffSuit()
        return track

    def __doMicroManager(self, lerpTime, toMicroManager):
        node = self.getGeomNode()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=0)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        dust = getDustCloudIval()
        track = Sequence()
        if toMicroManager:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.putOnSuit('mm')
        else:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.takeOffSuit()
        return track

    def __doBigFish(self, lerpTime, toBigFish):
        node = self.getGeomNode()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=0)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        dust = getDustCloudIval()
        track = Sequence()
        if toBigFish:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.putOnSuit('bfh')
        else:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.takeOffSuit()
        return track

    def __doCorporateRaider(self, lerpTime, toCorporateRaider):
        node = self.getGeomNode()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=0)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        dust = getDustCloudIval()
        track = Sequence()
        if toCorporateRaider:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.putOnSuit('cr')
        else:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.takeOffSuit()
        return track

    def __doHeadHoncho(self, lerpTime, toHeadHoncho):
        node = self.getGeomNode()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=0)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        dust = getDustCloudIval()
        track = Sequence()
        if toHeadHoncho:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.putOnSuit('hho')
        else:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.takeOffSuit()
        return track

    def __doDoubleTalker(self, lerpTime, toDoubleTalker):
        node = self.getGeomNode()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=0)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        dust = getDustCloudIval()
        track = Sequence()
        if toDoubleTalker:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.putOnSuit('dt')
        else:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.takeOffSuit()
        return track

    def __doTwoFace(self, lerpTime, toTwoFace):
        node = self.getGeomNode()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=0)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        dust = getDustCloudIval()
        track = Sequence()
        if toTwoFace:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.putOnSuit('tf')
        else:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.takeOffSuit()
        return track

    def __doConArtist(self, lerpTime, toConArtist):
        node = self.getGeomNode()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=0)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        dust = getDustCloudIval()
        track = Sequence()
        if toConArtist:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.putOnSuit('ca')
        else:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.takeOffSuit()
        return track

    def __doConnoisseur(self, lerpTime, toConnoisseur):
        node = self.getGeomNode()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=0)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        dust = getDustCloudIval()
        track = Sequence()
        if toConnoisseur:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.putOnSuit('cn')
        else:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.takeOffSuit()
        return track

    def __doSwindler(self, lerpTime, toSwindler):
        node = self.getGeomNode()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=0)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        dust = getDustCloudIval()
        track = Sequence()
        if toSwindler:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.putOnSuit('sw')
        else:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.takeOffSuit()
        return track

    def __doMiddleman(self, lerpTime, toMiddleman):
        node = self.getGeomNode()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=0)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        dust = getDustCloudIval()
        track = Sequence()
        if toMiddleman:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.putOnSuit('mdm')
        else:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.takeOffSuit()
        return track

    def __doToxicManager(self, lerpTime, toToxicManager):
        node = self.getGeomNode()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=0)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        dust = getDustCloudIval()
        track = Sequence()
        if toToxicManager:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.putOnSuit('txm')
        else:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.takeOffSuit()
        return track

    def __doMagnate(self, lerpTime, toMagnate):
        node = self.getGeomNode()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=0)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        dust = getDustCloudIval()
        track = Sequence()
        if toMagnate:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.putOnSuit('mg')
        else:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.takeOffSuit()
        return track

    def __doLegalEagle(self, lerpTime, toLegalEagle):
        node = self.getGeomNode()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=0)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        dust = getDustCloudIval()
        track = Sequence()
        if toLegalEagle:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.putOnSuit('le')
        else:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.takeOffSuit()
        return track

    def __doRobberBaron(self, lerpTime, toRobberBaron):
        node = self.getGeomNode()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=0)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        dust = getDustCloudIval()
        track = Sequence()
        if toRobberBaron:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.putOnSuit('rb')
        else:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.takeOffSuit()
        return track

    def __doColdCaller(self, lerpTime, toColdCaller):
        node = self.getGeomNode()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=0)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        dust = getDustCloudIval()
        track = Sequence()
        if toColdCaller:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.putOnSuit('cc')
        else:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.takeOffSuit()
        return track

    def __doShortChange(self, lerpTime, toShortChange):
        node = self.getGeomNode()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=0)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        dust = getDustCloudIval()
        track = Sequence()
        if toShortChange:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.putOnSuit('sc')
        else:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.takeOffSuit()
        return track

    def __doBloodsucker(self, lerpTime, toBloodsucker):
        node = self.getGeomNode()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=0)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        dust = getDustCloudIval()
        track = Sequence()
        if toBloodsucker:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.putOnSuit('b')
        else:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.takeOffSuit()
        return track

    def __doNameDropper(self, lerpTime, toNameDropper):
        node = self.getGeomNode()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=0)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        dust = getDustCloudIval()
        track = Sequence()
        if toNameDropper:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.putOnSuit('nd')
        else:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.takeOffSuit()
        return track

    def __doHeadHunter(self, lerpTime, toHeadHunter):
        node = self.getGeomNode()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=0)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        dust = getDustCloudIval()
        track = Sequence()
        if toHeadHunter:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.putOnSuit('hh')
        else:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.takeOffSuit()
        return track

    def __doHollywood(self, lerpTime, toHollywood):
        node = self.getGeomNode()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=0)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        dust = getDustCloudIval()
        track = Sequence()
        if toHollywood:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.putOnSuit('mh')
        else:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.takeOffSuit()
        return track

    def __doPencilPusher(self, lerpTime, toPencilPusher):
        node = self.getGeomNode()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=0)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        dust = getDustCloudIval()
        track = Sequence()
        if toPencilPusher:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.putOnSuit('p')
        else:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.takeOffSuit()
        return track

    def __doMoneyBags(self, lerpTime, toMoneyBags):
        node = self.getGeomNode()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=0)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        dust = getDustCloudIval()
        track = Sequence()
        if toMoneyBags:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.putOnSuit('mb')
        else:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.takeOffSuit()
        return track

    def __doSpinDoctor(self, lerpTime, toSpinDoctor):
        node = self.getGeomNode()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=0)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        dust = getDustCloudIval()
        track = Sequence()
        if toSpinDoctor:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.putOnSuit('sd')
        else:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.takeOffSuit()
        return track

    def __doAmbulanceChaser(self, lerpTime, toAmbulanceChaser):
        node = self.getGeomNode()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=0)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        dust = getDustCloudIval()
        track = Sequence()
        if toAmbulanceChaser:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.putOnSuit('ac')
        else:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.takeOffSuit()
        return track

    def __doNumberCruncher(self, lerpTime, toNumberCruncher):
        node = self.getGeomNode()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=0)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        dust = getDustCloudIval()
        track = Sequence()
        if toNumberCruncher:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.putOnSuit('nc')
        else:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.takeOffSuit()
        return track

    def __doPennyPincher(self, lerpTime, toPennyPincher):
        node = self.getGeomNode()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=0)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        dust = getDustCloudIval()
        track = Sequence()
        if toPennyPincher:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.putOnSuit('pp')
        else:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.takeOffSuit()
        return track

    def __doTightwad(self, lerpTime, toTightwad):
        node = self.getGeomNode()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=0)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        dust = getDustCloudIval()
        track = Sequence()
        if toTightwad:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.putOnSuit('tw')
        else:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.takeOffSuit()
        return track

    def __doBeanCounter(self, lerpTime, toBeanCounter):
        node = self.getGeomNode()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=0)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        dust = getDustCloudIval()
        track = Sequence()
        if toBeanCounter:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.putOnSuit('bc')
        else:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.takeOffSuit()
        return track

    def __doBackStabber(self, lerpTime, toBackStabber):
        node = self.getGeomNode()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=0)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        dust = getDustCloudIval()
        track = Sequence()
        if toBackStabber:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.putOnSuit('bs')
        else:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.takeOffSuit()
        return track

    def __doBottomFeeder(self, lerpTime, toBottomFeeder):
        node = self.getGeomNode()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=0)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        dust = getDustCloudIval()
        track = Sequence()
        if toBottomFeeder:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.putOnSuit('bf')
        else:
            if lerpTime > 0.0:
                track.append(Func(dust.start))
                track.append(Wait(0.5))
            else:
                dust.finish()

            self.takeOffSuit()
        return track

    def __doGreenToon(self, lerpTime, toGreen):
        track = Sequence()
        greenTrack = Parallel()
        if not self.getGeomNode():
            self.notify.warning("A error has occured when attempting to give a toon the luck of the Irish!")
            return

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        if lerpTime > 0.0:
            dust = getDustCloudIval()
            track.append(Func(dust.start))
            track.append(Wait(0.5))
        if toGreen:
            skinGreen = VBase4(76 / 255.0, 240 / 255.0, 84 / 255.0, 1)
            muzzleGreen = VBase4(4 / 255.0, 205 / 255.0, 90 / 255.0, 1)
            gloveGreen = VBase4(14 / 255.0, 173 / 255.0, 40 / 255.0, 1)
            greenTrack.append(self.__colorToonSkin(skinGreen, lerpTime))
            greenTrack.append(self.__colorToonEars(skinGreen, muzzleGreen, lerpTime))
            greenTrack.append(self.__colorScaleToonMuzzle(muzzleGreen, lerpTime))
            greenTrack.append(self.__colorToonGloves(gloveGreen, lerpTime))
        else:
            greenTrack.append(self.__colorToonSkin(None, lerpTime))
            greenTrack.append(self.__colorToonEars(None, None, lerpTime))
            greenTrack.append(self.__colorScaleToonMuzzle(None, lerpTime))
            greenTrack.append(self.__colorToonGloves(None, lerpTime))
        track.append(greenTrack)
        return track
        
    def __colorToonSkin(self, color, lerpTime):
        if not self.getGeomNode():
            self.notify.warning("A error has occured when attempting to color a Toon's skin!")
            return
        track = Sequence()
        colorTrack = Parallel()
        torsoPieces = self.getPieces(('torso', ('arms', 'neck')))
        legPieces = self.getPieces(('legs', ('legs', 'feet')))
        headPieces = self.getPieces(('head', '*head*'))
        if color == None:
            armColor = self.style.getArmColor()
            legColor = self.style.getLegColor()
            headColor = self.style.getHeadColor()
        else:
            armColor = color
            legColor = color
            headColor = color
        for piece in torsoPieces:
            colorTrack.append(Func(piece.setColor, *armColor))

        for piece in legPieces:
            colorTrack.append(Func(piece.setColor, *legColor))

        for piece in headPieces:
            if 'hatNode' not in str(piece) and 'glassesNode' not in str(piece):
                colorTrack.append(Func(piece.setColor, *headColor))

        track.append(colorTrack)
        return track

    def __colorToonEars(self, color, colorScale, lerpTime):
        track = Sequence()
        earPieces = self.getPieces(('head', '*ear*'))
        if len(earPieces) == 0:
            return track
        colorTrack = Parallel()
        if earPieces[0].hasColor():
            if color == None:
                headColor = self.style.getHeadColor()
            else:
                headColor = color
            for piece in earPieces:
                colorTrack.append(Func(piece.setColor, *headColor))

        else:
            if colorScale == None:
                colorScale = VBase4(1, 1, 1, 1)
            for piece in earPieces:
                colorTrack.append(Func(piece.setColorScale, *colorScale))

        track.append(colorTrack)
        return track

    def __colorScaleToonMuzzle(self, scale, lerpTime):
        track = Sequence()
        colorTrack = Parallel()
        muzzlePieces = self.getPieces(('head', '*muzzle*'))
        if scale == None:
            scale = VBase4(1, 1, 1, 1)
        for piece in muzzlePieces:
            colorTrack.append(Func(piece.setColorScale, scale))

        track.append(colorTrack)
        return track

    def __colorToonGloves(self, color, lerpTime):
        track = Sequence()
        colorTrack = Parallel()
        glovePieces = self.getPieces(('torso', '*hands*'))
        if color == None:
            for piece in glovePieces:
                colorTrack.append(Func(piece.clearColor))

        else:
            for piece in glovePieces:
                colorTrack.append(Func(piece.setColor, color))

        track.append(colorTrack)
        return track

    def __doBigAndWhite(self, color, scale, lerpTime):
        track = Parallel()
        track.append(self.__doToonColor(color, lerpTime))
        track.append(self.__doToonScale(scale, lerpTime))
        return track

    def __doVirtual(self):
        track = Parallel()
        track.append(self.__doToonColor(VBase4(0.25, 0.25, 1.0, 1), 0.0))
        self.setPartsAdd(self.getHeadParts())
        self.setPartsAdd(self.getTorsoParts())
        self.setPartsAdd(self.getHipsParts())
        self.setPartsAdd(self.getLegsParts())
        return track

    def __doUnVirtual(self):
        track = Parallel()
        track.append(self.__doToonColor(None, 0.0))
        self.setPartsNormal(self.getHeadParts(), 1)
        self.setPartsNormal(self.getTorsoParts(), 1)
        self.setPartsNormal(self.getHipsParts(), 1)
        self.setPartsNormal(self.getLegsParts(), 1)
        return track

    def setPartsAdd(self, parts):
        actorCollection = parts
        for thingIndex in range(0, actorCollection.getNumPaths()):
            thing = actorCollection[thingIndex]
            if thing.getName() not in ('joint_attachMeter', 'joint_nameTag'):
                thing.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd))
                thing.setDepthWrite(False)
                self.setBin('fixed', 1)

    def setPartsNormal(self, parts, alpha = 0):
        actorCollection = parts
        for thingIndex in range(0, actorCollection.getNumPaths()):
            thing = actorCollection[thingIndex]
            if thing.getName() not in ('joint_attachMeter', 'joint_nameTag'):
                thing.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MNone))
                thing.setDepthWrite(True)
                self.setBin('default', 0)
                if alpha:
                    thing.setTransparency(1)
                    thing.setBin('transparent', 0)

    def __doToonGhostColorScale(self, scale, lerpTime, keepDefault = 0):
        if keepDefault:
            self.defaultColorScale = scale
        if scale == None:
            scale = VBase4(1, 1, 1, 1)
        if not self.getGeomNode():
            self.notify.warning("A error has occured when attempting to ghostify Toon!")
            return
        node = self.getGeomNode()
        caps = self.getPieces(('torso', 'torso-bot-cap'))
        track = Sequence()
        track.append(Func(node.setTransparency, 1))
        track.append(ShowInterval(node))
        if scale[3] != 1:
            for cap in caps:
                track.append(HideInterval(cap))

        track.append(LerpColorScaleInterval(node, lerpTime, scale, blendType='easeInOut'))
        if scale[3] == 1:
            track.append(Func(node.clearTransparency))
            for cap in caps:
                track.append(ShowInterval(cap))

        elif scale[3] == 0:
            track.append(Func(node.clearTransparency))
            track.append(HideInterval(node))
        return track

    def restoreDefaultColorScale(self):
        if not self.getGeomNode():
            self.notify.warning("A error has occured when attempting to restore color to Toon!")
            return
        node = self.getGeomNode()
        if node:
            if self.defaultColorScale:
                node.setColorScale(self.defaultColorScale)
                if self.defaultColorScale[3] != 1:
                    node.setTransparency(1)
                else:
                    node.clearTransparency()
            else:
                node.clearColorScale()
                node.clearTransparency()

    def __doToonColor(self, color, lerpTime):
        if not self.getGeomNode():
            self.notify.warning("A error has occured when attempting to color Toon!")
            return
        node = self.getGeomNode()
        if color == None:
            return Func(node.clearColor)
        else:
            return Func(node.setColor, color, 1)
        return

    def __doPartsColorScale(self, scale, lerpTime):
        if scale == None:
            scale = VBase4(1, 1, 1, 1)
        if not self.getGeomNode():
            self.notify.warning("A error has occured when attempting to colorscale parts!")
            return
        node = self.getGeomNode()
        pieces = self.getPieces(('torso', ('arms', 'neck')), ('legs', ('legs', 'feet')), ('head', '+GeomNode'))
        track = Sequence()
        track.append(Func(node.setTransparency, 1))
        for piece in pieces:
            if piece.getName()[:7] == 'muzzle-' and piece.getName()[-8:] != '-neutral':
                continue
            track.append(ShowInterval(piece))

        p1 = Parallel()
        for piece in pieces:
            if piece.getName()[:7] == 'muzzle-' and piece.getName()[-8:] != '-neutral':
                continue
            p1.append(LerpColorScaleInterval(piece, lerpTime, scale, blendType='easeInOut'))

        track.append(p1)
        if scale[3] == 1:
            track.append(Func(node.clearTransparency))
        elif scale[3] == 0:
            track.append(Func(node.clearTransparency))
            for piece in pieces:
                if piece.getName()[:7] == 'muzzle-' and piece.getName()[-8:] != '-neutral':
                    continue
                track.append(HideInterval(piece))

        self.generateHat()
        self.generateGlasses()
        return track

    def __doRogerDog(self, lerpTime, toRoger):
        track = Sequence()
        rogerTrack = Parallel()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        if lerpTime > 0.0:
            dust = getDustCloudIval()
            track.append(Func(dust.start))
            track.append(Wait(0.5))
            
        if toRoger:
            self.oldStyle = self.style.clone()
            self.oldHat = self.hat
            dna = ToonDNA.ToonDNA()
            dna.newToonFromProperties('dll', 'ls', 'l', 'm', 19, 0, 21, 8, 4, 0, 4, 0, 7, 15)
            rogerTrack.append(Func(self.updateToonDNA, dna, True))
            if hasattr(self, 'animFSM'):
                state = self.animFSM.getCurrentState()
                rogerTrack.append(Func(self.animFSM.request, 'off'))
                rogerTrack.append(Func(self.animFSM.request, state))
            rogerTrack.append(Func(self.nametag.setText, 'Roger Dog'))
            rogerTrack.append(Func(self.setHat, 24, 0, 0))
        else:
            rogerTrack.append(Func(self.updateToonDNA, self.oldStyle))
            if hasattr(self, 'animFSM'):
                state = self.animFSM.getCurrentState()
                rogerTrack.append(Func(self.animFSM.request, 'off'))
                rogerTrack.append(Func(self.animFSM.request, state))
            rogerTrack.append(Func(self.nametag.setText, self.nametag.name))
            rogerTrack.append(Func(self.setHat, self.oldHat[0], self.oldHat[1], self.oldHat[2]))
            rogerTrack.append(Func(self.generateToonAccessories))
        track.append(rogerTrack)
        return track

    def __doFlippy(self, lerpTime, toFlippy):
        track = Sequence()
        flippyTrack = Parallel()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        if lerpTime > 0.0:
            dust = getDustCloudIval()
            track.append(Func(dust.start))
            track.append(Wait(0.5))
            
        if toFlippy:
            self.oldStyle = self.style.clone()
            self.oldHat = self.hat
            dna = ToonDNA.ToonDNA()
            dna.newToonFromProperties('dss', 'ms', 'm', 'm', 17, 0, 17, 17, 3, 3, 3, 3, 7, 2)
            flippyTrack.append(Func(self.updateToonDNA, dna, True))
            if hasattr(self, 'animFSM'):
                state = self.animFSM.getCurrentState()
                flippyTrack.append(Func(self.animFSM.request, 'off'))
                flippyTrack.append(Func(self.animFSM.request, state))
            flippyTrack.append(Func(self.nametag.setText, 'Flippy'))
        else:
            flippyTrack.append(Func(self.updateToonDNA, self.oldStyle))
            if hasattr(self, 'animFSM'):
                state = self.animFSM.getCurrentState()
                flippyTrack.append(Func(self.animFSM.request, 'off'))
                flippyTrack.append(Func(self.animFSM.request, state))
            flippyTrack.append(Func(self.nametag.setText, self.nametag.name))
            flippyTrack.append(Func(self.setHat, self.oldHat[0], self.oldHat[1], self.oldHat[2]))
            flippyTrack.append(Func(self.generateToonAccessories))
        track.append(flippyTrack)
        return track

    def __doSurlee(self, lerpTime, toSurlee):
        track = Sequence()
        surleeTrack = Parallel()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        if lerpTime > 0.0:
            dust = getDustCloudIval()
            track.append(Func(dust.start))
            track.append(Wait(0.5))
            
        if toSurlee:
            self.oldStyle = self.style.clone()
            self.oldHat = self.hat
            dna = ToonDNA.ToonDNA()
            dna.newToonFromProperties('pls', 'ls', 'l', 'm', 9, 0, 9, 9, 98, 27, 86, 27, 38, 27)
            surleeTrack.append(Func(self.updateToonDNA, dna, True))
            if hasattr(self, 'animFSM'):
                state = self.animFSM.getCurrentState()
                surleeTrack.append(Func(self.animFSM.request, 'off'))
                surleeTrack.append(Func(self.animFSM.request, state))
            surleeTrack.append(Func(self.nametag.setText, 'Doctor Surlee'))
        else:
            surleeTrack.append(Func(self.updateToonDNA, self.oldStyle))
            if hasattr(self, 'animFSM'):
                state = self.animFSM.getCurrentState()
                surleeTrack.append(Func(self.animFSM.request, 'off'))
                surleeTrack.append(Func(self.animFSM.request, state))
            surleeTrack.append(Func(self.nametag.setText, self.nametag.name))
            surleeTrack.append(Func(self.setHat, self.oldHat[0], self.oldHat[1], self.oldHat[2]))
            surleeTrack.append(Func(self.generateToonAccessories))
        track.append(surleeTrack)
        return track

    def __doDimm(self, lerpTime, toDimm):
        track = Sequence()
        dimmTrack = Parallel()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        if lerpTime > 0.0:
            dust = getDustCloudIval()
            track.append(Func(dust.start))
            track.append(Wait(0.5))
            
        if toDimm:
            self.oldStyle = self.style.clone()
            self.oldHat = self.hat
            dna = ToonDNA.ToonDNA()
            dna.newToonFromProperties('fll', 'ss', 's', 'm', 15, 0, 15, 15, 99, 27, 86, 27, 39, 27)
            dimmTrack.append(Func(self.updateToonDNA, dna, True))
            if hasattr(self, 'animFSM'):
                state = self.animFSM.getCurrentState()
                dimmTrack.append(Func(self.animFSM.request, 'off'))
                dimmTrack.append(Func(self.animFSM.request, state))
            dimmTrack.append(Func(self.nametag.setText, 'Doctor Dimm'))
        else:
            dimmTrack.append(Func(self.updateToonDNA, self.oldStyle))
            if hasattr(self, 'animFSM'):
                state = self.animFSM.getCurrentState()
                dimmTrack.append(Func(self.animFSM.request, 'off'))
                dimmTrack.append(Func(self.animFSM.request, state))
            dimmTrack.append(Func(self.nametag.setText, self.nametag.name))
            dimmTrack.append(Func(self.setHat, self.oldHat[0], self.oldHat[1], self.oldHat[2]))
            dimmTrack.append(Func(self.generateToonAccessories))
        track.append(dimmTrack)
        return track

    def __doAlecTinn(self, lerpTime, toAlecTinn):
        track = Sequence()
        alecTrack = Parallel()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        if lerpTime > 0.0:
            dust = getDustCloudIval()
            track.append(Func(dust.start))
            track.append(Wait(0.5))
            
        if toAlecTinn:
            self.oldStyle = self.style.clone()
            self.oldHat = self.hat
            dna = ToonDNA.ToonDNA()
            dna.newToonFromProperties('cll', 'ls', 'l', 'm', 2, 0, 2, 2, 14, 9, 10, 9, 1, 14)
            alecTrack.append(Func(self.updateToonDNA, dna, True))
            if hasattr(self, 'animFSM'):
                state = self.animFSM.getCurrentState()
                alecTrack.append(Func(self.animFSM.request, 'off'))
                alecTrack.append(Func(self.animFSM.request, state))
            alecTrack.append(Func(self.nametag.setText, 'Alec Tinn'))
        else:
            alecTrack.append(Func(self.updateToonDNA, self.oldStyle))
            if hasattr(self, 'animFSM'):
                state = self.animFSM.getCurrentState()
                alecTrack.append(Func(self.animFSM.request, 'off'))
                alecTrack.append(Func(self.animFSM.request, state))
            alecTrack.append(Func(self.nametag.setText, self.nametag.name))
            alecTrack.append(Func(self.setHat, self.oldHat[0], self.oldHat[1], self.oldHat[2]))
            alecTrack.append(Func(self.generateToonAccessories))
        track.append(alecTrack)
        return track

    def __doSlappy(self, lerpTime, toSlappy):
        track = Sequence()
        slappyTrack = Parallel()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        if lerpTime > 0.0:
            dust = getDustCloudIval()
            track.append(Func(dust.start))
            track.append(Wait(0.5))
            
        if toSlappy:
            self.oldStyle = self.style.clone()
            self.oldHat = self.hat
            dna = ToonDNA.ToonDNA()
            dna.newToonFromProperties('fls', 'ms', 'l', 'm', 14, 0, 14, 14, 152, 27, 139, 27, 59, 27)
            slappyTrack.append(Func(self.updateToonDNA, dna, True))
            if hasattr(self, 'animFSM'):
                state = self.animFSM.getCurrentState()
                slappyTrack.append(Func(self.animFSM.request, 'off'))
                slappyTrack.append(Func(self.animFSM.request, state))
            slappyTrack.append(Func(self.nametag.setText, 'Slappy'))
        else:
            slappyTrack.append(Func(self.updateToonDNA, self.oldStyle))
            if hasattr(self, 'animFSM'):
                state = self.animFSM.getCurrentState()
                slappyTrack.append(Func(self.animFSM.request, 'off'))
                slappyTrack.append(Func(self.animFSM.request, state))
            slappyTrack.append(Func(self.nametag.setText, self.nametag.name))
            slappyTrack.append(Func(self.setHat, self.oldHat[0], self.oldHat[1], self.oldHat[2]))
            slappyTrack.append(Func(self.generateToonAccessories))
        track.append(slappyTrack)
        return track

    def __doTutorialTom(self, lerpTime, toTom):
        track = Sequence()
        tomTrack = Parallel()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        if lerpTime > 0.0:
            dust = getDustCloudIval()
            track.append(Func(dust.start))
            track.append(Wait(0.5))
            
        if toTom:
            self.oldStyle = self.style.clone()
            self.oldHat = self.hat
            dna = ToonDNA.ToonDNA()
            dna.newToonFromProperties('dls', 'ms', 'm', 'm', 7, 0, 7, 7, 2, 6, 2, 6, 2, 16)
            tomTrack.append(Func(self.updateToonDNA, dna, True))
            if hasattr(self, 'animFSM'):
                state = self.animFSM.getCurrentState()
                tomTrack.append(Func(self.animFSM.request, 'off'))
                tomTrack.append(Func(self.animFSM.request, state))
            tomTrack.append(Func(self.nametag.setText, 'Tutorial Tom'))
        else:
            tomTrack.append(Func(self.updateToonDNA, self.oldStyle))
            if hasattr(self, 'animFSM'):
                state = self.animFSM.getCurrentState()
                tomTrack.append(Func(self.animFSM.request, 'off'))
                tomTrack.append(Func(self.animFSM.request, state))
            tomTrack.append(Func(self.nametag.setText, self.nametag.name))
            tomTrack.append(Func(self.setHat, self.oldHat[0], self.oldHat[1], self.oldHat[2]))
            tomTrack.append(Func(self.generateToonAccessories))
        track.append(tomTrack)
        return track

    def __doLilOldman(self, lerpTime, toOldman):
        track = Sequence()
        oldmanTrack = Parallel()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        if lerpTime > 0.0:
            dust = getDustCloudIval()
            track.append(Func(dust.start))
            track.append(Wait(0.5))
            
        if toOldman:
            self.oldStyle = self.style.clone()
            self.oldHat = self.hat
            dna = ToonDNA.ToonDNA()
            dna.newToonFromProperties('rll', 'ls', 'm', 'm', 21, 0, 21, 21, 1, 5, 1, 5, 1, 9)
            oldmanTrack.append(Func(self.updateToonDNA, dna, True))
            if hasattr(self, 'animFSM'):
                state = self.animFSM.getCurrentState()
                oldmanTrack.append(Func(self.animFSM.request, 'off'))
                oldmanTrack.append(Func(self.animFSM.request, state))
            oldmanTrack.append(Func(self.nametag.setText, 'Lil Oldman'))
        else:
            oldmanTrack.append(Func(self.updateToonDNA, self.oldStyle))
            if hasattr(self, 'animFSM'):
                state = self.animFSM.getCurrentState()
                oldmanTrack.append(Func(self.animFSM.request, 'off'))
                oldmanTrack.append(Func(self.animFSM.request, state))
            oldmanTrack.append(Func(self.nametag.setText, self.nametag.name))
            oldmanTrack.append(Func(self.setHat, self.oldHat[0], self.oldHat[1], self.oldHat[2]))
            oldmanTrack.append(Func(self.generateToonAccessories))
        track.append(oldmanTrack)
        return track

    def __doKion(self, lerpTime, toKion):
        track = Sequence()
        kionTrack = Parallel()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        if lerpTime > 0.0:
            dust = getDustCloudIval()
            track.append(Func(dust.start))
            track.append(Wait(0.5))
            
        if toKion:
            self.oldStyle = self.style.clone()
            self.oldHat = self.hat
            dna = ToonDNA.ToonDNA()
            dna.newToonFromProperties('cls', 'ms', 'm', 'm', 2, 0, 2, 2, 14, 9, 10, 9, 1, 14)
            kionTrack.append(Func(self.updateToonDNA, dna, True))
            if hasattr(self, 'animFSM'):
                state = self.animFSM.getCurrentState()
                kionTrack.append(Func(self.animFSM.request, 'off'))
                kionTrack.append(Func(self.animFSM.request, state))
            kionTrack.append(Func(self.nametag.setText, 'Kion'))
        else:
            kionTrack.append(Func(self.updateToonDNA, self.oldStyle))
            if hasattr(self, 'animFSM'):
                state = self.animFSM.getCurrentState()
                kionTrack.append(Func(self.animFSM.request, 'off'))
                kionTrack.append(Func(self.animFSM.request, state))
            kionTrack.append(Func(self.nametag.setText, self.nametag.name))
            kionTrack.append(Func(self.setHat, self.oldHat[0], self.oldHat[1], self.oldHat[2]))
            kionTrack.append(Func(self.generateToonAccessories))
        track.append(kionTrack)
        return track

    def __doSqueaky(self, lerpTime, toSqueaky):
        track = Sequence()
        squeakyTrack = Parallel()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        if lerpTime > 0.0:
            dust = getDustCloudIval()
            track.append(Func(dust.start))
            track.append(Wait(0.5))
            
        if toSqueaky:
            self.oldStyle = self.style.clone()
            self.oldHat = self.hat
            dna = ToonDNA.ToonDNA()
            dna.newToonFromProperties('mss', 'ms', 'm', 'm', 2, 0, 2, 2, 14, 9, 10, 9, 1, 14)
            squeakyTrack.append(Func(self.updateToonDNA, dna, True))
            if hasattr(self, 'animFSM'):
                state = self.animFSM.getCurrentState()
                squeakyTrack.append(Func(self.animFSM.request, 'off'))
                squeakyTrack.append(Func(self.animFSM.request, state))
            squeakyTrack.append(Func(self.nametag.setText, 'Squeaky'))
        else:
            squeakyTrack.append(Func(self.updateToonDNA, self.oldStyle))
            if hasattr(self, 'animFSM'):
                state = self.animFSM.getCurrentState()
                squeakyTrack.append(Func(self.animFSM.request, 'off'))
                squeakyTrack.append(Func(self.animFSM.request, state))
            squeakyTrack.append(Func(self.nametag.setText, self.nametag.name))
            squeakyTrack.append(Func(self.setHat, self.oldHat[0], self.oldHat[1], self.oldHat[2]))
            squeakyTrack.append(Func(self.generateToonAccessories))
        track.append(squeakyTrack)
        return track

    def __doFreddy(self, lerpTime, toFreddy):
        track = Sequence()
        freddyTrack = Parallel()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        if lerpTime > 0.0:
            dust = getDustCloudIval()
            track.append(Func(dust.start))
            track.append(Wait(0.5))
            
        if toFreddy:
            self.oldStyle = self.style.clone()
            self.oldHat = self.hat
            dna = ToonDNA.ToonDNA()
            dna.newToonFromProperties('rss', 'ls', 'l', 'm', 17, 0, 17, 17, 1, 6, 1, 6, 1, 1)
            freddyTrack.append(Func(self.updateToonDNA, dna, True))
            if hasattr(self, 'animFSM'):
                state = self.animFSM.getCurrentState()
                freddyTrack.append(Func(self.animFSM.request, 'off'))
                freddyTrack.append(Func(self.animFSM.request, state))
            freddyTrack.append(Func(self.nametag.setText, 'Fisherman Freddy'))
        else:
            freddyTrack.append(Func(self.updateToonDNA, self.oldStyle))
            if hasattr(self, 'animFSM'):
                state = self.animFSM.getCurrentState()
                freddyTrack.append(Func(self.animFSM.request, 'off'))
                freddyTrack.append(Func(self.animFSM.request, state))
            freddyTrack.append(Func(self.nametag.setText, self.nametag.name))
            freddyTrack.append(Func(self.setHat, self.oldHat[0], self.oldHat[1], self.oldHat[2]))
            freddyTrack.append(Func(self.generateToonAccessories))
        track.append(freddyTrack)
        return track

    def __doBilly(self, lerpTime, toBilly):
        track = Sequence()
        billyTrack = Parallel()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        if lerpTime > 0.0:
            dust = getDustCloudIval()
            track.append(Func(dust.start))
            track.append(Wait(0.5))
            
        if toBilly:
            self.oldStyle = self.style.clone()
            self.oldHat = self.hat
            dna = ToonDNA.ToonDNA()
            dna.newToonFromProperties('dls', 'ls', 'l', 'm', 10, 0, 10, 10, 1, 9, 1, 9, 1, 10)
            billyTrack.append(Func(self.updateToonDNA, dna, True))
            if hasattr(self, 'animFSM'):
                state = self.animFSM.getCurrentState()
                billyTrack.append(Func(self.animFSM.request, 'off'))
                billyTrack.append(Func(self.animFSM.request, state))
            billyTrack.append(Func(self.nametag.setText, 'Fisherman Billy'))
        else:
            billyTrack.append(Func(self.updateToonDNA, self.oldStyle))
            if hasattr(self, 'animFSM'):
                state = self.animFSM.getCurrentState()
                billyTrack.append(Func(self.animFSM.request, 'off'))
                billyTrack.append(Func(self.animFSM.request, state))
            billyTrack.append(Func(self.nametag.setText, self.nametag.name))
            billyTrack.append(Func(self.setHat, self.oldHat[0], self.oldHat[1], self.oldHat[2]))
            billyTrack.append(Func(self.generateToonAccessories))
        track.append(billyTrack)
        return track

    def __doDroopy(self, lerpTime, toDroopy):
        track = Sequence()
        droopyTrack = Parallel()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        if lerpTime > 0.0:
            dust = getDustCloudIval()
            track.append(Func(dust.start))
            track.append(Wait(0.5))
            
        if toDroopy:
            self.oldStyle = self.style.clone()
            self.oldHat = self.hat
            dna = ToonDNA.ToonDNA()
            dna.newToonFromProperties('cll', 'ls', 'm', 'm', 9, 0, 9, 9, 1, 1, 1, 1, 0, 13)
            droopyTrack.append(Func(self.updateToonDNA, dna, True))
            if hasattr(self, 'animFSM'):
                state = self.animFSM.getCurrentState()
                droopyTrack.append(Func(self.animFSM.request, 'off'))
                droopyTrack.append(Func(self.animFSM.request, state))
            droopyTrack.append(Func(self.nametag.setText, 'Fisherman Droopy'))
        else:
            droopyTrack.append(Func(self.updateToonDNA, self.oldStyle))
            if hasattr(self, 'animFSM'):
                state = self.animFSM.getCurrentState()
                droopyTrack.append(Func(self.animFSM.request, 'off'))
                droopyTrack.append(Func(self.animFSM.request, state))
            droopyTrack.append(Func(self.nametag.setText, self.nametag.name))
            droopyTrack.append(Func(self.setHat, self.oldHat[0], self.oldHat[1], self.oldHat[2]))
            droopyTrack.append(Func(self.generateToonAccessories))
        track.append(droopyTrack)
        return track

    def __doPunchy(self, lerpTime, toPunchy):
        track = Sequence()
        punchyTrack = Parallel()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        if lerpTime > 0.0:
            dust = getDustCloudIval()
            track.append(Func(dust.start))
            track.append(Wait(0.5))
            
        if toPunchy:
            self.oldStyle = self.style.clone()
            self.oldHat = self.hat
            dna = ToonDNA.ToonDNA()
            dna.newToonFromProperties('fsl', 'ss', 'l', 'm', 21, 0, 21, 21, 1, 5, 1, 5, 0, 12)
            punchyTrack.append(Func(self.updateToonDNA, dna, True))
            if hasattr(self, 'animFSM'):
                state = self.animFSM.getCurrentState()
                punchyTrack.append(Func(self.animFSM.request, 'off'))
                punchyTrack.append(Func(self.animFSM.request, state))
            punchyTrack.append(Func(self.nametag.setText, 'Fisherman Punchy'))
        else:
            punchyTrack.append(Func(self.updateToonDNA, self.oldStyle))
            if hasattr(self, 'animFSM'):
                state = self.animFSM.getCurrentState()
                punchyTrack.append(Func(self.animFSM.request, 'off'))
                punchyTrack.append(Func(self.animFSM.request, state))
            punchyTrack.append(Func(self.nametag.setText, self.nametag.name))
            punchyTrack.append(Func(self.setHat, self.oldHat[0], self.oldHat[1], self.oldHat[2]))
            punchyTrack.append(Func(self.generateToonAccessories))
        track.append(punchyTrack)
        return track

    def __doFurball(self, lerpTime, toFurball):
        track = Sequence()
        furballTrack = Parallel()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        if lerpTime > 0.0:
            dust = getDustCloudIval()
            track.append(Func(dust.start))
            track.append(Wait(0.5))
            
        if toFurball:
            self.oldStyle = self.style.clone()
            self.oldHat = self.hat
            dna = ToonDNA.ToonDNA()
            dna.newToonFromProperties('cls', 'ms', 'm', 'm', 3, 0, 3, 3, 0, 27, 0, 27, 0, 17)
            furballTrack.append(Func(self.updateToonDNA, dna, True))
            if hasattr(self, 'animFSM'):
                state = self.animFSM.getCurrentState()
                furballTrack.append(Func(self.animFSM.request, 'off'))
                furballTrack.append(Func(self.animFSM.request, state))
            furballTrack.append(Func(self.nametag.setText, 'Fisherman Furball'))
        else:
            furballTrack.append(Func(self.updateToonDNA, self.oldStyle))
            if hasattr(self, 'animFSM'):
                state = self.animFSM.getCurrentState()
                furballTrack.append(Func(self.animFSM.request, 'off'))
                furballTrack.append(Func(self.animFSM.request, state))
            furballTrack.append(Func(self.nametag.setText, self.nametag.name))
            furballTrack.append(Func(self.setHat, self.oldHat[0], self.oldHat[1], self.oldHat[2]))
            furballTrack.append(Func(self.generateToonAccessories))
        track.append(furballTrack)
        return track

    def __doBarney(self, lerpTime, toBarney):
        track = Sequence()
        barneyTrack = Parallel()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        if lerpTime > 0.0:
            dust = getDustCloudIval()
            track.append(Func(dust.start))
            track.append(Wait(0.5))
            
        if toBarney:
            self.oldStyle = self.style.clone()
            self.oldHat = self.hat
            dna = ToonDNA.ToonDNA()
            dna.newToonFromProperties('cls', 'ms', 'l', 'm', 4, 0, 4, 4, 1, 11, 1, 11, 0, 19)
            barneyTrack.append(Func(self.updateToonDNA, dna, True))
            if hasattr(self, 'animFSM'):
                state = self.animFSM.getCurrentState()
                barneyTrack.append(Func(self.animFSM.request, 'off'))
                barneyTrack.append(Func(self.animFSM.request, state))
            barneyTrack.append(Func(self.nametag.setText, 'Fisherman Barney'))
        else:
            barneyTrack.append(Func(self.updateToonDNA, self.oldStyle))
            if hasattr(self, 'animFSM'):
                state = self.animFSM.getCurrentState()
                barneyTrack.append(Func(self.animFSM.request, 'off'))
                barneyTrack.append(Func(self.animFSM.request, state))
            barneyTrack.append(Func(self.nametag.setText, self.nametag.name))
            barneyTrack.append(Func(self.setHat, self.oldHat[0], self.oldHat[1], self.oldHat[2]))
            barneyTrack.append(Func(self.generateToonAccessories))
        track.append(barneyTrack)
        return track

    def __doPete(self, lerpTime, toPete):
        track = Sequence()
        peteTrack = Parallel()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        if lerpTime > 0.0:
            dust = getDustCloudIval()
            track.append(Func(dust.start))
            track.append(Wait(0.5))
            
        if toPete:
            self.oldStyle = self.style.clone()
            self.oldHat = self.hat
            dna = ToonDNA.ToonDNA()
            dna.newToonFromProperties('cll', 'ms', 'l', 'm', 18, 0, 18, 18, 0, 4, 0, 4, 1, 15)
            peteTrack.append(Func(self.updateToonDNA, dna, True))
            if hasattr(self, 'animFSM'):
                state = self.animFSM.getCurrentState()
                peteTrack.append(Func(self.animFSM.request, 'off'))
                peteTrack.append(Func(self.animFSM.request, state))
            peteTrack.append(Func(self.nametag.setText, 'Professor Pete'))
        else:
            peteTrack.append(Func(self.updateToonDNA, self.oldStyle))
            if hasattr(self, 'animFSM'):
                state = self.animFSM.getCurrentState()
                peteTrack.append(Func(self.animFSM.request, 'off'))
                peteTrack.append(Func(self.animFSM.request, state))
            peteTrack.append(Func(self.nametag.setText, self.nametag.name))
            peteTrack.append(Func(self.setHat, self.oldHat[0], self.oldHat[1], self.oldHat[2]))
            peteTrack.append(Func(self.generateToonAccessories))
        track.append(peteTrack)
        return track

    def __doLouis(self, lerpTime, toLouis):
        track = Sequence()
        louisTrack = Parallel()

        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, self), dustCloud.track, Func(dustCloud.destroy), name='dustCloadIval')

        if lerpTime > 0.0:
            dust = getDustCloudIval()
            track.append(Func(dust.start))
            track.append(Wait(0.5))
            
        if toLouis:
            self.oldStyle = self.style.clone()
            self.oldHat = self.hat
            dna = ToonDNA.ToonDNA()
            dna.newToonFromProperties('fss', 'ss', 'l', 'm', 12, 0, 12, 12, 1, 5, 1, 5, 1, 12)
            louisTrack.append(Func(self.updateToonDNA, dna, True))
            if hasattr(self, 'animFSM'):
                state = self.animFSM.getCurrentState()
                louisTrack.append(Func(self.animFSM.request, 'off'))
                louisTrack.append(Func(self.animFSM.request, state))
            louisTrack.append(Func(self.nametag.setText, 'Loony Louis'))
        else:
            louisTrack.append(Func(self.updateToonDNA, self.oldStyle))
            if hasattr(self, 'animFSM'):
                state = self.animFSM.getCurrentState()
                louisTrack.append(Func(self.animFSM.request, 'off'))
                louisTrack.append(Func(self.animFSM.request, state))
            louisTrack.append(Func(self.nametag.setText, self.nametag.name))
            louisTrack.append(Func(self.setHat, self.oldHat[0], self.oldHat[1], self.oldHat[2]))
            louisTrack.append(Func(self.generateToonAccessories))
        track.append(louisTrack)
        return track

    def __doCheesyEffect(self, effect, lerpTime):
        if effect == ToontownGlobals.CEBigHead:
            return self.__doHeadScale(2.5, lerpTime)
        elif effect == ToontownGlobals.CESmallHead:
            return self.__doHeadScale(0.5, lerpTime)
        elif effect == ToontownGlobals.CEBigLegs:
            return self.__doLegsScale(1.4, lerpTime)
        elif effect == ToontownGlobals.CESmallLegs:
            return self.__doLegsScale(0.6, lerpTime)
        elif effect == ToontownGlobals.CEBigToon:
            return self.__doToonScale(ToontownGlobals.BigToonScale, lerpTime)
        elif effect == ToontownGlobals.CESmallToon:
            return self.__doToonScale(ToontownGlobals.SmallToonScale, lerpTime)
        elif effect == ToontownGlobals.CEFlatPortrait:
            return self.__doToonScale(VBase3(1, 0.05, 1), lerpTime)
        elif effect == ToontownGlobals.CEFlatProfile:
            return self.__doToonScale(VBase3(0.05, 1, 1), lerpTime)
        elif effect == ToontownGlobals.CETransparent:
            return self.doToonColorScale(VBase4(1, 1, 1, 0.6), lerpTime, keepDefault=1)
        elif effect == ToontownGlobals.CENoColor:
            return self.__doToonColor(VBase4(1, 1, 1, 1), lerpTime)
        elif effect == ToontownGlobals.CEInvisible:
            return self.__doPartsColorScale(VBase4(1, 1, 1, 0), lerpTime)
        elif effect == ToontownGlobals.CEPumpkin:
            return self.__doPumpkinHeadSwitch(lerpTime, toPumpkin=True)
        elif effect == ToontownGlobals.CEBigWhite:
            return self.__doBigAndWhite(VBase4(1, 1, 1, 1), ToontownGlobals.BigToonScale, lerpTime)
        elif effect == ToontownGlobals.CESnowMan:
            return self.__doSnowManHeadSwitch(lerpTime, toSnowMan=True)
        elif effect == ToontownGlobals.CEVirtual:
            return self.__doVirtual()
        elif effect == ToontownGlobals.CEGreenToon:
            return self.__doGreenToon(lerpTime, toGreen = True)
        elif effect == ToontownGlobals.CEGhost:
            alpha = 0.25
            if base.localAvatar.getAdminAccess() < self.adminAccess:
                alpha = 0
            return Sequence(self.__doToonGhostColorScale(VBase4(1, 1, 1, alpha), lerpTime, keepDefault=1), Func(self.nametag3d.hide))
        elif effect == ToontownGlobals.CEWire:
            return self.__doWireFrame()
        return Sequence()

    def __undoCheesyEffect(self, effect, lerpTime):
        if effect == ToontownGlobals.CEBigHead:
            return self.__doHeadScale(None, lerpTime)
        elif effect == ToontownGlobals.CESmallHead:
            return self.__doHeadScale(None, lerpTime)
        if effect == ToontownGlobals.CEBigLegs:
            return self.__doLegsScale(None, lerpTime)
        elif effect == ToontownGlobals.CESmallLegs:
            return self.__doLegsScale(None, lerpTime)
        elif effect == ToontownGlobals.CEBigToon:
            return self.__doToonScale(None, lerpTime)
        elif effect == ToontownGlobals.CESmallToon:
            return self.__doToonScale(None, lerpTime)
        elif effect == ToontownGlobals.CETinyToon:
            return self.__doToonScale(None, lerpTime)
        elif effect == ToontownGlobals.CEGiantToon:
            return self.__doToonScale(None, lerpTime)
        elif effect == ToontownGlobals.CEBeanToon:
            return self.__doToonScale(None, lerpTime)
        elif effect == ToontownGlobals.CEFlatPortrait:
            return self.__doToonScale(None, lerpTime)
        elif effect == ToontownGlobals.CEFlatProfile:
            return self.__doToonScale(None, lerpTime)
        elif effect == ToontownGlobals.CETransparent:
            return self.doToonColorScale(None, lerpTime, keepDefault=1)
        elif effect == ToontownGlobals.CENoColor:
            return self.__doToonColor(None, lerpTime)
        elif effect == ToontownGlobals.CEInvisible:
            return self.__doPartsColorScale(None, lerpTime)
        elif effect == ToontownGlobals.CEPumpkin:
            return self.__doPumpkinHeadSwitch(lerpTime, toPumpkin=False)
        elif effect == ToontownGlobals.CEBigWhite:
            return self.__doBigAndWhite(None, None, lerpTime)
        elif effect == ToontownGlobals.CESnowMan:
            return self.__doSnowManHeadSwitch(lerpTime, toSnowMan=False)
        elif effect == ToontownGlobals.CEYesMan:
            return self.__doYesMan(lerpTime, toYesMan=False)
        elif effect == ToontownGlobals.CEDownsizer:
            return self.__doDownsizer(lerpTime, toDownsizer=False)
        elif effect == ToontownGlobals.CEMoverShaker:
            return self.__doMoverShaker(lerpTime, toMoverShaker=False)
        elif effect == ToontownGlobals.CEBigCheese:
            return self.__doBigCheese(lerpTime, toBigCheese=False)
        elif effect == ToontownGlobals.CEGladHander:
            return self.__doGladHander(lerpTime, toGladHander=False)
        elif effect == ToontownGlobals.CEMingler:
            return self.__doMingler(lerpTime, toMingler=False)
        elif effect == ToontownGlobals.CEFlunky:
            return self.__doFlunky(lerpTime, toFlunky=False)
        elif effect == ToontownGlobals.CETelemarketer:
            return self.__doTelemarketer(lerpTime, toTelemarketer=False)
        elif effect == ToontownGlobals.CELoanShark:
            return self.__doLoanShark(lerpTime, toLoanShark=False)
        elif effect == ToontownGlobals.CEBigWig:
            return self.__doBigWig(lerpTime, toBigWig=False)
        elif effect == ToontownGlobals.CEMicroManager:
            return self.__doMicroManager(lerpTime, toMicroManager=False)
        elif effect == ToontownGlobals.CEBigFish:
            return self.__doBigFish(lerpTime, toBigFish=False)
        elif effect == ToontownGlobals.CECorporateRaider:
            return self.__doCorporateRaider(lerpTime, toCorporateRaider=False)
        elif effect == ToontownGlobals.CEHeadHoncho:
            return self.__doHeadHoncho(lerpTime, toHeadHoncho=False)
        elif effect == ToontownGlobals.CEDoubleTalker:
            return self.__doDoubleTalker(lerpTime, toDoubleTalker=False)
        elif effect == ToontownGlobals.CETwoFace:
            return self.__doTwoFace(lerpTime, toTwoFace=False)
        elif effect == ToontownGlobals.CEConArtist:
            return self.__doConArtist(lerpTime, toConArtist=False)
        elif effect == ToontownGlobals.CEConnoisseur:
            return self.__doConnoisseur(lerpTime, toConnoisseur=False)
        elif effect == ToontownGlobals.CESwindler:
            return self.__doSwindler(lerpTime, toSwindler=False)
        elif effect == ToontownGlobals.CEMiddleman:
            return self.__doMiddleman(lerpTime, toMiddleman=False)
        elif effect == ToontownGlobals.CEToxicManager:
            return self.__doToxicManager(lerpTime, toToxicManager=False)
        elif effect == ToontownGlobals.CEMagnate:
            return self.__doMagnate(lerpTime, toMagnate=False)
        elif effect == ToontownGlobals.CELegalEagle:
            return self.__doLegalEagle(lerpTime, toLegalEagle=False)
        elif effect == ToontownGlobals.CERobberBaron:
            return self.__doRobberBaron(lerpTime, toRobberBaron=False)
        elif effect == ToontownGlobals.CEColdCaller:
            return self.__doColdCaller(lerpTime, toColdCaller=False)
        elif effect == ToontownGlobals.CEShortChange:
            return self.__doShortChange(lerpTime, toShortChange=False)
        elif effect == ToontownGlobals.CEBloodsucker:
            return self.__doBloodsucker(lerpTime, toBloodsucker=False)
        elif effect == ToontownGlobals.CENameDropper:
            return self.__doNameDropper(lerpTime, toNameDropper=False)
        elif effect == ToontownGlobals.CEHeadHunter:
            return self.__doHeadHunter(lerpTime, toHeadHunter=False)
        elif effect == ToontownGlobals.CEHollywood:
            return self.__doHollywood(lerpTime, toHollywood=False)
        elif effect == ToontownGlobals.CEPencilPusher:
            return self.__doPencilPusher(lerpTime, toPencilPusher=False)
        elif effect == ToontownGlobals.CEMoneyBags:
            return self.__doMoneyBags(lerpTime, toMoneyBags=False)
        elif effect == ToontownGlobals.CESpinDoctor:
            return self.__doSpinDoctor(lerpTime, toSpinDoctor=False)
        elif effect == ToontownGlobals.CEAmbulanceChaser:
            return self.__doAmbulanceChaser(lerpTime, toAmbulanceChaser=False)
        elif effect == ToontownGlobals.CENumberCruncher:
            return self.__doNumberCruncher(lerpTime, toNumberCruncher=False)
        elif effect == ToontownGlobals.CEPennyPincher:
            return self.__doPennyPincher(lerpTime, toPennyPincher=False)
        elif effect == ToontownGlobals.CETightwad:
            return self.__doTightwad(lerpTime, toTightwad=False)
        elif effect == ToontownGlobals.CEBeanCounter:
            return self.__doBeanCounter(lerpTime, toBeanCounter=False)
        elif effect == ToontownGlobals.CEBackStabber:
            return self.__doBackStabber(lerpTime, toBackStabber=False)
        elif effect == ToontownGlobals.CEBottomFeeder:
            return self.__doBottomFeeder(lerpTime, toBottomFeeder=False)
        elif effect == ToontownGlobals.CEGreenToon:
            return self.__doGreenToon(lerpTime, toGreen=False)
        elif effect == ToontownGlobals.CERogerDog:
            return self.__doRogerDog(lerpTime, toRoger=False)
        elif effect == ToontownGlobals.CEFlippy:
            return self.__doFlippy(lerpTime, toFlippy=False)
        elif effect == ToontownGlobals.CESurlee:
            return self.__doSurlee(lerpTime, toSurlee=False)
        elif effect == ToontownGlobals.CEDimm:
            return self.__doDimm(lerpTime, toDimm=False)
        elif effect == ToontownGlobals.CEAlecTinn:
            return self.__doAlecTinn(lerpTime, toAlecTinn=False)
        elif effect == ToontownGlobals.CESlappy:
            return self.__doSlappy(lerpTime, toSlappy=False)
        elif effect == ToontownGlobals.CETutorialTom:
            return self.__doTutorialTom(lerpTime, toTom=False)
        elif effect == ToontownGlobals.CEOldman:
            return self.__doLilOldman(lerpTime, toOldman=False)
        elif effect == ToontownGlobals.CEKion:
            return self.__doKion(lerpTime, toKion=False)
        elif effect == ToontownGlobals.CESqueaky:
            return self.__doSqueaky(lerpTime, toSqueaky=False)
        elif effect == ToontownGlobals.CEFreddy:
            return self.__doFreddy(lerpTime, toFreddy=False)
        elif effect == ToontownGlobals.CEBilly:
            return self.__doBilly(lerpTime, toBilly=False)
        elif effect == ToontownGlobals.CEDroopy:
            return self.__doDroopy(lerpTime, toDroopy=False)
        elif effect == ToontownGlobals.CEPunchy:
            return self.__doPunchy(lerpTime, toPunchy=False)
        elif effect == ToontownGlobals.CEFurball:
            return self.__doFurball(lerpTime, toFurball=False)
        elif effect == ToontownGlobals.CEBarney:
            return self.__doBarney(lerpTime, toBarney=False)
        elif effect == ToontownGlobals.CEPete:
            return self.__doPete(lerpTime, toPete=False)
        elif effect == ToontownGlobals.CELouis:
            return self.__doLouis(lerpTime, toLouis=False)
        elif effect == ToontownGlobals.CEVirtual:
            return self.__doUnVirtual()
        elif effect == ToontownGlobals.CEGhost:
            return Sequence(Func(self.nametag3d.show), self.__doToonGhostColorScale(None, lerpTime, keepDefault=1))
        elif effect == ToontownGlobals.CEWire:
            return self.__doUnWireFrame()
        return Sequence()

    def printCameraPos():
        print(base.localAvatar.getPos())
        print(base.localAvatar.getHpr())

    def printCameraPos2():
        print(base.camera.getPos(render))
        print(base.camera.getHpr(render))

    base.accept('[', printCameraPos)

    base.accept(']', printCameraPos2)
            
    def putOnSuit(self, suitType, setDisplayName = True, rental = False):
        if self.isDisguised:
            self.takeOffSuit()
        if launcher and not launcher.getPhaseComplete(5):
            return
        from toontown.suit import Suit
        deptIndex = suitType
        suit = Suit.Suit()
        dna = SuitDNA.SuitDNA()
        if rental == True:
            if SuitDNA.suitDepts[deptIndex] == 's':
                suitType = 'cc'
            elif SuitDNA.suitDepts[deptIndex] == 'm':
                suitType = 'sc'
            elif SuitDNA.suitDepts[deptIndex] == 'l':
                suitType = 'bf'
            elif SuitDNA.suitDepts[deptIndex] == 'c':
                suitType = 'f'
            elif SuitDNA.suitDepts[deptIndex] == 'g':
                suitType = 'bgh'
            else:
                self.notify.warning('Suspicious: Incorrect rental suit department requested')
                suitType = 'cc'
        dna.newSuit(suitType)
        suit.setStyle(dna)
        suit.isDisguised = 1
        suit.generateSuit()
        suit.getDialogueArray()
        suit.initializeDropShadow()
        suit.setPos(self.getPos())
        suit.setHpr(self.getHpr())
        '''for part in suit.getHeadParts():
            part.hide()

        suitHeadNull = suit.find('**/joint_head')
        toonHead = self.getPart('head', '1000')'''
        Emote.globalEmote.disableAll(self)
        toonGeom = self.getGeomNode()
        toonGeom.hide()
        '''worldScale = toonHead.getScale(render)
        self.headOrigScale = toonHead.getScale()
        headPosNode = hidden.attachNewNode('headPos')
        toonHead.reparentTo(headPosNode)
        toonHead.setPos(0, 0, 0.2
        headPosNode.reparentTo(suitHeadNull)
        headPosNode.setScale(render, worldScale)'''
        suitGeom = suit.getGeomNode()
        suitGeom.reparentTo(self)
        if rental == True:
            suit.makeRentalSuit(SuitDNA.suitDepts[deptIndex])
        self.suit = suit
        self.suitGeom = suitGeom
        self.setHeight(suit.getHeight())
        self.nametag3d.setPos(0, 0, self.height + 1.3)
        if self.isLocal():
            if hasattr(self, 'book'):
                self.book.obscureButton(1)
            self.oldForward = ToontownGlobals.ToonForwardSpeed
            self.oldReverse = ToontownGlobals.ToonReverseSpeed
            self.oldRotate = ToontownGlobals.ToonRotateSpeed
            ToontownGlobals.ToonForwardSpeed = ToontownGlobals.SuitWalkSpeed
            ToontownGlobals.ToonReverseSpeed = ToontownGlobals.SuitWalkSpeed
            ToontownGlobals.ToonRotateSpeed = ToontownGlobals.ToonRotateSlowSpeed
            if self.hasTrackAnimToSpeed():
                self.stopTrackAnimToSpeed()
                self.startTrackAnimToSpeed()
            self.controlManager.disableAvatarJump()
            #indices = range(OTPLocalizer.SCMenuCommonCogIndices[0], OTPLocalizer.SCMenuCommonCogIndices[1] + 1)
            #customIndices = OTPLocalizer.SCMenuCustomCogIndices[suitType]
            #indices += range(customIndices[0], customIndices[1] + 1)
            #self.chatMgr.chatInputSpeedChat.addCogMenu(indices)
        self.suit.loop('neutral')
        self.isDisguised = 1
        self.setFont(ToontownGlobals.getSuitFont())
        if setDisplayName:
            if hasattr(base, 'idTags') and base.idTags:
                name = self.getAvIdName()
            else:
                name = self.getName()
            # Avatar.setNametagWithTag() now owns the complete disguise
            # layout so Club/tag refreshes cannot erase the Cog lines.
            self.setDisplayName(name)
            self.nametag.setWordWrap(12.0)

    def setChatAbsolute(
        self,
        chatString,
        chatFlags,
        dialogue=None,
        interrupt=1):

    # Run all normal Avatar chat handling first.
        Avatar.Avatar.setChatAbsolute(
            self,
            chatString,
            chatFlags,
            dialogue,
            interrupt
        )

        # Only Toons have disguise handling here.
        if not self.isDisguised:
            return

        suit = getattr(self, 'suit', None)

        if suit is None or suit.isEmpty():
            return

        animName = getattr(self, 'animHead', None)

        if not animName:
            return

        for headPart in getattr(suit, 'animatedHeadParts', []):
            if not headPart or headPart.isEmpty():
                continue

            if not headPart.getAnimControl(animName):
                continue

            Sequence(
                ActorInterval(headPart, animName),
                Func(headPart.loop, 'neutral')
            ).start()

    def takeOffSuit(self):
        if not self.isDisguised:
            return
        suitType = self.suit.style.name
        '''toonHeadNull = self.find('**/1000/**/def_head')
        if not toonHeadNull:
            toonHeadNull = self.find('**/1000/**/joint_head')
        toonHead = self.getPart('head', '1000')
        toonHead.reparentTo(toonHeadNull)
        toonHead.setScale(self.headOrigScale)
        toonHead.setPos(0, 0, 0)
        headPosNode = self.suitGeom.find('**/headPos')
        headPosNode.removeNode()'''
        self.suitGeom.reparentTo(self.suit)
        self.resetHeight()
        self.nametag3d.setPos(0, 0, self.height + 0.5)
        toonGeom = self.getGeomNode()
        toonGeom.show()
        Emote.globalEmote.releaseAll(self)
        self.isDisguised = 0
        self.setFont(ToontownGlobals.getToonFont())
        self.nametag.setWordWrap(None)
        if hasattr(base, 'idTags') and base.idTags:
            name = self.getAvIdName()
        else:
            name = self.getName()
        self.setDisplayName(name)
        if self.isLocal():
            if hasattr(self, 'book'):
                self.book.obscureButton(0)
            ToontownGlobals.ToonForwardSpeed = self.oldForward
            ToontownGlobals.ToonReverseSpeed = self.oldReverse
            ToontownGlobals.ToonRotateSpeed = self.oldRotate
            if self.hasTrackAnimToSpeed():
                self.stopTrackAnimToSpeed()
                self.startTrackAnimToSpeed()
            del self.oldForward
            del self.oldReverse
            del self.oldRotate
            self.controlManager.enableAvatarJump()
            self.chatMgr.chatInputSpeedChat.removeCogMenu()
        #self.suit.delete()
        del self.suit
        del self.suitGeom

    def makeWaiter(self):
        if not self.isDisguised:
            return
        self.suit.makeWaiter2(self.suitGeom)

    def getPieModel(self):
        from toontown.toonbase import ToontownBattleGlobals
        from toontown.battle import BattleProps
        if self.pieModel != None and self.__pieModelType != self.pieType:
            self.pieModel.detachNode()
            self.pieModel = None
        if self.pieModel == None:
            self.__pieModelType = self.pieType
            pieName = ToontownBattleGlobals.pieNames[self.pieType]
            self.pieModel = BattleProps.globalPropPool.getProp(pieName)
            self.pieScale = self.pieModel.getScale()
        return self.pieModel

    def getPresentPieInterval(self, x, y, z, h):
        from toontown.toonbase import ToontownBattleGlobals
        from toontown.battle import BattleProps
        from toontown.battle import MovieUtil
        pie = self.getPieModel()
        pieName = ToontownBattleGlobals.pieNames[self.pieType]
        pieType = BattleProps.globalPropPool.getPropType(pieName)
        animPie = Sequence()
        pingpongPie = Sequence()
        if pieType == 'actor':
            animPie = ActorInterval(pie, pieName, startFrame=0, endFrame=31)
            pingpongPie = Func(pie.pingpong, pieName, fromFrame=32, toFrame=47)
        partName = None
        if self.playingAnim != 'neutral':
            partName = 'torso'
        track = Sequence(Func(self.setPosHpr, x, y, z, h, 0, 0), Func(pie.reparentTo, self.rightHand), Func(pie.setPosHpr, 0, 0, 0, 0, 0, 0), Parallel(pie.scaleInterval(1, self.pieScale, startScale=MovieUtil.PNT3_NEARZERO), ActorInterval(self, 'throw', startFrame=0, endFrame=31, partName=partName), animPie), Func(self.pingpong, 'throw', fromFrame=32, toFrame=45, partName=partName), pingpongPie)
        return track

    def getTossPieInterval(self, x, y, z, h, power, throwType, beginFlyIval = Sequence()):
        from toontown.toonbase import ToontownBattleGlobals
        from toontown.battle import BattleProps
        pie = self.getPieModel()
        flyPie = pie.copyTo(NodePath('a'))
        pieName = ToontownBattleGlobals.pieNames[self.pieType]
        pieType = BattleProps.globalPropPool.getPropType(pieName)
        animPie = Sequence()
        if pieType == 'actor':
            animPie = ActorInterval(pie, pieName, startFrame=48)
        sound = loader.loadSfx('phase_3.5/audio/sfx/AA_pie_throw_only.ogg')
        if throwType == ToontownGlobals.PieThrowArc:
            t = power / 100.0
            dist = 100 - 70 * t
            time = 1 + 0.5 * t
            proj = ProjectileInterval(None, startPos=Point3(0, 0, 0),
                                      endPos=Point3(0, dist, 0), duration=time)
            relVel = proj.startVel
        elif throwType == ToontownGlobals.PieThrowLinear:
            magnitude = power / 2. + 25
 
            relVel = Vec3(0, 1, 0.25)
            relVel.normalize()
            relVel *= magnitude

        def getVelocity(toon = self, relVel = relVel):
            return render.getRelativeVector(toon, relVel)
        partName = None
        oldanim = self.playingAnim
        if self.playingAnim != 'neutral':
            partName = 'torso'
        toss = Track((0, Sequence(Func(self.setPosHpr, x, y, z, h, 0, 0), Func(pie.reparentTo, self.rightHand), Func(pie.setPosHpr, 0, 0, 0, 0, 0, 0), Parallel(ActorInterval(self, 'throw', startFrame=48, partName=partName), animPie), Func(self.loop, oldanim))), (16.0 / 24.0, Func(pie.detachNode)))
        fly = Track((14.0 / 24.0, SoundInterval(sound, node=self)), (16.0 / 24.0, Sequence(Func(flyPie.reparentTo, render), Func(flyPie.setScale, self.pieScale), Func(flyPie.setPosHpr, self, 0.52, 0.97, 2.24, 89.42, -10.56, 87.94), beginFlyIval, ProjectileInterval(flyPie, startVel=getVelocity, duration=3), Func(flyPie.detachNode))))
        return (toss, fly, flyPie)

    def getPieSplatInterval(self, x, y, z, pieCode):
        from toontown.toonbase import ToontownBattleGlobals
        from toontown.battle import BattleProps
        pieName = ToontownBattleGlobals.pieNames[self.pieType]
        splatName = 'splat-%s' % pieName
        if pieName == 'wedding-cake':
            splatName = 'splat-birthday-cake'
        if pieName == 'lawbook':
            splatName = 'dust'
        splat = BattleProps.globalPropPool.getProp(splatName)
        splat.setBillboardPointWorld(2)
        color = ToontownGlobals.PieCodeColors.get(pieCode)
        if color:
            splat.setColor(*color)
        vol = 1.0
        if pieName == 'lawbook':
            sound = loader.loadSfx('phase_11/audio/sfx/LB_evidence_miss.ogg')
            vol = 0.25
        else:
            sound = loader.loadSfx('phase_4/audio/sfx/AA_wholepie_only.ogg')
        ival = Parallel(Func(splat.reparentTo, render), Func(splat.setPos, x, y, z), SoundInterval(sound, node=splat, volume=vol), Sequence(ActorInterval(splat, splatName), Func(splat.detachNode)))
        return ival

    def cleanupPieModel(self):
        if self.pieModel != None:
            self.pieModel.detachNode()
            self.pieModel = None

    def getFeedPetIval(self):
        return Sequence(ActorInterval(self, 'feedPet'), Func(self.animFSM.request, 'neutral'))

    def getScratchPetIval(self):
        return Sequence(ActorInterval(self, 'pet-start'), ActorInterval(self, 'pet-loop'), ActorInterval(self, 'pet-end'))

    def getCallPetIval(self):
        return ActorInterval(self, 'callPet')

    def enterGolfPuttLoop(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = []):
        self.loop('loop-putt')

    def exitGolfPuttLoop(self):
        self.stop()

    def enterGolfRotateLeft(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = []):
        self.loop('rotateL-putt')

    def exitGolfRotateLeft(self):
        self.stop()

    def enterGolfRotateRight(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = []):
        self.loop('rotateR-putt')

    def exitGolfRotateRight(self):
        self.stop()

    def enterGolfPuttSwing(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = []):
        self.loop('swing-putt')

    def exitGolfPuttSwing(self):
        self.stop()

    def enterGolfGoodPutt(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = []):
        self.loop('good-putt', restart=0)

    def exitGolfGoodPutt(self):
        self.stop()

    def enterGolfBadPutt(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = []):
        self.loop('badloop-putt', restart=0)

    def exitGolfBadPutt(self):
        self.stop()

    def enterFlattened(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = []):
        Emote.globalEmote.disableAll(self)
        sound = loader.loadSfx('phase_9/audio/sfx/toon_decompress.ogg')
        lerpTime = 0.1
        node = self.getGeomNode().getChild(0)
        self.origScale = node.getScale()
        self.track = Sequence(LerpScaleInterval(node, lerpTime, VBase3(2, 2, 0.025), blendType='easeInOut'))
        self.track.start(ts)
        self.setActiveShadow(1)

    def exitFlattened(self):
        self.playingAnim = 'neutral'
        if self.track != None:
            self.track.finish()
            DelayDelete.cleanupDelayDeletes(self.track)
            self.track = None
        node = self.getGeomNode().getChild(0)
        node.setScale(self.origScale)
        Emote.globalEmote.releaseAll(self)

    def enterCogThiefRunning(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = []):
        self.playingAnim = None
        self.playingRate = None
        self.standWalkRunReverse = (('neutral', 1.0),
         ('run', 1.0),
         ('run', 1.0),
         ('run', -1.0))
        self.setSpeed(self.forwardSpeed, self.rotateSpeed)
        self.setActiveShadow(1)

    def exitCogThiefRunning(self):
        self.standWalkRunReverse = None
        self.stop()
        self.motion.exit()

    def enterScientistJealous(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = []):
        self.loop('scientistJealous')

    def exitScientistJealous(self):
        self.stop()

    def enterScientistEmcee(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = []):
        self.loop('scientistEmcee')

    def exitScientistEmcee(self):
        self.stop()

    def enterScientistWork(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = []):
        self.loop('scientistWork')

    def exitScientistWork(self):
        self.stop()

    def enterScientistLessWork(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = []):
        self.loop('scientistWork', fromFrame=319, toFrame=619)

    def exitScientistLessWork(self):
        self.stop()

    def enterScientistPlay(self, animMultiplier = 1, ts = 0, callback = None, extraArgs = []):
        self.loop('scientistGame')

    def exitScientistPlay(self):
        self.stop()


loadModels()
compileGlobalAnimList()
