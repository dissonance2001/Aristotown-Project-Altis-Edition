from toontown.quest3.base.QuestReference import QuestReference
from toontown.quest3.gui.Quest3Poster import QuestPoster


class SidequestPoster(QuestPoster):

    def __init__(self, parent, questReference: QuestReference = None, **kw):
        # GUI boilerplate.
        posterModel = loader.loadModel('phase_3.5/models/gui/quests/ttcc_quest_posters')
        optiondefs = (('image', posterModel.find('**/side_task_scroll'), None),)
        self.defineoptions(kw, optiondefs)
        super().__init__(parent, questReference, **kw)
        self.initialiseoptions(SidequestPoster)

    def performPosterModification(self, questObjective, questReference):
        """We set the poster with stuff ourselves."""
        self.visual_setNpcFrame(self.CENTER, questObjective.getFromNpcId())
        self.visual_setFrameColor(self.CENTER, 'brown')
        self.visual_setFrameText(self.CENTER, questObjective.getFromNpcName())
        infoStrings = [
            questObjective.getFromNpcBuildingName(),
            questObjective.getFromNpcStreetName(),
            questObjective.getFromNpcLocationName(),
        ]
        if infoStrings[0] == infoStrings[2]:
            infoStrings.pop()
        self.text_questInfo.setTextWithVerticalAlignment('\n'.join(infoStrings))

    def updateObjectiveButtonStatus(self):
        self.button_objectiveLeft.hide()
        self.button_objectiveRight.hide()

    def isComplete(self):
        if not self.questReference:
            return False
        return base.localAvatar.hasCompletedQuest(self.questReference.getQuestSource(), self.questReference.getChainId()) \
               or self.questReference.isQuestComplete(base.localAvatar, self.objectiveSelected)

    def canShowSteps(self, questLength, isComplete):
        # Do not show steps if this poster is completed
        return questLength > 1 and not isComplete
