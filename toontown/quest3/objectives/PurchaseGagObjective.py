from toontown.quest3.base.QuestObjective import *
from toontown.quest3.context.PurchaseGagContext import PurchaseGagContext
from toontown.quest3.QuestLocalizer import AtTheGagShop, HL_Purchase, OBJ_PurchaseGag, QuestProgress_Complete, SC_Gags, \
    PROG_Times
from toontown.clashbattle.battle.BattleGlobals import AvPropsNew


class PurchaseGagObjective(QuestObjective):
    """
    A quest where you must purchase gags.
    """

    def __init__(self,
                 npc=2001,
                 rewards=None,
                 nextStep=None,
                 npcReturnable: bool = True):
        super().__init__(npc=npc, rewards=rewards, nextStep=nextStep, npcReturnable=npcReturnable)

    def calculateProgress(self, context: QuestContext, questReference: QuestReference, quester: Quester) -> int:
        return type(context) is PurchaseGagContext

    def modifyPoster(self, questReference: QuestReference, poster):
        complete = questReference.isQuestComplete(base.localAvatar, self.objectiveIndex)
        searchPoster = poster.CENTER if not (complete and self.npcReturnable) else poster.LEFT

        poster.visual_setFrameColor(searchPoster, 'lightBlue')
        poster.visual_setFrameText(searchPoster, "Purchase a Gag")
        
        invModel = loader.loadModel('phase_3.5/models/gui/inventory_icons')
        track = random.randint(0, 7)
        level = random.randint(0, 7)
        lIconGeom = invModel.find('**/' + AvPropsNew[track][level])
        poster.visual_setFrameGeom(searchPoster, geom=lIconGeom)
        invModel.removeNode()

        # If we're complete, bonus info
        if complete:
            if self.npcReturnable:
                poster.visual_setFrameColor(poster.RIGHT, 'lightBlue')
                poster.visual_setNpcFrame(poster.RIGHT, self.getToNpcId())
                poster.visual_setFrameText(poster.RIGHT, self.getToNpcName())
                poster.label_auxillaryText.show()

    def getInfoTextStrings(self, questReference: QuestReference) -> tuple:
        # If we're complete and demand NPC completion, point to NPC instead
        if questReference.isQuestComplete(base.localAvatar, self.objectiveIndex) and self.npcReturnable:
            return super().getInfoTextStrings(questReference)

        return AtTheGagShop,

    def getSpeedchatMessages(self, quester, questReference: QuestReference) -> tuple:
        if questReference.isQuestComplete(quester, self.objectiveIndex):
            return tuple()
        return SC_Gags,

    def getHeadline(self, questReference: QuestReference, objectiveSelected: int = 0) -> str:
        return HL_Purchase
    
    def getObjectiveGoal(self) -> str:
        return OBJ_PurchaseGag

    def getProgressFormat(self, questReference):
        return questReference.getQuestProgress(self.objectiveIndex), 1, PROG_Times

    def getProgressString(self, questReference: QuestReference, progress: int) -> str:
        if questReference.isQuestComplete(base.localAvatar, self.objectiveIndex):
            return QuestProgress_Complete
        return ''

    def __repr__(self):
        return f'PurchaseGagObjective({self._getKwargStr()[:-2]})'
