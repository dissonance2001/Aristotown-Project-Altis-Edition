import math
import time

from direct.showbase.DirectObject import DirectObject

from typing import Dict, Tuple, TYPE_CHECKING

from toontown.club import ClubGlobals

if TYPE_CHECKING:
    from toontown.club.DistributedClubManagerUD import DistributedClubManagerUD
    from toontown.club.ClubsServiceUD import ClubsServiceUD
    from toontown.uberdog.ToonTrackerUD import ToonTrackerUD
    from toontown.uberdog.ToontownUberRepository import ToontownUberRepository


class ClubCoinServiceUD(DirectObject):
    """
    A UD-sided object in charge of handling ClubCoin announcements for Clubs.
    """
    BATCH_UPDATES = 3       # How many Clubs receive Club Coin notifs
    BATCH_DELAY   = 0.50    # The delay between batches

    def __init__(self, air):
        self.air = air  # type: ToontownUberRepository

        # Keep track of the start & end coins that Clubs are accumulating.
        self._clubStartCoins = dict()  # type: Dict[int, float]
        self._clubEndCoins   = dict()  # type: Dict[int, float]
        self._batch          = dict()  # type: Dict[int, Tuple[float, float]]

        # Run a task for sending out the crypto notifications
        self._startCoinsTask()

    """
    Property access
    """

    @property
    def _clubMgr(self):
        """:rtype: DistributedClubManagerUD"""
        return self.air.clubsManager

    @property
    def _clubService(self):
        """:rtype: ClubsServiceUD"""
        return self.air.clubsService

    @property
    def _toonTracker(self):
        """:rtype: ToonTrackerUD"""
        return self.air.toonTracker

    """
    Buisness logic
    """

    def fileTaxes(self, clubId: int, startCoin: float, earnings: float):
        """
        Marks a Club for when they start earning coins.
        """
        if clubId not in self._clubStartCoins:
            # Declare the start for tracking coin tallys.
            self._clubStartCoins[clubId] = startCoin
            self._clubEndCoins[clubId] = startCoin + earnings
        else:
            # Add the earning to the end coin amount.
            self._clubEndCoins[clubId] += earnings

    """
    Task loops
    """

    def _startCoinsTask(self):
        """Begin the coin task."""
        period = ClubGlobals.ClubCoinAnnouncementPeriod
        currTime = time.time()

        # Get the time we need to wait before starting the task.
        timeBeforeTask = ((currTime // period) * period) + period - currTime

        # Begin the announcement chain.
        self.doMethodLater(
            delayTime=timeBeforeTask,
            funcOrTask=self._taskLoop,
            name='ClubCoinServiceUD_TaskLoop',
        )

    def _taskLoop(self, task):
        # Make the batch and start the batch task.
        self._makeBatch()
        self.addTask(
            funcOrTask=self._batchLoop,
            name='ClubCoinServiceUD_BatchLoop'
        )

        # Refresh the task loop. Make sure it's accurate !
        self.doMethodLater(
            delayTime=2.0,
            funcOrTask=self._startCoinsTask, extraArgs=[],
            name='ClubCoinServiceUD_RefreshTaskLoop',
        )
        return task.done

    """
    Batch announcements
    """

    def _makeBatch(self):
        """Creates the batches for calculating update amounts."""
        self._batch = {
            clubId: (self._clubStartCoins.get(clubId, 0.0), self._clubEndCoins.get(clubId, 0.0))
            for clubId in self._clubStartCoins.keys()
        }

    def _batchLoop(self, task):
        # Go through the first few values in the batch.
        updatesSent = 0
        for clubId in tuple(self._batch.keys()):
            # Break if we've sent all the batches we can this task.
            if updatesSent >= self.BATCH_UPDATES:
                break

            # Calculate the coins to send.
            oldCoin, newCoin = self._batch[clubId]
            coinDiff = max(0, math.floor(newCoin) - math.floor(oldCoin))

            # Send the batch update if necessary.
            if coinDiff > 0:
                self._clubMgr.sendClubCoinReport(clubId=clubId, coins=coinDiff)
                updatesSent += 1

            # Remove the clubId from the batch.
            if clubId in self._batch:
                del self._batch[clubId]
            if clubId in self._clubStartCoins:
                del self._clubStartCoins[clubId]
            if clubId in self._clubEndCoins:
                del self._clubEndCoins[clubId]

        # Check to see if we need to run it again.
        if self._batch:
            # We have updates yet to be sent, prepare for another call
            task.delayTime = self.BATCH_DELAY
            return task.again
        else:
            # Batch cleared
            return task.done
