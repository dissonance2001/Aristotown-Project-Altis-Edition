"""Module containing every basic suit attack movie object."""

import random

from panda3d.core import Point3, Point4, TextNode, VBase3, Vec3, Vec4, VBase4, NodePath
from direct.interval.IntervalGlobal import *

from toontown.battle import BattleParticles, MovieUtil
from toontown.battle.BattleProps import globalPropPool
from toontown.battle.BattleSounds import globalBattleSoundCache
from toontown.battle.attacks.base.AttackEnum import AttackEnum
from toontown.battle.attacks.client.AttackRepository import AttackClass
from toontown.battle.attacks.client.suit.SuitGroupAttack import SuitGroupAttack
from toontown.battle.attacks.client.suit.SuitSingleAttack import SuitSingleAttack
from toontown.battle.attacks.client.Attack import AttackAnimKeys as AAK
from toontown.suit.SuitDNA import getSuitBodyType
from toontown.toonbase import TTLocalizer, ToontownGlobals


@AttackClass(attackType=AttackEnum.AUDIT)
class Audit(SuitSingleAttack):
    ANIM_NAME = "calculator"
    OPEN_SHOT_DUR = 2.0
    PLAY_RATE = 1.3
    Particle1 = "audit-one"
    Particle2 = "audit-two"
    Particle3 = "audit-three"
    Particle4 = 'audit-four'
    Particle5 = 'audit-mult'
    SoundPath = 'SA_audit.ogg'

    def doAttack(self):
        calculator = globalPropPool.getProp("calculator")
        BattleParticles.loadParticles()
        particleEffect = BattleParticles.createParticleEffect("Calculate")
        BattleParticles.setEffectTexture(
            particleEffect, self.Particle1, color=Vec4(0, 0, 0, 1)
        )
        particleEffect2 = BattleParticles.createParticleEffect("Calculate")
        BattleParticles.setEffectTexture(
            particleEffect2, self.Particle2, color=Vec4(0, 0, 0, 1)
        )
        particleEffect3 = BattleParticles.createParticleEffect("Calculate")
        BattleParticles.setEffectTexture(
            particleEffect3, self.Particle3, color=Vec4(0, 0, 0, 1)
        )
        particleEffect4 = BattleParticles.createParticleEffect("Calculate")
        BattleParticles.setEffectTexture(
            particleEffect4, self.Particle4, color=Vec4(0, 0, 0, 1)
        )
        particleEffect5 = BattleParticles.createParticleEffect("Calculate")
        BattleParticles.setEffectTexture(
            particleEffect5, self.Particle5, color=Vec4(0, 0, 0, 1)
        )
        suitTrack = self.getSuitTrack(playRate=self.PLAY_RATE)
        particleNode = self.invoker.attachNewNode('audit-particle-node')
        particleNode.setBin('fixed', 1)
        partTrack = self.getPartTrack(
            particleEffect, 1.4/self.PLAY_RATE, 1.9/self.PLAY_RATE, [particleEffect, particleNode, 0]
        )
        partTrack2 = self.getPartTrack(
            particleEffect2, 1.5/self.PLAY_RATE, 2.0/self.PLAY_RATE, [particleEffect2, particleNode, 0]
        )
        partTrack3 = self.getPartTrack(
            particleEffect3, 1.6/self.PLAY_RATE, 2.1/self.PLAY_RATE, [particleEffect3, particleNode, 0]
        )
        partTrack4 = self.getPartTrack(
            particleEffect4, 1.7/self.PLAY_RATE, 2.2/self.PLAY_RATE, [particleEffect4, particleNode, 0]
        )
        partTrack5 = self.getPartTrack(
            particleEffect5, 1.8/self.PLAY_RATE, 2.3/self.PLAY_RATE, [particleEffect5, particleNode, 0]
        )

        bodyType = getSuitBodyType(self.invoker.style.name)

        if bodyType == "a":
            calcPosPoints = [Point3(-0.7219, 0.37, -0.1062), VBase3(-3.55, 0, 180)]
            scaleUpPoint = Point3(1.5, 1.5, 1.5)
        else:
            calcPosPoints = [Point3(-0.0774, 0.4245, -0.0517), VBase3(-3.55, 0, 180)]
            scaleUpPoint = Point3(1.1, 1.1, 1.5)

        calcPropTrack = Sequence(
            Func(self.showProp, calculator, self.invoker.getLeftHand(), *calcPosPoints),
            Func(calculator.setScale, scaleUpPoint),
            ActorInterval(calculator, 'calculator', playRate=self.PLAY_RATE),
            Func(MovieUtil.removeProp, calculator),
        )

        damageAnims = [["cringe", 0.01]]
        toonTrack = self.getToonTrack(
            damageDelay=2.9/self.PLAY_RATE,
            splicedDamageAnims=damageAnims,
            dodgeDelay=0.6/self.PLAY_RATE,
            dodgeAnimNames=["duck"],
            showMissedExtraTime=2.2/self.PLAY_RATE,
        )
        soundTrack = self.getSoundTrack("SA_audit.ogg", delay=1.3/self.PLAY_RATE, node=self.invoker, playRate=1.05)
        return Parallel(
            suitTrack,
            toonTrack,
            calcPropTrack,
            soundTrack,
            Sequence(
                Parallel(
                    partTrack,
                    partTrack2,
                    partTrack3,
                    partTrack4,
                    partTrack5,
                ),
                Func(particleNode.removeNode),
            ),
        )


@AttackClass(attackType=AttackEnum.BITE)
class Bite(SuitSingleAttack):
    ANIM_NAME = "throw-object"
    OPEN_SHOT_DUR = 2.8/1.5
    PLAY_RATE = 1.5

    def doAttack(self):
        target = self.targetDicts[0]
        toon = target["avatar"]
        dmg = target["hp"]
        teeth = globalPropPool.getProp("teeth")
        propDelay = 0.8 / self.PLAY_RATE
        propScaleUpTime = 0.1 / self.PLAY_RATE
        suitDelay = 2.05 / self.PLAY_RATE
        throwDelay = propDelay + propScaleUpTime + suitDelay
        throwDuration = 0.4 / self.PLAY_RATE
        suitTrack = self.getSuitTrack(playRate=self.PLAY_RATE)
        posPoints = [Point3(-0.3, 0.1, 0), VBase3(4.465, -3.563, 180)]
        teethAppearTrack = Sequence(
            self.getPropAppearTrack(
                teeth,
                self.invoker.getRightHand(),
                posPoints,
                propDelay,
                Point3(3, 3, 3),
                scaleUpTime=propScaleUpTime,
            )
        )
        teethAppearTrack.append(Wait(suitDelay))
        teethAppearTrack.append(Func(self.movie.needRestoreRenderProp, teeth))
        teethAppearTrack.append(Func(teeth.wrtReparentTo, self.battle))
        if target["landed"]:
            x = toon.getX(self.battle)
            y = toon.getY(self.battle)
            z = toon.getZ(self.battle)
            toonHeight = z + toon.getHeight()
            flyPoint = Point3(x, y + 2.7, toonHeight * 0.8)
            teethAppearTrack.append(LerpPosInterval(teeth, throwDuration, pos=flyPoint))
            teethAppearTrack.append(
                LerpPosInterval(teeth, 0.4, pos=Point3(x, y + 3.2, toonHeight * 0.7))
            )
            teethAppearTrack.append(
                LerpPosInterval(teeth, 0.3, pos=Point3(x, y + 4.7, toonHeight * 0.5))
            )
            teethAppearTrack.append(Wait(0.2))
            teethAppearTrack.append(
                LerpPosInterval(teeth, 0.1, pos=Point3(x, y - 0.2, toonHeight * 0.9))
            )
            teethAppearTrack.append(Wait(0.4))
            scaleTrack = Sequence(
                Wait(throwDelay),
                LerpScaleInterval(teeth, throwDuration, Point3(8, 8, 8)),
                Wait(0.9),
                LerpScaleInterval(teeth, 0.2, Point3(14, 14, 14)),
                Wait(1.2),
                LerpScaleInterval(teeth, 0.3, MovieUtil.PNT3_NEARZERO),
            )
            hprTrack = Sequence(
                Wait(throwDelay),
                LerpHprInterval(teeth, 0.3, Point3(180, 0, 0)),
                Wait(0.2),
                LerpHprInterval(
                    teeth, 0.4, Point3(180, -35, 0), startHpr=Point3(180, 0, 0)
                ),
                Wait(0.4),
                LerpHprInterval(
                    teeth, 0.1, Point3(180, -75, 0), startHpr=Point3(180, -35, 0)
                ),
            )
            animTrack = Sequence(
                Wait(throwDelay),
                ActorInterval(teeth, "teeth", duration=throwDuration),
                ActorInterval(teeth, "teeth", duration=0.3),
                Func(teeth.pose, "teeth", 1),
                Wait(0.7),
                ActorInterval(teeth, "teeth", duration=0.9),
            )
            propTrack = Sequence(
                Parallel(teethAppearTrack, scaleTrack, hprTrack, animTrack),
                Func(MovieUtil.removeProp, teeth),
                Func(self.movie.clearRenderProp, teeth),
            )
        else:
            flyPoint = self.toonFacePoint(toon, parent=self.battle)
            flyPoint.setY(flyPoint.getY() - 7.1)
            teethAppearTrack.append(LerpPosInterval(teeth, throwDuration, pos=flyPoint))
            teethAppearTrack.append(Func(MovieUtil.removeProp, teeth))
            teethAppearTrack.append(Func(self.movie.clearRenderProp, teeth))
            propTrack = teethAppearTrack
        damageAnims = [
            ["cringe", 0.01, 0.7, 1.2],
            ["conked", 0.01, 0.2, 2.1],
            ["conked", 0.01, 3.2],
        ]
        dodgeAnims = [["cringe", 0.01, 0.7, 0.2], ["duck", 0.01, 1.6]]
        toonTrack = self.getToonTrack(
            damageDelay=2.1,
            splicedDamageAnims=damageAnims,
            dodgeDelay=1.8,
            splicedDodgeAnims=dodgeAnims,
            showDamageExtraTime=2.4,
            damageAnimPlayRate=1.15,
            dodgeAnimPlayRate=1.15,
        )
        if target["landed"]:
            soundTrack = self.getSoundTrack(
                "SA_bite.ogg", delay=throwDelay, node=self.invoker, playRate=1.05)
        else:
            soundTrack = Sequence()
        return Parallel(suitTrack, toonTrack, soundTrack, propTrack)


@AttackClass(attackType=AttackEnum.BLUE_CHIP)
class BlueChip(SuitSingleAttack):
    ANIM_NAME = "blue-chip"
    OPEN_SHOT_DUR = 2.45

    def doAttack(self):
        target = self.targetDicts[0]
        toon = target["avatar"]

        chip = globalPropPool.getProp("blue_chip")
        firstHoldPosPoints = [Point3(-0.0012, 0.5083, -0.1271), Point3(-100, 0, 0)]
        grabPosPoints = [Point3(-0.2336, -0.0272, -0.0817), Point3(76.7974, -95.719, 0)]

        damageDelay = 3.1
        dodgeDelay = 2.2

        suitTrack = self.getSuitTrack()

        landPos = toon.getPos(render)
        landPos.setZ(landPos.getZ() + 0.25)
        landUpPos = toon.getPos(render)
        landUpPos.setZ(landUpPos.getZ() + 0.8)

        invokerScale = self.invoker.getScale()

        bodyType = getSuitBodyType(self.invoker.dna.name)
        if bodyType == "a":
            scaleFactor = 1.19636963  # Head honcho scale
            startX, startY = 2.9, 4.2
            endX, endY = 0.7, 5.1
            startZ = 7.4
            endZ = 8.8
            chipHandScale = 1.15
            chipGrabScale = 1.15
            chipFlipMult = 6.5
        else:
            scaleFactor = 0.82041587901  # Insider scale
            startX, startY = 0.9, 2.1
            endX, endY = 0.9, 2.45
            startZ = 3.0
            endZ = 4.4
            chipHandScale = 0.95
            chipGrabScale = 0.8
            chipFlipMult = 5.0

        propTrack = Sequence(
            self.getPropAppearTrack(
                chip,
                self.invoker.getRightHand(),
                firstHoldPosPoints,
                0.2,
                Point3(chipHandScale),
                scaleUpTime=0.25,
            ),
        )

        chipHandPosRenderStart = Point3(startX * (invokerScale[0] / scaleFactor),
                                        startY * (invokerScale[0] / scaleFactor),
                                        startZ * (invokerScale[0] / scaleFactor))
        chipHandPosRenderEnd = Point3(endX * (invokerScale[0] / scaleFactor),
                                      endY * (invokerScale[0] / scaleFactor),
                                      endZ * (invokerScale[0] / scaleFactor))

        propFlyTrack = Sequence(
            Wait(1.05),
            Func(chip.wrtReparentTo, self.invoker),
            Parallel(
                ProjectileInterval(chip, startPos=chipHandPosRenderStart, endPos=chipHandPosRenderEnd, duration=0.5, gravityMult=chipFlipMult),
                LerpHprInterval(chip, 0.5, (90, -360, 0), startHpr=(0, 90, 0)),
            ),
            Func(chip.wrtReparentTo, self.invoker.getRightHand()),
            Func(chip.setPosHpr, *grabPosPoints[0], *grabPosPoints[1]),
            Func(chip.setScale, chipGrabScale),
            Wait(0.7),
            Func(chip.wrtReparentTo, render),
            Parallel(
                ProjectileInterval(chip, endPos=landPos, duration=0.95, gravityMult=2.15),
                LerpHprInterval(chip, 0.95, (0, 450, 0), startHpr=(0, 90, 0)),
                Sequence(
                    Wait(0.25),
                    LerpScaleInterval(chip, 0.65, 6.5),
                ),
            ),
            Parallel(
                LerpHprInterval(chip, 0.15, (20, 441, 0)),
                LerpPosInterval(chip, 0.15, landUpPos, blendType='easeOut'),
            ),
            Parallel(
                LerpHprInterval(chip, 0.225, (40, 450, 0)),
                LerpPosInterval(chip, 0.225, landPos, blendType='easeIn'),
            ),
            LerpHprInterval(chip, 0.3, (60, 450, 0)),
            LerpHprInterval(chip, 0.3, (70, 450, 0), blendType='easeOut'),
            Wait(0.1),
            LerpScaleInterval(chip, 0.35, 0.01, blendType='easeIn'),
            Func(chip.hide),
        )
        if target["landed"]:
            toonReactTrack = Sequence(
                Wait(damageDelay),
                Func(toon.setAnimState, "Squish"),
                Func(toon.playDialogueForString, "!"),
                Wait(2.5),
            )
        else:
            toonReactTrack = Sequence()

        toonTrack = self.getToonTrack(
            damageDelay=damageDelay,
            damageAnimNames=[],
            dodgeDelay=dodgeDelay,
            dodgeAnimNames=["sidestep"],
            dodgeAnimPlayRate=1.2,
        )
        soundTrack = self.getSoundTrack(
            "SA_blue_chip.ogg", delay=0, node=self.invoker
        )
        return Sequence(
            Parallel(
                suitTrack, toonTrack, toonReactTrack, soundTrack, propTrack, propFlyTrack,
            ),
            Func(MovieUtil.removeProp, chip),
        )


@AttackClass(attackType=AttackEnum.BOUNCE_CHECK)
class BounceCheck(SuitSingleAttack):
    ANIM_NAME = "throw-object"
    FORCE_SPLIT_CAMERA = True

    def doAttack(self):
        self.ONE = Vec3(-5.0, 0.0, 0.8)
        self.TWO = Vec3(2.75, -2.0, 0.8)

        target = self.targetDicts[0]
        toon = target["avatar"]
        hitSuit = target['landed']
        check = globalPropPool.getProp("bounced-check")
        checkPosPoints = [MovieUtil.PNT3_ZERO, VBase3(90, 90, 180)]
        bounce1Point = lambda: self.getThrowEndPoint(toon, "one")
        bounce2Point = lambda: self.getThrowEndPoint(toon, "two")
        hitPoint = lambda: self.getThrowEndPoint(toon, "hit")
        missPoint = lambda: self.getThrowEndPoint(toon, "miss")
        throwDelay = 48/24 / 2
        dodgeDelay = 1.7 + throwDelay
        damageDelay = 2.0 + throwDelay
        suitTrack = self.getSuitTrack(playRate=2)
        checkPropTrack = Sequence(
            self.getPropAppearTrack(
                check,
                self.invoker.getRightHand(),
                checkPosPoints,
                1e-05,
                Point3(8.5, 8.5, 8.5),
                startScale=MovieUtil.PNT3_ONE,
            )
        )
        checkPropTrack.append(Wait(throwDelay))
        checkPropTrack.append(Func(check.wrtReparentTo, self.battle))
        releaseDur = checkPropTrack.getDuration()
        grav = -130
        checkPropTrack.append(
            self.getThrowTrack(check, bounce1Point, duration=0.5, parent=self.battle, gravity=grav)
        )
        checkPropTrack.append(
            self.getThrowTrack(check, bounce2Point, duration=0.6, parent=self.battle, gravity=grav)
        )
        if hitSuit:
            checkPropTrack.append(
                self.getThrowTrack(check, hitPoint, duration=0.5, parent=self.battle, gravity=grav)
            )
        else:
            checkPropTrack.append(
                self.getThrowTrack(check, missPoint, duration=0.5, parent=self.battle, gravity=grav)
            )
            checkPropTrack.append(
                LerpScaleInterval(check, 0.1, MovieUtil.PNT3_NEARZERO, blendType='easeIn')
            )
        endDur = checkPropTrack.getDuration() - releaseDur - 0.01
        checkPropTrack.append(Sequence(
            Func(check.setScale, MovieUtil.PNT3_NEARZERO),
            Wait(1.0),
            Func(MovieUtil.removeProp, check)
        ))
        spinCheckTrack = Sequence(
            Wait(releaseDur),
            LerpHprInterval(check, endDur, startHpr=(0, 90, 0), hpr=(1200, 90, 0)),
        )
        toonTrack = Parallel(
            self.getToonTrack(damageDelay, [], dodgeDelay, []),
            Sequence(
                Wait(damageDelay),
                ActorInterval(toon, 'slip-backward', playRate=1.3),
                Func(toon.loop, 'neutral'),
            ) if hitSuit else Sequence(Wait(dodgeDelay), Func(toon.doEmote, 24), Wait(1.5)),
        )

        soundName = "SA_pink_slip.ogg"  # "AA_drop_anvil_miss.ogg"  # "SA_pink_slip.ogg"
        soundTracks = Parallel(
            self.getSoundTrack(soundName, delay=throwDelay + 0.2, duration=0.7,
                               node=self.invoker, playRate=1.05),
            self.getSoundTrack(soundName, delay=throwDelay+0.8, duration=0.7, node=self.invoker, playRate=1.05, volume=0.8),
            self.getSoundTrack(soundName, delay=throwDelay+1.4, duration=0.7, node=self.invoker, playRate=1.05, volume=0.8),
        )
        hitSeq = Sequence()
        if hitSuit:
            hitSeq = self.getSoundTrack("Toon_bodyfall_synergy.ogg", delay=throwDelay + 1.9,
                                        duration=0.6, node=self.invoker, playRate=1.0)

        BattleParticles.loadParticles()
        trailEffect = BattleParticles.createParticleEffect(file='bouncecheck')
        partTrack = self.getPartTrack(trailEffect, releaseDur, endDur+1.0, [trailEffect, check, 1], softStop=-1.0)

        return Parallel(suitTrack, checkPropTrack, toonTrack, soundTracks, spinCheckTrack, partTrack, hitSeq)

    def getThrowEndPoint(self, toon, whichBounce):
        pnt = toon.getPos(self.battle)
        if whichBounce == "one":
            pnt = self.ONE  # Vec3(2, 2, 0.8)
        elif whichBounce == "two":
            pnt = self.TWO  # Vec3(-6, -4.5, 0.8)
        elif whichBounce == "hit":
            pnt.setZ(pnt[2] + toon.shoulderHeight + 0.3)
        elif whichBounce == "miss":
            pnt = Vec3(0, -8, 13)
        return Point3(pnt)


