from toontown.battle.BattleBase import *
from toontown.battle.BattleGlobals import *
from toontown.battle import SuitBattleGlobals
import random
import math

class SuitSpawnCalculatorAI:

    def __init__(self, calculator):
        self.calculator = calculator
        self.battle = calculator.battle
        self._pacesetterSpawnCycleRounds = {}

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

    def calculateSuitSpawns(self):
        for i in xrange(len(self.battle.activeSuits)): # Cheat Calculators
            suitId = self.battle.activeSuits[i].doId
            x = self.TurnsElapsed
            # if self.battle.activeSuits[i].dna.name == 'stenog':
            #     if x % 2 == 0 and self.battle.activeSuits[i].currHP > 0:
            #         from toontown.suit.DistributedLawbotBossAI import DistributedLawbotBossAI

            #         boss = None
            #         for do in simbase.air.doId2do.values():
            #             if isinstance(do, DistributedLawbotBossAI):
            #                 for s in self.battle.activeSuits:
            #                     if s in do.activeSuits:
            #                         boss = do
            #                         break
            #                 for s in self.battle.activeSuits:
            #                     if s in do.activeSuits:
            #                         if s.dna.name == 'stenog':
            #                             if len(self.battle.activeSuits) < 6 and not self.suitHasCondition(suitId, 'alreadyCogSpawn'):
            #                                 if self.suitHasCondition(suitId, 'desperation'):
            #                                     boss.appendSuitsToBattle(boss.battleNumber, 'lit')
            #                                     boss.appendSuitsToBattle(boss.battleNumber, 'lit')
            #                                 else:
            #                                     boss.appendSuitsToBattle(boss.battleNumber, 'lit')
            # if self.battle.activeSuits[i].dna.name == 'caseman':
            #     if x % 2 == 0 and self.battle.activeSuits[i].currHP > 0:
            #         from toontown.suit.DistributedLawbotBossAI import DistributedLawbotBossAI

            #         boss = None
            #         for do in simbase.air.doId2do.values():
            #             if isinstance(do, DistributedLawbotBossAI):
            #                 for s in self.battle.activeSuits:
            #                     if s in do.activeSuits:
            #                         boss = do
            #                         break
            #                 for s in self.battle.activeSuits:
            #                     if s in do.activeSuits:
            #                         if s.dna.name == 'caseman':
            #                             if len(self.battle.activeSuits) < 6 and not self.suitHasCondition(suitId, 'alreadyCogSpawn'):
            #                                 if self.suitHasCondition(suitId, 'desperation'):
            #                                     boss.appendSuitsToBattle(boss.battleNumber, 'lit')
            #                                     boss.appendSuitsToBattle(boss.battleNumber, 'lit')
            #                                 else:
            #                                     boss.appendSuitsToBattle(boss.battleNumber, 'lit')
            # if self.battle.activeSuits[i].dna.name == 'sgoat':
            #     if x % 2 == 0 and self.battle.activeSuits[i].currHP > 0:
            #         from toontown.suit.DistributedLawbotBossAI import DistributedLawbotBossAI

            #         boss = None
            #         for do in simbase.air.doId2do.values():
            #             if isinstance(do, DistributedLawbotBossAI):
            #                 for s in self.battle.activeSuits:
            #                     if s in do.activeSuits:
            #                         boss = do
            #                         break
            #                 for s in self.battle.activeSuits:
            #                     if s in do.activeSuits:
            #                         if s.dna.name == 'sgoat':
            #                             if len(self.battle.activeSuits) < 6 and not self.suitHasCondition(suitId, 'alreadyCogSpawn'):
            #                                 if self.suitHasCondition(suitId, 'desperation'):
            #                                     boss.appendSuitsToBattle(boss.battleNumber, 'lit')
            #                                     boss.appendSuitsToBattle(boss.battleNumber, 'lit')
            #                                 else:
            #                                     boss.appendSuitsToBattle(boss.battleNumber, 'lit')
            # if self.battle.activeSuits[i].dna.name == 'phouse': #powerhouse
            #     if x % 2 == 0 and self.battle.activeSuits[i].currHP > 0:
            #         from toontown.suit.DistributedDirectorsAI import DistributedDirectorsAI

            #         boss = None
            #         for do in simbase.air.doId2do.values():
            #             if isinstance(do, DistributedDirectorsAI):
            #                 for s in self.battle.activeSuits:
            #                     if s in do.activeSuits:
            #                         boss = do
            #                         break
            #                 for s in self.battle.activeSuits:
            #                     if s in do.activeSuits:
            #                         if s.dna.name == 'phouse':
            #                             if len(self.battle.activeSuits) < 6 and not self.suitHasCondition(suitId, 'alreadyCogSpawn'):
            #                                 if self.suitHasCondition(suitId, 'desperation'):
            #                                     boss.appendSuitsToBattle(boss.battleNumber, 'ambDesperation')
            #                                     boss.appendSuitsToBattle(boss.battleNumber, 'ambDesperation')
            #                                 else:
            #                                     boss.appendSuitsToBattle(boss.battleNumber, 'amb')
            # if self.battle.activeSuits[i].dna.name == 'bkeeper':  # bookkeeper
            #     if x % 2 == 0 and self.battle.activeSuits[i].currHP > 0:
            #         from toontown.suit.DistributedDirectorsAI import DistributedDirectorsAI

            #         boss = None
            #         for do in simbase.air.doId2do.values():
            #             if isinstance(do, DistributedDirectorsAI):
            #                 for s in self.battle.activeSuits:
            #                     if s in do.activeSuits:
            #                         boss = do
            #                         break
            #                 for s in self.battle.activeSuits:
            #                     if s in do.activeSuits:
            #                         if s.dna.name == 'bkeeper':
            #                             if len(self.battle.activeSuits) < 6 and not self.suitHasCondition(suitId, 'alreadyCogSpawn'):
            #                                 if self.suitHasCondition(suitId, 'desperation'):
            #                                     boss.appendSuitsToBattle(boss.battleNumber, 'ambDesperation')
            #                                     boss.appendSuitsToBattle(boss.battleNumber, 'ambDesperation')
            #                                 else:
            #                                     boss.appendSuitsToBattle(boss.battleNumber, 'amb')
            # if self.battle.activeSuits[i].dna.name == 'wtapper':  # wiretapper
            #     if x % 2 == 0 and self.battle.activeSuits[i].currHP > 0:
            #         from toontown.suit.DistributedDirectorsAI import DistributedDirectorsAI

            #         boss = None
            #         for do in simbase.air.doId2do.values():
            #             if isinstance(do, DistributedDirectorsAI):
            #                 for s in self.battle.activeSuits:
            #                     if s in do.activeSuits:
            #                         boss = do
            #                         break
            #                 for s in self.battle.activeSuits:
            #                     if s in do.activeSuits:
            #                         if s.dna.name == 'wtapper':
            #                             if len(self.battle.activeSuits) < 6 and not self.suitHasCondition(suitId, 'alreadyCogSpawn'):
            #                                 if self.suitHasCondition(suitId, 'desperation'):
            #                                     boss.appendSuitsToBattle(boss.battleNumber, 'ambDesperation')
            #                                     boss.appendSuitsToBattle(boss.battleNumber, 'ambDesperation')
            #                                 else:
            #                                     boss.appendSuitsToBattle(boss.battleNumber, 'amb')
            # if self.battle.activeSuits[i].dna.name == 'ambass': #ambassador
            #     if x % 2 == 0 and self.battle.activeSuits[i].currHP > 0:
            #         from toontown.suit.DistributedDirectorsAI import DistributedDirectorsAI

            #         boss = None
            #         for do in simbase.air.doId2do.values():
            #             if isinstance(do, DistributedDirectorsAI):
            #                 for s in self.battle.activeSuits:
            #                     if s in do.activeSuits:
            #                         boss = do
            #                         break
            #                 for s in self.battle.activeSuits:
            #                     if s in do.activeSuits:
            #                         if s.dna.name == 'ambass':
            #                             if len(self.battle.activeSuits) < 6 and not self.suitHasCondition(suitId, 'alreadyCogSpawn'):
            #                                 if self.suitHasCondition(suitId, 'desperation'):
            #                                     boss.appendSuitsToBattle(boss.battleNumber, 'ambDesperation')
            #                                     boss.appendSuitsToBattle(boss.battleNumber, 'ambDesperation')
            #                                 else:
            #                                     boss.appendSuitsToBattle(boss.battleNumber, 'amb')
            # if self.battle.activeSuits[i].dna.name == 'safesupervis': #safety supervisor
            #     if x % 2 == 0 and self.battle.activeSuits[i].currHP > 0:
            #         from toontown.suit.DistributedSellbotBossMiniAI import DistributedSellbotBossMiniAI

            #         boss = None
            #         for do in simbase.air.doId2do.values():
            #             if isinstance(do, DistributedSellbotBossMiniAI):
            #                 for s in self.battle.activeSuits:
            #                     if s in do.activeSuits:
            #                         boss = do
            #                         break
            #                 for s in self.battle.activeSuits:
            #                     if s in do.activeSuits:
            #                         if s.dna.name == 'safesupervis':
            #                             if len(self.battle.activeSuits) < 6 and not self.suitHasCondition(suitId, 'alreadyCogSpawn'):
            #                                 if self.suitHasCondition(suitId, 'desperation'):
            #                                     boss.appendSuitsToBattle(boss.battleNumber, 'presDesperation')
            #                                     boss.appendSuitsToBattle(boss.battleNumber, 'presDesperation')
            #                                 else:
            #                                     boss.appendSuitsToBattle(boss.battleNumber, 'pres')
            # if self.battle.activeSuits[i].dna.name == 'ubuster': #union buster
            #     if x % 2 == 0 and self.battle.activeSuits[i].currHP > 0:
            #         from toontown.suit.DistributedSellbotBossMiniAI import DistributedSellbotBossMiniAI

            #         boss = None
            #         for do in simbase.air.doId2do.values():
            #             if isinstance(do, DistributedSellbotBossMiniAI):
            #                 for s in self.battle.activeSuits:
            #                     if s in do.activeSuits:
            #                         boss = do
            #                         break
            #                 for s in self.battle.activeSuits:
            #                     if s in do.activeSuits:
            #                         if s.dna.name == 'ubuster':
            #                             if len(self.battle.activeSuits) < 6 and not self.suitHasCondition(suitId, 'alreadyCogSpawn'):
            #                                 if self.suitHasCondition(suitId, 'desperation'):
            #                                     boss.appendSuitsToBattle(boss.battleNumber, 'presDesperation')
            #                                     boss.appendSuitsToBattle(boss.battleNumber, 'presDesperation')
            #                                 else:
            #                                     boss.appendSuitsToBattle(boss.battleNumber, 'pres')
            # if self.battle.activeSuits[i].dna.name == 'hustle': #hustler
            #     if x % 2 == 0 and self.battle.activeSuits[i].currHP > 0:
            #         from toontown.suit.DistributedSellbotBossMiniAI import DistributedSellbotBossMiniAI

            #         boss = None
            #         for do in simbase.air.doId2do.values():
            #             if isinstance(do, DistributedSellbotBossMiniAI):
            #                 for s in self.battle.activeSuits:
            #                     if s in do.activeSuits:
            #                         boss = do
            #                         break
            #                 for s in self.battle.activeSuits:
            #                     if s in do.activeSuits:
            #                         if s.dna.name == 'hustle':
            #                             if len(self.battle.activeSuits) < 6 and not self.suitHasCondition(suitId, 'alreadyCogSpawn'):
            #                                 if self.suitHasCondition(suitId, 'desperation'):
            #                                     boss.appendSuitsToBattle(boss.battleNumber, 'presDesperation')
            #                                     boss.appendSuitsToBattle(boss.battleNumber, 'presDesperation')
            #                                 else:
            #                                     boss.appendSuitsToBattle(boss.battleNumber, 'pres')
            # if self.battle.activeSuits[i].dna.name == 'radiog': #radiographer
            #     if x % 2 == 0 and self.battle.activeSuits[i].currHP > 0:
            #         from toontown.suit.DistributedSellbotBossMiniAI import DistributedSellbotBossMiniAI

            #         boss = None
            #         for do in simbase.air.doId2do.values():
            #             if isinstance(do, DistributedSellbotBossMiniAI):
            #                 for s in self.battle.activeSuits:
            #                     if s in do.activeSuits:
            #                         boss = do
            #                         break
            #                 for s in self.battle.activeSuits:
            #                     if s in do.activeSuits:
            #                         if s.dna.name == 'radiog':
            #                             if len(self.battle.activeSuits) < 6 and not self.suitHasCondition(suitId, 'alreadyCogSpawn'):
            #                                 if self.suitHasCondition(suitId, 'desperation'):
            #                                     boss.appendSuitsToBattle(boss.battleNumber, 'presDesperation')
            #                                     boss.appendSuitsToBattle(boss.battleNumber, 'presDesperation')
            #                                 else:
            #                                     boss.appendSuitsToBattle(boss.battleNumber, 'pres')
            # if self.battle.activeSuits[i].dna.name == 'rkeeper': #recordkeeper
            #     if x % 2 == 0 and self.battle.activeSuits[i].currHP > 0:
            #         from toontown.suit.DistributedBoardbotBossAI import DistributedBoardbotBossAI

            #         boss = None
            #         for do in simbase.air.doId2do.values():
            #             if isinstance(do, DistributedBoardbotBossAI):
            #                 for s in self.battle.activeSuits:
            #                     if s in do.activeSuits:
            #                         boss = do
            #                         break
            #                 for s in self.battle.activeSuits:
            #                     if s in do.activeSuits:
            #                         if s.dna.name == 'rkeeper':
            #                             if len(self.battle.activeSuits) < 6 and not self.suitHasCondition(suitId, 'alreadyCogSpawn'):
            #                                 if self.suitHasCondition(suitId, 'desperation'):
            #                                     boss.appendSuitsToBattle(boss.battleNumber, 'bdlitDesperation')
            #                                     boss.appendSuitsToBattle(boss.battleNumber, 'bdlitDesperation')
            #                                 else:
            #                                     boss.appendSuitsToBattle(boss.battleNumber, 'bdlit')
            # if self.battle.activeSuits[i].dna.name == 'cdirector':
            #     if x % 2 == 0 and self.battle.activeSuits[i].currHP > 0:
            #         from toontown.suit.DistributedBoardbotBossAI import DistributedBoardbotBossAI

            #         boss = None
            #         for do in simbase.air.doId2do.values():
            #             if isinstance(do, DistributedBoardbotBossAI):
            #                 for s in self.battle.activeSuits:
            #                     if s in do.activeSuits:
            #                         boss = do
            #                         break
            #                 for s in self.battle.activeSuits:
            #                     if s in do.activeSuits:
            #                         if s.dna.name == 'cdirector':
            #                             if len(self.battle.activeSuits) < 6 and not self.suitHasCondition(suitId, 'alreadyCogSpawn'):
            #                                 if self.suitHasCondition(suitId, 'desperation'):
            #                                     boss.appendSuitsToBattle(boss.battleNumber, 'bdlitDesperation')
            #                                     boss.appendSuitsToBattle(boss.battleNumber, 'bdlitDesperation')
            #                                 else:
            #                                     boss.appendSuitsToBattle(boss.battleNumber, 'bdlit')
            # if self.battle.activeSuits[i].dna.name == 'liquid':
            #     if x % 2 == 0 and self.battle.activeSuits[i].currHP > 0:
            #         from toontown.suit.DistributedBoardbotBossAI import DistributedBoardbotBossAI

            #         boss = None
            #         for do in simbase.air.doId2do.values():
            #             if isinstance(do, DistributedBoardbotBossAI):
            #                 for s in self.battle.activeSuits:
            #                     if s in do.activeSuits:
            #                         boss = do
            #                         break
            #                 for s in self.battle.activeSuits:
            #                     if s in do.activeSuits:
            #                         if s.dna.name == 'liquid':
            #                             if len(self.battle.activeSuits) < 6 and not self.suitHasCondition(suitId, 'alreadyCogSpawn'):
            #                                 if self.suitHasCondition(suitId, 'desperation'):
            #                                     boss.appendSuitsToBattle(boss.battleNumber, 'bdlitDesperation')
            #                                     boss.appendSuitsToBattle(boss.battleNumber, 'bdlitDesperation')
            #                                 else:
            #                                     boss.appendSuitsToBattle(boss.battleNumber, 'bdlit')
            # if self.battle.activeSuits[i].dna.name == 'dking':
            #     if x % 2 == 0 and self.battle.activeSuits[i].currHP > 0:
            #         from toontown.suit.DistributedBoardbotBossAI import DistributedBoardbotBossAI

            #         boss = None
            #         for do in simbase.air.doId2do.values():
            #             if isinstance(do, DistributedBoardbotBossAI):
            #                 for s in self.battle.activeSuits:
            #                     if s in do.activeSuits:
            #                         boss = do
            #                         break
            #                 for s in self.battle.activeSuits:
            #                     if s in do.activeSuits:
            #                         if s.dna.name == 'dking':
            #                             maxSuits = 6

            #                             aliveCount = len(self.battle.activeSuits) - self.deadSuits
            #                             spawnAmount = min(3, maxSuits - aliveCount)

            #                             if spawnAmount > 0 and not self.suitHasCondition(suitId, 'alreadyCogSpawn'):
            #                                 for i in xrange(spawnAmount):
            #                                     if self.suitHasCondition(suitId, 'desperation'):
            #                                         boss.appendSuitsToBattle(boss.battleNumber, 'bdlitDesperation')
            #                                     else:
            #                                         boss.appendSuitsToBattle(boss.battleNumber, 'bdlit')
            SPAWNER_DNAS_BOARD = (
                'dking',
                'rkeeper',
                'cdirector',
                'dking',
            )

            currentSuit = self.battle.activeSuits[i]

            if currentSuit.dna.name in SPAWNER_DNAS_BOARD:
                if x % 2 == 0 and currentSuit.currHP > 0:
                    # Find all living Cogs that are capable of spawning.
                    eligibleSpawners = [
                        suit for suit in self.battle.activeSuits
                        if suit.currHP > 0 and suit.dna.name in SPAWNER_DNAS_BOARD
                    ]

                    if eligibleSpawners:
                        # The oldest/lowest-doId Cog becomes the only spawner.
                        designatedSpawner = min(
                            eligibleSpawners,
                            key=lambda suit: suit.doId
                        )

                        # Only the designated Cog is allowed to continue.
                        if currentSuit.doId == designatedSpawner.doId:
                            from toontown.suit.DistributedBoardbotBossAI import (
                                DistributedBoardbotBossAI
                            )

                            boss = None

                            # Find the boss controlling this battle.
                            for do in simbase.air.doId2do.values():
                                if not isinstance(do, DistributedBoardbotBossAI):
                                    continue

                                for suit in self.battle.activeSuits:
                                    if suit in do.activeSuits:
                                        boss = do
                                        break

                                if boss:
                                    break

                            if boss:
                                maxSuits = 6
                                maxSpawnPerTurn = 3

                                # Count only living Cogs.
                                aliveCount = sum(
                                    1 for suit in self.battle.activeSuits
                                    if suit.currHP > 0
                                )

                                availableSlots = maxSuits - aliveCount

                                # Never summon more than three at once.
                                spawnAmount = min(
                                    maxSpawnPerTurn,
                                    availableSlots
                                )

                                spawnerId = designatedSpawner.doId

                                if (
                                        spawnAmount > 0 and
                                        not self.suitHasCondition(
                                            spawnerId,
                                            'alreadyCogSpawn'
                                        )):

                                    # Mark the designated Cog immediately so this block
                                    # cannot run again during the same spawning window.
                                    self.setSuitCondition(
                                        spawnerId,
                                        'alreadyCogSpawn',
                                        1,
                                        1,
                                        'setBoth'
                                    )

                                    if self.suitHasCondition(
                                            spawnerId,
                                            'desperation'):
                                        spawnCode = 'bdlitDesperation'
                                    else:
                                        spawnCode = 'bdlit'

                                    for spawnIndex in xrange(spawnAmount):
                                        boss.appendSuitsToBattle(
                                            boss.battleNumber,
                                            spawnCode
                                        )
            SPAWNER_DNAS_BOSS = (
                                        'ambass',
                                        'phouse',
                                        'wtapper',
                                        'bkeeper',
                                    )
                        
            currentSuit = self.battle.activeSuits[i]

            if currentSuit.dna.name in SPAWNER_DNAS_BOSS:
                if x % 2 == 0 and currentSuit.currHP > 0:
                    # Find all living Cogs that are capable of spawning.
                    eligibleSpawners = [
                        suit for suit in self.battle.activeSuits
                        if suit.currHP > 0 and suit.dna.name in SPAWNER_DNAS_BOSS
                    ]

                    if eligibleSpawners:
                        # The oldest/lowest-doId Cog becomes the only spawner.
                        designatedSpawner = min(
                            eligibleSpawners,
                            key=lambda suit: suit.doId
                        )

                        # Only the designated Cog is allowed to continue.
                        if currentSuit.doId == designatedSpawner.doId:
                            from toontown.suit.DistributedDirectorsAI import (
                                DistributedDirectorsAI
                            )

                            boss = None

                            # Find the boss controlling this battle.
                            for do in simbase.air.doId2do.values():
                                if not isinstance(do, DistributedDirectorsAI):
                                    continue

                                for suit in self.battle.activeSuits:
                                    if suit in do.activeSuits:
                                        boss = do
                                        break

                                if boss:
                                    break

                            if boss:
                                maxSuits = 6
                                maxSpawnPerTurn = 3

                                # Count only living Cogs.
                                aliveCount = sum(
                                    1 for suit in self.battle.activeSuits
                                    if suit.currHP > 0
                                )

                                availableSlots = maxSuits - aliveCount

                                # Never summon more than three at once.
                                spawnAmount = min(
                                    maxSpawnPerTurn,
                                    availableSlots
                                )

                                spawnerId = designatedSpawner.doId

                                if (
                                        spawnAmount > 0 and
                                        not self.suitHasCondition(
                                            spawnerId,
                                            'alreadyCogSpawn'
                                        )):

                                    # Mark the designated Cog immediately so this block
                                    # cannot run again during the same spawning window.
                                    self.setSuitCondition(
                                        spawnerId,
                                        'alreadyCogSpawn',
                                        1,
                                        1,
                                        'setBoth'
                                    )

                                    if self.suitHasCondition(
                                            spawnerId,
                                            'desperation'):
                                        spawnCode = 'ambDesperation'
                                    else:
                                        spawnCode = 'amb'

                                    for spawnIndex in xrange(spawnAmount):
                                        boss.appendSuitsToBattle(
                                            boss.battleNumber,
                                            spawnCode
                                        )
            SPAWNER_DNAS_SELL = (
                            'ubuster',
                            'hustle',
                            'radiog',
                            'safesupervis',
                        )
            
            currentSuit = self.battle.activeSuits[i]

            if currentSuit.dna.name in SPAWNER_DNAS_SELL:
                if x % 2 == 0 and currentSuit.currHP > 0:
                    # Find all living Cogs that are capable of spawning.
                    eligibleSpawners = [
                        suit for suit in self.battle.activeSuits
                        if suit.currHP > 0 and suit.dna.name in SPAWNER_DNAS_SELL
                    ]

                    if eligibleSpawners:
                        # The oldest/lowest-doId Cog becomes the only spawner.
                        designatedSpawner = min(
                            eligibleSpawners,
                            key=lambda suit: suit.doId
                        )

                        # Only the designated Cog is allowed to continue.
                        if currentSuit.doId == designatedSpawner.doId:
                            from toontown.suit.DistributedSellbotBossMiniAI import (
                                DistributedSellbotBossMiniAI
                            )

                            boss = None

                            # Find the boss controlling this battle.
                            for do in simbase.air.doId2do.values():
                                if not isinstance(do, DistributedSellbotBossMiniAI):
                                    continue

                                for suit in self.battle.activeSuits:
                                    if suit in do.activeSuits:
                                        boss = do
                                        break

                                if boss:
                                    break

                            if boss:
                                maxSuits = 6
                                maxSpawnPerTurn = 3

                                # Count only living Cogs.
                                aliveCount = sum(
                                    1 for suit in self.battle.activeSuits
                                    if suit.currHP > 0
                                )

                                availableSlots = maxSuits - aliveCount

                                # Never summon more than three at once.
                                spawnAmount = min(
                                    maxSpawnPerTurn,
                                    availableSlots
                                )

                                spawnerId = designatedSpawner.doId

                                if (
                                        spawnAmount > 0 and
                                        not self.suitHasCondition(
                                            spawnerId,
                                            'alreadyCogSpawn'
                                        )):

                                    # Mark the designated Cog immediately so this block
                                    # cannot run again during the same spawning window.
                                    self.setSuitCondition(
                                        spawnerId,
                                        'alreadyCogSpawn',
                                        1,
                                        1,
                                        'setBoth'
                                    )

                                    if self.suitHasCondition(
                                            spawnerId,
                                            'desperation'):
                                        spawnCode = 'presDesperation'
                                    else:
                                        spawnCode = 'pres'

                                    for spawnIndex in xrange(spawnAmount):
                                        boss.appendSuitsToBattle(
                                            boss.battleNumber,
                                            spawnCode
                                        )
            SPAWNER_DNAS_LAW = (
                            'stenog',
                            'lgator',
                            'sgoat',
                            'caseman',
                        )
            
            currentSuit = self.battle.activeSuits[i]

            if currentSuit.dna.name in SPAWNER_DNAS_LAW:
                if x % 2 == 0 and currentSuit.currHP > 0:
                    # Find all living Cogs that are capable of spawning.
                    eligibleSpawners = [
                        suit for suit in self.battle.activeSuits
                        if suit.currHP > 0 and suit.dna.name in SPAWNER_DNAS_LAW
                    ]

                    if eligibleSpawners:
                        # The oldest/lowest-doId Cog becomes the only spawner.
                        designatedSpawner = min(
                            eligibleSpawners,
                            key=lambda suit: suit.doId
                        )

                        # Only the designated Cog is allowed to continue.
                        if currentSuit.doId == designatedSpawner.doId:
                            from toontown.suit.DistributedLawbotBossAI import (
                                DistributedLawbotBossAI
                            )

                            boss = None

                            # Find the boss controlling this battle.
                            for do in simbase.air.doId2do.values():
                                if not isinstance(do, DistributedLawbotBossAI):
                                    continue

                                for suit in self.battle.activeSuits:
                                    if suit in do.activeSuits:
                                        boss = do
                                        break

                                if boss:
                                    break

                            if boss:
                                maxSuits = 6
                                maxSpawnPerTurn = 3

                                # Count only living Cogs.
                                aliveCount = sum(
                                    1 for suit in self.battle.activeSuits
                                    if suit.currHP > 0
                                )

                                availableSlots = maxSuits - aliveCount

                                # Never summon more than three at once.
                                spawnAmount = min(
                                    maxSpawnPerTurn,
                                    availableSlots
                                )

                                spawnerId = designatedSpawner.doId

                                if (
                                        spawnAmount > 0 and
                                        not self.suitHasCondition(
                                            spawnerId,
                                            'alreadyCogSpawn'
                                        )):

                                    # Mark the designated Cog immediately so this block
                                    # cannot run again during the same spawning window.
                                    self.setSuitCondition(
                                        spawnerId,
                                        'alreadyCogSpawn',
                                        1,
                                        1,
                                        'setBoth'
                                    )

                                    if self.suitHasCondition(
                                            spawnerId,
                                            'desperation'):
                                        spawnCode = 'litDesperation'
                                    else:
                                        spawnCode = 'lit'

                                    for spawnIndex in xrange(spawnAmount):
                                        boss.appendSuitsToBattle(
                                            boss.battleNumber,
                                            spawnCode
                                        )
                #if self.battle.activeSuits[i].dna.name == 'racket': #racketeer
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
            SPAWNER_DNAS_REDD = (
                                       'redd'
                                    )
                        
            currentSuit = self.battle.activeSuits[i]

            if currentSuit.dna.name in SPAWNER_DNAS_REDD:
                if x % 2 == 0 and currentSuit.currHP > 0:
                    # Find all living Cogs that are capable of spawning.
                    eligibleSpawners = [
                        suit for suit in self.battle.activeSuits
                        if suit.currHP > 0 and suit.dna.name in SPAWNER_DNAS_REDD
                    ]

                    if eligibleSpawners:
                        # The oldest/lowest-doId Cog becomes the only spawner.
                        designatedSpawner = min(
                            eligibleSpawners,
                            key=lambda suit: suit.doId
                        )

                        # Only the designated Cog is allowed to continue.
                        if currentSuit.doId == designatedSpawner.doId:
                            from toontown.suit.DistributedLawbotBossAI import (
                                DistributedLawbotBossAI
                            )

                            boss = None

                            # Find the boss controlling this battle.
                            for do in simbase.air.doId2do.values():
                                if not isinstance(do, DistributedLawbotBossAI):
                                    continue

                                for suit in self.battle.activeSuits:
                                    if suit in do.activeSuits:
                                        boss = do
                                        break

                                if boss:
                                    break

                            if boss:
                                maxSuits = 6
                                maxSpawnPerTurn = 3

                                # Count only living Cogs.
                                aliveCount = sum(
                                    1 for suit in self.battle.activeSuits
                                    if suit.currHP > 0
                                )

                                availableSlots = maxSuits - aliveCount

                                # Never summon more than three at once.
                                spawnAmount = min(
                                    maxSpawnPerTurn,
                                    availableSlots
                                )

                                spawnerId = designatedSpawner.doId

                                if (
                                        spawnAmount > 0 and
                                        not self.suitHasCondition(
                                            spawnerId,
                                            'alreadyCogSpawn'
                                        )):

                                    # Mark the designated Cog immediately so this block
                                    # cannot run again during the same spawning window.
                                    self.setSuitCondition(
                                        spawnerId,
                                        'alreadyCogSpawn',
                                        1,
                                        1,
                                        'setBoth'
                                    )

                                    spawnCode = 'lit2'

                                    for spawnIndex in xrange(spawnAmount):
                                        boss.appendSuitsToBattle(
                                            boss.battleNumber,
                                            spawnCode
                                        )
            SPAWNER_DNAS_PACE = (
                                       'psetter'
                                    )
                        
            currentSuit = self.battle.activeSuits[i]

            if currentSuit.dna.name in SPAWNER_DNAS_PACE:
                if currentSuit.currHP > 0:
                    # Find all living Cogs that are capable of spawning.
                    eligibleSpawners = [
                        suit for suit in self.battle.activeSuits
                        if suit.currHP > 0 and suit.dna.name in SPAWNER_DNAS_PACE
                    ]

                    if eligibleSpawners:
                        # The oldest/lowest-doId Pacesetter becomes the only spawner.
                        designatedSpawner = min(
                            eligibleSpawners,
                            key=lambda suit: suit.doId
                        )

                        # Only the designated Pacesetter is allowed to continue.
                        if currentSuit.doId == designatedSpawner.doId:
                            from toontown.suit.DistributedPacesetterBossAI import (
                                DistributedPacesetterBossAI
                            )

                            boss = None

                            # Find the boss controlling this battle.
                            for do in simbase.air.doId2do.values():
                                if not isinstance(do, DistributedPacesetterBossAI):
                                    continue

                                for suit in self.battle.activeSuits:
                                    if suit in do.activeSuits:
                                        boss = do
                                        break

                                if boss:
                                    break

                            if boss:
                                spawnerId = designatedSpawner.doId

                                # Clash gates Pacesetter's natural reserves on whether
                                # his normal attack generation is active, not on HP.
                                # Altis represents the opening challenge with turn1 /
                                # turn2 plus openingChallengeCancelled.
                                openingChallengeCancelled = self.suitHasCondition(
                                    spawnerId,
                                    'openingChallengeCancelled'
                                )

                                # Detect the exact round that Early Overclocked is
                                # being queued.  This round must remain spawn-free;
                                # Clash's first post-challenge reserve wave is the
                                # following round.
                                earlyOverclockTriggeredThisRound = False
                                for suitAttack in self.battle.suitAttacks:
                                    if suitAttack[SUIT_ID_COL] != spawnerId:
                                        continue
                                    attackInfo = suitAttack[SUIT_ATK_COL]
                                    if (
                                            isinstance(attackInfo, dict) and
                                            attackInfo.get('name') ==
                                            'PacesetterEarlyOverclocked'):
                                        earlyOverclockTriggeredThisRound = True
                                        break

                                earlyOverclockActive = (
                                    self.suitHasCondition(spawnerId, 'overclocked') and
                                    self.suitHasCondition(spawnerId, 'turn1') and
                                    self.suitHasCondition(spawnerId, 'turn2')
                                )

                                normalFightActive = (
                                    openingChallengeCancelled or
                                    (
                                        earlyOverclockActive and
                                        not earlyOverclockTriggeredThisRound
                                    )
                                )

                                if normalFightActive:
                                    # Match Clash: only eligible normal-fight rounds
                                    # advance the natural-spawn cycle.  Challenge
                                    # Pass/timeout rounds do not consume spawn turns.
                                    spawnCycleRound = (
                                        self._pacesetterSpawnCycleRounds.get(
                                            spawnerId,
                                            0
                                        ) + 1
                                    )
                                    self._pacesetterSpawnCycleRounds[spawnerId] = (
                                        spawnCycleRound
                                    )

                                    # Clash spawns on odd eligible cycles: 1, 3, 5...
                                    spawnThisRound = (spawnCycleRound % 2 == 1)

                                    if spawnThisRound:
                                        maxSuits = 7
                                        maxSpawnPerTurn = 3

                                        # Count only living Cogs.
                                        aliveCount = sum(
                                            1 for suit in self.battle.activeSuits
                                            if suit.currHP > 0
                                        )

                                        availableSlots = maxSuits - aliveCount

                                        # Never summon more than three at once.
                                        spawnAmount = min(
                                            maxSpawnPerTurn,
                                            availableSlots
                                        )

                                        if (
                                                spawnAmount > 0 and
                                                not self.suitHasCondition(
                                                    spawnerId,
                                                    'alreadyCogSpawn'
                                                )):

                                            # Prevent a duplicate call in the same
                                            # spawning window.
                                            self.setSuitCondition(
                                                spawnerId,
                                                'alreadyCogSpawn',
                                                1,
                                                1,
                                                'setBoth'
                                            )

                                            spawnCode = 'paceGrunts'

                                            for spawnIndex in xrange(spawnAmount):
                                                boss.appendSuitsToBattle(
                                                    boss.battleNumber,
                                                    spawnCode
                                                )
            # if self.battle.activeSuits[i].dna.name == 'redd':
            #     currentBossHealth = -1
            #     for s in self.battle.suits:
            #         if s.dna.name == 'wsi':
            #             currentBossHealth = s.currHP
            #     if currentBossHealth == -1:
            #         from toontown.suit.DistributedLawbotBossAI import DistributedLawbotBossAI

            #         boss = None
            #         for do in simbase.air.doId2do.values():
            #             if isinstance(do, DistributedLawbotBossAI):
            #                 for s in self.battle.activeSuits:
            #                     if s in do.activeSuits:
            #                         boss = do
            #                         break
            #                 for s in self.battle.activeSuits:
            #                     if s in do.activeSuits:
            #                         if s.dna.name == 'redd':
            #                             maxSuits = 7
    
            #                             aliveCount = len(self.battle.activeSuits) - self.deadSuits
            #                             spawnAmount = maxSuits - aliveCount
    
            #                             if spawnAmount > 0:
            #                                 for i in xrange(spawnAmount):
            #                                     boss.appendSuitsToBattle(boss.battleNumber, 'lit2')
    
            #                             break
