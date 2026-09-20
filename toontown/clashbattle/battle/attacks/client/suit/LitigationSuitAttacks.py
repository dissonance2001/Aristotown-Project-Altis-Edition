import random

from panda3d.core import Point3, VBase3, TextNode, VBase4, Vec3
from toontown.chat.constants.ChatGlobals import  CFSpeech, CFTimeout
from direct.interval.IntervalGlobal import *

from toontown.audio.IsolatedSoundInterval import IsolatedSoundInterval
from toontown.clashbattle.battle import BattleParticles, MovieLure, MovieUtil
from toontown.clashbattle.battle.BattleProps import globalPropPool
from toontown.clashbattle.battle.BattleSounds import globalBattleSoundCache
from toontown.clashbattle.battle.attacks.base.AttackEnum import AttackEnum
from toontown.clashbattle.battle.attacks.client.Attack import Attack
from toontown.clashbattle.battle.attacks.client.AttackRepository import AttackClass
from toontown.clashbattle.battle.attacks.client.suit.SuitSingleAttack import SuitSingleAttack
from toontown.clashbattle.battle.visuals.VisualEffectEnums import VisualEffectEnum, SUIT_VISUAL_EFFECTS_TO_REMOVE
from toontown.toonbase import TTLocalizer, ToontownGlobals
from toontown.cutscene.repository.CutsceneLoader import CutsceneLoader
from toontown.cutscene.repository.CutsceneKeyEnum import CutsceneKeyEnum


@AttackClass(attackType=AttackEnum.BAYOU_BASH)
class BayouBash(SuitSingleAttack):
    ANIM_NAME = "snap"
    CHEAT = True
    OPEN_SHOT_DUR = 4.0

    def doAttack(self):
        suitTrack = self.getSuitAnimTrack(wantSpeechHeadAnim=False)
        sfx = self.getSoundTrack(
            "phase_11/audio/sfx/SA_bash.ogg", delay=0.1, node=self.invoker
        )

        suitTrack = Sequence(Func(self.invoker.specialHead.play, 'gsnap'), suitTrack, Func(self.invoker.loop, "neutral"))

        return Parallel(Wait(4.0), suitTrack, sfx)

    def getCameraShot(self, duration):
        return self.camera.heldRelativeHeadsUpShot(
            self.invoker, 1, 12, 8, self.invoker, duration, "bayouBashShot"
        )


@AttackClass(attackType=AttackEnum.INSURANCE_PLAN)
class InsurancePlan(SuitSingleAttack):
    CHEAT = True
    OPEN_SHOT_DUR = 6.5

    def doAttack(self):
        cutscene = CutsceneLoader.createLoader(
            CutsceneKeyEnum.CaseManager_Insurance,
            casemanager=self.invoker,
            suits=self.targetObjs,
            battle=self.battle,
            affectsCamera=self.battle.localToonPendingOrActive()
        ).buildCutscene()
        healer = self.invoker
        damageDelay = 5.4
        suitTrack = self.getSuitAnimTrack(wantSpeechHeadAnim=False, doActorInterval=False)
        healTracks = Parallel()


        books = []

        def updateSuitHP(suit):
            hpText = TTLocalizer.GeneralAttackHpTexts[TTLocalizer.HP_TEXT_INSURANCE]
            suit.showHpString(hpText[0], color=hpText[1])
            if suit != healer:
                suit.setChatAbsolute(
                    random.choice(TTLocalizer.MovieSuitHealResponses),
                    CFSpeech | CFTimeout,
                )

        def removeBooks():
            MovieUtil.removeProps(books)

        for suit in self.targetObjs:
            paper = globalPropPool.getProp("shredder-paper")
            paper.reparentTo(healer.getRightHand())
            paper.setScale(0.01)
            paper.setPos(0.8, -1.5, 0)
            paper.setHpr(150, -45, 120)
            paper.hide()
            books.append(paper)
            endPos = (0, 0, suit.height + 3)
            scaleSeq = LerpScaleInterval(paper, duration=0.25, scale=0.85)
            pInterval = Sequence(
                Func(paper.wrtReparentTo, suit),
                Parallel(
                    ProjectileInterval(
                        paper, duration=1.65, endPos=endPos, gravityMult=0.4
                    ),
                    LerpHprInterval(paper, 1.65, (180, -90, 0)),
                ),
            )
            endScaleSeq = LerpScaleInterval(paper, duration=1, scale=0.01)
            fallInterval = LerpPosInterval(paper, 0.65, (0, 0, suit.height / 2))
            seq = Sequence(
                Wait(0.75),
                Func(paper.show),
                scaleSeq,
                Wait(2),
                Parallel(
                    Sequence(Wait(0.4), pInterval, Parallel(endScaleSeq, fallInterval))
                ),
            )
            seq = Parallel(
                seq,
                Sequence(
                    Wait(damageDelay),
                    Func(updateSuitHP, suit),
                    Func(MovieUtil.applyVisualEffect, suit, VisualEffectEnum.INSURANCE),
                )
            )

            healTracks.append(seq)
        sfx = loader.loadSfx("phase_11/audio/sfx/LB_toonup.ogg")
        repairSoundTrack = Sequence(Wait(damageDelay), SoundInterval(sfx, node=healer, volume=0.8))
        return Sequence(
            Parallel(
                cutscene,
                suitTrack,
                repairSoundTrack,
                healTracks,
            ),
            Func(removeBooks),
        )

    def getCameraShot(self, duration):
        return Wait(duration)


