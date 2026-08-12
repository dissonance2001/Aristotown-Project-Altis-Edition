# -*- coding: utf-8 -*-
"""Python 2-safe Toon Profile data and pose helpers for Project Altis."""

from collections import OrderedDict

DEFAULT_POSE = 0
DEFAULT_NAMEPLATE = 101
DEFAULT_BACKGROUND = 0


# These poses use Clash's posed-composition fitting because their animation,
# rotation, root motion, or attached prop makes Neutral-body fitting look
# off-centre.  Other poses retain the Neutral-reference path, including
# Fire Hands, which is already correctly centred.
POSED_PANEL_FIT_IDS = frozenset((
    8,   # Casting
    9,   # Yippie!
    11,  # Resistance Salute
    12,  # Throw
    14,  # Running
    15,  # Diving
    19,  # Presenting...
    22,  # Upset
    27,  # Sinking
    28,  # Megaphone
    33,  # Banana
    34,  # Seltzer Bottle
    35,  # Gag Button
    36,  # Pie Toss
    38,  # Treasure
    39,  # At The Gate
    44,  # Naptime
    45,
))


def usesPosedPanelFit(value):
    return normalisePoseId(value) in POSED_PANEL_FIT_IDS

POSES = [OrderedDict({'id': 0, 'enum': 'Neutral', 'name': 'Neutral', 'data': OrderedDict({'Animation': ('neutral', 0)})}), OrderedDict({'id': 1, 'enum': 'Wave', 'name': 'Wave', 'data': OrderedDict({'Animation': ('wave', 50)})}), OrderedDict({'id': 2, 'enum': 'Sit', 'name': 'Sit', 'data': OrderedDict({'Animation': ('sit', 0)})}), OrderedDict({'id': 3, 'enum': 'Applause', 'name': 'Applause', 'data': OrderedDict({'Animation': ('applause', 14)})}), OrderedDict({'id': 4, 'enum': 'Thinking', 'name': 'Thinking', 'data': OrderedDict({'Animation': ('think', 40)})}), OrderedDict({'id': 5, 'enum': 'Greened', 'name': 'Greened', 'data': OrderedDict({'Animation': ('sad-neutral', 0)})}), OrderedDict({'id': 6, 'enum': 'Taunt', 'name': 'Taunt', 'data': OrderedDict({'Animation': ('taunt', 27)})}), OrderedDict({'id': 7, 'enum': 'ImOuttaHere', 'name': "I'm Outta Here!", 'data': OrderedDict({'Animation': ('sidestep-left', 11), 'Eyes': 'surprise'})}), OrderedDict({'id': 8, 'enum': 'Casting', 'name': 'Casting', 'data': OrderedDict({'Animation': ('cast', 28), 'AvatarPanelPos': (-0.68, 0, 0), 'Hpr': (-20, 0, 0)})}), OrderedDict({'id': 9, 'enum': 'Yippie', 'name': 'Yippie!', 'data': OrderedDict({'Animation': ('good-putt', 12)})}), OrderedDict({'id': 10, 'enum': 'Selfie', 'name': 'Selfie', 'data': OrderedDict({'Animation': ('battlecast', 20), 'Muzzle': 'smile'})}), OrderedDict({'id': 11, 'enum': 'ResistanceSalute', 'name': 'Resistance Salute', 'data': OrderedDict({'Animation': ('victory', 130)})}), OrderedDict({'id': 12, 'enum': 'Throw', 'name': 'Throw', 'data': OrderedDict({'Animation': ('throw', 55), 'Eyes': 'angry', 'AvatarPanelPos': (0.8, 0, 0), 'Hpr': (20, 0, 0)})}), OrderedDict({'id': 13, 'enum': 'Hypnotizer', 'name': 'Hypnotizer', 'data': OrderedDict({'Animation': ('hypnotize', 23)})}), OrderedDict({'id': 14, 'enum': 'Running', 'name': 'Running', 'data': OrderedDict({'Animation': ('wheelRun', 30), 'AvatarPanelPos': (2.39, 0, 0), 'Hpr': (50, 0, 0)})}), OrderedDict({'id': 15, 'enum': 'Diving', 'name': 'Diving', 'data': OrderedDict({'Animation': ('climb', 115)})}), OrderedDict({'id': 16, 'enum': 'WhatAreYouDoing', 'name': 'What Are You Doing?!', 'data': OrderedDict({'Animation': ('down', 3), 'Eyes': 'surprise'})}), OrderedDict({'id': 17, 'enum': 'Slapped', 'name': 'Slapped', 'data': OrderedDict({'Animation': ('sound', 4), 'Eyes': 'surprise', 'Muzzle': 'sad'})}), OrderedDict({'id': 18, 'enum': 'Surprised', 'name': 'Surprised', 'data': OrderedDict({'Animation': ('conked', 17), 'Eyes': 'surprise', 'Muzzle': 'surprise'})}), OrderedDict({'id': 19, 'enum': 'Presenting', 'name': 'Presenting...', 'data': OrderedDict({'Animation': ('smooch', 120), 'Muzzle': 'smile', 'AvatarPanelPos': (0.35, 0, 0), 'Hpr': (10, 0, 0)})}), OrderedDict({'id': 20, 'enum': 'Victory', 'name': 'Victory', 'data': OrderedDict({'Animation': ('victory', 230)})}), OrderedDict({'id': 21, 'enum': 'Shrug', 'name': 'Shrug', 'data': OrderedDict({'Animation': ('shrug', 132)})}), OrderedDict({'id': 22, 'enum': 'Upset', 'name': 'Upset', 'data': OrderedDict({'Animation': ('confused', 72), 'Eyes': 'angry', 'Muzzle': 'angry', 'AvatarPanelPos': (1.59, 0, 0), 'Hpr': (38, 0, 0)})}), OrderedDict({'id': 23, 'enum': 'ToBeOrNotToBe', 'name': 'To Be Or Not To Be?', 'data': OrderedDict({'Animation': ('right', 9), 'Eyes': 'sad', 'Muzzle': 'sad'})}), OrderedDict({'id': 24, 'enum': 'Spooky', 'name': 'Spooky', 'data': OrderedDict({'Animation': ('cringe', 18), 'Muzzle': 'surprise'})}), OrderedDict({'id': 25, 'enum': 'Zombie', 'name': 'Zombie', 'data': OrderedDict({'Animation': ('block', 17)})}), OrderedDict({'id': 26, 'enum': 'Yawn', 'name': 'Yawn', 'data': OrderedDict({'Animation': ('victory', 104), 'Eyes': 'close', 'Muzzle': 'surprise'})}), OrderedDict({'id': 27, 'enum': 'Sinking', 'name': 'Sinking', 'data': OrderedDict({'Animation': ('melt', 49), 'Eyes': 'sad', 'Muzzle': 'sad', 'AvatarPanelPos': (0, 0, -0.015), 'ItemsPagePos': (0, 0, 0.228)})}), OrderedDict({'id': 28, 'enum': 'Megaphone', 'name': 'Megaphone', 'data': OrderedDict({'Animation': ('sound', 23), 'AvatarPanelPos': (1.08, 0, 0), 'Hpr': (30, 0, 0), 'Prop': ['blue-megaphone'], 'PropParent': ['rightHand']})}), OrderedDict({'id': 29, 'enum': 'UpsideDown', 'name': 'Upside Down', 'data': OrderedDict({'Animation': ('neutral', 0), 'AvatarPanelPos': (0, 0, -0.5), 'ItemsPagePos': (0, 0, 0.4), 'Hpr': (0, 0, 180)})}), OrderedDict({'id': 30, 'enum': 'Sideways', 'name': 'Sideways', 'data': OrderedDict({'Animation': ('neutral', 0), 'AvatarPanelPos': (-0.25, 0, -0.3), 'ItemsPagePos': (0.2, 0, 0.2), 'Hpr': (0, 0, 90)})}), OrderedDict({'id': 31, 'enum': 'Small', 'name': 'Small', 'data': OrderedDict({'Animation': ('neutral', 0), 'Scale': 0.4})}), OrderedDict({'id': 32, 'enum': 'SilentTreatment', 'name': 'Silent Treatment', 'data': OrderedDict({'Animation': ('neutral', 0), 'Hpr': (180, 0, 0)})}), OrderedDict({'id': 33, 'enum': 'Banana', 'name': 'Banana', 'data': OrderedDict({'Animation': ('toss', 32), 'AvatarPanelPos': (1.09, 0, 0), 'Hpr': (30, 0, 0), 'Eyes': 'angry', 'Muzzle': 'smile', 'Prop': ['banana'], 'PropScale': [0.75], 'PropParent': ['rightHand']})}), OrderedDict({'id': 34, 'enum': 'SeltzerBottle', 'name': 'Seltzer Bottle', 'data': OrderedDict({'Animation': ('hold-bottle', 24), 'AvatarPanelPos': (1.09, 0, 0), 'Hpr': (30, 0, 0), 'Prop': ['bottle'], 'PropParent': ['rightHand']})}), OrderedDict({'id': 35, 'enum': 'GagButton', 'name': 'Gag Button', 'data': OrderedDict({'Animation': ('pushbutton', 41), 'AvatarPanelPos': (1.09, 0, 0), 'Hpr': (30, 0, 0), 'Prop': ['button-no-actor'], 'PropParent': ['leftHand']})}), OrderedDict({'id': 36, 'enum': 'PieToss', 'name': 'Pie Toss', 'data': OrderedDict({'Animation': ('toss', 43), 'AvatarPanelPos': (1.13, 0, 0), 'Hpr': (30, 0, 0), 'Muzzle': 'laugh', 'Prop': ['fruitpie'], 'PropParent': ['rightHand']})}), OrderedDict({'id': 37, 'enum': 'BecomeDuck', 'name': 'Become Duck', 'data': OrderedDict({'Animation': ('neutral', 0), 'Species': 'f'})}), OrderedDict({'id': 38, 'enum': 'Treasure', 'name': 'Treasure', 'data': OrderedDict({'Animation': ('bank', 50), 'AvatarPanelPos': (2.39, 0, 0), 'Hpr': (50, 0, 0), 'Muzzle': 'smile', 'Prop': ['treasure-chest'], 'PropParent': ['rightHand'], 'PropHpr': [(180, 0, 0)], 'PropScale': [0.8]})}), OrderedDict({'id': 39, 'enum': 'AtTheGate', 'name': 'At The Gate', 'data': OrderedDict({'Animation': ('tickle', 21), 'Eyes': 'angry', 'AvatarPanelPos': (-0.94, 0, 0), 'Hpr': (-25, 0, 0), 'Prop': ['cosmetics/backpack/models/cc_m_acc_bp_sword_classic'], 'PropParent': ['rightHand'], 'PropPos': [(0.3, 1.35, 0.1)], 'PropHpr': [(0, 90, 0)], 'PropScale': [0.4]})}), OrderedDict({'id': 40, 'enum': 'Elegance', 'name': 'Elegance', 'data': OrderedDict({'Animation': ('sprinkle-dust', 36)})}), OrderedDict({'id': 41, 'enum': 'PickUpThePhone', 'name': 'Pick Up The Phone', 'data': OrderedDict({'Animation': ('pushbutton', 57), 'Muzzle': 'surprise', 'Prop': ['receiver', 'phone'], 'PropParent': ['rightHand', 'leftHand'], 'PropPos': [(-0.2, -0.37, 0.8), (0, 0, 0)], 'PropHpr': [(90, 180, 0), (0, 0, 0)], 'PropScale': [1.0, 1.0]})}), OrderedDict({'id': 42, 'enum': 'FireHands', 'name': 'Fire Hands', 'data': OrderedDict({'Animation': ('juggle', 57), 'Eyes': 'surprise', 'Muzzle': 'surprise', 'Prop': [['phase_12/models/char/suits/ttcc_ene_firestarter-zero', '**/fire_seq'], ['phase_12/models/char/suits/ttcc_ene_firestarter-zero', '**/fire_seq']], 'PropParent': ['rightHand', 'leftHand'], 'PropPos': [(-0.5, 0.0, -3.4), (-0.5, 0.0, -3.4)], 'PropHpr': [(90, 0, 0), (90, 0, 0)], 'PropScale': [2.0, 2.0]})}), OrderedDict({'id': 43, 'enum': 'Rolled', 'name': 'Rolled', 'data': OrderedDict({'Animation': ('slip-forward', 75), 'Eyes': 'sad', 'Muzzle': 'sad', 'Prop': ['treekiller_log'], 'PropParent': [None], 'PropPos': [(-0.1, 0.7, 0.8)], 'PropHpr': [(0, 0, 0)], 'PropScale': [1.75]})}), OrderedDict({'id': 44, 'enum': 'Naptime', 'name': 'Naptime', 'data': OrderedDict({'Animation': ('slip-backward', 22), 'Eyes': 'close', 'AvatarPanelPos': (2.34, 0, 0.04), 'Hpr': (50, 0, 0), 'Prop': ['phase_8/models/props/zzz_treasure'], 'PropParent': [None], 'PropPos': [(-1.6, 0.4, 1.5)], 'PropHpr': [(0, 0, -15)], 'PropScale': [0.6]})})]
POSES.append(OrderedDict({'id': 45, 'enum': 'HighRoller', 'name': 'High Roller', 'data': OrderedDict({'HighRollerPose': True, 'Muzzle': 'laugh'})}))
_HIGH_ROLLER_ANIM = 'profile-high-roller'
_HIGH_ROLLER_LEG_ANIMS = {'s': 'phase_3/models/char/tt_a_chr_dgs_shorts_legs_high-roller', 'm': 'phase_3/models/char/tt_a_chr_dgm_shorts_legs_high-roller', 'l': 'phase_3/models/char/tt_a_chr_dgl_shorts_legs_high-roller'}
_HIGH_ROLLER_TORSO_ANIMS = {'ss': 'phase_3/models/char/tt_a_chr_dgs_shorts_torso_high-roller', 'ms': 'phase_3/models/char/tt_a_chr_dgm_shorts_torso_high-roller', 'ls': 'phase_3/models/char/tt_a_chr_dgl_shorts_torso_high-roller', 'sd': 'phase_3/models/char/tt_a_chr_dgs_skirt_torso_high-roller', 'md': 'phase_3/models/char/tt_a_chr_dgm_skirt_torso_high-roller', 'ld': 'phase_3/models/char/tt_a_chr_dgl_skirt_torso_high-roller'}

