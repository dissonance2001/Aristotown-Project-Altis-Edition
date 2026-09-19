"""
Item definitions for Altis's original (pre-hammerspace) hat, glasses, and backpack
catalog, auto-ported from ToonDNA.HatStyles / GlassesStyles / BackpackStyles so the
old catalog/closet/trunk content keeps working as hammerspace items.

Unlike Clash's HatItemDefinition/GlassesItemDefinition/BackpackItemDefinition, these
store the exact Altis model/texture path directly rather than building a path from a
naming convention (Altis's asset names don't follow Clash's cosmetics/ convention).
"""
from __future__ import annotations
from typing import Optional

from toontown.inventory.definitions.AccessoryDefinition import AccessoryDefinition
from toontown.inventory.enums.ItemTags import ItemTag
from toontown.inventory.base.InventoryItem import InventoryItem
from toontown.toon import ToonDNA, AccessoryGlobals


def _getLegacyAccessoryPlacement(definition, stylePrefix, styles, models, placementTable):
    name = definition.getName()
    if name.startswith(stylePrefix):
        styleName = name[len(stylePrefix):]
        styleData = styles.get(styleName)
        if styleData:
            return placementTable.get(styleData[0], {})

    modelPath = definition.getModelPath()
    if modelPath:
        try:
            modelIndex = models.index(modelPath)
        except ValueError:
            return {}
        return placementTable.get(modelIndex, {})

    return {}


class AltisLegacyHatItemDefinition(AccessoryDefinition):
    """An Altis-original hat, ported as a hammerspace item."""

    def __init__(self, modelPath: str, texturePath: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self._modelPath = modelPath
        self._texturePath = texturePath

    def getItemTypeName(self):
        return 'Head'

    def getModelPath(self):
        return self._modelPath

    def getTexturePath(self):
        return self._texturePath

    def getAccessoryPlacement(self, item: Optional[InventoryItem] = None):
        return _getLegacyAccessoryPlacement(
            self, 'Hat Style ', ToonDNA.HatStyles, ToonDNA.HatModels,
            AccessoryGlobals.ExtendedHatTransTable)

    def getTags(self, item: 'InventoryItem') -> set:
        tags = super().getTags(item)
        tags.add(ItemTag.Hat)
        return tags


class AltisLegacyGlassesItemDefinition(AccessoryDefinition):
    """An Altis-original pair of glasses, ported as a hammerspace item."""

    def __init__(self, modelPath: str, texturePath: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self._modelPath = modelPath
        self._texturePath = texturePath

    def getItemTypeName(self):
        return 'Glasses'

    def getRewardName(self, item: Optional[InventoryItem] = None):
        return f'{self.getName()} Glasses'

    def getModelPath(self):
        return self._modelPath

    def getTexturePath(self):
        return self._texturePath

    def getAccessoryPlacement(self, item: Optional[InventoryItem] = None):
        return _getLegacyAccessoryPlacement(
            self, 'Glasses Style ', ToonDNA.GlassesStyles, ToonDNA.GlassesModels,
            AccessoryGlobals.ExtendedGlassesTransTable)


class AltisLegacyBackpackItemDefinition(AccessoryDefinition):
    """An Altis-original backpack, ported as a hammerspace item."""

    def __init__(self, modelPath: str, texturePath: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self._modelPath = modelPath
        self._texturePath = texturePath

    def getItemTypeName(self):
        return 'Backpack'

    def getRewardName(self, item: Optional[InventoryItem] = None):
        return f'{self.getName()} Backpack'

    def getModelPath(self):
        return self._modelPath

    def getTexturePath(self):
        return self._texturePath

    def getAccessoryPlacement(self, item: Optional[InventoryItem] = None):
        return _getLegacyAccessoryPlacement(
            self, 'Backpack Style ', ToonDNA.BackpackStyles, ToonDNA.BackpackModels,
            AccessoryGlobals.ExtendedBackpackTransTable)


class AltisLegacyShoeItemDefinition(AccessoryDefinition):
    """
    An Altis-original pair of shoes, ported as a hammerspace item.

    Unlike hats/glasses/backpacks, Altis shoes are NOT a separate loadable model --
    they're geometry baked into the toon's own leg model, hidden by default and
    revealed by unstashing a node whose name matches `nodeName` (Altis's old
    ToonDNA.ShoesModels[idx] value), then textured. See AltisLegacyShoeAccessory
    for the matching client-side rendering logic.
    """

    def __init__(self, nodeName: str, texturePath: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.nodeName = nodeName
        self._texturePath = texturePath

    def getItemTypeName(self):
        return 'Shoes'

    def getModelPath(self):
        # No separate model to load -- the geometry already exists on the toon.
        return None

    def getTexturePath(self):
        return self._texturePath

    def getAccessoryClass(self):
        from toontown.toon.accessories.AltisLegacyShoeAccessory import AltisLegacyShoeAccessory
        return AltisLegacyShoeAccessory

    def getTags(self, item: 'InventoryItem') -> set:
        tags = super().getTags(item)
        tags.add(ItemTag.Shoes)
        return tags
