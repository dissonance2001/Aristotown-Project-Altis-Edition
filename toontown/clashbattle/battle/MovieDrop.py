from direct.interval.IntervalGlobal import *
from direct.showutil import Effects

from toontown.audio.IsolatedSoundInterval import IsolatedSoundInterval
from toontown.battle import MovieUtil
from toontown.battle.BattleBase import *
from toontown.battle.BattleProps import *
from toontown.battle.BattleSounds import *
from toontown.battle.MovieUtil import calcAvgSuitPos
from toontown.battle.movielistener.BattleMovieListenerEnum import BMLE
from toontown.suit.SuitDNA import getSuitBodyType
from toontown.utils.DirectNotifyCategory import getNotify

notify = getNotify('MovieDrop')

hitSoundFiles  = ('AA_drop_flowerpot.ogg',
                  'AA_drop_sandbag.ogg',
                  'AA_drop_bowling_ball.ogg',
                  'AA_drop_anvil.ogg',
                  'AA_drop_bigweight.ogg',
                  'AA_drop_safe.ogg',
                  'AA_drop_boulder.ogg',
                  'AA_drop_piano.ogg',
                  'AA_drop_boat.ogg')
 
missSoundFiles  = ('AA_drop_flowerpot_miss.ogg',
                   'AA_drop_sandbag_miss.ogg',
                   'AA_drop_bigweight_miss.ogg',
                   'AA_drop_anvil_miss.ogg',
                   'AA_drop_bigweight_miss.ogg',
                   'AA_drop_safe_miss.ogg',
                   'AA_drop_boulder_miss.ogg',
                   'AA_drop_piano_miss.ogg',
                   'AA_drop_boat_miss.ogg')
                  
# Time offsets
tDropShadow     = 1.30
tSuitDodges     = 2.45 + tDropShadow
tObjectAppears  = 3.00 + tDropShadow
tButtonPressed  = 2.44

# Durations
dShrink         = 0.3
dShrinkOnMiss   = 0.1
dPropFall       = 0.6

# Battle Prop names
objects = ('flowerpot',
           'sandbag',
           'bowling_ball',
           'anvil',
           'weight',
           'safe',
           'boulder',
           'piano',
           'ship')

objZOffsets         = (0.75, 0.75, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)  # Offsets for gags when landing
objStartingScales   = (1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0)    # Starting scale of gag as it begins to shrink away. This should almost always be 1.0
landFrames          = (12, 4, 1, 1, 11, 11, 11, 11, 2)                      # The animation frame of the prop actor in which impact occurs with the ground
shoulderHeights     = {'a': 13.28 / 4.0,
                       'b': 13.74 / 4.0,
                       'c': 10.02 / 4.0}


def doDrops(drops):
    """ Drops occur in the following order:
        a) by suit, in order of increasing number of drops per suit
          1) level 1 drops, right to left, (TOON_DROP_DELAY later)
          2) level 2 drops, right to left, (TOON_DROP_DELAY later)
          3) level 3 drops, right to left, (TOON_DROP_DELAY later)
          etc.
        b) next suit, (TOON_DROP_SUIT_DELAY later)
    """
    if len(drops) == 0:
        return (None, None)
    major = 0
    
    # Group the drops by targeted suit
    suitDropsDict = OrderedDict()
    groupDrops = []
    hasUber = False
    suitsDied = {}
    for drop in drops:
        track = drop['track']
        level = drop['level']
        targets = drop['target']

        if level == UBER_GAG_LEVEL_INDEX:
            hasUber = True

        if len(targets) == 1:
            suitId = targets[0]['suit'].doId
            suitDied = targets[0]['died']
            if suitDied != 0 and suitId not in suitsDied:
                suitsDied[suitId] = 1
            if suitId in suitDropsDict:
                if level >= 4:
                    major += 1
                suitDropsDict[suitId].append((drop, targets[0]))
            else:
                suitDropsDict[suitId] = [(drop, targets[0])]
                major = 0
        elif level == UBER_GAG_LEVEL_INDEX:
            for target in targets:
                suitId = target['suit'].doId
                suitDied = target['died']
                if suitDied != 0 and suitId not in suitsDied:
                    suitsDied[suitId] = 1
            groupDrops.append(drop)
        else:
            # We're dealing with a multi target drop
            for target in targets:
                suitId = target['suit'].doId
                suitDied = target['died']
                if suitDied != 0 and suitId not in suitsDied:
                    suitsDied[suitId] = 1
                if suitId in suitDropsDict:
                    if level >= 4:
                        major += 1
                    otherDrops = suitDropsDict[suitId]
                    alreadyInList = 0
                    for oDrop in otherDrops:
                        if oDrop[0]["avatar"] == drop["avatar"]:
                            alreadyInList = 1

                    if alreadyInList == 0:
                        suitDropsDict[suitId].append((drop, target))
                else:
                    suitDropsDict[suitId] = [(drop, target)]

    suitDrops = list(suitDropsDict.values())
    suitDrops.sort(key=len)

    delay = 0.0
    mtrack = Parallel(name='toplevel-drop')
    for st in suitDrops:
        if len(st) > 0:
            ival = __doSuitDrops(st, major, hasUber)
            if ival:
                mtrack.append(Sequence(Wait(delay), ival))
            delay = random.random() * 0.3

    # We do the group drops after all the single drops have gone
    if groupDrops:
        ival = __doGroupDrops(groupDrops, major, suitsDied, delay)
        mtrack.append(ival)

    camDuration = mtrack.getDuration()
    camTrack = drops[0]['battle'].camera.chooseDropShot(drops, suitDropsDict, camDuration)
    return (mtrack, camTrack)


