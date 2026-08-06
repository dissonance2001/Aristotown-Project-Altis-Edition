"""Python 2-compatible event registration used by Clash .ctsc files."""

cutsceneEventUniqueId = 0
cutsceneMethodDefs = {}


def getUniqueCutsceneId():
    global cutsceneEventUniqueId
    cutsceneEventUniqueId += 1
    return cutsceneEventUniqueId


def cutsceneSequence(name, enum, hidden=False):
    def cutsceneDecorator(func):
        enumName = getattr(enum, 'name', str(enum))
        cutsceneMethodDefs[enumName] = {
            'name': name,
            'enum': enum,
            'hidden': hidden,
            'method': func,
        }
        return func
    return cutsceneDecorator
