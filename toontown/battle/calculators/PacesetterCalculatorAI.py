from __future__ import absolute_import
from toontown.battle.BattleBase import *
from toontown.battle.BattleGlobals import *
from toontown.battle import SuitBattleGlobals
import random
import math
from six.moves import range

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

    def __getGenericSuitAttack(self, suitId):
        return self.calculator.getGenericSuitAttack(suitId)

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

    def __openingChallengeHasRealAction(self):
        # DistributedBattleBaseAI has already converted PASS and UN_ATTACK
        # into the same NO_ATTACK entry used by a timer expiry before the
        # calculator runs.  That is exactly what Clash wants here: both a
        # deliberate Pass and doing nothing for the whole timer count as one
        # empty challenge round.  Any remaining attack entry (gag, IOU/NPCSOS,
        # Cog reward, SOS, etc.) is a real Toon action and cancels the opening
        # challenge.
        for toonId in self.battle.activeToons:
            attack = self.battle.toonAttacks.get(toonId)
            if attack and attack[TOON_TRACK_COL] != NO_ATTACK:
                return True
        return False

    def __chooseRushJobAttack(self, suitId):
        choices = [
            'RushJobTrap',
            'RushJobLure',
            'RushJobThrow',
            'RushJobSquirt',
            'RushJobZap',
            'RushJobSound',
            'RushJobDrop',
        ]

        targetIndex = self.getSuitConditionModifier(
            suitId, 'targetCheckCondition')
        if (targetIndex is not None and
                targetIndex >= 0 and
                targetIndex < len(self.battle.activeSuits)):
            targetSuit = self.battle.activeSuits[targetIndex]
            if targetSuit is not None:
                # Match Clash: Trap is not a legal Rush Job track when the
                # selected Cog already has an active trap.  Pacesetter is
                # intentionally included in the same check.
                try:
                    trapped = (
                        self.calculator.getSuitTrapType(targetSuit.doId)
                        != NO_TRAP
                    )
                except:
                    trapped = targetSuit.doId in getattr(
                        self.calculator, 'traps', {})

                if trapped and 'RushJobTrap' in choices:
                    choices.remove('RushJobTrap')

        return random.choice(choices)

    def __encodeSuitOrder(self, oldSuits, newSuits):
        value = 0
        for newIndex in range(len(newSuits)):
            oldIndex = oldSuits.index(newSuits[newIndex])
            value |= oldIndex << (newIndex * 3)
        return value

    def __cancelOpeningChallengeIfNeeded(self, suitId):
        if self.suitHasCondition(suitId, 'openingChallengeCancelled'):
            return False
        if self.suitHasCondition(suitId, 'overclocked'):
            return False
        if self.suitHasCondition(suitId, 'turn2'):
            return False

        # Clash challenge rule:
        #   empty round (Pass OR timeout) -> keep the challenge alive
        #   any real Toon action -> permanently cancel the challenge
        if self.__openingChallengeHasRealAction():
            self.setSuitCondition(
                suitId, 'openingChallengeCancelled', 1, -1, 'setBoth')
            return True
        return False

    def calculatePacesetterAttacks(self):
        for i in range(len(self.battle.activeSuits)):
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

        rushJobsQueued = set()
        for i in range(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'psetter':
                self.__cancelOpeningChallengeIfNeeded(suitId)
                if self.battle.activeSuits[i].currHP > 0 and (not self.battle.activeSuits[i].currHP >= 12750 or self.suitHasCondition(suitId, 'openingChallengeCancelled')):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                'name': self.__chooseRushJobAttack(suitId),
                                                                'animName': 'rush-job',
                                                                'hp': 0,
                                                                'acc': 100,
                                                                'freq': 0,
                                                                'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                                                            'targetType': 'suit',
                                                            'allowSelfTarget': True,
                                                             'excludeConditions': ('trapRushJob', 'lureRushJob', 'throwRushJob', 'squirtRushJob', 'zapRushJob', 'soundRushJob', 'dropRushJob',),
                                                            'targetSelf': False,
                                                        'excludeManagers': False})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                        rushJobsQueued.add(suitId)

                roll = random.randint(0, 100)
                if roll >= 25 and (self.battle.activeSuits[i].currHP < 8925 or self.suitHasCondition(suitId, 'overclocked')):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                'name': self.__chooseRushJobAttack(suitId),
                                                                'animName': 'rush-job',
                                                                'hp': 0,
                                                                'acc': 100,
                                                                'freq': 0,
                                                                'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                                                            'targetType': 'suit',
                                                            'allowSelfTarget': True,
                                                             'excludeConditions': ('trapRushJob', 'lureRushJob', 'throwRushJob', 'squirtRushJob', 'zapRushJob', 'soundRushJob', 'dropRushJob',),
                                                            'targetSelf': False,
                                                        'excludeManagers': False})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                        rushJobsQueued.add(suitId)

                roll = random.randint(0, 100)
                if roll >= 25 and self.battle.activeSuits[i].currHP < 3825:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                'name': self.__chooseRushJobAttack(suitId),
                                                                'animName': 'rush-job',
                                                                'hp': 0,
                                                                'acc': 100,
                                                                'freq': 0,
                                                                'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                                                            'targetType': 'suit',
                                                            'allowSelfTarget': True,
                                                             'excludeConditions': ('trapRushJob', 'lureRushJob', 'throwRushJob', 'squirtRushJob', 'zapRushJob', 'soundRushJob', 'dropRushJob',),
                                                            'targetSelf': False,
                                                        'excludeManagers': False})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                        rushJobsQueued.add(suitId)


        for suit in self.battle.activeSuits[:]:
            if suit.dna.name != 'psetter' or suit.currHP <= 0:
                continue
            oldActiveSuits = self.battle.activeSuits[:]
            oldLivingSuits = []
            livingPositions = []
            for index in range(len(oldActiveSuits)):
                otherSuit = oldActiveSuits[index]
                if otherSuit.currHP > 0 and not self.suitHasCondition(otherSuit.doId, 'dead'):
                    oldLivingSuits.append(otherSuit)
                    livingPositions.append(index)
            if suit not in oldLivingSuits or len(oldLivingSuits) < 2:
                continue
            newLivingSuits = oldLivingSuits[:]
            random.shuffle(newLivingSuits)
            if newLivingSuits == oldLivingSuits:
                newLivingSuits.reverse()
            newActiveSuits = oldActiveSuits[:]
            for index in range(len(livingPositions)):
                newActiveSuits[livingPositions[index]] = newLivingSuits[index]
            payload = self.__encodeSuitOrder(oldActiveSuits, newActiveSuits)
            attack = self.__getCheatAttack(suit.doId, {
                'suitName': suit.dna.name,
                'name': 'PacesetterCorporateRestructuring',
                'animName': 'quick-jump',
                'hp': payload,
                'acc': 100,
                'freq': 0,
                'group': SuitBattleGlobals.ATK_TGT_GROUP
            })
            if attack[SUIT_ATK_COL]:
                self.battle.suitAttacks.append(attack)
            self.battle.queueSuitOrder([otherSuit.doId for otherSuit in newActiveSuits])

        for i in range(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'psetter':  # Pacesetter
                self.__cancelOpeningChallengeIfNeeded(suitId)
                openingChallengeCancelled = self.suitHasCondition(
                    suitId, 'openingChallengeCancelled')

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
                    if self.battle.activeSuits[i].currHP >= 12750 and not openingChallengeCancelled and not self.suitHasCondition(suitId, 'overclocked') and not self.suitHasCondition(suitId, 'turn2') and self.suitHasCondition(suitId, 'turn1'):
                        attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                    'name': 'PacesetterTurn2',
                                                                    'animName': 'nothing',
                                                                    'hp': 0,
                                                                    'acc': 100,
                                                                    'freq': 0,
                                                                    'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                                        'targetType': 'none'})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                            self.setSuitCondition(suitId, 'turn2', 1, -1, 'setBoth')
                    if self.battle.activeSuits[i].currHP >= 12750 and not openingChallengeCancelled and not self.suitHasCondition(suitId, 'overclocked') and not self.suitHasCondition(suitId, 'turn1'):
                        attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                    'name': 'PacesetterTurn1',
                                                                    'animName': 'nothing',
                                                                    'hp': 0,
                                                                    'acc': 100,
                                                                    'freq': 0,
                                                                    'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                                        'targetType': 'none'})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                            self.setSuitCondition(suitId, 'turn1', 1, -1, 'setBoth')
                    if self.battle.activeSuits[i].currHP >= 12750 and not openingChallengeCancelled and not self.suitHasCondition(suitId, 'overclocked') and self.suitHasCondition(suitId, 'turn2') and self.suitHasCondition(suitId, 'turn1'):
                        attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                    'name': 'PacesetterEarlyOverclocked',
                                                                    'animName': 'overclocked',
                                                                    'hp': 0,
                                                                    'acc': 100,
                                                                    'freq': 0,
                                                                    'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                                        'targetType': 'none'})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    if (self.battle.activeSuits[i].currHP <= 5100 and
                            not self.suitHasCondition(suitId, 'overclocked') and
                            suitId in rushJobsQueued):
                        attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                    'name': 'PacesetterOverclocked',
                                                                    'animName': 'overclocked',
                                                                    'hp': 0,
                                                                    'acc': 100,
                                                                    'freq': 0,
                                                                    'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                                        'targetType': 'none'})
                        if attack[SUIT_ATK_COL]:
                            self.setSuitCondition(suitId, 'battleSpeed', 6, -1, 'setBoth')
                            self.battle.suitAttacks.append(attack)
                    if not self.getSuitConditionModifier(suitId, 'battleSpeed') >= 4 and not self.suitHasCondition(suitId, 'overclocked') and not self.battle.activeSuits[i].currHP >= 12750:
                        attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                    'name': 'PacesetterComeOn',
                                                                    'animName': 'come-on',
                                                                    'hp': 0,
                                                                    'acc': 100,
                                                                    'freq': 0,
                                                                    'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                                        'targetType': 'none'})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)

        for suit in self.battle.activeSuits[:]:
            if suit.dna.name != 'psetter' or suit.currHP <= 0:
                continue
            oldActiveSuits = self.battle.activeSuits[:]
            oldLivingSuits = []
            livingPositions = []
            for index in range(len(oldActiveSuits)):
                otherSuit = oldActiveSuits[index]
                if otherSuit.currHP > 0 and not self.suitHasCondition(otherSuit.doId, 'dead'):
                    oldLivingSuits.append(otherSuit)
                    livingPositions.append(index)
            if suit not in oldLivingSuits or len(oldLivingSuits) < 2:
                continue
            newLivingSuits = oldLivingSuits[:]
            random.shuffle(newLivingSuits)
            if newLivingSuits == oldLivingSuits:
                newLivingSuits.reverse()
            newActiveSuits = oldActiveSuits[:]
            for index in range(len(livingPositions)):
                newActiveSuits[livingPositions[index]] = newLivingSuits[index]
            payload = self.__encodeSuitOrder(oldActiveSuits, newActiveSuits)
            attack = self.__getCheatAttack(suit.doId, {
                'suitName': suit.dna.name,
                'name': 'PacesetterCorporateRestructuring',
                'animName': 'quick-jump',
                'hp': payload,
                'acc': 100,
                'freq': 0,
                'group': SuitBattleGlobals.ATK_TGT_GROUP,
                                        'targetType': 'none'
            })
            if attack[SUIT_ATK_COL]:
                self.battle.suitAttacks.append(attack)
            self.battle.queueSuitOrder([otherSuit.doId for otherSuit in newActiveSuits])