def __getSoundTrack(level, hitSuit, delay, node=None, duration=None):
    # level: the level of attack, int 0-8
    # hitSuit: does the attack hit toon, bool
    if hitSuit:
        soundEffect = globalBattleSoundCache.getSound(hitSoundFiles[level])
    else:
        soundEffect = globalBattleSoundCache.getSound(missSoundFiles[level])
        
    soundTrack = Sequence()
    
    if soundEffect:
        buttonSound = globalBattleSoundCache.getSound('AA_drop_trigger_box.ogg')
        fallingSound = None
        buttonDelay = tButtonPressed - 0.3
        fallingDuration = 1.5
        if not level == UBER_GAG_LEVEL_INDEX:
            # Toontanic has the whistle in it's sfx already
            fallingSound = globalBattleSoundCache.getSound('incoming_whistleALT.ogg')

        soundTrack.append(Wait(buttonDelay + delay))
        soundTrack.append(SoundInterval(buttonSound, duration=0.67, node=node))
        if fallingSound:
            soundTrack.append(SoundInterval(fallingSound, duration=fallingDuration, node=node))
        if not level == UBER_GAG_LEVEL_INDEX:
            # The dropping effects seem to be timed at the start of the press, not after
            if duration:
                soundTrack.append(SoundInterval(soundEffect, node=node, duration=duration))
            else:
                soundTrack.append(SoundInterval(soundEffect, node=node))

        if level == UBER_GAG_LEVEL_INDEX:
            if hitSuit:
                uberDelay = tButtonPressed
            else:
                uberDelay = tButtonPressed - 0.1
            oldSoundTrack = soundTrack
            soundTrack = Parallel()
            soundTrack.append(oldSoundTrack)

            uberTrack = Sequence()
            uberTrack.append(Wait(uberDelay + delay))
            uberTrack.append(SoundInterval(soundEffect, node=node))

            soundTrack.append(uberTrack)
    else:
        soundTrack.append(Wait(0.1))  # Dummy interval in case sfx is not found
    return soundTrack


def __doSuitDrops(dropTargetPairs, major, hasUber=False):
    """ __doSuitDrops(drops) 
        1 or more toons drop at the same target suit
        Note: attacks are sorted by increasing level (as are toons)
        Returns a track with toon drops in the following order:
        1) level 1 drops, right to left, (TOON_DROP_DELAY later)
        2) level 2 drops, right to left, (TOON_DROP_DELAY later)
        etc.
    """
    toonTracks = Parallel()
    delay = 0.0
    alreadyDodged = 0
    alreadyTeased = 0
    hasDied = sum([drop[1]['died'] for drop in dropTargetPairs]) > 0
    lastDrop = [drop[0] for drop in dropTargetPairs if drop[1]['landed']]
    lastDrop = lastDrop[-1] if lastDrop else dropTargetPairs[-1][0]
    diedObjectIsMajor = lastDrop['level'] >= 4
    for dropTargetPair in dropTargetPairs:
        drop = dropTargetPair[0]
        level = drop['level']
        objName = objects[level]
        target = dropTargetPair[1]
        last = drop == lastDrop and hasDied
        suit = target['suit']
        # Don't do the big drop effect if:
        # suit is virtual or
        # there is a boat but this drop isn't the boat or
        # suit has a different special death animation
        currHasDied = hasDied and (not hasUber or (hasUber and level == UBER_GAG_LEVEL_INDEX)) and not MovieUtil.shouldOverrideSuitDeath(suit)
        track = __dropObjectForSingle(drop, delay, objName, level, alreadyDodged, alreadyTeased, target, major, last, currHasDied, diedObjectIsMajor, hasUber)
        if track:
            toonTracks.append(track)
            delay += TOON_DROP_DELAY
        # Only allow teasing on the first drop
        alreadyTeased = 1

    return toonTracks


