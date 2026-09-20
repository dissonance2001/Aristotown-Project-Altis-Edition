from toontown.chat.ui.speedchat.SCMenu import SCMenu
from toontown.chat.ui.speedchat.SCMenuHolder import SCMenuHolder
from toontown.chat.ui.speedchat.SCStaticTextTerminal import SCStaticTextTerminal
from toontown.toonbase import TTLocalizer

AprilToonsMenu = [
    (TTLocalizer.AprilToonsMenuSections[1], [30100, 30101, 30102, 30103, 30104, 30105, 30106]),
    (TTLocalizer.AprilToonsMenuSections[2], [30107, 30108, 30109, 30110, 30111, 30112, 30113, 30114]),
    (TTLocalizer.AprilToonsMenuSections[3], [30115, 30116, 30117]),
    (TTLocalizer.AprilToonsMenuSections[0], [30118, 30119, 30120, 30121])
]


class TTSCAprilToonsMenu(SCMenu):
    def __init__(self, binLevel=1):
        SCMenu.__init__(self, binLevel=binLevel)
        self.__aprilToonsMessagesChanged()

    def __aprilToonsMessagesChanged(self):
        self.clearMenu()

        for section in AprilToonsMenu:
            menu = SCMenu(binLevel=self.binLevel + 1)
            menuName = str(section[0])
            for phrase in section[1]:
                if phrase not in TTLocalizer.SpeedChatStaticText:  # First we can validate the phrase
                    print('warning: tried to link April Toons phrase %s which does not seem to exist' % phrase)
                    continue

                if section[0] == -1:
                    self.append(SCStaticTextTerminal(phrase))
                else:
                    menu.append(SCStaticTextTerminal(phrase))
            if len(menu):
                self.append(SCMenuHolder(menuName, menu))
