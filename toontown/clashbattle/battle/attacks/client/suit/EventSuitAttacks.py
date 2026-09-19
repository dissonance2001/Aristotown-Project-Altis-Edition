import math
import random

from panda3d.core import VBase4, Vec4, Point3, VBase3, TransparencyAttrib
from toontown.chat.constants.ChatGlobals import  CFSpeech, CFTimeout
from direct.interval.IntervalGlobal import *
from direct.task.TaskManagerGlobal import taskMgr

from otp.nametag import NametagGroup
from toontown.audio.IsolatedSoundInterval import IsolatedSoundInterval
from toontown.battle import BattleParticles, BattleProps, MovieUtil, MovieZap, SuitBattleGlobals, BattleGlobals
from toontown.battle.BattleProps import globalPropPool
from toontown.battle.BattleSounds import globalBattleSoundCache
from toontown.battle.MovieUtil import createKapowExplosionTrack
from toontown.battle.attacks.base.AttackEnum import AttackEnum
from toontown.battle.attacks.client.Attack import Attack
from toontown.battle.attacks.client.AttackRepository import AttackClass
from toontown.battle.attacks.client.suit import SuitGroupAttack
from toontown.battle.attacks.client.suit.BasicAttacks import AvatarSayPhraseAttack
from toontown.battle.attacks.client.suit.BasicSuitAttacks import TeeOff, Synergy, CigarSmoke
from toontown.battle.attacks.client.suit.SuitSingleAttack import SuitSingleAttack
from toontown.battle.attacks.client.suit.MercSuitAttacks import PickUpThePace, ShatterDamage
from toontown.battle.attacks.client.suit.MinibossSuitAttacks import Objection
from toontown.battle.visuals.VisualEffectEnums import VisualEffectEnum
from toontown.battle.visuals.VisualEffects import ErfitReviveVisualEffect
from toontown.building import ElevatorConstants, ElevatorUtils
from toontown.instances import HighRollerGlobals
from toontown.toonbase import TTLocalizer, ToontownGlobals
from toontown.toonbase.ToontownGlobals import CountErclaimBattleAPosHpr
from toontown.cutscene.repository.CutsceneLoader import CutsceneLoader
from toontown.cutscene.repository.CutsceneKeyEnum import CutsceneKeyEnum


@AttackClass(attackType=AttackEnum.LAFF_STEAL)
class LaffSteal(SuitSingleAttack):
    ANIM_NAME = "magic1"
    CHEAT = True
    OPEN_SHOT_DUR = 4.5

    def doAttack(self):
        result = self.findTarget(self.invoker.doId)
        healHP = result.hpAdjust
        suitTrack = self.getSuitAnimTrack()

        # Making Red Dot Particles
        BattleParticles.loadParticles()
        particleEffectRed = BattleParticles.createParticleEffect("LaffSteal")
        BattleParticles.setEffectTexture(particleEffectRed, "snow-particle")
        partTrack = self.getPartTrack(
            particleEffectRed,
            1e-05,
            suitTrack.getDuration(),
            [particleEffectRed, self.invoker, 0],
            softStop=-1.0,
        )

        sfx = self.getSoundTrack(
            "phase_13/audio/sfx/halloween/SA_laff_steal.ogg", delay=0, node=self.invoker
        )

        toonTrack = Parallel()
        for toon in self.battle.activeToons:
            # Toon Reaction
            reactionTrack = Sequence()
            reactionTrack.append(
                Func(toon.headsUp, self.battle, self.invoker.getPos(self.battle))
            )
            reactionTrack.append(Wait(0.2))
            reactionTrack.append(ActorInterval(toon, "cringe", playRate=0.7))
            reactionTrack.append(Func(toon.loop, "neutral"))
            toonTrack.append(reactionTrack)

        healSfx = loader.loadSfx("phase_11/audio/sfx/LB_toonup.ogg")
        suitTrack = Sequence(suitTrack, Func(self.invoker.loop, "neutral"))
        return Parallel(
            Sequence(
                Wait(2.0),
                Parallel(Func(self.updateSuitHP, self.invoker, healHP),
                SoundInterval(healSfx, node=self.invoker)),
            ),
            suitTrack,
            partTrack,
            sfx,
            toonTrack,
        )

    def getCameraShot(self, duration):
        return self.camera.heldRelativeShot(
            self.invoker, 0, 22, 10, 180, -18, 0, duration, "laffStealShot"
        )

    def getSoundTrack(self, filePath, delay=0.01, duration=None, node=None):
        soundEffect = loader.loadSfx(filePath)
        if duration:
            return Sequence(
                Wait(delay), SoundInterval(soundEffect, duration=duration, node=node)
            )
        else:
            return Sequence(Wait(delay), SoundInterval(soundEffect, node=node))


@AttackClass(attackType=AttackEnum.RISE_FROM_THE_SCRAP)
class RiseFromTheScrap(SuitSingleAttack):
    ANIM_NAME = "effort"
    CHEAT = True
    OPEN_SHOT_DUR = 7.0

    def doAttack(self):
        suitTrack = self.getSuitAnimTrack()

        sfx = self.getSoundTrack(
            "phase_13/audio/sfx/halloween/SA_rise_from_the_scrap.ogg",
            delay=0,
            node=self.invoker,
        )

        darkenTime = 3.0
        lightenTime = 1.0
        darkenColor = (0.15, 0.15, 0.15, 1.0)
        normalColor = (1.0, 1.0, 1.0, 1.0)

        darkenTrack = Sequence(
            Func(self.invoker.wrtReparentTo, render),
            Wait(0.25),
            Parallel(
                LerpColorScaleInterval(
                    self.battle, darkenTime, darkenColor, blendType="easeIn"
                ),
                LerpColorScaleInterval(
                    base.bossGeom, darkenTime, darkenColor, blendType="easeIn"
                ),
            ),
            Wait(1.0),
            Parallel(
                LerpColorScaleInterval(
                    self.battle, lightenTime, normalColor, blendType="easeOut"
                ),
                LerpColorScaleInterval(
                    base.bossGeom, lightenTime, normalColor, blendType="easeOut"
                ),
            ),
            Func(self.invoker.wrtReparentTo, self.battle),
        )

        flashRed = Sequence(
            LerpColorScaleInterval(
                self.invoker, 0.2, colorScale=VBase4(1, 0.2, 0.2, 1)
            ),
            LerpColorScaleInterval(self.invoker, 0.6, colorScale=VBase4(1, 1, 1, 1)),
        )
        redTrack = Sequence(
            Wait(0.8),
            flashRed,
            Wait(0.5),
            flashRed,
            Wait(0.5),
            flashRed,
            Wait(0.5),
            flashRed,
        )

        suitTrack = Sequence(suitTrack, Func(self.invoker.loop, "neutral"))
        return Parallel(suitTrack, darkenTrack, redTrack, sfx)

    def getSoundTrack(self, filePath, delay=0.01, duration=None, node=None):
        soundEffect = loader.loadSfx(filePath)
        if duration:
            return Sequence(
                Wait(delay), SoundInterval(soundEffect, duration=duration, node=node)
            )
        else:
            return Sequence(Wait(delay), SoundInterval(soundEffect, node=node))


@AttackClass(attackType=AttackEnum.SACRIFICE)
class Sacrifice(SuitSingleAttack):
    ANIM_NAME = "quick-jump"
    CHEAT = True
    OPEN_SHOT_DUR = 5.0

    def doAttack(self):
        chosenSuit = self.targetObjs[0]
        result = self.findTarget(self.invoker.doId)
        healHP = result.hpAdjust
        suitTrack = self.getSuitAnimTrack()
        soundTrack = self.getSoundTrack(
            "phase_13/audio/sfx/halloween/SA_sacrifice.ogg",
            delay=1.0,
            node=self.invoker,
        )
        trapProp = BattleProps.globalPropPool.getProp("quicksand")
        trapProp.setColor(Vec4(0.1, 0.1, 1.0, 1))
        trapProp.setHpr(Point3(300, 0, 0))
        trapProp.setScale(0.01)

        dmgMult = self.extraArgs[0] / 100

        healSfx = loader.loadSfx("phase_11/audio/sfx/LB_toonup.ogg")

        def updateSuitHP(suit, hp, response=False):
            suit.updateHealthBar(hp)
            suit.showHpText(hp)
            if response:
                chosenResponse = random.choice(
                    TTLocalizer.CountErclaimCogSacrificeResponses
                )
                suit.setChatAbsolute(chosenResponse, CFSpeech | CFTimeout)

        smallScale = 0.01
        bigScale = 2.25
        biggerScale = 2.5
        trapTrack = Sequence(
            Wait(0.1),
            LerpScaleInterval(trapProp, 0.65, biggerScale, blendType="easeIn"),
            LerpScaleInterval(trapProp, 0.15, bigScale, blendType="easeOut"),
            Wait(1.5),
            LerpScaleInterval(trapProp, 0.15, biggerScale, blendType="easeIn"),
            LerpScaleInterval(trapProp, 0.65, smallScale, blendType="easeOut"),
            Func(trapProp.removeNode),
        )

        def setupHole():
            suitPos = chosenSuit.getPos(render)
            trapProp.setPos(suitPos)
            trapProp.reparentTo(render)

        moveTrack = Sequence(
            Func(setupHole),
            Wait(0.9),
            LerpPosInterval(chosenSuit, 0.9, (0, 0, -1.65), other=trapProp),
            LerpPosInterval(chosenSuit, 0.4, (0, 0, -5.2), other=trapProp),
            Func(chosenSuit.wrtReparentTo, hidden),
        )

        animTrack = Sequence(
            ActorInterval(chosenSuit, "flail"),
            ActorInterval(chosenSuit, "flail", startTime=1.1),
        )

        animTrack.append(
            Sequence(Wait(0.7), ActorInterval(chosenSuit, "slip-forward", duration=2.1))
        )

        fallingSoundTrack = Sequence(
            Wait(0.7),
            SoundInterval(
                globalBattleSoundCache.getSound("TL_quicksand.ogg"), node=chosenSuit
            ),
            Wait(0.1),
        )

        dmgMultTrack = Sequence(
            Wait(4.45),
            Func(base.playSfx, healSfx),
            Func(
                self.invoker.showHpString,
                text=TTLocalizer.SuitAttackDmgMult % str(dmgMult),
                color=(0.45, 0.45, 1.0, 1.0),
            ),
        )

        suitFallTrack = Sequence(
            Wait(1.2), Parallel(trapTrack, moveTrack, animTrack, fallingSoundTrack)
        )

        suitTalkTrack = Sequence(
            Wait(2.4),
            Func(updateSuitHP, chosenSuit, -healHP, True),
            Func(base.playSfx, healSfx),
            Func(updateSuitHP, self.invoker, healHP, False),
            Wait(2.5),
            Func(chosenSuit.clearChat),
        )

        return Parallel(
            suitTrack, suitFallTrack, suitTalkTrack, dmgMultTrack, soundTrack
        )

    def getCameraShot(self, duration):
        shakeIntensity = 1
        quake = 1
        return self.camera.suitCameraShakeShot(duration, shakeIntensity, quake)

    def getSoundTrack(self, filePath, delay=0.01, duration=None, node=None):
        soundEffect = loader.loadSfx(filePath)
        if duration:
            return Sequence(
                Wait(delay), SoundInterval(soundEffect, duration=duration, node=node)
            )
        else:
            return Sequence(Wait(delay), SoundInterval(soundEffect, node=node))

    def getAttackDisplayName(self):
        if len(self.extraArgs) <= 2:
            # the normal name for this attack
            return TTLocalizer.SuitAttackNames[self.attackType]
        else:
            # If extra extra args were passed, it is definitely from something else.
            # In this case, index 2 indicates intent.
            intent = self.extraArgs[2]
            return TTLocalizer.SuitAttackBonusPhrases["sacrifice_alts"][intent]


@AttackClass(attackType=AttackEnum.SCOPE_CREEP)
class ScopeCreep(RiseFromTheScrap):
    ANIM_NAME = "effort"
    CHEAT = True
    OPEN_SHOT_DUR = 5.0

    def doAttack(self):
        suitTrack = self.getSuitAnimTrack()

        sfx = self.getSoundTrack(
            "phase_13/audio/sfx/halloween/SA_rise_from_the_scrap.ogg",
            delay=0,
            node=self.invoker,
        )
        lightningSfx = globalBattleSoundCache.getSound("AA_lightning.ogg")

        oldcolor = MovieZap.lightningPreColor()
        darkenTime = 2.0
        lightenTime = 1.0
        darkenColor = (0.15, 0.15, 0.15, 1.0)
        normalColor = (1.0, 1.0, 1.0, 1.0)

        darkenTrack = Sequence(
            Func(self.invoker.wrtReparentTo, render),
            Wait(0.25),
            Parallel(
                LerpColorScaleInterval(
                    self.battle, darkenTime, darkenColor, blendType="easeIn"
                ),
                LerpColorScaleInterval(
                    render, darkenTime, darkenColor, blendType="easeIn"
                ),
            ),
            Wait(1.5),
            Parallel(
                LerpColorScaleInterval(
                    self.battle, lightenTime, normalColor, blendType="easeOut"
                ),
                LerpColorScaleInterval(
                    render, lightenTime, oldcolor, blendType="easeOut"
                ),
            ),
            Func(MovieZap.lightningPostColor),
            Func(self.invoker.wrtReparentTo, self.battle),
        )

        sfx2 = Sequence(
            Wait(0.7),
            SoundInterval(lightningSfx, node=None),
        )

        flashRed = Sequence(
            LerpColorScaleInterval(
                self.invoker, 0.2, colorScale=VBase4(0.9, 0.1, 0.1, 1)
            ),
            LerpColorScaleInterval(self.invoker, 0.6, colorScale=VBase4(1, 1, 1, 1)),
        )
        redTrack = Sequence(
            Wait(0.8),
            flashRed,
            Wait(0.5),
            flashRed,
            Wait(0.5),
            flashRed,
            Wait(0.5),
            flashRed,
        )

        suitTrack = Sequence(suitTrack, Func(self.invoker.loop, "neutral"))
        return Parallel(suitTrack, darkenTrack, redTrack, sfx, sfx2)


