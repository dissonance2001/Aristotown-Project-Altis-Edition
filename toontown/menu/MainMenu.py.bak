from direct.fsm.FSM import FSM
from direct.interval.IntervalGlobal import *
from panda3d.core import *

from toontown.menu import MainMenuScreenHome, MainMenuScreenPlay, MainMenuScreenOptions
from toontown.hood import SkyUtil


class MainMenu(FSM):
    def __init__(self, skipMenu=False):
        FSM.__init__(self, 'MainMenu')
        self.skipMenu = skipMenu
        self.homeScreen = None
        self.playScreen = None
        self.optionsScreen = None
        self.bgModel = None
        self.sky = None
        self.lamps = []
        self.trashCan = None
        self._closed = False
        base.cr.mainmenu = self
        self.loadScene()

    def loadScene(self):
        self.bgModel = loader.loadModel('phase_3/models/menu/TTC_scene')
        self.bgModel.reparentTo(render)
        self.bgModel.setScale(.6)

        try:
            lampModel = loader.loadModel('phase_3.5/models/props/tt_m_ara_TT_streetlight_three_light')
        except:
            lampModel = loader.loadModel('phase_3.5/models/props/streetlight_TT')
        locators = self.bgModel.findAllMatches('**/lamp_locator_*')
        if locators.getNumPaths():
            for locator in locators:
                lamp = lampModel.copyTo(locator)
                self.lamps.append(lamp)
        else:
            for pos in ((-16, 51.6, 7.10146), (11.4, 51.6, 7.10146)):
                lamp = lampModel.copyTo(render)
                lamp.setPos(*pos)
                self.lamps.append(lamp)
        lampModel.removeNode()

        self.trashCan = loader.loadModel('phase_8/models/char/tt_r_ara_dga_trashcan')
        trashLocator = self.bgModel.find('**/trashcan_locator_1')
        if not trashLocator.isEmpty():
            self.trashCan.reparentTo(trashLocator)
        else:
            self.trashCan.reparentTo(render)
            self.trashCan.setPosHpr(5.18212, 51.2468, 7, -30, 0, 0)

        self.sky = loader.loadModel('phase_3.5/models/props/TT_sky')
        SkyUtil.startCloudSky(self)
        base.camera.setPosHpr(-1.5, -20, 20, 0, -5, 0)
        self.request('Home')

    def skyTrack(self, task):
        return SkyUtil.cloudSkyTrack(task)

    def enterHome(self):
        self.homeScreen = MainMenuScreenHome.MainMenuScreenHome()

    def exitHome(self):
        if self.homeScreen:
            self.homeScreen.destroy()
            self.homeScreen = None

    def enterPlay(self):
        self.playScreen = MainMenuScreenPlay.MainMenuScreenPlay(
            base.cr.PAT_AVLIST,
            base.cr.PAT_LOGINFSM,
            base.cr.PAT_DONEEVENT
        )

    def exitPlay(self):
        if self.playScreen:
            self.playScreen.destroy()
            self.playScreen = None

    def enterOptions(self):
        self.optionsScreen = MainMenuScreenOptions.MainMenuScreenOptions()

    def exitOptions(self):
        if self.optionsScreen:
            self.optionsScreen.destroy()
            self.optionsScreen = None

    def enterQuit(self):
        pass

    def exitQuit(self):
        pass

    def exitMenu(self):
        if self._closed:
            return
        self._closed = True
        if self.homeScreen:
            self.homeScreen.destroy()
            self.homeScreen = None
        if self.playScreen:
            self.playScreen.destroy()
            self.playScreen = None
        if self.optionsScreen:
            self.optionsScreen.destroy()
            self.optionsScreen = None
        if self.bgModel:
            self.bgModel.removeNode()
            self.bgModel = None
        for lamp in self.lamps:
            if lamp:
                lamp.removeNode()
        self.lamps = []
        if self.trashCan:
            self.trashCan.removeNode()
            self.trashCan = None
        if self.sky:
            taskMgr.remove('skyTrack')
            self.sky.removeNode()
            self.sky = None
        try:
            FSM.cleanup(self)
        except:
            pass
