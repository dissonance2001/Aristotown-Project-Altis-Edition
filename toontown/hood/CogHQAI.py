from __future__ import absolute_import
from toontown.building import DoorTypes
from toontown.building.DistributedBoardingPartyAI import DistributedBoardingPartyAI
from toontown.coghq import DistributedCogHQDoorAI
from toontown.coghq import DistributedCogHQBossDoorAI
from toontown.coghq import LobbyManagerAI
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownGlobals

class CogHQAI:
    notify = directNotify.newCategory('CogHQAI')
    notify.setInfo(True)

    def __init__(
            self, air, zoneId, lobbyZoneId, hardmodeLobbyZoneId, 
            lobbyFADoorCode, hardmodeFADoorCode,
            lobbyElevatorCtor, bossCtor, hardmodeLobbyElevatorCtor, 
            hardmodeBossCtor, zoneIdrCode):
        self.air = air  # type: ToontownAIRepository
        self.zoneId = zoneId
        self.lobbyZoneId = lobbyZoneId
        self.hardmodeLobbyZoneId = hardmodeLobbyZoneId
        self.lobbyFADoorCode = lobbyFADoorCode
        self.hardmodeFADoorCode = hardmodeFADoorCode
        self.lobbyElevatorCtor = lobbyElevatorCtor
        self.bossCtor = bossCtor
        self.hardmodeLobbyElevatorCtor = hardmodeLobbyElevatorCtor
        self.hardmodeBossCtor = hardmodeBossCtor
        self.zoneIdrCode = zoneIdrCode

        self.lobbyMgr = None
        self.lobbyElevator = None
        self.hardLobbyMgr = None
        self.hardLobbyElevator = None

        #NPCToons.createNpcsInZone(self.air, self.lobbyZoneId)

        self.notify.info('Creating objects... ' + self.getLocationName(zoneId))

    def getLocationName(self, zoneId):
        lookupTable = ToontownGlobals.hoodNameMap
        if (zoneId % 1000) != 0:
            lookupTable = TTLocalizer.GlobalStreetNames
        name = lookupTable.get(zoneId, '')
        if isinstance(name, str):
            return name
        return name[2]

    def startup(self):
        self.createLobbyManager()
        self.createLobbyElevator()
        self.extDoor = self.makeCogHQDoor(self.lobbyZoneId, 0, 0, self.lobbyFADoorCode, boss = 1)
        if self.hardmodeLobbyZoneId:
            self.hardmodeDoor = self.makeHardCogHQDoor(self.hardmodeLobbyZoneId, 0, 1, self.hardmodeFADoorCode)

    def createLobbyManager(self):
        self.lobbyMgr = LobbyManagerAI.LobbyManagerAI(self.air, self.bossCtor, self.zoneIdrCode)
        self.lobbyMgr.generateWithRequired(self.lobbyZoneId)
        if self.hardmodeLobbyZoneId:
            self.hardLobbyMgr = LobbyManagerAI.LobbyManagerAI(self.air, self.hardmodeBossCtor, self.zoneIdrCode)
            self.hardLobbyMgr.generateWithRequired(self.hardmodeLobbyZoneId)


    def createLobbyElevator(self):
        self.lobbyElevator = self.lobbyElevatorCtor(
            self.air, self.lobbyMgr, self.lobbyZoneId, antiShuffle = 1
        )
        self.lobbyElevator.generateWithRequired(self.lobbyZoneId)
        if self.hardmodeLobbyZoneId:
            self.hardLobbyElevator = self.hardmodeLobbyElevatorCtor(
                self.air, self.hardLobbyMgr, self.hardmodeLobbyZoneId, antiShuffle = 1
            )
            self.hardLobbyElevator.generateWithRequired(self.hardmodeLobbyZoneId)


    def makeCogHQDoor(self, destinationZone, intDoorIndex, extDoorIndex, lock = 0, boss = 0, zoneOverride=None):
        """
        :param destinationZone: Destination ZoneID
        :type destinationZone: int
        :param intDoorIndex: Name of the door index node (door_0, door_1, door_x) for destination zoneID
        :type intDoorIndex: int
        :param extDoorIndex: Name of the door index node (door_0, door_1, door_x) for source/origin zoneID
        :type extDoorIndex: int
        :param lock: Determines if the door is locked by default , unlock logic located in DistCogHQDoorAI.
                     If 1, door is inherently locked.
                     If 0, door is inherently unlocked.
        :type lock: int
        :param boss: Determines the CogHQ Door type:
                     If 1, uses DistributedCogHQBossDoorAI.
                     If 0, uses DistributedCogHQDoorAI
        :type boss: int
        :return: Door to enter specified zone.
        :rtype: DistributedCogHQBossDoorAI.DistributedCogHQBossDoorAI | DistributedCogHQDoorAI.DistributedCogHQDoorAI
        """
        # Use a different door class if it is specified.
        doorClass = DistributedCogHQDoorAI.DistributedCogHQDoorAI if boss else DistributedCogHQDoorAI.DistributedCogHQDoorAI
        if zoneOverride:
            doorSpawnZone = zoneOverride
        else:
            doorSpawnZone = self.zoneId
        intDoor = doorClass(self.air, 0, DoorTypes.INT_COGHQ, doorSpawnZone, doorIndex=intDoorIndex, lockValue=lock)
        intDoor.zoneId = destinationZone

        extDoor = doorClass(self.air, 0, DoorTypes.EXT_COGHQ, destinationZone, doorIndex=extDoorIndex, lockValue=lock)

        extDoor.setOtherDoor(intDoor)
        intDoor.setOtherDoor(extDoor)

        intDoor.generateWithRequired(destinationZone)
        intDoor.sendUpdate('setDoorIndex', [intDoor.getDoorIndex()])

        extDoor.generateWithRequired(doorSpawnZone)
        extDoor.sendUpdate('setDoorIndex', [extDoor.getDoorIndex()])

        return extDoor
    
    def makeHardCogHQDoor(self, destinationZone, intDoorIndex, extDoorIndex, lock=0):
        """
        :param destinationZone: Destination ZoneID
        :type destinationZone: int
        :param intDoorIndex: Name of the door index node (door_0, door_1, door_x) for destination zoneID
        :type intDoorIndex: int
        :param extDoorIndex: Name of the door index node (door_0, door_1, door_x) for source/origin zoneID
        :type extDoorIndex: int
        :param lock: Determines if the door is locked by default , unlock logic located in DistCogHQDoorAI.
                     If 1, door is inherently locked.
                     If 0, door is inherently unlocked.
        :type lock: int
        :return: Door to enter specified zone.
        :rtype: DistributedCogHQDoorAI.DistributedCogHQDoorAI
        """
        intDoor = DistributedCogHQDoorAI.DistributedCogHQDoorAI(
            self.air, 0, DoorTypes.INT_COGHQ, self.lobbyZoneId,
            doorIndex=intDoorIndex, lockValue=lock, hardmode = True
        )
        intDoor.zoneId = destinationZone

        extDoor = DistributedCogHQDoorAI.DistributedCogHQDoorAI(
            self.air, 0, DoorTypes.EXT_COGHQ, destinationZone,
            doorIndex=extDoorIndex, lockValue=lock, hardmode = True
        )

        extDoor.setOtherDoor(intDoor)
        intDoor.setOtherDoor(extDoor)

        intDoor.generateWithRequired(destinationZone)
        intDoor.sendUpdate('setDoorIndex', [intDoor.getDoorIndex()])

        extDoor.generateWithRequired(self.lobbyZoneId)
        extDoor.sendUpdate('setDoorIndex', [extDoor.getDoorIndex()])

        return extDoor

    def createBoardingParty(self):
        self.boardingParty = DistributedBoardingPartyAI(self.air, [self.lobbyElevator.doId], 8)
        self.boardingParty.generateWithRequired(self.lobbyZoneId)