NAMEPLATES = [OrderedDict({'id': 101, 'enum': 'DefaultBlue', 'name': 'Default Blue', 'node': 'default_med_blue'}), OrderedDict({'id': 102, 'enum': 'DefaultGreen', 'name': 'Default Green', 'node': 'default_green'}), OrderedDict({'id': 103, 'enum': 'DefaultPurple', 'name': 'Default Purple', 'node': 'default_purple'}), OrderedDict({'id': 104, 'enum': 'DefaultRed', 'name': 'Default Red', 'node': 'default_red'}), OrderedDict({'id': 105, 'enum': 'DefaultYellow', 'name': 'Default Yellow', 'node': 'default_yellow'}), OrderedDict({'id': 106, 'enum': 'DefaultOrange', 'name': 'Default Orange', 'node': 'default_orange'}), OrderedDict({'id': 107, 'enum': 'DefaultBlueB', 'name': 'Default Blue', 'node': 'default_blue'}), OrderedDict({'id': 108, 'enum': 'DefaultDarkBlue', 'name': 'Default Dark Blue', 'node': 'default_dark_blue'}), OrderedDict({'id': 109, 'enum': 'DefaultDarkGreen', 'name': 'Default Dark Green', 'node': 'default_dark_green'}), OrderedDict({'id': 200, 'enum': 'PG_TTC', 'name': 'Toontown Central', 'node': 'hidden_pg_ttc'}), OrderedDict({'id': 201, 'enum': 'PG_BB', 'name': 'Barnacle Boatyard', 'node': 'hidden_pg_bb'}), OrderedDict({'id': 202, 'enum': 'PG_YOTT', 'name': 'Ye Olde Toontowne', 'node': 'hidden_pg_yott'}), OrderedDict({'id': 203, 'enum': 'PG_DG', 'name': 'Daffodil Gardens', 'node': 'hidden_pg_dg'}), OrderedDict({'id': 204, 'enum': 'PG_MML', 'name': 'Mezzo Melodyland', 'node': 'hidden_pg_mml'}), OrderedDict({'id': 205, 'enum': 'PG_TB', 'name': 'The Brrrgh', 'node': 'hidden_pg_tb'}), OrderedDict({'id': 206, 'enum': 'PG_AA', 'name': 'Acorn Acres', 'node': 'hidden_pg_aa'}), OrderedDict({'id': 207, 'enum': 'PG_DDL', 'name': 'Drowsy Dreamland', 'node': 'hidden_pg_ddl'}), OrderedDict({'id': 300, 'enum': 'Activity_Golfing', 'name': 'Golfing', 'node': 'hidden_golfing'}), OrderedDict({'id': 301, 'enum': 'Activity_Trolley', 'name': 'The Trolley', 'node': 'hidden_trolley'}), OrderedDict({'id': 302, 'enum': 'Activity_Racing', 'name': 'Racing', 'node': 'hidden_racing'}), OrderedDict({'id': 400, 'enum': 'Tasks_Judy', 'name': 'Crocheting Lessons', 'node': 'sidetask_judy', 'position': (0.008, 0, 0.138)}), OrderedDict({'id': 500, 'enum': 'Special_Stars', 'name': 'Stars', 'node': 'hidden_stars'}), OrderedDict({'id': 501, 'enum': 'Special_UnderTheSea', 'name': 'Under the Sea', 'node': 'hidden_underwater'}), OrderedDict({'id': 502, 'enum': 'Special_Slippin', 'name': 'Slippin', 'node': 'hidden_banana'}), OrderedDict({'id': 503, 'enum': 'Special_UpToEleven', 'name': 'Turning It Up To 11', 'node': 'hidden_maxevidence'}), OrderedDict({'id': 504, 'enum': 'Special_SnowballFight', 'name': 'Snowball Fight', 'node': 'hidden_steve'}), OrderedDict({'id': 505, 'enum': 'Special_SellbotPaint', 'name': 'Sellbot Paint', 'node': 'hidden_ocftf'}), OrderedDict({'id': 600, 'enum': 'Event_Tinsel', 'name': 'Tinsel', 'node': 'event_tinsel'}), OrderedDict({'id': 601, 'enum': 'Event_Candy', 'name': 'Candy', 'node': 'event_candy'}), OrderedDict({'id': 602, 'enum': 'Event_Wrapping', 'name': 'Wrapping', 'node': 'event_wrapping'}), OrderedDict({'id': 603, 'enum': 'Event_NightLights', 'name': 'Night Lights', 'node': 'event_nightlights'}), OrderedDict({'id': 604, 'enum': 'Event_NewYears2019', 'name': 'New Years 2019 Fireworks', 'node': 'event_2019_fireworks'}), OrderedDict({'id': 605, 'enum': 'Event_SkyClan', 'name': 'Dreams Come True', 'node': 'event_skyclan'}), OrderedDict({'id': 606, 'enum': 'Event_Outback', 'name': 'Outback', 'node': 'event_outback'}), OrderedDict({'id': 607, 'enum': 'Event_LazyBones', 'name': 'Lazy Bones', 'node': 'event_lazy'}), OrderedDict({'id': 608, 'enum': 'Event_Thanksgiving2019', 'name': 'Thanksgiving 2019', 'node': 'event_2019_thanksgiving'}), OrderedDict({'id': 609, 'enum': 'Event_NewYears2020', 'name': 'New Years 2020 Fireworks', 'node': 'event_2020_newyears'}), OrderedDict({'id': 610, 'enum': 'Event_PinkSlip', 'name': 'Pink Slip', 'node': 'event_btl'}), OrderedDict({'id': 611, 'enum': 'Event_Easter2020', 'name': 'Easter 2020', 'node': 'event_easter2020'}), OrderedDict({'id': 612, 'enum': 'Event_AtticusDesk', 'name': "Atticus' Desk", 'node': 'event_standin'}), OrderedDict({'id': 613, 'enum': 'Event_FourthJuly2020', 'name': 'Prepare for Launch', 'node': 'firework_nameplate'}), OrderedDict({'id': 614, 'enum': 'Event_Electric', 'name': 'Electric', 'node': 'event_electric', 'scale': (1.08, 1, 1.08)}), OrderedDict({'id': 619, 'enum': 'Event_Witch', 'name': 'Halloween Night', 'node': 'event_halloween_witch'}), OrderedDict({'id': 615, 'enum': 'Event_HighRoller', 'name': 'High Roller', 'node': 'event_highroller'}), OrderedDict({'id': 700, 'enum': 'Halloween_CandyBlue', 'name': 'Blue Halloween Candy', 'node': 'event_halloween_candy_blue', 'scale': (1.125, 1, 0.95)}), OrderedDict({'id': 701, 'enum': 'Halloween_CandyGreen', 'name': 'Green Halloween Candy', 'node': 'event_halloween_candy_green', 'scale': (1.125, 1, 0.95)}), OrderedDict({'id': 702, 'enum': 'Halloween_CandyMagenta', 'name': 'Magenta Halloween Candy', 'node': 'event_halloween_candy_magenta', 'scale': (1.125, 1, 0.95)}), OrderedDict({'id': 703, 'enum': 'Halloween_CandyPurple', 'name': 'Purple Halloween Candy', 'node': 'event_halloween_candy_purple', 'scale': (1.125, 1, 0.95)}), OrderedDict({'id': 704, 'enum': 'Halloween_CandyRed', 'name': 'Red Halloween Candy', 'node': 'event_halloween_candy_red', 'scale': (1.125, 1, 0.95)}), OrderedDict({'id': 705, 'enum': 'Halloween_SpookyBat', 'name': 'Spooky Bat', 'node': 'event_halloween_bat', 'position': (0, 0, 0.1325), 'scale': (1.125, 1, 1)}), OrderedDict({'id': 800, 'enum': 'Kudos_TTC', 'name': 'You Did It', 'node': 'kudos_ttc'}), OrderedDict({'id': 801, 'enum': 'Kudos_BB', 'name': 'Sandcastles', 'node': 'kudos_bb'}), OrderedDict({'id': 802, 'enum': 'Kudos_YOTT', 'name': 'The Doodragon', 'node': 'kudos_yott'}), OrderedDict({'id': 803, 'enum': 'Kudos_DG', 'name': 'Gardening', 'node': 'kudos_dg'}), OrderedDict({'id': 804, 'enum': 'Kudos_MML', 'name': "Fires n' Flames", 'node': 'kudos_mml'}), OrderedDict({'id': 805, 'enum': 'Kudos_TB', 'name': 'Scarf', 'node': 'kudos_tb'}), OrderedDict({'id': 806, 'enum': 'Kudos_AA', 'name': 'Light Show', 'node': 'kudos_aa'}), OrderedDict({'id': 807, 'enum': 'Kudos_DDL', 'name': 'Sweet', 'node': 'kudos_ddl'}), OrderedDict({'id': 616, 'enum': 'Makeship_DuckShufflerGreen', 'name': 'Duck Shuffler Green', 'node': 'makeship_duckshuffler_green'}), OrderedDict({'id': 617, 'enum': 'Makeship_DuckShufflerRed', 'name': 'Duck Shuffler Red', 'node': 'makeship_duckshuffler_red'}), OrderedDict({'id': 618, 'enum': 'Makeship_FirePace', 'name': 'Firestarter & Pacesetter', 'node': 'makeship_firepace'})]

