from toontown.suit import Suit
from toontown.town import DLStreet
from toontown.town import TownLoader


class DLTownLoader(TownLoader.TownLoader):
    def __init__(self, hood, parentFSM, doneEvent):
        TownLoader.TownLoader.__init__(self, hood, parentFSM, doneEvent)
        self.streetClass = DLStreet.DLStreet
        self.townStorageDNAFile = 'phase_8/dna/storage_DL_town.pdna'
        self.playgroundTexPath = 'phase_8/maps/drowsy_dreamland'

    def load(self, zoneId):
        TownLoader.TownLoader.load(self, zoneId)
        dnaFile = 'phase_8/dna/donalds_dreamland_' + str(self.canonicalBranchZone) + '.pdna'
        self.createHood(dnaFile)
        self.setupTunnelTexture()

    def unload(self):
        TownLoader.TownLoader.unload(self)
        del self.playgroundTexPath

    def setupTunnelTexture(self):
        tunnels = self.geom.findAllMatches("**/linktunnel_dl_*")
        if not tunnels:
            return
        tunnelTextureFiles = (
            loader.loadTexture(self.playgroundTexPath + "/cc_t_gen_prp_tunnel_ddl.png"),
            loader.loadTexture(self.playgroundTexPath +"/ttcc_ddl_floor_1.png")
        )
        for tunnel in tunnels:
            tunnel.replaceTexture(tunnel.findTexture("cc_t_gen_prp_tunnel_ttc"), tunnelTextureFiles[0])
            tunnel.replaceTexture(tunnel.findTexture("cc_t_ara_ttc_floor_cobble_1"), tunnelTextureFiles[1])
