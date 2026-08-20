from __future__ import absolute_import
from toontown.building import DistributedCJElevatorAI
from toontown.building import DistributedCountErclaimElevatorAI
from toontown.building import FADoorCodes
from toontown.building.DistributedBoardingPartyAI import DistributedBoardingPartyAI
from toontown.coghq.DistributedLawOfficeElevatorExtAI import DistributedLawOfficeElevatorExtAI
from toontown.hood import CogHQAI
from toontown.suit import DistributedLawbotBossAI
from toontown.suit import DistributedCountErclaimBossAI
from toontown.suit import DistributedSuitPlannerAI
from toontown.toonbase import ToontownGlobals
from six.moves import range

class LawbotHQAI(CogHQAI.CogHQAI):

    def __init__(self, air):
        CogHQAI.CogHQAI.__init__(
            self, air, ToontownGlobals.LawbotHQ, ToontownGlobals.LawbotLobby, ToontownGlobals.LawbotLounge,
            FADoorCodes.LB_DISGUISE_INCOMPLETE,
            FADoorCodes.LB_WASHROOM_MISSING,
             DistributedCountErclaimElevatorAI.DistributedCountErclaimElevatorAI,
            DistributedCountErclaimBossAI.DistributedCountErclaimBossAI,
            DistributedCJElevatorAI.DistributedCJElevatorAI,
            DistributedLawbotBossAI.DistributedLawbotBossAI,
            ToontownGlobals.ZoneIdrCLO)

        # Required for our plants NPCs.
        # NPCToons.createNpcsInZone(self.air, ToontownGlobals.LawbotHQ)
        # NPCToons.createNpcsInZone(self.air, ToontownGlobals.LawbotOfficeExt)
        # NPCToons.createNpcsInZone(self.air, ToontownGlobals.LawbotLounge)

        self.lawOfficeElevators = []
        self.suitPlanners = []

        self.startup()
    
    # def __init__(self, air):
    #     CogHQAI.CogHQAI.__init__(
    #         self, air, ToontownGlobals.LawbotHQ, ToontownGlobals.LawbotLobby,
    #         FADoorCodes.LB_DISGUISE_INCOMPLETE,
    #         DistributedCJElevatorAI.DistributedCJElevatorAI,
    #         DistributedLawbotBossAI.DistributedLawbotBossAI)

    #     self.lawOfficeElevators = []
    #     self.officeBoardingParty = None
    #     self.suitPlanners = []

    #     self.startup()

    def startup(self):
        CogHQAI.CogHQAI.startup(self)

        self.createLawOfficeElevators()
        self.makeCogHQDoor(ToontownGlobals.LawbotOfficeExt, 0, 0)
        # if simbase.config.GetBool('want-boarding-groups', True):
        #     self.createOfficeBoardingParty()
        if simbase.config.GetBool('want-suit-planners', True):
            self.createSuitPlanners()

    def makeCogHQDoor(self, destinationZone, intDoorIndex, extDoorIndex, lock=0, boss=0):
        # For LBHQ, the lobby door index is 1, even though that index should be for the Lawbot office exterior door.
        if destinationZone == self.lobbyZoneId:
            extDoorIndex = 1
        elif destinationZone == ToontownGlobals.LawbotOfficeExt:
            # Lawbot DA Office / Lawfice Lobby
            extDoorIndex = 0

        return CogHQAI.CogHQAI.makeCogHQDoor(
            self, destinationZone, intDoorIndex, extDoorIndex, lock=lock, boss=boss
        )

    def createLawOfficeElevators(self):
        destZones = (
            ToontownGlobals.LawbotStageIntA,
            ToontownGlobals.LawbotStageIntB,
            ToontownGlobals.LawbotStageIntC,
            ToontownGlobals.LawbotStageIntD
        )
        mins = ToontownGlobals.FactoryLaffMinimums[2]
        for i in range(len(destZones)):
            lawOfficeElevator = DistributedLawOfficeElevatorExtAI(
                self.air, self.air.lawOfficeMgr, destZones[i], i,
                antiShuffle=0, minLaff=mins[i])
            lawOfficeElevator.generateWithRequired(
                ToontownGlobals.LawbotOfficeExt)
            self.lawOfficeElevators.append(lawOfficeElevator)

    def createOfficeBoardingParty(self):
        lawOfficeIdList = []
        for lawOfficeElevator in self.lawOfficeElevators:
            lawOfficeIdList.append(lawOfficeElevator.doId)
        self.officeBoardingParty = DistributedBoardingPartyAI(
            self.air, lawOfficeIdList, 4)
        self.officeBoardingParty.generateWithRequired(ToontownGlobals.LawbotOfficeExt)

    def createSuitPlanners(self):
        suitPlanner = DistributedSuitPlannerAI.DistributedSuitPlannerAI(self.air, self.zoneId)
        suitPlanner.generateWithRequired(self.zoneId)
        suitPlanner.d_setZoneId(self.zoneId)
        suitPlanner.initTasks()
        self.suitPlanners.append(suitPlanner)
        self.air.suitPlanners[self.zoneId] = suitPlanner

        # suitPlanner = DistributedSuitPlannerAI.DistributedSuitPlannerAI(self.air, ToontownGlobals.LawbotOfficeExt)
        # suitPlanner.generateWithRequired(ToontownGlobals.LawbotOfficeExt)
        # suitPlanner.d_setZoneId(ToontownGlobals.LawbotOfficeExt)
        # suitPlanner.initTasks()
        # self.suitPlanners.append(suitPlanner)
        # self.air.suitPlanners[ToontownGlobals.LawbotOfficeExt] = suitPlanner
