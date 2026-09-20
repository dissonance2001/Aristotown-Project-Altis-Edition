from direct.task.Timer import *

from toontown.clashbattle.battle.BattleGlobals import *
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class BattleBase:
    # This defines the points where the suits will stand in battle.
    # For each number of suits in the battle (1 to 6), the
    # corresponding element of suitPoints is a list of n (pos, heading)
    # pairs for each of the n suits to stand.
    suitPoints = (
        ((Point3(0, 5, 0), 179),),
        ((Point3(2, 5.3, 0), 170), (Point3(-2, 5.3, 0), 180)),
        ((Point3(4, 5.2, 0), 170), (Point3(0, 6, 0), 179), (Point3(-4, 5.2, 0), 190)),
        ((Point3(6, 4.4, 0), 160), (Point3(2, 6.3, 0), 170), (Point3(-2, 6.3, 0), 190), 
         (Point3(-6, 4.4, 0), 200),),
        ((Point3(8, 3.8, 0), 160), (Point3(4, 5.4, 0), 170), (Point3(0, 6, 0), 179), 
         (Point3(-4, 5.4, 0), 190), (Point3(-8, 3.8, 0), 200)),
        ((Point3(10, 3.3, 0), 150), (Point3(6, 5.3, 0), 160), (Point3(2, 6.3, 0), 170), 
         (Point3(-2, 6.3, 0), 190), (Point3(-6, 5.3, 0), 200), (Point3(-10, 3.3, 0), 210)),
    )

    # And this defines the single set of points for suits who are
    # "pending": they have joined the battle, but are waiting for the
    # next round to begin before they take their place.
    suitPendingPoints = (
        (Point3(4, 8.2, 0), 170),
        (Point3(0, 9, 0), 179),
        (Point3(-4, 8.2, 0), 190),
        (Point3(-8, 7.4, 0), 200),
        (Point3(8, 7.4, 0), 160),
        (Point3(12, 7.4, 0), 150),
    )

    # This is similar to the above, but for toons instead of suits.
    toonPoints = (
        ((Point3(0, -6, 0), 0),),
        ((Point3(1.5, -6.5, 0), 5), (Point3(-1.5, -6.5, 0), -5)),
        ((Point3(3, -6.75, 0), 5), (Point3(0, -7, 0), 0), (Point3(-3, -6.75, 0), -5)),
        ((Point3(4.5, -7, 0), 10), (Point3(1.5, -7.5, 0), 5), (Point3(-1.5, -7.5, 0), -5), (Point3(-4.5, -7, 0), -10),),
    )

    toonPendingPoints = (
        (Point3(-3, -8, 0), -5),
        (Point3(0, -9, 0), 0),
        (Point3(3, -8, 0), 5),
        (Point3(5.5, -5.5, 0), 20),
    )

    # These define the points on the perimeter of the battle circle
    # for suits and toons who are "joining"; this allows the avatar to
    # walk a circle around the battle to get to its pending point,
    # defined above.
    posA = Point3(0, 10, 0)
    posB = Point3(-7.071, 7.071, 0)
    posC = Point3(-10, 0, 0)
    posD = Point3(-7.071, -7.071, 0)
    posE = Point3(0, -10, 0)
    posF = Point3(7.071, -7.071, 0)
    posG = Point3(10, 0, 0)
    posH = Point3(7.071, 7.071, 0)
    allPoints = (posA, posB, posC, posD, posE, posF, posG, posH)
    toonCwise = [posA, posB, posC, posD, posE]
    toonCCwise = [posH, posG, posF, posE]
    suitCwise = [posE, posF, posG, posH, posA]
    suitCCwise = [posD, posC, posB, posA]

    suitSpeed = 4.8
    toonSpeed = 8.0

    def __init__(self):
        self.pos = Point3(0, 0, 0)
        self.initialSuitPos = Point3(0, 1, 0)
        self.timer = Timer()
        self.resetLists()

    def resetLists(self):
        self.suits = []
        self.luredSuits = []
        self.suitGone = 0

        self.toons = []
        self.toonGone = 0

        # keep track of toons who helped, so we know which toons just passed all the time
        self.helpfulToons = []
        self.toonRoundParticipation = {}

    def calcFaceoffTime(self, centerpos, suitpos):
        facing = Vec3(centerpos - suitpos)
        facing.normalize()
        suitdest = Point3(centerpos - Point3(facing * 6.0))
        dist = Vec3(suitdest - suitpos).length()
        return dist / BattleBase.suitSpeed

    def calcSuitMoveTime(self, pos0, pos1):
        dist = Vec3(pos0 - pos1).length()
        return dist / BattleBase.suitSpeed

    def calcToonMoveTime(self, pos0, pos1):
        dist = Vec3(pos0 - pos1).length()
        return dist / BattleBase.toonSpeed

    def buildJoinPointList(self, avPos, destPos, toon=0):
        """ buildJoinPointList(avPos, destPos, toon)

        This function is called when suits or toons ask to join the
        battle and need to figure out how to walk to their selected
        pending point (destPos).  It builds a list of points the
        avatar should walk through in order to get there.  If the list
        is empty, the avatar will walk straight there.
        """
        # In the default case, avatars walk around the perimeter of
        # the battle cell to get to their target point.  Figure out
        # the shortest path around the circle.

        # First, find the closest battle join point
        minDist = 999999.0
        nearestP = None
        for p in BattleBase.allPoints:
            dist = Vec3(avPos - p).length()
            if dist < minDist:
                nearestP = p
                minDist = dist

        self.notify.debug("buildJoinPointList() - avp: %s nearp: %s" % (avPos, nearestP))

        # See if destPos is the closest point
        dist = Vec3(avPos - destPos).length()
        if dist < minDist:
            self.notify.debug("buildJoinPointList() - destPos is nearest")
            return []

        if toon == 1:
            if nearestP == BattleBase.posE:
                self.notify.debug("buildJoinPointList() - posE")
                plist = [BattleBase.posE]
            elif BattleBase.toonCwise.count(nearestP) == 1:
                self.notify.debug("buildJoinPointList() - clockwise")
                index = BattleBase.toonCwise.index(nearestP)
                plist = BattleBase.toonCwise[index + 1 :]
            else:
                self.notify.debug("buildJoinPointList() - counter-clockwise")
                index = BattleBase.toonCCwise.index(nearestP)
                plist = BattleBase.toonCCwise[index + 1 :]
        elif nearestP == BattleBase.posA:
            self.notify.debug("buildJoinPointList() - posA")
            plist = [BattleBase.posA]
        elif BattleBase.suitCwise.count(nearestP) == 1:
            self.notify.debug("buildJoinPointList() - clockwise")
            index = BattleBase.suitCwise.index(nearestP)
            plist = BattleBase.suitCwise[index + 1 :]
        else:
            self.notify.debug("buildJoinPointList() - counter-clockwise")
            index = BattleBase.suitCCwise.index(nearestP)
            plist = BattleBase.suitCCwise[index + 1 :]
        self.notify.debug("buildJoinPointList() - plist: %s" % plist)
        return plist

    def addHelpfulToon(self, toonId):
        """Add toonId to our helpful toons, make sure it's in the list at most once."""
        if toonId not in self.helpfulToons:
            self.helpfulToons.append(toonId)

    def incrementToonParticipation(self, toonId):
        """Increment a toonId's round participation."""
        if toonId not in self.toonRoundParticipation:
            self.toonRoundParticipation[toonId] = 1
        else:
            self.toonRoundParticipation[toonId] += 1

    """
    Getters
    """

    def getToonPoint(self, numToons, index, **kwargs):
        return self.toonPoints[numToons][index]

    def getSuitPoint(self, numSuits, index, **kwargs):
        return self.suitPoints[numSuits][index]
    
    """
    Properties
    """

    @property
    def aliveSuits(self):
        return [suit for suit in self.activeSuits if suit.getHp() > 0]

    @property
    def activeSuits(self):
        return [suit for suit in self.suits if suit.getBattleState() == BattleStateEnum.ACTIVE]
    
    @property
    def pendingSuits(self):
        return [suit for suit in self.suits if suit.getBattleState() == BattleStateEnum.PENDING]
    
    @property
    def joiningSuits(self):
        return [suit for suit in self.suits if suit.getBattleState() == BattleStateEnum.JOINING]
    
    @property
    def joiningNotPendingSuits(self):
        return [suit for suit in self.suits if suit.getBattleState() == BattleStateEnum.JOINING_NOT_PENDING]
