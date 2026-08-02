from toontown.battle.BattleBase import *
from toontown.battle.BattleGlobals import *
from toontown.battle import SuitBattleGlobals
import random
import math

class CashbotLitigationCalculatorAI:

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

    def calculateSuitAttacksCashbotLitigation(self):
            x = self.TurnsElapsed
            for i in xrange(len(self.battle.activeSuits)):
                suitId = self.battle.activeSuits[i].doId
                if self.battle.activeSuits[i].dna.name == 'racket':
                    if self.suitHasCondition(suitId, 'extortioncalculator') and not self.__suitCanAttack(suitId) and \
                            self.battle.activeSuits[i].currHP > 0:
                        attack = self.__getAbilityQueued(suitId)
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    if self.suitHasCondition(suitId, 'extortioncalculator') and self.__suitCanAttack(suitId) and self.calculator.racketeerMultiplier >= 8:
                        attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                        'name': 'RacketeerExtortion', # Extortion
                        'animName': 'sacrifice-cog',
                        'hp': 0,
                        'acc': 100,
                        'freq': 0,
                        'group': SuitBattleGlobals.ATK_TGT_GROUP})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    if self.syphonHP.get(suitId, 0) > 0:
                        attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                'name': 'SyphonMovie',  # Wiretapped
                                                                'animName': 'nothing',
                                                                'hp': 0,
                                                                'acc': 100,
                                                                'freq': 0,
                                                                'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    if self.calculator.racketeerMultiplier >= 4 and self.suitHasCondition(suitId, 'profiteeringcalculator') and self.__suitCanAttack(suitId):
                        attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                        'name': 'TargetCheck', # Target Check for Promotion
                        'animName': 'nothing',
                        'hp': 0,
                        'acc': 100,
                        'freq': 0,
                        'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    if self.calculator.racketeerMultiplier >= 4 and self.suitHasCondition(suitId, 'profiteeringcalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                        attack = self.__getAbilityQueued(suitId)
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    if self.calculator.racketeerMultiplier >= 4 and self.suitHasCondition(suitId, 'profiteeringcalculator') and not (self.suitHasCondition(suitId, 'targetCheckCondition') and self.getSuitConditionModifier(suitId, 'targetCheckCondition') > -1) and self.battle.activeSuits[i].currHP > 0 and self.__suitCanAttack(suitId):
                        attack = self.__getAbilityQueued(suitId)
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    if self.calculator.racketeerMultiplier >= 4 and self.suitHasCondition(suitId, 'profiteeringcalculator') and (self.suitHasCondition(suitId, 'targetCheckCondition') and self.getSuitConditionModifier(suitId, 'targetCheckCondition') > -1) and self.battle.activeSuits[i].currHP > 0 and self.__suitCanAttack(suitId):
                        attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                        'name': 'RacketeerProfiteering', # Profiteering
                        'animName': 'neutral',
                        'hp': 0,
                        'acc': 100,
                        'freq': 0,
                        'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)

            for i in xrange(len(self.battle.activeSuits)):
                suitId = self.battle.activeSuits[i].doId
                if self.battle.activeSuits[i].dna.name == 'payman':
                    if self.suitHasCondition(suitId, 'bonuscalculator') and not len(self.battle.activeSuits) > 1 and self.battle.activeSuits[i].currHP > 0 and self.__suitCanAttack(suitId):
                        attack = self.__getAbilityQueued(suitId)
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    if self.suitHasCondition(suitId, 'bonuscalculator') and self.battle.activeSuits[i].currHP > 0 and not self.__suitCanAttack(suitId):
                        attack = self.__getAbilityQueued(suitId)
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    if self.suitHasCondition(suitId, 'bonuscalculator') and self.__suitCanAttack(suitId) and len(self.battle.activeSuits) > 1:
                        attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                'name': 'PayrollPerformanceBonus',  # Trick Of The Light
                                                'animName': 'throw-paper',
                                                'hp': 0,
                                                'acc': 100,
                                                'freq': 0,
                                                'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)

            for i in xrange(len(self.battle.activeSuits)):
                suitId = self.battle.activeSuits[i].doId
                if self.battle.activeSuits[i].dna.name == 'payman':
                    if self.suitHasCondition(suitId, 'processcalculator') and not len(self.battle.activeSuits) > 1 and self.battle.activeSuits[i].currHP > 0 and self.__suitCanAttack(suitId):
                        attack = self.__getAbilityQueued(suitId)
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    if self.suitHasCondition(suitId, 'processcalculator') and self.battle.activeSuits[i].currHP > 0 and not self.__suitCanAttack(suitId):
                        attack = self.__getAbilityQueued(suitId)
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    if self.suitHasCondition(suitId, 'processcalculator') and self.__suitCanAttack(suitId) and len(self.battle.activeSuits) > 1:
                        attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                'name': 'PayrollPayrollProcessing',  # Trick Of The Light
                                                'animName': 'throw-paper',
                                                'hp': 0,
                                                'acc': 100,
                                                'freq': 0,
                                                'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                if self.battle.activeSuits[i].dna.name == 'racket':
                    if self.calculator.racketeerMultiplier >= 20 and not self.__suitCanAttack(suitId) and \
                            self.battle.activeSuits[i].currHP > 0:
                        attack = self.__getAbilityQueued(suitId)
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    if self.__suitCanAttack(suitId) and self.calculator.racketeerMultiplier >= 20:
                        self.costsMultiplier += 10
                        self.battle.activeSuits[i].setDamageMultiplier(self.battle.activeSuits[i].getDamageMultiplier() * (1 +((self.costsMultiplier / 2) * .01)))
                        attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                'name': 'RacketeerExtortion2',  # Compensation
                                                                'animName': 'summon-cog',
                                                                'hp': 0,
                                                                'acc': 100,
                                                                'freq': 0,
                                                                'group': SuitBattleGlobals.ATK_TGT_GROUP})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    if self.battle.activeSuits[i].currHP > 0 and self.calculator.racketeerMultiplier >= 20 and self.__suitCanAttack(suitId):
                        self.calculator.racketeerMultiplier -= (self.calculator.racketeerMultiplier / 2)
                        attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                'name': 'RacketeerOverextendedLeverage2',  # Extortion
                                                                'animName': 'nothing',
                                                                'hp': 0,
                                                                'acc': 100,
                                                                'freq': 0,
                                                                'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                        attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                'name': 'RacketeerOverextendedLeverage',  # Extortion
                                                                'animName': 'nothing',
                                                                'hp': 0,
                                                                'acc': 100,
                                                                'freq': 0,
                                                                'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    if self.__suitCanAttack(suitId):
                        damageCogs = 0
                        for suit in self.battle.activeSuits:
                            if suit.currHP <= 0:
                                continue
                            if suit.getHP() < suit.maxHP and suit.dna.name != 'racket':
                                damageCogs = 1
                        if damageCogs > 0 and self.__suitCanAttack(suitId) and self.calculator.racketeerMultiplier >= 1:
                            attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                    'name': 'RacketeerCompensation',  # Compensation
                                                                    'animName': 'nothing',
                                                                    'hp': 0,
                                                                    'acc': 100,
                                                                    'freq': 0,
                                                                    'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                            if attack[SUIT_ATK_COL]:
                                self.battle.suitAttacks.append(attack)

            for i in xrange(len(self.battle.activeSuits)):
                suitId = self.battle.activeSuits[i].doId
                if self.battle.activeSuits[i].dna.name == 'racket':
                    if self.TurnsElapsed % 1 == 0 and not self.suitHasCondition(suitId,
                                                                                'hustlingcalculator') and self.__suitCanAttack(
                            suitId):
                        attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                        'name': 'RacketeerRacketeering', # Racketeering
                        'animName': 'nothing',
                        'hp': 0,
                        'acc': 100,
                        'freq': 0,
                        'group': SuitBattleGlobals.ATK_TGT_GROUP})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
