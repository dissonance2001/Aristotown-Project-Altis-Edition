from direct.distributed.DistributedObjectAI import DistributedObjectAI
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from toontown.toonbase import ToontownGlobals
from toontown.cutscene import CutsceneLocalizer
import random


@DirectNotifyCategory()
class DistributedHighRollerTeleporterAI(DistributedObjectAI):
    AdvertisementTaskName = 'DistHighRollerTeleporterAI-IdleAdvertiseTask'
    AdvertisementTaskTimeRange = (16, 34)

    def __init__(self, air):
        super().__init__(air)
        self.lastAdvertisementIndex = -1
        self.blockedTeleports = []

    def announceGenerate(self):
        super().announceGenerate()
        if self.zoneId != ToontownGlobals.MajorPlayerLobby:
            self.__beginAdvertisementTask()

    def delete(self):
        self.removeAllTasks()
        super().delete()

    def __getNewTaskTime(self):
        return lerp(self.AdvertisementTaskTimeRange[0], self.AdvertisementTaskTimeRange[1], random.random())

    def __beginAdvertisementTask(self):
        self.removeTask(self.uniqueName(self.AdvertisementTaskName))
        self.doMethodLater(self.__getNewTaskTime(), self.__advertisementTask, name=self.uniqueName(self.AdvertisementTaskName))

    def __advertisementTask(self, task=None):
        dialogueIndexChoices = list(range(len(CutsceneLocalizer.HighRollerTeleporterAdvertising)))
        if self.lastAdvertisementIndex != -1 and self.lastAdvertisementIndex in dialogueIndexChoices:
            dialogueIndexChoices.remove(self.lastAdvertisementIndex)

        newIndex = random.choice(dialogueIndexChoices)
        self.lastAdvertisementIndex = newIndex
        self.d_advertise(newIndex)

        task.delayTime = self.__getNewTaskTime()
        return task.again

    def d_advertise(self, dialogueIndex):
        self.sendUpdate('advertise', [dialogueIndex])

    def requestTeleport(self):
        avId = self.air.getAvatarIdFromSender()
        av = self.air.doId2do.get(avId)
        if not av:
            return
        if av.zoneId != self.zoneId:
            return
        if avId in self.blockedTeleports:
            return

        def removeBlockedTeleport(avId):
            if avId in self.blockedTeleports:
                self.blockedTeleports.remove(avId)

        self.sendUpdate('handleToonTeleport', [avId])
        self.blockedTeleports.append(avId)
        self.doMethodLater(7.5, removeBlockedTeleport, extraArgs=[avId], name=self.uniqueName(f'removeBlockedTeleport-{avId}'))
