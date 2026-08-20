from __future__ import absolute_import
from direct.fsm import State

from toontown.suit import Suit
from toontown.town import OZStreet
from toontown.town import TownLoader
from toontown.hood import ZoneUtil
from toontown.toonbase import ToontownGlobals
from toontown.building import ChainsawInstanceGlobals


class OZTownLoader(TownLoader.TownLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        TownLoader.TownLoader.__init__(self, hood, parentFSM, doneEvent)
        self.streetClass = OZStreet.OZStreet
        self.musicFile = 'phase_6/audio/bgm/AA_SZ.ogg'
        self.activityMusicFile = 'phase_6/audio/bgm/AA_SZ_activity.ogg'
        self.townStorageDNAFile = 'phase_6/dna/storage_OZ_town.dna'

        chainsawState = State.State(
            ChainsawInstanceGlobals.BOSS_BATTLE_STATE,
            self.enterChainsawBossBattle,
            self.exitChainsawBossBattle,
            ['quietZone'])
        self.fsm.addState(chainsawState)
        self.fsm.getStateNamed('start').addTransition(
            ChainsawInstanceGlobals.BOSS_BATTLE_STATE)
        self.fsm.getStateNamed('quietZone').addTransition(
            ChainsawInstanceGlobals.BOSS_BATTLE_STATE)

    def load(self, zoneId):
        TownLoader.TownLoader.load(self, zoneId)
        Suit.loadSuits(2)
        dnaFile = ('phase_6/dna/outdoor_zone_' +
                   str(self.canonicalBranchZone) + '.pdna')
        self.createHood(dnaFile)

    def unload(self):
        TownLoader.TownLoader.unload(self)
        Suit.unloadSuits(2)

    def enterChainsawBossBattle(self, requestStatus):
        if requestStatus.get('minibossId') != ChainsawInstanceGlobals.CHAINSAW:
            self.notify.error(
                'Unknown Chainsaw miniboss instance: %r' %
                requestStatus.get('minibossId'))
            return

        from toontown.coghq import ChainsawBossBattle
        self.acceptOnce(
            self.placeDoneEvent, self.handleChainsawBossBattleDone)
        self.place = ChainsawBossBattle.ChainsawBossBattle(
            self, self.fsm, self.placeDoneEvent)
        base.cr.playGame.setPlace(self.place)
        self.place.load()

        base.localAvatar.setCameraFov(ToontownGlobals.CogHQCameraFov)
        base.camLens.setNearFar(
            ToontownGlobals.DefaultCameraNear,
            ToontownGlobals.DefaultCameraFar)
        base.cr.forbidCheesyEffects(1)
        self.place.enter(requestStatus)

    def exitChainsawBossBattle(self):
        self.ignore(self.placeDoneEvent)
        if self.place:
            self.place.exit()
            self.place.unload()
            self.place = None
            base.cr.playGame.setPlace(None)

        base.cr.forbidCheesyEffects(0)
        base.localAvatar.setCameraFov(settings['fieldofview'])
        base.camLens.setNearFar(
            ToontownGlobals.DefaultCameraNear,
            ToontownGlobals.DefaultCameraFar)

    def handleChainsawBossBattleDone(self):
        status = self.place.doneStatus
        if (status.get('loader') == ChainsawInstanceGlobals.INSTANCE_LOADER and
                ZoneUtil.getBranchZone(status['zoneId']) == self.branchZone and
                status.get('shardId') is None):
            self.fsm.request('quietZone', [status])
        else:
            self.doneStatus = status
            messenger.send(self.doneEvent)
