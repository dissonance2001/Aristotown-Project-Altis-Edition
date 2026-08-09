from toontown.battle.BattleBase import *
from toontown.battle.BattleGlobals import *
from toontown.battle import SuitBattleGlobals
import random
import math

class SellbotLitigationCalculatorAI:

    def __init__(self, calculator):
        self.calculator = calculator
        self.battle = calculator.battle

    def __getattr__(self, name):
        return getattr(self.calculator, name)

    def __suitCanAttack(self, suitId):
        return self.calculator.suitCanAttack(suitId)

    def __getCheatAttack(self, suitId, attackInfo):
        return self.calculator.getCheatAttack(
            suitId,
            attackInfo
        )

    def __getLureRemoval(self, suitId):
        return self.calculator.getLureRemoval(suitId)

    def __getAbilityQueued(self, suitId):
        return self.calculator.getAbilityQueued(suitId)

    def __appendToonConditionDamageAndRetaliation(
            self,
            *args,
            **kwargs):

        return self.calculator.appendToonConditionDamageAndRetaliation(
            *args,
            **kwargs
        )

    def calculateSuitAttacksSellbotLitigation(self):
        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'hustle':
                attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'TrafficRedLightRetaliation', # Breach Of Contract
                     'animName': 'nothing',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_GROUP})
                if attack[SUIT_ATK_COL]:
                    self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'hustle':
                attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'TrafficTrafficViolation', # Breach Of Contract
                     'animName': 'nothing',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_GROUP})
                if attack[SUIT_ATK_COL]:
                    self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'hustle':
                sacrificedCogs = 0
                for suit in self.battle.activeSuits:
                    if suit.currHP <= 0:
                        continue
                    if self.suitHasCondition(suit.doId, 'greenLight'):
                        sacrificedCogs += 1
                    if sacrificedCogs > 0:
                        attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                            'name': 'TrafficGreenLightRetaliation', # Breach Of Contract
                            'animName': 'nothing',
                            'hp': 0,
                            'acc': 100,
                            'freq': 0,
                            'group': SuitBattleGlobals.ATK_TGT_GROUP})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)

        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'safesupervis':
                if self.suitHasCondition(suitId, 'highpressurecalculator') and not self.__suitCanAttack(suitId) and \
                        self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'highpressurecalculator') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'UnionBusterContractEnforcement',  # Hot Take Soak Retaliation
                                                            'animName': 'magic2',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'radiog':
                if self.suitHasCondition(suitId, 'hottakecalculator2') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'hottakecalculator2') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                      'name': 'UnionBusterContractEnforcement2', # ThrowBook
                     'animName': 'throw-object',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)

        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if not self.suitHasCondition(suitId, 'dotfinished'):
                self.__appendToonConditionDamageAndRetaliation(
                    condition='busted',
                    damage=25,
                    damageMovie='UnionBusterUnionBusterDamage',
                    retaliateAtTurns=[1],
                    retaliations=[
                        {
                            'suitNames': ['safesupervis'],
                            'movie': 'UnionBusterContractEnforcement',
                            'animName': 'magic2',
                            'hp': 25,
                            'queueCondition': 'highpressurecalculator',
                        },
                        {
                            'suitNames': ['radiog'],
                            'movie': 'UnionBusterContractEnforcement2',
                            'animName': 'throw-object',
                            'hp': 30, 
                            'queueCondition': 'hottakecalculator2',
                        }
                    ]
                )
            if self.battle.activeSuits[i].dna.name == 'safesupervis':  # powerhouse
                if (self.suitHasCondition(suitId, 'soaked') or self.suitHasCondition(suitId, 'drenched')) and self.__suitCanAttack(suitId):
                    if self.battle.activeSuits[i].currHP <= 1000:
                        attack = self.__getCheatAttack(suitId, {'suitName': 'safesupervis',
                                                    'name': 'RacketeerPeckingOrderRetaliationSoak',
                                                'animName': 'nothing',
                                                'hp': 0,
                                                'acc': 100,
                                                'freq': 0,
                                                'group': SuitBattleGlobals.ATK_TGT_GROUP})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    elif self.battle.activeSuits[i].currHP <= 2000:
                        attack = self.__getCheatAttack(suitId, {'suitName': 'safesupervis',
                                                    'name': 'RacketeerPeckingOrderRetaliationSoak',
                                                'animName': 'nothing',
                                                'hp': 0,
                                                'acc': 100,
                                                'freq': 0,
                                                'group': SuitBattleGlobals.ATK_TGT_TRIPLE})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    elif self.battle.activeSuits[i].currHP <= 3000:
                        attack = self.__getCheatAttack(suitId, {'suitName': 'safesupervis',
                                                    'name': 'RacketeerPeckingOrderRetaliationSoak',
                                                'animName': 'nothing',
                                                'hp': 0,
                                                'acc': 100,
                                                'freq': 0,
                                                'group': SuitBattleGlobals.ATK_TGT_DOUBLE})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    else:
                        attack = self.__getCheatAttack(suitId, {'suitName': 'safesupervis',
                                        'name': 'RacketeerPeckingOrderRetaliationSoak',
                                        'animName': 'nothing',
                                    'hp': 0,
                                    'acc': 100,
                                    'freq': 0,
                                    'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'ubuster':
                if self.hustlerHits > 0 and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                      'name': 'UnionBusterUnionDues', # ThrowBook
                     'animName': 'magic3',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_GROUP})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                        self.calculator.unionDues += 2


            # Primary Cheats
        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'hustle':
                if self.suitHasCondition(suitId, 'unionbustercalculator') and not self.__suitCanAttack(suitId) and \
                        self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'unionbustercalculator') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'TrafficDetour', # Breach Of Contract
                     'animName': 'throw-object',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'safesupervis':
                if self.suitHasCondition(suitId, 'unionbustercalculator') and not self.__suitCanAttack(suitId) and \
                        self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'unionbustercalculator') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'RadiographerHotTakeRetaliation',  # Hot Take Soak Retaliation
                                                            'animName': 'magic2',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'ubuster':
                if self.suitHasCondition(suitId, 'breachcalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'breachcalculator') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                      'name': 'UnionBusterBreachOfContract', # ThrowBook
                     'animName': 'sanction',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)

        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'ubuster':
                if self.suitHasCondition(suitId, 'breachvulnerable') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'breachvulnerable') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                      'name': 'UnionBusterBreachOfContract2', # ThrowBook
                     'animName': 'sanction',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'breachvulnerable3') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'breachvulnerable3') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                      'name': 'UnionBusterNoStrikeClause', # ThrowBook
                     'animName': 'nothing',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'breachvulnerable2') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'breachvulnerable2') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                      'name': 'UnionBusterBreachOfContract3', # ThrowBook
                     'animName': 'sanction',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)

        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'ubuster':
                self.__appendToonConditionDamageAndRetaliation(
                    condition='snapped',
                    damage=25,
                    damageMovie=None,
                    retaliations=[
                        {
                            'suitNames': ['ubuster'],
                            'movie': 'UnionBusterBreachOfContract3',
                            'animName': 'sanction',
                            'hp': 25,
                            'queueCondition': 'breachvulnerable2',
                        }
                    ]
                )
            if self.battle.activeSuits[i].dna.name == 'ubuster':
                self.__appendToonConditionDamageAndRetaliation(
                    condition='confused',
                    damage=25,
                    damageMovie=None,
                    retaliateAtTurns=[1],
                    retaliations=[
                        {
                            'suitNames': ['ubuster'],
                            'movie': 'UnionBusterNoStrikeClause',
                            'animName': 'nothing',
                            'hp': 25,
                            'queueCondition': 'breachvulnerable3',
                        }
                    ]
                )
            if self.battle.activeSuits[i].dna.name == 'safesupervis':
                self.__appendToonConditionDamageAndRetaliation(
                    condition='banned3',
                    damage=25,
                    damageMovie=None,
                    retaliations=[
                        {
                            'suitNames': ['ubuster'],
                            'movie': 'UnionBusterBreachOfContract2',
                            'animName': 'sanction',
                            'hp': 25,
                            'queueCondition': 'breachvulnerable',
                        },
                        {
                            'suitNames': ['safesupervis'],
                            'movie': 'SafetyPromotion2',
                            'animName': 'magic3-alt',
                            'hp': 50,
                        }
                    ]
                )
                if self.suitHasCondition(suitId, 'overpressurecalculator') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'TargetCheck', # Target Check for Promotion
                     'animName': 'nothing',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'overpressurecalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'overpressurecalculator') and not (self.suitHasCondition(suitId, 'targetCheckCondition') and self.getSuitConditionModifier(suitId, 'targetCheckCondition') > -1) and self.battle.activeSuits[i].currHP > 0 and self.__suitCanAttack(suitId):
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'overpressurecalculator') and (self.suitHasCondition(suitId, 'targetCheckCondition') and self.getSuitConditionModifier(suitId, 'targetCheckCondition') > -1) and self.battle.activeSuits[i].currHP > 0 and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'SafetyOverpressured', # Promotion
                     'animName': 'nothing',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'target3'):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'SafetyOverpressured2',  # Promotion
                                                            'animName': 'nothing',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'target4'):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'SafetyOverpressured3',  # Promotion
                                                            'animName': 'nothing',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'target5'):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'SafetyOverpressured4',  # Promotion
                                                            'animName': 'nothing',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'target6'):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'SafetyOverpressured5',  # Promotion
                                                            'animName': 'nothing',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)

            # Secondary Cheats
        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'ubuster':
                if self.suitHasCondition(suitId, 'unionbustercalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'unionbustercalculator') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                      'name': 'UnionBusterUnionBuster', # ThrowBook
                     'animName': 'nothing',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'ubuster':  # arbitrator
                if self.suitHasCondition(suitId, 'unionbustcalculator') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'TargetCheck', # Target Check for Throw Book
                     'animName': 'throw-object',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'unionbustcalculator') and not self.getSuitConditionModifier(suitId, 'targetCheckCondition') > -1 and self.__suitCanAttack(suitId):
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'unionbustcalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'unionbustcalculator') and self.suitHasCondition(suitId, 'targetCheckCondition') and self.getSuitConditionModifier(suitId, 'targetCheckCondition') > -1 and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                      'name': 'UnionBusterUnionBust', # ThrowBook
                     'animName': 'quick-jump',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'unionbustcalculator2') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'TargetCheck', # Target Check for Throw Book
                     'animName': 'throw-object',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'unionbustcalculator2') and not self.getSuitConditionModifier(suitId, 'targetCheckCondition') > -1 and self.__suitCanAttack(suitId):
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'unionbustcalculator2') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'unionbustcalculator2') and self.suitHasCondition(suitId, 'targetCheckCondition') and self.getSuitConditionModifier(suitId, 'targetCheckCondition') > -1 and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                      'name': 'UnionBusterUnionBust', # ThrowBook
                     'animName': 'quick-jump',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                        self.setSuitCondition(suitId, 'unionbustcalculator2', 0, 0, 'setBoth')
                if (self.calculator.unionSacrifices % 2 == 0 and not self.calculator.unionSacrifices == 0) and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                      'name': 'UnionBusterCompensationClaims', # ThrowBook
                     'animName': 'nothing',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                        self.calculator.unionSacrifices *= 0
            if self.battle.activeSuits[i].dna.name == 'radiog':
                if self.suitHasCondition(suitId, 'radioinfrequencycalculator') and not self.__suitCanAttack(suitId) and \
                        self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'radioinfrequencycalculator') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'RadiographerRadioInfrequency', # Radio Infrequency
                     'animName': 'nothing',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_GROUP})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'safesupervis':
                if self.suitHasCondition(suitId, 'heatwavecalculator') and not self.__suitCanAttack(suitId) and \
                        self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'heatwavecalculator') and self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP < 4850:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'SafetyHeatWave', # Heat Wave
                     'animName': 'magic3-alt',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_GROUP})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.__suitCanAttack(suitId) and self.damageHP.get(suitId, 0) > 0:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'DamageMovie', # Damage From Heat Wave
                     'animName': 'nothing',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.battle.activeSuits[i].currHP <= 0 and not self.suitHasCondition(suitId, 'alreadyDesperation2'):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'Desperation',  # Desperation Activation
                                                            'animName': 'nothing',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                    for i in xrange(len(self.battle.activeSuits)):  # Desperation for Litigation Managers
                        suitId = self.battle.activeSuits[i].doId
                        if self.suitHasCondition(suitId, 'desperationcalculator') and self.battle.activeSuits[i].dna.name in SuitBattleGlobals.LitigationManagers and not self.battle.activeSuits[i].currHP <= 0 and not self.suitHasCondition(suitId, 'alreadyDesperation2'):
                            attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                    'name': 'Desperation2',  # Desperation Activation
                                                                    'animName': 'nothing',
                                                                    'hp': 0,
                                                                    'acc': 100,
                                                                    'freq': 0,
                                                                    'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                            if attack[SUIT_ATK_COL]:
                                self.battle.suitAttacks.append(attack)

            # Gag Bans & End Of Round Cheats
        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'hustle':
                if self.suitHasCondition(suitId, 'contractenforcementcalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[
                    i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'contractenforcementcalculator') and self.__suitCanAttack(suitId):
                   attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                    'name': 'HustlerCustomerRetention',
                     'animName': 'nothing',
                    'hp': 0,
                    'acc': 100,
                    'freq': 0,
                    'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                   if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            # if self.battle.activeSuits[i].dna.name == 'hustle':
            #     if self.__suitCanAttack(suitId):
            #         damageCogs = 0
            #         for suit in self.battle.activeSuits:
            #             if suit.currHP <= 0:
            #                 continue
            #             if suit.getHP() < suit.maxHP and suit.dna.name != 'hustle':
            #                 damageCogs = 1
            #         if damageCogs > 0 and self.__suitCanAttack(suitId):
            #             attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
            #                                                     'name': 'HustlerCustomerRetention',  # Compensation
            #                                                     'animName': 'nothing',
            #                                                     'hp': 0,
            #                                                     'acc': 100,
            #                                                     'freq': 0,
            #                                                     'group': SuitBattleGlobals.ATK_TGT_SINGLE})
            #             if attack[SUIT_ATK_COL]:
            #                 self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'hustle':
                if self.suitHasCondition(suitId, 'yellowlightcalculator') and not self.__suitCanAttack(suitId) and \
                        self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'yellowlightcalculator') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'TrafficYellowLight',
                     'animName': 'nothing',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'greenlightcalculator') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'PresidentTargetCheck', # Target Check for Promotion
                     'animName': 'nothing',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'greenlightcalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'greenlightcalculator') and not (self.suitHasCondition(suitId, 'targetCheckCondition') and self.getSuitConditionModifier(suitId, 'targetCheckCondition') > -1) and self.battle.activeSuits[i].currHP > 0 and self.__suitCanAttack(suitId):
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'greenlightcalculator') and (self.suitHasCondition(suitId, 'targetCheckCondition') and self.getSuitConditionModifier(suitId, 'targetCheckCondition') > -1) and self.battle.activeSuits[i].currHP > 0 and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'TrafficGreenLight', # Promotion
                     'animName': 'nothing',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'redlightcalculator') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'PresidentTargetCheck', # Target Check for Promotion
                     'animName': 'nothing',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'redlightcalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'redlightcalculator') and not (self.suitHasCondition(suitId, 'targetCheckCondition') and self.getSuitConditionModifier(suitId, 'targetCheckCondition') > -1) and self.battle.activeSuits[i].currHP > 0 and self.__suitCanAttack(suitId):
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'redlightcalculator') and (self.suitHasCondition(suitId, 'targetCheckCondition') and self.getSuitConditionModifier(suitId, 'targetCheckCondition') > -1) and self.battle.activeSuits[i].currHP > 0 and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'TrafficRedLight', # Promotion
                     'animName': 'nothing',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'hustle':
                if self.TurnsElapsed % 1 == 0 and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'TrafficCongestionPricing', # Breach Of Contract Confused
                     'animName': 'throw-object',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_GROUP})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
