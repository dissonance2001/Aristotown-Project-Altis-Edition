"""EditorGlobals module: contains global editor data"""

from panda3d.core import ConfigVariableBool, ConfigVariableString
from toontown.toonbase import RealmGlobals
from direct.showbase.PythonUtil import uniqueElements

# levels should put themselves into the bboard under this posting
# to assert themselves as the level to be edited by ~edit
EditTargetPostName = 'inGameEditTarget'

EntIdRange = 10000
username2entIdBase = {'CheezedFish': 1 * EntIdRange,
                      'Sketched': 2 * EntIdRange,
                      'Sheep': 3 * EntIdRange,
                      'Goose': 4 * EntIdRange,
                      'Minimus': 5 * EntIdRange,
                      'Loonatic': 6 * EntIdRange,
                      'Salem': 7 * EntIdRange,
                      'user8': 8 * EntIdRange,
                      'user9': 9 * EntIdRange,
                      'user10': 10 * EntIdRange,
                      'user11': 11 * EntIdRange}
usernameConfigVar = 'level-edit-username'
undefinedUsername = 'UNDEFINED_USERNAME'
editUsername = ConfigVariableString(usernameConfigVar, undefinedUsername).getValue()


# call this to make sure things have been set up correctly
def checkNotReadyToEdit():
    # returns error string if not ready, None if ready
    if editUsername == undefinedUsername:
        return "you must config '%s'; see %s.py" % (usernameConfigVar, __name__)
    # Feel free to add your name to the table if it's not in there
    if editUsername not in username2entIdBase:
        return "unknown editor username '%s'; see %s.py" % (editUsername, __name__)

    return None


def assertReadyToEdit():
    msg = checkNotReadyToEdit()
    if msg is not None:
        pass


def getEditUsername():
    return editUsername


def getEntIdAllocRange():
    """range of valid entId values for this user.
    returns [min, max+1] (values taken by range() and xrange())"""
    baseId = username2entIdBase[editUsername]
    return [baseId, baseId + EntIdRange]


def wantLevelEditor():
    return RealmGlobals.getCurrentRealm().isDevRealm() and ConfigVariableBool('want-level-editor', False).getValue()
