from toontown.toonbase.ToontownGlobals import (
    ToontownCentral,
    DonaldsDock,
    YeOlde,
    DaisyGardens,
    MinniesMelodyland,
    TheBrrrgh,
    OutdoorZone,
    DonaldsDreamland,
)

COUNT_UP_RATE = 0.15
COUNT_UP_DURATION = 0.5
DELAY_BEFORE_COUNT_UP = 1.0
DELAY_AFTER_COUNT_UP = 1.0
COUNT_DOWN_RATE = 0.075
COUNT_DOWN_DURATION = 0.5
DELAY_AFTER_COUNT_DOWN = 0.0
DELAY_AFTER_CELEBRATE = 2.6
COUNT_SFX_MIN_DELAY = 0.034
COUNT_SFX_START_T = 0.079
OVERMAX_SFX_MIN_DELAY = 0.067
OVERMAX_SFX_START_T = 0.021
DEFAULT_SIDEWALK_COLOR = [0.9, 0.6, 0.4]
HOOD_TO_BUILDING_MODEL = {
    ToontownCentral: "phase_3.5/models/modules/TT_A1",
    DonaldsDock: "phase_6/models/modules/DD_A1",
    YeOlde: "phase_7/models/modules/D3_Str",
    DaisyGardens: "phase_8/models/modules/DG_A1",
    MinniesMelodyland: "phase_6/models/modules/MM_A1",
    TheBrrrgh: "phase_8/models/modules/BR_A1",
    OutdoorZone: "phase_6/models/modules/OZ_A1",
    DonaldsDreamland: "phase_8/models/modules/DL_A1",
}
HOOD_TO_BUILDING_X_OFFSET = {
    YeOlde: 7,
    DaisyGardens: 2,
    OutdoorZone: 2,
    DonaldsDreamland: -2,
}
HOOD_TO_BUILDING_Y_OFFSET = {YeOlde: 1, DonaldsDreamland: 2}
HOOD_TO_BUILDING_Z_OFFSET = {}
HOOD_TO_DOOR_Y_OFFSET = {YeOlde: 2.4, OutdoorZone: 2.75, DonaldsDreamland: 0.75}
HOOD_TO_SIDEWALK_TEXTURE = {
    ToontownCentral: "phase_3.5/maps/sidewalk_4cont_brown.png",
    DonaldsDock: "phase_3.5/maps/boardwalk_floor_dark.png",
    YeOlde: "phase_7/maps/olde_sidewalk.png",
    DaisyGardens: "phase_3.5/maps/grassDG.png",
    MinniesMelodyland: "phase_3.5/maps/sidewalk_4cont_red.png",
    TheBrrrgh: "phase_3.5/maps/snow.png",
    OutdoorZone: "phase_3.5/maps/grassAA.png",
    DonaldsDreamland: "phase_3.5/maps/sidewalk_4cont_purple.png",
}
HOOD_TO_DOOR_COLOR = {
    DonaldsDock: [0.7, 0.4, 0.15, 1.0],
    YeOlde: [0.7, 0.4, 0.15, 1.0],
    DaisyGardens: [0.8, 1.0, 0.8, 1.0],
    MinniesMelodyland: [1.0, 0.8, 0.8, 1.0],
    TheBrrrgh: [0.6, 1.0, 1.0, 1.0],
    OutdoorZone: [0.7, 0.4, 0.15, 1.0],
    DonaldsDreamland: [0.4, 0.3, 0.4, 1.0],
}