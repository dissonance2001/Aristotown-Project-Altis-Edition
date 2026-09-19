import math
import random

from panda3d.core import NodePath, Point3, VBase3, Vec4, Vec3, VBase4
from toontown.chat.constants.ChatGlobals import  CFSpeech, CFTimeout
from direct.interval.IntervalGlobal import *
from direct.showbase.PythonUtil import lerp
from toontown.audio.IsolatedSoundInterval import IsolatedSoundInterval

from toontown.battle import BattleGlobals, BattleParticles, MovieLure, MovieUtil, MovieTrap
from toontown.battle.BattleProps import globalPropPool
from toontown.battle.BattleSounds import globalBattleSoundCache
from toontown.battle.attacks.base.AttackEnum import AttackEnum
from toontown.battle.attacks.client.Attack import Attack
from toontown.battle.attacks.client.AttackRepository import AttackClass
from toontown.battle.attacks.client.suit.BasicAttacks import (
    AllowGroupingAttack, AvatarSayPhraseAttack, SuitDamageAttack, DoNothing,
    SuitHealAttack, ShowHpTextAttack, PlayCutsceneAttack, ToonDamageAttack,
)
from toontown.battle.attacks.client.suit.SuitGroupAttack import SuitGroupAttack
from toontown.battle.attacks.client.suit.SuitSingleAttack import SuitSingleAttack
from toontown.battle.attacks.client.suit.BasicSuitAttacks import CigarSmoke
from toontown.battle.environmental.base.EnvironmentalEnum import RainmakerWeather
from toontown.battle.gui.special.ChainsawMeterGUI import ChainsawMeterGUI
from toontown.battle.statuses import SEE
from toontown.cutscene import CutsceneLocalizer
from toontown.cutscene.repository.CutsceneKeyEnum import CutsceneKeyEnum
from toontown.effects import DustCloud
from toontown.battle.visuals.VisualEffectEnums import VisualEffectEnum, SUIT_VISUAL_EFFECTS_TO_REMOVE
from toontown.battle.visuals.VisualEffects import ChangeSpeciesVisualEffect
from toontown.cutscene.repository.CutsceneLoader import CutsceneLoader
from toontown.inventory.enums.ItemEnums import BoosterItemType
from toontown.suit import SuitHealthMeter
from toontown.suit.DistributedSuitBase import DistributedSuitBase
from toontown.suit.SuitDNA import getSuitBodyType
from toontown.toon import ToonDNA
from toontown.instances.mercs.InstanceMercGlobals import InvestorEnum2Name
from toontown.toonbase import TTLocalizer, ToontownGlobals


class WagerBase(SuitSingleAttack):
    ANIM_NAME = "pull-slots"
    CHEAT = True
    WANT_TARGET_INDICATORS = False

    secondsBeforeStarting = (
        0.7  # will need to change the event in DuckShufflerWagerCutscene to accommodate
    )

    OPEN_SHOT_DUR = 4.0
    pbpSubtextDelay = 2.0

    damageDelay = 3.5
    eyeLandIndex = 0

    # list of sounds based on eyeLandIndex
    soundFileFormat = 'phase_5/audio/sfx/SA_wager_{resultName}_hit.ogg'
    resultNameList = [
        'sevens',
        'ducks',
        'bar',
        'beans',
        'bust'
    ]

    def doAttack(self):
        # Do the rest of the track.
        suitTrack = self.getDuckTrack()
        toonTrack = self.getToonTracks(
            damageDelay=self.damageDelay, damageAnimNames=["cringe"], dodgeDelay=0.91
        )
        speciesTrack = self.getToonResponseTrack()
        return Parallel(suitTrack, toonTrack, speciesTrack)

    def getCameraShot(self, duration):
        # delegated to CutsceneLoader
        return Wait(duration)

    def getTauntPool(self, suit, attackType, round, tauntIndex) -> list:
        return TTLocalizer.DuckShufflerRollStart

    """
    Sequence makings
    """

    def getToonResponseTrack(self):
        return Sequence()

    def getDuckTrack(self):
        cutsceneLoader = CutsceneLoader.createLoader(
            key=CutsceneKeyEnum.DuckShuffler_Wager_Base,
            invoker=self.invoker,
            battle=self.battle,
            eyeLandIndex=self.eyeLandIndex,
            dialogue=self.getRollReactDialogue(),
            resultSound=self.soundFileFormat.format(resultName=self.resultNameList[self.eyeLandIndex]),
            affectsCamera=self.battle.localToonPendingOrActive()
        )
        track = cutsceneLoader.buildCutscene()

        suitTrack = self.getSuitAnimTrack(
            doActorInterval=False,
            wantSpeechHeadAnim=False,
            forceWait=track.getDuration(),
        )
        return Parallel(track, suitTrack)

    def getRollReactDialogue(self):
        taunts = TTLocalizer.SuitAttackTaunts.get(self.attackType)
        return taunts[self.taunt[0] % len(taunts)]


@AttackClass(attackType=AttackEnum.WAGER_DUCKS)
class WagerDucks(WagerBase):
    eyeLandIndex = 1
    damageDelay = 4.5

    def getDuckVisualEffect(self, av) -> ChangeSpeciesVisualEffect:
        return ChangeSpeciesVisualEffect(
            avProfile=av,
            effectEnum=VisualEffectEnum.TOON_BECOME_DUCK,
            extraArgs=[ToonDNA.toonSpeciesTypes.index("f")],
        )

    def doAttack(self):
        # Do the rest of the track.
        suitTrack = self.getDuckTrack()
        toonTrack = self.getToonTracks(
            damageDelay=self.damageDelay + self.secondsBeforeStarting,
            damageAnimNames=["neutral"],
            dodgeAnimNames=[],
            dodgeDelay=0.91,
        )
        speciesTrack = self.getToonResponseTrack()
        return Parallel(suitTrack, toonTrack, speciesTrack)

    def getToonResponseTrack(self):
        speciesTrack = Parallel()
        toon = None
        for target in self.targetDicts:
            toon = target["avatar"]
            speciesEffect = self.getDuckVisualEffect(toon)
            applyMovie, _ = speciesEffect.getApplyMovie()
            speciesTrack.append(applyMovie)
        if not toon:
            return Sequence()

        camTrack = Sequence()
        if self.battle.hasLocalToon():
            camTrack = Func(camera.setPosHpr, 0, 4, 4, 180, 0, 0)

        return Sequence(
            Wait(self.damageDelay + self.secondsBeforeStarting),
            Parallel(
                speciesTrack,
                camTrack,
                self.getSoundTrack("SA_duckification.ogg", delay=0, node=toon),
            ),
        )


@AttackClass(attackType=AttackEnum.WAGER_SEVENS)
class WagerSevens(WagerBase):
    eyeLandIndex = 0

    timeBetweenHeals = 0.12

    def doAttack(self):
        eventfulTrack = Parallel(
            self.getDuckTrack(),
            self.getAvHealTrack(4.0 + self.secondsBeforeStarting),
            self.getSoundTrack(
                "SA_sevens_heal.ogg",
                delay=4.0 + self.secondsBeforeStarting,
                node=self.invoker,
            ),
        )
        if self.battle.hasLocalToon():
            eventfulTrack.append(Sequence(
                Wait(3.6 + self.secondsBeforeStarting),
                LerpFunctionInterval(
                    base.camLens.setMinFov,
                    duration=0.6,
                    fromData=BattleGlobals.BattleCamDefaultFov / (4.0 / 3.0),
                    toData=(BattleGlobals.BattleCamDefaultFov / (4.0 / 3.0)) / 0.88,
                    blendType="easeInOut",
                ),
            ))
            eventfulTrack = Parallel(
                eventfulTrack,
                Sequence(
                    Wait(eventfulTrack.getDuration() + 0.01),
                    Func(
                        base.camLens.setMinFov,
                        BattleGlobals.BattleCamDefaultFov / (4.0 / 3.0),
                    ),
                ),
            )

        return eventfulTrack

    def getAvHealTrack(self, delay):
        retSequence = Track()
        index = -1
        for target in self.targetObjs:
            result = self.findTarget(target.doId)
            healAmount = result.hpAdjust
            if healAmount == 0:
                continue
            # increment our index
            index += 1
            # do a toon heal
            if self.isToon(target):
                retSequence.append(
                    (
                        delay + (index * self.timeBetweenHeals),
                        Parallel(
                            Func(target.toonUp, healAmount, False, "", True),
                            Sequence(
                                ActorInterval(target, "jump"),
                                Wait(0.01),
                                Func(target.loop, "neutral"),
                            ),
                            self.doGreenSpinParticles(target, 0, 1.5, 1.0),
                        ),
                    )
                )
            elif self.isSuit(target):
                retSequence.append(
                    (
                        delay + (index * self.timeBetweenHeals),
                        Parallel(
                            Func(target.updateHealthBar, healAmount),
                            Func(target.showHpText, healAmount),
                            self.doGreenSpinParticles(target, 0, 1.5, 1.0),
                        ),
                    )
                )
        return retSequence

    def doGreenSpinParticles(self, av, delay, duration, softstop):
        retParallel = Parallel()
        for i in range(3):
            effect = BattleParticles.createParticleEffect(file="healSpinEffect")
            effect.reparentTo(av)
            height = av.getHeight() * (random.random() * 0.2 + 0.1 + (0.3 * i))
            effect.setPos(0.8, -0.7, height)
            effect.setHpr(0, 0, -random.random() * 10 - 85)
            effect.setHpr(effect, i * 120, 50, 0)
            effect.wrtReparentTo(self.battle)
            retParallel.append(
                self.getPartTrack(
                    effect,
                    delay,
                    duration,
                    [effect, self.battle, 0],
                    duration - softstop,
                )
            )
        return retParallel


@AttackClass(attackType=AttackEnum.WAGER_BEANS)
class WagerBeans(WagerBase):
    eyeLandIndex = 3

    beanModel = loader.loadModel("phase_4/models/props/jellybean4.bam")
    beanColors = (
        (1, 1, 0.2, 1),
        (1, 0.2, 0.2, 1),
        (0.2, 1, 0.2, 1),
        (0.2, 0.2, 1, 1),
        (1, 0.2, 1, 1),
    )

    def doAttack(self):
        duckTrack = self.getDuckTrack()
        rainstormTracks = self.getToonRainstormTracks(4.5 + self.secondsBeforeStarting)
        camTrack = Sequence()
        if self.battle.hasLocalToon():
            camTrack = Sequence(
                Wait(5.0 + self.secondsBeforeStarting),
                Func(camera.setPosHpr, 0, 4, 4, 180, 0, 0),
            )
        return Parallel(
            duckTrack,
            rainstormTracks,
            camTrack,
            self.getLocalAvScavengeTrack(delay=5.0 + self.secondsBeforeStarting),
        )

    def getLocalAvScavengeTrack(self, delay):
        if not base.localAvatar:
            return Sequence()
        if not self.battle.hasLocalToon():
            return Sequence()

        def addScavenge():
            toon = base.localAvatar
            amount = toon.applyBoosters(BoosterItemType.Jellybeans_Global, 20)
            # TODO: Figure out the best way to bring back this scavenge
            # toon.queueScavenge(amount, ScavengeType.Jellybeans)

        return Sequence(
            Wait(delay),
            Func(addScavenge),
        )

    def getToonRainstormTracks(self, delay):
        retParallel = Parallel()
        toon = None
        for toon in self.battle.activeToons:
            retParallel.append(
                Sequence(
                    Wait(delay),
                    self.doToonStormTrack(toon),
                )
            )

        # funny sound
        if toon:
            retParallel.append(
                self.getSoundTrack("SA_wager_beans_fanfare.ogg", delay=delay, node=toon)
            )
            retParallel.append(
                self.getSoundTrack("SA_wager_beans_effect.ogg", delay=delay, node=toon)
            )

        return retParallel

    def doToonStormTrack(self, toon):
        jellybean = self.beanModel.find("**/jellybean")
        systems = []
        rainScenes = Parallel()
        for i, color in enumerate(self.beanColors):
            cutsceneLoader = CutsceneLoader.createLoader(
                key=CutsceneKeyEnum.DuckShuffler_Wager_Beans,
                toon=toon,
                affectsCamera=self.battle.localToonPendingOrActive()
            )
            geomH = 360 * (i / (len(self.beanColors) - 1))
            for ps in cutsceneLoader.getParticleSystems():
                systems.append(ps)
                for particle in ps.getParticlesList():
                    node = jellybean.copyTo(NodePath())
                    node.setColorScale(*color)
                    node.setH(geomH)
                    particle.renderer.setGeomNode(node.node())
            cutsceneLoader.getParticleSystems()[0].setZ(toon.getHeight() + 3)
            cutsceneLoader.addArgumentsToCutscene([color])
            rainScenes.append(
                Sequence(
                    Wait(0.5 * (i / (len(self.beanColors) - 1))),
                    cutsceneLoader.buildCutscene(),
                )
            )

        # get the stormcloud
        cloud = globalPropPool.getProp("stormcloud")
        cloud.pose("stormcloud", 0)
        cloudTrack = Sequence()
        cloudTrack.append(
            self.getPropAppearTrack(
                cloud,
                toon,
                [Point3(0, 0, toon.getHeight() + 3), VBase3(180, 0, 0)],
                1e-06,
                Point3(3, 3, 3),
                scaleUpTime=0.7,
            )
        )
        cloudTrack.append(Func(cloud.wrtReparentTo, render))
        cloudTrack.append(Wait(3.0))
        cloudTrack.append(LerpScaleInterval(cloud, 0.5, MovieUtil.PNT3_NEARZERO))
        cloudTrack.append(Func(MovieUtil.removeProp, cloud))
        rainScenes.append(cloudTrack)

        # toon react
        toonReactSeq = Sequence(
            Wait(0.5),
            Parallel(
                ActorInterval(toon, "good-putt", playRate=0.8),
                Func(toon.stopBlink),
                Func(toon.surpriseEyes),
                Func(toon.showSurpriseMuzzle),
            ),
            Wait(0.01),
            Parallel(
                Func(toon.loop, "neutral"),
                Func(toon.hideSurpriseMuzzle),
                Func(toon.openEyes),
                Func(toon.startBlink),
            ),
        )
        toonVocalPog = Sequence(
            Wait(1.0),
            Wait(random.random() * 0.4),
            Func(toon.playDialogueForString, "yoooo"),
        )
        rainScenes.append(toonReactSeq)
        rainScenes.append(toonVocalPog)

        return rainScenes


@AttackClass(attackType=AttackEnum.WAGER_BAR)
class WagerBar(WagerBase):
    eyeLandIndex = 2
    pbpSubtextDelay = 1.1
    DISRESPECT_ANIM_BLEND = True

    def doAttack(self):
        # Do the rest of the track.
        suitTrack = self.getDuckTrack()
        suitHitTrack = self.getSuitDamageNumbers(
            damageDelay=5.61 + self.secondsBeforeStarting
        )
        toonTracks = self.getToonTracks(
            damageDelay=5.71 + self.secondsBeforeStarting,
            splicedDamageAnims=[],
            forceHit=True,
        )
        barCutscene = self.makeBarCutscene(delay=4.0 + self.secondsBeforeStarting)
        soundDelay = 0.2
        suitBarSound = self.getSoundTrack(
            "tt_s_ara_cmg_itemHitsFloor.ogg",
            delay=5.61 - soundDelay + self.secondsBeforeStarting,
            node=self.invoker,
        )
        toonBarSound = self.getSoundTrack(
            "tt_s_ara_cmg_itemHitsFloor.ogg",
            delay=5.71 - soundDelay + self.secondsBeforeStarting,
            node=self.invoker,
        )
        return Parallel(
            suitTrack, suitHitTrack, toonTracks, barCutscene, suitBarSound, toonBarSound
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
            key=CutsceneKeyEnum.DuckShuffler_Wager_Bar,
            toons=self.battle.activeToons[:],
            suits=self.battle.activeSuits[:],
            battle=self.battle,
            affectsCamera=self.battle.localToonPendingOrActive()
        )
        return Sequence(Wait(delay), cutsceneLoader.buildCutscene())


@AttackClass(attackType=AttackEnum.WAGER_BUST)
class WagerBust(WagerBase):
    eyeLandIndex = 4

    def doAttack(self):
        duckTrack = self.getDuckTrack()
        depressionTrack = (
            Sequence()
        )  # self.getDepressionTrack(duckTrack.getDuration()) No depression :)
        return Parallel(duckTrack, depressionTrack)

    def getDepressionTrack(self, endDuration):
        timeBeforeSad = 4.0
        return Sequence(
            Wait(timeBeforeSad),
            Func(self.invoker.specialHead.setHurtMode, True),
            Wait(endDuration - timeBeforeSad),
            Func(self.invoker.specialHead.setHurtMode, False),
        )


@AttackClass(attackType=AttackEnum.DIVE)
class Dive(SuitSingleAttack):
    ANIM_NAME = "dive"
    CHEAT = True
    OPEN_SHOT_DUR = 5

    forceLoopNeutral = False

    def doAttack(self):
        cutsceneDelay = 2.0
        visualEffectDelay = 2.8

        cutsceneTrack = self.makeCutscene()
        effectTrack = Sequence(
            Wait(cutsceneDelay + visualEffectDelay),
            Func(MovieUtil.applyVisualEffect, self.invoker, VisualEffectEnum.DIVING),
        )
        clearChatTrack = Sequence(
            Wait(cutsceneDelay + 1.0), Func(self.invoker.clearChat)
        )

        return Parallel(cutsceneTrack, effectTrack, clearChatTrack)

    def makeCutscene(self, delay=0.0):
        # Build the cutscene.
        cutsceneLoader = CutsceneLoader.createLoader(
            key=CutsceneKeyEnum.DeepDiver_Dive,
            invoker=self.invoker,
            toons=self.battle.activeToons[:],
            battle=self.battle,
            affectsCamera=self.battle.localToonPendingOrActive()
        )
        track = cutsceneLoader.buildCutscene()

        # Return result.
        return Sequence(
            Func(
                self.invoker.setChatAbsolute,
                self.getAttackTaunt(),
                CFSpeech | CFTimeout,
            ),
            Wait(delay),
            track,
            Wait(1.0),
        )

    def getCameraShot(self, duration):
        # Handled by cutscene loader
        return Wait(duration)


@AttackClass(attackType=AttackEnum.SINK_OR_SWIM)
class SinkOrSwim(SuitSingleAttack):
    ANIM_NAME = "exitWater"
    CHEAT = True
    OPEN_SHOT_DUR = 5

    forceLoopNeutral = False

    def doAttack(self):
        visualEffectDelay = 1.4
        damageDelay = 2.58
        hitAtleastOneToon = 0
        for t in self.targetDicts:
            if t["hp"] < 0:
                hitAtleastOneToon = 1

        suitTrack = self.makeCutscene()
        effectTrack = Sequence(
            Wait(visualEffectDelay),
            Func(MovieUtil.unapplyVisualEffect, self.invoker, VisualEffectEnum.DIVING),
        )
        toonTracks = self.getToonTracks(damageDelay, ["slip-forward"], 2.07, ["jump"])

        # Compile all the tracks.
        track = Parallel(suitTrack, effectTrack, toonTracks)

        # Add sound for toons hitting the ground if any got hit.
        if hitAtleastOneToon == 1:
            track.append(
                Sequence(
                    Wait(damageDelay + 0.5),
                    SoundInterval(
                        globalBattleSoundCache.getSound("Toon_bodyfall_synergy.ogg"),
                        node=self.invoker,
                        volume=0.8
                    ),
                )
            )

        return track

    def makeCutscene(self, delay=0.0):
        # Build the cutscene.
        cutsceneLoader = CutsceneLoader.createLoader(
            key=CutsceneKeyEnum.DeepDiver_SinkOrSwim,
            invoker=self.invoker,
            battle=self.battle,
            affectsCamera=self.battle.localToonPendingOrActive()
        )
        track = cutsceneLoader.buildCutscene()

        # Return result.
        return Sequence(
            Wait(delay),
            track,
            Wait(1.0),
        )

    def getCameraShot(self, duration):
        # Handled by cutscene loader
        return Wait(duration)


@AttackClass(attackType=AttackEnum.DEEP_DIVER_PROMOTE_FODDER)
class DeepDiverPromoteFodder(Attack):
    CHEAT = True

    def doAttack(self):
        specialMan: DistributedSuitBase = self.battle.findSuit(self.extraArgs[0])

        if specialMan:
            def loopNeutralAnim():
                loopAnim = "lured" if specialMan.isLured else "neutral"
                specialMan.loop(loopAnim)

            def updateDNA():
                specialMan.setElite(1)
                specialMan.setLevel(self.extraArgs[1])
                specialMan.setMaxHp(int(specialMan.getHp() * 1.5))
                specialMan.healthBar.updateMeterMode(SuitHealthMeter.MODE_BATTLE)
                specialMan.healthBar.updateHealthBar(forceUpdate=1)

                specialMan.setDisplayName(specialMan.createNameInfo())

            def getDustCloudIval():
                dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
                dustCloud.setBillboardAxis(2.0)
                dustCloud.setZ(3)
                dustCloud.setScale(1.0)
                dustCloud.createTrack()
                return Sequence(Func(dustCloud.reparentTo, specialMan), dustCloud.track, Func(dustCloud.destroy),
                                name='dustCloudIval')

            specialManTrack = Sequence(
                Func(updateDNA),
                Parallel(
                    getDustCloudIval(),
                    Func(specialMan.showHpString, "PROMOTED!", 0.85, 0.7, (1, 1, 1, 1)),
                    ActorInterval(specialMan, 'slip-forward', startTime=2.43),
                ),
                Func(loopNeutralAnim),
            )
        else:
            return Sequence()

        return Sequence(Wait(1), specialManTrack, Wait(2.0))

    def getCameraShot(self, duration):
        return self.camera.allGroupOverheadShot(duration=duration)


@AttackClass(attackType=AttackEnum.DEEP_DIVER_DIVING_DOT)
class ToonPuddleDOT(Attack):
    OPEN_SHOT_DUR = 2.5
    CHEAT = True

    def doAttack(self):
        allToonTracks = Parallel()
        for target in self.targetDicts:
            toon = target["avatar"]

            damageDelay = 1.5 + (random.random() * 0.2)

            damageAnims = [["melt"], ["jump", 1.5, 0.4]]
            toonTrack = self.getToonTrack(
                damageDelay=damageDelay,
                splicedDamageAnims=damageAnims,
                target=target,
            )

            puddle = globalPropPool.getProp("quicksand")
            puddle.setColor(Vec4(0.15, 0.15, 1.0, 1.0))
            puddle.setHpr(Point3(120, 0, 0))
            puddle.setScale(0.01)
            puddleTrack = Sequence(
                Func(self.battle.movie.needRestoreRenderProp, puddle),
                Wait(damageDelay - 0.7),
                Func(puddle.reparentTo, self.battle),
                Func(puddle.setPos, toon.getPos(self.battle)),
                LerpScaleInterval(
                    puddle,
                    1.7,
                    Point3(1.7, 1.7, 1.7),
                    startScale=MovieUtil.PNT3_NEARZERO,
                ),
                Wait(3.2),
                LerpFunctionInterval(
                    puddle.setAlphaScale, fromData=1, toData=0, duration=0.8
                ),
                Func(MovieUtil.removeProp, puddle),
                Func(self.battle.movie.clearRenderProp, puddle),
            )
            allToonTracks.append(Parallel(
                toonTrack, puddleTrack
            ))

        return allToonTracks

    def getCameraShot(self, duration):
        return self.camera.heldShot(0.0, 3.25, 5.0, 180, -5, 0, duration=duration, name='toonPuddleDOTHeldShot')

    def getAttackDisplayName(self):
        return (
            TTLocalizer.SuitAttackNames[self.attackType][0],
            TTLocalizer.SuitAttackNames[self.attackType][1]
            % abs(self.targetDicts[0]["hp"]),
        )


@AttackClass(attackType=AttackEnum.OIL_RAIN_DOT)
class OilRainDot(ToonPuddleDOT):
    ALLOW_GROUPING = True

    def getAttackDisplayName(self):
        return ('', '')


@AttackClass(attackType=AttackEnum.BACKBURNER)
class Backburner(SuitSingleAttack):
    ANIM_NAME = "snap"
    CHEAT = True
    OPEN_SHOT_DUR = 6.0

    def doAttack(self):
        healer = self.invoker
        damageDelay = 2
        suitTrack = self.getSuitAnimTrack()
        healTracks = Parallel()

        flameDelay = 0.6
        flameDuration = 2.6
        flecksDelay = 0.6
        flecksDuration = 2.6
        vanishDelay = 1.6
        vanishDuration = 1.6

        soundTrackSnap = self.getSoundTrack(
            "SA_backburner.ogg", delay=0, node=self.invoker
        )

        for suit in self.targetObjs:
            # Figure out if this suit's hp needs to be adjusted.
            result = self.findTarget(suit.doId)
            if suit is self.invoker:
                hpAdjustTrack = Sequence(
                    Func(self.updateSuitHP, suit, result.hpAdjust, nonZero=True),
                )  
            elif result.extraArgs:
                newMaxHp = result.extraArgs[0]
                newHp = result.extraArgs[1]
                hpAdjustTrack = Sequence(
                    Func(suit.setMaxHp, newMaxHp),
                    Func(suit.setHp, newHp),
                )
            else:
                hpAdjustTrack = Sequence()

            BattleParticles.loadParticles()
            flameEffect = BattleParticles.createParticleEffect(file="backburnerBuff")
            flameEffectB = BattleParticles.createParticleEffect(file="backburnerBuff")
            flecksEffect = BattleParticles.createParticleEffect(file="backburnerSmoke")
            flameEffectB.setH(180)
            BattleParticles.setEffectTexture(flameEffect, "fire")
            BattleParticles.setEffectTexture(flameEffectB, "fire")
            BattleParticles.setEffectTexture(
                flecksEffect, "roll-o-dex", color=Vec4(0.95, 0.95, 0.95, 1)
            )
            flameTrack = self.getPartTrack(
                flameEffect, flameDelay, flameDuration, [flameEffect, suit, 0]
            )
            flameTrackB = self.getPartTrack(
                flameEffectB, flameDelay, flameDuration, [flameEffectB, suit, 0]
            )
            flecksTrack = self.getPartTrack(
                flecksEffect, flecksDelay, flecksDuration, [flecksEffect, suit, 0]
            )
            actorInterval = Sequence()
            veTrack = Func(MovieUtil.applyVisualEffect, suit, VisualEffectEnum.BACKBURNER) if suit is not self.invoker else Sequence()
            seq = Parallel(
                flameTrack,
                flameTrackB,
                flecksTrack,
                actorInterval,
                Sequence(
                    Wait(damageDelay),
                    Func(suit.hideHpText),
                    Func(suit.showHpString, "BURNED!", 0.85, 0.7, (1, 1, 1, 1)),
                    hpAdjustTrack,
                    veTrack,
                ),
                Sequence(
                    Wait(vanishDelay),
                    Parallel(
                        LerpColorScaleInterval(
                            flameEffect, vanishDuration, (1, 1, 1, 0)
                        ),
                        LerpColorScaleInterval(
                            flameEffectB, vanishDuration, (1, 1, 1, 0)
                        ),
                        LerpColorScaleInterval(
                            flecksEffect, vanishDuration, (1, 1, 1, 0)
                        ),
                    ),
                ),
            )

            healTracks.append(seq)
        sfx = loader.loadSfx("phase_11/audio/sfx/LB_toonup.ogg")
        repairSoundTrack = Sequence(Wait(damageDelay), SoundInterval(sfx, node=healer))
        return Sequence(
            Parallel(
                soundTrackSnap,
                Sequence(suitTrack, Func(healer.loop, "neutral")),
                repairSoundTrack,
                healTracks,
            )
        )

    def getCameraShot(self, duration):
        return self.camera.allGroupOverheadShot(duration=duration)


