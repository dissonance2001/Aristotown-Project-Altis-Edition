import random, sys
from math import floor
from toontown.battle.BattleBase import *
from toontown.battle.BattleGlobals import *
from toontown.battle.DistributedBattleAI import *
from toontown.toonbase import ToontownBattleGlobals
from math import floor
from direct.directnotify import DirectNotifyGlobal
from direct.interval.IntervalGlobal import *
from toontown.toonbase.ToontownBattleGlobals import *
from toontown.toonbase import ToontownGlobals
from toontown.suit import DistributedSuitBaseAI
from toontown.battle import SuitBattleGlobals
from toontown.battle import BattleExperienceAI
from toontown.toon import NPCToons
from toontown.pets import PetTricks, DistributedPetProxyAI
from toontown.hood import ZoneUtil
from toontown.toonbase.ToonPythonUtil import lerp
from toontown.battle.calculators.LawbotLitigationCalculatorAI import LawbotLitigationCalculatorAI
from toontown.battle.calculators.BoardbotLitigationCalculatorAI import BoardbotLitigationCalculatorAI
from toontown.battle.calculators.BossbotLitigationCalculatorAI import BossbotLitigationCalculatorAI
from toontown.battle.calculators.CashbotLitigationCalculatorAI import CashbotLitigationCalculatorAI
from toontown.battle.calculators.CountsCalculatorAI import CountsCalculatorAI
from toontown.battle.calculators.DirectorsCalculatorAI import DirectorsCalculatorAI
from toontown.battle.calculators.FaceTheFamilyCalculatorAI import FaceTheFamilyCalculatorAI
from toontown.battle.calculators.HighRollerCalculatorAI import HighRollerCalculatorAI
from toontown.battle.calculators.PacesetterCalculatorAI import PacesetterCalculatorAI
from toontown.battle.calculators.ChainsawCalculatorAI import ChainsawCalculatorAI
from toontown.battle.calculators.SellbotLitigationCalculatorAI import SellbotLitigationCalculatorAI
from toontown.battle.calculators.SuitConditionCalculatorAI import SuitConditionCalculatorAI
from toontown.battle.calculators.SuitSpawnCalculatorAI import SuitSpawnCalculatorAI
from toontown.battle.calculators.WitnessStandInCalculatorAI import WitnessStandInCalculatorAI
from toontown.battle.calculators.SuitAttackTracksCalculatorAI import SuitAttackTracksCalculatorAI
from toontown.battle.calculators.BaseSuitAttackCalculatorAI import BaseSuitAttackCalculatorAI
from toontown.battle.calculators.AttackHPCalculatorAI import AttackHPCalculatorAI
import StatusEffects

SUIT_ATTACK_UNTARGETABLE_CONDITIONS = {
    'default': ['hidden'],
    'SoakRemoval': [],
    'LureRemoval': [],
    'AbsorbMovieLure': [],
    'AbsorbMovieThrow': [],
    'AbsorbMovieSquirt': [],
    'AbsorbMovieZap': [],
    'AbsorbMovieSound': [],
    'AbsorbMovieDrop': [],
    'AbsorbMovieLevelLure': [],
    'AbsorbMovieLevelThrow': [],
    'AbsorbMovieLevelSquirt': [],
    'AbsorbMovieLevelZap': [],
    'AbsorbMovieLevelSound': [],
    'AbsorbMovieLevelDrop': [],
    'ScapegoatEnraged': [],
    'ScapegoatShieldsUp': [],
    'ScapegoatRageBuilding': [],
    'ComboThrow': [],
    'ComboSquirt': [],
    'ComboDrop': [],
    'AttorneyChrono': [],
    'SyphonMovie': [],
    'DamageMovie': [],
    'LureRemovalPreToon': [],
    'LureRemoval': [],
    'Desperation': [],
    'Desperation2': [],
    'LureRemovalHeal': [],
    'CalculatingFees': [],
    'OilRemoval': [],
    'MarkRemoval': [],
    'LureRemovalTrap': [],
    'LureRemovalLure': [],
    'LureRemovalSound': [],
    'LureRemovalThrow': [],
    'LureRemovalSquirt': [],
    'LureRemovalZap': [],
    'LureRemovalDrop': [],
    'AbilityQueued': [],
    'ErfitHydrationCheckRevert': [],
    'ErfitHydrationCheck': [],
    'ScapegoatGavel': [],
    'PowerhouseGroundbreakerRevert': [],
    'AbilityQueuedPreToon': [],
}
SUIT_ATTACK_RECENT_TARGET_CONDITIONS = {
    'UnionBusterUnionBuster': 'unionBusterRecentlyTargeted',
    'RadiographerHotTake': 'hotTakeRecentlyTargeted',
    'BookkeeperPaperCut': 'paperCutRecentlyTargeted',
    'ContingencyRiskThresholdBreach50': 'riskBreachRecentlyTargeted',
    'WiretapperCollectCall': 'collectCallRecentlyTargeted',
    'CaseManagerLegalBindings': 'legalBindingsRecentlyTargeted',
    'DividendLiquidationEvent': 'liquidationRecentlyTargeted',
}

CONTENT_SYNC_ORDERS = {
    1: [DROP, SQUIRT, ZAP, TRAP, THROW, LURE, SOUND, HEAL],
    2: [SOUND, DROP, SQUIRT, HEAL, ZAP, TRAP, LURE, THROW],
    3: [SQUIRT, SOUND, HEAL, TRAP, THROW, ZAP, LURE, DROP],
    4: [SQUIRT, TRAP, LURE, DROP, HEAL, ZAP, SOUND, THROW],
    5: [THROW, SOUND, DROP, TRAP, SQUIRT, HEAL, LURE, ZAP],
    6: [THROW, SQUIRT, ZAP, SOUND, TRAP, LURE, DROP, HEAL],
    7: [TRAP, DROP, SQUIRT, SOUND, THROW, ZAP, LURE, HEAL],
    8: [TRAP, SQUIRT, DROP, THROW, ZAP, LURE, HEAL, SOUND],
}

CONTENT_SYNC_CONDITION_ORDERS = {
    'contentSync1': [DROP, SQUIRT, ZAP, TRAP, THROW, LURE, SOUND, HEAL],
    'contentSync2': [SOUND, DROP, SQUIRT, HEAL, ZAP, TRAP, LURE, THROW],
    'contentSync3': [SQUIRT, SOUND, HEAL, TRAP, THROW, ZAP, LURE, DROP],
    'contentSync4': [SQUIRT, TRAP, LURE, DROP, HEAL, ZAP, SOUND, THROW],
    'contentSync5': [THROW, SOUND, DROP, TRAP, SQUIRT, HEAL, LURE, ZAP],
    'contentSync6': [THROW, SQUIRT, ZAP, SOUND, TRAP, LURE, DROP, HEAL],
    'contentSync7': [TRAP, DROP, SQUIRT, SOUND, THROW, ZAP, LURE, HEAL],
    'contentSync8': [TRAP, SQUIRT, DROP, THROW, ZAP, LURE, HEAL, SOUND],
}