@AttackClass(attackType=AttackEnum.LEGAL_BINDINGS)
class LegalBindings(SuitSingleAttack):
    ANIM_NAME = "throw-object"
    CHEAT = True
    OPEN_SHOT_DUR = 3.5

    def doAttack(self):
        target = self.targetDicts[0]
        toon = target["avatar"]
        tape = globalPropPool.getProp("redtape")
        tape.setColorScale(0.25, 0.25, 1.0, 1.0)
        tubes = []
        tube = globalPropPool.getProp("redtape-tube")
        tube.setColorScale(0.25, 0.25, 1.0, 1.0)
        tubes.append(tube)

        playRate = 1.35

        suitTrack = self.getSuitTrack(playRate=playRate)
        if self.invoker.dna.name in ("tf", "nc", "caseman"):
            tapePosPoints = [
                Point3(-0.0, 0.09, -0.38),
                VBase3(-1.152, -180, -76.784),
            ]
        else:
            tapePosPoints = [Point3(0.24, 0.09, -0.38), VBase3(-1.152, -180, -76.784)]
        tapeScaleUpPoint = Point3(0.9, 0.9, 0.24)
        propTrack = Sequence(
            self.getPropAppearTrack(
                tape,
                self.invoker.getRightHand(),
                tapePosPoints,
                0.8/playRate,
                tapeScaleUpPoint,
                scaleUpTime=0.5/playRate,
            )
        )

        propTrack.append(Wait(1.73/playRate))
        hitPoint = lambda toon=toon: self.toonTorsoPoint(toon)
        propTrack.append(
            self.getPropThrowTrack(tape, [hitPoint], [self.toonGroundPoint(toon, 0.7)], hitDuration=0.5/playRate, missDuration=0.5/playRate)
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
                    3.25/playRate,
                    3.17/playRate,
                    scaleUpPoint=scaleUpPoint,
                )
            )

        tubeTracks.append(Func(self.battle.movie.clearRestoreHips))
        toonTrack = self.getToonTrack(
            3.4/playRate,
            ["struggle"],
            2.8/playRate,
            ["jump"],
            forceHit=1,
            hpTextType=TTLocalizer.HP_TEXT_LEGALLY_BOUND,
            damageAnimPlayRate=playRate,
            dodgeAnimPlayRate=playRate,
        )
        soundTrack = self.getSoundTrack("SA_red_tape.ogg", delay=2.9, node=self.invoker, playRate=playRate)
        visualEffectTrack = Sequence(
            Wait(6.42/playRate),
            Func(MovieUtil.applyVisualEffect, toon, VisualEffectEnum.LEGALLY_BOUND),
        )
        return Parallel(
            suitTrack, toonTrack, propTrack, soundTrack, tubeTracks, visualEffectTrack
        )


