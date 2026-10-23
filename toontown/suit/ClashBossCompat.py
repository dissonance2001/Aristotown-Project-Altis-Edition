"""
Compatibility layer so Corporate Clash's VP (client + AI) can run on top of
Altis's DistributedBossCog / DistributedBossCogAI.

Everything here either replaces a Clash-only base-class feature (unites, IOUs,
department exp bars, the Clash music manager, ...) with the closest Altis
behaviour, or turns it into a harmless no-op.
"""
from direct.directnotify import DirectNotifyGlobal

# Altis-side files that are known to exist (taken from the Altis VP code).
ClashMusicFiles = {
    'battleTwoMusic': 'phase_7/audio/bgm/encntr_suit_winning_indoor.ogg',
    'battleThreeMusic': 'phase_9/audio/bgm/encntr_head_suit_theme.ogg',
    'victoryMusic': 'phase_9/audio/bgm/encntr_toon_winning.ogg',
    'promotionMusic': 'phase_9/audio/bgm/encntr_head_suit_theme.ogg',
    'fleeingBattleOneMusic': 'phase_9/audio/bgm/encntr_sting_announce.ogg',
    'battleThreePrepMusic': 'phase_9/audio/bgm/encntr_toon_winning.ogg',
}


class ClashMusicShim:
    """Implements the handful of base.musicMgr calls the Clash VP makes, on
    top of Altis's base.playMusic and plain AudioSound objects."""

    def __init__(self):
        self.playing = []

    def playMusic(self, sound, looping=0, volume=1.0, time=0.0, **kwargs):
        if sound is None or isinstance(sound, str):
            return
        # Clash's music manager plays one track at a time: stop whatever else is playing first
        for other in list(self.playing):
            if other is not sound:
                other.stop()
                self.playing.remove(other)
        # ...including the tracks Altis's own base class started (elevator, battle one, sting, ...)
        owner = getattr(self, 'owner', None)
        if owner is not None:
            for attr in ('elevatorMusic', 'battleOneMusic', 'stingMusic', 'epilogueMusic', 'battleTwoMusic',
                         'battleThreeMusic', 'victoryMusic', 'promotionMusic', 'fleeingBattleOneMusic',
                         'battleThreePrepMusic', 'battleThreeDizzyMusic', 'killMusic'):
                other = getattr(owner, attr, None)
                if other is not None and other is not sound and hasattr(other, 'stop'):
                    other.stop()
        base.playMusic(sound, looping=looping, volume=volume, time=time)
        if sound not in self.playing:
            self.playing.append(sound)

    def stopMusic(self, sound=None):
        if sound is None:
            for s in self.playing:
                s.stop()
            self.playing = []
        elif not isinstance(sound, str):
            sound.stop()
            if sound in self.playing:
                self.playing.remove(sound)

    def getMusicTime(self, sound):
        if sound is None or isinstance(sound, str):
            return 0.0
        return sound.getTime()

    def getMusicFilepath(self, sound):
        if sound is None or isinstance(sound, str):
            return sound
        return sound.getName()


def installClashSkelecogNametagPatch():
    """Client only. Turning a cog into a skelecog rebuilds its model, which drops its clickable
    nametag. The boss sets the skelecog flag after the cogs are generated, so skelecogs in the VP
    battle could not be clicked. Re-enable the nametag after the rebuild (Clash VP battles only)."""
    try:
        from toontown.suit import DistributedSuitBase
    except Exception:
        return
    cls = DistributedSuitBase.DistributedSuitBase
    if getattr(cls, '_clashSkelePickablePatched', False):
        return

    def inClashVpBattle():
        try:
            for obj in base.cr.doId2do.values():
                if getattr(obj, 'useClashJoinCam', False):
                    return True
        except Exception:
            pass
        return False

    def wrap(original):
        def setSkelecog(self, flag, *args, **kwargs):
            result = original(self, flag, *args, **kwargs)
            if flag and inClashVpBattle():
                try:
                    self.setPickable(1)
                except Exception:
                    pass
            return result
        return setSkelecog

    for name in ('setSkelecog', 'setSkelecog2'):
        if hasattr(cls, name):
            setattr(cls, name, wrap(getattr(cls, name)))
    cls._clashSkelePickablePatched = True


