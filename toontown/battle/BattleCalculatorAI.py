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
    notify.setDebug(False)
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
        self.absorbDamage = 0
        self.levelDamage = 0
        self.traps = {}
        self.npcTraps = {}
        self.suitAtkStats = {}
        self.deadSuits = 0
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
        self.costsMultiplier = 20
        self.costsCalculatorMultiplier = 24

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
                        'decrementConditionTurns() - Decremented %s condition on suit %i (new turns: %i new modifier: %i)' % (
                        condition, suit, self.suitStatusConditions[suit][condition]['turnsRemaining'] - 1, self.suitStatusConditions[suit][condition]['modifier']))
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
        if atkTrack == SUE:
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
                if suit.dna.name == 'bkeeper' and self.suitHasCondition(suitId, 'bookkeeping'):
                    self.setToonCondition(toon.doId, 'bookkeepingtoon', 1, 5, 'setBoth')
               # for s in self.battle.activeSuits:
                   # if s.dna.name == 'sgoat' and self.suitHasCondition(s.doId, 'shielding'):
                     #   self.setSuitCondition(s.doId, 'rageBuilding', self.getSuitConditionModifier(s.doId, 'rageBuilding') + 10, 99, 'setBoth')
                      #  self.notify.debug('setSuitCondition() - scapegoat rage building %i' % (self.getSuitConditionModifier(s.doId, 'rageBuilding')))
                if self.toonHasCondition(toon.doId, 'useTrap'):
                    self.setToonCondition(toon.doId, 'rushJobCompleted', 1, 3, 'setBoth')
                self.setToonCondition(toon.doId, 'usedTrap', 1, 3, 'setBoth')
                if organicBonus:
                    damage = (getTrapDamage(trapLvl, toon, suit) * 1.15)
                    self.setSuitCondition(suitId, 'dazed2', 1, 10, 'setBoth')
                else:
                    damage = getTrapDamage(trapLvl, toon, suit)
                    self.setSuitCondition(suitId, 'dazed2', 1, 10, 'setBoth')
                if self.suitHasCondition(suitId, 'sued'):
                    self.setSuitCondition(suitId, 'sued', 1, 4, 'alternateBoth')
                if self.suitHasCondition(suitId, 'lured'):
                    self.setSuitCondition(suitId, 'lured', 0, 0, 'setBoth')
                if self.suitHasCondition(suitId, 'immune'):
                    damage = 0
                if self.suitHasCondition(suitId, 'HRdamagereduction'):
                    damage *= 0.1
                if self.suitHasCondition(suitId, 'vulnerablebroadcaster'):
                    damage *= 2
                if self.suitHasCondition(suitId, 'vulnerablesilhouette1'):
                    damage *= 1.5
                if self.suitHasCondition(suitId, 'vulnerablesilhouette2'):
                    damage *= 2
                if self.suitHasCondition(suitId, 'vulnerablesilhouette3'):
                    damage *= 3
                if self.toonHasCondition(attackerId, 'trapBoost'):
                    damage *= (1.0 + self.getToonConditionModifier(attackerId, 'trapBoost') * 0.01)
                if self.toonHasCondition(attackerId, 'allGagBoost'):
                    damage *= (1.0 + self.getToonConditionModifier(attackerId, 'allGagBoost') * 0.01)
                if self.toonHasCondition(attackerId, 'raisedAnte'):
                    damage *= (1.0 + self.getToonConditionModifier(attackerId, 'raisedAnte') * 0.01)
                if self.toonHasCondition(attackerId, 'encore'):
                    damage *= 1.2
                if self.toonHasCondition(attackerId, 'encore2'):
                    damage *= 1.1
                if self.suitHasCondition(suitId, 'enraged') and not self.suitHasCondition(suitId, 'desperation'):
                    damage *= 0.7
                if self.suitHasCondition(suitId, 'brokenconnection'):
                    damage *= 1.3
                if self.suitHasCondition(suitId, 'vulnerablevideographer'):
                    damage *= (1.0 + (self.getSuitConditionModifier(suit.doId, 'vulnerablevideographer') * 0.01))
                if self.suitHasCondition(suitId, 'enraged') and self.suitHasCondition(suitId, 'desperation'):
                    damage *= 1
               # if self.suitHasCondition(suitId, 'enraged'):
                   # damage *= 0.7
                if self.suitHasCondition(suitId, 'dancesession'):
                    damage *= 0.7
                if self.suitHasCondition(suitId, 'soakImmune') and self.suitHasCondition(suitId, 'soaked'):
                    damage *= 0.4
             #   for s in self.battle.activeSuits:
                  #  if self.suitHasCondition(s.doId, 'shielding') and not self.suitHasCondition(suitId, 'shielding'):
                    #    damage *= .7
                        #self.absorbDamage += int((damage * .425))
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
               # for s in self.battle.activeSuits:
                   # if s.dna.name == 'sgoat' and self.suitHasCondition(s.doId, 'shielding'):
                    #    self.setSuitCondition(s.doId, 'rageBuilding', self.getSuitConditionModifier(s.doId, 'rageBuilding') + 10, 99, 'setBoth')
                      #  self.notify.debug('setSuitCondition() - scapegoat rage building %i' % (
                         #   self.getSuitConditionModifier(s.doId, 'rageBuilding')))
                if suit.dna.name == 'bkeeper' and self.suitHasCondition(suitId, 'bookkeeping'):
                    self.setToonCondition(toon.doId, 'bookkeepingtoon', 1, 5, 'setBoth')
                if self.toonHasCondition(toon.doId, 'useTrap'):
                    self.setToonCondition(toon.doId, 'rushJobCompleted', 1, 3, 'setBoth')
                self.setToonCondition(toon.doId, 'usedTrap', 1, 3, 'setBoth')
                if organicBonus:
                    damage = (getTrapDamage(trapLvl, toon, suit) * 1.15)
                    self.setSuitCondition(suitId, 'dazed2', 1, 10, 'setBoth')
                else:
                    damage = getTrapDamage(trapLvl, toon, suit)
                    self.setSuitCondition(suitId, 'dazed2', 1, 10, 'setBoth')
                if self.suitHasCondition(suitId, 'sued'):
                    self.setSuitCondition(suitId, 'sued', 1, 4, 'alternateBoth')
                if self.suitHasCondition(suitId, 'lured'):
                    self.setSuitCondition(suitId, 'lured', 0, 0, 'setBoth')
                if self.suitHasCondition(suitId, 'immune'):
                    damage = 0
                if self.suitHasCondition(suitId, 'HRdamagereduction'):
                    damage *= 0.1
                if self.toonHasCondition(attackerId, 'trapBoost'):
                    damage *= (1.0 + self.getToonConditionModifier(attackerId, 'trapBoost') * 0.01)
                if self.toonHasCondition(attackerId, 'allGagBoost'):
                    damage *= (1.0 + self.getToonConditionModifier(attackerId, 'allGagBoost') * 0.01)
                if self.toonHasCondition(attackerId, 'raisedAnte'):
                    damage *= (1.0 + self.getToonConditionModifier(attackerId, 'raisedAnte') * 0.01)
                if self.toonHasCondition(attackerId, 'encore'):
                    damage *= 1.2
                if self.toonHasCondition(attackerId, 'encore2'):
                    damage *= 1.1
                if self.suitHasCondition(suitId, 'enraged') and not self.suitHasCondition(suitId, 'desperation'):
                    damage *= 0.7
                if self.suitHasCondition(suitId, 'brokenconnection'):
                    damage *= 1.3
                if self.suitHasCondition(suitId, 'vulnerablevideographer'):
                    damage *= (1.0 + (self.getSuitConditionModifier(suit.doId, 'vulnerablevideographer') * 0.01))
                if self.suitHasCondition(suitId, 'vulnerablebroadcaster'):
                    damage *= 2
                if self.suitHasCondition(suitId, 'vulnerablesilhouette1'):
                    damage *= 1.5
                if self.suitHasCondition(suitId, 'vulnerablesilhouette2'):
                    damage *= 2
                if self.suitHasCondition(suitId, 'vulnerablesilhouette3'):
                    damage *= 3
                if self.suitHasCondition(suitId, 'enraged') and self.suitHasCondition(suitId, 'desperation'):
                    damage *= 1
                if self.suitHasCondition(suitId, 'dancesession'):
                    damage *= 0.7
                if self.suitHasCondition(suitId, 'soakImmune') and self.suitHasCondition(suitId, 'soaked'):
                    damage *= 0.4
             #   for s in self.battle.activeSuits:
                   # if self.suitHasCondition(s.doId, 'shielding') and not self.suitHasCondition(suitId, 'shielding'):
                      #  damage *= .7
                       # self.absorbDamage += int((damage * .425))
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
            if atkTrack == SUE:
                suit = self.battle.findSuit(targetId)
                toon = self.battle.getToon(toonId)
                if not suit.getManager() and suit.currHP <= (suit.maxHP * 1.5) and not self.suitHasCondition(targetId, 'insured') and not self.suitHasCondition(targetId, 'extraAttack'):
                    self.setSuitCondition(targetId, 'sued', 1, 4, 'setBoth')
                    self.setToonCondition(toonId, 'noSOS', 1, 3, 'setBoth')
                    self.setToonCondition(toonId, 'noFires', 1, 3, 'setBoth')
                    self.setToonCondition(toonId, 'noUnites', 1, 3, 'setBoth')
                    self.setToonCondition(toonId, 'noSues', 1, 3, 'setBoth')
                    costToSue = math.ceil(suit.getActualLevel() / 4)
                    abilityToSue = toon.getCeaseAndDesists()
                    toon.removeCeaseAndDesists(costToSue)
                    if costToSue > abilityToSue:
                        commentStr = 'Toon attempting to sue a %s cost cog with %s C&Ds' % (costToSue, abilityToSue)
                        simbase.air.writeServerEvent('suspicious', toonId, commentStr)
                        dislId = toon.DISLid
                        simbase.air.banManager.ban(toonId, dislId, commentStr)
                        print
                        'Not enough Cease & Desists to sue cog - print a warning here'
            elif atkTrack == LURE:
                self.currentlyImmuneSuits = self.getImmuneSuits()
                if targetId not in self.currentlyImmuneSuits:
                    if self.getSuitTrapType(targetId) == NO_TRAP:
                        if self.notify.getDebug():
                            self.notify.debug('Suit lured, but no trap exists')
                        if self.SUITS_UNLURED_IMMEDIATELY:
                            if not self.__suitIsLured(targetId, prevRound=1):
                                if not self.__combatantDead(targetId, toon=toonTarget):
                                    validTargetAvail = 1
                                theSuit = self.battle.findSuit(targetId)
                                if theSuit.getVirtual() > 0:
                                    rounds = self.NumRoundsLured[atkLevel] - 2
                                elif theSuit.getSkeleton() > 0:
                                    rounds = self.NumRoundsLured[atkLevel] - 1
                                else:
                                    rounds = self.NumRoundsLured[atkLevel]
                                chance = ToontownBattleGlobals.LureMissChance[atkLevel]
                                lureKBValue = (ToontownBattleGlobals.AvLureKnockback[atkLevel] * 100)
                                if self.suitHasCondition(targetId, 'noKB'):
                                    lureKBValue *= 0
                                if self.suitHasCondition(targetId, 'immune'):
                                    lureKBValue *= 0
                                if self.suitHasCondition(targetId, 'lureImmune'):
                                    lureKBValue *= 0
                                if self.suitHasCondition(targetId, 'enraged') and self.suitHasCondition(targetId, 'desperation'):
                                    lureKBValue = 0
                                if random.randint(0, 99) <= chance and not self.suitHasCondition(targetId, 'lureImmune') and not self.suitHasCondition(targetId, 'enraged') and not self.suitHasCondition(targetId, 'immune') and not self.suitHasCondition(targetId, 'noKB'):
                                    lureKBValue = 0
                                organicBonus = self.__toonCheckGagBonus(attack[TOON_ID_COL], atkTrack, atkLevel)
                                theSuit = self.battle.findSuit(targetId)
                                self.setToonCondition(toonId, 'usedLure', 1, 3, 'setBoth')
                                if self.toonHasCondition(toonId, 'useLure'):
                                    self.setToonCondition(toonId, 'rushJobCompleted', 1, 3, 'setBoth')
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
                                    lureKBValue *= 1.2
                                if self.toonHasCondition(toonId, 'encore2'):
                                    lureKBValue *= 1.1
                                if theSuit.dna.name == 'fbd' and self.suitHasCondition(targetId, 'bookkeeping'):
                                    self.setToonCondition(toonId, 'bookkeepingtoon', 1, 5, 'setBoth')
                                if theSuit.dna.name == 'sgoat' and not self.suitHasCondition(targetId, 'enraged'):
                                    self.setSuitCondition(targetId, 'rageBuilding', self.getSuitConditionModifier(targetId, 'rageBuilding') + 15, 99, 'setBoth')
                                if theSuit.dna.name == 'phouse':
                                    self.setSuitCondition(targetId, 'powerhouseRotation', self.getSuitConditionModifier(targetId, 'powerhouseRotation') + 15, 99, 'setBoth')
                                if self.suitHasCondition(targetId, 'immune'):
                                    self.setSuitCondition(targetId, 'lured', 0,
                                                          0,
                                                          'setBoth')
                                if self.suitHasCondition(targetId, 'lureImmune'):
                                    self.setSuitCondition(targetId, 'lured', 0,
                                                          0,
                                                          'setBoth')
                                if self.suitHasCondition(targetId, 'enraged') and self.suitHasCondition(targetId, 'desperation'):
                                    self.setSuitCondition(targetId, 'lured', 0,
                                                          0,
                                                          'setBoth')
                                else:
                                    self.setSuitCondition(targetId, 'lured', lureKBValue, self.NumRoundsLured[atkLevel] + 2,
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
                            theSuit = self.battle.findSuit(targetId)
                           # for s in self.battle.activeSuits:
                               # if s.dna.name == 'sgoat' and self.suitHasCondition(s.doId, 'shielding'):
                                   # self.setSuitCondition(s.doId, 'rageBuilding', self.getSuitConditionModifier(s.doId, 'rageBuilding') + 10, 99, 'setBoth')
                                    #self.notify.debug('setSuitCondition() - scapegoat rage building %i' % (self.getSuitConditionModifier(s.doId, 'rageBuilding')))
                            for s in self.battle.activeSuits:
                                if self.suitHasCondition(s.doId, 'shielding') and not self.suitHasCondition(targetId, 'shielding'):
                                    attackDamage *= .7
                                    self.absorbDamage += math.ceil((attackDamage * .45))
                                    self.setSuitCondition(s.doId, 'rageBuilding', self.getSuitConditionModifier(s.doId, 'rageBuilding') + (attackDamage * .45) * .1, 99, 'setBoth')
                                    self.notify.debug('setSuitCondition() - scapegoat rage building %i' % (self.getSuitConditionModifier(s.doId, 'rageBuilding')))
                            if theSuit.dna.name == 'sgoat' and not self.suitHasCondition(targetId, 'enraged'):
                                self.setSuitCondition(targetId, 'rageBuilding',
                                                  self.getSuitConditionModifier(targetId, 'rageBuilding') + (
                                                          attackDamage * .1), 99, 'setBoth')
                            elif theSuit.dna.name == 'phouse':
                                self.setSuitCondition(targetId, 'powerhouseRotation',
                                                      self.getSuitConditionModifier(targetId, 'powerhouseRotation') + (
                                                                  attackDamage * .1), 99, 'setBoth')
                            elif self.suitHasCondition(targetId, 'immune'):
                                validTargetAvail = 0
                            elif self.suitHasCondition(targetId, 'lureImmune'):
                                validTargetAvail = 0
                            elif self.suitHasCondition(targetId, 'enraged') and self.suitHasCondition(targetId, 'desperation'):
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
                        elif self.suitHasCondition(targetId, 'contracted'):
                            attackDamage = 0
                        else:
                            costToFire = math.ceil(suit.getActualLevel() / 3)
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
                    self.setToonCondition(toon.doId, 'noSues', 1, 3, 'setBoth')
                    bonus = 0
                elif atkTrack == SUE:
                    suit = self.battle.findSuit(targetId)
                    attackDamage = 0
                    if suit:
                        if not suit.getManager() and suit.currHP > (suit.maxHP * 1.5) and not self.suitHasCondition(targetId, 'insured') and not self.suitHasCondition(targetId, 'contracted'):
                            costToSue = math.ceil(suit.getActualLevel() / 4)
                            abilityToSue = toon.getCeaseAndDesists()
                            toon.removeCeaseAndDesists(costToSue)
                            if costToSue > abilityToSue:
                                commentStr = 'Toon attempting to sue a %s cost cog with %s C&Ds' % (costToSue, abilityToSue)
                                simbase.air.writeServerEvent('suspicious', toonId, commentStr)
                                dislId = toon.DISLid
                                simbase.air.banManager.ban(toonId, dislId, commentStr)
                                print 'Not enough Cease & Desists to sue cog - print a warning here'
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
                    if self.toonHasCondition(toonId, 'allGagBoost'):
                        attackDamage *= (1.0 + (self.getToonConditionModifier(toonId, 'allGagBoost') * 0.01))
                    if self.toonHasCondition(toonId, 'raisedAnte'):
                        attackDamage *= (1.0 + (self.getToonConditionModifier(toonId, 'raisedAnte') * 0.01))
                    if self.toonHasCondition(toonId, 'encore'):
                        attackDamage *= 1.2
                    if self.toonHasCondition(toonId, 'encore2'):
                        attackDamage *= 1.1
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
                    if self.suitHasCondition(targetId, 'vulnerablevideographer'):
                        attackDamage *= (1.0 + (self.getSuitConditionModifier(suit.doId, 'vulnerablevideographer') * 0.01))
                    if self.toonHasCondition(toonId, 'allGagBoost'):
                        attackDamage *= (1.0 + (self.getToonConditionModifier(toonId, 'allGagBoost') * 0.01))
                    if self.toonHasCondition(toonId, 'raisedAnte'):
                        attackDamage *= (1.0 + (self.getToonConditionModifier(toonId, 'raisedAnte') * 0.01))
                    if self.suitHasCondition(targetId, 'immune'):
                        attackDamage = 0
                    if self.suitHasCondition(targetId, 'HRdamagereduction'):
                        attackDamage *= 0.1
                    if self.suitHasCondition(targetId, 'enraged') and not self.suitHasCondition(targetId, 'desperation'):
                        attackDamage *= 0.7
                    if self.suitHasCondition(targetId, 'vulnerable'):
                        attackDamage *= 1.3
                    if self.suitHasCondition(targetId, 'dancesession'):
                        attackDamage *= .7
                    if self.suitHasCondition(targetId, 'vulnerablebroadcaster'):
                        attackDamage *= 2
                    if self.suitHasCondition(targetId, 'vulnerablesilhouette1'):
                        attackDamage *= 1.5
                    if self.suitHasCondition(targetId, 'vulnerablesilhouette2'):
                        attackDamage *= 2
                    if self.suitHasCondition(targetId, 'vulnerablesilhouette3'):
                        attackDamage *= 3
                    if self.suitHasCondition(targetId, 'marked'):
                        attackDamage *= 1.1
                    if self.suitHasCondition(targetId, 'enraged') and self.suitHasCondition(targetId, 'desperation'):
                        attackDamage *= 1
                    if self.suitHasCondition(targetId, 'soakImmune') and self.suitHasCondition(targetId, 'soaked'):
                        attackDamage *= 0.4
                    if self.toonHasCondition(toonId, 'groupDamageDown'):
                        attackDamage *= 0.5
                    if self.toonHasCondition(toonId, 'noDamage'):
                        attackDamage *= 0
                    for s in self.battle.activeSuits:
                        if self.suitHasCondition(s.doId, 'shielding') and not self.suitHasCondition(targetId, 'shielding'):
                            attackDamage *= .7
                            self.absorbDamage += math.ceil(attackDamage * .45)
                            self.setSuitCondition(s.doId, 'rageBuilding',
                                                  self.getSuitConditionModifier(s.doId, 'rageBuilding') + (
                                                              attackDamage * .45) * .1, 99, 'setBoth')
                            self.notify.debug('setSuitCondition() - scapegoat rage building %i' % (
                                self.getSuitConditionModifier(s.doId, 'rageBuilding')))
                    suit = self.battle.findSuit(targetId)
                    target = self.battle.findSuit(attack[TOON_TGT_COL])
                    activeSuits = self.battle.activeSuits
                    suitIndex = activeSuits.index(target)
                    if suitIndex - 1 >= 0 and attackDamage > 0:
                        target2 = activeSuits[suitIndex - 1]
                        if not self.suitHasCondition(target2.doId, 'immune'):
                            if target2.dna.name == 'sgoat' and not self.suitHasCondition(targetId, 'enraged'):
                                self.setSuitCondition(target2.doId, 'rageBuilding',
                                                      self.getSuitConditionModifier(target2.doId, 'rageBuilding') + ((attackDamage * .1) + 15), 99, 'setBoth')
                            if target2.dna.name == 'lgator' and not self.suitHasCondition(target2.doId, 'soaked'):
                                self.setSuitCondition(target2.doId, 'soakedcalculator', 1, 10, 'setBoth')
                                self.setSuitCondition(target2.doId, 'soakedcalculator2', 0, 0, 'setBoth')
                            if target2.dna.name == 'bkeeper' and self.suitHasCondition(target2.doId, 'bookkeeping'):
                                self.setToonCondition(toon.doId, 'bookkeepingtoon', 1, 5, 'setBoth')
                                self.setSuitCondition(target2.doId, 'soakedcalculator', 1, 10, 'setBoth')
                                self.setSuitCondition(target2.doId, 'soakedcalculator2', 0, 0, 'setBoth')
                            if target2.dna.name == 'bkeeper':
                                self.setSuitCondition(target2.doId, 'soakedcalculator', 1, 10, 'setBoth')
                                self.setSuitCondition(target2.doId, 'soakedcalculator2', 0, 0, 'setBoth')
                            if target2.dna.name == 'phouse':
                                self.setSuitCondition(target2.doId, 'soakedcalculator', 1, 10, 'setBoth')
                                self.setSuitCondition(target2.doId, 'soakedcalculator2', 0, 0, 'setBoth')
                            if target2.dna.name == 'radiog':
                                self.setSuitCondition(target2.doId, 'soakedcalculator', 1, 10, 'setBoth')
                                self.setSuitCondition(target2.doId, 'soakedcalculator2', 0, 0, 'setBoth')
                            if target2.dna.name == 'wsi':
                                self.setSuitCondition(target2.doId, 'soakedcalculator', 1, 10, 'setBoth')
                                self.setSuitCondition(target2.doId, 'soakedcalculator2', 0, 0, 'setBoth')
                            self.setSuitCondition(target2.doId, 'soaked', 1, self.NumRoundsSoaked[attackLevel],
                                                      'alternateBoth')
                            if self.suitHasCondition(target2.doId, 'sued'):
                                self.setSuitCondition(target2.doId, 'sued', 1, 4, 'alternateBoth')
                            organicBonus = self.__toonCheckGagBonus(attack[TOON_ID_COL], atkTrack, atkLevel)
                            if organicBonus:
                                target2.setHP(target2.currHP - math.ceil(attackDamage / 1.33))
                                attackDamageAbsorb = (math.ceil(attackDamage / 1.33) * .45)
                                attackDamageAbsorbHR = (math.ceil(attackDamage / 1.33) * .115)
                            else:
                                target2.setHP(target2.currHP - math.ceil(attackDamage / 3))
                                attackDamageAbsorb = (math.ceil(attackDamage / 3) * .45)
                                attackDamageAbsorbHR = (math.ceil(attackDamage / 3) * .115)
                            if target2.dna.name == 'phouse':
                                if organicBonus:
                                    self.setSuitCondition(target2.doId, 'powerhouseRotation', self.getSuitConditionModifier(target2.doId, 'powerhouseRotation') + (((attackDamage / 1.33) * .1) + 15), 99, 'setBoth')
                                else:
                                    self.setSuitCondition(target2.doId, 'powerhouseRotation',
                                                          self.getSuitConditionModifier(target2.doId,
                                                                                        'powerhouseRotation') + (
                                                                      ((attackDamage / 1.33) * .1) + 15), 99, 'setBoth')
                            for s in self.battle.activeSuits:
                                if self.suitHasCondition(s.doId, 'shielding') and not self.suitHasCondition(target2.doId, 'shielding'):
                                    self.absorbDamage += math.ceil(attackDamageAbsorb)
                                    self.setSuitCondition(s.doId, 'rageBuilding',
                                                          self.getSuitConditionModifier(s.doId, 'rageBuilding') + (
                                                                      attackDamageAbsorb) * .1, 99, 'setBoth')
                                    self.notify.debug('setSuitCondition() - scapegoat rage building %i' % (
                                        self.getSuitConditionModifier(s.doId, 'rageBuilding')))
                            if target2.getHP() <= 0:
                                self.__removeLured(target2.doId)
                                if target2.getSkeleRevives() >= 1:
                                    target2.useSkeleRevive()
                    if suitIndex + 1 < len(activeSuits) and attackDamage > 0:
                        target3 = activeSuits[suitIndex + 1]
                        if not self.suitHasCondition(target3.doId, 'immune'):
                            if target3.dna.name == 'sgoat' and not self.suitHasCondition(targetId, 'enraged'):
                                self.setSuitCondition(target3.doId, 'rageBuilding',
                                                      self.getSuitConditionModifier(target3.doId, 'rageBuilding') + ((
                                                                  attackDamage * .1) + 15), 99, 'setBoth')
                            if target3.dna.name == 'lgator' and not self.suitHasCondition(target3.doId, 'soaked'):
                                self.setSuitCondition(target3.doId, 'soakedcalculator', 1, 10, 'setBoth')
                                self.setSuitCondition(target3.doId, 'soakedcalculator2', 0, 0, 'setBoth')
                            if target3.dna.name == 'bkeeper' and self.suitHasCondition(target3.doId, 'bookkeeping'):
                                self.setToonCondition(toon.doId, 'bookkeepingtoon', 1, 5, 'setBoth')
                                self.setSuitCondition(target3.doId, 'soakedcalculator', 1, 10, 'setBoth')
                                self.setSuitCondition(target3.doId, 'soakedcalculator2', 0, 0, 'setBoth')
                            if target3.dna.name == 'bkeeper':
                                self.setSuitCondition(target3.doId, 'soakedcalculator', 1, 10, 'setBoth')
                                self.setSuitCondition(target3.doId, 'soakedcalculator2', 0, 0, 'setBoth')
                            if target3.dna.name == 'phouse':
                                self.setSuitCondition(target3.doId, 'soakedcalculator', 1, 10, 'setBoth')
                                self.setSuitCondition(target3.doId, 'soakedcalculator2', 0, 0, 'setBoth')
                            if target3.dna.name == 'radiog':
                                self.setSuitCondition(target3.doId, 'soakedcalculator', 1, 10, 'setBoth')
                                self.setSuitCondition(target3.doId, 'soakedcalculator2', 0, 0, 'setBoth')
                            if target3.dna.name == 'wsi':
                                self.setSuitCondition(target3.doId, 'soakedcalculator', 1, 10, 'setBoth')
                                self.setSuitCondition(target3.doId, 'soakedcalculator2', 0, 0, 'setBoth')
                            self.setSuitCondition(target3.doId, 'soaked', 1, self.NumRoundsSoaked[attackLevel],
                                                      'alternateBoth')
                            if self.suitHasCondition(target3.doId, 'sued'):
                                self.setSuitCondition(target3.doId, 'sued', 1, 4, 'alternateBoth')
                            organicBonus = self.__toonCheckGagBonus(attack[TOON_ID_COL], atkTrack, atkLevel)
                            if organicBonus:
                                target3.setHP(target3.currHP - math.ceil(attackDamage / 1.33))
                                attackDamageAbsorb = (math.ceil(attackDamage / 1.33) * .45)
                                attackDamageAbsorbHR = (math.ceil(attackDamage / 1.33) * .115)
                            else:
                                target3.setHP(target3.currHP - math.ceil(attackDamage / 3))
                                attackDamageAbsorb = (math.ceil(attackDamage / 3) * .45)
                                attackDamageAbsorbHR = (math.ceil(attackDamage / 3) * .115)
                            if target3.dna.name == 'phouse':
                                if organicBonus:
                                    self.setSuitCondition(target3.doId, 'powerhouseRotation', self.getSuitConditionModifier(target3.doId, 'powerhouseRotation') + (((attackDamage / 1.33) * .1) + 15), 99, 'setBoth')
                                else:
                                    self.setSuitCondition(target3.doId, 'powerhouseRotation',
                                                          self.getSuitConditionModifier(target3.doId,
                                                                                        'powerhouseRotation') + (
                                                                      ((attackDamage / 1.33) * .1) + 15), 99, 'setBoth')
                            for s in self.battle.activeSuits:
                                if self.suitHasCondition(s.doId, 'shielding') and not self.suitHasCondition(target3.doId, 'shielding'):
                                    self.absorbDamage += math.ceil(attackDamageAbsorb)
                                    self.setSuitCondition(s.doId, 'rageBuilding',
                                                          self.getSuitConditionModifier(s.doId, 'rageBuilding') + (
                                                                      attackDamageAbsorb) * .1, 99, 'setBoth')
                                    self.notify.debug('setSuitCondition() - scapegoat rage building %i' % (
                                        self.getSuitConditionModifier(s.doId, 'rageBuilding')))
                            if target3.getHP() <= 0:
                                self.__removeLured(target3.doId)
                                if target3.getSkeleRevives() >= 1:
                                    target3.useSkeleRevive()
                    if attackDamage > 0:
                        if suit.dna.name == 'sgoat' and not self.suitHasCondition(targetId, 'enraged'):
                            self.setSuitCondition(targetId, 'rageBuilding', self.getSuitConditionModifier(targetId, 'rageBuilding') + ((attackDamage * .1) + 15), 99, 'setBoth')
                        if suit.dna.name == 'phouse':
                            self.setSuitCondition(targetId, 'powerhouseRotation', self.getSuitConditionModifier(targetId, 'powerhouseRotation') + ((attackDamage * .1) + 15), 99, 'setBoth')
                        if suit.dna.name == 'lgator' and not self.suitHasCondition(target.doId, 'soaked'):
                            self.setSuitCondition(targetId, 'soakedcalculator', 1, 10, 'setBoth')
                            self.setSuitCondition(targetId, 'soakedcalculator2', 0, 0, 'setBoth')
                        if suit.dna.name == 'bkeeper' and self.suitHasCondition(targetId, 'bookkeeping'):
                            self.setToonCondition(toon.doId, 'bookkeepingtoon', 1, 5, 'setBoth')
                            self.setSuitCondition(targetId, 'soakedcalculator', 1, 10, 'setBoth')
                            self.setSuitCondition(targetId, 'soakedcalculator2', 0, 0, 'setBoth')
                        if suit.dna.name == 'bkeeper':
                            self.setSuitCondition(targetId, 'soakedcalculator', 1, 10, 'setBoth')
                            self.setSuitCondition(targetId, 'soakedcalculator2', 0, 0, 'setBoth')
                        if suit.dna.name == 'phouse':
                            self.setSuitCondition(targetId, 'soakedcalculator', 1, 10, 'setBoth')
                            self.setSuitCondition(targetId, 'soakedcalculator2', 0, 0, 'setBoth')
                        if suit.dna.name == 'radiog':
                            self.setSuitCondition(targetId, 'soakedcalculator', 1, 10, 'setBoth')
                            self.setSuitCondition(targetId, 'soakedcalculator2', 0, 0, 'setBoth')
                        if suit.dna.name == 'wsi':
                            self.setSuitCondition(targetId, 'soakedcalculator', 1, 10, 'setBoth')
                            self.setSuitCondition(targetId, 'soakedcalculator2', 0, 0, 'setBoth')
                        self.setSuitCondition(targetId, 'soaked', 1, self.NumRoundsSoaked[attackLevel],
                                                  'alternateBoth')
                        self.setToonCondition(toon.doId, 'soakToon', 1, 5, 'setBoth')
                        if self.suitHasCondition(targetId, 'sued'):
                            self.setSuitCondition(targetId, 'sued', 1, 4, 'alternateBoth')
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
                    self.setToonCondition(toon.doId, 'markToon', 1, 5, 'setBoth')
                    suit = self.battle.findSuit(targetId)
                    attackDamage = getAvPropDamage(attackTrack, attackLevel, toon.experience.getExp(attackTrack))
                    if self.toonHasCondition(toonId, 'throwBoost'):
                        attackDamage *= (1.0 + self.getToonConditionModifier(toonId, 'throwBoost') * 0.01)
                    if self.suitHasCondition(targetId, 'vulnerablevideographer'):
                        attackDamage *= (1.0 + (self.getSuitConditionModifier(suit.doId, 'vulnerablevideographer') * 0.01))
                    if self.toonHasCondition(toonId, 'allGagBoost'):
                        attackDamage *= (1.0 + (self.getToonConditionModifier(toonId, 'allGagBoost') * 0.01))
                    if self.toonHasCondition(toonId, 'raisedAnte'):
                        attackDamage *= (1.0 + (self.getToonConditionModifier(toonId, 'raisedAnte') * 0.01))
                    if attackDamage > 0:
                        self.setSuitCondition(targetId, 'marked', 1, 1, 'setBoth')
                        if self.suitHasCondition(targetId, 'sued'):
                            self.setSuitCondition(targetId, 'sued', 1, 4, 'alternateBoth')
                        if suit.dna.name == 'bkeeper' and self.suitHasCondition(targetId, 'bookkeeping'):
                            self.setToonCondition(toon.doId, 'bookkeepingtoon', 1, 5, 'setBoth')
                            self.setSuitCondition(targetId, 'markedcalculator', 1, 10, 'setBoth')
                            self.setSuitCondition(targetId, 'markedcalculator2', 0, 0, 'setBoth')
                        if suit.dna.name == 'bkeeper':
                            self.setSuitCondition(targetId, 'markedcalculator', 1, 10, 'setBoth')
                            self.setSuitCondition(targetId, 'markedcalculator2', 0, 0, 'setBoth')
                        if suit.dna.name == 'ubuster':
                            self.setSuitCondition(targetId, 'markedcalculator', 1, 10, 'setBoth')
                            self.setSuitCondition(targetId, 'markedcalculator2', 0, 0, 'setBoth')
                        if suit.dna.name == 'sgoat' and not self.suitHasCondition(targetId, 'enraged'):
                            self.setSuitCondition(targetId, 'rageBuilding', self.getSuitConditionModifier(targetId, 'rageBuilding') + (attackDamage * .1), 99, 'setBoth')
                        if suit.dna.name == 'phouse':
                            self.setSuitCondition(targetId, 'powerhouseRotation', self.getSuitConditionModifier(targetId, 'powerhouseRotation') + (attackDamage * .1), 99, 'setBoth')
                    target = self.battle.findSuit(attack[TOON_TGT_COL])
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
                    self.__removeLured(suit.doId)
                    if self.suitHasCondition(suit.doId, 'lured'):
                        self.setSuitCondition(suit.doId, 'lured', 0, 0, 'setBoth')
                    if self.suitHasCondition(targetId, 'sued'):
                        self.setSuitCondition(targetId, 'sued', 1, 4, 'alternateBoth')
                    if self.toonHasCondition(toonId, 'soundBoost'):
                        attackDamage *= (1.0 + self.getToonConditionModifier(toonId, 'soundBoost') * 0.01)
                    if self.suitHasCondition(targetId, 'vulnerablevideographer'):
                        attackDamage *= (1.0 + (self.getSuitConditionModifier(suit.doId, 'vulnerablevideographer') * 0.01))
                    if self.toonHasCondition(toonId, 'allGagBoost'):
                        attackDamage *= (1.0 + (self.getToonConditionModifier(toonId, 'allGagBoost') * 0.01))
                    if self.toonHasCondition(toonId, 'raisedAnte'):
                        attackDamage *= (1.0 + (self.getToonConditionModifier(toonId, 'raisedAnte') * 0.01))
                    if suit.dna.name == 'bkeeper' and self.suitHasCondition(targetId, 'bookkeeping'):
                        self.setToonCondition(toon.doId, 'bookkeepingtoon', 1, 5, 'setBoth')
                    if suit.dna.name == 'sgoat' and not self.suitHasCondition(targetId, 'enraged'):
                        self.setSuitCondition(targetId, 'rageBuilding', self.getSuitConditionModifier(targetId, 'rageBuilding') + (attackDamage * .1), 99, 'setBoth')
                    if suit.dna.name == 'phouse':
                        self.setSuitCondition(targetId, 'powerhouseRotation', self.getSuitConditionModifier(targetId, 'powerhouseRotation') + (attackDamage * .1), 99, 'setBoth')
                    organicBonus = self.__toonCheckGagBonus(attack[TOON_ID_COL], atkTrack, atkLevel)
                    if self.getToonConditionTurns(toonId, 'encore') == 1:
                        self.setToonCondition(toon.doId, 'winded', -50, 3, 'setBoth')
                    elif self.getToonConditionTurns(toonId, 'encore2') == 1:
                        self.setToonCondition(toon.doId, 'winded', -50, 3, 'setBoth')
                    elif not self.toonHasCondition(toon.doId, 'encore') and not self.toonHasCondition(toonId, 'winded') and organicBonus:
                        self.setToonCondition(toon.doId, 'encore', 20, 2, 'setBoth')
                    elif not self.toonHasCondition(toon.doId, 'encore2') and not self.toonHasCondition(toonId, 'winded') and not organicBonus:
                        self.setToonCondition(toon.doId, 'encore2', 10, 2, 'setBoth')
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
                    suit = self.battle.findSuit(targetId)
                    chance = ToontownBattleGlobals.DropMissChance[atkLevel]
                    if self.toonHasCondition(toonId, 'dropBoost'):
                        attackDamage *= (1.0 + self.getToonConditionModifier(toonId, 'dropBoost') * 0.01)
                    if self.suitHasCondition(targetId, 'vulnerablevideographer'):
                        attackDamage *= (1.0 + (self.getSuitConditionModifier(suit.doId, 'vulnerablevideographer') * 0.01))
                    if self.toonHasCondition(toonId, 'allGagBoost'):
                        attackDamage *= (1.0 + (self.getToonConditionModifier(toonId, 'allGagBoost') * 0.01))
                    if self.toonHasCondition(toonId, 'raisedAnte'):
                        attackDamage *= (1.0 + (self.getToonConditionModifier(toonId, 'raisedAnte') * 0.01))
                    if self.suitHasCondition(targetId, 'dazed') and self.suitHasCondition(targetId, 'soaked') and self.suitHasCondition(targetId, 'marked'):
                        if organicBonus:
                            attackDamage *= 1.2
                    if self.suitHasCondition(targetId, 'dazed') and self.suitHasCondition(targetId, 'soaked') and not self.suitHasCondition(targetId, 'marked'):
                        if organicBonus:
                            attackDamage *= 1.15
                    if self.suitHasCondition(targetId, 'soaked') and self.suitHasCondition(targetId, 'marked') and not self.suitHasCondition(targetId, 'dazed'):
                        if organicBonus:
                            attackDamage *= 1.15
                    if self.suitHasCondition(targetId, 'dazed') and self.suitHasCondition(targetId, 'marked') and not self.suitHasCondition(targetId, 'soaked'):
                        if organicBonus:
                            attackDamage *= 1.15
                    if self.suitHasCondition(targetId, 'soaked') and not self.suitHasCondition(targetId, 'dazed') and not self.suitHasCondition(targetId, 'marked'):
                        if organicBonus:
                            attackDamage *= 1.1
                    if self.suitHasCondition(targetId, 'dazed') and not self.suitHasCondition(targetId, 'soaked') and not self.suitHasCondition(targetId, 'marked'):
                        if organicBonus:
                            attackDamage *= 1.1
                    if self.suitHasCondition(targetId, 'marked') and not self.suitHasCondition(targetId, 'dazed') and not self.suitHasCondition(targetId, 'soaked'):
                        if organicBonus:
                            attackDamage *= 1.1
                    if self.suitHasCondition(targetId, 'soaked'):
                        chance -= 15
                    if self.suitHasCondition(targetId, 'dazed'):
                        chance -= 15
                    if self.toonHasCondition(toonId, 'cheer'):
                        chance -= 5
                    if self.suitHasCondition(targetId, 'marked'):
                        chance -= 10
                    if suit.getHP() <= 0:
                        chance -= 40
                    if random.randint(0, 99) <= chance:
                        self.notify.debug(
                                'Toon attack rolled' + str(chance))
                        attackDamage = 0
                    elif random.randint(0, 99) >= chance:
                        self.notify.debug(
                                'Toon attack rolled' + str(chance))
                        attackDamage *= 1
                    if suit.dna.name == 'bkeeper' and self.suitHasCondition(targetId, 'bookkeeping'):
                        self.setToonCondition(toon.doId, 'bookkeepingtoon', 1, 5, 'setBoth')
                    if suit.dna.name == 'sgoat' and not self.suitHasCondition(targetId, 'enraged'):
                        self.setSuitCondition(targetId, 'rageBuilding', self.getSuitConditionModifier(targetId, 'rageBuilding') + (attackDamage * .1), 99, 'setBoth')
                    if suit.dna.name == 'phouse':
                        self.setSuitCondition(targetId, 'powerhouseRotation', self.getSuitConditionModifier(targetId, 'powerhouseRotation') + (attackDamage * .1), 99, 'setBoth')
                    target = self.battle.findSuit(attack[TOON_TGT_COL])
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
                    attackDamage = getAvPropDamage(attackTrack, attackLevel, toon.experience.getExp(attackTrack))
                    if self.suitHasCondition(targetId, 'sued'):
                        self.setSuitCondition(targetId, 'sued', 1, 4, 'alternateBoth')
                    if self.suitHasCondition(targetId, 'soaked'):
                        attackDamage *= 1
                    if not self.suitHasCondition(targetId, 'soaked'):
                        attackDamage *= 0
                    if self.suitHasCondition(targetId, 'zapImmune'):
                        attackDamage *= 0
                    if self.suitHasCondition(targetId, 'immune'):
                        attackDamage *= 0
                    if self.toonHasCondition(toonId, 'zapBoost'):
                        attackDamage *= (1.0 + self.getToonConditionModifier(toonId, 'zapBoost') * 0.01)
                    if self.suitHasCondition(targetId, 'vulnerablevideographer'):
                        attackDamage *= (1.0 + (self.getSuitConditionModifier(targetId, 'vulnerablevideographer') * 0.01))
                    if self.toonHasCondition(toonId, 'allGagBoost'):
                        attackDamage *= (1.0 + (self.getToonConditionModifier(toonId, 'allGagBoost') * 0.01))
                    if self.toonHasCondition(toonId, 'raisedAnte'):
                        attackDamage *= (1.0 + (self.getToonConditionModifier(toonId, 'raisedAnte') * 0.01))
                    suit = self.battle.findSuit(targetId)
                    if suit.dna.name == 'bkeeper' and self.suitHasCondition(targetId, 'bookkeeping'):
                        self.setToonCondition(toon.doId, 'bookkeepingtoon', 1, 5, 'setBoth')
                    if suit.dna.name == 'phouse':
                        self.setSuitCondition(targetId, 'powerhouseRotation', self.getSuitConditionModifier(targetId, 'powerhouseRotation') + (attackDamage * .1), 99, 'setBoth')
                    if suit.dna.name == 'sgoat' and not self.suitHasCondition(targetId, 'enraged'):
                        self.setSuitCondition(targetId, 'rageBuilding', self.getSuitConditionModifier(targetId, 'rageBuilding') + (attackDamage * .1), 99, 'setBoth')
                    activeSuits = self.battle.activeSuits
                    target = self.battle.findSuit(targetId)
                    suitIndex = activeSuits.index(target)
                    organicBonus = self.__toonCheckGagBonus(attack[TOON_ID_COL], atkTrack, atkLevel)
                    if organicBonus:
                        attackDamage *= 1.1
                    if attackDamage > 0:
                        self.setSuitCondition(target.doId, 'soaked', 1, 1, 'setBoth')
                        self.setSuitCondition(target.doId, 'zapped', 1, 1, 'setBoth')
                        self.__removeLured(target.doId)
                        if self.suitHasCondition(target.doId, 'lured'):
                            self.setSuitCondition(target.doId, 'lured', 0, 0, 'setBoth')
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
                suit = self.battle.findSuit(targetId)
                if atkTrack is not SQUIRT:
                    if self.suitHasCondition(targetId, 'immune'):
                        attackDamage = 0
                    if self.suitHasCondition(targetId, 'HRdamagereduction'):
                        attackDamage *= 0.1
                    if self.suitHasCondition(targetId, 'enraged') and not self.suitHasCondition(targetId, 'desperation'):
                        attackDamage *= 0.7
                    if self.suitHasCondition(targetId, 'vulnerable'):
                        attackDamage *= 1.3
                    if self.suitHasCondition(targetId, 'dancesession'):
                        attackDamage *= .7
                    if self.suitHasCondition(targetId, 'vulnerablebroadcaster'):
                        attackDamage *= 2
                    if self.suitHasCondition(targetId, 'vulnerablesilhouette1'):
                        attackDamage *= 1.5
                    if self.suitHasCondition(targetId, 'vulnerablesilhouette2'):
                        attackDamage *= 2
                    if self.suitHasCondition(targetId, 'vulnerablesilhouette3'):
                        attackDamage *= 3
                    if self.suitHasCondition(targetId, 'marked') and atkTrack is not THROW:
                        attackDamage *= 1.1
                    if self.suitHasCondition(targetId, 'enraged') and self.suitHasCondition(targetId, 'desperation'):
                        attackDamage *= 1
                   # if self.suitHasCondition(targetId, 'enraged') and not self.suitHasCondition(targetId, 'desperation') and atkTrack is not ZAP and atkTrack is not SQUIRT:
                        #attackDamage *= 0.7
                    if self.suitHasCondition(targetId, 'soakImmune') and self.suitHasCondition(targetId, 'soaked'):
                        attackDamage *= 0.4
                 #   if self.suitHasCondition(targetId, 'vulnerable') and atkTrack is not ZAP and atkTrack is not SQUIRT:
                      #  attackDamage *= 1.25
                    if self.toonHasCondition(toonId, 'encore') and atkTrack is not SOUND:
                        attackDamage *= 1.2
                    if self.toonHasCondition(toonId, 'encore2') and atkTrack is not SOUND:
                        attackDamage *= 1.1
                    if self.toonHasCondition(toonId, 'groupDamageDown') and atkTrack == ZAP:
                        attackDamage *= 0.5
                    if self.toonHasCondition(toonId, 'groupDamageDown') and atkTrack == SOUND:
                        attackDamage *= 0.5
                    if self.toonHasCondition(toonId, 'groupDamageDown') and atkTrack == SQUIRT:
                        attackDamage *= 0.5
                    if self.toonHasCondition(toonId, 'groupDamageDown') and atkTrack == HEAL and atkLevel == 7:
                        attackDamage *= 0.5
                    if self.toonHasCondition(toonId, 'groupDamageDown') and atkTrack == HEAL and atkLevel == 5:
                        attackDamage *= 0.5
                    if self.toonHasCondition(toonId, 'groupDamageDown') and atkTrack == HEAL and atkLevel == 3:
                        attackDamage *= 0.5
                    if self.toonHasCondition(toonId, 'groupDamageDown') and atkTrack == HEAL and atkLevel == 1:
                        attackDamage *= 0.5
                    if self.getToonConditionTurns(toonId, 'encore') == 1 and atkTrack == SOUND:
                        attackDamage *= 1.2
                    if self.getToonConditionTurns(toonId, 'encore2') == 1 and atkTrack == SOUND:
                        attackDamage *= 1.1
                    if self.toonHasCondition(toonId, 'winded') and not self.getToonConditionTurns(toonId, 'encore') == 1 and not self.getToonConditionTurns(toonId, 'encore2') == 1 and atkTrack == SOUND:
                        attackDamage *= 0.5
                    if self.toonHasCondition(toonId, 'noDamage'):
                        attackDamage *= 0
                    for s in self.battle.activeSuits:
                        if self.suitHasCondition(s.doId, 'shielding') and not self.suitHasCondition(targetId, 'shielding') and not atkTrack == TRAP and not atkTrack == SQUIRT:
                            attackDamage *= .7
                            self.absorbDamage += math.ceil(attackDamage * .45)
                            self.setSuitCondition(s.doId, 'rageBuilding',
                                                  self.getSuitConditionModifier(s.doId, 'rageBuilding') + (
                                                              attackDamage * .45) * .1, 99, 'setBoth')
                            self.notify.debug('setSuitCondition() - scapegoat rage building %i' % (
                                self.getSuitConditionModifier(s.doId, 'rageBuilding')))
                attackDamage = math.ceil(attackDamage)
                if atkTrack == TRAP:
                    for suit in self.battle.activeSuits:
                        if suit.dna.name == 'hrollers' and suit.getActualLevel() == 29:
                            self.setSuitCondition(suit.doId, 'barcalculator', 1, 1, 'setBoth')
                if self.toonHasCondition(toonId, 'useDrop') and atkTrack == DROP:
                    self.setToonCondition(toonId, 'rushJobCompleted', 1, 3, 'setBoth')
                if self.toonHasCondition(toonId, 'useToonUp') and atkTrack == HEAL:
                    self.setToonCondition(toonId, 'rushJobCompleted', 1, 3, 'setBoth')
                if self.toonHasCondition(toonId, 'useTrap') and atkTrack == TRAP:
                    self.setToonCondition(toonId, 'rushJobCompleted', 1, 3, 'setBoth')
                if self.toonHasCondition(toonId, 'useLure') and atkTrack == LURE:
                    self.setToonCondition(toonId, 'rushJobCompleted', 1, 3, 'setBoth')
                if self.toonHasCondition(toonId, 'useThrow') and atkTrack == THROW:
                    self.setToonCondition(toonId, 'rushJobCompleted', 1, 3, 'setBoth')
                if self.toonHasCondition(toonId, 'useSquirt') and atkTrack == SQUIRT:
                    self.setToonCondition(toonId, 'rushJobCompleted', 1, 3, 'setBoth')
                if self.toonHasCondition(toonId, 'useZap') and atkTrack == ZAP:
                    self.setToonCondition(toonId, 'rushJobCompleted', 1, 3, 'setBoth')
                if self.toonHasCondition(toonId, 'useSound') and atkTrack == SOUND:
                    self.setToonCondition(toonId, 'rushJobCompleted', 1, 3, 'setBoth')
                if atkTrack == DROP:
                    self.setToonCondition(toonId, 'usedDrop', 1, 3, 'setBoth')
                if atkTrack == HEAL:
                    self.setToonCondition(toonId, 'usedHeal', 1, 3, 'setBoth')
                if atkTrack == TRAP:
                    self.setToonCondition(toonId, 'usedTrap', 1, 3, 'setBoth')
                if atkTrack == LURE:
                    self.setToonCondition(toonId, 'usedLure', 1, 3, 'setBoth')
                if atkTrack == THROW:
                    self.setToonCondition(toonId, 'usedThrow', 1, 3, 'setBoth')
                if atkTrack == SQUIRT:
                    self.setToonCondition(toonId, 'usedSquirt', 1, 3, 'setBoth')
                if atkTrack == ZAP:
                    self.setToonCondition(toonId, 'usedZap', 1, 3, 'setBoth')
                if atkTrack == SOUND:
                    self.setToonCondition(toonId, 'usedSound', 1, 3, 'setBoth')
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
                        toon.toonUp(math.ceil((attackDamage / 2.22) / len(targetList)))
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
                          #  if suit.dna.name == 'tcm':
                             #   self.setSuitCondition(targetId, 'trapcalculator', 1, 10, 'setBoth')
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
                       # if self.getSuitConditionModifier(currTarget.doId, 'lured') > 0:
                           # if self.suitHasCondition(currTarget.doId, 'lured'):
                               # self.setSuitCondition(currTarget.doId, 'lured', 0, 0, 'setBoth')
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
                if not self.suitHasCondition(suit.doId, 'dead'):
                    self.setSuitCondition(suit.doId, 'dead', 1, 2, 'setBoth')
                    self.deadSuits += 1
                    theSuit = None
                    currentBossHealth = -1
                    for s in self.battle.suits:
                        if s.dna.name == 'hroller':
                            theSuit = s
                            currentBossHealth = theSuit.currHP
                            if currentBossHealth >= 1:
                                if not self.suitHasCondition(suit.doId, 'killedbyroller'):
                                    if suit.getExecutive():
                                        self.levelDamage += (suit.getActualLevel() * 7)
                                    elif suit.getGovernaught():
                                        self.levelDamage += (suit.getActualLevel() * 7)
                                    else:
                                        self.levelDamage += (suit.getActualLevel() * 4)
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
                        if self.suitHasCondition(suit, 'lureImmune'):
                            lureKBValue = 0
                            self.setSuitCondition(suit, 'lured', 0, 0, 'none')
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
                unlureAttack = self.__unlureAtk(toonId, toon=1)
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
        if toon and (track == THROW or track == SQUIRT or track == SOUND):
            if self.notify.getDebug():
                self.notify.debug('attack is an unlure')
            return 1
        return 0

    def __calcSuitAtkType(self, theSuit):
        attacks = SuitBattleGlobals.SuitAttributes[theSuit.dna.name]['attacks']
        atk = SuitBattleGlobals.pickSuitAttack(attacks, theSuit.getLevel())
        if theSuit.dna.name == 'lgator':
            currentBossHealth = -1
            for s in self.battle.suits:
                if s.dna.name == 'stenog' or s.dna.name == 'sgoat' or s.dna.name == 'caseman':
                    currentBossHealth = s.currHP
            currentBossHealth3 = -1
            for s in self.battle.suits:
                if s.dna.name == 'caseman':
                    currentBossHealth3 = s.currHP
            if currentBossHealth3 == -1:
                self.setSuitCondition(theSuit.doId, 'deadcase', 1, 100, 'setBoth')
        if theSuit.dna.name == 'stenog':
            currentBossHealth = -1
            for s in self.battle.suits:
                if s.dna.name == 'lgator' or s.dna.name == 'sgoat' or s.dna.name == 'caseman':
                    currentBossHealth = s.currHP
        if theSuit.dna.name == 'caseman':
            currentBossHealth = -1
            for s in self.battle.suits:
                if s.dna.name == 'stenog' or s.dna.name == 'sgoat' or s.dna.name == 'lgator':
                    currentBossHealth = s.currHP
        if theSuit.dna.name == 'sgoat':
            currentBossHealth = -1
            for s in self.battle.suits:
                if s.dna.name == 'stenog' or s.dna.name == 'lgator' or s.dna.name == 'caseman':
                    currentBossHealth = s.currHP
        if theSuit.dna.name == 'phouse':
            x = self.TurnsElapsed
            currentBossHealth = -1
            for s in self.battle.suits:
                if s.dna.name == 'wtapper' or s.dna.name == 'bkeeper' or s.dna.name == 'ambass':
                    currentBossHealth = s.currHP
        if theSuit.dna.name == 'bkeeper':
            x = self.TurnsElapsed
            currentBossHealth = -1
            for s in self.battle.suits:
                if s.dna.name == 'wtapper' or s.dna.name == 'phouse' or s.dna.name == 'ambass':
                    currentBossHealth = s.currHP
        if theSuit.dna.name == 'wtapper':
            x = self.TurnsElapsed
            currentBossHealth = -1
            for s in self.battle.suits:
                if s.dna.name == 'phouse' or s.dna.name == 'bkeeper' or s.dna.name == 'ambass':
                    currentBossHealth = s.currHP
        if theSuit.dna.name == 'ambass':
            x = self.TurnsElapsed
            currentBossHealth = -1
            for s in self.battle.suits:
                if s.dna.name == 'wtapper' or s.dna.name == 'bkeeper' or s.dna.name == 'phouse':
                    currentBossHealth = s.currHP
        if theSuit.dna.name == 'videog':
            x = self.TurnsElapsed
            currentBossHealth = -1
            for s in self.battle.suits:
                if s.dna.name == 'bcaster':
                    currentBossHealth = s.currHP
            currentBossHealth2 = -1
            currentBossHealth3 = -1
            for s in self.battle.suits:
                if s.dna.name == 'mh2':
                    currentBossHealth2 = s.currHP
                if s.dna.name == 'std2':
                    currentBossHealth3 = s.currHP
            if currentBossHealth == -1 and not self.suitHasCondition(theSuit.doId, 'silhouettespawn') and self.suitHasCondition(theSuit.doId, 'phase3'):
                self.setSuitCondition(theSuit.doId, 'silhouettespawn', 1, 1, 'setBoth')
            if currentBossHealth2 >= 1 and (x + 1) % 3 == 0:
                self.setSuitCondition(theSuit.doId, 'hollywoodcalculator', 1, 1, 'setBoth')
            if currentBossHealth3 >= 1 and (x + 1) % 3 == 0:
                self.setSuitCondition(theSuit.doId, 'hollywoodcalculator', 1, 1, 'setBoth')
     #   if theSuit.dna.name == 'hroller':
           # x = self.TurnsElapsed
           # return 'HighRollerWheelSpin'
     #   if theSuit.dna.name == 'hroller2':
         #   x = self.TurnsElapsed
          #  if x % 99 == 0:
           #     return 14
           # else:
              #  return 1
       # if theSuit.dna.name == 'hrollers':
           # x = self.TurnsElapsed
           # if theSuit.maxHP <= 12275:
              #  return random.randint(1, 2)
           # if theSuit.maxHP <= 12100:
                #return random.randint(1, 2)
            #if theSuit.maxHP <= 12000:
                #return random.randint(1, 2)
        #    else:
              #  return 2
        if theSuit.dna.name == 'radiog':
            x = self.TurnsElapsed
            currentBossHealth = -1
            for s in self.battle.suits:
                if s.dna.name == 'ubuster' or s.dna.name == 'racket' or s.dna.name == 'safesupervis':
                    currentBossHealth = s.currHP
        if theSuit.dna.name == 'racket':
            x = self.TurnsElapsed
            currentBossHealth = -1
            for s in self.battle.suits:
                if s.dna.name == 'ubuster' or s.dna.name == 'safesupervis' or s.dna.name == 'radiog':
                    currentBossHealth = s.currHP
        if theSuit.dna.name == 'ubuster':
            x = self.TurnsElapsed
            currentBossHealth = -1
            for s in self.battle.suits:
                if s.dna.name == 'safesupervis' or s.dna.name == 'racket' or s.dna.name == 'radiog':
                    currentBossHealth = s.currHP
        if theSuit.dna.name == 'safesupervis':
            x = self.TurnsElapsed
            currentBossHealth = -1
            for s in self.battle.suits:
                if s.dna.name == 'ubuster' or s.dna.name == 'racket' or s.dna.name == 'radiog':
                    currentBossHealth = s.currHP
        return atk

    def __calcSuitTarget(self, attack):
        targets = []
        # Get the amount of Toons we are targeting and make sure it isn't more than the number of currently existing Toons.
        atkType = attack[SUIT_ATK_COL]
        if self.__suitAtkAffectsGroup(attack):
            toonCount = len(self.battle.activeToons)
        elif atkType['group'] == SuitBattleGlobals.ATK_TGT_TRIPLE:
            toonCount = min(len(self.battle.activeToons),
                            3)
        elif atkType['group'] == SuitBattleGlobals.ATK_TGT_DOUBLE:
            toonCount = min(len(self.battle.activeToons),
                            2)
        else:
            toonCount = 1
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
                chosen = self.battle.activeToons.index(toonId)
            else:
                chosen = self.__pickRandomToon(suitId)
            while chosen in targets:
                chosen = self.__pickRandomToon(suitId)
            targets.append(chosen)

        return targets

    def __calcSuitTargetSuit(self, attack):
        targets = []
        # Get the amount of Suits we are targeting and make sure it isn't more than the number of currently existing Suits.
        atkType = attack[SUIT_ATK_COL]
        if self.__suitAtkAffectsGroup(attack):
            suitCount = len(self.battle.activeSuits)
        else:
            suitCount = min(len(self.battle.activeSuits),
                            2 if atkType['group'] == SuitBattleGlobals.ATK_TGT_DOUBLE else 1)
        suitId = attack[SUIT_ID_COL]
        for i in xrange(0, suitCount):
            if suitId in self.SuitAttackers and random.randint(0, 99) < 75:
                totalDamage = 0
                for currSuit in self.SuitAttackers[suitId].keys():
                    totalDamage += self.SuitAttackers[suitId][currSuit]

                dmgs = []
                for currSuit in self.SuitAttackers[suitId].keys():
                    dmgs.append(self.SuitAttackers[suitId][currSuit] / totalDamage * 100)

                dmgIdx = SuitBattleGlobals.pickFromFreqList(dmgs)
                if dmgIdx == None:
                    suitId2 = self.__pickRandomSuit(suitId)
                else:
                    suitId2 = self.SuitAttackers[suitId].keys()[dmgIdx]
                if suitId2 == -1 or suitId2 not in self.battle.activeSuits:
                    continue
                chosen = self.battle.activeSuits.index(suitId2)
            else:
                chosen = self.__pickRandomSuit(suitId)
            while chosen in targets:
                chosen = self.__pickRandomSuit(suitId)
            targets.append(chosen)

        return targets

    def __calcSuitTargetOLD(self, attack):
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
                    return -1
                return self.battle.activeToons.index(toonId)
            else:
                return self.__pickRandomToon(suitId)

    def __calcSuitTargetALT(self, attack):
        targets = []
        # Get the amount of Toons we are targeting and make sure it isn't more than the number of currently existing Toons.
        atkType = attack[SUIT_ATK_COL]
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

    def __pickRandomSuit(self, suitId):
        liveSuits = []
        for currSuit in self.battle.activeSuits:
            if not self.__combatantDead(currSuit, toon=0):
                liveSuits.append(self.battle.activeSuits.index(currSuit))

        if len(liveSuits) == 0:
            self.notify.debug('No tgts avail. for suit ' + str(suitId))
            return -1
        chosen = random.choice(liveSuits)
        self.notify.debug('Suit randomly attacking suit ' + str(self.battle.activeSuits[chosen]))
        return chosen

    def __suitAtkHit(self, suitId, atkType):
        if self.suitsAlwaysHit:
            return True
        elif self.suitsAlwaysMiss:
            return False
        theSuit = self.battle.findSuit(suitId)
        # if not theSuit:
        #     self.notify.warning('We did not find a Suit with ID %s.' % suitId)
        #     return False
        atkAcc = atkType['acc']
        # suitAcc = SuitBattleGlobals.SuitAttributes[theSuit.dna.name]['acc'][theSuit.getLevel()]
        suitAcc = 0 # suitAcc does absolutely nothing.  It was supposedly intended to alter the attack accuracy by using the average of the attack and Cog's accuracy, but that is likely obtrusive.  I'm keeping the variable anyway because of what is printed.
        acc = atkAcc
        randChoice = random.randint(0, 99)
        if randChoice < acc:
            return True
        return False

    def __suitAtkAffectsGroup(self, attack):
        atkType = attack[SUIT_ATK_COL]
        return atkType['group'] == SuitBattleGlobals.ATK_TGT_GROUP

    def __createSuitTargetList(self, attack):
        targetList = []
        if not attack[SUIT_ATK_COL]:
            return targetList
        debug = self.notify.getDebug()
        if not self.__suitAtkAffectsGroup(attack):
            for currToon in attack[SUIT_TGT_COL]:
                targetList.append(self.battle.activeToons[currToon])

        else:
            for currToon in self.battle.activeToons:
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
            if toon and toon.immortalMode:
                result = 1
            elif TOONS_TAKE_NO_DAMAGE:
                result = 0
            elif self.__suitAtkHit(attack[SUIT_ID_COL], attack[SUIT_ATK_COL]):
                mult = 1.0
                result = math.ceil(atkType['hp'] * mult)
                if theSuit.getExecutive():
                    result = math.ceil(result * ToontownBattleGlobals.EXECUTIVE_DMG_MULT)
                elif theSuit.getGovernaught():
                    result = math.ceil(result * ToontownBattleGlobals.GOVERNAUGHT_DMG_MULT)
            targetIndex = self.battle.activeToons.index(toonId)
            if atkType['name'] == 'Aftershock':
                result = random.randint(18, 38)
                attack[SUIT_HP_COL][targetIndex] = result
            else:
                attack[SUIT_HP_COL][targetIndex] = result


            if self.toonHasCondition(toonId, 'hidden'):
                result *= 0
            if theSuit.getHP() > (theSuit.getMaxHP() * 1.5):
                result *= 1.5
            if self.suitHasCondition(theSuit.doId, 'desperation'):
                result *= (1 + self.getSuitConditionModifier(theSuit.doId, 'desperation'))
            if self.suitHasCondition(theSuit.doId, 'brokenconnection'):
                result *= self.getSuitConditionModifier(theSuit.doId, 'brokenconnection')
            if self.suitHasCondition(theSuit.doId, 'enraged'):
                result *= self.getSuitConditionModifier(theSuit.doId, 'enraged')
            if self.toonHasCondition(toonId, 'snapped'):
                result *= self.getToonConditionModifier(toonId, 'snapped')
            if self.toonHasCondition(toonId, 'corruption'):
                result *= self.getToonConditionModifier(toonId, 'corruption')
            if theSuit.getDamageMultiplier() > 1:
                result *= theSuit.getDamageMultiplier()
            attack[SUIT_HP_COL][targetIndex] = math.ceil(result)

            if self.suitHasCondition(theSuit.doId, 'syphon'):
                theSuit.setHP(math.ceil(theSuit.currHP + result))

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
            if toon and toon.immortalMode:
                result = 1
            elif TOONS_TAKE_NO_DAMAGE:
                result = 0
            elif self.__suitAtkHit(attack[SUIT_ID_COL], attack[SUIT_ATK_COL]):
                mult = 1.0
                result = math.ceil(atkType['hp'] * mult)
                if theSuit:
                    if theSuit.getExecutive():
                        result = math.ceil(result * ToontownBattleGlobals.EXECUTIVE_DMG_MULT)
                    elif theSuit.getGovernaught():
                        result = math.ceil(result * ToontownBattleGlobals.GOVERNAUGHT_DMG_MULT)
            targetIndex = self.battle.activeToons.index(toonId)
            if atkType['name'] == 'SynergyFees':
                result = self.costsMultiplier
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'costscalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'CalculatingFees':
                result = self.costsCalculatorMultiplier
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'calculatingcalculator', 1, 1, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'costscalculator', 1, 10, 'setBoth')
                self.costsMultiplier += 4
                self.costsCalculatorMultiplier += 4
            elif atkType['name'] == 'StenographerSanction':
                result = 25
                attack[SUIT_HP_COL][targetIndex] = result
                currentBossHealth = -1
                currentBossHealth2 = -1
                for s in self.battle.suits:
                    if s.dna.name == 'lgator':
                        currentBossHealth = s.currHP
                    if s.dna.name == 'caseman':
                        suit = s
                        currentBossHealth2 = s.currHP
                if currentBossHealth2 >= 1:
                    self.setSuitCondition(suit.doId, 'bindingscalculator2', 1, 10, 'setBoth')
                if currentBossHealth >= 1:
                    if self.getToonConditionModifier(toonId, 'allGagBoost') < -75:
                        self.setToonCondition(toon.doId, 'allGagBoost',
                                              self.getToonConditionModifier(toonId, 'allGagBoost'), 3, 'setBoth')
                        self.setToonCondition(toon.doId, 'lureBoost',
                                              self.getToonConditionModifier(toonId, 'lureBoost'), 3, 'setBoth')
                    else:
                        self.setToonCondition(toon.doId, 'allGagBoost', -75, 3, 'setBoth')
                        self.setToonCondition(toon.doId, 'lureBoost', -75, 3, 'setBoth')
                else:
                    if self.getToonConditionModifier(toonId, 'allGagBoost') < -50:
                        self.setToonCondition(toon.doId, 'allGagBoost',
                                              self.getToonConditionModifier(toonId, 'allGagBoost'), 3, 'setBoth')
                        self.setToonCondition(toon.doId, 'lureBoost',
                                              self.getToonConditionModifier(toonId, 'lureBoost'), 3, 'setBoth')
                    else:
                        self.setToonCondition(toon.doId, 'allGagBoost', -50, 3, 'setBoth')
                        self.setToonCondition(toon.doId, 'lureBoost', -50, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'sanctioncalculator', 0, 0, 'setBoth')
                from toontown.suit.DistributedLawbotBossAI import DistributedLawbotBossAI

                boss = None
                for do in simbase.air.doId2do.values():
                    if isinstance(do, DistributedLawbotBossAI):
                        for t in self.battle.activeToons:
                            if t in do.involvedToons:
                                boss = do
                                break
                        for t in self.battle.activeToons:
                            if t in do.involvedToons:
                                if len(self.battle.activeSuits) < 4:
                                    boss.appendSuitsToBattle(boss.battleNumber, 'lit')
            elif atkType['name'] == 'StenographerSanctionBindings':
                self.setSuitCondition(theSuit.doId, 'sanctioncalculator2', 0, 0, 'setBoth')
                if self.toonHasCondition(toon.doId, 'markedforsanction'):
                    self.setToonCondition(toon.doId, 'markedforsanction', 1, 1, 'setBoth')
                    if self.getToonConditionModifier(toonId, 'allGagBoost') < -25:
                        self.setToonCondition(toon.doId, 'allGagBoost', self.getToonConditionModifier(toonId, 'allGagBoost'), 3, 'setBoth')
                        self.setToonCondition(toon.doId, 'lureBoost', self.getToonConditionModifier(toonId, 'lureBoost'), 3, 'setBoth')
                    else:
                        self.setToonCondition(toon.doId, 'allGagBoost', -25, 3, 'setBoth')
                        self.setToonCondition(toon.doId, 'lureBoost', -25, 3, 'setBoth')
                    result = 25
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'StenographerCourtRecordBan':
                if self.toonHasCondition(toon.doId, 'banned'):
                    self.setToonCondition(toon.doId, 'banned', 1, 1, 'setBoth')
                    result = 50
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'CaseManagerInsurancePlan':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'insurancecalculator', 0, 0, 'setBoth')
                for suit in self.battle.activeSuits:
                    if not self.suitHasCondition(suit.doId, 'insured'):
                        self.setSuitCondition(suit.doId, 'insured', 1, 99, 'setBoth')
                        self.setSuitCondition(suit.doId, 'sued', 0, 0, 'setBoth')
                        self.setSuitCondition(suit.doId, 'suemovie', 0, 0, 'setBoth')
                from toontown.suit.DistributedLawbotBossAI import DistributedLawbotBossAI

                boss = None
                for do in simbase.air.doId2do.values():
                    if isinstance(do, DistributedLawbotBossAI):
                        for t in self.battle.activeToons:
                            if t in do.involvedToons:
                                boss = do
                                break
                        for t in self.battle.activeToons:
                            if t in do.involvedToons:
                                if len(self.battle.activeSuits) < 4:
                                    boss.appendSuitsToBattle(boss.battleNumber, 'lit')
            elif atkType['name'] == 'CaseManagerInsurance':
                for s in self.battle.suits:
                    if s.getManager():
                        self.setSuitCondition(s.doId, 'healfinished', 1, 1, 'setBoth')
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                currentBossHealth = -1
                for s in self.battle.suits:
                    if s.dna.name == 'sgoat':
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
            elif atkType['name'] == 'CaseManagerLegalBindings':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'bound', 1, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'bindingscalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'CaseManagerLegalBindings2':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'bound', 1, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'bindingscalculator2', 0, 0, 'setBoth')
            elif atkType['name'] == 'CaseManagerLegallyBound':
                for s in self.battle.suits:
                    if s.getManager():
                        self.setSuitCondition(s.doId, 'dotfinished', 1, 1, 'setBoth')
                if self.toonHasCondition(toon.doId, 'bound'):
                    if self.toonHasCondition(toon.doId, 'bound') and self.getToonConditionTurns(toon.doId,
                                                                                                'bound') <= 1:
                        self.setToonCondition(toon.doId, 'markedforsanction', 1, 5, 'setBoth')
                        for s in self.battle.suits:
                            if s.dna.name == 'stenog':
                                suit = s
                                currentBossHealth = s.currHP
                                if currentBossHealth >= 1:
                                    self.setSuitCondition(suit.doId, 'sanctioncalculator2', 1, 10, 'setBoth')
                    result = 20
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'CaseManagerCourtRecordBan':
                if self.toonHasCondition(toon.doId, 'banned2'):
                    self.setToonCondition(toon.doId, 'banned2', 1, 1, 'setBoth')
                    result = 50
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'LitigatorSnapSoak': #soaked snap
                if self.toonHasCondition(toon.doId, 'soakToon'):
                    result = 33
                    attack[SUIT_HP_COL][targetIndex] = result
                    if self.getToonConditionModifier(toonId, 'snapped') > 1.1:
                        self.setToonCondition(toon.doId, 'snapped', self.getToonConditionModifier(toonId, 'snapped'), 3, 'setBoth')
                    else:
                        self.setToonCondition(toon.doId, 'snapped', 1.1, 3, 'setBoth')
                    self.setToonCondition(toon.doId, 'soakToon', 1, 1, 'setBoth')
                    self.setSuitCondition(theSuit.doId, 'soakedcalculator', 0, 0, 'setBoth')
                    self.setSuitCondition(theSuit.doId, 'soakedcalculator2', 1, 10, 'setBoth')
                else:
                    result = 0
                    attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'LitigatorSnap':
                currentBossHealth = -1
                for s in self.battle.suits:
                    if s.dna.name == 'stenog':
                        currentBossHealth = s.currHP
                if currentBossHealth >= 1:
                    result = 21
                    attack[SUIT_HP_COL][targetIndex] = result
                    if self.getToonConditionModifier(toonId, 'snapped') > 1.4:
                        self.setToonCondition(toon.doId, 'snapped', self.getToonConditionModifier(toonId, 'snapped'), 3, 'setBoth')
                    else:
                        self.setToonCondition(toon.doId, 'snapped', 1.4, 3, 'setBoth')
                else:
                    result = 25
                    attack[SUIT_HP_COL][targetIndex] = result
                    if self.getToonConditionModifier(toonId, 'snapped') > 1.2:
                        self.setToonCondition(toon.doId, 'snapped', self.getToonConditionModifier(toonId, 'snapped'), 3, 'setBoth')
                    else:
                        self.setToonCondition(toon.doId, 'snapped', 1.2, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'snappedcalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'LitigatorBayouBellow':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'bellowcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'bellowcalculator2', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'soakedcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'soakedcalculator2', 0, 0, 'setBoth')
                for suit in self.battle.activeSuits:
                    self.setSuitCondition(suit.doId, 'soaked', 0, 0, 'setBoth')
                    self.setSuitCondition(suit.doId, 'dazed', 0, 0, 'setBoth')
                    self.setSuitCondition(suit.doId, 'sued', 0, 0, 'setBoth')
                    self.setSuitCondition(suit.doId, 'suemovie', 0, 0, 'setBoth')
                    if self.suitHasCondition(suit.doId, 'lured'):
                        self.setSuitCondition(suit.doId, 'lured', 0, 0, 'setBoth')
                    continue
                for suit in self.currentlyLuredSuits.keys():
                    self.setSuitCondition(suit, 'bellowattack', 1, 1, 'setBoth')
                    self.__removeLured(suit)
            elif atkType['name'] == 'LitigatorBayouBash':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'bashcalculator', 0, 0, 'setBoth')
                from toontown.suit.DistributedLawbotBossAI import DistributedLawbotBossAI

                boss = None
                for do in simbase.air.doId2do.values():
                    if isinstance(do, DistributedLawbotBossAI):
                        for t in self.battle.activeToons:
                            if t in do.involvedToons:
                                boss = do
                                break
                        for t in self.battle.activeToons:
                            if t in do.involvedToons:
                                if len(self.battle.activeSuits) < 6:
                                    boss.appendSuitsToBattle(boss.battleNumber, 'lit')
            elif atkType['name'] == 'ScapegoatEnraged':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'shielding', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'rageBuilding', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'enraged', 1.3, 3, 'setBoth')
                if self.suitHasCondition(theSuit.doId, 'lured'):
                    self.setSuitCondition(theSuit.doId, 'lured', 0, 0, 'setBoth')
                self.__removeLured(theSuit.doId)
                for s in self.battle.suits:
                    if s.dna.name == 'caseman':
                        suit = s
                        currentBossHealth = s.currHP
                        if currentBossHealth >= 1:
                            self.setSuitCondition(suit.doId, 'bindingscalculator2', 1, 10, 'setBoth')
                            self.setSuitCondition(suit.doId, 'ban2tracks', 1, 3, 'setBoth')
                    if s.dna.name == 'stenog':
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
                        for t in self.battle.activeToons:
                            if t in do.involvedToons:
                                if len(self.battle.activeSuits) < 4:
                                    boss.appendSuitsToBattle(boss.battleNumber, 'lit')
            elif atkType['name'] == 'ScapegoatCourtRecordBan':
                if self.toonHasCondition(toon.doId, 'banned3'):
                    self.setToonCondition(toon.doId, 'banned3', 1, 1, 'setBoth')
                    result = 50
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'ScapegoatShieldsUp':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                theSuit.setHP(math.ceil(theSuit.currHP + result))
                self.setSuitCondition(theSuit.doId, 'shielding', 1, 99, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'rageBuilding', 0, 99, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'enraged', 0, 0, 'none')
                #self.setSuitCondition(theSuit.doId, 'gavelcalculator', 1, 10, 'setBoth')
                for s in self.battle.suits:
                    if s.dna.name == 'lgator':
                        suit = s
                        currentBossHealth = s.currHP
                        if currentBossHealth >= 1:
                            self.setSuitCondition(suit.doId, 'bellowcalculator2', 1, 10, 'setBoth')
                            self.setSuitCondition(suit.doId, 'bashcalculator', 1, 10, 'setBoth')
            elif atkType['name'] == 'ScapegoatGavel':
                result = 25
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'noDamage', 1, 3, 'setBoth')
                self.setToonCondition(toon.doId, 'hidden', 1, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'gavelcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'gavelcalculator2', 1, 10, 'setBoth')
            elif atkType['name'] == 'ScapegoatBarnyardBash':
                if self.toonHasCondition(toon.doId, 'noDamage'):
                    result = 25
                    attack[SUIT_HP_COL][targetIndex] = result
                    self.setToonCondition(toon.doId, 'noDamage', 0, 0, 'setBoth')
                    self.setToonCondition(toon.doId, 'hidden', 0, 0, 'setBoth')
                    self.setSuitCondition(theSuit.doId, 'gavelcalculator2', 0, 0, 'setBoth')
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'ReddPeckingOrder':
                result = 25
                attack[SUIT_HP_COL][targetIndex] = result
                if self.getToonConditionModifier(toonId, 'snapped') > 1.2:
                    self.setToonCondition(toon.doId, 'snapped', self.getToonConditionModifier(toonId, 'snapped'), 3, 'setBoth')
                else:
                    self.setToonCondition(toon.doId, 'snapped', 1.2, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'snappedcalculator', 0, 0, 'setBoth')
                from toontown.suit.DistributedLawbotBossAI import DistributedLawbotBossAI

                boss = None
                for do in simbase.air.doId2do.values():
                    if isinstance(do, DistributedLawbotBossAI):
                        for t in self.battle.activeToons:
                            if t in do.involvedToons:
                                boss = do
                                break
                        for t in self.battle.activeToons:
                            if t in do.involvedToons:
                                if len(self.battle.activeSuits) < 6:
                                    boss.appendSuitsToBattle(boss.battleNumber, 'lit2')
            elif atkType['name'] == 'ReddLiquidationSale':
                result = 38
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'ReddAutoRepair':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
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
            elif atkType['name'] == 'WSIJuryNotice':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                from toontown.suit.DistributedLawbotBossAI import DistributedLawbotBossAI

                boss = None
                for do in simbase.air.doId2do.values():
                    if isinstance(do, DistributedLawbotBossAI):
                        for t in self.battle.activeToons:
                            if t in do.involvedToons:
                                boss = do
                                break
                        for t in self.battle.activeToons:
                            if t in do.involvedToons:
                                if len(self.battle.activeSuits) < 6:
                                    boss.appendSuitsToBattle(boss.battleNumber, 'lit2')
            elif atkType['name'] == 'WSICeaseAndDesist':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'soakedcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'soakedcalculator2', 1, 10, 'setBoth')
                self.setToonCondition(toon.doId, 'noSOS', 1, 2, 'setBoth')
                self.setToonCondition(toon.doId, 'noFires', 1, 2, 'setBoth')
                self.setToonCondition(toon.doId, 'noSues', 1, 2, 'setBoth')
                self.setToonCondition(toon.doId, 'noUnites', 1, 2, 'setBoth')
                self.setToonCondition(toon.doId, 'noDamage', 1, 2, 'setBoth')
                for suit in self.battle.activeSuits:
                    self.setSuitCondition(suit.doId, 'immune', 1, 2, 'setBoth')
                    continue
            elif atkType['name'] == 'PowerhouseBurnDamage':
                for s in self.battle.suits:
                    if s.getManager():
                        self.setSuitCondition(theSuit.doId, 'dotfinished', 1, 1, 'setBoth')
                if self.toonHasCondition(toon.doId, 'burned'):
                    result = 30
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'PowerhouseAbsorb':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'shielding', 1, 99, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'soakImmune', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'syphon', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'lureImmune', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'powerhouseRotation', 0, 0, 'setBoth')
                for s in self.battle.suits:
                    if s.dna.name == 'wtapper':
                        suit = s
                        currentBossHealth = s.currHP
                        if currentBossHealth >= 1:
                            self.setSuitCondition(suit.doId, 'bantracks', 1, 3, 'setBoth')
            elif atkType['name'] == 'PowerhouseSoakImmune':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'shielding', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'soakImmune', 1, 99, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'syphon', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'lureImmune', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'powerhouseRotation', 0, 0, 'setBoth')
                for s in self.battle.suits:
                    if s.dna.name == 'wtapper':
                        suit = s
                        currentBossHealth = s.currHP
                        if currentBossHealth >= 1:
                            self.setSuitCondition(suit.doId, 'bantracks', 1, 3, 'setBoth')
            elif atkType['name'] == 'PowerhouseLureImmune':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'shielding', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'soakImmune', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'syphon', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'lureImmune', 1, 99, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'powerhouseRotation', 0, 0, 'setBoth')
                for s in self.battle.suits:
                    if s.dna.name == 'wtapper':
                        suit = s
                        currentBossHealth = s.currHP
                        if currentBossHealth >= 1:
                            self.setSuitCondition(suit.doId, 'bantracks', 1, 3, 'setBoth')
            elif atkType['name'] == 'PowerhouseSyphon':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'shielding', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'soakImmune', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'syphon', 1, 99, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'lureImmune', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'powerhouseRotation', 0, 0, 'setBoth')
                for s in self.battle.suits:
                    if s.dna.name == 'wtapper':
                        suit = s
                        currentBossHealth = s.currHP
                        if currentBossHealth >= 1:
                            self.setSuitCondition(suit.doId, 'bantracks', 1, 3, 'setBoth')
            elif atkType['name'] == 'PowerhouseSyphonDesperation':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'syphoncalculator', 0, 0, 'setBoth')
                for suit in self.battle.activeSuits:
                    self.setSuitCondition(suit.doId, 'syphon', 1, 99, 'setBoth')
                    self.setSuitCondition(suit.doId, 'sued', 0, 0, 'setBoth')
                    self.setSuitCondition(suit.doId, 'suemovie', 0, 0, 'setBoth')
            elif atkType['name'] == 'PowerhouseSnipeVulnerable':
                if self.toonHasCondition(toon.doId, 'snapped'):
                    self.setToonCondition(toon.doId, 'burned', 1, 2, 'setBoth')
                    result = 25
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'vulnerablesnipe', 0, 0, 'setBoth')
            elif atkType['name'] == 'PowerhouseSnipeMulligan':
                if self.toonHasCondition(toon.doId, 'mulligan'):
                    self.setToonCondition(toon.doId, 'burned', 1, 2, 'setBoth')
                    self.setToonCondition(toon.doId, 'mulligan', 1, 1, 'setBoth')
                    result = 25
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'mulligansnipe', 0, 0, 'setBoth')
            elif atkType['name'] == 'PowerhouseSnipeCollectCall':
                if self.toonHasCondition(toon.doId, 'collectcalled'):
                    self.setToonCondition(toon.doId, 'burned', 1, 2, 'setBoth')
                    result = 25
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'collectcallsnipe', 0, 0, 'setBoth')
            elif atkType['name'] == 'PowerhouseSnipeBookkept':
                if self.toonHasCondition(toon.doId, 'bookkeepingtoon'):
                    self.setToonCondition(toon.doId, 'burned', 1, 2, 'setBoth')
                    result = 25
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'bookkeepersnipe', 0, 0, 'setBoth')
            elif atkType['name'] == 'PowerhouseSnipeSoaked':
                if self.toonHasCondition(toon.doId, 'soakToon'):
                    self.setToonCondition(toon.doId, 'burned', 1, 2, 'setBoth')
                    self.setToonCondition(toon.doId, 'soakToon', 1, 1, 'setBoth')
                    self.setSuitCondition(theSuit.doId, 'soakedcalculator', 0, 0, 'setBoth')
                    self.setSuitCondition(theSuit.doId, 'soakedcalculator2', 1, 10, 'setBoth')
                    result = 25
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'PowerhouseSnipeGagBan':
                if self.toonHasCondition(toon.doId, 'banned') or self.toonHasCondition(toon.doId, 'banned2'):
                    self.setToonCondition(toon.doId, 'banned2', 1, 1, 'setBoth')
                    self.setToonCondition(toon.doId, 'banned', 1, 1, 'setBoth')
                    self.setToonCondition(toon.doId, 'burned', 1, 2, 'setBoth')
                    result = 25
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'gagbansnipe', 0, 0, 'setBoth')
            elif atkType['name'] == 'PowerhouseGeneration':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = theSuit
                if not self.suitHasCondition(theSuit.doId, 'vulnerablevideographer'):
                    self.setSuitCondition(theSuit.doId, 'vulnerablevideographer', 10.5, 99, 'setBoth')
                else:
                    self.setSuitCondition(theSuit.doId, 'vulnerablevideographer', (self.getSuitConditionModifier(theSuit.doId, 'vulnerablevideographer') + 10.5),
                                              99, 'setBoth')
                theSuit.setDamageMultiplier(theSuit.getDamageMultiplier() * 1.05)
                self.setSuitCondition(theSuit.doId, 'syphon', 1, 99, 'setBoth')
            elif atkType['name'] == 'AmbassadorManagerialProtection':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'bashcalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'AmbassadorRefinement':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'immune', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'refinementcalculator', 0, 0, 'setBoth')
                currentBossHealth = -1
                for s in self.battle.suits:
                    if s.dna.name == 'phouse':
                        currentBossHealth = s.currHP
                if currentBossHealth >= 1:
                    for suit in self.battle.activeSuits:
                        self.setSuitCondition(suit.doId, 'sued', 0, 0, 'setBoth')
                        self.setSuitCondition(suit.doId, 'suemovie', 0, 0, 'setBoth')
                        if suit.currHP <= 0:
                            continue
                        x = (suit.maxHP * suit.hardMaxHP) - suit.currHP
                        if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
                            suit.setHP(suit.currHP + 0)
                        elif suit.currHP + 275 > (suit.maxHP * suit.hardMaxHP):
                            suit.setHP(suit.currHP + x)
                        else:
                            suit.setHP(suit.currHP + 275)
                elif currentBossHealth <= 0:
                    for suit in self.battle.activeSuits:
                        self.setSuitCondition(suit.doId, 'sued', 0, 0, 'setBoth')
                        self.setSuitCondition(suit.doId, 'suemovie', 0, 0, 'setBoth')
                        if suit.currHP <= 0:
                            continue
                        x = (suit.maxHP * suit.hardMaxHP) - suit.currHP
                        if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
                            suit.setHP(suit.currHP + 0)
                        elif suit.currHP + 175 > (suit.maxHP * suit.hardMaxHP):
                            suit.setHP(suit.currHP + x)
                        else:
                            suit.setHP(suit.currHP + 175)
                    continue
            elif atkType['name'] == 'AmbassadorRefinementManager':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'immune', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'refinemanagercalculator', 0, 0, 'setBoth')
                currentBossHealth = -1
                for s in self.battle.suits:
                    if s.dna.name == 'phouse':
                        currentBossHealth = s.currHP
                if currentBossHealth >= 1:
                    for suit in self.battle.activeSuits:
                        if suit.dna.name == 'wtapper' or suit.dna.name == 'bkeeper' or suit.dna.name == 'phouse':
                            if suit.currHP <= 0:
                                continue
                            x = (suit.maxHP * suit.hardMaxHP) - suit.currHP
                            if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
                                suit.setHP(suit.currHP + 0)
                            elif suit.currHP + 350 > (suit.maxHP * suit.hardMaxHP):
                                suit.setHP(suit.currHP + x)
                            else:
                                suit.setHP(suit.currHP + 350)
                elif currentBossHealth <= 0:
                    for suit in self.battle.activeSuits:
                        if suit.dna.name == 'wtapper' or suit.dna.name == 'bkeeper' or suit.dna.name == 'phouse':
                            if suit.currHP <= 0:
                                continue
                            x = (suit.maxHP * suit.hardMaxHP) - suit.currHP
                            if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
                                suit.setHP(suit.currHP + 0)
                            elif suit.currHP + 200 > (suit.maxHP * suit.hardMaxHP):
                                suit.setHP(suit.currHP + x)
                            else:
                                suit.setHP(suit.currHP + 200)
                        continue
            elif atkType['name'] == 'AmbassadorAdvancement':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'advancementcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'headrollertargetcalculator', 1, 10, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target6', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target5', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target4', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target3', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target2', 0, 0, 'setBoth')
                targetSuit = self.battle.activeSuits[1]
                self.setSuitCondition(targetSuit.doId, 'ambheadrollertarget', 1, 10, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'bellowattack', 1, 1, 'setBoth')
                self.__removeLured(targetSuit.doId)
                if self.suitHasCondition(targetSuit.doId, 'lured'):
                    self.setSuitCondition(targetSuit.doId, 'lured', 0, 0, 'setBoth')
            elif atkType['name'] == 'AmbassadorAdvancement2':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'advancementcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'headrollertargetcalculator', 1, 10, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target6', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target5', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target4', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target3', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target2', 0, 0, 'setBoth')
                targetSuit = self.battle.activeSuits[2]
                self.setSuitCondition(targetSuit.doId, 'ambheadrollertarget', 1, 10, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'bellowattack', 1, 1, 'setBoth')
                self.__removeLured(targetSuit.doId)
                if self.suitHasCondition(targetSuit.doId, 'lured'):
                    self.setSuitCondition(targetSuit.doId, 'lured', 0, 0, 'setBoth')
            elif atkType['name'] == 'AmbassadorAdvancement3':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'advancementcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'headrollertargetcalculator', 1, 10, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target6', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target5', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target4', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target3', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target2', 0, 0, 'setBoth')
                targetSuit = self.battle.activeSuits[3]
                self.setSuitCondition(targetSuit.doId, 'ambheadrollertarget', 1, 10, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'bellowattack', 1, 1, 'setBoth')
                self.__removeLured(targetSuit.doId)
                if self.suitHasCondition(targetSuit.doId, 'lured'):
                    self.setSuitCondition(targetSuit.doId, 'lured', 0, 0, 'setBoth')
            elif atkType['name'] == 'AmbassadorAdvancement4':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'advancementcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'headrollertargetcalculator', 1, 10, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target6', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target5', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target4', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target3', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target2', 0, 0, 'setBoth')
                targetSuit = self.battle.activeSuits[4]
                self.setSuitCondition(targetSuit.doId, 'ambheadrollertarget', 1, 10, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'bellowattack', 1, 1, 'setBoth')
                self.__removeLured(targetSuit.doId)
                if self.suitHasCondition(targetSuit.doId, 'lured'):
                    self.setSuitCondition(targetSuit.doId, 'lured', 0, 0, 'setBoth')
            elif atkType['name'] == 'AmbassadorAdvancement5':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'advancementcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'headrollertargetcalculator', 1, 10, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target6', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target5', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target4', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target3', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target2', 0, 0, 'setBoth')
                targetSuit = self.battle.activeSuits[5]
                self.setSuitCondition(targetSuit.doId, 'ambheadrollertarget', 1, 10, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'bellowattack', 1, 1, 'setBoth')
                self.__removeLured(targetSuit.doId)
                if self.suitHasCondition(targetSuit.doId, 'lured'):
                    self.setSuitCondition(targetSuit.doId, 'lured', 0, 0, 'setBoth')
            elif atkType['name'] == 'AmbassadorHeadRoller':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'headrollertargetcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'bellowattack', 1, 1, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'ambtarget6', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'ambtarget5', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'ambtarget4', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'ambtarget3', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'ambtarget2', 0, 0, 'setBoth')
                targetSuit = self.battle.activeSuits[1]
                if not targetSuit.dna.name in SuitBattleGlobals.SpecialCogDict:
                    theSuit.setHP(theSuit.currHP + targetSuit.currHP)
                    targetSuit.setHP(targetSuit.currHP - targetSuit.currHP)
                    theSuit.setDamageMultiplier(theSuit.getDamageMultiplier() * 1.05)
                    self.__removeLured(targetSuit.doId)
                    if self.suitHasCondition(targetSuit.doId, 'lured'):
                        self.setSuitCondition(targetSuit.doId, 'lured', 0, 0, 'setBoth')
            elif atkType['name'] == 'AmbassadorHeadRoller2':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'headrollertargetcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'bellowattack', 1, 1, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'ambtarget6', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'ambtarget5', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'ambtarget4', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'ambtarget3', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'ambtarget2', 0, 0, 'setBoth')
                targetSuit = self.battle.activeSuits[2]
                if not targetSuit.dna.name in SuitBattleGlobals.SpecialCogDict:
                    theSuit.setHP(theSuit.currHP + targetSuit.currHP)
                    targetSuit.setHP(targetSuit.currHP - targetSuit.currHP)
                    theSuit.setDamageMultiplier(theSuit.getDamageMultiplier() * 1.05)
                    self.__removeLured(targetSuit.doId)
                    if self.suitHasCondition(targetSuit.doId, 'lured'):
                        self.setSuitCondition(targetSuit.doId, 'lured', 0, 0, 'setBoth')
            elif atkType['name'] == 'AmbassadorHeadRoller3':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'headrollertargetcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'bellowattack', 1, 1, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'ambtarget6', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'ambtarget5', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'ambtarget4', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'ambtarget3', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'ambtarget2', 0, 0, 'setBoth')
                targetSuit = self.battle.activeSuits[3]
                if not targetSuit.dna.name in SuitBattleGlobals.SpecialCogDict:
                    theSuit.setHP(theSuit.currHP + targetSuit.currHP)
                    targetSuit.setHP(targetSuit.currHP - targetSuit.currHP)
                    theSuit.setDamageMultiplier(theSuit.getDamageMultiplier() * 1.05)
                    self.__removeLured(targetSuit.doId)
                    if self.suitHasCondition(targetSuit.doId, 'lured'):
                        self.setSuitCondition(targetSuit.doId, 'lured', 0, 0, 'setBoth')
            elif atkType['name'] == 'AmbassadorHeadRoller4':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'headrollertargetcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'bellowattack', 1, 1, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'ambtarget6', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'ambtarget5', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'ambtarget4', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'ambtarget3', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'ambtarget2', 0, 0, 'setBoth')
                targetSuit = self.battle.activeSuits[4]
                if not targetSuit.dna.name in SuitBattleGlobals.SpecialCogDict:
                    theSuit.setHP(theSuit.currHP + targetSuit.currHP)
                    targetSuit.setHP(targetSuit.currHP - targetSuit.currHP)
                    theSuit.setDamageMultiplier(theSuit.getDamageMultiplier() * 1.05)
                    self.__removeLured(targetSuit.doId)
                    if self.suitHasCondition(targetSuit.doId, 'lured'):
                        self.setSuitCondition(targetSuit.doId, 'lured', 0, 0, 'setBoth')
            elif atkType['name'] == 'AmbassadorHeadRoller5':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'headrollertargetcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'bellowattack', 1, 1, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'ambtarget6', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'ambtarget5', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'ambtarget4', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'ambtarget3', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'ambtarget2', 0, 0, 'setBoth')
                targetSuit = self.battle.activeSuits[5]
                if not targetSuit.dna.name in SuitBattleGlobals.SpecialCogDict:
                    theSuit.setHP(theSuit.currHP + targetSuit.currHP)
                    targetSuit.setHP(targetSuit.currHP - targetSuit.currHP)
                    theSuit.setDamageMultiplier(theSuit.getDamageMultiplier() * 1.05)
                    self.__removeLured(targetSuit.doId)
                    if self.suitHasCondition(targetSuit.doId, 'lured'):
                        self.setSuitCondition(targetSuit.doId, 'lured', 0, 0, 'setBoth')
            elif atkType['name'] == 'AmbassadorPhase2':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'phase3', 1, 99, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'headroller2calculator', 1, 10, 'setBoth')
                theSuit.setDamageMultiplier(theSuit.getDamageMultiplier() * 1.5)
            elif atkType['name'] == 'AmbassadorMulligan':
                roll = random.randint(0, 100)
                if roll >= 20:
                    result = 25
                    self.setToonCondition(toon.doId, 'mulligan', 1, 5, 'setBoth')
                    for s in self.battle.suits:
                        if s.dna.name == 'phouse':
                            suit = s
                            currentBossHealth = s.currHP
                            if currentBossHealth >= 1:
                                self.setSuitCondition(suit.doId, 'mulligansnipe', 1, 10, 'setBoth')
                    attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'AmbassadorManagerialProtectionImmunity':
                roll = random.randint(0, 100)
                if roll >= 20:
                    result = 25
                    self.setToonCondition(toon.doId, 'mulligan', 1, 5, 'setBoth')
                    for s in self.battle.suits:
                        if s.dna.name == 'phouse':
                            suit = s
                            currentBossHealth = s.currHP
                            if currentBossHealth >= 1:
                                self.setSuitCondition(suit.doId, 'mulligansnipe', 1, 10, 'setBoth')
                    attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'AmbassadorHeadRollerGroup':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'damageupcalculator2', 1, 1, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'headroller2calculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'headrollercalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'bellowattack', 1, 1, 'setBoth')
                for suit in self.battle.activeSuits:
                    if suit.currHP <= 0:
                        continue
                    if not suit.dna.name in SuitBattleGlobals.SpecialCogDict:
                        theSuit.setDamageMultiplier(theSuit.getDamageMultiplier() * 1.05)
                        theSuit.setHP(theSuit.currHP + 100)
                        suit.setHP(suit.currHP - suit.currHP)
                        if self.suitHasCondition(suit.doId, 'lured'):
                            self.setSuitCondition(suit.doId, 'lured', 0, 0, 'setBoth')
                    else:
                        if not suit.dna.name == 'ambass':
                            theSuit.setHP(theSuit.currHP + 250)
                            suit.setHP(suit.currHP - 250)
                    continue
                for suit in self.currentlyLuredSuits.keys():
                    self.__removeLured(suit)
            elif atkType['name'] == 'AmbassadorDamageUp': # Visual Damage Up
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'AmbassadorGhostMentality':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'headroller2calculator', 0, 0, 'setBoth')
                for suit in self.battle.activeSuits:
                    if not suit.isVirtual:
                        if suit.dna.name not in SuitBattleGlobals.SpecialCogDict:
                            self.setSuitCondition(suit.doId, 'sued', 0, 0, 'setBoth')
                            self.setSuitCondition(suit.doId, 'suemovie', 0, 0, 'setBoth')
                            suit.setDamageMultiplier(suit.getDamageMultiplier() * 1.5)
                            #self.setSuitCondition(suit.doId, 'contracted', 1, 99, 'setBoth')
            elif atkType['name'] == 'BookkeeperBookkeepingRetaliation':
                if self.toonHasCondition(toon.doId, 'bookkeepingtoon'):
                    self.setToonCondition(toon.doId, 'bookkeepingtoon', 1, 1, 'setBoth')
                    if self.getToonConditionModifier(toonId, 'allGagBoost') < -40:
                        self.setToonCondition(toon.doId, 'allGagBoost',
                                                  self.getToonConditionModifier(toonId, 'allGagBoost'), 3, 'setBoth')
                        self.setToonCondition(toon.doId, 'lureBoost',
                                                  self.getToonConditionModifier(toonId, 'lureBoost'), 3, 'setBoth')
                    else:
                        self.setToonCondition(toon.doId, 'allGagBoost', -40, 3, 'setBoth')
                        self.setToonCondition(toon.doId, 'lureBoost', -40, 3, 'setBoth')
                    for s in self.battle.suits:
                        if s.dna.name == 'phouse':
                            suit = s
                            currentBossHealth = s.currHP
                            if currentBossHealth >= 1:
                                self.setSuitCondition(suit.doId, 'bookkeepersnipe', 1, 10, 'setBoth')
                    result = 30
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'BookkeeperBookkeeping':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'bookkeeping', 1, 2, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'bookkeepingcalculator', 0, 0, 'setBoth')
                if self.suitHasCondition(theSuit.doId, 'lured'):
                    self.setSuitCondition(theSuit.doId, 'lured', 0, 0, 'setBoth')
                self.__removeLured(theSuit.doId)
            elif atkType['name'] == 'BookkeeperExplodingDocument':
                result = 30
                attack[SUIT_HP_COL][targetIndex] = result
                currentBossHealth = -1
                for s in self.battle.suits:
                    if s.dna.name == 'wtapper':
                        currentBossHealth = s.currHP
                if currentBossHealth >= 1:
                    if self.getToonConditionModifier(toonId, 'allGagBoost') < -75:
                        self.setToonCondition(toon.doId, 'allGagBoost',
                                              self.getToonConditionModifier(toonId, 'allGagBoost'), 3, 'setBoth')
                        self.setToonCondition(toon.doId, 'lureBoost',
                                              self.getToonConditionModifier(toonId, 'lureBoost'), 3, 'setBoth')
                    else:
                        self.setToonCondition(toon.doId, 'allGagBoost', -75, 3, 'setBoth')
                        self.setToonCondition(toon.doId, 'lureBoost', -75, 3, 'setBoth')
                else:
                    if self.getToonConditionModifier(toonId, 'allGagBoost') < -50:
                        self.setToonCondition(toon.doId, 'allGagBoost',
                                              self.getToonConditionModifier(toonId, 'allGagBoost'), 3, 'setBoth')
                        self.setToonCondition(toon.doId, 'lureBoost',
                                              self.getToonConditionModifier(toonId, 'lureBoost'), 3, 'setBoth')
                    else:
                        self.setToonCondition(toon.doId, 'allGagBoost', -50, 3, 'setBoth')
                        self.setToonCondition(toon.doId, 'lureBoost', -50, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'explodingcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'explodingcalculator2', 0, 0, 'setBoth')
            elif atkType['name'] == 'BookkeeperPaperCutMarked':
                result = 39
                attack[SUIT_HP_COL][targetIndex] = result
                if self.getToonConditionModifier(toonId, 'snapped') > 1.15:
                    self.setToonCondition(toon.doId, 'snapped', self.getToonConditionModifier(toonId, 'snapped'), 3, 'setBoth')
                else:
                    self.setToonCondition(toon.doId, 'snapped', 1.15, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'markedcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'markedcalculator2', 1, 10, 'setBoth')
                for s in self.battle.suits:
                    if s.dna.name == 'phouse':
                        suit = s
                        currentBossHealth = s.currHP
                        if currentBossHealth >= 1:
                            self.setSuitCondition(suit.doId, 'vulnerablesnipe', 1, 10, 'setBoth')
            elif atkType['name'] == 'BookkeeperPaperCutSoaked':
                result = 39
                attack[SUIT_HP_COL][targetIndex] = result
                if self.getToonConditionModifier(toonId, 'snapped') > 1.15:
                    self.setToonCondition(toon.doId, 'snapped', self.getToonConditionModifier(toonId, 'snapped'), 3, 'setBoth')
                else:
                    self.setToonCondition(toon.doId, 'snapped', 1.15, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'soakedcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'soakedcalculator2', 1, 10, 'setBoth')
                for s in self.battle.suits:
                    if s.dna.name == 'phouse':
                        suit = s
                        currentBossHealth = s.currHP
                        if currentBossHealth >= 1:
                            self.setSuitCondition(suit.doId, 'vulnerablesnipe', 1, 10, 'setBoth')
            elif atkType['name'] == 'BookkeeperPaperCut':
                result = 20
                attack[SUIT_HP_COL][targetIndex] = result
                currentBossHealth = -1
                for s in self.battle.suits:
                    if s.dna.name == 'phouse':
                        currentBossHealth = s.currHP
                if currentBossHealth >= 1:
                    if self.getToonConditionModifier(toonId, 'snapped') > 1.5:
                        self.setToonCondition(toon.doId, 'snapped', self.getToonConditionModifier(toonId, 'snapped'), 3, 'setBoth')
                    else:
                        self.setToonCondition(toon.doId, 'snapped', 1.5, 3, 'setBoth')
                else:
                    if self.getToonConditionModifier(toonId, 'snapped') > 1.25:
                        self.setToonCondition(toon.doId, 'snapped', self.getToonConditionModifier(toonId, 'snapped'), 3, 'setBoth')
                    else:
                        self.setToonCondition(toon.doId, 'snapped', 1.25, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'papercutcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'bookkeeping', 1, 1, 'setBoth')
                for s in self.battle.suits:
                    if s.dna.name == 'phouse':
                        suit = s
                        currentBossHealth = s.currHP
                        if currentBossHealth >= 1:
                            self.setSuitCondition(suit.doId, 'vulnerablesnipe', 1, 10, 'setBoth')
            elif atkType['name'] == 'WiretapperGagBan':
                if self.toonHasCondition(toon.doId, 'banned') or self.toonHasCondition(toon.doId, 'banned2'):
                    self.setToonCondition(toon.doId, 'banned2', 1, 1, 'setBoth')
                    self.setToonCondition(toon.doId, 'banned', 1, 1, 'setBoth')
                    for s in self.battle.suits:
                        if s.dna.name == 'phouse':
                            suit = s
                            currentBossHealth = s.currHP
                            if currentBossHealth >= 1:
                                self.setSuitCondition(suit.doId, 'gagbansnipe', 1, 10, 'setBoth')
                    result = 50
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'WiretapperBusySignal':
                self.setToonCondition(toon.doId, 'confused', 1, 2, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'busycalculator', 0, 0, 'setBoth')
                result = 30
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'WiretapperCollectCall2': # Collect Call Calculator
                result = self.costsCalculatorMultiplier
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'calculatingcalculator', 1, 1, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'costscalculator', 1, 10, 'setBoth')
                self.costsMultiplier += 4
                self.costsCalculatorMultiplier += 4
            elif atkType['name'] == 'WiretapperVoicemail':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'immune', 1, 2, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'voicemailcalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'WiretapperBrokenConnection':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'vulnerable', 1, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'brokenconnection', 1.3, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'brokenconnectioncalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'WiretapperWiretapped':
                result = random.randint(25, 45)
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'wiretappedcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'collectcallcalculator2', 1, 10, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'vulnerable', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'brokenconnection', 0, 0, 'setBoth')
                theSuit.setHP(math.ceil(theSuit.currHP + attack[SUIT_HP_COL][targetIndex] * 4))
            elif atkType['name'] == 'WiretapperCollectCall':
                result = self.costsMultiplier
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'collectcalled', 1, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'collectcallcalculator', 0, 0, 'setBoth')
                for s in self.battle.suits:
                    if s.dna.name == 'phouse':
                        suit = s
                        currentBossHealth = s.currHP
                        if currentBossHealth >= 1:
                            self.setSuitCondition(suit.doId, 'collectcallsnipe', 1, 10, 'setBoth')
            elif atkType['name'] == 'WiretapperCollectCall2':
                result = self.costsMultiplier
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'collectcalled', 1, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'collectcallcalculator3', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'collectcallcalculator2', 0, 0, 'setBoth')
                for s in self.battle.suits:
                    if s.dna.name == 'phouse':
                        suit = s
                        currentBossHealth = s.currHP
                        if currentBossHealth >= 1:
                            self.setSuitCondition(suit.doId, 'collectcallsnipe', 1, 10, 'setBoth')
            elif atkType['name'] == 'WiretapperCollectCallDamage':
                self.setSuitCondition(theSuit.doId, 'costscalculator', 0, 0, 'setBoth')
                for s in self.battle.suits:
                    if s.dna.name == 'bkeeper':
                        suit = s
                        currentBossHealth = s.currHP
                        if currentBossHealth >= 1:
                            self.setSuitCondition(suit.doId, 'explodingcalculator2', 1, 10, 'setBoth')
                result = self.costsMultiplier
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'SafetyHighPressure':
                result = 35
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'cannotDodge', 100, 2, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'cannotDodge', 100, 2, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'highpressurecalculator', 0, 0, 'setBoth')
                for suit in self.battle.activeSuits:
                    suit.setHP(math.ceil(suit.currHP - 100))
                    if suit.currHP <= 0:
                        if suit.getSkeleRevives() >= 1:
                            suit.useSkeleRevive()
                        self.__removeLured(suit.doId)
                        if self.suitHasCondition(suit.doId, 'lured'):
                            self.setSuitCondition(suit.doId, 'lured', 0, 0, 'setBoth')
                    continue
            elif atkType['name'] == 'SafetyHeatWaveCalculation':
                result = (1 + ((theSuit.getMaxHP() - theSuit.getHP()) / 60))
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'heatwavecalculationcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'heatwavecalculator', 1, 10, 'setBoth')
            elif atkType['name'] == 'SafetyHeatWave':
                result = (1 + ((theSuit.getMaxHP() - theSuit.getHP()) / 60))
                theSuit.setHP(theSuit.currHP - ((result / len(self.battle.activeToons)) * 3))
                if theSuit.currHP <= 0:
                    self.setSuitCondition(theSuit.doId, 'deathcheck', 1, 99, 'setBoth')
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'heatwavecalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'SafetyPromotion':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                targetSuit = self.battle.activeSuits[1]
                self.setSuitCondition(theSuit.doId, 'target6', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target5', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target4', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target3', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target2', 0, 0, 'setBoth')
                targetSuit.setManager(1)
                targetSuit.setHP(1000)
                targetSuit.setMaxHP(1000)
                self.setSuitCondition(targetSuit.doId, 'shielding', 1, 99, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'sued', 0, 0, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'suemovie', 0, 0, 'setBoth')
                if not self.suitHasCondition(targetSuit.doId, 'dead'):
                    self.setSuitCondition(theSuit.doId, 'promotioncalculator', 0, 0, 'setBoth')
                continue
            elif atkType['name'] == 'SafetyPromotion2':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                targetSuit = self.battle.activeSuits[2]
                self.setSuitCondition(theSuit.doId, 'target6', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target5', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target4', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target3', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target2', 0, 0, 'setBoth')
                targetSuit.setManager(1)
                targetSuit.setHP(1000)
                targetSuit.setMaxHP(1000)
                self.setSuitCondition(targetSuit.doId, 'shielding', 1, 99, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'sued', 0, 0, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'suemovie', 0, 0, 'setBoth')
                if not self.suitHasCondition(targetSuit.doId, 'dead'):
                    self.setSuitCondition(theSuit.doId, 'promotioncalculator', 0, 0, 'setBoth')
                continue
            elif atkType['name'] == 'SafetyPromotion3':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                targetSuit = self.battle.activeSuits[3]
                self.setSuitCondition(theSuit.doId, 'target6', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target5', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target4', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target3', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target2', 0, 0, 'setBoth')
                targetSuit.setManager(1)
                targetSuit.setHP(1000)
                targetSuit.setMaxHP(1000)
                self.setSuitCondition(targetSuit.doId, 'shielding', 1, 99, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'sued', 0, 0, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'suemovie', 0, 0, 'setBoth')
                if not self.suitHasCondition(targetSuit.doId, 'dead'):
                    self.setSuitCondition(theSuit.doId, 'promotioncalculator', 0, 0, 'setBoth')
                continue
            elif atkType['name'] == 'SafetyPromotion4':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                targetSuit = self.battle.activeSuits[4]
                self.setSuitCondition(theSuit.doId, 'target6', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target5', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target4', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target3', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target2', 0, 0, 'setBoth')
                targetSuit.setManager(1)
                targetSuit.setHP(1000)
                targetSuit.setMaxHP(1000)
                self.setSuitCondition(targetSuit.doId, 'shielding', 1, 99, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'sued', 0, 0, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'suemovie', 0, 0, 'setBoth')
                if not self.suitHasCondition(targetSuit.doId, 'dead'):
                    self.setSuitCondition(theSuit.doId, 'promotioncalculator', 0, 0, 'setBoth')
                continue
            elif atkType['name'] == 'SafetyPromotion5':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                targetSuit = self.battle.activeSuits[5]
                self.setSuitCondition(theSuit.doId, 'target6', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target5', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target4', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target3', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target2', 0, 0, 'setBoth')
                targetSuit.setManager(1)
                targetSuit.setHP(1000)
                targetSuit.setMaxHP(1000)
                self.setSuitCondition(targetSuit.doId, 'shielding', 1, 99, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'sued', 0, 0, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'suemovie', 0, 0, 'setBoth')
                if not self.suitHasCondition(targetSuit.doId, 'dead'):
                    self.setSuitCondition(theSuit.doId, 'promotioncalculator', 0, 0, 'setBoth')
                continue
            elif atkType['name'] == 'SafetyViolation':
                if self.toonHasCondition(toon.doId, 'banned'):
                    self.setToonCondition(toon.doId, 'banned', 1, 1, 'setBoth')
                    for s in self.battle.suits:
                        if s.dna.name == 'ubuster':
                            suit = s
                            currentBossHealth = s.currHP
                            if currentBossHealth >= 1:
                                self.setSuitCondition(suit.doId, 'breachgagban', 1, 10, 'setBoth')
                    result = 50
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'UnionBusterUnionDues':
                result = self.costsMultiplier
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'unionduescalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'UnionBusterUnionBusterDamage':
                for s in self.battle.suits:
                    if s.getManager():
                        self.setSuitCondition(theSuit.doId, 'dotfinished', 1, 1, 'setBoth')
                if self.toonHasCondition(toon.doId, 'busted'):
                    result = 25
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'UnionBusterUnionCalculator':
                result = self.costsCalculatorMultiplier
                toon.setHp(toon.hp + result)
                attack[SUIT_HP_COL][targetIndex] = result
                self.costsMultiplier += 4
                self.costsCalculatorMultiplier += 4
                self.setSuitCondition(theSuit.doId, 'unionduescalculationcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'unionduescalculator', 1, 10, 'setBoth')
            elif atkType['name'] == 'UnionBusterContractEnforcement':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'contractenforcementcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'unionbustcalculator', 1, 10, 'setBoth')
                for suit in self.battle.activeSuits:
                    self.setSuitCondition(suit.doId, 'contracted', 1, 99, 'setBoth')
                    self.setSuitCondition(suit.doId, 'sued', 0, 0, 'setBoth')
                    self.setSuitCondition(suit.doId, 'suemovie', 0, 0, 'setBoth')
                    currentBossHealth = -1
                    for s in self.battle.suits:
                        if s.dna.name == 'safesupervis':
                            currentBossHealth = s.currHP
                    if currentBossHealth >= 1:
                        if suit.currHP <= 0:
                            continue
                        x = (suit.maxHP * suit.hardMaxHP) - suit.currHP
                        if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
                            suit.setHP(suit.currHP + 0)
                        elif suit.currHP + 200 > (suit.maxHP * suit.hardMaxHP):
                            suit.setHP(suit.currHP + x)
                        else:
                            suit.setHP(suit.currHP + 200)
                        continue
                    elif currentBossHealth <= 0:
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
            elif atkType['name'] == 'UnionBusterUnionBust':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'unionbustcalculator', 0, 0, 'setBoth')
                for targetSuit in self.battle.activeSuits:
                    if not self.suitHasCondition(targetSuit.doId, 'contracted'):
                        self.setSuitCondition(theSuit.doId, 'unionwagescalculator', 1, 10, 'setBoth')
                        theSuit.setDamageMultiplier(theSuit.getDamageMultiplier() * 1.05)
                        theSuit.setHP(theSuit.currHP + 100)
                        targetSuit.setHP(math.ceil(targetSuit.currHP - targetSuit.currHP))
                        self.__removeLured(targetSuit.doId)
            elif atkType['name'] == 'UnionBusterUnionBuster':
                result = 35
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'busted', 1, 4, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'unionbustercalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'UnionBusterBreachOfContract':
                result = 30
                attack[SUIT_HP_COL][targetIndex] = result
                currentBossHealth = -1
                for s in self.battle.suits:
                    if s.dna.name == 'safesupervis':
                        currentBossHealth = s.currHP
                if currentBossHealth >= 1:
                    if self.getToonConditionModifier(toonId, 'allGagBoost') < -75:
                        self.setToonCondition(toon.doId, 'allGagBoost',
                                              self.getToonConditionModifier(toonId, 'allGagBoost'), 3, 'setBoth')
                        self.setToonCondition(toon.doId, 'lureBoost',
                                              self.getToonConditionModifier(toonId, 'lureBoost'), 3, 'setBoth')
                    else:
                        self.setToonCondition(toon.doId, 'allGagBoost', -75, 3, 'setBoth')
                        self.setToonCondition(toon.doId, 'lureBoost', -75, 3, 'setBoth')
                else:
                    if self.getToonConditionModifier(toonId, 'allGagBoost') < -50:
                        self.setToonCondition(toon.doId, 'allGagBoost',
                                              self.getToonConditionModifier(toonId, 'allGagBoost'), 3, 'setBoth')
                        self.setToonCondition(toon.doId, 'lureBoost',
                                              self.getToonConditionModifier(toonId, 'lureBoost'), 3, 'setBoth')
                    else:
                        self.setToonCondition(toon.doId, 'allGagBoost', -50, 3, 'setBoth')
                        self.setToonCondition(toon.doId, 'lureBoost', -50, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'breachcalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'UnionBusterBreachOfContract2':
                if self.toonHasCondition(toon.doId, 'soakToon'):
                    self.setToonCondition(toon.doId, 'soakToon', 0, 0, 'setBoth')
                    currentBossHealth = -1
                    for s in self.battle.suits:
                        if s.dna.name == 'safesupervis':
                            currentBossHealth = s.currHP
                    if currentBossHealth >= 1:
                        if self.getToonConditionModifier(toonId, 'allGagBoost') < -50:
                            self.setToonCondition(toon.doId, 'allGagBoost',
                                                  self.getToonConditionModifier(toonId, 'allGagBoost'), 3, 'setBoth')
                            self.setToonCondition(toon.doId, 'lureBoost',
                                                  self.getToonConditionModifier(toonId, 'lureBoost'), 3, 'setBoth')
                        else:
                            self.setToonCondition(toon.doId, 'allGagBoost', -50, 3, 'setBoth')
                            self.setToonCondition(toon.doId, 'lureBoost', -50, 3, 'setBoth')
                    else:
                        if self.getToonConditionModifier(toonId, 'allGagBoost') < -25:
                            self.setToonCondition(toon.doId, 'allGagBoost',
                                                  self.getToonConditionModifier(toonId, 'allGagBoost'), 3, 'setBoth')
                            self.setToonCondition(toon.doId, 'lureBoost',
                                                  self.getToonConditionModifier(toonId, 'lureBoost'), 3, 'setBoth')
                        else:
                            self.setToonCondition(toon.doId, 'allGagBoost', -25, 3, 'setBoth')
                            self.setToonCondition(toon.doId, 'lureBoost', -25, 3, 'setBoth')
                    result = 30
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'UnionBusterBreachOfContract3':
                if self.toonHasCondition(toon.doId, 'snapped'):
                    currentBossHealth = -1
                    for s in self.battle.suits:
                        if s.dna.name == 'safesupervis':
                            currentBossHealth = s.currHP
                    if currentBossHealth >= 1:
                        if self.getToonConditionModifier(toonId, 'allGagBoost') < -50:
                            self.setToonCondition(toon.doId, 'allGagBoost',
                                                  self.getToonConditionModifier(toonId, 'allGagBoost'), 3, 'setBoth')
                            self.setToonCondition(toon.doId, 'lureBoost',
                                                  self.getToonConditionModifier(toonId, 'lureBoost'), 3, 'setBoth')
                        else:
                            self.setToonCondition(toon.doId, 'allGagBoost', -50, 3, 'setBoth')
                            self.setToonCondition(toon.doId, 'lureBoost', -50, 3, 'setBoth')
                    else:
                        if self.getToonConditionModifier(toonId, 'allGagBoost') < -25:
                            self.setToonCondition(toon.doId, 'allGagBoost',
                                                  self.getToonConditionModifier(toonId, 'allGagBoost'), 3, 'setBoth')
                            self.setToonCondition(toon.doId, 'lureBoost',
                                                  self.getToonConditionModifier(toonId, 'lureBoost'), 3, 'setBoth')
                        else:
                            self.setToonCondition(toon.doId, 'allGagBoost', -25, 3, 'setBoth')
                            self.setToonCondition(toon.doId, 'lureBoost', -25, 3, 'setBoth')
                    result = 30
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'breachvulnerable', 0, 0, 'setBoth')
            elif atkType['name'] == 'UnionBusterBreachOfContract4':
                if self.toonHasCondition(toon.doId, 'banned'):
                    currentBossHealth = -1
                    for s in self.battle.suits:
                        if s.dna.name == 'safesupervis':
                            currentBossHealth = s.currHP
                    if currentBossHealth >= 1:
                        if self.getToonConditionModifier(toonId, 'allGagBoost') < -50:
                            self.setToonCondition(toon.doId, 'allGagBoost',
                                                  self.getToonConditionModifier(toonId, 'allGagBoost'), 3, 'setBoth')
                            self.setToonCondition(toon.doId, 'lureBoost',
                                                  self.getToonConditionModifier(toonId, 'lureBoost'), 3, 'setBoth')
                        else:
                            self.setToonCondition(toon.doId, 'allGagBoost', -50, 3, 'setBoth')
                            self.setToonCondition(toon.doId, 'lureBoost', -50, 3, 'setBoth')
                    else:
                        if self.getToonConditionModifier(toonId, 'allGagBoost') < -25:
                            self.setToonCondition(toon.doId, 'allGagBoost',
                                                  self.getToonConditionModifier(toonId, 'allGagBoost'), 3, 'setBoth')
                            self.setToonCondition(toon.doId, 'lureBoost',
                                                  self.getToonConditionModifier(toonId, 'lureBoost'), 3, 'setBoth')
                        else:
                            self.setToonCondition(toon.doId, 'allGagBoost', -25, 3, 'setBoth')
                            self.setToonCondition(toon.doId, 'lureBoost', -25, 3, 'setBoth')
                    result = 30
                elif self.toonHasCondition(toon.doId, 'banned2'):
                    currentBossHealth = -1
                    for s in self.battle.suits:
                        if s.dna.name == 'safesupervis':
                            currentBossHealth = s.currHP
                    if currentBossHealth >= 1:
                        if self.getToonConditionModifier(toonId, 'allGagBoost') < -50:
                            self.setToonCondition(toon.doId, 'allGagBoost',
                                                  self.getToonConditionModifier(toonId, 'allGagBoost'), 3, 'setBoth')
                            self.setToonCondition(toon.doId, 'lureBoost',
                                                  self.getToonConditionModifier(toonId, 'lureBoost'), 3, 'setBoth')
                        else:
                            self.setToonCondition(toon.doId, 'allGagBoost', -50, 3, 'setBoth')
                            self.setToonCondition(toon.doId, 'lureBoost', -50, 3, 'setBoth')
                    else:
                        if self.getToonConditionModifier(toonId, 'allGagBoost') < -25:
                            self.setToonCondition(toon.doId, 'allGagBoost',
                                                  self.getToonConditionModifier(toonId, 'allGagBoost'), 3, 'setBoth')
                            self.setToonCondition(toon.doId, 'lureBoost',
                                                  self.getToonConditionModifier(toonId, 'lureBoost'), 3, 'setBoth')
                        else:
                            self.setToonCondition(toon.doId, 'allGagBoost', -25, 3, 'setBoth')
                            self.setToonCondition(toon.doId, 'lureBoost', -25, 3, 'setBoth')
                    result = 30
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'breachgagban', 0, 0, 'setBoth')
            elif atkType['name'] == 'UnionBusterUnionWages':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'unionwagescalculator', 1, 1, 'setBoth')
            elif atkType['name'] == 'RacketeerProfiteering':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                targetSuit = self.battle.activeSuits[1]
                self.setSuitCondition(theSuit.doId, 'target6', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target5', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target4', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target3', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target2', 0, 0, 'setBoth')
                theSuit.setHP(math.ceil(theSuit.currHP + (targetSuit.maxHP / 4)))
                targetSuit.setHP(math.ceil(targetSuit.currHP - (targetSuit.maxHP / 4)))
                if targetSuit.currHP <= 0:
                    self.__removeLured(targetSuit.doId)
                if not self.suitHasCondition(targetSuit.doId, 'dead'):
                    self.setSuitCondition(theSuit.doId, 'profiteeringcalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'RacketeerProfiteering2':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                targetSuit = self.battle.activeSuits[2]
                self.setSuitCondition(theSuit.doId, 'target6', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target5', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target4', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target3', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target2', 0, 0, 'setBoth')
                theSuit.setHP(math.ceil(theSuit.currHP + (targetSuit.maxHP / 4)))
                targetSuit.setHP(math.ceil(targetSuit.currHP - (targetSuit.maxHP / 4)))
                if targetSuit.currHP <= 0:
                    self.__removeLured(targetSuit.doId)
                if not self.suitHasCondition(targetSuit.doId, 'dead'):
                    self.setSuitCondition(theSuit.doId, 'profiteeringcalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'RacketeerProfiteering3':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                targetSuit = self.battle.activeSuits[3]
                self.setSuitCondition(theSuit.doId, 'target6', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target5', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target4', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target3', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target2', 0, 0, 'setBoth')
                theSuit.setHP(math.ceil(theSuit.currHP + (targetSuit.maxHP / 4)))
                targetSuit.setHP(math.ceil(targetSuit.currHP - (targetSuit.maxHP / 4)))
                if targetSuit.currHP <= 0:
                    self.__removeLured(targetSuit.doId)
                if not self.suitHasCondition(targetSuit.doId, 'dead'):
                    self.setSuitCondition(theSuit.doId, 'profiteeringcalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'RacketeerProfiteering4':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                targetSuit = self.battle.activeSuits[4]
                self.setSuitCondition(theSuit.doId, 'target6', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target5', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target4', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target3', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target2', 0, 0, 'setBoth')
                theSuit.setHP(math.ceil(theSuit.currHP + (targetSuit.maxHP / 4)))
                targetSuit.setHP(math.ceil(targetSuit.currHP - (targetSuit.maxHP / 4)))
                if targetSuit.currHP <= 0:
                    self.__removeLured(targetSuit.doId)
                if not self.suitHasCondition(targetSuit.doId, 'dead'):
                    self.setSuitCondition(theSuit.doId, 'profiteeringcalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'RacketeerProfiteering5':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                targetSuit = self.battle.activeSuits[5]
                self.setSuitCondition(theSuit.doId, 'target6', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target5', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target4', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target3', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target2', 0, 0, 'setBoth')
                theSuit.setHP(math.ceil(theSuit.currHP + (targetSuit.maxHP / 4)))
                targetSuit.setHP(math.ceil(targetSuit.currHP - (targetSuit.maxHP / 4)))
                if targetSuit.currHP <= 0:
                    self.__removeLured(targetSuit.doId)
                if not self.suitHasCondition(targetSuit.doId, 'dead'):
                    self.setSuitCondition(theSuit.doId, 'profiteeringcalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'RacketeerExtortion':
                result = random.randint(20, 40)
                attack[SUIT_HP_COL][targetIndex] = result
                theSuit.setHP(math.ceil(theSuit.currHP + result))
                self.setSuitCondition(theSuit.doId, 'extortioncalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'RacketeerExtortion2':
                if not self.toonHasCondition(toon.doId, 'rushJobCompleted'):
                    result = random.randint(30, 50)
                    attack[SUIT_HP_COL][targetIndex] = result
                    theSuit.setHP(math.ceil(theSuit.currHP + (result * 2)))
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'extortioncalculator2', 0, 0, 'setBoth')
            elif atkType['name'] == 'RacketeerCompensation':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for suit in self.battle.activeSuits:
                    if suit.getHP() < suit.maxHP and not suit.dna.name == 'racket':
                        suit.setDamageMultiplier(suit.getDamageMultiplier() * 1.05)
                        self.setSuitCondition(suit.doId, 'lureResist', 1, 99, 'setBoth')
            elif atkType['name'] == 'RacketeerHustling':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'hustlingcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'extortioncalculator2', 1, 10, 'setBoth')
                for t in self.battle.activeToons:
                    self.setToonCondition(t, random.choice(
                        ('useToonUp','useTrap', 'useLure', 'useThrow', 'useSquirt', 'useZap', 'useSound', 'useDrop',)), 1, 2, 'setBoth')
            elif atkType['name'] == 'RacketeerRacketeering':
                if self.toonHasCondition(toon.doId, 'usedDrop'):
                    self.setToonCondition(toon.doId, 'noDropGags', 1, 2, 'setBoth')
                    self.setToonCondition(toon.doId, 'usedDrop', 1, 1, 'setBoth')
                if self.toonHasCondition(toon.doId, 'usedThrow'):
                    self.setToonCondition(toon.doId, 'noThrowGags', 1, 2, 'setBoth')
                    self.setToonCondition(toon.doId, 'usedThrow', 1, 1, 'setBoth')
                if self.toonHasCondition(toon.doId, 'usedSquirt'):
                    self.setToonCondition(toon.doId, 'noSquirtGags', 1, 2, 'setBoth')
                    self.setToonCondition(toon.doId, 'usedSquirt', 1, 1, 'setBoth')
                if self.toonHasCondition(toon.doId, 'usedSound'):
                    self.setToonCondition(toon.doId, 'noSoundGags', 1, 2, 'setBoth')
                    self.setToonCondition(toon.doId, 'usedSound', 1, 1, 'setBoth')
                if self.toonHasCondition(toon.doId, 'usedTrap'):
                    self.setToonCondition(toon.doId, 'noTrapGags', 1, 2, 'setBoth')
                    self.setToonCondition(toon.doId, 'usedTrap', 1, 1, 'setBoth')
                if self.toonHasCondition(toon.doId, 'usedLure'):
                    self.setToonCondition(toon.doId, 'noLureGags', 1, 2, 'setBoth')
                    self.setToonCondition(toon.doId, 'usedLure', 1, 1, 'setBoth')
                if self.toonHasCondition(toon.doId, 'usedHeal'):
                    self.setToonCondition(toon.doId, 'noToonUpGags', 1, 2, 'setBoth')
                    self.setToonCondition(toon.doId, 'usedHeal', 1, 1, 'setBoth')
                if self.toonHasCondition(toon.doId, 'usedZap'):
                    self.setToonCondition(toon.doId, 'noZapGags', 1, 2, 'setBoth')
                    self.setToonCondition(toon.doId, 'usedZap', 1, 1, 'setBoth')
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'RacketeerPeckingOrderRetaliation':
                if self.toonHasCondition(toon.doId, 'banned'):
                    result = 45
                elif self.toonHasCondition(toon.doId, 'banned2'):
                    result = 45
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'RacketeerPeckingOrderRetaliationSoak':
                result = 45
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'RadiographerRadioInfrequency':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'groupDamageDown', -50, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'radioinfrequencycalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'RadiographerHotTake':
                result = 23
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'snapped', 1.50, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'hottakecalculator', 0, 0, 'setBoth')
                theSuit.setHP(math.ceil(theSuit.currHP - (result * 4)))
                attack[SUIT_HP_COL][targetIndex] = result
                for s in self.battle.suits:
                    if s.dna.name == 'phouse':
                        suit = s
                        currentBossHealth = s.currHP
                        if currentBossHealth >= 1:
                            self.setSuitCondition(suit.doId, 'breachvulnerable', 1, 10, 'setBoth')
            elif atkType['name'] == 'RadiographerHotTakeRetaliation':
                result = 36
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'soakedcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'soakedcalculator2', 1, 10, 'setBoth')
                self.setToonCondition(toon.doId, 'snapped', 1.25, 3, 'setBoth')
                theSuit.setHP(math.ceil(theSuit.currHP - (result * 4)))
                for s in self.battle.suits:
                    if s.dna.name == 'ubuster':
                        suit = s
                        currentBossHealth = s.currHP
                        if currentBossHealth >= 1:
                            self.setSuitCondition(suit.doId, 'breachvulnerable', 1, 10, 'setBoth')
            elif atkType['name'] == 'RadiographerDanceSession':
                result = 0
                self.setSuitCondition(theSuit.doId, 'dancesession', 1, 4, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'dancesessioncalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'RadiographerOvermodulated':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                targetSuit = self.battle.activeSuits[1]
                self.setSuitCondition(theSuit.doId, 'target6', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target5', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target4', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target3', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target2', 0, 0, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'bellowattack', 1, 1, 'setBoth')
                if self.suitHasCondition(targetSuit.doId, 'sued'):
                    self.setSuitCondition(targetSuit.doId, 'sued', 1, 1, 'setBoth')
                if not self.suitHasCondition(targetSuit.doId, 'dead'):
                    self.setSuitCondition(theSuit.doId, 'overmodulatedcalculator', 0, 0, 'setBoth')
                if not self.suitHasCondition(targetSuit.doId, 'extraAttack'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack') and not self.suitHasCondition(targetSuit.doId, 'extraAttack2'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack2', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack2') and not self.suitHasCondition(targetSuit.doId, 'extraAttack3'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack3', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack3') and not self.suitHasCondition(targetSuit.doId, 'extraAttack4'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack4', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack4') and not self.suitHasCondition(targetSuit.doId, 'extraAttack5'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack5', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack5') and not self.suitHasCondition(targetSuit.doId, 'extraAttack6'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack6', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack6') and not self.suitHasCondition(targetSuit.doId, 'extraAttack7'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack7', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack7') and not self.suitHasCondition(targetSuit.doId, 'extraAttack8'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack8', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack8') and not self.suitHasCondition(targetSuit.doId, 'extraAttack9'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack9', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack9') and not self.suitHasCondition(targetSuit.doId, 'extraAttack10'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack10', 1, 99, 'setBoth')
                self.__removeLured(targetSuit.doId)
            elif atkType['name'] == 'RadiographerOvermodulated2':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                targetSuit = self.battle.activeSuits[2]
                self.setSuitCondition(theSuit.doId, 'target6', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target5', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target4', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target3', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target2', 0, 0, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'bellowattack', 1, 1, 'setBoth')
                if self.suitHasCondition(targetSuit.doId, 'sued'):
                    self.setSuitCondition(targetSuit.doId, 'sued', 1, 1, 'setBoth')
                if not self.suitHasCondition(targetSuit.doId, 'dead'):
                    self.setSuitCondition(theSuit.doId, 'overmodulatedcalculator', 0, 0, 'setBoth')
                if not self.suitHasCondition(targetSuit.doId, 'extraAttack'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack2'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack2', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack2') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack3'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack3', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack3') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack4'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack4', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack4') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack5'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack5', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack5') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack6'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack6', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack6') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack7'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack7', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack7') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack8'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack8', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack8') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack9'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack9', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack9') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack10'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack10', 1, 99, 'setBoth')
                self.__removeLured(targetSuit.doId)
            elif atkType['name'] == 'RadiographerOvermodulated3':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                targetSuit = self.battle.activeSuits[3]
                self.setSuitCondition(theSuit.doId, 'target6', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target5', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target4', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target3', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target2', 0, 0, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'bellowattack', 1, 1, 'setBoth')
                if self.suitHasCondition(targetSuit.doId, 'sued'):
                    self.setSuitCondition(targetSuit.doId, 'sued', 1, 1, 'setBoth')
                if not self.suitHasCondition(targetSuit.doId, 'dead'):
                    self.setSuitCondition(theSuit.doId, 'overmodulatedcalculator', 0, 0, 'setBoth')
                if not self.suitHasCondition(targetSuit.doId, 'extraAttack'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack2'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack2', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack2') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack3'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack3', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack3') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack4'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack4', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack4') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack5'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack5', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack5') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack6'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack6', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack6') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack7'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack7', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack7') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack8'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack8', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack8') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack9'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack9', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack9') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack10'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack10', 1, 99, 'setBoth')
                self.__removeLured(targetSuit.doId)
            elif atkType['name'] == 'RadiographerOvermodulated4':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                targetSuit = self.battle.activeSuits[4]
                self.setSuitCondition(theSuit.doId, 'target6', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target5', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target4', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target3', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target2', 0, 0, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'bellowattack', 1, 1, 'setBoth')
                if self.suitHasCondition(targetSuit.doId, 'sued'):
                    self.setSuitCondition(targetSuit.doId, 'sued', 1, 1, 'setBoth')
                if not self.suitHasCondition(targetSuit.doId, 'dead'):
                    self.setSuitCondition(theSuit.doId, 'overmodulatedcalculator', 0, 0, 'setBoth')
                if not self.suitHasCondition(targetSuit.doId, 'extraAttack'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack2'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack2', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack2') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack3'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack3', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack3') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack4'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack4', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack4') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack5'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack5', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack5') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack6'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack6', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack6') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack7'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack7', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack7') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack8'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack8', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack8') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack9'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack9', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack9') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack10'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack10', 1, 99, 'setBoth')
                self.__removeLured(targetSuit.doId)
            elif atkType['name'] == 'RadiographerOvermodulated5':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                targetSuit = self.battle.activeSuits[5]
                self.setSuitCondition(theSuit.doId, 'target6', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target5', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target4', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target3', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target2', 0, 0, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'bellowattack', 1, 1, 'setBoth')
                if self.suitHasCondition(targetSuit.doId, 'sued'):
                    self.setSuitCondition(targetSuit.doId, 'sued', 1, 1, 'setBoth')
                if not self.suitHasCondition(targetSuit.doId, 'dead'):
                    self.setSuitCondition(theSuit.doId, 'overmodulatedcalculator', 0, 0, 'setBoth')
                if not self.suitHasCondition(targetSuit.doId, 'extraAttack'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack2'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack2', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack2') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack3'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack3', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack3') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack4'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack4', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack4') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack5'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack5', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack5') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack6'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack6', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack6') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack7'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack7', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack7') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack8'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack8', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack8') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack9'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack9', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack9') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack10'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack10', 1, 99, 'setBoth')
                self.__removeLured(targetSuit.doId)
            elif atkType['name'] == 'HighRollerCheerRetaliation':
                if self.toonHasCondition(toon.doId, 'cheer'):
                    result = 35
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'HighRollerSingingBlues':
                result = 20
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'winded', -50, 2, 'setBoth')
            elif atkType['name'] == 'HighRollerSyphon':
                result = random.randint(20, 40)
                attack[SUIT_HP_COL][targetIndex] = result
                theSuit.setHP(math.ceil(theSuit.currHP + attack[SUIT_HP_COL][
                    targetIndex]))
            elif atkType['name'] == 'HighRollerBar':
                result = 50
                attack[SUIT_HP_COL][targetIndex] = result
                self.__removeLured(theSuit.doId)
                for suit in self.battle.activeSuits:
                    if suit.dna.name == 'hroller2':
                        suit.setHP(math.ceil(suit.currHP - 25))
                        if suit.getHP() <= 0:
                            self.setSuitCondition(suit.doId, 'deathcheck', 1, 1, 'setBoth')
                            self.__removeLured(suit.doId)
                    else:
                        suit.setHP(math.ceil(suit.currHP - 250))
                        if suit.getHP() <= 0:
                            self.setSuitCondition(suit.doId, 'deathcheck', 1, 1, 'setBoth')
                            self.__removeLured(suit.doId)
                    continue
            elif atkType['name'] == 'HighRollerDiceRouletteEveryone':
                result = 35
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'immune', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'HRdamagereduction', 1, 99, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'HRdiceroulette', 1, 1, 'setBoth')
                for suit in self.battle.activeSuits:
                    if suit.dna.name == 'hroller2':
                        suit.setHP(math.ceil(suit.currHP - 25))
                        if suit.getHP() <= 0:
                            self.setSuitCondition(suit.doId, 'deathcheck', 1, 1, 'setBoth')
                            self.__removeLured(suit.doId)
                    else:
                        suit.setHP(math.ceil(suit.currHP - 250))
                        if suit.getHP() <= 0:
                            self.setSuitCondition(suit.doId, 'deathcheck', 1, 1, 'setBoth')
                            self.__removeLured(suit.doId)
                    if self.suitHasCondition(suit.doId, 'lured'):
                        self.setSuitCondition(suit.doId, 'lured', 0, 0, 'setBoth')
                    continue
            elif atkType['name'] == 'HighRollerDiceRouletteCogs':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'immune', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'HRdamagereduction', 1, 99, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'HRdiceroulette', 1, 1, 'setBoth')
                for suit in self.battle.activeSuits:
                    if suit.dna.name == 'hroller2':
                        suit.setHP(math.ceil(suit.currHP - 25))
                        if suit.getHP() <= 0:
                            self.setSuitCondition(suit.doId, 'deathcheck', 1, 1, 'setBoth')
                            self.__removeLured(suit.doId)
                    else:
                        suit.setHP(math.ceil(suit.currHP - 250))
                        if suit.getHP() <= 0:
                            self.setSuitCondition(suit.doId, 'deathcheck', 1, 1, 'setBoth')
                            self.__removeLured(suit.doId)
                    if self.suitHasCondition(suit.doId, 'lured'):
                        self.setSuitCondition(suit.doId, 'lured', 0, 0, 'setBoth')
                    continue
            elif atkType['name'] == 'HighRollerDiceRouletteNobody':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'immune', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'HRdamagereduction', 1, 99, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'HRdiceroulette', 1, 1, 'setBoth')
            elif atkType['name'] == 'HighRollerDiceRouletteToons':
                result = random.choice((0, 35))
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'immune', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'HRdamagereduction', 1, 99, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'HRdiceroulette', 1, 1, 'setBoth')
            elif atkType['name'] == 'HighRollerDonation':
                managerTarget = None
                for suit in self.battle.activeSuits:
                    if self.battle.findSuit(suit.doId).getManager() and not suit.dna.name == 'hrollers':
                        managerTarget = suit
                    if managerTarget == None:
                        managerTarget = theSuit
                if theSuit.currHP < 3000:
                    managerTarget.setHP(managerTarget.getHP() + theSuit.currHP)
                    theSuit.setHP(math.ceil(theSuit.currHP - theSuit.currHP))
                    if theSuit.getHP() <= 0:
                        self.setSuitCondition(theSuit.doId, 'deathcheck', 1, 1, 'setBoth')
                else:
                    managerTarget.setHP(managerTarget.getHP() + 3000)
                    theSuit.setHP(math.ceil(theSuit.currHP - 3000))
            elif atkType['name'] == 'HighRollerSplashback':
                if self.toonHasCondition(toon.doId, 'soakToon'):
                    self.setToonCondition(toon.doId, 'soakToon', 0, 0, 'setBoth')
                    result = 25
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'HighRollerBust':
                if self.toonHasCondition(toon.doId, 'banned') or self.toonHasCondition(toon.doId, 'banned2'):
                    self.setToonCondition(toon.doId, 'banned2', 1, 1, 'setBoth')
                    self.setToonCondition(toon.doId, 'banned', 1, 1, 'setBoth')
                    result = 25
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'HighRollerCommercialBreak':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for suit in self.battle.activeSuits:
                    if suit.currHP <= 0:
                        continue
                    if not suit.dna.name == 'hroller':
                        suit.setHP(suit.currHP - suit.currHP)
                    self.setSuitCondition(suit.doId, 'killedbyroller', 1, 2, 'setBoth')
                    if self.suitHasCondition(suit.doId, 'lured'):
                        self.setSuitCondition(suit.doId, 'lured', 0, 0, 'setBoth')
                    continue
                for suit in self.currentlyLuredSuits.keys():
                    self.__removeLured(suit)
            elif atkType['name'] == 'HighRollerDamageReduction':
                result = 25
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'lureBoost', -50, 2, 'setBoth')
                self.setToonCondition(toon.doId, 'throwBoost', -50, 2, 'setBoth')
                self.setToonCondition(toon.doId, 'dropBoost', -50, 2, 'setBoth')
                self.setToonCondition(toon.doId, 'zapBoost', -50, 2, 'setBoth')
                self.setToonCondition(toon.doId, 'healBoost', -50, 2, 'setBoth')
                self.setToonCondition(toon.doId, 'squirtBoost', -50, 2, 'setBoth')
                self.setToonCondition(toon.doId, 'trapBoost', -50, 2, 'setBoth')
                self.setToonCondition(toon.doId, 'soundBoost', -50, 2, 'setBoth')
            elif atkType['name'] == 'HighRollerWheelSpin':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'HighRollerPuzzleBan':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'nolevel8s', 1, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel6s', 1, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel7s', 1, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel5s', 1, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel4s', 1, 0, 'setBoth')
                    self.setToonCondition(t, random.choice(('nolevel5s', 'nolevel7s', 'nolevel4s', 'nolevel6s', 'nolevel8s')), 1, 2, 'setBoth')
                    self.setToonCondition(t, 'noSquirtGags', 1, 0, 'setBoth')
                    self.setToonCondition(t, 'noThrowGags', 1, 0, 'setBoth')
                    self.setToonCondition(t, 'noLureGags', 1, 0, 'setBoth')
                    self.setToonCondition(t, 'noDropGags', 1, 0, 'setBoth')
                    self.setToonCondition(t, 'noToonUpGags', 1, 0, 'setBoth')
                    self.setToonCondition(t, 'noTrapGags', 1, 0, 'setBoth')
                    self.setToonCondition(t, 'noZapGags', 1, 0, 'setBoth')
                    self.setToonCondition(t, 'noSoundGags', 1, 0, 'setBoth')
                    self.setToonCondition(t, random.choice(('noSquirtGags', 'noSoundGags', 'noToonUpGags', 'noLureGags')), 1, 2, 'setBoth')
            elif atkType['name'] == 'HighRollerNoAttack':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                if theSuit.dna.name == 'hroller2':
                    for t in self.battle.activeToons:
                        self.setToonCondition(t, 'nolevel8s', 1, 0, 'setBoth')
                        self.setToonCondition(t, 'nolevel6s', 1, 0, 'setBoth')
                        self.setToonCondition(t, 'nolevel7s', 1, 0, 'setBoth')
                        self.setToonCondition(t, 'nolevel5s', 1, 0, 'setBoth')
                        self.setToonCondition(t, 'nolevel4s', 1, 0, 'setBoth')
                        self.setToonCondition(t, random.choice(('nolevel5s', 'nolevel7s', 'nolevel4s', 'nolevel6s', 'nolevel8s')), 1, 2, 'setBoth')
                        self.setToonCondition(t, 'noSquirtGags', 1, 0, 'setBoth')
                        self.setToonCondition(t, 'noThrowGags', 1, 0, 'setBoth')
                        self.setToonCondition(t, 'noLureGags', 1, 0, 'setBoth')
                        self.setToonCondition(t, 'noDropGags', 1, 0, 'setBoth')
                        self.setToonCondition(t, 'noToonUpGags', 1, 0, 'setBoth')
                        self.setToonCondition(t, 'noTrapGags', 1, 0, 'setBoth')
                        self.setToonCondition(t, 'noZapGags', 1, 0, 'setBoth')
                        self.setToonCondition(t, 'noSoundGags', 1, 0, 'setBoth')
                        self.setToonCondition(t, random.choice(('noSquirtGags', 'noSoundGags', 'noToonUpGags', 'noLureGags')), 1, 2, 'setBoth')
            elif atkType['name'] == 'HighRollerGameTimeSpawn':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'spawncalculator', 1, 1, 'setBoth')
                from toontown.suit.DistributedCashbotBossAI import DistributedCashbotBossAI

                boss = None
                for do in simbase.air.doId2do.values():
                    if isinstance(do, DistributedCashbotBossAI):
                        for toon in self.battle.activeToons:
                            if toon in do.involvedToons:
                                boss = do
                                break
                        for t in self.battle.activeToons:
                            if t in do.involvedToons:
                                boss.appendSuitsToBattle(boss.battleNumber, 'crf1')
            elif atkType['name'] == 'HighRollerPuzzle':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'gameovercalculator', 1, 10, 'setBoth')
                for t in self.battle.activeToons:
                    self.setToonCondition(t, random.choice(
                        ('useToonUp','useTrap', 'useLure', 'useThrow', 'useSquirt', 'useZap', 'useSound', 'useDrop',)), 1, 2, 'setBoth')
            elif atkType['name'] == 'HighRollerGameOver':
                if not self.toonHasCondition(toon.doId, 'rushJobCompleted'):
                    result = 35
                    attack[SUIT_HP_COL][targetIndex] = result
                else:
                    result = 0
                    attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'gameovercalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'HighRollerGameTimeCog':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'gametimecalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target6', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target5', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target4', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target3', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target2', 0, 0, 'setBoth')
                targetSuit = self.battle.activeSuits[1]
                x = (targetSuit.maxHP * targetSuit.hardMaxHP) - targetSuit.currHP
                targetSuit.setHP(math.ceil(targetSuit.currHP + x))
                if not self.suitHasCondition(targetSuit.doId, 'extraAttack'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack2'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack2', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack2') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack3'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack3', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack3') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack4'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack4', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack4') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack5'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack5', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack5') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack6'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack6', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack6') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack7'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack7', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack7') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack8'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack8', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack8') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack9'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack9', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack9') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack10'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack10', 1, 99, 'setBoth')
                self.__removeLured(targetSuit.doId)
                self.setSuitCondition(targetSuit.doId, 'bellowattack', 1, 1, 'setBoth')
            elif atkType['name'] == 'HighRollerGameTimeCog2':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'gametimecalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target6', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target5', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target4', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target3', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target2', 0, 0, 'setBoth')
                targetSuit = self.battle.activeSuits[1]
                targetSuit.setHP(0)
                self.setSuitCondition(targetSuit.doId, 'killedbyroller', 1, 2, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'lured', 0, 0, 'setBoth')
                self.__removeLured(targetSuit.doId)
            elif atkType['name'] == 'HighRollerGameTimeCog3':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'gametimecalculator', 0, 0, 'setBoth')
                targetSuit = self.battle.activeSuits[2]
                x = (targetSuit.maxHP * targetSuit.hardMaxHP) - targetSuit.currHP
                targetSuit.setHP(math.ceil(targetSuit.currHP + x))
                if not self.suitHasCondition(targetSuit.doId, 'extraAttack'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack2'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack2', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack2') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack3'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack3', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack3') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack4'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack4', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack4') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack5'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack5', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack5') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack6'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack6', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack6') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack7'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack7', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack7') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack8'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack8', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack8') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack9'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack9', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack9') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack10'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack10', 1, 99, 'setBoth')
                self.__removeLured(targetSuit.doId)
                self.setSuitCondition(targetSuit.doId, 'bellowattack', 1, 1, 'setBoth')
            elif atkType['name'] == 'HighRollerGameTimeCog4':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'gametimecalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target6', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target5', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target4', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target3', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target2', 0, 0, 'setBoth')
                targetSuit = self.battle.activeSuits[2]
                targetSuit.setHP(0)
                self.setSuitCondition(targetSuit.doId, 'killedbyroller', 1, 2, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'lured', 0, 0, 'setBoth')
                self.__removeLured(targetSuit.doId)
            elif atkType['name'] == 'HighRollerGameTimeCog5':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'gametimecalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target6', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target5', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target4', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target3', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target2', 0, 0, 'setBoth')
                targetSuit = self.battle.activeSuits[3]
                x = (targetSuit.maxHP * targetSuit.hardMaxHP) - targetSuit.currHP
                targetSuit.setHP(math.ceil(targetSuit.currHP + x))
                if not self.suitHasCondition(targetSuit.doId, 'extraAttack'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack2'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack2', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack2') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack3'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack3', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack3') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack4'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack4', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack4') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack5'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack5', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack5') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack6'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack6', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack6') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack7'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack7', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack7') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack8'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack8', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack8') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack9'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack9', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack9') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack10'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack10', 1, 99, 'setBoth')
                self.__removeLured(targetSuit.doId)
                self.setSuitCondition(targetSuit.doId, 'bellowattack', 1, 1, 'setBoth')
            elif atkType['name'] == 'HighRollerGameTimeCog6':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'gametimecalculator', 0, 0, 'setBoth')
                targetSuit = self.battle.activeSuits[3]
                targetSuit.setHP(0)
                self.setSuitCondition(targetSuit.doId, 'killedbyroller', 1, 2, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target6', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target5', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target4', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target3', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target2', 0, 0, 'setBoth')
                self.__removeLured(targetSuit.doId)
                self.setSuitCondition(targetSuit.doId, 'lured', 0, 0, 'setBoth')
            elif atkType['name'] == 'HighRollerGameTimeCog7':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'gametimecalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target6', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target5', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target4', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target3', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target2', 0, 0, 'setBoth')
                targetSuit = self.battle.activeSuits[4]
                x = (targetSuit.maxHP * targetSuit.hardMaxHP) - targetSuit.currHP
                targetSuit.setHP(math.ceil(targetSuit.currHP + x))
                if not self.suitHasCondition(targetSuit.doId, 'extraAttack'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack2'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack2', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack2') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack3'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack3', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack3') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack4'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack4', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack4') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack5'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack5', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack5') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack6'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack6', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack6') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack7'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack7', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack7') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack8'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack8', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack8') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack9'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack9', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack9') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack10'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack10', 1, 99, 'setBoth')
                self.__removeLured(targetSuit.doId)
                self.setSuitCondition(targetSuit.doId, 'bellowattack', 1, 1, 'setBoth')
            elif atkType['name'] == 'HighRollerGameTimeCog8':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                targetSuit = self.battle.activeSuits[4]
                targetSuit.setHP(0)
                self.setSuitCondition(targetSuit.doId, 'killedbyroller', 1, 2, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'gametimecalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target6', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target5', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target4', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target3', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target2', 0, 0, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'lured', 0, 0, 'setBoth')
                self.__removeLured(targetSuit.doId)
            elif atkType['name'] == 'HighRollerGameTimeCog9':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'gametimecalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target6', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target5', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target4', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target3', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target2', 0, 0, 'setBoth')
                targetSuit = self.battle.activeSuits[5]
                x = (targetSuit.maxHP * targetSuit.hardMaxHP) - targetSuit.currHP
                targetSuit.setHP(math.ceil(targetSuit.currHP + x))
                if not self.suitHasCondition(targetSuit.doId, 'extraAttack'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack2'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack2', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack2') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack3'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack3', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack3') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack4'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack4', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack4') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack5'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack5', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack5') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack6'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack6', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack6') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack7'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack7', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack7') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack8'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack8', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack8') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack9'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack9', 1, 99, 'setBoth')
                elif self.suitHasCondition(targetSuit.doId, 'extraAttack9') and not self.suitHasCondition(
                        targetSuit.doId, 'extraAttack10'):
                    self.setSuitCondition(targetSuit.doId, 'extraAttack10', 1, 99, 'setBoth')
                self.__removeLured(targetSuit.doId)
                self.setSuitCondition(targetSuit.doId, 'bellowattack', 1, 1, 'setBoth')
            elif atkType['name'] == 'HighRollerGameTimeCog10':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'gametimecalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target6', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target5', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target4', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target3', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target2', 0, 0, 'setBoth')
                targetSuit = self.battle.activeSuits[5]
                targetSuit.setHP(0)
                self.setSuitCondition(targetSuit.doId, 'killedbyroller', 1, 2, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'lured', 0, 0, 'setBoth')
                self.__removeLured(targetSuit.doId)
            elif atkType['name'] == 'PowerTrip' and theSuit.dna.name == 'hrollers':
                for suit in self.battle.activeSuits:
                    self.setSuitCondition(suit.doId, 'HRpowertrip', 1, 1, 'setBoth')
            elif atkType['name'] == 'HighRollerTrickOfTheLight':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                #self.setToonCondition(toon.doId, 'silhouettespawn', 1, 99, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'bashcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'vulnerable', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'trickofthelight', 1, 2, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'immune', 1, 2, 'setBoth')
                if self.suitHasCondition(theSuit.doId, 'firsttrick') and self.getSuitConditionTurns(
                        theSuit.doId,
                        'firsttrick') < 97 and not self.suitHasCondition(theSuit.doId, 'secondtrick'):
                    self.setSuitCondition(theSuit.doId, 'secondtrick', 1, 99, 'setBoth')
                if self.suitHasCondition(theSuit.doId, 'secondtrick') and self.getSuitConditionTurns(
                        theSuit.doId,
                        'secondtrick') < 97 and not self.suitHasCondition(theSuit.doId, 'thirdtrick'):
                    self.setSuitCondition(theSuit.doId, 'thirdtrick', 1, 99, 'setBoth')
                if self.suitHasCondition(theSuit.doId, 'thirdtrick') and self.getSuitConditionTurns(
                        theSuit.doId,
                        'thirdtrick') < 97 and not self.suitHasCondition(theSuit.doId, 'fourthtruck'):
                    self.setSuitCondition(theSuit.doId, 'fourthtrick', 1, 99, 'setBoth')
                else:
                    self.setSuitCondition(theSuit.doId, 'firsttrick', 1, 99, 'setBoth')
                from toontown.suit.DistributedCashbotBossAI import DistributedCashbotBossAI

                boss = None
                for do in simbase.air.doId2do.values():
                    if isinstance(do, DistributedCashbotBossAI):
                        for toon in self.battle.activeToons:
                            if toon in do.involvedToons:
                                boss = do
                                break
                        for t in self.battle.activeToons:
                            if t in do.involvedToons:
                                if self.toonHasCondition(t, 'silhouettespawn'):
                                    boss.appendSuitsToBattle(boss.battleNumber, 'sil1')
                                    boss.appendSuitsToBattle(boss.battleNumber, 'sil2')
                                    boss.appendSuitsToBattle(boss.battleNumber, 'sil4')
                                    boss.appendSuitsToBattle(boss.battleNumber, 'sil3')
                                    boss.appendSuitsToBattle(boss.battleNumber, 'sil5')
            elif atkType['name'] == 'HighRollerPhase3':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'bashcalculator', 1, 10, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'phase3', 1, 99, 'setBoth')
            elif atkType['name'] == 'HighRollerRaisingTheAnte':
                result = 25
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'phase3', 1, 99, 'setBoth')
                self.setToonCondition(toon.doId, 'raisedAnte', 1250, 99, 'setBoth')
            elif atkType['name'] == 'HighRollerConduction':
                result = 40
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'HRconduction', 1, 1, 'setBoth')
            elif atkType['name'] == 'HighRollerRolled':
                result = random.randint(25, 50)
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'HRrolled', 1, 1, 'setBoth')
            elif atkType['name'] == 'HighRollerFreeCruise':
                result = 35
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'HRfreecruise', 1, 1, 'setBoth')
            elif atkType['name'] == 'HighRollerVulnerable':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'vulnerable', 1, 10, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'phase3', 1, 99, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'HRdamagereduction', 0, 0, 'setBoth')
            elif atkType['name'] == 'HighRollerAceInTheHole':
                result = 33
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'aceInTheHole', 1, 99, 'setBoth')
                if self.getToonConditionModifier(toonId, 'snapped') > 1.15:
                    self.setToonCondition(toon.doId, 'snapped', self.getToonConditionModifier(toonId, 'snapped'), 99, 'setBoth')
                else:
                    self.setToonCondition(toon.doId, 'snapped', 1.15, 99, 'setBoth')
            elif atkType['name'] == 'VideographerRisingStars':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                if not self.suitHasCondition(theSuit.doId, 'silspawn'):
                    self.setToonCondition(toon.doId, 'silhouettespawn', 1, 99, 'setBoth')
                    self.setSuitCondition(theSuit.doId, 'silspawn', 1, 99, 'setBoth')
                from toontown.suit.DistributedCashbotBossAI import DistributedCashbotBossAI

                boss = None
                for do in simbase.air.doId2do.values():
                    if isinstance(do, DistributedCashbotBossAI):
                        for toon in self.battle.activeToons:
                            if toon in do.involvedToons:
                                boss = do
                                break
                        for t in self.battle.activeToons:
                            if t in do.involvedToons:
                                if self.toonHasCondition(t, 'silhouettespawn'):
                                    boss.appendSuitsToBattle(boss.battleNumber, 'videog')
            elif atkType['name'] == 'VideographerRisingStars2':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                from toontown.suit.DistributedCashbotBossAI import DistributedCashbotBossAI

                boss = None
                for do in simbase.air.doId2do.values():
                    if isinstance(do, DistributedCashbotBossAI):
                        for toon in self.battle.activeToons:
                            if toon in do.involvedToons:
                                boss = do
                                break
                        for t in self.battle.activeToons:
                            if t in do.involvedToons:
                                if self.toonHasCondition(t, 'silhouettespawn'):
                                    boss.appendSuitsToBattle(boss.battleNumber, 'videog2')
            elif atkType['name'] == 'VideographerDirectorCuts':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'phase3', 1, 99, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'immune', 1, 99, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'directorscutscalculator', 1, 2, 'setBoth')
                for suit in self.battle.activeSuits:
                    if suit.dna.name == 'mh2':
                        managerTarget = suit
                        if managerTarget.currHP <= 0:
                            continue
                        if managerTarget == None:
                            continue
                        managerTarget.setHP(0)
                        self.__removeLured(managerTarget.doId)
                    if suit.dna.name == 'std2':
                        managerTarget = suit
                        if managerTarget.currHP <= 0:
                            continue
                        if managerTarget == None:
                            continue
                        managerTarget.setHP(0)
                        self.__removeLured(managerTarget.doId)
                from toontown.suit.DistributedCashbotBossAI import DistributedCashbotBossAI

                boss = None
                for do in simbase.air.doId2do.values():
                    if isinstance(do, DistributedCashbotBossAI):
                        for toon in self.battle.activeToons:
                            if toon in do.involvedToons:
                                boss = do
                                break
                        for t in self.battle.activeToons:
                            if t in do.involvedToons:
                                if self.toonHasCondition(t, 'silhouettespawn'):
                                    boss.appendSuitsToBattle(boss.battleNumber, 'fmaker')
                                    boss.appendSuitsToBattle(boss.battleNumber, 'cinema')
                                    boss.appendSuitsToBattle(boss.battleNumber, 'director')
                                    boss.appendSuitsToBattle(boss.battleNumber, 'choreo')
            elif atkType['name'] == 'VideographerRisingStarsSilhouette':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                from toontown.suit.DistributedCashbotBossAI import DistributedCashbotBossAI

                boss = None
                for do in simbase.air.doId2do.values():
                    if isinstance(do, DistributedCashbotBossAI):
                        for toon in self.battle.activeToons:
                            if toon in do.involvedToons:
                                boss = do
                                break
                        for t in self.battle.activeToons:
                            if t in do.involvedToons:
                                if self.toonHasCondition(t, 'silhouettespawn'):
                                    boss.appendSuitsToBattle(boss.battleNumber, 'videog4')
            elif atkType['name'] == 'VideographerDeath':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for suit in self.battle.activeSuits:
                    if not suit.dna.name == 'hroller2' and not suit.dna.name == 'videog':
                        managerTarget = suit
                        if managerTarget.currHP <= 0:
                            continue
                        if managerTarget == None:
                            continue
                        self.setSuitCondition(managerTarget.doId, 'killedbyvideo', 1, 2, 'setBoth')
                        managerTarget.setHP(0)
                        self.__removeLured(managerTarget.doId)
            elif atkType['name'] == 'VideographerVideoStatic':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                managerTarget = None
                for suit in self.battle.activeSuits:
                    if suit.dna.name == 'videog':
                        managerTarget = suit
                        if managerTarget == None:
                            continue
                        self.setSuitCondition(managerTarget.doId, 'vulnerable', 1, 99, 'setBoth')
                        #self.setSuitCondition(managerTarget.doId, 'vulnerablevideographer', 1, 99, 'setBoth')
                        if theSuit.dna.name == 'bcaster':
                            if not self.suitHasCondition(managerTarget.doId, 'vulnerablevideographer'):
                                self.setSuitCondition(managerTarget.doId, 'vulnerablevideographer', 25, 99, 'setBoth')
                            else:
                                self.setSuitCondition(managerTarget.doId, 'vulnerablevideographer', (self.getSuitConditionModifier(managerTarget.doId, 'vulnerablevideographer') + 25), 99, 'setBoth')
                            managerTarget.setDamageMultiplier(managerTarget.getDamageMultiplier() * 1.25)
                        if theSuit.dna.name == 'director':
                            if not self.suitHasCondition(managerTarget.doId, 'vulnerablevideographer'):
                                self.setSuitCondition(managerTarget.doId, 'vulnerablevideographer', 11, 99, 'setBoth')
                            else:
                                self.setSuitCondition(managerTarget.doId, 'vulnerablevideographer', (self.getSuitConditionModifier(managerTarget.doId, 'vulnerablevideographer') + 11), 99, 'setBoth')
                            managerTarget.setDamageMultiplier(managerTarget.getDamageMultiplier() * 1.1)
                        if theSuit.dna.name == 'choreo':
                            if not self.suitHasCondition(managerTarget.doId, 'vulnerablevideographer'):
                                self.setSuitCondition(managerTarget.doId, 'vulnerablevideographer', 11, 99, 'setBoth')
                            else:
                                self.setSuitCondition(managerTarget.doId, 'vulnerablevideographer', (self.getSuitConditionModifier(managerTarget.doId, 'vulnerablevideographer') + 11), 99, 'setBoth')
                            managerTarget.setDamageMultiplier(managerTarget.getDamageMultiplier() * 1.1)
                        if theSuit.dna.name == 'cinema':
                            if not self.suitHasCondition(managerTarget.doId, 'vulnerablevideographer'):
                                self.setSuitCondition(managerTarget.doId, 'vulnerablevideographer', 11, 99, 'setBoth')
                            else:
                                self.setSuitCondition(managerTarget.doId, 'vulnerablevideographer', (self.getSuitConditionModifier(managerTarget.doId, 'vulnerablevideographer') + 11), 99, 'setBoth')
                            managerTarget.setDamageMultiplier(managerTarget.getDamageMultiplier() * 1.1)
                        if theSuit.dna.name == 'fmaker':
                            if not self.suitHasCondition(managerTarget.doId, 'vulnerablevideographer'):
                                self.setSuitCondition(managerTarget.doId, 'vulnerablevideographer', 11, 99, 'setBoth')
                            else:
                                self.setSuitCondition(managerTarget.doId, 'vulnerablevideographer', (self.getSuitConditionModifier(managerTarget.doId, 'vulnerablevideographer') + 11), 99, 'setBoth')
                            managerTarget.setDamageMultiplier(managerTarget.getDamageMultiplier() * 1.1)
            elif atkType['name'] == 'VideographerRisingStarsSacrifice':
                managerTarget = None
                for suit in self.battle.activeSuits:
                    if suit.dna.name == 'mh2':
                        managerTarget = suit
                        if managerTarget.currHP <= 0:
                            continue
                        if managerTarget == None:
                            continue
                        managerTarget.setHP(managerTarget.maxHP / 2)
                        managerTarget.setMaxHP(managerTarget.maxHP / 2)
                        managerTarget.setDamageMultiplier(managerTarget.getDamageMultiplier() * 1.5)
                    if suit.dna.name == 'std2':
                        managerTarget = suit
                        if managerTarget.currHP <= 0:
                            continue
                        if managerTarget == None:
                            continue
                        managerTarget.setHP(managerTarget.maxHP / 2)
                        managerTarget.setMaxHP(managerTarget.maxHP / 2)
                        managerTarget.setDamageMultiplier(managerTarget.getDamageMultiplier() * 1.5)
            elif atkType['name'] == 'BroadcasterDonation':
                managerTarget = None
                for suit in self.battle.activeSuits:
                    if suit.dna.name == 'videog':
                        managerTarget = suit
                        if managerTarget.currHP <= 0:
                            continue
                        if managerTarget == None:
                            continue
                        if theSuit.currHP < (theSuit.maxHP / 3):
                            managerTarget.setHP(managerTarget.currHP + theSuit.currHP)
                            theSuit.setHP(math.ceil(theSuit.currHP - theSuit.currHP))
                            if suit.getHP() <= 0:
                                self.setSuitCondition(suit.doId, 'deathcheck', 1, 1, 'setBoth')
                        else:
                            managerTarget.setHP(managerTarget.currHP + (theSuit.maxHP / 3))
                            theSuit.setHP(math.ceil(theSuit.currHP - (theSuit.maxHP / 3)))
                self.__removeLured(theSuit.doId)
            elif atkType['name'] == 'BroadcasterViralSensation':
                result = 30
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'allGagBoost', 50, 2, 'setBoth')
                self.setToonCondition(toon.doId, 'lureBoost', 50, 2, 'setBoth')
            elif atkType['name'] == 'VideographerElectricShock':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'electricshockcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target6', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target5', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target4', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target3', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target2', 0, 0, 'setBoth')
                targetSuit = self.battle.activeSuits[2]
                if targetSuit.currHP <= 0:
                    continue
                x = (targetSuit.maxHP * targetSuit.hardMaxHP) - targetSuit.currHP
                targetSuit.setHP(math.ceil(targetSuit.currHP + x))
                self.__removeLured(targetSuit.doId)
                self.setSuitCondition(targetSuit.doId, 'bellowattack', 1, 1, 'setBoth')
            elif atkType['name'] == 'VideographerElectricShock2':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'electricshockcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target6', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target5', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target4', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target3', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target2', 0, 0, 'setBoth')
                targetSuit = self.battle.activeSuits[3]
                if targetSuit.currHP <= 0:
                    continue
                x = (targetSuit.maxHP * targetSuit.hardMaxHP) - targetSuit.currHP
                targetSuit.setHP(math.ceil(targetSuit.currHP + x))
                self.__removeLured(targetSuit.doId)
                self.setSuitCondition(targetSuit.doId, 'bellowattack', 1, 1, 'setBoth')
            elif atkType['name'] == 'VideographerElectricShock3':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'electricshockcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target6', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target5', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target4', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target3', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target2', 0, 0, 'setBoth')
                targetSuit = self.battle.activeSuits[4]
                if targetSuit.currHP <= 0:
                    continue
                x = (targetSuit.maxHP * targetSuit.hardMaxHP) - targetSuit.currHP
                targetSuit.setHP(math.ceil(targetSuit.currHP + x))
                self.__removeLured(targetSuit.doId)
                self.setSuitCondition(targetSuit.doId, 'bellowattack', 1, 1, 'setBoth')
            elif atkType['name'] == 'VideographerElectricShock4':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'electricshockcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target6', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target5', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target4', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target3', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target2', 0, 0, 'setBoth')
                targetSuit = self.battle.activeSuits[5]
                if targetSuit.currHP <= 0:
                    continue
                x = (targetSuit.maxHP * targetSuit.hardMaxHP) - targetSuit.currHP
                targetSuit.setHP(math.ceil(targetSuit.currHP + x))
                self.__removeLured(targetSuit.doId)
                self.setSuitCondition(targetSuit.doId, 'bellowattack', 1, 1, 'setBoth')
            elif atkType['name'] == 'FilmmakerCameraRewind':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'filmmakercalculator', 0, 0, 'setBoth')
                for suit in self.battle.activeSuits:
                    if suit.currHP <= 0:
                          continue
                    if suit.currHP < suit.maxHP and not suit.dna.name == 'videog' and not suit.dna.name == 'hroller2':
                        x = (suit.maxHP * suit.hardMaxHP) - suit.currHP
                        if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
                            suit.setHP(suit.currHP + 0)
                        elif suit.currHP + 125 > (suit.maxHP * suit.hardMaxHP):
                            suit.setHP(suit.currHP + x)
                        else:
                            suit.setHP(suit.currHP + 125)
                    if not suit.currHP < suit.maxHP and not suit.dna.name == 'videog' and not suit.dna.name == 'hroller2':
                        suit.setDamageMultiplier(suit.getDamageMultiplier() * 1.1)
            elif atkType['name'] == 'FilmmakerCameraFlash':
                result = 25
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'confused', 1, 2, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'cinemacalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'ChoreoChoreography':
                result = random.choice((0, 20))
                attack[SUIT_HP_COL][targetIndex] = result
                if result > 0:
                    self.setToonCondition(toon.doId, 'snapped', 1.25, 2, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'choreocalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'DirectorCut':
                self.setToonCondition(toon.doId, 'allGagBoost', -50, 2, 'setBoth')
                self.setToonCondition(toon.doId, 'lureBoost', -50, 2, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'directorcalculator', 0, 0, 'setBoth')
                result = 25
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'DirectorAction':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'extortioncalculator2', 1, 10, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'directorcalculator', 0, 0, 'setBoth')
                for t in self.battle.activeToons:
                    self.setToonCondition(t, random.choice(
                        ('useToonUp','useTrap', 'useLure', 'useThrow', 'useSquirt', 'useZap', 'useSound', 'useDrop',)), 1, 2, 'setBoth')
            elif atkType['name'] == 'DirectorActionRetaliation':
                if not self.toonHasCondition(toon.doId, 'rushJobCompleted'):
                    result = random.randint(20, 40)
                    attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'extortioncalculator2', 0, 0, 'setBoth')
            elif atkType['name'] == 'DirectorBackToOnes':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'directorcalculator', 0, 0, 'setBoth')
                theSuit.setHP(math.ceil(theSuit.maxHP))
            elif atkType['name'] == 'DeathCheck':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.__removeLured(theSuit)
                if not self.suitHasCondition(theSuit.doId, 'dead'):
                    self.setSuitCondition(theSuit.doId, 'dead', 1, 99, 'setBoth')
            elif atkType['name'] == 'AbsorbMovie':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                theSuit.setHP(math.ceil(theSuit.currHP - math.ceil(self.absorbDamage)))
                if theSuit.currHP <= 0:
                    self.setSuitCondition(theSuit.doId, 'deathcheck', 1, 99, 'setBoth')
            elif atkType['name'] == 'AbsorbMovieLevel':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                theSuit.setHP(math.ceil(theSuit.currHP - math.ceil(self.levelDamage)))
            elif atkType['name'] == 'SueApplication':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'suemovie', 1, 99, 'setBoth')
            elif atkType['name'] == 'SueDamage':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                theSuit.setHP(math.ceil(theSuit.currHP - (theSuit.maxHP / 4)))
                if theSuit.currHP <= 0:
                    self.__removeLured(theSuit.doId)
                    self.setSuitCondition(theSuit.doId, 'deathcheck', 1, 2, 'setBoth')
            elif atkType['name'] == 'SueRemoval':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'suemovie', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'sued', 0, 0, 'setBoth')
            elif atkType['name'] == 'LureRemoval':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'lured', 0, 0, 'setBoth')
            elif atkType['name'] == 'Desperation':
                managerTarget = None
                if not self.suitHasCondition(theSuit.doId, 'deadgoat') and not self.suitHasCondition(theSuit.doId, 'deadgator') and not self.suitHasCondition(theSuit.doId, 'deadsteno') and not self.suitHasCondition(theSuit.doId, 'deadcase'):
                    self.setToonCondition(toon.doId, 'desperation', 1, 99, 'setBoth')
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'noToonUpGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noTrapGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noLureGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noThrowGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noSquirtGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noZapGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noSoundGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'noDropGags', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel4s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel5s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel6s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel7s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel8s', 0, 0, 'setBoth')
                for suit in self.battle.activeSuits:
                    if self.battle.findSuit(suit.doId).getManager():
                        managerTarget = suit
                    if managerTarget == None:
                        managerTarget = theSuit
                    self.setSuitCondition(managerTarget.doId, 'desperation', self.getSuitConditionModifier(managerTarget.doId, 'desperation') + (.4 / (len(self.battle.activeSuits) - 1)), 99, 'setBoth')
                    self.setSuitCondition(managerTarget.doId, 'desperationcalculator', 0, 0, 'setBoth')
                    if theSuit.dna.name == 'lgator':
                        self.setSuitCondition(managerTarget.doId, 'deadgator', 1, 99, 'setBoth')
                    if theSuit.dna.name == 'caseman':
                        self.setSuitCondition(managerTarget.doId, 'deadcase', 1, 99, 'setBoth')
                    if theSuit.dna.name == 'stenog':
                        self.setSuitCondition(managerTarget.doId, 'deadsteno', 1, 99, 'setBoth')
                    if theSuit.dna.name == 'sgoat':
                        self.setSuitCondition(managerTarget.doId, 'deadgoat', 1, 99, 'setBoth')
                from toontown.suit.DistributedLawbotBossAI import DistributedLawbotBossAI

                boss = None
                for do in simbase.air.doId2do.values():
                    if isinstance(do, DistributedLawbotBossAI):
                        for t in self.battle.activeToons:
                            if t in do.involvedToons:
                                boss = do
                                break
                        for t in self.battle.activeToons:
                            if t in do.involvedToons:
                                if self.toonHasCondition(t, 'desperation') and not self.suitHasCondition(theSuit.doId, 'deadgator') and not self.suitHasCondition(theSuit.doId, 'activegator') and not managerTarget.dna.name == 'lgator':
                                    boss.appendSuitsToBattle(boss.battleNumber, 'lgator')
                                elif self.toonHasCondition(t, 'desperation') and not self.suitHasCondition(theSuit.doId, 'deadsteno') and not self.suitHasCondition(theSuit.doId, 'activesteno') and not managerTarget.dna.name == 'stenog':
                                    boss.appendSuitsToBattle(boss.battleNumber, 'stenog')
                                elif self.toonHasCondition(t, 'desperation') and not self.suitHasCondition(theSuit.doId, 'deadcase') and not self.suitHasCondition(theSuit.doId, 'activecase') and not managerTarget.dna.name == 'caseman':
                                    boss.appendSuitsToBattle(boss.battleNumber, 'caseman')
                                elif self.toonHasCondition(t, 'desperation') and not self.suitHasCondition(theSuit.doId, 'deadgoat') and not self.suitHasCondition(theSuit.doId, 'activegoat') and not managerTarget.dna.name == 'sgoat':
                                    boss.appendSuitsToBattle(boss.battleNumber, 'sgoat')
            elif atkType['name'] == 'Desperation2':
                self.setSuitCondition(theSuit.doId, 'desperation', self.getSuitConditionModifier(theSuit.doId, 'desperation') + .4, 99, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'desperationcalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'TargetCheck':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                if len(self.battle.activeSuits) > 1:
                    targetSuit = self.battle.activeSuits[1]
                    if targetSuit.getHP() > 0 and not targetSuit.getHP() > targetSuit.maxHP and not targetSuit.getManager() and not theSuit.dna.name == 'videog' and not self.suitHasCondition(targetSuit.doId, 'extraAttack10'):
                        self.setSuitCondition(theSuit.doId, 'target2', 1, 10, 'setBoth')
                    else:
                        if len(self.battle.activeSuits) > 2:
                            targetSuit = self.battle.activeSuits[2]
                            if targetSuit.getHP() > 0 and not targetSuit.getHP() > targetSuit.maxHP and not targetSuit.getManager() and not self.suitHasCondition(targetSuit.doId, 'extraAttack10'):
                                self.setSuitCondition(theSuit.doId, 'target3', 1, 10, 'setBoth')
                            else:
                                if len(self.battle.activeSuits) > 3:
                                    targetSuit = self.battle.activeSuits[3]
                                    if targetSuit.getHP() > 0 and not targetSuit.getHP() > targetSuit.maxHP and not targetSuit.getManager() and not self.suitHasCondition(targetSuit.doId, 'extraAttack10'):
                                        self.setSuitCondition(theSuit.doId, 'target4', 1, 10, 'setBoth')
                                    else:
                                        if len(self.battle.activeSuits) > 4:
                                            targetSuit = self.battle.activeSuits[4]
                                            if targetSuit.getHP() > 0 and not targetSuit.getHP() > targetSuit.maxHP and not targetSuit.getManager() and not self.suitHasCondition(targetSuit.doId, 'extraAttack10'):
                                                self.setSuitCondition(theSuit.doId, 'target5', 1, 10, 'setBoth')
                                            else:
                                                if len(self.battle.activeSuits) > 5:
                                                    targetSuit = self.battle.activeSuits[5]
                                                    if targetSuit.getHP() > 0 and not targetSuit.getHP() > targetSuit.maxHP and not targetSuit.getManager() and not self.suitHasCondition(targetSuit.doId, 'extraAttack10'):
                                                        self.setSuitCondition(theSuit.doId, 'target6', 1, 10, 'setBoth')
                                                    else:
                                                        pass
            elif atkType['name'] == 'AmbassadorTargetCheck':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                if len(self.battle.activeSuits) > 1:
                    targetSuit = self.battle.activeSuits[1]
                    if targetSuit.getHP() > 0 and self.suitHasCondition(targetSuit.doId, 'ambheadrollertarget'):
                        self.setSuitCondition(theSuit.doId, 'ambtarget2', 1, 10, 'setBoth')
                    else:
                        if len(self.battle.activeSuits) > 2:
                            targetSuit = self.battle.activeSuits[2]
                            if targetSuit.getHP() > 0 and self.suitHasCondition(targetSuit.doId, 'ambheadrollertarget'):
                                self.setSuitCondition(theSuit.doId, 'ambtarget3', 1, 10, 'setBoth')
                            else:
                                if len(self.battle.activeSuits) > 3:
                                    targetSuit = self.battle.activeSuits[3]
                                    if targetSuit.getHP() > 0 and self.suitHasCondition(targetSuit.doId, 'ambheadrollertarget'):
                                        self.setSuitCondition(theSuit.doId, 'ambtarget4', 1, 10, 'setBoth')
                                    else:
                                        if len(self.battle.activeSuits) > 4:
                                            targetSuit = self.battle.activeSuits[4]
                                            if targetSuit.getHP() > 0 and self.suitHasCondition(targetSuit.doId, 'ambheadrollertarget'):
                                                self.setSuitCondition(theSuit.doId, 'ambtarget5', 1, 10, 'setBoth')
                                            else:
                                                if len(self.battle.activeSuits) > 5:
                                                    targetSuit = self.battle.activeSuits[5]
                                                    if targetSuit.getHP() > 0 and self.suitHasCondition(targetSuit.doId, 'ambheadrollertarget'):
                                                        self.setSuitCondition(theSuit.doId, 'ambtarget6', 1, 10, 'setBoth')
                                                    else:
                                                        pass
            elif atkType['name'] == 'BanLevel4':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'nolevel4s', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'nolevel6s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel5s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel8s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel7s', 0, 0, 'setBoth')
            elif atkType['name'] == 'BanLevel5':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'nolevel4s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel6s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel5s', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'nolevel8s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel7s', 0, 0, 'setBoth')
            elif atkType['name'] == 'BanLevel6':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'nolevel4s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel6s', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'nolevel5s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel8s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel7s', 0, 0, 'setBoth')
            elif atkType['name'] == 'BanLevel7':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'nolevel4s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel6s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel5s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel8s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel7s', 1, 3, 'setBoth')
            elif atkType['name'] == 'BanLevel8':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'nolevel4s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel5s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel6s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel7s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel8s', 1, 3, 'setBoth')
            elif atkType['name'] == 'BanLevel45':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'nolevel4s', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'nolevel5s', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'nolevel6s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel7s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel8s', 0, 0, 'setBoth')
            elif atkType['name'] == 'BanLevel46':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'nolevel4s', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'nolevel5s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel6s', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'nolevel7s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel8s', 0, 0, 'setBoth')
            elif atkType['name'] == 'BanLevel47':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'nolevel4s', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'nolevel5s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel6s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel7s', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'nolevel8s', 0, 0, 'setBoth')
            elif atkType['name'] == 'BanLevel48':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'nolevel4s', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'nolevel5s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel6s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel7s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel8s', 1, 3, 'setBoth')
            elif atkType['name'] == 'BanLevel56':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'nolevel4s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel5s', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'nolevel6s', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'nolevel7s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel8s', 0, 0, 'setBoth')
            elif atkType['name'] == 'BanLevel57':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'nolevel4s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel5s', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'nolevel6s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel7s', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'nolevel8s', 0, 0, 'setBoth')
            elif atkType['name'] == 'BanLevel58':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'nolevel4s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel5s', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'nolevel6s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel7s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel8s', 1, 3, 'setBoth')
            elif atkType['name'] == 'BanLevel67':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'nolevel4s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel5s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel6s', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'nolevel7s', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'nolevel8s', 0, 0, 'setBoth')
            elif atkType['name'] == 'BanLevel68':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'nolevel4s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel5s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel6s', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'nolevel7s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel8s', 1, 3, 'setBoth')
            elif atkType['name'] == 'BanLevel78':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'nolevel4s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel5s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel6s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'nolevel7s', 1, 3, 'setBoth')
                    self.setToonCondition(t, 'nolevel8s', 1, 3, 'setBoth')
            elif atkType['name'] == 'BanToonup':
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
            elif atkType['name'] == 'BanTrap':
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
            elif atkType['name'] == 'BanLure':
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
            elif atkType['name'] == 'BanThrow':
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
            elif atkType['name'] == 'BanSquirt':
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
            elif atkType['name'] == 'BanZap':
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
            elif atkType['name'] == 'BanSound':
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
            elif atkType['name'] == 'BanDrop':
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
            elif atkType['name'] == 'BanToonupTrap':
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
            elif atkType['name'] == 'BanToonupLure':
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
            elif atkType['name'] == 'BanToonupThrow':
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
            elif atkType['name'] == 'BanToonupSquirt':
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
            elif atkType['name'] == 'BanToonupZap':
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
            elif atkType['name'] == 'BanToonupSound':
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
            elif atkType['name'] == 'BanToonupDrop':
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
            elif atkType['name'] == 'BanTrapLure':
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
            elif atkType['name'] == 'BanTrapThrow':
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
            elif atkType['name'] == 'BanTrapSquirt':
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
            elif atkType['name'] == 'BanTrapZap':
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
            elif atkType['name'] == 'BanTrapSound':
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
            elif atkType['name'] == 'BanTrapDrop':
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
            elif atkType['name'] == 'BanLureThrow':
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
            elif atkType['name'] == 'BanLureSquirt':
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
            elif atkType['name'] == 'BanLureZap':
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
            elif atkType['name'] == 'BanLureSound':
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
            elif atkType['name'] == 'BanLureDrop':
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
            elif atkType['name'] == 'BanThrowSquirt':
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
            elif atkType['name'] == 'BanThrowZap':
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
            elif atkType['name'] == 'BanThrowSound':
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
            elif atkType['name'] == 'BanThrowDrop':
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
            elif atkType['name'] == 'BanSquirtZap':
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
            elif atkType['name'] == 'BanSquirtSound':
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
            elif atkType['name'] == 'BanSquirtDrop':
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
            elif atkType['name'] == 'BanZapSound':
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
            elif atkType['name'] == 'BanZapDrop':
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
            elif atkType['name'] == 'BanSoundDrop':
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

            # Professor Control: I honestly do not know how to best approach this issue.  Especially in the case of damage over times, a Cog's ID is -1 because no Cog exists.  However, this sets theSuit to None, and the rest of this is treated as if a Cog exists.  So, this will have to do for the time being.
            try:
                if atkType['name'] == 'CalculatingFees':
                    if self.suitHasCondition(theSuit.doId, 'desperation'):
                        attack[SUIT_HP_COL][targetIndex] = math.ceil(result * (1 + self.getSuitConditionModifier(theSuit.doId, 'desperation')))
                        toon.setHp(toon.hp + math.ceil(result * (1 + self.getSuitConditionModifier(theSuit.doId, 'desperation'))))
                    if theSuit.getDamageMultiplier() > 1:
                        attack[SUIT_HP_COL][targetIndex] = math.ceil(result * theSuit.getDamageMultiplier())
                        toon.setHp(toon.hp + math.ceil(result * theSuit.getDamageMultiplier()))
                elif atkType['name'] == 'CaseManagerLegallyBound' and self.suitHasCondition(theSuit.doId, 'desperation'):
                    attack[SUIT_HP_COL][targetIndex] = math.ceil(result * 1.4)
                elif atkType['name'] == 'CaseManagerLegallyBound':
                    attack[SUIT_HP_COL][targetIndex] = math.ceil(result * self.getSuitConditionModifier(theSuit.doId, 'desperation'))
                elif atkType['name'] == 'PowerhouseBurnDamage' and self.suitHasCondition(theSuit.doId, 'desperation'):
                    attack[SUIT_HP_COL][targetIndex] = math.ceil(result * 1.4)
                elif atkType['name'] == 'PowerhouseBurnDamage':
                    attack[SUIT_HP_COL][targetIndex] = result
                elif atkType['name'] == 'UnionBusterUnionBusterDamage' and self.suitHasCondition(theSuit.doId, 'desperation'):
                    attack[SUIT_HP_COL][targetIndex] = math.ceil(result * 1.4)
                elif atkType['name'] == 'UnionBusterUnionBusterDamage':
                    attack[SUIT_HP_COL][targetIndex] = result
                elif atkType['name'] == 'WiretapperGagBan' and self.suitHasCondition(theSuit.doId, 'desperation'):
                    attack[SUIT_HP_COL][targetIndex] = math.ceil(result * 1.4)
                elif atkType['name'] == 'WiretapperGagBan':
                    attack[SUIT_HP_COL][targetIndex] = result
                elif atkType['name'] == 'StenographerCourtRecordBan' and self.suitHasCondition(theSuit.doId, 'desperation'):
                    attack[SUIT_HP_COL][targetIndex] = math.ceil(result * 1.4)
                elif atkType['name'] == 'StenographerCourtRecordBan':
                    attack[SUIT_HP_COL][targetIndex] = result
                elif atkType['name'] == 'CaseManagerCourtRecordBan' and self.suitHasCondition(theSuit.doId, 'desperation'):
                    attack[SUIT_HP_COL][targetIndex] = math.ceil(result * 1.4)
                elif atkType['name'] == 'CaseManagerCourtRecordBan':
                    attack[SUIT_HP_COL][targetIndex] = result
                elif atkType['name'] == 'UnionBusterUnionCalculator':
                    if self.suitHasCondition(theSuit.doId, 'desperation'):
                        attack[SUIT_HP_COL][targetIndex] = math.ceil(result * (1 + self.getSuitConditionModifier(theSuit.doId, 'desperation')))
                        toon.setHp(toon.hp + math.ceil(result * (1 + self.getSuitConditionModifier(theSuit.doId, 'desperation'))))
                    if theSuit.getDamageMultiplier() > 1:
                        attack[SUIT_HP_COL][targetIndex] = math.ceil(result * theSuit.getDamageMultiplier())
                        toon.setHp(toon.hp + math.ceil(result * theSuit.getDamageMultiplier()))
                elif atkType['name'] == 'SafetyHeatWaveCalculation':
                    if self.suitHasCondition(theSuit.doId, 'desperation'):
                        attack[SUIT_HP_COL][targetIndex] = math.ceil(result * (1 + self.getSuitConditionModifier(theSuit.doId, 'desperation')))
                        toon.setHp(toon.hp + math.ceil(result * (1 + self.getSuitConditionModifier(theSuit.doId, 'desperation'))))
                    if theSuit.getDamageMultiplier() > 1:
                        attack[SUIT_HP_COL][targetIndex] = math.ceil(result * theSuit.getDamageMultiplier())
                        toon.setHp(toon.hp + math.ceil(result * theSuit.getDamageMultiplier()))
                elif atkType['name'] == 'WiretapperCollectCall2':
                    if self.suitHasCondition(theSuit.doId, 'desperation'):
                        attack[SUIT_HP_COL][targetIndex] = math.ceil(result * (1 + self.getSuitConditionModifier(theSuit.doId, 'desperation')))
                        toon.setHp(toon.hp + math.ceil(result * (1 + self.getSuitConditionModifier(theSuit.doId, 'desperation'))))
                    if self.suitHasCondition(theSuit.doId, 'brokenconnection'):
                        attack[SUIT_HP_COL][targetIndex] = math.ceil(result * self.getSuitConditionModifier(theSuit.doId, 'brokenconnection'))
                        toon.setHp(toon.hp + math.ceil(result * self.getSuitConditionModifier(theSuit.doId, 'brokenconnection')))
                    if theSuit.getDamageMultiplier() > 1:
                        attack[SUIT_HP_COL][targetIndex] = math.ceil(result * theSuit.getDamageMultiplier())
                        toon.setHp(toon.hp + math.ceil(result * theSuit.getDamageMultiplier()))
                else:
                    if theSuit.getHP() > (theSuit.getMaxHP() * 1.5):
                        result *= 1.5
                    if self.suitHasCondition(theSuit.doId, 'desperation'):
                        result *= (1 + self.getSuitConditionModifier(theSuit.doId, 'desperation'))
                    if self.suitHasCondition(theSuit.doId, 'brokenconnection'):
                        result *= self.getSuitConditionModifier(theSuit.doId, 'brokenconnection')
                    if self.suitHasCondition(theSuit.doId, 'enraged'):
                        result *= self.getSuitConditionModifier(theSuit.doId, 'enraged')
                    if self.toonHasCondition(toonId, 'snapped'):
                        result *= self.getToonConditionModifier(toonId, 'snapped')
                    if self.toonHasCondition(toonId, 'corruption'):
                        result *= self.getToonConditionModifier(toonId, 'corruption')
                    if theSuit.getDamageMultiplier() > 1:
                        result *= theSuit.getDamageMultiplier()
                    attack[SUIT_HP_COL][targetIndex] = math.ceil(result)
            except:
                if theSuit.getHP() > (theSuit.getMaxHP() * 1.5):
                    result *= 1.5
                if self.suitHasCondition(theSuit.doId, 'desperation'):
                    result *= (1 + self.getSuitConditionModifier(theSuit.doId, 'desperation'))
                if self.suitHasCondition(theSuit.doId, 'brokenconnection'):
                    result *= self.getSuitConditionModifier(theSuit.doId, 'brokenconnection')
                if self.suitHasCondition(theSuit.doId, 'enraged'):
                    result *= self.getSuitConditionModifier(theSuit.doId, 'enraged')
                if self.toonHasCondition(toonId, 'snapped'):
                    result *= self.getToonConditionModifier(toonId, 'snapped')
                if self.toonHasCondition(toonId, 'corruption'):
                    result *= self.getToonConditionModifier(toonId, 'corruption')
                if theSuit.getDamageMultiplier() > 1:
                    result *= theSuit.getDamageMultiplier()
                attack[SUIT_HP_COL][targetIndex] = math.ceil(result)

    def __getToonHp(self, toonDoId):
        handle = self.battle.getToon(toonDoId)
        if handle != None:
            return handle.hp
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
                if toonHp - attack[SUIT_HP_COL][position] <= 0:
                    if self.notify.getDebug():
                        self.notify.debug('Toon %d has died, removing' % t)
                    self.toonLeftBattle(t)
                    attack[TOON_DIED_COL] = attack[TOON_DIED_COL] | 1 << position
                self.toonHPAdjusts[t] -= math.ceil(attack[SUIT_HP_COL][position])

    def __suitCanAttack(self, suitId):
        if self.__combatantDead(suitId, toon=0) or self.__suitIsLured(suitId) or self.suitHasCondition(suitId, 'suemovie'):
            return 0
        return 1

    def __updateSuitAtkStat(self, toonId):
        if toonId in self.suitAtkStats:
            self.suitAtkStats[toonId] += 1
        else:
            self.suitAtkStats[toonId] = 1

    def __printSuitAtkStats(self):
        for currTgt in self.suitAtkStats.keys():
            if currTgt not in self.battle.activeToons:
                continue
            tgtPos = self.battle.activeToons.index(currTgt)

    def __getAbilityQueued(self, suitId):
        '''
        This method is for use with making standard Cog attacks.  Attacks with specific parameters (e.g. cheats) should be created manually.  This method can work for extra attacks, though, as a generic extra attack can be made easily with this method that, quite franky, gets used often.
        '''
        theSuit = self.battle.findSuit(suitId)
        attack = getDefaultSuitAttack()
        attack[SUIT_ID_COL] = suitId
        # attack[SUIT_ATK_COL] = self.__calcSuitAtkType(theSuit)
        attack[SUIT_ATK_COL] = {'suitName': '',
                                    'name': 'AbilityQueued',  # Ability Queue if Manager Cogs are unable to Cheat
                                    'animName': 'nothing',
                                    'hp': 0,
                                    'acc': 100,
                                    'freq': 0,
                                    'group': SuitBattleGlobals.ATK_TGT_SINGLE}
        attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
        if attack[SUIT_TGT_COL] == []:
            attack = getDefaultSuitAttack()
        attack[SUIT_HP_COL] = [-1 for i in xrange(len(self.battle.activeToons))]
        self.__calcSuitAtkHpALT(attack)
        if attack[SUIT_ATK_COL]:
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
        return attack

    def __getLureRemoval(self, suitId):
        '''
        This method is for use with making standard Cog attacks.  Attacks with specific parameters (e.g. cheats) should be created manually.  This method can work for extra attacks, though, as a generic extra attack can be made easily with this method that, quite franky, gets used often.
        '''
        theSuit = self.battle.findSuit(suitId)
        attack = getDefaultSuitAttack()
        attack[SUIT_ID_COL] = suitId
        # attack[SUIT_ATK_COL] = self.__calcSuitAtkType(theSuit)
        attack[SUIT_ATK_COL] = {'suitName': '',
                                    'name': 'LureRemoval',  # Lure Removal Movie
                                    'animName': 'nothing',
                                    'hp': 0,
                                    'acc': 100,
                                    'freq': 0,
                                    'group': SuitBattleGlobals.ATK_TGT_SINGLE}
        attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
        if attack[SUIT_TGT_COL] == []:
            attack = getDefaultSuitAttack()
        attack[SUIT_HP_COL] = [-1 for i in xrange(len(self.battle.activeToons))]
        self.__calcSuitAtkHpALT(attack)
        if attack[SUIT_ATK_COL]:
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
        return attack

    def __getGenericSuitAttack(self, suitId):
        '''
        This method is for use with making standard Cog attacks.  Attacks with specific parameters (e.g. cheats) should be created manually.  This method can work for extra attacks, though, as a generic extra attack can be made easily with this method that, quite franky, gets used often.
        '''
        theSuit = self.battle.findSuit(suitId)
        if theSuit.dna.name == 'lgator':
            currentBossHealth = -1
            for s in self.battle.suits:
                if s.dna.name == 'stenog' or s.dna.name == 'sgoat' or s.dna.name == 'caseman':
                    currentBossHealth = s.currHP
            currentBossHealth3 = -1
            currentBossHealth4 = -1
            currentBossHealth5 = -1
            for s in self.battle.suits:
                if s.dna.name == 'caseman':
                    currentBossHealth3 = s.currHP
                if s.dna.name == 'sgoat':
                    currentBossHealth4 = s.currHP
                if s.dna.name == 'stenog':
                    currentBossHealth5 = s.currHP
            if currentBossHealth == -1 and not self.suitHasCondition(theSuit.doId, 'desperation'):
                self.setSuitCondition(theSuit.doId, 'desperationcalculator', 1, 100, 'setBoth')
        if theSuit.dna.name == 'stenog':
            currentBossHealth = -1
            for s in self.battle.suits:
                if s.dna.name == 'lgator' or s.dna.name == 'sgoat' or s.dna.name == 'caseman':
                    currentBossHealth = s.currHP
            currentBossHealth3 = -1
            currentBossHealth4 = -1
            currentBossHealth5 = -1
            for s in self.battle.suits:
                if s.dna.name == 'caseman':
                    currentBossHealth3 = s.currHP
                if s.dna.name == 'lgator':
                    currentBossHealth4 = s.currHP
                if s.dna.name == 'sgoat':
                    currentBossHealth5 = s.currHP
            if currentBossHealth == -1 and not self.suitHasCondition(theSuit.doId, 'desperation'):
                self.setSuitCondition(theSuit.doId, 'desperationcalculator', 1, 100, 'setBoth')
        if theSuit.dna.name == 'caseman':
            currentBossHealth = -1
            for s in self.battle.suits:
                if s.dna.name == 'stenog' or s.dna.name == 'sgoat' or s.dna.name == 'lgator':
                    currentBossHealth = s.currHP
            currentBossHealth3 = -1
            currentBossHealth4 = -1
            currentBossHealth5 = -1
            for s in self.battle.suits:
                if s.dna.name == 'sgoat':
                    currentBossHealth3 = s.currHP
                if s.dna.name == 'lgator':
                    currentBossHealth4 = s.currHP
                if s.dna.name == 'stenog':
                    currentBossHealth5 = s.currHP
            if currentBossHealth == -1 and not self.suitHasCondition(theSuit.doId, 'desperation'):
                self.setSuitCondition(theSuit.doId, 'desperationcalculator', 1, 100, 'setBoth')
        if theSuit.dna.name == 'sgoat':
            currentBossHealth = -1
            for s in self.battle.suits:
                if s.dna.name == 'stenog' or s.dna.name == 'lgator' or s.dna.name == 'caseman':
                    currentBossHealth = s.currHP
            currentBossHealth3 = -1
            currentBossHealth4 = -1
            currentBossHealth5 = -1
            for s in self.battle.suits:
                if s.dna.name == 'caseman':
                    currentBossHealth3 = s.currHP
                if s.dna.name == 'lgator':
                    currentBossHealth4 = s.currHP
                if s.dna.name == 'stenog':
                    currentBossHealth5 = s.currHP
            if currentBossHealth == -1 and not self.suitHasCondition(theSuit.doId, 'desperation'):
                self.setSuitCondition(theSuit.doId, 'desperationcalculator', 1, 100, 'setBoth')
        if theSuit.dna.name == 'phouse':
            x = self.TurnsElapsed
            currentBossHealth = -1
            for s in self.battle.suits:
                if s.dna.name == 'wtapper' or s.dna.name == 'bkeeper' or s.dna.name == 'ambass':
                    currentBossHealth = s.currHP
            if currentBossHealth == -1 and not self.suitHasCondition(theSuit.doId, 'desperation'):
                self.setSuitCondition(theSuit.doId, 'desperationcalculator', 1, 100, 'setBoth')
        if theSuit.dna.name == 'bkeeper':
            x = self.TurnsElapsed
            currentBossHealth = -1
            for s in self.battle.suits:
                if s.dna.name == 'wtapper' or s.dna.name == 'phouse' or s.dna.name == 'ambass':
                    currentBossHealth = s.currHP
            currentBossHealth3 = -1
            for s in self.battle.suits:
                if s.dna.name == 'phouse':
                    currentBossHealth3 = s.currHP
            if currentBossHealth3 == -1:
                self.setSuitCondition(theSuit.doId, 'deadpower', 1, 100, 'setBoth')
            if currentBossHealth == -1 and not self.suitHasCondition(theSuit.doId, 'desperation'):
                self.setSuitCondition(theSuit.doId, 'desperationcalculator', 1, 100, 'setBoth')
        if theSuit.dna.name == 'wtapper':
            x = self.TurnsElapsed
            currentBossHealth = -1
            for s in self.battle.suits:
                if s.dna.name == 'phouse' or s.dna.name == 'bkeeper' or s.dna.name == 'ambass':
                    currentBossHealth = s.currHP
            currentBossHealth3 = -1
            for s in self.battle.suits:
                if s.dna.name == 'phouse':
                    currentBossHealth3 = s.currHP
            if currentBossHealth3 == -1:
                self.setSuitCondition(theSuit.doId, 'deadpower', 1, 100, 'setBoth')
            if currentBossHealth == -1 and not self.suitHasCondition(theSuit.doId, 'desperation'):
                self.setSuitCondition(theSuit.doId, 'desperationcalculator', 1, 100, 'setBoth')
        if theSuit.dna.name == 'ambass':
            x = self.TurnsElapsed
            currentBossHealth = -1
            for s in self.battle.suits:
                if s.dna.name == 'wtapper' or s.dna.name == 'bkeeper' or s.dna.name == 'phouse':
                    currentBossHealth = s.currHP
            currentBossHealth3 = -1
            for s in self.battle.suits:
                if s.dna.name == 'phouse':
                    currentBossHealth3 = s.currHP
            if currentBossHealth3 == -1:
                self.setSuitCondition(theSuit.doId, 'deadpower', 1, 100, 'setBoth')
            if currentBossHealth == -1 and not self.suitHasCondition(theSuit.doId, 'desperation'):
                self.setSuitCondition(theSuit.doId, 'desperationcalculator', 1, 100, 'setBoth')
        if theSuit.dna.name == 'videog':
            x = self.TurnsElapsed
            currentBossHealth = -1
            for s in self.battle.suits:
                if s.dna.name == 'bcaster':
                    currentBossHealth = s.currHP
            currentBossHealth2 = -1
            currentBossHealth3 = -1
            for s in self.battle.suits:
                if s.dna.name == 'mh2':
                    currentBossHealth2 = s.currHP
                if s.dna.name == 'std2':
                    currentBossHealth3 = s.currHP
            if currentBossHealth == -1 and not self.suitHasCondition(theSuit.doId,
                                                                     'silhouettespawn') and self.suitHasCondition(
                    theSuit.doId, 'phase3'):
                self.setSuitCondition(theSuit.doId, 'silhouettespawn', 1, 1, 'setBoth')
            if currentBossHealth2 >= 1 and (x + 1) % 3 == 0:
                self.setSuitCondition(theSuit.doId, 'hollywoodcalculator', 1, 1, 'setBoth')
            if currentBossHealth3 >= 1 and (x + 1) % 3 == 0:
                self.setSuitCondition(theSuit.doId, 'hollywoodcalculator', 1, 1, 'setBoth')
        if theSuit.dna.name == 'radiog':
            x = self.TurnsElapsed
            currentBossHealth = -1
            for s in self.battle.suits:
                if s.dna.name == 'ubuster' or s.dna.name == 'racket' or s.dna.name == 'safesupervis':
                    currentBossHealth = s.currHP
            currentBossHealth3 = -1
            for s in self.battle.suits:
                if s.dna.name == 'ubuster':
                    currentBossHealth3 = s.currHP
            if currentBossHealth3 == -1:
                self.setSuitCondition(theSuit.doId, 'deadunion', 1, 100, 'setBoth')
            if currentBossHealth == -1 and not self.suitHasCondition(theSuit.doId, 'desperation'):
                self.setSuitCondition(theSuit.doId, 'desperationcalculator', 1, 100, 'setBoth')
        if theSuit.dna.name == 'racket':
            x = self.TurnsElapsed
            currentBossHealth = -1
            for s in self.battle.suits:
                if s.dna.name == 'ubuster' or s.dna.name == 'safesupervis' or s.dna.name == 'radiog':
                    currentBossHealth = s.currHP
            currentBossHealth3 = -1
            for s in self.battle.suits:
                if s.dna.name == 'ubuster':
                    currentBossHealth3 = s.currHP
            if currentBossHealth3 == -1:
                self.setSuitCondition(theSuit.doId, 'deadunion', 1, 100, 'setBoth')
            if currentBossHealth == -1 and not self.suitHasCondition(theSuit.doId, 'desperation'):
                self.setSuitCondition(theSuit.doId, 'desperationcalculator', 1, 100, 'setBoth')
        if theSuit.dna.name == 'ubuster':
            x = self.TurnsElapsed
            currentBossHealth = -1
            for s in self.battle.suits:
                if s.dna.name == 'safesupervis' or s.dna.name == 'racket' or s.dna.name == 'radiog':
                    currentBossHealth = s.currHP
            if currentBossHealth == -1 and not self.suitHasCondition(theSuit.doId, 'desperation'):
                self.setSuitCondition(theSuit.doId, 'desperationcalculator', 1, 100, 'setBoth')
        if theSuit.dna.name == 'safesupervis':
            x = self.TurnsElapsed
            currentBossHealth = -1
            for s in self.battle.suits:
                if s.dna.name == 'ubuster' or s.dna.name == 'racket' or s.dna.name == 'radiog':
                    currentBossHealth = s.currHP
            currentBossHealth3 = -1
            for s in self.battle.suits:
                if s.dna.name == 'ubuster':
                    currentBossHealth3 = s.currHP
            if currentBossHealth3 == -1:
                self.setSuitCondition(theSuit.doId, 'deadunion', 1, 100, 'setBoth')
            if currentBossHealth == -1 and not self.suitHasCondition(theSuit.doId, 'desperation'):
                self.setSuitCondition(theSuit.doId, 'desperationcalculator', 1, 100, 'setBoth')
        attack = getDefaultSuitAttack()
        attack[SUIT_ID_COL] = suitId
        # attack[SUIT_ATK_COL] = self.__calcSuitAtkType(theSuit)
        attack[SUIT_ATK_COL] = SuitBattleGlobals.getSuitAttack(theSuit.dna.name, theSuit.getLevel())  # Professor Control: __calcSuitAtkType() is no longer used, but that has desperation code.  TODO: Find a new, possibly neater, way to pull off desperation.
        attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
        if attack[SUIT_TGT_COL] == []:
            attack = getDefaultSuitAttack()
        attack[SUIT_HP_COL] = [-1 for i in xrange(len(self.battle.activeToons))]
        self.__calcSuitAtkHp(attack)
        if attack[SUIT_ATK_COL]:
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
        return attack

    def __calculateSuitConditions(self):
        for i in xrange(len(self.battle.activeSuits)): # Cheat Calculators
            suitId = self.battle.activeSuits[i].doId
            x = self.TurnsElapsed
            if self.battle.activeSuits[i].dna.name == 'stenog':
                if (x + 1) % 3 == 0:
                    self.setSuitCondition(suitId, 'sanctioncalculator', 1, 9, 'setBoth')
                if (x + 3) % 3 == 0:
                    self.setSuitCondition(suitId, 'calculatingcalculator', 1, 10, 'setBoth')
            if self.battle.activeSuits[i].dna.name == 'caseman':
                if (x + 2) % 3 == 0:
                    self.setSuitCondition(suitId, 'bindingscalculator', 1, 9, 'setBoth')
                if x % 2 == 0:
                    self.setSuitCondition(suitId, 'insurancecalculator', 1, 10, 'setBoth')
            if self.battle.activeSuits[i].dna.name == 'lgator':
                if (x + 2) % 3 == 0:
                    self.setSuitCondition(suitId, 'snappedcalculator', 1, 10, 'setBoth')
                if x % 4 == 0 and len(self.battle.activeSuits) <= 6:
                    self.setSuitCondition(suitId, 'bashcalculator', 1, 10, 'setBoth')
                if x % 4 == 0 and self.suitHasCondition(suitId, 'bashcalculator') and len(self.battle.activeSuits) >= 6 and not self.deadSuits > 0:
                    self.setSuitCondition(suitId, 'bashcalculator', 0, 0, 'setBoth')
                    self.setSuitCondition(suitId, 'bellowcalculator', 1, 10, 'setBoth')
                if self.battle.activeSuits[i].currHP <= 4100:
                    if (x + 1) % 4 == 0 and self.suitHasCondition(suitId, 'bashcalculator') and len(self.battle.activeSuits) >= 6 and not self.deadSuits > 0:
                        self.setSuitCondition(suitId, 'bashcalculator', 0, 0, 'setBoth')
                        self.setSuitCondition(suitId, 'bellowcalculator', 1, 10, 'setBoth')
                    elif (x + 1) % 4 == 0 and not self.suitHasCondition(suitId, 'bashcalculator') and len(self.battle.activeSuits) <= 6:
                        self.setSuitCondition(suitId, 'bashcalculator', 1, 10, 'setBoth')
                if self.battle.activeSuits[i].currHP <= 3600:
                    if (x + 2) % 4 == 0 and self.suitHasCondition(suitId, 'bashcalculator') and len(self.battle.activeSuits) >= 6 and not self.deadSuits > 0:
                        self.setSuitCondition(suitId, 'bashcalculator', 0, 0, 'setBoth')
                        self.setSuitCondition(suitId, 'bellowcalculator', 1, 10, 'setBoth')
                    elif (x + 2) % 4 == 0 and not self.suitHasCondition(suitId, 'bashcalculator') and len(self.battle.activeSuits) <= 6:
                        self.setSuitCondition(suitId, 'bashcalculator', 1, 10, 'setBoth')
                if self.battle.activeSuits[i].currHP <= 3100:
                    if (x + 3) % 4 == 0 and self.suitHasCondition(suitId, 'bashcalculator') and len(self.battle.activeSuits) >= 6 and not self.deadSuits > 0:
                        self.setSuitCondition(suitId, 'bashcalculator', 0, 0, 'setBoth')
                        self.setSuitCondition(suitId, 'bellowcalculator', 1, 10, 'setBoth')
                    elif (x + 3) % 4 == 0 and not self.suitHasCondition(suitId, 'bashcalculator') and len(self.battle.activeSuits) <= 6:
                        self.setSuitCondition(suitId, 'bashcalculator', 1, 10, 'setBoth')
                if self.battle.activeSuits[i].currHP <= 2600:
                    if (x + 4) % 4 == 0 and self.suitHasCondition(suitId, 'bashcalculator') and len(self.battle.activeSuits) >= 6 and not self.deadSuits > 0:
                        self.setSuitCondition(suitId, 'bashcalculator', 0, 0, 'setBoth')
                        self.setSuitCondition(suitId, 'bellowcalculator', 1, 10, 'setBoth')
                    elif (x + 4) % 4 == 0 and not self.suitHasCondition(suitId, 'bashcalculator') and len(self.battle.activeSuits) <= 6:
                        self.setSuitCondition(suitId, 'bashcalculator', 1, 10, 'setBoth')
                if self.battle.activeSuits[i].currHP <= 2100:
                    if (x + 3) % 3 == 0 and self.suitHasCondition(suitId, 'bashcalculator') and len(self.battle.activeSuits) >= 6 and not self.deadSuits > 0:
                        self.setSuitCondition(suitId, 'bashcalculator', 0, 0, 'setBoth')
                        self.setSuitCondition(suitId, 'bellowcalculator', 1, 10, 'setBoth')
                    elif (x + 3) % 3 == 0 and not self.suitHasCondition(suitId, 'bashcalculator') and len(self.battle.activeSuits) <= 6:
                        self.setSuitCondition(suitId, 'bashcalculator', 1, 10, 'setBoth')
                if self.battle.activeSuits[i].currHP <= 1600:
                    if (x + 2) % 2 == 0 and self.suitHasCondition(suitId, 'bashcalculator') and len(self.battle.activeSuits) >= 6 and not self.deadSuits > 0:
                        self.setSuitCondition(suitId, 'bashcalculator', 0, 0, 'setBoth')
                        self.setSuitCondition(suitId, 'bellowcalculator', 1, 10, 'setBoth')
                    elif (x + 2) % 2 == 0 and not self.suitHasCondition(suitId, 'bashcalculator') and len(self.battle.activeSuits) <= 6:
                        self.setSuitCondition(suitId, 'bashcalculator', 1, 10, 'setBoth')
                if self.battle.activeSuits[i].currHP <= 1100:
                    if (x + 2) % 2 == 0 and self.suitHasCondition(suitId, 'bashcalculator') and len(self.battle.activeSuits) >= 6 and not self.deadSuits > 0:
                        self.setSuitCondition(suitId, 'bashcalculator', 0, 0, 'setBoth')
                        self.setSuitCondition(suitId, 'bellowcalculator', 1, 10, 'setBoth')
                    elif (x + 2) % 2 == 0 and not self.suitHasCondition(suitId, 'bashcalculator') and len(self.battle.activeSuits) <= 6:
                        self.setSuitCondition(suitId, 'bashcalculator', 1, 10, 'setBoth')
                if self.battle.activeSuits[i].currHP <= 600:
                    if (x + 1) % 1 == 0 and self.suitHasCondition(suitId, 'bashcalculator') and len(self.battle.activeSuits) >= 6 and not self.deadSuits > 0:
                        self.setSuitCondition(suitId, 'bashcalculator', 0, 0, 'setBoth')
                        self.setSuitCondition(suitId, 'bellowcalculator', 1, 10, 'setBoth')
                    elif (x + 1) % 1 == 0 and not self.suitHasCondition(suitId, 'bashcalculator') and len(self.battle.activeSuits) <= 6:
                        self.setSuitCondition(suitId, 'bashcalculator', 1, 10, 'setBoth')
                if self.battle.activeSuits[i].currHP <= 100:
                    if (x + 1) % 1 == 0 and self.suitHasCondition(suitId, 'bashcalculator') and len(self.battle.activeSuits) >= 6 and not self.deadSuits > 0:
                        self.setSuitCondition(suitId, 'bashcalculator', 0, 0, 'setBoth')
                        self.setSuitCondition(suitId, 'bellowcalculator', 1, 10, 'setBoth')
                    elif (x + 1) % 1 == 0 and not self.suitHasCondition(suitId, 'bashcalculator') and len(self.battle.activeSuits) <= 6:
                        self.setSuitCondition(suitId, 'bashcalculator', 1, 10, 'setBoth')
            if self.battle.activeSuits[i].dna.name == 'sgoat':
                if (x + 2) % 4 == 0:
                    self.setSuitCondition(suitId, 'gavelcalculator', 1, 10, 'setBoth')
            if self.battle.activeSuits[i].dna.name == 'phouse': #powerhouse
                if x % 99 == 0:
                    self.setSuitCondition(suitId, 'rotationcalculator', 1, 10, 'setBoth')
            if self.battle.activeSuits[i].dna.name == 'bkeeper':  # bookkeeper
                if (x + 1) % 4 == 0:
                    self.setSuitCondition(suitId, 'explodingcalculator', 1, 9, 'setBoth')
                if (x + 2) % 3 == 0:
                    self.setSuitCondition(suitId, 'papercutcalculator', 1, 10, 'setBoth')
                if x % 5 == 0:
                    self.setSuitCondition(suitId, 'bookkeepingcalculator', 1, 10, 'setBoth')
            if self.battle.activeSuits[i].dna.name == 'wtapper':  # wiretapper
                if (x + 3) % 3 == 0:
                    self.setSuitCondition(suitId, 'calculatingcalculator', 1, 10, 'setBoth')
                if self.getSuitConditionTurns(suitId, 'immune') == 1:
                    self.setSuitCondition(suitId, 'brokenconnectioncalculator', 1, 10, 'setBoth')
                if self.getSuitConditionTurns(suitId, 'brokenconnection') == 1:
                    self.setSuitCondition(suitId, 'wiretappedcalculator', 1, 10, 'setBoth')
                if (x + 4) % 5 == 0:
                    self.setSuitCondition(suitId, 'voicemailcalculator', 1, 10, 'setBoth')
                if (x + 4) % 5 == 0:
                    self.setSuitCondition(suitId, 'busycalculator', 1, 10, 'setBoth')
                if (x + 2) % 3 == 0:
                    self.setSuitCondition(suitId, 'collectcallcalculator', 1, 10, 'setBoth')
                #if len(self.battle.activeSuits) >= 4 and x % 4 == 0:
                    #self.setSuitCondition(suitId, 'voicemailcalculator', 1, 10, 'setBoth')
            if self.battle.activeSuits[i].dna.name == 'ambass': #ambassador
                if (x + 2) % 4 == 0:
                    self.setSuitCondition(suitId, 'refinementcalculator', 1, 10, 'setBoth')
                if (x + 2) % 4 == 0:
                    self.setSuitCondition(suitId, 'advancementcalculator', 1, 10, 'setBoth')
                currentBossHealth = -1
                for s in self.battle.suits:
                    if s.dna.name == 'wtapper' or s.dna.name == 'bkeeper' or s.dna.name == 'phouse':
                        currentBossHealth = s.currHP
                    if (x + 2) % 3 == 0 and currentBossHealth > 0:
                        self.setSuitCondition(suitId, 'refinemanagercalculator', 1, 10, 'setBoth')
                if (x + 4) % 5 == 0:
                    self.setSuitCondition(suitId, 'headroller2calculator', 1, 10, 'setBoth')
            if self.battle.activeSuits[i].dna.name == 'safesupervis': #safety supervisor
                if len(self.battle.activeSuits) >= 6 and (x + 1) % 2 == 0:
                    self.setSuitCondition(suitId, 'highpressurecalculator', 1, 10, 'setBoth')
                if (x + 3) % 5 == 0:
                    self.setSuitCondition(suitId, 'promotioncalculator', 1, 10, 'setBoth')
                if (x + 1) % 3 == 0:
                    self.setSuitCondition(suitId, 'heatwavecalculationcalculator', 1, 10, 'setBoth')
            if self.battle.activeSuits[i].dna.name == 'ubuster': #union buster
                if x % 4 == 0:
                    self.setSuitCondition(suitId, 'contractenforcementcalculator', 1, 10, 'setBoth')
                if (x + 2) % 3 == 0:
                    self.setSuitCondition(suitId, 'unionbustercalculator', 1, 10, 'setBoth')
                if (x + 1) % 3 == 0:
                    self.setSuitCondition(suitId, 'breachcalculator', 1, 10, 'setBoth')
                if x % 3 == 0:
                    self.setSuitCondition(suitId, 'unionduescalculationcalculator', 1, 10, 'setBoth')
            if self.battle.activeSuits[i].dna.name == 'racket': #racketeer
                if (x + 1) % 2 == 0:
                    self.setSuitCondition(suitId, 'profiteeringcalculator', 1, 10, 'setBoth')
                if (x + 1) % 4 == 0:
                    self.setSuitCondition(suitId, 'extortioncalculator', 1, 10, 'setBoth')
                if (x + 2) % 4 == 0:
                    self.setSuitCondition(suitId, 'hustlingcalculator', 1, 10, 'setBoth')
            if self.battle.activeSuits[i].dna.name == 'radiog': #radiographer
                if (x + 4) % 5 == 0:
                    self.setSuitCondition(suitId, 'radioinfrequencycalculator', 1, 10, 'setBoth')
                if x % 3 == 0:
                    self.setSuitCondition(suitId, 'overmodulatedcalculator', 1, 10, 'setBoth')
                #if (x + 4) % 5 == 0:
                    #self.setSuitCondition(suitId, 'dancesessioncalculator', 1, 10, 'setBoth')
                if (x + 2) % 3 == 0:
                    self.setSuitCondition(suitId, 'hottakecalculator', 1, 10, 'setBoth')
            if self.battle.activeSuits[i].dna.name == 'fmaker':  # filmmaker
                if x % 2 == 0:
                    self.setSuitCondition(suitId, 'filmmakercalculator', 1, 10, 'setBoth')
            if self.battle.activeSuits[i].dna.name == 'director':  # director
                if x % 3 == 0:
                    self.setSuitCondition(suitId, 'directorcalculator', 1, 10, 'setBoth')
            if self.battle.activeSuits[i].dna.name == 'choreo':  # choreographer
                if x % 2 == 0:
                    self.setSuitCondition(suitId, 'choreocalculator', 1, 10, 'setBoth')
            if self.battle.activeSuits[i].dna.name == 'cinema':  # photographer
                if x % 2 == 0:
                    self.setSuitCondition(suitId, 'cinemacalculator', 1, 10, 'setBoth')
            if self.battle.activeSuits[i].dna.name == 'hroller':  # high roller phase 1
                if (x + 1) % 2 == 0:
                    self.setSuitCondition(suitId, 'gametimecalculator', 1, 10, 'setBoth')
            if self.battle.activeSuits[i].dna.name == 'videog':  # videographer
                if (x + 2) % 3 == 0:
                    self.setSuitCondition(suitId, 'electricshockcalculator', 1, 10, 'setBoth')

    def __calculateSuitAttacksLawbotLitigation(self):
        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId

            # Gag Ban Retaliations & DOT
            if self.battle.activeSuits[i].dna.name == 'sgoat':
                if self.TurnsElapsed % 1 == 0:
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'ScapegoatCourtRecordBan', # Gavel Court Record Ban Retaliation
                     'animName': 'nothing',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_GROUP}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
            if self.suitHasCondition(suitId, 'deadcase') and not self.suitHasCondition(suitId, 'dotfinished') and self.battle.activeSuits[i].dna.name in SuitBattleGlobals.SpecialCogDict and not self.battle.activeSuits[i].dna.name == 'caseman':
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': '',
                                            'name': 'CaseManagerLegallyBound',  # Legally Bound for when Case Manager is defeated
                                            'animName': 'nothing',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_GROUP}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)

                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
            if self.suitHasCondition(suitId, 'deadcase') and not self.suitHasCondition(suitId, 'healfinished') and self.battle.activeSuits[i].dna.name in SuitBattleGlobals.SpecialCogDict and not self.battle.activeSuits[i].dna.name == 'caseman':
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': '',
                                            'name': 'CaseManagerInsurance',  # Insurance for when Case Manager is defeated
                                            'animName': 'nothing',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
            if self.battle.activeSuits[i].dna.name == 'caseman':
                if self.TurnsElapsed % 1 == 0:
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'CaseManagerInsurance', # Insurance Healing
                     'animName': 'nothing',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                    attack[SUIT_ATK_COL] = {'suitName': '',
                     'name': 'CaseManagerLegallyBound', # Legally Bound
                     'animName': 'nothing',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_GROUP}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)

                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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

            # Primary Cheats
        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'stenog':
                if self.suitHasCondition(suitId, 'sanctioncalculator2') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'sanctioncalculator2') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'StenographerSanctionBindings', # Court Sanction Legal Bindings Retaliation
                     'animName': 'sanction',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_GROUP}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
            if self.battle.activeSuits[i].dna.name == 'caseman':
                if self.suitHasCondition(suitId, 'insurancecalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'insurancecalculator') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'CaseManagerInsurancePlan', # Insurance Plan
                     'animName': 'throw-insurance',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
            if self.battle.activeSuits[i].dna.name == 'sgoat':
                if self.suitHasCondition(suitId, 'gavelcalculator2'):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'ScapegoatBarnyardBash', # Suppression Revert
                     'animName': 'nothing',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_GROUP}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
            if self.battle.activeSuits[i].dna.name == 'lgator':
                if self.suitHasCondition(suitId, 'snappedcalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'snappedcalculator') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'LitigatorSnap', # Snap Most Dangerous
                     'animName': 'throw-object',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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

            # Secondary Cheats
        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'stenog':
                if self.suitHasCondition(suitId, 'costscalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'costscalculator') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'SynergyFees', # Court Costs
                     'animName': 'magic3',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_GROUP}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'sanctioncalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'sanctioncalculator') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'StenographerSanction', # Court Sanction Regular
                     'animName': 'sanction',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
            if self.battle.activeSuits[i].dna.name == 'sgoat':
                if self.getSuitConditionTurns(suitId, 'enraged') == 1 and self.battle.activeSuits[i].currHP > 0:
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'ScapegoatShieldsUp', # Shield's Up
                     'animName': 'defense',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.getSuitConditionModifier(suitId, 'rageBuilding') >= 100 and self.battle.activeSuits[i].currHP > 0:
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'ScapegoatEnraged', # Enraged
                     'animName': 'rage',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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

            # Gag Banning & End Of Round Cheats
        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.suitHasCondition(suitId, 'gavelcalculator') and not self.__suitCanAttack(suitId) and \
                    self.battle.activeSuits[i].currHP > 0:
                attack = self.__getAbilityQueued(suitId)
                self.battle.suitAttacks.append(attack)
            if self.suitHasCondition(suitId, 'gavelcalculator') and self.__suitCanAttack(suitId):
                attack = getDefaultSuitAttack()
                attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                        'name': 'ScapegoatGavel',  # Suppression
                                        'animName': 'throw-paper',
                                        'hp': 0,
                                        'acc': 100,
                                        'freq': 0,
                                        'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                if attack[SUIT_TGT_COL] == []:
                    continue
                attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                self.__calcSuitAtkHpALT(attack)
                if attack[SUIT_ATK_COL]:
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
            if self.battle.activeSuits[i].dna.name == 'caseman':
                if self.suitHasCondition(suitId, 'bindingscalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'bindingscalculator') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'CaseManagerLegalBindings', # Legal Bindings
                     'animName': 'throw-object',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'bindingscalculator2') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'bindingscalculator2') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'CaseManagerLegalBindings2', # Legal Bindings
                     'animName': 'throw-object',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
            if self.battle.activeSuits[i].dna.name == 'lgator':
                if self.suitHasCondition(suitId, 'bashcalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'bashcalculator') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'LitigatorBayouBash', # Bayou Bash
                     'animName': 'none',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'bellowcalculator') and self.deadSuits > 0 and self.battle.activeSuits[i].currHP > 0:
                    self.setSuitCondition(suitId, 'bellowcalculator', 0, 0, 'setBoth')
                if self.suitHasCondition(suitId, 'bellowcalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'bellowcalculator') and self.__suitCanAttack(suitId) and not self.deadSuits > 0:
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'LitigatorBayouBellow', # Bayou Bellow
                     'animName': 'bellow',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'bellowcalculator2') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'bellowcalculator2') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'LitigatorBayouBellow', # Bayou Bellow
                     'animName': 'bellow',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
            if self.battle.activeSuits[i].dna.name == 'stenog':
                if self.suitHasCondition(suitId, 'calculatingcalculator') and self.battle.activeSuits[i].currHP > 0:
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'CalculatingFees', # Calculating Costs
                     'animName': 'calculating-costs',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'BanLevel%s' % random.choice(['45', '46', '47', '48', '56', '57', '58', '67', '68', '78']),
                     'animName': 'cease',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_GROUP}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'BanLevel%s' % random.randint(4, 8),
                     'animName': 'cease',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_GROUP}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
            if self.battle.activeSuits[i].dna.name == 'caseman':
                if self.TurnsElapsed % 1 == 0 and self.suitHasCondition(suitId, 'ban2tracks') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'Ban%s' % random.choice(['ToonupTrap', 'ToonupLure', 'ToonupThrow', 'ToonupSquirt', 'ToonupZap', 'ToonupSound', 'ToonupDrop', 'TrapLure', 'TrapThrow', 'TrapSquirt', 'TrapZap', 'TrapSound', 'TrapDrop', 'LureThrow', 'LureSquirt', 'LureZap', 'LureSound', 'LureDrop', 'ThrowSquirt', 'ThrowZap', 'ThrowSound', 'ThrowDrop', 'SquirtZap', 'SquirtSound', 'SquirtDrop', 'ZapSound', 'ZapDrop', 'SoundDrop']),
                     'animName': 'cease',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_GROUP}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'Ban%s' % random.choice(['Toonup', 'Trap', 'Lure', 'Throw', 'Squirt', 'Zap', 'Sound', 'Drop']),
                     'animName': 'cease',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_GROUP}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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

    def __calculateSuitAttacksBossbotLitigation(self):
        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId

            # Gag Ban Retaliations & DOT
            if self.battle.activeSuits[i].dna.name == 'ambass':
                if self.suitHasCondition(suitId, 'headrollertargetcalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'headrollertargetcalculator') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'AmbassadorTargetCheck',
                     'animName': 'throw-object',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'ambtarget2'):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                      'name': 'AmbassadorHeadRoller', # Advancement
                     'animName': 'snap',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'ambtarget3'):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                      'name': 'AmbassadorHeadRoller2', # Advancement
                     'animName': 'snap',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'ambtarget4'):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'AmbassadorHeadRoller3', # Advancement
                     'animName': 'snap',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'ambtarget5'):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                      'name': 'AmbassadorHeadRoller4', # Advancement
                     'animName': 'snap',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'ambtarget6'):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'AmbassadorHeadRoller5', # Advancement
                     'animName': 'snap',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
            if self.battle.activeSuits[i].dna.name == 'phouse':
                if self.suitHasCondition(suitId, 'gagbansnipe') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'gagbansnipe') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'PowerhouseSnipeGagBan', # Snipe Retaliation For Gag Bans
                     'animName': 'magic3-alt',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_GROUP}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
            if self.battle.activeSuits[i].dna.name == 'phouse':
                if self.suitHasCondition(suitId, 'bookkeepersnipe') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'bookkeepersnipe') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'PowerhouseSnipeBookkept', # Snipe Retaliation For Bookkeeping
                     'animName': 'magic3-alt',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_GROUP}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
            if self.suitHasCondition(suitId, 'deadpower') and not self.suitHasCondition(suitId, 'dotfinished') and self.battle.activeSuits[i].dna.name in SuitBattleGlobals.SpecialCogDict and not self.battle.activeSuits[i].dna.name == 'caseman':
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'PowerhouseBurnDamage',  # Slow Burn
                                            'animName': 'nothing',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_GROUP}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
            if self.battle.activeSuits[i].dna.name == 'phouse': #powerhouse
                if self.TurnsElapsed % 1 == 0:
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'PowerhouseBurnDamage',  # Slow Burn
                                            'animName': 'nothing',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_GROUP}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'collectcallsnipe') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'collectcallsnipe') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'PowerhouseSnipeCollectCall', # Snipe Retaliation Collect Call
                     'animName': 'magic3-alt',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_GROUP}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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

            # Primary Cheats
        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'ambass':  # ambassador
                if self.suitHasCondition(suitId, 'advancementcalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'advancementcalculator') and not self.suitHasCondition(suitId, 'headroller2calculator') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'TargetCheck',
                     'animName': 'throw-object',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'target2'):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                      'name': 'AmbassadorAdvancement', # Advancement
                     'animName': 'throw-paper',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'target3'):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                      'name': 'AmbassadorAdvancement2', # Advancement
                     'animName': 'throw-paper',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'target4'):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'AmbassadorAdvancement3',  # Advancement
                                            'animName': 'throw-paper',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'target5'):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                      'name': 'AmbassadorAdvancement4', # Advancement
                     'animName': 'throw-paper',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'target6'):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'AmbassadorAdvancement5', # Advancement
                     'animName': 'throw-paper',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'refinementcalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'refinementcalculator') and not self.suitHasCondition(suitId, 'headroller2calculator') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'AmbassadorRefinement', # Refinement
                     'animName': 'throw-object',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'refinemmanagercalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'refinemanagercalculator') and not self.suitHasCondition(suitId, 'headroller2calculator') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'AmbassadorRefinementManager', # Refinement Manager
                     'animName': 'throw-object',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'headroller2calculator') and self.suitHasCondition(suitId, 'phase3') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'headroller2calculator') and not len(self.battle.activeSuits) > 1 and self.suitHasCondition(suitId, 'phase3') and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'headroller2calculator') and len(self.battle.activeSuits) > 1 and self.suitHasCondition(suitId, 'phase3') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'AmbassadorGhostMentality', # Ghost Mentality
                     'animName': 'deadwood',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'headroller2calculator') and not len(self.battle.activeSuits) > 1 and not self.suitHasCondition(suitId, 'phase3') and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'headroller2calculator') and not self.suitHasCondition(suitId, 'phase3') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'headroller2calculator') and len(self.battle.activeSuits) > 1 and not self.suitHasCondition(suitId, 'phase3') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'AmbassadorHeadRollerGroup', # Group Head Roller
                     'animName': 'snap',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
            if self.battle.activeSuits[i].dna.name == 'bkeeper':
                if self.suitHasCondition(suitId, 'explodingcalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'explodingcalculator') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'BookkeeperExplodingDocument', # Paper Rain
                     'animName': 'magic3',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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

            # Secondary Cheats
        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'phouse': #powerhouse
                if self.suitHasCondition(suitId, 'mulligansnipe') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'mulligansnipe') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'PowerhouseSnipeMulligan', # Snipe Retaliation For Mulligan Attacks
                     'animName': 'magic3-alt',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_GROUP}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
            if self.battle.activeSuits[i].dna.name == 'bkeeper':  # bookkeeper
                if self.suitHasCondition(suitId, 'papercutcalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'papercutcalculator') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'BookkeeperPaperCut', # Paper Cut
                     'animName': 'throw-paper',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'bookkeepingcalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'bookkeepingcalculator') and self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'BookkeeperBookkeeping', # Bookkeeping
                     'animName': 'effort',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
            if self.battle.activeSuits[i].dna.name == 'wtapper':  # wiretapper
                if self.suitHasCondition(suitId, 'costscalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'costscalculator') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'WiretapperCollectCallDamage', # Court Costs
                     'animName': 'magic3',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_GROUP}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'collectcallcalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'collectcallcalculator') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'WiretapperCollectCall', # Collect Call
                     'animName': 'snap',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'busycalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'busycalculator') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'WiretapperBusySignal',  # Busy Signal
                                            'animName': 'cease',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'voicemailcalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'voicemailcalculator') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'WiretapperVoicemail', # Voicemail Immunity
                     'animName': 'phone',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'brokenconnectioncalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'brokenconnectioncalculator') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'WiretapperBrokenConnection', # Broken Connection
                     'animName': 'pie-small-react',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
            if self.battle.activeSuits[i].dna.name == 'ambass': #ambassador
                if self.battle.activeSuits[i].currHP <= 2000 and not self.suitHasCondition(suitId, 'phase3') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'AmbassadorPhase2', # 'Phase 2'
                     'animName': 'pie-small-react',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'bashcalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'bashcalculator') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'AmbassadorManagerialProtection', # Managerial Protection
                     'animName': 'snap',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'AmbassadorDamageUp', # Compensation
                     'animName': 'summon',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'AmbassadorManagerialProtectionImmunity', # Managerial Protection Immunity
                     'animName': 'cease',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
            if self.battle.activeSuits[i].dna.name == 'ambass':
                if self.deadSuits == 1 and self.battle.activeSuits[i].currHP > 0:
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'AmbassadorMulligan',  # Extra Attack for Dead Suits
                                            'animName': 'golf-club-swing',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.deadSuits == 2 and self.battle.activeSuits[i].currHP > 0:
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'AmbassadorMulligan',  # Extra Attack for Dead Suits
                                            'animName': 'golf-club-swing',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_DOUBLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.deadSuits == 3 and self.battle.activeSuits[i].currHP > 0:
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'AmbassadorMulligan',  # Extra Attack for Dead Suits
                                            'animName': 'golf-club-swing',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_TRIPLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.deadSuits > 3 and self.battle.activeSuits[i].currHP > 0:
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'AmbassadorMulligan',  # Extra Attack for Dead Suits
                                            'animName': 'golf-club-swing',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_GROUP}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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

            # End Of Round & Gag Ban Cheats
        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'phouse': #powerhouse
                if self.suitHasCondition(suitId, 'vulnerablesnipe') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'vulnerablesnipe') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'PowerhouseSnipeVulnerable', # Snipe Retaliation Vulnerabilities
                     'animName': 'magic3-alt',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_GROUP}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
            if self.battle.activeSuits[i].dna.name == 'phouse': #powerhouse
                if self.getSuitConditionModifier(suitId, 'powerhouseRotation') >= 100 and self.suitHasCondition(suitId, 'desperation') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.getSuitConditionModifier(suitId, 'powerhouseRotation') >= 100 and self.suitHasCondition(suitId, 'desperation') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'PowerhouseSyphonDesperation', # Desperation Syphon For All Cogs
                     'animName': 'scabbard',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'rotationcalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'rotationcalculator') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = random.choice([{'suitName': self.battle.activeSuits[i].dna.name,
                      'name': 'PowerhouseAbsorb',
                      'animName': 'defense',
                      'hp': 0,
                      'acc': 100,
                      'freq': 0,
                      'group': SuitBattleGlobals.ATK_TGT_SINGLE},
                     {'suitName': self.battle.activeSuits[i].dna.name,
                      'name': 'PowerhouseSoakImmune',
                      'animName': 'nothing',
                      'hp': 0,
                      'acc': 100,
                      'freq': 0,
                      'group': SuitBattleGlobals.ATK_TGT_SINGLE},
                                                          {'suitName': self.battle.activeSuits[i].dna.name,
                                                           'name': 'PowerhouseLureImmune',
                                                           'animName': 'nothing',
                                                           'hp': 0,
                                                           'acc': 100,
                                                           'freq': 0,
                                                           'group': SuitBattleGlobals.ATK_TGT_SINGLE},
                     {'suitName': self.battle.activeSuits[i].dna.name,
                      'name': 'PowerhouseSyphon',
                      'animName': 'summon',
                      'hp': 0,
                      'acc': 100,
                      'freq': 0,
                      'group': SuitBattleGlobals.ATK_TGT_SINGLE}]) # Rotation Of Conditions
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                    self.setSuitCondition(suitId, 'rotationcalculator', 0, 0, 'setBoth')
                if self.getSuitConditionModifier(suitId, 'powerhouseRotation') >= 100 and self.suitHasCondition(suitId, 'lureImmune') and self.__suitCanAttack(suitId):
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.getSuitConditionModifier(suitId, 'powerhouseRotation') >= 100 and self.suitHasCondition(suitId, 'lureImmune') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = random.choice([{'suitName': self.battle.activeSuits[i].dna.name,
                      'name': 'PowerhouseAbsorb',
                      'animName': 'defense',
                      'hp': 0,
                      'acc': 100,
                      'freq': 0,
                      'group': SuitBattleGlobals.ATK_TGT_SINGLE},
                     {'suitName': self.battle.activeSuits[i].dna.name,
                      'name': 'PowerhouseSoakImmune',
                      'animName': 'nothing',
                      'hp': 0,
                      'acc': 100,
                      'freq': 0,
                      'group': SuitBattleGlobals.ATK_TGT_SINGLE},
                                                          {'suitName': self.battle.activeSuits[i].dna.name,
                                                           'name': 'PowerhouseLureImmune',
                                                           'animName': 'nothing',
                                                           'hp': 0,
                                                           'acc': 100,
                                                           'freq': 0,
                                                           'group': SuitBattleGlobals.ATK_TGT_SINGLE},
                     {'suitName': self.battle.activeSuits[i].dna.name,
                      'name': 'PowerhouseSyphon',
                      'animName': 'summon',
                      'hp': 0,
                      'acc': 100,
                      'freq': 0,
                      'group': SuitBattleGlobals.ATK_TGT_SINGLE}]) # Rotation Of Conditions
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.getSuitConditionModifier(suitId, 'powerhouseRotation') >= 100 and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.getSuitConditionModifier(suitId, 'powerhouseRotation') >= 100 and self.suitHasCondition(suitId, 'lureImmune') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = random.choice([{'suitName': self.battle.activeSuits[i].dna.name,
                      'name': 'PowerhouseAbsorb',
                      'animName': 'defense',
                      'hp': 0,
                      'acc': 100,
                      'freq': 0,
                      'group': SuitBattleGlobals.ATK_TGT_SINGLE},
                     {'suitName': self.battle.activeSuits[i].dna.name,
                      'name': 'PowerhouseSoakImmune',
                      'animName': 'nothing',
                      'hp': 0,
                      'acc': 100,
                      'freq': 0,
                      'group': SuitBattleGlobals.ATK_TGT_SINGLE},
                     {'suitName': self.battle.activeSuits[i].dna.name,
                      'name': 'PowerhouseSyphon',
                      'animName': 'summon',
                      'hp': 0,
                      'acc': 100,
                      'freq': 0,
                      'group': SuitBattleGlobals.ATK_TGT_SINGLE}]) # Rotation Of Conditions
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.getSuitConditionModifier(suitId, 'powerhouseRotation') >= 100 and self.suitHasCondition(suitId, 'soakImmune') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = random.choice([{'suitName': self.battle.activeSuits[i].dna.name,
                      'name': 'PowerhouseAbsorb',
                      'animName': 'defense',
                      'hp': 0,
                      'acc': 100,
                      'freq': 0,
                      'group': SuitBattleGlobals.ATK_TGT_SINGLE},
                     {'suitName': self.battle.activeSuits[i].dna.name,
                      'name': 'PowerhouseLureImmune',
                      'animName': 'nothing',
                      'hp': 0,
                      'acc': 100,
                      'freq': 0,
                      'group': SuitBattleGlobals.ATK_TGT_SINGLE},
                     {'suitName': self.battle.activeSuits[i].dna.name,
                      'name': 'PowerhouseSyphon',
                      'animName': 'summon',
                      'hp': 0,
                      'acc': 100,
                      'freq': 0,
                      'group': SuitBattleGlobals.ATK_TGT_SINGLE}]) # Rotation Of Conditions
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.getSuitConditionModifier(suitId, 'powerhouseRotation') >= 100 and self.suitHasCondition(suitId, 'shielding') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = random.choice([
                     {'suitName': self.battle.activeSuits[i].dna.name,
                      'name': 'PowerhouseSoakImmune',
                      'animName': 'nothing',
                      'hp': 0,
                      'acc': 100,
                      'freq': 0,
                      'group': SuitBattleGlobals.ATK_TGT_SINGLE},
                     {'suitName': self.battle.activeSuits[i].dna.name,
                      'name': 'PowerhouseLureImmune',
                      'animName': 'nothing',
                      'hp': 0,
                      'acc': 100,
                      'freq': 0,
                      'group': SuitBattleGlobals.ATK_TGT_SINGLE},
                     {'suitName': self.battle.activeSuits[i].dna.name,
                      'name': 'PowerhouseSyphon',
                      'animName': 'summon',
                      'hp': 0,
                      'acc': 100,
                      'freq': 0,
                      'group': SuitBattleGlobals.ATK_TGT_SINGLE}]) # Rotation Of Conditions
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.getSuitConditionModifier(suitId, 'powerhouseRotation') >= 100 and self.suitHasCondition(suitId, 'shielding') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = random.choice([
                     {'suitName': self.battle.activeSuits[i].dna.name,
                      'name': 'PowerhouseSoakImmune',
                      'animName': 'nothing',
                      'hp': 0,
                      'acc': 100,
                      'freq': 0,
                      'group': SuitBattleGlobals.ATK_TGT_SINGLE},
                     {'suitName': self.battle.activeSuits[i].dna.name,
                      'name': 'PowerhouseLureImmune',
                      'animName': 'nothing',
                      'hp': 0,
                      'acc': 100,
                      'freq': 0,
                      'group': SuitBattleGlobals.ATK_TGT_SINGLE},
                     {'suitName': self.battle.activeSuits[i].dna.name,
                      'name': 'PowerhouseSyphon',
                      'animName': 'summon',
                      'hp': 0,
                      'acc': 100,
                      'freq': 0,
                      'group': SuitBattleGlobals.ATK_TGT_SINGLE}]) # Rotation Of Conditions
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.TurnsElapsed % 1 == 0 and self.suitHasCondition(suitId, 'desperation') and not self.__suitCanAttack(suitId) and \
                        self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.TurnsElapsed % 1 == 0 and self.suitHasCondition(suitId, 'desperation') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'PowerhouseGeneration',  # Generation
                                            'animName': 'effort',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
            if self.battle.activeSuits[i].dna.name == 'wtapper':
                if self.suitHasCondition(suitId, 'wiretappedcalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'wiretappedcalculator') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'WiretapperWiretapped', # Wiretapped
                     'animName': 'phone',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_GROUP}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'calculatingcalculator') and self.battle.activeSuits[i].currHP > 0:
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'WiretapperCollectCall2', # Calculating Collect Call Dues
                     'animName': 'calculating-costs',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'Ban%s' % random.choice(
                                                ['Toonup', 'Trap', 'Lure', 'Throw', 'Squirt', 'Zap', 'Sound', 'Drop']),
                     'animName': 'cease',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_GROUP}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                          'name': 'BanLevel%s' % random.randint(4, 8),
                     'animName': 'cease',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_GROUP}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
            if self.battle.activeSuits[i].dna.name == 'phouse':
                if self.suitHasCondition(suitId, 'explodingcalculator2') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'explodingcalculator2') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'BookkeeperExplodingDocument', # Paper Rain
                     'animName': 'magic3',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
            if self.battle.activeSuits[i].dna.name == 'phouse' and not self.suitHasCondition(suitId, 'dead'):
                if self.battle.activeSuits[i].currHP <= 0 and not self.__suitCanAttack(suitId) and self.suitHasCondition(suitId, 'shielding'):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'DeathCheck', # Check for Death
                     'animName': 'nothing',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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

    def __calculateSuitAttacksSellbotLitigation(self):
        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId

            # Gag Ban Retaliations & DOT
            if self.battle.activeSuits[i].dna.name == 'ubuster':
                if self.TurnsElapsed % 1 == 0:
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'UnionBusterUnionBusterDamage', # DOT Union Buster
                     'animName': 'nothing',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_GROUP}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)

                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                # if self.TurnsElapsed % 1 == 0 and self.__suitCanAttack(suitId):
                #     attack = getDefaultSuitAttack()
                #     attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                #     attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                #      'name': 'UnionBusterBreachOfContract2', # Breach Of Contract Soaked
                #      'animName': 'sanction',
                #      'hp': 0,
                #      'acc': 100,
                #      'freq': 0,
                #      'group': SuitBattleGlobals.ATK_TGT_GROUP}
                #     attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                #     if attack[SUIT_TGT_COL] == []:
                #         continue
                #     attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                #     self.__calcSuitAtkHpALT(attack)
                #     if attack[SUIT_ATK_COL]:
                #         if self.__suitAtkAffectsGroup(attack):
                #             for currTgt in self.battle.activeToons:
                #                 self.__updateSuitAtkStat(currTgt)

                #         else:
                #             for currTgt in attack[SUIT_TGT_COL]:
                #                 self.__updateSuitAtkStat(self.battle.activeToons[currTgt])
                #     targets = self.__createSuitTargetList(attack)
                #     allTargetsDead = True
                #     for currTgt in targets:
                #         if self.__getToonHp(currTgt) > 0:
                #             allTargetsDead = False
                #             break

                #     if allTargetsDead:
                #         attack = getDefaultSuitAttack()
                #     if self.__attackHasHit(attack, suit=1):
                #         self.__applySuitAttackDamages(attack, self.battle.findSuit(attack[SUIT_ID_COL]))
                #     attack[SUIT_BEFORE_TOONS_COL] = 0
                #     self.battle.suitAttacks.append(attack)
            if self.suitHasCondition(suitId, 'deadunion') and not self.suitHasCondition(suitId, 'dotfinished') and self.battle.activeSuits[i].dna.name in SuitBattleGlobals.SpecialCogDict and not self.battle.activeSuits[i].dna.name == 'ubuster':
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': '',
                                            'name': 'UnionBusterUnionBusterDamage',  # Union Buster for when Union Buster is defeated
                                            'animName': 'nothing',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_GROUP}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)

                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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

            # Primary Cheats
        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'ubuster':
                if self.suitHasCondition(suitId, 'breachgagban') and not self.__suitCanAttack(suitId) and \
                        self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'breachgagban') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'UnionBusterBreachOfContract4', # Breach Of Contract Gag Ban Retaliation
                     'animName': 'sanction',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_GROUP}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'unionbustcalculator') and not self.__suitCanAttack(suitId) and \
                        self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'unionbustcalculator') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'UnionBusterUnionBust', # Union Bust
                     'animName': 'quick-jump',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'unionwagescalculator') and not self.__suitCanAttack(suitId) and \
                        self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'unionwagescalculator') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'UnionBusterUnionWages', # Union Wages
                     'animName': 'calculator',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'unionbustercalculator') and not self.__suitCanAttack(suitId) and \
                        self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'unionbustercalculator') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'UnionBusterUnionBuster', # Union Buster
                     'animName': 'summon',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
            if self.battle.activeSuits[i].dna.name == 'radiog':
                if self.suitHasCondition(suitId, 'hottakecalculator') and not self.__suitCanAttack(suitId) and \
                        self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'hottakecalculator') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'RadiographerHotTake', # Hot Take
                     'animName': 'throw-object',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'overmodulatedcalculator') and not len(self.battle.activeSuits) > 1 and self.battle.activeSuits[i].currHP > 0  and self.__suitCanAttack(suitId):
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'overmodulatedcalculator') and not self.__suitCanAttack(suitId) and \
                        self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'overmodulatedcalculator') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'TargetCheck', # Target Check
                     'animName': 'nothing',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'target2'):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'RadiographerOvermodulated', # Overmodulated
                     'animName': 'sanction',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'target3'):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'RadiographerOvermodulated2', # Overmodulated
                     'animName': 'sanction',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'target4'):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'RadiographerOvermodulated3', # Overmodulated
                     'animName': 'sanction',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'target5'):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'RadiographerOvermodulated4', # Overmodulated
                     'animName': 'sanction',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'target6'):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'RadiographerOvermodulated5', # Overmodulated
                     'animName': 'sanction',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
            if self.battle.activeSuits[i].dna.name == 'safesupervis':
                if self.suitHasCondition(suitId, 'promotioncalculator') and not len(self.battle.activeSuits) > 1 and self.battle.activeSuits[i].currHP > 0 and self.__suitCanAttack(suitId):
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'promotioncalculator') and not self.__suitCanAttack(suitId) and \
                        self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'promotioncalculator') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'TargetCheck', # Target Check for Promotion
                     'animName': 'nothing',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'target2'):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'SafetyPromotion', # Promotion
                     'animName': 'mob-mentality',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'target3'):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'SafetyPromotion2', # Promotion
                     'animName': 'mob-mentality',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'target4'):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'SafetyPromotion3', # Promotion
                     'animName': 'mob-mentality',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'target5'):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'SafetyPromotion4', # Promotion
                     'animName': 'mob-mentality',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'target6'):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'SafetyPromotion5', # Promotion
                     'animName': 'mob-mentality',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
            if self.battle.activeSuits[i].dna.name == 'radiog':
                if self.suitHasCondition(suitId, 'radioinfrequencycalculator') and not self.__suitCanAttack(suitId) and \
                        self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'radioinfrequencycalculator') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'RadiographerRadioInfrequency', # Radio Infrequency
                     'animName': 'nothing',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_GROUP}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
            if self.battle.activeSuits[i].dna.name == 'racket':
                if self.suitHasCondition(suitId, 'extortioncalculator') and not self.__suitCanAttack(suitId) and \
                        self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'extortioncalculator') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'RacketeerExtortion', # Extortion
                     'animName': 'magic3',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_GROUP}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'profiteeringcalculator') and not len(self.battle.activeSuits) > 1 and self.battle.activeSuits[i].currHP > 0  and self.__suitCanAttack(suitId):
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'profiteeringcalculator') and not self.__suitCanAttack(suitId) and \
                        self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'profiteeringcalculator') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'TargetCheck', # Target Check for Profiteering
                     'animName': 'nothing',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'target2'):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'RacketeerProfiteering', # Profiteering
                     'animName': 'come-on',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'target3'):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'RacketeerProfiteering2', # Profiteering
                     'animName': 'come-on',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'target4'):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'RacketeerProfiteering3', # Profiteering
                     'animName': 'come-on',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'target5'):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'RacketeerProfiteering4', # Profiteering
                     'animName': 'come-on',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'target6'):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'RacketeerProfiteering5', # Profiteering
                     'animName': 'come-on',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'RacketeerCompensation', # Compensation
                     'animName': 'rush-job',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'extortioncalculator2') and not self.__suitCanAttack(suitId) and \
                        self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'extortioncalculator2') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'RacketeerExtortion2', # Extortion Retaliation
                     'animName': 'magic3',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_GROUP}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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

            # Secondary Cheats
        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'ubuster':
                if self.suitHasCondition(suitId, 'breachvulnerable') and not self.__suitCanAttack(suitId) and \
                        self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'breachvulnerable') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'UnionBusterBreachOfContract3', # Breach Of Contract Vulnerabilities
                     'animName': 'sanction',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_GROUP}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'unionduescalculator') and not self.__suitCanAttack(suitId) and \
                        self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'unionduescalculator') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'UnionBusterUnionDues', # Union Dues
                     'animName': 'magic3',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_GROUP}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'breachcalculator') and not self.__suitCanAttack(suitId) and \
                        self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'breachcalculator') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'UnionBusterBreachOfContract', # Breach Of Contract
                     'animName': 'sanction',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'unionduescalculationcalculator') and self.battle.activeSuits[i].currHP > 0:
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'UnionBusterUnionCalculator', # Union Dues Calculation
                     'animName': 'calculator',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
            if self.battle.activeSuits[i].dna.name == 'racket':
                if self.suitHasCondition(suitId, 'soaked') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'RacketeerPeckingOrderRetaliationSoak', # Extra Attack for Being Soaked
                     'animName': 'throw-object',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'RacketeerPeckingOrderRetaliation', # Retaliation to Gag Bans
                     'animName': 'throw-object',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_GROUP}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
            if self.battle.activeSuits[i].dna.name == 'safesupervis':
                if self.suitHasCondition(suitId, 'highpressurecalculator') and self.deadSuits > 0 and self.battle.activeSuits[i].currHP > 0:
                    self.setSuitCondition(suitId, 'highpressurecalculator', 0, 0, 'setBoth')
                if self.suitHasCondition(suitId, 'highpressurecalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'highpressurecalculator') and self.__suitCanAttack(suitId) and self.deadSuits == 0:
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'SafetyHighPressure', # High Pressure
                     'animName': 'throw-object',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_GROUP}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'heatwavecalculator') and not self.__suitCanAttack(suitId) and \
                        self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'heatwavecalculator') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'SafetyHeatWave', # Heat Wave
                     'animName': 'magic3-alt',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_GROUP}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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

            # Gag Bans & End Of Round Cheats
        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'ubuster':
                if self.suitHasCondition(suitId, 'contractenforcementcalculator') and not self.__suitCanAttack(suitId) and \
                        self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'contractenforcementcalculator') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'UnionBusterContractEnforcement', # Contract Enforcement
                     'animName': 'throw-paper',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
            if self.battle.activeSuits[i].dna.name == 'radiog':
                if self.suitHasCondition(suitId, 'dancesessioncalculator') and not self.__suitCanAttack(suitId) and \
                        self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'dancesessioncalculator') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'RadiographerDanceSession', # Dance Session
                     'animName': 'song-and-dance',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_GROUP}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
            if self.battle.activeSuits[i].dna.name == 'safesupervis':
                if self.suitHasCondition(suitId, 'heatwavecalculationcalculator') and self.battle.activeSuits[i].currHP > 0:
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'SafetyHeatWaveCalculation', # Calculating Heat Wave
                     'animName': 'soak',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'BanLevel%s' % random.choice(['45', '46', '47', '48', '56', '57', '58', '67', '68', '78']), # Gag Bans
                     'animName': 'cease',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_GROUP}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
            if self.battle.activeSuits[i].dna.name == 'racket':
                if self.TurnsElapsed % 1 == 0 and not self.suitHasCondition(suitId,
                                                                            'hustlingcalculator') and self.__suitCanAttack(
                        suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'RacketeerRacketeering', # Racketeering
                     'animName': 'objection',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_GROUP}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'hustlingcalculator') and not self.__suitCanAttack(suitId) and \
                        self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'hustlingcalculator') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'RacketeerHustling', # Hustling
                     'animName': 'come-on',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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

    def __calculateSuitAttacksHighRoller(self):
        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            x = self.TurnsElapsed
            # Initial Cheats
            if self.battle.activeSuits[i].dna.name == 'videog':  # videographer
                if self.battle.activeSuits[i].currHP <= 0 and not self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'VideographerDeath',  # Videographer Death to Sacrifice All Cogs
                                            'animName': 'snap',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
            if self.battle.activeSuits[i].dna.name == 'bcaster':  # broadcaster
                if self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'BroadcasterViralSensation',  # ViralSensation
                                            'animName': 'magic3',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': random.choice((SuitBattleGlobals.ATK_TGT_SINGLE, SuitBattleGlobals.ATK_TGT_DOUBLE))}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'BroadcasterDonation',  # Donation
                                            'animName': 'nothing',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.battle.activeSuits[i].currHP <= 0 and not self.suitHasCondition(suitId,
                                                                                        'killedbyvideo') and not self.suitHasCondition(suitId,
                                                                                        'dead') and not self.__suitCanAttack(
                    suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'DeathCheck',  # Check for Death
                                            'animName': 'nothing',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.battle.activeSuits[i].currHP <= 0 and not self.suitHasCondition(suitId,
                                                                                        'killedbyvideo') and not self.__suitCanAttack(
                    suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'VideographerVideoStatic',  # Video Static Upon Death
                                            'animName': 'nothing',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
            if self.battle.activeSuits[i].dna.name == 'fmaker':  # filmmaker
                if self.battle.activeSuits[i].currHP <= 0 and not self.suitHasCondition(suitId,
                                                                                        'killedbyvideo') and not self.__suitCanAttack(
                    suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'VideographerVideoStatic',  # Video Static Upon Death
                                            'animName': 'glower',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'filmmakercalculator') and not self.__suitCanAttack(suitId) and \
                        self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'filmmakercalculator') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                             'name': 'FilmmakerCameraRewind',
                                                           'animName': 'throw-object',
                                            'hp': 30,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_DOUBLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.battle.activeSuits[i].currHP < self.battle.activeSuits[i].maxHP and not self.__suitCanAttack(suitId) and \
                        self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.battle.activeSuits[i].currHP < self.battle.activeSuits[i].maxHP and self.__suitCanAttack(
                        suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'FilmmakerBudgetCuts',
                                            'animName': 'throw-paper',
                                            'hp': 30,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
            if self.battle.activeSuits[i].dna.name == 'cinema':  # cinematographer
                if self.battle.activeSuits[i].currHP <= 0 and not self.suitHasCondition(suitId,
                                                                                        'killedbyvideo') and not self.__suitCanAttack(
                    suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'VideographerVideoStatic',  # Video Static Upon Death
                                            'animName': 'glower',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'cinemacalculator') and not self.__suitCanAttack(suitId) and \
                        self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'cinemacalculator') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                             'name': 'FilmmakerCameraFlash',
                                                           'animName': 'glower',
                                            'hp': 30,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.battle.activeSuits[i].currHP < self.battle.activeSuits[i].maxHP and not self.__suitCanAttack(suitId) and \
                        self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.battle.activeSuits[i].currHP < self.battle.activeSuits[i].maxHP and self.__suitCanAttack(
                        suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'FilmmakerBudgetCuts',
                                            'animName': 'throw-paper',
                                            'hp': 30,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
            if self.battle.activeSuits[i].dna.name == 'choreo':  # choreographer
                if self.battle.activeSuits[i].currHP <= 0 and not self.suitHasCondition(suitId,
                                                                                        'killedbyvideo') and not self.__suitCanAttack(
                    suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'VideographerVideoStatic',  # Video Static Upon Death
                                            'animName': 'glower',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'choreocalculator') and not self.__suitCanAttack(suitId) and \
                        self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'choreocalculator') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                             'name': 'ChoreoChoreography',
                                                           'animName': 'song-and-dance',
                                            'hp': 30,
                                            'acc': 25,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_GROUP}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.battle.activeSuits[i].currHP < self.battle.activeSuits[i].maxHP and not self.__suitCanAttack(suitId) and \
                        self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.battle.activeSuits[i].currHP < self.battle.activeSuits[i].maxHP and self.__suitCanAttack(
                        suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'FilmmakerBudgetCuts',
                                            'animName': 'throw-paper',
                                            'hp': 30,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
            if self.battle.activeSuits[i].dna.name == 'director':  # director
                if self.battle.activeSuits[i].currHP <= 0 and not self.suitHasCondition(suitId,
                                                                                        'killedbyvideo') and not self.__suitCanAttack(
                    suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'VideographerVideoStatic',  # Video Static Upon Death
                                            'animName': 'glower',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'extortioncalculator2') and not self.__suitCanAttack(suitId) and \
                        self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'extortioncalculator2') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'DirectorActionRetaliation',
                                            'animName': 'glower',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_GROUP}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'directorcalculator') and not self.__suitCanAttack(suitId) and \
                        self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'directorcalculator') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    if self.battle.activeSuits > 4:
                        attack[SUIT_ATK_COL] = random.choice([{'suitName': self.battle.activeSuits[i].dna.name,
                                                           'name': 'DirectorAction',
                                                           'animName': 'nothing',
                                                           'hp': 0,
                                                           'acc': 100,
                                                           'freq': 0,
                                                           'group': SuitBattleGlobals.ATK_TGT_SINGLE},
                                                          {'suitName': self.battle.activeSuits[i].dna.name,
                                                           'name': 'DirectorCut',
                                                           'animName': 'nothing',
                                                           'hp': 0,
                                                           'acc': 100,
                                                           'freq': 0,
                                                           'group': SuitBattleGlobals.ATK_TGT_SINGLE},
                                                          {'suitName': self.battle.activeSuits[i].dna.name,
                                                           'name': 'DirectorBackToOnes',
                                                           'animName': 'nothing',
                                                           'hp': 0,
                                                           'acc': 100,
                                                           'freq': 0,
                                                           'group': SuitBattleGlobals.ATK_TGT_SINGLE}])
                    else:
                        attack[SUIT_ATK_COL] = random.choice([{'suitName': self.battle.activeSuits[i].dna.name,
                                                               'name': 'DirectorAction',
                                                               'animName': 'nothing',
                                                               'hp': 0,
                                                               'acc': 100,
                                                               'freq': 0,
                                                               'group': SuitBattleGlobals.ATK_TGT_SINGLE},
                                                              {'suitName': self.battle.activeSuits[i].dna.name,
                                                               'name': 'DirectorCut',
                                                               'animName': 'nothing',
                                                               'hp': 0,
                                                               'acc': 100,
                                                               'freq': 0,
                                                               'group': SuitBattleGlobals.ATK_TGT_SINGLE}])
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.battle.activeSuits[i].currHP < self.battle.activeSuits[i].maxHP and not self.__suitCanAttack(suitId) and \
                        self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.battle.activeSuits[i].currHP < self.battle.activeSuits[i].maxHP and self.__suitCanAttack(
                        suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'FilmmakerBudgetCuts',
                                            'animName': 'throw-paper',
                                            'hp': 30,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
            if self.battle.activeSuits[i].dna.name == 'hrollers':
                if self.battle.activeSuits[i].getActualLevel() == 28 and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'HighRollerSingingBlues',  # Blue Silhouette
                                            'animName': 'nothing',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_GROUP}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.battle.activeSuits[i].getActualLevel() == 29 and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'HighRollerBar',  # Red Silhouette
                                            'animName': 'snap',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_GROUP}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.battle.activeSuits[i].getActualLevel() == 29 and self.suitHasCondition(suitId,
                                                                                               'barcalculator') and not \
                        self.battle.activeSuits[i].currHP <= 0:
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'HighRollerBar',  # Red Silhouette
                                            'animName': 'snap',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_GROUP}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.battle.activeSuits[i].getActualLevel() == 30 and not self.battle.activeSuits[i].currHP <= 0:
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'HighRollerSplashback',  # Pink Silhouette
                                            'animName': 'throw-object',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_GROUP}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.battle.activeSuits[i].getActualLevel() == 31 and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'HighRollerDamageReduction',  # Light Blue Silhouette
                                            'animName': 'snap',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_DOUBLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.battle.activeSuits[i].getActualLevel() == 32 and not self.battle.activeSuits[i].currHP <= 0:
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'HighRollerCheerRetaliation',  # Purple Silhouette
                                            'animName': 'glower',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_GROUP}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.battle.activeSuits[i].getActualLevel() == 33 and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'HighRollerDonation',  # White Silhouette
                                            'animName': 'shot5',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'deathcheck'):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'DeathCheck',  # Check for Death
                                            'animName': 'nothing',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.battle.activeSuits[i].getActualLevel() == 34 and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'HighRollerSyphon',  # Magenta Silhouette
                                            'animName': 'sanction',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_GROUP}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
            if self.battle.activeSuits[i].dna.name == 'hroller2':
                if self.TurnsElapsed % 1 == 0 and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'HighRollerBust',
                                            'animName': 'bust',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_GROUP}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
            if self.battle.activeSuits[i].dna.name == 'hroller':
                if self.TurnsElapsed % 1 == 0:
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'HighRollerBust',  # Bust
                                            'animName': 'bust',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_GROUP}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.levelDamage > 0 and self.battle.activeSuits[i].currHP > 0:
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'AbsorbMovieLevel',  # Absorb Damage Movie Level
                                            'animName': 'nothing',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.TurnsElapsed % 3 == 0 and not self.TurnsElapsed == 0 and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'HighRollerCommercialBreak',  # Commercial Break after Puzzle
                                            'animName': 'snap',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'gameovercalculator'):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'HighRollerGameOver',  # Game Over after Using Puzzle
                                            'animName': 'song-and-dance',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_GROUP}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.TurnsElapsed % 3 == 0 and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'HighRollerWheelSpin',  # Wheel Spin
                                            'animName': 'wheelspin',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.TurnsElapsed % 3 == 0 and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = random.choice([{'suitName': self.battle.activeSuits[i].dna.name,
                                                           'name': 'HighRollerPuzzle',
                                                           'animName': 'taunt',
                                                           'hp': 0,
                                                           'acc': 100,
                                                           'freq': 0,
                                                           'group': SuitBattleGlobals.ATK_TGT_SINGLE},
                                                          {'suitName': self.battle.activeSuits[i].dna.name,
                                                           'name': 'HighRollerPuzzleBan',
                                                           'animName': 'cease',
                                                           'hp': 0,
                                                           'acc': 100,
                                                           'freq': 0,
                                                           'group': SuitBattleGlobals.ATK_TGT_SINGLE}])  # Variation of these 2 every round
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.TurnsElapsed % 3 == 0 and not self.TurnsElapsed == 0 and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'HighRollerGameTimeSpawn',  # Spawn After Puzzle
                                            'animName': 'snap',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'gametimecalculator'):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'TargetCheck',  # Checks for Alive Cogs to use Game Time on
                                            'animName': 'nothing',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'target2') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = random.choice([{'suitName': self.battle.activeSuits[i].dna.name,
                                                           'name': 'HighRollerGameTimeCog',
                                                           'animName': 'snap',
                                                           'hp': 0,
                                                           'acc': 100,
                                                           'freq': 0,
                                                           'group': SuitBattleGlobals.ATK_TGT_SINGLE},
                                                          {'suitName': self.battle.activeSuits[i].dna.name,
                                                           'name': 'HighRollerGameTimeCog2',
                                                           'animName': 'snap',
                                                           'hp': 0,
                                                           'acc': 100,
                                                           'freq': 0,
                                                           'group': SuitBattleGlobals.ATK_TGT_SINGLE}])  # Game Time
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'target3') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = random.choice([{'suitName': self.battle.activeSuits[i].dna.name,
                                                           'name': 'HighRollerGameTimeCog3',
                                                           'animName': 'snap',
                                                           'hp': 0,
                                                           'acc': 100,
                                                           'freq': 0,
                                                           'group': SuitBattleGlobals.ATK_TGT_SINGLE},
                                                          {'suitName': self.battle.activeSuits[i].dna.name,
                                                           'name': 'HighRollerGameTimeCog4',
                                                           'animName': 'snap',
                                                           'hp': 0,
                                                           'acc': 100,
                                                           'freq': 0,
                                                           'group': SuitBattleGlobals.ATK_TGT_SINGLE}])  # Game Time
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'target4') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = random.choice([{'suitName': self.battle.activeSuits[i].dna.name,
                                                           'name': 'HighRollerGameTimeCog5',
                                                           'animName': 'snap',
                                                           'hp': 0,
                                                           'acc': 100,
                                                           'freq': 0,
                                                           'group': SuitBattleGlobals.ATK_TGT_SINGLE},
                                                          {'suitName': self.battle.activeSuits[i].dna.name,
                                                           'name': 'HighRollerGameTimeCog6',
                                                           'animName': 'snap',
                                                           'hp': 0,
                                                           'acc': 100,
                                                           'freq': 0,
                                                           'group': SuitBattleGlobals.ATK_TGT_SINGLE}])  # Game Time
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'target5') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = random.choice([{'suitName': self.battle.activeSuits[i].dna.name,
                                                           'name': 'HighRollerGameTimeCog7',
                                                           'animName': 'snap',
                                                           'hp': 0,
                                                           'acc': 100,
                                                           'freq': 0,
                                                           'group': SuitBattleGlobals.ATK_TGT_SINGLE},
                                                          {'suitName': self.battle.activeSuits[i].dna.name,
                                                           'name': 'HighRollerGameTimeCog8',
                                                           'animName': 'snap',
                                                           'hp': 0,
                                                           'acc': 100,
                                                           'freq': 0,
                                                           'group': SuitBattleGlobals.ATK_TGT_SINGLE}])  # Game Time
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'target6') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = random.choice([{'suitName': self.battle.activeSuits[i].dna.name,
                                                           'name': 'HighRollerGameTimeCog9',
                                                           'animName': 'snap',
                                                           'hp': 0,
                                                           'acc': 100,
                                                           'freq': 0,
                                                           'group': SuitBattleGlobals.ATK_TGT_SINGLE},
                                                          {'suitName': self.battle.activeSuits[i].dna.name,
                                                           'name': 'HighRollerGameTimeCog10',
                                                           'animName': 'snap',
                                                           'hp': 0,
                                                           'acc': 100,
                                                           'freq': 0,
                                                           'group': SuitBattleGlobals.ATK_TGT_SINGLE}])  # Game Time
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if len(self.battle.activeSuits) < 6 and self.__suitCanAttack(suitId) and not self.suitHasCondition(
                        suitId, 'spawncalculator'):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'HighRollerGameTimeSpawn',  # Spawn Cogs
                                            'animName': 'snap',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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

        # Secondary Cheats
        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'videog':
                if self.suitHasCondition(suitId, 'hollywoodcalculator') and not self.suitHasCondition(suitId, 'electricshockcalculator') and self.__suitCanAttack(suitId):
                                attack = getDefaultSuitAttack()
                                attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                                attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                                        'name': 'VideographerRisingStarsSacrifice',
                                                        # Rising Stars Sacrifice
                                                        'animName': 'snap',
                                                        'hp': 0,
                                                        'acc': 100,
                                                        'freq': 0,
                                                        'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                                attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                                if attack[SUIT_TGT_COL] == []:
                                    continue
                                attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                                self.__calcSuitAtkHpALT(attack)
                                if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'electricshockcalculator') and self.__suitCanAttack(
                                    suitId) and self.suitHasCondition(suitId, 'phase3'):
                                attack = getDefaultSuitAttack()
                                attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                                attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                                        'name': 'TargetCheck',  # Target Check
                                                        'animName': 'nothing',
                                                        'hp': 0,
                                                        'acc': 100,
                                                        'freq': 0,
                                                        'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                                attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                                if attack[SUIT_TGT_COL] == []:
                                    continue
                                attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                                self.__calcSuitAtkHpALT(attack)
                                if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'target3'):
                                attack = getDefaultSuitAttack()
                                attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                                attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                                        'name': 'VideographerElectricShock',  # Electric Shock
                                                        'animName': 'glower',
                                                        'hp': 0,
                                                        'acc': 100,
                                                        'freq': 0,
                                                        'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                                attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                                if attack[SUIT_TGT_COL] == []:
                                    continue
                                attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                                self.__calcSuitAtkHpALT(attack)
                                if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'target4'):
                                attack = getDefaultSuitAttack()
                                attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                                attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                                        'name': 'VideographerElectricShock2',  # Electric Shock
                                                        'animName': 'glower',
                                                        'hp': 0,
                                                        'acc': 100,
                                                        'freq': 0,
                                                        'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                                attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                                if attack[SUIT_TGT_COL] == []:
                                    continue
                                attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                                self.__calcSuitAtkHpALT(attack)
                                if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'target5'):
                                attack = getDefaultSuitAttack()
                                attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                                attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                                        'name': 'VideographerElectricShock3',  # Electric Shock
                                                        'animName': 'glower',
                                                        'hp': 0,
                                                        'acc': 100,
                                                        'freq': 0,
                                                        'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                                attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                                if attack[SUIT_TGT_COL] == []:
                                    continue
                                attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                                self.__calcSuitAtkHpALT(attack)
                                if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'target6'):
                                attack = getDefaultSuitAttack()
                                attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                                attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                                        'name': 'VideographerElectricShock4',  # Electric Shock
                                                        'animName': 'glower',
                                                        'hp': 0,
                                                        'acc': 100,
                                                        'freq': 0,
                                                        'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                                attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                                if attack[SUIT_TGT_COL] == []:
                                    continue
                                attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                                self.__calcSuitAtkHpALT(attack)
                                if attack[SUIT_ATK_COL]:
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
                if not self.suitHasCondition(suitId, 'phase3') and self.battle.activeSuits[
                                i].currHP <= 7777 and self.__suitCanAttack(suitId):
                                attack = getDefaultSuitAttack()
                                attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                                attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                                        'name': 'VideographerDirectorCuts',  # Director Cuts
                                                        'animName': 'song-and-dance',
                                                        'hp': 0,
                                                        'acc': 100,
                                                        'freq': 0,
                                                        'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                                attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                                if attack[SUIT_TGT_COL] == []:
                                    continue
                                attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                                self.__calcSuitAtkHpALT(attack)
                                if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'silhouettespawn') and not len(
                                    self.battle.activeSuits) > 5 and self.__suitCanAttack(suitId):
                                attack = getDefaultSuitAttack()
                                attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                                attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                                        'name': 'VideographerRisingStarsSilhouette',
                                                        # Rising Stars Silhouette
                                                        'animName': 'shot5',
                                                        'hp': 0,
                                                        'acc': 100,
                                                        'freq': 0,
                                                        'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                                attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                                if attack[SUIT_TGT_COL] == []:
                                    continue
                                attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                                self.__calcSuitAtkHpALT(attack)
                                if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'phase3') and not self.suitHasCondition(suitId,
                                                                                                     'immune') and not self.suitHasCondition(
                                suitId, 'directorscutscalculator') and not self.suitHasCondition(suitId,
                                                                                                 'silhouettespawn') and not len(
                                self.battle.activeSuits) > 5 and self.__suitCanAttack(suitId):
                                attack = getDefaultSuitAttack()
                                attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                                attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                                        'name': 'VideographerRisingStars2',  # Rising Stars w/ Managers
                                                        'animName': 'shot5',
                                                        'hp': 0,
                                                        'acc': 100,
                                                        'freq': 0,
                                                        'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                                attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                                if attack[SUIT_TGT_COL] == []:
                                    continue
                                attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                                self.__calcSuitAtkHpALT(attack)
                                if attack[SUIT_ATK_COL]:
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
                if not self.suitHasCondition(suitId, 'phase3') and not self.suitHasCondition(suitId,
                                                                                                         'immune') and not self.suitHasCondition(
                                suitId, 'silhouettespawn') and not self.suitHasCondition(suitId,
                                                                                         'directorscuts') and not len(
                                self.battle.activeSuits) > 5 and self.__suitCanAttack(suitId):
                                attack = getDefaultSuitAttack()
                                attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                                attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                                        'name': 'VideographerRisingStars',  # Rising Stars Hollywoods
                                                        'animName': 'shot5',
                                                        'hp': 0,
                                                        'acc': 100,
                                                        'freq': 0,
                                                        'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                                attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                                if attack[SUIT_TGT_COL] == []:
                                    continue
                                attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                                self.__calcSuitAtkHpALT(attack)
                                if attack[SUIT_ATK_COL]:
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

                # End Of Round High Roller Attacks
        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'hroller2':
                if self.TurnsElapsed % 1 == 0 and self.suitHasCondition(suitId, 'phase3') and self.__suitCanAttack(
                        suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = random.choice([{'suitName': self.battle.activeSuits[i].dna.name,
                                                           'name': 'HighRollerConduction',
                                                           'animName': 'throw-object',
                                                           'hp': 0,
                                                           'acc': 100,
                                                           'freq': 0,
                                                           'group': SuitBattleGlobals.ATK_TGT_DOUBLE},
                                                          {'suitName': self.battle.activeSuits[i].dna.name,
                                                           'name': 'HighRollerFreeCruise',
                                                           'animName': 'song-and-dance',
                                                           'hp': 0,
                                                           'acc': 100,
                                                           'freq': 0,
                                                           'group': SuitBattleGlobals.ATK_TGT_GROUP},
                                                          {'suitName': self.battle.activeSuits[i].dna.name,
                                                           'name': 'HighRollerDiceRouletteCogs',
                                                           'animName': 'nothing',
                                                           'hp': 0,
                                                           'acc': 100,
                                                           'freq': 0,
                                                           'group': SuitBattleGlobals.ATK_TGT_SINGLE},
                                                          {'suitName': self.battle.activeSuits[i].dna.name,
                                                           'name': 'HighRollerDiceRouletteToons',
                                                           'animName': 'nothing',
                                                           'hp': 0,
                                                           'acc': 100,
                                                           'freq': 0,
                                                           'group': SuitBattleGlobals.ATK_TGT_GROUP},
                                                          {'suitName': self.battle.activeSuits[i].dna.name,
                                                           'name': 'HighRollerDiceRouletteNobody',
                                                           'animName': 'nothing',
                                                           'hp': 0,
                                                           'acc': 100,
                                                           'freq': 0,
                                                           'group': SuitBattleGlobals.ATK_TGT_SINGLE},
                                                          {'suitName': self.battle.activeSuits[i].dna.name,
                                                           'name': 'HighRollerRolled',
                                                           'animName': 'magic3',
                                                           'hp': 0,
                                                           'acc': 100,
                                                           'freq': 0,
                                                           'group': SuitBattleGlobals.ATK_TGT_GROUP}
                                                          ])  # Choice Conduction or Free Cruise or No Attack
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
            if self.battle.activeSuits[i].dna.name == 'hroller2':
                if self.battle.activeSuits[i].currHP <= 51851 and not self.suitHasCondition(suitId,
                                                                                            'aceInTheHole') and len(
                    self.battle.activeSuits) > 1:
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                                'name': 'HighRollerAceInTheHole',  # Ace In The Hole
                                                'animName': 'nothing',
                                                'hp': 0,
                                                'acc': 100,
                                                'freq': 0,
                                                'group': SuitBattleGlobals.ATK_TGT_GROUP}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
            if self.battle.activeSuits[i].dna.name == 'hroller2':
                if self.TurnsElapsed % 1 == 0 and self.suitHasCondition(suitId, 'phase3') and self.__suitCanAttack(
                        suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    if self.suitHasCondition(suitId, 'HRconduction'):
                        attack[SUIT_ATK_COL] = random.choice([
                                                          {'suitName': self.battle.activeSuits[i].dna.name,
                                                           'name': 'HighRollerFreeCruise',
                                                           'animName': 'song-and-dance',
                                                           'hp': 0,
                                                           'acc': 100,
                                                           'freq': 0,
                                                           'group': SuitBattleGlobals.ATK_TGT_GROUP},
                                                          {'suitName': self.battle.activeSuits[i].dna.name,
                                                           'name': 'HighRollerDiceRouletteCogs',
                                                           'animName': 'nothing',
                                                           'hp': 0,
                                                           'acc': 100,
                                                           'freq': 0,
                                                           'group': SuitBattleGlobals.ATK_TGT_SINGLE},
                                                          {'suitName': self.battle.activeSuits[i].dna.name,
                                                           'name': 'HighRollerDiceRouletteToons',
                                                           'animName': 'nothing',
                                                           'hp': 0,
                                                           'acc': 100,
                                                           'freq': 0,
                                                           'group': SuitBattleGlobals.ATK_TGT_GROUP},
                                                          {'suitName': self.battle.activeSuits[i].dna.name,
                                                           'name': 'HighRollerDiceRouletteNobody',
                                                           'animName': 'nothing',
                                                           'hp': 0,
                                                           'acc': 100,
                                                           'freq': 0,
                                                           'group': SuitBattleGlobals.ATK_TGT_SINGLE},
                                                          {'suitName': self.battle.activeSuits[i].dna.name,
                                                           'name': 'HighRollerRolled',
                                                           'animName': 'magic3',
                                                           'hp': 0,
                                                           'acc': 100,
                                                           'freq': 0,
                                                           'group': SuitBattleGlobals.ATK_TGT_GROUP}
                                                          ])  # Choice Conduction or Free Cruise or No Attack
                    elif self.suitHasCondition(suitId, 'HRfreecruise'):
                        attack[SUIT_ATK_COL] = random.choice([
                                                          {'suitName': self.battle.activeSuits[i].dna.name,
                                                           'name': 'HighRollerDiceRouletteCogs',
                                                           'animName': 'nothing',
                                                           'hp': 0,
                                                           'acc': 100,
                                                           'freq': 0,
                                                           'group': SuitBattleGlobals.ATK_TGT_SINGLE},
                                                          {'suitName': self.battle.activeSuits[i].dna.name,
                                                           'name': 'HighRollerDiceRouletteToons',
                                                           'animName': 'nothing',
                                                           'hp': 0,
                                                           'acc': 100,
                                                           'freq': 0,
                                                           'group': SuitBattleGlobals.ATK_TGT_GROUP},
                                                          {'suitName': self.battle.activeSuits[i].dna.name,
                                                           'name': 'HighRollerDiceRouletteNobody',
                                                           'animName': 'nothing',
                                                           'hp': 0,
                                                           'acc': 100,
                                                           'freq': 0,
                                                           'group': SuitBattleGlobals.ATK_TGT_SINGLE},
                            {'suitName': self.battle.activeSuits[i].dna.name,
                             'name': 'HighRollerConduction',
                             'animName': 'throw-object',
                             'hp': 0,
                             'acc': 100,
                             'freq': 0,
                             'group': SuitBattleGlobals.ATK_TGT_DOUBLE},
                                                          {'suitName': self.battle.activeSuits[i].dna.name,
                                                           'name': 'HighRollerRolled',
                                                           'animName': 'magic3',
                                                           'hp': 0,
                                                           'acc': 100,
                                                           'freq': 0,
                                                           'group': SuitBattleGlobals.ATK_TGT_GROUP}
                                                          ])  # Choice Conduction or Free Cruise or No Attack
                    elif self.suitHasCondition(suitId, 'HRdiceroulette'):
                        attack[SUIT_ATK_COL] = random.choice([
                            {'suitName': self.battle.activeSuits[i].dna.name,
                             'name': 'HighRollerConduction',
                             'animName': 'throw-object',
                             'hp': 0,
                             'acc': 100,
                             'freq': 0,
                             'group': SuitBattleGlobals.ATK_TGT_DOUBLE},
                            {'suitName': self.battle.activeSuits[i].dna.name,
                             'name': 'HighRollerFreeCruise',
                             'animName': 'song-and-dance',
                             'hp': 0,
                             'acc': 100,
                             'freq': 0,
                             'group': SuitBattleGlobals.ATK_TGT_GROUP},
                                                          {'suitName': self.battle.activeSuits[i].dna.name,
                                                           'name': 'HighRollerRolled',
                                                           'animName': 'magic3',
                                                           'hp': 0,
                                                           'acc': 100,
                                                           'freq': 0,
                                                           'group': SuitBattleGlobals.ATK_TGT_GROUP}
                                                          ])  # Choice Conduction or Free Cruise or No Attack
                    elif self.suitHasCondition(suitId, 'HRrolled'):
                        attack[SUIT_ATK_COL] = random.choice([
                            {'suitName': self.battle.activeSuits[i].dna.name,
                             'name': 'HighRollerDiceRouletteCogs',
                             'animName': 'nothing',
                             'hp': 0,
                             'acc': 100,
                             'freq': 0,
                             'group': SuitBattleGlobals.ATK_TGT_SINGLE},
                            {'suitName': self.battle.activeSuits[i].dna.name,
                             'name': 'HighRollerDiceRouletteToons',
                             'animName': 'nothing',
                             'hp': 0,
                             'acc': 100,
                             'freq': 0,
                             'group': SuitBattleGlobals.ATK_TGT_GROUP},
                            {'suitName': self.battle.activeSuits[i].dna.name,
                             'name': 'HighRollerDiceRouletteNobody',
                             'animName': 'nothing',
                             'hp': 0,
                             'acc': 100,
                             'freq': 0,
                             'group': SuitBattleGlobals.ATK_TGT_SINGLE},
                            {'suitName': self.battle.activeSuits[i].dna.name,
                             'name': 'HighRollerConduction',
                             'animName': 'throw-object',
                             'hp': 0,
                             'acc': 100,
                             'freq': 0,
                             'group': SuitBattleGlobals.ATK_TGT_DOUBLE},
                            {'suitName': self.battle.activeSuits[i].dna.name,
                             'name': 'HighRollerFreeCruise',
                             'animName': 'song-and-dance',
                             'hp': 0,
                             'acc': 100,
                             'freq': 0,
                             'group': SuitBattleGlobals.ATK_TGT_GROUP},
                        ])  # Choice Conduction or Free Cruise or No Attack
                    else:
                        attack[SUIT_ATK_COL] = random.choice([{'suitName': self.battle.activeSuits[i].dna.name,
                                                               'name': 'HighRollerConduction',
                                                               'animName': 'throw-object',
                                                               'hp': 0,
                                                               'acc': 100,
                                                               'freq': 0,
                                                               'group': SuitBattleGlobals.ATK_TGT_DOUBLE},
                                                              {'suitName': self.battle.activeSuits[i].dna.name,
                                                               'name': 'HighRollerFreeCruise',
                                                               'animName': 'song-and-dance',
                                                               'hp': 0,
                                                               'acc': 100,
                                                               'freq': 0,
                                                               'group': SuitBattleGlobals.ATK_TGT_GROUP},
                                                              {'suitName': self.battle.activeSuits[i].dna.name,
                                                               'name': 'HighRollerDiceRouletteCogs',
                                                               'animName': 'nothing',
                                                               'hp': 0,
                                                               'acc': 100,
                                                               'freq': 0,
                                                               'group': SuitBattleGlobals.ATK_TGT_SINGLE},
                                                              {'suitName': self.battle.activeSuits[i].dna.name,
                                                               'name': 'HighRollerDiceRouletteToons',
                                                               'animName': 'nothing',
                                                               'hp': 0,
                                                               'acc': 100,
                                                               'freq': 0,
                                                               'group': SuitBattleGlobals.ATK_TGT_GROUP},
                                                              {'suitName': self.battle.activeSuits[i].dna.name,
                                                               'name': 'HighRollerDiceRouletteNobody',
                                                               'animName': 'nothing',
                                                               'hp': 0,
                                                               'acc': 100,
                                                               'freq': 0,
                                                               'group': SuitBattleGlobals.ATK_TGT_SINGLE},
                                                              {'suitName': self.battle.activeSuits[i].dna.name,
                                                               'name': 'HighRollerRolled',
                                                               'animName': 'magic3',
                                                               'hp': 0,
                                                               'acc': 100,
                                                               'freq': 0,
                                                               'group': SuitBattleGlobals.ATK_TGT_GROUP}
                                                              ])  # Choice Conduction or Free Cruise or No Attack
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
            if self.battle.activeSuits[i].dna.name == 'hroller2':
                if self.suitHasCondition(suitId, 'vulnerable') and self.suitHasCondition(suitId,
                                                                                         'phase3') and self.__suitCanAttack(
                    suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'HighRollerTrickOfTheLight',  # Trick Of The Light
                                            'animName': 'nothing',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if len(self.battle.activeSuits) == 1 and self.suitHasCondition(suitId,
                                                                               'phase3') and not self.suitHasCondition(
                    suitId, 'trickofthelight') and not self.suitHasCondition(suitId,
                                                                             'vulnerable') and self.__suitCanAttack(
                    suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'HighRollerVulnerable',  # Vulnerability
                                            'animName': 'nothing',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if len(self.battle.activeSuits) > 1 and not self.suitHasCondition(suitId,
                                                                                  'phase3') and self.__suitCanAttack(
                    suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'HighRollerNoAttack',  # No Attack
                                            'animName': 'nothing',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 100,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if len(self.battle.activeSuits) == 1 and not self.suitHasCondition(suitId,
                                                                                   'phase3') and self.__suitCanAttack(
                    suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'HighRollerPhase3',  # Phase 3 Movie
                                            'animName': 'nothing',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_GROUP}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'HighRollerRaisingTheAnte',  # Raising The Ante
                                            'animName': 'magic3',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_GROUP}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'HighRollerTrickOfTheLight',  # Trick Of The Light
                                            'animName': 'nothing',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
            if self.battle.activeSuits[i].dna.name == 'hroller':
                if self.battle.activeSuits[i].currHP <= 0 and not self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'DeathCheck',  # Check for Death
                                            'animName': 'nothing',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
            if self.battle.activeSuits[i].dna.name == 'videog':
                if self.deadSuits == 1 and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'VideographerAttackRewind',  # Attack Rewind for Dead Suits
                                            'animName': 'snap',
                                            'hp': 25,
                                            'acc': 85,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.deadSuits == 2 and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'VideographerAttackRewind',  # Attack Rewind for Dead Suits
                                            'animName': 'snap',
                                            'hp': 25,
                                            'acc': 85,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_DOUBLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.deadSuits == 3 and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'VideographerAttackRewind',  # Attack Rewind for Dead Suits
                                            'animName': 'snap',
                                            'hp': 25,
                                            'acc': 85,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_TRIPLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.deadSuits > 3 and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'VideographerAttackRewind',  # Attack Rewind for Dead Suits
                                            'animName': 'snap',
                                            'hp': 25,
                                            'acc': 85,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_GROUP}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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

    def __calculateSuitAttacksWitnessStandIn(self):
        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId

            # Initial Cheats
            if self.battle.activeSuits[i].dna.name == 'redd': #redd heir wing
                if self.suitHasCondition(suitId, 'soaked') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'ReddLiquidationSale',
                     'animName': 'magic1',
                     'hp': 0,
                     'acc': 85,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_GROUP}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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

            # Primary Cheats
        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'wsi': #witness stand-in
                if self.suitHasCondition(suitId, 'soakedcalculator') or (x + 1) % 3 == 0 and len(self.battle.activeSuits) >= 6 and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'WSICeaseAndDesist', # Cease And Desist
                     'animName': 'cease',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_GROUP}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if x % 2 == 0 and len(self.battle.activeSuits) < 6 and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'WSIJuryNotice', # Jury Notice
                     'animName': 'summon',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
            if self.battle.activeSuits[i].dna.name == 'redd':  # redd heir wing
                if (x + 3) % 4 == 0 and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'ReddAutoRepair', # Auto Repair
                     'animName': 'effort',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if (x + 1) % 3 == 0 and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'ReddPeckingOrder', # Pecking Order
                     'animName': 'throw-object',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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

    def __calculateEndOfRoundAttacks(self):
        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.suitHasCondition(suitId, 'deathcheck') and not self.suitHasCondition(suitId, 'dead'):
                attack = getDefaultSuitAttack()
                attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                        'name': 'DeathCheck',  # Check for Death
                                        'animName': 'nothing',
                                        'hp': 0,
                                        'acc': 100,
                                        'freq': 0,
                                        'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                if attack[SUIT_TGT_COL] == []:
                    continue
                attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                self.__calcSuitAtkHpALT(attack)
                if attack[SUIT_ATK_COL]:
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
            if self.suitHasCondition(suitId, 'bellowattack') and self.suitHasCondition(suitId, 'lured') and self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                attack = self.__getLureRemoval(suitId)
                self.battle.suitAttacks.append(attack)
            if self.suitHasCondition(suitId, 'bellowattack') and self.battle.activeSuits[i].currHP > 0 and not self.battle.activeSuits[i].dna.name == 'ambass':
                attack = self.__getGenericSuitAttack(suitId) # Extra Attack for Lured Cogs affected by Bayou Bellow
                self.battle.suitAttacks.append(attack)
            if self.suitHasCondition(suitId, 'bellowattack') and self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0 and self.battle.activeSuits[i].dna.name == 'ambass':
                attack = getDefaultSuitAttack()
                attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                        'name': 'AmbassadorManagerialProtectionImmunity',  # Extra Attack for Head Roller
                                        'animName': 'golf-club-swing',
                                        'hp': 0,
                                        'acc': 100,
                                        'freq': 0,
                                        'group': SuitBattleGlobals.ATK_TGT_GROUP}
                attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                if attack[SUIT_TGT_COL] == []:
                    continue
                attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                self.__calcSuitAtkHpALT(attack)
                if attack[SUIT_ATK_COL]:
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
            if not self.suitHasCondition(suitId, 'zapped') and self.suitHasCondition(suitId, 'soaked') and self.getSuitConditionTurns(suitId, 'soaked') == 1 and self.battle.activeSuits[i].currHP > 0:
                attack = getDefaultSuitAttack()
                attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                 'name': 'SoakRemoval', # Soak Removal
                 'animName': 'nothing',
                 'hp': 0,
                 'acc': 100,
                 'freq': 0,
                 'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                if attack[SUIT_TGT_COL] == []:
                    continue
                attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                self.__calcSuitAtkHpALT(attack)
                if attack[SUIT_ATK_COL]:
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
            if self.suitHasCondition(suitId, 'marked') and not self.battle.activeSuits[i].dna.name == 'bcaster' and not self.battle.activeSuits[i].dna.name == 'hrollers' and self.battle.activeSuits[i].currHP > 0:
                attack = getDefaultSuitAttack()
                attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                 'name': 'MarkRemoval', # Mark Removal
                 'animName': 'nothing',
                 'hp': 0,
                 'acc': 100,
                 'freq': 0,
                 'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                if attack[SUIT_TGT_COL] == []:
                    continue
                attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                self.__calcSuitAtkHpALT(attack)
                if attack[SUIT_ATK_COL]:
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
            if self.suitHasCondition(suitId, 'sued') and self.getSuitConditionTurns(suitId, 'sued') == 1 and self.battle.activeSuits[i].currHP > 0:
                attack = getDefaultSuitAttack()
                attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                 'name': 'SueRemoval', # Sue Removal
                 'animName': 'nothing',
                 'hp': 0,
                 'acc': 100,
                 'freq': 0,
                 'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                if attack[SUIT_TGT_COL] == []:
                    continue
                attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                self.__calcSuitAtkHpALT(attack)
                if attack[SUIT_ATK_COL]:
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
            if self.suitHasCondition(suitId, 'sued') and not self.suitHasCondition(suitId, 'suemovie') and self.battle.activeSuits[i].currHP > 0:
                attack = getDefaultSuitAttack()
                attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                 'name': 'SueRemoval', # Sue Removal
                 'animName': 'nothing',
                 'hp': 0,
                 'acc': 100,
                 'freq': 0,
                 'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                if attack[SUIT_TGT_COL] == []:
                    continue
                attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                self.__calcSuitAtkHpALT(attack)
                if attack[SUIT_ATK_COL]:
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

    def __calculateSuitAttacks(self):
        for i in xrange(len(self.battle.activeSuits)): # Cheats before Cog Attacks
            suitId = self.battle.activeSuits[i].doId
            x = self.TurnsElapsed
            attack = self.__getGenericSuitAttack(suitId)
            if self.suitHasCondition(suitId, 'sued') and self.suitHasCondition(suitId, 'suemovie'):
                attack = getDefaultSuitAttack()
                attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                 'name': 'SueDamage', # Sue Damage
                 'animName': 'nothing',
                 'hp': 0,
                 'acc': 100,
                 'freq': 0,
                 'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                if attack[SUIT_TGT_COL] == []:
                    continue
                attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                self.__calcSuitAtkHpALT(attack)
                if attack[SUIT_ATK_COL]:
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
            if not self.suitHasCondition(suitId, 'suemovie') and self.suitHasCondition(suitId,
                                                                                       'sued') and self.battle.activeSuits[i].currHP > 0:
                attack = getDefaultSuitAttack()
                attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                attack[SUIT_ATK_COL] = {'suitName': '',
                                        'name': 'SueApplication',
                                        # Sue Application movie since the actual movie doesnt exist
                                        'animName': 'nothing',
                                        'hp': 0,
                                        'acc': 100,
                                        'freq': 0,
                                        'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                if attack[SUIT_TGT_COL] == []:
                    continue
                attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                self.__calcSuitAtkHpALT(attack)
                if attack[SUIT_ATK_COL]:
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
            if self.suitHasCondition(suitId, 'shielding') and self.absorbDamage > 0 and self.battle.activeSuits[i].currHP > 0:
                attack = getDefaultSuitAttack()
                attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                        'name': 'AbsorbMovie',  # Absorb Damage Movie
                                        'animName': 'nothing',
                                        'hp': 0,
                                        'acc': 100,
                                        'freq': 0,
                                        'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                if attack[SUIT_TGT_COL] == []:
                    continue
                attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                self.__calcSuitAtkHpALT(attack)
                if attack[SUIT_ATK_COL]:
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
            if self.suitHasCondition(suitId, 'deathcheck') and not self.suitHasCondition(suitId, 'dead'):
                attack = getDefaultSuitAttack()
                attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                        'name': 'DeathCheck',  # Check for Death
                                        'animName': 'nothing',
                                        'hp': 0,
                                        'acc': 100,
                                        'freq': 0,
                                        'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                if attack[SUIT_TGT_COL] == []:
                    continue
                attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                self.__calcSuitAtkHpALT(attack)
                if attack[SUIT_ATK_COL]:
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
            if self.battle.activeSuits[i].dna.name == 'phouse': #powerhouse
                if self.suitHasCondition(suitId, 'soakedcalculator') and self.suitHasCondition(suitId, 'lured') and self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getLureRemoval(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'soakedcalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'soakedcalculator') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'PowerhouseSnipeSoaked', # Soak Retaliation Snipe
                     'animName': 'magic3-alt',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_GROUP}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
            if self.battle.activeSuits[i].dna.name == 'radiog': # radiographer
                if self.suitHasCondition(suitId, 'soakedcalculator') and self.suitHasCondition(suitId, 'lured') and self.__suitCanAttack(suitId) and  self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getLureRemoval(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'soakedcalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'soakedcalculator') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'RadiographerHotTakeRetaliation',  # Hot Take Soak Retaliation
                                            'animName': 'throw-object',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
            if self.battle.activeSuits[i].dna.name == 'caseman':  # case manager
                if self.TurnsElapsed % 1 == 0:
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'CaseManagerCourtRecordBan', # Court Record Ban Retaliation
                     'animName': 'nothing',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_GROUP}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
            if self.battle.activeSuits[i].dna.name == 'stenog':
                if self.TurnsElapsed % 1 == 0:
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'StenographerCourtRecordBan', # Court Record Retaliation
                     'animName': 'nothing',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_GROUP}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
            if self.battle.activeSuits[i].dna.name == 'lgator': # litigator
                if self.suitHasCondition(suitId, 'soakedcalculator') and self.suitHasCondition(suitId, 'lured') and self.__suitCanAttack(suitId) and  self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getLureRemoval(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'soakedcalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'soakedcalculator') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'LitigatorSnapSoak', # Snap Soaked
                     'animName': 'throw-object',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_GROUP}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
            if self.battle.activeSuits[i].dna.name == 'safesupervis':
                if self.__suitCanAttack(suitId) and self.suitHasCondition(suitId, 'lured') and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getLureRemoval(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.TurnsElapsed % 1 == 0 and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'SafetyViolation',
                     'animName': 'snap',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_GROUP}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
            if self.battle.activeSuits[i].dna.name == 'wtapper':
                if self.TurnsElapsed % 1 == 0:
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'WiretapperGagBan', # Budget Cuts Gag Ban Retaliation
                     'animName': 'nothing',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_GROUP}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
            if self.battle.activeSuits[i].dna.name == 'bkeeper':  # bookkeeper
                if self.TurnsElapsed % 1 == 0 and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'BookkeeperBookkeepingRetaliation', # Bookkeeping Retaliation
                     'animName': 'nothing',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_GROUP}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                if self.suitHasCondition(suitId, 'soakedcalculator') and self.suitHasCondition(suitId, 'lured') and self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getLureRemoval(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'soakedcalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'soakedcalculator') and self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'BookkeeperPaperCutSoaked',  # Soaked Paper Cut Retaliation
                                            'animName': 'throw-paper',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
                    attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'BookkeeperPaperCutMarked',  # Marked Paper Cut Retaliation
                                            'animName': 'throw-paper',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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

        for i in xrange(len(self.battle.activeSuits)): # Regular Manager Attacks
            suitId = self.battle.activeSuits[i].doId
            x = self.TurnsElapsed
            #attack = self.__getGenericSuitAttack(suitId)
            # Managers Attack Before Cogs
            if self.battle.activeSuits[i].dna.name in SuitBattleGlobals.SpecialCogDict and self.suitHasCondition(suitId, 'lured') and self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                attack = self.__getLureRemoval(suitId)
                self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name in SuitBattleGlobals.SpecialCogDict and self.__suitCanAttack(suitId) and not self.battle.activeSuits[i].dna.name == 'hrollers':
                attack = self.__getGenericSuitAttack(suitId)
                self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'hrollers':
                if self.__suitCanAttack(suitId):
                    attack = getDefaultSuitAttack()
                    attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                    if self.suitHasCondition(suitId, 'HRpowertrip'):
                        attack[SUIT_ATK_COL] = {'suitName': 'hrollers',
                         'name': 'HighRollerNoAttack',
                         'animName': 'nothing',
                         'hp': 0,
                         'acc': 100,
                         'freq': 0,
                         'group': SuitBattleGlobals.ATK_TGT_SINGLE}
                    else:
                        attack[SUIT_ATK_COL] = {'suitName': 'hrollers',
                         'name': 'PowerTrip',
                         'animName': 'magic1',
                         'hp': 25,
                         'acc': 75,
                         'freq': 0,
                         'group': SuitBattleGlobals.ATK_TGT_GROUP}
                    attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                    if attack[SUIT_TGT_COL] == []:
                        continue
                    attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                    self.__calcSuitAtkHpALT(attack)
                    if attack[SUIT_ATK_COL]:
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
            #if i < len(self.battle.activeSuits):
                suitId = self.battle.activeSuits[i].doId

                if not self.__suitCanAttack(suitId):
                    if self.notify.getDebug():
                        self.notify.debug("Suit %d can't attack" % suitId)
                    continue
                if self.battle.pendingSuits.count(self.battle.activeSuits[i]) > 0 or self.battle.joiningSuits.count(self.battle.activeSuits[i]) > 0:
                    continue
               # attack = self.__getGenericSuitAttack(suitId)
                # Grunt Cog Attacks
                if not self.battle.activeSuits[i].dna.name in SuitBattleGlobals.SpecialCogDict and self.suitHasCondition(suitId, 'lured') and self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getLureRemoval(suitId)
                    self.battle.suitAttacks.append(attack)
                if not self.battle.activeSuits[i].dna.name in SuitBattleGlobals.SpecialCogDict:
                    attack = self.__getGenericSuitAttack(suitId)
                    self.battle.suitAttacks.append(attack)

                if self.battle.findSuit(suitId).dna.name == 'erclaim': # Check if the Cog that just attacked is capable of cheating (e.g. if self.battle.findSuit(suitId).dna.name == 'erclaim').
                    pass # Professor Control: I don't believe there's a Laff Steal cheat, and if there is, I do not know how I would get it to function correctly.  I already have issues trying to get a cheat in my source to work when the Cog misses an attack.
                elif False: # Keep checking for other corresponding Cog names; False is a placeholder.
                    pass

                for i in xrange(len(self.battle.activeSuits)): # Now, how about the other Cogs, including the one that just attacked?
                    suitId = self.battle.activeSuits[i].doId
                    if self.battle.activeSuits[i].dna.name == 'foreman' and self.getActualLevel() == 25 and self.__suitCanAttack(suitId): # Sniper Factory Foreman
                        snipeAttack = getDefaultSuitAttack()
                        snipeAttack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                        snipeAttack[SUIT_ATK_COL] = {'suitName': 'foreman',
                         'name': 'PowerhouseSnipeBookkept',
                         'animName': 'glower',
                         'hp': 0,
                         'acc': 100,
                         'freq': 0,
                         'group': SuitBattleGlobals.ATK_TGT_GROUP}
                        snipeAttack[SUIT_TGT_COL] = attack[SUIT_TGT_COL] # All the same targets as the previous attack.  NOTE: This assumes attack was not used for any cheats between the attack and now, so DO NOT make a cheat list with the variable name attack.
                        snipeAttack[SUIT_HP_COL] = [(hp * 0.75) for hp in attack[SUIT_HP_COL]] # Same HP values, but at 0.75x effectiveness.  May or may not need to be cast to ints.
                        self.__calcSuitAtkHpALT(attack) # Professor Control: Due to sharing the Powerhouse's Bookkept Snipe, this will ruin the calculations and cause all Toons to take 0 damage because no Toon is bookkept, but I want to get this update out, along with other unforeseen consequences I overlooked due to my hastiness.
                        for currTgt in snipeAttack[SUIT_TGT_COL]:
                            self.__updateSuitAtkStat(self.battle.activeToons[currTgt])

                        targets = self.__CreateSuitTargetList(attack)
                        allTargetsDead = True
                        for currTgt in targets:
                            if self.__getToonHp(currTgt) > 0:
                                allTargetsDead = False
                                break

                        if allTargetsDead:
                            snipeAttack = getDefaultSuitAttack()
                        if self.__attackHasHit(snipeAttack, suit=1):
                            self.__applySuitAttackDamages(snipeAttack, self.battle.findSuit(snipeAttack[SUIT_ID_COL]))
                        snipeAttack[SUIT_BEFORE_TOONS_COL] = 0
                        self.battle.suitAttacks.append(snipeAttack)

        for i in xrange(len(self.battle.activeSuits)): # Desperation for Litigation Managers
            suitId = self.battle.activeSuits[i].doId
            x = self.TurnsElapsed
            if self.battle.activeSuits[i].currHP <= 0 and self.battle.activeSuits[i].dna.name in SuitBattleGlobals.LitigationManagers:
                attack = getDefaultSuitAttack()
                attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                 'name': 'Desperation', # Desperation Activation
                 'animName': 'nothing',
                 'hp': 0,
                 'acc': 100,
                 'freq': 0, # Professor Control: I do not know how relevant attack frequency is, but keep it anyway.
                 'group': SuitBattleGlobals.ATK_TGT_SINGLE} # Why is Desperation single-target?
                attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                if attack[SUIT_TGT_COL] == []:
                    continue
                attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                self.__calcSuitAtkHpALT(attack)
                if attack[SUIT_ATK_COL]:
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
            if self.suitHasCondition(suitId, 'desperationcalculator'):
                attack = getDefaultSuitAttack()
                attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                attack[SUIT_ATK_COL] = {'suitName': self.battle.activeSuits[i].dna.name,
                 'name': 'Desperation2', # Desperation Activation when Litigation managers start battles alone
                 'animName': 'nothing',
                 'hp': 0,
                 'acc': 100,
                 'freq': 0, # Professor Control: I do not know how relevant attack frequency is, but keep it anyway.
                 'group': SuitBattleGlobals.ATK_TGT_SINGLE} # Why is Desperation single-target?
                attack[SUIT_TGT_COL] = self.__calcSuitTarget(attack)
                if attack[SUIT_TGT_COL] == []:
                    continue
                attack[SUIT_HP_COL] = [-1 for j in xrange(len(self.battle.activeToons))]
                self.__calcSuitAtkHpALT(attack)
                if attack[SUIT_ATK_COL]:
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

        # Extra Attacks
        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            x = self.TurnsElapsed
            if self.battle.activeSuits[i].dna.name == 'wsi': #witness stand-in
                if self.battle.activeSuits[i].getSkeleRevives() == 0 and self.__suitCanAttack(suitId):
                    attack = self.__getGenericSuitAttack(suitId)
                    self.battle.suitAttacks.append(attack)
            if self.suitHasCondition(suitId, 'extraAttack') and self.battle.activeSuits[i].currHP > 0:
                attack = self.__getGenericSuitAttack(suitId)
                self.battle.suitAttacks.append(attack)
            if self.suitHasCondition(suitId, 'extraAttack2') and self.battle.activeSuits[i].currHP > 0:
                attack = self.__getGenericSuitAttack(suitId)
                self.battle.suitAttacks.append(attack)
            if self.suitHasCondition(suitId, 'extraAttack3') and self.battle.activeSuits[i].currHP > 0:
                attack = self.__getGenericSuitAttack(suitId)
                self.battle.suitAttacks.append(attack)
            if self.suitHasCondition(suitId, 'extraAttack4') and self.battle.activeSuits[i].currHP > 0:
                attack = self.__getGenericSuitAttack(suitId)
                self.battle.suitAttacks.append(attack)
            if self.suitHasCondition(suitId, 'extraAttack5') and self.battle.activeSuits[i].currHP > 0:
                attack = self.__getGenericSuitAttack(suitId)
                self.battle.suitAttacks.append(attack)
            if self.suitHasCondition(suitId, 'extraAttack6') and self.battle.activeSuits[i].currHP > 0:
                attack = self.__getGenericSuitAttack(suitId)
                self.battle.suitAttacks.append(attack)
            if self.suitHasCondition(suitId, 'extraAttack7') and self.battle.activeSuits[i].currHP > 0:
                attack = self.__getGenericSuitAttack(suitId)
                self.battle.suitAttacks.append(attack)
            if self.suitHasCondition(suitId, 'extraAttack8') and self.battle.activeSuits[i].currHP > 0:
                attack = self.__getGenericSuitAttack(suitId)
                self.battle.suitAttacks.append(attack)
            if self.suitHasCondition(suitId, 'extraAttack9') and self.battle.activeSuits[i].currHP > 0:
                attack = self.__getGenericSuitAttack(suitId)
                self.battle.suitAttacks.append(attack)
            if self.suitHasCondition(suitId, 'extraAttack10') and self.battle.activeSuits[i].currHP > 0:
                attack = self.__getGenericSuitAttack(suitId)
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
        
        attacks = findToonAttack(self.battle.activeToons, self.battle.toonAttacks, SUE)
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
                      ##  self.setToonCondition(toon.doId, 'noUnites', 1, 2, 'setBoth')
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

        #for i in xrange(6):
           # for j in xrange(len(self.battle.activeToons)):
             #   self.battle.suitAttacks[i][SUIT_HP_COL].append(-1)

        toonsHit, cogsMiss = self.__initRound()
        for suit in self.battle.activeSuits:
            if suit.isGenerated():
                if self.suitHasCondition(suit.doId, 'deadcase'):
                    for s in self.battle.activeSuits:
                        self.setSuitCondition(s.doId, 'deadcase', 1, 100, 'setBoth')
                if self.suitHasCondition(suit.doId, 'deadsteno'):
                    for s in self.battle.activeSuits:
                        self.setSuitCondition(s.doId, 'deadsteno', 1, 100, 'setBoth')
                if self.suitHasCondition(suit.doId, 'deadgoat'):
                    for s in self.battle.activeSuits:
                        self.setSuitCondition(s.doId, 'deadgoat', 1, 100, 'setBoth')
                if self.suitHasCondition(suit.doId, 'deadgator'):
                    for s in self.battle.activeSuits:
                        self.setSuitCondition(s.doId, 'deadgator', 1, 100, 'setBoth')
                if suit.dna.name == 'bcaster':
                    self.setSuitCondition(suit.doId, 'vulnerablebroadcaster', 1, 99, 'setBoth')
                if suit.dna.name == 'hrollers' and suit.getActualLevel() == 30:
                    for s in self.battle.activeSuits:
                        self.setSuitCondition(s.doId, 'soakImmune', 1, 2, 'setBoth')
                if suit.dna.name == 'hrollers' and suit.getActualLevel() == 27:
                    for s in self.battle.activeSuits:
                        self.setSuitCondition(s.doId, 'zapImmune', 1, 2, 'setBoth')
                if suit.dna.name == 'hrollers' and suit.getActualLevel() == 26:
                    for s in self.battle.activeSuits:
                        self.setSuitCondition(s.doId, 'kbImmune', 1, 2, 'setBoth')
                if suit.dna.name == 'hrollers' and suit.getActualLevel() == 25:
                    self.setSuitCondition(suit.doId, 'lureImmune', 1, 99, 'setBoth')
                    for s in self.battle.activeSuits:
                        self.setSuitCondition(s.doId, 'noKB', 1, 2, 'setBoth')
                if suit.dna.name == 'hroller':
                    self.setSuitCondition(suit.doId, 'immune', 1, 99, 'setBoth')
                    self.setSuitCondition(suit.doId, 'absorbingHR', 1, 99, 'setBoth')
                if suit.dna.name == 'hroller2' and not self.suitHasCondition(suit.doId, 'phase3'):
                    self.setSuitCondition(suit.doId, 'immune', 1, 99, 'setBoth')
                if suit.dna.name == 'hroller2' and len(self.battle.activeSuits) == 1:
                    self.setSuitCondition(suit.doId, 'HRdamagereduction', 0, 0, 'setBoth')
                if suit.dna.name == 'videog' and len(self.battle.activeSuits) == 2:
                    self.setSuitCondition(suit.doId, 'immune', 0, 0, 'setBoth')
                    self.setSuitCondition(suit.doId, 'spawncalculator', 1, 2, 'setBoth')
                    currentBossHealth = -1
                    currentBossHealth2 = -1
                    currentBossHealth3 = -1
                    currentBossHealth4 = -1
                    for s in self.battle.suits:
                        if s.dna.name == 'director':
                            currentBossHealth = s.currHP
                        if s.dna.name == 'fmaker':
                            currentBossHealth2 = s.currHP
                        if s.dna.name == 'choreo':
                            currentBossHealth3 = s.currHP
                        if s.dna.name == 'cinema':
                            currentBossHealth4 = s.currHP
                    if currentBossHealth <= 0 and currentBossHealth2 <= 0 and currentBossHealth3 <= 0 and currentBossHealth4 <= 0:
                        self.setSuitCondition(suit.doId, 'immune', 0, 0, 'setBoth')
                if suit.dna.name == 'sgoat' and self.TurnsElapsed == 0:
                    self.setSuitCondition(suit.doId, 'shielding', 1, 99, 'setBoth')
                if suit.dna.name == 'sgoat':
                    for s in self.battle.activeSuits:
                        self.setSuitCondition(s.doId, 'activegoat', 1, 99, 'setBoth')
                if suit.dna.name == 'caseman':
                    for s in self.battle.activeSuits:
                        self.setSuitCondition(s.doId, 'activecase', 1, 99, 'setBoth')
                if suit.dna.name == 'stenog':
                    for s in self.battle.activeSuits:
                        self.setSuitCondition(s.doId, 'activesteno', 1, 99, 'setBoth')
                if suit.dna.name == 'lgator':
                    for s in self.battle.activeSuits:
                        self.setSuitCondition(s.doId, 'activegator', 1, 99, 'setBoth')
                if suit.dna.name == 'director':
                    self.setSuitCondition(suit.doId, 'shielding', 1, 99, 'setBoth')
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
        self.__calculateSuitConditions()
        self.__calculateSuitAttacks()
        self.__calculateSuitAttacksBossbotLitigation()
        self.__calculateSuitAttacksHighRoller()
        self.__calculateSuitAttacksSellbotLitigation()
        self.__calculateSuitAttacksWitnessStandIn()
        self.__calculateSuitAttacksLawbotLitigation()
        self.__calculateEndOfRoundAttacks()
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
        self.deadSuits -= self.deadSuits
        self.absorbDamage -= self.absorbDamage
        self.levelDamage -= self.levelDamage
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
       # if x % 99 == 0 and theSuit.dna.name == 'sgoat':
           # self.currentlyLuredSuits[suitId][0] = self.currentlyLuredSuits[suitId][1] - 1
        if theSuit.dna.name == 'hroller':
            self.currentlyLuredSuits[suitId][0] = self.currentlyLuredSuits[suitId][1] - 1
        if theSuit.dna.name == 'hroller2':
            self.currentlyLuredSuits[suitId][0] = self.currentlyLuredSuits[suitId][1] - 1
        if theSuit.dna.name == 'videog':
            self.currentlyLuredSuits[suitId][0] = self.currentlyLuredSuits[suitId][1] - 1
        if theSuit.dna.name == 'bcaster':
            self.currentlyLuredSuits[suitId][0] = self.currentlyLuredSuits[suitId][1] - 1
        if theSuit.dna.name == 'fires':
            self.currentlyLuredSuits[suitId][0] = self.currentlyLuredSuits[suitId][1] - 1
        if theSuit.dna.name == 'dopr':
            self.currentlyLuredSuits[suitId][0] = self.currentlyLuredSuits[suitId][1] - 1
        if theSuit.dna.name == 'dopa':
            self.currentlyLuredSuits[suitId][0] = self.currentlyLuredSuits[suitId][1] - 1
        if theSuit.dna.name == 'fbed':
            self.currentlyLuredSuits[suitId][0] = self.currentlyLuredSuits[suitId][1] - 1
        if theSuit.dna.name == 'mouthp':
            self.currentlyLuredSuits[suitId][0] = self.currentlyLuredSuits[suitId][1] - 1
        if theSuit.dna.name == 'rainmake':
            self.currentlyLuredSuits[suitId][0] = self.currentlyLuredSuits[suitId][1] - 1
        if theSuit.dna.name == 'bellring':
            self.currentlyLuredSuits[suitId][0] = self.currentlyLuredSuits[suitId][1] - 1
        if theSuit.dna.name == 'treek':
            self.currentlyLuredSuits[suitId][0] = self.currentlyLuredSuits[suitId][1] - 1
        if theSuit.dna.name == 'whunter':
            self.currentlyLuredSuits[suitId][0] = self.currentlyLuredSuits[suitId][1] - 1
        if theSuit.dna.name == 'wsi':
            self.currentlyLuredSuits[suitId][0] = self.currentlyLuredSuits[suitId][1] - 1
        if theSuit.dna.name == 'redd':
            self.currentlyLuredSuits[suitId][0] = self.currentlyLuredSuits[suitId][1] - 1
        if theSuit.dna.name == 'ddiver':
            self.currentlyLuredSuits[suitId][0] = self.currentlyLuredSuits[suitId][1] - 1
        if theSuit.dna.name == 'duckshfl':
            self.currentlyLuredSuits[suitId][0] = self.currentlyLuredSuits[suitId][1] - 1
        if theSuit.dna.name == 'gatekeep':
            self.currentlyLuredSuits[suitId][0] = self.currentlyLuredSuits[suitId][1] - 1
        if theSuit.isSkeleton and self.battle.findSuit(suitId).getManager() and self.currentlyLuredSuits[suitId][0] < 1:
            self.currentlyLuredSuits[suitId][0] = self.currentlyLuredSuits[suitId][1] - 1
        if self.suitHasCondition(suitId, 'enraged') and self.currentlyLuredSuits[suitId][0] < 1:
            self.currentlyLuredSuits[suitId][0] = self.currentlyLuredSuits[suitId][1] - 1
        if self.suitHasCondition(suitId, 'brokenconnection') and self.currentlyLuredSuits[suitId][0] < 1:
            self.currentlyLuredSuits[suitId][0] = self.currentlyLuredSuits[suitId][1] - 1
        if self.suitHasCondition(suitId, 'desperation') and self.currentlyLuredSuits[suitId][0] < 1:
            self.currentlyLuredSuits[suitId][0] = self.currentlyLuredSuits[suitId][1] - 1
        if self.suitHasCondition(suitId, 'bookkeeping') and self.currentlyLuredSuits[suitId][0] < 1:
            self.currentlyLuredSuits[suitId][0] = self.currentlyLuredSuits[suitId][1] - 1
        if self.suitHasCondition(suitId, 'extraAttack') and self.currentlyLuredSuits[suitId][0] < 1:
            self.currentlyLuredSuits[suitId][0] = self.currentlyLuredSuits[suitId][1] - 1
        if self.battle.findSuit(suitId).getManager() and self.currentlyLuredSuits[suitId][0] < 1:
            self.currentlyLuredSuits[suitId][0] = self.currentlyLuredSuits[suitId][1] - 2
        if self.suitHasCondition(suitId, 'immune'):
            self.currentlyLuredSuits[suitId][0] = self.currentlyLuredSuits[suitId][1] - 1
        if self.suitHasCondition(suitId, 'lureImmune'):
            self.currentlyLuredSuits[suitId][0] = self.currentlyLuredSuits[suitId][1] - 1
        if self.suitHasCondition(suitId, 'insured') and not self.suitHasCondition(suitId, 'desperation') and self.currentlyLuredSuits[suitId][0] < 1:
            self.currentlyLuredSuits[suitId][0] = self.currentlyLuredSuits[suitId][1] - 2
        if self.suitHasCondition(suitId, 'lureResist') and self.currentlyLuredSuits[suitId][0] < 1:
            self.currentlyLuredSuits[suitId][0] = self.currentlyLuredSuits[suitId][1] - 2
        if self.suitHasCondition(suitId, 'contracted') and not self.suitHasCondition(suitId, 'desperation') and self.currentlyLuredSuits[suitId][0] < 1:
            self.currentlyLuredSuits[suitId][0] = self.currentlyLuredSuits[suitId][1] - 2
        if theSuit.isSkeleton and self.battle.findSuit(suitId).getManager() and self.currentlyLuredSuits[suitId][0] < 1:
            self.currentlyLuredSuits[suitId][0] = self.currentlyLuredSuits[suitId][1] - 1
        if theSuit.isSkeleton and theSuit.getHP() > (theSuit.getMaxHP() * 1.5) and self.currentlyLuredSuits[suitId][0] < 1:
            self.currentlyLuredSuits[suitId][0] = self.currentlyLuredSuits[suitId][1] - 1
        if theSuit.isVirtual and theSuit.getHP() > (theSuit.getMaxHP() * 1.5) and self.currentlyLuredSuits[suitId][0] < 1:
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
                    hp = math.ceil(lerp(healRange[0], healRange[1], aptitude))
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