@AttackClass(attackType=AttackEnum.BAYOU_BELLOW)
class BayouBellow(SuitSingleAttack):
    ANIM_NAME = "bellow"
    CHEAT = True
    OPEN_SHOT_DUR = 4.0

    def doAttack(self):
        cutscene = CutsceneLoader.createLoader(
            CutsceneKeyEnum.Litigator_Bellow,
            litigator=self.invoker,
            battle=self.battle,
            affectsCamera=self.battle.localToonPendingOrActive()
        ).buildCutscene()

        spraySeq = Sequence()
        sprayEffect = BattleParticles.createParticleEffect(file="soundWaveQuick")
        sprayEffect.setDepthWrite(0)
        sprayEffect.setDepthTest(0)
        sprayEffect.setTwoSided(1)

        spraySeq.append(
            Func(
                sprayEffect.setPos,
                self.invoker,
                Point3(0, 1.5, self.invoker.getHeight() - 1),
            )
        )
        sprayParticles = self.getPartTrack(
            sprayEffect,
            0.6,
            5.0,
            [sprayEffect, self.invoker.specialHead, 0],
            softStop=-3.5,
        )
        spraySeq.append(sprayParticles)

        finishPartSeq = Sequence(Wait(3.5), Func(spraySeq.finish))
        suitTrack = Parallel(spraySeq, finishPartSeq)

        # Create a visual to show all suits unluring.
        unlureTrack = Parallel()
        for suit in self.battle.activeSuits:
            suitResponseTrack = Sequence()
            if suit.isLured:
                suitResponseTrack.append(
                    Sequence(MovieLure.createSuitResetPosTrack(suit, self.battle))
                )
                suitResponseTrack.append(MovieUtil.unlureSuit(suit, self.battle))
                suitResponseTrack.append(Func(suit.neutralAvatar))
            suitResponseTrack.append(
                Func(MovieUtil.unapplyVisualEffect, suit, SUIT_VISUAL_EFFECTS_TO_REMOVE)
            )
            unlureTrack.append(suitResponseTrack)

        return Parallel(cutscene, Wait(3.0), suitTrack, Sequence(Wait(1.5), unlureTrack))

    def getCameraShot(self, duration):
        return Wait(duration)

    def getAttackDisplayName(self):
        if self.invoker.dna.name == 'lgator':
            return TTLocalizer.SuitAttackNames.get(self.attackType, "")
        else:
            return TTLocalizer.SuitAttackBonusPhrases['bellow'].get(self.invoker.dna.name, "")


@AttackClass(attackType=(AttackEnum.SNAP, AttackEnum.SNAP_RETALIATE, AttackEnum.FTF_PRESIDENT_SNAP))
class Snap(SuitSingleAttack):
    ANIM_NAME = "throw-object"
    CHEAT = True
    OPEN_SHOT_DUR = 2.8/1.5
    PLAY_RATE = 1.5

    def doAttack(self):
        target = self.targetDicts[0]
        toon = target["avatar"]
        teeth = globalPropPool.getProp("litigator_teeth")
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
            ActorInterval(teeth, "litigator_teeth", duration=throwDuration),
            ActorInterval(teeth, "litigator_teeth", duration=0.3),
            Func(teeth.pose, "litigator_teeth", 1),
            Wait(0.7),
            ActorInterval(teeth, "litigator_teeth", duration=0.9),
        )
        propTrack = Sequence(
            Parallel(teethAppearTrack, scaleTrack, hprTrack, animTrack),
            Func(MovieUtil.removeProp, teeth),
            Func(self.movie.clearRenderProp, teeth),
        )

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
            hpTextType=TTLocalizer.HP_TEXT_VULNERABLE,
        )
        soundTrack = self.getSoundTrack(
            "SA_bite.ogg", delay=throwDelay, node=self.invoker, playRate=1.05
        )
        visualEffectTrack = Sequence(
            Wait((3.2 + 2.4)/self.PLAY_RATE),
            Func(MovieUtil.applyVisualEffect, toon, VisualEffectEnum.VULNERABLE),
        )
        return Parallel(suitTrack, toonTrack, soundTrack, propTrack, visualEffectTrack)


