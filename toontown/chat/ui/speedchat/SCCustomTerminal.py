from toontown.chat.ui.speedchat.SCTerminal import SCTerminal
from toontown.toonbase.TTLocalizer import CustomSCStrings

SCCustomMsgEvent = 'SCCustomMsg'


class SCCustomTerminal(SCTerminal):
    def __init__(self, textId):
        SCTerminal.__init__(self)
        self.textId = textId
        self.text = CustomSCStrings[self.textId]

    def handleSelect(self):
        SCTerminal.handleSelect(self)
        messenger.send(self.getEventName(SCCustomMsgEvent), [self.textId, self.linkedEmote, False])

    def handleThreeSelect(self):
        SCTerminal.handleThreeSelect(self)
        messenger.send(self.getEventName(SCCustomMsgEvent), [self.textId, self.linkedEmote, True])
