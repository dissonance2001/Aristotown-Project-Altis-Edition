from toontown.battle.BattleBase import *
from toontown.battle.BattleGlobals import *
from toontown.battle import SuitBattleGlobals
import random
import math

class DirectorsCalculatorAI:

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

    def calculateSuitAttacksDirectors(self):
        x = self.TurnsElapsed
        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId

        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId

        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'dola':
                if not self.suitHasCondition(suitId, 'sounded') and self.suitHasCondition(suitId, 'unlureSuit') and self.suitHasCondition(suitId, 'inkDraincalculator'):
                    attack = self.__getLureRemoval(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'inkDraincalculator'):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'DOLAInkDrain',  # Extra Tip
                                                            'animName': 'effort',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_GROUP})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)

        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'derrman':
                if not self.suitHasCondition(suitId, 'sounded') and self.suitHasCondition(suitId, 'unlureSuit') and self.suitHasCondition(suitId, 'refinementDerrick'):
                    attack = self.__getLureRemoval(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'refinementDerrick'):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'DerrickManRefinement',  # Extra Tip
                                                            'animName': 'throw-object',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