@AttackClass(attackType=(AttackEnum.COURT_SANCTION, AttackEnum.COURT_SANCTION_RETALIATE))
class CourtSanction(SuitSingleAttack):
    ANIM_NAME = "sanction"
    CHEAT = True
    OPEN_SHOT_DUR = 1.0

    def doAttack(self):
        target = self.targetDicts[0]
        toon = target["avatar"]
        suitTrack = Sequence(self.getSuitTrack(), Func(self.invoker.loop, "neutral"))

        sanctioned = self.makeSanctionedNodePath()
        missPoint = lambda cancelled=sanctioned, toon=toon: self.toonMissPoint(
            cancelled, toon
        )
        propTrack = Sequence(
            Wait(0.55),
            Func(self.battle.movie.needRestoreRenderProp, sanctioned),
            Func(sanctioned.reparentTo, render),
            Func(sanctioned.setScale, 0.6),
            Func(sanctioned.setPosHpr, self.invoker, -3, 4, 6, 0, 0, 90),
            Func(sanctioned.setP, 0),
            Func(sanctioned.setR, 0),
        )
        propTrack.append(
            self.getPropThrowTrack(
                sanctioned, [self.toonFacePoint(toon)], [missPoint], hitDuration=0.4
            )
        )
        propTrack.append(Func(MovieUtil.removeProp, sanctioned))
        propTrack.append(Func(self.battle.movie.clearRenderProp, sanctioned))
        dodgeDelay = suitTrack.getDuration() - 4.35
        toonTrack = self.getToonTrack(
            suitTrack.getDuration() - 1.6,
            ["conked"],
            dodgeDelay,
            ["duck"],
            showMissedExtraTime=1.7,
            hpTextType=TTLocalizer.HP_TEXT_SANCTIONED,
        )
        visualEffectTrack = Sequence(
            Wait(suitTrack.getDuration() - 0.9),
            Func(MovieUtil.applyVisualEffect, toon, VisualEffectEnum.GAG_DOWN),
        )
        soundTrack = self.getSoundTrack(
            "phase_11/audio/sfx/SA_sanction.ogg", delay=0.25, node=self.invoker
        )
        return Parallel(suitTrack, toonTrack, propTrack, soundTrack, visualEffectTrack)

    @staticmethod
    def makeSanctionedNodePath():
        tn = TextNode("SANCTIONED")
        tn.setFont(ToontownGlobals.getSuitFont())
        tn.setText(TTLocalizer.MovieSuitSanctioned)
        tn.setAlign(TextNode.ACenter)
        tntop = hidden.attachNewNode("SanctionedTop")
        tnpath = tntop.attachNewNode(tn)
        tnpath.setPosHpr(0, 0, 0, 0, 0, 0)
        tnpath.setScale(1.2)
        tnpath.setColor(0.7, 0, 0, 1)
        tnpathback = tnpath.instanceUnderNode(tntop, "backside")
        tnpathback.setPosHpr(0, 0, 0, 180, 0, 0)
        tnpath.setScale(1.2)
        return tntop


@AttackClass(attackType=AttackEnum.COURT_RECORD)
class CourtRecord(SuitSingleAttack):
    ANIM_NAME = "cease"
    CHEAT = True
    OPEN_SHOT_DUR = 7.0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gagLevel = self.extraArgs[0]
        self.gagLevel2 = self.extraArgs[1]

    def doAttack(self):
        suitTrack = self.getSuitAnimTrack()

        sfx = self.getSoundTrack("SA_cease_and_desist.ogg", delay=0, node=self.invoker)

        suitTrack = Sequence(suitTrack, Func(self.invoker.loop, "neutral"))

        return Parallel(Wait(5.0), suitTrack, sfx)

    def getSuitAnimTrack(self, delay=0):
        levelText = self.gagLevel + 1
        if self.gagLevel2 != -1:
            levelText2 = self.gagLevel2 + 1
            if levelText < levelText2:
                levelText = f"{levelText} and {levelText2}"
            else:
                levelText = f"{levelText2} and {levelText}"
        taunt = self.getAttackTaunt() % levelText
        return Sequence(
            Wait(delay),
            Func(self.invoker.setChatAbsolute, taunt, CFSpeech | CFTimeout),
            ActorInterval(self.invoker, self.getAnimName()),
            Func(self.invoker.clearChat),
        )

    def getAttackDisplayName(self):
        levelText = self.gagLevel + 1
        if self.gagLevel2 != -1:
            levelText2 = self.gagLevel2 + 1
            if levelText < levelText2:
                levelText = f"{levelText} and {levelText2}"
            else:
                levelText = f"{levelText2} and {levelText}"
        return (
            TTLocalizer.SuitAttackNames[self.attackType][0],
            TTLocalizer.SuitAttackNames[self.attackType][1] % levelText,
        )


