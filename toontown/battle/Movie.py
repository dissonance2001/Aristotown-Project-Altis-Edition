from __future__ import absolute_import
import copy
import random
from direct.directnotify import DirectNotifyGlobal
from direct.interval.IntervalGlobal import *
from direct.interval.Interval import Interval
from pandac.PandaModules import CInterval, NodePath, TextNode
from direct.showbase import DirectObject
from toontown.battle.BattleBase import *
from toontown.battle import BattleExperience
from toontown.battle import BattleParticles
from toontown.battle.attacks.toons import MovieDrop
from toontown.battle import SuitBattleGlobals
from toontown.battle import BattleProps
from toontown.battle.attacks.toons import MovieFire
from toontown.battle.attacks.toons import MovieSue
from . import PlayByPlayText
from otp.otpbase import OTPLocalizerEnglish
from toontown.battle.BattleSounds import *
from toontown.battle.attacks.toons import MovieHeal
from toontown.battle.attacks.toons import MovieLure
from toontown.battle.attacks.toons import MovieNPCSOS
from toontown.battle.attacks.toons import MoviePetSOS
from toontown.battle.attacks.toons import MovieSOS
from toontown.battle.attacks.toons import MovieSound
from toontown.battle.attacks.toons import MovieSquirt
from toontown.battle.attacks.suits import MovieSuitAttacks
from toontown.battle.attacks.toons import MovieThrow
from toontown.battle import MovieToonVictory
from toontown.battle.attacks.toons import MovieTrap
from toontown.battle import MovieCamera
from toontown.battle.attacks.toons import MovieZap
from toontown.battle import MovieUtil
from toontown.battle import PlayByPlayText
from toontown.battle import RewardPanel
from toontown.battle.SuitBattleGlobals import *
from toontown.chat.ChatGlobals import *
from toontown.distributed import DelayDelete
from toontown.toon import NPCToons
from toontown.toon import IOURegistry
from toontown.toon import Toon
from toontown.toon import LaffMeter
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownGlobals
from toontown.toonbase.ToontownBattleGlobals import *
from toontown.toontowngui import TTDialog
from toontown.nametag import NametagGlobals
from six.moves import range

camPos = Point3(14, 0, 10)
camHpr = Vec3(89, -30, 0)
randomBattleTimestamp = base.config.GetBool('random-battle-timestamp', 0)

CONTENT_SYNC_CONDITION_ORDERS = {
    'contentSync1': [DROP, SQUIRT, ZAP, TRAP, THROW, LURE, SOUND, HEAL],
    'contentSync2': [SOUND, DROP, SQUIRT, HEAL, ZAP, TRAP, LURE, THROW],
    'contentSync3': [SQUIRT, SOUND, HEAL, TRAP, THROW, ZAP, LURE, DROP],
    'contentSync4': [SQUIRT, TRAP, LURE, DROP, HEAL, ZAP, SOUND, THROW],
    'contentSync5': [THROW, SOUND, DROP, TRAP, SQUIRT, HEAL, LURE, ZAP],
    'contentSync6': [THROW, SQUIRT, ZAP, SOUND, TRAP, LURE, DROP, HEAL],
    'contentSync7': [TRAP, DROP, SQUIRT, SOUND, THROW, ZAP, LURE, HEAL],
    'contentSync8': [TRAP, SQUIRT, DROP, THROW, ZAP, LURE, HEAL, SOUND],
}

