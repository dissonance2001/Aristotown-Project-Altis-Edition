"""
A module to store balance data for estate items.
"""

from toontown.estate.EstateGlobals import EstateItemType


ESTATE_ITEM_SCALE_RANGE = (0.50, 1.50)

ESTATE_LAVA_LAMP_SPEED_RANGE = (0.50, 2.00)

ESTATE_TRAMPOLINE_JUMP_FORCE_RANGE = (20, 100)

ESTATE_DEBUG_PAIN_RANGE = (1, 150)

ESTATE_THROWABLE_AMOUNT = 10

# Non-defaults. If not listed, it will default to ESTATE_ITEM_SCALE_RANGE.
EstateItemTypeToScaleRange = {
    EstateItemType.DEBUG_PRIMITIVE: (0.1, 100.0)
}

# A list of estate item types that want precise (3-dimensional) scaling.
EstateItemTypesWantPreciseScale = [
    EstateItemType.DEBUG_PRIMITIVE,
    EstateItemType.DEBUG_OUCH,
]
