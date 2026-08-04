from toontown.battle.BattleBase import *
from toontown.battle.BattleGlobals import *
from toontown.battle import SuitBattleGlobals
from toontown.toonbase import ToontownBattleGlobals
from toontown.battle import StatusEffects
import random
import math

class AttackHPCalculatorAI(object):

    def __init__(self, calculator):
        object.__setattr__(self, 'calculator', calculator)

    @property
    def battle(self):
        return self.calculator.battle

    def __getattr__(self, name):
        return getattr(self.calculator, name)

    def __setattr__(self, name, value):
        if name == 'calculator' or name.startswith(
                '_SuitAttackHpCalculatorAI__'):
            object.__setattr__(self, name, value)
        else:
            setattr(self.calculator, name, value)

    def __suitCanAttack(self, suitId):
        return self.calculator.suitCanAttack(suitId)

    def __getCheatAttack(self, suitId, attackInfo):
        return self.calculator.getCheatAttack(
            suitId,
            attackInfo
        )

    def __getAbilityQueued(self, suitId):
        return self.calculator.getAbilityQueued(suitId)

    def __appendToonConditionDamageAndRetaliation(
            self,
            *args,
            **kwargs):

        return self.calculator.appendToonConditionDamageAndRetaliation(
            *args,
            **kwargs
        )

    def __suitAtkHit(self, suitId, atkType):
        return self.calculator.suitAtkHit(suitId, atkType)
    
    def __getLureRemoval(self, suitId):
        return self.calculator.getLureRemoval(suitId)
    
    def __getLureRemovalPreToon(self, suitId):
        return self.calculator.getLureRemovalPreToon(suitId)

    def __getLureRemovalHeal(self, suitId):
        return self.calculator.getLureRemovalHeal(suitId)

    def __getLureRemovalTrap(self, suitId):
        return self.calculator.getLureRemovalTrap(suitId)

    def __getLureRemovalLure(self, suitId):
        return self.calculator.getLureRemovalLure(suitId)

    def __getLureRemovalSound(self, suitId):
        return self.calculator.getLureRemovalSound(suitId)

    def __getLureRemovalThrow(self, suitId):
        return self.calculator.getLureRemovalThrow(suitId)

    def __getLureRemovalSquirt(self, suitId):
        return self.calculator.getLureRemovalSquirt(suitId)

    def __getLureRemovalZap(self, suitId):
        return self.calculator.getLureRemovalZap(suitId)

    def __getLureRemovalDrop(self, suitId):
        return self.calculator.getLureRemovalDrop(suitId)

    def __addsyphonHP(self, suitId, amount):
        return self.calculator.addSyphonHP(suitId, amount)

    def __createSuitTargetList(self, attack):
        return self.calculator.createSuitTargetList(attack)

    def __getRandomValidTargetSuitDigitRadiographer(
            self,
            excludeSuitId=None):

        return self.calculator.getRandomValidTargetSuitDigitRadiographer(
            excludeSuitId=excludeSuitId
        )

    def __getRandomValidTargetSuitDigitAttorney(
            self,
            excludeSuitId=None):

        return self.calculator.getRandomValidTargetSuitDigitAttorney(
            excludeSuitId=excludeSuitId
        )


    def __getRandomValidTargetSuitDigitErclaim(
            self,
            excludeSuitId=None):

        return self.calculator.getRandomValidTargetSuitDigitErclaim(
            excludeSuitId=excludeSuitId
        )


    def __getErfitTargetByHPPercentSacrifice(
            self,
            excludeSuitId=None,
            mode='lowest'):

        return self.calculator.getErfitTargetByHPPercentSacrifice(
            excludeSuitId=excludeSuitId,
            mode=mode
        )

    def __getRandomValidTargetSuitDigitRushJob(self):
        return self.calculator.getRandomValidTargetSuitDigitRushJob()


    def __getRandomValidTargetSuitDigitAttorney(
            self,
            excludeSuitId=None):

        return self.calculator.getRandomValidTargetSuitDigitAttorney(
            excludeSuitId=excludeSuitId
        )


    def __getRandomValidTargetSuitDigitPresident(
            self,
            excludeSuitId=None):

        return self.calculator.getRandomValidTargetSuitDigitPresident(
            excludeSuitId=excludeSuitId
        )


    def __getRandomValidTargetSuitDigitVideographer(
            self,
            excludeSuitId=None):

        return self.calculator.getRandomValidTargetSuitDigitVideographer(
            excludeSuitId=excludeSuitId
        )


    def __getRandomValidTargetSuitDigit(
            self,
            excludeSuitId=None):

        return self.calculator.getRandomValidTargetSuitDigit(
            excludeSuitId=excludeSuitId
        )

    def __suitAtkHit(self, suitId, attack):
        return self.calculator.suitAtkHit(suitId, attack)


    def __removeLured(self, suitId):
        return self.calculator.removeLured(suitId)


    def __addsyphonHP(self, suitId, amount):
        return self.calculator.addSyphonHP(suitId, amount)

    def calcSuitAtkHpALT(self, attack):
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
                result = self.calculator.costsMultiplier
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'costscalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'CalculatingFees':
                self.setSuitCondition(theSuit.doId, 'calculatingcalculator', 1, 1, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'costscalculator', 1, 10, 'setBoth')
                self.calculator.costsMultiplier += 4
                self.calculator.costsCalculatorMultiplier += 4
                result = self.calculator.costsCalculatorMultiplier
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'StenographerSanction':
                result = 25
                attack[SUIT_HP_COL][targetIndex] = result
                if self.getToonConditionModifier(toonId, 'allGagBoost') < -50:
                    self.setToonCondition(toon.doId, 'allGagBoost',
                                            self.getToonConditionModifier(toonId, 'allGagBoost'), 3, 'setBoth')
                    self.setToonCondition(toon.doId, 'lureBoost',
                                            self.getToonConditionModifier(toonId, 'lureBoost'), 3, 'setBoth')
                else:
                    self.setToonCondition(toon.doId, 'allGagBoost', -50, 3, 'setBoth')
                    self.setToonCondition(toon.doId, 'lureBoost', -50, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'sanctioncalculator', 0, 0, 'setBoth')
                for s in self.battle.suits:
                    if s.dna.name == 'caseman':
                        suit = s
                        currentBossHealth = s.currHP
                        if currentBossHealth >= 1:
                            self.setSuitCondition(suit.doId, 'bindingscalculator2', 1, 10, 'setBoth')
            elif atkType['name'] == 'StenographerSanctionLitigator':
                result = 25
                attack[SUIT_HP_COL][targetIndex] = result
                if self.getToonConditionModifier(toonId, 'allGagBoost') < -75:
                    self.setToonCondition(toon.doId, 'allGagBoost',
                                            self.getToonConditionModifier(toonId, 'allGagBoost'), 3, 'setBoth')
                    self.setToonCondition(toon.doId, 'lureBoost',
                                            self.getToonConditionModifier(toonId, 'lureBoost'), 3, 'setBoth')
                else:
                    self.setToonCondition(toon.doId, 'allGagBoost', -75, 3, 'setBoth')
                    self.setToonCondition(toon.doId, 'lureBoost', -75, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'sanctioncalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'StenographerSanctionBindings':
                self.setSuitCondition(theSuit.doId, 'sanctioncalculator2', 0, 0, 'setBoth')
                if self.getToonConditionModifier(toonId, 'allGagBoost') < -25:
                    self.setToonCondition(toon.doId, 'allGagBoost', self.getToonConditionModifier(toonId, 'allGagBoost'), 3, 'setBoth')
                    self.setToonCondition(toon.doId, 'lureBoost', self.getToonConditionModifier(toonId, 'lureBoost'), 3, 'setBoth')
                else:
                    self.setToonCondition(toon.doId, 'allGagBoost', -25, 3, 'setBoth')
                    self.setToonCondition(toon.doId, 'lureBoost', -25, 3, 'setBoth')
                result = 25
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'StenographerSanctionSuppression':
                result = 25
                self.setSuitCondition(theSuit.doId, 'sanctioncalculator3', 0, 0, 'setBoth')
                self.setToonCondition(toon.doId, 'markedforsanction2', 1, 1, 'setBoth')
                if self.getToonConditionModifier(toonId, 'allGagBoost') < -25:
                    self.setToonCondition(toon.doId, 'allGagBoost', self.getToonConditionModifier(toonId, 'allGagBoost'), 3, 'setBoth')
                    self.setToonCondition(toon.doId, 'lureBoost', self.getToonConditionModifier(toonId, 'lureBoost'), 3, 'setBoth')
                else:
                    self.setToonCondition(toon.doId, 'allGagBoost', -25, 3, 'setBoth')
                    self.setToonCondition(toon.doId, 'lureBoost', -25, 3, 'setBoth')
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'StenographerCourtRecordBan':
                if self.toonHasCondition(toon.doId, 'banned'):
                    self.setToonCondition(toon.doId, 'banned', 1, 1, 'setBoth')
                    result = 50
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'bannedGagUsed', 0, 0, 'setBoth')
            elif atkType['name'] == 'CaseManagerInsurancePlanScapegoat':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                if len(self.battle.activeSuits) >= 2:
                    targetSuit = self.battle.activeSuits[1]
                else:
                    targetSuit = None
                if len(self.battle.activeSuits) >= 4:
                    targetSuit2 = self.battle.activeSuits[3]
                else:
                    targetSuit2 = None
                if len(self.battle.activeSuits) >= 6:
                    targetSuit3 = self.battle.activeSuits[5]
                else:
                    targetSuit3 = None
                targetSuits = [s for s in (targetSuit, targetSuit2, targetSuit3) if s is not None]
                self.setSuitCondition(theSuit.doId, 'insurancecalculator', 0, 0, 'setBoth')
                if self.suitHasCondition(theSuit.doId, 'insured2'):
                    self.setSuitCondition(theSuit.doId, 'insured2', 1, 3, 'setBoth')
                else:
                    self.setSuitCondition(theSuit.doId, 'insured2', 1, 3, 'setBoth')
                for target in targetSuits:
                    if self.suitHasCondition(target.doId, 'insured2'):
                        self.setSuitCondition(target.doId, 'insured2', 1, 3, 'setBoth')
                    else:
                        self.setSuitCondition(target.doId, 'insured2', 1, 3, 'setBoth')
                    if self.suitHasCondition(target.doId, 'sued'):
                        self.setSuitCondition(target.doId, 'sued', 1, 1, 'setBoth')
                        self.setSuitCondition(target.doId, 'suemovie', 0, 0, 'setBoth')
            elif atkType['name'] == 'CaseManagerInsurancePlanScapegoat2':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                if len(self.battle.activeSuits) >= 1:
                    targetSuit = self.battle.activeSuits[0]
                else:
                    targetSuit = None
                if len(self.battle.activeSuits) >= 3:
                    targetSuit2 = self.battle.activeSuits[2]
                else:
                    targetSuit2 = None
                if len(self.battle.activeSuits) >= 5:
                    targetSuit3 = self.battle.activeSuits[4]
                else:
                    targetSuit3 = None
                targetSuits = [s for s in (targetSuit, targetSuit2, targetSuit3) if s is not None]
                self.setSuitCondition(theSuit.doId, 'insurancecalculator', 0, 0, 'setBoth')
                if self.suitHasCondition(theSuit.doId, 'insured2'):
                    self.setSuitCondition(theSuit.doId, 'insured2', 1, 3, 'setBoth')
                else:
                    self.setSuitCondition(theSuit.doId, 'insured2', 1, 3, 'setBoth')
                for target in targetSuits:
                    if self.suitHasCondition(target.doId, 'insured2'):
                        self.setSuitCondition(target.doId, 'insured2', 1, 3, 'setBoth')
                    else:
                        self.setSuitCondition(target.doId, 'insured2', 1, 3, 'setBoth')
                    if self.suitHasCondition(target.doId, 'sued'):
                        self.setSuitCondition(target.doId, 'sued', 1, 1, 'setBoth')
                        self.setSuitCondition(target.doId, 'suemovie', 0, 0, 'setBoth')
            elif atkType['name'] == 'CaseManagerInsurancePlan':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                if len(self.battle.activeSuits) >= 2:
                    targetSuit = self.battle.activeSuits[1]
                else:
                    targetSuit = None
                if len(self.battle.activeSuits) >= 4:
                    targetSuit2 = self.battle.activeSuits[3]
                else:
                    targetSuit2 = None
                if len(self.battle.activeSuits) >= 6:
                    targetSuit3 = self.battle.activeSuits[5]
                else:
                    targetSuit3 = None
                targetSuits = [s for s in (targetSuit, targetSuit2, targetSuit3) if s is not None]
                self.setSuitCondition(theSuit.doId, 'insurancecalculator', 0, 0, 'setBoth')
                if self.suitHasCondition(theSuit.doId, 'insured'):
                    self.setSuitCondition(theSuit.doId, 'insured', 1, 3, 'setBoth')
                else:
                    self.setSuitCondition(theSuit.doId, 'insured', 1, 3, 'setBoth')
                for target in targetSuits:
                    if self.suitHasCondition(target.doId, 'insured'):
                        self.setSuitCondition(target.doId, 'insured', 1, 3, 'setBoth')
                    else:
                        self.setSuitCondition(target.doId, 'insured', 1, 3, 'setBoth')
                    if self.suitHasCondition(target.doId, 'sued'):
                        self.setSuitCondition(target.doId, 'sued', 1, 1, 'setBoth')
                        self.setSuitCondition(target.doId, 'suemovie', 0, 0, 'setBoth')
            elif atkType['name'] == 'CaseManagerInsurancePlan2':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                if len(self.battle.activeSuits) >= 1:
                    targetSuit = self.battle.activeSuits[0]
                else:
                    targetSuit = None
                if len(self.battle.activeSuits) >= 3:
                    targetSuit2 = self.battle.activeSuits[2]
                else:
                    targetSuit2 = None
                if len(self.battle.activeSuits) >= 5:
                    targetSuit3 = self.battle.activeSuits[4]
                else:
                    targetSuit3 = None
                targetSuits = [s for s in (targetSuit, targetSuit2, targetSuit3) if s is not None]
                self.setSuitCondition(theSuit.doId, 'insurancecalculator', 0, 0, 'setBoth')
                if self.suitHasCondition(theSuit.doId, 'insured'):
                    self.setSuitCondition(theSuit.doId, 'insured', 1, 3, 'setBoth')
                else:
                    self.setSuitCondition(theSuit.doId, 'insured', 1, 3, 'setBoth')
                for target in targetSuits:
                    if self.suitHasCondition(target.doId, 'insured'):
                        self.setSuitCondition(target.doId, 'insured', 1, 3, 'setBoth')
                    else:
                        self.setSuitCondition(target.doId, 'insured', 1, 3, 'setBoth')
                    if self.suitHasCondition(target.doId, 'sued'):
                        self.setSuitCondition(target.doId, 'sued', 1, 1, 'setBoth')
                        self.setSuitCondition(target.doId, 'suemovie', 0, 0, 'setBoth')
            elif atkType['name'] == 'CaseManagerInsurance':
                for s in self.battle.suits:
                    self.setSuitCondition(s.doId, 'healfinished', 1, 1, 'setBoth')
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for suit in self.battle.activeSuits:
                    if self.suitHasCondition(suit.doId, 'insured'):
                        if suit.currHP <= 0:
                            continue
                        x = (suit.maxHP * suit.hardMaxHP) - suit.currHP
                        if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
                            suit.setHP(suit.currHP + 0)
                        elif suit.currHP + 50 > (suit.maxHP * suit.hardMaxHP):
                            suit.setHP(suit.currHP + x)
                        else:
                            suit.setHP(suit.currHP + 50)
                    else:
                        pass
            elif atkType['name'] == 'CaseManagerInsurance2':
                for s in self.battle.suits:
                    self.setSuitCondition(s.doId, 'healfinished2', 1, 1, 'setBoth')
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for suit in self.battle.activeSuits:
                    if self.suitHasCondition(suit.doId, 'insured2'):
                        if suit.currHP <= 0:
                            continue
                        x = (suit.maxHP * suit.hardMaxHP) - suit.currHP
                        if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
                            suit.setHP(suit.currHP + 0)
                        elif suit.currHP + 85 > (suit.maxHP * suit.hardMaxHP):
                            suit.setHP(suit.currHP + x)
                        else:
                            suit.setHP(suit.currHP + 85)
                    else:
                        pass
            elif atkType['name'] == 'CaseManagerLegalBindings':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'bound', 1, 3, 'setBoth')
                self.setToonCondition(toon.doId, 'legalBindingsRecentlyTargeted', 1, 2, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'bindingscalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'CaseManagerLegalBindings2':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'insurancecalculator2', 0, 0, 'setBoth')
                currentBossHealth = -1
                for s in self.battle.suits:
                    if s.dna.name == 'lgator':
                        currentBossHealth = s.currHP
                if currentBossHealth >= 1:
                    for suit in self.battle.activeSuits:
                        suit.setDamageMultiplier(suit.getDamageMultiplier() * 1.1)
                elif currentBossHealth <= 0:
                    for suit in self.battle.activeSuits:
                        suit.setDamageMultiplier(suit.getDamageMultiplier() * 1.05)
                    continue
            elif atkType['name'] == 'CaseManagerLegallyBound':
                for s in self.battle.suits:
                    self.setSuitCondition(s.doId, 'dotfinished', 1, 1, 'setBoth')
                result = 20
                if self.toonHasCondition(toonId, 'snapped'):
                    result *= self.getToonConditionModifier(toonId, 'snapped')
                if self.toonHasCondition(toonId, 'bombedToon'):
                    result *= self.getToonConditionModifier(toonId, 'bombedToon')
                if self.toonHasCondition(toonId, 'markedwood'):
                    result *= self.getToonConditionModifier(toonId, 'markedwood')
                # Going to slowly replace individual status effects so we acclimate to the new system before moving onto a more sophisticated means of this.
                for condition in self.toonStatusConditionsNew[toonId]:
                    if isinstance(condition, StatusEffects.Snapped):
                        result *= condition.defenseMod
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'CaseManagerCourtRecordBan':
                if self.toonHasCondition(toon.doId, 'banned2'):
                    self.setToonCondition(toon.doId, 'banned2', 1, 1, 'setBoth')
                    result = 50
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'bannedGagUsed', 0, 0, 'setBoth')
            elif atkType['name'] == 'ArbitratorThrowBook': # Litigator
                result = self.getSuitConditionModifier(theSuit.doId, 'targetCheckCondition')
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'throwbookcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'targetCheckCondition', 0, 0, 'setBoth')
                targetSuit = self.battle.activeSuits[result]
                if not targetSuit.dna.name in SuitBattleGlobals.SpecialCogDict:
                    theSuit.setHP(theSuit.currHP + targetSuit.currHP)
                    targetSuit.setHP(targetSuit.currHP - targetSuit.currHP)
                    self.__removeLured(targetSuit.doId)
                    if self.suitHasCondition(targetSuit.doId, 'lured'):
                        self.setSuitCondition(targetSuit.doId, 'lured', 0, 0, 'setBoth')
            elif atkType['name'] == 'ArbitratorThrowBook2':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'throwbookcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target6', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target5', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target4', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target3', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target2', 0, 0, 'setBoth')
                targetSuit = self.battle.activeSuits[2]
                if not targetSuit.dna.name in SuitBattleGlobals.SpecialCogDict:
                    theSuit.setHP(theSuit.currHP + targetSuit.currHP)
                    targetSuit.setHP(targetSuit.currHP - targetSuit.currHP)
                    self.__removeLured(targetSuit.doId)
                    if self.suitHasCondition(targetSuit.doId, 'lured'):
                        self.setSuitCondition(targetSuit.doId, 'lured', 0, 0, 'setBoth')
            elif atkType['name'] == 'ArbitratorThrowBook3':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'throwbookcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target6', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target5', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target4', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target3', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target2', 0, 0, 'setBoth')
                targetSuit = self.battle.activeSuits[3]
                if not targetSuit.dna.name in SuitBattleGlobals.SpecialCogDict:
                    theSuit.setHP(theSuit.currHP + targetSuit.currHP)
                    targetSuit.setHP(targetSuit.currHP - targetSuit.currHP)
                    self.__removeLured(targetSuit.doId)
                    if self.suitHasCondition(targetSuit.doId, 'lured'):
                        self.setSuitCondition(targetSuit.doId, 'lured', 0, 0, 'setBoth')
            elif atkType['name'] == 'ArbitratorThrowBook4':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'throwbookcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target6', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target5', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target4', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target3', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target2', 0, 0, 'setBoth')
                targetSuit = self.battle.activeSuits[4]
                if not targetSuit.dna.name in SuitBattleGlobals.SpecialCogDict:
                    theSuit.setHP(theSuit.currHP + targetSuit.currHP)
                    targetSuit.setHP(targetSuit.currHP - targetSuit.currHP)
                    self.__removeLured(targetSuit.doId)
                    if self.suitHasCondition(targetSuit.doId, 'lured'):
                        self.setSuitCondition(targetSuit.doId, 'lured', 0, 0, 'setBoth')
            elif atkType['name'] == 'ArbitratorThrowBook5':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'throwbookcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target6', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target5', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target4', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target3', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target2', 0, 0, 'setBoth')
                targetSuit = self.battle.activeSuits[5]
                if not targetSuit.dna.name in SuitBattleGlobals.SpecialCogDict:
                    theSuit.setHP(theSuit.currHP + targetSuit.currHP)
                    targetSuit.setHP(targetSuit.currHP - targetSuit.currHP)
                    self.__removeLured(targetSuit.doId)
                    if self.suitHasCondition(targetSuit.doId, 'lured'):
                        self.setSuitCondition(targetSuit.doId, 'lured', 0, 0, 'setBoth')
            elif atkType['name'] == 'ArbitratorWhirlwind': # Stenographer
                self.setToonCondition(toon.doId, 'confused', 1, 2, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'whirlwindcalculator', 0, 0, 'setBoth')
                result = 25
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'ArbitratorPaperFiling': # Case Manager
                result = 15
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'noSOS', 1, 3, 'setBoth')
                self.setToonCondition(toon.doId, 'noFires', 1, 3, 'setBoth')
               # self.setToonCondition(toon.doId, 'noUnites', 1, 3, 'setBoth')
                self.setToonCondition(toon.doId, 'noSues', 1, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'paperfilingcalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'LitigatorSnapSoak': #soaked snap
                result = 33
                attack[SUIT_HP_COL][targetIndex] = result
                if self.getToonConditionModifier(toonId, 'snapped') > 1.1:
                    self.setToonCondition(toon.doId, 'snapped', self.getToonConditionModifier(toonId, 'snapped'), 3, 'setBoth')
                else:
                    self.setToonCondition(toon.doId, 'snapped', 1.1, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'snappedcalculator2', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'soakedcalculator', 0, 0, 'setBoth')
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'LitigatorSnapBindings': #bindings snap
                result = 33
                attack[SUIT_HP_COL][targetIndex] = result
                if self.getToonConditionModifier(toonId, 'snapped') > 1.1:
                    self.setToonCondition(toon.doId, 'snapped', self.getToonConditionModifier(toonId, 'snapped'), 3, 'setBoth')
                else:
                    self.setToonCondition(toon.doId, 'snapped', 1.1, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'snappedcalculator2', 0, 0, 'setBoth')
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'LitigatorSnapStenographer':
                result = 21
                attack[SUIT_HP_COL][targetIndex] = result
                if self.getToonConditionModifier(toonId, 'snapped') > 1.4:
                    self.setToonCondition(toon.doId, 'snapped', self.getToonConditionModifier(toonId, 'snapped'), 3, 'setBoth')
                else:
                    self.setToonCondition(toon.doId, 'snapped', 1.4, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'snappedcalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'LitigatorSnap':
                result = 25
                attack[SUIT_HP_COL][targetIndex] = result
                if self.getToonConditionModifier(toonId, 'snapped') > 1.2:
                    self.setToonCondition(toon.doId, 'snapped', self.getToonConditionModifier(toonId, 'snapped'), 3, 'setBoth')
                else:
                    self.setToonCondition(toon.doId, 'snapped', 1.2, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'snappedcalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'PresidentBayouBellow':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'bellowcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'bashcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'soakedcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'soakedcalculator2', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'unlureSuit', 0, 0, 'setBoth')
                for suit in self.battle.activeSuits:
                    self.setSuitCondition(suit.doId, 'dazed', 0, 0, 'setBoth')
                    if self.suitHasCondition(suit.doId, 'sued'):
                        self.setSuitCondition(suit.doId, 'sued', 1, 1, 'setBoth')
                        self.setSuitCondition(suit.doId, 'suemovie', 0, 0, 'setBoth')
                    if self.suitHasCondition(suit.doId, 'marked'):
                        self.setSuitCondition(suit.doId, 'marked', 1, 1, 'setBoth')
                    if self.suitHasCondition(suit.doId, 'soaked'):
                        self.setSuitCondition(suit.doId, 'soaked', 1, 1, 'setBoth')
                    if self.suitHasCondition(suit.doId, 'drenched'):
                        self.setSuitCondition(suit.doId, 'drenched', 1, 1, 'setBoth')
                    self.setSuitCondition(suit.doId, 'suemovie', 0, 0, 'setBoth')
                    self.setSuitCondition(suit.doId, 'zapped', 0, 0, 'setBoth')
                    if self.suitHasCondition(suit.doId, 'lured'):
                        self.setSuitCondition(suit.doId, 'lured', 0, 0, 'setBoth')
                        self.setSuitCondition(suit.doId, 'unlureSuit', 0, 0, 'setBoth')
                    continue
                for suit in self.currentlyLuredSuits.keys():
                    self.setSuitCondition(suit, 'bellowattack', 1, 1, 'setBoth')
                    self.__removeLured(suit)
            elif atkType['name'] == 'LitigatorBayouBellow':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'bellowcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'bashcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'soakedcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'soakedcalculator2', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'unlureSuit', 0, 0, 'setBoth')
                for suit in self.battle.activeSuits:
                    self.setSuitCondition(suit.doId, 'dazed', 0, 0, 'setBoth')
                    if self.suitHasCondition(suit.doId, 'sued'):
                        self.setSuitCondition(suit.doId, 'sued', 1, 1, 'setBoth')
                        self.setSuitCondition(suit.doId, 'suemovie', 0, 0, 'setBoth')
                    if self.suitHasCondition(suit.doId, 'marked'):
                        self.setSuitCondition(suit.doId, 'marked', 1, 1, 'setBoth')
                    if self.suitHasCondition(suit.doId, 'soaked'):
                        self.setSuitCondition(suit.doId, 'soaked', 1, 1, 'setBoth')
                    if self.suitHasCondition(suit.doId, 'drenched'):
                        self.setSuitCondition(suit.doId, 'drenched', 1, 1, 'setBoth')
                    self.setSuitCondition(suit.doId, 'suemovie', 0, 0, 'setBoth')
                    self.setSuitCondition(suit.doId, 'zapped', 0, 0, 'setBoth')
                    if self.suitHasCondition(suit.doId, 'lured'):
                        self.setSuitCondition(suit.doId, 'lured', 0, 0, 'setBoth')
                        self.setSuitCondition(suit.doId, 'unlureSuit', 0, 0, 'setBoth')
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
                        for s in self.battle.activeSuits:
                            if s in do.activeSuits:
                                boss = do
                                break
                        for s in self.battle.activeSuits:
                            if s in do.activeSuits:
                                if s.dna.name == 'lgator':
                                    maxSuits = 6

                                    aliveCount = len(self.battle.activeSuits) - self.deadSuits
                                    spawnAmount = maxSuits - aliveCount

                                    if spawnAmount > 0:
                                        for i in xrange(spawnAmount):
                                            if self.suitHasCondition(theSuit.doId, 'desperation'):
                                                boss.appendSuitsToBattle(boss.battleNumber, 'litDesperation')
                                            else:
                                                boss.appendSuitsToBattle(boss.battleNumber, 'lit')

                                    break
            elif atkType['name'] == 'ErfitPersonalTrainer':
                for suit in self.battle.activeSuits:
                    self.setSuitCondition(suit.doId, 'alreadyCogSpawn', 1, 1, 'setBoth')
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                if theSuit.currHP > 0:
                    if (theSuit.currHP - (theSuit.maxHP * .1)) <= 0:
                        theSuit.setHP(1)
                    else:
                        theSuit.setHP(theSuit.currHP - (theSuit.maxHP * .1))
                from toontown.suit.DistributedCountErclaimBossAI import DistributedCountErclaimBossAI

                boss = None
                for do in simbase.air.doId2do.values():
                    if isinstance(do, DistributedCountErclaimBossAI):
                        for s in self.battle.activeSuits:
                            if s in do.activeSuits:
                                boss = do
                                break
                        for s in self.battle.activeSuits:
                            if s in do.activeSuits:
                                if s.dna.name == 'erfit':
                                    maxSuits = 7

                                    aliveCount = len(self.battle.activeSuits) - self.deadSuits
                                    spawnAmount = min(4, maxSuits - aliveCount)

                                    if spawnAmount > 0:
                                        for i in xrange(spawnAmount):
                                            if theSuit.currHP <= (theSuit.maxHP * .25):
                                                boss.appendSuitsToBattle(boss.battleNumber, 'erfit5')
                                            elif theSuit.currHP <= (theSuit.maxHP * .375):
                                                boss.appendSuitsToBattle(boss.battleNumber, 'erfit4')
                                            elif theSuit.currHP <= (theSuit.maxHP * .5):
                                                boss.appendSuitsToBattle(boss.battleNumber, 'erfit3')
                                            elif theSuit.currHP <= (theSuit.maxHP * .675):
                                                boss.appendSuitsToBattle(boss.battleNumber, 'erfit3')
                                            elif theSuit.currHP <= (theSuit.maxHP * .75):
                                                boss.appendSuitsToBattle(boss.battleNumber, 'erfit2')
                                            else:
                                                boss.appendSuitsToBattle(boss.battleNumber, 'erfit1')

                                    break
            elif atkType['name'] == 'ErclaimRiseFromTheScrap':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                from toontown.suit.DistributedCountErclaimBossAI import DistributedCountErclaimBossAI

                boss = None
                for do in simbase.air.doId2do.values():
                    if isinstance(do, DistributedCountErclaimBossAI):
                        for s in self.battle.activeSuits:
                            if s in do.activeSuits:
                                boss = do
                                break
                        for s in self.battle.activeSuits:
                            if s in do.activeSuits:
                                if s.dna.name == 'erclaim':
                                    aliveCount = len(self.battle.activeSuits) - self.deadSuits
                                    spawnAmount = min(4, 7 - aliveCount)

                                    if spawnAmount > 0:
                                        for i in xrange(spawnAmount):
                                            if theSuit.currHP <= (theSuit.maxHP * .25):
                                                boss.appendSuitsToBattle(boss.battleNumber, 'erclaim2')
                                            else:
                                                boss.appendSuitsToBattle(boss.battleNumber, 'erclaim')
                                    break
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
                            self.setSuitCondition(suit.doId, 'insurancecalculator2', 1, 10, 'setBoth')
                            self.setSuitCondition(suit.doId, 'insurancecalculator3', 1, 10, 'setBoth')
                            self.setSuitCondition(suit.doId, 'ban2tracks', 1, 3, 'setBoth')
                    if s.dna.name == 'stenog':
                        suit = s
                        currentBossHealth = s.currHP
                        if currentBossHealth >= 1:
                            self.setSuitCondition(suit.doId, 'ban2levels', 1, 3, 'setBoth')
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
                self.setSuitCondition(theSuit.doId, 'shielding', 1, -1, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'rageBuilding', 1, -1, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'enraged', 0, 0, 'none')
                #self.setSuitCondition(theSuit.doId, 'gavelcalculator', 1, 10, 'setBoth')
                for s in self.battle.suits:
                    if s.dna.name == 'lgator':
                        suit = s
                        currentBossHealth = s.currHP
                        if currentBossHealth >= 1:
                            self.setSuitCondition(suit.doId, 'bellowcalculator2', 1, 10, 'setBoth')
                            self.setSuitCondition(suit.doId, 'bashcalculator', 1, 10, 'setBoth')
                            self.setSuitCondition(suit.doId, 'throwbookcalculator', 1, 10, 'setBoth')
            elif atkType['name'] == 'ScapegoatGavel':
                result = 5
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'noDamage', 1, 3, 'setBoth')
                self.setToonCondition(toon.doId, 'hidden', 1, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'gavelcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'gavelcalculator2', 1, 10, 'setBoth')
            elif atkType['name'] == 'ScapegoatRageBuilding':
                result = self.getSuitConditionModifier(theSuit.doId, 'rageBuilding')
                attack[SUIT_HP_COL][targetIndex] = result
                toon.setHp(toon.hp + result)
            elif atkType['name'] == 'ScapegoatBarnyardBash':
                result = 25
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'noDamage', 0, 0, 'setBoth')
                self.setToonCondition(toon.doId, 'hidden', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'gavelcalculator2', 0, 0, 'setBoth')
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'ReddPeckingOrder':
                result = 25
                attack[SUIT_HP_COL][targetIndex] = result
                if self.getToonConditionModifier(toonId, 'snapped') > 1.25:
                    self.setToonCondition(toon.doId, 'snapped', self.getToonConditionModifier(toonId, 'snapped'), 3, 'setBoth')
                else:
                    self.setToonCondition(toon.doId, 'snapped', 1.25, 3, 'setBoth')
                if self.getToonConditionModifier(toonId, 'allGagBoost2') > 25:
                    self.setToonCondition(toon.doId, 'allGagBoost2', self.getToonConditionModifier(toonId, 'allGagBoost2'), 3, 'setBoth')
                    self.setToonCondition(toon.doId, 'lureBoost2', self.getToonConditionModifier(toonId, 'lureBoost2'), 3, 'setBoth')
                else:
                    self.setToonCondition(toon.doId, 'allGagBoost', 25, 3, 'setBoth')
                    self.setToonCondition(toon.doId, 'lureBoost2', 25, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'snappedcalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'ErclaimSacrifice':
                result = self.getSuitConditionModifier(theSuit.doId, 'targetCheckCondition')
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'targetCheckCondition', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'sacrificeCooldown', 1, 4, 'setBoth')
                theSuit.setDamageMultiplier(theSuit.getDamageMultiplier() * 1.05)
                targetSuit = self.battle.activeSuits[result]
                self.calculator.deadSuits += 1
                if not targetSuit.dna.name in SuitBattleGlobals.SpecialCogDict:
                    theSuit.setHP(theSuit.currHP + targetSuit.currHP)
                    targetSuit.setHP(targetSuit.currHP - targetSuit.currHP)
                    self.__removeLured(targetSuit.doId)
                    if self.suitHasCondition(targetSuit.doId, 'lured'):
                        self.setSuitCondition(targetSuit.doId, 'lured', 0, 0, 'setBoth')
            elif atkType['name'] == 'ErfitGainsFromTheScrap':
                result = self.getSuitConditionModifier(theSuit.doId, 'targetCheckCondition')
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'targetCheckCondition', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'sacrificeCooldown', 1, 4, 'setBoth')
                theSuit.setDamageMultiplier(theSuit.getDamageMultiplier() * 1.05)
                targetSuit = self.battle.activeSuits[result]
                self.calculator.deadSuits += 1
                #theSuit.setHP(theSuit.currHP + targetSuit.currHP)
                for suit in self.battle.activeSuits:
                    if suit and suit != targetSuit and suit.getHP() > 0:
                        suit.setHP(suit.currHP + targetSuit.currHP)
                self.__removeLured(targetSuit.doId)
                targetSuit.setHP(targetSuit.currHP - targetSuit.currHP)
                if self.suitHasCondition(targetSuit.doId, 'lured'):
                    self.setSuitCondition(targetSuit.doId, 'lured', 0, 0, 'setBoth')
            elif atkType['name'] == 'ErclaimScopeCreep':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                if not self.suitHasCondition(theSuit.doId, 'directorDamageReduction'):
                    self.setSuitCondition(theSuit.doId, 'directorDamageReduction', .95, -1, 'setBoth')
                else:
                    self.setSuitCondition(theSuit.doId, 'directorDamageReduction', (self.getSuitConditionModifier(theSuit.doId, 'directorDamageReduction') - .05), -1, 'setBoth')
            elif atkType['name'] == 'ErclaimHemmorage':
                result = 20
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'snapped', 1.25, 1, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'snappedcalculator', 0, 0, 'setBoth')
                # from toontown.suit.DistributedLawbotBossAI import DistributedLawbotBossAI

                # boss = None
                # for do in simbase.air.doId2do.values():
                #     if isinstance(do, DistributedLawbotBossAI):
                #         for t in self.battle.activeToons:
                #             if t in do.involvedToons:
                #                 boss = do
                #                 break
                #         for t in self.battle.activeToons:
                #             if t in do.involvedToons:
                #                 for s in self.battle.suits:
                #                     if s.dna.name == 'wsi':
                #                         suit = s
                #                         currentBossHealth = s.currHP
                #                         if currentBossHealth <= 0:
                #                             if len(self.battle.activeSuits) < 5:
                #                                 boss.appendSuitsToBattle(boss.battleNumber, 'lit2')
            elif atkType['name'] == 'ReddLiquidationSale':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'soakedcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'soakedcalculator2', 1, 10, 'setBoth')
                #theSuit.setDamageMultiplier(theSuit.getDamageMultiplier() * 1.5)
            elif atkType['name'] == 'ReddAutoRepair':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for suit in self.battle.activeSuits:
                    if suit.currHP <= 0:
                        continue
                    x = (suit.maxHP * suit.hardMaxHP) - suit.currHP
                    if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
                        suit.setHP(suit.currHP + 0)
                    elif suit.currHP + (suit.maxHP * 0.35) > (suit.maxHP * suit.hardMaxHP):
                        suit.setHP(suit.currHP + x)
                    else:
                        suit.setHP(suit.currHP + (suit.maxHP * 0.35))
                continue
            elif atkType['name'] == 'WSIJuryNotice':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                from toontown.suit.DistributedLawbotBossAI import DistributedLawbotBossAI

                boss = None
                for do in simbase.air.doId2do.values():
                    if isinstance(do, DistributedLawbotBossAI):
                        for s in self.battle.activeSuits:
                            if s in do.activeSuits:
                                boss = do
                                break
                        for s in self.battle.activeSuits:
                            if s in do.activeSuits:
                                if s.dna.name == 'wsi':
                                    maxSuits = 7

                                    aliveCount = len(self.battle.activeSuits) - self.deadSuits
                                    spawnAmount = maxSuits - aliveCount

                                    if spawnAmount > 0:
                                        for i in xrange(spawnAmount):
                                            boss.appendSuitsToBattle(boss.battleNumber, 'lit2')

                                    break
            elif atkType['name'] == 'WSICeaseAndDesist':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'soakedcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'soakedcalculator2', 1, 10, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'unlureSuit', 0, 0, 'setBoth')
                for suit in self.battle.activeSuits:
                    self.setSuitCondition(suit.doId, 'deepfreeze', 1, 2, 'setBoth')
                    self.setSuitCondition(suit.doId, 'dazed', 0, 0, 'setBoth')
                    if self.suitHasCondition(suit.doId, 'sued'):
                        self.setSuitCondition(suit.doId, 'sued', 1, 1, 'setBoth')
                        self.setSuitCondition(suit.doId, 'suemovie', 0, 0, 'setBoth')
                    if self.suitHasCondition(suit.doId, 'marked'):
                        self.setSuitCondition(suit.doId, 'marked', 1, 1, 'setBoth')
                    if self.suitHasCondition(suit.doId, 'soaked'):
                        self.setSuitCondition(suit.doId, 'soaked', 1, 1, 'setBoth')
                    if self.suitHasCondition(suit.doId, 'drenched'):
                        self.setSuitCondition(suit.doId, 'drenched', 1, 1, 'setBoth')
                    self.setSuitCondition(suit.doId, 'suemovie', 0, 0, 'setBoth')
                    self.setSuitCondition(suit.doId, 'zapped', 0, 0, 'setBoth')
                    if self.suitHasCondition(suit.doId, 'lured'):
                        self.setSuitCondition(suit.doId, 'lured', 0, 0, 'setBoth')
                        self.setSuitCondition(suit.doId, 'unlureSuit', 0, 0, 'setBoth')
                    continue
                for suit in self.currentlyLuredSuits.keys():
                    self.__removeLured(suit)
            elif atkType['name'] == 'ErfitHydrationCheck':
                roll = random.randint(0, 100)
                if roll >= 15:
                    result = 18
                    self.setToonCondition(toon.doId, 'noDamage', 1, 1, 'setBoth')
                    self.setToonCondition(toon.doId, 'hidden', 1, 1, 'setBoth')
                    self.setToonCondition(toon.doId, 'hydrated', 1, 4, 'setBoth')
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'ErfitHydrationCheckRevert':
                if self.toonHasCondition(toon.doId, 'noDamage'):
                    result = 18
                    attack[SUIT_HP_COL][targetIndex] = result
                    self.setToonCondition(toon.doId, 'noDamage', 0, 0, 'setBoth')
                    self.setToonCondition(toon.doId, 'hidden', 0, 0, 'setBoth')
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'PowerhouseGroundbreaker':
                result = 5
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'noDamage', 1, 2, 'setBoth')
                self.setToonCondition(toon.doId, 'hidden', 1, 2, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'groundbreakercalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'PowerhouseGroundbreakerRevert':
                result = 25
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'noDamage', 0, 0, 'setBoth')
                self.setToonCondition(toon.doId, 'hidden', 0, 0, 'setBoth')
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'PowerhouseBurnDamage':
                for s in self.battle.suits:
                    self.setSuitCondition(s.doId, 'dotfinished', 1, 1, 'setBoth')
                result = 25
                if self.toonHasCondition(toonId, 'snapped'):
                    result *= self.getToonConditionModifier(toonId, 'snapped')
                if self.toonHasCondition(toonId, 'bombedToon'):
                    result *= self.getToonConditionModifier(toonId, 'bombedToon')
                if self.toonHasCondition(toonId, 'markedwood'):
                    result *= self.getToonConditionModifier(toonId, 'markedwood')
                # Going to slowly replace individual status effects so we acclimate to the new system before moving onto a more sophisticated means of this.
                for condition in self.toonStatusConditionsNew[toonId]:
                    if isinstance(condition, StatusEffects.Snapped):
                        result *= condition.defenseMod
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'PowerhouseAbsorb':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'shielding', 1, 1, 'setBoth')
            elif atkType['name'] == 'PowerhouseToleranceBuilding':
                result = self.getSuitConditionModifier(theSuit.doId, 'powerhouseRotation')
                attack[SUIT_HP_COL][targetIndex] = result
                toon.setHp(toon.hp + result)
            elif atkType['name'] == 'PowerhouseSoakImmune':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'soakImmune', 1, -1, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'powerhouseRotation', 1, -1, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'alreadySoakImmune', 1, 10, 'setBoth')
                for s in self.battle.suits:
                    if s.dna.name == 'wtapper':
                        suit = s
                        currentBossHealth = s.currHP
                        if currentBossHealth >= 1:
                            self.setSuitCondition(suit.doId, 'ban2levels', 1, 2, 'setBoth')
            elif atkType['name'] == 'PowerhouseDropImmune':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'dropImmune', 1, -1, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'powerhouseRotation', 1, -1, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'alreadyDropImmune', 1, 10, 'setBoth')
                for s in self.battle.suits:
                    if s.dna.name == 'wtapper':
                        suit = s
                        currentBossHealth = s.currHP
                        if currentBossHealth >= 1:
                            self.setSuitCondition(suit.doId, 'ban2levels', 1, 2, 'setBoth')
            elif atkType['name'] == 'PowerhouseZapImmune':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'zapImmune', 1, -1, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'powerhouseRotation', 1, -1, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'alreadyZapImmune', 1, 10, 'setBoth')
                for s in self.battle.suits:
                    if s.dna.name == 'wtapper':
                        suit = s
                        currentBossHealth = s.currHP
                        if currentBossHealth >= 1:
                            self.setSuitCondition(suit.doId, 'ban2levels', 1, 2, 'setBoth')
            elif atkType['name'] == 'PowerhouseLureImmune':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'lureImmune', 1, -1, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'powerhouseRotation', 1, -1, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'alreadyLureImmune', 1, 10, 'setBoth')
                for s in self.battle.suits:
                    if s.dna.name == 'wtapper':
                        suit = s
                        currentBossHealth = s.currHP
                        if currentBossHealth >= 1:
                            self.setSuitCondition(suit.doId, 'ban2levels', 1, 2, 'setBoth')
            elif atkType['name'] == 'PowerhouseSyphon':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'syphon', 1, -1, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'powerhouseRotation', 1, -1, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'alreadySyphon', 1, 10, 'setBoth')
                for s in self.battle.suits:
                    if s.dna.name == 'wtapper':
                        suit = s
                        currentBossHealth = s.currHP
                        if currentBossHealth >= 1:
                            self.setSuitCondition(suit.doId, 'ban2levels', 1, 2, 'setBoth')
            elif atkType['name'] == 'PowerhouseSyphonDesperation':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'syphoncalculator', 0, 0, 'setBoth')
                for suit in self.battle.activeSuits:
                    if suit.dna.name != 'cbutcher':
                        self.setSuitCondition(suit.doId, 'syphon', 1, 1, 'setBoth')
                        if self.suitHasCondition(suit.doId, 'sued'):
                            self.setSuitCondition(suit.doId, 'sued', 1, 1, 'setBoth')
                            self.setSuitCondition(suit.doId, 'suemovie', 0, 0, 'setBoth')
                        self.setSuitCondition(suit.doId, 'suemovie', 0, 0, 'setBoth')
            elif atkType['name'] == 'PowerhouseSnipeVulnerable':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'markImmune', 1, -1, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'powerhouseRotation', 1, -1, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'alreadyDropImmune', 1, 10, 'setBoth')
                for s in self.battle.suits:
                    if s.dna.name == 'wtapper':
                        suit = s
                        currentBossHealth = s.currHP
                        if currentBossHealth >= 1:
                            self.setSuitCondition(suit.doId, 'ban2levels', 1, 2, 'setBoth')
            elif atkType['name'] == 'PowerhouseSnipeMulligan':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'soundImmune', 1, -1, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'powerhouseRotation', 1, -1, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'alreadyDropImmune', 1, 10, 'setBoth')
                for s in self.battle.suits:
                    if s.dna.name == 'wtapper':
                        suit = s
                        currentBossHealth = s.currHP
                        if currentBossHealth >= 1:
                            self.setSuitCondition(suit.doId, 'ban2levels', 1, 2, 'setBoth')
            elif atkType['name'] == 'PowerhouseSnipeCollectCall':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'soakedcalculator', 0, 0, 'setBoth')
                if not self.suitHasCondition(theSuit.doId, 'vulnerablevideographer'):
                    self.setSuitCondition(theSuit.doId, 'vulnerablevideographer', 1.1, -1, 'setBoth')
                else:
                    self.setSuitCondition(theSuit.doId, 'vulnerablevideographer', (self.getSuitConditionModifier(theSuit.doId, 'vulnerablevideographer') * 1.1),
                                          -1, 'setBoth')
                theSuit.setDamageMultiplier(theSuit.getDamageMultiplier() * 1.1)
                self.setSuitCondition(theSuit.doId, 'soaked', 1, 1, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'drenched', 1, 1, 'setBoth')
            elif atkType['name'] == 'PowerhouseSnipeBookkept':
                if self.toonHasCondition(toon.doId, 'bookkeepingtoon'):
                    self.setToonCondition(toon.doId, 'zapped', 1, 3, 'setBoth')
                    self.setToonCondition(toon.doId, 'freshlyBurned', 1, 1, 'setBoth')
                    result = 25
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'bookkeepersnipe', 0, 0, 'setBoth')
            elif atkType['name'] == 'PowerhouseSnipeSoaked':
                if not self.toonHasCondition(toon.doId, 'noDamage'):
                    result = 25
                    self.setToonCondition(toon.doId, 'zapped', 1, 3, 'setBoth')
                    self.setToonCondition(toon.doId, 'freshlyBurned', 1, 1, 'setBoth')
                    attack[SUIT_HP_COL][targetIndex] = result
            # self.setSuitCondition(theSuit.doId, 'burncalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'PowerhouseSnipeGagBan':
                if self.toonHasCondition(toon.doId, 'banned') or self.toonHasCondition(toon.doId, 'banned2'):
                    self.setToonCondition(toon.doId, 'banned2', 1, 1, 'setBoth')
                    self.setToonCondition(toon.doId, 'banned', 1, 1, 'setBoth')
                    self.setToonCondition(toon.doId, 'zapped', 1, 3, 'setBoth')
                    self.setToonCondition(toon.doId, 'freshlyBurned', 1, 1, 'setBoth')
                    result = 25
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'gagbansnipe', 0, 0, 'setBoth')
            elif atkType['name'] == 'PowerhouseGeneration':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'zappedcalculator', 0, 0, 'setBoth')
                if not self.suitHasCondition(theSuit.doId, 'vulnerablevideographer'):
                    self.setSuitCondition(theSuit.doId, 'vulnerablevideographer', 1.05, -1, 'setBoth')
                else:
                    self.setSuitCondition(theSuit.doId, 'vulnerablevideographer', (self.getSuitConditionModifier(theSuit.doId, 'vulnerablevideographer') * 1.05),
                                              -1, 'setBoth')
                theSuit.setDamageMultiplier(theSuit.getDamageMultiplier() * 1.05)
                self.setSuitCondition(theSuit.doId, 'soaked', 1, 1, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'drenched', 1, 1, 'setBoth')
            elif atkType['name'] == 'PowerhouseGeneration2':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                if not self.suitHasCondition(theSuit.doId, 'vulnerablevideographer'):
                    self.setSuitCondition(theSuit.doId, 'vulnerablevideographer', 1.05, -1, 'setBoth')
                else:
                    self.setSuitCondition(theSuit.doId, 'vulnerablevideographer', (self.getSuitConditionModifier(theSuit.doId, 'vulnerablevideographer') * 1.05),
                                              -1, 'setBoth')
                theSuit.setDamageMultiplier(theSuit.getDamageMultiplier() * 1.05)
                self.setSuitCondition(theSuit.doId, 'damageReduction', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'shielding', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'zapImmune', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'dropImmune', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'soakImmune', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'markImmune', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'soundImmune', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'syphon', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'lureImmune', 0, 0, 'setBoth')
            elif atkType['name'] == 'AmbassadorManagerialProtection':
                self.setSuitCondition(theSuit.doId, 'pinkslipcalculator2', 0, 0, 'setBoth')
                result = 21
                attack[SUIT_HP_COL][targetIndex] = result
                if self.getToonConditionModifier(toonId, 'snapped') > 1.25:
                    self.setToonCondition(toon.doId, 'snapped', self.getToonConditionModifier(toonId, 'snapped'), 3, 'setBoth')
                else:
                    self.setToonCondition(toon.doId, 'snapped', 1.25, 3, 'setBoth')
                # # Search for if the Snapped effect exists.
                # for i in range(len(self.toonStatusConditionsNew[toon.doId])):
                #     if isinstance(self.toonStatusConditionsNew[toon.doId][i], StatusEffects.Snapped):
                #         # We have a Snapped effect.
                #         self.toonStatusConditionsNew[toon.doId][i].defenseMod = max(self.toonStatusConditionsNew[toon.doId][i].defenseMod, 1.25) # Set the defense modifier to whichever is greater.
                #         self.toonStatusConditionsNew[toon.doId][i].setRoundsLeft(2)
                #         break # Do not allow any more iterations.

                # else: # It does not; add a new effect.
                #     self.toonStatusConditionsNew[toon.doId].append(StatusEffects.Snapped(1.25))
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
                        self.setSuitCondition(suit.doId, 'oilRain', 1, 3, 'setBoth')
                        self.setSuitCondition(suit.doId, 'alreadyOilRain', 1, 1, 'setBoth')
                        self.setSuitCondition(suit.doId, 'directorDamageReduction', .9, 3, 'setBoth')
                        if self.suitHasCondition(suit.doId, 'sued'):
                            self.setSuitCondition(suit.doId, 'sued', 1, 1, 'setBoth')
                            self.setSuitCondition(suit.doId, 'suemovie', 0, 0, 'setBoth')
                        self.setSuitCondition(suit.doId, 'soaked', 0, 0, 'setBoth')
                        self.setSuitCondition(suit.doId, 'drenched', 0, 0, 'setBoth')
                        self.setSuitCondition(suit.doId, 'suemovie', 0, 0, 'setBoth')
                        # if suit.dna.name in ('wtapper', 'bkeeper', 'phouse', 'ambass'):
                        #     if suit.currHP <= 0:
                        #         continue
                        #     x = (suit.maxHP * suit.hardMaxHP) - suit.currHP
                        #     if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
                        #         suit.setHP(suit.currHP + 0)
                        #     elif suit.currHP + 350 > (suit.maxHP * suit.hardMaxHP):
                        #         suit.setHP(suit.currHP + x)
                        #     else:
                        #         suit.setHP(suit.currHP + 350)
                        # else:
                        #     if suit.currHP <= 0:
                        #         continue
                        #     x = (suit.maxHP * suit.hardMaxHP) - suit.currHP
                        #     if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
                        #         suit.setHP(suit.currHP + 0)
                        #     elif suit.currHP + 275 > (suit.maxHP * suit.hardMaxHP):
                        #         suit.setHP(suit.currHP + x)
                        #     else:
                        #         suit.setHP(suit.currHP + 275)
                elif currentBossHealth <= 0:
                    for suit in self.battle.activeSuits:
                        self.setSuitCondition(suit.doId, 'oilRain', 1, 3, 'setBoth')
                        self.setSuitCondition(suit.doId, 'alreadyOilRain', 1, 1, 'setBoth')
                        self.setSuitCondition(suit.doId, 'directorDamageReduction', .9, 3, 'setBoth')
                        if self.suitHasCondition(suit.doId, 'sued'):
                            self.setSuitCondition(suit.doId, 'sued', 1, 1, 'setBoth')
                            self.setSuitCondition(suit.doId, 'suemovie', 0, 0, 'setBoth')
                        self.setSuitCondition(suit.doId, 'soaked', 0, 0, 'setBoth')
                        self.setSuitCondition(suit.doId, 'drenched', 0, 0, 'setBoth')
                        self.setSuitCondition(suit.doId, 'suemovie', 0, 0, 'setBoth')
                        # if suit.dna.name in ('wtapper', 'bkeeper', 'phouse', 'ambass'):
                        #     if suit.currHP <= 0:
                        #         continue
                        #     x = (suit.maxHP * suit.hardMaxHP) - suit.currHP
                        #     if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
                        #         suit.setHP(suit.currHP + 0)
                        #     elif suit.currHP + 200 > (suit.maxHP * suit.hardMaxHP):
                        #         suit.setHP(suit.currHP + x)
                        #     else:
                        #         suit.setHP(suit.currHP + 200)
                        # else:
                        #     if suit.currHP <= 0:
                        #         continue
                        #     x = (suit.maxHP * suit.hardMaxHP) - suit.currHP
                        #     if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
                        #         suit.setHP(suit.currHP + 0)
                        #     elif suit.currHP + 175 > (suit.maxHP * suit.hardMaxHP):
                        #         suit.setHP(suit.currHP + x)
                        #     else:
                        #         suit.setHP(suit.currHP + 175)
            elif atkType['name'] == 'AmbassadorRefinementManager':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'immune', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'refinemanagercalculator', 0, 0, 'setBoth')
                # currentBossHealth = -1
                # for s in self.battle.suits:
                #     if s.dna.name == 'phouse':
                #         currentBossHealth = s.currHP
                # if currentBossHealth >= 1:
                #     for suit in self.battle.activeSuits:
                #         if suit.dna.name in ('wtapper', 'bkeeper', 'phouse'):
                #             if suit.currHP <= 0:
                #                 continue
                #             x = (suit.maxHP * suit.hardMaxHP) - suit.currHP
                #             if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
                #                 suit.setHP(suit.currHP + 0)
                #             elif suit.currHP + 350 > (suit.maxHP * suit.hardMaxHP):
                #                 suit.setHP(suit.currHP + x)
                #             else:
                #                 suit.setHP(suit.currHP + 350)
                # elif currentBossHealth <= 0:
                #     for suit in self.battle.activeSuits:
                #         if suit.dna.name in ('wtapper', 'bkeeper', 'phouse'):
                #             if suit.currHP <= 0:
                #                 continue
                #             x = (suit.maxHP * suit.hardMaxHP) - suit.currHP
                #             if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
                #                 suit.setHP(suit.currHP + 0)
                #             elif suit.currHP + 200 > (suit.maxHP * suit.hardMaxHP):
                #                 suit.setHP(suit.currHP + x)
                #             else:
                #                 suit.setHP(suit.currHP + 200)
                #         continue
            elif atkType['name'] == 'AmbassadorAdvancement':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'advancementcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'headroller2calculator', 1, 10, 'setBoth')
                for suit in self.battle.activeSuits:
                    if not suit.getManager() and not suit.getGovernaught():
                        self.setSuitCondition(suit.doId, 'ambheadrollertarget', 1, 10, 'setBoth')
            elif atkType['name'] == 'AmbassadorAdvancement2':
                self.setSuitCondition(theSuit.doId, 'papercutcalculator2', 0, 0, 'setBoth')
                self.setToonCondition(toon.doId, 'contingencyMarked', 1, 3, 'setBoth')
                result = 25
                attack[SUIT_HP_COL][targetIndex] = result
                if self.getToonConditionModifier(toonId, 'allGagBoost') > 25:
                    self.setToonCondition(toon.doId, 'allGagBoost',
                                          self.getToonConditionModifier(toonId, 'allGagBoost'), 3, 'setBoth')
                    self.setToonCondition(toon.doId, 'lureBoost',
                                          self.getToonConditionModifier(toonId, 'lureBoost'), 3, 'setBoth')
                else:
                    self.setToonCondition(toon.doId, 'allGagBoost', 25, 3, 'setBoth')
                    self.setToonCondition(toon.doId, 'lureBoost', 25, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'papercutcalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'AmbassadorAdvancement3':
                self.setSuitCondition(theSuit.doId, 'papercutcalculator3', 0, 0, 'setBoth')
                self.setToonCondition(toon.doId, 'contingencyMarked', 1, 3, 'setBoth')
                result = 25
                attack[SUIT_HP_COL][targetIndex] = result
                if self.getToonConditionModifier(toonId, 'allGagBoost') > 25:
                    self.setToonCondition(toon.doId, 'allGagBoost',
                                          self.getToonConditionModifier(toonId, 'allGagBoost'), 3, 'setBoth')
                    self.setToonCondition(toon.doId, 'lureBoost',
                                          self.getToonConditionModifier(toonId, 'lureBoost'), 3, 'setBoth')
                else:
                    self.setToonCondition(toon.doId, 'allGagBoost', 25, 3, 'setBoth')
                    self.setToonCondition(toon.doId, 'lureBoost', 25, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'papercutcalculator', 0, 0, 'setBoth')
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
                self.__removeLured(targetSuit.doId)
                if self.suitHasCondition(targetSuit.doId, 'lured'):
                    self.setSuitCondition(targetSuit.doId, 'lured', 0, 0, 'setBoth')
            elif atkType['name'] == 'AmbassadorHeadRoller':
                result = self.syphonedHP
                attack[SUIT_HP_COL][targetIndex] = result
                buffPercent = ((self.syphonedHP * 0.05) * 0.01)
                theSuit.setDamageMultiplier(theSuit.getDamageMultiplier() * (1.0 + buffPercent))
                theSuit.setHP(theSuit.currHP + result)
                self.setSuitCondition(theSuit.doId, 'headrollertargetcalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'AmbassadorHeadRoller2':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'headrollertargetcalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'AmbassadorHeadRoller3':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'headrollertargetcalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'AmbassadorHeadRoller4':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'headrollertargetcalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'AmbassadorHeadRoller5':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'headrollertargetcalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'AmbassadorPhase2':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'phase3', 1, -1, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'headrollercalculator', 1, 10, 'setBoth')
                theSuit.setDamageMultiplier(theSuit.getDamageMultiplier() * 1.5)
                theSuit.setSkeleton(1)
            elif atkType['name'] == 'AmbassadorMulligan':
                roll = random.randint(0, 100)
                if roll >= 20:
                    if not self.toonHasCondition(toon.doId, 'hidden'):
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
                self.setSuitCondition(theSuit.doId, 'pinkslipcalculator', 0, 0, 'setBoth')
                result = 21
                attack[SUIT_HP_COL][targetIndex] = result
                if self.getToonConditionModifier(toonId, 'snapped') > 1.25:
                    self.setToonCondition(toon.doId, 'snapped', self.getToonConditionModifier(toonId, 'snapped'), 3, 'setBoth')
                else:
                    self.setToonCondition(toon.doId, 'snapped', 1.25, 3, 'setBoth')
                # # Search for if the Snapped effect exists.
                # for i in range(len(self.toonStatusConditionsNew[toon.doId])):
                #     if isinstance(self.toonStatusConditionsNew[toon.doId][i], StatusEffects.Snapped):
                #         # We have a Snapped effect.
                #         self.toonStatusConditionsNew[toon.doId][i].defenseMod = max(self.toonStatusConditionsNew[toon.doId][i].defenseMod, 1.25) # Set the defense modifier to whichever is greater.
                #         self.toonStatusConditionsNew[toon.doId][i].setRoundsLeft(2)
                #         break # Do not allow any more iterations.

                # else: # It does not; add a new effect.
                #     self.toonStatusConditionsNew[toon.doId].append(StatusEffects.Snapped(1.25))
            elif atkType['name'] == 'AmbassadorHeadRollerGroup':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                #self.setSuitCondition(theSuit.doId, 'damageupcalculator2', 1, 1, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'headroller2calculator', 1, 1, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'headrollercalculator', 0, 0, 'setBoth')
                for s in self.battle.suits:
                    if s.dna.name == 'wtapper':
                        suit = s
                        currentBossHealth = s.currHP
                        if currentBossHealth >= 1:
                            self.setSuitCondition(suit.doId, 'ban2tracks', 1, 2, 'setBoth')
                for suit in self.battle.activeSuits:
                    if suit.currHP <= 0:
                        continue
                    if not suit.dna.name in SuitBattleGlobals.SpecialCogDict and self.suitHasCondition(suit.doId, 'ambheadrollertarget') and suit.currHP > 0:
                        #self.sacrificedCogs += 1
                        suit.setHP(suit.currHP - suit.currHP)
                        self.setSuitCondition(suit.doId, 'dead', 1, 2, 'setBoth')
                        if self.suitHasCondition(suit.doId, 'lured'):
                            self.setSuitCondition(suit.doId, 'lured', 0, 0, 'setBoth')
                        self.__removeLured(suit.doId)
                    continue
            elif atkType['name'] == 'AmbassadorDamageUp': # Visual Damage Up
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'AmbassadorGhostMentality':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'headrollercalculator', 0, 0, 'setBoth')
                for suit in self.battle.activeSuits:
                    if suit.dna.name not in SuitBattleGlobals.SpecialCogDict:
                        if self.suitHasCondition(suit.doId, 'sued'):
                            self.setSuitCondition(suit.doId, 'sued', 1, 1, 'setBoth')
                        self.setSuitCondition(suit.doId, 'suemovie', 0, 0, 'setBoth')
                        self.setSuitCondition(suit.doId, 'suemovie', 0, 0, 'setBoth')
                        suit.setDamageMultiplier(suit.getDamageMultiplier() * 1.5)
                        suit.setVirtual(1)
                        #self.setSuitCondition(suit.doId, 'contracted', 1, -1, 'setBoth')
            elif atkType['name'] == 'BookkeeperBookkeepingRetaliation':
                if self.toonHasCondition(toon.doId, 'bookkeepingtoon'):
                    self.setToonCondition(toon.doId, 'bookkeepingtoon', 1, 1, 'setBoth')
                    if self.getToonConditionModifier(toonId, 'allGagBoost') < -99:
                        self.setToonCondition(toon.doId, 'allGagBoost',
                                              self.getToonConditionModifier(toonId, 'allGagBoost'), 2, 'setBoth')
                        self.setToonCondition(toon.doId, 'lureBoost',
                                              self.getToonConditionModifier(toonId, 'lureBoost'), 2, 'setBoth')
                    else:
                        self.setToonCondition(toon.doId, 'allGagBoost', -99, 2, 'setBoth')
                        self.setToonCondition(toon.doId, 'lureBoost', -99, 2, 'setBoth')
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
                self.setSuitCondition(theSuit.doId, 'bookkeeping', 0, 0, 'setBoth')
            elif atkType['name'] == 'BookkeeperBookkeeping':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'bookkeeping', 1, 2, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'bookkeepingcalculator', 0, 0, 'setBoth')
                for s in self.battle.suits:
                    if s.dna.name == 'wtapper':
                        suit = s
                        currentBossHealth = s.currHP
                        if currentBossHealth >= 1:
                            self.setSuitCondition(suit.doId, 'ban2tracks', 1, 2, 'setBoth')
                if self.suitHasCondition(theSuit.doId, 'lured'):
                    self.setSuitCondition(theSuit.doId, 'lured', 0, 0, 'setBoth')
                self.__removeLured(theSuit.doId)
            elif atkType['name'] == 'BookkeeperMandatoryFiling':
                result = 10
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'dodgy', -100, 1, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'filingcalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'BookkeeperExplodingDocument':
                result = 20
                attack[SUIT_HP_COL][targetIndex] = result
                for s in self.battle.suits:
                    if s.dna.name == 'wtapper':
                        suit = s
                        currentBossHealth = s.currHP
                        if currentBossHealth >= 1:
                            self.setSuitCondition(suit.doId, 'ban2tracks', 1, 2, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'explodingcalculator', 0, 0, 'setBoth')
                for suit in self.battle.activeSuits:
                    self.setSuitCondition(suit.doId, 'overseer', 1, 3, 'setBoth')
            elif atkType['name'] == 'BookkeeperPaperCutMarked':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'bookkeeping', 0, 0, 'setBoth')
                theSuit.setDamageMultiplier(theSuit.getDamageMultiplier() * 1.1)
            elif atkType['name'] == 'BookkeeperPaperCutSoaked':
                if self.toonHasCondition(toon.doId, 'contingencyMarked') and self.toonHasCondition(toon.doId, 'contingencyHit'):
                    self.setToonCondition(toon.doId, 'contingencyHit', 0, 0, 'setBoth')
                    self.setSuitCondition(theSuit.doId, 'soakedcalculator', 0, 0, 'setBoth')
                    result = 20
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'BookkeeperPaperCut':
                self.setToonCondition(toon.doId, 'contingencyMarked', 1, 3, 'setBoth')
                self.setToonCondition(toon.doId, 'paperCutRecentlyTargeted', 1, 2, 'setBoth')
                result = 25
                attack[SUIT_HP_COL][targetIndex] = result
                if self.getToonConditionModifier(toonId, 'allGagBoost') > 25:
                    self.setToonCondition(toon.doId, 'allGagBoost',
                                          self.getToonConditionModifier(toonId, 'allGagBoost'), 3, 'setBoth')
                    self.setToonCondition(toon.doId, 'lureBoost',
                                          self.getToonConditionModifier(toonId, 'lureBoost'), 3, 'setBoth')
                else:
                    self.setToonCondition(toon.doId, 'allGagBoost', 25, 3, 'setBoth')
                    self.setToonCondition(toon.doId, 'lureBoost', 25, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'papercutcalculator', 0, 0, 'setBoth')
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
                self.setSuitCondition(theSuit.doId, 'collectcalled', 0, 0, 'setBoth')
                if self.toonHasCondition(toon.doId, 'collectcalled'):
                    self.setToonCondition(toon.doId, 'confused', 1, 2, 'setBoth')
                    result = 25
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'WiretapperCollectCall2': # Collect Call Calculator
                self.setSuitCondition(theSuit.doId, 'calculatingcalculator', 1, 1, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'costscalculator', 1, 10, 'setBoth')
                if theSuit.currHP <= 2500:
                    self.calculator.collectCallMultiplier += 8
                    self.calculator.collectCallCalculatorMultiplier += 8
                else:
                    self.calculator.collectCallMultiplier += 4
                    self.calculator.collectCallCalculatorMultiplier += 4
                result = self.calculator.collectCallCalculatorMultiplier
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'WiretapperVoicemail':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'immune', 1, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'voicemailcalculator', 0, 0, 'setBoth')
                #self.setSuitCondition(theSuit.doId, 'levelshielding', 1, 2, 'setBoth')
            elif atkType['name'] == 'WiretapperBrokenConnection':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                #self.setSuitCondition(theSuit.doId, 'vulnerable', 1, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'vulnerablevideographer', 1.3, -1, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'brokenconnection', 1, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'brokenconnectioncalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'WiretapperWiretapped':
                self.setSuitCondition(theSuit.doId, 'wiretappedcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'collectcallcalculator2', 1, 10, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'vulnerablevideographer', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'vulnerable', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'brokenconnection', 0, 0, 'setBoth')
                randomizer = random.randint(-99, 100)
                self.setToonCondition(toon.doId, 'allGagBoost', randomizer, 2, 'setBoth')
                self.setToonCondition(toon.doId, 'lureBoost', randomizer, 2, 'setBoth')
                result = randomizer
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'WiretapperCollectCall':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'collectCallRecentlyTargeted', 1, 1, 'setBoth')
                self.setToonCondition(toon.doId, 'collectcalled', 1, 2, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'collectcalled', 1, 2, 'setBoth')
                self.setToonCondition(toon.doId, 'partnered', 1, 2, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'partnered', 1, 2, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'collectcallcalculator2', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'collectcallcalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'WiretapperCollectCallDamage':
                self.setSuitCondition(theSuit.doId, 'costscalculator', 0, 0, 'setBoth')
                result = self.collectCallMultiplier
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'SafetyHighPressure':
                result = 35
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'cannotDodge', 100, 2, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'cannotDodge', 100, 2, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'highpressurecalculator', 0, 0, 'setBoth')
                for suit in self.battle.activeSuits:
                    if suit.dna.name != 'cdirector':
                        suit.setHP(math.ceil(suit.currHP - 50))
                        if suit.currHP <= 0:
                            self.setSuitCondition(suit.doId, 'dead', 1, 2, 'setBoth')
                            if suit.dna.name == 'cbutcher':
                                for s in self.battle.activeSuits:
                                    if s.dna.name == 'rkeeper':
                                        self.setSuitCondition(s.doId, 'phantomDeath', 1, 1, 'setBoth')
                            if self.suitHasCondition(suit.doId, 'overpressure'):
                                for s in self.battle.activeSuits:
                                    if s.dna.name == 'safesupervis':
                                        if self.suitHasCondition(suit.doId, 'overpressureDeath'):
                                            self.setSuitCondition(s.doId, 'overpressureDeath2', 1, 1, 'setBoth')
                                        elif self.suitHasCondition(suit.doId, 'overpressureDeath2'):
                                            self.setSuitCondition(s.doId, 'overpressureDeath3', 1, 1, 'setBoth')
                                        else:
                                            self.setSuitCondition(s.doId, 'overpressureDeath', 1, 1, 'setBoth')
                            self.__removeLured(suit.doId)
                            if not self.suitHasCondition(suit.doId, 'dead'):
                                self.calculator.deadSuits += 1
                                self.setSuitCondition(suit.doId, 'dead', 1, -1, 'setBoth')
                    continue
            elif atkType['name'] == 'SafetyHeatWaveCalculation':
                result = (1 + (math.ceil(theSuit.getMaxHP() - theSuit.getHP()) / 60))
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'heatwavecalculationcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'heatwavecalculator', 1, 10, 'setBoth')
            elif atkType['name'] == 'SafetyHeatWave':
                result = (1 + (math.ceil((theSuit.getMaxHP() - theSuit.getHP()) / 60)))
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'heatwavecalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'SafetyOverpressured':
                result = self.getSuitConditionModifier(theSuit.doId, 'targetCheckCondition')
                attack[SUIT_HP_COL][targetIndex] = result
                targetSuit = self.battle.activeSuits[result]
                targetSuit.setHP(targetSuit.getMaxHP() * 2)
                targetSuit.setMaxHP(targetSuit.getMaxHP() * 2)
                targetSuit.setDamageMultiplier(targetSuit.getDamageMultiplier() * 1.5)
                if not targetSuit.getSkeleton() > 0:
                    targetSuit.setSkeleton(1)
                else:
                    targetSuit.setVirtual(1)
                #self.setSuitCondition(targetSuit.doId, 'contracted', 1, -1, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'overpressure', 1, -1, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'vulnerablevideographer', 1.5, -1, 'setBoth')
                if not self.suitHasCondition(targetSuit.doId, 'dead'):
                    self.setSuitCondition(theSuit.doId, 'overpressurecalculator', 0, 0, 'setBoth')
                continue
            # elif atkType['name'] == 'SafetyOverpressured2':
            #     result = 0
            #     attack[SUIT_HP_COL][targetIndex] = result
            #     targetSuit = self.battle.activeSuits[2]
            #     self.setSuitCondition(theSuit.doId, 'target6', 0, 0, 'setBoth')
            #     self.setSuitCondition(theSuit.doId, 'target5', 0, 0, 'setBoth')
            #     self.setSuitCondition(theSuit.doId, 'target4', 0, 0, 'setBoth')
            #     self.setSuitCondition(theSuit.doId, 'target3', 0, 0, 'setBoth')
            #     self.setSuitCondition(theSuit.doId, 'target2', 0, 0, 'setBoth')
            #     targetSuit.setHP(targetSuit.getMaxHP() * 2)
            #     targetSuit.setMaxHP(targetSuit.getMaxHP() * 2)
            #     targetSuit.setDamageMultiplier(targetSuit.getDamageMultiplier() * 1.5)
            #     if not targetSuit.getSkeleton() > 0:
            #         targetSuit.setSkeleton(1)
            #     else:
            #         targetSuit.setVirtual(1)
            #     #self.setSuitCondition(targetSuit.doId, 'contracted', 1, -1, 'setBoth')
            #     self.setSuitCondition(targetSuit.doId, 'overpressure', 1, -1, 'setBoth')
            #     self.setSuitCondition(targetSuit.doId, 'vulnerablevideographer', 50, -1, 'setBoth')
            #     if not self.suitHasCondition(targetSuit.doId, 'dead'):
            #         self.setSuitCondition(theSuit.doId, 'overpressurecalculator', 0, 0, 'setBoth')
            #     continue
            # elif atkType['name'] == 'SafetyOverpressured3':
            #     result = 0
            #     attack[SUIT_HP_COL][targetIndex] = result
            #     for s in self.battle.suits:
            #         if s.dna.name == 'ubuster':
            #             suit = s
            #             currentBossHealth = s.currHP
            #             if currentBossHealth >= 1:
            #                 self.setSuitCondition(suit.doId, 'noUnionBust', 1, 1, 'setBoth')
            #     targetSuit = self.battle.activeSuits[3]
            #     self.setSuitCondition(theSuit.doId, 'target6', 0, 0, 'setBoth')
            #     self.setSuitCondition(theSuit.doId, 'target5', 0, 0, 'setBoth')
            #     self.setSuitCondition(theSuit.doId, 'target4', 0, 0, 'setBoth')
            #     self.setSuitCondition(theSuit.doId, 'target3', 0, 0, 'setBoth')
            #     self.setSuitCondition(theSuit.doId, 'target2', 0, 0, 'setBoth')
            #     targetSuit.setHP(targetSuit.getMaxHP() * 2)
            #     targetSuit.setMaxHP(targetSuit.getMaxHP() * 2)
            #     targetSuit.setDamageMultiplier(targetSuit.getDamageMultiplier() * 1.5)
            #     if not targetSuit.getSkeleton() > 0:
            #         targetSuit.setSkeleton(1)
            #     else:
            #         targetSuit.setVirtual(1)
            #     #self.setSuitCondition(targetSuit.doId, 'contracted', 1, -1, 'setBoth')
            #     self.setSuitCondition(targetSuit.doId, 'overpressure', 1, -1, 'setBoth')
            #     self.setSuitCondition(targetSuit.doId, 'vulnerablevideographer', 50, -1, 'setBoth')
            #     if not self.suitHasCondition(targetSuit.doId, 'dead'):
            #         self.setSuitCondition(theSuit.doId, 'overpressurecalculator', 0, 0, 'setBoth')
            #     continue
            # elif atkType['name'] == 'SafetyOverpressured4':
            #     result = 0
            #     attack[SUIT_HP_COL][targetIndex] = result
            #     for s in self.battle.suits:
            #         if s.dna.name == 'ubuster':
            #             suit = s
            #             currentBossHealth = s.currHP
            #             if currentBossHealth >= 1:
            #                 self.setSuitCondition(suit.doId, 'noUnionBust', 1, 1, 'setBoth')
            #     targetSuit = self.battle.activeSuits[4]
            #     self.setSuitCondition(theSuit.doId, 'target6', 0, 0, 'setBoth')
            #     self.setSuitCondition(theSuit.doId, 'target5', 0, 0, 'setBoth')
            #     self.setSuitCondition(theSuit.doId, 'target4', 0, 0, 'setBoth')
            #     self.setSuitCondition(theSuit.doId, 'target3', 0, 0, 'setBoth')
            #     self.setSuitCondition(theSuit.doId, 'target2', 0, 0, 'setBoth')
            #     if not targetSuit.getSkeleton() > 0:
            #         targetSuit.setSkeleton(1)
            #     else:
            #         targetSuit.setVirtual(1)
            #     targetSuit.setHP(targetSuit.getMaxHP() * 2)
            #     targetSuit.setMaxHP(targetSuit.getMaxHP() * 2)
            #     #self.setSuitCondition(targetSuit.doId, 'contracted', 1, -1, 'setBoth')
            #     self.setSuitCondition(targetSuit.doId, 'overpressure', 1, -1, 'setBoth')
            #     self.setSuitCondition(targetSuit.doId, 'vulnerablevideographer', 50, -1, 'setBoth')
            #     if not self.suitHasCondition(targetSuit.doId, 'dead'):
            #         self.setSuitCondition(theSuit.doId, 'overpressurecalculator', 0, 0, 'setBoth')
            #     continue
            # elif atkType['name'] == 'SafetyOverpressured5':
            #     result = 0
            #     attack[SUIT_HP_COL][targetIndex] = result
            #     for s in self.battle.suits:
            #         if s.dna.name == 'ubuster':
            #             suit = s
            #             currentBossHealth = s.currHP
            #             if currentBossHealth >= 1:
            #                 self.setSuitCondition(suit.doId, 'noUnionBust', 1, 1, 'setBoth')
            #     targetSuit = self.battle.activeSuits[5]
            #     self.setSuitCondition(theSuit.doId, 'target6', 0, 0, 'setBoth')
            #     self.setSuitCondition(theSuit.doId, 'target5', 0, 0, 'setBoth')
            #     self.setSuitCondition(theSuit.doId, 'target4', 0, 0, 'setBoth')
            #     self.setSuitCondition(theSuit.doId, 'target3', 0, 0, 'setBoth')
            #     self.setSuitCondition(theSuit.doId, 'target2', 0, 0, 'setBoth')
            #     if not targetSuit.getSkeleton() > 0:
            #         targetSuit.setSkeleton(1)
            #     else:
            #         targetSuit.setVirtual(1)
            #     targetSuit.setHP(targetSuit.getMaxHP() * 2)
            #     targetSuit.setMaxHP(targetSuit.getMaxHP() * 2)
            #     targetSuit.setDamageMultiplier(targetSuit.getDamageMultiplier() * 1.5)
            #    # self.setSuitCondition(targetSuit.doId, 'contracted', 1, -1, 'setBoth')
            #     self.setSuitCondition(targetSuit.doId, 'overpressure', 1, -1, 'setBoth')
            #     self.setSuitCondition(targetSuit.doId, 'vulnerablevideographer', 50, -1, 'setBoth')
            #     if not self.suitHasCondition(targetSuit.doId, 'dead'):
            #         self.setSuitCondition(theSuit.doId, 'overpressurecalculator', 0, 0, 'setBoth')
            #     continue
            elif atkType['name'] == 'SafetyOverpressureDeath':
                result = int(math.ceil(theSuit.getMaxHP() / 2))
                attack[SUIT_HP_COL][targetIndex] = result
                for suit in self.battle.activeSuits:
                    if not self.suitHasCondition(suit.doId, 'overpressure'):
                        managerTarget = suit
                        if managerTarget == None:
                            continue
                        managerTarget.setHP(managerTarget.currHP - result)
                        if managerTarget.currHP <= 0:
                            if managerTarget.getSkeleRevives() >= 1:
                                managerTarget.useSkeleRevive()
                            self.__removeLured(managerTarget.doId)
                            if not self.suitHasCondition(managerTarget.doId, 'dead'):
                                self.calculator.deadSuits += 1
                                self.setSuitCondition(managerTarget.doId, 'dead', 1, -1, 'setBoth')
            elif atkType['name'] == 'SafetyPromotion':
                result = self.getSuitConditionModifier(theSuit.doId, 'targetCheckCondition')
                attack[SUIT_HP_COL][targetIndex] = result
                targetSuit = self.battle.activeSuits[result]
                targetSuit.setManager(1)
                targetSuit.setHP(1250)
                targetSuit.setMaxHP(1250)
                self.setSuitCondition(targetSuit.doId, 'shielding', 1, -1, 'setBoth')
                if self.suitHasCondition(targetSuit.doId, 'sued'):
                    self.setSuitCondition(targetSuit.doId, 'sued', 1, 1, 'setBoth')
                    self.setSuitCondition(targetSuit.doId, 'suemovie', 0, 0, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'suemovie', 0, 0, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'govException', 1, -1, 'setBoth')
                if not self.suitHasCondition(targetSuit.doId, 'dead'):
                    self.setSuitCondition(theSuit.doId, 'promotioncalculator', 0, 0, 'setBoth')
                    self.setSuitCondition(theSuit.doId, 'deadpromotion', 0, 0, 'setBoth')
                continue
            elif atkType['name'] == 'SafetyPromotion2':
                result = 50
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'banned3', 0, 0, 'setBoth')
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
                targetSuit.setHP(1250)
                targetSuit.setMaxHP(1250)
                self.setSuitCondition(targetSuit.doId, 'shielding', 1, -1, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'sued', 0, 0, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'suemovie', 0, 0, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'govException', 1, -1, 'setBoth')
                if not self.suitHasCondition(targetSuit.doId, 'dead'):
                    self.setSuitCondition(theSuit.doId, 'promotioncalculator', 0, 0, 'setBoth')
                    self.setSuitCondition(theSuit.doId, 'deadpromotion', 0, 0, 'setBoth')
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
                targetSuit.setHP(1250)
                targetSuit.setMaxHP(1250)
                self.setSuitCondition(targetSuit.doId, 'shielding', 1, -1, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'sued', 0, 0, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'suemovie', 0, 0, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'govException', 1, -1, 'setBoth')
                if not self.suitHasCondition(targetSuit.doId, 'dead'):
                    self.setSuitCondition(theSuit.doId, 'promotioncalculator', 0, 0, 'setBoth')
                    self.setSuitCondition(theSuit.doId, 'deadpromotion', 0, 0, 'setBoth')
                continue
            elif atkType['name'] == 'SafetyPromotion5':
                result = self.getSuitConditionModifier(theSuit.doId, 'targetCheckCondition')
                attack[SUIT_HP_COL][targetIndex] = result
                targetSuit = self.battle.activeSuits[result]
                self.setSuitCondition(theSuit.doId, 'target6', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target5', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target4', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target3', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target2', 0, 0, 'setBoth')
                targetSuit.setManager(1)
                targetSuit.setHP(1250)
                targetSuit.setMaxHP(1250)
                self.setSuitCondition(targetSuit.doId, 'shielding', 1, -1, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'sued', 0, 0, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'suemovie', 0, 0, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'govException', 1, -1, 'setBoth')
                if not self.suitHasCondition(targetSuit.doId, 'dead'):
                    self.setSuitCondition(theSuit.doId, 'promotioncalculator', 0, 0, 'setBoth')
                    self.setSuitCondition(theSuit.doId, 'deadpromotion', 0, 0, 'setBoth')
                continue
            elif atkType['name'] == 'SafetyViolation':
                result = 50
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'bannedGagUsed', 0, 0, 'setBoth')
            elif atkType['name'] == 'UnionBusterUnionDues':
                result = self.calculator.unionDues
                attack[SUIT_HP_COL][targetIndex] = result
                #self.setSuitCondition(theSuit.doId, 'unionduescalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'UnionBusterNoStrikeClause':
                result = 5
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'busted', 1, 4, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'unionbustercalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'UnionBusterUnionBusterDamage':
                for s in self.battle.suits:
                    self.setSuitCondition(s.doId, 'dotfinished', 1, 1, 'setBoth')
                result = 25
                attack[SUIT_HP_COL][targetIndex] = result
                if self.toonHasCondition(toonId, 'snapped'):
                    result *= self.getToonConditionModifier(toonId, 'snapped')
                if self.toonHasCondition(toonId, 'bombedToon'):
                    result *= self.getToonConditionModifier(toonId, 'bombedToon')
                if self.toonHasCondition(toonId, 'markedwood'):
                    result *= self.getToonConditionModifier(toonId, 'markedwood')
                # Going to slowly replace individual status effects so we acclimate to the new system before moving onto a more sophisticated means of this.
                for condition in self.toonStatusConditionsNew[toonId]:
                    if isinstance(condition, StatusEffects.Snapped):
                        result *= condition.defenseMod
            elif atkType['name'] == 'UnionBusterUnionCalculator':
                self.setSuitCondition(theSuit.doId, 'unionduescalculationcalculator', 0, 0, 'setBoth')
               # self.setSuitCondition(theSuit.doId, 'unionduescalculator', 1, 10, 'setBoth')
                result = self.costsCalculatorMultiplier
                toon.setHp(toon.hp + result)
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'UnionBusterContractEnforcement':
                result = 25
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'noGags', 1, 2, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'highpressurecalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'UnionBusterContractEnforcementHealing':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'contractenforcementcalculator', 0, 0, 'setBoth')
                for suit in self.battle.suits:
                    if suit.currHP <= 0:
                        continue
                    x = (suit.maxHP * suit.hardMaxHP) - suit.currHP
                    if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
                        suit.setHP(suit.currHP + 0)
                    elif suit.currHP + 275 > (suit.maxHP * suit.hardMaxHP):
                        suit.setHP(suit.currHP + x)
                    else:
                        suit.setHP(suit.currHP + 275)
                    continue
            elif atkType['name'] == 'UnionBusterContractEnforcement2':
                result = 25
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'bombedToon', 1, 3, 'setBoth')
                self.setToonCondition(toon.doId, 'markedforsanction', 1, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'hottakecalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'UnionBusterUnionBust':
                self.setSuitCondition(theSuit.doId, 'unionbustcalculator', 0, 0, 'setBoth')
                result = self.getSuitConditionModifier(theSuit.doId, 'targetCheckCondition')
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'targetCheckCondition', 0, 0, 'setBoth')
                targetSuit = self.battle.activeSuits[result]
                if not targetSuit.dna.name in SuitBattleGlobals.SpecialCogDict:
                    theSuit.setHP(theSuit.currHP + targetSuit.currHP)
                    buffPercent = ((targetSuit.currHP * 0.05) * 0.01)
                    theSuit.setDamageMultiplier(theSuit.getDamageMultiplier() * (1.0 + buffPercent))
                    targetSuit.setHP(targetSuit.currHP - targetSuit.currHP)
                    self.__removeLured(targetSuit.doId)
                    if self.suitHasCondition(targetSuit.doId, 'lured'):
                        self.setSuitCondition(targetSuit.doId, 'lured', 0, 0, 'setBoth')
            elif atkType['name'] == 'UnionBusterUnionBuster':
                result = 5
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'busted', 1, 4, 'setBoth')
                self.setToonCondition(toon.doId, 'unionBusterRecentlyTargeted', 1, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'unionbustercalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'TrafficGreenLight':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'greenLight', 1, 2, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'lightcalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'TrafficRedLight':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'redLight', 1, 2, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'lightcalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'TrafficRedLightRetaliation':
                self.setSuitCondition(theSuit.doId, 'redLight', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'greenLight', 0, 0, 'setBoth')
                if self.toonHasCondition(toonId, 'bookkeepingtoon'):
                    self.setToonCondition(toonId, 'bookkeepingtoon', 1, 1, 'setBoth')
                    if self.getToonConditionModifier(toonId, 'allGagBoost') < -50:
                        self.setToonCondition(toonId, 'allGagBoost',
                                              self.getToonConditionModifier(toonId, 'allGagBoost'), 2, 'setBoth')
                        self.setToonCondition(toonId, 'lureBoost',
                                              self.getToonConditionModifier(toonId, 'lureBoost'), 2, 'setBoth')
                    else:
                        self.setToonCondition(toonId, 'allGagBoost', -50, 2, 'setBoth')
                        self.setToonCondition(toonId, 'lureBoost', -50, 2, 'setBoth')
                    result = 30
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'TrafficGreenLightRetaliation':
                self.setSuitCondition(theSuit.doId, 'redLight', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'greenLight', 0, 0, 'setBoth')
                if not self.toonHasCondition(toonId, 'bookkeepingtoon'):
                    if self.getToonConditionModifier(toonId, 'allGagBoost') < -50:
                        self.setToonCondition(toonId, 'allGagBoost',
                                              self.getToonConditionModifier(toonId, 'allGagBoost'), 2, 'setBoth')
                        self.setToonCondition(toonId, 'lureBoost',
                                              self.getToonConditionModifier(toonId, 'lureBoost'), 2, 'setBoth')
                    else:
                        self.setToonCondition(toonId, 'allGagBoost', -50, 2, 'setBoth')
                        self.setToonCondition(toonId, 'lureBoost', -50, 2, 'setBoth')
                    result = 30
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'UnionBusterBreachOfContract':
                result = 25
                attack[SUIT_HP_COL][targetIndex] = result
                if self.getToonConditionModifier(toonId, 'allGagBoost2') < -50:
                    self.setToonCondition(toon.doId, 'allGagBoost2',
                                            self.getToonConditionModifier(toonId, 'allGagBoost2'), 3, 'setBoth')
                    self.setToonCondition(toon.doId, 'lureBoost2',
                                            self.getToonConditionModifier(toonId, 'lureBoost2'), 3, 'setBoth')
                else:
                    self.setToonCondition(toon.doId, 'allGagBoost2', -50, 3, 'setBoth')
                    self.setToonCondition(toon.doId, 'lureBoost2', -50, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'breachcalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'UnionBusterBreachOfContract2':
                if self.getToonConditionModifier(toonId, 'allGagBoost2') < -25:
                    self.setToonCondition(toon.doId, 'allGagBoost2',
                                            self.getToonConditionModifier(toonId, 'allGagBoost2'), 3, 'setBoth')
                    self.setToonCondition(toon.doId, 'lureBoost2',
                                            self.getToonConditionModifier(toonId, 'lureBoost2'), 3, 'setBoth')
                else:
                    self.setToonCondition(toon.doId, 'allGagBoost2', -25, 3, 'setBoth')
                    self.setToonCondition(toon.doId, 'lureBoost2', -25, 3, 'setBoth')
                result = 25
                attack[SUIT_HP_COL][targetIndex] = result
                result = 25
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'breachvulnerable2', 0, 0, 'setBoth')
            elif atkType['name'] == 'UnionBusterBreachOfContract3':
                if self.getToonConditionModifier(toonId, 'allGagBoost2') < -25:
                    self.setToonCondition(toon.doId, 'allGagBoost2',
                                            self.getToonConditionModifier(toonId, 'allGagBoost2'), 3, 'setBoth')
                    self.setToonCondition(toon.doId, 'lureBoost2',
                                            self.getToonConditionModifier(toonId, 'lureBoost2'), 3, 'setBoth')
                else:
                    self.setToonCondition(toon.doId, 'allGagBoost2', -25, 3, 'setBoth')
                    self.setToonCondition(toon.doId, 'lureBoost2', -25, 3, 'setBoth')
                result = 25
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
                    result = 25
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
                    result = 25
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'breachgagban', 0, 0, 'setBoth')
            elif atkType['name'] == 'TrafficCongestionPricing':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'disable4s', 1, 0, 'setBoth')
                    self.setToonCondition(t, 'disable5s', 1, 0, 'setBoth')
                    self.setToonCondition(t, 'disable6s', 1, 0, 'setBoth')
                    self.setToonCondition(t, 'disable7s', 1, 0, 'setBoth')
                    self.setToonCondition(t, 'disable8s', 1, 0, 'setBoth')
                    self.setToonCondition(t, random.choice(('disable4s', 'disable5s', 'disable6s', 'disable7s', 'disable8s')), 1, 3, 'setBoth')
            elif atkType['name'] == 'TrafficDetour':
                result = 25
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'confused', 1, 2, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'unionbustercalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'HustlerBaitAndSwitch':
                result = random.randint(1, 8)

                attack[SUIT_HP_COL][targetIndex] = result

                syncCond = 'contentSync%s' % result

                self.battle.nextContentSyncOrderCondition = syncCond

                for t in self.battle.activeToons:

                    for cond in self.calculator.CONTENT_SYNC_CONDITION_ORDERS.keys():
                        self.setToonCondition(t, cond, 0, 0, 'setBoth')

                    self.setToonCondition(t, syncCond, 1, -1, 'setBoth')
            elif atkType['name'] == 'HustlerExclusiveOffer':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'collectcalled', 1, 2, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'collectcalled', 1, 2, 'setBoth')
                self.setToonCondition(toon.doId, 'partnered', 1, 2, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'partnered', 1, 2, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'exclusiveCalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'HustlerExclusiveOfferRetaliation':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'collectcalled', 0, 0, 'setBoth')
                if self.toonHasCondition(toon.doId, 'collectcalled'):
                    self.setToonCondition(toon.doId, 'hidden', 1, 2, 'setBoth')
                    self.setToonCondition(toon.doId, 'noDamage', 1, 2, 'setBoth')
                    result = 50
                else:
                    result = 0
            elif atkType['name'] == 'HustlerLimitedTimeOfferDenied':
                doHurrySickness = 0
                for suit in self.battle.activeSuits:
                    rushJobConditions = [
                    'trapRushJob',
                    'lureRushJob',
                    'throwRushJob',
                    'squirtRushJob',
                    'zapRushJob',
                    'soundRushJob',
                    'dropRushJob',
                ]
                    if any(self.suitHasCondition(suit.doId, cond)
                        for cond in rushJobConditions) and suit.currHP > 0:
                        doHurrySickness = 1
                        if not suit.getManager():
                            if suit.currHP <= 0:
                                continue
                            x = (suit.maxHP * suit.hardMaxHP) - suit.currHP
                            if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
                                suit.setHP(suit.currHP + 0)
                            elif suit.currHP > (suit.maxHP * 2):
                                suit.setHP(suit.currHP + x)
                            else:
                                suit.setHP(suit.currHP + suit.maxHP)
                            continue
                        else:
                            if suit.currHP <= 0:
                                continue
                            x = (suit.maxHP * suit.hardMaxHP) - suit.currHP
                            if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
                                suit.setHP(suit.currHP + 0)
                            elif suit.currHP + 450 > (suit.maxHP * suit.hardMaxHP):
                                suit.setHP(suit.currHP + x)
                            else:
                                suit.setHP(suit.currHP + 450)
                if doHurrySickness:
                    #theSuit.setDamageMultiplier(theSuit.getDamageMultiplier() * 1.25)
                    result = 1
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for suit in self.battle.activeSuits:
                    self.setSuitCondition(suit.doId, 'alreadyHurrySickness', 1, 1, 'setBoth')
            elif atkType['name'] == 'HustlerLimitedTimeOfferApprove':
                doHurrySickness = 0
                for suit in self.battle.activeSuits:
                    rushJobConditions = [
                    'trapRushJob',
                    'lureRushJob',
                    'throwRushJob',
                    'squirtRushJob',
                    'zapRushJob',
                    'soundRushJob',
                    'dropRushJob',
                ]
                    if any(self.suitHasCondition(suit.doId, cond)
                        for cond in rushJobConditions) and suit.currHP > 0:
                        doHurrySickness = 1
                if doHurrySickness:
                    result = 0
                else:
                    result = 1
                    self.setToonCondition(toon.doId, 'governaughtBoost', (self.getToonConditionModifier(toonId, 'governaughtBoost') + 5), -1, 'setBoth')
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'HustlerClosingTime':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                theSuit.setDamageMultiplier(theSuit.getDamageMultiplier() * 1.05)
            elif atkType['name'] == 'HustlerCustomerRetention':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'contractenforcementcalculator', 0, 0, 'setBoth')
                for suit in self.battle.suits:
                    if suit.currHP <= 0:
                        continue
                    x = (suit.maxHP * suit.hardMaxHP) - suit.currHP
                    if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
                        suit.setHP(suit.currHP + 0)
                    elif suit.currHP + 275 > (suit.maxHP * suit.hardMaxHP):
                        suit.setHP(suit.currHP + x)
                    else:
                        suit.setHP(suit.currHP + 275)
                    continue
            elif atkType['name'] == 'HustlerSalesPitch':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'hustlerTarget', 1, 2, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'pitchCalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'UnionBusterUnionWages':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'unionwagescalculator', 1, 1, 'setBoth')
                theSuit.setDamageMultiplier(theSuit.getDamageMultiplier() * 1.05)
                theSuit.setHP(theSuit.currHP + 100)
                #self.setSuitCondition(theSuit.doId, 'unionduescalculationcalculator', 1, 10, 'setBoth')
               # self.setSuitCondition(theSuit.doId, 'unionduescalculator', 1, 10, 'setBoth')
            elif atkType['name'] == 'UnionBusterUnionWages2':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'unionwagescalculator', 1, 1, 'setBoth')
                theSuit.setDamageMultiplier(theSuit.getDamageMultiplier() * 1.1)
                theSuit.setHP(theSuit.currHP + 200)
               # self.setSuitCondition(theSuit.doId, 'unionduescalculationcalculator', 1, 10, 'setBoth')
            # self.setSuitCondition(theSuit.doId, 'unionduescalculator', 1, 10, 'setBoth')
            elif atkType['name'] == 'UnionBusterUnionWages3':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'unionwagescalculator', 1, 1, 'setBoth')
                theSuit.setDamageMultiplier(theSuit.getDamageMultiplier() * 1.15)
                theSuit.setHP(theSuit.currHP + 300)
               # self.setSuitCondition(theSuit.doId, 'unionduescalculationcalculator', 1, 10, 'setBoth')
            # self.setSuitCondition(theSuit.doId, 'unionduescalculator', 1, 10, 'setBoth')
            elif atkType['name'] == 'UnionBusterUnionWages4':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'unionwagescalculator', 1, 1, 'setBoth')
                theSuit.setDamageMultiplier(theSuit.getDamageMultiplier() * 1.2)
                theSuit.setHP(theSuit.currHP + 400)
                #self.setSuitCondition(theSuit.doId, 'unionduescalculationcalculator', 1, 10, 'setBoth')
            # self.setSuitCondition(theSuit.doId, 'unionduescalculator', 1, 10, 'setBoth')
            elif atkType['name'] == 'UnionBusterUnionWages5':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'unionwagescalculator', 1, 1, 'setBoth')
                theSuit.setDamageMultiplier(theSuit.getDamageMultiplier() * 1.25)
                theSuit.setHP(theSuit.currHP + 500)
               # self.setSuitCondition(theSuit.doId, 'unionduescalculationcalculator', 1, 10, 'setBoth')
            # self.setSuitCondition(theSuit.doId, 'unionduescalculator', 1, 10, 'setBoth')
            elif atkType['name'] == 'RacketeerProfiteering':
                result = self.getSuitConditionModifier(theSuit.doId, 'targetCheckCondition')
                attack[SUIT_HP_COL][targetIndex] = result
                targetSuit = self.battle.activeSuits[result]
                theSuit.setHP(math.ceil(theSuit.currHP + math.ceil(targetSuit.maxHP / 2)))
                targetSuit.setHP(math.ceil(targetSuit.currHP - math.ceil(targetSuit.maxHP / 2)))
                if targetSuit.currHP <= 0:
                    if self.suitHasCondition(targetSuit.doId, 'overpressure'):
                        for s in self.battle.activeSuits:
                            if s.dna.name == 'safesupervis':
                                if self.suitHasCondition(targetSuit.doId, 'overpressureDeath'):
                                    self.setSuitCondition(s.doId, 'overpressureDeath2', 1, 1, 'setBoth')
                                elif self.suitHasCondition(targetSuit.doId, 'overpressureDeath2'):
                                    self.setSuitCondition(s.doId, 'overpressureDeath3', 1, 1, 'setBoth')
                                else:
                                    self.setSuitCondition(s.doId, 'overpressureDeath', 1, 1, 'setBoth')
                    if targetSuit.getSkeleRevives() >= 1:
                        targetSuit.useSkeleRevive()
                    self.__removeLured(targetSuit.doId)
                    if not self.suitHasCondition(targetSuit.doId, 'dead'):
                        self.calculator.deadSuits += 1
                        self.setSuitCondition(targetSuit.doId, 'dead', 1, -1, 'setBoth')
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
                    if self.suitHasCondition(targetSuit.doId, 'overpressure'):
                        for s in self.battle.activeSuits:
                            if s.dna.name == 'safesupervis':
                                if self.suitHasCondition(targetSuit.doId, 'overpressureDeath'):
                                    self.setSuitCondition(s.doId, 'overpressureDeath2', 1, 1, 'setBoth')
                                elif self.suitHasCondition(targetSuit.doId, 'overpressureDeath2'):
                                    self.setSuitCondition(s.doId, 'overpressureDeath3', 1, 1, 'setBoth')
                                else:
                                    self.setSuitCondition(s.doId, 'overpressureDeath', 1, 1, 'setBoth')
                    if targetSuit.getSkeleRevives() >= 1:
                        targetSuit.useSkeleRevive()
                    self.__removeLured(targetSuit.doId)
                    if not self.suitHasCondition(targetSuit.doId, 'dead'):
                        self.calculator.deadSuits += 1
                        self.setSuitCondition(targetSuit.doId, 'dead', 1, -1, 'setBoth')
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
                    if self.suitHasCondition(targetSuit.doId, 'overpressure'):
                        for s in self.battle.activeSuits:
                            if s.dna.name == 'safesupervis':
                                if self.suitHasCondition(targetSuit.doId, 'overpressureDeath'):
                                    self.setSuitCondition(s.doId, 'overpressureDeath2', 1, 1, 'setBoth')
                                elif self.suitHasCondition(targetSuit.doId, 'overpressureDeath2'):
                                    self.setSuitCondition(s.doId, 'overpressureDeath3', 1, 1, 'setBoth')
                                else:
                                    self.setSuitCondition(s.doId, 'overpressureDeath', 1, 1, 'setBoth')
                    if targetSuit.getSkeleRevives() >= 1:
                        targetSuit.useSkeleRevive()
                    self.__removeLured(targetSuit.doId)
                    if not self.suitHasCondition(targetSuit.doId, 'dead'):
                        self.calculator.deadSuits += 1
                        self.setSuitCondition(targetSuit.doId, 'dead', 1, -1, 'setBoth')
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
                    if self.suitHasCondition(targetSuit.doId, 'overpressure'):
                        for s in self.battle.activeSuits:
                            if s.dna.name == 'safesupervis':
                                if self.suitHasCondition(targetSuit.doId, 'overpressureDeath'):
                                    self.setSuitCondition(s.doId, 'overpressureDeath2', 1, 1, 'setBoth')
                                elif self.suitHasCondition(targetSuit.doId, 'overpressureDeath2'):
                                    self.setSuitCondition(s.doId, 'overpressureDeath3', 1, 1, 'setBoth')
                                else:
                                    self.setSuitCondition(s.doId, 'overpressureDeath', 1, 1, 'setBoth')
                    if targetSuit.getSkeleRevives() >= 1:
                        targetSuit.useSkeleRevive()
                    self.__removeLured(targetSuit.doId)
                    if not self.suitHasCondition(targetSuit.doId, 'dead'):
                        self.calculator.deadSuits += 1
                        self.setSuitCondition(targetSuit.doId, 'dead', 1, -1, 'setBoth')
            elif atkType['name'] == 'RacketeerProfiteering5':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                targetSuit = self.battle.activeSuits[5]
                self.setSuitCondition(theSuit.doId, 'target6', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target5', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target4', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target3', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target2', 0, 0, 'setBoth')
                theSuit.setHP(math.ceil(theSuit.currHP + (targetSuit.maxHP / 2)))
                targetSuit.setHP(math.ceil(targetSuit.currHP - (targetSuit.maxHP / 2)))
                if targetSuit.currHP <= 0:
                    if self.suitHasCondition(targetSuit.doId, 'overpressure'):
                        for s in self.battle.activeSuits:
                            if s.dna.name == 'safesupervis':
                                if self.suitHasCondition(targetSuit.doId, 'overpressureDeath'):
                                    self.setSuitCondition(s.doId, 'overpressureDeath2', 1, 1, 'setBoth')
                                elif self.suitHasCondition(targetSuit.doId, 'overpressureDeath2'):
                                    self.setSuitCondition(s.doId, 'overpressureDeath3', 1, 1, 'setBoth')
                                else:
                                    self.setSuitCondition(s.doId, 'overpressureDeath', 1, 1, 'setBoth')
                    if targetSuit.getSkeleRevives() >= 1:
                        targetSuit.useSkeleRevive()
                    self.__removeLured(targetSuit.doId)
                    if not self.suitHasCondition(targetSuit.doId, 'dead'):
                        self.calculator.deadSuits += 1
                        self.setSuitCondition(targetSuit.doId, 'dead', 1, -1, 'setBoth')
            elif atkType['name'] == 'RacketeerExtortion':
                result = random.randint(20, 35)
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'extortioncalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'RacketeerOverextendedLeverage':
                liveSuits = 0

                for s in self.battle.activeSuits:
                    if s.getHP() > 0 and not self.suitHasCondition(s.doId, 'dead'):
                        liveSuits += 1

                self.calculator.racketeerMultiplier += liveSuits
                result = self.calculator.racketeerMultiplier
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'RacketeerOverextendedLeverage2':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'vulnerablevideographer', self.getSuitConditionModifier(theSuit.doId, 'vulnerablevideographer') * 1.1, -1, 'setBoth')
            elif atkType['name'] == 'RacketeerExtortion2':
                result = self.calculator.costsMultiplier
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'RacketeerCompensation':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for suit in self.battle.activeSuits:
                    if suit.getHP() < suit.maxHP and suit.dna.name != 'racket':
                        suit.setDamageMultiplier(suit.getDamageMultiplier() * 1.05)
                        self.setSuitCondition(suit.doId, 'lureResist', 1, -1, 'setBoth')
            elif atkType['name'] == 'RacketeerHustling':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                if len(self.battle.activeSuits) > 1:
                    targetSuit = self.battle.activeSuits[1]
                    if targetSuit.getHP() > 0 and not targetSuit.getHP() > targetSuit.maxHP and not targetSuit.getManager() and not theSuit.dna.name == 'videog' and not self.suitHasCondition(
                            targetSuit.doId, 'overpressure') and targetSuit.getSkeleRevives() == 0:
                        self.setSuitCondition(theSuit.doId, 'target2', 1, 10, 'setBoth')
                    else:
                        if len(self.battle.activeSuits) > 2:
                            targetSuit = self.battle.activeSuits[2]
                            if targetSuit.getHP() > 0 and not targetSuit.getHP() > targetSuit.maxHP and not targetSuit.getManager() and not self.suitHasCondition(targetSuit.doId,
                                                                                                                                                                  'overpressure') and targetSuit.getSkeleRevives() == 0:
                                self.setSuitCondition(theSuit.doId, 'target3', 1, 10, 'setBoth')
                            else:
                                if len(self.battle.activeSuits) > 3:
                                    targetSuit = self.battle.activeSuits[3]
                                    if targetSuit.getHP() > 0 and not targetSuit.getHP() > targetSuit.maxHP and not targetSuit.getManager() and not self.suitHasCondition(targetSuit.doId,
                                                                                                                                                                          'overpressure') and targetSuit.getSkeleRevives() == 0:
                                        self.setSuitCondition(theSuit.doId, 'target4', 1, 10, 'setBoth')
                                    else:
                                        if len(self.battle.activeSuits) > 4:
                                            targetSuit = self.battle.activeSuits[4]
                                            if targetSuit.getHP() > 0 and not targetSuit.getHP() > targetSuit.maxHP and not targetSuit.getManager() and not self.suitHasCondition(targetSuit.doId,
                                                                                                                                                                                  'overpressure') and targetSuit.getSkeleRevives() == 0:
                                                self.setSuitCondition(theSuit.doId, 'target5', 1, 10, 'setBoth')
                                            else:
                                                if len(self.battle.activeSuits) > 5:
                                                    targetSuit = self.battle.activeSuits[5]
                                                    if targetSuit.getHP() > 0 and not targetSuit.getHP() > targetSuit.maxHP and not targetSuit.getManager() and not self.suitHasCondition(
                                                            targetSuit.doId, 'overpressure') and targetSuit.getSkeleRevives() == 0:
                                                        self.setSuitCondition(theSuit.doId, 'target6', 1, 10, 'setBoth')
                                                    else:
                                                        pass
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
                # if self.toonHasCondition(toon.doId, 'usedDrop'):
                #     self.setToonCondition(toon.doId, 'disableDrop', 1, 2, 'setBoth')
                #     self.setToonCondition(toon.doId, 'usedDrop', 1, 1, 'setBoth')
                # if self.toonHasCondition(toon.doId, 'usedThrow'):
                #     self.setToonCondition(toon.doId, 'disableThrow', 1, 2, 'setBoth')
                #     self.setToonCondition(toon.doId, 'usedThrow', 1, 1, 'setBoth')
                # if self.toonHasCondition(toon.doId, 'usedSquirt'):
                #     self.setToonCondition(toon.doId, 'disableSquirt', 1, 2, 'setBoth')
                #     self.setToonCondition(toon.doId, 'usedSquirt', 1, 1, 'setBoth')
                # if self.toonHasCondition(toon.doId, 'usedSound'):
                #     self.setToonCondition(toon.doId, 'disableSound', 1, 2, 'setBoth')
                #     self.setToonCondition(toon.doId, 'usedSound', 1, 1, 'setBoth')
                # if self.toonHasCondition(toon.doId, 'usedTrap'):
                #     self.setToonCondition(toon.doId, 'disableTrap', 1, 2, 'setBoth')__getRandomValidTargetSuitDigit
                #     self.setToonCondition(toon.doId, 'usedTrap', 1, 1, 'setBoth')
                # if self.toonHasCondition(toon.doId, 'usedLure'):
                #     self.setToonCondition(toon.doId, 'disableLure', 1, 2, 'setBoth')
                #     self.setToonCondition(toon.doId, 'usedLure', 1, 1, 'setBoth')
                # if self.toonHasCondition(toon.doId, 'usedHeal'):
                #     self.setToonCondition(toon.doId, 'disableToonUp', 1, 2, 'setBoth')
                #     self.setToonCondition(toon.doId, 'usedHeal', 1, 1, 'setBoth')
                # if self.toonHasCondition(toon.doId, 'usedZap'):
                #     self.setToonCondition(toon.doId, 'disableZap', 1, 2, 'setBoth')
                #     self.setToonCondition(toon.doId, 'usedZap', 1, 1, 'setBoth')
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'RacketeerPeckingOrderRetaliation':
                if self.toonHasCondition(toon.doId, 'banned'):
                    result = 40
                elif self.toonHasCondition(toon.doId, 'banned2'):
                    result = 40
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'RacketeerPeckingOrderRetaliationSoak':
                result = 25
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'dodgy', -100, 3, 'setBoth')
            elif atkType['name'] == 'SafetySoakRetaliation':
                if self.toonHasCondition(toon.doId, 'soakToon') and not self.toonHasCondition(toon.doId, 'hidden'):
                    result = 33
                    attack[SUIT_HP_COL][targetIndex] = result
                    self.setToonCondition(toon.doId, 'soakToon', 1, 1, 'setBoth')
                    self.setSuitCondition(theSuit.doId, 'soakedcalculator', 0, 0, 'setBoth')
                    self.setSuitCondition(theSuit.doId, 'soakedcalculator2', 1, 10, 'setBoth')
                    self.setToonCondition(toon.doId, 'dodgy', -100, 3, 'setBoth')
                else:
                    result = 0
                    attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'RadiographerRadioInfrequency':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'groupDamageDown', -50, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'radioinfrequencycalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'dancesession', 0, 0, 'setBoth')
            elif atkType['name'] == 'RadiographerHotTake':
                result = 25
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'bombedToon', 1, 3, 'setBoth')
                self.setToonCondition(toon.doId, 'hotTakeRecentlyTargeted', 1, 2, 'setBoth')
                self.setToonCondition(toon.doId, 'markedforsanction', 1, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'hottakecalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'RadiographerHotTakeDamage':
                if self.toonHasCondition(toon.doId, 'bombedToonDamage'):
                    self.setToonCondition(toon.doId, 'markedforsanction', 1, 3, 'setBoth')
                    self.setToonCondition(toon.doId, 'bombedToonDamage', 0, 0, 'setBoth')
                    self.setToonCondition(toon.doId, 'bombedToon', 0, 0, 'setBoth')
                    if self.getToonConditionModifier(toonId, 'snapped') > 1.75:
                        self.setToonCondition(toon.doId, 'snapped', self.getToonConditionModifier(toonId, 'snapped'), 2, 'setBoth')
                    else:
                        self.setToonCondition(toon.doId, 'snapped', 1.75, 2, 'setBoth')
                    if self.getToonConditionModifier(toonId, 'raisedAnte') > 75:
                        self.setToonCondition(toon.doId, 'raisedAnte',
                                              self.getToonConditionModifier(toonId, 'raisedAnte'), 2, 'setBoth')
                        self.setToonCondition(toon.doId, 'lureBoost',
                                              self.getToonConditionModifier(toonId, 'lureBoost'), 2, 'setBoth')
                    else:
                        self.setToonCondition(toon.doId, 'raisedAnte', 75, 2, 'setBoth')
                        self.setToonCondition(toon.doId, 'lureBoost', 75, 2, 'setBoth')
                    result = 15
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'RadiographerHotTakeRetaliation':
                result = 25
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'noGags', 1, 2, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'unionbustercalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'RadiographerDanceSession':
                result = 0
                self.setSuitCondition(theSuit.doId, 'targetCheckCondition', self.__getRandomValidTargetSuitDigitRadiographer(excludeSuitId=theSuit.doId), 1, 'setBoth')
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'RadiographerOvermodulated':
                result = self.getSuitConditionModifier(theSuit.doId, 'targetCheckCondition')
                attack[SUIT_HP_COL][targetIndex] = result
                targetSuit = self.battle.activeSuits[result]
                self.setSuitCondition(theSuit.doId, 'targetCheckCondition', -1, 0, 'setBoth')
               # self.setSuitCondition(targetSuit.doId, 'bellowattack', 1, 1, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'lured', 0, 0, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'unlureSuit', 0, 0, 'setBoth')
                if self.suitHasCondition(targetSuit.doId, 'sued'):
                    self.setSuitCondition(targetSuit.doId, 'sued', 1, 1, 'setBoth')
                if not self.suitHasCondition(targetSuit.doId, 'dead'):
                    self.setSuitCondition(theSuit.doId, 'overmodulatedcalculator', 0, 0, 'setBoth')

                found = False
                if targetSuit.doId not in self.suitStatusConditionsNew:
                    self.suitStatusConditionsNew[targetSuit.doId] = []

                for condIndex in range(len(self.suitStatusConditionsNew[targetSuit.doId])):
                    condition = self.suitStatusConditionsNew[targetSuit.doId][condIndex]
                    if isinstance(condition, StatusEffects.ExtraAttacks):
                        condition.extraAttacks += 1
                        found = True
                        break

                if not found:
                    self.suitStatusConditionsNew[targetSuit.doId].append(StatusEffects.ExtraAttacks(1))
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
                #self.setSuitCondition(targetSuit.doId, 'bellowattack', 1, 1, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'lured', 0, 0, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'unlureSuit', 0, 0, 'setBoth')
                if self.suitHasCondition(targetSuit.doId, 'sued'):
                    self.setSuitCondition(targetSuit.doId, 'sued', 1, 1, 'setBoth')
                if not self.suitHasCondition(targetSuit.doId, 'dead'):
                    self.setSuitCondition(theSuit.doId, 'overmodulatedcalculator', 0, 0, 'setBoth')
                # if not self.suitHasCondition(targetSuit.doId, 'extraAttack'):
                #     self.setSuitCondition(targetSuit.doId, 'extraAttack', 1, -1, 'setBoth')
                # elif self.suitHasCondition(targetSuit.doId, 'extraAttack') and not self.suitHasCondition(
                #         targetSuit.doId, 'extraAttack2'):
                #     self.setSuitCondition(targetSuit.doId, 'extraAttack2', 1, -1, 'setBoth')
                # elif self.suitHasCondition(targetSuit.doId, 'extraAttack2') and not self.suitHasCondition(
                #         targetSuit.doId, 'extraAttack3'):
                #     self.setSuitCondition(targetSuit.doId, 'extraAttack3', 1, -1, 'setBoth')
                # elif self.suitHasCondition(targetSuit.doId, 'extraAttack3') and not self.suitHasCondition(
                #         targetSuit.doId, 'extraAttack4'):
                #     self.setSuitCondition(targetSuit.doId, 'extraAttack4', 1, -1, 'setBoth')
                # elif self.suitHasCondition(targetSuit.doId, 'extraAttack4') and not self.suitHasCondition(
                #         targetSuit.doId, 'extraAttack5'):
                #     self.setSuitCondition(targetSuit.doId, 'extraAttack5', 1, -1, 'setBoth')
                # elif self.suitHasCondition(targetSuit.doId, 'extraAttack5') and not self.suitHasCondition(
                #         targetSuit.doId, 'extraAttack6'):
                #     self.setSuitCondition(targetSuit.doId, 'extraAttack6', 1, -1, 'setBoth')
                # elif self.suitHasCondition(targetSuit.doId, 'extraAttack6') and not self.suitHasCondition(
                #         targetSuit.doId, 'extraAttack7'):
                #     self.setSuitCondition(targetSuit.doId, 'extraAttack7', 1, -1, 'setBoth')
                # elif self.suitHasCondition(targetSuit.doId, 'extraAttack7') and not self.suitHasCondition(
                #         targetSuit.doId, 'extraAttack8'):
                #     self.setSuitCondition(targetSuit.doId, 'extraAttack8', 1, -1, 'setBoth')
                # elif self.suitHasCondition(targetSuit.doId, 'extraAttack8') and not self.suitHasCondition(
                #         targetSuit.doId, 'extraAttack9'):
                #     self.setSuitCondition(targetSuit.doId, 'extraAttack9', 1, -1, 'setBoth')
                # elif self.suitHasCondition(targetSuit.doId, 'extraAttack9') and not self.suitHasCondition(
                #         targetSuit.doId, 'extraAttack10'):
                #     self.setSuitCondition(targetSuit.doId, 'extraAttack10', 1, -1, 'setBoth')

                # Check to see if the target Cog already has extra attacks.
                for i in range(len(self.suitStatusConditionsNew[targetSuit.doId])):
                    if isinstance(self.suitStatusConditionsNew[targetSuit.doId][i], StatusEffects.ExtraAttacks): # Does this Cog have any extra attacks?
                        self.suitStatusConditionsNew[targetSuit.doId][i].extraAttacks += 1 # Add one more attack.
                        break # Stop the loop so that we do not go down to else.

                # The Cog does not have any extra attacks, so give them one.
                else:
                    self.suitStatusConditionsNew[targetSuit.doId].append(StatusEffects.ExtraAttacks(1))
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
                self.setSuitCondition(targetSuit.doId, 'lured', 0, 0, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'unlureSuit', 0, 0, 'setBoth')
                #self.setSuitCondition(targetSuit.doId, 'bellowattack', 1, 1, 'setBoth')
                if self.suitHasCondition(targetSuit.doId, 'sued'):
                    self.setSuitCondition(targetSuit.doId, 'sued', 1, 1, 'setBoth')
                if not self.suitHasCondition(targetSuit.doId, 'dead'):
                    self.setSuitCondition(theSuit.doId, 'overmodulatedcalculator', 0, 0, 'setBoth')
                # if not self.suitHasCondition(targetSuit.doId, 'extraAttack'):
                #     self.setSuitCondition(targetSuit.doId, 'extraAttack', 1, -1, 'setBoth')
                # elif self.suitHasCondition(targetSuit.doId, 'extraAttack') and not self.suitHasCondition(
                #         targetSuit.doId, 'extraAttack2'):
                #     self.setSuitCondition(targetSuit.doId, 'extraAttack2', 1, -1, 'setBoth')
                # elif self.suitHasCondition(targetSuit.doId, 'extraAttack2') and not self.suitHasCondition(
                #         targetSuit.doId, 'extraAttack3'):
                #     self.setSuitCondition(targetSuit.doId, 'extraAttack3', 1, -1, 'setBoth')
                # elif self.suitHasCondition(targetSuit.doId, 'extraAttack3') and not self.suitHasCondition(
                #         targetSuit.doId, 'extraAttack4'):
                #     self.setSuitCondition(targetSuit.doId, 'extraAttack4', 1, -1, 'setBoth')
                # elif self.suitHasCondition(targetSuit.doId, 'extraAttack4') and not self.suitHasCondition(
                #         targetSuit.doId, 'extraAttack5'):
                #     self.setSuitCondition(targetSuit.doId, 'extraAttack5', 1, -1, 'setBoth')
                # elif self.suitHasCondition(targetSuit.doId, 'extraAttack5') and not self.suitHasCondition(
                #         targetSuit.doId, 'extraAttack6'):
                #     self.setSuitCondition(targetSuit.doId, 'extraAttack6', 1, -1, 'setBoth')
                # elif self.suitHasCondition(targetSuit.doId, 'extraAttack6') and not self.suitHasCondition(
                #         targetSuit.doId, 'extraAttack7'):
                #     self.setSuitCondition(targetSuit.doId, 'extraAttack7', 1, -1, 'setBoth')
                # elif self.suitHasCondition(targetSuit.doId, 'extraAttack7') and not self.suitHasCondition(
                #         targetSuit.doId, 'extraAttack8'):
                #     self.setSuitCondition(targetSuit.doId, 'extraAttack8', 1, -1, 'setBoth')
                # elif self.suitHasCondition(targetSuit.doId, 'extraAttack8') and not self.suitHasCondition(
                #         targetSuit.doId, 'extraAttack9'):
                #     self.setSuitCondition(targetSuit.doId, 'extraAttack9', 1, -1, 'setBoth')
                # elif self.suitHasCondition(targetSuit.doId, 'extraAttack9') and not self.suitHasCondition(
                #         targetSuit.doId, 'extraAttack10'):
                #     self.setSuitCondition(targetSuit.doId, 'extraAttack10', 1, -1, 'setBoth')

                # Check to see if the target Cog already has extra attacks.
                for i in range(len(self.suitStatusConditionsNew[targetSuit.doId])):
                    if isinstance(self.suitStatusConditionsNew[targetSuit.doId][i], StatusEffects.ExtraAttacks): # Does this Cog have any extra attacks?
                        self.suitStatusConditionsNew[targetSuit.doId][i].extraAttacks += 1 # Add one more attack.
                        break # Stop the loop so that we do not go down to else.

                # The Cog does not have any extra attacks, so give them one.
                else:
                    self.suitStatusConditionsNew[targetSuit.doId].append(StatusEffects.ExtraAttacks(1))
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
                self.setSuitCondition(targetSuit.doId, 'lured', 0, 0, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'unlureSuit', 0, 0, 'setBoth')
               # self.setSuitCondition(targetSuit.doId, 'bellowattack', 1, 1, 'setBoth')
                if self.suitHasCondition(targetSuit.doId, 'sued'):
                    self.setSuitCondition(targetSuit.doId, 'sued', 1, 1, 'setBoth')
                if not self.suitHasCondition(targetSuit.doId, 'dead'):
                    self.setSuitCondition(theSuit.doId, 'overmodulatedcalculator', 0, 0, 'setBoth')
                # if not self.suitHasCondition(targetSuit.doId, 'extraAttack'):
                #     self.setSuitCondition(targetSuit.doId, 'extraAttack', 1, -1, 'setBoth')
                # elif self.suitHasCondition(targetSuit.doId, 'extraAttack') and not self.suitHasCondition(
                #         targetSuit.doId, 'extraAttack2'):
                #     self.setSuitCondition(targetSuit.doId, 'extraAttack2', 1, -1, 'setBoth')
                # elif self.suitHasCondition(targetSuit.doId, 'extraAttack2') and not self.suitHasCondition(
                #         targetSuit.doId, 'extraAttack3'):
                #     self.setSuitCondition(targetSuit.doId, 'extraAttack3', 1, -1, 'setBoth')
                # elif self.suitHasCondition(targetSuit.doId, 'extraAttack3') and not self.suitHasCondition(
                #         targetSuit.doId, 'extraAttack4'):
                #     self.setSuitCondition(targetSuit.doId, 'extraAttack4', 1, -1, 'setBoth')
                # elif self.suitHasCondition(targetSuit.doId, 'extraAttack4') and not self.suitHasCondition(
                #         targetSuit.doId, 'extraAttack5'):
                #     self.setSuitCondition(targetSuit.doId, 'extraAttack5', 1, -1, 'setBoth')
                # elif self.suitHasCondition(targetSuit.doId, 'extraAttack5') and not self.suitHasCondition(
                #         targetSuit.doId, 'extraAttack6'):
                #     self.setSuitCondition(targetSuit.doId, 'extraAttack6', 1, -1, 'setBoth')
                # elif self.suitHasCondition(targetSuit.doId, 'extraAttack6') and not self.suitHasCondition(
                #         targetSuit.doId, 'extraAttack7'):
                #     self.setSuitCondition(targetSuit.doId, 'extraAttack7', 1, -1, 'setBoth')
                # elif self.suitHasCondition(targetSuit.doId, 'extraAttack7') and not self.suitHasCondition(
                #         targetSuit.doId, 'extraAttack8'):
                #     self.setSuitCondition(targetSuit.doId, 'extraAttack8', 1, -1, 'setBoth')
                # elif self.suitHasCondition(targetSuit.doId, 'extraAttack8') and not self.suitHasCondition(
                #         targetSuit.doId, 'extraAttack9'):
                #     self.setSuitCondition(targetSuit.doId, 'extraAttack9', 1, -1, 'setBoth')
                # elif self.suitHasCondition(targetSuit.doId, 'extraAttack9') and not self.suitHasCondition(
                #         targetSuit.doId, 'extraAttack10'):
                #     self.setSuitCondition(targetSuit.doId, 'extraAttack10', 1, -1, 'setBoth')
                
                # Check to see if the target Cog already has extra attacks.
                for i in range(len(self.suitStatusConditionsNew[targetSuit.doId])):
                    if isinstance(self.suitStatusConditionsNew[targetSuit.doId][i], StatusEffects.ExtraAttacks): # Does this Cog have any extra attacks?
                        self.suitStatusConditionsNew[targetSuit.doId][i].extraAttacks += 1 # Add one more attack.
                        break # Stop the loop so that we do not go down to else.

                # The Cog does not have any extra attacks, so give them one.
                else:
                    self.suitStatusConditionsNew[targetSuit.doId].append(StatusEffects.ExtraAttacks(1))
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
                self.setSuitCondition(targetSuit.doId, 'lured', 0, 0, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'unlureSuit', 0, 0, 'setBoth')
                #self.setSuitCondition(targetSuit.doId, 'bellowattack', 1, 1, 'setBoth')
                if self.suitHasCondition(targetSuit.doId, 'sued'):
                    self.setSuitCondition(targetSuit.doId, 'sued', 1, 1, 'setBoth')
                if not self.suitHasCondition(targetSuit.doId, 'dead'):
                    self.setSuitCondition(theSuit.doId, 'overmodulatedcalculator', 0, 0, 'setBoth')
                # if not self.suitHasCondition(targetSuit.doId, 'extraAttack'):
                #     self.setSuitCondition(targetSuit.doId, 'extraAttack', 1, -1, 'setBoth')
                # elif self.suitHasCondition(targetSuit.doId, 'extraAttack') and not self.suitHasCondition(
                #         targetSuit.doId, 'extraAttack2'):
                #     self.setSuitCondition(targetSuit.doId, 'extraAttack2', 1, -1, 'setBoth')
                # elif self.suitHasCondition(targetSuit.doId, 'extraAttack2') and not self.suitHasCondition(
                #         targetSuit.doId, 'extraAttack3'):
                #     self.setSuitCondition(targetSuit.doId, 'extraAttack3', 1, -1, 'setBoth')
                # elif self.suitHasCondition(targetSuit.doId, 'extraAttack3') and not self.suitHasCondition(
                #         targetSuit.doId, 'extraAttack4'):
                #     self.setSuitCondition(targetSuit.doId, 'extraAttack4', 1, -1, 'setBoth')
                # elif self.suitHasCondition(targetSuit.doId, 'extraAttack4') and not self.suitHasCondition(
                #         targetSuit.doId, 'extraAttack5'):
                #     self.setSuitCondition(targetSuit.doId, 'extraAttack5', 1, -1, 'setBoth')
                # elif self.suitHasCondition(targetSuit.doId, 'extraAttack5') and not self.suitHasCondition(
                #         targetSuit.doId, 'extraAttack6'):
                #     self.setSuitCondition(targetSuit.doId, 'extraAttack6', 1, -1, 'setBoth')
                # elif self.suitHasCondition(targetSuit.doId, 'extraAttack6') and not self.suitHasCondition(
                #         targetSuit.doId, 'extraAttack7'):
                #     self.setSuitCondition(targetSuit.doId, 'extraAttack7', 1, -1, 'setBoth')
                # elif self.suitHasCondition(targetSuit.doId, 'extraAttack7') and not self.suitHasCondition(
                #         targetSuit.doId, 'extraAttack8'):
                #     self.setSuitCondition(targetSuit.doId, 'extraAttack8', 1, -1, 'setBoth')
                # elif self.suitHasCondition(targetSuit.doId, 'extraAttack8') and not self.suitHasCondition(
                #         targetSuit.doId, 'extraAttack9'):
                #     self.setSuitCondition(targetSuit.doId, 'extraAttack9', 1, -1, 'setBoth')
                # elif self.suitHasCondition(targetSuit.doId, 'extraAttack9') and not self.suitHasCondition(
                #         targetSuit.doId, 'extraAttack10'):
                #     self.setSuitCondition(targetSuit.doId, 'extraAttack10', 1, -1, 'setBoth')

                # Check to see if the target Cog already has extra attacks.
                for i in range(len(self.suitStatusConditionsNew[targetSuit.doId])):
                    if isinstance(self.suitStatusConditionsNew[targetSuit.doId][i], StatusEffects.ExtraAttacks): # Does this Cog have any extra attacks?
                        self.suitStatusConditionsNew[targetSuit.doId][i].extraAttacks += 1 # Add one more attack.
                        break # Stop the loop so that we do not go down to else.

                # The Cog does not have any extra attacks, so give them one.
                else:
                    self.suitStatusConditionsNew[targetSuit.doId].append(StatusEffects.ExtraAttacks(1))
                self.__removeLured(targetSuit.doId)
            elif atkType['name'] == 'RecordkeeperPaperTrail': # Recordkeeper
                self.setSuitCondition(theSuit.doId, 'papertrailcalculator', 0, 0, 'setBoth')
                result = 25
                attack[SUIT_HP_COL][targetIndex] = result
                if self.getToonConditionModifier(toonId, 'allGagBoost') < -50:
                    self.setToonCondition(toon.doId, 'allGagBoost',
                                            self.getToonConditionModifier(toonId, 'allGagBoost'), 3, 'setBoth')
                    self.setToonCondition(toon.doId, 'lureBoost',
                                            self.getToonConditionModifier(toonId, 'lureBoost'), 3, 'setBoth')
                else:
                    self.setToonCondition(toon.doId, 'allGagBoost', -50, 3, 'setBoth')
                    self.setToonCondition(toon.doId, 'lureBoost', -50, 3, 'setBoth')
            elif atkType['name'] == 'RecordkeeperMinutesTaken':
                self.recordkeeperCalculatorMultiplier += 2
                self.recordkeeperMultiplier += 2
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'RecordkeeperMinutesTakenContingency':
                self.recordkeeperCalculatorMultiplier += 20
                self.recordkeeperMultiplier += 20
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'RecordkeeperPhantomEntrySpawn':
                self.setSuitCondition(theSuit.doId, 'directorDamageReduction', .5, -1, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'phantomEntrycalculator', 0, 0, 'setBoth')
                # for suit in self.battle.activeSuits:
                #     if not self.TurnsElapsed == 0:
                #         self.setSuitCondition(suit.doId, 'alreadyCogSpawn', 1, 1, 'setBoth')
                if not self.suitHasCondition(theSuit.doId, 'phase3'):
                    self.setSuitCondition(theSuit.doId, 'phase3', 1, -1, 'setBoth')
                    self.setToonCondition(toon.doId, 'phantomDeath', 1, -1, 'setBoth')
                from toontown.suit.DistributedBoardbotBossAI import DistributedBoardbotBossAI

                boss = None
                for do in simbase.air.doId2do.values():
                    if isinstance(do, DistributedBoardbotBossAI):
                        for t in self.battle.activeToons:
                            if t in do.involvedToons:
                                boss = do
                                break
                        for s in self.battle.activeSuits:
                                if s in do.activeSuits:
                                    if s.dna.name == 'rkeeper':
                                        boss.appendSuitsToBattle(boss.battleNumber, 'phantom')
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'RecordkeeperPhantomEntryDamage':
                self.setSuitCondition(theSuit.doId, 'directorDamageReduction', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'phantomDeath', 0, 0, 'setBoth')
                theSuit.setHP(theSuit.currHP - 3000)
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                if (theSuit.currHP) <= 0:
                    if theSuit.getSkeleRevives() >= 1:
                        theSuit.useSkeleRevive()
                    self.__removeLured(theSuit)
                    if not self.suitHasCondition(theSuit.doId, 'dead'):
                        self.calculator.deadSuits += 1
                        self.setSuitCondition(theSuit.doId, 'dead', 1, -1, 'setBoth')
            elif atkType['name'] == 'RecordkeeperPhantomEntrySacrifice':
                self.setSuitCondition(theSuit.doId, 'directorDamageReduction', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'phantomDeath', 0, 0, 'setBoth')
                for suit in self.battle.activeSuits:
                    if suit.dna.name == 'rkeeper':
                        if suit.currHP <= 0:
                            continue
                        suit.setHP(suit.currHP + theSuit.currHP)
                        self.setSuitCondition(suit.doId, 'directorDamageReduction', 0, 0, 'setBoth')
                theSuit.setHP(0)
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'RecordkeeperMinutesTakenDamage':
                self.setSuitCondition(theSuit.doId, 'costscalculator', 0, 0, 'setBoth')
                result = self.recordkeeperMultiplier
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'RecordkeeperRevisedFilingLiquidation':
                self.setSuitCondition(theSuit.doId, 'liquidationRetaliation', 0, 0, 'setBoth')
                result = 25
                attack[SUIT_HP_COL][targetIndex] = result
                if self.getToonConditionModifier(toonId, 'allGagBoost') < -25:
                    self.setToonCondition(toon.doId, 'allGagBoost',
                                            self.getToonConditionModifier(toonId, 'allGagBoost'), 2, 'setBoth')
                    self.setToonCondition(toon.doId, 'lureBoost',
                                            self.getToonConditionModifier(toonId, 'lureBoost'), 2, 'setBoth')
                else:
                    self.setToonCondition(toon.doId, 'allGagBoost', -25, 2, 'setBoth')
                    self.setToonCondition(toon.doId, 'lureBoost', -25, 2, 'setBoth')
            elif atkType['name'] == 'RecordkeeperRevisedFiling':
                self.setSuitCondition(theSuit.doId, 'revisedcalculator', 0, 0, 'setBoth')
                result = 20
                attack[SUIT_HP_COL][targetIndex] = result
                if self.getToonConditionModifier(toonId, 'snapped') > 1.5:
                    self.setToonCondition(toon.doId, 'snapped', self.getToonConditionModifier(toonId, 'snapped'), 3, 'setBoth')
                else:
                    self.setToonCondition(toon.doId, 'snapped', 1.5, 3, 'setBoth')
                if self.getToonConditionModifier(toonId, 'allGagBoost2') > 50:
                    self.setToonCondition(toon.doId, 'allGagBoost2', self.getToonConditionModifier(toonId, 'allGagBoost2'), 3, 'setBoth')
                    self.setToonCondition(toon.doId, 'lureBoost2', self.getToonConditionModifier(toonId, 'lureBoost2'), 3, 'setBoth')
                else:
                    self.setToonCondition(toon.doId, 'allGagBoost2', 50, 3, 'setBoth')
                    self.setToonCondition(toon.doId, 'lureBoost2', 50, 3, 'setBoth')
            elif atkType['name'] == 'RecordkeeperRedlinedClause':
                result = 25
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'noSOS', 1, 3, 'setBoth')
                self.setToonCondition(toon.doId, 'noFires', 1, 3, 'setBoth')
               # self.setToonCondition(toon.doId, 'noUnites', 1, 3, 'setBoth')
                self.setToonCondition(toon.doId, 'noSues', 1, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'redlinedcalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'RecordkeeperRedlinedClauseMissedPayment':
                result = self.recordkeeperCalculatorMultiplier
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'RecordkeeperAuditCycle':
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
            elif atkType['name'] == 'ContingencySelfRepair':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                theSuit.setHP(theSuit.currHP + 750)
                self.setSuitCondition(theSuit.doId, 'selfRepairCalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'ContingencyContingencyClauseRetaliation':
                if self.toonHasCondition(toon.doId, 'banned') or self.toonHasCondition(toon.doId, 'banned2'):
                    self.setToonCondition(toon.doId, 'banned', 1, 1, 'setBoth')
                    self.setToonCondition(toon.doId, 'banned2', 1, 1, 'setBoth')
                    result = 50
                    self.setToonCondition(toon.doId, 'allGagBoost', -40, 2, 'setBoth')
                    self.setToonCondition(toon.doId, 'lureBoost', -40, 2, 'setBoth')
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'ContingencyRedundantAuthority':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'redundantcalculator', 0, 0, 'setBoth')
                theSuit.setHP(theSuit.currHP - 1000)
                if (theSuit.currHP) <= 0:
                    if theSuit.getSkeleRevives() >= 1:
                        theSuit.useSkeleRevive()
                    self.__removeLured(theSuit)
                    if not self.suitHasCondition(theSuit.doId, 'dead'):
                        self.calculator.deadSuits += 1
                        self.setSuitCondition(theSuit.doId, 'dead', 1, -1, 'setBoth')
                for suit in self.battle.activeSuits:
                    if suit.dna.name != 'cdirector':
                        if suit.currHP <= 0:
                            continue
                        suit.setHP(suit.currHP + 325)
            elif atkType['name'] == 'ContingencyContingencyClause':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                if theSuit.dna.name == 'cdirector':
                    for t in self.battle.activeToons:
                        self.setToonCondition(t, 'nolevel8s', 1, 0, 'setBoth')
                        self.setToonCondition(t, 'nolevel6s', 1, 0, 'setBoth')
                        self.setToonCondition(t, 'nolevel7s', 1, 0, 'setBoth')
                        self.setToonCondition(t, 'nolevel5s', 1, 0, 'setBoth')
                        self.setToonCondition(t, 'nolevel4s', 1, 0, 'setBoth')
                        self.setToonCondition(t, random.choice(('nolevel5s', 'nolevel7s', 'nolevel4s', 'nolevel6s', 'nolevel8s')), 1, 3, 'setBoth')
                        self.setToonCondition(t, 'noSquirtGags', 1, 0, 'setBoth')
                        self.setToonCondition(t, 'noThrowGags', 1, 0, 'setBoth')
                        self.setToonCondition(t, 'noLureGags', 1, 0, 'setBoth')
                        self.setToonCondition(t, 'noDropGags', 1, 0, 'setBoth')
                        self.setToonCondition(t, 'noToonUpGags', 1, 0, 'setBoth')
                        self.setToonCondition(t, 'noTrapGags', 1, 0, 'setBoth')
                        self.setToonCondition(t, 'noZapGags', 1, 0, 'setBoth')
                        self.setToonCondition(t, 'noSoundGags', 1, 0, 'setBoth')
                        self.setToonCondition(t, random.choice(('noSquirtGags', 'noSoundGags', 'noToonUpGags', 'noLureGags', 'noZapGags', 'noTrapGags', 'noThrowGags',
                                                                'noDropGags')), 1, 3, 'setBoth')
            elif atkType['name'] == 'ContingencyRiskThresholdBreach75':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'shielding', 1, -1, 'setBoth')
            elif atkType['name'] == 'ContingencyOperationalFreeze':
                result = 0

                attack[SUIT_HP_COL][targetIndex] = result

                # syncCond = 'contentSync%s' % result

                # self.battle.nextContentSyncOrderCondition = syncCond

                # for t in self.battle.activeToons:

                #     for cond in self.calculator.CONTENT_SYNC_CONDITION_ORDERS.keys():
                #         self.setToonCondition(t, cond, 0, 0, 'setBoth')

                #     self.setToonCondition(t, syncCond, 1, -1, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'contentSyncCalculator', 1, -1, 'setBoth')
            elif atkType['name'] == 'ContingencyFailsafeProtocol':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'contingencyHit', 0, 0, 'setBoth')
                if not self.suitHasCondition(theSuit.doId, 'directorDamageReduction'):
                    self.setSuitCondition(theSuit.doId, 'directorDamageReduction', .95, -1, 'setBoth')
                else:
                    self.setSuitCondition(theSuit.doId, 'directorDamageReduction', (self.getSuitConditionModifier(theSuit.doId, 'directorDamageReduction') - .05), -1, 'setBoth')
            elif atkType['name'] == 'ContingencyRiskThresholdBreach':
                result = self.contingencyThresholds
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'ContingencyRiskThresholdBreach25':
                if self.toonHasCondition(toon.doId, 'contingencyMarked') and self.toonHasCondition(toon.doId, 'contingencyHit'):
                    self.setToonCondition(toon.doId, 'contingencyHit', 0, 0, 'setBoth')
                    self.setSuitCondition(theSuit.doId, 'soakedcalculator', 0, 0, 'setBoth')
                    result = 25
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'ContingencyMarkLiquidated':
                self.setSuitCondition(theSuit.doId, 'markedcalculator2', 0, 0, 'setBoth')
                self.setToonCondition(toon.doId, 'contingencyMarked', 1, 3, 'setBoth')
                result = 5
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'ContingencyMarkRevisedFiling':
                condition = random.choice(self.unusedConditions)
                if condition == 1:
                    self.unusedConditions.remove(condition)
                    self.setSuitCondition(theSuit.doId, 'alreadyFailsafeProtocol', 1, -1, 'setBoth')
                if condition == 2:
                    self.unusedConditions.remove(condition)
                    self.setSuitCondition(theSuit.doId, 'alreadyAbsorbingContingency', 1, -1, 'setBoth')
                if condition == 3:
                    self.unusedConditions.remove(condition)
                    self.setSuitCondition(theSuit.doId, 'alreadyOperationalFreeze', 1, -1, 'setBoth')
                if condition == 4:
                    self.unusedConditions.remove(condition)
                    self.setSuitCondition(theSuit.doId, 'alreadyRedundant', 1, -1, 'setBoth')
                    self.setSuitCondition(theSuit.doId, 'redundantcalculator', 1, 3, 'setBoth')
                if condition == 5:
                    self.unusedConditions.remove(condition)
                    self.setSuitCondition(theSuit.doId, 'alreadyContingency', 1, -1, 'setBoth')
                if condition == 6:
                    self.unusedConditions.remove(condition)
                    self.setSuitCondition(theSuit.doId, 'alreadySecondAttack', 1, -1, 'setBoth')
                    self.setSuitCondition(theSuit.doId, 'markedcalculator', 1, 3, 'setBoth')
                if condition == 7:
                    self.unusedConditions.remove(condition)
                    self.setSuitCondition(theSuit.doId, 'alreadyHighPressure', 1, -1, 'setBoth')
                    self.setSuitCondition(theSuit.doId, 'highpressurecalculator', 1, 3, 'setBoth')
                if condition == 8:
                    self.unusedConditions.remove(condition)
                    self.setSuitCondition(theSuit.doId, 'alreadyContent', 1, -1, 'setBoth')
                # if condition in self.unusedConditions:
                #     del self.unusedConditions[condition]
                if self.suitHasCondition(theSuit.doId, 'risk1'):
                    self.setSuitCondition(theSuit.doId, 'alreadyRisk1', 1, -1, 'setBoth')
                    self.setSuitCondition(theSuit.doId, 'risk1', 0, 0, 'setBoth')
                elif self.suitHasCondition(theSuit.doId, 'risk2'):
                    self.setSuitCondition(theSuit.doId, 'alreadyRisk2', 1, -1, 'setBoth')
                    self.setSuitCondition(theSuit.doId, 'risk2', 0, 0, 'setBoth')
                elif self.suitHasCondition(theSuit.doId, 'risk3'):
                    self.setSuitCondition(theSuit.doId, 'alreadyRisk3', 1, -1, 'setBoth')
                    self.setSuitCondition(theSuit.doId, 'risk3', 0, 0, 'setBoth')
                elif self.suitHasCondition(theSuit.doId, 'risk4'):
                    self.setSuitCondition(theSuit.doId, 'alreadyRisk4', 1, -1, 'setBoth')
                    self.setSuitCondition(theSuit.doId, 'risk4', 0, 0, 'setBoth')
                elif self.suitHasCondition(theSuit.doId, 'risk5'):
                    self.setSuitCondition(theSuit.doId, 'alreadyRisk5', 1, -1, 'setBoth')
                    self.setSuitCondition(theSuit.doId, 'risk5', 0, 0, 'setBoth')
                elif self.suitHasCondition(theSuit.doId, 'risk6'):
                    self.setSuitCondition(theSuit.doId, 'alreadyRisk6', 1, -1, 'setBoth')
                    self.setSuitCondition(theSuit.doId, 'risk6', 0, 0, 'setBoth')
                elif self.suitHasCondition(theSuit.doId, 'risk7'):
                    self.setSuitCondition(theSuit.doId, 'alreadyRisk7', 1, -1, 'setBoth')
                    self.setSuitCondition(theSuit.doId, 'risk7', 0, 0, 'setBoth')
                elif self.suitHasCondition(theSuit.doId, 'risk8'):
                    self.setSuitCondition(theSuit.doId, 'alreadyRisk8', 1, -1, 'setBoth')
                    self.setSuitCondition(theSuit.doId, 'risk8', 0, 0, 'setBoth')
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'ContingencyRiskThresholdBreach50':
                self.setToonCondition(toon.doId, 'riskBreachRecentlyTargeted', 1, 2, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'markedcalculator', 0, 0, 'setBoth')
                self.setToonCondition(toon.doId, 'contingencyMarked', 1, 3, 'setBoth')
                result = 5
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'ContingencyForecastCollapse':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'phase3', 1, -1, 'setBoth')
                for suit in self.battle.activeSuits:
                    if suit.dna.name in ('dking', 'rkeeper', 'liquid'):
                        suit.setDamageMultiplier(suit.getDamageMultiplier() * 1.4)
            elif atkType['name'] == 'TollmasterRushHour':
                self.setSuitCondition(theSuit.doId, 'rushHour', 1, 3, 'setBoth')
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'rushHourcalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'TollmasterMandatoryToll':
                if self.toonHasCondition(toon.doId, 'tollmasterHit'):
                    if self.suitHasCondition(theSuit.doId, 'rushHour'):
                        if not self.toonHasCondition(toon.doId, 'tollmasterDamage'):
                            self.setToonCondition(toon.doId, 'tollmasterDamage', 16, -1, 'setBoth')
                        else:
                            self.setToonCondition(toon.doId, 'tollmasterDamage',
                                                  self.getToonConditionModifier(toonId, 'tollmasterDamage') + 16, -1, 'setBoth')
                        result = 16
                    else:
                        if not self.toonHasCondition(toon.doId, 'tollmasterDamage'):
                            self.setToonCondition(toon.doId, 'tollmasterDamage', 8, -1, 'setBoth')
                        else:
                            self.setToonCondition(toon.doId, 'tollmasterDamage',
                                                  self.getToonConditionModifier(toonId, 'tollmasterDamage') + 8, -1, 'setBoth')
                        result = 8
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'TollmasterMandatoryTollFinal':
                self.setSuitCondition(theSuit.doId, 'finalToll', 1, -1, 'setBoth')
                result = self.getToonConditionModifier(toonId, 'tollmasterDamage')
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'TollmasterLedgerOfSound':
                self.setSuitCondition(theSuit.doId, 'soundcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'vulnerablevideographer', self.getSuitConditionModifier(theSuit.doId, 'vulnerablevideographer') * 1 + (math.ceil(.05 / len(self.battle.activeToons))), -1, 'setBoth')
                if self.toonHasCondition(toon.doId, 'usedSound'):
                    result = 50
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'TollmasterResonanceTax':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                theSuit.setDamageMultiplier(theSuit.getDamageMultiplier() * 1.05)
            elif atkType['name'] == 'TollmasterResonanceTax2':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                theSuit.setDamageMultiplier(theSuit.getDamageMultiplier() * 1.1)
            elif atkType['name'] == 'TollmasterResonanceTax3':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                theSuit.setDamageMultiplier(theSuit.getDamageMultiplier() * 1.15)
            elif atkType['name'] == 'TollmasterResonanceTax4':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                theSuit.setDamageMultiplier(theSuit.getDamageMultiplier() * 1.2)
            elif atkType['name'] == 'TollmasterResonanceTax5':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                theSuit.setDamageMultiplier(theSuit.getDamageMultiplier() * 1.25)
            elif atkType['name'] == 'TollmasterBalanceTheLedger':
                result = self.syphonedHP
                attack[SUIT_HP_COL][targetIndex] = result
                buffPercent = ((self.syphonedHP * 0.05) * 0.01)
                for suit in self.battle.activeSuits:
                    if suit.getManager():
                        if suit.currHP > 0:
                            suit.setDamageMultiplier(suit.getDamageMultiplier() * (1.0 + buffPercent))
                            suit.setHP(suit.currHP + result)
                    if not suit.getManager() and (suit.currHP < suit.maxHP) and not suit.getGovernaught():
                        suit.setHP(0)
                        self.__removeLured(suit.doId)
                        self.setSuitCondition(suit.doId, 'dead', 1, 1, 'setBoth')
            elif atkType['name'] == 'TollmasterBalanceTheLedger2':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for suit in self.battle.activeSuits:
                    if suit.getManager():
                        if suit.currHP > 0:
                            suit.setHP(suit.currHP + 200)
                            suit.setDamageMultiplier(suit.getDamageMultiplier() * 1.1)
                    if not suit.getManager() and (suit.currHP < suit.maxHP):
                        suit.setHP(0)
                        self.__removeLured(suit.doId)
                        self.setSuitCondition(suit.doId, 'dead', 1, 1, 'setBoth')
            elif atkType['name'] == 'TollmasterBalanceTheLedger3':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for suit in self.battle.activeSuits:
                    if suit.getManager():
                        if suit.currHP > 0:
                            suit.setHP(suit.currHP + 300)
                            suit.setDamageMultiplier(suit.getDamageMultiplier() * 1.15)
                    if not suit.getManager() and (suit.currHP < suit.maxHP):
                        suit.setHP(0)
                        self.__removeLured(suit.doId)
                        self.setSuitCondition(suit.doId, 'dead', 1, 1, 'setBoth')
            elif atkType['name'] == 'TollmasterBalanceTheLedger4':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for suit in self.battle.activeSuits:
                    if suit.getManager():
                        if suit.currHP > 0:
                            suit.setHP(suit.currHP + 400)
                            suit.setDamageMultiplier(suit.getDamageMultiplier() * 1.2)
                    if not suit.getManager() and (suit.currHP < suit.maxHP):
                        suit.setHP(0)
                        self.__removeLured(suit.doId)
                        self.setSuitCondition(suit.doId, 'dead', 1, 1, 'setBoth')
            elif atkType['name'] == 'TollmasterBalanceTheLedger5':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for suit in self.battle.activeSuits:
                    if suit.getManager():
                        if suit.currHP > 0:
                            suit.setHP(suit.currHP + 500)
                            suit.setDamageMultiplier(suit.getDamageMultiplier() * 1.25)
                    if not suit.getManager() and (suit.currHP < suit.maxHP):
                        suit.setHP(0)
                        self.__removeLured(suit.doId)
                        self.setSuitCondition(suit.doId, 'dead', 1, 1, 'setBoth')
            elif atkType['name'] == 'TollmasterMissedPayment':
                if toon.hp >= 200:
                    result = 1
                    for s in self.battle.suits:
                        if s.dna.name == 'rkeeper':
                            suit = s
                            currentBossHealth = s.currHP
                            if currentBossHealth >= 1:
                                self.setSuitCondition(suit.doId, 'missedPaymentRetaliation', 1, 10, 'setBoth')
                    self.setToonCondition(toon.doId, 'dodgy', -100, 2, 'setBoth')
                    self.setToonCondition(toon.doId, 'markedForRedlined', 1, 5, 'setBoth')
                    if self.getToonConditionModifier(toonId, 'allGagBoost2') > 10:
                        self.setToonCondition(toonId, 'allGagBoost2', self.getToonConditionModifier(toonId, 'allGagBoost2'), 2, 'setBoth')
                        self.setToonCondition(toonId, 'lureBoost2', self.getToonConditionModifier(toonId, 'lureBoost2'), 2, 'setBoth')
                    else:
                        self.setToonCondition(toonId, 'allGagBoost', 10, 2, 'setBoth')
                        self.setToonCondition(toonId, 'lureBoost2', 10, 2, 'setBoth')
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'DividendZapRetaliation':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                theSuit.setDamageMultiplier(theSuit.getDamageMultiplier() * 1.1)
                theSuit.setHP(theSuit.currHP + 100)
            elif atkType['name'] == 'DividendLiquidationEvent':
                self.setSuitCondition(theSuit.doId, 'liquidationcalculator', 0, 0, 'setBoth')
                self.setToonCondition(toon.doId, 'liquidationRecentlyTargeted', 1, 2, 'setBoth')
                self.setToonCondition(toon.doId, 'liquidated', 1, 3, 'setBoth')
                result = 5
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'DividendPeckingOrderZapped':
                self.setSuitCondition(theSuit.doId, 'embezzlecalculator', 0, 0, 'setBoth')
                self.setToonCondition(toon.doId, 'disable6s', 1, 2, 'setBoth')
                self.setToonCondition(toon.doId, 'disable7s', 1, 2, 'setBoth')
                self.setToonCondition(toon.doId, 'disable8s', 1, 2, 'setBoth')
                result = 20
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'DividendLiquidationEventDamage':
                for s in self.battle.suits:
                    self.setSuitCondition(s.doId, 'dotfinished', 1, 1, 'setBoth')
                result = 30
                attack[SUIT_HP_COL][targetIndex] = result
                if self.toonHasCondition(toonId, 'snapped'):
                    result *= self.getToonConditionModifier(toonId, 'snapped')
                if self.toonHasCondition(toonId, 'bombedToon'):
                    result *= self.getToonConditionModifier(toonId, 'bombedToon')
                if self.toonHasCondition(toonId, 'markedwood'):
                    result *= self.getToonConditionModifier(toonId, 'markedwood')
                # Going to slowly replace individual status effects so we acclimate to the new system before moving onto a more sophisticated means of this.
                for condition in self.toonStatusConditionsNew[toonId]:
                    if isinstance(condition, StatusEffects.Snapped):
                        result *= condition.defenseMod
            elif atkType['name'] == 'DividendPeckingOrder':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'scabbardcalculator', 0, 0, 'setBoth')
                for suit in self.battle.activeSuits:
                    if not suit.getManager():
                        if suit.currHP <= 0:
                            continue
                        x = (suit.maxHP * suit.hardMaxHP) - suit.currHP
                        if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
                            suit.setHP(suit.currHP + 0)
                        elif suit.currHP > (suit.maxHP * 2):
                            suit.setHP(suit.currHP + x)
                        else:
                            suit.setHP(suit.currHP + suit.maxHP)
                        continue
                    else:
                        if suit.currHP <= 0:
                            continue
                        x = (suit.maxHP * suit.hardMaxHP) - suit.currHP
                        if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
                            suit.setHP(suit.currHP + 0)
                        elif suit.currHP + 200 > (suit.maxHP * suit.hardMaxHP):
                            suit.setHP(suit.currHP + x)
                        else:
                            suit.setHP(suit.currHP + 200)
            elif atkType['name'] == 'DividendTotalMarketMeltdown':
                result = 15
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'marketcalculator', 0, 0, 'setBoth')
                self.setToonCondition(toon.doId, 'disableGroupGags', 1, 3, 'setBoth')
                self.setToonCondition(toon.doId, 'raisedAnte', 50, 3, 'setBoth')
                self.setToonCondition(toon.doId, 'lureBoost', 50, 3, 'setBoth')
                for suit in self.battle.activeSuits:
                    self.setSuitCondition(suit.doId, 'marketMeltdown', 1, 3, 'setBoth')
            elif atkType['name'] == 'DividendTotalMarketMeltdown2':
                result = 15
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'marketcalculator', 0, 0, 'setBoth')
                self.setToonCondition(toon.doId, 'disableSingleGags', 1, 3, 'setBoth')
                self.setToonCondition(toon.doId, 'raisedAnte', 50, 3, 'setBoth')
                self.setToonCondition(toon.doId, 'lureBoost', 50, 3, 'setBoth')
                for suit in self.battle.activeSuits:
                    self.setSuitCondition(suit.doId, 'marketMeltdown', 1, 3, 'setBoth')
            elif atkType['name'] == 'DividendTotalMarketMeltdownDamage':
                result = 25
                attack[SUIT_HP_COL][targetIndex] = result
                if self.toonHasCondition(toonId, 'snapped'):
                    result *= self.getToonConditionModifier(toonId, 'snapped')
                if self.toonHasCondition(toonId, 'bombedToon'):
                    result *= self.getToonConditionModifier(toonId, 'bombedToon')
                if self.toonHasCondition(toonId, 'markedwood'):
                    result *= self.getToonConditionModifier(toonId, 'markedwood')
                for suit in self.battle.activeSuits:
                    if self.suitHasCondition(suit.doId, 'marketMeltdown'):
                        if not self.suitHasCondition(suit.doId, 'alreadyMelted'):
                            self.setSuitCondition(suit.doId, 'alreadyMelted', 1, 1, 'setBoth')
                            suit.setHP(suit.currHP - 100)
                            if (suit.currHP) <= 0:
                                self.__removeLured(suit.doId)
                                if suit.dna.name == 'cbutcher':
                                    for s in self.battle.activeSuits:
                                        if s.dna.name == 'rkeeper':
                                            self.setSuitCondition(s.doId, 'phantomDeath', 1, 2, 'setBoth')
                                if suit.getSkeleRevives() >= 1:
                                    suit.useSkeleRevive()
                                if not self.suitHasCondition(suit.doId, 'dead'):
                                    self.calculator.deadSuits += 1
                                    self.setSuitCondition(suit.doId, 'dead', 1, -1, 'setBoth')
                # Check to see if the Liquidator already has extra attacks.
            # elif atkType['name'] == 'LiquidatorTornado':
            #     self.setToonCondition(toon.doId, 'confused', 1, 2, 'setBoth')
            #     self.setSuitCondition(theSuit.doId, 'tornadocalculator', 0, 0, 'setBoth')
            #     result = 25
            #     attack[SUIT_HP_COL][targetIndex] = result
            # elif atkType['name'] == 'LiquidatorOilRain':
            #     result = 0
            #     attack[SUIT_HP_COL][targetIndex] = result
            #     self.setSuitCondition(theSuit.doId, 'liquidatorRotation', 0, 0, 'setBoth')
            #     for t in self.battle.activeToons:
            #         self.setToonCondition(t, 'groupDamageDown', 0, 0, 'setBoth')
            #     self.setSuitCondition(theSuit.doId, 'alreadyOil', 1, 10, 'setBoth')
            #     self.setSuitCondition(theSuit.doId, 'oilRain', 1, 4, 'setBoth')
            #     self.setSuitCondition(theSuit.doId, 'freezingRain', 0, 0, 'setBoth')
            #     self.setSuitCondition(theSuit.doId, 'heavyRain', 0, 0, 'setBoth')
            #     self.setSuitCondition(theSuit.doId, 'stormCell', 0, 0, 'setBoth')
            #     self.setSuitCondition(theSuit.doId, 'inversion', 0, 0, 'setBoth')
            #     self.setSuitCondition(theSuit.doId, 'monsoon', 0, 0, 'setBoth')
            # elif atkType['name'] == 'LiquidatorFreezingRain':
            #     result = 0
            #     attack[SUIT_HP_COL][targetIndex] = result
            #     self.setSuitCondition(theSuit.doId, 'liquidatorRotation', 0, 0, 'setBoth')
            #     self.setSuitCondition(theSuit.doId, 'alreadyFreezing', 1, 10, 'setBoth')
            #     self.setSuitCondition(theSuit.doId, 'freezingRain', 1, 4, 'setBoth')
            #     for t in self.battle.activeToons:
            #         self.setToonCondition(t, 'groupDamageDown', -50, 4, 'setBoth')
            #     self.setSuitCondition(theSuit.doId, 'oilRain', 0, 0, 'setBoth')
            #     self.setSuitCondition(theSuit.doId, 'heavyRain', 0, 0, 'setBoth')
            #     self.setSuitCondition(theSuit.doId, 'stormCell', 0, 0, 'setBoth')
            #     self.setSuitCondition(theSuit.doId, 'inversion', 0, 0, 'setBoth')
            #     self.setSuitCondition(theSuit.doId, 'monsoon', 0, 0, 'setBoth')
            # elif atkType['name'] == 'LiquidatorHeavyRain':
            #     result = 0
            #     attack[SUIT_HP_COL][targetIndex] = result
            #     self.setSuitCondition(theSuit.doId, 'liquidatorRotation', 0, 0, 'setBoth')
            #     self.setSuitCondition(theSuit.doId, 'alreadyHeavyRain', 1, 10, 'setBoth')
            #     self.setSuitCondition(theSuit.doId, 'heavyRain', 1, 4, 'setBoth')
            #     for suit in self.battle.activeSuits:
            #         self.setSuitCondition(suit.doId, 'heavyRainDamage', 1, -1, 'setBoth')
            #     for t in self.battle.activeToons:
            #         self.setToonCondition(t, 'groupDamageDown', 0, 0, 'setBoth')
            #         self.setToonCondition(t, 'heavyRainDamageToon', 1, -1, 'setBoth')
            #     self.setSuitCondition(theSuit.doId, 'oilRain', 0, 0, 'setBoth')
            #     self.setSuitCondition(theSuit.doId, 'freezingRain', 0, 0, 'setBoth')
            #     self.setSuitCondition(theSuit.doId, 'stormCell', 0, 0, 'setBoth')
            #     self.setSuitCondition(theSuit.doId, 'inversion', 0, 0, 'setBoth')
            #     self.setSuitCondition(theSuit.doId, 'monsoon', 0, 0, 'setBoth')
            # elif atkType['name'] == 'LiquidatorMonsoon':
            #     result = 0
            #     attack[SUIT_HP_COL][targetIndex] = result
            #     self.setSuitCondition(theSuit.doId, 'liquidatorRotation', 0, 0, 'setBoth')
            #     self.setSuitCondition(theSuit.doId, 'alreadyMonsoon', 1, 10, 'setBoth')
            #     self.setSuitCondition(theSuit.doId, 'monsoon', 1, 4, 'setBoth')
            #     for t in self.battle.activeToons:
            #         self.setToonCondition(t, 'groupDamageDown', 0, 0, 'setBoth')
            #     self.setSuitCondition(theSuit.doId, 'oilRain', 0, 0, 'setBoth')
            #     self.setSuitCondition(theSuit.doId, 'freezingRain', 0, 0, 'setBoth')
            #     self.setSuitCondition(theSuit.doId, 'stormCell', 0, 0, 'setBoth')
            #     self.setSuitCondition(theSuit.doId, 'inversion', 0, 0, 'setBoth')
            #     self.setSuitCondition(theSuit.doId, 'heavyRain', 0, 0, 'setBoth')
            # elif atkType['name'] == 'LiquidatorHeavyRainDamage':
            #     result = math.ceil(self.getSuitConditionModifier(theSuit.doId, 'heavyRainDamage') * .1)
            #     attack[SUIT_HP_COL][targetIndex] = result
            #     for suit in self.battle.activeSuits:
            #         if not self.suitHasCondition(suit.doId, 'alreadyHealed'):
            #             self.setSuitCondition(suit.doId, 'alreadyHealed', 1, 1, 'setBoth')
            #             suit.setHP(suit.currHP - self.getSuitConditionModifier(suit.doId, 'heavyRainDamage'))
            #             if suit.currHP <= 0:
            #                 if suit.getSkeleRevives() >= 1:
            #                     suit.useSkeleRevive()
            #                 self.__removeLured(suit.doId)
            #                 if self.suitHasCondition(suit.doId, 'lured'):
            #                     self.setSuitCondition(suit.doId, 'lured', 0, 0, 'setBoth')
            #             continue
            #         self.setSuitCondition(suit.doId, 'heavyRainDamage', self.getSuitConditionModifier(suit.doId, 'heavyRainDamage'), 1, 'setBoth')
            #     for t in self.battle.activeToons:
            #         self.setToonCondition(t, 'groupDamageDown', 0, 0, 'setBoth')
            #         self.setToonCondition(t, 'heavyRainDamageToon', self.getToonConditionModifier(toonId, 'heavyRainDamageToon'), 1, 'setBoth')
            #     self.setSuitCondition(theSuit.doId, 'oilRain', 0, 0, 'setBoth')
            #     self.setSuitCondition(theSuit.doId, 'freezingRain', 0, 0, 'setBoth')
            #     self.setSuitCondition(theSuit.doId, 'stormCell', 0, 0, 'setBoth')
            #     self.setSuitCondition(theSuit.doId, 'inversion', 0, 0, 'setBoth')
            #     self.setSuitCondition(theSuit.doId, 'monsoon', 0, 0, 'setBoth')
            # elif atkType['name'] == 'LiquidatorOilRainDamage':
            #     result = 25
            #     attack[SUIT_HP_COL][targetIndex] = result
            #     for suit in self.battle.activeSuits:
            #         if not self.suitHasCondition(suit.doId, 'alreadyHealed') and suit.currHP > 0:
            #             self.setSuitCondition(suit.doId, 'alreadyHealed', 1, 1, 'setBoth')
            #             suit.setHP(suit.currHP + 100)
            # elif atkType['name'] == 'LiquidatorInversion':
            #     result = 0
            #     attack[SUIT_HP_COL][targetIndex] = result
            #     self.setSuitCondition(theSuit.doId, 'liquidatorRotation', 0, 0, 'setBoth')
            #     self.setSuitCondition(theSuit.doId, 'alreadyInversion', 1, 10, 'setBoth')
            #     self.setSuitCondition(theSuit.doId, 'inversion', 1, 4, 'setBoth')
            #     for t in self.battle.activeToons:
            #         self.setToonCondition(t, 'groupDamageDown', 0, 0, 'setBoth')
            #     self.setSuitCondition(theSuit.doId, 'oilRain', 0, 0, 'setBoth')
            #     self.setSuitCondition(theSuit.doId, 'freezingRain', 0, 0, 'setBoth')
            #     self.setSuitCondition(theSuit.doId, 'stormCell', 0, 0, 'setBoth')
            #     self.setSuitCondition(theSuit.doId, 'monsoon', 0, 0, 'setBoth')
            #     self.setSuitCondition(theSuit.doId, 'heavyRain', 0, 0, 'setBoth')
            #     theSuit.setHP(theSuit.currHP + 250)
            #     # if not self.suitHasCondition(theSuit.doId, 'extraAttack'):
            #     #     self.setSuitCondition(theSuit.doId, 'extraAttack', 1, -1, 'setBoth')
            #     # elif self.suitHasCondition(theSuit.doId, 'extraAttack') and not self.suitHasCondition(
            #     #         theSuit.doId, 'extraAttack2'):
            #     #     self.setSuitCondition(theSuit.doId, 'extraAttack2', 1, -1, 'setBoth')
            #     # elif self.suitHasCondition(theSuit.doId, 'extraAttack2') and not self.suitHasCondition(
            #     #         theSuit.doId, 'extraAttack3'):
            #     #     self.setSuitCondition(theSuit.doId, 'extraAttack3', 1, -1, 'setBoth')
            #     # elif self.suitHasCondition(theSuit.doId, 'extraAttack3') and not self.suitHasCondition(
            #     #         theSuit.doId, 'extraAttack4'):
            #     #     self.setSuitCondition(theSuit.doId, 'extraAttack4', 1, -1, 'setBoth')
            #     # elif self.suitHasCondition(theSuit.doId, 'extraAttack4') and not self.suitHasCondition(
            #     #         theSuit.doId, 'extraAttack5'):
            #     #     self.setSuitCondition(theSuit.doId, 'extraAttack5', 1, -1, 'setBoth')
            #     # elif self.suitHasCondition(theSuit.doId, 'extraAttack5') and not self.suitHasCondition(
            #     #         theSuit.doId, 'extraAttack6'):
            #     #     self.setSuitCondition(theSuit.doId, 'extraAttack6', 1, -1, 'setBoth')
            #     # elif self.suitHasCondition(theSuit.doId, 'extraAttack6') and not self.suitHasCondition(
            #     #         theSuit.doId, 'extraAttack7'):
            #     #     self.setSuitCondition(theSuit.doId, 'extraAttack7', 1, -1, 'setBoth')
            #     # elif self.suitHasCondition(theSuit.doId, 'extraAttack7') and not self.suitHasCondition(
            #     #         theSuit.doId, 'extraAttack8'):
            #     #     self.setSuitCondition(theSuit.doId, 'extraAttack8', 1, -1, 'setBoth')
            #     # elif self.suitHasCondition(theSuit.doId, 'extraAttack8') and not self.suitHasCondition(
            #     #         theSuit.doId, 'extraAttack9'):
            #     #     self.setSuitCondition(theSuit.doId, 'extraAttack9', 1, -1, 'setBoth')
            #     # elif self.suitHasCondition(theSuit.doId, 'extraAttack9') and not self.suitHasCondition(
            #     #         theSuit.doId, 'extraAttack10'):
            #     #     self.setSuitCondition(theSuit.doId, 'extraAttack10', 1, -1, 'setBoth')
            #
            #     # Check to see if the Liquidator already has extra attacks.
            #     for i in range(len(self.suitStatusConditionsNew[theSuit.doId])):
            #         if isinstance(self.suitStatusConditionsNew[theSuit.doId][i], StatusEffects.ExtraAttacks): # Do they have any extra attacks?
            #             self.suitStatusConditionsNew[theSuit.doId][i].extraAttacks += 1 # Add one more attack.
            #             break # Stop the loop so that we do not go down to else.
            #
            #     # They do not have any extra attacks, so give them one.
            #     else:
            #         self.suitStatusConditionsNew[theSuit.doId].append(StatusEffects.ExtraAttacks(1))
            # elif atkType['name'] == 'LiquidatorStormCell':
            #     result = 0
            #     attack[SUIT_HP_COL][targetIndex] = result
            #     self.setSuitCondition(theSuit.doId, 'liquidatorRotation', 0, 0, 'setBoth')
            #     self.setSuitCondition(theSuit.doId, 'alreadyStormCell', 1, 10, 'setBoth')
            #     self.setSuitCondition(theSuit.doId, 'stormCell', 1, 4, 'setBoth')
            #     self.setSuitCondition(theSuit.doId, 'stormCellDamage', 60, -1, 'setBoth')
            #     for t in self.battle.activeToons:
            #         self.setToonCondition(t, 'groupDamageDown', 0, 0, 'setBoth')
            #     self.setSuitCondition(theSuit.doId, 'oilRain', 0, 0, 'setBoth')
            #     self.setSuitCondition(theSuit.doId, 'freezingRain', 0, 0, 'setBoth')
            #     self.setSuitCondition(theSuit.doId, 'inversion', 0, 0, 'setBoth')
            #     self.setSuitCondition(theSuit.doId, 'monsoon', 0, 0, 'setBoth')
            #     self.setSuitCondition(theSuit.doId, 'heavyRain', 0, 0, 'setBoth')
            # elif atkType['name'] == 'LiquidatorStormCellDamage':
            #     result = self.getSuitConditionModifier(theSuit.doId, 'stormCellDamage')
            #     self.setSuitCondition(theSuit.doId, 'stormCellDamage', self.getSuitConditionModifier(theSuit.doId, 'stormCellDamage'), 1, 'setBoth')
            #     attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'ButcherAggrandize':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                targetSuit = self.battle.activeSuits[1]
                self.setSuitCondition(theSuit.doId, 'rpm', self.getSuitConditionModifier(theSuit.doId, 'rpm') - 3, -1, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target6', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target5', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target4', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target3', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target2', 0, 0, 'setBoth')
                targetSuit.setManager(1)
                targetSuit.setHP(1000)
                targetSuit.setMaxHP(1000)
                self.setSuitCondition(targetSuit.doId, 'shielding', 1, -1, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'sued', 0, 0, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'suemovie', 0, 0, 'setBoth')
                if not self.suitHasCondition(targetSuit.doId, 'dead'):
                    self.setSuitCondition(theSuit.doId, 'aggrandizecalculator', 0, 0, 'setBoth')
                    self.setSuitCondition(theSuit.doId, 'deadpromotion', 0, 0, 'setBoth')
                continue
            elif atkType['name'] == 'ButcherAggrandize2':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                targetSuit = self.battle.activeSuits[2]
                self.setSuitCondition(theSuit.doId, 'rpm', self.getSuitConditionModifier(theSuit.doId, 'rpm') - 3, -1, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target6', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target5', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target4', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target3', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target2', 0, 0, 'setBoth')
                targetSuit.setManager(1)
                targetSuit.setHP(1000)
                targetSuit.setMaxHP(1000)
                self.setSuitCondition(targetSuit.doId, 'shielding', 1, -1, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'sued', 0, 0, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'suemovie', 0, 0, 'setBoth')
                if not self.suitHasCondition(targetSuit.doId, 'dead'):
                    self.setSuitCondition(theSuit.doId, 'aggrandizecalculator', 0, 0, 'setBoth')
                    self.setSuitCondition(theSuit.doId, 'deadpromotion', 0, 0, 'setBoth')
                continue
            elif atkType['name'] == 'ButcherAggrandize3':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                targetSuit = self.battle.activeSuits[3]
                self.setSuitCondition(theSuit.doId, 'rpm', self.getSuitConditionModifier(theSuit.doId, 'rpm') - 3, -1, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target6', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target5', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target4', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target3', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target2', 0, 0, 'setBoth')
                targetSuit.setManager(1)
                targetSuit.setHP(1000)
                targetSuit.setMaxHP(1000)
                self.setSuitCondition(targetSuit.doId, 'shielding', 1, -1, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'sued', 0, 0, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'suemovie', 0, 0, 'setBoth')
                if not self.suitHasCondition(targetSuit.doId, 'dead'):
                    self.setSuitCondition(theSuit.doId, 'aggrandizecalculator', 0, 0, 'setBoth')
                    self.setSuitCondition(theSuit.doId, 'deadpromotion', 0, 0, 'setBoth')
                continue
            elif atkType['name'] == 'ButcherAggrandize4':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                targetSuit = self.battle.activeSuits[4]
                self.setSuitCondition(theSuit.doId, 'rpm', self.getSuitConditionModifier(theSuit.doId, 'rpm') - 3, -1, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target6', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target5', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target4', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target3', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target2', 0, 0, 'setBoth')
                targetSuit.setManager(1)
                targetSuit.setHP(1000)
                targetSuit.setMaxHP(1000)
                self.setSuitCondition(targetSuit.doId, 'shielding', 1, -1, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'sued', 0, 0, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'suemovie', 0, 0, 'setBoth')
                if not self.suitHasCondition(targetSuit.doId, 'dead'):
                    self.setSuitCondition(theSuit.doId, 'aggrandizecalculator', 0, 0, 'setBoth')
                    self.setSuitCondition(theSuit.doId, 'deadpromotion', 0, 0, 'setBoth')
                continue
            elif atkType['name'] == 'ButcherAggrandize5':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'rpm', self.getSuitConditionModifier(theSuit.doId, 'rpm') - 3, -1, 'setBoth')
                targetSuit = self.battle.activeSuits[5]
                self.setSuitCondition(theSuit.doId, 'target6', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target5', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target4', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target3', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target2', 0, 0, 'setBoth')
                targetSuit.setManager(1)
                targetSuit.setHP(1000)
                targetSuit.setMaxHP(1000)
                self.setSuitCondition(targetSuit.doId, 'shielding', 1, -1, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'sued', 0, 0, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'suemovie', 0, 0, 'setBoth')
                if not self.suitHasCondition(targetSuit.doId, 'dead'):
                    self.setSuitCondition(theSuit.doId, 'aggrandizecalculator', 0, 0, 'setBoth')
                    self.setSuitCondition(theSuit.doId, 'deadpromotion', 0, 0, 'setBoth')
            elif atkType['name'] == 'ButcherOffboarding':
                result = 40
                attack[SUIT_HP_COL][targetIndex] = result
                targetSuit = self.battle.activeSuits[1]
                self.setSuitCondition(theSuit.doId, 'rpm', self.getSuitConditionModifier(theSuit.doId, 'rpm') - 2, -1, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target6', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target5', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target4', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target3', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target2', 0, 0, 'setBoth')
                targetSuit.setHP(0)
                if targetSuit.currHP <= 0:
                    self.__removeLured(targetSuit.doId)
                if not self.suitHasCondition(targetSuit.doId, 'dead'):
                    self.setSuitCondition(theSuit.doId, 'offboardingcalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'ButcherOffboarding2':
                result = 40
                attack[SUIT_HP_COL][targetIndex] = result
                targetSuit = self.battle.activeSuits[2]
                self.setSuitCondition(theSuit.doId, 'rpm', self.getSuitConditionModifier(theSuit.doId, 'rpm') - 2, -1, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target6', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target5', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target4', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target3', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target2', 0, 0, 'setBoth')
                targetSuit.setHP(0)
                if targetSuit.currHP <= 0:
                    self.__removeLured(targetSuit.doId)
                if not self.suitHasCondition(targetSuit.doId, 'dead'):
                    self.setSuitCondition(theSuit.doId, 'offboardingcalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'ButcherOffboarding3':
                result = 40
                attack[SUIT_HP_COL][targetIndex] = result
                targetSuit = self.battle.activeSuits[3]
                self.setSuitCondition(theSuit.doId, 'rpm', self.getSuitConditionModifier(theSuit.doId, 'rpm') - 2, -1, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target6', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target5', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target4', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target3', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target2', 0, 0, 'setBoth')
                targetSuit.setHP(0)
                if targetSuit.currHP <= 0:
                    self.__removeLured(targetSuit.doId)
                if not self.suitHasCondition(targetSuit.doId, 'dead'):
                    self.setSuitCondition(theSuit.doId, 'offboardingcalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'ButcherOffboarding4':
                result = 40
                attack[SUIT_HP_COL][targetIndex] = result
                targetSuit = self.battle.activeSuits[4]
                self.setSuitCondition(theSuit.doId, 'rpm', self.getSuitConditionModifier(theSuit.doId, 'rpm') - 2, -1, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target6', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target5', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target4', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target3', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target2', 0, 0, 'setBoth')
                targetSuit.setHP(0)
                if targetSuit.currHP <= 0:
                    self.__removeLured(targetSuit.doId)
                if not self.suitHasCondition(targetSuit.doId, 'dead'):
                    self.setSuitCondition(theSuit.doId, 'offboardingcalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'ButcherOffboarding5':
                result = 40
                attack[SUIT_HP_COL][targetIndex] = result
                targetSuit = self.battle.activeSuits[5]
                self.setSuitCondition(theSuit.doId, 'rpm', self.getSuitConditionModifier(theSuit.doId, 'rpm') - 2, -1, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target6', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target5', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target4', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target3', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target2', 0, 0, 'setBoth')
                targetSuit.setHP(0)
                if targetSuit.currHP <= 0:
                    self.__removeLured(targetSuit.doId)
                if not self.suitHasCondition(targetSuit.doId, 'dead'):
                    self.setSuitCondition(theSuit.doId, 'offboardingcalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'ButcherLayoffs':
                result = 50
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'layoffscalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'rpm', self.getSuitConditionModifier(theSuit.doId, 'rpm') - 10, -1, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'unionbustcalculator', 0, 0, 'setBoth')
                for targetSuit in self.battle.activeSuits:
                    if not targetSuit.getManager():
                        targetSuit.setHP(math.ceil(targetSuit.currHP - targetSuit.currHP))
                        self.__removeLured(targetSuit.doId)
            elif atkType['name'] == 'ButcherScabbard':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'vulnerablevideographer', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'rpm', self.getSuitConditionModifier(theSuit.doId, 'rpm') - 2, -1, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'whipsawcalculator', 1, 10, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'scabbardcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'kickback', 0, 0, 'setBoth')
                for suit in self.battle.activeSuits:
                    if not suit.getManager():
                        if suit.currHP <= 0:
                            continue
                        x = (suit.maxHP * suit.hardMaxHP) - suit.currHP
                        if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
                            suit.setHP(suit.currHP + 0)
                        elif suit.currHP > (suit.maxHP * 2):
                            suit.setHP(suit.currHP + x)
                        else:
                            suit.setHP(suit.currHP + suit.maxHP)
                        continue
                    else:
                        if suit.currHP <= 0:
                            continue
                        x = (suit.maxHP * suit.hardMaxHP) - suit.currHP
                        if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
                            suit.setHP(suit.currHP + 0)
                        elif suit.currHP + 200 > (suit.maxHP * suit.hardMaxHP):
                            suit.setHP(suit.currHP + x)
                        else:
                            suit.setHP(suit.currHP + 200)
            elif atkType['name'] == 'ButcherRevvingUp':
                self.setSuitCondition(theSuit.doId, 'rpm', self.getSuitConditionModifier(theSuit.doId, 'rpm') + self.getSuitConditionModifier(theSuit.doId, 'rpmincrease'), -1, 'setBoth')
                result = self.getSuitConditionModifier(theSuit.doId, 'rpmincrease')
                self.setSuitCondition(theSuit.doId, 'rpmincrease', 0, 0, 'setBoth')
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'rpmcalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'ButcherRevvingUpWhipsaw':
                self.setSuitCondition(theSuit.doId, 'rpm', self.getSuitConditionModifier(theSuit.doId, 'rpm') + (self.getSuitConditionModifier(theSuit.doId, 'rpmincrease') + 4), -1, 'setBoth')
                result = self.getSuitConditionModifier(theSuit.doId, 'rpmincrease') + 4
                self.setSuitCondition(theSuit.doId, 'rpmincrease', 0, 0, 'setBoth')
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'rpmcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'whipsawcalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'ButcherSparkPlug':
                result = 20
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'zapped', 1, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'sparkplugcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'rpm', self.getSuitConditionModifier(theSuit.doId, 'rpm') - 2, -1, 'setBoth')
            elif atkType['name'] == 'ButcherOverride':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'override', 1, 5, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'overridecalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'ButcherOverrideRemoval':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'override', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'kickbackcalculator', 1, 10, 'setBoth')
                if not self.suitHasCondition(theSuit.doId, 'phase3'):
                    self.setSuitCondition(theSuit.doId, 'phase3', 1, -1, 'setBoth')
                    theSuit.setDamageMultiplier(theSuit.getDamageMultiplier() * 1.5)
            elif atkType['name'] == 'ButcherKickback':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'kickback', 1, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'kickbackcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'vulnerablevideographer', 1.5, -1, 'setBoth')
            elif atkType['name'] == 'ButcherSparkPlugDamage':
                if self.toonHasCondition(toon.doId, 'zapped'):
                    result = 25
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'ButcherMarkedWood':
                result = 15
                attack[SUIT_HP_COL][targetIndex] = result
                currentBossHealth = -1
                for s in self.battle.suits:
                    if s.dna.name == 'cdirector':
                        currentBossHealth = s.currHP
                if currentBossHealth >= 1:
                    if self.getToonConditionModifier(toonId, 'markedwood') > 2.0:
                        self.setToonCondition(toon.doId, 'markedwood', self.getToonConditionModifier(toonId, 'markedwood'), 3, 'setBoth')
                    else:
                        self.setToonCondition(toon.doId, 'markedwood', 2.0, 3, 'setBoth')
                else:
                    if self.getToonConditionModifier(toonId, 'markedwood') > 1.75:
                        self.setToonCondition(toon.doId, 'snapped', self.getToonConditionModifier(toonId, 'markedwood'), 3, 'setBoth')
                    else:
                        self.setToonCondition(toon.doId, 'markedwood', 1.75, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'rpm', self.getSuitConditionModifier(theSuit.doId, 'rpm') - 7, -1, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'markedwoodcalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'PayrollPayrollProcessing':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'processcalculator', 0, 0, 'setBoth')
                for suit in self.battle.activeSuits:
                    if suit.currHP <= 0:
                        continue
                    x = (suit.maxHP * suit.hardMaxHP) - suit.currHP
                    if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
                        suit.setHP(suit.currHP + 0)
                    elif suit.currHP + 95 > (suit.maxHP * suit.hardMaxHP):
                        suit.setHP(suit.currHP + x)
                    else:
                        suit.setHP(suit.currHP + 95)
            elif atkType['name'] == 'PayrollPerformanceBonus':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'bonuscalculator', 0, 0, 'setBoth')
                for suit in self.battle.activeSuits:
                    if not suit.getManager():
                        suit.setDamageMultiplier(suit.getDamageMultiplier() * 1.1)
            elif atkType['name'] == 'DerrickManRefinement':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'refinementDerrick', 0, 0, 'setBoth')
                for suit in self.battle.activeSuits:
                    if suit.currHP <= 0:
                        continue
                    x = (suit.maxHP * suit.hardMaxHP) - suit.currHP
                    if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
                        suit.setHP(suit.currHP + 0)
                    elif suit.currHP + (suit.maxHP * .4) > (suit.maxHP * suit.hardMaxHP):
                        suit.setHP(suit.currHP + x)
                    else:
                        suit.setHP(suit.currHP + (suit.maxHP * .4))
            elif atkType['name'] == 'DOLAInkDrain':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'inkDraincalculator', 0, 0, 'setBoth')
                if self.getToonConditionModifier(toonId, 'allGagBoost') < -25:
                    self.setToonCondition(toon.doId, 'allGagBoost',
                                          self.getToonConditionModifier(toonId, 'allGagBoost'), 3, 'setBoth')
                    self.setToonCondition(toon.doId, 'lureBoost',
                                          self.getToonConditionModifier(toonId, 'lureBoost'), 3, 'setBoth')
                else:
                    self.setToonCondition(toon.doId, 'allGagBoost', -25, 3, 'setBoth')
                    self.setToonCondition(toon.doId, 'lureBoost', -25, 3, 'setBoth')
            elif atkType['name'] == 'DOPRAmbushMarketing':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                # Check to see if the target Cog already has extra attacks.
                for i in range(len(self.suitStatusConditionsNew[theSuit.doId])):
                    if isinstance(self.suitStatusConditionsNew[theSuit.doId][i], StatusEffects.ExtraAttacks):  # Does this Cog have any extra attacks?
                        self.suitStatusConditionsNew[theSuit.doId][i].extraAttacks += 1  # Add one more attack.
                        break  # Stop the loop so that we do not go down to else.

                # The Cog does not have any extra attacks, so give them one.
                else:
                    self.suitStatusConditionsNew[theSuit.doId].append(StatusEffects.ExtraAttacks(1))
            elif atkType['name'] == 'UnstableTransformation':
                if atkType['group'] == SuitBattleGlobals.ATK_TGT_FOREMAN:
                    newName = 'foreman'
                    result = random.randint(16, 26)
                    attack[SUIT_HP_COL][targetIndex] = result
                if atkType['group'] == SuitBattleGlobals.ATK_TGT_SUPERVISOR:
                    newName = 'supervis'
                    result = random.randint(16, 27)
                    attack[SUIT_HP_COL][targetIndex] = result
                if atkType['group'] == SuitBattleGlobals.ATK_TGT_ATTORNEY:
                    newName = 'clerk'
                    result = random.randint(16, 25)
                    attack[SUIT_HP_COL][targetIndex] = result
                if atkType['group'] == SuitBattleGlobals.ATK_TGT_PRESIDENT:
                    newName = 'clubpres'
                    result = random.randint(16, 24)
                    attack[SUIT_HP_COL][targetIndex] = result
                if atkType['group'] == SuitBattleGlobals.ATK_TGT_CONFUSED:
                    newName = 'ovt'
                    result = 15
                    attack[SUIT_HP_COL][targetIndex] = result

                self.transformUnstableCog(theSuit, result, newName)
                self.setSuitCondition(theSuit.doId, 'unstableTransform', 1, 1, 'setBoth')

            elif atkType['name'] == 'ForemanExtortion':
                result = random.randint(20, 25)
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'extortioncalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'ForemanPolish':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'immune', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'refinementcalculator', 0, 0, 'setBoth')
                for suit in self.battle.activeSuits:
                    self.setSuitCondition(suit.doId, 'oilRain', 1, 3, 'setBoth')
                    self.setSuitCondition(suit.doId, 'alreadyOilRain', 1, 1, 'setBoth')
                    self.setSuitCondition(suit.doId, 'directorDamageReduction', .9, 3, 'setBoth')
                    if self.suitHasCondition(suit.doId, 'sued'):
                        self.setSuitCondition(suit.doId, 'sued', 1, 1, 'setBoth')
                        self.setSuitCondition(suit.doId, 'suemovie', 0, 0, 'setBoth')
                    self.setSuitCondition(suit.doId, 'soaked', 0, 0, 'setBoth')
                    self.setSuitCondition(suit.doId, 'drenched', 0, 0, 'setBoth')
                    self.setSuitCondition(suit.doId, 'suemovie', 0, 0, 'setBoth')
                    if suit.dna.name in ('wtapper', 'bkeeper', 'phouse', 'ambass'):
                        if suit.currHP <= 0:
                            continue
                        x = (suit.maxHP * suit.hardMaxHP) - suit.currHP
                        if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
                            suit.setHP(suit.currHP + 0)
                        elif suit.currHP + 200 > (suit.maxHP * suit.hardMaxHP):
                            suit.setHP(suit.currHP + x)
                        else:
                            suit.setHP(suit.currHP + 200)
                    else:
                        if suit.currHP <= 0:
                            continue
                        x = (suit.maxHP * suit.hardMaxHP) - suit.currHP
                        if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
                            suit.setHP(suit.currHP + 0)
                        elif suit.currHP + 175 > (suit.maxHP * suit.hardMaxHP):
                            suit.setHP(suit.currHP + x)
                        else:
                            suit.setHP(suit.currHP + 175)
            elif atkType['name'] == 'ForemanSnipe':
                if self.toonHasCondition(toon.doId, 'noFires') and self.toonHasCondition(toon.doId, 'contingencyHit'):
                    self.setToonCondition(toon.doId, 'contingencyHit', 0, 0, 'setBoth')
                    result = 25
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'ForemanRedTape':
                result = 25
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'noSOS', 1, 3, 'setBoth')
                self.setToonCondition(toon.doId, 'noFires', 1, 3, 'setBoth')
               # self.setToonCondition(toon.doId, 'noUnites', 1, 3, 'setBoth')
                self.setToonCondition(toon.doId, 'noSues', 1, 3, 'setBoth')
            elif atkType['name'] == 'AttorneyChrono':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for suit in self.battle.activeSuits:
                    if not self.suitHasCondition(theSuit.doId, 'battleSpeed'):
                        self.setSuitCondition(suit.doId, 'battleSpeed', 1.5, -1, 'setBoth')
                    else:
                        self.setSuitCondition(suit.doId, 'battleSpeed', (self.getSuitConditionModifier(theSuit.doId, 'battleSpeed') + .5), -1, 'setBoth')
            elif atkType['name'] == 'PacesetterContentSync':
                result = random.randint(1, 8)

                attack[SUIT_HP_COL][targetIndex] = result

                syncCond = 'contentSync%s' % result

                self.battle.nextContentSyncOrderCondition = syncCond

                for t in self.battle.activeToons:

                    for cond in self.calculator.CONTENT_SYNC_CONDITION_ORDERS.keys():
                        self.setToonCondition(t, cond, 0, 0, 'setBoth')

                    self.setToonCondition(t, syncCond, 1, -1, 'setBoth')
            elif atkType['name'] == 'PacesetterMovingGoalposts':
                result = 0

                attack[SUIT_HP_COL][targetIndex] = result

                self.applyRandomSpecificGagBans(toonId, turns=2)
                self.setSuitCondition(theSuit.doId, 'alreadyMoving', 1, -1, 'setBoth')
            elif atkType['name'] == 'PacesetterComeOn':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for suit in self.battle.activeSuits:
                    if not self.suitHasCondition(theSuit.doId, 'battleSpeed'):
                        self.setSuitCondition(suit.doId, 'battleSpeed', 1.25, -1, 'setBoth')
                    else:
                        self.setSuitCondition(suit.doId, 'battleSpeed', (self.getSuitConditionModifier(theSuit.doId, 'battleSpeed') + .25), -1, 'setBoth')
            elif atkType['name'] == 'PacesetterOverclocked':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'overclocked', 1, -1, 'setBoth')
            elif atkType['name'] == 'PacesetterHurrySicknessBan':
                if self.toonHasCondition(toon.doId, 'banned'):
                    self.setToonCondition(toon.doId, 'allGagBoost', -40, 2, 'setBoth')
                    self.setToonCondition(toon.doId, 'lureBoost', -40, 2, 'setBoth')
                    if not self.suitHasCondition(theSuit.doId, 'alreadyHurrySickness'):
                        self.calculator.hurrySicknessDamage += 10
                    result = self.calculator.hurrySicknessDamage
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'PacesetterHurrySickness':
                if self.suitHasCondition(theSuit.doId, 'alreadyMoving'):
                    self.applyRandomSpecificGagBans(toon.doId, turns=2)
                doHurrySickness = 0
                for suit in self.battle.activeSuits:
                    rushJobConditions = (
                        'trapRushJob',
                        'lureRushJob',
                        'throwRushJob',
                        'squirtRushJob',
                        'zapRushJob',
                        'soundRushJob',
                        'dropRushJob',
                    )
                    if any(self.suitHasCondition(suit.doId, cond)
                        for cond in rushJobConditions) and suit.currHP > 0:
                        doHurrySickness = 1

                    # # TODO: Replace old system with new status effect system.  Slowly, but surely...
                    # if len(self.getAllRelevantConditions(suit.doId, StatusEffects.RushJob, toon=False)) > 0: # Are there any existing Rush Jobs?
                    #     doHurrySickness = 1 # We want Hurry Sickness.  Personally, I don't think this is ideal, but it can stay for now.
                    #     break # We've checked all that we need.

                if doHurrySickness:
                    if not self.suitHasCondition(theSuit.doId, 'alreadyHurrySickness'):
                        self.calculator.hurrySicknessDamage += 10
                    result = self.calculator.hurrySicknessDamage
                    self.setToonCondition(toon.doId, 'allGagBoost', -40, 2, 'setBoth')
                    self.setToonCondition(toon.doId, 'lureBoost', -40, 2, 'setBoth')
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for suit in self.battle.activeSuits:
                    self.setSuitCondition(suit.doId, 'alreadyHurrySickness', 1, 1, 'setBoth')
            elif atkType['name'] == 'AttorneyShakedownCooldown':
                result = 25
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'noSOS', 1, 3, 'setBoth')
                self.setToonCondition(toon.doId, 'noFires', 1, 3, 'setBoth')
               # self.setToonCondition(toon.doId, 'noUnites', 1, 3, 'setBoth')
                self.setToonCondition(toon.doId, 'noSues', 1, 3, 'setBoth')
            elif atkType['name'] == 'AttorneyShakedownVulnerable':
                result = 15
                attack[SUIT_HP_COL][targetIndex] = result
                if self.getToonConditionModifier(toonId, 'markedwood') > 1.25:
                    self.setToonCondition(toon.doId, 'markedwood', self.getToonConditionModifier(toonId, 'markedwood'), 3, 'setBoth')
                else:
                    self.setToonCondition(toon.doId, 'markedwood', 1.25, 3, 'setBoth')
            elif atkType['name'] == 'AttorneyInkDrain':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'inkDraincalculator', 0, 0, 'setBoth')
                if self.getToonConditionModifier(toonId, 'allGagBoost2') < -10:
                    self.setToonCondition(toon.doId, 'allGagBoost2',
                                          self.getToonConditionModifier(toonId, 'allGagBoost2'), 2, 'setBoth')
                    self.setToonCondition(toon.doId, 'lureBoost2',
                                          self.getToonConditionModifier(toonId, 'lureBoost2'), 2, 'setBoth')
                else:
                    self.setToonCondition(toon.doId, 'allGagBoost2', -10, 2, 'setBoth')
                    self.setToonCondition(toon.doId, 'lureBoost2', -10, 2, 'setBoth')
            elif atkType['name'] == 'AttorneyDrainingPower':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                theSuit.setDamageMultiplier(theSuit.getDamageMultiplier() * 1.15)
            elif atkType['name'] == 'RushJobTrap':
                result = self.getSuitConditionModifier(theSuit.doId, 'targetCheckCondition')
                attack[SUIT_HP_COL][targetIndex] = result
                targetSuit = self.battle.activeSuits[result]
                self.setSuitCondition(targetSuit.doId, 'trapRushJob', 1, 2, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'laborious', 1, 2, 'setBoth')
                self.__removeLured(targetSuit.doId)
                self.setSuitCondition(targetSuit.doId, 'lured', 0, 0, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'unlureSuit', 0, 0, 'setBoth')
                if self.suitHasCondition(targetSuit.doId, 'sued'):
                    self.setSuitCondition(targetSuit.doId, 'sued', 1, 1, 'setBoth')
                if self.suitHasCondition(targetSuit.doId, 'marked'):
                    self.setSuitCondition(targetSuit.doId, 'marked', 1, 1, 'setBoth')
                if self.suitHasCondition(targetSuit.doId, 'soaked'):
                    self.setSuitCondition(targetSuit.doId, 'soaked', 1, 1, 'setBoth')
                if self.suitHasCondition(targetSuit.doId, 'drenched'):
                    self.setSuitCondition(targetSuit.doId, 'drenched', 1, 1, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'zapped', 0, 0, 'setBoth')
            elif atkType['name'] == 'RushJobLure':
                result = self.getSuitConditionModifier(theSuit.doId, 'targetCheckCondition')
                attack[SUIT_HP_COL][targetIndex] = result
                targetSuit = self.battle.activeSuits[result]
                self.setSuitCondition(targetSuit.doId, 'lureRushJob', 1, 2, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'laborious', 1, 2, 'setBoth')
                self.__removeLured(targetSuit.doId)
                self.setSuitCondition(targetSuit.doId, 'lured', 0, 0, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'unlureSuit', 0, 0, 'setBoth')
                if self.suitHasCondition(targetSuit.doId, 'sued'):
                    self.setSuitCondition(targetSuit.doId, 'sued', 1, 1, 'setBoth')
                if self.suitHasCondition(targetSuit.doId, 'marked'):
                    self.setSuitCondition(targetSuit.doId, 'marked', 1, 1, 'setBoth')
                if self.suitHasCondition(targetSuit.doId, 'soaked'):
                    self.setSuitCondition(targetSuit.doId, 'soaked', 1, 1, 'setBoth')
                if self.suitHasCondition(targetSuit.doId, 'drenched'):
                    self.setSuitCondition(targetSuit.doId, 'drenched', 1, 1, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'zapped', 0, 0, 'setBoth')
            elif atkType['name'] == 'RushJobThrow':
                result = self.getSuitConditionModifier(theSuit.doId, 'targetCheckCondition')
                attack[SUIT_HP_COL][targetIndex] = result
                targetSuit = self.battle.activeSuits[result]
                self.setSuitCondition(targetSuit.doId, 'throwRushJob', 1, 2, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'laborious', 1, 2, 'setBoth')
                self.__removeLured(targetSuit.doId)
                self.setSuitCondition(targetSuit.doId, 'lured', 0, 0, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'unlureSuit', 0, 0, 'setBoth')
                if self.suitHasCondition(targetSuit.doId, 'sued'):
                    self.setSuitCondition(targetSuit.doId, 'sued', 1, 1, 'setBoth')
                if self.suitHasCondition(targetSuit.doId, 'marked'):
                    self.setSuitCondition(targetSuit.doId, 'marked', 1, 1, 'setBoth')
                if self.suitHasCondition(targetSuit.doId, 'soaked'):
                    self.setSuitCondition(targetSuit.doId, 'soaked', 1, 1, 'setBoth')
                if self.suitHasCondition(targetSuit.doId, 'drenched'):
                    self.setSuitCondition(targetSuit.doId, 'drenched', 1, 1, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'zapped', 0, 0, 'setBoth')
            elif atkType['name'] == 'RushJobSquirt':
                result = self.getSuitConditionModifier(theSuit.doId, 'targetCheckCondition')
                attack[SUIT_HP_COL][targetIndex] = result
                targetSuit = self.battle.activeSuits[result]
                self.setSuitCondition(targetSuit.doId, 'squirtRushJob', 1, 2, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'laborious', 1, 2, 'setBoth')
                self.__removeLured(targetSuit.doId)
                self.setSuitCondition(targetSuit.doId, 'lured', 0, 0, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'unlureSuit', 0, 0, 'setBoth')
                if self.suitHasCondition(targetSuit.doId, 'sued'):
                    self.setSuitCondition(targetSuit.doId, 'sued', 1, 1, 'setBoth')
                if self.suitHasCondition(targetSuit.doId, 'marked'):
                    self.setSuitCondition(targetSuit.doId, 'marked', 1, 1, 'setBoth')
                if self.suitHasCondition(targetSuit.doId, 'soaked'):
                    self.setSuitCondition(targetSuit.doId, 'soaked', 1, 1, 'setBoth')
                if self.suitHasCondition(targetSuit.doId, 'drenched'):
                    self.setSuitCondition(targetSuit.doId, 'drenched', 1, 1, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'zapped', 0, 0, 'setBoth')
            elif atkType['name'] == 'RushJobZap':
                result = self.getSuitConditionModifier(theSuit.doId, 'targetCheckCondition')
                attack[SUIT_HP_COL][targetIndex] = result
                targetSuit = self.battle.activeSuits[result]
                self.setSuitCondition(targetSuit.doId, 'zapRushJob', 1, 2, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'laborious', 1, 2, 'setBoth')
                self.__removeLured(targetSuit.doId)
                self.setSuitCondition(targetSuit.doId, 'lured', 0, 0, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'unlureSuit', 0, 0, 'setBoth')
                if self.suitHasCondition(targetSuit.doId, 'sued'):
                    self.setSuitCondition(targetSuit.doId, 'sued', 1, 1, 'setBoth')
                if self.suitHasCondition(targetSuit.doId, 'marked'):
                    self.setSuitCondition(targetSuit.doId, 'marked', 1, 1, 'setBoth')
                if self.suitHasCondition(targetSuit.doId, 'soaked'):
                    self.setSuitCondition(targetSuit.doId, 'soaked', 1, 1, 'setBoth')
                if self.suitHasCondition(targetSuit.doId, 'drenched'):
                    self.setSuitCondition(targetSuit.doId, 'drenched', 1, 1, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'zapped', 0, 0, 'setBoth')
            elif atkType['name'] == 'RushJobSound':
                result = self.getSuitConditionModifier(theSuit.doId, 'targetCheckCondition')
                attack[SUIT_HP_COL][targetIndex] = result
                targetSuit = self.battle.activeSuits[result]
                self.setSuitCondition(targetSuit.doId, 'soundRushJob', 1, 2, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'laborious', 1, 2, 'setBoth')
                self.__removeLured(targetSuit.doId)
                self.setSuitCondition(targetSuit.doId, 'lured', 0, 0, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'unlureSuit', 0, 0, 'setBoth')
                if self.suitHasCondition(targetSuit.doId, 'sued'):
                    self.setSuitCondition(targetSuit.doId, 'sued', 1, 1, 'setBoth')
                if self.suitHasCondition(targetSuit.doId, 'marked'):
                    self.setSuitCondition(targetSuit.doId, 'marked', 1, 1, 'setBoth')
                if self.suitHasCondition(targetSuit.doId, 'soaked'):
                    self.setSuitCondition(targetSuit.doId, 'soaked', 1, 1, 'setBoth')
                if self.suitHasCondition(targetSuit.doId, 'drenched'):
                    self.setSuitCondition(targetSuit.doId, 'drenched', 1, 1, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'zapped', 0, 0, 'setBoth')
            elif atkType['name'] == 'RushJobDrop':
                result = self.getSuitConditionModifier(theSuit.doId, 'targetCheckCondition')
                attack[SUIT_HP_COL][targetIndex] = result
                targetSuit = self.battle.activeSuits[result]
                self.setSuitCondition(targetSuit.doId, 'dropRushJob', 1, 2, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'laborious', 1, 2, 'setBoth')
                self.__removeLured(targetSuit.doId)
                self.setSuitCondition(targetSuit.doId, 'lured', 0, 0, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'unlureSuit', 0, 0, 'setBoth')
                if self.suitHasCondition(targetSuit.doId, 'sued'):
                    self.setSuitCondition(targetSuit.doId, 'sued', 1, 1, 'setBoth')
                if self.suitHasCondition(targetSuit.doId, 'marked'):
                    self.setSuitCondition(targetSuit.doId, 'marked', 1, 1, 'setBoth')
                if self.suitHasCondition(targetSuit.doId, 'soaked'):
                    self.setSuitCondition(targetSuit.doId, 'soaked', 1, 1, 'setBoth')
                if self.suitHasCondition(targetSuit.doId, 'drenched'):
                    self.setSuitCondition(targetSuit.doId, 'drenched', 1, 1, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'zapped', 0, 0, 'setBoth')
            elif atkType['name'] == 'AttorneyRemand':
                result = self.getSuitConditionModifier(theSuit.doId, 'targetCheckCondition')
                attack[SUIT_HP_COL][targetIndex] = result
                targetSuit = self.battle.activeSuits[result]
                theSuit.setHP(math.ceil(theSuit.currHP + math.ceil(targetSuit.maxHP / 4)))
                targetSuit.setHP(math.ceil(targetSuit.currHP - math.ceil(targetSuit.maxHP / 4)))
                if targetSuit.currHP <= 0:
                    if self.suitHasCondition(targetSuit.doId, 'overpressure'):
                        for s in self.battle.activeSuits:
                            if s.dna.name == 'safesupervis':
                                if self.suitHasCondition(targetSuit.doId, 'overpressureDeath'):
                                    self.setSuitCondition(s.doId, 'overpressureDeath2', 1, 1, 'setBoth')
                                elif self.suitHasCondition(targetSuit.doId, 'overpressureDeath2'):
                                    self.setSuitCondition(s.doId, 'overpressureDeath3', 1, 1, 'setBoth')
                                else:
                                    self.setSuitCondition(s.doId, 'overpressureDeath', 1, 1, 'setBoth')
                    if targetSuit.getSkeleRevives() >= 1:
                        targetSuit.useSkeleRevive()
                    self.__removeLured(targetSuit.doId)
                    if not self.suitHasCondition(targetSuit.doId, 'dead'):
                        self.calculator.deadSuits += 1
                        self.setSuitCondition(targetSuit.doId, 'dead', 1, -1, 'setBoth')
            elif atkType['name'] == 'MintUsury':
                result = self.getSuitConditionModifier(theSuit.doId, 'targetCheckCondition')
                attack[SUIT_HP_COL][targetIndex] = result
                targetSuit = self.battle.activeSuits[result]
                theSuit.setHP(math.ceil(theSuit.currHP + math.ceil(targetSuit.maxHP / 3)))
                targetSuit.setHP(math.ceil(targetSuit.currHP - math.ceil(targetSuit.maxHP / 3)))
                if targetSuit.currHP <= 0:
                    if self.suitHasCondition(targetSuit.doId, 'overpressure'):
                        for s in self.battle.activeSuits:
                            if s.dna.name == 'safesupervis':
                                if self.suitHasCondition(targetSuit.doId, 'overpressureDeath'):
                                    self.setSuitCondition(s.doId, 'overpressureDeath2', 1, 1, 'setBoth')
                                elif self.suitHasCondition(targetSuit.doId, 'overpressureDeath2'):
                                    self.setSuitCondition(s.doId, 'overpressureDeath3', 1, 1, 'setBoth')
                                else:
                                    self.setSuitCondition(s.doId, 'overpressureDeath', 1, 1, 'setBoth')
                    if targetSuit.getSkeleRevives() >= 1:
                        targetSuit.useSkeleRevive()
                    self.__removeLured(targetSuit.doId)
                    if not self.suitHasCondition(targetSuit.doId, 'dead'):
                        self.calculator.deadSuits += 1
                        self.setSuitCondition(targetSuit.doId, 'dead', 1, -1, 'setBoth')
            elif atkType['name'] == 'ForemanContributing':
                result = self.getSuitConditionModifier(theSuit.doId, 'targetCheckCondition')
                attack[SUIT_HP_COL][targetIndex] = result
                targetSuit = self.battle.activeSuits[result]
                targetSuit.setHP(math.ceil(targetSuit.currHP + int(math.ceil(theSuit.currHP * .1) * 4)))
                theSuit.setHP(math.ceil(theSuit.currHP - int(math.ceil(theSuit.currHP * .1))))
            elif atkType['name'] == 'ForemanContractor':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'partnered', 1, -1, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'partnered', 1, -1, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'alreadyContracted', 1, -1, 'setBoth')
            elif atkType['name'] == 'ForemanUnionized':
                result = int((len(self.battle.activeSuits) - self.deadSuits) - 1)
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'directorDamageReduction', (1 - (result * .1)), -1, 'setBoth')
                for suit in self.battle.activeSuits:
                    suit.setDamageMultiplier(suit.getDamageMultiplier() * 1.05)
            elif atkType['name'] == 'ForemanContractorDeath':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for toon in self.battle.activeToons:
                    self.setToonCondition(toon, 'partnered', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'partnered', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'alreadyContracted', 0, 0, 'setBoth')
            elif atkType['name'] == 'ForemanBurning':
                result = 25
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'smoked', 1, 3, 'setBoth')
            elif atkType['name'] == 'ForemanBurningDamage':
                for s in self.battle.suits:
                    if s.getManager():
                        self.setSuitCondition(s.doId, 'dotfinished', 1, 1, 'setBoth')
                if self.toonHasCondition(toon.doId, 'smoked'):
                    result = 30
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'ForemanSleepyOvercharge':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'sleepy', 0, 0, 'setBoth')
                theSuit.setHP(theSuit.currHP + 900)
            elif atkType['name'] == 'ForemanExplosion':
                result = 80
                attack[SUIT_HP_COL][targetIndex] = result
                for suit in self.battle.activeSuits:
                    suit.setHP(math.ceil(suit.currHP - 50))
                    if suit.getHP() <= 0:
                        self.calculator.deadSuits += 1
                        self.__removeLured(suit.doId)
                theSuit.setHP(0)
            elif atkType['name'] == 'ForemanCompensation':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                theSuit.setDamageMultiplier(theSuit.getDamageMultiplier() * 1.35)
                theSuit.setHP(theSuit.currHP + 225)
            elif atkType['name'] == 'ForemanCompensation2':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                theSuit.setDamageMultiplier(theSuit.getDamageMultiplier() * 1.70)
                theSuit.setHP(theSuit.currHP + 450)
            elif atkType['name'] == 'ForemanCompensation3':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                theSuit.setDamageMultiplier(theSuit.getDamageMultiplier() * 2.05)
                theSuit.setHP(theSuit.currHP + 675)
            elif atkType['name'] == 'ForemanCompensation4':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                theSuit.setDamageMultiplier(theSuit.getDamageMultiplier() * 2.4)
                theSuit.setHP(theSuit.currHP + 900)
            elif atkType['name'] == 'ForemanCompensation5':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                theSuit.setDamageMultiplier(theSuit.getDamageMultiplier() * 2.75)
                theSuit.setHP(theSuit.currHP + 1125)
            elif atkType['name'] == 'MintLifeInsurance':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                x = (theSuit.maxHP - theSuit.currHP)
                if theSuit.currHP >= theSuit.maxHP:
                    theSuit.setHP(theSuit.currHP + 0)
                elif theSuit.currHP + 225 > theSuit.maxHP:
                    theSuit.setHP(theSuit.currHP + x)
                else:
                    theSuit.setHP(theSuit.currHP + 225)
                if theSuit.getActualLevel() == 25:
                    theSuit.setDamageMultiplier(theSuit.getDamageMultiplier() * 1.1)
                else:
                    theSuit.setDamageMultiplier(theSuit.getDamageMultiplier() * 1.05)
            elif atkType['name'] == 'MintSynergy':
                result = 36
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'MintAbacusBelow15':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'below15', 1, 2, 'setBoth')
            elif atkType['name'] == 'MintAbacusAbove15':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'above15', 1, 2, 'setBoth')
            elif atkType['name'] == 'MintAccountant1':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, '1target', 1, 2, 'setBoth')
            elif atkType['name'] == 'MintAccountant2':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, '2targets', 2, 2, 'setBoth')
            elif atkType['name'] == 'MintAccountant3':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, '3targets', 3, 2, 'setBoth')
            elif atkType['name'] == 'MintAccountant4':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, '4targets', 4, 2, 'setBoth')
            elif atkType['name'] == 'MintAccountant5':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, '5targets', 5, 2, 'setBoth')
            elif atkType['name'] == 'MintScheming':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'lureResist', 1, -1, 'setBoth')
                # Check to see if the target Cog already has extra attacks.
                for i in range(len(self.suitStatusConditionsNew[theSuit.doId])):
                    if isinstance(self.suitStatusConditionsNew[theSuit.doId][i], StatusEffects.ExtraAttacks):  # Does this Cog have any extra attacks?
                        self.suitStatusConditionsNew[theSuit.doId][i].extraAttacks += 1  # Add one more attack.
                        break  # Stop the loop so that we do not go down to else.

                # The Cog does not have any extra attacks, so give them one.
                else:
                    self.suitStatusConditionsNew[theSuit.doId].append(StatusEffects.ExtraAttacks(1))
            elif atkType['name'] == 'MintAudit':
                if self.toonHasCondition(toon.doId, 'usedDrop'):
                    self.setToonCondition(toon.doId, 'disableDrop', 1, 2, 'setBoth')
                    self.setToonCondition(toon.doId, 'usedDrop', 1, 1, 'setBoth')
                if self.toonHasCondition(toon.doId, 'usedThrow'):
                    self.setToonCondition(toon.doId, 'disableThrow', 1, 2, 'setBoth')
                    self.setToonCondition(toon.doId, 'usedThrow', 1, 1, 'setBoth')
                if self.toonHasCondition(toon.doId, 'usedSquirt'):
                    self.setToonCondition(toon.doId, 'disableSquirt', 1, 2, 'setBoth')
                    self.setToonCondition(toon.doId, 'usedSquirt', 1, 1, 'setBoth')
                if self.toonHasCondition(toon.doId, 'usedSound'):
                    self.setToonCondition(toon.doId, 'disableSound', 1, 2, 'setBoth')
                    self.setToonCondition(toon.doId, 'usedSound', 1, 1, 'setBoth')
                if self.toonHasCondition(toon.doId, 'usedTrap'):
                    self.setToonCondition(toon.doId, 'disableTrap', 1, 2, 'setBoth')
                    self.setToonCondition(toon.doId, 'usedTrap', 1, 1, 'setBoth')
                if self.toonHasCondition(toon.doId, 'usedLure'):
                    self.setToonCondition(toon.doId, 'disableLure', 1, 2, 'setBoth')
                    self.setToonCondition(toon.doId, 'usedLure', 1, 1, 'setBoth')
                if self.toonHasCondition(toon.doId, 'usedHeal'):
                    self.setToonCondition(toon.doId, 'disableToonUp', 1, 2, 'setBoth')
                    self.setToonCondition(toon.doId, 'usedHeal', 1, 1, 'setBoth')
                if self.toonHasCondition(toon.doId, 'usedZap'):
                    self.setToonCondition(toon.doId, 'disableZap', 1, 2, 'setBoth')
                    self.setToonCondition(toon.doId, 'usedZap', 1, 1, 'setBoth')
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'MintMovingGoalposts':
                result = random.randint(1, 8)

                attack[SUIT_HP_COL][targetIndex] = result

                syncCond = 'contentSync%s' % result

                self.battle.nextContentSyncOrderCondition = syncCond

                for t in self.battle.activeToons:

                    for cond in self.calculator.CONTENT_SYNC_CONDITION_ORDERS.keys():
                        self.setToonCondition(t, cond, 0, 0, 'setBoth')

                    self.setToonCondition(t, syncCond, 1, -1, 'setBoth')
            elif atkType['name'] == 'AttorneyDizzy':
                self.setToonCondition(toon.doId, 'confused', 1, 2, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'whirlwindcalculator', 0, 0, 'setBoth')
                result = 25
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'MintLedger':
                self.setSuitCondition(theSuit.doId, 'soundcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'vulnerablevideographer', self.getSuitConditionModifier(theSuit.doId, 'vulnerablevideographer') * 1 + (math.ceil(.05 / len(self.battle.activeToons))), -1, 'setBoth')
                if self.toonHasCondition(toon.doId, 'usedSound'):
                    result = 50
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'MintLureResistance':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                if len(self.battle.activeSuits) >= 2:
                    targetSuit = self.battle.activeSuits[1]
                else:
                    targetSuit = None
                if len(self.battle.activeSuits) >= 4:
                    targetSuit2 = self.battle.activeSuits[3]
                else:
                    targetSuit2 = None
                if len(self.battle.activeSuits) >= 6:
                    targetSuit3 = self.battle.activeSuits[5]
                else:
                    targetSuit3 = None
                targetSuits = [s for s in (targetSuit, targetSuit2, targetSuit3) if s is not None]
                for target in targetSuits:
                    self.setSuitCondition(target.doId, 'lureImmune', 1, 1, 'setBoth')
                    self.__removeLured(target.doId)
                    self.setSuitCondition(target.doId, 'lured', 0, 0, 'setBoth')
                    self.setSuitCondition(target.doId, 'silhouetteUnlure', 1, 1, 'setBoth')
            elif atkType['name'] == 'MintLureResistance2':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                if len(self.battle.activeSuits) >= 3:
                    targetSuit = self.battle.activeSuits[2]
                else:
                    targetSuit = None
                if len(self.battle.activeSuits) >= 5:
                    targetSuit2 = self.battle.activeSuits[4]
                else:
                    targetSuit2 = None
                if len(self.battle.activeSuits) >= 7:
                    targetSuit3 = self.battle.activeSuits[6]
                else:
                    targetSuit3 = None
                targetSuits = [s for s in (targetSuit, targetSuit2, targetSuit3) if s is not None]
                for target in targetSuits:
                    self.setSuitCondition(target.doId, 'lureImmune', 1, 1, 'setBoth')
                    self.__removeLured(target.doId)
                    self.setSuitCondition(target.doId, 'lured', 0, 0, 'setBoth')
                    self.setSuitCondition(target.doId, 'silhouetteUnlure', 1, 1, 'setBoth')
            elif atkType['name'] == 'MintHurrySickness':
                if self.toonHasCondition(toon.doId, 'banned') or self.toonHasCondition(toon.doId, 'banned2'):
                    self.setToonCondition(toon.doId, 'banned2', 1, 1, 'setBoth')
                    self.setToonCondition(toon.doId, 'banned', 1, 1, 'setBoth')
                    self.setToonCondition(toon.doId, 'allGagBoost', -40, 2, 'setBoth')
                    self.setToonCondition(toon.doId, 'lureBoost', -40, 2, 'setBoth')
                    result = 50
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'MintFraudulentDamage':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                theSuit.setHP(theSuit.currHP - 158)
                if theSuit.currHP <= 0:
                    self.setSuitCondition(theSuit.doId, 'deathcheck', 1, -1, 'setBoth')
                    self.setSuitCondition(theSuit.doId, 'alreadyDeathCheck', 0, 0, 'setBoth')
            elif atkType['name'] == 'WhistleCompensation':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for suit in self.battle.activeSuits:
                    if suit.getHP() < suit.maxHP and suit.dna.name != 'whistleb':
                        suit.setDamageMultiplier(suit.getDamageMultiplier() * 1.05)
                        self.setSuitCondition(suit.doId, 'lureResist', 1, -1, 'setBoth')
            elif atkType['name'] in (
                    'AttorneyOverseer',
                    'AttorneyOverseerDrop',
                    'AttorneyOverseerSquirt',
                    'AttorneyOverseerThrow'
                ):
                result = math.ceil(self.comboDamage + self.knockbackDamage)
                attack[SUIT_HP_COL][targetIndex] = result
                theSuit.setHP(theSuit.currHP + result)
                self.setSuitCondition(theSuit.doId, 'overseerKB', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'overseerCombo', 0, 0, 'setBoth')
                self.comboDamage *= 0
                self.knockbackDamage *= 0
                toon.setHp(toon.hp + math.ceil(result))
            elif atkType['name'] == 'AttorneyHurrySickness':
                doHurrySickness = 0
                for suit in self.battle.activeSuits:
                    rushJobConditions = (
                        'trapRushJob',
                        'lureRushJob',
                        'throwRushJob',
                        'squirtRushJob',
                        'zapRushJob',
                        'soundRushJob',
                        'dropRushJob',
                    )
                    if any(self.suitHasCondition(suit.doId, cond)
                        for cond in rushJobConditions) and suit.currHP > 0:
                        doHurrySickness = 1

                    # TODO: Replace old system with new status effect system.  Slowly, but surely...
                    if len(self.getAllRelevantConditions(suit.doId, StatusEffects.RushJob, toon=False)) > 0: # Are there any existing Rush Jobs?
                        doHurrySickness = 1 # We want Hurry Sickness.  Personally, I don't think this is ideal, but it can stay for now.
                        break # We've checked all that we need.

                if doHurrySickness:
                    result = 35
                    self.setToonCondition(toon.doId, 'allGagBoost', -40, 2, 'setBoth')
                    self.setToonCondition(toon.doId, 'lureBoost', -40, 2, 'setBoth')
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for suit in self.battle.activeSuits:
                    self.setSuitCondition(suit.doId, 'alreadyHurrySickness', 1, 1, 'setBoth')
            elif atkType['name'] == 'AttorneyRushJob':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'laborious', 1, 2, 'setBoth')
                for t in self.battle.activeToons:
                    self.setToonCondition(t, random.choice(
                        ('useToonUp','useTrap', 'useLure', 'useThrow', 'useSquirt', 'useZap', 'useSound', 'useDrop',)), 1, 2, 'setBoth')
            elif atkType['name'] == 'AttorneyObjectionSustained':
                result = math.ceil(self.objectionDamage / 3)
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'attorneyKB', 0, 0, 'setBoth')
            elif atkType['name'] == 'AttorneyObjectionOverruled':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'attorneyKB', 0, 0, 'setBoth')
            elif atkType['name'] == 'PresidentSensational':
                result = self.getSuitConditionModifier(theSuit.doId, 'targetCheckCondition')
                attack[SUIT_HP_COL][targetIndex] = result
                targetSuit = self.battle.activeSuits[result]
                self.setSuitCondition(targetSuit.doId, 'guestVerse', 1, 1, 'setBoth')
            elif atkType['name'] == 'PresidentViralSensation':
                if self.toonHasCondition(toon.doId, 'viralSensation'):
                    result = 1
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'PresidentLiability2':
                if self.toonHasCondition(toon.doId, 'contingencyMarked') and self.toonHasCondition(toon.doId, 'contingencyHit'):
                    self.setToonCondition(toon.doId, 'contingencyHit', 0, 0, 'setBoth')
                    self.setSuitCondition(theSuit.doId, 'soakedcalculator', 0, 0, 'setBoth')
                    result = 20
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'PresidentLiability':
                self.setToonCondition(toon.doId, 'contingencyMarked', 1, 3, 'setBoth')
                result = 25
                attack[SUIT_HP_COL][targetIndex] = result
                if self.getToonConditionModifier(toonId, 'allGagBoost') > 25:
                    self.setToonCondition(toon.doId, 'allGagBoost',
                                          self.getToonConditionModifier(toonId, 'allGagBoost'), 3, 'setBoth')
                    self.setToonCondition(toon.doId, 'lureBoost',
                                          self.getToonConditionModifier(toonId, 'lureBoost'), 3, 'setBoth')
                else:
                    self.setToonCondition(toon.doId, 'allGagBoost', 25, 3, 'setBoth')
                    self.setToonCondition(toon.doId, 'lureBoost', 25, 3, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'papercutcalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'PresidentMandatoryFiling':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'dodgy', -100, 2, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'filingcalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'PresidentHighStakes':
                randomizer = random.randint(-99, 100)
                self.setToonCondition(toon.doId, 'allGagBoost', randomizer, 3, 'setBoth')
                self.setToonCondition(toon.doId, 'lureBoost', randomizer, 3, 'setBoth')
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'PresidentSyphon':
                result = random.randint(20, 25)
                attack[SUIT_HP_COL][targetIndex] = result
                theSuit.setHP(math.ceil(theSuit.currHP + result))
                self.setSuitCondition(theSuit.doId, 'extortioncalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'PresidentSnap':
                result = 30
                attack[SUIT_HP_COL][targetIndex] = result
                # if self.getToonConditionModifier(toonId, 'snapped') > 1.25:
                #     self.setToonCondition(toon.doId, 'snapped', self.getToonConditionModifier(toonId, 'snapped'), 3, 'setBoth')
                # else:
                #     self.setToonCondition(toon.doId, 'snapped', 1.25, 3, 'setBoth')
                # Search for if the Snapped effect exists.
                for i in range(len(self.toonStatusConditionsNew[toon.doId])):
                    if isinstance(self.toonStatusConditionsNew[toon.doId][i], StatusEffects.Snapped):
                        # We have a Snapped effect.
                        self.toonStatusConditionsNew[toon.doId][i].defenseMod = max(self.toonStatusConditionsNew[toon.doId][i].defenseMod, 1.25) # Set the defense modifier to whichever is greater.
                        self.toonStatusConditionsNew[toon.doId][i].setRoundsLeft(2)
                        break # Do not allow any more iterations.

                else: # It does not; add a new effect.
                    self.toonStatusConditionsNew[toon.doId].append(StatusEffects.Snapped(1.25))
            elif atkType['name'] in (
                        'HighStakesHeal',
                        'HighStakesTrap',
                        'HighStakesLure',
                        'HighStakesSound',
                        'HighStakesThrow',
                        'HighStakesSquirt',
                        'HighStakesZap',
                        'HighStakesDrop'
                    ):
                usedCondByAttack = {
                    'HighStakesHeal': 'usedHeal',
                    'HighStakesTrap': 'usedTrap',
                    'HighStakesLure': 'usedLure',
                    'HighStakesThrow': 'usedThrow',
                    'HighStakesSquirt': 'usedSquirt',
                    'HighStakesZap': 'usedZap',
                    'HighStakesSound': 'usedSound',
                    'HighStakesDrop': 'usedDrop'
                }

                usedCond = usedCondByAttack.get(atkType['name'])

                rollUse = random.randint(0, 100)
                if rollUse >= 50:
                    result = random.randint(-99, 100)
                    if result == 0:
                        continue
                    self.setToonCondition(toon.doId, 'highStakesBoost', result, 1, 'setBoth')


                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'PresidentDeepFreeze':
                result = 1
                attack[SUIT_HP_COL][targetIndex] = result
                for suit in self.battle.activeSuits:
                    self.setSuitCondition(suit.doId, 'deepfreeze', 1, 3, 'setBoth')
            elif atkType['name'] == 'PresidentPuzzling':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'confused', 1, 2, 'setBoth')
            elif atkType['name'] == 'PresidentTargetCheck':
                result = 0
                if theSuit.dna.name == 'clerk' and theSuit.getActualLevel() == 25:
                    self.setSuitCondition(theSuit.doId, 'targetCheckCondition', self.__getRandomValidTargetSuitDigitRushJob(), 1, 'setBoth')
                elif theSuit.dna.name == 'hustle':
                    self.setSuitCondition(theSuit.doId, 'targetCheckCondition', self.__getRandomValidTargetSuitDigitRushJob(), 1, 'setBoth')
                elif theSuit.dna.name == 'clerk':
                    self.setSuitCondition(theSuit.doId, 'targetCheckCondition', self.__getRandomValidTargetSuitDigitAttorney(excludeSuitId=theSuit.doId), 1, 'setBoth')
                elif theSuit.dna.name == 'psetter':
                    self.setSuitCondition(theSuit.doId, 'targetCheckCondition', self.__getRandomValidTargetSuitDigitRushJob(), 1, 'setBoth')
                elif theSuit.dna.name == 'foreman':
                    self.setSuitCondition(theSuit.doId, 'targetCheckCondition', self.__getRandomValidTargetSuitDigitAttorney(excludeSuitId=theSuit.doId), 1, 'setBoth')
                elif theSuit.dna.name == 'supervis':
                    self.setSuitCondition(theSuit.doId, 'targetCheckCondition', self.__getRandomValidTargetSuitDigitAttorney(excludeSuitId=theSuit.doId), 1, 'setBoth')
                else:
                    self.setSuitCondition(theSuit.doId, 'targetCheckCondition', self.__getRandomValidTargetSuitDigitPresident(excludeSuitId=theSuit.doId), 1, 'setBoth')
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'PresidentExtraTip':
                result = self.getSuitConditionModifier(theSuit.doId, 'targetCheckCondition')
                attack[SUIT_HP_COL][targetIndex] = result
                targetSuit = self.battle.activeSuits[result]
                targetSuit.setHP(targetSuit.currHP + 225)
                targetSuit.setDamageMultiplier(targetSuit.getDamageMultiplier() * 1.1)
                self.setSuitCondition(theSuit.doId, 'targetCheckCondition', -1, 0, 'setBoth')
                self.__removeLured(targetSuit.doId)
                self.setSuitCondition(targetSuit.doId, 'lured', 0, 0, 'setBoth')
                self.setSuitCondition(targetSuit.doId, 'unlureSuit', 0, 0, 'setBoth')
            elif atkType['name'] == 'PresidentExtraTip2':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'target7', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target6', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target5', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target4', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target3', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target2', 0, 0, 'setBoth')
                targetSuit = self.battle.activeSuits[2]
                targetSuit.setHP(targetSuit.currHP + 225)
                targetSuit.setDamageMultiplier(targetSuit.getDamageMultiplier() * 1.1)
                self.__removeLured(targetSuit.doId)
                if self.suitHasCondition(targetSuit.doId, 'lured'):
                    self.setSuitCondition(targetSuit.doId, 'lured', 0, 0, 'setBoth')
                    self.setSuitCondition(targetSuit.doId, 'unlureSuit', 0, 0, 'setBoth')
            elif atkType['name'] == 'PresidentExtraTip3':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'target7', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target6', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target5', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target4', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target3', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target2', 0, 0, 'setBoth')
                targetSuit = self.battle.activeSuits[3]
                targetSuit.setHP(targetSuit.currHP + 225)
                targetSuit.setDamageMultiplier(targetSuit.getDamageMultiplier() * 1.1)
                self.__removeLured(targetSuit.doId)
                if self.suitHasCondition(targetSuit.doId, 'lured'):
                    self.setSuitCondition(targetSuit.doId, 'lured', 0, 0, 'setBoth')
                    self.setSuitCondition(targetSuit.doId, 'unlureSuit', 0, 0, 'setBoth')
            elif atkType['name'] == 'PresidentExtraTip4':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'target7', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target6', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target5', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target4', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target3', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target2', 0, 0, 'setBoth')
                targetSuit = self.battle.activeSuits[4]
                targetSuit.setHP(targetSuit.currHP + 225)
                targetSuit.setDamageMultiplier(targetSuit.getDamageMultiplier() * 1.1)
                self.__removeLured(targetSuit.doId)
                if self.suitHasCondition(targetSuit.doId, 'lured'):
                    self.setSuitCondition(targetSuit.doId, 'lured', 0, 0, 'setBoth')
                    self.setSuitCondition(targetSuit.doId, 'unlureSuit', 0, 0, 'setBoth')
            elif atkType['name'] == 'PresidentExtraTip5':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'target7', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target6', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target5', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target4', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target3', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target2', 0, 0, 'setBoth')
                targetSuit = self.battle.activeSuits[5]
                targetSuit.setHP(targetSuit.currHP + 225)
                targetSuit.setDamageMultiplier(targetSuit.getDamageMultiplier() * 1.1)
                self.__removeLured(targetSuit.doId)
                if self.suitHasCondition(targetSuit.doId, 'lured'):
                    self.setSuitCondition(targetSuit.doId, 'lured', 0, 0, 'setBoth')
                    self.setSuitCondition(targetSuit.doId, 'unlureSuit', 0, 0, 'setBoth')
            elif atkType['name'] == 'PresidentExtraTip6':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'target7', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target6', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target5', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target4', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target3', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'target2', 0, 0, 'setBoth')
                targetSuit = self.battle.activeSuits[0]
                targetSuit.setHP(targetSuit.currHP + 225)
                targetSuit.setDamageMultiplier(targetSuit.getDamageMultiplier() * 1.1)
                self.__removeLured(targetSuit.doId)
                if self.suitHasCondition(targetSuit.doId, 'lured'):
                    self.setSuitCondition(targetSuit.doId, 'lured', 0, 0, 'setBoth')
                    self.setSuitCondition(targetSuit.doId, 'unlureSuit', 0, 0, 'setBoth')
            elif atkType['name'] == 'PresidentMulligan':
                roll = random.randint(0, 100)
                if roll > 15:
                    result = 36
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                if not self.suitHasCondition(theSuit.doId, 'alreadyMulligan'):
                    self.setSuitCondition(theSuit.doId, 'alreadyMulligan', 1, 1, 'setBoth')
                    if not self.suitHasCondition(theSuit.doId, 'mulligan'):
                        self.setSuitCondition(theSuit.doId, 'mulligan', 1, -1, 'setBoth')
                    elif self.suitHasCondition(theSuit.doId, 'mulligan') and not self.suitHasCondition(theSuit.doId, 'mulligan2') and self.getSuitConditionTurns(
                        theSuit.doId,
                        'mulligan') < 99:
                        self.setSuitCondition(theSuit.doId, 'mulligan2', 1, -1, 'setBoth')
                    elif self.suitHasCondition(theSuit.doId, 'mulligan2') and not self.suitHasCondition(theSuit.doId, 'mulligan3') and self.getSuitConditionTurns(
                        theSuit.doId,
                        'mulligan2') < 99:
                        self.setSuitCondition(theSuit.doId, 'mulligan3', 1, -1, 'setBoth')
                    elif self.suitHasCondition(theSuit.doId, 'mulligan3') and not self.suitHasCondition(theSuit.doId, 'mulligan4') and self.getSuitConditionTurns(
                        theSuit.doId,
                        'mulligan3') < 99:
                        self.setSuitCondition(theSuit.doId, 'mulligan4', 1, -1, 'setBoth')
                    elif self.suitHasCondition(theSuit.doId, 'mulligan4') and not self.suitHasCondition(theSuit.doId, 'mulligan5')and self.getSuitConditionTurns(
                        theSuit.doId,
                        'mulligan4') < 99:
                        self.setSuitCondition(theSuit.doId, 'mulligan5', 1, -1, 'setBoth')
                    elif self.suitHasCondition(theSuit.doId, 'mulligan5') and not self.suitHasCondition(theSuit.doId, 'mulligan6')and self.getSuitConditionTurns(
                        theSuit.doId,
                        'mulligan5') < 99:
                        self.setSuitCondition(theSuit.doId, 'mulligan6', 1, -1, 'setBoth')
                    elif self.suitHasCondition(theSuit.doId, 'mulligan6') and not self.suitHasCondition(theSuit.doId, 'mulligan7')and self.getSuitConditionTurns(
                        theSuit.doId,
                        'mulligan6') < 99:
                        self.setSuitCondition(theSuit.doId, 'mulligan7', 1, -1, 'setBoth')
                    elif self.suitHasCondition(theSuit.doId, 'mulligan7') and not self.suitHasCondition(theSuit.doId, 'mulligan8')and self.getSuitConditionTurns(
                        theSuit.doId,
                        'mulligan7') < 99:
                        self.setSuitCondition(theSuit.doId, 'mulligan8', 1, -1, 'setBoth')
                    elif self.suitHasCondition(theSuit.doId, 'mulligan8') and not self.suitHasCondition(theSuit.doId, 'mulligan9') and self.getSuitConditionTurns(
                        theSuit.doId,
                        'mulligan8') < 99:
                        self.setSuitCondition(theSuit.doId, 'mulligan9', 1, -1, 'setBoth')
                    elif self.suitHasCondition(theSuit.doId, 'mulligan9') and not self.suitHasCondition(theSuit.doId, 'mulligan10')and self.getSuitConditionTurns(
                        theSuit.doId,
                        'mulligan9') < 99:
                        self.setSuitCondition(theSuit.doId, 'mulligan10', 1, -1, 'setBoth')
            elif atkType['name'] == 'HighRollerLureResistance':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                if len(self.battle.activeSuits) >= 2:
                    targetSuit = self.battle.activeSuits[1]
                else:
                    targetSuit = None
                if len(self.battle.activeSuits) >= 4:
                    targetSuit2 = self.battle.activeSuits[3]
                else:
                    targetSuit2 = None
                if len(self.battle.activeSuits) >= 6:
                    targetSuit3 = self.battle.activeSuits[5]
                else:
                    targetSuit3 = None
                targetSuits = [s for s in (targetSuit, targetSuit2, targetSuit3) if s is not None]
                for target in targetSuits:
                    self.setSuitCondition(target.doId, 'lureImmune', 1, 1, 'setBoth')
                    self.__removeLured(target.doId)
                    self.setSuitCondition(target.doId, 'lured', 0, 0, 'setBoth')
                    self.setSuitCondition(target.doId, 'silhouetteUnlure', 1, 1, 'setBoth')
            elif atkType['name'] == 'HighRollerLureResistance2':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                if len(self.battle.activeSuits) >= 3:
                    targetSuit = self.battle.activeSuits[2]
                else:
                    targetSuit = None
                if len(self.battle.activeSuits) >= 5:
                    targetSuit2 = self.battle.activeSuits[4]
                else:
                    targetSuit2 = None
                if len(self.battle.activeSuits) >= 7:
                    targetSuit3 = self.battle.activeSuits[6]
                else:
                    targetSuit3 = None
                targetSuits = [s for s in (targetSuit, targetSuit2, targetSuit3) if s is not None]
                for target in targetSuits:
                    self.setSuitCondition(target.doId, 'lureImmune', 1, 1, 'setBoth')
                    self.__removeLured(target.doId)
                    self.setSuitCondition(target.doId, 'lured', 0, 0, 'setBoth')
                    self.setSuitCondition(target.doId, 'silhouetteUnlure', 1, 1, 'setBoth')
            elif atkType['name'] == 'HighRollerCheerRetaliation':
                if self.toonHasCondition(toon.doId, 'cheer'):
                    result = self.getToonConditionModifier(toon.doId, 'cheer')
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'HighRollerSingingBlues':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'winded', -50, 2, 'setBoth')
            elif atkType['name'] == 'HighRollerSyphon':
                result = random.randint(100, 200)
                attack[SUIT_HP_COL][targetIndex] = result
                theSuit.setHP(math.ceil(theSuit.currHP + attack[SUIT_HP_COL][
                    targetIndex]))
            elif atkType['name'] == 'HighRollerBar':
                result = 100
                attack[SUIT_HP_COL][targetIndex] = result
                self.__removeLured(theSuit.doId)
                for suit in self.battle.activeSuits:
                    if suit.dna.name == 'hroller2':
                        suit.setHP(math.ceil(suit.currHP - 25))
                        if suit.currHP <= 0:
                            if self.suitHasCondition(suit.doId, 'overpressure'):
                                for s in self.battle.activeSuits:
                                    if s.dna.name == 'safesupervis':
                                        if self.suitHasCondition(suit.doId, 'overpressureDeath'):
                                            self.setSuitCondition(s.doId, 'overpressureDeath2', 1, 1, 'setBoth')
                                        elif self.suitHasCondition(suit.doId, 'overpressureDeath2'):
                                            self.setSuitCondition(s.doId, 'overpressureDeath3', 1, 1, 'setBoth')
                                        else:
                                            self.setSuitCondition(s.doId, 'overpressureDeath', 1, 1, 'setBoth')
                            if suit.getSkeleRevives() >= 1:
                                suit.useSkeleRevive()
                            self.__removeLured(suit.doId)
                            if not self.suitHasCondition(suit.doId, 'dead'):
                                self.calculator.deadSuits += 1
                                self.setSuitCondition(suit.doId, 'dead', 1, -1, 'setBoth')
                    else:
                        suit.setHP(math.ceil(suit.currHP - 250))
                        if suit.currHP <= 0:
                            if self.suitHasCondition(suit.doId, 'overpressure'):
                                for s in self.battle.activeSuits:
                                    if s.dna.name == 'safesupervis':
                                        if self.suitHasCondition(suit.doId, 'overpressureDeath'):
                                            self.setSuitCondition(s.doId, 'overpressureDeath2', 1, 1, 'setBoth')
                                        elif self.suitHasCondition(suit.doId, 'overpressureDeath2'):
                                            self.setSuitCondition(s.doId, 'overpressureDeath3', 1, 1, 'setBoth')
                                        else:
                                            self.setSuitCondition(s.doId, 'overpressureDeath', 1, 1, 'setBoth')
                            if suit.getSkeleRevives() >= 1:
                                suit.useSkeleRevive()
                            self.__removeLured(suit.doId)
                            if not self.suitHasCondition(suit.doId, 'dead'):
                                self.calculator.deadSuits += 1
                                self.setSuitCondition(suit.doId, 'dead', 1, -1, 'setBoth')
                    continue
            elif atkType['name'] == 'HighRollerBar2':
                result = 100
                attack[SUIT_HP_COL][targetIndex] = result
                self.__removeLured(theSuit.doId)
                for suit in self.battle.activeSuits:
                    if suit.dna.name == 'hroller2':
                        suit.setHP(math.ceil(suit.currHP - 25))
                        if suit.currHP <= 0:
                            if self.suitHasCondition(suit.doId, 'overpressure'):
                                for s in self.battle.activeSuits:
                                    if s.dna.name == 'safesupervis':
                                        if self.suitHasCondition(suit.doId, 'overpressureDeath'):
                                            self.setSuitCondition(s.doId, 'overpressureDeath2', 1, 1, 'setBoth')
                                        elif self.suitHasCondition(suit.doId, 'overpressureDeath2'):
                                            self.setSuitCondition(s.doId, 'overpressureDeath3', 1, 1, 'setBoth')
                                        else:
                                            self.setSuitCondition(s.doId, 'overpressureDeath', 1, 1, 'setBoth')
                            if suit.getSkeleRevives() >= 1:
                                suit.useSkeleRevive()
                            self.__removeLured(suit.doId)
                            if not self.suitHasCondition(suit.doId, 'dead'):
                                self.calculator.deadSuits += 1
                                self.setSuitCondition(suit.doId, 'dead', 1, -1, 'setBoth')
                    else:
                        suit.setHP(math.ceil(suit.currHP - 250))
                        if suit.currHP <= 0:
                            if self.suitHasCondition(suit.doId, 'overpressure'):
                                for s in self.battle.activeSuits:
                                    if s.dna.name == 'safesupervis':
                                        if self.suitHasCondition(suit.doId, 'overpressureDeath'):
                                            self.setSuitCondition(s.doId, 'overpressureDeath2', 1, 1, 'setBoth')
                                        elif self.suitHasCondition(suit.doId, 'overpressureDeath2'):
                                            self.setSuitCondition(s.doId, 'overpressureDeath3', 1, 1, 'setBoth')
                                        else:
                                            self.setSuitCondition(s.doId, 'overpressureDeath', 1, 1, 'setBoth')
                            if suit.getSkeleRevives() >= 1:
                                suit.useSkeleRevive()
                            self.__removeLured(suit.doId)
                            if not self.suitHasCondition(suit.doId, 'dead'):
                                self.calculator.deadSuits += 1
                                self.setSuitCondition(suit.doId, 'dead', 1, -1, 'setBoth')
                    continue
            elif atkType['name'] == 'HighRollerDiceRouletteEveryone':
                result = 35
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'immune', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'HRdiceroulette', 1, 1, 'setBoth')
                for suit in self.battle.activeSuits:
                    if suit.dna.name == 'hroller2':
                        suit.setHP(math.ceil(suit.currHP - 25))
                        if suit.getHP() <= 0:
                            if not self.suitHasCondition(suit.doId, 'dead'):
                                self.setSuitCondition(suit.doId, 'deathcheck', 1, 1, 'setBoth')
                                self.setSuitCondition(suit.doId, 'alreadyDeathCheck', 0, 0, 'setBoth')
                                self.__removeLured(suit.doId)
                    else:
                        suit.setHP(math.ceil(suit.currHP - 250))
                        if suit.getHP() <= 0:
                            if not self.suitHasCondition(suit.doId, 'dead'):
                                self.setSuitCondition(suit.doId, 'deathcheck', 1, 1, 'setBoth')
                                self.setSuitCondition(suit.doId, 'alreadyDeathCheck', 0, 0, 'setBoth')
                                self.__removeLured(suit.doId)
                    if self.suitHasCondition(suit.doId, 'lured'):
                        self.setSuitCondition(suit.doId, 'lured', 0, 0, 'setBoth')
                    continue
            elif atkType['name'] == 'HighRollerDiceRouletteCogs':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'immune', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'HRdiceroulette', 1, 1, 'setBoth')
                for suit in self.battle.activeSuits:
                    if suit.dna.name == 'hroller2':
                        suit.setHP(math.ceil(suit.currHP - 25))
                        if suit.getHP() <= 0:
                            self.setSuitCondition(suit.doId, 'deathcheck', 1, 1, 'setBoth')
                            self.setSuitCondition(suit.doId, 'alreadyDeathCheck', 0, 0, 'setBoth')
                            self.__removeLured(suit.doId)
                    else:
                        suit.setHP(math.ceil(suit.currHP - 250))
                        if suit.getHP() <= 0:
                            self.setSuitCondition(suit.doId, 'deathcheck', 1, 1, 'setBoth')
                            self.setSuitCondition(suit.doId, 'alreadyDeathCheck', 0, 0, 'setBoth')
                            self.__removeLured(suit.doId)
                    if self.suitHasCondition(suit.doId, 'lured'):
                        self.setSuitCondition(suit.doId, 'lured', 0, 0, 'setBoth')
                    continue
            elif atkType['name'] == 'HighRollerDiceRouletteNobody':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'immune', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'HRdiceroulette', 1, 1, 'setBoth')
            elif atkType['name'] == 'HighRollerDiceRouletteToons':
                result = random.choice((30, 60, 120, 180, 240, 300))
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'immune', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'HRdiceroulette', 1, 1, 'setBoth')
            elif atkType['name'] == 'HighRollerDonation':
                managerTarget = None
                for suit in self.battle.activeSuits:
                    if self.battle.findSuit(suit.doId).getManager() and suit.dna.name != 'hrollers':
                        managerTarget = suit
                    if managerTarget == None:
                        managerTarget = theSuit
                if theSuit.currHP < 3000:
                    managerTarget.setHP(managerTarget.getHP() + theSuit.currHP)
                    theSuit.setHP(math.ceil(theSuit.currHP - theSuit.currHP))
                    if (theSuit.currHP - 3000) <= 0:
                        if self.suitHasCondition(theSuit.doId, 'overpressure'):
                            for s in self.battle.activeSuits:
                                if s.dna.name == 'safesupervis':
                                    if self.suitHasCondition(theSuit.doId, 'overpressureDeath'):
                                        self.setSuitCondition(s.doId, 'overpressureDeath2', 1, 1, 'setBoth')
                                    elif self.suitHasCondition(theSuit.doId, 'overpressureDeath2'):
                                        self.setSuitCondition(s.doId, 'overpressureDeath3', 1, 1, 'setBoth')
                                    else:
                                        self.setSuitCondition(s.doId, 'overpressureDeath', 1, 1, 'setBoth')
                        if theSuit.getSkeleRevives() >= 1:
                            theSuit.useSkeleRevive()
                        self.__removeLured(theSuit)
                        if not self.suitHasCondition(theSuit.doId, 'dead'):
                            self.calculator.deadSuits += 1
                            self.setSuitCondition(theSuit.doId, 'dead', 1, -1, 'setBoth')
                else:
                    managerTarget.setHP(managerTarget.getHP() + 3000)
                    theSuit.setHP(math.ceil(theSuit.currHP - 3000))
            elif atkType['name'] == 'HighRollerSplashback':
                result = self.getToonConditionModifier(toonId, 'soakToon')
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'HighRollerBust':
                if self.toonHasCondition(toon.doId, 'banned') or self.toonHasCondition(toon.doId, 'banned2'):
                    self.setToonCondition(toon.doId, 'banned2', 1, 1, 'setBoth')
                    self.setToonCondition(toon.doId, 'banned', 1, 1, 'setBoth')
                    result = 333
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'HighRollerCommercialBreak':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for suit in self.battle.activeSuits:
                    if suit.currHP <= 0:
                        continue
                    if suit.dna.name != 'hroller':
                        suit.setHP(suit.currHP - suit.currHP)
                    self.setSuitCondition(suit.doId, 'killedbyroller', 1, 2, 'setBoth')
                    if self.suitHasCondition(suit.doId, 'lured'):
                        self.setSuitCondition(suit.doId, 'lured', 0, 0, 'setBoth')
                    continue
                for suit in self.currentlyLuredSuits.keys():
                    self.__removeLured(suit)
            elif atkType['name'] == 'HighRollerDamageReduction':
                result = random.randint(1, 8)

                attack[SUIT_HP_COL][targetIndex] = result

                syncCond = 'contentSync%s' % result

                self.battle.nextContentSyncOrderCondition = syncCond

                for t in self.battle.activeToons:

                    for cond in self.calculator.CONTENT_SYNC_CONDITION_ORDERS.keys():
                        self.setToonCondition(t, cond, 0, 0, 'setBoth')

                    self.setToonCondition(t, syncCond, 1, -1, 'setBoth')
            elif atkType['name'] == 'HighRollerWheelSpin':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'HighRollerPuzzleBan':
                from toontown.suit.DistributedHighRollerBossAI import DistributedHighRollerBossAI

                boss = None
                for do in simbase.air.doId2do.values():
                    if isinstance(do, DistributedHighRollerBossAI):
                        for s in self.battle.activeSuits:
                            if s in do.activeSuits:
                                boss = do
                                break
                        for s in self.battle.activeSuits:
                            if s in do.activeSuits:
                                if s.dna.name == 'hroller':
                                    maxSuits = 7

                                    aliveCount = len(self.battle.activeSuits) - self.deadSuits
                                    spawnAmount = maxSuits - aliveCount

                                    for i in xrange(random.randint(1, 4)):
                                        boss.appendSuitsToBattle(boss.battleNumber, 'crfMinigame')

                                    break
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'gameovercalculator2', 1, 10, 'setBoth')
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'noSquirtGags', 1, 0, 'setBoth')
                    self.setToonCondition(t, 'noThrowGags', 1, 0, 'setBoth')
                    self.setToonCondition(t, 'noLureGags', 1, 0, 'setBoth')
                    self.setToonCondition(t, 'noDropGags', 1, 0, 'setBoth')
                    self.setToonCondition(t, 'noToonUpGags', 1, 0, 'setBoth')
                    self.setToonCondition(t, 'noTrapGags', 1, 0, 'setBoth')
                    self.setToonCondition(t, 'noZapGags', 1, 0, 'setBoth')
                    self.setToonCondition(t, 'noSoundGags', 1, 0, 'setBoth')
                    self.setToonCondition(t, random.choice(('noLureGags', 'noZapGags', 'noThrowGags')), 1, 2, 'setBoth')
                    self.setToonCondition(t, random.choice(('noSquirtGags', 'noSoundGags', 'noToonUpGags')), 1, 2, 'setBoth')
                    self.setToonCondition(t, random.choice(('noDropGags', 'noTrapGags')), 1, 2, 'setBoth')
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
                        self.setToonCondition(t, random.choice(('noSquirtGags', 'noSoundGags', 'noToonUpGags', 'noLureGags', 'noZapGags', 'noThrowGags', 'noDropGags', 'noTrapGags')), 1, 2, 'setBoth')
            elif atkType['name'] == 'HighRollerGameTimeSpawn':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'spawncalculator', 1, 1, 'setBoth')
                from toontown.suit.DistributedHighRollerBossAI import DistributedHighRollerBossAI

                boss = None
                for do in simbase.air.doId2do.values():
                    if isinstance(do, DistributedHighRollerBossAI):
                        for s in self.battle.activeSuits:
                            if s in do.activeSuits:
                                boss = do
                                break
                        for s in self.battle.activeSuits:
                            if s in do.activeSuits:
                                if s.dna.name == 'hroller':
                                    maxSuits = 7

                                    aliveCount = len(self.battle.activeSuits) - self.deadSuits
                                    spawnAmount = maxSuits - aliveCount

                                    for i in xrange(spawnAmount):
                                        boss.appendSuitsToBattle(boss.battleNumber, 'crf1')

                                    break
            elif atkType['name'] == 'HighRollerPhase2':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'phase3', 1, -1, 'setBoth')
                from toontown.suit.DistributedHighRollerBossAI import DistributedHighRollerBossAI

                boss = None
                for do in simbase.air.doId2do.values():
                    if isinstance(do, DistributedHighRollerBossAI):
                        for s in self.battle.activeSuits:
                            if s in do.activeSuits:
                                boss = do
                                break
                        for s in self.battle.activeSuits:
                            if s in do.activeSuits:
                                if s.dna.name == 'hroller':
                                    boss.appendSuitsToBattle(boss.battleNumber, 'videogPhase2')
                                    boss.appendSuitsToBattle(boss.battleNumber, 'cnd')
                                    boss.appendSuitsToBattle(boss.battleNumber, 'std')
                                    boss.appendSuitsToBattle(boss.battleNumber, 'mh')
            elif atkType['name'] == 'HighRollerPuzzle':
                from toontown.suit.DistributedHighRollerBossAI import DistributedHighRollerBossAI

                boss = None
                for do in simbase.air.doId2do.values():
                    if isinstance(do, DistributedHighRollerBossAI):
                        for s in self.battle.activeSuits:
                            if s in do.activeSuits:
                                boss = do
                                break
                        for s in self.battle.activeSuits:
                            if s in do.activeSuits:
                                if s.dna.name == 'hroller':
                                    maxSuits = 7

                                    aliveCount = len(self.battle.activeSuits) - self.deadSuits
                                    spawnAmount = maxSuits - aliveCount

                                    for i in xrange(random.randint(1, 4)):
                                        boss.appendSuitsToBattle(boss.battleNumber, 'crfMinigame')

                                    break
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'gameovercalculator', 1, 10, 'setBoth')
                for t in self.battle.activeToons:
                    self.setToonCondition(t, random.choice(
                        ('useToonUp','useTrap', 'useLure', 'useThrow', 'useSquirt', 'useZap', 'useSound', 'useDrop',)), 1, 2, 'setBoth')
            elif atkType['name'] == 'HighRollerGameOver':
                for suit in self.battle.activeSuits:
                    if suit.currHP <= 0:
                        continue
                    if suit.dna.name != 'hroller':
                        suit.setHP(suit.currHP - suit.currHP)
                    self.setSuitCondition(suit.doId, 'killedbyroller', 1, 2, 'setBoth')
                    if self.suitHasCondition(suit.doId, 'lured'):
                        self.setSuitCondition(suit.doId, 'lured', 0, 0, 'setBoth')
                    continue
                for suit in self.currentlyLuredSuits.keys():
                    self.__removeLured(suit)
                if not self.toonHasCondition(toon.doId, 'rushJobCompleted') or self.deadSuits != (len(self.battle.activeSuits) - 1):
                    result = 35
                    attack[SUIT_HP_COL][targetIndex] = result
                else:
                    result = 0
                    attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'gameovercalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'HighRollerGameOver2':
                for suit in self.battle.activeSuits:
                    if suit.currHP <= 0:
                        continue
                    if suit.dna.name != 'hroller':
                        suit.setHP(suit.currHP - suit.currHP)
                    self.setSuitCondition(suit.doId, 'killedbyroller', 1, 2, 'setBoth')
                    if self.suitHasCondition(suit.doId, 'lured'):
                        self.setSuitCondition(suit.doId, 'lured', 0, 0, 'setBoth')
                    continue
                for suit in self.currentlyLuredSuits.keys():
                    self.__removeLured(suit)
                if self.toonHasCondition(toon.doId, 'banned') or self.toonHasCondition(toon.doId, 'banned2') or self.deadSuits != (len(self.battle.activeSuits) - 1):
                    self.setToonCondition(toon.doId, 'banned2', 1, 1, 'setBoth')
                    self.setToonCondition(toon.doId, 'banned', 1, 1, 'setBoth')
                    result = 35
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'gameovercalculator2', 0, 0, 'setBoth')
            elif atkType['name'] == 'HighRollerGameTimeCog':
                self.setSuitCondition(theSuit.doId, 'gametimecalculator', 0, 0, 'setBoth')
                result = self.getSuitConditionModifier(theSuit.doId, 'targetCheckCondition')
                attack[SUIT_HP_COL][targetIndex] = result
                targetSuit = self.battle.activeSuits[result]
                x = (targetSuit.maxHP * targetSuit.hardMaxHP) - targetSuit.currHP
                targetSuit.setHP(math.ceil(targetSuit.currHP + x))
                self.__removeLured(targetSuit.doId)
                self.setSuitCondition(targetSuit.doId, 'bellowattack', 1, 1, 'setBoth')
            elif atkType['name'] == 'HighRollerGameTimeCog2':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'gametimecalculator', 0, 0, 'setBoth')
                result = self.getSuitConditionModifier(theSuit.doId, 'targetCheckCondition')
                attack[SUIT_HP_COL][targetIndex] = result
                targetSuit = self.battle.activeSuits[result]
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
                self.__removeLured(targetSuit.doId)
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
                self.__removeLured(targetSuit.doId)
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
                self.__removeLured(targetSuit.doId)
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
                self.__removeLured(targetSuit.doId)
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
                #self.setToonCondition(toon.doId, 'silhouettespawn', 1, -1, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'bashcalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'vulnerable', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'trickofthelight', 1, 2, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'HRdamagereduction', 1, -1, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'immune', 1, 2, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'dazed', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'sued', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'marked', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'soaked', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'drenched', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'suemovie', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'zapped', 0, 0, 'setBoth')
                if self.suitHasCondition(theSuit.doId, 'firsttrick') and self.getSuitConditionTurns(
                        theSuit.doId,
                        'firsttrick') < 97 and not self.suitHasCondition(theSuit.doId, 'secondtrick'):
                    self.setSuitCondition(theSuit.doId, 'secondtrick', 1, -1, 'setBoth')
                if self.suitHasCondition(theSuit.doId, 'secondtrick') and self.getSuitConditionTurns(
                        theSuit.doId,
                        'secondtrick') < 97 and not self.suitHasCondition(theSuit.doId, 'thirdtrick'):
                    self.setSuitCondition(theSuit.doId, 'thirdtrick', 1, -1, 'setBoth')
                if self.suitHasCondition(theSuit.doId, 'thirdtrick') and self.getSuitConditionTurns(
                        theSuit.doId,
                        'thirdtrick') < 97 and not self.suitHasCondition(theSuit.doId, 'fourthtruck'):
                    self.setSuitCondition(theSuit.doId, 'fourthtrick', 1, -1, 'setBoth')
                else:
                    self.setSuitCondition(theSuit.doId, 'firsttrick', 1, -1, 'setBoth')
                from toontown.suit.DistributedHighRollerBossAI import DistributedHighRollerBossAI

                boss = None
                for do in simbase.air.doId2do.values():
                    if isinstance(do, DistributedHighRollerBossAI):
                        for s in self.battle.activeSuits:
                            if s in do.activeSuits:
                                boss = do
                                break
                        for s in self.battle.activeSuits:
                            if s in do.activeSuits:
                                if s.dna.name == 'hroller2':
                                    selectedSpawns = self.calculator.getSilhouetteSpawns(6)

                                    for suitName in selectedSpawns:
                                        boss.appendSuitsToBattle(boss.battleNumber, suitName)
            elif atkType['name'] == 'FilmmakerBudgetCuts':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                #self.setSuitCondition(theSuit.doId, 'bashcalculator', 1, 10, 'setBoth')
                for t in self.battle.activeToons:
                    toon = self.battle.getToon(t)
                    toon.b_setHp(200)
                    toon.b_setMaxHp(200)
            elif atkType['name'] == 'HighRollerPhase3':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                #self.setSuitCondition(theSuit.doId, 'bashcalculator', 1, 10, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'phase3', 1, -1, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'HRdamagereduction', 1, -1, 'setBoth')
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'raisedAnte', 1250, -1, 'setBoth')
                    toon = self.battle.getToon(t)
                    toon.b_setHp(999)
                    toon.b_setMaxHp(999)
                from toontown.suit.DistributedHighRollerBossAI import DistributedHighRollerBossAI

                boss = None
                for do in simbase.air.doId2do.values():
                    if isinstance(do, DistributedHighRollerBossAI):
                        for s in self.battle.activeSuits:
                            if s in do.activeSuits:
                                boss = do
                                break
                        for s in self.battle.activeSuits:
                            if s in do.activeSuits:
                                if s.dna.name == 'hroller2':
                                    if not self.calculator.silhouetteSpawns:
                                        self.calculator.silhouetteSpawns = ['sil1', 'sil2', 'sil3', 'sil4', 'sil5', 'sil6', 'sil7', 'sil8', 'sil9', 'sil10', 'sil11', 'sil12']

                                        # Pick 6 unique silhouettes
                                    spawnCount = min(6, len(self.calculator.silhouetteSpawns))
                                    selectedSpawns = random.sample(self.calculator.silhouetteSpawns, spawnCount)

                                    for suitName in selectedSpawns:
                                        boss.appendSuitsToBattle(boss.battleNumber, suitName)
                                        self.calculator.silhouetteSpawns.remove(suitName)
            elif atkType['name'] == 'HighRollerRaisingTheAnte':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'HRfreecruise', 1, 1, 'setBoth')
            elif atkType['name'] == 'HighRollerConduction':
                roll = random.randint(0, 100)
                if roll >= 15:
                    result = 225
                else:
                    result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'HRconduction', 1, 1, 'setBoth')
            elif atkType['name'] == 'HighRollerRolled':
                result = random.randint(127, 172)
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'HRrolled', 1, 1, 'setBoth')
            elif atkType['name'] == 'HighRollerFreeCruise':
                result = 198
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'HRfreecruise', 1, 1, 'setBoth')
            elif atkType['name'] == 'HighRollerVulnerable':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'vulnerable', 1, 10, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'phase3', 1, -1, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'immune', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'HRdamagereduction', 0, 0, 'setBoth')
                self.calculator.silhouetteSpawns = ['sil1', 'sil2', 'sil3', 'sil4', 'sil5', 'sil6', 'sil7', 'sil8', 'sil9', 'sil10', 'sil11', 'sil12']
            elif atkType['name'] == 'HighRollerAceInTheHole':
                result = 193
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'aceInTheHole', 1, -1, 'setBoth')
                if self.getToonConditionModifier(toonId, 'snapped') > 1.15:
                    self.setToonCondition(toon.doId, 'snapped', self.getToonConditionModifier(toonId, 'snapped'), -1, 'setBoth')
                else:
                    self.setToonCondition(toon.doId, 'snapped', 1.15, -1, 'setBoth')
            elif atkType['name'] == 'VideographerRisingStars':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'immunecalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'immune', 0, 0, 'setBoth')
                # if not self.suitHasCondition(theSuit.doId, 'silspawn'):
                #     self.setToonCondition(toon.doId, 'silhouettespawn', 1, -1, 'setBoth')
                #     self.setSuitCondition(theSuit.doId, 'silspawn', 1, -1, 'setBoth')
                from toontown.suit.DistributedHighRollerBossAI import DistributedHighRollerBossAI

                boss = None
                for do in simbase.air.doId2do.values():
                    if isinstance(do, DistributedHighRollerBossAI):
                        for s in self.battle.activeSuits:
                            if s in do.activeSuits:
                                boss = do
                                break
                        for s in self.battle.activeSuits:
                            if s in do.activeSuits:
                                if s.dna.name == 'videog':
                                    boss.appendSuitsToBattle(boss.battleNumber, 'videog')
                                    boss.appendSuitsToBattle(boss.battleNumber, 'videog')
            elif atkType['name'] == 'VideographerRisingStars2':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'immunecalculator', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'immune', 0, 0, 'setBoth')
                from toontown.suit.DistributedHighRollerBossAI import DistributedHighRollerBossAI

                boss = None
                for do in simbase.air.doId2do.values():
                    if isinstance(do, DistributedHighRollerBossAI):
                        for s in self.battle.activeSuits:
                            if s in do.activeSuits:
                                boss = do
                                break
                        for s in self.battle.activeSuits:
                            if s in do.activeSuits:
                                if s.dna.name == 'videog':
                                    boss.appendSuitsToBattle(boss.battleNumber, 'videog2')
                                    boss.appendSuitsToBattle(boss.battleNumber, 'videog2')
            elif atkType['name'] == 'VideographerDirectorCuts':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'phase3', 1, -1, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'immune', 1, -1, 'setBoth')
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
                    if suit.dna.name == 'cnd2':
                        managerTarget = suit
                        if managerTarget.currHP <= 0:
                            continue
                        if managerTarget == None:
                            continue
                        managerTarget.setHP(0)
                        self.__removeLured(managerTarget.doId)
                from toontown.suit.DistributedHighRollerBossAI import DistributedHighRollerBossAI

                boss = None
                for do in simbase.air.doId2do.values():
                    if isinstance(do, DistributedHighRollerBossAI):
                        for s in self.battle.activeSuits:
                            if s in do.activeSuits:
                                boss = do
                                break
                        for s in self.battle.activeSuits:
                            if s in do.activeSuits:
                                if s.dna.name == 'videog':
                                    boss.appendSuitsToBattle(boss.battleNumber, 'fmaker')
                                    boss.appendSuitsToBattle(boss.battleNumber, 'cinema')
                                    boss.appendSuitsToBattle(boss.battleNumber, 'director')
                                    boss.appendSuitsToBattle(boss.battleNumber, 'choreo')
            elif atkType['name'] == 'VideographerRisingStarsSilhouette':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                from toontown.suit.DistributedHighRollerBossAI import DistributedHighRollerBossAI

                boss = None
                for do in simbase.air.doId2do.values():
                    if isinstance(do, DistributedHighRollerBossAI):
                        for s in self.battle.activeSuits:
                            if s in do.activeSuits:
                                boss = do
                                break
                        for s in self.battle.activeSuits:
                            if s in do.activeSuits:
                                if s.dna.name == 'videog':
                                    boss.appendSuitsToBattle(boss.battleNumber, 'videog4')
            elif atkType['name'] == 'VideographerDeath':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                theSuit.setHP(0)
                from toontown.suit.DistributedHighRollerBossAI import DistributedHighRollerBossAI

                boss = None
                for do in simbase.air.doId2do.values():
                    if isinstance(do, DistributedHighRollerBossAI):
                        for s in self.battle.activeSuits:
                            if s in do.activeSuits:
                                boss = do
                                break
                        for s in self.battle.activeSuits:
                            if s in do.activeSuits:
                                if s.dna.name == 'hroller':
                                    boss.appendSuitsToBattle(boss.battleNumber, 'hrollerPhase3')
                for suit in self.battle.activeSuits:
                    if suit.dna.name not in ('hroller2', 'videog'):
                        managerTarget = suit
                        if managerTarget.currHP <= 0:
                            continue
                        if managerTarget == None:
                            continue
                        self.setSuitCondition(managerTarget.doId, 'killedbyvideo', 1, 2, 'setBoth')
                        managerTarget.setHP(0)
                        self.__removeLured(managerTarget.doId)
            elif atkType['name'] == 'VideographerHardCut':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'disable4s', 1, 0, 'setBoth')
                    self.setToonCondition(t, 'disable5s', 1, 0, 'setBoth')
                    self.setToonCondition(t, 'disable6s', 1, 0, 'setBoth')
                    self.setToonCondition(t, 'disable7s', 1, 0, 'setBoth')
                    self.setToonCondition(t, 'disable8s', 1, 0, 'setBoth')
                    self.setToonCondition(t, random.choice(('disable4s', 'disable5s', 'disable6s')), 1, 2, 'setBoth')
                    self.setToonCondition(t, random.choice(('disable7s', 'disable8s')), 1, 2, 'setBoth')
            elif atkType['name'] == 'VideographerVideoStatic':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                managerTarget = None
                for suit in self.battle.activeSuits:
                    self.setSuitCondition(suit.doId, 'deadproducer', 1, -1, 'setBoth')
                    if suit.dna.name == 'videog':
                        managerTarget = suit
                        if managerTarget == None:
                            continue
                        self.setSuitCondition(managerTarget.doId, 'vulnerable', 1, -1, 'setBoth')
                        #self.setSuitCondition(managerTarget.doId, 'vulnerablevideographer', 1, -1, 'setBoth')
                        if theSuit.dna.name == 'bcaster':
                            if not self.suitHasCondition(managerTarget.doId, 'vulnerablevideographer'):
                                self.setSuitCondition(managerTarget.doId, 'vulnerablevideographer', 1.2, -1, 'setBoth')
                            else:
                                self.setSuitCondition(managerTarget.doId, 'vulnerablevideographer', (self.getSuitConditionModifier(managerTarget.doId, 'vulnerablevideographer') * 1.2), -1, 'setBoth')
                            managerTarget.setDamageMultiplier(managerTarget.getDamageMultiplier() * 1.2)
                        if theSuit.dna.name == 'director':
                            if not self.suitHasCondition(managerTarget.doId, 'vulnerablevideographer'):
                                self.setSuitCondition(managerTarget.doId, 'vulnerablevideographer', 1.05, -1, 'setBoth')
                            else:
                                self.setSuitCondition(managerTarget.doId, 'vulnerablevideographer', (self.getSuitConditionModifier(managerTarget.doId, 'vulnerablevideographer') * 1.05), -1, 'setBoth')
                            managerTarget.setDamageMultiplier(managerTarget.getDamageMultiplier() * 1.05)
                        if theSuit.dna.name == 'choreo':
                            if not self.suitHasCondition(managerTarget.doId, 'vulnerablevideographer'):
                                self.setSuitCondition(managerTarget.doId, 'vulnerablevideographer', 1.05, -1, 'setBoth')
                            else:
                                self.setSuitCondition(managerTarget.doId, 'vulnerablevideographer', (self.getSuitConditionModifier(managerTarget.doId, 'vulnerablevideographer') * 1.05), -1, 'setBoth')
                            managerTarget.setDamageMultiplier(managerTarget.getDamageMultiplier() * 1.05)
                        if theSuit.dna.name == 'cinema':
                            if not self.suitHasCondition(managerTarget.doId, 'vulnerablevideographer'):
                                self.setSuitCondition(managerTarget.doId, 'vulnerablevideographer', 1.05, -1, 'setBoth')
                            else:
                                self.setSuitCondition(managerTarget.doId, 'vulnerablevideographer', (self.getSuitConditionModifier(managerTarget.doId, 'vulnerablevideographer') * 1.05), -1, 'setBoth')
                            managerTarget.setDamageMultiplier(managerTarget.getDamageMultiplier() * 1.05)
                        if theSuit.dna.name == 'fmaker':
                            if not self.suitHasCondition(managerTarget.doId, 'vulnerablevideographer'):
                                self.setSuitCondition(managerTarget.doId, 'vulnerablevideographer', 1.05, -1, 'setBoth')
                            else:
                                self.setSuitCondition(managerTarget.doId, 'vulnerablevideographer', (self.getSuitConditionModifier(managerTarget.doId, 'vulnerablevideographer') * 1.05), -1, 'setBoth')
                            managerTarget.setDamageMultiplier(managerTarget.getDamageMultiplier() * 1.05)
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
                        managerTarget.setVirtual(1)
                    if suit.dna.name == 'std2':
                        managerTarget = suit
                        if managerTarget.currHP <= 0:
                            continue
                        if managerTarget == None:
                            continue
                        managerTarget.setHP(managerTarget.maxHP / 2)
                        managerTarget.setMaxHP(managerTarget.maxHP / 2)
                        managerTarget.setDamageMultiplier(managerTarget.getDamageMultiplier() * 1.5)
                        managerTarget.setVirtual(1)
                    if suit.dna.name == 'cnd2':
                        managerTarget = suit
                        if managerTarget.currHP <= 0:
                            continue
                        if managerTarget == None:
                            continue
                        managerTarget.setHP(managerTarget.maxHP / 2)
                        managerTarget.setMaxHP(managerTarget.maxHP / 2)
                        managerTarget.setDamageMultiplier(managerTarget.getDamageMultiplier() * 1.5)
                        managerTarget.setVirtual(1)
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
                            if (theSuit.currHP) <= 0:
                                if self.suitHasCondition(theSuit.doId, 'overpressure'):
                                    for s in self.battle.activeSuits:
                                        if s.dna.name == 'safesupervis':
                                            if self.suitHasCondition(theSuit.doId, 'overpressureDeath'):
                                                self.setSuitCondition(s.doId, 'overpressureDeath2', 1, 1, 'setBoth')
                                            elif self.suitHasCondition(theSuit.doId, 'overpressureDeath2'):
                                                self.setSuitCondition(s.doId, 'overpressureDeath3', 1, 1, 'setBoth')
                                            else:
                                                self.setSuitCondition(s.doId, 'overpressureDeath', 1, 1, 'setBoth')
                                if theSuit.getSkeleRevives() >= 1:
                                    theSuit.useSkeleRevive()
                                self.__removeLured(theSuit)
                                if not self.suitHasCondition(theSuit.doId, 'dead'):
                                    self.calculator.deadSuits += 1
                                    self.setSuitCondition(theSuit.doId, 'dead', 1, -1, 'setBoth')
                        else:
                            managerTarget.setHP(managerTarget.currHP + (theSuit.maxHP / 3))
                            theSuit.setHP(math.ceil(theSuit.currHP - (theSuit.maxHP / 3)))
                            if (theSuit.currHP) <= 0:
                                if self.suitHasCondition(theSuit.doId, 'overpressure'):
                                    for s in self.battle.activeSuits:
                                        if s.dna.name == 'safesupervis':
                                            if self.suitHasCondition(theSuit.doId, 'overpressureDeath'):
                                                self.setSuitCondition(s.doId, 'overpressureDeath2', 1, 1, 'setBoth')
                                            elif self.suitHasCondition(theSuit.doId, 'overpressureDeath2'):
                                                self.setSuitCondition(s.doId, 'overpressureDeath3', 1, 1, 'setBoth')
                                            else:
                                                self.setSuitCondition(s.doId, 'overpressureDeath', 1, 1, 'setBoth')
                                if theSuit.getSkeleRevives() >= 1:
                                    theSuit.useSkeleRevive()
                                self.__removeLured(theSuit)
                                if not self.suitHasCondition(theSuit.doId, 'dead'):
                                    self.calculator.deadSuits += 1
                                    self.setSuitCondition(theSuit.doId, 'dead', 1, -1, 'setBoth')
                self.__removeLured(theSuit.doId)
            elif atkType['name'] == 'BroadcasterDonation2':
                managerTarget = None
                for suit in self.battle.activeSuits:
                    if suit.dna.name == 'videog':
                        managerTarget = suit
                        if managerTarget.currHP <= 0:
                            continue
                        if managerTarget == None:
                            continue
                        if theSuit.currHP < 111:
                            managerTarget.setHP(managerTarget.currHP + theSuit.currHP)
                            theSuit.setHP(math.ceil(theSuit.currHP - theSuit.currHP))
                            if (theSuit.currHP) <= 0:
                                if self.suitHasCondition(theSuit.doId, 'overpressure'):
                                    for s in self.battle.activeSuits:
                                        if s.dna.name == 'safesupervis':
                                            if self.suitHasCondition(theSuit.doId, 'overpressureDeath'):
                                                self.setSuitCondition(s.doId, 'overpressureDeath2', 1, 1, 'setBoth')
                                            elif self.suitHasCondition(theSuit.doId, 'overpressureDeath2'):
                                                self.setSuitCondition(s.doId, 'overpressureDeath3', 1, 1, 'setBoth')
                                            else:
                                                self.setSuitCondition(s.doId, 'overpressureDeath', 1, 1, 'setBoth')
                                if theSuit.getSkeleRevives() >= 1:
                                    theSuit.useSkeleRevive()
                                self.__removeLured(theSuit)
                                if not self.suitHasCondition(theSuit.doId, 'dead'):
                                    self.calculator.deadSuits += 1
                                    self.setSuitCondition(theSuit.doId, 'dead', 1, -1, 'setBoth')
                                for suit in self.battle.activeSuits:
                                    self.setSuitCondition(suit.doId, 'deadpromotion', 1, -1, 'setBoth')
                        else:
                            managerTarget.setHP(managerTarget.currHP + 111)
                            theSuit.setHP(math.ceil(theSuit.currHP - 111))
                            if (theSuit.currHP) <= 0:
                                if self.suitHasCondition(theSuit.doId, 'overpressure'):
                                    for s in self.battle.activeSuits:
                                        if s.dna.name == 'safesupervis':
                                            if self.suitHasCondition(theSuit.doId, 'overpressureDeath'):
                                                self.setSuitCondition(s.doId, 'overpressureDeath2', 1, 1, 'setBoth')
                                            elif self.suitHasCondition(theSuit.doId, 'overpressureDeath2'):
                                                self.setSuitCondition(s.doId, 'overpressureDeath3', 1, 1, 'setBoth')
                                            else:
                                                self.setSuitCondition(s.doId, 'overpressureDeath', 1, 1, 'setBoth')
                                if theSuit.getSkeleRevives() >= 1:
                                    theSuit.useSkeleRevive()
                                self.__removeLured(theSuit)
                                if not self.suitHasCondition(theSuit.doId, 'dead'):
                                    self.calculator.deadSuits += 1
                                    self.setSuitCondition(theSuit.doId, 'dead', 1, -1, 'setBoth')
                                for suit in self.battle.activeSuits:
                                    self.setSuitCondition(suit.doId, 'deadpromotion', 1, -1, 'setBoth')
                self.__removeLured(theSuit.doId)
            elif atkType['name'] == 'BroadcasterViralSensation':
                result = 30
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'allGagBoost', 50, 2, 'setBoth')
                self.setToonCondition(toon.doId, 'lureBoost', 50, 2, 'setBoth')
            elif atkType['name'] == 'VideographerElectricShock':
                result = self.getSuitConditionModifier(theSuit.doId, 'targetCheckCondition')
                attack[SUIT_HP_COL][targetIndex] = result
                targetSuit = self.battle.activeSuits[result]
                self.setSuitCondition(theSuit.doId, 'electricshockcalculator', 0, 0, 'setBoth')
                if targetSuit.currHP <= 0:
                    continue
                x = (targetSuit.maxHP * targetSuit.hardMaxHP) - targetSuit.currHP
                targetSuit.setHP(math.ceil(targetSuit.currHP + x))
                self.__removeLured(targetSuit.doId)
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
            elif atkType['name'] == 'FilmmakerCameraRewind':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'filmmakercalculator', 0, 0, 'setBoth')
                for suit in self.battle.activeSuits:
                    if suit.currHP <= 0:
                          continue
                    if suit.currHP < suit.maxHP and suit.dna.name in ('director', 'fmaker', 'cinema'):
                        x = (suit.maxHP * suit.hardMaxHP) - suit.currHP
                        if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
                            suit.setHP(suit.currHP + 0)
                        elif suit.currHP + 125 > (suit.maxHP * suit.hardMaxHP):
                            suit.setHP(suit.currHP + x)
                        else:
                            suit.setHP(suit.currHP + 125)
                    if not suit.currHP < suit.maxHP and suit.dna.name in ('director', 'fmaker', 'cinema'):
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
            elif atkType['name'] == 'DirectorProductionBudget':
                result = self.directorMultiplier
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'costscalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'DirectorBudgetExpansion':
                self.directorMultiplier += (20 * self.deadSuits)
                result = self.directorMultiplier
                toon.setHp(toon.hp + result)
                attack[SUIT_HP_COL][targetIndex] = result
            elif atkType['name'] == 'DirectorCut':
                self.setToonCondition(toon.doId, 'allGagBoost2', -50, 2, 'setBoth')
                self.setToonCondition(toon.doId, 'lureBoost2', -50, 2, 'setBoth')
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
                #self.setSuitCondition(theSuit.doId, 'directorcalculator', 0, 0, 'setBoth')
                theSuit.setHP(math.ceil(theSuit.maxHP))
            elif atkType['name'] == 'DeathCheck':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for suit in self.battle.activeSuits:
                    self.setSuitCondition(suit.doId, 'alreadyDeathCheck', 1, 1, 'setBoth')
                    if suit.currHP <= 0:
                        self.__removeLured(suit.doId)
                        if not self.suitHasCondition(suit.doId, 'dead'):
                            self.calculator.deadSuits += 1
                            self.setSuitCondition(suit.doId, 'dead', 1, -1, 'setBoth')
            elif atkType['name'] == 'CogSpawn':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'cogSpawn', 1, -1, 'setBoth')
                for suit in self.battle.activeSuits:
                    self.setSuitCondition(suit.doId, 'alreadyCogSpawn2', 1, -1, 'setBoth')
            elif atkType['name'] == 'SueApplication':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'suemovie', 1, -1, 'setBoth')
            elif atkType['name'] == 'SueDamage':
                result = (theSuit.maxHP / 4)
                attack[SUIT_HP_COL][targetIndex] = result
                theSuit.setHP(math.ceil(theSuit.currHP - result))
                if (theSuit.currHP - result) <= 0:
                    if self.suitHasCondition(theSuit.doId, 'overpressure'):
                        for s in self.battle.activeSuits:
                            if s.dna.name == 'safesupervis':
                                if self.suitHasCondition(theSuit.doId, 'overpressureDeath'):
                                    self.setSuitCondition(s.doId, 'overpressureDeath2', 1, 1, 'setBoth')
                                elif self.suitHasCondition(theSuit.doId, 'overpressureDeath2'):
                                    self.setSuitCondition(s.doId, 'overpressureDeath3', 1, 1, 'setBoth')
                                else:
                                    self.setSuitCondition(s.doId, 'overpressureDeath', 1, 1, 'setBoth')
                    if theSuit.getSkeleRevives() >= 1:
                        theSuit.useSkeleRevive()
                    if not self.suitHasCondition(theSuit.doId, 'dead'):
                        self.calculator.deadSuits += 1
                        self.setSuitCondition(theSuit.doId, 'dead', 1, -1, 'setBoth')
                        if theSuit.getExecutive() or theSuit.getGovernaught():
                            levelAmount = theSuit.getActualLevel() * 9
                        else:
                            levelAmount = theSuit.getActualLevel() * 5

                        self.calculator.addLevelDamage(levelAmount)
            elif atkType['name'] == 'ZapMovie':
                result = self.getSuitConditionModifier(theSuit.doId, 'zapped')
                attack[SUIT_HP_COL][targetIndex] = result
                if self.suitHasCondition(theSuit.doId, 'zapped') and self.getSuitConditionTurns(theSuit.doId, 'zapped') == 1:
                    theSuit.setHP(math.ceil(theSuit.currHP - result))
                    self.setSuitCondition(theSuit.doId, 'zapped', 0, 0, 'setBoth')
                    if (theSuit.currHP) <= 0:
                        if theSuit.dna.name == 'cbutcher':
                            for s in self.battle.activeSuits:
                                if s.dna.name == 'rkeeper':
                                    self.setSuitCondition(s.doId, 'phantomDeath', 1, 2, 'setBoth')
                        if self.suitHasCondition(theSuit.doId, 'overpressure'):
                            for s in self.battle.activeSuits:
                                if s.dna.name == 'safesupervis':
                                    if self.suitHasCondition(theSuit.doId, 'overpressureDeath'):
                                        self.setSuitCondition(s.doId, 'overpressureDeath2', 1, 1, 'setBoth')
                                    elif self.suitHasCondition(theSuit.doId, 'overpressureDeath2'):
                                        self.setSuitCondition(s.doId, 'overpressureDeath3', 1, 1, 'setBoth')
                                    else:
                                        self.setSuitCondition(s.doId, 'overpressureDeath', 1, 1, 'setBoth')
                        if theSuit.getSkeleRevives() >= 1:
                            theSuit.useSkeleRevive()
                        if not self.suitHasCondition(theSuit.doId, 'dead'):
                            self.calculator.deadSuits += 1
                            self.setSuitCondition(theSuit.doId, 'dead', 1, -1, 'setBoth')
                            if theSuit.getExecutive() or theSuit.getGovernaught():
                                levelAmount = theSuit.getActualLevel() * 9
                            else:
                                levelAmount = theSuit.getActualLevel() * 5

                            self.calculator.addLevelDamage(levelAmount)
            elif atkType['name'] == 'SueRemoval':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'suemovie', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'sued', 0, 0, 'setBoth')
            elif atkType['name'] in (
                        'LureRemovalPreToon',
                        'LureRemoval',
                        'LureRemovalHeal',
                        'LureRemovalTrap',
                        'LureRemovalLure',
                        'LureRemovalSound',
                        'LureRemovalThrow',
                        'LureRemovalSquirt',
                        'LureRemovalZap',
                        'LureRemovalDrop'
                    ):
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'lured', 0, 0, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'unlureSuit', 0, 0, 'setBoth')
                self.__removeLured(theSuit.doId)
            elif atkType['name'] == 'SoakRemoval':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for suit in self.battle.activeSuits:
                    self.setSuitCondition(suit.doId, 'alreadySoakRemoval', 1, 1, 'setBoth')
            elif atkType['name'] == 'DrenchDecrement':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'drenched', 1, self.getSuitConditionTurns(theSuit.doId, 'drenched') - 1, 'setBoth')
            elif atkType['name'] == 'MarkRemoval':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for suit in self.battle.activeSuits:
                    self.setSuitCondition(suit.doId, 'alreadyMarkRemoval', 1, 1, 'setBoth')
            elif atkType['name'] == 'OilRemoval':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for suit in self.battle.activeSuits:
                    if self.suitHasCondition(suit.doId, 'oilRain'):
                        self.setSuitCondition(suit.doId, 'oilRain', 0, 0, 'setBoth')
                        self.setSuitCondition(suit.doId, 'soaked', 0, 0, 'setBoth')
                        self.setSuitCondition(suit.doId, 'drenched', 0, 0, 'setBoth')
                        self.setSuitCondition(suit.doId, 'alreadyOil', 1, 1, 'setBoth')
                        self.setSuitCondition(suit.doId, 'directorDamageReduction', 0, 0, 'setBoth')
            elif atkType['name'] == 'GovernaughtDeath':
                result = (5 * self.calculator.governaughtCogs)
                attack[SUIT_HP_COL][targetIndex] = result
                self.setToonCondition(toon.doId, 'governaughtBoost', (self.getToonConditionModifier(toonId, 'governaughtBoost') + (5 * self.calculator.governaughtCogs)), -1, 'setBoth')
                for suit in self.battle.activeSuits:
                    self.setSuitCondition(suit.doId, 'alreadyGovDeath', 1, 1, 'setBoth')
            elif atkType['name'] == 'Desperation':
                self.setSuitCondition(theSuit.doId, 'alreadyDesperation2', 1, -1, 'setBoth')
                managerTarget = None
                if not self.suitHasCondition(theSuit.doId, 'alreadyDesperation'):
                    for suit in self.battle.activeSuits:
                        self.setSuitCondition(suit.doId, 'alreadyDesperation', 1, -1, 'setBoth')
                        self.setSuitCondition(suit.doId, 'alreadyCogSpawn', 1, 1, 'setBoth')
                    self.setToonCondition(toon.doId, 'desperation', 1, -1, 'setBoth')
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'contentSync1', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'contentSync2', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'contentSync3', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'contentSync4', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'contentSync5', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'contentSync6', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'contentSync7', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'contentSync8', 0, 0, 'setBoth')
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
                    self.setToonCondition(t, 'disable4s', 1, 0, 'setBoth')
                    self.setToonCondition(t, 'disable5s', 1, 0, 'setBoth')
                    self.setToonCondition(t, 'disable6s', 1, 0, 'setBoth')
                    self.setToonCondition(t, 'disable7s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disable8s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableSquirt', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableThrow', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableToonUp', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableDrop', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableZap', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableLure', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableTrap', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableSound', 0, 0, 'setBoth')
                for suit in self.battle.activeSuits:
                    self.setSuitCondition(suit.doId, 'desperationcalculator', 1, 10, 'setBoth')
                    if self.battle.findSuit(suit.doId).getManager():
                        managerTarget = suit
                    if managerTarget == None:
                        managerTarget = theSuit
                from toontown.suit.DistributedLawbotBossAI import DistributedLawbotBossAI

                boss = None
                for do in simbase.air.doId2do.values():
                    if isinstance(do, DistributedLawbotBossAI):
                        for s in self.battle.activeSuits:
                            if s in do.activeSuits:
                                boss = do
                                break
                        for s in self.battle.activeSuits:
                            if s in do.activeSuits:
                                if (s.dna.name == 'lgator' or s.dna.name == 'stenog' or s.dna.name == 'caseman' or s.dna.name == 'sgoat') and s.getHP() <= 0:
                                    if not self.calculator.litigationSpawns:
                                        continue
                                    condition = random.choice(self.calculator.litigationSpawns)
                                    if condition == 1:
                                        self.calculator.litigationSpawns.remove(1)
                                        boss.appendSuitsToBattle(boss.battleNumber, 'lgator')
                                    elif condition == 2:
                                        self.calculator.litigationSpawns.remove(2)
                                        boss.appendSuitsToBattle(boss.battleNumber, 'stenog')
                                    elif condition == 3:
                                        self.calculator.litigationSpawns.remove(3)
                                        boss.appendSuitsToBattle(boss.battleNumber, 'caseman')
                                    elif condition == 4:
                                        self.calculator.litigationSpawns.remove(4)
                                        boss.appendSuitsToBattle(boss.battleNumber, 'sgoat')
                                    else:
                                        pass
                from toontown.suit.DistributedDirectorsAI import DistributedDirectorsAI

                boss = None
                for do in simbase.air.doId2do.values():
                    if isinstance(do, DistributedDirectorsAI):
                        for s in self.battle.activeSuits:
                            if s in do.activeSuits:
                                boss = do
                                break
                        for s in self.battle.activeSuits:
                            if s in do.activeSuits:
                                if s.dna.name in ('ambass', 'wtapper', 'bkeeper', 'phouse') and s.getHP() <= 0:
                                    if not self.calculator.litigationSpawns:
                                        continue
                                    condition = random.choice(self.calculator.litigationSpawns)
                                    if condition == 1:
                                        self.calculator.litigationSpawns.remove(1)
                                        boss.appendSuitsToBattle(boss.battleNumber, 'ambass')
                                    elif condition == 2:
                                        self.calculator.litigationSpawns.remove(2)
                                        boss.appendSuitsToBattle(boss.battleNumber, 'wtapper')
                                    elif condition == 3:
                                        self.calculator.litigationSpawns.remove(3)
                                        boss.appendSuitsToBattle(boss.battleNumber, 'bkeeper')
                                    elif condition == 4:
                                        self.calculator.litigationSpawns.remove(4)
                                        boss.appendSuitsToBattle(boss.battleNumber, 'phouse')
                                    else:
                                        pass
                from toontown.suit.DistributedBoardbotBossAI import DistributedBoardbotBossAI

                boss = None
                for do in simbase.air.doId2do.values():
                    if isinstance(do, DistributedBoardbotBossAI):
                        for s in self.battle.activeSuits:
                            if s in do.activeSuits:
                                boss = do
                                break
                        for s in self.battle.activeSuits:
                            if s in do.activeSuits:
                                if (s.dna.name == 'rkeeper' or s.dna.name == 'cdirector' or s.dna.name == 'dking' or s.dna.name == 'liquid') and s.getHP() <= 0:
                                    if not self.calculator.litigationSpawns:
                                        continue
                                    condition = random.choice(self.calculator.litigationSpawns)
                                    if condition == 1:
                                        self.calculator.litigationSpawns.remove(1)
                                        boss.appendSuitsToBattle(boss.battleNumber, 'cdirector')
                                    elif condition == 2:
                                        self.calculator.litigationSpawns.remove(2)
                                        boss.appendSuitsToBattle(boss.battleNumber, 'dking')
                                    elif condition == 3:
                                        self.calculator.litigationSpawns.remove(3)
                                        boss.appendSuitsToBattle(boss.battleNumber, 'rkeeper')
                                    elif condition == 4:
                                        self.calculator.litigationSpawns.remove(4)
                                        boss.appendSuitsToBattle(boss.battleNumber, 'liquid')
                                    else:
                                        pass
                from toontown.suit.DistributedSellbotBossMiniAI import DistributedSellbotBossMiniAI

                boss = None
                for do in simbase.air.doId2do.values():
                    if isinstance(do, DistributedSellbotBossMiniAI):
                        for s in self.battle.activeSuits:
                            if s in do.activeSuits:
                                boss = do
                                break
                        for s in self.battle.activeSuits:
                            if s in do.activeSuits:
                                if (s.dna.name == 'safesupervis' or s.dna.name == 'ubuster' or s.dna.name == 'hustle' or s.dna.name == 'radiog') and s.getHP() <= 0:
                                    if not self.calculator.litigationSpawns:
                                        continue
                                    condition = random.choice(self.calculator.litigationSpawns)
                                    if condition == 1:
                                        self.calculator.litigationSpawns.remove(1)
                                        boss.appendSuitsToBattle(boss.battleNumber, 'safesupervis')
                                    elif condition == 2:
                                        self.calculator.litigationSpawns.remove(2)
                                        boss.appendSuitsToBattle(boss.battleNumber, 'ubuster')
                                    elif condition == 3:
                                        self.calculator.litigationSpawns.remove(3)
                                        boss.appendSuitsToBattle(boss.battleNumber, 'racket')
                                    elif condition == 4:
                                        self.calculator.litigationSpawns.remove(4)
                                        boss.appendSuitsToBattle(boss.battleNumber, 'radiog')
                                    else:
                                        pass
            elif atkType['name'] == 'Desperation2':
                self.setSuitCondition(theSuit.doId, 'desperation', self.getSuitConditionModifier(theSuit.doId, 'desperation') + .4, -1, 'setBoth')
                self.setSuitCondition(theSuit.doId, 'desperationcalculator', 0, 0, 'setBoth')
            elif atkType['name'] == 'TargetCheck':
                result = 0
                if theSuit.dna.name == 'clubpres' and theSuit.getActualLevel() == 26:
                    self.setSuitCondition(theSuit.doId, 'targetCheckCondition', self.__getRandomValidTargetSuitDigitAttorney(excludeSuitId=theSuit.doId), 1, 'setBoth')
                elif theSuit.dna.name == 'erclaim':
                    self.setSuitCondition(theSuit.doId, 'targetCheckCondition', self.__getRandomValidTargetSuitDigitErclaim(excludeSuitId=theSuit.doId), 1, 'setBoth')
                elif theSuit.dna.name == 'erfit':
                    self.setSuitCondition(theSuit.doId, 'targetCheckCondition', self.__getErfitTargetByHPPercentSacrifice(excludeSuitId=theSuit.doId, mode='lowest'), 1, 'setBoth')
                elif theSuit.dna.name == 'videog':
                    self.setSuitCondition(theSuit.doId, 'targetCheckCondition', self.__getRandomValidTargetSuitDigitVideographer(excludeSuitId=theSuit.doId), 1, 'setBoth')
                else:
                    self.setSuitCondition(theSuit.doId, 'targetCheckCondition', self.__getRandomValidTargetSuitDigit(excludeSuitId=theSuit.doId), 1, 'setBoth')
                attack[SUIT_HP_COL][targetIndex] = result
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
            elif atkType['name'] == 'DisableLevel45':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'disable4s', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'disable5s', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'disable6s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disable7s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disable8s', 0, 0, 'setBoth')
            elif atkType['name'] == 'DisableLevel46':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'disable4s', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'disable5s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disable6s', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'disable7s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disable8s', 0, 0, 'setBoth')
            elif atkType['name'] == 'DisableLevel47':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'disable4s', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'disable5s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disable6s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disable7s', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'disable8s', 0, 0, 'setBoth')
            elif atkType['name'] == 'DisableLevel48':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'disable4s', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'disable5s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disable6s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disable7s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disable8s', 1, 2, 'setBoth')
            elif atkType['name'] == 'DisableLevel56':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'disable4s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disable5s', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'disable6s', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'disable7s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disable8s', 0, 0, 'setBoth')
            elif atkType['name'] == 'DisableLevel57':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'disable4s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disable5s', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'disable6s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disable7s', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'disable8s', 0, 0, 'setBoth')
            elif atkType['name'] == 'DisableLevel58':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'disable4s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disable5s', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'disable6s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disable7s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disable8s', 1, 2, 'setBoth')
            elif atkType['name'] == 'DisableLevel67':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'disable4s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disable5s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disable6s', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'disable7s', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'disable8s', 0, 0, 'setBoth')
            elif atkType['name'] == 'DisableLevel68':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'disable4s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disable5s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disable6s', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'disable7s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disable8s', 1, 2, 'setBoth')
            elif atkType['name'] == 'DisableLevel78':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'disable4s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disable5s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disable6s', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disable7s', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'disable8s', 1, 2, 'setBoth')
            elif atkType['name'] == 'DisableToonupTrap':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'disableToonUp', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'disableTrap', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'disableLure', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableThrow', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableSquirt', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableZap', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableSound', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableDrop', 0, 0, 'setBoth')
            elif atkType['name'] == 'DisableToonupLure':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'disableToonUp', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'disableTrap', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableLure', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'disableThrow', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableSquirt', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableZap', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableSound', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableDrop', 0, 0, 'setBoth')
            elif atkType['name'] == 'DisableToonupThrow':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'disableToonUp', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'disableTrap', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableLure', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableThrow', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'disableSquirt', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableZap', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableSound', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableDrop', 0, 0, 'setBoth')
            elif atkType['name'] == 'DisableToonupSquirt':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'disableToonUp', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'disableTrap', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableLure', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableThrow', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableSquirt', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'disableZap', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableSound', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableDrop', 0, 0, 'setBoth')
            elif atkType['name'] == 'DisableToonupZap':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'disableToonUp', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'disableTrap', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableLure', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableThrow', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableSquirt', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableZap', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'disableSound', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableDrop', 0, 0, 'setBoth')
            elif atkType['name'] == 'DisableToonupSound':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'disableToonUp', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'disableTrap', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableLure', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableThrow', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableSquirt', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableZap', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableSound', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'disableDrop', 0, 0, 'setBoth')
            elif atkType['name'] == 'DisableToonupDrop':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'disableToonUp', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'disableTrap', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableLure', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableThrow', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableSquirt', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableZap', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableSound', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableDrop', 1, 2, 'setBoth')
            elif atkType['name'] == 'DisableTrapLure':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'disableToonUp', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableTrap', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'disableLure', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'disableThrow', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableSquirt', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableZap', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableSound', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableDrop', 0, 0, 'setBoth')
            elif atkType['name'] == 'DisableTrapThrow':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'disableToonUp', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableTrap', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'disableLure', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableThrow', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'disableSquirt', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableZap', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableSound', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableDrop', 0, 0, 'setBoth')
            elif atkType['name'] == 'DisableTrapSquirt':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'disableToonUp', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableTrap', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'disableLure', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableThrow', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableSquirt', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'disableZap', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableSound', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableDrop', 0, 0, 'setBoth')
            elif atkType['name'] == 'DisableTrapZap':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'disableToonUp', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableTrap', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'disableLure', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableThrow', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableSquirt', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableZap', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'disableSound', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableDrop', 0, 0, 'setBoth')
            elif atkType['name'] == 'DisableTrapSound':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'disableToonUp', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableTrap', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'disableLure', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableThrow', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableSquirt', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableZap', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableSound', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'disableDrop', 0, 0, 'setBoth')
            elif atkType['name'] == 'DisableTrapDrop':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'disableToonUp', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableTrap', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'disableLure', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableThrow', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableSquirt', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableZap', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableSound', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableDrop', 1, 2, 'setBoth')
            elif atkType['name'] == 'DisableLureThrow':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'disableToonUp', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableTrap', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableLure', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'disableThrow', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'disableSquirt', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableZap', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableSound', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableDrop', 0, 0, 'setBoth')
            elif atkType['name'] == 'DisableLureSquirt':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'disableToonUp', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableTrap', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableLure', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'disableThrow', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableSquirt', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'disableZap', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableSound', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableDrop', 0, 0, 'setBoth')
            elif atkType['name'] == 'DisableLureZap':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'disableToonUp', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableTrap', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableLure', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'disableThrow', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableSquirt', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableZap', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'disableSound', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableDrop', 0, 0, 'setBoth')
            elif atkType['name'] == 'DisableLureSound':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'disableToonUp', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableTrap', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableLure', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'disableThrow', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableSquirt', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableZap', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableSound', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'disableDrop', 0, 0, 'setBoth')
            elif atkType['name'] == 'DisableLureDrop':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'disableToonUp', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableTrap', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableLure', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'disableThrow', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableSquirt', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableZap', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableSound', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableDrop', 1, 2, 'setBoth')
            elif atkType['name'] == 'DisableThrowSquirt':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'disableToonUp', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableTrap', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableLure', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableThrow', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'disableSquirt', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'disableZap', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableSound', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableDrop', 0, 0, 'setBoth')
            elif atkType['name'] == 'DisableThrowZap':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'disableToonUp', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableTrap', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableLure', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableThrow', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'disableSquirt', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableZap', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'disableSound', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableDrop', 0, 0, 'setBoth')
            elif atkType['name'] == 'DisableThrowSound':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'disableToonUp', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableTrap', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableLure', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableThrow', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'disableSquirt', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableZap', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableSound', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'disableDrop', 0, 0, 'setBoth')
            elif atkType['name'] == 'DisableThrowDrop':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'disableToonUp', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableTrap', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableLure', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableThrow', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'disableSquirt', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableZap', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableSound', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableDrop', 1, 2, 'setBoth')
            elif atkType['name'] == 'DisableSquirtZap':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'disableToonUp', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableTrap', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableLure', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableThrow', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableSquirt', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'disableZap', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'disableSound', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableDrop', 0, 0, 'setBoth')
            elif atkType['name'] == 'DisableSquirtSound':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'disableToonUp', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableTrap', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableLure', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableThrow', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableSquirt', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'disableZap', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableSound', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'disableDrop', 0, 0, 'setBoth')
            elif atkType['name'] == 'DisableSquirtDrop':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'disableToonUp', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableTrap', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableLure', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableThrow', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableSquirt', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'disableZap', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableSound', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableDrop', 1, 2, 'setBoth')
            elif atkType['name'] == 'DisableZapSound':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'disableToonUp', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableTrap', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableLure', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableThrow', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableSquirt', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableZap', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'disableSound', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'disableDrop', 0, 0, 'setBoth')
            elif atkType['name'] == 'DisableZapDrop':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'disableToonUp', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableTrap', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableLure', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableThrow', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableSquirt', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableZap', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'disableSound', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableDrop', 1, 2, 'setBoth')
            elif atkType['name'] == 'DisableSoundDrop':
                result = 0
                attack[SUIT_HP_COL][targetIndex] = result
                for t in self.battle.activeToons:
                    self.setToonCondition(t, 'disableToonUp', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableTrap', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableLure', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableThrow', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableSquirt', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableZap', 0, 0, 'setBoth')
                    self.setToonCondition(t, 'disableSound', 1, 2, 'setBoth')
                    self.setToonCondition(t, 'disableDrop', 1, 2, 'setBoth')
            elif atkType['name'] in (
                'GagBanRetaliationHeal',
                'GagBanRetaliationTrap',
                'GagBanRetaliationLure',
                'GagBanRetaliationThrow',
                'GagBanRetaliationSquirt',
                'GagBanRetaliationZap',
                'GagBanRetaliationSound',
                'GagBanRetaliationDrop'
            ):
                if self.toonHasCondition(toon.doId, 'banned') and not theSuit.dna.name == 'caseman' and not theSuit.dna.name == 'racket':
                    self.setToonCondition(toon.doId, 'banned', 0, 0, 'setBoth')
                    result = 50
                    if self.toonHasCondition(toonId, 'snapped'):
                        result *= self.getToonConditionModifier(toonId, 'snapped')
                    if self.toonHasCondition(toonId, 'bombedToon'):
                        result *= self.getToonConditionModifier(toonId, 'bombedToon')
                    if self.toonHasCondition(toonId, 'markedwood'):
                        result *= self.getToonConditionModifier(toonId, 'markedwood')
                    # Going to slowly replace individual status effects so we acclimate to the new system before moving onto a more sophisticated means of this.
                    for condition in self.toonStatusConditionsNew[toonId]:
                        if isinstance(condition, StatusEffects.Snapped):
                            result *= condition.defenseMod
                elif self.toonHasCondition(toon.doId, 'banned2') and not theSuit.dna.name == 'stenog':
                    self.setToonCondition(toon.doId, 'banned2', 0, 0, 'setBoth')
                    result = 50
                    if self.toonHasCondition(toonId, 'snapped'):
                        result *= self.getToonConditionModifier(toonId, 'snapped')
                    if self.toonHasCondition(toonId, 'bombedToon'):
                        result *= self.getToonConditionModifier(toonId, 'bombedToon')
                    if self.toonHasCondition(toonId, 'markedwood'):
                        result *= self.getToonConditionModifier(toonId, 'markedwood')
                    # Going to slowly replace individual status effects so we acclimate to the new system before moving onto a more sophisticated means of this.
                    for condition in self.toonStatusConditionsNew[toonId]:
                        if isinstance(condition, StatusEffects.Snapped):
                            result *= condition.defenseMod
                else:
                    result = 0
                if theSuit.dna.name == 'cdirector':
                    if result > 0:
                        self.setToonCondition(toon.doId, 'allGagBoost', -40, 2, 'setBoth')
                        self.setToonCondition(toon.doId, 'lureBoost', -40, 2, 'setBoth')
                attack[SUIT_HP_COL][targetIndex] = result
                self.setSuitCondition(theSuit.doId, 'bannedGagUsed', 0, 0, 'setBoth')
                for s in self.battle.suits:
                    if s.dna.name == 'phouse':
                        suit = s
                        currentBossHealth = s.currHP
                        if currentBossHealth >= 1:
                            self.setSuitCondition(suit.doId, 'gagbansnipe', 1, 10, 'setBoth')
            else:
                attack[SUIT_HP_COL][targetIndex] = result

            # Professor Control: I honestly do not know how to best approach this issue.  Especially in the case of damage over times, a Cog's ID is -1 because no Cog exists.  However, this sets theSuit to None, and the rest of this is treated as if a Cog exists.  So, this will have to do for the time being.
            try:
                DAMAGE_TOON_AND_STORE = (
                    'TollmasterMandatoryToll',
                    'WiretapperWiretapped,'
                    'PowerhouseToleranceBuilding',
                    'ScapegoatRageBuilding',
                    'ArbitratorThrowBook',
                    'PresidentExtraTip',
                    'ContingencyRiskThresholdBreach',
                    'ErclaimSacrifice',
                    'ErfitGainsFromTheScrap',
                    'PresidentSensational',
                    'HighRollerGameTimeCog',
                    'HighRollerGameTimeCog2',
                    'UnionBusterUnionBust',
                    'UnstableTransformation',
                    'RacketeerProfiteering',
                    'ForemanContributing',
                    'MintUsury',
                    'RushJobTrap',
                    'RushJobLure',
                    'RushJobThrow',
                    'RushJobSquirt',
                    'RushJobZap',
                    'RushJobSound',
                    'RushJobDrop',
                    'SafetyPromotion',
                    'SafetyOverpressured',
                    'RadiographerOvermodulated',
                    'RacketeerOverextendedLeverage',
                    'TollmasterMissedPayment',
                    'GovernaughtDeath',
                    'AmbassadorHeadRoller',
                    'ForemanUnionized',
                    'AttorneyRemand',
                    'VideographerElectricShock',
                    'MintMovingGoalposts',
                    'PacesetterContentSync',
                    'HighRollerDamageReduction',
                    'WiretapperWiretapped',
                    'TollmasterBalanceTheLedger',
                    'ContingencyOperationalFreeze',
                    'ButcherRevvingUp',
                    'HustlerBaitAndSwitch',
                    'ButcherRevvingUpWhipsaw',
                    'UnionBusterUnionCalculator',
                    'SafetyOverpressureDeath',
                    'ZapMovie',
                    'SueDamage',
                    'SafetyHeatWaveCalculation',
                )
                DAMAGE_STORE_ONLY = (
                    'TollmasterMandatoryTollFinal',
                    'ButcherSparkPlugDamage',
                    'RacketeerExtortion2',
                    'RecordkeeperMinutesTakenDamage',
                    'LiquidatorStormCellDamage',
                    'ButcherLayoffs',
                    'ButcherOffboarding',
                    'ButcherOffboarding2',
                    'ButcherOffboarding3',
                    'ButcherOffboarding4',
                    'ButcherOffboarding5',
                                         'CaseManagerLegallyBound',
                                         'DividendTotalMarketMeltdownDamage',
                             'RecordkeeperMinutesTaken',
                    'RecordkeeperMinutesTakenContingency',
                    'LiquidatorHeavyRainDamage',
                    'ForemanBurningDamage',
                    'AttorneyObjectionSustained',
                                        'RecordkeeperRedlinedClauseMissedPayment',
                    'PowerhouseGroundbreakerRevert',
                    'UnionBusterUnionBusterDamage',
                    'WiretapperGagBan',
                    'SafetyViolation',
                    'CaseManagerCourtRecordBan',
                )
                DESPERATION_AND_MULTIPLIER_DAMAGE_TOON = (
                    'CalculatingFees',
                    'WiretapperCollectCall',
                    'WiretapperCollectCallDamage',
                    'WiretapperCollectCall2',
                )
                HIGH_STAKES = (
                    'HighStakesHeal',
                    'HighStakesTrap',
                    'HighStakesLure',
                    'HighStakesSound',
                    'HighStakesThrow',
                    'HighStakesSquirt',
                    'HighStakesZap',
                    'HighStakesDrop',
                )
                ATTORNEY_OVERSEERS = (
                    'AttorneyOverseer',
                    'AttorneyOverseerDrop',
                    'AttorneyOverseerSquirt',
                    'AttorneyOverseerThrow',
                )
                GAG_BAN_RETALIATIONS = (
                    'GagBanRetaliationHeal',
                    'GagBanRetaliationTrap',
                    'GagBanRetaliationLure',
                    'GagBanRetaliationThrow',
                    'GagBanRetaliationSquirt',
                    'GagBanRetaliationZap',
                     'PowerhouseBurnDamage',
                     'DividendLiquidationEventDamage',
                     'ErfitHydrationCheck',
                     'ErfitHydrationCheckRevert',
                    'GagBanRetaliationSound',
                    'GagBanRetaliationDrop',
                )
                name = atkType['name']

                if name in DESPERATION_AND_MULTIPLIER_DAMAGE_TOON:
                    if self.suitHasCondition(theSuit.doId, 'desperation'):
                        result *= (1 + self.getSuitConditionModifier(theSuit.doId, 'desperation'))
                    if theSuit.getDamageMultiplier() > 1:
                        result *= theSuit.getDamageMultiplier()

                    result = math.ceil(result)
                    attack[SUIT_HP_COL][targetIndex] = result
                    toon.setHp(toon.hp + result)
                elif name in DAMAGE_TOON_AND_STORE or name in HIGH_STAKES or name in ATTORNEY_OVERSEERS:
                    result = math.ceil(result)
                    attack[SUIT_HP_COL][targetIndex] = result
                    toon.setHp(toon.hp + result)
                elif name in DAMAGE_STORE_ONLY:
                    attack[SUIT_HP_COL][targetIndex] = math.ceil(result)
                elif name in GAG_BAN_RETALIATIONS:
                    # if self.suitHasCondition(theSuit.doId, 'desperation'):
                    #     result = math.ceil(result * 1.4)
                    attack[SUIT_HP_COL][targetIndex] = result
                elif atkType['name'] in (
                    'AbsorbMovieLure',
                    'AbsorbMovieThrow',
                    'AbsorbMovieSquirt',
                    'AbsorbMovieZap',
                    'AbsorbMovieSound',
                    'AbsorbMovieDrop'
                ):
                    if theSuit.dna.name == 'cbutcher':
                        result = math.ceil(self.calculator.absorbDamageRecordkeeper)
                        theSuit.setHP(math.ceil(theSuit.currHP - math.ceil(self.calculator.absorbDamageRecordkeeper)))
                    else:
                        result = math.ceil(self.calculator.getAbsorbDamageForTrackName(atkType['name']))
                        theSuit.setHP(math.ceil(theSuit.currHP - result))

                    attack[SUIT_HP_COL][targetIndex] = result
                    toon.setHp(toon.hp + math.ceil(result))
                    if (theSuit.currHP) <= 0:
                        if self.suitHasCondition(theSuit.doId, 'overpressure'):
                            for s in self.battle.activeSuits:
                                if s.dna.name == 'safesupervis':
                                    if self.suitHasCondition(theSuit.doId, 'overpressureDeath'):
                                        self.setSuitCondition(s.doId, 'overpressureDeath2', 1, 1, 'setBoth')
                                    elif self.suitHasCondition(theSuit.doId, 'overpressureDeath2'):
                                        self.setSuitCondition(s.doId, 'overpressureDeath3', 1, 1, 'setBoth')
                                    else:
                                        self.setSuitCondition(s.doId, 'overpressureDeath', 1, 1, 'setBoth')
                        if theSuit.getSkeleRevives() >= 1:
                            theSuit.useSkeleRevive()
                        self.__removeLured(theSuit)
                        if not self.suitHasCondition(theSuit.doId, 'dead'):
                            self.calculator.deadSuits += 1
                            self.setSuitCondition(theSuit.doId, 'dead', 1, -1, 'setBoth')
                        for suit in self.battle.activeSuits:
                            self.setSuitCondition(suit.doId, 'deadpromotion', 1, -1, 'setBoth')
                elif atkType['name'] == 'AbsorbMovie':
                    if theSuit.dna.name == 'cbutcher':
                        result = math.ceil(self.calculator.absorbDamageRecordkeeper)
                        theSuit.setHP(math.ceil(theSuit.currHP - math.ceil(self.calculator.absorbDamageRecordkeeper)))
                    else:
                        result = math.ceil(self.calculator.absorbDamage)
                        theSuit.setHP(math.ceil(theSuit.currHP - math.ceil(self.calculator.absorbDamage)))
                    attack[SUIT_HP_COL][targetIndex] = result
                    toon.setHp(toon.hp + math.ceil(result))
                    if (theSuit.currHP) <= 0:
                        if self.suitHasCondition(theSuit.doId, 'overpressure'):
                            for s in self.battle.activeSuits:
                                if s.dna.name == 'safesupervis':
                                    if self.suitHasCondition(theSuit.doId, 'overpressureDeath'):
                                        self.setSuitCondition(s.doId, 'overpressureDeath2', 1, 1, 'setBoth')
                                    elif self.suitHasCondition(theSuit.doId, 'overpressureDeath2'):
                                        self.setSuitCondition(s.doId, 'overpressureDeath3', 1, 1, 'setBoth')
                                    else:
                                        self.setSuitCondition(s.doId, 'overpressureDeath', 1, 1, 'setBoth')
                        if theSuit.getSkeleRevives() >= 1:
                            theSuit.useSkeleRevive()
                        self.__removeLured(theSuit)
                        if not self.suitHasCondition(theSuit.doId, 'dead'):
                            self.calculator.deadSuits += 1
                            self.setSuitCondition(theSuit.doId, 'dead', 1, -1, 'setBoth')
                        for suit in self.battle.activeSuits:
                            self.setSuitCondition(suit.doId, 'deadpromotion', 1, -1, 'setBoth')
                elif atkType['name'] in (
                        'AbsorbMovieLevelLure',
                        'AbsorbMovieLevelThrow',
                        'AbsorbMovieLevelSquirt',
                        'AbsorbMovieLevelZap',
                        'AbsorbMovieLevelSound',
                        'AbsorbMovieLevelDrop'
                    ):

                    trackByName = {
                        'AbsorbMovieLevelLure': LURE,
                        'AbsorbMovieLevelThrow': THROW,
                        'AbsorbMovieLevelSquirt': SQUIRT,
                        'AbsorbMovieLevelZap': ZAP,
                        'AbsorbMovieLevelSound': SOUND,
                        'AbsorbMovieLevelDrop': DROP
                    }

                    track = trackByName[atkType['name']]

                    result = int(math.ceil(
                        self.calculator.levelDamageByTrack.get(track, 0)
                    ))

                    attack[SUIT_HP_COL][targetIndex] = result

                    if (
                        theSuit.dna.name in ('hroller', 'hrollers') and
                        result > 0
                    ):
                        if result >= theSuit.currHP:
                            theSuit.setHP(1)
                        else:
                            theSuit.setHP(theSuit.currHP - result)

                    if currTarget == len(targetList) - 1:
                        self.calculator.levelDamageByTrack[track] = 0
                        self.calculator.levelDamage = sum(
                            self.calculator.levelDamageByTrack.values()
                        )
                elif atkType['name'] == 'AbsorbMovieLevel':
                    result = math.ceil(self.calculator.levelDamage)
                    attack[SUIT_HP_COL][targetIndex] = result
                    toon.setHp(toon.hp + math.ceil(result))
                    if theSuit.dna.name == 'hroller':
                        if math.ceil(self.calculator.levelDamage) > theSuit.currHP:
                            theSuit.setHP(1)
                        else:
                            theSuit.setHP(math.ceil(theSuit.currHP - math.ceil(self.calculator.levelDamage)))
                elif atkType['name'] == 'SyphonMovie':
                    result = self.calculator.syphonHP.get(theSuit.doId, 0)
                    toon.setHp(toon.hp + math.ceil(result))
                    attack[SUIT_HP_COL][targetIndex] = result

                    if theSuit.currHP > 0:
                        theSuit.setHP(theSuit.currHP + result)

                    self.calculator.syphonHP[theSuit.doId] = 0
                elif atkType['name'] == 'ErclaimLaffSteal':
                    if theSuit.currHP < 1000:
                        result = self.calculator.syphonHP.get(theSuit.doId, 0) + 100
                    else:
                        result = self.calculator.syphonHP.get(theSuit.doId, 0)
                    toon.setHp(toon.hp + math.ceil(result))
                    attack[SUIT_HP_COL][targetIndex] = result

                    if theSuit.currHP > 0:
                        theSuit.setHP(theSuit.currHP + result)

                    self.calculator.syphonHP[theSuit.doId] = 0
                elif atkType['name'] == 'ErfitProToonShake':
                    targetSuit = self.battle.activeSuits[self.__getErfitTargetByHPPercent(excludeSuitId=theSuit.doId, mode='highest')]
                    result = self.calculator.syphonHP.get(theSuit.doId, 0)
                    toon.setHp(toon.hp + math.ceil(result))
                    attack[SUIT_HP_COL][targetIndex] = result

                    if targetSuit.currHP > 0:
                        self.setSuitCondition(targetSuit.doId, 'erfitHeal', 1, 1, 'setBoth')
                        if targetSuit.dna.name == 'erfit':
                            targetSuit.setHP(targetSuit.currHP + (result * 2))
                        else:
                            targetSuit.setHP(targetSuit.currHP + result)
                        self.calculator.syphonHP[targetSuit.doId] = result

                    if theSuit.currHP > 0 and not targetSuit.dna.name == 'erfit':
                        if (theSuit.currHP - result) <= 0:
                            theSuit.setHP(1)
                        else:
                            theSuit.setHP(theSuit.currHP - result)

                    self.calculator.syphonHP[theSuit.doId] = 0
                elif atkType['name'] == 'ErfitPhase2':
                    result = self.calculator.syphonHP.get(theSuit.doId, 0)
                    toon.setHp(toon.hp + math.ceil(result))
                    attack[SUIT_HP_COL][targetIndex] = result
                    self.setSuitCondition(theSuit.doId, 'erfitHeal', 0, 0, 'setBoth')
                    self.calculator.syphonHP.get(theSuit.doId, 0)
                elif atkType['name'] == 'DamageMovie':
                    result = self.damageHP.get(theSuit.doId, 0)
                    toon.setHp(toon.hp + math.ceil(result))
                    attack[SUIT_HP_COL][targetIndex] = result

                    if theSuit.currHP > 0:
                        theSuit.setHP(theSuit.currHP - result)

                    self.damageHP[theSuit.doId] = 0
                    if (theSuit.currHP) <= 0:
                        if self.suitHasCondition(theSuit.doId, 'overpressure'):
                            for s in self.battle.activeSuits:
                                if s.dna.name == 'safesupervis':
                                    if self.suitHasCondition(theSuit.doId, 'overpressureDeath'):
                                        self.setSuitCondition(s.doId, 'overpressureDeath2', 1, 1, 'setBoth')
                                    elif self.suitHasCondition(theSuit.doId, 'overpressureDeath2'):
                                        self.setSuitCondition(s.doId, 'overpressureDeath3', 1, 1, 'setBoth')
                                    else:
                                        self.setSuitCondition(s.doId, 'overpressureDeath', 1, 1, 'setBoth')
                        if theSuit.getSkeleRevives() >= 1:
                            theSuit.useSkeleRevive()
                        self.__removeLured(theSuit)
                        if not self.suitHasCondition(theSuit.doId, 'dead'):
                            self.calculator.deadSuits += 1
                            self.setSuitCondition(theSuit.doId, 'dead', 1, -1, 'setBoth')
                elif atkType['name'] in (
                    'AttorneyOverseer',
                    'AttorneyOverseerDrop',
                    'AttorneyOverseerSquirt',
                    'AttorneyOverseerThrow'
                        ):
                    attack[SUIT_HP_COL][targetIndex] = math.ceil(result)
                    toon.setHp(toon.hp + math.ceil(result))
                elif atkType['name'] == 'SafetyHeatWave':
                    attack[SUIT_HP_COL][targetIndex] = math.ceil(result)
                    self.damageHP[theSuit.doId] = self.calculator.damageHP.get(theSuit.doId, 0) + math.ceil(result)
                else:
                    if theSuit.getHP() > (theSuit.getMaxHP() * 1.5):
                        result *= 1.5
                    if theSuit.getHP() > theSuit.getMaxHP():
                        result *= 1.25
                    if self.suitHasCondition(theSuit.doId, 'dancesession'):
                        result *= 0.7
                    if self.suitHasCondition(theSuit.doId, 'ambassadorOverconfidence'):
                        result *= 0.75
                       # self.damageHP += math.ceil(result * 2)
                    if (self.suitHasCondition(theSuit.doId, 'soaked') or self.suitHasCondition(theSuit.doId, 'drenched')) and theSuit.dna.name == 'safesupervis':
                        result *= 0.75
                    if self.suitHasCondition(theSuit.doId, 'drenched'):
                        result *= 0.85
                    if self.suitHasCondition(theSuit.doId, 'desperation'):
                        result *= (1 + self.getSuitConditionModifier(theSuit.doId, 'desperation'))
                    if self.suitHasCondition(theSuit.doId, 'brokenconnection'):
                        result *= self.getSuitConditionModifier(theSuit.doId, 'brokenconnection')
                    if self.suitHasCondition(theSuit.doId, 'damageDown'):
                        result *= self.getSuitConditionModifier(theSuit.doId, 'damageDown')
                    if self.suitHasCondition(theSuit.doId, 'override'):
                        result *= 1.3
                    if self.suitHasCondition(theSuit.doId, 'enraged'):
                        result *= self.getSuitConditionModifier(theSuit.doId, 'enraged')
                    if self.toonHasCondition(toonId, 'snapped'):
                        result *= self.getToonConditionModifier(toonId, 'snapped')
                    if self.toonHasCondition(toonId, 'bombedToon'):
                        result *= self.getToonConditionModifier(toonId, 'bombedToon')
                    if self.toonHasCondition(toonId, 'markedwood'):
                        result *= self.getToonConditionModifier(toonId, 'markedwood')
                    # Going to slowly replace individual status effects so we acclimate to the new system before moving onto a more sophisticated means of this.
                    for condition in self.toonStatusConditionsNew[toonId]:
                        if isinstance(condition, StatusEffects.Snapped):
                            result *= condition.defenseMod

                    if theSuit.getDamageMultiplier() > 1:
                        result *= theSuit.getDamageMultiplier()
                    if self.suitHasCondition(theSuit.doId, 'soaked') and theSuit.dna.name == 'redd':
                        result *= 1.5
                    # if atkType['name'] == 'RadiographerHotTake':
                    #     self.damageHP += math.ceil(result * 2)
                    attack[SUIT_HP_COL][targetIndex] = math.ceil(result)
                    if result > 0 and self.__suitAtkHit(attack[SUIT_ID_COL], attack[SUIT_ATK_COL]):
                        if theSuit.dna.name in ('erfit', 'erclaim') and atkType['name'] == 'Quake':
                            self.__addsyphonHP(theSuit.doId, result)
                    if atkType['name'] == 'RacketeerExtortion':
                        self.calculator.syphonHP[theSuit.doId] = self.calculator.syphonHP.get(theSuit.doId, 0) + math.ceil(result * 2)
                    if atkType['name'] == 'ForemanExtortion':
                        self.calculator.syphonHP[theSuit.doId] = self.calculator.syphonHP.get(theSuit.doId, 0) + math.ceil(result * 2)
                    # if theSuit.dna.name in ['erfit', 'erclaim'] and self.__suitAtkHit(attack[SUIT_ID_COL], attack[SUIT_ATK_COL]) and atkType['name'] == 'Quake':
                    #     self.calculator.syphonHP[theSuit.doId] = 0
                    #     self.calculator.syphonHP[theSuit.doId] = self.calculator.syphonHP.get(theSuit.doId, 0) + math.ceil(result * 2)
                    # if atkType['name'] == 'WiretapperWiretapped':
                    #     self.calculator.syphonHP[theSuit.doId] = self.calculator.syphonHP.get(theSuit.doId, 0) + math.ceil(result * 2)
            except:
                if self.suitHasCondition(theSuit.doId, 'partnered'):
                    if self.toonHasCondition(toonId, 'partnered'):
                        result *= 1.5
                    else:
                        result *= 0.5
                if theSuit.getHP() > (theSuit.getMaxHP() * 1.5):
                    result *= 1.5
                if theSuit.getHP() > theSuit.getMaxHP():
                    result *= 1.25
                if self.suitHasCondition(theSuit.doId, 'dancesession'):
                    result *= 0.7
                if (self.suitHasCondition(theSuit.doId, 'soaked') or self.suitHasCondition(theSuit.doId, 'drenched')) and theSuit.dna.name == 'safesupervis':
                    result *= 0.75
                if self.suitHasCondition(theSuit.doId, 'drenched'):
                    result *= 0.85
                if self.suitHasCondition(theSuit.doId, 'damageDown'):
                    result *= self.getSuitConditionModifier(theSuit.doId, 'damageDown')
                if self.getSuitConditionTurns(theSuit.doId, 'sleepy') == 2 and self.suitHasCondition(theSuit.doId, 'sleepy'):
                    result *= 0.2
                if self.getSuitConditionTurns(theSuit.doId, 'sleepy') == 1 and self.suitHasCondition(theSuit.doId, 'sleepy'):
                    result *= 0.5
                if self.suitHasCondition(theSuit.doId, 'desperation'):
                    result *= (1 + self.getSuitConditionModifier(theSuit.doId, 'desperation'))
                if self.suitHasCondition(theSuit.doId, 'brokenconnection'):
                    result *= self.getSuitConditionModifier(theSuit.doId, 'brokenconnection')
                if self.suitHasCondition(theSuit.doId, 'override'):
                    result *= 1.3
                if self.suitHasCondition(theSuit.doId, 'enraged'):
                    result *= self.getSuitConditionModifier(theSuit.doId, 'enraged')
                if self.toonHasCondition(toonId, 'snapped'):
                    result *= self.getToonConditionModifier(toonId, 'snapped')
                if self.toonHasCondition(toonId, 'bombedToon'):
                    result *= self.getToonConditionModifier(toonId, 'bombedToon')
                if self.toonHasCondition(toonId, 'markedwood'):
                    result *= self.getToonConditionModifier(toonId, 'markedwood')
                # Going to slowly replace individual status effects so we acclimate to the new system before moving onto a more sophisticated means of this.
                for condition in self.toonStatusConditionsNew[toonId]:
                    if isinstance(condition, StatusEffects.Snapped):
                        result *= condition.defenseMod

                if theSuit.getDamageMultiplier() > 1:
                    result *= theSuit.getDamageMultiplier()
                if self.suitHasCondition(theSuit.doId, 'soaked') and theSuit.dna.name == 'redd':
                    result *= 1.5
                if result > 0 and self.__suitAtkHit(attack[SUIT_ID_COL], attack[SUIT_ATK_COL]):
                    if theSuit.dna.name in ('erfit', 'erclaim'):
                        self.__addsyphonHP(theSuit.doId, result)
                attack[SUIT_HP_COL][targetIndex] = math.ceil(result)

    def calcSuitAtkHp(self, attack):
        targetList = self.__createSuitTargetList(attack)
        for currTarget in xrange(len(targetList)):
            toonId = targetList[currTarget]
            toon = self.battle.getToon(toonId)
            result = 0
            theSuit = self.battle.findSuit(attack[SUIT_ID_COL])
            for i in xrange(len(self.battle.activeSuits)):
                suitId = self.battle.activeSuits[i].doId
            atkType = attack[SUIT_ATK_COL]
            targetIndex = self.battle.activeToons.index(toonId)
            if toon and toon.immortalMode:
                result = 1
            elif TOONS_TAKE_NO_DAMAGE:
                result = 0
            elif self.__suitAtkHit(attack[SUIT_ID_COL], attack[SUIT_ATK_COL]) or self.toonHasCondition(toonId, 'dodgy'):
                mult = 1.0
                result = math.ceil(atkType['hp'] * mult)
                targetIndex = self.battle.activeToons.index(toonId)
                if theSuit.getExecutive():
                    result = math.ceil(result * ToontownBattleGlobals.EXECUTIVE_DMG_MULT)
                elif theSuit.getGovernaught():
                    result = math.ceil(result * ToontownBattleGlobals.GOVERNAUGHT_DMG_MULT)
                if atkType['name'] == 'Aftershock':
                    result = random.randint(18, 38)
                    attack[SUIT_HP_COL][targetIndex] = result
                elif atkType['name'] == 'MintCompoundingInterest':
                    # self.interestMultiplier += 2
                    result = self.interestMultiplier
                    attack[SUIT_HP_COL][targetIndex] = result
                elif atkType['name'] == 'ErfitWringOut':
                    # self.interestMultiplier += 2
                    result = 44
                    attack[SUIT_HP_COL][targetIndex] = result
                    if self.toonHasCondition(toonId, 'hydrated') and result > 0 and not self.toonHasCondition(toonId, 'hidden'):
                        self.setToonCondition(toon.doId, 'energized', 50, 3, 'setBoth')
                        self.setToonCondition(toon.doId, 'markedwood', 1.15, 3, 'setBoth')
                    else:
                        self.setToonCondition(toon.doId, 'driedOut', 1, 3, 'setBoth')
                elif atkType['name'] == 'ForemanRedTape':
                    result = 25
                    attack[SUIT_HP_COL][targetIndex] = result
                elif atkType['name'] == 'ForemanBurning':
                    result = 25
                    attack[SUIT_HP_COL][targetIndex] = result
                elif atkType['name'] == 'PresidentDriver':
                    result = 36
                    attack[SUIT_HP_COL][targetIndex] = result
                elif atkType['name'] == 'RecordkeeperMinutesTakenDamage':
                    self.setSuitCondition(theSuit.doId, 'costscalculator', 0, 0, 'setBoth')
                    result = self.calculator.recordkeeperMultiplier
                    attack[SUIT_HP_COL][targetIndex] = result
                elif atkType['name'] == 'RacketeerPeckingOrderRetaliationSoak':
                    result = 25
                    attack[SUIT_HP_COL][targetIndex] = result
                    self.setToonCondition(toon.doId, 'dodgy', -100, 3, 'setBoth')
            if result > 0 and self.__suitCanAttack(theSuit.doId):
                if atkType['name'] == 'ForemanRedTape':
                    self.setToonCondition(toon.doId, 'noSOS', 1, 3, 'setBoth')
                    self.setToonCondition(toon.doId, 'noFires', 1, 3, 'setBoth')
                    #self.setToonCondition(toon.doId, 'noUnites', 1, 3, 'setBoth')
                    self.setToonCondition(toon.doId, 'noSues', 1, 3, 'setBoth')
                elif atkType['name'] == 'RecordkeeperMinutesTakenDamage':
                    self.setSuitCondition(theSuit.doId, 'costscalculator', 0, 0, 'setBoth')
                    result = self.recordkeeperMultiplier
                    attack[SUIT_HP_COL][targetIndex] = result
                elif atkType['name'] == 'RacketeerPeckingOrderRetaliationSoak':
                    result = 25
                    attack[SUIT_HP_COL][targetIndex] = result
                    self.setToonCondition(toon.doId, 'dodgy', -100, 3, 'setBoth')
                elif atkType['name'] == 'ForemanBurning':
                    self.setToonCondition(toon.doId, 'smoked', 1, 3, 'setBoth')
                elif atkType['name'] == 'PresidentDriver':
                    if self.getToonConditionModifier(toonId, 'allGagBoost') < -25:
                        self.setToonCondition(toon.doId, 'allGagBoost',
                                                      self.getToonConditionModifier(toonId, 'allGagBoost'), 2, 'setBoth')
                        self.setToonCondition(toon.doId, 'lureBoost',
                                                      self.getToonConditionModifier(toonId, 'lureBoost'), 2, 'setBoth')
                    else:
                        self.setToonCondition(toon.doId, 'allGagBoost', -25, 2, 'setBoth')
                        self.setToonCondition(toon.doId, 'lureBoost', -25, 2, 'setBoth')


                if self.toonHasCondition(toonId, 'hidden'):
                    result *= 0
                if self.suitHasCondition(theSuit.doId, 'partnered'):
                    if self.toonHasCondition(toonId, 'partnered'):
                        result *= 1.5
                    else:
                        result *= 0.5
                if self.suitHasCondition(theSuit.doId, 'dancesession'):
                    result *= 0.7
                    #self.damageHP += result
                if theSuit.dna.name == 'supervis':
                    self.calculator.damageHP[theSuit.doId] = 0
                    self.calculator.damageHP[theSuit.doId] = self.calculator.damageHP.get(theSuit.doId, 0) + math.ceil(result)
                # if theSuit.dna.name == 'phouse':
                #     self.damageHP[theSuit.doId] = self.damageHP.get(theSuit.doId, 0) + math.ceil(result)
                if (self.suitHasCondition(theSuit.doId, 'soaked') or self.suitHasCondition(theSuit.doId, 'drenched')) and theSuit.dna.name == 'safesupervis':
                    result *= 0.75
                if self.suitHasCondition(theSuit.doId, 'drenched'):
                    result *= 0.85
                if (self.suitHasCondition(theSuit.doId, 'soaked') or self.suitHasCondition(theSuit.doId, 'drenched')) and theSuit.dna.name == 'redd':
                    result *= 1.5
                if self.suitHasCondition(theSuit.doId, 'damageDown'):
                    result *= self.getSuitConditionModifier(theSuit.doId, 'damageDown')
                if theSuit.getHP() > (theSuit.getMaxHP() * 1.5):
                    result *= 1.5
                if theSuit.getHP() > theSuit.getMaxHP():
                    result *= 1.25
                if self.getSuitConditionTurns(theSuit.doId, 'sleepy') == 2 and self.suitHasCondition(theSuit.doId, 'sleepy'):
                    result *= 0.2
                if self.getSuitConditionTurns(theSuit.doId, 'sleepy') == 1 and self.suitHasCondition(theSuit.doId, 'sleepy'):
                    result *= 0.5
                if self.suitHasCondition(theSuit.doId, 'desperation'):
                    result *= (1 + self.getSuitConditionModifier(theSuit.doId, 'desperation'))
                if self.suitHasCondition(theSuit.doId, 'brokenconnection'):
                    result *= self.getSuitConditionModifier(theSuit.doId, 'brokenconnection')
                if self.suitHasCondition(theSuit.doId, 'override'):
                    result *= 1.3
                if self.suitHasCondition(theSuit.doId, 'enraged'):
                    result *= self.getSuitConditionModifier(theSuit.doId, 'enraged')
                if self.toonHasCondition(toonId, 'snapped'):
                    result *= self.getToonConditionModifier(toonId, 'snapped')
                if self.toonHasCondition(toonId, 'bombedToon'):
                    result *= self.getToonConditionModifier(toonId, 'bombedToon')
                if self.toonHasCondition(toonId, 'markedwood'):
                    result *= self.getToonConditionModifier(toonId, 'markedwood')
                # Going to slowly replace individual status effects so we acclimate to the new system before moving onto a more sophisticated means of this.
                for condition in self.toonStatusConditionsNew[toonId]:
                    if isinstance(condition, StatusEffects.Snapped):
                        result *= condition.defenseMod

                if theSuit.getDamageMultiplier() > 1:
                    result *= theSuit.getDamageMultiplier()
                #if self.toonHasCondition(toonId, 'heavyRainDamageToon'):
                   # result *= 0.6
                   # self.setToonCondition(toonId, 'heavyRainDamageToon', self.getToonConditionModifier(toonId, 'heavyRainDamageToon') + result, -1, 'setBoth')
                if result > 0:
                    if self.toonHasCondition(toonId, 'contingencyMarked') and self.__suitAtkHit(attack[SUIT_ID_COL], attack[SUIT_ATK_COL]):
                        for suit in self.battle.activeSuits:
                            if suit.dna.name in ('bkeeper', 'cdirector', 'clubpres'):
                                self.setSuitCondition(suit.doId, 'soakedcalculator', 1, 1, 'setBoth')
                        self.setToonCondition(toonId, 'contingencyHit', 1, 1, 'setBoth')
                    # self.snipeHP += math.ceil(result)
                    if self.toonHasCondition(toonId, 'noFires') and self.__suitAtkHit(attack[SUIT_ID_COL], attack[SUIT_ATK_COL]):
                        self.setToonCondition(toonId, 'contingencyHit', 1, 1, 'setBoth')
                        for suit in self.battle.activeSuits:
                            if suit.dna.name == 'foreman':
                                self.setSuitCondition(suit.doId, 'contingencyHit', 1, 1, 'setBoth')
                    # self.snipeHP += math.ceil(result)
                    if self.toonHasCondition(toonId, 'bombedToon') and self.__suitAtkHit(attack[SUIT_ID_COL], attack[SUIT_ATK_COL]):
                        self.setToonCondition(toonId, 'bombedToonDamage', 1, 1, 'setBoth')
                    if self.suitHasCondition(theSuit.doId, 'guestVerse') and self.__suitAtkHit(attack[SUIT_ID_COL], attack[SUIT_ATK_COL]):
                        self.setToonCondition(toonId, 'viralSensation', 50, 3, 'setBoth')
                        self.setSuitCondition(theSuit.doId, 'guestVerseComplete', 1, 1, 'setBoth')
                    if result > 0 and self.__suitAtkHit(attack[SUIT_ID_COL], attack[SUIT_ATK_COL]):
                        if self.suitHasCondition(theSuit.doId, 'syphon'):
                            self.__addsyphonHP(theSuit.doId, result)

                        if theSuit.dna.name in ('erfit', 'erclaim'):
                            self.__addsyphonHP(theSuit.doId, result)
                        #theSuit.setHP(theSuit.currHP + math.ceil(result))
                    #if theSuit.dna.name == 'supervis' and theSuit.getActualLevel() == 25 and self.__attackHasHit(attack):
                        #self.setSuitCondition(theSuit.doId, 'fraudulentDamage', result, 1, 'setBoth')
            attack[SUIT_HP_COL][targetIndex] = math.ceil(result)
