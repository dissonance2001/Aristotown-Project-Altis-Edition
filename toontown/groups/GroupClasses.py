from toontown.gui.toon.ToonHeadData import ToonHeadData
from toontown.utils.AstronStruct import AstronStruct


class GroupAvatar(AstronStruct):
    """
    Information about an avatar in a group.
    """

    def __init__(self, avId: int, name: str, status: int, reserved: bool):
        self.avId = avId
        self.name = name
        self.status = status
        self.reserved = reserved

    def getName(self):
        return self.name

    @property
    def doId(self):
        return self.avId

    def toStruct(self) -> list:
        return [self.avId, self.name, self.status, self.reserved]


class GroupAvatarUDToon(AstronStruct):
    """
    UD-facing information for a Group Avatar.
    """

    def __init__(self, avId: int, name: str, zoneId: int, districtId: int,
                 hp: int, gagLevels: list, gagPrestiges: list,
                 toonLevel: int, toonHeadData: ToonHeadData,
                 currHp: int, xp: int):
        self.avId = avId
        self.name = name
        self.zoneId = zoneId
        self.districtId = districtId
        self.hp = hp
        self.gagLevels = gagLevels
        self.gagPrestiges = gagPrestiges
        self.toonLevel = toonLevel
        self.toonHeadData = toonHeadData
        self.currHp = currHp
        self.xp = xp

    def toStruct(self) -> list:
        return [self.avId, self.name, self.zoneId, self.districtId, self.hp, self.gagLevels, self.gagPrestiges,
                self.toonLevel, self.toonHeadData.toStruct(), self.currHp, self.xp]

    @classmethod
    def fromStruct(cls, struct):
        avId, name, zoneId, districtId, hp, gagLevels, gagPrestiges, toonLevel, toonHeadData, currHp, xp = struct
        toonHeadData = ToonHeadData.fromStruct(toonHeadData)
        return cls(avId, name, zoneId, districtId, hp, gagLevels, gagPrestiges, toonLevel, toonHeadData, currHp, xp)

    def transformIntoGroupAv(self, status: int = 0, reserved: bool = False):
        return GroupAvatar(avId=self.avId, name=self.name, status=status, reserved=reserved)

    def getHp(self):
        return self.hp
