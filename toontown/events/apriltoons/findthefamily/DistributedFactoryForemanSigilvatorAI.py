from toontown.building import ElevatorConstants
from toontown.instances.elevators import DistributedSigilvatorAI
from typing import TYPE_CHECKING

from toontown.groups.GroupEnums import GroupType
from toontown.toonbase import ToontownGlobals

if TYPE_CHECKING:
    from toontown.ai.ToontownAIRepository import ToontownAIRepository


class DistributedFactoryForemanSigilvatorAI(DistributedSigilvatorAI.DistributedSigilvatorAI):
    """
    DistributedFactoryForemanSigilvatorAI(DistributedSigilvatorAI)
    """
    base_elevator_time = ElevatorConstants.ElevatorData[ElevatorConstants.ELEVATOR_INSTANCE_MERC_SIGIL]['countdown']
    groupType = [GroupType.FindTheFamily, GroupType.OverclockedFindTheFamily]

    def __init__(self, air, bldg, factoryId, entranceId, antiShuffle=0, minLaff=0):
        """
        :type air: ToontownAIRepository
        :type factoryId: int
        :type entranceId: int
        :param int antiShuffle: acts like a boolean
        :type minLaff: int
        """
        super().__init__(air, bldg, ToontownGlobals.SellbotFactoryInt, antiShuffle=antiShuffle, minLaff=minLaff)
        self.factoryId = factoryId
        self.entranceId = entranceId

    @property
    def closeTime(self):
        return 7.5

    def getEntranceId(self):
        return self.entranceId

    def getSpecificGroupType(self):
        groupDict = {
            2: GroupType.FindTheFamily,
            4: GroupType.OverclockedFindTheFamily
        }
        return groupDict[self.entranceId]

    def elevatorClosed(self):
        numPlayers = self.countFullSeats()

        # It is possible the players exited the district
        if numPlayers > 0:
            # Create a factory interior just for us

            # Make a nice list for the factory
            players = []
            for i in self.seats:
                if i not in [None, 0]:
                    players.append(i)
            reservedGroup = self._getReservedGroup()
            groupCreation = None if not reservedGroup else reservedGroup.getGroupCreation()
            factoryZone = self.bldg.createFactory(self.factoryId, self.entranceId, players, groupCreation=groupCreation)

            for seatIndex in range(len(self.seats)):
                avId = self.seats[seatIndex]
                if avId:
                    # Tell each player on the elevator that they should enter the factory And which zone it is in
                    self.sendUpdateToAvatarId(avId, 'setFactoryInteriorZone', [factoryZone])
                    # Clear the fill slot
                    self.clearFullNow(seatIndex)
        else:
            self.notify.warning('The elevator left, but was empty.')
        self.fsm.request('closed')

    def sendAvatarsToDestination(self, avIdList):
        """
        :type avIdList: list
        """
        if len(avIdList) > 0:
            factoryZone = self.bldg.createFactory(self.factoryId, self.entranceId, avIdList)
            for avId in avIdList:
                if avId:
                    # Tell each player on the elevator that they should enter the factory And which zone it is in
                    self.sendUpdateToAvatarId(avId, 'setFactoryInteriorZoneForce', [factoryZone])
