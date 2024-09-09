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
            boost = 5
        else:
            boost = 0
        suitAttr = SuitBattleGlobals.SuitAttributes.get(suit.dna.name)
        suitDef = SuitBattleGlobals.calculateDefense(suitAttr['level'], suit.getLevel(), boost = boost)
        if self.suitHasCondition(suit.doId, 'immune'):
            suitDef = 100
        if self.suitHasCondition(suit.doId, 'soaked'):
            suitDef -= ToontownBattleGlobals.AvSoakDefReduction
        if self.suitHasCondition(suit.doId, 'dazed'):
            suitDef -= ToontownBattleGlobals.AvDazeDefReduction
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
                damage = getTrapDamage(trapLvl, toon, suit)
                if self.toonHasCondition(attackerId, 'trapBoost'):
                    damage *= (1.0 + self.getToonConditionModifier(attackerId, 'trapBoost') * 0.01)
                    damage = math.ceil(damage)
                if self.toonHasCondition(attackerId, 'allGagBoost'):
                    damage *= (1.0 + self.getToonConditionModifier(attackerId, 'allGagBoost') * 0.01)
                    damage = math.ceil(damage)
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
                if self.suitHasCondition(suitId, 'immune'):
                    damage = 0
                else:
                    damage = getTrapDamage(trapLvl, toon, suit)
                if self.toonHasCondition(attackerId, 'trapBoost'):
                    damage *= (1.0 + self.getToonConditionModifier(attackerId, 'trapBoost') * 0.01)
                    damage = math.ceil(damage)
                if self.toonHasCondition(attackerId, 'allGagBoost'):
                    damage *= (1.0 + self.getToonConditionModifier(attackerId, 'allGagBoost') * 0.01)
                    damage = math.ceil(damage)
                if self.itemIsCredit(TRAP, trapLvl):
                    self.setSuitCondition(suitId, 'dazed', 1, self.NumRoundsDazed[atkLevel] + 1, 'alternateBoth')
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
                                lureKBValue = (ToontownBattleGlobals.AvLureKnockback[atkLevel] * 100)
                                # lureKBValue = (ToontownBattleGlobals.LURE_KNOCKBACK_VALUE * 100)
                                if self.toonHasCondition(toonId, 'lureBoost'):
                                    lureKBValue += self.getToonConditionModifier(toonId, 'lureBoost')
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
                            else:
                                validTargetAvail = 1
                        targetLured = 1
                if not self.SUITS_UNLURED_IMMEDIATELY:
                    if not self.__suitIsLured(targetId, prevRound=1):
                        if not self.__combatantDead(targetId, toon=toonTarget):
                            if self.suitHasCondition(targetId, 'immune'):
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
                    self.setSuitCondition(targetId, 'dazed', 1, self.NumRoundsDazed[atkLevel] + 1, 'alternateBoth')
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
                elif atkTrack == SOUND:
                    attackDamage = getAvPropDamage(attackTrack, attackLevel, toon.experience.getExp(attackTrack))
                    if self.toonHasCondition(toonId, 'soundBoost'):
                        attackDamage *= (1.0 + self.getToonConditionModifier(toonId, 'soundBoost') * 0.01)
                elif atkTrack == HEAL:
                    attackDamage = getAvPropDamage(attackTrack, attackLevel, toon.experience.getExp(attackTrack))
                    if self.toonHasCondition(toonId, 'healBoost'):
                        attackDamage *= (1.0 + self.getToonConditionModifier(toonId, 'healBoost') * 0.01)
                elif atkTrack == SQUIRT:
                    attackDamage = getAvPropDamage(attackTrack, attackLevel, toon.experience.getExp(attackTrack))
                    suit = self.battle.findSuit(targetId)
                    if suit.dna.name == 'lit':
                        self.setToonCondition(toon.doId, 'corruption', 1.2, 3, 'setBoth')
                    self.setSuitCondition(targetId, 'soaked', 1, self.NumRoundsSoaked[attackLevel], 'alternateBoth')
                    if self.toonHasCondition(toonId, 'squirtBoost'):
                        attackDamage *= (1.0 + self.getToonConditionModifier(toonId, 'squirtBoost') * 0.01)
                elif atkTrack == THROW:
                    suit = self.battle.findSuit(targetId)
                    self.setSuitCondition(targetId, 'marked', 1, 1, 'setBoth')
                    attackDamage = getAvPropDamage(attackTrack, attackLevel, toon.experience.getExp(attackTrack))
                    if self.toonHasCondition(toonId, 'throwBoost'):

                        attackDamage *= (1.0 + self.getToonConditionModifier(toonId, 'throwBoost') * 0.01)
                elif atkTrack == DROP:
                    #if self.suitHasCondition(targetId, 'marked'):
                        #attackDamage = getAvPropDamage(attackTrack, attackLevel, toon.experience.getExp(attackTrack)) * 1.1
                    if self.suitHasCondition(targetId, 'soaked'):
                        attackDamage = getAvPropDamage(attackTrack, attackLevel, toon.experience.getExp(attackTrack)) * 1.1
                    else:
                        if self.suitHasCondition(targetId, 'soaked'):
                            chance = ToontownBattleGlobals.DropMissChance[atkLevel] - 15
                        elif self.suitHasCondition(targetId, 'dazed'):
                            chance = ToontownBattleGlobals.DropMissChance[atkLevel] - 20
                        elif self.suitHasCondition(targetId, 'dazed') and self.suitHasCondition(targetId, 'soaked'):
                            chance = ToontownBattleGlobals.DropMissChance[atkLevel] - 30
                        elif self.suitHasCondition(targetId, 'dazed') and self.suitHasCondition(targetId, 'soaked') and self.suitHasCondition(targetId, 'marked'):
                            chance = ToontownBattleGlobals.DropMissChance[atkLevel] - 35
                        else:
                            chance = ToontownBattleGlobals.DropMissChance[atkLevel]
                        if random.randint(0, 99) <= chance:
                            self.notify.debug(
                                'Toon attack rolled' + str(chance))
                            attackDamage = 0
                        else:
                            attackDamage = getAvPropDamage(attackTrack, attackLevel, toon.experience.getExp(attackTrack))
                    if self.toonHasCondition(toonId, 'dropBoost'):
                        attackDamage *= (1.0 + self.getToonConditionModifier(toonId, 'dropBoost') * 0.01)
                    if self.suitHasCondition(targetId, 'dazed'):
                        self.notify.debug('toon doing extra damage to suit due to shadow influence')
                        attackDamage *= (1 + (self.getSuitConditionModifier(targetId, 'dazed') * 0.1))
                elif atkTrack == ZAP:
                    if self.suitHasCondition(targetId, 'soaked'):
                        attackDamage = getAvPropDamage(attackTrack, attackLevel, toon.experience.getExp(attackTrack)) * 3
                        #self.setSuitCondition(targetId, 'soaked', 0, 0, 'alternateBoth')
                    else:
                        attackDamage = getAvPropDamage(attackTrack, attackLevel, toon.experience.getExp(attackTrack))
                    if self.toonHasCondition(toonId, 'zapBoost'):
                        attackDamage *= (1.0 + self.getToonConditionModifier(toonId, 'zapBoost') * 0.01)
                    if self.__isWet(targetId) or self.__isRaining(self.battle.getToon(toonId)):
                        chance = InstaKillChance[atkLevel]
                        if organicBonus:
                            chance = int(InstaKillChance[atkLevel] * 1.5)
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
                if self.toonHasCondition(toonId, 'allGagBoost') and atkTrack is not FIRE:
                    attackDamage *= (1.0 + (self.getToonConditionModifier(toonId, 'allGagBoost') * 0.01))
                    attackDamage = math.ceil(attackDamage)
                elif self.suitHasCondition(targetId, 'marked') and not atkTrack == THROW:
                    self.notify.debug('toon doing extra damage to suit due to shadow influence')
                    attackDamage *= (1 + (self.getSuitConditionModifier(targetId, 'marked') * 0.1))
                elif self.suitHasCondition(targetId, 'immune'):
                    attackDamage = 0
                elif self.suitHasCondition(targetId, 'enraged') and self.suitHasCondition(targetId, 'desperation') and self.suitHasCondition(targetId, 'marked') and not atkTrack == THROW:
                    self.notify.debug('toon doing extra damage to suit due to shadow influence')
                    attackDamage *= (1 + (self.getSuitConditionModifier(targetId, 'marked') * 0.1))
                elif self.suitHasCondition(targetId, 'enraged') and self.suitHasCondition(targetId, 'desperation'):
                    attackDamage *= 1
                elif self.suitHasCondition(targetId, 'enraged'):
                    attackDamage *= 0.7
                attackDamage = math.ceil(attackDamage)
                if not self.__combatantDead(targetId, toon=toonTarget):
                    if self.__suitIsLured(targetId) and atkTrack == DROP:
                        self.notify.debug('not setting validTargetAvail, since drop on a lured suit')
                    else:
                        validTargetAvail = 1
            if attackLevel == -1 and not atkTrack == FIRE:
                if self.suitHasCondition(targetId, 'immune'):
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
                    result = result / len(targetList)
                    toon = self.battle.getToon(toonId)
                    toon.toonUp(math.ceil((attackDamage / 2.5) / len(targetList)))
                if atkTrack == THROW:
                    result = result / len(targetList)
                    toon = self.battle.getToon(toonId)
                    toon.toonUp(math.ceil((attackDamage / 5)))
                if targetId in self.successfulLures and atkTrack == LURE:
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
                return 1
        return 0

    def __combatantJustRevived(self, avId):
        suit = self.battle.findSuit(avId)
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

        atkAcc = atkInfo['acc']
        suitAcc = SuitBattleGlobals.SuitAttributes[theSuit.dna.name]['acc'][theSuit.getLevel()]
        acc = atkAcc
        randChoice = random.randint(0, 99)
        if self.notify.getDebug():
            self.notify.debug('Suit attack rolled ' + str(randChoice) + ' to hit with an accuracy of ' + str(acc) + ' (attackAcc: ' + str(atkAcc) + ' suitAcc: ' + str(suitAcc) + ')')
        if randChoice < acc:
            return 1
        return 0

    def __suitAtkAffectsGroup(self, attack):
        atkType = attack[SUIT_ATK_COL]
        theSuit = self.battle.findSuit(attack[SUIT_ID_COL])
        atkInfo = SuitBattleGlobals.getSuitAttack(theSuit.dna.name, theSuit.getLevel(), atkType)
        return atkInfo['group'] != SuitBattleGlobals.ATK_TGT_SINGLE

    def __createSuitTargetList(self, attackIndex):
        attack = self.battle.suitAttacks[attackIndex]
        targetList = []
        if attack[SUIT_ATK_COL] == NO_ATTACK:
            self.notify.debug('No attack, no targets')
            return targetList
        debug = self.notify.getDebug()
        if not self.__suitAtkAffectsGroup(attack):
            targetList.append(self.battle.activeToons[attack[SUIT_TGT_COL]])
            if debug:
                self.notify.debug('Suit attack is single target')
        else:
            if debug:
                self.notify.debug('Suit attack is group target')
            for currToon in self.battle.activeToons:
                if debug:
                    self.notify.debug('Suit attack will target toon' + str(currToon))
                targetList.append(currToon)

        return targetList

    def __calcSuitAtkHp(self, attackIndex):
        targetList = self.__createSuitTargetList(attackIndex)
        attack = self.battle.suitAttacks[attackIndex]
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
            elif self.__suitAtkHit(attackIndex):
                atkType = attack[SUIT_ATK_COL]
                theSuit = self.battle.findSuit(attack[SUIT_ID_COL])
                atkInfo = SuitBattleGlobals.getSuitAttack(theSuit.dna.name, theSuit.getLevel(), atkType)
                if theSuit.getElite():
                    mult = 1.0
                else:
                    mult = 1.0
                mult *= theSuit.getDamageMultiplier()
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
                attack[SUIT_HP_COL][targetIndex] = 30 * theSuit.getDamageMultiplier()
                if self.toonHasCondition(toonId, 'corruption'):
                    attack[SUIT_HP_COL][targetIndex] = 7 + int(floor(self.getToonConditionModifier(toonId, 'corruption') / 4.0) * 7)
            elif atkInfo['name'] == 'Gavel':
                result = 35 * theSuit.getDamageMultiplier()
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'noGags', 1, 2, 'setBoth')
                #self.setToonCondition(toon.doId, 'noSOS', 1, 2, 'setBoth')
                #self.setToonCondition(toon.doId, 'noFires', 1, 2, 'setBoth')
            elif atkInfo['name'] == 'Accusations':
                theSuit.setHP(int(theSuit.currHP + 1000))
                self.setSuitCondition(theSuit.doId, 'desperation', 1, 100, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'immune', 1, 2, 'setBoth')
            elif atkInfo['name'] == 'Accusations2':
                result = 25 * theSuit.getDamageMultiplier()
                attack[SUIT_HP_COL][targetIndex] = result
                theSuit.setHP(int(theSuit.currHP - 350))
                self.setToonCondition(toon.doId, 'allGagBoost', 25, 3, 'setBoth')
            elif atkInfo['name'] == 'Cage':
                result = 35 * theSuit.getDamageMultiplier()
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'noGags', 1, 2, 'setBoth')
                self.setToonCondition(toon.doId, 'noSOS', 1, 2, 'setBoth')
                self.setToonCondition(toon.doId, 'noFires', 1, 2, 'setBoth')
                self.setToonCondition(toon.doId, 'noUnites', 1, 2, 'setBoth')
            elif atkInfo['name'] == 'InkDrain':
                result = 35 * theSuit.getDamageMultiplier()
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'noGags', 1, 2, 'setBoth')
                self.setToonCondition(toon.doId, 'noSOS', 1, 2, 'setBoth')
                self.setToonCondition(toon.doId, 'noFires', 1, 2, 'setBoth')
                self.setToonCondition(toon.doId, 'noUnites', 1, 2, 'setBoth')
            elif atkInfo['name'] == 'WheelSpin':
                result = 35 * theSuit.getDamageMultiplier()
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'noGags', 1, 2, 'setBoth')
            elif atkInfo['name'] == 'BookKeeping':
                result = 35 * theSuit.getDamageMultiplier()
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'noGags', 1, 2, 'setBoth')
                self.setToonCondition(toon.doId, 'noSOS', 1, 2, 'setBoth')
                self.setToonCondition(toon.doId, 'noFires', 1, 2, 'setBoth')
                self.setToonCondition(toon.doId, 'noUnites', 1, 2, 'setBoth')
            elif atkInfo['name'] == 'CourtMandate':
                self.setToonCondition(toon.doId, 'noSquirtGags', 1, 3, 'setBoth')
                self.setToonCondition(toon.doId, 'noZapGags', 1, 3, 'setBoth')
            elif atkInfo['name'] == 'CourtMandate1':
                self.setToonCondition(toon.doId, 'noToonUpGags', 1, 3, 'setBoth')
                self.setToonCondition(toon.doId, 'noSoundGags', 1, 3, 'setBoth')
            elif atkInfo['name'] == 'CourtMandate2':
                self.setToonCondition(toon.doId, 'noLureGags', 1, 3, 'setBoth')
                self.setToonCondition(toon.doId, 'noThrowGags', 1, 3, 'setBoth')
            elif atkInfo['name'] == 'CourtMandate3':
                self.setToonCondition(toon.doId, 'noTrapGags', 1, 3, 'setBoth')
                self.setToonCondition(toon.doId, 'noDropGags', 1, 3, 'setBoth')
            elif atkInfo['name'] == 'QualityControl':
                self.setToonCondition(toon.doId, 'noSquirtGags', 1, 3, 'setBoth')
                self.setToonCondition(toon.doId, 'noZapGags', 1, 3, 'setBoth')
            elif atkInfo['name'] == 'QualityControl1':
                self.setToonCondition(toon.doId, 'noToonUpGags', 1, 3, 'setBoth')
                self.setToonCondition(toon.doId, 'noSoundGags', 1, 3, 'setBoth')
            elif atkInfo['name'] == 'QualityControl2':
                self.setToonCondition(toon.doId, 'noLureGags', 1, 3, 'setBoth')
                self.setToonCondition(toon.doId, 'noThrowGags', 1, 3, 'setBoth')
            elif atkInfo['name'] == 'QualityControl3':
                self.setToonCondition(toon.doId, 'noTrapGags', 1, 3, 'setBoth')
                self.setToonCondition(toon.doId, 'noDropGags', 1, 3, 'setBoth')
            elif atkInfo['name'] == 'QualityLvlControl':
                self.setToonCondition(toon.doId, 'nolevel6s', 1, 3, 'setBoth')
                self.setToonCondition(toon.doId, 'nolevel7s', 1, 3, 'setBoth')
                self.setToonCondition(toon.doId, 'nolevel5s', 1, 0, 'setBoth')
                self.setToonCondition(toon.doId, 'nolevel8s', 1, 0, 'setBoth')
            elif atkInfo['name'] == 'QualityLvlControl1':
                self.setToonCondition(toon.doId, 'nolevel5s', 1, 3, 'setBoth')
                self.setToonCondition(toon.doId, 'nolevel7s', 1, 3, 'setBoth')
                self.setToonCondition(toon.doId, 'nolevel8s', 1, 0, 'setBoth')
                self.setToonCondition(toon.doId, 'nolevel6s', 1, 0, 'setBoth')
            elif atkInfo['name'] == 'QualityLvlControl2':
                self.setToonCondition(toon.doId, 'nolevel7s', 1, 3, 'setBoth')
                self.setToonCondition(toon.doId, 'nolevel8s', 1, 3, 'setBoth')
                self.setToonCondition(toon.doId, 'nolevel5s', 1, 0, 'setBoth')
                self.setToonCondition(toon.doId, 'nolevel6s', 1, 0, 'setBoth')
            elif atkInfo['name'] == 'QualityLvlControl3':
                self.setToonCondition(toon.doId, 'nolevel8s', 1, 3, 'setBoth')
                self.setToonCondition(toon.doId, 'nolevel6s', 1, 3, 'setBoth')
                self.setToonCondition(toon.doId, 'nolevel7s', 1, 0, 'setBoth')
                self.setToonCondition(toon.doId, 'nolevel5s', 1, 0, 'setBoth')
            elif atkInfo['name'] == 'CourtRecord1':
                self.setToonCondition(toon.doId, 'nolevel6s', 1, 3, 'setBoth')
                self.setToonCondition(toon.doId, 'nolevel7s', 1, 3, 'setBoth')
                self.setToonCondition(toon.doId, 'nolevel5s', 1, 0, 'setBoth')
                self.setToonCondition(toon.doId, 'nolevel8s', 1, 0, 'setBoth')
            elif atkInfo['name'] == 'CourtRecord2':
                self.setToonCondition(toon.doId, 'nolevel5s', 1, 3, 'setBoth')
                self.setToonCondition(toon.doId, 'nolevel7s', 1, 3, 'setBoth')
                self.setToonCondition(toon.doId, 'nolevel8s', 1, 0, 'setBoth')
                self.setToonCondition(toon.doId, 'nolevel6s', 1, 0, 'setBoth')
            elif atkInfo['name'] == 'CourtRecord3':
                self.setToonCondition(toon.doId, 'nolevel5s', 1, 3, 'setBoth')
                self.setToonCondition(toon.doId, 'nolevel8s', 1, 3, 'setBoth')
                self.setToonCondition(toon.doId, 'nolevel7s', 1, 0, 'setBoth')
                self.setToonCondition(toon.doId, 'nolevel6s', 1, 0, 'setBoth')
            elif atkInfo['name'] == 'CourtRecord4':
                self.setToonCondition(toon.doId, 'nolevel8s', 1, 3, 'setBoth')
                self.setToonCondition(toon.doId, 'nolevel6s', 1, 3, 'setBoth')
                self.setToonCondition(toon.doId, 'nolevel7s', 1, 0, 'setBoth')
                self.setToonCondition(toon.doId, 'nolevel5s', 1, 0, 'setBoth')
            elif atkInfo['name'] == 'CourtRecord5':
                self.setToonCondition(toon.doId, 'nolevel7s', 1, 3, 'setBoth')
                self.setToonCondition(toon.doId, 'nolevel8s', 1, 3, 'setBoth')
                self.setToonCondition(toon.doId, 'nolevel5s', 1, 0, 'setBoth')
                self.setToonCondition(toon.doId, 'nolevel6s', 1, 0, 'setBoth')
            elif atkInfo['name'] == 'Drowning':
                result = 35 * theSuit.getDamageMultiplier()
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'noToonUpGags', 1, 2, 'setBoth')
                self.setToonCondition(toon.doId, 'noSoundGags', 1, 2, 'setBoth')
            elif atkInfo['name'] == 'Snap':
                result = 21.5 * theSuit.getDamageMultiplier()
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'corruption', 1.4, 3, 'setBoth')
            elif atkInfo['name'] == 'CollectCall':
                result = 21.5 * theSuit.getDamageMultiplier()
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'corruption', 1.4, 3, 'setBoth')
            elif atkInfo['name'] == 'Snap2':
                result = 38 * theSuit.getDamageMultiplier()
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'corruption', 1.1, 3, 'setBoth')
            elif atkInfo['name'] == 'Caress':
                result = random.randint(15, 40) * theSuit.getDamageMultiplier()
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'corruption', 1.4, 3, 'setBoth')
            elif atkInfo['name'] == 'ExplodingBill':
                result = 30 * theSuit.getDamageMultiplier()
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'corruption', 1.25, 3, 'setBoth')
            elif atkInfo['name'] == 'Blast':
                result = random.randint(25, 50) * theSuit.getDamageMultiplier()
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'noSOS', 1, 2, 'setBoth')
                self.setToonCondition(toon.doId, 'noFires', 1, 2, 'setBoth')
                self.setToonCondition(toon.doId, 'noUnites', 1, 2, 'setBoth')
            elif atkInfo['name'] == 'LegalBindings':
                result = 25 * theSuit.getDamageMultiplier()
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'corruption', 1.1, 3, 'setBoth')
            elif atkInfo['name'] == 'Investment':
                result = random.randint(35, 60) * theSuit.getDamageMultiplier()
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'cannotDodge', 100, 2, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'cannotDodge', 100, 2, 'setBoth')
                for suit in self.currentlyLuredSuits.keys():
                    self.__removeLured(suit)
                for suit in self.battle.activeSuits:
                    suit.setHP(int(suit.currHP - 100))
                    if self.suitHasCondition(suit.doId, 'lured'):
                        self.setSuitCondition(suit.doId, 'lured', 0, 0, 'setBoth')
                    continue
            elif atkInfo['name'] == 'Synergy':
                result = (24 + (self.TurnsElapsed * 1.3)) * theSuit.getDamageMultiplier()
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'nolevel6s', 1, 0, 'setBoth')
                self.setToonCondition(toon.doId, 'nolevel7s', 1, 2, 'setBoth')
                self.setToonCondition(toon.doId, 'nolevel8s', 1, 2, 'setBoth')
                self.setToonCondition(toon.doId, 'nolevel5s', 1, 0, 'setBoth')
            elif atkInfo['name'] == 'CollectCallFees':
                result = (24 + (self.TurnsElapsed * 1.3)) * theSuit.getDamageMultiplier()
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'nolevel6s', 1, 2, 'setBoth')
                self.setToonCondition(toon.doId, 'nolevel8s', 1, 2, 'setBoth')
                self.setToonCondition(toon.doId, 'nolevel7s', 1, 0, 'setBoth')
                self.setToonCondition(toon.doId, 'nolevel5s', 1, 0, 'setBoth')
            elif atkInfo['name'] == 'HeavyRainfall':
                result = (24 + (self.TurnsElapsed * 1.3)) * theSuit.getDamageMultiplier()
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'nolevel6s', 1, 2, 'setBoth')
                self.setToonCondition(toon.doId, 'nolevel7s', 1, 2, 'setBoth')
                self.setToonCondition(toon.doId, 'nolevel8s', 1, 0, 'setBoth')
                self.setToonCondition(toon.doId, 'nolevel5s', 1, 0, 'setBoth')
            elif atkInfo['name'] == 'RadioInfrequency':
                self.setToonCondition(toon.doId, 'soundBoost', -50, 2, 'setBoth')
                self.setToonCondition(toon.doId, 'lureBoost', -50, 2, 'setBoth')
            elif atkInfo['name'] == 'CourtCosts':
                result = (24 + (self.TurnsElapsed * 1.3)) * theSuit.getDamageMultiplier()
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'nolevel6s', 1, 2, 'setBoth')
                self.setToonCondition(toon.doId, 'nolevel8s', 1, 2, 'setBoth')
                self.setToonCondition(toon.doId, 'nolevel7s', 1, 0, 'setBoth')
                self.setToonCondition(toon.doId, 'nolevel5s', 1, 0, 'setBoth')
            elif atkInfo['name'] == 'UnionDues':
                result = (24 + (self.TurnsElapsed * 1.3)) * theSuit.getDamageMultiplier()
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'nolevel8s', 1, 2, 'setBoth')
                self.setToonCondition(toon.doId, 'nolevel7s', 1, 2, 'setBoth')
                self.setToonCondition(toon.doId, 'nolevel5s', 1, 0, 'setBoth')
                self.setToonCondition(toon.doId, 'nolevel6s', 1, 0, 'setBoth')
            elif atkInfo['name'] == 'LifeInsurance':
                theSuit.setHP(int(theSuit.currHP + 75))
            elif atkInfo['name'] == 'Voicemail':
                self.setSuitCondition(theSuit.doId, 'immune', 1, 2, 'setBoth')
            elif atkInfo['name'] == 'ManagerialProtection':
                self.setSuitCondition(theSuit.doId, 'immune', 1, 2, 'setBoth')
            elif atkInfo['name'] == 'WorkersCompensation':
                theSuit.setHP(int(theSuit.currHP + 50))
            elif atkInfo['name'] == 'asghashsah':
                from toontown.suit.DistributedLawbotBossAI import DistributedLawbotBossAI

                boss = None
                for do in simbase.air.doId2do.values():

                        continue

                    suit.setHP(suit.currHP + 75)
                    continue
            elif atkInfo['name'] == 'Snow':
                result = 30 * theSuit.getDamageMultiplier()
                attack[SUIT_HP_COL][targetIndex] = result
                theSuit.setHP(int(theSuit.currHP + (result * 2)))
                self.setSuitCondition(theSuit.doId, 'enraged', 0, 0, 'setBoth')
            elif atkInfo['name'] == 'Spotlight':
                for suit in self.battle.activeSuits:
                    if suit.currHP <= 0:
                        continue

                    suit.setHP(suit.currHP + 500)
                    continue
            elif atkInfo['name'] == 'OilRain':
                result = random.randint(25, 50) * theSuit.getDamageMultiplier()
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'healBoost', -50, 2, 'setBoth')
                self.setToonCondition(toon.doId, 'lureBoost', -50, 2, 'setBoth')
                self.setToonCondition(toon.doId, 'squirtBoost', -50, 2, 'setBoth')
                self.setToonCondition(toon.doId, 'soundBoost', -50, 2, 'setBoth')
            elif atkInfo['name'] == 'Refinement':
                for suit in self.battle.activeSuits:
                    if suit.currHP <= 0:
                        continue

                    suit.setHP(suit.currHP + 75)
                    continue