BACKGROUNDS = [OrderedDict({'id': 0, 'enum': 'Default', 'name': 'Default', 'node': 'default'}), OrderedDict({'id': 100, 'enum': 'PG_Sky_TTC', 'name': 'Toontown Central Sky', 'node': 'hidden_sky_ttc'}), OrderedDict({'id': 101, 'enum': 'PG_Sky_BB', 'name': 'Barnacle Boatyard Sky', 'node': 'hidden_sky_bb'}), OrderedDict({'id': 102, 'enum': 'PG_Sky_YOTT', 'name': 'Ye Olde Toontowne Sky', 'node': 'hidden_sky_ttc'}), OrderedDict({'id': 103, 'enum': 'PG_Sky_DG', 'name': 'Daffodil Gardens Sky', 'node': 'hidden_sky_dg'}), OrderedDict({'id': 104, 'enum': 'PG_Sky_MML', 'name': 'Mezzo Melodyland Sky', 'node': 'hidden_sky_mml'}), OrderedDict({'id': 105, 'enum': 'PG_Sky_TB', 'name': 'The Brrrgh Sky', 'node': 'hidden_sky_tb'}), OrderedDict({'id': 106, 'enum': 'PG_Sky_AA', 'name': 'Acorn Acres Sky', 'node': 'hidden_sky_aa'}), OrderedDict({'id': 107, 'enum': 'PG_Sky_DDL', 'name': 'Drowsy Dreamland Sky', 'node': 'hidden_sky_ddl'}), OrderedDict({'id': 200, 'enum': 'PG_TTC', 'name': 'Toontown Central', 'node': 'hidden_pg_ttc'}), OrderedDict({'id': 201, 'enum': 'PG_BB', 'name': 'Barnacle Boatyard', 'node': 'hidden_pg_bb'}), OrderedDict({'id': 202, 'enum': 'PG_YOTT', 'name': 'Ye Olde Toontowne', 'node': 'hidden_pg_ttc'}), OrderedDict({'id': 203, 'enum': 'PG_DG', 'name': 'Daffodil Gardens', 'node': 'hidden_pg_dg'}), OrderedDict({'id': 204, 'enum': 'PG_MML', 'name': 'Mezzo Melodyland', 'node': 'hidden_pg_mml'}), OrderedDict({'id': 205, 'enum': 'PG_TB', 'name': 'The Brrrgh', 'node': 'hidden_pg_tb'}), OrderedDict({'id': 206, 'enum': 'PG_AA', 'name': 'Acorn Acres', 'node': 'hidden_pg_aa'}), OrderedDict({'id': 207, 'enum': 'PG_DDL', 'name': 'Drowsy Dreamland', 'node': 'hidden_pg_ddl'}), OrderedDict({'id': 300, 'enum': 'HQ_Sellbot', 'name': 'Sellbot HQ', 'node': 'hidden_hq_sbhq'}), OrderedDict({'id': 301, 'enum': 'HQ_Cashbot', 'name': 'Cashbot HQ', 'node': 'hidden_hq_cbhq'}), OrderedDict({'id': 302, 'enum': 'HQ_Lawbot', 'name': 'Lawbot HQ', 'node': 'hidden_hq_lbhq'}), OrderedDict({'id': 303, 'enum': 'HQ_Bossbot', 'name': 'Bossbot HQ', 'node': 'hidden_hq_bbhq'}), OrderedDict({'id': 304, 'enum': 'HQ_Boardbot', 'name': 'Boardbot HQ', 'node': 'hidden_hq_bdhq'}), OrderedDict({'id': 400, 'enum': 'Activity_Fishing', 'name': 'Aquarium', 'node': 'hidden_aqua_fish'}), OrderedDict({'id': 401, 'enum': 'Activity_Golfing', 'name': 'Golfing', 'node': 'hidden_golfing'}), OrderedDict({'id': 402, 'enum': 'Activity_Racing', 'name': 'Chequered Flag', 'node': 'hidden_racing'}), OrderedDict({'id': 403, 'enum': 'Activity_Trolley', 'name': 'Jellybeans', 'node': 'hidden_trolley'}), OrderedDict({'id': 500, 'enum': 'Tasks_Judy', 'name': 'R.I.D.D.L.E.', 'node': 'sidetask_judy'}), OrderedDict({'id': 600, 'enum': 'Event_Winter2018_A', 'name': 'Winter Cabin', 'node': 'event_winter_cabin'}), OrderedDict({'id': 601, 'enum': 'Event_Winter2018_B', 'name': 'Fireplace', 'node': 'event_winter_fireplace'}), OrderedDict({'id': 602, 'enum': 'Event_NewYears2019', 'name': 'New Years 2019 Fireworks', 'node': 'event_2019'}), OrderedDict({'id': 603, 'enum': 'Event_SkyClan', 'name': 'Sky Clan', 'node': 'event_skyclan'}), OrderedDict({'id': 604, 'enum': 'Event_Outback', 'name': 'Outback', 'node': 'event_outback'}), OrderedDict({'id': 605, 'enum': 'Event_GoldenCorridor', 'name': 'The Golden Corridor', 'node': 'event_golden_corridor'}), OrderedDict({'id': 606, 'enum': 'Event_NewYears2020', 'name': 'New Years 2020 Fireworks', 'node': 'event_2020'}), OrderedDict({'id': 607, 'enum': 'Event_BTL', 'name': 'Break the Law!', 'node': 'event_btl'}), OrderedDict({'id': 608, 'enum': 'Event_Valentines2020', 'name': "Valentine's 2020", 'node': 'event_valentines'}), OrderedDict({'id': 609, 'enum': 'Event_Easter2020', 'name': 'Easter 2020', 'node': 'event_easter2020'}), OrderedDict({'id': 610, 'enum': 'Event_StandIn', 'name': 'Artificial Progeny', 'node': 'event_standin'}), OrderedDict({'id': 611, 'enum': 'Event_FourthJuly2020', 'name': 'Fireworks Show', 'node': 'firework_background'}), OrderedDict({'id': 612, 'enum': 'Event_Halloween2020', 'name': 'Halloween Town', 'node': 'event_halloween_town'}), OrderedDict({'id': 613, 'enum': 'Event_Electric', 'name': 'Electric', 'node': 'event_electric'}), OrderedDict({'id': 614, 'enum': 'Event_Witch', 'name': 'Halloween Night', 'node': 'event_halloween_witch'}), OrderedDict({'id': 700, 'enum': 'Special_PaintMixer', 'name': 'Paint Mixer', 'node': 'hidden_ocftf'}), OrderedDict({'id': 800, 'enum': 'Kudos_TTC', 'name': 'Congratulations', 'node': 'kudos_ttc'}), OrderedDict({'id': 801, 'enum': 'Kudos_BB', 'name': 'On the Dock', 'node': 'kudos_bb'}), OrderedDict({'id': 802, 'enum': 'Kudos_YOTT', 'name': 'Hearty Feast', 'node': 'kudos_yott'}), OrderedDict({'id': 803, 'enum': 'Kudos_DG', 'name': 'Tranquil Fountain', 'node': 'kudos_dg'}), OrderedDict({'id': 804, 'enum': 'Kudos_MML', 'name': 'Rock Concert', 'node': 'kudos_mml'}), OrderedDict({'id': 805, 'enum': 'Kudos_TB', 'name': 'Doodlesledding', 'node': 'kudos_tb'}), OrderedDict({'id': 806, 'enum': 'Kudos_AA', 'name': 'Light Show', 'node': 'kudos_aa'}), OrderedDict({'id': 807, 'enum': 'Kudos_DDL', 'name': 'Sweet', 'node': 'kudos_ddl'})]


