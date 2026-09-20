"""SuitDNA module: contains the methods and definitions for describing
multipart actors with a simple class"""

from typing import Iterable
from toontown.clashbattle.battle.SuitBattleGlobals import COG_DEPARTMENTS
from toontown.clashsuit.suit.SuitDefinitionsBase import suitGetAllNamesCode, suitGetFemales
from toontown.toonbase import TTLocalizer
import random
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator
from toontown.clashsuit.suit import SuitGlobals
from otp.avatar import AvatarDNA
from toontown.utils.DirectNotifyCategory import getNotify

notify = getNotify('SuitDNA')

# suit defines
allSuitNames = suitGetAllNamesCode()

suitHeadTypes = [
    #
    # warning: changes to this list will affect *Suit* methods below.
    # We also depend on this ordering in the battle exp system.
    # Boardbot
    'bgh', 'pph', 'ins', 'cbr', 'dl', 'shw', 'mg', 'hho',
    # Bossbot
    'f', 'p', 'ym', 'mm', 'ds', 'hh', 'cr', 'tbc',
    # Lawbot
    'bf', 'b', 'dt', 'ac', 'bs', 'sd', 'le', 'bw',
    # Cashbot
    'sc', 'pp', 'tw', 'bc', 'nc', 'mb', 'ls', 'rb',
    # Sellbot
    'cc', 'tm', 'nd', 'gh', 'ms', 'tf', 'mi', 'mh'
    ]

smallSuitHeadTypes = [  # This list will be used on the main menu screen, to ensure clipping with the tunnel/sidewalk doesn't occur
    # Boardbot
    'bgh', 'pph', 'ins', 'cbr', 'dl',
    # Bossbot
    'f', 'p', 'ym', 'mm', 'ds',
    # Lawbot
    'bf', 'b', 'dt', 'ac', 'bs',
    # Cashbot
    'sc', 'pp', 'tw', 'bc', 'nc',
    # Sellbot
    'cc', 'tm', 'nd', 'gh', 'ms', 'tf'
    ]

suitAlternates = [
    [], [], [], [], [], [], [], [],
    [], [], [], [], [], [], [], [],
    [], ['pf'], ['nn', 'pf'], ['cv', 'nn'], ['ad', 'nn'], ['sh', 'ad'], ['br', 'ad'], [],
    [], [], [], [], [], [], [], [],
    [], [], [], [], [], [], [], []
    ]

# Populate list with all added alternates
allAlternates = ['pf', 'nn', 'cv', 'ad', 'sh', 'br']

# Dynamically set ids for all suit brush offs and face offs at runtime.
TTL = TTLocalizer
currId = 20000
startId = currId
for brushOff in TTL.SuitBrushOffs[None]:
    TTL.SpeedChatStaticText[currId] = brushOff
    if TTL.SuitBrushOffs[None].index(brushOff) != len(TTL.SuitBrushOffs[None]) - 1:
        currId += 1

TTL.SCMenuCommonCogIndices = (startId, currId)
currId += 1

for suitName in suitHeadTypes + allAlternates:
    startId = currId

    brushOffs = TTL.SuitBrushOffs.get(suitName, [])
    for brushOff in brushOffs:
        TTL.SpeedChatStaticText[currId] = brushOff
        if brushOffs.index(brushOff) != len(brushOffs) - 1 or len(brushOffs) == 1:
            currId += 1

    faceOffs = TTL.ClashSuitFaceoffTaunts[suitName]
    for faceOff in faceOffs:
        TTL.SpeedChatStaticText[currId] = faceOff
        if faceOffs.index(faceOff) != len(faceOffs) - 1:
            currId += 1

    TTL.SCMenuCustomCogIndices[suitName] = (startId, currId)
    currId += 1

del currId
del startId

# Use the key values of the cog departments dictionary.
suitDepts = tuple(COG_DEPARTMENTS)
suitDeptTextGraphics = {
    'g': '\1white\1\5boardbotNametag\5\2',
    'c': '\1white\1\5bossbotNametag\5\2',
    'l': '\1white\1\5lawbotNametag\5\2',
    'm': '\1white\1\5cashbotNametag\5\2',
    's': '\1white\1\5sellbotNametag\5\2'
}