@AttackClass(attackType=AttackEnum.HYDRATION_CHECK)
class HydrationCheck(SuitSingleAttack):
    ANIM_NAME = "throw-object"
    OPEN_SHOT_DUR = 3.03

    def doAttack(self):
        target = self.targetDicts[0]
        damage = target["hp"]
        result = self.findTarget(target["avatar"].doId)
        dodged = not result.landed
        toon = target["avatar"]
        glass = globalPropPool.getProp("glass")

        # The other boring parts.
        suitTrack = self.getSuitTrack()
        glassPosPoints = [Point3(-0.14, -0.29, -0.58), VBase3(0, 0, 0)]
        glassScaleUpPoint = Point3(1, 1, 1)  # Point3(0.9, 0.9, 0.24) * 3
        propTrack = Sequence(
            self.getPropAppearTrack(
                glass,
                self.invoker.getRightHand(),
                glassPosPoints,
                0.8,
                glassScaleUpPoint,
                scaleUpTime=0.5,
            )
        )
        propTrack.append(Wait(1.73))
        hitPoint = lambda toon=toon: self.toonTorsoPoint(toon)
        hitDuration = 0.5
        propTrack.append(
            Parallel(
                self.getPropThrowTrack(
                    glass,
                    [hitPoint],
                    [self.toonGroundPoint(toon, 0.7)],
                    hitDuration=hitDuration,
                ),
                LerpHprInterval(glass, hitDuration, Point3(360, 360, 360)),
            )
        )

        if not dodged:
            # The unite disable track.
            uniteDisableTrack = Sequence()
            if toon is base.localAvatar:
                uniteDisableTrack = Sequence(
                    Func(self.battle.addUniteDisabledFlag, "hydration-check-no-unites"),
                    Func(toon.requestAddUniteImmunityFlag, 1),
                )

            # The elevator opening and closing.
            sfx = base.loader.loadSfx(
                "phase_3.5/audio/dial/AV_" + toon.style.getAnimal() + "_exclaim.ogg"
            )
            elevatorTrack = Sequence()
            if hasattr(base, "bossElevatorModel"):
                bem = base.bossElevatorModel
                elevatorTrack = Sequence(
                    Wait(2.0),
                    ElevatorUtils.getOpenInterval(
                        None,
                        bem.find("**/left_door"),
                        bem.find("**/right_door"),
                        None,
                        None,
                        ElevatorConstants.ELEVATOR_DERRICK_MAN,
                    ),
                    Wait(0.3),
                    Parallel(
                        ElevatorUtils.getCloseInterval(
                            None,
                            bem.find("**/left_door"),
                            bem.find("**/right_door"),
                            None,
                            None,
                            ElevatorConstants.ELEVATOR_DERRICK_MAN,
                        ),
                        Sequence(
                            Wait(0.5),
                            SoundInterval(sfx, node=toon, volume=0.7),
                        ),
                    ),
                    Func(toon.hide),
                    uniteDisableTrack,
                )

            # Particle track.
            BattleParticles.loadParticles()
            freezeEffect = BattleParticles.createParticleEffect(file="demotionUnFreeze")
            BattleParticles.setEffectTexture(freezeEffect, "snow-particle")
            facePoint = self.toonFacePoint(toon)
            freezeEffect.setPos(toon.getPos() + (0, 0, facePoint.getZ()))
            suitTrack = self.getSuitTrack()
            partTrack2 = self.getPartTrack(
                freezeEffect, 0.0, 0.5, [freezeEffect, render, 0]
            )

            # The toon being shot backwards.
            toonMoveTrack = Sequence(
                Wait(3.44),
                Parallel(
                    LerpPosInterval(
                        toon, 1.0, Point3(0, -40.0, 0), blendType="easeOut"
                    ),
                    LerpHprInterval(toon, 1.0, Point3(720, 0, 0), blendType="easeOut"),
                    partTrack2,
                ),
            )

            toonTrack = self.getToonTrack(
                3.44,
                ["slip-backward"],
                2.8,
                ["sidestep"],
                hpTextType=TTLocalizer.HP_TEXT_HYDRATED,
                forceHit=True,
            )
            soundTrack = self.getSoundTrack(
                "phase_13/audio/sfx/april_toons/SA_hydrate.ogg",
                delay=2.9,
                node=self.invoker,
            )
            return Parallel(
                suitTrack,
                toonTrack,
                propTrack,
                soundTrack,
                elevatorTrack,
                toonMoveTrack,
            )
        else:
            # The toon has passed the hydration check.
            # The water drink anim.
            startTime = 1.0
            drinkDuration = 1.7
            tracks = Parallel()
            tracks.append(
                Sequence(
                    ActorInterval(
                        toon, "spit", startTime=startTime, duration=drinkDuration
                    ),
                    Func(toon.loop, "neutral"),
                )
            )
            soundTrack = Sequence(
                Wait(1.7 - startTime),
                SoundInterval(
                    globalBattleSoundCache.getSound("AA_squirt_glasswater.ogg"),
                    node=toon,
                    duration=drinkDuration - startTime,
                ),
            )
            tracks.append(soundTrack)
            glass = globalPropPool.getProp("glass")
            hands = toon.getRightHands()
            hand_jointpath0 = hands[0].attachNewNode("handJoint0-path")
            glassTrack = Sequence(
                Func(MovieUtil.showProp, glass, hand_jointpath0),
                ActorInterval(glass, "glass", startTime=0.5, playRate=2.0),
                Func(hand_jointpath0.removeNode),
                Func(MovieUtil.removeProp, glass),
                Func(toon.loop, "neutral"),
            )
            tracks.append(glassTrack)

            # The toon catching the glass track.
            catchAndDrinkTrack = Sequence(
                Wait(3.44),
                tracks,
            )

            # The toon receiving the heal.
            throwSoundTrack = Parallel(
                Sequence(
                    Wait(2.9),
                    SoundInterval(
                        globalBattleSoundCache.getSound("AA_pie_throw_only.ogg"),
                        node=self.invoker,
                    ),
                ),
                self.getSoundTrack(
                    "phase_6/audio/sfx/CC_move.ogg", delay=3.4, node=toon
                ),
            )
            soundTrack = self.getSoundTrack(
                "SA_life_insurance_register.ogg", delay=0, node=toon
            )
            text, textColor = TTLocalizer.GeneralAttackHpTexts[
                TTLocalizer.HP_TEXT_HYDRATION_PASSED
            ]
            healFunc = (
                Func(toon.showHpString, text, color=textColor)
                if damage == 0
                else Func(toon.toonUp, -damage, False, text, True)
            )
            toonTrack = Sequence(
                Wait(4.0),
                healFunc,
                soundTrack,
            )

            return Parallel(
                suitTrack, propTrack, catchAndDrinkTrack, toonTrack, throwSoundTrack
            )

    def getCameraShot(self, duration):
        # Some logic to get the end point for the camera shot
        toon = self.targetDicts[0]["avatar"]
        height = toon.getHeight()
        centralPoint = toon.getPos(self.battle)
        pos = Point3(6, -0.5, 4.55)
        centralPoint.setZ(centralPoint.getZ() + height * 0.75)
        startShot = self.camera.randomActorShot(
            self.invoker, self.battle, self.OPEN_SHOT_DUR, "suit", notRandom=True
        )
        nextShot = self.camera.focusShot(pos, 0.0, centralPoint)

        result = self.findTarget(toon.doId)
        dodged = not result.hpAdjust

        if not dodged:
            return Sequence(
                startShot,
                nextShot,
                Wait(0.4),
                LerpHprInterval(
                    camera, 0.6, hpr=(170.134, -2.53444, 0), blendType="easeInOut"
                ),
            )
        else:
            return Sequence(
                startShot,
                nextShot,
            )


@AttackClass(attackType=AttackEnum.PROTOON_SHAKE)
class ProToonShake(SuitSingleAttack):
    ANIM_NAME = "effort"
    CHEAT = True
    OPEN_SHOT_DUR = 4.5

    def doAttack(self):
        targetSuit = self.targetObjs[0]
        doSelfDamage = targetSuit.dna.name != "erfit"

        sfx = self.getSoundTrack(
            "phase_13/audio/sfx/april_toons/SA_protoon_shake.ogg",
            delay=0.5,
            node=self.invoker,
        )

        def updateSuitHP():
            if targetSuit:
                result = self.findTarget(targetSuit.doId)
                targetSuit.updateHealthBar(result.hpAdjust)
                targetSuit.showHpText(result.hpAdjust)
            if doSelfDamage:
                # don't hurt Erfit if he's healing himself!
                result = self.findTarget(self.invoker.doId)
                self.invoker.updateHealthBar(result.hpAdjust)
                self.invoker.showHpText(result.hpAdjust)

        toonTrack = Parallel()
        for toon in self.battle.activeToons:
            # Toon Reaction
            reactionTrack = Sequence()
            reactionTrack.append(
                Func(toon.headsUp, self.battle, self.invoker.getPos(self.battle))
            )
            reactionTrack.append(Wait(2.0))
            reactionTrack.append(ActorInterval(toon, "slip-forward", playRate=0.7))
            reactionTrack.append(Func(toon.loop, "neutral"))
            toonTrack.append(reactionTrack)

        healSfx = loader.loadSfx("phase_11/audio/sfx/LB_toonup.ogg")
        suitTrack = Sequence(
            Parallel(
                Func(
                    self.invoker.setChatAbsolute,
                    self.getAttackTaunt(),
                    CFSpeech | CFTimeout,
                ),
                Sequence(
                    ActorInterval(self.invoker, "quick-jump", duration=1.4),
                    Parallel(
                        ActorInterval(self.invoker, "slip-forward"),
                        Sequence(
                            Wait(0.6),
                            Func(updateSuitHP),
                            SoundInterval(healSfx, node=self.invoker),
                        ),
                    ),
                ),
            ),
            Func(self.invoker.loop, "neutral"),
            Func(self.invoker.clearChat),
        )

        return Parallel(suitTrack, toonTrack, sfx)

    def getAttackMovie(self):
        """
        Overwriting this animation.
        As Erfit deals self-damage in this track,
        if he defeats himself from it, we want the focus to be on it entirely.

        To do so, the camTrack now only cares about the part of the track BEFORE the death/revival track.
        """
        suitTrack = self.doAttack()
        toonHprTrack = Parallel()
        for t in self.targetDicts:
            toon = t["avatar"]
            toonHprTrack.append(
                Sequence(
                    Func(toon.headsUp, self.battle, MovieUtil.PNT3_ZERO),
                    Func(toon.loop, "neutral"),
                )
            )

        neutralIval = Func(self.invoker.loop, "neutral")
        suitTrack = Sequence(suitTrack, neutralIval, toonHprTrack)
        resetTrack = self.getResetTrack()
        endTrack = self.getEndTrack()
        resetSuitTrack = Sequence(resetTrack, suitTrack)
        camTrack = self.chooseCameraShot(resetSuitTrack.getDuration())
        resetSuitTrack = Sequence(Func(self.doConditionCallout), resetSuitTrack, endTrack)
        return resetSuitTrack, camTrack

    def getCameraShot(self, duration):
        return self.camera.heldRelativeShot(
            self.invoker, 0, 22, 7, 180, 1, 0, duration, "proToonShakeShot"
        )

    def getSoundTrack(self, filePath, delay=0.01, duration=None, node=None):
        soundEffect = loader.loadSfx(filePath)
        if duration:
            return Sequence(
                Wait(delay), SoundInterval(soundEffect, duration=duration, node=node)
            )
        else:
            return Sequence(Wait(delay), SoundInterval(soundEffect, node=node))


