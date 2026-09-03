from direct.distributed import DistributedObject
from panda3d.core import Vec3
from direct.task import Task
from typing import TYPE_CHECKING

from toontown.utils.DirectNotifyCategory import DirectNotifyCategory

if TYPE_CHECKING:
    from toontown.distributed.ToontownClientRepository import ToontownClientRepository
    from toontown.fishing.DistributedPondBingoManager import DistributedPondBingoManager


@DirectNotifyCategory()
class DistributedFishingPond(DistributedObject.DistributedObject):
    """
    DistributedFishingPond(DistributedObject)
    """

    pollInterval = 0.5

    def __init__(self, cr):
        """
        :param ToontownClientRepository cr: The client repository which maintains all client-side distributed objects.
        """
        DistributedObject.DistributedObject.__init__(self, cr)
        self.notify.debug('init')
        self.targets = {}
        self.area = None
        self.localToonBobPos = None
        self.localToonSpot = None
        self.pondBingoMgr = None

        # This is necessary because we must restore the castGui bucket
        # and jar to their proper positions once Bingo Night ends.
        # We must know each spot that the localToon visited at the pond.
        self.visitedSpots = {}
        return

    def disable(self):
        self.visitedSpots.clear()
        self.stopCheckingTargets()
        DistributedObject.DistributedObject.disable(self)

    def setArea(self, area):
        self.area = area

    def getArea(self):
        return self.area

    def addTarget(self, target):
        self.notify.debug('addTarget: %s' % target)
        self.targets[target.getDoId()] = target

    def removeTarget(self, target):
        self.notify.debug('removeTarget: %s' % target)
        del self.targets[target.getDoId()]

    def startCheckingTargets(self, spot, bobPos):
        self.notify.debug('startCheckingTargets')
        self.localToonSpot = spot
        self.localToonBobPos = bobPos

        # Slight delay before checking for the first time
        taskMgr.doMethodLater(self.pollInterval * 2, self.checkTargets, self.taskName('checkTargets'))

    def stopCheckingTargets(self):
        self.notify.debug('stopCheckingTargets')
        taskMgr.remove(self.taskName('checkTargets'))
        self.localToonBobPos = None
        return

    def checkTargets(self, task = None):
        """
        Do a distance check against all the targets in the pond.
        If we hit one of the targets, send an update to the AI and return 1
        Otherwise just return 0

        :return: 1 | 0
        """
        self.notify.debug('checkTargets')
        if self.localToonSpot is not None:
            for target in list(self.targets.values()):
                targetPos = target.getPos(render)
                distVec = Vec3(targetPos - self.localToonBobPos)
                dist = distVec.length()
                if dist < target.getRadius():
                    self.notify.debug('checkTargets: hit target: %s' % target.getDoId())
                    self.d_hitTarget(target)
                    return Task.done

            # Check again later
            taskMgr.doMethodLater(self.pollInterval, self.checkTargets, self.taskName('checkTargets'))
        else:
            # Not sure why this is happening.
            self.notify.warning('localToonSpot became None while checking targets')
        return Task.done

    def d_hitTarget(self, target):
        self.localToonSpot.hitTarget()
        self.sendUpdate('hitTarget', [target.getDoId()])

    def setPondBingoManager(self, pondBingoMgr):
        """
        This method sets the reference to a PondBingoManager instance.

        :type pondBingoMgr: DistributedPondBingoManager
        """
        self.pondBingoMgr = pondBingoMgr

    def removePondBingoManager(self):
        """
        This method deletes the reference to the PBMgrAI for this pond.

        This is called whenever Bingo Night closes and the PBMgrAI is ending.
        """
        del self.pondBingoMgr
        self.pondBingoMgr = None
        return

    def getPondBingoManager(self):
        """
        This method returns the reference to a PondBingoManager instance.

        :return: The pondBingoManager object that is associated with the pond instance
        """
        return self.pondBingoMgr

    def hasPondBingoManager(self):
        """
        This method determines if the pond has a PBMgr and returns the result.

        :return: result 1 if there is a PBMgr or 0
        """
        return (self.pondBingoMgr and [1] or [0])[0]

    def handleBingoCatch(self, catch):
        """
        This method sets the last catch of the BingoManager to the last fish caught by the client.

        :param catch: Last Fish caught by the client.
        """
        if self.pondBingoMgr:
            self.pondBingoMgr.setLastCatch(catch)

    def handleBingoBoot(self):
        """
        This method calls the handleBoot method of the BingoManager because the client caught a boot.
        """
        if self.pondBingoMgr:
            self.pondBingoMgr.handleBoot()

    def cleanupBingoMgr(self):
        """
        This method tells the BingoManager to cleanup because the corresponding client has left the FishingSpot.
        """
        if self.pondBingoMgr:
            self.pondBingoMgr.cleanup()

    def setLocalToonSpot(self, spot = None):
        """
        Purpose: This method sets the fishing spot for which the the local avatar has entered.

        Note: Initially, this was set only when the pond needed to check for targets during the 'fishing' state
        """
        self.localToonSpot = spot
        if spot is not None and spot.getDoId() not in self.visitedSpots:
            self.visitedSpots[spot.getDoId()] = spot
        return

    def showBingoGui(self):
        """
        This method tells the PondBingoManager to display the Bingo GUI.
        """
        if self.pondBingoMgr:
            self.pondBingoMgr.showCard()

    def getLocalToonSpot(self):
        """
        This method returns the current localToonSpot.

        :return: Fishing Spot where the local toon of the avatar is found.
        """
        return self.localToonSpot

    def resetSpotGui(self):
        """
        This method resets the CastGui (Bucket and Jar) for each pond that the local toon visited during Bingo Night.

        During Bingo Night, the bucket and jar are moved to the far left of the screen.

        This resets their normal positions for normal fishing.
        """
        for spot in list(self.visitedSpots.values()):
            spot.resetCastGui()

    def setSpotGui(self):
        """
        This method sets the spot Cast Gui for Bingo night.

        This is called whenever a toon is already fishing and bingo night starts.

        This tells the spot to play a sequence to move the bucket and jar to the far left on the screen.
        """
        for spot in list(self.visitedSpots.values()):
            spot.setCastGui()
