"""Contains various types of attack classes which to inherit functionality from."""

from panda3d.core import Point3, Vec3
from toontown.chat.constants.ChatGlobals import  CFSpeech, CFTimeout
from direct.interval.IntervalGlobal import *

from toontown.audio.IsolatedSoundInterval import IsolatedSoundInterval
from toontown.battle import MovieUtil

from toontown.battle.attacks.base.AttackEnum import AttackEnum
from toontown.battle.attacks.client.Attack import Attack
from toontown.battle.attacks.client.AttackRepository import AttackClass
from toontown.battle.visuals.VisualEffectEnums import VisualEffectEnum
from toontown.cutscene.repository.CutsceneLoader import CutsceneLoader
from toontown.toonbase import TTLocalizer, ToontownGlobals


@AttackClass(attackType=AttackEnum.AVATAR_SAY_PHRASE)
class AvatarSayPhraseAttack(Attack):
    OPEN_SHOT_DUR = 10
    WANT_TARGET_INDICATORS = False
    ClearChat = False
    ExtraArgPhraseIndex = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sayPhraseType = self.extraArgs[self.ExtraArgPhraseIndex]

    @property
    def phraseData(self):
        return TTLocalizer.GeneralAttackSayPhrases[self.sayPhraseType]

    @property
    def avatar(self):
        return self.invoker

    def doAttack(self):
        # Grab a phrase that will be consistent across all clients
        phraseIndex = self.avatar.doId % len(self.phraseData[0])
        phrase = self.phraseData[0][phraseIndex]
        phraseTime = self.phraseData[1]
        sayPhraseSeq = Sequence(
            Wait(0.25),
            Func(self.avatar.setChatAbsolute, phrase, CFSpeech | CFTimeout),
            Wait(phraseTime),
        )
        if self.ClearChat:
            sayPhraseSeq.append(Func(self.avatar.clearChat))
        return sayPhraseSeq

    def getCameraShot(self, duration):
        return self.camera.heldRelativeShot(self.avatar, 0, 12, 13, 180, -30, 0, duration, 'singleAvatarShot')


@AttackClass(attackType=AttackEnum.AVATAR_SAY_PHRASE_ON_TARGET)
class AvatarSayPhraseOnTargetAttack(AvatarSayPhraseAttack):
    WANT_TARGET_INDICATORS = False

    @property
    def avatar(self):
        return self.targetObjs[0]

    @property
    def shouldClearChat(self):
        return self.ClearChat or (len(self.extraArgs) > 1 and self.extraArgs[1])

    def doAttack(self):
        globalPhraseSeq = Parallel()
        # Grab a phrase that will be consistent across all clients
        for target in self.targetDicts:
            avatar = target["avatar"]
            avId = avatar.doId

            phraseIndex = avId % len(self.phraseData[0])
            phrase = self.phraseData[0][phraseIndex]
            phraseTime = self.phraseData[1]
            sayPhraseSeq = Sequence(
                Wait(0.25),
                Func(avatar.setChatAbsolute, phrase, CFSpeech | CFTimeout),
                Wait(phraseTime),
            )
            if self.shouldClearChat:
                sayPhraseSeq.append(Func(avatar.clearChat))
            globalPhraseSeq.append(sayPhraseSeq)

        return globalPhraseSeq

    def getCameraShot(self, duration):
        if len(self.targetObjs) == 1:
            return self.camera.heldRelativeShot(self.avatar, 0, 12, 13, 180, -30, 0, duration, 'singleAvatarShot')
        else:
            return self.camera.toonGroupShot(duration=duration)


class AllowGroupingAttack(Attack):
    ALLOW_GROUPING = True


@AttackClass(attackType=AttackEnum.SUIT_HEAL)
class SuitHealAttack(AllowGroupingAttack):
    OPEN_SHOT_DUR = 1.5
    WANT_TARGET_INDICATORS = False

    def doAttack(self):
        healTracks = Parallel()

        for suit in self.targetObjs:
            result = self.findTarget(suit.doId)
            healHP = result.hpAdjust
            seq = Func(self.updateSuitHP, suit, healHP, nonZero=True)
            healTracks.append(seq)

        sfx = loader.loadSfx("phase_11/audio/sfx/LB_toonup.ogg")
        soundTrack = IsolatedSoundInterval(sfx)
        return Sequence(
            Parallel(soundTrack, healTracks, Wait(1.5))
        )


