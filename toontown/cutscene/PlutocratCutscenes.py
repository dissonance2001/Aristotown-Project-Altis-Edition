from direct.interval.IntervalGlobal import Func, Parallel, Sequence, Wait
from direct.particles.ParticleEffect import ParticleEffect
from panda3d.core import NodePath

from toontown.cutscene.repository.CutsceneRuntime import buildCutscene
from toontown.cutscene.PlutocratCutsceneParticles import getPlutocratParticles
from toontown.distributed import DelayDelete
from toontown.suit import Suit
from toontown.suit import SuitDNA

INTRO_PATH = 'phase_10/data/cutscenes/plutocrat/plutocrat_intro.ctsc'
DEATH_PATH = 'phase_10/data/cutscenes/plutocrat/plutocrat_death.ctsc'
JOIN_GENERIC_PATH = 'phase_10/data/cutscenes/plutocrat/plutocrat_joinbattle_generic.ctsc'
JOIN_PCRAT_PATH = 'phase_10/data/cutscenes/plutocrat/plutocrat_joinbattle_pcrat.ctsc'
HATCH_OPEN_PATH = 'phase_10/data/cutscenes/plutocrat/plutocrat_joinbattle_hatch_open.ctsc'
HATCH_CLOSE_PATH = 'phase_10/data/cutscenes/plutocrat/plutocrat_joinbattle_hatch_close.ctsc'
KICKUP_PATH = 'phase_10/data/cutscenes/plutocrat/plutocrat_investor_kickup.ctsc'
SITDOWN_PATH = 'phase_10/data/cutscenes/plutocrat/plutocrat_investor_sitdown.ctsc'
TRIBUTE_PATH = 'phase_10/data/cutscenes/plutocrat/plutocrat_investor_tribute.ctsc'
USURY_PATH = 'phase_10/data/cutscenes/plutocrat/plutocrat_investor_usury.ctsc'
USURY_FODDER_PATH = 'phase_10/data/cutscenes/plutocrat/plutocrat_investor_usury_fodder.ctsc'
DEEPFREEZE_PATH = 'phase_10/data/cutscenes/plutocrat/plutocrat_deepfreeze_camera.ctsc'
SNOW_START_PATH = 'phase_10/data/cutscenes/plutocrat/plutocrat_snowsquall_start.ctsc'
SNOW_END_PATH = 'phase_10/data/cutscenes/plutocrat/plutocrat_snowsquall_end.ctsc'
SNOW_DAMAGE_PATH = 'phase_10/data/cutscenes/plutocrat/plutocrat_snowsquall_damage.ctsc'

INTRO_DIALOGUE = (
    "As for these three scamps, they haven't joined my system yet.",
    "That's where YOU meteoroids come in, see? I want these three 'persuaded' to-",
    "Hey Don, we've been ratted out!",
    "Oh. Looks like them weasels sent in some muscle.",
    "Ya know, I don't take too kindly to interruptions.  Too much racket.",
    "Ice these deadbeats for me, will ya?",
)

JOIN_DIALOGUE = (
    '...',
    'Hmm.',
    "Y'know, ya mutts are pretty good at this.",
    "Tell ya what, I'll even consider lettin' ya join my crew.",
    "Ya just gotta do whatever I tell ya to do, and I'll make sure no one messes wit' ya.",
    'Whaddaya say?',
    'Your loss, chump!',
    "If that's the case, I'mma launch ya outta town wit ya tails between ya legs!",
)

DEATH_DIALOGUE = (
    "Ya ain't putting me in retrograde, ya dirty rats!",
    "I'M the one who's gonna put ya away for good!",
    'The lot of ya are going straight to the stratosphere!',
    'HIT IT, BOYS!',
    "YA LUGHEADS! THAT'S THE WRONG BUTTON!",
)

DUMMY_DIALOGUE = ('Boo!-booyodididdlyyodoo!',)
INVESTORS = ('charon', 'nix', 'hydra', 'styx', 'kerberos')
LEVELS = {'charon': 25, 'nix': 21, 'hydra': 22, 'styx': 20, 'kerberos': 23, 'pcrat': 38}


def _dict(nodes=None, toons=None, suits=None, actors=None, messages=None,
          sounds=None, particles=None):
    toonList = list(toons or [])
    return {
        'nodes': [render, hidden, camera] + list(nodes or []),
        'affectsCamera': True,
        'maxPlayers': 4,
        'toons': toonList,
        'suits': list(suits or []),
        'actors': list(actors or []),
        'messages': tuple(messages or ()),
        'sounds': list(sounds or []),
        'music': [],
        'particles': list(particles or []),
        'visualEffects': [],
        'functions': [],
        'arguments': [],
        'bosses': [],
        'elevators': [],
        'suppressSuitNametags': True,
        'suitAnimationMaps': [],
        'suitAnimationControls': [],
        'suitHeadAnimationControls': [],
    }


