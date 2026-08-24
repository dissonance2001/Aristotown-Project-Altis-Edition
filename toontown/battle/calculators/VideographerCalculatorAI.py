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

    def __encodeSuitOrder(self, oldSuits, newSuits):
        value = 0
        for newIndex in xrange(len(newSuits)):
            oldIndex = oldSuits.index(newSuits[newIndex])
            value |= oldIndex << (newIndex * 3)
        return value

    
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
                if self.calculator.deadSuits > 0 and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'DirectorBackToOnes',
                                            'animName': 'nothing',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_GROUP,
                        'targetType': 'suit',
                        'allowSelfTarget': True,
                        'targetSelf': False,
                        'damageTarget': 'target',
                        'healTarget': 'target',
                        'requiredManagerNames': ('choreo', 'fmaker', 'director', 'cinema')})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'mplayers':  # broadcaster
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
                if self.TurnsElapsed % 2 == 0 and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                             'name': 'FilmmakerCameraFlash',
                                            'animName': 'glower',
                                            'hp': 0,
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
                        attack = self.__getCheatAttack(suitId, {
                            'suitName': self.battle.activeSuits[i].dna.name,
                            'name': 'BroadcasterDonation2',
                            'animName': 'nothing',
                            'hp': 0,
                            'acc': 100,
                            'freq': 0,
                             'group': SuitBattleGlobals.ATK_TGT_DOUBLE,
                         'targetType': 'suit',
                         'damageTarget': 'target',
                        'healTarget': 'target',
                        'allowSelfTarget': True,
                        'targetSelf': False,
                     'excludeManagers': False,
                        'requiredManagerNames':  ('bcaster', 'videog'),
                        })

                        if attack[SUIT_ATK_COL]:
                            self.battle.suitAttacks.append(attack)
                    else:
                        attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                                'name': 'BroadcasterDonation',  # Donation
                                                                'animName': 'nothing',
                                                                'hp': 0,
                                                                'acc': 100,
                                                                'freq': 0,
                                                                 'group': SuitBattleGlobals.ATK_TGT_DOUBLE,
                         'targetType': 'suit',
                         'damageTarget': 'target',
                        'healTarget': 'target',
                        'allowSelfTarget': True,
                        'targetSelf': False,
                     'excludeManagers': False,
                        'requiredManagerNames':  ('bcaster', 'videog'),})
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
            if self.battle.activeSuits[i].dna.name == 'director':  # filmmaker
                if not self.suitHasCondition(suitId, 'collectcalledCog') and self.suitHasCondition(suitId, 'collectcalled') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'DirectorAction',
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
        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'fmaker':  # filmmaker
                # if self.battle.activeSuits[i].currHP <= 0 and not self.suitHasCondition(suitId, 'killedbyvideo') and not self.__suitCanAttack(
                #     suitId):
                #     attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                #                             'name': 'VideographerVideoStatic',  # Video Static Upon Death
                #                             'animName': 'glower',
                #                             'hp': 0,
                #                             'acc': 100,
                #                             'freq': 0,
                #                             'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                #     if attack[SUIT_ATK_COL]:
                #         self.battle.suitAttacks.append(attack)
                if self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'FilmmakerWrappedInTheFilm',  # Video Static Upon Death
                                            'animName': 'throw-object',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                        'excludeToonConditions': (
                            'dodgy',
                        )})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if (self.TurnsElapsed + 1) % 2 == 0 and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'FilmmakerCameraRewind',
                                                            'animName': 'throw-object',
                                                            'hp': 30,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_GROUP,
                                                            'targetType': 'suit',
                                                            'allowSelfTarget': True,
                                                            'requireDamaged': True,
                                                            'targetSelf': False,
                                                            'excludeManagers': False, 
                                                            'requiredManagerNames': ('choreo', 'fmaker', 'director', 'cinema')})


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
            # if self.battle.activeSuits[i].dna.name == 'cinema':  # cinematographer
            #     if self.battle.activeSuits[i].currHP <= 0 and not self.suitHasCondition(suitId, 'killedbyvideo') and not self.__suitCanAttack(
            #         suitId):
            #         attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
            #                                 'name': 'VideographerVideoStatic',  # Video Static Upon Death
            #                                 'animName': 'glower',
            #                                 'hp': 0,
            #                                 'acc': 100,
            #                                 'freq': 0,
            #                                 'group': SuitBattleGlobals.ATK_TGT_SINGLE})
            #         if attack[SUIT_ATK_COL]:
            #             self.battle.suitAttacks.append(attack)
            if self.battle.activeSuits[i].dna.name == 'choreo':  # choreographer
                # if self.battle.activeSuits[i].currHP <= 0 and not self.suitHasCondition(suitId, 'killedbyvideo') and not self.__suitCanAttack(
                #     suitId):
                #     attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                #                             'name': 'VideographerVideoStatic',  # Video Static Upon Death
                #                             'animName': 'glower',
                #                             'hp': 0,
                #                             'acc': 100,
                #                             'freq': 0,
                #                             'group': SuitBattleGlobals.ATK_TGT_SINGLE})
                #     if attack[SUIT_ATK_COL]:
                #         self.battle.suitAttacks.append(attack)
                if (self.TurnsElapsed + 1) % 2 == 0 and self.__suitCanAttack(suitId):
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
                if self.suitHasCondition(suitId, 'retaliationcalculator') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                            'name': 'DirectorActionRetaliation',
                                            'animName': 'nothing',
                                            'hp': 0,
                                            'acc': 100,
                                            'freq': 0,
                                            'group': SuitBattleGlobals.ATK_TGT_GROUP,
                                            'priorityToonConditions': ('collectcalled',)})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'retaliationcalculator2') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                           'name': 'DirectorCut',
                                                           'animName': 'nothing',
                                                           'hp': 0,
                                                           'acc': 100,
                                                           'freq': 0,
                                                           'group': SuitBattleGlobals.ATK_TGT_GROUP,
                                            'excludeToonConditions': ('bookkeepingtoon',)})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.TurnsElapsed % 3 == 0 and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                           'name': 'DirectorActionCog',
                                                           'animName': 'nothing',
                                                           'hp': 0,
                                                           'acc': 100,
                                                           'freq': 0,
                                                           'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                            'targetType': 'suit',

                            'allowSelfTarget': True,
                            'targetSelf': False,
                        'excludeManagers': False,
                        'requireDamaged': False,
                             'requiredManagerNames':  ('cinema', 'fmaker', 'director', 'choreo'),})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if (self.TurnsElapsed + 1) % 3 == 0 and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                           'name': 'DirectorActionPartner',
                                                           'animName': 'nothing',
                                                           'hp': 0,
                                                           'acc': 100,
                                                           'freq': 0,
                                                           'group': SuitBattleGlobals.ATK_TGT_SINGLE})
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
                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE,

                        'targetType': 'suit',
                        'applyDamage': False,
                        'targetSelf': True,})
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
                        self.calculator.directorMultiplier += 2

        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'videog' and not self.suitHasCondition(suitId, 'immune'):
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
    

        # Secondary Cheats
        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'videog':
                if self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                        'name': 'VideographerRisingStarsSacrifice',
                                                        # Rising Stars Sacrifice
                                                        'animName': 'snap',
                                                        'hp': 0,
                                                        'acc': 100,
                                                        'freq': 0,
                        'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                        'targetType': 'suit',
                        'allowSelfTarget': False,
                        'targetSelf': False,
                        'targetHealthiest': True,
                        'excludeManagers': True
                    })
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'phase3') and not len(self.battle.activeSuits) > 5 and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'VideographerRisingStars2',  # Rising Stars
                                                            'animName': 'song-and-dance',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                            'targetType': 'none',})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'phase2') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                            'name': 'VideographerElectricShock4',  # Rising Stars
                                                            'animName': 'snap',
                                                            'hp': 0,
                                                            'acc': 100,
                                                            'freq': 0,
                                                            'group': SuitBattleGlobals.ATK_TGT_GROUP,
                                    'targetType': 'suit',
                                'excludedManagerNames': ('videog', 'bcaster', 'mplayers',),
                            'allowSelfTarget': False,
                            'targetSelf': False,
                        'excludeManagers': False})

                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if not self.suitHasCondition(suitId, 'phase2') and self.battle.activeSuits[
                                i].currHP <= 28888 and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                        'name': 'VideographerDirectorCuts',  # Director Cuts
                                                        'animName': 'song-and-dance',
                                                        'hp': 0,
                                                        'acc': 100,
                                                        'freq': 0,
                                                        'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                            'targetType': 'none',})
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
                                                        'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                            'targetType': 'none',})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if not self.suitHasCondition(suitId, 'phase3') and not self.suitHasCondition(suitId, 'phase2') and not self.suitHasCondition(suitId, 'immune') and not self.suitHasCondition(suitId, 'silhouettespawn') and not self.suitHasCondition(suitId, 'directorscuts') and not len(
                                self.battle.activeSuits) > 7 and self.__suitCanAttack(suitId) and self.TurnsElapsed % 2 == 0:
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                        'name': 'VideographerRisingStars',  # Rising Stars Hollywoods
                                                        'animName': 'song-and-dance',
                                                        'hp': 0,
                                                        'acc': 100,
                                                        'freq': 0,
                                                        'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                                        'targetType': 'none'})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)
                if self.suitHasCondition(suitId, 'electricshockcalculator') and not self.suitHasCondition(suitId, 'phase2') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                        'name': 'VideographerStarOfTheShow',  # Electric Shock
                                                        'animName': 'snap',
                                                        'hp': 0,
                                                        'acc': 100,
                                                        'freq': 0,
                                                        'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                                                           'targetType': 'suit',

                            'allowSelfTarget': False,
                            'targetSelf': False,
                        'excludeManagers': True})

                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)

        for i in xrange(len(self.battle.activeSuits)):
            suitId = self.battle.activeSuits[i].doId
            if self.battle.activeSuits[i].dna.name == 'videog':
                if self.suitHasCondition(suitId, 'immunecalculator') and not self.suitHasCondition(suitId, 'phase3') and self.suitHasCondition(suitId, 'phase2') and self.__suitCanAttack(suitId):
                    attack = self.__getCheatAttack(suitId, {'suitName': self.battle.activeSuits[i].dna.name,
                                                        'name': 'VideographerPhase3',
                                                        # Rising Stars Sacrifice
                                                        'animName': 'nothing',
                                                        'hp': 0,
                                                        'acc': 100,
                                                        'freq': 0,
                                                        'group': SuitBattleGlobals.ATK_TGT_SINGLE,
                                                           'targetType': 'none',
})
                    if attack[SUIT_ATK_COL]:
                        self.battle.suitAttacks.append(attack)

        for suit in self.battle.activeSuits[:]:
            suitId = suit.doId

            if (
                suit.dna.name == 'choreo' and
                suit.currHP > 0
            ):

                # If he cannot attack, use the queued ability instead.
                if not self.__suitCanAttack(suitId):
                    continue

                # Otherwise do the Failsafe Protocol shuffle.
                oldActiveSuits = self.battle.activeSuits[:]
                oldLivingSuits = []
                livingPositions = []

                for index in xrange(len(oldActiveSuits)):
                    otherSuit = oldActiveSuits[index]

                    if (
                        otherSuit.currHP > 0 and
                        not self.suitHasCondition(otherSuit.doId, 'dead')
                    ):
                        oldLivingSuits.append(otherSuit)
                        livingPositions.append(index)

                if suit not in oldLivingSuits or len(oldLivingSuits) < 2:
                    continue

                newLivingSuits = oldLivingSuits[:]
                random.shuffle(newLivingSuits)

                if newLivingSuits == oldLivingSuits:
                    newLivingSuits.reverse()

                newActiveSuits = oldActiveSuits[:]

                for index in xrange(len(livingPositions)):
                    newActiveSuits[livingPositions[index]] = newLivingSuits[index]

                payload = self.__encodeSuitOrder(
                    oldActiveSuits,
                    newActiveSuits
                )

                attack = self.__getCheatAttack(
                    suitId,
                    {
                        'suitName': suit.dna.name,
                        'name': 'ChoreoPlacesEveryone',
                        'animName': 'song-and-dance',
                        'hp': payload,
                        'acc': 100,
                        'freq': 0,
                        'group': SuitBattleGlobals.ATK_TGT_GROUP,
                                        'targetType': 'none'
                    }
                )

                if attack[SUIT_ATK_COL]:
                    self.battle.suitAttacks.append(attack)

                    # Corporate Restructuring invalidates all existing trap positions.

                    self.battle.queueSuitOrder(
                        [otherSuit.doId for otherSuit in newActiveSuits]
                    )


