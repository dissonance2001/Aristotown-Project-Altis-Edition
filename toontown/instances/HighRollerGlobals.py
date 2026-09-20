"""
This module contains all of the definitions & localizer
for the High Roller battle.
"""
from enum import IntEnum, auto
from typing import Union

from panda3d.core import Vec4

from toontown.clashbattle.battle.attacks.base.AttackEnum import AttackEnum
from toontown.clashbattle.battle.statuses.StatusEffectEnums import StatusEffectEnum

"""
General Enums
"""


class HighRollerGameEnum(IntEnum):
    TRIVIA = auto()
    PUZZLE = auto()
    SHUFFLE = auto()
    BETWEEN = auto()


"""
Clone Colors
"""

CloneType2Visuals = {
    # Copied from StatusEffectGlobals.
    # Toonup - Purple
    0: (Vec4(0.322, 0.086, 0.753, 1.0), "Purple Silhouette", 'cashback', 1.0),
    # Trap - Red
    1: (Vec4(0.792, 0.051, 0.051, 1.0), "Red Silhouette", 'trap_card', 0.85),
    # Lure - Green
    2: (Vec4(0.294, 0.918, 0.208, 1.0), "Green Silhouette", 'no_green_light', 1.0),
    # Throw - Orange
    3: (Vec4(0.925, 0.635, 0.200, 1.0), "Orange Silhouette", 'full_deck', 0.85),
    # Squirt - Pink
    4: (Vec4(0.871, 0.384, 0.910, 1.0), "Pink Silhouette", 'backfire', 1.0),
    # Zap - Yellow
    5: (Vec4(0.929, 0.945, 0.212, 1.0), "Yellow Silhouette", 'fizzle', 1.0),
    # Sound - Blue
    6: (Vec4(0.071, 0.396, 0.867, 1.0), "Blue Silhouette", 'singing_blues', 1.0),
    # Drop - Light Blue
    7: (Vec4(0.271, 0.886, 0.859, 1.0), "Light Blue Silhouette", 'duck_drop', 0.7),
}


"""
Dice Stuff
"""

# Additive gag power scaling for the 4 pip move.
PipGagBoost = 15

InventoryDiceName = {
    0: '1-Pip Dice',
    1: '2-Pip Dice',
    2: '3-Pip Dice',
    3: '4-Pip Dice',
    4: '5-Pip Dice',
    5: '6-Pip Dice',
    # Special gold-dice
    6: 'Golden 6-Pip Dice',
}

InventoryDiceDescription = {
    0: 'Reroll and get a \1deepGreen\1new\nset of dice\2.',
    1: 'Your next Gag will\nhave \1deepGreen\1perfect accuracy\2.\nStacks duration.',
    2: 'Reduce your \1deepGreen\1Pip Costs\2\nfor \1deepGreen\1Gags\2 and \1deepGreen\1Dice\2 this\nturn by \1deepGreen\1two\2.\nStacks duration.',
    3: f'Everyone\'s Gags this\nturn will be\1deepGreen\1 {PipGagBoost}%\nstronger\2. Stacks\nadditively.',
    4: 'Gain a \1deepGreen\1random IOU\2 buff\nfor \1deepGreen\1you and another\nToon\2.\nCan only be used once\nevery 2 rounds.',
    5: 'Instantly cast a free\1deepGreen\1\n30% Toon-Up unite\2.\nCan only be used once\nevery 3 rounds.',
    # Special gold-dice
    6: 'Grants you \1deepGreen\1access to\nyour Gags\2. Use your\nPips to buy Gags and\ndice to \1deepGreen\1strengthen\nyourself\2!',
}
DiceSpeedchatCast = {
    0: ['One more roll...', 'Try again...', 'Trust me!', 'This will work!'],
    1: ['I won\'t miss this!', 'You can count on me!'],
    2: ['Toons of the World, Spend Wisely!', 'Bargain time!'],
    3: ['We can do this!', 'Teamwork makes the dream work!'],
    4: ['Get ready, {partner}!', 'Look alive, {partner}!'],
    5: 'Toons of the World, Toon-Up!',
    # Special gold-dice
    6: ["I'm ready to rock!", "Bring it on!", "Let's get ready to rumble!", "Let the pies fly!", "Welcome to the danger zone!"],
}
YouAreAFailureCast = ["I CAN'T STOP!!!", "HELP!!! AHHHH!!!!", "Don't you jutht love the THRILL of it?!"]

# How many rerolls do you need before ones are forced?
RerollAddictionForceOneRequirement = 3
MaxRerollCount = 8


def getPipReward(currentGame, isPunished, leftoverSuits, wantExtraPunishment):
    return max({
        HighRollerGameEnum.TRIVIA: [3, 8],
        HighRollerGameEnum.PUZZLE: [8 - (2 * leftoverSuits) - (2 if wantExtraPunishment else 0), 8],
        HighRollerGameEnum.SHUFFLE: [3, 8],
    }[currentGame][int(isPunished)], 0)


def getPipCost(av, track: Union[AttackEnum, int], level: int):
    """
    Gets the ability cost of a move.
    """
    if level == -1:
        # No attack picked.
        return 0

    # Special golden-dice. Always 6 cost.
    if track == AttackEnum.TOON_DICE and level == 6:
        return 6

    discount = 0
    if av:
        effect = av.getStatusEffectOfId(StatusEffectEnum.EFFECT_PIP_DISCOUNT)
        if effect:
            discount = effect.getActiveDiscount()
        else:
            # hack
            if hasattr(av, 'forceShowDiscountLolz'):
                discount = getattr(av, 'forceShowDiscountLolz')

    # Thankfully, pip costs follow this nice formula,
    # even between regular moves and AttackEnum.TOON_DICE.
    return max(0, int(level + 1 - discount))


# Start black suit message
HighRollerSetupBlackSuitName = 'HighRoller-SetupBlackSuit'
