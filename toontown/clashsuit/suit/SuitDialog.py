import random
from toontown.utils.DirectNotifyCategory import getNotify
from toontown.toonbase import TTLocalizer

# Centralize everything a suit can say
# import this file
# Then call SuitDialog.requestBattle.get() to get the next dialog in the list

notify = getNotify('SuitDialog')


def getBrushOffIndex(suitName):
    """
    Chooses a suitable brushoff for a suit of the given type, and
    returns its index number (which can later be passed to
    getBrushOffText() to retrieve the message itself).
    """
    if suitName in SuitBrushOffs:
        brushoffs = SuitBrushOffs[suitName]
    else:
        brushoffs = SuitBrushOffs[None]
    return random.randrange(len(brushoffs))


def getBrushOffText(suitName, index):
    """
    Returns the text of the brushoff with the given index number for
    the given suit type.
    """
    if suitName in SuitBrushOffs:
        brushoffs = SuitBrushOffs[suitName]
    else:
        brushoffs = SuitBrushOffs[None]
    return brushoffs[index]


SuitBrushOffs = TTLocalizer.SuitBrushOffs
