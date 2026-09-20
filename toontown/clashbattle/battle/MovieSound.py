from toontown.audio.IsolatedSoundInterval import IsolatedSoundInterval
from toontown.clashbattle.battle import BattleGlobals
from toontown.clashbattle.battle import BattleParticles
from toontown.clashbattle.battle import MovieUtil
from toontown.clashbattle.battle.BattleBase import *
from toontown.clashbattle.battle.BattleProps import *
from toontown.clashbattle.battle.BattleSounds import *
from toontown.clashbattle.battle.RewardPanel import *
from toontown.clashbattle.battle.movielistener.BattleMovieListenerEnum import BMLE
from toontown.clashbattle.battle.statuses.StatusEffectEnums import SEE
from toontown.clashbattle.battle.visuals.VisualEffectEnums import VisualEffectEnum
from toontown.clashbattle.battle import SuitBattleGlobals
from toontown.clashsuit.suit.SuitDNA import getSuitBodyType
from toontown.utils.DirectNotifyCategory import getNotify
import random

notify = getNotify('MovieSound')
soundFiles = ('AA_sound_kazoo.ogg', 'AA_sound_bikehorn.ogg', 'AA_sound_whistle.ogg', 'AA_sound_bugle.ogg', 'AA_sound_aoogah.ogg', 'AA_sound_elephant.ogg', 'SZ_DD_foghorn.ogg', 'AA_sound_Opera_Singer.ogg')
appearSoundFiles = ('toonbldg_settle.ogg', 'MG_tag_1.ogg', 'LB_receive_evidence.ogg', 'm_match_trumpet.ogg', 'TL_step_on_rake.ogg', 'toonbldg_grow.ogg', 'mailbox_full_wobble.ogg', 'mailbox_full_wobble.ogg')
hitSoundFiles = ('AA_sound_Opera_Singer_Cog_Glass.ogg',)
tSound = 2.45
tSuitReact = 2.6
DISTANCE_TO_WALK_BACK = MovieUtil.SUIT_LURE_DISTANCE * 0.75
TIME_TO_WALK_BACK = 0.5
if DISTANCE_TO_WALK_BACK == 0:
    TIME_TO_WALK_BACK = 0
INSTRUMENT_SCALE_MODIFIER = 0.5
BEFORE_STARS = 0.5
AFTER_STARS = 1.75


def doSounds(sounds):
    if len(sounds) == 0:
        return (None, None)
    mtrack = Parallel(__doSoundsLevel(sounds, 0.0, 1))
    targets = sounds[0]['target']
    camDuration = mtrack.getDuration()
    camTrack = sounds[0]['battle'].camera.chooseSoundShot(sounds, targets, camDuration)
    return (mtrack, camTrack)


def __getSuitTrack(sound, lastSoundsThatHit, delay, hitCount, targets, totalDamage, toon, operacheck, numOfSounds):
    tracks = Parallel()
    uberDelay = 0.0
    isUber = 0
    if operacheck:
        uberDelay = 3.0
        isUber = 1
    for target in targets:
        suit = target['suit']
        suitId = suit.doId
        lastSoundThatHit = lastSoundsThatHit.get(suit)
        damage = totalDamage[suitId]
        if sound['sidestep'] == 0 and (lastSoundThatHit and sound == lastSoundThatHit[0]):
            died = target['died']
            battle = sound['battle']
            hpbonus = target['hpbonus']
            kbbonus = target['kbbonus']
            suitTrack = Sequence()
            showDamage = Func(suit.showHpText, damage, openEnded=0)
            updateHealthBar = Func(suit.updateHealthBar, damage)
            suitTrack.append(Wait(delay + tSuitReact + lerp(-0.07, 0.07, random.random())))
            if isUber:
                breakEffect = BattleParticles.createParticleEffect(file='soundBreak')
                breakEffect.setDepthWrite(0)
                breakEffect.setDepthTest(0)
                breakEffect.setTwoSided(1)
                soundEffect = globalBattleSoundCache.getSound(hitSoundFiles[0])
                suitTrack.append(Wait(0.65 + (random.random()*0.4)))
                suitTrack.append(Func(setPosFromOther, breakEffect, suit, Point3(0, 0.0, suit.getHeight() - 1.0)))
                suitTrack.append(Parallel(
                    showDamage,
                    updateHealthBar,
                    IsolatedSoundInterval(soundEffect, node=suit),
                    __getPartTrack(breakEffect, 0.0, 1.0, [breakEffect, suit, 0], softStop=-0.5)
                ))
                if died and not MovieUtil.shouldOverrideSuitDeath(suit):
                    suitTrack.append(MovieUtil.headExplodeTrack(suit, battle))
            else:
                suitTrack.append(showDamage)
                suitTrack.append(updateHealthBar)

            soundReactAnim = 'sound-react'
            if suit.dna.name in SuitBattleGlobals.NO_TIE_SUITS:
                soundReactAnim = 'sound-react-nt'
            elif suit.dna.name in SuitBattleGlobals.BOWTIE_SUITS or suit.isWaiter:
                soundReactAnim = 'sound-react-bow'

            if hitCount == 1:
                suitTrack.append(Parallel(ActorInterval(suit, soundReactAnim), MovieUtil.createSuitStunInterval(suit, 0.5, 1.8)))
            else:
                suitTrack.append(ActorInterval(suit, soundReactAnim))
            if kbbonus == 1:
                suitTrack.append(__createSuitResetPosTrack(suit, battle))
                suitTrack.append(MovieUtil.unlureSuit(suit, battle))
                suitTrack.append(Func(suit.loop, 'neutral'))
                if suit.specialHead:
                    suitTrack.append(Func(suit.specialHead.loopNeutral))
                if suit.stunStars:
                    suitTrack.append(Func(suit.cleanupStunStars))
            bonusTrack = None
            if hpbonus > 0:
                bonusTrack = Sequence(Wait(delay + tSuitReact + delay + 0.75 + uberDelay), Func(suit.showHpText, -hpbonus, 1, openEnded=0), Func(suit.updateHealthBar, hpbonus))
            suitTrack.append(Func(suit.loop, 'neutral'))
            if bonusTrack is None:
                tracks.append(suitTrack)
            else:
                tracks.append(Parallel(suitTrack, bonusTrack))
        elif sound['sidestep'] == 1:
            battle = sound['battle']
            tracks.append(Sequence(Wait(2.9), Func(MovieUtil.indicateMissed, suit, 1.0)))
            tracks.append(MovieUtil.createSuitTeaseMultiTrack(suit, delay + tSuitReact))
            if suit.specialHead:
                 tracks.append(Func(suit.specialHead.loopNeutral))
            if suit.stunStars:
                tracks.append(Func(suit.cleanupStunStars))
            if suit.isLured:
                tracks.append(Sequence(__createSuitResetPosTrack(suit, battle)))
                tracks.append(MovieUtil.unlureSuit(suit, battle))
            tracks.append(Func(suit.loop, 'neutral'))

    return tracks


