import random
from pandac.PandaModules import *
from direct.directnotify.DirectNotifyGlobal import *
from toontown.toonbase import TTLocalizer
import random
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator
from otp.avatar import AvatarDNA
notify = directNotify.newCategory('SuitDNA')
suitHeadTypes = [
    # Bossbots
'f', 'p', 'stg', 'ym', 'enf', 'mm', 'blh', 'ds', 'mldr', 'hh', 'bsht', 'cr', 'txl', 'tbc', 'autocad', 'clubpres', 'derrman', 'derrhand', 'mplayer', 'fires', 'fbed',
'choreo', 'chainsaw', 'chainsaw2', 'phouse', 'bkeeper', 'wtapper', 'ambass',
    # Lawbots
'bf', 'b', 'pf', 'dt', 'cv', 'ac', 'nn', 'bs', 'ad', 'sd', 'sh', 'le', 'br', 'bw', 'whistleb', 'clerk', 'arbit', 'judy', 'mouthp', 'rainmake', 'whunter', 'erclaim',
'redd', 'wsi', 'sgoat', 'caseman', 'stenog', 'lgator',
    # Cashbots
'sc', 'pp', 'shy', 'tw', 'sw', 'bc', 'fct', 'nc', 'gld', 'mb', 'trs', 'ls', 'bfh', 'rb', 'ovt', 'supervis', 'duckshfl', 'treek', 'styx', 'nix', 'hydra', 'kerberos', 'charon',
'pcrat', 'hroller', 'erfit', 'hrollers', 'hroller2',
    # Sellbots
'cc', 'tm', 'cn', 'nd', 'dc', 'gh', 'fcs', 'ms', 'cnd', 'tf', 'ppl', 'm', 'ksp', 'mh', 'watchm', 'foreman', 'dopr', 'dopa', 'bellring', 'mh2', 'prethink', 'mslacker', 'cinema',
'radiog', 'racket', 'ubuster', 'safesupervis', 'psetter',
    # Boardbots
'bgh', 'pph', 'ca', 'ins', 'mdm', 'cbr', 'txm', 'dl', 'ang', 'shw', 'bfh2', 'mg', 'chw', 'hho', 'chairp', 'bdirector', 'ddiver', 'gatekeep', 'dola', 'dold', 'trainer', 'fmaker',
'jgd', 'bby', 'dking', 'ottoman', 'crystal', 'chairman',
    # Techbots
'skd', 'cmk', 'dhr', 'vpr', 'brn', 'sdb', 'key', 'kbc', 'blk', 'sfs', 'pyc', 'inw', 'itn', 'rus', 'ant', 'sya', 'djockey', 'ptjockey', 'jas', 'tas', 'fhu', 'fsh', 'fhj',
'kdh', 'dar', 'nhy', 'wrt', 'auh',
    # Pressbots
'ppb', 'shb', 'bsd', 'gms', 'sbg', 'hck', 'ath', 'ghw', 'dcw', 'gzt', 'wnk', 'nsh', 'std', 'anc', 'jls', 'pbl', 'director', 'bcaster', 'std2', 'videog', 'prt', 'pla', 'plk', 'plh',
'plg', 'plf', 'pld', 'pls'
]
suitATypes = [
    # Bossbots
'ym', 'enf', 'mldr', 'hh', 'bsht', 'txl', 'tbc', 'autocad', 'clubpres', 'derrman', 'derrhand', 'mplayer', 'fires', 'choreo', 'chainsaw', 'chainsaw2', 'phouse',
'bkeeper', 'wtapper', 'ambass',
    # Lawbots
'dt', 'cv', 'le', 'br', 'bw', 'whistleb', 'arbit', 'whunter', 'wsi', 'caseman', 'stenog', 'lgator',
    # Cashbots
'pp', 'sw', 'nc', 'trs', 'rb', 'ovt', 'kerberos', 'charon', 'hroller', 'erfit', 'hrollers', 'hroller2',
    # Sellbots
'nd', 'dc', 'fcs', 'cnd', 'tf', 'ppl', 'm', 'ksp', 'mh', 'watchm', 'foreman', 'mh2', 'cinema', 'radiog', 'ubuster', 'safesupervis',
    # Boardbots
'mdm', 'cbr', 'mg', 'chw', 'hho', 'chairp', 'bdirector', 'gatekeep', 'fmaker', 'dold', 'dking', 'crystal', 'chairman', 'trainer',
    # Techbots
'vpr', 'brn', 'key', 'sfs', 'pyc', 'itn', 'rus', 'sya',
    # Pressbots
'ghw', 'dcw', 'gzt', 'nsh', 'std', 'anc', 'pbl', 'director', 'bcaster', 'std2', 'videog',
]
suitBTypes = [
    # Bossbots
'p', 'ds', 'blh',
    # Lawbots
'b', 'pf', 'ac', 'bs', 'sd', 'sh', 'clerk', 'mouthp', 'rainmake', 'erclaim', 'redd', 'sgoat',
    # Cashbots
'shy', 'bc', 'gld', 'ls', 'duckshfl', 'nix',
    # Sellbots
'tm', 'cn', 'ms', 'bellring', 'prethink', 'racket', 'psetter',
    # Boardbots
'pph', 'ins', 'ang', 'dola', 'ottoman',
    # Techbots
'kbc', 'blk', 'inw', 'ant',
    # Pressbots
'ppb', 'hck', 'ath', 'wnk', 'jls',
]
suitCTypes = [
    # Bossbots
'f', 'stg', 'mm', 'cr', 'fbed',
    # Lawbots
'bf', 'nn', 'ad', 'judy',
    # Cashbots
'sc', 'tw', 'fct', 'mb', 'bfh', 'supervis', 'treek', 'styx', 'hydra', 'pcrat',
    # Sellbots
'cc', 'gh', 'dopr', 'dopa', 'mslacker',
    # Boardbots
'bgh', 'ca', 'txm', 'dl', 'shw', 'bfh2', 'ddiver',
    # Techbots
'skd', 'cmk', 'dhr', 'sdb', 'djockey', 'ptjockey',
    # Pressbots
'shb', 'bsd', 'gms', 'sbg',
]
suitDepts = ['c', 'l', 'm', 's', 'g', 't', 'p']
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
corpPolyColor = VBase4(0.95, 0.75, 0.75, 1.0)
legalPolyColor = VBase4(0.75, 0.75, 0.95, 1.0)
moneyPolyColor = VBase4(0.65, 0.95, 0.85, 1.0)
salesPolyColor = VBase4(0.95, 0.75, 0.95, 1.0)
boardPolyColor = VBase4(.45, 0.45, .45, 1.0)
techPolyColor = VBase4(0.6, 0.48, 0.7, 1.0)
pressPolyColor = VBase4(0.643, 0.51, 0.525, 1.0)
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


