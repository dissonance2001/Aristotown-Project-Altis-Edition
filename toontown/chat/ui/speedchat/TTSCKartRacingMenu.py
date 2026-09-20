from toontown.chat.ui.speedchat.SCMenu import SCMenu
from toontown.chat.ui.speedchat.SCMenuHolder import SCMenuHolder
from toontown.chat.ui.speedchat.SCStaticTextTerminal import SCStaticTextTerminal
from toontown.toonbase import TTLocalizer

KartRacingMenuGuide = [
    (TTLocalizer.KartRacingMenuSections[1], [3130, 3160, 3190, 3170, 3180, 3150, 3110]),
    (TTLocalizer.KartRacingMenuSections[2], [3200, 3201, 3210, 3211, 3220, 3221, 3222, 3223, 3224, 3225, 3230, 3231, 3232, 3233, 3234, 3235]),
    (TTLocalizer.KartRacingMenuSections[3], [3600, 3601, 3602, 3603, 3640, 3641, 3642, 3643, 3660, 3661, 3662, 3663]),
    (TTLocalizer.KartRacingMenuSections[4], [3300, 3301, 3310, 3320, 3330, 3340, 3350, 3360]),
    (TTLocalizer.KartRacingMenuSections[5], [3410, 3400, 3430, 3450, 3451, 3452, 3453, 3460, 3461, 3462, 3470]),
    (TTLocalizer.KartRacingMenuSections[0], [3010, 3020, 3030, 3040, 3050, 3060, 3061])
]


class TTSCKartRacingMenu(SCMenu):

    def __init__(self, binLevel=1):
        SCMenu.__init__(self, binLevel=binLevel)
        self.accept('kartRacingMessagesChanged', self.__kartRacingMessagesChanged)
        self.__kartRacingMessagesChanged()

    def destroy(self):
        self.ignore('kartRacingMessagesChanged')
        SCMenu.destroy(self)

    def clearMenu(self):
        SCMenu.clearMenu(self)

    def __kartRacingMessagesChanged(self):
        self.clearMenu()
        for section in KartRacingMenuGuide:
            if section[0] == -1:
                for phrase in section[1]:
                    if phrase not in TTLocalizer.SpeedChatStaticText:
                        print('warning: tried to link kart phrase %s which does not seem to exist' % phrase)
                        break
                    self.append(SCStaticTextTerminal(phrase))

            else:
                menu = SCMenu(binLevel=self.binLevel + 1)
                for phrase in section[1]:
                    if phrase not in TTLocalizer.SpeedChatStaticText:
                        print('warning: tried to link kart phrase %s which does not seem to exist' % phrase)
                        break
                    menu.append(SCStaticTextTerminal(phrase))

                menuName = str(section[0])
                self.append(SCMenuHolder(menuName, menu))
