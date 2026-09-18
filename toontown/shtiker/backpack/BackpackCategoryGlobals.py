from enum import Enum, auto

from toontown.inventory.enums.ItemEnums import ItemType
from toontown.inventory.enums.ItemEnums import MaterialItemType
from toontown.inventory.base.InventoryItem import InventoryItem


class BackpackCategory(Enum):
    # Standard categories
    All = auto()
    Social = auto()
    Profile = auto()
    Battle = auto()
    Estates = auto()
    Activities = auto()
    Misc = auto()

    # Wardrobe-specific categories
    W_All = auto()
    W_Shirts = auto()
    W_Shorts = auto()
    W_Skirts = auto()
    W_Hats = auto()
    W_Glasses = auto()
    W_Neck = auto()
    W_Backpack = auto()
    W_Shoes = auto()


# Defines backpack category -> what item types show up in the book
CategoryToItemTypes: dict[BackpackCategory, list[ItemType]] = {
    # region Standard categories
    BackpackCategory.Social: [
        ItemType.Social_ChatStickers,
        ItemType.Social_CustomSpeedchat,
        ItemType.Social_NametagFont,
        ItemType.Social_CheesyEffect,
        ItemType.Social_Emote,
    ],
    BackpackCategory.Profile: [
        ItemType.Profile_Background,
        ItemType.Profile_Nameplate,
        ItemType.Profile_Pose,
    ],
    BackpackCategory.Battle: [
        # This category also includes counterfeits, sues, and fires,
        # but these are manually included in the getter function
        ItemType.Unite,
        ItemType.IOU,
    ],
    BackpackCategory.Estates: [
        ItemType.Estate_Furniture,
        ItemType.Estate_Style,
        ItemType.Estate_Ticket,
    ],
    BackpackCategory.Activities: [
        # Poor lonely fishing rod :(
        ItemType.Fishing_Rod
    ],
    BackpackCategory.Misc: [
        # Manually excludes counterfeits, sues, and fires
        # in the getter function
        ItemType.Material
    ],
    # endregion

    # region Wardrobe-specific categories
    BackpackCategory.W_Shirts: [
        ItemType.Cosmetic_Clothing_Top,
    ],
    BackpackCategory.W_Shorts: [
        ItemType.Cosmetic_Clothing_Bottom,
    ],
    BackpackCategory.W_Skirts: [
        # Shorts and skirts use the same item type, but the getter func will filter them
        ItemType.Cosmetic_Clothing_Bottom,
    ],
    BackpackCategory.W_Hats: [
        ItemType.Cosmetic_Hat,
    ],
    BackpackCategory.W_Glasses: [
        ItemType.Cosmetic_Glasses,
    ],
    BackpackCategory.W_Neck: [
        ItemType.Cosmetic_Neck,
    ],
    BackpackCategory.W_Backpack: [
        ItemType.Cosmetic_Backpack,
    ],
    BackpackCategory.W_Shoes: [
        ItemType.Cosmetic_Shoes,
    ],
}

AllWardrobeTypes = [
    ItemType.Cosmetic_Clothing_Top,
    ItemType.Cosmetic_Clothing_Bottom,
    ItemType.Cosmetic_Hat,
    ItemType.Cosmetic_Glasses,
    ItemType.Cosmetic_Neck,
    ItemType.Cosmetic_Backpack,
    ItemType.Cosmetic_Shoes,
]


# Battle relevant materials that should be included on the battle tab and excluded from the misc tab
BattleMaterials = [
    MaterialItemType.Counterfeits,
    MaterialItemType.CeaseAndDesists,
    MaterialItemType.PinkSlips,
]


def isItemValidForCategory(item: InventoryItem, category: BackpackCategory) -> bool:
    itemType = item.getItemType()
    itemSubtype = item.getItemSubtype()
    itemDefinition = item.getItemDefinition()

    # All (non-wardrobe) items should show up under the "all" category
    if category == BackpackCategory.All:
        return itemType not in AllWardrobeTypes
    # All (wardrobe) items should show up under the "W_all" category
    elif category == BackpackCategory.W_All:
        return itemType in AllWardrobeTypes

    if itemType == ItemType.Material and itemSubtype in BattleMaterials:
        # Battle materials (counterfeits/ceases/fires) should only show up under the battle category
        return category == BackpackCategory.Battle

    if category == BackpackCategory.W_Shorts and itemType == ItemType.Cosmetic_Clothing_Bottom and itemDefinition.isSkirt():
        # In the shorts category, do not show skirts
        return False
    elif category == BackpackCategory.W_Skirts and itemType == ItemType.Cosmetic_Clothing_Bottom and itemDefinition.isShorts():
        # In the Skirts category, do not show shorts
        return False

    # All other things can just check for the relevant category they're listed under
    return itemType in CategoryToItemTypes[category]


CategoryToString = {
    # region Standard categories
    BackpackCategory.All: 'All',
    BackpackCategory.Social: 'Social',
    BackpackCategory.Profile: 'Profile',
    BackpackCategory.Battle: 'Battle',
    BackpackCategory.Estates: 'Estates',
    BackpackCategory.Activities: 'Activities',
    BackpackCategory.Misc: 'Misc.',
    # endregion

    # region Wardrobe-specific categories
    BackpackCategory.W_All: 'All',
    BackpackCategory.W_Shirts: 'Shirts',
    BackpackCategory.W_Shorts: 'Shorts',
    BackpackCategory.W_Skirts: 'Skirts',
    BackpackCategory.W_Hats: 'Hats',
    BackpackCategory.W_Glasses: 'Glasses',
    BackpackCategory.W_Neck: 'Neck',
    BackpackCategory.W_Backpack: 'Backpack',
    BackpackCategory.W_Shoes: 'Shoes',
    # endregion
}
