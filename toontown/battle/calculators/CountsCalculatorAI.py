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
        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'erfit':
                if (((self.TurnsElapsed + 2) % 4 == 0) or (self.calculator.countErfitHP >= 650)) and self.__suitCanAttack(suitId):
                    livingOtherCogs = []

                    for otherSuit in self.battle.activeSuits:
                        if otherSuit.doId == suitId:
                            continue

                        if otherSuit.currHP <= 0:
                            continue

                        if self.suitHasCondition(otherSuit.doId, 'dead'):
                            continue

                        livingOtherCogs.append(otherSuit)

                    if livingOtherCogs:
                        attack = self.__getCheatAttack(suitId, {
                            'suitName': self.battle.activeSuits[i].dna.name,
                            'name': 'ErfitGainsFromTheScrap',
                            'animName': 'sacrifice-cog',
                            'hp': 0,
                            'acc': 100,
                            'freq': 0,
                            'group': SuitBattleGlobals.ATK_TGT_GROUP,
                            'targetType': 'suit',
                            'allowSelfTarget': True,
                            'targetSelf': False,
                            'excludeManagers': False,
                            'damageTarget': 'target',
                            'healTarget': 'target'
                        })
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    else:
                        attack = self.__getCheatAttack(suitId, {
                            'suitName': self.battle.activeSuits[i].dna.name,
                            'name': 'Quake',
                            'animName': 'quick-jump',
                            'hp': 40,
                            'acc': 85,
                            'freq': 0,
                            'group': SuitBattleGlobals.ATK_TGT_GROUP
                        })

                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                        attack = self.__getCheatAttack(suitId, {
                        'suitName': self.battle.activeSuits[i].dna.name,
                        'name': 'ErfitProToonShake',
                        'animName': 'nothing',
                        'hp': 0,
                        'acc': 100,
                        'freq': 0,
                        'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                        'targetType': 'suit',
                        'allowSelfTarget': False,
                        'targetSelf': False,
                         'targetHealthiest': True,
                        'excludeFullHealth': True,
                        'damageTarget': 'attacker',
                        'healTarget': 'target'
                        })

                        if not attack[SUIT_ATK_COL]:
                            # No other living Cog was available, so force Erfit to target himself.
                            attack = self.__getCheatAttack(suitId, {
                                'suitName': self.battle.activeSuits[i].dna.name,
                                'name': 'ErfitProToonShake',
                                'animName': 'nothing',
                                'hp': 0,
                                'acc': 100,
                                'freq': 0,
                                'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                                'targetType': 'suit',
                                'allowSelfTarget': True,
                                'targetSelf': True,
                                'damageTarget': 'target',
                                'healTarget': 'target'
                            })

                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'erfit':
                if (((self.TurnsElapsed + 2) % 4 == 0) or (self.calculator.countErfitHP >= 650)) and self.__suitCanAttack(suitId):
                    livingOtherCogs = []

                    for otherSuit in self.battle.activeSuits:
                        if otherSuit.doId == suitId:
                            continue

                        if otherSuit.currHP <= 0:
                            continue

                        if self.suitHasCondition(otherSuit.doId, 'dead'):
                            continue

                        livingOtherCogs.append(otherSuit)

                    if livingOtherCogs:
                        attack = self.__getCheatAttack(suitId, {
                            'suitName': self.battle.activeSuits[i].dna.name,
                            'name': 'ErfitGainsFromTheScrap',
                            'animName': 'sacrifice-cog',
                            'hp': 0,
                            'acc': 100,
                            'freq': 0,
                            'group': SuitBattleGlobals.ATK_TGT_GROUP,
                            'targetType': 'suit',
                            'allowSelfTarget': True,
                            'targetSelf': False,
                            'excludeManagers': False,
                            'damageTarget': 'target',
                            'healTarget': 'target'
                        })
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    else:
                        attack = self.__getCheatAttack(suitId, {
                            'suitName': self.battle.activeSuits[i].dna.name,
                            'name': 'Quake',
                            'animName': 'quick-jump',
                            'hp': 40,
                            'acc': 85,
                            'freq': 0,
                            'group': SuitBattleGlobals.ATK_TGT_GROUP
                        })

                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                        attack = self.__getCheatAttack(suitId, {
                        'suitName': self.battle.activeSuits[i].dna.name,
                        'name': 'ErfitProToonShake',
                        'animName': 'nothing',
                        'hp': 0,
                        'acc': 100,
                        'freq': 0,
                        'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                        'targetType': 'suit',
                        'allowSelfTarget': False,
                        'targetSelf': False,
                         'targetHealthiest': True,
                        'excludeFullHealth': True,
                        'damageTarget': 'attacker',
                        'healTarget': 'target'
                        })

                        if not attack[SUIT_ATK_COL]:
                            # No other living Cog was available, so force Erfit to target himself.
                            attack = self.__getCheatAttack(suitId, {
                                'suitName': self.battle.activeSuits[i].dna.name,
                                'name': 'ErfitProToonShake',
                                'animName': 'nothing',
                                'hp': 0,
                                'acc': 100,
                                'freq': 0,
                                'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                                'targetType': 'suit',
                                'allowSelfTarget': True,
                                'targetSelf': True,
                                'damageTarget': 'target',
                                'healTarget': 'target'
                            })

                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'erclaim':
                if not self.suitHasCondition(suitId, 'sounded') and self.suitHasCondition(suitId, 'unlureSuit') and (((self.TurnsElapsed + 3) % 4 == 0) or (self.calculator.countErclaimHP >= 650)) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getLureRemoval(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if (((self.TurnsElapsed + 3) % 4 == 0) or (self.calculator.countErclaimHP >= 650)) and self.__suitCanAttack(suitId):
                    sacrificeCandidates = []

                    for otherSuit in self.battle.activeSuits:
                        if otherSuit.doId == suitId:
                            continue

                        if otherSuit.currHP <= 0:
                            continue

                        if self.suitHasCondition(otherSuit.doId, 'dead'):
                            continue

                        sacrificeCandidates.append(otherSuit)

                    if sacrificeCandidates:
                        attack = self.__getCheatAttack(suitId, {
                            'suitName': self.battle.activeSuits[i].dna.name,
                            'name': 'ErclaimSacrifice',
                            'animName': 'quick-jump',
                            'hp': 0,
                            'acc': 100,
                            'freq': 0,
                            'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                            'targetType': 'suit',
                            'allowSelfTarget': False,
                            'targetSelf': False,
                            'targetWeakest': True,
                            'damageTarget': 'target',
                            'healTarget': 'attacker'
                        })
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)

                    else:
                        attack = self.__getCheatAttack(suitId, {
                            'suitName': self.battle.activeSuits[i].dna.name,
                            'name': 'Quake',
                            'animName': 'quick-jump',
                            'hp': 40,
                            'acc': 85,
                            'freq': 0,
                            'group': SuitBattleGlobals.ATK_TGT_GROUP
                        })

                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                        attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                        'name': 'ErclaimLaffSteal', # Syphon Movie
                        'animName': 'magic1',
                        'hp': 0,
                        'acc': 100,
                        'freq': 0, # Professor Control: I do not know how relevant attack frequency is, but keep it anyway.
                        'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                if not self.suitHasCondition(suitId, 'sounded') and self.suitHasCondition(suitId, 'unlureSuit') and (((self.TurnsElapsed + 3) % 4 == 0) and (self.calculator.countErclaimHP >= 650)) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getLureRemoval(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if (((self.TurnsElapsed + 3) % 4 == 0) and (self.calculator.countErclaimHP >= 650)) and self.__suitCanAttack(suitId):
                    sacrificeCandidates = []

                    for otherSuit in self.battle.activeSuits:
                        if otherSuit.doId == suitId:
                            continue

                        if otherSuit.currHP <= 0:
                            continue

                        if self.suitHasCondition(otherSuit.doId, 'dead'):
                            continue

                        sacrificeCandidates.append(otherSuit)

                    if sacrificeCandidates:
                        attack = self.__getCheatAttack(suitId, {
                            'suitName': self.battle.activeSuits[i].dna.name,
                            'name': 'ErclaimSacrifice',
                            'animName': 'quick-jump',
                            'hp': 0,
                            'acc': 100,
                            'freq': 0,
                            'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                            'targetType': 'suit',
                            'allowSelfTarget': False,
                            'targetSelf': False,
                            'targetWeakest': True,
                            'damageTarget': 'target',
                            'healTarget': 'attacker'
                        })
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)

                    else:
                        attack = self.__getCheatAttack(suitId, {
                            'suitName': self.battle.activeSuits[i].dna.name,
                            'name': 'Quake',
                            'animName': 'quick-jump',
                            'hp': 40,
                            'acc': 85,
                            'freq': 0,
                            'group': SuitBattleGlobals.ATK_TGT_GROUP
                        })

                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
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
                                                                'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                                        'targetType': 'none'})
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
                    attack = self.__getCheatAttack(suitId, {
                        'suitName': self.battle.activeSuits[i].dna.name,
                        'name': 'ErfitPersonalTrainer',
                        'animName': 'summon-cog',
                        'hp': 0,
                        'acc': 100,
                        'freq': 0,
                        'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                        'targetType': 'suit',
                        'allowSelfTarget': True,
                        'targetSelf': True,
                        'excludeManagers': False,
                        'damageTarget': 'target',
                        'healTarget': 'target'
                    })

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
                                                                'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                                        'targetType': 'none'})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