@AttackClass(attackType=AttackEnum.CASTLING)
class Castling(Attack):
    ANIM_NAME = "finger-wag"
    CHEAT = True
    DAMAGE_DELAY = 5.0

    def makeCastleCutscene(self, delay=0.0, direction='up', indicatorNode=None, rotateNode=None, overrideKey=None):
        # Build the cutscene.
        cutsceneLoader = CutsceneLoader.createLoader(
            key=overrideKey or (CutsceneKeyEnum.Prethinker_Castling_Exit if direction == 'up' else CutsceneKeyEnum.Prethinker_Castling_Enter),
            toons=self.battle.activeToons,
            prethinker=self.invoker,
            battle=self.battle,
            indicatorNode=indicatorNode,
            rotateNode=rotateNode,
        )
        track = cutsceneLoader.buildCutscene(delayDeleteToons=False)

        # Return result.
        return Sequence(
            Wait(delay),
            track,
        )

    def doAttack(self):
        if not self.targetObjs:
            return Sequence()

        suitTrack = self.getSuitAnimTrack(doActorInterval=False)
        suit = self.targetObjs[0]

        allOldSuits = [oldS for oldS in self.battle.activeSuits if not getattr(oldS, 'deadOrAboutToBe', False)]
        # Store this to get needed distance below
        oldSuitPos = {i: self.battle.getActorPosHpr(oldSuit)[0] for i, oldSuit in enumerate(allOldSuits)}

        invokerIndex = self.battle.suits.index(self.invoker)
        suitIndex = self.battle.suits.index(suit)
        # Remove invoker from the list.
        self.battle.suits.remove(self.invoker)
        # Reinsert at the other suit's index
        self.battle.suits.insert(suitIndex, self.invoker)
        # Same idea for the other suit
        self.battle.suits.remove(suit)
        self.battle.suits.insert(invokerIndex, suit)

        newSuitPos, newSuitHpr = self.battle.getActorPosHpr(suit)

        # Trap stuff
        # Attempt to get trap info
        invokerBattleTrapProp = getattr(self.invoker, "battleTrapProp", None)
        invokerBattleTrap = getattr(self.invoker, "battleTrap", BattleGlobals.NO_TRAP)
        invokerBattleTrapIsFresh = getattr(self.invoker, "battleTrapIsFresh", 0)
        suitBattleTrapProp = getattr(suit, "battleTrapProp", None)
        suitBattleTrap = getattr(suit, "battleTrap", BattleGlobals.NO_TRAP)
        suitBattleTrapIsFresh = getattr(suit, "battleTrapIsFresh", 0)

        # Swap info between the two
        self.invoker.battleTrapProp = suitBattleTrapProp
        self.invoker.battleTrap = suitBattleTrap
        self.invoker.battleTrapIsFresh = suitBattleTrapIsFresh
        suit.battleTrapProp = invokerBattleTrapProp
        suit.battleTrap = invokerBattleTrap
        suit.battleTrapIsFresh = invokerBattleTrapIsFresh

        def reparentTrapsToBattle():
            if invokerBattleTrapProp is not None and not invokerBattleTrapProp.isEmpty():
                # Reparent it to battle so it doesn't move during the anim
                invokerBattleTrapProp.wrtReparentTo(self.battle)

            if suitBattleTrapProp is not None and not suitBattleTrapProp.isEmpty():
                # Reparent it to battle so it doesn't move during the anim
                suitBattleTrapProp.wrtReparentTo(self.battle)

        def swapTraps():
            # If invoker has a trap give the other suit their trap, then vice versa.
            if invokerBattleTrapProp is not None and not invokerBattleTrapProp.isEmpty():
                MovieTrap.placeTrap(invokerBattleTrapProp, suit, invokerBattleTrap)
            if suitBattleTrapProp is not None and not suitBattleTrapProp.isEmpty():
                MovieTrap.placeTrap(suitBattleTrapProp, self.invoker, suitBattleTrap)

        adjustAllSuitsAfterSeq = Parallel()
        if self.invoker.style.name == 'ftf_l':
            # These are beefy boys so we need to make a greater effort to fix their positions.
            for i, moveSuit in enumerate([moveSuit for moveSuit in self.battle.activeSuits if not getattr(moveSuit, 'deadOrAboutToBe', False)]):
                overrideLureStatus = False if moveSuit is suit or moveSuit is self.invoker else None
                newMoveSuitPos, newMoveSuitHpr = self.battle.getActiveSuitPosHpr(moveSuit, overrideLureStatus=overrideLureStatus)
                oldMoveSuitPos = oldSuitPos[i]
                moveDist = Vec3(newMoveSuitPos - oldMoveSuitPos).length()

                # Doing it this way so that nuclear cog's glitchy effect doesn't interfere with anything
                walkInterval = ActorInterval(moveSuit, 'walk')

                suitMoveSeq = Sequence(
                    Wait(0.1),
                    Func(moveSuit.headsUp, self.battle, newMoveSuitPos),
                    Func(walkInterval.loop),
                    LerpPosInterval(moveSuit, moveDist / ToontownGlobals.SuitWalkSpeed, newMoveSuitPos, other=self.battle),
                    Func(walkInterval.finish),
                    Func(moveSuit.loop, 'lured' if moveSuit.isLured and moveSuit is not suit else 'neutral'),
                    Func(moveSuit.setHpr, self.battle, newMoveSuitHpr),
                )
                adjustAllSuitsAfterSeq.append(suitMoveSeq)
        else:
            adjustAllSuitsAfterSeq.append(Wait(0.5))

        suitWaitWalkT = {'a': 2.5, 'b': 1.65, 'c': 2.1}.get(suit.style.body, 2.1)
        adjustSuitsSeq = Parallel(
            MovieUtil.unlureSuit(suit, self.battle),
            ActorInterval(suit, 'slip-backward', playRate=1.15),
            Sequence(
                Func(suit.wrtReparentTo, self.battle),
                Parallel(
                    LerpHprInterval(suit, 1.5, hpr=(720, 0, 0), blendType='easeOut'),
                    LerpPosInterval(suit, 2.0, (0, -1, 0), blendType='easeOut')
                ),
                Wait(suitWaitWalkT),
                Func(suit.loop, 'walk'),
                Func(suit.headsUp, newSuitPos),
                LerpPosInterval(suit, 1.2, newSuitPos),
                Func(suit.setHpr, newSuitHpr),
                Func(suit.loop, 'neutral'),
                Wait(0.5),
                adjustAllSuitsAfterSeq,
            )
        )

        indicatorNode = self.battle.attachNewNode('indicator-node')
        indicatorNode.setPos(self.invoker.getPos(self.battle))
        indicatorNode.setHpr(self.invoker.getHpr(self.battle))

        newPosNode = self.battle.attachNewNode('new-pos-node')
        pX, pY, pZ = suit.getPos(self.battle)
        pH, pP, pR = suit.getHpr(self.battle)
        newPosNode.setPos(pX, pY, pZ)
        newPosNode.setHpr(pH, pP, pR)

        cameraRotateNode = self.battle.attachNewNode('camera-rotate-node')
        cameraRotateNode.setPos(newPosNode.getPos(self.battle))
        cameraRotateNode.setHpr(newPosNode.getHpr(self.battle))

        overrideKey = None
        if self.invoker.dna.name == 'ftf_l':
            overrideKey = CutsceneKeyEnum.FindTheFamily_Attorney_Castling_Exit

        castleTrackOut = self.makeCastleCutscene(direction='up', indicatorNode=indicatorNode, rotateNode=cameraRotateNode, overrideKey=overrideKey)
        castleTrackIn = self.makeCastleCutscene(direction='down', indicatorNode=newPosNode, rotateNode=cameraRotateNode)

        # If Prethinker is lured, adjust him to the unlured position after castling.
        if self.invoker.isLured:
            castleTrackIn = Sequence(
                castleTrackIn,
                MovieUtil.createSuitUnlureTrack(self.invoker, self.battle)
            )

        # This attack unlures the Prethinker and his target
        self.invoker.isLured = False
        suit.isLured = False

        return Sequence(
            MovieUtil.unlureSuit(self.invoker, self.battle),
            Func(reparentTrapsToBattle),
            Parallel(
                suitTrack,
                castleTrackOut,
                Sequence(
                    Wait(4.5),
                    Parallel(
                        castleTrackIn,
                        Sequence(
                            Wait(1.0),
                            adjustSuitsSeq,
                            Func(swapTraps),
                        ),
                    )
                )
            )
        )

    def getCameraShot(self, duration):
        # Handled by cutscene loader
        return Wait(duration)

    def getAttackDisplayName(self) -> str:
        if self.invoker.dna.name == 'prethink':
            return TTLocalizer.SuitAttackNames.get(self.attackType, "")
        else:
            return TTLocalizer.SuitAttackBonusPhrases['castling'].get(self.invoker.dna.name, "")


@AttackClass(attackType=AttackEnum.BRAIN_WAVE)
class BrainWave(SuitSingleAttack):
    ANIM_NAME = "effort"
    CHEAT = True
    OPEN_SHOT_DUR = 2.4

    def getLocalInvoker(self, index):
        if index == 0:
            return self.invoker
        else:
            suitId = self.extraArgs[index - 1]
            return self.battle.findSuit(suitId)

    def doAttack(self):
        brainstormTracks = Parallel()
        BattleParticles.loadParticles()
        totalDelay = 0.0
        for i, target in enumerate(self.targetDicts):
            totalDelay += (random.random() * 0.2)
            toon = target["avatar"]
            localInvoker = self.getLocalInvoker(i)
            snowEffect = BattleParticles.createParticleEffect("BrainStorm")
            snowEffect2 = BattleParticles.createParticleEffect("BrainStorm")
            snowEffect3 = BattleParticles.createParticleEffect("BrainStorm")
            effectColor = Vec4(0.65, 0.79, 0.93, 0.85)
            BattleParticles.setEffectTexture(
                snowEffect, "brainstorm-box", color=effectColor
            )
            BattleParticles.setEffectTexture(
                snowEffect2, "brainstorm-env", color=effectColor
            )
            BattleParticles.setEffectTexture(
                snowEffect3, "brainstorm-track", color=effectColor
            )
            cloud = globalPropPool.getProp("stormcloud")
            suitType = getSuitBodyType(localInvoker.dna.name)
            if suitType == "a":
                partDelay = 1.2
                damageDelay = 4.5
                dodgeDelay = 3.3
            elif suitType == "b":
                partDelay = 1.2
                damageDelay = 4.5
                dodgeDelay = 3.3
            elif suitType == "c":
                partDelay = 1.2
                damageDelay = 4.5
                dodgeDelay = 3.3
            if localInvoker is self.invoker:
                suitTrack = self.getSuitTrack(delay=0.9)
            else:
                toon = self.targetDicts[i]["avatar"]
                targetPos = toon.getPos(self.battle)

                trapStorage = {}
                trapStorage["trap"] = None

                def reparentTrap(suit, trapStorage):
                    trapProp = suit.battleTrapProp
                    if trapProp is not None and not trapProp.isEmpty():
                        trapProp.wrtReparentTo(self.battle)
                        trapStorage["trap"] = trapProp

                def neutralAvatar(suit):
                    if self.forceLoopNeutral:
                        suit.neutralAvatar()

                origPos, origHpr = self.battle.getActorPosHpr(localInvoker)

                def returnTrapToSuit(suit, trapStorage):
                    trapProp = trapStorage["trap"]
                    if trapProp is not None and not trapProp.isEmpty():
                        if trapProp.getName() == "traintrack":
                            self.notify.debug("deliberately not parenting traintrack to suit")
                        else:
                            trapProp.wrtReparentTo(suit)
                        suit.battleTrapProp = trapProp

                suitTrack = Sequence(
                    Wait(totalDelay),
                    self.getResetTrack(localInvoker),
                    Wait(0.9),
                    Func(reparentTrap, localInvoker, trapStorage),
                    Func(localInvoker.headsUp, self.battle, targetPos),
                    ActorInterval(localInvoker, self.getAnimName()),
                    Wait(0.01),
                    Func(neutralAvatar, localInvoker),
                    Func(localInvoker.setHpr, self.battle, origHpr),
                    Func(returnTrapToSuit, localInvoker, trapStorage)
                )
            initialCloudHeight = localInvoker.height + 3
            cloudPosPoints = [Point3(0, 3, initialCloudHeight), VBase3(180, 0, 0)]
            cloudPropTrack = Sequence()
            cloudPropTrack.append(Func(cloud.pose, "stormcloud", 0))
            cloudPropTrack.append(
                self.getPropAppearTrack(
                    cloud,
                    self.invoker if getattr(localInvoker, 'deadOrAboutToBe', False) else localInvoker,
                    cloudPosPoints,
                    1e-06,
                    Point3(3, 3, 3),
                    scaleUpTime=0.7,
                )
            )
            cloudPropTrack.append(Func(self.battle.movie.needRestoreRenderProp, cloud))
            cloudPropTrack.append(Func(cloud.wrtReparentTo, render))
            targetPoint = self.toonFacePoint(toon)
            targetPoint.setZ(targetPoint[2] + 3)
            cloudPropTrack.append(Wait(1.1))
            cloudPropTrack.append(LerpPosInterval(cloud, 1, pos=targetPoint))
            cloudPropTrack.append(Wait(partDelay))
            cloudPropTrack.append(
                Parallel(
                    ParticleInterval(
                        snowEffect, cloud, worldRelative=0, duration=2.2, cleanup=True
                    ),
                    Sequence(
                        Wait(0.5),
                        ParticleInterval(
                            snowEffect2, cloud, worldRelative=0, duration=1.7, cleanup=True
                        ),
                    ),
                    Sequence(
                        Wait(1.0),
                        ParticleInterval(
                            snowEffect3, cloud, worldRelative=0, duration=1.2, cleanup=True
                        ),
                    ),
                    Sequence(
                        ActorInterval(cloud, "stormcloud", startTime=3, duration=0.5),
                        ActorInterval(cloud, "stormcloud", startTime=2.5, duration=0.5),
                        ActorInterval(cloud, "stormcloud", startTime=1, duration=1.5),
                    ),
                )
            )
            cloudPropTrack.append(Wait(0.4))
            cloudPropTrack.append(LerpScaleInterval(cloud, 0.5, MovieUtil.PNT3_NEARZERO))
            cloudPropTrack.append(Func(MovieUtil.removeProp, cloud))
            cloudPropTrack.append(Func(self.battle.movie.clearRenderProp, cloud))
            damageAnims = [["cringe", 0.01, 0.4, 0.8], ["duck", 1e-06, 1.6]]
            toonTrack = self.getToonTrack(
                target=target,
                damageDelay=damageDelay,
                splicedDamageAnims=damageAnims,
                dodgeDelay=dodgeDelay,
                dodgeAnimNames=["sidestep"],
                showMissedExtraTime=1.1,
            )
            soundTrack = self.getSoundTrack(
                "SA_brainstorm.ogg", delay=2.6, node=localInvoker
            )
            brainstormTracks.append(Parallel(suitTrack, toonTrack, cloudPropTrack, soundTrack))

        return brainstormTracks


@AttackClass(attackType=AttackEnum.PT_BLOCK_SOUND_ENTER)
class PrethinkerBlockSoundEnter(Attack):
    def doAttack(self):
        suitIndex = self.extraArgs[0]
        invokerIndex = self.battle.activeSuits.index(self.invoker)
        direction = 'left' if invokerIndex > suitIndex else 'right'
        suitToStandBehind = self.battle.activeSuits[suitIndex]
        suitPos, suitHpr = self.battle.getActorPosHpr(suitToStandBehind)
        firstPos = Vec3(suitPos)
        firstPos[0] = self.battle.getActorPosHpr(self.invoker)[0][0]
        firstPos[1] += 5
        suitPos[1] += 5

        def fixHpr():
            if self.invoker.getH() < 0:
                self.invoker.setH(self.battle, 270)

        return Sequence(
            Func(self.invoker.loop, 'walk'),
            LerpHprInterval(self.invoker, 1.5, (0, 0, 0), other=self.battle),
            LerpPosInterval(self.invoker, 0.9, firstPos, other=self.battle),
            LerpHprInterval(self.invoker, 0.8, (90 if direction == 'right' else -90, 0, 0), other=self.battle),
            LerpPosInterval(self.invoker, 0.6 * abs(suitIndex - invokerIndex), suitPos, other=self.battle),
            Func(fixHpr),
            LerpHprInterval(self.invoker, 0.75, (180, 0, 0), other=self.battle),
            Func(self.invoker.loop, 'neutral'),
            Wait(0.8),
        )

    def getCameraShot(self, duration):
        return self.camera.allGroupOverheadShot(duration=duration)


@AttackClass(attackType=AttackEnum.PT_BLOCK_SOUND_EXIT)
class PrethinkerBlockSoundExit(Attack):
    def doAttack(self):
        suitIndex = self.extraArgs[0]
        invokerIndex = self.battle.activeSuits.index(self.invoker)
        direction = 'right' if invokerIndex > suitIndex else 'left'
        suitToStandBehind = self.battle.activeSuits[suitIndex]
        suitPos, suitHpr = self.battle.getActorPosHpr(suitToStandBehind)
        invokerPos, invokerHpr = self.battle.getActorPosHpr(self.invoker)
        firstPos = Vec3(suitPos)
        firstPos[0] = invokerPos[0]
        firstPos[1] += 5
        suitPos[1] += 5

        walkHpr = (90 if direction == 'right' else 270, 0, 0)

        return Sequence(
            Func(self.invoker.setPos, self.battle, suitPos),
            Func(self.invoker.loop, 'walk'),
            LerpHprInterval(self.invoker, 0.75, walkHpr, other=self.battle),
            LerpPosInterval(self.invoker, 0.6 * abs(suitIndex - invokerIndex), firstPos, startPos=suitPos, other=self.battle),
            LerpHprInterval(self.invoker, 0.8, (180, 0, 0), startHpr=walkHpr, other=self.battle),
            LerpPosInterval(self.invoker, 0.9, invokerPos, other=self.battle),
            Func(self.invoker.setHpr, self.battle, invokerHpr),
            Func(self.invoker.loop, 'neutral'),
            Wait(0.8),
        )

    def getCameraShot(self, duration):
        return self.camera.allGroupOverheadShot(duration=duration)


@AttackClass(attackType=AttackEnum.TRIAL_BY_FIRE)
class TrialByFire(SuitSingleAttack):
    ANIM_NAME = "magic3-alt"
    CHEAT = True
    OPEN_SHOT_DUR = 2.5

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.movieApplySeqs = {}

    def doAttack(self):
        arenaRingEffect = BattleParticles.createParticleEffect(file="trialByFireRing")
        arenaRingEffect.setZ(-10)
        ringTrack = self.getPartTrack(
            arenaRingEffect, 0.0, 4.5, [arenaRingEffect, render, 0], softStop=-1.1
        )
        arenaParticles = arenaRingEffect.getParticlesNamed("particles-1")

        def setRingLitterSize(value=1.0):
            arenaParticles.setLitterSize(int(lerp(18, 3, value)))

        fireRingSeq = Parallel(
            ringTrack,
            Sequence(
                Wait(2.64),
                LerpFunctionInterval(
                    setRingLitterSize,
                    duration=0.75,
                    fromData=0.0,
                    toData=1.0,
                    blendType="easeIn",
                ),
            ),
        )

        avgPoint = Point3(0, 0, 0)
        for target in self.targetDicts:
            toon = target["avatar"]
            avgPoint += toon.getPos(self.battle)
        avgPoint /= len(self.targetDicts)

        suitTrack = Sequence(Func(self.invoker.headsUp, avgPoint), self.getSuitTrack())
        soundTrack = self.getSoundTrack("SA_boilerplate_a.ogg", delay=1.0, node=self.invoker)
        hitSoundTrack = self.getSoundTrack("SA_boilerplate_hit.ogg", delay=3.4, node=self.invoker)

        anyHit = False

        toonTracks = Parallel()
        for target in self.targetDicts:
            toon = target["avatar"]
            dmg = target["hp"]
            if not anyHit and dmg < 0:
                anyHit = True
            BattleParticles.loadParticles()
            mainParticleEffect = BattleParticles.createParticleEffect(
                file="trialByFire"
            )
            mainParticleEffect2 = BattleParticles.createParticleEffect(
                file="trialByFire"
            )
            for particleSystem in (mainParticleEffect, mainParticleEffect2):
                particleSystem.getParticlesNamed("particles-1").setLitterSize(2)

            damageDelay = 3.6
            dodgeDelay = 0.8

            mainParticles = mainParticleEffect.getParticlesNamed("particles-1")
            mainParticles2 = mainParticleEffect2.getParticlesNamed("particles-1")

            def particleLookAt(
                value=1.0,
                toon=toon,
                particleSystem1=mainParticles,
                particleSystem2=mainParticles2,
                hitToon=False,
            ):
                toonPos = toon.getPos(render)
                if hitToon:
                    toonPos.setZ(toonPos.getZ() + toon.height / 2)
                else:
                    toonPos.setZ(0)
                handPosLeft = self.invoker.getLeftHand().getPos(render)
                handPosRight = self.invoker.getRightHand().getPos(render)
                particleSystem1.emitter.setExplicitLaunchVector(
                    (toonPos - handPosLeft) * value
                )
                particleSystem2.emitter.setExplicitLaunchVector(
                    (toonPos - handPosRight) * value
                )

            particleTime = 3.0
            partTrack = self.getPartTrack(
                mainParticleEffect,
                1.0,
                particleTime,
                [mainParticleEffect, self.invoker, 0],
                softStop=-1.1,
                renderParent=render,
            )
            partTrack2 = self.getPartTrack(
                mainParticleEffect2,
                1.0,
                particleTime,
                [mainParticleEffect2, self.invoker, 0],
                softStop=-1.1,
                renderParent=render,
            )

            partTrack = Parallel(
                LerpFunctionInterval(
                    particleLookAt,
                    duration=1.8,
                    fromData=0.0,
                    toData=1.0,
                    blendType="easeIn",
                    extraArgs=[toon, mainParticles, mainParticles2, dmg < 0],
                ),
                Sequence(
                    Func(mainParticleEffect.reparentTo, self.invoker.getLeftHand()),
                    Func(mainParticleEffect2.reparentTo, self.invoker.getRightHand()),
                    Parallel(
                        partTrack,
                        partTrack2,
                    ),
                ),
            )

            def applyVisualEffect(toon=toon):
                movieApplySeq, _ = MovieUtil.applyVisualEffect(
                    toon, VisualEffectEnum.TRIAL_BY_FIRE, useMovieApply=True
                )
                movieApplySeq.start()
                self.movieApplySeqs[toon.doId] = movieApplySeq

            def finishVisualEffectApply(toon=toon):
                movieApplySeq = self.movieApplySeqs.get(toon.doId)
                if movieApplySeq:
                    movieApplySeq.finish()
                    del self.movieApplySeqs[toon.doId]

            dodgeAnims = []
            dodgeAnims.append(["jump", 0.01, 0, 0.6])
            dodgeAnims.extend(
                self.getSplicedLerpAnims("jump", 0.31, 1.7, startTime=0.6)
            )
            dodgeAnims.append(["jump", 0, 0.91])

            hpTextType = TTLocalizer.HP_TEXT_TRIAL_BY_FIRE if dmg < 0 else None
            forceHit = (
                dmg < 0
            )  # Don't ask, I just made the movie with this in mind before it could miss
            toonTrack = self.getToonTrack(
                damageDelay=damageDelay,
                splicedDamageAnims=[],
                dodgeDelay=dodgeDelay,
                splicedDodgeAnims=dodgeAnims,
                showMissedExtraTime=1.0,
                forceHit=forceHit,
                hpTextType=hpTextType,
                target=target,
            )

            if dmg < 0:
                baseFlameEffect = BattleParticles.createParticleEffect(
                    file="firedBaseFlame"
                )
                flameEffect = BattleParticles.createParticleEffect("FiredFlame")
                flecksEffect = BattleParticles.createParticleEffect("SpriteFiredFlecks")
                BattleParticles.setEffectTexture(baseFlameEffect, "fire")
                BattleParticles.setEffectTexture(flameEffect, "fire")
                BattleParticles.setEffectTexture(
                    flecksEffect, "roll-o-dex", color=Vec4(0.95, 0.95, 0.0, 1)
                )
                flameDelay = 3.2
                flameDuration = 2.6
                flecksDelay = flameDelay + 0.8
                flecksDuration = flameDuration - 0.8
                baseFlameTrack = self.getPartTrack(
                    baseFlameEffect,
                    flameDelay,
                    flameDuration,
                    [baseFlameEffect, toon, 0],
                )
                flameTrack = self.getPartTrack(
                    flameEffect, flameDelay, flameDuration, [flameEffect, toon, 0]
                )
                flecksTrack = self.getPartTrack(
                    flecksEffect, flecksDelay, flecksDuration, [flecksEffect, toon, 0]
                )

                colorTrack = Sequence()
                colorTrack.append(Wait(4.0))

                colorTrack.append(Func(applyVisualEffect, toon))
                colorTrack.append(Wait(4.5))
                colorTrack.append(Func(finishVisualEffectApply, toon))

                toonReact = self.getToonReaction(toon=toon, delay=1.4)

                toonTracks.append(
                    Parallel(
                        toonTrack,
                        partTrack,
                        baseFlameTrack,
                        flameTrack,
                        flecksTrack,
                        colorTrack,
                        toonReact,
                    )
                )
            else:
                toonTracks.append(Parallel(toonTrack, partTrack))

        return Parallel(toonTracks, suitTrack, fireRingSeq, soundTrack, hitSoundTrack if anyHit else Sequence())

    def getToonReaction(self, toon=None, delay=0.0):
        if not toon:
            return Sequence()

        startPos = toon.getPos(self.battle)
        endPos = ((startPos - self.invoker.getPos(self.battle)) * 0.4) + startPos

        toonReact = Sequence(Wait(delay))
        toonReact.append(Func(toon.headsUp, self.invoker))
        toonReact.append(Func(toon.loop, "push"))
        toonReact.append(
            LerpPosInterval(toon, 2.0, endPos, startPos=startPos, blendType="easeIn")
        )
        toonReact.append(ActorInterval(toon, "confused"))
        toonReact.append(Func(toon.loop, "walk"))
        toonReact.append(LerpPosInterval(toon, 0.9, startPos, startPos=endPos))
        toonReact.append(Func(toon.loop, "neutral"))
        toonReact.append(Wait(1.0))

        return toonReact

    def getPartTrack(
        self,
        particleEffect,
        startDelay,
        durationDelay,
        partExtraArgs,
        softStop=0,
        renderParent=None,
    ):
        particleEffect = partExtraArgs[0]
        parent = partExtraArgs[1]
        renderParent = renderParent or parent
        if len(partExtraArgs) > 2:
            worldRelative = partExtraArgs[2]
        else:
            worldRelative = 1
        return Sequence(
            Wait(startDelay),
            ParticleInterval(
                particleEffect,
                parent,
                worldRelative,
                duration=durationDelay,
                cleanup=True,
                softStopT=softStop,
                renderParent=renderParent,
            ),
        )

    def getCameraShot(self, duration):
        for target in self.targetDicts:
            if target["avatar"].isLocal():
                toon = target["avatar"]
                break
        else:
            toon = random.choice(self.targetDicts)["avatar"]
        closeDur = duration - self.OPEN_SHOT_DUR
        openShot = self.camera.heldShot(
            -10, -10, 10, -40, -25, 0, self.OPEN_SHOT_DUR, name="trialByFireOpenShot"
        )
        closeShot = self.camera.randomActorShot(toon, self.battle, closeDur, "avatar")
        return Sequence(openShot, closeShot)