POSE_IDS = [entry['id'] for entry in POSES]
NAMEPLATE_IDS = [entry['id'] for entry in NAMEPLATES]
BACKGROUND_IDS = [entry['id'] for entry in BACKGROUNDS]

POSE_BY_ID = dict((entry['id'], entry) for entry in POSES)
NAMEPLATE_BY_ID = dict((entry['id'], entry) for entry in NAMEPLATES)
BACKGROUND_BY_ID = dict((entry['id'], entry) for entry in BACKGROUNDS)

# Old pre-inventory IDs used by early Clash/Altis profile resources.
LEGACY_NAMEPLATE_IDS = {
    0: 101, 1: 102, 2: 103, 3: 104, 4: 105, 5: 106, 6: 107, 7: 108, 8: 109,
    9: 500, 10: 203, 11: 207, 12: 501, 13: 600, 14: 601, 15: 602, 16: 603,
    17: 604, 18: 605, 19: 502, 20: 200, 21: 606, 22: 300, 23: 301, 24: 302,
    25: 201, 26: 202, 27: 204, 28: 205, 29: 206, 30: 607, 31: 608, 32: 609,
    33: 610, 34: 611, 35: 612, 36: 613, 37: 503, 38: 700, 39: 701, 40: 702,
    41: 703, 42: 704, 43: 705, 44: 400, 45: 504, 46: 505, 47: 800, 48: 801,
    49: 802, 50: 803, 51: 804, 52: 805, 53: 806, 54: 807, 55: 614, 56: 619,
}


