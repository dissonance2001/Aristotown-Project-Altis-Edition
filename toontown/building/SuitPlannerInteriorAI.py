from __future__ import absolute_import
import random
import types
from direct.directnotify import DirectNotifyGlobal
from toontown.building import SuitBuildingGlobals
from otp.ai.AIBaseGlobal import *
from toontown.suit import DistributedSuitAI
from direct.interval.IntervalGlobal import *
from toontown.suit import SuitDNA
from toontown.battle import SuitBattleGlobals
from toontown.suit.SuitInvasionGlobals import IFSkelecog, IFWaiter, IFV2
from toontown.toonbase import ToontownBattleGlobals
from six.moves import range

class SuitPlannerInteriorAI:
    notify = DirectNotifyGlobal.directNotify.newCategory('SuitPlannerInteriorAI')
    MIN_LEVEL_BY_TYPE = {
        1: 1,
        2: 2,
        3: 3,
        4: 4,
        5: 5,
        6: 6,
        7: 7,
        8: 8,
    }

    MAX_LEVEL_BY_TYPE = {
        1: 5,
        2: 6,
        3: 7,
        4: 12,
        5: 15,
        6: 15,
        7: 20,
        8: 50,
    }

    def __init__(self, numFloors, bldgLevel, bldgTrack, zone):
        self.dbg_4SuitsPerFloor = config.GetBool('4-suits-per-floor', 0)
        self.dbg_1SuitPerFloor = config.GetBool('1-suit-per-floor', 0)
        self.zoneId = zone
        self.numFloors = numFloors
        self.respectInvasions = 0
        dbg_defaultSuitName = simbase.config.GetString('suit-type', 'random')
        if dbg_defaultSuitName == 'random':
            self.dbg_defaultSuitType = None
        else:
            self.dbg_defaultSuitType = SuitDNA.getSuitType(dbg_defaultSuitName)
        if isinstance(bldgLevel, bytes):
            self.notify.warning('bldgLevel is a string!')
            bldgLevel = int(bldgLevel)
        
        self._genSuitInfos(numFloors, bldgLevel, bldgTrack)

    def __genJoinChances(self, num):
        joinChances = []
        for currChance in range(num):
            joinChances.append(random.randint(1, 100))

        joinChances.sort(cmp)
        return joinChances

    def _genSuitInfos(self, numFloors, bldgLevel, bldgTrack):
        self.suitInfos = []
        self.notify.debug('\n\ngenerating suitsInfos with numFloors (' + str(numFloors) + ') bldgLevel (' + str(bldgLevel) + '+1) and bldgTrack (' + str(bldgTrack) + ')')
        for currFloor in range(numFloors):
            infoDict = {}
            lvls = self.__genLevelList(bldgLevel, currFloor, numFloors)
            activeDicts = []
            if self.dbg_4SuitsPerFloor:
                numActive = 4
            else:
                numActive = random.randint(1, min(4, len(lvls)))
            if currFloor + 1 == numFloors and len(lvls) > 1:
                origBossSpot = len(lvls) - 1
                if numActive == 1:
                    newBossSpot = numActive - 1
                else:
                    newBossSpot = numActive - 2
                tmp = lvls[newBossSpot]
                lvls[newBossSpot] = lvls[origBossSpot]
                lvls[origBossSpot] = tmp
            bldgInfo = SuitBuildingGlobals.SuitBuildingInfo[bldgLevel]
            revives = 0
            for currActive in range(numActive - 1, -1, -1):
                level = lvls[currActive]
                type = self.__genNormalSuitType(level)
                activeDict = {}
                activeDict['type'] = type
                track = random.choice(['c', 'l', 'm', 's', 'g', 't'])
                activeDict['track'] = track
                activeDict['level'] = level
                activeDict['revives'] = revives
                activeDicts.append(activeDict)

            infoDict['activeSuits'] = activeDicts
            reserveDicts = []
            numReserve = len(lvls) - numActive
            joinChances = self.__genJoinChances(numReserve)
            for currReserve in range(numReserve):
                level = lvls[currReserve + numActive]
                type = self.__genNormalSuitType(level)
                reserveDict = {}
                reserveDict['type'] = type
                track = random.choice(['c', 'l', 'm', 's', 'g', 't'])
                reserveDict['track'] = track
                reserveDict['level'] = level
                reserveDict['revives'] = revives
                reserveDict['joinChance'] = joinChances[currReserve]
                reserveDicts.append(reserveDict)

            infoDict['reserveSuits'] = reserveDicts
            self.suitInfos.append(infoDict)

    def __genNormalSuitType(self, lvl):
        if self.dbg_defaultSuitType != None:
            return self.dbg_defaultSuitType
        return SuitDNA.getRandomSuitType(lvl)
    
    def __suitTierFromLevel(self, level):
        possibleTiers = []

        for tier in range(1, 8 + 1):
            minLevel = self.MIN_LEVEL_BY_TIER.get(tier, tier)
            maxLevel = self.MAX_LEVEL_BY_TIER.get(tier, tier + 4)

            if minLevel <= level <= maxLevel:
                possibleTiers.append(tier)

        if not possibleTiers:
            return 8

        return random.choice(possibleTiers)

    def __genLevelList(self, bldgLevel, currFloor, numFloors):
        bldgInfo = SuitBuildingGlobals.SuitBuildingInfo[bldgLevel]
        if self.dbg_1SuitPerFloor:
            return [1]
        elif self.dbg_4SuitsPerFloor:
            return [5,
             6,
             7,
             10]
        lvlPoolRange = bldgInfo[SuitBuildingGlobals.SUIT_BLDG_INFO_LVL_POOL]
        maxFloors = bldgInfo[SuitBuildingGlobals.SUIT_BLDG_INFO_FLOORS][1]
        lvlPoolMults = bldgInfo[SuitBuildingGlobals.SUIT_BLDG_INFO_LVL_POOL_MULTS]
        floorIdx = min(currFloor, maxFloors - 1)
        lvlPoolMin = lvlPoolRange[0] * lvlPoolMults[floorIdx]
        lvlPoolMax = lvlPoolRange[1] * lvlPoolMults[floorIdx]
        lvlPool = random.randint(int(lvlPoolMin), int(lvlPoolMax))
        lvlMin = bldgInfo[SuitBuildingGlobals.SUIT_BLDG_INFO_SUIT_LVLS][0]
        lvlMax = bldgInfo[SuitBuildingGlobals.SUIT_BLDG_INFO_SUIT_LVLS][1]
        self.notify.debug('Level Pool: ' + str(lvlPool))
        lvlList = []
        while lvlPool >= lvlMin:
            newLvl = random.randint(lvlMin, min(lvlPool, lvlMax))
            lvlList.append(newLvl)
            lvlPool -= newLvl

        if currFloor + 1 == numFloors:
            bossLvlRange = bldgInfo[SuitBuildingGlobals.SUIT_BLDG_INFO_BOSS_LVLS]
            newLvl = random.randint(bossLvlRange[0], bossLvlRange[1])
            lvlList.append(newLvl)
        lvlList.sort(cmp)
        self.notify.debug('LevelList: ' + repr(lvlList))
        return lvlList
    
    def __genRandomUncappedSuit(
            self,
            minLevel,
            maxLevel,
            bldgTrack=None,
            revives=0):

        if bldgTrack is None:
            bldgTrack = random.choice(SuitDNA.suitDepts)

        suitLevel = random.randint(
            minLevel,
            maxLevel
        )

        # suitTier must still be a valid tier from 1 through 8.
        suitTier = random.randint(1, 8)

        return self.__genSuitObject(
            self.zoneId,
            suitTier,
            bldgTrack,
            suitLevel,
            revives
        )

    def __setupSuitInfo(
        self,
        suit,
        bldgTrack,
        suitLevel,
        suitType=None,
        suitName=None,
        forceLevel=False):
        suitDeptIndex, suitTypeIndex, flags = simbase.air.suitInvasionManager.getInvadingCog()
        if self.respectInvasions:
            if suitDeptIndex is not None:
                bldgTrack = SuitDNA.suitDepts[suitDeptIndex]
            if suitTypeIndex is not None:
                suitName = SuitDNA.getSuitName(
                    suitDeptIndex,
                    suitTypeIndex
                )

                suitType = SuitDNA.getSuitType(
                    suitName
                )

    # Do not alter suitLevel here.
        dna = SuitDNA.SuitDNA()
        if suitName is not None:
            dna.newSuit(suitName)
        else:
            dna.newSuitRandom(suitType, bldgTrack)
        suit.dna = dna
        suit.setLevel(
            suitLevel,
            forceLevel=forceLevel
        )
        if suit.dna.name in SuitBattleGlobals.SpecialCogDict:
            suit.setManager(1)
        #if random.randint(0, 100) <= ToontownBattleGlobals.V2_BASE_CHANCE and not suit.getManager() and suit.dna.name != 'cg' and not suit.isSkeleton:
          #  suit.setSkeleRevives(random.choice((1, 2)))
        #if random.randint(0, 100) <= ToontownBattleGlobals.V2_BASE_CHANCE and suit.isSkeleton:
           # suit.setSkeleRevives(1)
        if suit.dna.name in ('autocad', 'chairp', 'watchm', 'ant'):
            suit.setExecutive(1)
        elif suit.dna.name in ('mh2', 'std2', 'cnd2'):
            suit.setGovernaught(1)
        elif random.randint(0, 100) <= ToontownBattleGlobals.EXECUTIVE_BASE_CHANCE and not suit.getManager() and suit.dna.name != 'ovt':
            suit.setExecutive(1)
        elif random.randint(0, 100) <= ToontownBattleGlobals.GOVERNAUGHT_BASE_CHANCE and not suit.getManager() and suit.dna.name not in ('djockey', 'ovt'):
            suit.setGovernaught(1)
        suit.setCog(1)
        return flags

    def __genSuitObject(
        self,
        suitZone,
        suitType=None,
        bldgTrack=None,
        suitLevel=1,
        revives=0,
        skelecogChance=0,
        revivesTwoChance=0,
        revivesThreeChance=0,
        forceExecutive=0,
        suitName=None,
        forceLevel=False):
        newSuit = DistributedSuitAI.DistributedSuitAI(simbase.air, None)
        flags = self.__setupSuitInfo(
            newSuit,
            bldgTrack,
            suitLevel,
            suitType=suitType,
            suitName=suitName,
            forceLevel=forceLevel
        )
        newSuit.setSkeleRevives(revives)
        # if forceExecutive > 0:
        #     newSuit.setExecutive(1)
        #     newSuit.setGovernaught(0)
        if random.randint(1, 100) <= revivesThreeChance:
            newSuit.setSkeleRevives(2)
        elif random.randint(1, 100) <= revivesTwoChance:
            newSuit.setSkeleRevives(1)
        if random.randint(1, 100) <= skelecogChance:
            newSuit.setSkelecog(1)
        elif flags & IFSkelecog:
            newSuit.setSkelecog(1)
        newSuit.generateWithRequired(suitZone)
        if flags & IFWaiter:
            newSuit.b_setWaiter(1)
        if flags & IFV2:
            newSuit.b_setSkeleRevives(1)
        newSuit.node().setName('suit-%s' % newSuit.doId)
        return newSuit

    def myPrint(self):
        self.notify.info('Generated suits for building: ')
        for currInfo in suitInfos:
            whichSuitInfo = suitInfos.index(currInfo) + 1
            self.notify.debug(' Floor ' + str(whichSuitInfo) + ' has ' + str(len(currInfo[0])) + ' active suits.')
            for currActive in range(len(currInfo[0])):
                self.notify.debug('  Active suit ' + str(currActive + 1) + ' is of type ' + str(currInfo[0][currActive][0]) + ' and of track ' + str(currInfo[0][currActive][1]) + ' and of level ' + str(currInfo[0][currActive][2]))

            self.notify.debug(' Floor ' + str(whichSuitInfo) + ' has ' + str(len(currInfo[1])) + ' reserve suits.')
            for currReserve in range(len(currInfo[1])):
                self.notify.debug('  Reserve suit ' + str(currReserve + 1) + ' is of type ' + str(currInfo[1][currReserve][0]) + ' and of track ' + str(currInfo[1][currReserve][1]) + ' and of lvel ' + str(currInfo[1][currReserve][2]) + ' and has ' + str(currInfo[1][currReserve][3]) + '% join restriction.')

    def genFloorSuits(self, floor):
        suitHandles = {}
        floorInfo = self.suitInfos[floor]
        activeSuits = []
        for activeSuitInfo in floorInfo['activeSuits']:
            suit = self.__genSuitObject(self.zoneId, activeSuitInfo['type'], activeSuitInfo['track'], activeSuitInfo['level'], random.choice((0, 1, 2)))
            activeSuits.append(suit)

        suitHandles['activeSuits'] = activeSuits
        reserveSuits = []
        for reserveSuitInfo in floorInfo['reserveSuits']:
            suit = self.__genSuitObject(self.zoneId, reserveSuitInfo['type'], reserveSuitInfo['track'], reserveSuitInfo['level'], random.choice((0, 1, 2)))
            reserveSuits.append((suit, reserveSuitInfo['joinChance']))

        suitHandles['reserveSuits'] = reserveSuits
        return suitHandles

    def genSuitsForEmptyPlanner(self, specialCode):
        suitHandles = {}
        activeSuits = []
        reserveSuits = []
        MIN_LEVEL_BY_TYPE = {
            8: 8,
            7: 7,
            6: 6, 
            5: 5,
            4: 4, 
            3: 3,
            2: 2, 
            1: 1,
        }
        MAX_LEVEL_BY_TYPE = {
            1: 5,
            2: 6,
            3: 7,
            4: 12,
            5: 15,
            6: 15,
            7: 20,
            8: 50,
        }
        def suitKindFromLevel(level):
            possibleTypes = []

            for suitType in range(1, 9):
                minLevel = MIN_LEVEL_BY_TYPE.get(suitType, suitType)
                maxLevel = MAX_LEVEL_BY_TYPE.get(suitType, suitType + 4)

                if level >= minLevel and level <= maxLevel:
                    possibleTypes.append(suitType)

            if not possibleTypes:
                return 8

            return random.choice(possibleTypes)


        suitLevel = random.randint(15, 20)
        suitKind = self.__genNormalSuitType(suitLevel)
        if specialCode == 'ffm':
            miniboss = self.__genSuitObject(
                self.zoneId,
                bldgTrack='c',
                suitLevel=50,
                revives=0,
                suitName='f'
            ) # Placeholder
            activeSuits.append(miniboss)
        elif specialCode == 'stenog':
            miniboss = self.__genSuitObject(
                self.zoneId,
                bldgTrack='l',
                suitLevel=35,
                revives=0,
                suitName='stenog'
            )
            activeSuits.append(miniboss)
        elif specialCode == 'lgator':
            miniboss = self.__genSuitObject(
                self.zoneId,
                bldgTrack='l',
                suitLevel=40,
                revives=0,
                suitName='lgator'
            )
            activeSuits.append(miniboss)
        elif specialCode == 'caseman':
            miniboss = self.__genSuitObject(
                self.zoneId,
                bldgTrack='l',
                suitLevel=35,
                revives=0,
                suitName='caseman'
            )
            activeSuits.append(miniboss)
        elif specialCode == 'sgoat':
            miniboss = self.__genSuitObject(
                self.zoneId,
                bldgTrack='l',
                suitLevel=30,
                revives=0,
                suitName='sgoat'
            )
            activeSuits.append(miniboss)
        elif specialCode == 'lit':
            miniboss = self.__genSuitObject(
                self.zoneId,
                bldgTrack='c',
                suitLevel=50,
                revives=0,
                suitName='f'
            ) # Placeholder
            activeSuits.append(miniboss)
        elif specialCode == 'erclaimerfit':
            miniboss = self.__genSuitObject(
                self.zoneId,
                bldgTrack='m',
                suitLevel=20,
                revives=1,
                suitName='erfit'
            )

            miniboss2 = self.__genSuitObject(
                self.zoneId,
                bldgTrack='l',
                suitLevel=20,
                revives=1,
                suitName='erclaim'
            )

            suitLevel = random.randint(15, 20)
            suitType = SuitDNA.getSuitType(suitLevel)

            suit = self.__genSuitObject(
                self.zoneId,
                suitType=suitType,
                bldgTrack=random.choice(('c', 'm', 's', 'g', 'l', 't', 'p')),
                suitLevel=suitLevel,
                revives=0
            )

            suitLevel2 = random.randint(15, 20)
            suitType2 = SuitDNA.getSuitType(suitLevel2)

            suit2 = self.__genSuitObject(
                self.zoneId,
                suitType=suitType2,
                bldgTrack=random.choice(('c', 'm', 's', 'g', 'l', 't', 'p')),
                suitLevel=suitLevel2,
                revives=0
            )

            activeSuits.extend((
                miniboss,
                miniboss2,
                suit,
                suit2
            ))
        elif specialCode == 'litpair1':
            miniboss = self.__genSuitObject(
                self.zoneId,
                bldgTrack='l',
                suitLevel=40,
                revives=0,
                suitName='lgator'
            ) # Litigator
            miniboss2 = self.__genSuitObject(
                self.zoneId,
                bldgTrack='l',
                suitLevel=35,
                revives=0,
                suitName='stenog'
            ) # Stenographer
            activeSuits.append(miniboss)
            activeSuits.append(miniboss2)
        elif specialCode == 'litpair2':
            miniboss = self.__genSuitObject(
                self.zoneId,
                bldgTrack='l',
                suitLevel=40,
                revives=0,
                suitName='lgator'
            ) # Litigator
            miniboss2 = self.__genSuitObject(
                self.zoneId,
                bldgTrack='l',
                suitLevel=35,
                revives=0,
                suitName='caseman'
            ) # Case Manager
            activeSuits.append(miniboss)
            activeSuits.append(miniboss2)
        elif specialCode == 'litpair3':
            miniboss = self.__genSuitObject(
                self.zoneId,
                bldgTrack='l',
                suitLevel=40,
                revives=0,
                suitName='lgator'
            ) # Litigator
            miniboss2 = self.__genSuitObject(
                self.zoneId,
                bldgTrack='l',
                suitLevel=30,
                revives=0,
                suitName='sgoat'
            ) # Scapegoat
            activeSuits.append(miniboss)
            activeSuits.append(miniboss2)
        elif specialCode == 'litpair4':
            miniboss = self.__genSuitObject(
                self.zoneId,
                bldgTrack='l',
                suitLevel=35,
                revives=0,
                suitName='caseman'
            ) # Case Manager
            miniboss2 = self.__genSuitObject(
                self.zoneId,
                bldgTrack='l',
                suitLevel=35,
                revives=0,
                suitName='stenog'
            ) # Stenographer
            activeSuits.append(miniboss)
            activeSuits.append(miniboss2)
        elif specialCode == 'litpair5':
            miniboss = self.__genSuitObject(
                self.zoneId,
                bldgTrack='l',
                suitLevel=35,
                revives=0,
                suitName='caseman'
            ) # Case Manager
            miniboss2 = self.__genSuitObject(
                self.zoneId,
                bldgTrack='l',
                suitLevel=30,
                revives=0,
                suitName='sgoat'
            ) # Scapegoat
            activeSuits.append(miniboss)
            activeSuits.append(miniboss2)
        elif specialCode == 'litpair6':
            miniboss = self.__genSuitObject(
                self.zoneId,
                bldgTrack='l',
                suitLevel=30,
                revives=0,
                suitName='sgoat'
            ) # Scapegoat
            miniboss2 = self.__genSuitObject(
                self.zoneId,
                bldgTrack='l',
                suitLevel=35,
                revives=0,
                suitName='stenog'
            ) # Stenographer
            activeSuits.append(miniboss)
            activeSuits.append(miniboss2)
        elif specialCode == 'blitpair1':
            miniboss = self.__genSuitObject(
                self.zoneId,
                bldgTrack='c',
                suitLevel=48,
                revives=0,
                suitName='ambass'
            ) # Ambassador
            miniboss2 = self.__genSuitObject(
                self.zoneId,
                bldgTrack='c',
                suitLevel=44,
                revives=0,
                suitName='wtapper'
            ) # Wiretapper
            activeSuits.append(miniboss)
            activeSuits.append(miniboss2)
        elif specialCode == 'blitpair2':
            miniboss = self.__genSuitObject(
                self.zoneId,
                bldgTrack='c',
                suitLevel=48,
                revives=0,
                suitName='ambass'
            ) # Ambassador
            miniboss2 = self.__genSuitObject(
                self.zoneId,
                bldgTrack='c',
                suitLevel=44,
                revives=0,
                suitName='bkeeper'
            ) # Commissioner
            activeSuits.append(miniboss)
            activeSuits.append(miniboss2)
        elif specialCode == 'blitpair3':
            miniboss = self.__genSuitObject(
                self.zoneId,
                bldgTrack='c',
                suitLevel=48,
                revives=0,
                suitName='ambass'
            ) # Ambassador
            miniboss2 = self.__genSuitObject(
                self.zoneId,
                bldgTrack='c',
                suitLevel=38,
                revives=0,
                suitName='phouse'
            ) # Powerhouse
            activeSuits.append(miniboss)
            activeSuits.append(miniboss2)
        elif specialCode == 'blitpair4':
            miniboss = self.__genSuitObject(
                self.zoneId,
                bldgTrack='c',
                suitLevel=44,
                revives=0,
                suitName='wtapper'
            ) # Wiretapper
            miniboss2 = self.__genSuitObject(
                self.zoneId,
                bldgTrack='c',
                suitLevel=44,
                revives=0,
                suitName='bkeeper'
            ) # Commissioner
            activeSuits.append(miniboss)
            activeSuits.append(miniboss2)
        elif specialCode == 'blitpair5':
            miniboss = self.__genSuitObject(
                self.zoneId,
                bldgTrack='c',
                suitLevel=44,
                revives=0,
                suitName='wtapper'
            ) # Wiretapper
            miniboss2 = self.__genSuitObject(
                self.zoneId,
                bldgTrack='c',
                suitLevel=38,
                revives=0,
                suitName='phouse'
            ) # Powerhouse
            activeSuits.append(miniboss)
            activeSuits.append(miniboss2)
        elif specialCode == 'blitpair6':
            miniboss = self.__genSuitObject(
                self.zoneId,
                bldgTrack='c',
                suitLevel=38,
                revives=0,
                suitName='phouse'
            ) # Powerhouse
            miniboss2 = self.__genSuitObject(
                self.zoneId,
                bldgTrack='c',
                suitLevel=44,
                revives=0,
                suitName='bkeeper'
            ) # Commissioner
            activeSuits.append(miniboss)
            activeSuits.append(miniboss2)
        elif specialCode == 'slitpair1':
            miniboss = self.__genSuitObject(
                self.zoneId,
                bldgTrack='s',
                suitLevel=45,
                revives=0,
                suitName='safesupervis'
            ) # Pressurizer
            miniboss2 = self.__genSuitObject(
                self.zoneId,
                bldgTrack='s',
                suitLevel=40,
                revives=0,
                suitName='ubuster'
            ) # Union Buster
            activeSuits.append(miniboss)
            activeSuits.append(miniboss2)
        elif specialCode == 'slitpair2':
            miniboss = self.__genSuitObject(
                self.zoneId,
                bldgTrack='s',
                suitLevel=45,
                revives=0,
                suitName='safesupervis'
            ) # Pressurizer
            miniboss2 = self.__genSuitObject(
                self.zoneId,
                bldgTrack='s',
                suitLevel=35,
                revives=0,
                suitName='hustle'
            ) # Traffic Manager
            activeSuits.append(miniboss)
            activeSuits.append(miniboss2)
        elif specialCode == 'slitpair3':
            miniboss = self.__genSuitObject(
                self.zoneId,
                bldgTrack='s',
                suitLevel=45,
                revives=0,
                suitName='safesupervis'
            ) # Pressurizer
            miniboss2 = self.__genSuitObject(
                self.zoneId,
                bldgTrack='s',
                suitLevel=40,
                revives=0,
                suitName='radiog'
            ) # Radiographer
            activeSuits.append(miniboss)
            activeSuits.append(miniboss2)
        elif specialCode == 'slitpair4':
            miniboss = self.__genSuitObject(
                self.zoneId,
                bldgTrack='s',
                suitLevel=35,
                revives=0,
                suitName='hustle'
            ) # Traffic Manager
            miniboss2 = self.__genSuitObject(
                self.zoneId,
                bldgTrack='s',
                suitLevel=40,
                revives=0,
                suitName='radiog'
            ) # Radiographer
            activeSuits.append(miniboss)
            activeSuits.append(miniboss2)
        elif specialCode == 'slitpair5':
            miniboss = self.__genSuitObject(
                self.zoneId,
                bldgTrack='s',
                suitLevel=35,
                revives=0,
                suitName='hustle'
            ) # Traffic Manager
            miniboss2 = self.__genSuitObject(
                self.zoneId,
                bldgTrack='s',
                suitLevel=40,
                revives=0,
                suitName='ubuster'
            ) # Union Buster
            activeSuits.append(miniboss)
            activeSuits.append(miniboss2)
        elif specialCode == 'slitpair6':
            miniboss = self.__genSuitObject(
                self.zoneId,
                bldgTrack='s',
                suitLevel=40,
                revives=0,
                suitName='ubuster'
            ) # Union Buster
            miniboss2 = self.__genSuitObject(
                self.zoneId,
                bldgTrack='s',
                suitLevel=40,
                revives=0,
                suitName='radiog'
            ) # Radiographer
            activeSuits.append(miniboss)
            activeSuits.append(miniboss2)
        elif specialCode == 'bdlitpair1':
            miniboss = self.__genSuitObject(
                self.zoneId,
                bldgTrack='g',
                suitLevel=66,
                revives=0,
                suitName='cdirector'
            ) # Contingency Director
            miniboss2 = self.__genSuitObject(
                self.zoneId,
                bldgTrack='g',
                suitLevel=60,
                revives=0,
                suitName='rkeeper'
            ) # Recordkeeper
            activeSuits.append(miniboss)
            activeSuits.append(miniboss2)
        elif specialCode == 'bdlitpair2':
            miniboss = self.__genSuitObject(
                self.zoneId,
                bldgTrack='g',
                suitLevel=66,
                revives=0,
                suitName='cdirector'
            ) # Contingency Director
            miniboss2 = self.__genSuitObject(
                self.zoneId,
                bldgTrack='g',
                suitLevel=60,
                revives=0,
                suitName='dking'
            ) # Dividend King
            activeSuits.append(miniboss)
            activeSuits.append(miniboss2)
        elif specialCode == 'bdlitpair3':
            miniboss = self.__genSuitObject(
                self.zoneId,
                bldgTrack='g',
                suitLevel=56,
                revives=0,
                suitName='liquid'
            ) # Tollmaster
            miniboss2 = self.__genSuitObject(
                self.zoneId,
                bldgTrack='g',
                suitLevel=60,
                revives=0,
                suitName='rkeeper'
            ) # Recordkeeper
            activeSuits.append(miniboss)
            activeSuits.append(miniboss2)
        elif specialCode == 'bdlitpair4':
            miniboss = self.__genSuitObject(
                self.zoneId,
                bldgTrack='g',
                suitLevel=60,
                revives=0,
                suitName='dking'
            ) # Dividend King
            miniboss2 = self.__genSuitObject(
                self.zoneId,
                bldgTrack='g',
                suitLevel=60,
                revives=0,
                suitName='rkeeper'
            ) # Recordkeeper
            activeSuits.append(miniboss)
            activeSuits.append(miniboss2)
        elif specialCode == 'bdlitpair5':
            miniboss = self.__genSuitObject(
                self.zoneId,
                bldgTrack='g',
                suitLevel=56,
                revives=0,
                suitName='liquid'
            ) # Tollmaster
            miniboss2 = self.__genSuitObject(
                self.zoneId,
                bldgTrack='g',
                suitLevel=60,
                revives=0,
                suitName='dking'
            ) # Dividend King
            activeSuits.append(miniboss)
            activeSuits.append(miniboss2)
        elif specialCode == 'bdlitpair6':
            miniboss = self.__genSuitObject(
                self.zoneId,
                bldgTrack='g',
                suitLevel=56,
                revives=0,
                suitName='liquid'
            ) # Tollmaster
            miniboss2 = self.__genSuitObject(
                self.zoneId,
                bldgTrack='g',
                suitLevel=66,
                revives=0,
                suitName='cdirector'
            ) # Contingency Director
            activeSuits.append(miniboss)
            activeSuits.append(miniboss2)
        elif specialCode == 'ambassador':
            miniboss = self.__genSuitObject(
                self.zoneId,
                bldgTrack='c',
                suitLevel=48,
                revives=0,
                suitName='f'
            ) # Placeholder
            activeSuits.append(miniboss)
        elif specialCode == 'directors':
            miniboss = self.__genSuitObject(
                self.zoneId,
                bldgTrack='g',
                suitLevel=25,
                revives=1,
                suitName='derrhand'
            ) # Derrick Hand
            miniboss2 = self.__genSuitObject(
                self.zoneId,
                bldgTrack='s',
                suitLevel=30,
                revives=1,
                suitName='dopa'
            ) # DOPA
            miniboss3 = self.__genSuitObject(
                self.zoneId,
                bldgTrack='g',
                suitLevel=25,
                revives=1,
                suitName='dold'
            ) # DOLD
            activeSuits.append(miniboss)
            activeSuits.append(miniboss2)
            activeSuits.append(miniboss3)
        elif specialCode == 'lit2':
            miniboss = self.__genSuitObject(
                self.zoneId,
                bldgTrack='l',
                suitLevel=50,
                revives=1,
                suitName='wsi'
            ) # Witness Stand-In
            miniboss2 = self.__genSuitObject(
                self.zoneId,
                bldgTrack='l',
                suitLevel=20,
                revives=1,
                suitName='redd'
            ) # Redd Heir Wing
            activeSuits.append(miniboss)
            activeSuits.append(miniboss2)
        elif specialCode == 'oclo1':
            miniboss = self.__genSuitObject(
                self.zoneId,
                bldgTrack='c',
                suitLevel=50,
                revives=0,
                suitName='f'
            ) # Placeholder
            activeSuits.append(miniboss)
        elif specialCode == 'ffm2':
            miniboss = self.__genSuitObject(
                self.zoneId,
                bldgTrack='c',
                suitLevel=50,
                revives=0,
                suitName='f'
            ) # Placeholder
            activeSuits.append(miniboss)
        elif specialCode == 'crf1':
            miniboss = self.__genSuitObject(
                self.zoneId,
                bldgTrack='m',
                suitLevel=100,
                revives=0,
                suitName='hroller'
            )
            activeSuits.append(miniboss)
        elif specialCode == 'videog':
            miniboss = self.__genSuitObject(
                self.zoneId,
                bldgTrack='t',
                suitLevel=99,
                revives=0,
                suitName='videog'
            )
            activeSuits.append(miniboss)
        elif specialCode == 'pace':
            miniboss = self.__genSuitObject(
                self.zoneId,
                bldgTrack='s',
                suitLevel=66,
                revives=0,
                suitName='psetter'
            )
            activeSuits.append(miniboss)
        elif specialCode == 'crf2':
            miniboss = self.__genSuitObject(
                self.zoneId,
                bldgTrack='c',
                suitLevel=50,
                revives=0,
                suitName='f'
            ) # Placeholder
            activeSuits.append(miniboss)
        elif specialCode == 'gtk':
            miniboss = self.__genSuitObject(
                self.zoneId,
                bldgTrack='c',
                suitLevel=50,
                revives=0,
                suitName='f'
            ) # Placeholder
            activeSuits.append(miniboss)
        suitHandles['activeSuits'] = activeSuits
        suitHandles['reserveSuits'] = reserveSuits
        return suitHandles

    def genReserveSuits(self, specialCode = 'ffm'):
        suitHandles = {}
        reserveSuits = []
        MIN_LEVEL_BY_TYPE = {
            14: 8,   # Big Wig tier can spawn at level 8+
            13: 7,
            12: 7,
            11: 6,
            10: 6,
            9: 5,
            8: 5,
            7: 3,
            6: 4, 
            5: 4,
            4: 3, 
            3: 2,
            2: 2, 
            1: 1,
        }
        MAX_LEVEL_BY_TYPE = {
            1: 5,
            2: 6,
            3: 8,
            4: 10,
            5: 10,
            6: 12,
            7: 14,
            8: 15,
            9: 20,
            10: 20,
            11: 20,
            12: 25,
            13: 25,
            14: 50,
        }
        def suitKindFromLevel(level):
            possibleTypes = []

            for suitType in range(1, 15):
                minLevel = MIN_LEVEL_BY_TYPE.get(suitType, suitType)
                maxLevel = MAX_LEVEL_BY_TYPE.get(suitType, suitType + 4)

                if level >= minLevel and level <= maxLevel:
                    possibleTypes.append(suitType)

            if not possibleTypes:
                return 14

            return random.choice(possibleTypes)


        suitLevel = random.randint(10, 20)
        suitKind = suitKindFromLevel(suitLevel)

        suitLevelHighRoller = random.randint(1, 35)
        suitKindHighRoller = suitKindFromLevel(suitLevelHighRoller)

        suitLevel3 = random.randint(1, 31)
        suitKind3 = suitKindFromLevel(suitLevel3)

        suitLevelWSI = random.randint(10, 20)
        suitKindWSI = suitKindFromLevel(suitLevelWSI)

        suitLevel2 = random.randint(7, 15)
        suitKind2 = suitKindFromLevel(suitLevel2)

        suitLevelDesperation = random.randint(15, 25)
        suitKindDesperation = suitKindFromLevel(suitLevelDesperation)

        suitLevelNormal = random.randint(10, 20)
        suitKindNormal = suitKindFromLevel(suitLevelNormal)

        suitLevelErfit1 = random.randint(10, 14)
        suitKindErfit1 = suitKindFromLevel(suitLevelErfit1)
        suitLevelErfit2 = random.randint(12, 16)
        suitKindErfit2 = suitKindFromLevel(suitLevelErfit2)
        suitLevelErfit3 = random.randint(14, 18)
        suitKindErfit3 = suitKindFromLevel(suitLevelErfit3)
        suitLevelErfit4 = random.randint(16, 20)
        suitKindErfit4 = suitKindFromLevel(suitLevelErfit4)
        suitLevelErfit5 = random.randint(20, 30)
        suitKindErfit5 = suitKindFromLevel(suitLevelErfit5)
        suitLevelErclaim = random.randint(10, 15)
        suitKindErclaim = suitKindFromLevel(suitLevelErclaim)
        suitLevelErclaim2 = random.randint(15, 20)
        suitKindErclaim2 = suitKindFromLevel(suitLevelErclaim)
        if specialCode == 'erfit1':
            dept = random.choice(('c', 'm', 's', 'g', 'l', 't', 'p'))
            suitLevel = random.randint(10, 14)
            suitType = SuitDNA.getRandomSuitTierSpawn(suitLevel, dept)

            suit = self.__genSuitObject(
                self.zoneId,
                suitType=suitType,
                bldgTrack=dept,
                suitLevel=suitLevel,
                revives=0,
            skelecogChance=100
            )
            reserveSuits.append(suit)
        if specialCode == 'erfit2':
            dept = random.choice(('c', 'm', 's', 'g', 'l', 't', 'p'))
            suitLevel = random.randint(12, 16)
            suitType = SuitDNA.getRandomSuitTierSpawn(suitLevel, dept)

            suit = self.__genSuitObject(
                self.zoneId,
                suitType=suitType,
                bldgTrack=dept,
                suitLevel=suitLevel,
                revives=0,
            skelecogChance=100
            )
            reserveSuits.append(suit)
        if specialCode == 'erfit3':
            dept = random.choice(('c', 'm', 's', 'g', 'l', 't', 'p'))
            suitLevel = random.randint(14, 18)
            suitType = SuitDNA.getRandomSuitTierSpawn(suitLevel, dept)

            suit = self.__genSuitObject(
                self.zoneId,
                suitType=suitType,
                bldgTrack=dept,
                suitLevel=suitLevel,
                revives=0,
            skelecogChance=100
            )
            reserveSuits.append(suit)
        if specialCode == 'erfit4':
            dept = random.choice(('c', 'm', 's', 'g', 'l', 't', 'p'))
            suitLevel = random.randint(16, 20)
            suitType = SuitDNA.getRandomSuitTierSpawn(suitLevel, dept)

            suit = self.__genSuitObject(
                self.zoneId,
                suitType=suitType,
                bldgTrack=dept,
                suitLevel=suitLevel,
                revives=0,
            skelecogChance=100
            )
            reserveSuits.append(suit)
        if specialCode == 'erfit5':
            dept = random.choice(('c', 'm', 's', 'g', 'l', 't', 'p'))
            suitLevel = random.randint(20, 30)
            suitType = SuitDNA.getRandomSuitTierSpawn(suitLevel, dept)

            suit = self.__genSuitObject(
                self.zoneId,
                suitType=suitType,
                bldgTrack=dept,
                suitLevel=suitLevel,
                revives=0,
            skelecogChance=100
            )
            reserveSuits.append(suit)
        if specialCode == 'erclaim':
            dept = random.choice(('c', 'm', 's', 'g', 'l', 't', 'p'))
            suitLevel = random.randint(10, 15)
            suitType = SuitDNA.getRandomSuitTierSpawn(suitLevel, dept)

            suit = self.__genSuitObject(
                self.zoneId,
                suitType=suitType,
                bldgTrack=dept,
                suitLevel=suitLevel,
                revives=0,
            skelecogChance=100
            )
            reserveSuits.append(suit)
        if specialCode == 'erclaim2':
            dept = random.choice(('c', 'm', 's', 'g', 'l', 't', 'p'))
            suitLevel = random.randint(15, 25)
            suitType = SuitDNA.getRandomSuitTierSpawn(suitLevel, dept)

            suit = self.__genSuitObject(
                self.zoneId,
                suitType=suitType,
                bldgTrack=dept,
                suitLevel=suitLevel,
                revives=0,
            skelecogChance=100
            )
            reserveSuits.append(suit)
        if specialCode == 'paceGrunts':
            dept = random.choice(('c', 'm', 's', 'g', 'l', 't', 'p'))
            suitLevel = random.randint(10, 25)
            suitType = SuitDNA.getRandomSuitTierSpawn(suitLevel, dept)

            suit = self.__genSuitObject(
                self.zoneId,
                suitType=suitType,
                bldgTrack=dept,
                suitLevel=suitLevel,
                revives=0
            )
            reserveSuits.append(suit)
        if specialCode == 'crf':
            # generate random cashbot from lv 12 to 20
            suit = self.__genSuitObject(self.zoneId, 25, 'm', 25, 0)
            suit2 = self.__genSuitObject(self.zoneId, 20, 's', 20, 1)
            suit3 = self.__genSuitObject(self.zoneId, 27, 'm', 27, 0)
            reserveSuits.append(random.choice((suit, suit2, suit3)))
        if specialCode == 'lit':
            # litigation
            suitLevel = random.randint(10, 20)
            suitType = SuitDNA.getRandomSuitTierSpawn(suitLevel, 'l')

            suit = self.__genSuitObject(
                self.zoneId,
                suitType=suitType,
                bldgTrack='l',
                suitLevel=suitLevel,
                revives=0
            )
            reserveSuits.append(suit)
        if specialCode == 'litDesperation':
            # litigation
            suitLevel = random.randint(15, 25)
            suitType = SuitDNA.getRandomSuitTierSpawn(suitLevel, 'l')

            suit = self.__genSuitObject(
                self.zoneId,
                suitType=suitType,
                bldgTrack='l',
                suitLevel=suitLevel,
                revives=0
            )
            reserveSuits.append(suit)
        if specialCode == 'amb':
            # litigation
            suitLevel = random.randint(10, 20)
            suitType = SuitDNA.getRandomSuitTierSpawn(suitLevel, 'c')

            suit = self.__genSuitObject(
                self.zoneId,
                suitType=suitType,
                bldgTrack='c',
                suitLevel=suitLevel,
                revives=0
            )
            reserveSuits.append(suit)
        if specialCode == 'ambDesperation':
            # litigation
            suitLevel = random.randint(15, 25)
            suitType = SuitDNA.getRandomSuitTierSpawn(suitLevel, 'c')

            suit = self.__genSuitObject(
                self.zoneId,
                suitType=suitType,
                bldgTrack='c',
                suitLevel=suitLevel,
                revives=0
            )
            reserveSuits.append(suit)
        if specialCode == 'pres':
            # litigation
            suitLevel = random.randint(10, 20)
            suitType = SuitDNA.getRandomSuitTierSpawn(suitLevel, 's')

            suit = self.__genSuitObject(
                self.zoneId,
                suitType=suitType,
                bldgTrack='s',
                suitLevel=suitLevel,
                revives=0
            )
            reserveSuits.append(suit)
        if specialCode == 'presDesperation':
            # litigation
            suitLevel = random.randint(15, 25)
            suitType = SuitDNA.getRandomSuitTierSpawn(suitLevel, 's')

            suit = self.__genSuitObject(
                self.zoneId,
                suitType=suitType,
                bldgTrack='s',
                suitLevel=suitLevel,
                revives=0
            )
            reserveSuits.append(suit)
        if specialCode == 'bdlit':
            # litigation
            suitLevel = random.randint(10, 20)
            suitType = SuitDNA.getRandomSuitTierSpawn(suitLevel, 'g')

            suit = self.__genSuitObject(
                self.zoneId,
                suitType=suitType,
                bldgTrack='g',
                suitLevel=suitLevel,
                revives=0
            )
            reserveSuits.append(suit)
        if specialCode == 'bdlitDesperation':
            # litigation
            suitLevel = random.randint(15, 25)
            suitType = SuitDNA.getRandomSuitTierSpawn(suitLevel, 'g')

            suit = self.__genSuitObject(
                self.zoneId,
                suitType=suitType,
                bldgTrack='g',
                suitLevel=suitLevel,
                revives=0
            )
            reserveSuits.append(suit)
        if specialCode == 'lit2':
            # witness stand-in
            dept = random.choice(('c', 'm', 's', 'g', 'l', 't', 'p'))
            suitLevel = random.randint(10, 25)
            suitType = SuitDNA.getRandomSuitTierSpawn(suitLevel, dept)

            suit = self.__genSuitObject(
                self.zoneId,
                suitType=suitType,
                bldgTrack=dept,
                suitLevel=suitLevel,
                revives=0
            )
            reserveSuits.append(suit)
        if specialCode == 'phantom':
            miniboss = self.__genSuitObject(
                self.zoneId,
                bldgTrack='g',
                suitLevel=30,
                revives=0,
                suitName='cbutcher'
            )
            reserveSuits.append(miniboss)
        if specialCode == 'dking':
            miniboss = self.__genSuitObject(
                self.zoneId,
                bldgTrack='g',
                suitLevel=60,
                revives=0,
                suitName='dking'
            )
            reserveSuits.append(miniboss)
        if specialCode == 'cdirector':
            miniboss = self.__genSuitObject(
                self.zoneId,
                bldgTrack='g',
                suitLevel=66,
                revives=0,
                suitName='cdirector'
            )
            reserveSuits.append(miniboss)
        if specialCode == 'rkeeper':
            miniboss = self.__genSuitObject(
                self.zoneId,
                bldgTrack='g',
                suitLevel=60,
                revives=0,
                suitName='rkeeper'
            )
            reserveSuits.append(miniboss)
        if specialCode == 'liquid':
            miniboss = self.__genSuitObject(
                self.zoneId,
                bldgTrack='g',
                suitLevel=56,
                revives=0,
                suitName='liquid'
            )
            reserveSuits.append(miniboss)
        if specialCode == 'ubuster':
            miniboss = self.__genSuitObject(
                self.zoneId,
                bldgTrack='s',
                suitLevel=40,
                revives=0,
                suitName='ubuster'
            )
            reserveSuits.append(miniboss)
        if specialCode == 'safesupervis':
            miniboss = self.__genSuitObject(
                self.zoneId,
                bldgTrack='s',
                suitLevel=45,
                revives=0,
                suitName='safesupervis'
            )
            reserveSuits.append(miniboss)
        if specialCode == 'racket':
            miniboss = self.__genSuitObject(
                self.zoneId,
                bldgTrack='s',
                suitLevel=35,
                revives=0,
                suitName='hustle'
            )
            reserveSuits.append(miniboss)
        if specialCode == 'radiog':
            miniboss = self.__genSuitObject(
                self.zoneId,
                bldgTrack='s',
                suitLevel=40,
                revives=0,
                suitName='radiog'
            )
            reserveSuits.append(miniboss)
        if specialCode == 'wtapper':
            miniboss = self.__genSuitObject(
                self.zoneId,
                bldgTrack='c',
                suitLevel=44,
                revives=0,
                suitName='wtapper'
            )
            reserveSuits.append(miniboss)
        if specialCode == 'ambass':
            miniboss = self.__genSuitObject(
                self.zoneId,
                bldgTrack='c',
                suitLevel=48,
                revives=0,
                suitName='ambass'
            )
            reserveSuits.append(miniboss)
        if specialCode == 'bkeeper':
            miniboss = self.__genSuitObject(
                self.zoneId,
                bldgTrack='c',
                suitLevel=44,
                revives=0,
                suitName='bkeeper'
            )
            reserveSuits.append(miniboss)
        if specialCode == 'phouse':
            miniboss = self.__genSuitObject(
                self.zoneId,
                bldgTrack='c',
                suitLevel=38,
                revives=0,
                suitName='phouse'
            )
            reserveSuits.append(miniboss)
        if specialCode == 'stenog':
            miniboss = self.__genSuitObject(
                self.zoneId,
                bldgTrack='l',
                suitLevel=35,
                revives=0,
                suitName='stenog'
            )
            reserveSuits.append(miniboss)
        if specialCode == 'lgator':
            miniboss = self.__genSuitObject(
                self.zoneId,
                bldgTrack='l',
                suitLevel=40,
                revives=0,
                suitName='lgator'
            )
            reserveSuits.append(miniboss)
        if specialCode == 'caseman':
            miniboss = self.__genSuitObject(
                self.zoneId,
                bldgTrack='l',
                suitLevel=35,
                revives=0,
                suitName='caseman'
            )
            reserveSuits.append(miniboss)
        if specialCode == 'sgoat':
            miniboss = self.__genSuitObject(
                self.zoneId,
                bldgTrack='l',
                suitLevel=30,
                revives=0,
                suitName='sgoat'
            )
            reserveSuits.append(miniboss)
        if specialCode == 'hrollerPhase3':
            miniboss = self.__genSuitObject(
                self.zoneId,
                bldgTrack='m',
                suitLevel=100,
                revives=0,
                suitName='hroller2'
            )
            reserveSuits.append(miniboss)
        if specialCode == 'videogPhase2':
            miniboss = self.__genSuitObject(
                self.zoneId,
                bldgTrack='t',
                suitLevel=99,
                revives=0,
                suitName='videog'
            )
            reserveSuits.append(miniboss)
        if specialCode == 'std':
            suit = self.__genSuitObject(
                self.zoneId,
                bldgTrack='s',
                suitLevel=25,
                revives=0,
                suitName='std2'
            )
            reserveSuits.append(suit)
        if specialCode == 'mh':
            suit = self.__genSuitObject(
                self.zoneId,
                bldgTrack='s',
                suitLevel=25,
                revives=0,
                suitName='mh2'
            )
            reserveSuits.append(suit)
        if specialCode == 'cnd':
            suit = self.__genSuitObject(
                self.zoneId,
                bldgTrack='s',
                suitLevel=25,
                revives=0,
                suitName='cnd2'
            )
            reserveSuits.append(suit)
        if specialCode == 'ffm2':
            suit = self.__genSuitObject(self.zoneId, 17, 't', random.randint(17, 20), 0)
            reserveSuits.append(suit)
        if specialCode == 'ffm':
            suit = self.__genSuitObject(self.zoneId, suitKind, 's', suitLevel, 0)
            reserveSuits.append(suit)
        if specialCode == 'crf1':
            suit = self.__genRandomUncappedSuit(
                1,
                35,
                bldgTrack=random.choice(('c', 'm', 'l', 'p', 't', 'g', 's')),
                revives=0
            )
            reserveSuits.append(suit)
        if specialCode == 'crfMinigame':
            suit = self.__genRandomUncappedSuit(
                1,
                20,
                bldgTrack=random.choice(('c', 'm', 'l', 'p', 't', 'g', 's')),
                revives=0
            )
            reserveSuits.append(suit)
        if specialCode == 'crf2':
            suit = self.__genSuitObject(self.zoneId, 27, 'm', random.randint(27, 36), 0)
            reserveSuits.append(suit)
        if specialCode == 'sil1':
            suit = self.__genSuitObject(
                self.zoneId,
                bldgTrack='m',
                suitLevel=25,
                revives=0,
                suitName='hrollers'
            )
            reserveSuits.append(suit)
        if specialCode == 'sil2':
            suit = self.__genSuitObject(
                self.zoneId,
                bldgTrack='m',
                suitLevel=26,
                revives=0,
                suitName='hrollers'
            )
            reserveSuits.append(suit)
        if specialCode == 'sil3':
            suit = self.__genSuitObject(
                self.zoneId,
                bldgTrack='m',
                suitLevel=27,
                revives=0,
                suitName='hrollers'
            )
            reserveSuits.append(suit)
        if specialCode == 'sil4':
            suit = self.__genSuitObject(
                self.zoneId,
                bldgTrack='m',
                suitLevel=28,
                revives=0,
                suitName='hrollers'
            )
            reserveSuits.append(suit)
        if specialCode == 'sil5':
            suit = self.__genSuitObject(
                self.zoneId,
                bldgTrack='m',
                suitLevel=29,
                revives=0,
                suitName='hrollers'
            )
            reserveSuits.append(suit)
        if specialCode == 'sil6':
            suit = self.__genSuitObject(
                self.zoneId,
                bldgTrack='m',
                suitLevel=30,
                revives=0,
                suitName='hrollers'
            )
            reserveSuits.append(suit)
        if specialCode == 'sil7':
            suit = self.__genSuitObject(
                self.zoneId,
                bldgTrack='m',
                suitLevel=31,
                revives=0,
                suitName='hrollers'
            )
            reserveSuits.append(suit)
        if specialCode == 'sil8':
            suit = self.__genSuitObject(
                self.zoneId,
                bldgTrack='m',
                suitLevel=32,
                revives=0,
                suitName='hrollers'
            )
            reserveSuits.append(suit)
        if specialCode == 'sil9':
            suit = self.__genSuitObject(
                self.zoneId,
                bldgTrack='m',
                suitLevel=33,
                revives=0,
                suitName='hrollers'
            )
            reserveSuits.append(suit)
        if specialCode == 'sil10':
            suit = self.__genSuitObject(
                self.zoneId,
                bldgTrack='m',
                suitLevel=34,
                revives=0,
                suitName='hrollers'
            )
            reserveSuits.append(suit)
        if specialCode == 'sil11':
            suit = self.__genSuitObject(
                self.zoneId,
                bldgTrack='m',
                suitLevel=35,
                revives=0,
                suitName='hrollers'
            )
            reserveSuits.append(suit)
        if specialCode == 'sil12':
            suit = self.__genSuitObject(
                self.zoneId,
                bldgTrack='m',
                suitLevel=36,
                revives=0,
                suitName='hrollers'
            )
            reserveSuits.append(suit)
        if specialCode == 'videog':
            suit = self.__genSuitObject(
                self.zoneId,
                bldgTrack='s',
                suitLevel=25,
                revives=0,
                suitName='std2'
            )
            suit2 = self.__genSuitObject(
                self.zoneId,
                bldgTrack='s',
                suitLevel=25,
                revives=0,
                suitName='cnd2'
            )
            suit3 = self.__genSuitObject(
                self.zoneId,
                bldgTrack='s',
                suitLevel=25,
                revives=0,
                suitName='mh2'
            )
            reserveSuits.append(random.choice((suit, suit2, suit3)))
        if specialCode == 'videoPhase1':
            suit = self.__genSuitObject(
                self.zoneId,
                bldgTrack='c',
                suitLevel=random.randint(10, 20),
                revives=0,
                suitName=random.choice(('txl', 'ksp', 'tbc'))
            )
            suit2 = self.__genSuitObject(
                self.zoneId,
                bldgTrack='l',
                suitLevel=random.randint(10, 20),
                revives=0,
                suitName=random.choice(('le', 'le2', 'bw', 'bw2', 'magi', 'whistleb', 'br'))
            )
            suit3 = self.__genSuitObject(
                self.zoneId,
                bldgTrack='m',
                suitLevel=random.randint(10, 20),
                revives=0,
                suitName=random.choice(('rb', 'timer'))
            )
            suit4 = self.__genSuitObject(
                self.zoneId,
                bldgTrack='s',
                suitLevel=random.randint(10, 20),
                revives=0,
                suitName=random.choice(('mh', 'cnd', 'std', 'm'))
            )
            suit5 = self.__genSuitObject(
                self.zoneId,
                bldgTrack='g',
                suitLevel=random.randint(10, 20),
                revives=0,
                suitName=random.choice(('mg', 'hho', 'chw'))
            )
            suit6 = self.__genSuitObject(
                self.zoneId,
                bldgTrack='t',
                suitLevel=random.randint(10, 20),
                revives=0,
                suitName=random.choice(('rus', 'rus2', 'itn'))
            )
            suit7 = self.__genSuitObject(
                self.zoneId,
                bldgTrack='p',
                suitLevel=random.randint(10, 20),
                revives=0,
                suitName=random.choice(('nsh', 'anc'))
            )
            reserveSuits.append(random.choice((suit, suit2, suit3, suit4, suit5, suit6, suit7)))
        if specialCode == 'videog4':
            suit = self.__genSuitObject(
                self.zoneId,
                bldgTrack='t',
                suitLevel=33,
                revives=0,
                suitName='bcaster'
            )
            suit2 = self.__genSuitObject(
                self.zoneId,
                bldgTrack='c',
                suitLevel=28,
                revives=0,
                suitName='mplayers'
            )
            reserveSuits.append(suit)
            reserveSuits.append(suit2)
        if specialCode == 'choreo':
            suit = self.__genSuitObject(
                self.zoneId,
                bldgTrack='c',
                suitLevel=26,
                revives=0,
                suitName='choreo'
            )
            reserveSuits.append(suit)
        if specialCode == 'cinema':
            suit = self.__genSuitObject(
                self.zoneId,
                bldgTrack='s',
                suitLevel=26,
                revives=0,
                suitName='cinema'
            )
            reserveSuits.append(suit)
        if specialCode == 'fmaker':
            suit = self.__genSuitObject(
                self.zoneId,
                bldgTrack='g',
                suitLevel=26,
                revives=0,
                suitName='fmaker'
            )
            reserveSuits.append(suit)
        if specialCode == 'director':
            suit = self.__genSuitObject(
                self.zoneId,
                bldgTrack='p',
                suitLevel=30,
                revives=0,
                suitName='director'
            )
            reserveSuits.append(suit)
        if specialCode == 'videog2':
            suit = self.__genSuitObject(
                self.zoneId,
                bldgTrack='s',
                suitLevel=25,
                revives=0,
                suitName='std2'
            )
            suit2 = self.__genSuitObject(
                self.zoneId,
                bldgTrack='s',
                suitLevel=25,
                revives=0,
                suitName='cnd2'
            )
            suit3 = self.__genSuitObject(
                self.zoneId,
                bldgTrack='s',
                suitLevel=25,
                revives=0,
                suitName='mh2'
            )
            reserveSuits.append(random.choice((suit, suit2, suit3)))
        if specialCode == 'videog3':
            suit2 = self.__genSuitObject(self.zoneId, 17, 'p', 17, 0)
            suit3 = self.__genSuitObject(self.zoneId, 19, 't', 19, 0)
            suit = self.__genSuitObject(self.zoneId, 22, 'c', 22, 0)
            suit4 = self.__genSuitObject(self.zoneId, 23, 's', 23, 0)
            reserveSuits.append(suit3)
            reserveSuits.append(suit)
            reserveSuits.append(suit2)
            reserveSuits.append(suit4)
        if specialCode == 'gtk':
            # generate random bossbot from lv 12 to 20
            suit = self.__genSuitObject(self.zoneId, suitKind, random.choice(('c', 'm', 's', 'g', 'l', 't', 'p')), suitLevel, 0)
            reserveSuits.append(suit)
        if specialCode == 'gtk2':
            # generate random bossbot from lv 12 to 20
            suit = self.__genSuitObject(self.zoneId, suitKind, random.choice(('c', 'm', 's', 'g', 'l', 't', 'p')), suitLevel, 0)
            reserveSuits.append(suit)

        suitHandles['reserveSuits'] = reserveSuits
        return suitHandles

    def genSuits(self):
        suitHandles = []
        for floor in range(len(self.suitInfos)):
            floorSuitHandles = self.genFloorSuits(floor)
            suitHandles.append(floorSuitHandles)

        return suitHandles