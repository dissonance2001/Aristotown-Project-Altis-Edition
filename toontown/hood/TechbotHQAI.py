from toontown.building import DistributedCMElevatorAI
from toontown.building import FADoorCodes
from toontown.building.DistributedBoardingPartyAI import DistributedBoardingPartyAI
from toontown.coghq.boardbothq.DistributedBoardOfficeElevatorExtAI import DistributedBoardOfficeElevatorExtAI
from toontown.hood import CogHQAI
from toontown.suit import DistributedBoardbotBossAI
from toontown.suit import DistributedSuitPlannerAI
from toontown.toonbase import ToontownGlobals

class TechbotHQAI(CogHQAI.CogHQAI):
    
    def __init__(self, air):
        CogHQAI.CogHQAI.__init__(
            self, air, ToontownGlobals.TechbotHQ, ToontownGlobals.TechbotLobby, None,
            FADoorCodes.BD_DISGUISE_INCOMPLETE,
            FADoorCodes.BD_WASHROOM_MISSING,
            DistributedCMElevatorAI.DistributedCMElevatorAI,
            DistributedBoardbotBossAI.DistributedBoardbotBossAI,
            DistributedCMElevatorAI.DistributedCMElevatorAI,
            DistributedBoardbotBossAI.DistributedBoardbotBossAI,
            ToontownGlobals.ZoneIdrChairman)

        self.boardofficeElevators = []
        self.boardofficeBoardingParty = None
        self.suitPlanners = []

        self.startup()

    def startup(self):
        CogHQAI.CogHQAI.startup(self)

        #self.createBoardOfficeElevators()
        self.makeCogHQDoor(ToontownGlobals.TechbotLobby, 0, 0)
        # if simbase.config.GetBool('want-boarding-groups', True):
        #     self.createBoardOfficeBoardingParty()
        # if simbase.config.GetBool('want-suit-planners', True):
        #     self.createSuitPlanners()
		
    def makeCogHQDoor(self, destinationZone, intDoorIndex, extDoorIndex, lock=0, boss=0):
        return CogHQAI.CogHQAI.makeCogHQDoor(
            self, destinationZone, intDoorIndex, extDoorIndex, lock=lock, boss=boss
        )

    def createBoardOfficeElevators(self):
        destZones = (
            ToontownGlobals.BoardOfficeIntA,
            ToontownGlobals.BoardOfficeIntB,
            ToontownGlobals.BoardOfficeIntC
        )
        mins = ToontownGlobals.FactoryLaffMinimums[1]
        for i in range(len(destZones)):
            boardofficeElevator = DistributedBoardOfficeElevatorExtAI(
                self.air, self.air.boardofficeMgr, destZones[i],
                antiShuffle=0, minLaff=mins[i])
            boardofficeElevator.generateWithRequired(ToontownGlobals.BoardbotOfficeLobby)
            self.boardofficeElevators.append(boardofficeElevator)


    def createBoardOfficeBoardingParty(self):
        boardofficeIdList = []
        for boardofficeElevator in self.boardofficeElevators:
            boardofficeIdList.append(boardofficeElevator.doId)
        self.boardofficeBoardingParty = DistributedBoardingPartyAI(self.air, boardofficeIdList, 4)
        self.boardofficeBoardingParty.generateWithRequired(self.zoneId)

    def createSuitPlanners(self):
        suitPlanner = DistributedSuitPlannerAI.DistributedSuitPlannerAI(self.air, self.zoneId)
        suitPlanner.generateWithRequired(self.zoneId)
        suitPlanner.d_setZoneId(self.zoneId)
        suitPlanner.initTasks()
        self.suitPlanners.append(suitPlanner)
        self.air.suitPlanners[self.zoneId] = suitPlanner