@AttackClass(attackType=AttackEnum.PERSONAL_TRAINER)
class PersonalTrainer(SuitSingleAttack):
    ANIM_NAME = "smile"
    CHEAT = True
    OPEN_SHOT_DUR = 7.0

    def doAttack(self):
        suitTrack = self.getSuitAnimTrack()
        result = self.findTarget(self.invoker.doId)
        damageDealt = result.hpAdjust

        sfx = self.getSoundTrack(
            "phase_13/audio/sfx/april_toons/SA_personal_trainer.ogg",
            delay=0.8,
            node=self.invoker,
        )
        col = base.getBackgroundColor()

        darkenTime = 3.0
        lightenTime = 1.0
        darkenColor = (1.0, 1.0, 1.0, 0.5)
        normalColor = (1.0, 1.0, 1.0, 1.0)

        def checkBackgroundColor():
            if not self.invoker.getVisualEffectOfId(VisualEffectEnum.ERFIT_REVIVE):
                base.setBackgroundColor(1, 1, 1)

        darkenTrack = Sequence(
            Func(self.invoker.wrtReparentTo, render),
            Func(checkBackgroundColor),
            Wait(0.25),
            Parallel(
                LerpColorScaleInterval(
                    self.battle, darkenTime, darkenColor, blendType="easeIn"
                ),
                LerpColorScaleInterval(
                    base.bossGeom, darkenTime, darkenColor, blendType="easeIn"
                ),
            ),
            Wait(1.0),
            Parallel(
                LerpColorScaleInterval(
                    self.battle, lightenTime, normalColor, blendType="easeOut"
                ),
                LerpColorScaleInterval(
                    base.bossGeom, lightenTime, normalColor, blendType="easeOut"
                ),
            ),
            Func(self.invoker.wrtReparentTo, self.battle),
            Func(base.setBackgroundColor, col),
        )

        flashRed = Sequence(
            LerpColorScaleInterval(
                self.invoker, 0.2, colorScale=VBase4(1, 0.2, 0.2, 1)
            ),
            LerpColorScaleInterval(self.invoker, 0.6, colorScale=VBase4(1, 1, 1, 1)),
        )
        redTrack = Sequence(
            Wait(0.8),
            flashRed,
            Wait(0.5),
            flashRed,
            Func(self.updateSuitHP, self.invoker, damageDealt),
            Wait(0.5),
            flashRed,
            Wait(0.5),
        )

        suitTrack = Sequence(suitTrack, Func(self.invoker.loop, "neutral"))
        return Parallel(suitTrack, darkenTrack, redTrack, sfx)

    def getAttackMovie(self):
        """
        Overwriting this animation.
        As Erfit deals self-damage in this track,
        if he defeats himself from it, we want the focus to be on it entirely.

        To do so, the camTrack now only cares about the part of the track BEFORE the death/revival track.
        """
        suitTrack = self.doAttack()
        toonHprTrack = Parallel()
        for t in self.targetDicts:
            toon = t["avatar"]
            toonHprTrack.append(
                Sequence(
                    Func(toon.headsUp, self.battle, MovieUtil.PNT3_ZERO),
                    Func(toon.loop, "neutral"),
                )
            )

        neutralIval = Func(self.invoker.loop, "neutral")
        suitTrack = Sequence(suitTrack, neutralIval, toonHprTrack)
        resetTrack = self.getResetTrack()
        endTrack = self.getEndTrack()
        resetSuitTrack = Sequence(resetTrack, suitTrack)
        camTrack = self.chooseCameraShot(resetSuitTrack.getDuration())
        resetSuitTrack = Sequence(Func(self.doConditionCallout), resetSuitTrack, endTrack)
        return resetSuitTrack, camTrack

    def getSoundTrack(self, filePath, delay=0.01, duration=None, node=None):
        soundEffect = loader.loadSfx(filePath)
        if duration:
            return Sequence(
                Wait(delay), SoundInterval(soundEffect, duration=duration, node=node)
            )
        else:
            return Sequence(Wait(delay), SoundInterval(soundEffect, node=node))


@AttackClass(attackType=AttackEnum.GAINS_FROM_THE_SCRAP)
class GainsFromTheScrap(SuitSingleAttack):
    ANIM_NAME = "quick-jump"
    CHEAT = True
    OPEN_SHOT_DUR = 5.0

    def doAttack(self):
        chosenSuit = self.battle.activeSuits[self.extraArgs[0]]
        suitTrack = self.getSuitAnimTrack()
        soundTrack = self.getSoundTrack(
            "phase_13/audio/sfx/april_toons/SA_gains_from_the_scrap.ogg",
            delay=0.0,
            node=self.invoker,
        )
        trapProp = BattleProps.globalPropPool.getProp("quicksand")
        trapProp.setColor(Vec4(0.1, 1.0, 0.1, 1))
        trapProp.setHpr(Point3(300, 0, 0))
        trapProp.setScale(0.01)

        healSfx = loader.loadSfx("phase_11/audio/sfx/LB_toonup.ogg")

        def updateSuitHP(suit, hp, response=False):
            suit.updateHealthBar(hp)
            suit.showHpText(hp)
            if response:
                chosenResponse = random.choice(
                    TTLocalizer.CountErfitCogSacrificeResponses
                )
                suit.setChatAbsolute(chosenResponse, CFSpeech | CFTimeout)

        smallScale = 0.01
        bigScale = 2.25
        biggerScale = 2.5
        trapTrack = Sequence(
            Wait(0.1),
            LerpScaleInterval(trapProp, 0.65, biggerScale, blendType="easeIn"),
            LerpScaleInterval(trapProp, 0.15, bigScale, blendType="easeOut"),
            Wait(1.5),
            LerpScaleInterval(trapProp, 0.15, biggerScale, blendType="easeIn"),
            LerpScaleInterval(trapProp, 0.65, smallScale, blendType="easeOut"),
            Func(trapProp.removeNode),
        )

        def setupHole():
            suitPos = chosenSuit.getPos(render)
            trapProp.setPos(suitPos)
            trapProp.reparentTo(render)

        moveTrack = Sequence(
            Func(setupHole),
            Wait(0.9),
            LerpPosInterval(chosenSuit, 0.9, (0, 0, -1.65), other=trapProp),
            LerpPosInterval(chosenSuit, 0.4, (0, 0, -5.2), other=trapProp),
            Func(chosenSuit.wrtReparentTo, hidden),
        )

        animTrack = Sequence(
            ActorInterval(chosenSuit, "flail"),
            ActorInterval(chosenSuit, "flail", startTime=1.1),
        )

        animTrack.append(
            Sequence(Wait(0.7), ActorInterval(chosenSuit, "slip-forward", duration=2.1))
        )

        fallingSoundTrack = Sequence(
            Wait(0.7),
            SoundInterval(
                globalBattleSoundCache.getSound("TL_quicksand.ogg"), node=chosenSuit
            ),
            Wait(0.1),
        )

        suitFallTrack = Sequence(
            Wait(1.2), Parallel(trapTrack, moveTrack, animTrack, fallingSoundTrack)
        )

        result = self.findTarget(chosenSuit.doId)

        suitTalkTrack = Sequence(
            Wait(2.4),
            Func(updateSuitHP, chosenSuit, result.hpAdjust, True),
            Func(base.playSfx, healSfx),
        )

        for target in self.targetObjs:
            if target.doId == chosenSuit.doId:
                continue
            result = self.findTarget(target.doId)
            if result.hpAdjust:
                suitTalkTrack.append(
                    Func(updateSuitHP, target, result.hpAdjust, False)
                )

        hpTextInfo = TTLocalizer.GeneralAttackHpTexts[TTLocalizer.HP_TEXT_RIPPED]
        hpTextString, hpTextColor = hpTextInfo
        rippedTextSeq = Sequence(
            Func(self.invoker.hideHpText),
            Func(self.invoker.showHpString, hpTextString, 0.85, 0.7, hpTextColor),
        )

        suitTalkTrack.append(
            Sequence(
                Wait(1.0),
                rippedTextSeq,
                Wait(1.5),
                Func(chosenSuit.clearChat),
            )
        )

        return Parallel(suitTrack, suitFallTrack, suitTalkTrack, soundTrack)

    def getSuitDeathMovie(self, suit):
        return Sequence()

    def getCameraShot(self, duration):
        return self.camera.heldShot(9, -11, 13, 25, -16, 0, duration, "gfts-Shot")

    def getSoundTrack(self, filePath, delay=0.01, duration=None, node=None):
        soundEffect = loader.loadSfx(filePath)
        if duration:
            return Sequence(
                Wait(delay), SoundInterval(soundEffect, duration=duration, node=node)
            )
        else:
            return Sequence(Wait(delay), SoundInterval(soundEffect, node=node))


@AttackClass(attackType=AttackEnum.HYDRATION_COMEBACK)
class HydrationComeback(Attack):
    CHEAT = True
    OPEN_SHOT_DUR = 1.7

    def doAttack(self):
        target = self.targetDicts[0]
        toon = target['avatar']

        # The unite enable track.
        uniteEnableTrack = Sequence()
        if toon.isLocal():
            uniteEnableTrack = Sequence(
                Func(self.battle.removeUniteDisabledFlag, 'hydration-check-no-unites'),
                Func(toon.requestRemoveUniteImmunityFlag, 1),
            )

        pos, hpr = self.battle.getActorPosHpr(toon)
        pos = pos + self.battle.getPos()
        startPos = pos + Point3(0, 0, 100)
        cannonSfx = base.loader.loadSfx('phase_4/audio/sfx/MG_cannon_whizz_fast.ogg')
        result = self.findTarget(toon.doId)
        fallbackTrack = Parallel(
            SoundInterval(cannonSfx, volume=1.0, node=toon),
            Sequence(
                Func(toon.show),
                Func(toon.doEmote, 12),
                Func(toon.setHpr, hpr),
                Parallel(
                    LerpPosInterval(toon, 0.9, startPos=startPos, pos=pos),
                    LerpColorScaleInterval(toon.dropShadow, 0.9, toon.dropShadow.getColorScale(),
                                           startColorScale=(0, 0, 0, 0)),
                ),
                uniteEnableTrack,
                Func(toon.takeDamage, -result.hpAdjust),
                Wait(1.6),
            )
        )
        return fallbackTrack

    def getCameraShot(self, duration):
        return self.camera.heldShot(0, 5, 6, 180, -16, 0, duration, 'heldShot')


