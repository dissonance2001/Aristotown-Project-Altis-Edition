'''
This file contains a collection of functions to manage battle
experience and generation of reward movies on the client side.

These functions used to be methods on ClashBattleBase and
Movie, but they have been pulled out here to collect them together
and generalize them for final battles, which might have as many as 8
Toons.
'''

def genRewardDicts(entries):
    toonRewardDicts = []
    for toonId, origExp, earnedExp, origQuests, origMerits, merits, parts in entries:
        if toonId != -1:
            adict = {}
            toon = base.cr.doId2do.get(toonId)
            if toon is None:
                continue
            adict['toon'] = toon
            adict['origExp'] = origExp
            adict['earnedExp'] = earnedExp
            adict['origQuests'] = origQuests
            adict['origMerits'] = origMerits
            adict['merits'] = merits
            adict['parts'] = parts
            toonRewardDicts.append(adict)

    return toonRewardDicts
