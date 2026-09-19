from enum import IntEnum, auto


class BattleMovieListenerEnum(IntEnum):
    EVENT_ON_SOAKED = auto()
    # TODO: Add suit_died and suit_predied to custom cog deaths within cog battle movies
    # These are:
    # erfit revive, barnburner, cut the slack, offboarding, layoffs, rainmaker ending 1
    EVENT_SUIT_PREDIED = auto()  # Empty sequence right before the suit goes and dies
    EVENT_SUIT_DIED = auto()
    EVENT_ROUND_DONE = auto()


# Shorthand
BMLE = BattleMovieListenerEnum