def __doGroupDrops(groupDrops, major, suitsDied, delay):
    """ __doGroupDrops(drops) 
        1 or more toons drop at the same target suits
        Note: attacks are sorted by increasing level (as are toons)
        Returns a track with toon drops in the following order:
        1) level 1 drops, right to left, (TOON_DROP_DELAY later)
        2) level 2 drops, right to left, (TOON_DROP_DELAY later)
        etc.
    """
    toonTracks = Parallel()
    alreadyDodged = 0
    alreadyTeased = 0
    for drop in groupDrops:
        battle = drop['battle']
        level = drop['level']
        # Calculate center position, then figure out which suit is closest to it
        centerPos = calcAvgSuitPos(drop)
        targets = drop['target']
        numTargets = len(targets)
        closestTarget = -1
        nearestDistance = 100000.0
        for i in range(numTargets):
            suit = drop['target'][i]['suit']
            suitPos = suit.getPos(battle)
            displacement = Vec3(centerPos)
            displacement -= suitPos
            distance = displacement.lengthSquared()
            if distance < nearestDistance:
                closestTarget = i
                nearestDistance = distance

        # We have the suit to drop on
        track = __dropGroupObject(drop, delay, closestTarget, alreadyDodged, alreadyTeased, major, suitsDied)
        # Use our delay so that the toontanic does not come before or at the same time as another toon's drop
        if track:
            toonTracks.append(track)
            delay = delay + TOON_DROP_SUIT_DELAY
        if drop['sidestep'] == 1:
            if level >= 4:
                alreadyTeased = 1
            else:
                alreadyDodged = 1

    return toonTracks


def __dropGroupObject(drop, delay, closestTarget, alreadyDodged, alreadyTeased, major, suitsDied):
    level = drop['level']
    objName = objects[level]
    target = drop['target'][closestTarget]
    returnedParallel = __dropObject(drop, delay, objName, level, alreadyDodged, alreadyTeased, target, major)
    for i in range(len(drop['target'])):
        target = drop['target'][i]
        suit = target['suit']
        last = True
        # Only show the special squish animation if they aren't a virtual and don't have a special death animation
        hasDied = suit.doId in suitsDied and not MovieUtil.shouldOverrideSuitDeath(suit)
        # It's a huge drop (boat), so it is going to be a major object.
        diedObjectIsMajor = True
        suitTrack = __createSuitTrack(drop, delay, level, alreadyDodged, alreadyTeased, target, major, last, hasDied, diedObjectIsMajor)
        if suitTrack:
            returnedParallel.append(suitTrack)

    return returnedParallel


def __dropObjectForSingle(drop, delay, objName, level, alreadyDodged, alreadyTeased, target, major, last, hasDied, diedObjectIsMajor, hasUber):
    singleDropParallel = __dropObject(drop, delay, objName, level, alreadyDodged, alreadyTeased, target, major, last, hasDied, diedObjectIsMajor, hasUber)
    suitTrack = __createSuitTrack(drop, delay, level, alreadyDodged, alreadyTeased, target, major, last, hasDied, diedObjectIsMajor, hasUber)
    if suitTrack:
        singleDropParallel.append(suitTrack)
    return singleDropParallel