class _PacesetterRealtimeInterval(Interval):

    _serial = 0

    def __init__(self, interval, battleSpeed):
        _PacesetterRealtimeInterval._serial += 1
        self.interval = interval
        self.battleSpeed = max(0.1, float(battleSpeed))
        self.innerDuration = interval.getDuration()
        Interval.__init__(
            self,
            'PacesetterRealtimeInterval-%d' % _PacesetterRealtimeInterval._serial,
            self.innerDuration * self.battleSpeed)

    def _innerTime(self, t):
        return max(0.0, min(self.innerDuration, float(t) / self.battleSpeed))

    def privInitialize(self, t):
        self.interval.privInitialize(self._innerTime(t))
        self.interval.privPostEvent()
        self.state = CInterval.SStarted
        self.currT = t

    def privStep(self, t):
        self.interval.privStep(self._innerTime(t))
        self.interval.privPostEvent()
        self.state = CInterval.SStarted
        self.currT = t

    def privFinalize(self):
        self.interval.privFinalize()
        self.interval.privPostEvent()
        self.state = CInterval.SFinal
        self.currT = self.getDuration()
        self.intervalDone()

    def privInstant(self):
        self.interval.privInstant()
        self.interval.privPostEvent()
        self.state = CInterval.SFinal
        self.currT = self.getDuration()
        self.intervalDone()

    def privInterrupt(self):
        self.interval.privInterrupt()
        self.interval.privPostEvent()
        self.state = CInterval.SPaused

    def privReverseInitialize(self, t):
        self.interval.privReverseInitialize(self._innerTime(t))
        self.interval.privPostEvent()
        self.state = CInterval.SStarted
        self.currT = t

    def privReverseFinalize(self):
        self.interval.privReverseFinalize()
        self.interval.privPostEvent()
        self.state = CInterval.SInitial
        self.currT = 0.0

    def privReverseInstant(self):
        self.interval.privReverseInstant()
        self.interval.privPostEvent()
        self.state = CInterval.SInitial
        self.currT = 0.0


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
        self.laffMeters = []
        self.laffMeterAvatars = []
        self.laffMeterByAvatarId = {}
        self.targetNodesMeters = {}
        self.targetSeqMeters = {}
        self.hasBeenReset = 0
        self.reset()
        self.rewardHasBeenReset = 0
        self.resetReward()

    def cleanup(self):
        self.reset()
        self.resetReward()
        # for toon in self.battle.activeToons:
        #     toon.makeUnCooldown()
        #     toon.makeUnBurned()
        #     toon.makeUnDamageOvertime()
        #     toon.makeUnBurned()
        #     toon.makeUnGroupDamageDown()
        #     toon.makeUnGagBoost()
        #     toon.makeUnCooldown()
        #     toon.makeUnMarkedWood()
        #     toon.makeUnInkDrain()
        #     toon.makeUnHidden()
        #     toon.makeUnCollectCalled()
        #     toon.makeUnNoDodge()
        #     toon.makeUnConfused()
        #     toon.makeUnMandatoryToll()
        #     toon.makeUnCheer()
        #     toon.makeUnDamageUp()
        #     toon.makeUnDamageUpGovernaught()
        #     toon.makeUnDamageDown()
        #     toon.makeUnDamageUp()
        #     toon.makeUnEncore()
        #     toon.makeUnWinded()
        #     toon.makeUnBombed()
        #     toon.makeUnGagBan()
        #     toon.makeUnVulnerable()
        #     toon.makeUnSnapped()
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
            for i in range(len(list)):
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
            for i in range(len(hitPoints)):
                pos = hitPoints[i]
                propTrack.append(LerpPosInterval(prop, hitDuration, pos=pos))

        else:
            for i in range(len(missPoints)):
                pos = missPoints[i]
                propTrack.append(LerpPosInterval(prop, missDuration, pos=pos))

            if missScaleDown:
                propTrack.append(LerpScaleInterval(prop, missScaleDown, MovieUtil.PNT3_NEARZERO))
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
                    for partNum in range(0, parts.getNumPaths()):
                        nextPart = parts.getPath(partNum)
                        nextPart.clearColorScale()
                        nextPart.clearTransparency()

            if self.restoreHips == 1:
                parts = toon.getHipsParts()
                for partNum in range(0, parts.getNumPaths()):
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
            for partNum in range(0, headParts.getNumPaths()):
                part = headParts.getPath(partNum)
                part.setHpr(0, 0, 0)
                part.setPos(0, 0, 0)

            arms = toon.findAllMatches('**/arms')
            sleeves = toon.findAllMatches('**/sleeves')
            hands = toon.findAllMatches('**/hands')
            for partNum in range(0, arms.getNumPaths()):
                armPart = arms.getPath(partNum)
                sleevePart = sleeves.getPath(partNum)
                handsPart = hands.getPath(partNum)
                armPart.setHpr(0, 0, 0)
                sleevePart.setHpr(0, 0, 0)
                handsPart.setHpr(0, 0, 0)

        for suit in self.battle.activeSuits:
            if suit._Actor__animControlDict != None:
                #suit.setNeutralAnimation()
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

    def __updateSuitRoundEffects(self, s):
        s.battleTrapIsFresh = 0
        if s.getOilRainRounds() == 1:
            s.removeOilRain()
        if not s.getOverseerRounds() <= 0:
            s.makeOverseer(s.getOverseerRounds() - 1)
        if not s.getSoakRounds() <= 0:
            s.makeSoaked(s.getSoakRounds() - 1)
        if not s.getDeepFrozenRounds() <= 0:
            s.makeDeepFrozen(s.getDeepFrozenRounds() - 1)
        if not s.getMarkRounds() <= 0:
            s.makeMarked(s.getMarkRounds() - 1)
        if not s.getOilRainRounds() <= 0:
            s.addOilRainRounds(s.getOilRainRounds() - 1)
        if not s.getEnrageCounter() <= 1:
            s.makeAngry(s.getEnrageCounter() - 1)
        if s.getEnrageCounter() <= 1 and s.dna.name in ('liquid', 'wtapper'):
            s.makeUnAngry()
        if s.dna.name == 'clubpres' and s.getActualLevel() == 21:
            s.makeExtraAttacks(s.getExtraAttacks() + 1)
        if s.getLuredRounds() == 1:
            s.makeUnLured()
        if s.getOverseerRounds() == 1:
            s.makeUnOverseer()
        if s.getDeepFrozenRounds() == 1:
            s.makeUnDeepFrozen()
        if not s.getLuredRounds() <= 0:
            s.addLuredRounds(s.getLuredRounds() - 1)
        if not s.getExplosiveCondition() <= 0:
            s.makeExplosive(s.getExplosiveCondition() - 1)
        if not s.getSleepyCondition() <= 0:
            s.makeSleepy(s.getSleepyCondition() - 1)
        if not s.getSuedRounds() <= 0:
            s.makeSued(s.getSuedRounds() - 1)
        if s.isDazed:
            s.makeUnDazed()
        if s.isGreenLight:
            s.makeUnGreenLight()
        if s.isRedLight:
            s.makeUnRedLight()
        if s.dna.name == 'ambass':
            s.makeUnShielding()


    def __cleanupSuitAfterMovie(self, s):
        s.battleTrapIsFresh = 0
        s.makeUnFreshlyZapped()
        s.checkInsuranceCountdown()
        s.checkContractedCountdown()
        s.clearPendingQueuedDamageAll()
        s.clearPendingQueuedHealingAll()
        s.setPendingQueuedDeath(False)


    def __updateToonRoundEffects(self, toon):
        for methodName in (
            'checkCooldownRoundCountdown',
            'checkDriedOutRoundCountdown',
            'checkEnergizedRoundCountdown',
            'checkHydrationRoundCountdown',
            'checkInkDrainRoundCountdown',
            'checkBombedRoundCountdown',
            'checkGroupDamageDownRoundCountdown',
            'checkGagBoostRoundCountdown',
            'checkNoDodgeRoundCountdown',
            'checkCollectCallRoundCountdown',
            'checkVulnerabilityRoundCountdown',
            'checkCheerRoundCountdown',
            'checkBurnedRoundCountdown',
            'checkZappedRoundCountdown',
            'checkSnappedRoundCountdown',
            'checkWindedRoundCountdown',
            'checkFrozenRoundCountdown',
            'checkToonupGagBoostRoundCountdown',
            'checkTrapGagBoostRoundCountdown',
            'checkLureGagBoostRoundCountdown',
            'checkThrowGagBoostRoundCountdown',
            'checkSquirtGagBoostRoundCountdown',
            'checkZapGagBoostRoundCountdown',
            'checkSoundGagBoostRoundCountdown',
            'checkDropGagBoostRoundCountdown',
            'checkEncoreRoundCountdown',
            'checkDamageUpRoundCountdown',
            'checkDamageDownRoundCountdown',
            'checkViralSensationRoundCountdown',
            'checkConfusedRoundCountdown',
            'checkHiddenRoundCountdown',
            'checkMarkedWoodRoundCountdown',
            'checkDamageOvertimeRoundCountdown',
            'checkLiquidatedRoundCountdown'
        ):
            if hasattr(toon, methodName):
                getattr(toon, methodName)()

    def _cleanupMovieLaffMeters(self):
        for seq in self.targetSeqMeters.values():
            try:
                seq.pause()
            except:
                pass
        self.targetSeqMeters = {}

        for node in self.targetNodesMeters.values():
            if node and not node.isEmpty():
                node.removeNode()
        self.targetNodesMeters = {}

        for laffMeter in self.laffMeters:
            try:
                laffMeter.destroy()
            except:
                pass
        self.laffMeters = []
        self.laffMeterAvatars = []
        self.laffMeterByAvatarId = {}

    def _showMovieLaffMeters(self):
        self._cleanupMovieLaffMeters()
        if base.localAvatar not in self.battle.activeToons:
            return

        positions = ((0.38, 0.0, 0.13), (0.63, 0.0, 0.13), (0.88, 0.0, 0.13))
        for avatar in self.battle.activeToons:
            if avatar == base.localAvatar:
                continue
            if len(self.laffMeters) >= len(positions):
                break
            laffMeter = LaffMeter.LaffMeter(avatar.style, avatar.getHp(), avatar.getMaxHp())
            laffMeter.setAvatar(avatar)
            laffMeter.setScale(0.075)
            laffMeter.reparentTo(base.a2dBottomLeft)
            laffMeter.setPos(positions[len(self.laffMeters)])
            laffMeter.start()
            self.laffMeters.append(laffMeter)
            self.laffMeterAvatars.append(avatar)
            self.laffMeterByAvatarId[avatar.doId] = laffMeter

    def _getAttackTargetToonIds(self, attack):
        targetType = attack.get('targetType', 'toon')

        # Suit-only and no-target attacks should never affect
        # the Toon laff-meter targeting UI.
        if targetType in ('suit', 'none'):
            return []

        targets = attack.get('target', [])

        if isinstance(targets, dict):
            targets = [targets]

        toonIds = []

        for target in targets:
            if not isinstance(target, dict):
                continue

            toon = target.get('toon')
            damage = target.get('hp', 0)

            if toon is None or toon not in self.battle.activeToons:
                continue

            if damage <= 0:
                continue

            if toon.doId not in toonIds:
                toonIds.append(toon.doId)

        return toonIds

    def _handleLaffMeterTargets(self, *toonIds):
        textScaleNorm = (0.33, 0.26, 0.26)
        textScaleLarge = (textScaleNorm[0] * 1.1, textScaleNorm[1] * 1.1, textScaleNorm[2] * 1.1)

        for toonId in toonIds:
            toon = self.battle.findToon(toonId)
            if toon is None or toon not in self.battle.activeToons:
                continue

            if toonId == base.localAvatar.doId:
                laffMeter = getattr(base.localAvatar, 'laffMeter', None)
            else:
                laffMeter = self.laffMeterByAvatarId.get(toonId)
            if laffMeter is None or laffMeter.isEmpty():
                continue

            if toonId not in self.targetNodesMeters:
                textNode = TextNode('meter-target-exclamation-text')
                textNode.setFont(ToontownGlobals.getSignFont())
                textNode.setTextColor(1, 0.1, 0.1, 1)
                textNode.setText('!')
                textNode.setAlign(TextNode.ACenter)
                targetNode = NodePath('meter-target-exclamation')
                targetNode.attachNewNode(textNode.generate())
                targetNode.reparentTo(hidden)
                self.targetNodesMeters[toonId] = targetNode

            ourIndicator = self.targetNodesMeters[toonId]
            if toonId in self.targetSeqMeters:
                self.targetSeqMeters[toonId].finish()

            targetTrack = Sequence(
                Func(ourIndicator.reparentTo, aspect2d),
                Func(ourIndicator.setPos, laffMeter, 0.15, 0, 1.8),
                Func(ourIndicator.setR, -40),
                Func(ourIndicator.setScale, 0.01),
                Func(ourIndicator.setAlphaScale, 1.0),
                Func(ourIndicator.show),
                Parallel(
                    LerpScaleInterval(ourIndicator, 0.14, textScaleNorm, blendType='easeIn'),
                    LerpHprInterval(ourIndicator, 0.14, (0, 0, 0), blendType='easeIn')
                ),
                LerpScaleInterval(ourIndicator, 0.12, textScaleLarge, blendType='easeOut'),
                LerpScaleInterval(ourIndicator, 0.12, textScaleNorm, blendType='easeIn'),
                Wait(1.3),
                Parallel(
                    LerpFunctionInterval(ourIndicator.setAlphaScale, fromData=1.0, toData=0, duration=0.33, blendType='easeIn'),
                    LerpHprInterval(ourIndicator, 0.33, (0, 0, 60), blendType='easeIn')
                ),
                Func(ourIndicator.hide),
                Func(ourIndicator.reparentTo, hidden)
            )
            self.targetSeqMeters[toonId] = targetTrack
            targetTrack.start()

    def play(self, ts, callback):
        self._showMovieLaffMeters()
        self.hasBeenReset = 0

        speedSuit = None

        for s in self.battle.suits:
            if s.battleSpeed > 0 and s.dna.name != 'hustle':
                speedSuit = s
                break

        if speedSuit:
            speed = float(speedSuit.getBattleSpeed())
            for suit in self.battle.activeSuits:
                Func(suit.checkBattleSpeed2, speedSuit)
        else:
            speed = 1.0

        speed = max(0.1, speed)
        self.currentBattleSpeed = speed

        ptrack = Sequence(Wait(1.0))
        camtrack = Sequence(Wait(1.0))
        if random.random() > 0.5:
            MovieUtil.shotDirection = 'left'
        else:
            MovieUtil.shotDirection = 'right'
        # for toon in self.battle.activeToons:
        #     if toon.getCooldownRounds() <= 1:
        #         ptrack.append(Func(toon.makeUnCooldown))
        # for s in self.battle.activeSuits:
        #     ptrack.append(Func(self.__updateSuitRoundEffects, s))
        preSuitAttacks = []
        postSuitAttacks = []

        for a in self.suitAttackDicts:
            phase = a.get('phase', 'postToon')

            if phase == 'preToon':
                preSuitAttacks.append(a)
            elif phase in ('postToon', 'normal', None):
                postSuitAttacks.append(a)
            # after-squirt and other custom phases are ignored here
            # because __doToonAttacks() will play them in the middle

        preSattacks, preScam = self.__doSuitAttacks(preSuitAttacks, 'pre-suit-attacks')
        if preSattacks:
            ptrack.append(preSattacks)
            camtrack.append(preScam)

        tattacks, tcam = self.__doToonAttacks()
        if tattacks:
            ptrack.append(tattacks)
            camtrack.append(tcam)
            for t in self.battle.activeToons:
                t.loop('neutral')

        sattacks, scam = self.__doSuitAttacks(postSuitAttacks, 'post-suit-attacks')
        if sattacks:
            ptrack.append(sattacks)
            camtrack.append(scam)
        ptrack.append(Func(callback))
        for s in self.battle.activeSuits:
            ptrack.append(Func(s.decrementStatusEffects))
            s.battleTrapIsFresh = 0
            s.clearPendingQueuedDamageAll()
            s.clearPendingQueuedHealingAll()
            s.setPendingQueuedDeath(False)

        for toon in self.battle.activeToons:
            ptrack.append(Func(toon.decrementToonStatusEffects))
        for s in self.battle.activeSuits:
            if s.dna.name == 'hrollers' or s.dna.name == 'mh2' or s.dna.name == 'cnd2' or s.dna.name == 'std2' or s.dna.name == 'videog' or s.dna.name == 'bcaster' or s.dna.name == 'choreo' or s.dna.name == 'cinema' or s.dna.name == 'director' or s.dna.name == 'fmaker':
                ptrack.append(Parallel(Func(s.setNeutralAnimationRolled), Func(s.setChatAbsoluteSpecial,
                                                                               '',
                                                                               CFSpeech | CFTimeout), Func(s.updateHealthBar, 0, forceUpdate=1)))
            else:
                if s.isSleepy:
                    ptrack.append(Parallel(Func(s.setNeutralAnimation), Func(s.setChatAbsoluteSpecial,
                                                                             '. . . Z Z Z . . .',
                                                                             CFThought), Func(s.updateHealthBar, 0, forceUpdate=1)))
                else:
                    ptrack.append(Parallel(Func(s.setNeutralAnimation), Func(s.setChatAbsoluteSpecial,
                                                                             '',
                                                                             CFSpeech | CFTimeout), Func(s.updateHealthBar, 0, forceUpdate=1)))
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

        self.setTrackPlayRate(self.track, speed)
        self.track.start(ts, playRate=speed)
        return None

    def setTrackPlayRate(self, track, playRate):
        for seq in track:
            if isinstance(seq, SoundInterval):
                if seq.sound is None:
                    continue
                seq.sound.setPlayRate(playRate)
            elif isinstance(seq, MetaInterval):
                self.setTrackPlayRate(seq, playRate)


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
        self._cleanupMovieLaffMeters()

    def applyPendingContentSync(self):
        if not hasattr(base.localAvatar, 'battleConditions'):
            return

        if 'pendingContentSync' not in base.localAvatar.battleConditions:
            return

        orderId = base.localAvatar.battleConditions['pendingContentSync'][0]
        cond = 'contentSync%s' % orderId

        base.localAvatar.currentContentSyncOrderCondition = cond

        if hasattr(base.localAvatar, 'inventory'):
            base.localAvatar.inventory.applyDisplayTrackOrder()


    def getMovieToonTrackOrder(self):
        order = [HEAL, TRAP, LURE, THROW, SQUIRT, ZAP, SOUND, DROP]
        for toon in self.battle.activeToons:
            if toon.contentSync == 1:
                order = [DROP, SQUIRT, ZAP, TRAP, THROW, LURE, SOUND, HEAL]

            elif toon.contentSync == 2:
                order = [SOUND, DROP, SQUIRT, HEAL, ZAP, TRAP, LURE, THROW]

            elif toon.contentSync == 3:
                order = [SQUIRT, SOUND, HEAL, TRAP, THROW, ZAP, LURE, DROP]

            elif toon.contentSync == 4:
                order = [SQUIRT, TRAP, LURE, DROP, HEAL, ZAP, SOUND, THROW]

            elif toon.contentSync == 5:
                order = [THROW, SOUND, DROP, TRAP, SQUIRT, HEAL, LURE, ZAP]

            elif toon.contentSync == 6:
                order = [THROW, SQUIRT, ZAP, SOUND, TRAP, LURE, DROP, HEAL]

            elif toon.contentSync == 7:
                order = [TRAP, DROP, SQUIRT, SOUND, THROW, ZAP, LURE, HEAL]

            elif toon.contentSync == 8:
                order = [TRAP, SQUIRT, DROP, THROW, ZAP, LURE, HEAL, SOUND]

            else:
                order = [HEAL, TRAP, LURE, THROW, SQUIRT, ZAP, SOUND, DROP]

        return order

    def __doToonAttacks(self):
        if not base.config.GetBool('want-toon-attack-anims', 1):
            return (None, None)

        track = Sequence(name='toon-attacks')
        camTrack = Sequence(name='toon-attacks-cam')

        # Special tracks always happen first.
        specialTracks = [
            (FIRE, MovieFire.doFires),
            (SUE, MovieSue.doSues),
            (SOS, MovieSOS.doSOSs),
            (NPCSOS, MovieNPCSOS.doNPCSOSs),
            (PETSOS, MoviePetSOS.doPetSOSs)
        ]

        for toonTrack, func in specialTracks:
            ival, camIval = func(self.__findToonAttack(toonTrack))
            if ival:
                track.append(ival)
                camTrack.append(camIval)

        # Synced/randomized gag track order.
        order = self.getMovieToonTrackOrder()
        for toonTrack in order:
            self.__doToonTrackMoviePhase(toonTrack, track, camTrack)

        if len(track) == 0:
            return (None, None)

        return (track, camTrack)
        
    def __doSuitReactionPhase(self, phaseName):
        return self.__doSuitAttackPhase(phaseName)
    
    def __doToonTrackMoviePhase(self, toonTrack, track, camTrack):
        ival = None
        camIval = None
        phaseName = None

        if toonTrack == HEAL:
            hasHealBonus = self.battle.getInteractivePropTrackBonus() == HEAL
            ival, camIval = MovieHeal.doHeals(self.__findToonAttack(HEAL), hasHealBonus)
            phaseName = 'after-heal'

        elif toonTrack == TRAP:
            ival, camIval = MovieTrap.doTraps(self.__findToonAttack(TRAP))
            phaseName = 'after-trap'

        elif toonTrack == LURE:
            ival, camIval = MovieLure.doLures(self.__findToonAttack(LURE))
            phaseName = 'after-lure'

        elif toonTrack == THROW:
            ival, camIval = MovieThrow.doThrows(self.__findToonAttack(THROW))
            phaseName = 'after-throw'

        elif toonTrack == SQUIRT:
            ival, camIval = MovieSquirt.doSquirts(self.__findToonAttack(SQUIRT))
            phaseName = 'after-squirt'

        elif toonTrack == ZAP:
            ival, camIval = MovieZap.doZaps(self.__findToonAttack(ZAP))
            phaseName = 'after-zap'

        elif toonTrack == SOUND:
            ival, camIval = MovieSound.doSounds(self.__findToonAttack(SOUND))
            phaseName = 'after-sound'

        elif toonTrack == DROP:
            ival, camIval = MovieDrop.doDrops(self.__findToonAttack(DROP))
            phaseName = 'after-drop'

        if ival:
            track.append(ival)
            camTrack.append(camIval)

        if phaseName:
            sival, scamIval = self.__doSuitAttackPhase(phaseName)
            if sival:
                track.append(sival)
                camTrack.append(scamIval)


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
                    for ti in range(0, toonIndex):
                        rightToons.append(self.battle.activeToons[ti])
                    lenToons = len(self.battle.activeToons)
                    leftToons = []
                    if lenToons > toonIndex + 1:
                        for ti in range(toonIndex + 1, lenToons):
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
                    toon = target.get('toon')

                    if toon is None:
                        continue

                    if (
                        target.get('died', 0) and
                        toon.doId == base.localAvatar.doId
                    ):
                        isLocalToonSad = False
                
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
                iouAttack = 0
                if track == NPCSOS:
                    definition = IOURegistry.getIOU(level)
                    if definition is not None:
                        iouAttack = 1
                        adict['npcId'] = definition.getNpcId()
                        adict['avatar'] = toon
                        adict['track'] = NPCSOS
                        adict['level'] = level
                        adict['special'] = 1
                        recipients = []
                        targetIndex = ta[TOON_TGT_COL]
                        if targetIndex >= 0 and targetIndex < len(toons):
                            targetId = toons[targetIndex]
                            target = self.battle.findToon(targetId)
                            if target is not None:
                                recipients.append(target)
                        gagTrack = definition.getGagTrack()
                        if toon not in recipients and (gagTrack == -1 or toon.hasTrackAccess(gagTrack)):
                            recipients.append(toon)
                        adict['toons'] = recipients
                        adict['target'] = [{'avatar': target} for target in recipients]
                    else:
                        adict['npcId'] = ta[TOON_TGT_COL]
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
                elif iouAttack:
                    pass
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
                        for si in range(0, suitIndex):
                            asuit = self.battle.activeSuits[si]
                            if self.battle.isSuitLured(asuit) == 0:
                                leftSuits.append(asuit)

                        lenSuits = len(self.battle.activeSuits)
                        rightSuits = []
                        if lenSuits > suitIndex + 1:
                            for si in range(suitIndex + 1, lenSuits):
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
                        if track == SQUIRT:
                            targets = []

                            # MAIN TARGET FIRST
                            targets.append(sdict)

                            # Add every other Cog that actually received
                            # calculated Squirt damage from the AI.
                            for splashIndex in range(len(suits)):
                                if splashIndex == targetIndex:
                                    continue

                                splashId = suits[splashIndex]

                                if splashId == -1:
                                    continue

                                # No calculated splash damage = not a splash target.
                                if hps[splashIndex] <= 0:
                                    continue

                                splashSuit = self.battle.findSuit(splashId)

                                if splashSuit is None:
                                    continue

                                if splashSuit not in self.battle.activeSuits:
                                    continue

                                splashDict = {}

                                splashDict['suit'] = splashSuit
                                splashDict['hp'] = hps[splashIndex]
                                splashDict['kbbonus'] = kbbonuses[splashIndex]
                                splashDict['died'] = ta[SUIT_DIED_COL] & 1 << splashIndex
                                splashDict['revived'] = ta[SUIT_REVIVE_COL] & 1 << splashIndex

                                splashSuitIndex = self.battle.activeSuits.index(splashSuit)

                                leftSuits = []

                                for si in range(0, splashSuitIndex):
                                    asuit = self.battle.activeSuits[si]

                                    if self.battle.isSuitLured(asuit) == 0:
                                        leftSuits.append(asuit)

                                rightSuits = []

                                if len(self.battle.activeSuits) > splashSuitIndex + 1:
                                    for si in range(
                                        splashSuitIndex + 1,
                                        len(self.battle.activeSuits)
                                    ):
                                        asuit = self.battle.activeSuits[si]

                                        if self.battle.isSuitLured(asuit) == 0:
                                            rightSuits.append(asuit)

                                splashDict['leftSuits'] = leftSuits
                                splashDict['rightSuits'] = rightSuits

                                targets.append(splashDict)

                            adict['target'] = targets
                        elif track == ZAP:
                            targets = []

                            # MAIN TARGET FIRST.
                            targets.append(sdict)

                            mainSuit = target
                            mainSuitIndex = self.battle.activeSuits.index(mainSuit)

                            zapSuitOrder = []

                            # Priority: LEFT of main first.
                            index = mainSuitIndex - 1

                            while index >= 0 and len(zapSuitOrder) < 3:
                                zapSuit = self.battle.activeSuits[index]
                                zapIndex = suits.index(zapSuit.doId)

                                # Only include it if AI actually gave it Zap damage.
                                if hps[zapIndex] > 0:
                                    zapSuitOrder.append(zapSuit)

                                index -= 1

                            # Then fill remaining chain slots from RIGHT of main.
                            index = mainSuitIndex + 1

                            while index < len(self.battle.activeSuits) and len(zapSuitOrder) < 3:
                                zapSuit = self.battle.activeSuits[index]
                                zapIndex = suits.index(zapSuit.doId)

                                if hps[zapIndex] > 0:
                                    zapSuitOrder.append(zapSuit)

                                index += 1

                            # Build movie dictionaries in the exact Zap chain order.
                            for zapSuit in zapSuitOrder:
                                zapIndex = suits.index(zapSuit.doId)

                                zapDict = {}

                                zapDict['suit'] = zapSuit
                                zapDict['hp'] = hps[zapIndex]
                                zapDict['kbbonus'] = kbbonuses[zapIndex]
                                zapDict['died'] = ta[SUIT_DIED_COL] & 1 << zapIndex
                                zapDict['revived'] = ta[SUIT_REVIVE_COL] & 1 << zapIndex

                                battleIndex = self.battle.activeSuits.index(zapSuit)

                                leftSuits = []

                                for si in range(0, battleIndex):
                                    asuit = self.battle.activeSuits[si]

                                    if self.battle.isSuitLured(asuit) == 0:
                                        leftSuits.append(asuit)

                                rightSuits = []

                                if battleIndex + 1 < len(self.battle.activeSuits):
                                    for si in range(
                                        battleIndex + 1,
                                        len(self.battle.activeSuits)
                                    ):
                                        asuit = self.battle.activeSuits[si]

                                        if self.battle.isSuitLured(asuit) == 0:
                                            rightSuits.append(asuit)

                                zapDict['leftSuits'] = leftSuits
                                zapDict['rightSuits'] = rightSuits

                                targets.append(zapDict)

                            adict['target'] = targets

                        elif track == DROP or track == LURE or track == TRAP:
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
    
    def __doSuitAttackPhase(self, phaseName):
        if not base.config.GetBool('want-suit-anims', 1):
            return (None, None)

        phaseAttacks = []

        for a in self.suitAttackDicts:
            if a.get('phase') == phaseName:
                phaseAttacks.append(a)

        if not phaseAttacks:
            return (None, None)

        return self.__doSuitAttacks(phaseAttacks, phaseName)

    def __genSuitAttackDicts(self, toons, suits, suitAttacks):
        for sa in suitAttacks:
            targetGone = 0
            attack = sa[SUIT_ATK_COL]
            encodedGroup = attack[1]

            targetTypeCode = (
                encodedGroup >>
                SuitBattleGlobals.TARGET_TYPE_SHIFT
            )

            realGroup = (
                encodedGroup &
                SuitBattleGlobals.TARGET_GROUP_MASK
            )
            if attack:
                suitIndex = sa[SUIT_ID_COL]
                suitId = suits[suitIndex]
                suit = self.battle.findSuit(suitId)
                # if suit == None:
                #     self.notify.warning('suit: %d not in battle!' % suitId)
                #     return
                # NOTE: Maybe there's a better way to handle this?  ~Professor Control
                adict = {
                    'suitName': attack[4],
                    'name': attack[2],
                    'animName': attack[6],
                    'hp': attack[3],
                    'acc': attack[0],
                    'freq': attack[5],
                    'group': realGroup,
                    'targetType': targetTypeCode
                }
                adict['suit'] = suit
                adict['battle'] = self.battle
                adict['playByPlayText'] = self.playByPlayText
                adict['taunt'] = sa[SUIT_TAUNT_COL]


                phaseByName = {
                    'KnockbackThrow': 'after-throw',
                    'KnockbackSquirt': 'after-squirt',
                    'ComboThrow': 'after-throw',
                    'ComboSquirt': 'after-squirt',
                    'ComboDrop': 'after-drop',
                    'ReddLiquidationSale': 'after-squirt',
                    'LitigatorSnapSoak': 'after-squirt',
                    'PowerhouseGeneration': 'after-zap',
                    'PowerhouseSnipeCollectCall': 'after-squirt',
                    'TollmasterLedgerOfSound': 'after-sound',
                    'DividendZapRetaliation': 'after-throw',
                    'AttorneyOverseerDrop': 'after-drop',
                    'AttorneyOverseerSquirt': 'after-squirt',
                    'AttorneyOverseerThrow': 'after-throw',
                    'HighStakesTrap': 'after-heal',
                    'HighStakesLure': 'after-trap',
                    'HighStakesSound': 'after-zap',
                    'HighStakesThrow': 'after-lure',
                    'HighStakesSquirt': 'after-throw',
                    'HighStakesZap': 'after-squirt',
                    'HighStakesDrop': 'after-sound',
                    'LureRemovalHeal': 'after-heal',
                    'LureRemovalTrap': 'after-trap',
                    'LureRemovalLure': 'after-lure',
                    'LureRemovalSound': 'after-sound',
                    'LureRemovalThrow': 'after-throw',
                    'LureRemovalSquirt': 'after-squirt',
                    'LureRemovalZap': 'after-zap',
                    'LureRemovalDrop': 'after-drop',
                    'HighRollerSplashback': 'after-squirt',
                    'HighRollerBar2': 'after-trap',
                    'HighRollerCheerRetaliation': 'after-heal',
                    'MintLedger': 'after-sound',

                    # Court Record / gag ban retaliation
                    # 'StenographerCourtRecordBan': 'after-gag-check',
                    # 'CaseManagerCourtRecordBan': 'after-gag-check',

                    'GagBanRetaliationHeal': 'after-heal',
                    'GagBanRetaliationTrap': 'after-trap',
                    'GagBanRetaliationLure': 'after-lure',
                    'GagBanRetaliationThrow': 'after-throw',
                    'GagBanRetaliationSquirt': 'after-squirt',
                    'GagBanRetaliationZap': 'after-zap',
                    'GagBanRetaliationSound': 'after-sound',
                    'GagBanRetaliationDrop': 'after-drop',

                    # Absorb movies
                    'AbsorbMovieLure': 'after-lure',
                    'AbsorbMovieThrow': 'after-throw',
                    'AbsorbMovieSquirt': 'after-squirt',
                    'AbsorbMovieZap': 'after-zap',
                    'AbsorbMovieSound': 'after-sound',
                    'AbsorbMovieDrop': 'after-drop',

                    'AbsorbMovieLevelLure': 'after-lure',
                    'AbsorbMovieLevelThrow': 'after-throw',
                    'AbsorbMovieLevelSquirt': 'after-squirt',
                    'AbsorbMovieLevelZap': 'after-zap',
                    'AbsorbMovieLevelSound': 'after-sound',
                    'AbsorbMovieLevelDrop': 'after-drop',
                }

                PRE_TOON_ATTACKS = (
                    'ZapMovie',
                    'ErclaimHemmorage',
                    'SueDamage',
                    'UnionBusterContractEnforcementHealing',
                    'SueApplication',
                    'AbilityQueuedPreToon',
                    'BookkeeperPaperCut',
                    'AmbassadorAdvancement3',
                    'ContingencyMarkRevisedFiling',
                    'ContingencyRiskThresholdBreach50',
                    'ArbitratorPaperFiling',
                    'RadiographerHotTake',
                    'SafetyHeatWaveCalculation',
                    'RecordkeeperRedlinedClauseMissedPayment',
                    'SafetyPromotion',
                    'AttorneyRemand',
                    'HighStakesHeal',
                    'ContingencySelfRepair',
                    'PowerhouseBurnDamage',
                    'VideographerElectricShock',
                    'PowerhouseAbsorb',
                    'HighRollerSingingBlues',
                     'HighRollerLureResistance2',
                     'PresidentMandatoryFiling',
                     'PresidentLiability',
                     'ReddAutoRepair',
                    'HighRollerLureResistance',
                    'MintLureResistance2',
                    'MintLureResistance',
                    'RecordkeeperRedlinedClause',
                    'LureRemovalPreToon',
                )
                regularAttacks = [
                    'AcidRain',
                    'Aftershock',
                    'Audit',
                    'Bash',
                    'Beguile',
                    'CloseTheLoop',
                    'HostileTakeover',
                    'NickelAndDime',
                    'Quash',
                    'PennyPinch',
                    'Disassemble',
                    'DataCorruption',
                    'DataBreach',
                    'VersionControl',
                    'DenialOfService',
                    'Overload',
                    'Breakthrough',
                    'Encrypt',
                    'BounceRate',
                    'Reprogram',
                    'CloudStorage',
                    'DoubleCross',
                    'Forecast',
                    'GoldDust',
                    'GoldRush',
                    'DiskScratch',
                    'MysteriousDisappearance',
                    'VoodooMagic',
                    'ElectrostaticEnergy',
                    'Bite',
                    'BounceCheck',
                    'BrainStorm',
                    'BuzzWord',
                    'Calculate',
                    'Canned',
                    'EvictionNotice',
                    'Chomp',
                    'Watercooler',
                    'CigarSmoke',
                    'ClipOnTie',
                    'Crunch',
                    'Demotion',
                    'DoubleTalk',
                    'Downsize',
                    'EvilEye',
                    'FiveOClockShadow',
                    'SandTrap',
                    'Filibuster',
                    'FillWithLead',
                    'FingerWag',
                    'Fired',
                    'FountainPen',
                    'FreezeAssets',
                    'GlowerPower',
                    'ReArrange',
                    'ShortSqueeze',
                    'BlueChip',
                    'FallingKnife',
                    'GuiltTrip',
                    'Embezzle',
                    'FloodTheMarket',
                    'MoneyTrip',
                    'HalfWindsor',
                    'HangUp',
                    'HeadShrink',
                    'HotAir',
                    'Jargon',
                    'Legalese',
                    'LawBook',
                    'Liquidate',
                    'MarketCrash',
                    'MumboJumbo',
                    'ParadigmShift',
                    'PeckingOrder',
                    'PickPocket',
                    'PinkSlip',
                    'PlayHardball',
                    'PoundKey',
                    'PowerTie',
                    'PowerTrip',
                    'Quake',
                    'RazzleDazzle',
                    'RedTape',
                    'ReOrg',
                    'RestrainingOrder',
                    'Rolodex',
                    'RubberStamp',
                    'RubOut',
                    'Sacked',
                    'Schmooze',
                    'TestSchmooze',
                    'Shake',
                    'Inject',
                    'Shred',
                    'SongAndDance',
                    'Spin',
                    'Synergy',
                    'Tabulate',
                    'Golf',
                    'ThrowBook',
                    'Novel',
                    'Newspaper',
                    'Tremor',
                    'Withdrawal',
                    'WriteOff',
                ]

                if sa[SUIT_BEFORE_TOONS_COL]:
                    adict['phase'] = 'preToon'
                elif suit and adict['name'] in phaseByName:
                    adict['phase'] = phaseByName[adict['name']]
                elif suit and adict['name'] in PRE_TOON_ATTACKS:
                    adict['phase'] = 'preToon'
                elif suit and adict['name'] in regularAttacks and suit.hasSuitStatusEffect('attackFirst'):
                    adict['phase'] = 'preToon'
                else:
                    adict['phase'] = 'postToon'


                hps = sa[SUIT_HP_COL]
                heals = sa[SUIT_HEAL_COL]

                # =========================================================
                # SUIT-TARGETING ATTACK
                # =========================================================
                if adict['targetType'] == SuitBattleGlobals.ATK_TARGET_SUIT:
                    targets = []

                    for targetIndex in sa[SUIT_TGT_COL]:
                        if (
                            targetIndex < 0 or
                            targetIndex >= len(suits)
                        ):
                            continue

                        targetId = suits[targetIndex]
                        targetSuit = self.battle.findSuit(targetId)

                        if targetSuit is None:
                            continue
                        tdict = {
                            'suit': targetSuit,
                            'hp': hps[targetIndex] if targetIndex < len(hps) else 0,
                            'heal': heals[targetIndex] if targetIndex < len(heals) else 0,
                            'died': sa[SUIT_TARGET_DIED_COL] & (1 << targetIndex)
                        }

                        targets.append(tdict)

                    if targets:
                        adict['target'] = targets
                    else:
                        targetGone = 1


                # =========================================================
                # MIXED TOON + SUIT TARGETING
                # =========================================================
                elif adict['targetType'] == SuitBattleGlobals.ATK_TARGET_BOTH:
                    targets = []

                    toonCount = len(toons)

                    for mixedIndex in sa[SUIT_TGT_COL]:

                        # -----------------------------------------
                        # TOON TARGET
                        # -----------------------------------------
                        if mixedIndex < toonCount:
                            toonIndex = mixedIndex

                            if (
                                toonIndex < 0 or
                                toonIndex >= len(toons)
                            ):
                                continue

                            targetId = toons[toonIndex]
                            targetToon = self.battle.findToon(targetId)

                            if targetToon is None:
                                continue

                            tdict = {
                                'toon': targetToon,
                                'hp': hps[mixedIndex] if mixedIndex < len(hps) else 0,
                                'died': sa[TOON_DIED_COL] & 1 << toonIndex
                            }

                            targets.append(tdict)

                        # -----------------------------------------
                        # SUIT TARGET
                        # -----------------------------------------
                        else:
                            suitIndex = mixedIndex - toonCount

                            if (
                                suitIndex < 0 or
                                suitIndex >= len(suits)
                            ):
                                continue

                            targetId = suits[suitIndex]
                            targetSuit = self.battle.findSuit(targetId)

                            if targetSuit is None:
                                continue

                            tdict = {
                                'suit': targetSuit,
                                'hp': hps[mixedIndex] if mixedIndex < len(hps) else 0,
                                'heal': heals[mixedIndex] if mixedIndex < len(heals) else 0,
                                'died': sa[SUIT_TARGET_DIED_COL] & (1 << mixedIndex)
                            }
                            

                            targets.append(tdict)

                    if targets:
                        adict['target'] = targets
                    else:
                        targetGone = 1


                # =========================================================
                # NO TARGET
                # =========================================================
                elif adict['targetType'] == SuitBattleGlobals.ATK_TARGET_NONE:
                    adict['target'] = []


                # =========================================================
                # NORMAL TOON-TARGETING ATTACK
                # =========================================================
                else:
                    if adict['group'] == ATK_TGT_GROUP:
                        targets = []

                        for t in toons:
                            if t == -1:
                                continue

                            target = self.battle.findToon(t)

                            if target is None:
                                continue

                            targetIndex = toons.index(t)

                            tdict = {}
                            tdict['toon'] = target
                            tdict['hp'] = hps[targetIndex]

                            toonDied = (
                                sa[TOON_DIED_COL] &
                                1 << targetIndex
                            )

                            tdict['died'] = toonDied

                            targets.append(tdict)

                        if targets:
                            adict['target'] = targets
                        else:
                            targetGone = 1
                    elif (
                        adict['group'] == ATK_TGT_SINGLE or
                        adict['group'] == ATK_TGT_DOUBLE or
                        adict['group'] == ATK_TGT_TRIPLE
                    ):
                        targets = []

                        for targetIndex in sa[SUIT_TGT_COL]:
                            if (
                                targetIndex < 0 or
                                targetIndex >= len(toons)
                            ):
                                continue

                            targetId = toons[targetIndex]
                            target = self.battle.findToon(targetId)

                            if target is None:
                                continue

                            tdict = {}
                            tdict['toon'] = target
                            tdict['hp'] = hps[targetIndex]

                            toonDied = (
                                sa[TOON_DIED_COL] &
                                1 << targetIndex
                            )

                            tdict['died'] = toonDied

                            toonIndex = self.battle.activeToons.index(
                                target
                            )

                            rightToons = []

                            for ti in range(0, toonIndex):
                                rightToons.append(
                                    self.battle.activeToons[ti]
                                )

                            leftToons = []

                            if len(self.battle.activeToons) > toonIndex + 1:
                                for ti in range(
                                    toonIndex + 1,
                                    len(self.battle.activeToons)
                                ):
                                    leftToons.append(
                                        self.battle.activeToons[ti]
                                    )

                            tdict['leftToons'] = leftToons
                            tdict['rightToons'] = rightToons

                            targets.append(tdict)

                        if targets:
                            adict['target'] = targets
                        else:
                            targetGone = 1

                    else:
                        self.notify.warning(
                            'got suit attack not group or single!'
                        )
                if targetGone == 0:
                    self.suitAttackDicts.append(adict)
                else:
                    self.notify.warning('genSuitAttackDicts() - target gone!')


    def __doSuitAttacks(self, suitAttacks=None, name='suit-attacks'):
        if not base.config.GetBool('want-suit-anims', 1):
            return (None, None)

        if suitAttacks is None:
            suitAttacks = self.suitAttackDicts

        track = Sequence(name=name)
        camTrack = Sequence(name=name + '-cam')

        IGNORE_LAFF_METER = (
            'BroadcasterDonation', 
            'ContingencyForecastCollapse',
            'RacketeerOverextendedLeverage',
             'AttorneyOverseer',
        'AttorneyOverseerDrop',
        'BroadcasterDonation2',
        'MarkRemoval',
        'TrafficCongestionPricing',
        'HighRollerTrickOfTheLight',
        'HighRollerDonation',
        'HighRollerDamageReduction',
        'Desperation',
        'Desperation2',
        'AttorneyOverseerSquirt',
        'VideographerStarOfTheShow',
        'AttorneyOverseerThrow',
        'KnockbackThrow',
    'KnockbackSquirt',
    'ComboThrow',
    'ComboSquirt',
    'ComboDrop',
    'RushJobTrap',
    'RushJobLure',
    'RushJobThrow',
    'CalculatingFees',
    'RushJobSquirt',
                'ScapegoatRageBuilding',
            'ArbitratorThrowBook',
            'RadiographerOvermodulated',
            'PowerhouseToleranceBuilding',
            'TollmasterResonanceTax',
            'RacketeerProfiteering',
            'UnionBusterUnionWages',
            'AmbassadorHeadRoller',
            'WiretapperCollectCall2',
            'SafetyPromotion',
            'SafetyHeatWaveCalculation',
            'TollmasterBalanceTheLedger',
            'DividendAccountRollover',
            'RecordkeeperMinutesTakenContingency',
            'RecordkeeperMinutesTaken',
            'SafetyOverpressured',
            'VideographerElectricShock',
    'RushJobZap',
    'RushJobSound',
    'RushJobDrop',
    'PresidentTargetCheck',
    'PresidentExtraTip',
      'HighStakesHeal',
    'HighStakesTrap',
    'HighStakesLure',
    'HighStakesSound',
    'HighStakesThrow',
    'HighStakesSquirt',
    'HighStakesZap',
    'HighStakesDrop',
     'AbsorbMovieLure',
        'AbsorbMovieThrow',
        'AbsorbMovieSquirt',
        'AbsorbMovieZap',
        'AbsorbMovieSound',
        'AbsorbMovieDrop',
          'AbsorbMovieLevelLure',
        'AbsorbMovieLevelThrow',
        'AbsorbMovieLevelSquirt',
        'AbsorbMovieLevelZap',
        'AbsorbMovieLevelSound',
        'AbsorbMovieLevelDrop',
        'ZapMovie',
        'SueDamage',
        'SueApplication',
        'DamageMovie', 
        'SyphonMovie',
        'AbilityQueued', 
        'AbilityQueuedPreToon',
       'LureRemovalPreToon',
    'LureRemoval',
    'LureRemovalHeal',
    'LureRemovalTrap',
    'LureRemovalLure',
    'LureRemovalSound',
    'LureRemovalThrow',
    'LureRemovalSquirt',
    'LureRemovalZap',
    'LureRemovalDrop',
    'DeathCheck', 
    'CogSpawn', 
    'SoakRemoval',
    'DrenchDecrement',
    'OilRemoval',
    'GovernaughtDeath',
    'MarkRemoval',
        )

        IGNORE_BATTLE_PLAYRATE = (
            'PacesetterOverclocked',
            'PacesetterEarlyOverclocked',
        )

        parallelGroupNames = {
            'ErfitProToonShake': 'ErfitPhaseCombo',
            'ErfitPhase2': 'ErfitPhaseCombo',
            'SoakRemoval': 'soakremove',
            'DrenchDecrement': 'soakremove',
        }

        parallelRemovalNames = (
            'MarkRemoval',
            'SoakRemoval',
            'DrenchDecrement',
            'ZapMovie',
            'SueDamage',
            'SueApplication',
            'SueRemoval',
            'AbsorbMovieLure',
            'AbsorbMovieThrow',
            'AbsorbMovieSquirt',
            'AbsorbMovieZap',
            'AbsorbMovieSound',
            'AbsorbMovieDrop',
             'AbsorbMovieLure',
        'AbsorbMovieThrow',
        'AbsorbMovieSquirt',
        'AbsorbMovieZap',
        'AbsorbMovieSound',
        'AbsorbMovieDrop',
        )

        attackCounts = {}
        for a in suitAttacks:
            attackName = a.get('name')
            attackCounts[attackName] = attackCounts.get(attackName, 0) + 1

        def getGroupedCamera(attack, attackName, count, duration, fallbackCamTrack):
            battle = self.battle

            if attackName in ('AbsorbMovieLure',
                            'AbsorbMovieThrow',
                            'AbsorbMovieSquirt',
                            'AbsorbMovieZap',
                            'AbsorbMovieSound',
                            'ZapMovie',
                            'SueDamage',
                            'AbsorbMovieDrop',
                            'AbsorbMovieLure',
                        'AbsorbMovieThrow',
                        'AbsorbMovieSquirt',
                        'AbsorbMovieZap',
                        'AbsorbMovieSound',
                        'AbsorbMovieDrop',):
                if count > 1:
                    return MovieCamera.heldShot(0.0, -15.0, 10.0, 0, -20, 0, duration)
                else:
                    return MovieCamera.chooseSuitShot(attack, duration)

            return fallbackCamTrack

        pendingName = None
        pendingTrack = Parallel()
        pendingCamTrack = Parallel()

        def flushPending():
            if len(pendingTrack) > 0:
                track.append(pendingTrack)
                camTrack.append(pendingCamTrack)

        for a in suitAttacks:
            attackName = a.get('name')

            ival, camIval = MovieSuitAttacks.doSuitAttack(a)
            if not ival:
                continue

            targetToonIds = self._getAttackTargetToonIds(a)
            if targetToonIds and attackName not in IGNORE_LAFF_METER:
                ival = Sequence(Func(self._handleLaffMeterTargets, *targetToonIds), ival)

            if attackName in IGNORE_BATTLE_PLAYRATE:
                speed = max(0.1, float(getattr(self, 'currentBattleSpeed', 1.0)))
                ival = _PacesetterRealtimeInterval(ival, speed)
                if camIval:
                    camIval = _PacesetterRealtimeInterval(camIval, speed)

            groupName = parallelGroupNames.get(attackName, attackName)

            if attackName in parallelRemovalNames or attackName in parallelGroupNames:
                if pendingName is None:
                    pendingName = groupName

                if groupName != pendingName:
                    flushPending()
                    pendingName = attackName
                    pendingTrack = Parallel()
                    pendingCamTrack = Parallel()

                count = attackCounts.get(attackName, 1)
                duration = ival.getDuration()

                camIval = getGroupedCamera(a,
                    attackName,
                    count,
                    duration,
                    camIval
                )

                pendingTrack.append(ival)

                if camIval:
                    pendingCamTrack.append(camIval)

                continue

            flushPending()

            pendingName = None
            pendingTrack = Parallel()
            pendingCamTrack = Parallel()

            track.append(ival)

            if camIval:
                camTrack.append(camIval)

        flushPending()

        if len(track) == 0:
            return (None, None)

        return (track, camTrack)
