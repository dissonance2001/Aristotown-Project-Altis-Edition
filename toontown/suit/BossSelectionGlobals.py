"""
Boss selection for the Sellbot (VP) lobby elevator.

Each selectable boss is identified by a small integer that is sent over the
network (uint8).  OCVP is Altis's own DistributedSellbotBossMini; VP is the
Corporate Clash VP (DistributedClashSellbotBoss).
"""

SELLBOT_OCVP = 0
SELLBOT_VP = 1

DEFAULT_SELLBOT_BOSS = SELLBOT_OCVP

SellbotOptions = [SELLBOT_OCVP, SELLBOT_VP]

BossNames = {
    SELLBOT_OCVP: 'Overclocked VP',
    SELLBOT_VP: 'Vice President',
}

SelectTitle = 'Choose Your Boss'
SelectLeaderHint = 'Click a boss to choose who your group fights.'
SelectFollowerHint = 'The first toon aboard picks the boss.'
SelectCurrent = 'Boss: %s'


def getSellbotOptions():
    return list(SellbotOptions)


def isValidSellbotBoss(bossType):
    return bossType in BossNames


def getBossName(bossType):
    return BossNames.get(bossType, '???')