@AttackClass(attackType=AttackEnum.MOB_MENTALITY)
class MobMentality(SuitSingleAttack):
    ANIM_NAME = "magic3"
    CHEAT = True
    OPEN_SHOT_DUR = 5.0

    MOB_POSITIONS = (
        Point3(0, 30, 10),
        Point3(-30, 0, 10),
        Point3(0, -30, 10),
        Point3(30, 0, 10),

        Point3(20, 20, 10),
        Point3(20, -20, 10),
        Point3(-20, -20, 10),
        Point3(-20, 20, 10),

        Point3(0, 20, 5),
        Point3(-20, 0, 5),
        Point3(0, -20, 5),
        Point3(20, 0, 5),

        Point3(13.4, 13.4, 5),
        Point3(13.4, -13.4, 5),
        Point3(-13.4, -13.4, 5),
        Point3(-13.4, 13.4, 5),
    )

    def doAttack(self):
        mobTrack = self.makeMobCutscene()
        suitTrack = self.getSuitAnimTrack(
            doActorInterval=False, forceWait=mobTrack.getDuration() - 2.25
        )

        totalReserves = self.extraArgs[1] + len(self.getReserves())

        if totalReserves <= 3:
            musicCode = "witchhunter_battle"
        elif totalReserves <= 6:
            musicCode = "witchhunter_battle_2"
        else:
            musicCode = "witchhunter_battle_3"
        music = self.battle.instance.getPreloadedSong(musicCode)
        if musicCode != self.battle.musicPlaying:
            crossfadeFunc = Func(base.musicMgr.crossfadeIntoMusic, music, duration=1.5, matchTime=True,
                                 musicCode=musicCode)
        else:
            crossfadeFunc = Sequence()
        self.battle.musicPlaying = musicCode
        self.battle.reserves = totalReserves

        return Parallel(
            suitTrack, mobTrack,
            Sequence(
                Wait(7),
                crossfadeFunc,
            )
        )

    def makeMobCutscene(self, delay=0.0):
        # Build the cutscene.
        suits = self.targetObjs.copy()
        suits.insert(0, self.invoker)

        cutsceneLoader = CutsceneLoader.createLoader(
            key=CutsceneKeyEnum.Witchhunter_MobMentality,
            toons=self.battle.activeToons[:],
            suits=suits,
            instance=self.battle.instance,
        )
        track = cutsceneLoader.buildCutscene(delayDeleteToons=False)

        cogVoicesTrack = Parallel()
        if any([suit.style.isFemale() for suit in self.targetObjs[1:]]):
            cogVoicesTrack.append(SoundInterval(loader.loadSfx('phase_11/audio/sfx/SA_mob_mentality_cogf.ogg')))
        if any([not suit.style.isFemale() for suit in self.targetObjs[1:]]):
            cogVoicesTrack.append(SoundInterval(loader.loadSfx('phase_11/audio/sfx/SA_mob_mentality_cogm.ogg')))
        track = Sequence(Parallel(track, cogVoicesTrack))

        if len(self.extraArgs) > 2:
            reserves = self.getReserves()
            if reserves:
                rotateNode = self.battle.instance.mobRotateNode
                counterRotateNode = self.battle.instance.mobCounterRotateNode

                positions = [p for i, p in enumerate(self.MOB_POSITIONS) if i not in self.battle.instance.mobPositions.values()]

                joinSeq = Parallel()
                joinDelay = 0
                for reserve, pos in zip(reserves, positions):
                    self.battle.instance.mobPositions[reserve.doId] = self.MOB_POSITIONS.index(pos)
                    rotateNodeToUse = rotateNode if self.battle.instance.mobPositions[reserve.doId] < 8 else counterRotateNode
                    reserve.reparentTo(rotateNodeToUse)
                    reserve.hide()
                    reserve.setPos(pos)
                    reserve.dropShadow.hide()
                    reserve.headsUp(rotateNodeToUse)

                    # Handle all of the propeller/flying loop stuff.
                    reserve.flyingSeq = Sequence(
                        ActorInterval(reserve, 'landing', startFrame=10, endFrame=20, playRate=0.5),
                        ActorInterval(reserve, 'landing', startFrame=20, endFrame=10, playRate=0.5)
                    )
                    reserve.flyingSeq.loop()
                    reserve.attachPropeller()
                    lastSpinFrame = 8
                    fr = reserve.prop.getFrameRate('propeller')
                    spinTime = lastSpinFrame / fr
                    reserve.propellerInterval = ActorInterval(
                        reserve.prop, 'propeller', constrainedLoop=1, duration=spinTime)
                    reserve.propellerInterval.loop()

                    joinSeq.append(Sequence(
                        Wait(joinDelay),
                        Func(reserve.show),
                        LerpPosInterval(reserve, 1.6, pos, (pos[0], pos[1], 40)),
                    ))
                    joinDelay += 0.4

                track += Sequence(
                    Func(base.camera.setPos, Point3(-50, 0, 40)),
                    Func(base.camera.lookAt, rotateNode),
                    joinSeq,
                )

        # Return result.
        return Sequence(
            Wait(delay),
            track,
        )

    def getReserves(self) -> list:
        reserves = [base.cr.getDo(doId) for doId in self.extraArgs[2:]]
        reserves = [r for r in reserves if r]
        return reserves

    def getCameraShot(self, duration):
        # Handled by cutscene loader
        return Wait(duration)


@AttackClass(attackType=AttackEnum.BOILERPLATE)
class Boilerplate(SuitSingleAttack):
    ANIM_NAME = "magic3-alt"
    CHEAT = True
    OPEN_SHOT_DUR = 2.5

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.movieApplySeqs = {}

    def doAttack(self):
        arenaRingEffect = BattleParticles.createParticleEffect(file="trialByFireRing")
        arenaRingEffect.setZ(-10)
        ringTrack = self.getPartTrack(
            arenaRingEffect, 0.0, 4.5, [arenaRingEffect, render, 0], softStop=-1.1
        )
        arenaParticles = arenaRingEffect.getParticlesNamed("particles-1")

        def setRingLitterSize(value=1.0):
            arenaParticles.setLitterSize(int(lerp(18, 3, value)))

        fireRingSeq = Parallel(
            ringTrack,
            Sequence(
                Wait(2.64),
                LerpFunctionInterval(
                    setRingLitterSize,
                    duration=0.75,
                    fromData=0.0,
                    toData=1.0,
                    blendType="easeIn",
                ),
            ),
        )

        avgPoint = Point3(0, 0, 0)
        for target in self.targetDicts:
            toon = target["avatar"]
            avgPoint += toon.getPos(self.battle)
        avgPoint /= len(self.targetDicts)

        suitTrack = Sequence(Func(self.invoker.headsUp, avgPoint), self.getSuitTrack())
        soundTrack = self.getSoundTrack("SA_boilerplate_a.ogg", delay=1.0, node=self.invoker)
        hitSoundTrack = self.getSoundTrack("SA_boilerplate_hit.ogg", delay=3.4, node=self.invoker)

        anyHit = False

        toonTracks = Parallel()
        suitTracks = Parallel()

        extraText = TTLocalizer.GeneralAttackHpTexts[TTLocalizer.HP_TEXT_TRIAL_BY_FIRE]
        for target in self.targetDicts:
            toon = target["avatar"]
            dmg = target["hp"]
            if not anyHit and dmg < 0:
                anyHit = True

            if self.isSuit(toon):
                def loopNeutralAnim(suit):
                    loopAnim = "lured" if suit.isLured else "neutral"
                    suit.loop(loopAnim)

                suitTracks.append(Sequence(
                    Wait(4.0),
                    Func(MovieUtil.applyVisualEffect, toon, VisualEffectEnum.TRIAL_BY_FIRE),
                    Parallel(
                        (ActorInterval(toon, 'pie-small-react') if toon in self.suits else Sequence()),
                        Func(toon.showHpText, dmg, extraText=extraText[0]),
                        Func(toon.updateHealthBar, dmg),
                    ),
                    Func(loopNeutralAnim, toon),
                ))
                continue

            BattleParticles.loadParticles()
            mainParticleEffect = BattleParticles.createParticleEffect(
                file="trialByFire"
            )
            mainParticleEffect2 = BattleParticles.createParticleEffect(
                file="trialByFire"
            )
            for particleSystem in (mainParticleEffect, mainParticleEffect2):
                particleSystem.getParticlesNamed("particles-1").setLitterSize(2)

            damageDelay = 3.6
            dodgeDelay = 0.8

            mainParticles = mainParticleEffect.getParticlesNamed("particles-1")
            mainParticles2 = mainParticleEffect2.getParticlesNamed("particles-1")

            def particleLookAt(
                value=1.0,
                toon=toon,
                particleSystem1=mainParticles,
                particleSystem2=mainParticles2,
                hitToon=False,
            ):
                toonPos = toon.getPos(render)
                if hitToon:
                    toonPos.setZ(toonPos.getZ() + toon.height / 2)
                else:
                    toonPos.setZ(0)
                handPosLeft = self.invoker.getLeftHand().getPos(render)
                handPosRight = self.invoker.getRightHand().getPos(render)
                particleSystem1.emitter.setExplicitLaunchVector(
                    (toonPos - handPosLeft) * value
                )
                particleSystem2.emitter.setExplicitLaunchVector(
                    (toonPos - handPosRight) * value
                )

            particleTime = 3.0
            partTrack = self.getPartTrack(
                mainParticleEffect,
                1.0,
                particleTime,
                [mainParticleEffect, self.invoker, 0],
                softStop=-1.1,
                renderParent=render,
            )
            partTrack2 = self.getPartTrack(
                mainParticleEffect2,
                1.0,
                particleTime,
                [mainParticleEffect2, self.invoker, 0],
                softStop=-1.1,
                renderParent=render,
            )

            partTrack = Parallel(
                LerpFunctionInterval(
                    particleLookAt,
                    duration=1.8,
                    fromData=0.0,
                    toData=1.0,
                    blendType="easeIn",
                    extraArgs=[toon, mainParticles, mainParticles2, dmg < 0],
                ),
                Sequence(
                    Func(mainParticleEffect.reparentTo, self.invoker.getLeftHand()),
                    Func(mainParticleEffect2.reparentTo, self.invoker.getRightHand()),
                    Parallel(
                        partTrack,
                        partTrack2,
                    ),
                ),
            )

            def applyVisualEffect(toon=toon):
                movieApplySeq, _ = MovieUtil.applyVisualEffect(
                    toon, VisualEffectEnum.TRIAL_BY_FIRE, useMovieApply=True
                )
                movieApplySeq.start()
                self.movieApplySeqs[toon.doId] = movieApplySeq

            def finishVisualEffectApply(toon=toon):
                movieApplySeq = self.movieApplySeqs.get(toon.doId)
                if movieApplySeq:
                    movieApplySeq.finish()
                    del self.movieApplySeqs[toon.doId]

            dodgeAnims = []
            dodgeAnims.append(["jump", 0.01, 0, 0.6])
            dodgeAnims.extend(
                self.getSplicedLerpAnims("jump", 0.31, 1.7, startTime=0.6)
            )
            dodgeAnims.append(["jump", 0, 0.91])

            hpTextType = TTLocalizer.HP_TEXT_TRIAL_BY_FIRE if dmg < 0 else None
            forceHit = (
                dmg < 0
            )  # Don't ask, I just made the movie with this in mind before it could miss
            toonTrack = self.getToonTrack(
                damageDelay=damageDelay,
                splicedDamageAnims=[],
                dodgeDelay=dodgeDelay,
                splicedDodgeAnims=dodgeAnims,
                showMissedExtraTime=1.0,
                forceHit=forceHit,
                hpTextType=hpTextType,
                target=target,
            )

            if dmg < 0:
                baseFlameEffect = BattleParticles.createParticleEffect(
                    file="firedBaseFlame"
                )
                flameEffect = BattleParticles.createParticleEffect("FiredFlame")
                flecksEffect = BattleParticles.createParticleEffect("SpriteFiredFlecks")
                BattleParticles.setEffectTexture(baseFlameEffect, "fire")
                BattleParticles.setEffectTexture(flameEffect, "fire")
                BattleParticles.setEffectTexture(
                    flecksEffect, "roll-o-dex", color=Vec4(0.95, 0.95, 0.0, 1)
                )
                flameDelay = 3.2
                flameDuration = 2.6
                flecksDelay = flameDelay + 0.8
                flecksDuration = flameDuration - 0.8
                baseFlameTrack = self.getPartTrack(
                    baseFlameEffect,
                    flameDelay,
                    flameDuration,
                    [baseFlameEffect, toon, 0],
                )
                flameTrack = self.getPartTrack(
                    flameEffect, flameDelay, flameDuration, [flameEffect, toon, 0]
                )
                flecksTrack = self.getPartTrack(
                    flecksEffect, flecksDelay, flecksDuration, [flecksEffect, toon, 0]
                )

                colorTrack = Sequence()
                colorTrack.append(Wait(4.0))

                colorTrack.append(Func(applyVisualEffect, toon))
                colorTrack.append(Wait(4.5))
                colorTrack.append(Func(finishVisualEffectApply, toon))

                toonReact = self.getToonReaction(toon=toon, delay=1.4)

                toonTracks.append(
                    Parallel(
                        toonTrack,
                        partTrack,
                        baseFlameTrack,
                        flameTrack,
                        flecksTrack,
                        colorTrack,
                        toonReact,
                    )
                )
            else:
                toonTracks.append(Parallel(toonTrack, partTrack))

        return Parallel(toonTracks, suitTrack, suitTracks, fireRingSeq, soundTrack, hitSoundTrack if anyHit else Sequence())

    def getToonReaction(self, toon=None, delay=0.0):
        if not toon:
            return Sequence()

        startPos = toon.getPos(self.battle)
        endPos = ((startPos - self.invoker.getPos(self.battle)) * 0.4) + startPos

        toonReact = Sequence(Wait(delay))
        toonReact.append(Func(toon.headsUp, self.invoker))
        toonReact.append(Func(toon.loop, "push"))
        toonReact.append(
            LerpPosInterval(toon, 2.0, endPos, startPos=startPos, blendType="easeIn")
        )
        toonReact.append(ActorInterval(toon, "confused"))
        toonReact.append(Func(toon.loop, "walk"))
        toonReact.append(LerpPosInterval(toon, 0.9, startPos, startPos=endPos))
        toonReact.append(Func(toon.loop, "neutral"))
        toonReact.append(Wait(1.0))

        return toonReact

    def getPartTrack(
        self,
        particleEffect,
        startDelay,
        durationDelay,
        partExtraArgs,
        softStop=0,
        renderParent=None,
    ):
        particleEffect = partExtraArgs[0]
        parent = partExtraArgs[1]
        renderParent = renderParent or parent
        if len(partExtraArgs) > 2:
            worldRelative = partExtraArgs[2]
        else:
            worldRelative = 1
        return Sequence(
            Wait(startDelay),
            ParticleInterval(
                particleEffect,
                parent,
                worldRelative,
                duration=durationDelay,
                cleanup=True,
                softStopT=softStop,
                renderParent=renderParent,
            ),
        )

    def getCameraShot(self, duration):
        for target in self.targetDicts:
            if target["avatar"].isLocal():
                toon = target["avatar"]
                break
        else:
            toon = random.choice(self.targetDicts)["avatar"]
        closeDur = duration - self.OPEN_SHOT_DUR
        openShot = self.camera.heldShot(
            -10, -10, 10, -40, -25, 0, self.OPEN_SHOT_DUR, name="trialByFireOpenShot"
        )
        closeShot = self.camera.randomActorShot(toon, self.battle, closeDur, "avatar")
        return Sequence(openShot, closeShot)


@AttackClass(attackType=AttackEnum.PICK_UP_THE_PACE)
class PickUpThePace(SuitSingleAttack):
    ANIM_NAME = "come-on"
    CHEAT = True
    OPEN_SHOT_DUR = 5.0
    SHOW_PLAY_BY_PLAY = False

    def doAttack(self):
        suitTrackSfx = Sequence(self.suitSfxTrack, Func(self.invoker.loop, "neutral"))
        speedupMusic = self.getSpeedTrack()
        suitTrack = self.getSuitAnimTrack(doActorInterval=False, forceWait=3.0)
        return Parallel(suitTrackSfx, speedupMusic, suitTrack)

    @property
    def suitSfxTrack(self):
        suitTrack = Sequence()
        sfx = Sequence()
        return Sequence(suitTrack, sfx)

    def getSpeedTrack(self) -> Sequence:
        timescale = self.extraArgs[0] / 100
        oldSpeed = self.currentPlaybackSpeed
        newSpeed = math.pow(timescale, 0.16)
        if timescale < 1:
            newSpeed = timescale

        if self.bml.storedMusic is None:
            self.bml.lookForSuits(self.battle.suits, None)

        return Sequence(
            Func(messenger.send, 'SuitAttack-PickUpThePace-changePlaybackSpeed', [self.extraArgs]),
            Func(self.bml.changePlaybackSpeed, newSpeed, duration=(3.0 / oldSpeed))
        )

    def getCameraShot(self, duration):
        cutsceneLoader = CutsceneLoader.createLoader(
            key=CutsceneKeyEnum.Pacesetter_PickUpThePace,
            toons=self.battle.activeToons,
            pacesetter=self.invoker,
            battle=self.battle,
            newSpeed=self.extraArgs[0] / 100,
            oldSpeed=self.extraArgs[1] / 100,
        )
        return cutsceneLoader.buildCutscene()

    @property
    def bml(self):
        return self.battle.battleMusicListener

    @property
    def currentPlaybackSpeed(self):
        return self.bml.currentPlayback


@AttackClass(attackType=AttackEnum.OVERCLOCKED)
class Overclocked(PickUpThePace):
    ANIM_NAME = "overclocked"

    def getCameraShot(self, duration):
        # Handled by cutscene loader
        return Wait(duration)

    @property
    def suitSfxTrack(self):
        # Load in cutscene
        cutsceneLoader = CutsceneLoader.createLoader(
            key=CutsceneKeyEnum.Pacesetter_GuitarSolo,
            toons=self.battle.activeToons[:],
            suit=self.invoker,
            battle=self.battle
        )
        cutsceneTrack = cutsceneLoader.buildCutscene()

        # Music Track
        if self.bml.storedMusic is None:
            self.bml.lookForSuits(self.battle.suits, None)
        pauseA = 0.1
        slowdownDuration = 1.5
        musicDelay = -4.0
        slowdownTrack = Sequence(
            Wait(pauseA),
            Func(self.bml.changePlaybackSpeed, 0.001, slowdownDuration),
            Wait(slowdownDuration),
            Func(self.bml.stopMusic),
            Func(self.bml.changePlaybackSpeed, 1.0, 0.0),
            Wait(cutsceneTrack.getDuration() - pauseA - slowdownDuration + musicDelay),
            Func(self.bml.playMusic, None, None, 1.0, 'pacesetter_final', 1.0),
            # Clock Track
            CutsceneLoader.createLoader(key=CutsceneKeyEnum.Pacesetter_OverclockedGUI, oldSpeed=1.0).buildCutscene(),
        )

        # Timescale update
        timescaleFunc = Func(messenger.send, self.battle.msg_updateTimescale, [1.0])

        return Parallel(cutsceneTrack, slowdownTrack, timescaleFunc)

    def getSpeedTrack(self) -> Sequence:
        return Sequence()


@AttackClass(attackType=AttackEnum.FORWARD_THINKING)
class ForwardThinking(SuitSingleAttack):
    ANIM_NAME = "magic3"
    CHEAT = True
    OPEN_SHOT_DUR = 5.0

    def doAttack(self):
        music = None
        instance = getattr(base, 'instance', None)
        if instance:
            music = instance.getPreloadedSong('prethinker_battle_forward')
        if music is None:
            music = loader.loadMusic('phase_X/audio/bgm/prethinker_battle_forward.ogg')
        suitTrack = self.getSuitAnimTrack(doActorInterval=False)
        cutsceneLoader = CutsceneLoader.createLoader(
            key=CutsceneKeyEnum.Prethinker_ForwardThinking,
            toons=self.battle.activeToons,
            prethinker=self.invoker,
            battle=self.battle,
        )
        return Parallel(
            cutsceneLoader.buildCutscene(),
            suitTrack,
            Func(base.musicMgr.crossfadeIntoMusic, music, duration=1.0, looping=True, matchTime=True, musicCode='prethinker_battle_forward')
        )

    def getCameraShot(self, duration):
        # Handled by cutscene editor
        return Sequence(Wait(duration))


@AttackClass(attackType=AttackEnum.SLUSH_FUND)
class SlushFund(SuitSingleAttack):
    """Lovingly plagiarized from Backburner."""
    ANIM_NAME = "mob-mentality"
    CHEAT = True
    OPEN_SHOT_DUR = 6.0

    def doAttack(self):

        suitTrack = self.getSuitAnimTrack()
        fundTracks = Parallel()
        fundSfxTrack = self.getSoundTrack(
            "SA_life_insurance_register.ogg", delay=0, node=self.invoker
        )
        invokerSfxTrack = self.getSoundTrack(
            "SA_extra_tip.ogg", delay=0, node=self.invoker
        )

        damageDelay = 2
        dollarDelay = 0.6
        dollarDuration = 2.6
        vanishDelay = 1.6
        vanishDuration = 1.6

        for suit in self.targetObjs:
            BattleParticles.loadParticles()
            dollarEffect = BattleParticles.createParticleEffect(file="backburnerBuff")
            dollarEffectB = BattleParticles.createParticleEffect(file="backburnerBuff")
            dollarEffectB.setH(180)
            BattleParticles.setEffectTexture(dollarEffect, "dollar-sign", color=(.5 * random.random() + .3, .8, 1, 1))
            BattleParticles.setEffectTexture(dollarEffectB, "dollar-sign", color=(.5 * random.random() + .3, .8, 1, 1))

            dollarTrack = self.getPartTrack(
                dollarEffect, dollarDelay, dollarDuration, [dollarEffect, suit, 0]
            )
            dollarTrackB = self.getPartTrack(
                dollarEffectB, dollarDelay, dollarDuration, [dollarEffectB, suit, 0]
            )
            actorInterval = Sequence()
            seq = Parallel(
                dollarTrack,
                dollarTrackB,
                actorInterval,
                invokerSfxTrack,
                Sequence(
                    Wait(damageDelay),
                    Func(suit.hideHpText),
                    Parallel(
                        fundSfxTrack,
                        Func(suit.showHpString, "FUNDED!", 0.85, 0.7, (1, 1, 1, 1)),
                        Func(MovieUtil.applyVisualEffect, suit, VisualEffectEnum.SLUSH_FUND)
                    )

                ),
                Sequence(
                    Wait(vanishDelay),
                    Parallel(
                        LerpColorScaleInterval(
                            dollarEffect, vanishDuration, (1, 1, 1, 0)
                        ),
                        LerpColorScaleInterval(
                            dollarEffectB, vanishDuration, (1, 1, 1, 0)
                        ),
                    ),
                ),
            )
            fundTracks.append(seq)

        suitTrack = Sequence(suitTrack, Func(self.invoker.loop, "neutral"))
        return Parallel(suitTrack, fundTracks)

    def getAttackDisplayName(self):
        """
        Slush Fund can get used by Investors so we need to account for that.
        """
        nameInfo = super().getAttackDisplayName()

        # Insert the invoker's name into the description.
        return nameInfo[0], nameInfo[1] % TTLocalizer.suitName(self.invoker.dna.name)


@AttackClass(attackType=AttackEnum.DEEP_FREEZE)
class DeepFreeze(SuitGroupAttack):
    ANIM_NAME = "magic3"
    CHEAT = True
    OPEN_SHOT_DUR = 1.6

    def doAttack(self):
        overallDelay = 0.5
        suitTrack = self.getSuitAnimTrack(delay=overallDelay)

        BattleParticles.loadParticles()
        particleEffect = BattleParticles.createParticleEffect("Withdrawal")
        BattleParticles.setEffectTexture(particleEffect, "snow-particle")

        withdrawalNode = self.battle.attachNewNode('deepFreeze-withdrawalNode')
        withdrawalNode.setPos(0, 8, -1)
        withdrawalNode.setH(180)
        partTrack = Sequence(
            self.getPartTrack(particleEffect, overallDelay + 0.5, suitTrack.getDuration() + 1.7,
                               [particleEffect, withdrawalNode, 0], softStop=-1.0),
            Wait(0.1),
            Func(withdrawalNode.removeNode),
        )

        def changeColor(parts):
            track = Parallel()
            for nextPart in parts:
                track.append(
                    LerpColorScaleInterval(
                        nextPart,
                        duration=4.0,
                        colorScale=Vec4(51 / 255, 255 / 255, 255 / 255, 1.0),
                    )
                )

            return track

        def resetColor(parts):
            track = Parallel()
            for nextPart in parts:
                track.append(Func(nextPart.clearColorScale))

            return track

        soundTrack = self.getSoundTrack(
            "SA_withdrawl.ogg", delay=overallDelay + 1.4, node=self.invoker
        )
        snowSoundTrack = self.getSoundTrack(
            "phase_10/audio/sfx/SA_deepfreeze.ogg", delay=overallDelay + 1.2, node=self.invoker, duration=3.0
        )

        toonTracks = Parallel()
        for target in self.targetDicts:
            # Get Toon Info
            toon = target["avatar"]
            headParts = toon.getHeadParts()
            torsoParts = toon.getTorsoParts()
            legsParts = toon.getLegsParts()

            # Toon Reaction
            reactionTrack = Sequence()
            reactionTrack.append(
                Func(toon.headsUp, self.battle, self.invoker.getPos(self.battle))
            )
            reactionTrack.append(Wait(overallDelay + 1.6))
            reactionTrack.append(ActorInterval(toon, "cringe", playRate=0.4))
            reactionTrack.append(Func(toon.loop, "neutral"))

            particleEffect = BattleParticles.loadParticleFile('plutocratDeepFreeze.ptf')
            particleNode = toon.attachNewNode('deepFreeze-particleNode')
            particleNode.setZ(-3.0)
            particleTrack = self.getPartTrack(particleEffect, overallDelay + 1.6, 4.0,
                                              [particleEffect, particleNode, 0], softStop=-2.0)

            def adjustRadius(value, particleEffect=particleEffect):
                particleEffect.getParticlesList()[0].emitter.setRadius(lerp(0.2, 0.4, value))

            particleTrack = Parallel(
                Sequence(
                    Wait(overallDelay + 1.6),
                    LerpFunc(adjustRadius, duration=0.5, fromData=0.0, toData=1.0, blendType='easeIn'),
                    LerpFunc(adjustRadius, duration=0.5, fromData=1.0, toData=0.0, blendType='easeOut'),
                    LerpFunc(adjustRadius, duration=0.5, fromData=0.0, toData=1.0, blendType='easeIn'),
                    LerpFunc(adjustRadius, duration=0.5, fromData=1.0, toData=0.0, blendType='easeOut')
                ),
                Sequence(
                    particleTrack,
                    Wait(0.1),
                    Func(particleNode.removeNode)
                )
            )

            # Color
            colorTrack = Sequence()
            colorTrack.append(Wait(overallDelay + 1.6))
            colorTrack.append(Func(self.battle.movie.needRestoreColor))
            colorTrack.append(
                Parallel(
                    changeColor(headParts),
                    changeColor(torsoParts),
                    changeColor(legsParts),
                )
            )
            colorTrack.append(Wait(1.4))
            # colorTrack.append(resetColor(headParts))
            # colorTrack.append(resetColor(torsoParts))
            # colorTrack.append(resetColor(legsParts))
            colorTrack.append(
                Func(MovieUtil.applyVisualEffect, toon, VisualEffectEnum.DEEP_FREEZE)
            )
            colorTrack.append(Func(self.battle.movie.clearRestoreColor))

            toonTracks.append(Parallel(reactionTrack, colorTrack, particleTrack))

        cutsceneLoader = CutsceneLoader.createLoader(
            key=CutsceneKeyEnum.Plutocrat_DeepFreeze_Camera,
            plutocrat=self.invoker,
            battle=self.battle,
        )
        cameraTrack = cutsceneLoader.buildCutscene()
        return Parallel(suitTrack, partTrack, toonTracks, soundTrack, snowSoundTrack, cameraTrack)

    def getCameraShot(self, duration):
        # Handled by Cutscene Loader
        return Sequence(Wait(duration))


