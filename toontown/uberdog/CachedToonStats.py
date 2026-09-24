from toontown.toon.DistributedSettingsAI import DistributedSettingsAI
from toontown.utils.AstronStruct import AstronStruct

from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from toontown.toon.DistributedToonAI import DistributedToonAI


class CachedToonStats(AstronStruct):
    """
    A data class for various Toon stats.
    These are cached on the UD for all online users.
    """

    def __init__(self, avId: int, level: int, name: str, zoneId: int, districtId: int, hp: int,
                 gagLevels: List[int], gagPrestiges: List[int], settings: DistributedSettingsAI):
        self.avId = avId
        self.level = level
        self.name = name
        self.zoneId = zoneId
        self.districtId = districtId
        self.hp = hp
        self.gagLevels = gagLevels
        self.gagPrestiges = gagPrestiges
        self.settings = settings

    def __repr__(self):
        return f'{self.getName()} (TT-{self.getAvId()})'

    def toStruct(self) -> list:
        return [self.avId, self.level, self.name, self.zoneId, self.districtId, self.hp,
                self.gagLevels, self.gagPrestiges, self.settings.toStruct()]

    @classmethod
    def fromStruct(cls, struct):
        avId, level, name, zoneId, districtId, hp, gagLevels, gagPrestiges, settings = struct
        settings = DistributedSettingsAI.fromStruct(settings)
        return CachedToonStats(avId, level, name, zoneId, districtId, hp, gagLevels, gagPrestiges, settings)

    """
    "bro main why dont you just access by attributes" Despair, Young One. Despair
    """

    def getAvId(self) -> int:
        return self.avId

    def getLevel(self) -> int:
        return self.level

    def getName(self) -> str:
        return self.name

    def getZoneId(self) -> int:
        return self.zoneId

    def getDistrictId(self) -> int:
        return self.districtId

    def getHp(self) -> int:
        return self.hp

    def getGagLevels(self) -> List[int]:
        return self.gagLevels

    def getGagPrestiges(self) -> List[int]:
        return self.gagPrestiges

    def getSettings(self) -> DistributedSettingsAI:
        return self.settings

    """
    Other building methods
    """

    @classmethod
    def fromToon(cls, toon):
        """:type toon: DistributedToonAI"""
        return cls(
            avId=toon.doId,
            level=toon.toonLevel,
            name=toon.getName(),
            zoneId=toon.zoneId,
            districtId=toon.air.districtId,
            hp=toon.maxHp,
            gagLevels=toon.getGagLevels(),
            gagPrestiges=toon.getPrestigeLevels(),
            settings=toon.getSettings(),
        )
