from __future__ import absolute_import
from toontown.classicchars import DistributedPlutoAI
from toontown.hood import HoodAI
from toontown.hood import ZoneUtil
from toontown.building import DistributedBuildingMgrAI
from toontown.building import CountErfitBuildingMgrAI
from toontown.building import DistributedCountErfitElevatorAI
from toontown.safezone import DistributedTrolleyAI
from toontown.toonbase import ToontownGlobals
from toontown.ai import DistributedPolarPlaceEffectMgrAI
from toontown.ai import DistributedTrickOrTreatTargetAI
from toontown.ai import DistributedWinterCarolingTargetAI

class BRHoodAI(HoodAI.HoodAI):
    
    def __init__(self, air):
        HoodAI.HoodAI.__init__(self, air,
                               ToontownGlobals.TheBrrrgh,
                               ToontownGlobals.TheBrrrgh)

        self.trolley = None
        self.classicChar = None
        self.countErfitElevator = None

        self.startup()

    def startup(self):
        HoodAI.HoodAI.startup(self)

        if simbase.config.GetBool('want-minigames', True):
            self.createTrolley()
        if simbase.config.GetBool('want-classic-chars', True):
            if simbase.config.GetBool('want-pluto', True):
                self.createClassicChar()

        self.PolarPlaceEffectManager = DistributedPolarPlaceEffectMgrAI.DistributedPolarPlaceEffectMgrAI(self.air)
        self.PolarPlaceEffectManager.generateWithRequired(3821)
        self.createCountErfitElevator()
        
        if simbase.air.wantHalloween:
            self.TrickOrTreatTargetManager = DistributedTrickOrTreatTargetAI.DistributedTrickOrTreatTargetAI(self.air)
            self.TrickOrTreatTargetManager.generateWithRequired(3707)
        
        if simbase.air.wantChristmas:
            self.WinterCarolingTargetManager = DistributedWinterCarolingTargetAI.DistributedWinterCarolingTargetAI(self.air)
            self.WinterCarolingTargetManager.generateWithRequired(3828)

    def createBuildingManagers(self):
        for zoneId in self.getZoneTable():
            dnaStore = self.air.dnaStoreMap[zoneId]
            zoneId = ZoneUtil.getTrueZoneId(zoneId, self.zoneId)
            if zoneId == ToontownGlobals.PolarPlace:
                buildingManager = CountErfitBuildingMgrAI.CountErfitBuildingMgrAI(
                    self.air, zoneId, dnaStore, self.air.trophyMgr)
            else:
                buildingManager = DistributedBuildingMgrAI.DistributedBuildingMgrAI(
                    self.air, zoneId, dnaStore, self.air.trophyMgr)
            self.buildingManagers.append(buildingManager)
            self.air.buildingManagers[zoneId] = buildingManager

    def createCountErfitElevator(self):
        self.countErfitElevator = DistributedCountErfitElevatorAI.DistributedCountErfitElevatorAI(
            self.air,
            ToontownGlobals.CountErfitBattle
        )
        self.countErfitElevator.generateWithRequired(3328)

    def createTrolley(self):
        self.trolley = DistributedTrolleyAI.DistributedTrolleyAI(self.air)
        self.trolley.generateWithRequired(self.zoneId)
        self.trolley.start()

    def createClassicChar(self):
        self.classicChar = DistributedPlutoAI.DistributedPlutoAI(self.air)
        self.classicChar.generateWithRequired(self.zoneId)
        self.classicChar.start()
