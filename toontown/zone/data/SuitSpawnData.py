from strenum import StrEnum
from typing import Dict, Union, List
import random

from toontown.suit import SuitDNA
from toontown.battle.SuitBattleGlobals import ALWAYS_EXECUTIVES, ALWAYS_SKELECOGS, COG_MINIBOSSES


SpawnRng = random.Random()


class SuitSpawnID(StrEnum):
    Test = 'test_spawn'
    TestShuffler = 'test_shuffler'


class SpawnDef:
    """
    Defines an individual spawn or set of spawns within a Spawn Container.
    For example, one spawn definition could spawn flunkies level 1-2 in an area.
    """

    def __init__(self,
                 suitType: Union[List, str],
                 suitLevel: Union[List, int],
                 executiveChance: float = 0.25,
                 skelecogChance: float = 0.0,
                 weight: int = 100):
        if type(suitType) is str:
            suitType = [suitType]
        self.suitType = suitType
        if type(suitLevel) is int:
            suitLevel = [suitLevel]
        self.suitLevel = suitLevel
        self.executiveChance = executiveChance
        self.skelecogChance = skelecogChance
        self.weight = weight

    def getSuitType(self) -> List:
        return self.suitType

    def getRandomSuitType(self) -> str:
        return SpawnRng.choice(self.getSuitType())

    def getSuitLevel(self) -> List:
        return self.suitLevel

    def getRandomSuitLevel(self) -> int:
        return SpawnRng.choice(self.getSuitLevel())

    def getExecutiveChance(self) -> float:
        return self.executiveChance

    def getSkelecogChance(self) -> float:
        return self.skelecogChance

    def getSpawnWeight(self) -> float:
        return self.weight


class SpawnContainer:
    """
    Holds a collection of SpawnDefs, which overall will
    determine the spawn rates of enemies in this area of the world.
    """
    def __init__(self, *spawnDefs: SpawnDef):
        self.spawnDefs = list(spawnDefs)

    def getSpawnDefs(self) -> List[SpawnDef]:
        return self.spawnDefs

    def getSpawnWeights(self) -> List[float]:
        return [spawnDef.getSpawnWeight() for spawnDef in self.getSpawnDefs()]

    def chooseRandomDefinition(self) -> SpawnDef:
        return SpawnRng.choices(self.getSpawnDefs(), self.getSpawnWeights())[0]

    def getRandomSuitDict(self) -> dict:
        spawnDef = self.chooseRandomDefinition()
        suitType = spawnDef.getRandomSuitType()
        isElite = True if suitType in ALWAYS_EXECUTIVES or suitType in COG_MINIBOSSES else SpawnRng.random() <= spawnDef.getExecutiveChance()
        isSkeleton = True if suitType in ALWAYS_SKELECOGS else SpawnRng.random() <= spawnDef.getSkelecogChance()
        suitDict = {
            'type': suitType,
            'level': spawnDef.getRandomSuitLevel(),
            'dept': SuitDNA.getSuitDept(suitType),
            'elite': isElite,
            'skeleton': isSkeleton,
            'virtual': False,
        }
        return suitDict


SuitSpawnRegistry: Dict[StrEnum, SpawnContainer] = {
    SuitSpawnID.Test: SpawnContainer(
        SpawnDef(suitType='f', suitLevel=[1, 2, 3, 4, 5], executiveChance=0.25),
        SpawnDef(suitType='cc', suitLevel=[1, 2, 3], executiveChance=0.25)
    ),
    SuitSpawnID.TestShuffler: SpawnContainer(
        SpawnDef(suitType='duckshfl', suitLevel=5)
    ),
}