, 'lured'):
                        self.setSuitCondition(suit.doId, 'lured', 0, 0, 'setBoth')
                    continue
                for suit in self.currentlyLuredSuits.keys():
                    self.__removeLured(suit)
            elif atkInfo['name'] == 'CeaseAndDesist':
                for suit in self.currentlyLuredSuits.keys():
                    self.__removeLured(suit)
            elif atkInfo['name'] == 'GoodMorningToontown':
                for suit in self.currentlyLuredSuits.keys():
                    self.__removeLured(suit)
            elif atkInfo['name'] == 'MobMentality':
                for suit in self.battle.activeSuits:
                    if suit.currHP <= 0:
                        continue

                    suit.setHP(suit.currHP + 100)
                    if self.suitHasCondition(suit.doId, 'lured'):
                        self.setSuitCondition(suit.doId, 'lured', 0, 0, 'setBoth')
                    continue
                for suit in self.currentlyLuredSuits.keys():
                    self.__removeLured(suit)
            elif atkInfo['name'] == 'HeatWave':
                result = (36 + (self.TurnsElapsed * 2)) * theSuit.getDamageMultiplier()
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'nolevel6s', 1, 2, 'setBoth')
                self.setToonCondition(toon.doId, 'nolevel7s', 1, 2, 'setBoth')
            elif atkInfo['name'] == 'StealSafe':
                result = random.randint(30, 50) * theSuit.getDamageMultiplier()
                attack[SUIT_HP_COL][targetIndex] = result
                theSuit.setHP(int(theSuit.currHP + (result * 3)))
            elif atkInfo['name'] == 'Wiretapped':
                result = random.randint(25, 50) * theSuit.getDamageMultiplier()
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'allGagBoost', 25, 2, 'setBoth')
                theSuit.setHP(int(theSuit.currHP + attack[SUIT_HP_COL][
                    targetIndex] * 3))
            #elif atkInfo['name'] == 'WhitePowder':
                #for suit in self.currentlyLuredSuits.keys():
                    #self.__removeLured(suit)
            elif atkInfo['name'] == 'HeadRoller':
                #attack[SUIT_HP_COL][targetIndex] = 1
                targetSuit = self.battle.activeSuits[attack[SUIT_ATK_COL] + 2]
                theSuit.setHP(int(theSuit.currHP + targetSuit.maxHP))
                targetSuit.setHP(0)
                for targetSuit in self.currentlyLuredSuits.keys():
                    self.__removeLured(targetSuit)
            elif atkInfo['name'] == 'HeadRoller2':
                #attack[SUIT_HP_COL][targetIndex] = 1
                targetSuit = self.battle.activeSuits[attack[SUIT_ATK_COL] + 2]
                theSuit.setHP(int(theSuit.currHP + targetSuit.maxHP))
                targetSuit.setHP(0)
                for targetSuit in self.currentlyLuredSuits.keys():
                    self.__removeLured(targetSuit)
            elif atkInfo['name'] == 'Detonate':
                attack[SUIT_HP_COL][targetIndex] = 45 * theSuit.getDamageMultiplier()
                targetSuit = self.battle.activeSuits[attack[SUIT_ATK_COL] + 2]
                targetSuit.setHP(int(targetSuit.currHP - targetSuit.currHP))
                theSuit.setHP(int(theSuit.currHP + targetSuit.currHP))
            #elif atkInfo['name'] == 'HeadRoller3':
                #targetSuit = self.battle.activeSuits[attack[SUIT_ATK_COL] - 5]
                #theSuit.setHP(int(theSuit.currHP + targetSuit.currHP))
            elif atkInfo['name'] == 'Enraged':
                attack[SUIT_HP_COL][targetIndex] = 20 * theSuit.getDamageMultiplier()
                self.setSuitCondition(theSuit.doId, 'enraged', 1, 5, 'setBoth')
            else:
                self.notify.debug('__calcSuitAtkHp - Target is not corrupt, not doing any bonus here')
                attack[SUIT_HP_COL][targetIndex] = result

            if self.suitHasCondition(theSuit.doId, 'desperation') and self.suitHasCondition(theSuit.doId, 'enraged') and self.toonHasCondition(toonId, 'corruption') and result > 0:
                attack[SUIT_HP_COL][targetIndex] *= (.7 + self.getToonConditionModifier(toonId, 'corruption'))
            elif self.suitHasCondition(theSuit.doId, 'enraged') and self.toonHasCondition(toonId, 'corruption') and result > 0:
                attack[SUIT_HP_COL][targetIndex] *= (.3 + self.getToonConditionModifier(toonId, 'corruption'))
            elif self.suitHasCondition(theSuit.doId, 'desperation') and self.suitHasCondition(theSuit.doId, 'enraged') and result > 0:
                attack[SUIT_HP_COL][targetIndex] *= 1.8
            elif self.suitHasCondition(theSuit.doId, 'desperation') and self.toonHasCondition(toonId, 'corruption') and result > 0:
                attack[SUIT_HP_COL][targetIndex] *= (.4 + self.getToonConditionModifier(toonId, 'corruption'))
            elif self.toonHasCondition(toonId, 'corruption') and result > 0 and theSuit.getHP() > (theSuit.getMaxHP() * 1.5):
                attack[SUIT_HP_COL][targetIndex] *= (.5 + self.getToonConditionModifier(toonId, 'corruption'))
            elif self.toonHasCondition(toonId, 'corruption') and result > 0:
                attack[SUIT_HP_COL][targetIndex] *= self.getToonConditionModifier(toonId, 'corruption')
            elif self.suitHasCondition(theSuit.doId, 'enraged') and result > 0:
                attack[SUIT_HP_COL][targetIndex] *= 1.3
            elif self.suitHasCondition(theSuit.doId, 'desperation') and result > 0:
                attack[SUIT_HP_COL][targetIndex] *= 1.4
            elif theSuit.getHP() > (theSuit.getMaxHP() * 1.5):
                attack[SUIT_HP_COL][targetIndex] *= 1.5
            else:
                attack[SUIT_HP_COL][targetIndex] = result

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

    def __applySuitAttackDamages(self, attackIndex):
        attack = self.battle.suitAttacks[attackIndex]
        theSuit = self.battle.activeSuits[attackIndex]
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
        if self.__combatantDead(suitId, toon=0) or self.__suitIsLured(suitId) or self.__combatantJustRevived(suitId):
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
        for i in xrange(len(self.battle.suitAttacks)):
            if i < len(self.battle.activeSuits):
                suitId = self.battle.activeSuits[i].doId
                self.battle.suitAttacks[i][SUIT_ID_COL] = suitId
                if not self.__suitCanAttack(suitId):
                    if self.notify.getDebug():
                        self.notify.debug("Suit %d can't attack" % suitId)
                    continue
                if self.battle.pendingSuits.count(self.battle.activeSuits[i]) > 0 or self.battle.joiningSuits.count(self.battle.activeSuits[i]) > 0:
                    continue
                attack = self.battle.suitAttacks[i]
                attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                attack[SUIT_ATK_COL] = self.__calcSuitAtkType(i)
                attack[SUIT_TGT_COL] = self.__calcSuitTarget(i)
                if attack[SUIT_TGT_COL] == -1:
                    self.battle.suitAttacks[i] = getDefaultSuitAttack()
                    attack = self.battle.suitAttacks[i]
                self.__calcSuitAtkHp(i)
                if attack[SUIT_ATK_COL] != NO_ATTACK:
                    if self.__suitAtkAffectsGroup(attack):
                        for currTgt in self.battle.activeToons:
                            self.__updateSuitAtkStat(currTgt)

                    else:
                        tgtId = self.battle.activeToons[attack[SUIT_TGT_COL]]
                        self.__updateSuitAtkStat(tgtId)
                targets = self.__createSuitTargetList(i)
                allTargetsDead = 1
                for currTgt in targets:
                    if self.__getToonHp(currTgt) > 0:
                        allTargetsDead = 0
                        break

                if allTargetsDead:
                    self.battle.suitAttacks[i] = getDefaultSuitAttack()
                    attack = self.battle.suitAttacks[i]
                if self.__attackHasHit(attack, suit=1):
                    self.__applySuitAttackDamages(i)
                attack[SUIT_BEFORE_TOONS_COL] = 0

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
                'healBoost', 'trapBoost', 'lureBoost', 'soundBoost', 'throwBoost', 'squirtBoost', 'zapBoost', 'dropBoost',
                'allGagBoost')
                for t in self.battle.activeToons:
                    toon = self.battle.getToon(t)
                    if toon != None:
                        self.setToonCondition(toon.doId, lvToDict[npc_level], npc_hp, 3, 'alternateBoth')
                        self.setToonCondition(toon.doId, 'noSOS', 1, 5, 'setBoth')
                        self.setToonCondition(toon.doId, 'noFires', 1, 5, 'setBoth')
                        self.setToonCondition(toon.doId, 'noUnites', 1, 5, 'setBoth')
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

        for i in xrange(6):
            for j in xrange(len(self.battle.activeToons)):
                self.battle.suitAttacks[i][SUIT_HP_COL].append(-1)

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
        if x % 3 == 0 and theSuit.dna.name == 'scg':
            self.currentlyLuredSuits[suitId][0] = self.currentlyLuredSuits[suitId][1] - 1
        if x % 3 == 0 and theSuit.dna.name == 'dar':
            self.currentlyLuredSuits[suitId][0] = self.currentlyLuredSuits[suitId][1] - 1
        if x % 3 == 0 and theSuit.dna.name == 'ghd':
            self.currentlyLuredSuits[suitId][0] = self.currentlyLuredSuits[suitId][1] - 1
        if x % 5 == 0 and theSuit.dna.name == 'ghd':
            self.currentlyLuredSuits[suitId][0] = self.currentlyLuredSuits[suitId][1] - 1
        if self.suitHasCondition(suitId, 'enraged') and self.currentlyLuredSuits[suitId][0] < 1:
            self.currentlyLuredSuits[suitId][0] = self.currentlyLuredSuits[suitId][1] - 1
        if self.suitHasCondition(suitId, 'desperation') and self.currentlyLuredSuits[suitId][0] < 1:
            self.currentlyLuredSuits[suitId][0] = self.currentlyLuredSuits[suitId][1] - 1
        if self.battle.findSuit(suitId).getManager() and self.currentlyLuredSuits[suitId][0] < 1:
            self.currentlyLuredSuits[suitId][0] = self.currentlyLuredSuits[suitId][1] - 2
        if self.suitHasCondition(suitId, 'immune'):
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
