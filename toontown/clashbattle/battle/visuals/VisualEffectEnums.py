from enum import Enum, auto


class VisualEffectEnum(Enum):
    NOTHING = auto()
    LURED = auto()
    SOAKED = auto()
    DRENCHED = auto()
    SPLAT = auto()
    SUED = auto()
    ENCORE = auto()
    WINDED = auto()
    SKELECOG = auto()
    TOON_BOOST = auto()
    VULNERABLE = auto()
    SCAPEGOAT_ENRAGED = auto()
    INSURANCE = auto()
    ERFIT_REVIVE = auto()
    LEGALLY_BOUND = auto()
    GAG_DOWN = auto()
    OVERCHARGED = auto()
    OC_FOREMAN = auto()
    DISRUPTIVE_ADVERTISEMENT = auto()
    INK_DRAIN = auto()
    EXTRA_GLOWER_POWERS = auto()
    UNITE_COOLDOWN = auto()
    COGS_DAMAGE_DOWN = auto()
    TOONS_ACCURACY_UP = auto()
    FROZEN = auto()
    TOON_BECOME_DUCK = auto()
    DIVING = auto()
    BACKBURNER = auto()
    PEELED = auto()
    WOODCHIPPED = auto()
    OVERHIRE = auto()
    TRIAL_BY_FIRE = auto()
    CORE_COMPETENCY = auto()
    DEEP_FREEZE = auto()
    RUSH_JOB = auto()
    AFTERIMAGE = auto()
    MANDATORY_LUNCH_MSLACKER = auto()
    CHEER = auto()
    PRETHINKER_BRAIN_STORM = auto()
    POWER_NAP = auto()
    BEWITCHMENT = auto()
    MARKET_BUBBLE = auto()
    SLUSH_FUND = auto()
    CHAIN_LINKED = auto()
    SPARK_PLUG_DAMAGE = auto()
    MARKED_WOOD = auto()
    HIGHROLLER_COMMERCIAL = auto()
    HIGHROLLER_TRIVIA = auto()
    HIGHROLLER_CLONE = auto()
    JOGGING = auto()
    ROLLED = auto()
    FTF_ATTORNEY_JOGGING = auto()
    HR_UNTOUCHABLE = auto()
    CONFUSION = auto()
    BAKERY_AFICIONADO = auto()
    RED_THREAD = auto()
    MOUTHPIECE_BONUS = auto()
    CHAINSAW_OVERRIDE = auto()
    CHAINSAW_OVERRIDE_GLITCHED = auto()


# Handy dandy alias for VisualEffectEnum.
VEE = VisualEffectEnum


# -=- Common Groupings of Visual Effects -=-
# For removing "all" negative effects from a suit.
SUIT_VISUAL_EFFECTS_TO_REMOVE = [
    VEE.SOAKED,
    VEE.SUED,
    VEE.SPLAT,
]
