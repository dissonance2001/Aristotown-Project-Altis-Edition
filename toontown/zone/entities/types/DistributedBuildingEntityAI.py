import random

from toontown.level.editor import EditorGlobals
from toontown.level.DistributedEntityAI import DistributedEntityAI
from toontown.toon.DistributedToonAI import DistributedToonAI
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from toontown.building import DoorTypes
from toontown.building import FADoorCodes
from toontown.building import SuitBuildingGlobals
from toontown.building import SuitPlannerInteriorAI
from toontown.quest3.context.BuildingContext import BuildingContext
from toontown.quest3.context.BuildingLaffContext import BuildingLaffContext
from toontown.suit.SuitDNA import suitDeptFullnames
from direct.distributed.ClockDelta import *
from toontown.toon.ToonStatsGlobals import ToonStats
from toontown.toonbase import TTLocalizer
from toontown.building import DistributedElevatorStreetAI
from toontown.building.DistributedToonInteriorAI import DistributedToonInteriorAI
from toontown.building.interior.ToonInteriorClassesAI import CustomToonInteriors
from toontown.zone.entities.standalone.DistributedLevelDoorAI import DistributedLevelDoorAI
from toontown.zone.entities.standalone.DistributedInteriorLevelDoorAI import DistributedInteriorLevelDoorAI
from toontown.zone.entities.standalone.DistributedLevelSuitInteriorAI import DistributedLevelSuitInteriorAI

from direct.fsm.FSM import FSM
import time


