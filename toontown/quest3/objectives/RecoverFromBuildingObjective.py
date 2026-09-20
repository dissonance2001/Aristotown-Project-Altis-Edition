from toontown.quest3.base.QuestObjective import *
from toontown.quest3.context.BuildingContext import BuildingContext
from toontown.quest3.objectives import BuildingObjective
from toontown.quest3.QuestEnums import QuestItemName
from toontown.quest3.QuestLocalizer import (AuxillaryText_Complete,
                                            AuxillaryText_From, HL_Recover, OBJ_Recover,
                                            PROG_Recover, QuestItemNames, QuestProgress_Complete,
                                            SC_RecoverCogs, itemTuple2Word, PFX_RECOVER)


class RecoverFromBuildingObjective(BuildingObjective):

    def __init__(self,
                 npc = 2001,
                 rewards=None,
                 nextStep=None,
                 npcReturnable: bool = True,
                 zoneUnlocks=None,
                 buildingLocation: int = None,
                 cogTrack: str = None,
                 floorMinimum: int = 1,
                 buildingCount: int = 1,
                 recoverItem: QuestItemName = QuestItemName.LaughingGas,
                 recoverChance: float = 0.8,
                 recoverRequired: int = 1,
                 *args, **kwargs):
        super().__init__(npc=npc, rewards=rewards, nextStep=nextStep, npcReturnable=npcReturnable, zoneUnlocks=zoneUnlocks,
                         cogTrack=cogTrack, floorMinimum=floorMinimum, buildingLocation=buildingLocation,
                         buildingCount=buildingCount)
        self.recoverItem = recoverItem
        self.recoverChance = recoverChance
        self.recoverRequired = recoverRequired

    def calculateProgress(self, context: BuildingContext, questReference: QuestReference, quester: Quester) -> int:
        result = super().calculateProgress(context, questReference, quester)

        # If the building counts, roll the recovery chance.
        if result:
            return random.random() <= self.recoverChance
        return 0

    @staticmethod
    def getDifficultyRange(questerType: QuesterType, questSource: QuestSource, **extraArgs):
        return None

    def getCompletionRequirement(self) -> int:
        return self.recoverRequired

    def modifyPoster(self, questReference: QuestReference, poster):
        complete = questReference.isQuestComplete(base.localAvatar, self.objectiveIndex)

        # Set item posted attributes
        itemPoster = poster.LEFT
        poster.visual_setFramePackageGeom(itemPoster)
        poster.visual_setFrameText(itemPoster, text=PFX_RECOVER + itemTuple2Word(
            QuestItemNames.get(self.recoverItem), self.recoverRequired, capitalizeFirstInSingular=True), maxRows=1 if complete and self.npcReturnable else 2)

        buildingPoster = poster.RIGHT
        geom, offset = self.getBuildingIconGeom()
        poster.fitGeometry(geom=geom, fFlip=0)
        if self.cogTrack:
            self.loadElevator(geom, self.floorMinimum)
            poster.visual_setFrameGeom(buildingPoster, geom=geom, scale=0.15, pos=(-0.06 + offset, 10, 0), hpr=(180, 0, 0))
        else:
            poster.visual_setFrameGeom(buildingPoster, geom=geom, scale=0.13)
        poster.visual_setFrameText(buildingPoster, self.getBuildingName(capitalize=True, accurate=True))

        # Other poster changes
        poster.visual_setFrameColor(poster.LEFT, 'green')
        poster.visual_setFrameColor(poster.RIGHT, 'green')
        poster.visual_setAuxText(AuxillaryText_From)
        poster.label_auxillaryText.show()

        # If we're complete, bonus info
        if complete:
            if self.npcReturnable:
                poster.visual_setNpcFrame(poster.RIGHT, self.getToNpcId())
                poster.visual_setFrameText(poster.RIGHT, self.getToNpcName())
                poster.visual_setAuxText(AuxillaryText_Complete)
        # And if we're not, show progress
        else:
            if self.recoverRequired > 1:
                poster.visual_setProgressInfo(
                    value=questReference.getQuestProgress(self.objectiveIndex),
                    range=self.recoverRequired,
                    textFormat=PROG_Recover,
                )

    def getProgressFormat(self, questReference):
        return questReference.getQuestProgress(self.objectiveIndex), self.recoverRequired, PROG_Recover

    def getSpeedchatMessages(self, quester, questReference: QuestReference) -> tuple:
        if questReference.isQuestComplete(quester, self.objectiveIndex):
            if self.npcReturnable:
                return self.getFinishToontaskStrings()
            return tuple()

        # Get the message formatting.
        message = SC_RecoverCogs
        buildingName = self.getBuildingName()
        itemName = itemTuple2Word(QuestItemNames.get(self.recoverItem), self.recoverRequired)
        location = ''

        # Figure out location name
        if self.buildingLocation is not None:
            location = self.getLocationName(zoneId=self.buildingLocation)

        # Return message
        return message % (itemName, buildingName, location),

    def getHeadline(self, questReference: QuestReference, objectiveSelected: int = 0) -> str:
        return HL_Recover
    
    def getObjectiveGoal(self) -> str:
        itemName = itemTuple2Word(QuestItemNames.get(self.recoverItem), self.recoverRequired)
        buildingName = self.getBuildingName()
        return OBJ_Recover % (itemName, buildingName)
    
    def getProgressString(self, questReference: QuestReference, progress: int) -> str:
        if questReference.isQuestComplete(base.localAvatar, self.objectiveIndex):
            return QuestProgress_Complete
        elif self.recoverRequired == 1:
            return ''
        return PROG_Recover.format(value=min(progress, self.recoverRequired), range=self.recoverRequired)

    def _getKwargStr(self):
        kwargstr = super()._getKwargStr()
        kwargstr += f'recoverItem=QuestItemName.{QuestItemName(self.recoverItem).name}, '
        kwargstr += f'recoverChance={self.recoverChance}, '
        if self.recoverRequired != 1:
            kwargstr += f'recoverRequired={self.recoverRequired}, '
        return kwargstr

    def __repr__(self):
        return f'RecoverFromBuildingObjective({self._getKwargStr()[:-2]})'
