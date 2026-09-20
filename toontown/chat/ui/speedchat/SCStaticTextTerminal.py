from toontown.chat.ui.speedchat.SCTerminal import SCTerminal
from toontown.toonbase import TTLocalizer

SCStaticTextMsgEvent = 'SCStaticTextMsg'


class SCStaticTextTerminal(SCTerminal):

    def __init__(self, textId):
        SCTerminal.__init__(self)
        self.textId = textId
        self.text = TTLocalizer.SpeedChatStaticText[self.textId]

    def handleSelect(self):
        SCTerminal.handleSelect(self)
        messenger.send(self.getEventName(SCStaticTextMsgEvent), [self.textId, self.linkedEmote, False])

    def handleThreeSelect(self):
        SCTerminal.handleThreeSelect(self)
        messenger.send(self.getEventName(SCStaticTextMsgEvent), [self.textId, self.linkedEmote, True])
