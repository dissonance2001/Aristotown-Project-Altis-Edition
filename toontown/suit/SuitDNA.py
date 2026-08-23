import random
from pandac.PandaModules import *
from direct.directnotify.DirectNotifyGlobal import *
from toontown.toonbase import TTLocalizer
import random
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator
from toontown.battle import SuitBattleGlobals
from otp.avatar import AvatarDNA
notify = directNotify.newCategory('SuitDNA')
suitDeptCogs = {
    'c': [
        'f', 'p', 'ym', 'mm','ds', 'hh', 'cr', 'tbc', 
        'stg', 'enf', 'blh', 'ksp', 'psh', 'drk', 'ppg', 'mldr', 'bsht', 'stck', 'txl', 'wnk',
        # Regular Bossbots...
    ],

    'l': [
        'bf', 'b', 'dt', 'ac', 'bs', 'sd', 'le', 'bw',
        'bf2', 'b2', 'dt2', 'ac2', 'bs2', 'sd2', 'le2', 'bw2',
        'bsd', 'dcr', 'dcw', 'bck', 'surg', 'rat', 'magi', 'whistleb',
        'pf', 'cv', 'nn', 'ad', 'sh', 'br', 
        # Regular Lawbots...
    ],

    'm': [
        'sc', 'pp',  'tw', 'bc', 'nc', 'mb', 'ls', 'rb',
        'shy', 'fct', 'gld', 'trs', 'bfh', 'nb', 'qc', 'aud', 'pwn', 'cow', 'brck', 'timer',
        # Regular Cashbots...
    ],

    's': [
        'cc', 'tm', 'nd', 'gh', 'ms', 'tf', 'm', 'mh',
        'sbg', 'dc', 'mad', 'bam', 'lvw', 'fcs', 'ppl', 'cnd', 'std',
        # Regular Sellbots...
    ],

    'g': [
        'bgh', 'pph', 'ins', 'cbr', 'dl', 'shw', 'mg', 'hho',
        'ca', 'mdm', 'txm', 'ang', 'bfh2', 'chw', 'cor', 'sab', 'cn', 'sw', 'rng', 'neg', 'vul', 'stol',
        # Regular Boardbots...
    ],

    't': [
        'skd', 'cmk', 'vpr', 'sdb', 'shrp', 'kbc', 'sfs', 'inw', 'rus',
        'dhr', 'brn', 'key', 'blk', 'pyc', 'itn', 'skd2', 'cmk2', 'pdx', 'phis', 'inw2', 'rus2', 'asm', 'cpu', 'vpr2', 'oilg', 'chg',
        # Regular Techbots...
    ],

    'p': [
        'ppb', 'shb', 'gms', 'hck', 'ghw', 'gzt', 'nsh', 'anc',
        # Regular Pressbots...
    ],
}
suitDeptManagers = {
    'c': [
        'autocad', 'clubpres', 'derrman', 'derrhand',
        'mplayer', 'mplayers', 'fires', 'fbed', 'choreo', 'chainsaw', 'phouse', 'bkeeper', 'wtapper', 'ambass', 'ceo',
    ],

    'l': [
       'clerk', 'judy', 'mouthp', 'rainmake',
        'whunter', 'erclaim', 'redd', 'wsi',
        'sgoat', 'caseman', 'stenog', 'lgator', 'cj', 'clo',
    ],

    'm': [
        'supervis', 'duckshfl', 'treek', 'payman',
        'bookkeep', 'racket', 'liquidr', 'treasure',
        'charon', 'nix', 'hydra', 'styx', 'kerberos',
        'pcrat', 'hroller', 'erfit', 'hrollers', 'hroller2', 'cfo',
    ],

    's': [
        'foreman', 'dopr', 'dopa', 'bellring',
        'mh2', 'prethink', 'mslacker', 'cinema',
        'radiog', 'hustle', 'ubuster', 'safesupervis',
        'psetter', 'std2', 'cnd2', 'vp',
    ],

    'g': [
        'ddiver', 'gatekeep',
        'dola', 'dold', 'liquid', 'rkeeper', 'cbutcher',
        'cdirector', 'dking', 'ottoman', 'fmaker', 'chairman', 'chairman2',
    ],

    't': [
        'djockey', 'ptjockey', 'bcaster', 'videog', 'cio',
    ],

    'p': [
        'director', 'hocn',
    ],
}
# suitHeadTypes = [
#     # Bossbots
# 'f', 'p', 'stg', 'ym', 'enf', 'mm', 'blh', 'ds', 'ksp', 'hh', 'bsht', 'cr', 'txl', 'tbc', 'autocad', 'clubpres', 'derrman', 'derrhand', 'mplayer', 'fires', 'fbed',
# 'choreo', 'chainsaw', 'chainsaw2', 'phouse', 'bkeeper', 'wtapper', 'ambass',
#     # Lawbots
# 'bf', 'b', 'pf', 'dt', 'cv', 'ac', 'nn', 'bs', 'ad', 'sd', 'sh', 'le', 'br', 'bw', 'whistleb', 'clerk', 'arbit', 'judy', 'mouthp', 'rainmake', 'whunter', 'erclaim',
# 'redd', 'wsi', 'sgoat', 'caseman', 'stenog', 'lgator',
#     # Cashbots
# 'sc', 'pp', 'shy', 'tw', 'sw', 'bc', 'fct', 'nc', 'gld', 'mb', 'trs', 'ls', 'bfh', 'rb', 'ovt', 'supervis', 'duckshfl', 'treek', 'payman', 'bookkeep', 'racket', 'liquidr', 'treasure',
# 'pcrat', 'hroller', 'erfit', 'hrollers', 'hroller2',
#     # Sellbots
# 'cc', 'tm', 'cn', 'nd', 'dc', 'gh', 'fcs', 'ms', 'asm', 'tf', 'ppl', 'm', 'cnd', 'mh', 'watchm', 'foreman', 'dopr', 'dopa', 'bellring', 'mh2', 'prethink', 'mslacker', 'cinema',
# 'radiog', 'hustle', 'ubuster', 'safesupervis', 'psetter',
#     # Boardbots
# 'bgh', 'pph', 'ca', 'ins', 'mdm', 'cbr', 'txm', 'dl', 'ang', 'shw', 'bfh2', 'mg', 'chw', 'hho', 'chairp', 'bdirector', 'ddiver', 'gatekeep', 'dola', 'dold', 'liquid', 'rkeeper',
# 'cbutcher', 'cdirector', 'dking', 'ottoman', 'fmaker', 'chairman',
#     # Techbots
# 'skd', 'cmk', 'dhr', 'vpr', 'brn', 'sdb', 'key', 'kbc', 'blk', 'sfs', 'pyc', 'inw', 'itn', 'rus', 'ant', 'sya', 'djockey', 'ptjockey', 'crystal', 'tas', 'fhu', 'fsh', 'fhj',
# 'kdh', 'dar', 'nhy', 'wrt', 'auh',
#     # Pressbots
# 'ppb', 'shb', 'bsd', 'gms', 'sbg', 'hck', 'ath', 'ghw', 'dcw', 'gzt', 'wnk', 'nsh', 'std', 'anc', 'jls', 'pbl', 'director', 'bcaster', 'std2', 'videog', 'prt', 'pla', 'plk', 'plh',
# 'plg', 'plf', 'pld', 'pls'
# ]
suitHeadTypes = []
suitATypes = [
    # Bossbots
'ym', 'enf', 'ksp', 'hh', 'bsht', 'txl', 'tbc', 'autocad', 'clubpres', 'derrman', 'derrhand', 'mplayer', 'mplayers', 'fires', 'choreo', 'chainsaw', 'chainsaw2', 'phouse',
'bkeeper', 'wtapper', 'ambass',
    # Lawbots
'dt', 'cv', 'le', 'br', 'bw', 'bw2', 'le2', 'bs2', 'dt2', 'whistleb', 'whunter', 'wsi', 'caseman', 'stenog', 'lgator',
    # Cashbots
'pp', 'sw', 'nc', 'trs', 'rb', 'payman', 'racket', 'liquidr', 'treasure', 'charon', 'kerberos', 'hroller', 'erfit', 'hrollers', 'hroller2',
    # Sellbots
'nd', 'dc', 'fcs', 'tf', 'ppl', 'm', 'cnd', 'mh', 'watchm', 'foreman', 'mh2', 'cinema', 'radiog', 'hustle', 'ubuster', 'safesupervis',
    # Boardbots
'mdm', 'cbr', 'mg', 'chw', 'hho', 'chairp', 'bdirector', 'gatekeep', 'dold', 'dking', 'fmaker', 'liquid', 'rkeeper', 'cbutcher', 'cdirector',
    # Techbots
'vpr', 'brn', 'key', 'sfs', 'pyc', 'itn', 'rus',
    # Pressbots
'ghw', 'gzt', 'nsh', 'std', 'anc', 'pbl', 'director', 'bcaster', 'std2', 'videog',
]
suitBTypes = [
    # Bossbots
'p', 'ds', 'wnk', 'drk', 'stck', 'ppg', 'psh',
    # Lawbots
'b', 'pf', 'ac', 'bs', 'b2', 'sd2', 'ac2', 'sd', 'sh', 'clerk', 'mouthp', 'rainmake', 'erclaim', 'redd', 'sgoat', 'rat', 'surg',
    # Cashbots
'shy', 'bc', 'gld', 'ls', 'ovt', 'duckshfl', 'nix',
    # Sellbots
'tm', 'cn', 'ms', 'bam', 'bellring', 'prethink', 'psetter',
    # Boardbots
'pph', 'ins', 'ang', 'dola', 'ottoman', 'vul',
    # Techbots
'kbc', 'blk', 'inw', 'ant', 'shrp', 'pdx', 'cpu', 'chg', 'inw2',
    # Pressbots
'ppb', 'hck', 'ath', 'jls',
]
suitCTypes = [
    # Bossbots
'f', 'stg', 'mm', 'blh', 'cr', 'fbed',
    # Lawbots
'bf', 'nn', 'ad', 'judy', 'bf2', 'bsd',
    # Cashbots
'sc', 'tw', 'fct', 'mb', 'bfh', 'supervis', 'treek', 'bookkeep', 'hydra', 'styx', 'pcrat', 'aud', 'cow', 'brck',
    # Sellbots
'cc', 'gh', 'mad', 'asm', 'dopr', 'dopa', 'mslacker',
    # Boardbots
'bgh', 'ca', 'txm', 'dl', 'shw', 'bfh2', 'ddiver', 'chairman',
    # Techbots
'skd', 'cmk', 'dhr', 'sdb', 'djockey', 'ptjockey', 'asm', 'cmk2', 'skd2', 
    # Pressbots
'shb', 'gms', 'sbg',
]
suitDepts = ['c', 'l', 'm', 's', 'g', 't', 'p']
for dept in suitDepts:
    suitHeadTypes.extend(suitDeptCogs.get(dept, []))
    suitHeadTypes.extend(suitDeptManagers.get(dept, []))
