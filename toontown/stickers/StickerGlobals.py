# Python 2 compatible sticker registry for Project Altis.

DICE_ROLL = 40
ERFIT_HYDRATE = 56

# id, display name, node path inside phase_3.5/models/gui/stickers.bam,
# 3-D scale, 2-D menu scale
STICKERS = (
    (0, 'Disgust Gator', '**/disgust_gator', 1.0, 1.0),
    (1, 'Concerned Dog', '**/concerned_dog', 1.0, 1.0),
    (2, 'Confused Kangaroo', '**/confused_kangaroo', 1.0, 1.0),
    (3, 'Cry Cat', '**/cry_cat', 1.0, 1.0),
    (4, 'Grief Kiwi', '**/grief_kiwi', 1.0, 1.0),
    (5, 'Blush Bat', '**/blush_bat', 1.0, 1.0),
    (6, 'Grin Duck', '**/grin_duck', 1.0, 1.0),
    (7, 'Heart Rabbit', '**/heart_rabbit', 1.0, 1.0),
    (8, 'Greened Cat', '**/greened_cat', 1.0, 1.0),
    (9, 'Pensive Fox', '**/pensive_fox', 1.0, 1.0),
    (10, 'Pleading Dog', '**/pleading_dog', 1.0, 1.0),
    (11, 'Sad Bat', '**/sad_bat', 1.0, 1.0),
    (12, 'Surprised Armadillo', '**/surprised_armadillo', 1.0, 1.0),
    (13, 'Surprised Raccoon', '**/surprised_raccoon', 1.0, 1.0),
    (14, 'Suspicious Beaver', '**/sus_beaver', 1.0, 1.0),
    (15, 'Wink Deer', '**/wink_deer', 1.0, 1.0),
    (16, 'Bellringer', '**/bellringer', 1.0, 1.0),
    (17, 'Chainsaw Consultant', '**/chainsaw_consultant', 1.0, 1.0),
    (18, 'Deep Diver', '**/deep_diver', 1.0, 1.0),
    (19, 'Duck Shuffler', '**/duck_shuffler', 1.0, 1.0),
    (20, 'Featherbedder', '**/featherbedder', 1.0, 1.0),
    (21, 'Firestarter', '**/firestarter', 1.0, 1.0),
    (22, 'Gatekeeper', '**/gatekeeper', 1.0, 1.0),
    (23, 'Major Player', '**/major_player', 1.0, 1.0),
    (24, 'Mouthpiece', '**/mouthpiece', 1.0, 1.0),
    (25, 'Multislacker', '**/multislacker', 1.0, 1.0),
    (26, 'Pacesetter', '**/pacesetter', 1.0, 1.0),
    (27, 'Plutocrat', '**/plutocrat', 1.0, 1.0),
    (28, 'Prethinker', '**/prethinker', 1.0, 1.0),
    (29, 'Rainmaker', '**/rainmaker', 1.0, 1.0),
    (30, 'Treekiller', '**/treekiller', 1.0, 1.0),
    (31, 'Witch Hunter', '**/witch_hunter', 1.0, 1.0),
    (32, 'Sellbot Emblem', '**/insignia_sellbot', 0.90625, 1.0),
    (33, 'Cashbot Emblem', '**/insignia_cashbot', 0.90625, 1.0),
    (34, 'Lawbot Emblem', '**/insignia_lawbot', 0.90625, 1.0),
    (35, 'Bossbot Emblem', '**/insignia_bossbot', 0.90625, 1.0),
    (36, 'Boardbot Emblem', '**/insignia_boardbot', 0.90625, 1.0),
    (40, 'Dice Roll', '**/dice_base', 0.9375, 0.88),
    (50, 'High Roller', '**/high_roller', 1.0, 1.0),
    (51, 'Frustrated Foreman', '**/frustrated_foreman', 1.0, 1.0),
    (52, 'Litigator', '**/litigator', 1.0, 1.0),
    (53, 'Stenographer', '**/stenographer', 1.0, 1.0),
    (54, 'Case Manager', '**/case_manager', (1.0, 1.0, 406.0 / 676.0), (1.0, 1.0, 406.0 / 676.0)),
    (55, 'Scapegoat', '**/scapegoat', 1.0, 1.0),
    (56, 'Erfit Hydrate', '**/erfit_hydrate', 1.0, 1.0),
)