def __doSoundsLevel(sounds, delay, hitCount):
    lastSoundsThatHit = {}
    battle = sounds[0]['battle']
    totalDamage = {suitId: 0 for suitId in [suit.doId for suit in battle.activeSuits]}
    operacheck = 0
    suitsDied = {}
    for sound in sounds:
        if sound['level'] >= BattleGlobals.LAST_REGULAR_GAG_LEVEL:
            operacheck += 1
        for target in sound['target']:
            if sound['sidestep'] == 0:
                suit = target['suit']
                suitId = suit.doId
                currentDamage = totalDamage.get(suitId, 0)
                totalDamage[suitId] = currentDamage + target['hp']

                died = target['died']
                if died and suitId not in suitsDied:
                    suitsDied[suitId] = 1
                prevSound = lastSoundsThatHit.get(suit)
                if not prevSound or (prevSound and not prevSound[1]):
                    lastSoundsThatHit[suit] = (sound, died)

    mainTrack = Sequence()
    tracks = Parallel()
    deathTracks = Parallel()

    encoreApplicationSeqs = {}

    for i, sound in enumerate(sounds):
        toon = sound["avatar"]
        level = sound['level']
        targets = sound['target']
        attackMTrack = soundfn_array[sound['level']](sound, delay, toon, targets, level)
        tracks.append(Sequence(Wait(delay), attackMTrack))
        tracks.append(__getSuitTrack(sound, lastSoundsThatHit, delay, hitCount, targets, totalDamage, toon, operacheck, len(sounds)))
        # If prestige, show 'encore' text when hitting the cog if they don't already have the effect
        if sound['sidestep'] == 0:
            if not toon.getStatusEffectOfId(SEE.EFFECT_WINDED):
                encoreEffect = toon.getStatusEffectOfId(SEE.EFFECT_ENCORE)
                if not encoreEffect:
                    def applyEncore(toon=toon):
                        prestige = int(toon.getTrackBonusLevel(AttackEnum.TOON_SOUND) >= 1)
                        returnVal = MovieUtil.applyVisualEffect(toon, VisualEffectEnum.ENCORE, extraArgs=[SoundAtkBonus[prestige]], useMovieApply=True)
                        if returnVal is None:
                            return
                        applySeq, _ = returnVal
                        encoreApplicationSeqs[toon.doId] = applySeq
                        applySeq.start()

                    def cleanupEncore(toon=toon):
                        if toon.doId in encoreApplicationSeqs:
                            encoreApplicationSeqs[toon.doId].finish()
                            del encoreApplicationSeqs[toon.doId]

                    tracks.append(Sequence(
                        Wait(delay + tSuitReact),
                        Func(toon.showHpString, text='Encore!', color=(0.85, 0.78, 1.0, 1.0)),
                        Wait(0.75),
                        Func(applyEncore),
                        Wait(0.5),
                        Func(cleanupEncore),
                    ))
                else:
                    if not encoreEffect.isDisabled():
                        tracks.append(Sequence(
                            Wait(delay + tSuitReact),
                            Func(toon.showHpString, text='Winded!', color=(0.85, 0.78, 1.0, 1.0)),
                            Wait(0.75),
                            Func(MovieUtil.applyVisualEffect, toon, VisualEffectEnum.WINDED),
                            Func(MovieUtil.unapplyVisualEffect, toon, VisualEffectEnum.ENCORE),
                            Wait(0.5),
                        ))

        for target in targets:
            battle = sound['battle']
            suit = target['suit']
            suitID = suit.doId
            revived = target['revived']
            # If they revived but are dead by the end of the turn, don't show the revive movie.
            # This way, it doesn't mess with any custom death movies that may accidentally play
            # at the same time as the revive movie.
            if revived and suitID not in suitsDied:
                deathTracks.append(MovieUtil.createSuitReviveTrack(suit, toon, battle))
            # Check if this suit has died and hasn't already been shown as dead.
            # We don't want this animation playing twice.
            # Also check that they don't have a special death animation.
            elif i == len(sounds) - 1 and suitID in suitsDied and suitsDied[suitID] == 1:
                suitsDied[suitID] = 2
                if operacheck and not MovieUtil.shouldOverrideSuitDeath(suit):
                    headlessDeathSound = globalBattleSoundCache.getSound(
                        f'cc_s_sfx_ene_suit_headlessDeath_{getSuitBodyType(suit.dna.name).upper()}.ogg')
                    quickDeathParallelHolder = Parallel()
                    battle.sendMovieEvent(BMLE.EVENT_SUIT_PREDIED, quickDeathParallelHolder, suit=suit)
                    quickDeathTrack = Sequence(
                        Parallel(
                            ActorInterval(suit, 'headless-death'),
                            IsolatedSoundInterval(headlessDeathSound, node=suit)
                        ),
                        Func(MovieUtil.avatarHide, suit)
                    )
                    battle.sendMovieEvent(BMLE.EVENT_SUIT_DIED, quickDeathTrack, suit=suit)
                    quickDeathParallelHolder.append(quickDeathTrack)
                    deathTracks.append(quickDeathParallelHolder)
                else:
                    deathTracks.append(MovieUtil.createSuitDeathTrack(suit, toon, battle))
    mainTrack.append(tracks)
    mainTrack.append(deathTracks)
    return mainTrack


