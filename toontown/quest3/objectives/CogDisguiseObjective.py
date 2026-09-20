from toontown.quest3.base.QuestObjective import *
from toontown.quest3.context.NPCInteractContext import NPCInteractContext
from toontown.quest3.objectives import VisitObjective
from toontown.quest3.QuestLocalizer import (AuxillaryText_For, HL_Disguise, OBJ_Assemble, QuestProgress_Complete,
                                            SC_CogDisguise, PROG_Assembled)


class CogDisguiseObjective(VisitObjective):

    # TODO - move the local imports out after the quest2->quest3 conversion
    #  there's no harm in moving them out, i just couldn't run the conversion file without it  - main

    suitIndexToString = {
        0: TTLocalizer.Boardbot,
        1: TTLocalizer.Bossbot,
        2: TTLocalizer.Lawbot,
        3: TTLocalizer.Cashbot,
        4: TTLocalizer.Sellbot
    }

    def __init__(self,
                 npc = 2001,
                 rewards=None,
                 nextStep=None,
                 npcReturnable: bool = True,
                 dept: int = None):
        super().__init__(npc=npc, rewards=rewards, nextStep=nextStep, npcReturnable=npcReturnable)
        self.dept = dept

    def calculateProgress(self, context: NPCInteractContext, questReference: QuestReference, quester: Quester) -> int:
        result = super().calculateProgress(context, questReference, quester)
        if result:
            from toontown.coghq import CogDisguiseGlobals
            return CogDisguiseGlobals.isSuitComplete(context.av.cogParts, self.dept)

        return 0

    def modifyPoster(self, questReference: QuestReference, poster):
        bookModel = loader.loadModel('phase_3.5/models/gui/stickerbook_gui')
        lIconGeom = bookModel.find('**/CogArmIcon2')
        poster.visual_setFrameGeom(poster.LEFT, geom=lIconGeom, scale=0.11, pos=(0, 10, -0.01))
        poster.visual_setFrameColor(poster.LEFT, 'red')
        poster.visual_setFrameText(poster.LEFT, OBJ_Assemble % self.suitIndexToString[self.dept])

        poster.visual_setNpcFrame(poster.RIGHT, self.getToNpcId())
        poster.visual_setFrameColor(poster.RIGHT, 'red')
        poster.visual_setFrameText(poster.RIGHT, self.getToNpcName())

        poster.visual_setAuxText(AuxillaryText_For)
        poster.label_auxillaryText.show()

        bookModel.removeNode()

    def getSpeedchatMessages(self, quester, questReference: QuestReference) -> tuple:
        if questReference.isQuestComplete(quester, self.objectiveIndex):
            return tuple()
        return tuple([SC_CogDisguise % self.suitIndexToString[self.dept]] + list(self.getFinishToontaskStrings()))

    def getHeadline(self, questReference: QuestReference, objectiveSelected: int = 0) -> str:
        return HL_Disguise
    
    def isComplete(self, questReference: QuestReference, objectiveIndex: int, quester: Quester) -> bool:
        from toontown.coghq import CogDisguiseGlobals
        return CogDisguiseGlobals.isSuitComplete(quester.cogParts, self.dept)
    
    def getObjectiveGoal(self) -> str:
        from toontown.clashsuit.suit import SuitDNA
        deptStr = self.suitIndexToString[self.dept]
        return OBJ_Assemble % f'{SuitDNA.getDeptTextGraphic(ToontownGlobals.cogIndex2dept[self.dept])}{deptStr}'

    def getProgressFormat(self, questReference):
        return questReference.getQuestProgress(self.objectiveIndex), 1, PROG_Assembled

    def getProgressString(self, questReference: QuestReference, progress: int) -> str:
        return PROG_Assembled.format(value=progress, range=1)

    def _getKwargStr(self):
        kwargstr = super()._getKwargStr()
        kwargstr += f'dept={self.dept}, '
        return kwargstr

    def __repr__(self):
        return f'CogDisguiseObjective({self._getKwargStr()[:-2]})'
