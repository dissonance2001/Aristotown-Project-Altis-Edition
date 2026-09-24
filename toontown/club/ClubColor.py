"""
An theme color for your club.
"""
import math
import time

from toontown.toonbase import ProcessGlobals
from toontown.utils.ColorHelper import hexToPCol


class ClubColor:
    """
    Generic container class for Club color.
    """

    def __init__(self, color: str = 'ffffff'):
        self.color = color
        self.decipheredCol = hexToPCol(self.color)
        self.uniqueName = self._makeUniqueName()
        self.updateName = self._makeUpdateName()

    def getColor(self) -> tuple:
        return self.decipheredCol

    """Task methods"""

    def _makeUniqueName(self):
        return f'ClubColor-{self.color}'

    def getUniqueName(self):
        return self.uniqueName

    def canUpdate(self):
        # Does this send messenger calls?
        return False

    def getUpdateName(self):
        return self.updateName

    def _makeUpdateName(self):
        # For messenger calls.
        return f'{self.getUniqueName()}-update'

    def getTaskName(self, taskName: str):
        # For any tasks.
        return f'{self.getUniqueName()}-task-{taskName}'


class ClubColorPulser(ClubColor):
    """
    Given a tuple of colors, we return an interpolated color
    between two different times.

    The colors tuple format is:
    (
        (color, duration),
        (color, duration),
        [...]
    )
    """

    def __init__(self, colors: tuple):
        self.colors = colors
        self.optimizedColors = self.makeOptimizedColors()
        self.duration = sum(color[1] for color in colors)
        super().__init__()

    def getColor(self) -> tuple:
        # Gets the color at this moment in time.
        return self.getColorAtTime(self.getTime())

    def getColorAtTime(self, t, fancy: bool = False):
        colors = self.getColors()

        # Iterate over the colors until we find the tuples we care about.
        for thisTuple, nextTuple in zip(colors, colors[1:]):
            duration = thisTuple[1]
            if (t - duration) < 0:
                # Calculate our color difference.
                return tuple(
                    self.blendTwoValues(colA, colB, t / duration, fancy=fancy)
                    for colA, colB in zip(thisTuple[0], nextTuple[0])
                )
            else:
                # We have not yet made it to the color we're looking for.
                # Reduce the time and move onto the next duration.
                t -= duration

        raise Exception("ClubColorPulser could not find color.")

    def getColorAtPercent(self, x: float):
        # Returns the color at a % through the sequence (x is 0 to 1).
        # We skip the last color in the sequence.
        seconds = x * sum(color[1] for color in self.colors[:-1])
        return self.getColorAtTime(seconds, fancy=True)

    def getColors(self) -> list:
        """Returns a list of the colors to be used during interpolation."""
        return self.optimizedColors

    def makeOptimizedColors(self) -> list:
        """Optimizes the colors."""
        colList = list(self.colors) + [self.colors[0]]
        colList = list(map(lambda t: (hexToPCol(t[0]), t[1]), colList))
        return colList

    @staticmethod
    def blendTwoValues(a, b, t, fancy: bool = False):
        if not fancy:
            return a + ((b - a) * t)
        else:
            # This way is more accurate, but laggy
            return math.sqrt(((1 - t) * (a ** 2)) + (t * (b ** 2)))

    def getTime(self) -> float:
        # Gets the current time.
        return time.time() % self.getDuration()

    def getDuration(self) -> float:
        # Gets the total duration of the pulse sequence.
        return self.duration

    """Task methods"""

    def _makeUniqueName(self):
        uniqueStr = ''
        for color, duration in self.colors:
            uniqueStr = f'{uniqueStr}-{color}/{duration}'
        return 'ClubColorPulser' + uniqueStr

    """Task/Messenger hooks"""

    def canUpdate(self):
        # Does this send messenger calls?
        return True

    def doColorUpdate(self):
        # Update the color.
        updateName = self.getUpdateName()
        if messenger.whoAccepts(updateName):
            messenger.send(updateName, [self.getColor()])


class ClubColorReversePulser(ClubColorPulser):
    """Same as the ColorPulser, but reverses backwards through the colors list as well."""

    def getColors(self) -> list:
        """Returns a list of the colors to be used during interpolation."""
        colorList = list(self.colors)
        secondColorList = list(self.colors)[-2::-1]  # skips the 'last' item, so [1, 2, 3, 4] -> [3, 2, 1]
        return colorList + secondColorList
