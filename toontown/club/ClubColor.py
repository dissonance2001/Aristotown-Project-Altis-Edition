# -*- coding: utf-8 -*-
"""Python 2 compatible animated Club colours for Project Altis.

This is a lightweight port of Corporate Clash's ClubColor/ClubColorPulser
classes.  Colours use wall-clock time, so every GUI displaying the same Club
colour remains synchronized without storing animation state in Astron.
"""

import math
import time

try:
    xrange
except NameError:
    xrange = range


def _hexToColor(value):
    value = str(value or 'ffffff').strip().lstrip('#')
    if len(value) == 3:
        value = ''.join(character * 2 for character in value)
    if len(value) != 6:
        value = 'ffffff'
    try:
        red = int(value[0:2], 16) / 255.0
        green = int(value[2:4], 16) / 255.0
        blue = int(value[4:6], 16) / 255.0
    except (TypeError, ValueError):
        red, green, blue = 1.0, 1.0, 1.0
    return (red, green, blue, 1.0)


class ClubColor(object):
    """Static Club colour container."""

    def __init__(self, color='ffffff'):
        self.color = str(color)
        self.decipheredCol = _hexToColor(self.color)

    def getColor(self):
        return self.decipheredCol

    def canUpdate(self):
        return False


class ClubColorPulser(ClubColor):
    """Smoothly interpolates through a sequence of hexadecimal colours.

    ``colors`` is a tuple in the Corporate Clash format::

        (('eb4d4d', 2.0), ('eb8f4d', 2.0), ...)

    Each duration controls the transition from that colour to the next one.
    The final colour transitions back to the first colour.
    """

    def __init__(self, colors):
        self.colors = tuple(colors or ())
        if not self.colors:
            self.colors = (('ffffff', 1.0),)
        self.optimizedColors = self._makeOptimizedColors()
        self.duration = sum(max(0.0001, float(entry[1])) for entry in self.colors)
        ClubColor.__init__(self, self.colors[0][0])

    def _makeOptimizedColors(self):
        colorList = list(self.colors) + [self.colors[0]]
        return [(_hexToColor(entry[0]), max(0.0001, float(entry[1])))
                for entry in colorList]

    def getDuration(self):
        return self.duration

    def getTime(self):
        return time.time() % self.getDuration()

    def getColor(self):
        return self.getColorAtTime(self.getTime())

    def getColorAtTime(self, currentTime, fancy=False):
        currentTime = float(currentTime) % self.getDuration()
        colors = self.optimizedColors
        for index in range(len(colors) - 1):
            thisColor, duration = colors[index]
            nextColor = colors[index + 1][0]
            if currentTime < duration:
                amount = currentTime / duration
                return tuple(self._blendTwoValues(a, b, amount, fancy)
                             for a, b in zip(thisColor, nextColor))
            currentTime -= duration
        return colors[0][0]

    def getColorAtPercent(self, percent):
        percent = min(1.0, max(0.0, float(percent)))
        return self.getColorAtTime(percent * self.getDuration(), fancy=True)

    @staticmethod
    def _blendTwoValues(a, b, amount, fancy=False):
        if fancy:
            return math.sqrt(((1.0 - amount) * (a ** 2)) +
                             (amount * (b ** 2)))
        return a + ((b - a) * amount)

    def canUpdate(self):
        return True
