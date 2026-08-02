from toontown.battle.BattleBase import *
from toontown.battle.BattleGlobals import *
from toontown.battle import SuitBattleGlobals
import random
import math

class BoardbotLitigationCalculatorAI:

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

    def calculateSuitAttacksBoardbotLitigation(self):
        for i in xrange(len(self.battle.activeSuits)):  # Cheats before Cog Attacks
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'rkeeper':
                if self.suitHasCondition(suitId, 'bannedGagUsed') and not self.suitHasCondition(suitId, 'sounded') and self.suitHasCondition(suitId, 'unlureSuit') and self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getLureRemoval(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'bannedGagUsed') and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'RecordkeeperMinutesTakenContingency',  # Audit
                                            'animName': 'throw-object',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if not self.suitHasCondition(suitId, 'sounded') and self.suitHasCondition(suitId, 'unlureSuit') and self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getLureRemoval(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.battle.activeSuits[i].currHP > 0 and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'RecordkeeperMinutesTaken',  # Audit
                                            'animName': 'throw-paper',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'cdirector':
                if self.battle.activeSuits[i].currHP < 13000 and not self.suitHasCondition(suitId, 'alreadyRisk1'):
                    self.setSuitCondition(suitId, 'risk1', 1, 10, 'setBoth')
                    self.contingencyThresholds += 1
                if self.battle.activeSuits[i].currHP <= 12000 and not self.suitHasCondition(suitId, 'alreadyRisk2'):
                    self.setSuitCondition(suitId, 'risk2', 1, 10, 'setBoth')
                    self.contingencyThresholds += 1
                if self.battle.activeSuits[i].currHP <= 11000 and not self.suitHasCondition(suitId, 'alreadyRisk3'):
                    self.setSuitCondition(suitId, 'risk3', 1, 10, 'setBoth')
                    self.contingencyThresholds += 1
                if self.battle.activeSuits[i].currHP <= 10000 and not self.suitHasCondition(suitId, 'alreadyRisk4'):
                    self.setSuitCondition(suitId, 'risk4', 1, 10, 'setBoth')
                    self.contingencyThresholds += 1
                if self.battle.activeSuits[i].currHP <= 9000 and not self.suitHasCondition(suitId, 'alreadyRisk5'):
                    self.setSuitCondition(suitId, 'risk5', 1, 10, 'setBoth')
                    self.contingencyThresholds += 1
                if self.battle.activeSuits[i].currHP <= 8000 and not self.suitHasCondition(suitId, 'alreadyRisk6'):
                    self.setSuitCondition(suitId, 'risk6', 1, 10, 'setBoth')
                    self.contingencyThresholds += 1
                if self.battle.activeSuits[i].currHP <= 7000 and not self.suitHasCondition(suitId, 'alreadyRisk7'):
                    self.setSuitCondition(suitId, 'risk7', 1, 10, 'setBoth')
                    self.contingencyThresholds += 1
                if self.battle.activeSuits[i].currHP <= 6000 and not self.suitHasCondition(suitId, 'alreadyRisk8'):
                    self.setSuitCondition(suitId, 'risk8', 1, 10, 'setBoth')
                    self.contingencyThresholds += 1
                # if self.suitHasCondition(suitId, 'bannedGagUsed') and not self.suitHasCondition(suitId, 'sounded') and self.suitHasCondition(suitId, 'unlureSuit') and self.__suitCanAttack(suitId) and  self.battle.activeSuits[i].currHP > 0:
                #     attack = self.__getLureRemoval(suitId)
                #     if attack[SUIT_ATK_COL]:
                        # self.battle.suitAttacks.append(attack)
                # if self.suitHasCondition(suitId, 'bannedGagUsed') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[
                #     i].currHP > 0:
                #     attack = self.__getAbilityQueued(suitId)
                #     if attack[SUIT_ATK_COL]:
                        # self.battle.suitAttacks.append(attack)
                # if self.suitHasCondition(suitId, 'bannedGagUsed') and self.__suitCanAttack(suitId):
                #     attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                #                                             'name': 'ContingencyContingencyClauseRetaliation',
                #                                             'animName': 'glower',
                #                                             'hp': 0,
                #                                             'acc': 100,
                #                                             'freq': 0,
                #                                             'group': SuitBattleGlobals.ATK_TGT_GROUP})
                #     if attack[SUIT_ATK_COL]:
                        # self.battle.suitAttacks.append(attack)
                if self.contingencyThresholds > 0 and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                     'name': 'ContingencyRiskThresholdBreach',
                                    'animName': 'revvedup',
                                     'hp': 0,
                                     'acc': 100,
                                     'freq': 0,
                                     'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'risk1') and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'ContingencyMarkRevisedFiling',
                     'animName': 'revvedup',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'risk2') and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'ContingencyMarkRevisedFiling',
                     'animName': 'revvedup',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'risk3') and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'ContingencyMarkRevisedFiling',
                     'animName': 'revvedup',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'risk4') and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'ContingencyMarkRevisedFiling',
                    'animName': 'revvedup',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'risk5') and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'ContingencyMarkRevisedFiling',
                     'animName': 'revvedup',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'risk6') and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'ContingencyMarkRevisedFiling',
                     'animName': 'revvedup',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'risk7') and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'ContingencyMarkRevisedFiling',
                     'animName': 'revvedup',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'risk8') and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'ContingencyMarkRevisedFiling',
                    'animName': 'revvedup',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)

        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if not self.suitHasCondition(suitId, 'alreadyMelted') and self.suitHasCondition(suitId, 'marketMeltdown'):
                attack = self.__getCheatAttack(suitId, {'suitName': '',
                                            'name': 'DividendTotalMarketMeltdownDamage',  # Insurance for when Case Manager is defeated
                                            'animName': 'nothing',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_GROUP})
                if attack[SUIT_ATK_COL]:
                    self.battle.suitAttacks.append(attack)

            if not self.suitHasCondition(suitId, 'dotfinished'):
                self.__appendToonConditionDamageAndRetaliation(
                    condition='liquidated',
                    damage=30,
                    damageMovie='DividendLiquidationEventDamage',
                    retaliateAtTurns=[1],
                    retaliations=[
                        {
                            'suitNames': ['cdirector'],
                            'movie': 'ContingencyMarkLiquidated',
                            'animName': 'throw-object',
                            'hp': 5,
                            'queueCondition': 'markedcalculator2',
                        },
                        {
                            'suitNames': ['cbutcher'],
                            'movie': 'RecordkeeperRevisedfilingLiquidation',
                            'animName': 'magic2',
                            'hp': 33, 
                            'queueCondition': 'liquidationRetaliation',
                        }
                    ]
                )
            # if self.battle.activeSuits[i].dna.name == 'dking':
            #     if self.TurnsElapsed % 1 == 0:
            #         attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
            #          'name': 'DividendLiquidationEventDamage', # Insurance Healing
            #          'animName': 'nothing',
            #          'hp': 0,
            #          'acc': 100,
            #          'freq': 0,
            #          'group': SuitBattleGlobals.ATK_TGT_GROUP})
            #         if attack[SUIT_ATK_COL]:
            #             self.battle.suitAttacks.append(attack)
        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'liquid':
                if self.suitHasCondition(suitId, 'tollmasterHit') and not self.suitHasCondition(suitId, 'finalToll') and self.battle.activeSuits[
                    i].currHP > 0:
                        attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                'name': 'TollmasterMandatoryToll',  # Audit
                                                                'animName': 'nothing',
                                                                'hp': 0,
                                                                'acc': 100,
                                                                'freq': 0,
                                                                'group': SuitBattleGlobals.ATK_TGT_GROUP})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'cdirector':
                if self.suitHasCondition(suitId, 'contingencyHit') and self.suitHasCondition(suitId, 'alreadyFailsafeProtocol') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[
                    i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'contingencyHit') and self.suitHasCondition(suitId, 'alreadyFailsafeProtocol') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'ContingencyFailsafeProtocol',
                                                            'animName': 'nothing',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                damageCogs = 0
                if self.suitHasCondition(suitId, 'redundantcalculator') and self.battle.activeSuits[i].currHP > 0:
                    for suit in self.battle.activeSuits:
                        if suit.currHP <= 0:
                            continue
                        if suit.getHP() > 0 and suit.dna.name != 'cdirector':
                            damageCogs += 1
                if self.suitHasCondition(suitId, 'redundantcalculator') and not damageCogs > 2 and self.battle.activeSuits[
                    i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'redundantcalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[
                    i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'redundantcalculator') and self.suitHasCondition(suitId, 'highpressurecalculator') and self.__suitCanAttack(suitId):
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if damageCogs > 2 and self.suitHasCondition(suitId, 'redundantcalculator') and not self.suitHasCondition(suitId, 'highpressurecalculator') and self.__suitCanAttack(suitId) and len(self.battle.activeSuits) > 1:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'ContingencyRedundantAuthority',
                                                            'animName': 'scabbard',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'highpressurecalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'highpressurecalculator') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'SafetyHighPressure', # High Pressure
                     'animName': 'throw-object',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_GROUP})
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
            if self.battle.activeSuits[i].dna.name == 'dking':
                if self.suitHasCondition(suitId, 'marketcalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[
                    i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'marketcalculator') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, random.choice(({'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'DividendTotalMarketMeltdown',  # Audit
                                                            'animName': 'magic3',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_GROUP}, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'DividendTotalMarketMeltdown2',  # Audit
                                                            'animName': 'magic3',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_GROUP})))
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                    for i in range(len(self.suitStatusConditionsNew[suitId])):
                        if isinstance(self.suitStatusConditionsNew[suitId][i], StatusEffects.ExtraAttacks):  # Do they have any extra attacks?
                            self.suitStatusConditionsNew[suitId][i].extraAttacks += 1  # Add one more attack.
                            break
                    else:
                        self.suitStatusConditionsNew[suitId].append(StatusEffects.ExtraAttacks(1))
            if self.battle.activeSuits[i].dna.name == 'cbutcher':
                if not self.__suitCanAttack(suitId) and self.battle.activeSuits[
                    i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'RecordkeeperPaperTrail',  # Audit
                                                            'animName': 'magic2',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'rkeeper':
                if self.battle.activeSuits[i].currHP > 0 and self.suitHasCondition(suitId, 'costscalculator'):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'RecordkeeperMinutesTakenDamage',  # Audit
                                            'animName': 'nothing',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_GROUP})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)

        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'liquid':
                for suit in self.battle.activeSuits:
                    if not suit.getManager() and (suit.currHP < suit.maxHP) and suit.currHP > 0 and not suit.getGovernaught():
                        if (self.TurnsElapsed + 1) % 3 == 0:
                            self.calculator.sacrificedCogs += 1
                            self.calculator.syphonedHP += suit.currHP
                if self.sacrificedCogs > 0 and self.suitHasCondition(suitId, 'unlureSuit') and not self.suitHasCondition(suitId, 'sounded') and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getLureRemoval(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.sacrificedCogs > 0 and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'TollmasterBalanceTheLedger',  # Extra Attack for Dead Suits
                                                            'animName': 'nothing',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                        self.syphonedHP *= 0
                # if self.sacrificedCogs == 2 and self.battle.activeSuits[i].currHP > 0:
                #     attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                #                                             'name': 'TollmasterBalanceTheLedger2',  # Extra Attack for Dead Suits
                #                                             'animName': 'nothing',
                #                                             'hp': 0,
                #                                             'acc': 100,
                #                                             'freq': 0,
                #                                             'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                #     if attack[SUIT_ATK_COL]:
                        # self.battle.suitAttacks.append(attack)
                # if self.sacrificedCogs == 3 and self.battle.activeSuits[i].currHP > 0:
                #     attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                #                                             'name': 'TollmasterBalanceTheLedger3',  # Extra Attack for Dead Suits
                #                                             'animName': 'nothing',
                #                                             'hp': 0,
                #                                             'acc': 100,
                #                                             'freq': 0,
                #                                             'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                #     if attack[SUIT_ATK_COL]:
                        # self.battle.suitAttacks.append(attack)
                # if self.sacrificedCogs == 4 and self.battle.activeSuits[i].currHP > 0:
                #     attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                #                                             'name': 'TollmasterBalanceTheLedger4',  # Extra Attack for Dead Suits
                #                                             'animName': 'nothing',
                #                                             'hp': 0,
                #                                             'acc': 100,
                #                                             'freq': 0,
                #                                             'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                #     if attack[SUIT_ATK_COL]:
                        # self.battle.suitAttacks.append(attack)
                # if self.sacrificedCogs >= 5 and self.battle.activeSuits[i].currHP > 0:
                #     attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                #                                             'name': 'TollmasterBalanceTheLedger5',  # Extra Attack for Dead Suits
                #                                             'animName': 'nothing',
                #                                             'hp': 0,
                #                                             'acc': 100,
                #                                             'freq': 0,
                #                                             'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                #     if attack[SUIT_ATK_COL]:
                        # self.battle.suitAttacks.append(attack)

        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'dking':
                if self.deadSuits == 1 and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'TollmasterResonanceTax',  # Extra Attack for Dead Suits
                                                            'animName': 'calculator',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.deadSuits == 2 and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'TollmasterResonanceTax2',  # Extra Attack for Dead Suits
                                                            'animName': 'calculator',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.deadSuits == 3 and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'TollmasterResonanceTax3',  # Extra Attack for Dead Suits
                                                            'animName': 'calculator',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.deadSuits == 4 and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'TollmasterResonanceTax4',  # Extra Attack for Dead Suits
                                                            'animName': 'calculator',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.deadSuits > 4 and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'TollmasterResonanceTax5',  # Extra Attack for Dead Suits
                                                            'animName': 'calculator',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            # if self.TurnsElapsed % 1 == 0 and not self.suitHasCondition(suitId, 'dotfinished') and self.battle.activeSuits[i].dna.name in ['cdirector', 'rkeeper', 'liquid'] and not self.battle.activeSuits[i].dna.name == 'dking':
            #     attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
            #         'name': 'DividendLiquidationEventDamage',
            #         'animName': 'nothing',
            #         'hp': 0,
            #         'acc': 100,
            #         'freq': 0,
            #         'group': SuitBattleGlobals.ATK_TGT_GROUP})
            #     if attack[SUIT_ATK_COL]:
            #         self.battle.suitAttacks.append(attack)

        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'cdirector':
                if self.suitHasCondition(suitId, 'markedcalculator2') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[
                    i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'markedcalculator2') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'ContingencyMarkLiquidated', # Insurance Healing
                     'animName': 'throw-object',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            #     if self.suitHasCondition(suitId, 'liquidationRetaliation') and self.suitHasCondition(suitId, 'alreadySecondAttack') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[
            #         i].currHP > 0:
            #         attack = self.__getAbilityQueued(suitId)
            #         if attack[SUIT_ATK_COL]:
                        # self.battle.suitAttacks.append(attack)
            #     if self.suitHasCondition(suitId, 'liquidationRetaliation') and self.suitHasCondition(suitId, 'alreadySecondAttack') and self.__suitCanAttack(suitId):
            #         attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
            #          'name': 'ContingencyMarkLiquidated', # Insurance Healing
            #          'animName': 'nothing',
            #          'hp': 0,
            #          'acc': 100,
            #          'freq': 0,
            #          'group': SuitBattleGlobals.ATK_TGT_GROUP})
            #         if attack[SUIT_ATK_COL]:
                        # self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'cbutcher':
                if self.suitHasCondition(suitId, 'liquidationRetaliation') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[
                    i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'liquidationRetaliation') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'RecordkeeperRevisedFilingLiquidation', # Insurance Healing
                     'animName': 'magic2',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)

        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'dking':
                # if self.suitHasCondition(suitId, 'scabbardcalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[
                #     i].currHP > 0:
                #     attack = self.__getAbilityQueued(suitId)
                #     if attack[SUIT_ATK_COL]:
                        # self.battle.suitAttacks.append(attack)
                # if self.suitHasCondition(suitId, 'scabbardcalculator') and self.__suitCanAttack(suitId):
                #     attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                #                                             'name': 'DividendPeckingOrder',  # Audit
                #                                             'animName': 'nothing',
                #                                             'hp': 0,
                #                                             'acc': 100,
                #                                             'freq': 0,
                #                                             'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                #     if attack[SUIT_ATK_COL]:
                        # self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'embezzlecalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[
                    i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'embezzlecalculator') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'DividendPeckingOrderZapped',  # Audit
                                                            'animName': 'pickpocket',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'cdirector':
                if self.suitHasCondition(suitId, 'alreadyAbsorbingContingency') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[
                    i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'alreadyAbsorbingContingency') and not self.suitHasCondition(suitId, 'shielding') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'ContingencyRiskThresholdBreach75',
                     'animName': 'defense',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'rkeeper':
                if self.suitHasCondition(suitId, 'revisedcalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[
                    i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'revisedcalculator') and self.__suitCanAttack(suitId):
                    if self.battle.activeSuits[i].currHP <= 1000:
                        attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                'name': 'RecordkeeperRevisedFiling',  # Audit
                                                                'animName': 'snap',
                                                                'hp': 0,
                                                                'acc': 100,
                                                                'freq': 0,
                                                                'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    elif self.battle.activeSuits[i].currHP <= 2000:
                        attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                'name': 'RecordkeeperRevisedFiling',  # Audit
                                                                'animName': 'snap',
                                                                'hp': 0,
                                                                'acc': 100,
                                                                'freq': 0,
                                                                'group': SuitBattleGlobals.ATK_TGT_DOUBLE})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    else:
                        attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                'name': 'RecordkeeperRevisedFiling',  # Audit
                                                                'animName': 'snap',
                                                                'hp': 0,
                                                                'acc': 100,
                                                                'freq': 0,
                                                                'group': SuitBattleGlobals.ATK_TGT_TRIPLE})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'phantomEntrycalculator') and self.battle.activeSuits[
                    i].currHP > 0 and (len(self.battle.activeSuits) < 7 or self.deadSuits > 0):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'RecordkeeperPhantomEntrySpawn',  # Audit
                                                            'animName': 'effort',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)

        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'dking':
                if self.suitHasCondition(suitId, 'liquidationcalculator2') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[
                    i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'liquidationcalculator2') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                'name': 'DividendLiquidationEvent',  # Audit
                                                                'animName': 'magic1',
                                                                'hp': 0,
                                                                'acc': 100,
                                                                'freq': 0,
                                                                'group': random.choice((SuitBattleGlobals.ATK_TGT_DOUBLE, SuitBattleGlobals.ATK_TGT_SINGLE))})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                    self.setSuitCondition(suitId, 'liquidationcalculator2', 0, 0, 'setBoth')
                if self.suitHasCondition(suitId, 'liquidationcalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[
                    i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'liquidationcalculator') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                'name': 'DividendLiquidationEvent',  # Audit
                                                                'animName': 'magic1',
                                                                'hp': 0,
                                                                'acc': 100,
                                                                'freq': 0,
                                                                'group': random.choice((SuitBattleGlobals.ATK_TGT_DOUBLE, SuitBattleGlobals.ATK_TGT_SINGLE))})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'liquid':
                if self.battle.activeSuits[i].currHP <= 2614 and not self.suitHasCondition(suitId, 'finalToll') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[
                    i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.battle.activeSuits[i].currHP <= 2614 and not self.suitHasCondition(suitId, 'finalToll') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'TollmasterMandatoryTollFinal',  # Budget Cuts Gag Ban Retaliation
                                                            'animName': 'nothing',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_GROUP})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'rushHourcalculator') and not self.suitHasCondition(suitId, 'finalToll') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'rushHourcalculator') and not self.suitHasCondition(suitId, 'finalToll') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'TollmasterRushHour',  # Budget Cuts Gag Ban Retaliation
                                                            'animName': 'nothing',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_GROUP})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'cdirector':
                currentBossHealth = -1
                for s in self.battle.suits:
                    if s.getManager() and not s.dna.name == 'cdirector':
                        currentBossHealth = s.currHP
                if self.battle.activeSuits[i].currHP <= 4000 and currentBossHealth > 0 and not self.suitHasCondition(suitId, 'phase3') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'ContingencyForecastCollapse',
                     'animName': 'speak',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'alreadyContingency') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'BanLevel%s' % random.choice(['45', '46', '47', '48', '56', '57', '58', '67', '68', '78']), # Gag Bans
                     'animName': 'sparkplug',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_GROUP})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'alreadyOperationalFreeze') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'Ban%s' % random.choice(['ToonupTrap', 'ToonupLure', 'ToonupThrow', 'ToonupSquirt', 'ToonupZap', 'ToonupSound', 'ToonupDrop', 'TrapLure', 'TrapThrow', 'TrapSquirt', 'TrapZap', 'TrapSound', 'TrapDrop', 'LureThrow', 'LureSquirt', 'LureZap', 'LureSound', 'LureDrop', 'ThrowSquirt', 'ThrowZap', 'ThrowSound', 'ThrowDrop', 'SquirtZap', 'SquirtSound', 'SquirtDrop', 'ZapSound', 'ZapDrop', 'SoundDrop']),
                     'animName': 'sparkplug',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_GROUP})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                # if self.suitHasCondition(suitId, 'alreadyContingency') and self.__suitCanAttack(suitId):
                #     attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                #                                             'name': 'ContingencyContingencyClause',
                #                                             'animName': 'throw-object',
                #                                             'hp': 0,
                #                                             'acc': 100,
                #                                             'freq': 0,
                #                                             'group': SuitBattleGlobals.ATK_TGT_GROUP})
                #     if attack[SUIT_ATK_COL]:
                      #  self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'alreadyContent') and not self.suitHasCondition(suitId, 'contentSyncCalculator') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'ContingencyOperationalFreeze',
                                                            'animName': 'snap',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_GROUP})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'rkeeper':
                if self.TurnsElapsed % 1 == 0 and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'RecordkeeperAuditCycle',
                                                            'animName': 'calculating-costs',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_GROUP})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)