def installClashBattleFinalPatch():
    """Client only. Replaces DistributedBattleFinal.showSuitsJoining for the Clash VP (and only
    for it; OCVP keeps Altis's behaviour) without touching the Altis file. Cogs grow while they
    walk out of the door and walk straight to their final battle spot instead of stopping at
    the pending spot first."""
    try:
        from toontown.battle import DistributedBattleFinal as dbf
    except Exception:
        return
    cls = dbf.DistributedBattleFinal
    if getattr(cls, '_clashJoinPatched', False):
        return
    original = cls.showSuitsJoining

    def showSuitsJoining(self, suits, ts, name, callback):
        bossCog = self.bossCog
        if bossCog is None or not getattr(bossCog, 'useClashJoinCam', False):
            return original(self, suits, ts, name, callback)
        import random
        from direct.interval.IntervalGlobal import Func, Parallel, Sequence, Track
        from panda3d.core import VBase3, Point3
        if self.battleSide:
            openDoor = Func(bossCog.doorB.request, 'open')
            closeDoor = Func(bossCog.doorB.request, 'close')
        else:
            openDoor = Func(bossCog.doorA.request, 'open')
            closeDoor = Func(bossCog.doorA.request, 'close')
        active = list(self.activeSuits)
        joining = list(self.joiningSuits)
        total = len(active) + len(joining)
        if len(active) < 2:
            ordered = active + joining
        else:
            ordered = active[:-1] + joining + [active[-1]]
        suitTrack = Parallel()
        delay = 0
        for suit in suits:
            suit.setState('Battle')
            suit.setPos(bossCog, 0, 0, 0)
            suit.headsUp(self)
            suit.setScale(3.8 / suit.height)
            if suit in joining and suit in ordered and 0 < total <= 4:
                # walk straight to the final spot (same layout Altis's adjust step would use)
                point = self.suitPoints[total - 1][ordered.index(suit)]
                destPos = Point3(point[0])
                destHpr = VBase3(point[1], 0, 0)
            elif suit in self.joiningSuits:
                i = len(self.pendingSuits) + self.joiningSuits.index(suit)
                destPos, h = self.suitPendingPoints[i]
                destHpr = VBase3(h, 0, 0)
            else:
                destPos, destHpr = self.getActorPosHpr(suit, self.suits)
            # grow while walking so the cog reaches full size as it arrives
            growTime = max(1.0, self.calcSuitMoveTime(destPos, suit.getPos(self)))
            suitTrack.append(Track((delay, self.createAdjustInterval(suit, destPos, destHpr)),
                                   (delay, suit.scaleInterval(growTime, 1))))
            delay += 1
        if self.hasLocalToon() and hasattr(base, 'camera') and base.camera is not None:
            base.camera.reparentTo(self)
            if random.choice([0, 1]):
                base.camera.setPosHpr(20, -4, 7, 60, 0, 0)
            else:
                base.camera.setPosHpr(-20, -4, 7, -60, 0, 0)
        track = Sequence(openDoor, suitTrack, closeDoor, Func(callback), name=name)
        track.start(ts)
        self.storeInterval(track, name)

    cls.showSuitsJoining = showSuitsJoining
    cls._clashJoinPatched = True


