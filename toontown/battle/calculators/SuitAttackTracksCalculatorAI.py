from toontown.battle.BattleBase import *
from toontown.battle.BattleGlobals import *
from toontown.battle import SuitBattleGlobals
from toontown.toonbase import ToontownBattleGlobals
from toontown.battle import StatusEffects
import random
import math

class SuitAttackTracksCalculatorAI:

    def __init__(self, calculator):
        self.calculator = calculator
        self.battle = calculator.battle

    def __getattr__(self, name):
        return getattr(self.calculator, name)

    def __suitCanAttack(self, suitId):
        return self.calculator.suitCanAttack(suitId)

    def __getCheatAttack(self, suitId, attackInfo):
        return self.calculator.getCheatAttack(
            suitId,
            attackInfo
        )

    def __getPerToonCheatAttack(self, suitId, targetIndex, attackInfo):
        return self.calculator.getPerToonCheatAttack(
            suitId, targetIndex,
            attackInfo
        )

    def __getLureRemoval(self, suitId):
        return self.calculator.getLureRemoval(suitId)

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

    def __queueAbsorbMovieForTrack(self, suit, trackName, trackConst):
        suitId = suit.doId

        if suit.currHP <= 0:
            return

        absorbDamage = self.absorbDamageByTrack.get(trackConst, 0)
        levelDamage = self.levelDamageByTrack.get(trackConst, 0)

        queuedAbsorb = False
        queuedLevel = False

        if (
            (self.suitHasCondition(suitId, 'shielding') or self.suitHasCondition(suitId, 'recordkeeperShielding') or suit.dna.name == 'mplayers') and
            (absorbDamage > 0)
        ):
            attack = self.__getCheatAttack(suitId, {
                'suitName': suit.dna.name,
                'name': 'AbsorbMovie%s' % trackName,
                'animName': 'nothing',
                'hp': 0,
                'acc': 100,
                'freq': 0,
                'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                            'targetType': 'suit',
                            'allowSelfTarget': True,
                            'targetSelf': True,
                            'damageTarget': 'target',
                            'healTarget': 'target'
                        })
            if attack[SUIT_ATK_COL]:
                self.battle.suitAttacks.append(attack)
            queuedAbsorb = True

        if levelDamage > 0 and suit.currHP > 1 and suit.dna.name == 'hroller':
            attack = self.__getCheatAttack(suitId, {
                'suitName': suit.dna.name,
                'name': 'AbsorbMovieLevel%s' % trackName,
                'animName': 'nothing',
                'hp': 0,
                'acc': 100,
                'freq': 0,
                'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                            'targetType': 'suit',
                            'allowSelfTarget': True,
                            'targetSelf': True,
                            'damageTarget': 'target',
                            'healTarget': 'target'
                        })
            if attack[SUIT_ATK_COL]:
                self.battle.suitAttacks.append(attack)
            queuedLevel = True

        # if queuedAbsorb:
        #     self.absorbDamageByTrack[trackConst] = 0

        if queuedLevel:
            self.levelDamage *= 0

    def __queueGagBanRetaliation(self, suit, trackName):
        suitId = suit.doId

        if not self.suitHasCondition(suitId, 'bannedGagUsed'):
            return

        retaliationData = {
            'caseman': {
                'name': 'GagBanRetaliation%s' % trackName,
                'animName': 'nothing',
                'mode': 'single'
            },
            'stenog': {
                'name': 'GagBanRetaliation%s' % trackName,
                'animName': 'nothing',
                'mode': 'single'
            },
            'cdirector': {
                'name': 'GagBanRetaliation%s' % trackName,
                'animName': 'nothing',
                'mode': 'group'
            },
            'racket': {
                'name': 'GagBanRetaliation%s' % trackName,
                'animName': 'throw-object',
                'mode': 'group'
            },
            'wtapper': {
                'name': 'GagBanRetaliation%s' % trackName,
                'animName': 'nothing',
                'mode': 'single'
            },
        }

        data = retaliationData.get(suit.dna.name)
        if not data:
            return

        lureRemovalByTrack = {
            'Heal': self.__getLureRemovalHeal,
            'Trap': self.__getLureRemovalTrap,
            'Lure': self.__getLureRemovalLure,
            'Throw': self.__getLureRemovalThrow,
            'Squirt': self.__getLureRemovalSquirt,
            'Zap': self.__getLureRemovalZap,
            'Sound': self.__getLureRemovalSound,
            'Drop': self.__getLureRemovalDrop
        }

        mode = data.get('mode', 'group')

        if (
            mode == 'group' and
            not self.suitHasCondition(suitId, 'sounded') and
            self.suitHasCondition(suitId, 'unlureSuit') and
            suit.dna.name not in ('stenog', 'caseman', 'wtapper')
        ):
            lureRemovalFunc = lureRemovalByTrack.get(trackName, self.__getLureRemovalPreToon)
            attack = lureRemovalFunc(suitId)
            if attack[SUIT_ATK_COL]:
                self.battle.suitAttacks.append(attack)

        if mode == 'group':
            attack = self.__getCheatAttack(suitId, {
                'suitName': suit.dna.name,
                'name': data['name'],
                'animName': data['animName'],
                'hp': 0,
                'acc': 100,
                'freq': 0,
                'group': SuitBattleGlobals.ATK_TGT_GROUP
            })

            if suit.currHP > 0 or suit.dna.name in ('stenog', 'caseman'):
                if attack[SUIT_ATK_COL]:
                    self.battle.suitAttacks.append(attack)

            return

        # toonConditionByTrack = {
        #     'Heal': 'bannedHealUsed',
        #     'Trap': 'bannedTrapUsed',
        #     'Lure': 'bannedLureUsed',
        #     'Throw': 'bannedThrowUsed',
        #     'Squirt': 'bannedSquirtUsed',
        #     'Zap': 'bannedZapUsed',
        #     'Sound': 'bannedSoundUsed',
        #     'Drop': 'bannedDropUsed'
        # }

        for toonId in self.battle.activeToons:

            toonCondition = None

            if suit.dna.name == 'caseman':
                toonCondition = 'banned2'

            elif suit.dna.name == 'stenog':
                toonCondition = 'banned'

            else:
                if self.toonHasCondition(toonId, 'banned'):
                    toonCondition = 'banned'
                elif self.toonHasCondition(toonId, 'banned2'):
                    toonCondition = 'banned2'
                else:
                    continue

            if not toonCondition:
                continue

            if not self.toonHasCondition(toonId, toonCondition):
                continue

            targetIndex = self.battle.activeToons.index(toonId)

            retaliation = self.__getPerToonCheatAttack(suit.doId, targetIndex, {
            'suitName': suit.dna.name,
            'name': data['name'],
            'animName': data['animName'],
            'hp': 0,
            'acc': 100,
            'freq': 0,
            'group': SuitBattleGlobals.ATK_TGT_SINGLE
        })

            # self.battle.suitAttacks.append(retaliation)
            # # Save the damage that __getCheatAttack already calculated.
            # calculatedHp = attack[SUIT_HP_COL]

            # # Retarget to this specific toon.
            # attack[SUIT_TGT_COL] = [targetIndex]
            # attack[SUIT_HP_COL] = [-1 for i in xrange(len(self.battle.activeToons))]
            # attack[SUIT_HP_COL][targetIndex] = calculatedHp[targetIndex]

            if suit.currHP > 0 or suit.dna.name in ('stenog', 'caseman'):
                self.battle.suitAttacks.append(retaliation)

    
    def calculateSuitAttacksAfterHeal(self):
        for i in range(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'videog':
                damageCogs = 0
                for suit in self.battle.activeSuits:
                    if not suit.dna.name in ['director', 'fmaker', 'choreo', 'cinema']:
                        continue
                    if suit.getHP() > 0 and suit.dna.name in ['director', 'fmaker', 'choreo', 'cinema']:
                        damageCogs = 1
                if damageCogs == 0:
                    self.setSuitCondition(suitId, 'immunecalculator', 1, 1, 'setBoth')
            if self.battle.activeSuits[i].dna.name == 'hrollers':
                if self.battle.activeSuits[i].getActualLevel() == 32 and not self.battle.activeSuits[i].currHP <= 0:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'HighRollerCheerRetaliation',  # Purple Silhouette
                                            'animName': 'glower',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_GROUP})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
        for suit in self.battle.activeSuits:
            self.__queueGagBanRetaliation(suit, 'Heal')


    def calculateSuitAttacksAfterTrap(self):
        for i in range(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'videog':
                damageCogs = 0
                for suit in self.battle.activeSuits:
                    if not suit.dna.name in ['director', 'fmaker', 'choreo', 'cinema']:
                        continue
                    if suit.getHP() > 0 and suit.dna.name in ['director', 'fmaker', 'choreo', 'cinema']:
                        damageCogs = 1
                if damageCogs == 0:
                    self.setSuitCondition(suitId, 'immunecalculator', 1, 1, 'setBoth')
            if self.battle.activeSuits[i].dna.name == 'hrollers':
                if self.suitHasCondition(suitId, 'barcalculator') and self.suitHasCondition(suitId, 'unlureSuit') and not self.suitHasCondition(suitId, 'sounded') and not \
                        self.battle.activeSuits[i].currHP <= 0:
                    attack = self.__getLureRemovalTrap(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.battle.activeSuits[i].getActualLevel() == 29 and self.suitHasCondition(suitId,
                                                                                               'barcalculator') and not \
                        self.battle.activeSuits[i].currHP <= 0:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'HighRollerBar2',  # Red Silhouette
                                            'animName': 'snap',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_GROUP})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
        for suit in self.battle.activeSuits:
            self.__queueGagBanRetaliation(suit, 'Trap')


    def calculateSuitAttacksAfterLure(self):
        for i in range(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'videog':
                damageCogs = 0
                for suit in self.battle.activeSuits:
                    if not suit.dna.name in ['director', 'fmaker', 'choreo', 'cinema']:
                        continue
                    if suit.getHP() > 0 and suit.dna.name in ['director', 'fmaker', 'choreo', 'cinema']:
                        damageCogs = 1
                if damageCogs == 0:
                    self.setSuitCondition(suitId, 'immunecalculator', 1, 1, 'setBoth')
            if self.battle.activeSuits[i].dna.name == 'hroller':
                damageCogs = 0
                for suit in self.battle.activeSuits:
                    if suit.dna.name != 'hrollers':
                        continue
                    if suit.getHP() > 0 and suit.dna.name == 'hrollers':
                        damageCogs = 1
                if damageCogs == 0:
                    self.setSuitCondition(suitId, 'HRdamagereduction', 0, 0, 'setBoth')
            if self.battle.activeSuits[i].dna.name == 'director':
                damageCogs = 0
                for suit in self.battle.activeSuits:
                    if suit.dna.name not in ['choreo', 'fmaker', 'cinema']:
                        continue
                    if suit.getHP() > 0 and suit.dna.name in ['choreo', 'fmaker', 'cinema']:
                        damageCogs = 1
                if damageCogs == 0:
                    self.setSuitCondition(suitId, 'directorDamageReduction', 0, 0, 'setBoth')
        for suit in self.battle.activeSuits:
            self.__queueGagBanRetaliation(suit, 'Lure')
            self.__queueAbsorbMovieForTrack(suit, 'Lure', LURE)

        self.absorbDamageByTrack[LURE] = 0


    def calculateSuitAttacksAfterThrow(self):
        for i in range(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if (self.suitHasCondition(suitId, 'overseerKB') or self.suitHasCondition(suitId, 'overseerCombo')) and (self.comboDamage > 0 or self.knockbackDamage > 0) and self.battle.activeSuits[i].currHP > 0:
                attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                        'name': 'AttorneyOverseerThrow',  # Overseer Combo/Knockback Heal Movie
                                        'animName': 'nothing',
                                        'hp': 0,
                                        'acc': 100,
                                        'freq': 0,
                                        'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                            'targetType': 'suit',
                            'allowSelfTarget': True,
                            'targetSelf': True,
                            'damageTarget': 'target',
                            'healTarget': 'target'})
                if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
        for i in range(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            # if self.battle.activeSuits[i].dna.name == 'clerk' and self.battle.activeSuits[i].getActualLevel() == 20:
            #     if (self.knockbackDamage > 0) and self.battle.activeSuits[i].currHP > 0:
            #         attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
            #                                 'name': 'KnockbackThrow',  # Overseer Combo/Knockback Heal Movie
            #                                 'animName': 'nothing',
            #                                 'hp': 0,
            #                                 'acc': 100,
            #                                 'freq': 0,
            #                                 'group': SuitBattleGlobals.ATK_TGT_SINGLE})
            #         if attack[SUIT_ATK_COL]:
                        # self.battle.suitAttacks.append(attack)
            #         self.knockbackDamage *= 0
            if self.battle.activeSuits[i].dna.name == 'hrollers' and self.battle.activeSuits[i].getActualLevel() == 25:
                if (self.knockbackDamage > 0) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'KnockbackThrow',  # Overseer Combo/Knockback Heal Movie
                                            'animName': 'nothing',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                                        'targetType': 'none'})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                    self.knockbackDamage *= 0
            if self.battle.activeSuits[i].dna.name == 'hrollers' and self.battle.activeSuits[i].getActualLevel() == 26:
                if (self.comboDamage > 0) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'ComboThrow',  # Overseer Combo/Knockback Heal Movie
                                            'animName': 'nothing',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                                        'targetType': 'none'})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                    self.comboDamage *= 0
        for i in range(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'dking':
                if self.suitHasCondition(suitId, 'marked') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {
                        'suitName': self.battle.activeSuits[i].dna.name,
                        'name': 'DividendZapRetaliation',
                        'animName': 'blue-chip',
                        'hp': 0,
                        'acc': 100,
                        'freq': 0,
                        'group': SuitBattleGlobals.ATK_TGT_SINGLE
                    })
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'videog':
                damageCogs = 0
                for suit in self.battle.activeSuits:
                    if not suit.dna.name in ['director', 'fmaker', 'choreo', 'cinema']:
                        continue
                    if suit.getHP() > 0 and suit.dna.name in ['director', 'fmaker', 'choreo', 'cinema']:
                        damageCogs = 1
                if damageCogs == 0:
                    self.setSuitCondition(suitId, 'immunecalculator', 1, 1, 'setBoth')
            if self.battle.activeSuits[i].dna.name == 'hroller':
                damageCogs = 0
                for suit in self.battle.activeSuits:
                    if suit.dna.name != 'hrollers':
                        continue
                    if suit.getHP() > 0 and suit.dna.name == 'hrollers':
                        damageCogs = 1
                if damageCogs == 0:
                    self.setSuitCondition(suitId, 'HRdamagereduction', 0, 0, 'setBoth')
            if self.battle.activeSuits[i].dna.name == 'director':
                damageCogs = 0
                for suit in self.battle.activeSuits:
                    if suit.dna.name not in ['choreo', 'fmaker', 'cinema']:
                        continue
                    if suit.getHP() > 0 and suit.dna.name in ['choreo', 'fmaker', 'cinema']:
                        damageCogs = 1
                if damageCogs == 0:
                    self.setSuitCondition(suitId, 'directorDamageReduction', 0, 0, 'setBoth')
        for suit in self.battle.activeSuits:
            self.__queueGagBanRetaliation(suit, 'Throw')
            self.__queueAbsorbMovieForTrack(suit, 'Throw', THROW)

        self.absorbDamageByTrack[THROW] = 0


    def calculateSuitAttacksAfterSquirt(self):
        for i in range(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if (self.suitHasCondition(suitId, 'overseerKB') or self.suitHasCondition(suitId, 'overseerCombo')) and (self.comboDamage > 0 or self.knockbackDamage > 0) and self.battle.activeSuits[i].currHP > 0:
                attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                        'name': 'AttorneyOverseerSquirt',  # Overseer Combo/Knockback Heal Movie
                                        'animName': 'nothing',
                                        'hp': 0,
                                        'acc': 100,
                                        'freq': 0,
                                        'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                            'targetType': 'suit',
                            'allowSelfTarget': True,
                            'targetSelf': True,
                            'damageTarget': 'target',
                            'healTarget': 'target'})
                if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
        for i in range(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            # if self.battle.activeSuits[i].dna.name == 'clerk' and self.battle.activeSuits[i].getActualLevel() == 20:
            #     if (self.knockbackDamage > 0) and self.battle.activeSuits[i].currHP > 0:
            #         attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
            #                                 'name': 'KnockbackSquirt',  # Overseer Combo/Knockback Heal Movie
            #                                 'animName': 'nothing',
            #                                 'hp': 0,
            #                                 'acc': 100,
            #                                 'freq': 0,
            #                                 'group': SuitBattleGlobals.ATK_TGT_SINGLE})
            #         if attack[SUIT_ATK_COL]:
                        # self.battle.suitAttacks.append(attack)
            #         self.knockbackDamage *= 0
            if self.battle.activeSuits[i].dna.name == 'hrollers' and self.battle.activeSuits[i].getActualLevel() == 25:
                if (self.knockbackDamage > 0) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'KnockbackSquirt',  # Overseer Combo/Knockback Heal Movie
                                            'animName': 'nothing',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                                        'targetType': 'none'})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                    self.knockbackDamage *= 0
            if self.battle.activeSuits[i].dna.name == 'hrollers' and self.battle.activeSuits[i].getActualLevel() == 26:
                if (self.comboDamage > 0) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'ComboSquirt',  # Overseer Combo/Knockback Heal Movie
                                            'animName': 'nothing',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                                        'targetType': 'none'})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                    self.comboDamage *= 0
            if self.battle.activeSuits[i].dna.name == 'hrollers':
                if self.battle.activeSuits[i].getActualLevel() == 30 and not self.battle.activeSuits[i].currHP <= 0:
                    self.__appendToonConditionDamageAndRetaliation(
                        condition='soakToon',
                        damage=0,
                        damageMovie=None,
                        retaliations=[
                            {
                                'suitNames': ['hrollers'],
                                'actualLevel': 30,
                                'movie': 'HighRollerSplashback',
                                'animName': 'throw-object',
                                'hp': 0,
                                'queueCondition': 'nothing',
                            }
                        ]
                    )
        for i in range(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'redd': #redd heir wing
                if self.suitHasCondition(suitId, 'soakedcalculator') and not self.suitHasCondition(suitId, 'sounded') and self.suitHasCondition(suitId, 'unlureSuit') and self.__suitCanAttack(suitId) and  self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getLureRemoval(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'soakedcalculator') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'ReddLiquidationSale',
                     'animName': 'rage',
                     'hp': 0,
                     'acc': 85,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                                        'targetType': 'none'})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'videog':
                damageCogs = 0
                for suit in self.battle.activeSuits:
                    if not suit.dna.name in ['director', 'fmaker', 'choreo', 'cinema']:
                        continue
                    if suit.getHP() > 0 and suit.dna.name in ['director', 'fmaker', 'choreo', 'cinema']:
                        damageCogs = 1
                if damageCogs == 0:
                    self.setSuitCondition(suitId, 'immunecalculator', 1, 1, 'setBoth')
            if self.battle.activeSuits[i].dna.name == 'hroller':
                damageCogs = 0
                for suit in self.battle.activeSuits:
                    if suit.dna.name != 'hrollers':
                        continue
                    if suit.getHP() > 0 and suit.dna.name == 'hrollers':
                        damageCogs = 1
                if damageCogs == 0:
                    self.setSuitCondition(suitId, 'HRdamagereduction', 0, 0, 'setBoth')
            if self.battle.activeSuits[i].dna.name == 'director':
                damageCogs = 0
                for suit in self.battle.activeSuits:
                    if suit.dna.name not in ['choreo', 'fmaker', 'cinema']:
                        continue
                    if suit.getHP() > 0 and suit.dna.name in ['choreo', 'fmaker', 'cinema']:
                        damageCogs = 1
                if damageCogs == 0:
                    self.setSuitCondition(suitId, 'directorDamageReduction', 0, 0, 'setBoth')
        for suit in self.battle.activeSuits:
            self.__queueGagBanRetaliation(suit, 'Squirt')
            self.__queueAbsorbMovieForTrack(suit, 'Squirt', SQUIRT)

            suitId = suit.doId

            # if suit.dna.name == 'lgator':

            #     if self.suitHasCondition(suitId, 'soakedcalculator') and self.suitHasCondition(suitId, 'unlureSuit') and not self.suitHasCondition(suitId, 'sounded') and suit.currHP > 0:
            #         attack = self.__getLureRemovalSquirt(suitId)
            #         if attack[SUIT_ATK_COL]:
                        # self.battle.suitAttacks.append(attack)

            #     if self.suitHasCondition(suitId, 'soakedcalculator') and suit.currHP > 0:
            #         attack = self.__getCheatAttack(suitId, {
            #             'suitName': suit.dna.name,
            #             'name': 'LitigatorSnapSoak',
            #             'animName': 'throw-object',
            #             'hp': 0,
            #             'acc': 100,
            #             'freq': 0,
            #             'group': SuitBattleGlobals.ATK_TGT_GROUP
            #         })
            # #         if attack[SUIT_ATK_COL]:
                        # self.battle.suitAttacks.append(attack)
            # if suit.dna.name == 'phouse': #powerhouse
            #     if self.suitHasCondition(suitId, 'soakedcalculator') and self.suitHasCondition(suitId, 'unlureSuit') and not self.suitHasCondition(suitId, 'sounded') and suit.currHP > 0:
            #         attack = self.__getLureRemovalSquirt(suitId)
            #         if attack[SUIT_ATK_COL]:
                        # self.battle.suitAttacks.append(attack)
            #     if self.suitHasCondition(suitId, 'soakedcalculator') and suit.currHP > 0:
            #         attack = self.__getCheatAttack(suitId, {'suitName': suit.dna.name,
            #                                 'name': 'PowerhouseSnipeCollectCall',  # Generation
            #                                 'animName': 'nothing',
            #                                 'hp': 0,
            #                                 'acc': 100,
            #                                 'freq': 0,
            #                                 'group': SuitBattleGlobals.ATK_TGT_SINGLE})
            #         if attack[SUIT_ATK_COL]:
                        # self.battle.suitAttacks.append(attack)

        for i in range(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'phouse':
                if self.suitHasCondition(suitId, 'soakedcalculator') and not self.suitHasCondition(suitId, 'sounded') and self.suitHasCondition(suitId, 'unlureSuit') and self.__suitCanAttack(suitId) and  self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getLureRemovalSquirt(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'soakedcalculator') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': suit.dna.name,
                                            'name': 'PowerhouseSnipeCollectCall',  # Generation
                                            'animName': 'nothing',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'lgator':
                if self.suitHasCondition(suitId, 'soakedcalculator') and self.suitHasCondition(suitId, 'unlureSuit') and not self.suitHasCondition(suitId, 'sounded') and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getLureRemovalSquirt(suitId)
                    if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'soakedcalculator') and self.battle.activeSuits[i].currHP > 0:
                    self.__appendToonConditionDamageAndRetaliation(
                        condition='soakToon',
                        damage=0,
                        damageMovie=None,
                        retaliations=[
                            {
                                'suitNames': ['lgator'],
                                'movie': 'LitigatorSnapSoak',
                                'animName': 'throw-object',
                                'hp': 33,
                                'queueCondition': 'nothing',
                            }
                        ]
                    )
                # attack = self.__getCheatAttack(suitId, {
                #     'suitName': self.battle.activeSuits[i].dna.name,
                #     'name': 'LitigatorSnapSoak',
                #     'animName': 'throw-object',
                #     'hp': 0,
                #     'acc': 100,
                #     'freq': 0,
                #     'group': SuitBattleGlobals.ATK_TGT_GROUP
                # })
                # if attack[SUIT_ATK_COL]:
                        # self.battle.suitAttacks.append(attack)

        self.absorbDamageByTrack[SQUIRT] = 0

    def calculateSuitAttacksAfterZap(self):
        for i in range(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
        for i in range(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'videog':
                damageCogs = 0
                for suit in self.battle.activeSuits:
                    if not suit.dna.name in ['director', 'fmaker', 'choreo', 'cinema']:
                        continue
                    if suit.getHP() > 0 and suit.dna.name in ['director', 'fmaker', 'choreo', 'cinema']:
                        damageCogs = 1
                if damageCogs == 0:
                    self.setSuitCondition(suitId, 'immunecalculator', 1, 1, 'setBoth')
            if self.battle.activeSuits[i].dna.name == 'hroller':
                damageCogs = 0
                for suit in self.battle.activeSuits:
                    if suit.dna.name != 'hrollers':
                        continue
                    if suit.getHP() > 0 and suit.dna.name == 'hrollers':
                        damageCogs = 1
                if damageCogs == 0:
                    self.setSuitCondition(suitId, 'HRdamagereduction', 0, 0, 'setBoth')
            if self.battle.activeSuits[i].dna.name == 'director':
                damageCogs = 0
                for suit in self.battle.activeSuits:
                    if suit.dna.name not in ['choreo', 'fmaker', 'cinema']:
                        continue
                    if suit.getHP() > 0 and suit.dna.name in ['choreo', 'fmaker', 'cinema']:
                        damageCogs = 1
                if damageCogs == 0:
                    self.setSuitCondition(suitId, 'directorDamageReduction', 0, 0, 'setBoth')
        for suit in self.battle.activeSuits:
            suitId = suit.doId
            self.__queueGagBanRetaliation(suit, 'Zap')
            self.__queueAbsorbMovieForTrack(suit, 'Zap', ZAP)

            # if suit.dna.name == 'dking':
            #     if self.suitHasCondition(suitId, 'zappedcalculator') and self.suitHasCondition(suitId, 'unlureSuit') and not self.suitHasCondition(suitId, 'sounded') and suit.currHP > 0:
            #         attack = self.__getLureRemovalZap(suitId)
            #         if attack[SUIT_ATK_COL]:
                        # self.battle.suitAttacks.append(attack)
            #     if self.suitHasCondition(suitId, 'zappedcalculator') and self.__suitCanAttack(suitId):
            #         attack = self.__getCheatAttack(suitId, {
            #             'suitName': suit.dna.name,
            #             'name': 'DividendZapRetaliation',
            #             'animName': 'glower',
            #             'hp': 0,
            #             'acc': 100,
            #             'freq': 0,
            #             'group': SuitBattleGlobals.ATK_TGT_GROUP
            #         })
            #         if attack[SUIT_ATK_COL]:
                        # self.battle.suitAttacks.append(attack)
            if suit.dna.name == 'phouse': #powerhouse
                if self.suitHasCondition(suitId, 'zappedcalculator') and self.suitHasCondition(suitId, 'unlureSuit') and not self.suitHasCondition(suitId, 'sounded') and suit.currHP > 0:
                    attack = self.__getLureRemovalZap(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'zappedcalculator') and suit.currHP > 0:
                    attack = self.__getCheatAttack(suitId, {'suitName': suit.dna.name,
                                            'name': 'PowerhouseGeneration',  # Generation
                                            'animName': 'nothing',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)

        self.absorbDamageByTrack[ZAP] = 0


    def calculateSuitAttacksAfterSound(self):
        for i in range(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'videog':
                damageCogs = 0
                for suit in self.battle.activeSuits:
                    if not suit.dna.name in ['director', 'fmaker', 'choreo', 'cinema']:
                        continue
                    if suit.getHP() > 0 and suit.dna.name in ['director', 'fmaker', 'choreo', 'cinema']:
                        damageCogs = 1
                if damageCogs == 0:
                    self.setSuitCondition(suitId, 'immunecalculator', 1, 1, 'setBoth')
            if self.battle.activeSuits[i].dna.name == 'hroller':
                damageCogs = 0
                for suit in self.battle.activeSuits:
                    if suit.dna.name != 'hrollers':
                        continue
                    if suit.getHP() > 0 and suit.dna.name == 'hrollers':
                        damageCogs = 1
                if damageCogs == 0:
                    self.setSuitCondition(suitId, 'HRdamagereduction', 0, 0, 'setBoth')
            if self.battle.activeSuits[i].dna.name == 'director':
                damageCogs = 0
                for suit in self.battle.activeSuits:
                    if suit.dna.name not in ['choreo', 'fmaker', 'cinema']:
                        continue
                    if suit.getHP() > 0 and suit.dna.name in ['choreo', 'fmaker', 'cinema']:
                        damageCogs = 1
                if damageCogs == 0:
                    self.setSuitCondition(suitId, 'directorDamageReduction', 0, 0, 'setBoth')
        for suit in self.battle.activeSuits:
            self.__queueGagBanRetaliation(suit, 'Sound')
            self.__queueAbsorbMovieForTrack(suit, 'Sound', SOUND)

        for i in range(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'supervis' and self.battle.activeSuits[i].getActualLevel() == 27:
                if self.suitHasCondition(suitId, 'soundcalculator') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'MintLedger',
                                                            'animName': 'glower',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_GROUP})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'liquid':
                if self.suitHasCondition(suitId, 'soundcalculator') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'TollmasterLedgerOfSound',  # Budget Cuts Gag Ban Retaliation
                                                            'animName': 'glower',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_GROUP,
                                                                'requiredToonConditions': (
                                                                            'usedSound',
                                                                        )})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)

        self.absorbDamageByTrack[SOUND] = 0


    def calculateSuitAttacksAfterDrop(self):
        for i in range(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if (self.suitHasCondition(suitId, 'overseerKB') or self.suitHasCondition(suitId, 'overseerCombo')) and (self.comboDamage > 0 or self.knockbackDamage > 0) and self.battle.activeSuits[i].currHP > 0:
                attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                        'name': 'AttorneyOverseerDrop',  # Overseer Combo/Knockback Heal Movie
                                        'animName': 'nothing',
                                        'hp': 0,
                                        'acc': 100,
                                        'freq': 0,
                                        'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                            'targetType': 'suit',
                            'allowSelfTarget': True,
                            'targetSelf': True,
                            'damageTarget': 'target',
                            'healTarget': 'target'})
                if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
        for i in range(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'hrollers' and self.battle.activeSuits[i].getActualLevel() == 26:
                if (self.comboDamage > 0) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'ComboDrop',  # Overseer Combo/Knockback Heal Movie
                                            'animName': 'nothing',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                                        'targetType': 'none'})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                    self.comboDamage *= 0
            if self.battle.activeSuits[i].dna.name == 'videog':
                damageCogs = 0
                for suit in self.battle.activeSuits:
                    if not suit.dna.name in ['director', 'fmaker', 'choreo', 'cinema']:
                        continue
                    if suit.getHP() > 0 and suit.dna.name in ['director', 'fmaker', 'choreo', 'cinema']:
                        damageCogs = 1
                if damageCogs == 0:
                    self.setSuitCondition(suitId, 'immunecalculator', 1, 1, 'setBoth')
            if self.battle.activeSuits[i].dna.name == 'hroller':
                damageCogs = 0
                for suit in self.battle.activeSuits:
                    if suit.dna.name != 'hrollers':
                        continue
                    if suit.getHP() > 0 and suit.dna.name == 'hrollers':
                        damageCogs = 1
                if damageCogs == 0:
                    self.setSuitCondition(suitId, 'HRdamagereduction', 0, 0, 'setBoth')
            if self.battle.activeSuits[i].dna.name == 'director':
                damageCogs = 0
                for suit in self.battle.activeSuits:
                    if suit.dna.name not in ['choreo', 'fmaker', 'cinema']:
                        continue
                    if suit.getHP() > 0 and suit.dna.name in ['choreo', 'fmaker', 'cinema']:
                        damageCogs = 1
                if damageCogs == 0:
                    self.setSuitCondition(suitId, 'directorDamageReduction', 0, 0, 'setBoth')
        for suit in self.battle.activeSuits:
            self.__queueGagBanRetaliation(suit, 'Drop')
            self.__queueAbsorbMovieForTrack(suit, 'Drop', DROP)

        self.absorbDamageByTrack[DROP] = 0