def __createSuitResetPosTrack(suit, battle):
    resetPos, resetHpr = battle.getActorPosHpr(suit)
    moveDuration = 0.5
    walkTrack = Sequence(Func(suit.setHpr, battle, resetHpr), ActorInterval(suit, 'walk', startTime=1, duration=moveDuration, endTime=0.0001), Func(suit.loop, 'neutral'))
    moveTrack = LerpPosInterval(suit, moveDuration, resetPos, other=battle)
    return Parallel(walkTrack, moveTrack)


def createSuitResetPosTrack(suit, battle):
    return __createSuitResetPosTrack(suit, battle)


def __createToonInterval(sound, delay, toon, operaInstrument = None):
    battle = sound['battle']
    hasLuredSuits = __hasLuredSuits(sound)
    oldPos, oldHpr = battle.getActorPosHpr(toon)
    newPos = Point3(oldPos)
    newPos.setY(newPos.getY() - DISTANCE_TO_WALK_BACK)
    retval = Sequence(Wait(delay))
    if DISTANCE_TO_WALK_BACK and hasLuredSuits:
        retval.append(Parallel(ActorInterval(toon, 'walk', startTime=1, duration=TIME_TO_WALK_BACK, endTime=0.0001), LerpPosInterval(toon, TIME_TO_WALK_BACK, newPos, other=battle)))
    if operaInstrument:
        sprayEffect = BattleParticles.createParticleEffect(file='soundWave')
        sprayEffect.setDepthWrite(0)
        sprayEffect.setDepthTest(0)
        sprayEffect.setTwoSided(1)
        I1 = 2.8
        retval.append(Parallel(
            Sequence(
                ActorInterval(toon, 'sound', playRate=1.0, startTime=0.0, endTime=I1),
                Func(setPosFromOther, sprayEffect, operaInstrument, Point3(0, 1.6, -0.18)),
                __getPartTrack(sprayEffect, 0.0, 5.0, [sprayEffect, toon, 0], softStop=-2.5),
            ),
            Sequence(
                Wait(5.5),
                ActorInterval(toon, 'sound', playRate=1.0, startTime=I1)
            ),
            Sequence(
                Wait(7.3),
                LerpFunctionInterval(sprayEffect.setAlphaScale, fromData=1, toData=0, duration=0.5, blendType='easeIn'),
            ),
        ))
    else:
        retval.append(ActorInterval(toon, 'sound'))
    if DISTANCE_TO_WALK_BACK and hasLuredSuits:
        retval.append(Parallel(ActorInterval(toon, 'walk', startTime=0.0001, duration=TIME_TO_WALK_BACK, endTime=1), LerpPosInterval(toon, TIME_TO_WALK_BACK, oldPos, other=battle)))
    retval.append(Func(toon.loop, 'neutral'))
    return retval


def __hasLuredSuits(sound):
    targets = sound['target']
    for target in targets:
        kbbonus = target['kbbonus']
        if kbbonus == 1:
            return True

    return False


