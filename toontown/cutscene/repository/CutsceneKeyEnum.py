from enum import Enum, auto


class CutsceneKeyEnum(Enum):
    # region Taskline Instance Bosses
    Derrickman_Intro = auto()
    Derrickman_Death = auto()
    Derrickman_Vict = auto()

    Dola_Intro = auto()
    Dola_Death = auto()

    Dopr_Intro = auto()
    Dopr_Death = auto()
    # endregion

    # region litigation team Mercs
    Litigator_Bellow = auto()
    Scapegoat_Enraged = auto()
    CaseManager_Insurance = auto()
    # endregion

    # region Street Mercs
    DuckShuffler_Wager_Bar = auto()
    DuckShuffler_Wager_Beans = auto()
    DuckShuffler_Wager_Base = auto()

    DeepDiver_Dive = auto()
    DeepDiver_SinkOrSwim = auto()

    Featherbedder_Insomnia = auto()
    # endregion

    # region Instance Mercs
    Prethinker_Intro = auto()
    Prethinker_Death = auto()
    Prethinker_Castling_Exit = auto()
    Prethinker_Castling_Enter = auto()
    Prethinker_ForwardThinking = auto()

    Rainmaker_Intro = auto()
    Rainmaker_Transformation = auto()
    Rainmaker_Tornado = auto()
    Rainmaker_ToonsComeHome = auto()
    Rainmaker_HeavyRainDamage = auto()
    Rainmaker_StormCellDamage = auto()
    Rainmaker_Ending_1 = auto()
    Rainmaker_Ending_2 = auto()
    Rainmaker_Ending_3 = auto()
    Rainmaker_Ending_4 = auto()

    Witchhunter_Intro = auto()
    Witchhunter_Death = auto()
    Witchhunter_MobMentality = auto()

    Multislacker_Intro = auto()
    Multislacker_Death = auto()
    Multislacker_MandatoryLunch_Start = auto()
    Multislacker_MandatoryLunch_End = auto()
    Multislacker_Foreman_UnionBust = auto()
    Multislacker_JoinBattle_Foreman = auto()
    Multislacker_JoinBattle_Generic = auto()
    Multislacker_WastefulManagement = auto()

    MajorPlayer_Intro_Start = auto()
    MajorPlayer_Intro_End = auto()
    MajorPlayer_Death = auto()
    MajorPlayer_Revive = auto()
    MajorPlayer_RisingStar_A = auto()  # the audience member being grabbed
    MajorPlayer_RisingStar_B = auto()  # the new audience member appearing
    MajorPlayer_BeginMatching = auto()
    MajorPlayer_DancePartners = auto()
    MajorPlayer_StarOfTheShow = auto()
    MajorPlayer_GuestVerse = auto()
    MajorPlayer_DancePartnersSpawn = auto()

    Plutocrat_Intro = auto()
    Plutocrat_Death = auto()
    Plutocrat_JoinBattle_Generic = auto()
    Plutocrat_JoinBattle_Pcrat = auto()
    Plutocrat_JoinBattle_Hatch_Open = auto()
    Plutocrat_JoinBattle_Hatch_Close = auto()
    Plutocrat_Investor_SitDown = auto()
    Plutocrat_Investor_Usury = auto()
    Plutocrat_Investor_Usury_Fodder = auto()
    Plutocrat_Investor_Kickup = auto()
    Plutocrat_Investor_Tribute = auto()
    Plutocrat_DeepFreeze_Camera = auto()
    Plutocrat_SnowSquall_Start = auto()
    Plutocrat_SnowSquall_End = auto()
    Plutocrat_SnowSquall_Damage = auto()

    ChainsawConsultant_Intro = auto()
    ChainsawConsultant_Death = auto()
    ChainsawConsultant_Ending = auto()
    ChainsawConsultant_Deadwood = auto()
    ChainsawConsultant_Throttle = auto()
    ChainsawConsultant_ThrottleTwo = auto()
    ChainsawConsultant_Scabbard = auto()
    ChainsawConsultant_RevvedUp = auto()
    ChainsawConsultant_SparkPlug = auto()
    ChainsawConsultant_Offboarding = auto()
    ChainsawConsultant_Layoffs = auto()
    ChainsawConsultant_ChainLinked = auto()
    ChainsawConsultant_PhaseTwo = auto()
    ChainsawConsultant_PhaseThree = auto()

    Pacesetter_Intro = auto()
    Pacesetter_Death = auto()
    Pacesetter_GuitarSolo = auto()
    Pacesetter_OverclockedGUI = auto()
    Pacesetter_PickUpThePace = auto()
    Pacesetter_RushJob = auto()
    # endregion

    # region Event Bosses
    Erfit_Intro = auto()
    Erfit_Intro_Elevator = auto()

    HighRoller_Intro = auto()
    HighRoller_Death = auto()
    HighRoller_RandomGame = auto()
    HighRoller_RandomGameSpawn = auto()
    HighRoller_RandomGameSpawn_Podium = auto()
    HighRoller_Commercial_Start = auto()
    HighRoller_Commercial_End = auto()
    HighRoller_CloneSpawn = auto()
    HighRoller_Clone_Trap = auto()
    HighRoller_FreeCruise = auto()
    HighRoller_FreeCruiseMissed = auto()
    HighRoller_AceInTheHole = auto()
    HighRoller_DiceRouletteNothing = auto()
    HighRoller_DiceRouletteSuitsDamaged = auto()
    HighRoller_DiceRouletteToonsDamaged = auto()
    HighRoller_MinigameResults = auto()
    HighRoller_PhaseTwo = auto()
    HighRoller_PhaseThree = auto()

    FindTheFamily_Attorney_Castling_Exit = auto()
    FindTheFamily_Attorney_RushJob = auto()
    # endregion

    # region Clash Meta
    Trailer_HiresAndHeroesOpeningA = auto()
    Trailer_HiresAndHeroesOpeningB = auto()
    Trailer_MajorPlayer = auto()
    # endregion