@AttackClass(attackType=AttackEnum.SCAPEGOAT_ENRAGED)
class ScapegoatEnraged(SuitSingleAttack):
    CHEAT = True
    OPEN_SHOT_DUR = 5.0

    def doAttack(self):
        cutscene = CutsceneLoader.createLoader(
            CutsceneKeyEnum.Scapegoat_Enraged,
            scapegoat=self.invoker,
            toons=self.targetObjs,
            battle=self.battle,
            affectsCamera=self.battle.localToonPendingOrActive()
        ).buildCutscene()

        suitTrack = self.getSuitAnimTrack(wantSpeechHeadAnim=False, doActorInterval=False)
        flashRed = Sequence(
            LerpColorScaleInterval(
                self.invoker, 0.2, colorScale=VBase4(1, 0.2, 0.2, 1)
            ),
            LerpColorScaleInterval(self.invoker, 0.275, colorScale=VBase4(1, 1, 1, 1)),
        )
        redTrack = Sequence(Wait(0.825), flashRed, Wait(0.1), flashRed, Wait(0.1))
        visualEffectTrack = Sequence(
            Wait(0.8),
            Func(
                MovieUtil.applyVisualEffect,
                self.invoker,
                VisualEffectEnum.SCAPEGOAT_ENRAGED,
            ),
        )
        return Parallel(cutscene, suitTrack, redTrack, visualEffectTrack)

    def getCameraShot(self, duration):
        return Wait(duration)


@AttackClass(attackType=AttackEnum.SCAPEGOAT_DEFENSE)
class ScapegoatDefense(SuitSingleAttack):
    ANIM_NAME = "defense"
    CHEAT = True
    OPEN_SHOT_DUR = 5

    def doAttack(self):
        suitTrack = self.getSuitAnimTrack()
        sfx = self.getSoundTrack(
            "phase_11/audio/sfx/SA_defense.ogg", delay=0, node=self.invoker
        )
        flashBlue = Sequence(
            LerpColorScaleInterval(
                self.invoker, 0.2, colorScale=VBase4(0.4, 0.4, 1, 1)
            ),
            LerpColorScaleInterval(self.invoker, 0.6, colorScale=VBase4(1, 1, 1, 1)),
        )
        blueTrack = Sequence(Wait(0.5), flashBlue, Wait(0.5))
        visualEffectTrack = Sequence(
            Func(
                MovieUtil.unapplyVisualEffect,
                self.invoker,
                VisualEffectEnum.SCAPEGOAT_ENRAGED,
            ),
        )

        # Before returning the sequence, make sure we find their visual effect and mark us as not needing
        # the post attack return anim.
        rageEffect = self.invoker.getVisualEffectOfId(VisualEffectEnum.SCAPEGOAT_ENRAGED)
        if rageEffect:
            rageEffect.setWantPostAttackSeq(False)

        return Parallel(suitTrack, blueTrack, sfx, visualEffectTrack)

    def getSuitAnimTrack(self, delay=0):
        taunt = self.getAttackTaunt()
        return Sequence(
            Wait(delay),
            Func(self.invoker.setChatAbsolute, taunt, CFSpeech | CFTimeout),
            ActorInterval(self.invoker, self.getAnimName()),
            Func(self.invoker.loop, "neutral"),
            Wait(3),
            Func(self.invoker.clearChat),
        )


