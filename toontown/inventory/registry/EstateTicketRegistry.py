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

from toontown.inventory.enums.ItemEnums import FurnitureItemType, EstateTextureItemType, EstateTicketItemType
from toontown.utils import ColorHelper


class EstateTicketDefinition(ItemDefinition):
    """
    The definition structure for estate textures.
    """

    def __init__(self,
                 **kwargs):
        super().__init__(**kwargs)

    def getItemTypeName(self):
        return 'Ticket'


# The registry dictionary for textures.
EstateTicketRegistry: Dict[EstateTicketItemType, EstateTicketDefinition] = {
    ### Debug Ticket ###
    EstateTicketItemType.Generic_Ticket: EstateTicketDefinition(
        name='Generic Ticket',
        description='hi :)'
    )
}
