from __future__ import absolute_import
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

        self.musicFile = random.choice(['phase_12/audio/bgm/BB_courtyard.ogg', 'phase_12/audio/bgm/BB_courtyard_2.ogg'])
        self.lobbyMusicFile = 'phase_12/audio/bgm/BB_boss_lobby.ogg'
        self.battleMusic = 'phase_12/audio/bgm/BB_courtyard_encntr.ogg'
        self.cogHQExteriorModelPath = 'phase_12/models/bossbotHQ/ttr_m_ara_bhq_bossbotCourtyard'
        self.factoryExteriorModelPath = 'phase_11/models/lawbotHQ/LB_DA_Lobby'
        self.cogHQLobbyModelPath = 'phase_12/models/bossbotHQ/BossbotLobby'
        self.geom = None

    def load(self, zoneId):
        self.battleMusic = 'phase_11/audio/bgm/LB_courtyard_encntr.ogg'
        CogHQLoader.CogHQLoader.load(self, zoneId)
        Toon.loadBossbotHQAnims()

    def enter(self, requestStatus):
        if self.geom is None or self.geom.isEmpty():
            if requestStatus.get('where') == 'cogHQLobby':
                self.loadPlaceGeom(ToontownGlobals.BossbotLobby)
            else:
                self.loadPlaceGeom(ToontownGlobals.BossbotHQ)
        CogHQLoader.CogHQLoader.enter(self, requestStatus)

    def unloadPlaceGeom(self):
        if self.geom and not self.geom.isEmpty():
            self.geom.removeNode()
        self.geom = None
        self.helicopter = None
        self.dish = None
        self.lightPost = None
        self.lightPost2 = None
        self.lightPost3 = None
        self.lightPost4 = None
        self.lightPost5 = None
        self.lightPost6 = None

    def loadPlaceGeom(self, zoneId):
        zoneId = zoneId - zoneId % 100

        if self.geom and not self.geom.isEmpty():
            self.geom.removeNode()
        self.geom = None

        if zoneId == ToontownGlobals.BossbotHQ:
            self.geom = loader.loadModel(self.cogHQExteriorModelPath)

            if self.geom is None or self.geom.isEmpty():
                self.notify.error('Unable to load Bossbot HQ exterior model: %s' % self.cogHQExteriorModelPath)
                return

            gzLinkTunnel = self.geom.find('**/LinkTunnel1')
            if not gzLinkTunnel.isEmpty():
                gzLinkTunnel.setName('linktunnel_oz_6320_DNARoot')

            self.helicopter = globalPropPool.getProp('CogNationChopper')
            if self.helicopter and not self.helicopter.isEmpty():
                self.helicopter.reparentTo(self.geom)
                self.helicopter.setPosHprScale(-167.277, 33.2723, 3.9249, 90, 0, 0, 0.75, 0.75, 0.75)
                self.helicopter.loop('CogNationChopper')

            self.dish = loader.loadModel('phase_14/models/props/radar.bam')
            if self.dish and not self.dish.isEmpty():
                self.dish.reparentTo(self.geom)
                self.dish.setPosHprScale(-248.467, -18.5363, 13.9249, -10, 0, 0, 0.25, 0.25, 0.25)

            lightData = (
                (-140.322, -63.0132, 3.92496, 899.728),
                (-140.424, -26.7279, 3.92527, 1082.18),
                (-140.368, 62.8114, 3.92538, 1079.88),
                (-140.235, 26.7049, 3.92398, 1259.28),
                (290.832, 9.65186, 0.0249996, 1445.4),
                (292.982, -8.64156, 0.024999, 1624.35),
            )

            lights = []
            for x, y, z, h in lightData:
                light = loader.loadModel('phase_14/models/props/CN-streetlight.bam')
                if light and not light.isEmpty():
                    light.reparentTo(self.geom)
                    light.setPosHprScale(x, y, z, h, 0, 0, 2, 2, 2)
                lights.append(light)

            self.lightPost = lights[0]
            self.lightPost2 = lights[1]
            self.lightPost3 = lights[2]
            self.lightPost4 = lights[3]
            self.lightPost5 = lights[4]
            self.lightPost6 = lights[5]

        elif zoneId == ToontownGlobals.BossbotLobby:
            self.geom = loader.loadModel(self.cogHQLobbyModelPath)
            if self.geom is None or self.geom.isEmpty():
                self.notify.error('Unable to load Bossbot lobby model: %s' % self.cogHQLobbyModelPath)
                return
        else:
            self.notify.warning('loadPlaceGeom: unclassified zone %s' % zoneId)

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