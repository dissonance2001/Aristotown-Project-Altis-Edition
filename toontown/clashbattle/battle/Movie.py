import copy

from panda3d.core import ConfigVariableBool
from otp import *
from direct.interval.IntervalGlobal import *
from direct.showbase import DirectObject
from direct.gui.DirectGui import *

from toontown.clashbattle.battle import BattleExperience, BattleAvatar, MovieNPCSOS
from toontown.clashbattle.battle import BattleGUIGlobals
from toontown.clashbattle.battle import MovieDrop
from toontown.clashbattle.battle import MovieFire
from toontown.clashbattle.battle import MovieSue
from toontown.clashbattle.battle import MovieHeal
from toontown.clashbattle.battle import MovieLure
from toontown.clashbattle.battle import MovieSound
from toontown.clashbattle.battle import MovieSquirt
from toontown.clashbattle.battle import MovieThrow
from toontown.clashbattle.battle import MovieToonVictory
from toontown.clashbattle.battle import MovieTrap
from toontown.clashbattle.battle import MovieZap
from toontown.clashbattle.battle import MovieUtil
from toontown.clashbattle.battle import PlayByPlayText
from toontown.clashbattle.battle import RewardPanel
from toontown.clashbattle.battle.SuitBattleGlobals import *
from toontown.clashbattle.battle.attacks.base.AttackEnum import AttackEnum
from toontown.clashbattle.battle.attacks.client.Attack import Attack
from toontown.clashbattle.battle.attacks.client.AttackRepository import AttackRepository
from toontown.clashbattle.battle.attacks.client.suit import *
from toontown.clashbattle.battle.attacks.client.toon.ToonAttack import ToonAttack
from toontown.clashbattle.battle.movielistener.BattleMovieListenerEnum import BMLE
from toontown.clashbattle.battle.visuals.VisualEffectGlobals import createVisualEffect
from toontown.clashbattle.battle.visuals.VisualEffects import VisualEffectRemoved
from toontown.distributed import DelayDelete
from toontown.toon import OldLaffMeter
from toontown.toonbase import ToontownGlobals
from toontown.clashbattle.battle.BattleGlobals import *
from toontown.gui import TTDialog
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from toontown.cutscene.repository.CutsceneDataImports import *  # TODO: find a better way to do this

camPos = Point3(14, 0, 10)
camHpr = Vec3(89, -30, 0)
randomBattleTimestamp = ConfigVariableBool("random-battle-timestamp", False).getValue()


