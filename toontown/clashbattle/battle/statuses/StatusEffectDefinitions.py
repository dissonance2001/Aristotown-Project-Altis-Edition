from typing import Dict

from toontown.battle.attacks.base.AttackEnum import AttackEnum
from . import StatusEffects
from toontown.toonbase import TTLocalizer
from toontown.battle import BattleGlobals
from toontown.battle.BattleEventGlobals import BEG
from . import SEE
from ..visuals.VisualEffectEnums import VisualEffectEnum

"""
StatusEffectDefinitions.py is used for defining all of the
various visual attributes for new status effects, along with
their basic properties (e.g. round count, arguments passed to them).

IMPORTANT:
The actual technical implementation of Status Effects are defined in StatusEffects.py.
This file is exclusively for defining all of the non-gameplay qualities of a status effect.
"""

NO_ROUNDS = -1
THIS_ROUND = 0

DEBUFF = 0
BUFF = 1
NEUTRAL = 2

StatusEffectDescriptions = TTLocalizer.StatusEffectDescriptions
StatusEffectDefinitions: Dict[SEE, 'StatusEffectDefinition'] = {}


class StatusEffectDefinition:
    """
    A Suit Definition object, which hosts all information and data on a given suit.
    """

    def __init__(self, effectId: int, quality: int, effectClass) -> None:
        # The basic associations of a Status Effect definition.
        self.effectId = effectId
        self.effectClass = effectClass
        self.quality = quality

        # Set the default attributes.
        self.roundCount = None
        self.disabledRoundCount = None
        self.extraArgs = None
        self.setDefaults()

        # Set the icon properties.
        self.background = None
        self.icon = None
        self.iconSuffix = None
        self.bgSuffix = None
        self.iconScale = None
        self.setIconProperties('')
        self.visible = True

        # Any visual effects associated?
        self.visualEffectEnums = []

        # Add the effect to the dict of all definitions
        StatusEffectDefinitions[effectId] = self

    def setDefaults(self, rounds: int = NO_ROUNDS, disabledRounds: int = 0, extraArgs=()):
        self.roundCount = rounds
        self.disabledRoundCount = disabledRounds
        self.extraArgs = (extraArgs,) if type(extraArgs) not in (tuple, list) else tuple(extraArgs)

    def setIconProperties(self, icon, background: str = 'default', visible: bool = True,
                          iconSuffix: str = '_icon', bgSuffix: str = '_background', iconScale: float = 1.0):
        self.icon = icon
        self.background = background
        self.iconSuffix = iconSuffix
        self.bgSuffix = bgSuffix
        self.visible = visible
        self.iconScale = iconScale

    def setVisualEffectEnums(self, visualEffectEnums):
        if type(visualEffectEnums) is not list:
            visualEffectEnums = [visualEffectEnums]
        self.visualEffectEnums = visualEffectEnums

    def getVisualEffectEnums(self):
        return self.visualEffectEnums

    def setFlag(self):
        """
        Sets this Definition to be a "flag".
        """
        self.setDefaults()
        self.visible = False

    ## Build Methods ##
    def buildAttributes(self):
        retdict = {
            'class': self.effectClass,
            'rounds': self.roundCount,
            'disabledRounds': self.disabledRoundCount,
        }
        if self.extraArgs:
            retdict['extraArgs'] = self.extraArgs
        return retdict

    def buildTextProperties(self):
        default = StatusEffectDescriptions[SEE.EFFECT_BASE]
        return TTLocalizer.StatusEffectDescriptions.get(self.effectId, default)

    def buildImageProperties(self):
        return self.background, self.icon, self.iconSuffix, self.bgSuffix, self.iconScale

    def getBuffStatus(self):
        return self.quality


### DEFINITIONS START ###
# region General Status Effects
__BASE = StatusEffectDefinition(SEE.EFFECT_BASE, BUFF, StatusEffects.StatusEffectBase)
__BASE.setDefaults(rounds=3)

__CANT_ATTACK = StatusEffectDefinition(SEE.EFFECT_CANT_ATTACK, DEBUFF, StatusEffects.CantAttackStatusEffect)
__CANT_ATTACK.setDefaults(rounds=THIS_ROUND)

__DAMAGE_DOWN = StatusEffectDefinition(SEE.EFFECT_DAMAGE_DOWN, DEBUFF, StatusEffects.AttackEffectivenessStatusEffect)
__DAMAGE_DOWN.setDefaults(rounds=THIS_ROUND, extraArgs=(1.0,))

__OVERRIDE_ADDED = StatusEffectDefinition(SEE.DEFINITION_OVERRIDE_ADDED, BUFF, StatusEffects.OverrideAddedStatusEffect)
__OVERRIDE_ADDED.setDefaults(rounds=NO_ROUNDS)
__OVERRIDE_ADDED.setIconProperties(None, visible=False)

__CONFUSION = StatusEffectDefinition(SEE.EFFECT_CONFUSION, DEBUFF, StatusEffects.AttackAccuracyStatusEffect)
__CONFUSION.setDefaults(rounds=2, extraArgs=(-30, -1))
__CONFUSION.setIconProperties('toon_accuracy_up')

__UNTOUCHABLE = StatusEffectDefinition(SEE.EFFECT_UNTOUCHABLE, BUFF, StatusEffects.UntouchableStatusEffect)
__UNTOUCHABLE.setDefaults(rounds=THIS_ROUND)

__DAMAGE_ABSORB_DAMAGE_DOWN = StatusEffectDefinition(SEE.EFFECT_DAMAGE_ABSORB_DAMAGE_DOWN, BUFF, StatusEffects.DamageAbsorbDamageDownStatusEffect)
__DAMAGE_ABSORB_DAMAGE_DOWN.setDefaults(rounds=NO_ROUNDS, extraArgs=(0.8,))

__DAMAGE_TAKEN_UP = StatusEffectDefinition(SEE.EFFECT_DAMAGE_TAKEN_UP, DEBUFF, StatusEffects.AvatarTakeModifiedDamageStatusEffect)
__DAMAGE_TAKEN_UP.setDefaults(rounds=2, extraArgs=(1.2,))
__DAMAGE_TAKEN_UP.setIconProperties(icon='broken_shield', iconScale=0.9)

__DAMAGE_TAKEN_DOWN = StatusEffectDefinition(SEE.EFFECT_DAMAGE_TAKEN_DOWN, BUFF, StatusEffects.AvatarTakeModifiedDamageStatusEffect)
__DAMAGE_TAKEN_DOWN.setDefaults(rounds=NO_ROUNDS, extraArgs=(0.8,))
__DAMAGE_TAKEN_DOWN.setIconProperties(icon='shield', iconScale=0.85)

__DAMAGE_TAKEN_FLAT_DOWN = StatusEffectDefinition(SEE.EFFECT_FLATTENED_DAMAGE_TAKEN, BUFF, StatusEffects.AvatarTakeFlattenedDamageStatusEffect)
__DAMAGE_TAKEN_FLAT_DOWN.setDefaults(rounds=NO_ROUNDS, extraArgs=(5))
__DAMAGE_TAKEN_FLAT_DOWN.setIconProperties(icon='shield', iconScale=0.85)

__DAMAGE_ABSORB = StatusEffectDefinition(SEE.EFFECT_COGS_DAMAGE_ABSORB, BUFF, StatusEffects.DamageAbsorbStatusEffect)
__DAMAGE_ABSORB.setDefaults(rounds=NO_ROUNDS, extraArgs=(0.7, 0))
__DAMAGE_ABSORB.setIconProperties(icon='damage_absorb')

__DAMAGE_ABSORB_INSTANT = StatusEffectDefinition(SEE.EFFECT_COGS_DAMAGE_ABSORB_INSTANT, BUFF, StatusEffects.DamageAbsorbInstantStatusEffect)
__DAMAGE_ABSORB_INSTANT.setDefaults(rounds=NO_ROUNDS, extraArgs=(0.7, 0))
__DAMAGE_ABSORB_INSTANT.setIconProperties(icon='damage_absorb')

__HIT = StatusEffectDefinition(SEE.EFFECT_HIT, BUFF, StatusEffects.HiddenAttackAccuracyStatusEffect)
__HIT.setDefaults(rounds=NO_ROUNDS, extraArgs=(100, 100))

__MISS = StatusEffectDefinition(SEE.EFFECT_MISS, DEBUFF, StatusEffects.HiddenAttackAccuracyStatusEffect)
__MISS.setDefaults(rounds=NO_ROUNDS, extraArgs=(-100, -100))

__RUSH_JOB = StatusEffectDefinition(SEE.EFFECT_RUSH_JOB, BUFF, StatusEffects.RushJobStatusEffect)
__RUSH_JOB.setDefaults(rounds=THIS_ROUND, extraArgs=(AttackEnum.TOON_NO_ATTACK, 0))
__RUSH_JOB.setIconProperties(icon='attack')
__RUSH_JOB.setVisualEffectEnums(VisualEffectEnum.RUSH_JOB)

__HURRY_SICKNESS = StatusEffectDefinition(SEE.EFFECT_HURRY_SICKNESS, DEBUFF, StatusEffects.HurrySicknessStatusEffect)
__HURRY_SICKNESS.setDefaults(rounds=1, extraArgs=(.5, .75, StatusEffects.PacesetterStatusEffectBase.NORMAL, 0))
__HURRY_SICKNESS.setIconProperties(icon='hurry_sickness')

__MOVING_GOAL_POSTS = StatusEffectDefinition(SEE.EFFECT_MOVING_GOALPOSTS, DEBUFF, StatusEffects.UseGagLevelsWithTrackSenderStatusEffect)
__MOVING_GOAL_POSTS.setDefaults(rounds=NO_ROUNDS, extraArgs=(*[-1] * len(BattleGlobals.Tracks), BEG.EVENT_PACESETTER_BAD_LEVEL_USED))
__MOVING_GOAL_POSTS.setIconProperties('backfire')

__DEAD = StatusEffectDefinition(SEE.EFFECT_DEAD, DEBUFF, StatusEffects.StatusEffectBase)

# endregion

# region Toon-Specific Status Effects
__TOON_DAMAGE_UP = StatusEffectDefinition(SEE.EFFECT_TOON_DAMAGE_UP, BUFF, StatusEffects.ToonDamageBoostStatusEffect)
__TOON_DAMAGE_UP.setDefaults(rounds=NO_ROUNDS, extraArgs=(10, -1, 1))
__TOON_DAMAGE_UP.setIconProperties('toon_damage_up')

