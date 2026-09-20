from toontown.quest3.objectives.DefeatCogObjective import *


class DefeatCogInFacilityObjective(DefeatCogObjective):
    """
    Purely a subclass for RNG task generation. Small weighted chance to defeat cogs inside of facilities.
    """
    PossibleMods = {
        'cogType': 0.15,
        'cogLevelMin': 0.25,
        'executive': 0.3,
        'skelecog': 0.25,
    }
    CogChoices = {
        ToontownGlobals.SellbotHQ: ('gh', 'ms', 'tf', 'mi'),
        ToontownGlobals.CashbotHQ: ('nc', 'mb', 'ls', 'rb'),
        ToontownGlobals.LawbotHQ: ('sd', 'le', 'bw'),
        ToontownGlobals.BossbotHQ: ('hh', 'cr', 'tbc'),
    }
    LevelAsk = {
        ToontownGlobals.SellbotHQ: 7,
        ToontownGlobals.CashbotHQ: 9,
        ToontownGlobals.LawbotHQ: 11,
        ToontownGlobals.BossbotHQ: 11,
    }
    FacilityChoices = {
        ToontownGlobals.SellbotHQ: SpecialQuestZones.SellbotFactory,
        ToontownGlobals.CashbotHQ: SpecialQuestZones.CashbotMints,
        ToontownGlobals.LawbotHQ: SpecialQuestZones.LawbotLawfices,
        ToontownGlobals.BossbotHQ: SpecialQuestZones.BossbotGolfCourses,
    }
    FacilityChoiceWeights = [0.5, 0.3, 0.2]

    @staticmethod
    def getDifficultyRange(questerType: QuesterType, questSource: QuestSource, **extraArgs):
        if questSource == QuestSource.KudosQuest:
            zoneId = extraArgs.get("zoneId")
            if zoneId in (ToontownCentral, DonaldsDock, YeOlde):
                return None
        elif questSource == QuestSource.DailyQuest:
            questTier = extraArgs.get("questTier")
            if questTier in (QuestTier.NEWBIE, QuestTier.TTC, QuestTier.BB, QuestTier.YOTT):
                return None

        if questerType == QuesterType.Toon:
            return 3, None
        elif questerType == QuesterType.Club:
            return 25, None
        else:
            return 3, None

    @classmethod
    def generateFromDifficulty(cls, rng, difficulty: float, questSource: QuestSource, **extraArgs):
        """
        Given an arbitrary difficulty value, generate a QuestObjective.
        For more info, seek QuestGenerator.py.

        :param rng:        A seeded Random instance. Use this for .random() or .randint() calculations.
        :param difficulty: The arbitrary difficulty of the task.
        :return:           This QuestObjective, set with values to match the arbitrary difficulty.
        """
        # Set initial parameters.
        cogCount = 0.425 * (difficulty ** 1.65)
        cogType = None
        cogLevelMin = None
        executive = False
        skelecog = False
        zoneId = extraArgs.get("zoneId")
        questTier = extraArgs.get("questTier")
        modifiers = []
        for possibleMod in cls.PossibleMods:
            # Do not choose a cogType if we have a club quest.
            if possibleMod == 'cogType' and questSource == QuestSource.ClubQuest:
                continue
            # Can't combine these two
            if possibleMod == 'skelecog' and 'cogType' in modifiers:
                continue
            if rng.random() <= cls.PossibleMods[possibleMod]:
                modifiers.append(possibleMod)

        hqs = (SellbotHQ, CashbotHQ, LawbotHQ, BossbotHQ)  # TODO: Add Boardbot HQ eventually
        zoneRange = 0
        if zoneId:
            if zoneId == DaisyGardens:
                zoneRange = 1
            elif zoneId == MinniesMelodyland:
                zoneRange = 2
            elif zoneId == TheBrrrgh:
                zoneRange = 3
            elif zoneId == OutdoorZone:
                zoneRange = 4
            elif zoneId == DonaldsDreamland:
                zoneRange = 4  # TODO: 5 for boardbot eventually
        elif questTier:
            tier2ZoneRange = {QuestTier.DG: 1, QuestTier.MML: 2, QuestTier.TB: 3, QuestTier.AA: 4, QuestTier.DDL: 4}
            zoneRange = tier2ZoneRange[questTier]
        else:
            zoneRange = 4
        hqLocation = rng.choice(hqs[:zoneRange])
        cogLocation = cls.FacilityChoices[hqLocation]

        # Apply the modifiers.
        for modifier in modifiers:
            if modifier == 'cogType':
                cogType = rng.choice(cls.CogChoices[hqLocation])
                cogCount *= 0.45
            elif modifier == 'cogLevelMin':
                cogLevelMin = cls.LevelAsk[hqLocation]
                cogCount *= 0.6
            elif modifier == 'executive':
                executive = True
                cogCount *= 0.38
            elif modifier == 'skelecog':
                skelecog = True
                cogCount *= 0.38

        # For club quests, scale the cog count down by 30%.
        if questSource == QuestSource.ClubQuest:
            cogCount *= 0.7
        # Round off our cog count so that it is pretty.
        cogCount = math.ceil(cogCount)
        if cogCount < 1:
            cogCount = 1
        elif cogCount < 10:
            pass
        else:
            cogCount = round(round(cogCount / 2) * 2)

        # Return our objective.
        return cls(
            cogCount=math.ceil(cogCount),
            cogLocation=cogLocation,
            cogType=cogType,
            cogTrack=None,
            cogLevelMin=cogLevelMin,
            executive=executive,
            manager=False,
            skelecog=skelecog,
            npcReturnable=False,
        )

    def getLowestToonLevel(self) -> Optional[int]:
        return LowestToonLevelPerHQ[self.cogLocation]

    @staticmethod
    def getObjectiveWeight(questerType: QuesterType) -> int:
        return 14

    def __repr__(self):
        return f'DefeatCogInFacilityObjective({self._getKwargStr()[:-2]})'


DefeatCogInFacilityObjective()  # Thanks main