@AttackClass(attackType=AttackEnum.ERFIT_REVIVE)
class ErfitRevive(Attack):
    CHEAT = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.suitsToRectifyIMeanFlexifyAkaKill = []
        self.erfitSet = False

    def placeAliveSuits(self):
        aliveCogs = self.stillAliveCogs
        for suit in aliveCogs:
            pos, hpr = self.battle.getActorPosHpr(suit, aliveCogs)
            suit.setPosHpr(self.battle, pos, hpr)

    def runFadeSequence(self):
        delay = 0.1
        fadeOutTime = 0.6
        fadePauseTime = 0.8
        fadeInTime = 0.6
        Sequence(
            Wait(delay),
            Parallel(
                LerpColorScaleInterval(render, fadeOutTime, (0, 0, 0, 1)),
                LerpColorScaleInterval(render2d, fadeOutTime, (0, 0, 0, 1)),
            ),
            Wait(fadePauseTime),
            Parallel(
                LerpColorScaleInterval(render, fadeInTime, (1, 1, 1, 1)),
                LerpColorScaleInterval(render2d, fadeInTime, (1, 1, 1, 1)),
            ),
        ).start()

    def getCameraShot(self, duration):
        stallDuration = 1.5
        freezeDuration = 0.0  # 4.1
        return Parallel(
            Sequence(
                Func(base.camera.setPosHpr, self.erfit, 0, 22, 12, 180, -18, 0),
                Wait(stallDuration),
                Func(self.startCameraSpinTask),
                Wait(duration - stallDuration - freezeDuration),
                Func(self.endCameraSpinTask),
                # Func(base.camera.setPosHpr, self.erfit, 0, 22 * 0.8, 12 * 0.8, 180, -18, 0),
                Wait(freezeDuration),
            ),
            Sequence(
                Wait(17.25),
                Func(self.runFadeSequence),
            )
        )

    def startCameraSpinTask(self):
        taskMgr.add(self.cameraSpinTask, 'cameraSpinTask')

    def endCameraSpinTask(self):
        taskMgr.remove('cameraSpinTask')

    def cameraSpinTask(self, task = None):
        taskTime = task.time
        if round(taskTime * 100) % 2:
            return task.cont

        # Get the center position.
        x, y, *_ = CountErclaimBattleAPosHpr

        # Move the Z up.
        z = 10

        # Get X and Y offsets.
        startRadians = math.pi / 2
        spinSpeed = 1 / 5.5
        radius = 19
        xOffset = math.sin((taskTime * spinSpeed) + startRadians) * radius
        yOffset = math.cos((taskTime * spinSpeed) + startRadians) * radius

        # Get heading for camera.
        heading = (-math.degrees((taskTime * spinSpeed) + startRadians) + 180) % 360

        # Set camera pos.
        camera.setPosHpr(x + xOffset, -y + yOffset, z, heading, -12, 0)

        # Set erfit, if we need to.
        if not self.erfitSet:
            self.placeAliveSuits()
            self.erfitSet = True

        return task.cont

    @property
    def erfit(self):
        for target in self.targetObjs:
            if self.isSuit(target) and target.dna.name == 'erfit':
                return target

    @property
    def nonErfitCogs(self):
        retList = []
        for target in self.targetObjs:
            if self.isSuit(target) and target.dna.name != 'erfit':
                retList.append(av)
        return retList

    @property
    def stillAliveCogs(self):
        retList = []
        for target in self.targetObjs:
            if self.isSuit(target):
                if target in self.suitsToRectifyIMeanFlexifyAkaKill:
                    continue
                if target.getHp() > 0:
                    retList.append(target)
        return retList

    @property
    def erfitVisualEffect(self) -> ErfitReviveVisualEffect:
        return ErfitReviveVisualEffect(
            avProfile=self.erfit,
            effectEnum=VisualEffectEnum.ERFIT_REVIVE,
            extraArgs=[]
        )

    # def getCameraShot(self, duration):
    #     return Parallel(
    #         Sequence(
    #             Func(base.camera.setPosHpr, self.erfit, 0, 22, 12, 180, -18, 0)
    #         ),
    #         Wait(duration),
    #     )

    def doAttack(self):
        toonHurtTrack = Parallel()
        suitHurtTrack = Parallel(Func(self.killSuits))
        for target in self.targetObjs:
            # if self.battle.findToon(target) and target in self.hps:
            #     toonHurtTrack.append(self.buildToonDamageTrack(target))
            result = self.findTarget(target.doId)
            if self.isSuit(target) and result.hpAdjust:
                suitHurtTrack.append(self.buildSuitDamageTrack(target, result.hpAdjust))

        applyMovie, _ = self.erfitVisualEffect.getApplyMovie()

        return Parallel(
            applyMovie,
            Sequence(Parallel(toonHurtTrack, suitHurtTrack)),
            self.getMonologue(),
            self.getSpeedTrack(),
            self.getBossRoomFadeTrack(),
            Func(base.instance.activateSky),
        )

    def getMonologue(self):
        suit = self.erfit
        swoleDialog = TTLocalizer.ErfitSwoleTransition

        startTalkTime = 1.5
        msgTime = 4.0
        endDelay = 2

        return Track(
            (0.0, Func(suit.setHp, suit.getMaxHp())),
            (startTalkTime, Parallel(Func(suit.setChatAbsolute, swoleDialog[0], CFSpeech))),
            (startTalkTime + (msgTime * 1), Func(suit.setChatAbsolute, swoleDialog[1], CFSpeech)),
            (startTalkTime + (msgTime * 2), Func(suit.setChatAbsolute, swoleDialog[2], CFSpeech)),
            (startTalkTime + (msgTime * 3) - 1, Parallel(ActorInterval(suit, 'smile', duration=3.9),
                                                         Func(suit.showHpString,
                                                              text=TTLocalizer.SuitAttackDmgMult % '1.40',
                                                              color=(0.45, 0.45, 1.0, 1.0)))),
            (startTalkTime + (msgTime * 3), Func(suit.setChatAbsolute, swoleDialog[3], CFSpeech)),
            (startTalkTime + (msgTime * 3) - 1 + 3.95, Func(suit.neutralAvatar)),
            (startTalkTime + (msgTime * 3) - 1 + 3.95 + endDelay, Func(suit.clearChat)),
        )

    # def buildToonDamageTrack(self, target):
    #     """An individual track played per Toon"""
    #     toon = self.battle.findToon(target)
    #     return self.getToonTrack(damageDelay=0.0, damageAnimNames=['slip-forward'],
    #                              dodgeAnimNames=['neutral'],
    #                              target=self.getTargetDictFromAvatar(toon))

    def buildSuitDamageTrack(self, suit, damageHP):
        """An individual track played per Suit"""
        # if suit in self.battle.joiningSuits + self.battle.pendingSuits:
        #     return Sequence()

        def loopNeutralAnim():
            loopAnim = 'lured' if suit.isLured else 'neutral'
            suit.loop(loopAnim)

        hp = suit.getHp() + damageHP

        if hp > 0:
            return Parallel(
                Sequence(
                    Func(self.updateSuitHP, suit, damageHP),
                    ActorInterval(suit, 'pie-small-react'),
                    Func(loopNeutralAnim)
                )
            )
        else:
            self.getSuitDeathMovie(suit)
            return Sequence()  # they will be murdered

    def getEndTrack(self):
        """overwrite default death anim"""
        deathReviveTracks = Parallel()
        for target in self.targetObjs:
            result = self.findTarget(target.doId)
            if self.isSuit(target) and result.revived:
                deathReviveTracks.append(self.getSuitReviveMovie(target))
        return Sequence(deathReviveTracks)

    def getSuitDeathMovie(self, chosenSuit):
        self.suitsToRectifyIMeanFlexifyAkaKill.append(chosenSuit)

    def killSuits(self):
        for suit in self.suitsToRectifyIMeanFlexifyAkaKill:
            if not suit:
                continue
            if suit.getHp() <= 0:
                continue
            seq = MovieUtil.createSuitDeathTrack(suit, None, self.battle, affectToons=False)
            seq.start()
            seq.setT(5.3)

    def getSpeedTrack(self) -> Sequence:
        return Sequence(
            Func(base.musicMgr.playMusic, 'erfit_supreme', looping=1, volume=1)
        )
        # if self.bml.storedMusic is None:
        #     self.bml.lookForSuits(self.battle.suits, None)
        #
        # def killStoredMusic():
        #     # need to kill the stored music or it'll stop the end cutscene music
        #     self.bml.storedMusic = None
        #
        # return Sequence(
        #     Func(self.bml.changePlaybackSpeed, 1.1, duration=1.0),
        #     Wait(5.0),
        #     Func(killStoredMusic),
        # )

    @property
    def bml(self):
        return self.battle.battleMusicListener

    @property
    def currentPlaybackSpeed(self):
        return self.bml.currentPlayback

    def getBossRoomFadeTrack(self):
        fadeDuration = 1.5

        fadeParts = base.bossGeom.getChild(0).getChildren()
        partsToRemove = (base.bossGeom.find('**/rug'),
                         base.bossGeom.find('**/elevator_origin'),
                         base.bossGeom.find('**/decor_1'),
                         base.bossGeom.find('**/collisions'))
        for removePart in partsToRemove:
            if removePart and removePart in fadeParts:
                fadeParts.removePath(removePart)

        fadeParallel = Parallel()
        fadeParallel.append(Func(base.bossGeom.find('**/skylight').hide))
        for part in fadeParts:
            partPos = part.getPos()
            partPos[2] -= 40
            fadeParallel.append(Parallel(
                LerpColorScaleInterval(part, fadeDuration, (0, 0, 0, 0), blendType='easeOut'),
                LerpPosInterval(part, fadeDuration, partPos, blendType='easeOut')
            ))
        return fadeParallel


# region FTF / OCFTF

@AttackClass(attackType=AttackEnum.FTF_PRESIDENT_MULLIGAN)
class FtfPresidentMulligan(TeeOff):
    CHEAT = True
    OPEN_SHOT_DUR = 2.25
    PLAY_RATE = 2.0
    HitDelay = 3.5
    ToonHitDelay = 4.35
    ToonDodgeDelay = 1.4
    ToonHitAnim = 'slip-backward'


@AttackClass(attackType=AttackEnum.FTF_FOREMAN_REDTAPE)
class FTFForemanRedTape(SuitSingleAttack):
    ANIM_NAME = "throw-object"
    OPEN_SHOT_DUR = 3.5

    def doAttack(self):
        suitTrack = self.getSuitAnimTrack()
        globalParallel = Parallel()
        soundTrack = self.getSoundTrack("SA_red_tape.ogg", delay=2.9, node=self.invoker)

        for target in self.targetDicts:
            toon = target["avatar"]
            dmg = target["hp"]
            tape = globalPropPool.getProp("redtape")
            tubes = [globalPropPool.getProp("redtape-tube")]

            tapePosPoints = [Point3(-0.24, 0.09, -0.38), VBase3(-1.152, 86.581, -76.784)]
            tapeScaleUpPoint = Point3(0.9, 0.9, 0.24)
            propTrack = Sequence(
                self.getPropAppearTrack(
                    tape,
                    self.invoker.getRightHand(),
                    tapePosPoints,
                    0.8,
                    tapeScaleUpPoint,
                    scaleUpTime=0.5,
                )
            )
            propTrack.append(Wait(1.73))
            hitPoint = lambda toon=toon: self.toonTorsoPoint(toon)
            propTrack.append(
                self.getPropThrowTrack(tape, [hitPoint], [self.toonGroundPoint(toon, 0.7)])
            )
            hips = toon.getHipsParts()
            animal = toon.style.getAnimal()
            scale = ToontownGlobals.toonBodyScales[animal]
            legs = toon.style.legs
            torso = toon.style.torso
            torso = torso[0]
            animal = animal[0]
            tubeHeight = -0.8
            if torso == "s":
                scaleUpPoint = Point3(scale * 2.03, scale * 2.03, scale * 0.7975)
            elif torso == "m":
                scaleUpPoint = Point3(scale * 2.03, scale * 2.03, scale * 0.7975)
            elif torso == "l":
                scaleUpPoint = Point3(scale * 2.03, scale * 2.03, scale * 1.11)
            if animal == "h" or animal == "d":
                tubeHeight = -0.87
                scaleUpPoint = Point3(scale * 1.69, scale * 1.69, scale * 0.67)
            tubePosPoints = [Point3(0, 0, tubeHeight), MovieUtil.PNT3_ZERO]
            tubeTracks = Parallel()
            tubeTracks.append(Func(self.battle.movie.needRestoreHips))
            for partNum, nextPart in enumerate(hips):
                tubeTracks.append(
                    self.getPropTrack(
                        tubes[partNum],
                        nextPart,
                        tubePosPoints,
                        3.25,
                        3.17,
                        scaleUpPoint=scaleUpPoint,
                    )
                )

            tubeTracks.append(Func(self.battle.movie.clearRestoreHips))
            toonTrack = self.getToonTrack(3.4, ["struggle"], 2.8, ["jump"], target=target, hpTextType=TTLocalizer.HP_TEXT_2_REWARD_CD)
            if dmg < 0:
                visualEffectTrack = Sequence(
                    Wait(3.4),
                    Func(MovieUtil.applyVisualEffect, toon, VisualEffectEnum.UNITE_COOLDOWN)
                )
                globalParallel.append(Parallel(toonTrack, propTrack, tubeTracks, visualEffectTrack))
            else:
                globalParallel.append(Parallel(toonTrack, propTrack))

        return Parallel(globalParallel, suitTrack, soundTrack)


@AttackClass(attackType=(AttackEnum.FTF_FOREMAN_SNIPE, AttackEnum.FTF_PRESIDENT_SNIPE))
class FTFForemanSnipe(SuitGroupAttack):
    ANIM_NAME = "glower"
    CHEAT = True
    OPEN_SHOT_DUR = 1.2
    DefaultPoints = (
        [Point3(0.1, 5.2, 6.0), MovieUtil.PNT3_ZERO],
        [Point3(-0.5, 5.2, 6.0), MovieUtil.PNT3_ZERO],
    )

    def doAttack(self):
        leftPosPoints, rightPosPoints = self.DefaultPoints

        suitTrack = self.getSuitAnimTrack()
        soundTrack = self.getSoundTrack("SA_glower_power.ogg", delay=1.1, node=self.invoker)
        globalParallel = Parallel()

        for target in self.targetDicts:
            leftKnives = []
            rightKnives = []
            for i in range(0, 3):
                leftKnives.append(globalPropPool.getProp("dagger"))
                rightKnives.append(globalPropPool.getProp("dagger"))

            leftKnifeTracks = Parallel()
            rightKnifeTracks = Parallel()
            for i in range(0, 3):
                knifeDelay = 0.11
                leftTrack = Sequence()
                leftTrack.append(Wait(1.1))
                leftTrack.append(Wait(i * knifeDelay))
                leftTrack.append(
                    self.getPropAppearTrack(
                        leftKnives[i],
                        self.invoker,
                        leftPosPoints,
                        1e-06,
                        Point3(0.4, 0.4, 0.4),
                        scaleUpTime=0.1,
                    )
                )
                leftTrack.append(
                    self.getPropThrowTrack(
                        leftKnives[i],
                        hitPointNames=["face"],
                        missPointNames=["miss"],
                        hitDuration=0.3,
                        missDuration=0.3,
                        target=target,
                    )
                )
                leftKnifeTracks.append(leftTrack)
                rightTrack = Sequence()
                rightTrack.append(Wait(1.1))
                rightTrack.append(Wait(i * knifeDelay))
                rightTrack.append(
                    self.getPropAppearTrack(
                        rightKnives[i],
                        self.invoker,
                        rightPosPoints,
                        1e-06,
                        Point3(0.4, 0.4, 0.4),
                        scaleUpTime=0.1,
                    )
                )
                rightTrack.append(
                    self.getPropThrowTrack(
                        rightKnives[i],
                        hitPointNames=["face"],
                        missPointNames=["miss"],
                        hitDuration=0.3,
                        missDuration=0.3,
                        target=target,
                    )
                )
                rightKnifeTracks.append(rightTrack)

            damageAnims = [["slip-backward", 0.01, 0.35]]
            toonTrack = self.getToonTrack(
                damageDelay=1.6,
                splicedDamageAnims=damageAnims,
                dodgeDelay=0.7,
                dodgeAnimNames=["sidestep"],
                target=target,
                hpTextType=TTLocalizer.HP_TEXT_SNIPED,
            )
            toon = target["avatar"]
            deathSound = base.loader.loadSfx('phase_3.5/audio/sfx/ENC_cogfall_apart.ogg')
            explosionTrack = Sequence(
                Wait(1.6),
                Parallel(
                    SoundInterval(deathSound, node=self.invoker),
                    createKapowExplosionTrack(self.battle, explosionPoint=toon.getPos(self.battle), scale=3.5),
                ),
                Wait(2.0),
            )

            globalParallel.append(Parallel(toonTrack, leftKnifeTracks, rightKnifeTracks, explosionTrack))

        return Parallel(suitTrack, soundTrack, globalParallel)

    def getCameraShot(self, duration):
        if len(self.targetObjs) == 1:
            return SuitSingleAttack.getCameraShot(self, duration)
        else:
            return SuitGroupAttack.getCameraShot(self, duration)