def __dropObject(drop, delay, objName, level, alreadyDodged, alreadyTeased, target, major, last=False, hasDied=False, diedObjectIsMajor=False, hasUber=False):
    toon = drop["avatar"]
    battle = drop['battle']
    origHpr = toon.getHpr(battle)
    suit = target['suit']
    hp = target['hp']
    majorObject = level >= 4
    died = target['died']
    hitSuit = drop['sidestep'] == 0
    leftSuits = target['leftSuits']
    rightSuits = target['rightSuits']
    kbbonus = target['kbbonus']
    suitPos = suit.getPos(battle)

    button = globalPropPool.getProp('drop-button')
    buttons = [button]
    hands = toon.getLeftHands()
    obj = globalPropPool.getProp(objName)
    objectType = globalPropPool.getPropType(objName)
    
    # The weight, safe, and boulder are a bit too big
    if objName == 'weight':
        obj.setScale(obj.getScale() * 0.75)
    elif objName == 'safe':
        obj.setScale(obj.getScale() * 0.85)
    elif objName == 'boulder':
        obj.setScale(obj.getScale() * 0.675)

    # The object will likely animate far from its initial bounding
    # volume while it drops.  To work around this bug, we artificially
    # change the object's bounding volume to be really big.  In fact,
    # we make it infinite, so it will never be culled while it's
    # onscreen.
    node = obj.node()
    node.setBounds(OmniBoundingVolume())
    node.setFinal(1)
    wantEarlyEnd = (hasUber and level != UBER_GAG_LEVEL_INDEX) or (hasDied and diedObjectIsMajor)
    duration = 2.0 if wantEarlyEnd else None
    # Create the soundTrack
    soundTrack = __getSoundTrack(level, hitSuit, delay, toon, duration)

    # Toon pulls the button out, presses it, and puts it away
    toonTrack = Sequence()

    toonFace = Func(toon.headsUp, suit)
    toonTrack.append(Wait(delay))
    toonTrack.append(toonFace)
    toonTrack.append(Parallel(ActorInterval(toon, 'pushbutton'), ActorInterval(button, 'drop-button')))
    toonTrack.append(Func(toon.loop, 'neutral'))
    toonTrack.append(Func(toon.setHpr, battle, origHpr))
        
    # Button scales up in Toon's hand as they take it out, and
    # scales down to nothing as it is put away
    buttonTrack = Sequence()

    buttonShow = Func(MovieUtil.showProps, buttons, hands)
    buttonScaleUp = LerpScaleInterval(button, 1.0, button.getScale(), startScale=Point3(0.01, 0.01, 0.01))
    buttonScaleDown = LerpScaleInterval(button, 1.0, Point3(0.01, 0.01, 0.01), startScale=button.getScale())
    buttonHide = Func(MovieUtil.removeProps, buttons)
    buttonTrack.append(Wait(delay))
    buttonTrack.append(buttonShow)
    buttonTrack.append(buttonScaleUp)
    buttonTrack.append(Wait(2.5))
    buttonTrack.append(buttonScaleDown)
    buttonTrack.append(buttonHide)
        
    # Object appears above Suit
    objectTrack = Sequence()

    def posObject(obj, suit, level, majorObject, miss, battle = battle):
        obj.reparentTo(battle)
        # Options for positioning a drop:
        #   1) Any successful drop on an unlured suit - strikes at suit battle pos
        #   2) Unsuccessful drops on an unlured suit that are of the largest three -
        #      these strike behind the suit (who shouldn't dodge)
        #   3) The first three (smallest drops) on a lured suit strike the battle pos,
        #      where the larger ones get bumped back a bit.
        if suit.isLured:
            suitPos, suitHpr = battle.getActorPosHpr(suit)
            obj.setPos(suitPos)
            obj.setHpr(suitHpr)
            obj.setY(obj.getY() + 2)
        else:
            obj.setPos(suit.getPos(battle))
            obj.setHpr(suit.getHpr(battle))
            if miss:
                obj.setY(obj.getY(battle) + 5)
        if not majorObject:
            if not miss:
                shoulderHeight = shoulderHeights[suit.style.body] * suit.scale
                obj.setZ(obj.getPos(battle)[2] + shoulderHeight)
        # Fix up the Z offset of the prop
        obj.setZ(obj.getPos(battle)[2] + objZOffsets[level])

    # The object will need to scale down to nothing at some point
    # and then it will immediately get deleted.
    # Since we already have an animation interval playing,
    # we need to put the scale on a separate track.
    # to avoid cases where the object has been deleted,
    # and the scale interval is still trying to scale the
    # object, we'll put the animation and scale intervals into
    # separate tracks, combine them into a track, and
    # put the hide interval after the track.
    objectTrack.append(Func(battle.movie.needRestoreRenderProp, obj))
    objInit = Func(posObject, obj, suit, level, majorObject, not hitSuit)
    objectTrack.append(Wait(delay + tObjectAppears))
    objectTrack.append(objInit)

    def animControlsHitDrop():
        # Prop hits the Suit
        animProp = ActorInterval(obj, objName)
        shrinkProp = LerpScaleInterval(obj, dShrink, Point3(0.01, 0.01, 0.01), startScale=obj.getScale())
        objAnimShrink = ParallelEndTogether(animProp, shrinkProp)
        objectTrack.append(objAnimShrink)

    def noAnimControlsHitDrop():
        # For non animated drop props. This was originally
        # used when the Toontanic used Donald's boat. However,
        # I'll leave it here in case we find a use for it
        # in the future
        startingScale = objStartingScales[level]
        # Increase the size of the ship based on the number of suits over 4.
        if objName == 'ship':
            obj.setScale(obj.getScale() * max(1.0, 1.0 + ((len(battle.activeSuits) - 4) * 0.15)))

        object2 = MovieUtil.copyProp(obj)
        posObject(object2, suit, level, majorObject, not hitSuit)
        endingPos = object2.getPos()
        startPos = Point3(endingPos[0], endingPos[1], endingPos[2] + 5)
        startHpr = object2.getHpr()
        endHpr = Point3(startHpr[0] + 90, startHpr[1], startHpr[2])
        animProp = LerpPosInterval(obj, landFrames[level] / 24.0, endingPos, startPos=startPos)
        shrinkProp = LerpScaleInterval(obj, dShrink, Point3(0.01, 0.01, 0.01), startScale=startingScale)
        bounceProp = Effects.createZBounce(obj, 2, endingPos, 0.5, 1.5)
        objAnimShrink = Sequence(Func(obj.setScale, startingScale), Func(obj.setH, endHpr[0]), animProp, bounceProp,
                                 Wait(1.5), shrinkProp)
        objectTrack.append(objAnimShrink)
        MovieUtil.removeProp(object2)

    def animControlsMissDrop():
        # Prop misses the Suit
        # Only play the animation up to the point where it lands
        animProp = ActorInterval(obj, objName, duration=landFrames[level] / 24.0)

        def poseProp(prop, animName, level):
            prop.pose(animName, landFrames[level])

        poseProp = Func(poseProp, obj, objName, level)
        wait = Wait(1.0)
        shrinkProp = LerpScaleInterval(obj, dShrinkOnMiss, Point3(0.01, 0.01, 0.01), startScale=obj.getScale())
        objectTrack.append(animProp)
        objectTrack.append(poseProp)
        objectTrack.append(wait)
        objectTrack.append(shrinkProp)

    def noAnimControlsMissDrop():
        # Prop misses the Suit
        # For non animated drop props. This was originally
        # used when the Toontanic used Donald's boat. However,
        # I'll leave it here in case we find a use for it
        # in the future
        startingScale = objStartingScales[level]
        object2 = MovieUtil.copyProp(obj)
        posObject(object2, suit, level, majorObject, not hitSuit)
        endingPos = object2.getPos()
        startPos = Point3(endingPos[0], endingPos[1], endingPos[2] + 5)
        startHpr = object2.getHpr()
        endHpr = Point3(startHpr[0] + 90, startHpr[1], startHpr[2])
        animProp = LerpPosInterval(obj, landFrames[level] / 24.0, endingPos, startPos=startPos)
        shrinkProp = LerpScaleInterval(obj, dShrinkOnMiss, Point3(0.01, 0.01, 0.01), startScale=startingScale)
        bounceProp = Effects.createZBounce(obj, 2, endingPos, 0.5, 1.5)
        objAnimShrink = Sequence(Func(obj.setScale, startingScale), Func(obj.setH, endHpr[0]), animProp, bounceProp,
                                 Wait(1.5), shrinkProp)
        objectTrack.append(objAnimShrink)
        MovieUtil.removeProp(object2)

    # Use the 'miss' drop animation under the following special circumstances:
    # If there is a boat and this drop isn't the boat, or
    # the cog died via a major object
    if (hasUber and level != UBER_GAG_LEVEL_INDEX) or (hitSuit and majorObject and diedObjectIsMajor and hasDied):
        if hasattr(obj, 'getAnimControls'):
            animControlsMissDrop()
        else:
            noAnimControlsMissDrop()
    # Use the 'normal' drop animation if the drop hit the suit, or if it is levels 2/3/4.
    elif hitSuit or level in (1, 2, 3):
        if hasattr(obj, 'getAnimControls'):
            animControlsHitDrop()
        else:
            noAnimControlsHitDrop()
    elif hasattr(obj, 'getAnimControls'):
        animControlsMissDrop()
    else:
        noAnimControlsMissDrop()

    objectTrack.append(Func(MovieUtil.removeProp, obj))
    objectTrack.append(Func(battle.movie.clearRenderProp, obj))
    # We will see a shadow scale up before the object drops
    if level == 4 or level == 5:  # Big weight and Safe uses square drop shadows
        dropShadow = loader.loadModel('phase_3/models/props/square_drop_shadow')  # I know I shouldn't use model load calls like this, but this prop is not in the BattleProp pool, and I don't want to add all of phase 3 for it.
        dropShadow.setColor(0.0, 0.0, 0.0, 0.5)
    else:
        dropShadow = MovieUtil.copyProp(suit.getShadowJoint())

    if level == 0:
        dropShadow.setScale(0.5)
    elif level <= 3:
        dropShadow.setScale(0.8)
    elif level == 4:
        dropShadow.setScale(0.8)
    elif level == 5:
        dropShadow.setScale(1.0)
    elif level == 6:
        dropShadow.setScale(2.3)
    else:
        dropShadow.setScale(3.6)

    def posShadow(dropShadow = dropShadow, suit = suit, battle = battle, hp = hp, level = level):
        dropShadow.reparentTo(battle)
        if suit.isLured:
            # Suit is lured, shadow at battle position
            suitPos, suitHpr = battle.getActorPosHpr(suit)
            dropShadow.setPos(suitPos)
            dropShadow.setHpr(suitHpr)
            if level >= 4: # Bump back larger drops
                dropShadow.setY(dropShadow.getY() + 2)
        else:
            dropShadow.setPos(suit.getPos(battle))
            dropShadow.setHpr(suit.getHpr(battle))
            if not hitSuit:
                dropShadow.setY(dropShadow.getY(battle) + 5)
        # Raise the drop shadow to curb level
        dropShadow.setZ(dropShadow.getZ() + 0.5)

    shadowTrack = Sequence(Wait(delay + tButtonPressed), Func(battle.movie.needRestoreRenderProp, dropShadow), Func(posShadow), LerpScaleInterval(dropShadow, tObjectAppears - tButtonPressed, dropShadow.getScale(), startScale=Point3(0.01, 0.01, 0.01)), Wait(0.3), Func(MovieUtil.removeProp, dropShadow), Func(battle.movie.clearRenderProp, dropShadow))
    return Parallel(toonTrack, soundTrack, buttonTrack, objectTrack, shadowTrack)


