import random

from panda3d.core import Vec4, Point3, TextNode, VBase3
from toontown.chat.constants.ChatGlobals import  CFSpeech, CFTimeout
from direct.interval.IntervalGlobal import *

from toontown.clashbattle.battle import BattleParticles, MovieUtil
from toontown.clashbattle.battle.BattleProps import globalPropPool
from toontown.clashbattle.battle.attacks.base.AttackEnum import AttackEnum
from toontown.clashbattle.battle.attacks.client.Attack import Attack
from toontown.clashbattle.battle.attacks.client.AttackRepository import AttackClass
from toontown.clashbattle.battle.attacks.client.suit.SuitGroupAttack import SuitGroupAttack
from toontown.clashbattle.battle.attacks.client.suit.SuitSingleAttack import SuitSingleAttack
from toontown.clashbattle.battle.visuals.VisualEffectEnums import VisualEffectEnum
from toontown.toonbase import TTLocalizer, ToontownGlobals, ToontownIntervals


@AttackClass(attackType=(AttackEnum.REFINEMENT, AttackEnum.REFINEMENT_DIRECTORS))
class Refinement(SuitSingleAttack):
    ANIM_NAME = "throw-object"
    CHEAT = True
    OPEN_SHOT_DUR = 6.5

    def doAttack(self):
        healer = self.invoker
        damageDelay = 5.25
        suitTrack = self.getSuitAnimTrack()
        healTracks = Parallel()

        oilCan = loader.loadModel("phase_12/models/bossbotHQ/canoffood")
        oilCans = []

        def updateSuitHP(suit, response, heal):
            suit.updateHealthBar(heal)
            if heal != 0:
                suit.showHpText(heal)
            if suit != healer:
                suit.setChatAbsolute(response, CFSpeech | CFTimeout)

        def removeOilCans():
            for oil in oilCans:
                oil.removeNode()

        for suit in self.targetObjs:
            result = self.findTarget(suit.doId)
            can = oilCan.copyTo(healer.getRightHand())
            tray = can.find("**/tray")
            if not tray.isEmpty():
                tray.hide()
            can.setScale(0.01)
            can.setPos(0, 0, 0)
            can.setH(180)
            can.setR(180)
            oilCans.append(can)
            endPos = (0, 0, suit.height + 3)
            scaleSeq = LerpScaleInterval(can, duration=1, scale=0.7)
            pInterval = Sequence(
                Func(can.wrtReparentTo, suit),
                Parallel(
                    ProjectileInterval(
                        can, duration=1.65, endPos=endPos, gravityMult=0.4
                    ),
                    LerpHprInterval(can, 1.65, (180, 0, 0)),
                ),
            )
            endScaleSeq = LerpScaleInterval(can, duration=0.65, scale=0.01)
            fallInterval = LerpPosInterval(can, 0.65, (0, 0, suit.height / 2))
            response = random.choice(TTLocalizer.MovieSuitHealResponses)
            oilGlug = self.getSoundTrack(
                "SA_refinement.ogg", delay=0, node=self.invoker
            )
            seq = Sequence(
                scaleSeq,
                Wait(2.15),
                Parallel(
                    Sequence(pInterval, Parallel(endScaleSeq, fallInterval)), oilGlug
                ),
            )

            seq.append(Func(updateSuitHP, suit, response, result.hpAdjust))

            healTracks.append(seq)
        sfx = loader.loadSfx("phase_11/audio/sfx/LB_toonup.ogg")
        repairSoundTrack = Sequence(Wait(damageDelay), SoundInterval(sfx, node=healer))
        return Sequence(
            Parallel(
                Sequence(suitTrack, Func(healer.loop, "neutral")),
                repairSoundTrack,
                healTracks,
            ),
            Func(removeOilCans),
        )