def normalisePoseId(value):
    try:
        value = int(value)
    except:
        return DEFAULT_POSE
    if value not in POSE_BY_ID:
        return DEFAULT_POSE
    return value


def normaliseNameplateId(value):
    try:
        value = int(value)
    except:
        return DEFAULT_NAMEPLATE
    value = LEGACY_NAMEPLATE_IDS.get(value, value)
    if value not in NAMEPLATE_BY_ID:
        return DEFAULT_NAMEPLATE
    return value


def normaliseBackgroundId(value):
    try:
        value = int(value)
    except:
        return DEFAULT_BACKGROUND
    if value not in BACKGROUND_BY_ID:
        return DEFAULT_BACKGROUND
    return value


def getPose(value):
    return POSE_BY_ID[normalisePoseId(value)]


def getNameplate(value):
    return NAMEPLATE_BY_ID[normaliseNameplateId(value)]


def getBackground(value):
    return BACKGROUND_BY_ID[normaliseBackgroundId(value)]


def _call(toon, name, *args):
    method = getattr(toon, name, None)
    if method:
        try:
            return method(*args)
        except:
            return None
    return None


def _clearPoseProps(toon):
    props = getattr(toon, '_toonProfilePoseProps', [])
    for prop in props:
        try:
            prop.removeNode()
        except:
            pass
    toon._toonProfilePoseProps = []