__TOON_MULT_DAMAGE_UP = StatusEffectDefinition(SEE.EFFECT_TOON_MULT_DAMAGE_UP, BUFF, StatusEffects.AttackEffectivenessStatusEffect)
__TOON_MULT_DAMAGE_UP.setDefaults(rounds=1, extraArgs=(1.1, 2))
__TOON_MULT_DAMAGE_UP.setIconProperties('toon_damage_up')

__UNITE_COOLDOWN = StatusEffectDefinition(SEE.EFFECT_UNITE_COOLDOWN, DEBUFF, StatusEffects.UnitesDisabledStatusEffect)
__UNITE_COOLDOWN.setDefaults(rounds=4)
__UNITE_COOLDOWN.setIconProperties('unite_cooldown')

__REWARD_COOLDOWN = StatusEffectDefinition(SEE.EFFECT_REWARD_COOLDOWN, DEBUFF, StatusEffects.RewardCooldownStatusEffect)
__REWARD_COOLDOWN.setDefaults(rounds=3)
__REWARD_COOLDOWN.setIconProperties('reward_cooldown')

__HYDRATED = StatusEffectDefinition(SEE.EFFECT_HYDRATED, BUFF, StatusEffects.AttackAccuracyStatusEffect)
__HYDRATED.setDefaults(rounds=3, extraArgs=(15, -1))

__ENCORE = StatusEffectDefinition(SEE.EFFECT_ENCORE, BUFF, StatusEffects.EncoreStatusEffect)
__ENCORE.setDefaults(rounds=1, extraArgs=(1.15, -1, 1))
__ENCORE.setVisualEffectEnums(VisualEffectEnum.ENCORE)
__ENCORE.setIconProperties('encore')

__WINDED = StatusEffectDefinition(SEE.EFFECT_WINDED, DEBUFF, StatusEffects.WindedStatusEffect)
__WINDED.setDefaults(rounds=2, extraArgs=(0.50,))
__WINDED.setVisualEffectEnums(VisualEffectEnum.WINDED)
__WINDED.setIconProperties('encore')

__DEEP_FREEZE = StatusEffectDefinition(SEE.EFFECT_DEEP_FREEZE, DEBUFF, StatusEffects.DeepFreezeStatusEffect)
__DEEP_FREEZE.setDefaults(rounds=2, extraArgs=(100, -1, 0))
__DEEP_FREEZE.setIconProperties('deepfreeze')
__DEEP_FREEZE.setVisualEffectEnums([VisualEffectEnum.DEEP_FREEZE, VisualEffectEnum.UNITE_COOLDOWN])

__MARKED_WOOD = StatusEffectDefinition(SEE.EFFECT_MARKED_WOOD, DEBUFF, StatusEffects.MarkedWoodStatusEffect)
__MARKED_WOOD.setDefaults(rounds=1, extraArgs=1.75)
__MARKED_WOOD.setIconProperties(icon='marked_wood')
__MARKED_WOOD.setVisualEffectEnums(VisualEffectEnum.MARKED_WOOD)

__JUST_MISSED = StatusEffectDefinition(SEE.EFFECT_TOON_JUST_MISSED, BUFF, StatusEffects.ToonJustMissedStatusEffect)
__JUST_MISSED.setDefaults(rounds=1, extraArgs=(10, -1))
__JUST_MISSED.setIconProperties(icon=None, visible=False)
# endregion

# region Suit-Specific Status Effects
__SUIT_BASE = StatusEffectDefinition(SEE.EFFECT_SUIT, BUFF, StatusEffects.CogStatusEffect)
__SUIT_BASE.setDefaults(rounds=NO_ROUNDS)

__SUIT_LURED = StatusEffectDefinition(SEE.EFFECT_SUIT_LURED, DEBUFF, StatusEffects.LureStatusEffect)
__SUIT_LURED.setDefaults(rounds=0, extraArgs=(False, 0, BattleGlobals.LureAccuracy))
__SUIT_LURED.setIconProperties(('lured', 'lured_prestige'))

__SUIT_SOAKED = StatusEffectDefinition(SEE.EFFECT_SUIT_SOAKED, DEBUFF, StatusEffects.SoakStatusEffect)
__SUIT_SOAKED.setDefaults(rounds=0, extraArgs=(BattleGlobals.SoakDefBonusAmt,))
__SUIT_SOAKED.setIconProperties('soaked')

__SUIT_DRENCHED = StatusEffectDefinition(SEE.EFFECT_SUIT_DRENCHED, DEBUFF, StatusEffects.DrenchStatusEffect)
__SUIT_DRENCHED.setDefaults(rounds=0, extraArgs=(BattleGlobals.DrenchDefBonusAmt, 0.85, 2))
__SUIT_DRENCHED.setIconProperties('soaked')

__SUIT_SUED = StatusEffectDefinition(SEE.EFFECT_SUIT_SUED, DEBUFF, StatusEffects.SueStatusEffect)
__SUIT_SUED.setDefaults(rounds=BattleGlobals.NumRoundsCeaseDesist)
__SUIT_SUED.setIconProperties('sued', iconScale=0.95)

__SUIT_DAMAGE_BOOST = StatusEffectDefinition(SEE.EFFECT_SUIT_DAMAGE_BOOST, BUFF, StatusEffects.MultiplicativeDamageBoostStatusEffect)
__SUIT_DAMAGE_BOOST.setDefaults(rounds=NO_ROUNDS, extraArgs=(1.5, 2))
__SUIT_DAMAGE_BOOST.setIconProperties(('attack', 'suit_damage_up'))

__SUIT_TRAPPED = StatusEffectDefinition(SEE.EFFECT_SUIT_TRAPPED, DEBUFF, StatusEffects.TrappedStatusEffect)
__SUIT_TRAPPED.setDefaults(rounds=NO_ROUNDS, extraArgs=(0, 0))
__SUIT_TRAPPED.setIconProperties(None)

__SUIT_DAZED = StatusEffectDefinition(SEE.EFFECT_SUIT_DAZED, DEBUFF, StatusEffects.SuitDefenseModifierStatusEffect)
__SUIT_DAZED.setDefaults(rounds=1, extraArgs=(-10,))
__SUIT_DAZED.setIconProperties('confusion')

__SUIT_DEFENSE_MODIFIER = StatusEffectDefinition(SEE.EFFECT_SUIT_DEFENSE_MODIFIER, DEBUFF, StatusEffects.SuitDefenseModifierStatusEffect)
__SUIT_DEFENSE_MODIFIER.setDefaults(rounds=NO_ROUNDS, extraArgs=(-20,))
__SUIT_DEFENSE_MODIFIER.setIconProperties('confusion')

__SUIT_CANNOT_DODGE = StatusEffectDefinition(SEE.EFFECT_SUIT_NODODGE, DEBUFF, StatusEffects.SuitCannotDodgeStatusEffect)
__SUIT_CANNOT_DODGE.setDefaults(rounds=1)
__SUIT_CANNOT_DODGE.setIconProperties('confusion')

__SUIT_ADDITIVE_DAMAGE_BOOST = StatusEffectDefinition(SEE.EFFECT_SUIT_ADDITIVE_DAMAGE_BOOST, BUFF, StatusEffects.AdditiveDamageBoostStatusEffect)
__SUIT_ADDITIVE_DAMAGE_BOOST.setDefaults(rounds=NO_ROUNDS, extraArgs=(0, 2))
__SUIT_ADDITIVE_DAMAGE_BOOST.setIconProperties(('attack', 'suit_damage_up'))

__LURE_RESISTANCE = StatusEffectDefinition(SEE.EFFECT_LURE_RESISTANCE, BUFF, StatusEffects.LureResistanceStatusEffect)
__LURE_RESISTANCE.setDefaults(rounds=NO_ROUNDS, extraArgs=1)
__LURE_RESISTANCE.setIconProperties('lured_prestige')

__MARKED_FOR_LAUGH = StatusEffectDefinition(SEE.EFFECT_MARKED_FOR_LAUGH, DEBUFF, StatusEffects.MarkedForLaughStatusEffect)
__MARKED_FOR_LAUGH.setDefaults(rounds=THIS_ROUND, extraArgs=(BattleGlobals.ThrowMarkPercent, 0))
__MARKED_FOR_LAUGH.setIconProperties('marked')
__MARKED_FOR_LAUGH.setVisualEffectEnums(VisualEffectEnum.SPLAT)

__OVERCHARGED = StatusEffectDefinition(SEE.EFFECT_OVERCHARGED, BUFF, StatusEffects.OverchargeStatusEffect)
__OVERCHARGED.setDefaults(rounds=NO_ROUNDS, extraArgs=(2, 1.5, 2, 1.5))
__OVERCHARGED.setIconProperties('overcharge')
__OVERCHARGED.setVisualEffectEnums(VisualEffectEnum.OVERCHARGED)

__GATEKEEPER_FODDER_BONUS = StatusEffectDefinition(SEE.EFFECT_GATEKEEPER_FODDER_BONUS, BUFF, StatusEffects.GatekeeperFodderBonusEffect)
__GATEKEEPER_FODDER_BONUS.setDefaults(rounds=NO_ROUNDS, extraArgs=(100, 3))
__GATEKEEPER_FODDER_BONUS.setIconProperties('gatekeeper')
__GATEKEEPER_FODDER_BONUS.setVisualEffectEnums(VisualEffectEnum.CORE_COMPETENCY)

__GATEKEEPER_TOON_PIERCE = StatusEffectDefinition(SEE.EFFECT_GATEKEEPER_TOON_PIERCE, BUFF, StatusEffects.GatekeeperToonPierceEffect)
__GATEKEEPER_TOON_PIERCE.setDefaults(rounds=1, extraArgs=(3,))
__GATEKEEPER_TOON_PIERCE.setIconProperties(icon='broken_shield', iconScale=0.9)

__COMBO_KB_IMMUNITY = StatusEffectDefinition(SEE.EFFECT_COMBO_KB_IMMUNITY, BUFF, StatusEffects.ComboKbImmunityStatusEffect)
__COMBO_KB_IMMUNITY.setDefaults(rounds=NO_ROUNDS)

__PLASTIC_SUIT = StatusEffectDefinition(SEE.EFFECT_PLASTIC_SUIT, BUFF, StatusEffects.PlasticSuitStatusEffect)
__PLASTIC_SUIT.setDefaults(rounds=NO_ROUNDS)
__PLASTIC_SUIT.setIconProperties('zapimmune')

