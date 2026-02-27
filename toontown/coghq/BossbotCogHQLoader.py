from direct.directnotify import DirectNotifyGlobal
from direct.fsm import StateData
from toontown.coghq import CogHQLoader
from toontown.toonbase import ToontownGlobals
from direct.gui import DirectGui
from toontown.toonbase import TTLocalizer
from toontown.toon import Toon
from direct.fsm import State
from toontown.battle.BattleProps import *
from toontown.coghq import BossbotHQExterior
from toontown.coghq import BossbotHQBossBattle
from toontown.coghq import BossbotOfficeExterior
from toontown.coghq import CountryClubInterior
from pandac.PandaModules import DecalEffect, TextEncoder
import random
aspectSF = 0.7227

class BossbotCogHQLoader(CogHQLoader.CogHQLoader):
    notify = DirectNotifyGlobal.directNotify.newCategory('BossbotCogHQLoader')

    def __init__(self, hood, parentFSMState, doneEvent):
        CogHQLoader.CogHQLoader.__init__(self, hood, parentFSMState, doneEvent)
        self.fsm.addState(State.State('countryClubInterior', self.enterCountryClubInterior, self.exitCountryClubInterior, ['quietZone', 'cogHQExterior']))
        for stateName in ['start', 'cogHQExterior', 'quietZone']:
            state = self.fsm.getStateNamed(stateName)
            state.addTransition('countryClubInterior')

        self.musicFile = random.choice(['phase_12/audio/bgm/Bossbot_Entry_v1.ogg', 'phase_12/audio/bgm/Bossbot_Entry_v2.ogg', 'phase_12/audio/bgm/Bossbot_Entry_v3.ogg'])
        self.cogHQExteriorModelPath = 'phase_12/models/bossbotHQ/CogGolfHub'
        self.factoryExteriorModelPath = 'phase_11/models/lawbotHQ/LB_DA_Lobby'
        self.cogHQLobbyModelPath = 'phase_12/models/bossbotHQ/BossbotLobby'
        self.geom = None

    def load(self, zoneId):
        CogHQLoader.CogHQLoader.load(self, zoneId)
        Toon.loadBossbotHQAnims()

    def unloadPlaceGeom(self):
        if self.geom:
            self.geom.removeNode()
            self.geom = None
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
        CogHQLoader.CogHQLoader.unloadPlaceGeom(self)

    def loadPlaceGeom(self, zoneId):
        self.notify.info('loadPlaceGeom: %s' % zoneId)
        zoneId = zoneId - zoneId % 100
        self.notify.debug('zoneId = %d ToontownGlobals.BossbotHQ=%d' % (zoneId, ToontownGlobals.BossbotHQ))
        if zoneId == ToontownGlobals.BossbotHQ:
            self.helicopter = globalPropPool.getProp('CogNationChopper')
            self.helicopter.loop('CogNationChopper')
            self.helicopter.reparentTo(render)
            self.helicopter.setHpr(868.959, 0, 0)  # Adjust position
            self.helicopter.setPos(29.3427, -51.9375, 0.025)
            self.helicopter.setScale(0.75)
            self.lightPost = loader.loadModel('phase_14/models/props/CN-streetlight.bam')
            self.lightPost.reparentTo(render)
            self.lightPost.setHpr(629.967, 0, 0)  # Adjust position
            self.lightPost.setPos(84.8929, 154.228, 0.025)
            self.lightPost.setScale(2.0)
            self.lightPost2 = loader.loadModel('phase_14/models/props/CN-streetlight.bam')
            self.lightPost2.reparentTo(render)
            self.lightPost2.setHpr(450.51, 0, 0) # Adjust position
            self.lightPost2.setPos(40.4167, 154.254, 0.025)
            self.lightPost2.setScale(2.0)
            self.lightPost3 = loader.loadModel('phase_14/models/props/CN-streetlight.bam')
            self.lightPost3.reparentTo(render)
            self.lightPost3.setHpr(449.49, 0, 0) # Adjust position
            self.lightPost3.setPos(52.6975, 179.591, 0.025)
            self.lightPost3.setScale(2.0)
            self.lightPost4 = loader.loadModel('phase_14/models/props/CN-streetlight.bam')
            self.lightPost4.reparentTo(render)
            self.lightPost4.setHpr(627.188, 0, 0) # Adjust position
            self.lightPost4.setPos(73.5187, 179.406, 0.025)
            self.lightPost4.setScale(2.0)
            self.lightPost5 = loader.loadModel('phase_14/models/props/CN-streetlight.bam')
            self.lightPost5.reparentTo(render)
            self.lightPost5.setHpr(629.492, 0, 0) # Adjust position
            self.lightPost5.setPos(73.0005, 211.505, 0.025)
            self.lightPost5.setScale(2.0)
            self.lightPost6 = loader.loadModel('phase_14/models/props/CN-streetlight.bam')
            self.lightPost6.reparentTo(render)
            self.lightPost6.setHpr(447.533, 0, 0) # Adjust position
            self.lightPost6.setPos(52.7881, 212.166, 0.0255188)
            self.lightPost6.setScale(2.0)
            self.lightPost7 = loader.loadModel('phase_14/models/props/CN-streetlight.bam')
            self.lightPost7.reparentTo(render)
            self.lightPost7.setHpr(38.4983, 0, 0) # Adjust position
            self.lightPost7.setPos(74.6562, 131.042, 0.275)
            self.lightPost7.setScale(2.0)
            self.lightPost8 = loader.loadModel('phase_14/models/props/CN-streetlight.bam')
            self.lightPost8.reparentTo(render)
            self.lightPost8.setHpr(-49.6244, 0, 0) # Adjust position
            self.lightPost8.setPos(51.0679, 129.965, 0.275)
            self.lightPost8.setScale(2.0)
            self.geom = loader.loadModel(self.cogHQExteriorModelPath)
            gzLinkTunnel = self.geom.find('**/LinkTunnel1')
            gzLinkTunnel.setName('linktunnel_oz_6320_DNARoot')
            self.makeSigns()
            top = self.geom.find('**/TunnelEntrance')
            origin = top.find('**/tunnel_origin')
            origin.setH(-33.33)
            self.geom.flattenMedium()
        elif zoneId == ToontownGlobals.BossbotLobby:
            if base.config.GetBool('want-qa-regression', 0):
                self.notify.info('QA-REGRESSION: COGHQ: Visit BossbotLobby')
            self.notify.debug('cogHQLobbyModelPath = %s' % self.cogHQLobbyModelPath)
            self.geom = loader.loadModel(self.cogHQLobbyModelPath)
            self.geom.flattenMedium()
        else:
            self.notify.warning('loadPlaceGeom: unclassified zone %s' % zoneId)
        CogHQLoader.CogHQLoader.loadPlaceGeom(self, zoneId)

    def makeSigns(self):

        def makeSign(topStr, signStr, textId):
            top = self.geom.find('**/' + topStr)
            sign = top.find('**/' + signStr)
            locator = top.find('**/sign_origin')
            signText = DirectGui.OnscreenText(text=TextEncoder.upper(TTLocalizer.GlobalStreetNames[textId][-1]), font=ToontownGlobals.getSuitFont(), scale=TTLocalizer.BCHQLsignText, fg=(0, 0, 0, 1), parent=sign)
            signText.setPosHpr(locator, 0, -0.1, -0.25, 0, 0, 0)
            signText.setDepthWrite(0)

        makeSign('Gate_2', 'Sign_6', 10700)
        makeSign('TunnelEntrance', 'Sign_2', 6300)
        makeSign('Gate_3', 'Sign_3', 10600)
        makeSign('Gate_4', 'Sign_4', 10500)
        makeSign('GateHouse', 'Sign_5', 10200)

    def unload(self):
        CogHQLoader.CogHQLoader.unload(self)
        Toon.unloadSellbotHQAnims()

    def enterStageInterior(self, requestStatus):
        self.placeClass = StageInterior.StageInterior
        self.stageId = requestStatus['stageId']
        self.enterPlace(requestStatus)

    def exitStageInterior(self):
        self.exitPlace()
        self.placeClass = None
        return

    def getExteriorPlaceClass(self):
        self.notify.debug('getExteriorPlaceClass')
        return BossbotHQExterior.BossbotHQExterior

    def getBossPlaceClass(self):
        self.notify.debug('getBossPlaceClass')
        return BossbotHQBossBattle.BossbotHQBossBattle

    def enterFactoryExterior(self, requestStatus):
        self.placeClass = BossbotOfficeExterior.BossbotOfficeExterior
        self.enterPlace(requestStatus)

    def exitFactoryExterior(self):
        taskMgr.remove('titleText')
        self.hood.hideTitleText()
        self.exitPlace()
        self.placeClass = None
        return

    def enterCogHQBossBattle(self, requestStatus):
        self.notify.debug('BossbotCogHQLoader.enterCogHQBossBattle')
        CogHQLoader.CogHQLoader.enterCogHQBossBattle(self, requestStatus)
        base.cr.forbidCheesyEffects(1)

    def exitCogHQBossBattle(self):
        self.notify.debug('BossbotCogHQLoader.exitCogHQBossBattle')
        CogHQLoader.CogHQLoader.exitCogHQBossBattle(self)
        base.cr.forbidCheesyEffects(0)

    def enterCountryClubInterior(self, requestStatus):
        self.placeClass = CountryClubInterior.CountryClubInterior
        self.notify.info('enterCountryClubInterior, requestStatus=%s' % requestStatus)
        self.countryClubId = requestStatus['countryClubId']
        self.enterPlace(requestStatus)

    def exitCountryClubInterior(self):
        self.exitPlace()
        self.placeClass = None
        del self.countryClubId
        return