@AttackClass(attackType=AttackEnum.TOON_DAMAGE)
class ToonDamageAttack(AllowGroupingAttack):
    OPEN_SHOT_DUR = 3.0
    HP_TEXT_TYPE = None

    def doAttack(self):
        damageAnims = [["cringe", 0.01, 0.01, 0.7], ["cringe", 0.01, 0.01, 0.7]]
        toonTrack = self.getToonTrack(
            damageDelay=0,
            splicedDamageAnims=damageAnims,
            dodgeDelay=3.0,
            dodgeAnimNames=["sidestep"],
            showDamageExtraTime=1.8,
            showMissedExtraTime=0.8,
            hpTextType=self.HP_TEXT_TYPE,
        )

        return Sequence(Parallel(Sequence(toonTrack), Wait(3.0)))


@AttackClass(attackType=(AttackEnum.SUIT_DAMAGE,))
class SuitDamageAttack(AllowGroupingAttack):
    OPEN_SHOT_DUR = 2.25
    EXTRA_TEXT = None
    WANT_TARGET_INDICATORS = False

    def doAttack(self):
        damageTracks = Parallel()

        for suit in self.targetObjs:
            result = self.findTarget(suit.doId)
            damageHP = result.hpAdjust

            def loopNeutralAnim(suit):
                loopAnim = "lured" if suit.isLured else "neutral"
                suit.loop(loopAnim)

            seq = Sequence(
                Func(self.updateSuitHP, suit, damageHP),
                ActorInterval(suit, "pie-small-react"),
                Func(loopNeutralAnim, suit),
            )

            damageTracks.append(seq)

        return Sequence(Parallel(Sequence(damageTracks), Wait(2.25)))

    def updateSuitHP(self, suit, damage):
        suit.updateHealthBar(damage)
        suit.showHpText(damage, extraText=self.EXTRA_TEXT or "")


@AttackClass(attackType=AttackEnum.SUIT_MARKED_DAMAGE)
class MarkedSuitDamageAttack(SuitDamageAttack):
    OPEN_SHOT_DUR = 3.0
    EXTRA_TEXT = TTLocalizer.HpTextMarked


# Override to show the "Damage absorbed!" text.
@AttackClass(attackType=(AttackEnum.DAMAGE_ABSORB_SUIT_DAMAGE, AttackEnum.DAMAGE_ABSORB_SUIT_DAMAGE_WITH_UNLURE))
class DamageAbsorbSuitDamageAttack(SuitDamageAttack):
    OPEN_SHOT_DUR = 3.0
    EXTRA_TEXT = TTLocalizer.HpTextDamageAbsorbed


@AttackClass(attackType=AttackEnum.DAMAGE_ABSORB_SUIT_DAMAGE_INSTANT)
class DamageAbsorbInstantSuitDamageAttack(SuitDamageAttack):
    OPEN_SHOT_DUR = 0.0

    def doAttack(self):
        damageTracks = Parallel()

        for suit in self.targetObjs:
            result = self.findTarget(suit.doId)
            damageHP = result.hpAdjust
            seq = Sequence(
                Func(self.updateSuitHP, suit, damageHP),
            )
            damageTracks.append(seq)

        return Sequence(Parallel(Sequence(damageTracks), Wait(0.01)))

    def getCameraShot(self, duration):
        return Wait(duration)

    def updateSuitHP(self, suit, damage):
        suit.updateHealthBar(damage)


@AttackClass(attackType=AttackEnum.DAMAGE_ABSORB_TOON_DAMAGE)
class DamageAbsorbToonDamageAttack(ToonDamageAttack):
    HP_TEXT_TYPE = TTLocalizer.HP_TEXT_ABSORBED


@AttackClass(attackType=AttackEnum.SHOW_HP_TEXT)
class ShowHpTextAttack(Attack):
    """
    You can pass in 1 extra arg to show a certain HP text across all targets.
    Pass in a list of extra args corresponding to each target to show the HP text to their respective target.
    """
    OPEN_SHOT_DUR = 2.25
    WANT_TARGET_INDICATORS = False

    def doAttack(self):
        hpTextTracks = Parallel()

        if len(self.extraArgs) != len(self.targetObjs):
            self.extraArgs = [self.extraArgs[0] for _ in range(len(self.targetObjs))]
        for target, textInfo in {self.targetObjs[i]: self.extraArgs[i] for i in range(len(self.targetObjs))}.items():
            hpTextString, hpTextColor = TTLocalizer.GeneralAttackHpTexts[textInfo]
            hpTextTracks.append(Sequence(Func(target.hideHpText),
                                         Func(target.showHpString, hpTextString, 0.85, 0.7, hpTextColor)))

        return Sequence(Parallel(Sequence(hpTextTracks), Wait(2.25)))


