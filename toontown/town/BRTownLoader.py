from direct.fsm import State
from toontown.battle import BattleParticles
from toontown.suit import Suit
from toontown.town import BRStreet
from toontown.town import TownLoader
from toontown.hood import ZoneUtil
from toontown.toonbase import ToontownGlobals
from toontown.building import PlutocratInstanceGlobals

class BRTownLoader(TownLoader.TownLoader):
    
    def __init__(self, hood, parentFSM, doneEvent):
        TownLoader.TownLoader.__init__(self, hood, parentFSM, doneEvent)
        self.streetClass = BRStreet.BRStreet
        self.musicFile = 'phase_8/audio/bgm/TB_SZ.ogg'
        self.activityMusicFile = 'phase_8/audio/bgm/TB_SZ_activity.ogg'
        self.townStorageDNAFile = 'phase_8/dna/storage_BR_town.pdna'

        plutocratState = State.State(
            PlutocratInstanceGlobals.BOSS_BATTLE_STATE,
            self.enterPlutocratBossBattle,
            self.exitPlutocratBossBattle,
            ['quietZone'])
        self.fsm.addState(plutocratState)
        self.fsm.getStateNamed('start').addTransition(PlutocratInstanceGlobals.BOSS_BATTLE_STATE)
        self.fsm.getStateNamed('quietZone').addTransition(PlutocratInstanceGlobals.BOSS_BATTLE_STATE)

    def load(self, zoneId):
        TownLoader.TownLoader.load(self, zoneId)
        Suit.loadSuits(3)
        dnaFile = 'phase_8/dna/the_burrrgh_' + str(self.canonicalBranchZone) + '.pdna'
        self.createHood(dnaFile)
        self.windSound = map(base.loader.loadSfx, ['phase_8/audio/sfx/SZ_TB_wind_1.ogg',
                                            'phase_8/audio/sfx/SZ_TB_wind_2.ogg',
                                            'phase_8/audio/sfx/SZ_TB_wind_3.ogg'])
        self.snow = BattleParticles.loadParticleFile('snowdisk.ptf')
        self.snow.setPos(0, 0, 5)
        self.snowRender = self.geom.attachNewNode('snowRender')
        self.snowRender.setDepthWrite(0)
        self.snowRender.setBin('fixed', 1)

    def unload(self):
        TownLoader.TownLoader.unload(self)
        Suit.unloadSuits(3)
        del self.windSound
        del self.snow
        del self.snowRender

    def enter(self, requestStatus):
        TownLoader.TownLoader.enter(self, requestStatus)
        self.snow.start(camera, self.snowRender)

    def exit(self):
        TownLoader.TownLoader.exit(self)
        self.snow.cleanup()
        self.snowRender.removeNode()

    def enterPlutocratBossBattle(self, requestStatus):
        if requestStatus.get('minibossId') != PlutocratInstanceGlobals.PLUTOCRAT:
            self.notify.error('Unknown Plutocrat miniboss instance: %r' % requestStatus.get('minibossId'))
            return
        from toontown.coghq import PlutocratBossBattle
        self.acceptOnce(self.placeDoneEvent, self.handlePlutocratBossBattleDone)
        self.place = PlutocratBossBattle.PlutocratBossBattle(self, self.fsm, self.placeDoneEvent)
        base.cr.playGame.setPlace(self.place)
        self.place.load()
        base.localAvatar.setCameraFov(ToontownGlobals.CogHQCameraFov)
        base.camLens.setNearFar(ToontownGlobals.DefaultCameraNear, ToontownGlobals.DefaultCameraFar)
        base.cr.forbidCheesyEffects(1)
        self.place.enter(requestStatus)

    def exitPlutocratBossBattle(self):
        self.ignore(self.placeDoneEvent)
        if self.place:
            self.place.exit()
            self.place.unload()
            self.place = None
            base.cr.playGame.setPlace(None)
        base.cr.forbidCheesyEffects(0)
        base.localAvatar.setCameraFov(settings['fieldofview'])
        base.camLens.setNearFar(ToontownGlobals.DefaultCameraNear, ToontownGlobals.DefaultCameraFar)

    def handlePlutocratBossBattleDone(self):
        status = self.place.doneStatus
        if (status.get('loader') == PlutocratInstanceGlobals.INSTANCE_LOADER and
                ZoneUtil.getBranchZone(status['zoneId']) == self.branchZone and
                status.get('shardId') is None):
            self.fsm.request('quietZone', [status])
        else:
            self.doneStatus = status
            messenger.send(self.doneEvent)
