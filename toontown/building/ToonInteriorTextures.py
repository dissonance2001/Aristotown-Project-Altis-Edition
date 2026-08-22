"""
Formerly, interior textures for wallpaper, wallpaper borders, wainscotting, etc. were stored and picked from random
in storage_interior. This module allows for more fluid customization of interior textures depending on the zone.
For special shops that prefer to use a specific interior model/texture set, see DistributedToonInterior.py
In theory, this can be converted to an external JSON for allowing more customization by content pack users.
"""

from toontown.toonbase.ToontownGlobals import *

# Molding currently does not support custom colors, don't use any desat textures here
moldingBase = [
    "phase_3.5/maps/molding_wood1.png",
    "phase_3.5/maps/molding_wood2.png",
]

wallpaperBase = [
    "phase_3.5/maps/stripeB5.png",  # Original
    # "phase_3.5/maps/wall_paper_a1.png", # this is nice but not should be in base
    # "phase_3.5/maps/wall_paper_a2.png",
    # "phase_3.5/maps/wall_paper_a3.png",
    # "phase_3.5/maps/wall_paper_a4.png",
    # "phase_5.5/maps/flat_wallpaper1.png",
    # "phase_4/maps/a_purple.png"
    "phase_5.5/maps/big_stripes3.png",
    "phase_5.5/maps/two_stripes3.png",
    "phase_5.5/maps/stripeB1.png",
    "phase_5.5/maps/stripeB7.png",
    # "phase_5.5/maps/squiggle5.png",
]

wallpaperBorderBase = [
    "phase_3.5/maps/wall_paper_b3.png",
    "phase_3.5/maps/molding_wood1.png",
    "phase_5.5/maps/dental_Border_wood_neutral.png",
]

wainscottingBase = [
    "phase_3.5/maps/wall_paper_b3.png",
    # "phase_3.5/maps/wall_paper_b4.png",
    "phase_3.5/maps/shot_lamp_base.png",
    "phase_3.5/maps/molding_wood1.png",
    "phase_5.5/maps/wainscotings_neutral.png",
    "phase_5.5/maps/dental_Border_wood_neutral.png",

]

# Doors don't actually have any sort of pattern/randomization, just use the same door graphic[model].
# Here just to prevent a crash
doorBase = [
    "phase_3/maps/invisible.png"
]

floorBase = [
    "phase_3.5/maps/floor_wood.png",
    "phase_3.5/maps/carpet.png",
    "phase_5.5/maps/floor_woodtile_neutral.png",
    "phase_4/maps/flooring_tile_neutral.png",
    "phase_5.5/maps/floor_woodtile.png",
    "phase_5.5/maps/flooring_tileB2.png"
]

baseScheme = {
    "TI_wainscotting": wainscottingBase,
    "TI_wallpaper": wallpaperBase,
    "TI_wallpaper_border": wallpaperBorderBase,
    "TI_door": doorBase,
    "TI_floor": floorBase,
    "TI_molding": moldingBase,
}

