from enum import IntEnum, auto
from toontown.clashbattle.battle.statuses.StatusEffectEnums import SEE
from toontown.utils.ColorHelper import hexToPCol


"""
I apologize for any inconvenient or confusing naming schemes.
"Unstable" cogs were originally called "Nuclear", and "Nuclear" cogs were originally called "Dual Core"
Thus, anything thats referring to transforming cogs will be referred to as Nuclear internally.
In-game, Nuclear cogs are just the finale cogs. Unstable cogs are the ones that transform forward-facing
"""

# Chance for Nuclear Cogs to randomly spawn throughout the facility
StandardNuclearCogChance = 0.1
UnstableNuclearCogChance = 0.15
NuclearHealthBoost = 2.0

# Data for "Dual Core" final battle stats
DualCoreHealthBoost = 4.0  # Stacks with nuclear

# Data for "Prismatic Toon" final battle stats
PrismaticToonHealthBoost = 3.0


class AbilityEnum(IntEnum):
    Foreman_Explosive = auto()
    Foreman_Sleepy = auto()
    Foreman_Contractor = auto()
    Foreman_RedTape = auto()
    Foreman_Sniper = auto()
    Foreman_Burning = auto()

    Supervisor_Abacus = auto()
    Supervisor_Absorption = auto()
    Supervisor_Confused = auto()
    Supervisor_Fraud = auto()
    Supervisor_Controlling = auto()
    Supervisor_Accountant = auto()

    Attorney_Monolith = auto()
    Attorney_Omnipotent = auto()
    Attorney_Overseer = auto()
    Attorney_Sneaky = auto()
    Attorney_Chrono = auto()
    Attorney_RushJob = auto()

    President_Mulligan = auto()
    President_ChipFan = auto()
    President_Ancient = auto()
    President_Puzzling = auto()
    President_Shivering = auto()
    President_HighStakes = auto()


class FamilyAbilityEntry:
    def __init__(self, effectId: SEE, health: int, suitType: str, suitLevel: int, suitName: str, color: tuple = (1, 1, 1, 1), unMorphable: bool = False, onlyOne: bool = False, disabled: bool = False):
        # Each entry has a relevant status effect they acquire
        self.effectId = effectId
        # Each has relevant health as well
        self.health = health
        # Suit type to choose from. Can be ('ftf_s', 'ftf_m', 'ftf_l', 'ftf_c')
        self.suitType = suitType
        # Level for this entry (Mostly arbitrary)
        self.suitLevel = suitLevel
        # Name for this entry
        self.suitName = suitName
        # Color related to this entry
        self.color = color
        # If Nuclear Cogs are blocked from being able to transform into this
        self.unMorphable = unMorphable
        # Sets that only one of these can show up in a row.
        self.onlyOne = onlyOne
        # Whether or not this entry should be able to spawn in general
        self.disabled = disabled


