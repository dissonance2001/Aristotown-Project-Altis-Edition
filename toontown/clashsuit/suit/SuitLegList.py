from toontown.dna.DNAParser import DNASuitPoint
from toontown.clashsuit.suit import SuitTimings
from toontown.toonbase import ToontownGlobals
from bisect import bisect_left

class SuitLeg:
    TWalkFromStreet = 0
    TWalkToStreet = 1
    TWalk = 2
    TFromSky = 3
    TToSky = 4
    TFromSuitBuilding = 5
    TToSuitBuilding = 6
    TToToonBuilding = 7
    TFromCogHQ = 8
    TToCogHQ = 9
    TOff = 10
    TWalkHidden = 11
    TypeToName = {
        TWalkFromStreet: 'WalkFromStreet',
        TWalkToStreet: 'WalkToStreet',
        TWalk: 'Walk',
        TFromSky: 'FromSky',
        TToSky: 'ToSky',
        TFromSuitBuilding: 'FromSuitBuilding',
        TToSuitBuilding: 'ToSuitBuilding',
        TToToonBuilding: 'ToToonBuilding',
        TFromCogHQ: 'FromCogHQ',
        TToCogHQ: 'ToCogHQ',
        TOff: 'Off',
        TWalkHidden: 'Walk',
    }

    def __init__(self, startTime, zoneId, blockNumber, pointA, pointB, type):
        self.startTime = startTime
        self.zoneId = zoneId
        self.blockNumber = blockNumber
        self.pointA = pointA
        self.pointB = pointB
        self.type = type

        self.posA = self.pointA.getPos()
        self.posB = self.pointB.getPos()

        distance = (self.posB - self.posA).length()
        self.legTime = distance / ToontownGlobals.SuitWalkSpeed
        self.endTime = self.startTime + self.getLegTime()

    def getStartTime(self):
        return self.startTime

    def getZoneId(self):
        """
        :returns: the current zone ID.
        :rtype: int
        """
        return self.zoneId

    def getBlockNumber(self):
        return self.blockNumber

    def getPointA(self):
        return self.pointA

    def getPointB(self):
        return self.pointB

    def getType(self):
        return self.type

    def getPosA(self):
        return self.posA

    def getPosB(self):
        return self.posB

    def getLegTime(self):
        if self.type in (SuitLeg.TWalk, SuitLeg.TWalkFromStreet,
                         SuitLeg.TWalkToStreet, SuitLeg.TWalkHidden):
            return self.legTime
        if self.type == SuitLeg.TFromSky:
            return SuitTimings.fromSky
        if self.type == SuitLeg.TToSky:
            return SuitTimings.toSky
        if self.type == SuitLeg.TFromSuitBuilding:
            return SuitTimings.fromSuitBuilding
        if self.type == SuitLeg.TToSuitBuilding:
            return SuitTimings.toSuitBuilding
        if self.type in (SuitLeg.TToToonBuilding, SuitLeg.TToCogHQ):
            return SuitTimings.toToonBuilding
        if self.type == SuitLeg.TFromCogHQ:
            return SuitTimings.fromCogHQ
        
        return 0.0

    def getEndTime(self):
        return self.endTime

    def getPosAtTime(self, time):
        if self.type in (SuitLeg.TFromSky, SuitLeg.TFromSuitBuilding,
                         SuitLeg.TFromCogHQ):
            return self.posA
        elif self.type in (SuitLeg.TToSky, SuitLeg.TToSuitBuilding,
                           SuitLeg.TToToonBuilding, SuitLeg.TToCogHQ,
                           SuitLeg.TOff):
            return self.posB

        delta = self.posB - self.posA
        return self.posA + (delta * (time/self.getLegTime()))

    def getTypeName(self):
        if self.type in SuitLeg.TypeToName:
            return SuitLeg.TypeToName[self.type]
        
        return '**invalid**'


