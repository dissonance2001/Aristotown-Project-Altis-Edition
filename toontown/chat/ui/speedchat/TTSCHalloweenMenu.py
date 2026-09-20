from toontown.chat.ui.speedchat.SCMenu import SCMenu
from toontown.chat.ui.speedchat.SCMenuHolder import SCMenuHolder
from toontown.chat.ui.speedchat.SCStaticTextTerminal import SCStaticTextTerminal
from toontown.toonbase import TTLocalizer

# NOTE: 30255 is not relevant for 2023 Halloween and has been removed
HalloweenMenu = [(TTLocalizer.HalloweenMenuSections[0], [30250, 30251, 30252, 30253, 30254, 30256])]


class TTSCHalloweenMenu(SCMenu):
    def __init__(self, binLevel=1):
        SCMenu.__init__(self, binLevel=binLevel)
        self.__messagesChanged()

    def destroy(self):
        SCMenu.destroy(self)

    def clearMenu(self):
        SCMenu.clearMenu(self)

    def __messagesChanged(self):
        self.clearMenu()

        for section in HalloweenMenu:
            if section[0] == -1:
                for phrase in section[1]:
                    if phrase not in TTLocalizer.SpeedChatStaticText:
                        print('warning: tried to link Halloween phrase %s which does not seem to exist' % phrase)
                        break
                    self.append(SCStaticTextTerminal(phrase))

            else:
                menu = SCMenu(binLevel=self.binLevel + 1)
                for phrase in section[1]:
                    if phrase not in TTLocalizer.SpeedChatStaticText:
                        print('warning: tried to link Halloween phrase %s which does not seem to exist' % phrase)
                        break
                    menu.append(SCStaticTextTerminal(phrase))

                menuName = str(section[0])
                self.append(SCMenuHolder(menuName, menu))