def _isUsableModel(model):
    if model is None:
        return False
    try:
        return not model.isEmpty()
    except:
        return True


def _loadFirstModel(paths):
    for path in paths:
        try:
            model = loader.loadModel(path)
            if _isUsableModel(model):
                return model
        except:
            pass
    return None


def _loadProp(propName):
    try:
        if isinstance(propName, (list, tuple)):
            model = _loadFirstModel((propName[0], propName[0] + '.bam'))
            if not _isUsableModel(model):
                return None
            part = model.find(propName[1])
            if part.isEmpty():
                model.removeNode()
                return None
            part = part.copyTo(hidden)
            model.removeNode()
            return part

        # These aliases exist in Clash's BattleProps pool but not in Altis'.
        # Load their original models directly so the profile poses work
        # without replacing Altis' global prop registry.
        if propName == 'blue-megaphone':
            prop = _loadFirstModel((
                'phase_5/models/props/megaphone',
                'phase_5/models/props/megaphone.bam',
            ))
            if _isUsableModel(prop):
                try:
                    prop.setTexture(loader.loadTexture('phase_5/maps/gag_palette_1.png'), 1)
                except:
                    pass
            return prop

        if propName == 'button-no-actor':
            return _loadFirstModel((
                'phase_3.5/models/props/button-mod',
                'phase_3.5/models/props/button-mod.bam',
            ))

        if propName == 'treasure-chest':
            return _loadFirstModel((
                'phase_5/models/props/treasure-chest-mod',
                'phase_5/models/props/treasure-chest-mod.bam',
                'phase_5/models/props/treasure-chest',
                'phase_5/models/props/treasure-chest.bam',
            ))

        if propName == 'cosmetics/backpack/models/cc_m_acc_bp_sword_classic':
            # Clash mounts this at a virtual cosmetics/ path.  Altis content
            # packs may preserve that path, place it under phase_14, or only
            # have the original Toontown wooden sword, so try each safely.
            return _loadFirstModel((
                'cosmetics/backpack/models/cc_m_acc_bp_sword_classic',
                'cosmetics/backpack/models/cc_m_acc_bp_sword_classic.bam',
                'phase_14/cosmetics/backpack/models/cc_m_acc_bp_sword_classic',
                'phase_14/cosmetics/backpack/models/cc_m_acc_bp_sword_classic.bam',
                'phase_14/models/cosmetics/backpack/cc_m_acc_bp_sword_classic',
                'phase_14/models/cosmetics/backpack/cc_m_acc_bp_sword_classic.bam',
                'phase_14/models/accessories/cc_m_acc_bp_sword_classic',
                'phase_14/models/accessories/cc_m_acc_bp_sword_classic.bam',
                'phase_4/models/accessories/tt_m_chr_avt_acc_pac_woodenSword',
                'phase_4/models/accessories/tt_m_chr_avt_acc_pac_woodenSword.bam',
            ))

        if '/' in propName or propName.startswith('phase_'):
            return _loadFirstModel((propName, propName + '.bam'))

        from toontown.battle import BattleProps
        try:
            return BattleProps.globalPropPool.getProp(propName)
        except:
            return None
    except:
        return None