suitDeptFullnames = {'c': TTLocalizer.Bossbot,
 'l': TTLocalizer.Lawbot,
 'm': TTLocalizer.Cashbot,
 's': TTLocalizer.Sellbot,
 'g': TTLocalizer.Boardbot,
 't': TTLocalizer.Techbot,
 'p': TTLocalizer.Pressbot
                     }
suitDeptFullnamesP = {'c': TTLocalizer.BossbotP,
 'l': TTLocalizer.LawbotP,
 'm': TTLocalizer.CashbotP,
 's': TTLocalizer.SellbotP,
 'g': TTLocalizer.BoardbotP,
 't': TTLocalizer.TechbotP,
 'p': TTLocalizer.PressbotP
                      }
suitDeptModelPaths = {'c': '**/CorpIcon',
 0: '**/CorpIcon',
 'l': '**/LegalIcon',
 1: '**/LegalIcon',
 'm': '**/MoneyIcon',
 2: '**/MoneyIcon',
 's': '**/SalesIcon',
 3: '**/SalesIcon',
 'g': '**/BoardIcon',
 4: '**/BoardIcon',
 't': '**/BoardIcon',
  5: '**/BoardIcon',
'p': '**/BoardIcon',
 6: '**/BoardIcon'
                      }
corpPolyColor = VBase4(0.839, 0.808, 0.769, 1.0)
legalPolyColor = VBase4(0.784, 0.816, 0.863, 1.0)
moneyPolyColor = VBase4(0.78, 0.808, 0.796, 1.0)
salesPolyColor = VBase4(0.761, 0.714, 0.725, 1.0)
boardPolyColor = VBase4(0.675, 0.761, 0.769, 1.0)
techPolyColor = VBase4(0.675, 0.608, 0.69, 1.0)
pressPolyColor = VBase4(0.647, 0.518, 0.537, 1.0)
suitsPerLevel = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
suitsPerDept = 28
levelsPerSuit = 12
goonTypes = ['pg', 'sg', 'gg']

