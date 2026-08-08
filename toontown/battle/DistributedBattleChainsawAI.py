from direct.directnotify import DirectNotifyGlobal

from toontown.battle import DistributedBattleMinibossAI


class DistributedBattleChainsawAI(
        DistributedBattleMinibossAI.DistributedBattleMinibossAI):
    notify = DirectNotifyGlobal.directNotify.newCategory(
        'DistributedBattleChainsawAI')

    def __init__(self, air, bossCog, roundCallback, finishCallback, battleSide):
        DistributedBattleMinibossAI.DistributedBattleMinibossAI.__init__(
            self, air, bossCog, roundCallback, finishCallback, battleSide)
        # Altis' DistributedBattleFinalAI retains only bossCogId on the AI
        # object.  Chainsaw's dedicated calculator/modifier code needs the
        # live controller itself for RPM, phase, and cheat state.
        self.bossCog = bossCog
        self.maxSuits = 5

    def __findChainsaw(self):
        for suit in self.activeSuits:
            try:
                if suit.dna.name == 'chainsaw':
                    return suit
            except:
                pass
        return None

    def startBattle(self, toonIds, suits):
        # Chainsaw is already inside the office when the battle begins.  He is
        # the sole active Cog for turn one and occupies the front manager slot;
        # unlike later support Cogs he must never enter through the office door.
        #
        # Altis' generic miniboss startBattle() routes every supplied Suit
        # through suitRequestJoin(), which puts it in joiningSuits.  The client
        # then interprets it as a reserve and runs showSuitsFalling(), creating
        # the one-frame/ghost Cog and wrong opening lineup seen in v3.0.
        # Pre-stage the initial Chainsaw as active instead.  ReservesJoining is
        # still entered with an empty joining list so the client runs its
        # doInitialSuitsJoining() hook and places only Chainsaw at the canonical
        # front point.
        self.joinableFsm.request('Joinable')
        for toonId in toonIds:
            if self.addToon(toonId):
                self.activeToons.append(toonId)

        for suit in suits:
            self.addSuit(suit)
            if suit not in self.activeSuits:
                self.activeSuits.append(suit)
            try:
                suit.prepareToJoinBattle()
            except:
                pass

        try:
            self._rebuildSuitStateLists()
        except:
            pass
        self.d_setMembers()
        self.b_setState('ReservesJoining')

    def enterWaitForInput(self):
        # Install the modifiers before Toon damage is calculated for this
        # round.  Phase 2 changes damage *taken* based on current RPM; phases
        # 1/3 change the Chainsaw's outgoing normal attack damage.
        boss = self.__findChainsaw()
        controller = getattr(self, 'bossCog', None)
        if boss and controller:
            revving = self.battleCalc.chainsawCalculator.syncRevvingEffect(
                boss, controller)
            outgoing = float(revving.damageMod) if revving else 1.0
            bossCondition = 1.0

            if getattr(controller, 'chainsawKickbackRounds', 0) > 0:
                bossCondition *= float(getattr(
                    controller, 'chainsawKickbackMultiplier', 1.0))

            chainLinked = bool(getattr(
                controller, 'chainsawChainLinked', False))
            chainIds = getattr(controller, 'chainsawChainStartSupportIds', [])

            # Chain Link: Chainsaw is immune while a linked Cog survives.
            # The living chain is recalculated left-to-right every round: the
            # first Cog has no reduction, the next has 25%, then 50%, then 75%.
            linkedSupports = []
            for suit in self.activeSuits:
                if suit is boss:
                    continue
                try:
                    if suit.getHP() > 0 and suit.doId in chainIds:
                        linkedSupports.append(suit)
                except:
                    pass

            try:
                self.battleCalc.setSuitCondition(
                    boss.doId,
                    'vulnerablevideographer',
                    0.0 if chainLinked and linkedSupports else bossCondition,
                    -1,
                    'setBoth')
            except:
                pass

            for support in self.activeSuits:
                if support is boss:
                    continue
                if support in linkedSupports:
                    continue
                try:
                    self.battleCalc.setSuitCondition(
                        support.doId,
                        'vulnerablevideographer',
                        1.0,
                        -1,
                        'setBoth')
                except:
                    pass

            for index in xrange(len(linkedSupports)):
                support = linkedSupports[index]
                supportIncoming = min(1.0, 0.25 * (index + 1))
                try:
                    self.battleCalc.setSuitCondition(
                        support.doId,
                        'vulnerablevideographer',
                        supportIncoming,
                        -1,
                        'setBoth')
                except:
                    pass

            try:
                boss.setDamageMultiplier(outgoing)
            except:
                pass

        return DistributedBattleMinibossAI.DistributedBattleMinibossAI.enterWaitForInput(self)

    def localMovieDone(self, needUpdate, deadToons, deadSuits, lastActiveSuitDied):
        # Altis normally delays the membership packet until resume().  Chainsaw
        # can create a replacement reserve in that same callback, which left a
        # defeated Cog visible in the target list until the reserve movie was
        # over.  Push the post-death membership immediately; resume() will send
        # the later reserve membership as a second, normal update.
        if needUpdate or deadSuits or deadToons:
            try:
                self.d_setMembers()
            except:
                pass
        return DistributedBattleMinibossAI.DistributedBattleMinibossAI.localMovieDone(
            self, needUpdate, deadToons, deadSuits, lastActiveSuitDied)

    def _pruneChainsawStaleSuitState(self):
        # Altis' generic __removeSuit() does not notify BattleCalculatorAI via
        # suitLeftBattle().  With reserve-heavy Chainsaw rounds this can leave a
        # deleted Cog doId in currentlyLuredSuits; the next movieDone() then
        # indexes air.doId2do[oldId] and resets the district with KeyError.
        activeIds = []
        for suit in self.activeSuits:
            try:
                if not suit.isDeleted():
                    activeIds.append(suit.doId)
            except:
                try:
                    activeIds.append(suit.doId)
                except:
                    pass

        try:
            staleIds = []
            for suitId in self.battleCalc.currentlyLuredSuits.keys():
                if suitId not in activeIds or suitId not in self.air.doId2do:
                    staleIds.append(suitId)
            for suitId in staleIds:
                try:
                    self.battleCalc.suitLeftBattle(suitId)
                except:
                    try:
                        del self.battleCalc.currentlyLuredSuits[suitId]
                    except:
                        pass
        except:
            pass

    def movieDone(self):
        self._pruneChainsawStaleSuitState()
        return DistributedBattleMinibossAI.DistributedBattleMinibossAI.movieDone(self)