def __doBikehorn(sound, delay, toon, targets, level):
    tracks = Parallel()
    instrMin = Vec3(0.001, 0.001, 0.001)
    instrMax = Vec3(0.65, 0.65, 0.65)
    instrMax *= INSTRUMENT_SCALE_MODIFIER
    instrStretch = Vec3(0.6, 1.1, 0.6)
    instrStretch *= INSTRUMENT_SCALE_MODIFIER
    megaphone = globalPropPool.getProp('blue-megaphone')
    megaphones = [megaphone]
    instrument = globalPropPool.getProp('bikehorn')
    instruments = [instrument]

    def setInstrumentStats(instrument = instrument):
        instrument.setPos(-1.1, -1.4, 0.1)
        instrument.setHpr(145, 0, 0)
        instrument.setScale(instrMin)

    hands = toon.getRightHands()
    megaphoneShow = Sequence(
        Func(MovieUtil.showProps, megaphones, hands), 
        Func(MovieUtil.showProps, instruments, hands), 
        Func(setInstrumentStats)
    )
    megaphoneHide = Sequence(
        Parallel(
            LerpScaleInterval(megaphone, 0.3, instrMin, blendType="easeInOut"),
        ),
        Func(MovieUtil.removeProps, megaphones), 
        Func(MovieUtil.removeProps, instruments),
    )
    instrumentAppearSfx = globalBattleSoundCache.getSound(appearSoundFiles[level])
    grow = getScaleIntervals(instruments, duration=0.2, startScale=instrMin, endScale=instrMax)
    instrumentAppear = Parallel(grow, Sequence(Wait(0.15), IsolatedSoundInterval(instrumentAppearSfx, node=toon)))
    stretchInstr = getScaleBlendIntervals(instruments, duration=0.2, startScale=instrMax, endScale=instrStretch, blendType='easeOut')
    backInstr = getScaleBlendIntervals(instruments, duration=0.2, startScale=instrStretch, endScale=instrMax, blendType='easeIn')
    stretchMega = getScaleBlendIntervals(megaphones, duration=0.2, startScale=megaphone.getScale(), endScale=0.9, blendType='easeOut')
    backMega = getScaleBlendIntervals(megaphones, duration=0.2, startScale=0.9, endScale=megaphone.getScale(), blendType='easeIn')
    attackTrack = Parallel(Sequence(stretchInstr, backInstr), Sequence(stretchMega, backMega))
    hasLuredSuits = __hasLuredSuits(sound)
    delayTime = delay
    if hasLuredSuits:
        delayTime += TIME_TO_WALK_BACK
    megaphoneTrack = Sequence(Wait(delayTime), megaphoneShow, Wait(1.0), instrumentAppear, Wait(3.0), megaphoneHide)
    tracks.append(megaphoneTrack)
    toonTrack = __createToonInterval(sound, delay, toon)
    tracks.append(toonTrack)
    soundEffect = globalBattleSoundCache.getSound(soundFiles[level])
    instrumentshrink = getScaleIntervals(instruments, duration=0.1, startScale=instrMax, endScale=instrMin)
    if soundEffect:
        delayTime = delay + tSound
        if hasLuredSuits:
            delayTime += TIME_TO_WALK_BACK
        soundTrack = Sequence(Wait(delayTime), Parallel(attackTrack, IsolatedSoundInterval(soundEffect, node=toon)), Wait(0.2), instrumentshrink)
        tracks.append(soundTrack)
    return tracks


def __doWhistle(sound, delay, toon, targets, level):
    tracks = Parallel()
    instrMin = Vec3(0.001, 0.001, 0.001)
    instrMax = Vec3(0.2, 0.2, 0.2)
    instrMax *= INSTRUMENT_SCALE_MODIFIER
    instrStretch = Vec3(0.25, 0.25, 0.25)
    instrStretch *= INSTRUMENT_SCALE_MODIFIER
    megaphone = globalPropPool.getProp('blue-megaphone')
    megaphones = [megaphone]
    instrument = globalPropPool.getProp('whistle')
    instruments = [instrument]

    def setInstrumentStats(instrument = instrument):
        instrument.setPos(-1.2, -1.3, 0.1)
        instrument.setHpr(145, 0, 85)
        instrument.setScale(instrMin)

    hands = toon.getRightHands()
    megaphoneShow = Sequence(
        Func(MovieUtil.showProps, megaphones, hands), 
        Func(MovieUtil.showProps, instruments, hands), 
        Func(setInstrumentStats)
    )
    megaphoneHide = Sequence(
        Parallel(
            LerpScaleInterval(megaphone, 0.3, instrMin, blendType="easeInOut"),
        ),
        Func(MovieUtil.removeProps, megaphones), 
        Func(MovieUtil.removeProps, instruments),
    )
    instrumentAppearSfx = globalBattleSoundCache.getSound(appearSoundFiles[level])
    grow = getScaleIntervals(instruments, duration=0.2, startScale=instrMin, endScale=instrMax)
    instrumentAppear = Parallel(grow, Sequence(Wait(0.05), IsolatedSoundInterval(instrumentAppearSfx, node=toon)))
    stretchInstr = getScaleBlendIntervals(instruments, duration=0.2, startScale=instrMax, endScale=instrStretch, blendType='easeOut')
    backInstr = getScaleBlendIntervals(instruments, duration=0.2, startScale=instrStretch, endScale=instrMax, blendType='easeIn')
    attackTrack = Sequence(stretchInstr, backInstr)
    hasLuredSuits = __hasLuredSuits(sound)
    delayTime = delay
    if hasLuredSuits:
        delayTime += TIME_TO_WALK_BACK
    megaphoneTrack = Sequence(Wait(delayTime), megaphoneShow, Wait(1.0), instrumentAppear, Wait(3.0), megaphoneHide)
    tracks.append(megaphoneTrack)
    toonTrack = __createToonInterval(sound, delay, toon)
    tracks.append(toonTrack)
    soundEffect = globalBattleSoundCache.getSound(soundFiles[level])
    instrumentshrink = getScaleIntervals(instruments, duration=0.1, startScale=instrMax, endScale=instrMin)
    if soundEffect:
        delayTime = delay + tSound
        if hasLuredSuits:
            delayTime += TIME_TO_WALK_BACK
        soundTrack = Sequence(Wait(delayTime), Parallel(attackTrack, IsolatedSoundInterval(soundEffect, node=toon)), Wait(0.2), instrumentshrink)
        tracks.append(soundTrack)
    return tracks


