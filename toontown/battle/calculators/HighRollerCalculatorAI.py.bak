from toontown.battle.BattleBase import *
from toontown.battle.BattleGlobals import *
from toontown.battle import SuitBattleGlobals
import random
import math

class HighRollerCalculatorAI:

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

    
    def calculateSuitAttacksHighRoller(self):
        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId


        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            x = self.TurnsElapsed
            # Initial Cheats
            if self.battle.activeSuits[i].dna.name == 'hrollers':
                if self.battle.activeSuits[i].getActualLevel() == 29 and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'HighRollerBar',  # Red Silhouette
                                            'animName': 'snap',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_GROUP})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                
                if self.battle.activeSuits[i].getActualLevel() == 36 and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'HighRollerDamageReduction',  # Red Silhouette
                                            'animName': 'snap',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.battle.activeSuits[i].getActualLevel() == 33 and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'HighRollerDonation',  # White Silhouette
                                            'animName': 'shot5',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.battle.activeSuits[i].getActualLevel() == 34 and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'HighRollerSyphon',  # Magenta Silhouette
                                            'animName': 'sanction',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_GROUP})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'hroller' and self.suitHasCondition(suitId, 'phase3'):
                if self.battle.activeSuits[i].currHP <= 0 and not self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'FilmmakerBudgetCuts',  # Video Static Upon Death
                                            'animName': 'nothing',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.TurnsElapsed % 1 == 0 and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'HighRollerBust',
                                            'animName': 'bust',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_GROUP})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'hroller':
                # if self.levelDamage > 0 and self.battle.activeSuits[i].currHP > 1:
                #     attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                #                             'name': 'AbsorbMovieLevel',  # Absorb Damage Movie Level
                #                             'animName': 'nothing',
                #                             'hp': 0,
                #                             'acc': 100,
                #                             'freq': 0,
                #                             'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                #     if attack[SUIT_ATK_COL]:
                        # self.battle.suitAttacks.append(attack)
                if self.TurnsElapsed % 3 == 0 and not self.TurnsElapsed == 0 and self.__suitCanAttack(suitId) and not self.suitHasCondition(suitId, 'phase3'):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'HighRollerCommercialBreak',  # Commercial Break after Puzzle
                                            'animName': 'snap',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'gameovercalculator') and not self.suitHasCondition(suitId, 'phase3'):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'HighRollerGameOver',  # Game Over after Using Puzzle
                                            'animName': 'song-and-dance',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_GROUP})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'gameovercalculator2') and not self.suitHasCondition(suitId, 'phase3'):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'HighRollerGameOver2',  # Game Over after Using Puzzle
                                            'animName': 'song-and-dance',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_GROUP})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.TurnsElapsed % 3 == 0 and self.__suitCanAttack(suitId) and not self.suitHasCondition(suitId, 'phase3'):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'HighRollerWheelSpin',  # Wheel Spin
                                            'animName': 'wheelspin',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.TurnsElapsed % 3 == 0 and self.__suitCanAttack(suitId) and not self.suitHasCondition(suitId, 'phase3'):
                    attack = self.__getCheatAttack(suitId, random.choice([{'suitName': self.battle.activeSuits[i].dna.name,
                                                           'name': 'HighRollerPuzzle',
                                                           'animName': 'taunt',
                                                           'hp': 0,
                                                           'acc': 100,
                                                           'freq': 0,
                                                           'group': SuitBattleGlobals.ATK_TGT_SINGLE},
                                                          {'suitName': self.battle.activeSuits[i].dna.name,
                                                           'name': 'HighRollerPuzzleBan',
                                                           'animName': 'cease',
                                                           'hp': 0,
                                                           'acc': 100,
                                                           'freq': 0,
                                                           'group': SuitBattleGlobals.ATK_TGT_SINGLE}]))
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                # if not self.TurnsElapsed % 3 == 0 and not self.TurnsElapsed == 0 and self.__suitCanAttack(suitId):
                #     attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                #                             'name': 'HighRollerGameTimeSpawn',  # Spawn After Puzzle
                #                             'animName': 'snap',
                #                             'hp': 0,
                #                             'acc': 100,
                #                             'freq': 0,
                #                             'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                #     if attack[SUIT_ATK_COL]:
                #         self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'gametimecalculator') and not self.suitHasCondition(suitId, 'phase3'):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'TargetCheck',  # Checks for Alive Cogs to use Game Time on
                                            'animName': 'nothing',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'targetCheckCondition') and self.getSuitConditionModifier(suitId, 'targetCheckCondition') > -1 and self.__suitCanAttack(suitId) and not self.suitHasCondition(suitId, 'phase3'):
                    attack = self.__getCheatAttack(suitId, random.choice([{'suitName': self.battle.activeSuits[i].dna.name,
                                                           'name': 'HighRollerGameTimeCog',
                                                           'animName': 'snap',
                                                           'hp': 0,
                                                           'acc': 100,
                                                           'freq': 0,
                                                           'group': SuitBattleGlobals.ATK_TGT_SINGLE},
                                                          {'suitName': self.battle.activeSuits[i].dna.name,
                                                           'name': 'HighRollerGameTimeCog2',
                                                           'animName': 'snap',
                                                           'hp': 0,
                                                           'acc': 100,
                                                           'freq': 0,
                                                           'group': SuitBattleGlobals.ATK_TGT_SINGLE}]))
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if len(self.battle.activeSuits) < 7 and self.__suitCanAttack(suitId) and not self.suitHasCondition(
                        suitId, 'spawncalculator') and not self.TurnsElapsed % 3 == 0 and not self.suitHasCondition(suitId, 'phase3'):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'HighRollerGameTimeSpawn',  # Spawn Cogs
                                            'animName': 'snap',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                # if self.suitHasCondition(suitId, 'target3') and self.__suitCanAttack(suitId):
                #     attack = self.__getCheatAttack(suitId, random.choice([{'suitName': self.battle.activeSuits[i].dna.name,
                #                                                            'name': 'HighRollerGameTimeCog3',
                #                                                            'animName': 'snap',
                #                                                            'hp': 0,
                #                                                            'acc': 100,
                #                                                            'freq': 0,
                #                                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE},
                #                                                           {'suitName': self.battle.activeSuits[i].dna.name,
                #                                                            'name': 'HighRollerGameTimeCog4',
                #                                                            'animName': 'snap',
                #                                                            'hp': 0,
                #                                                            'acc': 100,
                #                                                            'freq': 0,
                #                                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE}]))
                #     if attack[SUIT_ATK_COL]:
                        # self.battle.suitAttacks.append(attack)
                # if self.suitHasCondition(suitId, 'target4') and self.__suitCanAttack(suitId):
                #     attack = self.__getCheatAttack(suitId, random.choice([{'suitName': self.battle.activeSuits[i].dna.name,
                #                                                            'name': 'HighRollerGameTimeCog5',
                #                                                            'animName': 'snap',
                #                                                            'hp': 0,
                #                                                            'acc': 100,
                #                                                            'freq': 0,
                #                                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE},
                #                                                           {'suitName': self.battle.activeSuits[i].dna.name,
                #                                                            'name': 'HighRollerGameTimeCog6',
                #                                                            'animName': 'snap',
                #                                                            'hp': 0,
                #                                                            'acc': 100,
                #                                                            'freq': 0,
                #                                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE}]))
                #     if attack[SUIT_ATK_COL]:
                        # self.battle.suitAttacks.append(attack)
                # if self.suitHasCondition(suitId, 'target5') and self.__suitCanAttack(suitId):
                #     attack = self.__getCheatAttack(suitId, random.choice([{'suitName': self.battle.activeSuits[i].dna.name,
                #                                                            'name': 'HighRollerGameTimeCog7',
                #                                                            'animName': 'snap',
                #                                                            'hp': 0,
                #                                                            'acc': 100,
                #                                                            'freq': 0,
                #                                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE},
                #                                                           {'suitName': self.battle.activeSuits[i].dna.name,
                #                                                            'name': 'HighRollerGameTimeCog8',
                #                                                            'animName': 'snap',
                #                                                            'hp': 0,
                #                                                            'acc': 100,
                #                                                            'freq': 0,
                #                                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE}]))
                #     if attack[SUIT_ATK_COL]:
                        # self.battle.suitAttacks.append(attack)
                # if self.suitHasCondition(suitId, 'target6') and self.__suitCanAttack(suitId):
                #     attack = self.__getCheatAttack(suitId, random.choice([{'suitName': self.battle.activeSuits[i].dna.name,
                #                                                            'name': 'HighRollerGameTimeCog9',
                #                                                            'animName': 'snap',
                #                                                            'hp': 0,
                #                                                            'acc': 100,
                #                                                            'freq': 0,
                #                                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE},
                #                                                           {'suitName': self.battle.activeSuits[i].dna.name,
                #                                                            'name': 'HighRollerGameTimeCog10',
                #                                                            'animName': 'snap',
                #                                                            'hp': 0,
                #                                                            'acc': 100,
                #                                                            'freq': 0,
                #                                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE}]))
                #     if attack[SUIT_ATK_COL]:
                        # self.battle.suitAttacks.append(attack)

        # Secondary Cheats
        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId


                # End Of Round High Roller Attacks
        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'hroller' and self.suitHasCondition(suitId, 'phase3'):
                self.highRollerAttacks = [1, 2, 3, 4]
                if self.TurnsElapsed % 1 == 0 and self.suitHasCondition(suitId, 'phase3') and self.__suitCanAttack(
                        suitId):
                    condition = random.choice(self.highRollerAttacks)
                    if condition == 1:
                        self.highRollerAttacks.remove(condition)
                        attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                           'name': 'HighRollerConduction',
                                                           'animName': 'throw-object',
                                                           'hp': 0,
                                                           'acc': 100,
                                                           'freq': 0,
                                                           'group': SuitBattleGlobals.ATK_TGT_DOUBLE})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    elif condition == 2:
                        self.highRollerAttacks.remove(condition)
                        attack = self.__getCheatAttack(suitId, random.choice([
                                                          {'suitName': self.battle.activeSuits[i].dna.name,
                                                           'name': 'HighRollerDiceRouletteCogs',
                                                           'animName': 'nothing',
                                                           'hp': 0,
                                                           'acc': 100,
                                                           'freq': 0,
                                                           'group': SuitBattleGlobals.ATK_TGT_SINGLE},
                                                          {'suitName': self.battle.activeSuits[i].dna.name,
                                                           'name': 'HighRollerDiceRouletteToons',
                                                           'animName': 'nothing',
                                                           'hp': 0,
                                                           'acc': 100,
                                                           'freq': 0,
                                                           'group': random.choice((SuitBattleGlobals.ATK_TGT_GROUP, SuitBattleGlobals.ATK_TGT_DOUBLE, SuitBattleGlobals.ATK_TGT_TRIPLE, SuitBattleGlobals.ATK_TGT_SINGLE))},
                                                          {'suitName': self.battle.activeSuits[i].dna.name,
                                                           'name': 'HighRollerDiceRouletteNobody',
                                                           'animName': 'nothing',
                                                           'hp': 0,
                                                           'acc': 100,
                                                           'freq': 0,
                                                           'group': SuitBattleGlobals.ATK_TGT_SINGLE},
                                                          ]))
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    elif condition == 3:
                        self.highRollerAttacks.remove(condition)
                        attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                           'name': 'HighRollerRolled',
                                                           'animName': 'magic3',
                                                           'hp': 0,
                                                           'acc': 100,
                                                           'freq': 0,
                                                           'group': SuitBattleGlobals.ATK_TGT_GROUP})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    elif condition == 4:
                        self.highRollerAttacks.remove(condition)
                        roll = random.randint(0, 100)
                        if roll > 15:
                            attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'HighRollerFreeCruise',
                                                            'animName': 'song-and-dance',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_GROUP})
                            if attack[SUIT_ATK_COL]:
                                self.battle.suitAttacks.append(attack)
                        else:
                            attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                           'name': 'HighRollerRaisingTheAnte',
                                                           'animName': 'song-and-dance',
                                                           'hp': 0,
                                                           'acc': 100,
                                                           'freq': 0,
                                                           'group': SuitBattleGlobals.ATK_TGT_GROUP})
                            if attack[SUIT_ATK_COL]:
                                self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'hroller' and self.suitHasCondition(suitId, 'phase3'):
                if self.battle.activeSuits[i].currHP <= 51851 and not self.suitHasCondition(suitId,
                                                                                            'aceInTheHole') and len(
                    self.battle.activeSuits) > 1:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                'name': 'HighRollerAceInTheHole',  # Ace In The Hole
                                                'animName': 'nothing',
                                                'hp': 0,
                                                'acc': 100,
                                                'freq': 0,
                                                'group': SuitBattleGlobals.ATK_TGT_GROUP})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'hroller' and self.suitHasCondition(suitId, 'phase3'):
                if self.TurnsElapsed % 1 == 0 and self.suitHasCondition(suitId, 'phase3') and self.__suitCanAttack(
                        suitId):
                    condition = random.choice(self.highRollerAttacks)
                    if condition == 1:
                        self.highRollerAttacks.remove(condition)
                        attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                           'name': 'HighRollerConduction',
                                                           'animName': 'throw-object',
                                                           'hp': 0,
                                                           'acc': 100,
                                                           'freq': 0,
                                                           'group': SuitBattleGlobals.ATK_TGT_DOUBLE})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    elif condition == 2:
                        self.highRollerAttacks.remove(condition)
                        attack = self.__getCheatAttack(suitId, random.choice([
                                                          {'suitName': self.battle.activeSuits[i].dna.name,
                                                           'name': 'HighRollerDiceRouletteCogs',
                                                           'animName': 'nothing',
                                                           'hp': 0,
                                                           'acc': 100,
                                                           'freq': 0,
                                                           'group': SuitBattleGlobals.ATK_TGT_SINGLE},
                                                          {'suitName': self.battle.activeSuits[i].dna.name,
                                                           'name': 'HighRollerDiceRouletteToons',
                                                           'animName': 'nothing',
                                                           'hp': 0,
                                                           'acc': 100,
                                                           'freq': 0,
                                                           'group': random.choice((SuitBattleGlobals.ATK_TGT_GROUP, SuitBattleGlobals.ATK_TGT_DOUBLE, SuitBattleGlobals.ATK_TGT_TRIPLE, SuitBattleGlobals.ATK_TGT_SINGLE))},
                                                          {'suitName': self.battle.activeSuits[i].dna.name,
                                                           'name': 'HighRollerDiceRouletteNobody',
                                                           'animName': 'nothing',
                                                           'hp': 0,
                                                           'acc': 100,
                                                           'freq': 0,
                                                           'group': SuitBattleGlobals.ATK_TGT_SINGLE},
                                                          ]))
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    elif condition == 3:
                        self.highRollerAttacks.remove(condition)
                        attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                           'name': 'HighRollerRolled',
                                                           'animName': 'magic3',
                                                           'hp': 0,
                                                           'acc': 100,
                                                           'freq': 0,
                                                           'group': SuitBattleGlobals.ATK_TGT_GROUP})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    elif condition == 4:
                        self.highRollerAttacks.remove(condition)
                        roll = random.randint(0, 100)
                        if roll > 15:
                            attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'HighRollerFreeCruise',
                                                            'animName': 'song-and-dance',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_GROUP})
                            if attack[SUIT_ATK_COL]:
                                self.battle.suitAttacks.append(attack)
                        else:
                            attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                           'name': 'HighRollerRaisingTheAnte',
                                                           'animName': 'song-and-dance',
                                                           'hp': 0,
                                                           'acc': 100,
                                                           'freq': 0,
                                                           'group': SuitBattleGlobals.ATK_TGT_GROUP})
                            if attack[SUIT_ATK_COL]:
                                self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'hroller' and self.suitHasCondition(suitId, 'phase3'):
                if self.suitHasCondition(suitId, 'vulnerable') and self.suitHasCondition(suitId,
                                                                                         'phase3') and self.__suitCanAttack(
                    suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'HighRollerTrickOfTheLight',  # Trick Of The Light
                                            'animName': 'nothing',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                damageCogs = 0
                for suit in self.battle.activeSuits:
                    if suit.dna.name != 'hrollers':
                        continue
                    if suit.getHP() > 0 and suit.dna.name == 'hrollers':
                        damageCogs = 1
                if damageCogs == 0 and self.suitHasCondition(suitId, 'phase3') and not self.suitHasCondition(suitId, 'trickofthelight') and not self.suitHasCondition(suitId, 'vulnerable') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'HighRollerVulnerable',  # Vulnerability
                                            'animName': 'nothing',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                # if len(self.battle.activeSuits) == 1 and not self.suitHasCondition(suitId,
                #                                                                    'phase3') and self.__suitCanAttack(
                #     suitId):
                #     attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                #                             'name': 'HighRollerPhase3',  # Phase 3 Movie
                #                             'animName': 'nothing',
                #                             'hp': 0,
                #                             'acc': 100,
                #                             'freq': 0,
                #                             'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                #     if attack[SUIT_ATK_COL]:
                #         self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'bashcalculator') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'HighRollerTrickOfTheLight',  # Trick Of The Light
                                            'animName': 'nothing',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)

        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'hroller':
                if self.suitHasCondition(suitId, 'hollywoodHijinks') and self.getSuitConditionTurns(suitId, 'hollywoodHijinks') == 1 and not self.suitHasCondition(suitId, 'phase3'):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'HighRollerCommercialBreak',  # Videographer Death to Sacrifice All Cogs
                                            'animName': 'snap',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.battle.activeSuits[i].currHP == 1 and not self.suitHasCondition(suitId, 'hollywoodHijinks') and not self.suitHasCondition(suitId, 'phase2'):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'HighRollerCommercialBreak',  # Absorb Damage Movie Level
                                            'animName': 'snap',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.battle.activeSuits[i].currHP == 1 and not self.suitHasCondition(suitId, 'hollywoodHijinks') and not self.suitHasCondition(suitId, 'phase2'):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'HighRollerPhase2',  # Spawn Cogs
                                            'animName': 'nothing',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'hollywoodHijinks') and self.getSuitConditionTurns(suitId, 'hollywoodHijinks') == 1 and not self.suitHasCondition(suitId, 'phase3'):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'HighRollerPhase3',  # Phase 3 Movie
                                            'animName': 'nothing',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
