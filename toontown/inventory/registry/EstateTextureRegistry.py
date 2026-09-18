"""
This module contains the item data for estate textures (wallpapers / flooring).
"""
from __future__ import annotations
from panda3d.core import NodePath

from toontown.building.interior.props.LavaLamp import LavaLamp
from toontown.estate.EstateGlobals import EstateItemType, EstateItemPlacementFlags
from toontown.estate.zones.EstateDoorGlobals import EstateDoorType
from toontown.inventory.base.InventoryItem import InventoryItem
from toontown.inventory.base.ItemDefinition import ItemDefinition
from typing import Dict, Optional
from enum import IntEnum

from toontown.inventory.enums.ItemEnums import FurnitureItemType, EstateTextureItemType
from toontown.utils import ColorHelper


class EstateTextureDefinition(ItemDefinition):
    """
    The definition structure for estate textures.
    """

    def __init__(self,
                 texturePath,
                 **kwargs):
        super().__init__(**kwargs)
        self.texturePath = texturePath

    def getTexturePath(self):
        return self.texturePath

    def getItemTypeName(self):
        return 'Texture'


# The registry dictionary for textures.
EstateTextureRegistry: Dict[EstateTextureItemType, EstateTextureDefinition] = {

}
