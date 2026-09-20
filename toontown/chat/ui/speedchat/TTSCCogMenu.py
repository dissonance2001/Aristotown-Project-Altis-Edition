from toontown.chat.ui.speedchat.SCMenu import SCMenu
from toontown.chat.ui.speedchat.SCStaticTextTerminal import SCStaticTextTerminal


class TTSCCogMenu(SCMenu):
    def __init__(self, indices, binLevel=1):
        SCMenu.__init__(self, binLevel=binLevel)
        for index in indices:
            term = SCStaticTextTerminal(index)
            self.append(term)
