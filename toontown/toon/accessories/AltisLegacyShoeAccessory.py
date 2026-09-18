"""
Client-side rendering for Altis's original shoe styles, ported as hammerspace items.

Altis shoes are not separate loadable models -- they're geometry already present on
the toon's own leg model, hidden by default and revealed by unstashing the node whose
name matches the style's ShoesModels entry, then textured. This mirrors
Toon.generateShoes() in toontown/toon/Toon.py exactly, rather than going through
ToonAccessory's normal "load an external model and attach it" pipeline, which doesn't
apply here.
"""
from panda3d.core import Texture

from toontown.toon.accessories.ToonAccessory import ToonAccessory


class AltisLegacyShoeAccessory(ToonAccessory):
    def __init__(self, toon, item):
        super().__init__(toon, item)
        self.shoeGeoms = []

    def load(self):
        # No external model to load -- go straight to applying the shoe geometry.
        self._applyShoes()
        self.async_loadDone()

    def _applyShoes(self):
        itemDef = self.item.getItemDefinition()
        nodeName = itemDef.nodeName

        # Hide any other shoe geometry first, matching Toon.generateShoes().
        self.toon.findAllMatches('**/feet;+s').stash()
        self.toon.findAllMatches('**/boots_short;+s').stash()
        self.toon.findAllMatches('**/boots_long;+s').stash()
        self.toon.findAllMatches('**/shoes;+s').stash()

        geoms = self.toon.findAllMatches('**/%s;+s' % nodeName)
        for geom in geoms:
            geom.unstash()
        self.shoeGeoms = list(geoms)

        texturePath = itemDef.getTexturePath()
        if texturePath:
            texture = loader.loadTexture(texturePath, okMissing=True)
            if texture:
                texture.setMinfilter(Texture.FTLinearMipmapLinear)
                texture.setMagfilter(Texture.FTLinear)
                for geom in self.shoeGeoms:
                    geom.setTexture(texture, 1)

    def unload(self):
        for geom in self.shoeGeoms:
            geom.stash()
        self.shoeGeoms = []
        super().unload()