@AttackClass(attackType=(AttackEnum.INK_DRAIN, AttackEnum.INK_DRAIN_DIRECTORS))
class InkDrain(SuitSingleAttack):
    ANIM_NAME = "effort"
    CHEAT = True
    OPEN_SHOT_DUR = 1.6

    def getAnimName(self):
        if self.invoker.style.body == 'a':
            return "magic1"
        return self.ANIM_NAME

    def doAttack(self):
        suitTrack = self.getSuitAnimTrack()

        # Making Red, Green and Blue particles
        BattleParticles.loadParticles()
        particleEffectRed = BattleParticles.createParticleEffect("Withdrawal")
        BattleParticles.setEffectTexture(
            particleEffectRed, "snow-particle", color=Vec4(1.0, 0.6, 0.6, 1)
        )
        particle = particleEffectRed.getParticlesNamed("particles-1")
        particle.setBirthRate(0.0600)
        particleEffectGreen = BattleParticles.createParticleEffect("Withdrawal")
        BattleParticles.setEffectTexture(
            particleEffectGreen, "snow-particle", color=Vec4(0.6, 1.0, 0.6, 1)
        )
        particle = particleEffectGreen.getParticlesNamed("particles-1")
        particle.setBirthRate(0.0600)
        particleEffectBlue = BattleParticles.createParticleEffect("Withdrawal")
        BattleParticles.setEffectTexture(
            particleEffectBlue, "snow-particle", color=Vec4(0.6, 0.6, 1.0, 1)
        )
        particle = particleEffectBlue.getParticlesNamed("particles-1")
        particle.setBirthRate(0.0600)

        partTracks = Parallel()
        partTracks.append(
            self.getPartTrack(
                particleEffectRed,
                1e-05,
                suitTrack.getDuration() + 1.2,
                [particleEffectRed, self.invoker, 0],
            )
        )
        partTracks.append(
            self.getPartTrack(
                particleEffectGreen,
                1e-05,
                suitTrack.getDuration() + 1.26,
                [particleEffectGreen, self.invoker, 0],
            )
        )
        partTracks.append(
            self.getPartTrack(
                particleEffectBlue,
                1e-05,
                suitTrack.getDuration() + 1.32,
                [particleEffectBlue, self.invoker, 0],
            )
        )

        def changeColor(parts):
            track = Parallel()
            for nextPart in parts:
                track.append(
                    LerpColorScaleInterval(
                        nextPart, duration=4.0, colorScale=Vec4(0.2, 0.2, 0.2, 1)
                    )
                )

            return track

        def resetColor(parts):
            track = Parallel()
            for nextPart in parts:
                track.append(Func(nextPart.clearColorScale))

            return track

        soundTrack = self.getSoundTrack("SA_ink_drain.ogg", delay=0, node=self.invoker)

        toonTracks = Parallel()
        for toon in self.battle.activeToons:
            # Get Toon Info
            headParts = toon.getHeadParts()
            torsoParts = toon.getTorsoParts()
            legsParts = toon.getLegsParts()

            # Toon Reaction
            reactionTrack = Sequence()
            reactionTrack.append(
                Func(toon.headsUp, self.battle, self.invoker.getPos(self.battle))
            )
            reactionTrack.append(Wait(1.6))
            reactionTrack.append(ActorInterval(toon, "cringe", playRate=0.4))
            reactionTrack.append(Func(toon.loop, "neutral"))

            # Color
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
            colorTrack.append(Wait(1.4))
            # colorTrack.append(resetColor(headParts))
            # colorTrack.append(resetColor(torsoParts))
            # colorTrack.append(resetColor(legsParts))
            colorTrack.append(
                Func(MovieUtil.applyVisualEffect, toon, VisualEffectEnum.INK_DRAIN)
            )
            colorTrack.append(Func(self.battle.movie.clearRestoreColor))

            toonTracks.append(Parallel(reactionTrack, colorTrack))

        return Parallel(suitTrack, partTracks, toonTracks, soundTrack)

    def getCameraShot(self, duration):
        toons = []
        for toon in self.targetObjs:
            toons.append({"avatar": toon})
        return self.camera.randomGroupAttackCam(
            self.invoker, toons, self.battle, duration, self.OPEN_SHOT_DUR
        )


