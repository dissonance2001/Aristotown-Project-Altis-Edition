from enum import IntEnum, auto


class StatusEffectEnum(IntEnum):
    EFFECT_BASE = auto()
    EFFECT_SUIT = auto()
    EFFECT_SKELECOG = auto()
    EFFECT_VIRTUAL_COG = auto()
    EFFECT_MINIBOSS = auto()
    # 'Trick' the battle into believing an avatar is dead.
    EFFECT_DEAD = auto()
    EFFECT_SUIT_LURED = auto()
    # Displays that a suit is trapped
    EFFECT_SUIT_TRAPPED = auto()
    EFFECT_SUIT_DAZED = auto()
    EFFECT_SUIT_DEFENSE_MODIFIER = auto()
    EFFECT_SUIT_NODODGE = auto()
    EFFECT_SUIT_SOAKED = auto()
    EFFECT_SUIT_DRENCHED = auto()
    EFFECT_SUIT_SUED = auto()
    EFFECT_COGS_DAMAGE_DOWN = auto()
    EFFECT_COGS_DAMAGE_ABSORB = auto()
    EFFECT_COGS_DAMAGE_ABSORB_INSTANT = auto()
    EFFECT_DAMAGE_TAKEN_UP = auto()
    EFFECT_DAMAGE_TAKEN_DOWN = auto()
    EFFECT_FLATTENED_DAMAGE_TAKEN = auto()
    EFFECT_HIT = auto()
    EFFECT_MISS = auto()
    # Desk Jockey manager
    EFFECT_MANAGER_DESK_JOCKEY = auto()
    # Land acq. status effect
    EFFECT_INK_DRAIN = auto()
    EFFECT_TOONS_ACCURACY_UP = auto()
    # Accuracy bonus for Toons, provided by Toon-Up.
    EFFECT_CHEER = auto()
    # Directors status effects
    EFFECT_OVERWHELMING_AUTHORITY = auto()
    EFFECT_DISRUPTIVE_ADVERTISEMENT = auto()
    EFFECT_MULTI_LEVEL_MARKETING = auto()
    EFFECT_GENERIC_EXTRA_ATTACKS = auto()
    # Generally used for cheats
    EFFECT_CANT_ATTACK = auto()
    EFFECT_DAMAGE_DOWN = auto()
    # Revive, workers comp, etc.
    EFFECT_SUIT_DAMAGE_BOOST = auto()
    # DOPR status effect
    EFFECT_AMBUSH_MARKETING = auto()
    # Litigation team manager status effects
    EFFECT_LITIGATOR_MANAGER = auto()
    EFFECT_STENOGRAPHER_MANAGER = auto()
    EFFECT_CASE_MANAGER_MANAGER = auto()
    EFFECT_SCAPEGOAT_MANAGER = auto()
    # Toon unite cooldown effect
    EFFECT_UNITE_COOLDOWN = auto()
    EFFECT_REWARD_COOLDOWN = auto()
    # Case manager heal over time
    EFFECT_CASE_MANAGER_HOT = auto()
    # Case manager damage over time
    EFFECT_CASE_MANAGER_DOT = auto()
    # Litigator snap, general take more damage effect
    EFFECT_VULNERABLE = auto()
    # Stenographer court sanction, -50% gag effectiveness down
    EFFECT_SANCTIONED = auto()
    # Stenographer court record, disallows random level gag 5 to 8
    EFFECT_COURT_RECORD = auto()
    # Scapegoat rage counter
    EFFECT_SCAPEGOAT_RAGE = auto()
    # Scapegoat damage down (to other cogs)
    EFFECT_SCAPEGOAT_DAMAGE_TAKEN_DOWN = auto()
    # Supervisor insured effect, keeps him healed if other cogs are alive
    EFFECT_SUPERVISOR_INSURED = auto()
    EFFECT_SUIT_ADDITIVE_DAMAGE_BOOST = auto()
    # Displays that a suit has lure resistance
    EFFECT_LURE_RESISTANCE = auto()
    # Can be track specific or global - used for IOUs
    EFFECT_TOON_DAMAGE_UP = auto()
    # Toon damage up multiplier
    EFFECT_TOON_MULT_DAMAGE_UP = auto()
    # Effect for when a Toon just missed
    EFFECT_TOON_JUST_MISSED = auto()
    # Hidden effect for when a Suit dodges a soak
    EFFECT_SUIT_JUST_DODGED_SOAK = auto()
    # Hidden effect for when a Suit dodges a lure
    EFFECT_SUIT_JUST_DODGED_LURE = auto()

    # Prestige Throw effect
    EFFECT_MARKED_FOR_LAUGH = auto()

    # Sound Atk Bonus Effect
    EFFECT_ENCORE = auto()
    EFFECT_WINDED = auto()

    # Effect that clears out all other suits from the battle when this suit dies.
    EFFECT_END_BATTLE_ON_DEATH = auto()

    # Effect that prevents a Suit from dying.
    EFFECT_PREVENT_DEATH = auto()

    ### Street Mercenaries ###
    # region
    EFFECT_MANAGER_MERC = auto()

    # Duck Shuffler
    EFFECT_MANAGER_DUCK_SHUFFLER = auto()

    # Deep Diver
    EFFECT_MANAGER_DEEP_DIVER = auto()
    EFFECT_DIVING = auto()
    
    # Gatekeeper
    EFFECT_MANAGER_GATEKEEPER = auto()
    EFFECT_GATEKEEPER_FODDER_BONUS = auto()
    EFFECT_GATEKEEPER_TOON_PIERCE = auto()

    # Bellringer
    EFFECT_MANAGER_BELLRINGER = auto()
    EFFECT_BELLRINGER_FODDER_EXPLOSION = auto()

    # Mouthpiece
    EFFECT_MANAGER_MOUTHPIECE = auto()
    EFFECT_MOUTHPIECE_EXTRA_ATTACK = auto()
    EFFECT_MOUTHPIECE_BONUS = auto()
    EFFECT_RED_THREAD = auto()
    EFFECT_RED_THREAD_TANGLED = auto()
    
    # Firestarter
    EFFECT_MANAGER_FIRESTARTER = auto()
    EFFECT_BACKBURNER = auto()

    # Treekiller
    EFFECT_PEELING_THE_BARK = auto()
    EFFECT_PEELING_THE_BARK_SUIT = auto()
    EFFECT_WOODCHIPPER = auto()

    # Featherbedder
    EFFECT_MANAGER_FEATHERBEDDER = auto()
    EFFECT_POWER_NAP = auto()
    EFFECT_POWER_NAP_KILL_DMG_BOOST = auto()
    EFFECT_PEACEFUL_SLUMBER = auto()
    # endregion

    ### Instance Mercenaries ###
    # region

    # Prethinker
    EFFECT_MANAGER_PRETHINKER = auto()
    EFFECT_PRETHINKER_DODGE_SOUND = auto()
    EFFECT_PRETHINKER_DAMAGE_TAKEN_DOWN = auto()
    EFFECT_PLASTIC_SUIT = auto()

    # Rainmaker
    EFFECT_MANAGER_RAINMAKER = auto()
    EFFECT_MONSOON = auto()
    EFFECT_MONSOON_DEFENSE = auto()
    EFFECT_OIL_RAIN_HOT = auto()
    EFFECT_OIL_RAIN_DOT = auto()
    EFFECT_FOG = auto()
    EFFECT_HEAVY_RAIN = auto()
    EFFECT_HEAVY_RAIN_RAINMAKER = auto()
    EFFECT_STORM_CELL = auto()

    # Witch Hunter
    EFFECT_MANAGER_WITCH_HUNTER = auto()
    EFFECT_WILL_OF_THE_PEOPLE = auto()
    EFFECT_TRIAL_BY_FIRE = auto()
    EFFECT_BEWITCHMENT = auto()
    EFFECT_HIVEMIND = auto()
    EFFECT_WHUNTER_CAT_DEFENSE_MODIFIER = auto()

    # Multislacker
    EFFECT_MANAGER_MULTISLACKER = auto()
    EFFECT_LUNCH_BREAK = auto()
    EFFECT_LUNCH_BREAK_MSLACKER = auto()
    EFFECT_OUT_FOR_LUNCH = auto()
    EFFECT_SOAK_RESISTANCE = auto()

    # Multislacker's Foreman
    EFFECT_FOCUSED_DEFENSE = auto()
    EFFECT_WORKER_MANAGEMENT = auto()
    EFFECT_UNION_BUST = auto()

    # Major Player
    EFFECT_MANAGER_MAJOR_PLAYER = auto()
    EFFECT_STAR_OF_THE_SHOW = auto()
    EFFECT_STAR_OF_THE_SHOW_TOON = auto()
    EFFECT_GUEST_VERSE = auto()
    EFFECT_VIRAL_SENSATION = auto()
    EFFECT_DANCE_PARTNER = auto()
    EFFECT_LAST_TAP = auto()
    EFFECT_SIPHON = auto()
    EFFECT_MP_COGS_DAMAGE_DOWN = auto()

    # Plutocrat
    EFFECT_MANAGER_PLUTOCRAT = auto()
    EFFECT_CONFUSION = auto()
    EFFECT_DEEP_FREEZE = auto()
    EFFECT_SLUSH_FUND = auto()
    EFFECT_SUIT_FROZEN = auto()

    # Satellite Investors
    EFFECT_SATELLITE_INVESTOR_MANAGER = auto()
    EFFECT_MANAGER_CHARON = auto()
    EFFECT_MANAGER_NIX = auto()
    EFFECT_MANAGER_HYDRA = auto()
    EFFECT_MANAGER_STYX = auto()
    EFFECT_MANAGER_KERBEROS = auto()
    EFFECT_STANDUP_GUY = auto()
    EFFECT_GHOST_PAYROLL = auto()

    # Chainsaw Consultant
    EFFECT_MANAGER_CHAINSAW_CONSULTANT = auto()
    EFFECT_MARKED_WOOD = auto()
    EFFECT_CHAIN_LINKED = auto()
    EFFECT_KICKBACK = auto()
    EFFECT_SPARK_PLUG = auto()
    EFFECT_AGGRANDIZE = auto()

    # Pacesetter
    EFFECT_MANAGER_PACESETTER = auto()
    EFFECT_RUSH_JOB = auto()
    EFFECT_HURRY_SICKNESS = auto()
    EFFECT_MOVING_GOALPOSTS = auto()
    # endregion

    ### Event Minibosses ###
    # region

    # Count Erclaim
    EFFECT_COUNT_ERCLAIM = auto()
    EFFECT_COUNT_CREEP = auto()

    # Count Erfit
    EFFECT_COUNT_ERFIT = auto()
    EFFECT_HYDRATED = auto()
    EFFECT_RIPPED = auto()
    EFFECT_ERFIT_GODMODE = auto()

    # OFTF
    EFFECT_OVERCLOCKED_FOREMAN = auto()

    # Find the family
    # FTF General
    EFFECT_FTF_SUPERVISOR_INSURED = auto()
    EFFECT_FTF_NUCLEAR = auto()
    EFFECT_FTF_DUALCORE = auto()
    EFFECT_FTF_PRISMATIC_TOON = auto()

    # FTF Specific
    EFFECT_FTF_FOREMAN_CONTRACTOR = auto()
    EFFECT_FTF_FOREMAN_CONTRACTOR_TANGO = auto()
    EFFECT_FTF_FOREMAN_REDTAPE = auto()
    EFFECT_FTF_FOREMAN_SNIPER = auto()
    EFFECT_FTF_FOREMAN_SLEEPY = auto()
    EFFECT_FTF_FOREMAN_SLEEPY_POWER_NAP = auto()
    EFFECT_FTF_FOREMAN_EXPLOSIVE = auto()
    EFFECT_FTF_FOREMAN_BURNING = auto()
    EFFECT_FTF_FOREMAN_BURNING_SMOKED = auto()

    EFFECT_FTF_SUPERVISOR_ABSORPTION = auto()
    EFFECT_FTF_SUPERVISOR_FRAUD = auto()
    EFFECT_FTF_SUPERVISOR_ABACUS = auto()
    EFFECT_FTF_SUPERVISOR_CONFUSED = auto()
    EFFECT_FTF_SUPERVISOR_CONTROLLING = auto()
    EFFECT_FTF_SUPERVISOR_ACCOUNTANT = auto()

    EFFECT_FTF_ATTORNEY_SNEAKY = auto()
    EFFECT_FTF_ATTORNEY_CHRONO = auto()
    EFFECT_FTF_ATTORNEY_OVERSEER = auto()
    EFFECT_FTF_ATTORNEY_RUSHJOB = auto()
    EFFECT_FTF_ATTORNEY_MONOLITH = auto()
    EFFECT_FTF_ATTORNEY_OMNIPOTENT = auto()

    EFFECT_FTF_PRESIDENT_MULLIGAN = auto()
    EFFECT_FTF_PRESIDENT_CHIPFAN = auto()
    EFFECT_FTF_PRESIDENT_ANCIENT = auto()
    EFFECT_FTF_PRESIDENT_PUZZLING = auto()
    EFFECT_FTF_PRESIDENT_PUZZLING_CONFUSED = auto()
    EFFECT_FTF_PRESIDENT_SHIVERING = auto()
    EFFECT_FTF_PRESIDENT_HIGHSTAKES = auto()

    # High Roller
    EFFECT_MANAGER_HIGH_ROLLER = auto()
    EFFECT_SHOW_HOST = auto()
    EFFECT_COMMERCIAL = auto()
    EFFECT_HARMONIOUS_COLORS = auto()
    EFFECT_QUESTION = auto()
    EFFECT_TRIVIA = auto()
    EFFECT_PUZZLE = auto()
    EFFECT_SHUFFLE = auto()
    EFFECT_HOLLYWOOD_STAR = auto()
    EFFECT_HIGHROLLER_CLONE = auto()
    EFFECT_RAISING_THE_ANTE = auto()
    EFFECT_HIGHROLLER_SHIELD_SUIT = auto()
    EFFECT_FAKE_SOAKED = auto()
    EFFECT_PIP_COUNTER = auto()
    EFFECT_PIP_DISCOUNT = auto()
    EFFECT_DICE_COOLDOWN = auto()
    EFFECT_HR_UNTOUCHABLE = auto()
    EFFECT_AITH_DAMAGE_TAKEN_UP = auto()
    EFFECT_HR_TOON_GAGS_UNLOCKED = auto()
    EFFECT_SOAK_POWERED_RESISTANCE = auto()
    EFFECT_HIGHROLLER_MINIGAME_HOST = auto()
    # endregion

    EFFECT_OVERCHARGED = auto()
    EFFECT_UNTOUCHABLE = auto()
    EFFECT_COMBO_KB_IMMUNITY = auto()
    EFFECT_DISABLE_GAG_TRACKS = auto()
    EFFECT_DISABLE_GAG_LEVELS = auto()
    # Contains what gags are currently counterfeited
    EFFECT_COUNTERFEIT_CONTAINER = auto()
    # Contains what gags have gotten used counterfeits this battle session
    EFFECT_COUNTERFEIT_USAGE_CONTAINER = auto()
    
    # Generic damage taken down for damage absorb
    EFFECT_DAMAGE_ABSORB_DAMAGE_DOWN = auto()

    EFFECT_NERVOUS_PACING = auto()

    # -=-=- #
    # Flags #
    # -=-=- #

    FLAG_BASE = auto()
    FLAG_EMPOWER = auto()

    TARGET_LIST_GHOSTWRITER = auto()

    # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= #
    # More or less environmental effects #
    # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= #

    EFFECT_SOAK_TO_FROZEN = auto()

    # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= #
    # Event Definition Only Enums (not tied to a specific status effect) #
    # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= #

    DEFINITION_ROUND_TIMER = auto()
    DEFINITION_MULTI_TIMER = auto()
    DEFINITION_SUIT_HEAL_OVER_TIME = auto()
    DEFINITION_LITIGATION_TEAM_MANAGER = auto()
    DEFINITION_DAMAGE_LISTENER = auto()
    DEFINITION_HP_GATEKEEPER = auto()
    DEFINITION_DAMAGE_ABSORB = auto()
    DEFINITION_ROUNDS_MODIFIER = auto()

    DEFINITION_OC_FAMILY_BASE = auto()
    DEFINITION_OC_FAMILY_S = auto()
    DEFINITION_OC_FAMILY_M = auto()
    DEFINITION_OC_FAMILY_L = auto()
    DEFINITION_OC_FAMILY_C = auto()

    # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= #
    # Spicy Generic Effects (obtuse, useful functionality) #
    # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= #

    DEFINITION_OVERRIDE_ADDED = auto()


# Handy dandy alias for StatusEffectEnum.
SEE = StatusEffectEnum


# -=- Common Groupings of Status Effects -=-
# For removing "all" negative effects from a suit.
SUIT_STATUS_EFFECTS_TO_REMOVE = [
    SEE.EFFECT_SUIT_LURED, SEE.EFFECT_SUIT_SOAKED, SEE.EFFECT_SUIT_DRENCHED,
    SEE.EFFECT_SUIT_SUED, SEE.EFFECT_COGS_DAMAGE_DOWN, SEE.EFFECT_SUIT_DAZED,
]

# For reducing the rounds of "all" negative effects on a suit.
SUIT_STATUS_EFFECTS_TO_REDUCE = [
    SEE.EFFECT_SUIT_LURED, SEE.EFFECT_SUIT_SOAKED, SEE.EFFECT_SUIT_DRENCHED,
    SEE.EFFECT_SUIT_SUED, SEE.EFFECT_COGS_DAMAGE_DOWN,
]