def __doKazoo(sound, delay, toon, targets, level):
    tracks = Parallel()
    instrMin = Vec3(0.001, 0.001, 0.001)
    instrMax = Vec3(0.2, 0.2, 0.2)
    instrMax *= INSTRUMENT_SCALE_MODIFIER
    instrStretch = Vec3(0.25, 0.25, 0.25)
    instrStretch *= INSTRUMENT_SCALE_MODIFIER
    megaphone = globalPropPool.getProp('blue-megaphone')
    megaphones = [megaphone,]
    instrument = globalPropPool.getProp('kazoo')
    instruments = [instrument]

    def setInstrumentStats(instrument = instrument):
        instrument.setPos(-1.2, -1.3, 0.1)
        instrument.setHpr(145, 0, 85)
        instrument.setScale(instrMin)

    hands = toon.getRightHands()
    megaphoneShow = Sequence(
        Func(MovieUtil.showProps, megaphones, hands), 
        Func(MovieUtil.showProps, instruments, hands), 
        Func(setInstrumentStats)
    )
    megaphoneHide = Sequence(
        Parallel(
            LerpScaleInterval(megaphone, 0.3, instrMin, blendType="easeInOut"),
        ),
        Func(MovieUtil.removeProps, megaphones), 
        Func(MovieUtil.removeProps, instruments),
    )
    instrumentAppearSfx = globalBattleSoundCache.getSound(appearSoundFiles[level])
    grow = getScaleIntervals(instruments, duration=0.2, startScale=instrMin, endScale=instrMax)
    instrumentAppear = Parallel(grow, Sequence(Wait(0.05), IsolatedSoundInterval(instrumentAppearSfx, node=toon)))
    stretchInstr = getScaleBlendIntervals(instruments, duration=0.2, startScale=instrMax, endScale=instrStretch, blendType='easeOut')
    backInstr = getScaleBlendIntervals(instruments, duration=0.2, startScale=instrStretch, endScale=instrMax, blendType='easeIn')
    attackTrack = Sequence(stretchInstr, backInstr)
    hasLuredSuits = __hasLuredSuits(sound)
    delayTime = delay
    if hasLuredSuits:
        delayTime += TIME_TO_WALK_BACK
    megaphoneTrack = Sequence(Wait(delayTime), megaphoneShow, Wait(1.0), instrumentAppear, Wait(3.0), megaphoneHide)
    tracks.append(megaphoneTrack)
    toonTrack = __createToonInterval(sound, delay, toon)
    tracks.append(toonTrack)
    soundEffect = globalBattleSoundCache.getSound(soundFiles[level])
    instrumentshrink = getScaleIntervals(instruments, duration=0.1, startScale=instrMax, endScale=instrMin)
    if soundEffect:
        delayTime = delay + tSound
        if hasLuredSuits:
            delayTime += TIME_TO_WALK_BACK
        soundTrack = Sequence(Wait(delayTime), Parallel(attackTrack, IsolatedSoundInterval(soundEffect, node=toon)), Wait(0.2), instrumentshrink)
        tracks.append(soundTrack)
    return tracks


def __doBugle(sound, delay, toon, targets, level):
    tracks = Parallel()
    instrMin = Vec3(0.001, 0.001, 0.001)
    instrMax = Vec3(0.4, 0.4, 0.4)
    instrMax *= INSTRUMENT_SCALE_MODIFIER
    instrStretch = Vec3(0.5, 0.5, 0.5)
    instrStretch *= INSTRUMENT_SCALE_MODIFIER
    megaphone = globalPropPool.getProp('blue-megaphone')
    megaphones = [megaphone]
    instrument = globalPropPool.getProp('bugle')
    instruments = [instrument]

    def setInstrumentStats(instrument = instrument):
        instrument.setPos(-1.3, -1.4, 0.1)
        instrument.setHpr(145, 0, 85)
        instrument.setScale(instrMin)

    def longshake(models, num):
        inShake = getScaleBlendIntervals(models, duration=0.2, startScale=instrMax, endScale=instrStretch, blendType='easeInOut')
        outShake = getScaleBlendIntervals(models, duration=0.2, startScale=instrStretch, endScale=instrMax, blendType='easeInOut')
        i = 1
        seq = Sequence()
        while i < num:
            if i % 2 == 0:
                seq.append(inShake)
            else:
                seq.append(outShake)
            i += 1

        seq.start()

    hands = toon.getRightHands()
    megaphoneShow = Sequence(
        Func(MovieUtil.showProps, megaphones, hands), 
        Func(MovieUtil.showProps, instruments, hands), 
        Func(setInstrumentStats)
    )
    megaphoneHide = Sequence(
        Parallel(
            LerpScaleInterval(megaphone, 0.3, instrMin, blendType="easeInOut"),
        ),
        Func(MovieUtil.removeProps, megaphones), 
        Func(MovieUtil.removeProps, instruments),
    )
    instrumentAppearSfx = globalBattleSoundCache.getSound(appearSoundFiles[level])
    grow = getScaleBlendIntervals(instruments, duration=1, startScale=instrMin, endScale=instrMax, blendType='easeInOut')
    instrumentshrink = getScaleIntervals(instruments, duration=0.1, startScale=instrMax, endScale=instrMin)
    instrumentAppear = Sequence(grow, Wait(0), Func(longshake, instruments, 5))
    hasLuredSuits = __hasLuredSuits(sound)
    delayTime = delay
    if hasLuredSuits:
        delayTime += TIME_TO_WALK_BACK
    soundEffect = globalBattleSoundCache.getSound(soundFiles[level])
    megaphoneTrack = Parallel(Sequence(Wait(delay + 1.7), IsolatedSoundInterval(soundEffect, node=toon)), Sequence(Wait(delayTime), megaphoneShow, Wait(1.7), instrumentAppear, Wait(1), instrumentshrink, Wait(1.5), megaphoneHide))
    tracks.append(megaphoneTrack)
    toonTrack = __createToonInterval(sound, delay, toon)
    tracks.append(toonTrack)
    if soundEffect:
        delayTime = delay + tSound
        if hasLuredSuits:
            delayTime += TIME_TO_WALK_BACK
        soundTrack = Wait(delayTime)
        tracks.append(soundTrack)
    return tracks


