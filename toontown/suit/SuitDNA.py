import random
from pandac.PandaModules import *
from direct.directnotify.DirectNotifyGlobal import *
from toontown.toonbase import TTLocalizer
import random
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator
from otp.avatar import AvatarDNA
notify = directNotify.newCategory('SuitDNA')
suitHeadTypes = ['f',
 'p',
 'ym',
 'mm',
 'ds',
 'hh',
 'cr',
 'tbc',
 'trb',
 'dot',
                 'dvg',
                 'cpl',
                 'bkp',
                 'kpn',
 'cg',
 'bg',
 'msr',
 'kb',
 'ts',
                 'tc',
                 'tg',
                 'tb',
                 'adc',
                 'drm',
                 'cp',
                 'fbd',
                 'frs',
                 'gtk',
 'bf',
 'b',
 'dt',
 'ac',
 'bs',
 'sd',
 'le',
 'bw',
 'brv',
 'sb',
                 'cfp',
                 'arb',
                 'sjg',
                 'lsc',
 'jdg',
 'jur',
 'tlr',
 'cm',
 'ggm',
                 'th',
                 'kc',
                 'tr',
                 'mp',
                 'laa',
                 'scg',
                 'csm',
                 'ste',
                 'lit',
 'sc',
 'pp',
 'tw',
 'bc',
 'nc',
 'mb',
 'ls',
 'rb',
 'gm',
 'ad',
                 'cvy',
                 'ptr',
                 'mld',
                 'pht',
 'csh',
 'bgr',
 'mes',
 'dm',
 'tcc',
                 'fb',
                 'jl',
                 'gb',
                 'lbs',
                 'trk',
                 'dsf',
                 'msp',
                 'mad',
                 'crf',
 'cc',
 'tm',
 'nd',
 'gh',
 'ms',
 'tf',
 'm',
 'mh',
 'ka',
 'mka',
                 'trm',
                 'ssm',
                 'isw',
                 'ssr',
 'fas',
 'mdr',
 'nar',
 'fd',
 'fm',
                 'jb',
                 'jg',
                 'jr',
                 'prr',
                 'blr',
                 'dvp',
                 'dsk',
                 'ffm',
                 'sft',
'ca',
 'cn',
 'sw',
 'mdm',
 'txm',
 'mg',
 'bfh',
 'hho',
                 'bdb',
                 'bgh',
                 'dfh',
                 'rng',
                 'cps',
                 'tld',
                 'gkp',
                 'ddv',
                 'dty',
                 'dfg',
                 'dfr',
                 'bsh',
                 'ghd',
                 'tyh',
                 'jgd',
                 'bby',
                 'dvk',
                 'otm',
                 'cry',
                 'tcm',
                 'skd',
                 'cmk',
                 'phs',
                 'vpr',
                 'kyl',
                 'sdb',
                 'gry',
                 'kbc',
                 'shp',
                 'sfs',
                 'pyc',
                 'inw',
                 'sys',
                 'rus',
                 'ant',
                 'sya',
                 'yuh',
                 'yhi',
                 'jas',
                 'tas',
                 'fhu',
                 'fsh',
                 'fhj',
                 'kdh',
                 'dar',
                 'nhy',
                 'wrt',
                 'auh']