@AttackClass(attackType=AttackEnum.WORKERS_COMP)
class WorkersComp(SuitSingleAttack):
    ANIM_NAME = "frustrated"
    CHEAT = True
    OPEN_SHOT_DUR = 7.0

    def doAttack(self):
        cogsKilled, damageMult, *_ = self.extraArgs
        damageMult /= 100
        result = self.findTarget(self.invokerId)
        healHP = result.hpAdjust
        suitTrack = self.getSuitAnimTrack()
        suitTrack.append(Func(self.invoker.loop, "neutral"))

        dmgMult = str(round(damageMult**cogsKilled, 2))

        sfx = loader.loadSfx("phase_11/audio/sfx/LB_toonup.ogg")
        dmgMultSeq = Sequence(
            Func(base.playSfx, sfx),
            Func(
                self.invoker.showHpString,
                text=TTLocalizer.SuitAttackDmgMult % dmgMult,
                color=(0.45, 0.45, 1.0, 1.0),
            ),
        )

        if healHP > 0:
            hpText1 = Sequence(
                Func(base.playSfx, sfx), Func(self.updateSuitHP, self.invoker, healHP)
            )
            hpText2 = dmgMultSeq
        else:
            hpText1 = dmgMultSeq
            hpText2 = Sequence()

        return Sequence(
            Parallel(suitTrack, Sequence(Wait(1), hpText1, Wait(2), hpText2)), Wait(2)
        )

    def getAttackDisplayName(self):
        if len(self.extraArgs) <= 2:
            # the normal name for this attack
            return TTLocalizer.SuitAttackNames[self.attackType]
        else:
            # If extra extra args were passed, it is definitely from an overclocked foreman.
            # In this case, index 3 indicates intent.
            intent = self.extraArgs[3]
            return TTLocalizer.SuitAttackBonusPhrases[
                "workers_compensation"
            ][intent]

    def getAttackTaunt(self):
        if len(self.extraArgs) <= 2:
            taunts = TTLocalizer.SuitAttackTaunts.get(
                self.attackType, TTLocalizer.SuitAttackDefaultTaunts
            )
            if self.taunt[0] >= len(taunts):
                return TTLocalizer.SuitAttackDefaultTaunts[0]
        else:
            # If extra extra args were passed, it is definitely from an overclocked foreman.
            # In this case, index 2 is the amount of new procs, and index 3 indicates intent.
            intent = self.extraArgs[3]
            return random.choice(
                TTLocalizer.SuitAttackBonusTaunts["workers_compensation"][
                    intent
                ]
            )
        return taunts[self.taunt[0]]