@AttackClass(attackType=AttackEnum.SHOW_PIP_TEXT)
class ShowPipTextAttack(Attack):
    """
    Largely the same as the above attack, but instead of passing in localizer enums, you'll pass in pip diffs.
    """
    WANT_TARGET_INDICATORS = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.OPEN_SHOT_DUR, *self.pipCounts = self.extraArgs

    def doAttack(self):
        hpTextTracks = Parallel()
        playingSound = False

        if len(self.pipCounts) != len(self.targetObjs):
            self.pipCounts = [self.pipCounts[0] for _ in range(len(self.targetObjs))]
        for target, pips in {self.targetObjs[i]: self.pipCounts[i] for i in range(len(self.targetObjs))}.items():
            if pips == 0:
                continue
            hpTextString, hpTextColor = TTLocalizer.GeneralAttackHpTexts[TTLocalizer.HP_TEXT_SHOW_PIPS]
            hpTextString = hpTextString % f"{'+' if pips > 0 else ''}{str(pips)}"
            if pips in range(-1, 2):
                hpTextString = hpTextString.replace('S', '')  # You're welcome Sketched
            hpTextTracks.append(Sequence(Func(target.hideHpText),
                                         Func(target.showHpString, hpTextString, 0.85, 0.7, hpTextColor)))
            if pips > 0 and not playingSound:
                healSfx = loader.loadSfx("phase_11/audio/sfx/LB_toonup.ogg")
                hpTextTracks.append(Func(healSfx.play))
                playingSound = True

        if not self.OPEN_SHOT_DUR:
            return hpTextTracks
        else:
            return Parallel(hpTextTracks, Wait(self.OPEN_SHOT_DUR))

    def getCameraShot(self, duration):
        camAv = base.localAvatar
        if not camAv:
            camAv = self.targetObjs[0]
        return self.camera.heldRelativeShot(camAv, 0, 11, (camAv.height / 2) + 2.25, 180, 0, 0, duration, 'singleAvatarShot')


@AttackClass(attackType=AttackEnum.SUIT_LURE)
class SuitLureAttack(AllowGroupingAttack):
    OPEN_SHOT_DUR = 3.0
    WANT_TARGET_INDICATORS = False

    def doAttack(self):
        lureTracks = Parallel()

        def handleLureSuit(suit):
            suitTrack = Sequence()
            opos, ohpr = self.battle.getActorPosHpr(suit)
            reachDist = MovieUtil.SUIT_LURE_DISTANCE
            reachPos = Point3(opos[0], opos[1] - reachDist, opos[2])
            suitTrack.append(Func(suit.loop, "walk"))
            suitTrack.append(LerpPosInterval(suit, 0.5, reachPos, other=self.battle))
            suitTrack.append(MovieUtil.lureSuit(suit))
            suitTrack.append(Func(suit.loop, "neutral"))
            return suitTrack

        for suit in self.targetObjs:
            seq = handleLureSuit(suit)
            lureTracks.append(seq)

        return Sequence(Wait(1.5), Parallel(Sequence(lureTracks, Wait(1.5))))


@AttackClass(attackType=AttackEnum.SUIT_UNLURE)
class SuitUnlureAttack(AllowGroupingAttack):
    OPEN_SHOT_DUR = 0.0
    WANT_TARGET_INDICATORS = False

    def doAttack(self):
        unlureTracks = Parallel()

        for suit in self.targetObjs:
            unlureTracks.append(MovieUtil.createSuitUnlureTrack(suit, self.battle))

        return unlureTracks


@AttackClass(attackType=AttackEnum.APPLY_VISUAL_EFFECT_MOVIE)
class ApplyVisualEffectMovieAttack(AllowGroupingAttack):
    OPEN_SHOT_DUR = 0.5
    WANT_TARGET_INDICATORS = False

    def doAttack(self):
        hpTextTracks = Parallel()

        for target in self.targetObjs:
            effectEnum = VisualEffectEnum(self.extraArgs[0])
            hpTextTracks.append(Func(MovieUtil.applyVisualEffect, target, effectEnum))

        return Sequence(Parallel(Sequence(hpTextTracks)))