__SUIT_FROZEN = StatusEffectDefinition(SEE.EFFECT_SUIT_FROZEN, DEBUFF, StatusEffects.FrozenStatusEffect)
__SUIT_FROZEN.setDefaults(rounds=NO_ROUNDS, extraArgs=(BattleGlobals.FrozenDefBonusAmt, 0))
__SUIT_FROZEN.setIconProperties('frozen')

__PRETHINKER_DODGE_SOUND = StatusEffectDefinition(SEE.EFFECT_PRETHINKER_DODGE_SOUND, BUFF, StatusEffects.UntouchableStatusEffect)
__PRETHINKER_DODGE_SOUND.setDefaults(rounds=THIS_ROUND)

__PRETHINKER_DAMAGE_TAKEN_DOWN = StatusEffectDefinition(SEE.EFFECT_PRETHINKER_DAMAGE_TAKEN_DOWN, BUFF, StatusEffects.AvatarTakeModifiedDamageStatusEffect)
__PRETHINKER_DAMAGE_TAKEN_DOWN.setDefaults(rounds=THIS_ROUND, extraArgs=0.5)

__SLUSH_FUND = StatusEffectDefinition(SEE.EFFECT_SLUSH_FUND, BUFF, StatusEffects.AvatarTakeModifiedDamageStatusEffect)
__SLUSH_FUND.setDefaults(rounds=2, extraArgs=0.6)
__SLUSH_FUND.setIconProperties(icon='slush_fund')
__SLUSH_FUND.setVisualEffectEnums(VisualEffectEnum.SLUSH_FUND)

__LUNCH_BREAK = StatusEffectDefinition(SEE.EFFECT_LUNCH_BREAK, DEBUFF, StatusEffects.LunchBreakStatusEffect)
__LUNCH_BREAK.setDefaults(rounds=1)

__LUNCH_BREAK_MSLACKER = StatusEffectDefinition(SEE.EFFECT_LUNCH_BREAK_MSLACKER, BUFF, StatusEffects.LunchBreakMslackerEffect)
__LUNCH_BREAK_MSLACKER.setDefaults(rounds=3)
__LUNCH_BREAK_MSLACKER.setIconProperties(None, 'lunch')
__LUNCH_BREAK_MSLACKER.setVisualEffectEnums(VisualEffectEnum.MANDATORY_LUNCH_MSLACKER)

__OUT_FOR_LUNCH = StatusEffectDefinition(SEE.EFFECT_OUT_FOR_LUNCH, BUFF, StatusEffects.AvatarTakeModifiedDamageStatusEffect)
__OUT_FOR_LUNCH.setDefaults(rounds=NO_ROUNDS, extraArgs=(0.75))
__OUT_FOR_LUNCH.setIconProperties(None, 'lunch')

__FOCUSED_DEFENSE = StatusEffectDefinition(SEE.EFFECT_FOCUSED_DEFENSE, BUFF, StatusEffects.FocusedDefenseStatusEffect)
__FOCUSED_DEFENSE.setDefaults(rounds=NO_ROUNDS, extraArgs=0.5)
__FOCUSED_DEFENSE.setIconProperties('focused_defense')

__WORKER_MANAGEMENT = StatusEffectDefinition(SEE.EFFECT_WORKER_MANAGEMENT, BUFF, StatusEffects.WorkerManagementStatusEffect)
__WORKER_MANAGEMENT.setDefaults(rounds=NO_ROUNDS)
__WORKER_MANAGEMENT.setIconProperties('worker_management')

__UNION_BUST = StatusEffectDefinition(SEE.EFFECT_UNION_BUST, BUFF, StatusEffects.UnionBustStatusEffect)
__UNION_BUST.setDefaults(rounds=1)
__UNION_BUST.setIconProperties(icon='union_bust')

__SOAK_RESISTANCE = StatusEffectDefinition(SEE.EFFECT_SOAK_RESISTANCE, BUFF, StatusEffects.SoakResistanceStatusEffect)
__SOAK_RESISTANCE.setDefaults(rounds=NO_ROUNDS, extraArgs=(0.4))
__SOAK_RESISTANCE.setIconProperties('soak_shield', iconScale=0.85)

__MONSOON = StatusEffectDefinition(SEE.EFFECT_MONSOON, DEBUFF, StatusEffects.MonsoonStatusEffect)
__MONSOON.setDefaults(rounds=2, extraArgs=[100, 100])
__MONSOON.setIconProperties(icon='schadenfreude')

__MONSOON_DEFENSE = StatusEffectDefinition(SEE.EFFECT_MONSOON_DEFENSE, BUFF, StatusEffects.AvatarTakeModifiedDamageStatusEffect)
__MONSOON_DEFENSE.setDefaults(rounds=2, extraArgs=0.1)
__MONSOON_DEFENSE.setIconProperties(icon='schadenfreude')

__END_BATTLE_ON_DEATH = StatusEffectDefinition(SEE.EFFECT_END_BATTLE_ON_DEATH, NEUTRAL, StatusEffects.EndBattleOnDeathEffect)
__END_BATTLE_ON_DEATH.setDefaults(rounds=NO_ROUNDS)

__END_BATTLE_ON_DEATH = StatusEffectDefinition(SEE.EFFECT_PREVENT_DEATH, NEUTRAL, StatusEffects.EndBattleOnDeathEffect)
__END_BATTLE_ON_DEATH.setDefaults(rounds=NO_ROUNDS)

__SKELECOG = StatusEffectDefinition(SEE.EFFECT_SKELECOG, BUFF, StatusEffects.SkelecogStatusEffect)
__SKELECOG.setDefaults(rounds=NO_ROUNDS, extraArgs=(-1, True, 1.0))
__SKELECOG.setIconProperties('skelecog')

__VIRTUAL_COG = StatusEffectDefinition(SEE.EFFECT_VIRTUAL_COG, BUFF, StatusEffects.SkelecogStatusEffect)
__VIRTUAL_COG.setDefaults(rounds=NO_ROUNDS, extraArgs=(-2, True, 1.0))
__VIRTUAL_COG.setIconProperties('virtual')

__EFFECT_MINIBOSS = StatusEffectDefinition(SEE.EFFECT_MINIBOSS, BUFF, StatusEffects.ToonRewardImmunityStatusEffect)
__EFFECT_MINIBOSS.setDefaults(rounds=NO_ROUNDS)
__EFFECT_MINIBOSS.setIconProperties(icon='tie', iconScale=0.95)

__JUST_DODGED_SOAK = StatusEffectDefinition(SEE.EFFECT_SUIT_JUST_DODGED_SOAK, NEUTRAL, StatusEffects.SuitJustDodgedSoakStatusEffect)
__JUST_DODGED_SOAK.setDefaults(rounds=THIS_ROUND)
__JUST_DODGED_SOAK.setIconProperties(icon=None, visible=False)

__JUST_DODGED_LURE = StatusEffectDefinition(SEE.EFFECT_SUIT_JUST_DODGED_LURE, NEUTRAL, StatusEffects.AttackEffectivenessStatusEffect)
__JUST_DODGED_LURE.setDefaults(rounds=THIS_ROUND, extraArgs=(0.75, 2))
__JUST_DODGED_LURE.setIconProperties(icon=None, visible=False)

__GAG_TRACKS_DISABLED = StatusEffectDefinition(SEE.EFFECT_DISABLE_GAG_TRACKS, NEUTRAL, StatusEffects.GagTracksDisabled)
__GAG_TRACKS_DISABLED.setDefaults(rounds=NO_ROUNDS, extraArgs=(*[0] * len(BattleGlobals.Tracks),))

__GAG_LEVELS_DISABLED = StatusEffectDefinition(SEE.EFFECT_DISABLE_GAG_LEVELS, NEUTRAL, StatusEffects.GagLevelsDisabled)
__GAG_LEVELS_DISABLED.setDefaults(rounds=NO_ROUNDS, extraArgs=(*[0] * (BattleGlobals.MAX_LEVEL_INDEX + 1),))

__COUNTERFEIT_CONTAINER = StatusEffectDefinition(SEE.EFFECT_COUNTERFEIT_CONTAINER, NEUTRAL, StatusEffects.CounterfeitContainer)
__COUNTERFEIT_CONTAINER.setDefaults(rounds=NO_ROUNDS, extraArgs=(*[0] * ((BattleGlobals.MAX_LEVEL_INDEX + 1) * (len(BattleGlobals.Tracks))),))

__COUNTERFEIT_USAGE_CONTAINER = StatusEffectDefinition(SEE.EFFECT_COUNTERFEIT_USAGE_CONTAINER, NEUTRAL, StatusEffects.CounterfeitContainer)
__COUNTERFEIT_USAGE_CONTAINER.setDefaults(rounds=NO_ROUNDS, extraArgs=(*[0] * ((BattleGlobals.MAX_LEVEL_INDEX + 1) * (len(BattleGlobals.Tracks))),))
# endregion

# region Environmental Effect Definitions
__EFFECT_SOAK_TO_FROZEN = StatusEffectDefinition(SEE.EFFECT_SOAK_TO_FROZEN, DEBUFF, StatusEffects.SoakToFrozenStatusEffect)
__EFFECT_SOAK_TO_FROZEN.setDefaults(rounds=NO_ROUNDS)
__EFFECT_SOAK_TO_FROZEN.setIconProperties(icon=None, visible=False)
# endregion

# region Toontorial
__MANAGER_DESK_JOCKEY = StatusEffectDefinition(SEE.EFFECT_MANAGER_DESK_JOCKEY, BUFF, StatusEffects.DeskJockeyEffect)
__MANAGER_DESK_JOCKEY.setDefaults(rounds=NO_ROUNDS)

# region Taskline Minibosses Status Effects
__INK_DRAIN = StatusEffectDefinition(SEE.EFFECT_INK_DRAIN, DEBUFF, StatusEffects.AttackEffectivenessStatusEffect)
__INK_DRAIN.setDefaults(rounds=1, extraArgs=0.75)
__INK_DRAIN.setIconProperties('ink_drain')
__INK_DRAIN.setVisualEffectEnums(VisualEffectEnum.INK_DRAIN)

__OVERWHELMING_AUTHORITY = StatusEffectDefinition(SEE.EFFECT_OVERWHELMING_AUTHORITY, DEBUFF, StatusEffects.UnitesDisabledStatusEffect)
__OVERWHELMING_AUTHORITY.setDefaults(rounds=NO_ROUNDS)
__OVERWHELMING_AUTHORITY.setIconProperties('unite_cooldown')

