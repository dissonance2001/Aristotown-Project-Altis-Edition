"""
FogGlobals
Manage default fog colors & intensities here.

@author: Loonatic
@date: 5/30/2022
"""
from panda3d.core import Vec3, Vec4, Fog
from toontown.utils.ColorHelper import hexToPCol

# Assumes base.wantFog doesn't ever toggle off during a session
WANT_FOG = base.wantFog

"""
zoneId : [
    Fog Color (Vec3 or Vec4)
    Fog Mode (Fog.M_x)
    Fog Mode Attribute (linear range/exp density)
    (Linear mode only) Fog Linear Fallback (angle, onset, opaque)
]
"""
from toontown.toonbase.ToontownGlobals import (
    DonaldsDock,
    DonaldsDreamland,
    BossbotHQ,
    TheBrrrgh
)

zoneId2FogAttrs = {
    BossbotHQ: [
        hexToPCol('#000000'),
        Fog.M_exponential,
        (.0045)
    ],
    DonaldsDock: [
        hexToPCol('#cccccc'),
        Fog.M_linear,
        (0.0, 400.0),
        None
    ],
    DonaldsDreamland: [
        hexToPCol('#8c8ca6'),
        Fog.M_linear,
        (0.0, 800.0),
        None
    ],
    TheBrrrgh: [
        hexToPCol('#f1f3f9'),
        Fog.M_exponential,
        (0.0017),
    ],
}

"""
Racing Area Fogs
"""
RacetrackGeneralFogAttrs = [
    Vec4(0.6, 0.7, 0.8, 1.0),
    Fog.M_linear,
    (200.0, 650.0)
]

RacetrackUrbanFogAttrs = [
    Vec4(0.6, 0.7, 0.8, 1.0),
    Fog.M_linear,
    (200.0, 800.0)
]

"""
Zone-Unrelated Defined Fog Attributes
"""

DefaultFogAttrs = [
    hexToPCol('#ffffff', a = 255),  # Color
    Fog.M_linear,  # Mode
    (0.0, 100.0),  # Attributes (wrt mode)
    None
]

UnderwaterFogAttrs = [
    hexToPCol('#000099'),  # Color
    Fog.M_linear,  # Mode
    (0.1, 100.0),  # Attributes (wrt mode)
    None
]

RingGameFogAttrs = [
    hexToPCol('#000099'),  # Color
    Fog.M_linear,  # Mode
    # self.FAR_PLANE_DIST - 1.0 (DistributedRingGame)
    (0.1, 149.0),  # Attributes (wrt mode)
    None
]

TargetGameFogAttrs = [
    Vec4(0.75, 0.8, 1.0, 1.0),
    Fog.M_linear,  # Mode
    (0.1, 600)  # FOGDISTGROUND
]

TugOfWarFogAttrs = [
Vec4(0.8, 0.8, 0.8, 1.0),
    Fog.M_linear,
    (0.0, 400.0)
]

FaintFogAttrs = [
    hexToPCol('#cccccc'),
    Fog.M_linear,
    (0.0, 700.0),
    None
]

# ToonHood accommodation
WhiteFogAttrs = [
    hexToPCol('#cccccc'),
    Fog.M_linear,
    (0.0, 400.0),
    None
]

FireworksFogAttrs = WhiteFogAttrs


# Sellbot VP Bossroom

SellbotVPBossSkyFogAttrs = [
    hexToPCol('#000000'),
    Fog.M_exponential,
    (0.0009889792263507843),
]

SellbotVPBossBuildingFogAttrs = [
    hexToPCol('#000000'),
    Fog.M_exponential,
    (0.004322273191064596),
]

SellbotVPBossRoomFogAttrs = [
    hexToPCol('#000000'),
    Fog.M_exponential,
    (0.0008525646990165114),
]


def zoneId2FogColor(zoneId):
    return zoneId2FogAttrs.get(zoneId)[0]


# Merc fogs

ChainsawConsultantFogAttrs = [
    hexToPCol('#000000'),
    Fog.M_exponential,
    (0.009999999776482582),
]

MultislackerFogAttrs = [
    Vec4(0.05371369421482086, 0.044700875878334045, 0.031182244420051575, 1.0),
    Fog.M_exponential_squared,
    (0.0024747587740421295),
]

MultislackerHallwayFogAttrs = [
    Vec4(0.0, 0.0, 0.0, 1.0),
    Fog.M_exponential,
    (0.004322282038629055),
]

MultislackerCorridorFogAttrs = [
    Vec4(0.0, 0.0, 0.0, 1.0),
    Fog.M_linear,
    (-288.751953, 513.3382568),
]

PlutocratColdRoomFogAttrs = [
    Vec4(0.9098765850067139, 0.9864819645881653, 1.0, 1.0),
    Fog.M_exponential,
    (0.00441)
]

PlutocratBossRoomFogAttrs = [
    Vec4(0.6044301986694336, 0.6166014671325684, 1.0, 1.0),
    Fog.M_exponential,
    (0.0099999)
]

PacesetterBossRoomFogAttrs = [
    Vec4(0.7521629929542542, 0.13482369482517242, 0.5993223786354065, 1.0),
    Fog.M_exponential_squared,
    (0.002159339)
]

PrethinkerBossroomFogAttrs = [
    Vec4(0.7161135077476501, 0.7208651900291443, 0.5674121379852295, 1.0),
    Fog.M_exponential,
    (0.0015735484194010496)
]

RainmakerGhostShipFogAttrs = [
    hexToPCol('#000000'),
    Fog.M_exponential_squared,
    (0.008017301559448242)
]

AprilToonsMenuFogAttrs = [
    Vec4(0.8090276122093201, 0.8263886570930481, 1.0, 1.0),
    Fog.M_exponential,
    (0.0016),
]
