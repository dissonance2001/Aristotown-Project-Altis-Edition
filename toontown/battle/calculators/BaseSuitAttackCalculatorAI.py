from toontown.battle.BattleBase import *
from toontown.battle.BattleGlobals import *
from toontown.battle import SuitBattleGlobals
from toontown.toonbase import ToontownBattleGlobals
from toontown.battle import StatusEffects
import random
import math

class BaseSuitAttackCalculatorAI:

    LEVEL_MOVIE_BY_TRACK = {
    LURE: 'AbsorbMovieLevelLure',
    THROW: 'AbsorbMovieLevelThrow',
    SQUIRT: 'AbsorbMovieLevelSquirt',
    ZAP: 'AbsorbMovieLevelZap',
    SOUND: 'AbsorbMovieLevelSound',
    DROP: 'AbsorbMovieLevelDrop'
}

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

    def __getAbilityQueued(self, suitId):
        return self.calculator.getAbilityQueued(suitId)

    def __getAbilityQueuedPreToon(self, suitId):
        return self.calculator.getAbilityQueuedPreToon(suitId)

    def __getGenericSuitAttack(self, suitId):
        return self.calculator.getGenericSuitAttack(suitId)

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

    def __getLureRemoval(self, suitId):
        return self.calculator.getLureRemoval(suitId)


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

    def calculateSuitAttacks(self):
        for i in xrange(len(self.battle.activeSuits)): # Cheats before Cog Attacks
            suitId = self.battle.activeSuits[i].doId
            x = self.TurnsElapsed
            attack = self.__getGenericSuitAttack(suitId)
            if self.battle.activeSuits[i].dna.name == 'videog':
                if not self.suitHasCondition(suitId, 'sounded') and self.suitHasCondition(suitId, 'unlureSuit') and self.suitHasCondition(suitId, 'bannedGagUsed') and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getLureRemoval(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'bannedGagUsed') and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'VideographerElectricShock3',  # Snap Bindings Retaliation
                                                            'animName': 'nothing',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'erfit':
                if not self.suitHasCondition(suitId, 'sounded') and self.suitHasCondition(suitId, 'unlureSuit') and (x + 2) % 3 == 0 and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getLureRemoval(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if (x + 2) % 3 == 0 and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                'name': 'ErfitHydrationCheck',  # Extra Tip
                                                                'animName': 'throw-object',
                                                                'hp': 0,
                                                                'acc': 100,
                                                                'freq': 0,
                                                                'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.suitHasCondition(suitId, 'attorneyKB') and self.objectionDamage > 0 and not self.suitHasCondition(suitId, 'dead'):
                attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                        'name': 'AttorneyObjection',  # Head Attorney Objection
                                        'animName': 'objection',
                                        'hp': 0,
                                        'acc': 100,
                                        'freq': 0,
                                        'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                roll = random.randint(0, 100)
                if roll > 10:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                           'name': 'AttorneyObjectionSustained',  # Head Attorney Objection
                                                                           'animName': 'magic1',
                                                                           'hp': 0,
                                                                           'acc': 100,
                                                                           'freq': 0,
                                                                           'group': SuitBattleGlobals.ATK_TGT_GROUP})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                    self.battle.activeSuits[i].setHP(self.battle.activeSuits[i].currHP + self.objectionDamage)
                    self.objectionDamage = 0
                else:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                        'name': 'AttorneyObjectionOverruled',  # Head Attorney Objection
                                                        'animName': 'frustrated',
                                                        'hp': 0,
                                                        'acc': 100,
                                                        'freq': 0,
                                                        'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                    self.objectionDamage = 0
            if self.suitHasCondition(suitId, 'overpressure') and self.battle.activeSuits[i].currHP <= 0:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'SafetyOverpressureDeath', # Heat Wave
                     'animName': 'nothing',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].getGovernaught() and self.battle.activeSuits[i].currHP <= 0 and not self.suitHasCondition(suitId, 'alreadyGovDeath'):
                for suit in self.battle.activeSuits:
                    if suit.getGovernaught():
                        if suit.currHP <= 0:
                            self.calculator.governaughtCogs += 1
                attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                        'name': 'GovernaughtDeath',  # Governaught Death Gag Damage Boost
                                        'animName': 'nothing',
                                        'hp': 0,
                                        'acc': 100,
                                        'freq': 0,
                                        'group': SuitBattleGlobals.ATK_TGT_GROUP})
                if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'std2' and self.battle.activeSuits[i].currHP <= 0 and not self.suitHasCondition(suitId, 'alreadyGovDeath'):
                for suit in self.battle.activeSuits:
                    if suit.getGovernaught():
                        if suit.currHP <= 0:
                            self.calculator.governaughtCogs += 1
                attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                        'name': 'GovernaughtDeath',  # Governaught Death Gag Damage Boost
                                        'animName': 'nothing',
                                        'hp': 0,
                                        'acc': 100,
                                        'freq': 0,
                                        'group': SuitBattleGlobals.ATK_TGT_GROUP})
                if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'mh2' and self.battle.activeSuits[i].currHP <= 0 and not self.suitHasCondition(suitId, 'alreadyGovDeath'):
                for suit in self.battle.activeSuits:
                    if suit.getGovernaught():
                        if suit.currHP <= 0:
                            self.calculator.governaughtCogs += 1
                attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                        'name': 'GovernaughtDeath',  # Governaught Death Gag Damage Boost
                                        'animName': 'nothing',
                                        'hp': 0,
                                        'acc': 100,
                                        'freq': 0,
                                        'group': SuitBattleGlobals.ATK_TGT_GROUP})
                if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'cnd2' and self.battle.activeSuits[i].currHP <= 0 and not self.suitHasCondition(suitId, 'alreadyGovDeath'):
                for suit in self.battle.activeSuits:
                    if suit.getGovernaught():
                        if suit.currHP <= 0:
                            self.calculator.governaughtCogs += 1
                attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                        'name': 'GovernaughtDeath',  # Governaught Death Gag Damage Boost
                                        'animName': 'nothing',
                                        'hp': 0,
                                        'acc': 100,
                                        'freq': 0,
                                        'group': SuitBattleGlobals.ATK_TGT_GROUP})
                if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'videog':
                for s in self.battle.activeSuits:
                    if self.suitHasCondition(s.doId, 'starOfTheShow'):
                        if s.currHP <= 0:
                            self.setSuitCondition(suitId, 'phantomDeath', s.maxHP, 10, 'setBoth')
                if self.suitHasCondition(suitId, 'phantomDeath') and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'VideographerElectricShock2',  # Snap Bindings Retaliation
                                                            'animName': 'nothing',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'rkeeper':
                for s in self.battle.activeSuits:
                    if s.dna.name == 'cbutcher':
                        if s.currHP <= 0:
                            self.setSuitCondition(suitId, 'phantomDeath', 1, 10, 'setBoth')
                if self.suitHasCondition(suitId, 'phantomDeath') and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'RecordkeeperPhantomEntryDamage',  # Snap Bindings Retaliation
                                                            'animName': 'nothing',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.battle.activeSuits[i].currHP <= 0 and not self.suitHasCondition(suitId, 'alreadyDesperation2'):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'Desperation',  # Desperation Activation
                                                            'animName': 'nothing',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)

        for i in xrange(len(self.battle.activeSuits)):  # Cheats before Cog Attacks
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'cbutcher':
                for s in self.battle.activeSuits:
                    if s.dna.name == 'rkeeper':
                        if s.currHP <= 0:
                            if not self.suitHasCondition(suitId, 'sounded') and self.suitHasCondition(suitId, 'unlureSuit') and self.battle.activeSuits[i].currHP > 0:
                                attack = self.__getLureRemoval(suitId)
                                if attack[SUIT_ATK_COL]:
                                    self.battle.suitAttacks.append(attack)
                            if self.battle.activeSuits[i].currHP > 0:
                                attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                        'name': 'RecordkeeperPhantomEntrySacrifice',  # Audit
                                                                        'animName': 'nothing',
                                                                        'hp': 0,
                                                                        'acc': 100,
                                                                        'freq': 0,
                                                                        'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                                if attack[SUIT_ATK_COL]:
                                    self.battle.suitAttacks.append(attack)
            # if self.battle.activeSuits[i].dna.name == 'caseman':  # case manager
            #     if self.TurnsElapsed % 1 == 0:
            #         attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
            #          'name': 'CaseManagerCourtRecordBan', # Court Record Ban Retaliation
            #          'animName': 'nothing',
            #          'hp': 0,
            #          'acc': 100,
            #          'freq': 0,
            #          'group': SuitBattleGlobals.ATK_TGT_GROUP})
            #         if attack[SUIT_ATK_COL]:
            #             self.battle.suitAttacks.append(attack)
            # # if self.battle.activeSuits[i].dna.name == 'stenog':
            # #     if self.TurnsElapsed % 1 == 0:
            # #         attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
            # #          'name': 'StenographerCourtRecordBan', # Court Record Retaliation
            # #          'animName': 'nothing',
            # #          'hp': 0,
            # #          'acc': 100,
            # #          'freq': 0,
            # #          'group': SuitBattleGlobals.ATK_TGT_GROUP})
            # #         if attack[SUIT_ATK_COL]:
            #             self.battle.suitAttacks.append(attack)
            # # if self.battle.activeSuits[i].dna.name == 'ovt' and self.battle.activeSuits[i].currHP > 0:  # Mint Supervisor Life Insurance
            # #     if not self.suitHasCondition(suitId, 'sounded') and self.suitHasCondition(suitId, 'unlureSuit'):
            # #         attack = self.__getLureRemoval(suitId)
            # #         if attack[SUIT_ATK_COL]:
            #             self.battle.suitAttacks.append(attack)
            # #     attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
            # #                                                 'name': 'MintHurrySickness',
            # #                                                 'animName': 'finger-wag',
            # #                                                 'hp': 0,
            # #                                                 'acc': 100,
            # #                                                 'freq': 0,
            # #                                                 'group': SuitBattleGlobals.ATK_TGT_GROUP})
            # #     if attack[SUIT_ATK_COL]:
            #             self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'clubpres':
                if self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                'name': 'PresidentTargetCheck',  # Target Check
                                                                'animName': 'nothing',
                                                                'hp': 0,
                                                                'acc': 100,
                                                                'freq': 0,
                                                                'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if not self.suitHasCondition(suitId, 'sounded') and self.suitHasCondition(suitId, 'unlureSuit') and (self.suitHasCondition(suitId, 'targetCheckCondition') and self.getSuitConditionModifier(suitId, 'targetCheckCondition') > -1) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getLureRemoval(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'targetCheckCondition') and self.getSuitConditionModifier(suitId, 'targetCheckCondition') > -1 and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'PresidentExtraTip',  # Extra Tip
                                                            'animName': 'throw-paper',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'target3'):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'PresidentExtraTip2',  # Extra Tip
                                                            'animName': 'throw-paper',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'target4'):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'PresidentExtraTip3',  # Extra Tip
                                                            'animName': 'throw-paper',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'target5'):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'PresidentExtraTip4',  # Extra Tip
                                                            'animName': 'throw-paper',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'target6'):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'PresidentExtraTip5',  # Extra Tip
                                                            'animName': 'throw-paper',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'target7'):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'PresidentExtraTip6',  # Extra Tip
                                                            'animName': 'throw-paper',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'clerk' and self.battle.activeSuits[i].getActualLevel() == 25:  # Mint Supervisor Life Insurance
                if not self.suitHasCondition(suitId, 'sounded') and self.suitHasCondition(suitId, 'unlureSuit') and self.suitHasCondition(suitId, 'laborious') and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getLureRemoval(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'laborious') and not self.suitHasCondition(suitId, 'alreadyHurrySickness') and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'AttorneyHurrySickness',
                                                            'animName': 'finger-wag',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_GROUP})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'dopr':
                if not self.suitHasCondition(suitId, 'sounded') and self.suitHasCondition(suitId, 'unlureSuit') and not self.suitHasCondition(suitId, 'doprHit') and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getLureRemoval(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if not self.suitHasCondition(suitId, 'doprHit') and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'DOPRAmbushMarketing',  # Extra Tip
                                                            'animName': 'victory',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'radiog':
                if self.suitHasCondition(suitId, 'overmodulatedcalculator') and not self.__suitCanAttack(suitId) and \
                        self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'overmodulatedcalculator') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'RadiographerDanceSession', # Target Check
                     'animName': 'nothing',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'overmodulatedcalculator') and not self.suitHasCondition(suitId, 'sounded') and self.suitHasCondition(suitId, 'unlureSuit') and self.__suitCanAttack(suitId) and (self.suitHasCondition(suitId, 'targetCheckCondition') and self.getSuitConditionModifier(suitId, 'targetCheckCondition') > -1):
                    attack = self.__getLureRemoval(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'overmodulatedcalculator') and not (self.suitHasCondition(suitId, 'targetCheckCondition') and self.getSuitConditionModifier(suitId, 'targetCheckCondition') > -1) and self.battle.activeSuits[i].currHP > 0 and self.__suitCanAttack(suitId):
                    attack = self.__getAbilityQueued(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'overmodulatedcalculator') and self.suitHasCondition(suitId, 'targetCheckCondition') and self.getSuitConditionModifier(suitId, 'targetCheckCondition') > -1 and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'RadiographerOvermodulated', # Overmodulated
                     'animName': 'sanction',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                # if self.suitHasCondition(suitId, 'target3'):
                #     attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                #                                             'name': 'RadiographerOvermodulated2',  # Overmodulated
                #                                             'animName': 'sanction',
                #                                             'hp': 0,
                #                                             'acc': 100,
                #                                             'freq': 0,
                #                                             'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                #     if attack[SUIT_ATK_COL]:
                        # self.battle.suitAttacks.append(attack)
                # if self.suitHasCondition(suitId, 'target4'):
                #     attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                #                                             'name': 'RadiographerOvermodulated3',  # Overmodulated
                #                                             'animName': 'sanction',
                #                                             'hp': 0,
                #                                             'acc': 100,
                #                                             'freq': 0,
                #                                             'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                #     if attack[SUIT_ATK_COL]:
                        # self.battle.suitAttacks.append(attack)
                # if self.suitHasCondition(suitId, 'target5'):
                #     attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                #                                             'name': 'RadiographerOvermodulated4',  # Overmodulated
                #                                             'animName': 'sanction',
                #                                             'hp': 0,
                #                                             'acc': 100,
                #                                             'freq': 0,
                #                                             'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                #     if attack[SUIT_ATK_COL]:
                        # self.battle.suitAttacks.append(attack)
                # if self.suitHasCondition(suitId, 'target6'):
                #     attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                #                                             'name': 'RadiographerOvermodulated5',  # Overmodulated
                #                                             'animName': 'sanction',
                #                                             'hp': 0,
                #                                             'acc': 100,
                #                                             'freq': 0,
                #                                             'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                #     if attack[SUIT_ATK_COL]:
                        # self.battle.suitAttacks.append(attack)
                # if self.suitHasCondition(suitId, 'overmodulatedcalculator2') and not len(self.battle.activeSuits) > 1 and self.battle.activeSuits[i].currHP > 0 and self.__suitCanAttack(suitId):
                #     attack = self.__getAbilityQueued(suitId)
                #     if attack[SUIT_ATK_COL]:
                        # self.battle.suitAttacks.append(attack)
                # if self.suitHasCondition(suitId, 'overmodulatedcalculator2') and not self.__suitCanAttack(suitId) and \
                #         self.battle.activeSuits[i].currHP > 0:
                #     attack = self.__getAbilityQueued(suitId)
                #     if attack[SUIT_ATK_COL]:
                        # self.battle.suitAttacks.append(attack)
                # if self.suitHasCondition(suitId, 'overmodulatedcalculator2') and self.__suitCanAttack(suitId):
                #     attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                #      'name': 'PresidentTargetCheck', # Target Check
                #      'animName': 'nothing',
                #      'hp': 0,
                #      'acc': 100,
                #      'freq': 0,
                #      'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                #     if attack[SUIT_ATK_COL]:
                        # self.battle.suitAttacks.append(attack)
                # if not self.suitHasCondition(suitId, 'sounded') and self.suitHasCondition(suitId, 'unlureSuit') and self.__suitCanAttack(suitId) and (self.suitHasCondition(suitId, 'target2')
                # or self.suitHasCondition(suitId, 'target3') or self.suitHasCondition(suitId, 'target4') or self.suitHasCondition(suitId, 'target5') or self.suitHasCondition(suitId, 'target6')):
                #     attack = self.__getLureRemoval(suitId)
                #     if attack[SUIT_ATK_COL]:
                        # self.battle.suitAttacks.append(attack)
                # if self.suitHasCondition(suitId, 'target2'):
                #     attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                #      'name': 'RadiographerOvermodulated', # Overmodulated
                #      'animName': 'sanction',
                #      'hp': 0,
                #      'acc': 100,
                #      'freq': 0,
                #      'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                #     if attack[SUIT_ATK_COL]:
                        # self.battle.suitAttacks.append(attack)
                # if self.suitHasCondition(suitId, 'target3'):
                #     attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                #                                             'name': 'RadiographerOvermodulated2',  # Overmodulated
                #                                             'animName': 'sanction',
                #                                             'hp': 0,
                #                                             'acc': 100,
                #                                             'freq': 0,
                #                                             'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                #     if attack[SUIT_ATK_COL]:
                        # self.battle.suitAttacks.append(attack)
                # if self.suitHasCondition(suitId, 'target4'):
                #     attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                #                                             'name': 'RadiographerOvermodulated3',  # Overmodulated
                #                                             'animName': 'sanction',
                #                                             'hp': 0,
                #                                             'acc': 100,
                #                                             'freq': 0,
                #                                             'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                #     if attack[SUIT_ATK_COL]:
                        # self.battle.suitAttacks.append(attack)
                # if self.suitHasCondition(suitId, 'target5'):
                #     attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                #                                             'name': 'RadiographerOvermodulated4',  # Overmodulated
                #                                             'animName': 'sanction',
                #                                             'hp': 0,
                #                                             'acc': 100,
                #                                             'freq': 0,
                #                                             'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                #     if attack[SUIT_ATK_COL]:
                        # self.battle.suitAttacks.append(attack)
                # if self.suitHasCondition(suitId, 'target6'):
                #     attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                #                                             'name': 'RadiographerOvermodulated5',  # Overmodulated
                #                                             'animName': 'sanction',
                #                                             'hp': 0,
                #                                             'acc': 100,
                #                                             'freq': 0,
                #                                             'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                #     if attack[SUIT_ATK_COL]:
                        # self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'racket':
                if not self.suitHasCondition(suitId, 'sounded') and self.suitHasCondition(suitId, 'unlureSuit') and self.__suitCanAttack(suitId):
                    attack = self.__getLureRemoval(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'RacketeerOverextendedLeverage',  # Extortion
                                                            'animName': 'nothing',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'dking': # dividend king
                if not self.suitHasCondition(suitId, 'sounded') and self.suitHasCondition(suitId, 'unlureSuit') and self.__suitCanAttack(suitId):
                    attack = self.__getLureRemoval(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.__suitCanAttack(suitId):
                    roll = random.randint(0, 100)
                    if roll > 50:
                        attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                        'name': 'PowerhouseSyphonDesperation', # Desperation Syphon For All Cogs
                        'animName': 'snap',
                        'hp': 0,
                        'acc': 100,
                        'freq': 0,
                        'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
            # if self.battle.activeSuits[i].dna.name == 'racket':
            #     if not self.suitHasCondition(suitId, 'sounded') and self.suitHasCondition(suitId, 'unlureSuit') and self.__suitCanAttack(suitId):
            #         attack = self.__getLureRemoval(suitId)
            #         if attack[SUIT_ATK_COL]:
                        # self.battle.suitAttacks.append(attack)
            #     if self.TurnsElapsed % 1 == 0 and self.__suitCanAttack(suitId):
            #         attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
            #             'name': 'RacketeerPeckingOrderRetaliation', # Retaliation to Gag Bans
            #             'animName': 'throw-object',
            #             'hp': 0,
            #             'acc': 100,
            #             'freq': 0,
            #             'group': SuitBattleGlobals.ATK_TGT_GROUP})
            #         if attack[SUIT_ATK_COL]:
                        # self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'wtapper':
                self.__appendToonConditionDamageAndRetaliation(
                    condition='collectcalled',
                    damage=25,
                    damageMovie=None,
                    retaliations=[
                        {
                            'suitNames': ['wtapper'],
                            'movie': 'WiretapperBusySignal',
                            'animName': 'snap',
                            'hp': 25,
                        }
                    ]
                )
                # if self.suitHasCondition(suitId, 'collectcalled') and not self.suitHasCondition(suitId, 'wiretapperHit2') and self.battle.activeSuits[
                #     i].currHP > 0:
                #     attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                #                                             'name': 'WiretapperBusySignal',  # Busy Signal
                #                                             'animName': 'snap',
                #                                             'hp': 0,
                #                                             'acc': 100,
                #                                             'freq': 0,
                #                                             'group': SuitBattleGlobals.ATK_TGT_GROUP})
                #     if attack[SUIT_ATK_COL]:
                        # self.battle.suitAttacks.append(attack)
                self.setSuitCondition(suitId, 'collectcalled', 0, 0, 'setBoth')
                # if self.TurnsElapsed % 1 == 0:
                #     attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                #      'name': 'WiretapperGagBan', # Budget Cuts Gag Ban Retaliation
                #      'animName': 'nothing',
                #      'hp': 0,
                #      'acc': 100,
                #      'freq': 0,
                #      'group': SuitBattleGlobals.ATK_TGT_GROUP})
                #     if attack[SUIT_ATK_COL]:
                        # self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'liquid':
                if self.TurnsElapsed % 1 == 0 and not self.suitHasCondition(suitId, 'sounded') and self.suitHasCondition(suitId, 'unlureSuit') and self.__suitCanAttack(suitId) and self.battle.activeSuits[
                    i].currHP > 0:
                    attack = self.__getLureRemoval(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.TurnsElapsed % 1 == 0 and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'TollmasterMissedPayment',  # Budget Cuts Gag Ban Retaliation
                                                            'animName': 'pick-pocket',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_GROUP})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'foreman':
                if not self.suitHasCondition(suitId, 'sounded') and self.suitHasCondition(suitId, 'unlureSuit') and self.getSuitConditionTurns(suitId, 'explosive') == 1 and self.suitHasCondition(suitId, 'explosive'):
                    attack = self.__getLureRemoval(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.battle.activeSuits[i].currHP > 0 and self.getSuitConditionTurns(suitId, 'explosive') == 1 and self.suitHasCondition(suitId, 'explosive'):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'ForemanExplosion',
                                                            'animName': 'nothing',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_GROUP})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
        
        for i in xrange(len(self.battle.activeSuits)): # Regular Manager Attacks
            suitId = self.battle.activeSuits[i].doId
            x = self.TurnsElapsed
            #attack = self.__getGenericSuitAttack(suitId)
            # Managers Attack Before Cogs
            if self.battle.activeSuits[i].dna.name == 'erfit' and not self.suitHasCondition(suitId, 'sounded') and self.suitHasCondition(suitId, 'unlureSuit') and self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                attack = self.__getLureRemoval(suitId)
                if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'erfit' and not self.suitHasCondition(suitId, 'deepfreeze') and self.__suitCanAttack(suitId):
                attack = self.__getGenericSuitAttack(suitId)
                if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'erfit' and self.syphonHP.get(suitId, 0) > 0 and not self.suitHasCondition(suitId, 'dead') and self.battle.activeSuits[i].currHP > 0 and self.__suitCanAttack(suitId):
                attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                 'name': 'ErfitProToonShake', # Syphon Movie
                 'animName': 'nothing',
                 'hp': 0,
                 'acc': 100,
                 'freq': 0, # Professor Control: I do not know how relevant attack frequency is, but keep it anyway.
                 'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.suitHasCondition(suitId, 'erfitHeal') and self.battle.activeSuits[i].currHP > 0:
                attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                 'name': 'ErfitPhase2', # Syphon Movie
                 'animName': 'nothing',
                 'hp': 0,
                 'acc': 100,
                 'freq': 0, # Professor Control: I do not know how relevant attack frequency is, but keep it anyway.
                 'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)

        for i in xrange(len(self.battle.activeSuits)): # Regular Manager Attacks
            suitId = self.battle.activeSuits[i].doId
            x = self.TurnsElapsed
            #attack = self.__getGenericSuitAttack(suitId)
            # Managers Attack Before Cogs
            if self.battle.activeSuits[i].dna.name in SuitBattleGlobals.SpecialCogDict and not (self.battle.activeSuits[i].dna.name == 'psetter' and self.battle.activeSuits[i].currHP >= 12750) and not self.suitHasCondition(suitId, 'sounded') and self.suitHasCondition(suitId, 'unlureSuit') and self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                attack = self.__getLureRemoval(suitId)
                if attack[SUIT_ATK_COL]:
                    self.battle.suitAttacks.append(attack)
            specialCogCanUseRegularAttack = not (self.battle.activeSuits[i].dna.name == 'psetter' and self.battle.activeSuits[i].currHP >= 12750)
            if self.battle.activeSuits[i].dna.name == 'psetter':
                pacesetterHasRealToonAction = False
                for toonId in self.battle.activeToons:
                    toonAttack = self.battle.toonAttacks.get(toonId)
                    if toonAttack and toonAttack[TOON_TRACK_COL] != NO_ATTACK:
                        pacesetterHasRealToonAction = True
                        break
                specialCogCanUseRegularAttack = (
                    self.battle.activeSuits[i].currHP < 12750 or
                    self.suitHasCondition(suitId, 'openingChallengeCancelled') or
                    self.suitHasCondition(suitId, 'overclocked') or
                    pacesetterHasRealToonAction)
            if self.battle.activeSuits[i].dna.name in SuitBattleGlobals.SpecialCogDict and specialCogCanUseRegularAttack and not self.suitHasCondition(suitId, 'deepfreeze') and self.__suitCanAttack(suitId) and not self.battle.activeSuits[i].dna.name == 'erfit' and not (self.battle.activeSuits[i].dna.name == 'videog' and self.suitHasCondition(suitId, 'immune')) and not self.battle.activeSuits[i].dna.name == 'hrollers' and not self.battle.activeSuits[i].dna.name == 'phouse':
                attack = self.__getGenericSuitAttack(suitId)
                if attack[SUIT_ATK_COL]:
                    self.battle.suitAttacks.append(attack)
                    if self.battle.activeSuits[i].dna.name == 'videog':
                        self.calculator.applyVideographerSilhouetteAttack(attack)
            if self.suitHasCondition(suitId, 'syphon') and self.battle.activeSuits[i].dna.name in SuitBattleGlobals.SpecialCogDict and self.syphonHP.get(suitId, 0) > 0 and not self.suitHasCondition(suitId, 'dead') and not self.battle.activeSuits[i].dna.name == 'phouse' and not self.battle.activeSuits[i].dna.name == 'safesupervis':
                attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                 'name': 'SyphonMovie', # Syphon Movie
                 'animName': 'nothing',
                 'hp': 0,
                 'acc': 100,
                 'freq': 0, # Professor Control: I do not know how relevant attack frequency is, but keep it anyway.
                 'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'erclaim' and self.syphonHP.get(suitId, 0) > 0 and not self.suitHasCondition(suitId, 'dead') and self.battle.activeSuits[i].currHP > 0 and self.__suitCanAttack(suitId):
                attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                 'name': 'ErclaimLaffSteal', # Syphon Movie
                 'animName': 'magic1',
                 'hp': 0,
                 'acc': 100,
                 'freq': 0, # Professor Control: I do not know how relevant attack frequency is, but keep it anyway.
                 'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)

        for i in xrange(len(self.battle.activeSuits)): # Regular Manager Attacks
            suitId = self.battle.activeSuits[i].doId
            x = self.TurnsElapsed
            # #attack = self.__getGenericSuitAttack(suitId)
            # if self.battle.activeSuits[i].dna.name == 'supervis' and self.battle.activeSuits[i].getActualLevel() == 25 and self.damageHP.get(suitId, 0) > 0:
            #     if self.__suitCanAttack(suitId):
            #         attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
            #                                                 'name': 'DamageMovie',  # Fraudulent Mint Supervisor
            #                                                 'animName': 'pie-small-react',
            #                                                 'hp': 0,
            #                                                 'acc': 100,
            #                                                 'freq': 0,
            #                                                 'group': SuitBattleGlobals.ATK_TGT_SINGLE})
            #         if attack[SUIT_ATK_COL]:
            #             self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'bcaster':
                if self.__suitCanAttack(suitId):
                    if self.suitHasCondition(suitId, 'schmoozecalculator'):
                        attack = self.__getCheatAttack(suitId, {'suitName': 'bcaster',
                         'name': 'Schmooze',
                         'animName': 'speak',
                         'hp': 32,
                         'acc': 85,
                         'freq': 0,
                         'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    if self.suitHasCondition(suitId, 'razzledazzlecalculator'):
                        attack = self.__getCheatAttack(suitId, {'suitName': 'bcaster',
                         'name': 'RazzleDazzle',
                         'animName': 'smile',
                         'hp': 34,
                         'acc': 85,
                         'freq': 0,
                         'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    if self.suitHasCondition(suitId, 'fingerwagcalculator'):
                        attack = self.__getCheatAttack(suitId, {'suitName': 'bcaster',
                         'name': 'FingerWag',
                         'animName': 'finger-wag',
                         'hp': 28,
                         'acc': 90,
                         'freq': 0,
                         'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    if self.suitHasCondition(suitId, 'cigarsmokecalculator'):
                        attack = self.__getCheatAttack(suitId, {'suitName': 'bcaster',
                         'name': 'CigarSmoke',
                         'animName': 'cigar-smoke',
                         'hp': 32,
                         'acc': 90,
                         'freq': 0,
                         'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    if self.suitHasCondition(suitId, 'songanddancecalculator'):
                        attack = self.__getCheatAttack(suitId, {'suitName': 'bcaster',
                         'name': 'SongAndDance',
                         'animName': 'song-and-dance',
                         'hp': 28,
                         'acc': 85,
                         'freq': 0,
                         'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    if self.suitHasCondition(suitId, 'beguilecalculator'):
                        attack = self.__getCheatAttack(suitId, {'suitName': 'bcaster',
                         'name': 'Beguile',
                         'animName': 'glower',
                         'hp': 30,
                         'acc': 95,
                         'freq': 0,
                         'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'hrollers':
                if self.__suitCanAttack(suitId):
                    if self.suitHasCondition(suitId, 'HRpowertrip'):
                        attack = self.__getCheatAttack(suitId, {'suitName': 'hrollers',
                         'name': 'HighRollerNoAttack',
                         'animName': 'nothing',
                         'hp': 0,
                         'acc': 100,
                         'freq': 0,
                         'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    else:
                        attack = self.__getCheatAttack(suitId, {'suitName': 'hrollers',
                         'name': 'PowerTrip',
                         'animName': 'magic1',
                         'hp': 50,
                         'acc': 85,
                         'freq': 0,
                         'group': SuitBattleGlobals.ATK_TGT_GROUP})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'phouse':  # powerhouse
                if self.__suitCanAttack(suitId):
                    roll = random.randint(0, 100)
                    if roll > 35:
                        attack = self.__getGenericSuitAttack(suitId)
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    else:
                        attack = self.__getCheatAttack(suitId, {'suitName': 'phouse',
                                                     'name': 'PowerhouseSnipeSoaked',
                                                    'animName': 'nothing',
                                                   'hp': 0,
                                                   'acc': 100,
                                                   'freq': 0,
                                                   'group': random.choice((SuitBattleGlobals.ATK_TGT_DOUBLE, SuitBattleGlobals.ATK_TGT_SINGLE))})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'syphon') and self.battle.activeSuits[i].dna.name in SuitBattleGlobals.SpecialCogDict and self.syphonHP.get(suitId, 0) > 0 and not self.suitHasCondition(suitId,
                                                                                                                                                                                           'dead'):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'SyphonMovie',  # Syphon Movie
                                                            'animName': 'nothing',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,  # Professor Control: I do not know how relevant attack frequency is, but keep it anyway.
                                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.__suitCanAttack(suitId) and self.damageHP.get(suitId, 0) > 0:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'DamageMovie',  # Fraudulent Mint Supervisor
                                                            'animName': 'pie-small-react',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)

            for i in xrange(len(self.battle.activeSuits)):  # Now, how about the other Cogs, including the one that just attacked?
                suitId = self.battle.activeSuits[i].doId
                if self.battle.activeSuits[i].dna.name == 'radiog':  # Sniper Factory Foreman
                    attack = self.__getCheatAttack(suitId, {'suitName': 'radiog',
                                                                'name': 'RadiographerHotTakeDamage',
                                                                'animName': 'nothing',
                                                                'hp': 0,
                                                                'acc': 100,
                                                                'freq': 0,
                                                                'group': SuitBattleGlobals.ATK_TGT_GROUP})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.battle.findSuit(suitId).dna.name == 'foreman' and self.battle.activeSuits[i].getActualLevel() == 25:  # Sniper Factory Foreman
                    if self.battle.activeSuits[i].currHP > 0 and not self.suitHasCondition(suitId, 'sounded') and self.suitHasCondition(suitId, 'unlureSuit'):
                        attack = self.__getLureRemoval(suitId)
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    if self.battle.activeSuits[i].currHP > 0:
                        attack = self.__getCheatAttack(suitId, {'suitName': 'foreman',
                                                                'name': 'ForemanSnipe',
                                                                'animName': 'glower',
                                                                'hp': 0,
                                                                'acc': 100,
                                                                'freq': 0,
                                                                'group': SuitBattleGlobals.ATK_TGT_GROUP})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                if self.battle.findSuit(suitId).dna.name == 'cdirector' and self.suitHasCondition(suitId, 'alreadySecondAttack'):  # Sniper Factory Foreman
                    if self.battle.activeSuits[i].currHP > 0 and not self.suitHasCondition(suitId, 'sounded') and self.suitHasCondition(suitId, 'unlureSuit') and self.suitHasCondition(suitId, 'soakedcalculator'):
                        attack = self.__getLureRemoval(suitId)
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    if self.battle.activeSuits[i].currHP > 0 and self.suitHasCondition(suitId, 'soakedcalculator'):
                        attack = self.__getCheatAttack(suitId, {'suitName': 'cdirector',
                                                                'name': 'ContingencyRiskThresholdBreach25',
                                                                'animName': 'glower',
                                                                'hp': 0,
                                                                'acc': 100,
                                                                'freq': 0,
                                                                'group': SuitBattleGlobals.ATK_TGT_GROUP})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                if self.battle.findSuit(suitId).dna.name == 'bkeeper' and self.suitHasCondition(suitId, 'soakedcalculator'):  # Sniper Factory Foreman
                    if self.battle.activeSuits[i].currHP > 0 and not self.suitHasCondition(suitId, 'sounded') and self.suitHasCondition(suitId, 'unlureSuit') and self.suitHasCondition(suitId, 'soakedcalculator'):
                        attack = self.__getLureRemoval(suitId)
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    if self.battle.activeSuits[i].currHP > 0 and self.suitHasCondition(suitId, 'soakedcalculator'):
                        attack = self.__getCheatAttack(suitId, {'suitName': 'bkeeper',
                                                                'name': 'BookkeeperPaperCutSoaked',
                                                                'animName': 'sanction',
                                                                'hp': 0,
                                                                'acc': 100,
                                                                'freq': 0,
                                                                'group': SuitBattleGlobals.ATK_TGT_GROUP})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                if self.battle.findSuit(suitId).dna.name == 'clubpres' and self.suitHasCondition(suitId, 'soakedcalculator') and self.battle.activeSuits[i].getActualLevel() == 27:  # Sniper Factory Foreman
                    if self.battle.activeSuits[i].currHP > 0 and not self.suitHasCondition(suitId, 'sounded') and self.suitHasCondition(suitId, 'unlureSuit') and self.suitHasCondition(suitId, 'soakedcalculator'):
                        attack = self.__getLureRemoval(suitId)
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    if self.battle.activeSuits[i].currHP > 0 and self.suitHasCondition(suitId, 'soakedcalculator'):
                        attack = self.__getCheatAttack(suitId, {'suitName': 'clubpres',
                                                                'name': 'PresidentLiability2',
                                                                'animName': 'sanction',
                                                                'hp': 0,
                                                                'acc': 100,
                                                                'freq': 0,
                                                                'group': SuitBattleGlobals.ATK_TGT_GROUP})
                        if attack[SUIT_ATK_COL]:
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
                if not self.battle.activeSuits[i].dna.name in SuitBattleGlobals.SpecialCogDict and not self.suitHasCondition(suitId, 'deepfreeze') and not self.suitHasCondition(suitId, 'sounded') and self.suitHasCondition(suitId, 'unlureSuit') and self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getLureRemoval(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if not self.battle.activeSuits[i].dna.name in SuitBattleGlobals.SpecialCogDict and not self.suitHasCondition(suitId, 'deepfreeze') and not self.suitHasCondition(suitId, 'sued'):
                    attack = self.__getGenericSuitAttack(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'syphon') and not self.battle.activeSuits[i].dna.name in SuitBattleGlobals.SpecialCogDict and self.syphonHP.get(suitId, 0) > 0 and not self.suitHasCondition(suitId, 'dead'):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'SyphonMovie',  # Syphon Movie
                                                            'animName': 'nothing',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,  # Professor Control: I do not know how relevant attack frequency is, but keep it anyway.
                                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.battle.activeSuits[i].dna.name == 'radiog':
                    if self.__suitCanAttack(suitId) and self.damageHP.get(suitId, 0) > 0:
                        attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                'name': 'DamageMovie',  # Damage Movie
                                                                'animName': 'nothing',
                                                                'hp': 0,
                                                                'acc': 100,
                                                                'freq': 0,
                                                                'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                for i in xrange(len(self.battle.activeSuits)):  # Now, how about the other Cogs, including the one that just attacked?
                    suitId = self.battle.activeSuits[i].doId
                    if self.battle.activeSuits[i].dna.name == 'radiog':  # Sniper Factory Foreman
                        attack = self.__getCheatAttack(suitId, {'suitName': 'radiog',
                                                                    'name': 'RadiographerHotTakeDamage',
                                                                    'animName': 'nothing',
                                                                    'hp': 0,
                                                                    'acc': 100,
                                                                    'freq': 0,
                                                                    'group': SuitBattleGlobals.ATK_TGT_GROUP})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    if self.battle.findSuit(suitId).dna.name == 'foreman' and self.battle.activeSuits[i].getActualLevel() == 25:  # Sniper Factory Foreman
                        if self.battle.activeSuits[i].currHP > 0 and not self.suitHasCondition(suitId, 'sounded') and self.suitHasCondition(suitId, 'unlureSuit'):
                            attack = self.__getLureRemoval(suitId)
                            if attack[SUIT_ATK_COL]:
                                self.battle.suitAttacks.append(attack)
                        if self.battle.activeSuits[i].currHP > 0:
                            attack = self.__getCheatAttack(suitId, {'suitName': 'foreman',
                                                                    'name': 'ForemanSnipe',
                                                                    'animName': 'glower',
                                                                    'hp': 0,
                                                                    'acc': 100,
                                                                    'freq': 0,
                                                                    'group': SuitBattleGlobals.ATK_TGT_GROUP})
                            if attack[SUIT_ATK_COL]:
                                self.battle.suitAttacks.append(attack)
                    if self.battle.findSuit(suitId).dna.name == 'cdirector' and self.suitHasCondition(suitId, 'alreadySecondAttack'):  # Sniper Factory Foreman
                        if self.battle.activeSuits[i].currHP > 0 and not self.suitHasCondition(suitId, 'sounded') and self.suitHasCondition(suitId, 'unlureSuit') and self.suitHasCondition(suitId, 'soakedcalculator'):
                            attack = self.__getLureRemoval(suitId)
                            if attack[SUIT_ATK_COL]:
                                self.battle.suitAttacks.append(attack)
                        if self.battle.activeSuits[i].currHP > 0 and self.suitHasCondition(suitId, 'soakedcalculator'):
                            attack = self.__getCheatAttack(suitId, {'suitName': 'cdirector',
                                                                    'name': 'ContingencyRiskThresholdBreach25',
                                                                    'animName': 'glower',
                                                                    'hp': 0,
                                                                    'acc': 100,
                                                                    'freq': 0,
                                                                    'group': SuitBattleGlobals.ATK_TGT_GROUP})
                            if attack[SUIT_ATK_COL]:
                                self.battle.suitAttacks.append(attack)
                    if self.battle.findSuit(suitId).dna.name == 'bkeeper' and self.suitHasCondition(suitId, 'soakedcalculator'):  # Sniper Factory Foreman
                        if self.battle.activeSuits[i].currHP > 0 and not self.suitHasCondition(suitId, 'sounded') and self.suitHasCondition(suitId, 'unlureSuit') and self.suitHasCondition(suitId, 'soakedcalculator'):
                            attack = self.__getLureRemoval(suitId)
                            if attack[SUIT_ATK_COL]:
                                self.battle.suitAttacks.append(attack)
                        if self.battle.activeSuits[i].currHP > 0 and self.suitHasCondition(suitId, 'soakedcalculator'):
                            attack = self.__getCheatAttack(suitId, {'suitName': 'bkeeper',
                                                                    'name': 'BookkeeperPaperCutSoaked',
                                                                    'animName': 'sanction',
                                                                    'hp': 0,
                                                                    'acc': 100,
                                                                    'freq': 0,
                                                                    'group': SuitBattleGlobals.ATK_TGT_GROUP})
                            if attack[SUIT_ATK_COL]:
                                self.battle.suitAttacks.append(attack)
                    if self.battle.findSuit(suitId).dna.name == 'clubpres' and self.suitHasCondition(suitId, 'soakedcalculator') and self.battle.activeSuits[i].getActualLevel() == 27:  # Sniper Factory Foreman
                        if self.battle.activeSuits[i].currHP > 0 and not self.suitHasCondition(suitId, 'sounded') and self.suitHasCondition(suitId, 'unlureSuit') and self.suitHasCondition(suitId, 'soakedcalculator'):
                            attack = self.__getLureRemoval(suitId)
                            if attack[SUIT_ATK_COL]:
                                self.battle.suitAttacks.append(attack)
                        if self.battle.activeSuits[i].currHP > 0 and self.suitHasCondition(suitId, 'soakedcalculator'):
                            attack = self.__getCheatAttack(suitId, {'suitName': 'clubpres',
                                                                    'name': 'PresidentLiability2',
                                                                    'animName': 'sanction',
                                                                    'hp': 0,
                                                                    'acc': 100,
                                                                    'freq': 0,
                                                                    'group': SuitBattleGlobals.ATK_TGT_GROUP})
                            if attack[SUIT_ATK_COL]:
                                self.battle.suitAttacks.append(attack)

                if self.battle.findSuit(suitId).dna.name == 'erclaim': # Check if the Cog that just attacked is capable of cheating (e.g. if self.battle.findSuit(suitId).dna.name == 'erclaim').
                    pass # Professor Control: I don't believe there's a Laff Steal cheat, and if there is, I do not know how I would get it to function correctly.  I already have issues trying to get a cheat in my source to work when the Cog misses an attack.
                elif False: # Keep checking for other corresponding Cog names; False is a placeholder.
                    pass

        for i in xrange(len(self.battle.activeSuits)): # Desperation for Litigation Managers
            suitId = self.battle.activeSuits[i].doId
            x = self.TurnsElapsed
            if self.battle.activeSuits[i].currHP <= 0 and self.battle.activeSuits[i].dna.name in SuitBattleGlobals.LitigationManagers and not self.suitHasCondition(suitId, 'alreadyDesperation2'):
                attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                 'name': 'Desperation', # Desperation Activation
                 'animName': 'nothing',
                 'hp': 0,
                 'acc': 100,
                 'freq': 0,
                 'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            for i in xrange(len(self.battle.activeSuits)):  # Desperation for Litigation Managers
                suitId = self.battle.activeSuits[i].doId
                if self.suitHasCondition(suitId, 'desperationcalculator') and self.battle.activeSuits[i].dna.name in SuitBattleGlobals.LitigationManagers and not self.battle.activeSuits[i].currHP <= 0:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'Desperation2',  # Desperation Activation
                                                            'animName': 'nothing',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)

        # Extra Attacks
        for i in xrange(len(self.battle.activeSuits)):
            suit = self.battle.activeSuits[i]
            suitId = suit.doId
            x = self.TurnsElapsed
            if self.battle.activeSuits[i].dna.name == 'wsi': #witness stand-in
                if self.battle.activeSuits[i].getSkeleRevives() == 0 and self.__suitCanAttack(suitId):
                    attack = self.__getGenericSuitAttack(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'redd': #redd
                if self.battle.activeSuits[i].getSkeleRevives() == 0 and self.__suitCanAttack(suitId):
                    attack = self.__getGenericSuitAttack(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            
            for condition in self.getAllRelevantConditions(suitId, StatusEffects.ExtraAttacks, toon=False):
                extraSuitId = suitId
                extraSuit = self.battle.findSuit(extraSuitId)

                extraAttackConditions = self.getAllRelevantConditions(
                    extraSuitId,
                    StatusEffects.ExtraAttacks,
                    toon=False
                )
                for extraIndex in xrange(condition.extraAttacks):
                    if not extraSuit:
                        continue
                    attack = self.__getGenericSuitAttack(extraSuitId)
                    attack[SUIT_ID_COL] = extraSuitId
                    if self.battle.findSuit(extraSuitId).dna.name == 'dopr' and self.__suitCanAttack(extraSuitId):
                        attack = self.__getCheatAttack(extraSuitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                'name': 'GlowerPower',  # Syphon Movie
                                                                'animName': 'glower',
                                                                'hp': 23,
                                                                'acc': 70,
                                                                'freq': 0,
                                                                'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    elif self.battle.findSuit(extraSuitId).dna.name == 'supervis' and self.__suitCanAttack(extraSuitId):
                        attack = self.__getCheatAttack(extraSuitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                'name': 'GlowerPower',  # Syphon Movie
                                                                'animName': 'glower',
                                                                'hp': 23,
                                                                'acc': 70,
                                                                'freq': 0,
                                                                'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    elif self.battle.findSuit(extraSuitId).dna.name == 'dking' and self.__suitCanAttack(extraSuitId):
                        attack = self.__getCheatAttack(extraSuitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                'name': 'PeckingOrder',  # Syphon Movie
                                                                'animName': 'throw-object',
                                                                'hp': 25,
                                                                'acc': 80,
                                                                'freq': 0,
                                                                'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    elif self.__suitCanAttack(extraSuitId) and self.battle.findSuit(extraSuitId).dna.name == 'dopa':
                        attack = self.__getCheatAttack(extraSuitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                'name': 'GlowerPower',  # Syphon Movie
                                                                'animName': 'glower',
                                                                'hp': 26,
                                                                'acc': 70,
                                                                'freq': 0,
                                                                'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    else:
                        if(self.__suitCanAttack(extraSuitId) and
                        self.battle.findSuit(extraSuitId).dna.name not in ('dopr', 'supervis', 'dopa', 'dking') and
                        not self.suitHasCondition(extraSuitId, 'sued')):

                            attack = self.__getGenericSuitAttack(extraSuitId)
                            self.battle.suitAttacks.append(attack)
                    # Syphon if necessary.
                    if self.suitHasCondition(extraSuitId, 'syphon') and not self.battle.activeSuits[i].dna.name in SuitBattleGlobals.SpecialCogDict and self.syphonHP.get(extraSuitId, 0) > 0:
                        attack = self.__getCheatAttack(extraSuitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                'name': 'SyphonMovie',  # Syphon Movie
                                                                'animName': 'nothing',
                                                                'hp': 0,
                                                                'acc': 100,
                                                                'freq': 0,  # Professor Control: I do not know how relevant attack frequency is, but keep it anyway.
                                                                'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)

                    for i in xrange(len(self.battle.activeSuits)):  # Now, how about the other Cogs, including the one that just attacked?
                        suitId = self.battle.activeSuits[i].doId
                        if self.battle.activeSuits[i].dna.name == 'radiog':  # Sniper Factory Foreman
                            attack = self.__getCheatAttack(suitId, {'suitName': 'radiog',
                                                                        'name': 'RadiographerHotTakeDamage',
                                                                        'animName': 'nothing',
                                                                        'hp': 0,
                                                                        'acc': 100,
                                                                        'freq': 0,
                                                                        'group': SuitBattleGlobals.ATK_TGT_GROUP})
                            if attack[SUIT_ATK_COL]:
                                self.battle.suitAttacks.append(attack)
                        if self.battle.findSuit(suitId).dna.name == 'foreman' and self.battle.activeSuits[i].getActualLevel() == 25:  # Sniper Factory Foreman
                            if self.battle.activeSuits[i].currHP > 0 and not self.suitHasCondition(suitId, 'sounded') and self.suitHasCondition(suitId, 'unlureSuit'):
                                attack = self.__getLureRemoval(suitId)
                                if attack[SUIT_ATK_COL]:
                                    self.battle.suitAttacks.append(attack)
                            if self.battle.activeSuits[i].currHP > 0:
                                attack = self.__getCheatAttack(suitId, {'suitName': 'foreman',
                                                                        'name': 'ForemanSnipe',
                                                                        'animName': 'glower',
                                                                        'hp': 0,
                                                                        'acc': 100,
                                                                        'freq': 0,
                                                                        'group': SuitBattleGlobals.ATK_TGT_GROUP})
                                if attack[SUIT_ATK_COL]:
                                    self.battle.suitAttacks.append(attack)
                        if self.battle.findSuit(suitId).dna.name == 'cdirector' and self.suitHasCondition(suitId, 'alreadySecondAttack'):  # Sniper Factory Foreman
                            if self.battle.activeSuits[i].currHP > 0 and not self.suitHasCondition(suitId, 'sounded') and self.suitHasCondition(suitId, 'unlureSuit') and self.suitHasCondition(suitId, 'soakedcalculator'):
                                attack = self.__getLureRemoval(suitId)
                                if attack[SUIT_ATK_COL]:
                                    self.battle.suitAttacks.append(attack)
                            if self.battle.activeSuits[i].currHP > 0 and self.suitHasCondition(suitId, 'soakedcalculator'):
                                attack = self.__getCheatAttack(suitId, {'suitName': 'cdirector',
                                                                        'name': 'ContingencyRiskThresholdBreach25',
                                                                        'animName': 'glower',
                                                                        'hp': 0,
                                                                        'acc': 100,
                                                                        'freq': 0,
                                                                        'group': SuitBattleGlobals.ATK_TGT_GROUP})
                                if attack[SUIT_ATK_COL]:
                                    self.battle.suitAttacks.append(attack)
                        if self.battle.findSuit(suitId).dna.name == 'bkeeper' and self.suitHasCondition(suitId, 'soakedcalculator'):  # Sniper Factory Foreman
                            if self.battle.activeSuits[i].currHP > 0 and not self.suitHasCondition(suitId, 'sounded') and self.suitHasCondition(suitId, 'unlureSuit') and self.suitHasCondition(suitId, 'soakedcalculator'):
                                attack = self.__getLureRemoval(suitId)
                                if attack[SUIT_ATK_COL]:
                                    self.battle.suitAttacks.append(attack)
                            if self.battle.activeSuits[i].currHP > 0 and self.suitHasCondition(suitId, 'soakedcalculator'):
                                attack = self.__getCheatAttack(suitId, {'suitName': 'bkeeper',
                                                                        'name': 'BookkeeperPaperCutSoaked',
                                                                        'animName': 'sanction',
                                                                        'hp': 0,
                                                                        'acc': 100,
                                                                        'freq': 0,
                                                                        'group': SuitBattleGlobals.ATK_TGT_GROUP})
                                if attack[SUIT_ATK_COL]:
                                    self.battle.suitAttacks.append(attack)
                        if self.battle.findSuit(suitId).dna.name == 'clubpres' and self.suitHasCondition(suitId, 'soakedcalculator') and self.battle.activeSuits[i].getActualLevel() == 27:  # Sniper Factory Foreman
                            if self.battle.activeSuits[i].currHP > 0 and not self.suitHasCondition(suitId, 'sounded') and self.suitHasCondition(suitId, 'unlureSuit') and self.suitHasCondition(suitId, 'soakedcalculator'):
                                attack = self.__getLureRemoval(suitId)
                                if attack[SUIT_ATK_COL]:
                                    self.battle.suitAttacks.append(attack)
                            if self.battle.activeSuits[i].currHP > 0 and self.suitHasCondition(suitId, 'soakedcalculator'):
                                attack = self.__getCheatAttack(suitId, {'suitName': 'clubpres',
                                                                        'name': 'PresidentLiability2',
                                                                        'animName': 'sanction',
                                                                        'hp': 0,
                                                                        'acc': 100,
                                                                        'freq': 0,
                                                                        'group': SuitBattleGlobals.ATK_TGT_GROUP})
                                if attack[SUIT_ATK_COL]:
                                    self.battle.suitAttacks.append(attack)

    def calculatePreToonSuitAttacks(self):
        x = self.TurnsElapsed
        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.suitHasCondition(suitId, 'zapped') and not self.suitHasCondition(suitId, 'alreadyZapped') and self.getSuitConditionTurns(suitId, 'zapped') == 1 and self.battle.activeSuits[i].currHP > 0:
                attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                        'name': 'ZapMovie',  # Zap Damage
                                        'animName': 'nothing',
                                        'hp': 0,
                                        'acc': 100,
                                        'freq': 0,
                                        'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.suitHasCondition(suitId, 'sued') and self.battle.activeSuits[i].currHP > 0:
                attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                 'name': 'SueDamage', # Sue Damage
                 'animName': 'nothing',
                 'hp': 0,
                 'acc': 100,
                 'freq': 0,
                 'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)

        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            # if self.battle.activeSuits[i].dna.name in ['cdirector', 'dking', 'rkeeper', 'liquid']:
            #     if not self.suitHasCondition(suitId, 'boardbotLit') and self.__suitCanAttack(suitId):
            #         attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
            #             'name': 'ContingencyMarkRevisedFiling',
            #             'animName': 'nothing',
            #             'hp': 0,
            #             'acc': 100,
            #             'freq': 0,
            #             'group': SuitBattleGlobals.ATK_TGT_GROUP})
            #         if attack[SUIT_ATK_COL]:
                        # self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'redd':  # redd heir wing
                if (x + 2) % 5 == 0 and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'ReddAutoRepair', # Auto Repair
                     'animName': 'effort',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'erclaim':
                if not self.suitHasCondition(suitId, 'sounded') and self.suitHasCondition(suitId, 'unlureSuit') and (x + 2) % 3 == 0 and self.battle.activeSuits[
                    i].currHP > 0:
                    attack = self.__getLureRemovalPreToon(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if (x + 2) % 3 == 0 and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'ErclaimHemmorage', # Auto Repair
                     'animName': 'throw-object',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'clerk' and self.battle.activeSuits[i].getActualLevel() == 20:  # Head Attorney
                if self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                'name': 'PresidentTargetCheck',  # Target Check
                                                                'animName': 'nothing',
                                                                'hp': 0,
                                                                'acc': 100,
                                                                'freq': 0,
                                                                'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if not self.suitHasCondition(suitId, 'sounded') and self.suitHasCondition(suitId, 'unlureSuit') and not self.suitHasCondition(suitId, 'attorneyRemand') and (self.suitHasCondition(suitId, 'targetCheckCondition') and self.getSuitConditionModifier(suitId, 'targetCheckCondition') > -1):
                    attack = self.__getLureRemovalPreToon(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.battle.activeSuits[i].currHP > 0 and (self.suitHasCondition(suitId, 'targetCheckCondition') and self.getSuitConditionModifier(suitId, 'targetCheckCondition') > -1) and not self.suitHasCondition(suitId, 'attorneyRemand'):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                'name': 'AttorneyRemand',
                                                                'animName': 'nothing',
                                                                'hp': 0,
                                                                'acc': 100,
                                                                'freq': 0,
                                                                'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'supervis':
                if self.battle.activeSuits[i].getActualLevel() == 26:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': random.choice(('MintLureResistance', 'MintLureResistance2')), 
                                            'animName': 'rake-react',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_GROUP})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'hrollers':
                if self.battle.activeSuits[i].getActualLevel() == 25 and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': random.choice(('HighRollerLureResistance', 'HighRollerLureResistance2')), 
                                            'animName': 'rake-react',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_GROUP})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)

        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.suitHasCondition(suitId, 'silhouetteUnlure') and self.suitHasCondition(suitId, 'unlureSuit') and self.battle.activeSuits[i].currHP > 0:
                attack = self.__getLureRemovalPreToon(suitId)
                if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'hrollers':
                if self.battle.activeSuits[i].getActualLevel() == 28 and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'HighRollerSingingBlues',  # Blue Silhouette
                                            'animName': 'nothing',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_GROUP})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'cdirector':
                if self.suitHasCondition(suitId, 'markedcalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[
                    i].currHP > 0:
                    attack = self.__getAbilityQueuedPreToon(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'markedcalculator') and self.__suitCanAttack(suitId):
                   attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                    'name': 'ContingencyRiskThresholdBreach50',
                     'animName': 'throw-object',
                    'hp': 0,
                    'acc': 100,
                    'freq': 0,
                    'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                   if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'selfRepairCalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[
                    i].currHP > 0:
                    attack = self.__getAbilityQueuedPreToon(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'selfRepairCalculator') and self.__suitCanAttack(suitId):
                   attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                    'name': 'ContingencySelfRepair',
                     'animName': 'nothing',
                    'hp': 0,
                    'acc': 100,
                    'freq': 0,
                    'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                   if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'caseman':
                if self.suitHasCondition(suitId, 'paperfilingcalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueuedPreToon(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'paperfilingcalculator') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'ArbitratorPaperFiling',  # Paperweight
                                                            'animName': 'throw-object',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'rkeeper':
                if self.suitHasCondition(suitId, 'redlinedcalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[
                    i].currHP > 0:
                    attack = self.__getAbilityQueuedPreToon(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'redlinedcalculator') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'RecordkeeperRedlinedClause',
                                                            'animName': 'sanction',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'ambass':
                roll = random.randint(0, 100)
                if roll >= 75 and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'PowerhouseAbsorb',  # Desperation Syphon For All Cogs
                                                            'animName': 'defense',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            # if self.battle.activeSuits[i].dna.name == 'safesupervis':
                # if self.suitHasCondition(suitId, 'promotioncalculator') and self.__suitCanAttack(suitId):
                #     attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                #      'name': 'TargetCheck', # Target Check for Promotion
                #      'animName': 'nothing',
                #      'hp': 0,
                #      'acc': 100,
                #      'freq': 0,
                #      'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                #     if attack[SUIT_ATK_COL]:
                #         self.battle.suitAttacks.append(attack)
                # if self.suitHasCondition(suitId, 'promotioncalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                #     attack = self.__getAbilityQueuedPreToon(suitId)
                #     if attack[SUIT_ATK_COL]:
                #         self.battle.suitAttacks.append(attack)
                # if self.suitHasCondition(suitId, 'promotioncalculator') and not (self.suitHasCondition(suitId, 'targetCheckCondition') and self.getSuitConditionModifier(suitId, 'targetCheckCondition') > -1) and self.battle.activeSuits[i].currHP > 0 and self.__suitCanAttack(suitId):
                #     attack = self.__getAbilityQueuedPreToon(suitId)
                #     if attack[SUIT_ATK_COL]:
                #         self.battle.suitAttacks.append(attack)
                # if self.suitHasCondition(suitId, 'promotioncalculator') and (self.suitHasCondition(suitId, 'targetCheckCondition') and self.getSuitConditionModifier(suitId, 'targetCheckCondition') > -1) and self.__suitCanAttack(suitId):
                #     attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                #      'name': 'SafetyPromotion', # Promotion
                #      'animName': 'magic3',
                #      'hp': 0,
                #      'acc': 100,
                #      'freq': 0,
                #      'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                #     if attack[SUIT_ATK_COL]:
                #         self.battle.suitAttacks.append(attack)
                # if self.suitHasCondition(suitId, 'target3'):
                #     attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                #                                             'name': 'SafetyPromotion2',  # Promotion
                #                                             'animName': 'magic3',
                #                                             'hp': 0,
                #                                             'acc': 100,
                #                                             'freq': 0,
                #                                             'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                #     if attack[SUIT_ATK_COL]:
                #         self.battle.suitAttacks.append(attack)
                # if self.suitHasCondition(suitId, 'target4'):
                #     attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                #                                             'name': 'SafetyPromotion3',  # Promotion
                #                                             'animName': 'magic3',
                #                                             'hp': 0,
                #                                             'acc': 100,
                #                                             'freq': 0,
                #                                             'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                #     if attack[SUIT_ATK_COL]:
                #         self.battle.suitAttacks.append(attack)
                # if self.suitHasCondition(suitId, 'target5'):
                #     attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                #                                             'name': 'SafetyPromotion4',  # Promotion
                #                                             'animName': 'magic3',
                #                                             'hp': 0,
                #                                             'acc': 100,
                #                                             'freq': 0,
                #                                             'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                #     if attack[SUIT_ATK_COL]:
                #         self.battle.suitAttacks.append(attack)
                # if self.suitHasCondition(suitId, 'target6'):
                #     attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                #                                             'name': 'SafetyPromotion5',  # Promotion
                #                                             'animName': 'magic3',
                #                                             'hp': 0,
                #                                             'acc': 100,
                #                                             'freq': 0,
                #                                             'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                #     if attack[SUIT_ATK_COL]:
                #         self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'safesupervis':
                if self.suitHasCondition(suitId, 'heatwavecalculationcalculator') and not (self.battle.activeSuits[i].currHP < self.battle.activeSuits[i].maxHP) and \
                        self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueuedPreToon(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'heatwavecalculationcalculator') and self.battle.activeSuits[i].currHP > 0 and (self.battle.activeSuits[i].currHP < self.battle.activeSuits[i].maxHP):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'SafetyHeatWaveCalculation', # Calculating Heat Wave
                     'animName': 'soak',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'radiog':
                if self.suitHasCondition(suitId, 'hottakecalculator') and not self.__suitCanAttack(suitId) and \
                        self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueuedPreToon(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'hottakecalculator') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'RadiographerHotTake', # Hot Take
                     'animName': 'throw-object',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'hottakecalculator2') and not self.__suitCanAttack(suitId) and \
                        self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueuedPreToon(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'hottakecalculator2') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                        'name': 'RadiographerHotTake', # Hot Take
                        'animName': 'throw-object',
                        'hp': 0,
                        'acc': 100,
                        'freq': 0,
                        'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                    self.setSuitCondition(suitId, 'hottakecalculator2', 0, 0, 'setBoth')
            if self.battle.activeSuits[i].dna.name == 'clubpres' and self.battle.activeSuits[i].getActualLevel() == 27:  # bookkeeper
                if self.TurnsElapsed % 2 == 0 and self.suitHasCondition(suitId, 'unlureSuit') and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getLureRemovalPreToon(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.TurnsElapsed % 2 == 0 and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'PresidentLiability', # Paper Cut
                     'animName': 'sanction',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                # if (self.TurnsElapsed + 1) % 2 == 0 and self.suitHasCondition(suitId, 'unlureSuit') and self.battle.activeSuits[i].currHP > 0:
                #     attack = self.__getLureRemovalPreToon(suitId)
                #     if attack[SUIT_ATK_COL]:
                #         self.battle.suitAttacks.append(attack)
                # if (self.TurnsElapsed + 1) % 2 == 0 and self.__suitCanAttack(suitId):
                #     attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                #      'name': 'BookkeeperMandatoryFiling', # Paper Rain
                #      'animName': 'glower',
                #      'hp': 0,
                #      'acc': 100,
                #      'freq': 0,
                #      'group': SuitBattleGlobals.ATK_TGT_DOUBLE})
                #     if attack[SUIT_ATK_COL]:
                #         self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'bkeeper':  # bookkeeper
                if self.suitHasCondition(suitId, 'papercutcalculator') and not self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                    attack = self.__getAbilityQueuedPreToon(suitId)
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'papercutcalculator') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'BookkeeperPaperCut', # Paper Cut
                     'animName': 'sanction',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'bkeeper':
                if self.suitHasCondition(suitId, 'papercutcalculator3') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'AmbassadorAdvancement3', # Paper Cut
                     'animName': 'sanction',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if not self.suitHasCondition(suitId, 'dotfinished'):  # powerhouse
                self.__appendToonConditionDamageAndRetaliation(
                    condition='zapped',
                    damage=25,
                    damageMovie='PowerhouseBurnDamage',
                    retaliateAtTurns=[1],
                    retaliations=[
                        {
                            'suitNames': ['bkeeper'],
                            'movie': 'AmbassadorAdvancement3',
                            'animName': 'sanction',
                            'hp': 25,
                            'queueCondition': 'papercutcalculator3',
                        }
                    ]
                )
                # if self.TurnsElapsed % 1 == 0 and self.battle.activeSuits[i].currHP > 0 and not self.suitHasCondition(suitId, 'dotfinished'):
                #     attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                #                                             'name': 'PowerhouseBurnDamage',  # Slow Burn
                #                                             'animName': 'nothing',
                #                                             'hp': 0,
                #                                             'acc': 100,
                #                                             'freq': 0,
                #                                             'group': SuitBattleGlobals.ATK_TGT_GROUP})
                #     if attack[SUIT_ATK_COL]:
                        # self.battle.suitAttacks.append(attack)
            # if self.battle.activeSuits[i].dna.name == 'rkeeper':
            #     if self.suitHasCondition(suitId, 'costscalculator') and self.battle.activeSuits[i].currHP > 0:
            #         attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
            #          'name': 'RecordkeeperRedlinedClauseMissedPayment', # Paper Rain
            #          'animName': 'calculating-costs',
            #          'hp': 0,
            #          'acc': 100,
            #          'freq': 0,
            #          'group': SuitBattleGlobals.ATK_TGT_SINGLE})
            #         if attack[SUIT_ATK_COL]:
            #             self.battle.suitAttacks.append(attack)

        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            # if self.suitHasCondition(suitId, 'deadpower') and not self.suitHasCondition(suitId, 'dotfinished') and self.battle.activeSuits[i].dna.name in SuitBattleGlobals.SpecialCogDict and not \
            # self.battle.activeSuits[i].dna.name == 'phouse':
            #     attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
            #                                             'name': 'PowerhouseBurnDamage',  # Slow Burn for Managers when Powerhouse is dead
            #                                             'animName': 'nothing',
            #                                             'hp': 0,
            #                                             'acc': 100,
            #                                             'freq': 0,
            #                                             'group': SuitBattleGlobals.ATK_TGT_GROUP})
            #     if attack[SUIT_ATK_COL]:
                        # self.battle.suitAttacks.append(attack)

        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'cdirector' and self.suitHasCondition(suitId, 'alreadyContent'):  # High Stakes President
                attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'HighStakesHeal',
                                                            'animName': 'nothing',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_GROUP})
                if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'clubpres' and self.battle.activeSuits[i].getActualLevel() == 20:  # High Stakes President
                attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'HighStakesHeal',
                                                            'animName': 'nothing',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_GROUP})
                if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'hrollers' and self.battle.activeSuits[i].getActualLevel() == 31 and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'HighStakesHeal',  # Light Blue Silhouette
                                            'animName': 'nothing',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_GROUP})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)

        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.suitHasCondition(suitId, 'deepfreeze') and not self.suitHasCondition(suitId, 'sounded') and self.suitHasCondition(suitId, 'unlureSuit') and self.__suitCanAttack(suitId) and self.battle.activeSuits[i].currHP > 0:
                attack = self.__getLureRemovalPreToon(suitId)
                if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.suitHasCondition(suitId, 'deepfreeze') and self.__suitCanAttack(suitId) and not self.battle.activeSuits[i].dna.name == 'hrollers' and not self.battle.activeSuits[i].dna.name == 'phouse' and not self.battle.activeSuits[i].dna.name == 'safesupervis':
                attack = self.__getGenericSuitAttack(suitId)
                if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.suitHasCondition(suitId, 'syphon') and self.syphonHP.get(suitId, 0) > 0 and not self.suitHasCondition(suitId, 'dead') and not self.battle.activeSuits[i].dna.name == 'phouse' and not self.battle.activeSuits[i].dna.name == 'safesupervis':
                attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                    'name': 'SyphonMovie', # Syphon Movie
                    'animName': 'nothing',
                    'hp': 0,
                    'acc': 100,
                    'freq': 0, # Professor Control: I do not know how relevant attack frequency is, but keep it anyway.
                    'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'supervis' and self.battle.activeSuits[i].getActualLevel() == 25 and self.damageHP.get(suitId, 0) > 0:
                if self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'DamageMovie',  # Fraudulent Mint Supervisor
                                                            'animName': 'pie-small-react',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)

    def calculateEndOfRoundAttacks(self):
        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.suitHasCondition(suitId, 'bellowattack') and self.suitHasCondition(suitId, 'unlureSuit') and not self.suitHasCondition(suitId, 'sounded') and self.battle.activeSuits[i].currHP > 0:
                attack = self.__getLureRemoval(suitId)
                if attack[SUIT_ATK_COL]:
                    self.battle.suitAttacks.append(attack)
            if self.suitHasCondition(suitId, 'bellowattack') and self.battle.activeSuits[i].currHP > 0 and not self.suitHasCondition(suitId, 'sued') and not self.suitHasCondition(suitId, 'deepfreeze'):
                attack = self.__getGenericSuitAttack(suitId) # Extra Attack for Lured Cogs affected by Bayou Bellow
                if attack[SUIT_ATK_COL]:
                    self.battle.suitAttacks.append(attack)
            if self.suitHasCondition(suitId, 'guestVerse') and self.battle.activeSuits[i].currHP > 0 and not self.suitHasCondition(suitId, 'sued'):
                attack = self.__getGenericSuitAttack(suitId) # Extra Attack for Lured Cogs affected by Bayou Bellow
                if attack[SUIT_ATK_COL]:
                    self.battle.suitAttacks.append(attack)
            for i in xrange(len(self.battle.activeSuits)):  # Now, how about the other Cogs, including the one that just attacked?
                suitId = self.battle.activeSuits[i].doId
                if self.suitHasCondition(suitId, 'guestVerse') and self.suitHasCondition(suitId, 'guestVerseComplete') and self.battle.activeSuits[i].currHP > 0: 
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                'name': 'PresidentViralSensation',
                                                                'animName': 'nothing',
                                                                'hp': 0,
                                                                'acc': 100,
                                                                'freq': 0,
                                                                'group': SuitBattleGlobals.ATK_TGT_GROUP})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            for i in xrange(len(self.battle.activeSuits)):  # Now, how about the other Cogs, including the one that just attacked?
                suitId = self.battle.activeSuits[i].doId
                if self.battle.activeSuits[i].dna.name == 'radiog':  # Sniper Factory Foreman
                    attack = self.__getCheatAttack(suitId, {'suitName': 'radiog',
                                                                'name': 'RadiographerHotTakeDamage',
                                                                'animName': 'nothing',
                                                                'hp': 0,
                                                                'acc': 100,
                                                                'freq': 0,
                                                                'group': SuitBattleGlobals.ATK_TGT_GROUP})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.battle.findSuit(suitId).dna.name == 'foreman' and self.battle.activeSuits[i].getActualLevel() == 25:  # Sniper Factory Foreman
                    if self.battle.activeSuits[i].currHP > 0 and not self.suitHasCondition(suitId, 'sounded') and self.suitHasCondition(suitId, 'unlureSuit') and self.suitHasCondition(suitId, 'contingencyHit'):
                        attack = self.__getLureRemoval(suitId)
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    if self.battle.activeSuits[i].currHP > 0 and self.suitHasCondition(suitId, 'contingencyHit'):
                        attack = self.__getCheatAttack(suitId, {'suitName': 'foreman',
                                                                'name': 'ForemanSnipe',
                                                                'animName': 'glower',
                                                                'hp': 0,
                                                                'acc': 100,
                                                                'freq': 0,
                                                                'group': SuitBattleGlobals.ATK_TGT_GROUP})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                if self.battle.findSuit(suitId).dna.name == 'cdirector' and self.suitHasCondition(suitId, 'alreadySecondAttack'):  # Sniper Factory Foreman
                    if self.battle.activeSuits[i].currHP > 0 and not self.suitHasCondition(suitId, 'sounded') and self.suitHasCondition(suitId, 'unlureSuit') and self.suitHasCondition(suitId, 'soakedcalculator'):
                        attack = self.__getLureRemoval(suitId)
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    if self.battle.activeSuits[i].currHP > 0 and self.suitHasCondition(suitId, 'soakedcalculator'):
                        attack = self.__getCheatAttack(suitId, {'suitName': 'cdirector',
                                                                'name': 'ContingencyRiskThresholdBreach25',
                                                                'animName': 'glower',
                                                                'hp': 0,
                                                                'acc': 100,
                                                                'freq': 0,
                                                                'group': SuitBattleGlobals.ATK_TGT_GROUP})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                if self.battle.findSuit(suitId).dna.name == 'clubpres' and self.suitHasCondition(suitId, 'soakedcalculator') and self.battle.activeSuits[i].getActualLevel() == 27:  # Sniper Factory Foreman
                    if self.battle.activeSuits[i].currHP > 0 and not self.suitHasCondition(suitId, 'sounded') and self.suitHasCondition(suitId, 'unlureSuit') and self.suitHasCondition(suitId, 'soakedcalculator'):
                        attack = self.__getLureRemoval(suitId)
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    if self.battle.activeSuits[i].currHP > 0 and self.suitHasCondition(suitId, 'soakedcalculator'):
                        attack = self.__getCheatAttack(suitId, {'suitName': 'clubpres',
                                                                'name': 'PresidentLiability2',
                                                                'animName': 'sanction',
                                                                'hp': 0,
                                                                'acc': 100,
                                                                'freq': 0,
                                                                'group': SuitBattleGlobals.ATK_TGT_GROUP})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                if self.battle.findSuit(suitId).dna.name == 'bkeeper' and self.suitHasCondition(suitId, 'soakedcalculator'):  # Sniper Factory Foreman
                    if self.battle.activeSuits[i].currHP > 0 and not self.suitHasCondition(suitId, 'sounded') and self.suitHasCondition(suitId, 'unlureSuit') and self.suitHasCondition(suitId, 'soakedcalculator'):
                        attack = self.__getLureRemoval(suitId)
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    if self.battle.activeSuits[i].currHP > 0 and self.suitHasCondition(suitId, 'soakedcalculator'):
                        attack = self.__getCheatAttack(suitId, {'suitName': 'bkeeper',
                                                                'name': 'BookkeeperPaperCutSoaked',
                                                                'animName': 'sanction',
                                                                'hp': 0,
                                                                'acc': 100,
                                                                'freq': 0,
                                                                'group': SuitBattleGlobals.ATK_TGT_GROUP})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)

        # for i in xrange(len(self.battle.activeSuits)):
        #     suitId = self.battle.activeSuits[i].doId
        #     if not self.suitHasCondition(suitId, 'suemovie') and self.suitHasCondition(suitId, 'sued') and self.battle.activeSuits[i].currHP > 0:
        #         attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
        #                                 'name': 'SueApplication', # Sue Application movie since the actual movie doesnt exist
        #                                 'animName': 'nothing',
        #                                 'hp': 0,
        #                                 'acc': 100,
        #                                 'freq': 0,
        #                                 'group': SuitBattleGlobals.ATK_TGT_SINGLE})
        #         if attack[SUIT_ATK_COL]:
                        # self.battle.suitAttacks.append(attack)

        # for i in xrange(len(self.battle.activeSuits)):
        #     suitId = self.battle.activeSuits[i].doId
        #     if self.battle.activeSuits[i].dna.name == 'foreman': 
        #         if self.battle.activeSuits[i].currHP > 0:
        #             attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
        #                                                     'name': 'UnstableTransformation',
        #                                                     'animName': 'nothing',
        #                                                     'hp': 0,
        #                                                     'acc': 100,
        #                                                     'freq': 0,
        #                                                     'group': random.choice((SuitBattleGlobals.ATK_TGT_FOREMAN,
        #                                                     SuitBattleGlobals.ATK_TGT_SUPERVISOR,
        #                                                     SuitBattleGlobals.ATK_TGT_ATTORNEY,
        #                                                     SuitBattleGlobals.ATK_TGT_PRESIDENT,
        #                                                     SuitBattleGlobals.ATK_TGT_CONFUSED))})
        #             if attack[SUIT_ATK_COL]:
                        # self.battle.suitAttacks.append(attack)

        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.suitHasCondition(suitId, 'zapped') and self.suitHasCondition(suitId, 'drenched') and not self.getSuitConditionTurns(suitId, 'drenched') == 1 and self.battle.activeSuits[i].currHP > 0:
                attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                 'name': 'DrenchDecrement', # Soak Removal
                 'animName': 'nothing',
                 'hp': 0,
                 'acc': 100,
                 'freq': 0,
                 'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                if attack[SUIT_ATK_COL]:
                    self.battle.suitAttacks.append(attack)
            if self.suitHasCondition(suitId, 'drenched') and self.getSuitConditionTurns(suitId, 'drenched') == 1 and self.battle.activeSuits[i].currHP > 0:
                attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                 'name': 'SoakRemoval', # Soak Removal
                 'animName': 'nothing',
                 'hp': 0,
                 'acc': 100,
                 'freq': 0,
                 'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                if attack[SUIT_ATK_COL]:
                    self.battle.suitAttacks.append(attack)
            if self.suitHasCondition(suitId, 'soaked') and self.getSuitConditionTurns(suitId, 'soaked') == 1 and self.battle.activeSuits[i].currHP > 0:
                attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                 'name': 'SoakRemoval', # Soak Removal
                 'animName': 'nothing',
                 'hp': 0,
                 'acc': 100,
                 'freq': 0,
                 'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                if attack[SUIT_ATK_COL]:
                    self.battle.suitAttacks.append(attack)

        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.suitHasCondition(suitId, 'oilRain') and not self.suitHasCondition(suitId, 'alreadyOil') and self.getSuitConditionTurns(suitId, 'oilRain') == 1 and self.battle.activeSuits[i].currHP > 0:
                attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                 'name': 'OilRemoval', # Soak Removal
                 'animName': 'nothing',
                 'hp': 0,
                 'acc': 100,
                 'freq': 0,
                 'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            
        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.suitHasCondition(suitId, 'marked') and self.getSuitConditionTurns(suitId, 'marked') == 1 and not self.battle.activeSuits[i].dna.name == 'bcaster' and not self.battle.activeSuits[i].dna.name == 'mplayers' and not self.battle.activeSuits[i].dna.name == 'hrollers' and self.battle.activeSuits[i].currHP > 0:
                attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                 'name': 'MarkRemoval', # Mark Removal
                 'animName': 'nothing',
                 'hp': 0,
                 'acc': 100,
                 'freq': 0,
                 'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)

        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.suitHasCondition(suitId, 'sued') and self.getSuitConditionTurns(suitId, 'sued') == 1 and self.battle.activeSuits[i].currHP > 0:
                attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                 'name': 'SueRemoval', # Sue Removal
                 'animName': 'nothing',
                 'hp': 0,
                 'acc': 100,
                 'freq': 0,
                 'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)


