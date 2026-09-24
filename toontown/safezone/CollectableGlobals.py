from toontown.quest3.QuestEnums import QuestCollectable

TreasureModels = {
    (QuestCollectable.SwingsetA, QuestCollectable.SwingsetB,
     QuestCollectable.SwingsetC, QuestCollectable.SwingsetD): (
        'areas/estate/furniture/models/cc_m_ara_est_prp_furn_candy_swingset',
        'phase_4/audio/sfx/SZ_DD_treasure.ogg',
        0.25,
        None,
        True,
    ),
    QuestCollectable.ToonselPresent: (
        'phase_13/models/events/toonseltown/present_1',
        'phase_4/audio/sfx/SZ_DD_treasure.ogg',
        1.2,
        None,
        True,
    ),
    QuestCollectable.TumblesTiara: (
        'cosmetics/hat/models/cc_m_acc_hat_crown_tiara_classic',
        'phase_4/audio/sfx/SZ_DD_treasure.ogg',
        1.0,
        None,
        True,
    ),
    QuestCollectable.KudosBox: (
        'phase_9/models/cogHQ/woodCrateB',
        'phase_4/audio/sfx/SZ_DD_treasure.ogg',
        0.4,
        '**/collision',
        True,
    ),
    QuestCollectable.AllStarShower: (
        'areas/estate/furniture/models/cc_m_ara_est_prp_furn_candy_swingset',
        'phase_4/audio/sfx/MG_sfx_travel_game_bonus.ogg',
        0.25,
        None,
        False,
    )
}

Collectable2Pos = {
    QuestCollectable.SwingsetA: [(631.8, 114.5, 0.5)],
    QuestCollectable.SwingsetB: [(202, -83.6, -1.9)],
    QuestCollectable.SwingsetC: [(13, 124.6, 6.2)],
    QuestCollectable.SwingsetD: [(-9.6, 117, 0.2)],
    QuestCollectable.TumblesTiara:   [(-69.13, 38.6, 1.3)],
    QuestCollectable.ToonselPresent: [(-57.451, 338.9, 34.7)],
    QuestCollectable.KudosBox: [(124.411, 146.040, 5.025)],
    QuestCollectable.AllStarShower: [(0.072, 58.834, 0.025)],
}