class ClashBossClientCompat:
    """Mixin placed in front of DistributedBossCog for DistributedClashSellbotBoss."""

    prevCogSuitType = 0
    localUniteEffectPageNumber = -1
    updatedQuests = None
    healthGui = None

    @property
    def musicMgr(self):
        mgr = self.__dict__.get('_clashMusicMgr')
        if mgr is None:
            mgr = ClashMusicShim()
            mgr.owner = self
            self.__dict__['_clashMusicMgr'] = mgr
        return mgr

    def clashBaseAnnounceGenerate(self):
        """Altis's base announceGenerate plus the bits Clash's base adds."""
        from toontown.suit import DistributedBossCog, BossHealthBar
        from toontown.coghq import CogDisguiseGlobals
        installClashBattleFinalPatch()
        installClashSkelecogNametagPatch()
        DistributedBossCog.DistributedBossCog.announceGenerate(self)
        # Altis's base uses its own arena battle spots; Clash's VP arena (BossRoomHQ) needs Clash's
        from toontown.suit import BossCogGlobals
        self.battleANode.setPosHpr(*BossCogGlobals.BossCogBattleAPosHpr)
        self.battleBNode.setPosHpr(*BossCogGlobals.BossCogBattleBPosHpr)
        try:
            self.prevCogSuitType = localAvatar.getCogTypes()[CogDisguiseGlobals.dept2deptIndex(self.style.dept)]
        except Exception:
            self.prevCogSuitType = 0
        self.healthGui = BossHealthBar.BossHealthBar(self.style.dept, 1, 1)
        self.healthGui.load()
        self.healthGui.hide()

    def clashDestroyHealthGui(self):
        if self.healthGui:
            self.healthGui.destroy()
            self.healthGui = None

    def loadClashMusic(self):
        """Replace Clash's music-manager keys with real Altis AudioSounds.
        elevator / sting / battle-one / epilogue music are already loaded by
        Altis's DistributedBossCog.loadEnvironment, so they are left alone."""
        for attr, path in ClashMusicFiles.items():
            setattr(self, attr, base.loader.loadMusic(path))
        self.battleThreeDizzyMusic = self.battleThreeMusic
        self.killMusic = self.battleThreeMusic

    def preloadFinalBattleMusic(self):
        self.preloadedFinalBattleMusic = None
        self.preloadedFinalBattleDizzyMusic = None

    def handleUniteSpeech(self, speech):
        return speech

    def handleLocalUniteEffect(self):
        pass

    def hideToonsMeters(self):
        for toonId in getattr(self, 'involvedToons', []):
            toon = base.cr.doId2do.get(toonId)
            if toon and hasattr(toon, 'obscureOverheadMeter'):
                toon.obscureOverheadMeter(True)

    def setBattleDifficulty(self, difficulty):
        self.battleDifficulty = difficulty


    # ---- toon / battle plumbing Clash's base class has and Altis's does not ----

    useClashJoinCam = True  # read by Altis's DistributedBattleFinal.showSuitsJoining

    def releaseToons(self, finalBattle=0):
        """Clash's version: in the final (pie) battle every toon is released even if a stale
        battle object still lists it, otherwise the toon stays frozen."""
        for toonId in self.involvedToons:
            toon = self.cr.doId2do.get(toonId)
            if toon:
                if self.battleA and toon in self.battleA.toons and not finalBattle:
                    pass
                elif self.battleB and toon in self.battleB.toons and not finalBattle:
                    pass
                else:
                    toon.startLookAround()
                    toon.startSmooth()
                    toon.wrtReparentTo(render)
                    if toon == localAvatar:
                        if finalBattle:
                            self.toFinalBattleMode()
                        else:
                            self.toWalkMode()

    attackThreshold = 1.0  # grace period (seconds) after being zapped by the VP, like Clash

    def zapLocalToon(self, attackCode, origin=None):
        from toontown.suit import DistributedBossCog
        now = globalClock.getFrameTime()
        if now < getattr(self, 'lastZapLocalTime', 0) + self.attackThreshold:
            return
        wasStunned = localAvatar.isStunned
        DistributedBossCog.DistributedBossCog.zapLocalToon(self, attackCode, origin)
        if not wasStunned and localAvatar.isStunned:
            self.lastZapLocalTime = now

    def clashAcceptNametagClicks(self):
        """Altis's base class only reacts to nametag clicks in the pie battle; OCVP lets you click
        toons and cogs in every battle state. Do the same for the Clash VP."""
        self.accept('clickedNametag', self.clashClickedNameTag)
        self.accept('friendAvatar', self.clashHandleFriendAvatar)
        self.accept('avatarDetails', self.clashHandleAvatarDetails)

    def clashClickedNameTag(self, avatar):
        from toontown.friends import FriendsListManager
        place = self.cr.playGame.getPlace() if self.cr else None
        if place and hasattr(place, 'fsm'):
            FriendsListManager.FriendsListManager._FriendsListManager__handleClickedNametag(place, avatar)

    def clashHandleFriendAvatar(self, avId, avName, avDisableName):
        from toontown.friends import FriendsListManager
        place = self.cr.playGame.getPlace() if self.cr else None
        if place and hasattr(place, 'fsm'):
            FriendsListManager.FriendsListManager._FriendsListManager__handleFriendAvatar(place, avId, avName, avDisableName)

    def clashHandleAvatarDetails(self, avId, avName, playerId=None):
        from toontown.friends import FriendsListManager
        place = self.cr.playGame.getPlace() if self.cr else None
        if place and hasattr(place, 'fsm'):
            FriendsListManager.FriendsListManager._FriendsListManager__handleAvatarDetails(place, avId, avName, playerId)

    def clashIdleToons(self):
        """Put every involved toon back on its idle loop and restart the look-around task."""
        for toonId in self.involvedToons:
            toon = self.cr.doId2do.get(toonId)
            if toon and not toon.isDisguised:
                try:
                    toon.loop('neutral')
                    toon.startLookAround()
                except Exception:
                    pass

    def clashBaseEnterBattleTwo(self):
        """Clash's base enterBattleTwo (Altis's base class has none)."""
        from toontown.toonbase import ToontownBattleGlobals
        self.cleanupIntervals()
        localAvatar.inventory.setBattleCreditMultiplier(ToontownBattleGlobals.getBossBattleCreditMultiplier(2))
        self.toonsToBattlePosition(self.toonsA, self.battleANode)
        self.toonsToBattlePosition(self.toonsB, self.battleBNode)
        self.releaseToons()
        self.musicMgr.playMusic(self.battleTwoMusic, looping=1, volume=0.9)

    def clashBaseExitBattleTwo(self):
        self.cleanupBattles()
        self.musicMgr.stopMusic(self.battleTwoMusic)
        localAvatar.inventory.setBattleCreditMultiplier(1)


