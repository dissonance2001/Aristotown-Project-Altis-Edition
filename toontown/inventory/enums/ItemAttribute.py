from strenum import StrEnum


class ItemAttribute(StrEnum):
    """
    A string enum list for item attributes.
    Keep the string values short & unique.
    """
    MODEL_COLORSCALE   = 'cs'
    MODIFIER    = 'm'
    MODIFIER_3D = 'm3'
    MODIFIER_2D = 'm2'

    ESTATE_ENTRANCE = 'e'
    HEX_COLOR_A = 'ha'
    HEX_COLOR_B = 'hb'
    SPEED = 's'

    JUMP_FORCE = 'jf'
    PAIN_AMOUNT = 'pa'

    PROP_COLOR_HEX = 'ci'
    PROP_MODEL_STATE = 'ms'

    # Clothing / Accessories
    CLOTHES_PRIMARY_COL   = 'a'
    CLOTHES_SECONDARY_COL = 'b'

    # Boosters
    MINUTES = 'i'


# A set of attributes to be removed on items that are being added to inventories.
# (DO THIS FOR ALL ESTATE ATTRIBUTES FOR THINGS YOU WANT TO KEEP STACKABLE!!)
InventoryStripAttributes: set[ItemAttribute] = {
    ItemAttribute.ESTATE_ENTRANCE,
    ItemAttribute.HEX_COLOR_A,
    ItemAttribute.HEX_COLOR_B,
    ItemAttribute.SPEED,
    ItemAttribute.JUMP_FORCE,
    ItemAttribute.PAIN_AMOUNT,
}
