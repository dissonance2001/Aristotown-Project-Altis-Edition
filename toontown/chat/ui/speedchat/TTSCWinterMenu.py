from toontown.chat.ui.speedchat.SCMenu import SCMenu
from toontown.chat.ui.speedchat.SCMenuHolder import SCMenuHolder
from toontown.chat.ui.speedchat.SCStaticTextTerminal import SCStaticTextTerminal
from toontown.chat.ui.speedchat.TTSCIndexedTerminal import TTSCIndexedTerminal
from toontown.toonbase import TTLocalizer

WinterMenu = [
    (TTLocalizer.WinterMenuSections[0], {
        30220: 30220,
        30221: 30221,
        30222: 30222,
        30223: 30223,
        30224: 30224,
        30225: 30225,
        30226: 30226,
        30227: 30227
    }),
    (TTLocalizer.WinterMenuSections[1], {
        30278: 30278,
        30279: 30279,
        30280: 30280,
        30281: 30281,
        30282: 30282,
        30283: 30283,
        30284: 30284,
        30285: 30285,
        30275: 30275,
        30276: 30276,
        30277: 30277
    })
]


class TTSCWinterMenu(SCMenu):

    def __init__(self, carol, binLevel=1):
        SCMenu.__init__(self, binLevel=binLevel)
        self.__messagesChanged(carol)

    def destroy(self):
        SCMenu.destroy(self)

    def clearMenu(self):
        SCMenu.clearMenu(self)

    def __messagesChanged(self, carol):
        self.clearMenu()
        winterMenu = []
        if carol:
            winterMenu.append(WinterMenu[0])
        winterMenu.append(WinterMenu[1])
        for section in winterMenu:
            if section[0] == -1:
                for phrase in section[1]:
                    if phrase not in TTLocalizer.SpeedChatStaticText:
                        print('warning: tried to link Winter phrase %s which does not seem to exist' % phrase)
                        break
                    self.append(SCStaticTextTerminal(phrase))

            else:
                menu = SCMenu(binLevel = self.binLevel + 1)
                for phrase in list(section[1].keys()):
                    blatherTxt = section[1][phrase]
                    if blatherTxt not in TTLocalizer.SpeedChatStaticText:
                        print('warning: tried to link Winter phrase %s which does not seem to exist' % phrase)
                        break
                    menu.append(TTSCIndexedTerminal(TTLocalizer.SpeedChatStaticText.get(phrase, None), blatherTxt))

                menuName = str(section[0])
                self.append(SCMenuHolder(menuName, menu))

        return
