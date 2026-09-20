from toontown.chat.ui.speedchat.SCTerminal import SCTerminal

TTSCToontaskMsgEvent = 'SCToontaskMsg'


class TTSCToontaskTerminal(SCTerminal):

    def __init__(self, msg, msgIndex):
        SCTerminal.__init__(self)
        self.msg = msg
        self.msgIndex = msgIndex

    def getDisplayText(self):
        return self.msg

    def handleSelect(self):
        SCTerminal.handleSelect(self)
        messenger.send(self.getEventName(TTSCToontaskMsgEvent), [self.msgIndex])

    def handleThreeSelect(self):
        self.handleSelect()  # Default to handleSelect(). Done to avoid task spamming or glitches between zones
