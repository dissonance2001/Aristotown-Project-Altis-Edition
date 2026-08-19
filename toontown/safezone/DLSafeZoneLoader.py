from toontown.safezone import DLPlayground
from toontown.safezone import SafeZoneLoader
from toontown.toonbase import ToontownGlobals


class DLSafeZoneLoader(SafeZoneLoader.SafeZoneLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        SafeZoneLoader.SafeZoneLoader.__init__(self, hood, parentFSM, doneEvent)
        self.playgroundClass = DLPlayground.DLPlayground
        self.musicFile = 'phase_8/audio/bgm/DL_nbrhood.ogg'
        self.activityMusicFile = 'phase_8/audio/bgm/DL_SZ_activity.ogg'
        self.dnaFile = 'phase_8/dna/donalds_dreamland_sz.dna'
        self.safeZoneStorageDNAFile = 'phase_8/dna/storage_DL_sz.dna'
        self.snowPile = None
        self.playgroundTexPath = "phase_8/maps/drowsy_dreamland"

    def load(self):
        SafeZoneLoader.SafeZoneLoader.load(self)
        if base.cr.newsManager and base.cr.newsManager.isHolidayRunning(ToontownGlobals.CHRISTMAS):
            self.setupSnowPile()
        self.setupTrolleyTexture()
        self.setupTunnelTexture()
        self.setupPetshopTexture()

    def unload(self):
        SafeZoneLoader.SafeZoneLoader.unload(self)
        if base.cr.newsManager and base.cr.newsManager.isHolidayRunning(ToontownGlobals.CHRISTMAS):
            self.cleanupSnowPile()
        del self.playgroundTexPath

    def enter(self, requestStatus):
        SafeZoneLoader.SafeZoneLoader.enter(self, requestStatus)

    def exit(self):
        SafeZoneLoader.SafeZoneLoader.exit(self)

    def setupSnowPile(self):
        snowPileModel = loader.loadModel('phase_8/models/props/snow_pile_full')
        self.snowPile = snowPileModel.find('**/prop_snow_pile_full')
        self.snowPile.reparentTo(self.geom)
        self.snowPile.setPos(26.513, 45.125, -16.250)
        self.snowPile.setH(20)
        self.snowPile.setScale(4)

    def cleanupSnowPile(self):
        if self.snowPile:
            self.snowPile.removeNode()
            self.snowPile = None

    def _safeReplaceTexture(self, node, oldTexName, newTex):
        """Replace a texture by name, logging a warning if not found."""
        oldTex = node.findTexture(oldTexName)
        if oldTex is None:
            print("Warning: could not find texture '%s' on %s" % (oldTexName, node.getName()))
            return
        node.replaceTexture(oldTex, newTex)

    def setupTrolleyTexture(self):
        trolleyStation = self.geom.find("**/prop_trolley_station*")
        if not trolleyStation:
            return
        trolleyStationTextureFiles = (
            loader.loadTexture(self.playgroundTexPath + "/ttcc_ext_ts_ddl_palette_1.png"),
            loader.loadTexture(self.playgroundTexPath + "/ttcc_ext_ts_ddl_palette_2.png")
        )
        self._safeReplaceTexture(trolleyStation, "ttcc_mg_trolleyStation_palette_1", trolleyStationTextureFiles[0])
        self._safeReplaceTexture(trolleyStation, "ttcc_mg_trolleyStation_palette_2", trolleyStationTextureFiles[1])

    def setupPetshopTexture(self):
        petshop = self.geom.find("**/*_pet_shop_*")
        if not petshop:
            return
        petshopTextureFiles = (
            loader.loadTexture(self.playgroundTexPath + "/cc_t_ara_petshop_ext_ddl_1.png"),
            loader.loadTexture(self.playgroundTexPath + "/cc_t_ara_petshop_ext_ddl_2.png")
        )
        self._safeReplaceTexture(petshop, "cc_t_ara_petshop_ext_ttc_1", petshopTextureFiles[0])
        self._safeReplaceTexture(petshop, "cc_t_ara_petshop_ext_ttc_2", petshopTextureFiles[1])

    def setupTunnelTexture(self):
        tunnels = self.geom.findAllMatches("**/linktunnel_dl_*")
        if not tunnels:
            return
        tunnelTextureFiles = (
            loader.loadTexture(self.playgroundTexPath + "/cc_t_gen_prp_tunnel_ddl.png"),
            loader.loadTexture(self.playgroundTexPath + "/ttcc_ddl_floor_1.png")
        )
        for tunnel in tunnels:
            self._safeReplaceTexture(tunnel, "cc_t_gen_prp_tunnel_ttc", tunnelTextureFiles[0])
            self._safeReplaceTexture(tunnel, "cc_t_ara_ttc_floor_cobble_1", tunnelTextureFiles[1])