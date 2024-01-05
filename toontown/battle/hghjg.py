def doPoisonSpray(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target['hp']
    theSuit = None
    for s in battle.suits:
        if s.dna.name == 'ste':
            print('Found manager... using it...')
            theSuit = s
        elif s.dna.name == 'lit':
            print('Found manager... using it...')
            theSuit = s
        elif s.dna.name == 'csm':
            print('Found manager... using it...')
            theSuit = s


    if theSuit == None:
        print('Error finding manager... using self...')
        theSuit = suit

    print('*************************************')

    print('suit.currHP %i' % int(suit.currHP))
    print('setHP() %i' % int(suit.currHP - 800))
    suit.setHealthForMe(int(suit.currHP - 800))
    print('suit.currHP %i' % int(suit.currHP))

    print('ts.currHP %i' % int(theSuit.currHP))
    print('setHP() %i' % int(theSuit.currHP + 800))
    theSuit.setHealthForMe(int(theSuit.currHP + 800))
    print('ts.currHP %i' % int(theSuit.currHP))

    suitTrack = Sequence(getSuitAnimTrack(attack), ActorInterval(attack['suit'], 'neutral'))
    soundTrack = Sequence(SoundInterval(globalBattleSoundCache.getSound('SA_defense.ogg'), node=suit))
    selfDamageTrack = Sequence(Wait(2), Func(suit.showHpText, -800), Func(suit.updateHealthBar, 0))
    managerHealTrack = Sequence(Wait(2), Func(theSuit.showHpText, 800), Func(theSuit.updateHealthBar, 0),
                                SoundInterval(globalBattleSoundCache.getSound('LB_toonup.ogg'), node=theSuit))
    return Parallel(suitTrack, soundTrack, selfDamageTrack, managerHealTrack)