suitDeptFullnames = {
    'g': TTLocalizer.Boardbot,
    'c': TTLocalizer.Bossbot,
    'l': TTLocalizer.Lawbot,
    'm': TTLocalizer.Cashbot,
    's': TTLocalizer.Sellbot
    }

suitDeptFullnamesP = {
    'g': TTLocalizer.BoardbotP,
    'c': TTLocalizer.BossbotP,
    'l': TTLocalizer.LawbotP,
    'm': TTLocalizer.CashbotP,
    's': TTLocalizer.SellbotP
    }

bossToDept = {
    'vp': 's',
    'cfo': 'm',
    'clo': 'l',
    'ceo': 'c',
    'chairman': 'g'
}

suitDeptModelPaths = {
    'g': '**/BoardIcon', 0: '**/BoardIcon',
    'c': '**/CorpIcon', 1: '**/CorpIcon',
    'l': '**/LegalIcon', 2: '**/LegalIcon',
    'm': '**/MoneyIcon', 3: '**/MoneyIcon',
    's': '**/SalesIcon', 4: '**/SalesIcon',
    }

suitsPerLevel = [1, 1, 1, 1, 1, 1, 1, 1, 1]
suitsPerDept = 8

goonTypes = ['pg', 'sg', 'gg']
femaleCogs = suitGetFemales()


def getSuitBodyType(name):
    """getSuitBodyType(string):
    Given a suit name, return its body type (a, b, or c)
    """
    if name in SuitGlobals.suitProperties:
        return SuitGlobals.suitProperties.get(name)[SuitGlobals.BODY_INDEX]

    notify.warning(f'Unknown body type for suit name: {name}')


def getSuitDept(name):
    """getSuitDept(string):
    Given a suit name, return its department name as a string
    """
    if name in SuitGlobals.suitProperties:  # Continues here if it isn't found in regular suits
        return SuitGlobals.suitProperties.get(name)[SuitGlobals.DEPT_INDEX]
    else:
        print('Unknown dept for suit name: ', name)
    return 


def getDeptTextGraphic(dept):
    """getDeptFullname(string):
    Given a dept code, return the fullname
    """
    return suitDeptTextGraphics[dept]


def getDeptFullname(dept):
    """getDeptFullname(string):
    Given a dept code, return the fullname
    """
    return suitDeptFullnames[dept]


def getDeptFullnameP(dept):
    """getDeptFullnameP(string):
    Given a dept code, return the fullname (plural)
    """
    return suitDeptFullnamesP[dept]


def getSuitDeptFullname(name):
    """getSuitDept(string):
    Given a suit code, return the fullname
    """
    return suitDeptFullnames[getSuitDept(name)]


def getSuitType(name):
    """getSuitType(string):
    Given a suit name, return its type index (1..8).
    """
    if name in suitHeadTypes:  # Regular suits
        index = suitHeadTypes.index(name)
        return index % suitsPerDept + 1
    else:
        retIndex = -1
        index = 0
        for altList in suitAlternates:  # Iterate through alternates
            if name in altList:
                retIndex = index
                break
            index += 1
        if retIndex == -1:  # Special Cog
            return 100
        else:  # Alternate was found
            return retIndex % suitsPerDept + 1


def getSuitName(deptIndex, typeIndex):
    return suitHeadTypes[(suitsPerDept*deptIndex) + typeIndex]


def getRandomSuitType(level, rng = random):
    """ given a suit level, return a randomly-chosen suit type """
    if level <= 8:
        returnval = random.randint(max(level - 4, 1), min(level, 8))
    elif level <= 10:
        returnval = random.choice([5, 6, 7, 8])
    elif level <= 12:
        returnval = random.choice([6, 7, 8])
    elif level <= 15:
        returnval = random.choice([7, 8])
    else:
        returnval = 8

    return returnval


