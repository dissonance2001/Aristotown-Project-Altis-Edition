from toontown.battle.BattleBase import *
from toontown.battle.BattleGlobals import *
from toontown.battle import SuitBattleGlobals
import random
import math

class VideographerCalculatorAI:

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

    def __appendToonConditionDamageAndRetaliation(
            self,
            *args,
            **kwargs):

        return self.calculator.appendToonConditionDamageAndRetaliation(
            *args,
            **kwargs
        )

    
    def calculateSuitAttacksVideographer(self):
        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            # if self.battle.activeSuits[i].dna.name == 'videog':  # videographer
            #     if self.battle.activeSuits[i].currHP <= 0 and not self.__suitCanAttack(suitId):
            #         attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
            #                                 'name': 'VideographerDeath',  # Videographer Death to Sacrifice All Cogs
            #                                 'animName': 'snap',
            #                                 'hp': 0,
            #                                 'acc': 100,
            #                                 'freq': 0,
            #                                 'group': SuitBattleGlobals.ATK_TGT_SINGLE})
            #         if attack[SUIT_ATK_COL]:
            #             self.battle.suitAttacks.append(attack)

        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'director':
                if not self.suitHasCondition(suitId, 'deadproducer') and len(self.battle.activeSuits) == 6 and not self.deadSuits > 0 and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'DirectorBackToOnes',
                                            'animName': 'nothing',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'bcaster':  # broadcaster
                if self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'BroadcasterViralSensation',  # ViralSensation
                                            'animName': 'magic3',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': random.choice((SuitBattleGlobals.ATK_TGT_TRIPLE, SuitBattleGlobals.ATK_TGT_DOUBLE))})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'cinema':  
                if self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                             'name': 'FilmmakerCameraFlash',
                                            'animName': 'glower',
                                            'hp': 30,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)


        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            x = self.TurnsElapsed
            # Initial Cheats
            if self.battle.activeSuits[i].dna.name == 'bcaster':  # broadcaster
                if self.__suitCanAttack(suitId):
                    roll = random.randint(0, 100)
                    if roll >= 85 and self.battle.activeSuits[i].currHP > 0:
                        attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                'name': 'BroadcasterDonation2',  # Donation
                                                'animName': 'nothing',
                                                'hp': 0,
                                                'acc': 100,
                                                'freq': 0,
                                                'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    else:
                        attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                'name': 'BroadcasterDonation',  # Donation
                                                                'animName': 'nothing',
                                                                'hp': 0,
                                                                'acc': 100,
                                                                'freq': 0,
                                                                'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                if self.battle.activeSuits[i].currHP <= 0 and not self.suitHasCondition(suitId, 'killedbyvideo') and not self.__suitCanAttack(
                    suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'VideographerVideoStatic',  # Video Static Upon Death
                                            'animName': 'nothing',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'mplayers':  # filmmaker
                if self.battle.activeSuits[i].currHP <= 0 and not self.suitHasCondition(suitId, 'killedbyvideo') and not self.__suitCanAttack(
                    suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'VideographerVideoStatic',  # Video Static Upon Death
                                            'animName': 'glower',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'fmaker':  # filmmaker
                if self.battle.activeSuits[i].currHP <= 0 and not self.suitHasCondition(suitId, 'killedbyvideo') and not self.__suitCanAttack(
                    suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'VideographerVideoStatic',  # Video Static Upon Death
                                            'animName': 'glower',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'filmmakercalculator') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                             'name': 'FilmmakerCameraRewind',
                                                           'animName': 'throw-object',
                                            'hp': 30,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                # if self.battle.activeSuits[i].currHP < self.battle.activeSuits[i].maxHP and self.__suitCanAttack(
                #         suitId):
                #     attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                #                             'name': 'FilmmakerBudgetCuts',
                #                             'animName': 'throw-paper',
                #                             'hp': 30,
                #                             'acc': 100,
                #                             'freq': 0,
                #                             'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                #     if attack[SUIT_ATK_COL]:
                #         self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'cinema':  # cinematographer
                if self.battle.activeSuits[i].currHP <= 0 and not self.suitHasCondition(suitId, 'killedbyvideo') and not self.__suitCanAttack(
                    suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'VideographerVideoStatic',  # Video Static Upon Death
                                            'animName': 'glower',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'choreo':  # choreographer
                if self.battle.activeSuits[i].currHP <= 0 and not self.suitHasCondition(suitId, 'killedbyvideo') and not self.__suitCanAttack(
                    suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'VideographerVideoStatic',  # Video Static Upon Death
                                            'animName': 'glower',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                             'name': 'ChoreoChoreography',
                                                           'animName': 'song-and-dance',
                                            'hp': 30,
                                            'acc': 25,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_GROUP})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'director':  # director
                if self.battle.activeSuits[i].currHP <= 0 and not self.suitHasCondition(suitId, 'killedbyvideo') and not self.__suitCanAttack(
                    suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'VideographerVideoStatic',  # Video Static Upon Death
                                            'animName': 'glower',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'extortioncalculator2') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'DirectorActionRetaliation',
                                            'animName': 'glower',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_GROUP})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'directorcalculator') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, random.choice([{'suitName': self.battle.activeSuits[i].dna.name,
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
                                                           'group': SuitBattleGlobals.ATK_TGT_SINGLE}]))
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            for i in xrange(len(self.battle.activeSuits)):
                suitId = self.battle.activeSuits[i].doId
                if self.battle.activeSuits[i].dna.name == 'director': 
                    if self.calculator.deadSuits > 0 and self.battle.activeSuits[i].currHP > 0:
                        attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                'name': 'DirectorBudgetExpansion',
                                                'animName': 'calculator',
                                                'hp': 0,
                                                'acc': 100,
                                                'freq': 0,
                                                'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    if self.__suitCanAttack(suitId):
                        attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                'name': 'DirectorProductionBudget',
                                                'animName': 'magic3',
                                                'hp': 0,
                                                'acc': 100,
                                                'freq': 0,
                                                'group': SuitBattleGlobals.ATK_TGT_GROUP})
                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
    

        # Secondary Cheats
        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'videog':
                if self.suitHasCondition(suitId, 'hollywoodcalculator') and self.suitHasCondition(suitId, 'phase3') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                        'name': 'VideographerRisingStarsSacrifice',
                                                        # Rising Stars Sacrifice
                                                        'animName': 'snap',
                                                        'hp': 0,
                                                        'acc': 100,
                                                        'freq': 0,
                                                        'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'phase3') and self.suitHasCondition(suitId, 'immunecalculator') and not len(
                        self.battle.activeSuits) > 5 and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'VideographerRisingStars2',  # Rising Stars
                                                            'animName': 'song-and-dance',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'phase2') and not len(self.battle.activeSuits) > 1 and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'VideographerElectricShock4',  # Rising Stars
                                                            'animName': 'snap',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if not self.suitHasCondition(suitId, 'phase2') and self.battle.activeSuits[
                                i].currHP <= 18888 and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                        'name': 'VideographerDirectorCuts',  # Director Cuts
                                                        'animName': 'song-and-dance',
                                                        'hp': 0,
                                                        'acc': 100,
                                                        'freq': 0,
                                                        'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'silhouettespawn') and not len(
                                    self.battle.activeSuits) > 7 and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                        'name': 'VideographerRisingStarsSilhouette',
                                                        # Rising Stars Silhouette
                                                        'animName': 'scabbard',
                                                        'hp': 0,
                                                        'acc': 100,
                                                        'freq': 0,
                                                        'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if not self.suitHasCondition(suitId, 'phase3') and not self.suitHasCondition(suitId, 'phase2') and not self.suitHasCondition(suitId, 'immune') and not self.suitHasCondition(suitId, 'silhouettespawn') and not self.suitHasCondition(suitId, 'directorscuts') and not len(
                                self.battle.activeSuits) > 5 and self.__suitCanAttack(suitId) and self.TurnsElapsed % 2 == 0:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                        'name': 'VideographerRisingStars',  # Rising Stars Hollywoods
                                                        'animName': 'song-and-dance',
                                                        'hp': 0,
                                                        'acc': 100,
                                                        'freq': 0,
                                                        'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'electricshockcalculator') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                     'name': 'TargetCheck', # Target Check for Promotion
                     'animName': 'nothing',
                     'hp': 0,
                     'acc': 100,
                     'freq': 0,
                     'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'electricshockcalculator') and (self.suitHasCondition(suitId, 'targetCheckCondition') and self.getSuitConditionModifier(suitId, 'targetCheckCondition') > -1) and self.battle.activeSuits[i].currHP > 0 and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                        'name': 'VideographerStarOfTheShow',  # Electric Shock
                                                        'animName': 'snap',
                                                        'hp': 0,
                                                        'acc': 100,
                                                        'freq': 0,
                                                        'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)


                # End Of Round High Roller Attacks
        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'videog':
                if self.calculator.deadSuits == 1 and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'VideographerAttackRewind',  # Attack Rewind for Dead Suits
                                            'animName': 'snap',
                                            'hp': 25,
                                            'acc': 85,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.calculator.deadSuits == 2 and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'VideographerAttackRewind',  # Attack Rewind for Dead Suits
                                                            'animName': 'snap',
                                                            'hp': 25,
                                                            'acc': 85,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_DOUBLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.calculator.deadSuits == 3 and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'VideographerAttackRewind',  # Attack Rewind for Dead Suits
                                                            'animName': 'snap',
                                                            'hp': 25,
                                                            'acc': 85,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_TRIPLE})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.calculator.deadSuits > 3 and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'VideographerAttackRewind',  # Attack Rewind for Dead Suits
                                                            'animName': 'snap',
                                                            'hp': 25,
                                                            'acc': 85,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_GROUP})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.__suitCanAttack(suitId) and self.suitHasCondition(suitId, 'phase3'):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'VideographerHardCut',  # Attack Rewind for Dead Suits
                                                            'animName': 'magic3',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_GROUP})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