def getSuitBodyType(name):
    if name in suitATypes:
        return 'a'
    elif name in suitBTypes:
        return 'b'
    elif name in suitCTypes:
        return 'c'
    else:
        return 'a'

    return

suitSpawnTiers = {}

suitTierPools = {
    'c': {
        1: ['f'],
        2: ['p', 'stg'],
        3: ['ym', 'enf', 'psh'],
        4: ['mm'],
        5: ['ds', 'blh', 'stck'],
        6: ['hh', 'bsht', 'mldr', 'ppg'],
        7: ['cr', 'txl', 'ksp', 'wnk', 'drk'],
        8: ['tbc'],
    },

    'l': {
        1: ['bf', 'bf2'],
        2: ['b', 'pf', 'b2', 'bsd'],
        3: ['dt', 'nn', 'dt2', 'dcr'],
        4: ['ac', 'cv', 'ac2'],
        5: ['bs', 'ad', 'bs2', 'bck', 'dcw'],
        6: ['sd', 'sh', 'sd2', 'surg', 'rat'],
        7: ['le', 'br', 'le2', 'magi', 'whistleb'],
        8: ['bw', 'bw2',],
    },

    'm': {
        1: ['sc'],
        2: ['pp', 'shy', 'qc', 'nb'],
        3: ['tw', 'trs', 'pwn'],
        4: ['bc'],
        5: ['nc', 'cow', 'brck'],
        6: ['mb', 'aud'],
        7: ['ls', 'bfh', 'gld', 'fct', 'timer'],
        8: ['rb'],
    },

    's': {
        1: ['cc'],
        2: ['tm', 'sbg'],
        3: ['nd', 'dc'],
        4: ['gh', 'mad'],
        5: ['ms', 'bam', 'lvw'],
        6: ['tf', 'ppl', 'fcs'],
        7: ['m', 'cnd', 'std'],
        8: ['mh'],
    },

    'g': {
        1: ['bgh', 'ca'],
        2: ['pph', 'cn'],
        3: ['ins', 'sw'],
        4: ['cbr', 'mdm'],
        5: ['dl', 'txm', 'neg', 'cor', 'sab'],
        6: ['shw', 'rng', 'vul', 'stol'],
        7: ['mg', 'chw', 'bfh2', 'ang'],
        8: ['hho'],
    },

    't': {
        1: ['skd', 'skd2'],
        2: ['cmk', 'dhr', 'cmk2'],
        3: ['vpr', 'key', 'vpr2', 'pdx'],
        4: ['sdb', 'brn'],
        5: ['kbc', 'blk', 'phis'],
        6: ['sfs', 'pyc', 'shrp', 'oilg'],
        7: ['inw', 'itn', 'asm', 'inw2', 'cpu', 'chg'],
        8: ['rus', 'rus2'],
    },

    'p': {
        1: ['ppb'],
        2: ['shb'],
        3: ['gms'],
        4: ['hck'],
        5: ['ghw'],
        6: ['gzt'],
        7: ['nsh'],
        8: ['anc'],
    },
}