@AttackClass(attackType=AttackEnum.FTF_ATTORNEY_PICK_UP_THE_PACE)
class FTFAttorneyPickUpThePace(PickUpThePace):
    def doAttack(self):
        attackTrack = super().doAttack()
        finalTrack = Parallel(
            attackTrack,
            Sequence(
                Wait(1.0),
                Func(MovieUtil.applyVisualEffect, self.invoker, VisualEffectEnum.FTF_ATTORNEY_JOGGING)
            )
        )
        return finalTrack


@AttackClass(attackType=AttackEnum.FTF_NUCLEAR_TRANSFORMATION)
class FTFNuclearTransformation(Attack):
    ALLOW_GROUPING = True
    CHEAT = True

    @property
    def specialContainerId(self):
        return self.extraArgs[0]

    @property
    def maxHealth(self):
        return self.extraArgs[1]

    @property
    def newHealth(self):
        return self.extraArgs[2]

    def doAttack(self):
        if not self.targetObjs:
            return Sequence()

        target = self.targetObjs[0]
        # Need to clear this out whenever they transform
        setattr(target, 'movieFrozen', False)

        def loopNeutralAnim():
            loopAnim = "lured" if target.isLured else "neutral"
            target.loop(loopAnim)

        def updateDNA():
            currentAnim = target.getCurrentAnim()

            # Copied from Suit.delete()
            # region
            if target.leftHand:
                target.leftHand.removeNode()
                target.leftHand = None

            if target.rightHand:
                target.rightHand.removeNode()
                target.rightHand = None

            if target.shadowJoint:
                target.shadowJoint.removeNode()
                target.shadowJoint = None

            if target.nametagJoint:
                target.nametagJoint.removeNode()
                target.nametagJoint = None

            # grab the drop shadow
            dropShadow = target.dropShadow
            if not dropShadow.isEmpty():
                dropShadow.reparentTo(hidden)

            # remove the old geometry
            target.removePart('modelRoot')

            from direct.actor.Actor import Actor
            for part in target.headParts:
                if isinstance(part, Actor):
                    part.cleanup()
                    part.delete()
                else:
                    part.removeNode()

            target.headParts = []
            target.removeHealthBar()
            if target.specialHead:
                target.specialHead.cleanup()
                target.specialHead.destroy()
                del target.specialHead

            # Unload their animations
            target.unloadAnims(target.generateAnimDict(skeleton=target.isSkelecog))

            # endregion

            target.setSpecialContainerId(self.specialContainerId)

            # Set the new DNA.
            from toontown.suit.SuitDNA import SuitDNA
            from toontown.suit import SuitHealthMeter
            dna = SuitDNA()
            dna.newSuit(target.specialContainer.suitType)
            target.dna = dna
            target.setStyle(dna)

            # Regenerate the suit.
            target.generateSuit()
            target.initializeDropShadow()
            target.initializeNametag3d()
            target.setElite(1)
            target.makeSkeleton(elite=True)
            attributes = SuitBattleGlobals.SuitAttributes[target.dna.name]
            target.setLevel(target.specialContainer.suitLevel - attributes['level'] - 1)
            target.setMaxHp(self.maxHealth)
            target.setHp(self.newHealth)
            target.healthBar.updateMeterMode(SuitHealthMeter.MODE_BATTLE)
            target.healthBar.updateHealthBar(forceUpdate=1)

            target.overrideDisplayName(target.specialContainer.suitName)

        deathSound = base.loader.loadSfx('phase_3.5/audio/sfx/ENC_cogfall_apart.ogg')
        targetPos, _ = self.battle.getActiveSuitPosHpr(target)
        explodePoint = self.battle.attachNewNode('foo')
        explodePoint.setPos(self.battle, targetPos)
        explodePoint.setY(explodePoint.getY() - 2)
        explodePoint.setZ(explodePoint.getZ() + 2)
        explosionTrack = Sequence(
            Parallel(
                IsolatedSoundInterval(deathSound, node=self.invoker),
                createKapowExplosionTrack(self.battle, explosionPoint=explodePoint.getPos(self.battle), scale=6.0),
            ),
            Wait(2.0),
            Func(explodePoint.removeNode),
        )

        slipForwardIval = Sequence()

        def startSlipForwardIval():
            target.stopHeadFreakout()
            nonlocal slipForwardIval
            slipForwardIval = Sequence(
                ActorInterval(target, 'slip-forward', startTime=2.43/target.timescale, playRate=target.timescale),
                Func(loopNeutralAnim),
                Func(target.startHeadFreakout)
            )
            slipForwardIval.start()

        targetTrack = Sequence(
            # Could not find a better place to get rid of this
            Func(MovieUtil.unapplyVisualEffect, target, VisualEffectEnum.FTF_ATTORNEY_JOGGING),
            Func(updateDNA),
            Func(self.battle.adjustFTFMusic),
            Parallel(
                explosionTrack,
                Func(target.showHpString, "TRANSFORM!", 0.85, 0.7, (0, 1, 0, 1)),
                Func(startSlipForwardIval),
            ),
            Func(slipForwardIval.finish),
        )

        return Parallel(Sequence(Wait(1), targetTrack))

    def getCameraShot(self, duration):
        return self.camera.heldShot(0, -17, 13, 0, -20, 0, duration, "nuclearTransformOverheadShot")


@AttackClass(attackType=AttackEnum.FTF_SUPERVISOR_ABACUS_SYNERGY)
class FTFSupervisorAbacusSynergy(Synergy):
    CHEAT = True


@AttackClass(attackType=AttackEnum.FTF_PRESIDENT_DRIVER)
class FTFPresidentAncientDriver(TeeOff):
    HP_TEXT_TYPE = TTLocalizer.HP_TEXT_25_DAMAGE_DOWN


@AttackClass(attackType=AttackEnum.OVERCLOCKED_FOREMAN_DESTRUCTION)
class FTFForemanDestruction(Attack):
    """
    Battle movie for when an Overclocked Foreman with the 'Destruction'
    compensation gets Destroyed Epic Style.
    Also reused for explosive foreman in FTF 2023
    """
    CHEAT = True
    OPEN_SHOT_DUR = 4.01

    def getAttackTaunt(self):
        return "My people need me."

    def doAttack(self):
        # find the suit
        if not self.targetObjs:
            return

        suit = self.invoker

        # build the dialogue
        dialogue = self.getAttackTaunt()
        deathSound = base.loader.loadSfx('phase_3.5/audio/sfx/ENC_cogfall_apart.ogg')

        globalTrack = Parallel()
        globalTrack.append(Track(
            (0.0, MovieUtil.createSuitUnlureTrack(suit, self.battle) if suit.isLured else Sequence()),
            (0.5, Sequence(
                Func(suit.setChatAbsolute, dialogue, CFSpeech)
            )),
            (3.0, Sequence(
                Func(suit.clearChat), Func(self.killSuits),
            )),
            (3.0, SoundInterval(deathSound, node=self.invoker)),
            (4.0, Wait(0.01)),
        ))

        hpTextInfo = TTLocalizer.GeneralAttackHpTexts[TTLocalizer.HP_TEXT_LURE_RESISTANCE]
        hpTextString = hpTextInfo[0]
        hpTextColor = hpTextInfo[1]

        suitReactTrack = Parallel()
        for target in self.targetDicts:
            avatar = target['avatar']
            if avatar is self.invoker:
                continue

            if avatar.isToon():
                suitReactTrack.append(Sequence(
                    self.getToonTrack(damageDelay=3.0 + lerp(0.0, 0.3, random.random()),
                                      damageAnimNames=["slip-backward"], target=target),
                ))
            else:
                newPos, newHpr = self.battle.getSuitBattlePosHpr(avatar, self.battle.activeSuits)
                suitReactTrack.append(Sequence(
                    Wait(3.0),
                    Parallel(
                        Sequence(
                            Func(self.updateSuitHP, avatar, target['hp']),
                            Wait(1.5),
                            Func(avatar.hideHpText),
                            Func(avatar.showHpString, hpTextString, 0.85, 0.7, hpTextColor),
                            Wait(1.0),
                        ),
                        Parallel(
                            Sequence(
                                ActorInterval(avatar, 'slip-backward', playRate=1.5),
                                MovieUtil.unlureSuit(avatar, self.battle),
                                Func(avatar.loop, 'neutral'),
                            ),
                        ),
                        LerpPosInterval(avatar, 0.5, newPos, other=self.battle),
                    ),
                ))

        globalTrack.append(suitReactTrack)
        return globalTrack

    def getCameraShot(self, duration):
        return self.camera.allGroupOverheadShot(duration=duration)

    def killSuits(self):
        seq = MovieUtil.createSuitDeathTrack(self.invoker, None, self.battle, affectToons=False)
        seq.start()
        seq.setT(5.5)
        explodePoint = self.battle.attachNewNode('foo')
        explodePoint.setPos(self.battle, self.invoker.getPos(self.battle))
        explodePoint.setY(explodePoint.getY() - 2)
        explodePoint.setZ(explodePoint.getZ() + 2)
        createKapowExplosionTrack(self.battle, explosionPoint=explodePoint.getPos(self.battle), scale=6.0).start()
        explodePoint.removeNode()

    def getSuitDeathMovie(self, suit):
        if suit is self.invoker:
            return Sequence()
        else:
            return super().getSuitDeathMovie(suit)


@AttackClass(attackType=AttackEnum.FTF_ATTORNEY_COURT_MANDATE_MONOLITH)
class FTFAttorneyCourtMandateMonolith(Objection):
    CHEAT = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gagTrack = self.extraArgs[0]
        self.gagTrack2 = self.extraArgs[1]

    def modifyTauntString(self, tauntStr):
        tauntStr = tauntStr % (TTLocalizer.BattleGlobalTracksUpper[self.gagTrack], TTLocalizer.BattleGlobalTracksUpper[self.gagTrack2])
        return tauntStr

    def getAttackDisplayName(self):
        return (
            TTLocalizer.SuitAttackNames[self.attackType][0],
            TTLocalizer.SuitAttackNames[self.attackType][1] % (TTLocalizer.BattleGlobalTracksUpper[self.gagTrack].upper(), TTLocalizer.BattleGlobalTracksUpper[self.gagTrack2].upper()),
        )


@AttackClass(attackType=AttackEnum.FTF_ATTORNEY_COURT_MANDATE_OMNIPOTENT)
class FTFAttorneyCourtMandateOmnipotent(Objection):
    CHEAT = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gagLevel = self.extraArgs[0]
        self.gagLevel2 = self.extraArgs[1]

    def modifyTauntString(self, tauntStr):
        tauntStr = tauntStr % self.getAdjustedGagLevels()
        return tauntStr

    def getAdjustedGagLevels(self):
        gagLevel1 = self.gagLevel + 1
        gagLevel2 = self.gagLevel2 + 1
        if gagLevel1 < gagLevel2:
            return gagLevel1, gagLevel2
        else:
            return gagLevel2, gagLevel1

    def getAttackDisplayName(self):
        return (
            TTLocalizer.SuitAttackNames[self.attackType][0],
            TTLocalizer.SuitAttackNames[self.attackType][1] % self.getAdjustedGagLevels(),
        )


@AttackClass(attackType=AttackEnum.FTF_PRESIDENT_SHATTER_DAMAGE)
class FTFPresidentShatterDamage(ShatterDamage):
    EXTRA_TEXT = TTLocalizer.HpTextSlushFunded

    def updateSuitHP(self, suit, damage):
        super().updateSuitHP(suit, damage)
        MovieUtil.applyVisualEffect(suit, VisualEffectEnum.SLUSH_FUND)


@AttackClass(attackType=AttackEnum.FTF_FOREMAN_CIGAR_SMOKE)
class FTFForemanCigarSmoke(CigarSmoke):
    def getToonTrack(self, *args, **kwargs):
        kwargs['hpTextType'] = TTLocalizer.HP_TEXT_FOREMAN_SMOKED
        toon = kwargs['target']['avatar']
        return Parallel(
            super().getToonTrack(*args, **kwargs),
            Sequence(
                Wait(self.getDamageDelay()),
                Func(MovieUtil.applyVisualEffect, toon, VisualEffectEnum.TRIAL_BY_FIRE)
            ),
        )