def isAlternate(name):
    for alternateList in suitAlternates:
        if name in alternateList:
            return True
    return False


def getBaseCog(alternateName):
    index = -1
    for alternateList in suitAlternates:
        if alternateName in alternateList:
            index = suitAlternates.index(alternateList)
    if index == -1:
        return None
    else:
        return suitHeadTypes[index]


def getAlternateCog(baseName):
    if baseName not in suitHeadTypes:
        return None
    index = suitHeadTypes.index(baseName)
    if suitAlternates[index]:
        return suitAlternates[index][0]
    return None


def getRandomSuitByDept(dept):
    """ given a suit dept, return a randomly-chosen suit """
    deptNumber = suitDepts.index(dept)
    return suitHeadTypes[suitsPerDept * deptNumber + random.randint(0, 7)]


def getSuitsInDept(dept: str, minRank: int = 0, maxRank: int = suitsPerDept):
    """
    Returns a list of suitHeads from `dept`, within `minRank` and `maxRank`

    :param dept: The department from which to retrieve suitHeads
    :param minRank: The lowest Suit-rank to retrieve (0-indexed, inclusive)
    :param maxRank: The highest Suit rank to retrieve (0-indexed, exclusive)
    :return: List of `suitHeadTypes` based on above parameters
    """
    deptNumber = suitDepts.index(dept)
    start = deptNumber * suitsPerDept + minRank
    end = start + (maxRank - minRank)
    return suitHeadTypes[start:end]


def getSuitsInDeptList(deptList: Iterable[str], minRank: int = 0, maxRank: int = suitsPerDept):
    """
    Returns a list of suitHeads from all `dept` in `deptList`, within `minRank` and `maxRank`

    :param deptList: The departments from which to retrieve suitHeads
    :param minRank: The lowest Suit-rank to retrieve (0-indexed, inclusive)
    :param maxRank: The highest Suit rank to retrieve (0-indexed, exclusive)
    :return: List of `suitHeadTypes` based on above parameters
    """
    suitHeadList = []
    for dept in deptList:
        suitHeadList += getSuitsInDept(dept, minRank=minRank, maxRank=maxRank)
    return suitHeadList


