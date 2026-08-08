def _normalise(value):
    if value is None:
        return ''
    return ''.join([char.lower() for char in str(value) if char.isalnum()])


def _getStateName(owner):
    try:
        return owner.getCurrentState().getName()
    except:
        return getattr(owner, 'state', '')


def _isSkippable(owner):
    stateKey = _normalise(_getStateName(owner))
    for word in ('victory', 'reward', 'epilogue', 'defeat', 'elevator'):
        if word in stateKey:
            return False
    if stateKey in ('battleone', 'battletwo', 'battlethree', 'battlefour'):
        return False
    for word in ('introduction', 'preparebattle', 'rolltobattle'):
        if word in stateKey:
            return True
    return False


def reset(owner):
    owner.cutsceneSkipVoters = []
    owner.cutsceneSkipTriggered = False


def _ensure(owner):
    if not hasattr(owner, 'cutsceneSkipVoters'):
        owner.cutsceneSkipVoters = []
    if not hasattr(owner, 'cutsceneSkipTriggered'):
        owner.cutsceneSkipTriggered = False


def _sendState(owner):
    involvedToons = getattr(owner, 'involvedToons', [])
    playerTotal = max(1, len(involvedToons))
    validVoters = []
    for avId in owner.cutsceneSkipVoters:
        if avId in involvedToons and avId not in validVoters:
            validVoters.append(avId)
    owner.cutsceneSkipVoters = validVoters
    voteTotal = len(validVoters)
    owner.sendUpdate('setVoteSkips', [voteTotal, playerTotal])
    if voteTotal >= playerTotal and not owner.cutsceneSkipTriggered:
        owner.cutsceneSkipTriggered = True
        owner.sendUpdate('setCutsceneSkip', [])


def requestSkip(owner):
    _ensure(owner)
    if owner.cutsceneSkipTriggered or not _isSkippable(owner):
        return
    avId = owner.air.getAvatarIdFromSender()
    if avId not in getattr(owner, 'involvedToons', []):
        return
    if avId in owner.cutsceneSkipVoters:
        return
    owner.cutsceneSkipVoters.append(avId)
    _sendState(owner)


def toonLeft(owner, avId):
    _ensure(owner)
    if avId in owner.cutsceneSkipVoters:
        owner.cutsceneSkipVoters.remove(avId)
    if not owner.cutsceneSkipTriggered and _isSkippable(owner):
        _sendState(owner)
