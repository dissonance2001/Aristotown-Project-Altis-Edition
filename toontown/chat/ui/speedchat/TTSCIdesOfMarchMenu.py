from toontown.chat.ui.speedchat.SCMenu import SCMenu
from toontown.chat.ui.speedchat.SCMenuHolder import SCMenuHolder
from toontown.chat.ui.speedchat.SCStaticTextTerminal import SCStaticTextTerminal
from toontown.toonbase import TTLocalizer

IdesOfMarchMenu = [(TTLocalizer.IdesOfMarchMenuSections[0], [30450, 30451, 30452])]


class TTSCIdesOfMarchMenu(SCMenu):

    def __init__(self, binLevel=1):
        SCMenu.__init__(self, binLevel=binLevel)
        self.__messagesChanged()

    def destroy(self):
        SCMenu.destroy(self)

    def clearMenu(self):
        SCMenu.clearMenu(self)

    def __messagesChanged(self):
        self.clearMenu()
        for section in IdesOfMarchMenu:
            if section[0] == -1:
                for phrase in section[1]:
                    if phrase not in TTLocalizer.SpeedChatStaticText:
                        print('warning: tried to link IdesOfMarch phrase %s which does not seem to exist' % phrase)
                        break
                    self.append(SCStaticTextTerminal(phrase))

            else:
                menu = SCMenu(binLevel=self.binLevel + 1)
                for phrase in section[1]:
                    if phrase not in TTLocalizer.SpeedChatStaticText:
                        print('warning: tried to link IdesOfMarch phrase %s which does not seem to exist' % phrase)
                        break
                    menu.append(SCStaticTextTerminal(phrase))

                menuName = str(section[0])
                self.append(SCMenuHolder(menuName, menu))