@AttackClass(attackType=AttackEnum.OFFBOARDING)
class Offboarding(SuitSingleAttack):
    CHEAT = True

    def doAttack(self):
        suit, toon = self.targetObjs

        cutscene = CutsceneLoader.createLoader(
            CutsceneKeyEnum.ChainsawConsultant_Offboarding,
            toons=[toon],
            suits=[suit],
            battle=self.battle,
            taunt=self.getAttackTaunt(),
            chainsaw=self.invoker,
        ).buildCutscene()

        tdict = self.targetDicts[1]

        return Parallel(
            cutscene,
            Sequence(Wait(6), Func(self.doDamage, toon, tdict["hp"], tdict["died"]))
        )

    def getEndTrack(self):
        return Sequence()

    def getCameraShot(self, duration):
        return Sequence(Wait(duration))


@AttackClass(attackType=AttackEnum.LAYOFFS)
class Layoffs(SuitSingleAttack):
    CHEAT = True
    
    def doAttack(self):
        cutscene = CutsceneLoader.createLoader(
            CutsceneKeyEnum.ChainsawConsultant_Layoffs,
            suits=self.targetObjs[len(self.targetObjs) // 2:],
            toons=self.targetObjs[:len(self.targetObjs) // 2],
            battle=self.battle,
            chainsaw=self.invoker,
            taunt=self.getAttackTaunt(),
        ).buildCutscene()

        return Parallel(
            cutscene,
            Sequence(
                Wait(5.35),
                Parallel(
                    *[Func(self.doDamage, td["avatar"], td["hp"], td["died"])
                      for td in self.targetDicts if td["avatar"].isToon()]
                )
            )
        )

    def getCameraShot(self, duration):
        return Sequence(Wait(duration))

    def getEndTrack(self):
        return Sequence()


@AttackClass(attackType=AttackEnum.REVVING_UP)
class RevvingUp(SuitSingleAttack):
    CHEAT = True

    def getChainsawTexRollDur(self, stacks: int) -> float:
        return max(1.6 - (0.075 * stacks), 0.1)

    def doAttack(self):
        cutscene = CutsceneLoader.createLoader(
            key=CutsceneKeyEnum.ChainsawConsultant_RevvedUp,
            toons=self.toons,
            suits=[suit for suit in self.suits if suit is not self.invoker],
            chainsaw=self.invoker,
            battle=self.battle,
            taunt=self.getAttackTaunt(),
        ).buildCutscene()

        # Get the cycle duration.
        duration = self.getChainsawTexRollDur(sum(self.extraArgs))
        return Parallel(
            cutscene,
            LerpFunc(
                self.invoker.specialHead.setChainsawTexRoll, 
                2, 
                self.getChainsawTexRollDur(self.extraArgs[1]),
                duration,
                blendType='easeInOut'
            ),
            Sequence(
                Wait(1.0),
                Func(messenger.send, ChainsawMeterGUI.getRPMDeltaEvent(), [int(self.extraArgs[0] + self.extraArgs[2])]),
            )
        )
    
    def getAttackDisplayName(self) -> str:
        title, desc = super().getAttackDisplayName()
        desc = desc % f'{self.extraArgs[0]*1000:,}'
        if self.extraArgs[2]:
            desc += f'\n(WHIPSAW: +{self.extraArgs[2]*1000:,} RPM)'
        return title, desc

    def getCameraShot(self, duration):
        # Handled by cutscene editor
        return Sequence(Wait(duration))


@AttackClass(attackType=AttackEnum.WASTEFUL_MGMT)
class WastefulManagement(SuitSingleAttack):
    ANIM_NAME = "effort"
    CHEAT = True
    OPEN_SHOT_DUR = 5.0

    def doAttack(self):
        # Set this flag to true so that the funny extra animation will play when the suits join
        self.battle.wantStandardReserveJoinAnim = True

        cutsceneLoader = CutsceneLoader.createLoader(
            key=CutsceneKeyEnum.Multislacker_WastefulManagement,
            multislacker=self.invoker,
            battle=self.battle,
        )

        suitTrack = self.getSuitAnimTrack(doActorInterval=False)
        return Parallel(suitTrack, cutsceneLoader.buildCutscene(), Wait(6.0))

    def getCameraShot(self, duration):
        # Handled by cutscene editor
        return Sequence(Wait(duration))


@AttackClass(attackType=AttackEnum.HYPER_TASK)
class HyperTask(SuitSingleAttack):
    ANIM_NAME = "effort"
    CHEAT = True
    OPEN_SHOT_DUR = 6.0

    def doAttack(self):
        suitTrack = self.getSuitAnimTrack()
        sfx = self.getSoundTrack("phase_9/audio/sfx/SA_hypertask.ogg", delay=3.5, node=self.invoker)
        effectTrack = Sequence(
            Wait(3.7),
            Func(MovieUtil.applyVisualEffect, self.invoker, VisualEffectEnum.AFTERIMAGE),
            Wait(suitTrack.getDuration() - 3.7),
            Func(MovieUtil.unapplyVisualEffect, self.invoker, VisualEffectEnum.AFTERIMAGE, wantApplyLock=True)
        )
        return Parallel(effectTrack, suitTrack, sfx)


@AttackClass(attackType=AttackEnum.ZERO_TASK)
class ZeroTask(SuitSingleAttack):
    ANIM_NAME = "throw-paper"
    CHEAT = True
    OPEN_SHOT_DUR = 7.0

    def doAttack(self):
        healer = self.invoker
        damageDelay = 4.8
        suitTrack = self.getSuitAnimTrack()
        healTracks = Parallel()

        sandwichModel = loader.loadModel("phase_6/models/golf/picnic_sandwich.bam")
        sandwichModel.setScale(2)
        sandwiches = []

        def updateSuitHP(suit, response, heal):
            suit.updateHealthBar(heal)
            if heal != 0:
                suit.showHpText(heal)

            if suit is not self.invoker:
                suit.setChatAbsolute(response, CFSpeech | CFTimeout)

        def removeSandwiches():
            for sandwich in sandwiches:
                sandwich.removeNode()
            sandwichModel.removeNode()

        for i, result in enumerate(self.targets):
            suitId = result.avId
            suit = self.battle.findSuit(suitId)
            sandwich = sandwichModel.copyTo(healer.getRightHand())
            sandwich.setScale(0.01)
            sandwich.setPos(0.3, 0, -0.3)
            sandwiches.append(sandwich)
            endPos = (0, 0, suit.height + 3)
            scaleSeq = LerpScaleInterval(sandwich, duration=1, scale=2.0)
            pInterval = Sequence(
                Func(sandwich.wrtReparentTo, suit),
                Parallel(
                    ProjectileInterval(
                        sandwich, duration=1.65, endPos=endPos, gravityMult=0.4
                    ),
                    LerpHprInterval(sandwich, 1.65, (180, 90, 180)),
                ),
            )
            endScaleSeq = LerpScaleInterval(sandwich, duration=0.55, scale=0.01)
            fallInterval = LerpPosInterval(sandwich, 0.65, (0, 0, suit.height / 2))

            seq = Sequence(
                scaleSeq,
                Wait(47/24),
                Sequence(pInterval, Parallel(endScaleSeq, fallInterval)),
                Func(
                    updateSuitHP,
                    suit,
                    self.getRandomHealResponse(self.extraArgs[i]),
                    result.hpAdjust,
                )
            )

            healTracks.append(seq)
            if suit.specialHead:
                def setHeadP(value, suit=suit):
                    suit.specialHead.setP(value)

                headTrack = Sequence(
                    Wait(3.4),
                    LerpFunctionInterval(setHeadP, fromData=0, toData=30, duration=0.5, blendType='easeInOut', extraArgs=[suit]),
                    Wait(1.5),
                    LerpFunctionInterval(setHeadP, fromData=30, toData=0, duration=0.5, blendType='easeInOut', extraArgs=[suit]),
                )
                healTracks.append(headTrack)

                headAnimTrack = Sequence(
                    Wait(2.5),
                    ActorInterval(suit.specialHead, 'grunt', endFrame=5),
                    Func(suit.specialHead.pose, 'grunt', 5),
                    Wait(2.0),
                    ActorInterval(suit.specialHead, 'grunt', startFrame=5),
                    Func(suit.specialHead.loopNeutral),
                )
                healTracks.append(headAnimTrack)

        tipSfx = self.getSoundTrack("SA_extra_tip.ogg", delay=0, node=self.invoker)
        sfx = loader.loadSfx("phase_11/audio/sfx/LB_toonup.ogg")
        repairSoundTrack = Sequence(Wait(damageDelay), SoundInterval(sfx, node=healer))
        return Sequence(
            Parallel(
                Sequence(suitTrack, Func(healer.loop, "neutral")),
                repairSoundTrack,
                healTracks,
                Sequence(
                    Wait(2.5),
                    tipSfx,
                ),
            ),
            Func(removeSandwiches),
        )

    @staticmethod
    def getRandomHealResponse(num: int) -> str:
        # >:(
        if num == 0:
            return TTLocalizer.MultislackerResponseBruh

        # How much do they like it?
        return TTLocalizer.MultislackerResponsesGreat[int(num % len(TTLocalizer.MultislackerResponsesGreat))]


@AttackClass(attackType=AttackEnum.MANDATORY_LUNCH)
class MandatoryLunch(SuitSingleAttack):
    ANIM_NAME = "magic2"
    CHEAT = True
    OPEN_SHOT_DUR = 5.0

    def doAttack(self):
        lunchTrack = self.makeLunchCutscene()

        return Parallel(lunchTrack, Func(self.battle.instance.changeTVScreen))

    def makeLunchCutscene(self, delay=0.0):
        # Build the cutscene.
        from toontown.suit import Suit, SuitDNA, SuitHealthMeter
        fakeSuit = Suit.Suit()
        suitDNA = SuitDNA.SuitDNA()
        suitDNA.newSuit('mslacker')

        fakeSuit.setDNA(suitDNA)
        fakeSuit.loop('neutral')
        fakeSuit.addActive()
        fakeSuit.hide()
        fakeSuit.setPos(self.invoker.getPos(render))
        fakeSuit.setHpr(self.invoker.getHpr(render))

        def updateFakeHpBar():
            fakeSuit.hp = self.invoker.getHp()
            fakeSuit.maxHp = self.invoker.getMaxHp()
            fakeSuit.getHp = lambda: fakeSuit.hp
            fakeSuit.getMaxHp = lambda: fakeSuit.maxHp
            fakeSuit.healthInitialized = True
            fakeSuit.healthBar.updateMeterMode(SuitHealthMeter.MODE_BATTLE)
            fakeSuit.healthBar.updateHealthBar(forceUpdate=1)

        updateFakeHpBar()
        fakeSuit.getActualLevel = lambda: self.invoker.getActualLevel()
        fakeSuit.getStyleDept = lambda: self.invoker.getStyleDept()
        fakeSuit.setDisplayName(self.invoker.nametag.getDisplayName())
        fakeSuit.setPickable(0)

        cutsceneLoader = CutsceneLoader.createLoader(
            key=CutsceneKeyEnum.Multislacker_MandatoryLunch_Start,
            multislacker=fakeSuit,
            battle=self.battle
        )
        track = cutsceneLoader.buildCutscene()

        music = base.instance.getPreloadedSong('multislacker_battle_foreman')
        musicTrack = Func(
            base.musicMgr.crossfadeIntoMusic, music, 5.0, 0.5, 1, True, 1.0, 'multislacker_battle_foreman'
        )

        # Return result.
        return Parallel(
            musicTrack,
            Sequence(
                Wait(delay),
                Func(fakeSuit.setChatAbsolute, self.getAttackTaunt(), CFSpeech | CFTimeout),
                Wait(3.5),
                Func(fakeSuit.clearChat),
            ),
            Sequence(
                Wait(delay),
                Func(camera.wrtReparentTo, render),
                Func(self.invoker.hide),
                Func(updateFakeHpBar),
                Func(fakeSuit.show),
                Func(fakeSuit.reparentTo, render),
                track,
                Func(MovieUtil.applyVisualEffect, self.invoker, VisualEffectEnum.MANDATORY_LUNCH_MSLACKER),
                Func(camera.wrtReparentTo, self.battle),
            )
        )

    def getCameraShot(self, duration):
        # Handled by cutscene loader
        return Wait(duration)


@AttackClass(attackType=AttackEnum.UNION_BUST)
class UnionBust(SuitSingleAttack):
    ANIM_NAME = "quick-jump"
    CHEAT = True
    OPEN_SHOT_DUR = 3.0

    def doAttack(self):
        suits = []
        for suit in self.battle.activeSuits:
            if suit.style.name in ('mslacker', 'msfore'):
                continue
            elif not getattr(suit, 'deadOrAboutToBe', False):
                suits.append(suit)

        suits.insert(0, self.invoker)

        cutsceneLoader = CutsceneLoader.createLoader(
            key=CutsceneKeyEnum.Multislacker_Foreman_UnionBust,
            toons=self.battle.activeToons,
            suits=suits,
            battle=self.battle,
        )

        suitTrack = self.getSuitAnimTrack(doActorInterval=False)
        return Parallel(suitTrack, cutsceneLoader.buildCutscene())

    def getEndTrack(self):
        return Sequence()

    def getCameraShot(self, duration):
        # Handled by cutscene editor
        return Sequence(Wait(duration))


@AttackClass(attackType=AttackEnum.HEALING_BELL)
class HealingBell(SuitSingleAttack):
    ANIM_NAME = "quick-jump"
    CHEAT = True
    OPEN_SHOT_DUR = 1.5
    particleFrames = [
        13,
        26,
        46,
        66,
        82,
    ]

    def doAttack(self):
        suitTrack = self.getSuitAnimTrack(
            doActorInterval=False, wantSpeechHeadAnim=False, forceWait=4.5
        )
        soundTrack = self.getSoundTrack("SA_healing_bell.ogg")

        particleTrack = Parallel()
        for frameNum in self.particleFrames:
            ringEffect = BattleParticles.createParticleEffect(
                file="healingBellRingWave"
            )
            ringEffect.setDepthWrite(0)
            ringEffect.setDepthTest(0)
            ringEffect.setTwoSided(1)

            particleSeq = Sequence(
                Func(
                    ringEffect.setPos,
                    self.invoker,
                    Point3(0, 0, self.invoker.getHeight() - 1),
                ),
                Wait(frameNum / 24.0),
                self.getPartTrack(
                    ringEffect,
                    0,
                    3.0,
                    [ringEffect, self.invoker.specialHead, 0],
                    softStop=-2.85,
                ),
            )
            particleTrack.append(particleSeq)

        headAndSound = Sequence(
            Wait(0.1),
            Parallel(
                self.invoker.specialHead.actorInterval("healing-bell"), soundTrack
            ),
        )
        suitTrackAndAttack = Parallel(suitTrack, headAndSound, particleTrack)

        # Create a visual to show all suits unluring.
        unlureTracks = Parallel()
        healTracks = Parallel()
        responses = Parallel()
        unapplyVETrack = Parallel()
        for suit in self.targetObjs:
            result = self.findTarget(suit.doId)
            if suit.isLured:
                unlureTracks.append(self.getUnlureTrack(suit))
            if result.hpAdjust:
                healHP = result.hpAdjust
                seq = Func(self.updateSuitHP, suit, healHP)
                healTracks.append(seq)
            if suit != self.invoker:
                responses.append(Func(self.getSuitHealChat, suit))

            if suit:
                unapplyVETrack.append(
                    Func(
                        MovieUtil.unapplyVisualEffect, suit, SUIT_VISUAL_EFFECTS_TO_REMOVE
                    )
                )
        allHealTracks = Sequence(
            Wait(2.2), Parallel(unlureTracks, healTracks, unapplyVETrack, responses)
        )

        return Parallel(suitTrackAndAttack, allHealTracks, Wait(1))

    def updateSuitHP(self, suit, heal):
        if heal > 0:
            sfx = loader.loadSfx("phase_11/audio/sfx/LB_toonup.ogg")
            suit.updateHealthBar(heal)
            suit.showHpText(heal)
            sfx.play()

    def getSuitHealChat(self, suit):
        suit.setChatAbsolute(
            random.choice(TTLocalizer.MovieSuitHealResponses), CFSpeech | CFTimeout
        )

    def getUnlureTrack(self, suit):
        suitResponseTrack = Sequence()
        suitResponseTrack.append(
            Sequence(MovieLure.createSuitResetPosTrack(suit, self.battle))
        )
        suitResponseTrack.append(MovieUtil.unlureSuit(suit, self.battle))
        suitResponseTrack.append(Func(suit.neutralAvatar))
        return suitResponseTrack


@AttackClass(attackType=AttackEnum.HEARTBROKEN)
class Heartbroken(SuitDamageAttack):
    ALLOW_GROUPING = False

    # def doAttack(self):
    #     sfx = loader.loadSfx("phase_10/audio/sfx/SA_shatter_hit.ogg")
    #     return Parallel(super().doAttack(), SoundInterval(sfx))


@AttackClass(attackType=AttackEnum.RED_THREAD)
class RedThread(Attack):
    CHEAT = True
    OPEN_SHOT_DUR = 3.5
    ANIM_NAME = 'magic2'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.visualApplySeqs = {}

    def doAttack(self):
        effects = [effect for toon in self.toons for effect in toon.getVisualEffectsOfId(VisualEffectEnum.RED_THREAD)]

        def applyVisuals():
            for idA, idB in zip(*[iter(self.extraArgs)] * 2):  # groups of 2
                avA = self.findAvatar(idA)
                if not avA:
                    continue
                returnVal = MovieUtil.applyVisualEffect(
                    avA,
                    VisualEffectEnum.RED_THREAD,
                    useMovieApply=True,
                    extraArgs=[idB])
                if returnVal is None:
                    continue
                applySeq, _ = returnVal
                self.visualApplySeqs[idA] = applySeq
                applySeq.start()

        def cleanupVisuals():
            for avId in self.visualApplySeqs.keys():
                self.visualApplySeqs[avId].finish()
            self.visualApplySeqs = {}

        return Parallel(
            self.getSoundTrack("SA_red_tape.ogg", node=self.invoker),
            # Unapply all visual effects here.
            Parallel(*[Func(effect.requestUnapply, wantApplyLock=True) for effect in effects if effect]),
            self.getSuitAnimTrack(),
            Sequence(
                Func(applyVisuals),
                Wait(1.0),
                Func(cleanupVisuals),
            )
        )


@AttackClass(attackType=AttackEnum.RED_THREAD_DAMAGE)
class RedThreadDamage(AllowGroupingAttack):
    SHOW_PLAY_BY_PLAY = False

    def doAttack(self):
        target = self.targetObjs[0]
        if target.isToon():
            toonTrack = self.getToonTrack(
                target=self.targetDicts[0],
                damageAnimNames=['cringe'],
                showDamageExtraTime=1.8,
                hpTextType=TTLocalizer.HP_TEXT_RED_THREAD,
            )
            return Sequence(Parallel(Sequence(toonTrack), Wait(3.0)))
        elif target.isSuit():
            suit = target
            result = self.findTarget(suit.doId)
            damageHP = result.hpAdjust

            def loopNeutralAnim(suit):
                loopAnim = "lured" if suit.isLured else "neutral"
                suit.loop(loopAnim)

            seq = Sequence(
                Parallel(
                    Func(suit.updateHealthBar, damageHP),
                    Func(suit.showHpString,
                         ("-" if damageHP == 0 else "") +
                         TTLocalizer.GeneralAttackHpTexts[TTLocalizer.HP_TEXT_RED_THREAD][0].format(damageHP)),
                    ActorInterval(suit, random.choice(['pie-small-react']))
                ),
                Func(loopNeutralAnim, suit)
            )
            return seq
        return Sequence()  # degenerate case

    def getCameraShot(self, duration):
        target = self.targetDicts[0]["avatar"]
        return self.camera.randomActorShot(target, self.battle, duration, "avatar")


@AttackClass(attackType=AttackEnum.PEELING_THE_BARK)
class PeelingTheBark(SuitSingleAttack):
    ANIM_NAME = "victory"
    CHEAT = True
    OPEN_SHOT_DUR = 5.0

    def doAttack(self):
        suitTrack = Sequence(
            Func(self.invoker.setChatAbsolute, self.getAttackTaunt(), CFSpeech | CFTimeout),
            ActorInterval(self.invoker, self.ANIM_NAME, endTime=2),
            ActorInterval(self.invoker, 'slip-forward', startTime=2.43), 
            Func(self.invoker.loop, "neutral")
        )

        log = globalPropPool.getProp("treekiller_log_center")
        log.setScale(0.01)
        globalLog = self.battle.attachNewNode("global-treekiller-log")
        log.reparentTo(globalLog)
        globalLog.hide()
        globalLog.wrtReparentTo(self.battle)
        globalLog.setPos(0, 20, 15)

        finalLogScale = (5, 3.5, 3.5)

        floorZ = 1.3

        firstDropPos = Point3(0, 10, floorZ)
        disappearPos = Point3(0, -15, floorZ)
        fallDisappearPos = Point3(0, -20, -9)

        def setLogZ(value, mult=1):
            log.setZ(lerp(0, -0.7 * mult, value))

        logTrack = Sequence(
            Func(globalLog.show),
            Parallel(
                ProjectileInterval(globalLog, endPos=firstDropPos, duration=2.0),
                LerpScaleInterval(log, 1.0, finalLogScale, blendType="easeIn"),
            ),
            Parallel(
                Parallel(
                    Sequence(
                        LerpPosInterval(globalLog, 1.5, disappearPos),
                        LerpPosInterval(globalLog, 0.5, fallDisappearPos),
                    ),
                    LerpHprInterval(globalLog, 2, (0, 360 * 4, 0), startHpr=(0, 0, 0)),
                ),
                Sequence(
                    LerpFunctionInterval(setLogZ, fromData=0, toData=1, duration=0.25, blendType="easeInOut", extraArgs=[2.2]),
                    LerpFunctionInterval(setLogZ, fromData=1, toData=0, duration=0.25, blendType="easeInOut", extraArgs=[2.2]),
                    LerpFunctionInterval(setLogZ, fromData=0, toData=1, duration=0.25, blendType="easeInOut"),
                    LerpFunctionInterval(setLogZ, fromData=1, toData=0, duration=0.25, blendType="easeInOut"),
                    LerpFunctionInterval(setLogZ, fromData=0, toData=1, duration=0.25, blendType="easeInOut"),
                    LerpFunctionInterval(setLogZ, fromData=1, toData=0, duration=0.25, blendType="easeInOut"),
                    LerpFunctionInterval(setLogZ, fromData=0, toData=1, duration=0.25, blendType="easeInOut"),
                    LerpFunctionInterval(setLogZ, fromData=1, toData=0, duration=0.25, blendType="easeInOut"),
                ),
                Sequence(
                    Wait(1.4),
                    LerpScaleInterval(globalLog, 0.5, 0.01, blendType="easeIn"),
                ),
            ),
            Func(MovieUtil.removeProp, globalLog),
        )

        soundTrack = self.getSoundTrack("phase_5/audio/sfx/tt_s_ara_cmg_itemHitsFloor.ogg", delay=2.0, node=self.invoker)
        hitSoundTrack = self.getSoundTrack("phase_5/audio/sfx/SA_peeling_the_bark.ogg", delay=2.8, node=self.invoker)

        toonTracks = Parallel()
        suitTracks = Parallel()
        for target in self.targetDicts:
            avatar = target["avatar"]
            if self.isToon(avatar):
                toonTrack = Sequence(
                    Wait(2.8),
                    Func(avatar.playDialogueForString, "!"),
                    Func(avatar.setAnimState, "Squish"),
                    Func(MovieUtil.applyVisualEffect, avatar, VisualEffectEnum.PEELED),
                )

                toonDamageTrack = self.getToonTrack(
                    target=target,
                    group=1,
                    hpTextType=TTLocalizer.HP_TEXT_PEELED,
                    damageDelay=1.4,
                    splicedDamageAnims=[],
                    forceHit=True,
                )
                toonTrack.append(toonDamageTrack)
                toonTrack.append(Wait(1.2))
                toonTrack.append(Func(avatar.setAnimState, "Neutral"))

                toonTracks.append(toonTrack)
            else:
                def loopNeutralAnim(suit):
                    loopAnim = "lured" if suit.isLured else "neutral"
                    suit.loop(loopAnim)

                hpText = TTLocalizer.GeneralAttackHpTexts[TTLocalizer.HP_TEXT_PEELED]
                suitTracks.append(Sequence(
                    Wait(2),
                    Func(avatar.playDialogueForString, "!"),
                    Func(avatar.showHpText, target["hp"], extraText=hpText[0]),
                    Func(avatar.updateHealthBar, target["hp"]),
                    ActorInterval(avatar, 'flatten'),
                    Func(loopNeutralAnim, avatar),
                ))

        return Parallel(suitTrack, logTrack, toonTracks, suitTracks, soundTrack, hitSoundTrack)

    def getCameraShot(self, duration):
        return self.camera.heldShot(
            14.37,
            6.75,
            10.16,
            124.61,
            -22.7,
            0,
            duration,
            "suitGroupThreeQuarterLeftBehindShot",
        )


@AttackClass(attackType=AttackEnum.WOODCHIPPER)
class Woodchipper(SuitSingleAttack):
    ANIM_NAME = "throw-paper"
    CHEAT = True
    OPEN_SHOT_DUR = 2.3

    def doAttack(self):
        target = self.targetDicts[0]
        toon = target["avatar"]
        log = globalPropPool.getProp("treekiller_log")
        suitDelay = 1.44
        damageDelay = 2.76
        dodgeDelay = 1.86
        suitTrack = self.getSuitTrack()
        logPosPoints = [Point3(-0.1, 0.6, 0.0), VBase3(-1.152, 86.581, -76.784)]
        propTrack = Sequence(
            self.getPropAppearTrack(
                log,
                self.invoker.getRightHand(),
                logPosPoints,
                0.7,
                Point3(0.6, 1.0, 1.0),
                scaleUpTime=0.25,
            )
        )
        propTrack.append(Wait(suitDelay))
        propTrack.append(Func(self.battle.movie.needRestoreRenderProp, log))
        propTrack.append(Func(log.wrtReparentTo, self.battle))

        propTrack.append(
            LerpPosInterval(log, 0.3, self.toonFacePoint(toon, parent=self.battle))
        )
        soundTrack = self.getSoundTrack(
            "SA_hardball_impact_only.ogg", delay=2.0, node=self.invoker
        )
        hitSoundTrack = self.getSoundTrack("SA_woodchipper.ogg", delay=damageDelay - 0.1, node=toon)

        # Particle track.
        BattleParticles.loadParticles()
        freezeEffect = BattleParticles.createParticleEffect(file="treekillerWoodchips")
        facePoint = self.toonFacePoint(toon)
        freezeEffect.setPos(toon.getPos() + (0, 0, facePoint.getZ()))
        partTrack2 = self.getPartTrack(
            freezeEffect, propTrack.getDuration(), 0.5, [freezeEffect, render, 0]
        )

        propTrack.append(LerpScaleInterval(log, 0.05, MovieUtil.PNT3_NEARZERO))
        propTrack.append(Func(MovieUtil.removeProp, log))
        propTrack.append(Func(self.battle.movie.clearRenderProp, log))
        damageAnims = [
            ["cringe", damageDelay, 0.01],
        ]
        toonTrack = self.getToonTrack(
            splicedDamageAnims=damageAnims,
            dodgeDelay=dodgeDelay,
            dodgeAnimNames=["sidestep"],
            showDamageExtraTime=damageDelay,
            forceHit=True,
            hpTextType=TTLocalizer.HP_TEXT_WOODCHIPPER,
        )

        effectTrack = Sequence(
            Wait(damageDelay),
            Func(MovieUtil.applyVisualEffect, toon, VisualEffectEnum.WOODCHIPPED),
        )

        return Parallel(
            suitTrack, toonTrack, propTrack, partTrack2, soundTrack, hitSoundTrack, effectTrack
        )

    def getCameraShot(self, duration):
        toon = self.targetDicts[0]["avatar"]
        closeDur = duration - self.OPEN_SHOT_DUR
        openShot = self.camera.randomOverShoulderShot(
            self.invoker,
            self.targetDicts[0]["avatar"],
            self.battle,
            self.OPEN_SHOT_DUR,
            "suit",
        )
        closeShot = self.camera.randomActorShot(toon, self.battle, closeDur, "avatar")
        return Sequence(openShot, closeShot)

    def getSplicedAnimsTrack(self, anims, actor=None, playRate=1.0):
        return super().getSplicedAnimsTrack(anims, actor=actor, playRate=1.5)


@AttackClass(attackType=AttackEnum.POWER_NAP_HEAL)
class PowerNapHeal(SuitHealAttack):
    @staticmethod
    def updateSuitHP(suit: DistributedSuitBase, hp: int, nonZero: bool=False) -> None:
        suit.updateHealthBar(hp)
        if nonZero and hp == 0:
            return
        suit.showHpText(hp, extraText=TTLocalizer.HpTextPowerNapOver)
        # Also make sure and unapply this thing so they aren't still sleeping!!
        MovieUtil.unapplyVisualEffect(suit, VisualEffectEnum.POWER_NAP)
        # Loop head neutral again now that power nap is gone
        if suit.specialHead:
            suit.specialHead.loopNeutral()


@AttackClass(attackType=AttackEnum.POWER_NAP_KILL_DAMAGE_UP)
class PowerNapKillDamageUp(ShowHpTextAttack):
    BaseString = '+{0} DMG UP!'

    def doAttack(self):
        hpTextTracks = Parallel()

        for toon in self.targetObjs:
            seq = Sequence(
                Func(toon.hideHpText),
                Func(toon.showHpString, self.BaseString.format(self.extraArgs[0]), 0.85, 0.7, (0.85, 0.78, 1.0, 1.0)),
            )

            hpTextTracks.append(seq)

        sfx = loader.loadSfx("phase_11/audio/sfx/LB_toonup.ogg")
        soundTrack = IsolatedSoundInterval(sfx)
        return Sequence(Parallel(Sequence(hpTextTracks, soundTrack), Wait(2.25)))

    def getCameraShot(self, duration):
        return self.camera.heldShot(0.0, 2.5, 3, 180, 10, 0, duration=duration, name='PowerNapKillDamageUpHeldShot')


@AttackClass(attackType=AttackEnum.INSOMNIA)
class Insomnia(SuitSingleAttack):
    CHEAT = True

    def doAttack(self):
        cutsceneLoader = CutsceneLoader.createLoader(
            key=CutsceneKeyEnum.Featherbedder_Insomnia,
            affectsCamera=self.battle.localToonPendingOrActive(),
            toons=self.battle.activeToons,
            fbed=self.invoker,
            battle=self.battle,
        )
        return Parallel(self.getSuitAnimTrack(doActorInterval=False), cutsceneLoader.buildCutscene(), Wait(7.0))

    def getCameraShot(self, duration):
        # Handled by Cutscene Loader
        return Sequence(Wait(duration))


@AttackClass(attackType=AttackEnum.GATEKEEPER_FODDER_KILL_PIERCE)
class GatekeeperFodderKillPierce(PowerNapKillDamageUp):
    BaseString = '+{0} DMG UP!\n\1damage_subtext_orange\1SHIELD PIERCE!\2'


@AttackClass(attackType=AttackEnum.GATEKEEPER_JUMP_UNLURE_FODDER)
class GatekeeperJumpUnlureFodder(Attack):
    def doAttack(self):
        suitTrack = Parallel(
            self.getSuitAnimTrack(doActorInterval=False),
            Sequence(
                ActorInterval(self.invoker, 'quick-jump', duration=1.5),
                ActorInterval(self.invoker, 'quick-jump', duration=0.9, startTime=4.8),
                Func(self.invoker.loop, 'neutral'),
            ),
        )

        reactTrack = Parallel()
        for target in self.targetObjs:
            reactTrack.append(Sequence(
                Wait(1.5),
                Func(MovieUtil.unlureSuit, target, self.battle),
                ActorInterval(target, 'slip-forward', playRate=1.25),
                MovieUtil.createSuitUnlureTrack(target, self.battle),
            ))

        soundTrack = self.getSoundTrack("SA_quake.ogg", delay=0, node=self.invoker, duration=2.1)
        reactSoundTrack = self.getSoundTrack("Toon_bodyfall_synergy.ogg", node=self.invoker, volume=0.8, delay=1.9)
        return Parallel(suitTrack, reactTrack, soundTrack, reactSoundTrack)

    def getCameraShot(self, duration):
        return self.camera.allGroupOverheadShot(duration=duration)


@AttackClass(attackType=AttackEnum.BELLRINGER_FODDER_EXPLOSION)
class BellringerFodderExplosion(Attack):
    """
    Battle movie for when an Overcharged Cog dies in the Bellringer fight
    """
    CHEAT = True
    OPEN_SHOT_DUR = 4.01

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
                        Func(self.updateSuitHP, avatar, target['hp']),
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
        MovieUtil.createKapowExplosionTrack(self.battle, explosionPoint=explodePoint.getPos(self.battle), scale=6.0).start()
        explodePoint.removeNode()

    def getSuitDeathMovie(self, suit):
        if suit is self.invoker:
            return Sequence()
        else:
            return super().getSuitDeathMovie(suit)


class WeatherBase(AvatarSayPhraseAttack):
    ANIM_NAME = "transformation"
    CHEAT = True
    OPEN_SHOT_DUR = 5.0

    MUSIC_CODE = ""
    AMBIENCE = ""

    waitDuration = 6.1

    weather = RainmakerWeather.NORMAL

    @property
    def hairState(self):
        raise NotImplementedError

    def doAttack(self):
        speechSeq = Parallel(super().doAttack(), ActorInterval(self.invoker, self.getAnimName(), playRate=(5/6.1)))
        speechSeq = Sequence(speechSeq, Func(self.invoker.loop, "neutral"))
        suitTrack = Func(self.invoker.specialHead.setHairState, self.hairState)

        BattleParticles.loadParticles()
        firstWhirlwind = BattleParticles.createParticleEffect(file="whirlwind1")
        secondWhirlwind = BattleParticles.createParticleEffect(file="whirlwind2")

        particleNode = render.attachNewNode('rainmaker-weather-particle-node')
        particleNode.setBin('fixed', 1)

        def positionWhirlwinds():
            if not self.invoker:
                return
            if not firstWhirlwind:
                return
            if not secondWhirlwind:
                return
            pos = self.invoker.getPos(render)
            firstWhirlwind.setPos(pos)
            secondWhirlwind.setPos(pos)

        partTrack = Sequence(
            Parallel(
                Func(positionWhirlwinds),
                self.getPartTrack(
                    firstWhirlwind, 0.0, 5.5, [firstWhirlwind, particleNode, 0], softStop=-1.0,
                ),
                self.getPartTrack(
                    secondWhirlwind, 2.75, 2.75, [secondWhirlwind, particleNode, 0], softStop=-1.0,
                ),
            ),
            Func(particleNode.removeNode),
        )

        if self.MUSIC_CODE is None:
            musicTrack = Func(base.musicMgr.fadeOutMusic, 6.0)
        else:
            music = base.instance.getPreloadedSong(self.MUSIC_CODE)
            musicTrack = Func(
                base.musicMgr.crossfadeIntoMusic, music, 6.0, 0.5, 1, True, 1.0, self.MUSIC_CODE
            )

        ambienceSeq = getattr(base.instance, self.AMBIENCE, None)
        if not ambienceSeq:
            raise NotImplementedError(f"No ambience sequence specified for weather state {self.attackType}!")

        setBattleWeather = Func(self.battle.setWeather, self.weather)

        tornadoCleanupTrack = Sequence()
        if self.battle.crazyTornado:
            tornado = self.battle.crazyTornado
            self.battle.crazyTornado = None
            removeClouds = Parallel()
            for cloud in self.battle.toonClouds:
                if cloud:
                    removeClouds.append(Func(cloud.removeNode))
            self.battle.toonClouds = []
            tornadoCleanupTrack = Sequence(
                removeClouds,
                Func(tornado.softStop),
                Func(tornado.reset),
                Func(tornado.cleanup),
            )

        return Parallel(
            speechSeq,
            musicTrack,
            Func(ambienceSeq),
            suitTrack,
            partTrack,
            setBattleWeather,
            Wait(self.waitDuration),
            tornadoCleanupTrack,
            Sequence(
                Wait(1.0),
                Func(self.battle.correctToonPosition, forceNormal=True),
            )
        )
    
    def getCameraShot(self, duration):
        node = self.invoker.attachNewNode('cameraHelperNode')
        cutsceneLoader = CutsceneLoader.createLoader(
            key=CutsceneKeyEnum.Rainmaker_Transformation,
            node=node
        )

        return Sequence(
            cutsceneLoader.buildCutscene(),
            Wait(0.05),
            Func(camera.wrtReparentTo, self.battle),
            Func(node.removeNode),
        )


@AttackClass(attackType=AttackEnum.WEATHER_MONSOON)
class Monsoon(WeatherBase):
    MUSIC_CODE = "rainmaker_monsoon"
    AMBIENCE = "ambienceMonsoon"
    weather = RainmakerWeather.MONSOON

    waitDuration = 10.7

    def getCameraShot(self, duration):
        cutsceneLoader = CutsceneLoader.createLoader(
            key=CutsceneKeyEnum.Rainmaker_Tornado,
            affectsCamera=self.battle.localToonPendingOrActive(),
            toons=self.battle.activeToons,
            rainmaker=self.invoker,
            battle=self.battle,
        )
        tornadoes = cutsceneLoader.getParticleSystems()
        self.battle.crazyTornado = tornadoes[1]
        self.battle.toonClouds.append(cutsceneLoader.getNodeIndex(16))
        self.battle.toonClouds.append(cutsceneLoader.getNodeIndex(17))
        self.battle.toonClouds.append(cutsceneLoader.getNodeIndex(18))
        self.battle.toonClouds.append(cutsceneLoader.getNodeIndex(19))
        return Parallel(
            Sequence(
                cutsceneLoader.buildCutscene(cleanupParticles=False),
                Wait(0.05),
                Func(camera.wrtReparentTo, self.battle),
                Func(tornadoes[0].reset),
                Func(tornadoes[0].cleanup),
            ),
            Sequence(
                Wait(9.3),
                Func(self.battle.correctToonPosition),
            )
        )

    @property
    def hairState(self):
        return self.invoker.specialHead.HEAVY


@AttackClass(attackType=AttackEnum.WEATHER_OIL_RAIN)
class OilRain(WeatherBase):
    MUSIC_CODE = "rainmaker_oil"
    AMBIENCE = "ambienceOilRain"
    weather = RainmakerWeather.OIL_RAIN

    @property
    def hairState(self):
        return self.invoker.specialHead.OIL


@AttackClass(attackType=AttackEnum.WEATHER_FOG)
class Fog(WeatherBase):
    MUSIC_CODE = "rainmaker_fog"
    AMBIENCE = "ambienceFog"
    weather = RainmakerWeather.FOG

    @property
    def hairState(self):
        return self.invoker.specialHead.FOG


@AttackClass(attackType=AttackEnum.WEATHER_HEAVY_RAIN)
class HeavyRain(WeatherBase):
    MUSIC_CODE = "rainmaker_heavy"
    AMBIENCE = "ambienceHeavyRain"
    weather = RainmakerWeather.HEAVY_RAIN

    @property
    def hairState(self):
        return self.invoker.specialHead.HEAVY


@AttackClass(attackType=AttackEnum.WEATHER_STORM_CELL)
class StormCell(WeatherBase):
    MUSIC_CODE = "rainmaker_storm"
    AMBIENCE = "ambienceStormCell"
    weather = RainmakerWeather.STORM_CELL

    @property
    def hairState(self):
        return self.invoker.specialHead.STORM


@AttackClass(attackType=AttackEnum.WEATHER_INVERSION)
class Inversion(WeatherBase):
    MUSIC_CODE = "rainmaker_empty"
    AMBIENCE = "ambienceDefault"
    weather = RainmakerWeather.NORMAL

    @property
    def hairState(self):
        return self.invoker.specialHead.DEFAULT

    def doAttack(self):
        suit = self.invoker
        suitTrack = WeatherBase.doAttack(self)
        flashRed = Sequence(
            LerpColorScaleInterval(suit, 0.2, colorScale=VBase4(1, 0.2, 0.2, 1)),
            LerpColorScaleInterval(suit, 0.6, colorScale=VBase4(1, 1, 1, 1)),
            name='inversionFlash'
        )
        redTrack = Sequence(Wait(0.8), flashRed, Wait(0.5), flashRed, Wait(0.5))

        sfx = loader.loadSfx("phase_11/audio/sfx/LB_toonup.ogg")
        soundTrack = IsolatedSoundInterval(sfx)

        return Parallel(suitTrack,
                        redTrack,
                        soundTrack,
                        Sequence(
                            Func(suit.showHpString, TTLocalizer.HpTextAdditionalAttack, color=(0.85, 0.78, 1.0, 1.0)),
                            Wait(3.0)
                        ))


@AttackClass(attackType=AttackEnum.HEAVY_RAIN_ZAP)
class HeavyRainZap(Attack):
    ANIM_NAME = "magic3"
    CHEAT = True

    def doAttack(self):
        damageTrack = Parallel(
            self.getToonTracks()
        )
        rainmaker = None
        for target in self.targetObjs:
            if self.isSuit(target):
                if target.style.name == 'rainmake':
                    rainmaker = target
                result = self.findTarget(target.doId)
                damageHP = result.hpAdjust
                hp = target.getHp() + damageHP
                if hp > 0 or True:
                    damageTrack.append(
                        Func(self.updateSuitHP, target, damageHP),
                    )
                else:
                    # todo - custom death movie
                    pass

        soundTrack = SoundInterval(globalBattleSoundCache.getSound('AA_lightning.ogg'))
        cutsceneLoader = CutsceneLoader.createLoader(
            key=CutsceneKeyEnum.Rainmaker_HeavyRainDamage,
            toons=self.battle.activeToons,
            rainmaker=rainmaker,
            allSuits=self.battle.activeSuits,
            battle=self.battle,
        )
        return Parallel(
            cutsceneLoader.buildCutscene(),
            Sequence(Wait(2.15), damageTrack),
            Sequence(Wait(1.079), soundTrack),
        )

    def getCameraShot(self, duration):
        return Wait(duration)

    def updateSuitHP(self, suit, damage):
        suit.updateHealthBar(damage)
        suit.showHpText(damage)


@AttackClass(attackType=AttackEnum.STORM_CELL_ZAP)
class StormCellZap(AllowGroupingAttack):
    CHEAT = True
    OPEN_SHOT_DUR = 1.7

    def doAttack(self):
        rainmaker = None
        for suit in self.battle.activeSuits:
            if suit.style.name == 'rainmake':
                rainmaker = suit
                break
        soundTrack = SoundInterval(globalBattleSoundCache.getSound('AA_lightning.ogg'))

        toons = self.battle.activeToons
        strikes = []
        for _ in range(4):
            lightning = globalPropPool.getProp('lightning')
            lightning.reparentTo(self.battle)
            lightning.hide()
            lightning.setScale(1, 1, 3)
            strikes.append(lightning)

        cutsceneLoader = CutsceneLoader.createLoader(
            key=CutsceneKeyEnum.Rainmaker_StormCellDamage,
            toons=toons,
            rainmaker=rainmaker,
            allSuits=self.battle.activeSuits,
            battle=self.battle,
            strikes=strikes
        )

        lightningTrack = Parallel()
        for index, toon in enumerate(toons):
            if toon is None:
                continue
            lightning = strikes[index]

            # run particles
            cutsceneDict = cutsceneLoader.getCutsceneDict()
            particleSystem = cutsceneDict['particles'][index]
            lightningTrack.append(
                Sequence(
                    Func(lightning.reparentTo, toon),
                    Func(lightning.wrtReparentTo, self.battle),
                    Func(lightning.setH, random.randint(0, 360)),
                    Func(lightning.show),
                    Parallel(
                        Parallel(
                            Sequence(
                                Func(particleSystem.start, parent=lightning, renderParent=render),
                                Func(particleSystem.softStart),
                                Wait(0.3407),
                                Func(particleSystem.softStop),
                            ),
                            LerpColorScaleInterval(
                                lightning, duration=1.2532, colorScale=(1, 1, 1, 0), startColorScale=(1, 1, 1, 1),
                                blendType='easeIn',
                            )
                        ),
                        Sequence(
                            ActorInterval(toon, 'slip-forward'),
                            Wait(0.01),
                            Func(toon.loop, 'neutral')
                        )
                    ),
                    Func(MovieUtil.removeProp, lightning)
                ),
            )

        return Parallel(
            cutsceneLoader.buildCutscene(),
            Sequence(Wait(1.38), self.getToonTracks()),
            Sequence(Wait(0.2), soundTrack),
            Sequence(Wait(1.38), lightningTrack),
        )

    def getCameraShot(self, duration):
        return Wait(duration)


@AttackClass(attackType=AttackEnum.RAINMAKER_ENDING_0)
class RainmakerEnding0(WeatherBase):
    MUSIC_CODE = "rainmaker_end"
    AMBIENCE = "ambienceDefault"
    weather = RainmakerWeather.NORMAL

    @property
    def hairState(self):
        return self.invoker.specialHead.DEFAULT


@AttackClass(attackType=AttackEnum.RAINMAKER_ENDING_1)
class RainmakerEnding1(PlayCutsceneAttack):
    CUTSCENE_KEY = CutsceneKeyEnum.Rainmaker_Ending_1

    def doAttack(self):
        self.invoker.specialHead.setForceUnhurtMode(1)
        self.invoker.hideNametag2d()
        return Sequence(
            Func(MovieTrap.enableTrapFreeMove, self.invoker, self.battle),
            super().doAttack(),
            Func(MovieTrap.disableTrapFreeMove, self.invoker, self.battle),
        )

    def getEndTrack(self):
        return Sequence()

    def getLoaderKwargs(self) -> dict:
        rainmaker = None
        for suit in self.battle.activeSuits:
            if suit.style.name == 'rainmake':
                rainmaker = suit
                break
        return {'rainmaker': rainmaker}


@AttackClass(attackType=AttackEnum.RAINMAKER_ENDING_2)
class RainmakerEnding2(RainmakerEnding1):
    CUTSCENE_KEY = CutsceneKeyEnum.Rainmaker_Ending_2


@AttackClass(attackType=AttackEnum.RAINMAKER_ENDING_3)
class RainmakerEnding3(RainmakerEnding1):
    CUTSCENE_KEY = CutsceneKeyEnum.Rainmaker_Ending_3


@AttackClass(attackType=AttackEnum.RAINMAKER_ENDING_4)
class RainmakerEnding4(RainmakerEnding1):
    CUTSCENE_KEY = CutsceneKeyEnum.Rainmaker_Ending_4


@AttackClass(attackType=AttackEnum.BARNBURNER)
class Barnburner(Attack):
    ANIM_NAME = "magic3"
    CHEAT = True

    def getCameraShot(self, duration):
        camSeq = Sequence(
            self.camera.heldRelativeShot(
                self.battle, 11, -12, 3, 40, 0, 0, 1.3, "barnburnerRelativeShot"
            ),
            LerpPosHprInterval(
                camera,
                duration=3.0,
                blendType="easeInOut",
                other=self.battle,
                startPos=Vec3(-10, -10, 4),
                startHpr=Vec3(-45, -14, 0),
                pos=Vec3(-14, -14, 12),
                hpr=Vec3(-45, -20, 0),
            ),
        )
        return Parallel(
            camSeq,
            Wait(duration),
        )

    def doAttack(self):
        burninatorTrack = Parallel()
        suitBurninatorTrack = Parallel()
        startTrack = self.buildInitialTrack()
        for target in self.targetObjs:
            if self.isSuit(target):
                suitBurninatorTrack.append(self.buildSuitDamageTrack(target))
            elif self.isToon(target):
                burninatorTrack.append(self.buildToonDamageTrack(target, self.findTargetDict(target.doId)))

        return Parallel(
            startTrack,
            Sequence(Wait(1.0), Parallel(burninatorTrack, suitBurninatorTrack)),
        )

    def buildInitialTrack(self):
        """Firestarter's opening move"""
        useCog = self.invoker
        useCogInterval = Sequence()
        a = ActorInterval(useCog, "magic2")
        BattleParticles.loadParticles()
        sprayEffect = BattleParticles.createParticleEffect(file="barnburnerSpray")
        BattleParticles.setEffectTexture(sprayEffect, "fire")
        b = self.getPartTrack(sprayEffect, 0.8, 1.7, [sprayEffect, useCog, 0])
        useCogInterval = Parallel(a, b)
        particleTrack = self.buildParticleTrack(useCog)
        chatMsgs = TTLocalizer.SuitAttackTaunts[self.attackType]
        return Parallel(
            particleTrack,
            self.getSoundTrack("SA_barnburner.ogg", node=useCog),
            useCogInterval,
            Sequence(
                Func(
                    useCog.setChatAbsolute,
                    random.choice(chatMsgs),
                    CFSpeech | CFTimeout,
                ),
                Wait(3.0),
                Func(useCog.clearChat),
            ),
        )

    def buildParticleTrack(self, suit):
        """Makes the silly little fire particles"""
        BattleParticles.loadParticles()
        fullTrack = Parallel()
        colors = (
            # (0.1, 0.1, 0.1, 1.0),
            (0.9, 0.5, 0.1, 1.0),
            (1.0, 0.2, 0.1, 1.0),
            (0.9, 0.8, 0.1, 1.0),
        )
        DURATION = 3.0
        TIME_BETWEEN = 0.3
        Z_OFFSET = -4
        SMOKE_Z_OFFSET = 2
        Y_OFFSET = 0

        LAYERS = 5
        DENSITY = len(colors)
        for i in range(LAYERS):  # layers
            for o in range(DENSITY):  # density
                # fire
                particleEffect = BattleParticles.createParticleEffect(file="barnburner")
                particleEffect.setScale(4 + (i * 1))
                particleEffect.setH(o * (90 / DENSITY) + (45 * o))
                particleEffect.setPos(
                    particleEffect.getPos() + Vec3(0, Y_OFFSET, Z_OFFSET)
                )
                BattleParticles.setEffectTexture(
                    particleEffect, "fire", color=colors[o % len(colors)]
                )

                # smoke
                particleEffectB = BattleParticles.createParticleEffect(
                    file="barnburner_smoke"
                )
                particleEffectB.setScale(4 + (i * 1))
                particleEffectB.setH(o * (90 / DENSITY) + (45 * o))
                particleEffectB.setPos(
                    particleEffectB.getPos()
                    + Vec3(0, Y_OFFSET, Z_OFFSET + SMOKE_Z_OFFSET)
                )
                BattleParticles.setEffectTexture(particleEffectB, "snow-particle")

                time_beforeStart = (i * TIME_BETWEEN) + 1e-05
                time_duration = DURATION - (i * TIME_BETWEEN)
                fullTrack.append(
                    Parallel(
                        self.getPartTrack(
                            particleEffect,
                            time_beforeStart,
                            time_duration,
                            [particleEffect, self.battle, 0],
                        ),
                        self.getPartTrack(
                            particleEffectB,
                            time_beforeStart,
                            time_duration,
                            [particleEffectB, self.battle, 0],
                        ),
                        Sequence(
                            Func(particleEffect.hide),
                            Wait(time_beforeStart),
                            Func(particleEffect.show),
                            LerpPosInterval(
                                particleEffect,
                                pos=particleEffect.getPos() - Vec3(0, 0, Z_OFFSET),
                                duration=time_duration * 0.7,
                                blendType="easeInOut",
                            ),
                            LerpColorScaleInterval(
                                particleEffect,
                                time_duration * 0.3,
                                colorScale=(0, 0, 0, 0),
                            ),
                        ),
                        Sequence(
                            Func(particleEffectB.hide),
                            Wait(time_beforeStart + 0.5),
                            Func(particleEffectB.show),
                            LerpPosInterval(
                                particleEffectB,
                                pos=particleEffectB.getPos() - Vec3(0, 0, Z_OFFSET),
                                duration=time_duration * 0.7,
                                blendType="easeInOut",
                            ),
                            LerpPosInterval(
                                particleEffectB,
                                pos=particleEffectB.getPos() + Vec3(0, 0, Z_OFFSET * 2),
                                duration=time_duration * 0.3,
                                blendType="easeInOut",
                            ),
                        ),
                    )
                )
        return fullTrack

    def burnModel(self, actor, parts):
        BattleParticles.loadParticles()
        baseFlameEffect = BattleParticles.createParticleEffect(file="firedBaseFlame")
        flameEffect = BattleParticles.createParticleEffect("FiredFlame")
        flecksEffect = BattleParticles.createParticleEffect("SpriteFiredFlecks")
        BattleParticles.setEffectTexture(baseFlameEffect, "fire")
        BattleParticles.setEffectTexture(flameEffect, "fire")
        BattleParticles.setEffectTexture(
            flecksEffect, "roll-o-dex", color=Vec4(0.8, 0.8, 0.8, 1)
        )
        baseFlameSmall = BattleParticles.createParticleEffect(file="firedBaseFlame")
        flameSmall = BattleParticles.createParticleEffect("FiredFlame")
        flecksSmall = BattleParticles.createParticleEffect("SpriteFiredFlecks")
        BattleParticles.setEffectTexture(baseFlameSmall, "fire")
        BattleParticles.setEffectTexture(flameSmall, "fire")
        BattleParticles.setEffectTexture(
            flecksSmall, "roll-o-dex", color=Vec4(0.8, 0.8, 0.8, 1)
        )
        baseFlameSmall.setScale(0.7)
        flameSmall.setScale(0.7)
        flecksSmall.setScale(0.7)
        baseFlameTrack = self.getPartTrack(
            baseFlameEffect, 1.0, 1.9, [baseFlameEffect, actor, 0]
        )
        flameTrack = self.getPartTrack(flameEffect, 1.0, 1.9, [flameEffect, actor, 0])
        flecksTrack = self.getPartTrack(
            flecksEffect, 1.8, 1.1, [flecksEffect, actor, 0]
        )

        ogColorScales = []

        def changeColor(partMaps):
            track = Parallel()
            for parts in partMaps:
                for nextPart in parts:
                    ogColorScales.append(nextPart.getColorScale())
                    track.append(Func(nextPart.setColorScale, Vec4(0, 0, 0, 1)))
            return track

        def resetColor(partMaps):
            track = Parallel()
            for parts in partMaps:
                for partNum, nextPart in enumerate(parts):
                    track.append(
                        LerpColorScaleInterval(
                            nextPart,
                            colorScale=ogColorScales[partNum],
                            duration=1.5,
                            blendType="easeInOut",
                        )
                    )
            return track

        colorTrack = Sequence()
        colorTrack.append(Wait(1.5))
        colorTrack.append(Func(self.battle.movie.needRestoreColor))
        colorTrack.append(changeColor(parts))
        colorTrack.append(Wait(0.5))
        colorTrack.append(resetColor(parts))
        colorTrack.append(Func(self.battle.movie.clearRestoreColor))
        return Parallel(baseFlameTrack, flameTrack, flecksTrack, colorTrack)

    def buildToonDamageTrack(self, toon, tdict):
        """An individual track played per Toon"""
        burnTrack = self.burnModel(
            toon, (toon.getHeadParts(), toon.getTorsoParts(), toon.getLegsParts())
        )
        damageAnims = []
        damageAnims.append(["cringe", 0.01, 0.7, 0.62])
        damageAnims.append(["slip-forward", 1e-05, 1.0, 1.2])
        # damageAnims.extend(self.getSplicedLerpAnims('slip-forward', 0.31, 0.2, startTime=1.2))
        toonTrack = self.getToonTrack(
            damageDelay=1.5,
            splicedDamageAnims=damageAnims,
            dodgeDelay=0.3,
            dodgeAnimNames=["sidestep"],
            target=tdict,
        )
        return Parallel(burnTrack, toonTrack)

    def buildSuitDamageTrack(self, suit):
        """An individual track played per Suit"""
        burnTrack = self.burnModel(suit, (suit.findAllMatches("**"),))
        result = self.findTarget(suit.doId)
        damageHP = result.hpAdjust

        hp = suit.getHp() + damageHP

        if hp > 0:
            cleanseTrack = Parallel(Func(MovieUtil.unapplyVisualEffect, suit, SUIT_VISUAL_EFFECTS_TO_REMOVE))
            if suit.isLured:
                cleanseTrack.append(MovieUtil.createSuitUnlureTrack(suit, self.battle))

            return Parallel(
                burnTrack,
                Sequence(
                    Wait(1.5),
                    Func(self.updateSuitHP, suit, damageHP),
                    ActorInterval(suit, "pie-small-react"),
                    cleanseTrack,
                    Func(suit.neutralAvatar),
                ),
            )
        else:
            return self.getSuitDeathMovie(suit)

    def updateSuitHP(self, suit, damage):
        suit.updateHealthBar(damage)
        suit.showHpText(damage)

    def getEndTrack(self):
        """Barnburner has a unique suit death anim."""
        deathReviveTracks = Parallel()
        for target in self.targetDicts:
            av = target["avatar"]
            avId = av.doId
            result = self.findTarget(avId)
            if self.isSuit(av) and result.revived:
                deathReviveTracks.append(self.getSuitReviveMovie(av))
        return Sequence(deathReviveTracks)

    def getSuitDeathMovie(self, chosenSuit):
        suitHeight = chosenSuit.getHeight()
        moveTrack = Sequence(
            Wait(0.4),
            LerpPosInterval(
                chosenSuit, 0.7, chosenSuit.getPos() + Vec3(0, 0, -suitHeight * 0.6)
            ),
            LerpPosInterval(
                chosenSuit, 0.5, chosenSuit.getPos() + Vec3(0, 0, -suitHeight * 1.2)
            ),
            Func(chosenSuit.wrtReparentTo, hidden),
        )

        animTrack = Sequence(
            ActorInterval(chosenSuit, "flail"),
            ActorInterval(chosenSuit, "flail", startTime=1.1),
            Sequence(
                Wait(0.7),
                ActorInterval(chosenSuit, "slip-forward", duration=2.1),
            ),
        )

        burnTrack = LerpColorScaleInterval(
            chosenSuit,
            colorScale=(0, 0, 0, 1.0),
            duration=1.6,
            blendType="easeOut",
        )

        messagePool = (
            TTLocalizer.BarnburnerResponses
            if chosenSuit.style.name != "fires"
            else TTLocalizer.FirestarterBarnburnerResponses
        )
        messageTrack = Sequence(Wait(0.3))
        if messagePool:
            messageTrack.append(
                Func(
                    chosenSuit.setChatAbsolute,
                    random.choice(messagePool),
                    CFSpeech | CFTimeout,
                )
            )

        return Parallel(moveTrack, animTrack, burnTrack, messageTrack)


@AttackClass(attackType=AttackEnum.CIGAR_SMOKE_FIRESTARTER)
class CigarSmokeFirestarter(CigarSmoke):
    SmokeNodePos = (0, 1.5, -0.5)
    CigarPosPoints = [Point3(0.0, 0.0, 0.0), VBase3(180.0, 0.0, 0.0)]
    CigarScale = Point3(3.0)
    CigarRemainTime = 3.85
    CigarScaleUpTime = 0.25
    CigarScaleDownTime = 0.25

    def getCigarSuitTrack(self):
        return Parallel(
            self.getSuitTrack(wantSpeechHeadAnim=False, playRate=self.PLAY_RATE),
            Sequence(
                self.invoker.specialHead.actorInterval('cigar-smoke', playRate=self.PLAY_RATE),
                Func(self.invoker.specialHead.loopNeutral),
            )
        )


@AttackClass(attackType=AttackEnum.CIGAR_SMOKE_PLUTOCRAT)
class CigarSmokePlutocrat(CigarSmoke):
    WantCigarProp = False

    def getCigarSuitTrack(self):
        return Parallel(
            self.getSuitTrack(wantSpeechHeadAnim=False, playRate=self.PLAY_RATE),
            Sequence(
                self.invoker.specialHead.actorInterval('cigar-smoke', playRate=self.PLAY_RATE),
                Func(self.invoker.specialHead.loopNeutral),
            )
        )

    def getDamageDelay(self):
        return 2.7/self.PLAY_RATE


@AttackClass(attackType=AttackEnum.WOODCHIPPER_DAMAGE)
class WoodchipperDamage(Attack):
    CHEAT = True
    OPEN_SHOT_DUR = 1.7

    def doAttack(self):
        target = self.targetDicts[0]
        toon = target["avatar"]
        overallDelay = 0.5
        damageDelay = 0.5 + overallDelay
        BattleParticles.loadParticles()
        spinEffect1 = BattleParticles.createParticleEffect(
            file="woodchipperDamageEffect"
        )
        spinEffect1.reparentTo(toon)
        height1 = toon.getHeight() * (random.random() * 0.2 + 0.7)
        spinEffect1.setPos(0, 0, height1)
        spinEffect1.setHpr(0, 0, -random.random() * 10 - 85)
        spinEffect1.setHpr(spinEffect1, 0, 50, 0)
        spinEffect1.wrtReparentTo(self.battle)
        spinTrack1 = self.getPartTrack(
            spinEffect1,
            0.5 + overallDelay,
            2.9,
            [spinEffect1, self.battle, 0],
            softStop=-1.0,
        )
        damageAnims = []
        damageAnims.append(["conked", 0.0001, 0.4, 0.09])
        damageAnims.append(["conked", 0.0001, 0.4, 0.09])
        damageAnims.append(["conked", 0.0001, 0.4, 0.66])
        damageAnims.append(["conked", 0.0001, 0.4, 0.09])
        damageAnims.append(["conked", 0.0001, 0.4, 0.09])
        damageAnims.append(["conked", 0.0001, 0.4, 0.86])
        damageAnims.append(["conked", 0.0001, 0.4, 0.14])
        damageAnims.append(["conked", 0.0001, 0.4, 0.14])
        damageAnims.append(["conked", 0.0001, 0.4])

        toonTrack = self.getToonTrack(
            damageDelay=damageDelay,
            splicedDamageAnims=damageAnims,
            dodgeDelay=0.91,
            dodgeAnimNames=["sidestep"],
            showDamageExtraTime=2.1,
            showMissedExtraTime=1.0,
            forceHit=1,
        )
        toonSpinTrack = Sequence()
        soundTrack = self.getSoundTrack(
            "SA_woodchipped.ogg", delay=overallDelay + 0.3
        )
        return Parallel(toonTrack, toonSpinTrack, soundTrack, spinTrack1)

    def getCameraShot(self, duration):
        return self.camera.heldRelativeShot(
            self.targetDicts[0]["avatar"],
            0, 9, 3.5,
            180, -5, 0,
            duration,
            "singleAvatarShot",
        )

    def getAttackDisplayName(self):
        return (
            TTLocalizer.SuitAttackNames[self.attackType][0],
            TTLocalizer.SuitAttackNames[self.attackType][1]
            % abs(self.targetDicts[0]["hp"]),
        )


@AttackClass(attackType=AttackEnum.GHOST_PAYROLL_HEAL)
class GhostPayrollHeal(AllowGroupingAttack):
    CHEAT = True
    OPEN_SHOT_DUR = 6.5

    def doAttack(self):
        damageDelay = 2.65
        healTracks = Parallel()

        books = []

        def updateSuitHP(suit):
            hpText = TTLocalizer.GeneralAttackHpTexts[TTLocalizer.HP_TEXT_GHOST_PAYROLL]
            suit.showHpString(hpText[0], color=hpText[1])
            suit.setChatAbsolute(
                TTLocalizer.GhostPayrollResponses[suit.dna.name],
                CFSpeech | CFTimeout,
            )

        def removeBooks():
            MovieUtil.removeProps(books)

        for suit in self.targetObjs:
            paper = globalPropPool.getProp("shredder-paper")
            paper.reparentTo(suit)
            paper.setPos(0, 0, 30)
            paper.setHpr(180, -90, 0)
            paper.setColorScale(0.2, 0.2, 0.6, 1)
            books.append(paper)
            endPos = (0, 0, suit.height + 3)
            pInterval = Sequence(
                ProjectileInterval(
                    paper, duration=2, endPos=endPos, gravityMult=0.4
                ),
            )
            endScaleSeq = LerpScaleInterval(paper, duration=0.65, scale=0.01)
            fallInterval = LerpPosInterval(paper, 0.65, (0, 0, suit.height / 2))
            soundTrack = self.getSoundTrack("SA_extra_tip.ogg", delay=0)
            healTracks.append(Sequence(
                Parallel(
                    Sequence(pInterval, Parallel(endScaleSeq, fallInterval)), soundTrack
                ),
                Func(updateSuitHP, suit),
            ))

        sfx = loader.loadSfx("phase_11/audio/sfx/LB_toonup.ogg")
        repairSoundTrack = Sequence(Wait(damageDelay), SoundInterval(sfx))
        return Sequence(
            Parallel(repairSoundTrack, healTracks),
            Func(removeBooks),
            Wait(0.5),
        )

    def getCameraShot(self, duration):
        return self.camera.heldShot(0, -17, 14, 0, -22, 0, duration, "allGroupOverheadShot")


@AttackClass(attackType=AttackEnum.STANDUP_GUY)
class StandupGuy(AvatarSayPhraseAttack):
    ANIM_NAME = "defense"
    CHEAT = True

    def doAttack(self):
        phraseSeq = super().doAttack()

        neutralAnim = 'lured' if self.avatar.isLured else 'neutral'

        suitTrack = Sequence(ActorInterval(self.avatar, self.ANIM_NAME), Func(self.avatar.loop, neutralAnim))
        soundTrack = self.getSoundTrack("phase_11/audio/sfx/SA_defense.ogg", delay=0, node=self.invoker)
        return Parallel(suitTrack, soundTrack, phraseSeq)


@AttackClass(attackType=AttackEnum.SHAKEDOWN)
class Shakedown(SuitSingleAttack):
    ANIM_NAME = "magic3"
    CHEAT = True
    OPEN_SHOT_DUR = 1.6

    def doAttack(self):
        damageDelay = 1.95

        suitTrack = self.getSuitAnimTrack()

        def applyVisualEffect(toon):
            if self.extraArgs[0] == 0:
                MovieUtil.applyVisualEffect(toon, VisualEffectEnum.UNITE_COOLDOWN)

        liftTracks = Parallel()
        toonRiseTracks = Parallel()
        for toon in self.targetObjs:
            liftEffect = BattleParticles.createParticleEffect("ShiftLift")
            liftEffect.setPos(toon.getPos(self.battle))
            liftEffect.setZ(liftEffect.getZ() - 1.3)
            liftTracks.append(
                self.getPartTrack(
                    liftEffect, 1.1, 4.1, [liftEffect, self.battle, 0]
                )
            )
            shadow = toon.dropShadow
            fakeShadow = MovieUtil.copyProp(shadow)
            x = toon.getX()
            y = toon.getY()
            z = toon.getZ()
            height = 3
            groundPoint = Point3(x, y, z)
            risePoint = Point3(x, y, z + height)
            shakeRight = Point3(x, y + 0.7, z + height)
            shakeLeft = Point3(x, y - 0.7, z + height)
            shakeTrack = Sequence()
            shakeTrack.append(Wait(damageDelay + 0.25))
            shakeTrack.append(Func(shadow.hide))
            shakeTrack.append(LerpPosInterval(toon, 1.1, risePoint))
            for i in range(0, 17):
                shakeTrack.append(LerpPosInterval(toon, 0.03, shakeLeft))
                shakeTrack.append(LerpPosInterval(toon, 0.03, shakeRight))

            shakeTrack.append(LerpPosInterval(toon, 0.1, risePoint))
            shakeTrack.append(LerpPosInterval(toon, 0.1, groundPoint))
            shakeTrack.append(Func(shadow.show))
            shadowTrack = Sequence()
            shadowTrack.append(
                Func(self.battle.movie.needRestoreRenderProp, fakeShadow)
            )
            shadowTrack.append(Wait(damageDelay + 0.25))
            shadowTrack.append(Func(fakeShadow.hide))
            shadowTrack.append(Func(fakeShadow.setScale, 0.27))
            shadowTrack.append(Func(fakeShadow.reparentTo, toon))
            shadowTrack.append(Func(fakeShadow.setPos, MovieUtil.PNT3_ZERO))
            shadowTrack.append(Func(fakeShadow.wrtReparentTo, self.battle))
            shadowTrack.append(Func(fakeShadow.show))
            shadowTrack.append(
                LerpScaleInterval(fakeShadow, 0.4, Point3(0.17, 0.17, 0.17))
            )
            shadowTrack.append(Wait(1.81))
            shadowTrack.append(
                LerpScaleInterval(fakeShadow, 0.1, Point3(0.27, 0.27, 0.27))
            )
            shadowTrack.append(Func(MovieUtil.removeProp, fakeShadow))
            shadowTrack.append(Func(self.battle.movie.clearRenderProp, fakeShadow))
            toonRiseTracks.append(Parallel(
                shakeTrack, 
                shadowTrack,
                Func(applyVisualEffect, toon),
            ))

        damageAnims = []
        damageAnims.extend(self.getSplicedLerpAnims("think", 0.66, 1.9, startTime=2.06))
        damageAnims.append(["slip-backward", 0.01, 0.5])

        toonTracks = self.getToonTracks(
            damageDelay=damageDelay,
            splicedDamageAnims=damageAnims,
            showDamageExtraTime=2.7,
        )

        soundTrack = self.getSoundTrack(
            "SA_paradigm_shift.ogg", delay=2.1, node=self.invoker
        )

        return Parallel(
            suitTrack,
            liftTracks,
            toonTracks,
            toonRiseTracks,
            soundTrack,
        )
    
    def getCameraShot(self, duration):
        return self.camera.randomAttackCam(
            self.invoker, self.targetDicts[0]["avatar"], self.battle, duration, self.OPEN_SHOT_DUR, 'suit')

    def getAttackDisplayName(self):
        """There are two possible outcomes for Shakedown,
        thus in order to provide the correct description, index the
        description tuple with the second value in our extraArgs.
        """
        nameInfo = super().getAttackDisplayName()

        # This shouldn't ever happen, but just in-case.
        if not self.extraArgs:
            return nameInfo[0]

        # Return the correct name/desc pair.
        return (nameInfo[0], nameInfo[1][self.extraArgs[0]])


@AttackClass(attackType=AttackEnum.KICK_UP)
class KickUp(SuitSingleAttack):
    ANIM_NAME = "throw-object"
    CHEAT = True
    OPEN_SHOT_DUR = 7.0

    def doAttack(self):
        satellite = self.targetObjs[0]

        def showDamageBuff():
            satellite.hideHpText()
            satellite.showHpString('DAMAGE UP!', 0.85, 0.7, (0.718, 0.549, 0.722, 1.0))

        # registerSfx = self.getSoundTrack(
        #     "SA_life_insurance_register.ogg", delay=1.143, node=self.invoker
        # )
        cutsceneLoader = CutsceneLoader.createLoader(
            key=CutsceneKeyEnum.Plutocrat_Investor_Kickup,
            hydra=self.invoker,
            target=satellite,
            battle=self.battle,
        )
        return Parallel(
            # registerSfx,
            Sequence(
                Parallel(
                    Sequence(
                        Wait(1.143),
                        Func(showDamageBuff)
                    ),
                    cutsceneLoader.buildCutscene(),
                ),
                Func(camera.wrtReparentTo, self.battle),
            ),
            self.getSuitSayTrack(),
        )

    def getCameraShot(self, duration):
        return Wait(duration)
    
    def getAttackDisplayName(self):
        """Give a special shout out to the investor that was
        picked to be buffed :)
        """
        name = super().getAttackDisplayName()
        if not self.targetObjs:
            return name[0], name[1] % "A RANDOM INVESTOR!"
        return name[0], name[1] % TTLocalizer.suitName(self.targetObjs[0].dna.name)


@AttackClass(attackType=AttackEnum.SITDOWN)
class Sitdown(Attack):
    OPEN_SHOT_DUR = 3.0
    CHEAT = True
    ANIM_NAME = "sit-hungry-left"

    def doAttack(self):
        cutscene = CutsceneLoader.createLoader(
            key=CutsceneKeyEnum.Plutocrat_Investor_SitDown,
            styx=self.invoker,
            battle=self.battle,
        ).buildCutscene()
        bell1 = SoundInterval(loader.loadSfx('phase_8/audio/sfx/ttcc_int_psetter_bell.ogg'), duration=2.2)
        bell2 = SoundInterval(loader.loadSfx('phase_8/audio/sfx/ttcc_int_psetter_bell.ogg'), duration=2.2)
        return Parallel(
            cutscene,
            Sequence(Wait(0.40), bell1),
            Sequence(Wait(0.56), bell2),
            self.getSuitSayTrack(delay=0.1, duration=3.2),
        )

    def getCameraShot(self, duration):
        return Wait(duration)


@AttackClass(attackType=AttackEnum.USURY)
class Usury(Attack):
    OPEN_SHOT_DUR = 5.0
    CHEAT = True
    ANIM_NAME = "effort"

    def getAttackDisplayName(self):
        return (
            TTLocalizer.SuitAttackNames[self.attackType][0],
            TTLocalizer.SuitAttackNames[self.attackType][1] % ("WAITER'S" if self.extraArgs[0] else "COGS'"),
        )

    def doAttack(self):
        suitTrack = self.getSuitSayTrack()
        damageTracks = Parallel()

        suits = []
        for suit in self.targetObjs:
            result = self.findTarget(suit.doId)
            damageHP = result.hpAdjust
            damageTracks.append(
                Sequence(
                    Wait(2.783),
                    Func(self.updateSuitHP, suit, damageHP, nonZero=True),
                )
            )
            if suit is not self.invoker:
                suits.append(suit)

        damageTrack = Sequence(Parallel(Sequence(damageTracks), Wait(3)))

        waiterUsury = self.extraArgs[0]
        if waiterUsury:
            cutsceneLoader = CutsceneLoader.createLoader(
                key=CutsceneKeyEnum.Plutocrat_Investor_Usury,
                styx=self.invoker,
                waiter=suits[0],
                battle=self.battle,
            )
        else:
            cutsceneLoader = CutsceneLoader.createLoader(
                key=CutsceneKeyEnum.Plutocrat_Investor_Usury_Fodder,
                styx=self.invoker,
                suits=suits,
                battle=self.battle,
            )

        return Parallel(suitTrack, damageTrack, cutsceneLoader.buildCutscene())

    def getCameraShot(self, duration):
        return Wait(duration)


@AttackClass(attackType=AttackEnum.TRIBUTE)
class Tribute(Attack):
    OPEN_SHOT_DUR = 6.0
    CHEAT = True
    ANIM_NAME = "effort"

    def doAttack(self):
        damageTracks = Parallel()
        target = None

        for suit in self.targetObjs:
            result = self.findTarget(suit.doId)
            damageHP = result.hpAdjust

            if suit is self.invoker:
                seq = Sequence(
                    Wait(1.56),
                    Func(self.updateSuitHP, suit, damageHP),
                    Func(suit.neutralAvatar),
                )
            else:
                target = suit
                response = random.choice(TTLocalizer.MovieSuitHealResponses)
                seq = Sequence(
                    Wait(1.56),
                    Func(self.updateSuitHP, suit, damageHP),
                    Func(suit.setChatAbsolute, response, CFSpeech | CFTimeout),
                    Func(suit.neutralAvatar),
                )
            damageTracks.append(seq)

        cutsceneLoader = CutsceneLoader.createLoader(
            key=CutsceneKeyEnum.Plutocrat_Investor_Tribute,
            kerberos=self.invoker,
            target=target,
            battle=self.battle,
        )

        return Parallel(
            damageTracks,
            self.getSuitSayTrack(),
            Sequence(
                cutsceneLoader.buildCutscene(),
                Func(camera.wrtReparentTo, self.battle),
            )
        )

    def getCameraShot(self, duration):
        return Wait(duration)
    
    def getAttackDisplayName(self):
        """Give a special shout out to the investor that was
        picked to be healed :)
        """
        name = super().getAttackDisplayName()
        if not self.targetObjs or len(self.targetObjs) < 2:
            return name[0], name[1] % "A RANDOM INVESTOR!"
        return name[0], name[1] % TTLocalizer.suitName(self.targetObjs[1].dna.name)


@AttackClass(attackType=AttackEnum.PCRAT_INVESTOR_DEATH_PHRASE)
class PlutocratInvestorDeathPhrase(AvatarSayPhraseAttack):
    ClearChat = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.whoDied = [InvestorEnum2Name[suitEnum] for suitEnum in self.investorEnums]

    @property
    def investorEnums(self):
        return self.extraArgs[1:]

    @property
    def avatar(self):
        if getattr(self.battle.instance, 'cutscenePlutocrat', None):
            return self.battle.instance.cutscenePlutocrat
        return None

    @property
    def phraseBank(self):
        if len(self.whoDied) > 1:
            return self.phraseData[0]["multiple"]
        else:
            return self.phraseData[0][self.whoDied[0]]

    def doAttack(self):
        if not self.avatar:
            return Sequence(Wait(0.5))

        # Grab a phrase that will be consistent across all clients
        phraseIndex = self.avatar.doId % len(self.phraseBank)
        phrase = self.phraseBank[phraseIndex]
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
        return self.camera.heldRelativeShot(
            self.battle, 0, 10.5, 8, 0, 7.5, 0, duration=duration, name='plutocratSpeechHeldRelativeShot')


@AttackClass(attackType=AttackEnum.RUSH_JOB)
class RushJob(Attack):
    ANIM_NAME = "rushjob"
    OPEN_SHOT_DUR = 1.1
    CHEAT = True

    def doAttack(self):
        suitTrack = self.getSuitAnimTrack(doActorInterval=False)
        soundTrack = self.getSoundTrack("phase_9/audio/sfx/SA_rush_job_target.ogg")

        def updateArrows():
            applyTrack = Parallel()
            for av in self.targetObjs:
                visualEffect = av.getVisualEffectOfId(VisualEffectEnum.RUSH_JOB)
                if visualEffect:
                    visualEffect._doUnapply()
                MovieUtil.unapplyVisualEffect(av, VisualEffectEnum.RUSH_JOB)
                movieSeq = Sequence()
                applyMovie, _ = MovieUtil.applyVisualEffect(av, VisualEffectEnum.RUSH_JOB, useMovieApply=True)
                visualEffect = av.getVisualEffectOfId(VisualEffectEnum.RUSH_JOB)
                visualEffect.setGagTrack(self.extraArgs[0])
                movieSeq.append(applyMovie)
                applyTrack.append(movieSeq)
            applyTrack.start(playRate=self.battle.timescale)

        unlureTrack = Parallel()
        for av in self.targetObjs:
            if av.isLured:
                unlureTrack.append(self.getResetTrack(av))
            av.isLured = False

        suitTrack = Parallel(
            suitTrack,
            Sequence(
                Wait(0.5),
                Func(updateArrows),
                Parallel(
                    unlureTrack,
                    soundTrack,
                ),
            ),
        )
        return Sequence(
            self.getResetTrack(), 
            suitTrack, 
            Func(self.invoker.loop, "neutral"), 
            Wait(4.6),
        )

    def getAttackDisplayName(self) -> str:
        if self.invoker.dna.name == 'psetter':
            nameInfo = TTLocalizer.SuitAttackNames.get(self.attackType, "")
        else:
            nameInfo = TTLocalizer.SuitAttackBonusPhrases['rushjob'].get(self.invoker.dna.name, "")

        trackName = TTLocalizer.ToonTrackNames[self.extraArgs[0]]
        trackName = f"\1toon_track_{int(self.extraArgs[0])}\1{trackName} TRACK\2"
        if isinstance(self.targetObjs[0], DistributedSuitBase):
            targetName = f"THE {TTLocalizer.suitName(self.targetObjs[0].dna.name)}"
        else:
            targetName = self.targetObjs[0].getName()
        return nameInfo[0], nameInfo[1] % (trackName, targetName)

    def getCameraShot(self, duration):
        cutsceneKey = CutsceneKeyEnum.FindTheFamily_Attorney_RushJob if self.invoker.style.name == 'ftf_l' else CutsceneKeyEnum.Pacesetter_RushJob
        cutsceneLoader = CutsceneLoader.createLoader(
            key=cutsceneKey,
            toons=self.battle.activeToons,
            pacesetter=self.invoker,
            target=self.targetObjs[0],
            battle=self.battle,
        )
        return Parallel(cutsceneLoader.buildCutscene(), Wait(duration))


@AttackClass(attackType=AttackEnum.HURRY_SICKNESS)
class HurrySickness(SuitGroupAttack):
    ANIM_NAME = "finger-wag"
    OPEN_SHOT_DUR = 2.3
    CHEAT = True

    def updateArrows(self):
        for av in self.battle.activeSuits:
            visualEffect = av.getVisualEffectOfId(VisualEffectEnum.RUSH_JOB)
            if visualEffect:
                visualEffect._doUnapply()
            MovieUtil.unapplyVisualEffect(av, VisualEffectEnum.RUSH_JOB)

    def doAttack(self):
        suitTrack = self.getSuitTrack()
        toonTracks = self.getToonTracks(2.7, ["slip-backward"], 1.8, ["sidestep"])
        soundTrack = self.getSoundTrack(
            "SA_finger_wag.ogg", delay=1.3, node=self.invoker
        )
        buzzerTrack = self.getSoundTrack("phase_9/audio/sfx/SA_hurry_sickness.ogg")

        return Parallel(suitTrack, toonTracks, soundTrack, buzzerTrack, Func(self.updateArrows))

    def getAttackDisplayName(self) -> str:
        if self.invoker.dna.name == 'psetter':
            return TTLocalizer.SuitAttackNames.get(self.attackType, "")
        else:
            return TTLocalizer.SuitAttackBonusPhrases['hurry_sickness'].get(self.invoker.dna.name, "")


@AttackClass(attackType=AttackEnum.HURRY_SICKNESS_MG)
class HurrySicknessMG(HurrySickness):
    def updateArrows(self):
        return


@AttackClass(attackType=AttackEnum.CORPORATE_RESTRUCTURING)
class CorporateRestructuring(Attack):
    ANIM_NAME = "quick-jump"
    CHEAT = True
    DAMAGE_DELAY = 1.5

    def doAttack(self):
        suitTrack = self.getSuitAnimTrack()
        suitTracks = Parallel()

        def sortActiveSuit(suit):
            if suit in self.targetObjs:
                result = self.findTarget(suit.doId)
                if result:
                    return result.extraArgs[0]
            return -1

        activeSuits = sorted(self.battle.activeSuits, key=sortActiveSuit)
        for suit in self.targetObjs:
            result = self.findTarget(suit.doId)
            index = result.extraArgs[0]
            newPos, newHpr = self.battle.getSuitBattlePosHpr(suit, activeSuits)
            if suit.isLured:
                newPos.setY(newPos[1] - MovieUtil.SUIT_LURE_DISTANCE)

            if suit is self.invoker:
                if self.battle.activeSuits.index(suit) != activeSuits.index(suit):
                    # yeah
                    yeah = self.battle.attachNewNode("yeah")
                    yeah.setPos(self.battle.getActiveSuitPosHpr(suit)[0])
                    yeah.lookAt(newPos)
                    suitTrack = Parallel(
                        suitTrack,
                        Sequence(
                            LerpHprInterval(suit, self.DAMAGE_DELAY, yeah.getHpr(self.battle), startHpr=suit.getHpr(self.battle), other=self.battle, fluid=1),
                            LerpPosInterval(suit, 2.0, newPos, fluid=1, other=self.battle),
                            LerpHprInterval(suit, 1.0, newHpr, startHpr=yeah.getHpr(), other=self.battle, fluid=1)
                        ),
                    )
                    yeah.detachNode()
                continue

            # This will take the values from the old suit list
            suitStartPos, _ = self.battle.getActiveSuitPosHpr(suit)
            suitFloat = Point3(0, 0, 28)
            suitEndPos = Point3(
                suitStartPos[0] + suitFloat[0],
                suitStartPos[1] + suitFloat[1],
                suitStartPos[2] + suitFloat[2],
            )
            suitAbovePos = Point3(
                newPos[0] + suitFloat[0],
                newPos[1] + suitFloat[1],
                newPos[2] + suitFloat[2],
            )
            suitType = getSuitBodyType(suit.getStyleName())
            if suitType == "a":
                startFlailFrame = 16
                endFlailFrame = 16
            elif suitType == "b":
                startFlailFrame = 15
                endFlailFrame = 15
            else:
                startFlailFrame = 15
                endFlailFrame = 15
            sival = Sequence(
                ActorInterval(
                    suit,
                    "slip-backward",
                    playRate=0.5,
                    startFrame=0,
                    endFrame=startFlailFrame - 1,
                ),
                Func(
                    suit.pingpong,
                    "slip-backward",
                    fromFrame=startFlailFrame,
                    toFrame=endFlailFrame,
                ),
                Wait(0.5),
                ActorInterval(
                    suit, "slip-backward", playRate=1.0, startFrame=endFlailFrame
                ),
                Wait(0.05),
                Func(suit.loop, 'neutral'),
            )
            sUp = LerpPosInterval(suit, 1.1, suitEndPos, startPos=suitStartPos, other=self.battle, fluid=1)
            sDown = Parallel(
                LerpPosInterval(
                    suit, 0.6, newPos, startPos=suitAbovePos, other=self.battle, fluid=1
                ),
                LerpHprInterval(
                    suit, 0.6, newHpr, startHpr=suit.getHpr(), other=self.battle, fluid=1
                )
            )
            geyserMotion = Sequence(sUp, Wait(0.0), sDown)
            suitTracks.append(Parallel(sival, geyserMotion))

        # Now that everything else is done, adjust the actual battle suits list.
        newSuitsList = []
        for suitId in self.extraArgs:
            newSuitsList.append(self.battle.getSuit(suitId))
        self.battle.suits = newSuitsList[:]

        soundTrack = self.getSoundTrack("SA_quake.ogg", delay=0, node=self.invoker)
        return Sequence(Parallel(suitTrack, soundTrack, Sequence(Wait(self.DAMAGE_DELAY), suitTracks)), Func(self.invoker.loop, 'neutral'))

    def getCameraShot(self, duration):
        return self.camera.allGroupOverheadShot(duration=duration)

    def getAttackDisplayName(self) -> str:
        if self.invoker.dna.name == 'psetter':
            return TTLocalizer.SuitAttackNames.get(self.attackType, "")
        else:
            return TTLocalizer.SuitAttackBonusPhrases['corporate_restructuring'].get(self.invoker.dna.name, "")


@AttackClass(attackType=AttackEnum.CONTENT_SYNC)
class ContentSync(Attack):
    ANIM_NAME = "magic3"
    OPEN_SHOT_DUR = 1.1
    CHEAT = True

    def doAttack(self):
        BattleParticles.loadParticles()

        damageDelay = 1.7
        damageAnims = [
            ["neutral", 0.01, 0.01, 0.5],
            ["juggle", 0.01, 0.01, 1.48],
            ["think", 0.01, 2.28],
        ]
        dodgeAnims = []
        dodgeAnims.append(["think", 0.01, 0, 0.6])

        headTracks = Parallel()
        chestTracks = Parallel()
        partTracks = Parallel()
        toonTracks = Parallel()
        suitTrack = self.getSuitTrack()

        toonTracks.append(self.getToonTracks(
            damageDelay=damageDelay,
            splicedDamageAnims=damageAnims,
            showDamageExtraTime=2.1,
            showMissedExtraTime=2.0,
            forceHit=1,
        ))

        for target in self.targetDicts:
            toon = target["avatar"]
            attackDelay = 1.7
            sprayEffect = BattleParticles.createParticleEffect(file="reorgSpray")
            partTracks.append(self.getPartTrack(
                sprayEffect, 1.0, 1.9, [sprayEffect, self.invoker, 0]
            ))
            headParts = toon.getHeadParts()
            for part in headParts:
                x = part.getX()
                y = part.getY()
                z = part.getZ()
                h = part.getH()
                p = part.getP()
                r = part.getR()
                headTracks.append(
                    Sequence(
                        Wait(attackDelay),
                        LerpPosInterval(part, 0.1, Point3(x - 0.2, y, z - 0.03)),
                        LerpPosInterval(part, 0.1, Point3(x + 0.4, y, z - 0.03)),
                        LerpPosInterval(part, 0.1, Point3(x - 0.4, y, z - 0.03)),
                        LerpPosInterval(part, 0.1, Point3(x + 0.4, y, z - 0.03)),
                        LerpPosInterval(part, 0.1, Point3(x - 0.2, y, z - 0.04)),
                        LerpPosInterval(part, 0.25, Point3(x, y, z + 2.2)),
                        LerpHprInterval(part, 0.4, VBase3(360, 0, 180)),
                        LerpPosInterval(part, 0.3, Point3(x, y, z + 3.1)),
                        LerpPosInterval(part, 0.15, Point3(x, y, z + 0.3)),
                        Wait(0.15),
                        LerpHprInterval(
                            part, 0.6, VBase3(-745, 0, 180), startHpr=VBase3(0, 0, 180)
                        ),
                        LerpHprInterval(
                            part, 0.8, VBase3(25, 0, 180), startHpr=VBase3(0, 0, 180)
                        ),
                        LerpPosInterval(part, 0.15, Point3(x, y, z + 1)),
                        LerpHprInterval(part, 0.3, VBase3(h, p, r)),
                        Wait(0.2),
                        LerpPosInterval(part, 0.1, Point3(x, y, z)),
                        Wait(0.9),
                    )
                )

            def getChestTrack(part, attackDelay=attackDelay):
                origScale = part.getScale()
                return Sequence(
                    Wait(attackDelay),
                    LerpHprInterval(part, 1.1, VBase3(180, 0, 0)),
                    Wait(1.1),
                    LerpHprInterval(part, 1.1, part.getHpr()),
                )

            arms = toon.findAllMatches("**/arms")
            sleeves = toon.findAllMatches("**/sleeves")
            hands = toon.findAllMatches("**/hands")
            for part in arms + sleeves + hands:
                chestTracks.append(getChestTrack(part))

        return Parallel(suitTrack, partTracks, toonTracks, headTracks, chestTracks)

    def getCameraShot(self, duration):
        return self.camera.randomGroupAttackCam(
            self.invoker, self.targetDicts, self.battle, duration, self.OPEN_SHOT_DUR)

    def getAttackDisplayName(self) -> str:
        if self.invoker.dna.name == 'psetter':
            return TTLocalizer.SuitAttackNames.get(self.attackType, "")
        else:
            return TTLocalizer.SuitAttackBonusPhrases['content_sync'].get(self.invoker.dna.name, "")


@AttackClass(attackType=AttackEnum.MOVING_GOALPOSTS)
class MovingGoalposts(SuitSingleAttack):
    ANIM_NAME = "magic3"
    OPEN_SHOT_DUR = 1.7
    CHEAT = True

    def doAttack(self):
        suitTrack = self.getSuitAnimTrack()
        allToonTracks = Parallel()

        for target in self.targetDicts:
            damageDelay = 1.7 + (random.random() * 0.2)
            toon = target["avatar"]
            sprayEffect = BattleParticles.createParticleEffect(file="spinSpray")
            spinEffect1 = BattleParticles.createParticleEffect(file="spinEffect")
            spinEffect2 = BattleParticles.createParticleEffect(file="spinEffect")
            spinEffect3 = BattleParticles.createParticleEffect(file="spinEffect")
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
            particleNode = self.invoker.attachNewNode('moving-goalposts-particle-node')
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
                forceHit=True,
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


@AttackClass(attackType=AttackEnum.ROCKING_IN_RHYTHM)
class RockingInRhythm(Attack):
    ANIM_NAME = "song-and-dance"
    OPEN_SHOT_DUR = 4.1
    CHEAT = True
    
    def doAttack(self):
        damageDelay = 4.2
        mp = None
        for suit in self.battle.activeSuits:
            if getattr(suit.dna, "name", "mplayer"):
                mp = suit
                break
        if mp is None:
            return Sequence()

        toonTracks = Parallel()

        passedLastTapDance = False
        # Toons dance if they take no damage.
        for toon in self.battle.activeToons:
            if toon not in self.targetObjs:
                toonTracks.append(Sequence(
                    Wait(damageDelay),
                    ActorInterval(toon, "victory"),
                    Func(toon.loop, "neutral"),
                ))

                # If you someone somehow pass the Phase 2 dance, do some funnies
                if mp.getStatusEffectOfId(SEE.EFFECT_LAST_TAP):
                    passedLastTapDance = True

        toonTracks.append(
            self.getToonTracks(
                damageDelay, ["cringe"], damageDelay, ["dance"]
            )
        )

        if passedLastTapDance:
            def getDanceTrack(amount=6):
                track = Sequence()
                for _ in range(amount):
                    track.append(ActorInterval(mp, self.getAnimName(), playRate=amount))
                return track

            suitTrack = Sequence(
                Func(mp.setChatAbsolute, CutsceneLocalizer.MajorPlayerLastTapDanceSuccess[0], CFSpeech | CFTimeout),
                getDanceTrack(),
                Func(mp.setChatAbsolute, CutsceneLocalizer.MajorPlayerLastTapDanceSuccess[1], CFSpeech | CFTimeout),
                getDanceTrack(),
            )
        else:
            suitTrack = Sequence(
                Func(mp.setChatAbsolute, self.getAttackTaunt(), CFSpeech | CFTimeout),
                ActorInterval(mp, self.getAnimName()),
            )
        if mp in self.targetObjs:
            mpDict = self.findTargetDict(mp.doId)
            hp = mpDict.get("hp", 0)
            if hp < 0:
                suitTrack.append(Parallel(
                    ActorInterval(mp, "pie-small-react"),
                    Func(self.updateSuitHP, mp, hp)
                ))
        suitTrack.append(Func(mp.neutralAvatar))

        soundTrack = self.getSoundTrack("AA_heal_happydance.ogg", node=self.invoker)
        return Parallel(suitTrack, toonTracks, soundTrack)
    
    def getCameraShot(self, duration):
        return self.camera.allGroupLowerOverheadShot(duration=duration)


@AttackClass(attackType=AttackEnum.STAR_OF_THE_SHOW)
class StarOfTheShow(Attack):
    ANIM_NAME = "song-and-dance"
    OPEN_SHOT_DUR = 4.1
    CHEAT = True

    def doAttack(self):
        suitIndex, *_ = self.extraArgs
        if suitIndex == -1:
            # No more audience members. Copium
            return Sequence()

        # Start putting the movie together
        cutsceneLoader = CutsceneLoader.createLoader(
            key=CutsceneKeyEnum.MajorPlayer_StarOfTheShow,
            mplayer=self.invoker,
            battle=self.battle,
        )

        # Return the movie
        return Parallel(cutsceneLoader.buildCutscene(), self.getSuitAnimTrack())

    def getCameraShot(self, duration):
        return Wait(duration)


@AttackClass(attackType=AttackEnum.STAR_OF_THE_SHOW_END)
class StarOfTheShowEnd(AllowGroupingAttack):

    def doAttack(self):
        return Sequence(
            Func(self.clearStagelight),
            Func(self.targetObjs[0].setMaxHp, self.extraArgs[1]),
            Func(self.targetObjs[0].setHp, self.extraArgs[0]),
            Func(self.targetObjs[0].clearColorScale),
            SoundInterval(sound=loader.loadSfx('phase_11/audio/sfx/LB_camera_shutter_2.ogg')),
        )

    def clearStagelight(self):
        target = self.targetObjs[0]
        stagelight = getattr(target, 'cutsceneStagelight', None)
        if stagelight:
            stagelight.removeNode()
            del target.cutsceneStagelight

    def getCameraShot(self, duration):
        return self.camera.allGroupOverheadShot(duration=duration)


@AttackClass(attackType=AttackEnum.GUEST_VERSE_START)
class GuestVerseStart(Attack):
    ANIM_NAME = "neutral"
    OPEN_SHOT_DUR = 2.0
    CHEAT = True

    def doAttack(self):
        hasRevived = self.extraArgs[0]
        isStar = self.extraArgs[1]
        colorScaleSequence = Sequence() if hasRevived else Sequence(Func(render.setColorScale, 0.1, 0.1, 0.1, 1))

        soundTrack = self.getSoundTrack("phase_11/audio/sfx/LB_camera_shutter_2.ogg", node=self.invoker)
        snapTrack = self.getSoundTrack("phase_11/audio/sfx/SA_bash.ogg", node=self.invoker)

        def changeCutsceneStagelight():
            target = self.targetObjs[0]
            stagelight = getattr(target, 'cutsceneStagelight', None)
            if stagelight:
                growStagelight(stagelight)

        def guestStagelight():
            # Make a fake stagelight that looks like a normal one but bigger and brighter.
            stagelight = globalPropPool.getProp('stagelight')
            setattr(self.targetObjs[0], 'guestStagelight', stagelight)
            stagelight.hide()
            node = stagelight.node()
            from panda3d.core import OmniBoundingVolume
            node.setBounds(OmniBoundingVolume())
            node.setFinal(1)
            stagelight.find('**/stagelight').hide()

            # Position the stagelight.
            stagelight.reparentTo(self.targetObjs[0])
            stagelight.setPos(0, 0, 15 * 2)

            growStagelight(stagelight)

            return Sequence(Func(stagelight.show))

        def growStagelight(stagelight):
            stagelight.setScale(2, 2, 3)
            from toontown.utils import ColorHelper
            stagelight.setColor(ColorHelper.hexToPCol('FEFDA8', a=int(0.8 * 255)))

        stagelightTrack = Func(changeCutsceneStagelight) if isStar else guestStagelight()

        cutsceneLoader = CutsceneLoader.createLoader(
            key=CutsceneKeyEnum.MajorPlayer_GuestVerse,
            mplayer=self.invoker,
            guest=self.targetObjs[0],
            battle=self.battle,
        )
        return Parallel(cutsceneLoader.buildCutscene(),
                        self.getSuitAnimTrack(),
                        Sequence(Wait(2.2), snapTrack),
                        Sequence(Wait(2.691), Parallel(colorScaleSequence, soundTrack, stagelightTrack)))


@AttackClass(attackType=AttackEnum.GUEST_VERSE_END)
class GuestVerseEnd(Attack):
    def doAttack(self):
        hasRevived = self.extraArgs[0]
        isStar = self.extraArgs[1]
        colorScaleSequence = Sequence() if hasRevived else Sequence(Func(render.setColorScale, 1, 1, 1, 1))

        def removeFakeStagelight():
            target = self.invoker
            stagelight = getattr(target, 'guestStagelight', None)
            if stagelight:
                stagelight.removeNode()
                del target.guestStagelight

        def shrinkStagelight():
            target = self.invoker
            stagelight = getattr(target, 'cutsceneStagelight', None)
            if stagelight:
                stagelight.setScale(1, 1, 2)
                from toontown.utils import ColorHelper
                stagelight.setColor(ColorHelper.hexToPCol('FEFDA8', a=int(0.28 * 255)))

        soundTrack = self.getSoundTrack("phase_11/audio/sfx/LB_camera_shutter_2.ogg", node=self.invoker)
        stagelightSequence = Parallel(soundTrack)
        stagelightSequence.append(Func(shrinkStagelight) if isStar else Func(removeFakeStagelight))

        return Parallel(colorScaleSequence, stagelightSequence)

    def getCameraShot(self, duration):
        return self.camera.allGroupOverheadShot(duration=duration)


@AttackClass(attackType=AttackEnum.DANCE_PARTNERS)
class DancePartners(Attack):
    ANIM_NAME = "song-and-dance"
    OPEN_SHOT_DUR = 4.1
    CHEAT = True

    def doAttack(self):
        pairCount, *pairs = self.extraArgs
        if pairCount == 0:
            # No pairs were made.
            return Sequence()

        # Start putting the movie together
        cutsceneLoader = CutsceneLoader.createLoader(
            key=CutsceneKeyEnum.MajorPlayer_DancePartners,
            mplayer=self.invoker,
            battle=self.battle,
        )

        # Return the movie
        return Parallel(cutsceneLoader.buildCutscene(), self.getSuitAnimTrack())

    def getCameraShot(self, duration):
        return Wait(duration)


@AttackClass(attackType=AttackEnum.TOON_STAR_BONUS_TEXT)
class ToonStarBonusText(PowerNapKillDamageUp):
    BaseString = '\1damage_subtext_orange\1STARDOM!\2\n+{0} DMG UP!'


@AttackClass(attackType=AttackEnum.CUT_THE_SLACK)
class CutTheSlack(SuitSingleAttack):
    ANIM_NAME = "snap-override"
    CHEAT = True

    def doAttack(self):
        specialMan: DistributedSuitBase = base.cr.getDo(self.extraArgs[0])

        if specialMan:
            def loopNeutralAnim():
                loopAnim = "lured" if specialMan.isLured else "neutral"
                specialMan.loop(loopAnim)

            def updateDNA():
                specialMan.setElite(1)
                specialMan.setLevel(self.extraArgs[1])
                specialMan.setMaxHp(int(specialMan.getHp() * 1.5))
                specialMan.healthBar.updateMeterMode(SuitHealthMeter.MODE_BATTLE)
                specialMan.healthBar.updateHealthBar(forceUpdate=1)

                specialMan.setDisplayName(specialMan.createNameInfo())
            
            def getDustCloudIval():
                dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
                dustCloud.setBillboardAxis(2.0)
                dustCloud.setZ(3)
                dustCloud.setScale(1.0)
                dustCloud.createTrack()
                return Sequence(Func(dustCloud.reparentTo, specialMan), dustCloud.track, Func(dustCloud.destroy),
                                name='dustCloudIval')

            specialManTrack = Sequence(
                Func(updateDNA),
                Parallel(
                    getDustCloudIval(),
                    Func(specialMan.showHpString, "PROMOTED!", 0.85, 0.7, (1, 1, 1, 1)),
                    ActorInterval(specialMan, 'slip-forward', startTime=2.43),
                ),
                Func(loopNeutralAnim),
            )
        else:
            return Sequence()

        suitTrack = self.getSuitAnimTrack()
        sfx = self.getSoundTrack(
            "phase_11/audio/sfx/SA_bash.ogg", delay=0.1, node=self.invoker
        )
        targetTrack = Parallel()
        for target in self.targetObjs:
            if target is specialMan:
                continue
            targetTrack.append(MovieUtil.suitDisintegrateTrack(target, self.battle))

        return Parallel(suitTrack, sfx, Sequence(Wait(1), targetTrack), Sequence(Wait(2 if self.targetObjs else 1), specialManTrack))

    def getCameraShot(self, duration):
        return self.camera.allGroupOverheadShot(duration=duration)
    
    def getEndTrack(self):
        # Override this track in favor of the disintegrate track.
        return Sequence()


@AttackClass(attackType=AttackEnum.MARKED_WOOD)
class MarkedWood(SuitSingleAttack):
    ANIM_NAME = "throw-paper"
    CHEAT = True
    OPEN_SHOT_DUR = 3.2

    def doAttack(self):
        target = self.targetDicts[0]
        toon = target["avatar"]
        log = globalPropPool.getProp("treekiller_log")
        suitDelay = 2.34
        damageDelay = 3.66
        dodgeDelay = 2.76
        suitTrack = self.getSuitTrack()
        logPosPoints = [Point3(-0.1, 0.6, 0.0), VBase3(-1.152, 86.581, -76.784)]
        propTrack = Sequence(
            self.getPropAppearTrack(
                log,
                self.invoker.getRightHand(),
                logPosPoints,
                0.7,
                Point3(0.6, 1.0, 1.0),
                scaleUpTime=0.25,
            )
        )
        propTrack.append(Wait(suitDelay))
        propTrack.append(Func(self.battle.movie.needRestoreRenderProp, log))
        propTrack.append(Func(log.wrtReparentTo, self.battle))

        propTrack.append(
            LerpPosInterval(log, 0.3, self.toonFacePoint(toon, parent=self.battle))
        )
        soundTrack = self.getSoundTrack(
            "SA_hardball_impact_only.ogg", delay=2.9, node=self.invoker
        )
        hitSoundTrack = self.getSoundTrack("SA_woodchipper.ogg", delay=damageDelay - 0.1, node=toon)

        # Particle track.
        BattleParticles.loadParticles()
        freezeEffect = BattleParticles.createParticleEffect(file="treekillerWoodchips")
        facePoint = self.toonFacePoint(toon)
        freezeEffect.setPos(toon.getPos() + (0, 0, facePoint.getZ()))
        partTrack2 = self.getPartTrack(
            freezeEffect, propTrack.getDuration(), 0.5, [freezeEffect, render, 0]
        )

        propTrack.append(LerpScaleInterval(log, 0.05, MovieUtil.PNT3_NEARZERO))
        propTrack.append(Func(MovieUtil.removeProp, log))
        propTrack.append(Func(self.battle.movie.clearRenderProp, log))
        damageAnims = [
            ["cringe", damageDelay, 0.01],
        ]
        toonTrack = self.getToonTrack(
            splicedDamageAnims=damageAnims,
            dodgeDelay=dodgeDelay,
            dodgeAnimNames=["sidestep"],
            showDamageExtraTime=damageDelay,
            forceHit=True,
            hpTextType=TTLocalizer.HP_TEXT_MARKEDWOOD,
        )

        effectTrack = Sequence(
            Wait(damageDelay),
            Func(MovieUtil.applyVisualEffect, toon, VisualEffectEnum.MARKED_WOOD),
        )

        return Parallel(
            suitTrack, toonTrack, propTrack, partTrack2, soundTrack, hitSoundTrack, effectTrack
        )

    def getCameraShot(self, duration):
        toon = self.targetDicts[0]["avatar"]
        closeDur = duration - self.OPEN_SHOT_DUR
        openShot = self.camera.randomOverShoulderShot(
            self.invoker,
            self.targetDicts[0]["avatar"],
            self.battle,
            self.OPEN_SHOT_DUR,
            "suit",
        )
        closeShot = self.camera.randomActorShot(toon, self.battle, closeDur, "avatar")
        return Sequence(openShot, closeShot)

    def getSplicedAnimsTrack(self, anims, actor=None, playRate=1.0):
        return super().getSplicedAnimsTrack(anims, actor=actor, playRate=1.5)


@AttackClass(attackType=AttackEnum.SNOW_SQUALL)
class SnowSquall(SuitSingleAttack, AvatarSayPhraseAttack):
    ANIM_NAME = "effort"
    CHEAT = True
    OPEN_SHOT_DUR = 8.0

    def doAttack(self):
        suitTrack = Parallel(
            AvatarSayPhraseAttack.doAttack(self),
            # ActorInterval(self.invoker, self.ANIM_NAME),
        )
        # Toggle the ambience and music.
        cutsceneSeq = Sequence()
        music = base.instance.getPreloadedSong('plutocrat_battle_cold' if self.extraArgs[1] else 'plutocrat_battle')
        if self.extraArgs[1]:
            ambienceSeq = Parallel(
                Func(base.instance.ambienceSnowSquall),
                Func(base.musicMgr.crossfadeIntoMusic, music,
                     duration=3.0, delay=0.0, looping=1, matchTime=True, volume=1.0, musicCode='plutocrat_battle_cold')
            )
            cutscene = CutsceneLoader.createLoader(
                CutsceneKeyEnum.Plutocrat_SnowSquall_Start,
                toons=self.toons,
                plutocrat=self.invoker,
                battle=self.battle,
                instance=self.battle.instance,
            ).buildCutscene()
            cutsceneSeq.append(cutscene)
        else:
            ambienceSeq = Parallel(
                Func(base.instance.ambienceDefault),
                Func(base.musicMgr.crossfadeIntoMusic, music, duration=3.0, delay=0.0, looping=1,
                     matchTime=True, volume=1.0, musicCode='plutocrat_battle')
            )
            openHatch = CutsceneLoader.createLoader(
                key=CutsceneKeyEnum.Plutocrat_JoinBattle_Hatch_Open,
                instance=self.battle.bossCog
            ).buildCutscene()
            cutscene = CutsceneLoader.createLoader(
                CutsceneKeyEnum.Plutocrat_SnowSquall_End,
                toons=self.toons,
                plutocrat=self.invoker,
                battle=self.battle,
                instance=self.battle.instance,
            ).buildCutscene()
            closeHatch = CutsceneLoader.createLoader(
                key=CutsceneKeyEnum.Plutocrat_JoinBattle_Hatch_Close,
                instance=self.battle.bossCog
            ).buildCutscene()
            cutsceneSeq.append(openHatch)
            cutsceneSeq.append(cutscene)
            cutsceneSeq.append(closeHatch)

        def loopNeutralAnim(suit):
            loopAnim = "lured" if suit.isLured else "neutral"
            suit.loop(loopAnim)

        return Sequence(
            Parallel(
                cutsceneSeq,
                Sequence(Wait(.5), suitTrack, Func(loopNeutralAnim, self.invoker)),
                Sequence(Wait(1.5), ambienceSeq),
            ),
        )

    def getAttackDisplayName(self):
        """There are two possible outcomes for Snow Squall,
        thus in order to provide the correct description, index the
        description tuple with the second value in our extraArgs.
        """
        nameInfo = super().getAttackDisplayName()

        # This shouldn't ever happen, but just in-case.
        if len(self.extraArgs) < 2:
            return nameInfo[0]

        # Return the correct name/desc pair.
        return (nameInfo[0], nameInfo[1][int(self.extraArgs[1])])


@AttackClass(attackType=AttackEnum.SNOW_SQUALL_DAMAGE)
class SnowSquallDamage(AllowGroupingAttack):
    CHEAT = True
    OPEN_SHOT_DUR = 1.7

    def doAttack(self):
        partTrack = Parallel()
        BattleParticles.loadParticles()
        coldExpressionTrack = Parallel()
        normalExpressionTrack = Parallel()
        for target in self.targetDicts:
            toon = target['avatar']
            freezeEffect = BattleParticles.createParticleEffect("DemotionFreeze")
            unFreezeEffect = BattleParticles.createParticleEffect(file="demotionUnFreeze")
            BattleParticles.setEffectTexture(freezeEffect, "snow-particle")
            BattleParticles.setEffectTexture(unFreezeEffect, "snow-particle")

            partTrack2 = self.getPartTrack(freezeEffect, 0.4, 2.9, [freezeEffect, toon, 0])
            partTrack3 = self.getPartTrack(
                unFreezeEffect, 5.5, 0.5, [unFreezeEffect, toon, 0]
            )
            facePoint = self.toonFacePoint(toon, parent=toon)
            freezeEffect.setPos(0, 0, facePoint.getZ() - 1.5)
            unFreezeEffect.setPos(0, 0, facePoint.getZ() - 1.5)
            partTrack.append(Parallel(partTrack2, partTrack3))

            toonGeom = toon.getGeomNode()
            coldExpressionTrack.append(Parallel(Func(toon.showAngryMuzzle), Func(toon.sadEyes)))
            coldExpressionTrack.append(LerpColorScaleInterval(toonGeom, 5.0, (.5, .9, 1.0, 1.0)))
            coldExpressionTrack.append(Sequence(Wait(6.0), self.getToonTrack(forceHit=True, lookAtInvoker=False, target=target)))
            normalExpressionTrack.append(
                Parallel(
                    Func(toon.normalEyes),
                    Func(toon.hideAngryMuzzle),
                    Func(toon.blinkEyes),
                    LerpColorScaleInterval(toonGeom, .5, (1.0, 1.0, 1.0, 1.0))
                )
            )

        cutscene = CutsceneLoader.createLoader(
            CutsceneKeyEnum.Plutocrat_SnowSquall_Damage,
            toons=self.targetObjs, battle=self.battle, instance=self.battle.instance
        ).buildCutscene()

        return Sequence(Parallel(cutscene, partTrack, coldExpressionTrack), normalExpressionTrack)
    
    def getCameraShot(self, duration):
        # Handled by the cutscene loader
        return Sequence(Wait(duration))


@AttackClass(attackType=AttackEnum.SHATTER_DAMAGE)
class ShatterDamage(SuitDamageAttack):
    ALLOW_GROUPING = False
    CHEAT = True

    def doAttack(self):
        # the actual damage anim from shatter
        sfx = loader.loadSfx("phase_10/audio/sfx/SA_shatter_hit.ogg")
        damageTracks = Parallel()
        for suit in self.targetObjs:
            result = self.findTarget(suit.doId)
            damageHP = result.hpAdjust

            def loopNeutralAnim(suit):
                loopAnim = "lured" if suit.isLured else "neutral"
                suit.loop(loopAnim)

            seq = Sequence(
                Parallel(
                    Func(self.updateSuitHP, suit, damageHP),
                    SoundInterval(sfx),
                    ActorInterval(suit, random.choice(["squirt-small-react", 'pie-small-react']))
                ),
                Func(loopNeutralAnim, suit)
            )

            # the plutocrat has his own specil interaction with shattering
            # if the market bubble is active, show that it has burst
            from toontown.battle.statuses.StatusEffectEnums import StatusEffectEnum as SEE
            plutoStatus = suit.getStatusEffectOfId(SEE.EFFECT_MANAGER_PLUTOCRAT)
            if plutoStatus:
                if plutoStatus.marketBubbleStacks > 0:
                    suitPos, _ = self.battle.getActorPosHpr(suit)
                    explosionPoint = Point3(suitPos.getX(), suitPos.getY(), suitPos.getZ() + suit.height - 0.5)
                    burstTextTrack = Sequence(
                        Wait(2.0),
                        Func(suit.hideHpText),
                        Func(suit.showHpString, "BUBBLE BURST!", 0.85, 0.7, (1, 1, 1, 1)),
                    )
                    seq = Sequence(
                        Parallel(
                            seq,
                            burstTextTrack,
                            Func(MovieUtil.unapplyVisualEffect, suit, VisualEffectEnum.MARKET_BUBBLE),
                            MovieUtil.createKapowExplosionTrack(self.battle, explosionPoint=explosionPoint)
                        ),
                    )

            damageTracks.append(seq)


        return Sequence(
            Parallel(damageTracks)
        )

    def updateSuitHP(self, suit, damage):
        suit.updateHealthBar(damage)
        suit.showHpText(damage, extraText=self.EXTRA_TEXT or "")


@AttackClass(attackType=AttackEnum.BEWITCHMENT)
class Bewitchment(SuitSingleAttack):
    ANIM_NAME = "magic3"
    CHEAT = True

    def doAttack(self):
        suitTrack = self.getSuitAnimTrack()
        toonTracks = Parallel()

        for toon in self.targetObjs:
            # applyMovie, _ = self.getBewitchmentVisualEffect(toon).getApplyMovie()
            BattleParticles.loadParticles()
            spinEffectTracks = []
            for i in range(3):
                spinEffect = BattleParticles.createParticleEffect(file='bewitchedSpin')
                spinEffect.reparentTo(toon)
                height = toon.getHeight() * (random.random() * 0.2 + 0.1 + i * 0.3)
                spinEffect.setPos(0.8, -0.7, height)
                spinEffect.setHpr(0, 0, -random.random() * 10 - 85)
                spinEffect.setHpr(spinEffect, 0, 50, 0)
                spinEffect.wrtReparentTo(self.battle)
                spinTrack = self.getPartTrack(
                    spinEffect, 1.1, 2.9, [spinEffect, self.battle, 0]
                )
                spinEffectTracks.append(spinTrack)
            toonSpinTrack = Sequence(
                Wait(0.1),
                LerpHprInterval(toon, 0.7, Point3(-10, 0, 0)),
                LerpHprInterval(toon, 0.5, Point3(-30, 0, 0)),
                LerpHprInterval(toon, 0.2, Point3(-60, 0, 0)),
                LerpHprInterval(toon, 0.7, Point3(-700, 0, 0)),
                LerpHprInterval(toon, 1.0, Point3(-1310, 0, 0)),
                LerpHprInterval(toon, 0.4, toon.getHpr()),
                Wait(0.5),
            )
            soundTrack = self.getSoundTrack(
                "SA_head_shrink_only.ogg", delay=1.2
            )
            def applyVisualEffect(toon=toon):
                movieApplySeq = MovieUtil.applyVisualEffect(
                    toon, VisualEffectEnum.BEWITCHMENT, useMovieApply=True
                )
                if movieApplySeq is not None:
                    movieApplySeq[0].start()
            effectApplyTrack = Func(applyVisualEffect, toon)
            toonTracks.append(Sequence(
                Wait(1.5),
                ActorInterval(toon, "duck", endTime=0.75),
                Parallel(
                    ActorInterval(toon, "cringe", playRate=0.4),
                    toonSpinTrack,
                    soundTrack,
                    *spinEffectTracks,
                    Sequence(
                        Wait(2.5),
                        Parallel(
                            effectApplyTrack,
                            Func(toon.showHpString, "BEWITCHED!", 0.85, 0.7, (1, 1, 1, 1))
                        )
                    )
                )
            ))
        return Parallel(suitTrack, toonTracks)
    
    def getCameraShot(self, duration):
        return self.camera.allGroupOverheadShot(duration=duration)


@AttackClass(attackType=AttackEnum.CHAINSAW_ENTER_DORMANT)
class EnterDormantAttack(Attack):
    """Simply a visual representation of the Chainsaw Consultant going
    into his second phase.
    """

    def doAttack(self):
        chainsaw = self.targetObjs[0]

        cutsceneLoader = CutsceneLoader.createLoader(
            key=CutsceneKeyEnum.ChainsawConsultant_PhaseTwo,
            chainsaw=chainsaw,
            battle=self.battle,
        )

        suitTrack = Parallel(
            Sequence(
                Wait(4.753),
                Func(base.musicMgr.crossfadeIntoMusic, 'chainsaw_battle_2', duration=6.0, matchTime=False),
            ),
            cutsceneLoader.buildCutscene(),
        )

        return suitTrack
    
    def getCameraShot(self, duration):
        return Wait(duration)
    

@AttackClass(attackType=AttackEnum.CHAINSAW_EXIT_DORMANT)
class ExitDormantAttack(Attack):
    """Simply a visual representation of the Chainsaw Consultant going
    into his third phase.
    """

    def doAttack(self):
        chainsaw = self.targetObjs[0]
        cutsceneLoader = CutsceneLoader.createLoader(
            key=CutsceneKeyEnum.ChainsawConsultant_PhaseThree,
            chainsaw=chainsaw,
            battle=self.battle,
        )

        suitTrack = Parallel(
            Sequence(
                Wait(7.6),
                Func(chainsaw.specialHead.enterGlitch),
                Func(messenger.send, ChainsawMeterGUI.getPhaseThreeEvent()),
                Func(base.musicMgr.crossfadeIntoMusic, 'chainsaw_battle_3', duration=0.5, matchTime=False),
            ),
            cutsceneLoader.buildCutscene()
        )

        return suitTrack
    
    def getCameraShot(self, duration):
        return Wait(duration)


@AttackClass(attackType=AttackEnum.SCABBARD)
class Scabbard(SuitSingleAttack):
    CHEAT = True

    def doAttack(self):
        cutscene = CutsceneLoader.createLoader(
            CutsceneKeyEnum.ChainsawConsultant_Scabbard,
            toons=self.toons,
            chainsaw=self.invoker,
            suits=self.suits,
            battle=self.battle,
            taunt=self.getAttackTaunt(),
        ).buildCutscene()

        BattleParticles.loadParticles()
        healTracks = Parallel()
        particleTracks = Parallel()
        for suit in self.targetObjs:
            result = self.findTarget(suit.doId)
            healHP = result.hpAdjust
            seq = Parallel(
                Func(self.updateSuitHP, suit, healHP, nonZero=True),
                Func(suit.setChatAbsolute,
                    random.choice(TTLocalizer.MovieSuitHealResponses),
                    CFSpeech | CFTimeout,
                )
            )
            healTracks.append(seq)
            particleEffect = BattleParticles.loadParticleFile('chainsawScabbardDown.ptf')
            particleNode = suit.attachNewNode('scabbard-particleNode')
            particleNode.setZ(suit.height + 1.0)
            particleTrack = self.getPartTrack(particleEffect, 0.0, 3.0,
                                              [particleEffect, particleNode, 0], softStop=-2.0)
            particleTracks.append(Sequence(particleTrack, Func(particleNode.removeNode)))

        sfx = loader.loadSfx("phase_11/audio/sfx/LB_toonup.ogg")

        return Parallel(
            cutscene,
            Sequence(
                Wait(2.0), 
                Parallel(
                    IsolatedSoundInterval(sfx),
                    healTracks,
                    particleTracks,
                    Wait(1.5)
                )
            ),
        )
    
    def getCameraShot(self, duration):
        # Handled by Cutscene Loader
        return Wait(duration)


@AttackClass(attackType=AttackEnum.CHAIN_LINKED)
class ChainLinked(SuitSingleAttack):
    CHEAT = True

    def doAttack(self):
        cutscene = CutsceneLoader.createLoader(
            CutsceneKeyEnum.ChainsawConsultant_ChainLinked,
            toons=self.toons,
            suits=[suit for suit in self.suits if suit is not self.invoker],
            chainsaw=self.invoker,
            battle=self.battle,
            taunt=self.getAttackTaunt(),
        ).buildCutscene()
        return Parallel(cutscene)
    
    def getCameraShot(self, duration):
        return Sequence(Wait(duration))


@AttackClass(attackType=AttackEnum.KICKBACK)
class Kickback(SuitSingleAttack):
    ANIM_NAME = "pie-small-react"
    CHEAT = True

    def doAttack(self):
        return Parallel(self.getSuitAnimTrack(wantDialog=False), Wait(5.75))
    
    def getCameraShot(self, duration):
        return self.camera.allGroupOverheadShot(duration=duration)


@AttackClass(attackType=AttackEnum.AGGRANDIZE)
class Aggrandize(SuitSingleAttack):
    ANIM_NAME = "snap-override"
    CHEAT = True

    def doAttack(self):
        if not self.targetObjs:
            return Sequence()

        target = self.targetObjs[0] # type: DistributedSuitBase

        def loopNeutralAnim():
            loopAnim = "lured" if target.isLured else "neutral"
            target.loop(loopAnim)

        def updateDNA():
            target.setElite(1)
            target.setLevel(self.extraArgs[0])
            target.setMaxHp(int(target.getHp() * 1.5))
            target.healthBar.updateMeterMode(SuitHealthMeter.MODE_BATTLE)
            target.healthBar.updateHealthBar(forceUpdate=1)

            target.setDisplayName(target.createNameInfo())
        
        def getDustCloudIval():
            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(1.0)
            dustCloud.createTrack()
            return Sequence(Func(dustCloud.reparentTo, target), dustCloud.track, Func(dustCloud.destroy),
                            name='dustCloudIval')

        targetTrack = Sequence(
            Func(updateDNA),
            Parallel(
                getDustCloudIval(),
                Func(target.showHpString, "PROMOTED!", 0.85, 0.7, (1, 1, 1, 1)),
                ActorInterval(target, 'slip-forward', startTime=2.43),
            ),
            Func(loopNeutralAnim),
        )
        
        suitTrack = self.getSuitAnimTrack()
        sfx = self.getSoundTrack(
            "phase_11/audio/sfx/SA_bash.ogg", delay=0.1, node=self.invoker
        )

        return Parallel(suitTrack, sfx, Sequence(Wait(1), targetTrack))

    def getCameraShot(self, duration):
        return self.camera.allGroupOverheadShot(duration=duration)


@AttackClass(attackType=AttackEnum.DEADWOOD)
class Deadwood(SuitSingleAttack):
    ANIM_NAME = "snap-override"
    CHEAT = True

    pbpWordwrapMult = 10.0

    def doAttack(self):
        cutsceneLoader = CutsceneLoader.createLoader(
            key=CutsceneKeyEnum.ChainsawConsultant_Deadwood,
            toons=self.toons,
            suits=[suit for suit in self.suits if suit is not self.invoker],
            chainsaw=self.invoker,
            battle=self.battle,
            taunt=self.getAttackTaunt(),
            doors=base.instance.doorList,
        )

        base.localAvatar.deadwood = True

        return Sequence(
            Parallel(
                cutsceneLoader.buildCutscene(),
                Func(base.musicMgr.fadeOutMusic, 2.3),
            ),
            Func(base.transitions.irisOut),
            Wait(1),
            Func(self.sendLocalToonAway, 6837, exitState='TeleportOut'),
        )
    
    def getCameraShot(self, duration):
        # Handled by Cutscene Loader
        return Wait(duration)


@AttackClass(attackType=AttackEnum.THROTTLE)
class Throttle(SuitSingleAttack):
    CHEAT = True
    CUTSCENE_ENUMS = (CutsceneKeyEnum.ChainsawConsultant_Throttle, CutsceneKeyEnum.ChainsawConsultant_ThrottleTwo)

    def doAttack(self):
        cutscene = CutsceneLoader.createLoader(
            self.CUTSCENE_ENUMS[self.extraArgs[0]],
            toons=self.toons,
            suits=[suit for suit in self.suits if suit is not self.invoker],
            chainsaw=self.invoker,
            battle=self.battle,
            taunt=self.getAttackTaunt(),
        ).buildCutscene()

        toonTracks = Parallel()
        for target in self.targetDicts:
            toonTracks.append(Sequence(
                Wait(4.5),
                Func(self.doDamage, target["avatar"], target["hp"], target["died"]),
            ))

        if self.extraArgs[0] == 0:
            toonTracks.append(Sequence(
                Wait(4.0),
                Func(messenger.send, ChainsawMeterGUI.getPhaseTwoEvent()),
            ))
    
        return Parallel(cutscene, toonTracks)

    def getCameraShot(self, duration):
        # Handled by Cutscene Loader
        return Wait(duration)

    def chooseCameraShot(self, duration):
        """
        Returns the camera shot and the text that should display for
        the suit attack.
        """
        if duration < 0:
            duration = 1e-06

        camTrack = Sequence()
        camTrack.append(self.getCameraShot(duration))

        # Reason we are making this a method is because we want this executed as the movie is happening, not before
        def getTextColor():
            return (0.45, 0.45, 1.0, 1.0)

        def getTextPos():
            return (0.0, 0.775)

        fakeTextDuration = [3.76, 3.16][self.extraArgs[0]]

        pbpTrack = self.playByPlayText.getShowInterval(
            TTLocalizer.SuitAttackNames[AttackEnum.DEADWOOD],
            fakeTextDuration,
            colorOverride=getTextColor,
            posOverride=getTextPos,
            pbpDelay=self.pbpDelay,
            pbpSubtextDelay=self.pbpSubtextDelay,
            wantFadeOut=False,
            wordwrapMult=10.0,
        )
        realPbpTrack = self.playByPlayText.getShowInterval(
            self.getAttackDisplayName(),
            duration - fakeTextDuration,
            colorOverride=getTextColor,
            posOverride=getTextPos,
            pbpDelay=self.pbpDelay,
            pbpSubtextDelay=self.pbpSubtextDelay,
            wantFadeIn=False,
        )

        return Parallel(camTrack, Sequence(pbpTrack, realPbpTrack))


@AttackClass(attackType=AttackEnum.SPARK_PLUG)
class SparkPlug(SuitSingleAttack):
    CHEAT = True

    def doAttack(self):
        cutscene = CutsceneLoader.createLoader(
            CutsceneKeyEnum.ChainsawConsultant_SparkPlug,
            toons=self.targetObjs,
            suits=[suit for suit in self.suits if suit is not self.invoker],
            chainsaw=self.invoker,
            battle=self.battle,
            taunt=self.getAttackTaunt(),
        ).buildCutscene()

        def getChainsawFingerPos():
            handNode = self.invoker.leftHand.attachNewNode('foo')
            handNode.setPos(-1.5631, 0.3, 0.0)
            handPos = handNode.getPos(render)
            handNode.removeNode()
            return handPos
        
        def getToonTargetPoint(toon):
            pnt = toon.getPos(render)
            pnt.setZ(pnt[2] + toon.getHeight() * 0.5)
            return Point3(pnt)

        targetPoint = lambda toon = self.targetObjs[0]: getToonTargetPoint(toon)

        dSprayScale = 0.05

        toon = self.targetObjs[0]
        targetPos = toon.getPos(self.battle)
        origPos, origHpr = self.battle.getActorPosHpr(self.invoker)

        return Sequence(
            Func(self.invoker.specialHead.exitGlitch),
            Func(self.invoker.headsUp, self.battle, targetPos),
            Parallel(
                Parallel(
                    cutscene,
                    Sequence(
                        Wait(5.36),
                        Func(self.invoker.specialHead.enterSemiGlitch),
                    ),
                ),
                Sequence(
                    Wait(3.812),
                    Parallel(
                        MovieUtil.getZapTrack(
                            self.battle,
                            Point4(1.0, 1.0, 0, 1.0),
                            getChainsawFingerPos,
                            targetPoint,
                            dSprayScale, 0.2, dSprayScale,
                        ),
                        Func(MovieUtil.applyVisualEffect, self.targetObjs[0], VisualEffectEnum.SPARK_PLUG_DAMAGE),
                        Func(toon.showHpString,  text='SPARK PLUG!', color=(0.85, 0.78, 1.0, 1.0))
                    )
                )
            ),
            Func(self.invoker.setHpr, self.battle, origHpr),
        )

    def getCameraShot(self, duration):
        return Sequence(Wait(duration))


@AttackClass(attackType=AttackEnum.SPENDING_REV)
class SpendingRev(Attack):

    def getChainsawTexRollDur(self, stacks: int) -> float:
        return max(1.6 - (0.075 * stacks), 0.1)

    def doAttack(self):
        chainsaw = self.targetObjs[0]
        rpm = int(self.extraArgs[0]) * 1000
        duration = self.getChainsawTexRollDur(self.extraArgs[1] - self.extraArgs[0])

        return Parallel(
            LerpFunc(
                chainsaw.specialHead.setChainsawTexRoll, 
                2, 
                self.getChainsawTexRollDur(self.extraArgs[1]),
                duration,
                blendType='easeInOut'
            ),
            Sequence(
                Func(chainsaw.clearChat),
                Func(chainsaw.showHpString, f"-{rpm:,} RPM", 0.85, 0.7, (1, 1, 1, 1)),
                Wait(2.0)
            ),
            Func(
                messenger.send, ChainsawMeterGUI.getRPMDeltaEvent(), [int(self.extraArgs[0]) * -1]
            ),
        )
    
    def getCameraShot(self, duration):
        return self.camera.heldRelativeShot(self.targetObjs[0], 0, 12, 15, 180, -30, 0, duration, 'singleAvatarShot')


@AttackClass(attackType=AttackEnum.PYROMANIAC)
class Pyromaniac(ShowHpTextAttack):
    ANIM_NAME = 'summon'
    CHEAT = True

    def doAttack(self):
        hpTextTrack = super().doAttack()
        suitTrack = self.getSuitAnimTrack(wantDialog=False)
        soundTrack = self.getSoundTrack(
            "SA_trial_by_fire_a.ogg", delay=0.2, node=self.invoker
        )

        BattleParticles.loadParticles()
        flameEffect = BattleParticles.createParticleEffect(file="firestarterPyromaniac")
        flameTrack = self.getPartTrack(
            flameEffect, 0.2, 4.5, [flameEffect, self.invoker, 0], softStop=-1.5
        )

        return Parallel(Func(self.invoker.clearChat), hpTextTrack, suitTrack, flameTrack, soundTrack, Wait(5.75))

    def getAttackDisplayName(self) -> str:
        """There are two possible outcomes for Pyromaniac,
        thus in order to provide the correct description, index the
        description tuple with the second value in our extraArgs.
        """
        nameInfo = super().getAttackDisplayName()

        # This shouldn't ever happen, but just in-case.
        if len(self.extraArgs) < 2:
            return nameInfo[0]

        # Return the correct name/desc pair.
        return (nameInfo[0], nameInfo[1][int(self.extraArgs[1])])

    def getCameraShot(self, duration):
        return self.camera.heldRelativeHeadsUpShot(self.invoker, -8, 10, 6.5, self.invoker, duration, name='pyromaniacHeldRelativeHeadsUpShot')


@AttackClass(attackType=AttackEnum.SPARK_PLUG_DAMAGE)
class SparkPlugDamage(AllowGroupingAttack):
    def doAttack(self):
        target = self.targetDicts[0]
        toon = target["avatar"]
        sfx = loader.loadSfx("phase_5/audio/sfx/AA_battery.ogg")
        toonTrack = Sequence(
            Sequence(ActorInterval(toon, 'slip-backward')),
            self.getToonTrack(damageAnimNames=['neutral'], lookAtInvoker=False)
        )
        BattleParticles.loadParticles()
        particleEffect = BattleParticles.createParticleEffect(file='chainsawSparkPlugDamage')
        particleEffect.setScale(toon.scale)
        particleEffect.setColorScaleOff(1)
        particleEffect.setDepthWrite(False)
        # particleEffect.getParticlesNamed('particles-1').emitter.setOffsetForce(
        #     Vec3(0.0000, 0.0000, 7.0000 + toon.height))
        particleNode = toon.attachNewNode('SparkPlugDamage-particleNode')
        particleNode.setZ(toon.height * 0.4)
        particleTrack = ParticleInterval(particleEffect, particleNode, worldRelative=False, duration=3, softStopT=-1.0, cleanup=True)

        return Sequence(Parallel(toonTrack, particleTrack, SoundInterval(sfx)), Func(particleNode.removeNode))

    def getCameraShot(self, duration):
        return self.camera.heldShot(0.0, 3.25, 5.0, 180, -5, 0, duration=duration, name='toonSparkDOTHeldShot')


@AttackClass(attackType=AttackEnum.PACESETTER_CHALLENGE)
class PacesetterChallengeAttack(AvatarSayPhraseAttack):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.phraseIndex = self.extraArgs[1]

    @property
    def phraseData(self):
        # We need to take in phrase data from Pacesetter's base status effect, so we can match up phrases between the two
        phraseData = TTLocalizer.GeneralAttackSayPhrases[self.sayPhraseType]
        if self.phraseIndex > len(phraseData[0]):
            phraseData[0] = [phraseData[0][self.phraseIndex]]
        return phraseData

    @property
    def bml(self):
        return self.battle.battleMusicListener

    def doAttack(self):
        self.bml.updateStoredMusic()
        fadeOutSeq = Sequence(LerpFunctionInterval(
            self.bml.setVolume, duration=2, blendType='easeIn',
            fromData=self.bml.currentVolume, toData=0.0
        ), Wait(2), Func(self.bml.stopMusic))
        return Sequence(Parallel(fadeOutSeq, super().doAttack()))


@AttackClass(attackType=AttackEnum.PACESETTER_CHALLENGE_CANCELLED)
class PacesetterChallengeCancelAttack(DoNothing):
    @property
    def bml(self):
        return self.battle.battleMusicListener

    def getAttackMovie(self):
        return Sequence(Func(self.bml.playMusic, 0, 0, self.bml.currentPlayback, 'pacesetter_battle', 1.0)), Sequence()
