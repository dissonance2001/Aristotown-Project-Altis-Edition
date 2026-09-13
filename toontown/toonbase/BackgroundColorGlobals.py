"""
BackgroundColorGlobals
Manage the color of the render background here.

@author: Loonatic
@date: 5/31/2022
"""
from panda3d.core import Vec3, Vec4
from toontown.utils.ColorHelper import hexToPCol, randomNormalizedColor
from toontown.toonbase.ToontownGlobals import (
    ToontownCentral,
    DonaldsDock,
    YeOlde,
    DaisyGardens,
    MinniesMelodyland,
    TheBrrrgh,
    OutdoorZone,
    DonaldsDreamland,
    BossbotHQ,
    SkyClan,
)


def randomBackgroundColor(a=1.0):
    color = randomNormalizedColor(a)
    base.setBackgroundColor(color)
    return color


# This is what the background color should be when we don't explicitly set it to something else.
DefaultBG = hexToPCol('#4d4d4d')

"""
Playground/street relative colors
"""

zoneId2BG = {
    SkyClan:            hexToPCol('#9ed4e8'),
    ToontownCentral:    hexToPCol('#178c36'),
    DonaldsDock:        hexToPCol('#cccccc'),
    DaisyGardens:       hexToPCol('#148a12'),
    MinniesMelodyland:  Vec4(189/255, 183/255, 229/255, 1.0),
    TheBrrrgh:          hexToPCol('#f1f3f9'),
    OutdoorZone:        hexToPCol('#178c36'),
    DonaldsDreamland:   hexToPCol('#33364b'),
    BossbotHQ:          hexToPCol('#000000'),
}

OutdoorZoneUnderwaterBG = hexToPCol('#3dd8ff')
SkyClanUnderwaterBG     = hexToPCol('#9ed4e8')

"""
Suit Interior relative colors
"""
intZoneId2BG = {
    ToontownCentral:    hexToPCol('#b5bbca'),
    DonaldsDock:        hexToPCol('#b5bbca'),
    YeOlde:       hexToPCol('#cbbedc'),
    DaisyGardens:       hexToPCol('#b5bbca'),
    MinniesMelodyland:  Vec4(189/255, 183/255, 229/255, 1.0),
    TheBrrrgh:          hexToPCol('#b5bbca'),
    OutdoorZone:        hexToPCol('#b5bbca'),
    DonaldsDreamland:   hexToPCol('#7a82a6'),
}
intDefaultBG = hexToPCol('#b3bbc8')

"""
GUI relative colors
"""
AvatarChooserBG =       hexToPCol('#255ec7')
CatalogScreenBG =       hexToPCol('#874a49')
CongratulationsNameBG = hexToPCol('#c35a3c')

# toontown.minigame.Purchase
PurchaseMenuBG =        hexToPCol('#c7a687')  # enterPurchase state
PurchaseRewardMenuBG =  hexToPCol('#0099ff')  # enterReward state

"""
Minigame relative colors
"""
PatternGameBG =         hexToPCol('#fbfb95')
RaceGameBG =            hexToPCol('#30ca00')
RingGameBG =            hexToPCol('#000099')  # WATER_COLOR
TargetGameBG =          hexToPCol('#bfccff')
TravelGameBG =          hexToPCol('#30ca00')