@AttackClass(attackType=AttackEnum.COURT_COSTS)
class CourtCosts(SuitSingleAttack):
    ANIM_NAME = "magic3"
    CHEAT = True
    OPEN_SHOT_DUR = 1.7

    def doAttack(self):
        damageDelay = 1.7

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
        fallingSoundTrack = Sequence(
            Wait(damageDelay + 0.5),
            SoundInterval(
                globalBattleSoundCache.getSound("Toon_bodyfall_synergy.ogg"),
                node=self.invoker,
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


@AttackClass(attackType=AttackEnum.LEGAL_BINDINGS_DAMAGE)
class LegalBindingsDamage(Attack):
    CHEAT = True
    OPEN_SHOT_DUR = 1.7
    ALLOW_GROUPING = False

    def doAttack(self):
        target = self.targetDicts[0]
        toon = target["avatar"]
        damageDelay = 0
        BattleParticles.loadParticles()
        spinEffect1 = BattleParticles.createParticleEffect(
            file="legalBindingsDamageEffect"
        )
        spinEffect2 = BattleParticles.createParticleEffect(
            file="legalBindingsDamageEffect"
        )
        spinEffect3 = BattleParticles.createParticleEffect(
            file="legalBindingsDamageEffect"
        )
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
        spinTrack1 = self.getPartTrack(
            spinEffect1, 1.1, 2.9, [spinEffect1, self.battle, 0]
        )
        spinTrack2 = self.getPartTrack(
            spinEffect2, 1.1, 2.9, [spinEffect2, self.battle, 0]
        )
        spinTrack3 = self.getPartTrack(
            spinEffect3, 1.1, 2.9, [spinEffect3, self.battle, 0]
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
        )
        toonSpinTrack = Sequence(
            Wait(damageDelay + 0.1),
            LerpHprInterval(toon, 0.7, Point3(-10, 0, 0)),
            LerpHprInterval(toon, 0.5, Point3(-30, 0, 0)),
            LerpHprInterval(toon, 0.2, Point3(-60, 0, 0)),
            LerpHprInterval(toon, 0.7, Point3(-700, 0, 0)),
            LerpHprInterval(toon, 1.0, Point3(-1310, 0, 0)),
            LerpHprInterval(toon, 0.4, toon.getHpr()),
            Wait(0.5),
        )
        paperSound = self.getSoundTrack(
            "phase_11/audio/sfx/LB_boss_paper_spin.ogg", delay=damageDelay + 0.1
        )
        soundTrack = self.getSoundTrack(
            "tt_s_ara_cfg_toonInWhirlwind.ogg", delay=damageDelay + 0.1
        )
        return Parallel(
            toonTrack,
            toonSpinTrack,
            soundTrack,
            paperSound,
            spinTrack1,
            spinTrack2,
            spinTrack3,
        )

    def getAttackDisplayName(self):
        return (
            TTLocalizer.SuitAttackNames[self.attackType][0],
            TTLocalizer.SuitAttackNames[self.attackType][1]
            % abs(self.targetDicts[0]["hp"]),
        )


@AttackClass(attackType=AttackEnum.COURT_RECORD_DAMAGE)
class CourtRecordDamage(Attack):
    CHEAT = True
    OPEN_SHOT_DUR = 5.0
    ALLOW_GROUPING = False

    def doAttack(self):
        target = self.targetDicts[0]
        toon = target["avatar"]
        dmg = target["hp"]
        died = target["died"]
        gavel = loader.loadModel("phase_11/models/lawbotHQ/LB_gavel")
        gavelSfx = loader.loadSfx("phase_11/audio/sfx/LB_gavel.ogg")
        gavel.setScale(0.01)
        gavel.setPos(toon, 0, -14, 0)
        gavel.setHpr(toon, 0, 0, 0)
        finalScale = 1.75
        finalP = -80
        startHpr = toon.getHpr()
        toon.headsUp(gavel)
        endHpr = toon.getHpr()
        toon.setHpr(startHpr)

        gavelScale = LerpScaleInterval(gavel, 2.0, finalScale, blendType="easeOut")
        gavelShow = Sequence(Func(gavel.wrtReparentTo, render), gavelScale)
        gavelFall1 = LerpHprInterval(
            gavel,
            0.5,
            (startHpr[0], startHpr[1] - 15, startHpr[2]),
            blendType="easeInOut",
        )
        gavelFall2 = LerpHprInterval(
            gavel,
            0.4,
            (startHpr[0], startHpr[1] + finalP, startHpr[2]),
            blendType="easeIn",
        )

        def finishToonEmote():
            if toon.emoteTrack:
                toon.emoteTrack.finish()

        toonWalkTrack = Sequence(
            Func(toon.loop, "walk"),
            LerpHprInterval(toon, 1.0, endHpr),
            Func(toon.loop, "neutral"),
            Func(toon.doEmote, 20),
            Wait(0.39),
            Func(finishToonEmote),
        )

        gavelTrack = Sequence(
            gavelShow,
            gavelFall1,
            Parallel(Sequence(Wait(1), gavelFall2), toonWalkTrack),
        )
        gavelTrack.append(Func(base.playSfx, gavelSfx))
        gavelTrack.append(Func(toon.setAnimState, "Squish"))
        gavelTrack.append(Func(toon.playDialogueForString, "!"))
        gavelTrack.append(Func(toon.setHpr, startHpr))
        gavelTrack.append(Wait(1))
        gavelTrack.append(Func(self.doDamage, toon, dmg, died))
        gavelTrack.append(LerpScaleInterval(gavel, 0.5, 0.01))
        gavelTrack.append(Wait(1.2))
        gavelTrack.append(Func(toon.setAnimState, "Neutral"))
        gavelTrack.append(Func(gavel.removeNode))

        return Sequence(Parallel(Sequence(gavelTrack), Wait(3.0)))

    def getCameraShot(self, duration):
        toon = self.targetDicts[0]["avatar"]
        camSeq = Sequence(
            self.camera.heldRelativeShot(
                toon, 3, 10, 3, 163, 0, 0, 2.5, "courtRecordDamageHeldShot"
            )
        )
        camSeq.append(LerpFunctionInterval(camera.setP, 0.5, fromData=0, toData=10))
        return Parallel(camSeq, Wait(duration))

    def getAttackDisplayName(self):
        return (
            TTLocalizer.SuitAttackNames[self.attackType][0],
            TTLocalizer.SuitAttackNames[self.attackType][1]
            % abs(self.targetDicts[0]["hp"]),
        )


@AttackClass(attackType=AttackEnum.STENOG_CALCULATING_COSTS)
class StenographerCalculatingCosts(Attack):
    CHEAT = True
    OPEN_SHOT_DUR = 5.0
    ALLOW_GROUPING = False

    def doAttack(self):
        target = self.targetDicts[0]
        suit = target["avatar"]

        calculator = globalPropPool.getProp("calculator")
        calculatorAnimName = 'cc_a_prp_bat_calculator-calculating-costs'
        calcPosPoints = [Point3(-0.3449, 0.2611, -0.079), VBase3(7.8879, 0, 180)]
        scaleUpPoint = Point3(1.3, 1.5, 1.5)
        propTrack = self.getPropTrack(
            calculator,
            suit.getRightHand(),
            calcPosPoints,
            scaleUpPoint=scaleUpPoint,
            appearDelay=0,
            remainDelay=0,
            scaleUpTime=0,
            scaleDownTime=0,
            anim=1,
            propName=calculatorAnimName,
            animDuration=calculator.getDuration(calculatorAnimName),

        )

        animName = 'lured' if suit.isLured else 'neutral'
        suitTrack = Sequence(
            Func(suit.setChatAbsolute, self.getAttackTaunt().format(self.extraArgs[0]), CFSpeech | CFTimeout),
            ActorInterval(suit, "calculating-costs"),
            Func(suit.loop, animName),
            Wait(1.5),
        )

        soundTrack = self.getSoundTrack("phase_11/audio/sfx/SA_calculating_costs.ogg", delay=0.17, node=self.invoker)
        return Parallel(suitTrack, propTrack, soundTrack)

    def getCameraShot(self, duration):
        return self.camera.randomActorShot(self.targetDicts[0]["avatar"], self.battle, duration, 'suit')
