from toontown.hood import SkyUtil
from toontown.level.LevelMgr import LevelMgr


class PersistentLevelMgr(LevelMgr):
    def __init__(self, level, entId):
        super().__init__(level, entId)
        if self.geom:
            self.geom.reparentTo(render)

        self.sky = None

        if hasattr(base, 'persistentLevelReady'):
            self.initMusic()
        else:
            self.acceptOnce('PersistentLevelReady', self.handleReady)

    def destroy(self):
        super().destroy()
        if self.sky:
            self.stopSky()
            del self.sky

    def handleReady(self):
        self.initMusic()
        self.startSky()

    def initMusic(self):
        if self.musicKey:
            base.musicMgr.playMusic(self.musicKey, looping=True)
            base.cr.playGame.hood.loader.music = self.musicKey
        if self.battleMusicKey:
            base.cr.playGame.hood.loader.battleMusic = self.battleMusicKey

    def startSky(self):
        if self.skyboxModel:
            self.sky = loader.loadModel(self.skyboxModel)
            SkyUtil.startCloudSky(self)
            # TODO: Halloween sky code (maybe make it not crap)

    def stopSky(self):
        # Remove the sky task just in case it was spawned.
        taskMgr.remove('skyTrack')
        self.sky.removeNode()
