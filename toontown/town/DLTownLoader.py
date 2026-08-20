from direct.fsm import State
from toontown.suit import Suit
from toontown.town import DLStreet
from toontown.town import TownLoader
from toontown.hood import ZoneUtil
from toontown.toonbase import ToontownGlobals
from toontown.building import PacesetterInstanceGlobals
from toontown.building import MotoroomInstanceGlobals


class DLTownLoader(TownLoader.TownLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        TownLoader.TownLoader.__init__(self, hood, parentFSM, doneEvent)
        self.streetClass = DLStreet.DLStreet
        self.musicFile = 'phase_8/audio/bgm/DL_SZ.ogg'
        self.activityMusicFile = 'phase_8/audio/bgm/DL_SZ_activity.ogg'
        self.townStorageDNAFile = 'phase_8/dna/storage_DL_town.dna'

        # Pacesetter's lobby is on Lullaby Lane.  The dynamic encounter stays
        # inside this already-loaded town loader instead of being handed to a
        # normal Cog-HQ boss loader.
        pacesetterState = State.State(
            PacesetterInstanceGlobals.BOSS_BATTLE_STATE,
            self.enterPacesetterBossBattle,
            self.exitPacesetterBossBattle,
            ['quietZone'])
        self.fsm.addState(pacesetterState)
        self.fsm.getStateNamed('start').addTransition(
            PacesetterInstanceGlobals.BOSS_BATTLE_STATE)
        self.fsm.getStateNamed('quietZone').addTransition(
            PacesetterInstanceGlobals.BOSS_BATTLE_STATE)

        motoroomState = State.State(
            MotoroomInstanceGlobals.INSTANCE_STATE,
            self.enterMotoroom,
            self.exitMotoroom,
            ['quietZone'])
        self.fsm.addState(motoroomState)
        self.fsm.getStateNamed('start').addTransition(
            MotoroomInstanceGlobals.INSTANCE_STATE)
        self.fsm.getStateNamed('quietZone').addTransition(
            MotoroomInstanceGlobals.INSTANCE_STATE)

    def load(self, zoneId):
        TownLoader.TownLoader.load(self, zoneId)
        Suit.loadSuits(3)
        dnaFile = ('phase_8/dna/donalds_dreamland_' +
                   str(self.canonicalBranchZone) + '.dna')
        self.createHood(dnaFile)

    def unload(self):
        TownLoader.TownLoader.unload(self)
        Suit.unloadSuits(3)


    def enterMotoroom(self, requestStatus):
        from toontown.instances import MotoroomPlace

        self.acceptOnce(self.placeDoneEvent, self.handleMotoroomDone)
        state = self.fsm.getStateNamed(MotoroomInstanceGlobals.INSTANCE_STATE)
        self.place = MotoroomPlace.MotoroomPlace(
            self, state, self.placeDoneEvent)
        base.cr.playGame.setPlace(self.place)
        self.place.load()
        self.place.enter(requestStatus)

    def exitMotoroom(self):
        self.ignore(self.placeDoneEvent)
        if self.place:
            self.place.exit()
            self.place.unload()
            self.place = None
            base.cr.playGame.setPlace(None)

    def handleMotoroomDone(self):
        status = self.place.doneStatus
        if (ZoneUtil.getBranchZone(status['zoneId']) == self.branchZone and
                status['shardId'] is None):
            self.fsm.request('quietZone', [status])
        else:
            self.doneStatus = status
            messenger.send(self.doneEvent)

    def enterPacesetterBossBattle(self, requestStatus):
        from toontown.coghq import PacesetterBossBattle

        self.acceptOnce(
            self.placeDoneEvent, self.handlePacesetterBossBattleDone)
        self.place = PacesetterBossBattle.PacesetterBossBattle(
            self, self.fsm, self.placeDoneEvent)
        base.cr.playGame.setPlace(self.place)
        self.place.load()

        base.localAvatar.setCameraFov(ToontownGlobals.CogHQCameraFov)
        base.camLens.setNearFar(ToontownGlobals.DefaultCameraNear,
                               ToontownGlobals.DefaultCameraFar)
        base.cr.forbidCheesyEffects(1)
        self.place.enter(requestStatus)

    def exitPacesetterBossBattle(self):
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

    def handlePacesetterBossBattleDone(self):
        status = self.place.doneStatus
        if (status.get('loader') ==
                PacesetterInstanceGlobals.INSTANCE_LOADER and
                ZoneUtil.getBranchZone(status['zoneId']) == self.branchZone and
                status.get('shardId') is None):
            self.fsm.request('quietZone', [status])
        else:
            self.doneStatus = status
            messenger.send(self.doneEvent)