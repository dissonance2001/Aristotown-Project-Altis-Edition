import time

from panda3d.core import ConfigVariableBool, Vec3

from toontown.events.winter import DistributedToonseltownMinigameAI
from toontown.hood import HoodAI
from toontown.quest3.QuestEnums import QuestCollectable
from toontown.safezone import QuestCollectablePlannerAI
from toontown.safezone.ChairConstants import ChairTypeEnum
from toontown.safezone.DistributedChairAI import DistributedChairAI
from toontown.toon.npc import NPCToons
from toontown.toonbase import ToontownGlobals, RealmGlobals


class TSHoodAI(HoodAI.HoodAI):

    ChairHeight = -0.2
    ChairLocations = {
        ToontownGlobals.Toonseltown: (
            # First two benches upon walking down the entryway
            (Vec3(-160.412, 37.453, 20.716 + ChairHeight), Vec3(44.402, 0, 0), 0, ChairTypeEnum.BENCH),
            (Vec3(-154.367, 43.742, 20.716 + ChairHeight), Vec3(43.777, 0, 0), 0, ChairTypeEnum.BENCH),

            # Reindeer Ranch Frozen lake Benches
            (Vec3(-24.361, 279.846, 34.732 + ChairHeight), Vec3(103.424, 0, 0), 0, ChairTypeEnum.BENCH),
            (Vec3(-19.943, 267.853, 34.732 + ChairHeight), Vec3(116.798, 0, 0), 0, ChairTypeEnum.BENCH),
            (Vec3(-10.743, 253.938, 34.732 + ChairHeight), Vec3(134.184, 0, 0), 0, ChairTypeEnum.BENCH)
        )
    }

    def __init__(self, air):
        HoodAI.HoodAI.__init__(self, air,
                               ToontownGlobals.Toonseltown,
                               ToontownGlobals.Toonseltown)
        self.timeBetweenGame = 20  # 20 minutes between games
        if RealmGlobals.getCurrentRealm().isDevRealm():
            self.timeBetweenGame = 500  # I HATE YOU TOONSELTOWN
        self.minigame = None
        self.startup()

    def startup(self):
        HoodAI.HoodAI.startup(self)

        self.setupChairs()
        # If the hood is active, generate npcs and start the minigame
        if self.isActive():
            NPCToons.createNpcsInZone(self.air, ToontownGlobals.ToonselTown)
            self.collectablePlanner = QuestCollectablePlannerAI.QuestCollectablePlannerAI(18000, QuestCollectable.ToonselPresent)
            self.collectablePlanner.start()

            if not self.air.safeDistrict:  # No minigame in safe districts
                taskMgr.doMethodLater(self.get_time_until_next_game(), self.start_minigame, 'ts-start-minigame-loop')

    def shutdown(self):
        HoodAI.HoodAI.shutdown(self)

    def setupChairs(self):
        index = 0

        for zoneId, chairLocations in self.ChairLocations.items():
            for pos, hpr, height, chairType in chairLocations:
                wantToono = False
                chair = DistributedChairAI(self.air, index, hopOffPos=[0, -5, 0.4 - height],
                                           chairType=chairType, wantToono=wantToono)
                chair.generateWithRequired(zoneId)

                index += 1

                x, y, z = pos
                h, p, r = hpr
                chair.b_setPosHpr(x, y, z, h, p, r)


    def get_time_until_next_game(self):
        """
        Returns the about of seconds until the next game should start.
        E.g. if minutes_between_game = 30
        The game will run at 12:00, 12:30, 13:00 etc
        if minutes_between_game = 7
        The game will run at 12:07, 12:14, 12:21 etc
        """
        return (self.timeBetweenGame * 60) - (time.time() % (self.timeBetweenGame * 60))

    def isActive(self):
        return simbase.air.holidayManager.isHolidayRunning(ToontownGlobals.WINTER_DECORATIONS)

    def start_minigame(self, task=None):
        """
        Starts the TS minigame
        """
        if self.minigame:  # If the minigame exists, we should not start another one
            return

        self.minigame = DistributedToonseltownMinigameAI.DistributedToonseltownMinigameAI(self.air)
        self.minigame.generateWithRequired(18000)
        taskMgr.doMethodLater(self.minigame.gameTime + 10, self.finish_minigame, 'ts-minigame-end')
        self.minigame.startGameWarnings()

    def finish_minigame(self, task=None):
        if self.minigame:
            self.minigame.endGame()
            self.minigame = None
            taskMgr.doMethodLater(self.get_time_until_next_game(), self.start_minigame, 'ts-start-minigame-loop')

    def doFireworks(self, task=None):
        pass
