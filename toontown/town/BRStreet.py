import random
from direct.task.Task import Task
from toontown.town import Street
from toontown.toonbase import ToontownGlobals

class BRStreet(Street.Street):
    
    def enter(self, requestStatus):
        self.__erfitLobbyMusicActive = False
        Street.Street.enter(self, requestStatus)
        taskMgr.doMethodLater(1, self.__windTask, 'BR-wind')
        if self.loader.canonicalBranchZone == ToontownGlobals.PolarPlace:
            taskMgr.remove('BR-erfit-lobby-music')
            taskMgr.add(self.__erfitLobbyMusicTask, 'BR-erfit-lobby-music')

    def exit(self):
        taskMgr.remove('BR-erfit-lobby-music')
        if getattr(self, '_BRStreet__erfitLobbyMusicActive', False):
            if self.loader.erfitLobbyMusic:
                self.loader.erfitLobbyMusic.stop()
            self.__erfitLobbyMusicActive = False
        Street.Street.exit(self)
        taskMgr.remove('BR-wind')

    def __erfitLobbyMusicTask(self, task):
        if not base.localAvatar or not self.loader.countErfitBuilding:
            return Task.cont
        currentState = self.fsm.getCurrentState()
        stateName = currentState and currentState.getName() or ''
        if stateName not in ('walk', 'sit', 'stickerBook', 'stopped', 'elevator', 'elevatorIn'):
            if self.__erfitLobbyMusicActive and self.loader.erfitLobbyMusic:
                self.loader.erfitLobbyMusic.stop()
                self.__erfitLobbyMusicActive = False
            return Task.cont
        origin = self.loader.countErfitBuilding.find('**/count_door_origin')
        if origin.isEmpty():
            origin = self.loader.countErfitBuilding
        distance = base.localAvatar.getDistance(origin)
        if not self.__erfitLobbyMusicActive and distance <= 58.0:
            if self.loader.music:
                self.loader.music.stop()
            if self.loader.erfitLobbyMusic:
                base.playMusic(self.loader.erfitLobbyMusic, looping=1, volume=0.8)
                self.__erfitLobbyMusicActive = True
        elif self.__erfitLobbyMusicActive and distance >= 70.0:
            if self.loader.erfitLobbyMusic:
                self.loader.erfitLobbyMusic.stop()
            if self.loader.music:
                base.playMusic(self.loader.music, looping=1, volume=0.8)
            self.__erfitLobbyMusicActive = False
        return Task.cont

    def __windTask(self, task):
        base.playSfx(random.choice(self.loader.windSound))
        time = random.random() * 8.0 + 1
        taskMgr.doMethodLater(time, self.__windTask, 'BR-wind')
        return Task.done