class SuitDNA(AvatarDNA.AvatarDNA):
    """SuitDNA class: contains methods for describing avatars with a
    simple class. The SuitDNA class may be converted to lists of strings
    for network transmission. Also, SuitDNA objects can be constructed
    from lists of strings recieved over the network. Some examples are in
    order.

        # create a suit's dna
        dna = AvatarDNA()
        dna.newSuit()             # no args defaults to 'Downsizer'
        dna.newSuit('ym')         # make 'Yes Man' dna
        dna.newSuitRandom(3)      # make a random level 3 suit
        dna.newSuitRandom(3, 'l') # make a random level 3 legal suit

    """
    # special methods

    def __init__(self, str = None, type = None, dna = None, r = None, b = None, g = None):
        """__init__(self, string=None, string=None, string()=None, float=None,
        float=None, float=None)
        SuitDNA contructor - see class comment for usage
        """
        # have they passed in a stringified DNA object?
        if str is not None:
            self.makeFromNetString(str)
        # have they specified what type of DNA?
        elif type is not None:
            if type == 's': # Suit
                self.newSuit()
        else:
            # mark DNA as undefined
            self.type = 'u'

    def __str__(self):
        """__str__(self)
        Avatar DNA print method
        """
        if self.type == 's':
            return 'type = %s\nbody = %s, dept = %s, name = %s' % ('suit',
             self.body,
             self.dept,
             self.name)
        elif self.type == 'b':
            return 'type = boss cog\ndept = %s' % self.dept
        else:
            return 'type undefined'

    # stringification methods
    def makeNetString(self):
        dg = PyDatagram()
        dg.addFixedString(self.type, 1)
        if self.type == 's':
            dg.addFixedString(self.name, 8)
            dg.addFixedString(self.dept, 1)
        elif self.type == 'b': # Boss Cog
            dg.addFixedString(self.dept, 1)
        elif self.type == 'u':
            notify.error('undefined avatar')
        else:
            notify.error('unknown avatar type: ', self.type)
        
        return dg.getMessage()

    def makeFromNetString(self, string):
        dg = PyDatagram(string)
        dgi = PyDatagramIterator(dg)
        self.type = dgi.getFixedString(1)
        if self.type == 's': # Suit
            self.name = dgi.getFixedString(8)
            self.dept = dgi.getFixedString(1)
            self.body = getSuitBodyType(self.name)
        elif self.type == 'b': # Boss Cog
            self.dept = dgi.getFixedString(1)
        else:
            notify.error('unknown avatar type: ', self.type)

    def __defaultGoon(self):
        """__defaultGoon(self)
        Make a goon (normal helmet)
        """
        self.type = 'g'
        self.name = goonTypes[0]

    def __defaultSuit(self):
        """__defaultSuit(self)
        Make a default suit dna
        """
        self.type = 's'
        self.name = 'ds'
        self.dept = getSuitDept(self.name)
        self.body = getSuitBodyType(self.name)

    def newSuit(self, name = None):
        """newSuit(self, string=None)
        If no suit name specified, set the dna for the default suit
        else set the dna for suit specified by the given string.
        """
        if name is None:
            self.__defaultSuit()
        else:
            self.type = 's'
            self.name = name
            self.dept = getSuitDept(self.name)
            self.body = getSuitBodyType(self.name)

    def newBossCog(self, dept):
        self.type = 'b'
        self.dept = dept

    def newSuitRandom(self, level = None, dept = None, invading = False, wantAlts = True, rng: random.Random = None,
                      returnLevel: bool = False):
        """newSuitRandom(self, int=None, string=None, bool=False, bool=True)
        Generate dna for a random suit of random level (unless level
        is specified) and random dept (again, unless specified)
        """
        # Use the random module by default.
        rng = rng or random

        self.type = 's'
        # calculate range to choose from based on the level and dept
        if level is None:
            # pick a random level
            level = rng.choice(list(range(1, len(suitsPerLevel))))
        elif level < 0 or level > len(suitsPerLevel):
            # make sure supplied one is valid
            notify.error('Invalid suit level: %d' % level)
        if dept is None:
            # pick a random dept
            dept = rng.choice(suitDepts)
        self.dept = dept
        index = suitDepts.index(dept)
        base = index * suitsPerDept
        offset = 0
        if level > 1:
            for i in range(1, level):
                offset = offset + suitsPerLevel[i - 1]
        bottom = base + offset
        top = bottom + suitsPerLevel[level - 1]
        self.name = suitHeadTypes[rng.choice(list(range(bottom, top)))]
        suitIndex = suitHeadTypes.index(self.name)
        if not invading:
            if suitAlternates[suitIndex] and wantAlts:
                randNum = rng.random()
                if randNum <= 0.25: # 25% chance to spawn an alternate cog
                    if len(suitAlternates[suitIndex]) > 1:
                        if randNum <= 0.20:
                            self.name = suitAlternates[suitIndex][0] # 80% chance to spawn main variant
                        else:
                            self.name = rng.choice(suitAlternates[suitIndex][1:]) # Rest of the time, pick from the other types
                    else:
                        self.name = suitAlternates[suitIndex][0]
        elif invading != True:
            self.name = invading
        self.body = getSuitBodyType(self.name)
        if returnLevel:
            return level

    def newGoon(self, name = None):
        """newGoon(self, type)
        Return the dna for the goon of this name.  If no name is given
        return the default goon.
        """
        if type is None:
            self.__defaultGoon()
        else:
            self.type = 'g'
            if name in goonTypes:
                self.name = name
            else:
                notify.error('unknown goon type: ', name)

    def getType(self):
        """getType(self)
        Return which type of actor this dna represents.
        """
        if self.type == 's':
            # suit type
            type = 'suit'
        elif self.type == 'b':
            # boss type
            type = 'boss'
        else:
            notify.error('Invalid DNA type: ', self.type)
        
        return type
        
    def isFemale(self):
        return self.name in femaleCogs
