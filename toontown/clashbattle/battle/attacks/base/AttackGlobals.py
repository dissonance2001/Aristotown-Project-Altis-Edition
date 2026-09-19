"""Contains constants which can be used for any type of attack."""

from toontown.toonbase import TTLocalizer


def getTauntPool(suit, attackType: int, rounds: int, tauntIndex: int=0):
    taunts = None

    def getAttackTypeTaunts(suitTaunts):
        return suitTaunts.get(attackType, TTLocalizer.SuitAttackTaunts.get(attackType))

    # Check if we have any sort of custom taunt replacement
    if suit and suit.getStyleName() in TTLocalizer.SuitAttackSpecificTaunts:
        baseTaunts = TTLocalizer.SuitAttackSpecificTaunts[suit.getStyleName()]
        # First, check if we have a pool of taunts that replace *all* taunts
        if 'all' in baseTaunts:
            taunts = baseTaunts['all']
        # Next, check if we have a round-based taunt replacement.
        elif 'rounds' in baseTaunts and rounds is not None:
            # Is our current round in the round pool?
            if rounds in baseTaunts['rounds']:
                taunts = baseTaunts['rounds'][rounds]
            # Rounds not in the dictionary, check if we have an "after rounds" key.
            # If we do, and our rounds is greater than whatever was in the rounds dict,
            # Then 'after rounds' will be our pool for the rest of the battle.
            elif 'afterrounds' in baseTaunts:
                finalTauntRound = max(list(baseTaunts['rounds'].keys()))
                # Our current round is greater than the final round that has a round-specific taunt.
                # That means we should use the 'after rounds' taunt pool.
                if rounds > finalTauntRound:
                    taunts = baseTaunts['afterrounds']
        # Everything else failed, check for attack-specific taunts
        if taunts is None:
            taunts = getAttackTypeTaunts(baseTaunts)
    else:
        taunts = TTLocalizer.SuitAttackTaunts.get(attackType)

    if taunts is None:
        taunts = []
    if type(taunts) not in (list, tuple):
        taunts = [taunts]

    # If the taunt list contains a list of lists,
    # index into the list based on the taunt index provided.
    if taunts and isinstance(taunts[0], (tuple, list)):
        taunts = taunts[tauntIndex]

    return taunts
