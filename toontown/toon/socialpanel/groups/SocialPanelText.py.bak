from direct.gui.OnscreenText import OnscreenText


class ExtendedOnscreenText(OnscreenText):
    def getTextY(self):
        return self.getTextPos()[1]

    def getYScale(self):
        return self.getScale()[1]

    def getLineCount(self):
        return self.textNode.getHeight()

    def _shiftYPosByLineCount(self, lineCount, yScale=None):
        if self['text'] == '' or not lineCount:
            return
        offsetYScale = (yScale or self.getYScale()) / 2.0
        xpos, ypos = self['pos']
        self['pos'] = (xpos, ypos + (offsetYScale * lineCount))

    def setTextWithVerticalAlignment(self, text):
        if self['text'] != '':
            oldLineCount = self.sanity(self.getLineCount()) or 1
        else:
            oldLineCount = 1
        self['text'] = text
        newLineCount = self.sanity(self.getLineCount()) or 1
        self._shiftYPosByLineCount(newLineCount - oldLineCount)

    @staticmethod
    def sanity(value):
        value = round(value, 4)
        if not 0 <= value <= 20:
            return 0
        return value
