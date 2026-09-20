import datetime
import time

from direct.showbase.MessengerGlobal import messenger
from direct.task.TaskManagerGlobal import taskMgr, Task

from toontown.booster import BoosterGlobals
from toontown.inventory.enums.ItemEnums import MaterialItemType
from toontown.quest3.kudos.KudosConstants import KUDOS_RESET_INTERVAL, RANK_REQUIREMENTS, getKudosRank, LOOPING_KUDOS, \
    MAXIMUM_KUDOS, getKudosRankupGumballAmount
from toontown.quest3.questlines.KudosQuestLine import KudosSafezoneIdToTier
from toontown.time import TimeUtil
from toontown.toon.DistributedToonAI import DistributedToonAI
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class KudosManagerAI:
    """Handles everything related to kudos, which
    includes receiving kudos, ranking up, and earning rewards.
    """

    def __init__(self, air) -> None:
        self.air = air

        # Begin a bi-daily task which will reset the kudos quests
        # which the HQ officers are currently offering.
        self.bidailyTask = "kudos_bidailyReset_task"
        self.bidailyPurgeTask = "kudos_purge_task"
        timestamp = TimeUtil.getNextTimestampOfInterval(KUDOS_RESET_INTERVAL)
        taskMgr.doMethodLater(
            timestamp - time.time(),
            self.doBidailyReset,
            self.bidailyTask,
        )
    
    def doBidailyReset(self, task: Task.Task) -> None:
        """Method called every 12 hours to reset the kudos
        quests provided by all of the shopkeepers.
        """
        messenger.send("kudos_bidailyReset")
        taskMgr.doMethodLater(
            5,
            self.sendThePurge,
            self.bidailyPurgeTask,
        )
        task.delayTime = TimeUtil.getNextTimestampOfInterval(KUDOS_RESET_INTERVAL) - time.time()
        return task.again

    def sendThePurge(self, task: Task.Task):
        messenger.send('kudos_purge')
        return task.done

    def giveKudos(self, av: DistributedToonAI, kudos: int, zoneId: int) -> None:
        """When a kudos quest is completed, call this function to
        handle giving the avatar their kudos.
        """
        # Get the map of our kudos. (zoneId: kudos)
        kudosDict = av.getKudos()

        # Safely retrieve the kudos for this zoneId.
        currKudos = kudosDict.get(zoneId, 0)
        currKudos += kudos

        # Get their kudos rank.
        currentRank = getKudosRank(av, zoneId)
        if currentRank == 10:
            # If they are at rank 10, they are eligible for
            # rewards at every 30 kudos earned. Let's try
            # to give them some.
            while currKudos >= MAXIMUM_KUDOS + LOOPING_KUDOS:
                # Give the av some gumballs.
                av.addMoney(
                    num=getKudosRankupGumballAmount(zoneId),
                    doAnim=True,
                    currencyType=MaterialItemType.Gumballs,
                )

                # Eat the kudos juice
                currKudos -= LOOPING_KUDOS
        
        # Update the kudos dict with the new value.
        kudosDict[zoneId] = currKudos

        # Finally, set their kudos.
        av.b_setKudos(kudosDict)
