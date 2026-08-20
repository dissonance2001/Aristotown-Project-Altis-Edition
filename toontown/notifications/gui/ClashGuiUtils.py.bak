from direct.gui.DirectGui import OnscreenText


def kwargsToOptionDefs(**kwargs):
    """Python 2-compatible copy of Clash's kwargsToOptionDefs helper."""
    optionDefs = []
    for key, value in kwargs.items():
        if type(value) is not list:
            optionDefs.append((key, value, None))
        else:
            value, callback = value
            optionDefs.append((key, value, callback))
    return tuple(optionDefs)


class ExtendedOnscreenText(OnscreenText):
    """The exact vertical-alignment behavior used by Clash notifications."""

    def getTextY(self):
        return self.getTextPos()[1]

    def getYScale(self):
        return self.getScale()[1]

    def getLineCount(self):
        return self.textNode.getHeight()

    def _shiftYPosByLineCount(self, lineCount, yScale=None):
        if self['text'] == '':
            return
        if not lineCount:
            return
        offsetYScale = (yScale or self.getYScale()) / 2.0
        xPos, yPos = self['pos']
        self['pos'] = (xPos, yPos + (offsetYScale * lineCount))

    def setTextWithVerticalAlignment(self, text):
        if self['text'] != '':
            oldLineCount = self.sanity(self.getLineCount()) or 1
        else:
            oldLineCount = 1
        self['text'] = text
        newLineCount = self.getLineCount()
        self._shiftYPosByLineCount(newLineCount - oldLineCount)

    def multPos(self, x_mult=1.0, y_mult=1.0):
        xPos, yPos = self.getPos()
        self.setPos(xPos * x_mult, yPos * y_mult)

    @staticmethod
    def sanity(value):
        value = round(value, 4)
        if not 0 <= value <= 20:
            return 0
        return value