class BattleCalculatorAI:
    CONTENT_SYNC_ORDERS = CONTENT_SYNC_ORDERS
    CONTENT_SYNC_CONDITION_ORDERS = CONTENT_SYNC_CONDITION_ORDERS
    notify = DirectNotifyGlobal.directNotify.newCategory('BattleCalculatorAI')
    notify.setDebug(False)
    AccuracyBonuses = [0, 20, 40, 60]
    DamageBonuses = [0, 20, 20, 20]
    DamageBonusesDrop = [0, 30, 30, 30]
    AttackExpPerTrack = [0, 10, 20, 30, 40, 50, 60, 70]
    TRAP_CONFLICT = -2
    NumRoundsLured = ToontownBattleGlobals.AvLureRounds
    NumRoundsSoaked = ToontownBattleGlobals.AvSoakRounds
    NumRoundsMarked = ToontownBattleGlobals.AvMarkRounds
    NumRoundsDazed = ToontownBattleGlobals.AvDazeRounds
    APPLY_HEALTH_ADJUSTMENTS = 1
    TOONS_TAKE_NO_DAMAGE = 0
    CAP_HEALS = 1
    CLEAR_SUIT_ATTACKERS = 1
    SUITS_UNLURED_IMMEDIATELY = 1
    CLEAR_MULTIPLE_TRAPS = 0
    KBBONUS_LURED_FLAG = 0
    KBBONUS_TGT_LURED = 1
    notify = DirectNotifyGlobal.directNotify.newCategory('BattleCalculatorAI')
    toonsAlwaysHit = simbase.config.GetBool('toons-always-hit', False)
    toonsAlwaysMiss = simbase.config.GetBool('toons-always-miss', False)
    toonsAlways5050 = simbase.config.GetBool('toons-always-5050', False)
    suitsAlwaysHit = simbase.config.GetBool('suits-always-hit', False)
    suitsAlwaysMiss = simbase.config.GetBool('suits-always-miss', False)
    immortalSuits = simbase.config.GetBool('immortal-suits', False)
    propAndOrganicBonusStack = simbase.config.GetBool('prop-and-organic-bonus-stack', False)

    def __init__(self, battle, tutorialFlag = 0):
        self.battle = battle
        self.lawbotCalculator = LawbotLitigationCalculatorAI(self)
        self.boardbotCalculator = BoardbotLitigationCalculatorAI(self)
        self.bossbotCalculator = BossbotLitigationCalculatorAI(self)
        self.cashbotCalculator = CashbotLitigationCalculatorAI(self)
        self.sellbotCalculator = SellbotLitigationCalculatorAI(self)
        self.countsCalculator = CountsCalculatorAI(self)
        self.witnessStandInCalculator = WitnessStandInCalculatorAI(self)
        self.pacesetterCalculator = PacesetterCalculatorAI(self)
        self.chainsawCalculator = ChainsawCalculatorAI(self)
        self.highRollerCalculator = HighRollerCalculatorAI(self)
        self.suitConditionCalculator = SuitConditionCalculatorAI(self)
        self.suitSpawnCalculator = SuitSpawnCalculatorAI(self)
        self.faceTheFamilyCalculator = FaceTheFamilyCalculatorAI(self)
        self.directorsCalculator = DirectorsCalculatorAI(self)
        self.tracksCalculator = SuitAttackTracksCalculatorAI(self)
        self.baseSuitAttacksCalculator = BaseSuitAttackCalculatorAI(self)
        self.suitAttackHpCalculator = AttackHPCalculatorAI(self)
        self.SuitAttackers = {}
        self.currentlyLuredSuits = {}
        self.currentlyWetSuits = {}
        self.currentlySoakedSuits = {}
        self.currentlyImmuneSuits = {}
        self.currentlyEnragedSuits = {}
        self.currentlyAbsorbingSuits = {}
        self.successfulLures = {}
        self.toonAtkOrder = []
        self.unionSacrifices = 0
        self.toonHPAdjusts = {}
        self.toonSkillPtsGained = {}
        self.syphonedHP = 0
        self.countErclaimHP = 0
        self.countErfitHP = 0
        self.absorbDamage = 0
        self.hurrySicknessDamage = 25
        self.absorbDamageByTrack = {
            LURE: 0,
            THROW: 0,
            SQUIRT: 0,
            ZAP: 0,
            SOUND: 0,
            DROP: 0
        }

        self.levelDamageByTrack = {
            LURE: 0,
            THROW: 0,
            SQUIRT: 0,
            ZAP: 0,
            SOUND: 0,
            DROP: 0
        }
        self.absorbDamageRecordkeeper = 0
        self.syphonHP = {}
        self.damageHP = {}
        self.snipeHP = 0
        self.fraudulentDamage = 0
        self.levelDamage = 0
        self.traps = {}
        self.instakillTraps = {}
        self.npcTraps = {}
        self.suitAtkStats = {}
        self.unusedConditions = [1, 2, 3, 4, 5, 6, 7, 8]
        self.unusedPhases = [2, 3, 4, 5, 6, 7, 8]
        self.highRollerAttacks = [1, 2, 3, 4]
        self.litigationSpawns = [1, 2, 3, 4]
        self.silhouetteSpawns = ['sil1', 'sil2', 'sil3', 'sil4', 'sil5', 'sil6', 'sil7', 'sil8', 'sil9', 'sil10', 'sil11', 'sil12']
        self.silhouetteDeath = 0
        self.racketeerMultiplier = 0
        self.hustlerHits = 0
        self.usedConditions = []
        self.deadSuits = 0
        self.levels = 0
        self.targets = 0
        self.roundsToonsHit = 0
        self.unionDues = 20
        self.roundsCogsMiss = 0
        self.__clearBonuses(hp=1)
        self.__clearBonuses(hp=0)
        self.delayedUnlures = []
        self.__skillCreditMultiplier = simbase.air.baseXpMultiplier
        self.tutorialFlag = tutorialFlag
        self.trainTrapTriggered = False
        self.fireDifficulty = 0
        self.sacrificedCogs = 0
        self.governaughtCogs = 0
        self.TurnsElapsed = 0
        self.TurnsSinceSummonWithOnlyOneCog = 0
        self.TurnsSinceSummon = 0
        self.numShadowsSummoned = 0
        self.recordkeeperMultiplier = 28
        self.recordkeeperCalculatorMultiplier = 28
        self.costsMultiplier = 20
        self.interestMultiplier = 24
        self.costsCalculatorMultiplier = 20
        self.collectCallMultiplier = 20
        self.collectCallCalculatorMultiplier = 20
        self.directorMultiplier = 24
        self.interestMultiplier = 24
        self.objectionDamage = 0
        self.comboDamage = 0
        self.knockbackDamage = 0
        self.contingencyThresholds = 0

        # a dictionary of each toon's status conditions
        #
        # each status is formatted this way
        # 'condition': {modifier, turnsRemaining}
        #
        # the dictionary holds all four toons, so a possible dictionary could be
        # { 10000000: { 'corruption': {'modifier': 2, 'turnsRemaining': -1} } }
        self.toonStatusConditions = {}
        self.toonStatusConditionsNew = {}

        self.suitStatusConditions = {}
        self.suitStatusConditionsNew = {}

    def printSuitConditions(self):
        self.notify.debug('printSuitConditions() *********************************************')
        self.notify.debug('printSuitConditions(): Beginning Turn Readout')
        self.notify.debug('printSuitConditions() *********************************************')
        for suit in self.suitStatusConditions:
            self.notify.debug('printSuitConditions(): Suit %i has the following Conditions:' % suit)
            for condition in self.suitStatusConditions[suit]:
                self.notify.debug('printSuitConditions(): %s x %i, with %i turn%s remaining' % (
                    condition, self.suitStatusConditions[suit][condition]['modifier'],
                    self.suitStatusConditions[suit][condition]['turnsRemaining'] - 1,
                    '' if self.suitStatusConditions[suit][condition]['turnsRemaining'] - 1 == 1 else 's'))
        self.notify.debug('printSuitConditions() *********************************************')
        self.notify.debug('printSuitConditions(): Ending Turn Readout')
        self.notify.debug('printSuitConditions() *********************************************')

    def toonHasCondition(self, toonId, condition):
        #self.notify.debug('toonHasCondition() - checking for \'%s\' on toonId %i' % (condition, toonId))
        if toonId not in self.toonStatusConditions:
            return False

        return condition in self.toonStatusConditions[toonId]

    def getToonConditionModifier(self, toonId, condition):
        if not self.toonHasCondition(toonId, condition):
            #self.notify.warning('getToonConditionModifier() - method called, but toon %i did not have %s condition' % (
            #toonId, condition))
            return 0
        return self.toonStatusConditions[toonId][condition]['modifier']

    def getToonConditionTurns(self, toonId, condition):
        if not self.toonHasCondition(toonId, condition):
            #self.notify.warning(
                #'getToonConditionTurns() - method called, but toon %i did not have %s condition' % (toonId, condition))
            return 0
        return self.toonStatusConditions[toonId][condition]['turnsRemaining']

    def setToonCondition(self, toonId, condition, modifier, turns=-1, mode='none'):
        # first, check if the toon is even in the dictionary
        if toonId not in self.toonStatusConditions:
            # if not, make them an entry
            self.toonStatusConditions[toonId] = {}

        # if condition not in ToontownBattleGlobals.ValidStatusConditions:
        #     self.notify.warning(
        #         'setToonCondition() - ERROR! Condition %s is not a valid condition! Not setting.' % condition)
        #     return

        # special handling to remove a condition
        if modifier == 0 or turns == 0 and mode == 'none':
            if condition in self.toonStatusConditions[toonId]:
                del self.toonStatusConditions[toonId][condition]
            return

        # next, check if the toon has the condition already
        if condition not in self.toonStatusConditions[toonId]:
            # if not, add the condition, and we're done
            self.toonStatusConditions[toonId][condition] = {'modifier': modifier, 'turnsRemaining': turns}
            return
        else:
            # otherwise, increase the existing modifier appropriately
            newModifier = 0  # the variable we will set the modifier to
            newTurns = 0  # the variable we will set the turns to

            # modifier APPENDED, turns SET, used to change a buff/debuff's timer, but keep its potency
            if mode is 'refreshTurns':
                newModifier = self.getToonConditionModifier(toonId, condition) + modifier
                newTurns = turns

            # modifer SET, turns APPENDED, used to modify a buff/debuff's potency, but change its duration
            if mode is 'refreshModifier':
                newModifier = modifier
                newTurns = self.getToonConditionTurns(toonId, condition) + turns

            # modifier APPENDED, turns APPENDED, used to change a buff/debuff's potency AND duration
            if mode is 'refreshBoth':
                newModifier = self.getToonConditionModifier(toonId, condition) + modifier
                newTurns = self.getToonConditionTurns(toonId, condition) + turns

            # modifier SET, turns SET, used to explicitly set a modifier to a precise potency and duration
            if mode is 'setBoth':
                newModifier = modifier
                newTurns = turns

            if mode is 'alternateBoth':
                if modifier > self.toonStatusConditions[toonId][condition]['modifier']:
                    newModifier = modifier
                else:
                    newModifier = self.toonStatusConditions[toonId][condition]['modifier']
                newTurns = turns

            if mode is 'refreshTurnNoUndercut':
                newModifier = modifier
                if turns > self.toonStatusConditions[toonId][condition]['turnsRemaining']:
                    newTurns = turns
                else:
                    newTurns = self.toonStatusConditions[toonId][condition]['turnsRemaining']

            self.notify.debug(
                'setToonCondition() - gave toon %i condition %s with modifier %i with %i turns remaining' % (
                toonId, condition, newModifier, newTurns))
            self.toonStatusConditions[toonId][condition] = {'modifier': newModifier, 'turnsRemaining': newTurns}

    def suitHasCondition(self, suitId, condition):
        #self.notify.debug('suitHasCondition() - checking for \'%s\' on suitId %i' % (condition, suitId))
        if suitId not in self.suitStatusConditions:
            return False

        return condition in self.suitStatusConditions[suitId]

    def getSuitConditionModifier(self, suitId, condition):
        if not self.suitHasCondition(suitId, condition):
            self.notify.warning('getSuitConditionModifier() - method called, but suit %i did not have %s condition' % (
            suitId, condition))
            return 0
        return self.suitStatusConditions[suitId][condition]['modifier']

    def getSuitConditionTurns(self, suitId, condition):
        if not self.suitHasCondition(suitId, condition):
            return 0
        return self.suitStatusConditions[suitId][condition]['turnsRemaining']

    def setSuitCondition(self, suitId, condition, modifier, turns=-1, mode='none'):
        # first, check if the suit is even in the dictionary
        if suitId not in self.suitStatusConditions:
            # if not, make them an entry
            self.suitStatusConditions[suitId] = {}

        # if condition not in ToontownBattleGlobals.ValidStatusConditions:
        #     self.notify.warning(
        #         'setSuitCondition() - ERROR! Condition %s is not a valid condition! Not setting.' % condition)
        #     return

        # special handling to remove a condition
        if turns == 0 or mode == 'none':
            if condition in self.suitStatusConditions[suitId]:
                del self.suitStatusConditions[suitId][condition]
            return

        if condition == 'drenched':
            if 'soaked' in self.suitStatusConditions[suitId]:
                del self.suitStatusConditions[suitId]['soaked']

        if condition == 'soaked' and self.suitHasCondition(suitId, 'drenched'):
            self.suitStatusConditions[suitId]['drenched'] = {'modifier': modifier, 'turnsRemaining': turns}
            if 'soaked' in self.suitStatusConditions[suitId]:
                del self.suitStatusConditions[suitId]['soaked']

        # next, check if the suit has the condition already
        if condition not in self.suitStatusConditions[suitId]:
            # if not, add the condition, and we're done
            self.suitStatusConditions[suitId][condition] = {'modifier': modifier, 'turnsRemaining': turns}
            return
        else:
            # otherwise, increase the existing modifier appropriately
            newModifier = 0  # the variable we will set the modifier to
            newTurns = 0  # the variable we will set the turns to

            # modifier APPENDED, turns SET, used to change a buff/debuff's timer, but keep its potency
            if mode is 'refreshTurns':
                newModifier = self.getSuitConditionModifier(suitId, condition) + modifier
                newTurns = turns

            # modifer SET, turns APPENDED, used to modify a buff/debuff's potency, but change its duration
            if mode is 'refreshModifier':
                newModifier = modifier
                newTurns = self.getSuitConditionTurns(suitId, condition) + turns

            # modifier APPENDED, turns APPENDED, used to change a buff/debuff's potency AND duration
            if mode is 'refreshBoth':
                newModifier = self.getSuitConditionModifier(suitId, condition) + modifier
                newTurns = self.getSuitConditionTurns(suitId, condition) + turns

            # modifier SET, turns SET, used to explicitly set a modifier to a precise potency and duration
            if mode is 'setBoth':
                newModifier = modifier
                newTurns = turns

            if mode is 'alternateBoth':
                if modifier > self.suitStatusConditions[suitId][condition]['modifier']:
                    newModifier = modifier
                else:
                    newModifier = self.suitStatusConditions[suitId][condition]['modifier']
                newTurns = turns

            if mode is 'refreshTurnNoUndercut':
                newModifier = modifier
                if turns > self.suitStatusConditions[suitId][condition]['turnsRemaining']:
                    newTurns = turns
                else:
                    newTurns = self.suitStatusConditions[suitId][condition]['turnsRemaining']

            self.notify.debug(
                'setSuitCondition() - gave suit %i condition %s with modifier %i with %i turns remaining' % (
                suitId, condition, newModifier, newTurns))
            self.suitStatusConditions[suitId][condition] = {'modifier': newModifier, 'turnsRemaining': newTurns}

    def decrementConditionTurns(self):
        for toon in self.toonStatusConditions.keys():
            for condition in self.toonStatusConditions[toon].keys():
                if self.toonStatusConditions[toon][condition]['turnsRemaining'] > 0:
                    self.notify.debug(
                        'decrementConditionTurns() - Decremented %s condition on toon %i (new turns: %i)' % (
                        condition, toon, self.toonStatusConditions[toon][condition]['turnsRemaining'] - 1))
                    self.toonStatusConditions[toon][condition]['turnsRemaining'] -= 1

                if self.toonStatusConditions[toon][condition]['turnsRemaining'] == -1:
                    continue

                if self.toonStatusConditions[toon][condition]['turnsRemaining'] == 0:
                    self.notify.debug(
                        'decrementConditionTurns() - %s condition on toon %i have reached 0, removing.' % (
                        condition, toon))
                    del self.toonStatusConditions[toon][condition]

        for suit in self.suitStatusConditions.keys():
            for condition in self.suitStatusConditions[suit].keys():
                if self.suitStatusConditions[suit][condition]['turnsRemaining'] > 0:
                    self.notify.debug(
                        'decrementConditionTurns() - Decremented %s condition on suit %i (new turns: %i new modifier: %i)' % (
                        condition, suit, self.suitStatusConditions[suit][condition]['turnsRemaining'] - 1, self.suitStatusConditions[suit][condition]['modifier']))
                    self.suitStatusConditions[suit][condition]['turnsRemaining'] -= 1

                if self.suitStatusConditions[suit][condition]['turnsRemaining'] == -1:
                    continue

                if self.suitStatusConditions[suit][condition]['turnsRemaining'] == 0:
                    self.notify.debug(
                        'decrementConditionTurns() - %s condition on suit %i have reached 0, removing.' % (
                        condition, suit))
                    del self.suitStatusConditions[suit][condition]
            if not self.suitStatusConditions[suit].keys():
                del self.suitStatusConditions[suit]
        
        # Similar to the system above, check all Toons and Cogs for their status effects.
        for toonId in self.toonStatusConditionsNew.keys():
            for i in range(len(self.toonStatusConditionsNew[toonId])): # Do it like this so that we can go back later and check the effect in the list.
                self.toonStatusConditionsNew[toonId][i].subtractRound() # The included method that will allow for a round to be subtracted, along with any additional modifications to the status effect as needed (e.g. Rising Star damage boost).
                if self.toonStatusConditionsNew[toonId][i].roundsLeft == 0: # Are we out of rounds, and is it not a constantly-remaining status effect (-1 rounds left)?
                    self.toonStatusConditionsNew[toonId][i] = None # Turn the status effect into nothing.
        
            # Now, find all conditions that were turned into None and remove them from the list.
            # TODO: Find a better way to handle removing status effects.
            while None in self.toonStatusConditionsNew[toonId]:
                self.toonStatusConditionsNew[toonId].remove(None)
        
        # Repeat the process, but for Cogs.
        for suitId in self.suitStatusConditionsNew.keys():
            for i in range(len(self.suitStatusConditionsNew[suitId])):
                self.suitStatusConditionsNew[suitId][i].subtractRound()
                if self.suitStatusConditionsNew[suitId][i].roundsLeft == 0:
                    self.suitStatusConditionsNew[suitId][i] = None
            
            while None in self.suitStatusConditionsNew[suitId]:
                self.suitStatusConditionsNew[suitId].remove(None)
    
    def getAllRelevantConditions(self, avId, conditionType, toon = True):
        '''
        Return a list of all status effects that match and inherit the condition type.

        Parameters:
            avId: The ID of who is being checked.
            conditionType (type): The type of the effect that is being searched, as well as any effects that inherit it (e.g. Snapped will be included if checking for DefenseModifier, but not vice versa)
            toon (bool): Whether or not the avatar is a Toon, which determines which dict we check from.
        '''
        conditions = []

        source = self.toonStatusConditionsNew if toon else self.suitStatusConditionsNew

        if avId not in source:
            return conditions

        for condition in source[avId]:
            if isinstance(condition, conditionType):
                conditions.append(condition)

        return conditions

    def printToonConditions(self):
        self.notify.debug('printToonConditions() *********************************************')
        self.notify.debug('printToonConditions(): Beginning Turn Readout')
        self.notify.debug('printToonConditions() *********************************************')
        for toon in self.toonStatusConditions:
            self.notify.debug('printToonConditions(): Toon %i has the following Conditions:' % toon)
            for condition in self.toonStatusConditions[toon]:
                self.notify.debug('printToonConditions(): %s x %i, with %i turn%s remaining' % (
                condition, self.toonStatusConditions[toon][condition]['modifier'],
                self.toonStatusConditions[toon][condition]['turnsRemaining'] - 1,
                '' if self.toonStatusConditions[toon][condition]['turnsRemaining'] - 1 == 1 else 's'))
        self.notify.debug('printToonConditions() *********************************************')
        self.notify.debug('printToonConditions(): Ending Turn Readout')
        self.notify.debug('printToonConditions() *********************************************')

    def printSuitConditions(self):
        self.notify.debug('printSuitConditions() *********************************************')
        self.notify.debug('printSuitConditions(): Beginning Turn Readout')
        self.notify.debug('printSuitConditions() *********************************************')
        for suit in self.suitStatusConditions:
            self.notify.debug('printSuitConditions(): Suit %i has the following Conditions:' % suit)
            for condition in self.suitStatusConditions[suit]:
                self.notify.debug('printSuitConditions(): %s x %i, with %i turn%s remaining' % (
                condition, self.suitStatusConditions[suit][condition]['modifier'],
                self.suitStatusConditions[suit][condition]['turnsRemaining'] - 1,
                '' if self.suitStatusConditions[suit][condition]['turnsRemaining'] - 1 == 1 else 's'))
        self.notify.debug('printSuitConditions() *********************************************')
        self.notify.debug('printSuitConditions(): Ending Turn Readout')
        self.notify.debug('printSuitConditions() *********************************************')

    def setSkillCreditMultiplier(self, mult):
        self.__skillCreditMultiplier = simbase.air.baseXpMultiplier * mult

    def getSkillCreditMultiplier(self):
        return self.__skillCreditMultiplier

    def cleanup(self):
        self.battle = None

    def __calcToonAtkHit(self, attackIndex, atkTargets):
        if len(atkTargets) == 0:
            return (0, 0)
        if self.tutorialFlag:
            return (1, 95)
        if self.toonsAlways5050:
            roll = random.randint(0, 70)
            if roll > 40:
                return (1, 95)
            else:
                return (0, 0)
        if self.toonsAlwaysHit:
            return (1, 95)
        elif self.toonsAlwaysMiss:
            return (0, 0)
        debug = self.notify.getDebug()
        attack = self.battle.toonAttacks[attackIndex]
        atkTrack, atkLevel = self.__getActualTrackLevel(attack)

        hasAccuracyBuff = False
        toon = simbase.air.doId2do.get(attack[TOON_ID_COL])
        if toon:
            if toon.hasBuff(BGagAccuracy):
                if not ZoneUtil.isDynamicZone(toon.zoneId):
                    if ZoneUtil.getWhereName(toon.zoneId, True) in ('street', 'factoryExterior', 'cogHQExterior'):
                        hasAccuracyBuff = True

        if atkTrack == NPCSOS:
            return (1, 95)
        if atkTrack == FIRE:
            return (1, 95)
        if atkTrack == SUE:
            return (1, 95)
        if atkTrack == HEAL:
            return (1, 95)
        if atkTrack == TRAP:
            if debug:
                self.notify.debug('Attack is a trap, so it hits regardless')
            attack[TOON_ACCBONUS_COL] = 0
            return (1, 100)
        # elif atkTrack == DROP and attack[TOON_TRACK_COL] == NPCSOS:
        #     unluredSuits = 0
        #     for tgt in atkTargets:
        #         if not self.suitHasCondition(tgt.getDoId(), 'unlureSuit'):
        #             unluredSuits = 1

        #     if unluredSuits == 0:
        #         attack[TOON_ACCBONUS_COL] = 1
        #         return (0, 0)
        # elif atkTrack == DROP:
        #     allLured = True
        #     for i in xrange(len(atkTargets)):
        #         if not self.suitHasCondition(atkTargets[i].getDoId(), 'unlureSuit'):
        #             pass
        #         else:
        #             allLured = False

        #     if allLured:
        #         attack[TOON_ACCBONUS_COL] = 1
        #         return (0, 0)
        elif atkTrack == PETSOS:
            return self.__calculatePetTrickSuccess(attack)
        tgtDef = 0
        numLured = 0
        if atkTrack != HEAL:
            for currTarget in atkTargets:
                thisSuitDef = self.__targetDefense(currTarget, atkTrack)
                if self.suitHasCondition(currTarget.doId, 'soaked'):
                    thisSuitDef -= 10
                if self.suitHasCondition(currTarget.doId, 'dazed'):
                    thisSuitDef -= 10
                if self.suitHasCondition(currTarget.doId, 'drenched'):
                    thisSuitDef -= 20
                rushJobConditions = [
                    'trapRushJob',
                    'lureRushJob',
                    'throwRushJob',
                    'squirtRushJob',
                    'zapRushJob',
                    'soundRushJob',
                    'dropRushJob',
                ]
                if any(self.suitHasCondition(currTarget.doId, cond)
                    for cond in rushJobConditions):
                    thisSuitDef *= 0
                if debug:
                    self.notify.debug('Examining suit def for toon attack: ' + str(thisSuitDef))
                tgtDef = min(thisSuitDef, tgtDef)
                if self.__suitIsLured(currTarget.getDoId()):
                    numLured += 1

        trackExp = self.__toonTrackExp(attack[TOON_ID_COL], atkTrack)
        for currOtherAtk in self.toonAtkOrder:
            if currOtherAtk != attack[TOON_ID_COL]:
                nextAttack = self.battle.toonAttacks[currOtherAtk]
                nextAtkTrack = self.__getActualTrack(nextAttack)
                if atkTrack == nextAtkTrack and attack[TOON_TGT_COL] == nextAttack[TOON_TGT_COL]:
                    currTrackExp = self.__toonTrackExp(nextAttack[TOON_ID_COL], atkTrack)
                    if debug:
                        self.notify.debug('Examining toon track exp bonus: ' + str(currTrackExp))
                    trackExp = max(currTrackExp, trackExp)

        if debug:
            if atkTrack == HEAL:
                self.notify.debug('Toon attack is a heal, no target def used')
            else:
                self.notify.debug('Suit defense used for toon attack: ' + str(tgtDef))
            self.notify.debug('Toon track exp bonus used for toon attack: ' + str(trackExp))
        if attack[TOON_TRACK_COL] == NPCSOS:
            randChoice = 0
        elif attack[TOON_TRACK_COL] == ZAP:
            randChoice = 0
        elif attack[TOON_TRACK_COL] == DROP:
            randChoice = 0
        else:
            randChoice = random.randint(0, 99)
        propAcc = AvPropAccuracy[atkTrack][atkLevel]
        if hasAccuracyBuff:
            propAcc *= BGagAccuracyMultiplier
        if atkTrack == DROP:
            treebonus = self.__toonCheckGagBonus(attack[TOON_ID_COL], atkTrack, atkLevel)
            propBonus = self.__checkPropBonus(atkTrack)
            if self.propAndOrganicBonusStack:
                propAcc = 0
                if treebonus:
                    self.notify.debug('using organic bonus lure accuracy')
                    propAcc = AvDropBonusAccuracy[atkLevel]
                if propBonus:
                    self.notify.debug('using prop bonus lure accuracy')
                    propAcc = AvDropBonusAccuracy[atkLevel]
            elif treebonus or propBonus:
                self.notify.debug('using oragnic OR prop bonus lure accuracy')
                propAcc = AvDropBonusAccuracy[atkLevel]
        #if atkTrack == ZAP:
            #for tgt in atkTargets:
                #if self.suitHasCondition(suit.doId, 'soaked'):
                    #propAcc = 100
                    #break
                #else:
                    #continue
        attackAcc = propAcc + trackExp + tgtDef
        currAtk = self.toonAtkOrder.index(attackIndex)
        if currAtk > 0 and atkTrack != HEAL:
            prevAtkId = self.toonAtkOrder[currAtk - 1]
            prevAttack = self.battle.toonAttacks[prevAtkId]
            prevAtkTrack = self.__getActualTrack(prevAttack)
            lure = atkTrack == LURE and (not attackAffectsGroup(atkTrack, atkLevel,
             attack[TOON_TRACK_COL]) and attack[TOON_TGT_COL] in self.successfulLures or attackAffectsGroup(atkTrack, atkLevel, attack[TOON_TRACK_COL]))
            if atkTrack == prevAtkTrack and (attack[TOON_TGT_COL] == prevAttack[TOON_TGT_COL] or lure):
                if prevAttack[TOON_ACCBONUS_COL] == 1:
                    if debug:
                        self.notify.debug('DODGE: Toon attack track dodged')
                elif prevAttack[TOON_ACCBONUS_COL] == 0:
                    if debug:
                        self.notify.debug('HIT: Toon attack track hit')
                attack[TOON_ACCBONUS_COL] = prevAttack[TOON_ACCBONUS_COL]
                return (not attack[TOON_ACCBONUS_COL], attackAcc)
        atkAccResult = attackAcc
        if debug:
            self.notify.debug('setting atkAccResult to %d' % atkAccResult)
        acc = attackAcc + self.__calcToonAccBonus(attackIndex)

        toonId = attack[TOON_ID_COL]

        if self.toonHasCondition(toonId, 'viralSensation'):
            acc -= 20

        if self.toonHasCondition(toonId, 'driedOut'):
            acc -= 50

        if self.toonHasCondition(toonId, 'hydrated'):
            acc += 50
        
        for effect in self.getAllRelevantConditions(toonId, StatusEffects.AccuracyModifier, toon=True): # Sift through all accuracy-modifying effects.
            acc += effect.accuracyMod # Change the accuracy according to the effect's modifier.

        if atkTrack not in (LURE, HEAL, SOUND):
            if atkTrack != DROP:
                if numLured == len(atkTargets):
                    if debug:
                        self.notify.debug('all targets are lured, attack hits')
                    attack[TOON_ACCBONUS_COL] = 0
                    return (1, 100)
                else:
                    luredRatio = float(numLured) / float(len(atkTargets))
                    accAdjust = 100 * luredRatio
                    if accAdjust > 0 and debug:
                        self.notify.debug(str(numLured) + ' out of ' + str(len(atkTargets)) + ' targets are lured, so adding ' + str(accAdjust) + ' to attack accuracy')
                    acc += accAdjust
            elif numLured == len(atkTargets) and atkTrack != DROP:
                if debug:
                    self.notify.debug('all targets are lured, attack misses')
                attack[TOON_ACCBONUS_COL] = 0
                return (0, 0)
        if acc > MaxToonAcc:
            acc = MaxToonAcc

        if self.suitHasCondition(attack[TOON_TGT_COL], 'dodgy'):
            self.notify.debug('Original accuracy target: %i' % acc)
            acc *= abs(self.getSuitConditionModifier(attack[TOON_TGT_COL], 'dodgy') - 100.0) / 100.0    # 100% dodgy is 0x chance to hit, 50% dodgy is 50% from base acc., and -50% dodgy is 150% chance to hit from base, -100% is 2x
            self.notify.debug('Toon attack target has dodgy, modifying accuracy by %fx, new accuracy target is %f' % ((abs(self.getSuitConditionModifier(attack[TOON_TGT_COL], 'dodgy') - 100.0) / 100.0), acc))

        if randChoice < acc:
            if debug:
                self.notify.debug('HIT: Toon attack rolled' + str(randChoice) + 'to hit with an accuracy of' + str(acc))
            attack[TOON_ACCBONUS_COL] = 0
        else:
            if debug:
                self.notify.debug('MISS: Toon attack rolled' + str(randChoice) + 'to hit with an accuracy of' + str(acc))
            attack[TOON_ACCBONUS_COL] = 1
        return (not attack[TOON_ACCBONUS_COL], atkAccResult)

    def __toonTrackExp(self, toonId, track):
        toon = self.battle.getToon(toonId)
        if toon != None:
            toonExpLvl = toon.experience.getExpLevel(track)
            exp = AttackExpPerTrack[toonExpLvl]
            if track == HEAL:
                exp = exp * 0.5
            self.notify.debug('Toon track exp: ' + str(toonExpLvl) + ' and resulting acc bonus: ' + str(exp))
            return exp
        else:
            return 0

    def __toonCheckGagBonus(self, toonId, track, level):
        toon = self.battle.getToon(toonId)
        if toon != None:
            return toon.checkGagBonus(track, level)
        else:
            return False

    def __checkPropBonus(self, track):
        result = False
        if self.battle.getInteractivePropTrackBonus() == track:
            result = True
        return result

    def __targetDefense(self, suit, atkTrack):
        if atkTrack == HEAL:
            return 0
        if suit.getElite():
            boost = 0
        else:
            boost = 0
        suitAttr = SuitBattleGlobals.SuitAttributes.get(suit.dna.name)
        suitDef = SuitBattleGlobals.calculateDefense(suitAttr['level'], suit.getLevel(), boost = boost)
        return -suitDef

    def __createToonTargetList(self, attackIndex):
        attack = self.battle.toonAttacks[attackIndex]
        atkTrack, atkLevel = self.__getActualTrackLevel(attack)
        targetList = []
        if atkTrack == NPCSOS:
            return targetList
        if not attackAffectsGroup(atkTrack, atkLevel, attack[TOON_TRACK_COL]):
            if atkTrack == HEAL:
                target = attack[TOON_TGT_COL]
            else:
                target = self.battle.findSuit(attack[TOON_TGT_COL])
            if target != None:
                targetList.append(target)
        elif atkTrack == HEAL or atkTrack == PETSOS:
            if attack[TOON_TRACK_COL] == NPCSOS or atkTrack == PETSOS:
                targetList = self.battle.activeToons
            else:
                for currToon in self.battle.activeToons:
                    if attack[TOON_ID_COL] != currToon:
                        targetList.append(currToon)

        else:
            targetList = self.battle.activeSuits
        return targetList

    def __prevAtkTrack(self, attackerId, toon = 1):
        if toon:
            prevAtkIdx = self.toonAtkOrder.index(attackerId) - 1
            if prevAtkIdx >= 0:
                prevAttackerId = self.toonAtkOrder[prevAtkIdx]
                attack = self.battle.toonAttacks[prevAttackerId]
                return self.__getActualTrack(attack)
            else:
                return NO_ATTACK

    def __getInstakillDamage(self, toonId):
        toon = self.battle.getToon(toonId)
        if toon is None:
            return 0
        try:
            damage = int(getattr(toon, 'instakillDamage', 0))
        except:
            return 0
        if damage < 1:
            return 0
        return min(damage, 60000)

    def getSuitTrapType(self, suitId):
        if suitId in self.traps:
            if self.traps[suitId][0] == TRAP_CONFLICT:
                return NO_TRAP
            else:
                return self.traps[suitId][0]
        else:
            return NO_TRAP

    def __suitTrapDamage(self, suitId):
        if suitId in self.traps:
            return self.traps[suitId][2]
        else:
            return 0

    def addTrainTrapForJoiningSuit(self, suitId):
        self.notify.debug('addTrainTrapForJoiningSuit suit=%d self.traps=%s' % (suitId, self.traps))
        trapInfoToUse = None
        trapInstakillDamage = 0
        for trapSuitId, trapInfo in self.traps.items():
            if trapInfo[0] == UBER_GAG_LEVEL_INDEX:
                trapInfoToUse = trapInfo
                trapInstakillDamage = self.instakillTraps.get(trapSuitId, 0)
                break

        if trapInfoToUse:
            self.traps[suitId] = trapInfoToUse
            if trapInstakillDamage:
                self.instakillTraps[suitId] = trapInstakillDamage
        else:
            self.notify.warning('huh we did not find a train trap?')

    def __addSuitGroupTrap(self, suitId, trapLvl, attackerId, allSuits, npcDamage = 0):
        if npcDamage == 0:
            if suitId in self.traps:
                self.instakillTraps.pop(suitId, None)
                if self.traps[suitId][0] == TRAP_CONFLICT:
                    pass
                else:
                    self.traps[suitId][0] = TRAP_CONFLICT
                for suit in allSuits:
                    id = suit.doId
                    self.instakillTraps.pop(id, None)
                    if id in self.traps:
                        self.traps[id][0] = TRAP_CONFLICT
                    else:
                        self.traps[id] = [TRAP_CONFLICT, 0, 0]

            else:
                toon = self.battle.getToon(attackerId)
                organicBonus = toon.checkGagBonus(TRAP, trapLvl)
                propBonus = self.__checkPropBonus(TRAP)
                suit = self.battle.findSuit(suitId)
                if self.toonHasCondition(toon.doId, 'nolevel8s') and atkLevel == 7:
                    for suit in self.battle.activeSuits:
                        self.setSuitCondition(suit.doId, 'bannedGagUsed', 1, 1, 'setBoth')
                    self.setToonCondition(toon.doId, 'banned', 1, 1, 'setBoth')
                if self.toonHasCondition(toon.doId, 'nolevel7s') and atkLevel == 6:
                    for suit in self.battle.activeSuits:
                        self.setSuitCondition(suit.doId, 'bannedGagUsed', 1, 1, 'setBoth')
                    self.setToonCondition(toon.doId, 'banned', 1, 1, 'setBoth')
                if self.toonHasCondition(toon.doId, 'nolevel6s') and atkLevel == 5:
                    for suit in self.battle.activeSuits:
                        self.setSuitCondition(suit.doId, 'bannedGagUsed', 1, 1, 'setBoth')
                    self.setToonCondition(toon.doId, 'banned', 1, 1, 'setBoth')
                if self.toonHasCondition(toon.doId, 'nolevel5s') and atkLevel == 4:
                    for suit in self.battle.activeSuits:
                        self.setSuitCondition(suit.doId, 'bannedGagUsed', 1, 1, 'setBoth')
                    self.setToonCondition(toon.doId, 'banned', 1, 1, 'setBoth')
                if self.toonHasCondition(toon.doId, 'nolevel4s') and atkLevel == 3:
                    for suit in self.battle.activeSuits:
                        self.setSuitCondition(suit.doId, 'bannedGagUsed', 1, 1, 'setBoth')
                    self.setToonCondition(toon.doId, 'banned', 1, 1, 'setBoth')
                if self.toonHasCondition(toon.doId, 'noTrapGags'):
                    for suit in self.battle.activeSuits:
                        self.setSuitCondition(suit.doId, 'bannedGagUsed', 1, 1, 'setBoth')
                    self.setToonCondition(toon.doId, 'banned2', 1, 1, 'setBoth')
                if self.toonHasCondition(toon.doId, 'noGags'):
                    for suit in self.battle.activeSuits:
                        self.setSuitCondition(suit.doId, 'bannedGagUsed', 1, 1, 'setBoth')
                    self.setToonCondition(toon.doId, 'banned3', 1, 1, 'setBoth')
                suit = self.battle.findSuit(suitId)
                if suit.dna.name == 'supervis' and suit.getActualLevel() == 20:
                    self.levels += atkLevel
                if suit.dna.name == 'bkeeper' and self.suitHasCondition(suitId, 'bookkeeping'):
                    self.setToonCondition(toon.doId, 'bookkeepingtoon', 1, 1, 'setBoth')
                    self.setSuitCondition(suit.doId, 'bookkeeperHit', 1, 1, 'setBoth')
                if suit.dna.name == 'hustle':
                    self.setToonCondition(toon.doId, 'bookkeepingtoon', 1, 1, 'setBoth')
                    self.setSuitCondition(suit.doId, 'bookkeeperHit', 1, 1, 'setBoth')
                if suit.dna.name == 'ubuster':
                    self.hustlerHits += 1
                if suit.dna.name == 'rkeeper':
                    self.setSuitCondition(suit.doId, 'recordkeeperHit', 1, 1, 'setBoth')
                if suit.dna.name == 'wtapper' and self.toonHasCondition(toon.doId, 'partnered'):
                    self.setSuitCondition(suit.doId, 'wiretapperHit2', 1, 1, 'setBoth')
                    self.setToonCondition(toon.doId, 'collectcalled', 0, 0, 'setBoth')
                if suit.dna.name == 'hustle' and self.toonHasCondition(toon.doId, 'partnered'):
                    self.setSuitCondition(suit.doId, 'wiretapperHit2', 1, 1, 'setBoth')
                if suit.dna.name == 'wtapper':
                    self.setSuitCondition(suit.doId, 'wiretapperHit', 1, 1, 'setBoth')
                if suit.dna.name == 'hustle':
                    self.setSuitCondition(suit.doId, 'wiretapperHit', 1, 1, 'setBoth')
                if suit.dna.name == 'dopr':
                    self.setSuitCondition(suit.doId, 'doprHit', 1, 1, 'setBoth')
                if suit.dna.name == 'supervis' and suit.getActualLevel() == 30:
                    self.setSuitCondition(suit.doId, 'doprHit', 1, 1, 'setBoth')
                if suit.dna.name == 'dopa':
                    self.setSuitCondition(suit.doId, 'dopaHit', 1, 1, 'setBoth')
                if suit.dna.name == 'liquid':
                    self.setSuitCondition(suit.doId, 'tollmasterHit', 1, 1, 'setBoth')
                    self.setToonCondition(toon.doId, 'tollmasterHit', 1, 1, 'setBoth')
                if self.suitHasCondition(suit.doId, 'trapRushJob'):
                    self.setSuitCondition(suit.doId, 'trapRushJob', 0, 0, 'setBoth')
                if suit.dna.name == 'liquid' and self.suitHasCondition(suit.doId, 'stormCellDamage'):
                    self.setSuitCondition(suit.doId, 'stormCellDamage', self.getSuitConditionModifier(suit.doId, 'stormCellDamage') - 6, -1, 'setBoth')
                if suit.dna.name == 'cdirector':
                    self.setSuitCondition(suit.doId, 'contingencyHit', 1, 1, 'setBoth')
               # for s in self.battle.activeSuits:
                   # if s.dna.name == 'sgoat' and self.suitHasCondition(s.doId, 'shielding'):
                     #   self.setSuitCondition(s.doId, 'rageBuilding', self.getSuitConditionModifier(s.doId, 'rageBuilding') + 10, -1, 'setBoth')
                      #  self.notify.debug('setSuitCondition() - scapegoat rage building %i' % (self.getSuitConditionModifier(s.doId, 'rageBuilding')))
                if self.toonHasCondition(toon.doId, 'useTrap'):
                    self.setToonCondition(toon.doId, 'rushJobCompleted', 1, 3, 'setBoth')
                self.setToonCondition(toon.doId, 'usedTrap', 1, 3, 'setBoth')
                if organicBonus:
                    damage = (getTrapDamage(trapLvl, toon, suit) * 1.15)
                    self.setSuitCondition(suitId, 'dazed2', 1, 10, 'setBoth')
                else:
                    damage = getTrapDamage(trapLvl, toon, suit)
                    self.setSuitCondition(suitId, 'dazed2', 1, 10, 'setBoth')
                if self.suitHasCondition(suitId, 'sued'):
                    self.setSuitCondition(suitId, 'sued', 1, 4, 'alternateBoth')
                if self.suitHasCondition(suitId, 'lured'):
                    self.setSuitCondition(suitId, 'lured', 0, 0, 'setBoth')
                if self.toonHasCondition(attackerId, 'highStakesBoost'):
                    damage *= (1.0 + self.getToonConditionModifier(attackerId, 'highStakesBoost') * 0.01)
                if self.toonHasCondition(attackerId, 'trapBoost'):
                    damage *= (1.0 + self.getToonConditionModifier(attackerId, 'trapBoost') * 0.01)
                if self.toonHasCondition(attackerId, 'encore'):
                    damage *= 1.2
                if self.toonHasCondition(attackerId, 'encore2'):
                    damage *= 1.1
                if self.toonHasCondition(attackerId, 'allGagBoost'):
                    damage *= (1.0 + self.getToonConditionModifier(attackerId, 'allGagBoost') * 0.01)
                if self.toonHasCondition(attackerId, 'allGagBoost2'):
                    damage *= (1.0 + self.getToonConditionModifier(attackerId, 'allGagBoost2') * 0.01)
                if self.toonHasCondition(attackerId, 'viralSensation'):
                    damage *= (1.0 + self.getToonConditionModifier(attackerId, 'viralSensation') * 0.01)
                if self.toonHasCondition(attackerId, 'energized'):
                    damage *= (1.0 + self.getToonConditionModifier(attackerId, 'energized') * 0.01)
                if self.toonHasCondition(attackerId, 'governaughtBoost'):
                    damage *= (1.0 + self.getToonConditionModifier(attackerId, 'governaughtBoost') * 0.01)
                if self.toonHasCondition(attackerId, 'raisedAnte'):
                    damage *= (1.0 + self.getToonConditionModifier(attackerId, 'raisedAnte') * 0.01)
                if suit.dna.name == 'hustle' and self.toonHasCondition(attackerId, 'hustlerTarget'):
                    damage *= 0.5
                if self.toonHasCondition(attackerId, 'partnered'):
                    if self.suitHasCondition(suitId, 'partnered'):
                        damage *= 1.5
                    else:
                        damage *= 0.5
                if not self.suitHasCondition(suitId, 'alreadyTargeted'):
                    self.setSuitCondition(suitId, 'alreadyTargeted', 1, 1, 'setBoth')
                    self.targets += 1
                if not self.suitHasCondition(suitId, 'alreadyTargeted'):
                    self.setSuitCondition(suitId, 'alreadyTargeted', 1, 1, 'setBoth')
                    self.targets += 1
               # if self.suitHasCondition(suitId, 'enraged'):
                   # damage *= 0.7
                if self.suitHasCondition(suitId, 'dancesession'):
                    damage *= 0.7
                if suit.dna.name == 'erfit':
                    self.countErfitHP += damage
                if suit.dna.name == 'erclaim':
                    self.countErclaimHP += damage
             #   for s in self.battle.activeSuits:
                  #  if self.suitHasCondition(s.doId, 'shielding') and not self.suitHasCondition(suitId, 'shielding'):
                    #    damage *= .7
                        #self.absorbDamage += int((damage * .425))
                instakillDamage = self.__getInstakillDamage(attackerId)
                if instakillDamage:
                    self.instakillTraps[suitId] = instakillDamage
                    damage = min(instakillDamage, 32767)
                else:
                    self.instakillTraps.pop(suitId, None)
                if self.itemIsCredit(TRAP, trapLvl):
                    self.traps[suitId] = [trapLvl, attackerId, damage]
                else:
                    self.traps[suitId] = [trapLvl, 0, damage]
                self.__addLuredSuitsDelayed(attackerId, targetId=-1, ignoreDamageCheck=True)
        else:
            if suitId in self.traps:
                if self.traps[suitId][0] == self.TRAP_CONFLICT:
                    self.instakillTraps.pop(suitId, None)
                    self.traps[suitId] = [
                        trapLvl, 0, npcDamage]
            else:
                if not self.__suitIsLured(suitId):
                    self.instakillTraps.pop(suitId, None)
                    self.traps[suitId] = [
                        trapLvl, 0, npcDamage]

    def getConditionCount(self, targetId, conds):
        return sum(1 for cond in conds if self.suitHasCondition(targetId, cond))

    def __addSuitTrap(self, suitId, trapLvl, attackerId, npcDamage=0):
        if npcDamage == 0:
            if suitId in self.traps:
                self.instakillTraps.pop(suitId, None)
                if self.traps[suitId][0] == self.TRAP_CONFLICT:
                    pass
                else:
                    self.traps[suitId][0] = self.TRAP_CONFLICT
            else:
                attack = self.battle.toonAttacks[attackerId]
                atkTrack, atkLevel, atkHp = self.__getActualTrackLevelHp(attack)
                toon = self.battle.getToon(attackerId)
                suit = self.battle.findSuit(suitId)
                organicBonus = toon.checkGagBonus(TRAP, trapLvl)
                if self.toonHasCondition(toon.doId, 'nolevel8s') and atkLevel == 7:
                    for suit in self.battle.activeSuits:
                        self.setSuitCondition(suit.doId, 'bannedGagUsed', 1, 1, 'setBoth')
                    self.setToonCondition(toon.doId, 'banned', 1, 1, 'setBoth')
                if self.toonHasCondition(toon.doId, 'nolevel7s') and atkLevel == 6:
                    for suit in self.battle.activeSuits:
                        self.setSuitCondition(suit.doId, 'bannedGagUsed', 1, 1, 'setBoth')
                    self.setToonCondition(toon.doId, 'banned', 1, 1, 'setBoth')
                if self.toonHasCondition(toon.doId, 'nolevel6s') and atkLevel == 5:
                    for suit in self.battle.activeSuits:
                        self.setSuitCondition(suit.doId, 'bannedGagUsed', 1, 1, 'setBoth')
                    self.setToonCondition(toon.doId, 'banned', 1, 1, 'setBoth')
                if self.toonHasCondition(toon.doId, 'nolevel5s') and atkLevel == 4:
                    for suit in self.battle.activeSuits:
                        self.setSuitCondition(suit.doId, 'bannedGagUsed', 1, 1, 'setBoth')
                    self.setToonCondition(toon.doId, 'banned', 1, 1, 'setBoth')
                if self.toonHasCondition(toon.doId, 'nolevel4s') and atkLevel == 3:
                    for suit in self.battle.activeSuits:
                        self.setSuitCondition(suit.doId, 'bannedGagUsed', 1, 1, 'setBoth')
                    self.setToonCondition(toon.doId, 'banned', 1, 1, 'setBoth')
                if self.toonHasCondition(toon.doId, 'noTrapGags'):
                    for suit in self.battle.activeSuits:
                        self.setSuitCondition(suit.doId, 'bannedGagUsed', 1, 1, 'setBoth')
                    self.setToonCondition(toon.doId, 'banned2', 1, 1, 'setBoth')
                if self.toonHasCondition(toon.doId, 'noGags'):
                    for suit in self.battle.activeSuits:
                        self.setSuitCondition(suit.doId, 'bannedGagUsed', 1, 1, 'setBoth')
                    self.setToonCondition(toon.doId, 'banned3', 1, 1, 'setBoth')
                suit = self.battle.findSuit(suitId)
                if suit.dna.name == 'supervis' and suit.getActualLevel() == 20:
                    self.levels += atkLevel
               # for s in self.battle.activeSuits:
                   # if s.dna.name == 'sgoat' and self.suitHasCondition(s.doId, 'shielding'):
                    #    self.setSuitCondition(s.doId, 'rageBuilding', self.getSuitConditionModifier(s.doId, 'rageBuilding') + 10, -1, 'setBoth')
                      #  self.notify.debug('setSuitCondition() - scapegoat rage building %i' % (
                         #   self.getSuitConditionModifier(s.doId, 'rageBuilding')))
                if suit.dna.name == 'bkeeper' and self.suitHasCondition(suitId, 'bookkeeping'):
                    self.setToonCondition(toon.doId, 'bookkeepingtoon', 1, 1, 'setBoth')
                    self.setSuitCondition(suit.doId, 'bookkeeperHit', 1, 1, 'setBoth')
                if suit.dna.name == 'ubuster':
                    self.hustlerHits += 1
                if suit.dna.name == 'rkeeper':
                    self.setSuitCondition(suit.doId, 'recordkeeperHit', 1, 1, 'setBoth')
                if suit.dna.name == 'wtapper' and self.toonHasCondition(toon.doId, 'partnered'):
                    self.setSuitCondition(suit.doId, 'wiretapperHit2', 1, 1, 'setBoth')
                    self.setToonCondition(toon.doId, 'collectcalled', 0, 0, 'setBoth')
                if suit.dna.name == 'hustle' and self.toonHasCondition(toon.doId, 'partnered'):
                    self.setSuitCondition(suit.doId, 'wiretapperHit2', 1, 1, 'setBoth')
                if suit.dna.name == 'wtapper':
                    self.setSuitCondition(suit.doId, 'wiretapperHit', 1, 1, 'setBoth')
                if suit.dna.name == 'hustle':
                    self.setToonCondition(toon.doId, 'bookkeepingtoon', 1, 1, 'setBoth')
                    self.setSuitCondition(suit.doId, 'bookkeeperHit', 1, 1, 'setBoth')
                if suit.dna.name == 'dopr':
                    self.setSuitCondition(suit.doId, 'doprHit', 1, 1, 'setBoth')
                if suit.dna.name == 'supervis' and suit.getActualLevel() == 30:
                    self.setSuitCondition(suit.doId, 'doprHit', 1, 1, 'setBoth')
                if suit.dna.name == 'dopa':
                    self.setSuitCondition(suit.doId, 'dopaHit', 1, 1, 'setBoth')
                if self.suitHasCondition(suit.doId, 'trapRushJob'):
                    self.setSuitCondition(suit.doId, 'trapRushJob', 0, 0, 'setBoth')
                if suit.dna.name == 'liquid':
                    self.setSuitCondition(suit.doId, 'tollmasterHit', 1, 1, 'setBoth')
                    self.setToonCondition(toon.doId, 'tollmasterHit', 1, 1, 'setBoth')
                if suit.dna.name == 'liquid' and self.suitHasCondition(suitId, 'stormCellDamage'):
                    self.setSuitCondition(suit.doId, 'stormCellDamage', self.getSuitConditionModifier(suit.doId, 'stormCellDamage') - 6, -1, 'setBoth')
                if suit.dna.name == 'cdirector':
                    self.setSuitCondition(suit.doId, 'contingencyHit', 1, 1, 'setBoth')
                if self.toonHasCondition(toon.doId, 'useTrap'):
                    self.setToonCondition(toon.doId, 'rushJobCompleted', 1, 3, 'setBoth')
                self.setToonCondition(toon.doId, 'usedTrap', 1, 3, 'setBoth')
                if organicBonus:
                    damage = (getTrapDamage(trapLvl, toon, suit) * 1.15)
                    self.setSuitCondition(suitId, 'dazed2', 1, 10, 'setBoth')
                else:
                    damage = getTrapDamage(trapLvl, toon, suit)
                    self.setSuitCondition(suitId, 'dazed2', 1, 10, 'setBoth')
                if self.suitHasCondition(suitId, 'sued'):
                    self.setSuitCondition(suitId, 'sued', 1, 4, 'alternateBoth')
                if self.suitHasCondition(suitId, 'lured'):
                    self.setSuitCondition(suitId, 'lured', 0, 0, 'setBoth')
                if self.toonHasCondition(attackerId, 'highStakesBoost'):
                    damage *= (1.0 + self.getToonConditionModifier(attackerId, 'highStakesBoost') * 0.01)
                if self.toonHasCondition(attackerId, 'trapBoost'):
                    damage *= (1.0 + self.getToonConditionModifier(attackerId, 'trapBoost') * 0.01)
                if self.toonHasCondition(attackerId, 'encore'):
                    damage *= 1.2
                if self.toonHasCondition(attackerId, 'encore2'):
                    damage *= 1.1
                if self.toonHasCondition(attackerId, 'allGagBoost'):
                    damage *= (1.0 + self.getToonConditionModifier(attackerId, 'allGagBoost') * 0.01)
                if self.toonHasCondition(attackerId, 'allGagBoost2'):
                    damage *= (1.0 + self.getToonConditionModifier(attackerId, 'allGagBoost2') * 0.01)
                if self.toonHasCondition(attackerId, 'viralSensation'):
                    damage *= (1.0 + self.getToonConditionModifier(attackerId, 'viralSensation') * 0.01)
                if self.toonHasCondition(attackerId, 'energized'):
                    damage *= (1.0 + self.getToonConditionModifier(attackerId, 'energized') * 0.01)
                if self.toonHasCondition(attackerId, 'governaughtBoost'):
                    damage *= (1.0 + self.getToonConditionModifier(attackerId, 'governaughtBoost') * 0.01)
                if self.toonHasCondition(attackerId, 'raisedAnte'):
                    damage *= (1.0 + self.getToonConditionModifier(attackerId, 'raisedAnte') * 0.01)
                if not self.suitHasCondition(suitId, 'alreadyTargeted'):
                    self.setSuitCondition(suitId, 'alreadyTargeted', 1, 1, 'setBoth')
                    self.targets += 1
                if suit.dna.name == 'hustle' and self.toonHasCondition(attackerId, 'hustlerTarget'):
                    damage *= 0.5
                if self.toonHasCondition(attackerId, 'partnered'):
                    if self.suitHasCondition(suitId, 'partnered'):
                        damage *= 1.5
                    else:
                        damage *= 0.5
             #   for s in self.battle.activeSuits:
                   # if self.suitHasCondition(s.doId, 'shielding') and not self.suitHasCondition(suitId, 'shielding'):
                      #  damage *= .7
                       # self.absorbDamage += int((damage * .425))
                instakillDamage = self.__getInstakillDamage(attackerId)
                if instakillDamage:
                    self.instakillTraps[suitId] = instakillDamage
                    damage = min(instakillDamage, 32767)
                else:
                    self.instakillTraps.pop(suitId, None)
                if self.itemIsCredit(TRAP, trapLvl):
                    self.traps[suitId] = [
                        trapLvl, attackerId, damage]
                else:
                    self.traps[suitId] = [trapLvl, 0, damage]
        else:
            if suitId in self.traps:
                if self.traps[suitId][0] == self.TRAP_CONFLICT:
                    self.instakillTraps.pop(suitId, None)
                    self.traps[suitId] = [
                        trapLvl, 0, npcDamage]
            else:
                if not self.__suitIsLured(suitId):
                    self.instakillTraps.pop(suitId, None)
                    self.traps[suitId] = [
                        trapLvl, 0, npcDamage]

    def __removeSuitTrap(self, suitId):
        if suitId in self.traps:
            del self.traps[suitId]

    def __clearTrapCreator(self, creatorId, suitId = None):
        if suitId == None:
            for currTrap in self.traps.keys():
                if creatorId == self.traps[currTrap][1]:
                    self.traps[currTrap][1] = 0

        elif suitId in self.traps:
            self.traps[suitId][1] = 0

    def __trapCreator(self, suitId):
        if suitId in self.traps:
            return self.traps[suitId][1]
        else:
            return 0

    def __initTraps(self):
        self.trainTrapTriggered = False
        keysList = self.traps.keys()
        for currTrap in keysList:
            if self.traps[currTrap][0] == TRAP_CONFLICT:
                del self.traps[currTrap]

    def applySoundHitEffects(self, toon, toonId, suit, targetId, atkLevel, attackDamage):
        #self.setSuitCondition(targetId, 'sounded', 1, 1, 'setBoth')
        if self.suitHasCondition(targetId, 'soundRushJob'):
            self.setSuitCondition(targetId, 'soundRushJob', 0, 0, 'setBoth')

        self.setSuitCondition(targetId, 'soundcalculator', 1, 1, 'setBoth')

        self.setToonCondition(toonId, 'usedSound', 1, 3, 'setBoth')

        if self.toonHasCondition(toonId, 'useSound'):
            self.setToonCondition(toonId, 'rushJobCompleted', 1, 3, 'setBoth')

    def calculateSquirtTargetDamage(self, baseDamage, toon, toonId, suit, suitId, atkLevel, organicBonus, splashMult=1.0):
        damage = baseDamage * splashMult

        if damage <= 0:
            return 0

        damage = self.applyToonGagDamageMultipliers(
            damage,
            toonId,
            suitId,
            SQUIRT,
            atkLevel,
            organicBonus=organicBonus
        )

        damage = self.applyCogDamageInterceptors(
            damage,
            toonId,
            suit,
            suitId,
            SQUIRT
        )

        if damage > 0:
            if self.suitHasCondition(suitId, 'squirtRushJob'):
                self.setSuitCondition(suitId, 'squirtRushJob', 0, 0, 'setBoth')
            if self.suitHasCondition(suitId, 'sued'):
                self.setSuitCondition(suitId, 'sued', 1, 4, 'alternateBoth')
            if suit.dna.name == 'lgator':
                self.setSuitCondition(suit.doId, 'soakedcalculator', 1, 10, 'setBoth')
                self.setToonCondition(toonId, 'soakToon', 1, 1, 'setBoth')
            if suit.dna.name == 'hrollers':
                self.setToonCondition(toonId, 'soakToon', math.ceil(baseDamage * 5), 1, 'setBoth')

            if suit.dna.name == 'phouse':
                self.setSuitCondition(suit.doId, 'soakedcalculator', 1, 10, 'setBoth')
            if suit.dna.name == 'sgoat' and not self.suitHasCondition(suitId, 'enraged'):
                self.setSuitCondition(suitId, 'rageBuilding',
                                self.getSuitConditionModifier(suitId, 'rageBuilding') + 15, -1, 'setBoth')


            if suit.dna.name == 'phouse':
                self.setSuitCondition(
                    suitId,
                    'powerhouseRotation',
                    self.getSuitConditionModifier(suitId, 'powerhouseRotation') + 15,
                    -1,
                    'setBoth'
                )
            if organicBonus:
                if suit.dna.name == 'redd':
                    self.setSuitCondition(suitId, 'drenched', 1, 1,
                                            'alternateBoth')
                if suit.getVirtual() > 0 or suit.dna.name in ('hrollers', 'bcaster'):
                    self.setSuitCondition(suitId, 'drenched', 1, self.NumRoundsSoaked[atkLevel] - 2,
                                            'alternateBoth')
                elif suit.getSkeleton() > 0 or suit.dna.name in ('foreman', 'supervis', 'clerk', 'wsi', 'autocad', 'ovt', 'dopa', 'dopr', 'bdirector', 'sya', 'pbl'):
                    self.setSuitCondition(suitId, 'drenched', 1, self.NumRoundsSoaked[atkLevel] - 1,
                                            'alternateBoth')
                else:
                    self.setSuitCondition(suitId, 'drenched', 1, self.NumRoundsSoaked[atkLevel],
                                        'alternateBoth')
            else:
                if suit.dna.name == 'redd':
                    self.setSuitCondition(suitId, 'soaked', 1, 1,
                                            'alternateBoth')
                if suit.getVirtual() > 0 or suit.dna.name in ('hrollers', 'bcaster'):
                    self.setSuitCondition(suitId, 'soaked', 1, self.NumRoundsSoaked[atkLevel] - 2,
                                            'alternateBoth')
                elif suit.getSkeleton() > 0 or suit.dna.name in ('foreman', 'supervis', 'clerk', 'wsi', 'autocad', 'ovt', 'dopa', 'dopr', 'bdirector', 'sya', 'pbl'):
                    self.setSuitCondition(suitId, 'soaked', 1, self.NumRoundsSoaked[atkLevel] - 1,
                                            'alternateBoth')
                else:
                    self.setSuitCondition(suitId, 'soaked', 1, self.NumRoundsSoaked[atkLevel],
                                        'alternateBoth')

        return damage

    def applyToonGagUseEffects(self, toonId, atkTrack):
        trackUseConditions = {
            DROP:   ('useDrop',   'usedDrop'),
            HEAL:   ('useToonUp', 'usedHeal'),
            TRAP:   ('useTrap',   'usedTrap'),
            LURE:   ('useLure',   'usedLure'),
            THROW:  ('useThrow',  'usedThrow'),
            SQUIRT: ('useSquirt', 'usedSquirt'),
            ZAP:    ('useZap',    'usedZap'),
            SOUND:  ('useSound',  'usedSound')
        }

        if atkTrack not in trackUseConditions:
            return

        requiredCond, usedCond = trackUseConditions[atkTrack]

        if self.toonHasCondition(toonId, requiredCond):
            self.setToonCondition(toonId, 'rushJobCompleted', 1, 1, 'setBoth')

        self.setToonCondition(toonId, usedCond, 1, 1, 'setBoth')

    def applyCogHitEffects(self, toon, toonId, suit, targetId, atkTrack, atkLevel, attackDamage, unLureSuit=True):
        rushJobMap = {
            TRAP: 'trapRushJob',
            LURE: 'lureRushJob',
            THROW: 'throwRushJob',
            SQUIRT: 'squirtRushJob',
            ZAP: 'zapRushJob',
            SOUND: 'soundRushJob',
            DROP: 'dropRushJob',
        }
        if attackDamage > 0:
            rushCond = rushJobMap.get(atkTrack)

            if rushCond and self.suitHasCondition(targetId, rushCond):
                self.setSuitCondition(targetId, rushCond, 0, 0, 'setBoth')
            
            # Use the new status effect system to get rid of completed Rush Jobs.
            for i in range(len(self.suitStatusConditionsNew[targetId]) - 1, -1, -1): # Sift through all of the target Cog's status effects.
                if isinstance(self.suitStatusConditionsNew[targetId][i], StatusEffects.RushJob) and self.suitStatusConditionsNew[targetId][i].trackToUse == atkTrack: # Check to see if the status effect is a Rush Job and if the track that is required to use is used by the Toon.
                    del self.suitStatusConditionsNew[targetId][i] # Remove the effect.

        if not self.suitHasCondition(targetId, 'alreadyTargeted'):
            self.setSuitCondition(targetId, 'alreadyTargeted', 1, 1, 'setBoth')
            self.targets += 1
        
        if unLureSuit == True:
            if self.suitHasCondition(targetId, 'unlureSuit'):
                self.setSuitCondition(targetId, 'unlureSuit', 0, 0, 'setBoth')

        if self.suitHasCondition(targetId, 'sued'):
            self.setSuitCondition(targetId, 'sued', 1, 4, 'alternateBoth')

        if suit.dna.name == 'supervis' and suit.getActualLevel() == 20:
            self.levels += atkLevel

        if suit.dna.name == 'clubpres' and suit.getActualLevel() == 25:
            self.setSuitCondition(
                suit.doId,
                'shivering',
                self.getSuitConditionModifier(suit.doId, 'shivering') + 1,
                1,
                'setBoth'
            )

        if suit.dna.name == 'clubpres' and suit.getActualLevel() == 23:
            self.setSuitCondition(
                suit.doId,
                'rpm',
                self.getSuitConditionModifier(suit.doId, 'rpm') + 1,
                1,
                'setBoth'
            )

        # if suit.dna.name == 'cbutcher':
        #     self.setSuitCondition(
        #         suit.doId,
        #         'rpmincrease',
        #         self.getSuitConditionModifier(suit.doId, 'rpmincrease') + 1,
        #         -1,
        #         'setBoth'
        #     )
        #     self.setSuitCondition(suit.doId, 'rpmcalculator', 1, 10, 'setBoth')

        if suit.dna.name == 'bkeeper' and self.suitHasCondition(targetId, 'bookkeeping'):
            self.setToonCondition(toon.doId, 'bookkeepingtoon', 1, 1, 'setBoth')
            self.setSuitCondition(suit.doId, 'bookkeeperHit', 1, 1, 'setBoth')

        if suit.dna.name == 'hustle':
            self.setToonCondition(toon.doId, 'bookkeepingtoon', 1, 1, 'setBoth')
            self.setSuitCondition(suit.doId, 'bookkeeperHit', 1, 1, 'setBoth')

        if suit.dna.name == 'ubuster':
            self.hustlerHits += 1

        if suit.dna.name == 'rkeeper':
            self.setSuitCondition(suit.doId, 'recordkeeperHit', 1, 1, 'setBoth')

        if suit.dna.name == 'wtapper' and self.toonHasCondition(toon.doId, 'partnered'):
            self.setSuitCondition(suit.doId, 'wiretapperHit2', 1, 1, 'setBoth')
            self.setToonCondition(toon.doId, 'collectcalled', 0, 0, 'setBoth')

        if suit.dna.name == 'hustle' and self.toonHasCondition(toon.doId, 'partnered'):
            self.setSuitCondition(suit.doId, 'wiretapperHit2', 1, 1, 'setBoth')

        if suit.dna.name == 'wtapper':
            self.setSuitCondition(suit.doId, 'wiretapperHit', 1, 1, 'setBoth')

        if suit.dna.name == 'hustle':
            self.setSuitCondition(suit.doId, 'wiretapperHit', 1, 1, 'setBoth')

        if suit.dna.name == 'dopr':
            self.setSuitCondition(suit.doId, 'doprHit', 1, 1, 'setBoth')

        if suit.dna.name == 'supervis' and suit.getActualLevel() == 30:
            self.setSuitCondition(suit.doId, 'doprHit', 1, 1, 'setBoth') 

        if suit.dna.name == 'dopa':
            self.setSuitCondition(suit.doId, 'dopaHit', 1, 1, 'setBoth')

        if suit.dna.name == 'lgator' and atkTrack == SQUIRT:
            self.setSuitCondition(suit.doId, 'soakedcalculator', 1, 10, 'setBoth')

        if suit.dna.name == 'wsi' and atkTrack == SQUIRT:
            self.setSuitCondition(suit.doId, 'soakedcalculator', 1, 10, 'setBoth')

        if suit.dna.name == 'redd' and atkTrack == SQUIRT:
            self.setSuitCondition(suit.doId, 'soakedcalculator', 1, 10, 'setBoth')

        if suit.dna.name == 'phouse' and atkTrack == SQUIRT:
            self.setSuitCondition(suit.doId, 'soakedcalculator', 1, 10, 'setBoth')

        if suit.dna.name == 'phouse' and atkTrack == ZAP:
            self.setSuitCondition(suit.doId, 'zappedcalculator', 1, 10, 'setBoth')

        if suit.dna.name == 'dking' and atkTrack == ZAP:
            self.setSuitCondition(suit.doId, 'zappedcalculator', 1, 10, 'setBoth')

        if suit.dna.name == 'liquid':
            self.setSuitCondition(suit.doId, 'tollmasterHit', 1, 1, 'setBoth')
            self.setToonCondition(toon.doId, 'tollmasterHit', 1, 1, 'setBoth')

        if suit.dna.name == 'liquid' and self.suitHasCondition(suit.doId, 'stormCellDamage'):
            self.setSuitCondition(
                suit.doId,
                'stormCellDamage',
                self.getSuitConditionModifier(suit.doId, 'stormCellDamage') - 6,
                -1,
                'setBoth'
            )

        if suit.dna.name == 'cdirector':
            self.setSuitCondition(suit.doId, 'contingencyHit', 1, 1, 'setBoth')

        if suit.dna.name == 'racket':
            if self.racketeerMultiplier == 0:
                pass
            else:
                self.racketeerMultiplier -= 1

        if suit.dna.name == 'sgoat' and not self.suitHasCondition(targetId, 'enraged'):
            self.setSuitCondition(targetId, 'rageBuilding',
                                self.getSuitConditionModifier(targetId, 'rageBuilding') + (
                                        attackDamage * .1), -1, 'setBoth')


        if suit.dna.name == 'phouse':
            self.setSuitCondition(
                targetId,
                'powerhouseRotation',
                self.getSuitConditionModifier(targetId, 'powerhouseRotation') + (attackDamage * 0.1),
                -1,
                'setBoth'
            )

        if suit.dna.name == 'erfit':
            self.countErfitHP += attackDamage

        if suit.dna.name == 'erclaim':
            self.countErclaimHP += attackDamage

    def applyThrowMarkEffects(self, toon, toonId, targetId, atkTrack, atkLevel):
        if atkTrack != THROW:
            return

        self.setToonCondition(toon.doId, 'markToon', 1, 5, 'setBoth')

        organicBonus = self.__toonCheckGagBonus(toonId, THROW, atkLevel)

        if organicBonus:
            if self.suitHasCondition(targetId, 'marked2') and self.getSuitConditionTurns(targetId, 'marked2') == 1:
                self.setSuitCondition(targetId, 'markedThrow', 1, 1, 'setBoth')

            self.setSuitCondition(targetId, 'marked', 1, 2, 'setBoth')
            self.setSuitCondition(targetId, 'marked2', 1, 2, 'setBoth')

        else:
            if self.suitHasCondition(targetId, 'marked2') and self.getSuitConditionTurns(targetId, 'marked2') == 1:
                self.setSuitCondition(targetId, 'markedThrow', 1, 1, 'setBoth')

            if not self.suitHasCondition(targetId, 'marked'):
                self.setSuitCondition(targetId, 'marked', 1, 1, 'setBoth')

    def getAbsorbDamageForTrackName(self, name):
        trackByName = {
            'AbsorbMovieLure': LURE,
            'AbsorbMovieThrow': THROW,
            'AbsorbMovieSquirt': SQUIRT,
            'AbsorbMovieZap': ZAP,
            'AbsorbMovieSound': SOUND,
            'AbsorbMovieDrop': DROP
        }

        track = trackByName.get(name)
        if track is None:
            return self.absorbDamage

        return self.absorbDamageByTrack.get(track, 0)

    def addLevelDamage(self, amount, atkTrack=None):
        amount = int(math.ceil(amount))

        self.levelDamage += amount

        if atkTrack in self.levelDamageByTrack:
            self.levelDamageByTrack[atkTrack] += amount
        else:
            self.levelDamageByTrack[LURE] += amount

    def __addLevelDamage(self, amount, atkTrack=None):
        self.levelDamage += amount

        if atkTrack in self.levelDamageByTrack:
            self.levelDamageByTrack[atkTrack] += amount
        else:
            self.levelDamageByTrack[LURE] += amount


    def getLevelDamageForTrackName(self, name):
        trackByName = {
            'AbsorbMovieLevelLure': LURE,
            'AbsorbMovieLevelThrow': THROW,
            'AbsorbMovieLevelSquirt': SQUIRT,
            'AbsorbMovieLevelZap': ZAP,
            'AbsorbMovieLevelSound': SOUND,
            'AbsorbMovieLevelDrop': DROP
        }

        track = trackByName.get(name)
        if track is None:
            return self.levelDamage

        return self.levelDamageByTrack.get(track, 0)

    def applyCogDamageInterceptors(self, attackDamage, toonId, suit, targetId, atkTrack):
        # Scapegoat-style shielding.
        for s in self.battle.activeSuits:
            if (
                self.suitHasCondition(s.doId, 'shielding') and
                not self.suitHasCondition(targetId, 'shielding') and
                atkTrack not in (FIRE, HEAL, SUE) and
                s.getHP() > 0 and not self.suitHasCondition(s.doId, 'dead')
            ):
                attackDamage *= 0.7
                absorbed = math.ceil(attackDamage * 0.5)
                self.absorbDamage += absorbed

                if atkTrack in self.absorbDamageByTrack:
                    self.absorbDamageByTrack[atkTrack] += absorbed
                self.setSuitCondition(
                    s.doId,
                    'rageBuilding',
                    self.getSuitConditionModifier(s.doId, 'rageBuilding') + (absorbed * 0.1),
                    -1,
                    'setBoth'
                )

            if (
                self.suitHasCondition(s.doId, 'recordkeeperShielding') and
                not self.suitHasCondition(targetId, 'recordkeeperShielding') and
                atkTrack not in (FIRE, HEAL, SUE) and
                s.getHP() > 0
            ):
                # Your old code only applies this if the TARGET is rkeeper.
                if suit.dna.name == 'rkeeper':
                    attackDamage *= 0.1
                    self.absorbDamageRecordkeeper += math.ceil(attackDamage * 0.9)

        # Rainmaker-style stored damage.
        if suit.dna.name == 'sgoat' and not self.suitHasCondition(suit.doId, 'enraged'):
             self.setSuitCondition(
                    suit.doId,
                    'rageBuilding',
                    self.getSuitConditionModifier(suit.doId, 'rageBuilding') + math.ceil(math.ceil(attackDamage * 0.1) - 15),
                    -1,
                    'setBoth'
                )
        if suit.dna.name == 'phouse':
             self.setSuitCondition(
                    suit.doId,
                    'powerhouseRotation',
                    self.getSuitConditionModifier(suit.doId, 'powerhouseRotation') + math.ceil(math.ceil(attackDamage * 0.1) - 15),
                    -1,
                    'setBoth'
                )
        if self.suitHasCondition(targetId, 'heavyRainDamage'):
            attackDamage *= 0.6
            self.setSuitCondition(
                targetId,
                'heavyRainDamage',
                self.getSuitConditionModifier(targetId, 'heavyRainDamage') + attackDamage,
                -1,
                'setBoth'
            )

        return attackDamage

    def applyToonGagDamageMultipliers(self, damage, toonId, suitId, atkTrack, atkLevel, organicBonus=False):
        mult = 1.0
        suit = self.battle.findSuit(suitId)
        trackBoosts = {
            THROW: 'throwBoost',
            SQUIRT: 'squirtBoost',
            SOUND: 'soundBoost',
            DROP: 'dropBoost',
            ZAP: 'zapBoost'
        }

        boostCond = trackBoosts.get(atkTrack)
        if boostCond and self.toonHasCondition(toonId, boostCond) and atkTrack != TRAP:
            mult *= 1.0 + self.getToonConditionModifier(toonId, boostCond) * 0.01

        if atkTrack not in (SOUND, LURE, TRAP):
            if self.toonHasCondition(toonId, 'encore'):
                mult *= 1.2
            if self.toonHasCondition(toonId, 'encore2'):
                mult *= 1.1
        else:
            if atkTrack not in (LURE, TRAP):
                if self.getToonConditionTurns(toonId, 'encore') == 1 and self.toonHasCondition(toonId, 'encore'):
                    mult *= 1.2
                if self.getToonConditionTurns(toonId, 'encore2') == 1 and self.toonHasCondition(toonId, 'encore2'):
                    mult *= 1.1
                if self.getToonConditionTurns(toonId, 'winded') < 3 and self.toonHasCondition(toonId, 'winded'):
                    mult *= .5

        for cond in ('allGagBoost', 'allGagBoost2', 'viralSensation', 'energized', 'raisedAnte', 'governaughtBoost', 'highStakesBoost'):
            if self.toonHasCondition(toonId, cond) and atkTrack != LURE and atkTrack != TRAP:
                mult *= 1.0 + self.getToonConditionModifier(toonId, cond) * 0.01

        if self.toonHasCondition(toonId, 'groupDamageDown'):
            if atkTrack in (ZAP, SOUND, SQUIRT):
                mult *= 0.5
            elif atkTrack == HEAL and atkLevel in (1, 3, 5, 7):
                mult *= 0.5

        if self.suitHasCondition(suitId, 'oilRain') and atkTrack == SQUIRT:
            return 0

        if self.toonHasCondition(toonId, 'noDamage'):
            return 0

        if self.toonHasCondition(toonId, 'partnered') and atkTrack not in (LURE, TRAP):
            if self.suitHasCondition(suitId, 'partnered'):
                mult *= 1.5
            else:
                mult *= 0.5

        if organicBonus and atkTrack == DROP:
            count = self.getConditionCount(suitId, ['dazed', 'soaked', 'marked', 'zapped', 'drenched'])
            if count > 0:
                mult *= 1.1 + ((count - 1) * 0.05)

        if self.suitHasCondition(suitId, 'immune'):
            return 0

        if atkTrack == DROP and self.suitHasCondition(suitId, 'dropImmune'):
            return 0

        if atkTrack == THROW and self.suitHasCondition(suitId, 'markImmune'):
            return 0

        if atkTrack == SOUND and self.suitHasCondition(suitId, 'soundImmune'):
            return 0

        if atkTrack == ZAP and self.suitHasCondition(suitId, 'zapImmune'):
            return 0

        if self.suitHasCondition(suitId, 'HRdamagereduction'):
            mult *= 0.1

        if self.suitHasCondition(suitId, 'trapRushJob') and atkTrack != LURE:
            mult *= 0.6

        if self.suitHasCondition(suitId, 'lureRushJob') and atkTrack != LURE:
            mult *= 0.6

        if self.suitHasCondition(suitId, 'throwRushJob') and atkTrack != THROW:
            mult *= 0.6

        if self.suitHasCondition(suitId, 'squirtRushJob') and atkTrack != SQUIRT:
            mult *= 0.6

        if self.suitHasCondition(suitId, 'soundRushJob') and atkTrack != SOUND:
            mult *= 0.6

        if self.suitHasCondition(suitId, 'dropRushJob') and atkTrack != DROP:
            mult *= 0.6

        if self.suitHasCondition(suitId, 'zapRushJob') and atkTrack != ZAP:
            mult *= 0.6
        
        for effect in self.getAllRelevantConditions(suitId, StatusEffects.RushJob, toon=False): # Get all Rush Job status effects from the Cog.
            if atkTrack != effect.trackToUse: # Is the track different from what the Rush Job is calling for?
                mult *= effect.defenseMod # Apply the damage reduction.
                break # We'll break because we probably do not want repeated damage reduction if, for some reason, two or more Rush Jobs are placed on the same Cog.

        if self.suitHasCondition(suitId, 'damageReduction'):
            mult *= 0.7

        if self.suitHasCondition(suitId, 'monsoon'):
            mult *= 0.1

        if self.suitHasCondition(suitId, 'enraged') and not self.suitHasCondition(suitId, 'desperation'):
            mult *= 0.7

        if self.suitHasCondition(suitId, 'vulnerable'):
            mult *= 1.3

        if self.suitHasCondition(suitId, 'dancesession'):
            mult *= 0.7

        if self.suitHasCondition(suitId, 'vulnerablebroadcaster'):
            mult *= 2.0

        if self.suitHasCondition(suitId, 'vulnerablesilhouette1'):
            mult *= 1.5

        if self.suitHasCondition(suitId, 'vulnerablesilhouette2'):
            mult *= 2.0

        if self.suitHasCondition(suitId, 'vulnerablesilhouette3'):
            mult *= 3.0

        if self.suitHasCondition(suitId, 'marked') and atkTrack != THROW:
            mult *= 1.1

        if self.suitHasCondition(suitId, 'markedThrow') and atkTrack == THROW:
            mult *= 1.1

        if self.suitHasCondition(suitId, 'soakImmune') and (self.suitHasCondition(suitId, 'soaked') or self.suitHasCondition(suitId, 'drenched')):
            mult *= 0.4

        if suit.dna.name == 'hustle' and self.toonHasCondition(toonId, 'hustlerTarget'):
            mult *= 0.5

        if self.getSuitConditionTurns(suitId, 'sleepy') == 2 and self.suitHasCondition(suitId, 'sleepy'):
            mult *= 0.3
        elif self.getSuitConditionTurns(suitId, 'sleepy') == 1 and self.suitHasCondition(suitId, 'sleepy'):
            mult *= 0.6

        if self.suitHasCondition(suitId, 'directorDamageReduction'):
            mult *= self.getSuitConditionModifier(suitId, 'directorDamageReduction')

        if self.suitHasCondition(suitId, 'vulnerablevideographer'):
            mult *= self.getSuitConditionModifier(suitId, 'vulnerablevideographer')
        
        for effect in self.getAllRelevantConditions(suitId, StatusEffects.DefenseModifier, toon=False): # Find all DefenseModifier effects.
            if isinstance(effect.defenseMod, float): # Check all decimal damage reductions.  TODO: Flat damage modification.
                mult *= effect.defenseMod

        return damage * mult

    def applySoundEncoreChecks(self, toonId, atkTrack, atkLevel):
        hasTrackBonus = self.__toonCheckGagBonus(toonId, atkTrack, atkLevel)
        if self.toonHasCondition(toonId, 'soundEncoreChecked'):
            return

        self.setToonCondition(toonId, 'soundEncoreChecked', 1, 1, 'setBoth')

        if (self.toonHasCondition(toonId, 'encore') or self.toonHasCondition(toonId, 'encore2')) and not self.toonHasCondition(toonId, 'winded'):
            self.setToonCondition(toonId, 'encore', 20, 1, 'setBoth')
            self.setToonCondition(toonId, 'encore2', 10, 1, 'setBoth')
            self.setToonCondition(toonId, 'winded', -50, 3, 'setBoth')

        elif not (self.toonHasCondition(toonId, 'encore') or self.toonHasCondition(toonId, 'encore2')) and not self.toonHasCondition(toonId, 'winded'):
            if hasTrackBonus:
                self.setToonCondition(toonId, 'encore', 20, 2, 'setBoth')
            else:    
                self.setToonCondition(toonId, 'encore2', 10, 2, 'setBoth')

    def applyGagBanChecks(self, toonId, atkTrack, atkLevel):


        banned = False
        if self.toonUsedBannedGag(toonId, atkTrack, atkLevel):
            self.setToonCondition(toonId, 'banned', 1, 1, 'setBoth')

        levelBanConds = {
            7: 'nolevel8s',
            6: 'nolevel7s',
            5: 'nolevel6s',
            4: 'nolevel5s',
            3: 'nolevel4s'
        }

        if atkLevel in levelBanConds:
            if self.toonHasCondition(toonId, levelBanConds[atkLevel]):
                self.setToonCondition(toonId, 'banned', 1, 1, 'setBoth')
                banned = True

        trackBanConds = {
            HEAL: 'noToonupGags',
            TRAP: 'noTrapGags',
            LURE: 'noLureGags',
            SOUND: 'noSoundGags',
            THROW: 'noThrowGags',
            SQUIRT: 'noSquirtGags',
            ZAP: 'noZapGags',
            DROP: 'noDropGags'
        }

        if atkTrack in trackBanConds:
            if self.toonHasCondition(toonId, trackBanConds[atkTrack]):
                self.setToonCondition(toonId, 'banned2', 1, 1, 'setBoth')
                banned = True

        if self.toonHasCondition(toonId, 'noGags'):
            self.setToonCondition(toonId, 'banned3', 1, 1, 'setBoth')
            banned = True

        if banned:
            for suit in self.battle.activeSuits:
                self.setSuitCondition(suit.doId, 'bannedGagUsed', 1, 1, 'setBoth')

        return banned

    def applyLureKBModifiers(self, lureKBValue, toonId, targetId, atkLevel):
        # Flat lure KB bonuses.
        for cond in ('lureBoost', 'lureBoost2', 'governaughtBoost', 'highStakesBoost'):
            if self.toonHasCondition(toonId, cond):
                lureKBValue += self.getToonConditionModifier(toonId, cond)

        # Multipliers.
        if self.toonHasCondition(toonId, 'encore'):
            lureKBValue *= 1.2

        if self.toonHasCondition(toonId, 'encore2'):
            lureKBValue *= 1.1

        if self.suitHasCondition(targetId, 'marked'):
            lureKBValue *= 1.1

        if self.toonHasCondition(toonId, 'groupDamageDown') and atkLevel in (1, 3, 5, 7):
            lureKBValue *= 0.5

        # Hard lure KB blockers.
        if (
            self.suitHasCondition(targetId, 'immune') or
            self.suitHasCondition(targetId, 'lureImmune') or
            (
                self.suitHasCondition(targetId, 'enraged') and
                self.suitHasCondition(targetId, 'desperation')
            )
        ):
            lureKBValue = 0

        return lureKBValue

    def applyLureHitEffects(self, toon, toonId, suit, targetId):
        if suit.dna.name == 'bkeeper' and self.suitHasCondition(targetId, 'bookkeeping'):
            self.setToonCondition(toonId, 'bookkeepingtoon', 1, 1, 'setBoth')
            self.setSuitCondition(suit.doId, 'bookkeeperHit', 1, 1, 'setBoth')

        if suit.dna.name == 'hustle':
            self.setToonCondition(toonId, 'bookkeepingtoon', 1, 1, 'setBoth')
            self.setSuitCondition(suit.doId, 'bookkeeperHit', 1, 1, 'setBoth')
    

        if self.suitHasCondition(targetId, 'lureRushJob'):
            self.setSuitCondition(targetId, 'lureRushJob', 0, 0, 'setBoth')

        if suit.dna.name == 'sgoat' and not self.suitHasCondition(targetId, 'enraged'):
            self.setSuitCondition(
                targetId,
                'rageBuilding',
                self.getSuitConditionModifier(targetId, 'rageBuilding') + 15,
                -1,
                'setBoth'
            )

        if suit.dna.name == 'phouse':
            self.setSuitCondition(
                targetId,
                'powerhouseRotation',
                self.getSuitConditionModifier(targetId, 'powerhouseRotation') + 15,
                -1,
                'setBoth'
            )

    def __calcToonAtkHp(self, toonId):
        toon = self.battle.getToon(toonId)
        attack = self.battle.toonAttacks[toonId]
        targetList = self.__createToonTargetList(toonId)
        atkHit, atkAcc = self.__calcToonAtkHit(toonId, targetList)
        atkTrack, atkLevel, atkHp = self.__getActualTrackLevelHp(attack)
        if not atkHit and atkTrack == SQUIRT:
            target = self.battle.findSuit(attack[TOON_TGT_COL])
            activeSuits = self.battle.activeSuits
            suitIndex = activeSuits.index(target)
            self.setSuitCondition(target.doId, 'missedSoak', 1, 1, 'setBoth')
            if suitIndex - 1 >= 0:
                target2 = activeSuits[suitIndex - 1]
                self.setSuitCondition(target2.doId, 'missedSoak', 1, 1, 'setBoth')
            if suitIndex + 1 < len(activeSuits):
                target3 = activeSuits[suitIndex + 1]
                self.setSuitCondition(target3.doId, 'missedSoak', 1, 1, 'setBoth')
        if not atkHit and atkTrack != HEAL:
            if atkTrack == SOUND:
                for currTarget in xrange(len(targetList)):
                    targetId = targetList[currTarget].getDoId()
                    self.__removeLured(targetId)
                    #self.setSuitCondition(targetId, 'sounded', 1, 1, 'setBoth')
                    self.setSuitCondition(targetId, 'unlureSuit', 0, 0, 'setBoth')
                return
            return
        validTargetAvail = 0
        lureDidDamage = 0
        currLureId = -1
        for currTarget in xrange(len(targetList)):
            attackLevel = -1
            attackTrack = None
            attackDamage = 0
            toonTarget = 0
            targetLured = 0
            if atkTrack == HEAL or atkTrack == PETSOS:
                targetId = targetList[currTarget]
                toonTarget = 1
            else:
                targetId = targetList[currTarget].getDoId()
            if atkTrack == LURE:
                self.currentlyImmuneSuits = self.getImmuneSuits()
                if targetId not in self.currentlyImmuneSuits:
                    if self.getSuitTrapType(targetId) == NO_TRAP:
                        if self.notify.getDebug():
                            self.notify.debug('Suit lured, but no trap exists')
                        if self.SUITS_UNLURED_IMMEDIATELY:
                            if not self.__suitIsLured(targetId, prevRound=1):
                                if not self.__combatantDead(targetId, toon=toonTarget):
                                    validTargetAvail = 1
                                theSuit = self.battle.findSuit(targetId)
                                suit = self.battle.findSuit(targetId)
                                if (theSuit.getManager() > 0) and (self.suitHasCondition(targetId, 'desperation') and not self.suitHasCondition(targetId, 'cantAttack')):
                                    rounds = 0
                                elif self.getSuitConditionTurns(targetId, 'damageReduction') == 1 and self.suitHasCondition(targetId, 'damageReduction'):
                                    rounds = 0
                                elif self.suitHasCondition(targetId, 'immune'):
                                    rounds = 0
                                elif self.suitHasCondition(targetId, 'dead'):
                                    rounds = 0
                                elif self.suitHasCondition(targetId, 'lureImmune'):
                                    rounds = 0
                                elif self.suitHasCondition(targetId, 'enraged'):
                                    rounds = 0
                                # elif self.suitHasCondition(targetId, 'brokenconnection'):
                                #     rounds = 0
                                elif self.suitHasCondition(targetId, 'bookkeeping'):
                                    rounds = 0
                                # elif (theSuit.getVirtual() > 0) and (theSuit.getManager() > 0) and not theSuit.dna.name == 'hrollers':
                                #     rounds = 0
                                # elif (theSuit.getSkeleton() > 0) and (theSuit.getManager() > 0):
                                #     rounds = 0
                                elif theSuit.dna.name == 'hroller':
                                    rounds = 0
                                elif theSuit.dna.name == 'hroller2':
                                     rounds = 0
                                elif theSuit.dna.name == 'videog':
                                     rounds = 0
                                elif theSuit.dna.name == 'bcaster':
                                     rounds = 0
                                elif theSuit.dna.name == 'fires':
                                     rounds = 0
                                elif theSuit.dna.name == 'fbed':
                                     rounds = 0
                                elif theSuit.dna.name == 'psetter':
                                     rounds = 0
                                elif theSuit.dna.name == 'mouthp':
                                     rounds = 0
                                elif theSuit.dna.name == 'rainmake':
                                     rounds = 0
                                elif theSuit.dna.name == 'bellring':
                                     rounds = 0
                                elif theSuit.dna.name == 'treek':
                                     rounds = 0
                                elif theSuit.dna.name == 'whunter':
                                     rounds = 0
                                elif theSuit.dna.name == 'wsi':
                                     rounds = 0
                                elif theSuit.dna.name == 'redd':
                                     rounds = 0
                                elif theSuit.dna.name == 'ddiver':
                                     rounds = 0
                                elif theSuit.dna.name == 'director':
                                     rounds = 0
                                elif theSuit.dna.name == 'duckshfl':
                                     rounds = 0
                                elif theSuit.dna.name == 'gatekeep':
                                     rounds = 0
                                elif (theSuit.getHP() > (theSuit.getMaxHP() * 1.5)) and suit.dna.name in ('foreman', 'supervis', 'clerk', 'wsi', 'autocad', 'ovt', 'dopa', 'dopr', 'bdirector', 'sya', 'pbl'):
                                    rounds = 0
                                elif (theSuit.getHP() > (theSuit.getMaxHP() * 1.5)) and ((theSuit.getSkeleton() or theSuit.getVirtual()) > 0):
                                    rounds = 0
                                elif self.suitHasCondition(targetId, 'lureResist') and theSuit.dna.name == 'supervis':
                                    rounds = 0
                                elif getattr(theSuit, 'chainsawOvercharged', False):
                                    rounds = min(2, self.NumRoundsLured[atkLevel])
                                elif (theSuit.getManager() > 0 or
                                      getattr(theSuit, 'chainsawManagerBeneficiary', False) or
                                      getattr(getattr(theSuit, 'dna', None), 'name', None) == 'chainsaw'):
                                    rounds = 1
                                elif theSuit.getGovernaught() > 0:
                                    rounds = 1
                                elif self.suitHasCondition(targetId, 'insured'):
                                    rounds = 1
                                elif self.suitHasCondition(targetId, 'lureResist'):
                                    rounds = 1
                                elif self.suitHasCondition(targetId, 'contracted'):
                                    rounds = 1
                                elif self.suitHasCondition(targetId, 'insured2'):
                                    rounds = 1
                                elif self.suitHasCondition(targetId, 'contracted2'):
                                    rounds = 1
                                elif len(self.getAllRelevantConditions(targetId, StatusEffects.LureResistance, toon=False)) > 0: # Check for the new Lure Resistance status effect.
                                    rounds = self.NumRoundsLured[atkLevel] # Set up the normal rounds a Cog is Lured for.

                                    # Pick the one with the lowest rounds.
                                    for effect in self.getAllRelevantConditions(targetId, StatusEffects.LureResistance, toon=False): # Sift through all existing Lure Resistance effects.
                                        if effect.maxLureRounds < rounds: # Is the effect's Lure-round limit less that that of the current rounds we want to Lure for?
                                            rounds = effect.maxLureRounds # Set it.

                                elif theSuit.getHP() > (theSuit.getMaxHP() * 1.5):
                                    rounds = 1
                                elif theSuit.getVirtual() > 0:
                                    rounds = self.NumRoundsLured[atkLevel] - 2
                                elif theSuit.getSkeleton() > 0:
                                    rounds = self.NumRoundsLured[atkLevel] - 1
                                else:
                                    rounds = self.NumRoundsLured[atkLevel]
                                chance = ToontownBattleGlobals.LureMissChance[atkLevel]
                                self.applyGagBanChecks(toonId, LURE, atkLevel)
                                self.applyToonGagUseEffects(toonId, LURE)

                                organicBonus = self.__toonCheckGagBonus(attack[TOON_ID_COL], atkTrack, atkLevel)
                                lureKBValue = ToontownBattleGlobals.AvLureKnockback[atkLevel] * 100

                                if organicBonus:
                                    lureKBValue *= 1.2

                                lureKBValue = self.applyLureKBModifiers(
                                    lureKBValue,
                                    toonId,
                                    targetId,
                                    atkLevel
                                )

                                self.applyLureHitEffects(
                                    toon,
                                    toonId,
                                    theSuit,
                                    targetId
                                )
                                if theSuit.dna.name == 'redd':
                                    self.setSuitCondition(targetId, 'lured', lureKBValue / 2, self.NumRoundsLured[atkLevel] + 1,
                                                          'setBoth')
                                    self.setSuitCondition(targetId, 'unlureSuit', 1, 10,
                                                          'setBoth')
                                elif self.suitHasCondition(targetId, 'immune'):
                                    self.setSuitCondition(targetId, 'lured', 0,
                                                          0,
                                                          'setBoth')
                                    self.setSuitCondition(targetId, 'unlureSuit', 0, 0,
                                                          'setBoth')
                                elif self.suitHasCondition(targetId, 'lureImmune'):
                                    self.setSuitCondition(targetId, 'lured', 0,
                                                          0,
                                                          'setBoth')
                                    self.setSuitCondition(targetId, 'unlureSuit', 0, 0,
                                                          'setBoth')
                                elif self.suitHasCondition(targetId, 'enraged') and self.suitHasCondition(targetId, 'desperation'):
                                    self.setSuitCondition(targetId, 'lured', 0,
                                                          0,
                                                          'setBoth')
                                    self.setSuitCondition(targetId, 'unlureSuit', 0, 0,
                                                          'setBoth')
                                else:
                                    self.setSuitCondition(targetId, 'lured', lureKBValue, self.NumRoundsLured[atkLevel] + 1,
                                                      'setBoth')
                                    self.setSuitCondition(targetId, 'unlureSuit', 1, 10,
                                                          'setBoth')
                                wakeupChance = 100 - atkAcc * 2
                                npcLurer = attack[TOON_TRACK_COL] == NPCSOS
                                if not self.suitHasCondition(targetId, 'immune') and not self.suitHasCondition(targetId, 'lureImmune') \
                                        and not (theSuit.dna.name == 'sgoat' and self.suitHasCondition(targetId, 'desperation') and self.suitHasCondition(targetId, 'enraged')):
                                    currLureId = self.__addLuredSuitInfo(targetId, -1, rounds, wakeupChance, toonId,
                                                                     atkLevel,
                                                                     lureId=currLureId, npc=npcLurer)
                                if self.notify.getDebug():
                                    self.notify.debug('Suit lured for ' + str(rounds) + ' rounds max with ' + str(
                                        wakeupChance) + '% chance to wake up each round')
                                if self.suitHasCondition(targetId, 'immune'):
                                    targetLured = 0
                                elif self.suitHasCondition(targetId, 'dead'):
                                    targetLured = 0
                                elif self.suitHasCondition(targetId, 'lureImmune'):
                                    targetLured = 0
                                elif self.suitHasCondition(targetId, 'enraged') and self.suitHasCondition(targetId, 'desperation'):
                                    targetLured = 0
                                else:
                                    targetLured = 1
                    else:
                        theSuit = self.battle.findSuit(targetId)

                        trapBlocked = (
                            self.suitHasCondition(targetId, 'immune') or
                            self.suitHasCondition(targetId, 'lureImmune') or
                            (
                                theSuit and
                                theSuit.dna.name == 'sgoat' and
                                self.suitHasCondition(targetId, 'desperation') and
                                self.suitHasCondition(targetId, 'enraged')
                            )
                        )

                        if trapBlocked:
                            attackTrack = LURE
                            attackLevel = atkLevel
                            attackDamage = 0
                            lureDidDamage = 0
                            targetLured = 0

                            self.setSuitCondition(targetId, 'lured', 0, 0, 'setBoth')
                            self.setSuitCondition(targetId, 'unlureSuit', 0, 0, 'setBoth')

                            continue

                        attackTrack = TRAP
                        if targetId in self.traps:
                            trapInfo = self.traps[targetId]
                            attackLevel = trapInfo[0]
                        else:
                            attackLevel = NO_TRAP
                        attackDamage = self.__suitTrapDamage(targetId)
                        trapCreatorId = self.__trapCreator(targetId)
                        damageOwnerId = trapCreatorId
                        if damageOwnerId <= 0:
                            damageOwnerId = toonId

                        organicBonus = False
                        if damageOwnerId > 0:
                            organicBonus = self.__toonCheckGagBonus(damageOwnerId, TRAP, attackLevel)

                        if attackDamage > 0:
                            attackDamage = self.applyToonGagDamageMultipliers(
                                attackDamage,
                                damageOwnerId,
                                targetId,
                                TRAP,
                                attackLevel,
                                organicBonus=organicBonus
                            )

                            attackDamage = self.applyCogDamageInterceptors(
                                attackDamage,
                                damageOwnerId,
                                theSuit,
                                targetId,
                                LURE
                            )
                            trapInstakillDamage = self.instakillTraps.get(targetId, 0)
                            if trapInstakillDamage:
                                attackDamage = min(trapInstakillDamage, 32767)
                        if trapCreatorId > 0:
                            self.notify.debug('Giving trap EXP to toon ' + str(trapCreatorId))
                            self.__addAttackExp(attack, track=TRAP, level=attackLevel, attackerId=trapCreatorId)
                        self.__clearTrapCreator(trapCreatorId, targetId)
                        if self.suitHasCondition(targetId, 'immune'):
                            lureDidDamage = 0
                        elif self.suitHasCondition(targetId, 'dead'):
                            lureDidDamage = 0
                        elif self.suitHasCondition(targetId, 'lureImmune'):
                            lureDidDamage = 0
                        elif (theSuit.dna.name == 'sgoat' and self.suitHasCondition(targetId, 'desperation') and self.suitHasCondition(targetId, 'enraged')):
                            lureDidDamage = 0
                        else:
                            lureDidDamage = 1
                        if self.notify.getDebug():
                            self.notify.debug(
                                'Suit lured right onto a trap! (' + str(AvProps[attackTrack][attackLevel]) + ',' + str(
                                    attackLevel) + ')')
                        if not self.__combatantDead(targetId, toon=toonTarget):
                            theSuit = self.battle.findSuit(targetId)
                           # for s in self.battle.activeSuits:
                               # if s.dna.name == 'sgoat' and self.suitHasCondition(s.doId, 'shielding'):
                                   # self.setSuitCondition(s.doId, 'rageBuilding', self.getSuitConditionModifier(s.doId, 'rageBuilding') + 10, -1, 'setBoth')
                                    #self.notify.debug('setSuitCondition() - scapegoat rage building %i' % (self.getSuitConditionModifier(s.doId, 'rageBuilding')))
                            self.setSuitCondition(targetId, 'unlureSuit', 0, 0, 'setBoth')
                            validTargetAvail = 1
                        if self.suitHasCondition(targetId, 'immune'):
                            targetLured = 0
                        elif self.suitHasCondition(targetId, 'lureImmune'):
                            targetLured = 0
                        elif (theSuit.dna.name == 'sgoat' and self.suitHasCondition(targetId, 'desperation') and self.suitHasCondition(targetId, 'enraged')):
                            targetLured = 0
                        else:
                            targetLured = 1
                if not self.SUITS_UNLURED_IMMEDIATELY:
                    if not self.__suitIsLured(targetId, prevRound=1):
                        if not self.__combatantDead(targetId, toon=toonTarget):
                            validTargetAvail = 1
                        rounds = self.NumRoundsLured[atkLevel]
                        wakeupChance = 100 - atkAcc * 2
                        npcLurer = attack[TOON_TRACK_COL] == NPCSOS
                        currLureId = self.__addLuredSuitInfo(targetId, -1, rounds, wakeupChance, toonId, atkLevel,
                                                                 lureId=currLureId, npc=npcLurer)
                        if self.notify.getDebug():
                            self.notify.debug('Suit lured for ' + str(rounds) + ' rounds max with ' + str(
                                wakeupChance) + '% chance to wake up each round')
                        if self.suitHasCondition(targetId, 'immune'):
                            targetLured = 0
                        elif self.suitHasCondition(targetId, 'dead'):
                            targetLured = 0
                        elif self.suitHasCondition(targetId, 'lureImmune'):
                            targetLured = 0
                        elif (theSuit.dna.name == 'sgoat' and self.suitHasCondition(targetId, 'desperation') and self.suitHasCondition(targetId, 'enraged')):
                            targetLured = 0
                        else:
                            targetLured = 1
                    if attackLevel != -1 and targetLured:
                        self.__addLuredSuitsDelayed(toonId, targetId)
                if targetLured and (targetId not in self.successfulLures or targetId in self.successfulLures and
                                    self.successfulLures[targetId][1] < atkLevel):
                    self.notify.debug('Adding target ' + str(targetId) + ' to successfulLures list')
                    self.successfulLures[targetId] = [
                        toonId, atkLevel, atkAcc, -1]
            else:
                if atkTrack == TRAP:
                    npcDamage = 0
                    if attack[TOON_TRACK_COL] == NPCSOS:
                        npcDamage = atkHp
                    if self.CLEAR_MULTIPLE_TRAPS:
                        if self.getSuitTrapType(targetId) != NO_TRAP:
                            self.__clearAttack(toonId)
                            return
                    else:
                        self.__addSuitTrap(targetId, atkLevel, toonId, npcDamage)
                elif self.__suitIsLured(targetId) and atkTrack == SOUND:
                    tgtPos = self.battle.activeSuits.index(targetList[currTarget])
                    attack[TOON_KBBONUS_COL][tgtPos] = self.KBBONUS_LURED_FLAG
                attackLevel = atkLevel
                attackTrack = atkTrack
                toon = self.battle.getToon(toonId)
                if attack[TOON_TRACK_COL] == NPCSOS and lureDidDamage != 1 or attack[TOON_TRACK_COL] == PETSOS:
                    attackDamage = atkHp
                elif atkTrack == FIRE:
                    suit = self.battle.findSuit(targetId)
                    managerFireImmune = False
                    if suit:
                        managerFireImmune = bool(
                            suit.getManager() or
                            getattr(suit, 'chainsawManagerBeneficiary', False) or
                            getattr(suit, 'chainsawOvercharged', False) or
                            getattr(getattr(suit, 'dna', None), 'name', None) == 'chainsaw')
                        if managerFireImmune:
                            attackDamage = 0
                        elif suit.getGovernaught():
                            attackDamage = 0
                        elif suit.currHP > (suit.maxHP * 1.5):
                            attackDamage = 0
                        elif self.suitHasCondition(targetId, 'insured'):
                            attackDamage = 0
                        elif self.suitHasCondition(targetId, 'contracted'):
                            attackDamage = 0
                        elif self.suitHasCondition(targetId, 'insured2'):
                            attackDamage = 0
                        elif self.suitHasCondition(targetId, 'contracted2'):
                            attackDamage = 0
                        else:
                            costToFire = math.ceil(suit.getActualLevel() / 3)
                            abilityToFire = toon.getPinkSlips()
                            toon.removePinkSlips(costToFire)
                            if costToFire > abilityToFire:
                                commentStr = 'Toon attempting to fire a %s cost cog with %s pinkslips' % (
                                costToFire, abilityToFire)
                                simbase.air.writeServerEvent('suspicious', toonId, commentStr)
                                dislId = toon.DISLid
                                simbase.air.banManager.ban(toonId, dislId, commentStr)
                                print
                                'Not enough PinkSlips to fire cog - print a warning here'
                            else:
                                suit.skeleRevives = 0
                                attackDamage = suit.getHP()
                    else:
                        attackDamage = 0
                    self.setToonCondition(toon.doId, 'noSOS', 1, 3, 'setBoth')
                    self.setToonCondition(toon.doId, 'noFires', 1, 3, 'setBoth')
                    # self.setToonCondition(toon.doId, 'noUnites', 1, 3, 'setBoth')
                    self.setToonCondition(toon.doId, 'noSues', 1, 3, 'setBoth')
                    if not managerFireImmune:
                        self.setSuitCondition(targetId, 'dead', 1, 2, 'setBoth')
                    bonus = 0
                elif atkTrack == SUE:
                    suit = self.battle.findSuit(targetId)
                    if suit:
                        if (suit.getManager() or
                                getattr(suit, 'chainsawManagerBeneficiary', False) or
                                getattr(suit, 'chainsawOvercharged', False) or
                                getattr(getattr(suit, 'dna', None), 'name', None) == 'chainsaw'):
                            attackDamage = 0
                        elif suit.getGovernaught():
                            attackDamage = 0
                        elif suit.currHP > (suit.maxHP * 1.5):
                            attackDamage = 0
                        elif self.suitHasCondition(targetId, 'insured'):
                            attackDamage = 0
                        elif self.suitHasCondition(targetId, 'contracted'):
                            attackDamage = 0
                        elif self.suitHasCondition(targetId, 'insured2'):
                            attackDamage = 0
                        elif self.suitHasCondition(targetId, 'contracted2'):
                            attackDamage = 0
                        else:
                            costToSue = math.ceil(suit.getActualLevel() / 4)
                            abilityToSue = toon.getCeaseAndDesists()
                            toon.removeCeaseAndDesists(costToSue)
                            if costToSue > abilityToSue:
                                commentStr = 'Toon attempting to sue a %s cost cog with %s C&Ds' % (costToSue, abilityToSue)
                                simbase.air.writeServerEvent('suspicious', toonId, commentStr)
                                dislId = toon.DISLid
                                simbase.air.banManager.ban(toonId, dislId, commentStr)
                                print 'Not enough Cease & Desists to sue cog - print a warning here'
                            else:
                                self.setSuitCondition(targetId, 'sued', 1, 4, 'setBoth')
                                suit.setHP(suit.currHP + 1)
                                attackDamage = 1
                elif atkTrack == HEAL:
                    if self.toonUsedBannedGag(toonId, atkTrack, attackLevel):
                        self.setToonCondition(toon.doId, 'banned', 1, 1, 'setBoth')
                    if self.toonHasCondition(toon.doId, 'nolevel8s') and attackLevel == 7:
                        for suit in self.battle.activeSuits:
                            self.setSuitCondition(suit.doId, 'bannedGagUsed', 1, 1, 'setBoth')
                        self.setToonCondition(toon.doId, 'banned', 1, 1, 'setBoth')
                    if self.toonHasCondition(toon.doId, 'nolevel7s') and attackLevel == 6:
                        for suit in self.battle.activeSuits:
                            self.setSuitCondition(suit.doId, 'bannedGagUsed', 1, 1, 'setBoth')
                        self.setToonCondition(toon.doId, 'banned', 1, 1, 'setBoth')
                    if self.toonHasCondition(toon.doId, 'nolevel6s') and attackLevel == 5:
                        for suit in self.battle.activeSuits:
                            self.setSuitCondition(suit.doId, 'bannedGagUsed', 1, 1, 'setBoth')
                        self.setToonCondition(toon.doId, 'banned', 1, 1, 'setBoth')
                    if self.toonHasCondition(toon.doId, 'nolevel5s') and attackLevel == 4:
                        for suit in self.battle.activeSuits:
                            self.setSuitCondition(suit.doId, 'bannedGagUsed', 1, 1, 'setBoth')
                        self.setToonCondition(toon.doId, 'banned', 1, 1, 'setBoth')
                    if self.toonHasCondition(toon.doId, 'nolevel4s') and attackLevel == 3:
                        for suit in self.battle.activeSuits:
                            self.setSuitCondition(suit.doId, 'bannedGagUsed', 1, 1, 'setBoth')
                        self.setToonCondition(toon.doId, 'banned', 1, 1, 'setBoth')
                    if self.toonHasCondition(toon.doId, 'noToonUpGags'):
                        for suit in self.battle.activeSuits:
                            self.setSuitCondition(suit.doId, 'bannedGagUsed', 1, 1, 'setBoth')
                        self.setToonCondition(toon.doId, 'banned2', 1, 1, 'setBoth')
                    if self.toonHasCondition(toon.doId, 'noGags'):
                        for suit in self.battle.activeSuits:
                            self.setSuitCondition(suit.doId, 'bannedGagUsed', 1, 1, 'setBoth')
                        self.setToonCondition(toon.doId, 'banned3', 1, 1, 'setBoth')
                    attackDamage = getAvPropDamage(attackTrack, attackLevel, toon.experience.getExp(attackTrack))
                    organicBonus = self.__toonCheckGagBonus(attack[TOON_ID_COL], atkTrack, atkLevel)
                    if organicBonus:
                        self.setToonCondition(targetId, 'cheer', attackDamage * .5, 2, 'setBoth')
                    else:
                        self.setToonCondition(targetId, 'cheer', attackDamage* .5, 1, 'setBoth')
                    if self.toonHasCondition(toonId, 'healBoost'):
                        attackDamage *= (1.0 + self.getToonConditionModifier(toonId, 'healBoost') * 0.01)
                    if self.toonHasCondition(toonId, 'encore'):
                        attackDamage *= 1.2
                    if self.toonHasCondition(toonId, 'encore2'):
                        attackDamage *= 1.1
                    if self.toonHasCondition(toonId, 'viralSensation'):
                        attackDamage *= (1.0 + self.getToonConditionModifier(toonId, 'viralSensation') * 0.01)
                    if self.toonHasCondition(toonId, 'energized'):
                        attackDamage *= (1.0 + self.getToonConditionModifier(toonId, 'energized') * 0.01)
                    if self.toonHasCondition(toonId, 'allGagBoost'):
                        attackDamage *= (1.0 + (self.getToonConditionModifier(toonId, 'allGagBoost') * 0.01))
                    if self.toonHasCondition(toonId, 'allGagBoost2'):
                        attackDamage *= (1.0 + (self.getToonConditionModifier(toonId, 'allGagBoost2') * 0.01))
                    if self.toonHasCondition(toonId, 'raisedAnte'):
                        attackDamage *= (1.0 + (self.getToonConditionModifier(toonId, 'raisedAnte') * 0.01))
                    if self.toonHasCondition(toonId, 'governaughtBoost'):
                        attackDamage *= (1.0 + self.getToonConditionModifier(toonId, 'governaughtBoost') * 0.01)
                    if self.toonHasCondition(toonId, 'groupDamageDown') and atkLevel in (1, 3, 5, 7):
                        attackDamage *= 0.5
                elif atkTrack == SQUIRT:
                    self.applyGagBanChecks(toonId, SQUIRT, atkLevel)

                    suit = self.battle.findSuit(targetId)
                    organicBonus = self.__toonCheckGagBonus(attack[TOON_ID_COL], atkTrack, atkLevel)

                    activeSuits = self.battle.activeSuits
                    suitIndex = activeSuits.index(suit)

                    baseDamage = getAvPropDamage(
                        attackTrack,
                        attackLevel,
                        toon.experience.getExp(attackTrack)
                    )

                    # Main target.
                    attackDamage = self.calculateSquirtTargetDamage(
                        baseDamage,
                        toon,
                        toonId,
                        suit,
                        targetId,
                        atkLevel,
                        organicBonus,
                        splashMult=1.0
                    )

                    if atkHit and attackDamage > 0:
                        self.applyToonGagUseEffects(toonId, SQUIRT)
                        self.applyCogHitEffects(toon, toonId, suit, targetId, SQUIRT, atkLevel, attackDamage)

                    # Left splash.
                    if suitIndex - 1 >= 0:
                        splashSuit = activeSuits[suitIndex - 1]
                        splashDamage = self.calculateSquirtTargetDamage(
                            baseDamage,
                            toon,
                            toonId,
                            splashSuit,
                            splashSuit.doId,
                            atkLevel,
                            organicBonus,
                            splashMult=0.5
                        )

                        if atkHit and splashDamage > 0:
                            self.applyCogHitEffects(toon, toonId, splashSuit, splashSuit.doId, SQUIRT, atkLevel, splashDamage, unLureSuit=False)

                        # You need to assign this wherever your calculator stores splash HP.
                        # Example only:
                        # attack[SUIT_HP_COL][indexOfSplashSuit] = splashDamage

                    # Right splash.
                    if suitIndex + 1 < len(activeSuits):
                        splashSuit = activeSuits[suitIndex + 1]
                        splashDamage = self.calculateSquirtTargetDamage(
                            baseDamage,
                            toon,
                            toonId,
                            splashSuit,
                            splashSuit.doId,
                            atkLevel,
                            organicBonus,
                            splashMult=0.5
                        )

                        if atkHit and splashDamage > 0:
                            self.applyCogHitEffects(toon, toonId, splashSuit, splashSuit.doId, SQUIRT, atkLevel, splashDamage, unLureSuit=False)

                        # Example only:
                        # attack[SUIT_HP_COL][indexOfSplashSuit] = splashDamage
                elif atkTrack == THROW:
                    self.applyGagBanChecks(toonId, THROW, atkLevel)

                    suit = self.battle.findSuit(targetId)
                    organicBonus = self.__toonCheckGagBonus(attack[TOON_ID_COL], atkTrack, atkLevel)

                    attackDamage = getAvPropDamage(
                        attackTrack,
                        attackLevel,
                        toon.experience.getExp(attackTrack)
                    )

                    if attackDamage > 0:
                        attackDamage = self.applyToonGagDamageMultipliers(
                            attackDamage,
                            toonId,
                            targetId,
                            THROW,
                            atkLevel,
                            organicBonus=organicBonus
                        )

                        attackDamage = self.applyCogDamageInterceptors(
                            attackDamage,
                            toonId,
                            suit,
                            targetId,
                            THROW
                        )

                    if atkHit and attackDamage > 0:
                        if self.suitHasCondition(targetId, 'sued'):
                            self.setSuitCondition(targetId, 'sued', 1, 4, 'alternateBoth')

                        self.applyToonGagUseEffects(toonId, THROW)

                        self.applyThrowMarkEffects(
                            toon,
                            toonId,
                            targetId,
                            THROW,
                            atkLevel
                        )

                        self.applyCogHitEffects(
                            toon,
                            toonId,
                            suit,
                            targetId,
                            THROW,
                            atkLevel,
                            attackDamage
                        )

                    target = self.battle.findSuit(attack[TOON_TGT_COL])
                elif atkTrack == SOUND:
                    self.applyGagBanChecks(toonId, SOUND, atkLevel)
                    suit = self.battle.findSuit(targetId)
                    organicBonus = self.__toonCheckGagBonus(attack[TOON_ID_COL], atkTrack, atkLevel)

                    attackDamage = getAvPropDamage(
                        attackTrack,
                        attackLevel,
                        toon.experience.getExp(attackTrack)
                    )

                    if attackDamage > 0:
                        attackDamage = self.applyToonGagDamageMultipliers(
                            attackDamage,
                            toonId,
                            targetId,
                            SOUND,
                            atkLevel,
                            organicBonus=organicBonus
                        )

                        attackDamage = self.applyCogDamageInterceptors(
                            attackDamage,
                            toonId,
                            suit,
                            targetId,
                            SOUND
                        )
                    if atkHit and attackDamage > 0:
                        self.applySoundEncoreChecks(toonId, SOUND, atkLevel)
                        if self.suitHasCondition(targetId, 'sued'):
                            self.setSuitCondition(targetId, 'sued', 1, 4, 'alternateBoth')

                        self.applySoundHitEffects(
                            toon,
                            toonId,
                            suit,
                            targetId,
                            atkLevel,
                            attackDamage
                        )

                        self.applyCogHitEffects(
                            toon,
                            toonId,
                            suit,
                            targetId,
                            SOUND,
                            atkLevel,
                            attackDamage
                        )

                    target = self.battle.findSuit(attack[TOON_TGT_COL])
                elif atkTrack == DROP:
                    self.applyGagBanChecks(toonId, DROP, atkLevel)

                    suit = self.battle.findSuit(targetId)
                    organicBonus = self.__toonCheckGagBonus(attack[TOON_ID_COL], atkTrack, atkLevel)

                    chance = ToontownBattleGlobals.DropMissChance[atkLevel]

                    attackDamage = getAvPropDamage(
                        attackTrack,
                        attackLevel,
                        toon.experience.getExp(attackTrack)
                    )
                    if self.suitHasCondition(targetId, 'dropRushJob'):
                        chance -= 40

                    modifiers = [
                        ((self.suitHasCondition(targetId, 'soaked') or self.suitHasCondition(targetId, 'drenched')), 15),
                        (self.suitHasCondition(targetId, 'dazed'), 15),
                        (self.suitHasCondition(targetId, 'zapped'), 15),
                        (self.toonHasCondition(toonId, 'cheer'), 5),
                        (self.suitHasCondition(targetId, 'marked'), 15),
                    ]

                    totalReduction = sum(val for cond, val in modifiers if cond)

                    chance = max(chance - totalReduction, 4)

                    roll = random.randint(0, 99)
                    if roll <= chance:
                        self.notify.debug('DROP missed: rolled %s against miss chance %s' % (roll, chance))
                        attackDamage = 0
                    elif self.suitHasCondition(targetId, 'unlureSuit'):
                        attackDamage = 0
                    else:
                        self.notify.debug('DROP hit: rolled %s against miss chance %s' % (roll, chance))

                    if attackDamage > 0:
                        attackDamage = self.applyToonGagDamageMultipliers(
                            attackDamage,
                            toonId,
                            targetId,
                            DROP,
                            atkLevel,
                            organicBonus=organicBonus
                        )

                        attackDamage = self.applyCogDamageInterceptors(
                            attackDamage,
                            toonId,
                            suit,
                            targetId,
                            DROP
                        )

                    if atkHit and attackDamage > 0:
                        self.applyCogHitEffects(
                            toon,
                            toonId,
                            suit,
                            targetId,
                            DROP,
                            atkLevel,
                            attackDamage
                        )

                    target = self.battle.findSuit(attack[TOON_TGT_COL])
                elif atkTrack == ZAP:
                    self.applyGagBanChecks(toonId, ZAP, atkLevel)

                    suit = self.battle.findSuit(targetId)

                    attackDamage = getAvPropDamage(
                        attackTrack,
                        attackLevel,
                        toon.experience.getExp(attackTrack)
                    )

                    # ZAP-specific conductivity rules.
                    if self.suitHasCondition(targetId, 'oilRain'):
                        attackDamage = 0

                    elif self.suitHasCondition(targetId, 'immune'):
                        attackDamage = 0

                    elif self.suitHasCondition(targetId, 'dead'):
                        attackDamage = 0

                    elif self.suitHasCondition(targetId, 'zapImmune'):
                        attackDamage = 0

                    elif not (self.suitHasCondition(targetId, 'soaked') or self.suitHasCondition(targetId, 'drenched')):
                        if self.suitHasCondition(targetId, 'missedSoak'):
                            attackDamage *= 0.25
                        else:
                            attackDamage = 0

                    if attackDamage > 0:
                        attackDamage = self.applyToonGagDamageMultipliers(
                            attackDamage,
                            toonId,
                            targetId,
                            ZAP,
                            atkLevel,
                            organicBonus=False
                        )

                        attackDamage = self.applyCogDamageInterceptors(
                            attackDamage,
                            toonId,
                            suit,
                            targetId,
                            ZAP
                        )

                    if atkHit and attackDamage > 0:
                        self.applyCogHitEffects(
                            toon,
                            toonId,
                            suit,
                            targetId,
                            ZAP,
                            atkLevel,
                            attackDamage
                        )

                    target = self.battle.findSuit(attack[TOON_TGT_COL])
                    activeSuits = self.battle.activeSuits
                    target = self.battle.findSuit(targetId)
                    suitIndex = activeSuits.index(target)
                    organicBonus = self.__toonCheckGagBonus(attack[TOON_ID_COL], atkTrack, atkLevel)
                    if attackDamage > 0:
                        self.setToonCondition(toonId, 'zapToon', 1, 1, 'setBoth')
                        if organicBonus:
                            if self.suitHasCondition(targetId, 'soaked') or self.suitHasCondition(targetId, 'missedSoak') or self.suitHasCondition(targetId, 'drenched'):
                                self.setSuitCondition(targetId, 'zapped', self.getSuitConditionModifier(targetId, 'zapped') + math.ceil(attackDamage / 2), 2, 'setBoth')
                        else:
                            if self.suitHasCondition(targetId, 'soaked') or self.suitHasCondition(targetId, 'missedSoak') or self.suitHasCondition(targetId, 'drenched'):
                                self.setSuitCondition(targetId, 'zapped', self.getSuitConditionModifier(targetId, 'zapped') + math.ceil(attackDamage / 4), 2, 'setBoth')
                        if self.suitHasCondition(targetId, 'soaked'):
                            self.setSuitCondition(targetId, 'soaked', 1, 1, 'setBoth')
                        if target.dna.name == 'dking':
                            self.setSuitCondition(targetId, 'zappedcalculator', 1, 1, 'setBoth')
                        if self.suitHasCondition(targetId, 'missedSoak'):
                            self.setSuitCondition(targetId, 'missedSoak', 1, 1, 'setBoth')
                        self.__removeLured(targetId)
                else:
                    if not atkTrack == ZAP:
                        attackDamage = getAvPropDamage(attackTrack, attackLevel, toon.experience.getExp(attackTrack))
                suit = self.battle.findSuit(targetId)
                # if atkTrack in (THROW, SOUND, DROP):
                #     if atkHit and attackDamage > 0:
                #         if suit.dna.name == 'racket' and self.racketeerMultiplier > 0:
                #             self.racketeerMultiplier -= 1

                #         organicBonus = self.__toonCheckGagBonus(
                #             attack[TOON_ID_COL],
                #             atkTrack,
                #             atkLevel
                #         )

                #         attackDamage = self.applyToonGagDamageMultipliers(
                #             attackDamage,
                #             toonId,
                #             targetId,
                #             atkTrack,
                #             atkLevel,
                #             organicBonus=organicBonus
                #         )

                #         attackDamage = self.applyCogDamageInterceptors(
                #             attackDamage,
                #             toonId,
                #             suit,
                #             targetId,
                #             atkTrack
                #         )

                #         if attackDamage > 0:
                #             self.applyCogHitEffects(
                #                 toon,
                #                 toonId,
                #                 suit,
                #                 targetId,
                #                 atkTrack,
                #                 atkLevel,
                #                 attackDamage
                #             )
                attackDamage = math.ceil(attackDamage)
                if atkTrack == TRAP:
                    for suit in self.battle.activeSuits:
                        if suit.dna.name == 'hrollers' and suit.getActualLevel() == 29:
                            self.setSuitCondition(suit.doId, 'barcalculator', 1, 1, 'setBoth')
                if atkHit:
                    self.applyToonGagUseEffects(toonId, atkTrack)
                if not self.__combatantDead(targetId, toon=toonTarget):
                    validTargetAvail = 1
            if attackLevel == -1 and not atkTrack == FIRE and not atkTrack == SUE:
                if self.suitHasCondition(targetId, 'immune'):
                    result = 0
                elif self.suitHasCondition(targetId, 'enraged') and self.suitHasCondition(targetId, 'desperation'):
                    result = 0
                elif self.suitHasCondition(targetId, 'lureImmune'):
                    result = 0
                else:
                    result = LURE_SUCCEEDED
            elif atkTrack != TRAP:
                result = attackDamage
                if atkTrack == HEAL:
                    if not self.__attackHasHit(attack, suit=0):
                        result = result * 0.2
                # else:
                #     if self.suitHasCondition(targetId, 'unlureSuit') and atkTrack == DROP:
                #         result = 0
            else:
                result = 0
            instakillDamage = self.__getInstakillDamage(toonId)
            if instakillDamage and result > 0 and atkTrack in (SOUND, THROW, SQUIRT, ZAP, DROP):
                result = min(instakillDamage, 32767)
            if result != 0 or atkTrack == PETSOS:
                targets = self.__getToonTargets(attack)
                if targetList[currTarget] not in targets:
                    if self.notify.getDebug():
                        self.notify.debug('Target of toon is not accessible!')
                    continue
                targetIndex = targets.index(targetList[currTarget])
                if atkTrack == HEAL:
                    organicBonus = self.__toonCheckGagBonus(attack[TOON_ID_COL], atkTrack, atkLevel)
                    result = result / len(targetList)
                    toon = self.battle.getToon(toonId)
                    if organicBonus:
                        toon.setHp(toon.hp + math.ceil((attackDamage * .45)))
                       # self.toonHPAdjusts[attack[TOON_ID_COL]] += math.ceil((attackDamage * .25))
                       # toon.setHp(toon.hp + math.ceil((attackDamage * .25)))
                       # toon.toonUp(math.ceil((attackDamage / 5)))
                    else:
                        toon.setHp(toon.hp + math.ceil((attackDamage * .25)))
                       # self.toonHPAdjusts[attack[TOON_ID_COL]] += math.ceil((attackDamage * .2))
                if atkTrack == THROW:
                    organicBonus = self.__toonCheckGagBonus(attack[TOON_ID_COL], atkTrack, atkLevel)
                    result = result / len(targetList)
                    toon = self.battle.getToon(toonId)
                    if organicBonus:
                        toon.setHp(toon.hp + math.ceil((attackDamage * .25)))
                       # toon.toonUp(math.ceil((attackDamage / 5)))
                    else:
                        toon.setHp(toon.hp + math.ceil((attackDamage * .2)))
                if targetId in self.successfulLures and atkTrack == LURE:
                    if lureDidDamage:
                        if self.suitHasCondition(targetId, 'dazed2'):
                            suit = self.battle.findSuit(targetId)
                          #  if suit.dna.name == 'tcm':
                             #   self.setSuitCondition(targetId, 'trapcalculator', 1, 10, 'setBoth')
                            self.setSuitCondition(targetId, 'dazed', 1, 2, 'setBoth')
                            self.setSuitCondition(targetId, 'dazed2', 0, 0, 'setBoth')
                            if suit.dna.name == 'radiog' and not self.suitHasCondition(targetId, 'dazed'):
                                self.setSuitCondition(targetId, 'dazedcalculator', 1, 10, 'setBoth')
                                self.setSuitCondition(targetId, 'dazedcalculator2', 0, 0, 'setBoth')
                            if suit.dna.name == 'liquid' and not self.suitHasCondition(targetId, 'dazed'):
                                self.setSuitCondition(targetId, 'dazedcalculator', 1, 10, 'setBoth')
                                self.setSuitCondition(targetId, 'dazedcalculator2', 0, 0, 'setBoth')
                    self.successfulLures[targetId][3] = result
                else:
                    attack[TOON_HP_COL][targetIndex] = result
                if result > 0 and atkTrack != HEAL and atkTrack != DROP and atkTrack != PETSOS:
                    attackTrack = LURE
                    lureInfos = self.__getLuredExpInfo(targetId)
                    for currInfo in lureInfos:
                        if currInfo[3]:
                            self.__addAttackExp(attack, track=attackTrack, level=currInfo[1], attackerId=currInfo[0])
                        self.__clearLurer(currInfo[0], lureId=currInfo[2])

        if lureDidDamage:
            if self.itemIsCredit(atkTrack, atkLevel):
                self.__addAttackExp(attack)
        if not validTargetAvail and self.__prevAtkTrack(toonId) != atkTrack:
            self.__clearAttack(toonId)
        return

    def __getToonTargets(self, attack):
        track = self.__getActualTrack(attack)
        if track == HEAL or track == PETSOS:
            return self.battle.activeToons
        else:
            return self.battle.activeSuits

    def __attackHasHit(self, attack, suit = 0):
        if suit == 1:
            for dmg in attack[SUIT_HP_COL]:
                if dmg > 0:
                    return 1

            return 0
        else:
            track = self.__getActualTrack(attack)
            return not attack[TOON_ACCBONUS_COL] and track != NO_ATTACK

    def __attackDamage(self, attack, suit = 0):
        if suit:
            for dmg in attack[SUIT_HP_COL]:
                if dmg > 0:
                    return dmg

            return 0
        else:
            for dmg in attack[TOON_HP_COL]:
                if dmg > 0:
                    return dmg

            return 0

    def __addEnragedSuitInfo(self, suitId, currRounds, maxRounds, decreasedDef = False):
        self.currentlyEnragedSuits[suitId] = [currRounds, maxRounds, decreasedDef,]

    def __isEnraged(self, suit):
        if suit in self.currentlyEnragedSuits:
            return True
        else:
            return False
    def __addAbsorbingSuitInfo(self, suitId, currRounds, maxRounds, decreasedDef = False):
        self.currentlyAbsorbingSuits[suitId] = [currRounds, maxRounds, decreasedDef,]

    def __isAbsorbing(self, suit):
        if suit in self.currentlyAbsorbingSuits:
            return True
        else:
            return False

    def __addWetSuitInfo(self, suitId, currRounds, maxRounds, decreasedDef = False):
        self.currentlyWetSuits[suitId] = [currRounds, maxRounds, decreasedDef,]

    def __isWet(self, suit):
        if suit in self.currentlyWetSuits:
            return True
        else:
            return False

    def __isRaining(self, toon):
        if simbase.air.isRaining == True and self.checkIfStreetZone(toon):
            return True
        else:
            return False

    def checkIfStreetZone(self, toon):
        try:
            if ZoneUtil.getWhereName(toon.zoneId, True) == 'street' and not ZoneUtil.isDynamicZone(toon.zoneId):
                return True
            else:
                return False
        except:
            return False

    def __attackDamageForTgt(self, attack, tgtPos, suit = 0):
        if suit:
            return attack[SUIT_HP_COL][tgtPos]
        else:
            return attack[TOON_HP_COL][tgtPos]

    def getSilhouetteSpawns(self, amount=6):
        fullPool = ['sil1', 'sil2', 'sil3', 'sil4', 'sil5',
                    'sil6', 'sil7', 'sil8', 'sil9', 'sil10', 'sil11', 'sil12']

        if not hasattr(self, 'silhouetteSpawns') or self.silhouetteSpawns is None:
            self.silhouetteSpawns = fullPool[:]

        selected = []

        while len(selected) < amount:
            if not self.silhouetteSpawns:
                self.silhouetteSpawns = fullPool[:]

            suitName = random.choice(self.silhouetteSpawns)
            self.silhouetteSpawns.remove(suitName)
            selected.append(suitName)

        return selected

    def __calcToonAccBonus(self, attackKey):
        numPrevHits = 0
        attackIdx = self.toonAtkOrder.index(attackKey)
        for currPrevAtk in xrange(attackIdx - 1, -1, -1):
            attack = self.battle.toonAttacks[attackKey]
            atkTrack, atkLevel = self.__getActualTrackLevel(attack)
            prevAttackKey = self.toonAtkOrder[currPrevAtk]
            prevAttack = self.battle.toonAttacks[prevAttackKey]
            prvAtkTrack, prvAtkLevel = self.__getActualTrackLevel(prevAttack)
            if self.__attackHasHit(prevAttack) and (attackAffectsGroup(prvAtkTrack, prvAtkLevel, prevAttack[TOON_TRACK_COL]) or attackAffectsGroup(atkTrack, atkLevel, attack[TOON_TRACK_COL]) or attack[TOON_TGT_COL] == prevAttack[TOON_TGT_COL]) and atkTrack != prvAtkTrack:
                numPrevHits += 1

        if numPrevHits > 0 and self.notify.getDebug():
            self.notify.debug('ACC BONUS: toon attack received accuracy ' + 'bonus of ' + str(AccuracyBonuses[numPrevHits]) + ' from previous attack by (' + str(attack[TOON_ID_COL]) + ') which hit')
        return AccuracyBonuses[numPrevHits]

    def __getRandomValidTargetSuitDigitPresident(self, excludeSuitId=None):
        validTargets = []

        for index, suit in enumerate(self.battle.activeSuits):
            if suit is None:
                continue

            if excludeSuitId is not None and suit.doId == excludeSuitId:
                continue

            if suit.getHP() <= 0:
                continue

            if suit.getSkeleRevives() > 0:
                continue

            if not self.suitHasCondition(suit.doId, 'unlureSuit'):
                continue

            validTargets.append(index)

        if not validTargets:
            return -1

        return random.choice(validTargets)

    def __getRandomValidTargetSuitDigitRushJob(self, excludeSuitId=None):
        validTargets = []

        for index, suit in enumerate(self.battle.activeSuits):
            if suit is None:
                continue

            if excludeSuitId is not None and suit.doId == excludeSuitId:
                continue

            if suit.getHP() <= 0:
                continue

            rushJobConditions = (
                'trapRushJob',
                'lureRushJob',
                'throwRushJob',
                'squirtRushJob',
                'zapRushJob',
                'soundRushJob',
                'dropRushJob',
            )

            if any(self.suitHasCondition(suit.doId, cond)
                    for cond in rushJobConditions):
                continue

            validTargets.append(index)

        if not validTargets:
            return -1

        return random.choice(validTargets)

    def __getRandomValidTargetSuitDigitAttorney(self, excludeSuitId=None):
        validTargets = []

        for index, suit in enumerate(self.battle.activeSuits):
            if suit is None:
                continue

            if excludeSuitId is not None and suit.doId == excludeSuitId:
                continue

            if suit.getHP() <= 0:
                continue

            validTargets.append(index)

        if not validTargets:
            return -1

        return random.choice(validTargets)

    def __getRandomValidTargetSuitDigitErclaim(self, excludeSuitId=None):
        validTargets = []

        for index, suit in enumerate(self.battle.activeSuits):
            if suit is None:
                continue

            if excludeSuitId is not None and suit.doId == excludeSuitId:
                continue

            if suit.getHP() <= 0:
                continue

            if suit.getManager():
                continue

            validTargets.append(index)

        if not validTargets:
            return -1

        return random.choice(validTargets)

    def __getRandomValidTargetSuitDigitVideographer(self, excludeSuitId=None):
        validTargets = []

        for index, suit in enumerate(self.battle.activeSuits):
            if suit is None:
                continue

            if excludeSuitId is not None and suit.doId == excludeSuitId:
                continue

            if suit.getHP() <= 0:
                continue

            if suit.getManager():
                continue

            validTargets.append(index)

        if not validTargets:
            return -1

        return random.choice(validTargets)

    def __getRandomValidTargetSuitDigitRadiographer(self, excludeSuitId=None):
        validTargets = []

        for index, suit in enumerate(self.battle.activeSuits):
            if suit is None:
                continue

            if excludeSuitId is not None and suit.doId == excludeSuitId:
                continue

            if suit.getHP() <= 0:
                continue

            if suit.getManager():
                continue

            if suit.getSkeleRevives() > 0:
                continue

            if not self.suitHasCondition(suit.doId, 'unlureSuit'):
                continue

            validTargets.append(index)

        if not validTargets:
            return -1

        return random.choice(validTargets)

    def __getErfitTargetByHPPercent(self, excludeSuitId=None, mode='lowest'):
        def getValidTargets(allowSelf=False):
            validTargets = []

            for index, suit in enumerate(self.battle.activeSuits):
                if suit is None:
                    continue

                if not allowSelf and excludeSuitId is not None and suit.doId == excludeSuitId:
                    continue

                if suit.getHP() <= 0:
                    continue

                if suit.getHP() >= (suit.getMaxHP() * 2.0):
                    continue

                hpPercent = float(suit.getHP()) / float(suit.getMaxHP())
                validTargets.append((index, hpPercent))

            return validTargets

        validTargets = getValidTargets(allowSelf=False)

        if not validTargets:
            validTargets = getValidTargets(allowSelf=True)

        if not validTargets:
            return -1

        if mode == 'highest':
            return max(validTargets, key=lambda x: x[1])[0]

        return min(validTargets, key=lambda x: x[1])[0]

    def __getErfitTargetByHPPercentSacrifice(self, excludeSuitId=None, mode='lowest'):
        def getValidTargets(allowSelf=False):
            validTargets = []

            for index, suit in enumerate(self.battle.activeSuits):
                if suit is None:
                    continue

                if excludeSuitId is not None and suit.doId == excludeSuitId:
                    continue

                if suit.getHP() <= 0:
                    continue

                if suit.getManager():
                    continue

                hpPercent = float(suit.getHP()) / float(suit.getMaxHP())
                validTargets.append((index, hpPercent))

            return validTargets

        validTargets = getValidTargets(allowSelf=False)

        if not validTargets:
            validTargets = getValidTargets(allowSelf=True)

        if not validTargets:
            return -1

        if mode == 'highest':
            return max(validTargets, key=lambda x: x[1])[0]

        return min(validTargets, key=lambda x: x[1])[0]

    def __getRandomValidTargetSuitDigit(self, excludeSuitId=None):
        validTargets = []

        for index, suit in enumerate(self.battle.activeSuits):
            if suit is None:
                continue

            if excludeSuitId is not None and suit.doId == excludeSuitId:
                continue

            if suit.getHP() <= 0:
                continue

            if suit.getManager():
                continue

            if suit.getGovernaught():
                continue

            if suit.getSkeleRevives() > 0:
                continue

            if self.suitHasCondition(suit.doId, 'shielding'):
                continue

            if self.suitHasCondition(suit.doId, 'overpressure'):
                continue

            if self.suitHasCondition(suit.doId, 'insured'):
                continue

            if self.suitHasCondition(suit.doId, 'insured2'):
                continue

            if suit.getHP() > (suit.getMaxHP() * 1.5):
                continue

            validTargets.append(index)

        if not validTargets:
            return -1

        return random.choice(validTargets)

    def __applyToonAttackDamages(self, toonId, hpbonus = 0, kbbonus = 0):
        totalDamages = 0
        if not APPLY_HEALTH_ADJUSTMENTS:
            return totalDamages
        attack = self.battle.toonAttacks[toonId]
        track = self.__getActualTrack(attack)
        directInstakillDamage = self.__getInstakillDamage(toonId)
        if directInstakillDamage and (hpbonus or kbbonus):
            return totalDamages
        if track != NO_ATTACK and track != SOS and track != TRAP and track != NPCSOS:
            targets = self.__getToonTargets(attack)
            for position in xrange(len(targets)):
                currTarget = targets[position]
                if hpbonus:
                    if targets[position] in self.__createToonTargetList(toonId):
                        damageDone = attack[TOON_HPBONUS_COL]
                    else:
                        damageDone = 0
                elif kbbonus:
                    if targets[position] in self.__createToonTargetList(toonId):
                        damageDone = attack[TOON_KBBONUS_COL][position]
                       # if self.getSuitConditionModifier(currTarget.doId, 'lured') > 0:
                           # if self.suitHasCondition(currTarget.doId, 'lured'):
                               # self.setSuitCondition(currTarget.doId, 'lured', 0, 0, 'setBoth')
                    else:
                        damageDone = 0
                elif self.suitHasCondition(currTarget, 'immune'):
                    damageDone = 0
                else:
                    damageDone = attack[TOON_HP_COL][position]
                trapInstakillDamage = 0
                if not hpbonus and not kbbonus and track == LURE and damageDone > 0:
                    trapInstakillDamage = self.instakillTraps.pop(currTarget.doId, 0)
                fixedDamage = 0
                if directInstakillDamage and track in (SOUND, THROW, SQUIRT, ZAP, DROP):
                    fixedDamage = directInstakillDamage
                elif trapInstakillDamage:
                    fixedDamage = trapInstakillDamage
                if fixedDamage and damageDone > 0:
                    damageDone = fixedDamage
                if damageDone <= 0 or self.immortalSuits:
                    continue
                if track == HEAL or track == PETSOS:
                    currTarget = targets[position]
                    # if CAP_HEALS:
                    #     toonHp = self.__getToonHp(currTarget)
                    #     toonMaxHp = self.__getToonMaxHp(currTarget)
                    #     if toonHp + damageDone > toonMaxHp:
                    #         damageDone = toonMaxHp - toonHp
                    #         attack[TOON_HP_COL][position] = damageDone
                    self.toonHPAdjusts[currTarget] += damageDone
                    totalDamages = totalDamages + damageDone
                    continue
                currTarget = targets[position]
                currentlyImmuneSuits = self.getImmuneSuits()
                if currTarget.getImmuneStatus() == 1:
                    currTarget.setHP(currTarget.getHP())
                elif self.suitHasCondition(currTarget, 'immune'):
                    currTarget.setHP(currTarget.getHP())
                else:
                    if fixedDamage:
                        currTarget.setHP(max(0, currTarget.getHP() - damageDone))
                    elif track == SQUIRT and kbbonus == 0 and hpbonus == 0:
                        toon = self.battle.getToon(toonId)
                        attack = self.battle.toonAttacks[toonId]
                        atkTrack, atkLevel, atkHp = self.__getActualTrackLevelHp(attack)
                        attackDamage = getAvPropDamage(atkTrack, atkLevel, toon.experience.getExp(atkTrack))
                        suit = self.battle.findSuit(currTarget.doId)
                        if self.suitHasCondition(currTarget.doId, 'vulnerablevideographer'):
                            attackDamage *= self.getSuitConditionModifier(suit.doId, 'vulnerablevideographer')
                        if self.suitHasCondition(currTarget.doId, 'directorDamageReduction'):
                            attackDamage *= self.getSuitConditionModifier(suit.doId, 'directorDamageReduction')
                        if self.toonHasCondition(toonId, 'viralSensation'):
                            attackDamage *= (1.0 + self.getToonConditionModifier(toonId, 'viralSensation') * 0.01)
                        if self.toonHasCondition(toonId, 'energized'):
                            attackDamage *= (1.0 + self.getToonConditionModifier(toonId, 'energized') * 0.01)
                        if self.toonHasCondition(toonId, 'allGagBoost'):
                            attackDamage *= (1.0 + (self.getToonConditionModifier(toonId, 'allGagBoost') * 0.01))
                        if self.toonHasCondition(toonId, 'allGagBoost2'):
                            attackDamage *= (1.0 + (self.getToonConditionModifier(toonId, 'allGagBoost2') * 0.01))
                        if self.toonHasCondition(toonId, 'raisedAnte'):
                            attackDamage *= (1.0 + (self.getToonConditionModifier(toonId, 'raisedAnte') * 0.01))
                        if self.toonHasCondition(toonId, 'governaughtBoost'):
                            attackDamage *= (1.0 + self.getToonConditionModifier(toonId, 'governaughtBoost') * 0.01)
                        if self.suitHasCondition(currTarget.doId, 'immune'):
                            attackDamage = 0
                        if self.suitHasCondition(currTarget.doId, 'HRdamagereduction'):
                            attackDamage *= 0.1
                        if self.suitHasCondition(currTarget.doId, 'damageReduction'):
                            attackDamage *= 0.7
                        if self.suitHasCondition(currTarget.doId, 'monsoon'):
                            attackDamage *= 0.1
                        if self.toonHasCondition(toonId, 'encore'):
                            attackDamage *= 1.2
                        if self.toonHasCondition(toonId, 'encore2'):
                            attackDamage *= 1.1
                        if self.suitHasCondition(currTarget.doId, 'enraged') and not self.suitHasCondition(currTarget.doId, 'desperation'):
                            attackDamage *= 0.7
                        if self.suitHasCondition(currTarget.doId, 'vulnerable'):
                            attackDamage *= 1.3
                        if self.suitHasCondition(currTarget.doId, 'dancesession'):
                            attackDamage *= .7
                        if self.suitHasCondition(currTarget.doId, 'vulnerablebroadcaster'):
                            attackDamage *= 2
                        if self.suitHasCondition(currTarget.doId, 'vulnerablesilhouette1'):
                            attackDamage *= 1.5
                        if self.suitHasCondition(currTarget.doId, 'vulnerablesilhouette2'):
                            attackDamage *= 2
                        if self.suitHasCondition(currTarget.doId, 'vulnerablesilhouette3'):
                            attackDamage *= 3
                        if self.suitHasCondition(currTarget.doId, 'marked'):
                            attackDamage *= 1.1
                        if self.suitHasCondition(currTarget.doId, 'enraged') and self.suitHasCondition(currTarget.doId, 'desperation'):
                            attackDamage *= 1
                        if self.suitHasCondition(currTarget.doId, 'soakImmune') and (self.suitHasCondition(currTarget.doId, 'soaked') or self.suitHasCondition(currTarget.doId, 'drenched')):
                            attackDamage *= 0.4
                        if self.toonHasCondition(toonId, 'groupDamageDown'):
                            attackDamage *= 0.5
                        if self.toonHasCondition(toonId, 'noDamage'):
                            attackDamage *= 0
                        if self.suitHasCondition(currTarget.doId, 'heavyRainDamage'):
                            attackDamage *= 0.6
                            self.setSuitCondition(currTarget.doId, 'heavyRainDamage', self.getSuitConditionModifier(currTarget.doId, 'heavyRainDamage') + attackDamage, -1, 'setBoth')
                        activeSuits = self.battle.activeSuits
                        currTarget.setHP(currTarget.getHP() - damageDone)
                        suitIndex = activeSuits.index(currTarget)
                        damageDone2 = attack[TOON_HP_COL][position]
                        if suitIndex - 1 >= 0:
                            target2 = activeSuits[suitIndex - 1]
                            organicBonus = self.__toonCheckGagBonus(attack[TOON_ID_COL], atkTrack, atkLevel)
                            if organicBonus:
                                if not self.suitHasCondition(target2.doId, 'immune') and not self.suitHasCondition(target2.doId, 'oilRain'):
                                    target2.setHP(target2.getHP() - math.ceil(damageDone * .75))
                                    if self.suitHasCondition(target2.doId, 'heavyRainDamage'):
                                        self.setSuitCondition(target2.doId, 'heavyRainDamage', self.getSuitConditionModifier(target2.doId, 'heavyRainDamage') + damageDone, -1, 'setBoth')
                                    if target2.dna.name == 'supervis' and target2.getActualLevel() == 20:
                                        self.levels += atkLevel
                                    if target2.dna.name == 'clubpres' and target2.getActualLevel() == 25:
                                        self.setSuitCondition(target2.doId, 'shivering', self.getSuitConditionModifier(target2.doId, 'shivering') + 1, 1, 'setBoth')
                                    if target2.dna.name == 'clubpres' and target2.getActualLevel() == 23:
                                        self.setSuitCondition(target2.doId, 'rpm', self.getSuitConditionModifier(target2.doId, 'rpm') + 1, 1, 'setBoth')
                                    # if target2.dna.name == 'cbutcher':
                                    #     self.setSuitCondition(target2.doId, 'rpmincrease', self.getSuitConditionModifier(target2.doId, 'rpmincrease') + 1, -1, 'setBoth')
                                    #     self.setSuitCondition(target2.doId, 'rpmcalculator', 1, 10, 'setBoth')
                                    if not self.suitHasCondition(target2.doId, 'alreadyTargeted'):
                                        self.setSuitCondition(target2.doId, 'alreadyTargeted', 1, 1, 'setBoth')
                                        self.targets += 1
                                    if target2.getHP() <= 0:
                                        self.__removeLured(target2.doId)
                                        if target2.getSkeleRevives() >= 1:
                                            target2.useSkeleRevive()
                                        if not self.suitHasCondition(target2.doId, 'dead'):
                                            if target2.dna.name == 'cbutcher':
                                                for s in self.battle.activeSuits:
                                                    if s.dna.name == 'rkeeper':
                                                        self.setSuitCondition(s.doId, 'phantomDeath', 1, 1, 'setBoth')
                                            if self.suitHasCondition(target2.doId, 'overpressure'):
                                                for s in self.battle.activeSuits:
                                                    if s.dna.name == 'safesupervis':
                                                        if self.suitHasCondition(s.doId, 'overpressureDeath'):
                                                            self.setSuitCondition(s.doId, 'overpressureDeath2', 1, 1, 'setBoth')
                                                        elif self.suitHasCondition(s.doId, 'overpressureDeath2'):
                                                            self.setSuitCondition(s.doId, 'overpressureDeath3', 1, 1, 'setBoth')
                                                        else:
                                                            self.setSuitCondition(s.doId, 'overpressureDeath', 1, 1, 'setBoth')
                                            self.setSuitCondition(target2.doId, 'dead', 1, 2, 'setBoth')
                                            self.deadSuits += 1
                                            if target2.getExecutive() or target2.getGovernaught():
                                                levelAmount = target2.getActualLevel() * 9
                                            else:
                                                levelAmount = target2.getActualLevel() * 5

                                            self.addLevelDamage(levelAmount, atkTrack)
                            else:
                                if not self.suitHasCondition(target2.doId, 'immune'):
                                    target2.setHP(target2.getHP() - math.ceil(damageDone / 3))
                                    if self.suitHasCondition(target2.doId, 'heavyRainDamage'):
                                        self.setSuitCondition(target2.doId, 'heavyRainDamage', self.getSuitConditionModifier(target2.doId, 'heavyRainDamage') + damageDone, -1, 'setBoth')
                                    if target2.dna.name == 'supervis' and target2.getActualLevel() == 20:
                                        self.levels += atkLevel
                                    if target2.dna.name == 'clubpres' and target2.getActualLevel() == 25:
                                        self.setSuitCondition(target2.doId, 'shivering', self.getSuitConditionModifier(target2.doId, 'shivering') + 1, 1, 'setBoth')
                                    if target2.dna.name == 'clubpres' and target2.getActualLevel() == 23:
                                        self.setSuitCondition(target2.doId, 'rpm', self.getSuitConditionModifier(target2.doId, 'rpm') + 1, 1, 'setBoth')
                                    # if target2.dna.name == 'cbutcher':
                                    #     self.setSuitCondition(target2.doId, 'rpmincrease', self.getSuitConditionModifier(target2.doId, 'rpmincrease') + 1, -1, 'setBoth')
                                    #     self.setSuitCondition(target2.doId, 'rpmcalculator', 1, 10, 'setBoth')
                                    if not self.suitHasCondition(target2.doId, 'alreadyTargeted'):
                                        self.setSuitCondition(target2.doId, 'alreadyTargeted', 1, 1, 'setBoth')
                                        self.targets += 1
                                    if target2.getHP() <= 0:
                                        self.__removeLured(target2.doId)
                                        if target2.getSkeleRevives() >= 1:
                                            target2.useSkeleRevive()
                                        if not self.suitHasCondition(target2.doId, 'dead'):
                                            if target2.dna.name == 'cbutcher':
                                                for s in self.battle.activeSuits:
                                                    if s.dna.name == 'rkeeper':
                                                        self.setSuitCondition(s.doId, 'phantomDeath', 1, 1, 'setBoth')
                                            if self.suitHasCondition(target2.doId, 'overpressure'):
                                                for s in self.battle.activeSuits:
                                                    if s.dna.name == 'safesupervis':
                                                        if self.suitHasCondition(s.doId, 'overpressureDeath'):
                                                            self.setSuitCondition(s.doId, 'overpressureDeath2', 1, 1, 'setBoth')
                                                        elif self.suitHasCondition(s.doId, 'overpressureDeath2'):
                                                            self.setSuitCondition(s.doId, 'overpressureDeath3', 1, 1, 'setBoth')
                                                        else:
                                                            self.setSuitCondition(s.doId, 'overpressureDeath', 1, 1, 'setBoth')
                                            self.setSuitCondition(target2.doId, 'dead', 1, 2, 'setBoth')
                                            self.deadSuits += 1
                                            if target2.getExecutive() or target2.getGovernaught():
                                                levelAmount = target2.getActualLevel() * 9
                                            else:
                                                levelAmount = target2.getActualLevel() * 5

                                            self.addLevelDamage(levelAmount, atkTrack)
                        if suitIndex + 1 < len(activeSuits):
                            target3 = activeSuits[suitIndex + 1]
                            organicBonus = self.__toonCheckGagBonus(attack[TOON_ID_COL], atkTrack, atkLevel)
                            if organicBonus:
                                if not self.suitHasCondition(target3.doId, 'immune') and not self.suitHasCondition(target3.doId, 'oilRain'):
                                    target3.setHP(target3.getHP() - math.ceil(damageDone * .75))
                                    if self.suitHasCondition(target3.doId, 'heavyRainDamage'):
                                        self.setSuitCondition(target3.doId, 'heavyRainDamage', self.getSuitConditionModifier(target3.doId, 'heavyRainDamage') + damageDone, -1, 'setBoth')
                                    if target3.dna.name == 'supervis' and target3.getActualLevel() == 20:
                                        self.levels += atkLevel
                                    if target3.dna.name == 'clubpres' and target3.getActualLevel() == 25:
                                        self.setSuitCondition(target3.doId, 'shivering', self.getSuitConditionModifier(target3.doId, 'shivering') + 1, 1, 'setBoth')
                                    if target3.dna.name == 'clubpres' and target3.getActualLevel() == 23:
                                        self.setSuitCondition(target3.doId, 'rpm', self.getSuitConditionModifier(target3.doId, 'rpm') + 1, 1, 'setBoth')
                                    # if target3.dna.name == 'cbutcher':
                                    #     self.setSuitCondition(target3.doId, 'rpmincrease', self.getSuitConditionModifier(target3.doId, 'rpmincrease') + 1, -1, 'setBoth')
                                    #     self.setSuitCondition(target3.doId, 'rpmcalculator', 1, 10, 'setBoth')
                                    if not self.suitHasCondition(target3.doId, 'alreadyTargeted'):
                                        self.setSuitCondition(target3.doId, 'alreadyTargeted', 1, 1, 'setBoth')
                                        self.targets += 1
                                    if target3.getHP() <= 0:
                                        self.__removeLured(target3.doId)
                                        if target3.getSkeleRevives() >= 1:
                                            target3.useSkeleRevive()
                                        if not self.suitHasCondition(target3.doId, 'dead'):
                                            if target3.dna.name == 'cbutcher':
                                                for s in self.battle.activeSuits:
                                                    if s.dna.name == 'rkeeper':
                                                        self.setSuitCondition(s.doId, 'phantomDeath', 1, 1, 'setBoth')
                                            if self.suitHasCondition(target3.doId, 'overpressure'):
                                                for s in self.battle.activeSuits:
                                                    if s.dna.name == 'safesupervis':
                                                        if self.suitHasCondition(s.doId, 'overpressureDeath'):
                                                            self.setSuitCondition(s.doId, 'overpressureDeath2', 1, 1, 'setBoth')
                                                        elif self.suitHasCondition(s.doId, 'overpressureDeath2'):
                                                            self.setSuitCondition(s.doId, 'overpressureDeath3', 1, 1, 'setBoth')
                                                        else:
                                                            self.setSuitCondition(s.doId, 'overpressureDeath', 1, 1, 'setBoth')
                                            self.setSuitCondition(target3.doId, 'dead', 1, 2, 'setBoth')
                                            self.deadSuits += 1
                                            if target3.getExecutive() or target3.getGovernaught():
                                                levelAmount = target3.getActualLevel() * 9
                                            else:
                                                levelAmount = target3.getActualLevel() * 5

                                            self.addLevelDamage(levelAmount, atkTrack)
                            else:
                                if not self.suitHasCondition(target3.doId, 'immune'):
                                    target3.setHP(target3.getHP() - math.ceil(damageDone / 3))
                                    if self.suitHasCondition(target3.doId, 'heavyRainDamage'):
                                        self.setSuitCondition(target3.doId, 'heavyRainDamage', self.getSuitConditionModifier(target3.doId, 'heavyRainDamage') + damageDone, -1, 'setBoth')
                                    if target3.dna.name == 'supervis' and target3.getActualLevel() == 20:
                                        self.levels += atkLevel
                                    if target3.dna.name == 'clubpres' and target3.getActualLevel() == 25:
                                        self.setSuitCondition(target3.doId, 'shivering', self.getSuitConditionModifier(target3.doId, 'shivering') + 1, 1, 'setBoth')
                                    if target3.dna.name == 'clubpres' and target3.getActualLevel() == 23:
                                        self.setSuitCondition(target3.doId, 'rpm', self.getSuitConditionModifier(target3.doId, 'rpm') + 1, 1, 'setBoth')
                                    # if target3.dna.name == 'cbutcher':
                                    #     self.setSuitCondition(target3.doId, 'rpmincrease', self.getSuitConditionModifier(target3.doId, 'rpmincrease') + 1, -1, 'setBoth')
                                    #     self.setSuitCondition(target3.doId, 'rpmcalculator', 1, 10, 'setBoth')
                                    if not self.suitHasCondition(target3.doId, 'alreadyTargeted'):
                                        self.setSuitCondition(target3.doId, 'alreadyTargeted', 1, 1, 'setBoth')
                                        self.targets += 1
                                    if target3.getHP() <= 0:
                                        self.__removeLured(target3.doId)
                                        if target3.getSkeleRevives() >= 1:
                                            target3.useSkeleRevive()
                                        if not self.suitHasCondition(target3.doId, 'dead'):
                                            if target3.dna.name == 'cbutcher':
                                                for s in self.battle.activeSuits:
                                                    if s.dna.name == 'rkeeper':
                                                        self.setSuitCondition(s.doId, 'phantomDeath', 1, 1, 'setBoth')
                                            if self.suitHasCondition(target3.doId, 'overpressure'):
                                                for s in self.battle.activeSuits:
                                                    if s.dna.name == 'safesupervis':
                                                        if self.suitHasCondition(s.doId, 'overpressureDeath'):
                                                            self.setSuitCondition(s.doId, 'overpressureDeath2', 1, 1, 'setBoth')
                                                        elif self.suitHasCondition(s.doId, 'overpressureDeath2'):
                                                            self.setSuitCondition(s.doId, 'overpressureDeath3', 1, 1, 'setBoth')
                                                        else:
                                                            self.setSuitCondition(s.doId, 'overpressureDeath', 1, 1, 'setBoth')
                                            self.setSuitCondition(target3.doId, 'dead', 1, 2, 'setBoth')
                                            self.deadSuits += 1
                                            if target3.getExecutive() or target3.getGovernaught():
                                                levelAmount = target3.getActualLevel() * 9
                                            else:
                                                levelAmount = target3.getActualLevel() * 5

                                            self.addLevelDamage(levelAmount, atkTrack)
                    else:
                        currTarget.setHP(currTarget.getHP() - damageDone)
                targetId = currTarget.getDoId()
                totalDamages = totalDamages + damageDone
                atkTrack, atkLevel, atkHp = self.__getActualTrackLevelHp(attack)
                if currTarget.getHP() <= 0:
                    if currTarget.getSkeleRevives() >= 1:
                        currTarget.useSkeleRevive()
                        attack[SUIT_REVIVE_COL] = attack[SUIT_REVIVE_COL] | 1 << position
                    else:
                        if not self.suitHasCondition(currTarget.doId, 'dead'):
                            # for s in self.battle.activeSuits:
                            #     # if s.dna.name == 'cbutcher':
                            #     #     self.setSuitCondition(s.doId, 'rpmincrease', self.getSuitConditionModifier(s.doId, 'rpmincrease') + 1, -1, 'setBoth')
                            #     #     self.setSuitCondition(s.doId, 'rpmcalculator', 1, 10, 'setBoth')
                            if currTarget.dna.name == 'cbutcher':
                                for s in self.battle.activeSuits:
                                    if s.dna.name == 'rkeeper':
                                        self.setSuitCondition(s.doId, 'phantomDeath', 1, 1, 'setBoth')
                            if self.suitHasCondition(currTarget.doId, 'overpressure'):
                                for s in self.battle.activeSuits:
                                    if s.dna.name == 'safesupervis':
                                        if self.suitHasCondition(currTarget.doId, 'overpressureDeath'):
                                            self.setSuitCondition(s.doId, 'overpressureDeath2', 1, 1, 'setBoth')
                                        elif self.suitHasCondition(currTarget.doId, 'overpressureDeath2'):
                                            self.setSuitCondition(s.doId, 'overpressureDeath3', 1, 1, 'setBoth')
                                        else:
                                            self.setSuitCondition(s.doId, 'overpressureDeath', 1, 1, 'setBoth')
                            self.setSuitCondition(currTarget.doId, 'dead', 1, 2, 'setBoth')
                            self.deadSuits += 1
                            if currTarget.getExecutive() or currTarget.getGovernaught():
                                levelAmount = currTarget.getActualLevel() * 9
                            else:
                                levelAmount = currTarget.getActualLevel() * 5

                            self.addLevelDamage(levelAmount, atkTrack)
                        self.suitLeftBattle(targetId)
                        attack[SUIT_DIED_COL] = attack[SUIT_DIED_COL] | 1 << position
                        if self.notify.getDebug():
                            self.notify.debug('Suit' + str(targetId) + 'bravely expired in combat')

        return totalDamages

    def __combatantDead(self, avId, toon):
        if toon:
            if self.__getToonHp(avId) <= 0:
                return 1
        else:
            suit = self.battle.findSuit(avId)
            if suit.getHP() <= 0:
                if suit.dna.name == 'cbutcher':
                    for s in self.battle.activeSuits:
                        if s.dna.name == 'rkeeper':
                            self.setSuitCondition(s.doId, 'phantomDeath', 1, 1, 'setBoth')
                self.__removeLured(suit.doId)
                self.setSuitCondition(suit.doId, 'lured', 0, 0, 'setBoth')
                if self.suitHasCondition(suit.doId, 'shielding'):
                    for suit in self.battle.activeSuits:
                        self.setSuitCondition(suit.doId, 'deadpromotion', 1, -1, 'setBoth')
                return 1
        return 0

    def __combatantJustRevived(self, avId):
        suit = self.battle.findSuit(avId)
        self.__removeLured(avId)
        if suit.reviveCheckAndClear():
            return 1
        else:
            return 0

    def checkRevertImmuneCogs(self):
        currentlyImmuneSuits = self.getImmuneSuits()
        immuneNum = 0
        for suit in self.battle.activeSuits:
            if suit.getImmuneStatus() == 1:
                immuneNum += 1
        if immuneNum == len(self.battle.activeSuits) and len(self.battle.joiningSuits) == 0 and len(
                self.battle.pendingSuits) == 0:
            return 1
        else:
            return 0

    def checkRevertEnragedCogs(self):
        currentlyEnragedSuits = self.getEnragedSuits()
        enragedNum = 0
        for suit in self.battle.activeSuits:
            if suit.getEnragedStatus() == 1:
                enragedNum += 1
        if enragedNum == len(self.battle.activeSuits) and len(self.battle.joiningSuits) == 0 and len(
                self.battle.pendingSuits) == 0:
            return 1
        else:
            return 0

    def checkRevertAbsorbingCogs(self):
        currentlyAbsorbingSuits = self.getAbsorbingSuits()
        absorbingNum = 0
        for suit in self.battle.activeSuits:
            if suit.getAbsorbingStatus() == 1:
                absorbingNum += 1
        if absorbingNum == len(self.battle.activeSuits) and len(self.battle.joiningSuits) == 0 and len(
                self.battle.pendingSuits) == 0:
            return 1
        else:
            return 0

    def checkRevertSoakedCogs(self):
        currentlySoakedSuits = self.getSoakedSuits()
        soakedNum = 0
        for suit in self.battle.activeSuits:
            if suit.getSoakedStatus() == 1:
                soakedNum += 1
        if soakedNum == len(self.battle.activeSuits) and len(self.battle.joiningSuits) == 0 and len(
                self.battle.pendingSuits) == 0:
            return 1
        else:
            return 0

    def __addAttackExp(self, attack, track = -1, level = -1, attackerId = -1):
        trk = -1
        lvl = -1
        id = -1
        if track != -1 and level != -1 and attackerId != -1:
            trk = track
            lvl = level
            id = attackerId
        elif self.__attackHasHit(attack):
            if self.notify.getDebug():
                self.notify.debug('Attack ' + repr(attack) + ' has hit')
            trk = attack[TOON_TRACK_COL]
            lvl = attack[TOON_LVL_COL]
            id = attack[TOON_ID_COL]
        if trk != -1 and trk != NPCSOS and trk != PETSOS and lvl != -1 and id != -1:
            expList = self.toonSkillPtsGained.get(id, None)
            if expList == None:
                expList = [0,
                 0,
                 0,
                 0,
                 0,
                 0,
                 0,
                 0]
                self.toonSkillPtsGained[id] = expList
            expList[trk] = min(ExperienceCap, expList[trk] + (lvl + 1) * self.__skillCreditMultiplier)


    def __clearTgtDied(self, tgt, lastAtk, currAtk):
        position = self.battle.activeSuits.index(tgt)
        currAtkTrack = self.__getActualTrack(currAtk)
        lastAtkTrack = self.__getActualTrack(lastAtk)
        if currAtkTrack == lastAtkTrack and lastAtk[SUIT_DIED_COL] & 1 << position and self.__attackHasHit(currAtk, suit=0):
            if self.notify.getDebug():
                self.notify.debug('Clearing suit died for ' + str(tgt.getDoId()) + ' at position ' + str(position) + ' from toon attack ' + str(lastAtk[TOON_ID_COL]) + ' and setting it for ' + str(currAtk[TOON_ID_COL]))
            lastAtk[SUIT_DIED_COL] = lastAtk[SUIT_DIED_COL] ^ 1 << position
            self.suitLeftBattle(tgt.getDoId())
            self.__removeLured(tgt)
            currAtk[SUIT_DIED_COL] = currAtk[SUIT_DIED_COL] | 1 << position

    def __addDmgToBonuses(self, dmg, attackIndex, hp = 1):
        toonId = self.toonAtkOrder[attackIndex]
        attack = self.battle.toonAttacks[toonId]
        atkTrack = self.__getActualTrack(attack)
        if atkTrack == HEAL or atkTrack == PETSOS:
            return
        tgts = self.__createToonTargetList(toonId)
        for currTgt in tgts:
            tgtPos = self.battle.activeSuits.index(currTgt)
            attackerId = self.toonAtkOrder[attackIndex]
            attack = self.battle.toonAttacks[attackerId]
            track = self.__getActualTrack(attack)
            if hp:
                if track in self.hpBonuses[tgtPos]:
                    self.hpBonuses[tgtPos][track].append([attackIndex, dmg])
                else:
                    self.hpBonuses[tgtPos][track] = [[attackIndex, dmg]]
            elif self.__suitIsLured(currTgt.getDoId()):
                if track in self.kbBonuses[tgtPos]:
                    self.kbBonuses[tgtPos][track].append([attackIndex, dmg])
                else:
                    self.kbBonuses[tgtPos][track] = [[attackIndex, dmg]]

    def __clearBonuses(self, hp = 1):
        if hp:
            self.hpBonuses = [{},
             {},
             {},
             {},
                              {},
                              {},
             {}]
        else:
            self.kbBonuses = [{},
             {},
             {},
                          {},
                              {},
                              {},
             {}]

    def __bonusExists(self, tgtSuit, hp = 1):
        tgtPos = self.activeSuits.index(tgtSuit)
        if hp:
            bonusLen = len(self.hpBonuses[tgtPos])
        else:
            bonusLen = len(self.kbBonuses[tgtPos])
        if bonusLen > 0:
            return 1
        return 0

    def __processBonuses(self, hp = 1):
        if hp:
            bonusList = self.hpBonuses
            self.notify.debug('Processing hpBonuses: ' + repr(self.hpBonuses))
        else:
            bonusList = self.kbBonuses
            self.notify.debug('Processing kbBonuses: ' + repr(self.kbBonuses))
        tgtPos = 0
        for currTgt in bonusList:
            for currAtkType in currTgt.keys():
                if len(currTgt[currAtkType]) > 1 or not hp and len(currTgt[currAtkType]) > 0:
                    totalDmgs = 0
                    for currDmg in currTgt[currAtkType]:
                        totalDmgs += currDmg[1]

                    numDmgs = len(currTgt[currAtkType])
                    attackIdx = currTgt[currAtkType][numDmgs - 1][0]
                    attackerId = self.toonAtkOrder[attackIdx]
                    attack = self.battle.toonAttacks[attackerId]
                    atkTrack = self.__getActualTrack(attack)
                    if hp:
                        suit = self.battle.activeSuits[tgtPos].doId
                        theSuit = self.battle.findSuit(suit)
                        if self.suitHasCondition(suit, 'kbImmune') and not atkTrack == ZAP and not atkTrack == SOUND:
                            attack[TOON_HPBONUS_COL] = 0
                            self.comboDamage += math.ceil(totalDmgs * (DamageBonuses[numDmgs - 1] * 0.01))
                        elif self.suitHasCondition(suit, 'overseer') and not atkTrack == DROP and not atkTrack == ZAP and not atkTrack == SOUND:
                            attack[TOON_HPBONUS_COL] = 1
                            self.comboDamage += math.ceil(totalDmgs * (DamageBonuses[numDmgs - 1] * 0.01))
                            self.setSuitCondition(suit, 'overseerCombo', 1, 1, 'setBoth')
                        elif self.suitHasCondition(suit, 'overseer') and atkTrack == DROP:
                            attack[TOON_HPBONUS_COL] = 1
                            self.comboDamage += math.ceil(totalDmgs * (DamageBonusesDrop[numDmgs - 1] * 0.01))
                            self.setSuitCondition(suit, 'overseerCombo', 1, 1, 'setBoth')
                        elif self.suitHasCondition(suit, 'attorney') and not atkTrack == DROP and not atkTrack == ZAP and not atkTrack == SOUND:
                            attack[TOON_HPBONUS_COL] =  math.ceil(totalDmgs * (DamageBonuses[numDmgs - 1] * 0.01))
                            self.objectionDamage += math.ceil(totalDmgs * (DamageBonuses[numDmgs - 1] * 0.01))
                            self.setSuitCondition(suit, 'attorneyKB', 1, 1, 'setBoth')
                        elif self.suitHasCondition(suit, 'attorney') and atkTrack == DROP:
                            attack[TOON_HPBONUS_COL] = math.ceil(totalDmgs * (DamageBonusesDrop[numDmgs - 1] * 0.01))
                            self.objectionDamage += math.ceil(totalDmgs * (DamageBonusesDrop[numDmgs - 1] * 0.01))
                            self.setSuitCondition(suit, 'attorneyKB', 1, 1, 'setBoth')
                        elif atkTrack == DROP:
                            attack[TOON_HPBONUS_COL] = math.ceil(totalDmgs * (DamageBonusesDrop[numDmgs - 1] * 0.01))
                            if theSuit.dna.name == 'erfit':
                                self.countErfitHP += math.ceil(totalDmgs * (DamageBonusesDrop[numDmgs - 1] * 0.01))
                            if theSuit.dna.name == 'erclaim':
                                self.countErclaimHP += math.ceil(totalDmgs * (DamageBonusesDrop[numDmgs - 1] * 0.01))
                        elif atkTrack == ZAP:
                            attack[TOON_HPBONUS_COL] = 0
                        elif atkTrack == SOUND:
                            attack[TOON_HPBONUS_COL] = 0
                        else:
                            attack[TOON_HPBONUS_COL] = math.ceil(totalDmgs * (DamageBonuses[numDmgs - 1] * 0.01))
                            if theSuit.dna.name == 'erfit':
                                self.countErfitHP += math.ceil(totalDmgs * (DamageBonuses[numDmgs - 1] * 0.01))
                            if theSuit.dna.name == 'erclaim':
                                self.countErclaimHP += math.ceil(totalDmgs * (DamageBonuses[numDmgs - 1] * 0.01))
                        if self.notify.getDebug():
                            self.notify.debug(
                                'Applying hp bonus to track ' + str(attack[TOON_TRACK_COL]) + ' of ' + str(
                                    attack[TOON_HPBONUS_COL]))
                    elif len(attack[TOON_KBBONUS_COL]) > tgtPos:
                        lureKBValue = 0
                        suit = self.battle.activeSuits[tgtPos].doId
                        if self.suitHasCondition(suit, 'lureImmune'):
                            lureKBValue = 0
                            self.setSuitCondition(suit, 'lured', 0, 0, 'setBoth')
                        if self.suitHasCondition(suit, 'lured'):
                            lureKBValue = self.getSuitConditionModifier(suit, 'lured') * 0.01
                            self.setSuitCondition(suit, 'lured', 0, 0, 'setBoth')
                        if self.suitHasCondition(suit, 'overseer'):
                            attack[TOON_KBBONUS_COL][tgtPos] = 1
                            self.knockbackDamage += math.ceil(totalDmgs * (lureKBValue / 2))
                            self.setSuitCondition(suit, 'overseerKB', 1, 1, 'setBoth')
                        elif self.suitHasCondition(suit, 'noKB'):
                            attack[TOON_KBBONUS_COL][tgtPos] = 0
                            self.knockbackDamage += math.ceil(totalDmgs * (lureKBValue / 2))
                        else:
                            attack[TOON_KBBONUS_COL][tgtPos] = math.ceil(totalDmgs * (lureKBValue / 2))
                        if self.notify.getDebug():
                            self.notify.debug(
                                'Applying kb bonus to track ' + str(attack[TOON_TRACK_COL]) + ' of ' + str(
                                    attack[TOON_KBBONUS_COL][tgtPos]) + ' to target ' + str(tgtPos))
                    else:
                        self.notify.warning('invalid tgtPos for knock back bonus: %d' % tgtPos)

            tgtPos += 1

        if hp:
            self.__clearBonuses()
        else:
            self.__clearBonuses(hp=0)

    def __handleBonus(self, attackIdx, hp = 1):
        attackerId = self.toonAtkOrder[attackIdx]
        attack = self.battle.toonAttacks[attackerId]
        atkDmg = self.__attackDamage(attack, suit=0)
        atkTrack = self.__getActualTrack(attack)
        if atkDmg > 0:
            if hp:
                if atkTrack != LURE:
                    self.notify.debug('Adding dmg of ' + str(atkDmg) + ' to hpBonuses list')
                    self.__addDmgToBonuses(atkDmg, attackIdx)
            elif self.__knockBackAtk(attackerId, toon=1):
                self.notify.debug('Adding dmg of ' + str(atkDmg) + ' to kbBonuses list')
                self.__addDmgToBonuses(atkDmg, attackIdx, hp=0)

    def __clearAttack(self, attackIdx, toon = 1):
        if toon:
            attack = self.battle.toonAttacks[attackIdx]

            # Do not clear Sue before the movie packet is sent.
            if attack[TOON_TRACK_COL] == SUE:
                longest = max(len(self.battle.activeToons), len(self.battle.activeSuits))
                for j in xrange(longest):
                    attack[TOON_HP_COL].append(1)
                    attack[TOON_KBBONUS_COL].append(0)
                return

            self.battle.toonAttacks[attackIdx] = getToonAttack(attackIdx)

            longest = max(len(self.battle.activeToons), len(self.battle.activeSuits))
            taList = self.battle.toonAttacks
            for j in xrange(longest):
                taList[attackIdx][TOON_HP_COL].append(-1)
                taList[attackIdx][TOON_KBBONUS_COL].append(-1)

    def __rememberToonAttack(self, suitId, toonId, damage):
        if not suitId in self.SuitAttackers:
            self.SuitAttackers[suitId] = {toonId: damage}
        elif not toonId in self.SuitAttackers[suitId]:
            self.SuitAttackers[suitId][toonId] = damage
        elif self.SuitAttackers[suitId][toonId] <= damage:
            self.SuitAttackers[suitId] = [toonId, damage]

    def __postProcessToonAttacks(self):
        self.notify.debug('__postProcessToonAttacks()')
        lastTrack = -1
        lastAttacks = []
        self.__clearBonuses()
        for currToonAttack in self.toonAtkOrder:
            if currToonAttack != -1:
                attack = self.battle.toonAttacks[currToonAttack]
                atkTrack, atkLevel = self.__getActualTrackLevel(attack)
                if atkTrack != HEAL and atkTrack != SOS and atkTrack != NO_ATTACK and atkTrack != NPCSOS and atkTrack != PETSOS:
                    targets = self.__createToonTargetList(currToonAttack)
                    allTargetsDead = 1
                    for currTgt in targets:
                        damageDone = self.__attackDamage(attack, suit=0)
                        if damageDone > 0:
                            self.__rememberToonAttack(currTgt.getDoId(), attack[TOON_ID_COL], damageDone)
                        if atkTrack == TRAP:
                            if currTgt.doId in self.traps:
                                trapInfo = self.traps[currTgt.doId]
                                currTgt.battleTrap = trapInfo[0]
                        targetDead = 0
                        if currTgt.getHP() > 0:
                            allTargetsDead = 0
                        else:
                            targetDead = 1
                            if atkTrack != LURE:
                                for currLastAtk in lastAttacks:
                                    self.__clearTgtDied(currTgt, currLastAtk, attack)

                        tgtId = currTgt.getDoId()
                        if tgtId in self.successfulLures and atkTrack == LURE:
                            lureInfo = self.successfulLures[tgtId]
                            self.notify.debug('applying lure data: ' + repr(lureInfo))
                            toonId = lureInfo[0]
                            lureAtk = self.battle.toonAttacks[toonId]
                            tgtPos = self.battle.activeSuits.index(currTgt)
                            if currTgt.doId in self.traps:
                                trapInfo = self.traps[currTgt.doId]
                                if trapInfo[0] == UBER_GAG_LEVEL_INDEX:
                                    self.notify.debug('train trap triggered for %d' % currTgt.doId)
                                    self.trainTrapTriggered = True
                            if not self.suitHasCondition(tgtId, 'lureImmune') and not self.suitHasCondition(tgtId, 'immune') and not (self.suitHasCondition(tgtId, 'enraged') and self.suitHasCondition(tgtId, 'desperation')):
                                self.__removeSuitTrap(tgtId)
                            lureAtk[TOON_KBBONUS_COL][tgtPos] = KBBONUS_TGT_LURED
                            lureAtk[TOON_HP_COL][tgtPos] = lureInfo[3]
                        elif self.__suitIsLured(tgtId) and atkTrack == DROP:
                            self.notify.debug('Drop on lured suit, ' + 'indicating with KBBONUS_COL ' + 'flag')
                            tgtPos = self.battle.activeSuits.index(currTgt)
                            attack[TOON_KBBONUS_COL][tgtPos] = KBBONUS_LURED_FLAG
                        if targetDead and atkTrack != lastTrack:
                            tgtPos = self.battle.activeSuits.index(currTgt)
                            attack[TOON_HP_COL][tgtPos] = 0
                            attack[TOON_KBBONUS_COL][tgtPos] = -1

                    if allTargetsDead and atkTrack != lastTrack:
                        if self.notify.getDebug():
                            self.notify.debug('all targets of toon attack ' + str(currToonAttack) + ' are dead')
                        self.__clearAttack(currToonAttack, toon=1)
                        attack = self.battle.toonAttacks[currToonAttack]
                        atkTrack, atkLevel = self.__getActualTrackLevel(attack)
                damagesDone = self.__applyToonAttackDamages(currToonAttack)
                self.__applyToonAttackDamages(currToonAttack, hpbonus=1)
                if atkTrack != LURE and atkTrack != DROP and atkTrack != SOUND:
                    self.__applyToonAttackDamages(currToonAttack, kbbonus=1)
                if lastTrack != atkTrack:
                    lastAttacks = []
                    lastTrack = atkTrack
                lastAttacks.append(attack)
                if self.itemIsCredit(atkTrack, atkLevel):
                    if atkTrack == TRAP or atkTrack == LURE:
                        pass
                    elif atkTrack == HEAL:
                        if damagesDone != 0:
                            self.__addAttackExp(attack)
                    else:
                        self.__addAttackExp(attack)

        if self.trainTrapTriggered:
            for suit in self.battle.activeSuits:
                suitId = suit.doId
                self.__removeSuitTrap(suitId)
                suit.battleTrap = NO_TRAP
                self.notify.debug('train trap triggered, removing trap from %d' % suitId)

        if self.notify.getDebug():
            for currToonAttack in self.toonAtkOrder:
                attack = self.battle.toonAttacks[currToonAttack]
                self.notify.debug('Final Toon attack: ' + str(attack))
                
    def __postProcessToonAttacksForTracks(self, allowedTracks):
        self.notify.debug('__postProcessToonAttacksForTracks(%s)' % str(allowedTracks))

        lastTrack = -1
        lastAttacks = []
        self.__clearBonuses()

        for currToonAttack in self.toonAtkOrder:
            if currToonAttack == -1:
                continue

            attack = self.battle.toonAttacks[currToonAttack]
            atkTrack, atkLevel = self.__getActualTrackLevel(attack)

            if atkTrack not in allowedTracks:
                continue

            # paste the body from your old __postProcessToonAttacks() here
            # starting at:
            # if atkTrack != HEAL and atkTrack != SOS ...
            # through:
            # if self.itemIsCredit(atkTrack, atkLevel): ...
            if atkTrack != HEAL and atkTrack != SOS and atkTrack != NO_ATTACK and atkTrack != NPCSOS and atkTrack != PETSOS:
                targets = self.__createToonTargetList(currToonAttack)
                allTargetsDead = 1
                for currTgt in targets:
                    damageDone = self.__attackDamage(attack, suit=0)
                    if damageDone > 0:
                        self.__rememberToonAttack(currTgt.getDoId(), attack[TOON_ID_COL], damageDone)
                    if atkTrack == TRAP:
                        if currTgt.doId in self.traps:
                            trapInfo = self.traps[currTgt.doId]
                            currTgt.battleTrap = trapInfo[0]
                    targetDead = 0
                    if currTgt.getHP() > 0:
                        allTargetsDead = 0
                    else:
                        targetDead = 1
                        if atkTrack != LURE:
                            for currLastAtk in lastAttacks:
                                self.__clearTgtDied(currTgt, currLastAtk, attack)

                    tgtId = currTgt.getDoId()
                    if tgtId in self.successfulLures and atkTrack == LURE:
                        lureInfo = self.successfulLures[tgtId]
                        self.notify.debug('applying lure data: ' + repr(lureInfo))
                        toonId = lureInfo[0]
                        lureAtk = self.battle.toonAttacks[toonId]
                        tgtPos = self.battle.activeSuits.index(currTgt)
                        if currTgt.doId in self.traps:
                            trapInfo = self.traps[currTgt.doId]
                            if trapInfo[0] == UBER_GAG_LEVEL_INDEX:
                                self.notify.debug('train trap triggered for %d' % currTgt.doId)
                                self.trainTrapTriggered = True
                        if not self.suitHasCondition(tgtId, 'lureImmune') and not self.suitHasCondition(tgtId, 'immune') and not (self.suitHasCondition(tgtId, 'enraged') and self.suitHasCondition(tgtId, 'desperation')):
                            self.__removeSuitTrap(tgtId)
                        lureAtk[TOON_KBBONUS_COL][tgtPos] = KBBONUS_TGT_LURED
                        lureAtk[TOON_HP_COL][tgtPos] = lureInfo[3]
                    elif self.__suitIsLured(tgtId) and atkTrack == DROP:
                        self.notify.debug('Drop on lured suit, ' + 'indicating with KBBONUS_COL ' + 'flag')
                        tgtPos = self.battle.activeSuits.index(currTgt)
                        attack[TOON_KBBONUS_COL][tgtPos] = KBBONUS_LURED_FLAG
                    if targetDead and atkTrack != lastTrack:
                        tgtPos = self.battle.activeSuits.index(currTgt)
                        attack[TOON_HP_COL][tgtPos] = 0
                        attack[TOON_KBBONUS_COL][tgtPos] = -1

                if allTargetsDead and atkTrack != lastTrack:
                    if self.notify.getDebug():
                        self.notify.debug('all targets of toon attack ' + str(currToonAttack) + ' are dead')
                    self.__clearAttack(currToonAttack, toon=1)
                    attack = self.battle.toonAttacks[currToonAttack]
                    atkTrack, atkLevel = self.__getActualTrackLevel(attack)
            damagesDone = self.__applyToonAttackDamages(currToonAttack)
            self.__applyToonAttackDamages(currToonAttack, hpbonus=1)
            if atkTrack != LURE and atkTrack != DROP and atkTrack != SOUND:
                self.__applyToonAttackDamages(currToonAttack, kbbonus=1)
            if lastTrack != atkTrack:
                lastAttacks = []
                lastTrack = atkTrack
            lastAttacks.append(attack)
            if self.itemIsCredit(atkTrack, atkLevel):
                if atkTrack == TRAP or atkTrack == LURE:
                    pass
                elif atkTrack == HEAL:
                    if damagesDone != 0:
                        self.__addAttackExp(attack)
                else:
                    self.__addAttackExp(attack)

        if self.trainTrapTriggered:
            for suit in self.battle.activeSuits:
                suitId = suit.doId
                self.__removeSuitTrap(suitId)
                suit.battleTrap = NO_TRAP
                self.notify.debug('train trap triggered, removing trap from %d' % suitId)

        if self.notify.getDebug():
            for currToonAttack in self.toonAtkOrder:
                attack = self.battle.toonAttacks[currToonAttack]
                self.notify.debug('Final Toon attack: ' + str(attack))

    def __allTargetsDead(self, attackIdx, toon = 1):
        allTargetsDead = 1
        if toon:
            targets = self.__createToonTargetList(attackIdx)
            for currTgt in targets:
                if currTgt.getHp() > 0:
                    allTargetsDead = 0
                    break

        else:
            self.notify.warning('__allTargetsDead: suit ver. not implemented!')
        return allTargetsDead

    def __clearLuredSuitsByAttack(self, toonId, kbBonusReq = 0, targetId = -1):
        if self.notify.getDebug():
            self.notify.debug('__clearLuredSuitsByAttack')
        if targetId != -1 and self.__suitIsLured(t.getDoId()):
            self.__removeLured(t.getDoId())
        else:
            tgtList = self.__createToonTargetList(toonId)
            for t in tgtList:
                if self.__suitIsLured(t.getDoId()) and (not kbBonusReq or self.__bonusExists(t, hp=0)):
                    self.__removeLured(t.getDoId())
                    if self.notify.getDebug():
                        self.notify.debug('Suit %d stepping from lured spot' % t.getDoId())
                else:
                    self.notify.debug('Suit ' + str(t.getDoId()) + ' not found in currently lured suits')

    def __clearLuredSuitsDelayed(self):
        if self.notify.getDebug():
            self.notify.debug('__clearLuredSuitsDelayed')
        for t in self.delayedUnlures:
            if self.__suitIsLured(t):
                self.__removeLured(t)
                if self.notify.getDebug():
                    self.notify.debug('Suit %d stepping back from lured spot' % t)
            else:
                self.notify.debug('Suit ' + str(t) + ' not found in currently lured suits')

        self.delayedUnlures = []

    def __addLuredSuitsDelayed(self, toonId, targetId = -1, ignoreDamageCheck = False):
        if self.notify.getDebug():
            self.notify.debug('__addLuredSuitsDelayed')
        if targetId != -1:
            self.delayedUnlures.append(targetId)
        else:
            tgtList = self.__createToonTargetList(toonId)
            for t in tgtList:
                if self.__suitIsLured(t.getDoId()) and t.getDoId() not in self.delayedUnlures and (self.__attackDamageForTgt(self.battle.toonAttacks[toonId], self.battle.activeSuits.index(t), suit=0) > 0 or ignoreDamageCheck):
                    self.delayedUnlures.append(t.getDoId())

    def __calculateToonAttacksForTracks(self, allowedTracks, finalizeBonuses=True):
        self.notify.debug('Traps: ' + str(self.traps))
        maxSuitLevel = 0
        for cog in self.battle.activeSuits:
            maxSuitLevel = max(maxSuitLevel, cog.getActualLevel())

        self.creditLevel = maxSuitLevel
        currTrack = None

        for toonId in self.toonAtkOrder:
            if self.__combatantDead(toonId, toon=1):
                continue

            attack = self.battle.toonAttacks[toonId]
            atkTrack = self.__getActualTrack(attack)

            if atkTrack not in allowedTracks:
                continue

            if atkTrack == NO_ATTACK or atkTrack == SOS or atkTrack == NPCSOS:
                continue

            if SUITS_UNLURED_IMMEDIATELY:
                if currTrack and atkTrack != currTrack:
                    self.__clearLuredSuitsDelayed()

            currTrack = atkTrack

            self.__calcToonAtkHp(toonId)

            attackIdx = self.toonAtkOrder.index(toonId)
            self.__handleBonus(attackIdx, hp=0)
            self.__handleBonus(attackIdx, hp=1)
            lastAttack = self.toonAtkOrder.index(toonId) >= len(self.toonAtkOrder) - 1
            unlureAttack = self.__unlureAtk(toonId, toon=1)
            if unlureAttack:
                if lastAttack:
                    self.__clearLuredSuitsByAttack(toonId)
                else:
                    self.__addLuredSuitsDelayed(toonId)
            if lastAttack:
                self.__clearLuredSuitsDelayed()


        if finalizeBonuses:
            self.__processBonuses(hp=0)
            self.__processBonuses(hp=1)
            self.__clearBonuses(hp=0)
            self.__clearBonuses(hp=1)

    def __calculateToonAttacks(self):
        self.notify.debug('__calculateToonAttacks()')
        self.__clearBonuses(hp=0)
        currTrack = None
        self.notify.debug('Traps: ' + str(self.traps))
        maxSuitLevel = 0
        for cog in self.battle.activeSuits:
            maxSuitLevel = max(maxSuitLevel, cog.getActualLevel())

        self.creditLevel = maxSuitLevel
        for toonId in self.toonAtkOrder:
            if self.__combatantDead(toonId, toon=1):
                if self.notify.getDebug():
                    self.notify.debug("Toon %d is dead and can't attack" % toonId)
                continue
            attack = self.battle.toonAttacks[toonId]
            atkTrack = self.__getActualTrack(attack)
            if atkTrack != NO_ATTACK and atkTrack != SOS and atkTrack != NPCSOS:
                if self.notify.getDebug():
                    self.notify.debug('Calculating attack for toon: %d' % toonId)
                if SUITS_UNLURED_IMMEDIATELY:
                    if currTrack and atkTrack != currTrack:
                        self.__clearLuredSuitsDelayed()
                currTrack = atkTrack
                self.__calcToonAtkHp(toonId)
                attackIdx = self.toonAtkOrder.index(toonId)
                self.__handleBonus(attackIdx, hp=0)
                self.__handleBonus(attackIdx, hp=1)
                lastAttack = self.toonAtkOrder.index(toonId) >= len(self.toonAtkOrder) - 1
                unlureAttack = self.__unlureAtk(toonId, toon=1)
                if unlureAttack:
                    if lastAttack:
                        self.__clearLuredSuitsByAttack(toonId)
                    else:
                        self.__addLuredSuitsDelayed(toonId)
                if lastAttack:
                    self.__clearLuredSuitsDelayed()

        self.__processBonuses(hp=0)
        self.__processBonuses(hp=1)
        self.__postProcessToonAttacks()

    def __knockBackAtk(self, attackIndex, toon = 1):
        if toon and (self.battle.toonAttacks[attackIndex][TOON_TRACK_COL] == THROW or self.battle.toonAttacks[attackIndex][TOON_TRACK_COL] == SQUIRT):
            if self.notify.getDebug():
                self.notify.debug('attack is a knockback')
            return 1
        return 0

    def __unlureAtk(self, attackIndex, toon = 1):
        attack = self.battle.toonAttacks[attackIndex]
        track = self.__getActualTrack(attack)
        if toon and (track == THROW or track == SQUIRT or track == SOUND):
            if self.notify.getDebug():
                self.notify.debug('attack is an unlure')
            return 1
        return 0

    def __calcSuitAtkType(self, theSuit):
        attacks = SuitBattleGlobals.SuitAttributes[theSuit.dna.name]['attacks']
        atk = SuitBattleGlobals.pickSuitAttack(attacks, theSuit.getLevel())
        if theSuit.dna.name == 'videog':
            x = self.TurnsElapsed
            currentBossHealth = -1
            for s in self.battle.suits:
                if s.dna.name == 'bcaster':
                    currentBossHealth = s.currHP
            currentBossHealth2 = -1
            currentBossHealth3 = -1
            for s in self.battle.suits:
                if s.dna.name == 'mh2':
                    currentBossHealth2 = s.currHP
                if s.dna.name == 'std2':
                    currentBossHealth3 = s.currHP
                if s.dna.name == 'cnd2':
                    currentBossHealth3 = s.currHP
            if currentBossHealth == -1 and not self.suitHasCondition(theSuit.doId, 'silhouettespawn') and self.suitHasCondition(theSuit.doId, 'phase3'):
                self.setSuitCondition(theSuit.doId, 'silhouettespawn', 1, 1, 'setBoth')
            if currentBossHealth2 >= 1 and (x + 1) % 3 == 0:
                self.setSuitCondition(theSuit.doId, 'hollywoodcalculator', 1, 1, 'setBoth')
            if currentBossHealth3 >= 1 and (x + 1) % 3 == 0:
                self.setSuitCondition(theSuit.doId, 'hollywoodcalculator', 1, 1, 'setBoth')
        return atk

    def __calcSuitTarget(self, attack):
        atkType = attack[SUIT_ATK_COL]
        attackName = atkType.get(
            'name',
            'unknown'
        )

        suitId = attack[SUIT_ID_COL]

        theSuit = self.battle.findSuit(suitId)
        if theSuit and getattr(getattr(theSuit, 'dna', None), 'name', None) == 'chainsaw':
            markedTargets = []
            for targetIndex, toonId in enumerate(self.battle.activeToons):
                if self.toonHasCondition(toonId, 'markedwood') and self.__toonCanBeTargetedBySuit(toonId, attack, ignoreRecentTarget=True):
                    markedTargets.append((targetIndex, toonId))
            if markedTargets:
                attackers = []
                if suitId in self.SuitAttackers:
                    for toonId in self.toonAtkOrder:
                        if toonId in self.SuitAttackers[suitId] and toonId in self.battle.activeToons:
                            attackers.append(toonId)
                if attackers:
                    toonId = attackers[-1]
                    return [self.battle.activeToons.index(toonId)]
                return [markedTargets[0][0]]

        validTargets = []

        for targetIndex, toonId in enumerate(
                self.battle.activeToons):

            if self.__toonCanBeTargetedBySuit(
                    toonId,
                    attack):

                validTargets.append(
                    targetIndex
                )

        # Everyone was recently targeted.
        # Allow one of them rather than creating no attack.
        if not validTargets:
            for targetIndex, toonId in enumerate(
                    self.battle.activeToons):

                if self.__toonCanBeTargetedBySuit(
                        toonId,
                        attack,
                        ignoreRecentTarget=True):

                    validTargets.append(
                        targetIndex
                    )

        if not validTargets:
            self.notify.warning(
                'Suit %s has no valid targets for attack %s'
                % (
                    suitId,
                    attackName
                )
            )

            return []

        if self.__suitAtkAffectsGroup(attack):
            targetCount = len(
                validTargets
            )

        elif (
            atkType['group']
            == SuitBattleGlobals.ATK_TGT_TRIPLE
        ):
            targetCount = min(
                len(validTargets),
                3
            )

        elif (
            atkType['group']
            == SuitBattleGlobals.ATK_TGT_DOUBLE
        ):
            targetCount = min(
                len(validTargets),
                2
            )

        else:
            targetCount = 1

        targets = []
        preferredTargets = []

        # Preserve retaliation targeting, but only among valid targets.
        if suitId in self.SuitAttackers:
            for toonId in self.SuitAttackers[
                    suitId].keys():

                if toonId not in self.battle.activeToons:
                    continue

                targetIndex = (
                    self.battle.activeToons.index(
                        toonId
                    )
                )

                if targetIndex in validTargets:
                    preferredTargets.append(
                        targetIndex
                    )

        while (
            preferredTargets
            and len(targets) < targetCount
        ):
            chosen = random.choice(
                preferredTargets
            )

            preferredTargets.remove(
                chosen
            )

            if chosen not in targets:
                targets.append(
                    chosen
                )

        remainingTargets = [
            targetIndex
            for targetIndex in validTargets
            if targetIndex not in targets
        ]

        random.shuffle(
            remainingTargets
        )

        targets.extend(
            remainingTargets[
                :targetCount - len(targets)
            ]
        )

        return targets

    def __calcSuitTargetSuit(self, attack):
        targets = []
        # Get the amount of Suits we are targeting and make sure it isn't more than the number of currently existing Suits.
        atkType = attack[SUIT_ATK_COL]
        if self.__suitAtkAffectsGroup(attack):
            suitCount = len(self.battle.activeSuits)
        else:
            suitCount = min(len(self.battle.activeSuits),
                            2 if atkType['group'] == SuitBattleGlobals.ATK_TGT_DOUBLE else 1)
        suitId = attack[SUIT_ID_COL]
        for i in xrange(0, suitCount):
            if suitId in self.SuitAttackers and random.randint(0, 99) < 75:
                totalDamage = 0
                for currSuit in self.SuitAttackers[suitId].keys():
                    totalDamage += self.SuitAttackers[suitId][currSuit]

                dmgs = []
                for currSuit in self.SuitAttackers[suitId].keys():
                    dmgs.append(self.SuitAttackers[suitId][currSuit] / totalDamage * 100)

                dmgIdx = SuitBattleGlobals.pickFromFreqList(dmgs)
                if dmgIdx == None:
                    suitId2 = self.__pickRandomSuit(suitId)
                else:
                    suitId2 = self.SuitAttackers[suitId].keys()[dmgIdx]
                if suitId2 == -1 or suitId2 not in self.battle.activeSuits:
                    continue
                chosen = self.battle.activeSuits.index(suitId2)
            else:
                chosen = self.__pickRandomSuit(suitId)
            while chosen in targets:
                chosen = self.__pickRandomSuit(suitId)
            targets.append(chosen)

        return targets

    def __calcSuitTargetOLD(self, attack):
        atkType = attack[SUIT_ATK_COL]
        theSuit = self.battle.findSuit(attack[SUIT_ID_COL])
        atkInfo = SuitBattleGlobals.getSuitAttack(theSuit.dna.name, theSuit.getLevel(), atkType)
        if self.__suitAtkAffectsGroup(attack):
            toonCount = len(self.battle.activeToons)
        else:
            toonCount = min(len(self.battle.activeToons),
                            2 if atkInfo['group'] == SuitBattleGlobals.ATK_TGT_DOUBLE else 1)
        suitId = attack[SUIT_ID_COL]
        for i in xrange(0, toonCount):
            if suitId in self.SuitAttackers and random.randint(0, 99) < 75:
                totalDamage = 0
                for currToon in self.SuitAttackers[suitId].keys():
                    totalDamage += self.SuitAttackers[suitId][currToon]

                dmgs = []
                for currToon in self.SuitAttackers[suitId].keys():
                    dmgs.append(self.SuitAttackers[suitId][currToon] / totalDamage * 100)

                dmgIdx = SuitBattleGlobals.pickFromFreqList(dmgs)
                if dmgIdx == None:
                    toonId = self.__pickRandomToon(suitId)
                else:
                    toonId = self.SuitAttackers[suitId].keys()[dmgIdx]
                if toonId == -1 or toonId not in self.battle.activeToons:
                    return -1
                return self.battle.activeToons.index(toonId)
            else:
                return self.__pickRandomToon(suitId)

    def __calcSuitTargetALT(self, attack):
        targets = []
        # Get the amount of Toons we are targeting and make sure it isn't more than the number of currently existing Toons.
        atkType = attack[SUIT_ATK_COL]
        toonCount = len(self.battle.activeToons)
        suitId = attack[SUIT_ID_COL]
        chosen = self.__pickRandomToon(suitId)
        targets.append(chosen)

        return targets

    def __pickRandomToon(self, suitId, attack=None):
        liveToons = []

        for currToon in self.battle.activeToons:
            if self.__toonCanBeTargetedBySuit(currToon, attack):
                liveToons.append(self.battle.activeToons.index(currToon))

        if len(liveToons) == 0:
            self.notify.debug('No tgts avail. for suit ' + str(suitId))
            return -1

        return random.choice(liveToons)

    def __pickRandomSuit(self, suitId):
        liveSuits = []
        for currSuit in self.battle.activeSuits:
            if not self.__combatantDead(currSuit, toon=0):
                liveSuits.append(self.battle.activeSuits.index(currSuit))

        if len(liveSuits) == 0:
            self.notify.debug('No tgts avail. for suit ' + str(suitId))
            return -1
        chosen = random.choice(liveSuits)
        self.notify.debug('Suit randomly attacking suit ' + str(self.battle.activeSuits[chosen]))
        return chosen

    def __suitAtkHit(self, suitId, atkType):
        if self.suitsAlwaysHit:
            return True
        elif self.suitsAlwaysMiss:
            return False
        theSuit = self.battle.findSuit(suitId)
        # if not theSuit:
        #     self.notify.warning('We did not find a Suit with ID %s.' % suitId)
        #     return False
        atkAcc = atkType['acc']
        # suitAcc = SuitBattleGlobals.SuitAttributes[theSuit.dna.name]['acc'][theSuit.getLevel()]
        suitAcc = 0 # suitAcc does absolutely nothing.  It was supposedly intended to alter the attack accuracy by using the average of the attack and Cog's accuracy, but that is likely obtrusive.  I'm keeping the variable anyway because of what is printed.
        acc = atkAcc
        randChoice = random.randint(0, 99)
        if randChoice < acc:
            return True
        return False

    def suitAtkHit(self, suitId, atkType):
        return self.__suitAtkHit(self, suitId, atkType)

    def __suitAtkAffectsGroup(self, attack):
        atkType = attack[SUIT_ATK_COL]
        return atkType['group'] == SuitBattleGlobals.ATK_TGT_GROUP

    def __createSuitTargetList(self, attack):
        targetList = []

        if not attack[SUIT_ATK_COL]:
            return targetList

        if not self.__suitAtkAffectsGroup(attack):
            for targetIndex in attack[SUIT_TGT_COL]:
                if (
                    targetIndex < 0
                    or targetIndex >= len(
                        self.battle.activeToons
                    )
                ):
                    continue

                toonId = self.battle.activeToons[
                    targetIndex
                ]

                if self.__toonCanBeTargetedBySuit(
                    toonId,
                    attack
                ):
                    targetList.append(toonId)

        else:
            for toonId in self.battle.activeToons:
                if self.__toonCanBeTargetedBySuit(
                    toonId,
                    attack
                ):
                    targetList.append(toonId)

        return targetList

    def getRandomValidTargetSuitDigitRushJob(self):
        return self.__getRandomValidTargetSuitDigitRushJob()


    def getRandomValidTargetSuitDigitAttorney(self, excludeSuitId=None):
        return self.__getRandomValidTargetSuitDigitAttorney(
            excludeSuitId=excludeSuitId
        )


    def getRandomValidTargetSuitDigitPresident(self, excludeSuitId=None):
        return self.__getRandomValidTargetSuitDigitPresident(
            excludeSuitId=excludeSuitId
        )

    def getRandomValidTargetSuitDigitAttorney(self, excludeSuitId=None):
        return self.__getRandomValidTargetSuitDigitAttorney(
            excludeSuitId=excludeSuitId
        )


    def getRandomValidTargetSuitDigitErclaim(self, excludeSuitId=None):
        return self.__getRandomValidTargetSuitDigitErclaim(
            excludeSuitId=excludeSuitId
        )


    def getErfitTargetByHPPercentSacrifice(
            self,
            excludeSuitId=None,
            mode='lowest'):

        return self.__getErfitTargetByHPPercentSacrifice(
            excludeSuitId=excludeSuitId,
            mode=mode
        )


    def getRandomValidTargetSuitDigitVideographer(
            self,
            excludeSuitId=None):

        return self.__getRandomValidTargetSuitDigitVideographer(
            excludeSuitId=excludeSuitId
        )

    def getRandomValidTargetSuitDigitRadiographer(
            self,
            excludeSuitId=None):

        return self.__getRandomValidTargetSuitDigitRadiographer(
            excludeSuitId=excludeSuitId
        )



    def getRandomValidTargetSuitDigit(self, excludeSuitId=None):
        return self.__getRandomValidTargetSuitDigit(
            excludeSuitId=excludeSuitId
        )

    def createSuitTargetList(self, attack):
        return self.__createSuitTargetList(attack)


    def suitAtkHit(self, suitId, attack):
        return self.__suitAtkHit(suitId, attack)


    def removeLured(self, suitId):
        return self.__removeLured(suitId)


    def addSyphonHP(self, suitId, amount):
        return self.__addSyphonHP(suitId, amount)

    def __addSyphonHP(self, suitId, amount):
        amount = int(math.ceil(amount))
        if amount <= 0:
            return
        self.syphonHP[suitId] = self.syphonHP.get(suitId, 0) + amount

    def toonUsedBannedGag(self, toonId, track, level):
        conditionName = 'noGag_%s_%s' % (track, level)
        return self.toonHasCondition(toonId, conditionName)

    def getRandomSpecificGagBansForToon(
            self,
            toonId,
            amount=3,
            minLevel=3,
            maxLevel=7):

        possible = []
        toon = self.battle.getToon(toonId)

        for track in range(8):

            if not toon.hasTrackAccess(track):
                continue

            for level in range(minLevel, maxLevel + 1):

                if toon.inventory.numItem(track, level) <= 0:
                    continue

                possible.append((track, level))

        if not possible:
            return []

        amount = min(amount, len(possible))

        return random.sample(possible, amount)


    def __calcSuitAtkHpALT(self, attack):
        return self.suitAttackHpCalculator.calcSuitAtkHpALT(attack)

    def __calcSuitAtkHp(self, attack):
        return self.suitAttackHpCalculator.calcSuitAtkHp(attack)

    def __getToonHp(self, toonDoId):
        handle = self.battle.getToon(toonDoId)
        if handle != None:
            return handle.hp
        else:
            return 0

    def __getToonMaxHp(self, toonDoId):
        handle = self.battle.getToon(toonDoId)
        if handle != None:
            return handle.maxHp
        else:
            return 0

    def getRandomGagBanPerTrack(self, minLevel=3, maxLevel=7):
        bans = []

        for track in range(8):
            level = random.randint(minLevel, maxLevel)
            bans.append((track, level))

        return bans

    def applyRandomSpecificGagBans(self, toonId, turns=3):
        bans = self.getRandomGagBanPerTrack()

        for track, level in bans:
            conditionName = 'noGag_%s_%s' % (track, level)

            self.setToonCondition(
                toonId,
                conditionName,
                1,
                turns,
                'setBoth'
            )

        return bans

    def __applySuitAttackDamages(self, attack, theSuit):
        if APPLY_HEALTH_ADJUSTMENTS:
            for t in self.battle.activeToons:
                position = self.battle.activeToons.index(t)
                if attack[SUIT_HP_COL][position] <= 0:
                    continue
                if theSuit and getattr(getattr(theSuit, 'dna', None), 'name', None) == 'chainsaw':
                    attackName = ''
                    try:
                        attackName = attack[SUIT_ATK_COL].get('name', '')
                    except:
                        pass
                    if not attackName.startswith('ChainsawCoreDeadwood'):
                        multiplier = 1.0
                        if self.toonHasCondition(t, 'vulnerable'):
                            multiplier *= self.getToonConditionModifier(t, 'vulnerable')
                        if attackName.startswith('ChainsawCore') and self.toonHasCondition(t, 'markedwood'):
                            multiplier *= self.getToonConditionModifier(t, 'markedwood')
                        attack[SUIT_HP_COL][position] = int(math.ceil(attack[SUIT_HP_COL][position] * multiplier))
                toonHp = self.__getToonHp(t)
                if toonHp - attack[SUIT_HP_COL][position] <= 0:
                    if self.notify.getDebug():
                        self.notify.debug('Toon %d has died, removing' % t)
                    self.toonLeftBattle(t)
                    attack[TOON_DIED_COL] = attack[TOON_DIED_COL] | 1 << position
                self.toonHPAdjusts[t] -= math.ceil(attack[SUIT_HP_COL][position])

    def __suitCanAttack(self, suitId):
        theSuit = self.battle.findSuit(suitId)
        if self.__combatantDead(suitId, toon=0) or self.__suitIsLured(suitId) or self.suitHasCondition(suitId, 'cantAttack'):
            return 0
        elif theSuit.dna.name == 'hroller' and theSuit.currHP == 1:
            return 0
        return 1

    def __updateSuitAtkStat(self, toonId):
        if toonId in self.suitAtkStats:
            self.suitAtkStats[toonId] += 1
        else:
            self.suitAtkStats[toonId] = 1

    def __printSuitAtkStats(self):
        for currTgt in self.suitAtkStats.keys():
            if currTgt not in self.battle.activeToons:
                continue
            tgtPos = self.battle.activeToons.index(currTgt)

    from toontown.battle import SuitBattleGlobals

    def getSafeSuitLevel(self, suitName, wantedLevel):
        from toontown.battle import SuitBattleGlobals

        attributes = SuitBattleGlobals.SuitAttributes.get(suitName)
        if not attributes:
            self.notify.warning('No SuitAttributes for %s' % suitName)
            return 0

        hp = attributes.get('hp', ())
        if not hp:
            self.notify.warning('No hp tuple for %s' % suitName)
            return 0

        maxLevel = len(hp) - 1
        safeLevel = max(0, min(int(wantedLevel), maxLevel))

        if safeLevel != wantedLevel:
            self.notify.warning(
                'transformUnstableCog: %s wanted level %s but clamped to %s' %
                (suitName, wantedLevel, safeLevel)
            )

        return safeLevel

    def printSuitLevelPool(self, suitName):
        from toontown.battle import SuitBattleGlobals

        attrs = SuitBattleGlobals.SuitAttributes.get(suitName)
        if not attrs:
            self.notify.warning('No SuitAttributes for %s' % suitName)
            return

        hp = attrs.get('hp', ())
        self.notify.warning('%s hp pool length: %s' % (suitName, len(hp)))
        self.notify.warning('%s valid internal levels: 0-%s' % (suitName, len(hp) - 1))
        self.notify.warning('%s hp values: %s' % (suitName, hp))


    def transformUnstableCog(self, suit, actualLevel, newName):
        import random
        from toontown.suit import SuitDNA
        from toontown.battle import SuitBattleGlobals

        pool = ['foreman', 'supervis', 'clerk', 'clubpres', 'ovt']

        oldName = suit.dna.name


        dna = SuitDNA.SuitDNA()
        dna.newSuit(newName)

        oldPercent = float(suit.currHP) / max(1.0, float(suit.maxHP))

        # self.notify.warning(
        #     'TRANSFORM old=%s new=%s rel=%s actual=%s hpLen=%s' %
        #     (oldName, newName, 0, actualLevel, len(hpPool))
        # )

        # AI state update only
        suit.dna = dna
        suit.setLevel(actualLevel)

        newHP = max(1, int(suit.maxHP * oldPercent))
        suit.b_setHP(newHP)

    def getAbilityQueuedPreToon(self, suitId):
        return self.__getAbilityQueuedPreToon(suitId)


    def __getAbilityQueuedPreToon(self, suitId):
        '''
        This method is for use with making standard Cog attacks.  Attacks with specific parameters (e.g. cheats) should be created manually.  This method can work for extra attacks, though, as a generic extra attack can be made easily with this method that, quite franky, gets used often.
        '''
        theSuit = self.battle.findSuit(suitId)
        attack = getDefaultSuitAttack()
        attack[SUIT_ID_COL] = suitId
        # attack[SUIT_ATK_COL] = self.__calcSuitAtkType(theSuit)
        attack[SUIT_ATK_COL] = {'suitName': '',
                                    'name': 'AbilityQueuedPreToon',  # Ability Queue if Manager Cogs are unable to Cheat
                                    'animName': 'nothing',
                                    'hp': 0,
                                    'acc': 100,
                                    'freq': 0,
                                    'group': SuitBattleGlobals.ATK_TGT_SINGLE}
        attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
        if attack[SUIT_TGT_COL] == []:
            attack = getDefaultSuitAttack()
        attack[SUIT_HP_COL] = [-1 for i in xrange(len(self.battle.activeToons))]
        self.__calcSuitAtkHpALT(attack)
        if attack[SUIT_ATK_COL]:
            if self.__suitAtkAffectsGroup(attack):
                for currTgt in self.battle.activeToons:
                    self.__updateSuitAtkStat(currTgt)

            else:
                for currTgt in attack[SUIT_TGT_COL]:
                    self.__updateSuitAtkStat(self.battle.activeToons[currTgt])

        targets = self.__createSuitTargetList(attack)
        allTargetsDead = True
        for currTgt in targets:
            if self.__getToonHp(currTgt) > 0:
                allTargetsDead = False
                break

        if allTargetsDead:
            attack = getDefaultSuitAttack()
        if self.__attackHasHit(attack, suit=1):
            self.__applySuitAttackDamages(attack, self.battle.findSuit(attack[SUIT_ID_COL]))
        attack[SUIT_BEFORE_TOONS_COL] = 0
        return attack

    def __getAbilityQueued(self, suitId):
        '''
        This method is for use with making standard Cog attacks.  Attacks with specific parameters (e.g. cheats) should be created manually.  This method can work for extra attacks, though, as a generic extra attack can be made easily with this method that, quite franky, gets used often.
        '''
        theSuit = self.battle.findSuit(suitId)
        attack = getDefaultSuitAttack()
        attack[SUIT_ID_COL] = suitId
        # attack[SUIT_ATK_COL] = self.__calcSuitAtkType(theSuit)
        attack[SUIT_ATK_COL] = {'suitName': '',
                                    'name': 'AbilityQueued',  # Ability Queue if Manager Cogs are unable to Cheat
                                    'animName': 'nothing',
                                    'hp': 0,
                                    'acc': 100,
                                    'freq': 0,
                                    'group': SuitBattleGlobals.ATK_TGT_SINGLE}
        attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
        if attack[SUIT_TGT_COL] == []:
            attack = getDefaultSuitAttack()
        attack[SUIT_HP_COL] = [-1 for i in xrange(len(self.battle.activeToons))]
        self.__calcSuitAtkHpALT(attack)
        if attack[SUIT_ATK_COL]:
            if self.__suitAtkAffectsGroup(attack):
                for currTgt in self.battle.activeToons:
                    self.__updateSuitAtkStat(currTgt)

            else:
                for currTgt in attack[SUIT_TGT_COL]:
                    self.__updateSuitAtkStat(self.battle.activeToons[currTgt])

        targets = self.__createSuitTargetList(attack)
        allTargetsDead = True
        for currTgt in targets:
            if self.__getToonHp(currTgt) > 0:
                allTargetsDead = False
                break

        if allTargetsDead:
            attack = getDefaultSuitAttack()
        if self.__attackHasHit(attack, suit=1):
            self.__applySuitAttackDamages(attack, self.battle.findSuit(attack[SUIT_ID_COL]))
        attack[SUIT_BEFORE_TOONS_COL] = 0
        return attack

    def __getCheatAttack(self, suitId, attackId):
        '''
        This method is for use with making standard Cog attacks.  Attacks with specific parameters (e.g. cheats) should be created manually.  This method can work for extra attacks, though, as a generic extra attack can be made easily with this method that, quite franky, gets used often.
        '''
        theSuit = self.battle.findSuit(suitId)
        attack = getDefaultSuitAttack()
        attack[SUIT_ID_COL] = suitId
        # attack[SUIT_ATK_COL] = self.__calcSuitAtkType(theSuit)
        attack[SUIT_ATK_COL] = attackId
        attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
        if attack[SUIT_TGT_COL] == []:
            attack = getDefaultSuitAttack()
        attack[SUIT_HP_COL] = [-1 for i in xrange(len(self.battle.activeToons))]
        self.__calcSuitAtkHpALT(attack)
        if attack[SUIT_ATK_COL]:
            if self.__suitAtkAffectsGroup(attack):
                for currTgt in self.battle.activeToons:
                    self.__updateSuitAtkStat(currTgt)

            else:
                for currTgt in attack[SUIT_TGT_COL]:
                    self.__updateSuitAtkStat(self.battle.activeToons[currTgt])

        targets = self.__createSuitTargetList(attack)
        allTargetsDead = True
        for currTgt in targets:
            if self.__getToonHp(currTgt) > 0:
                allTargetsDead = False
                break

        if allTargetsDead:
            attack = getDefaultSuitAttack()
        if self.__attackHasHit(attack, suit=1):
            self.__applySuitAttackDamages(attack, self.battle.findSuit(attack[SUIT_ID_COL]))
        attack[SUIT_BEFORE_TOONS_COL] = 0
        return attack

    def __getLureRemovalByName(self, suitId, name):
        theSuit = self.battle.findSuit(suitId)
        attack = getDefaultSuitAttack()
        attack[SUIT_ID_COL] = suitId

        attack[SUIT_ATK_COL] = {
            'suitName': '',
            'name': name,
            'animName': 'nothing',
            'hp': 0,
            'acc': 100,
            'freq': 0,
            'group': SuitBattleGlobals.ATK_TGT_SINGLE
        }

        attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
        if attack[SUIT_TGT_COL] == []:
            attack = getDefaultSuitAttack()

        attack[SUIT_HP_COL] = [-1 for i in xrange(len(self.battle.activeToons))]

        self.__calcSuitAtkHpALT(attack)

        if attack[SUIT_ATK_COL]:
            if self.__suitAtkAffectsGroup(attack):
                for currTgt in self.battle.activeToons:
                    self.__updateSuitAtkStat(currTgt)
            else:
                for currTgt in attack[SUIT_TGT_COL]:
                    self.__updateSuitAtkStat(self.battle.activeToons[currTgt])

        targets = self.__createSuitTargetList(attack)
        allTargetsDead = True

        for currTgt in targets:
            if self.__getToonHp(currTgt) > 0:
                allTargetsDead = False
                break

        if allTargetsDead:
            attack = getDefaultSuitAttack()

        if self.__attackHasHit(attack, suit=1):
            self.__applySuitAttackDamages(
                attack,
                self.battle.findSuit(attack[SUIT_ID_COL])
            )

        attack[SUIT_BEFORE_TOONS_COL] = 0
        return attack

    def __getLureRemoval(self, suitId):
        '''
        This method is for use with making standard Cog attacks.  Attacks with specific parameters (e.g. cheats) should be created manually.  This method can work for extra attacks, though, as a generic extra attack can be made easily with this method that, quite franky, gets used often.
        '''
        theSuit = self.battle.findSuit(suitId)
        attack = getDefaultSuitAttack()
        attack[SUIT_ID_COL] = suitId
        # attack[SUIT_ATK_COL] = self.__calcSuitAtkType(theSuit)
        attack[SUIT_ATK_COL] = {'suitName': '',
                                    'name': 'LureRemoval',  # Lure Removal Movie
                                    'animName': 'nothing',
                                    'hp': 0,
                                    'acc': 100,
                                    'freq': 0,
                                    'group': SuitBattleGlobals.ATK_TGT_SINGLE}
        attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
        if attack[SUIT_TGT_COL] == []:
            attack = getDefaultSuitAttack()
        attack[SUIT_HP_COL] = [-1 for i in xrange(len(self.battle.activeToons))]
        self.__calcSuitAtkHpALT(attack)
        if attack[SUIT_ATK_COL]:
            if self.__suitAtkAffectsGroup(attack):
                for currTgt in self.battle.activeToons:
                    self.__updateSuitAtkStat(currTgt)

            else:
                for currTgt in attack[SUIT_TGT_COL]:
                    self.__updateSuitAtkStat(self.battle.activeToons[currTgt])

        targets = self.__createSuitTargetList(attack)
        allTargetsDead = True
        for currTgt in targets:
            if self.__getToonHp(currTgt) > 0:
                allTargetsDead = False
                break

        if allTargetsDead:
            attack = getDefaultSuitAttack()
        if self.__attackHasHit(attack, suit=1):
            self.__applySuitAttackDamages(attack, self.battle.findSuit(attack[SUIT_ID_COL]))
        attack[SUIT_BEFORE_TOONS_COL] = 0
        return attack

    def __getGenericSuitAttack(self, suitId):
        '''
        This method is for use with making standard Cog attacks.  Attacks with specific parameters (e.g. cheats) should be created manually.  This method can work for extra attacks, though, as a generic extra attack can be made easily with this method that, quite franky, gets used often.
        '''
        theSuit = self.battle.findSuit(suitId)
        if theSuit.dna.name == 'lgator':
            currentBossHealth = -1
            for s in self.battle.suits:
                if s.dna.name == 'stenog' or s.dna.name == 'sgoat' or s.dna.name == 'caseman':
                    currentBossHealth = s.currHP
            currentBossHealth3 = -1
            currentBossHealth4 = -1
            currentBossHealth5 = -1
            for s in self.battle.suits:
                if s.dna.name == 'caseman':
                    currentBossHealth3 = s.currHP
                if s.dna.name == 'sgoat':
                    currentBossHealth4 = s.currHP
                if s.dna.name == 'stenog':
                    currentBossHealth5 = s.currHP
            if currentBossHealth == -1 and not self.suitHasCondition(theSuit.doId, 'desperation'):
                self.setSuitCondition(theSuit.doId, 'desperationcalculator', 1, 100, 'setBoth')
            currentBossHealth3 = -1
            for s in self.battle.suits:
                if s.dna.name == 'caseman':
                    currentBossHealth3 = s.currHP
            if currentBossHealth3 == -1:
                self.setSuitCondition(theSuit.doId, 'deadcase', 1, 100, 'setBoth')
        if theSuit.dna.name == 'stenog':
            currentBossHealth = -1
            for s in self.battle.suits:
                if s.dna.name == 'lgator' or s.dna.name == 'sgoat' or s.dna.name == 'caseman':
                    currentBossHealth = s.currHP
            currentBossHealth3 = -1
            currentBossHealth4 = -1
            currentBossHealth5 = -1
            for s in self.battle.suits:
                if s.dna.name == 'caseman':
                    currentBossHealth3 = s.currHP
                if s.dna.name == 'lgator':
                    currentBossHealth4 = s.currHP
                if s.dna.name == 'sgoat':
                    currentBossHealth5 = s.currHP
            if currentBossHealth == -1 and not self.suitHasCondition(theSuit.doId, 'desperation'):
                self.setSuitCondition(theSuit.doId, 'desperationcalculator', 1, 100, 'setBoth')
            currentBossHealth3 = -1
            for s in self.battle.suits:
                if s.dna.name == 'caseman':
                    currentBossHealth3 = s.currHP
            if currentBossHealth3 == -1:
                self.setSuitCondition(theSuit.doId, 'deadcase', 1, 100, 'setBoth')
        if theSuit.dna.name == 'caseman':
            currentBossHealth = -1
            for s in self.battle.suits:
                if s.dna.name == 'stenog' or s.dna.name == 'sgoat' or s.dna.name == 'lgator':
                    currentBossHealth = s.currHP
            currentBossHealth3 = -1
            currentBossHealth4 = -1
            currentBossHealth5 = -1
            for s in self.battle.suits:
                if s.dna.name == 'sgoat':
                    currentBossHealth3 = s.currHP
                if s.dna.name == 'lgator':
                    currentBossHealth4 = s.currHP
                if s.dna.name == 'stenog':
                    currentBossHealth5 = s.currHP
            if currentBossHealth == -1 and not self.suitHasCondition(theSuit.doId, 'desperation'):
                self.setSuitCondition(theSuit.doId, 'desperationcalculator', 1, 100, 'setBoth')
            currentBossHealth3 = -1
            for s in self.battle.suits:
                if s.dna.name == 'caseman':
                    currentBossHealth3 = s.currHP
            if currentBossHealth3 == -1:
                self.setSuitCondition(theSuit.doId, 'deadcase', 1, 100, 'setBoth')
        if theSuit.dna.name == 'sgoat':
            currentBossHealth = -1
            for s in self.battle.suits:
                if s.dna.name == 'stenog' or s.dna.name == 'lgator' or s.dna.name == 'caseman':
                    currentBossHealth = s.currHP
            currentBossHealth3 = -1
            currentBossHealth4 = -1
            currentBossHealth5 = -1
            for s in self.battle.suits:
                if s.dna.name == 'caseman':
                    currentBossHealth3 = s.currHP
                if s.dna.name == 'lgator':
                    currentBossHealth4 = s.currHP
                if s.dna.name == 'stenog':
                    currentBossHealth5 = s.currHP
            if currentBossHealth == -1 and not self.suitHasCondition(theSuit.doId, 'desperation'):
                self.setSuitCondition(theSuit.doId, 'desperationcalculator', 1, 100, 'setBoth')
            currentBossHealth3 = -1
            for s in self.battle.suits:
                if s.dna.name == 'caseman':
                    currentBossHealth3 = s.currHP
            if currentBossHealth3 == -1:
                self.setSuitCondition(theSuit.doId, 'deadcase', 1, 100, 'setBoth')
        if theSuit.dna.name == 'phouse':
            x = self.TurnsElapsed
            currentBossHealth = -1
            for s in self.battle.suits:
                if s.dna.name == 'wtapper' or s.dna.name == 'bkeeper' or s.dna.name == 'ambass':
                    currentBossHealth = s.currHP
            if currentBossHealth == -1 and not self.suitHasCondition(theSuit.doId, 'desperation'):
                self.setSuitCondition(theSuit.doId, 'desperationcalculator', 1, 100, 'setBoth')
        if theSuit.dna.name == 'bkeeper':
            x = self.TurnsElapsed
            currentBossHealth = -1
            for s in self.battle.suits:
                if s.dna.name == 'wtapper' or s.dna.name == 'phouse' or s.dna.name == 'ambass':
                    currentBossHealth = s.currHP
            currentBossHealth3 = -1
            for s in self.battle.suits:
                if s.dna.name == 'phouse':
                    currentBossHealth3 = s.currHP
            if currentBossHealth3 == -1:
                self.setSuitCondition(theSuit.doId, 'deadpower', 1, 100, 'setBoth')
            if currentBossHealth == -1 and not self.suitHasCondition(theSuit.doId, 'desperation'):
                self.setSuitCondition(theSuit.doId, 'desperationcalculator', 1, 100, 'setBoth')
        if theSuit.dna.name == 'wtapper':
            x = self.TurnsElapsed
            currentBossHealth = -1
            for s in self.battle.suits:
                if s.dna.name == 'phouse' or s.dna.name == 'bkeeper' or s.dna.name == 'ambass':
                    currentBossHealth = s.currHP
            currentBossHealth3 = -1
            for s in self.battle.suits:
                if s.dna.name == 'phouse':
                    currentBossHealth3 = s.currHP
            if currentBossHealth3 == -1:
                self.setSuitCondition(theSuit.doId, 'deadpower', 1, 100, 'setBoth')
            if currentBossHealth == -1 and not self.suitHasCondition(theSuit.doId, 'desperation'):
                self.setSuitCondition(theSuit.doId, 'desperationcalculator', 1, 100, 'setBoth')
        if theSuit.dna.name == 'ambass':
            x = self.TurnsElapsed
            currentBossHealth = -1
            for s in self.battle.suits:
                if s.dna.name == 'wtapper' or s.dna.name == 'bkeeper' or s.dna.name == 'phouse':
                    currentBossHealth = s.currHP
            currentBossHealth3 = -1
            for s in self.battle.suits:
                if s.dna.name == 'phouse':
                    currentBossHealth3 = s.currHP
            if currentBossHealth3 == -1:
                self.setSuitCondition(theSuit.doId, 'deadpower', 1, 100, 'setBoth')
            if currentBossHealth == -1 and not self.suitHasCondition(theSuit.doId, 'desperation'):
                self.setSuitCondition(theSuit.doId, 'desperationcalculator', 1, 100, 'setBoth')
        if theSuit.dna.name == 'liquid':
            x = self.TurnsElapsed
            currentBossHealth = -1
            for s in self.battle.suits:
                if s.dna.name == 'rkeeper' or s.dna.name == 'dking' or s.dna.name == 'cdirector':
                    currentBossHealth = s.currHP
            if currentBossHealth == -1 and not self.suitHasCondition(theSuit.doId, 'desperation'):
                self.setSuitCondition(theSuit.doId, 'desperationcalculator', 1, 100, 'setBoth')
        if theSuit.dna.name == 'rkeeper':
            x = self.TurnsElapsed
            currentBossHealth2 = -1
            for s in self.battle.suits:
                if s.dna.name == 'cbutcher':
                    currentBossHealth2 = s.currHP
            currentBossHealth = -1
            for s in self.battle.suits:
                if s.dna.name == 'liquid' or s.dna.name == 'dking' or s.dna.name == 'cdirector':
                    currentBossHealth = s.currHP
            if currentBossHealth == -1 and not self.suitHasCondition(theSuit.doId, 'desperation'):
                self.setSuitCondition(theSuit.doId, 'desperationcalculator', 1, 100, 'setBoth')
            if currentBossHealth2 == -1 and x % 3 == 0:
                self.setSuitCondition(theSuit.doId, 'phantomEntrycalculator', 1, 10, 'setBoth')
        if theSuit.dna.name == 'dking':
            x = self.TurnsElapsed
            currentBossHealth = -1
            for s in self.battle.suits:
                if s.dna.name == 'liquid' or s.dna.name == 'rkeeper' or s.dna.name == 'cdirector':
                    currentBossHealth = s.currHP
            if currentBossHealth == -1 and not self.suitHasCondition(theSuit.doId, 'desperation'):
                self.setSuitCondition(theSuit.doId, 'desperationcalculator', 1, 100, 'setBoth')
        if theSuit.dna.name == 'cdirector':
            x = self.TurnsElapsed
            currentBossHealth = -1
            for s in self.battle.suits:
                if s.dna.name == 'liquid' or s.dna.name == 'rkeeper' or s.dna.name == 'dking':
                    currentBossHealth = s.currHP
            if currentBossHealth == -1 and not self.suitHasCondition(theSuit.doId, 'desperation'):
                self.setSuitCondition(theSuit.doId, 'desperationcalculator', 1, 100, 'setBoth')
        if theSuit.dna.name == 'videog':
            x = self.TurnsElapsed
            currentBossHealth = -1
            for s in self.battle.suits:
                if s.dna.name == 'bcaster':
                    currentBossHealth = s.currHP
            currentBossHealth2 = -1
            currentBossHealth3 = -1
            for s in self.battle.suits:
                if s.dna.name == 'mh2' or s.dna.name == 'std2' or s.dna.name == 'cnd2':
                    currentBossHealth2 = s.currHP
                if s.dna.name == 'director' or s.dna.name == 'fmaker' or s.dna.name == 'choreo' or s.dna.name == 'cinema':
                    currentBossHealth3 = s.currHP
            if currentBossHealth == -1 and not self.suitHasCondition(theSuit.doId,  'silhouettespawn') and self.suitHasCondition(theSuit.doId, 'phase3') and len(self.battle.activeSuits) < 7:
                self.setSuitCondition(theSuit.doId, 'silhouettespawn', 1, 1, 'setBoth')
            if currentBossHealth2 >= 1 and (x + 1) % 2 == 0:
                self.setSuitCondition(theSuit.doId, 'hollywoodcalculator', 1, 1, 'setBoth')
            if currentBossHealth3 == -1:
                self.setSuitCondition(theSuit.doId, 'immunecalculator', 1, 1, 'setBoth')
        if theSuit.dna.name == 'radiog':
            x = self.TurnsElapsed
            currentBossHealth = -1
            for s in self.battle.suits:
                if s.dna.name == 'ubuster' or s.dna.name == 'hustle' or s.dna.name == 'safesupervis':
                    currentBossHealth = s.currHP
            if currentBossHealth == -1 and not self.suitHasCondition(theSuit.doId, 'desperation'):
                self.setSuitCondition(theSuit.doId, 'desperationcalculator', 1, 100, 'setBoth')
        if theSuit.dna.name == 'hustle':
            x = self.TurnsElapsed
            currentBossHealth = -1
            for s in self.battle.suits:
                if s.dna.name == 'ubuster' or s.dna.name == 'safesupervis' or s.dna.name == 'radiog':
                    currentBossHealth = s.currHP
            if currentBossHealth == -1 and not self.suitHasCondition(theSuit.doId, 'desperation'):
                self.setSuitCondition(theSuit.doId, 'desperationcalculator', 1, 100, 'setBoth')
        if theSuit.dna.name == 'ubuster':
            x = self.TurnsElapsed
            currentBossHealth = -1
            for s in self.battle.suits:
                if s.dna.name == 'safesupervis' or s.dna.name == 'hustle' or s.dna.name == 'radiog':
                    currentBossHealth = s.currHP
            if currentBossHealth == -1 and not self.suitHasCondition(theSuit.doId, 'desperation'):
                self.setSuitCondition(theSuit.doId, 'desperationcalculator', 1, 100, 'setBoth')
        if theSuit.dna.name == 'bookkeep':
            x = self.TurnsElapsed
            currentBossHealth = -1
            for s in self.battle.suits:
                if s.dna.name == 'treasure' or s.dna.name == 'liquidr' or s.dna.name == 'racket':
                    currentBossHealth = s.currHP
            if currentBossHealth == -1 and not self.suitHasCondition(theSuit.doId, 'desperation'):
                self.setSuitCondition(theSuit.doId, 'desperationcalculator', 1, 100, 'setBoth')
        if theSuit.dna.name == 'liquidr':
            x = self.TurnsElapsed
            currentBossHealth = -1
            for s in self.battle.suits:
                if s.dna.name == 'bookkeep' or s.dna.name == 'treasure' or s.dna.name == 'racket':
                    currentBossHealth = s.currHP
            if currentBossHealth == -1 and not self.suitHasCondition(theSuit.doId, 'desperation'):
                self.setSuitCondition(theSuit.doId, 'desperationcalculator', 1, 100, 'setBoth')
        if theSuit.dna.name == 'racket':
            x = self.TurnsElapsed
            currentBossHealth = -1
            for s in self.battle.suits:
                if s.dna.name == 'bookkeep' or s.dna.name == 'liquidr' or s.dna.name == 'treasure':
                    currentBossHealth = s.currHP
            if currentBossHealth == -1 and not self.suitHasCondition(theSuit.doId, 'desperation'):
                self.setSuitCondition(theSuit.doId, 'desperationcalculator', 1, 100, 'setBoth')
        if theSuit.dna.name == 'treasure':
            x = self.TurnsElapsed
            currentBossHealth = -1
            for s in self.battle.suits:
                if s.dna.name == 'bookkeep' or s.dna.name == 'liquidr' or s.dna.name == 'racket':
                    currentBossHealth = s.currHP
            if currentBossHealth == -1 and not self.suitHasCondition(theSuit.doId, 'desperation'):
                self.setSuitCondition(theSuit.doId, 'desperationcalculator', 1, 100, 'setBoth')
        if theSuit.dna.name == 'safesupervis':
            x = self.TurnsElapsed
            currentBossHealth = -1
            for s in self.battle.suits:
                if s.dna.name == 'ubuster' or s.dna.name == 'hustle' or s.dna.name == 'radiog':
                    currentBossHealth = s.currHP
            if currentBossHealth == -1 and not self.suitHasCondition(theSuit.doId, 'desperation'):
                self.setSuitCondition(theSuit.doId, 'desperationcalculator', 1, 100, 'setBoth')
        attack = getDefaultSuitAttack()
        attack[SUIT_ID_COL] = suitId
        # attack[SUIT_ATK_COL] = self.__calcSuitAtkType(theSuit)
        if theSuit.dna.name == 'supervis' and theSuit.getActualLevel() == 22:  # Compounding Mint Supervisor
            attack[SUIT_ATK_COL] = {'suitName': theSuit.dna.name,
                                                        'name': 'MintCompoundingInterest',
                                                        'animName': 'magic2',
                                                        'hp': 0,
                                                        'acc': 100,
                                                        'freq': 0,
                                                        'group': SuitBattleGlobals.ATK_TGT_GROUP}
        elif theSuit.dna.name == 'foreman' and theSuit.getActualLevel() == 24:
            attack[SUIT_ATK_COL] = {'suitName': theSuit.dna.name,
                                                        'name': 'ForemanRedTape',  # Foreman Red Tape
                                                        'animName': 'throw-object',
                                                        'hp': 0,
                                                        'acc': 100,
                                                        'freq': 0,  # Professor Control: I do not know how relevant attack frequency is, but keep it anyway.
                                                        'group': SuitBattleGlobals.ATK_TGT_DOUBLE}
        elif theSuit.dna.name == 'foreman' and theSuit.getActualLevel() == 21:
            attack[SUIT_ATK_COL] = {'suitName': theSuit.dna.name,
                                                        'name': 'ForemanBurning',  # Foreman Burning
                                                        'animName': 'magic3-alt',
                                                        'hp': 0,
                                                        'acc': 100,
                                                        'freq': 0,  # Professor Control: I do not know how relevant attack frequency is, but keep it anyway.
                                                        'group': SuitBattleGlobals.ATK_TGT_DOUBLE}
        elif theSuit.dna.name == 'clubpres' and theSuit.getActualLevel() == 22:
            attack[SUIT_ATK_COL] = {'suitName': theSuit.dna.name,
                                                        'name': 'PresidentDriver',  # Club President Driver
                                                        'animName': 'golf-club-swing',
                                                        'hp': 0,
                                                        'acc': 100,
                                                        'freq': 0,  # Professor Control: I do not know how relevant attack frequency is, but keep it anyway.
                                                        'group': SuitBattleGlobals.ATK_TGT_DOUBLE}
        else:
            attack[SUIT_ATK_COL] = SuitBattleGlobals.getSuitAttack(theSuit.dna.name, theSuit.getLevel())  # Professor Control: __calcSuitAtkType() is no longer used, but that has desperation code.  TODO: Find a new, possibly neater, way to pull off desperation.
        attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
        if attack[SUIT_TGT_COL] == []:
            attack = getDefaultSuitAttack()
        attack[SUIT_HP_COL] = [-1 for i in xrange(len(self.battle.activeToons))]
        if theSuit.dna.name == 'hroller2':
            self.__calcSuitAtkHpALT(attack)
        else:
            self.__calcSuitAtkHp(attack)
        if attack[SUIT_ATK_COL]:
            if self.__suitAtkAffectsGroup(attack):
                for currTgt in self.battle.activeToons:
                    self.__updateSuitAtkStat(currTgt)

            else:
                for currTgt in attack[SUIT_TGT_COL]:
                    self.__updateSuitAtkStat(self.battle.activeToons[currTgt])

        targets = self.__createSuitTargetList(attack)
        allTargetsDead = True
        for currTgt in targets:
            if self.__getToonHp(currTgt) > 0:
                allTargetsDead = False
                break

        if allTargetsDead:
            attack = getDefaultSuitAttack()
        if self.__attackHasHit(attack, suit=1):
            self.__applySuitAttackDamages(attack, self.battle.findSuit(attack[SUIT_ID_COL]))
        attack[SUIT_BEFORE_TOONS_COL] = 0
        return attack

    def __getPerToonCheatAttack(self, suitId, targetIndex, attackId):
        attack = getDefaultSuitAttack()
        attack[SUIT_ID_COL] = suitId
        attack[SUIT_ATK_COL] = attackId
        attack[SUIT_TGT_COL] = [targetIndex]
        attack[SUIT_HP_COL] = [-1 for i in xrange(len(self.battle.activeToons))]

        self.__calcSuitAtkHpALT(attack)

        suit = self.battle.findSuit(suitId)
        if self.__attackHasHit(attack, suit=1):
            self.__applySuitAttackDamages(attack, suit)

        attack[SUIT_BEFORE_TOONS_COL] = 0
        return attack

    def __getToonEffectiveHp(self, toonId):
        hp = self.__getToonHp(toonId)

        if toonId in self.toonHPAdjusts:
            hp += self.toonHPAdjusts[toonId]

        return hp

    def __toonCanBeTargetedBySuit(
        self,
        toonId,
        attack=None,
        ignoreRecentTarget=False):

        attackName = None

        if attack and attack[SUIT_ATK_COL]:
            attackName = attack[SUIT_ATK_COL].get(
                'name'
            )

        # Hidden Toons remain completely untargetable.
        if self.toonHasCondition(
                toonId,
                'hidden') and not attackName in [
                    'SoakRemoval',
                    'LureRemoval',
                    'AbsorbMovieLure',
                    'AbsorbMovieThrow',
                    'AbsorbMovieSquirt',
                    'AbsorbMovieZap',
                    'AbsorbMovieSound',
                    'AbsorbMovieDrop',
                    'AbsorbMovieLevelLure',
                    'PacesetterComeOn',
                    'PacesetterContentSync',
                    'AbsorbMovieLevelThrow',
                    'AbsorbMovieLevelSquirt',
                    'AbsorbMovieLevelZap',
                    'AbsorbMovieLevelSound',
                    'AbsorbMovieLevelDrop',
                    'ScapegoatEnraged',
                    'ScapegoatShieldsUp',
                    'ScapegoatRageBuilding',
                    'ComboThrow',
                    'ComboSquirt',
                    'ComboDrop',
                    'AttorneyChrono',
                    'SyphonMovie',
                    'DamageMovie',
                    'LureRemovalPreToon',
                    'Desperation',
                    'Desperation2',
                    'ContingencyMarkRevisedFiling',
                    'LureRemovalHeal',
                    'CalculatingFees',
                    'ContingencyRiskThresholdBreach',
                    'OilRemoval',
                    'MarkRemoval',
                    'LureRemovalTrap',
                    'LureRemovalLure',
                    'LureRemovalSound',
                    'LureRemovalThrow',
                    'LureRemovalSquirt',
                    'LureRemovalZap',
                    'ScapegoatBarnyardBash', 'ErfitHydrationCheck', 'ErfitHydrationCheckRevert', 'PowerhouseGroundbreakerRevert', 'PowerhouseGroundbreaker', 'ScapegoatGavel',
                    'LureRemovalDrop',
                    'AbilityQueued',
                    'ErfitHydrationCheckRevert',
                    'ErfitHydrationCheck',
                    'ScapegoatGavel',
                    'PowerhouseGroundbreakerRevert',
                    'AbilityQueuedPreToon',
                ]:

            return False

        recentTargetCondition = (
            SUIT_ATTACK_RECENT_TARGET_CONDITIONS.get(
                attackName
            )
        )

        # if (
        #     recentTargetCondition
        #     and not ignoreRecentTarget
        #     and self.toonHasCondition(
        #         toonId,
        #         recentTargetCondition)
        # ):
        #     return False

        return True

    def __appendToonConditionDamageAndRetaliation(self, condition, damage, damageMovie=None,
                                             retaliationMovie=None,
                                             retaliatorNames=[],
                                             retaliateAtTurns=None,
                                             retaliations=None):
        sourceSuit = None

        if retaliations is None:
            retaliations = []

        if retaliatorNames is None:
            retaliatorNames = []

        for suit in self.battle.activeSuits:
            if suit.currHP > 0:
                sourceSuit = suit
                break

        if sourceSuit is None:
            return

        for toonId in self.battle.activeToons:
            if self.__getToonHp(toonId) <= 0:
                continue

            if not self.toonHasCondition(toonId, condition):
                continue

            if damageMovie == 'PowerhouseBurnDamage' and self.toonHasCondition(toonId, 'hidden'):
                continue

            turnsLeft = self.getToonConditionTurns(toonId, condition)

            targetIndex = self.battle.activeToons.index(toonId)

            if damageMovie:
                dotAttack = self.__getPerToonCheatAttack(sourceSuit.doId, targetIndex, {
                    'suitName': sourceSuit.dna.name,
                    'name': damageMovie,
                    'animName': 'nothing',
                    'hp': damage,
                    'acc': 100,
                    'freq': 0,
                    'group': SuitBattleGlobals.ATK_TGT_SINGLE
                })
                if dotAttack[SUIT_ATK_COL]:
                    self.battle.suitAttacks.append(dotAttack)

                # # Save the damage that __getCheatAttack already calculated.
                # calculatedHp = dotAttack[SUIT_HP_COL]

                # # Retarget to this specific toon.
                # dotAttack[SUIT_TGT_COL] = [targetIndex]
                # dotAttack[SUIT_HP_COL] = [-1 for i in xrange(len(self.battle.activeToons))]
                # dotAttack[SUIT_HP_COL][targetIndex] = calculatedHp[targetIndex]

                # self.battle.suitAttacks.append(dotAttack)

                # if damage > 0:
                #     self.__applySuitAttackDamages(dotAttack, sourceSuit)

            shouldRetaliate = retaliationMovie is not None

            if retaliateAtTurns is not None:
                shouldRetaliate = shouldRetaliate and turnsLeft in retaliateAtTurns

            if retaliations:
                for rule in retaliations:
                    ruleTurns = rule.get('turns', retaliateAtTurns)

                    if ruleTurns is not None and turnsLeft not in ruleTurns:
                        continue

                    for suit in self.battle.activeSuits:
                        if suit.currHP <= 0:
                            continue

                        if suit.dna.name not in rule.get('suitNames', []):
                            continue

                        requiredLevel = rule.get('actualLevel')

                        if requiredLevel is not None:
                            if suit.getActualLevel() != requiredLevel:
                                continue

                        canAttack = self.__suitCanAttack(suit.doId)

                        if canAttack or suit.dna.name in ('wtapper', 'safesupervis') and suit.currHP > 0:
                            retaliation = self.__getPerToonCheatAttack(suit.doId, targetIndex, {
                                'suitName': suit.dna.name,
                                'name': rule['movie'],
                                'animName': rule.get('animName', 'nothing'),
                                'hp': rule.get('hp', 0),
                                'acc': 100,
                                'freq': 0,
                                'group': SuitBattleGlobals.ATK_TGT_SINGLE
                            })
                            if self.suitHasCondition(suit.doId, 'unlureSuit') and not self.suitHasCondition(suit.doId, 'sounded'):
                                attack = self.__getLureRemoval(suit.doId)
                                if attack[SUIT_ATK_COL]:
                                    self.battle.suitAttacks.append(attack)
                            if suit.currHP > 0:
                                if retaliation[SUIT_ATK_COL]:
                                    self.battle.suitAttacks.append(retaliation)

                            # retaliation[SUIT_TGT_COL] = [targetIndex]
                            # retaliation[SUIT_HP_COL] = [-1 for i in xrange(len(self.battle.activeToons))]
                            # retaliation[SUIT_HP_COL][targetIndex] = rule.get('hp', 0)

                            # if retaliation[SUIT_HP_COL][targetIndex] > 0:
                            #     self.__applySuitAttackDamages(retaliation, suit)

                            # self.battle.suitAttacks.append(retaliation)

                        else:
                            queueCondition = rule.get('queueCondition')

                            if queueCondition:
                                self.setSuitCondition(suit.doId, queueCondition, 1, 2, 'setBoth')

                                if suit.currHP > 0 and not canAttack and not suit.dna.name == 'hrollers':
                                    attack = self.__getAbilityQueued(suit.doId)
                                    if attack[SUIT_ATK_COL]:
                                        self.battle.suitAttacks.append(attack)


    def calculateRoundAttorney(self):
        self.__calculateAttorneyRemand()

    def calculateAttorneyTargetCheck(self):
        for suit in self.battle.activeSuits:
            suitId = suit.doId

            # if suit.dna.name == 'clerk' and suit.getActualLevel() == 20 and suit.currHP > 0:
            #     self.setSuitCondition(suitId, 'targetCheckCondition', self.__getRandomValidTargetSuitDigitAttorney(excludeSuitId=suitId), 1, 'setBoth')

    # def calculateAttorneyRemand(self):
    #     x = self.TurnsElapsed
    #     for i in xrange(len(self.battle.activeSuits)):
    #         suitId = self.battle.activeSuits[i].doId
    #         if self.battle.activeSuits[i].dna.name == 'clerk' and self.battle.activeSuits[i].getActualLevel() == 20:  # Head Attorney
    #             if self.battle.activeSuits[i].currHP > 0:
    #                 result = self.getSuitConditionModifier(suitId, 'targetCheckCondition')
    #                 targetSuit = self.battle.activeSuits[result]
    #                 self.battle.swapSuitVisualIndexes(suitId, targetSuit.doId)
    #             # if not self.suitHasCondition(suitId, 'sounded') and self.suitHasCondition(suitId, 'unlureSuit'):
    #             #     attack = self.__getLureRemoval(suitId)
    #             #     if attack[SUIT_ATK_COL]:
                        # self.battle.suitAttacks.append(attack)
    #             # if self.battle.activeSuits[i].currHP > 0 and (self.suitHasCondition(suitId, 'targetCheckCondition') and self.getSuitConditionModifier(suitId, 'targetCheckCondition') > -1):
    #             #     attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
    #             #                                                 'name': 'AttorneyRemand',
    #             #                                                 'animName': 'nothing',
    #             #                                                 'hp': 0,
    #             #                                                 'acc': 100,
    #             #                                                 'freq': 0,
    #             #                                                 'group': SuitBattleGlobals.ATK_TGT_SINGLE})
    #             #     if attack[SUIT_ATK_COL]:
                        # self.battle.suitAttacks.append(attack)

    def getPerToonCheatAttack(self, suitId, targetIndex, attackInfo):
        return self.__getPerToonCheatAttack(
            suitId, targetIndex,
            attackInfo
        )

    def getLureRemovalPreToon(self, suitId):
        return self.__getLureRemovalPreToon(suitId)


    def getLureRemovalHeal(self, suitId):
        return self.__getLureRemovalHeal(suitId)


    def getLureRemovalTrap(self, suitId):
        return self.__getLureRemovalTrap(suitId)


    def getLureRemovalLure(self, suitId):
        return self.__getLureRemovalLure(suitId)

    def getLureRemoval(self, suitId):
        return self.__getLureRemoval(suitId)


    def getLureRemovalSound(self, suitId):
        return self.__getLureRemovalSound(suitId)


    def getLureRemovalThrow(self, suitId):
        return self.__getLureRemovalThrow(suitId)


    def getLureRemovalSquirt(self, suitId):
        return self.__getLureRemovalSquirt(suitId)


    def getLureRemovalZap(self, suitId):
        return self.__getLureRemovalZap(suitId)


    def getLureRemovalDrop(self, suitId):
        return self.__getLureRemovalDrop(suitId)


    def __getLureRemovalPreToon(self, suitId):
        attack = self.__getLureRemovalByName(suitId, 'LureRemovalPreToon')
        attack[SUIT_BEFORE_TOONS_COL] = 1
        return attack

    def __getLureRemovalHeal(self, suitId):
        return self.__getLureRemovalByName(suitId, 'LureRemovalHeal')

    def __getLureRemovalTrap(self, suitId):
        return self.__getLureRemovalByName(suitId, 'LureRemovalTrap')

    def __getLureRemovalLure(self, suitId):
        return self.__getLureRemovalByName(suitId, 'LureRemovalLure')

    def __getLureRemovalSound(self, suitId):
        return self.__getLureRemovalByName(suitId, 'LureRemovalSound')

    def __getLureRemovalThrow(self, suitId):
        return self.__getLureRemovalByName(suitId, 'LureRemovalThrow')

    def __getLureRemovalSquirt(self, suitId):
        return self.__getLureRemovalByName(suitId, 'LureRemovalSquirt')

    def __getLureRemovalZap(self, suitId):
        return self.__getLureRemovalByName(suitId, 'LureRemovalZap')

    def __getLureRemovalDrop(self, suitId):
        return self.__getLureRemovalByName(suitId, 'LureRemovalDrop')


    def __updateLureTimeouts(self):
        noLongerLured = []
        for currLuredSuit in self.currentlyLuredSuits.keys():
            self.__incLuredCurrRound(currLuredSuit)
            if self.__luredMaxRoundsReached(currLuredSuit) or self.__luredWakeupTime(currLuredSuit):
                noLongerLured.append(currLuredSuit)


        for currLuredSuit in noLongerLured:
            self.__removeLured(currLuredSuit)

    def __updateWetTimeouts(self):
        noLongerWet = []
        for currentlyWetSuit in self.currentlyWetSuits.keys():
            self.__incWetCurrRound(currentlyWetSuit)
            if self.__wetMaxRoundsReached(currentlyWetSuit):
                noLongerWet.append(currentlyWetSuit)

        for currentlyWetSuit in noLongerWet:
            self.__removeWet(currentlyWetSuit)

    def __updateEnragedTimeouts(self):
        noLongerEnraged = []
        for currentlyEnragedSuit in self.currentlyEnragedSuits.keys():
            self.__incEnragedCurrRound(currentlyEnragedSuit)
            if self.__enragedMaxRoundsReached(currentlyEnragedSuit):
                noLongerEnraged.append(currentlyEnragedSuit)

        for currentlyEnragedSuit in noLongerEnraged:
            self.__removeEnraged(currentlyEnragedSuit)

    def __updateAbsorbingTimeouts(self):
        noLongerAbsorbing = []
        for currentlyAbsorbingSuit in self.currentlyAbsorbingSuits.keys():
            self.__incAbsorbingCurrRound(currentlyAbsorbingSuit)
            if self.__absorbingMaxRoundsReached(currentlyAbsorbingSuit):
                noLongerAbsorbing.append(currentlyAbsorbingSuit)

        for currentlyAbsorbingSuit in noLongerAbsorbing:
            self.__removeAbsorbing(currentlyAbsorbingSuit)

    def __initRound(self):
        if CLEAR_SUIT_ATTACKERS:
            self.SuitAttackers = {}
        self.toonAtkOrder = []
        attacks = findToonAttack(self.battle.activeToons, self.battle.toonAttacks, PETSOS)
        for atk in attacks:
            self.toonAtkOrder.append(atk[TOON_ID_COL])

        attacks = findToonAttack(self.battle.activeToons, self.battle.toonAttacks, FIRE)
        for atk in attacks:
            self.toonAtkOrder.append(atk[TOON_ID_COL])
        
        attacks = findToonAttack(self.battle.activeToons, self.battle.toonAttacks, SUE)
        for atk in attacks:
            self.toonAtkOrder.append(atk[TOON_ID_COL])

        for track in xrange(HEAL, DROP + 1):
            attacks = findToonAttack(self.battle.activeToons, self.battle.toonAttacks, track)
            if track == TRAP:
                sortedTraps = []
                for atk in attacks:
                    if atk[TOON_TRACK_COL] == TRAP:
                        sortedTraps.append(atk)

                for atk in attacks:
                    if atk[TOON_TRACK_COL] == NPCSOS:
                        sortedTraps.append(atk)

                attacks = sortedTraps
            for atk in attacks:
                self.toonAtkOrder.append(atk[TOON_ID_COL])

        specials = findToonAttack(self.battle.activeToons, self.battle.toonAttacks, NPCSOS)
        toonsHit = 0
        cogsMiss = 0
        for special in specials:
            npc_track, npc_level, npc_hp, npc_rarity = NPCToons.getNPCTrackLevelHpRarity(special[TOON_TGT_COL])
            if npc_track == NPC_TOONS_HIT:
                rounds = 3
                if self.roundsToonsHit < rounds:
                    self.roundsToonsHit = rounds
                    self.toonsAlwaysHit = 1
                    toonsHit = 1
                else:
                    self.toonsAlwaysHit = 1
                    toonsHit = 1
            elif npc_track == NPC_COGS_MISS:
                rounds = 3
                if self.roundsCogsMiss < rounds:
                    self.roundsCogsMiss = rounds
                    self.suitsAlwaysMiss = 1
                    cogsMiss = 1
                else:
                    self.suitsAlwaysMiss = 1
                    cogsMiss = 1
            elif npc_track == NPC_DAMAGE_BOOST:
                lvToDict = (
                'healBoost', 'trapBoost', 'lureBoost', 'throwBoost', 'squirtBoost', 'zapBoost',  'soundBoost', 'dropBoost',
                'allGagBoost')
                for t in self.battle.activeToons:
                    toon = self.battle.getToon(t)
                    if toon != None:
                        self.setToonCondition(toon.doId, lvToDict[npc_level], npc_hp, 3, 'setBoth')
                        self.setToonCondition(toon.doId, 'noSOS', 1, 2, 'setBoth')
                        self.setToonCondition(toon.doId, 'noFires', 1, 2, 'setBoth')
                      ##  self.setToonCondition(toon.doId, 'noUnites', 1, 2, 'setBoth')
                        # use alternate both because we want a better SOS card to replace a worse one
        if self.roundsToonsHit > 0:
           toonsHit =1
        if self.roundsCogsMiss > 0:
           cogsMiss =1

        self.toonHPAdjusts = {}
        for t in self.battle.activeToons:
            self.toonHPAdjusts[t] = 0

        self.__clearBonuses()
        self.__updateActiveToons()
        self.delayedUnlures = []
        self.__initTraps()
        self.successfulLures = {}
        return (toonsHit, cogsMiss)

    def __calculateToonTrackPhase(self, track):
        self.__calculateToonAttacksForTracks([track])
        self.__postProcessToonAttacksForTracks([track])

        if track == HEAL:
            self.tracksCalculator.calculateSuitAttacksAfterHeal()
        elif track == TRAP:
            self.tracksCalculator.calculateSuitAttacksAfterTrap()
        elif track == LURE:
            self.tracksCalculator.calculateSuitAttacksAfterLure()
        elif track == THROW:
            self.tracksCalculator.calculateSuitAttacksAfterThrow()
        elif track == SQUIRT:
            self.tracksCalculator.calculateSuitAttacksAfterSquirt()
        elif track == ZAP:
            self.tracksCalculator.calculateSuitAttacksAfterZap()
        elif track == SOUND:
            self.tracksCalculator.calculateSuitAttacksAfterSound()
        elif track == DROP:
            self.tracksCalculator.calculateSuitAttacksAfterDrop()

    def calculateRound(self):
        # self.printSuitLevelPool('foreman')
        # self.printSuitLevelPool('supervis')
        # self.printSuitLevelPool('clerk')
        # self.printSuitLevelPool('clubpres')
        # self.printSuitLevelPool('ovt')
        self.hustlerHits *= 0
        self.deadSuits *= 0
        self.contingencyThresholds *= 0
        self.governaughtCogs *= 0
        self.countErclaimHP *= 0
        self.countErfitHP *= 0
        self.interestMultiplier += 2
        self.absorbDamage = 0
        self.absorbDamageRecordkeeper = 0

        for track in self.absorbDamageByTrack:
            self.absorbDamageByTrack[track] = 0

        for track in self.levelDamageByTrack:
            self.levelDamageByTrack[track] = 0
        longest = max(len(self.battle.activeToons), len(self.battle.activeSuits))
        for t in self.battle.activeToons:
            for j in xrange(longest):
                self.battle.toonAttacks[t][TOON_HP_COL].append(-1)
                self.battle.toonAttacks[t][TOON_KBBONUS_COL].append(-1)

        #for i in xrange(6):'rkeeper
           # for j in xrange(len(self.battle.activeToons)):
             #   self.battle.suitAttacks[i][SUIT_HP_COL].append(-1)

        toonsHit, cogsMiss = self.__initRound()
        for suit in self.battle.activeSuits:
            if suit.isGenerated():
                if suit.dna.name == 'erfit':
                    if suit.getSkeleRevives() == 0:
                        self.setSuitCondition(suit.doId, 'vulnerablevideographer', 3.0, -1, 'setBoth')
                if self.suitHasCondition(suit.doId, 'battleSpeed'):
                    self.setSuitCondition(suit.doId, 'battleSpeed', (self.getSuitConditionModifier(suit.doId, 'battleSpeed')), -1, 'setBoth')
                if suit.dna.name == 'cbutcher':
                    if not self.suitHasCondition(suit.doId, 'phantomCounter'):
                        self.setSuitCondition(suit.doId, 'phantomCounter', 1, 5, 'setBoth')
                if suit.dna.name == 'ambass':
                    if not self.suitHasCondition(suit.doId, 'ambassadorOverconfidence') and not self.suitHasCondition(suit.doId, 'phase3'):
                        self.setSuitCondition(suit.doId, 'ambassadorOverconfidence', 1, 5, 'setBoth')
                if suit.dna.name == 'clubpres' and suit.getActualLevel() == 25:
                    self.setSuitCondition(suit.doId, 'shivering', 0, 0, 'setBoth')
                if suit.dna.name == 'clubpres' and suit.getActualLevel() == 23:
                    self.setSuitCondition(suit.doId, 'rpm', 0, 0, 'setBoth')
                if suit.dna.name == 'supervis' and suit.getActualLevel() == 21:
                    for t in self.battle.activeToons:
                        self.setToonCondition(t, 'groupDamageDown', -50, 1, 'setBoth')
                # if suit.dna.name == 'clerk' and suit.getActualLevel() == 20:
                #     for s in self.battle.activeSuits:
                #         self.setSuitCondition(s.doId, 'noKB', 1, 1, 'setBoth')
                if suit.dna.name == 'clerk' and suit.getActualLevel() == 22:
                    for s in self.battle.activeSuits:
                        self.setSuitCondition(s.doId, 'overseer', 1, 1, 'setBoth')
                if suit.dna.name == 'clerk':
                    self.setSuitCondition(suit.doId, 'attorney', 1, 1, 'setBoth')
                if suit.dna.name == 'ovt':
                    self.setSuitCondition(suit.doId, 'attorney', 1, 1, 'setBoth')
                if suit.dna.name == 'hrollers' and suit.getActualLevel() == 35:
                    self.setSuitCondition(suit.doId, 'shielding', 1, -1, 'setBoth')
                if suit.dna.name == 'supervis' and suit.getActualLevel() == 24:
                    self.setSuitCondition(suit.doId, 'shielding', 1, -1, 'setBoth')
                if self.suitHasCondition(suit.doId, 'alreadyDesperation'):
                    for s in self.battle.activeSuits:
                        self.setSuitCondition(s.doId, 'alreadyDesperation', 1, -1, 'setBoth')
                if suit.dna.name == 'bcaster':
                    self.setSuitCondition(suit.doId, 'vulnerablebroadcaster', 1, -1, 'setBoth')
                if suit.dna.name == 'cbutcher':
                    self.setSuitCondition(suit.doId, 'vulnerablevideographer', 3.0, -1, 'setBoth')
                if suit.dna.name in ['cdirector', 'liquid', 'dking', 'rkeeper']:
                    self.setSuitCondition(suit.doId, 'vulnerablevideographer', 2.25, -1, 'setBoth')
                if suit.dna.name == 'hrollers' and suit.getActualLevel() == 30:
                    self.setSuitCondition(suit.doId, 'directorDamageReduction', .9, -1, 'setBoth')
                    for s in self.battle.activeSuits:
                        self.setSuitCondition(s.doId, 'soakImmune', 1, 1, 'setBoth')
                if suit.dna.name == 'hrollers' and suit.getActualLevel() == 27:
                    self.setSuitCondition(suit.doId, 'directorDamageReduction', .9, -1, 'setBoth')
                    for s in self.battle.activeSuits:
                        self.setSuitCondition(s.doId, 'zapImmune', 1, 1, 'setBoth')
                if suit.dna.name == 'hrollers' and suit.getActualLevel() == 26:
                    self.setSuitCondition(suit.doId, 'directorDamageReduction', .9, -1, 'setBoth')
                    for s in self.battle.activeSuits:
                        self.setSuitCondition(s.doId, 'kbImmune', 1, 1, 'setBoth')
                if suit.dna.name == 'supervis' and suit.getActualLevel() == 26:
                    self.setSuitCondition(suit.doId, 'lureImmune', 1, -1, 'setBoth')
                if suit.dna.name == 'hrollers' and suit.getActualLevel() == 25:
                    self.setSuitCondition(suit.doId, 'directorDamageReduction', .9, -1, 'setBoth')
                    self.setSuitCondition(suit.doId, 'lureImmune', 1, -1, 'setBoth')
                    for s in self.battle.activeSuits:
                        self.setSuitCondition(s.doId, 'noKB', 1, 1, 'setBoth')
                # if suit.dna.name == 'hrollers' and suit.getActualLevel() == 36:
                #     for s in self.battle.activeSuits:
                #         self.setSuitCondition(s.doId, 'overseer', 1, 1, 'setBoth')
                if suit.dna.name == 'hrollers':
                    self.setSuitCondition(suit.doId, 'directorDamageReduction', .9, -1, 'setBoth')
                if suit.dna.name == 'hroller':
                    #suit.setHP(1)
                    if self.TurnsElapsed == 0:
                        self.setSuitCondition(suit.doId, 'directorDamageReduction', .05, -1, 'setBoth')
                    else:
                        self.setSuitCondition(suit.doId, 'immune', 1, -1, 'setBoth')
                        self.setSuitCondition(suit.doId, 'absorbingHR', 1, -1, 'setBoth')
                if suit.dna.name == 'hroller2' and not self.suitHasCondition(suit.doId, 'phase3'):
                    self.setSuitCondition(suit.doId, 'immune', 1, -1, 'setBoth')
                if suit.dna.name == 'videog' and len(self.battle.activeSuits) == 2:
                    self.setSuitCondition(suit.doId, 'immune', 0, 0, 'setBoth')
                    self.setSuitCondition(suit.doId, 'spawncalculator', 1, 10, 'setBoth')
                    currentBossHealth = -1
                    currentBossHealth2 = -1
                    currentBossHealth3 = -1
                    currentBossHealth4 = -1
                    for s in self.battle.suits:
                        if s.dna.name == 'director':
                            currentBossHealth = s.currHP
                        if s.dna.name == 'fmaker':
                            currentBossHealth2 = s.currHP
                        if s.dna.name == 'choreo':
                            currentBossHealth3 = s.currHP
                        if s.dna.name == 'cinema':
                            currentBossHealth4 = s.currHP
                    if currentBossHealth <= 0 and currentBossHealth2 <= 0 and currentBossHealth3 <= 0 and currentBossHealth4 <= 0:
                        self.setSuitCondition(suit.doId, 'immune', 0, 0, 'setBoth')
                if suit.dna.name == 'foreman' and suit.getActualLevel() == 20  and not self.suitHasCondition(suit.doId, 'alreadySleepy'):
                    self.setSuitCondition(suit.doId, 'sleepy', 1, 2, 'setBoth')
                    self.setSuitCondition(suit.doId, 'alreadySleepy', 1, -1, 'setBoth')
                if suit.dna.name == 'foreman' and suit.getActualLevel() == 22  and not self.suitHasCondition(suit.doId, 'alreadyExplosive'):
                    self.setSuitCondition(suit.doId, 'explosive', 1, 2, 'setBoth')
                    self.setSuitCondition(suit.doId, 'alreadyExplosive', 1, -1, 'setBoth')
                if suit.dna.name == 'sgoat' and not self.suitHasCondition(suit.doId, 'enraged'):
                    self.setSuitCondition(
                            suit.doId,
                            'rageBuilding',
                            self.getSuitConditionModifier(suit.doId, 'rageBuilding') + 10,
                            -1,
                            'setBoth'
                        )
                if suit.dna.name == 'phouse':
                    self.setSuitCondition(
                            suit.doId,
                            'powerhouseRotation',
                            self.getSuitConditionModifier(suit.doId, 'powerhouseRotation') + 10,
                            -1,
                            'setBoth'
                        )
                if suit.dna.name == 'sgoat':
                    if not self.suitHasCondition(suit.doId, 'enraged'):
                        self.setSuitCondition(suit.doId, 'shielding', 1, -1, 'setBoth')
                    if self.TurnsElapsed == 0:
                        if 4 not in self.litigationSpawns:
                            continue
                        else:
                            self.litigationSpawns.remove(4)
                if suit.dna.name == 'caseman':
                    if self.TurnsElapsed == 0:
                        if 3 not in self.litigationSpawns:
                            continue
                        else:
                            self.litigationSpawns.remove(3)
                if suit.dna.name == 'stenog':
                    if self.TurnsElapsed == 0:
                        if 2 not in self.litigationSpawns:
                            continue
                        else:
                            self.litigationSpawns.remove(2)
                if suit.dna.name == 'lgator':
                    if self.TurnsElapsed == 0:
                        if 1 not in self.litigationSpawns:
                            continue
                        else:
                            self.litigationSpawns.remove(1)
                if suit.dna.name == 'ambass':
                    if self.TurnsElapsed == 0:
                        if 1 not in self.litigationSpawns:
                            continue
                        else:
                            self.litigationSpawns.remove(1)
                if suit.dna.name == 'wtapper':
                    if not self.suitHasCondition(suit.doId, 'alreadyBeginning'):
                        self.setSuitCondition(suit.doId, 'beginning', 1, -1, 'setBoth')
                        self.setSuitCondition(suit.doId, 'alreadyBeginning', 1, -1, 'setBoth')
                    if self.TurnsElapsed == 0:
                        if 2 not in self.litigationSpawns:
                            continue
                        else:
                            self.litigationSpawns.remove(2)
                if suit.dna.name == 'bkeeper':
                    if self.TurnsElapsed == 0:
                        if 3 not in self.litigationSpawns:
                            continue
                        else:
                            self.litigationSpawns.remove(3)
                if suit.dna.name == 'phouse':
                    if not self.suitHasCondition(suit.doId, 'alreadyBeginning'):
                        self.setSuitCondition(suit.doId, 'beginning', 1, -1, 'setBoth')
                        self.setSuitCondition(suit.doId, 'alreadyBeginning', 1, -1, 'setBoth')
                    if self.TurnsElapsed == 0:
                        if 4 not in self.litigationSpawns:
                            continue
                        else:
                            self.litigationSpawns.remove(4)
                if suit.dna.name == 'safesupervis':
                    if self.TurnsElapsed == 0:
                        if 1 not in self.litigationSpawns:
                            continue
                        else:
                            self.litigationSpawns.remove(1)
                if suit.dna.name == 'ubuster':
                    if self.TurnsElapsed == 0:
                        if 2 not in self.litigationSpawns:
                            continue
                        else:
                            self.litigationSpawns.remove(2)
                if suit.dna.name == 'racket':
                    if self.TurnsElapsed == 0:
                        if 3 not in self.litigationSpawns:
                            continue
                        else:
                            self.litigationSpawns.remove(3)
                if suit.dna.name == 'radiog':
                    if self.TurnsElapsed == 0:
                        if 4 not in self.litigationSpawns:
                            continue
                        else:
                            self.litigationSpawns.remove(4)
                if suit.dna.name == 'treasure':
                    if self.TurnsElapsed == 0:
                        if 1 not in self.litigationSpawns:
                            continue
                        else:
                            self.litigationSpawns.remove(1)
                if suit.dna.name == 'liquidr':
                    if self.TurnsElapsed == 0:
                        if 2 not in self.litigationSpawns:
                            continue
                        else:
                            self.litigationSpawns.remove(2)
                if suit.dna.name == 'hustle':
                    if self.TurnsElapsed == 0:
                        if 3 not in self.litigationSpawns:
                            continue
                        else:
                            self.litigationSpawns.remove(3)
                if suit.dna.name == 'bookkeep':
                    if self.TurnsElapsed == 0:
                        if 4 not in self.litigationSpawns:
                            continue
                        else:
                            self.litigationSpawns.remove(4)
                if suit.dna.name == 'cdirector':
                    if self.TurnsElapsed == 0:
                        if 1 not in self.litigationSpawns:
                            continue
                        else:
                            self.litigationSpawns.remove(1)
                if suit.dna.name == 'dking':
                    if self.TurnsElapsed == 0:
                        if 2 not in self.litigationSpawns:
                            continue
                        else:
                            self.litigationSpawns.remove(2)
                if suit.dna.name == 'rkeeper':
                    if self.TurnsElapsed == 0:
                        if 3 not in self.litigationSpawns:
                            continue
                        else:
                            self.litigationSpawns.remove(3)
                    self.setSuitCondition(suit.doId, 'beginning', 1, -1, 'setBoth')
                if suit.dna.name == 'liquid':
                    if self.TurnsElapsed == 0:
                        if 4 not in self.litigationSpawns:
                            continue
                        else:
                            self.litigationSpawns.remove(4)
                    self.setSuitCondition(suit.doId, 'beginning', 1, -1, 'setBoth')
                if suit.dna.name == 'director':
                    self.setSuitCondition(suit.doId, 'shielding', 1, -1, 'setBoth')
                suit.b_setHP(suit.getHP())

        for suit in self.battle.activeSuits:
            if not hasattr(suit, 'dna'):
                self.notify.warning('a removed suit is in this battle!')
                return None
        self.__clearBonuses(hp=0)
        self.__clearBonuses(hp=1)

        self.suitConditionCalculator.calculateSuitConditions()
        self.baseSuitAttacksCalculator.calculatePreToonSuitAttacks()

        self.__calculateToonAttacksForTracks([FIRE, SUE, SOS, NPCSOS, PETSOS])
        self.__postProcessToonAttacksForTracks([FIRE, SUE, SOS, NPCSOS, PETSOS])
        # choose once
        self.battle.toonTrackOrder = self.getCurrentToonTrackOrder()

        for track in self.getCurrentToonTrackOrder():
            self.__calculateToonTrackPhase(track)

        self.__updateLureTimeouts()
        self.baseSuitAttacksCalculator.calculateSuitAttacks()
        self.bossbotCalculator.calculateSuitAttacksBossbotLitigation()
        self.boardbotCalculator.calculateSuitAttacksBoardbotLitigation()
        self.highRollerCalculator.calculateSuitAttacksHighRoller()
        self.sellbotCalculator.calculateSuitAttacksSellbotLitigation()
        self.cashbotCalculator.calculateSuitAttacksCashbotLitigation()
        self.lawbotCalculator.calculateSuitAttacksLawbotLitigation()
        self.witnessStandInCalculator.calculateSuitAttacksWitnessStandIn()
        self.pacesetterCalculator.calculatePacesetterAttacks()
        self.chainsawCalculator.calculateChainsawAttacks()
        self.directorsCalculator.calculateSuitAttacksDirectors()
        self.countsCalculator.calculateSuitAttacksCounts()
        self.faceTheFamilyCalculator.calculateSuitAttacksFaceTheFamily()
        self.baseSuitAttacksCalculator.calculateEndOfRoundAttacks()
        self.suitSpawnCalculator.calculateSuitSpawns()
        if self.roundsToonsHit > 0:
            self.roundsToonsHit -= 1
        if self.roundsCogsMiss > 0:
            self.roundsCogsMiss -= 1
        if toonsHit == 1 and self.roundsToonsHit <= 0:
            self.toonsAlwaysHit = 0
        if cogsMiss == 1 and self.roundsCogsMiss <= 0:
            self.suitsAlwaysMiss = 0
            self.__printSuitAtkStats()
            if self.toonStatusConditions:
                self.printToonConditions()

    def getCurrentToonTrackOrder(self):
        defaultOrder = [HEAL, TRAP, LURE, THROW, SQUIRT, ZAP, SOUND, DROP]

        for toonId in self.battle.activeToons:
            for cond, order in CONTENT_SYNC_CONDITION_ORDERS.items():
                if self.toonHasCondition(toonId, cond):
                    return order

        return defaultOrder


    def __calculateFiredCogs():
        import pdb
        pdb.set_trace()

    def toonLeftBattle(self, toonId):
        if toonId in self.toonSkillPtsGained:
            del self.toonSkillPtsGained[toonId]
        if toonId in self.suitAtkStats:
            del self.suitAtkStats[toonId]
        if not CLEAR_SUIT_ATTACKERS:
            oldSuitIds = []
            for s in self.SuitAttackers.keys():
                if toonId in self.SuitAttackers[s]:
                    del self.SuitAttackers[s][toonId]
                    if len(self.SuitAttackers[s]) == 0:
                        oldSuitIds.append(s)

            for oldSuitId in oldSuitIds:
                del self.SuitAttackers[oldSuitId]

        self.__clearTrapCreator(toonId)
        self.__clearLurer(toonId)

    def suitLeftBattle(self, suitId):
        self.__removeLured(suitId)
        if suitId in self.SuitAttackers:
            del self.SuitAttackers[suitId]
        self.__removeSuitTrap(suitId)

    def __updateActiveToons(self):
        if not CLEAR_SUIT_ATTACKERS:
            oldSuitIds = []
            for s in self.SuitAttackers.keys():
                for t in self.SuitAttackers[s].keys():
                    if t not in self.battle.activeToons:
                        del self.SuitAttackers[s][t]
                        if len(self.SuitAttackers[s]) == 0:
                            oldSuitIds.append(s)

            for oldSuitId in oldSuitIds:
                del self.SuitAttackers[oldSuitId]

        for trap in self.traps.keys():
            if self.traps[trap][1] not in self.battle.activeToons:
                self.traps[trap][1] = 0

    def getSkillGained(self, toonId, track):
        return BattleExperienceAI.getSkillGained(self.toonSkillPtsGained, toonId, track)

    def getLuredSuits(self):
        self.TurnsElapsed += 1
        self.deadSuits = 0
        self.absorbDamage = 0
        self.absorbDamageRecordkeeper = 0
        self.sacrificedCogs = 0
        self.fraudulentDamage = 0
        self.comboDamage = 0
        self.knockbackDamage = 0
        self.objectionDamage = 0
        self.levels -= self.levels
        self.targets -= self.targets
        self.levelDamage -= self.levelDamage
        self.notify.debug('Current Elapsed Turns: ' + str(self.TurnsElapsed))
        self.printSuitConditions()
        luredSuits = self.currentlyLuredSuits.keys()
        #self.notify.debug('Lured suits reported to battle: ' + repr(luredSuits))
        return luredSuits

    def __suitIsLured(self, suitId, prevRound = 0):
        inList = suitId in self.currentlyLuredSuits
        if prevRound:
            return inList and self.currentlyLuredSuits[suitId][0] != -1
        return inList

    def getImmuneSuits(self):
        gottenImmuneSuits = []
        for suit in self.battle.activeSuits:
            if suit.getImmuneStatus() == 1:
                gottenImmuneSuits.append(suit.doId)
        #self.notify.debug('Immune suits reported to battle: ' + repr(gottenImmuneSuits))
        return gottenImmuneSuits

    def getEnragedSuits(self):
        gottenEnragedSuits = []
        for suit in self.battle.activeSuits:
            if suit.getEnragedStatus() == 1:
                gottenEnragedSuits.append(suit.doId)
        #self.notify.debug('Enraged suits reported to battle: ' + repr(gottenEnragedSuits))
        return gottenEnragedSuits

    def getAbsorbingSuits(self):
        gottenAbsorbingSuits = []
        for suit in self.battle.activeSuits:
            if suit.getAbsorbingStatus() == 1:
                gottenAbsorbingSuits.append(suit.doId)
        #self.notify.debug('Absorbing suits reported to battle: ' + repr(gottenAbsorbingSuits))
        return gottenAbsorbingSuits

    def getSoakedSuits(self):
        gottenSoakedSuits = []
        for suit in self.battle.activeSuits:
            if suit.getSoakedStatus() == 1:
                gottenSoakedSuits.append(suit.doId)
        #self.notify.debug('Soaked suits reported to battle: ' + repr(gottenSoakedSuits))
        return gottenSoakedSuits

    def __suitIsImmune(self, suitId, prevRound=0):
        inList = suitId in self.currentlyImmuneSuits
        if prevRound:
            return inList and self.currentlyImmuneSuits[suitId][0] != -1
        return inList

    def __suitIsEnraged(self, suitId, prevRound=0):
        inList = suitId in self.currentlyEnragedSuits
        if prevRound:
            return inList and self.currentlyEnragedSuits[suitId][0] != -1
        return inList

    def __suitIsAbsorbing(self, suitId, prevRound=0):
        inList = suitId in self.currentlyAbsorbingSuits
        if prevRound:
            return inList and self.currentlyAbsorbingSuits[suitId][0] != -1
        return inList

    def __suitIsSoaked(self, suitId, prevRound=0):
        inList = suitId in self.currentlySoakedSuits
        if prevRound:
            return inList and self.currentlySoakedSuits[suitId][0] != -1
        return inList

    def __suitIsWet(self, suitId, prevRound = 0):
        inList = suitId in self.currentlyWetSuits
        return inList

    def __findAvailLureId(self, lurerId):
        luredSuits = self.currentlyLuredSuits.keys()
        lureIds = []
        for currLured in luredSuits:
            lurerInfo = self.currentlyLuredSuits[currLured][3]
            lurers = lurerInfo.keys()
            for currLurer in lurers:
                currId = lurerInfo[currLurer][1]
                if currLurer == lurerId and currId not in lureIds:
                    lureIds.append(currId)

        lureIds.sort()
        currId = 1
        for currLureId in lureIds:
            if currLureId != currId:
                return currId
            currId += 1

        return currId

    def __addLuredSuitInfo(self, suitId, currRounds, maxRounds, wakeChance, lurer, lureLvl, lureId = -1, npc = 0):
        if lureId == -1:
            availLureId = self.__findAvailLureId(lurer)
        else:
            availLureId = lureId
        if npc == 1:
            credit = 0
        else:
            credit = self.itemIsCredit(LURE, lureLvl)
        if suitId in self.currentlyLuredSuits:
            lureInfo = self.currentlyLuredSuits[suitId]
            if not lurer in lureInfo[3]:
                lureInfo[1] += maxRounds
                if wakeChance < lureInfo[2]:
                    lureInfo[2] = wakeChance
                lureInfo[3][lurer] = [lureLvl, availLureId, credit]
        else:
            lurerInfo = {lurer: [lureLvl, availLureId, credit]}
            self.currentlyLuredSuits[suitId] = [currRounds,
             maxRounds,
             wakeChance,
             lurerInfo]
        #self.notify.debug('__addLuredSuitInfo: currLuredSuits -> %s' % repr(self.currentlyLuredSuits))
        return availLureId

    def __getLurers(self, suitId):
        if self.__suitIsLured(suitId):
            return self.currentlyLuredSuits[suitId][3].keys()
        return []

    def __getLuredExpInfo(self, suitId):
        returnInfo = []
        lurers = self.__getLurers(suitId)
        if len(lurers) == 0:
            return returnInfo
        lurerInfo = self.currentlyLuredSuits[suitId][3]
        for currLurer in lurers:
            returnInfo.append([currLurer,
             lurerInfo[currLurer][0],
             lurerInfo[currLurer][1],
             lurerInfo[currLurer][2]])

        return returnInfo

    def __clearLurer(self, lurerId, lureId = -1):
        luredSuits = self.currentlyLuredSuits.keys()
        for currLured in luredSuits:
            lurerInfo = self.currentlyLuredSuits[currLured][3]
            lurers = lurerInfo.keys()
            for currLurer in lurers:
                if currLurer == lurerId and (lureId == -1 or lureId == lurerInfo[currLurer][1]):
                    del lurerInfo[currLurer]

    def __setLuredMaxRounds(self, suitId, rounds):
        if self.__suitIsLured(suitId):
            self.currentlyLuredSuits[suitId][1] = rounds

    def __setLuredWakeChance(self, suitId, chance):
        if self.__suitIsLured(suitId):
            self.currentlyLuredSuits[suitId][2] = chance

    def __incLuredCurrRound(self, suitId):
        if self.__suitIsLured(suitId):
            self.currentlyLuredSuits[suitId][0] += 1

    def __removeLured(self, suitId):
        if self.__suitIsLured(suitId):
            del self.currentlyLuredSuits[suitId]

    def __luredMaxRoundsReached(self, suitId):
        return self.__suitIsLured(suitId) and self.currentlyLuredSuits[suitId][0] >= self.currentlyLuredSuits[suitId][1]

    def __incWetCurrRound(self, suitId):
        if self.__suitIsWet(suitId):
            self.currentlyWetSuits[suitId][0] += 1

    def __removeWet(self, suitId):
        if self.__suitIsWet(suitId):
            del self.currentlyWetSuits[suitId]

    def __wetMaxRoundsReached(self, suitId):
        return self.__suitIsWet(suitId) and self.currentlyWetSuits[suitId][0] >= self.currentlyWetSuits[suitId][1]

    def __incEnragedCurrRound(self, suitId):
        if self.__suitIsEnraged(suitId):
            self.currentlyEnragedSuits[suitId][0] += 1

    def __removeEnraged(self, suitId):
        if self.__suitIsEnraged(suitId):
            del self.currentlyEnragedSuits[suitId]

    def __enragedMaxRoundsReached(self, suitId):
        return self.__suitIsEnraged(suitId) and self.currentlyEnragedSuits[suitId][0] >= self.currentlyEnragedSuits[suitId][1]

    def __incAbsorbingCurrRound(self, suitId):
        if self.__suitIsAbsorbing(suitId):
            self.currentlyAbsorbingSuits[suitId][0] += 1

    def __removeAbsorbing(self, suitId):
        if self.__suitIsAbsorbing(suitId):
            del self.currentlyAbsorbingSuits[suitId]

    def __absorbingMaxRoundsReached(self, suitId):
        return self.__suitIsAbsorbing(suitId) and self.currentlyAbsorbingSuits[suitId][0] >= self.currentlyAbsorbingSuits[suitId][1]

    def __luredWakeupTime(self, suitId):
        return self.__suitIsLured(suitId) and self.currentlyLuredSuits[suitId][0] > 0 and random.randint(0, 99) < self.currentlyLuredSuits[suitId][2]

    def itemIsCredit(self, track, level):
        if track == PETSOS:
            return 0
        return level < self.creditLevel

    def __getActualTrack(self, toonAttack):
        if toonAttack[TOON_TRACK_COL] == NPCSOS:
            track = NPCToons.getNPCTrack(toonAttack[TOON_TGT_COL])
            if track != None:
                return track
            else:
                self.notify.warning('No NPC with id: %d' % toonAttack[TOON_TGT_COL])
        return toonAttack[TOON_TRACK_COL]

    def __getActualTrackLevel(self, toonAttack):
        if toonAttack[TOON_TRACK_COL] == NPCSOS:
            track, level, hp = NPCToons.getNPCTrackLevelHp(toonAttack[TOON_TGT_COL])
            if track != None:
                return (track, level)
            else:
                self.notify.warning('No NPC with id: %d' % toonAttack[TOON_TGT_COL])
        return (toonAttack[TOON_TRACK_COL], toonAttack[TOON_LVL_COL])

    def __getActualTrackLevelHp(self, toonAttack):
        if toonAttack[TOON_TRACK_COL] == NPCSOS:
            track, level, hp = NPCToons.getNPCTrackLevelHp(toonAttack[TOON_TGT_COL])
            if track != None:
                return (track, level, hp)
            else:
                self.notify.warning('No NPC with id: %d' % toonAttack[TOON_TGT_COL])
        elif toonAttack[TOON_TRACK_COL] == PETSOS:
            trick = toonAttack[TOON_LVL_COL]
            petProxyId = toonAttack[TOON_TGT_COL]
            trickId = toonAttack[TOON_LVL_COL]
            healRange = PetTricks.TrickHeals[trickId]
            hp = 0
            if petProxyId in simbase.air.doId2do:
                petProxy = simbase.air.doId2do[petProxyId]
                if trickId < len(petProxy.trickAptitudes):
                    aptitude = petProxy.trickAptitudes[trickId]
                    hp = math.ceil(lerp(healRange[0], healRange[1], aptitude))
            else:
                self.notify.warning('pet proxy: %d not in doId2do!' % petProxyId)
            return (toonAttack[TOON_TRACK_COL], toonAttack[TOON_LVL_COL], hp)
        return (toonAttack[TOON_TRACK_COL], toonAttack[TOON_LVL_COL], 0)

    def __calculatePetTrickSuccess(self, toonAttack):
        petProxyId = toonAttack[TOON_TGT_COL]
        if not petProxyId in simbase.air.doId2do:
            self.notify.warning('pet proxy %d not in doId2do!' % petProxyId)
            toonAttack[TOON_ACCBONUS_COL] = 1
            return (0, 0)
        petProxy = simbase.air.doId2do[petProxyId]
        trickId = toonAttack[TOON_LVL_COL]
        toonAttack[TOON_ACCBONUS_COL] = petProxy.attemptBattleTrick(trickId)
        if toonAttack[TOON_ACCBONUS_COL] == 1:
            return (0, 0)
        else:
            return (1, 100)

    def suitCanAttack(self, suitId):
        return self.__suitCanAttack(suitId)

    def getGenericSuitAttack(self, suitId):
        return self.__getGenericSuitAttack(suitId)

    def getCheatAttack(self, suitId, attackInfo):
        return self.__getCheatAttack(
            suitId,
            attackInfo
        )

    def getAbilityQueued(self, suitId):
        return self.__getAbilityQueued(suitId)

    def appendToonConditionDamageAndRetaliation(
            self,
            *args,
            **kwargs):

        return self.__appendToonConditionDamageAndRetaliation(
            *args,
            **kwargs
        )
