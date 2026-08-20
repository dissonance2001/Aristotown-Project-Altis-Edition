from __future__ import absolute_import
from direct.fsm import State
from toontown.battle import BattleParticles
from toontown.suit import Suit
from toontown.town import BRStreet
from toontown.town import TownLoader
from toontown.hood import ZoneUtil
from toontown.toonbase import ToontownGlobals
from toontown.building import PlutocratInstanceGlobals
from toontown.building import CountErfitInstanceGlobals
from toontown.dna.DNAParser import DNABulkLoader
from toontown.dna import DNAStorage
from pandac.PandaModules import NodePath
from six.moves import map
from six.moves import range

class BRTownLoader(TownLoader.TownLoader):
    
    def __init__(self, hood, parentFSM, doneEvent):
        TownLoader.TownLoader.__init__(self, hood, parentFSM, doneEvent)
        self.streetClass = BRStreet.BRStreet
        self.musicFile = 'phase_8/audio/bgm/TB_SZ.ogg'
        self.activityMusicFile = 'phase_8/audio/bgm/TB_SZ_activity.ogg'
        self.townStorageDNAFile = 'phase_8/dna/storage_BR_town.pdna'
        self.countErfitBuilding = None
        self.countErfitBuildingParent = None
        self.countErfitWalls = None
        self.countErfitDecorations = []
        self.countErfitDecorationRoot = None
        self.erfitLobbyMusicFile = 'phase_13/audio/bgm/april_toons/erfit/erfit_lobby.ogg'
        self.erfitLobbyMusic = None

        plutocratState = State.State(
            PlutocratInstanceGlobals.BOSS_BATTLE_STATE,
            self.enterPlutocratBossBattle,
            self.exitPlutocratBossBattle,
            ['quietZone'])
        self.fsm.addState(plutocratState)
        self.fsm.getStateNamed('start').addTransition(PlutocratInstanceGlobals.BOSS_BATTLE_STATE)
        self.fsm.getStateNamed('quietZone').addTransition(PlutocratInstanceGlobals.BOSS_BATTLE_STATE)


        countErfitState = State.State(
            CountErfitInstanceGlobals.BOSS_BATTLE_STATE,
            self.enterCountErfitBossBattle,
            self.exitCountErfitBossBattle,
            ['quietZone'])
        self.fsm.addState(countErfitState)
        self.fsm.getStateNamed('start').addTransition(CountErfitInstanceGlobals.BOSS_BATTLE_STATE)
        self.fsm.getStateNamed('quietZone').addTransition(CountErfitInstanceGlobals.BOSS_BATTLE_STATE)

    def load(self, zoneId):
        TownLoader.TownLoader.load(self, zoneId)
        self.erfitLobbyMusic = base.loader.loadMusic(self.erfitLobbyMusicFile)
        Suit.loadSuits(3)
        dnaFile = 'phase_8/dna/the_burrrgh_' + str(self.canonicalBranchZone) + '.pdna'
        self.createHood(dnaFile)
        self.loadCountErfitBuilding()
        self.loadCountErfitWalls()
        self.loadCountErfitDecorations()
        self.windSound = list(map(base.loader.loadSfx, ['phase_8/audio/sfx/SZ_TB_wind_1.ogg',
                                            'phase_8/audio/sfx/SZ_TB_wind_2.ogg',
                                            'phase_8/audio/sfx/SZ_TB_wind_3.ogg']))
        self.snow = BattleParticles.loadParticleFile('snowdisk.ptf')
        self.snow.setPos(0, 0, 5)
        self.snowRender = self.geom.attachNewNode('snowRender')
        self.snowRender.setDepthWrite(0)
        self.snowRender.setBin('fixed', 1)

    def _countErfitAngleDistance(self, a, b):
        distance = abs((a - b) % 360.0)
        if distance > 180.0:
            distance = 360.0 - distance
        return distance

    def _findCountErfitNode(self, pattern, x, y, z, h = None):
        candidates = self.geom.findAllMatches(pattern + ';+s')
        for i in range(candidates.getNumPaths()):
            node = candidates.getPath(i)
            pos = node.getPos(self.geom)
            if abs(pos.getX() - x) > 0.08:
                continue
            if abs(pos.getY() - y) > 0.08:
                continue
            if abs(pos.getZ() - z) > 0.08:
                continue
            if h is not None:
                hpr = node.getHpr(self.geom)
                if self._countErfitAngleDistance(hpr.getX(), h) > 0.75:
                    continue
            return node
        return None

    def prepareHoodGeometryBeforeFlatten(self):
        if self.canonicalBranchZone != ToontownGlobals.PolarPlace:
            return
        oldBuilding = self.geom.find('**/tb33:toon_landmark_BR_A2_DNARoot')
        if not oldBuilding.isEmpty():
            self.countErfitBuildingParent = oldBuilding.getParent()
            oldBuilding.stash()
        oldEntrance = self.geom.find('**/HW_candlegame-candle_DNARoot')
        if not oldEntrance.isEmpty():
            oldEntrance.stash()
        decorationPlaceholders = [
            ('**/HW_20_pumpkin_short_DNARoot', 116.973, 58.9899, 0.0, 135.0),
            ('**/HW_candle_stick_lit_DNARoot', 113.284, 58.3366, 0.0, 150.0),
            ('**/HW_candle_stick_lit_DNARoot', 119.121, 57.2391, 0.0, -135.0),
            ('**/HW_TTO_pumpkin_short_DNARoot', 113.0, 82.9994, 0.0, 165.0),
            ('**/gs_mailbox_DNARoot', 122.0, 49.0, 5.0, -90.0),
            ('**/gs_mailbox_DNARoot', 148.0, 49.0, 5.0, -90.0),
            ('**/gs_mailbox_DNARoot', 159.46, 42.9695, 5.0, 60.0),
        ]
        for pattern, x, y, z, h in decorationPlaceholders:
            placeholder = self._findCountErfitNode(pattern, x, y, z, h)
            if placeholder is not None:
                placeholder.stash()
        wallSpecs = [
            (115.0, 69.9994, 0.0, 90.0),
            (115.0, 60.0, 0.0, 90.0),
            (115.0, 45.0, 0.0, 90.0),
            (104.987, 19.9891, 5.0, -90.0),
            (125.0, 19.9901, 5.0, 180.0),
            (104.999, 20.0002, 5.0, 90.0),
            (105.0, 35.0001, 5.0, 90.0),
            (105.0, 45.0, 5.0, 0.0),
            (164.956, 44.9781, 5.0, -90.0),
            (164.98, 19.9902, 5.0, 180.0),
            (155.0, 45.0, 2.0, 0.0),
            (154.999, 59.9994, 0.0, -90.0),
            (155.0, 79.9992, 0.0, -90.0),
        ]
        for x, y, z, h in wallSpecs:
            toonWall = self._findCountErfitNode('**/tb0*', x, y, z, h)
            if toonWall is not None:
                toonWall.stash()

    def loadCountErfitBuilding(self):
        if self.canonicalBranchZone != ToontownGlobals.PolarPlace:
            return
        parent = self.countErfitBuildingParent
        if parent is None or parent.isEmpty():
            parent = self.geom.find('**/3328')
            if parent.isEmpty():
                parent = self.geom
        self.countErfitBuilding = loader.loadModel('phase_13/models/events/halloween/count_office_facade')
        self.countErfitBuilding.reparentTo(parent)
        self.countErfitBuilding.setPos(self.geom, 135.0, 19.9901, 5.0)
        self.countErfitBuilding.setHpr(self.geom, -180.0, 0.0, 0.0)
        self.countErfitBuilding.setScale(1)

    def loadCountErfitWalls(self):
        if self.canonicalBranchZone != ToontownGlobals.PolarPlace:
            return
        parent = self.geom.find('**/3328')
        if parent.isEmpty():
            parent = self.geom
        self.countErfitWalls = parent.attachNewNode('countErfitFieldOfficeWalls')
        wallStore = DNAStorage.DNAStorage()
        dnaBulk = DNABulkLoader(wallStore, ('phase_5/dna/storage_town.pdna',))
        dnaBulk.loadDNAFiles()
        wallSpecs = [
            (115.0, 69.9994, 0.0, 90.0, 10.0, 'wall_cogdo_build1_ur'),
            (115.0, 60.0, 0.0, 90.0, 10.0, 'wall_cogdo_build2_ur'),
            (115.0, 45.0, 0.0, 90.0, 15.0, 'wall_cogdo_build4_ur'),
            (104.987, 19.9891, 5.0, -90.0, 15.0, 'wall_cogdo_build4_ur'),
            (125.0, 19.9901, 5.0, 180.0, 20.7, 'wall_cogdo_build2_ur'),
            (104.999, 20.0002, 5.0, 90.0, 15.0, 'wall_cogdo_build1_ur'),
            (105.0, 35.0001, 5.0, 90.0, 10.0, 'wall_cogdo_build2_ur'),
            (105.0, 45.0, 5.0, 0.0, 10.0, 'wall_cogdo_build4_ur'),
            (164.956, 44.9781, 5.0, -90.0, 25.0, 'wall_cogdo_build4_ur'),
            (164.98, 19.9902, 5.0, 180.0, 20.0, 'wall_cogdo_build2_ur'),
            (155.0, 45.0, 2.0, 0.0, 10.0, 'wall_cogdo_build1_ur'),
            (154.999, 59.9994, 0.0, -90.0, 15.0, 'wall_cogdo_build2_ur'),
            (155.0, 79.9992, 0.0, -90.0, 20.0, 'wall_cogdo_build4_ur'),
        ]
        for x, y, z, h, width, code in wallSpecs:
            wall = wallStore.findNode(code)
            if wall.isEmpty():
                continue
            wall.reparentTo(self.countErfitWalls)
            wall.setPos(self.geom, x, y, z)
            wall.setHpr(self.geom, h, 0, 0)
            wall.setScale(width, 1, 20)
            wall.setColor(1, 1, 1, 1)
        wallStore.cleanup()

    def _loadCountErfitDecoration(self, modelPath, pos, hpr, scale = 1.0, nodeName = None):
        model = loader.loadModel(modelPath)
        if not model:
            return None
        decoration = model
        if nodeName:
            decoration = model.find('**/' + nodeName)
            if decoration.isEmpty():
                model.removeNode()
                return None
            decoration.wrtReparentTo(self.countErfitDecorationRoot)
            model.removeNode()
        else:
            decoration.reparentTo(self.countErfitDecorationRoot)
        decoration.setPos(pos[0], pos[1], pos[2])
        decoration.setHpr(hpr[0], hpr[1], hpr[2])
        decoration.setScale(scale)
        self.countErfitDecorations.append(decoration)
        return decoration

    def loadCountErfitDecorations(self):
        if self.canonicalBranchZone != ToontownGlobals.PolarPlace:
            return
        self.countErfitDecorationRoot = self.geom.attachNewNode('countErfitDecorations')
        self._loadCountErfitDecoration(
            'phase_8/models/props/tt_m_ara_BR_pinetrees_halloween',
            (122.0, 49.0, 5.0), (-90.0, 0.0, 0.0), 1.0,
            'prop_snow_tree_large_woodbox_ul')
        self._loadCountErfitDecoration(
            'phase_8/models/props/tt_m_ara_BR_pinetrees_halloween',
            (148.0, 49.0, 5.0), (-90.0, 0.0, 0.0), 1.0,
            'prop_snow_tree_large_woodbox_ul')
        self._loadCountErfitDecoration(
            'phase_5.5/models/estate/tt_m_ara_int_candlestickLit',
            (113.284, 58.3366, -0.000721931), (150.0, 0.0, 0.0), 1.22)
        self._loadCountErfitDecoration(
            'phase_5.5/models/estate/tt_m_ara_int_candlestickLit',
            (119.121, 57.2391, -0.000722408), (-135.0, 0.0, 0.0), 1.10763)
        self._loadCountErfitDecoration(
            'phase_4/models/estate/pumpkin_short',
            (113.0, 82.9994, 0.0), (165.0, 0.0, 0.0), 1.27902)
        self._loadCountErfitDecoration(
            'phase_13/models/events/halloween/cc_m_eve_hw_prp_pumpkin_short',
            (116.973, 58.9899, 0.0), (135.0, 0.0, 0.0), 1.22024,
            'pumpkin_short_cc')
        self._loadCountErfitDecoration(
            'phase_13/models/events/halloween/cc_m_eve_hw_prp_pumpkin_short',
            (159.46, 42.9695, 5.0), (60.0, 0.0, 0.0), 0.999967,
            'pumpkin_short_cc')

    def unload(self):
        if self.erfitLobbyMusic:
            self.erfitLobbyMusic.stop()
        for decoration in self.countErfitDecorations:
            if not decoration.isEmpty():
                decoration.removeNode()
        self.countErfitDecorations = []
        if self.countErfitDecorationRoot:
            self.countErfitDecorationRoot.removeNode()
            self.countErfitDecorationRoot = None
        if self.countErfitWalls:
            self.countErfitWalls.removeNode()
            self.countErfitWalls = None
        if self.countErfitBuilding:
            self.countErfitBuilding.removeNode()
            self.countErfitBuilding = None
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

    def enterCountErfitBossBattle(self, requestStatus):
        from toontown.coghq import CountErfitBossBattle
        self.acceptOnce(self.placeDoneEvent, self.handleCountErfitBossBattleDone)
        self.place = CountErfitBossBattle.CountErfitBossBattle(self, self.fsm, self.placeDoneEvent)
        base.cr.playGame.setPlace(self.place)
        self.place.load()
        base.localAvatar.setCameraFov(ToontownGlobals.CogHQCameraFov)
        base.camLens.setNearFar(ToontownGlobals.DefaultCameraNear, ToontownGlobals.DefaultCameraFar)
        base.cr.forbidCheesyEffects(1)
        self.place.enter(requestStatus)

    def exitCountErfitBossBattle(self):
        self.ignore(self.placeDoneEvent)
        if self.place:
            self.place.exit()
            self.place.unload()
            self.place = None
            base.cr.playGame.setPlace(None)
        base.cr.forbidCheesyEffects(0)
        base.localAvatar.setCameraFov(settings['fieldofview'])
        base.camLens.setNearFar(ToontownGlobals.DefaultCameraNear, ToontownGlobals.DefaultCameraFar)

    def handleCountErfitBossBattleDone(self):
        status = self.place.doneStatus
        if (status.get('loader') == CountErfitInstanceGlobals.INSTANCE_LOADER and
                ZoneUtil.getBranchZone(status['zoneId']) == self.branchZone and
                status.get('shardId') is None):
            self.fsm.request('quietZone', [status])
        else:
            self.doneStatus = status
            messenger.send(self.doneEvent)

