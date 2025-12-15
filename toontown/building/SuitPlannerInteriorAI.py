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

class SuitPlannerInteriorAI:
    notify = DirectNotifyGlobal.directNotify.newCategory('SuitPlannerInteriorAI')

    def __init__(self, numFloors, bldgLevel, bldgTrack, zone):
        self.dbg_4SuitsPerFloor = config.GetBool('4-suits-per-floor', 0)
        self.dbg_1SuitPerFloor = config.GetBool('1-suit-per-floor', 0)
        self.zoneId = zone
        self.numFloors = numFloors
        self.respectInvasions = 1
        dbg_defaultSuitName = simbase.config.GetString('suit-type', 'random')
        if dbg_defaultSuitName == 'random':
            self.dbg_defaultSuitType = None
        else:
            self.dbg_defaultSuitType = SuitDNA.getSuitType(dbg_defaultSuitName)
        if isinstance(bldgLevel, types.StringType):
            self.notify.warning('bldgLevel is a string!')
            bldgLevel = int(bldgLevel)
        
        self._genSuitInfos(numFloors, bldgLevel, bldgTrack)

    def __genJoinChances(self, num):
        joinChances = []
        for currChance in xrange(num):
            joinChances.append(random.randint(1, 100))

        joinChances.sort(cmp)
        return joinChances

    def _genSuitInfos(self, numFloors, bldgLevel, bldgTrack):
        self.suitInfos = []
        self.notify.debug('\n\ngenerating suitsInfos with numFloors (' + str(numFloors) + ') bldgLevel (' + str(bldgLevel) + '+1) and bldgTrack (' + str(bldgTrack) + ')')
        for currFloor in xrange(numFloors):
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
            for currActive in xrange(numActive - 1, -1, -1):
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
            for currReserve in xrange(numReserve):
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

    def __setupSuitInfo(self, suit, bldgTrack, suitLevel, suitType):
        suitDeptIndex, suitTypeIndex, flags = simbase.air.suitInvasionManager.getInvadingCog()
        if self.respectInvasions:
            if suitDeptIndex is not None:
                bldgTrack = SuitDNA.suitDepts[suitDeptIndex]
            if suitTypeIndex is not None:
                suitName = SuitDNA.getSuitName(suitDeptIndex, suitTypeIndex)
                suitType = SuitDNA.getSuitType(suitName)
                suitLevel = min(max(suitLevel, suitType), suitType + 4)
        dna = SuitDNA.SuitDNA()
        dna.newSuitRandom(suitType, bldgTrack)
        suit.dna = dna
        suit.setLevel(suitLevel)
        suit.setCog(1)
        if suit.dna.name in SuitBattleGlobals.SpecialCogDict:
            suit.setManager(1)
        #if random.randint(0, 100) <= ToontownBattleGlobals.V2_BASE_CHANCE and not suit.getManager() and not suit.dna.name == 'cg' and not suit.isSkeleton:
          #  suit.setSkeleRevives(random.choice((1, 2)))
        #if random.randint(0, 100) <= ToontownBattleGlobals.V2_BASE_CHANCE and suit.isSkeleton:
           # suit.setSkeleRevives(1)
        if suit.dna.name == 'autocad':
            suit.setExecutive(1)
        if suit.dna.name == 'chairp':
            suit.setExecutive(1)
        if suit.dna.name == 'watchm':
            suit.setExecutive(1)
        if suit.dna.name == 'ant':
            suit.setExecutive(1)
        if suit.dna.name == 'mh2':
            suit.setExecutive(1)
        if suit.dna.name == 'std2':
            suit.setExecutive(1)
        if random.randint(0, 100) <= ToontownBattleGlobals.EXECUTIVE_BASE_CHANCE and not suit.getManager() and not suit.dna.name == 'autocad' and not suit.dna.name == 'ant' and not suit.dna.name == 'chairp' and not suit.dna.name == 'mh2' and not suit.dna.name == 'ovt' and not suit.dna.name == 'watchm':
            suit.setExecutive(1)
        if random.randint(0, 100) <= ToontownBattleGlobals.GOVERNAUGHT_BASE_CHANCE and not suit.getManager() and not suit.getExecutive() and not suit.dna.name == 'ant' and not suit.dna.name == 'djockey' and not suit.dna.name == 'autocad' and not suit.dna.name == 'chairp' and not suit.dna.name == 'mh2' and not suit.dna.name == 'ovt' and not suit.dna.name == 'watchm':
            suit.setGovernaught(1)
        return flags

    def __genSuitObject(self, suitZone, suitType, bldgTrack, suitLevel, revives = 0):
        newSuit = DistributedSuitAI.DistributedSuitAI(simbase.air, None)
        #skel, exe = self.__setupSuitInfo(newSuit, bldgTrack, suitLevel, suitType)
        flags = self.__setupSuitInfo(newSuit, bldgTrack, suitLevel, suitType)
        if flags & IFSkelecog:
            newSuit.setSkelecog(1)
        newSuit.setSkeleRevives(revives)
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
            for currActive in xrange(len(currInfo[0])):
                self.notify.debug('  Active suit ' + str(currActive + 1) + ' is of type ' + str(currInfo[0][currActive][0]) + ' and of track ' + str(currInfo[0][currActive][1]) + ' and of level ' + str(currInfo[0][currActive][2]))

            self.notify.debug(' Floor ' + str(whichSuitInfo) + ' has ' + str(len(currInfo[1])) + ' reserve suits.')
            for currReserve in xrange(len(currInfo[1])):
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
        if specialCode == 'ffm':
            miniboss = self.__genSuitObject(self.zoneId, 24, 's', 24, 0)
            miniboss2 = self.__genSuitObject(self.zoneId, 27, 's', 27, 0)
            miniboss3 = self.__genSuitObject(self.zoneId, 26, 's', 26, 0)
            miniboss4 = self.__genSuitObject(self.zoneId, 25, 's', 25, 0)
            activeSuits.append(random.choice((miniboss, miniboss3)))
            activeSuits.append(random.choice((miniboss2, miniboss4)))
        elif specialCode == 'stenog':
            miniboss2 = self.__genSuitObject(self.zoneId, 27, 'l', 27, 0)
            activeSuits.append(miniboss2)
        elif specialCode == 'lgator':
            miniboss = self.__genSuitObject(self.zoneId, 28, 'l', 28, 0)
            activeSuits.append(miniboss)
        elif specialCode == 'caseman':
            miniboss3 = self.__genSuitObject(self.zoneId, 26, 'l', 26, 0)
            activeSuits.append(miniboss3)
        elif specialCode == 'sgoat':
            miniboss4 = self.__genSuitObject(self.zoneId, 25, 'l', 25, 0)
            activeSuits.append(miniboss4)
        elif specialCode == 'lit':
            pair1 = []
            pair2 = []
            pair3 = []
            pair4 = []
            pair5 = []
            pair6 = []
            miniboss = self.__genSuitObject(self.zoneId, 28, 'l', 28, 0) # Litigator
            miniboss2 = self.__genSuitObject(self.zoneId, 27, 'l', 27, 0) # Stenographer
            miniboss3 = self.__genSuitObject(self.zoneId, 26, 'l', 26, 0) # Case Manager
            miniboss4 = self.__genSuitObject(self.zoneId, 25, 'l', 25, 0) # Scapegoat
            pair1.append(miniboss)
            pair1.append(miniboss2)
            pair2.append(miniboss4)
            pair2.append(miniboss3)
            pair3.append(miniboss)
            pair3.append(miniboss3)
            pair4.append(miniboss4)
            pair4.append(miniboss2)
            pair5.append(miniboss)
            pair5.append(miniboss4)
            pair6.append(miniboss2)
            pair6.append(miniboss3)
            activeSuits.append(random.choice((pair1, pair2, pair3, pair4, pair5, pair6)))
        elif specialCode == 'litpair1':
            miniboss = self.__genSuitObject(self.zoneId, 28, 'l', 28, 0) # Litigator
            miniboss2 = self.__genSuitObject(self.zoneId, 27, 'l', 27, 0) # Stenographer
            activeSuits.append(miniboss)
            activeSuits.append(miniboss2)
        elif specialCode == 'litpair2':
            miniboss3 = self.__genSuitObject(self.zoneId, 26, 'l', 26, 0)  # Case Manager
            miniboss4 = self.__genSuitObject(self.zoneId, 25, 'l', 25, 0)  # Scapegoat
            activeSuits.append(miniboss3)
            activeSuits.append(miniboss4)
        elif specialCode == 'litpair3':
            miniboss = self.__genSuitObject(self.zoneId, 28, 'l', 28, 0)  # Litigator
            miniboss4 = self.__genSuitObject(self.zoneId, 25, 'l', 25, 0)  # Scapegoat
            activeSuits.append(miniboss)
            activeSuits.append(miniboss4)
        elif specialCode == 'litpair4':
            miniboss3 = self.__genSuitObject(self.zoneId, 26, 'l', 26, 0)  # Case Manager
            miniboss2 = self.__genSuitObject(self.zoneId, 27, 'l', 27, 0)  # Stenographer
            activeSuits.append(miniboss3)
            activeSuits.append(miniboss2)
        elif specialCode == 'litpair5':
            miniboss4 = self.__genSuitObject(self.zoneId, 25, 'l', 25, 0)  # Scapegoat
            miniboss2 = self.__genSuitObject(self.zoneId, 27, 'l', 27, 0)  # Stenographer
            activeSuits.append(miniboss4)
            activeSuits.append(miniboss2)
        elif specialCode == 'litpair6':
            miniboss3 = self.__genSuitObject(self.zoneId, 26, 'l', 26, 0)  # Case Manager
            miniboss = self.__genSuitObject(self.zoneId, 28, 'l', 28, 0)  # Litigator
            activeSuits.append(miniboss3)
            activeSuits.append(miniboss)
        elif specialCode == 'ambassador':
            miniboss = self.__genSuitObject(self.zoneId, 28, 'c', 28, 0)
            miniboss2 = self.__genSuitObject(self.zoneId, 27, 'c', 27, 0)
            miniboss3 = self.__genSuitObject(self.zoneId, 26, 'c', 26, 0)
            miniboss4 = self.__genSuitObject(self.zoneId, 25, 'c', 25, 0)
            activeSuits.append(miniboss)
            activeSuits.append(miniboss2)
            activeSuits.append(miniboss4)
            activeSuits.append(miniboss3)
        elif specialCode == 'directors':
            miniboss = self.__genSuitObject(self.zoneId, 17, 's', 17, 0)
            miniboss2 = self.__genSuitObject(self.zoneId, 19, 'g', 19, 0)
            miniboss3 = self.__genSuitObject(self.zoneId, 17, 'c', 17, 0)
            activeSuits.append(miniboss)
            activeSuits.append(miniboss2)
            activeSuits.append(miniboss3)
        elif specialCode == 'lit2':
            miniboss = self.__genSuitObject(self.zoneId, 24, 'l', 24, 1)
            miniboss2 = self.__genSuitObject(self.zoneId, 23, 'l', 23, 1)
            activeSuits.append(miniboss)
            activeSuits.append(miniboss2)
        elif specialCode == 'oclo1':
            miniboss = self.__genSuitObject(self.zoneId, 14, 'l', 22, 0)
            miniboss3 = self.__genSuitObject(self.zoneId, 12, 'l', 22, 0)
            miniboss2 = self.__genSuitObject(self.zoneId, 12, 'l', 23, 0)
            miniboss4 = self.__genSuitObject(self.zoneId, 14, 'l', 24, 0)
            miniboss5 = self.__genSuitObject(self.zoneId, 12, 'l', 17, 0)
            miniboss6 = self.__genSuitObject(self.zoneId, 14, 'l', 18, 0)
            activeSuits.append(random.choice((miniboss, miniboss2)))
            reserveSuits.append(random.choice((miniboss3, miniboss4, miniboss5, miniboss6)))
        elif specialCode == 'ffm2':
            miniboss2 = self.__genSuitObject(self.zoneId, 19, 's', 19, 0)
            miniboss3 = self.__genSuitObject(self.zoneId, 21, 's', 21, 0)
            miniboss4 = self.__genSuitObject(self.zoneId, 22, 's', 22, 0)
            activeSuits.append(miniboss4)
            activeSuits.append(random.choice((miniboss3, miniboss2)))
        elif specialCode == 'crf1':
            miniboss = self.__genSuitObject(self.zoneId, 25, 'm', 25, 0)
            activeSuits.append(miniboss)
        elif specialCode == 'crf2':
            miniboss = self.__genSuitObject(self.zoneId, 28, 'm', 28, 0)
            miniboss2 = self.__genSuitObject(self.zoneId, 20, 'p', 20, 0)
            suit = self.__genSuitObject(self.zoneId, 20, 's', 20, 0)
            suit4 = self.__genSuitObject(self.zoneId, 19, 'p', 19, 0)
            activeSuits.append(miniboss)
            activeSuits.append(miniboss2)
            activeSuits.append(suit)
            activeSuits.append(suit4)
        elif specialCode == 'videog':
            miniboss = self.__genSuitObject(self.zoneId, 23, 's', 23, 0)
            miniboss2 = self.__genSuitObject(self.zoneId, 20, 's', 20, 0)
            miniboss3 = self.__genSuitObject(self.zoneId, 20, 's', 20, 0)
            miniboss4 = self.__genSuitObject(self.zoneId, 20, 's', 20, 0)
            miniboss5 = self.__genSuitObject(self.zoneId, 20, 's', 20, 0)
            activeSuits.append(miniboss)
            activeSuits.append(miniboss2)
            activeSuits.append(miniboss3)
            activeSuits.append(miniboss4)
            activeSuits.append(miniboss5)
        elif specialCode == 'gtk':
            miniboss1 = self.__genSuitObject(self.zoneId, 27, 'c', 27, 0)
            miniboss2 = self.__genSuitObject(self.zoneId, 26, 'c', 26, 0)
            miniboss3 = self.__genSuitObject(self.zoneId, 28, 'c', 28, 0)
            activeSuits.append(miniboss1)
            activeSuits.append(miniboss2)
            activeSuits.append(miniboss3)
        suitHandles['activeSuits'] = activeSuits
        suitHandles['reserveSuits'] = reserveSuits
        return suitHandles

    def genReserveSuits(self, specialCode = 'ffm'):
        suitHandles = {}
        reserveSuits = []

        def suitKindFromLevel(level):
            if level >= 25:
                returnval = random.randint(14, 16)
            elif level >= 24:
                returnval = random.randint(13, 16)
            elif level >= 21:
                returnval = random.randint(12, 16)
            elif level >= 20:
                returnval = random.randint(11, 16)
            elif level >= 18:
                returnval = random.randint(10, 16)
            elif level >= 16:
                returnval = random.randint(9, 16)
            elif level >= 15:
                returnval = random.randint(9, 15)
            elif level >= 14:
                returnval = random.randint(7, 14)
            elif level >= 13:
                returnval = random.randint(7, 13)
            elif level >= 12:
                returnval = random.randint(7, 12)
            elif level >= 11:
                returnval = random.choice((5, 7, 8, 9, 10, 11))
            elif level >= 10:
                returnval = random.randint(5, 10)
            elif level >= 9:
                returnval = random.choice((3, 5, 6, 7, 8, 9))
            elif level >= 8:
                returnval = random.randint(3, 8)
            elif level >= 7:
                returnval = random.randint(3, 7)
            elif level >= 6:
                returnval = random.randint(2, 6)
            elif level >= 5:
                returnval = random.randint(1, 5)
            elif level >= 4:
                returnval = random.randint(1, 4)
            elif level >= 3:
                returnval = random.randint(1, 3)
            elif level >= 2:
                returnval = random.randint(1, 2)
            elif level == 1:
                returnval = 1
            else:
                returnval = 14

            return returnval

        suitLevel = random.randint(10, 31)
        suitLevel2 = random.randint(7, 15)
        suitKind = suitKindFromLevel(suitLevel)
        if specialCode == 'crf':
            # generate random cashbot from lv 12 to 20
            suit = self.__genSuitObject(self.zoneId, 25, 'm', 25, 0)
            suit2 = self.__genSuitObject(self.zoneId, 20, 's', 20, 1)
            suit3 = self.__genSuitObject(self.zoneId, 27, 'm', 27, 0)
            reserveSuits.append(random.choice((suit, suit2, suit3)))
        if specialCode == 'lit':
            # litigation
            suit = self.__genSuitObject(self.zoneId, suitKind, 'l', suitLevel, 0)
            reserveSuits.append(suit)
        if specialCode == 'lit2':
            # witness stand-in
            suit = self.__genSuitObject(self.zoneId, suitKind, random.choice(('c', 'm', 's', 'g', 'l', 't', 'p')), suitLevel, 0)
            reserveSuits.append(suit)
        if specialCode == 'stenog':
            miniboss2 = self.__genSuitObject(self.zoneId, 27, 'l', 27, 0)
            reserveSuits.append(miniboss2)
        if specialCode == 'lgator':
            miniboss = self.__genSuitObject(self.zoneId, 28, 'l', 28, 0)
            reserveSuits.append(miniboss)
        if specialCode == 'caseman':
            miniboss3 = self.__genSuitObject(self.zoneId, 26, 'l', 26, 0)
            reserveSuits.append(miniboss3)
        if specialCode == 'sgoat':
            miniboss4 = self.__genSuitObject(self.zoneId, 25, 'l', 25, 0)
            reserveSuits.append(miniboss4)
        if specialCode == 'ffm2':
            # generate random cashbot from lv 12 to 20
            suit = self.__genSuitObject(self.zoneId, 17, 't', random.randint(17, 20), 0)
            reserveSuits.append(suit)
        if specialCode == 'ffm':
            # generate random cashbot from lv 12 to 20
            suit = self.__genSuitObject(self.zoneId, suitKind, 's', suitLevel, 0)
            reserveSuits.append(suit)
        if specialCode == 'crf1':
            # generate random cashbot from lv 12 to 20
            suit = self.__genSuitObject(self.zoneId, suitKind, random.choice(('c', 'm', 's', 'g', 'l', 't', 'p')), suitLevel, 0)
            reserveSuits.append(suit)
        if specialCode == 'crf2':
            suit = self.__genSuitObject(self.zoneId, 27, 'm', random.randint(27, 36), 0)
            reserveSuits.append(suit)
        if specialCode == 'sil1':
            suit = self.__genSuitObject(self.zoneId, 27, 'm', random.choice((27, 29)), 0)
            reserveSuits.append(suit)
        if specialCode == 'sil2':
            suit = self.__genSuitObject(self.zoneId, 27, 'm', random.choice((28, 30)), 0)
            reserveSuits.append(suit)
        if specialCode == 'sil3':
            suit = self.__genSuitObject(self.zoneId, 27, 'm', random.choice((31, 32)), 0)
            reserveSuits.append(suit)
        if specialCode == 'sil4':
            suit = self.__genSuitObject(self.zoneId, 27, 'm', random.choice((33, 34)), 0)
            reserveSuits.append(suit)
        if specialCode == 'sil5':
            suit = self.__genSuitObject(self.zoneId, 27, 'm', random.choice((35, 36)), 0)
            reserveSuits.append(suit)
        if specialCode == 'videog':
            suit = self.__genSuitObject(self.zoneId, 20, 's', 20, 0)
            suit4 = self.__genSuitObject(self.zoneId, 19, 'p', 19, 0)
            reserveSuits.append(random.choice((suit, suit4)))
        if specialCode == 'videog4':
            suit = self.__genSuitObject(self.zoneId, 18, 'p', 18, 0)
            reserveSuits.append(suit)
        if specialCode == 'choreo':
            suit = self.__genSuitObject(self.zoneId, 17, 'p', 17, 0)
            reserveSuits.append(suit)
        if specialCode == 'cinema':
            suit = self.__genSuitObject(self.zoneId, 23, 's', 23, 0)
            reserveSuits.append(suit)
        if specialCode == 'fmaker':
            suit = self.__genSuitObject(self.zoneId, 22, 'g', 22, 0)
            reserveSuits.append(suit)
        if specialCode == 'director':
            suit = self.__genSuitObject(self.zoneId, 22, 'c', 22, 0)
            reserveSuits.append(suit)
        if specialCode == 'videog2':
            suit = self.__genSuitObject(self.zoneId, 20, 's', 20, 0)
            suit4 = self.__genSuitObject(self.zoneId, 19, 'p', 19, 0)
            reserveSuits.append(random.choice((suit, suit4)))
        if specialCode == 'videog3':
            suit2 = self.__genSuitObject(self.zoneId, 17, 'p', 17, 0)
            suit3 = self.__genSuitObject(self.zoneId, 22, 'g', 22, 0)
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
        for floor in xrange(len(self.suitInfos)):
            floorSuitHandles = self.genFloorSuits(floor)
            suitHandles.append(floorSuitHandles)

        return suitHandles