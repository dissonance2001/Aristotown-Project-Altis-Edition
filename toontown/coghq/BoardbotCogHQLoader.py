from direct.directnotify import DirectNotifyGlobal
from direct.fsm import StateData
import CogHQLoader
from toontown.toonbase import ToontownGlobals
from direct.gui import DirectGui
from toontown.toonbase import TTLocalizer
from toontown.battle.BattleProps import *
from toontown.toon import Toon
from direct.fsm import State
import BoardbotHQExterior
import BoardbotOfficeExterior
from toontown.coghq.boardbothq import BoardOfficeInterior
from toontown.coghq import CashbotHQBossBattle

aspectSF = 0.7227

class BoardbotCogHQLoader(CogHQLoader.CogHQLoader):
    notify = DirectNotifyGlobal.directNotify.newCategory('BoardbotCogHQLoader')

    def __init__(self, hood, parentFSMState, doneEvent):
        CogHQLoader.CogHQLoader.__init__(self, hood, parentFSMState, doneEvent)
        self.fsm.addState(State.State('boardofficeInterior', self.enterBoardOfficeInterior, self.exitBoardOfficeInterior, ['quietZone', 'cogHQExterior']))
        self.fsm.addState(State.State('factoryExterior', self.enterFactoryExterior, self.exitFactoryExterior, ['quietZone', 'cogHQExterior']))
        for stateName in ['start', 'cogHQExterior', 'quietZone']:
            state = self.fsm.getStateNamed(stateName)
            state.addTransition('boardofficeInterior')
			
        for stateName in ['quietZone']:
            state = self.fsm.getStateNamed(stateName)
            state.addTransition('factoryExterior')

        self.musicFile = 'phase_14/audio/bgm/BD_courtyard.ogg'
        self.cogHQExteriorModelPath = 'phase_14/models/neighborhoods/CogNation'
        self.factoryExteriorModelPath = 'phase_14/models/boardbotHQ/boardbot_factory_exterior'
        self.cogHQLobbyModelPath = 'phase_14/models/modules/ExecutiveLobby'
        self.geom = None
        return
        
    def load(self, zoneId):
        CogHQLoader.CogHQLoader.load(self, zoneId)
        Toon.loadCashbotHQAnims()

    def unloadPlaceGeom(self):
        if self.geom:
            self.geom.removeNode()
            self.geom = None
        if self.dish:
            self.dish.removeNode()
            self.dish = None
        if self.helicopter:
            self.helicopter.removeNode()
            self.helicopter = None
        if self.lightPost:
            self.lightPost.removeNode()
            self.lightPost = None
        if self.lightPost2:
            self.lightPost2.removeNode()
            self.lightPost2 = None
        if self.lightPost3:
            self.lightPost3.removeNode()
            self.lightPost3 = None
        if self.lightPost4:
            self.lightPost4.removeNode()
            self.lightPost4 = None
        if self.lightPost5:
            self.lightPost5.removeNode()
            self.lightPost5 = None
        if self.lightPost6:
            self.lightPost6.removeNode()
            self.lightPost6 = None
        if self.lightPost7:
            self.lightPost7.removeNode()
            self.lightPost7 = None
        if self.lightPost8:
            self.lightPost8.removeNode()
            self.lightPost8 = None
        if self.lightPost9:
            self.lightPost9.removeNode()
            self.lightPost9 = None
        if self.lightPost10:
            self.lightPost10.removeNode()
            self.lightPost10 = None
        if self.lightPost11:
            self.lightPost11.removeNode()
            self.lightPost11 = None
        if self.lightPost12:
            self.lightPost12.removeNode()
            self.lightPost12 = None
        if self.lightPost13:
            self.lightPost13.removeNode()
            self.lightPost13 = None
        if self.lightPost14:
            self.lightPost14.removeNode()
            self.lightPost14 = None
        if self.lightPost15:
            self.lightPost15.removeNode()
            self.lightPost15 = None
        if self.lightPost16:
            self.lightPost16.removeNode()
            self.lightPost16 = None
        if self.lightPost17:
            self.lightPost17.removeNode()
            self.lightPost17 = None
        if self.lightPost18:
            self.lightPost18.removeNode()
            self.lightPost18 = None
        CogHQLoader.CogHQLoader.unloadPlaceGeom(self)

    def loadPlaceGeom(self, zoneId):
        self.notify.info('loadPlaceGeom: %s' % zoneId)
        zoneId = zoneId - zoneId % 100
        if zoneId == ToontownGlobals.BoardbotHQ:
            self.geom = loader.loadModel(self.cogHQExteriorModelPath)
            self.geom.setPos(-35, -200, -64.5)
            self.geom.setScale(2)
            self.geom.setHpr(90, 0, 0)
            self.dish = loader.loadModel('phase_14/models/props/radar.bam')
            self.dish.reparentTo(self.geom)
            self.dish.setHpr(-90, 0, 0)  # Adjust position
            self.dish.setPos(0, 0, 10)
            self.dish.setScale(0.25)
            self.helicopter = globalPropPool.getProp('CogNationChopper')
            self.helicopter.reparentTo(render)
            self.helicopter.loop('CogNationChopper')
            self.helicopter.setHpr(-90, 0, 0)  # Adjust position
            self.helicopter.setPos(338.338, -196.359, -64.4747)
            self.helicopter.setScale(0.75)
            self.lightPost = loader.loadModel('phase_14/models/props/CN-streetlight.bam')
            self.lightPost.reparentTo(self.geom)
            self.lightPost.setHpr(55.6597, 0, 0)  # Adjust position
            self.lightPost.setPos(-28.817, 84.6601, 0.403174)
            self.lightPost.setScale(2.0)
            self.lightPost2 = loader.loadModel('phase_14/models/props/CN-streetlight.bam')
            self.lightPost2.reparentTo(self.geom)
            self.lightPost2.setHpr(-47.0231, 0, 0)  # Adjust position
            self.lightPost2.setPos(37.8294, 93.8389, 0.403174)
            self.lightPost2.setScale(2.0)
            self.lightPost3 = loader.loadModel('phase_14/models/props/CN-streetlight.bam')
            self.lightPost3.reparentTo(self.geom)
            self.lightPost3.setHpr(-449.653, 0, 0)  # Adjust position
            self.lightPost3.setPos(40.1556, -0.13351, 0.403174)
            self.lightPost3.setScale(2.0)
            self.lightPost4 = loader.loadModel('phase_14/models/props/CN-streetlight.bam')
            self.lightPost4.reparentTo(self.geom)
            self.lightPost4.setHpr(-272.189, 0, 0)  # Adjust position
            self.lightPost4.setPos(-40.2825, 1.19355, 0.403174)
            self.lightPost4.setScale(2.0)
            self.lightPost5 = loader.loadModel('phase_14/models/props/CN-streetlight.bam')
            self.lightPost5.reparentTo(self.geom)
            self.lightPost5.setHpr(-312.83, 0, 0)  # Adjust position
            self.lightPost5.setPos(-40.5655, -86.609, 0.403174)
            self.lightPost5.setScale(2.0)
            self.lightPost6 = loader.loadModel('phase_14/models/props/CN-streetlight.bam')
            self.lightPost6.reparentTo(self.geom)
            self.lightPost6.setHpr(-266.775, 0, 0)  # Adjust position
            self.lightPost6.setPos(-39.5258, -119.852, 0.403174)
            self.lightPost6.setScale(2.0)
            self.lightPost7 = loader.loadModel('phase_14/models/props/CN-streetlight.bam')
            self.lightPost7.reparentTo(self.geom)
            self.lightPost7.setHpr(0.0720297, 0, 0)  # Adjust position
            self.lightPost7.setPos(0.584705, 132.076, 0.403174)
            self.lightPost7.setScale(2.0)
            self.lightPost8 = loader.loadModel('phase_14/models/props/CN-streetlight.bam')
            self.lightPost8.reparentTo(self.geom)
            self.lightPost8.setHpr(-46.9395, 0, 0)  # Adjust position
            self.lightPost8.setPos(42.5149, -87.6713, 0.403174)
            self.lightPost8.setScale(2.0)
            self.lightPost9 = loader.loadModel('phase_14/models/props/CN-streetlight.bam')
            self.lightPost9.reparentTo(self.geom)
            self.lightPost9.setHpr(-141.825, 0, 0)  # Adjust position
            self.lightPost9.setPos(42.8344, -122.754, 0.403174)
            self.lightPost9.setScale(2.0)
            self.lightPost10 = loader.loadModel('phase_14/models/props/CN-streetlight.bam')
            self.lightPost10.reparentTo(self.geom)
            self.lightPost10.setHpr(-90, 0, 0)  # Adjust position
            self.lightPost10.setPos(45.3425, -201.864, 0.403174)
            self.lightPost10.setScale(2.0)
            self.lightPost11 = loader.loadModel('phase_14/models/props/CN-streetlight.bam')
            self.lightPost11.reparentTo(self.geom)
            self.lightPost11.setHpr(-270.332, 0, 0)  # Adjust position
            self.lightPost11.setPos(-39.7354, -201.859, 0.403174)
            self.lightPost11.setScale(2.0)
            self.lightPost12 = loader.loadModel('phase_14/models/props/CN-streetlight.bam')
            self.lightPost12.reparentTo(self.geom)
            self.lightPost12.setHpr(-315.088, 0, 0)  # Adjust position
            self.lightPost12.setPos(-39.5837, -297.263, 0.403174)
            self.lightPost12.setScale(2.0)
            self.lightPost13 = loader.loadModel('phase_14/models/props/CN-streetlight.bam')
            self.lightPost13.reparentTo(self.geom)
            self.lightPost13.setHpr(-180, 0, 0)  # Adjust position
            self.lightPost13.setPos(3.64376, -338.231, 0.403174)
            self.lightPost13.setScale(2.0)
            self.lightPost14 = loader.loadModel('phase_14/models/props/CN-streetlight.bam')
            self.lightPost14.reparentTo(self.geom)
            self.lightPost14.setHpr(313.777, 0, 0)  # Adjust position
            self.lightPost14.setPos(48.0548, -297.621, 0.403174)
            self.lightPost14.setScale(2.0)
            self.lightPost15 = loader.loadModel('phase_14/models/props/CN-streetlight.bam')
            self.lightPost15.reparentTo(self.geom)
            self.lightPost15.setHpr(180, 0, 0)  # Adjust position
            self.lightPost15.setPos(79.7079, -337.535, 0.403174)
            self.lightPost15.setScale(2.0)
            self.lightPost16 = loader.loadModel('phase_14/models/props/CN-streetlight.bam')
            self.lightPost16.reparentTo(self.geom)
            self.lightPost16.setHpr(180, 0, 0)  # Adjust position
            self.lightPost16.setPos(-88.0122, -341.62, 0.403174)
            self.lightPost16.setScale(2.0)
            self.lightPost17 = loader.loadModel('phase_14/models/props/CN-streetlight.bam')
            self.lightPost17.reparentTo(self.geom)
            self.lightPost17.setHpr(497.85, 0, 0)  # Adjust position
            self.lightPost17.setPos(-40.7189, 42.8691, 0.403174)
            self.lightPost17.setScale(2.0)
            self.lightPost18 = loader.loadModel('phase_14/models/props/CN-streetlight.bam')
            self.lightPost18.reparentTo(self.geom)
            self.lightPost18.setHpr(0, 0, 0)  # Adjust position
            self.lightPost18.setPos(-68.7107, 75.0015, 0.403174)
            self.lightPost18.setScale(2.0)
            self.elevatorModel = loader.loadModel('phase_9/models/cogHQ/ttcc_prop_ms_elevatorBroken.bam')
            locator = self.geom.find('**/elevator_origin1')
            if locator.isEmpty():
                self.elevatorModel.reparentTo(render)
                self.elevatorModel.setHpr(0, 0, 0)  # Adjust position
                self.elevatorModel.setPos(0, -1, 0)
            else:
                self.elevatorModel.reparentTo(locator)
                self.elevatorModel.setHpr(0, 0, 0)
                self.elevatorModel.setPos(0, -1, 0)
            self.elevatorModel2 = loader.loadModel('phase_9/models/cogHQ/ttcc_prop_ms_elevatorBroken.bam')
            locator = self.geom.find('**/elevator_origin2')
            if locator.isEmpty():
                self.elevatorModel2.reparentTo(render)
                self.elevatorModel2.setHpr(0, 0, 0)  # Adjust position
                self.elevatorModel2.setPos(0, -1, 0)
            else:
                self.elevatorModel2.reparentTo(locator)
                self.elevatorModel2.setHpr(0, 0, 0)
                self.elevatorModel2.setPos(0, -1, 0)
            self.elevatorModel3 = loader.loadModel('phase_9/models/cogHQ/ttcc_prop_ms_elevatorBroken.bam')
            locator = self.geom.find('**/elevator_origin3')
            if locator.isEmpty():
                self.elevatorModel3.reparentTo(render)
                self.elevatorModel3.setHpr(0, 0, 0)  # Adjust position
                self.elevatorModel3.setPos(0, -1, 0)
            else:
                self.elevatorModel3.reparentTo(locator)
                self.elevatorModel3.setHpr(0, 0, 0)
                self.elevatorModel3.setPos(0, -1, 0)
            self.elevatorModel4 = loader.loadModel('phase_9/models/cogHQ/ttcc_prop_ms_elevatorBroken.bam')
            locator = self.geom.find('**/elevator_origin4')
            if locator.isEmpty():
                self.elevatorModel4.reparentTo(render)
                self.elevatorModel4.setHpr(0, 0, 0)  # Adjust position
                self.elevatorModel4.setPos(0, -1, 0)
            else:
                self.elevatorModel4.reparentTo(locator)
                self.elevatorModel4.setHpr(0, 0, 0)
                self.elevatorModel4.setPos(0, -1, 0)
            #ddLinkTunnel = self.geom.find('**/tunnel1')
            #ddLinkTunnel.setName('linktunnel_dl_9252_DNARoot')
            # locator = self.geom.find('**/sign_origin')
            # signText = DirectGui.OnscreenText(text=TTLocalizer.DonaldsDreamland[-1], font=ToontownGlobals.getSuitFont(), scale=3, fg=(0.87, 0.87, 0.87, 1), mayChange=False, parent=self.geom)
            # signText.setPosHpr(locator, 0, 0, 0, 0, 0, 0)
            # signText.setDepthWrite(0)
            self.geom.flattenMedium()
        elif zoneId == ToontownGlobals.BoardbotOfficeLobby:
            self.geom = loader.loadModel(self.factoryExteriorModelPath)
            self.geom.flattenMedium()
        elif zoneId == ToontownGlobals.BoardbotLobby:
            if base.config.GetBool('want-qa-regression', 0):
                self.notify.info('QA-REGRESSION: COGHQ: Visit BoardbotLobby')
            self.geom = loader.loadModel(self.cogHQLobbyModelPath)
            self.geom.flattenMedium()
        else:
            self.notify.warning('loadPlaceGeom: unclassified zone %s' % zoneId)
        CogHQLoader.CogHQLoader.loadPlaceGeom(self, zoneId)

    def unload(self):
        CogHQLoader.CogHQLoader.unload(self)
        Toon.unloadCashbotHQAnims()

    def enterBoardOfficeInterior(self, requestStatus):
        self.placeClass = BoardOfficeInterior.BoardOfficeInterior
        self.boardofficeId = requestStatus['boardofficeId']
        self.enterPlace(requestStatus)

    def exitBoardOfficeInterior(self):
        self.exitPlace()
        self.placeClass = None
        del self.boardofficeId
        return

    def getExteriorPlaceClass(self):
        return BoardbotHQExterior.BoardbotHQExterior

    def getBossPlaceClass(self):
        return CashbotHQBossBattle.CashbotHQBossBattle
		
    def enterFactoryExterior(self, requestStatus):
        self.placeClass = BoardbotOfficeExterior.BoardbotOfficeExterior
        self.enterPlace(requestStatus)
        self.hood.spawnTitleText(requestStatus['zoneId'])

    def exitFactoryExterior(self):
        taskMgr.remove('titleText')
        self.hood.hideTitleText()
        self.exitPlace()
        self.placeClass = None