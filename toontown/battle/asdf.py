
tauntIndex = attack['taunt']
taunt = getAttackTaunt(attack['name'], tauntIndex)
suitTrack = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout),
                         ActorInterval(suit, attack['animName'], playRate=1.25))