__DISRUPTIVE_ADVERTISEMENT = StatusEffectDefinition(SEE.EFFECT_DISRUPTIVE_ADVERTISEMENT, BUFF, StatusEffects.DisruptiveAdvertisementEffect)
__DISRUPTIVE_ADVERTISEMENT.setDefaults(rounds=1, extraArgs=AttackEnum.MULTI_LEVEL_MARKETING)
__DISRUPTIVE_ADVERTISEMENT.setIconProperties('disruptive_advertisement')
__DISRUPTIVE_ADVERTISEMENT.setVisualEffectEnums(VisualEffectEnum.DISRUPTIVE_ADVERTISEMENT)

__MULTI_LEVEL_MARKETING = StatusEffectDefinition(SEE.EFFECT_MULTI_LEVEL_MARKETING, BUFF, StatusEffects.ExtraSuitAttacksStatusEffect)
__MULTI_LEVEL_MARKETING.setDefaults(rounds=NO_ROUNDS, extraArgs=(1, AttackEnum.GLOWER_POWER, True))
__MULTI_LEVEL_MARKETING.setIconProperties('extra_attacks')
__MULTI_LEVEL_MARKETING.setVisualEffectEnums(VisualEffectEnum.EXTRA_GLOWER_POWERS)

__AMBUSH_MARKETING = StatusEffectDefinition(SEE.EFFECT_AMBUSH_MARKETING, BUFF, StatusEffects.ExtraSuitAttacksStatusEffect)
__AMBUSH_MARKETING.setDefaults(rounds=NO_ROUNDS, extraArgs=(1, AttackEnum.GLOWER_POWER, False))
__AMBUSH_MARKETING.setIconProperties('extra_attacks')
__AMBUSH_MARKETING.setVisualEffectEnums(VisualEffectEnum.EXTRA_GLOWER_POWERS)

__GENERIC_EXTRA_ATTACKS = StatusEffectDefinition(SEE.EFFECT_GENERIC_EXTRA_ATTACKS, BUFF, StatusEffects.ExtraSuitAttacksStatusEffect)
__GENERIC_EXTRA_ATTACKS.setDefaults(rounds=NO_ROUNDS, extraArgs=(1, -1, True))
__GENERIC_EXTRA_ATTACKS.setIconProperties('extra_attacks')

__SUPERVISOR_INSURED = StatusEffectDefinition(SEE.EFFECT_SUPERVISOR_INSURED, BUFF, StatusEffects.SupervisorInsuredStatusEffect)
__SUPERVISOR_INSURED.setDefaults(rounds=NO_ROUNDS, extraArgs=(0, 1, 1.0))
__SUPERVISOR_INSURED.setIconProperties('insured')
# endregion

# region Generic Toon/Cog attack mod effects
__TOONS_ACCURACY_UP = StatusEffectDefinition(SEE.EFFECT_TOONS_ACCURACY_UP, BUFF, StatusEffects.AttackAccuracyStatusEffect)
__TOONS_ACCURACY_UP.setDefaults(rounds=2, extraArgs=(15, -1))
__TOONS_ACCURACY_UP.setIconProperties('toon_accuracy_up')
__TOONS_ACCURACY_UP.setVisualEffectEnums(VisualEffectEnum.TOONS_ACCURACY_UP)

__TOON_CHEER = StatusEffectDefinition(SEE.EFFECT_CHEER, BUFF, StatusEffects.AttackAccuracyStatusEffect)
__TOON_CHEER.setDefaults(rounds=THIS_ROUND, extraArgs=(10, -1))
__TOON_CHEER.setIconProperties('cheer')
__TOON_CHEER.setVisualEffectEnums(VisualEffectEnum.CHEER)

__COGS_DAMAGE_DOWN = StatusEffectDefinition(SEE.EFFECT_COGS_DAMAGE_DOWN, DEBUFF, StatusEffects.AttackEffectivenessStatusEffect)
__COGS_DAMAGE_DOWN.setDefaults(rounds=2, extraArgs=0.6)
__COGS_DAMAGE_DOWN.setIconProperties(('attack', 'suit_damage_down'))
__COGS_DAMAGE_DOWN.setVisualEffectEnums(VisualEffectEnum.COGS_DAMAGE_DOWN)
# endregion

# region OCLO Status Effects
__LITIGATOR_MANAGER = StatusEffectDefinition(SEE.EFFECT_LITIGATOR_MANAGER, BUFF, StatusEffects.LitigatorManagerStatusEffect)
__LITIGATOR_MANAGER.setDefaults(rounds=NO_ROUNDS, extraArgs=0)

__STENOGRAPHER_MANAGER = StatusEffectDefinition(SEE.EFFECT_STENOGRAPHER_MANAGER, BUFF, StatusEffects.StenographerManagerStatusEffect)
__STENOGRAPHER_MANAGER.setDefaults(rounds=NO_ROUNDS, extraArgs=0)

__CASE_MANAGER_MANAGER = StatusEffectDefinition(SEE.EFFECT_CASE_MANAGER_MANAGER, BUFF, StatusEffects.CaseManagerManagerStatusEffect)
__CASE_MANAGER_MANAGER.setDefaults(rounds=NO_ROUNDS, extraArgs=0)

__SCAPEGOAT_MANAGER = StatusEffectDefinition(SEE.EFFECT_SCAPEGOAT_MANAGER, BUFF, StatusEffects.ScapegoatManagerStatusEffect)
__SCAPEGOAT_MANAGER.setDefaults(rounds=NO_ROUNDS, extraArgs=0)

__CASE_MANAGER_HOT = StatusEffectDefinition(SEE.EFFECT_CASE_MANAGER_HOT, BUFF, StatusEffects.InsuranceStatusEffect)
__CASE_MANAGER_HOT.setDefaults(rounds=2, extraArgs=(50, 1, 2.0))
__CASE_MANAGER_HOT.setIconProperties('heal_over_time')

__CASE_MANAGER_DOT = StatusEffectDefinition(SEE.EFFECT_CASE_MANAGER_DOT, DEBUFF, StatusEffects.LegalBindingsStatusEffect)
__CASE_MANAGER_DOT.setDefaults(rounds=2, extraArgs=20)
__CASE_MANAGER_DOT.setIconProperties('damage_over_time')

__VULNERABLE = StatusEffectDefinition(SEE.EFFECT_VULNERABLE, DEBUFF, StatusEffects.AvatarTakeModifiedDamageStatusEffect)
__VULNERABLE.setDefaults(rounds=2, extraArgs=1.20)
__VULNERABLE.setIconProperties('vulnerable')
__VULNERABLE.setVisualEffectEnums(VisualEffectEnum.VULNERABLE)

__SANCTIONED = StatusEffectDefinition(SEE.EFFECT_SANCTIONED, DEBUFF, StatusEffects.AttackEffectivenessStatusEffect)
__SANCTIONED.setDefaults(rounds=2, extraArgs=0.50)
__SANCTIONED.setIconProperties('toon_damage_down')

__COURT_RECORD = StatusEffectDefinition(SEE.EFFECT_COURT_RECORD, DEBUFF, StatusEffects.UseGagLevelSenderStatusEffect)
__COURT_RECORD.setDefaults(rounds=NO_ROUNDS, extraArgs=(4, 0, BEG.EVENT_LT_STENOG_TRIGGER_COURT_RECORD_DAMAGE))
__COURT_RECORD.setIconProperties('backfire')

__SCAPEGOAT_RAGE = StatusEffectDefinition(SEE.EFFECT_SCAPEGOAT_RAGE, BUFF, StatusEffects.ScapegoatRageStatusEffect)
__SCAPEGOAT_RAGE.setDefaults(rounds=NO_ROUNDS, extraArgs=(0, 0, 0))
__SCAPEGOAT_RAGE.setIconProperties(('defense_mode', 'rage_mode'))

__SCAPEGOAT_DAMAGE_TAKEN_DOWN = StatusEffectDefinition(SEE.EFFECT_SCAPEGOAT_DAMAGE_TAKEN_DOWN, BUFF, StatusEffects.ScapegoatDamageTakenDownStatusEffect)
__SCAPEGOAT_DAMAGE_TAKEN_DOWN.setDefaults(rounds=NO_ROUNDS, extraArgs=0.70)
# endregion

# region Event Status Effects
__COUNT_ERCLAIM = StatusEffectDefinition(SEE.EFFECT_COUNT_ERCLAIM, BUFF, StatusEffects.CountErclaimStatusEffect)
__COUNT_ERCLAIM.setDefaults(rounds=NO_ROUNDS, extraArgs=0)

__COUNT_CREEP = StatusEffectDefinition(SEE.EFFECT_COUNT_CREEP, BUFF, StatusEffects.CountCreepStatusEffect)
__COUNT_CREEP.setDefaults(rounds=NO_ROUNDS)
__COUNT_CREEP.setIconProperties('scope_creep')

__COUNT_ERFIT = StatusEffectDefinition(SEE.EFFECT_COUNT_ERFIT, BUFF, StatusEffects.CountErfitStatusEffect)
__COUNT_ERFIT.setDefaults(rounds=NO_ROUNDS)

__RIPPED = StatusEffectDefinition(SEE.EFFECT_RIPPED, BUFF, StatusEffects.AdditiveDamageBoostStatusEffect)
__RIPPED.setDefaults(extraArgs=[2])
__RIPPED.setIconProperties('ripped')

__OVERCLOCKED_FOREMAN = StatusEffectDefinition(SEE.EFFECT_OVERCLOCKED_FOREMAN, BUFF, StatusEffects.OverclockedForemanStatusEffect)
__OVERCLOCKED_FOREMAN.setDefaults(rounds=NO_ROUNDS)

__ERFIT_GODMODE = StatusEffectDefinition(SEE.EFFECT_ERFIT_GODMODE, BUFF, StatusEffects.AvatarTakeModifiedDamageStatusEffect)
__ERFIT_GODMODE.setDefaults(rounds=NO_ROUNDS, extraArgs=5)
__ERFIT_GODMODE.setIconProperties(icon=None, visible=False)

__MANAGER_HIGH_ROLLER = StatusEffectDefinition(SEE.EFFECT_MANAGER_HIGH_ROLLER, BUFF, StatusEffects.HighRollerStatusEffectBase)
__MANAGER_HIGH_ROLLER.setDefaults(rounds=NO_ROUNDS, extraArgs=(StatusEffects.InstanceMercStatusEffectBase.NORMAL,))

