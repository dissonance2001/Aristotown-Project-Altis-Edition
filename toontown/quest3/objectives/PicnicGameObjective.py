import math

from direct.gui.OnscreenImage import OnscreenImage

from toontown.quest3.base.QuestObjective import *
from toontown.quest3.context.PicnicGameContext import PicnicGameContext
from toontown.quest3.QuestLocalizer import (HL_PicnicGames, OBJ_Play, OBJ_Win,
                                            PROG_Play, PROG_Win, QuestProgress_Complete,
                                            SC_PGTPlay, SC_PGTWin, SpecialQuestZone2Name)
from toontown.safezone.picnicgame.PicnicGameGlobals import PicnicGame
from toontown.toonbase.ToontownGlobals import DonaldsDreamland, ToontownCentral, DonaldsDock


class PicnicGameObjective(QuestObjective):

    def __init__(self,
                 npc = 2001,
                 rewards=None,
                 nextStep=None,
                 npcReturnable: bool = True,
                 gameAmount: int = 1,
                 gameType: PicnicGame = None,
                 wantWins: bool = False,
                 zoneId: int = None):
        super().__init__(npc=npc, rewards=rewards, nextStep=nextStep, npcReturnable=npcReturnable)
        self.gameAmount = gameAmount
        self.gameType = gameType
        self.wantWins = wantWins
        self.zoneId = zoneId

    def calculateProgress(self, context: PicnicGameContext, questReference: QuestReference, quester: Quester) -> int:
        if type(context) is not PicnicGameContext:
            return 0
        # A zone was defined, but it doesn't match the context.
        if self.zoneId is not None and context.getZoneId() != self.zoneId:
            return 0
        if self.gameType is not None and self.gameType != context.getGameType():
            return 0
        if self.wantWins and not context.getHasWon():
            return 0
        return 1

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
        if questSource == QuestSource.KudosQuest:
            zoneId = extraArgs.get("zoneId")
            if zoneId in (ToontownCentral, DonaldsDock):
                return None

        if questSource == QuestSource.ClubQuest:
            return None  # no club quests for this objective
        return 1, 45

    @staticmethod
    def getObjectiveWeight(questerType: QuesterType) -> int:
        """
        The likelihood for this objective to be chosen in a pool.
        The de facto amount is 100.
        """
        return 6

    @classmethod
    def generateFromDifficulty(cls, rng: random.Random, difficulty: float, questSource: QuestSource, **extraArgs):
        """
        Given an arbitrary difficulty value, generate a QuestObjective.
        For more info, seek QuestGenerator.py.

        :param rng:        A seeded Random instance. Use this for .random() or .randint() calculations.
        :param difficulty: The arbitrary difficulty of the task.
        :return:           This QuestObjective, set with values to match the arbitrary difficulty.
        """
        zoneId = extraArgs.get("zoneId")
        gameAmount = 1 + math.ceil(0.05 * (difficulty ** 1.4) + rng.randint(-1, 1))
        wantWins = (rng.random() * difficulty * rng.choice((-1, 1))) > 0

        # Choose a random picnic game, with a chance of it being any.
        gameType = rng.choices(
            [None, PicnicGame.CHECKERS, PicnicGame.CHESS, PicnicGame.TOONO],
            [50, 10, 10, 30],
        )[0]

        zoneId = None
        if gameType == PicnicGame.TOONO and extraArgs.get("zoneId") == DonaldsDreamland:
            if rng.random() <= 0.001:
                zoneId = SpecialQuestZones.HM_LawbotBoss

        return cls(
            gameAmount=gameAmount,
            gameType=gameType,
            wantWins=wantWins,
            npcReturnable=False,
            zoneId=zoneId,
        )
    
    def getCompletionRequirement(self) -> int:
        return self.gameAmount

    def modifyPoster(self, questReference: QuestReference, poster):
        complete = questReference.isQuestComplete(base.localAvatar, self.objectiveIndex)
        searchPoster = poster.CENTER if not (complete and self.npcReturnable) else poster.LEFT

        poster.visual_setFrameColor(searchPoster, 'lightBlue')
        frameText = self.getGameName()
        poster.visual_setFrameText(searchPoster, frameText)
        
        if self.gameType is None:
            questIcons = loader.loadModel('phase_3.5/models/gui/quests/ttcc_quest_icons')
            basket = questIcons.find('**/basket')
            questIcons.removeNode()

            poster.visual_setFrameGeom(searchPoster, geom=basket, scale=0.15, pos=(0, 0, 0.01))
        else:
            poster.visual_setFrameGeom(searchPoster, *self.getIconGeom())

        # If we're complete, bonus info
        if complete:
            if self.npcReturnable:
                poster.visual_setFrameColor(poster.RIGHT, 'lightBlue')
                poster.visual_setNpcFrame(poster.RIGHT, self.getToNpcId())
                poster.visual_setFrameText(poster.RIGHT, self.getToNpcName())
                poster.label_auxillaryText.show()
        else:
            if self.gameAmount > 1:
                value, range, textFormat = self.getProgressFormat(questReference)
                poster.visual_setProgressInfo(value=value, range=range, textFormat=textFormat)

    def getIconGeom(self):
        pos = Point3(0, 10, 0)
        hpr = Point3(0, 0, 0)
        if self.gameType == PicnicGame.CHECKERS:
            geom = loader.loadModel("phase_6/models/golf/regular_checker_piecewhite")
            geom.find("**/checker_k*").hide()
            scale = 0.26
            hpr = Point3(0, -90, 0)
        elif self.gameType == PicnicGame.CHESS:
            model = loader.loadModel("phase_6/models/golf/chess_pieces")
            geom = model.find("**/wq")
            model.removeNode()
            scale = 0.15
        elif self.gameType == PicnicGame.TOONO:
            model = loader.loadModel("phase_6/models/golf/toono_cards")
            geom = model.find("**/reversey")
            model.removeNode()
            scale = Vec3(0.2 / 2.5, 1, 0.3 / 2.5)
        else:
            self.notify.error(f"Invalid game type provided: {repr(self.gameType)}")
        
        return geom, scale, pos, hpr
    
    def getGameName(self) -> str:
        verb = 'Win' if self.wantWins else 'Complete'
        if self.gameType is None:
            if self.gameAmount == 1:
                return f'{verb} a Picnic Game'
            else:
                return f'{verb} {self.gameAmount} Picnic Games'
        else:
            gameName = TTLocalizer.PGTGameNames[self.gameType]
            if self.gameAmount == 1:
                return f'{verb} a {gameName} Game'
            else:
                return f'{verb} {self.gameAmount} {gameName} Games'
    
    def getProgressType(self) -> str:
        return PROG_Win if self.wantWins else PROG_Play

    def getProgressFormat(self, questReference):
        return questReference.getQuestProgress(self.objectiveIndex), self.gameAmount, self.getProgressType()

    def getInfoTextStrings(self, questReference: QuestReference) -> tuple:
        if questReference.isQuestComplete(base.localAvatar, self.objectiveIndex) and self.npcReturnable:
            return super().getInfoTextStrings(questReference)

        if self.zoneId in SpecialQuestZone2Name:
            return SpecialQuestZone2Name[self.zoneId][2],

        return self.getLocationName(self.zoneId),

    def getSpeedchatMessages(self, quester, questReference: QuestReference) -> tuple:
        if questReference.isQuestComplete(quester, self.objectiveIndex):
            if self.npcReturnable:
                return self.getFinishToontaskStrings()
            return tuple()

        scString = SC_PGTWin if self.wantWins else SC_PGTPlay
        if self.gameType is None:
            gameName = f"a picnic game" if self.gameAmount == 1 else "some picnic games"
        else:
            string = f"a game" if self.gameAmount == 1 else "some games"
            gameName = f"{string} of {TTLocalizer.PGTGameNames[self.gameType]}"

        return scString % gameName,

    def getHeadline(self, questReference: QuestReference, objectiveSelected: int = 0) -> str:
        return HL_PicnicGames
    
    def getObjectiveGoal(self) -> str:
        string = OBJ_Win if self.wantWins else OBJ_Play
        return string % "Picnic Game"

    def getProgressString(self, questReference: QuestReference, progress: int) -> str:
        if questReference.isQuestComplete(base.localAvatar, self.objectiveIndex):
            return QuestProgress_Complete
        elif self.gameAmount == 1:
            return ''
        return self.getProgressType().format(value=min(progress, self.gameAmount), range=self.gameAmount)
    
    def _getKwargStr(self):
        kwargstr = super()._getKwargStr()
        if self.gameAmount is not None:
            kwargstr += f'gameAmount={self.gameAmount}, '
        if self.gameType is not None:
            kwargstr += f'gameType={self.gameType}'
        kwargstr += f'wantWins={self.wantWins}'
        return kwargstr

    def __repr__(self):
        return f'PicnicGameObjective({self._getKwargStr()[:-2]})'


PicnicGameObjective() # thank you m ain
