from __future__ import absolute_import
from toontown.building import DistributedVPElevatorAI
from toontown.building import DistributedMultislackerElevatorAI
from toontown.building import FADoorCodes
from toontown.building.DistributedBoardingPartyAI import DistributedBoardingPartyAI
from toontown.coghq.DistributedFactoryElevatorExtAI import DistributedFactoryElevatorExtAI
from toontown.hood import CogHQAI
from toontown.suit import DistributedSellbotBossAI
from toontown.suit import DistributedSellbotBossMiniAI
from toontown.suit import DistributedSuitPlannerAI
from toontown.toonbase import ToontownGlobals
from six.moves import range

class SellbotHQAI(CogHQAI.CogHQAI):
    
    def __init__(self, air):
        CogHQAI.CogHQAI.__init__(
            self, air, ToontownGlobals.SellbotHQ, ToontownGlobals.SellbotLobby, ToontownGlobals.SellbotMultislackerLobby,
            FADoorCodes.SB_DISGUISE_INCOMPLETE,
            FADoorCodes.SB_WASHROOM_MISSING,
            DistributedVPElevatorAI.DistributedVPElevatorAI,
            DistributedSellbotBossMiniAI.DistributedSellbotBossMiniAI,
            DistributedMultislackerElevatorAI.DistributedMultislackerElevatorAI,
            DistributedSellbotBossAI.DistributedSellbotBossAI,
            ToontownGlobals.ZoneIdrVP)

        self.factoryElevators = []
        self.factoryBoardingParty = None
        self.suitPlanners = []

        self.startup()

    def startup(self):
        CogHQAI.CogHQAI.startup(self)

        # Sellbot HQ has not just one, but four lobby doors:
        self.cogHQDoors = [self.extDoor]
        for i in range(3):  # CogHQAI already created one of the doors for us.
            extDoor = self.makeCogHQDoor(self.lobbyZoneId, 0, i + 1, self.lobbyFADoorCode, boss=1)
            self.cogHQDoors.append(extDoor)

        # extDoor2 = self.makeCogHQDoor(ToontownGlobals.SellbotMultislackerLobby, 0, 2, self.lobbyFADoorCode, boss=1)
        # self.cogHQDoors.append(extDoor2)
        # extDoor3 = self.makeCogHQDoor(ToontownGlobals.SellbotMultislackerLobby, 0, 3, self.lobbyFADoorCode, boss=1)
        # self.cogHQDoors.append(extDoor3)
        self.createFactoryElevators()
        # if simbase.config.GetBool('want-boarding-groups', True):
        #     self.createFactoryBoardingParty()
        if simbase.config.GetBool('want-suit-planners', True):
            self.createSuitPlanners()
        # self.hardmodeDoor = self.makeHardCogHQDoor(
        #         ToontownGlobals.SellbotMultislackerLobby,
        #         0,
        #         3,
        #         self.hardmodeFADoorCode
        #     )
        # Our suit planner needs the Cog HQ doors as well:
        for sp in self.suitPlanners:
            if sp.zoneId == self.zoneId:
                sp.cogHQDoors = self.cogHQDoors

    def createFactoryElevators(self):
        # We only have two factory elevators: the front, and side elevators.
        for i in range(2):
            factoryElevator = DistributedFactoryElevatorExtAI(
                self.air, self.air.factoryMgr, ToontownGlobals.SellbotFactoryInt, i)
            factoryElevator.generateWithRequired(ToontownGlobals.SellbotFactoryExt)
            self.factoryElevators.append(factoryElevator)

    def createFactoryBoardingParty(self):
        factoryIdList = []
        for factoryElevator in self.factoryElevators:
            factoryIdList.append(factoryElevator.doId)
        self.factoryBoardingParty = DistributedBoardingPartyAI(self.air, factoryIdList, 4)
        self.factoryBoardingParty.generateWithRequired(ToontownGlobals.SellbotFactoryExt)

    def createSuitPlanners(self):
        suitPlanner = DistributedSuitPlannerAI.DistributedSuitPlannerAI(self.air, self.zoneId)
        suitPlanner.generateWithRequired(self.zoneId)
        suitPlanner.d_setZoneId(self.zoneId)
        suitPlanner.initTasks()
        self.suitPlanners.append(suitPlanner)
        self.air.suitPlanners[self.zoneId] = suitPlanner

        suitPlanner = DistributedSuitPlannerAI.DistributedSuitPlannerAI(self.air, ToontownGlobals.SellbotFactoryExt)
        suitPlanner.generateWithRequired(ToontownGlobals.SellbotFactoryExt)
        suitPlanner.d_setZoneId(ToontownGlobals.SellbotFactoryExt)
        suitPlanner.initTasks()
        self.suitPlanners.append(suitPlanner)
        self.air.suitPlanners[ToontownGlobals.SellbotFactoryExt] = suitPlanner
