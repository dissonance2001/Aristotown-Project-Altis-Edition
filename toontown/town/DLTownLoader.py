from direct.fsm import State
from toontown.town import DLStreet
from toontown.town import TownLoader


class DLTownLoader(TownLoader.TownLoader):
    def __init__(self, hood, parentFSM, doneEvent):
        TownLoader.TownLoader.__init__(self, hood, parentFSM, doneEvent)
        self.streetClass = DLStreet.DLStreet
        self.musicFile = 'phase_8/audio/bgm/DL_SZ.ogg'
        self.activityMusicFile = 'phase_8/audio/bgm/DL_SZ_activity.ogg'
        self.townStorageDNAFile = 'phase_8/dna/storage_DL_town.dna'
        self.playgroundTexPath = 'phase_8/maps/drowsy_dreamland'

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
        dnaFile = 'phase_8/dna/donalds_dreamland_' + str(self.canonicalBranchZone) + '.pdna'
        self.createHood(dnaFile)
        self.setupTunnelTexture()

    def unload(self):
        TownLoader.TownLoader.unload(self)
        del self.playgroundTexPath

    def _safeReplaceTexture(self, node, oldTexName, newTex):
        if newTex is None:
            print("Warning: new texture is None, skipping replace for '%s'" % oldTexName)
            return
        oldTex = node.findTexture(oldTexName)
        if oldTex is None:
            print("Warning: could not find texture '%s' on %s" % (oldTexName, node.getName()))
            return
        node.replaceTexture(oldTex, newTex)

    def setupTunnelTexture(self):
        if not hasattr(self, 'geom') or not self.geom:
            return
        tunnels = self.geom.findAllMatches("**/linktunnel_dl_*")
        if not tunnels:
            return
        tex1 = loader.loadTexture(self.playgroundTexPath + "/cc_t_gen_prp_tunnel_ddl.png")
        tex2 = loader.loadTexture(self.playgroundTexPath + "/ttcc_ddl_floor_1.png")
        for tunnel in tunnels:
            self._safeReplaceTexture(tunnel, "cc_t_gen_prp_tunnel_ttc", tex1)
            self._safeReplaceTexture(tunnel, "cc_t_ara_ttc_floor_cobble_1", tex2)