textures = {
    DonaldsDock: {
        "TI_wainscotting": wainscottingBase,
        "TI_wallpaper": wallpaperBase + [
            "phase_6/maps/barnacle_boatyard/interiors/ttcc_int_bb_wallpaper_1.png",
            "phase_6/maps/barnacle_boatyard/interiors/ttcc_int_bb_wallpaper_2.png",
        ],
        "TI_wallpaper_border": wallpaperBorderBase,
        "TI_door": doorBase,
        "TI_floor": floorBase + [
            "phase_6/maps/barnacle_boatyard/interiors/ttcc_int_bb_floor_1.png",
            "phase_6/maps/barnacle_boatyard/ttcc_bb_floorBoardwalk.png",
            # "phase_5.5/maps/UWtileFloor1.png",
            # "phase_5.5/maps/UWtileFloor4.png"
        ],
        "TI_molding": moldingBase,
    },
    ToontownCentral: {
        "TI_wainscotting": wainscottingBase,
        "TI_wallpaper": wallpaperBase,
        "TI_wallpaper_border": wallpaperBorderBase,
        "TI_door": doorBase,
        "TI_floor": floorBase,
        "TI_molding": moldingBase,
    },
    TheBrrrgh: {
        "TI_wainscotting": wainscottingBase,
        "TI_wallpaper": wallpaperBase + [
            "phase_4/maps/wrap_snow.png",
            'phase_5.5/maps/wall_paper_snowflakes.png',
            'phase_5.5/maps/wall_paper_snowman.png',
        ],
        "TI_wallpaper_border": wallpaperBorderBase,
        "TI_door": doorBase,
        "TI_floor": floorBase + [
            "phase_5.5/maps/floor_icecube.png",
            "phase_5.5/maps/floor_icecube_neutral.png",
            # "phase_5.5/maps/floor_snow.png",
            # "phase_5.5/maps/floor_snow_neutral.png",
        ],
        "TI_molding": moldingBase,
    },
    MinniesMelodyland: {
        "TI_wainscotting": wainscottingBase + [
            "phase_6/maps/small_wall_brick.png",
        ],
        "TI_wallpaper": wallpaperBase,
        "TI_wallpaper_border": wallpaperBorderBase,
        "TI_door": doorBase,
        "TI_floor": floorBase,
        "TI_molding": moldingBase,
    },
    DaisyGardens: {
        "TI_wainscotting":wainscottingBase,
        "TI_wallpaper":wallpaperBase + [
            "phase_5.5/maps/leaves1.png",
            "phase_5.5/maps/leaves2.png",
            "phase_5.5/maps/leaves3.png",
            "phase_5.5/maps/littleFlowers.png",
            "phase_5.5/maps/littleFlowers_neutral.png",
            #"phase_5.5/maps/wall_paper_flower1.png",
           # "phase_5.5/maps/basket.png"
        ],
        "TI_wallpaper_border": wallpaperBorderBase,
        "TI_door": doorBase,
        "TI_floor": floorBase + [
            "phase_3.5/maps/dustroad.png"
        ],
        "TI_molding": moldingBase,
    },
    OutdoorZone: {
        "TI_wainscotting": wainscottingBase + [
            "phase_6/maps/acorn_acres/interiors/ttcc_int_aa_wainscotting_1.png",
            "phase_6/maps/acorn_acres/interiors/ttcc_int_aa_wainscotting_2.png",
        ],
        "TI_wallpaper": wallpaperBase,
        "TI_wallpaper_border": wallpaperBorderBase,
        "TI_door": doorBase,
        "TI_floor": floorBase + [
            "phase_6/maps/acorn_acres/interiors/ttcc_int_aa_floor_1.png",
        ],
        "TI_molding": moldingBase,
    },
    YeOlde: baseScheme,  # Don't touch me
    GoofySpeedway: baseScheme,
    DonaldsDreamland: {
        "TI_wainscotting": wainscottingBase,
        "TI_wallpaper": wallpaperBase + [
            # "phase_5.5/maps/windowView_Stars2.png",
            "phase_8/maps/drowsy_dreamland/interiors/ttcc_int_ddl_wallpaper_1.png",
            "phase_8/maps/drowsy_dreamland/interiors/ttcc_int_ddl_wallpaper_2.png",
            "phase_8/maps/drowsy_dreamland/interiors/ttcc_int_ddl_wallpaper_3.png",
            "phase_8/maps/drowsy_dreamland/interiors/ttcc_int_ddl_wallpaper_4.png",
            "phase_8/maps/drowsy_dreamland/ttcc_ddl_walls_bricks_1.png"
        ],
        "TI_wallpaper_border": wallpaperBorderBase,
        "TI_door": doorBase,
        "TI_floor": floorBase + [
            "phase_8/maps/drowsy_dreamland/interiors/ttcc_int_ddl_floor_desat_1.png",
        ],
        "TI_molding": moldingBase + [
            "phase_8/maps/drowsy_dreamland/interiors/ttcc_int_ddl_moulding_1.png",
            "phase_8/maps/drowsy_dreamland/interiors/ttcc_int_ddl_moulding_2.png",
            "phase_8/maps/drowsy_dreamland/interiors/ttcc_int_ddl_moulding_3.png",
            "phase_8/maps/drowsy_dreamland/interiors/ttcc_int_ddl_moulding_4.png",
            "phase_8/maps/drowsy_dreamland/interiors/ttcc_int_ddl_moulding_5.png",
        ],
    },
    Tutorial: {
        # The tutorial is a cut and paste of Toontown Central
        "TI_wainscotting": wainscottingBase,
        "TI_wallpaper": wallpaperBase,
        "TI_wallpaper_border": wallpaperBorderBase,
        "TI_door": doorBase,
        "TI_floor": floorBase,
        "TI_molding": moldingBase,
    },
    Toonseltown: {
        "TI_wainscotting": wainscottingBase,
        "TI_wallpaper": [
            'phase_5.5/maps/wall_paper_snowflakes.png',
            'phase_5.5/maps/wall_paper_snowman.png',
            'phase_5.5/maps/wall_paper_hollyleaf.png',
            "phase_13/maps/events/toonseltown/wall-2_tst.png",
            "phase_13/maps/events/toonseltown/wall-tst.png",
        ],
        "TI_wallpaper_border": [
            'phase_5.5/maps/tt_t_ara_int_border_winterLights1.png',
            'phase_5.5/maps/tt_t_ara_int_border_winterLights2.png',
            'phase_5.5/maps/tt_t_ara_int_border_winterLights3.png',
        ],
        "TI_door": doorBase,
        "TI_floor": floorBase + [
            "phase_13/maps/events/toonseltown/floor-tst.png"
        ],
        "TI_molding": moldingBase,
    },
    SkyClan: baseScheme,
}

gagShop = {
    "TI_wallpaper": [
        "phase_3.5/maps/stripeB5.png"
    ],
    "TI_wainscotting": [
        "phase_3.5/maps/wall_paper_b3.png"
    ],
    "TI_floor": [
        "phase_5.5/maps/floor_wood_neutral.png"
    ],
    "TI_wallpaper_border": [
        "phase_3.5/maps/stripeB5.png"
    ]
}