@AttackClass(attackType=AttackEnum.BRAIN_STORM)
class BrainStorm(SuitSingleAttack):
    ANIM_NAME = "effort"
    OPEN_SHOT_DUR = 2.0

    def doAttack(self):
        target = self.targetDicts[0]
        toon = target["avatar"]
        BattleParticles.loadParticles()
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
        partDelay = 0.45
        damageDelay = 3.0
        dodgeDelay = 2.0
        suitTrack = self.getSuitTrack(delay=0.9, playRate=1.3)
        initialCloudHeight = self.invoker.height + 3
        cloudPosPoints = [Point3(0, 3, initialCloudHeight), VBase3(180, 0, 0)]
        cloudPropTrack = Sequence()
        cloudPropTrack.append(Func(cloud.pose, "stormcloud", 0))
        cloudPropTrack.append(
            self.getPropAppearTrack(
                cloud,
                self.invoker,
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
        cloudPropTrack.append(Wait(0.8))
        cloudPropTrack.append(LerpPosInterval(cloud, 0.7, pos=targetPoint, blendType='easeInOut'))
        cloudPropTrack.append(Wait(partDelay))
        cloudPropTrack.append(
            Parallel(
                ParticleInterval(
                    snowEffect, cloud, worldRelative=0, duration=2.0, cleanup=True, softStopT=-0.7,
                ),
                Sequence(
                    Wait(0.35),
                    ParticleInterval(
                        snowEffect2, cloud, worldRelative=0, duration=1.65, cleanup=True, softStopT=-0.7,
                    ),
                ),
                Sequence(
                    Wait(0.7),
                    ParticleInterval(
                        snowEffect3, cloud, worldRelative=0, duration=1.30, cleanup=True, softStopT=-0.7,
                    ),
                ),
                Sequence(
                    ActorInterval(cloud, "stormcloud", startTime=3, duration=0.33),
                    ActorInterval(cloud, "stormcloud", startTime=2.5, duration=0.33),
                    ActorInterval(cloud, "stormcloud", startTime=1, duration=1.33),
                ),
            )
        )
        cloudPropTrack.append(Wait(0.2))
        cloudPropTrack.append(LerpScaleInterval(cloud, 0.2, MovieUtil.PNT3_NEARZERO, blendType='easeIn'))
        cloudPropTrack.append(Func(MovieUtil.removeProp, cloud))
        cloudPropTrack.append(Func(self.battle.movie.clearRenderProp, cloud))
        damageAnims = [["cringe", 0.01, 0.4, 0.8], ["duck", 1e-06, 2.0]]
        toonTrack = self.getToonTrack(
            damageDelay=damageDelay,
            splicedDamageAnims=damageAnims,
            dodgeDelay=dodgeDelay,
            dodgeAnimNames=["sidestep"],
            showMissedExtraTime=1.1,
        )
        soundTrack = self.getSoundTrack(
            "SA_brainstorm.ogg", delay=1.6, node=self.invoker
        )
        return Parallel(suitTrack, toonTrack, cloudPropTrack, soundTrack)


@AttackClass(attackType=AttackEnum.BUZZ_WORD)
class BuzzWord(SuitSingleAttack):
    ANIM_NAME = "speak"
    OPEN_SHOT_DUR = 3.1
    PLAY_RATE = 1.3

    def doAttack(self):
        BattleParticles.loadParticles()
        particleEffects = []
        texturesList = [
            "buzzwords-crash",
            "buzzwords-inc",
            "buzzwords-main",
            "buzzwords-over",
            "buzzwords-syn",
        ]
        for texture in texturesList:
            effect = BattleParticles.createParticleEffect("BuzzWord")
            if random.random() < 0.5:
                BattleParticles.setEffectTexture(
                    effect, texture, color=Vec4(1, 0.94, 0.02, 1)
                )
            else:
                BattleParticles.setEffectTexture(
                    effect, texture, color=Vec4(0, 0, 0, 1)
                )
            particleEffects.append(effect)

        partDelay = 3.6
        partDuration = 3.3
        damageDelay = 4.5
        dodgeDelay = 3.8
        if self.invoker.dna.name == "mi":
            for effect in particleEffects:
                effect.setPos(0, 2.8, self.invoker.getHeight() - 2.5)
                effect.setHpr(0, -20, 0)
        elif self.invoker.dna.name == "sh":
            for effect in particleEffects:
                effect.setPos(0, 2.8, self.invoker.getHeight() - 2.5)
                effect.setHpr(0, -20, 0)
        elif self.invoker.dna.name == "dt":
            for effect in particleEffects:
                effect.setPos(0, 2.8, self.invoker.getHeight() - 1.6)
                effect.setHpr(0, -10, 0)
        elif self.invoker.dna.name == "mm":
            for effect in particleEffects:
                effect.setPos(0, 0.8, self.invoker.getHeight() - 0.25)
        elif self.invoker.dna.name == "prethink":
            for effect in particleEffects:
                effect.setPos(0, 2.1, self.invoker.getHeight() - 1.8)
        elif self.invoker.dna.name == "nn":
            for effect in particleEffects:
                effect.setPos(0, 2.5, self.invoker.getHeight() - 1.1)
        elif self.invoker.dna.name == "stenog":
            for effect in particleEffects:
                effect.setPos(0, 2.8, self.invoker.getHeight() - 2.5)
                effect.setHpr(0, -25, 0)

        suitTrack = self.getSuitTrack(playRate=self.PLAY_RATE)
        particleTracks = []
        for effect in particleEffects:
            particleTracks.append(
                self.getPartTrack(
                    effect, partDelay/self.PLAY_RATE, partDuration/self.PLAY_RATE, [effect, self.invoker, 0], softStop=-0.75
                )
            )

        toonTrack = self.getToonTrack(
            damageDelay=damageDelay/self.PLAY_RATE,
            damageAnimNames=["cringe"],
            splicedDodgeAnims=[["duck", dodgeDelay/self.PLAY_RATE, 1.4]],
            showMissedExtraTime=(dodgeDelay + 0.5)/self.PLAY_RATE,
        )
        soundTrack = self.getSoundTrack(
            "SA_buzz_word.ogg", delay=3.9/self.PLAY_RATE, node=self.invoker
        )
        return Parallel(suitTrack, toonTrack, soundTrack, *particleTracks)


@AttackClass(attackType=AttackEnum.CALCULATE)
class Calculate(Audit):
    Particle1 = "audit-one"
    Particle2 = "audit-plus"
    Particle3 = "audit-mult"
    Particle4 = 'audit-three'
    Particle5 = 'audit-div'
    SoundPath = 'SA_calculate.ogg'


@AttackClass(attackType=AttackEnum.CANNED)
class Canned(SuitSingleAttack):
    ANIM_NAME = "throw-object"
    OPEN_SHOT_DUR = 2.9 / 1.3
    PLAY_RATE = 1.35

    def doAttack(self):
        target = self.targetDicts[0]
        toon = target["avatar"]
        hips = toon.getHipsParts()
        propDelay = 0.8/self.PLAY_RATE
        suitDelay = 1.83/self.PLAY_RATE
        dodgeDelay = 2.1/self.PLAY_RATE
        throwDuration = 1.5/self.PLAY_RATE
        can = globalPropPool.getProp("can")
        dust = globalPropPool.getProp("dust")
        dust.setBillboardPointWorld(2)
        scale = 18
        torso = toon.style.torso
        torso = torso[0]
        if torso == "s":
            scaleUpPoint = Point3(scale * 2.63, scale * 2.63, scale * 1.9975)
        elif torso == "m":
            scaleUpPoint = Point3(scale * 2.63, scale * 2.63, scale * 1.7975)
        elif torso == "l":
            scaleUpPoint = Point3(scale * 2.63, scale * 2.63, scale * 2.31)
        canHpr = VBase3(-173.47, -0.42, 162.09)
        suitTrack = self.getSuitTrack(playRate=self.PLAY_RATE)
        posPoints = [Point3(-0.10, -0.1, 0.02), VBase3(-10.584, 11.945, -161.684)]
        throwTrack = Sequence(
            self.getPropAppearTrack(
                can,
                self.invoker.getRightHand(),
                posPoints,
                propDelay,
                Point3(6, 6, 6),
                scaleUpTime=0.5/self.PLAY_RATE,
            )
        )
        propDelay = propDelay + (0.5/self.PLAY_RATE)
        throwTrack.append(Wait(suitDelay))
        hitPoint = toon.getPos(self.battle)
        hitPoint.setX(hitPoint.getX() + 1.1)
        hitPoint.setY(hitPoint.getY() + (-0.5 if target["landed"] else -1.4))
        hitPoint.setZ(hitPoint.getZ() + toon.height + 1.1)
        throwTrack.append(Func(self.battle.movie.needRestoreRenderProp, can))
        throwTrack.append(
            self.getThrowTrack(
                can, hitPoint, duration=throwDuration, parent=self.battle
            )
        )
        if target["landed"]:
            throwTrack.append(Func(self.battle.movie.needRestoreHips))
            throwTrack.append(Func(can.wrtReparentTo, hips[0]))
            throwTrack.append(Wait(2.4/self.PLAY_RATE))
            throwTrack.append(Func(self.battle.movie.clearRestoreHips))
            scaleTrack = Sequence(
                Wait(propDelay + suitDelay),
                LerpScaleInterval(can, throwDuration, scaleUpPoint),
            )
            hprTrack = Sequence(
                Wait(propDelay + suitDelay), LerpHprInterval(can, throwDuration, canHpr)
            )
            soundTrack = Parallel(
                Sequence(
                    Wait(2.6 / self.PLAY_RATE),
                    SoundInterval(
                        globalBattleSoundCache.getSound("SA_canned_tossup_only.ogg"),
                        node=self.invoker,
                    ),
                ),
                Sequence(
                    Wait(4.45 / self.PLAY_RATE),
                    SoundInterval(
                        globalBattleSoundCache.getSound("SA_canned_impact_only.ogg"),
                        node=self.invoker,
                    ),
                ),
            )
            dustTrack = Sequence(
                Wait(4.45/self.PLAY_RATE),
                Func(dust.reparentTo, toon),
                ActorInterval(dust, "dust"),
                Func(dust.cleanup),
            )
        else:
            land = toon.getPos(self.battle)
            land = Point3(land.getX() + 1.1, land.getY() - 2.9, land.getZ() + 0.7)
            bouncePoint1 = Point3(land.getX(), land.getY() - 1.0, land.getZ() + 2.5)
            bouncePoint2 = Point3(land.getX(), land.getY() - 1.7, land.getZ() - 0.2)
            bouncePoint3 = Point3(land.getX(), land.getY() - 2.5, land.getZ() + 1.5)
            bouncePoint4 = Point3(land.getX(), land.getY() - 3.1, land.getZ() + 0.3)
            throwTrack.append(LerpPosInterval(can, 0.4, land))
            throwTrack.append(LerpPosInterval(can, 0.4, bouncePoint1))
            throwTrack.append(LerpPosInterval(can, 0.3, bouncePoint2))
            throwTrack.append(LerpPosInterval(can, 0.3, bouncePoint3))
            throwTrack.append(LerpPosInterval(can, 0.3, bouncePoint4))
            throwTrack.append(Wait(0.7/self.PLAY_RATE))
            throwTrack.append(LerpScaleInterval(can, 0.25, MovieUtil.PNT3_NEARZERO))
            scaleTrack = Sequence(
                Wait(propDelay + suitDelay),
                LerpScaleInterval(can, throwDuration, Point3(11, 11, 11)),
            )
            hprTrack = Sequence(
                Wait(propDelay + suitDelay),
                LerpHprInterval(can, throwDuration, canHpr),
                Wait(0.4/self.PLAY_RATE),
                LerpHprInterval(can, 0.4, Point3(83.27, 19.52, -177.92)),
                LerpHprInterval(can, 0.3, Point3(95.24, -72.09, 88.65)),
                LerpHprInterval(can, 0.2, Point3(-96.34, -2.63, 179.89)),
            )
            soundTrack = self.getSoundTrack(
                "SA_canned_tossup_only.ogg", delay=2.6/self.PLAY_RATE, node=self.invoker
            )
            dustTrack = Sequence()
        canTrack = Sequence(
            Parallel(throwTrack, scaleTrack, hprTrack),
            Func(MovieUtil.removeProp, can),
            Func(self.battle.movie.clearRenderProp, can),
        )
        damageAnims = [
            ["slip-backward", 0.01, 0.45],
        ]
        toonTrack = self.getToonTrack(
            damageDelay=propDelay+suitDelay+throwDuration,
            splicedDamageAnims=damageAnims,
            dodgeDelay=dodgeDelay,
            dodgeAnimNames=["duck"],
            showDamageExtraTime=0.3,
            showMissedExtraTime=1.1,
        )
        return Parallel(suitTrack, toonTrack, canTrack, soundTrack, dustTrack)


@AttackClass(attackType=AttackEnum.CHOMP)
class Chomp(SuitSingleAttack):
    ANIM_NAME = "throw-object"
    OPEN_SHOT_DUR = 2.8/1.5
    PLAY_RATE = 1.5

    def doAttack(self):
        target = self.targetDicts[0]
        toon = target["avatar"]
        teeth = globalPropPool.getProp("teeth")
        propDelay = 0.8 / self.PLAY_RATE
        propScaleUpTime = 0.1 / self.PLAY_RATE
        suitDelay = 2.05 / self.PLAY_RATE
        throwDelay = propDelay + propScaleUpTime + suitDelay
        throwDuration = 0.4 / self.PLAY_RATE
        suitTrack = self.getSuitTrack(playRate=self.PLAY_RATE)
        posPoints = [Point3(-0.3, 0.1, 0), VBase3(4.465, -3.563, 180)]
        teethAppearTrack = Sequence(
            self.getPropAppearTrack(
                teeth,
                self.invoker.getRightHand(),
                posPoints,
                propDelay,
                Point3(3, 3, 3),
                scaleUpTime=propScaleUpTime,
            )
        )
        teethAppearTrack.append(Wait(suitDelay))
        teethAppearTrack.append(Func(self.movie.needRestoreRenderProp, teeth))
        teethAppearTrack.append(Func(teeth.wrtReparentTo, self.battle))
        if target["landed"]:
            x = toon.getX(self.battle)
            y = toon.getY(self.battle)
            z = toon.getZ(self.battle)
            toonHeight = z + toon.getHeight()
            flyPoint = Point3(x, y + 2.7, toonHeight * 0.7)
            teethAppearTrack.append(LerpPosInterval(teeth, throwDuration, pos=flyPoint))
            teethAppearTrack.append(
                LerpPosInterval(teeth, 0.4, pos=Point3(x, y + 3.2, toonHeight * 0.7))
            )
            teethAppearTrack.append(
                LerpPosInterval(teeth, 0.3, pos=Point3(x, y + 4.7, toonHeight * 0.5))
            )
            teethAppearTrack.append(Wait(0.2))
            teethAppearTrack.append(
                LerpPosInterval(teeth, 0.1, pos=Point3(x, y, toonHeight + 3))
            )
            teethAppearTrack.append(
                LerpPosInterval(teeth, 0.1, pos=Point3(x, y - 1.2, toonHeight * 0.7))
            )
            teethAppearTrack.append(
                LerpPosInterval(teeth, 0.1, pos=Point3(x, y + 0.3, toonHeight * 0.4))
            )
            teethAppearTrack.append(Wait(0.4))
            scaleTrack = Sequence(
                Wait(throwDelay),
                LerpScaleInterval(teeth, throwDuration, Point3(6, 6, 6)),
                Wait(0.9),
                LerpScaleInterval(teeth, 0.2, Point3(10, 10, 10)),
                Wait(1.2),
                LerpScaleInterval(teeth, 0.3, MovieUtil.PNT3_NEARZERO),
            )
            hprTrack = Sequence(
                Wait(throwDelay),
                LerpHprInterval(teeth, 0.3, Point3(180, 0, 0)),
                Wait(0.2),
                LerpHprInterval(
                    teeth, 0.4, Point3(180, -35, 0), startHpr=Point3(180, 0, 0)
                ),
                Wait(0.2),
                LerpHprInterval(
                    teeth, 0.1, Point3(0, -35, 0), startHpr=Point3(180, -35, 0)
                ),
            )
            animTrack = Sequence(
                Wait(throwDelay),
                ActorInterval(teeth, "teeth", duration=throwDuration),
                ActorInterval(teeth, "teeth", duration=0.3),
                Func(teeth.pose, "teeth", 1),
                Wait(0.7),
                ActorInterval(teeth, "teeth", duration=0.9),
            )
            propTrack = Sequence(
                Parallel(teethAppearTrack, scaleTrack, hprTrack, animTrack),
                Func(MovieUtil.removeProp, teeth),
                Func(self.movie.clearRenderProp, teeth),
            )
        else:
            x = toon.getX(self.battle)
            y = toon.getY(self.battle)
            z = toon.getZ(self.battle)
            z = z + 0.2
            flyPoint = Point3(x, y - 2.1, z)
            teethAppearTrack.append(LerpPosInterval(teeth, throwDuration, pos=flyPoint))
            teethAppearTrack.append(Wait(0.2))
            teethAppearTrack.append(
                LerpPosInterval(teeth, 0.2, pos=Point3(x + 0.5, y - 2.5, z))
            )
            teethAppearTrack.append(
                LerpPosInterval(teeth, 0.2, pos=Point3(x + 1.0, y - 3.0, z + 0.4))
            )
            teethAppearTrack.append(
                LerpPosInterval(teeth, 0.2, pos=Point3(x + 1.3, y - 3.6, z))
            )
            teethAppearTrack.append(
                LerpPosInterval(teeth, 0.2, pos=Point3(x + 0.9, y - 3.1, z + 0.4))
            )
            teethAppearTrack.append(
                LerpPosInterval(teeth, 0.2, pos=Point3(x + 0.3, y - 2.6, z))
            )
            teethAppearTrack.append(
                LerpPosInterval(teeth, 0.2, pos=Point3(x - 0.1, y - 2.2, z + 0.4))
            )
            teethAppearTrack.append(
                LerpPosInterval(teeth, 0.2, pos=Point3(x - 0.4, y - 1.9, z))
            )
            teethAppearTrack.append(
                LerpPosInterval(teeth, 0.2, pos=Point3(x - 0.7, y - 2.1, z + 0.4))
            )
            teethAppearTrack.append(
                LerpPosInterval(teeth, 0.2, pos=Point3(x - 0.8, y - 2.3, z))
            )
            teethAppearTrack.append(
                LerpScaleInterval(teeth, 0.35, MovieUtil.PNT3_NEARZERO)
            )
            hprTrack = Sequence(
                Wait(throwDelay),
                LerpHprInterval(teeth, 0.3, Point3(180, 0, 0)),
                Wait(0.2),
                LerpHprInterval(
                    teeth, 0.3, Point3(80, 0, 0), startHpr=Point3(180, 0, 0)
                ),
                LerpHprInterval(
                    teeth, 0.6, Point3(-10, 0, 0), startHpr=Point3(80, 0, 0)
                ),
            )
            animTrack = Sequence(
                Wait(throwDelay), ActorInterval(teeth, "teeth", duration=3.6)
            )
            propTrack = Sequence(
                Parallel(teethAppearTrack, hprTrack, animTrack),
                Func(MovieUtil.removeProp, teeth),
                Func(self.battle.movie.clearRenderProp, teeth),
            )
        damageAnims = [
            ["cringe", 0.01, 0.7, 1.2],
            ["spit", 0.01, 2.95, 1.47],
            ["spit", 0.01, 4.42, 0.07],
            ["spit", 0.08, 4.49, -0.07],
            ["spit", 0.01, 4.42],
        ]
        dodgeAnims = [["jump", 0.01, 0.01]]
        toonTrack = self.getToonTrack(
            damageDelay=2.1,
            splicedDamageAnims=damageAnims,
            dodgeDelay=1.7,
            splicedDodgeAnims=dodgeAnims,
            showDamageExtraTime=1.4,
        )
        if target["landed"]:
            soundTrack = self.getSoundTrack("SA_bite.ogg", delay=throwDelay, node=self.invoker)
        else:
            soundTrack = Sequence()
        return Parallel(suitTrack, toonTrack, soundTrack, propTrack)


@AttackClass(attackType=AttackEnum.CIGAR_SMOKE)
class CigarSmoke(SuitSingleAttack):
    ANIM_NAME = "cigar-smoke"
    PLAY_RATE = 1.15
    OPEN_SHOT_DUR = (78/24)/PLAY_RATE
    WantCigarProp = True
    SmokeNodePos = (0, 0, 0)
    CigarPosPoints = [Point3(-0.05, -0.9, -0.35), VBase3(180.0, 0.0, 0.0)]
    CigarScale = Point3(9.0)
    CigarAppearTime = 0.3/PLAY_RATE
    CigarRemainTime = (115/24)/PLAY_RATE
    CigarScaleUpTime = 0.4/PLAY_RATE
    CigarScaleDownTime = 0.4/PLAY_RATE

    def getSmokeNodePos(self):
        defaultSmokeNodePos = {
            'a': (0, 2, -1.2),
            'c': (0, 0, -2.5),
        }.get(self.invoker.style.body, (0, 0, 0))
        if self.SmokeNodePos != (0, 0, 0):
            return self.SmokeNodePos
        return defaultSmokeNodePos

    def getDamageDelay(self):
        return {
            'a': 3.6/self.PLAY_RATE,
            'c': 2.7/self.PLAY_RATE,
        }.get(self.invoker.style.body, 3.6/self.PLAY_RATE)

    def getCigarSuitTrack(self):
        if len(self.targetObjs) == 1:
            return self.getSuitTrack(playRate=self.PLAY_RATE)
        else:
            return self.getSuitAnimTrack(playRate=self.PLAY_RATE)

    def doAttack(self):
        BattleParticles.loadParticles()
        suitTrack = self.getCigarSuitTrack()
        damageDelay = self.getDamageDelay()

        if self.WantCigarProp:
            cigar = globalPropPool.getProp("cigar")
            cigarPropTrack = self.getPropTrack(
                cigar,
                self.invoker.getRightHand(),
                self.CigarPosPoints,
                self.CigarAppearTime,
                self.CigarRemainTime,
                scaleUpTime=self.CigarScaleUpTime,
                scaleDownTime=self.CigarScaleDownTime,
                scaleUpPoint=self.CigarScale,
            )
        else:
            cigarPropTrack = Sequence(
                Wait(self.CigarAppearTime + self.CigarRemainTime + self.CigarScaleUpTime + self.CigarScaleDownTime))

        def changeColor(parts):
            track = Parallel()
            for nextPart in parts:
                track.append(Func(nextPart.setColorScale, Vec4(0, 0, 0, 1)))

            return track

        def resetColor(parts):
            track = Parallel()
            for nextPart in parts:
                track.append(Func(nextPart.clearColorScale))

            return track

        globalParallel = Parallel(suitTrack, cigarPropTrack)

        for target in self.targetDicts:
            toon = target["avatar"]
            smoke = BattleParticles.createParticleEffect("Smoke")
            BattleParticles.setEffectTexture(smoke, "snow-particle")

            toonTrack = self.getToonTrack(damageDelay - (0.05/self.PLAY_RATE),
                                          ["cringe"],
                                          damageDelay - (1.35/self.PLAY_RATE),
                                          ["duck"],
                                          showMissedExtraTime=0.4,
                                          target=target)
            smokeNode = self.invoker.attachNewNode('smoke-node')
            smokeNode.setBin('fixed', 1)
            smokeNode.setPos(self.getSmokeNodePos())
            smokeTrack = self.getPartTrack(smoke, damageDelay - (0.15/self.PLAY_RATE), 1.5/self.PLAY_RATE, [smoke, smokeNode, 0])
            smokeTrack = Sequence(
                Func(smokeNode.headsUp, toon),
                smokeTrack
            )
            multiTrackList = Parallel(toonTrack, smokeTrack)

            if target["landed"]:
                headParts = toon.getHeadParts()
                torsoParts = toon.getTorsoParts()
                legsParts = toon.getLegsParts()
                colorTrack = Sequence()
                colorTrack.append(Wait(damageDelay))
                colorTrack.append(Func(self.battle.movie.needRestoreColor))
                colorTrack.append(changeColor(headParts))
                colorTrack.append(changeColor(torsoParts))
                colorTrack.append(changeColor(legsParts))
                colorTrack.append(Wait(2.2/self.PLAY_RATE))
                colorTrack.append(resetColor(headParts))
                colorTrack.append(resetColor(torsoParts))
                colorTrack.append(resetColor(legsParts))
                colorTrack.append(Func(self.battle.movie.clearRestoreColor))
                multiTrackList.append(colorTrack)
            multiTrackList = Sequence(multiTrackList, Func(smokeNode.removeNode))

            globalParallel.append(multiTrackList)

        return globalParallel

    def getCameraShot(self, duration):
        if len(self.targetObjs) > 1:
            return self.camera.randomGroupAttackCam(
                self.invoker, self.targetDicts, self.battle, duration, self.OPEN_SHOT_DUR)
        else:
            return SuitSingleAttack.getCameraShot(self, duration)


@AttackClass(attackType=AttackEnum.CIGAR_SMOKE_HEAD_HONCHO)
class CigarSmokeHeadHoncho(CigarSmoke):
    ANIM_NAME = 'headhoncho-cigar-smoke'
    WantCigarProp = True
    PLAY_RATE = 1.15
    OPEN_SHOT_DUR = (50 / 24) / PLAY_RATE
    SmokeNodePos = (0, 1, 0.8)
    CigarPosPoints = [Point3(-0.1, -0.7, -0.15), VBase3(180.0, 0.0, 0.0)]
    CigarScale = Point3(9.0)
    CigarAppearTime = (42 / 24) / PLAY_RATE
    CigarRemainTime = (69 / 24) / PLAY_RATE
    CigarScaleUpTime = 0.01/PLAY_RATE
    CigarScaleDownTime = 0.01/PLAY_RATE

    def doAttack(self):
        if self.invoker.isSkeleton:
            self.ANIM_NAME = CigarSmoke.ANIM_NAME
            self.PLAY_RATE = CigarSmoke.PLAY_RATE
            self.OPEN_SHOT_DUR = CigarSmoke.OPEN_SHOT_DUR
            self.WantCigarProp = CigarSmoke.WantCigarProp
            self.SmokeNodePos = CigarSmoke.SmokeNodePos
            self.CigarPosPoints = CigarSmoke.CigarPosPoints
            self.CigarScale = CigarSmoke.CigarScale
            self.CigarAppearTime = CigarSmoke.CigarAppearTime
            self.CigarRemainTime = CigarSmoke.CigarRemainTime
            self.CigarScaleUpTime = CigarSmoke.CigarScaleUpTime
            self.CigarScaleDownTime = CigarSmoke.CigarScaleDownTime

        return super().doAttack()

    def getCigarSuitTrack(self):
        if self.invoker.isSkeleton:
            return super().getCigarSuitTrack()

        return Parallel(
            self.getSuitTrack(wantSpeechHeadAnim=False, playRate=self.PLAY_RATE),
            Sequence(
                self.invoker.specialHead.actorInterval('cigar-smoke', playRate=self.PLAY_RATE),
                Func(self.invoker.specialHead.loopNeutral),
            )
        )

    def getDamageDelay(self):
        if self.invoker.isSkeleton:
            return super().getDamageDelay()
        return (60 / 24) / self.PLAY_RATE


@AttackClass(attackType=AttackEnum.CLIPON_TIE)
class ClipOnTie(SuitSingleAttack):
    ANIM_NAME = "throw-object"
    FORCE_SPLIT_CAMERA = True

    def doAttack(self):
        throwDelay = 1.0
        damageDelay = throwDelay + 1.23
        dodgeDelay = damageDelay - 0.20
        suitTrack = self.getSuitTrack(playRate=1.5)
        hitTarget = False
        tiePropTracks = Parallel()
        for i, target in enumerate(self.targetDicts):
            toon = target["avatar"]
            tie = globalPropPool.getProp(self.getPropName())
            tiePropTrack = Sequence(
                self.getPropAppearTrack(
                    tie,
                    self.invoker.getRightHand(),
                    self.getPosPoints(),
                    0.25,
                    self.getPropScale(),
                    scaleUpTime=0.25,
                    poseExtraArgs=[self.getPropActorName(), 0] if self.getPropActorName() else None,
                    blendType='easeIn',
                )
            )
            if target["landed"]:
                tiePropTrack.append(
                    ActorInterval(tie, self.getPropActorName(), duration=throwDelay, startTime=1.1)
                    if self.getPropActorName() else Wait(throwDelay)
                )
            else:
                tiePropTrack.append(Wait(throwDelay))
            tiePropTrack.append(Wait(0.50))
            tiePropTrack.append(Func(self.movie.needRestoreRenderProp, tie))
            tiePropTrack.append(Func(tie.wrtReparentTo, render))
            tiePropTrack.append(Func(tie.setHpr, Point3(0, -90, 0)))
            if target['landed']:
                tiePropTrack.append(Parallel(
                    ProjectileInterval(
                        tie, endPos=self.toonFacePoint(toon), duration=0.3, gravityMult=-5.0,
                    ),
                    LerpHprInterval(tie, 0.3, (110, 160, 0)),
                ))
            else:
                startH, endH = self.missH()
                yoffset = random.randint(0, 20) / 10.0
                xoffset = random.randint(-7, 7) / 10.0
                tiePropTrack.append(Parallel(
                    ProjectileInterval(
                        tie, endPos=self.toonGroundPoint(toon, 0.1) + Vec3(0, 4 + yoffset, 0), duration=0.5, gravityMult=4.0,
                    ),
                    LerpHprInterval(tie, 0.5, (startH, 270, 0)),
                ))
                tiePropTrack.append(Parallel(
                    ProjectileInterval(
                        tie, endPos=self.toonGroundPoint(toon, 0.1) + Vec3(xoffset, 3.5 + yoffset, 0), duration=0.15, gravityMult=1.0,
                    ),
                    LerpHprInterval(tie, 0.30, (endH + random.randint(-30, 30), 270, 45), blendType='easeOut'),
                    Wait(0.60),
                ))
                tiePropTrack.append(LerpScaleInterval(tie, duration=0.30, scale=MovieUtil.PNT3_NEARZERO, blendType='easeIn',))
            tiePropTrack.append(Func(MovieUtil.removeProp, tie))
            tiePropTrack.append(Func(self.movie.clearRenderProp, tie))
            tiePropTracks.append(tiePropTrack)
            hitTarget = hitTarget or target['landed']

        toonTrack = self.getToonTracks(damageDelay, ["slip-backward"], dodgeDelay, [], damageAnimPlayRate=1.15, dodgeAnimPlayRate=1.15)
        throwSound = self.getSoundTrack(
            self.getSfxName(), delay=throwDelay + 0.8, node=self.invoker, playRate=1.2,
        )
        hitSound = Sequence()
        if self.getHitSound() and hitTarget:
            hitSound = self.getSoundTrack(
                self.getHitSound(), delay=throwDelay + 1.05, node=self.invoker
            )
        return Parallel(suitTrack, toonTrack, tiePropTracks, throwSound, hitSound)

    def getPropName(self):
        return "clip-on-tie"

    def getPropActorName(self):
        return "clip-on-tie"

    def getPosPoints(self):
        return [Point3(0.66, 0.51, -0.45), VBase3(-69.652, -57.199, 67.96)]

    def getPropScale(self):
        return MovieUtil.PNT3_ONE

    def getSfxName(self):
        return "SA_powertie_throw.ogg"

    def getHitSound(self):
        return None

    def missH(self):
        return 180, 280


@AttackClass(attackType=AttackEnum.CRUNCH)
class Crunch(SuitSingleAttack):
    ANIM_NAME = "throw-object"
    FORCE_SPLIT_CAMERA = True
    PLAY_RATE = 1.4

    def doAttack(self):
        throwDuration = 2.75/self.PLAY_RATE
        suitTrack = self.getSuitTrack(playRate=self.PLAY_RATE)
        numberNames = ["one", "two", "three", "four", "five", "six"]
        BattleParticles.loadParticles()
        numberSpill1 = BattleParticles.createParticleEffect(file="numberSpill")
        numberSpill2 = BattleParticles.createParticleEffect(file="numberSpill")
        spillTexture1 = random.choice(numberNames)
        spillTexture2 = random.choice(numberNames)
        BattleParticles.setEffectTexture(numberSpill1, "audit-" + spillTexture1)
        BattleParticles.setEffectTexture(numberSpill2, "audit-" + spillTexture2)
        numberSpillTrack1 = self.getPartTrack(
            numberSpill1, 1.1/self.PLAY_RATE, 2.2/self.PLAY_RATE, [numberSpill1, self.invoker, 0]
        )
        numberSpillTrack2 = self.getPartTrack(
            numberSpill2, 1.5/self.PLAY_RATE, 1.0/self.PLAY_RATE, [numberSpill2, self.invoker, 0]
        )
        numberSprayTracks = Parallel()
        numOfNumbers = random.randint(11, 16)
        particleNode = self.invoker.attachNewNode('particle-node')
        for i in range(0, numOfNumbers - 1):
            nextSpray = BattleParticles.createParticleEffect(file="numberSpray")
            nextTexture = random.choice(numberNames)
            BattleParticles.setEffectTexture(nextSpray, "audit-" + nextTexture)
            nextStartTime = random.random() * 0.2 + throwDuration
            nextDuration = random.random() * 0.3 + 1.2
            nextSprayTrack = self.getPartTrack(
                nextSpray, nextStartTime, nextDuration, [nextSpray, particleNode, 0]
            )
            numberSprayTracks.append(nextSprayTrack)
        numberSprayTracks = Parallel(
            Sequence(
                Wait(numberSprayTracks.getDuration() - 0.21),
                LerpColorScaleInterval(particleNode, 0.21, (1, 1, 1, 0), blendType='easeIn'),
            ),
            Sequence(
                numberSprayTracks,
                Func(particleNode.removeNode)
            )
        )

        numberTracks = Parallel()
        for i in range(0, numOfNumbers):
            texture = random.choice(numberNames)
            next = MovieUtil.copyProp(BattleParticles.getParticle("audit-" + texture))
            next.reparentTo(self.invoker.getRightHand())
            next.setScale(0.01, 0.01, 0.01)
            next.setColor(Vec4(0.0, 0.0, 0.0, 1.0))
            next.setPos(
                random.random() * 0.6 - 0.3,
                random.random() * 0.6 - 0.3,
                random.random() * 0.6 - 0.3,
            )
            next.setHpr(VBase3(-1.15, 86.58, -76.78))
            numberTrack = Sequence(
                Wait(0.9/self.PLAY_RATE),
                LerpScaleInterval(next, 0.6, MovieUtil.PNT3_ONE),
                Wait(1.7/self.PLAY_RATE),
                Func(MovieUtil.removeProp, next),
            )
            numberTracks.append(numberTrack)

        damageAnims = []
        damageAnims.append(["cringe", 0.01, 0.14, 0.28])
        damageAnims.append(["cringe", 0.01, 0.16, 0.3])
        damageAnims.append(["cringe", 0.01, 0.13, 0.22])
        damageAnims.append(["slip-forward", 0.01, 0.6])
        toonTrack = self.getToonTrack(
            damageDelay=4.7/self.PLAY_RATE,
            splicedDamageAnims=damageAnims,
            dodgeDelay=2.4/self.PLAY_RATE,
            dodgeAnimNames=["duck"],
            damageAnimPlayRate=1.2,
            dodgeAnimPlayRate=1.2,
        )
        return Parallel(
            suitTrack,
            toonTrack,
            numberSpillTrack1,
            numberSpillTrack2,
            numberTracks,
            numberSprayTracks,
        )


@AttackClass(attackType=AttackEnum.DEMOTION)
class Demotion(SuitSingleAttack):
    ANIM_NAME = "magic1"
    OPEN_SHOT_DUR = 1.7

    def doAttack(self):
        target = self.targetDicts[0]
        toon = target["avatar"]
        BattleParticles.loadParticles()
        sprayEffect = BattleParticles.createParticleEffect("DemotionSpray")
        freezeEffect = BattleParticles.createParticleEffect("DemotionFreeze")
        unFreezeEffect = BattleParticles.createParticleEffect(file="demotionUnFreeze")
        BattleParticles.setEffectTexture(sprayEffect, "snow-particle")
        BattleParticles.setEffectTexture(freezeEffect, "snow-particle")
        BattleParticles.setEffectTexture(unFreezeEffect, "snow-particle")
        facePoint = self.toonFacePoint(toon, parent=toon)
        freezeEffect.setPos(0, 0, facePoint.getZ() - 0.6)
        unFreezeEffect.setPos(0, 0, facePoint.getZ() - 0.6)
        suitTrack = self.getSuitTrack()
        sprayNode = self.battle.attachNewNode('spray-node')
        sprayNode.setPos(self.battle.getActorPosHpr(self.invoker)[0])
        sprayNode.setZ(self.invoker.getHeight() * 0.66)
        sprayNode.lookAt(toon)
        sprayNode.setP(sprayNode.getP() + 15)
        partTrack = Sequence(
            self.getPartTrack(sprayEffect, 0.7, 2.1, [sprayEffect, sprayNode, 0], softStop=-1.0),
            Func(sprayNode.removeNode),
        )
        partTrack2 = self.getPartTrack(freezeEffect, 1.4, 3.6, [freezeEffect, toon, 0])
        partTrack3 = self.getPartTrack(
            unFreezeEffect, 4.65, 0.5, [unFreezeEffect, toon, 0]
        )
        dodgeAnims = [["duck", 1e-06, 0.8]]
        damageAnims = []
        damageAnims.append(["cringe", 0.01, 0, 0.5])
        damageAnims.extend(self.getSplicedLerpAnims("cringe", 0.4, 0.5, startTime=0.5))
        damageAnims.extend(self.getSplicedLerpAnims("cringe", 0.3, 0.5, startTime=0.9))
        damageAnims.extend(self.getSplicedLerpAnims("cringe", 0.3, 0.6, startTime=1.2))
        damageAnims.append(["cringe", 0.6, 1.5])
        toonTrack = self.getToonTrack(
            damageDelay=1.0,
            splicedDamageAnims=damageAnims,
            splicedDodgeAnims=dodgeAnims,
            showMissedExtraTime=1.6,
            showDamageExtraTime=1.3,
        )
        soundTrack = self.getSoundTrack("SA_demotion.ogg", delay=1.2, node=self.invoker)
        if target["landed"]:
            return Parallel(
                suitTrack, toonTrack, soundTrack, partTrack, partTrack2, partTrack3
            )
        else:
            return Parallel(suitTrack, toonTrack, soundTrack, partTrack)


@AttackClass(attackType=AttackEnum.DOUBLE_TALK)
class DoubleTalk(SuitSingleAttack):
    ANIM_NAME = "speak"
    PLAY_RATE = 1.3
    OPEN_SHOT_DUR = 3.9/PLAY_RATE

    def doAttack(self):
        BattleParticles.loadParticles()
        particleEffect = BattleParticles.createParticleEffect("DoubleTalkLeft")
        particleEffect2 = BattleParticles.createParticleEffect("DoubleTalkRight")
        BattleParticles.setEffectTexture(
            particleEffect, "doubletalk-double", color=Vec4(0, 1.0, 0.0, 1)
        )
        BattleParticles.setEffectTexture(
            particleEffect2, "doubletalk-good", color=Vec4(0, 1.0, 0.0, 1)
        )
        partDelay = 3.5/self.PLAY_RATE
        damageDelay = 3.7/self.PLAY_RATE
        dodgeDelay = 3.3/self.PLAY_RATE
        suitTrack = self.getSuitTrack(playRate=self.PLAY_RATE)
        particleNode = self.invoker.attachNewNode('dt-particle-node')
        particleNode.setBin('fixed', 1)
        partTrack = self.getPartTrack(
            particleEffect, partDelay/self.PLAY_RATE, 2.8, [particleEffect, particleNode, 0], softStop=-1.0
        )
        partTrack2 = self.getPartTrack(
            particleEffect2, partDelay/self.PLAY_RATE, 2.8, [particleEffect2, particleNode, 0], softStop=-1.0
        )
        partTracks = Sequence(
            Parallel(partTrack, partTrack2),
            Func(particleNode.removeNode),
        )
        damageAnims = [["duck", 0.01, 0.4, 1.05], ["cringe", 1e-06, 0.8]]
        toonTrack = self.getToonTrack(
            damageDelay=damageDelay,
            splicedDamageAnims=damageAnims,
            dodgeDelay=dodgeDelay,
            splicedDodgeAnims=[["duck", 0.01, 1.4]],
            showMissedExtraTime=0.9,
            showDamageExtraTime=0.8,
        )
        soundTrack = self.getSoundTrack(
            "SA_doubletalk.ogg", delay=2.5/self.PLAY_RATE, node=self.invoker
        )
        return Parallel(suitTrack, toonTrack, partTracks, soundTrack)


@AttackClass(attackType=AttackEnum.DOWNSIZE)
class Downsize(SuitSingleAttack):
    ANIM_NAME = "magic2"
    PLAY_RATE = 1.2
    OPEN_SHOT_DUR = 1.8

    def doAttack(self):
        target = self.targetDicts[0]
        toon = target["avatar"]
        damageDelay = 2.3/self.PLAY_RATE
        sprayEffect = BattleParticles.createParticleEffect(file="downsizeSpray")
        cloudEffect = BattleParticles.createParticleEffect(file="downsizeCloud")
        toonPos = toon.getPos(toon)
        cloudPos = Point3(
            toonPos.getX(), toonPos.getY(), toonPos.getZ() + toon.getHeight() * 0.55
        )
        cloudEffect.setPos(cloudPos)
        suitTrack = self.getSuitTrack(playRate=self.PLAY_RATE)
        sprayNode = self.battle.attachNewNode('spray-node')
        sprayNode.setPos(self.battle.getActorPosHpr(self.invoker)[0])
        sprayNode.headsUp(toon)
        sprayTrack = Sequence(
            self.getPartTrack(sprayEffect, 1.0/self.PLAY_RATE, 2.28, [sprayEffect, sprayNode, 0], softStop=-1.0),
            Func(sprayNode.removeNode),
        )
        cloudTrack = self.getPartTrack(cloudEffect, 2.1/self.PLAY_RATE, 1.9, [cloudEffect, toon, 0])
        if target["landed"]:
            initialScale = toon.getScale()
            downScale = Vec3(0.4, 0.4, 0.4)
            shrinkTimeMod = 0.7
            shrinkTrack = Sequence(
                Wait(damageDelay + (0.5/self.PLAY_RATE)),
                Func(self.battle.movie.needRestoreToonScale),
                LerpScaleInterval(toon, 1.0*shrinkTimeMod, downScale * 1.05),
                LerpScaleInterval(toon, 0.1*shrinkTimeMod, downScale * 0.95),
                LerpScaleInterval(toon, 0.1*shrinkTimeMod, downScale),
                Wait(1.5*shrinkTimeMod),
                LerpScaleInterval(toon, 0.5*shrinkTimeMod, initialScale * 1.2),
                LerpScaleInterval(toon, 0.15*shrinkTimeMod, initialScale * 0.8),
                LerpScaleInterval(toon, 0.15*shrinkTimeMod, initialScale),
                Func(self.battle.movie.clearRestoreToonScale),
            )
        damageAnims = [
            ["lose", 0.5, 2.17, 1.7],
            ["sidestep-right", 0.01, 2.97, 1.49]
        ]
        toonTrack = self.getToonTrack(
            damageDelay=damageDelay,
            splicedDamageAnims=damageAnims,
            dodgeDelay=0.6/self.PLAY_RATE,
            dodgeAnimNames=["sidestep"],
        )
        if target["landed"]:
            shrinkSound = globalBattleSoundCache.getSound("SA_head_shrink_only.ogg")
            soundTrack = Sequence(
                Wait(damageDelay),
                Parallel(
                    SoundInterval(shrinkSound, duration=2.1, node=self.invoker),
                    Sequence(
                        Wait(1.9),
                        self.getSoundTrack("SA_head_grow_back_only.ogg", duration=1.8, node=self.invoker, playRate=1.05),
                    ),
                ),
            )
            return Parallel(suitTrack, sprayTrack, cloudTrack, shrinkTrack, soundTrack, toonTrack)
        else:
            return Parallel(suitTrack, sprayTrack, toonTrack)


@AttackClass(attackType=AttackEnum.EVICTION_NOTICE)
class EvictionNotice(SuitSingleAttack):
    ANIM_NAME = "throw-paper"
    PLAY_RATE = 1.4
    OPEN_SHOT_DUR = 3/PLAY_RATE

    def doAttack(self):
        target = self.targetDicts[0]
        toon = target["avatar"]
        paper = globalPropPool.getProp("shredder-paper")
        suitTrack = self.getSuitTrack(playRate=self.PLAY_RATE)
        posPoints = [Point3(0.8, -1.75,-0.55), VBase3(40.584, -101.945, 18.316)]
        propTrack = Sequence(
            self.getPropAppearTrack(
                paper,
                self.invoker.getRightHand(),
                posPoints,
                1.0/self.PLAY_RATE,
                MovieUtil.PNT3_ONE,
                scaleUpTime=0.2,
            )
        )
        propTrack.append(Wait(1.73/self.PLAY_RATE))
        hitPoint = self.toonTorsoPoint(toon, zOffset=-0.6)
        hitPoint.setX(hitPoint.getX() - 0.1)
        missPoint = self.toonGroundPoint(toon, 0.7, parent=self.battle)
        missPoint.setX(missPoint.getX() - 1.1)
        propTrack.append(
            self.getPropThrowTrack(paper, [hitPoint], [missPoint], hitDuration=0.36/self.PLAY_RATE,
                                   missDuration=0.36/self.PLAY_RATE, parent=self.battle)
        )
        dodgeAnims = [["duck", 0.01, 1.22, 2.5]]
        toonTrack = self.getToonTrack(3.4/self.PLAY_RATE, ["slip-backward"], 2.8/self.PLAY_RATE, splicedDodgeAnims=dodgeAnims, dodgeAnimPlayRate=1.3)
        return Parallel(suitTrack, toonTrack, propTrack)


@AttackClass(attackType=AttackEnum.EVIL_EYE)
class EvilEye(SuitSingleAttack):
    ANIM_NAME = "glower"
    PLAY_RATE = 1.15
    OPEN_SHOT_DUR = 2.7/PLAY_RATE

    def doAttack(self):
        target = self.targetDicts[0]
        toon = target["avatar"]
        eye = globalPropPool.getProp("evil-eye")
        damageDelay = 2.14/self.PLAY_RATE
        dodgeDelay = 1.64/self.PLAY_RATE

        eyePos = {
            "cr": [Point3(-0.25, 4.85, 5.75), VBase3(-155.0, -20.0, 0.0)],
            "tf": [Point3(-0.4, 3.85, 5.01), VBase3(-155.0, -20.0, 0.0)],
            "mg": [Point3(-0.7, 3.9, 5.2), VBase3(-155.0, -20.0, 0.0)],
            "le": [Point3(-0.3, 4.7, 5.3), VBase3(-155.0, -20.0, 0.0)],
            "dl": [Point3(-0.35, 4.0, 5.01), VBase3(-155.0, -20.0, 0.0)],
            "br": [Point3(-0.4, 5.0, 5.5), VBase3(-155.0, -20.0, 0.0)],
            "lgator": [Point3(-0.35, 5.5, 6.4), VBase3(-155.0, -20.0, 0.0)],
        }

        posPoints = eyePos.get(
            self.invoker.dna.name,
            [Point3(-0.4, 3.65, 5.01), VBase3(-155.0, -20.0, 0.0)],
        )
        suitHoldStart = 1.06/self.PLAY_RATE
        suitHoldStop = 1.69/self.PLAY_RATE
        suitHoldDuration = suitHoldStop - suitHoldStart
        eyeHoldDuration = 1.1/self.PLAY_RATE
        moveDuration = 1.1/self.PLAY_RATE
        suitSplicedAnims = []
        suitSplicedAnims.append(["glower", 0.01, 0.01, suitHoldStart])
        suitSplicedAnims.extend(
            self.getSplicedLerpAnims(
                "glower", suitHoldDuration, 1.1/self.PLAY_RATE, startTime=suitHoldStart
            )
        )
        suitSplicedAnims.append(["glower", 0.01, suitHoldStop])
        suitTrack = self.getSuitTrack(splicedAnims=suitSplicedAnims, playRate=self.PLAY_RATE)
        eyeAppearTrack = Sequence(
            Wait(suitHoldStart),
            Func(self.showProp, eye, self.invoker, posPoints[0], posPoints[1]),
            LerpScaleInterval(eye, suitHoldDuration, Point3(11, 11, 11)),
            Wait(eyeHoldDuration * 0.3),
            LerpHprInterval(eye, 0.02, Point3(205, 40, 0)),
            Wait(eyeHoldDuration * 0.7),
            Func(self.battle.movie.needRestoreRenderProp, eye),
            Func(eye.wrtReparentTo, self.battle),
        )
        useMoveDuration = moveDuration * (0.7 if target["landed"] else 1.0)
        toonFace = self.toonFacePoint(toon, parent=self.battle)
        if target["landed"]:
            lerpInterval = LerpPosInterval(eye, useMoveDuration, toonFace)
        else:
            lerpInterval = Parallel(
                LerpPosInterval(eye, useMoveDuration, Point3(toonFace.getX(), toonFace.getY() - 8, toonFace.getZ() - 2)),
                Sequence(
                    Wait(useMoveDuration - (0.4/self.PLAY_RATE)),
                    Func(eye.setTransparency, 1),
                    LerpColorScaleInterval(eye, (0.4/self.PLAY_RATE), (1, 1, 1, 0), blendType='easeIn'),
                ),
            )
        eyeMoveTrack = lerpInterval
        eyeRollTrack = LerpHprInterval(eye, useMoveDuration, Point3(0, 0, -180))
        eyePropTrack = Sequence(
            eyeAppearTrack,
            Parallel(eyeMoveTrack, eyeRollTrack),
            Func(self.battle.movie.clearRenderProp, eye),
            Func(MovieUtil.removeProp, eye),
        )
        damageAnims = [["duck", 0.01, 0.01, 1.4], ["cringe", 0.01, 0.3]]
        toonTrack = self.getToonTrack(
            splicedDamageAnims=damageAnims,
            damageDelay=damageDelay,
            dodgeDelay=dodgeDelay,
            dodgeAnimNames=["duck"],
            showDamageExtraTime=1.7,
            showMissedExtraTime=1.7,
            damageAnimPlayRate=self.PLAY_RATE,
            dodgeAnimPlayRate=self.PLAY_RATE,
        )
        soundTrack = self.getSoundTrack("SA_evil_eye.ogg", delay=1.3/self.PLAY_RATE, node=self.invoker, playRate=1.05, duration=1.0)
        soundTrack2 = self.getSoundTrack("SA_evil_eye.ogg", delay=2.5/self.PLAY_RATE, node=self.invoker, playRate=1.1, duration=2.0, startTime=1.9/self.PLAY_RATE)
        return Parallel(suitTrack, toonTrack, eyePropTrack, soundTrack, soundTrack2)


@AttackClass(attackType=AttackEnum.FALLING_KNIFE)
class FallingKnife(SuitSingleAttack):
    ANIM_NAME = "falling-knife"
    OPEN_SHOT_DUR = 3.2

    def doAttack(self):
        target = self.targetDicts[0]
        toon = target["avatar"]

        knife = globalPropPool.getProp("dagger")
        knife2 = MovieUtil.copyProp(knife)
        knife2.hide()
        suitTrack = self.getSuitTrack()

        damageDelay = 3.9
        dodgeDelay = 2.3
        propDelay = 0.35

        particleTrack = Sequence()
        if target["landed"]:
            particleNode = self.battle.attachNewNode('falling-knife-impact-particle-holder')
            particleNode.setPos(self.battle.getActorPosHpr(toon)[0])

            sprayEffect = BattleParticles.createParticleEffect(file='fallingKnifeSpray')

            softStop = 1.5
            particleTrack = Sequence(
                self.getPartTrack(
                    sprayEffect, damageDelay, 0.2+softStop, [sprayEffect, particleNode, 0], softStop=-softStop
                ),
                Func(particleNode.removeNode),
            )

        throwPoint = render.getRelativePoint(self.battle, self.battle.getActorPosHpr(self.invoker)[0])
        throwPoint.setZ(throwPoint.getZ() + 25)
        dropPoint = toon.getPos(render)
        dropPoint.setZ(dropPoint.getZ() + 25)
        hitPoint = toon.getPos(render)

        def setKnifeHpr(knife2=knife2):
            knife2.setHpr(camera.getH() + 90, -90, 0)

        posPoints = [Point3(-0.2723, 0.5628, -0.0545), Point3(0, 0, 0)]
        propTrack = Sequence(
            self.getPropAppearTrack(
                knife,
                self.invoker.getRightHand(),
                posPoints,
                propDelay,
                Point3(0.96, 0.96, 0.96),
                scaleUpTime=0.3,
            ),
            Wait(1.07),
            Parallel(
                Sequence(
                    Wait(0.15),
                    LerpScaleInterval(knife, 0.125, 0.01, blendType='easeIn'),
                    Func(knife.hide),
                ),
                Parallel(
                    self.getPropThrowTrack(
                        knife,
                        [throwPoint],
                        [throwPoint],
                        hitDuration=0.275,
                        missDuration=0.275,
                    ),
                    LerpHprInterval(knife, 0.45, (0, 90, 0), blendType='easeIn'),
                ),
            ),
            Wait(1.35),
            Func(knife2.setPos, dropPoint),
            Func(knife2.setScale, 0.9),
            Func(setKnifeHpr),
            Parallel(
                self.getPropThrowTrack(
                    knife2,
                    [hitPoint],
                    [hitPoint],
                    hitDuration=0.525,
                    missDuration=0.525,
                ),
                Func(knife2.show),
                Sequence(
                    Wait(0.4),
                    LerpScaleInterval(knife2, 0.124,  0.01, blendType='easeIn'),
                ),
            ),
        )

        damageAnims = [["slip-forward", 0.01, 0.35]]
        toonTrack = self.getToonTrack(
            damageDelay=damageDelay,
            splicedDamageAnims=damageAnims,
            dodgeDelay=dodgeDelay,
            dodgeAnimNames=["sidestep"],
            dodgeAnimPlayRate=1.2,
        )
        soundTrack = self.getSoundTrack(
            f"SA_falling_knife{'' if target['landed'] else '_miss'}.ogg", delay=0.0, node=self.invoker
        )
        return Parallel(suitTrack, toonTrack, soundTrack, propTrack, particleTrack)

    def getCameraShot(self, duration):
        toon = self.targetDicts[0]["avatar"]
        openShotDuration = self.OPEN_SHOT_DUR
        if openShotDuration > duration:
            openShotDuration = duration
        openShot = self.camera.randomOverShoulderShot(
            self.invoker, toon, self.battle, openShotDuration, focus='suit'
        )
        toonPos = toon.getPos(self.battle)
        closeShot = self.camera.heldRelativeShot(self.battle, toonPos[0] + 6, toonPos[1] + 6.75, toonPos[2] + 1.5, 138, 20, 0, duration - openShotDuration)
        return Sequence(openShot, closeShot)


@AttackClass(attackType=AttackEnum.FILIBUSTER)
class Filibuster(SuitSingleAttack):
    ANIM_NAME = "speak"
    PLAY_RATE = 1.5
    OPEN_SHOT_DUR = 3/PLAY_RATE

    def doAttack(self):
        target = self.targetDicts[0]
        toon = target["avatar"]
        BattleParticles.loadParticles()
        sprayEffect = BattleParticles.createParticleEffect(file="filibusterSpray")
        sprayEffect2 = BattleParticles.createParticleEffect(file="filibusterSpray")
        sprayEffect3 = BattleParticles.createParticleEffect(file="filibusterSpray")
        sprayEffect4 = BattleParticles.createParticleEffect(file="filibusterSpray")
        color = Vec4(0.4, 0, 0, 1)
        BattleParticles.setEffectTexture(sprayEffect, "filibuster-cut", color=color)
        BattleParticles.setEffectTexture(sprayEffect2, "filibuster-fiscal", color=color)
        BattleParticles.setEffectTexture(
            sprayEffect3, "filibuster-impeach", color=color
        )
        BattleParticles.setEffectTexture(sprayEffect4, "filibuster-inc", color=color)
        partDelay = 3.3/self.PLAY_RATE
        partDuration = 1.8/self.PLAY_RATE
        damageDelay = 3.7/self.PLAY_RATE
        dodgeDelay = 2.6/self.PLAY_RATE
        suitTrack = self.getSuitTrack(playRate=self.PLAY_RATE)
        sprayNode = self.battle.attachNewNode('filibuster-spray-node')
        sprayNode.setPos(self.battle.getActorPosHpr(self.invoker)[0])
        sprayNode.headsUp(toon)
        sprayNode.setBin('fixed', 1)
        sprayTrack = self.getPartTrack(
            sprayEffect, partDelay, partDuration, [sprayEffect, sprayNode, 0]
        )
        sprayTrack2 = self.getPartTrack(
            sprayEffect2, partDelay + 0.4, partDuration, [sprayEffect2, sprayNode, 0]
        )
        sprayTrack3 = self.getPartTrack(
            sprayEffect3, partDelay + 0.8, partDuration, [sprayEffect3, sprayNode, 0]
        )
        sprayTrack4 = Sequence(
            self.getPartTrack(sprayEffect4, partDelay + 1.2, partDuration, [sprayEffect4, sprayNode, 0]),
            Func(sprayNode.removeNode)
        )
        if self.invoker.dna.name == "stenog":
            sprayNode.setZ(self.invoker.getHeight() - 2.5)
            sprayNode.setP(-45)

        damageAnims = [
            ["cringe", 1e-05, 0.3, 0.8],
            ["cringe", 1e-05, 0.3, 2.0]
        ]

        toonTrack = self.getToonTrack(
            damageDelay=damageDelay,
            splicedDamageAnims=damageAnims,
            dodgeDelay=dodgeDelay,
            dodgeAnimNames=["duck"],
            damageAnimPlayRate=1.15,
            dodgeAnimPlayRate=1.15,
        )
        soundTrack = self.getSoundTrack(
            "SA_filibuster.ogg", delay=3.3/self.PLAY_RATE, node=self.invoker, duration=3.0
        )
        if target["landed"]:
            return Parallel(
                suitTrack,
                toonTrack,
                soundTrack,
                sprayTrack,
                sprayTrack2,
                sprayTrack3,
                sprayTrack4,
            )
        else:
            return Parallel(
                suitTrack, toonTrack, soundTrack, sprayTrack, sprayTrack2, sprayTrack3
            )


@AttackClass(attackType=AttackEnum.FILL_WITH_LEAD)
class FillWithLead(SuitSingleAttack):
    ANIM_NAME = "pencil-sharpener"
    PLAY_RATE = 1.2
    OPEN_SHOT_DUR = 3.3/PLAY_RATE

    def doAttack(self):
        target = self.targetDicts[0]
        toon = target["avatar"]
        pencil = globalPropPool.getProp("pencil")
        sharpener = globalPropPool.getProp("sharpener")
        BattleParticles.loadParticles()
        sprayEffect = BattleParticles.createParticleEffect(file="fillWithLeadSpray")
        torsoSmotherEffect = BattleParticles.createParticleEffect(
            file="fillWithLeadSmother"
        )
        BattleParticles.setEffectTexture(
            sprayEffect, "roll-o-dex", color=Vec4(0, 0, 0, 1)
        )
        BattleParticles.setEffectTexture(
            torsoSmotherEffect, "roll-o-dex", color=Vec4(0, 0, 0, 1)
        )
        suitTrack = self.getSuitTrack()
        sprayTrack = self.getPartTrack(
            sprayEffect, 3.05/self.PLAY_RATE, 1.9/self.PLAY_RATE, [sprayEffect, self.invoker, 0]
        )
        pencilPosPoints = [
            Point3(-0.29, -0.33, -0.13),
            VBase3(160.565, -11.653, -169.244),
        ]
        pencilPropTrack = self.getPropTrack(
            pencil,
            self.invoker.getRightHand(),
            pencilPosPoints,
            0.3/self.PLAY_RATE,
            3.5/self.PLAY_RATE,
            scaleUpTime=0.2/self.PLAY_RATE,
            scaleDownTime=0.5/self.PLAY_RATE,
        )
        sharpenerPosPoints = [Point3(0, 0.0, -0.03), MovieUtil.PNT3_ZERO]
        sharpenerPropTrack = self.getPropTrack(
            sharpener,
            self.invoker.getLeftHand(),
            sharpenerPosPoints,
            0.9/self.PLAY_RATE,
            2.8/self.PLAY_RATE,
            scaleUpPoint=MovieUtil.PNT3_ONE,
            scaleUpTime=0.5/self.PLAY_RATE,
            scaleDownTime=0.5/self.PLAY_RATE,
        )
        damageAnims = [["cringe", 0.01]]
        toonTrack = self.getToonTrack(
            damageDelay=3.7/self.PLAY_RATE,
            splicedDamageAnims=damageAnims,
            dodgeDelay=(suitTrack.getDuration() - 2.55)/self.PLAY_RATE,
            dodgeAnimNames=["sidestep"],
            showDamageExtraTime=0.5,
            showMissedExtraTime=0.2/self.PLAY_RATE,
            dodgeAnimPlayRate=1.2,
        )
        animal = toon.style.getAnimal()
        bodyScale = ToontownGlobals.toonBodyScales[animal]
        legsHeight = ToontownGlobals.legHeightDict[toon.style.legs] * bodyScale
        torsoEffectHeight = (
            ToontownGlobals.torsoHeightDict[toon.style.torso] * bodyScale / 2
            + legsHeight
        )
        effectX = torsoSmotherEffect.getX()
        effectY = torsoSmotherEffect.getY()
        torsoSmotherEffect.setPos(effectX, effectY - 1, torsoEffectHeight)
        partDelay = 3.5/self.PLAY_RATE
        partIvalDelay = 0.7/self.PLAY_RATE
        partDuration = 1.0/self.PLAY_RATE
        torsoTrack = self.getPartTrack(
            torsoSmotherEffect,
            partDelay + partIvalDelay,
            partDuration,
            [torsoSmotherEffect, toon, 0],
        )

        def colorParts(parts):
            track = Parallel()
            for nextPart in parts:
                track.append(Func(nextPart.setColorScale, Vec4(0, 0, 0, 1)))

            return track

        def resetParts(parts):
            track = Parallel()
            for nextPart in parts:
                track.append(Func(nextPart.clearColorScale))

            return track

        if target["landed"]:
            colorTrack = Sequence()
            headParts = toon.getHeadParts()
            torsoParts = toon.getTorsoParts()
            legsParts = toon.getLegsParts()
            colorTrack.append(Wait(partDelay + 0.2))
            colorTrack.append(Func(self.battle.movie.needRestoreColor))
            colorTrack.append(colorParts(headParts + torsoParts + legsParts))
            colorTrack.append(Wait(2.5))
            colorTrack.append(resetParts(headParts + torsoParts + legsParts))
            colorTrack.append(Func(self.battle.movie.clearRestoreColor))
            return Parallel(
                suitTrack,
                pencilPropTrack,
                sharpenerPropTrack,
                sprayTrack,
                torsoTrack,
                colorTrack,
                toonTrack,
            )
        else:
            return Parallel(
                suitTrack, pencilPropTrack, sharpenerPropTrack, sprayTrack, toonTrack
            )


@AttackClass(attackType=AttackEnum.FINGER_WAG)
class FingerWag(SuitSingleAttack):
    ANIM_NAME = "finger-wag"
    OPEN_SHOT_DUR = 2.2

    def doAttack(self):
        target = self.targetDicts[0]
        toon = target["avatar"]
        BattleParticles.loadParticles()
        particleEffect = BattleParticles.createParticleEffect("FingerWag")
        BattleParticles.setEffectTexture(
            particleEffect, "blah", color=Vec4(0.55, 0, 0.55, 1)
        )
        partDelay = 1.3
        damageDelay = 2.7
        dodgeDelay = 1.5
        suitTrack = self.getSuitTrack()
        particleNode = self.battle.attachNewNode('finger-wag-particle-node')
        particleNode.setPos(self.battle.getActorPosHpr(self.invoker)[0])
        particleNode.headsUp(toon)
        particleNode.setBin('fixed', 1)
        partTrack = Sequence(
            self.getPartTrack(particleEffect, partDelay, 3.5, [particleEffect, particleNode, 0], softStop=-1.5),
            Func(particleNode.removeNode),
        )
        if self.invoker.dna.name == "mm":
            particleEffect.setPos(0.167, 1.0, 1.3)
        elif self.invoker.dna.name == "tm":
            particleEffect.setPos(0, 1.1, self.invoker.getHeight() - 1.2)
        elif self.invoker.dna.name == "tw":
            particleEffect.setPos(0.167, 1.8, 5)
            particleEffect.setHpr(-90.0, -60.0, 180.0)
        elif self.invoker.dna.name == "p":
            particleEffect.setPos(0.167, 1.4, 3.6)
        elif self.invoker.dna.name == "pp":
            particleEffect.setPos(0.167, 1, 4.1)
        elif self.invoker.dna.name == "pf":
            particleEffect.setPos(0.167, 1.4, 4.65)
        elif self.invoker.dna.name == "bs":
            particleEffect.setPos(0.167, 1.4, 5.3)
        elif self.invoker.dna.name == "bw":
            particleEffect.setPos(0.167, 2.0, self.invoker.getHeight() - 1.75)
            particleEffect.setP(-110)
        elif self.invoker.dna.name == "sgoat":
            particleEffect.setPos(0.167, 1.9, self.invoker.getHeight() - 2)
            particleEffect.setP(-110)
        elif self.invoker.dna.name == "mouthp":
            particleEffect.setPos(0.167, 2.2, self.invoker.getHeight() - 1.9)
            particleEffect.setP(-110)
        elif self.invoker.dna.name == "erfit":
            particleEffect.setPos(0.167, 1.9, self.invoker.getHeight() - 1.9)
            particleEffect.setP(-115)
        toonTrack = self.getToonTrack(
            damageDelay, ["slip-backward"], dodgeDelay, ["duck"], dodgeAnimPlayRate=1.15, showMissedExtraTime=0.85
        )
        soundTrack = self.getSoundTrack(
            "SA_finger_wag.ogg", delay=1.3, node=self.invoker
        )
        return Parallel(suitTrack, toonTrack, partTrack, soundTrack)


@AttackClass(attackType=AttackEnum.FIRED)
class Fired(SuitSingleAttack):
    ANIM_NAME = "magic2"
    OPEN_SHOT_DUR = 1.5

    def doAttack(self):
        target = self.targetDicts[0]
        toon = target["avatar"]
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
        suitTrack = self.getSuitTrack()
        baseFlameTrack = self.getPartTrack(
            baseFlameEffect, 1.0, 1.9, [baseFlameEffect, toon, 0]
        )
        flameTrack = self.getPartTrack(flameEffect, 1.0, 1.9, [flameEffect, toon, 0])
        flecksTrack = self.getPartTrack(flecksEffect, 1.8, 1.1, [flecksEffect, toon, 0])
        baseFlameSmallTrack = self.getPartTrack(
            baseFlameSmall, 1.0, 1.9, [baseFlameSmall, toon, 0]
        )
        flameSmallTrack = self.getPartTrack(flameSmall, 1.0, 1.9, [flameSmall, toon, 0])
        flecksSmallTrack = self.getPartTrack(
            flecksSmall, 1.8, 1.1, [flecksSmall, toon, 0]
        )

        def changeColor(parts):
            track = Parallel()
            for nextPart in parts:
                track.append(Func(nextPart.setColorScale, Vec4(0, 0, 0, 1)))

            return track

        def resetColor(parts):
            track = Parallel()
            for nextPart in parts:
                track.append(Func(nextPart.clearColorScale))

            return track

        if target["landed"]:
            headParts = toon.getHeadParts()
            torsoParts = toon.getTorsoParts()
            legsParts = toon.getLegsParts()
            colorTrack = Sequence()
            colorTrack.append(Wait(2.0))
            colorTrack.append(Func(self.battle.movie.needRestoreColor))
            colorTrack.append(changeColor(headParts))
            colorTrack.append(changeColor(torsoParts))
            colorTrack.append(changeColor(legsParts))
            colorTrack.append(Wait(2.8))
            colorTrack.append(resetColor(headParts))
            colorTrack.append(resetColor(torsoParts))
            colorTrack.append(resetColor(legsParts))
            colorTrack.append(Func(self.battle.movie.clearRestoreColor))
        damageAnims = []
        damageAnims.append(["cringe", 0.01, 0.7, 0.62])
        damageAnims.append(["slip-forward", 1e-05, 0.4, 1.2])
        damageAnims.extend(
            self.getSplicedLerpAnims("slip-forward", 0.31, 0.8, startTime=1.2)
        )
        toonTrack = self.getToonTrack(
            damageDelay=1.5,
            splicedDamageAnims=damageAnims,
            dodgeDelay=0.3,
            dodgeAnimNames=["sidestep"],
        )
        soundTrack = self.getSoundTrack("SA_hot_air.ogg", delay=1.0, node=self.invoker)
        if target["landed"]:
            return Parallel(suitTrack, baseFlameTrack, flameTrack, flecksTrack, toonTrack, colorTrack, soundTrack)
        else:
            return Parallel(suitTrack, baseFlameSmallTrack, flameSmallTrack, flecksSmallTrack, toonTrack, soundTrack)


@AttackClass(attackType=AttackEnum.FOUNTAIN_PEN)
class FountainPen(SuitSingleAttack):
    ANIM_NAME = "pen-squirt"
    OPEN_SHOT_DUR = 30/24

    def doAttack(self):
        target = self.targetDicts[0]
        toon = target["avatar"]
        pen = globalPropPool.getProp("pen")

        def getPenTip(pen=pen):
            tip = pen.find("**/joint_toSpray")
            return tip.getPos(render)

        hitPoint = lambda toon=toon: self.toonFacePoint(toon)
        missPoint = lambda prop=pen, toon=toon: self.toonMissPoint(
            prop, toon, 0, parent=render
        )
        hitSprayTrack = MovieUtil.getSprayTrack(
            self.battle,
            VBase4(0, 0, 0, 1),
            getPenTip,
            hitPoint,
            0.2,
            0.2,
            0.2,
            horizScale=0.1,
            vertScale=0.1,
        )
        missSprayTrack = MovieUtil.getSprayTrack(
            self.battle,
            VBase4(0, 0, 0, 1),
            getPenTip,
            missPoint,
            0.2,
            0.2,
            0.2,
            horizScale=0.1,
            vertScale=0.1,
        )
        suitTrack = self.getSuitTrack()
        propTrack = Sequence(
            Wait(0.01),
            Func(self.showProp, pen, self.invoker.getRightHand(), MovieUtil.PNT3_ZERO),
            LerpScaleInterval(pen, 0.5, Point3(1.5, 1.5, 1.5)),
            Wait(0.9),
        )
        if target["landed"]:
            propTrack.append(hitSprayTrack)
        else:
            propTrack.append(missSprayTrack)
        propTrack += [
            LerpScaleInterval(pen, 0.5, MovieUtil.PNT3_NEARZERO),
            Func(MovieUtil.removeProp, pen),
        ]
        splashTrack = Sequence()
        if target["landed"]:

            def prepSplash(splash, targetPoint):
                splash.reparentTo(render)
                splash.setPos(targetPoint)
                scale = splash.getScale()
                splash.setBillboardPointWorld()
                splash.setScale(scale)

            splash = globalPropPool.getProp("splash-from-splat")
            splash.setColor(0, 0, 0, 1)
            splash.setScale(0.25)
            splashTrack = Sequence(
                Func(self.battle.movie.needRestoreRenderProp, splash),
                Wait(39/24),
                Func(prepSplash, splash, self.toonFacePoint(toon)),
                ActorInterval(splash, "splash-from-splat"),
                Func(MovieUtil.removeProp, splash),
                Func(self.battle.movie.clearRenderProp, splash),
            )
            headParts = toon.getHeadParts()
            splashTrack.append(Func(self.battle.movie.needRestoreColor))
            for nextPart in headParts:
                splashTrack.append(Func(nextPart.setColorScale, Vec4(0, 0, 0, 1)))

            splashTrack.append(Func(MovieUtil.removeProp, splash))
            splashTrack.append(Wait(2.6))
            for nextPart in headParts:
                splashTrack.append(Func(nextPart.clearColorScale))

            splashTrack.append(Func(self.battle.movie.clearRestoreColor))
        penSpill = BattleParticles.createParticleEffect(file="penSpill")
        penSpill.setPos(getPenTip())
        penSpillTrack = self.getPartTrack(penSpill, 1.0, 0.7, [penSpill, pen, 0])
        toonTrack = self.getToonTrack(
            1.6,
            ["conked"],
            dodgeDelay=0.11,
            splicedDodgeAnims=[["duck", 0.01, 0.6]],
            damageAnimPlayRate=1.2,
            showMissedExtraTime=1.66,
        )
        soundTrack = self.getSoundTrack(
            "SA_fountain_pen.ogg", delay=1.6, node=self.invoker
        )
        return Parallel(
            suitTrack, toonTrack, propTrack, soundTrack, penSpillTrack, splashTrack
        )


@AttackClass(attackType=AttackEnum.FREEZE_ASSETS)
class FreezeAssets(SuitSingleAttack):
    ANIM_NAME = "glower"
    PLAY_RATE = 1.2
    OPEN_SHOT_DUR = 1.7/PLAY_RATE

    def doAttack(self):
        target = self.targetDicts[0]
        toon = target["avatar"]
        BattleParticles.loadParticles()
        snowEffect = BattleParticles.createParticleEffect("FreezeAssets")
        BattleParticles.setEffectTexture(snowEffect, "snow-particle")
        cloud = globalPropPool.getProp("stormcloud")
        partDelay = 0.2/self.PLAY_RATE
        damageDelay = 2.5/self.PLAY_RATE
        dodgeDelay = 1.7/self.PLAY_RATE
        suitTrack = self.getSuitTrack(delay=0.4, playRate=self.PLAY_RATE)
        initialCloudHeight = self.invoker.height + 3
        cloudPosPoints = [Point3(0, 3, initialCloudHeight), MovieUtil.PNT3_ZERO]
        cloudPropTrack = Sequence()
        cloudPropTrack.append(Func(cloud.pose, "stormcloud", 0))
        cloudPropTrack.append(
            self.getPropAppearTrack(
                cloud,
                self.invoker,
                cloudPosPoints,
                1e-06,
                Point3(3, 3, 3),
                scaleUpTime=0.2,
                blendType='easeOut',
            )
        )
        cloudPropTrack.append(Func(self.battle.movie.needRestoreRenderProp, cloud))
        cloudPropTrack.append(Func(cloud.wrtReparentTo, render))
        targetPoint = self.toonFacePoint(toon)
        targetPoint.setZ(targetPoint[2] + 3)
        cloudPropTrack.append(Wait(1.1/self.PLAY_RATE))
        cloudPropTrack.append(LerpPosInterval(cloud, 0.7/self.PLAY_RATE, pos=targetPoint, blendType='easeInOut'))
        cloudPropTrack.append(Wait(partDelay))
        cloudPropTrack.append(
            ParticleInterval(
                snowEffect, cloud, worldRelative=0, duration=2.1/self.PLAY_RATE, cleanup=True, softStopT=-0.8
            )
        )
        cloudPropTrack.append(Wait(0.2/self.PLAY_RATE))
        cloudPropTrack.append(LerpScaleInterval(cloud, 0.25/self.PLAY_RATE, MovieUtil.PNT3_NEARZERO, blendType='easeIn'))
        cloudPropTrack.append(Func(MovieUtil.removeProp, cloud))
        cloudPropTrack.append(Func(self.battle.movie.clearRenderProp, cloud))
        damageAnims = [["cringe", 0.01, 0.4, 0.8], ["duck", 0.01, 1.6]]
        toonTrack = self.getToonTrack(
            damageDelay=damageDelay,
            splicedDamageAnims=damageAnims,
            dodgeDelay=dodgeDelay,
            dodgeAnimNames=["sidestep"],
            showMissedExtraTime=1.2/self.PLAY_RATE,
            dodgeAnimPlayRate=1.2,
        )
        return Parallel(suitTrack, toonTrack, cloudPropTrack)


@AttackClass(attackType=AttackEnum.GLOWER_POWER)
class GlowerPower(SuitSingleAttack):
    ANIM_NAME = "glower"
    OPEN_SHOT_DUR = 1.4
    DefaultPoints = (
        [Point3(0.4, 3.8, 3.7), MovieUtil.PNT3_ZERO],
        [Point3(-0.4, 3.8, 3.7), MovieUtil.PNT3_ZERO],
    )
    PosPoints = {
        # Sellbot
        "dopr": (
            [Point3(0.6, 4.5, 5.55), MovieUtil.PNT3_ZERO],
            [Point3(-0.3, 4.5, 5.55), MovieUtil.PNT3_ZERO],
        ),
        "dopa": (
            [Point3(0.6, 5.2, 7.6), MovieUtil.PNT3_ZERO],
            [Point3(-0.4, 5.2, 7.6), MovieUtil.PNT3_ZERO],
        ),
        # Cashbot
        "tw": (
            [Point3(0.45, 3.5, 3.9), MovieUtil.PNT3_ZERO],
            [Point3(-0.35, 3.5, 3.9), MovieUtil.PNT3_ZERO],
        ),
        # Lawbot
        "ad": (
            [Point3(0.36, 4.2, 4.55), MovieUtil.PNT3_ZERO],
            [Point3(-0.36, 4.2, 4.55), MovieUtil.PNT3_ZERO],
        ),
        # Bossbot
        "hh": (
            [Point3(0.54, 4.3, 5.4), MovieUtil.PNT3_ZERO],
            [Point3(-0.06, 4.3, 5.4), MovieUtil.PNT3_ZERO],
        ),
        "tbc": (
            [Point3(0.6, 5.3, 6.0), MovieUtil.PNT3_ZERO],
            [Point3(-0.1, 5.3, 6.0), MovieUtil.PNT3_ZERO],
        ),
        "autocad": (
            [Point3(0.4, 3.8, 3.7), MovieUtil.PNT3_ZERO],
            [Point3(-0.1, 3.8, 3.7), MovieUtil.PNT3_ZERO],
        ),
        "clubpres": (
            [Point3(0.7, 5.5, 6.8), MovieUtil.PNT3_ZERO],
            [Point3(0.1, 5.5, 6.8), MovieUtil.PNT3_ZERO],
        ),
        "chainsaw": (
            [Point3(0.6, 5.8, 6.2), MovieUtil.PNT3_ZERO],
            [Point3(0.0, 5.8, 6.2), MovieUtil.PNT3_ZERO],
        ),
        # Boardbot
        "dl": (
            [Point3(0.66, 4.2, 4.85), MovieUtil.PNT3_ZERO],
            [Point3(-0.06, 4.2, 4.85), MovieUtil.PNT3_ZERO],
        ),
        "shw": (
            [Point3(1.3, 4.75, 6.2), MovieUtil.PNT3_ZERO],
            [Point3(-0.9, 4.75, 6.2), MovieUtil.PNT3_ZERO],
        ),

        # Event
        "ftf_c": (
            [Point3(0.7, 5.5, 6.8), MovieUtil.PNT3_ZERO],
            [Point3(0.1, 5.5, 6.8), MovieUtil.PNT3_ZERO],
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
        toonTrack = self.getToonTrack(
            damageDelay=1.6,
            splicedDamageAnims=damageAnims,
            dodgeDelay=0.7,
            dodgeAnimNames=["sidestep"],
            dodgeAnimPlayRate=1.2,
        )
        soundTrack = self.getSoundTrack(
            "SA_glower_power.ogg", delay=1.1, node=self.invoker
        )
        return Parallel(
            suitTrack, toonTrack, soundTrack, leftKnifeTracks, rightKnifeTracks
        )


@AttackClass(attackType=AttackEnum.GUILT_TRIP)
class GuiltTrip(SuitGroupAttack):
    ANIM_NAME = "magic1"
    OPEN_SHOT_DUR = 0.9

    def doAttack(self):
        centerColor = Vec4(1.0, 0.2, 0.2, 0.9)
        edgeColor = Vec4(0.9, 0.9, 0.9, 0.4)
        powerBar1 = BattleParticles.createParticleEffect(file="guiltTrip")
        powerBar2 = BattleParticles.createParticleEffect(file="guiltTrip")
        powerBar1.setPos(0, 6.1, 0.4)
        powerBar1.setHpr(-90, 0, 0)
        powerBar2.setPos(0, 6.1, 0.4)
        powerBar2.setHpr(90, 0, 0)
        powerBar1.setScale(5)
        powerBar2.setScale(5)
        powerBar1Particles = powerBar1.getParticlesNamed("particles-1")
        powerBar2Particles = powerBar2.getParticlesNamed("particles-1")
        powerBar1Particles.renderer.setCenterColor(centerColor)
        powerBar1Particles.renderer.setEdgeColor(edgeColor)
        powerBar2Particles.renderer.setCenterColor(centerColor)
        powerBar2Particles.renderer.setEdgeColor(edgeColor)
        waterfallEffect = BattleParticles.createParticleEffect("Waterfall")
        waterfallEffect.setScale(11)
        waterfallParticles = waterfallEffect.getParticlesNamed("particles-1")
        waterfallParticles.renderer.setCenterColor(centerColor)
        waterfallParticles.renderer.setEdgeColor(edgeColor)
        suitTrack = self.getSuitAnimTrack()

        def getPowerTrack(effect):
            partTrack = Sequence(
                Wait(0.7),
                Func(self.battle.movie.needRestoreParticleEffect, effect),
                Func(effect.start, self.invoker),
                Wait(0.4),
                LerpPosInterval(effect, 1.0, Point3(0, 15, 0.4)),
                LerpFunctionInterval(
                    effect.setAlphaScale, fromData=1, toData=0, duration=0.4
                ),
                Func(effect.cleanup),
                Func(self.battle.movie.clearRestoreParticleEffect, effect),
            )
            return partTrack

        partTrack1 = getPowerTrack(powerBar1)
        partTrack2 = getPowerTrack(powerBar2)
        waterfallTrack = self.getPartTrack(
            waterfallEffect, 0.6, 0.6, [waterfallEffect, self.invoker, 0]
        )
        toonTracks = self.getToonTracks(1.5, ["slip-forward"], 0.86, ["jump"])
        soundTrack = self.getSoundTrack(
            "SA_guilt_trip.ogg", delay=1.1, node=self.invoker
        )
        return Parallel(
            suitTrack, partTrack1, partTrack2, soundTrack, waterfallTrack, toonTracks
        )


@AttackClass(attackType=AttackEnum.HALF_WINDSOR)
class HalfWindsor(ClipOnTie):
    def getPropName(self):
        return "half-windsor"

    def getPropActorName(self):
        return None

    def getPosPoints(self):
        return [Point3(-0.3, 1.2, 0.58), VBase3(109, -3, -108.2)]

    def getPropScale(self):
        return Vec3(7, 7, 7)

    def getSfxName(self):
        return "SA_half_windsor_throw.ogg"

    def getHitSound(self):
        return "SA_writeoff_ding_only.ogg"

    def missH(self):
        return -180, -280


@AttackClass(attackType=AttackEnum.HANG_UP)
class HangUp(SuitSingleAttack):
    ANIM_NAME = "phone"
    PLAY_RATE = 1.3
    OPEN_SHOT_DUR = (66/24)/PLAY_RATE

    def doAttack(self):
        phone = globalPropPool.getProp("phone")
        receiver = globalPropPool.getProp("receiver")
        suitTrack = self.getSuitTrack(playRate=self.PLAY_RATE)

        receiverAdjustScale = MovieUtil.PNT3_ONE
        pickupDelay = 0.1/self.PLAY_RATE
        dialDuration = 2.75/self.PLAY_RATE
        finalPhoneDelay = 0.4/self.PLAY_RATE
        scaleUpPoint = MovieUtil.PNT3_ONE

        suitType = getSuitBodyType(self.invoker.dna.name)
        if suitType == "a":
            phonePosPoints = [Point3(0.13, 0.27, -0.11), VBase3(5.939, 2.763, -177.591)]
            receiverPosPoints = [Point3(0.13, 0.27, -0.11), VBase3(-1.854, 2.434, -177.579)]
        else:
            phonePosPoints = [Point3(0.23, 0.17, -0.11), VBase3(5.939, 2.763, -177.591)]
            receiverPosPoints = [Point3(0.13, 0.17, -0.11), VBase3(5.939, 2.763, -177.591)]

        propTrack = Sequence(
            Wait(0.3/self.PLAY_RATE),
            Func(
                self.showProp,
                phone,
                self.invoker.getLeftHand(),
                phonePosPoints[0],
                phonePosPoints[1],
            ),
            Func(
                self.showProp,
                receiver,
                self.invoker.getLeftHand(),
                receiverPosPoints[0],
                receiverPosPoints[1],
            ),
            LerpScaleInterval(phone, 0.5/self.PLAY_RATE, scaleUpPoint, MovieUtil.PNT3_NEARZERO),
            Wait(pickupDelay),
            Func(receiver.wrtReparentTo, self.invoker.getRightHand()),
            LerpScaleInterval(receiver, 0.01, receiverAdjustScale),
            LerpPosHprInterval(
                receiver,
                0.0001,
                Point3(-0.53, 0.21, -0.54),
                VBase3(-99.49, -35.27, 1.84),
            ),
            Wait(dialDuration),
            Func(receiver.wrtReparentTo, phone),
            Func(receiver.setPosHpr, 0, 0, 0, 0, 0, 0),
            Wait(finalPhoneDelay),
            LerpScaleInterval(phone, 0.5 / self.PLAY_RATE, MovieUtil.PNT3_NEARZERO),
            Func(MovieUtil.removeProps, [receiver, phone]),
        )
        toonTrack = self.getToonTrack(3.7/self.PLAY_RATE, ["slip-backward"], 3.1/self.PLAY_RATE, ["jump"], damageAnimPlayRate=1.15)
        soundTrack = self.getSoundTrack("SA_hangup.ogg", delay=0.5/self.PLAY_RATE, node=self.invoker, playRate=1.1, duration=2.5)
        soundTrack2 = self.getSoundTrack("SA_hangup.ogg", delay=3.5/self.PLAY_RATE, node=self.invoker, playRate=1.1, startTime=3.0)
        return Parallel(suitTrack, toonTrack, propTrack, soundTrack, soundTrack2)


@AttackClass(attackType=AttackEnum.HEAD_SHRINK)
class HeadShrink(SuitSingleAttack):
    ANIM_NAME = "magic1"
    PLAY_RATE = 1.3
    OPEN_SHOT_DUR = 1.3/PLAY_RATE

    def doAttack(self):
        target = self.targetDicts[0]
        toon = target["avatar"]
        dmg = target["hp"]
        damageDelay = 2.1/self.PLAY_RATE
        dodgeDelay = 1.4/self.PLAY_RATE
        shrinkSpray = BattleParticles.createParticleEffect(file="headShrinkSpray")
        shrinkCloud = BattleParticles.createParticleEffect(file="headShrinkCloud")
        shrinkDrop = BattleParticles.createParticleEffect(file="headShrinkDrop")
        suitTrack = self.getSuitTrack()
        sprayTrack = self.getPartTrack(
            shrinkSpray, 0.3/self.PLAY_RATE, 1.4/self.PLAY_RATE, [shrinkSpray, self.invoker, 0]
        )
        shrinkCloud.reparentTo(self.battle)
        adjust = 0.4
        x = toon.getX(self.battle)
        y = toon.getY(self.battle) - adjust
        z = 8
        shrinkCloud.setPos(Point3(x, y, z))
        shrinkDrop.setPos(Point3(0, 0 - adjust, 7.5))
        off = 0.7
        cloudPoints = [
            Point3(x + off, y, z),
            Point3(x + off / 2, y + off / 2, z),
            Point3(x, y + off, z),
            Point3(x - off / 2, y + off / 2, z),
            Point3(x - off, y, z),
            Point3(x - off / 2, y - off / 2, z),
            Point3(x, y - off, z),
            Point3(x + off / 2, y - off / 2, z),
            Point3(x + off, y, z),
            Point3(x, y, z),
        ]
        circleTrack = Sequence()
        for point in cloudPoints:
            circleTrack.append(
                LerpPosInterval(shrinkCloud, 0.14/self.PLAY_RATE, point, other=self.battle)
            )

        cloudTrack = Sequence()
        cloudTrack.append(Wait(1.42/self.PLAY_RATE))
        cloudTrack.append(
            Func(self.battle.movie.needRestoreParticleEffect, shrinkCloud)
        )
        cloudTrack.append(Func(shrinkCloud.start, self.battle))
        cloudTrack.append(circleTrack)
        cloudTrack.append(circleTrack)
        cloudTrack.append(
            LerpFunctionInterval(
                shrinkCloud.setAlphaScale, fromData=1, toData=0, duration=0.7/self.PLAY_RATE
            )
        )
        cloudTrack.append(Func(shrinkCloud.cleanup))
        cloudTrack.append(
            Func(self.battle.movie.clearRestoreParticleEffect, shrinkCloud)
        )
        shrinkDelay = 0.8/self.PLAY_RATE
        shrinkDuration = 1.1/self.PLAY_RATE
        shrinkTrack = Sequence()
        if target["landed"]:
            headParts = toon.getHeadParts()
            initialScale = headParts[0].getScale()[0]
            shrinkTrack.append(Wait(damageDelay + shrinkDelay))

            def scaleHeadParallel(scale, duration, headParts=headParts):
                headTracks = Parallel()
                for nextPart in headParts:
                    headTracks.append(
                        LerpScaleInterval(
                            nextPart, duration, Point3(scale, scale, scale)
                        )
                    )

                return headTracks

            shrinkTrack.append(Func(self.battle.movie.needRestoreHeadScale))
            shrinkTrack.append(scaleHeadParallel(0.6, shrinkDuration))
            shrinkTrack.append(Wait(0.3/self.PLAY_RATE))
            shrinkTrack.append(scaleHeadParallel(initialScale * 3.2, 0.4/self.PLAY_RATE))
            shrinkTrack.append(scaleHeadParallel(initialScale * 0.7, 0.4/self.PLAY_RATE))
            shrinkTrack.append(scaleHeadParallel(initialScale * 2.5, 0.3/self.PLAY_RATE))
            shrinkTrack.append(scaleHeadParallel(initialScale * 0.8, 0.3/self.PLAY_RATE))
            shrinkTrack.append(scaleHeadParallel(initialScale * 1.9, 0.2/self.PLAY_RATE))
            shrinkTrack.append(scaleHeadParallel(initialScale * 0.85, 0.2/self.PLAY_RATE))
            shrinkTrack.append(scaleHeadParallel(initialScale * 1.7, 0.15/self.PLAY_RATE))
            shrinkTrack.append(scaleHeadParallel(initialScale * 0.9, 0.15/self.PLAY_RATE))
            shrinkTrack.append(scaleHeadParallel(initialScale * 1.3, 0.1/self.PLAY_RATE))
            shrinkTrack.append(scaleHeadParallel(initialScale, 0.1/self.PLAY_RATE))
            shrinkTrack.append(Func(self.battle.movie.clearRestoreHeadScale))
            shrinkTrack.append(Wait(0.7/self.PLAY_RATE))
        dropTrack = self.getPartTrack(shrinkDrop, 1.5/self.PLAY_RATE, 2.5/self.PLAY_RATE, [shrinkDrop, toon, 0])
        damageAnims = []
        damageAnims.append(["cringe", 0.01, 0.65, 0.2])
        damageAnims.append(["cringe", 0.01, 0.85, 0.6])
        damageAnims.append(["cringe", 0.4, 1.49, 0.5])
        damageAnims.append({AAK.Anim: "slip-backward", AAK.PlayRate: 1.25})
        toonTrack = self.getToonTrack(
            damageDelay=damageDelay,
            splicedDamageAnims=damageAnims,
            dodgeDelay=dodgeDelay,
            dodgeAnimNames=["sidestep"],
            dodgeAnimPlayRate=1.2,
        )
        if target["landed"]:
            soundTrack = Parallel(
                self.getSoundTrack("SA_head_shrink_only.ogg", delay=2.1/self.PLAY_RATE, node=self.invoker),
                self.getSoundTrack("SA_head_grow_back_only.ogg", delay=4.0/self.PLAY_RATE, node=self.invoker, playRate=1.05),
            )
            return Parallel(
                suitTrack,
                sprayTrack,
                cloudTrack,
                dropTrack,
                toonTrack,
                shrinkTrack,
                soundTrack,
            )
        else:
            return Parallel(suitTrack, sprayTrack, cloudTrack, dropTrack, toonTrack)


@AttackClass(attackType=AttackEnum.HOT_AIR)
class HotAir(SuitSingleAttack):
    ANIM_NAME = "speak"
    PLAY_RATE = 1.25
    OPEN_SHOT_DUR = 2/PLAY_RATE

    def doAttack(self):
        target = self.targetDicts[0]
        toon = target["avatar"]
        BattleParticles.loadParticles()
        sprayEffect = BattleParticles.createParticleEffect("HotAir")
        baseFlameEffect = BattleParticles.createParticleEffect(file="firedBaseFlame")
        flameEffect = BattleParticles.createParticleEffect("FiredFlame")
        flecksEffect = BattleParticles.createParticleEffect("SpriteFiredFlecks")
        BattleParticles.setEffectTexture(sprayEffect, "fire")
        BattleParticles.setEffectTexture(baseFlameEffect, "fire")
        BattleParticles.setEffectTexture(flameEffect, "fire")
        BattleParticles.setEffectTexture(
            flecksEffect, "roll-o-dex", color=Vec4(0.95, 0.95, 0.0, 1)
        )
        sprayDelay = 0.9/self.PLAY_RATE
        flameDelay = 2.9/1.4
        flameDuration = 4.4/self.PLAY_RATE
        flecksDelay = flameDelay + (0.8/self.PLAY_RATE)
        flecksDuration = flameDuration - (2/self.PLAY_RATE)
        damageDelay = 2.5/self.PLAY_RATE
        dodgeDelay = 1.5/self.PLAY_RATE
        suitTrack = self.getSuitTrack(playRate=1.4)
        sprayNode = self.battle.attachNewNode('spray-node')
        sprayNode.setPos(self.battle.getActorPosHpr(self.invoker)[0])
        sprayNode.headsUp(toon)
        sprayTrack = Sequence(
            self.getPartTrack(
                sprayEffect, sprayDelay, 3.5/self.PLAY_RATE, [sprayEffect, sprayNode, 0], softStop=-1.5
            ),
            Func(sprayNode.removeNode),
        )
        baseFlameTrack = self.getPartTrack(
            baseFlameEffect, flameDelay, flameDuration, [baseFlameEffect, toon, 0], softStop=-1.0
        )
        flameTrack = self.getPartTrack(
            flameEffect, flameDelay, flameDuration, [flameEffect, toon, 0], softStop=-1.0
        )
        flecksTrack = self.getPartTrack(
            flecksEffect, flecksDelay, flecksDuration, [flecksEffect, toon, 0]
        )

        if self.invoker.dna.name in ("foreman", "ftf_s", "msfore"):
            sprayNode.setY(sprayNode.getY() - 1)
            sprayNode.setZ(sprayNode.getZ() + 2)
        elif self.invoker.dna.name == "fires":
            sprayNode.setY(sprayNode.getY() - 1)
            sprayNode.setZ(sprayNode.getZ() + 1)
        elif self.invoker.dna.name == "whunter":
            sprayNode.setY(sprayNode.getY() - 0.8)
            sprayNode.setZ(sprayNode.getZ() + 1.5)
        elif self.invoker.dna.name == "mplayer":
            sprayNode.setY(sprayNode.getY() - 1)
            sprayNode.setZ(sprayNode.getZ() + 1.6)

        def changeColor(parts):
            track = Parallel()
            for nextPart in parts:
                track.append(Func(nextPart.setColorScale, Vec4(0, 0, 0, 1)))

            return track

        def resetColor(parts):
            track = Parallel()
            for nextPart in parts:
                track.append(Func(nextPart.clearColorScale))

            return track

        if target["landed"]:
            headParts = toon.getHeadParts()
            torsoParts = toon.getTorsoParts()
            legsParts = toon.getLegsParts()
            colorTrack = Sequence()
            colorTrack.append(Wait(3.0/self.PLAY_RATE))
            colorTrack.append(Func(self.battle.movie.needRestoreColor))
            colorTrack.append(changeColor(headParts))
            colorTrack.append(changeColor(torsoParts))
            colorTrack.append(changeColor(legsParts))
            colorTrack.append(Wait(2.6/self.PLAY_RATE))
            colorTrack.append(resetColor(headParts))
            colorTrack.append(resetColor(torsoParts))
            colorTrack.append(resetColor(legsParts))
            colorTrack.append(Func(self.battle.movie.clearRestoreColor))
        damageAnims = []
        damageAnims.append(["cringe", 0.01, 0.7, 0.62])
        damageAnims.append(["slip-forward", 0.01, 0.4, 1.2])
        damageAnims.append(["slip-forward", 0.01, 1.0])
        toonTrack = self.getToonTrack(
            damageDelay=damageDelay,
            splicedDamageAnims=damageAnims,
            dodgeDelay=dodgeDelay,
            dodgeAnimNames=["sidestep"],
            damageAnimPlayRate=1.2,
            dodgeAnimPlayRate=1.2,
        )
        soundTrack = self.getSoundTrack("SA_hot_air.ogg", delay=0.85/self.PLAY_RATE, node=self.invoker)
        if target["landed"]:
            return Parallel(
                suitTrack,
                toonTrack,
                sprayTrack,
                soundTrack,
                baseFlameTrack,
                flameTrack,
                flecksTrack,
                colorTrack,
            )
        else:
            return Parallel(suitTrack, toonTrack, sprayTrack, soundTrack)


@AttackClass(attackType=AttackEnum.JARGON)
class Jargon(SuitSingleAttack):
    ANIM_NAME = "speak"
    PLAY_RATE = 1.5
    OPEN_SHOT_DUR = 3.5/PLAY_RATE

    def doAttack(self):
        target = self.targetDicts[0]
        toon = target["avatar"]
        BattleParticles.loadParticles()
        particleEffect = BattleParticles.createParticleEffect(file="jargonSpray")
        particleEffect2 = BattleParticles.createParticleEffect(file="jargonSpray")
        particleEffect3 = BattleParticles.createParticleEffect(file="jargonSpray")
        particleEffect4 = BattleParticles.createParticleEffect(file="jargonSpray")
        BattleParticles.setEffectTexture(
            particleEffect, "jargon-brow", color=Vec4(1, 0, 0, 1)
        )
        BattleParticles.setEffectTexture(
            particleEffect2, "jargon-deep", color=Vec4(0, 0, 0, 1)
        )
        BattleParticles.setEffectTexture(
            particleEffect3, "jargon-hoop", color=Vec4(1, 0, 0, 1)
        )
        BattleParticles.setEffectTexture(
            particleEffect4, "jargon-ipo", color=Vec4(0, 0, 0, 1)
        )
        damageDelay = 3.8/self.PLAY_RATE
        dodgeDelay = 1.9/self.PLAY_RATE
        partDelay = 3.5/self.PLAY_RATE
        partInterval = 0.6/self.PLAY_RATE
        suitTrack = self.getSuitTrack(playRate=self.PLAY_RATE)
        particleNode = self.battle.attachNewNode('jargon-particle-node')
        particleNode.setPos(self.battle.getActorPosHpr(self.invoker)[0])
        particleNode.headsUp(toon)

        if self.invoker.dna.name == "le":
            particleNode.setZ(particleNode.getZ() + 2)
            particleNode.setP(particleNode.getP() - 15)
        elif self.invoker.dna.name == "stenog":
            particleNode.setZ(particleNode.getZ() + 4)
            particleNode.setP(particleNode.getP() - 23)

        partTrack = self.getPartTrack(
            particleEffect,
            partDelay + partInterval * 0,
            2.0/self.PLAY_RATE,
            [particleEffect, particleNode, 0],
            softStop=-1.0,
        )
        partTrack2 = self.getPartTrack(
            particleEffect2,
            partDelay + partInterval * 1,
            2.0/self.PLAY_RATE,
            [particleEffect2, particleNode, 0],
            softStop=-1.0,
        )
        partTrack3 = self.getPartTrack(
            particleEffect3,
            partDelay + partInterval * 2,
            2.0/self.PLAY_RATE,
            [particleEffect3, particleNode, 0],
            softStop=-1.0,
        )
        partTrack4 = Sequence(
            self.getPartTrack(
                particleEffect4,
                partDelay + partInterval * 3,
                1.5/self.PLAY_RATE,
                [particleEffect4, particleNode, 0],
                softStop=-1.0,
            ),
            Func(particleNode.removeNode),
        )
        damageAnims = [["conked", 0.01, 0.01, 0.9], ["conked", 0.01, 1.5]]
        dodgeAnims = [["duck"]]
        toonTrack = self.getToonTrack(
            damageDelay=damageDelay,
            splicedDamageAnims=damageAnims,
            dodgeDelay=dodgeDelay,
            splicedDodgeAnims=dodgeAnims,
            showMissedExtraTime=1.6,
            showDamageExtraTime=0.3,
            damageAnimPlayRate=1.1,
            dodgeAnimPlayRate=1.3,
        )
        soundTrack = self.getSoundTrack("SA_jargon.ogg", delay=3.4/self.PLAY_RATE, node=self.invoker)
        return Parallel(
            suitTrack,
            toonTrack,
            soundTrack,
            partTrack,
            partTrack2,
            partTrack3,
            partTrack4,
        )


@AttackClass(attackType=AttackEnum.LEGALESE)
class Legalese(SuitSingleAttack):
    ANIM_NAME = "speak"
    PLAY_RATE = 1.5
    OPEN_SHOT_DUR = 3.0/PLAY_RATE

    def doAttack(self):
        target = self.targetDicts[0]
        toon = target["avatar"]
        BattleParticles.loadParticles()
        sprayEffect1 = BattleParticles.createParticleEffect(file="legaleseSpray")
        sprayEffect2 = BattleParticles.createParticleEffect(file="legaleseSpray")
        sprayEffect3 = BattleParticles.createParticleEffect(file="legaleseSpray")
        sprayEffect4 = BattleParticles.createParticleEffect(file="legaleseSpray")
        sprayEffect5 = BattleParticles.createParticleEffect(file="legaleseSpray")
        sprayEffect6 = BattleParticles.createParticleEffect(file="legaleseSpray")
        color = Vec4(0.4, 0, 0, 1)
        BattleParticles.setEffectTexture(sprayEffect1, "legalese-hc", color=color)
        BattleParticles.setEffectTexture(sprayEffect2, "legalese-qpq", color=color)
        BattleParticles.setEffectTexture(sprayEffect3, "legalese-vd", color=color)
        BattleParticles.setEffectTexture(sprayEffect4, "legalese-hc", color=color)
        BattleParticles.setEffectTexture(sprayEffect5, "legalese-qpq", color=color)
        BattleParticles.setEffectTexture(sprayEffect6, "legalese-vd", color=color)
        partDelay = 3.5/self.PLAY_RATE
        partDuration = 1.5/self.PLAY_RATE
        damageDelay = 4.0/self.PLAY_RATE
        dodgeDelay = 2.7/self.PLAY_RATE
        suitTrack = self.getSuitTrack(playRate=self.PLAY_RATE)
        sprayNode = self.battle.attachNewNode('spray-node')
        sprayNode.setPos(self.battle.getActorPosHpr(self.invoker)[0])
        sprayNode.headsUp(toon)
        sprayNode.setBin('fixed', 1)

        if self.invoker.dna.name == "le":
            sprayNode.setZ(sprayNode.getZ() + 3.0)
            sprayNode.setP(sprayNode.getP() - 10)

        sprayTrack1 = self.getPartTrack(
            sprayEffect1, partDelay, partDuration, [sprayEffect1, sprayNode, 0]
        )
        sprayTrack2 = self.getPartTrack(
            sprayEffect2, partDelay + 0.4, partDuration, [sprayEffect2, sprayNode, 0]
        )
        sprayTrack3 = self.getPartTrack(
            sprayEffect3, partDelay + 0.8, partDuration, [sprayEffect3, sprayNode, 0]
        )
        sprayTrack4 = self.getPartTrack(
            sprayEffect4, partDelay + 1.2, partDuration, [sprayEffect4, sprayNode, 0]
        )
        sprayTrack5 = Sequence(
            self.getPartTrack(
                sprayEffect6, partDelay + 1.6, partDuration, [sprayEffect5, sprayNode, 0]
            ),
            Func(sprayNode.removeNode),
        )
        damageAnims = [
            ["cringe", 1e-05, 0.3, 0.8],
            ["cringe", 1e-05, 0.3]
        ]
        toonTrack = self.getToonTrack(
            damageDelay=damageDelay,
            splicedDamageAnims=damageAnims,
            dodgeDelay=dodgeDelay,
            dodgeAnimNames=["duck"],
            showMissedExtraTime=0.8,
            dodgeAnimPlayRate=1.1,
        )
        soundTrack = self.getSoundTrack("SA_jargon.ogg", delay=3.4/self.PLAY_RATE, node=self.invoker)
        return Parallel(
            suitTrack, toonTrack, soundTrack, sprayTrack1, sprayTrack2, sprayTrack3, sprayTrack4, sprayTrack5
        )


@AttackClass(attackType=AttackEnum.LIQUIDATE)
class Liquidate(SuitSingleAttack):
    ANIM_NAME = "magic1"
    OPEN_SHOT_DUR = 2.0

    def doAttack(self):
        target = self.targetDicts[0]
        toon = target["avatar"]
        BattleParticles.loadParticles()
        particleKwargs = self.getParticleKwargs()
        rainEffect = BattleParticles.createParticleEffect(**particleKwargs)
        rainEffect2 = BattleParticles.createParticleEffect(**particleKwargs)
        rainEffect3 = BattleParticles.createParticleEffect(**particleKwargs)
        self.processEffects(rainEffect, rainEffect2, rainEffect3)
        cloud = globalPropPool.getProp("stormcloud")
        damageDelay = 3.0
        dodgeDelay = 1.6
        suitTrack = self.getSuitTrack(delay=self.getSuitDelay(), playRate=self.getSuitPlayRate())
        initialCloudHeight = self.invoker.height + 3
        cloudPosPoints = [Point3(0, 3, initialCloudHeight), VBase3(180, 0, 0)]
        targetPoint = self.toonFacePoint(toon)
        targetPoint.setZ(targetPoint[2] + 3)
        cloudPropTrack = Parallel(
            Func(cloud.pose, "stormcloud", 0),
            self.getPropAppearTrack(
                cloud,
                self.invoker,
                cloudPosPoints,
                1e-06,
                Point3(3, 3, 3),
                scaleUpTime=0.7,
                blendType='easeOut',
            ),
            Func(self.battle.movie.needRestoreRenderProp, cloud),
            Func(cloud.wrtReparentTo, render),
            Sequence(
                Wait(1.5),
                LerpPosInterval(cloud, 0.7, pos=targetPoint, blendType='easeInOut'),
            ),
            Sequence(
                Wait(2.0),
                Parallel(
                    Sequence(
                        ParticleInterval(
                            rainEffect, cloud, worldRelative=0, duration=2.4, cleanup=True, softStopT=self.getParticleSoftStop(),
                        )
                    ),
                    Sequence(
                        Wait(0.1),
                        ParticleInterval(
                            rainEffect2, cloud, worldRelative=0, duration=2.3, cleanup=True, softStopT=self.getParticleSoftStop(),
                        ),
                    ),
                    Sequence(
                        Wait(0.1),
                        ParticleInterval(
                            rainEffect3, cloud, worldRelative=0, duration=2.3, cleanup=True, softStopT=self.getParticleSoftStop(),
                        ),
                    ),
                    Sequence(
                        ActorInterval(cloud, "stormcloud", startTime=3, duration=0.1),
                        ActorInterval(cloud, "stormcloud", startTime=1, duration=2.2),
                    ),
                )
            ),
            Sequence(
                Wait(self.getCloudVanishWait()),
                Parallel(
                    LerpScaleInterval(cloud, 0.45, MovieUtil.PNT3_NEARZERO, blendType='easeIn'),
                    Sequence(
                        LerpPosInterval(cloud, 0.45 / 2.0, pos=targetPoint + Vec3(0, 0, -0.5), blendType='easeOut'),
                        LerpPosInterval(cloud, 0.45 / 2.0, pos=targetPoint + Vec3(0, 0, 1), blendType='easeIn'),
                    ),
                ),
                Func(MovieUtil.removeProp, cloud),
                Func(self.battle.movie.clearRenderProp, cloud),
            )
        )

        toonTrack = Parallel(
            self.getToonTrack(
                damageDelay=damageDelay,
                splicedDamageAnims=[],
                dodgeDelay=dodgeDelay,
                dodgeAnimNames=['sidestep'],
                dodgeAnimPlayRate=1.05,
            )
        )

        if target['landed']:
            if self.toonMelts():
                toonTrack.append(Sequence(
                    Wait(2.0),
                    ActorInterval(toon, 'melt', playRate=1.1),
                    Wait(0.7),
                    ActorInterval(toon, 'jump', startTime=0.4, playRate=1.15),
                    Func(toon.loop, 'neutral'),
                ))
            else:
                toonTrack.append(Sequence(
                    ActorInterval(toon, 'cringe', playRate=1.3),
                    Func(toon.loop, 'neutral'),
                ))

        soundTrack = self.getSoundTrack(
            self.getSfxName(), delay=1.5, node=self.invoker, playRate=1.1,
        )
        if target["landed"] and self.hasQuicksand():
            puddle = globalPropPool.getProp("quicksand")
            puddle.setColor(self.getQuicksandColor())
            puddle.setHpr(Point3(120, 0, 0))
            puddle.setScale(0.01)
            puddleTrack = Sequence(
                Func(self.battle.movie.needRestoreRenderProp, puddle),
                Wait(damageDelay - 0.7),
                Func(puddle.reparentTo, self.battle),
                Func(puddle.setPos, toon.getPos(self.battle)),
                LerpScaleInterval(
                    puddle,
                    1.4,
                    Point3(1.7, 1.7, 1.7),
                    startScale=MovieUtil.PNT3_NEARZERO,
                ),
                Wait(1.3),
                LerpFunctionInterval(
                    puddle.setAlphaScale, fromData=1, toData=0, duration=0.35, blendType='easeIn',
                ),
                Func(MovieUtil.removeProp, puddle),
                Func(self.battle.movie.clearRenderProp, puddle),
            )
            return Parallel(
                suitTrack, toonTrack, cloudPropTrack, soundTrack, puddleTrack
            )
        else:
            return Parallel(suitTrack, toonTrack, cloudPropTrack, soundTrack)

    def getCameraShot(self, duration):
        if not self.targetDicts:
            toon = self.invoker
        else:
            toon = self.targetDicts[0]["avatar"]
        return self.camera.randomSplitShot(self.invoker, toon, self.battle, duration)

    """
    Movie Consts
    """

    def getParticleName(self) -> str:
        return "liquidate"

    def getQuicksandColor(self) -> Vec4:
        return Vec4(0.1, 0.1, 1.0, 1)

    def hasQuicksand(self) -> bool:
        return True

    def getSfxName(self) -> str:
        return "SA_liquidate.ogg"

    def toonMelts(self) -> bool:
        return True

    def processEffects(self, *vfx) -> None:
        pass

    def getParticleKwargs(self) -> dict:
        return {'file': self.getParticleName()}

    def getSuitPlayRate(self) -> float:
        return 1.3

    def getSuitDelay(self) -> float:
        return 0.9

    def getCloudVanishWait(self) -> float:
        return 4.2

    def getParticleSoftStop(self) -> float:
        return -0.5


@AttackClass(attackType=AttackEnum.MARKET_CRASH)
class MarketCrash(SuitSingleAttack):
    ANIM_NAME = "throw-object"
    PLAY_RATE = 1.3
    OPEN_SHOT_DUR = 2.7/PLAY_RATE

    DelayInfo = {
        'b': [2.03, 0.8, 1.5],
        'c': [2.03, 0.8, 1.5],
    }

    def doAttack(self):
        target = self.targetDicts[0]
        toon = target["avatar"]
        delayDict = self.DelayInfo[self.invoker.style.body]
        suitDelay = delayDict[0]/self.PLAY_RATE
        propDelay = delayDict[1]/self.PLAY_RATE
        throwDuration = delayDict[2]/self.PLAY_RATE
        paper = globalPropPool.getProp("newspaper")
        suitTrack = self.getSuitTrack(playRate=self.PLAY_RATE)
        posPoints = [Point3(0.1, -0.7, -0.0), VBase3(-180, 90, 90)]
        paperTrack = Sequence(
            self.getPropAppearTrack(
                paper,
                self.invoker.getRightHand(),
                posPoints,
                propDelay,
                Point3(3, 3, 3),
                scaleUpTime=0.2,
            )
        )
        paperTrack.append(Wait(suitDelay))
        hitPoint = toon.getPos(self.battle)
        hitPoint.setX(hitPoint.getX() + 1.2)
        hitPoint.setY(hitPoint.getY() + 1.5)
        if target["landed"]:
            hitPoint.setZ(hitPoint.getZ() + 1.1)
        movePoint = Point3(
            hitPoint.getX(), hitPoint.getY() - 1.8, hitPoint.getZ() + 0.2
        )
        paperTrack.append(Func(self.battle.movie.needRestoreRenderProp, paper))
        paperTrack.append(Func(paper.wrtReparentTo, self.battle))
        paperTrack.append(
            self.getThrowTrack(
                paper, hitPoint, duration=throwDuration, parent=self.battle, gravity=-50,
            )
        )
        paperTrack.append(Wait(0.6/self.PLAY_RATE))
        paperTrack.append(LerpPosInterval(paper, 0.4/self.PLAY_RATE, movePoint))
        spinTrack = Sequence(
            Wait(propDelay + suitDelay + (0.2/self.PLAY_RATE)),
            LerpHprInterval(paper, throwDuration, Point3(-360, 0, 0)),
        )
        sizeTrack = Sequence(
            Wait(propDelay + suitDelay + (0.2/self.PLAY_RATE)),
            LerpScaleInterval(paper, throwDuration, Point3(6, 6, 6)),
            Wait(0.95/self.PLAY_RATE),
            LerpScaleInterval(paper, 0.4/self.PLAY_RATE, MovieUtil.PNT3_NEARZERO),
        )
        propTrack = Sequence(
            Parallel(paperTrack, spinTrack, sizeTrack),
            Func(MovieUtil.removeProp, paper),
            Func(self.battle.movie.clearRenderProp, paper),
        )
        damageAnims = []
        damageAnims.extend(
            self.getSplicedLerpAnims("slip-forward", 0.31, 0.95, startTime=1.2)
        )
        damageAnims.append(["slip-forward", 0.01, 1.51])
        toonTrack = self.getToonTrack(
            damageDelay=3.42,
            splicedDamageAnims=damageAnims,
            dodgeDelay=2.47,
            dodgeAnimNames=["sidestep"],
            showDamageExtraTime=0.4,
            showMissedExtraTime=1.3,
            dodgeAnimPlayRate=1.2,
        )
        soundTrack = self.getSoundTrack("SA_market_crash.ogg", node=self.invoker, delay=0.17)
        return Parallel(suitTrack, toonTrack, propTrack, soundTrack)


@AttackClass(attackType=AttackEnum.MUMBO_JUMBO)
class MumboJumbo(SuitSingleAttack):
    ANIM_NAME = "speak"
    PLAY_RATE = 1.4
    OPEN_SHOT_DUR = 3/PLAY_RATE

    def doAttack(self):
        target = self.targetDicts[0]
        toon = target["avatar"]
        BattleParticles.loadParticles()
        particleEffect = BattleParticles.createParticleEffect(file="mumboJumboSpray")
        particleEffect2 = BattleParticles.createParticleEffect(file="mumboJumboSpray")
        particleEffect3 = BattleParticles.createParticleEffect(file="mumboJumboSmother")
        particleEffect4 = BattleParticles.createParticleEffect(file="mumboJumboSmother")
        particleEffect5 = BattleParticles.createParticleEffect(file="mumboJumboSmother")
        BattleParticles.setEffectTexture(
            particleEffect, "mumbojumbo-boiler", color=Vec4(1, 0, 0, 1)
        )
        BattleParticles.setEffectTexture(
            particleEffect2, "mumbojumbo-creative", color=Vec4(1, 0, 0, 1)
        )
        BattleParticles.setEffectTexture(
            particleEffect3, "mumbojumbo-deben", color=Vec4(1, 0, 0, 1)
        )
        BattleParticles.setEffectTexture(
            particleEffect4, "mumbojumbo-high", color=Vec4(1, 0, 0, 1)
        )
        BattleParticles.setEffectTexture(
            particleEffect5, "mumbojumbo-iron", color=Vec4(1, 0, 0, 1)
        )
        suitTrack = self.getSuitTrack(playRate=self.PLAY_RATE)
        particleNode = self.battle.attachNewNode('mumbo-jumbo-particle-node')
        particleNode.setPos(self.battle.getActorPosHpr(self.invoker)[0])
        particleNode.headsUp(toon)
        particleNode.setBin('fixed', 1)
        partTrack = self.getPartTrack(
            particleEffect, 3.3/self.PLAY_RATE, 3/self.PLAY_RATE, [particleEffect, particleNode, 0], softStop=-1.0
        )
        partTrack2 = Sequence(
            self.getPartTrack(
                particleEffect2, 3.3/self.PLAY_RATE, 3/self.PLAY_RATE, [particleEffect2, particleNode, 0], softStop=-1.0
            ),
            Func(particleNode.removeNode),
        )

        if self.invoker.dna.name == "mi":
            particleNode.setZ(particleNode.getZ() + 2.25)
            particleNode.setP(particleNode.getP() - 15)
        elif self.invoker.dna.name == "stenog":
            particleNode.setZ(particleNode.getZ() + 4.1)
            particleNode.setP(particleNode.getP() - 25)

        partTrack3 = self.getPartTrack(
            particleEffect3, 4.1/self.PLAY_RATE, 2.7/self.PLAY_RATE, [particleEffect3, toon, 0], softStop=-1.0
        )
        partTrack4 = self.getPartTrack(
            particleEffect4, 4.1/self.PLAY_RATE, 2.7/self.PLAY_RATE, [particleEffect4, toon, 0], softStop=-1.0
        )
        partTrack5 = self.getPartTrack(
            particleEffect5, 4.1/self.PLAY_RATE, 2.7/self.PLAY_RATE, [particleEffect5, toon, 0], softStop=-1.0
        )
        toonTrack = self.getToonTrack(3.7/self.PLAY_RATE, ["cringe"], 3.15/self.PLAY_RATE, ["sidestep"], dodgeAnimPlayRate=1.22)
        soundTrack = self.getSoundTrack(
            "SA_mumbo_jumbo.ogg", delay=3.3/self.PLAY_RATE, node=self.invoker
        )
        if target["landed"]:
            return Parallel(
                suitTrack,
                toonTrack,
                soundTrack,
                partTrack,
                partTrack2,
                partTrack3,
                partTrack4,
                partTrack5,
            )
        else:
            return Parallel(suitTrack, toonTrack, soundTrack, partTrack, partTrack2)


@AttackClass(attackType=AttackEnum.PARADIGM_SHIFT)
class ParadigmShift(SuitGroupAttack):
    ANIM_NAME = "magic2"
    PLAY_RATE = 1.2
    OPEN_SHOT_DUR = 1.01

    def doAttack(self):
        hitAtleastOneToon = 0
        for t in self.targetDicts:
            if t["landed"]:
                hitAtleastOneToon = 1
                break

        damageDelay = 0.9
        dodgeDelay = 0.95
        sprayEffect = BattleParticles.createParticleEffect("ShiftSpray")
        if self.invoker.dna.name == "mi":
            sprayEffect.setPos(Point3(-5.2, 4.6, 2.7))
        elif self.invoker.dna.name == "sd":
            sprayEffect.setPos(Point3(-5.2, 4.6, 2.7))
        else:
            sprayEffect.setPos(Point3(0.1, 4.6, 2.7))
        suitTrack = self.getSuitAnimTrack(playRate=self.PLAY_RATE)
        sprayTrack = self.getPartTrack(
            sprayEffect, 1.0/self.PLAY_RATE, 1.9, [sprayEffect, self.invoker, 0]
        )
        liftTracks = Parallel()
        toonRiseTracks = Parallel()
        for t in self.targetDicts:
            toon = t["avatar"]
            if t["landed"]:
                liftEffect = BattleParticles.createParticleEffect("ShiftLift")
                liftEffect.setPos(toon.getPos(self.battle))
                liftEffect.setZ(liftEffect.getZ() - 1.3)
                liftTracks.append(
                    self.getPartTrack(
                        liftEffect, 1.1/self.PLAY_RATE, 4.1, [liftEffect, self.battle, 0]
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
                toonRiseTracks.append(Parallel(shakeTrack, shadowTrack))

        damageAnims = []
        damageAnims.extend(self.getSplicedLerpAnims("think", 0.66, 1.9, startTime=2.06))
        damageAnims.append(["slip-backward", 0.01, 0.5])
        dodgeAnims = []
        dodgeAnims.append(["jump", 0.01, 0, 0.6])
        dodgeAnims.extend(self.getSplicedLerpAnims("jump", 0.31, 1.0, startTime=0.6))
        dodgeAnims.append(["jump", 0, 0.91])
        toonTracks = self.getToonTracks(
            damageDelay=damageDelay,
            splicedDamageAnims=damageAnims,
            dodgeDelay=dodgeDelay,
            splicedDodgeAnims=dodgeAnims,
            showDamageExtraTime=2.7,
        )
        if hitAtleastOneToon == 1:
            soundTrack = self.getSoundTrack(
                "SA_paradigm_shift.ogg", delay=1.5/self.PLAY_RATE, node=self.invoker
            )
            return Parallel(
                suitTrack,
                sprayTrack,
                soundTrack,
                liftTracks,
                toonTracks,
                toonRiseTracks,
            )
        else:
            return Parallel(
                suitTrack, sprayTrack, liftTracks, toonTracks, toonRiseTracks
            )


@AttackClass(attackType=AttackEnum.PECKING_ORDER)
class PeckingOrder(SuitSingleAttack):
    ANIM_NAME = "throw-object"
    PLAY_RATE = 1.4
    OPEN_SHOT_DUR = 2.8/PLAY_RATE

    def doAttack(self):
        target = self.targetDicts[0]
        toon = target["avatar"]
        throwDelay = 3.2/self.PLAY_RATE
        damageDelay = 4.2/self.PLAY_RATE
        dodgeDelay = 2.8/self.PLAY_RATE
        suitTrack = self.getSuitTrack(playRate=self.PLAY_RATE)
        numBirds = random.randint(4, 7)
        birdTracks = Parallel()
        for i in range(0, numBirds):
            next = globalPropPool.getProp("bird")
            next.setScale(0.01)
            next.reparentTo(self.invoker.getRightHand())
            next.setPos(
                random.random() * 0.6 - 0.3,
                random.random() * 0.6 - 0.3,
                random.random() * 0.6 - 0.3,
            )
            if target["landed"]:
                hitPoint = Point3(
                    toon.getX(self.battle) + lerp(-2.5, 2.5, random.random()),
                    random.random() * 2 - 1 - 6,
                    random.random() * 3 - 1.5 + toon.getHeight() - 0.9,
                )
            else:
                hitPoint = Point3(
                    toon.getX(self.battle) + (random.random() * 2 - 1),
                    random.random() * 4 - 2 - 15,
                    random.random() * 4 - 2 + 2.2,
                )
            birdTrack = Sequence(
                Wait(throwDelay),
                Func(self.battle.movie.needRestoreRenderProp, next),
                Func(next.wrtReparentTo, self.battle),
                Func(next.setHpr, Point3(90, 20, 0)),
                LerpPosInterval(next, 1.1/self.PLAY_RATE, hitPoint),
            )
            scaleTrack = Sequence(
                Wait(throwDelay), LerpScaleInterval(next, 0.15/self.PLAY_RATE, Point3(9, 9, 9))
            )
            soundTrack = self.getSoundTrack(
                "tt_s_ara_cfg_eagleCry.ogg", delay=2.95/self.PLAY_RATE, node=self.invoker
            )
            removeProp = Sequence(
                Wait(damageDelay),
                LerpScaleInterval(next, 0.6/self.PLAY_RATE, 0.01, blendType="easeIn"),
                Func(MovieUtil.removeProp, next),
            )
            birdTracks.append(Parallel(birdTrack, scaleTrack, soundTrack, removeProp))

        damageAnims = [
            ["cringe", 0.01, 0.14, 0.21],
            ["cringe", 0.01, 0.14, 0.13],
            ["cringe", 0.01, 0.43]
        ]
        toonTrack = self.getToonTrack(
            damageDelay=damageDelay,
            splicedDamageAnims=damageAnims,
            dodgeDelay=dodgeDelay,
            dodgeAnimNames=["sidestep"],
            showMissedExtraTime=1.1,
            dodgeAnimPlayRate=1.2,
        )
        return Parallel(suitTrack, toonTrack, birdTracks)


@AttackClass(attackType=AttackEnum.PICK_POCKET)
class PickPocket(SuitSingleAttack):
    ANIM_NAME = "pickpocket"
    PropName = "1dollar"
    PropPosPoints = [Point3(-0.01, 0.45, -0.25), VBase3(136.424, -46.434, -129.712)]
    PropScaleUpPoint = Point3(1.41, 1.41, 1.41)
    PropAppearDelay = 0.6
    PropRemainDelay = 0.55
    PropScaleUpTime = 0.5
    PropScaleDownTime = 0.5

    def doAttack(self):
        target = self.targetDicts[0]
        bill = globalPropPool.getProp(self.PropName)
        suitTrack = self.getSuitTrack()
        billPosPoints = self.PropPosPoints[:]
        billPropTrack = self.getPropTrack(
            bill,
            self.invoker.getRightHand(),
            billPosPoints,
            self.PropAppearDelay,
            self.PropRemainDelay,
            scaleUpPoint=self.PropScaleUpPoint,
            scaleUpTime=self.PropScaleUpTime,
            scaleDownTime=self.PropScaleDownTime,
        )
        toonTrack = self.getToonTrack(0.34, ["cringe"], 0.01, ["sidestep"], dodgeAnimPlayRate=1.2)
        multiTrackList = Parallel(suitTrack, toonTrack)
        if target["landed"]:
            soundTrack = self.getSoundTrack(
                "SA_pick_pocket.ogg", delay=0.2, node=self.invoker
            )
            multiTrackList.append(billPropTrack)
            multiTrackList.append(soundTrack)
        return multiTrackList

    def getCameraShot(self, duration):
        return self.camera.allGroupLowShot(duration=2.7)


@AttackClass(attackType=AttackEnum.PENNY_PINCH)
class PennyPinch(PickPocket):
    PropName = "coin_bronze"
    PropPosPoints = [Point3(-0.2396, 0.3411, -0.5068), VBase3(30.215, 12.3896, -3.895)]
    PropScaleUpPoint = Point3(1.8, 1.8, 1.8)
    PropAppearDelay = 0.5
    PropRemainDelay = 1.0
    PropScaleUpTime = 0.2
    PropScaleDownTime = 0.5


@AttackClass(attackType=AttackEnum.PINK_SLIP)
class PinkSlip(SuitSingleAttack):
    ANIM_NAME = "throw-paper"
    PLAY_RATE = 1.2
    OPEN_SHOT_DUR = 2.8/PLAY_RATE

    def doAttack(self):
        target = self.targetDicts[0]
        toon = target["avatar"]
        paper = globalPropPool.getProp("pink-slip")
        throwDelay = 3.03/self.PLAY_RATE
        throwDuration = 0.5/self.PLAY_RATE
        suitTrack = self.getSuitTrack(playRate=self.PLAY_RATE)
        posPoints = [Point3(0.0, -0.4, -0.18), VBase3(-180, -0, -0)]
        paperAppearTrack = Sequence(
            self.getPropAppearTrack(
                paper,
                self.invoker.getRightHand(),
                posPoints,
                1.0/self.PLAY_RATE,
                Point3(8, 8, 8),
                scaleUpTime=0.2,
            )
        )
        paperAppearTrack.append(Wait(1.73/self.PLAY_RATE))
        hitPoint = self.toonGroundPoint(toon, 0.2, parent=self.battle)
        paperAppearTrack.append(Func(self.battle.movie.needRestoreRenderProp, paper))
        paperAppearTrack.append(Func(paper.wrtReparentTo, self.battle))
        paperAppearTrack.append(LerpPosInterval(paper, throwDuration, hitPoint))
        if target["landed"]:
            paperPause = 0.01
            slidePoint = Point3(
                hitPoint.getX(), hitPoint.getY() - 5, hitPoint.getZ() + 4
            )
            landPoint = Point3(hitPoint.getX(), hitPoint.getY() - 5, hitPoint.getZ())
            paperAppearTrack.append(Wait(paperPause))
            paperAppearTrack.append(LerpPosInterval(paper, 0.2/self.PLAY_RATE, slidePoint))
            paperAppearTrack.append(LerpPosInterval(paper, 1.1/self.PLAY_RATE, landPoint))
            paperSpinTrack = Sequence(
                Wait(throwDelay),
                LerpHprInterval(paper, throwDuration, VBase3(300, 0, 0)),
                Wait(paperPause),
                LerpHprInterval(paper, 1.3/self.PLAY_RATE, VBase3(-200, 100, 100)),
            )
        else:
            slidePoint = Point3(hitPoint.getX(), hitPoint.getY() - 5, hitPoint.getZ())
            paperAppearTrack.append(LerpPosInterval(paper, 0.5/self.PLAY_RATE, slidePoint))
            paperSpinTrack = Sequence(
                Wait(throwDelay),
                LerpHprInterval(paper, throwDuration, VBase3(300, 0, 0)),
                LerpHprInterval(paper, 0.5, VBase3(10, 0, 0)),
            )
        propTrack = Sequence()
        propTrack.append(Parallel(paperAppearTrack, paperSpinTrack))
        propTrack.append(LerpScaleInterval(paper, 0.4/self.PLAY_RATE, MovieUtil.PNT3_NEARZERO))
        propTrack.append(Func(MovieUtil.removeProp, paper))
        propTrack.append(Func(self.battle.movie.clearRenderProp, paper))
        damageAnims = [["jump", 0.01, 0.3, 0.7], ["slip-forward", 0.01]]
        toonTrack = self.getToonTrack(
            damageDelay=2.65/self.PLAY_RATE,
            splicedDamageAnims=damageAnims,
            dodgeDelay=2.8/self.PLAY_RATE,
            dodgeAnimNames=["jump"],
            showDamageExtraTime=0.9,
        )
        soundTrack = self.getSoundTrack(
            "SA_pink_slip.ogg", delay=2.9/self.PLAY_RATE, duration=1.1, node=self.invoker
        )
        return Parallel(suitTrack, toonTrack, propTrack, soundTrack)


@AttackClass(attackType=AttackEnum.PLAY_HARDBALL)
class PlayHardball(SuitSingleAttack):
    ANIM_NAME = "throw-object"
    PLAY_RATE = 1.3
    OPEN_SHOT_DUR = (70/24)/PLAY_RATE

    def doAttack(self):
        target = self.targetDicts[0]
        toon = target["avatar"]
        ball = globalPropPool.getProp("baseball")
        suitDelay = 1.79/self.PLAY_RATE
        damageDelay = 3.46/self.PLAY_RATE
        dodgeDelay = 2.56/self.PLAY_RATE
        suitTrack = self.getSuitTrack(playRate=self.PLAY_RATE)
        ballPosPoints = [Point3(-0.24, -0.13, -0.21), VBase3(-1.152, 86.581, -76.784)]
        propTrack = Sequence(
            self.getPropAppearTrack(
                ball,
                self.invoker.getRightHand(),
                ballPosPoints,
                0.8/self.PLAY_RATE,
                Point3(5, 5, 5),
                scaleUpTime=0.5/self.PLAY_RATE,
            )
        )
        propTrack.append(Wait(suitDelay))
        propTrack.append(Func(self.battle.movie.needRestoreRenderProp, ball))
        propTrack.append(Func(ball.wrtReparentTo, self.battle))
        toonPos = toon.getPos(self.battle)
        x = toonPos.getX()
        y = toonPos.getY()
        z = toonPos.getZ()
        z = z + 0.2
        if target["landed"]:
            propTrack.append(
                LerpPosInterval(ball, 0.5/self.PLAY_RATE, self.toonFacePoint(toon, parent=self.battle))
            )
            propTrack.append(LerpPosInterval(ball, 0.5/self.PLAY_RATE, Point3(x, y + 3, z)))
            propTrack.append(LerpPosInterval(ball, 0.4/self.PLAY_RATE, Point3(x, y + 5, z + 2)))
            propTrack.append(LerpPosInterval(ball, 0.3/self.PLAY_RATE, Point3(x, y + 6, z)))
            propTrack.append(LerpPosInterval(ball, 0.1/self.PLAY_RATE, Point3(x, y + 7, z + 1)))
            propTrack.append(LerpPosInterval(ball, 0.1/self.PLAY_RATE, Point3(x, y + 8, z)))
            propTrack.append(LerpPosInterval(ball, 0.1/self.PLAY_RATE, Point3(x, y + 8.5, z + 0.6)))
            propTrack.append(LerpPosInterval(ball, 0.1/self.PLAY_RATE, Point3(x, y + 9, z + 0.2)))
            propTrack.append(Wait(0.4/self.PLAY_RATE))
            soundTrack = self.getSoundTrack(
                "SA_hardball_impact_only.ogg", delay=2.8/self.PLAY_RATE, node=self.invoker, playRate=1.05
            )
        else:
            propTrack.append(LerpPosInterval(ball, 0.5/self.PLAY_RATE, Point3(x, y + 2, z)))
            propTrack.append(LerpPosInterval(ball, 0.4/self.PLAY_RATE, Point3(x, y - 1, z + 2)))
            propTrack.append(LerpPosInterval(ball, 0.3/self.PLAY_RATE, Point3(x, y - 3, z)))
            propTrack.append(LerpPosInterval(ball, 0.1/self.PLAY_RATE, Point3(x, y - 4, z + 1)))
            propTrack.append(LerpPosInterval(ball, 0.1/self.PLAY_RATE, Point3(x, y - 5, z)))
            propTrack.append(LerpPosInterval(ball, 0.1/self.PLAY_RATE, Point3(x, y - 5.5, z + 0.6)))
            propTrack.append(LerpPosInterval(ball, 0.1/self.PLAY_RATE, Point3(x, y - 6, z + 0.2)))
            propTrack.append(Wait(0.4/self.PLAY_RATE))
            soundTrack = self.getSoundTrack(
                "SA_hardball.ogg", delay=3.1/self.PLAY_RATE, node=self.invoker
            )
        propTrack.append(LerpScaleInterval(ball, 0.3/self.PLAY_RATE, MovieUtil.PNT3_NEARZERO))
        propTrack.append(Func(MovieUtil.removeProp, ball))
        propTrack.append(Func(self.battle.movie.clearRenderProp, ball))
        damageAnims = [["conked", damageDelay, 0.01, 0.5], ["slip-backward", 0.01, 0.7]]
        toonTrack = self.getToonTrack(
            splicedDamageAnims=damageAnims,
            dodgeDelay=dodgeDelay,
            dodgeAnimNames=["sidestep"],
            showDamageExtraTime=3.9,
            dodgeAnimPlayRate=1.2,
        )
        return Parallel(suitTrack, toonTrack, propTrack, soundTrack)


@AttackClass(attackType=AttackEnum.POUND_KEY)
class PoundKey(SuitSingleAttack):
    ANIM_NAME = "phone"
    PLAY_RATE = 1.1
    OPEN_SHOT_DUR = (46/24)/PLAY_RATE

    def doAttack(self):
        target = self.targetDicts[0]
        toon = target["avatar"]
        phone = globalPropPool.getProp("phone")
        receiver = globalPropPool.getProp("receiver")
        BattleParticles.loadParticles()
        particleEffect = BattleParticles.createParticleEffect("PoundKey")
        BattleParticles.setEffectTexture(
            particleEffect, "poundsign", color=Vec4(0, 0, 0, 1)
        )
        suitTrack = self.getSuitTrack(playRate=self.PLAY_RATE)
        particleNode = self.battle.attachNewNode('pound-key-particle-node')
        particleNode.setPos(self.battle.getActorPosHpr(self.invoker)[0])
        particleNode.headsUp(toon)

        if self.invoker.dna.name == "stenog":
            particleNode.setZ(particleNode.getZ() + 3.5)
            particleNode.setP(particleNode.getP() - 15)
        elif self.invoker.dna.name in ("bellring", "mouthp"):
            particleNode.setZ(particleNode.getZ() + 1)
            particleNode.setP(particleNode.getP() - 5)

        partTrack = Sequence(
            self.getPartTrack(
                particleEffect, 1.6/self.PLAY_RATE, 2.55/self.PLAY_RATE, [particleEffect, particleNode, 0], softStop=-1.0
            ),
            Func(particleNode.removeNode),
        )
        phonePosPoints = [Point3(0.13, 0.27, -0.11), VBase3(5.939, 2.763, -177.591)]
        receiverPosPoints = [Point3(0.13, 0.27, -0.11), VBase3(5.939, 2.763, -177.591)]
        propTrack = Sequence(
            Wait(0.0),
            Func(
                self.showProp,
                phone,
                self.invoker.getLeftHand(),
                phonePosPoints[0],
                phonePosPoints[1],
            ),
            Func(
                self.showProp,
                receiver,
                self.invoker.getLeftHand(),
                receiverPosPoints[0],
                receiverPosPoints[1],
            ),
            LerpScaleInterval(phone, 1/self.PLAY_RATE, MovieUtil.PNT3_ONE, MovieUtil.PNT3_NEARZERO),
            Wait(0.0),
            Func(receiver.wrtReparentTo, self.invoker.getRightHand()),
            LerpPosHprInterval(
                receiver,
                0.0001,
                Point3(-0.45, 0.48, -0.62),
                VBase3(-87.47, -18.21, 7.82),
            ),
            Wait(2.6/self.PLAY_RATE),
            Func(receiver.wrtReparentTo, phone),
            Func(receiver.setPosHpr, 0, 0, 0, 0, 0, 0),
            Wait(0.55/self.PLAY_RATE),
            LerpScaleInterval(phone, 0.4/self.PLAY_RATE, MovieUtil.PNT3_NEARZERO),
            Func(MovieUtil.removeProps, [receiver, phone]),
        )
        toonTrack = self.getToonTrack(2.3/self.PLAY_RATE, ["cringe"], 1.8/self.PLAY_RATE, ["sidestep"], dodgeAnimPlayRate=1.2)
        soundTrack = self.getSoundTrack("SA_hangup.ogg", delay=0.61/self.PLAY_RATE, node=self.invoker, playRate=1.05)
        return Parallel(suitTrack, toonTrack, propTrack, partTrack, soundTrack)


@AttackClass(attackType=(AttackEnum.POWER_TIE, AttackEnum.MS_POWER_TIE))
class PowerTie(ClipOnTie):
    def getPropName(self):
        return "power-tie"

    def getPropActorName(self):
        return None

    def getPosPoints(self):
        return [Point3(0.6, -0.5, -0.3), VBase3(90, 90, -163.443)]

    def getPropScale(self):
        return Vec3(3.5, 3.5, 3.5)

    def getHitSound(self):
        return "SA_powertie_impact.ogg"

    def missH(self):
        return 180, 240


@AttackClass(attackType=AttackEnum.POWER_TRIP)
class PowerTrip(SuitGroupAttack):
    ANIM_NAME = "magic1"
    OPEN_SHOT_DUR = 0.9

    def doAttack(self):
        centerColor = Vec4(0.1, 0.1, 0.1, 0.4)
        edgeColor = Vec4(0.4, 0.1, 0.9, 0.7)
        powerBar1 = BattleParticles.createParticleEffect(file="powertrip")
        powerBar2 = BattleParticles.createParticleEffect(file="powertrip2")
        powerBar1.setPos(0, 6.1, 0.4)
        powerBar1.setHpr(-60, 0, 0)
        powerBar2.setPos(0, 6.1, 0.4)
        powerBar2.setHpr(60, 0, 0)
        powerBar1Particles = powerBar1.getParticlesNamed("particles-1")
        powerBar2Particles = powerBar2.getParticlesNamed("particles-1")
        powerBar1Particles.renderer.setCenterColor(centerColor)
        powerBar1Particles.renderer.setEdgeColor(edgeColor)
        powerBar2Particles.renderer.setCenterColor(centerColor)
        powerBar2Particles.renderer.setEdgeColor(edgeColor)
        waterfallEffect = BattleParticles.createParticleEffect("Waterfall")
        waterfallEffect.setScale(11)
        waterfallParticles = waterfallEffect.getParticlesNamed("particles-1")
        waterfallParticles.renderer.setCenterColor(centerColor)
        waterfallParticles.renderer.setEdgeColor(edgeColor)
        if self.invoker.dna.name == "mh":
            waterfallEffect.setPos(0, 4, 3.6)
        suitTrack = self.getSuitAnimTrack()

        def getPowerTrack(effect):
            partTrack = Sequence(
                Wait(0.4),
                Func(self.battle.movie.needRestoreParticleEffect, effect),
                Func(effect.start, self.invoker),
                Wait(0.35),
                LerpPosInterval(effect, 1.0, Point3(0, 15, 0.4), blendType='easeIn'),
                LerpFunctionInterval(
                    effect.setAlphaScale, fromData=1, toData=0, duration=0.4
                ),
                Func(effect.cleanup),
                Func(self.battle.movie.clearRestoreParticleEffect, effect),
            )
            return partTrack

        partTrack1 = getPowerTrack(powerBar1)
        partTrack2 = getPowerTrack(powerBar2)
        waterfallTrack = self.getPartTrack(
            waterfallEffect, 0.2, 1.3, [waterfallEffect, self.invoker, 0]
        )
        toonTracks = self.getToonTracks(1.45, ["slip-forward"], 0.89, ["jump"])
        soundTrack = self.getSoundTrack(
            "SA_powertrip.ogg", delay=0.9, node=self.invoker
        )
        return Parallel(
            suitTrack, partTrack1, partTrack2, soundTrack, waterfallTrack, toonTracks
        )


@AttackClass(attackType=(AttackEnum.QUAKE, AttackEnum.AFTERSHOCK))
class Quake(SuitGroupAttack):
    ANIM_NAME = "quick-jump"
    shakeIntensity = 1
    quake = 1

    def doAttack(self):
        suitTrack = self.getSuitAnimTrack()
        damageAnims = [["slip-forward"], {AAK.Anim: "slip-backward", AAK.PlayRate: 1.25}]
        dodgeAnims = [["jump"], ["jump", 0.01], ["jump", 0.01]]
        toonTracks = self.getToonTracks(
            damageDelay=1.7,
            splicedDamageAnims=damageAnims,
            dodgeDelay=1.1,
            splicedDodgeAnims=dodgeAnims,
            showMissedExtraTime=2.8,
            showDamageExtraTime=1.1,
        )
        soundTrack = self.getSoundTrack("SA_quake.ogg", delay=0, node=self.invoker, volume=0.9)
        return Parallel(suitTrack, soundTrack, toonTracks)

    def getCameraShot(self, duration):
        extraDelay = 0.0
        if self.shownUnlureMovie:
            extraDelay = 0.6
        return self.camera.suitCameraShakeShot(duration, self.shakeIntensity, self.quake, extraDelay=extraDelay)


@AttackClass(attackType=AttackEnum.RAZZLE_DAZZLE)
class RazzleDazzle(SuitSingleAttack):
    ANIM_NAME = "smile"
    OPEN_SHOT_DUR = 2.2

    def doAttack(self):
        target = self.targetDicts[0]
        toon = target["avatar"]
        dmg = target["hp"]
        suitB = getSuitBodyType(self.invoker.dna.name) == 'b'
        sign = globalPropPool.getProp("smile")
        BattleParticles.loadParticles()
        particleEffect = BattleParticles.createParticleEffect("Smile")
        suitTrack = self.getSuitTrack()
        signPosPoints = [Point3(0.0, -0.42, -0.04), VBase3(105.715, 73.977, 65.932)]
        if target["landed"]:
            hitPoint = lambda toon=toon: self.toonFacePoint(toon)
        else:
            hitPoint = (
                lambda particleEffect=particleEffect, toon=toon: self.toonMissPoint(
                    particleEffect, toon, parent=self.invoker.getRightHand()
                )
            )
        signPropTrack = Sequence(
            Wait(0.5),
            Func(
                self.showProp,
                sign,
                self.invoker.getRightHand(),
                signPosPoints[0],
                signPosPoints[1],
            ),
            LerpScaleInterval(sign, 0.5, Point3(1.39, 1.39, 1.39)),
            Wait(0.5 if not suitB else 0.0),
            Func(self.battle.movie.needRestoreParticleEffect, particleEffect),
            Func(particleEffect.start, sign),
            Func(particleEffect.wrtReparentTo, render),
            Parallel(
                LerpPosInterval(particleEffect, 2.0, pos=hitPoint),
                Sequence(
                    Wait(1.0),
                    Func(particleEffect.softStop),
                )
            ),
            Func(particleEffect.cleanup),
            Func(self.battle.movie.clearRestoreParticleEffect, particleEffect),
        )
        signPropAnimTrack = ActorInterval(sign, "smile", duration=4, startTime=0, playRate=1.0 if not suitB else 1.25)
        offset = 0.5 if not suitB else 0.0
        toonTrack = self.getToonTrack(2.1 + offset, ["cringe"], 1.4 + offset, ["sidestep"], dodgeAnimPlayRate=1.2)
        soundTrack = self.getSoundTrack(
            "SA_razzle_dazzle.ogg", delay=1.1 + offset, node=self.invoker
        )
        return Sequence(
            Parallel(
                suitTrack, signPropTrack, signPropAnimTrack, toonTrack, soundTrack
            ),
            Func(MovieUtil.removeProp, sign),
        )


@AttackClass(attackType=AttackEnum.RED_TAPE)
class RedTape(SuitSingleAttack):
    ANIM_NAME = "throw-object"
    PLAY_RATE = 1.4
    OPEN_SHOT_DUR = (70/24)/PLAY_RATE

    def doAttack(self):
        target = self.targetDicts[0]
        toon = target["avatar"]
        tape = globalPropPool.getProp("redtape")
        tubes = [globalPropPool.getProp("redtape-tube")]

        suitTrack = self.getSuitTrack(playRate=self.PLAY_RATE)
        tapePosPoints = [
            Point3(-0.0, 0.09, -0.38),
            VBase3(-1.152, 86.581, -76.784),
        ]
        tapeScaleUpPoint = Point3(0.9, 0.9, 0.24)
        propTrack = Sequence(
            self.getPropAppearTrack(
                tape,
                self.invoker.getRightHand(),
                tapePosPoints,
                0.8/self.PLAY_RATE,
                tapeScaleUpPoint,
                scaleUpTime=0.5/self.PLAY_RATE,
            )
        )
        propTrack.append(Wait(1.73/self.PLAY_RATE))
        hitPoint = lambda toon=toon: self.toonTorsoPoint(toon)
        propTrack.append(
            self.getPropThrowTrack(tape, [hitPoint], [self.toonGroundPoint(toon, 0.7)], hitDuration=0.5/self.PLAY_RATE, missDuration=0.5/self.PLAY_RATE)
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
                    3.25/self.PLAY_RATE,
                    3.17/self.PLAY_RATE,
                    scaleUpPoint=scaleUpPoint,
                )
            )

        tubeTracks.append(Func(self.battle.movie.clearRestoreHips))

        damageAnims = [{AAK.Anim: "struggle", AAK.StartTime: 1.0}]

        toonTrack = self.getToonTrack(
            damageDelay=3.4/self.PLAY_RATE,
            splicedDamageAnims=damageAnims,
            dodgeDelay=2.4/self.PLAY_RATE,
            dodgeAnimNames=["jump"],
            damageAnimPlayRate=1.3)
        soundTrack = self.getSoundTrack("SA_red_tape.ogg", delay=2.9/self.PLAY_RATE, node=self.invoker)
        if target["landed"]:
            return Parallel(suitTrack, toonTrack, propTrack, soundTrack, tubeTracks)
        else:
            return Parallel(suitTrack, toonTrack, propTrack, soundTrack)


@AttackClass(attackType=(AttackEnum.RE_ORG, AttackEnum.RE_ARRANGE))
class ReOrg(SuitSingleAttack):
    ANIM_NAME = "magic3"
    PLAY_RATE = 1.2
    OPEN_SHOT_DUR = 1.1

    def doAttack(self):
        target = self.targetDicts[0]
        toon = target["avatar"]
        damageDelay = 1.0
        attackDelay = 1.5/self.PLAY_RATE
        sprayEffect = BattleParticles.createParticleEffect(file="reorgSpray")
        suitTrack = self.getSuitTrack(playRate=self.PLAY_RATE)
        particleNode = self.battle.attachNewNode('reorg-particle-node')
        particleNode.setPos(self.battle.getActorPosHpr(self.invoker)[0])
        particleNode.headsUp(toon)

        if self.invoker.dna.name in ('foreman', 'msfore', 'ftf_s', "dold"):
            particleNode.setZ(particleNode.getZ() + 3)
            particleNode.setP(particleNode.getP() - 15)
        elif self.invoker.dna.name in ("hh", "dlao"):
            particleNode.setZ(particleNode.getZ() + 1)
            particleNode.setP(particleNode.getP() - 5)

        partTrack = Sequence(
            self.getPartTrack(
                sprayEffect, 1.0/self.PLAY_RATE, 2.9/self.PLAY_RATE, [sprayEffect, particleNode, 0], softStop=-1.0
            ),
            Func(particleNode.removeNode),
        )
        if target["landed"]:
            tPPR = 1.3
            headParts = toon.getHeadParts()
            headTracks = Parallel()
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
                        LerpPosInterval(part, 0.1/tPPR, Point3(x - 0.2, y, z - 0.03)),
                        LerpPosInterval(part, 0.1/tPPR, Point3(x + 0.4, y, z - 0.03)),
                        LerpPosInterval(part, 0.1/tPPR, Point3(x - 0.4, y, z - 0.03)),
                        LerpPosInterval(part, 0.1/tPPR, Point3(x + 0.4, y, z - 0.03)),
                        LerpPosInterval(part, 0.1/tPPR, Point3(x - 0.2, y, z - 0.04)),
                        LerpPosInterval(part, 0.25/tPPR, Point3(x, y, z + 2.2)),
                        LerpHprInterval(part, 0.4/tPPR, VBase3(360, 0, 180)),
                        LerpPosInterval(part, 0.3/tPPR, Point3(x, y, z + 3.1)),
                        LerpPosInterval(part, 0.15/tPPR, Point3(x, y, z + 0.3)),
                        Wait(0.15/tPPR),
                        LerpHprInterval(
                            part, 0.6/tPPR, VBase3(-745, 0, 180), startHpr=VBase3(0, 0, 180)
                        ),
                        LerpHprInterval(
                            part, 0.8/tPPR, VBase3(25, 0, 180), startHpr=VBase3(0, 0, 180)
                        ),
                        LerpPosInterval(part, 0.15/tPPR, Point3(x, y, z + 1)),
                        LerpHprInterval(part, 0.3/tPPR, VBase3(h, p, r)),
                        Wait(0.2/tPPR),
                        LerpPosInterval(part, 0.1/tPPR, Point3(x, y, z)),
                        Wait(0.9/tPPR),
                    )
                )

            def getChestTrack(part, attackDelay=attackDelay):
                origScale = part.getScale()
                return Sequence(
                    Wait(attackDelay),
                    LerpHprInterval(part, 1.1/tPPR, VBase3(180, 0, 0)),
                    Wait(1.1/tPPR),
                    LerpHprInterval(part, 1.1/tPPR, part.getHpr()),
                )

            chestTracks = Parallel()
            arms = toon.findAllMatches("**/arms")
            sleeves = toon.findAllMatches("**/sleeves")
            hands = toon.findAllMatches("**/hands")
            for part in arms + sleeves + hands:
                chestTracks.append(getChestTrack(part))

        damageAnims = [
            ["neutral", 0.01, 0.01, 0.5],
            ["juggle", 0.01, 0.01, 1.48],
            ["think", 0.01, 2.28],
        ]
        dodgeAnims = []
        dodgeAnims.append(["think", 0.01, 0, 0.6])
        toonTrack = self.getToonTrack(
            damageDelay=damageDelay,
            splicedDamageAnims=damageAnims,
            dodgeDelay=0.01,
            dodgeAnimNames=["duck"],
            showDamageExtraTime=2.1,
            showMissedExtraTime=2.0,
        )
        if target["landed"]:
            return Parallel(suitTrack, partTrack, toonTrack, headTracks, chestTracks)
        else:
            return Parallel(suitTrack, partTrack, toonTrack)


@AttackClass(attackType=AttackEnum.RESTRAINING_ORDER)
class RestrainingOrder(SuitSingleAttack):
    ANIM_NAME = "throw-paper"
    PLAY_RATE = 1.4
    OPEN_SHOT_DUR = 2.8/PLAY_RATE

    def doAttack(self):
        target = self.targetDicts[0]
        toon = target["avatar"]
        paper = globalPropPool.getProp("shredder-paper")
        suitTrack = self.getSuitTrack(playRate=self.PLAY_RATE)
        posPoints = [Point3(1.2, -1.5, 0), VBase3((150, -45, 120))]
        propTrack = Sequence(
            self.getPropAppearTrack(
                paper,
                self.invoker.getRightHand(),
                posPoints,
               0.9/self.PLAY_RATE,
                MovieUtil.PNT3_ONE,
                scaleUpTime=0.4/self.PLAY_RATE,
            )
        )
        propTrack.append(Wait(1.73/self.PLAY_RATE))
        hitPoint = self.toonFacePoint(toon, parent=self.battle)
        hitPoint.setX(hitPoint.getX() - 1.4)
        missPoint = self.toonGroundPoint(toon, 0.7, parent=self.battle)
        missPoint.setX(missPoint.getX() - 1.1)
        propTrack.append(
            self.getPropThrowTrack(paper, [hitPoint], [missPoint], parent=self.battle, hitDuration=0.5/self.PLAY_RATE,
                                   missDuration=0.5/self.PLAY_RATE)
        )
        damageAnims = [
            ["struggle", 0.01, 0.2],
        ]
        toonTrack = self.getToonTrack(
            damageDelay=3.3/self.PLAY_RATE,
            splicedDamageAnims=damageAnims,
            dodgeDelay=2.4/self.PLAY_RATE,
            dodgeAnimNames=["sidestep"],
            damageAnimPlayRate=1.3,
            dodgeAnimPlayRate=1.2,
        )
        if target["landed"]:
            restraintCloud = BattleParticles.createParticleEffect(
                file="restrainingOrderCloud"
            )
            restraintCloud.setPos(
                hitPoint.getX(), hitPoint.getY() + 0.5, hitPoint.getZ()
            )
            cloudTrack = self.getPartTrack(
                restraintCloud, 3.5/self.PLAY_RATE, 0.2, [restraintCloud, self.battle, 0]
            )
            return Parallel(suitTrack, cloudTrack, toonTrack, propTrack)
        else:
            return Parallel(suitTrack, toonTrack, propTrack)


@AttackClass(attackType=(AttackEnum.ROLODEX, AttackEnum.ROLODEX_DOUBLE))
class Rolodex(SuitSingleAttack):
    ANIM_NAME = "roll-o-dex"
    PLAY_RATE = 1.35
    OPEN_SHOT_DUR = 3.5/PLAY_RATE

    def doAttack(self):
        suitTrack = self.getSuitAnimTrack(playRate=self.PLAY_RATE)
        perToonTracks = Parallel()

        rollodex = globalPropPool.getProp("rollodex")
        part2Duration = 1.9
        part3Duration = 2.5
        suitType = getSuitBodyType(self.invoker.dna.name)
        if suitType == "a":
            propPosPoints = [Point3(-0.51, -0.03, -0.1), VBase3(89.673, 2.166, 177.786)]
            propScale = Point3(1.2, 1.2, 1.2)
            part2Delay = 2.8
            part3Delay = 3.2
            damageDelay = 3.8
            dodgeDelay = 2.5
        elif suitType == "b":
            propPosPoints = [Point3(0.12, 0.24, 0.01), VBase3(99.032, 5.973, -179.839)]
            propScale = Point3(0.91, 0.91, 0.91)
            part2Delay = 3.1
            part3Delay = 3.5
            damageDelay = 4
            dodgeDelay = 2.5
        elif suitType == "c":
            propPosPoints = [Point3(-0.51, -0.03, -0.1), VBase3(89.673, 2.166, 177.786)]
            propScale = Point3(1.2, 1.2, 1.2)
            part2Delay = 2.8
            part3Delay = 3.2
            damageDelay = 3.5
            dodgeDelay = 2.5
        propTrack = self.getPropTrack(
            rollodex,
            self.invoker.getLeftHand(),
            propPosPoints,
            1e-06,
            4.6/self.PLAY_RATE,
            scaleUpPoint=propScale,
            anim=0,
            propName="rollodex",
            animDuration=0,
            animStartTime=0,
            scaleUpTime=0.5/self.PLAY_RATE,
            scaleDownTime=0.5/self.PLAY_RATE,
        )

        for target in self.targetDicts:
            toon = target["avatar"]
            particleEffect2 = BattleParticles.createParticleEffect(file="rollodexWaterfall")
            particleEffect3 = BattleParticles.createParticleEffect(file="rollodexStream")

            particleNode = self.invoker.attachNewNode('rolodex-particle-node')
            headsUp = Sequence(Func(particleNode.headsUp, toon))

            if self.invoker.style.name == 'hh':
                headsUp.append(Func(particleNode.setZ, 2))
                headsUp.append(Func(particleNode.setP, -12))
            elif self.invoker.style.name in ('caseman', 'chainsaw'):
                headsUp.append(Func(particleNode.setZ, 2.9))
                headsUp.append(Func(particleNode.setP, -17))

            partTrack2 = self.getPartTrack(
                particleEffect2,
                part2Delay/self.PLAY_RATE,
                part2Duration/self.PLAY_RATE,
                [particleEffect2, particleNode, 0],
            )
            partTrack3 = self.getPartTrack(
                particleEffect3,
                part3Delay/self.PLAY_RATE,
                part3Duration/self.PLAY_RATE,
                [particleEffect3, particleNode, 0],
                softStop=-1.0,
            )
            particleTrack = Sequence(
                headsUp,
                Parallel(
                    partTrack2,
                    partTrack3,
                ),
                Func(particleNode.removeNode),
            )

            toonTrack = self.getToonTrack(damageDelay/self.PLAY_RATE, ["cringe"], dodgeDelay/self.PLAY_RATE,
                                          ["sidestep"], dodgeAnimPlayRate=1.2, target=target)
            soundTrack = self.getSoundTrack("SA_rolodex.ogg", delay=2.8/self.PLAY_RATE, node=self.invoker)
            perToonTracks.append(Parallel(toonTrack, soundTrack, particleTrack))

        return Parallel(suitTrack, propTrack, perToonTracks)

    def getCameraShot(self, duration):
        if len(self.targetObjs) > 1:
            return self.camera.randomGroupAttackCam(
                self.invoker, self.targetDicts, self.battle, duration, self.OPEN_SHOT_DUR)
        else:
            return SuitSingleAttack.getCameraShot(self, duration)


@AttackClass(attackType=AttackEnum.RUBBER_STAMP)
class RubberStamp(SuitSingleAttack):
    ANIM_NAME = "rubber-stamp"
    PLAY_RATE = 1.1
    OPEN_SHOT_DUR = (52/24)/PLAY_RATE

    def doAttack(self):
        target = self.targetDicts[0]
        toon = target["avatar"]
        suitTrack = self.getSuitTrack(playRate=self.PLAY_RATE)
        stamp = globalPropPool.getProp("rubber-stamp")
        pad = globalPropPool.getProp("rubber-stamp-pad")
        cancelled = self.makeCancelledNodePath()
        bodyType = getSuitBodyType(self.invoker.style.name)
        if bodyType == "a":
            padPosPoints = [Point3(-0.7541, 0.267, -0.13), VBase3(-77.0589, 180, -3.292)]
            stampPosPoints = [Point3(-0.0772, -0.7336, -0.0534), VBase3(270, -28.585, 270)]
        else:
            padPosPoints = [Point3(-0.1005, -0.1506, -0.0466), VBase3(-13.3334, 180, -14.7299)]
            stampPosPoints = [Point3(-0.0772, -0.7336, -0.0534), VBase3(270, -28.585, 270)]
        padPropTrack = self.getPropTrack(pad, self.invoker.getLeftHand(), padPosPoints, 1e-06, 3.3, scaleDownTime=0.2)
        missPoint = lambda cancelled=cancelled, toon=toon: self.toonMissPoint(cancelled, toon)
        propTrack = Sequence(
            Func(
                self.showProp,
                stamp,
                self.invoker.getRightHand(),
                stampPosPoints[0],
                stampPosPoints[1],
            ),
            LerpScaleInterval(stamp, 0.5/self.PLAY_RATE, 1.2),
            Wait(2.6/self.PLAY_RATE),
            Func(self.battle.movie.needRestoreRenderProp, cancelled),
            Func(cancelled.reparentTo, render),
            Func(cancelled.setScale, 0.6),
            Func(cancelled.setPosHpr, stamp, 0, -0.2, -0.16, 0, 0, 90),
            Func(cancelled.setP, 0),
            Func(cancelled.setR, 0),
        )
        propTrack.append(
            self.getPropThrowTrack(cancelled, [self.toonFacePoint(toon)], [missPoint],
                                   hitDuration=0.3/self.PLAY_RATE, missDuration=0.3/self.PLAY_RATE, lookAt=toon)
        )
        propTrack.append(Func(MovieUtil.removeProp, cancelled))
        propTrack.append(Func(self.battle.movie.clearRenderProp, cancelled))
        propTrack.append(Wait(0.2/self.PLAY_RATE))
        propTrack.append(LerpScaleInterval(stamp, 0.5/self.PLAY_RATE, MovieUtil.PNT3_NEARZERO))
        propTrack.append(Func(MovieUtil.removeProp, stamp))
        toonTrack = self.getToonTrack(damageDelay=3.28/self.PLAY_RATE,
                                      splicedDamageAnims=[["cringe"]],
                                      dodgeDelay=1.7/self.PLAY_RATE,
                                      dodgeAnimNames=["sidestep"],
                                      dodgeAnimPlayRate=1.2,
                                      )
        soundDuration = None
        if not target["landed"]:
            soundDuration = 2.3
        soundTrack = self.getSoundTrack("SA_rubber_stamp.ogg", delay=0.6/self.PLAY_RATE, duration=soundDuration,
                                        node=self.invoker)
        return Parallel(suitTrack, toonTrack, propTrack, padPropTrack, soundTrack)

    def makeCancelledNodePath(self):
        tn = TextNode("CANCELLED")
        tn.setFont(ToontownGlobals.getSuitFont())
        tn.setText(TTLocalizer.MovieSuitCancelled)
        tn.setAlign(TextNode.ACenter)
        tntop = hidden.attachNewNode("CancelledTop")
        tnpath = tntop.attachNewNode(tn)
        tnpath.setPosHpr(0, 0, 0, 0, 0, 0)
        tnpath.setScale(1)
        tnpath.setColor(0.7, 0, 0, 1)
        tnpathback = tnpath.instanceUnderNode(tntop, "backside")
        tnpathback.setPosHpr(0, 0, 0, 180, 0, 0)
        tnpath.setScale(1)
        return tntop


@AttackClass(attackType=AttackEnum.RUB_OUT)
class RubOut(SuitSingleAttack):
    ANIM_NAME = "hold-eraser"
    PLAY_RATE = 1.1
    OPEN_SHOT_DUR = (42/24)/PLAY_RATE

    def doAttack(self):
        target = self.targetDicts[0]
        toon = target["avatar"]
        pad = globalPropPool.getProp("pad")
        pencil = globalPropPool.getProp("pencil")
        headEffect = BattleParticles.createParticleEffect(
            "RubOut", color=toon.style.getHeadColor()
        )
        torsoEffect = BattleParticles.createParticleEffect(
            "RubOut", color=toon.style.getArmColor()
        )
        legsEffect = BattleParticles.createParticleEffect(
            "RubOut", color=toon.style.getLegColor()
        )
        appearEffect = BattleParticles.createParticleEffect(
            "RubOut", color=toon.style.getHeadColor()
        )
        suitTrack = self.getSuitTrack(playRate=self.PLAY_RATE)
        padPosPoints = [Point3(-0.16, 0.51, -0.06), VBase3(14.93, -2.29, 180.0)]
        padPropTrack = self.getPropTrack(
            pad, self.invoker.getLeftHand(), padPosPoints, 0.5/self.PLAY_RATE, 2.57/self.PLAY_RATE,
            scaleUpTime=0.5/self.PLAY_RATE, scaleDownTime=0.5/self.PLAY_RATE
        )
        pencilPosPoints = [Point3(0.04, -0.38, -0.1), VBase3(-170.223, -3.762, -62.929)]
        pencilPropTrack = self.getPropTrack(
            pencil, self.invoker.getRightHand(), pencilPosPoints, 0.5/self.PLAY_RATE, 2.57/self.PLAY_RATE,
            scaleUpTime=0.5/self.PLAY_RATE, scaleDownTime=0.5/self.PLAY_RATE
        )
        toonTrack = self.getToonTrack(1.7/self.PLAY_RATE, ["conked"], 2.0/self.PLAY_RATE, ["jump"],
                                      damageAnimPlayRate=1.2, showDamageExtraTime=1.0)
        hideTrack = Sequence()
        headParts = toon.getHeadParts()
        torsoParts = toon.getTorsoParts()
        legsParts = toon.getLegsParts()
        animal = toon.style.getAnimal()
        bodyScale = ToontownGlobals.toonBodyScales[animal]
        headEffectHeight = self.toonFacePoint(toon).getZ()
        legsHeight = ToontownGlobals.legHeightDict[toon.style.legs] * bodyScale
        torsoEffectHeight = (
            ToontownGlobals.torsoHeightDict[toon.style.torso] * bodyScale / 2
            + legsHeight
        )
        legsEffectHeight = legsHeight / 2
        effectX = headEffect.getX()
        effectY = headEffect.getY()
        headEffect.setPos(effectX, effectY, headEffectHeight)
        torsoEffect.setPos(effectX, effectY - 1, torsoEffectHeight)
        legsEffect.setPos(effectX, effectY - 0.6, legsEffectHeight)
        appearEffect.setPos(effectX, effectY - 1, torsoEffectHeight)
        partDelay = 1.8/self.PLAY_RATE
        headTrack = self.getPartTrack(
            headEffect, partDelay + 0, 0.5/self.PLAY_RATE, [headEffect, toon, 0]
        )
        torsoTrack = self.getPartTrack(
            torsoEffect, partDelay + (0.5/self.PLAY_RATE), 0.5/self.PLAY_RATE, [torsoEffect, toon, 0]
        )
        legsTrack = self.getPartTrack(
            legsEffect, partDelay + (1.0/self.PLAY_RATE), 0.5/self.PLAY_RATE, [legsEffect, toon, 0]
        )
        appearTrack = self.getPartTrack(
            appearEffect, partDelay + (2.0/self.PLAY_RATE), 0.5/self.PLAY_RATE, [appearEffect, toon, 0]
        )

        def hideParts(parts):
            track = Parallel()
            for nextPart in parts:
                track.append(Func(nextPart.setTransparency, 1))
                track.append(
                    LerpFunctionInterval(
                        nextPart.setAlphaScale, fromData=1, toData=0, duration=0.2/self.PLAY_RATE
                    )
                )

            return track

        def showParts(parts):
            track = Parallel()
            for nextPart in parts:
                track.append(Func(nextPart.clearColorScale))
                track.append(Func(nextPart.clearTransparency))

            return track

        soundTrack = self.getSoundTrack("SA_rubout.ogg", delay=1.65/self.PLAY_RATE, node=self.invoker)
        if target["landed"]:
            hideTrack.append(Wait(1.8/self.PLAY_RATE))
            hideTrack.append(Func(self.battle.movie.needRestoreColor))
            hideTrack.append(hideParts(headParts))
            hideTrack.append(Wait(0.3/self.PLAY_RATE))
            hideTrack.append(hideParts(torsoParts))
            hideTrack.append(Wait(0.3/self.PLAY_RATE))
            hideTrack.append(hideParts(legsParts))
            hideTrack.append(Wait(0.8/self.PLAY_RATE))
            hideTrack.append(showParts(headParts))
            hideTrack.append(showParts(torsoParts))
            hideTrack.append(showParts(legsParts))
            hideTrack.append(Func(self.battle.movie.clearRestoreColor))
            return Parallel(
                suitTrack,
                toonTrack,
                padPropTrack,
                pencilPropTrack,
                soundTrack,
                hideTrack,
                headTrack,
                torsoTrack,
                legsTrack,
                appearTrack,
            )
        else:
            return Parallel(
                suitTrack, toonTrack, padPropTrack, pencilPropTrack, soundTrack
            )


@AttackClass(attackType=AttackEnum.SACKED)
class Sacked(SuitSingleAttack):
    ANIM_NAME = "throw-object"
    PLAY_RATE = 1.3
    OPEN_SHOT_DUR = 2.9/PLAY_RATE

    def doAttack(self):
        target = self.targetDicts[0]
        toon = target["avatar"]
        hips = toon.getHipsParts()
        propDelay = 0.85/self.PLAY_RATE
        suitDelay = 47/24/self.PLAY_RATE
        throwDuration = 0.7/self.PLAY_RATE

        dust = globalPropPool.getProp("dust")
        dust.setBillboardPointWorld(2)

        sack = globalPropPool.getProp("sandbag")
        initialScale = Point3(0.4, 0.4, 0.4)
        scaleUpPoint = Point3(1.2, 1.2, 1.2) * 2.0
        sackHpr = VBase3(0, 45, 0)
        suitTrack = self.getSuitTrack(playRate=self.PLAY_RATE)
        posPoints = [Point3(-0.3, 0, 0), VBase3(-60, 0, 180)]
        sackAppearTrack = Sequence(
            self.getPropAppearTrack(
                sack,
                self.invoker.getRightHand(),
                posPoints,
                propDelay,
                initialScale,
                scaleUpTime=0.2/self.PLAY_RATE,
            )
        )
        propDelay = propDelay + (0.2/self.PLAY_RATE)
        sackAppearTrack.append(Wait(suitDelay))
        hitPoint = toon.getPos(self.battle)
        if target["landed"]:
            hitPoint.setX(hitPoint.getX() + 1.0)
            hitPoint.setY(hitPoint.getY() + 0.9)
            hitPoint.setZ(hitPoint.getZ() + (toon.height/2))
        else:
            hitPoint.setZ(hitPoint.getZ() - 0.2)
        sackAppearTrack.append(Func(self.battle.movie.needRestoreRenderProp, sack))
        sackAppearTrack.append(
            self.getThrowTrack(
                sack, hitPoint, duration=throwDuration, parent=self.battle
            )
        )
        if target["landed"]:
            sackAppearTrack.append(Func(self.battle.movie.needRestoreHips))
            sackAppearTrack.append(Func(sack.wrtReparentTo, hips[0]))
            sackAppearTrack.append(Wait(2.4/self.PLAY_RATE))
            sackAppearTrack.append(Func(self.battle.movie.clearRestoreHips))
            scaleTrack = Sequence(
                Wait(propDelay + suitDelay),
                LerpScaleInterval(sack, throwDuration, scaleUpPoint),
                Wait(1.8/self.PLAY_RATE),
                LerpScaleInterval(sack, 0.3/self.PLAY_RATE, MovieUtil.PNT3_NEARZERO),
            )
            hprTrack = Sequence(
                Wait(propDelay + suitDelay),
                LerpHprInterval(sack, throwDuration, sackHpr),
            )
            sackTrack = Sequence(
                Parallel(sackAppearTrack, scaleTrack, hprTrack),
                Func(MovieUtil.removeProp, sack),
                Func(self.battle.movie.clearRenderProp, sack),
            )
            dustTrack = Sequence(
                Wait(propDelay + suitDelay + throwDuration),
                Func(dust.reparentTo, toon),
                ActorInterval(dust, "dust"),
                Func(dust.cleanup),
            )
        else:
            missPoint1 = Vec3(hitPoint[0], hitPoint[1] - 2.5, hitPoint[2])
            missPoint2 = Vec3(hitPoint[0], hitPoint[1] - 3.3, hitPoint[2])
            sackHprTrack = Sequence(
                Wait(propDelay + suitDelay),
                LerpHprInterval(sack, throwDuration, (0, 0, 0), blendType='easeIn')
            )
            sackTrack = Sequence(
                Parallel(sackAppearTrack, sackHprTrack),
                ProjectileInterval(sack, duration=0.7, endPos=missPoint1),
                ProjectileInterval(sack, duration=0.4, endPos=missPoint2),
                Wait(0.4),
                LerpScaleInterval(sack, 0.3/self.PLAY_RATE, MovieUtil.PNT3_NEARZERO),
                Func(MovieUtil.removeProp, sack),
                Func(self.battle.movie.clearRenderProp, sack),
            )
            dustTrack = Sequence()
        damageAnims = [["struggle", 0.01, 0.01, 0.7], ["slip-backward", 0.01, 0.45]]
        toonTrack = self.getToonTrack(
            damageDelay=propDelay + suitDelay + throwDuration,
            splicedDamageAnims=damageAnims,
            dodgeDelay=3.0/self.PLAY_RATE,
            dodgeAnimNames=["sidestep"],
            showDamageExtraTime=1.8,
            showMissedExtraTime=0.8,
            damageAnimPlayRate=1.2,
            dodgeAnimPlayRate=1.2,
        )
        soundTrack = self.getSoundTrack(
            "AA_drop_sandbag.ogg",
            delay=propDelay + suitDelay + throwDuration,
            node=self.invoker,
        )
        return Parallel(suitTrack, toonTrack, soundTrack, sackTrack, dustTrack)


@AttackClass(attackType=AttackEnum.SCHMOOZE)
class Schmooze(SuitSingleAttack):
    ANIM_NAME = "speak"
    PLAY_RATE = 1.4
    OPEN_SHOT_DUR = 3/PLAY_RATE

    def doAttack(self):
        target = self.targetDicts[0]
        toon = target["avatar"]

        BattleParticles.loadParticles()
        upperEffects = []
        lowerEffects = []
        textureNames = [
            "schmooze-genius",
            "schmooze-instant",
            "schmooze-master",
            "schmooze-viz",
        ]
        particleNode = self.battle.attachNewNode('schmooze-particle-node')
        particleNode.setPos(self.battle.getActorPosHpr(self.invoker)[0])
        particleNode.headsUp(toon)
        particleNode.setBin('fixed', 1)

        for i in range(2):
            upperEffect = BattleParticles.createParticleEffect(
                file="schmoozeUpperSpray"
            )
            lowerEffect = BattleParticles.createParticleEffect(
                file="schmoozeLowerSpray"
            )
            BattleParticles.setEffectTexture(
                upperEffect, textureNames[i], color=Vec4(0, 0, 1, 1)
            )
            BattleParticles.setEffectTexture(
                lowerEffect, textureNames[i+2], color=Vec4(0, 0, 1, 1)
            )
            upperEffects.append(upperEffect)
            lowerEffects.append(lowerEffect)

        partDelay = 2.75/self.PLAY_RATE
        damageDelay = 3.1/self.PLAY_RATE
        dodgeDelay = 1.9/self.PLAY_RATE
        suitTrack = self.getSuitTrack(playRate=self.PLAY_RATE)
        upperPartTracks = Parallel()
        lowerPartTracks = Parallel()
        for i in range(2):
            upperPartTracks.append(
                self.getPartTrack(
                    upperEffects[i],
                    partDelay + (((i * 0.65) + 0.2)/self.PLAY_RATE),
                    2.0/self.PLAY_RATE,
                    [upperEffects[i], particleNode, 0],
                    softStop=-1.0,
                )
            )
            lowerPartTracks.append(
                self.getPartTrack(
                    lowerEffects[i],
                    partDelay + (((i * 0.65) + 0.2)/self.PLAY_RATE),
                    2.0/self.PLAY_RATE,
                    [lowerEffects[i], particleNode, 0],
                    softStop=-1.0,
                )
            )
        lowerPartTracks.append(Sequence(Wait(5.7), Func(particleNode.removeNode)))

        damageAnims = [
            ["conked", 0.01, 0.3, 0.71],
            ["conked", 0.01, 0.3],
        ]

        toonTrack = self.getToonTrack(
            damageDelay=damageDelay,
            splicedDamageAnims=damageAnims,
            dodgeDelay=dodgeDelay,
            dodgeAnimNames=["duck"],
            showMissedExtraTime=1.9,
            showDamageExtraTime=1.1,
            damageAnimPlayRate=1.3,
            dodgeAnimPlayRate=1.05,
        )
        soundTrack = self.getSoundTrack("SA_schmooze.ogg", delay=2.8/self.PLAY_RATE, node=self.invoker, playRate=1.05)
        return Parallel(
            suitTrack, toonTrack, soundTrack, upperPartTracks, lowerPartTracks
        )


@AttackClass(attackType=AttackEnum.SHAKE)
class Shake(SuitGroupAttack):
    ANIM_NAME = "stomp"

    def doAttack(self):
        suitTrack = self.getSuitAnimTrack()
        damageAnims = [["slip-forward"], ["slip-forward", 0.01]]
        dodgeAnims = [["jump"], ["jump", 0.01]]
        toonTracks = self.getToonTracks(
            damageDelay=1.1,
            splicedDamageAnims=damageAnims,
            dodgeDelay=0.7,
            splicedDodgeAnims=dodgeAnims,
            showMissedExtraTime=2.8,
            showDamageExtraTime=1.1,
        )
        soundTrack = self.getSoundTrack("SA_shake.ogg", delay=0, node=self.invoker)
        return Parallel(suitTrack, soundTrack, toonTracks)

    def getCameraShot(self, duration):
        extraDelay = 0.0
        if self.shownUnlureMovie:
            extraDelay = 0.6
        shakeIntensity = 0.5
        return self.camera.suitCameraShakeShot(duration, shakeIntensity, extraDelay=extraDelay)


@AttackClass(attackType=AttackEnum.SHORT_SQUEEZE)
class ShortSqueeze(SuitSingleAttack):
    ANIM_NAME = "short-squeeze"
    OPEN_SHOT_DUR = 0.0
    WantSprayParticles = True

    def doAttack(self):
        target = self.targetDicts[0]
        toon = target["avatar"]

        damageDelay = 1.07
        dodgeDelay = 0.4
        particleDelay = 0.9
        stretchDelay = 1.07

        suitTrack = self.getSuitTrack()

        damageAnims = [
            {AAK.Anim: "struggle", AAK.StartTime: 1.0, AAK.Duration: 1.0},
            {AAK.Anim: "slip-backward"},
        ]
        toonTrack = self.getToonTrack(
            damageDelay=damageDelay,
            splicedDamageAnims=damageAnims,
            dodgeDelay=dodgeDelay,
            dodgeAnimNames=["sidestep"],
            dodgeAnimPlayRate=1.2,
            showDamageExtraTime=1.0,
        )
        toonPos = toon.getPos()
        upPos = Vec3(toonPos[0], toonPos[1], toonPos[2] + 3.5)
        downPos = Vec3(toonPos[0], toonPos[1], toonPos[2] + 0.5)

        if target["landed"]:
            particleNode = self.battle.attachNewNode('short-squeeze-particle-node')
            particleNode.setPos(self.battle.getActorPosHpr(toon)[0])
            particleNode.setZ(toon.getHeight() / 2.0)
            crushEffect = BattleParticles.createParticleEffect(file='shortSqueezeCrush')
            crushEffect.setDepthWrite(0)
            crushEffect.setDepthTest(0)
            crushEffect.setTwoSided(1)

            sprayEffect = BattleParticles.createParticleEffect(file='shortSqueezeSpray')
            coinTypes = ('bronze', 'silver', 'gold')
            for i in range(3):
                coin = loader.loadModel(f'phase_3.5/models/props/cc_m_prp_gen_coin_{coinTypes[i]}')
                coin.setHpr(360 * random.random(), 360 * random.random(), 360 * random.random())
                coin = coin.copyTo(NodePath('coin-holder'))
                p = sprayEffect.getParticlesNamed(f'particles-{i+1}')
                p.renderer.setGeomNode(coin.node())

            partTrack = Sequence(
                Parallel(
                    self.getPartTrack(
                        crushEffect, particleDelay, 1.2, [crushEffect, particleNode, 0], softStop=-1.0
                    ),
                    self.getPartTrack(
                        sprayEffect, particleDelay + 0.2, 2.6, [sprayEffect, particleNode, 0], softStop=-1.4
                    ) if self.WantSprayParticles else Sequence(),
                ),

                Func(particleNode.removeNode),
            )

            stretchParts = toon.headParts + toon.legsParts + toon.torsoParts

            finalHeadPartsScale = 1.0
           # if toon.cheesyEffect == ToontownGlobals.CEBigHead:
            #    finalHeadPartsScale = ToontownGlobals.BigHeadScale
           # elif toon.cheesyEffect == ToontownGlobals.CESmallHead:
            #    finalHeadPartsScale = ToontownGlobals.SmallHeadScale

            #finalLegPartsScale = 1.0
            #if toon.cheesyEffect == ToontownGlobals.CEBigLegs:
            #    finalLegPartsScale = ToontownGlobals.BigLegsScale
            #elif toon.cheesyEffect == ToontownGlobals.CESmallLegs:
             #   finalLegPartsScale = ToontownGlobals.SmallLegsScale

            finalTorsoPartsScale = 1.0 / finalLegPartsScale

            toonStretchTrack = Sequence(
                Wait(stretchDelay),
                Parallel(
                    *[LerpScaleInterval(part, 0.2, (0.75, 0.75, 1.3), blendType='easeIn') for part in stretchParts],
                    Sequence(
                        *[Sequence(
                            LerpPosInterval(toon, 0.19 if i == 3 else 0.13, upPos),
                            LerpPosInterval(toon, 0.19 if i == 3 else 0.13, downPos),
                        ) for i in range(4)],
                    ),
                ),
                Parallel(
                    LerpPosInterval(toon, 0.06, toonPos, blendType='easeIn'),
                    Sequence(
                        Parallel(
                            *[LerpScaleInterval(part, 0.15, finalHeadPartsScale*1.3, blendType='easeOut') for part in toon.headParts],
                            *[LerpScaleInterval(part, 0.15, finalLegPartsScale*1.3, blendType='easeOut') for part in toon.legsParts],
                            *[LerpScaleInterval(part, 0.15, finalTorsoPartsScale*1.3, blendType='easeOut') for part in toon.torsoParts],
                        ),
                        Parallel(
                            *[LerpScaleInterval(part, 0.4, finalHeadPartsScale, blendType='easeIn') for part in toon.headParts],
                            *[LerpScaleInterval(part, 0.4, finalLegPartsScale, blendType='easeIn') for part in toon.legsParts],
                            *[LerpScaleInterval(part, 0.4, finalTorsoPartsScale, blendType='easeIn') for part in toon.torsoParts],
                        ),
                    ),
                ),
            )

            soundTrack = self.getSoundTrack("SA_pick_pocket.ogg", node=self.invoker, delay=0.4)
            soundTrack2 = self.getSoundTrack("Toon_bodyfall_synergy.ogg", delay=damageDelay + 1.2)
        else:
            toonStretchTrack, partTrack, soundTrack, soundTrack2 = Sequence(), Sequence(), Sequence(), Sequence()

        return Parallel(
            suitTrack, toonTrack, toonStretchTrack, partTrack, soundTrack, soundTrack2
        )

    def getCameraShot(self, duration):
        return self.camera.randomSplitShot(self.invoker, self.targetDicts[0]["avatar"], self.battle, duration)


@AttackClass(attackType=AttackEnum.SHRED)
class Shred(SuitSingleAttack):
    ANIM_NAME = "shredder"
    PLAY_RATE = 1.25
    OPEN_SHOT_DUR = (80/24)/PLAY_RATE

    def doAttack(self):
        target = self.targetDicts[0]
        toon = target["avatar"]

        paper = globalPropPool.getProp("shredder-paper")
        shredder = globalPropPool.getProp("shredder")
        particleEffect = BattleParticles.createParticleEffect("Shred")
        suitTrack = self.getSuitTrack(playRate=self.PLAY_RATE)
        particleNode = self.battle.attachNewNode('shred-particle-node')
        particleNode.setPos(self.battle.getActorPosHpr(self.invoker)[0])
        particleNode.headsUp(toon)
        particleNode.setBin('fixed', 1)

        partTrack = Sequence(
            self.getPartTrack(
                particleEffect, 3.4/self.PLAY_RATE, 2.9/self.PLAY_RATE, [particleEffect, particleNode, 0], softStop=-1.3
            ),
            Func(particleNode.removeNode),
        )
        paperPosPoints = [Point3(0.40, 0.11, 0.81), VBase3(79.224, 32.576, 179.449)]
        paperPropTrack = Parallel(
            self.getPropTrack(
                paper,
                self.invoker.getRightHand(),
                paperPosPoints,
                2.2/self.PLAY_RATE,
                1e-08,
                scaleUpTime=0.2/self.PLAY_RATE,
                anim=1,
                propName="shredder-paper",
                animDuration=2.5/self.PLAY_RATE,
                animStartTime=2.1/self.PLAY_RATE,
            ),
            Sequence(
                Wait(3.55/self.PLAY_RATE),
                Parallel(
                    LerpScaleInterval(paper, 0.9, 0.01),
                    LerpPosInterval(paper, 0.9, (-0.5, 0.11, 0.21)),
                ),
            ),
        )
        shredderPosPoints = [Point3(0.1089, 0.2976, -0.0314), VBase3(91.5032, -180, 1.64)]
        shredderPropTrack = self.getPropTrack(
            shredder,
            self.invoker.getLeftHand(),
            shredderPosPoints,
            0.7/self.PLAY_RATE,
            3.3/self.PLAY_RATE,
            scaleUpPoint=Point3(1.1476, 1.4, 1.0656),
            scaleUpTime=0.5/self.PLAY_RATE,
            scaleDownTime=0.5/self.PLAY_RATE,
        )
        toonTrack = self.getToonTrack(
            suitTrack.getDuration() - (1.5/self.PLAY_RATE),
            ["cringe"],
            suitTrack.getDuration() - (3.1/self.PLAY_RATE),
            ["duck"],
            damageAnimPlayRate=1.3,
            dodgeAnimPlayRate=1.2,
        )
        soundTrack = self.getSoundTrack("SA_shred.ogg", delay=3.4/self.PLAY_RATE, node=self.invoker)
        return Parallel(
            suitTrack,
            paperPropTrack,
            shredderPropTrack,
            partTrack,
            toonTrack,
            soundTrack,
        )


@AttackClass(attackType=AttackEnum.SONG_AND_DANCE)
class SongAndDance(SuitGroupAttack):
    ANIM_NAME = "song-and-dance"
    OPEN_SHOT_DUR = 4.1

    def doAttack(self):
        damageDelay = 4.2
        suitTrack = self.getSuitAnimTrack()
        toonTracks = self.getToonTracks(
            damageDelay, ["cringe"], damageDelay, ["applause"], damageAnimPlayRate=1.2,
        )
        soundTrack = self.getSoundTrack("AA_heal_happydance.ogg", node=self.invoker)
        return Parallel(suitTrack, toonTracks, soundTrack)


@AttackClass(attackType=AttackEnum.SPIN)
class Spin(SuitSingleAttack):
    ANIM_NAME = "magic3"
    PLAY_RATE = 1.1
    OPEN_SHOT_DUR = 1.7/PLAY_RATE

    def doAttack(self):
        target = self.targetDicts[0]
        toon = target["avatar"]
        damageDelay = 1.7/self.PLAY_RATE
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
        suitTrack = self.getSuitTrack()
        sprayTrack = self.getPartTrack(
            sprayEffect, 1.0, 1.9, [sprayEffect, self.invoker, 0]
        )
        spinTrack1 = self.getPartTrack(
            spinEffect1, 2.1, 3.75/self.PLAY_RATE, [spinEffect1, self.battle, 0]
        )
        spinTrack2 = self.getPartTrack(
            spinEffect2, 2.1, 3.75/self.PLAY_RATE, [spinEffect2, self.battle, 0]
        )
        spinTrack3 = self.getPartTrack(
            spinEffect3, 2.1, 3.75/self.PLAY_RATE, [spinEffect3, self.battle, 0]
        )
        damageAnims = [["duck", 0.01, 0.01, 1.1]]
        damageAnims.extend(self.getSplicedLerpAnims("think", 0.66, 1.1, startTime=2.26))
        damageAnims.extend(self.getSplicedLerpAnims("think", 0.66, 1.0, startTime=2.26))
        toonTrack = self.getToonTrack(
            damageDelay=damageDelay,
            splicedDamageAnims=damageAnims,
            dodgeDelay=0.91,
            dodgeAnimNames=["sidestep"],
            showDamageExtraTime=2.1,
            showMissedExtraTime=1.0,
            dodgeAnimPlayRate=1.2,
        )
        if target["landed"]:
            toonSpinTrack = Sequence(
                Wait(damageDelay + (0.9/self.PLAY_RATE)),
                LerpHprInterval(toon, 0.65/self.PLAY_RATE, Point3(-10, 0, 0)),
                LerpHprInterval(toon, 0.45/self.PLAY_RATE, Point3(-30, 0, 0)),
                LerpHprInterval(toon, 0.15/self.PLAY_RATE, Point3(-60, 0, 0)),
                LerpHprInterval(toon, 0.65/self.PLAY_RATE, Point3(-700, 0, 0)),
                LerpHprInterval(toon, 0.95/self.PLAY_RATE, Point3(-1310, 0, 0)),
                LerpHprInterval(toon, 0.35/self.PLAY_RATE, toon.getHpr()),
                Wait(0.45/self.PLAY_RATE),
            )
            soundTrack = self.getSoundTrack(
                "tt_s_ara_cfg_toonInWhirlwind.ogg",
                delay=damageDelay + (0.9/self.PLAY_RATE),
                node=self.invoker,
            )
            return Parallel(
                suitTrack,
                sprayTrack,
                toonTrack,
                toonSpinTrack,
                soundTrack,
                spinTrack1,
                spinTrack2,
                spinTrack3,
            )
        else:
            return Parallel(suitTrack, sprayTrack, toonTrack)


@AttackClass(attackType=AttackEnum.SYNERGY)
class Synergy(SuitGroupAttack):
    ANIM_NAME = "magic3"
    OPEN_SHOT_DUR = 1.7

    def doAttack(self):
        damageDelay = 1.7
        hitAtleastOneToon = 0
        for t in self.targetDicts:
            if t["landed"]:
                hitAtleastOneToon = 1

        particleEffect = BattleParticles.createParticleEffect("Synergy")
        waterfallEffect = BattleParticles.createParticleEffect(file="synergyWaterfall")
        suitTrack = self.getSuitAnimTrack()
        partTrack = self.getPartTrack(
            particleEffect, 1.0, 1.9, [particleEffect, self.invoker, 0]
        )
        waterfallTrack = self.getPartTrack(
            waterfallEffect, 0.8, 1.9, [waterfallEffect, self.invoker, 0]
        )
        dodgeAnims = []
        dodgeAnims.append(["jump", 0.01, 0, 0.6])
        dodgeAnims.extend(self.getSplicedLerpAnims("jump", 0.31, 1.3, startTime=0.6))
        dodgeAnims.append(["jump", 0, 0.91])
        toonTracks = self.getToonTracks(
            damageDelay=damageDelay,
            damageAnimNames=["slip-forward"],
            dodgeDelay=0.91,
            splicedDodgeAnims=dodgeAnims,
            showMissedExtraTime=1.0,
        )
        synergySoundTrack = Sequence(
            Wait(0.9),
            SoundInterval(
                globalBattleSoundCache.getSound("SA_synergy.ogg"), node=self.invoker
            ),
        )
        if hitAtleastOneToon == 1:
            fallingSoundTrack = Sequence(
                Wait(damageDelay + 0.5),
                SoundInterval(
                    globalBattleSoundCache.getSound("Toon_bodyfall_synergy.ogg"),
                    node=self.invoker,
                    volume=0.8
                ),
            )
            return Parallel(
                suitTrack,
                partTrack,
                waterfallTrack,
                synergySoundTrack,
                fallingSoundTrack,
                toonTracks,
            )
        else:
            return Parallel(
                suitTrack, partTrack, waterfallTrack, synergySoundTrack, toonTracks
            )


@AttackClass(attackType=AttackEnum.TABULATE)
class Tabulate(Audit):
    Particle1 = "audit-plus"
    Particle2 = "audit-minus"
    Particle3 = "audit-mult"
    Particle4 = 'audit-div'
    Particle5 = 'audit-one'
    SoundPath = 'SA_tabulate.ogg'


@AttackClass(attackType=AttackEnum.TEE_OFF)
class TeeOff(SuitSingleAttack):
    ANIM_NAME = "golf-club-swing"
    OPEN_SHOT_DUR = 2.9
    PLAY_RATE = 1.4
    HitDelay = 3.75
    ToonHitDelay = 4.35
    ToonDodgeDelay = 1.4
    ToonHitAnim = 'slip-backward'
    HP_TEXT_TYPE = None
    BallXMult = 1.56
    BallYMult = 0.753
    BallPos = {
        "ym": [Point3(2.25*BallXMult, 2.25*BallYMult, 0.1)],
        "autocad": [Point3(2.35*BallXMult, 2.35*BallYMult, 0.1)],
        "mi": [Point3(3.2*BallXMult, 3.2*BallYMult, 0.1)],
        "mh": [Point3(4.2*BallXMult, 4.2*BallYMult, 0.1)],
        "rb": [Point3(4.2*BallXMult, 4.2*BallYMult, 0.1)],
        "tbc": [Point3(4.2*BallXMult, 4.2*BallYMult, 0.1)],
        "mg": [Point3(4.1*BallXMult, 4.1*BallYMult, 0.1)],
        "hho": [Point3(4.2*BallXMult, 4.2*BallYMult, 0.1)],
        "clubpres": [Point3(4.5*BallXMult, 4.5*BallYMult, 0.1)],
        "ftf_c": [Point3(4.5*BallXMult, 4.5*BallYMult, 0.1)],
        "ftf_c_ac": [Point3(4.5*BallXMult, 4.5*BallYMult, 0.1)],
    }

    def doAttack(self):
        suitTrack = self.getSuitTrack(playRate=self.PLAY_RATE)
        soundTrack = self.getSoundTrack("SA_tee_off.ogg", delay=self.HitDelay / self.PLAY_RATE, node=self.invoker)
        club = globalPropPool.getProp("golf-club")

        clubPosPoints = [Point3(0.2724, 3.4425, 0.5446), VBase3(-1.3617, 60.5138, -84.6605)]
        clubPropTrack = self.getPropTrack(
            club,
            self.invoker.getRightHand(),
            clubPosPoints,
            0.7 / self.PLAY_RATE,
            (self.HitDelay + 1.3) / self.PLAY_RATE,
            Point3(1, 1, 1),
            scaleUpTime=0.15/self.PLAY_RATE,
            scaleDownTime=0.15/self.PLAY_RATE,
        )

        globalParallel = Parallel()
        for target in self.targetDicts:
            toon = target["avatar"]
            ball = globalPropPool.getProp("golf-ball")

            ballPosPoints = self.BallPos.get(self.invoker.dna.name, [Point3(2.1, 0, 0.1)])
            ballPropTrack = Sequence(
                self.getPropAppearTrack(
                    ball, self.invoker, ballPosPoints, 1.7/self.PLAY_RATE, Point3(1.5, 1.5, 1.5)
                ),
                Func(self.battle.movie.needRestoreRenderProp, ball),
                Func(ball.wrtReparentTo, render),
                Wait((self.HitDelay-1.95)/self.PLAY_RATE),
            )
            missPoint = lambda ball=ball, toon=toon: self.toonMissPoint(ball, toon)
            ballPropTrack.append(
                self.getPropThrowTrack(ball, [self.toonFacePoint(toon)], [missPoint], hitDuration=0.3/self.PLAY_RATE, missDuration=0.5/self.PLAY_RATE)
            )
            ballPropTrack.append(Func(self.battle.movie.clearRenderProp, ball))
            toonTrack = self.getToonTrack(
                self.ToonHitDelay/self.PLAY_RATE,
                [self.ToonHitAnim],
                self.ToonDodgeDelay/self.PLAY_RATE,
                ["duck"],
                showMissedExtraTime=1.7/self.PLAY_RATE,
                target=target,
                hpTextType=self.HP_TEXT_TYPE,
                dodgeAnimPlayRate=1.1,
                damageAnimPlayRate=1.1,
            )
            globalParallel.append(Parallel(toonTrack, ballPropTrack))

        return Parallel(suitTrack, clubPropTrack, soundTrack, globalParallel)


@AttackClass(attackType=AttackEnum.THROW_BOOK)
class ThrowBook(SuitSingleAttack):
    ANIM_NAME = "throw-object"
    PLAY_RATE = 1.25
    OPEN_SHOT_DUR = 2.9/PLAY_RATE

    def doAttack(self):
        target = self.targetDicts[0]
        toon = target["avatar"]
        suitDelay = 2.0/self.PLAY_RATE
        propDelay = 0.6/self.PLAY_RATE
        throwDuration = 1.5/self.PLAY_RATE
        paper = globalPropPool.getProp("lawbook")
        suitTrack = self.getSuitTrack(playRate=self.PLAY_RATE)
        posPoints = [Point3(-0.4, 0.0, -0.075), VBase3(180, 180, 0)]
        paperTrack = Sequence(
            self.getPropAppearTrack(
                paper,
                self.invoker.getRightHand(),
                posPoints,
                propDelay,
                Point3(1.95, 1.95, 1.95),
                scaleUpTime=0.5/self.PLAY_RATE,
            )
        )
        paperTrack.append(Wait(suitDelay))
        hitPoint = toon.getPos(self.battle)
        hitPoint.setX(hitPoint.getX())
        hitPoint.setY(hitPoint.getY())
        if target["landed"]:
            hitPoint.setZ(hitPoint.getZ() + 1.1)
        movePoint = Point3(
            hitPoint.getX(), hitPoint.getY() - 1.8, hitPoint.getZ() + 0.2
        )
        paperTrack.append(Func(self.battle.movie.needRestoreRenderProp, paper))
        paperTrack.append(Func(paper.wrtReparentTo, self.battle))
        paperTrack.append(
            self.getThrowTrack(
                paper, hitPoint, duration=throwDuration, parent=self.battle
            )
        )
        paperTrack.append(Wait(0.6/self.PLAY_RATE))
        paperTrack.append(LerpPosInterval(paper, 0.4/self.PLAY_RATE, movePoint))
        spinTrack = Sequence(
            Wait(propDelay + suitDelay + (0.2/self.PLAY_RATE)),
            LerpHprInterval(paper, throwDuration, Point3(-540, 0, 0)),
        )
        sizeTrack = Sequence(
            Wait(propDelay + suitDelay + (0.2/self.PLAY_RATE)),
            LerpScaleInterval(paper, throwDuration, Point3(6, 6, 6)),
            Wait(0.65/self.PLAY_RATE),
            LerpScaleInterval(paper, 0.4/self.PLAY_RATE, MovieUtil.PNT3_NEARZERO),
        )
        propTrack = Sequence(
            Parallel(paperTrack, spinTrack, sizeTrack),
            Func(MovieUtil.removeProp, paper),
            Func(self.battle.movie.clearRenderProp, paper),
        )
        damageAnims = [
            ["cringe", 0.01, 0.21, 0.08],
            ["slip-forward", 0.01, 0.6, 0.85],
            ["slip-forward", 0.01, 1.51]
        ]
        toonTrack = self.getToonTrack(
            damageDelay=4.35/self.PLAY_RATE,
            splicedDamageAnims=damageAnims,
            dodgeDelay=2.4/self.PLAY_RATE,
            dodgeAnimNames=["sidestep"],
            showDamageExtraTime=0.4,
            showMissedExtraTime=1.3,
            damageAnimPlayRate=1.25,
            dodgeAnimPlayRate=1.2,
        )
        soundTrack = self.getSoundTrack(
            "SA_throw_book.ogg", delay=0.4, node=self.invoker
        )
        return Parallel(suitTrack, toonTrack, soundTrack, propTrack)


@AttackClass(attackType=AttackEnum.TREMOR)
class Tremor(SuitGroupAttack):
    ANIM_NAME = "stomp"

    def doAttack(self):
        suitTrack = self.getSuitAnimTrack()
        damageAnims = [["slip-forward"], ["slip-forward", 0.01]]
        dodgeAnims = [["jump"], ["jump", 0.01]]
        toonTracks = self.getToonTracks(
            damageDelay=1.1,
            splicedDamageAnims=damageAnims,
            dodgeDelay=0.7,
            splicedDodgeAnims=dodgeAnims,
            showMissedExtraTime=2.8,
            showDamageExtraTime=1.1,
        )
        soundTrack = self.getSoundTrack("SA_tremor.ogg", delay=0.9, node=self.invoker)
        return Parallel(suitTrack, soundTrack, toonTracks)

    def getCameraShot(self, duration):
        extraDelay = 0.0
        if self.shownUnlureMovie:
            extraDelay = 0.6
        shakeIntensity = 0.25
        return self.camera.suitCameraShakeShot(duration, shakeIntensity, extraDelay=extraDelay)


@AttackClass(attackType=AttackEnum.WATERCOOLER)
class Watercooler(SuitSingleAttack):
    ANIM_NAME = "watercooler"

    def doAttack(self):
        suitTrack = self.getSuitAnimTrack()
        allToonTracks = Parallel()
        watercooler = globalPropPool.getProp("watercooler")
        posPoints = [Point3(0.48, 0.2462, 0.0332), VBase3(90, 0, 180)]

        propTrackSprayTracks = Parallel()
        propTrack = self.getPropTrack(
            watercooler,
            self.invoker.getLeftHand(),
            posPoints,
            appearDelay=0,
            remainDelay=0,
            scaleUpTime=0,
            scaleDownTime=0,
            anim=1,
            propName="watercooler",
            animDuration=watercooler.getDuration("watercooler"),
        )

        globalSpraySoundTrack = Sequence(
            Wait(1.1),
            SoundInterval(
                    globalBattleSoundCache.getSound("SA_watercooler_appear_only.ogg"),
                    node=self.invoker,
                    duration=1.4722,
            )
        )

        def getCoolerSpout(watercooler=watercooler):
            spout = watercooler.find("**/Dispenser")
            return render.getRelativePoint(spout, (0, 0.4, 0))

        for target in self.targetDicts:
            toon = target["avatar"]

            if target['landed']:
                hitPoint = lambda toon=toon: self.toonFacePoint(toon)
                hitSprayTrack = MovieUtil.getSprayTrack(
                    self.battle,
                    Point4(0.75, 0.75, 1.0, 0.8),
                    getCoolerSpout,
                    hitPoint,
                    0.2,
                    0.2,
                    0.2,
                    horizScale=0.3,
                    vertScale=0.3,
                )
                propTrackSprayTracks.append(hitSprayTrack)
            else:
                missPoint = self.getWatercoolerMissPoint(watercooler, toon)
                missSprayTrack = MovieUtil.getSprayTrack(
                    self.battle,
                    Point4(0.75, 0.75, 1.0, 0.8),
                    getCoolerSpout,
                    missPoint,
                    0.2,
                    0.2,
                    0.2,
                    horizScale=0.3,
                    vertScale=0.3,
                )
                propTrackSprayTracks.append(missSprayTrack)

            splashTrack = Sequence()
            if target['landed']:

                def prepSplash(splash, targetPoint):
                    splash.reparentTo(render)
                    splash.setPos(targetPoint)
                    scale = splash.getScale()
                    splash.setBillboardPointWorld()
                    splash.setScale(scale)

                splash = globalPropPool.getProp("splash-from-splat")
                splash.setColor(0.75, 0.75, 1, 0.8)
                splash.setScale(0.3)
                splashTrack = Sequence(
                    Func(self.battle.movie.needRestoreRenderProp, splash),
                    Wait(3.2),
                    Func(prepSplash, splash, self.toonFacePoint(toon)),
                    ActorInterval(splash, "splash-from-splat"),
                    Func(MovieUtil.removeProp, splash),
                    Func(self.battle.movie.clearRenderProp, splash),
                )
            toonTrack = self.getWatercoolerToonTracks(suitTrack, target)
            soundTrack = Sequence(
                Wait(1.1 + 1.4722 + 0.4),
                SoundInterval(
                    globalBattleSoundCache.getSound("SA_watercooler_spray_only.ogg"),
                    node=self.invoker,
                    duration=2.313,
                ),
            )
            allToonTracks.append(Parallel(toonTrack, soundTrack, splashTrack))

        propTrack = Sequence(
            Parallel(
                propTrack,
                Sequence(
                    Wait(3.05),
                    propTrackSprayTracks,
                ),
            ),

            Wait(0.01),
            LerpScaleInterval(watercooler, 0.3, MovieUtil.PNT3_NEARZERO),
            Func(MovieUtil.removeProp, watercooler),
        )
        return Parallel(suitTrack, allToonTracks, propTrack, globalSpraySoundTrack)

    def getWatercoolerToonTracks(self, suitTrack, target):
        return self.getToonTrack(
            suitTrack.getDuration() - 1.5,
            ["cringe"],
            2.25,
            ["sidestep"],
            target=target,
            damageAnimPlayRate=1.15,
            dodgeAnimPlayRate=1.2,
        )

    def getWatercoolerMissPoint(self, watercooler, toon):
        return lambda prop=watercooler, toon=toon: self.toonMissPoint(
            prop, toon, 0, parent=render
        )


@AttackClass(attackType=(AttackEnum.WATERCOOLER_DOUBLE, AttackEnum.WATERCOOLER_GROUP))
class WatercoolerGroup(Watercooler):
    def getWatercoolerToonTracks(self, suitTrack, target):
        # Slight variant to the dodge track that has them jump over the beam
        # This is to avoid weird stuff with multiple toons doing a sidestep at the same time
        dodgeAnims = [["jump", 0.01, 0, 0.6]]
        dodgeAnims.extend(self.getSplicedLerpAnims("jump", 0.31, 1.3, startTime=0.6))
        dodgeAnims.append(["jump", 0, 0.91])
        return self.getToonTrack(
            suitTrack.getDuration() - 1.5,
            ["cringe"],
            2.25,
            splicedDodgeAnims=dodgeAnims,
            target=target,
            damageAnimPlayRate=1.15,
        )

    def getWatercoolerMissPoint(self, watercooler, toon):
        # Change the water spray to point more towards the ground in case of a miss
        return watercooler.getRelativePoint(toon, (0, -2.0, 0.1))


@AttackClass(attackType=AttackEnum.WITHDRAWAL)
class Withdrawal(SuitSingleAttack):
    ANIM_NAME = "magic1"
    OPEN_SHOT_DUR = 1.2

    def doAttack(self):
        target = self.targetDicts[0]
        toon = target["avatar"]
        BattleParticles.loadParticles()
        particleEffect = BattleParticles.createParticleEffect("Withdrawal")
        BattleParticles.setEffectTexture(particleEffect, "snow-particle")
        suitTrack = self.getSuitAnimTrack()
        partTrack = self.getPartTrack(
            particleEffect,
            1e-05,
            suitTrack.getDuration() + 1.2,
            [particleEffect, self.invoker, 0],
        )
        toonTrack = self.getToonTrack(
            1.2,
            ["cringe"],
            0.2,
            splicedDodgeAnims=[["duck", 1e-05, 0.8]],
            showMissedExtraTime=0.8,
        )
        headParts = toon.getHeadParts()
        torsoParts = toon.getTorsoParts()
        legsParts = toon.getLegsParts()

        def changeColor(parts):
            track = Parallel()
            for nextPart in parts:
                track.append(Func(nextPart.setColorScale, Vec4(0, 0, 0, 1)))

            return track

        def resetColor(parts):
            track = Parallel()
            for nextPart in parts:
                track.append(Func(nextPart.clearColorScale))

            return track

        soundTrack = self.getSoundTrack(
            "SA_withdrawl.ogg", delay=1.4, node=self.invoker
        )
        if target["landed"]:
            colorTrack = Sequence()
            colorTrack.append(Wait(1.6))
            colorTrack.append(Func(self.battle.movie.needRestoreColor))
            colorTrack.append(
                Parallel(
                    changeColor(headParts),
                    changeColor(torsoParts),
                    changeColor(legsParts),
                )
            )
            colorTrack.append(Wait(2.9))
            colorTrack.append(resetColor(headParts))
            colorTrack.append(resetColor(torsoParts))
            colorTrack.append(resetColor(legsParts))
            colorTrack.append(Func(self.battle.movie.clearRestoreColor))
            return Parallel(suitTrack, partTrack, toonTrack, soundTrack, colorTrack)
        else:
            return Parallel(suitTrack, partTrack, toonTrack, soundTrack)


@AttackClass(attackType=AttackEnum.WRITE_OFF)
class WriteOff(SuitSingleAttack):
    ANIM_NAME = "hold-pencil"
    PLAY_RATE = 1.1
    OPEN_SHOT_DUR = (65/24)/PLAY_RATE

    def doAttack(self):
        target = self.targetDicts[0]
        toon = target["avatar"]
        pad = globalPropPool.getProp("pad")
        pencil = globalPropPool.getProp("pencil")
        BattleParticles.loadParticles()
        checkmark = MovieUtil.copyProp(BattleParticles.getParticle("checkmark"))
        checkmark.setBillboardPointEye()
        suitTrack = self.getSuitTrack(playRate=self.PLAY_RATE)
        padPosPoints = [Point3(-0.2704, 1.2162, -0.1285), VBase3(1.4371, -8.5398, -180.7844)]
        padPropTrack = self.getPropTrack(
            pad,
            self.invoker.getLeftHand(),
            padPosPoints,
            0.5/self.PLAY_RATE,
            2.57/self.PLAY_RATE,
            Point3(1.89, 1.89, 1.89),
            scaleUpTime=0.25/self.PLAY_RATE,
            scaleDownTime=0.25/self.PLAY_RATE,
        )
        missPoint = lambda checkmark=checkmark, toon=toon: self.toonMissPoint(
            checkmark, toon
        )
        pencilPosPoints = [Point3(-0.57, 1.08, 0.08), VBase3(21.045, 12.702, -176.374)]
        extraArgsForShowProp = [pencil, self.invoker.getRightHand()]
        extraArgsForShowProp.extend(pencilPosPoints)
        pencilPropTrack = Sequence(
            Wait(0.5/self.PLAY_RATE),
            Func(self.showProp, *extraArgsForShowProp),
            LerpScaleInterval(
                pencil, 0.25/self.PLAY_RATE, Point3(1.5, 1.5, 1.5), startScale=Point3(0.01)
            ),
            Wait(2.25/self.PLAY_RATE),
            Func(self.battle.movie.needRestoreRenderProp, checkmark),
            Func(checkmark.reparentTo, render),
            Func(checkmark.setScale, 1.6),
            Func(checkmark.setPosHpr, pencil, 0, 0, 0, 0, 0, 0),
            Func(checkmark.setP, 0),
            Func(checkmark.setR, 0),
        )
        pencilPropTrack.append(
            self.getPropThrowTrack(checkmark, [self.toonFacePoint(toon)], [missPoint],
                                   hitDuration=0.5/self.PLAY_RATE, missDuration=0.5/self.PLAY_RATE)
        )
        pencilPropTrack.append(Func(MovieUtil.removeProp, checkmark))
        pencilPropTrack.append(Func(self.battle.movie.clearRenderProp, checkmark))
        pencilPropTrack.append(Wait(0.3/self.PLAY_RATE))
        pencilPropTrack.append(LerpScaleInterval(pencil, 0.25/self.PLAY_RATE, MovieUtil.PNT3_NEARZERO))
        pencilPropTrack.append(Func(MovieUtil.removeProp, pencil))
        toonTrack = self.getToonTrack(
            3.4/self.PLAY_RATE, ["slip-forward"], 2.4/self.PLAY_RATE, ["sidestep"],
            damageAnimPlayRate=1.1, dodgeAnimPlayRate=1.2,
        )
        soundTrack = Sequence(
            Wait(2.1/self.PLAY_RATE),
            SoundInterval(
                globalBattleSoundCache.getSound("SA_writeoff_pen_only.ogg"),
                duration=0.9,
                node=self.invoker,
            ),
            SoundInterval(
                globalBattleSoundCache.getSound("SA_writeoff_ding_only.ogg"),
                node=self.invoker,
            ),
        )
        return Parallel(suitTrack, toonTrack, padPropTrack, pencilPropTrack, soundTrack)