suitATypes = [
'mm',
'ds',
              'dot',
              'trb',
              'bkp',
              'kpn',
              'vpr',
              'kyl',
              'sfs',
              'pyc',
              'sys',
              'rus',
              'sya',
              'yhi',
              'jas',
              'tas',
              'fhu',
              'fsh',
              'fhj',
              'kdh',
              'nhy',
              'wrt',
              'auh',
              'arb',
              'sjg',
              'lsc',
              'ssm',
              'ssr',
              'rng',
              'cps',
              'tld',
              'cg',
              'bg',
              'msr',
              'kb',
              'ts',
              'tc',
              'adc',
              'drm',
              'cp',
              'frs',
              'gtk',
              'ac',
              'bs',
              'arb',
              'sjg',
              'lsc',
              'kc',
              'laa',
              'csm',
              'ste',
              'lit',
              'pp',
            'tw',
              'nc',
              'rb',
              'cvy',
              'pht',
              'gb',
              'lbs',
              'dsf',
              'mad',
              'crf',
              'gh',
              'ms',
              'ka',
              'ssm',
              'cr',
              'isw',
              'ssr',
              'mka',
              'mdr',
              'dsk',
              'ffm',
              'ssr',
              'txm',
              'mg',
              'rng',
              'cps',
              'csh',
              'tld',
              'ddv',
              'dfg',
              'prr',
              'tb',
              'gm',
              'blr',
              'bsh',
              'tyh',
              'fbd',
              'msp',
              'jgd',
              'fas',
              'tlr',
              'jdg',
              'jb',
              'gkp',
    'ls',
              'bby',
    'm',
              'dvk',
              'ghd',
              'cry',
              'tcm']
suitBTypes = ['p',
              'tbc',
              'b',
              'dt',
              'cfp',
              'sd',
              'tm',
              'nd',
              'bw',
              'bdb',
              'dvp',
              'mb',
              'ptr',
              'kbc',
              'shp',
              'inw',
              'ant',
              'sb',
              'gry',
              'dar',
              'dfr',
              'ms',
              'pht',
              'cn',
              'mh',
              'mdm',
              'fm',
              'jur',
              'ggm',
              'th',
              'mes',
              'tr',
              'mp',
              'scg',
              'otm',
              'sdb',
              'isw',
              'fb',
              'sft',
              'jg']
suitCTypes = ['f',
              'hh',
              'cpl',
              'le',
              'brv',
              'dty',
'ym',
              'nar',
              'cm',
              'bfh',
              'yuh',
              'ca',
              'bf',
              'jr',
              'sw',
              'phs',
              'dvg',
              'trb',
              'hho',
              'bgh',
              'dfh',
              'tf',
              'skd',
              'cmk',
              'tg',
              'trm',
              'mb',
              'cvy',
              'bw',
              'sc',
              'bc',
              'bgr',
              'ad',
              'mld',
              'dm',
              'tcc',
              'jl',
              'trk',
              'cc',
              'nar',
              'fd']
suitDepts = ['c', 'l', 'm', 's', 'g', 't']
suitDeptFullnames = {'c': TTLocalizer.Bossbot,
 'l': TTLocalizer.Lawbot,
 'm': TTLocalizer.Cashbot,
 's': TTLocalizer.Sellbot,
 'g': TTLocalizer.Boardbot,
 't': TTLocalizer.Techbot
                     }
suitDeptFullnamesP = {'c': TTLocalizer.BossbotP,
 'l': TTLocalizer.LawbotP,
 'm': TTLocalizer.CashbotP,
 's': TTLocalizer.SellbotP,
 'g': TTLocalizer.BoardbotP,
 't': TTLocalizer.TechbotP}
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
  5: '**/BoardIcon'
                      }
corpPolyColor = VBase4(0.95, 0.75, 0.75, 1.0)
legalPolyColor = VBase4(0.75, 0.75, 0.95, 1.0)
moneyPolyColor = VBase4(0.65, 0.95, 0.85, 1.0)
salesPolyColor = VBase4(0.95, 0.75, 0.95, 1.0)
boardPolyColor = VBase4(.45, 0.45, .45, 1.0)
techPolyColor = VBase4(0.6, 0.48, 0.7, 1.0)
suitsPerLevel = [1,
 1,
 1,
 1,
 1,
 1,
 1,
 1,
 1,
 1,
 1,
 1,
 1,
 1,
 1,
 1,
 1,
 1,
 1,
 1,
 1,
                 1,
                 1,
                 1,
 1,
 1,
 1,
 1]
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
        print 'Unknown body type for suit name: ', name

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
    if level <= 18:
        returnval = random.randint(7, 13)
    elif level > 18:
        returnval = random.randint(12, 14)
    elif level > 20:
        returnval = 14
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
            dg.addFixedString(self.name, 3)
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
            self.name = dgi.getFixedString(3)
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