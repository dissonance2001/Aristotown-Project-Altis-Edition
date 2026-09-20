from direct.distributed.DistributedObjectAI import DistributedObjectAI

from toontown.quest3.base.QuestReference import QuestId
from toontown.quest3.kudos import KudosConstants
from toontown.quest3.questlines.KudosQuestLine import KudosQuestLine
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from toontown.utils.RateLimiter import RateLimiter


@DirectNotifyCategory()
class DistributedKudosBoardAI(DistributedObjectAI):
    def __init__(self, air):
        super().__init__(air)
        self.ratelimiters = {}

    def rateLimited(self, avId):
        if avId not in self.ratelimiters:
            self.ratelimiters[avId] = RateLimiter(max_hits=4, period=1)
        ratelimiter = self.ratelimiters.get(avId)
        return ratelimiter.tryRequest()

    def chooseKudosQuest(self, questId):
        # Get the av.
        avId = self.air.getAvatarIdFromSender()
        if self.rateLimited(avId):
            return

        av = self.air.doId2do.get(avId)
        if not av:
            return
        questId = QuestId.fromStruct(questId)

        # There's two types of quests that we care about:
        # 1) The rank-up task.
        # 2) The (available) individual kudos tasks.
        # The av can only get a rank-up task if they can even get one.
        # In addition, none of these tasks can be in the av's quest history.
        possibleQuestIds = []
        possibleQuestIds.extend(KudosQuestLine.getAvailableKudosQuests(self.zoneId))

        # OK, first check if the quest ID they're asking for is available.
        if questId not in possibleQuestIds:
            # NO! they can't have it :(
            return

        # And make sure that they don't already own it, or have done it already.
        if av.hasQuest(questId=questId, history=True):
            # NO!!!!!!! they still cant have it
            return

        # Add the quest.
        av.addQuest(questId)
