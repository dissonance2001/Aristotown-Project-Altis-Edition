import random, sys
from math import floor
from toontown.battle.BattleBase import *
from toontown.battle.BattleGlobals import *
from toontown.battle.DistributedBattleAI import *
from toontown.toonbase import ToontownBattleGlobals
from math import floor
from direct.directnotify import DirectNotifyGlobal
from direct.interval.IntervalGlobal import *
from toontown.toonbase.ToontownBattleGlobals import *
from toontown.toonbase import ToontownGlobals
from toontown.suit import DistributedSuitBaseAI
from toontown.battle import SuitBattleGlobals
from toontown.battle import BattleExperienceAI
from toontown.toon import NPCToons
from toontown.pets import PetTricks, DistributedPetProxyAI
from toontown.hood import ZoneUtil
from toontown.toonbase.ToonPythonUtil import lerp

class BattleCalculatorAI:
    notify = DirectNotifyGlobal.directNotify.newCategory('BattleCalculatorAI')
    notify.setDebug(True)
    AccuracyBonuses = [0, 20, 40, 60]
    DamageBonuses = [0, 20, 20, 20]
    DamageBonusesDrop = [0, 30, 30, 30]
    AttackExpPerTrack = [0, 10, 20, 30, 40, 50, 60, 70]
    TRAP_CONFLICT = -2
    NumRoundsLured = ToontownBattleGlobals.AvLureRounds
    NumRoundsSoaked = ToontownBattleGlobals.AvSoakRounds
    NumRoundsMarked = ToontownBattleGlobals.AvMarkRounds
    NumRoundsDazed = ToontownBattleGlobals.AvDazeRounds
    APPLY_HEALTH_ADJUSTMENTS = 1
    TOONS_TAKE_NO_DAMAGE = 0
    CAP_HEALS = 1
    CLEAR_SUIT_ATTACKERS = 1
    SUITS_UNLURED_IMMEDIATELY = 1
    CLEAR_MULTIPLE_TRAPS = 0
    KBBONUS_LURED_FLAG = 0
    KBBONUS_TGT_LURED = 1
    notify = DirectNotifyGlobal.directNotify.newCategory('BattleCalculatorAI')
    toonsAlwaysHit = simbase.config.GetBool('toons-always-hit', False)
    toonsAlwaysMiss = simbase.config.GetBool('toons-always-miss', False)
    toonsAlways5050 = simbase.config.GetBool('toons-always-5050', False)
    suitsAlwaysHit = simbase.config.GetBool('suits-always-hit', False)
    suitsAlwaysMiss = simbase.config.GetBool('suits-always-miss', False)
    immortalSuits = simbase.config.GetBool('immortal-suits', False)
    propAndOrganicBonusStack = simbase.config.GetBool('prop-and-organic-bonus-stack', False)

    def __init__(self, battle, tutorialFlag = 0):
        self.battle = battle
        self.SuitAttackers = {}
        self.currentlyLuredSuits = {}
        self.currentlyWetSuits = {}
        self.currentlySoakedSuits = {}
        self.currentlyImmuneSuits = {}
        self.currentlyEnragedSuits = {}
        self.currentlyAbsorbingSuits = {}
        self.successfulLures = {}
        self.toonAtkOrder = []
        self.toonHPAdjusts = {}
        self.toonSkillPtsGained = {}
        self.traps = {}
        self.npcTraps = {}
        self.suitAtkStats = {}
        self.roundsToonsHit = 0
        self.roundsCogsMiss = 0
        self.__clearBonuses(hp=1)
        self.__clearBonuses(hp=0)
        self.delayedUnlures = []
        self.__skillCreditMultiplier = simbase.air.baseXpMultiplier
        self.tutorialFlag = tutorialFlag
        self.trainTrapTriggered = False
        self.fireDifficulty = 0
        self.TurnsElapsed = 0
        self.TurnsSinceSummonWithOnlyOneCog = 0
        self.TurnsSinceSummon = 0
        self.numShadowsSummoned = 0

        # a dictionary of each toon's status conditions
        #
        # each status is formatted this way
        # 'condition': {modifier, turnsRemaining}
        #
        # the dictionary holds all four toons, so a possible dictionary could be
        # { 10000000: { 'corruption': {'modifier': 2, 'turnsRemaining': -1} } }
        self.toonStatusConditions = {}

        self.suitStatusConditions = {}

    def toonHasCondition(self, toonId, condition):
        #self.notify.debug('toonHasCondition() - checking for \'%s\' on toonId %i' % (condition, toonId))
        if toonId not in self.toonStatusConditions:
            return False

        if condition in self.toonStatusConditions[toonId]:
            return True
        else:
            return False

    def getToonConditionModifier(self, toonId, condition):
        if not self.toonHasCondition(toonId, condition):
            #self.notify.warning('getToonConditionModifier() - method called, but toon %i did not have %s condition' % (
            #toonId, condition))
            return 0
        return self.toonStatusConditions[toonId][condition]['modifier']

    def getToonConditionTurns(self, toonId, condition):
        if not self.toonHasCondition(toonId, condition):
            #self.notify.warning(
                #'getToonConditionTurns() - method called, but toon %i did not have %s condition' % (toonId, condition))
            return 0
        return self.toonStatusConditions[toonId][condition]['turnsRemaining']

    def setToonCondition(self, toonId, condition, modifier, turns, mode='none'):
        # first, check if the toon is even in the dictionary
        if toonId not in self.toonStatusConditions:
            # if not, make them an entry
            self.toonStatusConditions[toonId] = {}

        if condition not in ToontownBattleGlobals.ValidStatusConditions:
            self.notify.warning(
                'setToonCondition() - ERROR! Condition %s is not a valid condition! Not setting.' % condition)
            return

        # special handling to remove a condition
        if modifier == 0 or turns == 0 and mode == 'none':
            if condition in self.toonStatusConditions[toonId]:
                del self.toonStatusConditions[toonId][condition]
            return

        # next, check if the toon has the condition already
        if condition not in self.toonStatusConditions[toonId]:
            # if not, add the condition, and we're done
            self.toonStatusConditions[toonId][condition] = {'modifier': modifier, 'turnsRemaining': turns}
            return
        else:
            # otherwise, increase the existing modifier appropriately
            newModifier = 0  # the variable we will set the modifier to
            newTurns = 0  # the variable we will set the turns to

            # modifier APPENDED, turns SET, used to change a buff/debuff's timer, but keep its potency
            if mode is 'refreshTurns':
                newModifier = self.getToonConditionModifier(toonId, condition) + modifier
                newTurns = turns

            # modifer SET, turns APPENDED, used to modify a buff/debuff's potency, but change its duration
            if mode is 'refreshModifier':
                newModifier = modifier
                newTurns = self.getToonConditionTurns(toonId, condition) + turns

            # modifier APPENDED, turns APPENDED, used to change a buff/debuff's potency AND duration
            if mode is 'refreshBoth':
                newModifier = self.getToonConditionModifier(toonId, condition) + modifier
                newTurns = self.getToonConditionTurns(toonId, condition) + turns

            # modifier SET, turns SET, used to explicitly set a modifier to a precise potency and duration
            if mode is 'setBoth':
                newModifier = modifier
                newTurns = turns

            if mode is 'alternateBoth':
                if modifier > self.toonStatusConditions[toonId][condition]['modifier']:
                    newModifier = modifier
                else:
                    newModifier = self.toonStatusConditions[toonId][condition]['modifier']
                newTurns = turns

            if mode is 'refreshTurnNoUndercut':
                newModifier = modifier
                if turns > self.toonStatusConditions[toonId][condition]['turnsRemaining']:
                    newTurns = turns
                else:
                    newTurns = self.toonStatusConditions[toonId][condition]['turnsRemaining']

            self.notify.debug(
                'setToonCondition() - gave toon %i condition %s with modifier %i with %i turns remaining' % (
                toonId, condition, newModifier, newTurns))
            self.toonStatusConditions[toonId][condition] = {'modifier': newModifier, 'turnsRemaining': newTurns}

    def suitHasCondition(self, suitId, condition):
        #self.notify.debug('suitHasCondition() - checking for \'%s\' on suitId %i' % (condition, suitId))
        if suitId not in self.suitStatusConditions:
            return False

        if condition in self.suitStatusConditions[suitId]:
            return True
        else:
            return False

    def getSuitConditionModifier(self, suitId, condition):
        if not self.suitHasCondition(suitId, condition):
            self.notify.warning('getSuitConditionModifier() - method called, but suit %i did not have %s condition' % (
            suitId, condition))
            return 0
        return self.suitStatusConditions[suitId][condition]['modifier']

    def getSuitConditionTurns(self, suitId, condition):
        if not self.suitHasCondition(suitId, condition):
            self.notify.warning(
                'getSuitConditionTurns() - method called, but suit %i did not have %s condition' % (suitId, condition))
            return 0
        return self.suitStatusConditions[suitId][condition]['turnsRemaining']

    def setSuitCondition(self, suitId, condition, modifier, turns, mode='none'):
        # first, check if the suit is even in the dictionary
        if suitId not in self.suitStatusConditions:
            # if not, make them an entry
            self.suitStatusConditions[suitId] = {}

        if condition not in ToontownBattleGlobals.ValidStatusConditions:
            self.notify.warning(
                'setSuitCondition() - ERROR! Condition %s is not a valid condition! Not setting.' % condition)
            return

        # special handling to remove a condition
        if modifier == 0 or turns == 0 and mode == 'none':
            if condition in self.suitStatusConditions[suitId]:
                del self.suitStatusConditions[suitId][condition]
            return

        # next, check if the suit has the condition already
        if condition not in self.suitStatusConditions[suitId]:
            # if not, add the condition, and we're done
            self.suitStatusConditions[suitId][condition] = {'modifier': modifier, 'turnsRemaining': turns}
            return
        else:
            # otherwise, increase the existing modifier appropriately
            newModifier = 0  # the variable we will set the modifier to
            newTurns = 0  # the variable we will set the turns to

            # modifier APPENDED, turns SET, used to change a buff/debuff's timer, but keep its potency
            if mode is 'refreshTurns':
                newModifier = self.getSuitConditionModifier(suitId, condition) + modifier
                newTurns = turns

            # modifer SET, turns APPENDED, used to modify a buff/debuff's potency, but change its duration
            if mode is 'refreshModifier':
                newModifier = modifier
                newTurns = self.getSuitConditionTurns(suitId, condition) + turns

            # modifier APPENDED, turns APPENDED, used to change a buff/debuff's potency AND duration
            if mode is 'refreshBoth':
                newModifier = self.getSuitConditionModifier(suitId, condition) + modifier
                newTurns = self.getSuitConditionTurns(suitId, condition) + turns

            # modifier SET, turns SET, used to explicitly set a modifier to a precise potency and duration
            if mode is 'setBoth':
                newModifier = modifier
                newTurns = turns

            if mode is 'alternateBoth':
                if modifier > self.suitStatusConditions[suitId][condition]['modifier']:
                    newModifier = modifier
                else:
                    newModifier = self.suitStatusConditions[suitId][condition]['modifier']
                newTurns = turns

            if mode is 'refreshTurnNoUndercut':
                newModifier = modifier
                if turns > self.suitStatusConditions[suitId][condition]['turnsRemaining']:
                    newTurns = turns
                else:
                    newTurns = self.suitStatusConditions[suitId][condition]['turnsRemaining']

            self.notify.debug(
                'setSuitCondition() - gave suit %i condition %s with modifier %i with %i turns remaining' % (
                suitId, condition, newModifier, newTurns))
            self.suitStatusConditions[suitId][condition] = {'modifier': newModifier, 'turnsRemaining': newTurns}

    def decrementConditionTurns(self):
        for toon in self.toonStatusConditions.keys():
            for condition in self.toonStatusConditions[toon].keys():
                if self.toonStatusConditions[toon][condition]['turnsRemaining'] > 0:
                    self.notify.debug(
                        'decrementConditionTurns() - Decremented %s condition on toon %i (new turns: %i)' % (
                        condition, toon, self.toonStatusConditions[toon][condition]['turnsRemaining'] - 1))
                    self.toonStatusConditions[toon][condition]['turnsRemaining'] -= 1

                if self.toonStatusConditions[toon][condition]['turnsRemaining'] == 0:
                    self.notify.debug(
                        'decrementConditionTurns() - %s condition on toon %i have reached 0, removing.' % (
                        condition, toon))
                    del self.toonStatusConditions[toon][condition]

        for suit in self.suitStatusConditions.keys():
            for condition in self.suitStatusConditions[suit].keys():
                if self.suitStatusConditions[suit][condition]['turnsRemaining'] > 0:
                    self.notify.debug(
                        'decrementConditionTurns() - Decremented %s condition on suit %i (new turns: %i)' % (
                        condition, suit, self.suitStatusConditions[suit][condition]['turnsRemaining'] - 1))
                    self.suitStatusConditions[suit][condition]['turnsRemaining'] -= 1

                if self.suitStatusConditions[suit][condition]['turnsRemaining'] == 0:
                    self.notify.debug(
                        'decrementConditionTurns() - %s condition on suit %i have reached 0, removing.' % (
                        condition, suit))
                    del self.suitStatusConditions[suit][condition]
            if not self.suitStatusConditions[suit].keys():
                del self.suitStatusConditions[suit]

    def printToonConditions(self):
        self.notify.debug('printToonConditions() *********************************************')
        self.notify.debug('printToonConditions(): Beginning Turn Readout')
        self.notify.debug('printToonConditions() *********************************************')
        for toon in self.toonStatusConditions:
            self.notify.debug('printToonConditions(): Toon %i has the following Conditions:' % toon)
            for condition in self.toonStatusConditions[toon]:
                self.notify.debug('printToonConditions(): %s x %i, with %i turn%s remaining' % (
                condition, self.toonStatusConditions[toon][condition]['modifier'],
                self.toonStatusConditions[toon][condition]['turnsRemaining'] - 1,
                '' if self.toonStatusConditions[toon][condition]['turnsRemaining'] - 1 == 1 else 's'))
        self.notify.debug('printToonConditions() *********************************************')
        self.notify.debug('printToonConditions(): Ending Turn Readout')
        self.notify.debug('printToonConditions() *********************************************')

    def printSuitConditions(self):
        self.notify.debug('printSuitConditions() *********************************************')
        self.notify.debug('printSuitConditions(): Beginning Turn Readout')
        self.notify.debug('printSuitConditions() *********************************************')
        for suit in self.suitStatusConditions:
            self.notify.debug('printSuitConditions(): Suit %i has the following Conditions:' % suit)
            for condition in self.suitStatusConditions[suit]:
                self.notify.debug('printSuitConditions(): %s x %i, with %i turn%s remaining' % (
                condition, self.suitStatusConditions[suit][condition]['modifier'],
                self.suitStatusConditions[suit][condition]['turnsRemaining'] - 1,
                '' if self.suitStatusConditions[suit][condition]['turnsRemaining'] - 1 == 1 else 's'))
        self.notify.debug('printSuitConditions() *********************************************')
        self.notify.debug('printSuitConditions(): Ending Turn Readout')
        self.notify.debug('printSuitConditions() *********************************************')

    def setSkillCreditMultiplier(self, mult):
        self.__skillCreditMultiplier = simbase.air.baseXpMultiplier * mult

    def getSkillCreditMultiplier(self):
        return self.__skillCreditMultiplier

    def cleanup(self):
        self.battle = None

    def __calcToonAtkHit(self, attackIndex, atkTargets):
        if len(atkTargets) == 0:
            return (0, 0)
        if self.tutorialFlag:
            return (1, 95)
        if self.toonsAlways5050:
            roll = random.randint(0, 70)
            if roll > 40:
                return (1, 95)
            else:
                return (0, 0)
        if self.toonsAlwaysHit:
            return (1, 95)
        elif self.toonsAlwaysMiss:
            return (0, 0)
        debug = self.notify.getDebug()
        attack = self.battle.toonAttacks[attackIndex]
        atkTrack, atkLevel = self.__getActualTrackLevel(attack)

        hasAccuracyBuff = False
        toon = simbase.air.doId2do.get(attack[TOON_ID_COL])
        if toon:
            if toon.hasBuff(BGagAccuracy):
                if not ZoneUtil.isDynamicZone(toon.zoneId):
                    if ZoneUtil.getWhereName(toon.zoneId, True) in ('street', 'factoryExterior', 'cogHQExterior'):
                        hasAccuracyBuff = True

        if atkTrack == NPCSOS:
            return (1, 95)
        if atkTrack == FIRE:
            return (1, 95)
        if atkTrack == TRAP:
            if debug:
                self.notify.debug('Attack is a trap, so it hits regardless')
            attack[TOON_ACCBONUS_COL] = 0
            return (1, 100)
        elif atkTrack == DROP and attack[TOON_TRACK_COL] == NPCSOS:
            unluredSuits = 0
            for tgt in atkTargets:
                if not self.__suitIsLured(tgt.getDoId()):
                    unluredSuits = 1

            if unluredSuits == 0:
                attack[TOON_ACCBONUS_COL] = 1
                return (0, 0)
        elif atkTrack == DROP:
            allLured = True
            for i in xrange(len(atkTargets)):
                if self.__suitIsLured(atkTargets[i].getDoId()):
                    pass
                else:
                    allLured = False

            if allLured:
                attack[TOON_ACCBONUS_COL] = 1
                return (0, 0)
        elif atkTrack == PETSOS:
            return self.__calculatePetTrickSuccess(attack)
        tgtDef = 0
        numLured = 0
        if atkTrack != HEAL:
            for currTarget in atkTargets:
                thisSuitDef = self.__targetDefense(currTarget, atkTrack)
                if self.__isWet(currTarget.getDoId()):
                    if currTarget.getDoId() in self.currentlyWetSuits.keys():
                        if self.currentlyWetSuits[currTarget.getDoId()][2]:
                            thisSuitDef -= 20
                if debug:
                    self.notify.debug('Examining suit def for toon attack: ' + str(thisSuitDef))
                tgtDef = min(thisSuitDef, tgtDef)
                if self.__suitIsLured(currTarget.getDoId()):
                    numLured += 1

        trackExp = self.__toonTrackExp(attack[TOON_ID_COL], atkTrack)
        for currOtherAtk in self.toonAtkOrder:
            if currOtherAtk != attack[TOON_ID_COL]:
                nextAttack = self.battle.toonAttacks[currOtherAtk]
                nextAtkTrack = self.__getActualTrack(nextAttack)
                if atkTrack == nextAtkTrack and attack[TOON_TGT_COL] == nextAttack[TOON_TGT_COL]:
                    currTrackExp = self.__toonTrackExp(nextAttack[TOON_ID_COL], atkTrack)
                    if debug:
                        self.notify.debug('Examining toon track exp bonus: ' + str(currTrackExp))
                    trackExp = max(currTrackExp, trackExp)

        if debug:
            if atkTrack == HEAL:
                self.notify.debug('Toon attack is a heal, no target def used')
            else:
                self.notify.debug('Suit defense used for toon attack: ' + str(tgtDef))
            self.notify.debug('Toon track exp bonus used for toon attack: ' + str(trackExp))
        if attack[TOON_TRACK_COL] == NPCSOS:
            randChoice = 0
        elif attack[TOON_TRACK_COL] == ZAP:
            randChoice = 0
        elif attack[TOON_TRACK_COL] == DROP:
            randChoice = 0
        else:
            randChoice = random.randint(0, 99)
        propAcc = AvPropAccuracy[atkTrack][atkLevel]
        if hasAccuracyBuff:
            propAcc *= BGagAccuracyMultiplier
        if atkTrack == DROP:
            treebonus = self.__toonCheckGagBonus(attack[TOON_ID_COL], atkTrack, atkLevel)
            propBonus = self.__checkPropBonus(atkTrack)
            if self.propAndOrganicBonusStack:
                propAcc = 0
                if treebonus:
                    self.notify.debug('using organic bonus lure accuracy')
                    propAcc = AvDropBonusAccuracy[atkLevel]
                if propBonus:
                    self.notify.debug('using prop bonus lure accuracy')
                    propAcc = AvDropBonusAccuracy[atkLevel]
            elif treebonus or propBonus:
                self.notify.debug('using oragnic OR prop bonus lure accuracy')
                propAcc = AvDropBonusAccuracy[atkLevel]
        #if atkTrack == ZAP:
            #for tgt in atkTargets:
                #if self.suitHasCondition(suit.doId, 'soaked'):
                    #propAcc = 100
                    #break
                #else:
                    #continue
        attackAcc = propAcc + trackExp + tgtDef
        currAtk = self.toonAtkOrder.index(attackIndex)
        if currAtk > 0 and atkTrack != HEAL:
            prevAtkId = self.toonAtkOrder[currAtk - 1]
            prevAttack = self.battle.toonAttacks[prevAtkId]
            prevAtkTrack = self.__getActualTrack(prevAttack)
            lure = atkTrack == LURE and (not attackAffectsGroup(atkTrack, atkLevel,
             attack[TOON_TRACK_COL]) and attack[TOON_TGT_COL] in self.successfulLures or attackAffectsGroup(atkTrack, atkLevel, attack[TOON_TRACK_COL]))
            if atkTrack == prevAtkTrack and (attack[TOON_TGT_COL] == prevAttack[TOON_TGT_COL] or lure):
                if prevAttack[TOON_ACCBONUS_COL] == 1:
                    if debug:
                        self.notify.debug('DODGE: Toon attack track dodged')
                elif prevAttack[TOON_ACCBONUS_COL] == 0:
                    if debug:
                        self.notify.debug('HIT: Toon attack track hit')
                attack[TOON_ACCBONUS_COL] = prevAttack[TOON_ACCBONUS_COL]
                return (not attack[TOON_ACCBONUS_COL], attackAcc)
        atkAccResult = attackAcc
        if debug:
            self.notify.debug('setting atkAccResult to %d' % atkAccResult)
        acc = attackAcc + self.__calcToonAccBonus(attackIndex)
        if atkTrack != LURE and atkTrack != HEAL:
            if atkTrack != DROP:
                if numLured == len(atkTargets):
                    if debug:
                        self.notify.debug('all targets are lured, attack hits')
                    attack[TOON_ACCBONUS_COL] = 0
                    return (1, 100)
                else:
                    luredRatio = float(numLured) / float(len(atkTargets))
                    accAdjust = 100 * luredRatio
                    if accAdjust > 0 and debug:
                        self.notify.debug(str(numLured) + ' out of ' + str(len(atkTargets)) + ' targets are lured, so adding ' + str(accAdjust) + ' to attack accuracy')
                    acc += accAdjust
            elif numLured == len(atkTargets):
                if debug:
                    self.notify.debug('all targets are lured, attack misses')
                attack[TOON_ACCBONUS_COL] = 0
                return (0, 0)
        if acc > MaxToonAcc:
            acc = MaxToonAcc

        if self.suitHasCondition(attack[TOON_TGT_COL], 'dodgy'):
            self.notify.debug('Original accuracy target: %i' % acc)
            acc *= abs(self.getSuitConditionModifier(attack[TOON_TGT_COL], 'dodgy') - 100.0) / 100.0    # 100% dodgy is 0x chance to hit, 50% dodgy is 50% from base acc., and -50% dodgy is 150% chance to hit from base, -100% is 2x
            self.notify.debug('Toon attack target has dodgy, modifying accuracy by %fx, new accuracy target is %f' % ((abs(self.getSuitConditionModifier(attack[TOON_TGT_COL], 'dodgy') - 100.0) / 100.0), acc))

        if randChoice < acc:
            if debug:
                self.notify.debug('HIT: Toon attack rolled' + str(randChoice) + 'to hit with an accuracy of' + str(acc))
            attack[TOON_ACCBONUS_COL] = 0
        else:
            if debug:
                self.notify.debug('MISS: Toon attack rolled' + str(randChoice) + 'to hit with an accuracy of' + str(acc))
            attack[TOON_ACCBONUS_COL] = 1
        return (not attack[TOON_ACCBONUS_COL], atkAccResult)

    def __toonTrackExp(self, toonId, track):
        toon = self.battle.getToon(toonId)
        if toon != None:
            toonExpLvl = toon.experience.getExpLevel(track)
            exp = AttackExpPerTrack[toonExpLvl]
            if track == HEAL:
                exp = exp * 0.5
            self.notify.debug('Toon track exp: ' + str(toonExpLvl) + ' and resulting acc bonus: ' + str(exp))
            return exp
        else:
            return 0

    def __toonCheckGagBonus(self, toonId, track, level):
        toon = self.battle.getToon(toonId)
        if toon != None:
            return toon.checkGagBonus(track, level)
        else:
            return False

    def __checkPropBonus(self, track):
        result = False
        if self.battle.getInteractivePropTrackBonus() == track:
            result = True
        return result

    def __targetDefense(self, suit, atkTrack):
        if atkTrack == HEAL:
            return 0
        if suit.getElite():
            boost = 0
        else:
            boost = 0
        suitAttr = SuitBattleGlobals.SuitAttributes.get(suit.dna.name)
        suitDef = SuitBattleGlobals.calculateDefense(suitAttr['level'], suit.getLevel(), boost = boost)
        return -suitDef

    def __createToonTargetList(self, attackIndex):
        attack = self.battle.toonAttacks[attackIndex]
        atkTrack, atkLevel = self.__getActualTrackLevel(attack)
        targetList = []
        if atkTrack == NPCSOS:
            return targetList
        if not attackAffectsGroup(atkTrack, atkLevel, attack[TOON_TRACK_COL]):
            if atkTrack == HEAL:
                target = attack[TOON_TGT_COL]
            else:
                target = self.battle.findSuit(attack[TOON_TGT_COL])
            if target != None:
                targetList.append(target)
        elif atkTrack == HEAL or atkTrack == PETSOS:
            if attack[TOON_TRACK_COL] == NPCSOS or atkTrack == PETSOS:
                targetList = self.battle.activeToons
            else:
                for currToon in self.battle.activeToons:
                    if attack[TOON_ID_COL] != currToon:
                        targetList.append(currToon)

        else:
            targetList = self.battle.activeSuits
        return targetList

    def __prevAtkTrack(self, attackerId, toon = 1):
        if toon:
            prevAtkIdx = self.toonAtkOrder.index(attackerId) - 1
            if prevAtkIdx >= 0:
                prevAttackerId = self.toonAtkOrder[prevAtkIdx]
                attack = self.battle.toonAttacks[prevAttackerId]
                return self.__getActualTrack(attack)
            else:
                return NO_ATTACK

    def getSuitTrapType(self, suitId):
        if suitId in self.traps:
            if self.traps[suitId][0] == TRAP_CONFLICT:
                return NO_TRAP
            else:
                return self.traps[suitId][0]
        else:
            return NO_TRAP

    def __suitTrapDamage(self, suitId):
        if suitId in self.traps:
            return self.traps[suitId][2]
        else:
            return 0

    def addTrainTrapForJoiningSuit(self, suitId):
        self.notify.debug('addTrainTrapForJoiningSuit suit=%d self.traps=%s' % (suitId, self.traps))
        trapInfoToUse = None
        for trapInfo in self.traps.values():
            if trapInfo[0] == UBER_GAG_LEVEL_INDEX:
                trapInfoToUse = trapInfo
                break

        if trapInfoToUse:
            self.traps[suitId] = trapInfoToUse
        else:
            self.notify.warning('huh we did not find a train trap?')

    def __addSuitGroupTrap(self, suitId, trapLvl, attackerId, allSuits, npcDamage = 0):
        if npcDamage == 0:
            if suitId in self.traps:
                if self.traps[suitId][0] == TRAP_CONFLICT:
                    pass
                else:
                    self.traps[suitId][0] = TRAP_CONFLICT
                for suit in allSuits:
                    id = suit.doId
                    if id in self.traps:
                        self.traps[id][0] = TRAP_CONFLICT
                    else:
                        self.traps[id] = [TRAP_CONFLICT, 0, 0]

            else:
                toon = self.battle.getToon(attackerId)
                organicBonus = toon.checkGagBonus(TRAP, trapLvl)
                propBonus = self.__checkPropBonus(TRAP)
                suit = self.battle.findSuit(suitId)
                if self.toonHasCondition(toon.doId, 'nolevel8s') and atkLevel == 7:
                    self.setToonCondition(toon.doId, 'banned', 1, 1, 'setBoth')
                if self.toonHasCondition(toon.doId, 'nolevel7s') and atkLevel == 6:
                    self.setToonCondition(toon.doId, 'banned', 1, 1, 'setBoth')
                if self.toonHasCondition(toon.doId, 'nolevel6s') and atkLevel == 5:
                    self.setToonCondition(toon.doId, 'banned', 1, 1, 'setBoth')
                if self.toonHasCondition(toon.doId, 'nolevel5s') and atkLevel == 4:
                    self.setToonCondition(toon.doId, 'banned', 1, 1, 'setBoth')
                if self.toonHasCondition(toon.doId, 'nolevel4s') and atkLevel == 3:
                    self.setToonCondition(toon.doId, 'banned', 1, 1, 'setBoth')
                if self.toonHasCondition(toon.doId, 'noTrapGags'):
                    self.setToonCondition(toon.doId, 'banned2', 1, 1, 'setBoth')
                if self.toonHasCondition(toon.doId, 'noGags'):
                    self.setToonCondition(toon.doId, 'banned3', 1, 1, 'setBoth')
                if suit.dna.name == 'fbd' and self.suitHasCondition(suitId, 'bookkeeping'):
                    self.setToonCondition(toon.doId, 'bookkeepingtoon', 1, 5, 'setBoth')
                if organicBonus:
                    damage = (getTrapDamage(trapLvl, toon, suit) * 1.2)
                    self.setSuitCondition(suitId, 'dazed2', 1, 10, 'setBoth')
                else:
                    damage = getTrapDamage(trapLvl, toon, suit)
                    self.setSuitCondition(suitId, 'dazed2', 1, 10, 'setBoth')
                if self.suitHasCondition(suitId, 'immune'):
                    damage *= 0
                elif self.suitHasCondition(suitId, 'HRdamagereduction'):
                    damage *= 0.1
                elif self.toonHasCondition(attackerId, 'trapBoost'):
                    damage *= (1.0 + self.getToonConditionModifier(attackerId, 'trapBoost') * 0.01)
                elif self.toonHasCondition(attackerId, 'allGagBoost'):
                    damage *= (1.0 + self.getToonConditionModifier(attackerId, 'allGagBoost') * 0.01)
                elif self.toonHasCondition(attackerId, 'encore'):
                    damage *= 1.16
                elif self.toonHasCondition(attackerId, 'encore2'):
                    damage *= 1.08
                target = self.battle.findSuit(suitId)
                for s in self.battle.activeSuits:
                    if s.dna.name == 'scg':
                        target2 = s
                        if target2.dna.name == 'scg' and self.suitHasCondition(target2.doId,
                                                                               'shielding') and not suit.dna.name == 'scg':
                            damage *= .7
                            target2.setHP(target2.currHP - (int(damage * .425)))
                            if target2.getHP() <= 0:
                                self.__removeLured(target2.doId)
                                if target2.getSkeleRevives() >= 1:
                                    target2.useSkeleRevive()
                    elif s.dna.name == 'cp':
                        target2 = s
                        if target2.dna.name == 'cp' and self.suitHasCondition(target2.doId,
                                                                              'shielding') and not suit.dna.name == 'cp':
                            damage *= .7
                            target2.setHP(target2.currHP - (int(damage * .425)))
                            if target2.getHP() <= 0:
                                self.__removeLured(target2.doId)
                                if target2.getSkeleRevives() >= 1:
                                    target2.useSkeleRevive()
                    elif s.dna.name == 'blr':
                        target2 = s
                        if target2.dna.name == 'blr' and self.suitHasCondition(target2.doId,
                                                                              'shielding') and not suit.dna.name == 'blr':
                            damage *= .7
                            target2.setHP(target2.currHP - (int(damage * .425)))
                            if target2.getHP() <= 0:
                                self.__removeLured(target2.doId)
                                if target2.getSkeleRevives() >= 1:
                                    target2.useSkeleRevive()
                    elif s.dna.name == 'cry':
                        target2 = s
                        if target2.dna.name == 'cry' and self.suitHasCondition(target2.doId,
                                                                              'shielding') and not suit.dna.name == 'cry':
                            damage *= .7
                            target2.setHP(target2.currHP - (int(damage * .425)))
                            if target2.getHP() <= 0:
                                self.__removeLured(target2.doId)
                                if target2.getSkeleRevives() >= 1:
                                    target2.useSkeleRevive()
                    elif s.dna.name == 'dsf':
                        target2 = s
                        if target2.dna.name == 'dsf' and self.suitHasCondition(target2.doId,
                                                                               'absorbingHR') and not suit.dna.name == 'dsf':
                            damage *= .9
                            target2.setHP(target2.currHP - (int(damage * .115)))
                            if target2.getHP() <= 0:
                                self.__removeLured(target2.doId)
                                if target2.getSkeleRevives() >= 1:
                                    target2.useSkeleRevive()
                if self.itemIsCredit(TRAP, trapLvl):
                    self.traps[suitId] = [trapLvl, attackerId, damage]
                else:
                    self.traps[suitId] = [trapLvl, 0, damage]
                self.__addLuredSuitsDelayed(attackerId, targetId=-1, ignoreDamageCheck=True)
        else:
            if suitId in self.traps:
                if self.traps[suitId][0] == self.TRAP_CONFLICT:
                    self.traps[suitId] = [
                        trapLvl, 0, npcDamage]
            else:
                if not self.__suitIsLured(suitId):
                    self.traps[suitId] = [
                        trapLvl, 0, npcDamage]

    def __addSuitTrap(self, suitId, trapLvl, attackerId, npcDamage=0):
        if npcDamage == 0:
            if suitId in self.traps:
                if self.traps[suitId][0] == self.TRAP_CONFLICT:
                    pass
                else:
                    self.traps[suitId][0] = self.TRAP_CONFLICT
            else:
                attack = self.battle.toonAttacks[attackerId]
                atkTrack, atkLevel, atkHp = self.__getActualTrackLevelHp(attack)
                toon = self.battle.getToon(attackerId)
                suit = self.battle.findSuit(suitId)
                organicBonus = toon.checkGagBonus(TRAP, trapLvl)
                if self.toonHasCondition(toon.doId, 'nolevel8s') and atkLevel == 7:
                    self.setToonCondition(toon.doId, 'banned', 1, 1, 'setBoth')
                if self.toonHasCondition(toon.doId, 'nolevel7s') and atkLevel == 6:
                    self.setToonCondition(toon.doId, 'banned', 1, 1, 'setBoth')
                if self.toonHasCondition(toon.doId, 'nolevel6s') and atkLevel == 5:
                    self.setToonCondition(toon.doId, 'banned', 1, 1, 'setBoth')
                if self.toonHasCondition(toon.doId, 'nolevel5s') and atkLevel == 4:
                    self.setToonCondition(toon.doId, 'banned', 1, 1, 'setBoth')
                if self.toonHasCondition(toon.doId, 'nolevel4s') and atkLevel == 3:
                    self.setToonCondition(toon.doId, 'banned', 1, 1, 'setBoth')
                if self.toonHasCondition(toon.doId, 'noTrapGags'):
                    self.setToonCondition(toon.doId, 'banned2', 1, 1, 'setBoth')
                if self.toonHasCondition(toon.doId, 'noGags'):
                    self.setToonCondition(toon.doId, 'banned3', 1, 1, 'setBoth')
                if suit.dna.name == 'fbd' and self.suitHasCondition(suitId, 'bookkeeping'):
                    self.setToonCondition(toon.doId, 'bookkeepingtoon', 1, 5, 'setBoth')
                if organicBonus:
                    damage = (getTrapDamage(trapLvl, toon, suit) * 1.2)
                    self.setSuitCondition(suitId, 'dazed2', 1, 10, 'setBoth')
                else:
                    damage = getTrapDamage(trapLvl, toon, suit)
                    self.setSuitCondition(suitId, 'dazed2', 1, 10, 'setBoth')
                if self.suitHasCondition(suitId, 'immune'):
                    damage *= 0
                elif self.suitHasCondition(suitId, 'HRdamagereduction'):
                    damage *= 0.1
                elif self.toonHasCondition(attackerId, 'trapBoost'):
                    damage *= (1.0 + self.getToonConditionModifier(attackerId, 'trapBoost') * 0.01)
                elif self.toonHasCondition(attackerId, 'allGagBoost'):
                    damage *= (1.0 + self.getToonConditionModifier(attackerId, 'allGagBoost') * 0.01)
                elif self.toonHasCondition(attackerId, 'encore'):
                    damage *= 1.16
                elif self.toonHasCondition(attackerId, 'encore2'):
                    damage *= 1.08
                target = self.battle.findSuit(suitId)
                for s in self.battle.activeSuits:
                    if s.dna.name == 'scg':
                        target2 = s
                        if target2.dna.name == 'scg' and self.suitHasCondition(target2.doId,
                                                                               'shielding') and not suit.dna.name == 'scg':
                            damage *= .7
                            target2.setHP(target2.currHP - (int(damage * .425)))
                            if target2.getHP() <= 0:
                                self.__removeLured(target2.doId)
                                if target2.getSkeleRevives() >= 1:
                                    target2.useSkeleRevive()
                    elif s.dna.name == 'cp':
                        target2 = s
                        if target2.dna.name == 'cp' and self.suitHasCondition(target2.doId,
                                                                              'shielding') and not suit.dna.name == 'cp':
                            damage *= .7
                            target2.setHP(target2.currHP - (int(damage * .425)))
                            if target2.getHP() <= 0:
                                self.__removeLured(target2.doId)
                                if target2.getSkeleRevives() >= 1:
                                    target2.useSkeleRevive()
                    elif s.dna.name == 'cry':
                        target2 = s
                        if target2.dna.name == 'cry' and self.suitHasCondition(target2.doId,
                                                                              'shielding') and not suit.dna.name == 'cry':
                            damage *= .7
                            target2.setHP(target2.currHP - (int(damage * .425)))
                            if target2.getHP() <= 0:
                                self.__removeLured(target2.doId)
                                if target2.getSkeleRevives() >= 1:
                                    target2.useSkeleRevive()
                    elif s.dna.name == 'dsf':
                        target2 = s
                        if target2.dna.name == 'dsf' and self.suitHasCondition(target2.doId,
                                                                               'absorbingHR') and not suit.dna.name == 'dsf':
                            damage *= .9
                            target2.setHP(target2.currHP - (int(damage * .115)))
                            if target2.getHP() <= 0:
                                self.__removeLured(target2.doId)
                                if target2.getSkeleRevives() >= 1:
                                    target2.useSkeleRevive()
                    elif s.dna.name == 'blr':
                        target2 = s
                        if target2.dna.name == 'blr' and self.suitHasCondition(target2.doId,
                                                                              'shielding') and not suit.dna.name == 'blr':
                            damage *= .7
                            target2.setHP(target2.currHP - (int(damage * .425)))
                            if target2.getHP() <= 0:
                                self.__removeLured(target2.doId)
                                if target2.getSkeleRevives() >= 1:
                                    target2.useSkeleRevive()
                if self.itemIsCredit(TRAP, trapLvl):
                    self.traps[suitId] = [
                        trapLvl, attackerId, damage]
                else:
                    self.traps[suitId] = [trapLvl, 0, damage]
        else:
            if suitId in self.traps:
                if self.traps[suitId][0] == self.TRAP_CONFLICT:
                    self.traps[suitId] = [
                        trapLvl, 0, npcDamage]
            else:
                if not self.__suitIsLured(suitId):
                    self.traps[suitId] = [
                        trapLvl, 0, npcDamage]

    def __removeSuitTrap(self, suitId):
        if suitId in self.traps:
            del self.traps[suitId]

    def __clearTrapCreator(self, creatorId, suitId = None):
        if suitId == None:
            for currTrap in self.traps.keys():
                if creatorId == self.traps[currTrap][1]:
                    self.traps[currTrap][1] = 0

        elif suitId in self.traps:
            self.traps[suitId][1] = 0

    def __trapCreator(self, suitId):
        if suitId in self.traps:
            return self.traps[suitId][1]
        else:
            return 0

    def __initTraps(self):
        self.trainTrapTriggered = False
        keysList = self.traps.keys()
        for currTrap in keysList:
            if self.traps[currTrap][0] == TRAP_CONFLICT:
                del self.traps[currTrap]

    def __calcToonAtkHp(self, toonId):
        attack = self.battle.toonAttacks[toonId]
        targetList = self.__createToonTargetList(toonId)
        atkHit, atkAcc = self.__calcToonAtkHit(toonId, targetList)
        atkTrack, atkLevel, atkHp = self.__getActualTrackLevelHp(attack)
        if not atkHit and atkTrack != HEAL:
            return
        validTargetAvail = 0
        lureDidDamage = 0
        currLureId = -1
        for currTarget in xrange(len(targetList)):
            attackLevel = -1
            attackTrack = None
            attackDamage = 0
            toonTarget = 0
            targetLured = 0
            if atkTrack == HEAL or atkTrack == PETSOS:
                targetId = targetList[currTarget]
                toonTarget = 1
            else:
                targetId = targetList[currTarget].getDoId()
            if atkTrack == LURE:
                self.currentlyImmuneSuits = self.getImmuneSuits()
                if targetId not in self.currentlyImmuneSuits:
                    if self.getSuitTrapType(targetId) == NO_TRAP:
                        if self.notify.getDebug():
                            self.notify.debug('Suit lured, but no trap exists')
                        if self.SUITS_UNLURED_IMMEDIATELY:
                            if not self.__suitIsLured(targetId, prevRound=1):
                                if not self.__combatantDead(targetId, toon=toonTarget):
                                    validTargetAvail = 1
                                rounds = self.NumRoundsLured[atkLevel]
                                chance = ToontownBattleGlobals.LureMissChance[atkLevel]
                                if self.suitHasCondition(targetId, 'immune'):
                                    lureKBValue = 0
                                elif self.suitHasCondition(targetId, 'lureImmune'):
                                    lureKBValue = 0
                                elif self.suitHasCondition(targetId, 'enraged') and self.suitHasCondition(targetId, 'desperation'):
                                    lureKBValue = 0
                                elif random.randint(0, 99) <= chance and not self.suitHasCondition(targetId, 'lureImmune') and not self.suitHasCondition(targetId, 'enraged') and self.suitHasCondition(targetId, 'desperation'):
                                    self.notify.debug(
                                        'Toon attack rolled' + str(chance))
                                    lureKBValue = 0
                                else:
                                    lureKBValue = (ToontownBattleGlobals.AvLureKnockback[atkLevel] * 100)
                                # lureKBValue = (ToontownBattleGlobals.LURE_KNOCKBACK_VALUE * 100)
                                organicBonus = self.__toonCheckGagBonus(attack[TOON_ID_COL], atkTrack, atkLevel)
                                theSuit = self.battle.findSuit(targetId)
                                if organicBonus:
                                    lureKBValue *= 1.2
                                if self.toonHasCondition(toonId, 'nolevel8s') and atkLevel == 7:
                                    self.setToonCondition(toonId, 'banned', 1, 1, 'setBoth')
                                if self.toonHasCondition(toonId, 'nolevel7s') and atkLevel == 6:
                                    self.setToonCondition(toonId, 'banned', 1, 1, 'setBoth')
                                if self.toonHasCondition(toonId, 'nolevel6s') and atkLevel == 5:
                                    self.setToonCondition(toonId, 'banned', 1, 1, 'setBoth')
                                if self.toonHasCondition(toonId, 'nolevel5s') and atkLevel == 4:
                                    self.setToonCondition(toonId, 'banned', 1, 1, 'setBoth')
                                if self.toonHasCondition(toonId, 'nolevel4s') and atkLevel == 3:
                                    self.setToonCondition(toonId, 'banned', 1, 1, 'setBoth')
                                if self.toonHasCondition(toonId, 'noLureGags'):
                                    self.setToonCondition(toonId, 'banned2', 1, 1, 'setBoth')
                                if self.toonHasCondition(toonId, 'noGags'):
                                    self.setToonCondition(toonId, 'banned3', 1, 1, 'setBoth')
                                if self.toonHasCondition(toonId, 'lureBoost'):
                                    lureKBValue += self.getToonConditionModifier(toonId, 'lureBoost')
                                if self.toonHasCondition(toonId, 'encore'):
                                    lureKBValue *= 1.16
                                if self.toonHasCondition(toonId, 'encore2'):
                                    lureKBValue *= 1.08
                                if theSuit.dna.name == 'fbd' and self.suitHasCondition(targetId, 'bookkeeping'):
                                    self.setToonCondition(toonId, 'bookkeepingtoon', 1, 5, 'setBoth')
                                if self.suitHasCondition(targetId, 'immune'):
                                    self.setSuitCondition(targetId, 'lured', 0,
                                                          0,
                                                          'setBoth')
                                elif self.suitHasCondition(targetId, 'lureImmune'):
                                    self.setSuitCondition(targetId, 'lured', 0,
                                                          0,
                                                          'setBoth')
                                elif self.suitHasCondition(targetId, 'enraged') and self.suitHasCondition(targetId, 'desperation'):
                                    self.setSuitCondition(targetId, 'lured', 0,
                                                          0,
                                                          'setBoth')
                                elif theSuit.isSkeleton:
                                    self.setSuitCondition(targetId, 'lured', lureKBValue,
                                                          self.NumRoundsLured[atkLevel],
                                                          'setBoth')
                                else:
                                    self.setSuitCondition(targetId, 'lured', lureKBValue, self.NumRoundsLured[atkLevel] + 1,
                                                      'setBoth')
                                wakeupChance = 100 - atkAcc * 2
                                npcLurer = attack[TOON_TRACK_COL] == NPCSOS
                                currLureId = self.__addLuredSuitInfo(targetId, -1, rounds, wakeupChance, toonId,
                                                                     atkLevel,
                                                                     lureId=currLureId, npc=npcLurer)
                                if self.notify.getDebug():
                                    self.notify.debug('Suit lured for ' + str(rounds) + ' rounds max with ' + str(
                                        wakeupChance) + '% chance to wake up each round')
                                if self.suitHasCondition(currTarget, 'immune'):
                                    targetLured = 0
                                elif self.suitHasCondition(currTarget, 'lureImmune'):
                                    targetLured = 0
                                elif self.suitHasCondition(currTarget, 'enraged') and self.suitHasCondition(currTarget, 'desperation'):
                                    targetLured = 0
                                else:
                                    targetLured = 1
                    else:
                        attackTrack = TRAP
                        if targetId in self.traps:
                            trapInfo = self.traps[targetId]
                            attackLevel = trapInfo[0]
                        else:
                            attackLevel = NO_TRAP
                        attackDamage = self.__suitTrapDamage(targetId)
                        trapCreatorId = self.__trapCreator(targetId)
                        if trapCreatorId > 0:
                            self.notify.debug('Giving trap EXP to toon ' + str(trapCreatorId))
                            self.__addAttackExp(attack, track=TRAP, level=attackLevel, attackerId=trapCreatorId)
                        self.__clearTrapCreator(trapCreatorId, targetId)
                        lureDidDamage = 1
                        if self.notify.getDebug():
                            self.notify.debug(
                                'Suit lured right onto a trap! (' + str(AvProps[attackTrack][attackLevel]) + ',' + str(
                                    attackLevel) + ')')
                        if not self.__combatantDead(targetId, toon=toonTarget):
                            if self.suitHasCondition(targetId, 'immune'):
                                validTargetAvail = 0
                            elif self.suitHasCondition(currTarget, 'lureImmune'):
                                validTargetAvail = 0
                            elif self.suitHasCondition(currTarget, 'enraged') and self.suitHasCondition(currTarget, 'desperation'):
                                validTargetAvail = 0
                            else:
                                validTargetAvail = 1
                        targetLured = 1
                if not self.SUITS_UNLURED_IMMEDIATELY:
                    if not self.__suitIsLured(targetId, prevRound=1):
                        if not self.__combatantDead(targetId, toon=toonTarget):
                            if self.suitHasCondition(targetId, 'immune'):
                                validTargetAvail = 0
                            elif self.suitHasCondition(currTarget, 'lureImmune'):
                                validTargetAvail = 0
                            elif self.suitHasCondition(currTarget, 'enraged') and self.suitHasCondition(currTarget, 'desperation'):
                                validTargetAvail = 0
                            else:
                                validTargetAvail = 1
                        rounds = self.NumRoundsLured[atkLevel]
                        wakeupChance = 100 - atkAcc * 2
                        npcLurer = attack[TOON_TRACK_COL] == NPCSOS
                        currLureId = self.__addLuredSuitInfo(targetId, -1, rounds, wakeupChance, toonId, atkLevel,
                                                                 lureId=currLureId, npc=npcLurer)
                        if self.notify.getDebug():
                            self.notify.debug('Suit lured for ' + str(rounds) + ' rounds max with ' + str(
                                wakeupChance) + '% chance to wake up each round')
                        targetLured = 1
                    if attackLevel != -1:
                        self.__addLuredSuitsDelayed(toonId, targetId)
                if targetLured and (targetId not in self.successfulLures or targetId in self.successfulLures and
                                    self.successfulLures[targetId][1] < atkLevel):
                    self.notify.debug('Adding target ' + str(targetId) + ' to successfulLures list')
                    self.successfulLures[targetId] = [
                        toonId, atkLevel, atkAcc, -1]
            else:
                if atkTrack == TRAP:
                    npcDamage = 0
                    if attack[TOON_TRACK_COL] == NPCSOS:
                        npcDamage = atkHp
                    if self.CLEAR_MULTIPLE_TRAPS:
                        if self.getSuitTrapType(targetId) != NO_TRAP:
                            self.__clearAttack(toonId)
                            return
                    else:
                        self.__addSuitTrap(targetId, atkLevel, toonId, npcDamage)
                elif self.__suitIsLured(targetId) and atkTrack == SOUND:
                    tgtPos = self.battle.activeSuits.index(targetList[currTarget])
                    attack[TOON_KBBONUS_COL][tgtPos] = self.KBBONUS_LURED_FLAG
                attackLevel = atkLevel
                attackTrack = atkTrack
                toon = self.battle.getToon(toonId)
                if attack[TOON_TRACK_COL] == NPCSOS and lureDidDamage != 1 or attack[TOON_TRACK_COL] == PETSOS:
                    attackDamage = atkHp
                elif atkTrack == FIRE:
                    suit = self.battle.findSuit(targetId)
                    if suit:
                        if suit.getManager():
                            attackDamage = 0
                        elif suit.currHP > (suit.maxHP * 1.5):
                            attackDamage = 0
                        elif self.suitHasCondition(targetId, 'insured'):
                            attackDamage = 0
                        else:
                            costToFire = 1
                            abilityToFire = toon.getPinkSlips()
                            toon.removePinkSlips(costToFire)
                            if costToFire > abilityToFire:
                                commentStr = 'Toon attempting to fire a %s cost cog with %s pinkslips' % (
                                costToFire, abilityToFire)
                                simbase.air.writeServerEvent('suspicious', toonId, commentStr)
                                dislId = toon.DISLid
                                simbase.air.banManager.ban(toonId, dislId, commentStr)
                                print
                                'Not enough PinkSlips to fire cog - print a warning here'
                            else:
                                suit.skeleRevives = 0
                                attackDamage = suit.getHP()
                    else:
                        attackDamage = 0
                    self.setToonCondition(toon.doId, 'noSOS', 1, 3, 'setBoth')
                    self.setToonCondition(toon.doId, 'noFires', 1, 3, 'setBoth')
                    self.setToonCondition(toon.doId, 'noUnites', 1, 3, 'setBoth')
                    bonus = 0
                elif atkTrack == HEAL:
                    if self.toonHasCondition(toon.doId, 'nolevel8s') and attackLevel == 7:
                        self.setToonCondition(toon.doId, 'banned', 1, 1, 'setBoth')
                    if self.toonHasCondition(toon.doId, 'nolevel7s') and attackLevel == 6:
                        self.setToonCondition(toon.doId, 'banned', 1, 1, 'setBoth')
                    if self.toonHasCondition(toon.doId, 'nolevel6s') and attackLevel == 5:
                        self.setToonCondition(toon.doId, 'banned', 1, 1, 'setBoth')
                    if self.toonHasCondition(toon.doId, 'nolevel5s') and attackLevel == 4:
                        self.setToonCondition(toon.doId, 'banned', 1, 1, 'setBoth')
                    if self.toonHasCondition(toon.doId, 'nolevel4s') and attackLevel == 3:
                        self.setToonCondition(toon.doId, 'banned', 1, 1, 'setBoth')
                    if self.toonHasCondition(toon.doId, 'noToonUpGags'):
                        self.setToonCondition(toon.doId, 'banned2', 1, 1, 'setBoth')
                    if self.toonHasCondition(toon.doId, 'noGags'):
                        self.setToonCondition(toon.doId, 'banned3', 1, 1, 'setBoth')
                    attackDamage = getAvPropDamage(attackTrack, attackLevel, toon.experience.getExp(attackTrack))
                    organicBonus = self.__toonCheckGagBonus(attack[TOON_ID_COL], atkTrack, atkLevel)
                    if organicBonus:
                        self.setToonCondition(targetId, 'cheer', 1, 2, 'setBoth')
                    else:
                        self.setToonCondition(targetId, 'cheer', 1, 1, 'setBoth')
                    if self.toonHasCondition(toonId, 'healBoost'):
                        attackDamage *= (1.0 + self.getToonConditionModifier(toonId, 'healBoost') * 0.01)
                    if self.toonHasCondition(toonId, 'encore'):
                        attackDamage *= 1.16
                    if self.toonHasCondition(toonId, 'encore2'):
                        attackDamage *= 1.16
                elif atkTrack == SQUIRT:
                    if self.toonHasCondition(toon.doId, 'nolevel8s') and attackLevel == 7:
                        self.setToonCondition(toon.doId, 'banned', 1, 1, 'setBoth')
                    if self.toonHasCondition(toon.doId, 'nolevel7s') and attackLevel == 6:
                        self.setToonCondition(toon.doId, 'banned', 1, 1, 'setBoth')
                    if self.toonHasCondition(toon.doId, 'nolevel6s') and attackLevel == 5:
                        self.setToonCondition(toon.doId, 'banned', 1, 1, 'setBoth')
                    if self.toonHasCondition(toon.doId, 'nolevel5s') and attackLevel == 4:
                        self.setToonCondition(toon.doId, 'banned', 1, 1, 'setBoth')
                    if self.toonHasCondition(toon.doId, 'nolevel4s') and attackLevel == 3:
                        self.setToonCondition(toon.doId, 'banned', 1, 1, 'setBoth')
                    if self.toonHasCondition(toon.doId, 'noSquirtGags'):
                        self.setToonCondition(toon.doId, 'banned2', 1, 1, 'setBoth')
                    if self.toonHasCondition(toon.doId, 'noSquirtGags'):
                        self.setToonCondition(toon.doId, 'banned3', 1, 1, 'setBoth')
                    attackDamage = getAvPropDamage(attackTrack, attackLevel, toon.experience.getExp(attackTrack))
                    suit = self.battle.findSuit(targetId)
                    target = self.battle.findSuit(attack[TOON_TGT_COL])
                    activeSuits = self.battle.activeSuits
                    suitIndex = activeSuits.index(target)
                    if self.suitHasCondition(targetId, 'vulnerable') and self.suitHasCondition(targetId, 'marked'):
                        attackDamage *= (1.25 + (self.getSuitConditionModifier(targetId, 'marked') * 0.1))
                    elif self.suitHasCondition(targetId, 'enraged') and self.suitHasCondition(targetId, 'desperation') and self.suitHasCondition(targetId, 'marked'):
                        attackDamage *= (1 + (self.getSuitConditionModifier(targetId, 'marked') * 0.1))
                    elif self.suitHasCondition(targetId, 'enraged') and self.suitHasCondition(targetId, 'marked'):
                        attackDamage *= (0.7 + (self.getSuitConditionModifier(targetId, 'marked') * 0.1))
                    elif self.suitHasCondition(targetId, 'damageReduction') and self.suitHasCondition(targetId, 'marked'):
                        attackDamage *= (0.5 + (self.getSuitConditionModifier(targetId, 'marked') * 0.1))
                    elif self.suitHasCondition(targetId, 'marked'):
                        attackDamage *= (1 + (self.getSuitConditionModifier(targetId, 'marked') * 0.1))
                    elif self.suitHasCondition(targetId, 'enraged') and self.suitHasCondition(targetId, 'desperation'):
                        attackDamage *= 1
                    elif self.suitHasCondition(targetId, 'enraged'):
                        attackDamage *= 0.7
                    elif self.suitHasCondition(targetId, 'soakImmune') and self.suitHasCondition(targetId, 'soaked'):
                        attackDamage *= 0.4
                    elif self.suitHasCondition(targetId, 'damageReduction'):
                        attackDamage *= 0.5
                    elif self.suitHasCondition(targetId, 'vulnerable'):
                        attackDamage *= 1.25
                    elif self.toonHasCondition(toonId, 'squirtBoost'):
                        attackDamage *= (1.0 + self.getToonConditionModifier(toonId, 'squirtBoost') * 0.01)
                    elif self.toonHasCondition(toonId, 'encore'):
                        attackDamage *= 1.16
                    elif self.toonHasCondition(toonId, 'encore2'):
                        attackDamage *= 1.08
                    elif self.toonHasCondition(toonId,
                                               'allGagBoost'):
                        attackDamage *= (1.0 + (self.getToonConditionModifier(toonId, 'allGagBoost') * 0.01))
                        attackDamage = math.ceil(attackDamage)
                    elif self.suitHasCondition(targetId, 'HRdamagereduction'):
                        attackDamage *= 0.1
                    for s in self.battle.activeSuits:
                        if s.dna.name == 'scg':
                            target2 = s
                            if target2.dna.name == 'scg' and self.suitHasCondition(target2.doId, 'shielding') and not target.dna.name == 'scg':
                                attackDamage *= .7
                                target2.setHP(target2.currHP - (int(attackDamage * .425)))
                                if target2.getHP() <= 0:
                                    self.__removeLured(target2.doId)
                                    if target2.getSkeleRevives() >= 1:
                                        target2.useSkeleRevive()
                        elif s.dna.name == 'cp':
                            target2 = s
                            if target2.dna.name == 'cp' and self.suitHasCondition(target2.doId, 'shielding') and not target.dna.name == 'cp':
                                attackDamage *= .7
                                target2.setHP(target2.currHP - (int(attackDamage * .425)))
                                if target2.getHP() <= 0:
                                    self.__removeLured(target2.doId)
                                    if target2.getSkeleRevives() >= 1:
                                        target2.useSkeleRevive()
                        elif s.dna.name == 'cry':
                            target2 = s
                            if target2.dna.name == 'cry' and self.suitHasCondition(target2.doId, 'shielding') and not target.dna.name == 'cry':
                                attackDamage *= .7
                                target2.setHP(target2.currHP - (int(attackDamage * .425)))
                                if target2.getHP() <= 0:
                                    self.__removeLured(target2.doId)
                                    if target2.getSkeleRevives() >= 1:
                                        target2.useSkeleRevive()
                        elif s.dna.name == 'dsf':
                            target2 = s
                            if target2.dna.name == 'dsf' and self.suitHasCondition(target2.doId,
                                                                                   'absorbingHR') and not target.dna.name == 'dsf':
                                attackDamage *= .9
                                target2.setHP(target2.currHP - (int(attackDamage * .115)))
                                if target2.getHP() <= 0:
                                    self.__removeLured(target2.doId)
                                    if target2.getSkeleRevives() >= 1:
                                        target2.useSkeleRevive()
                        elif s.dna.name == 'blr':
                            target9 = s
                            if target9.dna.name == 'blr' and self.suitHasCondition(target9.doId, 'shielding') and not target.dna.name == 'blr':
                                target9.setHP(target9.currHP - (int(attackDamage * .425)))
                                if target9.getHP() <= 0:
                                    self.__removeLured(target9.doId)
                                    if target9.getSkeleRevives() >= 1:
                                        target9.useSkeleRevive()
                    if suitIndex - 1 >= 0:
                        target2 = activeSuits[suitIndex - 1]
                        if not self.suitHasCondition(target2.doId, 'immune'):
                            if target2.dna.name == 'tcm':
                                self.setSuitCondition(target2.doId, 'soakedcalculator', 1, 10, 'setBoth')
                            if target2.dna.name == 'dvk':
                                self.setSuitCondition(target2.doId, 'soakedcalculator', 1, 10, 'setBoth')
                            if target2.dna.name == 'lit' and not self.suitHasCondition(target2.doId, 'soaked'):
                                self.setSuitCondition(target2.doId, 'soakedcalculator', 1, 10, 'setBoth')
                                self.setSuitCondition(target2.doId, 'soakedcalculator2', 0, 0, 'setBoth')
                            if target2.dna.name == 'fbd' and self.suitHasCondition(target2.doId, 'bookkeeping'):
                                self.setToonCondition(toon.doId, 'bookkeepingtoon', 1, 5, 'setBoth')
                                self.setSuitCondition(target2.doId, 'soakedcalculator', 1, 10, 'setBoth')
                                self.setSuitCondition(target2.doId, 'soakedcalculator2', 0, 0, 'setBoth')
                            if target2.dna.name == 'fbd':
                                self.setSuitCondition(target2.doId, 'soakedcalculator', 1, 10, 'setBoth')
                                self.setSuitCondition(target2.doId, 'soakedcalculator2', 0, 0, 'setBoth')
                            if target2.dna.name == 'cp':
                                self.setSuitCondition(target2.doId, 'soakedcalculator', 1, 10, 'setBoth')
                                self.setSuitCondition(target2.doId, 'soakedcalculator2', 0, 0, 'setBoth')
                            if target2.dna.name == 'dvp':
                                self.setSuitCondition(target2.doId, 'soakedcalculator', 1, 10, 'setBoth')
                                self.setSuitCondition(target2.doId, 'soakedcalculator2', 0, 0, 'setBoth')
                            if target2.dna.name == 'blr':
                                self.setSuitCondition(target2.doId, 'soakedcalculator', 1, 10, 'setBoth')
                                self.setSuitCondition(target2.doId, 'soakedcalculator2', 0, 0, 'setBoth')
                            self.setSuitCondition(target2.doId, 'soaked', 1, self.NumRoundsSoaked[attackLevel],
                                                      'alternateBoth')
                            organicBonus = self.__toonCheckGagBonus(attack[TOON_ID_COL], atkTrack, atkLevel)
                            if organicBonus:
                                target2.setHP(target2.currHP - int(attackDamage / 2))
                                attackDamageAbsorb = (int(attackDamage / 2) * .425)
                                attackDamageAbsorbHR = (int(attackDamage / 2) * .115)
                            else:
                                target2.setHP(target2.currHP - int(attackDamage / 4))
                                attackDamageAbsorb = (int(attackDamage / 4) * .425)
                                attackDamageAbsorbHR = (int(attackDamage / 4) * .115)
                            for s in self.battle.activeSuits:
                                if s.dna.name == 'scg':
                                    target9 = s
                                    if target9.dna.name == 'scg' and self.suitHasCondition(target9.doId, 'shielding') and not target2.dna.name == 'scg':
                                        target9.setHP(target9.currHP - (int(attackDamageAbsorb)))
                                        if target9.getHP() <= 0:
                                            self.__removeLured(target9.doId)
                                            if target9.getSkeleRevives() >= 1:
                                                target9.useSkeleRevive()
                                elif s.dna.name == 'cp':
                                    target9 = s
                                    if target9.dna.name == 'cp' and self.suitHasCondition(target9.doId, 'shielding') and not target2.dna.name == 'cp':
                                        target9.setHP(target9.currHP - (int(attackDamageAbsorb)))
                                        if target9.getHP() <= 0:
                                            self.__removeLured(target9.doId)
                                            if target9.getSkeleRevives() >= 1:
                                                target9.useSkeleRevive()
                                elif s.dna.name == 'cry':
                                    target9 = s
                                    if target9.dna.name == 'cry' and self.suitHasCondition(target9.doId, 'shielding') and not target2.dna.name == 'cry':
                                        target9.setHP(target9.currHP - (int(attackDamageAbsorb)))
                                        if target9.getHP() <= 0:
                                            self.__removeLured(target9.doId)
                                            if target9.getSkeleRevives() >= 1:
                                                target9.useSkeleRevive()
                                elif s.dna.name == 'dsf':
                                    target2 = s
                                    if target2.dna.name == 'dsf' and self.suitHasCondition(target2.doId,
                                                                                           'absorbingHR') and not target2.dna.name == 'dsf':
                                        attackDamage *= .9
                                        target2.setHP(target2.currHP - (int(attackDamageAbsorbHR)))
                                        if target2.getHP() <= 0:
                                            self.__removeLured(target2.doId)
                                            if target2.getSkeleRevives() >= 1:
                                                target2.useSkeleRevive()
                                elif s.dna.name == 'blr':
                                    target9 = s
                                    if target9.dna.name == 'blr' and self.suitHasCondition(target9.doId, 'shielding') and not target2.dna.name == 'blr':
                                        target9.setHP(target9.currHP - (int(attackDamageAbsorb)))
                                        if target9.getHP() <= 0:
                                            self.__removeLured(target9.doId)
                                            if target9.getSkeleRevives() >= 1:
                                                target9.useSkeleRevive()
                            if target2.getHP() <= 0:
                                self.__removeLured(target2.doId)
                                if target2.getSkeleRevives() >= 1:
                                    target2.useSkeleRevive()
                    if suitIndex + 1 < len(activeSuits):
                        target3 = activeSuits[suitIndex + 1]
                        if not self.suitHasCondition(target3.doId, 'immune'):
                            if target3.dna.name == 'tcm':
                                self.setSuitCondition(target3.doId, 'soakedcalculator', 1, 10, 'setBoth')
                            if target3.dna.name == 'dvk':
                                self.setSuitCondition(target3.doId, 'soakedcalculator', 1, 10, 'setBoth')
                            if target3.dna.name == 'lit' and not self.suitHasCondition(target3.doId, 'soaked'):
                                self.setSuitCondition(target3.doId, 'soakedcalculator', 1, 10, 'setBoth')
                                self.setSuitCondition(target3.doId, 'soakedcalculator2', 0, 0, 'setBoth')
                            if target3.dna.name == 'fbd' and self.suitHasCondition(target3.doId, 'bookkeeping'):
                                self.setToonCondition(toon.doId, 'bookkeepingtoon', 1, 5, 'setBoth')
                                self.setSuitCondition(target3.doId, 'soakedcalculator', 1, 10, 'setBoth')
                                self.setSuitCondition(target3.doId, 'soakedcalculator2', 0, 0, 'setBoth')
                            if target3.dna.name == 'fbd':
                                self.setSuitCondition(target3.doId, 'soakedcalculator', 1, 10, 'setBoth')
                                self.setSuitCondition(target3.doId, 'soakedcalculator2', 0, 0, 'setBoth')
                            if target3.dna.name == 'cp':
                                self.setSuitCondition(target3.doId, 'soakedcalculator', 1, 10, 'setBoth')
                                self.setSuitCondition(target3.doId, 'soakedcalculator2', 0, 0, 'setBoth')
                            if target3.dna.name == 'dvp':
                                self.setSuitCondition(target3.doId, 'soakedcalculator', 1, 10, 'setBoth')
                                self.setSuitCondition(target3.doId, 'soakedcalculator2', 0, 0, 'setBoth')
                            if target3.dna.name == 'blr':
                                self.setSuitCondition(target3.doId, 'soakedcalculator', 1, 10, 'setBoth')
                                self.setSuitCondition(target3.doId, 'soakedcalculator2', 0, 0, 'setBoth')
                            self.setSuitCondition(target3.doId, 'soaked', 1, self.NumRoundsSoaked[attackLevel],
                                                      'alternateBoth')
                            organicBonus = self.__toonCheckGagBonus(attack[TOON_ID_COL], atkTrack, atkLevel)
                            if organicBonus:
                                target3.setHP(target3.currHP - int(attackDamage / 2))
                                attackDamageAbsorb = (int(attackDamage / 2) * .425)
                                attackDamageAbsorbHR = (int(attackDamage / 2) * .115)
                            else:
                                target3.setHP(target3.currHP - int(attackDamage / 4))
                                attackDamageAbsorb = (int(attackDamage / 4) * .425)
                                attackDamageAbsorbHR = (int(attackDamage / 4) * .115)
                            for s in self.battle.activeSuits:
                                if s.dna.name == 'scg':
                                    target9 = s
                                    if target9.dna.name == 'scg' and self.suitHasCondition(target9.doId, 'shielding') and not target3.dna.name == 'scg':
                                        target9.setHP(target9.currHP - (int(attackDamageAbsorb)))
                                        if target9.getHP() <= 0:
                                            self.__removeLured(target9.doId)
                                            if target9.getSkeleRevives() >= 1:
                                                target9.useSkeleRevive()
                                elif s.dna.name == 'cp':
                                    target9 = s
                                    if target9.dna.name == 'cp' and self.suitHasCondition(target9.doId, 'shielding') and not target3.dna.name == 'cp':
                                        target9.setHP(target9.currHP - (int(attackDamageAbsorb)))
                                        if target9.getHP() <= 0:
                                            self.__removeLured(target9.doId)
                                            if target9.getSkeleRevives() >= 1:
                                                target9.useSkeleRevive()
                                elif s.dna.name == 'cry':
                                    target9 = s
                                    if target9.dna.name == 'cry' and self.suitHasCondition(target9.doId, 'shielding') and not target3.dna.name == 'cry':
                                        target9.setHP(target9.currHP - (int(attackDamageAbsorb)))
                                        if target9.getHP() <= 0:
                                            self.__removeLured(target9.doId)
                                            if target9.getSkeleRevives() >= 1:
                                                target9.useSkeleRevive()
                                elif s.dna.name == 'dsf':
                                    target2 = s
                                    if target2.dna.name == 'dsf' and self.suitHasCondition(target2.doId,
                                                                                           'absorbingHR') and not target3.dna.name == 'dsf':
                                        attackDamage *= .9
                                        target2.setHP(target2.currHP - (int(attackDamageAbsorbHR)))
                                        if target2.getHP() <= 0:
                                            self.__removeLured(target2.doId)
                                            if target2.getSkeleRevives() >= 1:
                                                target2.useSkeleRevive()
                                elif s.dna.name == 'blr':
                                    target9 = s
                                    if target9.dna.name == 'blr' and self.suitHasCondition(target9.doId, 'shielding') and not target3.dna.name == 'blr':
                                        target9.setHP(target9.currHP - (int(attackDamageAbsorb)))
                                        if target9.getHP() <= 0:
                                            self.__removeLured(target9.doId)
                                            if target9.getSkeleRevives() >= 1:
                                                target9.useSkeleRevive()
                            if target3.getHP() <= 0:
                                self.__removeLured(target3.doId)
                                if target3.getSkeleRevives() >= 1:
                                    target3.useSkeleRevive()
                    if suit.dna.name == 'lit' and not self.suitHasCondition(target.doId, 'soaked'):
                        self.setSuitCondition(targetId, 'soakedcalculator', 1, 10, 'setBoth')
                        self.setSuitCondition(targetId, 'soakedcalculator2', 0, 0, 'setBoth')
                    if suit.dna.name == 'tcm':
                        self.setSuitCondition(targetId, 'soakedcalculator', 1, 10, 'setBoth')
                        self.setSuitCondition(targetId, 'soakedcalculator2', 0, 0, 'setBoth')
                    if suit.dna.name == 'fbd' and self.suitHasCondition(targetId, 'bookkeeping'):
                        self.setToonCondition(toon.doId, 'bookkeepingtoon', 1, 5, 'setBoth')
                        self.setSuitCondition(targetId, 'soakedcalculator', 1, 10, 'setBoth')
                        self.setSuitCondition(targetId, 'soakedcalculator2', 0, 0, 'setBoth')
                    if suit.dna.name == 'fbd':
                        self.setSuitCondition(targetId, 'soakedcalculator', 1, 10, 'setBoth')
                        self.setSuitCondition(targetId, 'soakedcalculator2', 0, 0, 'setBoth')
                    if suit.dna.name == 'cp':
                        self.setSuitCondition(targetId, 'soakedcalculator', 1, 10, 'setBoth')
                        self.setSuitCondition(targetId, 'soakedcalculator2', 0, 0, 'setBoth')
                    if suit.dna.name == 'blr':
                        self.setSuitCondition(targetId, 'soakedcalculator', 1, 10, 'setBoth')
                        self.setSuitCondition(targetId, 'soakedcalculator2', 0, 0, 'setBoth')
                    if suit.dna.name == 'dvk':
                        self.setSuitCondition(targetId, 'soakedcalculator', 1, 10, 'setBoth')
                    if suit.dna.name == 'dvp':
                        self.setSuitCondition(targetId, 'soakedcalculator', 1, 10, 'setBoth')
                        self.setSuitCondition(targetId, 'soakedcalculator2', 0, 0, 'setBoth')
                    self.setSuitCondition(targetId, 'soaked', 1, self.NumRoundsSoaked[attackLevel],
                                              'alternateBoth')
                elif atkTrack == THROW:
                    if self.toonHasCondition(toon.doId, 'nolevel8s') and attackLevel == 7:
                        self.setToonCondition(toon.doId, 'banned', 1, 1, 'setBoth')
                    if self.toonHasCondition(toon.doId, 'nolevel7s') and attackLevel == 6:
                        self.setToonCondition(toon.doId, 'banned', 1, 1, 'setBoth')
                    if self.toonHasCondition(toon.doId, 'nolevel6s') and attackLevel == 5:
                        self.setToonCondition(toon.doId, 'banned', 1, 1, 'setBoth')
                    if self.toonHasCondition(toon.doId, 'nolevel5s') and attackLevel == 4:
                        self.setToonCondition(toon.doId, 'banned', 1, 1, 'setBoth')
                    if self.toonHasCondition(toon.doId, 'nolevel4s') and attackLevel == 3:
                        self.setToonCondition(toon.doId, 'banned', 1, 1, 'setBoth')
                    if self.toonHasCondition(toon.doId, 'noThrowGags'):
                        self.setToonCondition(toon.doId, 'banned2', 1, 1, 'setBoth')
                    if self.toonHasCondition(toon.doId, 'noGags'):
                        self.setToonCondition(toon.doId, 'banned3', 1, 1, 'setBoth')
                    suit = self.battle.findSuit(targetId)
                    self.setSuitCondition(targetId, 'marked', 1, 1, 'setBoth')
                    if suit.dna.name == 'tcm':
                        self.setSuitCondition(targetId, 'markedcalculator', 1, 10, 'setBoth')
                    if suit.dna.name == 'fbd' and self.suitHasCondition(targetId, 'bookkeeping'):
                        self.setToonCondition(toon.doId, 'bookkeepingtoon', 1, 5, 'setBoth')
                        self.setSuitCondition(targetId, 'markedcalculator', 1, 10, 'setBoth')
                        self.setSuitCondition(targetId, 'markedcalculator2', 0, 0, 'setBoth')
                    if suit.dna.name == 'fbd':
                        self.setSuitCondition(targetId, 'markedcalculator', 1, 10, 'setBoth')
                        self.setSuitCondition(targetId, 'markedcalculator2', 0, 0, 'setBoth')
                    if suit.dna.name == 'dsk':
                        self.setSuitCondition(targetId, 'markedcalculator', 1, 10, 'setBoth')
                        self.setSuitCondition(targetId, 'markedcalculator2', 0, 0, 'setBoth')
                    attackDamage = getAvPropDamage(attackTrack, attackLevel, toon.experience.getExp(attackTrack))
                    if self.toonHasCondition(toonId, 'throwBoost'):
                        attackDamage *= (1.0 + self.getToonConditionModifier(toonId, 'throwBoost') * 0.01)
                    target = self.battle.findSuit(attack[TOON_TGT_COL])
                    for s in self.battle.activeSuits:
                        if s.dna.name == 'scg':
                            target2 = s
                            if target2.dna.name == 'scg' and self.suitHasCondition(target2.doId,
                                                                                   'shielding') and not target.dna.name == 'scg':
                                attackDamage *= .7
                                target2.setHP(target2.currHP - (int(attackDamage * .425)))
                                if target2.getHP() <= 0:
                                    self.__removeLured(target2.doId)
                                    if target2.getSkeleRevives() >= 1:
                                        target2.useSkeleRevive()
                        elif s.dna.name == 'cp':
                            target2 = s
                            if target2.dna.name == 'cp' and self.suitHasCondition(target2.doId, 'shielding') and not target.dna.name == 'cp':
                                attackDamage *= .7
                                target2.setHP(target2.currHP - (int(attackDamage * .425)))
                                if target2.getHP() <= 0:
                                    self.__removeLured(target2.doId)
                                    if target2.getSkeleRevives() >= 1:
                                        target2.useSkeleRevive()
                        elif s.dna.name == 'cry':
                            target2 = s
                            if target2.dna.name == 'cry' and self.suitHasCondition(target2.doId, 'shielding') and not target.dna.name == 'cry':
                                attackDamage *= .7
                                target2.setHP(target2.currHP - (int(attackDamage * .425)))
                                if target2.getHP() <= 0:
                                    self.__removeLured(target2.doId)
                                    if target2.getSkeleRevives() >= 1:
                                        target2.useSkeleRevive()
                        elif s.dna.name == 'dsf':
                            target2 = s
                            if target2.dna.name == 'dsf' and self.suitHasCondition(target2.doId, 'absorbingHR') and not target.dna.name == 'dsf':
                                attackDamage *= .9
                                target2.setHP(target2.currHP - (int(attackDamage * .115)))
                                if target2.getHP() <= 0:
                                    self.__removeLured(target2.doId)
                                    if target2.getSkeleRevives() >= 1:
                                        target2.useSkeleRevive()
                        elif s.dna.name == 'blr':
                            target9 = s
                            if target9.dna.name == 'blr' and self.suitHasCondition(target9.doId, 'shielding') and not target.dna.name == 'blr':
                                attackDamage *= .7
                                target9.setHP(target9.currHP - (int(attackDamage * .425)))
                                if target9.getHP() <= 0:
                                    self.__removeLured(target9.doId)
                                    if target9.getSkeleRevives() >= 1:
                                        target9.useSkeleRevive()
                elif atkTrack == SOUND:
                    suit = self.battle.findSuit(targetId)
                    if self.toonHasCondition(toon.doId, 'nolevel8s') and attackLevel == 7:
                        self.setToonCondition(toon.doId, 'banned', 1, 1, 'setBoth')
                    if self.toonHasCondition(toon.doId, 'nolevel7s') and attackLevel == 6:
                        self.setToonCondition(toon.doId, 'banned', 1, 1, 'setBoth')
                    if self.toonHasCondition(toon.doId, 'nolevel6s') and attackLevel == 5:
                        self.setToonCondition(toon.doId, 'banned', 1, 1, 'setBoth')
                    if self.toonHasCondition(toon.doId, 'nolevel5s') and attackLevel == 4:
                        self.setToonCondition(toon.doId, 'banned', 1, 1, 'setBoth')
                    if self.toonHasCondition(toon.doId, 'nolevel4s') and attackLevel == 3:
                        self.setToonCondition(toon.doId, 'banned', 1, 1, 'setBoth')
                    if self.toonHasCondition(toon.doId, 'noSoundGags'):
                        self.setToonCondition(toon.doId, 'banned2', 1, 1, 'setBoth')
                    if self.toonHasCondition(toon.doId, 'noGags'):
                        self.setToonCondition(toon.doId, 'banned3', 1, 1, 'setBoth')
                    attackDamage = getAvPropDamage(attackTrack, attackLevel, toon.experience.getExp(attackTrack))
                    if suit.dna.name == 'fbd' and self.suitHasCondition(targetId, 'bookkeeping'):
                        self.setToonCondition(toon.doId, 'bookkeepingtoon', 1, 5, 'setBoth')
                    if self.suitHasCondition(targetId, 'HRdamagereduction'):
                        attackDamage *= 0.1
                    if self.toonHasCondition(toonId, 'soundBoost'):
                        attackDamage *= (1.0 + self.getToonConditionModifier(toonId, 'soundBoost') * 0.01)
                    for s in self.battle.activeSuits:
                        if s.dna.name == 'scg':
                            target2 = s
                            if target2.dna.name == 'scg' and self.suitHasCondition(target2.doId, 'shielding'):
                                attackDamage *= .7
                                target2.setHP(target2.currHP - (int(attackDamage * .425)))
                                if target2.getHP() <= 0:
                                    self.__removeLured(target2.doId)
                                    if target2.getSkeleRevives() >= 1:
                                        target2.useSkeleRevive()
                        elif s.dna.name == 'cp':
                            target2 = s
                            if target2.dna.name == 'cp' and self.suitHasCondition(target2.doId, 'shielding'):
                                attackDamage *= .7
                                target2.setHP(target2.currHP - (int(attackDamage * .425)))
                                if target2.getHP() <= 0:
                                    self.__removeLured(target2.doId)
                                    if target2.getSkeleRevives() >= 1:
                                        target2.useSkeleRevive()
                        elif s.dna.name == 'cry':
                            target2 = s
                            if target2.dna.name == 'cry' and self.suitHasCondition(target2.doId, 'shielding'):
                                attackDamage *= .7
                                target2.setHP(target2.currHP - (int(attackDamage * .425)))
                                if target2.getHP() <= 0:
                                    self.__removeLured(target2.doId)
                                    if target2.getSkeleRevives() >= 1:
                                        target2.useSkeleRevive()
                        elif s.dna.name == 'dsf':
                            target2 = s
                            if target2.dna.name == 'dsf' and self.suitHasCondition(target2.doId,
                                                                                   'absorbingHR'):
                                attackDamage *= .9
                                target2.setHP(target2.currHP - (int(attackDamage * .115)))
                                if target2.getHP() <= 0:
                                    self.__removeLured(target2.doId)
                                    if target2.getSkeleRevives() >= 1:
                                        target2.useSkeleRevive()
                        elif s.dna.name == 'blr':
                            target9 = s
                            if target9.dna.name == 'blr' and self.suitHasCondition(target9.doId, 'shielding'):
                                attackDamage *= .7
                                target9.setHP(target9.currHP - (int(attackDamage * .425)))
                                if target9.getHP() <= 0:
                                    self.__removeLured(target9.doId)
                                    if target9.getSkeleRevives() >= 1:
                                        target9.useSkeleRevive()
                    organicBonus = self.__toonCheckGagBonus(attack[TOON_ID_COL], atkTrack, atkLevel)
                    if self.getToonConditionTurns(toonId, 'encore') == 1:
                        self.setToonCondition(toon.doId, 'winded', -50, 3, 'setBoth')
                    elif self.getToonConditionTurns(toonId, 'encore2') == 1:
                        self.setToonCondition(toon.doId, 'winded', -50, 3, 'setBoth')
                    elif not self.toonHasCondition(toon.doId, 'encore') and not self.getToonConditionTurns(toonId, 'winded') and organicBonus:
                        self.setToonCondition(toon.doId, 'encore', 16, 2, 'setBoth')
                    elif not self.toonHasCondition(toon.doId, 'encore2') and not self.getToonConditionTurns(toonId, 'winded') and not organicBonus:
                        self.setToonCondition(toon.doId, 'encore2', 8, 2, 'setBoth')
                elif atkTrack == DROP:
                    if self.toonHasCondition(toon.doId, 'nolevel8s') and attackLevel == 7:
                        self.setToonCondition(toon.doId, 'banned', 1, 1, 'setBoth')
                    if self.toonHasCondition(toon.doId, 'nolevel7s') and attackLevel == 6:
                        self.setToonCondition(toon.doId, 'banned', 1, 1, 'setBoth')
                    if self.toonHasCondition(toon.doId, 'nolevel6s') and attackLevel == 5:
                        self.setToonCondition(toon.doId, 'banned', 1, 1, 'setBoth')
                    if self.toonHasCondition(toon.doId, 'nolevel5s') and attackLevel == 4:
                        self.setToonCondition(toon.doId, 'banned', 1, 1, 'setBoth')
                    if self.toonHasCondition(toon.doId, 'nolevel4s') and attackLevel == 3:
                        self.setToonCondition(toon.doId, 'banned', 1, 1, 'setBoth')
                    if self.toonHasCondition(toon.doId, 'noDropGags'):
                        self.setToonCondition(toon.doId, 'banned2', 1, 1, 'setBoth')
                    if self.toonHasCondition(toon.doId, 'noGags'):
                        self.setToonCondition(toon.doId, 'banned3', 1, 1, 'setBoth')
                    organicBonus = self.__toonCheckGagBonus(attack[TOON_ID_COL], atkTrack, atkLevel)
                    attackDamage = getAvPropDamage(attackTrack, attackLevel, toon.experience.getExp(attackTrack))
                    if self.toonHasCondition(toonId, 'dropBoost'):
                        attackDamage *= (1.0 + self.getToonConditionModifier(toonId, 'dropBoost') * 0.01)
                    suit = self.battle.findSuit(targetId)
                    if suit.dna.name == 'tcm':
                        self.setSuitCondition(targetId, 'dropcalculator', 1, 10, 'setBoth')
                    if suit.dna.name == 'fbd' and self.suitHasCondition(targetId, 'bookkeeping'):
                        self.setToonCondition(toon.doId, 'bookkeepingtoon', 1, 5, 'setBoth')
                    if self.suitHasCondition(targetId, 'dazed') and self.suitHasCondition(targetId, 'soaked') and self.suitHasCondition(targetId, 'marked'):
                        chance = ToontownBattleGlobals.DropMissChance[atkLevel] - 35
                        if organicBonus:
                            attackDamage *= (1.15 + (self.getSuitConditionModifier(targetId, 'marked') * 0.17))
                    elif self.suitHasCondition(targetId, 'dazed') and self.suitHasCondition(targetId, 'soaked') and self.toonHasCondition(toonId, 'cheer'):
                        chance = ToontownBattleGlobals.DropMissChance[atkLevel] - 35
                        if organicBonus:
                            attackDamage *= 1.15
                    elif self.suitHasCondition(targetId, 'dazed') and self.suitHasCondition(targetId, 'soaked'):
                        chance = ToontownBattleGlobals.DropMissChance[atkLevel] - 30
                        if organicBonus:
                            attackDamage *= 1.15
                    elif self.suitHasCondition(targetId, 'soaked') and self.suitHasCondition(targetId, 'marked'):
                        chance = ToontownBattleGlobals.DropMissChance[atkLevel] - 20
                        if organicBonus:
                            attackDamage *= (1.1 + (self.getSuitConditionModifier(targetId, 'marked') * 0.15))
                    elif self.suitHasCondition(targetId, 'dazed') and self.suitHasCondition(targetId, 'marked'):
                        chance = ToontownBattleGlobals.DropMissChance[atkLevel] - 20
                        if organicBonus:
                            attackDamage *= (1.1 + (self.getSuitConditionModifier(targetId, 'marked') * 0.15))
                    elif self.toonHasCondition(toonId, 'cheer') and self.suitHasCondition(targetId, 'marked'):
                        chance = ToontownBattleGlobals.DropMissChance[atkLevel] - 10
                        if organicBonus:
                            attackDamage *= (1.1 + (self.getSuitConditionModifier(targetId, 'marked') * 0.15))
                    elif self.suitHasCondition(targetId, 'soaked'):
                        chance = ToontownBattleGlobals.DropMissChance[atkLevel] - 15
                        if organicBonus:
                            attackDamage *= 1.1
                    elif self.suitHasCondition(targetId, 'dazed'):
                        chance = ToontownBattleGlobals.DropMissChance[atkLevel] - 15
                        if organicBonus:
                            attackDamage *= 1.1
                    elif self.toonHasCondition(toonId, 'cheer'):
                        chance = ToontownBattleGlobals.DropMissChance[atkLevel] - 10
                        if organicBonus:
                            attackDamage *= 1.1
                    elif self.suitHasCondition(targetId, 'marked'):
                        chance = ToontownBattleGlobals.DropMissChance[atkLevel] - 5
                        attackDamage *= (1 + (self.getSuitConditionModifier(targetId, 'marked') * 0.1))
                    else:
                        chance = ToontownBattleGlobals.DropMissChance[atkLevel]
                    if random.randint(0, 99) <= chance:
                        self.notify.debug(
                                'Toon attack rolled' + str(chance))
                        attackDamage = 0
                    elif random.randint(0, 99) >= chance:
                        self.notify.debug(
                                'Toon attack rolled' + str(chance))
                        attackDamage *= 1
                    target = self.battle.findSuit(attack[TOON_TGT_COL])
                    for s in self.battle.activeSuits:
                        if s.dna.name == 'scg':
                            target2 = s
                            if target2.dna.name == 'scg' and self.suitHasCondition(target2.doId,
                                                                                   'shielding') and not target.dna.name == 'scg':
                                attackDamage *= .7
                                target2.setHP(target2.currHP - (int(attackDamage * .425)))
                                if target2.getHP() <= 0:
                                    self.__removeLured(target2.doId)
                                    if target2.getSkeleRevives() >= 1:
                                        target2.useSkeleRevive()
                        elif s.dna.name == 'cp':
                            target2 = s
                            if target2.dna.name == 'cp' and self.suitHasCondition(target2.doId, 'shielding') and not target.dna.name == 'cp':
                                attackDamage *= .7
                                target2.setHP(target2.currHP - (int(attackDamage * .425)))
                                if target2.getHP() <= 0:
                                    self.__removeLured(target2.doId)
                                    if target2.getSkeleRevives() >= 1:
                                        target2.useSkeleRevive()
                        elif s.dna.name == 'cry':
                            target2 = s
                            if target2.dna.name == 'cry' and self.suitHasCondition(target2.doId, 'shielding') and not target.dna.name == 'cry':
                                attackDamage *= .7
                                target2.setHP(target2.currHP - (int(attackDamage * .425)))
                                if target2.getHP() <= 0:
                                    self.__removeLured(target2.doId)
                                    if target2.getSkeleRevives() >= 1:
                                        target2.useSkeleRevive()
                        elif s.dna.name == 'dsf':
                            target2 = s
                            if target2.dna.name == 'dsf' and self.suitHasCondition(target2.doId, 'absorbingHR') and not target.dna.name == 'dsf':
                                attackDamage *= .9
                                target2.setHP(target2.currHP - (int(attackDamage * .115)))
                                if target2.getHP() <= 0:
                                    self.__removeLured(target2.doId)
                                    if target2.getSkeleRevives() >= 1:
                                        target2.useSkeleRevive()
                        elif s.dna.name == 'blr':
                            target9 = s
                            if target9.dna.name == 'blr' and self.suitHasCondition(target9.doId, 'shielding') and not target.dna.name == 'blr':
                                attackDamage *= .7
                                target9.setHP(target9.currHP - (int(attackDamage * .425)))
                                if target9.getHP() <= 0:
                                    self.__removeLured(target9.doId)
                                    if target9.getSkeleRevives() >= 1:
                                        target9.useSkeleRevive()
                elif atkTrack == ZAP:
                    if self.toonHasCondition(toon.doId, 'nolevel8s') and attackLevel == 7:
                        self.setToonCondition(toon.doId, 'banned', 1, 3, 'setBoth')
                    if self.toonHasCondition(toon.doId, 'nolevel7s') and attackLevel == 6:
                        self.setToonCondition(toon.doId, 'banned', 1, 3, 'setBoth')
                    if self.toonHasCondition(toon.doId, 'nolevel6s') and attackLevel == 5:
                        self.setToonCondition(toon.doId, 'banned', 1, 3, 'setBoth')
                    if self.toonHasCondition(toon.doId, 'nolevel5s') and attackLevel == 4:
                        self.setToonCondition(toon.doId, 'banned', 1, 3, 'setBoth')
                    if self.toonHasCondition(toon.doId, 'nolevel4s') and attackLevel == 3:
                        self.setToonCondition(toon.doId, 'banned', 1, 3, 'setBoth')
                    if self.toonHasCondition(toon.doId, 'noZapGags'):
                        self.setToonCondition(toon.doId, 'banned2', 1, 3, 'setBoth')
                    if self.toonHasCondition(toon.doId, 'noGags'):
                        self.setToonCondition(toon.doId, 'banned3', 1, 3, 'setBoth')
                    suit = self.battle.findSuit(targetId)
                    if suit.dna.name == 'tcm':
                        self.setSuitCondition(targetId, 'zapcalculator', 1, 10, 'setBoth')
                    if suit.dna.name == 'fbd' and self.suitHasCondition(targetId, 'bookkeeping'):
                        self.setToonCondition(toon.doId, 'bookkeepingtoon', 1, 5, 'setBoth')
                    if self.suitHasCondition(targetId, 'soaked'):
                        attackDamage = getAvPropDamage(attackTrack, attackLevel, toon.experience.getExp(attackTrack))
                    elif self.suitHasCondition(targetId, 'zapImmune'):
                        attackDamage = 0
                    else:
                        attackDamage = 0
                    if self.suitHasCondition(targetId, 'vulnerable') and self.suitHasCondition(targetId, 'marked'):
                        attackDamage *= (1.25 + (self.getSuitConditionModifier(targetId, 'marked') * 0.1))
                    if self.suitHasCondition(targetId, 'enraged') and self.suitHasCondition(targetId, 'desperation') and self.suitHasCondition(targetId, 'marked'):
                        attackDamage *= (1 + (self.getSuitConditionModifier(targetId, 'marked') * 0.1))
                    if self.suitHasCondition(targetId, 'enraged') and self.suitHasCondition(targetId, 'marked'):
                        attackDamage *= (0.7 + (self.getSuitConditionModifier(targetId, 'marked') * 0.1))
                    if self.suitHasCondition(targetId, 'damageReduction') and self.suitHasCondition(targetId, 'marked'):
                        attackDamage *= (0.5 + (self.getSuitConditionModifier(targetId, 'marked') * 0.1))
                    if self.suitHasCondition(targetId, 'marked'):
                        attackDamage *= (1 + (self.getSuitConditionModifier(targetId, 'marked') * 0.1))
                    if self.suitHasCondition(targetId, 'enraged') and self.suitHasCondition(targetId, 'desperation'):
                        attackDamage *= 1
                    if self.suitHasCondition(targetId, 'enraged'):
                        attackDamage *= 0.7
                    if self.suitHasCondition(targetId, 'soakImmune') and self.suitHasCondition(targetId, 'soaked'):
                        attackDamage *= 0.4
                    if self.suitHasCondition(targetId, 'damageReduction'):
                        attackDamage *= 0.5
                    if self.suitHasCondition(targetId, 'vulnerable'):
                        attackDamage *= 1.25
                    if self.toonHasCondition(toonId, 'zapBoost'):
                        attackDamage *= (1.0 + self.getToonConditionModifier(toonId, 'zapBoost') * 0.01)
                    elif self.toonHasCondition(toonId,
                                             'allGagBoost'):
                        attackDamage *= (1.0 + (self.getToonConditionModifier(toonId, 'allGagBoost') * 0.01))
                        attackDamage = math.ceil(attackDamage)
                    elif self.toonHasCondition(toonId, 'encore'):
                        attackDamage *= 1.16
                    elif self.toonHasCondition(toonId, 'encore2'):
                        attackDamage *= 1.08
                    elif self.suitHasCondition(targetId, 'HRdamagereduction'):
                        attackDamage *= 0.1
                    target = self.battle.findSuit(attack[TOON_TGT_COL])
                    activeSuits = self.battle.activeSuits
                    suitIndex = activeSuits.index(target)
                    if attackDamage > 0:
                        self.setSuitCondition(target.doId, 'soaked', 1, 1, 'setBoth')
                    for s in self.battle.activeSuits:
                        if s.dna.name == 'scg':
                            target2 = s
                            if target2.dna.name == 'scg' and self.suitHasCondition(target2.doId, 'shielding') and not target.dna.name == 'scg':
                                attackDamage *= .7
                                target2.setHP(target2.currHP - (int(attackDamage * .425)))
                                if target2.getHP() <= 0:
                                    self.__removeLured(target2.doId)
                                    if target2.getSkeleRevives() >= 1:
                                        target2.useSkeleRevive()
                        elif s.dna.name == 'cp':
                            target2 = s
                            if target2.dna.name == 'cp' and self.suitHasCondition(target2.doId, 'shielding') and not target.dna.name == 'cp':
                                attackDamage *= .7
                                target2.setHP(target2.currHP - (int(attackDamage * .425)))
                                if target2.getHP() <= 0:
                                    self.__removeLured(target2.doId)
                                    if target2.getSkeleRevives() >= 1:
                                        target2.useSkeleRevive()
                        elif s.dna.name == 'dsf':
                            target2 = s
                            if target2.dna.name == 'dsf' and self.suitHasCondition(target2.doId, 'absorbingHR') and not target.dna.name == 'dsf':
                                attackDamage *= .9
                                target2.setHP(target2.currHP - (int(attackDamage * .115)))
                                if target2.getHP() <= 0:
                                    self.__removeLured(target2.doId)
                                    if target2.getSkeleRevives() >= 1:
                                        target2.useSkeleRevive()
                        elif s.dna.name == 'cry':
                            target9 = s
                            if target9.dna.name == 'cry' and self.suitHasCondition(target9.doId, 'shielding') and not target.dna.name == 'cry':
                                attackDamage *= .7
                                target9.setHP(target9.currHP - (int(attackDamage * .425)))
                                if target9.getHP() <= 0:
                                    self.__removeLured(target9.doId)
                                    if target9.getSkeleRevives() >= 1:
                                        target9.useSkeleRevive()
                        elif s.dna.name == 'blr':
                            target9 = s
                            if target9.dna.name == 'blr' and self.suitHasCondition(target9.doId, 'shielding') and not target.dna.name == 'blr':
                                attackDamage *= .7
                                target9.setHP(target9.currHP - (int(attackDamage * .425)))
                                if target9.getHP() <= 0:
                                    self.__removeLured(target9.doId)
                                    if target9.getSkeleRevives() >= 1:
                                        target9.useSkeleRevive()
                    if suitIndex + 1 < len(activeSuits):
                        target3 = activeSuits[suitIndex + 1]
                        if not self.suitHasCondition(target3.doId, 'immune') and not self.suitHasCondition(target3.doId,
                                                                                                           'zapImmune') :
                            organicBonus = self.__toonCheckGagBonus(attack[TOON_ID_COL], atkTrack, atkLevel)
                            if organicBonus:
                                attackDamageAbsorb = (int(attackDamage * .84) * .425)
                                attackDamageAbsorbHR = (int(attackDamage * .84) * .115)
                                target3.setHP(target3.currHP - int(attackDamage * 0.84))
                            else:
                                attackDamageAbsorb = (int(attackDamage * .67) * .425)
                                attackDamageAbsorbHR = (int(attackDamage * .67) * .115)
                                target3.setHP(target3.currHP - int(attackDamage * 0.67))
                            self.setSuitCondition(target3.doId, 'lured', 0, 0, 'setBoth')
                            self.setSuitCondition(target3.doId, 'soaked', 1, 1, 'setBoth')
                            if target3.dna.name == 'fbd' and self.suitHasCondition(target3.doId, 'bookkeeping'):
                                self.setToonCondition(toon.doId, 'bookkeepingtoon', 1, 5, 'setBoth')
                            self.__removeLured(target3.doId)
                            for s in self.battle.activeSuits:
                                if s.dna.name == 'scg':
                                    target9 = s
                                    if target9.dna.name == 'scg' and self.suitHasCondition(target9.doId,
                                                                                           'shielding') and not target3.dna.name == 'scg':
                                        target9.setHP(target9.currHP - (int(attackDamageAbsorb)))
                                        if target9.getHP() <= 0:
                                            self.__removeLured(target9.doId)
                                            if target9.getSkeleRevives() >= 1:
                                                target9.useSkeleRevive()
                                elif s.dna.name == 'cp':
                                    target9 = s
                                    if target9.dna.name == 'cp' and self.suitHasCondition(target9.doId,
                                                                                          'shielding') and not target3.dna.name == 'cp':
                                        target9.setHP(target9.currHP - (int(attackDamageAbsorb)))
                                        if target9.getHP() <= 0:
                                            self.__removeLured(target9.doId)
                                            if target9.getSkeleRevives() >= 1:
                                                target9.useSkeleRevive()
                                elif s.dna.name == 'dsf':
                                    target9 = s
                                    if target9.dna.name == 'dsf' and self.suitHasCondition(target9.doId,
                                                                                           'absorbingHR') and not target3.dna.name == 'dsf':
                                        target9.setHP(target9.currHP - (int(attackDamageAbsorbHR)))
                                        if target9.getHP() <= 0:
                                            self.__removeLured(target9.doId)
                                            if target9.getSkeleRevives() >= 1:
                                                target9.useSkeleRevive()
                                elif s.dna.name == 'cry':
                                    target9 = s
                                    if target9.dna.name == 'cry' and self.suitHasCondition(target9.doId,
                                                                                           'shielding') and not target3.dna.name == 'cry':
                                        target9.setHP(target9.currHP - (int(attackDamageAbsorb)))
                                        if target9.getHP() <= 0:
                                            self.__removeLured(target9.doId)
                                            if target9.getSkeleRevives() >= 1:
                                                target9.useSkeleRevive()
                                elif s.dna.name == 'blr':
                                    target9 = s
                                    if target9.dna.name == 'blr' and self.suitHasCondition(target9.doId,
                                                                                           'shielding') and not target3.dna.name == 'blr':
                                        target9.setHP(target9.currHP - (int(attackDamageAbsorb)))
                                        if target9.getHP() <= 0:
                                            self.__removeLured(target9.doId)
                                            if target9.getSkeleRevives() >= 1:
                                                target9.useSkeleRevive()
                            if target3.getHP() <= 0:
                                self.__removeLured(target3.doId)
                                if target3.getSkeleRevives() >= 1:
                                    target3.useSkeleRevive()
                    if suitIndex + 2 < len(activeSuits):
                        target4 = activeSuits[suitIndex + 2]
                        if not self.suitHasCondition(target4.doId, 'immune') and not self.suitHasCondition(target4.doId,
                                                                                                           'zapImmune'):
                            organicBonus = self.__toonCheckGagBonus(attack[TOON_ID_COL], atkTrack, atkLevel)
                            if organicBonus:
                                attackDamageAbsorb = (int(attackDamage * .67) * .425)
                                attackDamageAbsorbHR = (int(attackDamage * .67) * .115)
                                target4.setHP(target4.currHP - int(attackDamage * 0.67))
                            else:
                                attackDamageAbsorb = (int(attackDamage * .35) * .425)
                                attackDamageAbsorbHR = (int(attackDamage * .35) * .115)
                                target4.setHP(target4.currHP - int(attackDamage * 0.35))
                            self.__removeLured(target4.doId)
                            self.setSuitCondition(target4.doId, 'lured', 0, 0, 'setBoth')
                            self.setSuitCondition(target4.doId, 'soaked', 1, 1, 'setBoth')
                            if target4.dna.name == 'fbd' and self.suitHasCondition(target4.doId, 'bookkeeping'):
                                self.setToonCondition(toon.doId, 'bookkeepingtoon', 1, 5, 'setBoth')
                            for s in self.battle.activeSuits:
                                if s.dna.name == 'scg':
                                    target9 = s
                                    if target9.dna.name == 'scg' and self.suitHasCondition(target9.doId,
                                                                                           'shielding') and not target4.dna.name == 'scg':
                                        target9.setHP(target9.currHP - (int(attackDamageAbsorb)))
                                        if target9.getHP() <= 0:
                                            self.__removeLured(target9.doId)
                                            if target9.getSkeleRevives() >= 1:
                                                target9.useSkeleRevive()
                                elif s.dna.name == 'cp':
                                    target9 = s
                                    if target9.dna.name == 'cp' and self.suitHasCondition(target9.doId,
                                                                                          'shielding') and not target4.dna.name == 'cp':
                                        target9.setHP(target9.currHP - (int(attackDamageAbsorb)))
                                        if target9.getHP() <= 0:
                                            self.__removeLured(target9.doId)
                                            if target9.getSkeleRevives() >= 1:
                                                target9.useSkeleRevive()
                                elif s.dna.name == 'blr':
                                    target9 = s
                                    if target9.dna.name == 'blr' and self.suitHasCondition(target9.doId,
                                                                                           'shielding') and not target4.dna.name == 'blr':
                                        target9.setHP(target9.currHP - (int(attackDamageAbsorb)))
                                        if target9.getHP() <= 0:
                                            self.__removeLured(target9.doId)
                                            if target9.getSkeleRevives() >= 1:
                                                target9.useSkeleRevive()
                                elif s.dna.name == 'cry':
                                    target9 = s
                                    if target9.dna.name == 'cry' and self.suitHasCondition(target9.doId,
                                                                                           'shielding') and not target4.dna.name == 'cry':
                                        target9.setHP(target9.currHP - (int(attackDamageAbsorb)))
                                        if target9.getHP() <= 0:
                                            self.__removeLured(target9.doId)
                                            if target9.getSkeleRevives() >= 1:
                                                target9.useSkeleRevive()
                                elif s.dna.name == 'dsf':
                                    target9 = s
                                    if target9.dna.name == 'dsf' and self.suitHasCondition(target9.doId,
                                                                                           'absorbingHR') and not target4.dna.name == 'dsf':
                                        target9.setHP(target9.currHP - (int(attackDamageAbsorbHR)))
                                        if target9.getHP() <= 0:
                                            self.__removeLured(target9.doId)
                                            if target9.getSkeleRevives() >= 1:
                                                target9.useSkeleRevive()
                            if target4.getHP() <= 0:
                                self.__removeLured(target4.doId)
                                if target4.getSkeleRevives() >= 1:
                                    target4.useSkeleRevive()
                    if suitIndex - 1 >= 0:
                        target2 = activeSuits[suitIndex - 1]
                        if not self.suitHasCondition(target2.doId, 'immune') and not self.suitHasCondition(target2.doId,
                                                                                                           'zapImmune'):
                            organicBonus = self.__toonCheckGagBonus(attack[TOON_ID_COL], atkTrack, atkLevel)
                            if organicBonus:
                                attackDamageAbsorb = (int(attackDamage * .84) * .425)
                                attackDamageAbsorbHR = (int(attackDamage * .84) * .115)
                                target2.setHP(target2.currHP - int(attackDamage * 0.84))
                            else:
                                attackDamageAbsorb = (int(attackDamage * .67) * .425)
                                attackDamageAbsorbHR = (int(attackDamage * .67) * .115)
                                target2.setHP(target2.currHP - int(attackDamage * 0.67))
                            self.__removeLured(target2.doId)
                            self.setSuitCondition(target2.doId, 'lured', 0, 0, 'setBoth')
                            self.setSuitCondition(target2.doId, 'soaked', 1, 1, 'setBoth')
                            if target2.dna.name == 'fbd' and self.suitHasCondition(target2.doId, 'bookkeeping'):
                                self.setToonCondition(toon.doId, 'bookkeepingtoon', 1, 5, 'setBoth')
                            for s in self.battle.activeSuits:
                                if s.dna.name == 'scg':
                                    target9 = s
                                    if target9.dna.name == 'scg' and self.suitHasCondition(target9.doId,
                                                                                           'shielding') and not target2.dna.name == 'scg':
                                        target9.setHP(target9.currHP - (int(attackDamageAbsorb)))
                                        if target9.getHP() <= 0:
                                            self.__removeLured(target9.doId)
                                            if target9.getSkeleRevives() >= 1:
                                                target9.useSkeleRevive()
                                elif s.dna.name == 'cp':
                                    target9 = s
                                    if target9.dna.name == 'cp' and self.suitHasCondition(target9.doId,
                                                                                          'shielding') and not target2.dna.name == 'cp':
                                        target9.setHP(target9.currHP - (int(attackDamageAbsorb)))
                                        if target9.getHP() <= 0:
                                            self.__removeLured(target9.doId)
                                            if target9.getSkeleRevives() >= 1:
                                                target9.useSkeleRevive()
                                elif s.dna.name == 'blr':
                                    target9 = s
                                    if target9.dna.name == 'blr' and self.suitHasCondition(target9.doId,
                                                                                           'shielding') and not target2.dna.name == 'blr':
                                        target9.setHP(target9.currHP - (int(attackDamageAbsorb)))
                                        if target9.getHP() <= 0:
                                            self.__removeLured(target9.doId)
                                            if target9.getSkeleRevives() >= 1:
                                                target9.useSkeleRevive()
                                elif s.dna.name == 'cry':
                                    target9 = s
                                    if target9.dna.name == 'cry' and self.suitHasCondition(target9.doId,
                                                                                           'shielding') and not target2.dna.name == 'cry':
                                        target9.setHP(target9.currHP - (int(attackDamageAbsorb)))
                                        if target9.getHP() <= 0:
                                            self.__removeLured(target9.doId)
                                            if target9.getSkeleRevives() >= 1:
                                                target9.useSkeleRevive()
                                elif s.dna.name == 'dsf':
                                    target9 = s
                                    if target9.dna.name == 'dsf' and self.suitHasCondition(target9.doId,
                                                                                           'absorbingHR') and not target2.dna.name == 'dsf':
                                        target9.setHP(target9.currHP - (int(attackDamageAbsorbHR)))
                                        if target9.getHP() <= 0:
                                            self.__removeLured(target9.doId)
                                            if target9.getSkeleRevives() >= 1:
                                                target9.useSkeleRevive()
                            if target2.getHP() <= 0:
                                self.__removeLured(target2.doId)
                                if target2.getSkeleRevives() >= 1:
                                    target2.useSkeleRevive()
                    if suitIndex - 2 >= 0:
                        target1 = activeSuits[suitIndex - 2]
                        if not self.suitHasCondition(target1.doId, 'immune') and not self.suitHasCondition(target1.doId,
                                                                                                           'zapImmune'):
                            organicBonus = self.__toonCheckGagBonus(attack[TOON_ID_COL], atkTrack, atkLevel)
                            if organicBonus:
                                attackDamageAbsorb = (int(attackDamage * .67) * .425)
                                attackDamageAbsorbHR = (int(attackDamage * .67) * .115)
                                target1.setHP(target1.currHP - int(attackDamage * 0.67))
                            else:
                                attackDamageAbsorb = (int(attackDamage * .35) * .425)
                                attackDamageAbsorbHR = (int(attackDamage * .35) * .115)
                                target1.setHP(target1.currHP - int(attackDamage * 0.35))
                            self.__removeLured(target1.doId)
                            self.setSuitCondition(target1.doId, 'lured', 0, 0, 'setBoth')
                            self.setSuitCondition(target1.doId, 'soaked', 1, 1, 'setBoth')
                            if target1.dna.name == 'fbd' and self.suitHasCondition(target1.doId, 'bookkeeping'):
                                self.setToonCondition(toon.doId, 'bookkeepingtoon', 1, 5, 'setBoth')
                            for s in self.battle.activeSuits:
                                if s.dna.name == 'scg':
                                    target9 = s
                                    if target9.dna.name == 'scg' and self.suitHasCondition(target9.doId,
                                                                                           'shielding') and not target1.dna.name == 'scg':
                                        target9.setHP(target9.currHP - (int(attackDamageAbsorb)))
                                        if target9.getHP() <= 0:
                                            self.__removeLured(target9.doId)
                                            if target9.getSkeleRevives() >= 1:
                                                target9.useSkeleRevive()
                                elif s.dna.name == 'cp':
                                    target9 = s
                                    if target9.dna.name == 'cp' and self.suitHasCondition(target9.doId,
                                                                                          'shielding') and not target1.dna.name == 'cp':
                                        target9.setHP(target9.currHP - (int(attackDamageAbsorb)))
                                        if target9.getHP() <= 0:
                                            self.__removeLured(target9.doId)
                                            if target9.getSkeleRevives() >= 1:
                                                target9.useSkeleRevive()
                                elif s.dna.name == 'blr':
                                    target9 = s
                                    if target9.dna.name == 'blr' and self.suitHasCondition(target9.doId,
                                                                                           'shielding') and not target1.dna.name == 'blr':
                                        target9.setHP(target9.currHP - (int(attackDamageAbsorb)))
                                        if target9.getHP() <= 0:
                                            self.__removeLured(target9.doId)
                                            if target9.getSkeleRevives() >= 1:
                                                target9.useSkeleRevive()
                                elif s.dna.name == 'dsf':
                                    target9 = s
                                    if target9.dna.name == 'dsf' and self.suitHasCondition(target9.doId,
                                                                                           'absorbingHR') and not target1.dna.name == 'dsf':
                                        target9.setHP(target9.currHP - (int(attackDamageAbsorbHR)))
                                        if target9.getHP() <= 0:
                                            self.__removeLured(target9.doId)
                                            if target9.getSkeleRevives() >= 1:
                                                target9.useSkeleRevive()
                                elif s.dna.name == 'cry':
                                    target9 = s
                                    if target9.dna.name == 'cry' and self.suitHasCondition(target9.doId,
                                                                                           'shielding') and not target1.dna.name == 'cry':
                                        target9.setHP(target9.currHP - (int(attackDamageAbsorb)))
                                        if target9.getHP() <= 0:
                                            self.__removeLured(target9.doId)
                                            if target9.getSkeleRevives() >= 1:
                                                target9.useSkeleRevive()
                            if target1.getHP() <= 0:
                                self.__removeLured(target1.doId)
                                if target1.getSkeleRevives() >= 1:
                                    target1.useSkeleRevive()
                    if self.__isWet(targetId) or self.__isRaining(self.battle.getToon(toonId)):
                        chance = InstaKillChance[atkLevel]
                        if random.randint(0, 99) <= chance:
                            suit = self.battle.findSuit(targetId)
                            if suit.getHP() > 500:
                                attackDamage = 500
                            else:
                                suit.b_setSkeleRevives(0)
                                attackDamage = suit.getHP()
                            targetList
                        else:
                            attackDamage = getAvPropDamage(attackTrack, attackLevel, toon.experience.getExp(attackTrack))
                else:
                    attackDamage = getAvPropDamage(attackTrack, attackLevel, toon.experience.getExp(attackTrack))
                if self.toonHasCondition(toonId, 'allGagBoost') and atkTrack is not FIRE and atkTrack is not ZAP and atkTrack is not SQUIRT:
                    attackDamage *= (1.0 + (self.getToonConditionModifier(toonId, 'allGagBoost') * 0.01))
                    attackDamage = math.ceil(attackDamage)
                elif self.suitHasCondition(targetId, 'immune'):
                    attackDamage = 0
                elif self.suitHasCondition(targetId, 'HRdamagereduction'):
                    attackDamage *= 0.1
                elif self.suitHasCondition(targetId, 'enraged') and self.suitHasCondition(targetId, 'desperation') and self.suitHasCondition(targetId, 'marked') and atkTrack is not DROP and not atkTrack == THROW and atkTrack is not ZAP and atkTrack is not SQUIRT:
                    attackDamage *= (1 + (self.getSuitConditionModifier(targetId, 'marked') * 0.1))
                elif self.suitHasCondition(targetId, 'enraged') and self.suitHasCondition(targetId, 'marked') and atkTrack is not THROW and atkTrack is not DROP and atkTrack is not ZAP and atkTrack is not SQUIRT:
                    attackDamage *= (0.7 + (self.getSuitConditionModifier(targetId, 'marked') * 0.1))
                elif self.suitHasCondition(targetId, 'damageReduction') and self.suitHasCondition(targetId, 'marked') and atkTrack is not DROP and atkTrack is not THROW and atkTrack is not ZAP and atkTrack is not SQUIRT:
                    attackDamage *= (0.5 + (self.getSuitConditionModifier(targetId, 'marked') * 0.1))
                elif self.suitHasCondition(targetId, 'vulnerable') and self.suitHasCondition(targetId, 'marked') and atkTrack is not DROP and atkTrack is not THROW and atkTrack is not ZAP and atkTrack is not SQUIRT:
                    attackDamage *= (1.25 + (self.getSuitConditionModifier(targetId, 'marked') * 0.1))
                elif self.suitHasCondition(targetId, 'marked') and atkTrack is not DROP and atkTrack is not THROW and atkTrack is not ZAP and atkTrack is not SQUIRT:
                    attackDamage *= (1 + (self.getSuitConditionModifier(targetId, 'marked') * 0.1))
                elif self.suitHasCondition(targetId, 'enraged') and self.suitHasCondition(targetId, 'desperation'):
                    attackDamage *= 1
                elif self.suitHasCondition(targetId, 'enraged') and atkTrack is not ZAP and atkTrack is not SQUIRT:
                    attackDamage *= 0.7
                elif self.suitHasCondition(targetId, 'soakImmune') and self.suitHasCondition(targetId, 'soaked') and atkTrack is not ZAP and atkTrack is not SQUIRT:
                    attackDamage *= 0.4
                elif self.suitHasCondition(targetId, 'damageReduction') and atkTrack is not ZAP and atkTrack is not SQUIRT:
                    attackDamage *= 0.5
                elif self.suitHasCondition(targetId, 'vulnerable') and atkTrack is not ZAP and atkTrack is not SQUIRT:
                    attackDamage *= 1.25
                elif self.getToonConditionTurns(toonId, 'encore') and atkTrack is not ZAP and atkTrack is not SQUIRT and not atkTrack == SOUND:
                    attackDamage *= 1.16
                elif self.getToonConditionTurns(toonId, 'encore2') and atkTrack is not ZAP and atkTrack is not SQUIRT and not atkTrack == SOUND:
                    attackDamage *= 1.16
                elif self.suitHasCondition(targetId, 'damageReduction') and atkTrack == SOUND:
                    attackDamage *= 0.1
                elif self.toonHasCondition(toonId, 'winded') and self.toonHasCondition(toonId, 'encore') and atkTrack == SOUND:
                    attackDamage *= 1.16
                elif self.getToonConditionTurns(toonId, 'encore') == 1 and atkTrack == SOUND:
                    attackDamage *= 1
                elif self.getToonConditionTurns(toonId, 'encore2') == 1 and atkTrack == SOUND:
                    attackDamage *= 1
                elif self.toonHasCondition(toonId, 'winded') and atkTrack == SOUND:
                    attackDamage *= 0.5
                attackDamage = math.ceil(attackDamage)
                if not self.__combatantDead(targetId, toon=toonTarget):
                    if self.__suitIsLured(targetId) and atkTrack == DROP:
                        self.notify.debug('not setting validTargetAvail, since drop on a lured suit')
                    else:
                        validTargetAvail = 1
            if attackLevel == -1 and not atkTrack == FIRE:
                if self.suitHasCondition(targetId, 'immune'):
                    result = 0
                elif self.suitHasCondition(targetId, 'enraged') and self.suitHasCondition(targetId, 'desperation'):
                    result = 0
                elif self.suitHasCondition(targetId, 'lureImmune'):
                    result = 0
                else:
                    result = LURE_SUCCEEDED
            elif atkTrack != TRAP:
                result = attackDamage
                if atkTrack == HEAL:
                    if not self.__attackHasHit(attack, suit=0):
                        result = result * 0.2
                else:
                    if self.__suitIsLured(targetId) and atkTrack == DROP:
                        result = 0
            else:
                result = 0
            if result != 0 or atkTrack == PETSOS:
                targets = self.__getToonTargets(attack)
                if targetList[currTarget] not in targets:
                    if self.notify.getDebug():
                        self.notify.debug('Target of toon is not accessible!')
                    continue
                targetIndex = targets.index(targetList[currTarget])
                if atkTrack == HEAL:
                    organicBonus = self.__toonCheckGagBonus(attack[TOON_ID_COL], atkTrack, atkLevel)
                    result = result / len(targetList)
                    toon = self.battle.getToon(toonId)
                    if organicBonus:
                        self.setToonCondition(toonId, 'cheer', 1, 2, 'setBoth')
                        toon.toonUp(math.ceil((attackDamage / 2.5) / len(targetList)))
                    else:
                        self.setToonCondition(toonId, 'cheer', 1, 1, 'setBoth')
                        toon.toonUp(math.ceil((attackDamage / 4) / len(targetList)))
                if atkTrack == THROW:
                    organicBonus = self.__toonCheckGagBonus(attack[TOON_ID_COL], atkTrack, atkLevel)
                    result = result / len(targetList)
                    toon = self.battle.getToon(toonId)
                    if organicBonus:
                        toon.toonUp(math.ceil((attackDamage / 5)))
                if targetId in self.successfulLures and atkTrack == LURE:
                    if lureDidDamage:
                        if self.suitHasCondition(targetId, 'dazed2'):
                            suit = self.battle.findSuit(targetId)
                            if suit.dna.name == 'tcm':
                                self.setSuitCondition(targetId, 'trapcalculator', 1, 10, 'setBoth')
                            self.setSuitCondition(targetId, 'dazed', 1, 2, 'setBoth')
                            self.setSuitCondition(targetId, 'dazed2', 0, 0, 'setBoth')
                    self.successfulLures[targetId][3] = result
                else:
                    attack[TOON_HP_COL][targetIndex] = result
                if result > 0 and atkTrack != HEAL and atkTrack != DROP and atkTrack != PETSOS:
                    attackTrack = LURE
                    lureInfos = self.__getLuredExpInfo(targetId)
                    for currInfo in lureInfos:
                        if currInfo[3]:
                            self.__addAttackExp(attack, track=attackTrack, level=currInfo[1], attackerId=currInfo[0])
                        self.__clearLurer(currInfo[0], lureId=currInfo[2])

        if lureDidDamage:
            if self.itemIsCredit(atkTrack, atkLevel):
                self.__addAttackExp(attack)
        if not validTargetAvail and self.__prevAtkTrack(toonId) != atkTrack:
            self.__clearAttack(toonId)
        return

    def __getToonTargets(self, attack):
        track = self.__getActualTrack(attack)
        if track == HEAL or track == PETSOS:
            return self.battle.activeToons
        else:
            return self.battle.activeSuits

    def __attackHasHit(self, attack, suit = 0):
        if suit == 1:
            for dmg in attack[SUIT_HP_COL]:
                if dmg > 0:
                    return 1

            return 0
        else:
            track = self.__getActualTrack(attack)
            return not attack[TOON_ACCBONUS_COL] and track != NO_ATTACK

    def __attackDamage(self, attack, suit = 0):
        if suit:
            for dmg in attack[SUIT_HP_COL]:
                if dmg > 0:
                    return dmg

            return 0
        else:
            for dmg in attack[TOON_HP_COL]:
                if dmg > 0:
                    return dmg

            return 0

    def __addEnragedSuitInfo(self, suitId, currRounds, maxRounds, decreasedDef = False):
        self.currentlyEnragedSuits[suitId] = [currRounds, maxRounds, decreasedDef,]

    def __isEnraged(self, suit):
        if suit in self.currentlyEnragedSuits:
            return True
        else:
            return False
    def __addAbsorbingSuitInfo(self, suitId, currRounds, maxRounds, decreasedDef = False):
        self.currentlyAbsorbingSuits[suitId] = [currRounds, maxRounds, decreasedDef,]

    def __isAbsorbing(self, suit):
        if suit in self.currentlyAbsorbingSuits:
            return True
        else:
            return False

    def __addWetSuitInfo(self, suitId, currRounds, maxRounds, decreasedDef = False):
        self.currentlyWetSuits[suitId] = [currRounds, maxRounds, decreasedDef,]

    def __isWet(self, suit):
        if suit in self.currentlyWetSuits:
            return True
        else:
            return False

    def __isRaining(self, toon):
        if simbase.air.isRaining == True and self.checkIfStreetZone(toon):
            return True
        else:
            return False

    def checkIfStreetZone(self, toon):
	try:
            if ZoneUtil.getWhereName(toon.zoneId, True) == 'street' and not ZoneUtil.isDynamicZone(toon.zoneId):
                return True
            else:
                return False
	except:
            return False

    def __attackDamageForTgt(self, attack, tgtPos, suit = 0):
        if suit:
            return attack[SUIT_HP_COL][tgtPos]
        else:
            return attack[TOON_HP_COL][tgtPos]

    def __calcToonAccBonus(self, attackKey):
        numPrevHits = 0
        attackIdx = self.toonAtkOrder.index(attackKey)
        for currPrevAtk in xrange(attackIdx - 1, -1, -1):
            attack = self.battle.toonAttacks[attackKey]
            atkTrack, atkLevel = self.__getActualTrackLevel(attack)
            prevAttackKey = self.toonAtkOrder[currPrevAtk]
            prevAttack = self.battle.toonAttacks[prevAttackKey]
            prvAtkTrack, prvAtkLevel = self.__getActualTrackLevel(prevAttack)
            if self.__attackHasHit(prevAttack) and (attackAffectsGroup(prvAtkTrack, prvAtkLevel, prevAttack[TOON_TRACK_COL]) or attackAffectsGroup(atkTrack, atkLevel, attack[TOON_TRACK_COL]) or attack[TOON_TGT_COL] == prevAttack[TOON_TGT_COL]) and atkTrack != prvAtkTrack:
                numPrevHits += 1

        if numPrevHits > 0 and self.notify.getDebug():
            self.notify.debug('ACC BONUS: toon attack received accuracy ' + 'bonus of ' + str(AccuracyBonuses[numPrevHits]) + ' from previous attack by (' + str(attack[TOON_ID_COL]) + ') which hit')
        return AccuracyBonuses[numPrevHits]

    def __applyToonAttackDamages(self, toonId, hpbonus = 0, kbbonus = 0):
        totalDamages = 0
        if not APPLY_HEALTH_ADJUSTMENTS:
            return totalDamages
        attack = self.battle.toonAttacks[toonId]
        track = self.__getActualTrack(attack)
        if track != NO_ATTACK and track != SOS and track != TRAP and track != NPCSOS:
            targets = self.__getToonTargets(attack)
            for position in xrange(len(targets)):
                currTarget = targets[position]
                if hpbonus:
                    if targets[position] in self.__createToonTargetList(toonId):
                        damageDone = attack[TOON_HPBONUS_COL]
                    else:
                        damageDone = 0
                elif kbbonus:
                    if targets[position] in self.__createToonTargetList(toonId):
                        damageDone = attack[TOON_KBBONUS_COL][position]
                    else:
                        damageDone = 0
                elif self.suitHasCondition(currTarget, 'immune'):
                    damageDone = 0
                else:
                    damageDone = attack[TOON_HP_COL][position]
                if damageDone <= 0 or self.immortalSuits:
                    continue
                if track == HEAL or track == PETSOS:
                    currTarget = targets[position]
                    if CAP_HEALS:
                        toonHp = self.__getToonHp(currTarget)
                        toonMaxHp = self.__getToonMaxHp(currTarget)
                        if toonHp + damageDone > toonMaxHp:
                            damageDone = toonMaxHp - toonHp
                            attack[TOON_HP_COL][position] = damageDone
                    self.toonHPAdjusts[currTarget] += damageDone
                    totalDamages = totalDamages + damageDone
                    continue
                currTarget = targets[position]
                currentlyImmuneSuits = self.getImmuneSuits()
                if currTarget.getImmuneStatus() == 1:
                    currTarget.setHP(currTarget.getHP())
                elif self.suitHasCondition(currTarget, 'immune'):
                    currTarget.setHP(currTarget.getHP())
                else:
                    currTarget.setHP(currTarget.getHP() - damageDone)
                targetId = currTarget.getDoId()
                totalDamages = totalDamages + damageDone
                if currTarget.getHP() <= 0:
                    if currTarget.getSkeleRevives() >= 1:
                        currTarget.useSkeleRevive()
                        attack[SUIT_REVIVE_COL] = attack[SUIT_REVIVE_COL] | 1 << position
                    else:
                        self.suitLeftBattle(targetId)
                        attack[SUIT_DIED_COL] = attack[SUIT_DIED_COL] | 1 << position
                        if self.notify.getDebug():
                            self.notify.debug('Suit' + str(targetId) + 'bravely expired in combat')

        return totalDamages

    def __combatantDead(self, avId, toon):
        if toon:
            if self.__getToonHp(avId) <= 0:
                return 1
        else:
            suit = self.battle.findSuit(avId)
            if suit.getHP() <= 0:
                self.__removeLured(suit.doId)
                self.setSuitCondition(suit.doId, 'lured', 0, 0, 'setBoth')
                return 1
        return 0

    def __combatantJustRevived(self, avId):
        suit = self.battle.findSuit(avId)
        self.__removeLured(suit)
        if suit.reviveCheckAndClear():
            return 1
        else:
            return 0

    def checkRevertImmuneCogs(self):
        currentlyImmuneSuits = self.getImmuneSuits()
        immuneNum = 0
        for suit in self.battle.activeSuits:
            if suit.getImmuneStatus() == 1:
                immuneNum += 1
        if immuneNum == len(self.battle.activeSuits) and len(self.battle.joiningSuits) == 0 and len(
                self.battle.pendingSuits) == 0:
            return 1
        else:
            return 0

    def checkRevertEnragedCogs(self):
        currentlyEnragedSuits = self.getEnragedSuits()
        enragedNum = 0
        for suit in self.battle.activeSuits:
            if suit.getEnragedStatus() == 1:
                enragedNum += 1
        if enragedNum == len(self.battle.activeSuits) and len(self.battle.joiningSuits) == 0 and len(
                self.battle.pendingSuits) == 0:
            return 1
        else:
            return 0

    def checkRevertAbsorbingCogs(self):
        currentlyAbsorbingSuits = self.getAbsorbingSuits()
        absorbingNum = 0
        for suit in self.battle.activeSuits:
            if suit.getAbsorbingStatus() == 1:
                absorbingNum += 1
        if absorbingNum == len(self.battle.activeSuits) and len(self.battle.joiningSuits) == 0 and len(
                self.battle.pendingSuits) == 0:
            return 1
        else:
            return 0

    def checkRevertSoakedCogs(self):
        currentlySoakedSuits = self.getSoakedSuits()
        soakedNum = 0
        for suit in self.battle.activeSuits:
            if suit.getSoakedStatus() == 1:
                soakedNum += 1
        if soakedNum == len(self.battle.activeSuits) and len(self.battle.joiningSuits) == 0 and len(
                self.battle.pendingSuits) == 0:
            return 1
        else:
            return 0

    def __addAttackExp(self, attack, track = -1, level = -1, attackerId = -1):
        trk = -1
        lvl = -1
        id = -1
        if track != -1 and level != -1 and attackerId != -1:
            trk = track
            lvl = level
            id = attackerId
        elif self.__attackHasHit(attack):
            if self.notify.getDebug():
                self.notify.debug('Attack ' + repr(attack) + ' has hit')
            trk = attack[TOON_TRACK_COL]
            lvl = attack[TOON_LVL_COL]
            id = attack[TOON_ID_COL]
        if trk != -1 and trk != NPCSOS and trk != PETSOS and lvl != -1 and id != -1:
            expList = self.toonSkillPtsGained.get(id, None)
            if expList == None:
                expList = [0,
                 0,
                 0,
                 0,
                 0,
                 0,
                 0,
                 0]
                self.toonSkillPtsGained[id] = expList
            expList[trk] = min(ExperienceCap, expList[trk] + (lvl + 1) * self.__skillCreditMultiplier)


    def __clearTgtDied(self, tgt, lastAtk, currAtk):
        position = self.battle.activeSuits.index(tgt)
        currAtkTrack = self.__getActualTrack(currAtk)
        lastAtkTrack = self.__getActualTrack(lastAtk)
        if currAtkTrack == lastAtkTrack and lastAtk[SUIT_DIED_COL] & 1 << position and self.__attackHasHit(currAtk, suit=0):
            if self.notify.getDebug():
                self.notify.debug('Clearing suit died for ' + str(tgt.getDoId()) + ' at position ' + str(position) + ' from toon attack ' + str(lastAtk[TOON_ID_COL]) + ' and setting it for ' + str(currAtk[TOON_ID_COL]))
            lastAtk[SUIT_DIED_COL] = lastAtk[SUIT_DIED_COL] ^ 1 << position
            self.suitLeftBattle(tgt.getDoId())
            self.__removeLured(tgt)
            currAtk[SUIT_DIED_COL] = currAtk[SUIT_DIED_COL] | 1 << position

    def __addDmgToBonuses(self, dmg, attackIndex, hp = 1):
        toonId = self.toonAtkOrder[attackIndex]
        attack = self.battle.toonAttacks[toonId]
        atkTrack = self.__getActualTrack(attack)
        if atkTrack == HEAL or atkTrack == PETSOS:
            return
        tgts = self.__createToonTargetList(toonId)
        for currTgt in tgts:
            tgtPos = self.battle.activeSuits.index(currTgt)
            attackerId = self.toonAtkOrder[attackIndex]
            attack = self.battle.toonAttacks[attackerId]
            track = self.__getActualTrack(attack)
            if hp:
                if track in self.hpBonuses[tgtPos]:
                    self.hpBonuses[tgtPos][track].append([attackIndex, dmg])
                else:
                    self.hpBonuses[tgtPos][track] = [[attackIndex, dmg]]
            elif self.__suitIsLured(currTgt.getDoId()):
                if track in self.kbBonuses[tgtPos]:
                    self.kbBonuses[tgtPos][track].append([attackIndex, dmg])
                else:
                    self.kbBonuses[tgtPos][track] = [[attackIndex, dmg]]

    def __clearBonuses(self, hp = 1):
        if hp:
            self.hpBonuses = [{},
             {},
             {},
                              {},
                              {},
             {}]
        else:
            self.kbBonuses = [{},
             {},
             {},
                              {},
                              {},
             {}]

    def __bonusExists(self, tgtSuit, hp = 1):
        tgtPos = self.activeSuits.index(tgtSuit)
        if hp:
            bonusLen = len(self.hpBonuses[tgtPos])
        else:
            bonusLen = len(self.kbBonuses[tgtPos])
        if bonusLen > 0:
            return 1
        return 0

    def __processBonuses(self, hp = 1):
        if hp:
            bonusList = self.hpBonuses
            self.notify.debug('Processing hpBonuses: ' + repr(self.hpBonuses))
        else:
            bonusList = self.kbBonuses
            self.notify.debug('Processing kbBonuses: ' + repr(self.kbBonuses))
        tgtPos = 0
        for currTgt in bonusList:
            for currAtkType in currTgt.keys():
                if len(currTgt[currAtkType]) > 1 or not hp and len(currTgt[currAtkType]) > 0:
                    totalDmgs = 0
                    for currDmg in currTgt[currAtkType]:
                        totalDmgs += currDmg[1]

                    numDmgs = len(currTgt[currAtkType])
                    attackIdx = currTgt[currAtkType][numDmgs - 1][0]
                    attackerId = self.toonAtkOrder[attackIdx]
                    attack = self.battle.toonAttacks[attackerId]
                    atkTrack = self.__getActualTrack(attack)
                    if hp:
                        suit = self.battle.activeSuits[tgtPos].doId
                        if self.suitHasCondition(suit, 'kbImmune'):
                            attack[TOON_HPBONUS_COL] = 0
                        elif atkTrack == DROP:
                            attack[TOON_HPBONUS_COL] = math.ceil(totalDmgs * (DamageBonusesDrop[numDmgs - 1] * 0.01))
                        elif atkTrack == ZAP:
                            attack[TOON_HPBONUS_COL] = 0
                        elif atkTrack == SOUND:
                            attack[TOON_HPBONUS_COL] = 0
                        else:
                            attack[TOON_HPBONUS_COL] = math.ceil(totalDmgs * (DamageBonuses[numDmgs - 1] * 0.01))
                        if self.notify.getDebug():
                            self.notify.debug(
                                'Applying hp bonus to track ' + str(attack[TOON_TRACK_COL]) + ' of ' + str(
                                    attack[TOON_HPBONUS_COL]))
                    elif len(attack[TOON_KBBONUS_COL]) > tgtPos:
                        lureKBValue = 0
                        suit = self.battle.activeSuits[tgtPos].doId
                        if self.suitHasCondition(suit, 'lured'):
                            lureKBValue = self.getSuitConditionModifier(suit, 'lured') * 0.01
                            self.setSuitCondition(suit, 'lured', 0, 0, 'none')
                        attack[TOON_KBBONUS_COL][tgtPos] = totalDmgs * (lureKBValue / 2)
                        if self.notify.getDebug():
                            self.notify.debug(
                                'Applying kb bonus to track ' + str(attack[TOON_TRACK_COL]) + ' of ' + str(
                                    attack[TOON_KBBONUS_COL][tgtPos]) + ' to target ' + str(tgtPos))
                    else:
                        self.notify.warning('invalid tgtPos for knock back bonus: %d' % tgtPos)

            tgtPos += 1

        if hp:
            self.__clearBonuses()
        else:
            self.__clearBonuses(hp=0)

    def __handleBonus(self, attackIdx, hp = 1):
        attackerId = self.toonAtkOrder[attackIdx]
        attack = self.battle.toonAttacks[attackerId]
        atkDmg = self.__attackDamage(attack, suit=0)
        atkTrack = self.__getActualTrack(attack)
        if atkDmg > 0:
            if hp:
                if atkTrack != LURE:
                    self.notify.debug('Adding dmg of ' + str(atkDmg) + ' to hpBonuses list')
                    self.__addDmgToBonuses(atkDmg, attackIdx)
            elif self.__knockBackAtk(attackerId, toon=1):
                self.notify.debug('Adding dmg of ' + str(atkDmg) + ' to kbBonuses list')
                self.__addDmgToBonuses(atkDmg, attackIdx, hp=0)

    def __clearAttack(self, attackIdx, toon = 1):
        if toon:
            if self.notify.getDebug():
                self.notify.debug('clearing out toon attack for toon ' + str(attackIdx) + '...')
            attack = self.battle.toonAttacks[attackIdx]
            self.battle.toonAttacks[attackIdx] = getToonAttack(attackIdx)
            longest = max(len(self.battle.activeToons), len(self.battle.activeSuits))
            taList = self.battle.toonAttacks
            for j in xrange(longest):
                taList[attackIdx][TOON_HP_COL].append(-1)
                taList[attackIdx][TOON_KBBONUS_COL].append(-1)

            if self.notify.getDebug():
                self.notify.debug('toon attack is now ' + repr(self.battle.toonAttacks[attackIdx]))
        else:
            self.notify.warning('__clearAttack not implemented for suits!')

    def __rememberToonAttack(self, suitId, toonId, damage):
        if not suitId in self.SuitAttackers:
            self.SuitAttackers[suitId] = {toonId: damage}
        elif not toonId in self.SuitAttackers[suitId]:
            self.SuitAttackers[suitId][toonId] = damage
        elif self.SuitAttackers[suitId][toonId] <= damage:
            self.SuitAttackers[suitId] = [toonId, damage]

    def __postProcessToonAttacks(self):
        self.notify.debug('__postProcessToonAttacks()')
        lastTrack = -1
        lastAttacks = []
        self.__clearBonuses()
        for currToonAttack in self.toonAtkOrder:
            if currToonAttack != -1:
                attack = self.battle.toonAttacks[currToonAttack]
                atkTrack, atkLevel = self.__getActualTrackLevel(attack)
                if atkTrack != HEAL and atkTrack != SOS and atkTrack != NO_ATTACK and atkTrack != NPCSOS and atkTrack != PETSOS:
                    targets = self.__createToonTargetList(currToonAttack)
                    allTargetsDead = 1
                    for currTgt in targets:
                        damageDone = self.__attackDamage(attack, suit=0)
                        if damageDone > 0:
                            self.__rememberToonAttack(currTgt.getDoId(), attack[TOON_ID_COL], damageDone)
                        if atkTrack == TRAP:
                            if currTgt.doId in self.traps:
                                trapInfo = self.traps[currTgt.doId]
                                currTgt.battleTrap = trapInfo[0]
                        targetDead = 0
                        if currTgt.getHP() > 0:
                            allTargetsDead = 0
                        else:
                            targetDead = 1
                            if atkTrack != LURE:
                                for currLastAtk in lastAttacks:
                                    self.__clearTgtDied(currTgt, currLastAtk, attack)

                        tgtId = currTgt.getDoId()
                        if tgtId in self.successfulLures and atkTrack == LURE:
                            lureInfo = self.successfulLures[tgtId]
                            self.notify.debug('applying lure data: ' + repr(lureInfo))
                            toonId = lureInfo[0]
                            lureAtk = self.battle.toonAttacks[toonId]
                            tgtPos = self.battle.activeSuits.index(currTgt)
                            if currTgt.doId in self.traps:
                                trapInfo = self.traps[currTgt.doId]
                                if trapInfo[0] == UBER_GAG_LEVEL_INDEX:
                                    self.notify.debug('train trap triggered for %d' % currTgt.doId)
                                    self.trainTrapTriggered = True
                            self.__removeSuitTrap(tgtId)
                            lureAtk[TOON_KBBONUS_COL][tgtPos] = KBBONUS_TGT_LURED
                            lureAtk[TOON_HP_COL][tgtPos] = lureInfo[3]
                        elif self.__suitIsLured(tgtId) and atkTrack == DROP:
                            self.notify.debug('Drop on lured suit, ' + 'indicating with KBBONUS_COL ' + 'flag')
                            tgtPos = self.battle.activeSuits.index(currTgt)
                            attack[TOON_KBBONUS_COL][tgtPos] = KBBONUS_LURED_FLAG
                        if targetDead and atkTrack != lastTrack:
                            tgtPos = self.battle.activeSuits.index(currTgt)
                            attack[TOON_HP_COL][tgtPos] = 0
                            attack[TOON_KBBONUS_COL][tgtPos] = -1

                    if allTargetsDead and atkTrack != lastTrack:
                        if self.notify.getDebug():
                            self.notify.debug('all targets of toon attack ' + str(currToonAttack) + ' are dead')
                        self.__clearAttack(currToonAttack, toon=1)
                        attack = self.battle.toonAttacks[currToonAttack]
                        atkTrack, atkLevel = self.__getActualTrackLevel(attack)
                damagesDone = self.__applyToonAttackDamages(currToonAttack)
                self.__applyToonAttackDamages(currToonAttack, hpbonus=1)
                if atkTrack != LURE and atkTrack != DROP and atkTrack != SOUND:
                    self.__applyToonAttackDamages(currToonAttack, kbbonus=1)
                if lastTrack != atkTrack:
                    lastAttacks = []
                    lastTrack = atkTrack
                lastAttacks.append(attack)
                if self.itemIsCredit(atkTrack, atkLevel):
                    if atkTrack == TRAP or atkTrack == LURE:
                        pass
                    elif atkTrack == HEAL:
                        if damagesDone != 0:
                            self.__addAttackExp(attack)
                    else:
                        self.__addAttackExp(attack)

        if self.trainTrapTriggered:
            for suit in self.battle.activeSuits:
                suitId = suit.doId
                self.__removeSuitTrap(suitId)
                suit.battleTrap = NO_TRAP
                self.notify.debug('train trap triggered, removing trap from %d' % suitId)

        if self.notify.getDebug():
            for currToonAttack in self.toonAtkOrder:
                attack = self.battle.toonAttacks[currToonAttack]
                self.notify.debug('Final Toon attack: ' + str(attack))

    def __allTargetsDead(self, attackIdx, toon = 1):
        allTargetsDead = 1
        if toon:
            targets = self.__createToonTargetList(attackIdx)
            for currTgt in targets:
                if currTgt.getHp() > 0:
                    allTargetsDead = 0
                    break

        else:
            self.notify.warning('__allTargetsDead: suit ver. not implemented!')
        return allTargetsDead

    def __clearLuredSuitsByAttack(self, toonId, kbBonusReq = 0, targetId = -1):
        if self.notify.getDebug():
            self.notify.debug('__clearLuredSuitsByAttack')
        if targetId != -1 and self.__suitIsLured(t.getDoId()):
            self.__removeLured(t.getDoId())
        else:
            tgtList = self.__createToonTargetList(toonId)
            for t in tgtList:
                if self.__suitIsLured(t.getDoId()) and (not kbBonusReq or self.__bonusExists(t, hp=0)):
                    self.__removeLured(t.getDoId())
                    if self.notify.getDebug():
                        self.notify.debug('Suit %d stepping from lured spot' % t.getDoId())
                else:
                    self.notify.debug('Suit ' + str(t.getDoId()) + ' not found in currently lured suits')

    def __clearLuredSuitsDelayed(self):
        if self.notify.getDebug():
            self.notify.debug('__clearLuredSuitsDelayed')
        for t in self.delayedUnlures:
            if self.__suitIsLured(t):
                self.__removeLured(t)
                if self.notify.getDebug():
                    self.notify.debug('Suit %d stepping back from lured spot' % t)
            else:
                self.notify.debug('Suit ' + str(t) + ' not found in currently lured suits')

        self.delayedUnlures = []

    def __addLuredSuitsDelayed(self, toonId, targetId = -1, ignoreDamageCheck = False):
        if self.notify.getDebug():
            self.notify.debug('__addLuredSuitsDelayed')
        if targetId != -1:
            self.delayedUnlures.append(targetId)
        else:
            tgtList = self.__createToonTargetList(toonId)
            for t in tgtList:
                if self.__suitIsLured(t.getDoId()) and t.getDoId() not in self.delayedUnlures and (self.__attackDamageForTgt(self.battle.toonAttacks[toonId], self.battle.activeSuits.index(t), suit=0) > 0 or ignoreDamageCheck):
                    self.delayedUnlures.append(t.getDoId())

    def __calculateToonAttacks(self):
        self.notify.debug('__calculateToonAttacks()')
        self.__clearBonuses(hp=0)
        currTrack = None
        self.notify.debug('Traps: ' + str(self.traps))
        maxSuitLevel = 0
        for cog in self.battle.activeSuits:
            maxSuitLevel = max(maxSuitLevel, cog.getActualLevel())

        self.creditLevel = maxSuitLevel
        for toonId in self.toonAtkOrder:
            if self.__combatantDead(toonId, toon=1):
                if self.notify.getDebug():
                    self.notify.debug("Toon %d is dead and can't attack" % toonId)
                continue
            attack = self.battle.toonAttacks[toonId]
            atkTrack = self.__getActualTrack(attack)
            if atkTrack != NO_ATTACK and atkTrack != SOS and atkTrack != NPCSOS:
                if self.notify.getDebug():
                    self.notify.debug('Calculating attack for toon: %d' % toonId)
                if SUITS_UNLURED_IMMEDIATELY:
                    if currTrack and atkTrack != currTrack:
                        self.__clearLuredSuitsDelayed()
                currTrack = atkTrack
                self.__calcToonAtkHp(toonId)
                attackIdx = self.toonAtkOrder.index(toonId)
                self.__handleBonus(attackIdx, hp=0)
                self.__handleBonus(attackIdx, hp=1)
                lastAttack = self.toonAtkOrder.index(toonId) >= len(self.toonAtkOrder) - 1
                unlureAttack = self.__attackHasHit(attack, suit=0) and self.__unlureAtk(toonId, toon=1)
                if unlureAttack:
                    if lastAttack:
                        self.__clearLuredSuitsByAttack(toonId)
                    else:
                        self.__addLuredSuitsDelayed(toonId)
                if lastAttack:
                    self.__clearLuredSuitsDelayed()

        self.__processBonuses(hp=0)
        self.__processBonuses(hp=1)
        self.__postProcessToonAttacks()

    def __knockBackAtk(self, attackIndex, toon = 1):
        if toon and (self.battle.toonAttacks[attackIndex][TOON_TRACK_COL] == THROW or self.battle.toonAttacks[attackIndex][TOON_TRACK_COL] == SQUIRT):
            if self.notify.getDebug():
                self.notify.debug('attack is a knockback')
            return 1
        return 0

    def __unlureAtk(self, attackIndex, toon = 1):
        attack = self.battle.toonAttacks[attackIndex]
        track = self.__getActualTrack(attack)
        if toon and (track == THROW or track == SQUIRT or track == SOUND or track == ZAP):
            if self.notify.getDebug():
                self.notify.debug('attack is an unlure')
            return 1
        return 0

    def __calcSuitAtkType(self, theSuit):
        attacks = SuitBattleGlobals.SuitAttributes[theSuit.dna.name]['attacks']
        atk = SuitBattleGlobals.pickSuitAttack(attacks, theSuit.getLevel())
        if theSuit.dna.name == 'lit':
            currentBossHealth = -1
            for s in self.battle.suits:
                if s.dna.name == 'ste' or s.dna.name == 'scg' or s.dna.name == 'csm':
                    currentBossHealth = s.currHP
            if currentBossHealth == -1 and not self.suitHasCondition(theSuit.doId, 'desperation'):
                self.setSuitCondition(theSuit.doId, 'desperation', 1, 100, 'setBoth')
        if theSuit.dna.name == 'ste':
            currentBossHealth = -1
            for s in self.battle.suits:
                if s.dna.name == 'scg' or s.dna.name == 'lit' or s.dna.name == 'csm':
                    currentBossHealth = s.currHP
            if currentBossHealth == -1 and not self.suitHasCondition(theSuit.doId, 'desperation'):
                self.setSuitCondition(theSuit.doId, 'desperation', 1, 100, 'setBoth')
        if theSuit.dna.name == 'csm':
            currentBossHealth = -1
            for s in self.battle.suits:
                if s.dna.name == 'ste' or s.dna.name == 'lit' or s.dna.name == 'scg':
                    currentBossHealth = s.currHP
            if currentBossHealth == -1 and not self.suitHasCondition(theSuit.doId, 'desperation'):
                self.setSuitCondition(theSuit.doId, 'desperation', 1, 100, 'setBoth')
        if theSuit.dna.name == 'scg':
            currentBossHealth = -1
            for s in self.battle.suits:
                if s.dna.name == 'ste' or s.dna.name == 'lit' or s.dna.name == 'csm':
                    currentBossHealth = s.currHP
            if currentBossHealth == -1 and not self.suitHasCondition(theSuit.doId, 'desperation'):
                self.setSuitCondition(theSuit.doId, 'desperation', 1, 100, 'setBoth')
        if theSuit.dna.name == 'cp':
            x = self.TurnsElapsed
            currentBossHealth = -1
            for s in self.battle.suits:
                if s.dna.name == 'frs' or s.dna.name == 'fbd' or s.dna.name == 'gtk':
                    currentBossHealth = s.currHP
            if currentBossHealth == -1 and not self.suitHasCondition(theSuit.doId, 'desperation'):
                self.setSuitCondition(theSuit.doId, 'desperation', 1, 100, 'setBoth')
        if theSuit.dna.name == 'fbd':
            x = self.TurnsElapsed
            currentBossHealth = -1
            for s in self.battle.suits:
                if s.dna.name == 'frs' or s.dna.name == 'cp' or s.dna.name == 'gtk':
                    currentBossHealth = s.currHP
            if currentBossHealth == -1 and not self.suitHasCondition(theSuit.doId, 'desperation'):
                self.setSuitCondition(theSuit.doId, 'desperation', 1, 100, 'setBoth')
        if theSuit.dna.name == 'frs':
            x = self.TurnsElapsed
            currentBossHealth = -1
            for s in self.battle.suits:
                if s.dna.name == 'cp' or s.dna.name == 'fbd' or s.dna.name == 'gtk':
                    currentBossHealth = s.currHP
            if currentBossHealth == -1 and not self.suitHasCondition(theSuit.doId, 'desperation'):
                self.setSuitCondition(theSuit.doId, 'desperation', 1, 100, 'setBoth')
        if theSuit.dna.name == 'gtk':
            x = self.TurnsElapsed
            currentBossHealth = -1
            for s in self.battle.suits:
                if s.dna.name == 'cp' or s.dna.name == 'fbd' or s.dna.name == 'frs':
                    currentBossHealth = s.currHP
            if currentBossHealth == -1 and not self.suitHasCondition(theSuit.doId, 'desperation'):
                self.setSuitCondition(theSuit.doId, 'desperation', 1, 100, 'setBoth')
        if theSuit.dna.name == 'dsf':
            x = self.TurnsElapsed
            if x % 99 == 0:
                return 0
            if len(self.battle.activeSuits) <= 2:
                return 0
            if len(self.battle.activeSuits) >= 6 and x % 2 == 0:
                return 6
            if x % 2 == 0:
                return random.choice((0, 1, 2, 3, 4))
            if x % 1 == 0:
                return 5
        if theSuit.dna.name == 'crf':
            if len(self.battle.activeSuits) == 1 and not self.suitHasCondition(theSuit.doId, 'phase3'):
                return 5
            if len(self.battle.activeSuits) > 1 and not self.suitHasCondition(theSuit.doId, 'phase3'):
                return random.choice((3, 4))
            if self.getSuitConditionTurns(theSuit.doId, 'vulnerablecalculator') == 1:
                return 2
            if len(self.battle.activeSuits) <= 2 and not self.suitHasCondition(theSuit.doId, 'vulnerablecalculator'):
                return 1
            if theSuit.currHP <= 38888 and not self.suitHasCondition(theSuit.doId, 'aceInTheHole'):
                return 0
            else:
                return random.choice((3, 4, 6, 7, 8, 9, 10))
        if theSuit.dna.name == 'mad':
            currentBossHealth = -1
            for s in self.battle.suits:
                if s.dna.name == 'crf':
                    currentBossHealth = s.currHP
            if theSuit.getMaxHP() > 13000:
                if currentBossHealth >= 1:
                    return 3
                else:
                    return 1
            elif theSuit.getMaxHP() > 12000:
                return random.choice((1, 2))
            elif theSuit.getMaxHP() > 11000:
                for t in self.battle.activeToons:
                    if self.toonHasCondition(t, 'cheer'):
                        return 4
                    else:
                        return 1
            elif theSuit.getMaxHP() > 10000:
                return 1
            elif theSuit.getMaxHP() > 9000:
                if self.suitHasCondition(theSuit.doId, 'soaked'):
                    return 5
                else:
                    return 1
            elif theSuit.getMaxHP() > 8000:
                return 0
            elif theSuit.getMaxHP() > 7000:
                for t in self.battle.activeToons:
                    if not self.toonHasCondition(t, 'winded'):
                        return 7
                    else:
                        return 1
            elif theSuit.getMaxHP() > 0:
                return 1
        if theSuit.dna.name == 'dvk':
            x = self.TurnsElapsed
            if x % 99 == 0:
                return 3
            currentBossHealth = -1
            for s in self.battle.suits:
                if s.dna.name == 'cry' or s.dna.name == 'tcm' or s.dna.name == 'otm':
                    currentBossHealth = s.currHP
            if currentBossHealth == -1 and not self.suitHasCondition(theSuit.doId, 'desperation'):
                self.setSuitCondition(theSuit.doId, 'desperation', 1, 100, 'setBoth')
            if self.suitHasCondition(theSuit.doId, 'costscalculator'):
                return 4
            if self.suitHasCondition(theSuit.doId, 'sanctioncalculator'):
                return 1
            if self.suitHasCondition(theSuit.doId, 'insurancecalculator'):
                return 2
            if self.suitHasCondition(theSuit.doId, 'soakedcalculator'):
                return 0
            if x % 5 == 0:
                return 2
            if x % 4 == 0:
                return 1
            if x % 3 == 0:
                return 4
        if theSuit.dna.name == 'otm':
            x = self.TurnsElapsed
            if x % 99 == 0:
                return 5
            currentBossHealth = -1
            for s in self.battle.suits:
                if s.dna.name == 'cry' or s.dna.name == 'dvk' or s.dna.name == 'tcm':
                    currentBossHealth = s.currHP
            if currentBossHealth == -1 and not self.suitHasCondition(theSuit.doId, 'desperation'):
                self.setSuitCondition(theSuit.doId, 'desperation', 1, 100, 'setBoth')
            if theSuit.currHP <= 7375 and not self.suitHasCondition(theSuit.doId, 'phase2'):
                return 3
            if self.suitHasCondition(theSuit.doId, 'costscalculator') and not self.suitHasCondition(theSuit.doId, 'desperation'):
                return random.choice((0, 1))
            if self.suitHasCondition(theSuit.doId, 'insurancecalculator'):
                return 2
            if self.suitHasCondition(theSuit.doId, 'costscalculator'):
                return 1
            if self.suitHasCondition(theSuit.doId, 'sanctioncalculator'):
                return 4
            if x % 5 == 0:
                return 2
            if x % 3 == 0 and not self.suitHasCondition(theSuit.doId, 'desperation'):
                return random.choice((0, 1))
            if x % 3 == 0:
                return 1
        if theSuit.dna.name == 'cry':
            x = self.TurnsElapsed
            if x % 99 == 0:
                return 7
            currentBossHealth = -1
            for s in self.battle.suits:
                if s.dna.name == 'tcm' or s.dna.name == 'dvk' or s.dna.name == 'otm':
                    currentBossHealth = s.currHP
            if currentBossHealth == -1 and not self.suitHasCondition(theSuit.doId, 'desperation'):
                self.setSuitCondition(theSuit.doId, 'desperation', 1, 100, 'setBoth')
            if theSuit.currHP <= 10500 and not self.suitHasCondition(theSuit.doId, 'phase2') and not self.suitHasCondition(theSuit.doId, 'phase3'):
                return 2
            if theSuit.currHP <= 3750 and not self.suitHasCondition(theSuit.doId, 'phase3'):
                return 3
            if self.suitHasCondition(theSuit.doId, 'costscalculator') and self.suitHasCondition(theSuit.doId, 'phase2'):
                return 9
            if self.suitHasCondition(theSuit.doId, 'costscalculator') and not self.suitHasCondition(theSuit.doId, 'phase2'):
                return 4
            if len(self.battle.activeSuits) >= 6 and x % 2 == 0 and self.suitHasCondition(theSuit.doId, 'phase2'):
                return 8
            if self.suitHasCondition(theSuit.doId, 'sanctioncalculator') and self.suitHasCondition(theSuit.doId, 'phase2') and len(self.battle.activeSuits) >= 3:
                return random.choice((0, 1))
            #if self.suitHasCondition(theSuit.doId, 'sanctioncalculator') and not self.suitHasCondition(theSuit.doId, 'phase2'):
                #return 6
            if len(self.battle.activeSuits) >= 3 and x % 4 == 0 and self.suitHasCondition(theSuit.doId, 'phase2'):
                return random.choice((0, 1))
            if x % 5 == 0 and not self.suitHasCondition(theSuit.doId, 'phase2'):
                return 5
            #if x % 4 == 0 and not self.suitHasCondition(theSuit.doId, 'phase2'):
                #return 6
            if x % 3 == 0 and self.suitHasCondition(theSuit.doId, 'phase2'):
                return 9
            if x % 3 == 0 and not self.suitHasCondition(theSuit.doId, 'phase2'):
                return 4
        if theSuit.dna.name == 'tcm':
            x = self.TurnsElapsed
            if x % 99 == 0:
                return 9
            currentBossHealth = -1
            for s in self.battle.suits:
                if s.dna.name == 'cry' or s.dna.name == 'dvk' or s.dna.name == 'otm':
                    currentBossHealth = s.currHP
            if currentBossHealth == -1 and not self.suitHasCondition(theSuit.doId, 'desperation'):
                self.setSuitCondition(theSuit.doId, 'desperation', 1, 100, 'setBoth')
            if theSuit.currHP <= 8375 and not self.suitHasCondition(theSuit.doId, 'phase2'):
                return 6
            if x % 3 == 0 and self.suitHasCondition(theSuit.doId, 'phase2') and len(self.battle.activeSuits) >= 4:
                return 0
            if x % 5 == 0 and len(self.battle.activeSuits) >= 4:
                return 0
            if x % 4 == 0:
                return 5
            if self.suitHasCondition(theSuit.doId, 'soakedcalculator'):
                return 4
            if self.suitHasCondition(theSuit.doId, 'markedcalculator'):
                return 1
            if self.suitHasCondition(theSuit.doId, 'dropcalculator'):
                return 7
            if self.suitHasCondition(theSuit.doId, 'zapcalculator'):
                return 8
            if self.suitHasCondition(theSuit.doId, 'trapcalculator'):
                return 3
            for t in self.battle.activeToons:
                if self.toonHasCondition(t, 'cheer'):
                    return 2
        if theSuit.dna.name == 'blr':
            x = self.TurnsElapsed
            if x % 99 == 0:
                return 0
            currentBossHealth = -1
            for s in self.battle.suits:
                if s.dna.name == 'dsk' or s.dna.name == 'dvp' or s.dna.name == 'ffm':
                    currentBossHealth = s.currHP
            if currentBossHealth == -1 and not self.suitHasCondition(theSuit.doId, 'desperation'):
                self.setSuitCondition(theSuit.doId, 'desperation', 1, 100, 'setBoth')
            if self.suitHasCondition(theSuit.doId, 'soakedcalculator'):
                return 1
            if self.suitHasCondition(theSuit.doId, 'costscalculator'):
                return 2
            if x % 4 == 0:
                return 2
            if x % 3 == 0:
                return 0
        if theSuit.dna.name == 'dvp':
            x = self.TurnsElapsed
            if x % 99 == 0:
                return random.choice((0, 2, 3, 4))
            currentBossHealth = -1
            for s in self.battle.suits:
                if s.dna.name == 'dsk' or s.dna.name == 'ffm' or s.dna.name == 'blr':
                    currentBossHealth = s.currHP
            if currentBossHealth == -1 and not self.suitHasCondition(theSuit.doId, 'desperation'):
                self.setSuitCondition(theSuit.doId, 'desperation', 1, 100, 'setBoth')
            if self.suitHasCondition(theSuit.doId, 'costscalculator'):
                return random.choice((0, 2, 3, 4))
            if x % 4 == 0:
                return 1
            if x % 3 == 0:
                return random.choice((0, 2, 3, 4))
        if theSuit.dna.name == 'dsk':
            x = self.TurnsElapsed
            if x % 99 == 0:
                return 5
            currentBossHealth2 = -1
            theSuit2 = None
            for s in self.battle.suits:
                if s.dna.name == 'blr':
                    theSuit2 = s
            currentBossHealth = -1
            for s in self.battle.suits:
                if s.dna.name == 'ffm' or s.dna.name == 'dvp' or s.dna.name == 'blr':
                    currentBossHealth = s.currHP
            if currentBossHealth == -1 and not self.suitHasCondition(theSuit.doId, 'desperation'):
                self.setSuitCondition(theSuit.doId, 'desperation', 1, 100, 'setBoth')
            if theSuit2 is not None:
                if self.suitHasCondition(theSuit2.doId, 'soakedcalculator'):
                    return 6
            if self.suitHasCondition(theSuit.doId, 'insurancecalculator'):
                return 5
            if self.suitHasCondition(theSuit.doId, 'costscalculator'):
                return 7
            if self.suitHasCondition(theSuit.doId, 'marked'):
                return 4
            if len(self.battle.activeSuits) >= 4 and x % 2 == 0:
                return random.choice((0, 1))
            if x % 5 == 0:
                return 3
            if x % 4 == 0:
                return 5
            if x % 3 == 0:
                return 7
        if theSuit.dna.name == 'ffm':
            x = self.TurnsElapsed
            if x % 99 == 0:
                return 2
            currentBossHealth = -1
            for s in self.battle.suits:
                if s.dna.name == 'dsk' or s.dna.name == 'dvp' or s.dna.name == 'blr':
                    currentBossHealth = s.currHP
            if currentBossHealth == -1 and not self.suitHasCondition(theSuit.doId, 'desperation'):
                self.setSuitCondition(theSuit.doId, 'desperation', 1, 100, 'setBoth')
            if self.suitHasCondition(theSuit.doId, 'costscalculator'):
                return random.choice((1, 2))
            if self.suitHasCondition(theSuit.doId, 'sanctioncalculator') and len(self.battle.activeSuits) >= 4:
                return 0
            if x % 3 == 0:
                return random.choice((1, 2))
        currentBossHealth = -1
        for s in self.battle.suits:
            if s.dna.name == 'csm':
                currentBossHealth = s.currHP
        if currentBossHealth == -1 and self.suitHasCondition(theSuit.doId, 'insured'):
            self.setSuitCondition(theSuit.doId, 'insured', 0, 0, 'setBoth')
        return atk

    def __calcSuitTarget(self, attack):
        targets = []
        # Get the amount of Toons we are targeting and make sure it isn't more than the number of currently existing Toons.
        atkType = attack[SUIT_ATK_COL]
        theSuit = self.battle.findSuit(attack[SUIT_ID_COL])
        atkInfo = SuitBattleGlobals.getSuitAttack(theSuit.dna.name, theSuit.getLevel(), atkType)
        if self.__suitAtkAffectsGroup(attack):
            toonCount = len(self.battle.activeToons)
        else:
            toonCount = min(len(self.battle.activeToons),
                            2 if atkInfo['group'] == SuitBattleGlobals.ATK_TGT_DOUBLE else 1)
        suitId = attack[SUIT_ID_COL]
        for i in xrange(0, toonCount):
            if suitId in self.SuitAttackers and random.randint(0, 99) < 75:
                totalDamage = 0
                for currToon in self.SuitAttackers[suitId].keys():
                    totalDamage += self.SuitAttackers[suitId][currToon]

                dmgs = []
                for currToon in self.SuitAttackers[suitId].keys():
                    dmgs.append(self.SuitAttackers[suitId][currToon] / totalDamage * 100)

                dmgIdx = SuitBattleGlobals.pickFromFreqList(dmgs)
                if dmgIdx == None:
                    toonId = self.__pickRandomToon(suitId)
                else:
                    toonId = self.SuitAttackers[suitId].keys()[dmgIdx]
                if toonId == -1 or toonId not in self.battle.activeToons:
                    continue
                self.notify.debug('Suit attacking back at toon ' + str(toonId))
                chosen = self.battle.activeToons.index(toonId)
            else:
                chosen = self.__pickRandomToon(suitId)
            while chosen in targets:
                chosen = self.__pickRandomToon(suitId)
            targets.append(chosen)

        return targets

    def __calcSuitTargetALT(self, attack):
        targets = []
        # Get the amount of Toons we are targeting and make sure it isn't more than the number of currently existing Toons.
        atkType = attack[SUIT_ATK_COL]
        theSuit = self.battle.findSuit(attack[SUIT_ID_COL])
        atkInfo = SuitBattleGlobals.getSuitAttack(theSuit.dna.name, theSuit.getLevel(), atkType)
        toonCount = len(self.battle.activeToons)
        suitId = attack[SUIT_ID_COL]
        chosen = self.__pickRandomToon(suitId)
        targets.append(chosen)

        return targets

    def __pickRandomToon(self, suitId):
        liveToons = []
        for currToon in self.battle.activeToons:
            if not self.__combatantDead(currToon, toon=1):
                liveToons.append(self.battle.activeToons.index(currToon))

        if len(liveToons) == 0:
            self.notify.debug('No tgts avail. for suit ' + str(suitId))
            return -1
        chosen = random.choice(liveToons)
        self.notify.debug('Suit randomly attacking toon ' + str(self.battle.activeToons[chosen]))
        return chosen

    def __suitAtkHit(self, suitId, atkType):
        if self.suitsAlwaysHit:
            return True
        elif self.suitsAlwaysMiss:
            return False
        theSuit = self.battle.findSuit(suitId)
        atkInfo = SuitBattleGlobals.getSuitAttack(theSuit.dna.name, theSuit.getLevel(), atkType)
        atkAcc = atkInfo['acc']
        suitAcc = SuitBattleGlobals.SuitAttributes[theSuit.dna.name]['acc'][theSuit.getLevel()]
        acc = atkAcc
        randChoice = random.randint(0, 99)
        if self.notify.getDebug():
            self.notify.debug('Suit attack rolled ' + str(randChoice) + ' to hit with an accuracy of ' + str(
                acc) + ' (attackAcc: ' + str(atkAcc) + ' suitAcc: ' + str(suitAcc) + ')')
        if randChoice < acc:
            return True
        return False

    def __suitAtkAffectsGroup(self, attack):
        atkType = attack[SUIT_ATK_COL]
        theSuit = self.battle.findSuit(attack[SUIT_ID_COL])
        atkInfo = SuitBattleGlobals.getSuitAttack(theSuit.dna.name, theSuit.getLevel(), atkType)
        return atkInfo['group'] == SuitBattleGlobals.ATK_TGT_GROUP

    def __createSuitTargetList(self, attack):
        targetList = []
        if attack[SUIT_ATK_COL] == NO_ATTACK:
            self.notify.debug('No attack, no targets')
            return targetList
        debug = self.notify.getDebug()
        if not self.__suitAtkAffectsGroup(attack):
            if debug:
                self.notify.debug('Suit attack is single or double target')
            for currToon in attack[SUIT_TGT_COL]:
                if debug:
                    self.notify.debug('Suit attack will target toon' + str(currToon))
                targetList.append(self.battle.activeToons[currToon])

        else:
            if debug:
                self.notify.debug('Suit attack is group target')
            for currToon in self.battle.activeToons:
                if debug:
                    self.notify.debug('Suit attack will target toon' + str(currToon))
                targetList.append(currToon)

        return targetList

    def __calcSuitAtkHp(self, attack):
        targetList = self.__createSuitTargetList(attack)
        for currTarget in xrange(len(targetList)):
            toonId = targetList[currTarget]
            toon = self.battle.getToon(toonId)
            result = 0
            theSuit = self.battle.findSuit(attack[SUIT_ID_COL])
            atkType = attack[SUIT_ATK_COL]
            atkInfo = SuitBattleGlobals.getSuitAttack(theSuit.dna.name, theSuit.getLevel(), atkType)
            if toon and toon.immortalMode:
                result = 1
            elif TOONS_TAKE_NO_DAMAGE:
                result = 0
            elif self.__suitAtkHit(attack[SUIT_ID_COL], attack[SUIT_ATK_COL]):
                atkType = attack[SUIT_ATK_COL]
                theSuit = self.battle.findSuit(attack[SUIT_ID_COL])
                atkInfo = SuitBattleGlobals.getSuitAttack(theSuit.dna.name, theSuit.getLevel(), atkType)
                mult = 1.0
                result = int(atkInfo['hp'] * mult)
                if theSuit.getExecutive():
                    result = int(result * ToontownBattleGlobals.EXECUTIVE_DMG_MULT)
                elif theSuit.getGovernaught():
                    result = int(result * ToontownBattleGlobals.GOVERNAUGHT_DMG_MULT)
            targetIndex = self.battle.activeToons.index(toonId)
            if atkInfo['name'] == 'Coalescence':
                if toon.getHp() == 1:
                    attack[SUIT_HP_COL][targetIndex] = 1
                else:
                    attack[SUIT_HP_COL][targetIndex] = toon.getHp() - 1
                theSuit.setHP(int(
                    theSuit.currHP + ToontownBattleGlobals.HUSTLER_COALESCENCE_HEAL_BASE + attack[SUIT_HP_COL][
                        targetIndex] * ToontownBattleGlobals.HUSTLER_COALESCENCE_HEAL_AMP))
            elif atkInfo['suitName'] == 'hst' and atkInfo['name'] == 'ShadowWave':
                if self.toonHasCondition(toonId, 'corruption'):
                    attack[SUIT_HP_COL][targetIndex] = 7 + int(
                        floor(self.getToonConditionModifier(toonId, 'corruption') / 4.0) * 7)
            elif atkInfo['name'] == 'UH':
                attack[SUIT_HP_COL][targetIndex] = 30
                if self.toonHasCondition(toonId, 'corruption'):
                    attack[SUIT_HP_COL][targetIndex] = 7 + int(floor(self.getToonConditionModifier(toonId, 'corruption') / 4.0) * 7)
            elif atkInfo['name'] == 'Gavel': #scapegoat bite into gavel
                result = 40
                attack[SUIT_HP_COL][targetIndex] = result
                for s in self.battle.suits:
                    if s.dna.name == 'lit':
                        currentBossHealth = s.currHP
                        if currentBossHealth >= 1:
                            self.setToonCondition(toon.doId, 'snapped', .2, 3, 'setBoth')
                self.setToonCondition(toon.doId, 'noGags', 1, 2, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'gavelcalculator', 0, 0, 'setBoth')
                from toontown.suit.DistributedLawbotBossAI import DistributedLawbotBossAI

                boss = None
                for do in simbase.air.doId2do.values():
                    if isinstance(do, DistributedLawbotBossAI):
                        for toon in self.battle.activeToons:
                            if toon in do.involvedToons:
                                boss = do
                                break
                if len(self.battle.activeSuits) < 6:
                    boss.appendSuitsToBattle(boss.battleNumber, 'lit')
            elif atkInfo['name'] == 'Cage':
                result = 60
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'noGags', 1, 2, 'setBoth')
                self.setToonCondition(toon.doId, 'noSOS', 1, 2, 'setBoth')
                self.setToonCondition(toon.doId, 'noFires', 1, 2, 'setBoth')
                self.setToonCondition(toon.doId, 'noUnites', 1, 2, 'setBoth')
            elif atkInfo['name'] == 'InkDrain':
                result = 35
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'noGags', 1, 2, 'setBoth')
                self.setToonCondition(toon.doId, 'noSOS', 1, 2, 'setBoth')
                self.setToonCondition(toon.doId, 'noFires', 1, 2, 'setBoth')
                self.setToonCondition(toon.doId, 'noUnites', 1, 2, 'setBoth')
            elif atkInfo['name'] == 'WheelSpin':
                result = 35
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'noGags', 1, 2, 'setBoth')
            elif atkInfo['name'] == 'BookKeeping':
                result = 70
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'noGags', 1, 2, 'setBoth')
                self.setToonCondition(toon.doId, 'noSOS', 1, 2, 'setBoth')
                self.setToonCondition(toon.doId, 'noFires', 1, 2, 'setBoth')
                self.setToonCondition(toon.doId, 'noUnites', 1, 2, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'soakedcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'soakedcalculator2', 1, 10, 'setBoth')
            elif atkInfo['name'] == 'CourtMandate2':
                result = 43
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'shielding', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'soakImmune', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'syphon', 1, 10, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'lureImmune', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'CourtMandate3':
                result = random.randint(15, 40)
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'shielding', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'soakImmune', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'syphon', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'lureImmune', 1, 10, 'setBoth')
                self.setToonCondition(toon.doId, 'corruption', .4, 3, 'setBoth')
            elif atkInfo['name'] == 'CourtMandate1':
                result = 66
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'shielding', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'soakImmune', 1, 10, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'syphon', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'lureImmune', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'CourtMandate':
                result = 78
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'shielding', 1, 10, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'soakImmune', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'lureImmune', 0, 0, 'setBoth')
                for suit in self.battle.activeSuits:
                    self.setSuitCondition(suit.doId, 'syphon', 1, 99, 'setBoth')
            elif atkInfo['name'] == 'Snap2':
                result = 58.3
                attack[SUIT_HP_COL][targetIndex] = result
                currentBossHealth = -1
                for s in self.battle.suits:
                    if s.dna.name == 'ste':
                        currentBossHealth = s.currHP
                if currentBossHealth >= 1:
                    self.setToonCondition(toon.doId, 'snapped', .4, 3, 'setBoth')
                else:
                    self.setToonCondition(toon.doId, 'snapped', .2, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'snappedcalculator', 0, 0, 'setBoth')
                from toontown.suit.DistributedLawbotBossAI import DistributedLawbotBossAI

                boss = None
                for do in simbase.air.doId2do.values():
                    if isinstance(do, DistributedLawbotBossAI):
                        for toon in self.battle.activeToons:
                            if toon in do.involvedToons:
                                boss = do
                                break
                if len(self.battle.activeSuits) < 6:
                    boss.appendSuitsToBattle(boss.battleNumber, 'lit')
            elif atkInfo['name'] == 'Snap': #soaked snap
                result = 81.5
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'snapped', .1, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'soakedcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'soakedcalculator2', 1, 10, 'setBoth')
                # from toontown.suit.DistributedLawbotBossAI import DistributedLawbotBossAI

                # boss = None
                # for do in simbase.air.doId2do.values():
                # if isinstance(do, DistributedLawbotBossAI):
                # for toon in self.battle.activeToons:
                # if toon in do.involvedToons:
                # boss = do
                # break
                # if len(self.battle.activeSuits) < 4 and not self.suitHasCondition(theSuit.doId, 'desperation'):
                # boss.appendSuitsToBattle(boss.battleNumber, 'lit')
                # elif len(self.battle.activeSuits) < 6 and self.suitHasCondition(theSuit.doId, 'desperation'):
                # boss.appendSuitsToBattle(boss.battleNumber, 'lit')
            elif atkInfo['name'] == 'CollectCall':
                result = 50
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'corruption', .4, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'vulnerable', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'collectcallcalculator', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'Caress':
                result = random.randint(15, 40)
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'corruption', .4, 3, 'setBoth')
            elif atkInfo['name'] == 'CourtRecord1':
                result = random.randint(15, 40)
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'corruption', .4, 3, 'setBoth')
            elif atkInfo['name'] == 'CourtRecord2':
                result = random.randint(15, 40)
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'corruption', .4, 3, 'setBoth')
            elif atkInfo['name'] == 'CourtRecord3':
                result = random.randint(15, 40)
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'corruption', .4, 3, 'setBoth')
            elif atkInfo['name'] == 'CourtRecord5':
                result = random.randint(15, 40)
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'winded', 1, 6, 'setBoth')
            elif atkInfo['name'] == 'ExplodingBill':
                result = 66
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'corruption', .25, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'explodingbillcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'papercutcalculator', 1, 10, 'setBoth')
            elif atkInfo['name'] == 'KickUp':
                result = 68
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'corruption', .1, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'soakedcalculator', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'Shakedown':
                result = 58
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'corruption', .4, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'sanctioncalculator', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'Blast':
                result = random.randint(25, 50)
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'noSOS', 1, 3, 'setBoth')
                self.setToonCondition(toon.doId, 'noFires', 1, 3, 'setBoth')
                self.setToonCondition(toon.doId, 'noUnites', 1, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'shielding', 1, 10, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'soakImmune', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'syphon', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'lureImmune', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'LegalBindings':
                result = 30
                attack[SUIT_HP_COL][targetIndex] = result
                for s in self.battle.suits:
                    if s.dna.name == 'ste':
                        currentBossHealth = s.currHP
                        if currentBossHealth >= 1:
                            self.setToonCondition(toon.doId, 'allGagBoost', -25, 3, 'setBoth')
                            self.setToonCondition(toon.doId, 'lureBoost', -25, 3, 'setBoth')
                #for s in self.battle.activeSuits:
                    #self.setSuitCondition(s.doId, 'insured', 1, 99, 'setBoth')
                self.setToonCondition(toon.doId, 'corruption', .2, 3, 'setBoth')
                self.setToonCondition(toon.doId, 'bound', 1, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'bindingscalculator', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'Quash':
                result = 75
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'snapped', .25, 99, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'aceInTheHole', 1, 99, 'setBoth')
            elif atkInfo['name'] == 'FieldPromotion':
                from toontown.suit.DistributedCashbotBossAI import DistributedCashbotBossAI

                boss = None
                for do in simbase.air.doId2do.values():
                    if isinstance(do, DistributedCashbotBossAI):
                        for toon in self.battle.activeToons:
                            if toon in do.involvedToons:
                                boss = do
                                break
                result = random.randint(25, 50)
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'allGagBoost', 1000, 99, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'immune', 1, 10, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'phase3', 1, 99, 'setBoth')
                boss.appendSuitsToBattle(boss.battleNumber, 'crf2')
            elif atkInfo['name'] == 'JuryNotice':
                result = random.randint(25, 50)
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'vulnerablecalculator', 1, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'HRdamagereduction', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'NickelAndDime':
                from toontown.suit.DistributedCashbotBossAI import DistributedCashbotBossAI

                boss = None
                for do in simbase.air.doId2do.values():
                    if isinstance(do, DistributedCashbotBossAI):
                        for toon in self.battle.activeToons:
                            if toon in do.involvedToons:
                                boss = do
                                break
                result = random.randint(25, 50)
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'allGagBoost', 1000, 99, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'vulnerablecalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'immune', 1, 10, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'phase3', 1, 99, 'setBoth')
                boss.appendSuitsToBattle(boss.battleNumber, 'crf2')
            elif atkInfo['name'] == 'FreeCruise':
                result = random.randint(25, 50)
                attack[SUIT_HP_COL][targetIndex] = result
                if self.suitHasCondition(theSuit.doId, 'phase3'):
                    self.setSuitCondition(theSuit.doId, 'HRdamagereduction', 1, 99, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'immune', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'Conduction':
                result = random.randint(25, 50)
                attack[SUIT_HP_COL][targetIndex] = result
                if self.suitHasCondition(theSuit.doId, 'phase3'):
                    self.setSuitCondition(theSuit.doId, 'HRdamagereduction', 1, 99, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'immune', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'LDQuake':
                result = random.randint(25, 50)
                attack[SUIT_HP_COL][targetIndex] = result
                for suit in self.battle.activeSuits:
                    suit.setHP(int(suit.currHP - 50))
                    self.__removeLured(suit)
                if self.suitHasCondition(theSuit.doId, 'phase3'):
                    self.setSuitCondition(theSuit.doId, 'HRdamagereduction', 1, 99, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'immune', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'LDReOrg':
                result = random.randint(25, 50)
                attack[SUIT_HP_COL][targetIndex] = result
                for suit in self.battle.activeSuits:
                    suit.setHP(int(suit.currHP - 250))
                    self.__removeLured(suit)
                if self.suitHasCondition(theSuit.doId, 'phase3'):
                    self.setSuitCondition(theSuit.doId, 'HRdamagereduction', 1, 99, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'immune', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'LDAfterShock':
                result = random.randint(25, 50)
                attack[SUIT_HP_COL][targetIndex] = result
                if self.suitHasCondition(theSuit.doId, 'phase3'):
                    self.setSuitCondition(theSuit.doId, 'HRdamagereduction', 1, 99, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'immune', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'LDRedTape':
                if self.suitHasCondition(theSuit.doId, 'phase3'):
                    self.setSuitCondition(theSuit.doId, 'HRdamagereduction', 1, 99, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'immune', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'LDEvictionNotice':
                result = random.randint(25, 50)
                attack[SUIT_HP_COL][targetIndex] = result
                if self.suitHasCondition(theSuit.doId, 'phase3'):
                    self.setSuitCondition(theSuit.doId, 'HRdamagereduction', 1, 99, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'immune', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'CloseTheLoop':
                result = 27.5
                attack[SUIT_HP_COL][targetIndex] = result
                for s in self.battle.suits:
                    if s.dna.name == 'ste':
                        currentBossHealth = s.currHP
                        if currentBossHealth >= 1:
                            self.setToonCondition(toon.doId, 'allGagBoost', -25, 3, 'setBoth')
                            self.setToonCondition(toon.doId, 'lureBoost', -25, 3, 'setBoth')
                #for s in self.battle.activeSuits:
                    #self.setSuitCondition(s, 'insured', 1, 99, 'setBoth')
                self.setToonCondition(toon.doId, 'corruption', .2, 3, 'setBoth')
                self.setToonCondition(toon.doId, 'bound', 1, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'bindingscalculator', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'Investment':
                result = 35
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'cannotDodge', 100, 2, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'cannotDodge', 100, 2, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'costscalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'sanctioncalculator', 1, 10, 'setBoth')
                for suit in self.battle.activeSuits:
                    suit.setHP(int(suit.currHP - 100))
                    if suit.currHP <= 0:
                        if suit.getSkeleRevives() >= 1:
                            suit.useSkeleRevive()
                        self.__removeLured(suit.doId)
                        if self.suitHasCondition(suit.doId, 'lured'):
                            self.setSuitCondition(suit.doId, 'lured', 0, 0, 'setBoth')
                    continue
            elif atkInfo['name'] == 'Bar':
                result = 40
                attack[SUIT_HP_COL][targetIndex] = result
                for suit in self.battle.activeSuits:
                    suit.setHP(int(suit.currHP - 250))
                    continue
            elif atkInfo['name'] == 'Synergy':
                result = (24 + (self.TurnsElapsed * 1.3))
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkInfo['name'] == 'CollectCallFees':
                result = (24 + (self.TurnsElapsed * 1.3))
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'collectcallfeescalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'collectcallcalculator', 1, 10, 'setBoth')
            elif atkInfo['name'] == 'Sitdown':
                result = (72 + (self.TurnsElapsed * 1.3))
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'allGagBoost', 100, 99, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'costscalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'sanctioncalculator', 1, 10, 'setBoth')
            elif atkInfo['name'] == 'HeavyRainfall':
                result = (48 + (self.TurnsElapsed * 1.3))
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'zapBoost', 50, 2, 'setBoth')
                self.setToonCondition(toon.doId, 'squirtBoost', 50, 2, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'costscalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'sanctioncalculator', 1, 10, 'setBoth')
            elif atkInfo['name'] == 'RadioInfrequency':
                result = 33
                self.setToonCondition(toon.doId, 'soundBoost', -50, 2, 'setBoth')
                self.setToonCondition(toon.doId, 'lureBoost', -50, 2, 'setBoth')
            elif atkInfo['name'] == 'CourtCosts':
                result = (24 + (self.TurnsElapsed * 1.3))
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'costscalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'sanctioncalculator', 1, 10, 'setBoth')
            elif atkInfo['name'] == 'UnionDues':
                result = (24 + (self.TurnsElapsed * 1.3))
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'noToonUpGags', 1, 2, 'setBoth')
                self.setToonCondition(toon.doId, 'noZapGags', 1, 2, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'costscalculator', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'LifeInsurance':
                theSuit.setHP(int(theSuit.currHP + 75))
            elif atkInfo['name'] == 'Voicemail':
                result = 41
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'immune', 1, 4, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'vulnerable', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'ManagerialProtection':
                result = 30
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'immune', 1, 4, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'refinementcalculator', 1, 10, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'vulnerable', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'WorkersCompensation':
                theSuit.setHP(int(theSuit.currHP + 50))
            elif atkInfo['name'] == 'ExtraTip':
                result = 38
                attack[SUIT_HP_COL][targetIndex] = result
                from toontown.suit.DistributedLawbotBossAI import DistributedLawbotBossAI

                boss = None
                for do in simbase.air.doId2do.values():
                    if isinstance(do, DistributedLawbotBossAI):
                        for toon in self.battle.activeToons:
                            if toon in do.involvedToons:
                                boss = do
                                break
                if len(self.battle.activeSuits) < 6:
                    boss.appendSuitsToBattle(boss.battleNumber, 'lit')
                self.setSuitCondition(theSuit.doId, 'bashcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'snappedcalculator', 1, 10, 'setBoth')
            elif atkInfo['name'] == 'CourtSanction': # jargon
                result = 70
                attack[SUIT_HP_COL][targetIndex] = result
                currentBossHealth = -1
                for s in self.battle.suits:
                    if s.dna.name == 'lit':
                        currentBossHealth = s.currHP
                if currentBossHealth >= 1:
                    self.setToonCondition(toon.doId, 'allGagBoost', -75, 3, 'setBoth')
                    self.setToonCondition(toon.doId, 'lureBoost', -75, 3, 'setBoth')
                else:
                    self.setToonCondition(toon.doId, 'allGagBoost', -50, 3, 'setBoth')
                    self.setToonCondition(toon.doId, 'lureBoost', -50, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'sanctioncalculator', 0, 0, 'setBoth')
                from toontown.suit.DistributedLawbotBossAI import DistributedLawbotBossAI

                boss = None
                for do in simbase.air.doId2do.values():
                    if isinstance(do, DistributedLawbotBossAI):
                        for toon in self.battle.activeToons:
                            if toon in do.involvedToons:
                                boss = do
                                break
                if len(self.battle.activeSuits) < 6:
                    boss.appendSuitsToBattle(boss.battleNumber, 'lit')
            elif atkInfo['name'] == 'CourtRecord4': # NEW SANCTION mumbo jumbo
                result = 59
                attack[SUIT_HP_COL][targetIndex] = result
                currentBossHealth = -1
                for s in self.battle.suits:
                    if s.dna.name == 'lit':
                        currentBossHealth = s.currHP
                if currentBossHealth >= 1:
                    self.setToonCondition(toon.doId, 'allGagBoost', -75, 3, 'setBoth')
                    self.setToonCondition(toon.doId, 'lureBoost', -75, 3, 'setBoth')
                else:
                    self.setToonCondition(toon.doId, 'allGagBoost', -50, 3, 'setBoth')
                    self.setToonCondition(toon.doId, 'lureBoost', -50, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'sanctioncalculator', 0, 0, 'setBoth')
                from toontown.suit.DistributedLawbotBossAI import DistributedLawbotBossAI

                boss = None
                for do in simbase.air.doId2do.values():
                    if isinstance(do, DistributedLawbotBossAI):
                        for toon in self.battle.activeToons:
                            if toon in do.involvedToons:
                                boss = do
                                break
                if len(self.battle.activeSuits) < 6:
                    boss.appendSuitsToBattle(boss.battleNumber, 'lit')
            elif atkInfo['name'] == 'CeaseAndDesist': # NEW SANCTION mumbo jumbo
                result = 59
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'allGagBoost', -25, 3, 'setBoth')
                self.setToonCondition(toon.doId, 'lureBoost', -25, 3, 'setBoth')
                self.setToonCondition(toon.doId, 'bound', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'sanctioncalculator2', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'MoneyTrip' and theSuit.dna.name == 'dvk':  # dividend king
                result = 38
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'nolevel7s', 1, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel6s', 1, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel5s', 1, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel8s', 1, 3, 'setBoth')
            elif atkInfo['name'] == 'PeckingOrder' and theSuit.dna.name == 'dvk':
                result = 49
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'nolevel5s', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'nolevel6s', 1, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel7s', 1, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel8s', 1, 0, 'setBoth')
            elif atkInfo['name'] == 'Calculate' and theSuit.dna.name == 'dvk':
                result = 44
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'nolevel6s', 1, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel5s', 1, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel8s', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'nolevel7s', 1, 0, 'setBoth')
            elif atkInfo['name'] == 'Tabulate' and theSuit.dna.name == 'dvk':
                result = 42
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'nolevel6s', 1, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel8s', 1, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel7s', 1, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel5s', 1, 3, 'setBoth')
            elif atkInfo['name'] == 'Audit' and theSuit.dna.name == 'dvk':
                result = 37
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'nolevel8s', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'nolevel7s', 1, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel5s', 1, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel6s', 1, 0, 'setBoth')
            elif atkInfo['name'] == 'MarketCrash' and theSuit.dna.name == 'dvk':
                result = 39
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'nolevel8s', 1, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel7s', 1, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel5s', 1, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel6s', 1, 3, 'setBoth')
            elif atkInfo['name'] == 'FloodTheMarket' and theSuit.dna.name == 'dvk':
                result = 35
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'nolevel8s', 1, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel7s', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'nolevel5s', 1, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel6s', 1, 0, 'setBoth')
            elif atkInfo['name'] == 'BounceCheck' and theSuit.dna.name == 'dvk':
                result = 39
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'nolevel5s', 1, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel7s', 1, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel8s', 1, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel6s', 1, 3, 'setBoth')
            elif atkInfo['name'] == 'FireCog':
                result = 35
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'allGagBoost', -75, 3, 'setBoth')
                self.setToonCondition(toon.doId, 'lureBoost', -75, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'sanctioncalculator', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'PaperCut':
                result = 72
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'noToonUpGags', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'noZapGags', 1, 2, 'setBoth')
                self.setToonCondition(toon.doId, 'allGagBoost', -50, 3, 'setBoth')
                self.setToonCondition(toon.doId, 'lureBoost', -50, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'papercutcalculator', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'WireCut':
                result = 82
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'noThrowGags', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'noSoundGags', 1, 2, 'setBoth')
                self.setToonCondition(toon.doId, 'allGagBoost', -25, 3, 'setBoth')
                self.setToonCondition(toon.doId, 'lureBoost', -25, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'markedcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'markedcalculator2', 1, 10, 'setBoth')
            elif atkInfo['name'] == 'GameShow':
                from toontown.suit.DistributedCashbotBossAI import DistributedCashbotBossAI

                boss = None
                for do in simbase.air.doId2do.values():
                    if isinstance(do, DistributedCashbotBossAI):
                        for toon in self.battle.activeToons:
                            if toon in do.involvedToons:
                                boss = do
                                break
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'absorbingHR', 1, 99, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'immune', 1, 99, 'setBoth')
                boss.appendSuitsToBattle(boss.battleNumber, 'crf1')
            elif atkInfo['name'] == 'QualityControl':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for suit in self.currentlyLuredSuits.keys():
                    self.__removeLured(suit)
            elif atkInfo['name'] == 'QualityControl1':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for suit in self.battle.activeSuits:
                    self.setSuitCondition(suit.doId, 'syphon', 1, 99, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'syphon', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'QualityControl2':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'noToonUpGags', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'noLureGags', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'noSoundGags', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'noSquirtGags', 1, 2, 'setBoth')
            elif atkInfo['name'] == 'QualityControl3':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'noTrapGags', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'noThrowGags', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'noZapGags', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'noDropGags', 1, 2, 'setBoth')
            elif atkInfo['name'] == 'ConeOfShame':
                result = 50
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'allGagBoost', -75, 3, 'setBoth')
                self.setToonCondition(toon.doId, 'lureBoost', -75, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'sanctioncalculator', 0, 0, 'setBoth')
                targetSuit = self.battle.activeSuits[attack[SUIT_ATK_COL] + 3]
                targetSuit.setHP(1000)
                targetSuit.setMaxHP(1000)
                targetSuit.setManager(1)
                continue
            elif atkInfo['name'] == 'UnionBuster':
                result = 35
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'snapped', .25, 3, 'setBoth')
            elif atkInfo['name'] == 'Drowning':
                result = 37
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'allGagBoost', -25, 3, 'setBoth')
                self.setToonCondition(toon.doId, 'lureBoost', -25, 3, 'setBoth')
            elif atkInfo['name'] == 'QualityLvlControl3':
                result = 40
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'allGagBoost', -50, 3, 'setBoth')
                self.setToonCondition(toon.doId, 'lureBoost', -50, 3, 'setBoth')
            elif atkInfo['name'] == 'AfterShock':
                result = 46
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'allGagBoost', -50, 3, 'setBoth')
                self.setToonCondition(toon.doId, 'lureBoost', -50, 3, 'setBoth')
                for suit in self.battle.activeSuits:
                    self.setSuitCondition(suit.doId, 'insured', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'OilRain':
                result = 25
                attack[SUIT_HP_COL][targetIndex] = result
                for suit in self.battle.activeSuits:
                    self.setSuitCondition(suit.doId, 'insured', 1, 99, 'setBoth')
            elif atkInfo['name'] == 'QualityLvlControl': #inversion
                result = 46
                attack[SUIT_HP_COL][targetIndex] = result
                for suit in self.battle.activeSuits:
                    self.setSuitCondition(suit.doId, 'insured', 0, 0, 'setBoth')
                theSuit.setHP(int(theSuit.currHP + 250))
            elif atkInfo['name'] == 'QualityLvlControl1':
                result = 35
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'noSquirtGags', 1, 2, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'soakedcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'soakedcalculator2', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'shielding', 1, 99, 'setBoth')
            elif atkInfo['name'] == 'UnionBust':
                attack[SUIT_HP_COL][targetIndex] = 37
                targetSuit = self.battle.activeSuits[attack[SUIT_ATK_COL] + 2]
                theSuit.setHP(int(theSuit.currHP + targetSuit.currHP))
                targetSuit.setHP(int(targetSuit.currHP - targetSuit.currHP))
                theSuit.setDamageMultiplier(theSuit.getDamageMultiplier() * 1.1)
                if self.suitHasCondition(targetSuit.doId, 'lured'):
                    self.setSuitCondition(targetSuit.doId, 'lured', 0, 0, 'setBoth')
                self.__removeLured(targetSuit.doId)
            elif atkInfo['name'] == 'UnionBust2':
                attack[SUIT_HP_COL][targetIndex] = 45
                targetSuit = self.battle.activeSuits[attack[SUIT_ATK_COL] + 2]
                theSuit.setHP(int(theSuit.currHP + targetSuit.currHP))
                targetSuit.setHP(int(targetSuit.currHP - targetSuit.currHP))
                theSuit.setDamageMultiplier(theSuit.getDamageMultiplier() * 1.1)
                if self.suitHasCondition(targetSuit.doId, 'lured'):
                    self.setSuitCondition(targetSuit.doId, 'lured', 0, 0, 'setBoth')
                self.__removeLured(targetSuit.doId)
            elif atkInfo['name'] == 'UnionBust3':
                attack[SUIT_HP_COL][targetIndex] = 38
                targetSuit = self.battle.activeSuits[attack[SUIT_ATK_COL] + 2]
                theSuit.setHP(int(theSuit.currHP + targetSuit.currHP))
                targetSuit.setHP(int(targetSuit.currHP - targetSuit.currHP))
                theSuit.setDamageMultiplier(theSuit.getDamageMultiplier() * 1.1)
                if self.suitHasCondition(targetSuit.doId, 'lured'):
                    self.setSuitCondition(targetSuit.doId, 'lured', 0, 0, 'setBoth')
                self.__removeLured(targetSuit.doId)
            elif atkInfo['name'] == 'FreezingRain':
                result = 70
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'noLureGags', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'noSoundGags', 1, 2, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'costscalculator', 0, 0, 'setBoth')
                for suit in self.battle.activeSuits:
                    self.setSuitCondition(suit.doId, 'insured', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'PoisonSpray':
                result = 43
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'shielding', 1, 4, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'enraged', 0, 0, 'none')
                self.setSuitCondition(theSuit.doId, 'gavelcalculator', 1, 10, 'setBoth')
                managerTarget = None
                for suit in self.battle.activeSuits:
                    if suit.dna.name == 'lit':
                        self.setSuitCondition(suit.doId, 'bellowcalculator', 1, 10, 'setBoth')
            elif atkInfo['name'] == 'SlushFund':
                theSuit.setHP(int(theSuit.currHP - (theSuit.currHP / 4)))
                managerTarget = None
                for suit in self.battle.activeSuits:
                    if self.battle.findSuit(suit.doId).getManager() and not suit.dna.name == 'mad':
                        managerTarget = suit
                        break
                managerTarget.setHP(managerTarget.getHP() + (theSuit.currHP / 4))
            elif atkInfo['name'] == 'MPQuake':
                result = 25
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'costscalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'sanctioncalculator', 1, 10, 'setBoth')
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'allGagBoost', 100, 99, 'setBoth')
                managerTarget = None
                for suit in self.battle.activeSuits:
                    if suit.dna.name == 'tcm':
                        managerTarget = suit
                        break
                    elif suit.dna.name == 'cry':
                        managerTarget = suit
                        break
                    elif suit.dna.name == 'dvk':
                        managerTarget = suit
                        break
                managerTarget.setHP(managerTarget.getHP() + 250)
            elif atkInfo['name'] == 'EvilEyeWSI':
                result = 45
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'refinementcalculator', 0, 0, 'setBoth')
                managerTarget = None
                for suit in self.battle.activeSuits:
                    if suit.dna.name == 'fbd':
                        managerTarget = suit
                        break
                    elif suit.dna.name == 'frs':
                        managerTarget = suit
                        break
                    elif suit.dna.name == 'cp':
                        managerTarget = suit
                        break
                managerTarget.setHP(managerTarget.getHP() + 250)
            elif atkInfo['name'] == 'MPHotAir':
                result = 37
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'costscalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'sanctioncalculator', 1, 10, 'setBoth')
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'allGagBoost', 100, 99, 'setBoth')
                for suit in self.battle.activeSuits:
                    if suit.currHP <= 0:
                        continue

                    x = (suit.maxHP * suit.hardMaxHP) - suit.currHP
                    if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
                        suit.setHP(suit.currHP + 0)
                    elif suit.currHP + 125 > (suit.maxHP * suit.hardMaxHP):
                        suit.setHP(suit.currHP + x)
                    else:
                        suit.setHP(suit.currHP + 125)
            elif atkInfo['name'] == 'Shakedown2':
                result = 37
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'sanctioncalculator', 1, 10, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'insurancecalculator', 0, 0, 'setBoth')
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'allGagBoost', 100, 99, 'setBoth')
                for suit in self.battle.activeSuits:
                    if suit.currHP <= 0:
                        continue

                    x = (suit.maxHP * suit.hardMaxHP) - suit.currHP
                    if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
                        suit.setHP(suit.currHP + 0)
                    elif suit.currHP + 100 > (suit.maxHP * suit.hardMaxHP):
                        suit.setHP(suit.currHP + x)
                    else:
                        suit.setHP(suit.currHP + 100)
            elif atkInfo['name'] == 'FireCog':
                result = 62
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'allGagBoost', -75, 3, 'setBoth')
                self.setToonCondition(toon.doId, 'lureBoost', -75, 3, 'setBoth')
            elif atkInfo['name'] == 'MPSongAndDance':
                result = 35
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'cannotDodge', 100, 2, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'cannotDodge', 100, 2, 'setBoth')
                self.setToonCondition(toon.doId, 'allGagBoost', 100, 99, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'insurancecalculator', 0, 0, 'setBoth')
                for suit in self.battle.activeSuits:
                    if not suit.dna.name == 'otm':
                        suit.setHP(int(suit.currHP - 200))
                        if suit.currHP <= 0:
                            if suit.getSkeleRevives() >= 1:
                                suit.useSkeleRevive()
                            self.__removeLured(suit.doId)
                            if self.suitHasCondition(suit.doId, 'lured'):
                                self.setSuitCondition(suit.doId, 'lured', 0, 0, 'setBoth')
                        continue
            elif atkInfo['name'] == 'ReArrange':
                result = 34
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'phase2', 1, 99, 'setBoth')
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'allGagBoost', 100, 99, 'setBoth')
                theSuit.setDamageMultiplier(theSuit.getDamageMultiplier() * 1.5)
            elif atkInfo['name'] == 'ChainsawRolodex':
                result = 26
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'phase2', 1, 99, 'setBoth')
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'allGagBoost', 100, 99, 'setBoth')
                theSuit.setDamageMultiplier(theSuit.getDamageMultiplier() * 1.05)
            elif atkInfo['name'] == 'RevvingUp':
                result = 30
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'phase2', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'phase3', 1, 99, 'setBoth')
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'allGagBoost', 100, 99, 'setBoth')
            elif atkInfo['name'] == 'StandUpGuy':
                result = 40
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'phase2', 1, 99, 'setBoth')
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'allGagBoost', 100, 99, 'setBoth')
                theSuit.setDamageMultiplier(theSuit.getDamageMultiplier() * 2)
            elif atkInfo['name'] == 'Usury':
                result = 60
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'corruption', .25, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'shielding', 0, 0, 'setBoth')
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'allGagBoost', 100, 99, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'costscalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'sanctioncalculator', 1, 10, 'setBoth')
            elif atkInfo['name'] == 'ChainsawDetonate2':
                result = 56
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'corruption', .75, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'costscalculator', 0, 0, 'setBoth')
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'allGagBoost', 100, 99, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'sanctioncalculator', 1, 10, 'setBoth')
            elif atkInfo['name'] == 'ClockChange':
                result = random.randint(10, 25)
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'allGagBoost', 150, 99, 'setBoth')
            elif atkInfo['name'] == 'ChainsawQuake':
                result = 48
                attack[SUIT_HP_COL][targetIndex] = result
                for suit in self.battle.activeSuits:
                    if suit.currHP <= 0:
                        continue
                    if not suit.dna.name == 'tcm' and not suit.dna.name == 'cry' and not suit.dna.name == 'otm' and not suit.dna.name == 'dvk':
                        suit.setHP(suit.currHP - suit.currHP)
                        self.__removeLured(suit.doId)
                        self.setSuitCondition(suit.doId, 'lured', 0, 0, 'setBoth')
                        continue
            elif atkInfo['name'] == 'ChainsawGlowerPower':
                result = 30
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'allGagBoost', 100, 99, 'setBoth')
                targetSuit = self.battle.activeSuits[attack[SUIT_ATK_COL] + 2]
                targetSuit.setHP(2000)
                targetSuit.setMaxHP(2000)
                targetSuit.setManager(1)
                continue
            elif atkInfo['name'] == 'ChainsawDetonate3':
                result = 30
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'allGagBoost', 100, 99, 'setBoth')
                targetSuit = self.battle.activeSuits[attack[SUIT_ATK_COL] + 3]
                targetSuit.setHP(1500)
                targetSuit.setMaxHP(1500)
                targetSuit.setManager(1)
                self.setSuitCondition(targetSuit.doId, 'insured', 1, 99, 'setBoth')
                continue
            elif atkInfo['name'] == 'BombCake':
                result = 50
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'markedcalculator', 0, 0, 'setBoth')
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'noThrowGags', 1, 3, 'setBoth')
            elif atkInfo['name'] == 'ChainsawCanned':
                result = 60
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'noToonUpGags', 1, 3, 'setBoth')
            elif atkInfo['name'] == 'Tribute2':
                result = 60
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'trapcalculator', 0, 0, 'setBoth')
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'noTrapGags', 1, 3, 'setBoth')
            elif atkInfo['name'] == 'SlushFund2':
                result = 62
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'soakedcalculator', 0, 0, 'setBoth')
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'noSquirtGags', 1, 3, 'setBoth')
            elif atkInfo['name'] == 'NotThrowPiano':
                result = 40
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'dropcalculator', 0, 0, 'setBoth')
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'noDropGags', 1, 3, 'setBoth')
            elif atkInfo['name'] == 'Detonate2':
                result = 50
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'zapcalculator', 0, 0, 'setBoth')
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'noZapGags', 1, 3, 'setBoth')
            elif atkInfo['name'] == 'Usury2':
                result = 26
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'sanctioncalculator', 0, 0, 'setBoth')
                for suit in self.battle.activeSuits:
                    if suit.currHP <= 0:
                        continue

                    x = (suit.maxHP * suit.hardMaxHP) - suit.currHP
                    if not suit.dna.name == 'tcm' and not suit.dna.name == 'cry' and not suit.dna.name == 'otm' and not suit.dna.name == 'dvk':
                        suit.setHP(suit.currHP + x)
                    continue
            elif atkInfo['name'] == 'ChainsawDetonate':
                result = 52
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'sanctioncalculator', 0, 0, 'setBoth')
                targetSuit = self.battle.activeSuits[attack[SUIT_ATK_COL] + 1]
                targetSuit.setHP(int(targetSuit.currHP - targetSuit.currHP))
                self.__removeLured(targetSuit.doId)
            elif atkInfo['name'] == 'Detonate':
                result = 28
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'sanctioncalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'shielding', 1, 99, 'setBoth')
            elif atkInfo['name'] == 'InsurancePlan':
                result = 38
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'insurancecalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'bindingscalculator', 1, 10, 'setBoth')
                currentBossHealth = -1
                for s in self.battle.suits:
                    if s.dna.name == 'scg':
                        currentBossHealth = s.currHP
                if currentBossHealth >= 1:
                    for suit in self.battle.activeSuits:
                        if suit.currHP <= 0:
                            continue
                        x = (suit.maxHP * suit.hardMaxHP) - suit.currHP
                        if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
                            suit.setHP(suit.currHP + 0)
                        elif suit.currHP + 85 > (suit.maxHP * suit.hardMaxHP):
                            suit.setHP(suit.currHP + x)
                        else:
                            suit.setHP(suit.currHP + 85)
                elif currentBossHealth <= 0:
                    for suit in self.battle.activeSuits:
                        if suit.currHP <= 0:
                            continue
                        x = (suit.maxHP * suit.hardMaxHP) - suit.currHP
                        if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
                            suit.setHP(suit.currHP + 0)
                        elif suit.currHP + 50 > (suit.maxHP * suit.hardMaxHP):
                            suit.setHP(suit.currHP + x)
                        else:
                            suit.setHP(suit.currHP + 50)
                    continue
                from toontown.suit.DistributedLawbotBossAI import DistributedLawbotBossAI

                boss = None
                for do in simbase.air.doId2do.values():
                    if isinstance(do, DistributedLawbotBossAI):
                        for toon in self.battle.activeToons:
                            if toon in do.involvedToons:
                                boss = do
                                break
                if len(self.battle.activeSuits) < 6:
                    boss.appendSuitsToBattle(boss.battleNumber, 'lit')
            elif atkInfo['name'] == 'Snow':
                result = 42
                attack[SUIT_HP_COL][targetIndex] = result
                theSuit.setHP(int(theSuit.currHP + result))
                self.setSuitCondition(theSuit.doId, 'shielding', 1, 4, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'enraged', 0, 0, 'none')
                self.setSuitCondition(theSuit.doId, 'gavelcalculator', 1, 10, 'setBoth')
            elif atkInfo['name'] == 'Accusations2':
                result = 25
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'phase3', 1, 99, 'setBoth')
                theSuit.useSkeleRevive()
                theSuit.setHP(2500)
                theSuit.setMaxHP(2500)
            elif atkInfo['name'] == 'Spotlight':
                for suit in self.battle.activeSuits:
                    if suit.currHP <= 0:
                        continue

                    x = (suit.maxHP * suit.hardMaxHP) - suit.currHP
                    if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
                        suit.setHP(suit.currHP + 0)
                    elif suit.currHP + 500 > (suit.maxHP * suit.hardMaxHP):
                        suit.setHP(suit.currHP + x)
                    else:
                        suit.setHP(suit.currHP + 500)
                    continue
            elif atkInfo['name'] == 'Beguile':
                result = 54
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'immune', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'Refinement':
                result = 50
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'vulnerable', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'refinementcalculator', 0, 0, 'setBoth')
                for suit in self.battle.activeSuits:
                    if suit.currHP <= 0:
                        continue
                    x = (suit.maxHP * suit.hardMaxHP) - suit.currHP
                    if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
                        suit.setHP(suit.currHP + 0)
                    elif suit.currHP + 125 > (suit.maxHP * suit.hardMaxHP):
                        suit.setHP(suit.currHP + x)
                    else:
                        suit.setHP(suit.currHP + 125)
                    continue
            elif atkInfo['name'] == 'Detonate3':
                result = 35
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'phase3', 1, 99, 'setBoth')
                theSuit.setHP(1500)
                theSuit.setDamageMultiplier(theSuit.getDamageMultiplier() * 1.5)
                for suit in self.battle.activeSuits:
                    if suit.currHP <= 0:
                        continue
                    x = (suit.maxHP * suit.hardMaxHP) - suit.currHP
                    if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
                        suit.setHP(suit.currHP + 0)
                    elif suit.currHP + 125 > (suit.maxHP * suit.hardMaxHP):
                        suit.setHP(suit.currHP + x)
                    else:
                        suit.setHP(suit.currHP + 125)
                    continue
            elif atkInfo['name'] == 'QualityLvlControl2':
                result = 40
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'insurancecalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'costscalculator', 1, 10, 'setBoth')
                for suit in self.battle.activeSuits:
                    if suit.currHP <= 0:
                        continue
                    x = (suit.maxHP * suit.hardMaxHP) - suit.currHP
                    if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
                        suit.setHP(suit.currHP + 0)
                    elif suit.currHP + 125 > (suit.maxHP * suit.hardMaxHP):
                        suit.setHP(suit.currHP + x)
                    else:
                        suit.setHP(suit.currHP + 125)
                    continue
            elif atkInfo['name'] == 'Bomb':
                result = 40
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'noSOS', 1, 3, 'setBoth')
                self.setToonCondition(toon.doId, 'noFires', 1, 3, 'setBoth')
                self.setToonCondition(toon.doId, 'noUnites', 1, 3, 'setBoth')
                theSuit.setHP(int(theSuit.currHP - (result * 4)))
                if theSuit.currHP <= 0:
                    if theSuit.getSkeleRevives() >= 1:
                        theSuit.useSkeleRevive()
                self.setSuitCondition(theSuit.doId, 'lured', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'costscalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'shielding', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'WhitePowder':
                result = 47.5
                attack[SUIT_HP_COL][targetIndex] = result
                currentBossHealth = -1
                for s in self.battle.suits:
                    if s.dna.name == 'ste':
                        currentBossHealth = s.currHP
                if currentBossHealth >= 1:
                    self.setToonCondition(toon.doId, 'snapped', .4, 3, 'setBoth')
                else:
                    self.setToonCondition(toon.doId, 'snapped', .2, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'bellowcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'soakedcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'soakedcalculator2', 0, 0, 'setBoth')
                for suit in self.battle.activeSuits:
                    #if suit.currHP <= 0:
                        #continue

                    #x = (suit.maxHP * suit.hardMaxHP) - suit.currHP
                    #if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
                        #suit.setHP(suit.currHP + 0)
                    #elif suit.currHP + 100 > (suit.maxHP * suit.hardMaxHP):
                        #suit.setHP(suit.currHP + x)
                    #else:
                        #suit.setHP(suit.currHP + 100)
                    self.setSuitCondition(suit.doId, 'soaked', 0, 0, 'setBoth')
                    self.setSuitCondition(suit.doId, 'dazed', 0, 0, 'setBoth')
                    if self.suitHasCondition(suit.doId, 'lured'):
                        self.setSuitCondition(suit.doId, 'lured', 0, 0, 'setBoth')
                    continue
                for suit in self.currentlyLuredSuits.keys():
                    self.__removeLured(suit)
                # from toontown.suit.DistributedLawbotBossAI import DistributedLawbotBossAI

                # boss = None
                # for do in simbase.air.doId2do.values():
                # if isinstance(do, DistributedLawbotBossAI):
                # for toon in self.battle.activeToons:
                # if toon in do.involvedToons:
                # boss = do
                # break
                # if len(self.battle.activeSuits) < 4 and not self.suitHasCondition(theSuit.doId, 'desperation'):
                # boss.appendSuitsToBattle(boss.battleNumber, 'lit')
                # elif len(self.battle.activeSuits) < 6 and self.suitHasCondition(theSuit.doId, 'desperation'):
                # boss.appendSuitsToBattle(boss.battleNumber, 'lit')
            elif atkInfo['name'] == 'CeaseAndDesist':
                for suit in self.currentlyLuredSuits.keys():
                    self.__removeLured(suit)
            elif atkInfo['name'] == 'GoodMorningToontown':
                result = 30
                attack[SUIT_HP_COL][targetIndex] = result
                theSuit.setHP(int(theSuit.currHP + (result * 4)))
            elif atkInfo['name'] == 'FieldPromotion':
                result = random.randint(30, 50)
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'phase3', 1, 99, 'setBoth')
            elif atkInfo['name'] == 'MobMentality':
                for suit in self.battle.activeSuits:
                    if suit.currHP <= 0:
                        continue
                    x = (suit.maxHP * suit.hardMaxHP) - suit.currHP
                    if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
                        suit.setHP(suit.currHP + 0)
                    elif suit.currHP + 100 > (suit.maxHP * suit.hardMaxHP):
                        suit.setHP(suit.currHP + x)
                    else:
                        suit.setHP(suit.currHP + 100)
                    if self.suitHasCondition(suit.doId, 'lured'):
                        self.setSuitCondition(suit.doId, 'lured', 0, 0, 'setBoth')
                    continue
                for suit in self.currentlyLuredSuits.keys():
                    self.__removeLured(suit)
            elif atkInfo['name'] == 'HeatWave':
                result = (60 + (self.TurnsElapsed * 2))
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'corruption', .2, 2, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'costscalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'sanctioncalculator', 1, 10, 'setBoth')
            elif atkInfo['name'] == 'StealSafe':
                result = random.randint(30, 50)
                attack[SUIT_HP_COL][targetIndex] = result
                theSuit.setHP(int(theSuit.currHP + (result * 4)))
            elif atkInfo['name'] == 'Wiretapped':
                result = 41
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'vulnerable', 1, 10, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'immune', 0, 0, 'setBoth')
                theSuit.setHP(int(theSuit.currHP + attack[SUIT_HP_COL][
                    targetIndex]))
            elif atkInfo['name'] == 'HeadRoller':
                result = 41
                attack[SUIT_HP_COL][targetIndex] = result
                targetSuit = self.battle.activeSuits[attack[SUIT_ATK_COL] + 2]
                theSuit.setHP(int(theSuit.currHP + targetSuit.currHP))
                targetSuit.setHP(int(targetSuit.currHP - targetSuit.currHP))
                theSuit.setDamageMultiplier(theSuit.getDamageMultiplier() * 1.1)
                self.__removeLured(targetSuit.doId)
            elif atkInfo['name'] == 'HeadRoller2':
                result = 38
                attack[SUIT_HP_COL][targetIndex] = result
                targetSuit = self.battle.activeSuits[attack[SUIT_ATK_COL] + 2]
                theSuit.setHP(int(theSuit.currHP + targetSuit.currHP))
                targetSuit.setHP(int(targetSuit.currHP - targetSuit.currHP))
                theSuit.setDamageMultiplier(theSuit.getDamageMultiplier() * 1.1)
                self.__removeLured(targetSuit.doId)
            elif atkInfo['name'] == 'HeadRoller3':
                result = 41
                attack[SUIT_HP_COL][targetIndex] = result
                theSuit.setDamageMultiplier(theSuit.getDamageMultiplier() * 1.25)
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'allGagBoost', 100, 3, 'setBoth')
                for suit in self.battle.activeSuits:
                    if suit.currHP <= 0:
                        continue
                    if not suit.dna.name == 'gtk' and not suit.dna.name == 'fhj':
                        theSuit.setHP(int(theSuit.currHP + suit.currHP))
                    if not suit.dna.name == 'gtk' and not suit.dna.name == 'fhj':
                        suit.setHP(suit.currHP - suit.currHP)
                    else:
                        pass
                    if self.suitHasCondition(suit.doId, 'lured'):
                        self.setSuitCondition(suit.doId, 'lured', 0, 0, 'setBoth')
                    continue
                for suit in self.currentlyLuredSuits.keys():
                    self.__removeLured(suit)
            elif atkInfo['name'] == 'SwirlBath':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for suit in self.battle.activeSuits:
                    if suit.currHP <= 0:
                        continue
                    if not suit.dna.name == 'dsf':
                        suit.setHP(suit.currHP - suit.currHP)
                    else:
                        pass
                    if self.suitHasCondition(suit.doId, 'lured'):
                        self.setSuitCondition(suit.doId, 'lured', 0, 0, 'setBoth')
                    continue
                for suit in self.currentlyLuredSuits.keys():
                    self.__removeLured(suit)
            elif atkInfo['name'] == 'Enraged':
                result = 30
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'shielding', 0, 0, 'none')
                self.setSuitCondition(theSuit.doId, 'enraged', 1, 3, 'setBoth')
            else:
                self.notify.debug('__calcSuitAtkHp - Target is not corrupt, not doing any bonus here')
                attack[SUIT_HP_COL][targetIndex] = result


            if self.suitHasCondition(theSuit.doId, 'desperation') and self.suitHasCondition(theSuit.doId, 'enraged') and theSuit.getHP() > (theSuit.getMaxHP() * 1.5):
                attack[SUIT_HP_COL][targetIndex] *= (1.2 + self.getToonConditionModifier(toonId, 'snapped') + self.getToonConditionModifier(toonId, 'corruption') + theSuit.getDamageMultiplier())
            elif self.suitHasCondition(theSuit.doId, 'desperation') and theSuit.getHP() > (theSuit.getMaxHP() * 1.5):
                attack[SUIT_HP_COL][targetIndex] *= (.9 + self.getToonConditionModifier(toonId, 'snapped') + self.getToonConditionModifier(toonId, 'corruption') + theSuit.getDamageMultiplier())
            elif theSuit.getHP() > (theSuit.getMaxHP() * 1.5):
                attack[SUIT_HP_COL][targetIndex] *= (.5 + self.getToonConditionModifier(toonId, 'snapped') + self.getToonConditionModifier(toonId, 'corruption') + theSuit.getDamageMultiplier())
            elif self.suitHasCondition(theSuit.doId, 'desperation') and self.suitHasCondition(theSuit.doId, 'enraged'):
                attack[SUIT_HP_COL][targetIndex] *= (.83 + self.getToonConditionModifier(toonId, 'snapped') + self.getToonConditionModifier(toonId, 'corruption') + theSuit.getDamageMultiplier())
            elif self.suitHasCondition(theSuit.doId, 'desperation'):
                attack[SUIT_HP_COL][targetIndex] *= (.4 + self.getToonConditionModifier(toonId, 'snapped') + self.getToonConditionModifier(toonId, 'corruption') + theSuit.getDamageMultiplier())
            elif self.suitHasCondition(theSuit.doId, 'enraged'):
                attack[SUIT_HP_COL][targetIndex] *= (.3 + self.getToonConditionModifier(toonId, 'snapped') + self.getToonConditionModifier(toonId, 'corruption') + theSuit.getDamageMultiplier())
            else:
                attack[SUIT_HP_COL][targetIndex] = result * (self.getToonConditionModifier(toonId, 'corruption') + self.getToonConditionModifier(toonId, 'snapped') + theSuit.getDamageMultiplier())

            if self.suitHasCondition(theSuit.doId, 'syphon'):
                theSuit.setHP(int(theSuit.currHP + result * 4))
            elif self.suitHasCondition(theSuit.doId, 'phase2') and not theSuit.dna.name == 'tcm' and not theSuit.dna.name == 'crf':
                theSuit.setDamageMultiplier(theSuit.getDamageMultiplier() * 1.05)
            elif self.suitHasCondition(theSuit.doId, 'phase3') and not theSuit.dna.name == 'crf':
                theSuit.setDamageMultiplier(theSuit.getDamageMultiplier() * 1.05)

            self.notify.debug('__calcSuitAtkHp - result is %s for index %i' % (str(attack[SUIT_HP_COL][targetIndex]), targetIndex))
    
    def __calcSuitAtkHpALT(self, attack):
        '''
        Professor Control: I'm sorry, but the original method is actually a pigstye and I cannot work in that.  I'm using an alternate form for now.
        '''
        targetList = self.__createSuitTargetList(attack)
        for currTarget in xrange(len(targetList)):
            toonId = targetList[currTarget]
            toon = self.battle.getToon(toonId)
            result = 0
            theSuit = self.battle.findSuit(attack[SUIT_ID_COL])
            atkType = attack[SUIT_ATK_COL]
            atkInfo = SuitBattleGlobals.getSuitAttack(theSuit.dna.name, theSuit.getLevel(), atkType)
            if toon and toon.immortalMode:
                result = 1
            elif TOONS_TAKE_NO_DAMAGE:
                result = 0
            elif self.__suitAtkHit(attack[SUIT_ID_COL], attack[SUIT_ATK_COL]):
                atkType = attack[SUIT_ATK_COL]
                theSuit = self.battle.findSuit(attack[SUIT_ID_COL])
                atkInfo = SuitBattleGlobals.getSuitAttack(theSuit.dna.name, theSuit.getLevel(), atkType)
                mult = 1.0
                result = int(atkInfo['hp'] * mult)
                if theSuit.getExecutive():
                    result = int(result * ToontownBattleGlobals.EXECUTIVE_DMG_MULT)
                elif theSuit.getGovernaught():
                    result = int(result * ToontownBattleGlobals.GOVERNAUGHT_DMG_MULT)
            targetIndex = self.battle.activeToons.index(toonId)
            if atkInfo['name'] == 'SynergyFees':
                result = (24 + ((self.TurnsElapsed - 1) * 1.3))
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'costscalculator', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'CalculatingFees':
                result = (24 + (self.TurnsElapsed * 1.3))
                toon.setHp(toon.hp + result)
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'calculatingcalculator', 1, 1, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'costscalculator', 1, 10, 'setBoth')
            elif atkInfo['name'] == 'StenographerSanction':
                result = 25
                attack[SUIT_HP_COL][targetIndex] = result
                currentBossHealth = -1
                for s in self.battle.suits:
                    if s.dna.name == 'lit':
                        currentBossHealth = s.currHP
                if currentBossHealth >= 1:
                    self.setToonCondition(toon.doId, 'allGagBoost', -75, 3, 'setBoth')
                    self.setToonCondition(toon.doId, 'lureBoost', -75, 3, 'setBoth')
                else:
                    self.setToonCondition(toon.doId, 'allGagBoost', -50, 3, 'setBoth')
                    self.setToonCondition(toon.doId, 'lureBoost', -50, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'sanctioncalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'sanctioncalculator3', 0, 0, 'setBoth')
                from toontown.suit.DistributedLawbotBossAI import DistributedLawbotBossAI

                boss = None
                for do in simbase.air.doId2do.values():
                    if isinstance(do, DistributedLawbotBossAI):
                        for t in self.battle.activeToons:
                            if t in do.involvedToons:
                                boss = do
                                break
               # if len(self.battle.activeSuits) < 4:
                   # boss.appendSuitsToBattle(boss.battleNumber, 'lit')
            elif atkInfo['name'] == 'StenographerSanctionBindings':
                    result = 25
                    attack[SUIT_HP_COL][targetIndex] = result
                    self.setToonCondition(toon.doId, 'allGagBoost', -25, 3, 'setBoth')
                    self.setToonCondition(toon.doId, 'lureBoost', -25, 3, 'setBoth')
                    self.setSuitCondition(theSuit.doId, 'sanctioncalculator2', 0, 0, 'setBoth')
                    self.setSuitCondition(theSuit.doId, 'sanctioncalculator4', 1, 1, 'setBoth')
            elif atkInfo['name'] == 'StenographerCourtRecordBan':
                if self.toonHasCondition(toon.doId, 'banned'):
                    result = 50
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkInfo['name'] == 'CaseManagerInsurancePlan':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'insurancecalculator', 0, 0, 'setBoth')
                for suit in self.battle.activeSuits:
                    if not self.suitHasCondition(suit.doId, 'insured'):
                        self.setSuitCondition(suit.doId, 'insured', 1, 99, 'setBoth')
                from toontown.suit.DistributedLawbotBossAI import DistributedLawbotBossAI

                boss = None
                for do in simbase.air.doId2do.values():
                    if isinstance(do, DistributedLawbotBossAI):
                        for t in self.battle.activeToons:
                            if t in do.involvedToons:
                                boss = do
                                break
             #   if len(self.battle.activeSuits) < 4:
                  # boss.appendSuitsToBattle(boss.battleNumber, 'lit')
            elif atkInfo['name'] == 'CaseManagerInsurance':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                currentBossHealth = -1
                for s in self.battle.suits:
                    if s.dna.name == 'scg':
                        currentBossHealth = s.currHP
                if currentBossHealth >= 1:
                    for suit in self.battle.activeSuits:
                        if suit.currHP <= 0:
                            continue
                        x = (suit.maxHP * suit.hardMaxHP) - suit.currHP
                        if self.suitHasCondition(suit.doId, 'insured') and self.getSuitConditionTurns(suit.doId, 'insured') < 99:
                            if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
                                suit.setHP(suit.currHP + 0)
                            elif suit.currHP + 85 > (suit.maxHP * suit.hardMaxHP):
                                suit.setHP(suit.currHP + x)
                            else:
                                suit.setHP(suit.currHP + 85)
                elif currentBossHealth <= 0:
                    for suit in self.battle.activeSuits:
                        if suit.currHP <= 0:
                            continue
                        x = (suit.maxHP * suit.hardMaxHP) - suit.currHP
                        if self.suitHasCondition(suit.doId, 'insured') and self.getSuitConditionTurns(suit.doId, 'insured') < 99:
                            if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
                                suit.setHP(suit.currHP + 0)
                            elif suit.currHP + 50 > (suit.maxHP * suit.hardMaxHP):
                                suit.setHP(suit.currHP + x)
                            else:
                                suit.setHP(suit.currHP + 50)
                    continue
            elif atkInfo['name'] == 'CaseManagerLegalBindings':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'bound', 1, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'bindingscalculator', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'CaseManagerLegallyBound':
                if self.toonHasCondition(toon.doId, 'bound') and self.getToonConditionTurns(toon.doId, 'bound') < 3:
                    result = 20
                    currentBossHealth = -1
                    for s in self.battle.suits:
                        if s.dna.name == 'ste':
                            currentBossHealth = s.currHP
                            s = s
                            if currentBossHealth >= 1:
                                self.setSuitCondition(s.doId, 'sanctioncalculator2', 1, 10, 'setBoth')
                                self.setSuitCondition(s.doId, 'sanctioncalculator4', 1, 10, 'setBoth')
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkInfo['name'] == 'CaseManagerCourtRecordBan':
                if self.toonHasCondition(toon.doId, 'banned2'):
                    result = 50
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkInfo['name'] == 'LitigatorSnapSoak': #soaked snap
                result = 36
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'snapped', .1, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'soakedcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'soakedcalculator2', 1, 10, 'setBoth')
            elif atkInfo['name'] == 'LitigatorSnap':
                result = 30
                attack[SUIT_HP_COL][targetIndex] = result
                currentBossHealth = -1
                for s in self.battle.suits:
                    if s.dna.name == 'ste':
                        currentBossHealth = s.currHP
                if currentBossHealth >= 1:
                    self.setToonCondition(toon.doId, 'snapped', .4, 3, 'setBoth')
                else:
                    self.setToonCondition(toon.doId, 'snapped', .2, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'snappedcalculator', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'LitigatorBayouBellow':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'bellowcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'soakedcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'soakedcalculator2', 0, 0, 'setBoth')
                for suit in self.battle.activeSuits:
                    self.setSuitCondition(suit.doId, 'soaked', 0, 0, 'setBoth')
                    self.setSuitCondition(suit.doId, 'dazed', 0, 0, 'setBoth')
                    self.setSuitCondition(suit.doId, 'bellowattack', 1, 1, 'setBoth')
                    if self.suitHasCondition(suit.doId, 'lured'):
                        self.setSuitCondition(suit.doId, 'lured', 0, 0, 'setBoth')
                    continue
                for suit in self.currentlyLuredSuits.keys():
                    self.__removeLured(suit)
            elif atkInfo['name'] == 'ScapegoatEnraged':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'shielding', 0, 0, 'none')
                self.setSuitCondition(theSuit.doId, 'enraged', 1, 3, 'setBoth')
                if self.suitHasCondition(theSuit.doId, 'lured'):
                    self.setSuitCondition(theSuit.doId, 'lured', 0, 0, 'setBoth')
                self.__removeLured(theSuit.doId)
                for s in self.battle.suits:
                    if s.dna.name == 'csm':
                        suit = s
                        currentBossHealth = s.currHP
                        if currentBossHealth >= 1:
                            self.setSuitCondition(suit.doId, 'bindingscalculator', 1, 10, 'setBoth')
                            self.setSuitCondition(suit.doId, 'insurancecalculator', 1, 10, 'setBoth')
                            self.setSuitCondition(suit.doId, 'ban2tracks', 1, 3, 'setBoth')
                    if s.dna.name == 'ste':
                        suit = s
                        currentBossHealth = s.currHP
                        if currentBossHealth >= 1:
                            self.setSuitCondition(suit.doId, 'ban2levels', 1, 3, 'setBoth')
                from toontown.suit.DistributedLawbotBossAI import DistributedLawbotBossAI

                boss = None
                for do in simbase.air.doId2do.values():
                    if isinstance(do, DistributedLawbotBossAI):
                        for t in self.battle.activeToons:
                            if t in do.involvedToons:
                                boss = do
                                break
              #  if len(self.battle.activeSuits) < 4:
                   # boss.appendSuitsToBattle(boss.battleNumber, 'lit')
            elif atkInfo['name'] == 'ScapegoatCourtRecordBan':
                if self.toonHasCondition(toon.doId, 'banned3'):
                    self.setToonCondition(toon.doId, 'banned3', 1, 1, 'setBoth')
                    result = 50
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkInfo['name'] == 'ScapegoatShieldsUp':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                theSuit.setHP(int(theSuit.currHP + result))
                self.setSuitCondition(theSuit.doId, 'shielding', 1, 4, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'enraged', 0, 0, 'none')
                #self.setSuitCondition(theSuit.doId, 'gavelcalculator', 1, 10, 'setBoth')
                for s in self.battle.suits:
                    if s.dna.name == 'lit':
                        suit = s
                        currentBossHealth = s.currHP
                        if currentBossHealth >= 1:
                            self.setSuitCondition(suit.doId, 'bellowcalculator', 1, 10, 'setBoth')
            elif atkInfo['name'] == 'ScapegoatGavel':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'noGags', 1, 2, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'gavelcalculator', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'ScapegoatBarnyardBash':
                result = 30
                attack[SUIT_HP_COL][targetIndex] = result
                theSuit.setHP(int(theSuit.currHP + result))
            elif atkInfo['name'] == 'PowerhouseAbsorb':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'shielding', 1, 10, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'soakImmune', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'syphon', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'lureImmune', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'rotationcalculator', 0, 0, 'setBoth')
                for s in self.battle.suits:
                    if s.dna.name == 'frs':
                        suit = s
                        currentBossHealth = s.currHP
                        if currentBossHealth >= 1:
                            self.setSuitCondition(suit.doId, 'bantracks', 1, 2, 'setBoth')
            elif atkInfo['name'] == 'PowerhouseSoakImmune':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'shielding', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'soakImmune', 1, 10, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'syphon', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'lureImmune', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'rotationcalculator', 0, 0, 'setBoth')
                for s in self.battle.suits:
                    if s.dna.name == 'frs':
                        suit = s
                        currentBossHealth = s.currHP
                        if currentBossHealth >= 1:
                            self.setSuitCondition(suit.doId, 'bantracks', 1, 2, 'setBoth')
            elif atkInfo['name'] == 'PowerhouseLureImmune':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'shielding', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'soakImmune', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'syphon', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'lureImmune', 1, 10, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'rotationcalculator', 0, 0, 'setBoth')
                for s in self.battle.suits:
                    if s.dna.name == 'frs':
                        suit = s
                        currentBossHealth = s.currHP
                        if currentBossHealth >= 1:
                            self.setSuitCondition(suit.doId, 'bantracks', 1, 2, 'setBoth')
            elif atkInfo['name'] == 'PowerhouseSyphon':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'shielding', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'soakImmune', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'syphon', 1, 10, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'lureImmune', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'rotationcalculator', 0, 0, 'setBoth')
                for s in self.battle.suits:
                    if s.dna.name == 'frs':
                        suit = s
                        currentBossHealth = s.currHP
                        if currentBossHealth >= 1:
                            self.setSuitCondition(suit.doId, 'bantracks', 1, 2, 'setBoth')
            elif atkInfo['name'] == 'PowerhouseSyphonDesperation':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'shielding', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'soakImmune', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'lureImmune', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'rotationcalculator', 1, 10, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'syphoncalculator', 1, 5, 'setBoth')
                for suit in self.battle.activeSuits:
                    self.setSuitCondition(suit.doId, 'syphon', 1, 99, 'setBoth')
            elif atkInfo['name'] == 'PowerhouseSnipeVulnerable':
                if self.toonHasCondition(toon.doId, 'snapped'):
                    if self.suitHasCondition(theSuit.doId, 'lured'):
                        self.setSuitCondition(theSuit.doId, 'lured', 0, 0, 'setBoth')
                    self.__removeLured(theSuit.doId)
                    result = 25
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkInfo['name'] == 'PowerhouseSnipeMulligan':
                if self.toonHasCondition(toon.doId, 'noUnites'):
                    if self.suitHasCondition(theSuit.doId, 'lured'):
                        self.setSuitCondition(theSuit.doId, 'lured', 0, 0, 'setBoth')
                    self.__removeLured(theSuit.doId)
                    result = 25
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkInfo['name'] == 'PowerhouseSnipeCollectCall':
                if self.toonHasCondition(toon.doId, 'bound'):
                    if self.suitHasCondition(theSuit.doId, 'lured'):
                        self.setSuitCondition(theSuit.doId, 'lured', 0, 0, 'setBoth')
                    self.__removeLured(theSuit.doId)
                    result = 25
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkInfo['name'] == 'PowerhouseSnipeBookkept':
                if self.toonHasCondition(toon.doId, 'bookkeepingtoon'):
                    if self.suitHasCondition(theSuit.doId, 'lured'):
                        self.setSuitCondition(theSuit.doId, 'lured', 0, 0, 'setBoth')
                    self.__removeLured(theSuit.doId)
                    result = 25
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkInfo['name'] == 'PowerhouseSnipeSoaked':
                result = 25
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'soakedcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'soakedcalculator2', 1, 10, 'setBoth')
            elif atkInfo['name'] == 'PowerhouseSnipeGagBan':
                if self.toonHasCondition(toon.doId, 'banned'):
                    if self.suitHasCondition(theSuit.doId, 'lured'):
                        self.setSuitCondition(theSuit.doId, 'lured', 0, 0, 'setBoth')
                    self.__removeLured(theSuit.doId)
                    result = 25
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkInfo['name'] == 'AmbassadorManagerialProtection':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'bashcalculator', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'AmbassadorRefinement':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'immune', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'refinementcalculator', 0, 0, 'setBoth')
                currentBossHealth = -1
                for s in self.battle.suits:
                    if s.dna.name == 'cp':
                        currentBossHealth = s.currHP
                if currentBossHealth >= 1:
                    for suit in self.battle.activeSuits:
                        if suit.currHP <= 0:
                            continue
                        x = (suit.maxHP * suit.hardMaxHP) - suit.currHP
                        if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
                            suit.setHP(suit.currHP + 0)
                        elif suit.currHP + 200 > (suit.maxHP * suit.hardMaxHP):
                            suit.setHP(suit.currHP + x)
                        else:
                            suit.setHP(suit.currHP + 200)
                elif currentBossHealth <= 0:
                    for suit in self.battle.activeSuits:
                        if suit.currHP <= 0:
                            continue
                        x = (suit.maxHP * suit.hardMaxHP) - suit.currHP
                        if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
                            suit.setHP(suit.currHP + 0)
                        elif suit.currHP + 125 > (suit.maxHP * suit.hardMaxHP):
                            suit.setHP(suit.currHP + x)
                        else:
                            suit.setHP(suit.currHP + 125)
                    continue
            elif atkInfo['name'] == 'AmbassadorHeadRoller':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'damageupcalculator1', 1, 1, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'headrollercalculator', 0, 0, 'setBoth')
                targetSuit = self.battle.activeSuits[2]
                if not targetSuit.dna.name in SuitBattleGlobals.SpecialCogDict:
                    targetSuit.setHP(targetSuit.currHP - targetSuit.currHP)
                    self.__removeLured(targetSuit.doId)
                    if self.suitHasCondition(targetSuit.doId, 'lured'):
                        self.setSuitCondition(targetSuit.doId, 'lured', 0, 0, 'setBoth')
                else:
                    targetSuit.setHP(targetSuit.currHP - 250)
                    self.__removeLured(targetSuit.doId)
                if self.suitHasCondition(theSuit.doId, 'mulligancalculator') and self.getSuitConditionTurns(
                        theSuit.doId,
                        'mulligancalculator') < 97:
                    self.setSuitCondition(theSuit.doId, 'mulligancalculator2', 1, 99, 'setBoth')
                if self.suitHasCondition(theSuit.doId, 'mulligancalculator2') and self.getSuitConditionTurns(
                        theSuit.doId,
                        'mulligancalculator2') < 97:
                    self.setSuitCondition(theSuit.doId, 'mulligancalculator3', 1, 99, 'setBoth')
                if self.suitHasCondition(theSuit.doId, 'mulligancalculator3') and self.getSuitConditionTurns(
                        theSuit.doId,
                        'mulligancalculator3') < 97:
                    self.setSuitCondition(theSuit.doId, 'mulligancalculator4', 1, 99, 'setBoth')
                else:
                    self.setSuitCondition(theSuit.doId, 'mulligancalculator', 1, 99, 'setBoth')
            elif atkInfo['name'] == 'AmbassadorPhase2':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'phase3', 1, 99, 'setBoth')
                theSuit.setHP(1500)
                theSuit.setDamageMultiplier(theSuit.getDamageMultiplier() * 1.5)
                if self.suitHasCondition(theSuit.doId, 'mulligancalculator') and self.getSuitConditionTurns(
                        theSuit.doId,
                        'mulligancalculator') < 97:
                    self.setSuitCondition(theSuit.doId, 'mulligancalculator2', 1, 99, 'setBoth')
                if self.suitHasCondition(theSuit.doId, 'mulligancalculator2') and self.getSuitConditionTurns(
                        theSuit.doId,
                        'mulligancalculator2') < 97:
                    self.setSuitCondition(theSuit.doId, 'mulligancalculator3', 1, 99, 'setBoth')
                if self.suitHasCondition(theSuit.doId, 'mulligancalculator3') and self.getSuitConditionTurns(
                        theSuit.doId,
                        'mulligancalculator3') < 97:
                    self.setSuitCondition(theSuit.doId, 'mulligancalculator4', 1, 99, 'setBoth')
                else:
                    self.setSuitCondition(theSuit.doId, 'mulligancalculator', 1, 99, 'setBoth')
            elif atkInfo['name'] == 'AmbassadorMulligan':
                self.setToonCondition(toon.doId, 'mulligan', 1, 1, 'setBoth')
                if self.suitHasCondition(theSuit.doId, 'lured'):
                    self.setSuitCondition(theSuit.doId, 'lured', 0, 0, 'setBoth')
                self.__removeLured(theSuit.doId)
                result = 36
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkInfo['name'] == 'AmbassadorManagerialProtectionImmunity':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'immune', 1, 4, 'setBoth')
            elif atkInfo['name'] == 'AmbassadorHeadRollerGroup':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'damageupcalculator2', 1, 1, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'mulligancalculator', 1, 99, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'headroller2calculator', 0, 0, 'setBoth')
                if self.suitHasCondition(theSuit.doId, 'mulligancalculator') and self.getSuitConditionTurns(
                        theSuit.doId,
                        'mulligancalculator') < 97:
                    self.setSuitCondition(theSuit.doId, 'mulligancalculator2', 1, 99, 'setBoth')
                if self.suitHasCondition(theSuit.doId, 'mulligancalculator2') and self.getSuitConditionTurns(
                        theSuit.doId,
                        'mulligancalculator2') < 97:
                    self.setSuitCondition(theSuit.doId, 'mulligancalculator3', 1, 99, 'setBoth')
                if self.suitHasCondition(theSuit.doId, 'mulligancalculator3') and self.getSuitConditionTurns(
                        theSuit.doId,
                        'mulligancalculator3') < 97:
                    self.setSuitCondition(theSuit.doId, 'mulligancalculator4', 1, 99, 'setBoth')
                else:
                    self.setSuitCondition(theSuit.doId, 'mulligancalculator', 1, 99, 'setBoth')
                for suit in self.battle.activeSuits:
                    if suit.currHP <= 0:
                        continue
                    if not suit.dna.name in SuitBattleGlobals.SpecialCogDict:
                        suit.setHP(suit.currHP - suit.currHP)
                        if self.suitHasCondition(suit.doId, 'lured'):
                            self.setSuitCondition(suit.doId, 'lured', 0, 0, 'setBoth')
                    else:
                        suit.setHP(suit.currHP - 250)
                    continue
                for suit in self.currentlyLuredSuits.keys():
                    self.__removeLured(suit)
            elif atkInfo['name'] == 'AmbassadorDamageUp':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                if self.suitHasCondition(theSuit.doId, 'damageupcalculator1'):
                    self.setSuitCondition(theSuit.doId, 'damageupcalculator1', 1, 1, 'setBoth')
                    theSuit.setDamageMultiplier(theSuit.getDamageMultiplier() * 1.1)
                    theSuit.setHP(theSuit.currHP + 100)
                elif self.suitHasCondition(theSuit.doId, 'damageupcalculator2'):
                    self.setSuitCondition(theSuit.doId, 'damageupcalculator2', 1, 1, 'setBoth')
                    theSuit.setDamageMultiplier(theSuit.getDamageMultiplier() * 1.25)
                    theSuit.setHP(theSuit.currHP + 500)
            elif atkInfo['name'] == 'BookkeeperBookkeepingRetaliation':
                if self.toonHasCondition(toon.doId, 'bookkeepingtoon'):
                    self.setToonCondition(toon.doId, 'bookkeepingtoon', 1, 1, 'setBoth')
                    self.setToonCondition(toon.doId, 'allGagBoost', -40, 3, 'setBoth')
                    self.setToonCondition(toon.doId, 'lureBoost', -40, 3, 'setBoth')
                    result = 30
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                #self.setSuitCondition(theSuit.doId, 'bookkeeping2', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'BookkeeperBookkeeping':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'bookkeeping', 1, 5, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'bookkeepingcalculator', 0, 0, 'setBoth')
                if self.suitHasCondition(theSuit.doId, 'lured'):
                    self.setSuitCondition(theSuit.doId, 'lured', 0, 0, 'setBoth')
                self.__removeLured(theSuit.doId)
            elif atkInfo['name'] == 'BookkeeperExplodingDocument':
                result = 25
                attack[SUIT_HP_COL][targetIndex] = result
                currentBossHealth = -1
                for s in self.battle.suits:
                    if s.dna.name == 'frs':
                        currentBossHealth = s.currHP
                if currentBossHealth >= 1:
                    self.setToonCondition(toon.doId, 'allGagBoost', -75, 3, 'setBoth')
                    self.setToonCondition(toon.doId, 'lureBoost', -75, 3, 'setBoth')
                else:
                    self.setToonCondition(toon.doId, 'allGagBoost', -50, 3, 'setBoth')
                    self.setToonCondition(toon.doId, 'lureBoost', -50, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'explodingcalculator', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'BookkeeperPaperCutMarked':
                result = 40
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'snapped', .2, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'markedcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'markedcalculator2', 1, 10, 'setBoth')
            elif atkInfo['name'] == 'BookkeeperPaperCutSoaked':
                result = 40
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'snapped', .2, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'soakedcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'soakedcalculator2', 1, 10, 'setBoth')
            elif atkInfo['name'] == 'BookkeeperPaperCut':
                result = 30
                attack[SUIT_HP_COL][targetIndex] = result
                currentBossHealth = -1
                for s in self.battle.suits:
                    if s.dna.name == 'cp':
                        currentBossHealth = s.currHP
                if currentBossHealth >= 1:
                    self.setToonCondition(toon.doId, 'snapped', .5, 3, 'setBoth')
                else:
                    self.setToonCondition(toon.doId, 'snapped', .25, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'papercutcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'bookkeeping', 1, 1, 'setBoth')
            elif atkInfo['name'] == 'WiretapperGagBan':
                if self.toonHasCondition(toon.doId, 'banned2'):
                    self.setToonCondition(toon.doId, 'banned2', 1, 1, 'setBoth')
                    self.setToonCondition(toon.doId, 'banned3', 1, 1, 'setBoth')
                    result = 50
                elif self.toonHasCondition(toon.doId, 'banned'):
                    self.setToonCondition(toon.doId, 'banned', 1, 1, 'setBoth')
                    self.setToonCondition(toon.doId, 'banned3', 1, 1, 'setBoth')
                    result = 50
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkInfo['name'] == 'WiretapperVoicemail':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'immune', 1, 4, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'brokenconnectioncalculator', 1, 4, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'voicemailcalculator', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'WiretapperBrokenConnection':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'immune', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'vulnerable', 1, 4, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'brokenconnectioncalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'collectcallcalculator', 1, 4, 'setBoth')
            elif atkInfo['name'] == 'WiretapperWiretapped':
                result = random.randint(25, 45)
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'wiretappedcalculator', 0, 0, 'setBoth')
                theSuit.setHP(int(theSuit.currHP + attack[SUIT_HP_COL][
                    targetIndex]))
            elif atkInfo['name'] == 'WiretapperCollectCall':
                result = (24 + (self.TurnsElapsed * 1.3))
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'bound', 1, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'vulnerable', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'collectcallcalculator', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'WiretapperCollectCallDamage':
                if self.toonHasCondition(toon.doId, 'bound') and self.getToonConditionTurns(toon.doId, 'bound') < 3:
                    result = (24 + (self.TurnsElapsed * 1.3))
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkInfo['name'] == 'BanLevel4':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'nolevel4s', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'nolevel6s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel5s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel8s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel7s', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'BanLevel5':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'nolevel4s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel6s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel5s', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'nolevel8s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel7s', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'BanLevel6':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'nolevel4s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel6s', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'nolevel5s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel8s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel7s', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'BanLevel7':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'nolevel4s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel6s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel5s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel8s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel7s', 1, 3, 'setBoth')
            elif atkInfo['name'] == 'BanLevel8':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'nolevel4s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel5s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel6s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel7s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel8s', 1, 3, 'setBoth')
            elif atkInfo['name'] == 'BanLevel45':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'nolevel4s', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'nolevel5s', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'nolevel6s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel7s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel8s', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'BanLevel46':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'nolevel4s', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'nolevel5s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel6s', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'nolevel7s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel8s', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'BanLevel47':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'nolevel4s', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'nolevel5s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel6s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel7s', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'nolevel8s', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'BanLevel48':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'nolevel4s', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'nolevel5s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel6s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel7s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel8s', 1, 3, 'setBoth')
            elif atkInfo['name'] == 'BanLevel56':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'nolevel4s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel5s', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'nolevel6s', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'nolevel7s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel8s', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'BanLevel57':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'nolevel4s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel5s', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'nolevel6s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel7s', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'nolevel8s', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'BanLevel58':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'nolevel4s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel5s', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'nolevel6s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel7s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel8s', 1, 3, 'setBoth')
            elif atkInfo['name'] == 'BanLevel67':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'nolevel4s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel5s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel6s', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'nolevel7s', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'nolevel8s', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'BanLevel68':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'nolevel4s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel5s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel6s', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'nolevel7s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel8s', 1, 3, 'setBoth')
            elif atkInfo['name'] == 'BanLevel78':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'nolevel4s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel5s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel6s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel7s', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'nolevel8s', 1, 3, 'setBoth')
            elif atkInfo['name'] == 'BanToonup':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'noToonUpGags', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'noTrapGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noLureGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noThrowGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noSquirtGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noZapGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noSoundGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noDropGags', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'BanTrap':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'noToonUpGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noTrapGags', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'noLureGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noThrowGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noSquirtGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noZapGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noSoundGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noDropGags', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'BanLure':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'noToonUpGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noTrapGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noLureGags', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'noThrowGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noSquirtGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noZapGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noSoundGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noDropGags', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'BanThrow':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'noToonUpGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noTrapGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noLureGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noThrowGags', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'noSquirtGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noZapGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noSoundGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noDropGags', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'BanSquirt':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'noToonUpGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noTrapGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noLureGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noThrowGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noSquirtGags', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'noZapGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noSoundGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noDropGags', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'BanZap':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'noToonUpGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noTrapGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noLureGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noThrowGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noSquirtGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noZapGags', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'noSoundGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noDropGags', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'BanSound':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'noToonUpGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noTrapGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noLureGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noThrowGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noSquirtGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noZapGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noSoundGags', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'noDropGags', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'BanDrop':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'noToonUpGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noTrapGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noLureGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noThrowGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noSquirtGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noZapGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noSoundGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noDropGags', 1, 3, 'setBoth')
            elif atkInfo['name'] == 'BanToonupTrap':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'noToonUpGags', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'noTrapGags', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'noLureGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noThrowGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noSquirtGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noZapGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noSoundGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noDropGags', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'BanToonupLure':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'noToonUpGags', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'noTrapGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noLureGags', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'noThrowGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noSquirtGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noZapGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noSoundGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noDropGags', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'BanToonupThrow':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'noToonUpGags', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'noTrapGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noLureGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noThrowGags', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'noSquirtGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noZapGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noSoundGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noDropGags', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'BanToonupSquirt':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'noToonUpGags', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'noTrapGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noLureGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noThrowGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noSquirtGags', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'noZapGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noSoundGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noDropGags', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'BanToonupZap':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'noToonUpGags', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'noTrapGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noLureGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noThrowGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noSquirtGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noZapGags', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'noSoundGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noDropGags', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'BanToonupSound':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'noToonUpGags', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'noTrapGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noLureGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noThrowGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noSquirtGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noZapGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noSoundGags', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'noDropGags', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'BanToonupDrop':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'noToonUpGags', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'noTrapGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noLureGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noThrowGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noSquirtGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noZapGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noSoundGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noDropGags', 1, 3, 'setBoth')
            elif atkInfo['name'] == 'BanTrapLure':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'noToonUpGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noTrapGags', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'noLureGags', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'noThrowGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noSquirtGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noZapGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noSoundGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noDropGags', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'BanTrapThrow':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'noToonUpGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noTrapGags', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'noLureGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noThrowGags', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'noSquirtGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noZapGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noSoundGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noDropGags', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'BanTrapSquirt':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'noToonUpGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noTrapGags', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'noLureGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noThrowGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noSquirtGags', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'noZapGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noSoundGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noDropGags', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'BanTrapZap':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'noToonUpGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noTrapGags', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'noLureGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noThrowGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noSquirtGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noZapGags', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'noSoundGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noDropGags', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'BanTrapSound':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'noToonUpGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noTrapGags', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'noLureGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noThrowGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noSquirtGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noZapGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noSoundGags', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'noDropGags', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'BanTrapDrop':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'noToonUpGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noTrapGags', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'noLureGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noThrowGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noSquirtGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noZapGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noSoundGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noDropGags', 1, 3, 'setBoth')
            elif atkInfo['name'] == 'BanLureThrow':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'noToonUpGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noTrapGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noLureGags', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'noThrowGags', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'noSquirtGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noZapGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noSoundGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noDropGags', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'BanLureSquirt':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'noToonUpGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noTrapGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noLureGags', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'noThrowGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noSquirtGags', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'noZapGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noSoundGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noDropGags', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'BanLureZap':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'noToonUpGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noTrapGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noLureGags', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'noThrowGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noSquirtGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noZapGags', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'noSoundGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noDropGags', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'BanLureSound':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'noToonUpGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noTrapGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noLureGags', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'noThrowGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noSquirtGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noZapGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noSoundGags', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'noDropGags', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'BanLureDrop':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'noToonUpGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noTrapGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noLureGags', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'noThrowGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noSquirtGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noZapGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noSoundGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noDropGags', 1, 3, 'setBoth')
            elif atkInfo['name'] == 'BanThrowSquirt':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'noToonUpGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noTrapGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noLureGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noThrowGags', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'noSquirtGags', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'noZapGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noSoundGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noDropGags', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'BanThrowZap':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'noToonUpGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noTrapGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noLureGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noThrowGags', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'noSquirtGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noZapGags', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'noSoundGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noDropGags', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'BanThrowSound':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'noToonUpGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noTrapGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noLureGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noThrowGags', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'noSquirtGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noZapGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noSoundGags', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'noDropGags', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'BanThrowDrop':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'noToonUpGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noTrapGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noLureGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noThrowGags', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'noSquirtGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noZapGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noSoundGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noDropGags', 1, 3, 'setBoth')
            elif atkInfo['name'] == 'BanSquirtZap':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'noToonUpGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noTrapGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noLureGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noThrowGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noSquirtGags', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'noZapGags', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'noSoundGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noDropGags', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'BanSquirtSound':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'noToonUpGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noTrapGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noLureGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noThrowGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noSquirtGags', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'noZapGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noSoundGags', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'noDropGags', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'BanSquirtDrop':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'noToonUpGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noTrapGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noLureGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noThrowGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noSquirtGags', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'noZapGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noSoundGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noDropGags', 1, 3, 'setBoth')
            elif atkInfo['name'] == 'BanZapSound':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'noToonUpGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noTrapGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noLureGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noThrowGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noSquirtGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noZapGags', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'noSoundGags', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'noDropGags', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'BanZapDrop':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'noToonUpGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noTrapGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noLureGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noThrowGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noSquirtGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noZapGags', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'noSoundGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noDropGags', 1, 3, 'setBoth')
            elif atkInfo['name'] == 'BanSoundDrop':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'noToonUpGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noTrapGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noLureGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noThrowGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noSquirtGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noZapGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noSoundGags', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'noDropGags', 1, 3, 'setBoth')
            else:
                attack[SUIT_HP_COL][targetIndex] = result

            if self.suitHasCondition(theSuit.doId, 'desperation') and self.suitHasCondition(theSuit.doId, 'enraged') and theSuit.getHP() > (theSuit.getMaxHP() * 1.5):
                attack[SUIT_HP_COL][targetIndex] *= (1.2 + self.getToonConditionModifier(toonId, 'snapped') + self.getToonConditionModifier(toonId, 'corruption') + theSuit.getDamageMultiplier())
            elif self.suitHasCondition(theSuit.doId, 'desperation') and theSuit.getHP() > (theSuit.getMaxHP() * 1.5):
                attack[SUIT_HP_COL][targetIndex] *= (.9 + self.getToonConditionModifier(toonId, 'snapped') + self.getToonConditionModifier(toonId, 'corruption') + theSuit.getDamageMultiplier())
            elif theSuit.getHP() > (theSuit.getMaxHP() * 1.5):
                attack[SUIT_HP_COL][targetIndex] *= (.5 + self.getToonConditionModifier(toonId, 'snapped') + self.getToonConditionModifier(toonId, 'corruption') + theSuit.getDamageMultiplier())
            elif self.suitHasCondition(theSuit.doId, 'desperation') and self.suitHasCondition(theSuit.doId, 'enraged'):
                attack[SUIT_HP_COL][targetIndex] *= (.83 + self.getToonConditionModifier(toonId, 'snapped') + self.getToonConditionModifier(toonId, 'corruption') + theSuit.getDamageMultiplier())
            elif self.suitHasCondition(theSuit.doId, 'desperation'):
                attack[SUIT_HP_COL][targetIndex] *= (.4 + self.getToonConditionModifier(toonId, 'snapped') + self.getToonConditionModifier(toonId, 'corruption') + theSuit.getDamageMultiplier())
            else:
                attack[SUIT_HP_COL][targetIndex] = result * (
                            self.getToonConditionModifier(toonId, 'corruption') + self.getToonConditionModifier(toonId,
                                                                                                                'snapped') + theSuit.getDamageMultiplier())
            if self.suitHasCondition(theSuit.doId, 'lured'):
                self.setSuitCondition(theSuit.doId, 'lured', 1, 1, 'setBoth')
            self.notify.debug('__calcSuitAtkHp - result is %s for index %i' % (str(attack[SUIT_HP_COL][targetIndex]), targetIndex))

    def __getToonHp(self, toonDoId):
        handle = self.battle.getToon(toonDoId)
        if handle != None and toonDoId in self.toonHPAdjusts:
            return handle.hp + self.toonHPAdjusts[toonDoId]
        else:
            return 0

    def __getToonMaxHp(self, toonDoId):
        handle = self.battle.getToon(toonDoId)
        if handle != None:
            return handle.maxHp
        else:
            return 0

    def __applySuitAttackDamages(self, attack, theSuit):
        if APPLY_HEALTH_ADJUSTMENTS:
            for t in self.battle.activeToons:
                position = self.battle.activeToons.index(t)
                if attack[SUIT_HP_COL][position] <= 0:
                    continue
                toonHp = self.__getToonHp(t)
                if theSuit.dna.name == 'ssb':
                    if attack[SUIT_ATK_COL] in [0, 2]:
                        self.notify.debug('__applySuitAttackDamages - applying corruption on toon %s' % str(t))
                        self.setToonCondition(t, 'corruption', 2, -2, 'refreshTurns')
                        if attack[SUIT_ATK_COL] == 0:
                            self.notify.debug(
                                '__applySuitAttackDamages - applying corruption on toon %s two additional times' % str(
                                    t))
                            self.setToonCondition(t, 'corruption', 4, -2, 'refreshTurns')
                    else:
                        self.notify.debug(
                            '__applySuitAttackDamages - We are a shadow, but we did not use corruption, not corrupting.')
                        self.toonHPAdjusts[t] -= 0  # toons take no damage from this cheat
                        return
                #if theSuit.dna.name == 'gtk' and attack[SUIT_ATK_COL] == 1:
                    #self.notify.debug('__applySuitAttackDamages - applying corruption on toon %s four times' % str(t))
                    #self.setToonCondition(t, 'corruption', 4, 3, 'setBoth')
                #if theSuit.dna.name == 'lit' and attack[SUIT_ATK_COL] == 1:
                    #self.notify.debug('__applySuitAttackDamages - applying corruption on toon %s four times' % str(t))
                    #self.setToonCondition(t, 'corruption', 4, 3, 'setBoth')
                if theSuit.dna.name == 'trk' and attack[SUIT_ATK_COL] == 0:
                    # FlameColumn - Burns the target, reducing damage output by 75%.
                    self.setToonCondition(t, 'allGagBoost', -75, 3, 'setBoth')
                #if theSuit.dna.name == 'lit' and attack[SUIT_ATK_COL] == 2:
                    #self.notify.debug('__applySuitAttackDamages - applying corruption on toon %s four times' % str(t))
                    #self.setToonCondition(t, 'corruption', 2, 3, 'setBoth')
                if toonHp - attack[SUIT_HP_COL][position] <= 0:
                    if self.notify.getDebug():
                        self.notify.debug('Toon %d has died, removing' % t)
                    self.toonLeftBattle(t)
                    attack[TOON_DIED_COL] = attack[TOON_DIED_COL] | 1 << position
                self.toonHPAdjusts[t] -= attack[SUIT_HP_COL][position]

    def __suitCanAttack(self, suitId):
        if self.__combatantDead(suitId, toon=0) or self.__suitIsLured(suitId):
            return 0
        return 1

    def __updateSuitAtkStat(self, toonId):
        if toonId in self.suitAtkStats:
            self.suitAtkStats[toonId] += 1
        else:
            self.suitAtkStats[toonId] = 1

    def __printSuitAtkStats(self):
        self.notify.debug('Suit Atk Stats:')
        for currTgt in self.suitAtkStats.keys():
            if currTgt not in self.battle.activeToons:
                continue
            tgtPos = self.battle.activeToons.index(currTgt)

        self.notify.debug('\n')

    def __calculateSuitAttacks(self):
        for i in xrange(len(self.battle.activeSuits)):
            #if i < len(self.battle.activeSuits):
                suitId = self.battle.activeSuits[i].doId
                # self.battle.suitAttacks[i][SUIT_ID_COL] = suitId
                if self.battle.activeSuits[i].dna.name == 'mad':
                    if self.battle.activeSuits[i].maxHP > 10000:
                        self.setSuitCondition(suitId, 'zapImmune', 0, 0, 'setBoth')
                        self.setSuitCondition(suitId, 'soakImmune', 0, 0, 'setBoth')
                        self.setSuitCondition(suitId, 'lureImmune', 0, 0, 'setBoth')
                        self.setSuitCondition(suitId, 'kbImmune', 0, 0, 'setBoth')
                    elif self.battle.activeSuits[i].maxHP > 9000:
                        self.setSuitCondition(suitId, 'soakImmune', 1, 99, 'setBoth')
                        self.setSuitCondition(suitId, 'zapImmune', 0, 0, 'setBoth')
                        self.setSuitCondition(suitId, 'lureImmune', 0, 0, 'setBoth')
                        self.setSuitCondition(suitId, 'kbImmune', 0, 0, 'setBoth')
                    elif self.battle.activeSuits[i].maxHP > 7000:
                        self.setSuitCondition(suitId, 'zapImmune', 0, 0, 'setBoth')
                        self.setSuitCondition(suitId, 'soakImmune', 0, 0, 'setBoth')
                        self.setSuitCondition(suitId, 'lureImmune', 0, 0, 'setBoth')
                        self.setSuitCondition(suitId, 'kbImmune', 0, 0, 'setBoth')
                    elif self.battle.activeSuits[i].maxHP > 6000:
                        self.setSuitCondition(suitId, 'zapImmune', 1, 99, 'setBoth')
                        self.setSuitCondition(suitId, 'soakImmune', 0, 0, 'setBoth')
                        self.setSuitCondition(suitId, 'lureImmune', 0, 0, 'setBoth')
                        self.setSuitCondition(suitId, 'kbImmune', 0, 0, 'setBoth')
                    elif self.battle.activeSuits[i].maxHP > 5000:
                        self.setSuitCondition(suitId, 'zapImmune', 0, 0, 'setBoth')
                        self.setSuitCondition(suitId, 'soakImmune', 0, 0, 'setBoth')
                        self.setSuitCondition(suitId, 'lureImmune', 0, 0, 'setBoth')
                        self.setSuitCondition(suitId, 'kbImmune', 0, 0, 'setBoth')
                    elif self.battle.activeSuits[i].maxHP > 0:
                        self.setSuitCondition(suitId, 'zapImmune', 0, 0, 'setBoth')
                        self.setSuitCondition(suitId, 'soakImmune', 0, 0, 'setBoth')
                        self.setSuitCondition(suitId, 'lureImmune', 1, 99, 'setBoth')
                        self.setSuitCondition(suitId, 'kbImmune', 0, 0, 'setBoth')

                if not self.__suitCanAttack(suitId):
                    if self.battle.activeSuits[i].dna.name == 'ste':
                        x = self.TurnsElapsed
                        currentBossHealth = -1
                        for s in self.battle.suits:
                            if s.dna.name == 'scg' or s.dna.name == 'lit' or s.dna.name == 'csm':
                                currentBossHealth = s.currHP
                        if currentBossHealth == -1 and not self.suitHasCondition(suitId, 'desperation'):
                            self.setSuitCondition(suitId, 'desperation', 1, 100, 'setBoth')
                    if self.battle.activeSuits[i].dna.name == 'csm':
                        x = self.TurnsElapsed
                        currentBossHealth = -1
                        for s in self.battle.suits:
                            if s.dna.name == 'ste' or s.dna.name == 'lit' or s.dna.name == 'scg':
                                currentBossHealth = s.currHP
                        if currentBossHealth == -1 and not self.suitHasCondition(theSuit.doId, 'desperation'):
                            self.setSuitCondition(suitId, 'desperation', 1, 100, 'setBoth')
                        if x % 3 == 0 and not self.suitHasCondition(suitId, 'desperation'):
                            self.setSuitCondition(suitId, 'insurancecalculator', 1, 10, 'setBoth')
                    if self.battle.activeSuits[i].dna.name == 'lit':
                        x = self.TurnsElapsed
                        currentBossHealth = -1
                        for s in self.battle.suits:
                            if s.dna.name == 'ste' or s.dna.name == 'scg' or s.dna.name == 'csm':
                                currentBossHealth = s.currHP
                        if currentBossHealth == -1 and not self.suitHasCondition(suitId, 'desperation'):
                            self.setSuitCondition(suitId, 'desperation', 1, 100, 'setBoth')
                        if len(self.battle.activeSuits) < 6:
                            self.setSuitCondition(suitId, 'bashcalculator', 1, 10, 'setBoth')
                        if len(self.battle.activeSuits) >= 6 and x % 3 == 0:
                            self.setSuitCondition(suitId, 'bellowcalculator', 1, 10, 'setBoth')
                        if x % 3 == 0 and not self.suitHasCondition(suitId, 'desperation'):
                            self.setSuitCondition(suitId, 'snappedcalculator', 1, 10, 'setBoth')
                    if self.battle.activeSuits[i].dna.name == 'scg':
                        x = self.TurnsElapsed
                        currentBossHealth = -1
                        for s in self.battle.suits:
                            if s.dna.name == 'ste' or s.dna.name == 'lit' or s.dna.name == 'csm':
                                currentBossHealth = s.currHP
                        if currentBossHealth == -1 and not self.suitHasCondition(suitId, 'desperation'):
                            self.setSuitCondition(suitId, 'desperation', 1, 100, 'setBoth')
                    if self.battle.activeSuits[i].dna.name == 'fbd':
                        x = self.TurnsElapsed
                        currentBossHealth = -1
                        for s in self.battle.suits:
                            if s.dna.name == 'gtk' or s.dna.name == 'cp' or s.dna.name == 'frs':
                                currentBossHealth = s.currHP
                        if currentBossHealth == -1 and not self.suitHasCondition(suitId, 'desperation'):
                            self.setSuitCondition(suitId, 'desperation', 1, 100, 'setBoth')
                        if x % 3 == 0:
                            self.setSuitCondition(suitId, 'explodingbillcalculator', 1, 10, 'setBoth')
                    if self.battle.activeSuits[i].dna.name == 'frs':
                        x = self.TurnsElapsed
                        currentBossHealth = -1
                        for s in self.battle.suits:
                            if s.dna.name == 'gtk' or s.dna.name == 'fbd' or s.dna.name == 'cp':
                                currentBossHealth = s.currHP
                        if currentBossHealth == -1 and not self.suitHasCondition(suitId, 'desperation'):
                            self.setSuitCondition(suitId, 'desperation', 1, 100, 'setBoth')
                        if x % 3 == 0:
                            self.setSuitCondition(suitId, 'collectcallfeescalculator', 1, 10, 'setBoth')
                    if self.battle.activeSuits[i].dna.name == 'gtk':
                        x = self.TurnsElapsed
                        currentBossHealth = -1
                        for s in self.battle.suits:
                            if s.dna.name == 'cp' or s.dna.name == 'fbd' or s.dna.name == 'frs':
                                currentBossHealth = s.currHP
                        if currentBossHealth == -1 and not self.suitHasCondition(suitId, 'desperation'):
                            self.setSuitCondition(suitId, 'desperation', 1, 100, 'setBoth')
                        if x % 3 == 0:
                            self.setSuitCondition(suitId, 'refinementcalculator', 1, 10, 'setBoth')
                    if self.battle.activeSuits[i].dna.name == 'cp':
                        x = self.TurnsElapsed
                        currentBossHealth = -1
                        for s in self.battle.suits:
                            if s.dna.name == 'gtk' or s.dna.name == 'fbd' or s.dna.name == 'frs':
                                currentBossHealth = s.currHP
                        if currentBossHealth == -1 and not self.suitHasCondition(suitId, 'desperation'):
                            self.setSuitCondition(suitId, 'desperation', 1, 100, 'setBoth')
                        if x % 3 == 0:
                            self.setSuitCondition(suitId, 'rotationcalculator', 1, 10, 'setBoth')
                    if self.battle.activeSuits[i].dna.name == 'blr':
                        x = self.TurnsElapsed
                        currentBossHealth = -1
                        for s in self.battle.suits:
                            if s.dna.name == 'dsk' or s.dna.name == 'dvp' or s.dna.name == 'ffm':
                                currentBossHealth = s.currHP
                        if currentBossHealth == -1 and not self.suitHasCondition(suitId, 'desperation'):
                            self.setSuitCondition(suitId, 'desperation', 1, 100, 'setBoth')
                        if x % 4 == 0:
                            self.setSuitCondition(suitId, 'costscalculator', 1, 10, 'setBoth')
                    if self.battle.activeSuits[i].dna.name == 'dsk':
                        x = self.TurnsElapsed
                        currentBossHealth = -1
                        for s in self.battle.suits:
                            if s.dna.name == 'dvp' or s.dna.name == 'blr' or s.dna.name == 'ffm':
                                currentBossHealth = s.currHP
                        if currentBossHealth == -1 and not self.suitHasCondition(suitId, 'desperation'):
                            self.setSuitCondition(suitId, 'desperation', 1, 100, 'setBoth')
                        if x % 3 == 0:
                            self.setSuitCondition(suitId, 'insurancecalculator', 1, 10, 'setBoth')
                    if self.battle.activeSuits[i].dna.name == 'dvp':
                        x = self.TurnsElapsed
                        currentBossHealth = -1
                        for s in self.battle.suits:
                            if s.dna.name == 'blr' or s.dna.name == 'dsk' or s.dna.name == 'ffm':
                                currentBossHealth = s.currHP
                        if currentBossHealth == -1 and not self.suitHasCondition(suitId, 'desperation'):
                            self.setSuitCondition(suitId, 'desperation', 1, 100, 'setBoth')
                        if x % 4 == 0:
                            self.setSuitCondition(suitId, 'costscalculator', 1, 10, 'setBoth')
                    if self.battle.activeSuits[i].dna.name == 'ffm':
                        x = self.TurnsElapsed
                        currentBossHealth = -1
                        for s in self.battle.suits:
                            if s.dna.name == 'blr' or s.dna.name == 'dsk' or s.dna.name == 'dvp':
                                currentBossHealth = s.currHP
                        if currentBossHealth == -1 and not self.suitHasCondition(suitId, 'desperation'):
                            self.setSuitCondition(suitId, 'desperation', 1, 100, 'setBoth')
                        if x % 3 == 0 and not self.suitHasCondition(suitId, 'desperation'):
                            self.setSuitCondition(suitId, 'costscalculator', 1, 10, 'setBoth')
                    if self.battle.activeSuits[i].dna.name == 'fbd':
                        x = self.TurnsElapsed
                        currentBossHealth = -1
                        for s in self.battle.suits:
                            if s.dna.name == 'gtk' or s.dna.name == 'cp' or s.dna.name == 'frs':
                                currentBossHealth = s.currHP
                        if currentBossHealth == -1 and not self.suitHasCondition(suitId, 'desperation'):
                            self.setSuitCondition(suitId, 'desperation', 1, 100, 'setBoth')
                        if x % 3 == 0:
                            self.setSuitCondition(suitId, 'explodingbillcalculator', 1, 10, 'setBoth')
                    if self.battle.activeSuits[i].dna.name == 'cry':
                        x = self.TurnsElapsed
                        currentBossHealth = -1
                        for s in self.battle.suits:
                            if s.dna.name == 'dvk' or s.dna.name == 'otm' or s.dna.name == 'tcm':
                                currentBossHealth = s.currHP
                        if currentBossHealth == -1 and not self.suitHasCondition(suitId, 'desperation'):
                            self.setSuitCondition(suitId, 'desperation', 1, 100, 'setBoth')
                        if x % 3 == 0:
                            self.setSuitCondition(suitId, 'costscalculator', 1, 10, 'setBoth')
                    if self.battle.activeSuits[i].dna.name == 'dvk':
                        x = self.TurnsElapsed
                        currentBossHealth = -1
                        for s in self.battle.suits:
                            if s.dna.name == 'cry' or s.dna.name == 'otm' or s.dna.name == 'tcm':
                                currentBossHealth = s.currHP
                        if currentBossHealth == -1 and not self.suitHasCondition(suitId, 'desperation'):
                            self.setSuitCondition(suitId, 'desperation', 1, 100, 'setBoth')
                        if x % 4 == 0:
                            self.setSuitCondition(suitId, 'insurancecalculator', 1, 10, 'setBoth')
                        if x % 3 == 0:
                            self.setSuitCondition(suitId, 'costscalculator', 1, 10, 'setBoth')
                    if self.battle.activeSuits[i].dna.name == 'tcm':
                        x = self.TurnsElapsed
                        currentBossHealth = -1
                        for s in self.battle.suits:
                            if s.dna.name == 'dvk' or s.dna.name == 'otm' or s.dna.name == 'cry':
                                currentBossHealth = s.currHP
                        if currentBossHealth == -1 and not self.suitHasCondition(suitId, 'desperation'):
                            self.setSuitCondition(suitId, 'desperation', 1, 100, 'setBoth')
                        if x % 3 == 0:
                            self.setSuitCondition(suitId, 'costscalculator', 1, 10, 'setBoth')
                    if self.battle.activeSuits[i].dna.name == 'otm':
                        x = self.TurnsElapsed
                        currentBossHealth = -1
                        for s in self.battle.suits:
                            if s.dna.name == 'dvk' or s.dna.name == 'tcm' or s.dna.name == 'cry':
                                currentBossHealth = s.currHP
                        if currentBossHealth == -1 and not self.suitHasCondition(suitId, 'desperation'):
                            self.setSuitCondition(suitId, 'desperation', 1, 100, 'setBoth')
                        if x % 3 == 0 and not self.suitHasCondition(suitId, 'desperation'):
                            self.setSuitCondition(suitId, 'costscalculator', 1, 10, 'setBoth')
                    if self.notify.getDebug():
                        self.notify.debug("Suit %d can't attack" % suitId)
                    if self.notify.getDebug():
                        self.notify.debug("Suit %d can't attack" % suitId)
                    continue
                if self.battle.pendingSuits.count(self.battle.activeSuits[i]) > 0 or self.battle.joiningSuits.count(self.battle.activeSuits[i]) > 0:
                    continue
                attack = getDefaultSuitAttack()
                attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                attack[SUIT_ATK_COL] = self.__calcSuitAtkType(self.battle.activeSuits[i])
                attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                if attack[SUIT_TGT_COL] == []:
                    attack = getDefaultSuitAttack()
                attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                self.__calcSuitAtkHp(attack)
                if attack[SUIT_ATK_COL] != NO_ATTACK:
                    if self.__suitAtkAffectsGroup(attack):
                        for currTgt in self.battle.activeToons:
                            self.__updateSuitAtkStat(currTgt)


                    else:
                        for currTgt in attack[SUIT_TGT_COL]:
                            self.__updateSuitAtkStat(self.battle.activeToons[currTgt])
                targets = self.__createSuitTargetList(attack)
                allTargetsDead = True
                for currTgt in targets:
                    if self.__getToonHp(currTgt) > 0:
                        allTargetsDead = False
                        break

                if allTargetsDead:
                    attack = getDefaultSuitAttack()
                if self.__attackHasHit(attack, suit=1):
                    self.__applySuitAttackDamages(attack, self.battle.findSuit(attack[SUIT_ID_COL]))
                attack[SUIT_BEFORE_TOONS_COL] = 0
                self.battle.suitAttacks.append(attack)



        for i in xrange(len(self.battle.activeSuits)): # Cheat Calculators
            suitId = self.battle.activeSuits[i].doId
            x = self.TurnsElapsed
            if self.battle.activeSuits[i].dna.name == 'ste':
                if (x + 1) % 3 == 0:
                    self.setSuitCondition(suitId, 'sanctioncalculator', 1, 9, 'setBoth')
                if (x + 3) % 3 == 0:
                    self.setSuitCondition(suitId, 'calculatingcalculator', 1, 10, 'setBoth')
            if self.battle.activeSuits[i].dna.name == 'csm':
                if x % 3 == 0:
                    self.setSuitCondition(suitId, 'bindingscalculator2', 1, 9, 'setBoth')
                if (x + 2) % 3 == 0:
                    self.setSuitCondition(suitId, 'bindingscalculator', 1, 9, 'setBoth')
                if (x + 3) % 3 == 0:
                    self.setSuitCondition(suitId, 'insurancecalculator', 1, 10, 'setBoth')
            if self.battle.activeSuits[i].dna.name == 'lit':
                if x % 99 == 0:
                    self.setSuitCondition(suitId, 'bashcalculator', 1, 10, 'setBoth')
                if (x + 2) % 3 == 0:
                    self.setSuitCondition(suitId, 'snappedcalculator', 1, 10, 'setBoth')
                if self.battle.activeSuits[i].currHP <= 4000 and not self.suitHasCondition(suitId, 'bash1'):
                    self.setSuitCondition(suitId, 'bash1', 1, 99, 'setBoth')
                if self.battle.activeSuits[i].currHP <= 3000 and not self.suitHasCondition(suitId, 'bash2'):
                    self.setSuitCondition(suitId, 'bash2', 1, 99, 'setBoth')
                if self.battle.activeSuits[i].currHP <= 2000 and not self.suitHasCondition(suitId, 'bash3'):
                    self.setSuitCondition(suitId, 'bash3', 1, 99, 'setBoth')
                if self.battle.activeSuits[i].currHP <= 1000 and not self.suitHasCondition(suitId, 'bash4'):
                    self.setSuitCondition(suitId, 'bash4', 1, 99, 'setBoth')
                if x % 4 and len(self.battle.activeSuits) < 4 and not self.suitHasCondition(suitId, 'bash1') and not self.suitHasCondition(suitId, 'bash2') and not self.suitHasCondition(suitId, 'bash3') \
                        and not self.suitHasCondition(suitId, 'bash4'):
                    self.setSuitCondition(suitId, 'bashcalculator', 1, 10, 'setBoth')
                if x % 4 and len(self.battle.activeSuits) < 5 and self.suitHasCondition(suitId, 'bash1') and not self.suitHasCondition(suitId, 'bash2') and not self.suitHasCondition(suitId, 'bash3') \
                        and not self.suitHasCondition(suitId, 'bash4'):
                    self.setSuitCondition(suitId, 'bashcalculator', 1, 10, 'setBoth')
                if len(self.battle.activeSuits) >= 5 and x % 4 == 0 and self.suitHasCondition(suitId, 'bash1') and not self.suitHasCondition(suitId, 'bash2') and not self.suitHasCondition(suitId, 'bash3') \
                        and not self.suitHasCondition(suitId, 'bash4'):
                    self.setSuitCondition(suitId, 'bellowcalculator', 1, 10, 'setBoth')
                if x % 3 and len(self.battle.activeSuits) < 6 and self.suitHasCondition(suitId, 'bash1') and self.suitHasCondition(suitId, 'bash2') and not self.suitHasCondition(suitId, 'bash3') \
                        and not self.suitHasCondition(suitId, 'bash4'):
                    self.setSuitCondition(suitId, 'bashcalculator', 1, 10, 'setBoth')
                if len(self.battle.activeSuits) >= 6 and x % 3 == 0 and self.suitHasCondition(suitId, 'bash1') and self.suitHasCondition(suitId, 'bash2') and not self.suitHasCondition(suitId, 'bash3') \
                        and not self.suitHasCondition(suitId, 'bash4'):
                    self.setSuitCondition(suitId, 'bellowcalculator', 1, 10, 'setBoth')
                if x % 2 and len(self.battle.activeSuits) < 6 and self.suitHasCondition(suitId, 'bash1') and self.suitHasCondition(suitId, 'bash2') and self.suitHasCondition(suitId, 'bash3') \
                        and not self.suitHasCondition(suitId, 'bash4'):
                    self.setSuitCondition(suitId, 'bashcalculator', 1, 10, 'setBoth')
                if len(self.battle.activeSuits) >= 6 and x % 2 == 0 and self.suitHasCondition(suitId, 'bash1') and self.suitHasCondition(suitId, 'bash2') and self.suitHasCondition(suitId, 'bash3') \
                        and not self.suitHasCondition(suitId, 'bash4'):
                    self.setSuitCondition(suitId, 'bellowcalculator', 1, 10, 'setBoth')
                if x % 1 and len(self.battle.activeSuits) < 6 and self.suitHasCondition(suitId, 'bash1') and self.suitHasCondition(suitId,
                                                                                              'bash2') and self.suitHasCondition(
                        suitId, 'bash3') \
                        and self.suitHasCondition(suitId, 'bash4') and not self.suitHasCondition(suitId, 'bash5'):
                    self.setSuitCondition(suitId, 'bashcalculator', 1, 10, 'setBoth')
                if len(self.battle.activeSuits) >= 6 and x % 1 == 0 and self.suitHasCondition(suitId,
                                                                                              'bash1') and self.suitHasCondition(
                        suitId, 'bash2') and self.suitHasCondition(suitId, 'bash3') \
                        and self.suitHasCondition(suitId, 'bash4'):
                    self.setSuitCondition(suitId, 'bellowcalculator', 1, 10, 'setBoth')
            if self.battle.activeSuits[i].dna.name == 'scg':
                if (x + 3) % 3 == 0:
                    self.setSuitCondition(suitId, 'gavelcalculator', 1, 10, 'setBoth')
            if self.battle.activeSuits[i].dna.name == 'cp': #powerhouse
                if x % 3 == 0:
                    self.setSuitCondition(suitId, 'rotationcalculator', 1, 10, 'setBoth')
            if self.battle.activeSuits[i].dna.name == 'fbd':  # bookkeeper
                if (x + 1) % 3 == 0:
                    self.setSuitCondition(suitId, 'explodingcalculator', 1, 9, 'setBoth')
                if (x + 2) % 3 == 0:
                    self.setSuitCondition(suitId, 'papercutcalculator', 1, 10, 'setBoth')
                if x % 5 == 0:
                    self.setSuitCondition(suitId, 'bookkeepingcalculator', 1, 10, 'setBoth')
            if self.battle.activeSuits[i].dna.name == 'frs':  # wiretapper
                if (x + 2) % 3 == 0:
                    self.setSuitCondition(suitId, 'wiretappedcalculator', 1, 9, 'setBoth')
                if (x + 3) % 3 == 0:
                    self.setSuitCondition(suitId, 'collectcallcalculator', 1, 10, 'setBoth')
                if len(self.battle.activeSuits) >= 6 and x % 3 == 0:
                    self.setSuitCondition(suitId, 'voicemailcalculator', 1, 10, 'setBoth')
            if self.battle.activeSuits[i].dna.name == 'gtk': #ambassador
                if (x + 2) % 3 == 0:
                    self.setSuitCondition(suitId, 'refinementcalculator', 1, 10, 'setBoth')
                if x % 4 and (len(self.battle.activeSuits) >= 3 and len(self.battle.activeSuits) <= 6) and not self.suitHasCondition(suitId, 'desperation'):
                    self.setSuitCondition(suitId, 'headrollercalculator', 1, 10, 'setBoth')
                if len(self.battle.activeSuits) >= 6 and x % 3 == 0 and self.suitHasCondition(suitId, 'desperation'):
                    self.setSuitCondition(suitId, 'headroller2calculator', 1, 10, 'setBoth')
        
        # The cheaters who act after all above attacks have played.
        for i in xrange(len(self.battle.activeSuits)): # Gag Banning Retaliation
            suitId = self.battle.activeSuits[i].doId
            x = self.TurnsElapsed
            if self.battle.activeSuits[i].dna.name == 'ste':
                if self.TurnsElapsed % 1 == 0:
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = 24  # Court Record Retaliation
                    attack[SUIT_TGT_COL] = self.__calcSuitTargetALT(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL] != NO_ATTACK:
                        if self.__suitAtkAffectsGroup(attack):
                            for currTgt in self.battle.activeToons:
                                self.__updateSuitAtkStat(currTgt)

                        else:
                            for currTgt in attack[SUIT_TGT_COL]:
                                self.__updateSuitAtkStat(self.battle.activeToons[currTgt])
                    targets = self.__createSuitTargetList(attack)
                    allTargetsDead = True
                    for currTgt in targets:
                        if self.__getToonHp(currTgt) > 0:
                            allTargetsDead = False
                            break

                    if allTargetsDead:
                        attack = getDefaultSuitAttack()
                    if self.__attackHasHit(attack, suit=1):
                        self.__applySuitAttackDamages(attack, self.battle.findSuit(attack[SUIT_ID_COL]))
                    attack[SUIT_BEFORE_TOONS_COL] = 0
                    self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'csm':
                if self.TurnsElapsed % 1 == 0:
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = 44  # Legally Bound
                    attack[SUIT_TGT_COL] = self.__calcSuitTargetALT(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL] != NO_ATTACK:
                        if self.__suitAtkAffectsGroup(attack):
                            for currTgt in self.battle.activeToons:
                                self.__updateSuitAtkStat(currTgt)

                        else:
                            for currTgt in attack[SUIT_TGT_COL]:
                                self.__updateSuitAtkStat(self.battle.activeToons[currTgt])
                    targets = self.__createSuitTargetList(attack)
                    allTargetsDead = True
                    for currTgt in targets:
                        if self.__getToonHp(currTgt) > 0:
                            allTargetsDead = False
                            break

                    if allTargetsDead:
                        attack = getDefaultSuitAttack()
                    if self.__attackHasHit(attack, suit=1):
                        self.__applySuitAttackDamages(attack, self.battle.findSuit(attack[SUIT_ID_COL]))
                    attack[SUIT_BEFORE_TOONS_COL] = 0
                    self.battle.suitAttacks.append(attack)
                if self.TurnsElapsed % 1 == 0:
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = 45  # Court Record Ban Retaliation
                    attack[SUIT_TGT_COL] = self.__calcSuitTargetALT(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL] != NO_ATTACK:
                        if self.__suitAtkAffectsGroup(attack):
                            for currTgt in self.battle.activeToons:
                                self.__updateSuitAtkStat(currTgt)

                        else:
                            for currTgt in attack[SUIT_TGT_COL]:
                                self.__updateSuitAtkStat(self.battle.activeToons[currTgt])
                    targets = self.__createSuitTargetList(attack)
                    allTargetsDead = True
                    for currTgt in targets:
                        if self.__getToonHp(currTgt) > 0:
                            allTargetsDead = False
                            break

                    if allTargetsDead:
                        attack = getDefaultSuitAttack()
                    if self.__attackHasHit(attack, suit=1):
                        self.__applySuitAttackDamages(attack, self.battle.findSuit(attack[SUIT_ID_COL]))
                    attack[SUIT_BEFORE_TOONS_COL] = 0
                    self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'cp':
                if self.TurnsElapsed % 1 == 0:
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = 12  # Snipe Retaliation For Gag Bans
                    attack[SUIT_TGT_COL] = self.__calcSuitTargetALT(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL] != NO_ATTACK:
                        if self.__suitAtkAffectsGroup(attack):
                            for currTgt in self.battle.activeToons:
                                self.__updateSuitAtkStat(currTgt)

                        else:
                            for currTgt in attack[SUIT_TGT_COL]:
                                self.__updateSuitAtkStat(self.battle.activeToons[currTgt])
                    targets = self.__createSuitTargetList(attack)
                    allTargetsDead = True
                    for currTgt in targets:
                        if self.__getToonHp(currTgt) > 0:
                            allTargetsDead = False
                            break

                    if allTargetsDead:
                        attack = getDefaultSuitAttack()
                    if self.__attackHasHit(attack, suit=1):
                        self.__applySuitAttackDamages(attack, self.battle.findSuit(attack[SUIT_ID_COL]))
                    attack[SUIT_BEFORE_TOONS_COL] = 0
                    self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'fbd':
                if self.TurnsElapsed % 1 == 0 and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = 11  # Bookkeeping Retaliation
                    attack[SUIT_TGT_COL] = self.__calcSuitTargetALT(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL] != NO_ATTACK:
                        if self.__suitAtkAffectsGroup(attack):
                            for currTgt in self.battle.activeToons:
                                self.__updateSuitAtkStat(currTgt)

                        else:
                            for currTgt in attack[SUIT_TGT_COL]:
                                self.__updateSuitAtkStat(self.battle.activeToons[currTgt])
                    targets = self.__createSuitTargetList(attack)
                    allTargetsDead = True
                    for currTgt in targets:
                        if self.__getToonHp(currTgt) > 0:
                            allTargetsDead = False
                            break

                    if allTargetsDead:
                        attack = getDefaultSuitAttack()
                    if self.__attackHasHit(attack, suit=1):
                        self.__applySuitAttackDamages(attack, self.battle.findSuit(attack[SUIT_ID_COL]))
                    attack[SUIT_BEFORE_TOONS_COL] = 0
                    self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'frs':
                if self.TurnsElapsed % 1 == 0:
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = 7  # Collect Call Fees
                    attack[SUIT_TGT_COL] = self.__calcSuitTargetALT(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL] != NO_ATTACK:
                        if self.__suitAtkAffectsGroup(attack):
                            for currTgt in self.battle.activeToons:
                                self.__updateSuitAtkStat(currTgt)

                        else:
                            for currTgt in attack[SUIT_TGT_COL]:
                                self.__updateSuitAtkStat(self.battle.activeToons[currTgt])
                    targets = self.__createSuitTargetList(attack)
                    allTargetsDead = True
                    for currTgt in targets:
                        if self.__getToonHp(currTgt) > 0:
                            allTargetsDead = False
                            break

                    if allTargetsDead:
                        attack = getDefaultSuitAttack()
                    if self.__attackHasHit(attack, suit=1):
                        self.__applySuitAttackDamages(attack, self.battle.findSuit(attack[SUIT_ID_COL]))
                    attack[SUIT_BEFORE_TOONS_COL] = 0
                    self.battle.suitAttacks.append(attack)
                if self.TurnsElapsed % 1 == 0:
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = 24  # Budget Cuts Gag Ban Retaliation
                    attack[SUIT_TGT_COL] = self.__calcSuitTargetALT(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL] != NO_ATTACK:
                        if self.__suitAtkAffectsGroup(attack):
                            for currTgt in self.battle.activeToons:
                                self.__updateSuitAtkStat(currTgt)

                        else:
                            for currTgt in attack[SUIT_TGT_COL]:
                                self.__updateSuitAtkStat(self.battle.activeToons[currTgt])
                    targets = self.__createSuitTargetList(attack)
                    allTargetsDead = True
                    for currTgt in targets:
                        if self.__getToonHp(currTgt) > 0:
                            allTargetsDead = False
                            break

                    if allTargetsDead:
                        attack = getDefaultSuitAttack()
                    if self.__attackHasHit(attack, suit=1):
                        self.__applySuitAttackDamages(attack, self.battle.findSuit(attack[SUIT_ID_COL]))
                    attack[SUIT_BEFORE_TOONS_COL] = 0
                    self.battle.suitAttacks.append(attack)



        for i in xrange(len(self.battle.activeSuits)): # Primary Cheats
            suitId = self.battle.activeSuits[i].doId
            x = self.TurnsElapsed
            if self.battle.activeSuits[i].dna.name == 'ste':
                if (self.getSuitConditionTurns(suitId, 'sanctioncalculator2') == 9 and self.__suitCanAttack(
                        suitId)) or (
                        self.getSuitConditionTurns(suitId, 'sanctioncalculator2') == 8 and self.__suitCanAttack(
                        suitId)):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = 5  # Court Sanction Legal Bindings Retaliation
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL] != NO_ATTACK:
                        if self.__suitAtkAffectsGroup(attack):
                            for currTgt in self.battle.activeToons:
                                self.__updateSuitAtkStat(currTgt)

                        else:
                            for currTgt in attack[SUIT_TGT_COL]:
                                self.__updateSuitAtkStat(self.battle.activeToons[currTgt])
                    targets = self.__createSuitTargetList(attack)
                    allTargetsDead = True
                    for currTgt in targets:
                        if self.__getToonHp(currTgt) > 0:
                            allTargetsDead = False
                            break

                    if allTargetsDead:
                        attack = getDefaultSuitAttack()
                    if self.__attackHasHit(attack, suit=1):
                        self.__applySuitAttackDamages(attack, self.battle.findSuit(attack[SUIT_ID_COL]))
                    attack[SUIT_BEFORE_TOONS_COL] = 0
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'sanctioncalculator4') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = 5  # Court Sanction Legal Bindings Retaliation
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL] != NO_ATTACK:
                        if self.__suitAtkAffectsGroup(attack):
                            for currTgt in self.battle.activeToons:
                                self.__updateSuitAtkStat(currTgt)

                        else:
                            for currTgt in attack[SUIT_TGT_COL]:
                                self.__updateSuitAtkStat(self.battle.activeToons[currTgt])
                    targets = self.__createSuitTargetList(attack)
                    allTargetsDead = True
                    for currTgt in targets:
                        if self.__getToonHp(currTgt) > 0:
                            allTargetsDead = False
                            break

                    if allTargetsDead:
                        attack = getDefaultSuitAttack()
                    if self.__attackHasHit(attack, suit=1):
                        self.__applySuitAttackDamages(attack, self.battle.findSuit(attack[SUIT_ID_COL]))
                    attack[SUIT_BEFORE_TOONS_COL] = 0
                    self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'csm':
                if self.TurnsElapsed % 3 == 0 and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = 5  # Insurance Plan
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL] != NO_ATTACK:
                        if self.__suitAtkAffectsGroup(attack):
                            for currTgt in self.battle.activeToons:
                                self.__updateSuitAtkStat(currTgt)

                        else:
                            for currTgt in attack[SUIT_TGT_COL]:
                                self.__updateSuitAtkStat(self.battle.activeToons[currTgt])
                    targets = self.__createSuitTargetList(attack)
                    allTargetsDead = True
                    for currTgt in targets:
                        if self.__getToonHp(currTgt) > 0:
                            allTargetsDead = False
                            break

                    if allTargetsDead:
                        attack = getDefaultSuitAttack()
                    if self.__attackHasHit(attack, suit=1):
                        self.__applySuitAttackDamages(attack, self.battle.findSuit(attack[SUIT_ID_COL]))
                    attack[SUIT_BEFORE_TOONS_COL] = 0
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'insurancecalculator') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = 5  # Insurance Plan
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL] != NO_ATTACK:
                        if self.__suitAtkAffectsGroup(attack):
                            for currTgt in self.battle.activeToons:
                                self.__updateSuitAtkStat(currTgt)

                        else:
                            for currTgt in attack[SUIT_TGT_COL]:
                                self.__updateSuitAtkStat(self.battle.activeToons[currTgt])
                    targets = self.__createSuitTargetList(attack)
                    allTargetsDead = True
                    for currTgt in targets:
                        if self.__getToonHp(currTgt) > 0:
                            allTargetsDead = False
                            break

                    if allTargetsDead:
                        attack = getDefaultSuitAttack()
                    if self.__attackHasHit(attack, suit=1):
                        self.__applySuitAttackDamages(attack, self.battle.findSuit(attack[SUIT_ID_COL]))
                    attack[SUIT_BEFORE_TOONS_COL] = 0
                    self.battle.suitAttacks.append(attack)
                if self.TurnsElapsed % 1 == 0:
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = 43  # Insurance Healing
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL] != NO_ATTACK:
                        if self.__suitAtkAffectsGroup(attack):
                            for currTgt in self.battle.activeToons:
                                self.__updateSuitAtkStat(currTgt)

                        else:
                            for currTgt in attack[SUIT_TGT_COL]:
                                self.__updateSuitAtkStat(self.battle.activeToons[currTgt])
                    targets = self.__createSuitTargetList(attack)
                    allTargetsDead = True
                    for currTgt in targets:
                        if self.__getToonHp(currTgt) > 0:
                            allTargetsDead = False
                            break

                    if allTargetsDead:
                        attack = getDefaultSuitAttack()
                    if self.__attackHasHit(attack, suit=1):
                        self.__applySuitAttackDamages(attack, self.battle.findSuit(attack[SUIT_ID_COL]))
                    attack[SUIT_BEFORE_TOONS_COL] = 0
                    self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'scg':
                if self.suitHasCondition(suitId, 'gavelcalculator') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = 5  # Gavel
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL] != NO_ATTACK:
                        if self.__suitAtkAffectsGroup(attack):
                            for currTgt in self.battle.activeToons:
                                self.__updateSuitAtkStat(currTgt)

                        else:
                            for currTgt in attack[SUIT_TGT_COL]:
                                self.__updateSuitAtkStat(self.battle.activeToons[currTgt])
                    targets = self.__createSuitTargetList(attack)
                    allTargetsDead = True
                    for currTgt in targets:
                        if self.__getToonHp(currTgt) > 0:
                            allTargetsDead = False
                            break

                    if allTargetsDead:
                        attack = getDefaultSuitAttack()
                    if self.__attackHasHit(attack, suit=1):
                        self.__applySuitAttackDamages(attack, self.battle.findSuit(attack[SUIT_ID_COL]))
                    attack[SUIT_BEFORE_TOONS_COL] = 0
                    self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'lit':
                if self.suitHasCondition(suitId, 'soakedcalculator') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = 8  # Snap Soaked
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL] != NO_ATTACK:
                        if self.__suitAtkAffectsGroup(attack):
                            for currTgt in self.battle.activeToons:
                                self.__updateSuitAtkStat(currTgt)

                        else:
                            for currTgt in attack[SUIT_TGT_COL]:
                                self.__updateSuitAtkStat(self.battle.activeToons[currTgt])
                    targets = self.__createSuitTargetList(attack)
                    allTargetsDead = True
                    for currTgt in targets:
                        if self.__getToonHp(currTgt) > 0:
                            allTargetsDead = False
                            break

                    if allTargetsDead:
                        attack = getDefaultSuitAttack()
                    if self.__attackHasHit(attack, suit=1):
                        self.__applySuitAttackDamages(attack, self.battle.findSuit(attack[SUIT_ID_COL]))
                    attack[SUIT_BEFORE_TOONS_COL] = 0
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'snappedcalculator') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = 7  # Snap Most Dangerous
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL] != NO_ATTACK:
                        if self.__suitAtkAffectsGroup(attack):
                            for currTgt in self.battle.activeToons:
                                self.__updateSuitAtkStat(currTgt)

                        else:
                            for currTgt in attack[SUIT_TGT_COL]:
                                self.__updateSuitAtkStat(self.battle.activeToons[currTgt])
                    targets = self.__createSuitTargetList(attack)
                    allTargetsDead = True
                    for currTgt in targets:
                        if self.__getToonHp(currTgt) > 0:
                            allTargetsDead = False
                            break

                    if allTargetsDead:
                        attack = getDefaultSuitAttack()
                    if self.__attackHasHit(attack, suit=1):
                        self.__applySuitAttackDamages(attack, self.battle.findSuit(attack[SUIT_ID_COL]))
                    attack[SUIT_BEFORE_TOONS_COL] = 0
                    self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'gtk':  # ambassador
                if self.suitHasCondition(suitId, 'refinementcalculator') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = 8  # Refinement
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL] != NO_ATTACK:
                        if self.__suitAtkAffectsGroup(attack):
                            for currTgt in self.battle.activeToons:
                                self.__updateSuitAtkStat(currTgt)

                        else:
                            for currTgt in attack[SUIT_TGT_COL]:
                                self.__updateSuitAtkStat(self.battle.activeToons[currTgt])
                    targets = self.__createSuitTargetList(attack)
                    allTargetsDead = True
                    for currTgt in targets:
                        if self.__getToonHp(currTgt) > 0:
                            allTargetsDead = False
                            break

                    if allTargetsDead:
                        attack = getDefaultSuitAttack()
                    if self.__attackHasHit(attack, suit=1):
                        self.__applySuitAttackDamages(attack, self.battle.findSuit(attack[SUIT_ID_COL]))
                    attack[SUIT_BEFORE_TOONS_COL] = 0
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'headrollercalculator') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = 6  # Single Head Roller
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL] != NO_ATTACK:
                        if self.__suitAtkAffectsGroup(attack):
                            for currTgt in self.battle.activeToons:
                                self.__updateSuitAtkStat(currTgt)

                        else:
                            for currTgt in attack[SUIT_TGT_COL]:
                                self.__updateSuitAtkStat(self.battle.activeToons[currTgt])
                    targets = self.__createSuitTargetList(attack)
                    allTargetsDead = True
                    for currTgt in targets:
                        if self.__getToonHp(currTgt) > 0:
                            allTargetsDead = False
                            break

                    if allTargetsDead:
                        attack = getDefaultSuitAttack()
                    if self.__attackHasHit(attack, suit=1):
                        self.__applySuitAttackDamages(attack, self.battle.findSuit(attack[SUIT_ID_COL]))
                    attack[SUIT_BEFORE_TOONS_COL] = 0
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'headroller2calculator') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = 7  # Group Head Roller
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL] != NO_ATTACK:
                        if self.__suitAtkAffectsGroup(attack):
                            for currTgt in self.battle.activeToons:
                                self.__updateSuitAtkStat(currTgt)

                        else:
                            for currTgt in attack[SUIT_TGT_COL]:
                                self.__updateSuitAtkStat(self.battle.activeToons[currTgt])
                    targets = self.__createSuitTargetList(attack)
                    allTargetsDead = True
                    for currTgt in targets:
                        if self.__getToonHp(currTgt) > 0:
                            allTargetsDead = False
                            break

                    if allTargetsDead:
                        attack = getDefaultSuitAttack()
                    if self.__attackHasHit(attack, suit=1):
                        self.__applySuitAttackDamages(attack, self.battle.findSuit(attack[SUIT_ID_COL]))
                    attack[SUIT_BEFORE_TOONS_COL] = 0
                    self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'fbd':
                if self.suitHasCondition(suitId, 'explodingcalculator') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = 9  # Exploding Document
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL] != NO_ATTACK:
                        if self.__suitAtkAffectsGroup(attack):
                            for currTgt in self.battle.activeToons:
                                self.__updateSuitAtkStat(currTgt)

                        else:
                            for currTgt in attack[SUIT_TGT_COL]:
                                self.__updateSuitAtkStat(self.battle.activeToons[currTgt])
                    targets = self.__createSuitTargetList(attack)
                    allTargetsDead = True
                    for currTgt in targets:
                        if self.__getToonHp(currTgt) > 0:
                            allTargetsDead = False
                            break

                    if allTargetsDead:
                        attack = getDefaultSuitAttack()
                    if self.__attackHasHit(attack, suit=1):
                        self.__applySuitAttackDamages(attack, self.battle.findSuit(attack[SUIT_ID_COL]))
                    attack[SUIT_BEFORE_TOONS_COL] = 0
                    self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'frs':
                if self.suitHasCondition(suitId, 'collectcallcalculator') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = 6  # Collect Call
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL] != NO_ATTACK:
                        if self.__suitAtkAffectsGroup(attack):
                            for currTgt in self.battle.activeToons:
                                self.__updateSuitAtkStat(currTgt)

                        else:
                            for currTgt in attack[SUIT_TGT_COL]:
                                self.__updateSuitAtkStat(self.battle.activeToons[currTgt])
                    targets = self.__createSuitTargetList(attack)
                    allTargetsDead = True
                    for currTgt in targets:
                        if self.__getToonHp(currTgt) > 0:
                            allTargetsDead = False
                            break

                    if allTargetsDead:
                        attack = getDefaultSuitAttack()
                    if self.__attackHasHit(attack, suit=1):
                        self.__applySuitAttackDamages(attack, self.battle.findSuit(attack[SUIT_ID_COL]))
                    attack[SUIT_BEFORE_TOONS_COL] = 0
                    self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'cp': #powerhouse
                if self.TurnsElapsed % 1 == 0:
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = 16  # Snipe Retaliation Collect Call
                    attack[SUIT_TGT_COL] = []
                    for t in self.battle.activeToons:
                        if self.toonHasCondition(t, 'bound'):
                            attack[SUIT_TGT_COL].append(self.battle.activeToons.index(t))
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL] != NO_ATTACK:
                        if self.__suitAtkAffectsGroup(attack):
                            for currTgt in self.battle.activeToons:
                                self.__updateSuitAtkStat(currTgt)

                        else:
                            for currTgt in attack[SUIT_TGT_COL]:
                                self.__updateSuitAtkStat(self.battle.activeToons[currTgt])
                    targets = self.__createSuitTargetList(attack)
                    allTargetsDead = True
                    for currTgt in targets:
                        if self.__getToonHp(currTgt) > 0:
                            allTargetsDead = False
                            break

                    if allTargetsDead:
                        attack = getDefaultSuitAttack()
                    if self.__attackHasHit(attack, suit=1):
                        self.__applySuitAttackDamages(attack, self.battle.findSuit(attack[SUIT_ID_COL]))
                    attack[SUIT_BEFORE_TOONS_COL] = 0
                    self.battle.suitAttacks.append(attack)


        for i in xrange(len(self.battle.activeSuits)): # Secondary Cheats
            suitId = self.battle.activeSuits[i].doId
            x = self.TurnsElapsed
            if self.battle.activeSuits[i].dna.name == 'ste':
                if self.suitHasCondition(suitId, 'costscalculator') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = 7  # Court Costs
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL] != NO_ATTACK:
                        if self.__suitAtkAffectsGroup(attack):
                            for currTgt in self.battle.activeToons:
                                self.__updateSuitAtkStat(currTgt)

                        else:
                            for currTgt in attack[SUIT_TGT_COL]:
                                self.__updateSuitAtkStat(self.battle.activeToons[currTgt])
                    targets = self.__createSuitTargetList(attack)
                    allTargetsDead = True
                    for currTgt in targets:
                        if self.__getToonHp(currTgt) > 0:
                            allTargetsDead = False
                            break

                    if allTargetsDead:
                        attack = getDefaultSuitAttack()
                    if self.__attackHasHit(attack, suit=1):
                        self.__applySuitAttackDamages(attack, self.battle.findSuit(attack[SUIT_ID_COL]))
                    attack[SUIT_BEFORE_TOONS_COL] = 0
                    self.battle.suitAttacks.append(attack)
                if (self.getSuitConditionTurns(suitId, 'sanctioncalculator') == 9 and self.__suitCanAttack(suitId)) or (
                        self.getSuitConditionTurns(suitId, 'sanctioncalculator') == 8 and self.__suitCanAttack(suitId)):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = 8  # Court Sanction Regular
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL] != NO_ATTACK:
                        if self.__suitAtkAffectsGroup(attack):
                            for currTgt in self.battle.activeToons:
                                self.__updateSuitAtkStat(currTgt)

                        else:
                            for currTgt in attack[SUIT_TGT_COL]:
                                self.__updateSuitAtkStat(self.battle.activeToons[currTgt])
                    targets = self.__createSuitTargetList(attack)
                    allTargetsDead = True
                    for currTgt in targets:
                        if self.__getToonHp(currTgt) > 0:
                            allTargetsDead = False
                            break

                    if allTargetsDead:
                        attack = getDefaultSuitAttack()
                    if self.__attackHasHit(attack, suit=1):
                        self.__applySuitAttackDamages(attack, self.battle.findSuit(attack[SUIT_ID_COL]))
                    attack[SUIT_BEFORE_TOONS_COL] = 0
                    self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'csm':
                if (self.getSuitConditionTurns(suitId, 'bindingscalculator') == 9 and self.__suitCanAttack(suitId)) or (self.getSuitConditionTurns(suitId, 'bindingscalculator') == 8 and self.__suitCanAttack(suitId)):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = 6  # Legal Bindings
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL] != NO_ATTACK:
                        if self.__suitAtkAffectsGroup(attack):
                            for currTgt in self.battle.activeToons:
                                self.__updateSuitAtkStat(currTgt)

                        else:
                            for currTgt in attack[SUIT_TGT_COL]:
                                self.__updateSuitAtkStat(self.battle.activeToons[currTgt])
                    targets = self.__createSuitTargetList(attack)
                    allTargetsDead = True
                    for currTgt in targets:
                        if self.__getToonHp(currTgt) > 0:
                            allTargetsDead = False
                            break

                    if allTargetsDead:
                        attack = getDefaultSuitAttack()
                    if self.__attackHasHit(attack, suit=1):
                        self.__applySuitAttackDamages(attack, self.battle.findSuit(attack[SUIT_ID_COL]))
                    attack[SUIT_BEFORE_TOONS_COL] = 0
                    self.battle.suitAttacks.append(attack)
                if (self.getSuitConditionTurns(suitId, 'bindingscalculator2') == 9 and self.__suitCanAttack(suitId)) or (self.getSuitConditionTurns(suitId, 'bindingscalculator2') == 8 and self.__suitCanAttack(suitId)):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = 6  # Legal Bindings
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL] != NO_ATTACK:
                        if self.__suitAtkAffectsGroup(attack):
                            for currTgt in self.battle.activeToons:
                                self.__updateSuitAtkStat(currTgt)

                        else:
                            for currTgt in attack[SUIT_TGT_COL]:
                                self.__updateSuitAtkStat(self.battle.activeToons[currTgt])
                    targets = self.__createSuitTargetList(attack)
                    allTargetsDead = True
                    for currTgt in targets:
                        if self.__getToonHp(currTgt) > 0:
                            allTargetsDead = False
                            break

                    if allTargetsDead:
                        attack = getDefaultSuitAttack()
                    if self.__attackHasHit(attack, suit=1):
                        self.__applySuitAttackDamages(attack, self.battle.findSuit(attack[SUIT_ID_COL]))
                    attack[SUIT_BEFORE_TOONS_COL] = 0
                    self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'scg':
                if self.TurnsElapsed % 99 == 0 and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = 7  # First Turn Enraged
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL] != NO_ATTACK:
                        if self.__suitAtkAffectsGroup(attack):
                            for currTgt in self.battle.activeToons:
                                self.__updateSuitAtkStat(currTgt)

                        else:
                            for currTgt in attack[SUIT_TGT_COL]:
                                self.__updateSuitAtkStat(self.battle.activeToons[currTgt])
                    targets = self.__createSuitTargetList(attack)
                    allTargetsDead = True
                    for currTgt in targets:
                        if self.__getToonHp(currTgt) > 0:
                            allTargetsDead = False
                            break

                    if allTargetsDead:
                        attack = getDefaultSuitAttack()
                    if self.__attackHasHit(attack, suit=1):
                        self.__applySuitAttackDamages(attack, self.battle.findSuit(attack[SUIT_ID_COL]))
                    attack[SUIT_BEFORE_TOONS_COL] = 0
                    self.battle.suitAttacks.append(attack)
                if self.getSuitConditionTurns(suitId, 'enraged') == 1:
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = 6  # Shield's Up
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL] != NO_ATTACK:
                        if self.__suitAtkAffectsGroup(attack):
                            for currTgt in self.battle.activeToons:
                                self.__updateSuitAtkStat(currTgt)

                        else:
                            for currTgt in attack[SUIT_TGT_COL]:
                                self.__updateSuitAtkStat(self.battle.activeToons[currTgt])
                    targets = self.__createSuitTargetList(attack)
                    allTargetsDead = True
                    for currTgt in targets:
                        if self.__getToonHp(currTgt) > 0:
                            allTargetsDead = False
                            break

                    if allTargetsDead:
                        attack = getDefaultSuitAttack()
                    if self.__attackHasHit(attack, suit=1):
                        self.__applySuitAttackDamages(attack, self.battle.findSuit(attack[SUIT_ID_COL]))
                    attack[SUIT_BEFORE_TOONS_COL] = 0
                    self.battle.suitAttacks.append(attack)
                if self.getSuitConditionTurns(suitId, 'shielding') == 1:
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = 7  # Enraged
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL] != NO_ATTACK:
                        if self.__suitAtkAffectsGroup(attack):
                            for currTgt in self.battle.activeToons:
                                self.__updateSuitAtkStat(currTgt)

                        else:
                            for currTgt in attack[SUIT_TGT_COL]:
                                self.__updateSuitAtkStat(self.battle.activeToons[currTgt])
                    targets = self.__createSuitTargetList(attack)
                    allTargetsDead = True
                    for currTgt in targets:
                        if self.__getToonHp(currTgt) > 0:
                            allTargetsDead = False
                            break

                    if allTargetsDead:
                        attack = getDefaultSuitAttack()
                    if self.__attackHasHit(attack, suit=1):
                        self.__applySuitAttackDamages(attack, self.battle.findSuit(attack[SUIT_ID_COL]))
                    attack[SUIT_BEFORE_TOONS_COL] = 0
                    self.battle.suitAttacks.append(attack)
                if self.TurnsElapsed % 1 == 0:
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = 9  # Gavel Court Record Ban Retaliation
                    attack[SUIT_TGT_COL] = []
                    for t in self.battle.activeToons:
                        if self.toonHasCondition(t, 'banned3'):
                            attack[SUIT_TGT_COL].append(self.battle.activeToons.index(t))
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL] != NO_ATTACK:
                        if self.__suitAtkAffectsGroup(attack):
                            for currTgt in self.battle.activeToons:
                                self.__updateSuitAtkStat(currTgt)

                        else:
                            for currTgt in attack[SUIT_TGT_COL]:
                                self.__updateSuitAtkStat(self.battle.activeToons[currTgt])
                    targets = self.__createSuitTargetList(attack)
                    allTargetsDead = True
                    for currTgt in targets:
                        if self.__getToonHp(currTgt) > 0:
                            allTargetsDead = False
                            break

                    if allTargetsDead:
                        attack = getDefaultSuitAttack()
                    if self.__attackHasHit(attack, suit=1):
                        self.__applySuitAttackDamages(attack, self.battle.findSuit(attack[SUIT_ID_COL]))
                    attack[SUIT_BEFORE_TOONS_COL] = 0
                    self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'cp': #powerhouse
                if self.TurnsElapsed % 1 == 0:
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = 11  # Snipe Retaliation Vulnerabilities
                    attack[SUIT_TGT_COL] = []
                    for t in self.battle.activeToons:
                        if self.toonHasCondition(t, 'snapped'):
                            attack[SUIT_TGT_COL].append(self.battle.activeToons.index(t))
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL] != NO_ATTACK:
                        if self.__suitAtkAffectsGroup(attack):
                            for currTgt in self.battle.activeToons:
                                self.__updateSuitAtkStat(currTgt)

                        else:
                            for currTgt in attack[SUIT_TGT_COL]:
                                self.__updateSuitAtkStat(self.battle.activeToons[currTgt])
                    targets = self.__createSuitTargetList(attack)
                    allTargetsDead = True
                    for currTgt in targets:
                        if self.__getToonHp(currTgt) > 0:
                            allTargetsDead = False
                            break

                    if allTargetsDead:
                        attack = getDefaultSuitAttack()
                    if self.__attackHasHit(attack, suit=1):
                        self.__applySuitAttackDamages(attack, self.battle.findSuit(attack[SUIT_ID_COL]))
                    attack[SUIT_BEFORE_TOONS_COL] = 0
                    self.battle.suitAttacks.append(attack)
                if self.TurnsElapsed % 1 == 0:
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = 14  # Snipe Retaliation For Bookkeeping
                    attack[SUIT_TGT_COL] = []
                    for t in self.battle.activeToons:
                        if self.toonHasCondition(t, 'bookkeepingtoon'):
                            attack[SUIT_TGT_COL].append(self.battle.activeToons.index(t))
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL] != NO_ATTACK:
                        if self.__suitAtkAffectsGroup(attack):
                            for currTgt in self.battle.activeToons:
                                self.__updateSuitAtkStat(currTgt)

                        else:
                            for currTgt in attack[SUIT_TGT_COL]:
                                self.__updateSuitAtkStat(self.battle.activeToons[currTgt])
                    targets = self.__createSuitTargetList(attack)
                    allTargetsDead = True
                    for currTgt in targets:
                        if self.__getToonHp(currTgt) > 0:
                            allTargetsDead = False
                            break

                    if allTargetsDead:
                        attack = getDefaultSuitAttack()
                    if self.__attackHasHit(attack, suit=1):
                        self.__applySuitAttackDamages(attack, self.battle.findSuit(attack[SUIT_ID_COL]))
                    attack[SUIT_BEFORE_TOONS_COL] = 0
                    self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'fbd':  # bookkeeper
                if self.suitHasCondition(suitId, 'soakedcalculator') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = 6  # Soaked Paper Cut Retaliation
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL] != NO_ATTACK:
                        if self.__suitAtkAffectsGroup(attack):
                            for currTgt in self.battle.activeToons:
                                self.__updateSuitAtkStat(currTgt)

                        else:
                            for currTgt in attack[SUIT_TGT_COL]:
                                self.__updateSuitAtkStat(self.battle.activeToons[currTgt])
                    targets = self.__createSuitTargetList(attack)
                    allTargetsDead = True
                    for currTgt in targets:
                        if self.__getToonHp(currTgt) > 0:
                            allTargetsDead = False
                            break

                    if allTargetsDead:
                        attack = getDefaultSuitAttack()
                    if self.__attackHasHit(attack, suit=1):
                        self.__applySuitAttackDamages(attack, self.battle.findSuit(attack[SUIT_ID_COL]))
                    attack[SUIT_BEFORE_TOONS_COL] = 0
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'markedcalculator') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = 7  # Marked Paper Cut Retaliation
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL] != NO_ATTACK:
                        if self.__suitAtkAffectsGroup(attack):
                            for currTgt in self.battle.activeToons:
                                self.__updateSuitAtkStat(currTgt)

                        else:
                            for currTgt in attack[SUIT_TGT_COL]:
                                self.__updateSuitAtkStat(self.battle.activeToons[currTgt])
                    targets = self.__createSuitTargetList(attack)
                    allTargetsDead = True
                    for currTgt in targets:
                        if self.__getToonHp(currTgt) > 0:
                            allTargetsDead = False
                            break

                    if allTargetsDead:
                        attack = getDefaultSuitAttack()
                    if self.__attackHasHit(attack, suit=1):
                        self.__applySuitAttackDamages(attack, self.battle.findSuit(attack[SUIT_ID_COL]))
                    attack[SUIT_BEFORE_TOONS_COL] = 0
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'papercutcalculator') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = 8  # Paper Cut
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL] != NO_ATTACK:
                        if self.__suitAtkAffectsGroup(attack):
                            for currTgt in self.battle.activeToons:
                                self.__updateSuitAtkStat(currTgt)

                        else:
                            for currTgt in attack[SUIT_TGT_COL]:
                                self.__updateSuitAtkStat(self.battle.activeToons[currTgt])
                    targets = self.__createSuitTargetList(attack)
                    allTargetsDead = True
                    for currTgt in targets:
                        if self.__getToonHp(currTgt) > 0:
                            allTargetsDead = False
                            break

                    if allTargetsDead:
                        attack = getDefaultSuitAttack()
                    if self.__attackHasHit(attack, suit=1):
                        self.__applySuitAttackDamages(attack, self.battle.findSuit(attack[SUIT_ID_COL]))
                    attack[SUIT_BEFORE_TOONS_COL] = 0
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'bookkeepingcalculator'):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = 10  # Bookkeeping
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL] != NO_ATTACK:
                        if self.__suitAtkAffectsGroup(attack):
                            for currTgt in self.battle.activeToons:
                                self.__updateSuitAtkStat(currTgt)

                        else:
                            for currTgt in attack[SUIT_TGT_COL]:
                                self.__updateSuitAtkStat(self.battle.activeToons[currTgt])
                    targets = self.__createSuitTargetList(attack)
                    allTargetsDead = True
                    for currTgt in targets:
                        if self.__getToonHp(currTgt) > 0:
                            allTargetsDead = False
                            break

                    if allTargetsDead:
                        attack = getDefaultSuitAttack()
                    if self.__attackHasHit(attack, suit=1):
                        self.__applySuitAttackDamages(attack, self.battle.findSuit(attack[SUIT_ID_COL]))
                    attack[SUIT_BEFORE_TOONS_COL] = 0
                    self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'frs':  # wiretapper
                if self.suitHasCondition(suitId, 'brokenconnectioncalculator') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = 10  # Broken Connection
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL] != NO_ATTACK:
                        if self.__suitAtkAffectsGroup(attack):
                            for currTgt in self.battle.activeToons:
                                self.__updateSuitAtkStat(currTgt)

                        else:
                            for currTgt in attack[SUIT_TGT_COL]:
                                self.__updateSuitAtkStat(self.battle.activeToons[currTgt])
                    targets = self.__createSuitTargetList(attack)
                    allTargetsDead = True
                    for currTgt in targets:
                        if self.__getToonHp(currTgt) > 0:
                            allTargetsDead = False
                            break

                    if allTargetsDead:
                        attack = getDefaultSuitAttack()
                    if self.__attackHasHit(attack, suit=1):
                        self.__applySuitAttackDamages(attack, self.battle.findSuit(attack[SUIT_ID_COL]))
                    attack[SUIT_BEFORE_TOONS_COL] = 0
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'voicemailcalculator') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = 9  # Voicemail
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL] != NO_ATTACK:
                        if self.__suitAtkAffectsGroup(attack):
                            for currTgt in self.battle.activeToons:
                                self.__updateSuitAtkStat(currTgt)

                        else:
                            for currTgt in attack[SUIT_TGT_COL]:
                                self.__updateSuitAtkStat(self.battle.activeToons[currTgt])
                    targets = self.__createSuitTargetList(attack)
                    allTargetsDead = True
                    for currTgt in targets:
                        if self.__getToonHp(currTgt) > 0:
                            allTargetsDead = False
                            break

                    if allTargetsDead:
                        attack = getDefaultSuitAttack()
                    if self.__attackHasHit(attack, suit=1):
                        self.__applySuitAttackDamages(attack, self.battle.findSuit(attack[SUIT_ID_COL]))
                    attack[SUIT_BEFORE_TOONS_COL] = 0
                    self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'gtk': #ambassador
                if self.battle.activeSuits[i].currHP <= 1500 and not self.suitHasCondition(suitId, 'phase3') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = 9  # 'Phase 2'
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL] != NO_ATTACK:
                        if self.__suitAtkAffectsGroup(attack):
                            for currTgt in self.battle.activeToons:
                                self.__updateSuitAtkStat(currTgt)

                        else:
                            for currTgt in attack[SUIT_TGT_COL]:
                                self.__updateSuitAtkStat(self.battle.activeToons[currTgt])
                    targets = self.__createSuitTargetList(attack)
                    allTargetsDead = True
                    for currTgt in targets:
                        if self.__getToonHp(currTgt) > 0:
                            allTargetsDead = False
                            break

                    if allTargetsDead:
                        attack = getDefaultSuitAttack()
                    if self.__attackHasHit(attack, suit=1):
                        self.__applySuitAttackDamages(attack, self.battle.findSuit(attack[SUIT_ID_COL]))
                    attack[SUIT_BEFORE_TOONS_COL] = 0
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'bashcalculator') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = 11  # Managerial Protection
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL] != NO_ATTACK:
                        if self.__suitAtkAffectsGroup(attack):
                            for currTgt in self.battle.activeToons:
                                self.__updateSuitAtkStat(currTgt)

                        else:
                            for currTgt in attack[SUIT_TGT_COL]:
                                self.__updateSuitAtkStat(self.battle.activeToons[currTgt])
                    targets = self.__createSuitTargetList(attack)
                    allTargetsDead = True
                    for currTgt in targets:
                        if self.__getToonHp(currTgt) > 0:
                            allTargetsDead = False
                            break

                    if allTargetsDead:
                        attack = getDefaultSuitAttack()
                    if self.__attackHasHit(attack, suit=1):
                        self.__applySuitAttackDamages(attack, self.battle.findSuit(attack[SUIT_ID_COL]))
                    attack[SUIT_BEFORE_TOONS_COL] = 0
                    self.battle.suitAttacks.append(attack)
                if (self.suitHasCondition(suitId, 'damageupcalculator1') and self.__suitCanAttack(suitId)) or (self.suitHasCondition(suitId, 'damageupcalculator2') and self.__suitCanAttack(suitId)):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = 10  # Compensation
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL] != NO_ATTACK:
                        if self.__suitAtkAffectsGroup(attack):
                            for currTgt in self.battle.activeToons:
                                self.__updateSuitAtkStat(currTgt)

                        else:
                            for currTgt in attack[SUIT_TGT_COL]:
                                self.__updateSuitAtkStat(self.battle.activeToons[currTgt])
                    targets = self.__createSuitTargetList(attack)
                    allTargetsDead = True
                    for currTgt in targets:
                        if self.__getToonHp(currTgt) > 0:
                            allTargetsDead = False
                            break

                    if allTargetsDead:
                        attack = getDefaultSuitAttack()
                    if self.__attackHasHit(attack, suit=1):
                        self.__applySuitAttackDamages(attack, self.battle.findSuit(attack[SUIT_ID_COL]))
                    attack[SUIT_BEFORE_TOONS_COL] = 0
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'immunecalculator') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = 12  # Managerial Protection Immunity
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL] != NO_ATTACK:
                        if self.__suitAtkAffectsGroup(attack):
                            for currTgt in self.battle.activeToons:
                                self.__updateSuitAtkStat(currTgt)

                        else:
                            for currTgt in attack[SUIT_TGT_COL]:
                                self.__updateSuitAtkStat(self.battle.activeToons[currTgt])
                    targets = self.__createSuitTargetList(attack)
                    allTargetsDead = True
                    for currTgt in targets:
                        if self.__getToonHp(currTgt) > 0:
                            allTargetsDead = False
                            break

                    if allTargetsDead:
                        attack = getDefaultSuitAttack()
                    if self.__attackHasHit(attack, suit=1):
                        self.__applySuitAttackDamages(attack, self.battle.findSuit(attack[SUIT_ID_COL]))
                    attack[SUIT_BEFORE_TOONS_COL] = 0
                    self.battle.suitAttacks.append(attack)


        for i in xrange(len(self.battle.activeSuits)): # Final & Gag Banning Cheats
            suitId = self.battle.activeSuits[i].doId
            x = self.TurnsElapsed
            if self.battle.activeSuits[i].dna.name == 'lit':
                if self.suitHasCondition(suitId, 'bashcalculator') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = 6  # Bayou Bash
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL] != NO_ATTACK:
                        if self.__suitAtkAffectsGroup(attack):
                            for currTgt in self.battle.activeToons:
                                self.__updateSuitAtkStat(currTgt)

                        else:
                            for currTgt in attack[SUIT_TGT_COL]:
                                self.__updateSuitAtkStat(self.battle.activeToons[currTgt])
                    targets = self.__createSuitTargetList(attack)
                    allTargetsDead = True
                    for currTgt in targets:
                        if self.__getToonHp(currTgt) > 0:
                            allTargetsDead = False
                            break

                    if allTargetsDead:
                        attack = getDefaultSuitAttack()
                    if self.__attackHasHit(attack, suit=1):
                        self.__applySuitAttackDamages(attack, self.battle.findSuit(attack[SUIT_ID_COL]))
                    attack[SUIT_BEFORE_TOONS_COL] = 0
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'bellowcalculator') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = 5  # Bayou Bellow
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL] != NO_ATTACK:
                        if self.__suitAtkAffectsGroup(attack):
                            for currTgt in self.battle.activeToons:
                                self.__updateSuitAtkStat(currTgt)

                        else:
                            for currTgt in attack[SUIT_TGT_COL]:
                                self.__updateSuitAtkStat(self.battle.activeToons[currTgt])
                    targets = self.__createSuitTargetList(attack)
                    allTargetsDead = True
                    for currTgt in targets:
                        if self.__getToonHp(currTgt) > 0:
                            allTargetsDead = False
                            break

                    if allTargetsDead:
                        attack = getDefaultSuitAttack()
                    if self.__attackHasHit(attack, suit=1):
                        self.__applySuitAttackDamages(attack, self.battle.findSuit(attack[SUIT_ID_COL]))
                    attack[SUIT_BEFORE_TOONS_COL] = 0
                    self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'ste':
                if self.suitHasCondition(suitId, 'calculatingcalculator'):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = 6  # Calculating Costs
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL] != NO_ATTACK:
                        if self.__suitAtkAffectsGroup(attack):
                            for currTgt in self.battle.activeToons:
                                self.__updateSuitAtkStat(currTgt)

                        else:
                            for currTgt in attack[SUIT_TGT_COL]:
                                self.__updateSuitAtkStat(self.battle.activeToons[currTgt])
                    targets = self.__createSuitTargetList(attack)
                    allTargetsDead = True
                    for currTgt in targets:
                        if self.__getToonHp(currTgt) > 0:
                            allTargetsDead = False
                            break

                    if allTargetsDead:
                        attack = getDefaultSuitAttack()
                    if self.__attackHasHit(attack, suit=1):
                        self.__applySuitAttackDamages(attack, self.battle.findSuit(attack[SUIT_ID_COL]))
                    attack[SUIT_BEFORE_TOONS_COL] = 0
                    self.battle.suitAttacks.append(attack)
                if self.TurnsElapsed % 1 == 0 and self.suitHasCondition(suitId, 'ban2levels') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = random.randint(14, 23)  # Court Record Banning 2 Levels
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL] != NO_ATTACK:
                        if self.__suitAtkAffectsGroup(attack):
                            for currTgt in self.battle.activeToons:
                                self.__updateSuitAtkStat(currTgt)

                        else:
                            for currTgt in attack[SUIT_TGT_COL]:
                                self.__updateSuitAtkStat(self.battle.activeToons[currTgt])
                    targets = self.__createSuitTargetList(attack)
                    allTargetsDead = True
                    for currTgt in targets:
                        if self.__getToonHp(currTgt) > 0:
                            allTargetsDead = False
                            break

                    if allTargetsDead:
                        attack = getDefaultSuitAttack()
                    if self.__attackHasHit(attack, suit=1):
                        self.__applySuitAttackDamages(attack, self.battle.findSuit(attack[SUIT_ID_COL]))
                    attack[SUIT_BEFORE_TOONS_COL] = 0
                    self.battle.suitAttacks.append(attack)
                if self.TurnsElapsed % 1 == 0 and not self.suitHasCondition(suitId, 'ban2levels') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = random.randint(9, 13)  # Court Record Banning 1 Level
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL] != NO_ATTACK:
                        if self.__suitAtkAffectsGroup(attack):
                            for currTgt in self.battle.activeToons:
                                self.__updateSuitAtkStat(currTgt)

                        else:
                            for currTgt in attack[SUIT_TGT_COL]:
                                self.__updateSuitAtkStat(self.battle.activeToons[currTgt])
                    targets = self.__createSuitTargetList(attack)
                    allTargetsDead = True
                    for currTgt in targets:
                        if self.__getToonHp(currTgt) > 0:
                            allTargetsDead = False
                            break

                    if allTargetsDead:
                        attack = getDefaultSuitAttack()
                    if self.__attackHasHit(attack, suit=1):
                        self.__applySuitAttackDamages(attack, self.battle.findSuit(attack[SUIT_ID_COL]))
                    attack[SUIT_BEFORE_TOONS_COL] = 0
                    self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'csm':
                if self.TurnsElapsed % 1 == 0 and self.suitHasCondition(suitId, 'ban2tracks') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = random.randint(15, 42)  # Court Record Ban 2 Tracks
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL] != NO_ATTACK:
                        if self.__suitAtkAffectsGroup(attack):
                            for currTgt in self.battle.activeToons:
                                self.__updateSuitAtkStat(currTgt)

                        else:
                            for currTgt in attack[SUIT_TGT_COL]:
                                self.__updateSuitAtkStat(self.battle.activeToons[currTgt])
                    targets = self.__createSuitTargetList(attack)
                    allTargetsDead = True
                    for currTgt in targets:
                        if self.__getToonHp(currTgt) > 0:
                            allTargetsDead = False
                            break

                    if allTargetsDead:
                        attack = getDefaultSuitAttack()
                    if self.__attackHasHit(attack, suit=1):
                        self.__applySuitAttackDamages(attack, self.battle.findSuit(attack[SUIT_ID_COL]))
                    attack[SUIT_BEFORE_TOONS_COL] = 0
                    self.battle.suitAttacks.append(attack)
                if self.TurnsElapsed % 1 == 0 and not self.suitHasCondition(suitId, 'ban2tracks') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = random.randint(7, 14)  # Court Record Ban 1 Track
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL] != NO_ATTACK:
                        if self.__suitAtkAffectsGroup(attack):
                            for currTgt in self.battle.activeToons:
                                self.__updateSuitAtkStat(currTgt)

                        else:
                            for currTgt in attack[SUIT_TGT_COL]:
                                self.__updateSuitAtkStat(self.battle.activeToons[currTgt])
                    targets = self.__createSuitTargetList(attack)
                    allTargetsDead = True
                    for currTgt in targets:
                        if self.__getToonHp(currTgt) > 0:
                            allTargetsDead = False
                            break

                    if allTargetsDead:
                        attack = getDefaultSuitAttack()
                    if self.__attackHasHit(attack, suit=1):
                        self.__applySuitAttackDamages(attack, self.battle.findSuit(attack[SUIT_ID_COL]))
                    attack[SUIT_BEFORE_TOONS_COL] = 0
                    self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'gtk':
                if self.suitHasCondition(suitId, 'mulligancalculator'):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = 13  # Mulligan
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL] != NO_ATTACK:
                        if self.__suitAtkAffectsGroup(attack):
                            for currTgt in self.battle.activeToons:
                                self.__updateSuitAtkStat(currTgt)

                        else:
                            for currTgt in attack[SUIT_TGT_COL]:
                                self.__updateSuitAtkStat(self.battle.activeToons[currTgt])
                    targets = self.__createSuitTargetList(attack)
                    allTargetsDead = True
                    for currTgt in targets:
                        if self.__getToonHp(currTgt) > 0:
                            allTargetsDead = False
                            break

                    if allTargetsDead:
                        attack = getDefaultSuitAttack()
                    if self.__attackHasHit(attack, suit=1):
                        self.__applySuitAttackDamages(attack, self.battle.findSuit(attack[SUIT_ID_COL]))
                    attack[SUIT_BEFORE_TOONS_COL] = 0
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'mulligancalculator2'):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = 13  # Mulligan #2
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL] != NO_ATTACK:
                        if self.__suitAtkAffectsGroup(attack):
                            for currTgt in self.battle.activeToons:
                                self.__updateSuitAtkStat(currTgt)

                        else:
                            for currTgt in attack[SUIT_TGT_COL]:
                                self.__updateSuitAtkStat(self.battle.activeToons[currTgt])
                    targets = self.__createSuitTargetList(attack)
                    allTargetsDead = True
                    for currTgt in targets:
                        if self.__getToonHp(currTgt) > 0:
                            allTargetsDead = False
                            break

                    if allTargetsDead:
                        attack = getDefaultSuitAttack()
                    if self.__attackHasHit(attack, suit=1):
                        self.__applySuitAttackDamages(attack, self.battle.findSuit(attack[SUIT_ID_COL]))
                    attack[SUIT_BEFORE_TOONS_COL] = 0
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'mulligancalculator3'):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = 13  # Mulligan #3
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL] != NO_ATTACK:
                        if self.__suitAtkAffectsGroup(attack):
                            for currTgt in self.battle.activeToons:
                                self.__updateSuitAtkStat(currTgt)

                        else:
                            for currTgt in attack[SUIT_TGT_COL]:
                                self.__updateSuitAtkStat(self.battle.activeToons[currTgt])
                    targets = self.__createSuitTargetList(attack)
                    allTargetsDead = True
                    for currTgt in targets:
                        if self.__getToonHp(currTgt) > 0:
                            allTargetsDead = False
                            break

                    if allTargetsDead:
                        attack = getDefaultSuitAttack()
                    if self.__attackHasHit(attack, suit=1):
                        self.__applySuitAttackDamages(attack, self.battle.findSuit(attack[SUIT_ID_COL]))
                    attack[SUIT_BEFORE_TOONS_COL] = 0
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'mulligancalculator4'):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = 13  # Mulligan #4
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL] != NO_ATTACK:
                        if self.__suitAtkAffectsGroup(attack):
                            for currTgt in self.battle.activeToons:
                                self.__updateSuitAtkStat(currTgt)

                        else:
                            for currTgt in attack[SUIT_TGT_COL]:
                                self.__updateSuitAtkStat(self.battle.activeToons[currTgt])
                    targets = self.__createSuitTargetList(attack)
                    allTargetsDead = True
                    for currTgt in targets:
                        if self.__getToonHp(currTgt) > 0:
                            allTargetsDead = False
                            break

                    if allTargetsDead:
                        attack = getDefaultSuitAttack()
                    if self.__attackHasHit(attack, suit=1):
                        self.__applySuitAttackDamages(attack, self.battle.findSuit(attack[SUIT_ID_COL]))
                    attack[SUIT_BEFORE_TOONS_COL] = 0
                    self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'cp': #powerhouse
                if self.suitHasCondition(suitId, 'desperation') and not self.suitHasCondition(suitId, 'syphoncalculator') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = 10  # Desperation Syphon For All Cogs
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL] != NO_ATTACK:
                        if self.__suitAtkAffectsGroup(attack):
                            for currTgt in self.battle.activeToons:
                                self.__updateSuitAtkStat(currTgt)

                        else:
                            for currTgt in attack[SUIT_TGT_COL]:
                                self.__updateSuitAtkStat(self.battle.activeToons[currTgt])
                    targets = self.__createSuitTargetList(attack)
                    allTargetsDead = True
                    for currTgt in targets:
                        if self.__getToonHp(currTgt) > 0:
                            allTargetsDead = False
                            break

                    if allTargetsDead:
                        attack = getDefaultSuitAttack()
                    if self.__attackHasHit(attack, suit=1):
                        self.__applySuitAttackDamages(attack, self.battle.findSuit(attack[SUIT_ID_COL]))
                    attack[SUIT_BEFORE_TOONS_COL] = 0
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'rotationcalculator') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = random.randint(6,9)  # Rotation Of Conditions
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL] != NO_ATTACK:
                        if self.__suitAtkAffectsGroup(attack):
                            for currTgt in self.battle.activeToons:
                                self.__updateSuitAtkStat(currTgt)

                        else:
                            for currTgt in attack[SUIT_TGT_COL]:
                                self.__updateSuitAtkStat(self.battle.activeToons[currTgt])
                    targets = self.__createSuitTargetList(attack)
                    allTargetsDead = True
                    for currTgt in targets:
                        if self.__getToonHp(currTgt) > 0:
                            allTargetsDead = False
                            break

                    if allTargetsDead:
                        attack = getDefaultSuitAttack()
                    if self.__attackHasHit(attack, suit=1):
                        self.__applySuitAttackDamages(attack, self.battle.findSuit(attack[SUIT_ID_COL]))
                    attack[SUIT_BEFORE_TOONS_COL] = 0
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'soakedcalculator') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = 13  # Soak Retaliation Snipe
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL] != NO_ATTACK:
                        if self.__suitAtkAffectsGroup(attack):
                            for currTgt in self.battle.activeToons:
                                self.__updateSuitAtkStat(currTgt)

                        else:
                            for currTgt in attack[SUIT_TGT_COL]:
                                self.__updateSuitAtkStat(self.battle.activeToons[currTgt])
                    targets = self.__createSuitTargetList(attack)
                    allTargetsDead = True
                    for currTgt in targets:
                        if self.__getToonHp(currTgt) > 0:
                            allTargetsDead = False
                            break

                    if allTargetsDead:
                        attack = getDefaultSuitAttack()
                    if self.__attackHasHit(attack, suit=1):
                        self.__applySuitAttackDamages(attack, self.battle.findSuit(attack[SUIT_ID_COL]))
                    attack[SUIT_BEFORE_TOONS_COL] = 0
                    self.battle.suitAttacks.append(attack)
                if self.TurnsElapsed % 1 == 0:
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = 15  # Snipe Retaliation For Being On Cooldown
                    attack[SUIT_TGT_COL] = []
                    for t in self.battle.activeToons:
                        if self.toonHasCondition(t, 'noUnites'):
                            attack[SUIT_TGT_COL].append(self.battle.activeToons.index(t))
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL] != NO_ATTACK:
                        if self.__suitAtkAffectsGroup(attack):
                            for currTgt in self.battle.activeToons:
                                self.__updateSuitAtkStat(currTgt)

                        else:
                            for currTgt in attack[SUIT_TGT_COL]:
                                self.__updateSuitAtkStat(self.battle.activeToons[currTgt])
                    targets = self.__createSuitTargetList(attack)
                    allTargetsDead = True
                    for currTgt in targets:
                        if self.__getToonHp(currTgt) > 0:
                            allTargetsDead = False
                            break

                    if allTargetsDead:
                        attack = getDefaultSuitAttack()
                    if self.__attackHasHit(attack, suit=1):
                        self.__applySuitAttackDamages(attack, self.battle.findSuit(attack[SUIT_ID_COL]))
                    attack[SUIT_BEFORE_TOONS_COL] = 0
                    self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'frs':
                if self.suitHasCondition(suitId, 'wiretappedcalculator') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = 8  # Wiretapped
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL] != NO_ATTACK:
                        if self.__suitAtkAffectsGroup(attack):
                            for currTgt in self.battle.activeToons:
                                self.__updateSuitAtkStat(currTgt)

                        else:
                            for currTgt in attack[SUIT_TGT_COL]:
                                self.__updateSuitAtkStat(self.battle.activeToons[currTgt])
                    targets = self.__createSuitTargetList(attack)
                    allTargetsDead = True
                    for currTgt in targets:
                        if self.__getToonHp(currTgt) > 0:
                            allTargetsDead = False
                            break

                    if allTargetsDead:
                        attack = getDefaultSuitAttack()
                    if self.__attackHasHit(attack, suit=1):
                        self.__applySuitAttackDamages(attack, self.battle.findSuit(attack[SUIT_ID_COL]))
                    attack[SUIT_BEFORE_TOONS_COL] = 0
                    self.battle.suitAttacks.append(attack)
                if self.TurnsElapsed % 1 == 0 and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = random.randint(19,23)  # Budget Cuts Level Ban
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL] != NO_ATTACK:
                        if self.__suitAtkAffectsGroup(attack):
                            for currTgt in self.battle.activeToons:
                                self.__updateSuitAtkStat(currTgt)

                        else:
                            for currTgt in attack[SUIT_TGT_COL]:
                                self.__updateSuitAtkStat(self.battle.activeToons[currTgt])
                    targets = self.__createSuitTargetList(attack)
                    allTargetsDead = True
                    for currTgt in targets:
                        if self.__getToonHp(currTgt) > 0:
                            allTargetsDead = False
                            break

                    if allTargetsDead:
                        attack = getDefaultSuitAttack()
                    if self.__attackHasHit(attack, suit=1):
                        self.__applySuitAttackDamages(attack, self.battle.findSuit(attack[SUIT_ID_COL]))
                    attack[SUIT_BEFORE_TOONS_COL] = 0
                    self.battle.suitAttacks.append(attack)
                if self.TurnsElapsed % 1 == 0 and self.__suitCanAttack(suitId) and self.suitHasCondition(suitId, 'bantracks'):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = random.randint(11,18)  # Budget Cuts Track Ban
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL] != NO_ATTACK:
                        if self.__suitAtkAffectsGroup(attack):
                            for currTgt in self.battle.activeToons:
                                self.__updateSuitAtkStat(currTgt)

                        else:
                            for currTgt in attack[SUIT_TGT_COL]:
                                self.__updateSuitAtkStat(self.battle.activeToons[currTgt])
                    targets = self.__createSuitTargetList(attack)
                    allTargetsDead = True
                    for currTgt in targets:
                        if self.__getToonHp(currTgt) > 0:
                            allTargetsDead = False
                            break

                    if allTargetsDead:
                        attack = getDefaultSuitAttack()
                    if self.__attackHasHit(attack, suit=1):
                        self.__applySuitAttackDamages(attack, self.battle.findSuit(attack[SUIT_ID_COL]))
                    attack[SUIT_BEFORE_TOONS_COL] = 0
                    self.battle.suitAttacks.append(attack)


        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            x = self.TurnsElapsed
            if self.suitHasCondition(suitId, 'bellowattack') and not self.battle.activeSuits[i].dna.name == 'lit':
                attack = getDefaultSuitAttack()
                attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                attack[SUIT_ATK_COL] = 0  # Random Extra Attack From Bayou Bellow
                attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                if attack[SUIT_TGT_COL] == []:
                    continue
                attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                self.__calcSuitAtkHpALT(attack)
                if attack[SUIT_ATK_COL] != NO_ATTACK:
                    if self.__suitAtkAffectsGroup(attack):
                        for currTgt in self.battle.activeToons:
                            self.__updateSuitAtkStat(currTgt)

                    else:
                        for currTgt in attack[SUIT_TGT_COL]:
                            self.__updateSuitAtkStat(self.battle.activeToons[currTgt])
                targets = self.__createSuitTargetList(attack)
                allTargetsDead = True
                for currTgt in targets:
                    if self.__getToonHp(currTgt) > 0:
                        allTargetsDead = False
                        break

                if allTargetsDead:
                    attack = getDefaultSuitAttack()
                if self.__attackHasHit(attack, suit=1):
                    self.__applySuitAttackDamages(attack, self.battle.findSuit(attack[SUIT_ID_COL]))
                attack[SUIT_BEFORE_TOONS_COL] = 0
                self.battle.suitAttacks.append(attack)



    def __updateLureTimeouts(self):
        noLongerLured = []
        for currLuredSuit in self.currentlyLuredSuits.keys():
            self.__incLuredCurrRound(currLuredSuit)
            if self.__luredMaxRoundsReached(currLuredSuit) or self.__luredWakeupTime(currLuredSuit):
                noLongerLured.append(currLuredSuit)


        for currLuredSuit in noLongerLured:
            self.__removeLured(currLuredSuit)

    def __updateWetTimeouts(self):
        noLongerWet = []
        for currentlyWetSuit in self.currentlyWetSuits.keys():
            self.__incWetCurrRound(currentlyWetSuit)
            if self.__wetMaxRoundsReached(currentlyWetSuit):
                noLongerWet.append(currentlyWetSuit)

        for currentlyWetSuit in noLongerWet:
            self.__removeWet(currentlyWetSuit)

    def __updateEnragedTimeouts(self):
        noLongerEnraged = []
        for currentlyEnragedSuit in self.currentlyEnragedSuits.keys():
            self.__incEnragedCurrRound(currentlyEnragedSuit)
            if self.__enragedMaxRoundsReached(currentlyEnragedSuit):
                noLongerEnraged.append(currentlyEnragedSuit)

        for currentlyEnragedSuit in noLongerEnraged:
            self.__removeEnraged(currentlyEnragedSuit)

    def __updateAbsorbingTimeouts(self):
        noLongerAbsorbing = []
        for currentlyAbsorbingSuit in self.currentlyAbsorbingSuits.keys():
            self.__incAbsorbingCurrRound(currentlyAbsorbingSuit)
            if self.__absorbingMaxRoundsReached(currentlyAbsorbingSuit):
                noLongerAbsorbing.append(currentlyAbsorbingSuit)

        for currentlyAbsorbingSuit in noLongerAbsorbing:
            self.__removeAbsorbing(currentlyAbsorbingSuit)

    def __initRound(self):
        if CLEAR_SUIT_ATTACKERS:
            self.SuitAttackers = {}
        self.toonAtkOrder = []
        attacks = findToonAttack(self.battle.activeToons, self.battle.toonAttacks, PETSOS)
        for atk in attacks:
            self.toonAtkOrder.append(atk[TOON_ID_COL])

        attacks = findToonAttack(self.battle.activeToons, self.battle.toonAttacks, FIRE)
        for atk in attacks:
            self.toonAtkOrder.append(atk[TOON_ID_COL])

        for track in xrange(HEAL, DROP + 1):
            attacks = findToonAttack(self.battle.activeToons, self.battle.toonAttacks, track)
            if track == TRAP:
                sortedTraps = []
                for atk in attacks:
                    if atk[TOON_TRACK_COL] == TRAP:
                        sortedTraps.append(atk)

                for atk in attacks:
                    if atk[TOON_TRACK_COL] == NPCSOS:
                        sortedTraps.append(atk)

                attacks = sortedTraps
            for atk in attacks:
                self.toonAtkOrder.append(atk[TOON_ID_COL])

        specials = findToonAttack(self.battle.activeToons, self.battle.toonAttacks, NPCSOS)
        toonsHit = 0
        cogsMiss = 0
        for special in specials:
            npc_track, npc_level, npc_hp, npc_rarity = NPCToons.getNPCTrackLevelHpRarity(special[TOON_TGT_COL])
            if npc_track == NPC_TOONS_HIT:
                if self.roundsToonsHit < rounds:
                    self.roundsToonsHit = rounds
                    self.toonsAlwaysHit = 1
                    toonsHit = 1
                else:
                    self.toonsAlwaysHit = 1
                    toonsHit = 1
            elif npc_track == NPC_COGS_MISS:
                if self.roundsCogsMiss < rounds:
                    self.roundsCogsMiss = rounds
                    self.suitsAlwaysMiss = 1
                    cogsMiss = 1
                else:
                    self.suitsAlwaysMiss = 1
                    cogsMiss = 1
            elif npc_track == NPC_DAMAGE_BOOST:
                lvToDict = (
                'healBoost', 'trapBoost', 'lureBoost', 'throwBoost', 'squirtBoost', 'zapBoost',  'soundBoost', 'dropBoost',
                'allGagBoost')
                for t in self.battle.activeToons:
                    toon = self.battle.getToon(t)
                    if toon != None:
                        self.setToonCondition(toon.doId, lvToDict[npc_level], npc_hp, 3, 'setBoth')
                        self.setToonCondition(toon.doId, 'noSOS', 1, 2, 'setBoth')
                        self.setToonCondition(toon.doId, 'noFires', 1, 2, 'setBoth')
                        self.setToonCondition(toon.doId, 'noUnites', 1, 2, 'setBoth')
                        # use alternate both because we want a better SOS card to replace a worse one
        if self.roundsToonsHit > 0:
           toonsHit =1
        if self.roundsCogsMiss > 0:
           cogsMiss =1

        self.toonHPAdjusts = {}
        for t in self.battle.activeToons:
            self.toonHPAdjusts[t] = 0

        self.__clearBonuses()
        self.__updateActiveToons()
        self.delayedUnlures = []
        self.__initTraps()
        self.successfulLures = {}
        return (toonsHit, cogsMiss)

    def calculateRound(self):
        longest = max(len(self.battle.activeToons), len(self.battle.activeSuits))
        for t in self.battle.activeToons:
            for j in xrange(longest):
                self.battle.toonAttacks[t][TOON_HP_COL].append(-1)
                self.battle.toonAttacks[t][TOON_KBBONUS_COL].append(-1)

        toonsHit, cogsMiss = self.__initRound()
        for suit in self.battle.activeSuits:
            if suit.isGenerated():
                suit.b_setHP(suit.getHP())

        for suit in self.battle.activeSuits:
            if not hasattr(suit, 'dna'):
                self.notify.warning('a removed suit is in this battle!')
                return None

        self.__calculateToonAttacks()
        self.__updateLureTimeouts()
        self.__updateWetTimeouts()
        self.__updateAbsorbingTimeouts()
        self.__updateEnragedTimeouts()
        self.__calculateSuitAttacks()
        if self.roundsToonsHit > 0:
            self.roundsToonsHit -= 1
        if self.roundsCogsMiss > 0:
            self.roundsCogsMiss -= 1
        if toonsHit == 1 and self.roundsToonsHit <= 0:
            self.toonsAlwaysHit = 0
        if cogsMiss == 1 and self.roundsCogsMiss <= 0:
            self.suitsAlwaysMiss = 0
            self.__printSuitAtkStats()
            if self.toonStatusConditions:
                self.printToonConditions()


    def __calculateFiredCogs():
        import pdb
        pdb.set_trace()

    def toonLeftBattle(self, toonId):
        if toonId in self.toonSkillPtsGained:
            del self.toonSkillPtsGained[toonId]
        if toonId in self.suitAtkStats:
            del self.suitAtkStats[toonId]
        if not CLEAR_SUIT_ATTACKERS:
            oldSuitIds = []
            for s in self.SuitAttackers.keys():
                if toonId in self.SuitAttackers[s]:
                    del self.SuitAttackers[s][toonId]
                    if len(self.SuitAttackers[s]) == 0:
                        oldSuitIds.append(s)

            for oldSuitId in oldSuitIds:
                del self.SuitAttackers[oldSuitId]

        self.__clearTrapCreator(toonId)
        self.__clearLurer(toonId)

    def suitLeftBattle(self, suitId):
        self.__removeLured(suitId)
        if suitId in self.SuitAttackers:
            del self.SuitAttackers[suitId]
        self.__removeSuitTrap(suitId)

    def __updateActiveToons(self):
        if not CLEAR_SUIT_ATTACKERS:
            oldSuitIds = []
            for s in self.SuitAttackers.keys():
                for t in self.SuitAttackers[s].keys():
                    if t not in self.battle.activeToons:
                        del self.SuitAttackers[s][t]
                        if len(self.SuitAttackers[s]) == 0:
                            oldSuitIds.append(s)

            for oldSuitId in oldSuitIds:
                del self.SuitAttackers[oldSuitId]

        for trap in self.traps.keys():
            if self.traps[trap][1] not in self.battle.activeToons:
                self.traps[trap][1] = 0

    def getSkillGained(self, toonId, track):
        return BattleExperienceAI.getSkillGained(self.toonSkillPtsGained, toonId, track)

    def getLuredSuits(self):
        self.TurnsElapsed += 1
        self.notify.debug('Current Elapsed Turns: ' + str(self.TurnsElapsed))
        luredSuits = self.currentlyLuredSuits.keys()
        #self.notify.debug('Lured suits reported to battle: ' + repr(luredSuits))
        return luredSuits

    def __suitIsLured(self, suitId, prevRound = 0):
        inList = suitId in self.currentlyLuredSuits
        if prevRound:
            return inList and self.currentlyLuredSuits[suitId][0] != -1
        return inList

    def getImmuneSuits(self):
        gottenImmuneSuits = []
        for suit in self.battle.activeSuits:
            if suit.getImmuneStatus() == 1:
                gottenImmuneSuits.append(suit.doId)
        #self.notify.debug('Immune suits reported to battle: ' + repr(gottenImmuneSuits))
        return gottenImmuneSuits

    def getEnragedSuits(self):
        gottenEnragedSuits = []
        for suit in self.battle.activeSuits:
            if suit.getEnragedStatus() == 1:
                gottenEnragedSuits.append(suit.doId)
        #self.notify.debug('Enraged suits reported to battle: ' + repr(gottenEnragedSuits))
        return gottenEnragedSuits

    def getAbsorbingSuits(self):
        gottenAbsorbingSuits = []
        for suit in self.battle.activeSuits:
            if suit.getAbsorbingStatus() == 1:
                gottenAbsorbingSuits.append(suit.doId)
        #self.notify.debug('Absorbing suits reported to battle: ' + repr(gottenAbsorbingSuits))
        return gottenAbsorbingSuits

    def getSoakedSuits(self):
        gottenSoakedSuits = []
        for suit in self.battle.activeSuits:
            if suit.getSoakedStatus() == 1:
                gottenSoakedSuits.append(suit.doId)
        #self.notify.debug('Soaked suits reported to battle: ' + repr(gottenSoakedSuits))
        return gottenSoakedSuits

    def __suitIsImmune(self, suitId, prevRound=0):
        inList = suitId in self.currentlyImmuneSuits
        if prevRound:
            return inList and self.currentlyImmuneSuits[suitId][0] != -1
        return inList

    def __suitIsEnraged(self, suitId, prevRound=0):
        inList = suitId in self.currentlyEnragedSuits
        if prevRound:
            return inList and self.currentlyEnragedSuits[suitId][0] != -1
        return inList

    def __suitIsAbsorbing(self, suitId, prevRound=0):
        inList = suitId in self.currentlyAbsorbingSuits
        if prevRound:
            return inList and self.currentlyAbsorbingSuits[suitId][0] != -1
        return inList

    def __suitIsSoaked(self, suitId, prevRound=0):
        inList = suitId in self.currentlySoakedSuits
        if prevRound:
            return inList and self.currentlySoakedSuits[suitId][0] != -1
        return inList

    def __suitIsWet(self, suitId, prevRound = 0):
        inList = suitId in self.currentlyWetSuits
        return inList

    def __findAvailLureId(self, lurerId):
        luredSuits = self.currentlyLuredSuits.keys()
        lureIds = []
        for currLured in luredSuits:
            lurerInfo = self.currentlyLuredSuits[currLured][3]
            lurers = lurerInfo.keys()
            for currLurer in lurers:
                currId = lurerInfo[currLurer][1]
                if currLurer == lurerId and currId not in lureIds:
                    lureIds.append(currId)

        lureIds.sort()
        currId = 1
        for currLureId in lureIds:
            if currLureId != currId:
                return currId
            currId += 1

        return currId

    def __addLuredSuitInfo(self, suitId, currRounds, maxRounds, wakeChance, lurer, lureLvl, lureId = -1, npc = 0):
        if lureId == -1:
            availLureId = self.__findAvailLureId(lurer)
        else:
            availLureId = lureId
        if npc == 1:
            credit = 0
        else:
            credit = self.itemIsCredit(LURE, lureLvl)
        if suitId in self.currentlyLuredSuits:
            lureInfo = self.currentlyLuredSuits[suitId]
            if not lurer in lureInfo[3]:
                lureInfo[1] += maxRounds
                if wakeChance < lureInfo[2]:
                    lureInfo[2] = wakeChance
                lureInfo[3][lurer] = [lureLvl, availLureId, credit]
        else:
            lurerInfo = {lurer: [lureLvl, availLureId, credit]}
            self.currentlyLuredSuits[suitId] = [currRounds,
             maxRounds,
             wakeChance,
             lurerInfo]
        #self.notify.debug('__addLuredSuitInfo: currLuredSuits -> %s' % repr(self.currentlyLuredSuits))
        return availLureId

    def __getLurers(self, suitId):
        if self.__suitIsLured(suitId):
            return self.currentlyLuredSuits[suitId][3].keys()
        return []

    def __getLuredExpInfo(self, suitId):
        returnInfo = []
        lurers = self.__getLurers(suitId)
        if len(lurers) == 0:
            return returnInfo
        lurerInfo = self.currentlyLuredSuits[suitId][3]
        for currLurer in lurers:
            returnInfo.append([currLurer,
             lurerInfo[currLurer][0],
             lurerInfo[currLurer][1],
             lurerInfo[currLurer][2]])

        return returnInfo

    def __clearLurer(self, lurerId, lureId = -1):
        luredSuits = self.currentlyLuredSuits.keys()
        for currLured in luredSuits:
            lurerInfo = self.currentlyLuredSuits[currLured][3]
            lurers = lurerInfo.keys()
            for currLurer in lurers:
                if currLurer == lurerId and (lureId == -1 or lureId == lurerInfo[currLurer][1]):
                    del lurerInfo[currLurer]

    def __setLuredMaxRounds(self, suitId, rounds):
        if self.__suitIsLured(suitId):
            self.currentlyLuredSuits[suitId][1] = rounds

    def __setLuredWakeChance(self, suitId, chance):
        if self.__suitIsLured(suitId):
            self.currentlyLuredSuits[suitId][2] = chance

    def __incLuredCurrRound(self, suitId):
        theSuit = self.battle.findSuit(suitId)
        x = self.TurnsElapsed
        if x % 99 == 0 and theSuit.dna.name == 'scg':
            self.currentlyLuredSuits[suitId][0] = self.currentlyLuredSuits[suitId][1] - 1
        if theSuit.dna.name == 'mad' and theSuit.currHP > 0 and not theSuit.maxHP > 5000:
            self.currentlyLuredSuits[suitId][0] = self.currentlyLuredSuits[suitId][1] - 1
        if theSuit.dna.name == 'crf':
            self.currentlyLuredSuits[suitId][0] = self.currentlyLuredSuits[suitId][1] - 1
        if theSuit.dna.name == 'dsf':
            self.currentlyLuredSuits[suitId][0] = self.currentlyLuredSuits[suitId][1] - 1
        if x % 3 == 0 and theSuit.dna.name == 'ghd':
            self.currentlyLuredSuits[suitId][0] = self.currentlyLuredSuits[suitId][1] - 1
        if x % 5 == 0 and theSuit.dna.name == 'ghd':
            self.currentlyLuredSuits[suitId][0] = self.currentlyLuredSuits[suitId][1] - 1
        if theSuit.isSkeleton and self.battle.findSuit(suitId).getManager() and self.currentlyLuredSuits[suitId][0] < 1:
            self.currentlyLuredSuits[suitId][0] = self.currentlyLuredSuits[suitId][1] - 1
        if self.suitHasCondition(suitId, 'enraged') and self.currentlyLuredSuits[suitId][0] < 1:
            self.currentlyLuredSuits[suitId][0] = self.currentlyLuredSuits[suitId][1] - 1
        if self.suitHasCondition(suitId, 'bookkeeping') and self.currentlyLuredSuits[suitId][0] < 1:
            self.currentlyLuredSuits[suitId][0] = self.currentlyLuredSuits[suitId][1] - 1
        if self.suitHasCondition(suitId, 'desperation') and self.currentlyLuredSuits[suitId][0] < 1:
            self.currentlyLuredSuits[suitId][0] = self.currentlyLuredSuits[suitId][1] - 1
        if self.battle.findSuit(suitId).getManager() and self.currentlyLuredSuits[suitId][0] < 1:
            self.currentlyLuredSuits[suitId][0] = self.currentlyLuredSuits[suitId][1] - 2
        if self.suitHasCondition(suitId, 'immune'):
            self.currentlyLuredSuits[suitId][0] = self.currentlyLuredSuits[suitId][1] - 1
        if self.suitHasCondition(suitId, 'lureImmune'):
            self.currentlyLuredSuits[suitId][0] = self.currentlyLuredSuits[suitId][1] - 1
        if self.suitHasCondition(suitId, 'insured') and not self.suitHasCondition(suitId, 'desperation') and self.currentlyLuredSuits[suitId][0] < 1:
            self.currentlyLuredSuits[suitId][0] = self.currentlyLuredSuits[suitId][1] - 2
        if theSuit.isSkeleton and theSuit.getHP() > (theSuit.getMaxHP() * 1.5) and self.currentlyLuredSuits[suitId][0] < 1:
            self.currentlyLuredSuits[suitId][0] = self.currentlyLuredSuits[suitId][1] - 1
        if theSuit.getHP() > (theSuit.getMaxHP() * 1.5) and self.currentlyLuredSuits[suitId][0] < 1:
            self.currentlyLuredSuits[suitId][0] = self.currentlyLuredSuits[suitId][1] - 2
        if self.__suitIsLured(suitId):
            self.currentlyLuredSuits[suitId][0] += 1

    def __removeLured(self, suitId):
        if self.__suitIsLured(suitId):
            del self.currentlyLuredSuits[suitId]

    def __luredMaxRoundsReached(self, suitId):
        return self.__suitIsLured(suitId) and self.currentlyLuredSuits[suitId][0] >= self.currentlyLuredSuits[suitId][1]

    def __incWetCurrRound(self, suitId):
        if self.__suitIsWet(suitId):
            self.currentlyWetSuits[suitId][0] += 1

    def __removeWet(self, suitId):
        if self.__suitIsWet(suitId):
            del self.currentlyWetSuits[suitId]

    def __wetMaxRoundsReached(self, suitId):
        return self.__suitIsWet(suitId) and self.currentlyWetSuits[suitId][0] >= self.currentlyWetSuits[suitId][1]

    def __incEnragedCurrRound(self, suitId):
        if self.__suitIsEnraged(suitId):
            self.currentlyEnragedSuits[suitId][0] += 1

    def __removeEnraged(self, suitId):
        if self.__suitIsEnraged(suitId):
            del self.currentlyEnragedSuits[suitId]

    def __enragedMaxRoundsReached(self, suitId):
        return self.__suitIsEnraged(suitId) and self.currentlyEnragedSuits[suitId][0] >= self.currentlyEnragedSuits[suitId][1]

    def __incAbsorbingCurrRound(self, suitId):
        if self.__suitIsAbsorbing(suitId):
            self.currentlyAbsorbingSuits[suitId][0] += 1

    def __removeAbsorbing(self, suitId):
        if self.__suitIsAbsorbing(suitId):
            del self.currentlyAbsorbingSuits[suitId]

    def __absorbingMaxRoundsReached(self, suitId):
        return self.__suitIsAbsorbing(suitId) and self.currentlyAbsorbingSuits[suitId][0] >= self.currentlyAbsorbingSuits[suitId][1]

    def __luredWakeupTime(self, suitId):
        return self.__suitIsLured(suitId) and self.currentlyLuredSuits[suitId][0] > 0 and random.randint(0, 99) < self.currentlyLuredSuits[suitId][2]

    def itemIsCredit(self, track, level):
        if track == PETSOS:
            return 0
        return level < self.creditLevel

    def __getActualTrack(self, toonAttack):
        if toonAttack[TOON_TRACK_COL] == NPCSOS:
            track = NPCToons.getNPCTrack(toonAttack[TOON_TGT_COL])
            if track != None:
                return track
            else:
                self.notify.warning('No NPC with id: %d' % toonAttack[TOON_TGT_COL])
        return toonAttack[TOON_TRACK_COL]

    def __getActualTrackLevel(self, toonAttack):
        if toonAttack[TOON_TRACK_COL] == NPCSOS:
            track, level, hp = NPCToons.getNPCTrackLevelHp(toonAttack[TOON_TGT_COL])
            if track != None:
                return (track, level)
            else:
                self.notify.warning('No NPC with id: %d' % toonAttack[TOON_TGT_COL])
        return (toonAttack[TOON_TRACK_COL], toonAttack[TOON_LVL_COL])

    def __getActualTrackLevelHp(self, toonAttack):
        if toonAttack[TOON_TRACK_COL] == NPCSOS:
            track, level, hp = NPCToons.getNPCTrackLevelHp(toonAttack[TOON_TGT_COL])
            if track != None:
                return (track, level, hp)
            else:
                self.notify.warning('No NPC with id: %d' % toonAttack[TOON_TGT_COL])
        elif toonAttack[TOON_TRACK_COL] == PETSOS:
            trick = toonAttack[TOON_LVL_COL]
            petProxyId = toonAttack[TOON_TGT_COL]
            trickId = toonAttack[TOON_LVL_COL]
            healRange = PetTricks.TrickHeals[trickId]
            hp = 0
            if petProxyId in simbase.air.doId2do:
                petProxy = simbase.air.doId2do[petProxyId]
                if trickId < len(petProxy.trickAptitudes):
                    aptitude = petProxy.trickAptitudes[trickId]
                    hp = int(lerp(healRange[0], healRange[1], aptitude))
            else:
                self.notify.warning('pet proxy: %d not in doId2do!' % petProxyId)
            return (toonAttack[TOON_TRACK_COL], toonAttack[TOON_LVL_COL], hp)
        return (toonAttack[TOON_TRACK_COL], toonAttack[TOON_LVL_COL], 0)

    def __calculatePetTrickSuccess(self, toonAttack):
        petProxyId = toonAttack[TOON_TGT_COL]
        if not petProxyId in simbase.air.doId2do:
            self.notify.warning('pet proxy %d not in doId2do!' % petProxyId)
            toonAttack[TOON_ACCBONUS_COL] = 1
            return (0, 0)
        petProxy = simbase.air.doId2do[petProxyId]
        trickId = toonAttack[TOON_LVL_COL]
        toonAttack[TOON_ACCBONUS_COL] = petProxy.attemptBattleTrick(trickId)
        if toonAttack[TOON_ACCBONUS_COL] == 1:
            return (0, 0)
        else:
            return (1, 100)
