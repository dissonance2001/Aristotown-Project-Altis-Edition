import copy
import random
from direct.directnotify import DirectNotifyGlobal
from direct.interval.IntervalGlobal import *
from direct.showbase import DirectObject
from toontown.battle.BattleBase import *
from toontown.battle import BattleExperience
from toontown.battle import BattleParticles
from toontown.battle import MovieDrop
from toontown.battle import BattleProps
from toontown.battle import MovieFire
import PlayByPlayText
from otp.otpbase import OTPLocalizerEnglish
from toontown.battle.BattleSounds import *
from toontown.battle import MovieHeal
from toontown.battle import MovieLure
from toontown.battle import MovieNPCSOS
from toontown.battle import MoviePetSOS
from toontown.battle import MovieSOS
from toontown.battle import MovieSound
from toontown.battle import MovieSquirt
from toontown.battle import MovieSuitAttacks
from toontown.battle import MovieThrow
from toontown.battle import MovieToonVictory
from toontown.battle import MovieTrap
from toontown.battle import MovieCamera
from toontown.battle import MovieZap
from toontown.battle import MovieUtil
from toontown.battle import PlayByPlayText
from toontown.battle import RewardPanel
from toontown.battle.SuitBattleGlobals import *
from toontown.chat.ChatGlobals import *
from toontown.distributed import DelayDelete
from toontown.toon import NPCToons
from toontown.toon import Toon
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownGlobals
from toontown.toonbase.ToontownBattleGlobals import *
from toontown.toontowngui import TTDialog
from toontown.nametag import NametagGlobals

camPos = Point3(14, 0, 10)
camHpr = Vec3(89, -30, 0)
randomBattleTimestamp = base.config.GetBool('random-battle-timestamp', 0)