def _applyHighRollerPose(toon):
    try:
        legPath = _HIGH_ROLLER_LEG_ANIMS[toon.style.legs]
        torsoPath = _HIGH_ROLLER_TORSO_ANIMS[toon.style.torso]
        for lodName in ('1000', '500', '250'):
            toon.loadAnims({_HIGH_ROLLER_ANIM: legPath}, 'legs', lodName)
            toon.loadAnims({_HIGH_ROLLER_ANIM: torsoPath}, 'torso', lodName)
        toon.pose(_HIGH_ROLLER_ANIM, 0, 'legs')
        toon.pose(_HIGH_ROLLER_ANIM, 0, 'torso')
        toon.pose('neutral', 0, 'head')
        return True
    except:
        return False


def applyPose(toon, poseId, notify=None):
    """Apply one profile pose. Missing animations or props fall back safely."""
    entry = getPose(poseId)
    data = entry['data']
    _clearPoseProps(toon)

    # Species-changing poses must update the Toon before the animation and face.
    if 'Species' in data:
        try:
            from toontown.toon import ToonDNA
            dna = ToonDNA.ToonDNA()
            dna.makeFromNetString(toon.style.makeNetString())
            dna.head = '%s%s' % (data['Species'], toon.style.head[1:])
            toon.updateToonDNA(dna)
        except:
            pass

    if data.get('HighRollerPose'):
        if not _applyHighRollerPose(toon):
            try:
                toon.pose('neutral', 0)
            except:
                pass
    else:
        animation = data.get('Animation', ('neutral', 0))
        try:
            toon.pose(animation[0], animation[1])
        except:
            try:
                toon.loop('neutral')
            except:
                pass

    _call(toon, 'normalEyes')
    _call(toon, 'closeEyes')
    _call(toon, 'openEyes')
    eyeType = data.get('Eyes')
    if eyeType == 'sad':
        _call(toon, 'sadEyes'); _call(toon, 'closeEyes'); _call(toon, 'openEyes')
    elif eyeType == 'surprise':
        _call(toon, 'surpriseEyes')
    elif eyeType == 'angry':
        _call(toon, 'angryEyes'); _call(toon, 'closeEyes'); _call(toon, 'openEyes')
    elif eyeType == 'close':
        _call(toon, 'closeEyes')

    for method in ('hideSadMuzzle', 'hideSurpriseMuzzle', 'hideAngryMuzzle', 'hideSmileMuzzle', 'hideLaughMuzzle'):
        _call(toon, method)
    muzzleType = data.get('Muzzle')
    muzzleMethods = {
        'sad': 'showSadMuzzle', 'surprise': 'showSurpriseMuzzle',
        'angry': 'showAngryMuzzle', 'smile': 'showSmileMuzzle',
        'laugh': 'showLaughMuzzle',
    }
    if muzzleType in muzzleMethods:
        _call(toon, muzzleMethods[muzzleType])

    try:
        toon.setHpr(*data.get('Hpr', (0, 0, 0)))
    except:
        toon.setHpr(0, 0, 0)

    if 'Scale' in data:
        try:
            toon.setScale(toon.getScale() * float(data['Scale']))
        except:
            pass

    propNames = data.get('Prop', [])
    propParents = data.get('PropParent', [])
    propPositions = data.get('PropPos', [])
    propHprs = data.get('PropHpr', [])
    propScales = data.get('PropScale', [])
    madeProps = []
    for index in xrange(len(propNames)):
        prop = _loadProp(propNames[index])
        if not prop:
            continue
        try:
            parentName = propParents[index] if index < len(propParents) else None
            parent = getattr(toon, parentName) if parentName else toon
            prop.reparentTo(parent)
            if index < len(propPositions):
                prop.setPos(propPositions[index])
            if index < len(propHprs):
                prop.setHpr(propHprs[index])
            if index < len(propScales):
                prop.setScale(propScales[index])
            madeProps.append(prop)
        except:
            try:
                prop.removeNode()
            except:
                pass
    toon._toonProfilePoseProps = madeProps
    _call(toon, 'stopLookAroundNow')
    return data.get('AvatarPanelPos', (0, 0, 0))
