from __future__ import absolute_import
from direct.fsm import State
from toontown.suit import Suit
from toontown.town import MMStreet
from toontown.town import TownLoader
from toontown.hood import ZoneUtil
from toontown.toonbase import ToontownGlobals
from toontown.building import MajorPlayerInstanceGlobals


class MMTownLoader(TownLoader.TownLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        TownLoader.TownLoader.__init__(self, hood, parentFSM, doneEvent)
        self.streetClass = MMStreet.MMStreet
        self.musicFile = 'phase_6/audio/bgm/MM_SZ.ogg'
        self.activityMusicFile = 'phase_6/audio/bgm/MM_SZ_activity.ogg'
        self.townStorageDNAFile = 'phase_6/dna/storage_MM_town.pdna'

        instanceState = State.State(
            MajorPlayerInstanceGlobals.BOSS_BATTLE_STATE,
            self.enterMajorPlayerBossBattle,
            self.exitMajorPlayerBossBattle,
            ['quietZone'])
        self.fsm.addState(instanceState)
        self.fsm.getStateNamed('start').addTransition(
            MajorPlayerInstanceGlobals.BOSS_BATTLE_STATE)
        self.fsm.getStateNamed('quietZone').addTransition(
            MajorPlayerInstanceGlobals.BOSS_BATTLE_STATE)

    def load(self, zoneId):
        TownLoader.TownLoader.load(self, zoneId)
        Suit.loadSuits(2)
        dnaFile = 'phase_6/dna/minnies_melody_land_' + str(self.canonicalBranchZone) + '.pdna'
        self.createHood(dnaFile)

    def unload(self):
        TownLoader.TownLoader.unload(self)
        Suit.unloadSuits(2)

    def getMajorPlayerBossPlaceClass(self, instanceId):
        if instanceId in (MajorPlayerInstanceGlobals.HIGH_ROLLER,
                          MajorPlayerInstanceGlobals.VIDEOGRAPHER):
            from toontown.coghq import HighRollerBossBattle
            return HighRollerBossBattle.HighRollerBossBattle
        return None

    def enterMajorPlayerBossBattle(self, requestStatus):
        instanceId = requestStatus.get('minibossId')
        placeClass = self.getMajorPlayerBossPlaceClass(instanceId)
        if placeClass is None:
            self.notify.error(
                'Unknown Major Player miniboss instance: %r' % instanceId)
            return

        self.acceptOnce(
            self.placeDoneEvent, self.handleMajorPlayerBossBattleDone)
        self.place = placeClass(self, self.fsm, self.placeDoneEvent)
        base.cr.playGame.setPlace(self.place)
        self.place.load()

        base.localAvatar.setCameraFov(ToontownGlobals.CogHQCameraFov)
        base.camLens.setNearFar(ToontownGlobals.DefaultCameraNear,
                               ToontownGlobals.DefaultCameraFar)
        base.cr.forbidCheesyEffects(1)
        self.place.enter(requestStatus)

    def exitMajorPlayerBossBattle(self):
        self.ignore(self.placeDoneEvent)
        if self.place:
            self.place.exit()
            self.place.unload()
            self.place = None
            base.cr.playGame.setPlace(None)

        base.cr.forbidCheesyEffects(0)
        base.localAvatar.setCameraFov(settings['fieldofview'])
        base.camLens.setNearFar(ToontownGlobals.DefaultCameraNear,
                               ToontownGlobals.DefaultCameraFar)

    def handleMajorPlayerBossBattleDone(self):
        status = self.place.doneStatus
        if (status.get('loader') ==
                MajorPlayerInstanceGlobals.INSTANCE_LOADER and
                ZoneUtil.getBranchZone(status['zoneId']) == self.branchZone and
                status.get('shardId') is None):
            self.fsm.request('quietZone', [status])
        else:
            self.doneStatus = status
            messenger.send(self.doneEvent)
