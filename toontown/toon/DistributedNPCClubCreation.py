from toontown.toon.ClubVinciNPCBase import ClubVinciNPCBase
from toontown.nametag.NametagGlobals import CFSpeech, CFTimeout


class DistributedNPCClubCreation(ClubVinciNPCBase):
    customHeadPrefix = '/models/char/toons/head/doevinci-heads-'
    exactPosition = (-0.0291, -3.376, 1.0)
    exactHeading = 180.0
    shirtTexture = 'cosmetics/clothing/maps/cc_t_clth_shirt_npc_doe.png'
    sleeveTexture = 'cosmetics/clothing/maps/cc_t_clth_shirt_npc_doe_sleeve.png'
    bottomTexture = 'cosmetics/clothing/maps/cc_t_clth_skirt_npc_doe.png'
    accessoryDefinitions = (
        ('cosmetics/hat/models/cc_m_acc_hat_beanie_doe.bam',
         'cosmetics/hat/maps/cc_t_acc_hat_beanie_doe_yellow.png',
         'head', (0.0, -0.119, 0.37), (0.0, 10.0, 0.0), (1.0, 1.0, 1.0)),
        ('cosmetics/neck/models/cc_m_acc_nec_bandana_doe.bam',
         'cosmetics/neck/maps/cc_t_acc_nec_bandana_doe_1.png', 'body', (0.39, -0.713, 0.595),
         (337.368, 5.39, -0.418), (1.22, 1.189, 1.183)),
    )

    def handleCollisionSphereEnter(self, collEntry):
        manager = getattr(base.cr, 'clubMgr', None)
        if not manager:
            self.setChatAbsolute('The Club-O-Matic is currently unavailable.', CFSpeech | CFTimeout)
            return
        if manager.isInClub():
            self.setChatAbsolute('You are already a member of a Club!', CFSpeech | CFTimeout)
            manager.openClubPanel()
            return
        self._prepareInteraction()
        self.acceptOnce('club-creation-gui-done', self._restoreInteraction)
        self.clubGui = manager.openCreationGui(self)
