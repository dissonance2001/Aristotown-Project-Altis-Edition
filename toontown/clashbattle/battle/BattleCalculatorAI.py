from operator import attrgetter

from otp.ai.AIBaseGlobal import simbase
from toontown.clashbattle.battle.BattleEventDefinitionClasses import EnvironmentalEventDefinition
from toontown.clashbattle.battle import BattleExperienceAI
from toontown.clashbattle.battle.BattleGlobals import *
from toontown.clashbattle.battle.BattleListenerAI import BattleListenerAI
from toontown.clashbattle.battle.attacks.base.AttackOrder import AttackOrder
from toontown.clashbattle.battle.attacks.server.AttackRepositoryAI import createAttack
from toontown.clashbattle.battle.attacks.server.suit import *
from toontown.clashbattle.battle.attacks.server.toon import *
from toontown.clashbattle.battle.BattleAvatar import BattleAvatar
from toontown.clashbattle.battle.BattleListenerObject import BattleListenerObject
from toontown.clashbattle.battle.environmental.base.EnvironmentalEnum import EnvironmentalEnum
from toontown.clashbattle.battle.environmental.server.EnvironmentalRepository import createEnvironmental
from toontown.clashbattle.battle.environmental.server.Environmentals import EnvironmentalBase
from toontown.clashbattle.battle.statuses import StatusEffects
from toontown.modifiers.classes.GagsContentSyncModifier import GagsContentSyncModifier
from toontown.clashsuit.suit.ClashSuitBaseAI import ClashSuitBaseAI
from toontown.toon.ClashDistributedToonBaseAI import ClashDistributedToonBaseAI
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory

from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from toontown.clashbattle.battle.distributed.ClashBattleBaseAI import ClashBattleBaseAI