# endregion

# region High Roller

@AttackClass(attackType=AttackEnum.HIGHROLLER_LEVEL_DAMAGE)
class LevelDamage(Attack):
    ANIM_NAME = "snap"
    OPEN_SHOT_DUR = 2.25
    ALLOW_GROUPING = False

    def doAttack(self):
        hpTextTracks = Parallel()
        hpTextString = "%s" % self.extraArgs[0]
        hpTextColor = (1, 0, 0, 1.0)

        if len(self.targetObjs) == 0 or self.extraArgs[0] in [0, '0']:
            self.OPEN_SHOT_DUR = 0
            return Sequence()

        hroller = self.targetObjs[0]

        visualEffect = hroller.getVisualEffectOfId(VisualEffectEnum.HIGHROLLER_COMMERCIAL)
        if not visualEffect:
            return Sequence()

        self.fakeSuit = visualEffect.fakeSuit

        seq = Parallel(
            Func(self.fakeSuit.showHpString, hpTextString, 0.85, 1.0, hpTextColor),
            Sequence(
                ActorInterval(self.fakeSuit, "pie-small-react"),
                Func(self.fakeSuit.loop, "neutral"),
            )
        )

        hpTextTracks.append(seq)

        return Sequence(Parallel(Sequence(hpTextTracks), Wait(2.25)))

    def getCameraShot(self, duration):
        if not hasattr(self, "fakeSuit"):
            return Sequence()
        return self.camera.heldRelativeShot(self.fakeSuit, 0, 20, 20, 180, -30, 0, duration, 'singleAvatarShot')


@AttackClass(attackType=AttackEnum.FINISH_BETWEEN)
class FinishBetween(Attack):
    def doAttack(self):
        # We need to find the taunt for the actual attack before switching to the fake suit.
        attackTaunt = self.getAttackTaunt()

        visualEffect = self.invoker.getVisualEffectOfId(VisualEffectEnum.HIGHROLLER_COMMERCIAL)
        if visualEffect:
            cutsceneLoader = CutsceneLoader.createLoader(
                key=CutsceneKeyEnum.HighRoller_Commercial_End,
                instance=self.battle.instance,
                battle=self.battle,
                suits=self.battle.suits,
                hroller=self.invoker,
                visualEffect=visualEffect
            )
        else:
            return Sequence()

        targetTrack = Parallel()
        for target in self.battle.suits:
            if target != self.invoker and not getattr(target, 'deadOrAboutToBe', False):
                targetTrack.append(MovieUtil.suitDisintegrateTrack(target, self.battle))

        return Parallel(
            cutsceneLoader.buildCutscene(),
            Sequence(
                Wait(3.0),
                Func(
                    visualEffect.fakeSuit.setChatAbsolute,
                    attackTaunt,
                    CFSpeech | CFTimeout,
                ),
                Wait(0.5),
                targetTrack
            )
        )

    def getEndTrack(self):
        # Override this track in favor of the disintegrate track.
        return Sequence()


@AttackClass(attackType=AttackEnum.SPIN_WHEEL)
class SpinWheel(Attack):
    CHEAT = True

    def doAttack(self):

        visualEffect = self.invoker.getVisualEffectOfId(VisualEffectEnum.HIGHROLLER_COMMERCIAL)
        if visualEffect:
            hroller = visualEffect.fakeSuit
        else:
            hroller = self.invoker

        currentGame = self.extraArgs[0]

        wheel = self.battle.instance.getEnvironment().getWheel()

        from toontown.instances.HighRollerGlobals import HighRollerGameEnum
        gameToDestDict = {
            HighRollerGameEnum.TRIVIA: wheel.WheelDestination.TRIVIA,
            HighRollerGameEnum.PUZZLE: wheel.WheelDestination.PUZZLE,
            HighRollerGameEnum.SHUFFLE: wheel.WheelDestination.SHUFFLE,
        }

        # Start putting the movie together
        cutsceneLoader = CutsceneLoader.createLoader(
            key=CutsceneKeyEnum.HighRoller_RandomGame,
            hroller=hroller,
            battle=self.battle,
            toons=self.battle.activeToons,
            wheelDest=gameToDestDict[currentGame]
        )

        # Return the movie
        return Parallel(
            Sequence(cutsceneLoader.buildCutscene()),
            Sequence(
                Wait(2.1),

                Func(self.battle.setH, 90),
                Func(self.battle.beginMinigame),
            )
            )


@AttackClass(attackType=AttackEnum.RANDOM_GAME)
class RandomGame(AvatarSayPhraseAttack):
    ANIM_NAME = "snap"
    OPEN_SHOT_DUR = 4.1
    CHEAT = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.epicPhrase = TTLocalizer.HighRollerQuestions[self.extraArgs[0]][0]

    @property
    def phraseData(self):
        phraseData = [[self.epicPhrase], 4.0]
        return phraseData

    def doAttack(self):
        # Grab a phrase that will be consistent across all clients
        phraseIndex = self.avatar.doId % len(self.phraseData[0])
        phrase = self.phraseData[0][phraseIndex]
        phraseTime = self.phraseData[1]

        # We need to find the taunt for the actual attack before switching to the fake suit.
        attackTaunt = self.getAttackTaunt()

        # We have to switch to the fake suit in between picking the phrase and saying it.
        visualEffect = self.invoker.getVisualEffectOfId(VisualEffectEnum.HIGHROLLER_COMMERCIAL)
        if visualEffect:
            self.invoker = visualEffect.fakeSuit

        sayPhraseSeq = Sequence(
            Wait(0.25),
            Func(self.invoker.setChatAbsolute, phrase, CFSpeech | CFTimeout),
            Wait(phraseTime),
        )
        if self.ClearChat:
            sayPhraseSeq.append(Func(self.invoker.clearChat))

        phraseSequence = Sequence()
        from toontown.instances.HighRollerGlobals import HighRollerGameEnum
        if self.battle.instance.currentGame == HighRollerGameEnum.TRIVIA:
            musicCode = 'highroller_trivia'
            phraseSequence = sayPhraseSeq
        elif self.battle.instance.currentGame == HighRollerGameEnum.PUZZLE:
            musicCode = 'highroller_puzzle'
        elif self.battle.instance.currentGame == HighRollerGameEnum.SHUFFLE:
            musicCode = 'highroller_shuffle'

        crossfadeFunc = Func(base.musicMgr.crossfadeIntoMusic, musicCode, duration=1.0, matchTime=False)
        return Sequence(
            Func(
                self.invoker.setChatAbsolute,
                attackTaunt,
                CFSpeech | CFTimeout,
            ),
            Wait(3.0),
            crossfadeFunc,
            phraseSequence,
            Func(
                base.camLens.setMinFov,
                BattleGlobals.BattleCamDefaultFov / (4.0 / 3.0),
            ),
        )

    def getCameraShot(self, duration):
        return self.camera.heldRelativeShot(self.invoker, 0, 20, 20, 180, -30, 0, duration, 'singleAvatarShot')


@AttackClass(attackType=AttackEnum.RANDOM_GAME_FINISH)
class RandomGameFinish(SuitSingleAttack):
    ANIM_NAME = "snap"
    OPEN_SHOT_DUR = 4.1
    CHEAT = True

    def doAttack(self):

        targetTrack = Parallel()
        for target in self.targetObjs:
            if not getattr(target, 'deadOrAboutToBe', False):
                targetTrack.append(MovieUtil.suitDisintegrateTrack(target, self.battle))
        television = self.battle.instance.getEnvironment().getTV()
        soundTrack = self.getSoundTrack("phase_11/audio/sfx/SA_bash.ogg", node=self.invoker)
        return Parallel(
            Sequence(self.getSuitAnimTrack(wantDialog=False), targetTrack, television.despawnTV()),
            Sequence(Wait(0.2), soundTrack)
        )

    def getCameraShot(self, duration):
        return self.camera.allGroupOverheadShot(duration=duration)

    def getEndTrack(self):
        # Override this track in favor of the disintegrate track.
        return Sequence()


@AttackClass(attackType=AttackEnum.RANDOM_GAME_PUNISH)
class RandomGamePunish(Attack):
    OPEN_SHOT_DUR = 4.1
    CHEAT = True

    def doAttack(self):
        damageDelay = 7.2
        hr = None
        for suit in self.battle.activeSuits:
            if getattr(suit.dna, "name", "hroller"):
                hr = suit
                break
        if hr is None:
            return Sequence()

        cutsceneLoader = CutsceneLoader.createLoader(
            key=CutsceneKeyEnum.HighRoller_MinigameResults,
            toons=self.battle.activeToons,
            hroller=hr,
            instance=self.battle.instance,
            battle=self.battle,
            successfulToons=[toon for toon in self.battle.activeToons if toon not in self.targetObjs]
        )

        indicatorTrack = Sequence(Wait(damageDelay))
        for target in self.targetDicts:
            toon = target["avatar"]
            indicatorTrack.append(
                Func(self.doDamage, toon, target["hp"], target["died"])
            )

        soundTrack = self.getSoundTrack("phase_11/audio/sfx/LB_camera_shutter_2.ogg", node=self.invoker)
        return Sequence(
            Func(self.battle.setH, 0),
            Parallel(soundTrack, Func(self.battle.endMinigame)),
            Parallel(
                cutsceneLoader.buildCutscene(),
                Sequence(
                    Wait(2.0),
                    Func(base.musicMgr.crossfadeIntoMusic, 'highroller_stinger', duration=0, matchTime=False)
                ),
                indicatorTrack
            ),
            Parallel(Func(base.musicMgr.crossfadeIntoMusic, 'highroller_battle_2', duration=0.25, matchTime=False, volume=0.8)),
        )

    def getCameraShot(self, duration):
        return self.camera.allGroupLowerOverheadShot(duration=duration)


@AttackClass(attackType=AttackEnum.HIGHROLLER_COMMERCIAL)
class HighRollerCommercial(Attack):
    ANIM_NAME = "magic2"
    CHEAT = True
    OPEN_SHOT_DUR = 0.0

    def doAttack(self):
        # Build the cutscene.
        from toontown.suit import Suit, SuitDNA, SuitHealthMeter
        fakeSuit = Suit.Suit()
        suitDNA = SuitDNA.SuitDNA()
        suitDNA.newSuit('hroller')

        fakeSuit.setDNA(suitDNA)
        fakeSuit.loop('neutral')
        fakeSuit.addActive()
        fakeSuit.hide()
        fakeSuit.setPos(self.invoker.getPos(render))
        fakeSuit.setHpr(self.invoker.getHpr(render))
        fakeSuit.getActualLevel = lambda: self.invoker.getActualLevel()
        fakeSuit.getStyleDept = lambda: self.invoker.getStyleDept()
        fakeSuit.setDisplayName(self.invoker.nametag.getDisplayName())
        fakeSuit.setPickable(0)

        cutsceneLoader = CutsceneLoader.createLoader(
            key=CutsceneKeyEnum.HighRoller_Commercial_Start,
            instance=self.battle.instance,
            hroller=fakeSuit,
            battle=self.battle
        )
        track = cutsceneLoader.buildCutscene()

        # Return result.
        return Parallel(
            Sequence(
                Func(camera.wrtReparentTo, render),
                Func(self.invoker.hide),
                Func(fakeSuit.show),
                Func(fakeSuit.reparentTo, render),
                Wait(0.1),
                Func(fakeSuit.setChatAbsolute, self.getAttackTaunt(), CFSpeech | CFTimeout),
                Wait(3.0),
                track,
                Func(MovieUtil.applyVisualEffect, self.invoker, VisualEffectEnum.HIGHROLLER_COMMERCIAL),
                Func(camera.wrtReparentTo, self.battle),
            )
        )

    def getCameraShot(self, duration):
        # Handled by cutscene loader
        return Sequence(
            Wait(0.1),
            self.camera.heldRelativeShot(self.invoker, 0, -10, 40, 180, -20, 0, 3.0, 'singleAvatarShot'),
            Wait(duration - 3.1)
        )


@AttackClass(attackType=AttackEnum.TRICK_OF_THE_LIGHT)
class TrickOfTheLight(Attack):
    ANIM_NAME = "snap"
    OPEN_SHOT_DUR = 4.1
    CHEAT = True

    def doAttack(self):
        applyMovie, _ = MovieUtil.applyVisualEffect(self.invoker, VisualEffectEnum.HR_UNTOUCHABLE, useMovieApply=True)
        visualEffect = self.invoker.getVisualEffectOfId(VisualEffectEnum.HR_UNTOUCHABLE)
        if visualEffect:
            # Visual effect, cease!
            visualEffect._doUnapply()
            visualEffect.setApplyLock(True)
        return Parallel(
            Sequence(self.getSuitSayTrack()),
            Sequence(Wait(1.4), Func(visualEffect.setApplyLock, False), applyMovie, Wait(2.75), Func(visualEffect.cleanup)),
        )

    def getCameraShot(self, duration):
        return self.camera.allGroupOverheadShot(duration=duration)