class SuitLegList:

    def __init__(self, path, dnaStore):
        self.path = path
        self.dnaStore = dnaStore

        self.legs = []
        self.legEndTimes = []

        # First, add the initial SuitLeg:
        self.add(self.path.getPoint(0), self.path.getPoint(1), self.getFirstLegType())

        # Next, connect each of the points in our path through SuitLegs:
        for i in range(self.path.getNumPoints() - 1):
            pointA = self.path.getPoint(i)
            pointB = self.path.getPoint(i + 1)
            pointTypeA = pointA.getPointType()
            pointTypeB = pointB.getPointType()
            legType = self.getLegType(pointTypeA, pointTypeB)

            if pointTypeA == DNASuitPoint.COGHQ_OUT_POINT:
                # We're going out of a door, so we'll need to insert a door
                # leg before the move:
                self.add(pointA, pointB, SuitLeg.TFromCogHQ)

            self.add(pointA, pointB, legType)

            if pointTypeB == DNASuitPoint.COGHQ_IN_POINT:
                # We're going into a door, so we'll need to insert a door leg
                # after the move:
                self.add(pointA, pointB, SuitLeg.TToCogHQ)

        # Add the last SuitLeg:
        numPoints = self.path.getNumPoints()
        pointA = self.path.getPoint(numPoints - 2)
        pointB = self.path.getPoint(numPoints - 1)
        self.add(pointA, pointB, self.getLastLegType())

        # Finally, take down the suit:
        self.add(pointA, pointB, SuitLeg.TOff)

    def add(self, pointA, pointB, legType):
        zoneId = self.dnaStore.getSuitEdgeZone(pointA.getIndex(), pointB.getIndex())
        landmarkBuildingIndex = pointB.getLandmarkBuildingIndex()
        if landmarkBuildingIndex == -1:
            landmarkBuildingIndex = pointA.getLandmarkBuildingIndex()
        startTime = 0.0
        if len(self.legs) > 0:
            startTime = self.legs[-1].getEndTime()
        leg = SuitLeg(startTime, zoneId, landmarkBuildingIndex, pointA, pointB, legType)
        self.legs.append(leg)
        self.legEndTimes.append(leg.getEndTime())

    def getFirstLegType(self):
        if self.path.getPoint(0).getPointType() == DNASuitPoint.SIDE_DOOR_POINT:
            return SuitLeg.TFromSuitBuilding
        else:
            return SuitLeg.TFromSky

    def getLegType(self, pointTypeA, pointTypeB):
        if pointTypeA in (DNASuitPoint.FRONT_DOOR_POINT,
                          DNASuitPoint.SIDE_DOOR_POINT):
            return SuitLeg.TWalkToStreet
        if pointTypeB in (DNASuitPoint.FRONT_DOOR_POINT,
                          DNASuitPoint.SIDE_DOOR_POINT):
            return SuitLeg.TWalkFromStreet
        if DNASuitPoint.HIDDEN_STREET_POINT in (pointTypeA, pointTypeB):
            return SuitLeg.TWalkHidden
        return SuitLeg.TWalk

    def getLastLegType(self):
        endPoint = self.path.getPoint(self.path.getNumPoints() - 1)
        endPointType = endPoint.getPointType()
        if endPointType == DNASuitPoint.FRONT_DOOR_POINT:
            return SuitLeg.TToToonBuilding
        if endPointType == DNASuitPoint.SIDE_DOOR_POINT:
            return SuitLeg.TToSuitBuilding
        
        return SuitLeg.TToSky

    def getNumLegs(self):
        return len(self.legs)

    def getLeg(self, index):
        return self.legs[index]

    def getType(self, index):
        return self.legs[index].getType()

    def getLegTime(self, index):
        return self.legs[index].getLegTime()

    def getZoneId(self, index):
        return self.legs[index].getZoneId()

    def getBlockNumber(self, index):
        return self.legs[index].getBlockNumber()

    def getPointA(self, index):
        return self.legs[index].getPointA()

    def getPointB(self, index):
        return self.legs[index].getPointB()

    def getStartTime(self, index):
        return self.legs[index].getStartTime()

    def getLegIndexAtTime(self, time, low=0):
        legIndex = bisect_left(self.legEndTimes, time, lo=low if low >= 0 else 0)
        if legIndex == len(self.legs):
            legIndex -= 1
        return legIndex

    def isPointInRange(self, point, lowTime, highTime):
        legIndex = self.getLegIndexAtTime(lowTime)
        while legIndex < self.getNumLegs():
            leg = self.legs[legIndex]
            if leg.getEndTime() > highTime:
                break
            if (leg.pointA == point) or (leg.pointB == point):
                return True
            legIndex += 1
        return False
