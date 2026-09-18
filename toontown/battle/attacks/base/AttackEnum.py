"""AttackEnum: Houses the enum of every attack in Toontown for both Toons and Suits."""
from enum import IntEnum, auto


class AttackEnum(IntEnum):
    ### Toon Attacks ###
    # region

    # Basic gag tracks (leave these as not auto as they are indices)
    TOON_HEAL   = 0
    TOON_TRAP   = 1
    TOON_LURE   = 2
    TOON_SOUND  = 3
    TOON_SQUIRT = 4
    TOON_ZAP    = 5
    TOON_THROW  = 6
    TOON_DROP   = 7

    # Special toon actions
    TOON_FIRE = auto()
    TOON_SUE = auto()
    TOON_NPC = auto()

    # Stupid non-existant attacks
    TOON_UN_ATTACK = auto()
    TOON_PASS = auto()
    TOON_NO_ATTACK = auto()

    # Extremely non-existant attacks
    # We need to rewrite battleGUI at some point...
    TOON_DICE = auto()
    # endregion

    ### Generic Suit Attacks ###
    # region
    AUDIT = auto()
    BITE = auto()
    BLUE_CHIP = auto()
    BOUNCE_CHECK = auto()
    BRAIN_STORM = auto()
    BUZZ_WORD = auto()
    CALCULATE = auto()
    CANNED = auto()
    CHOMP = auto()
    CIGAR_SMOKE = auto()
    CIGAR_SMOKE_HEAD_HONCHO = auto()
    CIGAR_SMOKE_FIRESTARTER = auto()
    CIGAR_SMOKE_PLUTOCRAT = auto()
    CLIPON_TIE = auto()
    CRUNCH = auto()
    DEMOTION = auto()
    DOWNSIZE = auto()
    DOUBLE_TALK = auto()
    EVICTION_NOTICE = auto()
    EVIL_EYE = auto()
    FALLING_KNIFE = auto()
    FILIBUSTER = auto()
    FILL_WITH_LEAD = auto()
    FINGER_WAG = auto()
    FIRED = auto()
    FOUNTAIN_PEN = auto()
    FREEZE_ASSETS = auto()
    GLOWER_POWER = auto()
    GUILT_TRIP = auto()
    HALF_WINDSOR = auto()
    HANG_UP = auto()
    HEAD_SHRINK = auto()
    HOT_AIR = auto()
    JARGON = auto()
    LEGALESE = auto()
    LIQUIDATE = auto()
    MARKET_CRASH = auto()
    MUMBO_JUMBO = auto()
    PARADIGM_SHIFT = auto()
    PECKING_ORDER = auto()
    PENNY_PINCH = auto()
    PICK_POCKET = auto()
    PINK_SLIP = auto()
    PLAY_HARDBALL = auto()
    POUND_KEY = auto()
    POWER_TIE = auto()
    POWER_TRIP = auto()
    QUAKE = auto()
    AFTERSHOCK = auto()
    RAZZLE_DAZZLE = auto()
    RED_TAPE = auto()
    RE_ORG = auto()
    RE_ARRANGE = auto()
    RESTRAINING_ORDER = auto()
    ROLODEX = auto()
    ROLODEX_DOUBLE = auto()
    RUBBER_STAMP = auto()
    RUB_OUT = auto()
    SACKED = auto()
    SCHMOOZE = auto()
    SHAKE = auto()
    SHORT_SQUEEZE = auto()
    SHRED = auto()
    SONG_AND_DANCE = auto()
    SPIN = auto()
    SYNERGY = auto()
    TABULATE = auto()
    TEE_OFF = auto()
    THROW_BOOK = auto()
    TREMOR = auto()
    WATERCOOLER = auto()
    WATERCOOLER_DOUBLE = auto()
    WATERCOOLER_GROUP = auto()
    WITHDRAWAL = auto()
    WRITE_OFF = auto()
    # endregion

    ### Taskline Minibosses ###
    # region

    # Derrick Man
    REFINEMENT = auto()

    # LAA
    INK_DRAIN = auto()

    # Derrick Hand
    REFINEMENT_DIRECTORS = auto()

    # DOLD
    INK_DRAIN_DIRECTORS = auto()

    # DOPA
    OVERWHELMING_AUTHORITY = auto()
    DISRUPTIVE_ADVERTISEMENT = auto()
    MULTI_LEVEL_MARKETING = auto()
    # endregion

    ### Facility Minibosses ###
    # region

    # Factory Foreman
    WORKERS_COMP = auto()

    # Mint Supervisor
    LIFE_INSURANCE = auto()

    # Head Attorney
    OBJECTION = auto()
    OBJECTION_SUSTAINED = auto()
    OBJECTION_OVERRULED = auto()

    # Club President
    EXTRA_TIP = auto()
    # endregion

    ### Litigation Team ###
    # region

    # Litigator
    BAYOU_BASH = auto()
    BAYOU_BELLOW = auto()
    SNAP = auto()
    SNAP_RETALIATE = auto()

    # Case Manager
    INSURANCE_PLAN = auto()
    LEGAL_BINDINGS = auto()
    LEGAL_BINDINGS_DAMAGE = auto()

    # Stenographer
    COURT_SANCTION = auto()
    COURT_SANCTION_RETALIATE = auto()
    COURT_RECORD = auto()
    COURT_RECORD_DAMAGE = auto()
    COURT_COSTS = auto()
    STENOG_CALCULATING_COSTS = auto()

    # Scapegoat
    SCAPEGOAT_ENRAGED = auto()
    SCAPEGOAT_DEFENSE = auto()
    # endregion

    ### Event Minibosses ###
    # region
    
    # Count Erclaim
    LAFF_STEAL = auto()
    RISE_FROM_THE_SCRAP = auto()
    SACRIFICE = auto()
    SCOPE_CREEP = auto()

    # Count Erfit
    HYDRATION_CHECK = auto()
    PROTOON_SHAKE = auto()
    PERSONAL_TRAINER = auto()
    GAINS_FROM_THE_SCRAP = auto()
    ERFIT_REVIVE = auto()
    HYDRATION_COMEBACK = auto()

    # OFTF
    OVERCLOCKED_FOREMAN_DESTRUCTION = auto()

    # Find the Family
    FTF_NUCLEAR_TRANSFORMATION = auto()
    FTF_FOREMAN_REDTAPE = auto()
    FTF_FOREMAN_SNIPE = auto()
    FTF_FOREMAN_CIGAR_SMOKE = auto()
    FTF_SUPERVISOR_LIFE_INSURANCE = auto()
    FTF_SUPERVISOR_ABACUS_SYNERGY = auto()
    FTF_ATTORNEY_PICK_UP_THE_PACE = auto()
    FTF_ATTORNEY_COURT_MANDATE_MONOLITH = auto()
    FTF_ATTORNEY_COURT_MANDATE_OMNIPOTENT = auto()
    FTF_PRESIDENT_MULLIGAN = auto()
    FTF_PRESIDENT_EXTRA_TIP = auto()
    FTF_PRESIDENT_SNAP = auto()
    FTF_PRESIDENT_SNIPE = auto()
    FTF_PRESIDENT_DRIVER = auto()
    FTF_PRESIDENT_SHATTER_DAMAGE = auto()

    # High Roller
    HIGHROLLER_LEVEL_DAMAGE = auto()
    FINISH_BETWEEN = auto()
    SPIN_WHEEL = auto()
    RANDOM_GAME = auto()
    RANDOM_GAME_FINISH = auto()
    RANDOM_GAME_PUNISH = auto()
    HIGHROLLER_COMMERCIAL = auto()
    HIGHROLLER_HOLLYWOOD = auto()
    HIGHROLLER_BEGIN_MADNESS = auto()
    TRICK_OF_THE_LIGHT = auto()
    HIGHROLLER_CLONE_TOONUP = auto()
    HIGHROLLER_CLONE_TRAP = auto()
    HIGHROLLER_CLONE_SQUIRT = auto()
    DICE_ROULETTE = auto()
    ACE_IN_THE_HOLE = auto()
    FREE_CRUISE = auto()
    CON_DUCK_TION = auto()
    ROLLED = auto()
    HR_EXIT_UNTOUCHABLE = auto()
    HR_TOON_LAFF_UP = auto()
    # endregion

    ### Street Mercenaries ###
    # region

    # Duck Shuffler
    WAGER_DUCKS = auto()
    WAGER_SEVENS = auto()
    WAGER_BEANS = auto()
    WAGER_BAR = auto()
    WAGER_BUST = auto()

    # Deep Diver
    DIVE = auto()
    SINK_OR_SWIM = auto()
    DEEP_DIVER_PROMOTE_FODDER = auto()
    DEEP_DIVER_DIVING_DOT = auto()

    # Gatekeeper
    GATEKEEPER_FODDER_KILL_PIERCE = auto()
    GATEKEEPER_JUMP_UNLURE_FODDER = auto()

    # Bellringer
    HEALING_BELL = auto()
    BELLRINGER_FODDER_EXPLOSION = auto()

    # Mouthpiece
    RED_THREAD = auto()
    RED_THREAD_DAMAGE = auto()
    HEARTBROKEN = auto()

    # Firestarter
    BACKBURNER = auto()
    BARNBURNER = auto()
    PYROMANIAC = auto()

    # Treekiller
    PEELING_THE_BARK = auto()
    WOODCHIPPER = auto()
    WOODCHIPPER_DAMAGE = auto()

    # Featherbedder
    INSOMNIA = auto()
    POWER_NAP_HEAL = auto()
    POWER_NAP_KILL_DAMAGE_UP = auto()
    # endregion

    ### Instance Minibosses ###
    # region

    # Prethinker
    CASTLING = auto()
    FORWARD_THINKING = auto()
    PT_BLOCK_SOUND_ENTER = auto()
    PT_BLOCK_SOUND_EXIT = auto()
    BRAIN_WAVE = auto()

    # Rainmaker
    WEATHER_OIL_RAIN = auto()
    WEATHER_FOG = auto()
    WEATHER_HEAVY_RAIN = auto()
    WEATHER_STORM_CELL = auto()
    WEATHER_INVERSION = auto()
    WEATHER_MONSOON = auto()
    STORM_CELL_ZAP = auto()
    HEAVY_RAIN_ZAP = auto()
    OIL_RAIN_DOT = auto()

    RAINMAKER_ENDING_0 = auto()
    RAINMAKER_ENDING_1 = auto()
    RAINMAKER_ENDING_2 = auto()
    RAINMAKER_ENDING_3 = auto()
    RAINMAKER_ENDING_4 = auto()

    # Witch Hunter
    TRIAL_BY_FIRE = auto()
    MOB_MENTALITY = auto()
    BOILERPLATE = auto()
    BEWITCHMENT = auto()

    # Multislacker
    WASTEFUL_MGMT = auto()
    HYPER_TASK = auto()
    ZERO_TASK = auto()
    MANDATORY_LUNCH = auto()
    MS_POWER_TIE = auto()
    # Multislacker Foreman
    UNION_BUST = auto()

    # Major Player
    ROCKING_IN_RHYTHM = auto()
    STAR_OF_THE_SHOW = auto()
    GUEST_VERSE_START = auto()
    GUEST_VERSE_END = auto()
    DANCE_PARTNERS = auto()
    STAR_OF_THE_SHOW_END = auto()
    TOON_STAR_BONUS_TEXT = auto()

    # Plutocrat
    SLUSH_FUND = auto()
    DEEP_FREEZE = auto()
    SNOW_SQUALL = auto()
    SNOW_SQUALL_DAMAGE = auto()
    SHATTER_DAMAGE = auto()
    PCRAT_INVESTOR_DEATH_PHRASE = auto()

    # Satellite Investors
    GHOST_PAYROLL_HEAL = auto()
    STANDUP_GUY = auto()
    SHAKEDOWN = auto()
    KICK_UP = auto()
    SITDOWN = auto()
    USURY = auto()
    TRIBUTE = auto()

    # Chainsaw Consultant
    OFFBOARDING = auto()
    REVVING_UP = auto()
    LAYOFFS = auto()
    CUT_THE_SLACK = auto()
    MARKED_WOOD = auto()
    WHIP_SAW = auto()
    CHAINSAW_ENTER_DORMANT = auto()
    CHAINSAW_EXIT_DORMANT = auto()
    SCABBARD = auto()
    CHAIN_LINKED = auto()
    KICKBACK = auto()
    AGGRANDIZE = auto()
    DEADWOOD = auto()
    THROTTLE = auto()
    SPARK_PLUG = auto()
    SPARK_PLUG_DAMAGE = auto()
    SPENDING_REV = auto()

    # Pacesetter
    PICK_UP_THE_PACE = auto()
    OVERCLOCKED = auto()
    RUSH_JOB = auto()
    HURRY_SICKNESS = auto()
    CORPORATE_RESTRUCTURING = auto()
    CONTENT_SYNC = auto()
    MOVING_GOALPOSTS = auto()
    HURRY_SICKNESS_MG = auto()  # Variant for moving goalposts
    PACESETTER_CHALLENGE = auto()
    PACESETTER_CHALLENGE_CANCELLED = auto()
    # endregion

    ### Unsorted Suit Attacks ###
    # region
    
    # Tutorial
    LIGHTS_ON = auto()
    # endregion

    ### General Toon Attacks ###
    # region
    TOON_DAMAGE = auto()
    TOON_HEALING = auto()
    DAMAGE_ABSORB_TOON_DAMAGE = auto()
    # endregion

    ### General Suit Attacks ###
    # region
    SUIT_DAMAGE = auto()
    SUIT_HEAL = auto()
    SUIT_MARKED_DAMAGE = auto()
    DAMAGE_ABSORB_SUIT_DAMAGE = auto()
    DAMAGE_ABSORB_SUIT_DAMAGE_WITH_UNLURE = auto()
    DAMAGE_ABSORB_SUIT_DAMAGE_INSTANT = auto()
    SUIT_LURE = auto()
    SUIT_UNLURE = auto()
    AVATAR_SAY_PHRASE = auto()
    # Target based instead of invoker based
    AVATAR_SAY_PHRASE_ON_TARGET = auto()
    # endregion

    ### General Avatar Attacks ###
    # region

    # Generic Instakill Attack
    AVATAR_INSTAKILL = auto()
    SHOW_HP_TEXT = auto()
    SHOW_PIP_TEXT = auto()
    REMOVE_VISUAL_EFFECT = auto()
    # This version only acts as a movie on the client.
    APPLY_VISUAL_EFFECT_MOVIE = auto()
    COGS_FLY_AWAY = auto()
    SUITS_ADJUST_POSITION = auto()
    # endregion

    def __repr__(self):
        for m in self.__class__:
            if m.value == self.value:
                return m.name
        return ""