def getSuitsForTier(dept, tier):
    deptPools = suitTierPools.get(dept, {})
    return list(deptPools.get(tier, ()))

def getRandomSuitTierSpawn(level, dept, rng=random):
    possibleTiers = []

    for tier in range(1, 8):
        for suitName in getSuitsForTier(dept, tier):
            minLevel = SuitBattleGlobals.getSuitMinLevel(suitName)
            maxLevel = SuitBattleGlobals.getSuitMaxLevel(suitName)

            if minLevel <= level <= maxLevel:
                possibleTiers.append(tier)
                break

    if not possibleTiers:
        # fallback to the highest available tier
        return 8

    return rng.choice(possibleTiers)


def getRandomSuitForTier(dept, tier):
    choices = getSuitsForTier(dept, tier)

    if not choices:
        notify.warning(
            'No suits configured for department %s tier %s' %
            (dept, tier)
        )
        return None

    return random.choice(choices)

def getSuitDept(name):
    for dept in suitDepts:
        if name in suitDeptCogs.get(dept, ()):
            return dept

        if name in suitDeptManagers.get(dept, ()):
            return dept

    notify.warning('Unknown department for suit: %s' % name)
    return None


def getDeptFullname(dept):
    return suitDeptFullnames[dept]


def getDeptFullnameP(dept):
    return suitDeptFullnamesP[dept]