@AttackClass(attackType=(AttackEnum.LIFE_INSURANCE, AttackEnum.FTF_SUPERVISOR_LIFE_INSURANCE))
class LifeInsurance(Attack):
    ANIM_NAME = "victory"
    CHEAT = True
    OPEN_SHOT_DUR = 7.0

    def doAttack(self):
        startingHP = self.invoker.getHp()
        result = self.findTarget(self.invoker.doId)
        healHP = result.hpAdjust
        suitTrack = self.getSuitAnimTrack()
        hpNode = self.invoker.attachNewNode("hpNode")
        self.hpTextNode = None

        registerSfx = self.getSoundTrack(
            "SA_life_insurance_register.ogg", delay=0, node=self.invoker
        )
        coinLoop = self.getSoundTrack(
            "SA_life_insurance_loop.ogg", delay=0, node=self.invoker
        )

        def showHpText(number, scale=1):
            self.invoker.HpTextGenerator.setFont(ToontownGlobals.getSignFont())
            self.invoker.HpTextGenerator.setText("+" + str(number))
            self.invoker.HpTextGenerator.clearShadow()
            self.invoker.HpTextGenerator.setAlign(TextNode.ACenter)
            r = 0
            g = 0.9
            b = 0
            a = 1
            self.invoker.HpTextGenerator.setTextColor(r, g, b, a)
            if self.hpTextNode:
                self.hpTextNode.removeNode()
            self.hpTextNode = self.invoker.HpTextGenerator.generate()
            self.hpTextNode = hpNode.attachNewNode(self.hpTextNode)
            self.hpTextNode.setScale(scale)
            self.hpTextNode.setBillboardPointEye()
            self.hpTextNode.setBin("fixed", 100)

        hpMoveSeq = Sequence(
            hpNode.posInterval(
                1.0,
                Point3(0, 0, self.invoker.height + 1.5),
                startPos=(0, 0, self.invoker.height / 2),
                blendType="easeOut",
            ),
            Wait(0.85),
            hpNode.colorInterval(0.5, Vec4(0, 0.9, 0, 0)),
            Func(hpNode.removeNode),
        )

        def updateSuitHP(hp):
            showHpText(int(hp - startingHP))

        def bounceHpText():
            if hpNode:
                name = "hpTextBoing"
                ToontownIntervals.start(
                    ToontownIntervals.getPulseLargerIval(hpNode, name)
                )

        hpText = Parallel(
            Sequence(
                Func(self.invoker.updateHealthBar, healHP),
                Func(coinLoop.loop),
                LerpFunctionInterval(
                    updateSuitHP,
                    1.5,
                    fromData=startingHP,
                    toData=startingHP + healHP,
                    extraArgs=[],
                ),
                Func(coinLoop.finish),
                Parallel(Func(bounceHpText), registerSfx),
                Func(self.invoker.showHpString, 
                    text=TTLocalizer.SuitAttackDmgAdditive % str(int(self.extraArgs[0])), color=(0.45, 0.45, 1.0, 1.0)),
                Wait(0.5),
                registerSfx,
            ),
            hpMoveSeq,
        )

        return Sequence(
            Parallel(suitTrack, Sequence(Wait(1.5), Func(self.invoker.clearChat), hpText))
        )


@AttackClass(attackType=AttackEnum.OBJECTION)
class Objection(SuitSingleAttack):
    ANIM_NAME = "finger-wag"
    CHEAT = True
    OPEN_SHOT_DUR = 8.0

    def doAttack(self):
        taunt = self.modifyTauntString(self.getAttackTaunt())
        sfx = self.getSoundTrack("SA_objection.ogg", delay=0, node=self.invoker)
        tauntIval = Func(self.invoker.setChatAbsolute, taunt, CFSpeech | CFTimeout)
        objectionInto = ActorInterval(self.invoker, "objection-in")
        objectionLoop = ActorInterval(self.invoker, "objection-loop")
        objectionOut = ActorInterval(self.invoker, "objection-out")
        return Parallel(
            Sequence(
                objectionInto,
                tauntIval,
                Func(objectionLoop.loop),
                Wait(4.0),
                Func(self.invoker.clearChat),
                Func(objectionLoop.finish),
                objectionOut,
            ),
            sfx,
        )

    def getCameraShot(self, duration):
        return self.camera.heldRelativeHeadsUpShot(self.invoker, 8, 10, 8.5, self.invoker, duration, name='objectionHeldRelativeHeadsUpShot')

    def getAttackDisplayName(self) -> str:
        if self.invoker.dna.name == 'clerk':
            return TTLocalizer.SuitAttackNames.get(self.attackType, "")
        else:
            return TTLocalizer.SuitAttackBonusPhrases['objection'].get(self.invoker.dna.name, "")


@AttackClass(attackType=AttackEnum.OBJECTION_SUSTAINED)
class ObjectionSustained(SuitGroupAttack):
    ANIM_NAME = "magic1"
    CHEAT = True
    OPEN_SHOT_DUR = 1.0

    def doAttack(self):
        result = self.findTarget(self.invokerId)
        healHP = result.hpAdjust

        sfx = loader.loadSfx("phase_11/audio/sfx/LB_toonup.ogg")

        hpText = Sequence(
            Func(base.playSfx, sfx), Func(self.updateSuitHP, self.invoker, healHP)
        )

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
            Sequence(Wait(0.5), hpText),
            suitTrack,
            partTrack1,
            partTrack2,
            soundTrack,
            waterfallTrack,
            toonTracks,
        )


