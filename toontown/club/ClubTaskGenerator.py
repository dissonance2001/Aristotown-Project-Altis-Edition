"""Shared generated Club Tasks for Project Altis.

The generator follows Corporate Clash's current Club Task structure:
three shared tasks, chain-ID seeded generation, Club-size difficulty scaling,
unique objective types where possible, and immediate replacement of a
completed or rerolled slot.

Altis does not contain Clash's Quest3 runtime, so the generated objective pool
uses the Club progress events already emitted by Altis gameplay systems.
"""

from __future__ import absolute_import
import math
import random
import time

from toontown.club import ClubTaskPricing
from six.moves import range


TASK_VERSION = 2
TASK_COUNT = 3
TASK_DIFFICULTY_COEFFICIENT = 1.15
MAX_EFFECTIVE_TOON_COUNT = 15

# Objective types for which Altis already reports shared Club progress.
# The goal functions intentionally scale from the same difficulty value kept
# in the millions field of the Clash-style chain ID.
OBJECTIVE_TYPES = (
    'cogs',
    'buildings',
    'trolley',
    'fish',
    'bosses',
)


def _goalForObjective(progressType, difficulty):
    difficulty = max(1, int(difficulty))
    if progressType == 'cogs':
        return max(25, int(round(18.0 * (difficulty ** 1.15))))
    if progressType == 'buildings':
        return max(2, int(round(1.2 * (difficulty ** 1.05))))
    if progressType == 'trolley':
        return max(3, int(round(1.5 * difficulty)))
    if progressType == 'fish':
        return max(10, int(round(4.0 * (difficulty ** 1.1))))
    if progressType == 'bosses':
        return max(1, int(round(0.35 * difficulty)))
    return max(1, difficulty)


def _nameForObjective(progressType, goal):
    if progressType == 'cogs':
        return 'Defeat %s Cogs' % goal
    if progressType == 'buildings':
        return 'Complete %s Cog Building%s' % (
            goal, '' if goal == 1 else 's')
    if progressType == 'trolley':
        return 'Complete %s Trolley Game%s' % (
            goal, '' if goal == 1 else 's')
    if progressType == 'fish':
        return 'Catch %s Fish' % goal
    if progressType == 'bosses':
        return 'Complete %s Cog Boss Battle%s' % (
            goal, '' if goal == 1 else 's')
    return 'Complete %s Club Actions' % goal


def calculateDifficulty(club):
    """Reproduce Clash's Club-size task difficulty calculation."""
    members = club.get('members', []) if club else []
    memberCount = max(1, len(members))
    clubLevel = max(1, int((club or {}).get('level', 1)))

    # Clash prevents high-level Clubs from receiving trivial tasks even after
    # members leave, while still basing normal scaling on active Club size.
    minToonCount = max(1, min(int(math.ceil(clubLevel / 4.0)),
                              MAX_EFFECTIVE_TOON_COUNT))
    toonCount = max(minToonCount, memberCount)
    scaledCount = int(math.ceil(toonCount * TASK_DIFFICULTY_COEFFICIENT))
    return max(1, int(round((scaledCount + 1) ** 1.06)))


def _objectiveFromChainId(chainId):
    chainId = int(chainId)
    seed = chainId % 1000000
    rng = random.Random(seed)
    return OBJECTIVE_TYPES[rng.randrange(len(OBJECTIVE_TYPES))]


def taskFromChainId(chainId, progress=0, generatedAt=None):
    chainId = int(chainId)
    difficulty = max(1, chainId // 1000000)
    progressType = _objectiveFromChainId(chainId)
    goal = _goalForObjective(progressType, difficulty)
    reward = ClubTaskPricing.calculateTaskReward(chainId)
    return {
        'taskVersion': TASK_VERSION,
        'chainId': chainId,
        # taskId remains for compatibility with older Altis UI/callers.
        'taskId': chainId,
        'name': _nameForObjective(progressType, goal),
        'progressType': progressType,
        'goal': int(goal),
        'progress': max(0, min(int(goal), int(progress))),
        'rewardCoins': int(reward),
        'rewardExp': int(ClubTaskPricing.calculateTaskExperience(chainId)),
        'rerollCost': ClubTaskPricing.calculateRerollCost(chainId),
        # Current generated tasks remain active until completion or reroll.
        'endTime': 0,
        'generatedAt': int(generatedAt or time.time()),
    }


def isGeneratedTask(task):
    if not isinstance(task, dict):
        return False
    try:
        return (
            int(task.get('taskVersion', 0)) == TASK_VERSION and
            int(task.get('chainId', 0)) >= 1000000 and
            str(task.get('progressType', '')) in OBJECTIVE_TYPES
        )
    except:
        return False


def normaliseTask(task):
    if not isGeneratedTask(task):
        return None
    rebuilt = taskFromChainId(
        int(task.get('chainId', 0)),
        progress=int(task.get('progress', 0)),
        generatedAt=int(task.get('generatedAt', int(time.time()))),
    )
    return rebuilt


def generateTask(club, otherTasks=None, ignoreObjectiveTypes=None):
    otherTasks = otherTasks or []
    ignoreObjectiveTypes = ignoreObjectiveTypes or []
    existingTypes = [
        task.get('progressType') for task in otherTasks
        if isinstance(task, dict) and task.get('progressType')
    ]
    difficulty = calculateDifficulty(club)
    fallback = None

    for attempt in range(16):
        seed = random.randint(0, 999999)
        chainId = (difficulty * 1000000) + seed
        task = taskFromChainId(chainId)
        fallback = task

        # Match Clash: strongly avoid duplicate objective classes during the
        # first attempts, then relax this if the pool cannot satisfy it.
        if attempt < 8 and task['progressType'] in (
                existingTypes + list(ignoreObjectiveTypes)):
            continue
        return task

    return fallback or taskFromChainId((difficulty * 1000000) + 1)


def makeClubTasks(club, rerollIndices=None):
    """Return exactly three valid shared tasks for a Club.

    Existing generated task progress is preserved.  Legacy purchased Altis
    tasks are migrated to the current generated format.  Indices supplied in
    rerollIndices are replaced in-place while the other slots remain intact.
    """
    rerollIndices = set(int(index) for index in (rerollIndices or []))
    sourceTasks = list((club or {}).get('tasks', []))
    tasks = [None] * TASK_COUNT
    ignoredTypes = []

    for index in range(TASK_COUNT):
        source = sourceTasks[index] if index < len(sourceTasks) else None
        normalised = normaliseTask(source)
        if index in rerollIndices:
            if normalised is not None:
                ignoredTypes.append(normalised.get('progressType'))
            normalised = None
        tasks[index] = normalised

    for index in range(TASK_COUNT):
        if tasks[index] is not None:
            continue
        otherTasks = [task for taskIndex, task in enumerate(tasks)
                      if taskIndex != index and task is not None]
        tasks[index] = generateTask(
            club,
            otherTasks=otherTasks,
            ignoreObjectiveTypes=ignoredTypes,
        )

    return tasks