class ClashBossAICompat:
    """Mixin placed in front of DistributedBossCogAI for DistributedClashSellbotBossAI."""

    begunToonAmount = -1
    toonLevels = 0

    def getBattleAPosHpr(self):
        from toontown.suit import BossCogGlobals
        return BossCogGlobals.BossCogBattleAPosHpr

    def getBattleBPosHpr(self):
        from toontown.suit import BossCogGlobals
        return BossCogGlobals.BossCogBattleBPosHpr

    def getToonDifficulty(self):
        """Clash semantics: compute once into self.toonLevels (and also return it, as Altis does).
        Safe with zero toons (everybody disconnected during the elevator ride)."""
        import math
        if self.toonLevels != 0:
            return self.toonLevels
        totalCogSuitTier = 0
        totalToons = 0
        for toonId in self.involvedToons:
            toon = simbase.air.doId2do.get(toonId)
            if not toon:
                continue
            totalToons += 1
            reviveLevels = getattr(toon, 'cogReviveLevels', None)
            if reviveLevels and reviveLevels[self.deptIndex] >= 0:
                totalCogSuitTier += 7
            else:
                totalCogSuitTier += toon.cogTypes[self.deptIndex]
        self.toonLevels = int(math.floor(totalCogSuitTier / max(1, totalToons)) + 1)
        return self.toonLevels

    # Clash-sized VP waves. Altis's VP planner entries (level pool 300, cog levels 12-30, boss
    # level 31) are tuned for OCVP and make the Clash VP far too hard, so the Clash VP builds
    # its own, much smaller waves here.
    VP_MAX_COG_LEVEL = 13
    VP_ACTIVE_COGS = 4
    VP_RESERVE_COGS = 4
    VP_BATTLE_ONE_LEVELS = (5, 12)
    VP_BATTLE_TWO_LEVELS = (8, 12)

    def invokeSuitPlanner(self, buildingCode, skelecog, skelecogRandom=0, dept=None, **kwargs):
        """Build one VP wave: VP_ACTIVE_COGS cogs that start the battle plus VP_RESERVE_COGS
        reserves, boss department only, no cog above level VP_MAX_COG_LEVEL, no V2 revives and
        no Governaughts (executives, e.g. 13.exe, are still possible)."""
        import random
        from toontown.building import SuitPlannerInteriorAI
        from toontown.suit import SuitDNA
        if dept is None:
            dept = self.dna.dept
        maxLevel = self.VP_MAX_COG_LEVEL
        lo, hi = self.VP_BATTLE_TWO_LEVELS if skelecog else self.VP_BATTLE_ONE_LEVELS
        hi = min(hi, maxLevel)
        total = self.VP_ACTIVE_COGS + self.VP_RESERVE_COGS
        levels = sorted(random.randint(lo, hi) for _ in range(total - 1))
        levels.append(maxLevel)  # the wave's strongest cog is a reserve and is level 13
        planner = SuitPlannerInteriorAI.SuitPlannerInteriorAI(1, buildingCode, dept, self.zoneId)
        planner.respectInvasions = 0
        joinChances = sorted(random.sample(range(1, 101), self.VP_RESERVE_COGS))
        active = []
        reserve = []
        for index, level in enumerate(levels):
            info = {'track': dept, 'level': level, 'revives': 0,
                    'type': SuitDNA.getRandomSuitTierSpawn(level, dept)}
            if index < self.VP_ACTIVE_COGS:
                active.append(info)
            else:
                info['joinChance'] = joinChances[index - self.VP_ACTIVE_COGS]
                reserve.append(info)
        planner.suitInfos = [{'activeSuits': active, 'reserveSuits': reserve}]
        suits = planner.genFloorSuits(0)
        allSuits = list(suits['activeSuits']) + [r[0] for r in suits['reserveSuits']]
        for suit in allSuits:
            if suit.getSkeleRevives():
                suit.b_setSkeleRevives(0)
            if suit.getGovernaught():
                suit.b_setGovernaught(0)
            if suit.getActualLevel() > maxLevel:
                suit.setLevel(maxLevel, forceLevel=True)
            if skelecog:
                flag = 1 if not skelecogRandom else random.randint(0, 1)
                # Altis's b_setSkelecog calls self.isSkeleton(flag) on an int and crashes
                suit.setSkelecog(flag)
                suit.d_setSkelecog(flag)
        return suits

    def handleRoundDone(self, battle, suits, activeSuits, toonIds, totalHp, deadSuits):
        """Altis's base version appends the (suit, joinChance) reserve *tuples* straight into the
        suit lists, which is what its Miniboss battle expects. The final-battle AI used by this
        boss (DistributedBattleFinalAI.resume) wants Toontown's original behaviour: suits join by
        HP-lost percentage and joinedReserves holds the tuples."""
        totalMaxHp = 0
        for suit in suits:
            totalMaxHp += suit.getMaxHp()

        for suit in deadSuits:
            if suit in activeSuits:
                activeSuits.remove(suit)

        joinedReserves = []
        if len(self.reserveSuits) > 0 and len(activeSuits) < 4:
            hpPercent = 100 - (totalHp / float(totalMaxHp) * 100.0) if totalMaxHp > 0 else 100
            for info in self.reserveSuits:
                if info[1] <= hpPercent and len(activeSuits) < 4:
                    suits.append(info[0])
                    activeSuits.append(info[0])
                    joinedReserves.append(info)

            for info in joinedReserves:
                self.reserveSuits.remove(info)

        battle.resume(joinedReserves)

    def enterWaitForToons(self):
        super().enterWaitForToons()
        # Clash's base records how many toons started the fight (used for the solo-defeat log).
        self.begunToonAmount = len(self.involvedToons)

    def resetBattles(self):
        # Altis's base only deletes the legacy self.suits list, so suits from battle one/two
        # (suitsA/suitsB) would leak when the next battle is set up. Clash/original behaviour:
        sendReset = 0
        if self.battleA:
            self.battleA.requestDelete()
            self.battleA = None
            self.battleAId = 0
            sendReset = 1
        if self.battleB:
            self.battleB.requestDelete()
            self.battleB = None
            self.battleBId = 0
            sendReset = 1
        for suit in list(self.suitsA) + list(self.suitsB):
            suit.requestDelete()
        for suit, joinChance in self.reserveSuits:
            suit.requestDelete()
        self.suitsA = []
        self.activeSuitsA = []
        self.suitsB = []
        self.activeSuitsB = []
        self.suits = []
        self.activeSuits = []
        self.reserveSuits = []
        self.battleNumber = 0
        if sendReset:
            self.sendBattleIds()

    def removeSkipButton(self):
        # Altis bosses use the built-in BossCutsceneSkip vote instead.
        pass

    def handleUniteRewards(self, toon):
        pass

    def prepareReward(self, rewardState='Reward'):
        # Same order as Altis's own VP: tell clients, switch state, then hand out the rewards.
        from toontown.battle import BattleExperienceAI
        from toontown.toonbase import ToontownGlobals
        self.d_setBattleExperience()
        self.b_setState(rewardState)
        BattleExperienceAI.assignRewards(self.involvedToons, self.toonSkillPtsGained, self.suitsKilled,
                                         ToontownGlobals.dept2cogHQ(self.dept), self.helpfulToons)

    def rewardClubCoins(self):
        pass

    def chatOnHit(self):
        pass

    def addDeptExp(self, toon, amount):
        fn = getattr(toon, 'addDepartmentExp', None)
        if fn:
            from toontown.toonbase import ToontownGlobals
            fn(amount, getattr(ToontownGlobals, 'DEPARTMENT_SELLBOT', 0))

    def showTip(self, toon, tipName):
        fn = getattr(toon, 'showToonTip', None)
        if not fn:
            return
        try:
            from toontown.toon.gui.ToonTipGlobals import TTE
            tip = getattr(TTE, tipName, None)
        except ImportError:
            return
        if tip is not None:
            fn(tip)


