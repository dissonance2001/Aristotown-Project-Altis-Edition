"""
Contains the SuitPlannerInteriorAI class which handles management of all suits within a suit building.

Date: 8/13/01
Author: jlbutler
"""

import random

from panda3d.core import ConfigVariableBool, ConfigVariableString

from toontown.building import ClashSuitBuildingGlobals
from toontown.suit import DistributedSuitAI
from toontown.suit import SuitDNA
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class ClashSuitPlannerInteriorAI:
    """
    Manages all suits which exist within a single suit building.
    This object only exists on the server AI.
    """

    def __init__(self, numFloors, bldgLevel, bldgTrack, zone, virtual=False, departmentBoss=False):
        """
        :param int numFloors: number of floors in the building
        :param int bldgLevel: how difficult the building is, based on the suit that initially took the building
        :param str bldgTrack: the track of the building, based on the track that initially took the building
        :param int zone: Zone ID of the building
        """
        # when the suit planner interior is created, create information about all suits that will exist in this building
        self.dbg_4SuitsPerFloor = ConfigVariableBool('4-suits-per-floor', False).getValue()
        self.dbg_1SuitPerFloor = ConfigVariableBool('1-suit-per-floor', False).getValue()
        self.zoneId = zone
        self.numFloors = numFloors

        # Variable for if we are handling a department boss fight (VP, CFO, CLO, CEO).
        self.isDepartmentBoss = departmentBoss

        # Variable for if we are handling a virtual cog round in a boss.
        self.virtualCogRound = virtual

        # By default, if an invasion is in progress we do NOT only generate suits of that kind.
        # Set this true to turn on this behavior.
        self.respectInvasions = 0
        dbg_defaultSuitName = ConfigVariableString('suit-type', 'random').getValue()
        if dbg_defaultSuitName == 'random':
            self.dbg_defaultSuitType = None
        else:
            self.dbg_defaultSuitType = SuitDNA.getSuitType(dbg_defaultSuitName)

        if isinstance(bldgLevel, str):
            self.notify.warning('bldgLevel is a string!')
            bldgLevel = int(bldgLevel)
        self.bldgLevel = bldgLevel
        
        self._genSuitInfos(numFloors, bldgLevel, bldgTrack)

    def _genJoinChances(self, num):
        """
        :type num: int
        """
        joinChances = []
        for currChance in range(num):
            joinChances.append(random.randint(1, 100))
        joinChances.sort()
        return joinChances

    def _genSuitType(self, bldgTrack, bldgLevel, isBoss=False):
        """
        This method abstracts out the logic determining what cogs generate in the building.
        There is a very small chance (2.5%) that a cog of a different type than the building's type is generated.
        This naturally isn't the case during the Boardbot Marketing Holiday, where Boardbot buildings solely have Boardbots,
        With a 10% chance increase to spawn in other buildings.

        :param bldgTrack (char): The cog type of the building
        :param bldgLevel (int): The size in floors of the building
        :param isBoss (bool): If this cog is the boss of the building
        :return (str): The randomly(ish) designated cog type
        """
        if bldgTrack == 'mixedCogs':
            return random.choice(['c', 'l', 'm', 's', 'g'])
        elif isBoss:
            return bldgTrack
        else:
            if bldgLevel <= ClashSuitBuildingGlobals.SPE.BLDG_FLOOR_11:
                if random.random() <= 0.025:
                    tracks = ['c', 'l', 'm', 's', 'g']  # create a list of all possible tracks
                    tracks.remove(bldgTrack)  # remove our dept
                    return random.choice(tracks)  # then choose
                else:
                    return bldgTrack
            else:
                return bldgTrack

    def _genSuitInfos(self, numFloors, bldgLevel, bldgTrack):
        """
        Creates information about all suits that will exist in this building

        :param int numFloors: number of floors in the building
        :param int bldgLevel: how difficult the building is, based on the suit that initially took the building
        :param str bldgTrack: the track of the building, based on the track that initially took the building
        """
        self.suitInfos = []
        self.notify.debug('generating suitsInfos with numFloors (' + str(numFloors) + ') bldgLevel (' + str(bldgLevel) + '+1) and bldgTrack (' + str(bldgTrack) + ')')

        # process each floor in the building and create all active and reserve suits
        for currFloor in range(numFloors):
            infoDict = {}
            lvls = self._genLevelList(bldgLevel, currFloor, numFloors)

            # now randomly decide how many suits will be active and how many will be in reserve, create the active suit
            # objects create the active suits in order of highest level to lowest.
            # this is only because we want ensure the highest level active suit is in the first position in the list
            activeDicts = []
            if self.dbg_4SuitsPerFloor:
                numActive = 4
            else:
                numActive = random.randint(1, min(4, len(lvls)))
            if currFloor + 1 == numFloors and len(lvls) > 1:
                # Make the boss be suit 1 (unless there is only 1 active suit)
                origBossSpot = len(lvls) - 1
                if numActive == 1:
                    newBossSpot = numActive - 1
                else:
                    newBossSpot = numActive - 2
                tmp = lvls[newBossSpot]
                lvls[newBossSpot] = lvls[origBossSpot]
                lvls[origBossSpot] = tmp

            bldgInfo = ClashSuitBuildingGlobals.getSuitBuildingInfo(bldgLevel)
            revives = bldgInfo.revives[0]  # Set revive info from building info
            for currActive in range(numActive - 1, -1, -1):
                level = lvls[currActive]
                type = self._genNormalSuitType(level)
                track = bldgTrack
                activeDict = {'type': type, 'track': track, 'level': level, 'revives': revives}
                # This has to be the boss suit since it is at least the lowest possible boss level
                if bldgLevel <= ClashSuitBuildingGlobals.SPE.BLDG_FLOOR_11 and level >= bldgInfo.suitBossLevels[0]:
                    activeDict['elite'] = 1
                    activeDict['track'] = bldgTrack  # Force it to be the dept of the bldg
                    activeDict['buildingBoss'] = True
                else:
                    activeDict['elite'] = self.getEliteRoll(bldgInfo)  # Otherwise, run the random calcluation on it
                activeDicts.append(activeDict)

            infoDict['activeSuits'] = activeDicts

            # now create the reserve suit objects, also assign each a % join restriction.
            # this indicates when the reserve suit should join the battle based on how much damage has been
            # done to the suits currently in the battle
            reserveDicts = []
            numReserve = len(lvls) - numActive
            joinChances = self._genJoinChances(numReserve)
            for currReserve in range(numReserve):
                level = lvls[currReserve + numActive]  # Set level
                type = self._genNormalSuitType(level)
                track = bldgTrack  # Set cog department
                elite = self.getEliteRoll(bldgInfo)  # Get the elite chance and set if it qualifies
                joinChance = joinChances[currReserve]  # In buildings, this is pretty redundant
                reserveDict = {'type': type, 'track': track, 'level': level, 'revives': revives, 'elite': elite,
                               'joinChance': joinChance}
                reserveDicts.append(reserveDict)  # Add the suit info to the reserve suit dictionary
                
            if len(reserveDicts) > 0:
                lastSuit = reserveDicts.pop()
                scrambledDicts = reserveDicts[:]
                random.shuffle(scrambledDicts)
                scrambledDicts.append(lastSuit)
                infoDict['reserveSuits'] = scrambledDicts
            else:
                infoDict['reserveSuits'] = reserveDicts
            self.suitInfos.append(infoDict)

    def _genNormalSuitType(self, lvl):
        """
        Generates info for a normal suit that we might find in this particular building

        :param int lvl: level of random suit to generate
        :returns: list containing the suit level, type, and track
        :rtype list[int, int, str]
        """
        # there is a similar formula in DistributedSuitPlannerAI used for picking suit types for the streets,
        # based on the suit level we need to make sure we pick a valid suit type that can actually be this level
        # (each suit type can be 1 of 5 levels)
        # TODO: track this formula down and make it use SuitDNA.getRandomSuitType
        if self.dbg_defaultSuitType is not None:
            return self.dbg_defaultSuitType

        return SuitDNA.getRandomSuitType(lvl)

    def _genLevelList(self, bldgLevel, currFloor, numFloors):
        """
        Based on a few parameters from the building, create a list of suit levels for a specific floor

        :param int bldgLevel: level of the current building (the level of the suit that took it over, value is 0-based)
        :param int currFloor: current floor that we are calculating
        :param int numFloors: total number of floors in this bldg
        :returns: list of suit levels
        :rtype: list[int]
        """
        bldgInfo = ClashSuitBuildingGlobals.getSuitBuildingInfo(bldgLevel)
        if self.dbg_1SuitPerFloor:
            return [1]
        elif self.dbg_4SuitsPerFloor:
            return [5, 6, 7, 10]
        lvlPoolRange = bldgInfo.levelPool
        maxFloors = bldgInfo.floors
        lvlPoolMults = bldgInfo.levelPoolMults
        floorIdx = min(currFloor, maxFloors - 1)
        lvlPoolMin = lvlPoolRange[0] * lvlPoolMults[floorIdx]
        lvlPoolMax = lvlPoolRange[1] * lvlPoolMults[floorIdx]
        lvlPool = random.randint(int(lvlPoolMin), int(lvlPoolMax))
        lvlMin = bldgInfo.suitLevels[0]
        lvlMax = bldgInfo.suitLevels[1]
        self.notify.debug('Level Pool: ' + str(lvlPool))

        lvlList = []
        while lvlPool >= lvlMin:
            newLvl = random.randint(lvlMin, min(lvlPool, lvlMax))
            lvlList.append(newLvl)
            lvlPool -= newLvl

        if currFloor + 1 == numFloors:
            bossLvlRange = bldgInfo.suitBossLevels
            newLvl = random.randint(bossLvlRange[0], bossLvlRange[1])
            lvlList.append(newLvl)
        lvlList.sort()
        self.notify.debug('LevelList: ' + repr(lvlList))
        return lvlList

    def __setupSuitInfo(self, suit, bldgTrack, suitLevel, suitType, name):
        """
        Creates dna information for the given suit with the given track and suit type
        """
        dna = SuitDNA.SuitDNA()
        if not name:
            dna.newSuitRandom(suitType, bldgTrack)
        else:
            dna.newSuit(name)
        suit.dna = dna
        suit.setLevel(suitLevel)

    def __genSuitObject(self, suitZone, suitType, bldgTrack, suitLevel, revives = 0, elite = 0, name = None):
        """
        Generates a distributed suit object

        :returns: the suit object created
        """
        newSuit = DistributedSuitAI.DistributedSuitAI(simbase.air, None)
        self.__setupSuitInfo(newSuit, bldgTrack, suitLevel, suitType, name)
        newSuit.setSkeleRevives(revives)
        newSuit.setElite(elite)
        newSuit.generateWithRequired(suitZone)

        # Fill in the name so we can tell one suit from another in printouts.
        newSuit.node().setName('suit-%s' % newSuit.doId)
        return newSuit

    def myPrint(self, suitInfos):
        """
        prints suit infos structure to see what and which suits exist on each floor of this building (debug use only)

        :param struct suitInfos: structure containing all suits in this building
        """
        self.notify.debug('Generated suits for building: ')
        for currInfo in suitInfos:
            whichSuitInfo = suitInfos.index(currInfo) + 1
            self.notify.debug(' Floor ' + str(whichSuitInfo) + ' has ' + str(len(currInfo[0])) + ' active suits.')
            for currActive in range(len(currInfo[0])):
                self.notify.debug('  Active suit ' + str(currActive + 1) + ' is of type ' + str(currInfo[0][currActive][0]) + ' and of track ' + str(currInfo[0][currActive][1]) + ' and of level ' + str(currInfo[0][currActive][2]))

            self.notify.debug(' Floor ' + str(whichSuitInfo) + ' has ' + str(len(currInfo[1])) + ' reserve suits.')
            for currReserve in range(len(currInfo[1])):
                self.notify.debug('  Reserve suit ' + str(currReserve + 1) + ' is of type ' + str(currInfo[1][currReserve][0]) + ' and of track ' + str(currInfo[1][currReserve][1]) + ' and of lvel ' + str(currInfo[1][currReserve][2]) + ' and has ' + str(currInfo[1][currReserve][3]) + '% join restriction.')

    def genFloorSuits(self, floor):
        """
        :type floor: int
        """
        self.notify.debug('genFloorSuits(): generating suits for floor: %d' % floor)
        suitHandles = {}
        floorInfo = self.suitInfos[floor]
        activeSuits = []
        for activeSuitInfo in floorInfo['activeSuits']:
            suit = self.__genSuitObject(
                self.zoneId,
                activeSuitInfo['type'],
                self._genSuitType(activeSuitInfo['track'], self.bldgLevel, isBoss=activeSuitInfo.get('buildingBoss', False)),
                activeSuitInfo['level'],
                activeSuitInfo['revives'],
                activeSuitInfo['elite'],
                activeSuitInfo.get('name'))
            activeSuits.append(suit)
        suitHandles['activeSuits'] = activeSuits

        reserveSuits = []
        for reserveSuitInfo in floorInfo['reserveSuits']:
            suit = self.__genSuitObject(
                self.zoneId,
                reserveSuitInfo['type'],
                self._genSuitType(reserveSuitInfo['track'], self.bldgLevel, isBoss=reserveSuitInfo.get('buildingBoss', False)),
                reserveSuitInfo['level'],
                reserveSuitInfo['revives'],
                reserveSuitInfo['elite'],
                reserveSuitInfo.get('name'))
            reserveSuits.append((suit, reserveSuitInfo['joinChance']))
        suitHandles['reserveSuits'] = reserveSuits

        return suitHandles

    def genSuits(self):
        """
        For each floor, create a list of active and reserve suits that should exist inside a suit building

        :returns: a map
        """
        self.notify.debug('genSuits(): for zone: %d' % self.zoneId)
        suitHandles = []

        # process each floor in the building and create all active and reserve suits
        for floor in range(len(self.suitInfos)):
            floorSuitHandles = self.genFloorSuits(floor)
            suitHandles.append(floorSuitHandles)

        return suitHandles

    def getEliteRoll(self, bldgInfo: ClashSuitBuildingGlobals.SuitBuildingInfo):
        return random.random() <= bldgInfo.exeChance


"""
History

13Aug01   jlbutler   created.
14Aug01   jlbutler   modified to have two separate steps, the first is done
                     automatically when the SuitPlannerInteriorAI is created,
                     which creates all suit information for the building (this way
                     the same suits will be in this building until it is taken back
                     by toons), the second step is done when genSuits is called, this
                     creates the actual suit objects for the entire building (only
                     needed to be done when a toon enters the building)
"""
