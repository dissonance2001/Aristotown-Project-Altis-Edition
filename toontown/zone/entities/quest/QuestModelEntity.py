from toontown.level.ModelEntity import ModelEntity
from toontown.level.editor import EditorGlobals
from toontown.zone.entities.quest.QuestEntityBase import QuestCutsceneEntityBase
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory(debug=True)
class QuestModelEntity(QuestCutsceneEntityBase, ModelEntity):
    def __init__(self, level, entId):
        QuestCutsceneEntityBase.__init__(self, level, entId)
        ModelEntity.__init__(self, level, entId)

    def loadModel(self):
        # Make sure wantedQuest is in QuestId format
        self.callSetters('wantedQuest')
        hasHistory = self.localAvHasQuestHistory()
        hasFurtherQuest = self.localAvHasFurtherQuest()
        if self.hideCondition == 'finishedQuest' and (hasHistory or hasFurtherQuest):
            # We've finished the quest and we want to hide if we have finished it.
            self.stash()
        elif self.hideCondition == 'unfinishedQuest' and not (hasHistory or hasFurtherQuest):
            # We haven't finished the quest and we want to hide if we haven't finished it.
            self.stash()
        else:
            self.unstash()

        ModelEntity.loadModel(self)

    if EditorGlobals.wantLevelEditor():
        def setHideCondition(self, hideCondition):
            self.hideCondition = hideCondition
            self.loadModel()