STICKER_BY_ID = dict((entry[0], entry) for entry in STICKERS)
VALID_STICKER_IDS = set(STICKER_BY_ID.keys())


# Sticker sound effects. Paths are relative to the resources directory.
# Stickers omitted from this table intentionally remain silent.
STICKER_SFX_PATHS = {
    16: 'phase_5/audio/sfx/SA_healing_bell.ogg',
    17: 'phase_5/audio/sfx/SA_revving_up.ogg',
    18: 'phase_3.5/audio/dial/ttcc_ene_ddiver_statement.ogg',
    19: 'phase_5/audio/sfx/SA_wager_spin.ogg',
    20: 'phase_3.5/audio/dial/ttcc_ene_fbed_statement.ogg',
    21: 'phase_3.5/audio/dial/ttcc_ene_fires_statement.ogg',
    22: 'phase_5/audio/sfx/SA_defense.ogg',
    23: 'phase_3.5/audio/dial/ttcc_ene_mplayer_statement.ogg',
    24: 'phase_3.5/audio/sfx/SA_hangup.ogg',
    25: 'phase_5/audio/sfx/SZ_MM_fanfare.ogg',
    26: 'phase_5/audio/sfx/SA_hurry_sickness.ogg',
    27: 'phase_5/audio/sfx/SA_deepfreeze.ogg',
    28: 'phase_3.5/audio/dial/ttcc_ene_prethink_statement.ogg',
    29: 'phase_3.5/audio/dial/ttcc_ene_rainmake_statement.ogg',
    30: 'phase_3.5/audio/dial/ttcc_ene_treek_statement.ogg',
    31: 'phase_5/audio/sfx/SA_mob_mentality.ogg',
    DICE_ROLL: 'phase_3.5/audio/sfx/tt_s_sfx_sticker_dice.ogg',
    50: 'phase_3.5/audio/dial/ttcc_ene_hrollerc_murmur.ogg',
    51: 'phase_3.5/audio/dial/COG_VO_statement_skel.ogg',
    52: 'phase_5/audio/sfx/SA_bash.ogg',
    53: 'phase_5/audio/sfx/SA_sanction.ogg',
    54: 'phase_5/audio/sfx/SA_insurance.ogg',
    55: 'phase_5/audio/sfx/SA_rage.ogg',
    ERFIT_HYDRATE: 'phase_13/audio/bgm/halloween/hydration_sticker.ogg',
}


def isValidSticker(stickerId):
    try:
        return int(stickerId) in VALID_STICKER_IDS
    except (TypeError, ValueError):
        return False


def getStickerName(stickerId, modifier=0):
    try:
        stickerId = int(stickerId)
    except (TypeError, ValueError):
        return 'Unknown Sticker'
    if stickerId == DICE_ROLL and modifier in (1, 2, 3, 4, 5, 6):
        return 'Rolled a %d' % modifier
    data = STICKER_BY_ID.get(stickerId)
    return data[1] if data else 'Unknown Sticker'


def getStickerNode(stickerId, modifier=0):
    try:
        stickerId = int(stickerId)
    except (TypeError, ValueError):
        return None
    if stickerId == DICE_ROLL and modifier in (1, 2, 3, 4, 5, 6):
        return '**/dice_%d' % modifier
    data = STICKER_BY_ID.get(stickerId)
    return data[2] if data else None


def getStickerScale3d(stickerId):
    data = STICKER_BY_ID.get(int(stickerId))
    return data[3] if data else 1.0


def getStickerScale2d(stickerId):
    data = STICKER_BY_ID.get(int(stickerId))
    return data[4] if data else 1.0


def getStickerSfxPath(stickerId):
    try:
        stickerId = int(stickerId)
    except (TypeError, ValueError):
        return None
    return STICKER_SFX_PATHS.get(stickerId)

