from toontown.chat.ui.speedchat.SCElement import SCElement
from toontown.chat.ui.speedchat.SCTerminal import SCTerminal


class SCUnselectableTextTerminal(SCTerminal):
    """
    Currently unused.

    A Speedchat terminal that is not selectable and is only used to display a string of text.
    """
    def __init__(self, text):
        SCTerminal.__init__(self)
        self.text = text

    def handleSelect(self):
        return

    def handleThreeSelect(self):
        return

    def isDisabled(self):
        return True

    def onMouseClick(self, event):
        return

    def onMouseThreeClick(self, event):
        return

    def finalize(self, dbArgs={}):
        if not self.isDirty():
            return
        args = {}
        args.update({'rolloverColor': (0, 0, 0, 0),
                     'pressedColor': (0, 0, 0, 0),
                     'rolloverSound': None,
                     'clickSound': None,
                     'text_fg': (0, 0, 0, 1)})
        args.update(dbArgs)
        SCElement.finalize(self, dbArgs=args)