def __doAoogah(sound, delay, toon, targets, level):
    tracks = Parallel()
    instrMin = Vec3(0.001, 0.001, 0.001)
    instrMax = Vec3(0.5, 0.5, 0.5)
    instrMax *= INSTRUMENT_SCALE_MODIFIER
    instrStretch = Vec3(1.1, 0.9, 0.4)
    instrStretch *= INSTRUMENT_SCALE_MODIFIER
    megaphone = globalPropPool.getProp('blue-megaphone')
    megaphones = [megaphone]
    instrument = globalPropPool.getProp('aoogah')
    instruments = [instrument]

    def setInstrumentStats(instrument = instrument):
        instrument.setPos(-1.0, -1.5, 0.2)
        instrument.setHpr(145, 0, 85)
        instrument.setScale(instrMin)

    hands = toon.getRightHands()
    megaphoneShow = Sequence(
        Func(MovieUtil.showProps, megaphones, hands), 
        Func(MovieUtil.showProps, instruments, hands), 
        Func(setInstrumentStats)
    )
    megaphoneHide = Sequence(
        Parallel(
            LerpScaleInterval(megaphone, 0.3, instrMin, blendType="easeInOut"),
        ),
        Func(MovieUtil.removeProps, megaphones), 
        Func(MovieUtil.removeProps, instruments),
    )
    instrumentAppearSfx = globalBattleSoundCache.getSound(appearSoundFiles[level])
    grow = getScaleIntervals(instruments, duration=0.2, startScale=instrMin, endScale=instrMax)
    instrumentAppear = Parallel(grow, Sequence(Wait(0.05), IsolatedSoundInterval(instrumentAppearSfx, node=toon)))
    stretchInstr = getScaleBlendIntervals(instruments, duration=0.2, startScale=instrMax, endScale=instrStretch, blendType='easeOut')
    backInstr = getScaleBlendIntervals(instruments, duration=0.2, startScale=instrStretch, endScale=instrMax, blendType='easeInOut')
    attackTrack = Sequence(stretchInstr, Wait(1), backInstr)
    hasLuredSuits = __hasLuredSuits(sound)
    delayTime = delay
    if hasLuredSuits:
        delayTime += TIME_TO_WALK_BACK
    megaphoneTrack = Sequence(Wait(delayTime), megaphoneShow, Wait(1.0), instrumentAppear, Wait(3.0), megaphoneHide)
    tracks.append(megaphoneTrack)
    toonTrack = __createToonInterval(sound, delay, toon)
    tracks.append(toonTrack)
    soundEffect = globalBattleSoundCache.getSound(soundFiles[level])
    instrumentshrink = getScaleIntervals(instruments, duration=0.1, startScale=instrMax, endScale=instrMin)
    if soundEffect:
        delayTime = delay + tSound
        if hasLuredSuits:
            delayTime += TIME_TO_WALK_BACK
        soundTrack = Sequence(Wait(delayTime), Parallel(attackTrack, IsolatedSoundInterval(soundEffect, node=toon), Sequence(Wait(1.5), instrumentshrink)))
        tracks.append(soundTrack)
    return tracks


