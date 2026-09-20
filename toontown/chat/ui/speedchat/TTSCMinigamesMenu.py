from toontown.chat.ui.speedchat.SCMenu import SCMenu
from toontown.chat.ui.speedchat.SCMenuHolder import SCMenuHolder
from toontown.chat.ui.speedchat.SCStaticTextTerminal import SCStaticTextTerminal
from toontown.chat.ui.speedchat.TTSCGolfMenu import TTSCGolfMenu
from toontown.toonbase import TTLocalizer

MinigameMenuGuide = [
    (TTLocalizer.MinigameMenuSections[5], [4800, 4801, 4802, 4803, 4804, 4805, 4806, 4807, 4808, 4809, 4810]),  # general
    (TTLocalizer.MinigameMenuSections[1], [4400, 4401, 4402]),  # checkers
    (TTLocalizer.MinigameMenuSections[2], [4500, 4501, 4502, 4503]),  # chess
    (TTLocalizer.MinigameMenuSections[3], [4600, 4601, 4602]),  # tuno
    (TTLocalizer.MinigameMenuSections[4], []),  # golf (generates a golf menu)
    (TTLocalizer.MinigameMenuSections[0], [4000, 4700, 4701, 4702, 1111, 4001])
]


class TTSCMinigameMenu(SCMenu):

    def __init__(self, binLevel=1):
        SCMenu.__init__(self, binLevel=binLevel)
        self.accept('minigameMessagesChanged', self.__minigameMessagesChanged)
        self.__minigameMessagesChanged()
        submenus = []

    def destroy(self):
        self.ignore('minigameMessagesChanged')
        SCMenu.destroy(self)

    def clearMenu(self):
        SCMenu.clearMenu(self)

    def __minigameMessagesChanged(self):
        self.clearMenu()
        for section in MinigameMenuGuide:
            if section[0] == -1:
                for phrase in section[1]:
                    if phrase not in TTLocalizer.SpeedChatStaticText:
                        print('warning: tried to link golf phrase %s which does not seem to exist' % phrase)
                        break
                    self.append(SCStaticTextTerminal(phrase))
            else:
                # link the golf menu instead if we find that
                binLevel = self.binLevel + 1
                menu = SCMenu(binLevel=binLevel) if section[0] != 'GOLF' else TTSCGolfMenu(binLevel=binLevel)
                for phrase in section[1]:
                    if phrase not in TTLocalizer.SpeedChatStaticText:
                        print('warning: tried to link golf phrase %s which does not seem to exist' % phrase)
                        break
                    menu.append(SCStaticTextTerminal(phrase))

                menuName = str(section[0])
                self.append(SCMenuHolder(menuName, menu))
