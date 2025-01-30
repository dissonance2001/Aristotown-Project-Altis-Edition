def doOceanliner(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']

    ship = globalPropPool.getProp('ship')
    freeCruiseDelay = 3.1
    suitTrack = getSuitAnimTrack(attack)
    objZOffset = 0.0
    landFrames = 2
    node = ship.node()
    node.setBounds(OmniBoundingVolume())
    node.setFinal(1)
    shipTrack = Sequence()

    def posObject(object, toon, miss, battle=battle):
        object.reparentTo(battle)
        object.setPos(toon.getPos(battle))
        object.setHpr(toon.getHpr(battle))
        if miss:
            object.setY(object.getY(battle) - 5)
        object.setZ(object.getPos(battle)[2] + objZOffset)

    shipTrack.append(Func(battle.movie.needRestoreRenderProp, ship))
    shipTrack.append(Wait(2.86 + freeCruiseDelay))
    closestTarget = -1
    nearestDistance = 100000.0
    for i in xrange(len(targets)):
        toon = targets[i]['toon']
        toonPos = toon.getPos(battle)
        displacement = Vec3(MovieUtil.calcAvgToonPos(attack))
        displacement -= toonPos
        distance = displacement.lengthSquared()
        if distance < nearestDistance:
            closestTarget = i
            nearestDistance = distance

    hitAtleastOneToon = 1
    shipTrack.append(Func(posObject, ship, targets[closestTarget]['toon'], not hitAtleastOneToon))
    if hitAtleastOneToon:
        if hasattr(ship, 'getAnimControls'):
            pass  # Not imperative at the moment given the Toontanic does not have the getAnimControls attribute
        else:
            startingScale = 1.0
            ship2 = MovieUtil.copyProp(ship)
            posObject(ship2, targets[closestTarget]['toon'], not hitAtleastOneToon)
            endingPos = ship2.getPos()
            startPos = Point3(endingPos[0], endingPos[1], endingPos[2] + 5)
            startHpr = ship2.getHpr()
            endHpr = Point3(startHpr[0] + 90, startHpr[1], startHpr[2])
            animProp = LerpPosInterval(ship, landFrames / 24.0, endingPos, startPos=startPos)
            shrinkProp = LerpScaleInterval(ship, 0.1, MovieUtil.PNT3_NEARZERO, startScale=startingScale)
            bounceProp = Effects.createZBounce(ship, 2, endingPos, 0.5, 1.5)
            objAnimShrink = Sequence(Func(ship.setScale, startingScale), Func(ship.setH, endHpr[0]), animProp,
                                     bounceProp, Wait(1.5), shrinkProp)
            shipTrack.append(objAnimShrink)
            MovieUtil.removeProp(ship2)
    elif hasattr(ship, 'getAnimControls'):
        pass  # Not imperative at the moment given the Toontanic does not have the getAnimControls attribute
    else:
        startingScale = 1.0
        ship2 = MovieUtil.copyProp(ship)
        posObject(ship2, targets[closestTarget]['toon'], not hitAtleastOneToon)
        endingPos = ship2.getPos()
        startPos = Point3(endingPos[0], endingPos[1], endingPos[2] + 5)
        startHpr = ship2.getHpr()
        endHpr = Point3(startHpr[0] + 90, startHpr[1], startHpr[2])
        animProp = LerpPosInterval(ship, landFrames / 24.0, endingPos, startPos=startPos)
        shrinkProp = LerpScaleInterval(ship, 0.1, MovieUtil.PNT3_NEARZERO, startScale=startingScale)
        bounceProp = Effects.createZBounce(ship, 2, endingPos, 0.5, 1.5)
        objAnimShrink = Sequence(Func(ship.setScale, startingScale), Func(ship.setH, endHpr[0]), animProp, bounceProp,
                                 Wait(1.5), shrinkProp)
        shipTrack.append(objAnimShrink)
        MovieUtil.removeProp(ship2)
    shipTrack.append(Func(MovieUtil.removeProp, ship))
    shipTrack.append(Func(battle.movie.clearRenderProp, ship))
    dropShadow = MovieUtil.copyProp(targets[closestTarget]['toon'].dropShadow)
    dropShadow.setScale(3.6)

    def posShadow(dropShadow=dropShadow, toon=toon, battle=battle, hp=targets[0]['hp']):
        dropShadow.reparentTo(battle)
        dropShadow.setPos(toon.getPos(battle))
        dropShadow.setHpr(toon.getHpr(battle))
        if hp == 0:
            dropShadow.setY(dropShadow.getY(battle) - 5)
        dropShadow.setZ(dropShadow.getZ() + 0.5)

    shadowTrack = Sequence(
        Wait(1.0 + freeCruiseDelay),
        Func(battle.movie.needRestoreRenderProp, dropShadow),
        Func(posShadow),
        LerpScaleInterval(dropShadow, 1.86, dropShadow.getScale(), startScale=MovieUtil.PNT3_NEARZERO),
        Wait(0.3),
        Func(MovieUtil.removeProp, dropShadow),
        Func(battle.movie.clearRenderProp, dropShadow)
    )
    toonTracks = getToonTracks(attack, damageDelay=2.86 + freeCruiseDelay, damageAnimNames=['slip-forward'],
                               dodgeDelay=2.86 + freeCruiseDelay)
    soundTrack = getSoundTrack('AA_drop_boat%s.ogg' % ('' if hitAtleastOneToon else '_miss'),
                               delay=(0.9 if targets[0]['hp'] == 0 else 1.0) + freeCruiseDelay, node=suit)
    hitSounds = Parallel()
    hitSounds.append(getSoundTrack('AA_drop_boat_cog.ogg', delay=2.86 + freeCruiseDelay))
    multiTrackList = Parallel(suitTrack, shipTrack, shadowTrack, toonTracks, soundTrack, hitSounds)
    multiTrackList.append(getSoundTrack('AA_heal_happydance.ogg', node=suit))
    return multiTrackList