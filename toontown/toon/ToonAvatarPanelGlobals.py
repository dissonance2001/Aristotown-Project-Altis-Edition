from __future__ import absolute_import
from pandac.PandaModules import Vec4


toonPos = {
    'ss': (0, 0, -0.28, 180, 0, 0),
    'sm': (0, 0, -0.32, 180, 0, 0),
    'sl': (0, 0, -0.39, 180, 0, 0),
    'ms': (0, 0, -0.303, 180, 0, 0),
    'mm': (0, 0, -0.34, 180, 0, 0),
    'ml': (0, 0, -0.42, 180, 0, 0),
    'ls': (0, 0, -0.36, 180, 0, 0),
    'lm': (0, 0, -0.4, 180, 0, 0),
    'll': (0, 0, -0.46, 180, 0, 0),
}

disguiseSuitPos = {
    # The details frame is mirrored on X, so positive X appears on the left.
    # Visible order: Sellbot, Cashbot, Lawbot, Bossbot, Boardbot.
    's': (0.315, 0, -0.20),
    'm': (0.1575, 0, -0.20),
    'l': (0.0, 0, -0.20),
    'c': (-0.1575, 0, -0.20),
    'g': (-0.315, 0, -0.20),
}

disguiseTextPos = {
    's': (0.315, 0, -0.23),
    'm': (0.1575, 0, -0.23),
    'l': (0.0, 0, -0.23),
    'c': (-0.1575, 0, -0.23),
    'g': (-0.315, 0, -0.23),
}

disguiseBarsPos = {
    's': (0.315, 0, 0.14),
    'm': (0.1575, 0, 0.14),
    'l': (0.0, 0, 0.14),
    'c': (-0.1575, 0, 0.14),
    'g': (-0.315, 0, 0.14),
}

questFramePlaceList = (
    (-0.17, 0, 0.02, 0, 0, 0),
    (0.17, 0, 0.02, 0, 0, 0),
    (-0.17, 0, -0.19, 0, 0, 0),
    (0.17, 0, -0.19, 0, 0, 0),
)

colors = {
    'disabledImageColor': Vec4(1, 1, 1, 0.4),
    'noPetImageColor': Vec4(1, 0, 0, 0.4),
    'text0Color': Vec4(1, 1, 1, 1),
    'text1Color': Vec4(0.5, 1, 0.5, 1),
    'text2Color': Vec4(1, 1, 0.5, 1),
    'text3Color': Vec4(0.6, 0.6, 0.6, 1),
}

badgeLocations = {
    'tr': (0.199, 0, 0.419),
}
