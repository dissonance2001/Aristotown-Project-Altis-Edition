from enum import Enum, auto
from typing import Dict

from toontown.toon import ToonGlobals


class GlobalCacheCategory(Enum):
    Models = auto()
    Sounds = auto()


class GlobalCacheKey(Enum):
    Global = auto()

    TTC = auto()
    BB = auto()
    YOTT = auto()
    DG = auto()
    MML = auto()
    TB = auto()
    OZ = auto()
    DDL = auto()
    GZ = auto()
    GS = auto()
    TS = auto()
    SC = auto()
    Estate = auto()

    SBHQ = auto()
    CBHQ = auto()
    LBHQ = auto()
    BBHQ = auto()
    BDHQ = auto()

    Factory = auto()
    Mint = auto()
    Lawfice = auto()
    CountryClub = auto()

    SellbotBoss = auto()
    CashbotBoss = auto()
    LawbotBoss = auto()
    BossbotBoss = auto()


toonLODs = [1000]
toonModels = [
    # Toon Heads
    *[f'phase_3{headValue}{lodValue}' for lodValue in toonLODs for headValue in ToonGlobals.HeadDict.values()],
    *[f'phase_3{eyelashValue}' for eyelashValue in ToonGlobals.EyelashDict.values()],
    *[f'phase_3{dogMuzzleValue}{lodValue}' for lodValue in toonLODs for dogMuzzleValue in ToonGlobals.DogMuzzleDict.values()],
    # Toon Bodies
    *[f'phase_3{torsoValue}{lodValue}' for lodValue in toonLODs for torsoValue in ToonGlobals.TorsoDict.values()],
    *[f'phase_3{legValue}{lodValue}' for lodValue in toonLODs for legValue in ToonGlobals.LegDict.values()],
]

cogBodyTex = 'char/suit/models/cc_m_texcard_ene_suit_body_common'
skelBodyTex = 'char/suit/models/cc_m_texcard_ene_skel_body_common'


