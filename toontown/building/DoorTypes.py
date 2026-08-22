"""
This module provides the types of door models that a DistributedDoor can be.

EXT indicate doors that are on the exterior part of a door, such as landmark building exteriors.
- These doors will have their bldg models grabbed from the loaded hood, having "landmark" or "DNARoot" in their name.
    - COGHQ Doors are an exception to this.

INT indicate doors that are on the interior part of the door, such as building interiors.
- These doors assume that the parent of a door node is the building node.
- Standard & Standard 3D require both leftDoor and rightDoor nodes.
- HQ and Multi Door require a door_0 node.
"""

"""
Standard Door Types

- Assumed to have a flat door.
"""
# This is most of the types of doors on landmark building exteriors.
EXT_STANDARD = 1
# This is most of the doors on building interiors.
INT_STANDARD = 2

"""
Toon HQ Door Types

- Essentially supports for two sets of doors.
- Assumed to have a flat door.
"""
# These doors have models built into the building, and there is possibly more than one of them on each building.
EXT_HQ = 3
# These are like interior standard doors, but there can be more than one of them leading out of the building.
INT_HQ = 4

"""
House Door Types

- Currently unused.
"""
# The exterior/interior doors of an estate building must be handled differently since the houses on an estate
# could possibly change
EXT_HOUSE = 5
INT_HOUSE = 6

"""
CogHQ Door Types
"""
# CogHQ main building -> lobby doors
EXT_COGHQ = 7
INT_COGHQ = 8

"""
Kart Shop Door Type

- The interior (building) node must be named KartShop_Interior*.
"""
# KartShop exterior -> interior doors
EXT_KS = 9
INT_KS = 10

"""
Animated Landmark Building

- Only supports exterior variants, also unused.
"""
EXT_ANIM_STANDARD = 11

"""
Multi-door / EO Types
Special versions of the HQ door types.
"""
EXT_MULTI_DOOR = 12
INT_MULTI_DOOR = 13
EXT_EO = 12
INT_EO = 13

"""
Standard 3D / Uncapturable Door types
Special versions of the standard door types.
This does not hide the left/right door geom and doesn't care for a 2D flat texture.
Requires 2D left/right frame holes.
"""

EXT_STANDARD_3D = 14
INT_STANDARD_3D = 15

EXT_UNCAP = 14
INT_UNCAP = 15
DAISYGARDENSCLASH = 16


class SpecialSoundTypes:
    Standard = 0
    Metal = 1