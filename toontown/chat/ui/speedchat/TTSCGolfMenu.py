from toontown.chat.ui.speedchat.SCMenu import SCMenu
from toontown.chat.ui.speedchat.SCMenuHolder import SCMenuHolder
from toontown.chat.ui.speedchat.SCStaticTextTerminal import SCStaticTextTerminal
from toontown.toonbase import TTLocalizer

GolfMenuGuide = [
    (TTLocalizer.GolfMenuSections[1], [4100, 4101, 4102, 4103, 4104, 4105]),
    (TTLocalizer.GolfMenuSections[2], [4200, 4201, 4202, 4203, 4204, 4205, 4206, 4207]),
    (TTLocalizer.GolfMenuSections[3], [4300, 4301, 4302, 4303, 4304, 4305, 4306, 4307])
]


class TTSCGolfMenu(SCMenu):
    def __init__(self, binLevel=1):
        SCMenu.__init__(self, binLevel=binLevel)
        self.accept('golfMessagesChanged', self.__golfMessagesChanged)
        self.__golfMessagesChanged()

    def destroy(self):
        self.ignore('golfMessagesChanged')
        SCMenu.destroy(self)

    def __golfMessagesChanged(self):
        self.clearMenu()

        for section in GolfMenuGuide:
            if section[0] == -1:
                for phrase in section[1]:
                    if phrase not in TTLocalizer.SpeedChatStaticText:
                        print('warning: tried to link golf phrase %s which does not seem to exist' % phrase)
                        break
                    self.append(SCStaticTextTerminal(phrase))

            else:
                menu = SCMenu(binLevel=self.binLevel + 1)
                for phrase in section[1]:
                    if phrase not in TTLocalizer.SpeedChatStaticText:
                        print('warning: tried to link golf phrase %s which does not seem to exist' % phrase)
                        break
                    menu.append(SCStaticTextTerminal(phrase))

                menuName = str(section[0])
                self.append(SCMenuHolder(menuName, menu))
