from toontown.chat.ui.speedchat.SCMenu import SCMenu
from toontown.chat.ui.speedchat.SCStaticTextTerminal import SCStaticTextTerminal
from toontown.chat.ui.speedchat.TTSCToontaskTerminal import TTSCToontaskTerminal
from toontown.quest3.base.QuestLine import QuestLine
from toontown.quest3.base.QuestReference import QuestReference


class TTSCToontaskMenu(SCMenu):

    def __init__(self, binLevel=1):
        SCMenu.__init__(self, binLevel=binLevel)
        self.accept('questsChanged', self.__tasksChanged)
        self.__tasksChanged()

    def destroy(self):
        self.ignore('questsChanged')
        SCMenu.destroy(self)

    def __tasksChanged(self):
        self.clearMenu()
        try:
            lt = base.localAvatar
        except:
            return

        phrases = []

        def addTerminal(terminal, self=self, phrases=phrases):
            displayText = terminal.getDisplayText()
            if displayText not in phrases:
                self.append(terminal)
                phrases.append(displayText)

        # Add EVERY POTENTIAL MESSAGE.
        i = 0
        for questReference in lt.getQuestReferences():
            questReference: QuestReference
            for questObjective in QuestLine.dereferenceQuestReference(questReference, quester=lt).getQuestObjectives():
                for msg in questObjective.getSpeedchatMessages(lt, questReference):
                    addTerminal(TTSCToontaskTerminal(msg.replace('  ', ' '), i))
                    i += 1

        needToontask = 1
        if hasattr(lt, 'questCarryLimit'):
            needToontask = len(lt.getQuestReferences()) != lt.questCarryLimit
        if needToontask:
            addTerminal(SCStaticTextTerminal(1299))
        return
