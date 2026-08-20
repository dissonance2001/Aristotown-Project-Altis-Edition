from __future__ import absolute_import
import time
from direct.task.TaskManagerGlobal import taskMgr
from toontown.events.winter import DistributedToonseltownMinigameAI
from toontown.classicchars import DistributedMinnieAI
from toontown.hood import HoodAI
from toontown.safezone import DistributedTrolleyAI
from toontown.toon import NPCToons
from toontown.toonbase import ToontownGlobals
from toontown.ai import DistributedTrickOrTreatTargetAI
from toontown.ai import DistributedWinterCarolingTargetAI
from six.moves import range

class TSHoodAI(HoodAI.HoodAI):
    def __init__(self, air):
        HoodAI.HoodAI.__init__(self, air,
                               ToontownGlobals.Toonseltown,
                               ToontownGlobals.Toonseltown)

        self.trolley = None
        self.classicChar = None
        self.timeBetweenGame = 20
        self.minigame = None

        self.startup()

    def startup(self):
        HoodAI.HoodAI.startup(self)

        existingNpcIds = set([getattr(obj, 'npcId', None) for obj in self.air.doId2do.values()])
        npcIdList = NPCToons.zone2NpcDict.get(self.zoneId, [])
        for i in range(len(npcIdList)):
            npcId = npcIdList[i]
            if npcId not in existingNpcIds:
                npcDesc = NPCToons.NPCToonDict.get(npcId)
                NPCToons.createNPC(self.air, npcId, npcDesc, self.zoneId, posIndex=i)

        # if simbase.config.GetBool('want-minigames', True):
        #     self.createTrolley()
        if simbase.config.GetBool('want-classic-chars', True):
            if simbase.config.GetBool('want-minnie', True):
                self.createClassicChar()

        if simbase.air.wantHalloween:
            self.TrickOrTreatTargetManager = DistributedTrickOrTreatTargetAI.DistributedTrickOrTreatTargetAI(self.air)
            self.TrickOrTreatTargetManager.generateWithRequired(4835)

        if simbase.air.wantChristmas:
            self.WinterCarolingTargetManager = DistributedWinterCarolingTargetAI.DistributedWinterCarolingTargetAI(
                self.air)
            self.WinterCarolingTargetManager.generateWithRequired(4614)

        if simbase.config.GetBool('want-toonseltown-present-thief', True):
            self.scheduleNextMinigame()

    # def createTrolley(self):
    #     self.trolley = DistributedTrolleyAI.DistributedTrolleyAI(self.air)
    #     self.trolley.generateWithRequired(self.zoneId)
    #     self.trolley.start()

    def getTimeUntilNextGame(self):
        return (self.timeBetweenGame * 60) - (time.time() % (self.timeBetweenGame * 60))

    def scheduleNextMinigame(self):
        taskMgr.remove('ts-start-minigame-loop')
        taskMgr.doMethodLater(self.getTimeUntilNextGame(), self.startMinigame, 'ts-start-minigame-loop')

    def getMissingPresentThiefDclasses(self):
        missing = []
        required = (
            ('DistributedToonseltownMinigameAI', 'DistributedToonseltownMinigame'),
            ('DistributedWinterMinigameSuitAI', 'DistributedWinterMinigameSuit'),
        )
        for className, displayName in required:
            if className not in self.air.dclassesByName:
                missing.append(displayName)
        return missing

    def beginPresentThief(self):
        if self.minigame:
            return False, 'Present Thief is already active.'
        missing = self.getMissingPresentThiefDclasses()
        if missing:
            message = 'Present Thief cannot start because the active dclass/toon.dc is missing: %s' % ', '.join(missing)
            self.notify.warning(message)
            return False, message
        taskMgr.remove('ts-start-minigame-loop')
        taskMgr.remove('ts-minigame-end')
        self.minigame = DistributedToonseltownMinigameAI.DistributedToonseltownMinigameAI(self.air)
        self.minigame.generateWithRequired(ToontownGlobals.Toonseltown)
        taskMgr.doMethodLater(self.minigame.gameTime + 10, self.finishMinigame, 'ts-minigame-end')
        self.minigame.startGameWarnings()
        return True, 'Present Thief will begin in 10 seconds.'

    def startMinigame(self, task=None):
        started, message = self.beginPresentThief()
        if not started and not self.minigame:
            self.scheduleNextMinigame()

    def endPresentThief(self):
        taskMgr.remove('ts-minigame-end')
        if not self.minigame:
            return False, 'There is no active Present Thief minigame.'
        self.minigame.endGame()
        self.minigame = None
        return True, 'Ended the Present Thief minigame.'

    def finishMinigame(self, task=None):
        self.endPresentThief()
        self.scheduleNextMinigame()

    def shutdown(self):
        taskMgr.remove('ts-start-minigame-loop')
        taskMgr.remove('ts-minigame-end')
        if self.minigame:
            self.minigame.endGame()
            self.minigame = None
        HoodAI.HoodAI.shutdown(self)

    def createClassicChar(self):
        self.classicChar = DistributedMinnieAI.DistributedMinnieAI(self.air)
        self.classicChar.generateWithRequired(self.zoneId)
        self.classicChar.start()
