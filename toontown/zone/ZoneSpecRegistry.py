from typing import Dict, Any
from toontown.toonbase import ToontownGlobals


# Zone pointing to resources .lvl filepath that contains the level data
ZoneSpecRegistry: Dict[int, str] = {}


# Use this to define new level data entries
def newEntry(zoneId, filePath):
    if zoneId in ZoneSpecRegistry:
        raise KeyError(f"ZoneId {zoneId} already in zone spec map.")

    ZoneSpecRegistry[zoneId] = filePath


# region Level definitions

newEntry(ToontownGlobals.YOTTTestStreet, 'phase_7/data/levels/cc_l_ara_ot_test.lvl')
newEntry(ToontownGlobals.DDLTestStreet, 'phase_8/data/levels/cc_l_ara_dl_test.lvl')

# endregion