@AttackClass(attackType=AttackEnum.REMOVE_VISUAL_EFFECT)
class RemoveVisualEffectAttack(AllowGroupingAttack):
    OPEN_SHOT_DUR = 0.5
    WANT_TARGET_INDICATORS = False

    def doAttack(self):
        hpTextTracks = Parallel()

        for target in self.targetObjs:
            effectEnum = VisualEffectEnum(self.extraArgs[0])
            wantApplyLock = False if len(self.extraArgs) < 2 else self.extraArgs[1]
            hpTextTracks.append(Func(MovieUtil.unapplyVisualEffect, target, [effectEnum], wantApplyLock))

        return Sequence(Parallel(Sequence(hpTextTracks)))


@AttackClass(attackType=(AttackEnum.AVATAR_INSTAKILL, AttackEnum.HIGHROLLER_HOLLYWOOD,
                         AttackEnum.HIGHROLLER_BEGIN_MADNESS,))
class DoNothing(Attack):
    """For all of your doing nothing needs."""
    WANT_TARGET_INDICATORS = False

    def getAttackMovie(self):
        return Sequence(), Sequence()

    def getCameraShot(self, duration):
        return Sequence()


class PlayCutsceneAttack(Attack):
    CUTSCENE_KEY = None
    WANT_TARGET_INDICATORS = False

    def doAttack(self):
        assert self.CUTSCENE_KEY is not None
        kwargs = {
            'battle': self.battle,
            'invoker': self.invoker,
        }
        if hasattr(self.battle, 'instance'):
            kwargs['instance'] = self.battle.instance
        kwargs.update(self.getLoaderKwargs())
        cutsceneLoader = CutsceneLoader.createLoader(
            key=self.CUTSCENE_KEY,
            **kwargs
        )
        return cutsceneLoader.buildCutscene()

    def getCameraShot(self, duration):
        return Wait(duration)

    def getLoaderKwargs(self) -> dict:
        return {}


@AttackClass(attackType=AttackEnum.COGS_FLY_AWAY)
class CogsFlyAway(Attack):
    """TODO : fix this attack"""
    WANT_TARGET_INDICATORS = False

    def getSuitDeathMovie(self, suit):
        return suit.beginSupaFlyMove(
            Point3(0, 0, 0),
            moveIn = 0,
            trackName = 'flyOut',
            flyOutBasedOnCurrentPos = True,
            speed=1.3, soundSpeed=1.3,
        )


@AttackClass(attackType=AttackEnum.SUITS_ADJUST_POSITION)
class SuitsAdjustPosition(Attack):
    WANT_TARGET_INDICATORS = False

    def doAttack(self):
        adjustAllSuitsAfterSeq = Parallel()
        suitToWalkIval = {}

        def runAdjustSeq():
            for i, moveSuit in enumerate([moveSuit for moveSuit in self.battle.activeSuits if not getattr(moveSuit, 'deadOrAboutToBe', False)]):
                newMoveSuitPos, newMoveSuitHpr = self.battle.getActiveSuitPosHpr(moveSuit)
                moveDist = Vec3(newMoveSuitPos - moveSuit.getPos(self.battle)).length()

                # Doing it this way so that nuclear cog's glitchy effect doesn't interfere with anything
                suitToWalkIval[moveSuit] = Sequence()

                def startSuitWalk(suit=moveSuit):
                    nonlocal suitToWalkIval
                    walkInterval = ActorInterval(suit, 'walk')
                    walkInterval.loop()
                    suitToWalkIval[suit] = walkInterval

                def finishSuitWalk(suit=moveSuit):
                    nonlocal suitToWalkIval
                    walkInterval = suitToWalkIval[suit]
                    walkInterval.finish()
                    suitToWalkIval[suit] = None

                suitMoveSeq = Sequence(
                    Func(moveSuit.headsUp, self.battle, newMoveSuitPos),
                    Func(startSuitWalk, suit=moveSuit),
                    LerpPosInterval(moveSuit, min(moveDist / ToontownGlobals.SuitWalkSpeed, 0.5), newMoveSuitPos, other=self.battle),
                    Func(finishSuitWalk, suit=moveSuit),
                    Func(moveSuit.loop, 'lured' if moveSuit.isLured else 'neutral'),
                    Func(moveSuit.setHpr, self.battle, newMoveSuitHpr),
                )
                adjustAllSuitsAfterSeq.append(suitMoveSeq)

            adjustAllSuitsAfterSeq.start()

        def finishAdjustSeq():
            if adjustAllSuitsAfterSeq:
                adjustAllSuitsAfterSeq.finish()

        return Sequence(Func(runAdjustSeq), Wait(0.5), Func(finishAdjustSeq))

    def getCameraShot(self, duration):
        return self.camera.allGroupOverheadShot(duration=duration)
