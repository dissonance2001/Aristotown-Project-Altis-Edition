from toontown.chat.ui.speedchat.SCTerminal import SCTerminal

TTSCIndexedMsgEvent = 'SCIndexedMsg'


class TTSCIndexedTerminal(SCTerminal):

    def __init__(self, msg, msgIndex):
        SCTerminal.__init__(self)
        self.text = msg
        self.msgIndex = msgIndex

    def handleSelect(self):
        SCTerminal.handleSelect(self)
        messenger.send(self.getEventName(TTSCIndexedMsgEvent), [self.msgIndex, self.linkedEmote, False])
