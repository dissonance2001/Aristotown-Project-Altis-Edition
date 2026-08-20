from __future__ import absolute_import
from toontown.battle.BattleBase import *
from toontown.battle.BattleGlobals import *
from toontown.battle import SuitBattleGlobals
import random
import math
from six.moves import range

# LawbotLitigationCalculatorAI.py

class LawbotLitigationCalculatorAI:

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

    def calculateSuitAttacksLawbotLitigation(self):
        for i in range(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'lgator':
                if self.suitHasCondition(suitId, 'snappedcalculator2') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'snappedcalculator2') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'LitigatorSnapBindings',  # Snap Bindings Retaliation
                                                            'animName': 'throw-object',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'stenog':
                if self.suitHasCondition(suitId, 'sanctioncalculator3') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'StenographerSanctionSuppression',  # Court Sanction Suppression Retaliation
                                                            'animName': 'sanction',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'sanctioncalculator2') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'StenographerSanctionBindings',  # Court Sanction Legal Bindings Retaliation
                                                            'animName': 'sanction',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
        for i in range(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId

            # Gag Ban Retaliations & DOT
            if self.battle.activeSuits[i].dna.name == 'sgoat' and not self.suitHasCondition(suitId, 'enraged'):
                attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'ScapegoatRageBuilding',  # Suppression Revert
                                            'animName': 'nothing',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE,

                        'targetType': 'suit',
                        'applyDamage': False,
                        'targetSelf': True,})
                if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'sgoat':
                self.__appendToonConditionDamageAndRetaliation(
                    condition='hidden',
                    damage=25,
                    damageMovie='ScapegoatBarnyardBash',
                    retaliations=[
                        {
                            'suitNames': ['stenog'],
                            'movie': 'StenographerSanctionSuppression',
                            'animName': 'sanction',
                            'hp': 25,
                            'queueCondition': 'sanctioncalculator3',
                        }
                    ]
                )


        for i in range(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if not self.suitHasCondition(suitId, 'dotfinished'):
                self.__appendToonConditionDamageAndRetaliation(
                    condition='bound',
                    damage=20,
                    damageMovie='CaseManagerLegallyBound',
                    retaliateAtTurns=[1],
                    retaliations=[
                        {
                            'suitNames': ['stenog'],
                            'movie': 'StenographerSanctionBindings',
                            'animName': 'sanction',
                            'hp': 25,
                            'queueCondition': 'sanctioncalculator2',
                        },
                        {
                            'suitNames': ['lgator'],
                            'movie': 'LitigatorSnapBindings',
                            'animName': 'throw-object',
                            'hp': 33, 
                            'queueCondition': 'snappedcalculator2',
                        }
                    ]
                )

            # Gag Ban Retaliations & DOT
            # if self.battle.activeSuits[i].dna.name == 'caseman':
            #     if self.TurnsElapsed % 1 == 0:
            #         attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
            #          'name': 'CaseManagerInsurance', # Insurance Healing
            #          'animName': 'nothing',
            #          'hp': 0,
            #          'acc': 100,
            #          'freq': 0,
            #          'group': SuitBattleGlobals.ATK_TGT_SINGLE})
            #         if attack[SUIT_ATK_COL]:
            #             self.battle.suitAttacks.append(attack)
                # if self.TurnsElapsed % 1 == 0:
                #     attack = self.__getCheatAttack(suitId, {'suitName': '',
                #      'name': 'CaseManagerLegallyBound', # Legally Bound
                #      'animName': 'nothing',
                #      'hp': 0,
                #      'acc': 100,
                #      'freq': 0,
                #      'group': SuitBattleGlobals.ATK_TGT_GROUP})
                #     if attack[SUIT_ATK_COL]:
                        # self.battle.suitAttacks.append(attack)

            # Primary Cheats
        for i in range(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            # if self.suitHasCondition(suitId, 'deadcase') and not self.suitHasCondition(suitId, 'dotfinished') and not self.battle.activeSuits[i].dna.name == 'caseman':
            #     attack = self.__getCheatAttack(suitId, {'suitName': '',
            #                                 'name': 'CaseManagerLegallyBound',  # Legally Bound for when Case Manager is defeated
            #                                 'animName': 'nothing',
            #                                 'hp': 0,
            #                                 'acc': 100,
            #                                 'freq': 0,
            #                                 'group': SuitBattleGlobals.ATK_TGT_GROUP})
            #     if attack[SUIT_ATK_COL]:
                        # self.battle.suitAttacks.append(attack)
            if not self.suitHasCondition(suitId, 'healfinished'):
                attack = self.__getCheatAttack(suitId, {
                    'suitName': '',
                    'name': 'CaseManagerInsurance',
                    'animName': 'nothing',
                    'hp': 0,
                    'acc': 100,
                    'freq': 0,
                    'group': SuitBattleGlobals.ATK_TGT_GROUP,
                    'targetType': 'suit',
                    'allowSelfTarget': True,
                    'targetSelf': False,
                    'requiredConditions': ('insured', 'insured2'),
                    'excludeManagers': False,
                    'damageTarget': 'target',
                    'healTarget': 'target'
                })

                if attack[SUIT_ATK_COL]:
                    self.battle.suitAttacks.append(attack)

        for i in range(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'caseman':
                if self.suitHasCondition(suitId, 'insurancecalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'insurancecalculator') and self.__suitCanAttack(suitId):
                    currentBossHealth = -1
                    for s in self.battle.suits:
                        if s.dna.name == 'sgoat':
                            currentBossHealth = s.currHP
                    if currentBossHealth >= 1:
                        attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                'name': 'CaseManagerInsurancePlanScapegoat',  # Insurance Plan
                                                                'animName': 'throw-insurance',
                                                                    'hp': 0,
                        'acc': 100,
                        'freq': 0,
                        'group': SuitBattleGlobals.ATK_TGT_TRIPLE,
                            'targetType': 'suit',
                            'allowSelfTarget': True,
                            'targetSelf': False,
                            'excludeManagers': False,
                            'damageTarget': 'target',
                            'healTarget': 'target'})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    else:
                        attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                'name': 'CaseManagerInsurancePlan',  # Insurance Plan
                                                                'animName': 'throw-insurance',
                                                                'hp': 0,
                                                                'acc': 100,
                        'freq': 0,
                        'group': SuitBattleGlobals.ATK_TGT_TRIPLE,
                            'targetType': 'suit',
                            'allowSelfTarget': True,
                            'targetSelf': False,
                            'excludeManagers': False,
                            'damageTarget': 'target',
                            'healTarget': 'target'})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'insurancecalculator3') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'insurancecalculator3') and self.__suitCanAttack(suitId):
                    currentBossHealth = -1
                    for s in self.battle.suits:
                        if s.dna.name == 'sgoat':
                            currentBossHealth = s.currHP
                    if currentBossHealth >= 1:
                        attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                'name': 'CaseManagerInsurancePlanScapegoat',  # Insurance Plan
                                                                'animName': 'throw-insurance',
                                                                    'hp': 0,
                        'acc': 100,
                        'freq': 0,
                        'group': SuitBattleGlobals.ATK_TGT_TRIPLE,
                            'targetType': 'suit',
                            'allowSelfTarget': True,
                            'targetSelf': False,
                            'excludeManagers': False,
                            'damageTarget': 'target',
                            'healTarget': 'target'})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    else:
                        attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                'name': 'CaseManagerInsurancePlan',  # Insurance Plan
                                                                'animName': 'throw-insurance',
                                                                'hp': 0,
                                                                'acc': 100,
                        'freq': 0,
                        'group': SuitBattleGlobals.ATK_TGT_TRIPLE,
                            'targetType': 'suit',
                            'allowSelfTarget': True,
                            'targetSelf': False,
                            'excludeManagers': False,
                            'damageTarget': 'target',
                            'healTarget': 'target'})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'insurancecalculator2') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'insurancecalculator2') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'CaseManagerLegalBindings2',  # Insurance Plan
                                                            'animName': 'throw-insurance',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_TRIPLE,
                            'targetType': 'suit',
                            'allowSelfTarget': True,
                            'targetSelf': False,
                            'excludeManagers': False,
                            'damageTarget': 'target',
                            'healTarget': 'target'})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                        self.setSuitCondition(suitId, 'insurancecalculator3', 0, 0, 'setBoth')
            if self.battle.activeSuits[i].dna.name == 'stenog':
                if self.suitHasCondition(suitId, 'whirlwindcalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'whirlwindcalculator') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'ArbitratorWhirlwind',  # Whirlwind
                                                            'animName': 'sanction',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'lgator':
                # if self.suitHasCondition(suitId, 'snappedcalculator2') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                #     attack = self.__getAbilityQueued(suitId)
                #     if attack[SUIT_ATK_COL]:
                        # self.battle.suitAttacks.append(attack)
                # if self.suitHasCondition(suitId, 'snappedcalculator2') and self.__suitCanAttack(suitId):
                #     attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                #                                             'name': 'LitigatorSnapBindings',  # Snap Bindings Retaliation
                #                                             'animName': 'throw-object',
                #                                             'hp': 0,
                #                                             'acc': 100,
                #                                             'freq': 0,
                #                                             'group': SuitBattleGlobals.ATK_TGT_GROUP})
                #     if attack[SUIT_ATK_COL]:
                        # self.battle.suitAttacks.append(attack)
                # if self.suitHasCondition(suitId, 'soakedcalculator') and self.__suitCanAttack(suitId):
                #     attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                #                                             'name': 'LitigatorSnapSoak',  # Snap Soaked
                #                                             'animName': 'throw-object',
                #                                             'hp': 0,
                #                                             'acc': 100,
                #                                             'freq': 0,
                #                                             'group': SuitBattleGlobals.ATK_TGT_GROUP})
                #     if attack[SUIT_ATK_COL]:
                        # self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'snappedcalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'snappedcalculator') and self.__suitCanAttack(suitId):
                    currentBossHealth = -1
                    for s in self.battle.suits:
                        if s.dna.name == 'stenog':
                            currentBossHealth = s.currHP
                    if currentBossHealth >= 1:
                        attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                'name': 'LitigatorSnapStenographer',  # Snap Most Dangerous
                                                                'animName': 'throw-object',
                                                                'hp': 0,
                                                                'acc': 100,
                                                                'freq': 0,
                                                                'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    else:
                        attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                'name': 'LitigatorSnap',  # Snap Most Dangerous
                                                                'animName': 'throw-object',
                                                                'hp': 0,
                                                                'acc': 100,
                                                                'freq': 0,
                                                                'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'sgoat':
                if self.deadSuits == 1 and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'ArbitratorObjection',  # Extra Attack for Dead Suits
                                                            'animName': 'objection',
                                                            'hp': 20,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.deadSuits == 2 and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'ArbitratorObjection',  # Extra Attack for Dead Suits
                                                            'animName': 'objection',
                                                            'hp': 20,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_DOUBLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.deadSuits == 3 and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'ArbitratorObjection',  # Extra Attack for Dead Suits
                                                            'animName': 'objection',
                                                            'hp': 20,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_TRIPLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.deadSuits > 3 and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'ArbitratorObjection',  # Extra Attack for Dead Suits
                                                            'animName': 'objection',
                                                            'hp': 20,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_GROUP})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)

            # Secondary Cheats
        for i in range(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'lgator':
                if self.suitHasCondition(suitId, 'throwbookcalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'throwbookcalculator') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                      'name': 'ArbitratorThrowBook', # ThrowBook
                     'animName': 'throw-object',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE,

                        'targetType': 'suit',
                         'damageTarget': 'target',
                        'healTarget': 'attacker',
                        'allowSelfTarget': False,
                        'targetSelf': False,
                     'excludeManagers': True,
                        'requiredConditions': (),
                        'excludeConditions': ('insured', 'insured2',),})
                    if not attack[SUIT_ATK_COL]:
                        ability = self.__getAbilityQueued(suitId)
                        self.battle.suitAttacks.append(ability)

                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'stenog':
                if self.suitHasCondition(suitId, 'costscalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'costscalculator') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'SynergyFees', # Court Costs
                     'animName': 'magic3',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_GROUP})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'sanctioncalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'sanctioncalculator') and self.__suitCanAttack(suitId):
                    currentBossHealth = -1
                    for s in self.battle.suits:
                        if s.dna.name == 'lgator':
                            currentBossHealth = s.currHP
                    if currentBossHealth >= 1:
                        attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                        'name': 'StenographerSanctionLitigator', # Court Sanction Least Dangerous
                        'animName': 'sanction',
                        'hp': 0,
                        'acc': 100,
                        'freq': 0,
                        'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    else:
                        attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                        'name': 'StenographerSanction', # Court Sanction Least Dangerous
                        'animName': 'sanction',
                        'hp': 0,
                        'acc': 100,
                        'freq': 0,
                        'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)

            # Legal Bindings
        for i in range(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'caseman':
                if self.suitHasCondition(suitId, 'bindingscalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'bindingscalculator') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'CaseManagerLegalBindings', # Legal Bindings
                     'animName': 'throw-object',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                        'excludeToonConditions': (
                            'bound',
                        )})
                    if not attack[SUIT_ATK_COL]:
                        ability = self.__getAbilityQueued(suitId)
                        self.battle.suitAttacks.append(ability)

                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'bindingscalculator2') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'bindingscalculator2') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'CaseManagerLegalBindings',
                     'animName': 'throw-object',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                    'excludeToonConditions': (
                        'bound',
                    )})
                    if not attack[SUIT_ATK_COL]:
                        ability = self.__getAbilityQueued(suitId)
                        self.battle.suitAttacks.append(ability)

                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                        self.setSuitCondition(suitId, 'bindingscalculator2', 0, 0, 'setBoth')

            # Gag Banning & End Of Round Cheats
        for i in range(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'sgoat':
                if self.suitHasCondition(suitId, 'gavelcalculator') and not self.__suitCanAttack(suitId) and \
                        self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'gavelcalculator') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'ScapegoatGavel',  # Evidence Suppression
                                            'animName': 'throw-paper',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.getSuitConditionModifier(suitId, 'rageBuilding') >= 100 and not self.suitHasCondition(suitId, 'enraged') and self.suitHasCondition(suitId, 'unlureSuit') and not self.suitHasCondition(suitId, 'sounded') and \
                        self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getLureRemoval(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.getSuitConditionModifier(suitId, 'rageBuilding') >= 100 and self.battle.activeSuits[i].currHP > 0 and not self.suitHasCondition(suitId, 'enraged'):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'ScapegoatEnraged', # Enraged
                     'animName': 'rage',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                                        'targetType': 'none'})
                    self.battle.suitAttacks.append(attack)
                if self.getSuitConditionTurns(suitId, 'enraged') == 1 and self.battle.activeSuits[i].currHP > 0 and self.suitHasCondition(suitId, 'enraged'):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'ScapegoatShieldsUp', # Shield's Up
                     'animName': 'defense',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                                        'targetType': 'none'})
                    self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'lgator':
                if self.suitHasCondition(suitId, 'bashcalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'bashcalculator') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'LitigatorBayouBash', # Bayou Bash
                     'animName': 'none',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                                        'targetType': 'none'})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'stenog':
                if self.suitHasCondition(suitId, 'calculatingcalculator') and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'CalculatingFees', # Calculating Costs
                     'animName': 'calculating-costs',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE,

                        'targetType': 'suit',
                        'applyDamage': False,
                        'targetSelf': True,})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.TurnsElapsed % 1 == 0 and self.suitHasCondition(suitId, 'ban2levels') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'BanLevel%s' % random.choice(['45', '46', '47', '48', '56', '57', '58', '67', '68', '78']),
                     'animName': 'cease',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_GROUP})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.TurnsElapsed % 1 == 0 and not self.suitHasCondition(suitId, 'ban2levels') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'BanLevel%s' % random.randint(4, 8),
                     'animName': 'cease',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_GROUP})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'caseman':
                if self.TurnsElapsed % 1 == 0 and self.suitHasCondition(suitId, 'ban2tracks') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'Ban%s' % random.choice(['ToonupTrap', 'ToonupLure', 'ToonupThrow', 'ToonupSquirt', 'ToonupZap', 'ToonupSound', 'ToonupDrop', 'TrapLure', 'TrapThrow', 'TrapSquirt', 'TrapZap', 'TrapSound', 'TrapDrop', 'LureThrow', 'LureSquirt', 'LureZap', 'LureSound', 'LureDrop', 'ThrowSquirt', 'ThrowZap', 'ThrowSound', 'ThrowDrop', 'SquirtZap', 'SquirtSound', 'SquirtDrop', 'ZapSound', 'ZapDrop', 'SoundDrop']),
                     'animName': 'cease',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_GROUP})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.TurnsElapsed % 1 == 0 and not self.suitHasCondition(suitId, 'ban2tracks') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'Ban%s' % random.choice(['Toonup', 'Trap', 'Lure', 'Throw', 'Squirt', 'Zap', 'Sound', 'Drop']),
                     'animName': 'cease',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_GROUP})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)

        for i in range(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'lgator':
                if self.suitHasCondition(suitId, 'bellowcalculator') and self.calculator.deadSuits > 0 and self.battle.activeSuits[i].currHP > 0:
                    self.setSuitCondition(suitId, 'bellowcalculator', 0, 0, 'setBoth')
                if self.suitHasCondition(suitId, 'bellowcalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'bellowcalculator') and self.__suitCanAttack(suitId) and not self.deadSuits > 0:
                    attack = self.__getCheatAttack(suitId,{'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'LitigatorBayouBellow',  # Bayou Bellow
                                            'animName': 'bellow',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                                        'targetType': 'none'})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'bellowcalculator2') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'bellowcalculator2') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'LitigatorBayouBellow',  # Bayou Bellow
                                                            'animName': 'bellow',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                                        'targetType': 'none'})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                self.setSuitCondition(suitId, 'bellowcalculator2', 0, 0, 'setBoth')