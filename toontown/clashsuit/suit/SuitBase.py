"""SuitBase module: contains the SuitBase class"""

from toontown.battle.BattleAvatar import BattleAvatar
from toontown.battle.attacks.base.AttackEnum import AttackEnum
from toontown.suit import SuitDNA
from toontown.suit.SuitLegList import *
from direct.distributed.ClockDelta import *
from toontown.battle import SuitBattleGlobals
from toontown.toonbase import TTLocalizer
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


# extra time to add (in seconds) to any time calculations for path movement
# for each leg
TIME_BUFFER_PER_WPT = 0.25
TIME_DIVISOR = 100

# spread out the creation of this suit's task, helps to prevent
# slowdowns, but causes suits to take longer to get moving
DISTRIBUTE_TASK_CREATION = 0


@DirectNotifyCategory()
class SuitBase(BattleAvatar):
    """
    ////////////////////////////////////////////////////////////////////////
    // SuitBase class:  a 'bad guy' which contains common functionality
    //                  that both a client side and a server side suit can
    //                  use
    //
    // Attributes:
    //
    ////////////////////////////////////////////////////////////////////////
    """

    def __init__(self):
        super().__init__()

        self.dna = None
        self.level = 0
        # This gets initialized to real value in d_setLevel()
        self.maxHp = 10
        self.hp = 10
        self.isSkelecog = 0
        self.isElite = 0
        self.isWaiter = 0
        self.superchargeRatio = 0

        # A dictionary mapping every toon that has hurt the suit
        # with the amount of damage dealt.
        self.aggroMap = {} # type: dict[int, int]

    def delete(self):
        if hasattr(self, 'legList'):
            del self.legList

        self.cleanupBattle()

    def getStyleName(self, doException: bool = True):
        if hasattr(self, 'dna') and self.dna:
            return self.dna.name
        else:
            if doException:
                self.notify.error('called getStyleName() before dna was set!')
            return 'unknown'

    def getStyleDept(self):
        if hasattr(self, 'dna') and self.dna:
            return SuitDNA.getDeptFullname(self.dna.dept)
        else:
            self.notify.error('called getStyleDept() before dna was set!')
            return 'unknown'

    def getLevel(self):
        return self.level

    def setLevel(self, level, hpMultIndex=0):
        self.level = level

        nameLevel = str(self.level)
        if self.isElite:
            nameLevel += TTLocalizer.AvatarSuitPanelExecutive

        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {
            'name': self._name,
            'dept': self.getStyleDept(),
            'level': nameLevel
        }
        self.setDisplayName(nameInfo)
        # Compute maxHp based on level
        attributes = SuitBattleGlobals.SuitAttributes[self.dna.name]
        self.maxHp = SuitBattleGlobals.calculateHp(attributes, self.level, hpMultIndex=hpMultIndex, dnaName=self.dna.name)
        self.hp = self.getMaxHp()

    def getSkelecog(self):
        return self.isSkelecog

    def setSkelecog(self, flag):
        self.isSkelecog = flag

    def setWaiter(self, flag):
        self.isWaiter = flag

    def getElite(self):
        return self.isElite

    def setElite(self, flag):
        self.isElite = flag

    def getActualLevel(self):
        """
        ////////////////////////////////////////////////////////////////////
        // Function:   from the suit's 'relative' level (relative to the
        //             type of suit that this guy is) figure out the suit's
        //             actual level (1-12)
        // Parameters: none
        // Changes:
        ////////////////////////////////////////////////////////////////////
        """

        # NOTE: This function is mostly kept around for legacy compatibility purposes.
        # Nowadays, getLevel() and getActualLevel() return the exact same things.
        return self.level

    def setPath(self, path):
        """
        ////////////////////////////////////////////////////////////////////
        // Function:    set the path to be used by this suit, this function
        //              is called by the SuitPlannerAI
        // Parameters:  path, the path that this suit should use
        // Changes:     none
        ////////////////////////////////////////////////////////////////////
        """
        self.path = path
        self.pathLength = self.path.getNumPoints()

    def getPath(self):
        """
        ////////////////////////////////////////////////////////////////////
        // Function:    set the path to be used by this suit, this function
        //              is called by the SuitPlannerAI
        // Parameters:  path, the path that this suit should use
        // Changes:     none
        ////////////////////////////////////////////////////////////////////
        """
        return self.path

    def printPath(self):
        """
        ////////////////////////////////////////////////////////////////////
        // Function:    print out this suit's current path
        // Parameters:  none
        // Changes:
        ////////////////////////////////////////////////////////////////////
        """
        # print out the path
        print('%d points in path' % self.pathLength)
        for currPathPt in range(self.pathLength):
            indexVal = self.path.getPointIndex(currPathPt)
            print('\t', self.sp.dnaStore.getSuitPointWithIndex(indexVal))

    def makeLegList(self):
        """
        makeLegList(self)
        Fills up self.legList with a list of SuitLeg objects that
        reflect the path previously set via setPath().  See
        suitLegList.h.
        """
        self.legList = SuitLegList(self.path, self.sp.dnaStore)

    def setSuperchargeRatio(self, ratio):
        self.superchargeRatio = ratio

    def resetSuperchargeState(self):
        self.superchargeRatio = 0

    def isSupercharged(self):
        if not self.superchargeRatio:
            return False
        return (self.getHp() / self.getMaxHp()) >= (self.superchargeRatio * 0.999)

    def getDefense(self) -> int:
        """
        Returns the defense (dodge rate) of this suit.
        """
        boost = 5 if self.getElite() else 0
        suitAttr = SuitBattleGlobals.SuitAttributes.get(self.dna.name)
        return SuitBattleGlobals.calculateDefense(suitAttr, self.level, boost=boost)

    @property
    def passives(self):
        suitName = self.dna.name
        attributes = SuitBattleGlobals.SuitAttributes[suitName]
        if attributes.get('passives'):
            return attributes['passives']

    def getPassive(self, passive, default=None):
        passives = self.passives
        if not passives:
            return default

        return passives.get(passive, default)

    def addAggro(self, toonId: int, damage: int) -> None:
        self.aggroMap.setdefault(toonId, 0)
        self.aggroMap[toonId] += max(damage, 1)

    def getReviveDamageMultiplier(self):
        revAttr = SuitBattleGlobals.REVIVE_ATTRIBUTES
        return revAttr.get(self.dna.name, revAttr['standard'])[1]

    def getAttackDamage(self, attackType: AttackEnum) -> int:
        definition = SuitBattleGlobals.SuitAttributes[self.dna.name]
        attackInfo = definition["attacks"][attackType]
        dmgIndex = self.getLevel() - (definition['level'] + 1)
        overlevel = self.getLevel() - (definition['maxLevel'] + 1)
        damage = attackInfo[0][min(dmgIndex, len(attackInfo[0]) - 1)]

        # If the level is somehow over the expected cap, let's
        # add the overlevel damage to their damage.
        return damage + (0 if overlevel < 0 else overlevel * definition["overlevelDamageFactor"])

    def getAttackAccuracy(self, attackType: AttackEnum) -> int:
        definition = SuitBattleGlobals.SuitAttributes[self.dna.name]
        attackInfo = definition["attacks"][attackType]
        suitLevel = self.getLevel()
        return attackInfo[1][min(suitLevel, len(attackInfo[1]) - 1)]
