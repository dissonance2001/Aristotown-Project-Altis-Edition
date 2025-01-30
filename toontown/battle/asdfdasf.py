taunt = random.choice(
        ["I'm going to take you by storm.", "I forecast rain.", "Hope you packed your umbrella!",
         "I want to enlighten you.", "I have a torrent of great ideas.",
         "I call this a lightning attack.", "How about a few rain DROPS?", "Ready for a downpour?",
         "I love to be a wet blanket."])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    suitTrack = Sequence(ActorInterval(suit, 'effort', playRate=1.25))