import math
from collections import OrderedDict

from toontown.chat.constants.ChatGlobals import  CFSpeech, CFTimeout
from direct.interval.IntervalGlobal import *

from toontown.battle import MovieUtil
from toontown.battle.BattleBase import *
from toontown.battle.BattleProps import *
from toontown.battle.BattleSounds import *
from toontown.battle.SuitBattleGlobals import ITERATIVE_CHAT
from toontown.battle.movielistener.BattleMovieListenerEnum import BMLE
from toontown.battle.visuals.VisualEffectEnums import VisualEffectEnum
from toontown.effects import DustCloud
from toontown.suit.SuitDNA import *
from toontown.toon.ToonDNA import *

notify = getNotify("MovieFire")

tPieHitsSuit = 3.0


def doFires(fires):
    """Fires occur in the following order:
    a) One per suit only, others will not animate
    b) Comboing a group fire with solo fire will crash (TODO: FIX)
    """
    if len(fires) == 0:
        return (None, None)

    # Group the fires by the targeted suit
    suitFiresDict = OrderedDict()
    i = 0
    try:
        attempt = fires[0]["target"][i]["suit"]
        doAdd = True
    except:
        doAdd = False
    for fire in fires:
        if doAdd:
            suitId = fire["target"][i]["suit"].doId
            i = i + 1
        else:
            suitId = fire["target"]["suit"].doId
        if suitId in suitFiresDict:
            suitFiresDict[suitId].append(fire)
        else:
            suitFiresDict[suitId] = [fire]

    # A list of lists of fires grouped by suit,
    # sorted based on the number of fires per suit
    suitFires = sorted(suitFiresDict.values(), key=len)

    # Apply attacks in order
    delay = 0.0
    mtrack = Parallel()
    for sf in suitFires:
        if len(sf) > 0:
            ival = __doSuitFires(sf)
            if ival:
                mtrack.append(Sequence(Wait(delay), ival))
            delay = random.random() * 0.3

    camDuration = mtrack.getDuration()
    camTrack = fires[0]['battle'].camera.chooseFireShot(fires, suitFiresDict, camDuration)
    return (mtrack, camTrack)


def __doSuitFires(fires):
    """__doSuitFires(fires)
    Create the intervals for the attacks on a particular suit.
    1 or more toons can fire the same target suit
    However, only the first Toon's fire will animate
    """
    toonTracks = Parallel()
    delay = 0.0
    # See if suit is hit multiple times, if it is, don't show stun animation
    hitCount = 0
    i = 0
    try:
        attempt = fires[0]["target"][i]["suit"]
        doAdd = True
    except:
        doAdd = False
    for fire in fires:
        if fire["sidestep"] == 0:
            # Hit, continue counting
            hitCount += 1
            if doAdd:
                i += 1
        else:
            # Miss, no need to think about stun effect
            break

    suitList = []
    i = 0
    for fire in fires:
        if doAdd:
            if fire["target"][i]["suit"] not in suitList:
                suitList.append(fire["target"][i]["suit"])
            i = i + 1
        else:
            if fire["target"]["suit"] not in suitList:
                suitList.append(fire["target"]["suit"])

    i = 0
    for fire in fires:
        showSuitCannon = 1
        if doAdd:
            if fire["target"][i]["suit"] not in suitList:
                showSuitCannon = 0
            else:
                suitList.remove(fire["target"][i]["suit"])
            for x in range(len(fire["target"])):
                tracks = __useFire(fire, i, delay, hitCount, showSuitCannon)
                i = i + 1
                if tracks:
                    for track in tracks:
                        toonTracks.append(track)

                delay = delay + TOON_THROW_DELAY
        else:
            if fire["target"]["suit"] not in suitList:
                showSuitCannon = 0
            else:
                suitList.remove(fire["target"]["suit"])
            tracks = __useFire(fire, i, delay, hitCount, showSuitCannon)
            if tracks:
                for track in tracks:
                    toonTracks.append(track)

            delay = delay + TOON_THROW_DELAY

    return toonTracks


