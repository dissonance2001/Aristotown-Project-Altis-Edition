from direct.interval.IntervalGlobal import Func, Parallel, Sequence, Wait

from toontown.cutscene.AltisCutsceneCompat import (
    cacheResolvedControls,
    loadAndValidateAdditionalAnimations,
)
from toontown.cutscene.repository.CutsceneRuntime import buildCutscene
from toontown.cutscene.ResolvedActorInterval import ResolvedActorInterval


CUTSCENE_PATH = 'phase_9/data/cutscenes/pacesetter/pacesetter_rushjob.ctsc'
RUSH_JOB_ANIM_PATH = 'phase_9/models/char/suitB-rushjob'


def _preparePacesetterAnimations(pacesetter):
    if getattr(pacesetter.style, 'body', None) != 'b':
        raise RuntimeError(
            '[Pacesetter Rush Job CTSC] Expected Pacesetter to use Suit B body.')

    additional = {
        'rushjob': RUSH_JOB_ANIM_PATH,
    }
    loadAndValidateAdditionalAnimations(
        pacesetter,
        additional,
        'Pacesetter Clash Rush Job body animation',
        logPrefix='[Pacesetter Rush Job CTSC]')

    animMap = pacesetter.generateAnimDict().copy()
    animMap.update(additional)
    controls = cacheResolvedControls(
        pacesetter,
        ('rushjob',),
        'Pacesetter Clash Rush Job body',
        logPrefix='[Pacesetter Rush Job CTSC]')
    return animMap, controls


def _beginRushJobAnimation(pacesetter, control):
    try:
        pacesetter.stop(None, 'modelRoot')
    except:
        pass
    try:
        control.stop()
    except:
        pass
    try:
        control.setPlayRate(1.0)
    except:
        pass


def makePacesetterRushJob(pacesetter, target, battle, duration):
    toons = list(getattr(battle, 'activeToons', []))
    while len(toons) < 4:
        toons.append(None)

    pacesetterAnimMap, pacesetterControls = _preparePacesetterAnimations(
        pacesetter)
    rushJobControl = pacesetterControls['rushjob']

    cutsceneDict = {
        'nodes': [render, hidden, camera, battle, pacesetter, target],
        'affectsCamera': True,
        'maxPlayers': 4,
        'toons': toons[:4],
        'suits': [pacesetter, target],
        'actors': [],
        'messages': [],
        'sounds': [],
        'music': [],
        'particles': [],
        'visualEffects': [],
        'functions': [],
        'arguments': [],
        'bosses': [],
        'elevators': [],
        'suppressSuitNametags': False,
        'suitAnimationMaps': [pacesetterAnimMap, {}],
        'suitAnimationControls': [pacesetterControls, {}],
    }

    cutsceneTrack = buildCutscene(CUTSCENE_PATH, cutsceneDict)
    rushJobTrack = ResolvedActorInterval(
        pacesetter, 'rushjob', rushJobControl, forceUpdate=1)
    return Parallel(
        Sequence(
            Func(_beginRushJobAnimation, pacesetter, rushJobControl),
            Parallel(cutsceneTrack, rushJobTrack),
            Func(pacesetter.loop, 'neutral'),
        ),
        Wait(duration),
    )