def __doElephant(sound, delay, toon, targets, level):
    tracks = Parallel()
    instrMin = Vec3(0.001, 0.001, 0.001)
    instrMax1 = Vec3(0.3, 0.4, 0.2)
    instrMax1 *= INSTRUMENT_SCALE_MODIFIER
    instrMax2 = Vec3(0.3, 0.3, 0.3)
    instrMax2 *= INSTRUMENT_SCALE_MODIFIER
    instrStretch1 = Vec3(0.3, 0.5, 0.25)
    instrStretch1 *= INSTRUMENT_SCALE_MODIFIER
    instrStretch2 = Vec3(0.3, 0.7, 0.3)
    instrStretch2 *= INSTRUMENT_SCALE_MODIFIER
    megaphone = globalPropPool.getProp('blue-megaphone')
    megaphones = [megaphone]
    instrument = globalPropPool.getProp('elephant')
    instruments = [instrument]

    def setInstrumentStats(instrument = instrument):
        instrument.setPos(-.6, -.9, 0.15)
        instrument.setHpr(145, 0, 85)
        instrument.setScale(instrMin)

    hands = toon.getRightHands()
    megaphoneShow = Sequence(
        Func(MovieUtil.showProps, megaphones, hands), 
        Func(MovieUtil.showProps, instruments, hands), 
        Func(setInstrumentStats)
    )
    megaphoneHide = Sequence(
        Parallel(
            LerpScaleInterval(megaphone, 0.3, instrMin, blendType="easeInOut"),
        ),
        Func(MovieUtil.removeProps, megaphones), 
        Func(MovieUtil.removeProps, instruments),
    )
    instrumentAppearSfx = globalBattleSoundCache.getSound(appearSoundFiles[level])
    grow1 = getScaleIntervals(instruments, duration=0.3, startScale=instrMin, endScale=instrMax1)
    grow2 = getScaleIntervals(instruments, duration=0.3, startScale=instrMax1, endScale=instrMax2)
    instrumentAppear = Parallel(Sequence(grow1, grow2), Sequence(Wait(0.05), IsolatedSoundInterval(instrumentAppearSfx, node=toon)))
    stretchInstr1 = getScaleBlendIntervals(instruments, duration=0.1, startScale=instrMax2, endScale=instrStretch1, blendType='easeOut')
    stretchInstr2 = getScaleBlendIntervals(instruments, duration=0.1, startScale=instrStretch1, endScale=instrStretch2, blendType='easeOut')
    stretchInstr = Sequence(stretchInstr1, stretchInstr2)
    backInstr = getScaleBlendIntervals(instruments, duration=0.1, startScale=instrStretch2, endScale=instrMax2, blendType='easeOut')
    attackTrack = Sequence(stretchInstr, Wait(1), backInstr)
    hasLuredSuits = __hasLuredSuits(sound)
    delayTime = delay
    if hasLuredSuits:
        delayTime += TIME_TO_WALK_BACK
    megaphoneTrack = Sequence(Wait(delayTime), megaphoneShow, Wait(1.0), instrumentAppear, Wait(3.0), megaphoneHide)
    tracks.append(megaphoneTrack)
    toonTrack = __createToonInterval(sound, delay, toon)
    tracks.append(toonTrack)
    soundEffect = globalBattleSoundCache.getSound(soundFiles[level])
    instrumentshrink = getScaleIntervals(instruments, duration=0.1, startScale=instrMax2, endScale=instrMin)
    if soundEffect:
        delayTime = delay + tSound
        if hasLuredSuits:
            delayTime += TIME_TO_WALK_BACK
        soundTrack = Sequence(Wait(delayTime), Parallel(attackTrack, IsolatedSoundInterval(soundEffect, node=toon), Sequence(Wait(1.5), instrumentshrink)))
        tracks.append(soundTrack)
    return tracks


def __doFoghorn(sound, delay, toon, targets, level):
    tracks = Parallel()
    instrMin = Vec3(0.001, 0.001, 0.001)
    instrMax1 = Vec3(0.1, 0.1, 0.1)
    instrMax1 *= INSTRUMENT_SCALE_MODIFIER
    instrMax2 = Vec3(0.3, 0.3, 0.3)
    instrMax2 *= INSTRUMENT_SCALE_MODIFIER
    instrStretch = Vec3(0.4, 0.4, 0.4)
    instrStretch *= INSTRUMENT_SCALE_MODIFIER
    megaphone = globalPropPool.getProp('blue-megaphone')
    megaphones = [megaphone]
    instrument = globalPropPool.getProp('fog_horn')
    instruments = [instrument]

    def setInstrumentStats(instrument = instrument):
        instrument.setPos(-.8, -.9, 0.2)
        instrument.setHpr(145, 0, 0)
        instrument.setScale(instrMin)

    hands = toon.getRightHands()
    megaphoneShow = Sequence(
        Func(MovieUtil.showProps, megaphones, hands), 
        Func(MovieUtil.showProps, instruments, hands), 
        Func(setInstrumentStats)
    )
    megaphoneHide = Sequence(
        Parallel(
            LerpScaleInterval(megaphone, 0.3, instrMin, blendType="easeInOut"),
        ),
        Func(MovieUtil.removeProps, megaphones), 
        Func(MovieUtil.removeProps, instruments),
    )
    instrumentAppearSfx = globalBattleSoundCache.getSound(appearSoundFiles[level])
    grow1 = getScaleIntervals(instruments, duration=1, startScale=instrMin, endScale=instrMax1)
    grow2 = getScaleIntervals(instruments, duration=0.1, startScale=instrMax1, endScale=instrMax2)
    instrumentAppear = Parallel(Sequence(grow1, grow2), Sequence(Wait(0.05), IsolatedSoundInterval(instrumentAppearSfx, node=toon)))
    stretchInstr = getScaleBlendIntervals(instruments, duration=0.3, startScale=instrMax2, endScale=instrStretch, blendType='easeOut')
    backInstr = getScaleBlendIntervals(instruments, duration=1.0, startScale=instrStretch, endScale=instrMin, blendType='easeIn')
    spinInstr1 = LerpHprInterval(instrument, duration=1.5, startHpr=Vec3(145, 0, 0), hpr=Vec3(145, 0, 90), blendType='easeInOut')
    spinInstr = Parallel(spinInstr1)
    attackTrack = Parallel(Sequence(Wait(0.2), spinInstr), Sequence(stretchInstr, Wait(0.5), backInstr))
    hasLuredSuits = __hasLuredSuits(sound)
    delayTime = delay
    if hasLuredSuits:
        delayTime += TIME_TO_WALK_BACK
    megaphoneTrack = Sequence(Wait(delayTime), megaphoneShow, Wait(1.0), instrumentAppear, Wait(3.0), megaphoneHide)
    tracks.append(megaphoneTrack)
    toonTrack = __createToonInterval(sound, delay, toon)
    tracks.append(toonTrack)
    soundEffect = globalBattleSoundCache.getSound(soundFiles[level])
    if soundEffect:
        delayTime = delay + tSound
        if hasLuredSuits:
            delayTime += TIME_TO_WALK_BACK
        soundTrack = Sequence(Wait(delayTime), Parallel(attackTrack, IsolatedSoundInterval(soundEffect, node=toon)))
        tracks.append(soundTrack)
    return tracks