@AttackClass(attackType=AttackEnum.OBJECTION_OVERRULED)
class ObjectionOverruled(SuitSingleAttack):
    ANIM_NAME = "frustrated"
    CHEAT = True
    OPEN_SHOT_DUR = 6.0

    def doAttack(self):
        suitTrack = self.getSuitAnimTrack()
        sfx = self.getSoundTrack(
            "SA_objection_overruled.ogg", delay=0, node=self.invoker
        )
        return Parallel(suitTrack, sfx)


@AttackClass(attackType=(AttackEnum.EXTRA_TIP, AttackEnum.FTF_PRESIDENT_EXTRA_TIP))
class ExtraTip(SuitSingleAttack):
    ANIM_NAME = "throw-object"
    CHEAT = True
    OPEN_SHOT_DUR = 7.0

    def doAttack(self):
        autocaddie = self.targetObjs[0]
        result = self.findTarget(autocaddie.doId)
        healHP = result.hpAdjust
        suitTrack = self.getSuitAnimTrack()
        damageDelay = 5.25

        def updateSuitHP(response):
            autocaddie.updateHealthBar(healHP)
            if healHP != 0:
                autocaddie.showHpText(healHP)
            autocaddie.setChatAbsolute(response, CFSpeech | CFTimeout)

        check = globalPropPool.getProp("bonus-check")
        check.setScale(0.01)
        check.setPos(0.3, 0.5, -0.3)
        check.reparentTo(self.invoker.getRightHand())
        endPos = (0, 0, autocaddie.height + 3)
        scaleSeq = LerpScaleInterval(check, duration=1, scale=8.0)
        pInterval = Sequence(
            Func(check.wrtReparentTo, autocaddie),
            Parallel(
                ProjectileInterval(check, duration=1.65, endPos=endPos, gravityMult=0.4),
                LerpHprInterval(check, 1.65, (180, -90, 180)),
            ),
        )
        endScaleSeq = LerpScaleInterval(check, duration=0.65, scale=0.01)
        fallInterval = LerpPosInterval(check, 0.65, (0, 0, autocaddie.height / 2))
        response = random.choice(TTLocalizer.MovieSuitHealResponses)
        soundTrack = self.getSoundTrack("SA_extra_tip.ogg", delay=0, node=self.invoker)
        checkSeq = Sequence(
            scaleSeq,
            Wait(2.15),
            Parallel(
                Sequence(pInterval, Parallel(endScaleSeq, fallInterval)), soundTrack
            ),
        )
        checkSeq.append(Func(updateSuitHP, response))
        checkSeq.append(MovieUtil.createSuitUnlureTrack(autocaddie, self.battle))
        registerSfx = self.getSoundTrack(
            "SA_life_insurance_register.ogg", delay=damageDelay, node=self.invoker
        )
        return Sequence(
            Parallel(
                Sequence(suitTrack, Func(self.invoker.loop, "neutral")),
                registerSfx,
                checkSeq,
            )
        )


@AttackClass(attackType=AttackEnum.OVERWHELMING_AUTHORITY)
class OverwhelmingAuthority(SuitSingleAttack):
    ANIM_NAME = "effort"
    CHEAT = True
    OPEN_SHOT_DUR = 9.0

    def doAttack(self):
        derrick = None
        landDev = None
        for suit in self.battle.activeSuits:
            if suit.dna.name == "derrhand":
                derrick = suit
            elif suit.dna.name == "dold":
                landDev = suit

        suits = [self.invoker, landDev, derrick]

        sfx = self.getSoundTrack(
            "SA_overwhelming_authority.ogg", delay=0, duration=6.0, node=self.invoker
        )

        visualEffectTrack = Parallel()
        for toon in self.battle.activeToons:
            effectToonTrack = Sequence(
                Wait(1.0),
                Func(
                    MovieUtil.applyVisualEffect, toon, VisualEffectEnum.UNITE_COOLDOWN
                ),
                Func(toon.loop, 'neutral'),
            )
            visualEffectTrack.append(effectToonTrack)

        derrickIval = (
            Sequence(
                Wait(0.1),
                ActorInterval(derrick, "speak"),
                Func(derrick.loop, "neutral"),
            )
            if derrick
            else Sequence()
        )
        landDevIval = (
            Sequence(
                Wait(0.2),
                ActorInterval(landDev, "finger-wag"),
                Func(landDev.loop, "neutral"),
            )
            if landDev
            else Sequence()
        )
        dopaIval = Sequence(
            ActorInterval(self.invoker, self.ANIM_NAME),
            Func(self.invoker.loop, "neutral"),
        )
        speechIval = Func(suits[self.taunt[1]].setChatAbsolute, self.getAttackTaunt(), CFSpeech | CFTimeout)
        return Parallel(
            Wait(5.0), dopaIval, sfx, visualEffectTrack, derrickIval, landDevIval, speechIval
        )

    def getCameraShot(self, duration):
        return self.camera.heldShot(0, -15, 6, 0, 10, 0, duration, "allGroupOverheadShot")