def _toons(ids, cr, delayDeletes=None, label='PlutocratCutscene'):
    result = []
    for toonId in ids:
        toon = cr.doId2do.get(toonId)
        if toon:
            toon.wrtReparentTo(render)
            result.append(toon)
            if delayDeletes is not None:
                delayDeletes.append(DelayDelete.DelayDelete(toon, label))
    return result


def _padToons(toons):
    result = list(toons)
    while len(result) < 4:
        result.append(None)
    return result[:4]


def createLocalSuit(name, level=None, manager=False):
    dna = SuitDNA.SuitDNA()
    dna.newSuit(name)
    suit = Suit.Suit()
    suit.setDNA(dna)
    suit.dna = dna
    suit.doId = -7000 - len(name)
    if level is None:
        level = LEVELS.get(name, 1)
    suit.getActualLevel = lambda level=level: level
    suit.getLevel = lambda level=level: max(0, level - 1)
    suit.getStyleName = lambda name=name: name
    suit.battleTrapProp = None
    if manager:
        try:
            suit.makeManagerSuit()
        except:
            suit.isManager = 1
    try:
        suit.initName()
    except:
        pass
    try:
        suit.setPickable(0)
    except:
        pass
    suit.reparentTo(render)
    suit.loop('neutral')
    _installCannonCompat(suit)
    return suit


def _installCannonCompat(suit):
    if not hasattr(suit, 'makeUnemployed'):
        suit.makeUnemployed = lambda: None
    original = getattr(suit, 'createNameInfo', None)
    def createNameInfo(wantDept=False):
        if original:
            try:
                return original()
            except:
                pass
        try:
            return suit.getName()
        except:
            return 'Cog'
    suit.createNameInfo = createNameInfo
    if not hasattr(suit, 'getActualLevel'):
        suit.getActualLevel = lambda: 1


def makeIntroduction(boss, delayDeletes, investors=None):
    investors = list(investors or [])
    if len(investors) < 3:
        investors = boss._getIntroductionInvestors()
    if len(investors) < 3:
        raise RuntimeError('Plutocrat introduction needs 3 Investors, got %s' % len(investors))
    investors = [investors[1], investors[2], investors[0]]
    for suit in investors:
        suit.wrtReparentTo(render)
        delayDeletes.append(DelayDelete.DelayDelete(suit, 'PlutocratIntroduction'))
    fake = createLocalSuit('pcrat', 38)
    try:
        fake.makeExecutive()
    except:
        pass
    fake.doId = -75
    boss.cutscenePlutocrat = fake
    for speaker in [fake] + investors:
        try:
            speaker.getDialogueArray()
        except:
            pass
    actualToons = _toons(boss.involvedToons, boss.cr, delayDeletes, 'PlutocratIntroduction')
    cutsceneToons = _padToons(actualToons)
    suits = [fake] + investors
    data = _dict(
        nodes=[boss.doorLeft, boss.doorRight],
        toons=cutsceneToons,
        suits=suits,
        actors=suits + actualToons,
        messages=INTRO_DIALOGUE,
        sounds=[loader.loadSfx('phase_9/audio/sfx/CHQ_door_open.ogg'),
                loader.loadSfx('phase_9/audio/sfx/CHQ_door_close.ogg')])
    return Parallel(
        Func(camera.wrtReparentTo, render),
        buildCutscene(INTRO_PATH, data))


def cleanupCutscenePlutocrat(boss):
    fake = getattr(boss, 'cutscenePlutocrat', None)
    if not fake:
        return
    try:
        fake.cleanup()
    except:
        try:
            fake.removeNode()
        except:
            pass
    boss.cutscenePlutocrat = None


def makeJoinPcrat(boss, suit, destNode, toons):
    suit.wrtReparentTo(boss.battleNode)
    data = _dict(
        nodes=[boss.battleNode, destNode, suit],
        toons=_padToons(toons), suits=[suit], actors=[suit],
        messages=JOIN_DIALOGUE)
    toonRefusal = Parallel()
    for toon in toons:
        if toon:
            toonRefusal.append(Sequence(
                Wait(12.5),
                ActorInterval(toon, 'taunt'),
                Func(toon.loop, 'neutral')))
    return Parallel(buildCutscene(JOIN_PCRAT_PATH, data), toonRefusal)


def makeJoinGeneric(boss, suit, destNode):
    suit.wrtReparentTo(boss.battleNode)
    data = _dict(nodes=[boss.battleNode, destNode, suit], suits=[suit])
    return buildCutscene(JOIN_GENERIC_PATH, data)