@AttackClass(attackType=AttackEnum.HIGHROLLER_CLONE_TOONUP)
class HighRollerCloneToonup(SuitSingleAttack):
    ANIM_NAME = "glower"
    OPEN_SHOT_DUR = 1.4
    CHEAT = True

    DefaultPoints = (
        [Point3(0.4, 3.8, 3.7), MovieUtil.PNT3_ZERO],
        [Point3(-0.4, 3.8, 3.7), MovieUtil.PNT3_ZERO],
    )
    PosPoints = {
        "hrollerc": (
            [Point3(0.3, 4.3, 5.3), MovieUtil.PNT3_ZERO],
            [Point3(-0.3, 4.3, 5.3), MovieUtil.PNT3_ZERO],
        ),
    }

    def doAttack(self):
        leftKnives = []
        rightKnives = []
        for i in range(0, 3):
            leftKnives.append(globalPropPool.getProp("dagger"))
            rightKnives.append(globalPropPool.getProp("dagger"))

        leftPosPoints, rightPosPoints = self.PosPoints.get(
            self.invoker.dna.name, self.DefaultPoints
        )

        suitTrack = self.getSuitTrack()
        leftKnifeTracks = Parallel()
        rightKnifeTracks = Parallel()

        for target in self.targetDicts:
            for i in range(0, 3):
                knifeDelay = 0.11
                leftTrack = Sequence()
                leftTrack.append(Wait(1.1))
                leftTrack.append(Wait(i * knifeDelay))
                leftTrack.append(
                    self.getPropAppearTrack(
                        leftKnives[i],
                        self.invoker,
                        leftPosPoints,
                        1e-06,
                        Point3(0.4, 0.4, 0.4),
                        scaleUpTime=0.1,
                    )
                )
                leftTrack.append(
                    self.getPropThrowTrack(
                        leftKnives[i],
                        hitPointNames=["face"],
                        missPointNames=["miss"],
                        hitDuration=0.3,
                        missDuration=0.3,
                        target=target,
                    )
                )
                leftKnifeTracks.append(leftTrack)
                rightTrack = Sequence()
                rightTrack.append(Wait(1.1))
                rightTrack.append(Wait(i * knifeDelay))
                rightTrack.append(
                    self.getPropAppearTrack(
                        rightKnives[i],
                        self.invoker,
                        rightPosPoints,
                        1e-06,
                        Point3(0.4, 0.4, 0.4),
                        scaleUpTime=0.1,
                    )
                )
                rightTrack.append(
                    self.getPropThrowTrack(
                        rightKnives[i],
                        hitPointNames=["face"],
                        missPointNames=["miss"],
                        hitDuration=0.3,
                        missDuration=0.3,
                    )
                )
                rightKnifeTracks.append(rightTrack)

        damageAnims = [["slip-backward", 0.01, 0.35]]
        toonTrack = self.getToonTracks(
            damageDelay=1.6,
            splicedDamageAnims=damageAnims,
            dodgeDelay=0.7,
            dodgeAnimNames=["sidestep"],
        )
        soundTrack = self.getSoundTrack(
            "SA_glower_power.ogg", delay=1.1, node=self.invoker
        )
        return Parallel(
            suitTrack, toonTrack, soundTrack, leftKnifeTracks, rightKnifeTracks
        )


@AttackClass(attackType=AttackEnum.HIGHROLLER_CLONE_TRAP)
class HighRollerCloneTrap(SuitSingleAttack):
    ANIM_NAME = "snap"
    eyeLandIndex = 2
    pbpSubtextDelay = 1.1
    DISRESPECT_ANIM_BLEND = True
    CHEAT = True

    def doAttack(self):
        # Do the rest of the track.
        suitHitTrack = self.getSuitDamageNumbers(
            damageDelay=3.86
        )
        toonTracks = self.getToonTracks(
            damageDelay=3.96,
            splicedDamageAnims=[],
            forceHit=True,
        )
        barCutscene = self.makeBarCutscene(delay=2.0)
        soundDelay = 0.2
        suitBarSound = self.getSoundTrack(
            "tt_s_ara_cmg_itemHitsFloor.ogg",
            delay=3.61 - soundDelay,
            node=self.invoker,
        )
        toonBarSound = self.getSoundTrack(
            "tt_s_ara_cmg_itemHitsFloor.ogg",
            delay=3.71 - soundDelay,
            node=self.invoker,
        )
        return Parallel(
            self.getSuitAnimTrack(wantDialog=False), suitHitTrack, toonTracks, barCutscene, suitBarSound, toonBarSound
        )

    def getSuitDamageNumbers(self, damageDelay=0.0):
        retParallel = Parallel()
        for suit in [target for target in self.targetObjs if self.isSuit(target)]:
            result = self.findTarget(suit.doId)
            retParallel.append(Func(self.updateSuitHP, suit, result.hpAdjust))
        return Sequence(Wait(damageDelay), retParallel)

    def makeBarCutscene(self, delay):
        # Build the cutscene.
        cutsceneLoader = CutsceneLoader.createLoader(
            key=CutsceneKeyEnum.HighRoller_Clone_Trap,
            toons=self.battle.activeToons[:],
            suits=self.battle.activeSuits[:],
            battle=self.battle,
            affectsCamera=self.battle.localToonPendingOrActive()
        )
        return Sequence(Wait(delay), cutsceneLoader.buildCutscene())

    def getCameraShot(self, duration):
        return self.camera.allGroupOverheadShot(duration=duration)


@AttackClass(attackType=AttackEnum.HIGHROLLER_CLONE_SQUIRT)
class HighRollerCloneSquirt(Attack):
    OPEN_SHOT_DUR = 3.0
    HP_TEXT_TYPE = TTLocalizer.HP_TEXT_FAKE_SOAK
    CHEAT = True

    def doAttack(self):
        from toontown.effects.Splash import Splash

        damageAnims = [["slip-backward", 0.01, 0.01]]

        propTracks = Parallel()
        for i, target in enumerate(self.targetDicts):
            toon = target['avatar']
            sphere = base.loader.loadModel('phase_3/models/misc/sphere')
            sphere.setBin('fixed', 1)
            sphere.setTransparency(TransparencyAttrib.MDual)
            sphere.setColorScaleOff()
            sphere.setColorScale(0.4, 0.4, 1.0, 0)
            sphere.setScale(0.55)
            sphere.reparentTo(render)
            sphere.setPos(toon.getPos(render) + Vec3(0, 0, 20))
            referenceNode = self.battle.attachNewNode('HRCloneSquirt-referenceNode')
            referenceNode.setPos(toon.getPos())

            splash = Splash(referenceNode)
            splash.setScale(2.5)
            splash.setBin('fixed', 1)
            splash.setTransparency(TransparencyAttrib.MDual)

            indexDelay = 0.2 + (0.15 * i)
            propTrack = Parallel(
                Sequence(
                    Wait(indexDelay),
                    Parallel(
                        Sequence(
                            Parallel(
                                LerpPosInterval(sphere, 0.55, toon.getPos(render), blendType='easeIn'),
                                LerpColorScaleInterval(sphere, 0.45, (0.4, 0.4, 1.0, 0.9), blendType='easeIn'),
                            ),
                            Func(sphere.hide),
                            Func(sphere.removeNode),
                        ),
                        Sequence(
                            Wait(0.55),
                            Func(splash.play),
                            Wait(splash.splashdown.getDuration('splashdown') * 0.65),
                            Func(splash.stop),
                            Func(splash.destroy),
                        ),
                    ),
                ),
                Sequence(
                    Wait(indexDelay + 0.55),
                    SoundInterval(loader.loadSfx('phase_4/audio/sfx/MG_cannon_splash.ogg')),
                ),
            )
            propToonTrack = self.getToonTrack(
                damageDelay=indexDelay + 0.55,
                splicedDamageAnims=damageAnims,
                dodgeDelay=3.0,
                dodgeAnimNames=["sidestep"],
                showDamageExtraTime=1.8,
                showMissedExtraTime=0.8,
                hpTextType=self.HP_TEXT_TYPE,
                target=target,
            )
            propTracks.append(Parallel(propTrack, propToonTrack))

        return Sequence(Parallel(Sequence(propTracks), Wait(3.0)))

    def getCameraShot(self, duration):
        return self.camera.heldShot(8.0, 3.0, 3, 142, 10, 0, duration=0.65, name='HighRollerCloneSquirtHeldShot')


@AttackClass(attackType=AttackEnum.DICE_ROULETTE)
class DiceRoulette(Attack):
    DISRESPECT_ANIM_BLEND = True
    CHEAT = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ashleyDie = self.extraArgs[0]
        self.maryKateDie = self.extraArgs[1]

    def doAttack(self):
        if self.maryKateDie == 6:
            # if the mary kate die is 6, the cogs get damaged instead
            cutsceneLoader = CutsceneLoader.createLoader(
                key=CutsceneKeyEnum.HighRoller_DiceRouletteSuitsDamaged,
                hroller=self.invoker,
                battle=self.battle,
                setDicePair=(self.ashleyDie, self.maryKateDie))
            return Parallel(self.getSuitTracks(damageDelay=6.4), cutsceneLoader.buildCutscene(), self.getEndTrack())
        elif self.maryKateDie <= 4:
            # if the mary kate die is 1-4, toons get damaged.
            cutsceneLoader = CutsceneLoader.createLoader(
                key=CutsceneKeyEnum.HighRoller_DiceRouletteToonsDamaged,
                toons=[base.cr.doId2do.get(target.avId) for target in self.targets],
                hroller=self.invoker,
                battle=self.battle,
                setDicePair=(self.ashleyDie, self.maryKateDie))
            return Parallel(self.getToonTracks(damageDelay=6.4), cutsceneLoader.buildCutscene())
        else:
            # if the mary kate die is 5, the attack will do nothing
            cutsceneLoader = CutsceneLoader.createLoader(
                key=CutsceneKeyEnum.HighRoller_DiceRouletteNothing,
                hroller=self.invoker,
                battle=self.battle,
                setDicePair=(self.ashleyDie, self.maryKateDie))
            return cutsceneLoader.buildCutscene()

    def getSuitTracks(self, damageDelay=0.0):
        retParallel = Parallel()
        for suit in [target for target in self.targetObjs if self.isSuit(target)]:
            result = self.findTarget(suit.doId)
            retParallel.append(Func(self.updateSuitHP, suit, result.hpAdjust))
        return Sequence(Wait(damageDelay), retParallel)

    def getCameraShot(self, duration):
        return Wait(duration)


@AttackClass(attackType=AttackEnum.ACE_IN_THE_HOLE)
class AceInTheHole(Attack):
    CHEAT = True

    pbpFadeInMult = 0.05
    pbpSubtextFadeInMult = 0.085
    pbpFadeOutMult = 0.23

    def doAttack(self):
        scarySfx = loader.loadSfx('phase_13/audio/sfx/april_toons/highroller/cc_s_sfx_ene_hroller_ace_in_the_hole.ogg')

        cutsceneLoader = CutsceneLoader.createLoader(
            key=CutsceneKeyEnum.HighRoller_AceInTheHole, hroller=self.invoker, battle=self.battle)
        return Parallel(Sequence(Wait(3.05), Parallel(*(SoundInterval(scarySfx) for _ in range(10)))),
                        self.getToonTracks(damageDelay=11.5, hpTextType=TTLocalizer.HP_TEXT_15_VULNERABLE_ICON),
                        cutsceneLoader.buildCutscene())

    def getCameraShot(self, duration):
        return Wait(duration)


@AttackClass(attackType=AttackEnum.FREE_CRUISE)
class FreeCruise(SuitSingleAttack):
    ANIM_NAME = "song-and-dance"
    eyeLandIndex = 2
    pbpSubtextDelay = 1.1
    DISRESPECT_ANIM_BLEND = True

    def doAttack(self):
        # Do the rest of the track.
        toonTracks = self.getToonTracks(
            damageDelay=5.71,
            splicedDamageAnims=[],
            dodgeDelay=5.71,
            dodgeAnimNames=["neutral"],
        )
        boatCutscene = self.makeAttackCutscene(delay=4.0)
        soundDelay = 0.2
        if self.landed:
            soundFile = "AA_drop_boat.ogg"
            toonBoatSound = self.getSoundTrack(
                "AA_drop_boat_cog.ogg",
                delay=5.71 - soundDelay,
                node=self.invoker,
            )
        else:
            soundFile = "AA_drop_boat_miss.ogg"
            toonBoatSound = Sequence()
        soundTrack = self.getSoundTrack("AA_heal_happydance.ogg", node=self.invoker)
        boatSoundTrack = self.getSoundTrack(
            soundFile,
            node=self.invoker,
            delay=3.6,
        )
        return Parallel(
            toonTracks, boatCutscene, self.getSuitAnimTrack(), soundTrack, toonBoatSound, boatSoundTrack
        )

    def makeAttackCutscene(self, delay):
        # Build the cutscene.
        if self.landed:
            cutsceneLoader = CutsceneLoader.createLoader(
                key=CutsceneKeyEnum.HighRoller_FreeCruise,
                toons=self.battle.activeToons[:],
                suits=self.battle.activeSuits[:],
                battle=self.battle,
                affectsCamera=self.battle.localToonPendingOrActive()
            )
        else:
            cutsceneLoader = CutsceneLoader.createLoader(
                key=CutsceneKeyEnum.HighRoller_FreeCruiseMissed,
                toons=self.battle.activeToons[:],
                suits=self.battle.activeSuits[:],
                battle=self.battle,
                affectsCamera=self.battle.localToonPendingOrActive()
            )

        return Sequence(Wait(delay), cutsceneLoader.buildCutscene())

    def getCameraShot(self, duration):
        return self.camera.allGroupOverheadShot(duration=duration)


