from toontown.events.apriltoons.findthefamily import FindTheFamilyGlobals
from toontown.clashsuit.suit import SuitDNA
from toontown.clashsuit.suit.DistributedFactorySuitAI import DistributedFactorySuitAI
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from toontown.clashbattle.battle.statuses.StatusEffectEnums import SEE


@DirectNotifyCategory()
class DistributedFindTheFamilySuitAI(DistributedFactorySuitAI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.isNuclear = False
        self.specialContainerId = -1
        self.specialContainer = None
        # Special flag holder for nuclear purposes
        self.ftf_cellIndex = -1
        # Holder for HP ratios with nuclear cogs
        self.ftf_nuclearStoredHp = None
        self.hasDualCoreEffect = False
        self.hasNuclearEffect = False

    def b_setSpecialContainerId(self, specialContainerId):
        self.setSpecialContainerId(specialContainerId)
        self.d_setSpecialContainerId(specialContainerId)

    def setSpecialContainerId(self, specialContainerId):
        self.specialContainerId = specialContainerId
        self.specialContainer = FindTheFamilyGlobals.FamilyRegistry[specialContainerId]
        self.setLevel(self.specialContainer.suitLevel)
        dna = SuitDNA.SuitDNA()
        dna.newSuit(self.specialContainer.suitType)
        self.b_setDNAString(dna.makeNetString())
        del dna
        maxHealth = self.specialContainer.health
        if self.getStatusEffectOfId(SEE.EFFECT_FTF_DUALCORE) or self.hasDualCoreEffect:
            maxHealth *= FindTheFamilyGlobals.DualCoreHealthBoost
        if self.getStatusEffectOfId(SEE.EFFECT_FTF_NUCLEAR) or self.hasNuclearEffect:
            maxHealth *= FindTheFamilyGlobals.NuclearHealthBoost
        self.b_setMaxHp(maxHealth)
        # Apply a stored health ratio if we have it
        if self.ftf_nuclearStoredHp:
            self.b_setHp(self.ftf_nuclearStoredHp)
            self.ftf_nuclearStoredHp = None
        else:
            self.b_setHp(maxHealth)

    def d_setSpecialContainerId(self, specialContainerId):
        self.sendUpdate('setSpecialContainerId', [specialContainerId])

    def b_setNuclear(self, isNuclear):
        self.setNuclear(isNuclear)
        self.d_setNuclear(isNuclear)

    def setNuclear(self, isNuclear):
        self.isNuclear = isNuclear

    def d_setNuclear(self, isNuclear):
        self.sendUpdate('setNuclear', [isNuclear])

    def getNuclear(self) -> bool:
        return self.isNuclear

    def delete(self):
        super().delete()
        self.specialContainer = None

    def addStartingStatusEffect(self, effectId, rounds=None, extraArgs: list = None):
        super().addStartingStatusEffect(effectId, rounds=rounds, extraArgs=extraArgs)
        # Store these so that the HP is sane
        if effectId == SEE.EFFECT_FTF_NUCLEAR:
            self.hasNuclearEffect = True
        if effectId == SEE.EFFECT_FTF_DUALCORE:
            self.hasDualCoreEffect = True