__HIGH_ROLLER_SHOW_HOST = StatusEffectDefinition(SEE.EFFECT_SHOW_HOST, BUFF, StatusEffects.HighRollerShowHostEffect)
__HIGH_ROLLER_SHOW_HOST.setDefaults(rounds=NO_ROUNDS)

__HIGH_ROLLER_COMMERCIAL = StatusEffectDefinition(SEE.EFFECT_COMMERCIAL, BUFF, StatusEffects.StatusEffectBase)
__HIGH_ROLLER_COMMERCIAL.setDefaults(rounds=2)
__HIGH_ROLLER_COMMERCIAL.setIconProperties(icon='insured')
__HIGH_ROLLER_COMMERCIAL.setVisualEffectEnums(VisualEffectEnum.HIGHROLLER_COMMERCIAL)

__HOLLYWOOD_STAR = StatusEffectDefinition(SEE.EFFECT_HOLLYWOOD_STAR, BUFF, StatusEffects.HollywoodStarStatusEffect)
__HOLLYWOOD_STAR.setDefaults(extraArgs=0)

__HARMONIOUS_COLORS = StatusEffectDefinition(SEE.EFFECT_HARMONIOUS_COLORS, BUFF, StatusEffects.HarmoniousColorsEffect)
__HARMONIOUS_COLORS.setDefaults(rounds=NO_ROUNDS, extraArgs=(1.0, 1.0))
__HARMONIOUS_COLORS.setIconProperties(icon='harmonious_colors', iconScale=0.925)

__QUESTION = StatusEffectDefinition(SEE.EFFECT_QUESTION, BUFF, StatusEffects.HighRollerQuestionEffect)

__TRIVIA = StatusEffectDefinition(SEE.EFFECT_TRIVIA, BUFF, StatusEffects.FlunkyTriviaEffect)
__TRIVIA.setDefaults(rounds=THIS_ROUND, extraArgs=(AttackEnum.TOON_NO_ATTACK, -1, -1))
__TRIVIA.setIconProperties(icon='attack')

__PUZZLE = StatusEffectDefinition(SEE.EFFECT_PUZZLE, BUFF, StatusEffects.PuzzleShowEffect)
__PUZZLE.setDefaults(rounds=THIS_ROUND)
__PUZZLE.setIconProperties(icon='attack')

__SHUFFLE = StatusEffectDefinition(SEE.EFFECT_SHUFFLE, BUFF, StatusEffects.CogShuffleEffect)
__SHUFFLE.setDefaults(rounds=THIS_ROUND, extraArgs=(AttackEnum.TOON_NO_ATTACK,))
__SHUFFLE.setIconProperties(icon='attack')

__HIGHROLLER_CLONE = StatusEffectDefinition(SEE.EFFECT_HIGHROLLER_CLONE, BUFF, StatusEffects.HighRollerCloneStatusEffect)
__HIGHROLLER_CLONE.setDefaults(rounds=NO_ROUNDS)

__RAISING_THE_ANTE = StatusEffectDefinition(SEE.EFFECT_RAISING_THE_ANTE, BUFF, StatusEffects.RaisingTheAnteEffect)
__RAISING_THE_ANTE.setDefaults(rounds=NO_ROUNDS, extraArgs=-200)
__RAISING_THE_ANTE.setIconProperties('raise_the_ante', iconScale=0.96)

__HIGHROLLER_SHIELD_SUIT = StatusEffectDefinition(SEE.EFFECT_HIGHROLLER_SHIELD_SUIT, BUFF, StatusEffects.StatusEffectBase)
__HIGHROLLER_SHIELD_SUIT.setDefaults(rounds=NO_ROUNDS)
__HIGHROLLER_SHIELD_SUIT.setIconProperties('shield', iconScale=0.85)

__FAKE_SOAKED = StatusEffectDefinition(SEE.EFFECT_FAKE_SOAKED, DEBUFF, StatusEffects.FakeSoakStatusEffect)
__FAKE_SOAKED.setDefaults(rounds=3)
__FAKE_SOAKED.setIconProperties('soaked')

__PIP_COUNTER = StatusEffectDefinition(SEE.EFFECT_PIP_COUNTER, BUFF, StatusEffects.PipCounterEffect)
__PIP_COUNTER.setDefaults(rounds=1)
__PIP_COUNTER.setIconProperties(icon=None, iconScale=0.65)

__PIP_DISCOUNT = StatusEffectDefinition(SEE.EFFECT_PIP_DISCOUNT, BUFF, StatusEffects.PipDiscountEffect)
__PIP_DISCOUNT.setDefaults(rounds=0, extraArgs=(2,))

__DICE_COOLDOWN = StatusEffectDefinition(SEE.EFFECT_DICE_COOLDOWN, BUFF, StatusEffects.DiceCooldownEffect)
__DICE_COOLDOWN.setIconProperties('attack', visible=False)
__DICE_COOLDOWN.setDefaults(rounds=0, extraArgs=(-1,))

__HR_UNTOUCHABLE = StatusEffectDefinition(SEE.EFFECT_HR_UNTOUCHABLE, BUFF, StatusEffects.HighRollerUntouchableStatusEffect)
__HR_UNTOUCHABLE.setDefaults(rounds=123)
__HR_UNTOUCHABLE.setVisualEffectEnums(VisualEffectEnum.HR_UNTOUCHABLE)
__HR_UNTOUCHABLE.setIconProperties('insured', visible=False)

__AITH_DAMAGE_TAKEN_UP = StatusEffectDefinition(SEE.EFFECT_AITH_DAMAGE_TAKEN_UP, DEBUFF, StatusEffects.AceInTheHoleVulnerabilityEffect)
__AITH_DAMAGE_TAKEN_UP.setDefaults(rounds=-1, extraArgs=(1.15,))
__AITH_DAMAGE_TAKEN_UP.setIconProperties(icon='broken_shield', iconScale=0.9)

__HR_TOONS_UNLOCKED_GAGS = StatusEffectDefinition(SEE.EFFECT_HR_TOON_GAGS_UNLOCKED, NEUTRAL, StatusEffects.HighRollerToonGagsUnlocked)

__SOAK_POWERED_RESISTANCE = StatusEffectDefinition(SEE.EFFECT_SOAK_POWERED_RESISTANCE, BUFF, StatusEffects.AvatarTakeModifiedDamageStatusEffect)
__SOAK_POWERED_RESISTANCE.setDefaults(rounds=-1, extraArgs=0.5)
__SOAK_POWERED_RESISTANCE.setIconProperties(icon='shield', visible=False)

__HIGH_ROLLER_MINIGAME_HOST = StatusEffectDefinition(SEE.EFFECT_HIGHROLLER_MINIGAME_HOST, BUFF, StatusEffects.StatusEffectBase)
__HIGH_ROLLER_MINIGAME_HOST.setDefaults(rounds=1)
__HIGH_ROLLER_MINIGAME_HOST.setIconProperties(icon='tie', iconScale=0.95)

# region overclocked find the family
__FTF_SUPERVISOR_INSURED = StatusEffectDefinition(SEE.EFFECT_FTF_SUPERVISOR_INSURED, BUFF, StatusEffects.FindTheFamilySupervisorLifeInsurance)
__FTF_SUPERVISOR_INSURED.setDefaults(rounds=NO_ROUNDS, extraArgs=(200, 1, 1.0))
__FTF_SUPERVISOR_INSURED.setIconProperties('insured')

__FTF_NUCLEAR = StatusEffectDefinition(SEE.EFFECT_FTF_NUCLEAR, BUFF, StatusEffects.FindTheFamilyNuclear)
__FTF_DUALCORE = StatusEffectDefinition(SEE.EFFECT_FTF_DUALCORE, BUFF, StatusEffects.FindTheFamilySuitFinalDamageBoost)
__FTF_DUALCORE.setDefaults(rounds=NO_ROUNDS, extraArgs=(2.0, 2))
__FTF_DUALCORE.setIconProperties(icon=None, iconScale=0.94)
__FTF_PRISMATIC_TOON = StatusEffectDefinition(SEE.EFFECT_FTF_PRISMATIC_TOON, BUFF, StatusEffects.FindTheFamilyFinalDamageBoost)
__FTF_PRISMATIC_TOON.setDefaults(rounds=NO_ROUNDS, extraArgs=(3.0, 2))
__FTF_PRISMATIC_TOON.setIconProperties(icon=None, iconScale=0.94)

__FTF_FOREMAN_CONTRACTOR = StatusEffectDefinition(SEE.EFFECT_FTF_FOREMAN_CONTRACTOR, BUFF, StatusEffects.FindTheFamilyContractorForeman)
__FTF_FOREMAN_CONTRACTOR_TANGO = StatusEffectDefinition(SEE.EFFECT_FTF_FOREMAN_CONTRACTOR_TANGO, BUFF, StatusEffects.FindTheFamilyContractorDancePartnerStatusEffect)
__FTF_FOREMAN_REDTAPE = StatusEffectDefinition(SEE.EFFECT_FTF_FOREMAN_REDTAPE, BUFF, StatusEffects.FindTheFamilyRedTapeForeman)
__FTF_FOREMAN_SNIPER = StatusEffectDefinition(SEE.EFFECT_FTF_FOREMAN_SNIPER, BUFF, StatusEffects.FindTheFamilySniperForeman)
__FTF_FOREMAN_SLEEPY = StatusEffectDefinition(SEE.EFFECT_FTF_FOREMAN_SLEEPY, BUFF, StatusEffects.FindTheFamilySleepyForeman)
__FTF_FOREMAN_SLEEPY_POWER_NAP = StatusEffectDefinition(SEE.EFFECT_FTF_FOREMAN_SLEEPY_POWER_NAP, BUFF, StatusEffects.FindTheFamilySleepForemanPowerNap)
__FTF_FOREMAN_SLEEPY_POWER_NAP.setDefaults(rounds=1, extraArgs=(1.0, 1.0, 600))
__FTF_FOREMAN_SLEEPY_POWER_NAP.setVisualEffectEnums(VisualEffectEnum.POWER_NAP)
__FTF_FOREMAN_EXPLOSIVE = StatusEffectDefinition(SEE.EFFECT_FTF_FOREMAN_EXPLOSIVE, BUFF, StatusEffects.FindTheFamilyExplosiveForeman)
__FTF_FOREMAN_EXPLOSIVE.setDefaults(rounds=1)
__FTF_FOREMAN_BURNING = StatusEffectDefinition(SEE.EFFECT_FTF_FOREMAN_BURNING, BUFF, StatusEffects.FindTheFamilyBurningForeman)
__FTF_FOREMAN_BURNING_SMOKED = StatusEffectDefinition(SEE.EFFECT_FTF_FOREMAN_BURNING_SMOKED, DEBUFF, StatusEffects.FindTheFamilyBurningForemanDamageOverTime)
__FTF_FOREMAN_BURNING_SMOKED.setDefaults(rounds=1, extraArgs=(0.15,))
__FTF_FOREMAN_BURNING_SMOKED.setIconProperties('fog', iconScale=1.05)
__FTF_FOREMAN_BURNING_SMOKED.setVisualEffectEnums(VisualEffectEnum.TRIAL_BY_FIRE)

