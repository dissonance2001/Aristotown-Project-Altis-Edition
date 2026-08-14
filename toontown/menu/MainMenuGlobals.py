from panda3d.core import Vec4

TT_PLAY_AV_BOX_COLORS = (
    Vec4(0.917, 0.164, 0.164, 1),
    Vec4(0.152, 0.75, 0.258, 1),
    Vec4(0.598, 0.402, 0.875, 1),
    Vec4(0.133, 0.59, 0.977, 1),
    Vec4(0.895, 0.348, 0.602, 1),
    Vec4(0.977, 0.816, 0.133, 1),
)

TT_PLAY_AV_BOX_POSITIONS = (
    (-1, 0, 0.25), (-0.55, 0, 0.25), (-0.1, 0, 0.25),
    (-1, 0, -0.25), (-0.55, 0, -0.25), (-0.1, 0, -0.25),
)

optionsPerRow = 2
maxRowsShownAtOnce = 3
colGlobals = [-.35, .35]
rowStartingZ = .4
rowSeparation = .25
colCondensedGlobals = [-.5, .5]
rowCondensedGlobals = [.5, .3, .1, -.1, -.3, -.5]
