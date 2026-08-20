from __future__ import absolute_import
from toontown.classicchars import DistributedMinnieAI
from toontown.hood import HoodAI
from toontown.safezone import DistributedTrolleyAI
from toontown.safezone import TreasureGlobals
from toontown.toonbase import ToontownGlobals
from toontown.ai import DistributedTrickOrTreatTargetAI
from toontown.ai import DistributedWinterCarolingTargetAI


ClashMMTreasurePositions = [
    (112.5, -39, 4.1),
    (114, -4, 4.15),
    (112, -22, 2.8),
    (108, -74, -4.5),
    (110, -65, -4.5),
    (102, 23.5, -4.5),
    (60, -115, 6.5),
    (-0.194, -111.486, 6.5),
    (-64, -77, 6.5),
    (-77, -44, 6.5),
    (-72, 6, 6.5),
    (44, 76, 6.5),
    (136, -96, -13.5),
    (85, -6.7, -13.5),
    (60, -95, -14.5),
    (72, 60, -13.5),
    (-55, -23, -14.5),
    (-31, 37, -14.5),
    (-24, -75, -14.5),
]


class MMHoodAI(HoodAI.HoodAI):

    def __init__(self, air):
        HoodAI.HoodAI.__init__(
            self,
            air,
            ToontownGlobals.MinniesMelodyland,
            ToontownGlobals.MinniesMelodyland,
        )

        self.trolley = None
        self.classicChar = None

        self.startup()

    def startup(self):
        self.applyClashTreasurePositions()
        HoodAI.HoodAI.startup(self)

        if simbase.config.GetBool('want-minigames', True):
            self.createTrolley()

        if simbase.config.GetBool('want-classic-chars', True):
            if simbase.config.GetBool('want-minnie', True):
                self.createClassicChar()

        if simbase.air.wantHalloween:
            self.TrickOrTreatTargetManager = \
                DistributedTrickOrTreatTargetAI.DistributedTrickOrTreatTargetAI(
                    self.air
                )
            self.TrickOrTreatTargetManager.generateWithRequired(4835)

        if simbase.air.wantChristmas:
            self.WinterCarolingTargetManager = \
                DistributedWinterCarolingTargetAI.DistributedWinterCarolingTargetAI(
                    self.air
                )
            self.WinterCarolingTargetManager.generateWithRequired(4614)

    def applyClashTreasurePositions(self):
        zoneId = ToontownGlobals.MinniesMelodyland
        spawnData = TreasureGlobals.SafeZoneTreasureSpawns.get(zoneId)
        if spawnData is None or len(spawnData) < 3:
            return

        updatedSpawnData = list(spawnData)
        updatedSpawnData[2] = list(ClashMMTreasurePositions)
        TreasureGlobals.SafeZoneTreasureSpawns[zoneId] = tuple(updatedSpawnData)

    def createTrolley(self):
        self.trolley = DistributedTrolleyAI.DistributedTrolleyAI(self.air)
        self.trolley.generateWithRequired(self.zoneId)
        self.trolley.start()

    def createClassicChar(self):
        self.classicChar = DistributedMinnieAI.DistributedMinnieAI(self.air)
        self.classicChar.generateWithRequired(self.zoneId)
        self.classicChar.start()