__FTF_SUPERVISOR_ABSORPTION = StatusEffectDefinition(SEE.EFFECT_FTF_SUPERVISOR_ABSORPTION, BUFF, StatusEffects.FindTheFamilySpongySupervisor)
__FTF_SUPERVISOR_ABSORPTION.setDefaults(rounds=NO_ROUNDS, extraArgs=(0.67, 0))
__FTF_SUPERVISOR_FRAUD = StatusEffectDefinition(SEE.EFFECT_FTF_SUPERVISOR_FRAUD, BUFF, StatusEffects.FindTheFamilyFraudSupervisor)
__FTF_SUPERVISOR_ABACUS = StatusEffectDefinition(SEE.EFFECT_FTF_SUPERVISOR_ABACUS, BUFF, StatusEffects.FindTheFamilyAbacusSupervisor)
__FTF_SUPERVISOR_ABACUS.setDefaults(rounds=NO_ROUNDS, extraArgs=(10, 0))
__FTF_SUPERVISOR_CONFUSED = StatusEffectDefinition(SEE.EFFECT_FTF_SUPERVISOR_CONFUSED, BUFF, StatusEffects.FindTheFamilyConfusedSupervisor)
__FTF_SUPERVISOR_CONTROLLING = StatusEffectDefinition(SEE.EFFECT_FTF_SUPERVISOR_CONTROLLING, BUFF, StatusEffects.FindTheFamilyControllingSupervisor)
__FTF_SUPERVISOR_ACCOUNTANT = StatusEffectDefinition(SEE.EFFECT_FTF_SUPERVISOR_ACCOUNTANT, BUFF, StatusEffects.FindTheFamilyAccountantSupervisor)
__FTF_SUPERVISOR_ACCOUNTANT.setDefaults(rounds=NO_ROUNDS, extraArgs=(2,))

__FTF_ATTORNEY_SNEAKY = StatusEffectDefinition(SEE.EFFECT_FTF_ATTORNEY_SNEAKY, BUFF, StatusEffects.FindTheFamilySneakyAttorney)
__FTF_ATTORNEY_CHRONO = StatusEffectDefinition(SEE.EFFECT_FTF_ATTORNEY_CHRONO, BUFF, StatusEffects.FindTheFamilyChronoAttorney)
__FTF_ATTORNEY_OVERSEER = StatusEffectDefinition(SEE.EFFECT_FTF_ATTORNEY_OVERSEER, BUFF, StatusEffects.FindTheFamilyOverseerAttorney)
__FTF_ATTORNEY_RUSHJOB = StatusEffectDefinition(SEE.EFFECT_FTF_ATTORNEY_RUSHJOB, BUFF, StatusEffects.FindTheFamilyRushJobAttorney)
__FTF_ATTORNEY_MONOLITH = StatusEffectDefinition(SEE.EFFECT_FTF_ATTORNEY_MONOLITH, BUFF, StatusEffects.FindTheFamilyMonolithAttorney)
__FTF_ATTORNEY_OMNIPOTENT = StatusEffectDefinition(SEE.EFFECT_FTF_ATTORNEY_OMNIPOTENT, BUFF, StatusEffects.FindTheFamilyOmnipotentAttorney)

__FTF_PRESIDENT_MULLIGAN = StatusEffectDefinition(SEE.EFFECT_FTF_PRESIDENT_MULLIGAN, BUFF, StatusEffects.FindTheFamilyMulliganClubPresident)
__FTF_PRESIDENT_CHIPFAN = StatusEffectDefinition(SEE.EFFECT_FTF_PRESIDENT_CHIPFAN, BUFF, StatusEffects.FindTheFamilyChipFanClubPresident)
__FTF_PRESIDENT_ANCIENT = StatusEffectDefinition(SEE.EFFECT_FTF_PRESIDENT_ANCIENT, BUFF, StatusEffects.FindTheFamilyAncientClubPresident)
__FTF_PRESIDENT_PUZZLING = StatusEffectDefinition(SEE.EFFECT_FTF_PRESIDENT_PUZZLING, BUFF, StatusEffects.FindTheFamilyPuzzlingClubPresident)
__FTF_PRESIDENT_PUZZLING_CONFUSED = StatusEffectDefinition(SEE.EFFECT_FTF_PRESIDENT_PUZZLING_CONFUSED, DEBUFF, StatusEffects.FindTheFamilyPuzzlingClubPresidentConfused)
__FTF_PRESIDENT_PUZZLING_CONFUSED.setDefaults(rounds=THIS_ROUND, extraArgs=(*[0] * ((BattleGlobals.MAX_LEVEL_INDEX + 1) * (len(BattleGlobals.Tracks))),))
__FTF_PRESIDENT_PUZZLING_CONFUSED.setIconProperties('confusion')
__FTF_PRESIDENT_PUZZLING_CONFUSED.setVisualEffectEnums(VisualEffectEnum.CONFUSION)
__FTF_PRESIDENT_SHIVERING = StatusEffectDefinition(SEE.EFFECT_FTF_PRESIDENT_SHIVERING, BUFF, StatusEffects.FindTheFamilyShiveringClubPresident)
__FTF_PRESIDENT_HIGHSTAKES = StatusEffectDefinition(SEE.EFFECT_FTF_PRESIDENT_HIGHSTAKES, BUFF, StatusEffects.FindTheFamilyHighStakesClubPresident)
# endregion
# endregion

# region Flags
__FLAG_BASE = StatusEffectDefinition(SEE.FLAG_BASE, BUFF, StatusEffects.FlagBase)
__FLAG_BASE.setFlag()

__FLAG_EMPOWER = StatusEffectDefinition(SEE.FLAG_EMPOWER, BUFF, StatusEffects.FlagEmpower)
__FLAG_EMPOWER.setFlag()

__ATTACK_TARGET_GHOSTWRITER = StatusEffectDefinition(SEE.TARGET_LIST_GHOSTWRITER, NEUTRAL, StatusEffects.AttackTargetGhostwriter)
__ATTACK_TARGET_GHOSTWRITER.setFlag()
# endregion

# region Street Merc Status Effects
__MANAGER_DUCK_SHUFFLER = StatusEffectDefinition(SEE.EFFECT_MANAGER_DUCK_SHUFFLER, BUFF, StatusEffects.DuckShufflerEffect)
__MANAGER_DUCK_SHUFFLER.setDefaults(rounds=NO_ROUNDS, extraArgs=(1.0, 1.0))

__MANAGER_DEEP_DIVER = StatusEffectDefinition(SEE.EFFECT_MANAGER_DEEP_DIVER, BUFF, StatusEffects.DeepDiverEffect)
__MANAGER_DEEP_DIVER.setDefaults(rounds=NO_ROUNDS)

__DIVING = StatusEffectDefinition(SEE.EFFECT_DIVING, BUFF, StatusEffects.DivingStatusEffect)
__DIVING.setDefaults(rounds=NO_ROUNDS, extraArgs=(False,))
__DIVING.setVisualEffectEnums(VisualEffectEnum.DIVING)
__DIVING.setIconProperties('diving')

__MANAGER_GATEKEEPER = StatusEffectDefinition(SEE.EFFECT_MANAGER_GATEKEEPER, BUFF, StatusEffects.GatekeeperManagerStatusEffect)
__MANAGER_GATEKEEPER.setDefaults(rounds=NO_ROUNDS, extraArgs=(1.0, 0.25))
__MANAGER_GATEKEEPER.setIconProperties('shield', iconScale=0.85)

__MANAGER_BELLRINGER = StatusEffectDefinition(SEE.EFFECT_MANAGER_BELLRINGER, BUFF, StatusEffects.BellringerStatusEffect)
__MANAGER_BELLRINGER.setDefaults(rounds=NO_ROUNDS)

__BELLRINGER_FODDER_EXPLOSION = StatusEffectDefinition(SEE.EFFECT_BELLRINGER_FODDER_EXPLOSION, DEBUFF, StatusEffects.BellringerFodderExplosionEffect)
__BELLRINGER_FODDER_EXPLOSION.setDefaults(rounds=NO_ROUNDS)
__BELLRINGER_FODDER_EXPLOSION.setIconProperties('union_bust')

__MANAGER_MOUTHPIECE = StatusEffectDefinition(SEE.EFFECT_MANAGER_MOUTHPIECE, BUFF, StatusEffects.MouthpieceStatusEffect)
__MANAGER_MOUTHPIECE.setIconProperties(icon='cookie_shield')
__MANAGER_MOUTHPIECE.setDefaults(rounds=NO_ROUNDS)
__MANAGER_MOUTHPIECE.setVisualEffectEnums(VisualEffectEnum.BAKERY_AFICIONADO)

__MANAGER_MOUTHPIECE_BONUS = StatusEffectDefinition(SEE.EFFECT_MOUTHPIECE_BONUS, BUFF, StatusEffects.MouthpieceBonusFlag)
__MANAGER_MOUTHPIECE_BONUS.setDefaults(rounds=NO_ROUNDS)
__MANAGER_MOUTHPIECE_BONUS.setIconProperties(icon='cookie_shield')
# __MANAGER_MOUTHPIECE_BONUS.setVisualEffectEnums(VisualEffectEnum.MOUTHPIECE_BONUS)

__RED_THREAD = StatusEffectDefinition(SEE.EFFECT_RED_THREAD, DEBUFF, StatusEffects.RedThreadStatusEffect)
# __RED_THREAD.setVisualEffectEnums(VisualEffectEnum.RED_THREAD)
__RED_THREAD.setIconProperties(icon='red_thread')
__RED_THREAD.setDefaults(rounds=1)

