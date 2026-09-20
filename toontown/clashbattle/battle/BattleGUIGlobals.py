# Positioning for the Gag Buttons
from toontown.clashbattle.battle.attacks.base.AttackEnum import AttackEnum

GagButtonsXOffset = -0.22
GagButtonsXSpacing = 0.084

# Separation between Gag Tracks
GagTracksZSeparation = 0.059

# Suit Panel
SuitPanelHeight = 0.7
SuitPanelXSpacing = 0.51
SuitPanelScale = 0.525

# Toon Panel
ToonPanelHeight = -0.8
ToonPanelXSpacing = 0.65
ToonPanelScaling = 0.645

# Battle Timer
BattleTimerPos = (-0.153, 0, 0.14)
BattleTimerScale = 0.35

# Targeting Arrows
TargetingArrowHeight = 0.4
TargetingArrowScale = 0.22

# Targeting GUI
TargetingGuiScale = 0.5

# EXP Text
TrackTitleZOffset = 0.013275
TrackTitleZOffsetNoBar = 0.0
TrackTitleToonupScale = (0.2, 1, 0.05)
TrackTitleScale = (0.1, 1, 0.05)
TrackTitleToonupScaleNoBar = (0.2 * 1.15, 1, 0.05 * 1.15)
TrackTitleScaleNoBar = (0.1 * 1.15, 1, 0.05 * 1.15)


# Movie Laff Meters Positions
MovieLaffMeterPos = {
    0: (0.38, 0.0, 0.13),
    1: (0.63, 0.0, 0.13),
    2: (0.88, 0.0, 0.13),
}


def getTrackTitleScale(track: int, showBar: bool):
    if track == AttackEnum.TOON_HEAL:
        return TrackTitleToonupScale if showBar else TrackTitleToonupScaleNoBar
    return TrackTitleScale if showBar else TrackTitleScaleNoBar
