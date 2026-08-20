from __future__ import absolute_import
from direct.directnotify import DirectNotifyGlobal
from direct.fsm import StateData
from . import CogHQLoader
from toontown.toonbase import ToontownGlobals
from direct.gui import DirectGui
from toontown.toonbase import TTLocalizer
from toontown.battle.BattleProps import *
from toontown.toon import Toon
from direct.fsm import State
from toontown.coghq import CogHQLoader
from . import TechbotHQExterior
from . import BoardbotOfficeExterior
from toontown.coghq.boardbothq import BoardOfficeInterior
from toontown.coghq import CashbotHQBossBattle

aspectSF = 0.7227

class TechbotCogHQLoader(CogHQLoader.CogHQLoader):
    notify = DirectNotifyGlobal.directNotify.newCategory('TechbotCogHQLoader')

    def __init__(self, hood, parentFSMState, doneEvent):
        CogHQLoader.CogHQLoader.__init__(self, hood, parentFSMState, doneEvent)
        self.fsm.addState(State.State('techofficeInterior', self.enterBoardOfficeInterior, self.exitBoardOfficeInterior, ['quietZone', 'cogHQExterior']))
        for stateName in ['start', 'cogHQExterior', 'quietZone']:
            state = self.fsm.getStateNamed(stateName)
            state.addTransition('techofficeInterior')

        self.musicFile = 'phase_14/audio/bgm/BD_courtyard.ogg'
        self.cogHQExteriorModelPath = 'phase_11/models/techbotHQ/TechbotPG'
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
        CogHQLoader.CogHQLoader.unloadPlaceGeom(self)

    def loadPlaceGeom(self, zoneId):
        self.notify.info('loadPlaceGeom: %s' % zoneId)
        zoneId = zoneId - zoneId % 100
        if zoneId == ToontownGlobals.TechbotHQ:
            self.geom = loader.loadModel(self.cogHQExteriorModelPath)
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
        return TechbotHQExterior.TechbotHQExterior

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