@DirectNotifyCategory()
class DistributedBuildingEntityAI(DistributedEntityAI, FSM):
    """
    DistributedBuildingEntityAI(DistributedEntityAI)

    A distributed building, maintaining an interior zone
    """
    ElevatorClass = DistributedElevatorStreetAI.DistributedElevatorStreetAI

    defaultTransitions = {
        'Off': ['WaitForVictors', 'BecomingToon', 'Toon', 'ClearOutToonInterior', 'BecomingSuit', 'Suit'],
        'WaitForVictors': ['BecomingToon'],
        'BecomingToon': ['Toon'],
        'Toon': ['ClearOutToonInterior'],
        'ClearOutToonInterior': ['BecomingSuit'],
        'BecomingSuit': ['Suit'],
        'Suit': ['WaitForVictors', 'BecomingToon']
    }

    def __init__(self, level, entId):
        self.notify.debug('init entity %s' % entId)
        DistributedEntityAI.__init__(self, level, entId)
        FSM.__init__(self, self.__class__.__name__)
        # Cog Building Data
        self.victorResponses = None
        self.track = 'c'
        self.difficulty = 1
        self.numFloors = 0
        self.savedBy = None
        self.becameSuitTime = 0
        # Interior/Exterior setup data
        self.interior = None
        self.doorData = {}
        self.doors = []
        self.insideDoors = []
        self.__doneSetup = False
        # Initialize building once the level is done generating
        self.acceptOnce(self.level.getLevelPostCreateEvent(), self.__initBuilding)
        self.request("Off")

    def announceGenerate(self):
        super().announceGenerate()
        if self.enabled:
            self.request("Toon")

    def cleanup(self):
        self.ignoreAll()

        if self.isDeleted():
            return

        self.request('Off')

        for door in self.doors:
            door.requestDelete()
            del door
        self.doors = []
        for insideDoor in self.insideDoors:
            insideDoor.requestDelete()
            del insideDoor
        self.insideDoors = []

        self.interior.requestDelete()
        del self.interior

        if hasattr(self, 'elevator'):
            self.elevator.requestDelete()
            del self.elevator

        FSM.cleanup(self)
        self.requestDelete()

    def destroy(self):
        self.cleanup()
        taskMgr.remove(self.taskName('suitbldg-time-out'))
        taskMgr.remove(self.taskName(str(self.blockNumber) + '_becomingToon-timer'))
        taskMgr.remove(self.taskName(str(self.blockNumber) + '_becomingSuit-timer'))
        taskMgr.remove(self.taskName(str(self.blockNumber) + '_clearOutToonInterior-timer'))
        self.removeTask(self.uniqueName('checkReclaim'))
        DistributedEntityAI.destroy(self)

    def __initBuilding(self):
        return

    @staticmethod
    def getDefaultDoorData():
        return {'numDoors': 1,
                'doorIndexStart': 0,
                'doorExtType': DoorTypes.EXT_STANDARD,
                'doorIntType': DoorTypes.INT_STANDARD}

    @property
    def numDoors(self):
        return self.doorData.get('numDoors', 1)

    @property
    def doorIndexStart(self):
        return self.doorData.get('doorIndexStart', 0)

    @property
    def doorExtType(self):
        return self.doorData.get('doorExtType', DoorTypes.EXT_STANDARD)

    @property
    def doorIntType(self):
        return self.doorData.get('doorIntType', DoorTypes.INT_STANDARD)

    def getSpecialSoundType(self, ext):
        soundBank = self.doorData.get('specialSoundType', {'ext': DoorTypes.SpecialSoundTypes.Standard,
                                                           'int': DoorTypes.SpecialSoundTypes.Standard})
        return soundBank.get('ext' if ext else 'int', DoorTypes.SpecialSoundTypes.Standard)

    @property
    def exteriorZone(self):
        return self.level.getEntityZoneId(self.entId)

    def setup(self, blockNumber):
        """
        :param int blockNumber: the landmark building number (from the name)
        """
        if self.__doneSetup:
            return

        self.__doneSetup = True
        # Create a custom interior object as defined.
        return

    def getDoor(self, ext, blockNumber, doorIndex=0):
        doorType = self.doorExtType if ext else self.doorIntType
        specialSoundType = self.getSpecialSoundType(ext)
        if ext:
            # Level door type for exteriors
            door = DistributedLevelDoorAI(
                self.air, blockNumber, doorType, self.entId, self.level.doId, lockValue=self.interior.LOCK_VALUE,
                doorIndex=doorIndex, soundType=specialSoundType
            )
        else:
            # Special interior door type, for handling zone movement
            door = DistributedInteriorLevelDoorAI(
                self.air, blockNumber, doorType, self.entId, self.level.doId, lockValue=self.interior.LOCK_VALUE, doorIndex=doorIndex
            )
        return door

    ### Begin DistributedBuildingAI garbage

    def suitTakeOver(self, suitTrack, difficulty):
        """Switch from toon to suit building
        suitTrack: one of 'g', 'c', 'l', 'm', or 's'
        difficulty: 0+
        """
        self.notify.debug('%s type Suit takeover at zone %s' % (suitDeptFullnames[suitTrack], self.zoneId))
        if not self.isToonBlock():
            return

        # Remove the old saved by credit with the old number of floors
        self.updateSavedBy(None)

        # Prevents one story DDL/AA buildings
        difficulty = min(difficulty, SuitBuildingGlobals.SuitPlannerEnum.BLDG_FLOOR_11)
        bldgInfo = SuitBuildingGlobals.getSuitBuildingInfo(difficulty)

        self.track = suitTrack
        self.difficulty = difficulty
        self.numFloors = bldgInfo.floors
        self.becameSuitTime = time.time()
        self.request('ClearOutToonInterior')

    def toonTakeOver(self):
        self.request('BecomingToon')
        if hasattr(self, 'interior'):
            self.interior.requestDelete()
            del self.interior

    def getFrontDoorPoint(self):
        return self.frontDoorPoint

    def setFrontDoorPoint(self, point):
        self.frontDoorPoint = point

    def getBlock(self):
        (dummy, interiorZoneId) = self.getExteriorAndInteriorZoneId()
        return [self.blockNumber, interiorZoneId]

    def getSuitData(self):
        return [ord(self.track), self.difficulty, self.numFloors]

    def getState(self):
        return [self.getCurrentOrNextState(), globalClockDelta.getRealNetworkTime()]

    def setState(self, state, timestamp=0):
        self.request(state)

    def isSuitBuilding(self):
        state = self.getCurrentOrNextState()
        return state in ('Suit', 'BecomingSuit', 'ClearOutToonInterior')

    def isSuitBlock(self):
        return self.isSuitBuilding()

    def isEstablishedSuitBlock(self):
        state = self.getCurrentOrNextState()
        return state == 'Suit'

    def isToonBlock(self):
        state = self.getCurrentOrNextState()
        return state in ('Toon', 'BecomingToon')

    def getSuitBuildingExteriorAndInteriorZoneId(self):
        return self.level.zoneId, self.destZone

    def getExteriorAndInteriorZoneId(self):
        return self.exteriorZone, self.destZone

    def d_setState(self, state):
        self.sendUpdate('setState', [state, globalClockDelta.getRealNetworkTime()])

    def b_setVictorList(self, victorList):
        self.setVictorList(victorList)
        self.d_setVictorList(victorList)

    def d_setVictorList(self, victorList):
        self.sendUpdate('setVictorList', [victorList])

    def setVictorList(self, victorList):
        self.victorList = victorList

    def findVictorIndex(self, avId):
        for i in range(len(self.victorList)):
            if self.victorList[i] == avId:
                return i

    def recordVictorResponse(self, avId):
        index = self.findVictorIndex(avId)
        if index is None:
            self.air.writeServerEvent('suspicious', avId, 'DistributedBuildingEntityAI.setVictorReady from toon not in %s.' % self.victorList)
            return
        self.victorResponses[index] = avId

    def allVictorsResponded(self):
        if self.victorResponses == self.victorList:
            return 1
        else:
            return 0

    def setVictorReady(self):
        avId = self.air.getAvatarIdFromSender()
        if self.victorResponses is None:
            self.air.writeServerEvent('suspicious', avId, 'DistributedBuildingEntityAI.setVictorReady in state %s.' % self.getCurrentOrNextState())
            return
        self.recordVictorResponse(avId)
        event = self.air.getAvatarExitEvent(avId)
        self.ignore(event)
        if self.allVictorsResponded():
            self.toonTakeOver()

    def setVictorExited(self, avId):
        self.notify.warning('Victor %d exited unexpectedly for bldg %d' % (avId, self.doId))
        self.recordVictorResponse(avId)
        if self.allVictorsResponded():
            self.toonTakeOver()

    def enterOff(self):
        pass

    def exitOff(self):
        pass

    def getToon(self, toonId):
        if toonId in self.air.doId2do:
            return self.air.doId2do[toonId]
        else:
            self.notify.warning('getToon(): toon: %d not in repository!' % toonId)

    def updateSavedBy(self, savedBy):
        if self.savedBy:
            toMessage = [avId for (avId, name, dna) in self.savedBy if self.air.doId2do.get(avId) is not None]
            self.air.chatManager.sendSystemMessageToToons(toMessage, TTLocalizer.RemoveTrophy, senderName=TTLocalizer.lToonHQ)

        self.savedBy = savedBy

    def enterWaitForVictors(self, victorList, savedBy):
        # Grab the list of active toons to pass in for each toon. (this is used by the quest system)
        activeToons = []
        self.notify.info("LogStats BuildingWasDefeated %s" % suitDeptFullnames[self.track])
        for t in victorList:
            toon = None
            if t:
                toon = self.getToon(t)
            if toon is not None:
                activeToons.append(toon)
        questBuildingContext = BuildingContext(
            zoneId=self.zoneId,
            track=self.track,
            floors=self.numFloors,
        )
        for t in victorList:
            toon = None
            if t:
                toon: DistributedToonAI = self.getToon(t)
                self.notify.info("LogStats ToonDefeatedBuilding %s avid %s" % (suitDeptFullnames[self.track], t))
                self.air.writeServerEvent('buildingDefeated', t, '%s|%s|%s|%s' % (self.track, self.numFloors, self.level.zoneId, victorList))
            if toon is not None:
                questBuildingLaffContext = BuildingLaffContext(
                    zoneId=self.level.zoneId,
                    track=self.track,
                    floors=self.numFloors,
                    laffRatio=toon.getHp()
                )
                self.air.quest3Manager.progressObjective(quester=toon, context=questBuildingContext)
                self.air.quest3Manager.progressObjective(quester=toon, context=questBuildingLaffContext)
                self.air.statsLeaderboardManager.updateLeaderboardFloors(toon, self.numFloors)
                toon.addStat(ToonStats.BLDGS)
                self.air.achievementsManager.bldg(t)
        for i in range(0, 4):
            victor = victorList[i]
            if (victor is None) or (victor not in self.air.doId2do):
                victorList[i] = 0
                continue
            event = self.air.getAvatarExitEvent(victor)
            self.accept(event, self.setVictorExited, extraArgs=[victor])

        self.b_setVictorList(victorList)
        self.updateSavedBy(savedBy)
        self.victorResponses = [0, 0, 0, 0]
        self.d_setState('WaitForVictors')

    def exitWaitForVictors(self):
        self.victorResponses = None
        for victor in self.victorList:
            event = simbase.air.getAvatarExitEvent(victor)
            self.ignore(event)

    def enterBecomingToon(self):
        self.d_setState('BecomingToon')
        name = self.taskName(str(self.blockNumber) + '_becomingToon-timer')
        taskMgr.doMethodLater(SuitBuildingGlobals.VICTORY_SEQUENCE_TIME, self.becomingToonTask, name)

    def exitBecomingToon(self):
        name = self.taskName(str(self.blockNumber) + '_becomingToon-timer')
        taskMgr.remove(name)

    def becomingToonTask(self, task):
        self.request('Toon')
        return task.done

    def enterToon(self):
        self.d_setState('Toon')

        if self.destZone in CustomToonInteriors:
            self.interior = CustomToonInteriors[self.destZone](self.blockNumber, self.air, self.destZone, self)
            # Set our door data based on the interior
            self.doorData = self.interior.DOOR_DATA or self.getDefaultDoorData()
        else:
            self.interior = DistributedToonInteriorAI(self.blockNumber, self.air, self.destZone, self)
        self.interior.generateWithRequired(self.destZone)

        for i in range(self.numDoors):
            doorIndex = i + self.doorIndexStart
            door = self.getDoor(ext=True, blockNumber=self.blockNumber, doorIndex=doorIndex)
            insideDoor = self.getDoor(ext=False, blockNumber=self.blockNumber, doorIndex=doorIndex)
            door.setOtherDoor(insideDoor)
            insideDoor.setOtherDoor(door)
            door.zoneId = self.exteriorZone
            insideDoor.zoneId = self.destZone
            door.generateWithRequired(self.exteriorZone)
            insideDoor.generateWithRequired(self.destZone)
            if doorIndex > 0:
                door.sendUpdate('setDoorIndex', [door.getDoorIndex()])
                insideDoor.sendUpdate('setDoorIndex', [insideDoor.getDoorIndex()])
            self.doors.append(door)
            self.insideDoors.append(insideDoor)

        self.becameSuitTime = 0
        self.air.writeServerEvent('building-toon', self.doId, '%s|%s' % (self.zoneId, self.blockNumber))

    def exitToon(self):
        for door in self.doors:
            door.setDoorLock(FADoorCodes.BUILDING_TAKEOVER)

    def enterClearOutToonInterior(self):
        self.d_setState('ClearOutToonInterior')
        if hasattr(self, 'interior'):
            self.interior.setState('beingTakenOver')
        name = self.taskName(str(self.blockNumber) + '_clearOutToonInterior-timer')
        # In the case of the level here, this also includes the time
        # it takes for a suit to walk up to the building and into the door
        taskMgr.doMethodLater(SuitBuildingGlobals.LEVEL_CLEAR_OUT_TOON_BLDG_TIME, self.clearOutToonInteriorTask, name)

    def exitClearOutToonInterior(self):
        name = self.taskName(str(self.blockNumber) + '_clearOutToonInterior-timer')
        taskMgr.remove(name)

    def clearOutToonInteriorTask(self, task):
        self.request('BecomingSuit')
        return task.done

    def enterBecomingSuit(self):
        self.notify.debug("enterBecomingSuit()")

        # We have to send this message before we send the distributed update to becomingSuit state, because the
        # clients depend on knowing what kind of suit building we're becoming.
        self.sendUpdate('setSuitData', [ord(self.track), self.difficulty, self.numFloors])
        self.d_setState('BecomingSuit')
        name = self.taskName(str(self.blockNumber) + '_becomingSuit-timer')
        taskMgr.doMethodLater(SuitBuildingGlobals.TO_SUIT_BLDG_TIME, self.becomingSuitTask, name)

    def exitBecomingSuit(self):
        name = self.taskName(str(self.blockNumber) + '_becomingSuit-timer')
        taskMgr.remove(name)
        if hasattr(self, 'interior'):
            self.interior.requestDelete()
            del self.interior
            for door in self.doors:
                door.requestDelete()
            self.doors = []
            for insideDoor in self.insideDoors:
                insideDoor.requestDelete()
            self.insideDoors = []

    def becomingSuitTask(self, task):
        self.request('Suit')
        return task.done

    def enterSuit(self):
        """Enters the cog building interior state for this building."""
        self.notify.debug("enterSuit()")

        # We have to send this message again, even though we've already sent it in becomingSuit, because we might have
        # come to this state directly on startup.
        self.sendUpdate('setSuitData', [ord(self.track), self.difficulty, self.numFloors])

        # Create the suit planner for the interior
        zoneId, interiorZoneId = self.getExteriorAndInteriorZoneId()
        self.planner = SuitPlannerInteriorAI.SuitPlannerInteriorAI(
            self.numFloors, self.difficulty, self.track, interiorZoneId)

        self.d_setState('Suit')
        # Create the DistributedDoor:
        exteriorZoneId, interiorZoneId = self.getExteriorAndInteriorZoneId()
        # Create the elevator.
        self.elevator = self.ElevatorClass(
            self.air,
            self)
        self.elevator.generateWithRequired(exteriorZoneId)

        # We're going to reclaim ourselves in a random amount of time between 2 and 4 hours.
        # This is to keep the rotation of buildings generally fresh
        self.doMethodLater(lerp(2*60*60, 4*60*60, random.random()), self.__checkReclaim, self.uniqueName('checkReclaim'))

        self.air.writeServerEvent(
            'building-cog', self.doId,
            '%s|%s|%s|%s' % (self.zoneId, self.blockNumber, self.track, self.numFloors))

    def exitSuit(self):
        self.removeTask(self.uniqueName('checkReclaim'))
        del self.planner
        if hasattr(self, 'elevator'):
            self.elevator.requestDelete()
            del self.elevator

    def __checkReclaim(self, task=None):
        # Check if we can reclaim this building naturally.
        if hasattr(self, 'elevator') and self.elevator.fsm.getCurrentState().getName() == 'waitEmpty':
            # We have an elevator still, and it's in the waitEmpty state.
            # This means there are no toons currently battling inside of us,
            # and we can go ahead and re-convert.
            self.b_setVictorList([0, 0, 0, 0])
            # Update the trophy manager to let it know these rescuers no longer
            # get credit for this building
            self.updateSavedBy(None)
            self.toonTakeOver()
            return task.done
        else:
            # Toons are most likely inside battling, so let's check again in about 15 minutes.
            task.delayTime = 15 * 60
            return task.again

    def _createSuitInterior(self):
        return DistributedLevelSuitInteriorAI(self.air, self.elevator, self.track)

    def createSuitInterior(self):
        self.interior = self._createSuitInterior()
        (dummy, interiorZoneId) = self.getExteriorAndInteriorZoneId()
        self.interior.generateWithRequired(interiorZoneId)
        self.interior.fsm.request('WaitForAllToonsInside')

    def deleteSuitInterior(self):
        if hasattr(self, 'interior'):
            self.interior.requestDelete()
            del self.interior

        if hasattr(self, 'elevator'):
            self.elevator.d_setFloor(-1)
            self.elevator.open()

    def suitInteriorComplete(self, victors, savedBy):
        self.request('WaitForVictors', victors, savedBy)

    if EditorGlobals.wantLevelEditor():
        def setEnabled(self, enabled):
            self.enabled = enabled
            if self.enabled:
                self.request('Toon')
            else:
                self.request('Off')
