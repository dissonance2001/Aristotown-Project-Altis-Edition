"""Corporate Clash Club Task pricing helpers for Project Altis.

The task chain ID stores the generated task difficulty in its millions
field. Corporate Clash awards 300 Club Coins for every effective Toon used
to scale the task. The effective Toon count can be reconstructed exactly
from the same difficulty formula used by the task generator.
"""

import math


TASK_DIFFICULTY_COEFFICIENT = 1.15
TASK_DIFFICULTY_POWER = 1.06
CLUB_TASK_COINS_PER_TOON = 300
CLUB_TASK_BASE_XP = 3
CLUB_TASK_XP_POWER = 1.5
MAX_DECODE_TOON_COUNT = 75


def _difficultyFromChainId(chainId):
    return max(1, int(chainId) // 1000000)


def _difficultyForToonCount(toonCount):
    toonCount = max(1, int(toonCount))
    scaledCount = int(math.ceil(toonCount * TASK_DIFFICULTY_COEFFICIENT))
    return max(1, int(round((scaledCount + 1) ** TASK_DIFFICULTY_POWER)))


def _toonCountFromDifficulty(difficulty):
    """Decode the effective Toon count embedded in a task difficulty.

    Clash creates the difficulty by rounding a nonlinear value. Searching
    the small legal Club-size range avoids inaccurate inverse rounding and
    reproduces the exact count for generated tasks.
    """
    difficulty = max(1, int(difficulty))
    closestCount = 1
    closestDistance = None

    for toonCount in range(1, MAX_DECODE_TOON_COUNT + 1):
        candidate = _difficultyForToonCount(toonCount)
        distance = abs(candidate - difficulty)
        if distance == 0:
            return toonCount
        if closestDistance is None or distance < closestDistance:
            closestCount = toonCount
            closestDistance = distance

    return closestCount


def calculateTaskReward(chainId):
    difficulty = _difficultyFromChainId(chainId)
    toonCount = _toonCountFromDifficulty(difficulty)
    return max(CLUB_TASK_COINS_PER_TOON,
               int(toonCount * CLUB_TASK_COINS_PER_TOON))


def calculateTaskExperience(chainId):
    """Return the difficulty-scaled XP reward for one Club Task.

    A one-Toon task starts at 3 XP.  The chain ID's nonlinear difficulty
    tier then raises the XP reward exponentially, so the substantially harder
    tasks generated for higher-level Clubs remain worthwhile without bringing
    back the old 300-XP level-jump bug.
    """
    difficulty = _difficultyFromChainId(chainId)
    baseDifficulty = float(_difficultyForToonCount(1))
    difficultyScale = max(1.0, float(difficulty) / baseDifficulty)
    return max(
        CLUB_TASK_BASE_XP,
        int(math.ceil(CLUB_TASK_BASE_XP *
                      (difficultyScale ** CLUB_TASK_XP_POWER))),
    )


def calculateRerollCost(chainId):
    difficulty = _difficultyFromChainId(chainId)
    return max(1, int(round(81 * round(difficulty ** 1.3, 1))))
