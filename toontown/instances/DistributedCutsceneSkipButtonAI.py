from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectAI import DistributedObjectAI


class DistributedCutsceneSkipButtonAI(DistributedObjectAI):
    """Server-side vote object for Altis instance cutscenes."""

    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedCutsceneSkipButtonAI')

    def __init__(self, air, instanceCog, involvedToons, forceNonskip=False):
        DistributedObjectAI.__init__(self, air)
        self.instanceCog = instanceCog
        self.avIdList = list(involvedToons)
        self.skipVoters = []
        self.skippable = not forceNonskip

    def generate(self):
        DistributedObjectAI.generate(self)
        required = self.getRequiredVotes()
        if self.skippable:
            self.sendUpdate('setVoteSkips', [0, required])
        else:
            self.sendUpdate('setVoteSkips', [-1, required])

    def getRequiredVotes(self):
        # Preserve Clash's multiplayer behaviour: all but one Toon can approve
        # the skip, while a solo instance still requires the local Toon to click.
        return max(1, len(self.avIdList) - 1)

    def requestSkip(self):
        if not self.skippable:
            return

        avId = self.air.getAvatarIdFromSender()
        if avId not in self.avIdList or avId in self.skipVoters:
            return

        self.skipVoters.append(avId)
        required = self.getRequiredVotes()
        if len(self.skipVoters) >= required:
            self.sendUpdate('setCutsceneSkip', [])
        else:
            self.sendUpdate('setVoteSkips', [len(self.skipVoters), required])