__RED_THREAD_TANGLED = StatusEffectDefinition(SEE.EFFECT_RED_THREAD_TANGLED, DEBUFF, StatusEffects.RedThreadTangledStatusEffect)
# __RED_THREAD_TANGLED.setVisualEffectEnums(VisualEffectEnum.RED_THREAD)
__RED_THREAD_TANGLED.setIconProperties(icon='red_thread')
__RED_THREAD_TANGLED.setDefaults(rounds=1)

__MANAGER_FIRESTARTER = StatusEffectDefinition(SEE.EFFECT_MANAGER_FIRESTARTER, BUFF, StatusEffects.FirestarterStatusEffect)
__MANAGER_FIRESTARTER.setDefaults(rounds=NO_ROUNDS, extraArgs=(0, 1.0))
__MANAGER_FIRESTARTER.setIconProperties(icon='pyromaniac')

__MANAGER_FEATHERBEDDER = StatusEffectDefinition(SEE.EFFECT_MANAGER_FEATHERBEDDER, BUFF, StatusEffects.FeatherbedderStatusEffect)
__MANAGER_FEATHERBEDDER.setDefaults(rounds=NO_ROUNDS, extraArgs=(1.0, 1.0))
__MANAGER_FEATHERBEDDER.setVisualEffectEnums(VisualEffectEnum.OVERHIRE)
__MANAGER_FEATHERBEDDER.setIconProperties('hands')

__POWER_NAP = StatusEffectDefinition(SEE.EFFECT_POWER_NAP, BUFF, StatusEffects.PowerNapStatusEffect)
__POWER_NAP.setDefaults(rounds=1, extraArgs=(1.0, 1.0, 500))
__POWER_NAP.setVisualEffectEnums(VisualEffectEnum.POWER_NAP)

__POWER_NAP_KILL_DMG_BOOST = StatusEffectDefinition(SEE.EFFECT_POWER_NAP_KILL_DMG_BOOST, BUFF, StatusEffects.AdditiveDamageBoostNoToonup)
__POWER_NAP_KILL_DMG_BOOST.setDefaults(rounds=NO_ROUNDS, extraArgs=3)
__POWER_NAP_KILL_DMG_BOOST.setIconProperties('toon_damage_up')

__PEACEFUL_SLUMBER = StatusEffectDefinition(SEE.EFFECT_PEACEFUL_SLUMBER, BUFF, StatusEffects.PeacefulSlumberEffect)
__PEACEFUL_SLUMBER.setDefaults(rounds=NO_ROUNDS, extraArgs=1.0)

__BACKBURNER = StatusEffectDefinition(SEE.EFFECT_BACKBURNER, BUFF, StatusEffects.BackburnerStatusEffect)
__BACKBURNER.setDefaults(rounds=NO_ROUNDS, extraArgs=(1.0, 1.0, -1, True, 0.05, 0.05))
__BACKBURNER.setIconProperties('backburner')
__BACKBURNER.setVisualEffectEnums(VisualEffectEnum.BACKBURNER)

__PEELING_THE_BARK = StatusEffectDefinition(SEE.EFFECT_PEELING_THE_BARK, DEBUFF, StatusEffects.AvatarTakeModifiedDamageStatusEffect)
__PEELING_THE_BARK.setDefaults(rounds=0, extraArgs=1.75)
__PEELING_THE_BARK.setIconProperties('broken_shield', iconScale=0.9)
__PEELING_THE_BARK.setVisualEffectEnums(VisualEffectEnum.PEELED)

__PEELING_THE_BARK_SUIT = StatusEffectDefinition(SEE.EFFECT_PEELING_THE_BARK_SUIT, BUFF, StatusEffects.PeelingTheBark)
__PEELING_THE_BARK_SUIT.setDefaults(rounds=THIS_ROUND, extraArgs=(1, False))

__WOODCHIPPER = StatusEffectDefinition(SEE.EFFECT_WOODCHIPPER, DEBUFF, StatusEffects.WoodchipperStatusEffect)
__WOODCHIPPER.setDefaults(rounds=1, extraArgs=12)
__WOODCHIPPER.setIconProperties('woodchipped')
__WOODCHIPPER.setVisualEffectEnums(VisualEffectEnum.WOODCHIPPED)
# endregion

# region Instance Merc Status Effects
__MANAGER_PRETHINKER = StatusEffectDefinition(SEE.EFFECT_MANAGER_PRETHINKER, BUFF, StatusEffects.PrethinkerStatusEffectBase)
__MANAGER_PRETHINKER.setDefaults(rounds=NO_ROUNDS, extraArgs=(StatusEffects.InstanceMercStatusEffectBase.NORMAL, 0))
__MANAGER_PRETHINKER.setIconProperties(icon='brain')

__MANAGER_CHAINSAW_CONSULTANT = StatusEffectDefinition(SEE.EFFECT_MANAGER_CHAINSAW_CONSULTANT, BUFF, StatusEffects.ChainsawConsultantStatusEffectBase)
__MANAGER_CHAINSAW_CONSULTANT.setDefaults(
    rounds=NO_ROUNDS, 
    extraArgs=(
        StatusEffects.InstanceMercStatusEffectBase.NORMAL, 
        1.0, 1.0, 0, 1, 0, 0.5
    )
)
__MANAGER_CHAINSAW_CONSULTANT.setIconProperties('chainsaw')

__EFFECT_CHAIN_LINKED = StatusEffectDefinition(SEE.EFFECT_CHAIN_LINKED, BUFF, StatusEffects.ChainLinkedStatusEffect)
__EFFECT_CHAIN_LINKED.setDefaults(rounds=NO_ROUNDS, extraArgs=1)
__EFFECT_CHAIN_LINKED.setIconProperties(icon='chain_linked')
__EFFECT_CHAIN_LINKED.setVisualEffectEnums(VisualEffectEnum.CHAIN_LINKED)

__EFFECT_KICKBACK = StatusEffectDefinition(SEE.EFFECT_KICKBACK, DEBUFF, StatusEffects.AvatarTakeModifiedDamageStatusEffect)
__EFFECT_KICKBACK.setDefaults(rounds=3, extraArgs=1.5)
__EFFECT_KICKBACK.setIconProperties(icon='kickback')

__EFFECT_SPARK_PLUG = StatusEffectDefinition(SEE.EFFECT_SPARK_PLUG, DEBUFF, StatusEffects.SparkPlugStatusEffect)
__EFFECT_SPARK_PLUG.setDefaults(rounds=2, extraArgs=20)
__EFFECT_SPARK_PLUG.setIconProperties('sparkplug')
__EFFECT_SPARK_PLUG.setVisualEffectEnums(VisualEffectEnum.SPARK_PLUG_DAMAGE)

__EFFECT_AGGRANDIZE = StatusEffectDefinition(SEE.EFFECT_AGGRANDIZE, DEBUFF, StatusEffects.AggrandizeStatusEffect)
__EFFECT_AGGRANDIZE.setDefaults(rounds=NO_ROUNDS, extraArgs=0)
__EFFECT_AGGRANDIZE.setIconProperties(icon='damage_absorb')

__MANAGER_PACESETTER = StatusEffectDefinition(SEE.EFFECT_MANAGER_PACESETTER, BUFF, StatusEffects.PacesetterStatusEffectBase)
__MANAGER_PACESETTER.setDefaults(rounds=NO_ROUNDS, extraArgs=(StatusEffects.InstanceMercStatusEffectBase.NORMAL, 1.0, False))
__MANAGER_PACESETTER.setIconProperties(icon='mileaminute')

__MANAGER_MERC_GENERAL = StatusEffectDefinition(SEE.EFFECT_MANAGER_MERC, BUFF, StatusEffects.InstanceMercStatusEffectBase)
__MANAGER_MERC_GENERAL.setDefaults(rounds=NO_ROUNDS, extraArgs=(StatusEffects.InstanceMercStatusEffectBase.NORMAL,))

__MANAGER_MULTISLACKER = StatusEffectDefinition(SEE.EFFECT_MANAGER_MULTISLACKER, BUFF, StatusEffects.MultislackerStatusEffectBase)
__MANAGER_MULTISLACKER.setDefaults(rounds=NO_ROUNDS, extraArgs=(StatusEffects.InstanceMercStatusEffectBase.NORMAL,))

__MANAGER_RAINMAKER = StatusEffectDefinition(SEE.EFFECT_MANAGER_RAINMAKER, BUFF, StatusEffects.RainmakerStatusEffectBase)
__MANAGER_RAINMAKER.setDefaults(rounds=NO_ROUNDS, extraArgs=(StatusEffects.InstanceMercStatusEffectBase.NORMAL,))

__OIL_RAIN_HOT = StatusEffectDefinition(SEE.EFFECT_OIL_RAIN_HOT, BUFF, StatusEffects.OilRainHealStatusEffect)
__OIL_RAIN_HOT.setDefaults(rounds=2, extraArgs=(0, 1, 1.0))
__OIL_RAIN_HOT.setIconProperties('oilrain')

__OIL_RAIN_DOT = StatusEffectDefinition(SEE.EFFECT_OIL_RAIN_DOT, DEBUFF, StatusEffects.OilRainDamageStatusEffect)
__OIL_RAIN_DOT.setDefaults(rounds=2, extraArgs=(5))
__OIL_RAIN_DOT.setIconProperties('oilrain')

__FOG = StatusEffectDefinition(SEE.EFFECT_FOG, DEBUFF, StatusEffects.ObscureInformationStatusEffect)
__FOG.setDefaults(rounds=2)
__FOG.setIconProperties('fog')

__HEAVY_RAIN = StatusEffectDefinition(SEE.EFFECT_HEAVY_RAIN, BUFF, StatusEffects.HeavyRainStatusEffect)
__HEAVY_RAIN.setDefaults(rounds=2, extraArgs=(0.50, 120))
__HEAVY_RAIN.setIconProperties('heavyrain')

__HEAVY_RAIN_RAINMAKER = StatusEffectDefinition(SEE.EFFECT_HEAVY_RAIN_RAINMAKER, BUFF, StatusEffects.AttackIOModificationStatusEffect)
__HEAVY_RAIN_RAINMAKER.setDefaults(rounds=2, extraArgs=(1.05, 0.8))
__HEAVY_RAIN_RAINMAKER.setIconProperties('heavyrain')