def __getSoundTrack(level, hitSuit, node=None):
    fireSound = globalBattleSoundCache.getSound("AA_drop_trigger_box.ogg")
    fireTrack = Sequence(Wait(2.15), SoundInterval(fireSound, node=node))
    return fireTrack


def __useFire(fire, i, delay, hitCount, showCannon=1):
    toon = fire["avatar"]
    target = fire["target"]
    try:
        target = target[i]
    except:
        pass
    suit = target["suit"]
    hp = target["hp"]
    died = target["died"]
    level = fire["level"]
    battle = fire["battle"]
    suitPos = suit.getPos(battle)
    origHpr = toon.getHpr(battle)
    notify.debug(
        "toon: %s fires suit: %d for hp: %d died: %d"
        % (toon.getName(), suit.doId, hp, died)
    )

    hitSuit = fire["sidestep"] == 0

    button = globalPropPool.getProp("button")
    buttons = [button]
    hands = toon.getLeftHands()

    # Immediately apply unite cooldown visual to toons, don't do it inside of the movie
    # The cooldown applies immediately on the AI so they should visually see it immediately as well
    if died:
        MovieUtil.applyVisualEffect(toon, VisualEffectEnum.UNITE_COOLDOWN)

    toonTrack = Sequence()
    toonFace = Func(toon.headsUp, suit)
    toonTrack.append(Wait(delay))
    toonTrack.append(toonFace)
    toonTrack.append(
        Parallel(ActorInterval(button, "button"), ActorInterval(toon, "pushbutton"))
    )
    doSpecialAnim = suit.getActualLevel() <= 4
    if died and not doSpecialAnim:
        toonTrack.append(ActorInterval(toon, "wave", duration=2.0))
        toonTrack.append(ActorInterval(toon, "duck"))
    toonTrack.append(Func(toon.loop, "neutral"))
    toonTrack.append(Func(toon.setHpr, battle, origHpr))

    buttonTrack = Sequence()

    buttonShow = Func(MovieUtil.showProps, buttons, hands)
    buttonScaleUp = LerpScaleInterval(
        button, 1.0, button.getScale(), startScale=Point3(0.01, 0.01, 0.01)
    )
    buttonScaleDown = LerpScaleInterval(
        button, 1.0, Point3(0.01, 0.01, 0.01), startScale=button.getScale()
    )
    buttonHide = Func(MovieUtil.removeProps, buttons)
    buttonTrack.append(Wait(delay))
    buttonTrack.append(buttonShow)
    buttonTrack.append(buttonScaleUp)
    buttonTrack.append(Wait(2.5))
    buttonTrack.append(buttonScaleDown)
    buttonTrack.append(buttonHide)

    soundTrack = __getSoundTrack(level, hitSuit, toon)

    if died:
        suitResponseHolderParallel = Parallel()
        battle.sendMovieEvent(BMLE.EVENT_SUIT_PREDIED, suitResponseHolderParallel, suit=suit)
    suitResponseTrack = Sequence()
    reactIval = Sequence()
    if showCannon and died:
        if not doSpecialAnim:
            showDamage = Func(suit.showHpText, hp, openEnded=0)
            updateHealthBar = Func(suit.updateHealthBar, hp)
            # If the suit gets knocked back, animate it
            # No stun animation shown here
            cannon = loader.loadModel("phase_4/models/minigames/toon_cannon")
            barrel = cannon.find("**/cannon")
            barrel.setHpr(0, 90, 0)

            cannonHolder = render.attachNewNode("CannonHolder")
            cannon.reparentTo(cannonHolder)
            cannon.setPos(0, 0, -8.6)
            cannonAttachPoint = barrel.attachNewNode("CannonAttach")
            kapowAttachPoint = barrel.attachNewNode("kapowAttach")
            scaleFactor = 1.6
            iScale = 1 / scaleFactor
            barrel.setScale(scaleFactor, 1, scaleFactor)
            cannonAttachPoint.setScale(iScale, 1, iScale)
            cannonAttachPoint.setPos(0, 6.7, 0)
            kapowAttachPoint.setPos(0, -0.5, 1.9)

            def getDustCloudIval(suit):
                dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
                dustCloud.setBillboardAxis(2.0)
                dustCloud.setZ(3)
                dustCloud.setScale(1.0)
                dustCloud.createTrack()
                if not suit:
                    return
                return Sequence(Func(dustCloud.reparentTo, suit), dustCloud.track, Func(dustCloud.destroy),
                                name='dustCloudIval')

            dust = getDustCloudIval(suit)

            def makeSuitUnemployed(suit):
                suit.makeUnemployed()
                suit.fired = True
                nameInfo = suit.createNameInfo(wantDept=False)
                suit.setDisplayName(nameInfo)

            def attachSuitToCannon():
                suit.reparentTo(cannonAttachPoint)
                suit.setPos(0, 0, 0)
                suit.setHpr(0, -90, 0)

            def positionCannonHolder():
                cannonHolder.setPos(suit.getPos(render))
                cannonHolder.setHpr(suit.getHpr(render))

            suitLevel = suit.getActualLevel()
            if suitLevel > 12:
                suitLevel = 12
            deep = 2.5 + suitLevel * 0.2

            suitScale = 0.9 - math.sqrt(suitLevel) * 0.1
            sival = []
            raiseAmount = 7.0
            raisePosCallback = lambda: cannonHolder.getPos() + Point3(0.0, 0.0, raiseAmount)
            lowerPosCallback = lambda: cannonHolder.getPos() - Point3(0.0, 0.0, raiseAmount)

            kapow = globalPropPool.getProp("kapow")
            kapow.reparentTo(kapowAttachPoint)
            kapow.hide()
            kapow.setScale(0.25)
            kapow.setBillboardPointEye()

            smoke = loader.loadModel("phase_4/models/props/test_clouds")
            smoke.reparentTo(cannonAttachPoint)
            smoke.setScale(0.5)
            smoke.hide()
            smoke.setBillboardPointEye()

            soundBomb = base.loader.loadSfx("phase_4/audio/sfx/MG_cannon_fire_alt.ogg")
            playSoundBomb = SoundInterval(soundBomb, node=cannonHolder)

            soundFly = base.loader.loadSfx("phase_4/audio/sfx/firework_whistle_01.ogg")
            playSoundFly = SoundInterval(soundFly, node=cannonHolder)

            soundCannonAdjust = base.loader.loadSfx(
                "phase_4/audio/sfx/MG_cannon_adjust.ogg"
            )
            playSoundCannonAdjust = SoundInterval(
                soundCannonAdjust, duration=0.6, node=cannonHolder
            )

            soundCogPanic = base.loader.loadSfx("phase_5/audio/sfx/ENC_cogafssm.ogg")
            playSoundCogPanic = SoundInterval(soundCogPanic, node=cannonHolder)

            reactIval = Parallel(
                Sequence(
                    Func(positionCannonHolder),
                    Func(attachSuitToCannon),
                    LerpPosInterval(
                        cannonHolder,
                        2.0,
                        raisePosCallback,
                        blendType="easeInOut",
                    ),
                    Parallel(
                        LerpHprInterval(
                            barrel,
                            0.6,
                            Point3(0, 45, 0),
                            startHpr=Point3(0, 90, 0),
                            blendType="easeIn",
                        ),
                        playSoundCannonAdjust,
                    ),
                    Wait(2.0),
                    Parallel(
                        LerpHprInterval(
                            barrel,
                            0.6,
                            Point3(0, 90, 0),
                            startHpr=Point3(0, 45, 0),
                            blendType="easeIn",
                        ),
                        playSoundCannonAdjust,
                    ),
                    LerpPosInterval(
                        cannonHolder,
                        1.0,
                        lowerPosCallback,
                        blendType="easeInOut",
                    ),
                ),
                Sequence(
                    Wait(0.0),
                    Parallel(
                        Sequence(
                            ActorInterval(suit, "flail", duration=1.4, playRate=1.2),
                            ActorInterval(suit, "pie-small-react", startTime=1.3, duration=0.6),
                            Func(suit.pose, 'neutral', 0),
                        ),
                        Func(dust.start),
                        Func(makeSuitUnemployed, suit),
                        suit.scaleInterval(1.0, suitScale),
                        LerpPosInterval(suit, 0.25, Point3(0, -1.0, 0.0)),
                        Sequence(
                            Wait(0.25),
                            Parallel(
                                playSoundCogPanic,
                                LerpPosInterval(
                                    suit, 1.5, Point3(0, -deep, 0.0), blendType="easeIn"
                                ),
                            ),
                        ),
                    ),
                    Wait(2.5),
                    Parallel(
                        playSoundBomb,
                        playSoundFly,
                        Sequence(
                            Func(smoke.show),
                            Parallel(
                                LerpScaleInterval(smoke, 0.5, 3),
                                LerpColorScaleInterval(smoke, 0.5, Vec4(2, 2, 2, 0)),
                            ),
                            Func(smoke.hide),
                        ),
                        Sequence(
                            Func(kapow.show),
                            ActorInterval(kapow, "kapow"),
                            Func(kapow.hide),
                        ),
                        LerpPosInterval(suit, 3.0, Point3(0, 150.0, 0.0)),
                        suit.scaleInterval(3.0, 0.01),
                    ),
                    Func(suit.hide),
                ),
            )

            sival = Sequence(
                Parallel(
                    reactIval, MovieUtil.createSuitStunInterval(suit, 0.3, 1.3)
                ),
                Wait(0.0),
                Func(cannonHolder.removeNode),
            )

            suitResponseTrack.append(Wait(delay + tPieHitsSuit))
            suitResponseTrack.append(showDamage)
            suitResponseTrack.append(updateHealthBar)
            suitResponseTrack.append(sival)
            # Make a bonus track for any hp bonus
            bonusTrack = Sequence(Wait(delay + tPieHitsSuit))
            suitResponseTrack = Parallel(suitResponseTrack, bonusTrack)
        else:
            # It's a low level Cog, they're just gonna quit
            suitResponseTrack = Sequence(
                Wait(delay + tPieHitsSuit),
                Func(
                    suit.setChatAbsolute,
                    TTLocalizer.FireQuitMessage,
                    CFSpeech | CFTimeout,
                ),
                Wait(1.85),
                Parallel(
                    suit.beginSupaFlyMove(Point3(0, 0, 0), 0, "fireFlyOut", False, flyOutBasedOnCurrentPos=True),
                    Sequence(
                        Wait(2.75),
                        ActorInterval(toon, "shrug"),
                        Func(toon.loop, "neutral"),
                    ),
                ),
            )
    else:
        suitResponseTrack = Sequence(
            Wait(delay + tPieHitsSuit + 2),
            Func(MovieUtil.indicateMissed, suit, 1.0),
            Parallel(
                Func(
                    (suit.setChatIterative if suit.style.name in ITERATIVE_CHAT else suit.setChatAbsolute),
                    TTLocalizer.FireFailMessages.get(suit.dna.name, TTLocalizer.FireFailMessage),
                    CFSpeech | CFTimeout,
                ),
                Wait(2),
                MovieUtil.createSuitTeaseMultiTrack(suit, 0),
            ),
        )

    if died:
        suitResponseTrack = Sequence(suitResponseTrack)
        battle.sendMovieEvent(BMLE.EVENT_SUIT_DIED, suitResponseTrack, suit=suit)
        suitResponseTrack = Parallel(suitResponseHolderParallel, suitResponseTrack)

    return [toonTrack, soundTrack, buttonTrack, suitResponseTrack]