def getSuitDeptFullname(name):
    return suitDeptFullnames[getSuitDept(name)]


def getSuitType(name):
    for dept, tiers in list(suitTierPools.items()):
        for tier, names in list(tiers.items()):
            if name in names:
                return tier

    # Managers/special Cogs do not need a normal spawn tier.
    return None


def getSuitName(deptIndex, typeIndex):
    dept = suitDepts[deptIndex]
    roster = suitDeptCogs[dept]

    # typeIndex is normally zero-based here.
    if typeIndex < 0 or typeIndex >= len(roster):
        notify.warning(
            'Invalid suit type %s for department %s' %
            (typeIndex, dept)
        )
        return roster[0]

    return roster[typeIndex]


def getRandomSuitType(level, rng = random):
    if level >= 25:
        returnval = 14
    elif level >= 24:
        returnval = random.randint(13, 14)
    elif level >= 21:
        returnval = random.randint(12, 14)
    elif level >= 20:
        returnval = random.randint(11, 14)
    elif level >= 18:
        returnval = random.randint(10, 14)
    elif level >= 16:
        returnval = random.randint(9, 14)
    elif level >= 14:
        returnval = random.randint(7, 14)
    elif level >= 13:
        returnval = random.randint(7, 13)
    elif level >= 12:
        returnval = random.randint(7, 12)
    elif level >= 11:
        returnval = random.choice((5, 7, 8, 9, 10, 11))
    elif level >= 10:
        returnval = random.randint(5, 10)
    elif level >= 9:
        returnval = random.choice((3, 5, 6, 7, 8, 9))
    elif level >= 8:
        returnval = random.randint(3, 8)
    elif level >= 7:
        returnval = random.randint(3, 7)
    elif level >= 6:
        returnval = random.randint(2, 6)
    elif level >= 5:
        returnval = random.randint(1, 5)
    elif level >= 4:
        returnval = random.randint(1, 4)
    elif level >= 3:
        returnval = random.randint(1, 3)
    elif level >= 2:
        returnval = random.randint(1, 2)
    elif level == 1:
        returnval = 1
    else:
        returnval = 14

    return returnval


