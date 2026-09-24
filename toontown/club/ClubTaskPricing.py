"""
Pricing functions for Club Tasks.
"""


def calculateTaskReward(chainId: int) -> int:
    return round(__calculateClubCoinBase(chainId))


def calculateRerollCost(chainId: int) -> int:
    capacity = chainId // 1_000_000
    return round(81 * round(capacity ** 1.3, 1))


def calculateTaskCost(chainId: int, coins: bool = False, beans: bool = False) -> int:
    assert coins or beans, "must pick one"
    if coins:
        return max(1, round(__calculateClubCoinBase(chainId)))
    elif beans:
        return max(1, round(__calculateClubCoinBase(chainId))) * 400


def __calculateClubCoinBase(chainId: int) -> float:
    baseCost = round(chainId // 1_000_000)
    return max(1.0, (baseCost ** 1.2) * 0.747)
