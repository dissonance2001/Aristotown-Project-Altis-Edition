from __future__ import absolute_import
from toontown.battle.BattleBase import *
from toontown.battle.BattleGlobals import *
from toontown.battle import SuitBattleGlobals
import random
import math
from six.moves import range

class BossbotLitigationCalculatorAI:

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

    def calculateSuitAttacksBossbotLitigation(self):
        for i in range(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'bkeeper':  # bookkeeper
                if self.suitHasCondition(suitId, 'unlureSuit') and self.suitHasCondition(suitId, 'bookkeeping') and not self.suitHasCondition(suitId, 'sounded') and self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getLureRemoval(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.TurnsElapsed % 1 == 0 and self.__suitCanAttack(suitId) and self.suitHasCondition(suitId, 'bookkeeperHit'):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'BookkeeperBookkeepingRetaliation', # Bookkeeping Retaliation
                     'animName': 'nothing',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_GROUP,
                                                                'requiredToonConditions': (
                                                                            'bookkeepingtoon',
                                                                        )})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.TurnsElapsed % 1 == 0 and self.__suitCanAttack(suitId) and not self.suitHasCondition(suitId, 'bookkeeperHit') and self.suitHasCondition(suitId, 'bookkeeping'):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'BookkeeperPaperCutMarked', # Bookkeeping Retaliation
                     'animName': 'effort',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                                        'targetType': 'none'})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)

        for i in range(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'ambass':
                if self.suitHasCondition(suitId, 'pinkslipcalculator2') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'AmbassadorManagerialProtection',  # Court Sanction Legal Bindings Retaliation
                                                            'animName': 'golf-club-swing',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'bkeeper':
                if self.suitHasCondition(suitId, 'papercutcalculator2') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'AmbassadorAdvancement2', # Paper Cut
                     'animName': 'sanction',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'phouse':
                self.__appendToonConditionDamageAndRetaliation(
                    condition='hidden',
                    damage=25,
                    damageMovie='PowerhouseGroundbreakerRevert',
                    retaliations=[
                        {
                            'suitNames': ['ambass'],
                            'movie': 'AmbassadorManagerialProtection',
                            'animName': 'golf-club-swing',
                            'hp': 21,
                            'queueCondition': 'pinkslipcalculator2',
                        }
                    ]
                )
            if self.battle.activeSuits[i].dna.name == 'bkeeper':
                self.__appendToonConditionDamageAndRetaliation(
                    condition='snapped',
                    damage=0,
                    damageMovie=None,
                    retaliateAtTurns=[1],
                    retaliations=[
                        {
                            'suitNames': ['bkeeper'],
                            'movie': 'AmbassadorAdvancement2',
                            'animName': 'sanction',
                            'hp': 25,
                            'queueCondition': 'papercutcalculator2',
                        }
                    ]
                )
                # if self.TurnsElapsed % 1 == 0:
                #     attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                #                             'name': 'PowerhouseGroundbreakerRevert',  # Toons Reappearing From Groundbreaker
                #                             'animName': 'nothing',
                #                             'hp': 0,
                #                             'acc': 100,
                #                             'freq': 0,
                #                             'group': SuitBattleGlobals.ATK_TGT_GROUP})
                #     if attack[SUIT_ATK_COL]:
                        # self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'phouse' and not self.calculator.TurnsElapsed % 99 == 0 or self.suitHasCondition(suitId, 'beginning'):
                attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'PowerhouseToleranceBuilding',  # Suppression Revert
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

        for i in range(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            # Gag Ban Retaliations & DOT
            if self.battle.activeSuits[i].dna.name == 'ambass':
                if self.suitHasCondition(suitId, 'refinementcalculator') and not self.suitHasCondition(suitId, 'headroller2calculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'refinementcalculator') and not self.suitHasCondition(suitId, 'headroller2calculator') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'AmbassadorRefinement', # Refinement
                     'animName': 'snap',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_GROUP,
                            'targetType': 'suit',

                            'allowSelfTarget': True,
                            'targetSelf': False,
                        'excludeManagers': False})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'headroller2calculator') and self.suitHasCondition(suitId, 'unlureSuit') and not self.suitHasCondition(suitId, 'sounded') and self.battle.activeSuits[
                    i].currHP > 0:
                    attack = self.__getLureRemoval(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'headroller2calculator') and self.battle.activeSuits[
                    i].currHP > 0:
                    attack = self.__getCheatAttack(suitId, {
                    'suitName': self.battle.activeSuits[i].dna.name,
                    'name': 'AmbassadorHeadRollerGroup',
                    'animName': 'snap-override',
                    'hp': 0,
                    'acc': 100,
                    'freq': 0,
                    'group': SuitBattleGlobals.ATK_TGT_GROUP,
                    'targetType': 'suit',
                    'allowSelfTarget': False,
                    'targetSelf': False,
                    'requiredConditions': ('ambheadrollertarget',),
                    'excludeManagers': True,
                    'damageTarget': 'target',
                    'healTarget': 'target'
                })
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.calculator.sacrificedCogs > 0 and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getCheatAttack(suitId, {
                        'suitName': self.battle.activeSuits[i].dna.name,
                        'name': 'AmbassadorHeadRoller',
                        'animName': 'summon',
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
                    # if self.sacrificedCogs == 2:
                    #     attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                    #                                             'name': 'AmbassadorHeadRoller2',  # Damage Up 2
                    #                                             'animName': 'summon',
                    #                                             'hp': 0,
                    #                                             'acc': 100,
                    #                                             'freq': 0,
                    #                                             'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    #     if attack[SUIT_ATK_COL]:
                        # self.battle.suitAttacks.append(attack)
                    # if self.sacrificedCogs == 3:
                    #     attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                    #                                             'name': 'AmbassadorHeadRoller3',  # Damage Up 3
                    #                                             'animName': 'summon',
                    #                                             'hp': 0,
                    #                                             'acc': 100,
                    #                                             'freq': 0,
                    #                                             'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    #     if attack[SUIT_ATK_COL]:
                        # self.battle.suitAttacks.append(attack)
                    # if self.sacrificedCogs == 4:
                    #     attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                    #                                             'name': 'AmbassadorHeadRoller4',  # Damage Up 4
                    #                                             'animName': 'summon',
                    #                                             'hp': 0,
                    #                                             'acc': 100,
                    #                                             'freq': 0,
                    #                                             'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    #     if attack[SUIT_ATK_COL]:
                        # self.battle.suitAttacks.append(attack)
                    # if self.sacrificedCogs >= 5:
                    #     attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                    #                                             'name': 'AmbassadorHeadRoller5',  # Damage Up 5
                    #                                             'animName': 'summon',
                    #                                             'hp': 0,
                    #                                             'acc': 100,
                    #                                             'freq': 0,
                    #                                             'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    #     if attack[SUIT_ATK_COL]:
                        # self.battle.suitAttacks.append(attack)
            # if self.battle.activeSuits[i].dna.name == 'phouse':
            #     if self.suitHasCondition(suitId, 'gagbansnipe') and self.battle.activeSuits[i].currHP > 0:
            #         attack = self.__getLureRemoval(suitId)
            #         if attack[SUIT_ATK_COL]:
                        # self.battle.suitAttacks.append(attack)
            #     if self.suitHasCondition(suitId, 'gagbansnipe') and self.__suitCanAttack(suitId):
            #         attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
            #          'name': 'PowerhouseSnipeGagBan', # Burn Retaliation For Gag Bans
            #          'animName': 'nothing',
            #          'hp': 0,
            #          'acc': 100,
            #          'freq': 0,
            #          'group': SuitBattleGlobals.ATK_TGT_GROUP})
            #         if attack[SUIT_ATK_COL]:
                        # self.battle.suitAttacks.append(attack)
            # if self.battle.activeSuits[i].dna.name == 'phouse':
            #     if self.suitHasCondition(suitId, 'bookkeepersnipe') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
            #         attack = self.__getAbilityQueued(suitId)
            #         if attack[SUIT_ATK_COL]:
                        # self.battle.suitAttacks.append(attack)
            #     if self.suitHasCondition(suitId, 'bookkeepersnipe') and self.__suitCanAttack(suitId):
            #         attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
            #          'name': 'PowerhouseSnipeBookkept', # Burn Retaliation For Attacking Bookkeeper
            #          'animName': 'nothing',
            #          'hp': 0,
            #          'acc': 100,
            #          'freq': 0,
            #          'group': SuitBattleGlobals.ATK_TGT_GROUP})
            #         if attack[SUIT_ATK_COL]:
                        # self.battle.suitAttacks.append(attack)

            # Primary Cheats
        for i in range(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'ambass':  # ambassador
                if self.suitHasCondition(suitId, 'advancementcalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'advancementcalculator') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {
                        'suitName': self.battle.activeSuits[i].dna.name,
                        'name': 'AmbassadorAdvancement',
                        'animName': 'bellow',
                        'hp': 0,
                        'acc': 100,
                        'freq': 0,
                        'group': SuitBattleGlobals.ATK_TGT_GROUP,
                        'targetType': 'suit',
                        'allowSelfTarget': False,
                        'targetSelf': False,
                        'excludeManagers': True,
                        'damageTarget': 'target',
                        'healTarget': 'target'
                    })
                    if not attack[SUIT_ATK_COL]:
                        ability = self.__getAbilityQueued(suitId)
                        self.battle.suitAttacks.append(ability)

                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'headrollercalculator') and self.suitHasCondition(suitId, 'phase3') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'headrollercalculator') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {
                        'suitName': self.battle.activeSuits[i].dna.name,
                        'name': 'AmbassadorGhostMentality',
                        'animName': 'deadwood',
                        'hp': 0,
                        'acc': 100,
                        'freq': 0,
                        'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                        'targetType': 'suit',
                        'allowSelfTarget': False,
                        'targetSelf': False,
                        'targetWeakest': True,
                        'excludeManagers': True
                    })
                    if not attack[SUIT_ATK_COL]:
                        ability = self.__getAbilityQueued(suitId)
                        self.battle.suitAttacks.append(ability)

                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'bkeeper':
                if self.suitHasCondition(suitId, 'explodingcalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'explodingcalculator') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'BookkeeperExplodingDocument', # Paper Rain
                     'animName': 'throw-paper',
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
                    if not attack[SUIT_ATK_COL]:
                        ability = self.__getAbilityQueued(suitId)
                        self.battle.suitAttacks.append(ability)

                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)

            # Secondary Cheats
        for i in range(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'bkeeper':  # bookkeeper
                if self.suitHasCondition(suitId, 'papercutcalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'bookkeepingcalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'bookkeepingcalculator') and self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'BookkeeperBookkeeping', # Bookkeeping
                     'animName': 'effort',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                                        'targetType': 'none'})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'wtapper':  # wiretapper
                if self.suitHasCondition(suitId, 'voicemailcalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'voicemailcalculator') and self.battle.activeSuits[i].currHP > 0 and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'WiretapperVoicemail', # Voicemail Damage Reduction
                     'animName': 'phone',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                                        'targetType': 'none'})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'collectcallcalculator') and not self.suitHasCondition(suitId, 'immune') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'collectcallcalculator') and not self.suitHasCondition(suitId, 'immune') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'WiretapperCollectCall', # Collect Call (Doubles The Dues For a Toon)
                     'animName': 'snap',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                    'excludeToonConditions': (
                        'collectcalled',
                    )})
                    if not attack[SUIT_ATK_COL]:
                        ability = self.__getAbilityQueued(suitId)
                        self.battle.suitAttacks.append(ability)

                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'collectcallcalculator4') and not self.suitHasCondition(suitId, 'immune') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'collectcallcalculator4') and not self.suitHasCondition(suitId, 'immune') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'WiretapperCollectCall', # Collect Call (Doubles The Dues For a Toon)
                     'animName': 'snap',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                    'excludeToonConditions': (
                        'collectcalled',
                    )})
                    if not attack[SUIT_ATK_COL]:
                        ability = self.__getAbilityQueued(suitId)
                        self.battle.suitAttacks.append(ability)

                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                    self.setSuitCondition(suitId, 'collectcallcalculator4', 0, 0, 'setBoth')
                if self.suitHasCondition(suitId, 'costscalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'costscalculator') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'WiretapperCollectCallDamage', # Collect Call Dues
                     'animName': 'magic3',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_GROUP})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'brokenconnectioncalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'brokenconnectioncalculator') and self.battle.activeSuits[i].currHP > 0 and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'WiretapperBrokenConnection', # Broken Connection
                     'animName': 'pie-small-react',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                                        'targetType': 'none'})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'ambass': #ambassador
                if self.suitHasCondition(suitId, 'pinkslipcalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'pinkslipcalculator') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'AmbassadorManagerialProtectionImmunity',  # Extra Attack for Head Roller
                                            'animName': 'golf-club-swing',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'ambass':
                if self.deadSuits == 1 and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'AmbassadorMulligan',  # Extra Attack for Dead Suits
                                            'animName': 'golf-club-swing',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.deadSuits == 2 and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'AmbassadorMulligan',  # Extra Attack for Dead Suits
                                                            'animName': 'golf-club-swing',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_DOUBLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.deadSuits == 3 and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'AmbassadorMulligan',  # Extra Attack for Dead Suits
                                                            'animName': 'golf-club-swing',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_TRIPLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.deadSuits > 3 and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'AmbassadorMulligan',  # Extra Attack for Dead Suits
                                                            'animName': 'golf-club-swing',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_GROUP})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if not self.suitHasCondition(suitId, 'sounded') and self.suitHasCondition(suitId, 'unlureSuit') and self.getSuitConditionTurns(suitId, 'ambassadorOverconfidence') == 1 and not self.suitHasCondition(suitId, 'phase3') and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getLureRemoval(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.getSuitConditionTurns(suitId, 'ambassadorOverconfidence') == 1 and not self.suitHasCondition(suitId, 'phase3'):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'AmbassadorPhase2', # 'Phase 2'
                     'animName': 'frustrated',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                                        'targetType': 'none'})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)

            # End Of Round & Gag Ban Cheats
        for i in range(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'phouse': #powerhouse
            #     if self.suitHasCondition(suitId, 'vulnerablesnipe') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
            #         attack = self.__getAbilityQueued(suitId)
            #         if attack[SUIT_ATK_COL]:
                        # self.battle.suitAttacks.append(attack)
            #     if self.suitHasCondition(suitId, 'vulnerablesnipe') and self.__suitCanAttack(suitId):
            #         attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
            #          'name': 'PowerhouseSnipeVulnerable', # Burn Retaliation Vulnerabilities
            #          'animName': 'nothing',
            #          'hp': 0,
            #          'acc': 100,
            #          'freq': 0,
            #          'group': SuitBattleGlobals.ATK_TGT_GROUP})
            #         if attack[SUIT_ATK_COL]:
                        # self.battle.suitAttacks.append(attack)
                if not self.suitHasCondition(suitId, 'sounded') and self.suitHasCondition(suitId, 'unlureSuit') and self.getSuitConditionModifier(suitId, 'powerhouseRotation') >= 100 and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getLureRemoval(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.getSuitConditionModifier(suitId, 'powerhouseRotation') >= 100 and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'PowerhouseGeneration2',  # Generation
                                            'animName': 'nothing',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                                        'targetType': 'none'})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if not self.suitHasCondition(suitId, 'sounded') and self.suitHasCondition(suitId, 'unlureSuit') and self.suitHasCondition(suitId, 'rotationcalculator') and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getLureRemoval(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'rotationcalculator') and self.__suitCanAttack(suitId):
                    if not self.calculator.unusedPhases:
                        self.calculator.unusedPhases = [2, 3, 4, 5, 6, 7, 8]
                    condition = random.choice(self.calculator.unusedPhases)
                    if condition == 1:
                        self.calculator.unusedPhases.remove(condition)
                        attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                'name': 'PowerhouseAbsorb',  # Desperation Syphon For All Cogs
                                                                'animName': 'defense',
                                                                'hp': 0,
                                                                'acc': 100,
                                                                'freq': 0,
                                                                'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                                        'targetType': 'none'})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    elif condition == 2:
                        self.calculator.unusedPhases.remove(condition)
                        attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                           'name': 'PowerhouseSoakImmune',
                                                                           'animName': 'nothing',
                                                                           'hp': 0,
                                                                           'acc': 100,
                                                                           'freq': 0,
                                                                           'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                                        'targetType': 'none'})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    elif condition == 3:
                        self.calculator.unusedPhases.remove(condition)
                        attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                           'name': 'PowerhouseZapImmune',
                                                                           'animName': 'nothing',
                                                                           'hp': 0,
                                                                           'acc': 100,
                                                                           'freq': 0,
                                                                           'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                                        'targetType': 'none'})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    elif condition == 4:
                        self.calculator.unusedPhases.remove(condition)
                        attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                           'name': 'PowerhouseLureImmune',
                                                                           'animName': 'nothing',
                                                                           'hp': 0,
                                                                           'acc': 100,
                                                                           'freq': 0,
                                                                           'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                                        'targetType': 'none'})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    elif condition == 5:
                        self.calculator.unusedPhases.remove(condition)
                        attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                           'name': 'PowerhouseDropImmune',
                                                                           'animName': 'nothing',
                                                                           'hp': 0,
                                                                           'acc': 100,
                                                                           'freq': 0,
                                                                           'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                                        'targetType': 'none'})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    elif condition == 6:
                        self.calculator.unusedPhases.remove(condition)
                        attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                           'name': 'PowerhouseSyphon',
                                                                           'animName': 'summon',
                                                                           'hp': 0,
                                                                           'acc': 100,
                                                                           'freq': 0,
                                                                           'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                                        'targetType': 'none'})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    elif condition == 7:
                        self.calculator.unusedPhases.remove(condition)
                        attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                'name': 'PowerhouseSnipeVulnerable',
                                                                'animName': 'cease',
                                                                'hp': 0,
                                                                'acc': 100,
                                                                'freq': 0,
                                                                'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                                        'targetType': 'none'})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    elif condition == 8:
                        self.calculator.unusedPhases.remove(condition)
                        attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                'name': 'PowerhouseSnipeMulligan',
                                                                'animName': 'sound-react',
                                                                'hp': 0,
                                                                'acc': 100,
                                                                'freq': 0,
                                                                'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                                        'targetType': 'none'})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    else:
                        pass
                    self.setSuitCondition(suitId, 'rotationcalculator', 0, 0, 'setBoth')
                    self.setSuitCondition(suitId, 'powerhouseRotation', 0, -1, 'setBoth')
                if self.getSuitConditionModifier(suitId, 'powerhouseRotation') >= 100 and self.battle.activeSuits[i].currHP > 0:
                    if not self.calculator.unusedPhases:
                        self.calculator.unusedPhases = [2, 3, 4, 5, 6, 7, 8]
                    condition = random.choice(self.calculator.unusedPhases)
                    if condition == 1:
                        self.calculator.unusedPhases.remove(condition)
                        attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                'name': 'PowerhouseAbsorb',  # Desperation Syphon For All Cogs
                                                                'animName': 'defense',
                                                                'hp': 0,
                                                                'acc': 100,
                                                                'freq': 0,
                                                                'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                                        'targetType': 'none'})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    elif condition == 2:
                        self.calculator.unusedPhases.remove(condition)
                        attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                'name': 'PowerhouseSoakImmune',
                                                                'animName': 'nothing',
                                                                'hp': 0,
                                                                'acc': 100,
                                                                'freq': 0,
                                                                'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                                        'targetType': 'none'})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    elif condition == 3:
                        self.calculator.unusedPhases.remove(condition)
                        attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                'name': 'PowerhouseZapImmune',
                                                                'animName': 'nothing',
                                                                'hp': 0,
                                                                'acc': 100,
                                                                'freq': 0,
                                                                'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                                        'targetType': 'none'})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    elif condition == 4:
                        self.calculator.unusedPhases.remove(condition)
                        attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                'name': 'PowerhouseLureImmune',
                                                                'animName': 'nothing',
                                                                'hp': 0,
                                                                'acc': 100,
                                                                'freq': 0,
                                                                'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                                        'targetType': 'none'})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    elif condition == 5:
                        self.calculator.unusedPhases.remove(condition)
                        attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                'name': 'PowerhouseDropImmune',
                                                                'animName': 'nothing',
                                                                'hp': 0,
                                                                'acc': 100,
                                                                'freq': 0,
                                                                'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                                        'targetType': 'none'})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    elif condition == 6:
                        self.calculator.unusedPhases.remove(condition)
                        attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                'name': 'PowerhouseSyphon',
                                                                'animName': 'summon',
                                                                'hp': 0,
                                                                'acc': 100,
                                                                'freq': 0,
                                                                'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                                        'targetType': 'none'})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    elif condition == 7:
                        self.calculator.unusedPhases.remove(condition)
                        attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                'name': 'PowerhouseSnipeVulnerable',
                                                                'animName': 'cease',
                                                                'hp': 0,
                                                                'acc': 100,
                                                                'freq': 0,
                                                                'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                                        'targetType': 'none'})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    elif condition == 8:
                        self.calculator.unusedPhases.remove(condition)
                        attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                'name': 'PowerhouseSnipeMulligan',
                                                                'animName': 'sound-react',
                                                                'hp': 0,
                                                                'acc': 100,
                                                                'freq': 0,
                                                                'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                                        'targetType': 'none'})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    else:
                        pass
            if self.battle.activeSuits[i].dna.name == 'wtapper':
                if self.suitHasCondition(suitId, 'wiretappedcalculator') and not self.suitHasCondition(suitId, 'sounded') and self.suitHasCondition(suitId, 'unlureSuit'):
                    attack = self.__getLureRemoval(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'wiretappedcalculator') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'WiretapperWiretapped', # Wiretapped
                     'animName': 'phone',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_GROUP})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                # if self.syphonHP.get(suitId, 0) > 0:
                #     attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                #      'name': 'SyphonMovie', # Wiretapped
                #      'animName': 'nothing',
                #      'hp': 0,
                #      'acc': 100,
                #      'freq': 0,
                #      'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                #     if attack[SUIT_ATK_COL]:
                       # self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'calculatingcalculator') and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'WiretapperCollectCall2', # Calculating Collect Call Dues
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
                if self.TurnsElapsed % 1 == 0  and not self.suitHasCondition(suitId, 'ban2levels') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'BanLevel%s' % random.randint(4, 8),
                     'animName': 'sanction',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_GROUP})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.TurnsElapsed % 1 == 0 and not self.suitHasCondition(suitId, 'ban2tracks') and self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP < 2388:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'Ban%s' % random.choice(
                                                ['Toonup', 'Trap', 'Lure', 'Throw', 'Squirt', 'Zap', 'Sound', 'Drop']),
                     'animName': 'sanction',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_GROUP})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.TurnsElapsed % 1 == 0 and self.suitHasCondition(suitId, 'ban2levels') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'BanLevel%s' % random.choice(['45', '46', '47', '48', '56', '57', '58', '67', '68', '78']),
                     'animName': 'sanction',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_GROUP})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.TurnsElapsed % 1 == 0 and self.suitHasCondition(suitId, 'ban2tracks') and self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP < 2388:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'Ban%s' % random.choice(['ToonupTrap', 'ToonupLure', 'ToonupThrow', 'ToonupSquirt', 'ToonupZap', 'ToonupSound', 'ToonupDrop', 'TrapLure', 'TrapThrow', 'TrapSquirt', 'TrapZap', 'TrapSound', 'TrapDrop', 'LureThrow', 'LureSquirt', 'LureZap', 'LureSound', 'LureDrop', 'ThrowSquirt', 'ThrowZap', 'ThrowSound', 'ThrowDrop', 'SquirtZap', 'SquirtSound', 'SquirtDrop', 'ZapSound', 'ZapDrop', 'SoundDrop']),
                     'animName': 'sanction',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_GROUP})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)

        for i in range(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            # Gag Ban Retaliations & DOT
            if self.battle.activeSuits[i].dna.name == 'bkeeper':  # bookkeeper
                if self.suitHasCondition(suitId, 'filingcalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueuedPreToon(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'filingcalculator') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'BookkeeperMandatoryFiling', # Paper Rain
                     'animName': 'glower',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_DOUBLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)

        for i in range(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'phouse': #powerhouse
                if self.suitHasCondition(suitId, 'scabbardcalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[
                    i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'scabbardcalculator') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {
                        'suitName': self.battle.activeSuits[i].dna.name,
                        'name': 'DividendPeckingOrder',
                        'animName': 'nothing',
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
                if self.suitHasCondition(suitId, 'groundbreakercalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'groundbreakercalculator') and self.__suitCanAttack(suitId):
                    if self.battle.activeSuits[i].currHP <= 2000:
                        attack = self.__getCheatAttack(suitId, {'suitName': 'phouse',
                                                'name': 'PowerhouseGroundbreaker',
                                                'animName': 'quick-jump',
                                                'hp': 0,
                                                'acc': 100,
                                                'freq': 0,
                                                'group': SuitBattleGlobals.ATK_TGT_DOUBLE})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    else:
                        attack = self.__getCheatAttack(suitId, {'suitName': 'phouse',
                                                'name': 'PowerhouseGroundbreaker',
                                                'animName': 'quick-jump',
                                                'hp': 0,
                                                'acc': 100,
                                                'freq': 0,
                                                'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)