FamilyRegistry: [AbilityEnum, FamilyAbilityEntry] = {
    # region foremen
    AbilityEnum.Foreman_Explosive: FamilyAbilityEntry(
        effectId=SEE.EFFECT_FTF_FOREMAN_EXPLOSIVE,
        health=720,
        suitType='ftf_s',
        suitLevel=22,
        suitName='Explosive Factory Foreman',
        color=(1, 1, 1, 1),
        unMorphable=True,
    ),
    AbilityEnum.Foreman_Sleepy: FamilyAbilityEntry(
        effectId=SEE.EFFECT_FTF_FOREMAN_SLEEPY,
        health=600,
        suitType='ftf_s',
        suitLevel=20,
        suitName='Sleepy Factory Foreman',
        color=hexToPCol('ffde17'),
        unMorphable=True,
    ),
    AbilityEnum.Foreman_Contractor: FamilyAbilityEntry(
        effectId=SEE.EFFECT_FTF_FOREMAN_CONTRACTOR,
        health=950,
        suitType='ftf_s',
        suitLevel=23,
        suitName='Contractor Factory Foreman',
        color=hexToPCol('4770ff'),
        unMorphable=True,
        onlyOne=True,
    ),
    AbilityEnum.Foreman_RedTape: FamilyAbilityEntry(
        effectId=SEE.EFFECT_FTF_FOREMAN_REDTAPE,
        health=770,
        suitType='ftf_s_rt',
        suitLevel=24,
        suitName='Red Tape Factory Foreman',
        color=hexToPCol('6e0117'),
    ),
    AbilityEnum.Foreman_Sniper: FamilyAbilityEntry(
        effectId=SEE.EFFECT_FTF_FOREMAN_SNIPER,
        health=800,
        suitType='ftf_s',
        suitLevel=25,
        suitName='Sniper Factory Foreman',
        color=hexToPCol('ff4c8a'),
        onlyOne=True,
    ),
    AbilityEnum.Foreman_Burning: FamilyAbilityEntry(
        effectId=SEE.EFFECT_FTF_FOREMAN_BURNING,
        health=810,
        suitType='ftf_s_br',
        suitLevel=21,
        suitName='Burning Factory Foreman',
        color=hexToPCol('ff671d'),
    ),
    # endregion

    # region supervisors
    AbilityEnum.Supervisor_Abacus: FamilyAbilityEntry(
        effectId=SEE.EFFECT_FTF_SUPERVISOR_ABACUS,
        health=760,
        suitType='ftf_m',
        suitLevel=20,
        suitName='Abacus Mint Supervisor',
        color=hexToPCol('ff363b'),
        onlyOne=True,
    ),
    AbilityEnum.Supervisor_Absorption: FamilyAbilityEntry(
        effectId=SEE.EFFECT_FTF_SUPERVISOR_ABSORPTION,
        health=1250,
        suitType='ftf_m',
        suitLevel=28,
        suitName='Spongy Mint Supervisor',
        color=hexToPCol('12e36d'),
        onlyOne=True,
    ),
    AbilityEnum.Supervisor_Confused: FamilyAbilityEntry(
        effectId=SEE.EFFECT_FTF_SUPERVISOR_CONFUSED,
        health=770,
        suitType='ftf_m_cf',
        suitLevel=22,
        suitName='Confused Mint Supervisor',
        color=hexToPCol('919191'),
        onlyOne=True,
    ),
    AbilityEnum.Supervisor_Fraud: FamilyAbilityEntry(
        effectId=SEE.EFFECT_FTF_SUPERVISOR_FRAUD,
        health=1100,
        suitType='ftf_m',
        suitLevel=25,
        suitName='Fraudulent Mint Supervisor',
        color=hexToPCol('393eff'),
    ),
    AbilityEnum.Supervisor_Controlling: FamilyAbilityEntry(
        effectId=SEE.EFFECT_FTF_SUPERVISOR_CONTROLLING,
        health=750,
        suitType='ftf_m',
        suitLevel=21,
        suitName='Controlling Mint Supervisor',
        color=hexToPCol('e88aff'),
        onlyOne=True,
    ),
    AbilityEnum.Supervisor_Accountant: FamilyAbilityEntry(
        effectId=SEE.EFFECT_FTF_SUPERVISOR_ACCOUNTANT,
        health=765,
        suitType='ftf_m',
        suitLevel=24,
        suitName='Accountant Mint Supervisor',
        color=hexToPCol('ff8900'),
        onlyOne=True,
    ),
    # endregion

    # region attorneys
    AbilityEnum.Attorney_Monolith: FamilyAbilityEntry(
        effectId=SEE.EFFECT_FTF_ATTORNEY_MONOLITH,
        health=720,
        suitType='ftf_l',
        suitLevel=24,
        suitName='Monolithic Head Attorney',
        color=hexToPCol('954b21'),
        onlyOne=True,
    ),
    AbilityEnum.Attorney_Omnipotent: FamilyAbilityEntry(
        effectId=SEE.EFFECT_FTF_ATTORNEY_OMNIPOTENT,
        health=725,
        suitType='ftf_l',
        suitLevel=23,
        suitName='Omnipotent Head Attorney',
        color=hexToPCol('5895ff'),
        onlyOne=True,
    ),
    AbilityEnum.Attorney_Overseer: FamilyAbilityEntry(
        effectId=SEE.EFFECT_FTF_ATTORNEY_OVERSEER,
        health=660,
        suitType='ftf_l',
        suitLevel=22,
        suitName='Overseer Head Attorney',
        color=hexToPCol('1bff7d'),
        onlyOne=True,
    ),
    AbilityEnum.Attorney_Sneaky: FamilyAbilityEntry(
        effectId=SEE.EFFECT_FTF_ATTORNEY_SNEAKY,
        health=660,
        suitType='ftf_l',
        suitLevel=20,
        suitName='Sneaky Head Attorney',
        color=hexToPCol('7242f5'),
        onlyOne=True,
    ),
    AbilityEnum.Attorney_Chrono: FamilyAbilityEntry(
        effectId=SEE.EFFECT_FTF_ATTORNEY_CHRONO,
        health=865,
        suitType='ftf_l',
        suitLevel=25,
        suitName='Chrono Head Attorney',
        color=hexToPCol('dfe746'),
    ),
    AbilityEnum.Attorney_RushJob: FamilyAbilityEntry(
        effectId=SEE.EFFECT_FTF_ATTORNEY_RUSHJOB,
        health=900,
        suitType='ftf_l',
        suitLevel=26,
        suitName='Laborious Head Attorney',
        color=hexToPCol('ff394c'),
        onlyOne=True,
    ),
    # endregion

    # region presidents
    AbilityEnum.President_Mulligan: FamilyAbilityEntry(
        effectId=SEE.EFFECT_FTF_PRESIDENT_MULLIGAN,
        health=870,
        suitType='ftf_c',
        suitLevel=21,
        suitName='Mulligan Club President',
        color=hexToPCol('c4986f'),
    ),
    AbilityEnum.President_ChipFan: FamilyAbilityEntry(
        effectId=SEE.EFFECT_FTF_PRESIDENT_CHIPFAN,
        health=920,
        suitType='ftf_c',
        suitLevel=23,
        suitName='Chip Fan Club President',
        color=hexToPCol('744b25'),
    ),
    AbilityEnum.President_Ancient: FamilyAbilityEntry(
        effectId=SEE.EFFECT_FTF_PRESIDENT_ANCIENT,
        health=800,
        suitType='ftf_c_ac',
        suitLevel=22,
        suitName='Ancient Club President',
        color=hexToPCol('868686'),
    ),
    AbilityEnum.President_Puzzling: FamilyAbilityEntry(
        effectId=SEE.EFFECT_FTF_PRESIDENT_PUZZLING,
        health=875,
        suitType='ftf_c',
        suitLevel=24,
        suitName='Puzzling Club President',
        color=hexToPCol('30c52f'),
        onlyOne=True,
    ),
    AbilityEnum.President_Shivering: FamilyAbilityEntry(
        effectId=SEE.EFFECT_FTF_PRESIDENT_SHIVERING,
        health=815,
        suitType='ftf_c',
        suitLevel=25,
        suitName='Shivering Club President',
        color=hexToPCol('4bd8ff'),
        onlyOne=True,
    ),
    AbilityEnum.President_HighStakes: FamilyAbilityEntry(
        effectId=SEE.EFFECT_FTF_PRESIDENT_HIGHSTAKES,
        health=844,
        suitType='ftf_c',
        suitLevel=21,
        suitName='High Stakes Club President',
        color=hexToPCol('883fff'),
        onlyOne=True,
    ),
    # endregion
}

# Entries that cannot be morphed to by Nuclear cogs
BlockedMorphs = [key for key, entry in FamilyRegistry.items() if entry.unMorphable]
# List of all ability IDs
AllAbilities = [abilityEnum for abilityEnum in AbilityEnum if not FamilyRegistry[abilityEnum].disabled]
# List of all abilities that can be morphed into
AllMorphableAbilities = [ability for ability in AllAbilities if ability not in BlockedMorphs]
# Dict of Effect Ids -> Ability entry container
EffectIdToContainer = {container.effectId: container for container in FamilyRegistry.values() if container.effectId != SEE.EFFECT_BASE}
