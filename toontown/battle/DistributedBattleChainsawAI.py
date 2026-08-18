from direct.directnotify import DirectNotifyGlobal

from toontown.battle import DistributedBattleMinibossAI
from toontown.battle.BattleBase import SUIT_ATK_COL, SUIT_HP_COL, TOON_DIED_COL


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
        boss = self.__findChainsaw()
        controller = getattr(self, 'bossCog', None)
        if boss:
            promoted = []
            regular = []
            for suit in self.activeSuits:
                if suit is boss:
                    continue
                if getattr(suit, 'chainsawManagerBeneficiary', False):
                    promoted.append(suit)
                else:
                    regular.append(suit)
            ordered = [boss] + regular + promoted
            if ordered != self.activeSuits:
                try:
                    if self._setActiveSuitOrderPrivately(ordered):
                        self.d_setMembers()
                except:
                    pass
        if boss and controller:
            revving = self.battleCalc.chainsawCalculator.syncRevvingEffect(
                boss, controller)
            if controller.chainsawPhase == 1:
                outgoing = float(revving.damageMod) if revving else 1.0
                outgoing = max(1.0, min(2.0, outgoing))
            elif controller.chainsawPhase == 3:
                outgoing = float(revving.damageMod) if revving else 1.0
                outgoing = max(1.0, min(3.0, outgoing))
            else:
                outgoing = 1.0

            bossCondition = 1.0
            if getattr(controller, 'chainsawKickbackRounds', 0) > 0:
                bossCondition *= float(getattr(
                    controller, 'chainsawKickbackMultiplier', 1.0))

            chainLinked = bool(getattr(
                controller, 'chainsawChainLinked', False))
            chainIds = getattr(controller, 'chainsawChainStartSupportIds', [])
            linkedSupports = []
            for suit in self.activeSuits:
                if suit is boss:
                    continue
                try:
                    if suit.getHP() > 0 and suit.doId in chainIds:
                        linkedSupports.append(suit)
                except:
                    pass

            linkedSuits = []
            if chainLinked and linkedSupports:
                linkedSuits = [boss] + linkedSupports
            incoming = [0.0, 0.25, 0.5, 0.75, 1.0]
            if linkedSuits:
                incoming = incoming[-len(linkedSuits):]

            try:
                bossIncoming = bossCondition
                if linkedSuits:
                    bossIncoming *= incoming[0]
                self.battleCalc.setSuitCondition(
                    boss.doId, 'vulnerablevideographer', bossIncoming,
                    -1, 'setBoth')
            except:
                pass

            for support in self.activeSuits:
                if support is boss:
                    continue
                try:
                    supportIncoming = 1.0
                    if support in linkedSuits:
                        supportIncoming = incoming[linkedSuits.index(support)]
                    self.battleCalc.setSuitCondition(
                        support.doId, 'vulnerablevideographer',
                        supportIncoming, -1, 'setBoth')
                except:
                    pass

            try:
                boss.setDamageMultiplier(outgoing)
            except:
                pass

        return DistributedBattleMinibossAI.DistributedBattleMinibossAI.enterWaitForInput(self)

    def _clampDeadwoodMovieDamage(self):
        controller = getattr(self, 'bossCog', None)
        if not controller or not getattr(controller, 'chainsawDeadwoodTriggered', False):
            return

        deadwoodIndex = -1
        for index in xrange(len(self.suitAttacks)):
            attack = self.suitAttacks[index]
            data = attack[SUIT_ATK_COL]
            if data and data.get('name', '').startswith('ChainsawCoreDeadwood'):
                deadwoodIndex = index
                break

        if deadwoodIndex < 0:
            return

        for toonIndex in xrange(len(self.activeToons)):
            toonId = self.activeToons[toonIndex]
            toon = self.getToon(toonId)
            if not toon:
                continue

            totalDamage = 0
            for attack in self.suitAttacks:
                hps = attack[SUIT_HP_COL]
                if toonIndex < len(hps) and hps[toonIndex] > 0:
                    totalDamage += hps[toonIndex]

            allowedDamage = max(0, toon.getHp() - 1)
            allowedDamage = 0
            excess = max(0, totalDamage - allowedDamage)

            for attackIndex in xrange(len(self.suitAttacks) - 1, deadwoodIndex, -1):
                if excess <= 0:
                    break
                attack = self.suitAttacks[attackIndex]
                hps = attack[SUIT_HP_COL]
                if toonIndex >= len(hps) or hps[toonIndex] <= 0:
                    continue
                reduction = min(hps[toonIndex], excess)
                hps[toonIndex] -= reduction
                excess -= reduction

            if excess > 0:
                attack = self.suitAttacks[deadwoodIndex]
                hps = attack[SUIT_HP_COL]
                if toonIndex < len(hps) and hps[toonIndex] > 0:
                    reduction = min(hps[toonIndex], excess)
                    hps[toonIndex] -= reduction
                    excess -= reduction

            for attackIndex in xrange(deadwoodIndex - 1, -1, -1):
                if excess <= 0:
                    break
                attack = self.suitAttacks[attackIndex]
                hps = attack[SUIT_HP_COL]
                if toonIndex >= len(hps) or hps[toonIndex] <= 0:
                    continue
                reduction = min(hps[toonIndex], excess)
                hps[toonIndex] -= reduction
                excess -= reduction

            mask = ~(1 << toonIndex)
            for attack in self.suitAttacks:
                attack[TOON_DIED_COL] &= mask

    def d_setMovie(self):
        self._clampDeadwoodMovieDamage()
        return DistributedBattleMinibossAI.DistributedBattleMinibossAI.d_setMovie(self)

    def _compactChainsawActiveSuits(self):
        boss = self.__findChainsaw()
        if not boss:
            return
        supports = []
        for suit in self.activeSuits:
            if suit is boss:
                continue
            try:
                if suit.getHP() <= 0:
                    continue
            except:
                pass
            supports.append(suit)
        ordered = [boss] + supports
        if ordered != self.activeSuits:
            self.activeSuits[:] = ordered

    def localMovieDone(self, needUpdate, deadToons, deadSuits, lastActiveSuitDied):
        result = DistributedBattleMinibossAI.DistributedBattleMinibossAI.localMovieDone(
            self, needUpdate, deadToons, deadSuits, lastActiveSuitDied)
        if needUpdate or deadSuits or deadToons:
            self._compactChainsawActiveSuits()
            try:
                self.d_setMembers()
            except:
                pass
        return result

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

