from direct.showbase import DirectObject
from panda3d.core import ConfigVariableBool
from toontown.suit import SuitDNA
from toontown.suit import SuitHoodGlobals as SHG
from toontown.battle import SuitBattleGlobals
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from toontown.zone.base.PersistentLevelBattleManagerAI import PersistentLevelBattleManagerAI
from toontown.zone.entities.standalone.DistributedPersistentLevelSuitAI import DistributedPersistentLevelSuitAI
import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from toontown.ai.ToontownAIRepository import ToontownAIRepository


@DirectNotifyCategory()
class PersistentLevelSuitPlannerAI(DirectObject.DirectObject):
    """
    PersistentLevelSuitPlannerAI(DirectObject)
    """

    def __init__(self, air, level, cogCtor, battleCtor):
        """
        :type air: ToontownAIRepository
        """
        self.notify.debug("init")
        self.air = air  # type: ToontownAIRepository
        self.level = level
        self.cogCtor = cogCtor

        self.battleMgr = PersistentLevelBattleManagerAI(self.air, self.level, battleCtor)

        # create a dict that will keep track of what suits are attached
        # to what battle cell
        self.battleCellId2suits = {}
        for battleCell in self.level.getEntitiesOfType('suitBattleCell'):
            self.battleCellId2suits[battleCell.entId] = []

    def destroy(self):
        self.battleMgr.destroyBattleMgr()
        del self.battleMgr

        self.battleCellId2suits = {}

        self.ignoreAll()

        del self.cogCtor
        del self.level
        del self.air

    def _genJoinChances(self, num):
        joinChances = []
        for currChance in range(num):
            joinChances.append(random.randint(1, 100))
        joinChances.sort()
        return joinChances

    def genSuitObject(self, suitDict):
        suit = self.cogCtor(simbase.air, self)
        dna = SuitDNA.SuitDNA()

        if suitDict['type']:
            dna.newSuit(suitDict['type'])
        else:
            dna.newSuitRandom(level=SuitDNA.getRandomSuitType(suitDict['level']), dept=suitDict['track'])

        suit.dna = dna
        suit.setLevel(suitDict['level'])
        suit.setSkeleRevives(suitDict.get('revives'))
        suit.setLevelDoId(self.level.doId)
        if suitDict['skeleton']:
            # 'skelecog' is a required attribute, it will be sent to clients
            # on generate
            suit.setSkelecog(1)

        if suitDict['elite']:
            suit.setElite(1)

        if suitDict['virtual']:
            suit.setVirtual(1)

        return suit

    def requestBattle(self, suit, toonId):
        """
        :return: 0 | 1
        """
        battleCell = suit.getBattleCell()
        if not battleCell:
            # Battle cell told us to die, probably none available
            return 0
        pos = battleCell.pos
        zone = self.level.getZoneId(self.level.getEntityZoneEntId(battleCell.parentEntId))

        maxSuits = 4

        battle, new = self.battleMgr.newBattle(battleCell.entId, zone, pos, suit, toonId,
                                               self.__handleRoundFinished, self.__handleBattleFinished, maxSuits)

        for otherSuit in reversed(self.battleCellId2suits[battleCell.entId]):
            if new:
                battle.addSuit(otherSuit)
            elif not battle.suitRequestJoin(otherSuit):
                # I guess we could also just let the suit carry on...
                # except that it might collide with localToon and
                # trigger another battle. Yech.
                ## This crashes; don't assign >4 suits to a battle cell
                ## for now
                battle = self.battleMgr.getBattle(battleCell.entId)
                if battle:
                    self.notify.warning(
                        'battle not joinable: numSuits=%s, joinable=%s, fsm=%s, toonId=%s' % (
                            len(battle.suits), battle.isJoinable(),
                            battle.getCurrentOrNextState(), toonId)
                    )
                else:
                    self.notify.warning(
                        'battle not joinable: no battle for cell %s, toonId=%s' % (battleCell.entId, toonId))
                return 0
        if new:
            battle.request("FaceOff")
            battle.generateWithRequired(zone)
        return 1

    def __handleRoundFinished(self, cellId, toonIds, totalHp, deadSuits):
        """
        Determine if any reserves need to join

        :type deadSuits: list
        """
        self.notify.debug('cell %s, handleRoundDone() - hp: %d' % (cellId, totalHp))

        # Calculate the total max HP for all the suits currently on the floor
        totalMaxHp = 0
        level = self.level
        battle = self.battleMgr.cellId2battle[cellId]

        for suit in battle.suits:
            totalMaxHp += suit.getMaxHp()

        self.notify.debug('handleRoundDone() - battleSuits: %d' % ( len(battle.suits)))

        if battle:
            battle.resume()

    def __handleBattleFinished(self, zoneId):
        pass

    def __suitCanJoinBattle(self, zoneId: int, suit: DistributedPersistentLevelSuitAI) -> bool:
        """
        Function:    look at a battle in a specific zone and calculate
                     if a suit is able to join the battle based on the
                     various join-chance values specified for this suit
                     planner
        Parameters:  zoneId, the zone in which a battle exists
        Returns:     True if the suit can join, False otherwise
        """
        battle = self.battleMgr.getBattle(zoneId)
        maxSuits = battle.maxSuitsIncludingOverrides
        if len(battle.suits) >= maxSuits:
            return False

        # Can this Suit even join battles?
        if suit.dna.name in SuitBattleGlobals.CANT_JOIN_BATTLES:
            return False

        # First, let's see if the battle has any cogs that would
        # override the chance for a suit to join the battle.
        suitNames = [suit.dna.name for suit in battle.suits]
        checkRatio = -1
        for potentialSuit in SuitBattleGlobals.JOIN_CHANCE_OVERRIDES:
            if potentialSuit in suitNames:
                # Aha, we found a suit with an override.
                # Time to get ratioed.
                checkRatio = max(SuitBattleGlobals.JOIN_CHANCE_OVERRIDES[potentialSuit], checkRatio)
        if checkRatio >= 0:
            return random.randint(0, 99) < checkRatio
        # Check to see if more cogs should join this battle based on
        # the total amount of cogs ever in this battle.
        limit = len(battle.toons) + 1
        if battle.numSuitsEver + 1 > limit:
            return False
        if battle:
            # the chance of a suit joining a battle depends on the suit to
            # toon ratio of the battle, once this chance is obtained, the
            # suit randomly decides if it should join, first check to see
            # if we have a config to tell us that suits always join battles
            # with an empty slot
            if ConfigVariableBool('suits-always-join', False).getValue():
                return True
            jChanceList = SHG.SUIT_JOIN_CHANCE
            ratioIdx = (len(battle.toons) - battle.numSuitsEver) + 2
            if ratioIdx >= 0:
                if ratioIdx < len(jChanceList):
                    if random.randint(0, 99) < jChanceList[ratioIdx]:
                        return True
                else:
                    self.notify.warning('__suitCanJoinBattle idx out of range!')
                    return True
        return False

    def checkForBattle(self, cellId, suit):
        # See if zone has a battle or not
        if self.battleMgr.cellHasBattle(cellId):
            # If zone has a battle, see if there are any spots in it
            # but first, randomly decide if this suit should even try
            # to join the battle based on the hood's join battle
            # randomness
            if suit.isStubborn():
                # The suit is stubborn, so it will try really hard
                # to join the battle. If the battle manager isn't happy,
                # then the suit will simply ignore the battle entirely.
                if suit.dna.name not in SuitBattleGlobals.CANT_JOIN_BATTLES and self.battleMgr.requestBattleAddSuit(cellId, suit):
                    return 1
                return 0
            if self.__suitCanJoinBattle(cellId, suit) and self.battleMgr.requestBattleAddSuit(cellId, suit):
                # The suit gets added to the battle and the battle
                # takes control
                return 1
            # Make the suit fly away
            suit.b_beginFlyAway()
            return 1
        else:
            # There is no battle, so continue
            return 0

    def getDoId(self):
        """
        This is a dummy function so we don't need to modify DistributedSuit
        """
        return 0

    def removeSuit(self, suit):
        """
        delete the suit
        """
        suit.requestDelete()