@AttackClass(attackType=AttackEnum.DISRUPTIVE_ADVERTISEMENT)
class DisruptiveAdvertisement(SuitSingleAttack):
    ANIM_NAME = "effort"
    CHEAT = True
    OPEN_SHOT_DUR = 6.0

    def doAttack(self):
        suitTrack = self.getSuitAnimTrack()
        sfx = self.getSoundTrack(
            "SA_disruptive_advertisement.ogg", delay=0, node=self.invoker
        )
        visualEffectTrack = Sequence(
            Wait(0.9),
            Func(
                MovieUtil.applyVisualEffect,
                self.invoker,
                VisualEffectEnum.DISRUPTIVE_ADVERTISEMENT,
            ),
        )
        return Parallel(suitTrack, visualEffectTrack, sfx)


@AttackClass(attackType=AttackEnum.MULTI_LEVEL_MARKETING)
class MultiLevelMarketing(SuitSingleAttack):
    ANIM_NAME = "victory"
    CHEAT = True
    OPEN_SHOT_DUR = 6.0

    def doAttack(self):
        suitTrack = self.getSuitAnimTrack()
        sfx = self.getSoundTrack(
            "SA_multi_level_marketing.ogg", delay=1.5, node=self.invoker
        )
        return Parallel(
            suitTrack,
            sfx,
            Func(
                MovieUtil.unapplyVisualEffect,
                self.invoker,
                [VisualEffectEnum.DISRUPTIVE_ADVERTISEMENT],
            ),
        )

@AttackClass(attackType=AttackEnum.LIGHTS_ON)
class LightsOnInitiative(SuitSingleAttack):
    CHEAT = True
    ANIM_NAME = "phone"
    OPEN_SHOT_DUR = 2.8

    def doAttack(self):
        phone = globalPropPool.getProp("phone")
        receiver = globalPropPool.getProp("receiver")
        suitTrack = self.getSuitAnimTrack()
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
            LerpScaleInterval(phone, 1, MovieUtil.PNT3_ONE, MovieUtil.PNT3_NEARZERO),
            Wait(0.0),
            Func(receiver.wrtReparentTo, self.invoker.getRightHand()),
            LerpPosHprInterval(
                receiver,
                0.0001,
                Point3(-0.45, 0.48, -0.62),
                VBase3(-87.47, -18.21, 7.82),
            ),
            Wait(2.6),
            Func(receiver.wrtReparentTo, phone),
            Wait(0.55),
            LerpScaleInterval(phone, 0.4, MovieUtil.PNT3_NEARZERO),
            Func(MovieUtil.removeProps, [receiver, phone]),
        )
        soundTrack = self.getSoundTrack("SA_hangup.ogg", delay=0.61, node=self.invoker)

        return Parallel(Wait(4.0), suitTrack, propTrack, soundTrack)

    def getCameraShot(self, duration):
        return self.camera.heldRelativeHeadsUpShot(
            self.invoker, -2, 10, 6, self.invoker, duration, "lightsOnInitiativeShot"
        )