@DirectNotifyCategory()
class BattleCalculatorAI(BattleListenerObject):
    """
    An object that persists throughout the entire duration of the battle
    which handles all of the calculations required, as well as stores
    important information pertaining to the battle, such as suit lures,
    suit traps, and toon experience.
    """

    __slots__ = (
        "propBonus", "skillCreditMultiplier", "toons", "suits", "environmentals",
        "toonSkillPtsGained", "attackOrder", "levelBonus", "rounds",
        "attacksAddedThisIndex", "battleListener", "targetHitsTrack", "target2attacks",
        "attackResults", "toonAttacks",
    )

    def __init__(self, battle, propBonus: int = -1) -> None:
        self.propBonus = propBonus
        self.skillCreditMultiplier: int = 1
        self.toons = []  # type: list[ClashDistributedToonBaseAI]
        self.suits = []  # type: list[ClashSuitBaseAI]
        self.environmentals = []  # type: list[EnvironmentalBase]
        self.toonSkillPtsGained: dict = {}
        self.attackOrder = AttackOrder()
        self.levelBonus: int = 0
        self.rounds: int = 0
        self.attacksAddedThisIndex: int = 0
        self.battle = battle  # type: ClashBattleBaseAI
        self.battleListener = BattleListenerAI(self)
        self.resetRoundStats()
        self.clearAttacks()
    
    def cleanup(self) -> None:
        self.clearAttacks()
        self.battleListener.cleanup()
        del self.battleListener
        del self.toons
        del self.suits
        del self.toonAttacks
        del self.environmentals
        del self.battle
    
    def setSkillCreditMultiplier(self, mult: float) -> None:
        self.skillCreditMultiplier = simbase.air.baseXpMultiplier * mult

    def getSkillCreditMultiplier(self) -> float:
        return self.skillCreditMultiplier

    def getBattleListener(self) -> BattleListenerAI:
        return self.battleListener
    
    def getAttackOrder(self) -> List[AttackAI]:
        return self.attackOrder.getAttacks()
    
    def setParticipants(self, toons: list, suits: list) -> None:
        self.toons = toons  # type: list[ClashDistributedToonBaseAI]
        self.suits = suits  # type: list[ClashSuitBaseAI]
        self.sendEvent(BEG.EVENT_SET_PARTICIPANTS, [toons, suits])
    
    def getParticipants(self) -> list:
        return self.toons + self.suits
    
    def clearAttacks(self) -> None:
        self.toonAttacks = {}  # type: dict[int, ToonAttackAI]
        self.attackOrder.cleanup()
    
    def getToon(self, toonId: int) -> ClashDistributedToonBaseAI:
        return simbase.air.getDo(toonId)
    
    def getSuit(self, suitId: int) -> ClashSuitBaseAI:
        return simbase.air.getDo(suitId)
    
    def showToonTipAll(self, tipId: int) -> None:
        for avId in self.toons:
            toon = self.getToon(avId)
            if toon:
                toon.showToonTip(tipId)
    
    """
    Methods related to round calculation.
    """

    def getCurrentRound(self) -> int:
        return self.rounds

    def resetRoundStats(self) -> None:
        """
        Reset any values that are only relevent to the current round.
        """
        self.targetHitsTrack = {}
        self.target2attacks = {}

        self.attackResults = []

    def calculateRound(self) -> None:
        """
        Initializes the round and calls the main functions used for calculating.
        """
        self.resetRoundStats()

        self.rounds += 1

        if self.rounds == 1:
            self.sendEvent(BEG.EVENT_BEGIN_FIRST_ROUND)
        self.sendEvent(BEG.EVENT_BEGIN_ROUND)

        # The credit level is determined by the highest level suit.
        self.creditLevel = max([suit.getActualLevel() for suit in self.suits])

        self.calculateAttackOrder()

        # Now that the round is initialized, calculate each attack in order.
        self.determineNextAttack()

        self.sendEvent(BEG.EVENT_END_ROUND)

    def getToonTracks(self):
        return NON_GAG_TRACK_ORDER + self.battle.gagOrder
    
    def calculateAttackOrder(self) -> None:
        """
        Defines the order of attacks for the current round.
        """

        # The toon attack order is a list of lists with the toon attack indicator, the track, and the attacks.
        toonAttackOrder = []

        # In the case that multiple Toons trap the same suit, don't trap cancel: choose the best Trap to use
        self.chooseBestTrapPerSuit()

        # Go through each toon gag track and add it to the attack order if it exists.
        for track in self.getToonTracks():
            attacks = self.findToonAttack(track)
            if attacks:
                # Sort based on whether the toon is an NPC or not.
                # Toons will calculate first, then the NPCS.
                attacks.sort(key=attrgetter("attackType"))

                # The level bonus is determined by the highest gag being used of the same track.
                if track in ATTACK_TRACKS:
                    highestLevelAttack = max(attacks, key=lambda atk, track=track: atk.getTrackExp(track))
                    highestLevelAttack = GagsContentSyncModifier.capTrackAccuracyLevel(
                        do=attacks[0].invoker,  # doesn't matter which invoker we choose
                        cap=highestLevelAttack.getTrackExp(track)
                    )
                    levelBonus = AttackAccPerGagLvl[highestLevelAttack]
                    if track == AttackEnum.TOON_HEAL:
                        levelBonus /= 2
                else:
                    levelBonus = 0

                for attack in attacks:
                    # Discard the old attack and replace it with a new one.
                    # The old attack is really only meant to store the toon's
                    # choice before the round begins to calculate, and
                    # lacks pertinent information that could be tacked on
                    # line by line, but this seems more elegant.
                    newAttack: AttackAI = createAttack(
                        attack.attackType, rounds=self.rounds, invoker=attack.invoker, 
                        level=attack.level, target=attack.target,
                        propBonus=self.propBonus, expGained=self.toonSkillPtsGained,
                        creditMult=self.getSkillCreditMultiplier(), creditLevel=self.creditLevel,
                        levelBonus=levelBonus, targetHitsTrack=self.targetHitsTrack,
                    )
                    self.toonAttacks[attack.invoker.doId] = newAttack

                    newAttack.battle = self.battle
                    newAttack.setBattleListener(self.getBattleListener())
                    newAttack.toons = self.toons
                    newAttack.suits = self.suits
                    newAttack.environmentals = self.environmentals
                    newAttack.attackAmount = len(attacks)
                    newAttack.setTargetList()

                    toonAttackOrder.append(newAttack)

                # Reset the list of attacks with our new attacks.
                attacks = self.findToonAttack(track)

                # Iterate through the target list and set the track bonus status for
                # each target. If the target hasn't been previously targeted with a
                # prestiged attack, reset the target's flag in the dictionary.
                # NOTE: this is needed for some prestiges to function better.
                for attack in attacks:
                    for target in attack.targets:
                        targetId = getattr(target, "doId", target)
                        # Track the amount of toon attacks being used against a certain
                        # target.
                        self.target2attacks.setdefault(targetId, [])
                        self.target2attacks[targetId].append(attack)
                
                # Finally, set the targetAttacks variable for each attack.
                for attack in attacks:
                    attack.targetAttacks = self.target2attacks

        # Add the toon attacks to the attack order.
        self.attackOrder.extend(toonAttackOrder)
        self.sendEvent(BEG.EVENT_TOON_ATTACK_ORDER, [toonAttackOrder])

        # Send an event telling any listening suits to create their attacks.
        self.sendEvent(BEG.EVENT_SUIT_ATTACK_ORDER)

        # Send an event with the "complete" attack order.
        self.sendEvent(BEG.EVENT_ATTACK_ORDER, [self.attackOrder])

    def determineNextAttack(self) -> None:
        """
        Recursively iterate through the attack order to calculate each attack.
        Returns once the attack index is out of bounds of the attack order.
        """
        attack = next(self.attackOrder)
        
        # We have reached the end of the attack order.
        if attack is None:
            # No attacks have gone at all. Forcefully run the normal attacks over events in this case.
            if self.attackOrder.attackIndex == -1:
                if self.attackOrder.reachedEnd():
                    if not self.hasEventBeenSent(BEG.EVENT_NORMAL_ATTACKS_OVER):
                        self.sendEvent(BEG.EVENT_NORMAL_ATTACKS_OVER)
                    else:
                        return
                self.determineNextAttack()
            return

        # Ensure that the attack hasn't already been calculated.
        if attack.attackIndex == -1:
            self.attacksAddedThisIndex = 0

            # We grab the attack again, as it might have changed since the event was called.
            if attack.isSuit(attack.invoker) and not attack.inserted and \
                not self.hasEventBeenSent(BEG.EVENT_BEGIN_SUIT_ATTACKS):
                self.sendEvent(BEG.EVENT_BEGIN_SUIT_ATTACKS)
                attack = self.attackOrder.getCurrentAttack()

            success = self.calculateAttack(attack)
            # If the attack didn't finish properly, check to see if the attack
            # chain has ended. (if one exists)
            if not success:
                self.checkFinishChain(attack)

            if self.attackOrder.reachedEnd() and not self.hasEventBeenSent(BEG.EVENT_NORMAL_ATTACKS_OVER):
                self.sendEvent(BEG.EVENT_NORMAL_ATTACKS_OVER)

            self.sendEvent(BEG.EVENT_NEXT_ATTACK)
        else:
            # Print to the console about what happened.
            self.notify.warning(
                "An attack which has already been calculated has somehow been shifted into the subsection "\
                "of the attack order which has yet to be calculated., thus queueing it to be calculated again.\n"\
                f"{repr(attack)}"
            )

        # If the attack inherits from the end battle attack,
        # stop calculating.
        if isinstance(attack, EndBattleAttackAI):
            return

        self.determineNextAttack()
    
    def calculateAttack(self, attack: AttackAI) -> bool:
        """Performs all of the necessary calculations for the
        attack object.

        :return: If the attack calculated in full without a hitch.
        """
        # Specific checks if an invoker was provided.
        if attack.invoker:
            if isinstance(attack.invoker, ClashSuitBaseAI):
                if attack.invoker.getHp() <= 0 or attack.invoker.reviveCheckAndClear():
                    return False

                # Suits that can't attack this turn, well, cannot attack this turn.
                # If the cant attack status effect in question is lure, first check if the unlure flag is set on the
                # attack before making them 'pass'.
                if attack.invoker.getStatusEffectOfType(StatusEffects.CantAttackStatusEffect):
                    if attack.invoker.getStatusEffectOfType(StatusEffects.LureStatusEffect) and attack.unlure:
                        AttackAI.unlureSuit(attack.invoker, instant=True)
                    else:
                        return False

            elif isinstance(attack.invoker, ClashDistributedToonBaseAI):
                if attack.invoker.getHp() <= 0:
                    return False

                if attack.invoker.getStatusEffectOfType(StatusEffects.CantAttackStatusEffect):
                    return False

        # Set the target list.
        attack.setTargetList()

        # Then sanity check the target list (if there is one for this attack).
        if attack.targets:
            # Ensure that all of the attack's targets
            # aren't dead.
            allDead = True
            for target in attack.targets:
                if isinstance(target, BattleAvatar):
                    if target.getHp() > 0:
                        allDead = False
                        break
                else:
                    tgt: ClashDistributedToonBaseAI = self.getToon(target)
                    if tgt and tgt.getHp() > 0:
                        allDead = False
                        break

            if allDead:
                return False

        # Ensure that the target list matches up
        # with what the attack requires.
        if attack.REQUIRED_TARGETS and len(attack.targets) < attack.REQUIRED_TARGETS:
            return False
        
        # Update the targets hit in the current track up until this
        # point.
        if isinstance(attack, ToonAttackAI):
            self.targetHitsTrack.update(self.getToonTargetHits(attack.attackType))

        # Set the attack's attack index.
        attack.attackIndex = self.attackOrder.attackIndex

        # Calculate the attack.
        attack.calculate()
        if isinstance(attack.invoker, ClashSuitBaseAI):
            self.notify.warning(f'>>> SUIT ATTACK CALC, dodge flag={getattr(simbase, "toonsAlwaysDodge", "MISSING")}')
        if getattr(simbase, 'toonsAlwaysDodge', False) and isinstance(attack.invoker, ClashSuitBaseAI):
            for result in attack.results:
                result.landed = False
                result.hpAdjust = 0
                result.hpBonus = 0
                result.kbBonus = 0

        # Stop this attack from listening to events now that it's calculated.
        self.removeListenerObject(attack)

        # Non-chained attacks will apply normally.
        if not self.checkFinishChain(attack):
            attack.apply()

        # Successfully calculated to the end.
        return True

    def checkFinishChain(self, attack: AttackAI) -> bool:
        # If we've reached the end of a chain of toon attacks,
        # handle all of the hp adjusts + bonuses.
        if isinstance(attack, ToonAttackAI):
            attacks = self.findToonAttack(attack.attackType)
            # This should never be the case. I hate Toontown.
            if not attacks:
                self.targetHitsTrack.clear()
                return False

            if attack == attacks[-1]:
                self.finishToonTrackChain(attacks, attack.attackType)
                self.targetHitsTrack.clear()
            return True

        return False

    def finishToonTrackChain(self, 
                             attacks,  # type: list[ToonAttackAI]
                             attackType: AttackEnum) -> None:
        # Cull toon attacks which didn't successfully calculate.
        attacks = [attack for attack in attacks if attack.attackIndex > -1]

        # Loop the first time to collect all of the base damages.
        base = {}
        for i, attack in enumerate(attacks):
            for result in attack.results:
                # Attacks that didn't hit the target
                # can't possibly contribute to any bonus damage.
                if not result.landed:
                    continue

                # Round the base damage value here.
                result.hpAdjust = attack.roundDamageValue(result.hpAdjust)

                # Attacks that don't have a set hp or kb bonus
                # can't possibly contribute to any bonus damage.
                if result.hpBonus == 0 and result.kbBonus == 0:
                    continue

                base.setdefault(result.avId, {'base': [], 'atkIndex': []})
                base[result.avId]['base'].append(result.hpAdjust)
                # Also keep track of every attack index which affects
                # this target id.
                base[result.avId]['atkIndex'].append(i)

        # Loop once more to attribute knockback and combination damage bonuses.
        for i, attack in enumerate(attacks):
            for result in attack.results:
                # Attacks that didn't hit the target
                # can't possibly contribute to any bonus damage.
                if not result.landed:
                    continue

                # Attacks that don't have a set hp or kb bonus
                # can't possibly contribute to any bonus damage.
                if result.hpBonus == 0 and result.kbBonus == 0:
                    continue

                obj = self.getToon(result.avId)
                lureEffect = obj.getStatusEffectOfType(StatusEffects.LureStatusEffect)
                numAttacks = len(base[result.avId]['base'])

                if attack.WANT_KB_BONUS and \
                    i == base[result.avId]['atkIndex'][-1] and lureEffect and result.kbBonus > 0:
                    result.kbBonus = -lureEffect.getKnockback() * numAttacks

                if attack.WANT_HP_BONUS and \
                    len(base[result.avId]['base']) > 1 and i == base[result.avId]['atkIndex'][-1]:
                    # The multiplier for hp bonus is initially stored in result itself.
                    # In cases where we don't want combo damage, this value will be 0, thus
                    # resulting in an hpBonus of 0.
                    mult = result.hpBonus

                    # Get the base damage.
                    baseDamage = sum(base[result.avId]['base'])
                    # Add the knockback bonus to it.
                    if attack.WANT_KB_BONUS and result.kbBonus < 0:
                        baseDamage += result.kbBonus

                    result.hpBonus = baseDamage * mult
                else:
                    result.hpBonus = 0

        # Apply all of the damages to the target list.
        for attack in attacks:
            attack.apply()
        
        # Update the battle trap for each suit.
        if attackType == AttackEnum.TOON_TRAP:
            for suit in self.suits:
                trapEffect = suit.getStatusEffectOfType(StatusEffects.TrappedStatusEffect)
                if trapEffect:
                    suit.battleTrap = trapEffect.getTrapLevel()
        
        # Clear the targets hit for this track.
        self.targetHitsTrack.clear()

        # Send event that we're ending this track, perhaps moving on to the next track.
        self.sendEvent(BEG.EVENT_END_TOON_TRACK, [attackType, attacks])
    
    def createToonAttack(self, attackType: AttackEnum, toon, *args, **kwargs) -> ToonAttackAI:
        """Safely creates a toon attack, defaulting to a ToonAttackAI if one
        does not exist for the given attackType.
        """
        if toon.doId in self.toonAttacks:
            self.toonAttacks[toon.doId].cleanup()
            del self.toonAttacks[toon.doId]

        attack = AttackRepository.get(attackType, ToonAttackAI)(attackType, self.rounds, toon, *args, **kwargs)
        self.toonAttacks[toon.doId] = attack
        return attack
    
    def createAndInsertAttack(self, attackType: AttackEnum, attackKwargs: dict=None,
                              insertKwargs: dict=None) -> None:
        """Creates an attack of the given AttackEnum and inserts it into the
        attack order.

        :param attackType: The AttackEnum which to create.
        :param attackKwargs: A dictionary of arguments to supply to the attack object.
        :param insertKwargs: A dictionary of arguments to supply to the insertAttack
        method.
        """
        attackKwargs = attackKwargs or {}
        insertKwargs = insertKwargs or {}

        # Sanity check to ensure that attacks aren't invoked by an avatar
        # who is outside of the battle.
        invoker = attackKwargs.get("invoker")
        if isinstance(invoker, BattleAvatar) and invoker.getBattleState() != BattleStateEnum.ACTIVE:
            return

        attack: AttackAI = createAttack(attackType, **attackKwargs)

        self.insertAttack(attack, **insertKwargs)
    
    def insertAttack(self, attack: AttackAI, mode: str = "insert", index: int = None,
                     respectPreviousAdditions: bool = True, adjust: bool = True,
                     priority: int = 0, overrideInserted=None) -> None:
        """Inserts an AttackAI object into the attack order.
        
        :param attack: The AttackAI object.
        :param mode: The defined insert behavior. Defined attack behaviors:

        - insert: Inserts the object at the current position of the attack order.
        - end: Appends the object to the attack order.
        - beginning: Inserts the object at the beginning of the attack order.
        (NOTE: this mode should only be used before attacks begin to calculate.)
        - replace: Replaces the attack object at the current index with the given
        attack object.

        :param index: The index in which to insert the attack object at. This value
        defaults to the current attack index.
        :param respectPreviousAdditions: When this flag is set to True, the attack object
        will be inserted *after* all of the attacks which have been inserted in the current
        attack index. Otherwise, it will ignore the inserted attacks.
        :param adjust: When this flag is set to False, the attack will be inserted in place
        of the current attack. This means that the current attack will happen after the
        inserted attack happens.
        :param priority: The relative priority of when this attack should happen in the queue.
        Higher will happen later.
        :param overrideInserted: Normally, attacks will be counted as inserted when appending onto the attack
        order. However, if we do not wish to count them as inserted (such as with standard cog attacks), we can
        override the inserted flag to ensure battle operations still run smoothly.
        """
        attack.priority = priority

        if mode == "insert":
            index = self.attackOrder.getNextAvailableIndex() if index is None else index

            amount = self.attacksAddedThisIndex if respectPreviousAdditions else 0
            # Adjustment basically defines whether or not you want this attack to be bumped up one
            # (next in line for attacks) or if you want it to go in place of the current attack.
            # Rarely will you want it to go in place of the current attack. For an example of this,
            # See the factory foreman event definition.
            adjustment = 1 if adjust else 0
            self.attacksAddedThisIndex += 1

            self.attackOrder.insert(index + adjustment + amount, attack, overrideInserted=overrideInserted)
        elif mode == "end":
            self.attackOrder.append(attack, overrideInserted=overrideInserted)
        elif mode == "beginning":
            self.attackOrder.insert(0, attack)
        elif mode == "replace":
            self.attackOrder.replaceCurrent(attack)
        else:
            raise Exception(f"Unknown insert mode: {mode}")

        attack.battle = self.battle
        attack.setBattleListener(self.getBattleListener())
        attack.toons = self.toons
        attack.suits = self.suits
        attack.rounds = self.rounds

    def createEnvironmental(self, environmentalType: EnvironmentalEnum, **kwargs) -> None:
        """Creates an environmental of the given type.
        
        :param environmentalType: The EnvironmentalEnum in which to create.
        :param kwargs: An option dictionary of keyword arguments to supply to the
        environmental object itself.
        """

        # Create the environmental object.
        environmental: EnvironmentalBase = createEnvironmental(environmentalType, self.battle, self.battleListener, **kwargs)

        # Assign any values stored in the battle calculator to the environmental.
        environmental.setParticipants(self.toons, self.suits)

        # Begin listening to events from the environmental.
        self.addListenerObject(environmental, EnvironmentalEventDefinition)
        self.environmentals.append(environmental)

    def getEnvironmentalOfType(self, envType: EnvironmentalEnum) -> Optional[EnvironmentalBase]:
        for env in self.environmentals:
            if envType in env.environmentalType:
                return env
        return None
    
    def removeEnvironmental(self, environmental: EnvironmentalBase) -> None:
        if not isinstance(environmental, EnvironmentalEnum):
            if environmental in self.environmentals:
                self.environmentals.remove(environmental)
            self.removeListenerObject(environmental)
            return
        
        for env in list(self.environmentals):
            if environmental in env.environmentalType:
                self.environmentals.remove(env)
                self.removeListenerObject(env)

    def toonLeftBattle(self, toonId):
        """
        Removes the indicated toon from the battle calculator.
        This should only be called after the movie is done playing,
        as only then can it be determined whether the toon has
        actually died or not.
        """
        av = simbase.air.doId2do.get(toonId)
        if av:
            self.sendEvent(BEG.EVENT_TOON_LEFT, [av])

        for suit in self.suits:
            if toonId in suit.aggroMap:
                del suit.aggroMap[toonId]

    def suitLeftBattle(self, suit: ClashSuitBaseAI) -> None:
        """
        Removes the indicated suit from the battle calculator.
        """
        # Clear their aggro map.
        suit.aggroMap.clear()

        # Clear all of their status effects now that they are dead.
        self.removeStatusEffectsFromSuit(suit)

        self.sendEvent(BEG.EVENT_SUIT_LEFT, [suit])

        # And make sure the battle listener is no longer listening to this suit.
        if not suit.hasCleanedUpBattle:
            self.removeListenerObject(suit)

    def getSkillGained(self, toonId, track):
        return BattleExperienceAI.getSkillGained(self.toonSkillPtsGained, toonId, track)

    def checkForSkillPoints(self):
        for toonId in list(self.toonSkillPtsGained.keys())[:]:
            toon = self.getToon(toonId)
            if toon and toon.getHp() <= 0:
                del self.toonSkillPtsGained[toonId]

    def getLuredSuits(self):
        return [suit for suit in self.getActiveSuits() if suit.getStatusEffectOfType(StatusEffects.LureStatusEffect)]

    def getSoakedSuits(self):
        soakedSuits = []
        for suit in self.suits:
            if suit.getStatusEffectsOfType(StatusEffects.SoakStatusEffect):
                soakedSuits.append(suit)
        return soakedSuits

    def unlureSuit(self, suit: ClashSuitBaseAI, instant: bool = False) -> None:
        """
        Unlures a suit given it is actually lured and it hasn't been already unlured.
        """
        lureEffect = suit.getStatusEffectOfType(StatusEffects.LureStatusEffect)

        if lureEffect:
            if instant:
                lureEffect.delete()
            else:
                lureEffect.setUsed(1)

    def unsoakSuit(self, suit: ClashSuitBaseAI) -> None:
        soakEffect = self.getSuitEffectOfType(suit, StatusEffects.SoakStatusEffect)
        if soakEffect:
            soakEffect.delete()

    def getAllToons(self):
        toons = []
        for toonID in self.toons:
            toon = self.getToon(toonID)
            if toon:
                toons.append(toon)
        return toons
    
    def getAliveToons(self):
        return [toon for toon in self.getAllToons() if toon.getHp() > 0]

    def doesToonHaveEffectOfType(self, toonID, effectType):
        toonProfile = self.getToon(toonID)
        if toonProfile:
            statusEffects = toonProfile.getStatusEffectsOfType(effectType)
            if statusEffects:
                return True

        return False

    def getSuitEffectOfType(self, suit: ClashSuitBaseAI, effectType):
        effects = suit.getStatusEffectsOfType(effectType)
        if effects:
            return effects[0]

    def removeStatusEffectsFromSuit(self, suit: ClashSuitBaseAI) -> None:
        # Prevent fail fast iteration and other wonky stuff
        suit.clearStatusEffects()

    def getAllToonStatusEffects(self):
        """
        :return: Returns a list of EVERY Status Effect on the Toons.
        """
        retList = []
        for profile in self.getAllToons():
            retList += profile.getStatusEffects()
        return retList
    
    def findToonAttack(self, track, overrideAttackDict=None):
        """ findToonAttack(track)
            Return all attacks of the specified track sorted by increasing level
        """
        foundAttacks = []  # type: list[ToonAttackAI]
        for toonId, attack in list((overrideAttackDict or self.toonAttacks).items()):

            # Prevent a race condition in which the invoker was
            # disconnected from the server, but they still have an attack.
            if getattr(attack.invoker, "experience", None) is None and not overrideAttackDict:
                attack.cleanup()
                del self.toonAttacks[toonId]
                continue

            # We need to do certain filtering based on the track then.
            # Continue looping if this track does not match.
            if track != attack.attackType:
                continue

            # Are we dealing with fires?
            elif track == AttackEnum.TOON_FIRE:
                # If fires are already being used on the same target, ignore.
                for attackCheck in foundAttacks:
                    if attackCheck.target == attack.target:
                        continue

            # Is this a gag track?
            elif track in BattleGlobals.ATTACK_TRACKS:

                # Need to confirm the Toon has this gag.
                if not getattr(attack.invoker, "inventory", None):
                    # Toon has no inventory -- ignore.
                    continue

                # Do they have an item?
                if attack.invoker.inventory.numItem(track, attack.originalLevel) <= 0:
                    pipsqueak = attack.invoker.getStatusEffectOfId(SEE.EFFECT_PIP_COUNTER)
                    counterfeit = attack.invoker.getStatusEffectOfId(SEE.EFFECT_COUNTERFEIT_CONTAINER)
                    if not (pipsqueak or (counterfeit and counterfeit.getGagTrackLevel(track, attack.originalLevel))):
                        # Toon does not have this Gag -- ignore.
                        continue

            # At this point, this attack is safe to add.
            foundAttacks.append(attack)

        return sorted(foundAttacks, key=attrgetter("level"))

    def getToonTargetHits(self, attackType: AttackEnum = None) -> dict:
        """Returns a dictionary with each avatar doId and how
        many times a toon attack gag has successfully
        landed on them.
        """
        # Start with all targets zeroed out.
        targetDict = {}

        for attack in self.attackOrder:
            if not isinstance(attack, ToonAttackAI):
                continue
            # If an attack type was specified, we want to only
            # look for attacks of that type.
            if attackType and attack.attackType != attackType:
                continue
            # Results will be empty for attacks which
            # have yet to be calculated.
            for result in attack.results:
                targetDict.setdefault(result.avId, [])
                targetDict[result.avId].append(result.landed)
        
        return targetDict

    def sortTrackByLevel(self, track):
        """
        Sorts a given track based on level and experience.
        This should only be necessary if you mess around with gag levels
        outside of standard means.
        """

        actualAttacks = self.attackOrder.getAttacks()
        attackDict = {attack.invoker.doId: attack for attack in actualAttacks if attack.attackType == track}

        trackIndices = self.attackOrder.getAllIndicesOfTrack(track)
        if not trackIndices:
            return

        # Grab a freshly, newly sorted version of our attacks.
        attacks = self.findToonAttack(track, overrideAttackDict=attackDict)
        # Sort based on whether the toon is an NPC or not.
        # Toons will calculate first, then the NPCS.
        attacks.sort(key=attrgetter("attackType"))
        newShortTrackAttackOrder = []  # Used for the below loop to fix self.toonAttacks
        # Rebuild a new trackIndices based on the new order
        # newTrackIndices = [trackIndices[attacks.index(newAttack)] for newAttack in attacks]
        # Now, we need to rebuild these indices based on our new sort order.
        for newAttackIndex in range(len(attacks)):
            # Run through the new order of attacks and move around our indices to fit
            # newActualAttack = actualAttacks[trackIndices[i]]
            newAttack = attacks[newAttackIndex]
            self.attackOrder._attacks[trackIndices[newAttackIndex]] = newAttack
            newShortTrackAttackOrder.append(newAttack)

        # We also need to replicate this to the battle calculator's self.toonAttacks dict.
        oldToonAttacks = self.toonAttacks.copy()
        self.toonAttacks = {}
        doneNewOrder = False
        # Don't look at this too hard
        for oldIndex, avId in enumerate(list(oldToonAttacks.keys())):
            attack = oldToonAttacks[avId]
            if attack in newShortTrackAttackOrder:
                if doneNewOrder:
                    continue
                doneNewOrder = True

                for newShortTrackAttack in newShortTrackAttackOrder:
                    self.toonAttacks[newShortTrackAttack.invoker.doId] = newShortTrackAttack
            else:
                self.toonAttacks[avId] = attack

    def chooseBestTrapPerSuit(self):
        """
        If multiple Toons target the same Suit with trap, only use the 'best' one and have the other Toons pass
            - Choose the trap that does the most damage
            - If traps deal the same damage, choose the lower level one
            - If traps are exactly the same, use the rightmost Toon's trap
        """
        trappedSuits = dict()
        for toon in self.toons:
            # Only care about Trap attacks
            attack = self.toonAttacks.get(toon)
            if not attack or attack.track != AttackEnum.TOON_TRAP:
                continue

            # Get a reference to the suit that we're targeting
            suit = self.getSuit(attack.target)
            if not suit:
                continue
            suitId = suit.doId

            # This suit is not being targeted by any Toon
            if trappedSuits.get(suitId) is None:
                trappedSuits[suitId] = toon
                continue

            # See if we override <existingTrap> and use <newTrap> on this suit, updating our <trappedSuits> dict
            existingTrap = self.toonAttacks[trappedSuits[suitId]]
            newTrap = self.toonAttacks[toon]

            # <newTrap> does more damage: always replace <existingTrap>
            if newTrap.getFinalDamage(suit) > existingTrap.getFinalDamage(suit):
                self.createToonAttack(AttackEnum.TOON_PASS, existingTrap.invoker)
                trappedSuits[suitId] = toon
            # Both traps deal the same damage: only replace <existingTrap> if <newTrap> is a lower level
            elif (newTrap.getFinalDamage(suit) == existingTrap.getFinalDamage(suit)
                  and newTrap.level < existingTrap.level):
                self.createToonAttack(AttackEnum.TOON_PASS, existingTrap.invoker)
                trappedSuits[suitId] = toon
            # Since rightmost toon is first element in <self.toons>,
            # we don't replace <existingTrap> in the event of ties
            else:
                self.createToonAttack(AttackEnum.TOON_PASS, newTrap.invoker)

    """
    Everything below is a set of functions useful for modifying the battle outside of normal means.
    These are largely used for suit special abilities.
    """

    @staticmethod
    def isCogHurt(suit, healthCap=1.0):
        return not suit.getHp() >= math.ceil(suit.getMaxHp() * healthCap)

    def getAliveCogs(self, suits=None):
        if not suits:
            suits = self.suits

        return [suit for suit in suits if suit.getHp() > 0]

    def getAliveSuits(self, suits=None):
        # Alias
        return self.getAliveCogs(suits=suits)

    def areCogsHurt(self, healthCap=1.0, suits=None):
        if not suits:
            suits = self.suits
        return any([self.isCogHurt(suit, healthCap) for suit in suits])

    def findCogInBattle(self, type, suits=None):
        if not suits:
            suits = self.suits
        for suit in suits:
            if not getattr(suit, "dna", None):
                continue
            if suit.dna.name == type:
                return suit

    def findNearbySuits(self, suit, suits=None):
        if not suits:
            suits = self.suits
        if suit not in suits:
            return []

        # Find the nearby suits.
        nearbySuits = []
        targetIndex = suits.index(suit)

        # First, attempt to find the target to the right.
        if targetIndex > 0:
            nearbySuits.append(suits[targetIndex - 1])

        # Then attempt to find the target to the left.
        if targetIndex < len(suits) - 1:
            nearbySuits.append(suits[targetIndex + 1])

        return nearbySuits

    def findAllCogsInBattle(self, name: str, suits=None):
        if not suits:
            suits = self.suits
        return [suit for suit in suits if suit.dna.name == name and suit.getHp() > 0]

    def allSuitsExceptMe(self, exceptSuit: ClashSuitBaseAI, suits=None):
        if not suits:
            suits = self.suits
        return [suit for suit in suits if suit is not exceptSuit]

    def unlureAllSuits(self, suits=None):
        if not suits:
            suits = self.suits
        [self.unlureSuit(suit, instant=True) for suit in suits]

    def isSuitLured(self, suit):
        return suit.getStatusEffectOfType(StatusEffects.LureStatusEffect)

    def isSuitSoaked(self, suit):
        return suit in self.getSoakedSuits()

    def unsoakAllSuits(self, suits=None):
        if not suits:
            suits = self.suits
        [self.unsoakSuit(suit) for suit in suits]

    def isASuitLured(self, suits=None):
        if suits is None:
            suits = self.suits
        return any([self.isSuitLured(suit) for suit in suits])

    def isASuitSoaked(self, suits=None):
        if not suits:
            suits = self.suits
        return any([self.isSuitSoaked(suit) for suit in suits])

    def doesBattleHaveMoreThanAmount(self, amount, suits=None):
        if not suits:
            suits = self.suits
        return len([suit for suit in suits if suit.getHp() > 0]) > amount

    @staticmethod
    def getSuitName(suit):
        return suit.dna.name
    
    def removeAllAttacksFromInvoker(self, invoker: BattleAvatar) -> None:
        for attack in self.getAttackOrder():
            if attack.invoker == invoker and attack.attackIndex == -1:
                self.attackOrder.remove(attack)
    
    def removeAttacksOfTypeFromInvoker(self, invoker: BattleAvatar, attackType: AttackEnum) -> None:
        """Removes every attack from the invoker which matches the given attack type.
        
        :param invoker: The avatar to remove the attacks from.
        :param attackType: The AttackEnum to remove.
        """
        for attack in self.getAttackOrder():
            if attack.invoker is invoker and attack.attackIndex == -1 and attack.attackType == attackType:
                self.attackOrder.remove(attack)

    def getActiveSuits(self):
        return self.suits

    @staticmethod
    def isCogElite(suit):
        return suit.isElite

    def isACogElite(self, suits=None):
        if not suits:
            suits = self.suits
        return any([suit.isElite for suit in suits])

    """
    Debug / QA Methods
    """

    def updateAccuracyGUI(self, attackOrder: list[ToonAttackAI]):
        """
        Sends a signal to update the Accuracy GUI for all Toons in battle

        :param attackOrder: The attacks used in this round
        """
        from toontown.toon.gui.DebugGagAccuracyGUI import AccuracyInfo
        for attack in attackOrder:
            target = self.getSuit(attack.target)

            # Toon-up and Trap have perfect accuracy
            if attack.attackType in [AttackEnum.TOON_HEAL, AttackEnum.TOON_TRAP]:
                accInfo = AccuracyInfo.getAttackAlwaysHits()
            # Drop always misses on lured cogs
            elif (attack.attackType == AttackEnum.TOON_DROP and
                  target.getStatusEffectOfType(StatusEffects.LureStatusEffect)):
                accInfo = AccuracyInfo.getAttackAlwaysMisses()
            # Zap always hits on soaked cogs, always misses on unsoaked cogs
            elif attack.attackType == AttackEnum.TOON_ZAP:
                if target.getStatusEffectOfType(StatusEffects.ZapDealsBoostedDamage):
                    accInfo = AccuracyInfo.getAttackAlwaysHits()
                else:
                    accInfo = AccuracyInfo.getAttackAlwaysMisses()
            # Use accuracy methods in 'ToonAttackAI' to calculate results
            elif attack.attackType in BattleGlobals.ATTACK_TRACKS:
                rawAcc, accOverride = attack.getRawAccuracyOrOverride()
                maxDef, defOverride = attack.getMaxDefenseOrOverride()
                numStuns = attack.maxTargetHits
                finalAcc = attack.getFinalAccuracy(rawAcc, maxDef)
                accInfo = AccuracyInfo(rawAcc, accOverride, maxDef, defOverride, numStuns, finalAcc)
            else:
                accInfo = AccuracyInfo.getAttackAlwaysMisses()

            # Update Gag-Accuracy GUI for <toon>
            accGUIInfo = ['update', *accInfo.toStruct()]
            toon = self.getToon(attack.invoker.doId)
            toon.d_debugGagAccuracy(accGUIInfo)

    @staticmethod
    def removeAccuracyGUI(toon: ClashDistributedToonBaseAI):
        """
        Sends a signal to remove the Accuracy GUI from 'toon'

        :param toon: The Toon to remove the GUI from
        """
        if not toon:
            return

        from toontown.toon.gui.DebugGagAccuracyGUI import AccuracyInfo
        accInfo = AccuracyInfo()
        accGUIInfo = ['delete', *accInfo.toStruct()]
        toon.d_debugGagAccuracy(accGUIInfo)

    def cleanupAllAccuracyGUIs(self):
        """
        Sends the 'Remove Accuracy GUI' signal to all Toons in the current battle
        """
        for avId in self.toons:
            toon = self.getToon(avId)
            self.removeAccuracyGUI(toon)

