from toontown.clashbattle.battle.statuses import SEE
from toontown.clashbattle.battle.visuals.VisualEffectEnums import VisualEffectEnum
from toontown.events.apriltoons.findthefamily.DistributedFindTheFamilySuitAI import DistributedFindTheFamilySuitAI
from toontown.groups import GroupEnums
from toontown.clashsuit.suit import SuitDNA
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from toontown.coghq import LevelSuitPlannerAI
from toontown.events.apriltoons.findthefamily import FindTheFamilyGlobals
import random


@DirectNotifyCategory()
class OverclockedFindTheFamilySuitPlannerAI(LevelSuitPlannerAI.LevelSuitPlannerAI):
    """
    OverclockedFindTheFamilySuitPlannerAI(LevelSuitPlannerAI)

    Used during April Toons 2023;
    It's a special Factory instance where every cog is a facility manager, but only one group is the real final battle
    """
    DebugEntry = None
    # DebugEntry = FindTheFamilyGlobals.AbilityEnum.President_HighStakes
    DebugEntry_Chance = 0.5
    # Respect the "one per row" rule of some abilities
    DebugEntry_RespectOnlyOne = True

    def __init__(self, air, level, cogCtor, battleCtor, cogSpecs, reserveCogSpecs, battleCellSpecs,
                 battleExpAggreg=None, groupCreation=None):
        self.groupCreation = groupCreation
        LevelSuitPlannerAI.LevelSuitPlannerAI.__init__(self, air, level, cogCtor, battleCtor, cogSpecs, reserveCogSpecs,
                                                       battleCellSpecs, battleExpAggreg)

    @property
    def highlyUnstable(self):
        return self.groupCreation and self.groupCreation.getOptions()[0] == GroupEnums.Options.HIGHLY_UNSTABLE

    def destroy(self):
        self.groupCreation = None
        super().destroy()

    def __genSuitObject(self, suitDict, reserve) -> DistributedFindTheFamilySuitAI:
        suit = self.cogCtor(simbase.air, self)
        dna = SuitDNA.SuitDNA()
        dna.newSuit('ftf_s')
        suit.dna = dna
        suit.setLevel(20)
        suit.setSkeleRevives(0)
        suit.setLevelDoId(self.level.doId)
        suit.setCogId(suitDict['cogId'])
        suit.setReserve(reserve)
        suit.setSkelecog(1)
        suit.setElite(1)
        suit.setMaxHp(300)
        setattr(suit, 'forceForemanFlag', 0)
        # i think they should be able to be overcharged too personally
        suit.addStartingStatusEffect(SEE.EFFECT_OVERCHARGED)
        suit.addStartingVisualEffect(VisualEffectEnum.OVERCHARGED)
        suit.generateWithRequired(suitDict['zoneId'])
        suit.boss = False
        return suit

    def genSuits(self):
        suitHandles = {}
        activeSuits = []
        for activeSuitInfo in self.suitInfos['activeSuits']:
            suit = self.__genSuitObject(activeSuitInfo, 0)
            suit.setBattleCellIndex(activeSuitInfo['battleCell'])
            activeSuits.append(suit)
            suit.ftf_cellIndex = activeSuitInfo['battleCell']

        suitHandles['activeSuits'] = activeSuits
        reserveSuits = []
        for reserveSuitInfo in self.suitInfos['reserveSuits']:
            suit = self.__genSuitObject(reserveSuitInfo, 1)
            reserveSuits.append([suit, reserveSuitInfo['joinChance'], reserveSuitInfo['battleCell']])

        hasBossAlready = False
        hasUnstableInRow = {}
        abilitiesPerRow = {}

        # 10% chance for RNG nuclears in standard, 15% chance for RNG nuclears in highly unstable mode.
        nuclearChance = FindTheFamilyGlobals.UnstableNuclearCogChance if self.highlyUnstable else FindTheFamilyGlobals.StandardNuclearCogChance

        for suit in activeSuits:
            bossRow = suit.ftf_cellIndex == 7
            # Check if this Cog should be nuclear
            # We force at least 1 unstable per row if we are in highly unstable mode
            guaranteedNuclear = bossRow or (self.highlyUnstable and not hasUnstableInRow.get(suit.ftf_cellIndex, False))
            if guaranteedNuclear or random.random() <= nuclearChance:
                hasUnstableInRow[suit.ftf_cellIndex] = True
                # They're nuclear, set the flag and move on !!
                suit.b_setNuclear(2 if bossRow else 1)
                suit.addStartingStatusEffect(SEE.EFFECT_FTF_NUCLEAR)
                if bossRow:
                    suit.addStartingStatusEffect(SEE.EFFECT_FTF_DUALCORE)

                # Check if we need to make one of these nuclears the "boss"
                if bossRow and not hasBossAlready:
                    suit.boss = True
                    hasBossAlready = True
            else:
                # Not nuclear
                suit.b_setNuclear(0)

            # Now decide what ability/suit type they should have
            # Nuclear Cogs have a slightly more strict choice pool than regular cogs
            choicePool = FindTheFamilyGlobals.AllMorphableAbilities[:] if suit.isNuclear else FindTheFamilyGlobals.AllAbilities[:]

            # Handle removing abilities of which there can only be one in a single row of.
            abilitiesPerRow.setdefault(suit.ftf_cellIndex, [])
            for abilityId in abilitiesPerRow[suit.ftf_cellIndex]:
                abilityContainer = FindTheFamilyGlobals.FamilyRegistry[abilityId]
                if abilityContainer.onlyOne and abilityId in choicePool:
                    choicePool.remove(abilityId)

            specialId = random.choice(choicePool)
            # Override with debug effect type if we have one
            if self.DebugEntry and random.random() <= self.DebugEntry_Chance:
                if self.DebugEntry_RespectOnlyOne and self.DebugEntry in abilitiesPerRow[suit.ftf_cellIndex] and FindTheFamilyGlobals.FamilyRegistry[self.DebugEntry].onlyOne:
                    pass
                elif FindTheFamilyGlobals.FamilyRegistry[self.DebugEntry].unMorphable and suit.isNuclear:
                    pass
                else:
                    specialId = self.DebugEntry

            abilitiesPerRow[suit.ftf_cellIndex].append(specialId)
            suit.b_setSpecialContainerId(specialId)
            # EFFECT_BASE is used as a no-effect placeholder
            if suit.specialContainer.effectId != SEE.EFFECT_BASE:
                suit.addStartingStatusEffect(suit.specialContainer.effectId)

        suitHandles['reserveSuits'] = reserveSuits
        return suitHandles