@DirectNotifyCategory()
class Movie(DirectObject.DirectObject):
    toonAttackToMovie = {
        AttackEnum.TOON_FIRE: MovieFire.doFires,
        AttackEnum.TOON_SUE: MovieSue.doSues,
        AttackEnum.TOON_NPC: MovieNPCSOS.doNPCSOSs,
        AttackEnum.TOON_HEAL: MovieHeal.doHeals,
        AttackEnum.TOON_TRAP: MovieTrap.doTraps,
        AttackEnum.TOON_LURE: MovieLure.doLures,
        AttackEnum.TOON_SOUND: MovieSound.doSounds,
        AttackEnum.TOON_SQUIRT: MovieSquirt.doSquirts,
        AttackEnum.TOON_ZAP: MovieZap.doZaps,
        AttackEnum.TOON_THROW: MovieThrow.doThrows,
        AttackEnum.TOON_DROP: MovieDrop.doDrops,
    }

    def __init__(self, battle):
        self.battle = battle
        self.track = None
        # self.delayDeleteTrack = None
        self.rewardPanel = None
        self.rewardCallback = None
        self.playByPlayText = PlayByPlayText.PlayByPlayText()
        self.playByPlayText.hide()
        self.renderProps = []
        self.hasBeenReset = 0
        self.originalSoundPlayRates = {}
        # Target indicator stuff
        self.targetNodesToons = {}
        self.targetSeqToons = {}
        self.targetNodesMeters = {}
        self.targetSeqMeters = {}
        self.reset()
        self.rewardHasBeenReset = 0
        self.resetReward()
        self.cleanedUpEffects = []
        self.intervalHasFinished = False
        self.forceFinish = False
        self.attackCallback = None
        self.laffMeters = []
        self.laffMeterAvatars = []
        self.hpChangeEvents = []

    def announceGenerate(self):
        # Not actually a DO, but called when the battle does announceGenerate.
        self.accept(self.battle.msg_updateTimescale, self.updateTimescale)

    def cleanup(self):
        self.reset()
        self.resetReward()
        del self.battle
        if self.playByPlayText is not None:
            self.playByPlayText.cleanup()
        del self.playByPlayText
        if self.rewardPanel is not None:
            self.rewardPanel.cleanup()
        self.rewardPanel = None
        self.rewardCallback = None
        self.ignoreAll()

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

    def restore(self):
        for toon in self.battle.activeToons:
            toon.loop("neutral")
            origPos, origHpr = self.battle.getActorPosHpr(toon)
            toon.setPosHpr(self.battle, origPos, origHpr)
            hands = toon.getRightHands()[:]
            hands += toon.getLeftHands()
            for hand in hands:
                props = hand.getChildren()
                for prop in props:
                    if prop.getName() != "book":
                        MovieUtil.removeProp(prop)

            if self.restoreColor == 1:
                headParts = toon.getHeadParts()
                torsoParts = toon.getTorsoParts()
                legsParts = toon.getLegsParts()
                partsList = [headParts, torsoParts, legsParts]
                for parts in partsList:
                    for nextPart in parts:
                        nextPart.clearColorScale()
                        nextPart.clearTransparency()

            if self.restoreHips == 1:
                parts = toon.getHipsParts()
                for nextPart in parts:
                    props = nextPart.getChildren()
                    for prop in props:
                        if prop.getName() == "redtape-tube.egg":
                            MovieUtil.removeProp(prop)

            if self.restoreHeadScale == 1:
                headScale = ToontownGlobals.toonHeadScales[toon.style.getAnimal()]
                toon.getPart("head").setScale(headScale)

            if self.restoreToonScale == 1:
                toon.setScale(1)
            headParts = toon.getHeadParts()
            for part in headParts:
                part.setHpr(0, 0, 0)
                part.setPos(0, 0, 0)

            arms = toon.findAllMatches("**/arms")
            sleeves = toon.findAllMatches("**/sleeves")
            hands = toon.findAllMatches("**/hands")
            partsList = [arms, sleeves, hands]
            for parts in partsList:
                for part in parts:
                    part.setHpr(0, 0, 0)

        for suit in self.battle.activeSuits:
            if suit._Actor__animControlDict is not None:
                suit.loop("neutral")
                suit.battleTrapIsFresh = 0
                origPos, origHpr = self.battle.getActorPosHpr(suit)
                suit.setPosHpr(self.battle, origPos, origHpr)
                hands = [suit.getRightHand(), suit.getLeftHand()]
                for hand in hands:
                    if hand:
                        props = hand.getChildren()
                        for prop in props:
                            MovieUtil.removeProp(prop)

        for effect in self.specialParticleEffects:
            if effect is not None:
                effect.cleanup()

        self.specialParticleEffects = []
        for prop in self.renderProps:
            MovieUtil.removeProp(prop)

        self.renderProps = []

    def _deleteTrack(self):
        if self.track:
            DelayDelete.cleanupDelayDeletes(self.track)
            self.track = None
        ### DelayDelete track for recursive battle movies ###
        # if self.track:
        #     self.track = None
        # if self.delayDeleteTrack:
        #     DelayDelete.cleanupDelayDeletes(self.delayDeleteTrack)
        #     self.delayDeleteTrack = None

    def reset(self, finish=0):
        if self.hasBeenReset == 1:
            return
        self.hasBeenReset = 1
        self.stop()
        self._deleteTrack()
        if finish == 1:
            self.restore()
        self.attackDicts = []
        self.toonAttackDicts = {}
        self.generalAttackDicts = {}
        self.prevGenAttackIndex = -1
        self.restoreColor = 0
        self.restoreHips = 0
        self.restoreHeadScale = 0
        self.restoreToonScale = 0
        self.specialParticleEffects = []
        self.originalSoundPlayRates = {}
        for prop in self.renderProps:
            MovieUtil.removeProp(prop)

        self.renderProps = []

    def resetReward(self, finish=0):
        if self.rewardHasBeenReset == 1:
            return
        self.rewardHasBeenReset = 1
        self.stop()
        self._deleteTrack()
        if finish == 1:
            self.restore()
        self.toonRewardDicts = []
        if self.rewardPanel is not None:
            self.rewardPanel.destroy()
        self.rewardPanel = None

    def play(self, ts, callback, timescale: float = 1.0):
        # Display all active toons laff meters
        if settings['movie-laff-meters']:
            if base.localAvatar in self.battle.activeToons:
                for avatar in self.battle.activeToons:
                    if avatar != base.localAvatar:
                        self.laffMeters.append(OldLaffMeter.OldLaffMeter(avatar.style, avatar.getHp(), avatar.getMaxHp()))
                        self.laffMeterAvatars.append(avatar)
                for pos, laffMeter in enumerate(self.laffMeters):
                    avatar = self.laffMeterAvatars[pos]
                    laffMeter.setAvatar(avatar)
                    laffMeter.setScale(0.075)
                    laffMeter.reparentTo(base.a2dBottomLeft)
                    laffMeter.setPos(BattleGUIGlobals.MovieLaffMeterPos[pos])
                    laffMeter.start()
                    self.hpChangeEvents.append(avatar.uniqueName('hpChange'))
                    self.accept(self.hpChangeEvents[pos], self.updateLaffMeter, extraArgs=[pos])

        if settings['battle-target-indicator-toon'] or settings['battle-target-indicator-meter'] \
                and base.localAvatar in self.battle.activeToons:
            self.accept(BattleGlobals.BattleAvatarTargetedMessage, self._handleAvatarTargeted)

        self.hasBeenReset = 0
        ptrack = Sequence()
        camtrack = Sequence()
        if random.random() > 0.5:
            MovieUtil.shotDirection = "left"
        else:
            MovieUtil.shotDirection = "right"
        for s in self.battle.activeSuits:
            s.battleTrapIsFresh = 0

        for attack in self.attackDicts:
            if attack in TRACK_ORDER:
                attackDicts = self.toonAttackDicts[attack]
                tattacks, tcam = self.__doToonAttack(attack, attackDicts)
                if tattacks:
                    ptrack.append(tattacks)
                    camtrack.append(tcam)
            else:
                gattacks, gcam = self.__doGeneralAttack(attack)
                if gattacks:
                    ptrack.append(gattacks)
                    camtrack.append(gcam)
            ptrack.append(Func(self.battle.checkLocalToonSad))

        # Go through all battle avatars and see about making their cleanup anims.
        battleAvatars = self.battle.activeToons + self.battle.activeSuits
        effectCleanupSequences = {}

        # We are gonna have to clean the visual effects off of folks now!!
        def unapplyThisVisualEffect(effect):
            # Get the unapply movie for this effect.
            seqs = effect.getUnapplyMovie()
            removeSeq, cameraSeq = seqs

            # If we have a cleanup seq, let's clean it up!
            if removeSeq or cameraSeq:
                # Init the cleanup seq dict for this entry.
                effectCleanups = effect.__class__
                if effectCleanups not in effectCleanupSequences:
                    effectCleanupSequences[effectCleanups] = [Parallel(), Sequence()]

                # Add to these sequences.
                cleanupAnim, cleanupCam = effectCleanupSequences[effectCleanups]
                cleanupAnim.append(removeSeq)
                cleanupCam.append(cameraSeq)

        for av in battleAvatars:
            av: BattleAvatar

            # Get the removed visual effects that influence us.
            ourRemovedEffects = [
                removedVer
                for removedVer in self.battle.removedVisualEffects
                if removedVer.avId == av.doId
            ]

            # Check all of the present effects on this av.
            for effect in av.getVisualEffects():
                ver = VisualEffectRemoved(av.doId, effect.effectEnum)
                effectWasRemoved = any(
                    removedVer for removedVer in ourRemovedEffects if ver == removedVer
                )
                if effectWasRemoved:
                    # The effect was removed -- keep note of that.
                    ourRemovedEffects.remove(ver)

                    # And appropriately remove it.
                    unapplyThisVisualEffect(effect)

            # Do we have any leftover effects?
            for ver in ourRemovedEffects:
                # Let's make dummy VEs to try and clean these up now.
                effect = createVisualEffect(av, ver.effectEnum)

                # Unapply it too.
                unapplyThisVisualEffect(effect)

                # No leaks!
                effect.cleanup()

        # Add avatar cleanup anims.
        for cleanupAnim, cleanupCam in effectCleanupSequences.values():
            ptrack.append(cleanupAnim)
            camtrack.append(cleanupCam)

        def clearChat(suit):
            # sanity
            if suit and not suit.isEmpty():
                suit.clearChat()

        clearChatSeq = Parallel()
        for suit in self.battle.activeSuits:
            clearChatSeq.append(Func(clearChat, suit))
            # force splat clear because i hate you
            clearChatSeq.append(Func(suit.clearSplats))

        ptrack.append(clearChatSeq)
        self.battle.sendMovieEvent(BMLE.EVENT_ROUND_DONE, ptrack)
        ptrack.append(Func(callback))
        self._deleteTrack()
        self.track = Sequence(ptrack, name="movie-track-%d" % self.battle.doId)
        if self.battle.localToonPendingOrActive():
            self.track = Parallel(
                self.track,
                Sequence(camtrack),
                name="movie-track-with-cam-%d" % self.battle.doId,
            )
        if randomBattleTimestamp == 1:
            randNum = random.randint(0, 99)
            dur = self.track.getDuration()
            ts = float(randNum) / 100.0 * dur
        self.track.delayDeletes = []
        for suit in self.battle.suits:
            self.track.delayDeletes.append(DelayDelete.DelayDelete(suit, "Movie.play"))

        for toon in self.battle.toons:
            self.track.delayDeletes.append(DelayDelete.DelayDelete(toon, "Movie.play"))

        # Run all battleav visual effects.
        for battleAv in self.battle.activeToons + self.battle.activeSuits:
            for visualEffect in battleAv.getVisualEffects():
                visualEffect.roundStart()

        # Battle camera can leave input now.
        self.battle.camera.exitWaitForInput()

        # Begin playing :)
        playRate = self.battle.timescale
        self.recursiveSpeedUpSounds(self.track, playRate=playRate)
        self.track.start(ts, playRate=playRate)

    def recursiveSpeedUpSounds(self, track, playRate):
        for seq in track:
            if isinstance(seq, SoundInterval):
                if seq.sound is None:
                    continue
                # Some sounds have custom playrates, so we need to track those
                soundId = id(seq.sound)
                if soundId in self.originalSoundPlayRates:
                    ogSoundPlayrate = self.originalSoundPlayRates[soundId]
                else:
                    ogSoundPlayrate = seq.sound.getPlayRate() or 1.0
                    self.originalSoundPlayRates[soundId] = ogSoundPlayrate
                seq.sound.setPlayRate(ogSoundPlayrate * playRate)
            elif isinstance(seq, MetaInterval):
                self.recursiveSpeedUpSounds(seq, playRate)

    def updateTimescale(self, newTs: float):
        # Updates the timescale.
        self.battle.timescale = newTs
        self.track.setPlayRate(newTs)
        self.recursiveSpeedUpSounds(track=self.track, playRate=newTs)

    def finish(self):
        if not self.intervalHasFinished:
            self.forceFinish = True
        self.track.finish()

    def playReward(self, ts, name, callback, noSkip=False):
        self.rewardHasBeenReset = 0
        ptrack = Sequence()
        camtrack = Sequence()
        self.rewardPanel = RewardPanel.RewardPanel(name)
        self.rewardPanel.hide()
        victory, camVictory, skipper = MovieToonVictory.doToonVictory(
            self.battle.localToonActive(),
            self.battle.activeToons,
            self.toonRewardIds,
            self.toonRewardDicts,
            self.rewardPanel,
            allowGroupShot=1,
            updatedQuests=self.updatedQuests,
            noSkip=noSkip,
        )
        if victory:
            skipper.setIvals((ptrack, camtrack), ptrack.getDuration())
            ptrack.append(victory)
            camtrack.append(camVictory)
        ptrack.append(Func(callback))
        self._deleteTrack()
        self.track = Sequence(ptrack, name="movie-reward-track-%d" % self.battle.doId)
        if self.battle.localToonActive():
            self.track = Parallel(
                self.track,
                camtrack,
                name="movie-reward-track-with-cam-%d" % self.battle.doId,
            )

        self.track.delayDeletes = []
        for t in self.battle.activeToons:
            self.track.delayDeletes.append(
                DelayDelete.DelayDelete(t, "Movie.playReward")
            )

        skipper.setIvals((self.track,), 0.0)
        skipper.setBattle(self.battle)
        self.track.start(ts)

    def stop(self):
        if self.track:
            if not self.intervalHasFinished:
                self.forceFinish = True
            self.track.finish()
            self._deleteTrack()
        if hasattr(self, "track1"):
            self.track1.finish()
            self.track1 = None
        if hasattr(self, "track2"):
            self.track2.finish()
            self.track2 = None
        if hasattr(self, "track3"):
            self.track3.finish()
            self.track3 = None
        if self.rewardPanel:
            self.rewardPanel.hide()
        if self.playByPlayText:
            self.playByPlayText.hide()
        if hasattr(self, "laffMeters"):
            for laffMeter in self.laffMeters:
                laffMeter.destroy()
            self.laffMeters = []
        if hasattr(self, "hpChangeEvents"):
            for event in self.hpChangeEvents:
                self.ignore(event)
            self.hpChangeEvents = []
        if hasattr(self, "laffMeterAvatars"):
            self.laffMeterAvatars = []
        # Target indicator cleanups
        if self.targetSeqToons:
            for seq in self.targetSeqToons.values():
                seq.pause()
            self.targetSeqToons = {}
        if self.targetSeqMeters:
            for seq in self.targetSeqMeters.values():
                seq.pause()
            self.targetSeqMeters = {}
        if self.targetNodesToons:
            [node.removeNode() for node in self.targetNodesToons.values()]
            self.targetNodesToons = {}
        if self.targetNodesMeters:
            [frame.removeNode() for frame in self.targetNodesMeters.values()]
            self.targetNodesMeters = {}

        self.ignore(BattleGlobals.BattleAvatarTargetedMessage)

    def __doToonAttack(self, attackType, attackDicts):
        if ConfigVariableBool("want-toon-attack-anims", True).getValue():
            track = Sequence(name="toon-attacks")
            camTrack = Sequence(name="toon-attacks-cam")

            if attackType not in self.toonAttackToMovie:
                raise NotImplementedError(f"Attack enum: {attackType}")

            args = [[atk.atkDict for atk in attackDicts]]

            if attackType == AttackEnum.TOON_HEAL:
                hasHealBonus = self.battle.getInteractivePropTrackBonus() == AttackEnum.TOON_HEAL
                args.append(hasHealBonus)
            else:
                # Setting deadOrAboutToBe on suits that died from these attacks
                # This is to allow special death movies to exclude suits that are dying at the same time
                for attack in args[0]:
                    try:
                        targets = [attack['target']] if isinstance(attack['target'], dict) else attack['target']
                    except KeyError as e:
                        # Somehow the attack didn't have targets. Let's not even try
                        print('Toon attack raised exception after receiving non-existent attack target!')
                        print(e)
                        return None, None
                    for target in targets:
                        if target.get('died', False):
                            suit = target.get('suit', None)
                            if suit:
                                suit.deadOrAboutToBe = True

            # Call a try/except here for KeyErrors to try and catch __throwPie crashes
            ival = None
            try:
                ival, camIval = self.toonAttackToMovie[attackType](*args)
            except KeyError as e:
                print("Movie.py raised KeyError exception during movie calculation!")
                print(f"It looks like this: {str(e)}\n{repr(e)}")
                if __debug__:
                    print("We're debugging, so I'll just give ya the scoop.")
                    raise e
            if ival:
                track.append(ival)
                camTrack.append(camIval)

            if len(track) == 0:
                return (None, None)
            else:
                return (track, camTrack)
        else:
            return (None, None)

    def __doGeneralAttack(self, attackKey: tuple):
        # Unpack the attack objects from the list of tuples. (attackObj, attackGroup)
        attacks = [
            atk[0]
            for atk in self.generalAttackDicts[attackKey[0]]
            if atk[1] == attackKey[1]
        ]
        track = Parallel()
        cam = None
        for attack in attacks:
            gattacks, gcam = attack.getAttackMovie()
            if gattacks:
                # Just use the first camera track.
                if cam is None:
                    cam = gcam
                track.append(gattacks)
        return (track, cam) if track else (None, None)

    def genRewardDicts(self, toonBattleExp, updatedQuests):
        self.toonRewardDicts = BattleExperience.genRewardDicts(toonBattleExp)
        self.toonRewardIds = [exp[0] for exp in toonBattleExp]
        self.updatedQuests = dict(updatedQuests)

    def genAttackDicts(self, toons, suits, attackStructs):
        if self.track and self.track.isPlaying():
            self.notify.warning("genAttackDicts() - track is playing!")

        attacks = [] # type: list[Attack]
        for attack in attackStructs:
            if attack[1] in TRACK_ORDER:
                attacks.append(ToonAttack.fromStruct(attack))
            else:
                try:
                    attacks.append(AttackRepository[attack[1]].fromStruct(attack))
                except KeyError:
                    raise KeyError(f"Attack not found in the attack repository: {repr(AttackEnum(attack[1]))}")

        # Perform the attack callback, if we're feeling it
        if self.attackCallback:
            self.attackCallback(attacks)

        toonObjs = []
        for t in toons:
            toon = self.battle.findToon(t)
            if toon:
                toonObjs.append(toon)

        suitObjs = []
        for s in suits:
            suit = self.battle.findSuit(s)
            if suit:
                suitObjs.append(suit)

        for attack in attacks:
            attack.invoker = self.battle.findToon(attack.invokerId) or self.battle.findSuit(attack.invokerId)
            attack.toons = toonObjs[:]
            attack.suits = suitObjs[:]
            attack.movie = self
            attack.playByPlayText = self.playByPlayText
            attack.battle = self.battle

            for target in attack.targets:
                obj = self.battle.findToon(target.avId) or self.battle.findSuit(target.avId)
                if obj:
                    attack.targetObjs.append(obj)

            targetGone = attack.setTargets()

            if targetGone:
                self.notify.warning(f"genAttackDicts() - target gone for attack {attack.attackType}!")
                continue

            attackType = attack.attackType

            if attackType in TRACK_ORDER:
                if attackType in self.toonAttackDicts:
                    self.toonAttackDicts[attackType].append(attack)
                else:
                    self.toonAttackDicts[attackType] = [attack]
                    self.attackDicts.append(attackType)
            else:
                # Animate each attackType in groups for the sake of
                # keeping things hasty.
                if attackType in self.generalAttackDicts:
                    genAttackGroup, prevGenAttackIndex = self.generalAttackDicts[attackType][-1][1:]
                    # If the previous general attack of this same type happened later
                    # than 1 index before this one,
                    # group it into a new a group of general attacks of the same type.
                    # Also split them up if this attack type doesn't want to be
                    # ran in parallel.
                    if not attack.ALLOW_GROUPING or attack.attackIndex - prevGenAttackIndex > 1:
                        genAttackGroup += 1
                        self.attackDicts.append((attackType, genAttackGroup))

                    self.generalAttackDicts[attackType].append((attack, genAttackGroup, attack.attackIndex))
                else:
                    self.generalAttackDicts[attackType] = [(attack, 0, attack.attackIndex)]
                    self.attackDicts.append((attackType, 0))

    def setAttackCallback(self, func):
        """Whenever the list of attacks are made when making the attack dictionaries,
        this method will be called."""
        self.attackCallback = func

    def updateLaffMeter(self, laffMeter, hp, maxHp, quietly=0):
        self.laffMeters[laffMeter].adjustFace(hp, maxHp)

    def _handleAvatarTargeted(self, *doIds):
        if settings['battle-target-indicator-toon']:
            # Add nodes if we do not have enough
            if any(doId not in self.targetNodesToons for doId in doIds):
                circleModel = loader.loadModel("phase_5/models/effects/cc_m_txc_fx_bat_target_indicators")
                openBurst = circleModel.find("**/bat_target_circle_gear").copyTo(NodePath('toon-target-holder'))
                openBurst.setTransparency(1)
                openBurst.setColorScaleOff(1)
                openBurst.setColorScale(1, 0.175, 0.175, 0.9)
                openBurst.setAlphaScale(0)
                openBurst.setScale(4.45)
                openBurst.setP(-90)
                openBurst.setBin('shadow', 1)
                openBurst.hide()
                openBurst.reparentTo(hidden)
                for doId in doIds:
                    if doId not in self.targetNodesToons:
                        self.targetNodesToons[doId] = openBurst.copyTo(NodePath('toon-target-circle'))
                circleModel.removeNode()
                openBurst.removeNode()

            # Run through doIds and apply a sequence for each of them
            for i, doId in enumerate(doIds):
                toon = base.cr.doId2do.get(doId)
                if not toon:
                    continue
                if toon not in self.battle.activeToons:
                    continue
                ourCircle = self.targetNodesToons[doId]
                targetTrack = Sequence(
                    Func(ourCircle.reparentTo, render),
                    Func(ourCircle.setPos, toon, 0, 0, 0.025),
                    Func(ourCircle.setScale, 4.45),
                    Func(ourCircle.show),
                    LerpFunctionInterval(ourCircle.setAlphaScale, fromData=0, toData=0.6, duration=0.33, blendType='easeIn'),
                    LerpFunctionInterval(ourCircle.setAlphaScale, fromData=0.66, toData=0, duration=0.33, blendType='easeIn'),
                    LerpFunctionInterval(ourCircle.setAlphaScale, fromData=0, toData=0.6, duration=0.33, blendType='easeIn'),
                    LerpFunctionInterval(ourCircle.setAlphaScale, fromData=0.66, toData=0, duration=0.33, blendType='easeIn'),
                    Func(ourCircle.hide),
                    Func(ourCircle.reparentTo, hidden),
                )
                # Ensure the existing target sequence for this toon is finished,
                if doId in self.targetSeqToons:
                    self.targetSeqToons[doId].finish()

                # Finish it off by starting the toon target seq
                self.targetSeqToons[doId] = targetTrack
                self.targetSeqToons[doId].start()

        if settings['battle-target-indicator-meter']:
            textScaleNorm = (0.33, 0.26, 0.26)
            textScaleLarge = (textScaleNorm[0]*1.1, textScaleNorm[1]*1.1, textScaleNorm[2]*1.1)

            # Add nodes if we do not have enough
            if any(doId not in self.targetNodesMeters for doId in doIds):
                hpTextGen = base.localAvatar.HpTextGenerator
                hpTextGen.setFont(ToontownGlobals.getSignFont())
                hpTextGen.setTextColor(1, 0.1, 0.1, 1)
                hpTextGen.setText('!')
                hpTextGen.setAlign(TextNode.ACenter)
                targetNode = NodePath('meter-target-holder')
                targetNode.attachNewNode(hpTextGen.generate())
                targetNode.reparentTo(hidden)
                for doId in doIds:
                    if doId not in self.targetNodesMeters:
                        self.targetNodesMeters[doId] = targetNode.copyTo(NodePath('meter-target-exclamation'))
                targetNode.removeNode()

            for i, doId in enumerate(doIds):
                toon = base.cr.doId2do.get(doId)
                if not toon:
                    continue
                if toon not in self.battle.activeToons:
                    continue
                ourIndicator = self.targetNodesMeters[doId]

                if doId == base.localAvatar.doId:
                    # We can show this on your local laff meter no matter what
                    laffMeter = base.cr.gameGui.laffMeter
                elif settings['movie-laff-meters']:
                    # We need the movie laff meters option on to show this here
                    laffMeter = [lm for lm in self.laffMeters if lm.av is toon]
                    if not len(laffMeter):
                        continue
                    laffMeter = laffMeter[0]
                else:
                    # We don't have the option on and this is someone else's laff meter;
                    # We don't need to care about this targeting event
                    continue

                targetTrack = Sequence(
                    Func(ourIndicator.reparentTo, aspect2d),
                    Func(ourIndicator.setPos, laffMeter, 0.15, 0, 1.8),
                    Func(ourIndicator.setR, -40),
                    Func(ourIndicator.setScale, 0.01),
                    Func(ourIndicator.setAlphaScale, 1.0),
                    Func(ourIndicator.show),
                    Parallel(
                        LerpScaleInterval(ourIndicator, 0.14, textScaleNorm, blendType='easeIn'),
                        LerpHprInterval(ourIndicator, 0.14, (0, 0, 0), blendType='easeIn'),
                    ),
                    LerpScaleInterval(ourIndicator, 0.12, textScaleLarge, blendType='easeOut'),
                    LerpScaleInterval(ourIndicator, 0.12, textScaleNorm, blendType='easeIn'),
                    Wait(1.3),
                    Parallel(
                        LerpFunctionInterval(ourIndicator.setAlphaScale, fromData=1.0, toData=0, duration=0.33,
                                             blendType='easeIn'),
                        LerpHprInterval(ourIndicator, 0.33, (0, 0, 60), blendType='easeIn'),
                    ),
                    Func(ourIndicator.hide),
                    Func(ourIndicator.reparentTo, hidden),
                )
                if doId in self.targetSeqMeters:
                    self.targetSeqMeters[doId].finish()

                # Finish it off by starting the meter target seq
                self.targetSeqMeters[doId] = targetTrack
                self.targetSeqMeters[doId].start()