GlobalCacheDataRegistry: Dict[GlobalCacheKey, Dict] = {
    # Global, used across the entire game in all circumstances
    GlobalCacheKey.Global: {
        GlobalCacheCategory.Models: [
            # All Toon stuff
            *toonModels,
            # Suits
            cogBodyTex,
            'phase_3.5/models/char/suitA-mod',
            'phase_3.5/models/char/suitB-mod',
            'phase_3.5/models/char/suitC-mod',
            'phase_3.5/models/char/suitA_f-mod',
            'phase_3.5/models/char/suitB_f-mod',
            'phase_3.5/models/char/suitC_f-mod',
            # Suit Heads are included at a later time, though they are here.
            # Dropshadows
            'phase_3/models/props/square_drop_shadow',
            'phase_3/models/props/drop_shadow',
            # Scaled Frame
            'phase_3/models/gui/ttcc_gui_scaledFrame',
        ],
        GlobalCacheCategory.Sounds: [
            'phase_3/audio/sfx/GUI_rollover.ogg',
            'phase_3/audio/sfx/GUI_create_toon_fwd.ogg',
        ],
    },
    # region Neighborhoods
    GlobalCacheKey.TTC: {
        GlobalCacheCategory.Models: [
            'phase_4/models/props/SZ_butterfly-mod',
        ],
    },
    GlobalCacheKey.DG: {
        GlobalCacheCategory.Models: [
            'phase_4/models/props/SZ_butterfly-mod',
        ],
    },
    # endregion
    # region Cog HQs
    # region Cog HQ Courtyards
    GlobalCacheKey.SBHQ: {
        GlobalCacheCategory.Models: [
            skelBodyTex,
        ],
    },
    GlobalCacheKey.CBHQ: {
        GlobalCacheCategory.Models: [
            skelBodyTex,
        ],
    },
    GlobalCacheKey.LBHQ: {
        GlobalCacheCategory.Models: [
            skelBodyTex,
        ],
    },
    GlobalCacheKey.BBHQ: {
        GlobalCacheCategory.Models: [
            skelBodyTex,
        ],
    },
    # endregion
    # region Cog HQ facilities
    GlobalCacheKey.Factory: {
        GlobalCacheCategory.Models: [
            skelBodyTex,
            'phase_9/models/char/Cog_Goonie-zero',
            'phase_9/models/cogHQ/alphaCone2',
            'phase_9/models/cogHQ/FloorWear',
            'phase_9/models/cogHQ/CogDoorHandShake',
            'phase_9/models/cogHQ/woodCrateB',
            'phase_9/models/cogHQ/square_stomper',
            'phase_4/models/props/test_clouds',
            'phase_9/models/cogHQ/platform1',
            'phase_9/models/cogHQ/FactoryGearB',
            'phase_9/models/cogHQ/CogDoor_Button',
        ],
        GlobalCacheCategory.Sounds: [
            'phase_9/audio/sfx/CHQ_GOON_hunker_down.ogg',
            'phase_9/audio/sfx/CHQ_GOON_rattle_shake.ogg',
            'phase_9/audio/sfx/CHQ_GOON_tractor_beam_alarmed.ogg',
            'phase_4/audio/sfx/CHQ_FACT_stomper_small.ogg',
            'phase_9/audio/sfx/CHQ_FACT_stomper_med.ogg',
            'phase_9/audio/sfx/CHQ_FACT_stomper_large.ogg',
            'phase_9/audio/sfx/CHQ_FACT_door_open_sliding.ogg',
            'phase_9/audio/sfx/CHQ_FACT_door_open_final.ogg',
            'phase_9/audio/sfx/CHQ_FACT_arms_retracting.ogg',
            'phase_9/audio/sfx/CHQ_FACT_door_unlock.ogg',
            'phase_9/audio/sfx/CHQ_FACT_switch_pressed.ogg',
            'phase_9/audio/sfx/CHQ_FACT_switch_depressed.ogg',
            'phase_9/audio/sfx/CHQ_FACT_switch_popup.ogg',
            'phase_9/audio/sfx/CHQ_FACT_crate_effort.ogg',
            'phase_9/audio/sfx/CHQ_FACT_crate_sliding.ogg',
            'phase_9/audio/sfx/CHQ_FACT_elevator_up_down.ogg',
        ],
    },
    GlobalCacheKey.Mint: {
        GlobalCacheCategory.Models: [
            skelBodyTex,
        ],
    },
    GlobalCacheKey.Lawfice: {
        GlobalCacheCategory.Models: [
            skelBodyTex,
        ],
    },
    GlobalCacheKey.CountryClub: {
        GlobalCacheCategory.Models: [
            skelBodyTex,
        ],
    },
    # endregion
    # region Cog HQ Bosses
    GlobalCacheKey.SellbotBoss: {
        GlobalCacheCategory.Models: [
            skelBodyTex,
        ],
    },
    GlobalCacheKey.CashbotBoss: {
        GlobalCacheCategory.Models: [
            skelBodyTex,
        ],
    },
    GlobalCacheKey.LawbotBoss: {
        GlobalCacheCategory.Models: [
            skelBodyTex,
        ],
    },
    GlobalCacheKey.BossbotBoss: {
        GlobalCacheCategory.Models: [
            skelBodyTex,
        ],
    },
    # endregion
}


def addSuitHeadsToGlobal():
    from toontown.suit import SuitGlobals
    from toontown.shtiker import CogPageGlobals

    # We want to delay this until all of our cog stuff would be good to go anyways,
    # That way we don't have to do stupid circular import stuff
    suitHeads = []
    for deptList in CogPageGlobals.indexToCogName:
        for suitName in deptList:
            if suitName in SuitGlobals.suitProperties:
                headParts = SuitGlobals.suitProperties[suitName][SuitGlobals.HEADS_INDEX]
                for headPart in headParts:
                    if headPart not in suitHeads:
                        suitHeads.append(headPart)
    suitHeads.extend([
        'phase_9/models/char/sellbotBoss-head-zero',
        'phase_10/models/char/cashbotBoss-head-zero',
        'phase_11/models/char/lawbotBoss-head-zero',
        'phase_12/models/char/bossbotBoss-head-zero',
    ])

    GlobalCacheDataRegistry[GlobalCacheKey.Global][GlobalCacheCategory.Models].extend(suitHeads)
