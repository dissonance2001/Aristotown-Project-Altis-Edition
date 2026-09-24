from toontown.toon.ClashDistributedToonBaseAI  import ClashDistributedToonBaseAI
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from toontown.ai.ToontownAIRepository import ToontownAIRepository


class DistributedNPCToonBaseAI(ClashDistributedToonBaseAI):

    def __init__(self, air, npcId, questCallback=None, canSpawn=True):
        super().__init__(air)
        self.air = air  # type: ToontownAIRepository
        self.npcId = npcId
        # busy will be replaced with the toon this npc is talking to
        self.busy = 0
        self.questCallback = questCallback
        # Does this NPC give out quests?
        self.givesQuests = 1
        self.canSpawn = canSpawn

    def delete(self):
        taskMgr.remove(self.uniqueName('clearMovie'))
        ClashDistributedToonBaseAI.delete(self)

    def getHq(self):
        """
        Override if you should be considered an HQ Toon
        """
        return 0

    def getTailor(self):
        """
        Override if you should be considered a Tailor
        """
        return 0

    def getGivesQuests(self):
        return self.givesQuests

    def avatarEnter(self):
        pass

    def isBusy(self):
        return self.busy > 0

    def getNpcId(self):
        return self.npcId

    def setNpcTag(self, tag):
        self.sendUpdate('setTag', [tag])

    def freeAvatar(self, avId):
        # Free this avatar, probably because he requested interaction while
        # I was busy. This can happen when two avatars request interaction
        # at the same time. The AI will accept the first, sending a setMovie,
        # and free the second
        self.sendUpdateToAvatarId(avId, 'freeAvatar', [])

    def setPositionIndex(self, posIndex):
        self.posIndex = posIndex

    def getPositionIndex(self):
        return self.posIndex

    def setCanSpawn(self, canSpawn):
        self.canSpawn = canSpawn

    def getCanSpawn(self):
        return self.canSpawn
