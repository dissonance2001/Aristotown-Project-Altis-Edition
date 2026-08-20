from toontown.toon.ClubVinciNPCBase import ClubVinciNPCBase
from toontown.nametag.NametagGlobals import CFSpeech, CFTimeout


class DistributedNPCClubShop(ClubVinciNPCBase):
    customHeadPrefix = '/models/char/toons/head/brovinci-heads-'
    exactPosition = (-0.0707, 3.2519, 1.0)
    exactHeading = -4.9358
    shirtTexture = 'cosmetics/clothing/maps/cc_t_clth_shirt_npc_bro.png'
    sleeveTexture = 'cosmetics/clothing/maps/cc_t_clth_shirt_npc_bro_sleeve.png'
    bottomTexture = 'cosmetics/clothing/maps/cc_t_clth_shorts_npc_bro.png'
    accessoryDefinitions = (
        ('cosmetics/hat/models/cc_m_acc_hat_hair_bro.bam',
         'cosmetics/hat/maps/cc_t_acc_hat_hair_bro_brown.png', 'head',
         (0.0, -0.00119, 0.0285), (0.0, 365.17827, 0.0),
         (1.02956, 1.05154, 0.96088)),
        ('cosmetics/face/models/cc_m_acc_face_gl_bro.bam',
         'cosmetics/face/maps/cc_t_acc_face_gl_bro_black.png', 'head',
         (0.0, 0.10827, 0.00746), (0.0, 3.918, 0.0),
         (0.98433, 0.87821, 0.89471)),
        ('cosmetics/neck/models/cc_m_acc_nec_necklace_brovinci.bam',
         'cosmetics/neck/maps/cc_t_acc_nec_necklace_bro_green.png', 'body',
         (0.21805, -0.52942, 0.37327),
         (365.82687, 356.50393, 360.10788),
         (1.07851, 1.07625, 1.08305)),
    )

    def handleCollisionSphereEnter(self, collEntry):
        manager = getattr(base.cr, 'clubMgr', None)
        if not manager:
            self.setChatAbsolute('My Club shop is currently unavailable.', CFSpeech | CFTimeout)
            return
        if not manager.isInClub():
            self.setChatAbsolute('Come back after you have joined or created a Club!', CFSpeech | CFTimeout)
            return
        self._prepareInteraction()
        self.acceptOnce('club-shop-gui-done', self._restoreInteraction)
        self.clubGui = manager.openShopGui(self)
