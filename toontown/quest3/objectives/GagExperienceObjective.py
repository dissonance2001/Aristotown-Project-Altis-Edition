from toontown.quest3.base.QuestObjective import *
from toontown.quest3.context.GagExperienceContext import GagExperienceContext
from toontown.quest3.context.PurchaseGagContext import PurchaseGagContext
from toontown.quest3.QuestLocalizer import AtTheGagShop, HL_Purchase, OBJ_PurchaseGag, QuestProgress_Complete, SC_Gags, \
    Anywhere, SC_GagExp, HL_Earn, OBJ_Earn, PROG_Earn, PFX_EARN
from toontown.clashbattle.battle.BattleGlobals import AvPropsNew, Levels


class GagExperienceObjective(QuestObjective):
    """
    A quest where you must earn gag experience.
    """

    def __init__(self,
                 npc=2001,
                 rewards=None,
                 nextStep=None,
                 npcReturnable: bool = True,
                 track: int = -1,
                 expReq: int = 10):
        super().__init__(npc=npc, rewards=rewards, nextStep=nextStep, npcReturnable=npcReturnable)
        self.track = track
        self.expReq = expReq

    @staticmethod
    def getDifficultyRange(questerType: QuesterType, questSource: QuestSource, **extraArgs):
        """
        Returns the difficulty range required to use this objective in random quest generation.

        :return: Any of the following:
                 A) Two floats, for a lower and upper bound
                 B) A float and None, for a lower bound and no upper bound
                 C) None and a float, for no lower bound and an upper bound
                 D) Two nones, for no difficulty bound
                 E) One none, for "cannot be used"
        """
        if questerType == QuesterType.Club:
            return None
        return 1, None

    @staticmethod
    def getObjectiveWeight(questerType: QuesterType) -> int:
        """
        The likelihood for this objective to be chosen in a pool.
        The de facto amount is 100.
        """
        return 20

    def calculateProgress(self, context: QuestContext, questReference: QuestReference, quester: Quester) -> int:
        if type(context) is not GagExperienceContext:
            return 0

        if self.track == context.getTrack() or self.track == -1:
            return context.getExperience()

        return 0

    @classmethod
    def generateFromDifficulty(cls, rng, difficulty: float, questSource: QuestSource, **extraArgs):
        """
        Given an arbitrary difficulty value, generate a QuestObjective.
        For more info, seek QuestGenerator.py.

        :param rng:        A seeded Random instance. Use this for .random() or .randint() calculations.
        :param difficulty: The arbitrary difficulty of the task.
        :return:           This QuestObjective, set with values to match the arbitrary difficulty.
        """
        expReq = 9.0 * (difficulty ** 1.8)
        track = -1
        # if questSource == QuestSource.KudosQuest or questSource == QuestSource.ClubQuest:
        #     track = -1 # Force universal quests for now, since we dont have access to toon track access
        # elif questSource == QuestSource.ClubQuest:
        #     track = rng.randint(-1, 7) # Clubs can have any gag track, since gag variety across all toons

        if track == -1:
            # Increase exp req if its a universal xp task
            expReq *= 1.5
        expReq = int(expReq)

        # Do some rounding on expReq
        expReqStr = str(expReq)
        if len(expReqStr) < 3: # <100
            pass
        else:
            newExpList = []
            for i, char in enumerate(expReqStr): # Keep first 3 sigfigs, purge/modify rest
                if i == 2:
                    newExpList.append(rng.choice((0, 5))) # Set the 3rd to either 0 or 5 for pretty numbers
                elif i > 2:
                    newExpList.append(0) # Set any further values to 0 to clean them up
                else:
                    newExpList.append(int(char))

            newExp = 0
            mult = 1
            newExpList.reverse()
            for xp in newExpList:
                newExp += mult * xp
                mult *= 10

            expReq = newExp

        # Generate the class
        return cls(
            track=track,
            expReq=expReq,
            npcReturnable=False,
        )

    def modifyPoster(self, questReference: QuestReference, poster):
        complete = questReference.isQuestComplete(base.localAvatar, self.objectiveIndex)
        searchPoster = poster.CENTER if not (complete and self.npcReturnable) else poster.LEFT

        poster.visual_setFrameColor(searchPoster, 'yellow')
        if self.track == -1:
            poster.visual_setFrameText(searchPoster, PFX_EARN + f"{self.expReq} Gag Experience")
            lIconGeom = ('phase_3.5/models/gui/exp_icon')
            scale = 0.15
        else:
            trackName = TTLocalizer.ToonTrackNames[self.track].upper()
            poster.visual_setFrameText(searchPoster, PFX_EARN + f"{self.expReq} {trackName} Experience")
            xpReqs = Levels[self.track]
            levelIdx = 0
            for req in xpReqs:
                if req < self.expReq:
                    levelIdx += 1

            invModel = loader.loadModel('phase_3.5/models/gui/inventory_icons')
            level = min(levelIdx, 7)
            lIconGeom = invModel.find('**/' + AvPropsNew[self.track][level])
            invModel.removeNode()
            scale = 1

        poster.visual_setFrameGeom(searchPoster,
                                   geom=lIconGeom,
                                   scale=scale)

        # If we're complete, bonus info
        if not complete:
            value, range, textFormat = self.getProgressFormat(questReference)
            poster.visual_setProgressInfo(value=value, range=range, textFormat=textFormat)
        else:
            if self.npcReturnable:
                poster.visual_setFrameColor(poster.RIGHT, 'yellow')
                poster.visual_setNpcFrame(poster.RIGHT, self.getToNpcId())
                poster.visual_setFrameText(poster.RIGHT, self.getToNpcName())
                poster.label_auxillaryText.show()

    def getProgressFormat(self, questReference):
        return questReference.getQuestProgress(self.objectiveIndex), self.expReq, PROG_Earn

    def getInfoTextStrings(self, questReference: QuestReference) -> tuple:
        # If we're complete and demand NPC completion, point to NPC instead
        if questReference.isQuestComplete(base.localAvatar, self.objectiveIndex) and self.npcReturnable:
            return super().getInfoTextStrings(questReference)

        return Anywhere,

    def getSpeedchatMessages(self, quester, questReference: QuestReference) -> tuple:
        if questReference.isQuestComplete(quester, self.objectiveIndex):
            return tuple()
        trackName = TTLocalizer.ToonTrackNames[self.track].upper() if self.track != -1 else TTLocalizer.Gag.lower()
        retVal = SC_GagExp % (self.expReq, trackName)
        return retVal,

    def getHeadline(self, questReference: QuestReference, objectiveSelected: int = 0) -> str:
        return HL_Earn

    def getCompletionRequirement(self) -> int:
        return self.expReq

    def getObjectiveGoal(self) -> str:
        trackName = TTLocalizer.ToonTrackNames[self.track].upper() if self.track != -1 else TTLocalizer.Gag.lower()
        retVal = OBJ_Earn % (f"{self.expReq} {trackName}", 'experience')
        return retVal

    def getProgressString(self, questReference: QuestReference, progress: int) -> str:
        if questReference.isQuestComplete(base.localAvatar, self.objectiveIndex):
            return QuestProgress_Complete
        elif self.expReq == 1:
            return ''
        return PROG_Earn.format(value=min(progress, self.expReq), range=self.expReq)

    def __repr__(self):
        return f'GagExperienceObjective({self._getKwargStr()[:-2]})'


GagExperienceObjective()  # hack thanks to main