__STORM_CELL = StatusEffectDefinition(SEE.EFFECT_STORM_CELL, BUFF, StatusEffects.StormCellStatusEffect)
__STORM_CELL.setDefaults(rounds=34)
__STORM_CELL.setIconProperties('stormcell')

__MANAGER_MAJOR_PLAYER = StatusEffectDefinition(SEE.EFFECT_MANAGER_MAJOR_PLAYER, BUFF, StatusEffects.MajorPlayerStatusEffect)
__MANAGER_MAJOR_PLAYER.setDefaults(rounds=NO_ROUNDS, extraArgs=(0, 0))

__STAR_OF_THE_SHOW = StatusEffectDefinition(SEE.EFFECT_STAR_OF_THE_SHOW, BUFF, StatusEffects.StarOfTheShowStatusEffect)
__STAR_OF_THE_SHOW.setDefaults(extraArgs=(10, 0))

__GUEST_VERSE = StatusEffectDefinition(SEE.EFFECT_GUEST_VERSE, BUFF, StatusEffects.GuestVerseStatusEffect)
__GUEST_VERSE.setDefaults(rounds=THIS_ROUND)

__VIRAL_SENSATION = StatusEffectDefinition(SEE.EFFECT_VIRAL_SENSATION, BUFF, StatusEffects.ViralSensationStatusEffect)
__VIRAL_SENSATION.setDefaults(rounds=2, extraArgs=(60, 8, 3))
__VIRAL_SENSATION.setIconProperties(icon='singing_blues', iconScale=0.9)

__SIPHON = StatusEffectDefinition(SEE.EFFECT_SIPHON, BUFF, StatusEffects.SiphonStatusEffect)
__SIPHON.setDefaults(rounds=1, extraArgs=(0.7, 3.0, 1.5))
__SIPHON.setIconProperties(icon='ink_drain')

__DANCE_PARTNER = StatusEffectDefinition(SEE.EFFECT_DANCE_PARTNER, BUFF, StatusEffects.DancePartnerStatusEffect)

__LAST_TAP = StatusEffectDefinition(SEE.EFFECT_LAST_TAP, BUFF, StatusEffects.StarOfTheShowStatusEffect)
__LAST_TAP.setDefaults(extraArgs=(5, 2))
__LAST_TAP.setIconProperties(icon='last_tap', iconScale=0.9)

__TOON_STAR_OF_THE_SHOW = StatusEffectDefinition(SEE.EFFECT_STAR_OF_THE_SHOW_TOON, BUFF, StatusEffects.AdditiveDamageBoostNoToonup)
__TOON_STAR_OF_THE_SHOW.setDefaults(extraArgs=15)

__MP_COGS_DAMAGE_DOWN = StatusEffectDefinition(SEE.EFFECT_MP_COGS_DAMAGE_DOWN, DEBUFF, StatusEffects.MajorPlayerPhaseTwoDamageDownStatusEffect)
__MP_COGS_DAMAGE_DOWN.setDefaults(rounds=NO_ROUNDS, extraArgs=0.8)

__MANAGER_WITCH_HUNTER = StatusEffectDefinition(SEE.EFFECT_MANAGER_WITCH_HUNTER, BUFF, StatusEffects.WitchHunterStatusEffect)
__MANAGER_WITCH_HUNTER.setDefaults(rounds=NO_ROUNDS, extraArgs=(StatusEffects.InstanceMercStatusEffectBase.NORMAL,))
__MANAGER_WITCH_HUNTER.setIconProperties(icon='mob')

__WILL_OF_THE_PEOPLE = StatusEffectDefinition(SEE.EFFECT_WILL_OF_THE_PEOPLE, BUFF, StatusEffects.WillOfThePeopleStatusEffect)
__WILL_OF_THE_PEOPLE.setDefaults(rounds=NO_ROUNDS, extraArgs=(0.5,))
__WILL_OF_THE_PEOPLE.setIconProperties(icon='shield', iconScale=0.85)

__TRIAL_BY_FIRE = StatusEffectDefinition(SEE.EFFECT_TRIAL_BY_FIRE, DEBUFF, StatusEffects.TrialByFireStatusEffect)
__TRIAL_BY_FIRE.setDefaults(rounds=2, extraArgs=.15)
__TRIAL_BY_FIRE.setVisualEffectEnums(VisualEffectEnum.TRIAL_BY_FIRE)
__TRIAL_BY_FIRE.setIconProperties('trialbyfire')

__BEWITCHMENT = StatusEffectDefinition(SEE.EFFECT_BEWITCHMENT, DEBUFF, StatusEffects.BewitchmentStatusEffect)
__BEWITCHMENT.setVisualEffectEnums(VisualEffectEnum.BEWITCHMENT)
__BEWITCHMENT.setDefaults(rounds=1, extraArgs=(1.75, True, True, 1.3, 1.2))
__BEWITCHMENT.setIconProperties(icon='bewitched')

__HIVEMIND = StatusEffectDefinition(SEE.EFFECT_HIVEMIND, BUFF, StatusEffects.HivemindEffect)
__HIVEMIND.setDefaults(rounds=NO_ROUNDS)
__HIVEMIND.setIconProperties(icon='mob')

# Custom one for this so we can make it neutral and not count for drop prestige
__WHUNTER_CAT_DEFENSE_MODIFIER = StatusEffectDefinition(SEE.EFFECT_WHUNTER_CAT_DEFENSE_MODIFIER, NEUTRAL, StatusEffects.SuitDefenseModifierStatusEffect)
__WHUNTER_CAT_DEFENSE_MODIFIER.setDefaults(rounds=NO_ROUNDS, extraArgs=(-20,))
__WHUNTER_CAT_DEFENSE_MODIFIER.setIconProperties('confusion')

# Satellite investor manager effects
__SATELLITE_INVESTOR_MANAGER = StatusEffectDefinition(SEE.EFFECT_SATELLITE_INVESTOR_MANAGER, BUFF, StatusEffects.SatelliteInvestorStatusEffectBase)
__SATELLITE_INVESTOR_MANAGER.setDefaults(rounds=NO_ROUNDS, extraArgs=(StatusEffects.InstanceMercStatusEffectBase.NORMAL,))

__MANAGER_CHARON = StatusEffectDefinition(SEE.EFFECT_MANAGER_CHARON, BUFF, StatusEffects.CharonStatusEffect)
__MANAGER_CHARON.setDefaults(rounds=NO_ROUNDS, extraArgs=(StatusEffects.CharonStatusEffect.NORMAL,))

__MANAGER_NIX = StatusEffectDefinition(SEE.EFFECT_MANAGER_NIX, BUFF, StatusEffects.NixStatusEffect)
__MANAGER_NIX.setDefaults(rounds=NO_ROUNDS, extraArgs=(StatusEffects.NixStatusEffect.NORMAL,))

__MANAGER_HYDRA = StatusEffectDefinition(SEE.EFFECT_MANAGER_HYDRA, BUFF, StatusEffects.HydraStatusEffect)
__MANAGER_HYDRA.setDefaults(rounds=NO_ROUNDS, extraArgs=(StatusEffects.HydraStatusEffect.NORMAL,))

__MANAGER_STYX = StatusEffectDefinition(SEE.EFFECT_MANAGER_STYX, BUFF, StatusEffects.StyxStatusEffect)
__MANAGER_STYX.setDefaults(rounds=NO_ROUNDS, extraArgs=(StatusEffects.StyxStatusEffect.NORMAL,))

__MANAGER_KERBEROS = StatusEffectDefinition(SEE.EFFECT_MANAGER_KERBEROS, BUFF, StatusEffects.KerberosStatusEffect)
__MANAGER_KERBEROS.setDefaults(rounds=NO_ROUNDS, extraArgs=(StatusEffects.KerberosStatusEffect.NORMAL,))

__GHOST_PAYROLL = StatusEffectDefinition(SEE.EFFECT_GHOST_PAYROLL, BUFF, StatusEffects.GhostPayrollEffect)
__GHOST_PAYROLL.setDefaults(rounds=NO_ROUNDS, extraArgs=(1,))
__GHOST_PAYROLL.setIconProperties(icon='ghost_payroll', iconScale=0.85)

__STANDUP_GUY = StatusEffectDefinition(SEE.EFFECT_STANDUP_GUY, BUFF, StatusEffects.DamageAbsorbStatusEffect)
__STANDUP_GUY.setDefaults(rounds=THIS_ROUND, extraArgs=(0.6, 0))

__MANAGER_PLUTOCRAT = StatusEffectDefinition(SEE.EFFECT_MANAGER_PLUTOCRAT, BUFF, StatusEffects.PlutocratStatusEffect)
__MANAGER_PLUTOCRAT.setDefaults(rounds=NO_ROUNDS, extraArgs=(StatusEffects.InstanceMercStatusEffectBase.NORMAL,))
__MANAGER_PLUTOCRAT.setIconProperties(icon='market_bubble')
__MANAGER_PLUTOCRAT.setVisualEffectEnums(VisualEffectEnum.MARKET_BUBBLE)
# endregion


### BUILDER FUNCTIONS START ###
def effectDefinitionClasses() -> list:
    return list(StatusEffectDefinitions.values())


def buildStatusEffectAttributes() -> dict:
    """Builds a massive dict of status effect attributes."""
    retdict = {}
    for effectDef in effectDefinitionClasses():
        retdict[effectDef.effectId] = effectDef.buildAttributes()
    return retdict


def buildStatusEffectText() -> dict:
    """Builds a massive dict of status effect text definitions."""
    retdict = {}
    for effectDef in effectDefinitionClasses():
        retdict[effectDef.effectId] = effectDef.buildTextProperties()
    return retdict


def buildStatusEffectImageProperties() -> dict:
    """Builds a massive dict of status effect image properties."""
    retdict = {}
    for effectDef in effectDefinitionClasses():
        retdict[effectDef.effectId] = effectDef.buildImageProperties()
    return retdict


def buildStatusEffectBuffStatus() -> dict:
    """Builds a massive dict of status effect buff statuses."""
    retdict = {}
    for effectDef in effectDefinitionClasses():
        retdict[effectDef.effectId] = effectDef.getBuffStatus()
    return retdict


def getEffectIdsOfQuality(quality: int) -> list:
    """Returns a list of status effect ids which match the given
    quality value. (BUFF, DEBUFF, NEUTRAL)
    """
    return [effectId for effectId, effectDef in StatusEffectDefinitions.items() if quality == effectDef.quality]
