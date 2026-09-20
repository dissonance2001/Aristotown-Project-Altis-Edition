from toontown.quest3.daily.DailyConstants import QuestTierToPlayground
from toontown.quest3.objectives.DefeatCogObjective import *
from toontown.clashsuit.suit.SuitDNA import suitHeadTypes
from toontown.clashbattle.battle.SuitBattleGlobals import SuitAttributes


class DefeatSpecificCogObjective(DefeatCogObjective):
    """
    Purely a subclass for RNG task generation. Small weighted chance to defeat specific cogs anywhere
    """
    PossibleMods = {
        'cogLevelMin': 0.25,
    }
    Location2Types = {
        ToontownCentral: (0, 2),
        DonaldsDock: (1, 3),
        YeOlde: (2, 4),
        DaisyGardens: (3, 5),
        MinniesMelodyland: (4, 6),
        TheBrrrgh: (5, 7),
        OutdoorZone: (5, 7),
        DonaldsDreamland: (6, 7),
    }
    Type2SuitName = {
        typeIndex: [suitName for i, suitName in enumerate(suitHeadTypes) if i % 8 == typeIndex] for typeIndex in range(8)
    }
    SpecificCogLevelMaxes = {
        'mi': 12,
        'ls': 14,
        'sh': 10,
        'ad': 10,

        'mh': 12,
        'rb': 14,
        'bw': 16,
        'tbc': 18,
        'hho': 15,
    }
    PlaygroundLevelMaxes = {
        ToontownCentral: 3,
        DonaldsDock: 5,
        YeOlde: 6,
        DaisyGardens: 9,
    }

    @staticmethod
    def getDifficultyRange(questerType: QuesterType, questSource: QuestSource, **extraArgs):
        if questerType == QuesterType.Club:
            return None  # Not for now
        return None, None

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
        cogCount = 0.4 * (difficulty ** 1.6)
        cogLocation = None
        cogLevelMin = None
        executive = False
        zoneId = extraArgs.get("zoneId")
        questTier = extraArgs.get("questTier")
        if questTier is not None:
            zoneId = QuestTierToPlayground.get(questTier, ToontownCentral)

        possibleMods = cls.PossibleMods.copy()
        # Add really rare autocaddie if in AA/DDL
        if zoneId in (OutdoorZone, DonaldsDreamland):
            possibleMods['autocad'] = 0.04
        possibleMods['executive'] = 0.09 if zoneId == ToontownCentral else 0.2

        modifiers = []
        for possibleMod in possibleMods:
            if rng.random() <= possibleMods[possibleMod]:
                modifiers.append(possibleMod)
                if possibleMod == 'autocad':
                    break

        if 'autocad' in modifiers:
            cogType = 'autocad'
            cogLocation = SpecialQuestZones.BossbotGolfCourses
            cogCount *= 0.22
        else:
            tierMin, tierMax = cls.Location2Types[zoneId]
            tierChoice = rng.randint(tierMin, tierMax)
            cogType = rng.choice(cls.Type2SuitName[tierChoice])
            localizedTierRange = tierMax - tierMin
            localizedTierDiff = tierMax - tierChoice
            cogCount *= lerp(1.0, 1.0-(0.14*localizedTierRange), lerp(1, 0, localizedTierDiff/localizedTierRange))

            # Apply the modifiers.
            for modifier in modifiers:
                if modifier == 'cogLevelMin':
                    # lowest = SuitAttributes[cogType]['level'] + 2
                    # highest = SuitAttributes[cogType]['level'] + len(SuitAttributes[cogType]['freq'])
                    # TODO: Make this not terrible
                    lowest = 1
                    highest = 20
                    # Enforce stricter level cap for 8s
                    if cogType in cls.SpecificCogLevelMaxes:
                        highest = cls.SpecificCogLevelMaxes[cogType]
                    if zoneId in cls.PlaygroundLevelMaxes:
                        highest = cls.PlaygroundLevelMaxes[zoneId]
                    if lowest >= highest:
                        # This cog's lowest level-locked level is not applicable here, Die.
                        continue
                    else:
                        cogLevelMin = rng.randint(lowest, highest)
                    # Now, -7.5% per level over base.
                    cogCount *= (1.0 - (0.075 + 0.075*(cogLevelMin - lowest)))
                    # Head honchos are hard!!!
                    if cogType == 'hho':
                        cogCount *= 0.7
                elif modifier == 'executive':
                    executive = True
                    cogCount *= 0.38
                    # Further reduce count by 50% if we have a club quest
                    if questSource == QuestSource.ClubQuest:
                        cogCount *= 0.5

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
            skelecog=False,
            npcReturnable=False,
        )

    @staticmethod
    def getObjectiveWeight(questerType: QuesterType) -> int:
        return 10

    def __repr__(self):
        return f'DefeatSpecificCogObjective({self._getKwargStr()[:-2]})'


DefeatSpecificCogObjective()  # Thanks main