def __doOpera(sound, delay, toon, targets, level):
    tracks = Parallel()
    delay = delay
    instrMin = Vec3(0.001, 0.001, 0.001)
    instrMax1 = Vec3(1.7, 1.7, 1.7)
    instrMax1 *= INSTRUMENT_SCALE_MODIFIER
    instrMax2 = Vec3(2.2, 2.2, 2.2)
    instrMax2 *= INSTRUMENT_SCALE_MODIFIER
    instrStretch = Vec3(0.4, 0.4, 0.4)
    instrStretch *= INSTRUMENT_SCALE_MODIFIER
    megaphone = globalPropPool.getProp('blue-megaphone')
    megaphones = [megaphone]
    instrument = globalPropPool.getProp('singing')
    instruments = [instrument]
    # head = instrument.find('**/opera_singer')
    # head.setPos(0, 0, 0)

    def setInstrumentStats(instrument = instrument):
        notify.debug('setInstrumentStats')
        newPos = Vec3(-0.8, -0.9, 0.2)
        newPos *= 1.3
        instrument.setPos(newPos[0], newPos[1], newPos[2])
        instrument.setHpr(145, 0, 90)
        instrument.setScale(instrMin)

    hands = toon.getRightHands()
    megaphoneShow = Sequence(
        Func(MovieUtil.showProps, megaphones, hands), 
        Func(MovieUtil.showProps, instruments, hands), 
        Func(setInstrumentStats)
    )
    megaphoneHide = Sequence(
        Parallel(
            LerpScaleInterval(megaphone, 0.3, instrMin, blendType="easeInOut"),
        ),
        Func(MovieUtil.removeProps, megaphones), 
        Func(MovieUtil.removeProps, instruments),
    )
    instrumentAppearSfx = globalBattleSoundCache.getSound(appearSoundFiles[level])
    grow1 = getScaleBlendIntervals(instruments, duration=1, startScale=instrMin, endScale=instrMax1, blendType='easeOut')
    grow2 = getScaleBlendIntervals(instruments, duration=1.1, startScale=instrMax1, endScale=instrMax2, blendType='easeIn')
    shrink2 = getScaleIntervals(instruments, duration=0.1, startScale=instrMax2, endScale=instrMin)
    instrumentAppear = Parallel(Sequence(grow1, grow2, Wait(4.5), shrink2), Sequence(Wait(0.0), IsolatedSoundInterval(instrumentAppearSfx, node=toon)))
    hasLuredSuits = __hasLuredSuits(sound)
    delayTime = delay
    if hasLuredSuits:
        delayTime += TIME_TO_WALK_BACK
    megaphoneTrack = Sequence(Wait(delayTime), megaphoneShow, Wait(1.0), instrumentAppear, megaphoneHide)
    tracks.append(megaphoneTrack)
    toonTrack = __createToonInterval(sound, delay, toon, operaInstrument=instrument)
    tracks.append(toonTrack)
    soundEffect = globalBattleSoundCache.getSound(soundFiles[level])
    if soundEffect:
        delayTime = delay + tSound - 0.3
        if hasLuredSuits:
            delayTime += TIME_TO_WALK_BACK
        soundTrack = Sequence(Wait(delayTime), IsolatedSoundInterval(soundEffect, node=toon, duration=5.0))
        tracks.append(Sequence(Wait(0)))
        tracks.append(soundTrack)
    return tracks


def setPosFromOther(dest, source, offset = Point3(0, 0, 0)):
    pos = render.getRelativePoint(source, offset)
    dest.setPos(pos)
    dest.reparentTo(render)


def getScaleIntervals(props, duration, startScale, endScale, blendType="noBlend"):
    tracks = Parallel()
    for prop in props:
        tracks.append(LerpScaleInterval(prop, duration, endScale, startScale=startScale, blendType=blendType))

    return tracks


def getScaleBlendIntervals(props, duration, startScale, endScale, blendType):
    tracks = Parallel()
    for prop in props:
        tracks.append(LerpScaleInterval(prop, duration, endScale, startScale=startScale, blendType=blendType))

    return tracks


soundfn_array = (__doKazoo, __doBikehorn, __doWhistle, __doBugle,
                 __doAoogah, __doElephant, __doFoghorn, __doOpera)


def __getPartTrack(particleEffect, startDelay, durationDelay, partExtraArgs, softStop = 0):
    pEffect = partExtraArgs[0]
    parent = partExtraArgs[1]
    if len(partExtraArgs) == 3:
        worldRelative = partExtraArgs[2]
    else:
        worldRelative = 1
    return Sequence(Wait(startDelay), ParticleInterval(pEffect, parent, worldRelative, duration=durationDelay, cleanup=True, softStopT=softStop))
