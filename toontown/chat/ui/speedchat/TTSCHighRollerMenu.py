from toontown.chat.ui.speedchat.SCMenu import SCMenu
from toontown.chat.ui.speedchat.SCMenuHolder import SCMenuHolder
from toontown.chat.ui.speedchat.SCStaticTextTerminal import SCStaticTextTerminal
from toontown.toonbase import TTLocalizer

HighRollerMenu = {
    1: [
        (TTLocalizer.HighRollerMenuSections[0], [30606, 30607, 30608, 30609]),
        (TTLocalizer.HighRollerMenuSections[1], [30610, 30611, 30612, 30613]),
        (TTLocalizer.HighRollerMenuSections[2], [30600, 30601, 30602, 30603, 30604]),
    ],
    2: [
        (TTLocalizer.HighRollerMenuSections[0], [30614, 30615, 30616, 30617, 30618, 30619, 30620, 30621, 30622]),
        (TTLocalizer.HighRollerMenuSections[1], [30623, 30624, 30625, 30626, 30627, 30628, 30629, 30630, 30631]),
        (TTLocalizer.HighRollerMenuSections[2], [30600, 30601, 30602, 30603, 30604, 30605]),
    ],
}

class TTSCHighRollerMenu(SCMenu):
    def __init__(self, binLevel=1):
        SCMenu.__init__(self, binLevel=binLevel)
        self.accept('highRollerPhaseChanged', self.__phaseChanged)
        self.__phaseChanged()

    def destroy(self):
        self.ignore('highRollerPhaseChanged')
        SCMenu.destroy(self)

    def __phaseChanged(self, phase=1):
        if phase not in HighRollerMenu:
            print('warning: tried to change to a High Roller phase menu %s which does not seem to exist' % str(phase))
            return

        self.clearMenu()

        for section in HighRollerMenu[phase]:
            menu = SCMenu(binLevel=self.binLevel + 1)
            menuName = str(section[0])
            for phrase in section[1]:
                if phrase not in TTLocalizer.SpeedChatStaticText:  # First we can validate the phrase
                    print('warning: tried to link High Roller phrase %s which does not seem to exist' % phrase)
                    continue

                if section[0] == -1:
                    self.append(SCStaticTextTerminal(phrase))
                else:
                    menu.append(SCStaticTextTerminal(phrase))
            if len(menu):
                self.append(SCMenuHolder(menuName, menu))
