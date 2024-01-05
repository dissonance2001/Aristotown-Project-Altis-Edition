def doClockChange(attack):
    suit = attack['suit']
    battle = attack['battle']

    cameraTrack = Sequence(LerpPosHprInterval(camera, duration=0.95, pos=Point3(0, -15, 2), hpr=Point3(0, 0, 0), blendType='easeInOut'))
    suitTrack = Sequence(getSuitAnimTrack(attack))
    toonTracks = getToonTracks(attack, suitTrack.getDuration() - 1.5, ['slip-backward'], suitTrack.getDuration() - 1.5, ['shrug'])
    soundTrack = getSoundTrack('SA_clock_trigger.ogg', node=suit)
    return Parallel(cameraTrack, suitTrack, toonTracks, soundTrack)