from toontown.battle.BattleBase import *
from toontown.battle.BattleGlobals import *
from toontown.battle import SuitBattleGlobals
import random
import math

class CountsCalculatorAI:

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

    def calculateSuitAttacksCounts(self):
        x = self.TurnsElapsed
        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'erfit':
                attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'ErfitHydrationCheckRevert',  # Extra Tip
                                                            'animName': 'throw-object',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_GROUP})
                if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)

        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'erfit':
                if not self.suitHasCondition(suitId, 'sounded') and self.suitHasCondition(suitId, 'unlureSuit') and ((self.countErfitHP >= 650) or (self.TurnsElapsed + 2) % 4 == 0):
                    attack = self.__getLureRemoval(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if (((self.TurnsElapsed + 2) % 4 == 0) or (self.countErfitHP >= 650)) and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'TargetCheck', # Target Check for Throw Book
                     'animName': 'nothing',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                # if self.getSuitConditionModifier(suitId, 'targetCheckCondition') > -1 and self.battle.activeSuits[i].currHP > 0:
                #     attack = self.__getLureRemoval(suitId)
                #     if attack[SUIT_ATK_COL]:
                        # self.battle.suitAttacks.append(attack)
        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'erfit':
                if (((self.TurnsElapsed + 2) % 4 == 0) or (self.countErfitHP >= 650)) and not (self.suitHasCondition(suitId, 'targetCheckCondition') and self.getSuitConditionModifier(suitId, 'targetCheckCondition') > -1) and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'Quake', # Target Check for Throw Book
                     'animName': 'quick-jump',
                     'hp': 40,
                     'acc': 85,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_GROUP})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if (((self.TurnsElapsed + 2) % 4 == 0) or (self.countErfitHP >= 650)) and not (self.suitHasCondition(suitId, 'targetCheckCondition') and self.getSuitConditionModifier(suitId, 'targetCheckCondition') > -1) and self.syphonHP.get(suitId, 0) > 0 and not self.suitHasCondition(suitId, 'dead') and self.battle.activeSuits[i].currHP > 0 and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                    'name': 'ErfitProToonShake', # Syphon Movie
                    'animName': 'nothing',
                    'hp': 0,
                    'acc': 100,
                    'freq': 0, # Professor Control: I do not know how relevant attack frequency is, but keep it anyway.
                    'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'targetCheckCondition') and self.getSuitConditionModifier(suitId, 'targetCheckCondition') > -1 and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                      'name': 'ErfitGainsFromTheScrap', 
                     'animName': 'sacrifice-cog',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.suitHasCondition(suitId, 'erfitHeal') and self.battle.activeSuits[i].currHP > 0:
                attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                'name': 'ErfitPhase2', # Syphon Movie
                'animName': 'nothing',
                'hp': 0,
                'acc': 100,
                'freq': 0, # Professor Control: I do not know how relevant attack frequency is, but keep it anyway.
                'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'erfit':
                if (((self.TurnsElapsed + 2) % 4 == 0) and (self.countErfitHP >= 650)) and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'Quake', # Target Check for Throw Book
                     'animName': 'quick-jump',
                     'hp': 40,
                     'acc': 85,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_GROUP})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if (((self.TurnsElapsed + 2) % 4 == 0) and (self.countErfitHP >= 650)) and self.syphonHP.get(suitId, 0) > 0 and not self.suitHasCondition(suitId, 'dead') and self.battle.activeSuits[i].currHP > 0 and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'ErfitProToonShake', # Syphon Movie
                    'animName': 'nothing',
                    'hp': 0,
                    'acc': 100,
                    'freq': 0, # Professor Control: I do not know how relevant attack frequency is, but keep it anyway.
                    'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.suitHasCondition(suitId, 'erfitHeal') and self.battle.activeSuits[i].currHP > 0:
                attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                'name': 'ErfitPhase2', # Syphon Movie
                'animName': 'nothing',
                'hp': 0,
                'acc': 100,
                'freq': 0, # Professor Control: I do not know how relevant attack frequency is, but keep it anyway.
                'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'erclaim':
                if not self.suitHasCondition(suitId, 'sounded') and self.suitHasCondition(suitId, 'unlureSuit') and ((self.countErclaimHP >= 650) or (self.TurnsElapsed + 3) % 4 == 0):
                    attack = self.__getLureRemoval(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if (((self.TurnsElapsed + 3) % 4 == 0) or (self.countErclaimHP >= 650)) and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'TargetCheck', # Target Check for Throw Book
                     'animName': 'nothing',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                # if self.getSuitConditionModifier(suitId, 'targetCheckCondition') > -1 and self.battle.activeSuits[i].currHP > 0:
                #     attack = self.__getLureRemoval(suitId)
                #     if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if (((self.TurnsElapsed + 3) % 4 == 0) or (self.countErclaimHP >= 650)) and not (self.suitHasCondition(suitId, 'targetCheckCondition') and self.getSuitConditionModifier(suitId, 'targetCheckCondition') > -1) and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'Quake', # Target Check for Throw Book
                     'animName': 'quick-jump',
                     'hp': 40,
                     'acc': 85,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_GROUP})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if (((self.TurnsElapsed + 3) % 4 == 0) or (self.countErclaimHP >= 650)) and not (self.suitHasCondition(suitId, 'targetCheckCondition') and self.getSuitConditionModifier(suitId, 'targetCheckCondition') > -1) and self.syphonHP.get(suitId, 0) > 0 and not self.suitHasCondition(suitId, 'dead') and self.battle.activeSuits[i].currHP > 0 and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                    'name': 'ErclaimLaffSteal', # Syphon Movie
                    'animName': 'magic1',
                    'hp': 0,
                    'acc': 100,
                    'freq': 0, # Professor Control: I do not know how relevant attack frequency is, but keep it anyway.
                    'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'targetCheckCondition') and self.getSuitConditionModifier(suitId, 'targetCheckCondition') > -1 and self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                      'name': 'ErclaimSacrifice', 
                     'animName': 'quick-jump',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if (((self.TurnsElapsed + 3) % 4 == 0) and (self.countErclaimHP >= 650)) and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'Quake', # Target Check for Throw Book
                     'animName': 'quick-jump',
                     'hp': 40,
                     'acc': 85,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_GROUP})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if (((self.TurnsElapsed + 3) % 4 == 0) and (self.countErclaimHP >= 650)) and self.syphonHP.get(suitId, 0) > 0 and not self.suitHasCondition(suitId, 'dead') and self.battle.activeSuits[i].currHP > 0 and self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                    'name': 'ErclaimLaffSteal', # Syphon Movie
                    'animName': 'magic1',
                    'hp': 0,
                    'acc': 100,
                    'freq': 0, # Professor Control: I do not know how relevant attack frequency is, but keep it anyway.
                    'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'erclaim':
                if (x + 1) % 4 == 0 and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                'name': 'ErclaimScopeCreep',  # Extra Tip
                                                                'animName': 'effort',
                                                                'hp': 0,
                                                                'acc': 100,
                                                                'freq': 0,
                                                                'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)

        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'erfit':
                if not self.suitHasCondition(suitId, 'sounded') and self.suitHasCondition(suitId, 'unlureSuit') and len(self.battle.activeSuits) < 5 and self.TurnsElapsed % 2 == 0:
                    attack = self.__getLureRemoval(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if len(self.battle.activeSuits) < 5 and self.battle.activeSuits[i].currHP > 0 and self.TurnsElapsed % 2 == 0:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                'name': 'ErfitPersonalTrainer',  # Extra Tip
                                                                'animName': 'summon-cog',
                                                                'hp': 0,
                                                                'acc': 100,
                                                                'freq': 0,
                                                                'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)

        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'erclaim':
                if self.deadSuits > 0 and not self.suitHasCondition(suitId, 'sounded') and not self.suitHasCondition(suitId, 'alreadyCogSpawn') and self.suitHasCondition(suitId, 'unlureSuit') and len(self.battle.activeSuits) < 7:
                    attack = self.__getLureRemoval(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.deadSuits > 0 and self.battle.activeSuits[i].currHP > 0 and not self.suitHasCondition(suitId, 'alreadyCogSpawn') and len(self.battle.activeSuits) < 7:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                'name': 'ErclaimRiseFromTheScrap',  # Extra Tip
                                                                'animName': 'effort',
                                                                'hp': 0,
                                                                'acc': 100,
                                                                'freq': 0,
                                                                'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