def makeHatch(boss, opening=True):
    data = _dict(
        nodes=[boss.chuteLeft, boss.chuteRight],
        sounds=[loader.loadSfx('phase_4/audio/sfx/CHQ_FACT_stomper_small.ogg')])
    return buildCutscene(HATCH_OPEN_PATH if opening else HATCH_CLOSE_PATH, data)


def makeKickUp(boss, hydra, target):
    helper = boss.battleNode.attachNewNode('hydraKicknode')
    data = _dict(nodes=[hydra, target, boss.battleNode, helper],
                 suits=[hydra, target], actors=[hydra, target], messages=DUMMY_DIALOGUE)
    return Sequence(
        buildCutscene(KICKUP_PATH, data),
        Func(camera.wrtReparentTo, boss.battleNode),
        Func(helper.removeNode))


def makeTribute(boss, kerberos, target):
    data = _dict(nodes=[kerberos, target, boss.battleNode],
                 suits=[kerberos, target], actors=[kerberos, target], messages=DUMMY_DIALOGUE)
    return buildCutscene(TRIBUTE_PATH, data)


def makeSitdown(boss, styx):
    chairNode = styx.attachNewNode('chairbase')
    table = loader.loadModel('phase_8/models/props/ttcc_prp_pc_table')
    chair = table.find('**/pizza_chair_1')
    chair.reparentTo(styx)
    chair.setPosHpr(0, 0, 0, 0, 0, 0)
    chair.hide()
    table.removeNode()
    subnode = boss.battleNode.attachNewNode('styxSitdownNode')
    data = _dict(nodes=[styx, boss.battleNode, subnode, chair, chairNode],
                 suits=[styx], actors=[styx], messages=DUMMY_DIALOGUE)
    return Sequence(
        buildCutscene(SITDOWN_PATH, data),
        Func(camera.wrtReparentTo, boss.battleNode),
        Func(subnode.removeNode),
        Func(chair.removeNode),
        Func(chairNode.removeNode))


def makeUsury(boss, styx, waiter):
    data = _dict(nodes=[styx, waiter, boss.battleNode],
                 suits=[styx, waiter], actors=[styx, waiter], messages=DUMMY_DIALOGUE)
    return buildCutscene(USURY_PATH, data)


def makeUsuryFodder(boss, styx, fodders):
    fodders = list(fodders)
    data = _dict(nodes=[boss.battleNode, styx] + fodders,
                 suits=[styx] + fodders, actors=[styx] + fodders, messages=DUMMY_DIALOGUE)
    return buildCutscene(USURY_FODDER_PATH, data)


def makeDeepFreeze(boss, plutocrat):
    data = _dict(nodes=[plutocrat, boss.battleNode])
    return buildCutscene(DEEPFREEZE_PATH, data)


def _snowData(boss, plutocrat=None, damage=False):
    actualToons = _toons(boss.involvedToons, boss.cr)
    particles = getPlutocratParticles(('chillyAir', 'chillyFlakes'))
    if damage:
        return _dict(nodes=[boss.battleNode, boss.particleRender],
                     toons=_padToons(actualToons),
                     sounds=[loader.loadSfx('phase_10/audio/sfx/SA_snowsquall_dot.ogg')],
                     particles=particles)
    return _dict(nodes=[plutocrat, boss.battleNode, boss.particleRender],
                 toons=_padToons(actualToons), suits=[plutocrat],
                 actors=actualToons + [plutocrat],
                 sounds=[loader.loadSfx('phase_10/audio/sfx/SA_snowsquall_start.ogg')],
                 particles=particles)


def makeSnowSquall(boss, plutocrat, active):
    data = _snowData(boss, plutocrat, False)
    return buildCutscene(SNOW_START_PATH if active else SNOW_END_PATH, data)


def makeSnowSquallDamage(boss):
    return buildCutscene(SNOW_DAMAGE_PATH, _snowData(boss, None, True))


def makeDeath(boss, plutocrat):
    _installCannonCompat(plutocrat)
    fakeInvestors = [createLocalSuit(name, LEVELS[name], True) for name in INVESTORS]
    boss.deathCutsceneSuits = fakeInvestors
    suits = [plutocrat] + fakeInvestors
    data = _dict(
        nodes=[boss.battleNode, plutocrat, boss.chuteLeft, boss.chuteRight, plutocrat.nametag3d],
        suits=suits, actors=[plutocrat], messages=DEATH_DIALOGUE,
        sounds=[loader.loadSfx('phase_4/audio/sfx/CHQ_FACT_stomper_small.ogg')])
    return buildCutscene(DEATH_PATH, data)


def cleanupDeath(boss):
    for suit in getattr(boss, 'deathCutsceneSuits', ()):
        try:
            suit.cleanup()
        except:
            try: suit.removeNode()
            except: pass
    boss.deathCutsceneSuits = []