# Strings the Clash VP / BossHealthBar use that Altis's TTLocalizerEnglish lacks.
# Installed only when missing, so adding them to TTLocalizerEnglish later is safe.
ClashLocalizerStrings = {
    'BossBarDamage': 'Damage Dealt: %s',
    'BossBarStuns': 'Stuns: %s',
    'BossBarHealth': '%s/%s',
    'BossBarGolf': 'Golf: %s',
    'BossBarCogDestruction': 'Cog Destruction: %s',
    'BossBarGoonsStomped': 'Goons Stomped: %s',
    'CagedToonTeleportAccess': '\x07Also, these promotion papers seem to mention something about "GPS coordinates" to Sellbot HQ!\x07I\'ll have these converted into teleport access for you, pronto!',
}


# Clash versions of strings whose Altis counterparts lack the format
# placeholders that Clash's VP code formats into them (a plain "%s" or the
# "primary"/"jump" dict keys). Always installed under a Clash-prefixed name;
# the Clash VP client uses these.
ClashOnlyLocalizerStrings = {'CagedToonThankYouTemp': {
        'one': "Thanks a lot for saving me again, by the way.\x07For your valiant efforts, I'll give you some IOUs!\x07You can call myself and {npc} during battle, and we'll come to help you out!\x07Don't worry about me, I'll do my best not to get captured again.",
        'many': "Thanks a lot for saving me again, by the way.\x07For your valiant efforts, I'll give you some IOUs!\x07You can call myself, {npcFirst} and {npcLast} during battle, and we'll come to help you out!\x07Don't worry about me, I'll do my best not to get captured again.",
    },
    'ClashCagedToonYippee': 'Thank you, %s! You took down the V.P.!',
 'ClashCagedToonPrepareBattleThree': 'Alright, now we need to attack the V.P. Cog directly.\x07Luckily, the '
                                     'Resistance has given me a whole bunch of pies you can use!\x07Jump up '
                                     "and touch the bottom of my cage and I'll give you some pies.\x07Press "
                                     "the %s key to throw pies once you've got them!",
 'ClashBossBattleHowToThrowPies': 'Press the %s key to throw pies!',
 'ClashCagedToonBattleThree': {10: 'Nice jump, %(toon)s.  Here are some pies!',
                               11: 'Hi, %(toon)s!  Have some pies!',
                               12: 'Good job, %(toon)s!  Here, have some pies!',
                               20: 'Hey, %(toon)s!  Jump up to the cage and get some pies to throw!',
                               21: 'Hi, %(toon)s!  Use the %(jump)s key to jump up here so I can give you '
                                   'some pies!',
                               100: 'Press the %(primary)s key to throw a pie.',
                               101: 'The blue power meter shows how high your pie will go.',
                               102: 'First, try to lob a pie inside his undercarriage to gum up his works.',
                               103: 'Wait for the door to open, and throw a pie straight inside.',
                               104: "When he's dizzy, hit him in the face or chest to knock him back!",
                               105: "You'll know you've got a good hit when you see the splat in color.",
                               106: 'If you hit a Toon with a pie, it gives that Toon a Laff point!'}}


def installClashLocalizerStrings():
    from toontown.toonbase import TTLocalizer
    for name, text in ClashLocalizerStrings.items():
        if not hasattr(TTLocalizer, name):
            setattr(TTLocalizer, name, text)
    for name, text in ClashOnlyLocalizerStrings.items():
        setattr(TTLocalizer, name, text)


installClashLocalizerStrings()
