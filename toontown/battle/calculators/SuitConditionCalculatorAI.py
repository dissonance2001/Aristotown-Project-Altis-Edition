from toontown.battle.BattleBase import *
from toontown.battle.BattleGlobals import *
from toontown.battle import SuitBattleGlobals
import random
import math

class SuitConditionCalculatorAI:

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

    def calculateSuitConditions(self):
        for i in range(len(self.battle.activeSuits)): # Cheat Calculators
            suitId = self.battle.activeSuits[i].doId
            x = self.calculator.TurnsElapsed
            # if x % 99 == 0 and not self.suitHasCondition(suitId, 'alreadyCogSpawn2'):
            #     attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
            #                             'name': 'CogSpawn',
            #                             'animName': 'nothing',
            #                             'hp': 0,
            #                             'acc': 100,
            #                             'freq': 0,
            #                             'group': SuitBattleGlobals.ATK_TGT_SINGLE})
            #     if attack[SUIT_ATK_COL]:
                        # self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'stenog':
                if (x + 1) % 4 == 0:
                    self.setSuitCondition(suitId, 'whirlwindcalculator', 1, 10, 'setBoth')
                if (x + 1) % 3 == 0:
                    self.setSuitCondition(suitId, 'sanctioncalculator', 1, 9, 'setBoth')
                if (x + 3) % 3 == 0:
                    self.setSuitCondition(suitId, 'calculatingcalculator', 1, 10, 'setBoth')
            if self.battle.activeSuits[i].dna.name == 'caseman':
                if (x + 1) % 4 == 0:
                    self.setSuitCondition(suitId, 'paperfilingcalculator', 1, 10, 'setBoth')
                if (x + 2) % 3 == 0:
                    self.setSuitCondition(suitId, 'bindingscalculator', 1, 9, 'setBoth')
                if x % 2 == 0:
                    self.setSuitCondition(suitId, 'insurancecalculator', 1, 10, 'setBoth')
                if (x + 2) % 3 == 0:
                    self.setSuitCondition(suitId, 'insurancecalculator3', 1, 10, 'setBoth')
                if (x + 2) % 3 == 0:
                    self.setSuitCondition(suitId, 'insurancecalculator2', 1, 10, 'setBoth')
            if self.battle.activeSuits[i].dna.name == 'lgator':
                for suit in self.battle.activeSuits:
                    self.setSuitCondition(suit.doId, 'alreadyCogSpawn', 1, 1, 'setBoth')
                if (x + 2) % 4 == 0:
                    self.setSuitCondition(suitId, 'throwbookcalculator', 1, 10, 'setBoth')
                if (x + 1) % 3 == 0:
                    self.setSuitCondition(suitId, 'snappedcalculator', 1, 10, 'setBoth')
                if x % 4 == 0:
                    self.setSuitCondition(suitId, 'bashcalculator', 1, 10, 'setBoth')
                if x % 4 == 0 and self.suitHasCondition(suitId, 'bashcalculator') and len(self.battle.activeSuits) >= 6 and not self.deadSuits > 0 and not x == 0:
                    self.setSuitCondition(suitId, 'bashcalculator', 0, 0, 'setBoth')
                    self.setSuitCondition(suitId, 'bellowcalculator', 1, 10, 'setBoth')
                if self.battle.activeSuits[i].currHP <= 4100:
                    if (x + 1) % 4 == 0 and self.suitHasCondition(suitId, 'bashcalculator') and not self.deadSuits > 0 and len(self.battle.activeSuits) >= 6:
                        self.setSuitCondition(suitId, 'bashcalculator', 0, 0, 'setBoth')
                        self.setSuitCondition(suitId, 'bellowcalculator', 1, 10, 'setBoth')
                    elif (x + 1) % 4 == 0 and not self.suitHasCondition(suitId, 'bashcalculator'):
                        self.setSuitCondition(suitId, 'bashcalculator', 1, 10, 'setBoth')
                if self.battle.activeSuits[i].currHP <= 3600:
                    if (x + 2) % 4 == 0 and self.suitHasCondition(suitId, 'bashcalculator') and not self.deadSuits > 0 and len(self.battle.activeSuits) >= 6:
                        self.setSuitCondition(suitId, 'bashcalculator', 0, 0, 'setBoth')
                        self.setSuitCondition(suitId, 'bellowcalculator', 1, 10, 'setBoth')
                    elif (x + 2) % 4 == 0 and not self.suitHasCondition(suitId, 'bashcalculator'):
                        self.setSuitCondition(suitId, 'bashcalculator', 1, 10, 'setBoth')
                if self.battle.activeSuits[i].currHP <= 3100:
                    if (x + 3) % 4 == 0 and self.suitHasCondition(suitId, 'bashcalculator') and not self.deadSuits > 0 and len(self.battle.activeSuits) >= 6:
                        self.setSuitCondition(suitId, 'bashcalculator', 0, 0, 'setBoth')
                        self.setSuitCondition(suitId, 'bellowcalculator', 1, 10, 'setBoth')
                    elif (x + 3) % 4 == 0 and not self.suitHasCondition(suitId, 'bashcalculator'):
                        self.setSuitCondition(suitId, 'bashcalculator', 1, 10, 'setBoth')
                if self.battle.activeSuits[i].currHP <= 2600:
                    if (x + 3) % 4 == 0 and self.suitHasCondition(suitId, 'bashcalculator') and not self.deadSuits > 0 and len(self.battle.activeSuits) >= 6:
                        self.setSuitCondition(suitId, 'bashcalculator', 0, 0, 'setBoth')
                        self.setSuitCondition(suitId, 'bellowcalculator', 1, 10, 'setBoth')
                    elif (x + 3) % 4 == 0 and not self.suitHasCondition(suitId, 'bashcalculator'):
                        self.setSuitCondition(suitId, 'bashcalculator', 1, 10, 'setBoth')
                if self.battle.activeSuits[i].currHP <= 2100:
                    if (x + 3) % 4 == 0 and self.suitHasCondition(suitId, 'bashcalculator') and not self.deadSuits > 0 and len(self.battle.activeSuits) >= 6:
                        self.setSuitCondition(suitId, 'bashcalculator', 0, 0, 'setBoth')
                        self.setSuitCondition(suitId, 'bellowcalculator', 1, 10, 'setBoth')
                    elif (x + 3) % 4 == 0 and not self.suitHasCondition(suitId, 'bashcalculator'):
                        self.setSuitCondition(suitId, 'bashcalculator', 1, 10, 'setBoth')
                if self.battle.activeSuits[i].currHP <= 1600:
                    if (x + 2) % 3 == 0 and self.suitHasCondition(suitId, 'bashcalculator') and not self.deadSuits > 0 and len(self.battle.activeSuits) >= 6:
                        self.setSuitCondition(suitId, 'bashcalculator', 0, 0, 'setBoth')
                        self.setSuitCondition(suitId, 'bellowcalculator', 1, 10, 'setBoth')
                    elif (x + 2) % 3 == 0 and not self.suitHasCondition(suitId, 'bashcalculator'):
                        self.setSuitCondition(suitId, 'bashcalculator', 1, 10, 'setBoth')
                if self.battle.activeSuits[i].currHP <= 1100:
                    if (x + 2) % 3 == 0 and self.suitHasCondition(suitId, 'bashcalculator') and not self.deadSuits > 0 and len(self.battle.activeSuits) >= 6:
                        self.setSuitCondition(suitId, 'bashcalculator', 0, 0, 'setBoth')
                        self.setSuitCondition(suitId, 'bellowcalculator', 1, 10, 'setBoth')
                    elif (x + 2) % 3 == 0 and not self.suitHasCondition(suitId, 'bashcalculator'):
                        self.setSuitCondition(suitId, 'bashcalculator', 1, 10, 'setBoth')
                if self.battle.activeSuits[i].currHP <= 600:
                    if (x + 1) % 2 == 0 and self.suitHasCondition(suitId, 'bashcalculator') and not self.deadSuits > 0 and len(self.battle.activeSuits) >= 6:
                        self.setSuitCondition(suitId, 'bashcalculator', 0, 0, 'setBoth')
                        self.setSuitCondition(suitId, 'bellowcalculator', 1, 10, 'setBoth')
                    elif (x + 1) % 2 == 0 and not self.suitHasCondition(suitId, 'bashcalculator'):
                        self.setSuitCondition(suitId, 'bashcalculator', 1, 10, 'setBoth')
                if self.battle.activeSuits[i].currHP <= 100:
                    if (x + 1) % 2 == 0 and self.suitHasCondition(suitId, 'bashcalculator') and not self.deadSuits > 0 and len(self.battle.activeSuits) >= 6:
                        self.setSuitCondition(suitId, 'bashcalculator', 0, 0, 'setBoth')
                        self.setSuitCondition(suitId, 'bellowcalculator', 1, 10, 'setBoth')
                    elif (x + 1) % 2 == 0 and not self.suitHasCondition(suitId, 'bashcalculator'):
                        self.setSuitCondition(suitId, 'bashcalculator', 1, 10, 'setBoth')
            if self.battle.activeSuits[i].dna.name == 'sgoat':
                if (x + 3) % 4 == 0:
                    self.setSuitCondition(suitId, 'gavelcalculator', 1, 10, 'setBoth')
            if self.battle.activeSuits[i].dna.name == 'notarbit':
                if (x + 2) % 4 == 0:
                    self.setSuitCondition(suitId, 'throwbookcalculator', 1, 10, 'setBoth')
                self.setSuitCondition(suitId, 'whirlwindcalculator', 1, 10, 'setBoth')
                if (x + 2) % 3 == 0:
                    self.setSuitCondition(suitId, 'paperfilingcalculator', 1, 10, 'setBoth')
            if self.battle.activeSuits[i].dna.name == 'phouse': #powerhouse
                if x % 99 == 0 or self.suitHasCondition(suitId, 'beginning'):
                    self.setSuitCondition(suitId, 'rotationcalculator', 1, 10, 'setBoth')
                    self.setSuitCondition(suitId, 'beginning', 0, 0, 'setBoth')
                if (x + 2) % 4 == 0:
                    self.setSuitCondition(suitId, 'groundbreakercalculator', 1, 10, 'setBoth')
                if (x + 3) % 5 == 0:
                    self.setSuitCondition(suitId, 'scabbardcalculator', 1, 10, 'setBoth')
                if x % 4 == 0:
                    self.setSuitCondition(suitId, 'burncalculator', 1, 10, 'setBoth')
                if (x + 2) % 5 == 0:
                    self.setSuitCondition(suitId, 'burncalculator2', 1, 10, 'setBoth')
            if self.battle.activeSuits[i].dna.name == 'bkeeper':  # bookkeeper
                if (x + 1) % 3 == 0:
                    self.setSuitCondition(suitId, 'explodingcalculator', 1, 9, 'setBoth')
                if (x + 1) % 2 == 0:
                    self.setSuitCondition(suitId, 'filingcalculator', 1, 9, 'setBoth')
                if (x + 2) % 3 == 0:
                    self.setSuitCondition(suitId, 'papercutcalculator', 1, 10, 'setBoth')
                if (x + 3) % 5 == 0:
                    self.setSuitCondition(suitId, 'bookkeepingcalculator', 1, 10, 'setBoth')
            if self.battle.activeSuits[i].dna.name == 'wtapper':  # wiretapper
                if x % 3 == 0:
                    self.setSuitCondition(suitId, 'calculatingcalculator', 1, 10, 'setBoth')
                if (x + 1) % 3 == 0:
                    self.setSuitCondition(suitId, 'collectcallcalculator', 1, 10, 'setBoth')
                if (x + 2) % 3 == 0 and self.battle.activeSuits[i].currHP <= 2500:
                    self.setSuitCondition(suitId, 'collectcallcalculator4', 1, 10, 'setBoth')
                if (x + 3) % 5 == 0:
                    self.setSuitCondition(suitId, random.choice(('brokenconnectioncalculator', 'voicemailcalculator')), 1, 10, 'setBoth')
                if self.getSuitConditionTurns(suitId, 'brokenconnection') == 1 and self.suitHasCondition(suitId, 'brokenconnection'):
                    self.setSuitCondition(suitId, 'wiretappedcalculator', 1, 10, 'setBoth')
                if self.getSuitConditionTurns(suitId, 'immune') == 1 and self.suitHasCondition(suitId, 'immune'):
                    self.setSuitCondition(suitId, 'wiretappedcalculator', 1, 10, 'setBoth')
            if self.battle.activeSuits[i].dna.name == 'ambass': #ambassador
                if (x + 2) % 5 == 0:
                    self.setSuitCondition(suitId, 'refinementcalculator', 1, 10, 'setBoth')
                if (x + 3) % 4 == 0:
                    self.setSuitCondition(suitId, 'advancementcalculator', 1, 10, 'setBoth')
                if (x + 2) % 3 == 0:
                    self.setSuitCondition(suitId, 'pinkslipcalculator', 1, 10, 'setBoth')
                # currentBossHealth = -1
                # for s in self.battle.suits:
                #     if s.dna.name == 'wtapper' or s.dna.name == 'bkeeper' or s.dna.name == 'phouse':
                #         currentBossHealth = s.currHP
                #     if (x + 3) % 4 == 0 and currentBossHealth > 0:
                #         self.setSuitCondition(suitId, 'refinemanagercalculator', 1, 10, 'setBoth')
                if (x + 1) % 3 == 0 and self.suitHasCondition(suitId, 'phase3'):
                    self.setSuitCondition(suitId, 'headrollercalculator', 1, 10, 'setBoth')
            if self.battle.activeSuits[i].dna.name == 'safesupervis': #safety supervisor
                # if len(self.battle.activeSuits) >= 6 and (x % 2 == 0) and self.deadSuits == 0:
                #     self.setSuitCondition(suitId, 'highpressurecalculator', 1, 10, 'setBoth')
                if (x + 3) % 5 == 0:
                    self.setSuitCondition(suitId, 'promotioncalculator', 1, 10, 'setBoth')
                if (x + 3) % 4 == 0:
                    self.setSuitCondition(suitId, 'overpressurecalculator', 1, 10, 'setBoth')
                if (x + 2) % 3 == 0:
                    self.setSuitCondition(suitId, 'heatwavecalculationcalculator', 1, 10, 'setBoth')
                if (x + 1) % 3 == 0:
                    self.setSuitCondition(suitId, 'unionbustercalculator', 1, 10, 'setBoth')
            if self.battle.activeSuits[i].dna.name == 'hustle': # traffic manager
                if (x + 1) % 3 == 0:
                    self.setSuitCondition(suitId, 'breachcalculator', 1, 10, 'setBoth')
                if (x + 1) % 3 == 0:
                    self.setSuitCondition(suitId, 'contractenforcementcalculator', 1, 10, 'setBoth')
                if (x + 2) % 5 == 0:
                    self.setSuitCondition(suitId, 'yellowlightcalculator', 1, 10, 'setBoth')
                if (x + 2) % 3 == 0:
                    self.setSuitCondition(suitId, 'redlightcalculator', 1, 10, 'setBoth')
                if (x + 3) % 4 == 0:
                    self.setSuitCondition(suitId, 'greenlightcalculator', 1, 10, 'setBoth')
                if (x + 2) % 4 == 0:
                    self.setSuitCondition(suitId, 'unionbustercalculator', 1, 10, 'setBoth')
            if self.battle.activeSuits[i].dna.name == 'ubuster': #union buster
                if (x + 1) % 3 == 0:
                    self.setSuitCondition(suitId, 'breachcalculator', 1, 10, 'setBoth')
                if (x + 1) % 3 == 0:
                    self.setSuitCondition(suitId, 'unionbustcalculator', 1, 10, 'setBoth')
                if (x + 2) % 3 == 0 and self.battle.activeSuits[i].currHP < 2000:
                    self.setSuitCondition(suitId, 'unionbustcalculator2', 1, 10, 'setBoth')
                if (x + 2) % 3 == 0:
                    self.setSuitCondition(suitId, 'unionbustercalculator', 1, 10, 'setBoth')
                if (x + 1) % 4 == 0:
                    self.setSuitCondition(suitId, 'contractenforcementcalculator', 1, 10, 'setBoth')
                # if (x + 3) % 4 == 0:
                #     self.setSuitCondition(suitId, 'exclusiveCalculator', 1, 10, 'setBoth')
            if self.battle.activeSuits[i].dna.name == 'radiog': #radiographer
                if (x + 3) % 5 == 0:
                    self.setSuitCondition(suitId, 'radioinfrequencycalculator', 1, 10, 'setBoth')
                if x % 3 == 0:
                    self.setSuitCondition(suitId, 'overmodulatedcalculator', 1, 10, 'setBoth')
                # if self.__suitCanAttack(suitId) and self.suitHasCondition(suitId, 'desperation') and x % 2 == 0:
                #     self.setSuitCondition(suitId, 'overmodulatedcalculator2', 1, 1, 'setBoth')
                # if (x + 2) % 5 == 0 and not self.suitHasCondition(suitId, 'desperation'):
                #     self.setSuitCondition(suitId, 'dancesessioncalculator', 1, 10, 'setBoth')
                if (x + 1) % 4 == 0:
                    self.setSuitCondition(suitId, 'hottakecalculator', 1, 10, 'setBoth')
                if (x + 1) % 3 == 0:
                    self.setSuitCondition(suitId, 'hottakecalculator2', 1, 10, 'setBoth')
            if self.battle.activeSuits[i].dna.name == 'rkeeper': #recordkeeper
                if (x + 2) % 3 == 0:
                    self.setSuitCondition(suitId, 'costscalculator', 1, 10, 'setBoth')
                # if (x + 5) % 6 == 0:
                #     self.setSuitCondition(suitId, 'phantomEntrycalculator', 1, 10, 'setBoth')
                if (x + 1) % 3 == 0:
                    self.setSuitCondition(suitId, 'papertrailcalculator', 1, 10, 'setBoth')
                if (x + 2) % 4 == 0:
                    self.setSuitCondition(suitId, 'revisedcalculator', 1, 10, 'setBoth')
                if (x + 1) % 2 == 0:
                    self.setSuitCondition(suitId, 'redlinedcalculator', 1, 10, 'setBoth')
            if self.battle.activeSuits[i].dna.name == 'cdirector':
                if (x + 2) % 3 == 0 and self.suitHasCondition(suitId, 'alreadySecondAttack'):
                    self.setSuitCondition(suitId, 'markedcalculator', 1, 10, 'setBoth')
                if (x + 3) % 4 == 0 and self.suitHasCondition(suitId, 'alreadyRedundant'):
                    self.setSuitCondition(suitId, 'redundantcalculator', 1, 10, 'setBoth')
                if (x % 3 == 0) and self.suitHasCondition(suitId, 'alreadyHighPressure'):
                    self.setSuitCondition(suitId, 'highpressurecalculator', 1, 10, 'setBoth')
                if ((x + 1) % 5 == 0) and self.battle.activeSuits[i].currHP < 6000:
                    self.setSuitCondition(suitId, 'selfRepairCalculator', 1, 10, 'setBoth')
            if self.battle.activeSuits[i].dna.name == 'liquid':
                if (x + 3) % 4 == 0:
                    self.setSuitCondition(suitId, 'rushHourcalculator', 1, 10, 'setBoth')
            if self.battle.activeSuits[i].dna.name == 'dking':
                if (x + 1) % 3 == 0:
                    self.setSuitCondition(suitId, 'embezzlecalculator', 1, 10, 'setBoth')
                # if (x + 4) % 5 == 0:
                #     self.setSuitCondition(suitId, 'scabbardcalculator', 1, 10, 'setBoth')
                if (x + 3) % 4 == 0:
                    self.setSuitCondition(suitId, 'marketcalculator', 1, 10, 'setBoth')
                if (x + 2) % 3 == 0:
                    self.setSuitCondition(suitId, 'liquidationcalculator', 1, 10, 'setBoth')
            if self.battle.activeSuits[i].dna.name == 'racket': #racketeer
                # if x % 2 == 0 and self.battle.activeSuits[i].currHP > 0:
                #     from toontown.suit.DistributedSellbotBossMiniAI import DistributedSellbotBossMiniAI

                #     boss = None
                #     for do in simbase.air.doId2do.values():
                #         if isinstance(do, DistributedSellbotBossMiniAI):
                #             for s in self.battle.activeSuits:
                #                 if s in do.activeSuits:
                #                     boss = do
                #                     break
                #             for s in self.battle.activeSuits:
                #                 if s in do.activeSuits:
                #                     if s.dna.name == 'racket':
                #                         if len(self.battle.activeSuits) < 6 and not self.suitHasCondition(suitId, 'alreadyCogSpawn'):
                #                             if self.suitHasCondition(suitId, 'desperation'):
                #                                 boss.appendSuitsToBattle(boss.battleNumber, 'pres')
                #                                 boss.appendSuitsToBattle(boss.battleNumber, 'pres')
                #                             else:
                #                                 boss.appendSuitsToBattle(boss.battleNumber, 'pres')
                if (x + 2) % 3 == 0:
                    self.setSuitCondition(suitId, 'profiteeringcalculator', 1, 10, 'setBoth')
                if (x + 1) % 3 == 0:
                    self.setSuitCondition(suitId, 'extortioncalculator', 1, 10, 'setBoth')
            if self.battle.activeSuits[i].dna.name == 'fmaker':  # filmmaker
                if x % 3 == 0:
                    self.setSuitCondition(suitId, 'rewindcalculator', 1, 10, 'setBoth')
            if self.battle.activeSuits[i].dna.name == 'director':  # director
                if (x + 2) % 3 == 0:
                    self.setSuitCondition(suitId, 'partnercalculator', 1, 10, 'setBoth')
                if x % 3 == 0:
                    self.setSuitCondition(suitId, 'directorcalculator', 1, 10, 'setBoth')
                if (x + 1) % 3 == 0:
                    self.setSuitCondition(suitId, 'actioncogcalculator', 1, 10, 'setBoth')
            if self.battle.activeSuits[i].dna.name == 'choreo':  # choreographer
                if (x + 1) % 3 == 0:
                    self.setSuitCondition(suitId, 'choreocalculator', 1, 10, 'setBoth')
            if self.battle.activeSuits[i].dna.name == 'cinema':  # photographer
                if (x + 1) % 2 == 0:
                    self.setSuitCondition(suitId, 'focuscalculator', 1, 10, 'setBoth')
                if (x + 1) % 3 == 0:
                    self.setSuitCondition(suitId, 'flashcalculator', 1, 10, 'setBoth')
            if self.battle.activeSuits[i].dna.name == 'hroller':  # high roller phase 1
                self.setSuitCondition(suitId, 'gametimecalculator', 1, 10, 'setBoth')
            if self.battle.activeSuits[i].dna.name == 'videog':  # videographer
                if (x + 2) % 3 == 0:
                    self.setSuitCondition(suitId, 'electricshockcalculator', 1, 10, 'setBoth')
            if self.battle.activeSuits[i].dna.name == 'derrman':  # Derrick Man
                if x % 3 == 0:
                    self.setSuitCondition(suitId, 'refinementDerrick', 1, 10, 'setBoth')
            if self.battle.activeSuits[i].dna.name == 'dola':  # DOLA
                if (x + 4) % 5 == 0:
                    self.setSuitCondition(suitId, 'inkDraincalculator', 1, 10, 'setBoth')
            if self.battle.activeSuits[i].dna.name == 'payman':  # Payroll Manager
                if x % 3 == 0:
                    self.setSuitCondition(suitId, 'processcalculator', 1, 10, 'setBoth')
                if (x + 1) % 3 == 0:
                    self.setSuitCondition(suitId, 'bonuscalculator', 1, 10, 'setBoth')