def __createSuitTrack(drop, delay, level, alreadyDodged, alreadyTeased, target, major, last=False, hasDied=False, diedObjectIsMajor=False, hasUber=False):
    toon = drop["avatar"]
    deathdelay = 0
    battle = drop['battle']

    majorObject = level >= 4
    suit = target['suit']
    hp = target['hp']
    hitSuit = drop['sidestep'] == 0
    died = target['died']
    revived = target['revived']
    leftSuits = target['leftSuits']
    rightSuits = target['rightSuits']
    kbbonus = target['kbbonus']
    hpbonus = target['hpbonus']
    deathdelay = 0

    # 4 options for a suit in a drop attack:
    #  1) A drop successfully lands
    #   a) If the suit is killed and it is minor drop, the Suit's head will explode, and wait
    #      for other drops to finish before dropping dead.
    #  2) It is lured, thus drop misses so suit does nothing (kbbonus == 0).  This is
    #     detected using a hack in the kbbonus.  There is no actual kickback bonus involved
    #     for drops, but if this kbbonus value is set to 0 instead of -1 (in the battle
    #     calculator), then we've specified that the suit is lured
    #  3) The suit dodges and is reacting to the first drop to dodge, detected when the
    #     variable alreadyDodged == 0
    #  4) The suit would dodge but is already dodging first drop, detected when the
    #     variable alreadyDodged == 1
    if hitSuit:
        # Suit takes damage (for each drop that hits)
        suitTrack = Sequence()
        suitReact = Sequence()
        showDamage = Func(suit.showHpText, hp, openEnded=0)
        updateHealthBar = Func(suit.updateHealthBar, hp)
        # We want this anim to end early if:
        # there's a boat and this drop is not the boat, or
        # our suit died and the death object is a big one
        # and they don't have a special death
        hasSpecialDeath = MovieUtil.shouldOverrideSuitDeath(suit)
        wantEarlyEnd = (hasUber and level != UBER_GAG_LEVEL_INDEX) or (hasDied and diedObjectIsMajor) and not hasSpecialDeath
        duration = TOON_DROP_DELAY - 0.1 if wantEarlyEnd else None
        if majorObject:
            if duration:
                suitReact.append(ActorInterval(suit, 'flatten', duration=duration))
            else:
                suitReact.append(ActorInterval(suit, 'flatten'))
            if major and not (drop['level'] >= 4) and not hasSpecialDeath:
                if major > 1:
                    deathdelay = 0.4
        else:
            if duration:
                suitReact.append(ActorInterval(suit, 'drop-react', duration=duration))
            else:
                suitReact.append(ActorInterval(suit, 'drop-react'))
            if major:
                deathdelay = (delay + tObjectAppears - 1.25) + (0.4 * (major - 1))
                
        suitTrack.append(Wait(delay + tObjectAppears))
        suitTrack.append(showDamage)
        suitTrack.append(updateHealthBar)

        if not (drop['level'] < 4):
            majorObject = level >= 4 or major
        # If there is a boat this round and this drop is not the boat, don't do anything special
        if hasUber and level != UBER_GAG_LEVEL_INDEX:
            suitGettingHit = Parallel(suitReact)
        # If the cog died via a small drop, give a headless death anim
        elif not majorObject and died and not suit.headless and not hasSpecialDeath:  # Anvil and below head explode
            suitGettingHitParallelHolder = Parallel()
            battle.sendMovieEvent(BMLE.EVENT_SUIT_PREDIED, suitGettingHitParallelHolder, suit=suit)
            suitGettingHitInternal = Sequence(Parallel(suitReact, MovieUtil.headExplodeTrack(suit, battle)))
            battle.sendMovieEvent(BMLE.EVENT_SUIT_DIED, suitGettingHitInternal, suit=suit)
            suitGettingHitParallelHolder.append(suitGettingHitInternal)
            suitGettingHit = Sequence(suitGettingHitParallelHolder)
            suit.headless = True
        # If the cog died via a big drop, give a special squish anim
        elif majorObject and not suit.crushed and hasDied and last and not hasSpecialDeath:  # Big weight and above floor collapse
            suitScale = suit.getGeomNode().getScale()
            fallSound = globalBattleSoundCache.getSound('cogbldg_land.ogg')
            crushSound = globalBattleSoundCache.getSound('TL_train_cog.ogg')

            # To make it match up a little better, make the squish sound start a little sooner for these gags.
            times = {4: 1.25, 5: 0.7, 6: 0.65, 7: 0.0}
            startTime = times.get(level, 0)

            if suit.specialHead:
                stopHead = Func(suit.specialHead.pose, 'neutral', 0)
            else:
                stopHead = Sequence()

            # Functions for quick death drop extension.
            finalSeq = Sequence(
                Wait(3),  # Delay 3 seconds
                LerpScaleInterval(suit, 0.5, (0.01, 0.01, 0.01), blendType='easeIn'),  # Shrink the silhouette
                Func(suit.hide),  # Hide the silhouette
            )

            initialZ = suit.getZ()

            # Define this here so that we can grab the length.
            suitFlatten = Sequence(Parallel(LerpFunc(suit.setZ, duration=0.125, fromData=initialZ, toData=initialZ - 1),
                                            ActorInterval(suit, 'flatten', startFrame=0, endFrame=4)))
            suitFlattenDuration = suitFlatten.getDuration()

            def waitPlaySquishSound():
                seq = Sequence(Wait(suitFlattenDuration - startTime), Func(base.playSfx, crushSound))
                seq.start()

            def suitSquished():
                suit.setColor(0, 0, 0, 1)
                # Flatten the suit
                suit.pose('flatten', 5)
                # Position the suit slightly above the ground to prevent clipping
                suit.setZ(initialZ + 0.1)
                # Set the scale of the suit to be regular, but flattened
                suit.getGeomNode().setScale(suitScale[0], suitScale[1], 0.025)

            suitGettingHitParallelHolder = Parallel()
            battle.sendMovieEvent(BMLE.EVENT_SUIT_PREDIED, suitGettingHitParallelHolder, suit=suit)
            suitReact = Sequence(Func(waitPlaySquishSound),                     # Set up our squish sound now to time it properly
                                 Func(messenger.send, 'MovieDrop-suitPreFlatten', [suit]),
                                 suitFlatten,                                   # Suit falls through the floor a little bit, play the first few frames of the crush animation
                                 Func(base.playSfx, fallSound, volume=0.65),    # Play fall sfx
                                 Func(suit.clearSplats),                        # Clear suit splats
                                 Func(suitSquished),                            # Squish the suit, and do the fun stuff
                                 stopHead,                                      # Stop the animated head if it exists
                                 finalSeq)                                      # Play the final sequence
            suitGettingHitInternal = Sequence(suitReact)
            battle.sendMovieEvent(BMLE.EVENT_SUIT_DIED, suitGettingHitInternal, suit=suit)
            suitGettingHitParallelHolder.append(suitGettingHitInternal)
            suitGettingHit = Sequence(suitGettingHitParallelHolder)
            suit.crushed = True
        else:
            suitGettingHit = Parallel(suitReact)
        # Special sound for boat drops
        if level == UBER_GAG_LEVEL_INDEX:
            gotHitSound = globalBattleSoundCache.getSound('AA_drop_boat_cog.ogg')
            suitGettingHit.append(SoundInterval(gotHitSound, node=toon))
        suitTrack.append(suitGettingHit)
        # Create a bonus track if there is an hp bonus
        bonusTrack = None
        if hpbonus < 0:
            bonusTrack = Sequence(Wait(delay + tObjectAppears + 0.75), Func(suit.showHpText, hpbonus, 1, openEnded=0), Func(suit.updateHealthBar, hpbonus))
        if revived != 0 and not hasDied:
            if deathdelay > 0:
                suitTrack.append(Sequence(Wait(deathdelay)))
            suitTrack.append(MovieUtil.createSuitReviveTrack(suit, toon, battle))
        elif (hasUber and level != UBER_GAG_LEVEL_INDEX) or (hasDied and diedObjectIsMajor) and not hasSpecialDeath:  # No special track for floor collapse deaths
            pass
        elif died != 0:
            if (level >= 4 and not suit.headless) or hasSpecialDeath:
                if deathdelay > 0:
                    suitTrack.append(Sequence(Wait(deathdelay)))
                suitTrack.append(MovieUtil.createSuitDeathTrack(suit, toon, battle))
            else:
                headlessDeathSound = globalBattleSoundCache.getSound(
                    f'cc_s_sfx_ene_suit_headlessDeath_{getSuitBodyType(suit.dna.name).upper()}.ogg')
                suitTrack.append(
                    Sequence(Parallel(
                        ActorInterval(suit, 'headless-death'),
                        IsolatedSoundInterval(headlessDeathSound, node=suit),
                        Sequence(Wait(2.2), Func(MovieUtil.avatarHide, suit))))
                )
        else:
            suitTrack.append(Func(suit.loop, 'neutral'))
        if bonusTrack is not None:
            suitTrack = Parallel(suitTrack, bonusTrack)
    elif kbbonus == 0:
        # If suit is lured, doesn't need to dodge and certainly won't get hit
        suitTrack = Sequence(Wait(delay + tObjectAppears), Func(MovieUtil.indicateMissed, suit, 0.6))
        if not suit.isLured:
            suitTrack.append(Func(suit.loop, 'neutral'))
    else:
        # Conditions regarding dodging:
        #    1) The suit will dodge only once with multiple drops in the same attack,
        #       so we only dodge if we haven't already (alreadyDodged==0)
        #    2) The suit will not NEED to dodge if attacked by a larger drop (which fall
        #       behind the suit on a miss rather than having the suit dodge
        # Special conditions:
        #    1) If there's a large drop followed by a small one at some point, we can allow
        #       the suit to start teasing and then dogde, this looks fine
        #    2) If there's a small drop followed by a large drop at some point, we don't allow
        #       the suit to tease, doesn't look right
        # Other suits may need to dodge as well

        # But if we've already started to tease, don't tease more than once
        if alreadyTeased > 0 or suit.headless or suit.crushed:
            return

        suitTrack = MovieUtil.createSuitTeaseMultiTrack(suit, delay=delay + tObjectAppears, wantIndicateMiss=True)

        # # First check if suit started dodging, if so, do not add any another reaction
        # if alreadyDodged > 0:
        #     return
            
        # # Check for large drops
        # if level >= 4: # The larger drops, suit doesn't dodge, but teases instead
        #     # But if we've already started to tease, don't tease more than once
        #     if alreadyTeased > 0:
        #         return
        #     else:
        #         suitTrack = MovieUtil.createSuitTeaseMultiTrack(suit, delay=delay + tObjectAppears)
        # else: # Small drop, so dodge
        #     suitTrack = MovieUtil.createSuitDodgeMultitrack(delay + tSuitDodges, suit, leftSuits, rightSuits, battle.activeSuits)
    return suitTrack
