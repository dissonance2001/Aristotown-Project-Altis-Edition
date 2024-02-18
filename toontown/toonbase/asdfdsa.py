def doCage(attack):
    battle = attack['battle']
    suitTrack = getSuitTrack(attack, animNames=['glower'])
    cagePropTracks = Parallel()
    for t in attack['target']:
        toon = t['toon']
        dmg = t['hp']
        cage = loader.loadModel('phase_5/models/cogdominium/tt_m_ara_crg_toonCage')
        toonPos = toon.getPos(battle)
        y = toonPos.getY()
        if dmg == 0:
            y -= 5
        cagePos = [Point3(toonPos.getX(), y, 20.0), toon.getHpr(battle)]
        cagePropTrack = Sequence(
            getPropAppearTrack(cage, battle, cagePos, 0.01, scaleUpPoint=Point3(0.4), scaleUpTime=1.0),
            Parallel(
                cage.posInterval(0.75, Point3(toonPos.getX(), y, 0.01), blendType='easeIn'),
                SoundInterval(base.loader.loadSfx('phase_5/audio/sfx/CHQ_SOS_cage_lower.ogg'), duration=0.75, node=cage)
            ),
            Func(base.playSfx, base.loader.loadSfx('phase_9/audio/sfx/CHQ_SOS_cage_land.ogg'), node=cage),
            Wait(1.5),
            LerpFunctionInterval(cage.setAlphaScale, fromData=1, toData=0, duration=1.0),
            Func(MovieUtil.removeProp, cage)
        )
        cagePropTracks.append(cagePropTrack)
    damageAnims = [['duck', 0.0001, 1.3]]
    toonTracks = getToonTracks(attack, damageDelay=1.5, splicedDamageAnims=damageAnims, dodgeDelay=1.75, dodgeAnimNames=[], splicedDodgeAnims=[], showDamageExtraTime=0.5)
    return Parallel(suitTrack, cagePropTracks, toonTracks)