@AttackClass(attackType=AttackEnum.CON_DUCK_TION)
class ConDuckTion(Attack):
    ANIM_NAME = "throw-object"
    OPEN_SHOT_DUR = 2.8
    appearDelay = 1.1
    throwDelay = 3.2
    damageDelay = 4.3
    dodgeDelay = 2.8
    duration = 1.7

    def doAttack(self):
        suitTrack = self.getSuitTrack()
        birdTracks = Parallel()
        for target in self.targetDicts:
            numBirds = 4
            dmg = target["hp"]
            duckDelay = 0
            for i in range(0, numBirds):
                duckie = globalPropPool.getProp("duck_hroller")
                duckie.setScale(0.01)
                duckie.reparentTo(self.invoker.getRightHand())
                duckie.setHpr(Point3(-70, 0, 180))
                duckie.setPos(
                    random.random() * 0.6 - 0.4,
                    random.random() * 0.6 - 0.2,
                    random.random() * 0.6 - 0.7,
                )
                # Grab their x and y compared to the battle real quick
                startX = duckie.getX(self.battle)
                startY = duckie.getY(self.battle)
                # Pick their final x and y
                hitPoint: Point3 = self.battle.getActorPosHpr(target['avatar'])[0]
                hitX = hitPoint.getX() + random.uniform(1, -1)
                hitY = hitPoint.getY()
                # Then average them out to get their hit points
                hitPoint1 = Point3(((startX*2)+hitX)/2, ((startY*2)+hitY)/2, 1)
                hitPoint2 = Point3(hitX*0.9, hitY*0.9, 1)
                hitPoint3 = Point3((hitX*1.5), (hitY*1.5), 1)

                def getSquashEffect(delay: float):
                    return Sequence(Wait(delay - 0.05),
                                    LerpScaleInterval(duckie, 0.1, (6, 6, 1.5), blendType='easeInOut'),
                                    LerpScaleInterval(duckie, 0.1, (2, 2, 5), blendType='easeInOut'),
                                    LerpScaleInterval(duckie, 0.05, (3, 3, 3), blendType='easeInOut'),)

                birdTrack = Sequence(
                    Wait(self.throwDelay + duckDelay),
                    Func(self.battle.movie.needRestoreRenderProp, duckie),
                    Func(duckie.wrtReparentTo, self.battle),
                    Func(duckie.setHpr, Point3(160, 20, 0)),
                    Parallel(
                        ProjectileInterval(duckie, duration=(self.duration*0.5), endPos=hitPoint1, gravityMult=1.5),
                        getSquashEffect(self.duration*0.5)),
                    Parallel(
                        ProjectileInterval(duckie, duration=(self.duration*0.3), endPos=hitPoint2, gravityMult=2),
                        getSquashEffect(self.duration*0.3)),
                    ProjectileInterval(duckie, duration=(self.duration*0.2), endPos=hitPoint3, gravityMult=2),
                    # LerpPosInterval(duckie, 1.1, hitPoint),
                )
                scaleTrack = Sequence(
                    Wait(self.appearDelay), LerpScaleInterval(duckie, 0.4, Point3(3, 3, 3))
                )
                removeProp = Sequence(
                    Wait(self.damageDelay + 1.5),
                    LerpScaleInterval(duckie, 0.6, 0.01, blendType="easeIn"),
                    Func(MovieUtil.removeProp, duckie),
                )
                birdTracks.append(Parallel(birdTrack, scaleTrack, removeProp))
                duckDelay += .1

        damageAnims = [["cringe", 0.01, 0.14, 0.21], ["cringe", 0.01, 0.14, 0.13], ["cringe", 0.01, 0.43]]
        toonTrack = self.getToonTracks(
            damageDelay=self.damageDelay,
            splicedDamageAnims=damageAnims,
            dodgeDelay=self.dodgeDelay,
            dodgeAnimNames=["sidestep"],
            showMissedExtraTime=1.1,
        )
        soundTrack = self.getSoundTrack(
            "phase_13/audio/sfx/april_toons/highroller/cc_s_sfx_ene_hroller_conducktion.ogg",
            delay=2.95, node=self.invoker
        )
        return Parallel(suitTrack, toonTrack, birdTracks, soundTrack)

    def getCameraShot(self, duration):
        return self.camera.allGroupOverheadShot(duration=duration)


@AttackClass(attackType=AttackEnum.HR_EXIT_UNTOUCHABLE)
class HRExitUntouchable(Attack):

    def doAttack(self):
        retParallel = Parallel()
        veList = self.invoker.getVisualEffectsOfId(VisualEffectEnum.HR_UNTOUCHABLE)
        rollingYet = False
        for ve in veList:
            seq, _ = ve.getUnapplyMovie()
            if not rollingYet:
                seq.append(Wait(0.1))
                seq.append(Func(self.invoker.addVisualEffect, VisualEffectEnum.ROLLED))
                rollingYet = True
            retParallel.append(seq)
        return retParallel

    def getCameraShot(self, duration):
        return self.camera.allGroupOverheadShot(duration=duration)


@AttackClass(attackType=AttackEnum.HR_TOON_LAFF_UP)
class HRToonLaffUp(Attack):
    ALLOW_GROUPING = True
    timeBetweenHeals = 0.12

    def doAttack(self):
        extraDelay = self.extraArgs[0]
        eventfulTrack = Parallel(
            self.getAvHealTrack(extraDelay + 0.1),
            self.getSoundTrack(
                "SA_sevens_heal.ogg",
                delay=extraDelay + 0.1,
                node=self.battle,
            ),
            Wait(extraDelay + 1.5),
        )

        return eventfulTrack

    def getExtraLaffOfIndex(self, index):
        return self.extraArgs[1 + index]

    def getAvHealTrack(self, delay):
        retSequence = Track()
        index = -1
        for target in self.targetDicts:
            toon = target['avatar']
            toonIndex = self.battle.activeToons.index(toon)
            # increment our index
            index += 1
            # do a toon heal
            retSequence.append(
                (
                    delay + (index * self.timeBetweenHeals),
                    Parallel(
                        Func(toon.showHpString, f"+{self.getExtraLaffOfIndex(toonIndex)}\n\1damage_subtext\1MAX LAFF!\2", color=(0, 0.9, 0, 1)),
                        Sequence(
                            ActorInterval(toon, "jump"),
                            Wait(0.01),
                            Func(toon.loop, "neutral"),
                        ),
                        self.doGreenSpinParticles(toon, 0, 1.5, 1.0),
                    ),
                )
            )

        return retSequence

    def doGreenSpinParticles(self, av, delay, duration, softstop):
        particleEffect = BattleParticles.loadParticleFile('chainsawScabbardDown.ptf')
        p0 = particleEffect.getParticlesList()[0]
        p0.emitter.setExplicitLaunchVector(Vec3(0.0000, 0.0000, -5.0000))
        particleNode = av.attachNewNode('scabbard-particleNode')
        particleNode.setZ(av.height + 1.0)
        particleTrack = self.getPartTrack(particleEffect, 0.0, 2.0,
                                          [particleEffect, particleNode, 0], softStop=-1.0)
        return Sequence(particleTrack, Func(particleNode.removeNode))

    def getCameraShot(self, duration):
        camAv = base.localAvatar
        if not camAv:
            camAv = self.targetObjs[0]
        return self.camera.heldRelativeShot(camAv, 0, 11, (camAv.height / 2) + 2.25, 180, 0, 0, duration, 'singleAvatarShot')


@AttackClass(attackType=AttackEnum.ROLLED)
class Rolled(SuitSingleAttack):
    ANIM_NAME = "magic3"
    OPEN_SHOT_DUR = 1.7

    def doAttack(self):
        suitTrack = self.getSuitAnimTrack()
        allToonTracks = Parallel()

        possibleColors = [cloneDict[0] for cloneDict in HighRollerGlobals.CloneType2Visuals.values()]

        for target in self.targetDicts:
            damageDelay = 1.7 + (random.random() * 0.2)
            toon = target["avatar"]
            sprayEffect = BattleParticles.createParticleEffect(file="spinSpray")
            spinEffect1 = BattleParticles.createParticleEffect(file="spinEffect")
            spinEffect2 = BattleParticles.createParticleEffect(file="spinEffect")
            spinEffect3 = BattleParticles.createParticleEffect(file="spinEffect")

            # Random colors
            for particle in [sprayEffect, spinEffect1, spinEffect2, spinEffect3]:
                color = random.choice(possibleColors)
                lightColor = Vec4(*[(colorPart + 0.95) / 2.0 for colorPart in color])
                particle.getParticlesList()[0].renderer.setColor(random.choice([color, lightColor]))

            spinEffect1.reparentTo(toon)
            spinEffect2.reparentTo(toon)
            spinEffect3.reparentTo(toon)
            height1 = toon.getHeight() * (random.random() * 0.2 + 0.7)
            height2 = toon.getHeight() * (random.random() * 0.2 + 0.4)
            height3 = toon.getHeight() * (random.random() * 0.2 + 0.1)
            spinEffect1.setPos(0.8, -0.7, height1)
            spinEffect1.setHpr(0, 0, -random.random() * 10 - 85)
            spinEffect1.setHpr(spinEffect1, 0, 50, 0)
            spinEffect2.setPos(0.8, -0.7, height2)
            spinEffect2.setHpr(0, 0, -random.random() * 10 - 85)
            spinEffect2.setHpr(spinEffect2, 0, 50, 0)
            spinEffect3.setPos(0.8, -0.7, height3)
            spinEffect3.setHpr(0, 0, -random.random() * 10 - 85)
            spinEffect3.setHpr(spinEffect3, 0, 50, 0)
            spinEffect1.wrtReparentTo(self.battle)
            spinEffect2.wrtReparentTo(self.battle)
            spinEffect3.wrtReparentTo(self.battle)
            particleNode = self.invoker.attachNewNode('rolled-particle-node')
            particleNode.headsUp(toon)
            sprayTrack = Sequence(
                self.getPartTrack(sprayEffect, 1.0, 1.9, [sprayEffect, particleNode, 0]),
                Func(particleNode.removeNode),
            )
            spinTrack1 = self.getPartTrack(
                spinEffect1, 2.1, 3.9, [spinEffect1, self.battle, 0]
            )
            spinTrack2 = self.getPartTrack(
                spinEffect2, 2.1, 3.9, [spinEffect2, self.battle, 0]
            )
            spinTrack3 = self.getPartTrack(
                spinEffect3, 2.1, 3.9, [spinEffect3, self.battle, 0]
            )
            damageAnims = []
            damageAnims.append(["duck", 0.01, 0.01, 1.1])
            damageAnims.extend(self.getSplicedLerpAnims("think", 0.66, 1.1, startTime=2.26))
            damageAnims.extend(self.getSplicedLerpAnims("think", 0.66, 1.1, startTime=2.26))
            toonTrack = self.getToonTrack(
                damageDelay=damageDelay,
                splicedDamageAnims=damageAnims,
                dodgeDelay=0.91,
                dodgeAnimNames=["sidestep"],
                showDamageExtraTime=2.1,
                showMissedExtraTime=1.0,
                target=target,
            )

            toonSpinTrack = Sequence(
                Wait(damageDelay + 0.9),
                LerpHprInterval(toon, 0.7, Point3(-10, 0, 0)),
                LerpHprInterval(toon, 0.5, Point3(-30, 0, 0)),
                LerpHprInterval(toon, 0.2, Point3(-60, 0, 0)),
                LerpHprInterval(toon, 0.7, Point3(-700, 0, 0)),
                LerpHprInterval(toon, 1.0, Point3(-1310, 0, 0)),
                LerpHprInterval(toon, 0.4, toon.getHpr()),
                Wait(0.5),
            )
            soundTrack = self.getSoundTrack(
                "tt_s_ara_cfg_toonInWhirlwind.ogg",
                delay=damageDelay + 0.9,
                node=self.invoker,
            )
            allToonTracks.append(Parallel(
                sprayTrack,
                toonTrack,
                toonSpinTrack,
                soundTrack,
                spinTrack1,
                spinTrack2,
                spinTrack3,
            ))

        return Parallel(suitTrack, allToonTracks)

    def getCameraShot(self, duration):
        return self.camera.randomGroupAttackCam(
            self.invoker, self.targetDicts, self.battle, duration, self.OPEN_SHOT_DUR)

# endregion
