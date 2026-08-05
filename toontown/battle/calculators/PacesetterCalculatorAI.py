from toontown.battle.BattleBase import *
from toontown.battle.BattleGlobals import *
from toontown.battle import SuitBattleGlobals
import random
import math

class PacesetterCalculatorAI:

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

    def calculatePacesetterAttacks(self):
        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'psetter': 
                if self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'PacesetterHurrySickness',
                                                            'animName': 'finger-wag',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_GROUP})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'psetter': 
                if self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'PacesetterHurrySicknessBan',
                                                            'animName': 'finger-wag',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_GROUP})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)

        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'psetter':
                if self.battle.activeSuits[i].currHP > 0 and not self.battle.activeSuits[i].currHP >= 12750:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                'name': 'PresidentTargetCheck',  # Target Check
                                                                'animName': 'nothing',
                                                                'hp': 0,
                                                                'acc': 100,
                                                                'freq': 0,
                                                                'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'targetCheckCondition') and self.getSuitConditionModifier(suitId, 'targetCheckCondition') > -1 and self.battle.activeSuits[i].currHP > 0:
                    if not self.suitHasCondition(suitId, 'sounded') and self.suitHasCondition(suitId, 'unlureSuit'):
                        attack = self.__getLureRemoval(suitId)
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                'name': random.choice(('RushJobTrap',
                                                                                            'RushJobLure',
                                                                                            'RushJobThrow',
                                                                                            'RushJobSquirt',
                                                                                            'RushJobZap',
                                                                                            'RushJobSound',
                                                                                            'RushJobDrop')),
                                                                'animName': 'rush-job',
                                                                'hp': 0,
                                                                'acc': 100,
                                                                'freq': 0,
                                                                'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)

                roll = random.randint(0, 100)
                if roll >= 25 and (self.battle.activeSuits[i].currHP < 8925 or self.suitHasCondition(suitId, 'overclocked')):
                    if self.battle.activeSuits[i].currHP > 0:
                        attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                    'name': 'PresidentTargetCheck',  # Target Check
                                                                    'animName': 'nothing',
                                                                    'hp': 0,
                                                                    'acc': 100,
                                                                    'freq': 0,
                                                                    'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    if self.suitHasCondition(suitId, 'targetCheckCondition') and self.getSuitConditionModifier(suitId, 'targetCheckCondition') > -1 and self.battle.activeSuits[i].currHP > 0:
                        if not self.suitHasCondition(suitId, 'sounded') and self.suitHasCondition(suitId, 'unlureSuit'):
                            attack = self.__getLureRemoval(suitId)
                            if attack[SUIT_ATK_COL]:
                                self.battle.suitAttacks.append(attack)
                        attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                    'name': random.choice(('RushJobTrap',
                                                                                                'RushJobLure',
                                                                                                'RushJobThrow',
                                                                                                'RushJobSquirt',
                                                                                                'RushJobZap',
                                                                                                'RushJobSound',
                                                                                                'RushJobDrop')),
                                                                    'animName': 'rush-job',
                                                                    'hp': 0,
                                                                    'acc': 100,
                                                                    'freq': 0,
                                                                    'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)

                roll = random.randint(0, 100)
                if roll >= 25 and self.battle.activeSuits[i].currHP < 3825:
                    if self.battle.activeSuits[i].currHP > 0:
                        attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                    'name': 'PresidentTargetCheck',  # Target Check
                                                                    'animName': 'nothing',
                                                                    'hp': 0,
                                                                    'acc': 100,
                                                                    'freq': 0,
                                                                    'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                        attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                    'name': random.choice(('RushJobTrap',
                                                                                                'RushJobLure',
                                                                                                'RushJobThrow',
                                                                                                'RushJobSquirt',
                                                                                                'RushJobZap',
                                                                                                'RushJobSound',
                                                                                                'RushJobDrop')),
                                                                    'animName': 'rush-job',
                                                                    'hp': 0,
                                                                    'acc': 100,
                                                                    'freq': 0,
                                                                    'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)


        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'psetter':  # Pacesetter
                if self.battle.activeSuits[i].currHP > 0 and self.battle.activeSuits[i].currHP <= 8415 and not self.getSuitConditionModifier(suitId, 'alreadyMoving'):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'PacesetterMovingGoalposts',
                                                            'animName': 'magic3',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_GROUP})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.battle.activeSuits[i].currHP > 0 and self.battle.activeSuits[i].currHP <= 10200 and self.TurnsElapsed % 4 == 0:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'PacesetterContentSync',
                                                            'animName': 'magic3',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.battle.activeSuits[i].currHP > 0:
                    if self.battle.activeSuits[i].currHP >= 12750 and not self.suitHasCondition(suitId, 'overclocked') and not self.suitHasCondition(suitId, 'turn2') and self.suitHasCondition(suitId, 'turn1'):
                        attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                    'name': 'PacesetterTurn2',
                                                                    'animName': 'nothing',
                                                                    'hp': 0,
                                                                    'acc': 100,
                                                                    'freq': 0,
                                                                    'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                            self.setSuitCondition(suitId, 'turn2', 1, -1, 'setBoth')
                    if self.battle.activeSuits[i].currHP >= 12750 and not self.suitHasCondition(suitId, 'overclocked') and not self.suitHasCondition(suitId, 'turn1'):
                        attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                    'name': 'PacesetterTurn1',
                                                                    'animName': 'nothing',
                                                                    'hp': 0,
                                                                    'acc': 100,
                                                                    'freq': 0,
                                                                    'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                            self.setSuitCondition(suitId, 'turn1', 1, -1, 'setBoth')
                    if self.battle.activeSuits[i].currHP >= 12750 and not self.suitHasCondition(suitId, 'overclocked') and self.suitHasCondition(suitId, 'turn2') and self.suitHasCondition(suitId, 'turn1'):
                        attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                    'name': 'PacesetterEarlyOverclocked',
                                                                    'animName': 'overclocked',
                                                                    'hp': 0,
                                                                    'acc': 100,
                                                                    'freq': 0,
                                                                    'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    if self.battle.activeSuits[i].currHP <= 5100 and not self.suitHasCondition(suitId, 'overclocked'):
                        attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                    'name': 'PacesetterOverclocked',
                                                                    'animName': 'overclocked',
                                                                    'hp': 0,
                                                                    'acc': 100,
                                                                    'freq': 0,
                                                                    'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    if not self.getSuitConditionModifier(suitId, 'battleSpeed') >= 4 and not self.suitHasCondition(suitId, 'overclocked') and not self.battle.activeSuits[i].currHP >= 12750:
                        attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                    'name': 'PacesetterComeOn',
                                                                    'animName': 'come-on',
                                                                    'hp': 0,
                                                                    'acc': 100,
                                                                    'freq': 0,
                                                                    'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