def getSuitDept(name):
    index = suitHeadTypes.index(name)
    if index < suitsPerDept:
        return suitDepts[0]
    elif index < suitsPerDept * 2:
        return suitDepts[1]
    elif index < suitsPerDept * 3:
        return suitDepts[2]
    elif index < suitsPerDept * 4:
        return suitDepts[3]
    elif index < suitsPerDept * 5:
        return suitDepts[4]
    elif index < suitsPerDept * 6:
        return suitDepts[5]
    elif index < suitsPerDept * 7:
        return suitDepts[6]
    else:
        print 'Unknown dept for suit name: ', name

    return


def getDeptFullname(dept):
    return suitDeptFullnames[dept]


def getDeptFullnameP(dept):
    return suitDeptFullnamesP[dept]


def getSuitDeptFullname(name):
    return suitDeptFullnames[getSuitDept(name)]


def getSuitType(name):
    index = suitHeadTypes.index(name)
    return index % suitsPerDept + 1


def getSuitName(deptIndex, typeIndex):
    return suitHeadTypes[(suitsPerDept*deptIndex) + typeIndex]


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

def getSuitsInDept(dept):
    start = dept * suitsPerDept
    end = start + suitsPerDept
    return suitHeadTypes[start:end]

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

    def newSuitRandom(self, level = None, dept = None):
        self.type = 's'
        if level == None:
            level = random.choice(range(1, len(suitsPerLevel)))
        elif level < 0 or level > len(suitsPerLevel):
            notify.error('Invalid suit level: %d' % level)
        if dept == None:
            dept = random.choice(suitDepts)
        self.dept = dept
        index = suitDepts.index(dept)
        base = index * suitsPerDept
        offset = 0
        if level > 1:
            for i in xrange(1, level):
                offset = offset + suitsPerLevel[i - 1]

        bottom = base + offset
        top = bottom + suitsPerLevel[level - 1]
        self.name = suitHeadTypes[random.choice(range(bottom, top))]
        self.body = getSuitBodyType(self.name)

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