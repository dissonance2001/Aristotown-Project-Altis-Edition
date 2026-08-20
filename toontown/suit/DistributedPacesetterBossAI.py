from __future__ import absolute_import
from direct.directnotify import DirectNotifyGlobal
from direct.fsm import FSM
import types
from otp.avatar import DistributedAvatarAI

from toontown.battle import BattleBase
from toontown.battle import BattleExperienceAI
from toontown.suit import DistributedMinibossAI
from toontown.suit import SuitDNA
from toontown.toonbase import ToontownGlobals


class DistributedPacesetterBossAI(DistributedMinibossAI.DistributedMinibossAI, FSM.FSM):
    """Server-side standalone Pacesetter miniboss controller.

    DistributedMinibossAI is only used for its battle/toon/barrier bookkeeping;
    unlike Altis's *client* DistributedMiniboss class, this AI base does not
    inherit BossCog.  Its default BossCog DNA is replaced with real ``psetter``
    Suit DNA immediately below.
    """

    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedPacesetterBossAI')

    def __init__(self, air):
        # Do NOT call DistributedMinibossAI.__init__ here.  Although that AI
        # class does not inherit BossCog, its constructor creates temporary
        # BossCog DNA and registers the object in AllBossCogs.  Pacesetter is a
        # standalone Suit miniboss, so initialise only the generic distributed
        # avatar/battle bookkeeping we actually reuse from that helper class.
        DistributedAvatarAI.DistributedAvatarAI.__init__(self, air)
        FSM.FSM.__init__(self, 'DistributedPacesetterBossAI')

        self.dna = SuitDNA.SuitDNA()
        self.dna.newSuit('psetter')
        self.dept = self.dna.dept
        self.deptIndex = SuitDNA.suitDepts.index(self.dept)

        self.resetBattleCounters()
        self.looseToons = []
        self.involvedToons = []
        self.toons = []
        self.nearToons = []
        self.suits = []
        self.activeSuits = []
        self.reserveSuits = []
        self.barrier = None
        self.keyStates = ['BattleOne', 'Reward']

        # Fields referenced by inherited generic battle helpers.  They no
        # longer drive a BossCog final round, but keeping them initialised makes
        # the reused battle bookkeeping self-contained and predictable.
        self.bossDamage = 0
        self.battleThreeStart = 0
        self.battleThreeDuration = 1800
        self.attackCode = None
        self.attackAvId = 0
        self.hitCount = 0
        self.nerfed = False
        self.numRentalDiguises = 0
        self.numNormalDiguises = 0

        self.pacesetterSuitId = 0
        self.pacesetterRewardsGranted = False

    def getHoodId(self):
        return ToontownGlobals.DonaldsDreamland

    def formatReward(self):
        return 'pacesetter'

    # ------------------------------------------------------------------
    # One real Pacesetter Suit battle
    # ------------------------------------------------------------------

    def initializeBattles(self, battleNumber, bossCogPosHpr):
        # Altis's generic DistributedMinibossAI.initializeBattles() calls
        # generateSuits() twice.  For Pacesetter that would create a second,
        # orphaned psetter actor beside the one used by the battle/CTSC.
        # Generate exactly once so there is exactly one real Pacesetter.
        self.resetBattles()
        if not self.involvedToons:
            self.notify.warning('initializeBattles: no toons!')
            return

        self.battleNumber = battleNumber
        suitHandles = self.generateSuits(battleNumber)
        self.suits = suitHandles['activeSuits']
        self.activeSuits = self.suits[:]
        self.reserveSuits = suitHandles['reserveSuits']

        if self.toons:
            self.battle = self.makeBattle(
                bossCogPosHpr,
                ToontownGlobals.BossCogBattleAPosHpr,
                self.handleRoundADone,
                self.handleBattleADone,
                battleNumber,
                0)
            self.battleId = self.battle.doId
        else:
            self.moveSuits(self.activeSuits)
            self.suits = []
            self.activeSuits = []
            if self.arenaSide is None:
                self.b_setArenaSide(0)

        self.sendBattleIds()

    def makeBattleOneBattles(self):
        # Pacesetter is a miniboss instance: the real psetter Suit battle is
        # the fight.  There is no inherited CJ BattleTwo/BattleThree round.
        self.postBattleState = 'Reward'
        self.initializeBattles(1, ToontownGlobals.PacesetterBattleAPosHpr)

    def generateSuits(self, battleNumber):
        if battleNumber != 1:
            return {'activeSuits': [], 'reserveSuits': []}

        cogs = self.invokeEmptyPlanner(11, 'pace')
        activeSuits = cogs['activeSuits']
        reserveSuits = cogs['reserveSuits']

        while len(activeSuits) >= 6:
            suit = activeSuits.pop()
            reserveSuits.append((suit, 100))

        def compareJoinChance(a, b):
            return cmp(a[1], b[1])

        reserveSuits.sort(compareJoinChance)
        return {
            'activeSuits': activeSuits,
            'reserveSuits': reserveSuits,
        }

    def generateNewReserves(self, battleNumber, specialCode):
        cogs = self.invokeReservesPlanner(11, specialCode)
        return {'reserveSuits': cogs['reserveSuits']}

    def __findPacesetterSuit(self):
        for suit in self.activeSuits:
            try:
                if suit.dna.name == 'psetter':
                    return suit
            except:
                pass
        for suit in self.suits:
            try:
                if suit.dna.name == 'psetter':
                    return suit
            except:
                pass
        return None

    def __installPacesetterHPClamp(self, pacesetter):
        if not pacesetter or getattr(pacesetter, '_pacesetterHPClampInstalled', False):
            return

        originalSetHP = pacesetter.setHP
        originalBSetHP = pacesetter.b_setHP
        originalDSetHP = pacesetter.d_setHP

        def clampHP(hp):
            try:
                return max(0, hp)
            except:
                return hp

        def setHPClamped(suit, hp):
            return originalSetHP(clampHP(hp))

        def b_setHPClamped(suit, hp):
            return originalBSetHP(clampHP(hp))

        def d_setHPClamped(suit, hp):
            return originalDSetHP(clampHP(hp))

        def bind(func):
            try:
                return types.MethodType(func, pacesetter, pacesetter.__class__)
            except TypeError:
                return types.MethodType(func, pacesetter)

        pacesetter.setHP = bind(setHPClamped)
        pacesetter.b_setHP = bind(b_setHPClamped)
        pacesetter.d_setHP = bind(d_setHPClamped)
        pacesetter._pacesetterHPClampInstalled = True
        self.notify.info('Installed Pacesetter 0-HP clamp on suit %s.' % pacesetter.doId)

    def d_setPacesetterSuitId(self, suitId):
        self.pacesetterSuitId = suitId
        self.sendUpdate('setPacesetterSuitId', [suitId])

    # ------------------------------------------------------------------
    # Standalone state flow
    # ------------------------------------------------------------------

    def enterWaitForToons(self):
        # Dynamic-zone clients need enough time to finish quietZone.  The
        # client also waits for its place FSM to reach walk before releasing
        # this barrier, preventing the old movable-elevator race.
        self.acceptNewToons()
        self.barrier = self.beginBarrier(
            'WaitForToons', self.involvedToons, 120,
            self.__donePacesetterWaitForToons)

    def __donePacesetterWaitForToons(self, avIds):
        self.b_setState('Elevator')

    def exitWaitForToons(self):
        self.ignoreBarrier(self.barrier)

    def enterElevator(self):
        self.resetBattles()
        self.d_setPacesetterSuitId(0)
        self.barrier = self.beginBarrier(
            'Elevator', self.involvedToons, 30,
            self.__doneElevator)

    def __doneElevator(self, avIds):
        self.b_setState('Introduction')

    def exitElevator(self):
        self.ignoreBarrier(self.barrier)

    def enterIntroduction(self):
        self.resetBattles()
        self.arenaSide = None
        self.makeBattleOneBattles()

        pacesetter = self.__findPacesetterSuit()
        if pacesetter:
            self.__installPacesetterHPClamp(pacesetter)
            self.d_setPacesetterSuitId(pacesetter.doId)
        else:
            self.notify.warning('BattleOne generated without a psetter Suit.')
            self.d_setPacesetterSuitId(0)

        self.barrier = self.beginBarrier(
            'Introduction', self.involvedToons, 500,
            self.__doneIntroduction)

    def __doneIntroduction(self, avIds):
        self.b_setState('BattleOne')

    def exitIntroduction(self):
        self.ignoreBarrier(self.barrier)

    def enterBattleOne(self):
        if self.battle:
            self.battle.startBattle(self.toons, self.suits)

    def exitBattleOne(self):
        # handleBattleADone already deletes the finished battle and changes to
        # postBattleState.  Do not create any second/final BossCog round.
        pass

    # ------------------------------------------------------------------
    # Rewards / completion
    # ------------------------------------------------------------------

    def __grantPacesetterRewards(self):
        if self.pacesetterRewardsGranted:
            return
        self.pacesetterRewardsGranted = True

        self.d_setBattleExperience()
        BattleExperienceAI.assignRewards(
            self.involvedToons,
            self.toonSkillPtsGained,
            self.suitsKilled,
            ToontownGlobals.dept2cogHQ(self.dept),
            self.helpfulToons)

        for toonId in self.involvedToons:
            toon = self.air.doId2do.get(toonId)
            if toon:
                # Standalone miniboss bookkeeping only.  Do not award CJ Cog
                # Summons, CJ statistics, or any legacy Lawbot boss rewards.
                toon.b_promote(self.deptIndex)
                simbase.air.questManager.toonDefeatedBoss(
                    toon,
                    ToontownGlobals.dept2cogHQ(self.dept),
                    self.dna.dept,
                    self.involvedToons)

    def enterReward(self):
        self.__grantPacesetterRewards()
        self.resetBattles()
        self.d_setPacesetterSuitId(0)
        DistributedMinibossAI.DistributedMinibossAI.enterReward(self)

    def enterVictory(self):
        # Compatibility for administrator-forced old state names.  Normal
        # gameplay goes BattleOne -> Reward directly.
        self.__grantPacesetterRewards()
        self.barrier = self.beginBarrier(
            'Victory', self.involvedToons, 5,
            self.__doneVictory)

    def __doneVictory(self, avIds):
        self.b_setState('Reward')

    def exitVictory(self):
        self.ignoreBarrier(self.barrier)

    def enterEpilogue(self):
        DistributedMinibossAI.DistributedMinibossAI.enterEpilogue(self)
