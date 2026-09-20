from toontown.chat.ui.speedchat import SCMenuHolder
from toontown.chat.ui.speedchat.SCMenu import SCMenu
from toontown.chat.ui.speedchat.SCStaticTextTerminal import SCStaticTextTerminal
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownGlobals

ZoneToMsgs = {
    ToontownGlobals.LawbotStageIntA: {
        1: [41201, 41501],
        2: [41202, 41502],
        3: [41203, 41503]
    }
}
GLOBAL_MSGS = [1700, 1701, 1702, 1703, 1704]


class TTSCLawficeMenu(SCMenu):

    def __init__(self, binLevel=1):
        SCMenu.__init__(self, binLevel=binLevel)
        self.meetMenuHolder = None
        self.otherHolder = None
        zoneId = base.cr.playGame.getPlaceId()
        if zoneId and zoneId == 12000:
            meetMenu = SCMenu(binLevel=self.binLevel + 1)
            for msgIndex in TTLocalizer.SCFactoryMeetMenuIndexes:
                term = SCStaticTextTerminal(msgIndex)
                meetMenu.append(term)

            self.meetMenuHolder = SCMenuHolder.SCMenuHolder(TTLocalizer.SCMenuFactoryMeet, meetMenu)
            self[0:0] = [self.meetMenuHolder]
        self.accept('factoryZoneChanged', self.__zoneChanged)
        self.__zoneChanged()
        return

    def destroy(self):
        self.ignore('factoryZoneChanged')
        SCMenu.destroy(self)

    def __zoneChanged(self, zoneId=0):
        if self.meetMenuHolder:
            del self[0]
        self.clearMenu()
        phrases = []

        def addTerminal(terminal, self=self, phrases=phrases):
            displayText = terminal.getDisplayText()
            if displayText not in phrases:
                self.append(terminal)
                phrases.append(displayText)

        try:
            lawficeZone = base.cr.playGame.getPlace().getZoneId()
            for msg in GLOBAL_MSGS + ZoneToMsgs.get(lawficeZone, {}).get(zoneId, []):
                addTerminal(SCStaticTextTerminal(msg))
        except:
            for msg in GLOBAL_MSGS + ZoneToMsgs.get(ToontownGlobals.LawbotStageIntA).get(zoneId, []):
                addTerminal(SCStaticTextTerminal(msg))

        if self.meetMenuHolder:
            self[0:0] = [self.meetMenuHolder]
