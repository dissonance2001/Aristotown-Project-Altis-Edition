"""Contains all constants relevant to toon stats."""

from enum import IntEnum


class ToonStats(IntEnum):
    COGS          = 0
    BLDGS         = 1
    ELITES        = 2
    FRIENDS       = 3
    CURR_FRIENDS  = 4
    TASKS         = 5
    VP            = 6
    CFO           = 7
    CJ            = 8
    CEO           = 9
    CM            = 10
    GONE_SAD      = 11
    CATALOG       = 12
    FISH          = 13
    TROLLEY       = 14
    GAGS          = 15
    TREASURES     = 16
    JB_SPENT      = 17
    JB_EARNED     = 18
    IOUS          = 19
    UNITES        = 20
    UNUSED_2      = 21
    FIRES         = 22
    FACTORIES     = 23
    MINTS         = 24
    STAGES        = 25
    CLUBS         = 26
    UNUSED_3      = 27
    SUES          = 28
    DAILY_TASKS   = 29
    PIZZA_POINTS  = 30
    COUNTERFEITS  = 31


# The total amount of stats. (updates dynamically)
TOTAL_STATS = len(ToonStats)