class Movie(DirectObject.DirectObject):
    notify = DirectNotifyGlobal.directNotify.newCategory('Movie')

    def __init__(self, battle):
        self.battle = battle
        self.track = None
        self.rewardPanel = None
        self.rewardCallback = None
        self.playByPlayText = PlayByPlayText.PlayByPlayText()
        self.playByPlayText.hide()
        self.renderProps = []
        self.hasBeenReset = 0
        self.reset()
        self.rewardHasBeenReset = 0
        self.resetReward()

    def cleanup(self):
        self.reset()
        self.resetReward()
        self.battle = None
        if self.playByPlayText != None:
            self.playByPlayText.cleanup()
        self.playByPlayText = None
        if self.rewardPanel != None:
            self.rewardPanel.cleanup()
        self.rewardPanel = None
        self.rewardCallback = None

    def needRestoreColor(self):
        self.restoreColor = 1

    def clearRestoreColor(self):
        self.restoreColor = 0

    def needRestoreHips(self):
        self.restoreHips = 1

    def clearRestoreHips(self):
        self.restoreHips = 0

    def needRestoreHeadScale(self):
        self.restoreHeadScale = 1

    def clearRestoreHeadScale(self):
        self.restoreHeadScale = 0

    def needRestoreToonScale(self):
        self.restoreToonScale = 1

    def clearRestoreToonScale(self):
        self.restoreToonScale = 0

    def needRestoreParticleEffect(self, effect):
        self.specialParticleEffects.append(effect)

    def clearRestoreParticleEffect(self, effect):
        if self.specialParticleEffects.count(effect) > 0:
            self.specialParticleEffects.remove(effect)

    def needRestoreRenderProp(self, prop):
        self.renderProps.append(prop)

    def clearRenderProp(self, prop):
        if self.renderProps.count(prop) > 0:
            self.renderProps.remove(prop)

    def getPropTrack(self, prop, parent, posPoints, appearDelay, remainDelay, scaleUpPoint=Point3(1), scaleUpTime=0.5,
                     scaleDownTime=0.5, startScale=Point3(0.01), anim=0, propName='none', animDuration=0.0,
                     animStartTime=0.0):
        if anim == 1:
            track = Sequence(Wait(appearDelay), Func(__showProp, prop, parent, *posPoints),
                             LerpScaleInterval(prop, scaleUpTime, scaleUpPoint, startScale=startScale),
                             ActorInterval(prop, propName, duration=animDuration, startTime=animStartTime),
                             Wait(remainDelay), Func(MovieUtil.removeProp, prop))
        else:
            track = Sequence(Wait(appearDelay), Func(__showProp, prop, parent, *posPoints),
                             LerpScaleInterval(prop, scaleUpTime, scaleUpPoint, startScale=startScale),
                             Wait(remainDelay), LerpScaleInterval(prop, scaleDownTime, MovieUtil.PNT3_NEARZERO),
                             Func(MovieUtil.removeProp, prop))
        return track

    def getPropAppearTrack(self, prop, parent, posPoints, appearDelay, scaleUpPoint=Point3(1), scaleUpTime=0.5,
                           startScale=Point3(0.01), poseExtraArgs=None):
        propTrack = Sequence(Wait(appearDelay), Func(__showProp, prop, parent, *posPoints))
        if poseExtraArgs:
            propTrack.append(Func(prop.pose, *poseExtraArgs))
        propTrack.append(LerpScaleInterval(prop, scaleUpTime, scaleUpPoint, startScale=startScale))
        return propTrack

    def getPropThrowTrack(self, attack, prop, hitPoints=[], missPoints=[], hitDuration=0.25, missDuration=0.25,
                          hitPointNames='none', missPointNames='none', lookAt='none', groundPointOffSet=0,
                          missScaleDown=None, parent=render):
        target = attack['target']
        toon = target[0]['toon']
        dmg = target[0]['hp']
        battle = attack['battle']

        def getLambdas(list, prop, toon):
            for i in xrange(len(list)):
                if list[i] == 'face':
                    list[i] = lambda toon=toon: __toonFacePoint(toon)
                elif list[i] == 'miss':
                    list[i] = lambda prop=prop, toon=toon: __toonMissPoint(prop, toon)
                elif list[i] == 'bounceHit':
                    list[i] = lambda prop=prop, toon=toon: __throwBounceHitPoint(prop, toon)
                elif list[i] == 'bounceMiss':
                    list[i] = lambda prop=prop, toon=toon: __throwBounceMissPoint(prop, toon)

            return list

        if hitPointNames != 'none':
            hitPoints = getLambdas(hitPointNames, prop, toon)
        if missPointNames != 'none':
            missPoints = getLambdas(missPointNames, prop, toon)
        propTrack = Sequence()
        propTrack.append(Func(battle.movie.needRestoreRenderProp, prop))
        propTrack.append(Func(prop.wrtReparentTo, parent))
        if lookAt != 'none':
            propTrack.append(Func(prop.lookAt, lookAt))
        if dmg > 0:
            for i in xrange(len(hitPoints)):
                pos = hitPoints[i]
                propTrack.append(LerpPosInterval(prop, hitDuration, pos=pos))

        else:
            for i in xrange(len(missPoints)):
                pos = missPoints[i]
                propTrack.append(LerpPosInterval(prop, missDuration, pos=pos))

            if missScaleDown:
                propTrack.append(LerpScaleInterval(prop, missScaleDown, MovieUtil.PNT3_NEARZERO))
        name = attack['id']
        propTrack.append(Func(MovieUtil.removeProp, prop))
        propTrack.append(Func(battle.movie.clearRenderProp, prop))
        return propTrack

    def restore(self):
        for toon in self.battle.activeToons:
            toon.loop('neutral')
            origPos, origHpr = self.battle.getActorPosHpr(toon)
            toon.setPosHpr(self.battle, origPos, origHpr)
            hands = toon.getRightHands()[:]
            hands += toon.getLeftHands()
            for hand in hands:
                props = hand.getChildren()
                for prop in props:
                    if prop.getName() != 'book':
                        MovieUtil.removeProp(prop)

            if self.restoreColor == 1:
                headParts = toon.getHeadParts()
                torsoParts = toon.getTorsoParts()
                legsParts = toon.getLegsParts()
                partsList = [headParts, torsoParts, legsParts]
                for parts in partsList:
                    for partNum in xrange(0, parts.getNumPaths()):
                        nextPart = parts.getPath(partNum)
                        nextPart.clearColorScale()
                        nextPart.clearTransparency()

            if self.restoreHips == 1:
                parts = toon.getHipsParts()
                for partNum in xrange(0, parts.getNumPaths()):
                    nextPart = parts.getPath(partNum)
                    props = nextPart.getChildren()
                    for prop in props:
                        if prop.getName() == 'redtape-tube.egg':
                            MovieUtil.removeProp(prop)

            if self.restoreHeadScale == 1:
                headScale = ToontownGlobals.toonHeadScales[toon.style.getAnimal()]
                for lod in toon.getLODNames():
                    toon.getPart('head', lod).setScale(headScale)

            if self.restoreToonScale == 1:
                toon.setScale(1)
            headParts = toon.getHeadParts()
            for partNum in xrange(0, headParts.getNumPaths()):
                part = headParts.getPath(partNum)
                part.setHpr(0, 0, 0)
                part.setPos(0, 0, 0)

            arms = toon.findAllMatches('**/arms')
            sleeves = toon.findAllMatches('**/sleeves')
            hands = toon.findAllMatches('**/hands')
            for partNum in xrange(0, arms.getNumPaths()):
                armPart = arms.getPath(partNum)
                sleevePart = sleeves.getPath(partNum)
                handsPart = hands.getPath(partNum)
                armPart.setHpr(0, 0, 0)
                sleevePart.setHpr(0, 0, 0)
                handsPart.setHpr(0, 0, 0)

        for suit in self.battle.activeSuits:
            if suit._Actor__animControlDict != None:
                suit.setNeutralAnimation()
                suit.battleTrapIsFresh = 0
                origPos, origHpr = self.battle.getActorPosHpr(suit)
                suit.setPosHpr(self.battle, origPos, origHpr)
                hands = [suit.getRightHand(), suit.getLeftHand()]
                for hand in hands:
                    props = hand.getChildren()
                    for prop in props:
                        MovieUtil.removeProp(prop)

        for effect in self.specialParticleEffects:
            if effect != None:
                effect.cleanup()

        self.specialParticleEffects = []
        for prop in self.renderProps:
            MovieUtil.removeProp(prop)

        self.renderProps = []

    def _deleteTrack(self):
        if self.track:
            DelayDelete.cleanupDelayDeletes(self.track)
            self.track = None

    def reset(self, finish = 0):
        if self.hasBeenReset == 1:
            return
        self.hasBeenReset = 1
        self.stop()
        self._deleteTrack()
        if finish == 1:
            self.restore()
        self.toonAttackDicts = []
        self.suitAttackDicts = []
        self.suitCheatDicts = []
        self.restoreColor = 0
        self.restoreHips = 0
        self.restoreHeadScale = 0
        self.restoreToonScale = 0
        self.specialParticleEffects = []
        for prop in self.renderProps:
            MovieUtil.removeProp(prop)

        self.renderProps = []

    def resetReward(self, finish = 0):
        if self.rewardHasBeenReset == 1:
            return
        self.rewardHasBeenReset = 1
        self.stop()
        self._deleteTrack()
        if finish == 1:
            self.restore()
        self.toonRewardDicts = []
        if self.rewardPanel != None:
            self.rewardPanel.destroy()
        self.rewardPanel = None

    def play(self, ts, callback):
        self.hasBeenReset = 0
        ptrack = Sequence()
        camtrack = Sequence()
        if random.random() > 0.5:
            MovieUtil.shotDirection = 'left'
        else:
            MovieUtil.shotDirection = 'right'
        for s in self.battle.activeSuits:
            s.battleTrapIsFresh = 0

        tattacks, tcam = self.__doToonAttacks()
        if tattacks:
            ptrack.append(tattacks)
            camtrack.append(tcam)
        sattacks, scam = self.__doSuitAttacks()
        if sattacks:
            ptrack.append(sattacks)
            camtrack.append(scam)
            for a in self.suitAttackDicts:
                battle = a['battle']
                ival, camIval = MovieSuitAttacks.doSuitAttack(a)
                for s in battle.activeSuits:
                    pbpText = PlayByPlayText.PlayByPlayText()
                    pbpDc = PlayByPlayText.PlayByPlayText()
                    ptrack.append(Parallel(Func(s.setNeutralAnimation), Func(s.setChatAbsolute,
                                                                             '',
                                                                             CFSpeech | CFTimeout)))
        ptrack.append(Func(callback))
        self._deleteTrack()
        self.track = Sequence(ptrack, name='movie-track-%d' % self.battle.doId)
        if self.battle.localToonPendingOrActive():
            self.track = Parallel(self.track, Sequence(camtrack), name='movie-track-with-cam-%d' % self.battle.doId)
        if randomBattleTimestamp == 1:
            randNum = random.randint(0, 99)
            dur = self.track.getDuration()
            ts = float(randNum) / 100.0 * dur
        self.track.delayDeletes = []
        for suit in self.battle.suits:
            self.track.delayDeletes.append(DelayDelete.DelayDelete(suit, 'Movie.play'))

        for toon in self.battle.toons:
            self.track.delayDeletes.append(DelayDelete.DelayDelete(toon, 'Movie.play'))

        playRate = 1
        self.setTrackPlayRate(self.track, playRate)
        self.track.start(ts, playRate=playRate)
        for s in self.battle.suits:
            if s.dna.name == 'laa':
                theSuit = s
                self.track.setPlayRate(theSuit.getPlayRate())
            else:
                pass
        return None

    def setTrackPlayRate(self, track, playRate):
        for seq in track:
            if isinstance(seq, SoundInterval):
                if seq.sound is None:
                    continue
                seq.sound.setPlayRate(playRate)
            elif isinstance(seq, MetaInterval):
                self.setTrackPlayRate(seq, playRate)

    def __makeSanctionedNodePath(self):
        tn = TextNode('CANCELLED')
        tn.setFont(getSuitFont())
        tn.setText('SANCTIONED\nSANCTIONED\nSANCTIONED')
        tn.setAlign(TextNode.ACenter)
        tntop = hidden.attachNewNode('CancelledTop')
        tnpath = tntop.attachNewNode(tn)
        tnpath.setPosHpr(0, 0, 0, 0, 0, 0)
        tnpath.setScale(1)
        tnpath.setColor(0.7, 0, 0, 1)
        tnpathback = tnpath.instanceUnderNode(tntop, 'backside')
        tnpathback.setPosHpr(0, 0, 0, 180, 0, 0)
        tnpath.setScale(1)
        return tntop

    def doSnapSoaked(self, attack):
        suit = attack['suit']
        battle = attack['battle']
        target = attack['target']
        toon = target[0]['toon']
        dmg = target[0]['hp']
        teeth = BattleProps.globalPropPool.getProp('litigator-teeth')
        propDelay = 0.25
        propScaleUpTime = 0.25
        suitDelay = 1.55
        throwDelay = propDelay + propScaleUpTime + suitDelay
        throwDuration = 0.25
        posPoints = [Point3(-0.35, 0, 0), VBase3(90, 180, 0)]
        teethAppearTrack = Sequence(
            getPropAppearTrack(teeth, suit.getRightHand(), posPoints, propDelay, Point3(4, 4, 4),
                               scaleUpTime=propScaleUpTime))
        teethAppearTrack.append(Wait(suitDelay))
        teethAppearTrack.append(Func(battle.movie.needRestoreRenderProp, teeth))
        teethAppearTrack.append(Func(teeth.wrtReparentTo, battle))
        if dmg > 0:
            x = toon.getX(battle)
            y = toon.getY(battle)
            z = toon.getZ(battle)
            toonHeight = z + toon.getHeight()
            flyPoint = Point3(x, y + 2.7, toonHeight * 0.7)
            teethAppearTrack.append(LerpPosInterval(teeth, throwDuration, pos=flyPoint))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.4, pos=Point3(x, y + 3.2, toonHeight * 0.7)))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.3, pos=Point3(x, y + 4.7, toonHeight * 0.5)))
            teethAppearTrack.append(Wait(0.2))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.1, pos=Point3(x, y, toonHeight + 3)))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.1, pos=Point3(x, y - 1.2, toonHeight * 0.7)))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.1, pos=Point3(x, y - 0.7, toonHeight * 0.4)))
            teethAppearTrack.append(Wait(0.4))
            scaleTrack = Sequence(Wait(throwDelay), LerpScaleInterval(teeth, throwDuration, Point3(6, 6, 6)), Wait(0.9),
                                  LerpScaleInterval(teeth, 0.2, Point3(10, 10, 10)), Wait(1.2),
                                  LerpScaleInterval(teeth, 0.3, MovieUtil.PNT3_NEARZERO))
            hprTrack = Sequence(Wait(throwDelay), LerpHprInterval(teeth, 0.3, Point3(180, 0, 0)), Wait(0.2),
                                LerpHprInterval(teeth, 0.4, Point3(180, -35, 0), startHpr=Point3(180, 0, 0)), Wait(0.6),
                                LerpHprInterval(teeth, 0.1, Point3(0, -35, 0), startHpr=Point3(180, -35, 0)))
            animTrack = Sequence(Wait(throwDelay), ActorInterval(teeth, 'litigator-teeth', duration=throwDuration),
                                 ActorInterval(teeth, 'litigator-teeth', duration=0.3),
                                 Func(teeth.pose, 'litigator-teeth', 1), Wait(0.7),
                                 ActorInterval(teeth, 'litigator-teeth', duration=0.9))
            propTrack = Sequence(Parallel(teethAppearTrack, scaleTrack, hprTrack, animTrack),
                                 Func(MovieUtil.removeProp, teeth), Func(battle.movie.clearRenderProp, teeth))
        else:
            x = toon.getX(battle)
            y = toon.getY(battle)
            z = toon.getZ(battle)
            z = z + 0.2
            flyPoint = Point3(x, y - 2.1, z)
            teethAppearTrack.append(LerpPosInterval(teeth, throwDuration, pos=flyPoint))
            teethAppearTrack.append(Wait(0.2))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.2, pos=Point3(x + 0.5, y - 2.5, z)))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.2, pos=Point3(x + 1.0, y - 3.0, z + 0.4)))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.2, pos=Point3(x + 1.3, y - 3.6, z)))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.2, pos=Point3(x + 0.9, y - 3.1, z + 0.4)))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.2, pos=Point3(x + 0.3, y - 2.6, z)))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.2, pos=Point3(x - 0.1, y - 2.2, z + 0.4)))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.2, pos=Point3(x - 0.4, y - 1.9, z)))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.2, pos=Point3(x - 0.7, y - 2.1, z + 0.4)))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.2, pos=Point3(x - 0.8, y - 2.3, z)))
            teethAppearTrack.append(LerpScaleInterval(teeth, 0.6, MovieUtil.PNT3_NEARZERO))
            hprTrack = Sequence(Wait(throwDelay), LerpHprInterval(teeth, 0.3, Point3(180, 0, 0)), Wait(0.5),
                                LerpHprInterval(teeth, 0.4, Point3(80, 0, 0), startHpr=Point3(180, 0, 0)),
                                LerpHprInterval(teeth, 0.8, Point3(-10, 0, 0), startHpr=Point3(80, 0, 0)))
            animTrack = Sequence(Wait(throwDelay), ActorInterval(teeth, 'teeth', duration=3.6))
            propTrack = Sequence(Parallel(teethAppearTrack, hprTrack, animTrack), Func(MovieUtil.removeProp, teeth),
                                 Func(battle.movie.clearRenderProp, teeth))
        damageAnims = [['cringe',
                        0.01,
                        0.7,
                        1.2],
                       ['spit',
                        0.01,
                        2.95,
                        1.47],
                       ['spit',
                        0.01,
                        4.42,
                        0.07],
                       ['spit',
                        0.08,
                        4.49,
                        -0.07],
                       ['spit',
                        0.08,
                        4.42,
                        0.07],
                       ['spit',
                        0.08,
                        4.49,
                        -0.07],
                       ['spit',
                        0.08,
                        4.42,
                        0.07],
                       ['spit',
                        0.08,
                        4.49,
                        -0.07],
                       ['spit', 0.01, 4.42]]
        dodgeAnims = [['jump', 0.01, 0.01]]
        toonTrack = getToonTakeDamageTrackCheat(attack, toon, target['died'], int(dmg / 1.93), 2.1,
                                                splicedDamageAnims=damageAnims, showDamageExtraTime=1)
        notifyTrack = Sequence(Wait(3.1), Func(toon.showHpTextCheat, - int(dmg / 1.93)),
                               Func(toon.showHpString, "VULNERABLE!"))
        soundTrack = getSoundTrack('SA_chomp.ogg', delay=2, node=suit)
        suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
        return Parallel(suitTrack, toonTrack, soundTrack, propTrack, notifyTrack)

    def doGavel(self, attack, suit):
        battle = attack['battle']
        target = attack['target']
        toon = target[0]['toon']
        targetPos = toon.getPos(battle)
        headsUp = Func(suit.headsUp, battle, targetPos)
        dmg = target[0]['hp']
        gavel = BattleProps.globalPropPool.getProp('LB_gavel')
        toonPos = toon.getPos(battle)
        initialScale = toon.getScale()
        gavelPos = Point3(toonPos.getX(), 2, 0)
        propTrack = Sequence(
            MovieSuitAttacks.getPropAppearTrack(gavel, parent=battle, posPoints=[gavelPos, VBase3(0, 0, 0)], appearDelay=0.0,
                               scaleUpPoint=Point3(1), scaleUpTime=1.5),
            LerpHprInterval(gavel, 0.5, VBase3(0, 90, 0)),
            Parallel(SoundInterval(globalBattleSoundCache.getSound('LB_gavel.ogg'), node=toon), Sequence(
                Wait(0.1),
                LerpHprInterval(gavel, 0.5, VBase3(0, 0, 0)),
                LerpScaleInterval(gavel, 1.5, MovieUtil.PNT3_ZERO)
            ))
        )
        taunt = "Any gags Toons use can and will be held against them in a court of law."
        origPos, origHpr = battle.getActorPosHpr(suit)
        suitReset = Func(suit.setHpr, battle, origHpr)
        suitTrack = Sequence(headsUp, Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout),
                             ActorInterval(suit, 'effort', playRate=1.25), suitReset, Func(suit.setNeutralAnimation))
        toonTrack = Sequence(
            Wait(2.0),
            Parallel(
                Func(toon.enterFlattened),
            ),
            Wait(1.0),
            Parallel(
                Sequence(
                    Wait(0.5),
                    Func(toon.exitFlattened)
                ),
                SoundInterval(globalBattleSoundCache.getSound('toon_decompress.ogg'), node=toon)),
                Sequence(
                    ActorInterval(toon, 'jump'),
                    Func(toon.loop, 'neutral')
                )
            )
        return Parallel(suitTrack, toonTrack, propTrack)

    def doEnraged(self, attack, suit):
        taunt = random.choice(
            ["I've had enough of all of this!",
"You got the goat, Toons!",
"You made me maaa-d!"])
        soundTrack = Sequence(
                        SoundInterval(globalBattleSoundCache.getSound('SA_rage.ogg'), node=suit))
        suitTrack = Sequence(ActorInterval(suit, 'rage'), Func(suit.makeAngry), Func(suit.setNeutralAnimation))
        headInterval = Sequence(MovieUtil.createSuitEnragedInterval(suit, 0))
        tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
        return Parallel(suitTrack, soundTrack, headInterval, tauntInterval)

    def doPoisonSpray(self, attack, suit):
        taunt = random.choice(
            ["I can take it!",
"My guard is up!",
"It's just a scratch!",
"Is that the best these Toons have?"])
        suitTrack = Sequence(ActorInterval(suit, 'defense'), Func(suit.makeShielding), Func(suit.setNeutralAnimation))
        tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
        soundTrack = Sequence(SoundInterval(globalBattleSoundCache.getSound('SA_defense.ogg'), node=suit))
        return Parallel(suitTrack, soundTrack, tauntInterval)

    def doCourtSanction(self, attack, suit):
        battle = attack['battle']
        target = attack['target']
        dmg = target[0]['hp']
        toon = target[0]['toon']
        sanctioned = self.__makeSanctionedNodePath()
        missPoint = lambda sanctioned=sanctioned, toon=toon: __toonMissPoint(sanctioned, toon)
        propTrack = Sequence(
            Wait(0.5),
            Func(battle.movie.needRestoreRenderProp, sanctioned),
            Func(sanctioned.reparentTo, render),
            Func(sanctioned.setScale, 0.6),
            Func(sanctioned.setPosHpr, suit.getLeftHand(), 0, 0.11, -0.16, 0, 100, 90),
            Func(sanctioned.setP, 0),
            Func(sanctioned.setR, 0),
            MovieSuitAttacks.getPropThrowTrack(attack, sanctioned, [toon.getPos(toon)], [missPoint], .25),
            Func(MovieUtil.removeProp, sanctioned),
            Func(battle.movie.clearRenderProp, sanctioned)
        )
        toonTrack = ActorInterval(toon, 'conked')
        tauntTrack = Func(suit.setChatAbsolute,
                          random.choice(("Someone isn't doing their part around here.", "What happened to your little strategy called, 'teamwork'?", "I spy with my little eye, a Toon who isn't pulling their weight.")),
                          CFSpeech | CFTimeout)
        # toonTrack = getToonTrack(attack, 0.8, ['conked'], 0.2, ['sidestep'])
        suitTrack = Sequence(ActorInterval(suit, 'sanction'), Func(suit.setNeutralAnimation))
        soundTrack = Sequence(Wait(0.5),
                    SoundInterval(globalBattleSoundCache.getSound('SA_sanction.ogg'), node=suit))
        notifyTrack = Sequence(Wait(.8), Func(toon.showHpTextCheat, - int(dmg / 2.2)),
                               Func(toon.showHpString, "SANCTIONED!"))
        return Parallel(suitTrack, toonTrack, propTrack, tauntTrack, soundTrack, notifyTrack)

    def doCourtRecord3(self, suit):
        tauntTrack = Func(suit.setChatAbsolute, 'Test Phrase.', CFSpeech | CFTimeout)
        suitTrack = Sequence(ActorInterval(suit, 'cease'), Func(suit.setNeutralAnimation))
        return Parallel(suitTrack, tauntTrack)

    def doCourtCalculations(self, attack, suit):
        calculator = BattleProps.globalPropPool.getProp('court-costs-calculator')
        suitTrack = Sequence(ActorInterval(suit, 'calculating-costs'), Func(suit.setNeutralAnimation),
                             Wait(2.0))
        suitSpeechTrack = Func(suit.setChatAbsolute,
                               "Calculating costs of litigation fees... Price index raised to %s." % (attack['target'][0]['hp'] + 4), CFSpeech | CFTimeout)
        calcPosPoints = [Point3(-0.35, 0.25, -0.1), VBase3(1.352, 0.0, 180.0)]
        calcDuration = 0.25
        scaleUpPoint = Point3(1.5, 1.5, 1.5)
        calcPropTrack = MovieSuitAttacks.getPropTrack(calculator, suit.getRightHand(), calcPosPoints, 0, calcDuration,
                                     scaleUpPoint=scaleUpPoint, scaleUpTime=0, anim=1,
                                     propName='court-costs-calculator', animStartTime=0,
                                     animDuration=2.9)
        soundTrack = Sequence(
                    SoundInterval(globalBattleSoundCache.getSound('SA_calculating_costs.ogg'), node=suit))
        return Parallel(suitTrack, soundTrack, suitSpeechTrack, calcPropTrack)

    def doCourtCalculations2(self, attack, suit):
        calculator = BattleProps.globalPropPool.getProp('court-costs-calculator')
        suitTrack = Sequence(ActorInterval(suit, 'calculating-costs'), Func(suit.setNeutralAnimation),
                             Wait(2.0))
        suitSpeechTrack = Func(suit.setChatAbsolute,
                               "Calculating costs of litigation fees... Price index raised to %s." % (attack['target'][0]['hp'] + 6), CFSpeech | CFTimeout)
        calcPosPoints = [Point3(-0.35, 0.25, -0.1), VBase3(1.352, 0.0, 180.0)]
        calcDuration = 0.25
        scaleUpPoint = Point3(1.5, 1.5, 1.5)
        calcPropTrack = MovieSuitAttacks.getPropTrack(calculator, suit.getRightHand(), calcPosPoints, 0, calcDuration,
                                     scaleUpPoint=scaleUpPoint, scaleUpTime=0, anim=1,
                                     propName='court-costs-calculator', animStartTime=0,
                                     animDuration=2.9)
        soundTrack = Sequence(
                    SoundInterval(globalBattleSoundCache.getSound('SA_calculating_costs.ogg'), node=suit))
        return Parallel(suitTrack, soundTrack, suitSpeechTrack, calcPropTrack)

    def doCourtCalculationsWiretapper(self, attack, suit):
        calculator = BattleProps.globalPropPool.getProp('court-costs-calculator')
        suitTrack = Sequence(ActorInterval(suit, 'calculating-costs'), Func(suit.setNeutralAnimation),
                             Wait(2.0))
        suitSpeechTrack = Func(suit.setChatAbsolute,
                               "Calculating costs of collect call fees... Price index raised to %s." % (attack['target'][0]['hp'] + 4), CFSpeech | CFTimeout)
        calcPosPoints = [Point3(-0.35, 0.25, -0.1), VBase3(1.352, 0.0, 180.0)]
        calcDuration = 0.25
        scaleUpPoint = Point3(1.5, 1.5, 1.5)
        calcPropTrack = MovieSuitAttacks.getPropTrack(calculator, suit.getRightHand(), calcPosPoints, 0, calcDuration,
                                     scaleUpPoint=scaleUpPoint, scaleUpTime=0, anim=1,
                                     propName='court-costs-calculator', animStartTime=0,
                                     animDuration=2.9)
        soundTrack = Sequence(
                    SoundInterval(globalBattleSoundCache.getSound('SA_calculating_costs.ogg'), node=suit))
        return Parallel(suitTrack, soundTrack, suitSpeechTrack, calcPropTrack)

    def doCourtCalculations2Wiretapper(self, attack, suit):
        calculator = BattleProps.globalPropPool.getProp('court-costs-calculator')
        suitTrack = Sequence(ActorInterval(suit, 'calculating-costs'), Func(suit.setNeutralAnimation),
                             Wait(2.0))
        suitSpeechTrack = Func(suit.setChatAbsolute,
                               "Calculating costs of collect call fees... Price index raised to %s." % (attack['target'][0]['hp'] + 6), CFSpeech | CFTimeout)
        calcPosPoints = [Point3(-0.35, 0.25, -0.1), VBase3(1.352, 0.0, 180.0)]
        calcDuration = 0.25
        scaleUpPoint = Point3(1.5, 1.5, 1.5)
        calcPropTrack = MovieSuitAttacks.getPropTrack(calculator, suit.getRightHand(), calcPosPoints, 0, calcDuration,
                                     scaleUpPoint=scaleUpPoint, scaleUpTime=0, anim=1,
                                     propName='court-costs-calculator', animStartTime=0,
                                     animDuration=2.9)
        soundTrack = Sequence(
                    SoundInterval(globalBattleSoundCache.getSound('SA_calculating_costs.ogg'), node=suit))
        return Parallel(suitTrack, soundTrack, suitSpeechTrack, calcPropTrack)

    def doCaseInsurancePlan(self, suit):
        theSuit = suit
        if theSuit.dna.name == 'csm':
            taunt = 'Hrm...'
        else:
            taunt = 'AHH!'

        suitTracks = Parallel()
        tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
        for suit in self.battle.activeSuits:
            suitTrack = Sequence()
            suitTrack.append(Wait(4.5))
            currentBossHealth = -1
            for s in self.battle.suits:
                if s.dna.name == 'scg':
                    currentBossHealth = s.currHP
            if currentBossHealth >= 1:
                x = int((suit.maxHP * suit.hardMaxHP) - suit.currHP)
                if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
                    suitTrack.append(Func(suit.showHpText, 0))
                    suitTrack.append(Func(suit.showHpString, "INSURANCE!"))
                elif suit.currHP + 85 > (suit.maxHP * suit.hardMaxHP):
                    suitTrack.append(Func(suit.showHpTextCheat, x))
                    suitTrack.append(Func(suit.showHpString, "INSURANCE!"))
                    suitTrack.append(Func(suit.setHealthForMe, 85))
                else:
                    suitTrack.append(Func(suit.showHpTextCheat, 85))
                    suitTrack.append(Func(suit.showHpString, "INSURANCE!"))
                    suitTrack.append(Func(suit.setHealthForMe, 85))
            else:
                x = int((suit.maxHP * suit.hardMaxHP) - suit.currHP)
                if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
                    suitTrack.append(Func(suit.showHpText, 0))
                    suitTrack.append(Func(suit.showHpString, "INSURANCE!"))
                elif suit.currHP + 50 > (suit.maxHP * suit.hardMaxHP):
                    suitTrack.append(Func(suit.showHpTextCheat, x))
                    suitTrack.append(Func(suit.showHpString, "INSURANCE!"))
                    suitTrack.append(Func(suit.setHealthForMe, x))
                else:
                    suitTrack.append(Func(suit.showHpTextCheat, 50))
                    suitTrack.append(Func(suit.showHpString, "INSURANCE!"))
                    suitTrack.append(Func(suit.setHealthForMe, 50))
            suitTrack.append(Func(suit.updateHealthBar, 0))
            if not suit.dna.name == 'csm':
                suitTrack.append(Parallel(Sequence(Wait(4.0)), Func(suit.setChatAbsolute, random.choice(
                    OTPLocalizerEnglish.SuitHealingPhrases), CFSpeech | CFTimeout)))
            suitTrack.append(Func(suit.setNeutralAnimation))
            suitTrack.append(Func(suit.makeInsured))
            suitTracks.append(suitTrack)
            suitTracks.append(tauntInterval)
            suitTracks.append(MovieUtil.createSuitInsuranceInterval(theSuit))
            suitTracks.append(Wait(6.5))
        posPoints = [Point3(0.375, -1.5, .85), VBase3(0, 220, -10)]
        knifeTracks = Parallel()
        for suit in self.battle.activeSuits:
            if suit.dna.name == 'csm':
                theSuit = suit
            hitPoint = suit.getPos(self.battle)
            hitPoint.setZ(suit.height + 2)
            hitPoint.setY(hitPoint.getY() + 0.5)
            knife = BattleProps.globalPropPool.getProp('shredder-paper')
            knifeTrack = Sequence(
                MovieSuitAttacks.getPropAppearTrack(knife, theSuit.getRightHand(), posPoints, .5, VBase3(1, 1, 1),
                                   scaleUpTime=0.1),
                Wait(2.3),
                Parallel(
                    MovieSuitAttacks.getThrowTrack(knife, hitPoint, 1.5, self.battle, -30.288),
                    LerpHprInterval(knife, 0.8, VBase3(0, -20, -20))),
                Parallel(
                    LerpPosInterval(knife, 1, VBase3(hitPoint.getX(), hitPoint.getY() + 0.5, hitPoint.getZ() - 10)),
                    Sequence(Wait(0.25), LerpScaleInterval(knife, 0.5, VBase3(0, 0, 0)))),
                Func(MovieUtil.removeProp, knife)
            )
            knifeTracks.append(knifeTrack)
        # cameraTrack = Sequence(LerpPosHprInterval(camera, duration=0.95, pos=Point3(0, -15, 2), hpr=Point3(0, 0, 0), blendType='easeInOut'))
        suitTrack = Sequence(Wait(6.0), Func(suit.setNeutralAnimation))
        # insuranceTrack = MovieUtil.createSuitInsuranceInterval(suit)
        soundTrack1 = Sequence(SoundInterval(globalBattleSoundCache.getSound('SA_insurance.ogg'), node=suit))
        soundTrack2 = Sequence(Wait(2.8), SoundInterval(globalBattleSoundCache.getSound('SA_extra_tip.ogg'), node=suit))
        multiTrack = Parallel(soundTrack1, soundTrack2)
        healSound = Sequence(Wait(4.5), SoundInterval(globalBattleSoundCache.getSound('LB_toonup.ogg'), node=suit))
        return Parallel(suitTrack, suitTracks, healSound, multiTrack, knifeTracks)

    def doCaseInsurancePlanSkelecog(self, suit):
        theSuit = suit
        if theSuit.dna.name == 'csm':
            taunt = random.choice(
                ["Hmph...", "Hrnhmpf...",
                 "Hrm...",
                 "Hm, hm..."])
        else:
            taunt = 'AHH'

        suitTracks = Parallel()
        tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
        for suit in self.battle.activeSuits:
            suitTrack = Sequence()
            suitTrack.append(Wait(4.5))
            currentBossHealth = -1
            for s in self.battle.suits:
                if s.dna.name == 'scg':
                    currentBossHealth = s.currHP
            if currentBossHealth >= 1:
                x = int((suit.maxHP * suit.hardMaxHP) - suit.currHP)
                if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
                    suitTrack.append(Func(suit.showHpText, 0))
                    suitTrack.append(Func(suit.showHpString, "INSURANCE!"))
                elif suit.currHP + 85 > (suit.maxHP * suit.hardMaxHP):
                    suitTrack.append(Func(suit.showHpTextCheat, x))
                    suitTrack.append(Func(suit.showHpString, "INSURANCE!"))
                    suitTrack.append(Func(suit.setHealthForMe, 85))
                else:
                    suitTrack.append(Func(suit.showHpTextCheat, 85))
                    suitTrack.append(Func(suit.showHpString, "INSURANCE!"))
                    suitTrack.append(Func(suit.setHealthForMe, 85))
            else:
                x = int((suit.maxHP * suit.hardMaxHP) - suit.currHP)
                if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
                    suitTrack.append(Func(suit.showHpText, 0))
                    suitTrack.append(Func(suit.showHpString, "INSURANCE!"))
                elif suit.currHP + 50 > (suit.maxHP * suit.hardMaxHP):
                    suitTrack.append(Func(suit.showHpTextCheat, x))
                    suitTrack.append(Func(suit.showHpString, "INSURANCE!"))
                    suitTrack.append(Func(suit.setHealthForMe, x))
                else:
                    suitTrack.append(Func(suit.showHpTextCheat, 50))
                    suitTrack.append(Func(suit.showHpString, "INSURANCE!"))
                    suitTrack.append(Func(suit.setHealthForMe, 50))
            suitTrack.append(Func(suit.updateHealthBar, 0))
            if not suit.dna.name == 'csm':
                suitTrack.append(Parallel(Sequence(Wait(4.0)), Func(suit.setChatAbsolute, random.choice(
                    OTPLocalizerEnglish.SuitHealingPhrases), CFSpeech | CFTimeout)))
            suitTrack.append(Func(suit.setNeutralAnimation))
            suitTrack.append(Func(suit.makeInsured))
            suitTracks.append(suitTrack)
            suitTracks.append(tauntInterval)
            suitTracks.append(ActorInterval(theSuit, 'throw-paper'))
            suitTracks.append(Wait(6.5))
        posPoints = [Point3(0.375, -1.5, .85), VBase3(0, 220, -10)]
        knifeTracks = Parallel()
        for suit in self.battle.activeSuits:
            if suit.dna.name == 'csm':
                theSuit = suit
            hitPoint = suit.getPos(self.battle)
            hitPoint.setZ(suit.height + 2)
            hitPoint.setY(hitPoint.getY() + 0.5)
            knife = BattleProps.globalPropPool.getProp('shredder-paper')
            knifeTrack = Sequence(
                MovieSuitAttacks.getPropAppearTrack(knife, theSuit.getRightHand(), posPoints, .5, VBase3(1, 1, 1),
                                   scaleUpTime=0.1),
                Wait(2.3),
                Parallel(
                    MovieSuitAttacks.getThrowTrack(knife, hitPoint, 1.5, self.battle, -30.288),
                    LerpHprInterval(knife, 0.8, VBase3(0, -20, -20))),
                Parallel(
                    LerpPosInterval(knife, 1, VBase3(hitPoint.getX(), hitPoint.getY() + 0.5, hitPoint.getZ() - 10)),
                    Sequence(Wait(0.25), LerpScaleInterval(knife, 0.5, VBase3(0, 0, 0)))),
                Func(MovieUtil.removeProp, knife)
            )
            knifeTracks.append(knifeTrack)
        # cameraTrack = Sequence(LerpPosHprInterval(camera, duration=0.95, pos=Point3(0, -15, 2), hpr=Point3(0, 0, 0), blendType='easeInOut'))
        suitTrack = Sequence(Wait(6.0), Func(suit.setNeutralAnimation))
        # insuranceTrack = MovieUtil.createSuitInsuranceInterval(suit)
        # soundTrack1 = getSoundTrack('SA_insurance.ogg', delay=0, node=suit)
        soundTrack2 = Sequence(Wait(2.8), SoundInterval(globalBattleSoundCache.getSound('SA_extra_tip.ogg'), node=suit))
        multiTrack = soundTrack2
        healSound = Sequence(Wait(4.5), SoundInterval(globalBattleSoundCache.getSound('LB_toonup.ogg'), node=suit))
        return Parallel(suitTrack, suitTracks, healSound, multiTrack, knifeTracks)

    def doCaseInsurancePlanInsurance(self, suit):
        theSuit = suit
        if theSuit.dna.name == 'csm':
            taunt = 'Hrm...'
        else:
            taunt = 'AHH!'

        suitTracks = Parallel()
        tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
        for suit in self.battle.activeSuits:
            suitTrack = Sequence()
            suitTrack.append(Wait(4.5))
            x = int((suit.maxHP * suit.hardMaxHP) - suit.currHP)
            if suit.currHP >= (suit.maxHP * suit.hardMaxHP) and not suit.isLured:
                suitTrack.append(Func(suit.showHpText, 0))
            elif suit.currHP + 50 > (suit.maxHP * suit.hardMaxHP) and not suit.isLured:
                suitTrack.append(Func(suit.setHealthForMe, 0))
            elif not suit.isLured:
                suitTrack.append(Func(suit.setHealthForMe, 0))
            suitTrack.append(Func(suit.showHpTextWhite, "INSURANCE!", 0))
            suitTrack.append(Func(suit.updateHealthBar, 0))
            if not suit.dna.name == 'csm':
                suitTrack.append(Parallel(Sequence(Wait(4.0)), Func(suit.setChatAbsolute, random.choice(
                    OTPLocalizerEnglish.SuitHealingPhrases), CFSpeech | CFTimeout)))
            suitTrack.append(Func(suit.setNeutralAnimation))
            suitTrack.append(Func(suit.makeInsured))
            suitTracks.append(suitTrack)
            suitTracks.append(tauntInterval)
            suitTracks.append(MovieUtil.createSuitInsuranceInterval(theSuit))
            suitTracks.append(Wait(6.5))
        posPoints = [Point3(0.375, -1.5, .85), VBase3(0, 220, -10)]
        knifeTracks = Parallel()
        for suit in self.battle.activeSuits:
            if suit.dna.name == 'csm':
                theSuit = suit
            hitPoint = suit.getPos(self.battle)
            hitPoint.setZ(suit.height + 2)
            hitPoint.setY(hitPoint.getY() + 0.5)
            knife = BattleProps.globalPropPool.getProp('shredder-paper')
            knifeTrack = Sequence(
                MovieSuitAttacks.getPropAppearTrack(knife, theSuit.getRightHand(), posPoints, .5, VBase3(1, 1, 1),
                                   scaleUpTime=0.1),
                Wait(2.3),
                Parallel(
                    MovieSuitAttacks.getThrowTrack(knife, hitPoint, 1.5, self.battle, -30.288),
                    LerpHprInterval(knife, 0.8, VBase3(0, -20, -20))),
                Parallel(
                    LerpPosInterval(knife, 1, VBase3(hitPoint.getX(), hitPoint.getY() + 0.5, hitPoint.getZ() - 10)),
                    Sequence(Wait(0.25), LerpScaleInterval(knife, 0.5, VBase3(0, 0, 0)))),
                Func(MovieUtil.removeProp, knife)
            )
            knifeTracks.append(knifeTrack)
        # cameraTrack = Sequence(LerpPosHprInterval(camera, duration=0.95, pos=Point3(0, -15, 2), hpr=Point3(0, 0, 0), blendType='easeInOut'))
        suitTrack = Sequence(Wait(6.0), Func(suit.setNeutralAnimation))
        # insuranceTrack = MovieUtil.createSuitInsuranceInterval(suit)
        soundTrack1 = Sequence(SoundInterval(globalBattleSoundCache.getSound('SA_insurance.ogg'), node=suit))
        soundTrack2 = Sequence(Wait(2.8), SoundInterval(globalBattleSoundCache.getSound('SA_extra_tip.ogg'), node=suit))
        multiTrack = Parallel(soundTrack1, soundTrack2)
        healSound = Sequence(Wait(4.5), SoundInterval(globalBattleSoundCache.getSound('LB_toonup.ogg'), node=suit))
        return Parallel(suitTrack, suitTracks, healSound, multiTrack, knifeTracks)

    def doCaseInsurancePlanSkelecogInsurance(self, suit):
        theSuit = suit
        if theSuit.dna.name == 'csm':
            taunt = random.choice(
                ["Hmph...", "Hrnhmpf...",
                 "Hrm...",
                 "Hm, hm..."])
        else:
            taunt = 'AHH'

        suitTracks = Parallel()
        tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
        for suit in self.battle.activeSuits:
            suitTrack = Sequence()
            suitTrack.append(Wait(4.5))
            x = int((suit.maxHP * suit.hardMaxHP) - suit.currHP)
            if suit.currHP >= (suit.maxHP * suit.hardMaxHP) and not suit.isLured and not suit.isInsured:
                suitTrack.append(Func(suit.showHpText, 0))
            elif suit.currHP + 50 > (suit.maxHP * suit.hardMaxHP) and not suit.isLured and not suit.isInsured:
                suitTrack.append(Func(suit.setHealthForMe, 0))
            elif not suit.isLured:
                suitTrack.append(Func(suit.setHealthForMe, 0))
            suitTrack.append(Func(suit.showHpTextWhite, "INSURANCE!", 0))
            suitTrack.append(Func(suit.updateHealthBar, 0))
            if not suit.dna.name == 'csm':
                suitTrack.append(Parallel(Sequence(Wait(4.0)), Func(suit.setChatAbsolute, random.choice(
                    OTPLocalizerEnglish.SuitHealingPhrases), CFSpeech | CFTimeout)))
            suitTrack.append(Func(suit.setNeutralAnimation))
            suitTrack.append(Func(suit.makeInsured))
            suitTracks.append(suitTrack)
            suitTracks.append(tauntInterval)
            suitTracks.append(ActorInterval(theSuit, 'throw-paper'))
            suitTracks.append(Wait(6.5))
        posPoints = [Point3(0.375, -1.5, .85), VBase3(0, 220, -10)]
        knifeTracks = Parallel()
        for suit in self.battle.activeSuits:
            if suit.dna.name == 'csm':
                theSuit = suit
            hitPoint = suit.getPos(self.battle)
            hitPoint.setZ(suit.height + 2)
            hitPoint.setY(hitPoint.getY() + 0.5)
            knife = BattleProps.globalPropPool.getProp('shredder-paper')
            knifeTrack = Sequence(
                MovieSuitAttacks.getPropAppearTrack(knife, theSuit.getRightHand(), posPoints, .5, VBase3(1, 1, 1),
                                   scaleUpTime=0.1),
                Wait(2.3),
                Parallel(
                    MovieSuitAttacks.getThrowTrack(knife, hitPoint, 1.5, self.battle, -30.288),
                    LerpHprInterval(knife, 0.8, VBase3(0, -20, -20))),
                Parallel(
                    LerpPosInterval(knife, 1, VBase3(hitPoint.getX(), hitPoint.getY() + 0.5, hitPoint.getZ() - 10)),
                    Sequence(Wait(0.25), LerpScaleInterval(knife, 0.5, VBase3(0, 0, 0)))),
                Func(MovieUtil.removeProp, knife)
            )
            knifeTracks.append(knifeTrack)
        # cameraTrack = Sequence(LerpPosHprInterval(camera, duration=0.95, pos=Point3(0, -15, 2), hpr=Point3(0, 0, 0), blendType='easeInOut'))
        suitTrack = Sequence(Wait(6.0), Func(suit.setNeutralAnimation))
        # insuranceTrack = MovieUtil.createSuitInsuranceInterval(suit)
        # soundTrack1 = getSoundTrack('SA_insurance.ogg', delay=0, node=suit)
        soundTrack2 = Sequence(Wait(2.8), SoundInterval(globalBattleSoundCache.getSound('SA_extra_tip.ogg'), node=suit))
        multiTrack = soundTrack2
        healSound = Sequence(Wait(4.5), SoundInterval(globalBattleSoundCache.getSound('LB_toonup.ogg'), node=suit))
        return Parallel(suitTrack, suitTracks, healSound, multiTrack, knifeTracks)

    def finish(self):
        self.track.finish()

    def playReward(self, ts, name, callback, noSkip = False):
        self.rewardHasBeenReset = 0
        ptrack = Sequence()
        camtrack = Sequence()
        self.rewardPanel = RewardPanel.RewardPanel(name)
        self.rewardPanel.hide()
        victory, camVictory, skipper = MovieToonVictory.doToonVictory(self.battle.localToonActive(), self.battle.activeToons, self.toonRewardIds, self.toonRewardDicts, self.deathList, self.rewardPanel, 1, self.uberList, self.helpfulToonsList, noSkip=noSkip)
        if victory:
            skipper.setIvals((ptrack, camtrack), ptrack.getDuration())
            ptrack.append(victory)
            camtrack.append(camVictory)
        ptrack.append(Func(callback))
        self._deleteTrack()
        self.track = Sequence(ptrack, name='movie-reward-track-%d' % self.battle.doId)
        if self.battle.localToonActive():
            self.track = Parallel(self.track, camtrack, name='movie-reward-track-with-cam-%d' % self.battle.doId)
        self.track.delayDeletes = []
        for t in self.battle.activeToons:
            self.track.delayDeletes.append(DelayDelete.DelayDelete(t, 'Movie.playReward'))

        skipper.setIvals((self.track,), 0.0)
        skipper.setBattle(self.battle)
        self.track.start(ts)

    def playTutorialReward(self, ts, name, callback):
        self.rewardHasBeenReset = 0
        self.rewardPanel = RewardPanel.RewardPanel(name)
        self.rewardCallback = callback
        self.questList = self.rewardPanel.getQuestIntervalList(base.localAvatar, [0,
         1,
         1,
         0], [base.localAvatar], base.localAvatar.quests[0], [], [base.localAvatar.getDoId()])
        camera.setPosHpr(0, 8, base.localAvatar.getHeight() * 0.66, 179, 15, 0)
        self.playTutorialReward_1()

    def playTutorialReward_1(self):
        self.tutRewardDialog_1 = TTDialog.TTDialog(text=TTLocalizer.MovieTutorialReward1, command=self.playTutorialReward_2, style=TTDialog.Acknowledge, fadeScreen=None, pos=(0.65, 0, 0.5), scale=0.8)
        self.tutRewardDialog_1.hide()
        self._deleteTrack()
        self.track = Sequence(name='tutorial-reward-1')
        self.track.append(Func(self.rewardPanel.initGagFrame, base.localAvatar, [0,
         0,
         0,
         0,
         0,
         0,
         0,
         0], [0,
         0,
         0,
         0,
         0], noSkip=True))
        self.track += self.rewardPanel.getTrackIntervalList(base.localAvatar, THROW_TRACK, 0, 1, 0)
        self.track.append(Func(self.tutRewardDialog_1.show))
        self.track.start()

    def playTutorialReward_2(self, value):
        self.tutRewardDialog_1.cleanup()
        self.tutRewardDialog_2 = TTDialog.TTDialog(text=TTLocalizer.MovieTutorialReward2, command=self.playTutorialReward_3, style=TTDialog.Acknowledge, fadeScreen=None, pos=(0.65, 0, 0.5), scale=0.8)
        self.tutRewardDialog_2.hide()
        self._deleteTrack()
        self.track = Sequence(name='tutorial-reward-2')
        self.track.append(Wait(1.0))
        self.track += self.rewardPanel.getTrackIntervalList(base.localAvatar, SQUIRT_TRACK, 0, 1, 0)
        self.track.append(Func(self.tutRewardDialog_2.show))
        self.track.start()

    def playTutorialReward_3(self, value):
        self.tutRewardDialog_2.cleanup()
        from toontown.toon import Toon
        from toontown.toon import ToonDNA

        def doneChat1(page, elapsed = 0):
            self.track2.start()

        def doneChat2(elapsed):
            self.track2.pause()
            self.track3.start()

        def uniqueName(hook):
            return 'TutorialTom-' + hook

        self.tutorialTom = Toon.Toon()
        dna = ToonDNA.ToonDNA()
        dnaList = ('dls', 'ms', 'm', 'm', 7, 0, 7, 7, 2, 6, 2, 6, 2, 16)
        dna.newToonFromProperties(*dnaList)
        self.tutorialTom.setDNA(dna)
        self.tutorialTom.setName(TTLocalizer.NPCToonNames[20000])
        self.tutorialTom.setPickable(0)
        self.tutorialTom.setPlayerType(NametagGlobals.CCNonPlayer)
        self.tutorialTom.uniqueName = uniqueName
        if base.config.GetString('language', 'english') == 'japanese':
            self.tomDialogue03 = base.loader.loadSfx('phase_3.5/audio/dial/CC_tom_movie_tutorial_reward01.ogg')
            self.tomDialogue04 = base.loader.loadSfx('phase_3.5/audio/dial/CC_tom_movie_tutorial_reward02.ogg')
            self.tomDialogue05 = base.loader.loadSfx('phase_3.5/audio/dial/CC_tom_movie_tutorial_reward03.ogg')
            self.musicVolume = base.config.GetFloat('tutorial-music-volume', 0.5)
        else:
            self.tomDialogue03 = None
            self.tomDialogue04 = None
            self.tomDialogue05 = None
            self.musicVolume = 0.9
        music = base.cr.playGame.place.loader.battleMusic
        if self.questList:
            self.track1 = Sequence(Wait(1.0), Func(self.rewardPanel.initQuestFrame, base.localAvatar, copy.deepcopy(base.localAvatar.quests)), Wait(1.0), Sequence(*self.questList), Wait(1.0), Func(self.rewardPanel.hide), Func(camera.setPosHpr, render, 34, 19.88, 3.48, -90, -2.36, 0), Func(base.localAvatar.animFSM.request, 'neutral'), Func(base.localAvatar.setPosHpr, 40.31, 22.0, -0.47, 150.0, 360.0, 0.0), Wait(0.5), Func(self.tutorialTom.reparentTo, render), Func(self.tutorialTom.show), Func(self.tutorialTom.setPosHpr, 40.29, 17.9, -0.47, 11.31, 0.0, 0.07), Func(self.tutorialTom.animFSM.request, 'TeleportIn'), Wait(1.517), Func(self.tutorialTom.animFSM.request, 'neutral'), Func(self.acceptOnce, self.tutorialTom.uniqueName('doneChatPage'), doneChat1), Func(self.tutorialTom.addActive), Func(music.setVolume, self.musicVolume), Func(self.tutorialTom.setLocalPageChat, TTLocalizer.MovieTutorialReward3, 0, None, [self.tomDialogue03]), name='tutorial-reward-3a')
            self.track2 = Sequence(Func(self.acceptOnce, self.tutorialTom.uniqueName('doneChatPage'), doneChat2), Func(self.tutorialTom.setLocalPageChat, TTLocalizer.MovieTutorialReward4, 1, None, [self.tomDialogue04]), Func(self.tutorialTom.setPlayRate, 1.5, 'right-hand-start'), Func(self.tutorialTom.play, 'right-hand-start'), Wait(self.tutorialTom.getDuration('right-hand-start') / 1.5), Func(self.tutorialTom.loop, 'right-hand'), name='tutorial-reward-3b')
            self.track3 = Parallel(Sequence(Func(self.tutorialTom.setPlayRate, -1.8, 'right-hand-start'), Func(self.tutorialTom.play, 'right-hand-start'), Wait(self.tutorialTom.getDuration('right-hand-start') / 1.8), Func(self.tutorialTom.animFSM.request, 'neutral'), name='tutorial-reward-3ca'), Sequence(Wait(0.5), Func(self.tutorialTom.setChatAbsolute, TTLocalizer.MovieTutorialReward5, CFSpeech | CFTimeout, self.tomDialogue05), Wait(1.0), Func(self.tutorialTom.animFSM.request, 'TeleportOut'), Wait(self.tutorialTom.getDuration('teleport')), Wait(1.0), Func(self.playTutorialReward_4, 0), name='tutorial-reward-3cb'), name='tutorial-reward-3c')
            self.track1.start()
        else:
            self.playTutorialReward_4(0)

    def playTutorialReward_4(self, value):
        base.localAvatar.setH(270)
        self.tutorialTom.removeActive()
        self.tutorialTom.delete()
        self.questList = None
        self.rewardCallback()

    def stop(self):
        if self.track:
            self.track.finish()
            self._deleteTrack()
        if hasattr(self, 'track1'):
            self.track1.finish()
            self.track1 = None
        if hasattr(self, 'track2'):
            self.track2.finish()
            self.track2 = None
        if hasattr(self, 'track3'):
            self.track3.finish()
            self.track3 = None
        if self.rewardPanel:
            self.rewardPanel.hide()
        if self.playByPlayText:
            self.playByPlayText.hide()

    def __doToonAttacks(self):
        if base.config.GetBool('want-toon-attack-anims', 1):
            track = Sequence(name='toon-attacks')
            camTrack = Sequence(name='toon-attacks-cam')
            ival, camIval = MovieFire.doFires(self.__findToonAttack(FIRE))
            if ival:
                track.append(ival)
                camTrack.append(camIval)
            ival, camIval = MovieSOS.doSOSs(self.__findToonAttack(SOS))
            if ival:
                track.append(ival)
                camTrack.append(camIval)
            ival, camIval = MovieNPCSOS.doNPCSOSs(self.__findToonAttack(NPCSOS))
            if ival:
                track.append(ival)
                camTrack.append(camIval)
            ival, camIval = MoviePetSOS.doPetSOSs(self.__findToonAttack(PETSOS))
            if ival:
                track.append(ival)
                camTrack.append(camIval)
            hasHealBonus = self.battle.getInteractivePropTrackBonus() == HEAL
            ival, camIval = MovieHeal.doHeals(self.__findToonAttack(HEAL), hasHealBonus)
            if ival:
                track.append(ival)
                camTrack.append(camIval)
            ival, camIval = MovieTrap.doTraps(self.__findToonAttack(TRAP))
            if ival:
                track.append(ival)
                camTrack.append(camIval)
            ival, camIval = MovieLure.doLures(self.__findToonAttack(LURE))
            if ival:
                track.append(ival)
                camTrack.append(camIval)
            ival, camIval = MovieThrow.doThrows(self.__findToonAttack(THROW))
            if ival:
                track.append(ival)
                camTrack.append(camIval)
            ival, camIval = MovieSquirt.doSquirts(self.__findToonAttack(SQUIRT))
            if ival:
                track.append(ival)
                camTrack.append(camIval)
            ival, camIval = MovieSound.doSounds(self.__findToonAttack(SOUND))
            if ival:
                track.append(ival)
                camTrack.append(camIval)
            ival, camIval = MovieZap.doZaps(self.__findToonAttack(ZAP))
            if ival:
                track.append(ival)
                camTrack.append(camIval)
            ival, camIval = MovieDrop.doDrops(self.__findToonAttack(DROP))
            if ival:
                track.append(ival)
                camTrack.append(camIval)
            if len(track) == 0:
                return (None, None)
            else:
                return (track, camTrack)
        else:
            return (None, None)

    def genRewardDicts(self, id0, origExp0, earnedExp0, origQuests0, items0, missedItems0, origMerits0, merits0, parts0, id1, origExp1, earnedExp1, origQuests1, items1, missedItems1, origMerits1, merits1, parts1, id2, origExp2, earnedExp2, origQuests2, items2, missedItems2, origMerits2, merits2, parts2, id3, origExp3, earnedExp3, origQuests3, items3, missedItems3, origMerits3, merits3, parts3, deathList, uberList, helpfulToonsList):
        self.deathList = deathList
        self.helpfulToonsList = helpfulToonsList
        entries = ((id0,
          origExp0,
          earnedExp0,
          origQuests0,
          items0,
          missedItems0,
          origMerits0,
          merits0,
          parts0),
         (id1,
          origExp1,
          earnedExp1,
          origQuests1,
          items1,
          missedItems1,
          origMerits1,
          merits1,
          parts1),
         (id2,
          origExp2,
          earnedExp2,
          origQuests2,
          items2,
          missedItems2,
          origMerits2,
          merits2,
          parts2),
         (id3,
          origExp3,
          earnedExp3,
          origQuests3,
          items3,
          missedItems3,
          origMerits3,
          merits3,
          parts3))
        self.toonRewardDicts = BattleExperience.genRewardDicts(entries)
        self.toonRewardIds = [id0,
         id1,
         id2,
         id3]
        self.uberList = uberList

    def genAttackDicts(self, toons, suits, toonAttacks, suitAttacks):
        if self.track and self.track.isPlaying():
            self.notify.warning('genAttackDicts() - track is playing!')
        self.__genToonAttackDicts(toons, suits, toonAttacks)
        self.__genSuitAttackDicts(toons, suits, suitAttacks)

    def __genSuitCheatDicts(self, toons, suits, suitCheats):
        for suitCheat in suitCheats:
            targetGone = 0
            attack = suitCheat[SUIT_ATK_COL]
            suitIndex = suitCheat[SUIT_ID_COL]
            suitId = suits[suitIndex]
            suit = self.battle.findSuit(suitId)
            if not suit:
                self.notify.error('suit: %d not in battle!' % suitId)
            cheatDict = {}
            cheatDict['suit'] = suit
            cheatDict['battle'] = self.battle
            cheatDict['playByPlayText'] = self.playByPlayText
            cheatDict['taunt'] = suitCheat[SUIT_TAUNT_COL]
            hps = suitCheat[SUIT_HP_COL]
            if ATK_TGT_GROUP:
                targets = []
                for t in toons:
                    if t != -1:
                        target = self.battle.findToon(t)
                        if not target:
                            continue
                        targetIndex = toons.index(t)
                        tdict = {}
                        tdict['toon'] = target
                        tdict['hp'] = hps[targetIndex]
                        self.notify.debug('DAMAGE: toon: %d hit for hp: %d' % (target.doId, hps[targetIndex]))
                        tdict['died'] = suitCheat[TOON_DIED_COL] & 1 << targetIndex
                        targets.append(tdict)
                if len(targets) > 0:
                    cheatDict['target'] = targets
                else:
                    targetGone = 1
            elif ATK_TGT_SINGLE:
                targetIndex = suitCheat[SUIT_TGT_COL]
                targetId = toons[targetIndex]
                target = self.battle.findToon(targetId)
                if not target:
                    targetGone = 1
                else:
                    self.notify.debug('DAMAGE: toon: %d hit for hp: %d' % (target.doId, hps[targetIndex]))
                    tdict = {'toon': target,
                             'hp': hps[targetIndex],
                             'died': suitCheat[TOON_DIED_COL] & 1 << targetIndex}
                    toonIndex = self.battle.activeToons.index(target)
                    rightToons = []
                    for ti in xrange(0, toonIndex):
                        rightToons.append(self.battle.activeToons[ti])
                    lenToons = len(self.battle.activeToons)
                    leftToons = []
                    if lenToons > toonIndex + 1:
                        for ti in xrange(toonIndex + 1, lenToons):
                            leftToons.append(self.battle.activeToons[ti])
                    tdict['leftToons'] = leftToons
                    tdict['rightToons'] = rightToons
                    cheatDict['target'] = tdict
            else:
                self.notify.warning('got suit attack not group or single!')
            if targetGone == 0:
                self.suitCheatDicts.append(cheatDict)
            else:
                self.notify.warning('genSuitCheatDicts() - target gone!')
        return

    def __doSuitCheats(self):
        if base.config.GetBool('want-suit-anims', 1):
            track = Sequence(name='suit-attacks')
            camTrack = Sequence(name='suit-attacks-cam')
            isLocalToonSad = False
            for cheat in self.suitCheatDicts:
                battle = cheat['battle']
                suit = cheat['suit']
                if battle.isSuitLured(suit):
                    resetTrack = MovieSuitAttacks.getResetTrack(suit, battle)
                    track.append(resetTrack)
                    waitTrack = Sequence(Wait(resetTrack.getDuration()), Func(battle.unlureSuit, suit))
                    camTrack.append(waitTrack)
                interval, cameraInterval = MovieSuitCheats.doSuitCheat(cheat)
                if interval:
                    track.append(interval)
                    camTrack.append(cameraInterval)
                targetField = cheat.get('target')
                if targetField is None:
                    continue
                for target in targetField:
                    if target['died'] and target['toon'].doId == base.localAvatar.doId:
                        isLocalToonSad = True
                
                if isLocalToonSad:
                    break
            if len(track) == 0:
                return None, None
            return track, camTrack
        else:
            return None, None

    def __genToonAttackDicts(self, toons, suits, toonAttacks):
        for ta in toonAttacks:
            targetGone = 0
            track = ta[TOON_TRACK_COL]
            if track != NO_ATTACK:
                adict = {}
                toonIndex = ta[TOON_ID_COL]
                toonId = toons[toonIndex]
                toon = self.battle.findToon(toonId)
                if toon == None:
                    continue
                level = ta[TOON_LVL_COL]
                adict['toon'] = toon
                adict['track'] = track
                adict['level'] = level
                hps = ta[TOON_HP_COL]
                kbbonuses = ta[TOON_KBBONUS_COL]
                if track == NPCSOS:
                    adict['npcId'] = ta[TOON_TGT_COL]
                    toonId = ta[TOON_TGT_COL]
                    track, npc_level, npc_hp = NPCToons.getNPCTrackLevelHp(adict['npcId'])
                    if track == None:
                        track = NPCSOS
                    adict['track'] = track
                    adict['level'] = npc_level
                elif track == PETSOS:
                    petId = ta[TOON_TGT_COL]
                    adict['toonId'] = toonId
                    adict['petId'] = petId
                if track == SOS:
                    targetId = ta[TOON_TGT_COL]
                    if targetId == base.localAvatar.doId:
                        target = base.localAvatar
                        adict['targetType'] = 'callee'
                    elif toon == base.localAvatar:
                        target = base.cr.identifyAvatar(targetId)
                        adict['targetType'] = 'caller'
                    else:
                        target = None
                        adict['targetType'] = 'observer'
                    adict['target'] = target
                elif track == NPCSOS or track == NPC_COGS_MISS or track == NPC_TOONS_HIT or track == NPC_RESTOCK_GAGS or track == NPC_DAMAGE_BOOST or track == PETSOS:
                    adict['special'] = 1
                    toonHandles = []
                    for t in toons:
                        if t != -1:
                            target = self.battle.findToon(t)
                            if target == None:
                                continue
                            if track == NPC_TOONS_HIT and t == toonId:
                                continue
                            toonHandles.append(target)

                    adict['toons'] = toonHandles
                    suitHandles = []
                    for s in suits:
                        if s != -1:
                            target = self.battle.findSuit(s)
                            if target == None:
                                continue
                            suitHandles.append(target)

                    adict['suits'] = suitHandles
                    if track == PETSOS:
                        del adict['special']
                        targets = []
                        for t in toons:
                            if t != -1:
                                target = self.battle.findToon(t)
                                if target == None:
                                    continue
                                tdict = {}
                                tdict['toon'] = target
                                tdict['hp'] = hps[toons.index(t)]
                                self.notify.debug('PETSOS: toon: %d healed for hp: %d' % (target.doId, hps[toons.index(t)]))
                                targets.append(tdict)

                        if len(targets) > 0:
                            adict['target'] = targets
                elif track == HEAL:
                    if levelAffectsGroup(HEAL, level):
                        targets = []
                        for t in toons:
                            if t != toonId and t != -1:
                                target = self.battle.findToon(t)
                                if target == None:
                                    continue
                                tdict = {}
                                tdict['toon'] = target
                                tdict['hp'] = hps[toons.index(t)]
                                self.notify.debug('HEAL: toon: %d healed for hp: %d' % (target.doId, hps[toons.index(t)]))
                                targets.append(tdict)

                        if len(targets) > 0:
                            adict['target'] = targets
                        else:
                            targetGone = 1
                    else:
                        targetIndex = ta[TOON_TGT_COL]
                        if targetIndex < 0:
                            targetGone = 1
                        else:
                            targetId = toons[targetIndex]
                            target = self.battle.findToon(targetId)
                            if target != None:
                                tdict = {}
                                tdict['toon'] = target
                                tdict['hp'] = hps[targetIndex]
                                adict['target'] = tdict
                            else:
                                targetGone = 1
                elif attackAffectsGroup(track, level, ta[TOON_TRACK_COL]):
                    targets = []
                    for s in suits:
                        if s != -1:
                            target = self.battle.findSuit(s)
                            if ta[TOON_TRACK_COL] == NPCSOS:
                                if track == LURE and self.battle.isSuitLured(target) == 1:
                                    continue
                                elif track == TRAP and (self.battle.isSuitLured(target) == 1 or target.battleTrap != NO_TRAP):
                                    continue
                            targetIndex = suits.index(s)
                            sdict = {}
                            sdict['suit'] = target
                            sdict['hp'] = hps[targetIndex]
                            if ta[TOON_TRACK_COL] == NPCSOS and track == DROP and hps[targetIndex] == 0:
                                continue
                            sdict['kbbonus'] = kbbonuses[targetIndex]
                            sdict['died'] = ta[SUIT_DIED_COL] & 1 << targetIndex
                            sdict['revived'] = ta[SUIT_REVIVE_COL] & 1 << targetIndex
                            if sdict['died'] != 0:
                                pass
                            sdict['leftSuits'] = []
                            sdict['rightSuits'] = []
                            targets.append(sdict)

                    adict['target'] = targets
                else:
                    targetIndex = ta[TOON_TGT_COL]
                    if targetIndex < 0:
                        targetGone = 1
                    else:
                        targetId = suits[targetIndex]
                        target = self.battle.findSuit(targetId)
                        sdict = {}
                        sdict['suit'] = target
                        if self.battle.activeSuits.count(target) == 0:
                            targetGone = 1
                            suitIndex = 0
                        else:
                            suitIndex = self.battle.activeSuits.index(target)
                        leftSuits = []
                        for si in xrange(0, suitIndex):
                            asuit = self.battle.activeSuits[si]
                            if self.battle.isSuitLured(asuit) == 0:
                                leftSuits.append(asuit)

                        lenSuits = len(self.battle.activeSuits)
                        rightSuits = []
                        if lenSuits > suitIndex + 1:
                            for si in xrange(suitIndex + 1, lenSuits):
                                asuit = self.battle.activeSuits[si]
                                if self.battle.isSuitLured(asuit) == 0:
                                    rightSuits.append(asuit)

                        sdict['leftSuits'] = leftSuits
                        sdict['rightSuits'] = rightSuits
                        sdict['hp'] = hps[targetIndex]
                        sdict['kbbonus'] = kbbonuses[targetIndex]
                        sdict['died'] = ta[SUIT_DIED_COL] & 1 << targetIndex
                        sdict['revived'] = ta[SUIT_REVIVE_COL] & 1 << targetIndex
                        if sdict['revived'] != 0:
                            pass
                        if sdict['died'] != 0:
                            pass
                        if track == DROP or track == LURE or track == TRAP:
                            adict['target'] = [sdict]
                        else:
                            adict['target'] = sdict
                adict['hpbonus'] = ta[TOON_HPBONUS_COL]
                adict['sidestep'] = ta[TOON_ACCBONUS_COL]
                if 'npcId' in adict:
                    adict['sidestep'] = 0
                adict['battle'] = self.battle
                adict['playByPlayText'] = self.playByPlayText
                if targetGone == 0:
                    self.toonAttackDicts.append(adict)
                else:
                    self.notify.warning('genToonAttackDicts() - target gone!')

        def compFunc(a, b):
            alevel = a['level']
            blevel = b['level']
            if alevel > blevel:
                return 1
            elif alevel < blevel:
                return -1
            return 0

        self.toonAttackDicts.sort(compFunc)
        return

    def __findToonAttack(self, track):
        setCapture = 0
        tp = []
        for ta in self.toonAttackDicts:
            if ta['track'] == track or track == NPCSOS and 'special' in ta:
                tp.append(ta)
                if track == SQUIRT:
                    setCapture = 1

        if track == TRAP:
            sortedTraps = []
            for attack in tp:
                if 'npcId' not in attack:
                    sortedTraps.append(attack)

            for attack in tp:
                if 'npcId' in attack:
                    sortedTraps.append(attack)

            tp = sortedTraps
        if setCapture:
            pass
        return tp

    def __genSuitAttackDicts(self, toons, suits, suitAttacks):
        for sa in suitAttacks:
            targetGone = 0
            attack = sa[SUIT_ATK_COL]
            if attack != NO_ATTACK:
                suitIndex = sa[SUIT_ID_COL]
                suitId = suits[suitIndex]
                suit = self.battle.findSuit(suitId)
                if suit == None:
                    self.notify.warning('suit: %d not in battle!' % suitId)
                    return
                adict = getSuitAttack(suit.getStyleName(), suit.getLevel(), attack)
                adict['suit'] = suit
                adict['battle'] = self.battle
                adict['playByPlayText'] = self.playByPlayText
                adict['taunt'] = sa[SUIT_TAUNT_COL]
                hps = sa[SUIT_HP_COL]
                if adict['group'] == ATK_TGT_GROUP:
                    targets = []
                    for t in toons:
                        if t != -1:
                            target = self.battle.findToon(t)
                            if target == None:
                                continue
                            targetIndex = toons.index(t)
                            tdict = {}
                            tdict['toon'] = target
                            tdict['hp'] = hps[targetIndex]
                            self.notify.debug('DAMAGE: toon: %d hit for hp: %d' % (target.doId, hps[targetIndex]))
                            toonDied = sa[TOON_DIED_COL] & 1 << targetIndex
                            tdict['died'] = toonDied
                            targets.append(tdict)

                    if len(targets) > 0:
                        adict['target'] = targets
                    else:
                        targetGone = 1
                elif adict['group'] == ATK_TGT_SINGLE or adict['group'] == ATK_TGT_DOUBLE:
                    targets = []
                    for targetIndex in sa[SUIT_TGT_COL]:
                        targetId = toons[targetIndex]
                        target = self.battle.findToon(targetId)
                        if target == None:
                            targetGone = 1
                            break
                        tdict = {}
                        tdict['toon'] = target
                        tdict['hp'] = hps[targetIndex]
                        self.notify.debug('DAMAGE: toon: %d hit for hp: %d' % (target.doId, hps[targetIndex]))
                        toonDied = sa[TOON_DIED_COL] & 1 << targetIndex
                        tdict['died'] = toonDied
                        toonIndex = self.battle.activeToons.index(target)
                        rightToons = []
                        for ti in xrange(0, toonIndex):
                            rightToons.append(self.battle.activeToons[ti])

                        lenToons = len(self.battle.activeToons)
                        leftToons = []
                        if lenToons > toonIndex + 1:
                            for ti in xrange(toonIndex + 1, lenToons):
                                leftToons.append(self.battle.activeToons[ti])

                        tdict['leftToons'] = leftToons
                        tdict['rightToons'] = rightToons
                        targets.append(tdict)

                    adict['target'] = targets
                else:
                    self.notify.warning('got suit attack not group or single!')
                if targetGone == 0:
                    self.suitAttackDicts.append(adict)
                else:
                    self.notify.warning('genSuitAttackDicts() - target gone!')

    def __doSuitAttacks(self):
        if base.config.GetBool('want-suit-anims', 1):
            track = Sequence(name='suit-attacks')
            camTrack = Sequence(name='suit-attacks-cam')
            isLocalToonSad = False
            for a in self.suitAttackDicts:
                ival, camIval = MovieSuitAttacks.doSuitAttack(a)
                if ival:
                    track.append(ival)
                    camTrack.append(camIval)
                targetField = a.get('target')
                if targetField is None:
                    continue
                # if a['group'] == ATK_TGT_GROUP:
                #     for target in targetField:
                #         if target['died'] and target['toon'].doId == base.localAvatar.doId:
                #             isLocalToonSad = False
                # 
                # elif a['group'] == ATK_TGT_SINGLE:
                #     if targetField['died'] and targetField['toon'].doId == base.localAvatar.doId:
                #         isLocalToonSad = False
                for target in targetField:
                    if target['died'] and target['toon'].doId == base.localAvatar.doId:
                        isLocalToonSad = False
                
                if isLocalToonSad:
                    continue

            if len(track) == 0:
                return (None, None)
            return (track, camTrack)
        else:
            return (None, None)