def getRandomSuitByDept(dept):
    deptNumber = suitDepts.index(dept)
    return suitHeadTypes[suitsPerDept * deptNumber + random.randint(0, 7)]

def getSuitsInDept(dept, includeManagers=True):
    if isinstance(dept, int):
        dept = suitDepts[dept]

    suits = list(suitDeptCogs.get(dept, ()))

    if includeManagers:
        suits.extend(suitDeptManagers.get(dept, ()))

    return suits
    

class SuitDNA(AvatarDNA.AvatarDNA):

    def __init__(self, str = None, type = None, dna = None, r = None, b = None, g = None):
        if str != None:
            self.makeFromNetString(str)
        elif type != None:
            if type == 's':
                self.newSuit()
        else:
            self.type = 'u'

    def __str__(self):
        if self.type == 's':
            return 'type = %s\nbody = %s, dept = %s, name = %s' % ('suit',
             self.body,
             self.dept,
             self.name)
        elif self.type == 'b':
            return 'type = boss cog\ndept = %s' % self.dept
        else:
            return 'type undefined'

    def makeNetString(self):
        dg = PyDatagram()
        dg.addFixedString(self.type, 1)
        if self.type == 's':
            dg.addFixedString(self.name, 20)
            dg.addFixedString(self.dept, 1)
        elif self.type == 'b':
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
        if self.type == 's':
            self.name = dgi.getFixedString(20)
            self.dept = dgi.getFixedString(1)
            self.body = getSuitBodyType(self.name)
        elif self.type == 'b':
            self.dept = dgi.getFixedString(1)
        else:
            notify.error('unknown avatar type: ', self.type)

    def __defaultGoon(self):
        self.type = 'g'
        self.name = goonTypes[0]

    def __defaultSuit(self):
        self.type = 's'
        self.name = 'ds'
        self.dept = getSuitDept(self.name)
        self.body = getSuitBodyType(self.name)

    def newSuit(self, name = None):
        if name == None:
            self.__defaultSuit()
        else:
            self.type = 's'
            self.name = name
            self.dept = getSuitDept(self.name)
            self.body = getSuitBodyType(self.name)

    def newBossCog(self, dept):
        self.type = 'b'
        self.dept = dept

    def getSuitsForTier(dept, tier):
        return [
            name for name in suitDeptCogs.get(dept, ())
            if suitSpawnTiers.get(name) == tier
        ]
    
    def newSuitRandom(self, tier=None, dept=None, name=None):
        self.type = 's'

        # If a specific suit name was supplied, use it directly.
        if name is not None:
            self.name = name
            self.dept = getSuitDept(name)
            self.body = getSuitBodyType(name)
            return

        if dept is None:
            dept = random.choice(suitDepts)

        if tier is None:
            availableTiers = []

            for testTier in range(1, 9):
                if getSuitsForTier(dept, testTier):
                    availableTiers.append(testTier)

            if not availableTiers:
                raise ValueError(
                    'No spawnable suits configured for department %s' %
                    dept
                )

            tier = random.choice(availableTiers)

        choices = getSuitsForTier(dept, tier)

        if not choices:
            raise ValueError(
                'No spawnable suits for department %s tier %s' %
                (dept, tier)
            )

        suitName = random.choice(choices)

        self.name = suitName
        self.dept = dept
        self.body = getSuitBodyType(suitName)

    def newGoon(self, name = None):
        if type == None:
            self.__defaultGoon()
        else:
            self.type = 'g'
            if name in goonTypes:
                self.name = name
            else:
                notify.error('unknown goon type: ', name)

    def getType(self):
        if self.type == 's':
            type = 'suit'
        elif self.type == 'b':
            type = 'boss'
        else:
            notify.error('Invalid DNA type: ', self.type)
        
        return type