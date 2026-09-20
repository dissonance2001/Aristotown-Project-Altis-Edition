from enum import IntEnum
from toontown.toonbase.ToontownGlobals import ToontownCentral, DonaldsDock, YeOlde, DaisyGardens, \
    MinniesMelodyland, TheBrrrgh, OutdoorZone, DonaldsDreamland


class QuestTier(IntEnum):
    """
    Quest tiers which are used for filtering out
    certain objective types.
    """
    NEWBIE = 0
    TTC = 1
    BB = 2
    YOTT = 3
    DG = 4
    MML = 5
    TB = 6
    AA = 7
    DDL = 8


QuestChainToTier = {
    12: QuestTier.TTC,
    22: QuestTier.BB,
    32: QuestTier.YOTT,
    42: QuestTier.DG,
    49: QuestTier.MML,
    57: QuestTier.TB,
    67: QuestTier.AA,
    75: QuestTier.DDL,
}

QuestTierToPlayground = {
    QuestTier.NEWBIE: ToontownCentral,
    QuestTier.TTC: ToontownCentral,
    QuestTier.BB: DonaldsDock,
    QuestTier.YOTT: YeOlde,
    QuestTier.DG: DaisyGardens,
    QuestTier.MML: MinniesMelodyland,
    QuestTier.TB: TheBrrrgh,
    QuestTier.AA: OutdoorZone,
    QuestTier.DDL: DonaldsDreamland
}

DailyGumballReward = 150
