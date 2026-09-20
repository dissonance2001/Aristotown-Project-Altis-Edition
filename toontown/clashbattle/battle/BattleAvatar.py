from typing import TYPE_CHECKING, List

from direct.showbase.MessengerGlobal import messenger

from toontown.clashbattle.battle.BattleEventGlobals import BEG
from toontown.clashbattle.battle.BattleGlobals import BattleOrderPriority, BattleStateEnum
from toontown.clashbattle.battle.BattleListenerObject import BattleListenerObject
from toontown.clashbattle.battle.statuses import StatusEffectGlobals as SEG
from toontown.clashbattle.battle.statuses import StatusEffects
from toontown.clashbattle.battle.statuses.StatusEffectDefinitions import StatusEffectDefinitions, DEBUFF
from toontown.clashbattle.battle.statuses.StatusEffectGlobals import StatusEffectId2Type
from toontown.clashbattle.battle.statuses.StatusEffects import *
from toontown.clashbattle.battle.statuses.StatusEffects import (OverrideAddedStatusEffect,
                                                    StatusEffectStruct)
from toontown.clashbattle.battle.visuals import VisualEffectGlobals as VEG
from toontown.clashbattle.battle.visuals.VisualEffectEnums import VisualEffectEnum
from toontown.clashbattle.battle.visuals.VisualEffects import (VisualEffectBase,
                                                   VisualEffectStruct,
                                                   debugSuitVisualEffectEnums)
from toontown.clashbattle.battle.statuses.StatusEffectsBase import StatusEffectBase
from toontown.toonbase import ProcessGlobals
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory

if TYPE_CHECKING:
    from toontown.clashbattle.battle.BattleListenerAI import BattleListenerAI


@DirectNotifyCategory()
class BattleAvatar(AstronStruct, BattleListenerObject):
    """
    Creates an instance of a BattleAvatar.

    A BattleAvatar is a representation of some avatar in a battle.
    Information about this avatar is stored, along with their status
    and visual effects, all to be used in battle calculations and
    distributed from the server to the clients for the battle GUI.
    """

    def __init__(self) -> None:
        """
        Creates a new instance of a BattleAvatar.
        """
        self.battle = None
        self.battleListener = None  # type: BattleListenerAI
        self.statusEffects = []  # type: List[StatusEffectBase]
        self.visualEffects = []  # type: List[VisualEffectBase]
        self.battlePlacement = BattleOrderPriority.NEUTRAL

        self.hasCleanedUpBattle = False
        self.setBattleState(BattleStateEnum.INACTIVE)

    def resetBattle(self) -> None:
        self.battle = None
        self.battleListener = None  # type: BattleListenerAI
        self.hasCleanedUpBattle = False

    def cleanupBattle(self) -> None:
        """
        Cleans up this BattleAvatar.
        Can be called on either server or client.
        :return: None.
        """

        # We let the client decide to clean up multiple times if they want to, just to be sure
        # that stuff is really gone
        # The server is more sure of what's happening and does not get that luxury.
        if self.isServerSided() and self.hasCleanedUpBattle:
            return
        self.hasCleanedUpBattle = True

        if self.isServerSided():
            # Delete all status effects and rid them permanently.
            for statusEffect in self.statusEffects[:]:
                self.deleteStatusEffect(statusEffect)
            self.battleListener = None
        elif self.isClientSided():
            # Requests to unapply all visual effects are handled upon cleanup.
            pass

        # Generic cleanup of visual effects.
        for ve in self.getVisualEffects():
            ve: VisualEffectBase
            ve.cleanup()

        self.visualEffects = []
        self.statusEffects = []
        self.battle = None
    
    def getBattleListener(self):
        return self.battleListener
    
    """
    Battle state
    """

    def setBattleState(self, battleState: BattleStateEnum) -> None:
        self.battleState = battleState
        if self.isServerSided() and self.battle and self.battleState == BattleStateEnum.ACTIVE:
            self.battle.accept(self.getZoneChangeEvent(), self.battle.handleZoneChange, extraArgs=[self.doId])

    def getBattleState(self) -> BattleStateEnum:
        return self.battleState
    
    """
    Battle order priority
    """

    def setBattleOrderPriority(self, battlePlacement: BattleOrderPriority) -> None:
        self.battlePlacement = battlePlacement
    
    def getBattleOrderPriority(self) -> BattleOrderPriority:
        return self.battlePlacement

    """
    BattleAvatar Initialization
    """

    def setBattle(self, battle) -> None:
        self.battle = battle

    def setBattleListener(self, battleListener) -> None:
        """
        Sets the battle listener on a BattleAvatar.
        MUST BE SERVER-SIDED.
        """
        self.battleListener = battleListener

    """
    BattleAv Struct Building
    """

    def toStruct(self) -> list:
        # Update our status effects.
        rawStatusEffects = []
        for statusEffect in self.statusEffects:
            statusEffect: StatusEffectBase
            if not statusEffect.wantShow:
                continue
            rawStatusEffects.append(
                StatusEffectStruct(statusEffect.effectId, statusEffect.rounds,
                                   statusEffect.disabledRounds, statusEffect.getTranslatedExtraArgs()))
        # Update our visual effects.
        rawVisualEffects = []
        for visualEffect in self.visualEffects:
            visualEffect: VisualEffectBase
            rawVisualEffects.append(
                VisualEffectStruct(visualEffect.effectEnum, visualEffect.extraArgs)
            )
        # Add debug visual effects.
        for ves in debugSuitVisualEffectEnums:
            # worry not, this list is always empty if __debug__ isn't active
            if ves not in rawVisualEffects:
                rawVisualEffects.append(ves)
        # Return struct.
        return (
            StatusEffectStruct.toStructList(rawStatusEffects),
            VisualEffectStruct.toStructList(rawVisualEffects),
        )

    @classmethod
    def fromStruct(cls, struct: list):
        """Converts a struct into an AstronStruct subclass."""
        _, rawStatusEffects, rawVisualEffects = struct
        # We don't care about setting avId, since it's the responsibility
        # of whoever is creating this BattleAvatar to setAv directly.
        avatarObject = cls()
        avatarObject.__setRawStatusEffects(rawStatusEffects)
        avatarObject.__setRawVisualEffects(rawVisualEffects)
        return avatarObject

    def __setRawStatusEffects(self, statusEffectStructs: list):
        """Sets the effects of this BattleAvatar from struct data."""
        self.statusEffects = []
        for ses in StatusEffectStruct.fromStructList(statusEffectStructs):
            newEffect = SEG.createStatusEffect(self, ses.effectId, ses.extraArgs)
            # No adjust so that it does not include the +1 rounds used on the server.
            newEffect.setRounds(ses.rounds, adjust=False)
            # Similar philosophy here; we need to make sure the "do this round" bit gets shown on the client.
            newEffect.setDisabledRounds(ses.disabledRounds, doThisRound=True)
            self.statusEffects.append(newEffect)

    def __setRawVisualEffects(self, visualEffectStructs: list):
        """Sets the effects of this BattleAvatar from struct data."""
        self.visualEffects = [
            VEG.createVisualEffect(self, ves.effectEnum, ves.extraArgs)
            for ves in VisualEffectStruct.fromStructList(visualEffectStructs)
        ]

    """
    Distributed methods
    """
    
    def sendStatusEffects(self) -> None:
        """Send the current status and visual effects applied onto the avatar
        to the client.
        """
        if not getattr(self, "doId", None):
            raise Exception("Called distributed method sendStatusEffects on an undistributed object!")
        self.sendUpdate("setRawStatusEffects", [*self.toStruct()])
    
    def setRawStatusEffects(self, statusEffectStructs, visualEffectStructs) -> None:
        self.cleanupAllVisualEffects()

        self.__setRawStatusEffects(statusEffectStructs)
        self.__setRawVisualEffects(visualEffectStructs)

        self.reassessVisualEffects()
        self.requestApplyAllVisualEffects()

        messenger.send(self.uniqueName("avatarUpdated"))

    """
    All things Status Effects
    """

    def getStatusEffects(self):
        return self.statusEffects

    def getVisibleStatusEffects(self):
        # Returns all status effects that are marked 'Visible'.
        visibleEffects = [
            statusEffect for statusEffect in self.statusEffects
            if StatusEffectDefinitions[statusEffect.effectId].visible and statusEffect.isVisible()
        ]

        # Sort the visual effects by visual sort order.
        return sorted(
            visibleEffects,
            key=lambda effect: -effect.getVisualSortOrder(),
        )

    def setStatusEffects(self, statusEffects) -> None:
        self.statusEffects = statusEffects  # type: List[StatusEffectBase]
        self.reassessVisualEffects()

    def addStatusEffect(self, effectId: int,
                        newStatusEffect: StatusEffectBase = None,
                        extraArgs: list=None):
        """
        Adds a StatusEffectID to this avatar.

        :param effectId: The ID to create a StatusEffect from.
        :param newStatusEffect: Overrides effectId with a StatusEffect class.
        :return: Returns the added effect, along with a flag if it combined.
        """
        hasOverrideEffects = self.getStatusEffectsOfType(OverrideAddedStatusEffect)
        if self.battleListener and hasOverrideEffects:
            # We have potential remappings to check out.
            for overrideEffect in hasOverrideEffects:
                # Check all of our remap effects, and see if there's one to use.
                newEffectId, newArgs = overrideEffect.checkStatusEffectForReplacementMap(effectId, newStatusEffect)
                if newEffectId is not None:
                    # There is a new status effect we can and should use instead. Use it.
                    newStatusEffect = SEG.createStatusEffect(self, newEffectId, extraArgs=newArgs)
                    # Don't check any other mappings.
                    break

        if not newStatusEffect:
            # Create a status effect of the effectId given
            newStatusEffect = SEG.createStatusEffect(self, effectId, extraArgs)

        # If the effect exists already and it has the combine flag set true, then combine it.
        # If it either doesn't exist yet or has combine set to False, then append it to our status effects.
        combined = False
        existingEffect = None
        existingEffects = self.getStatusEffectsOfId(effectId)
        for existingEffect in existingEffects:
            if existingEffect and existingEffect.wantCombine(newStatusEffect):
                combined = True
                existingEffect.combine(newStatusEffect)
                break

        if not combined:
            self.statusEffects.append(newStatusEffect)
            self.reassessVisualEffects()

        # AI Only
        if self.battleListener:
            if combined:
                self.sendEvent(BEG.EVENT_STATUS_EFFECT_COMBINED, [self, existingEffect, effectId])
                del newStatusEffect
                return existingEffect, combined
            else:
                from toontown.clashbattle.battle.BattleEventDefinitionClasses import StatusEffectEventDefinition
                self.addListenerObject(newStatusEffect, StatusEffectEventDefinition)
                self.sendEvent(BEG.EVENT_STATUS_EFFECT_CREATED, [self, newStatusEffect, effectId])

        if combined:
            return existingEffect, combined
        else:
            return newStatusEffect, combined

    def deleteStatusEffect(self, statusEffect: StatusEffectBase) -> None:
        if statusEffect not in self.statusEffects:
            self.notify.warning(f'Tried to delete status effect not in statusEffects.'
                                f'how did this status effect even get here? {statusEffect}')
            return

        self.statusEffects.remove(statusEffect)

        if self.isServerSided() and self.hasBattleListener():
            # Clear status effect from the battle listener.
            self.removeListenerObject(statusEffect)
            self.sendEvent(BEG.EVENT_STATUS_EFFECT_EXPIRED, [self, statusEffect.getEffectId()])

        statusEffect.cleanup()

        self.reassessVisualEffects()

        del statusEffect

    def deleteStatusEffectOfId(self, effectId: int) -> None:
        effect = self.getStatusEffectOfId(effectId)
        if effect:
            self.deleteStatusEffect(effect)

    def removeStatusEffectOfId(self, effectId: int) -> None:
        self.deleteStatusEffectOfId(effectId)

    def clearStatusEffectsOfQuality(self, quality=DEBUFF, exceptions=None):
        exceptions = exceptions or []
        if type(exceptions) not in (list, tuple, set):
            exceptions = [exceptions]
        statusEffects = [effect for effect in self.statusEffects if StatusEffectId2Type[effect.effectId] == quality]
        for effect in statusEffects[:]:
            if effect.effectId in exceptions:
                continue
            # Effects are automatically removed from self.statusEffects on deletion
            effect.delete()
        self.setStatusEffects(self.statusEffects)

    def clearStatusEffects(self) -> None:
        statusEffects = self.statusEffects[:]
        for effect in statusEffects:
            effect.delete()
        self.setStatusEffects([])

    def getStatusEffectOfId(self, effectId: int):
        for statusEffect in self.statusEffects:
            if statusEffect.getEffectId() == effectId:
                return statusEffect

        return None

    def getStatusEffectsOfId(self, effectId: int) -> list:
        effectsOfType = []
        for statusEffect in self.statusEffects:
            if statusEffect.getEffectId() == effectId:
                effectsOfType.append(statusEffect)
        return effectsOfType

    def removeStatusEffectOfType(self, effectClass) -> None:
        effect = self.getStatusEffectOfType(effectClass)
        if effect:
            self.deleteStatusEffect(effect)

    def hasStatusEffectOfId(self, effectId: int):
        return bool(self.getStatusEffectOfId(effectId))

    def getStatusEffectOfType(self, effectClass):
        """
        Returns first status effect of the given class.
        """
        for effect in self.statusEffects:
            if isinstance(effect, effectClass):
                return effect
        return None

    def getStatusEffectsOfType(self, effectClass):
        """
        Returns all status effects on avatar that subclass the given class.
        """
        effectsOfType = []
        for effect in self.statusEffects:
            if isinstance(effect, effectClass):
                effectsOfType.append(effect)
        return effectsOfType

    def getStatusEffectsOfSpecificType(self, effectClass):
        return [effect for effect in self.statusEffects if effect.__class__ == effectClass]

    """
    Updating Visual Effect Appearances on Client
    """

    def reapplyAllVisualEffects(self):
        """
        Reapplies all visual effects.
        Request unapplies them all in reverse priority (high to low), then requests
        them all to be applied again in priority order (low to high).
        """
        self.requestUnapplyAllVisualEffects()
        self.requestApplyAllVisualEffects()

    def requestUnapplyAllVisualEffects(self):
        """
        Requests all visual effects to be unapplied.
        """
        for visualEffect in self.getVisualEffects()[::-1]:
            visualEffect.requestUnapply()

    def requestApplyAllVisualEffects(self):
        """
        Requests all visual effects to be unapplied.
        """
        for visualEffect in self.getVisualEffects():
            visualEffect.requestApply()

    def requestUnapplyVisualEffect(self, effectEnum: VisualEffectEnum, wantApplyLock: bool = False) -> bool:
        """Requests a visual effect to get unapplied."""
        ve = self.getVisualEffectOfId(effectEnum)
        if not ve:
            return False
        ve.requestUnapply(wantApplyLock)
        return True

    def cleanupAllVisualEffects(self):
        """
        Cleans up all visual effects.
        """
        for visualEffect in self.getVisualEffects()[::-1]:
            visualEffect.cleanup()

    """
    Visual Effects in general
    """

    def getVisualEffects(self):
        self.visualEffects.sort(key=lambda ve: ve.priority)
        return self.visualEffects

    def addVisualEffect(self, effectEnum, extraArgs=None):
        if self.hasCleanedUpBattle:
            # no.
            return

        # Do we have an overrider effect?
        hasOverrideEffects = self.getStatusEffectsOfType(OverrideAddedStatusEffect)
        if hasOverrideEffects:
            # We have potential remappings to check out.
            for overrideEffect in hasOverrideEffects:
                # Check all of our remap effects, and see if there's one to use.
                newEffectEnum, newArgs = overrideEffect.checkVisualEffectForReplacementMap(effectEnum, extraArgs)
                if newEffectEnum is not None:
                    # There is a new visual effect we can and should use instead. Use it.
                    effectEnum = newEffectEnum
                    extraArgs = newArgs
                    # Don't check any other mappings.
                    break

        # Let's go ahead and create the new effect.
        newVisualEffect = VEG.createVisualEffect(self, effectEnum, extraArgs)

        # Let's compare it to the effects that we currently have.
        # Assume that we won't be doing any combination.
        attemptedCombine = False
        existingEffect = None
        existingEffects = self.getVisualEffectsOfId(effectEnum)
        for existingEffect in existingEffects:
            if existingEffect:
                attemptedCombine = True
                if existingEffect.wantCombine(newVisualEffect) and existingEffect is not newVisualEffect:
                    existingEffect.combine(newVisualEffect)
                    self.sendEvent(BEG.EVENT_VISUAL_EFFECT_COMBINED, [self, existingEffect, effectEnum])
                    break

        # If we attempted to combine whatsoever, we're done here.
        if attemptedCombine:
            newVisualEffect.cleanup(tellClientToExpire=False)  # This effect isn't even being applied -- no need to expire.
            return existingEffect

        # Do we have the dependencies needed to apply the effect?
        if newVisualEffect.missingStatusEffectDependencies() and self.isServerSided():
            newVisualEffect.cleanup(tellClientToExpire=False)  # This effect isn't even being applied -- no need to expire.
            return None  # guess not

        # Otherwise, this is a new, brilliant visual effect to extend.
        self.visualEffects.append(newVisualEffect)
        self.sendEvent(BEG.EVENT_VISUAL_EFFECT_CREATED, [self, newVisualEffect, effectEnum])
        return newVisualEffect

    def getVisualEffectOfId(self, effectEnum: VisualEffectEnum):
        for visualEffect in self.visualEffects:
            if visualEffect.effectEnum == effectEnum:
                return visualEffect
        return None

    def getVisualEffectsOfId(self, effectEnum: VisualEffectEnum):
        effectsOfType = []
        for visualEffect in self.visualEffects:
            if visualEffect.effectEnum == effectEnum:
                effectsOfType.append(visualEffect)
        return effectsOfType

    def removeVisualEffect(self, visualEffect: VisualEffectBase, tellClientToExpire: bool = True) -> bool:
        """Removes the visual effect on this profile."""
        if visualEffect in self.visualEffects:
            self.visualEffects.remove(visualEffect)
            visualEffect.cleanup(tellClientToExpire=tellClientToExpire)
            return True
        else:
            return False

    def removeVisualEffectOfId(self, effectEnum: VisualEffectEnum) -> bool:
        """Removes a visual effect of a given id."""
        ve = self.getVisualEffectOfId(effectEnum)
        if not ve:
            return False
        return self.removeVisualEffect(ve)

    def removeVisualEffectsOfId(self, effectEnum: VisualEffectEnum) -> None:
        """Removes a visual effect of a given id."""
        for ve in self.getVisualEffectsOfId(effectEnum):
            self.removeVisualEffect(ve)

    def reassessVisualEffects(self) -> bool:
        """
        Iterates over each visual effect, and cleans up any unnecessary ones.
        Only really called on the server.
        :return: None.
        """
        # Clean up any visual effects that may no longer have an attached status effect.
        newVisualEffectList = self.visualEffects[:]
        for visualEffect in self.visualEffects:
            if visualEffect.missingStatusEffectDependencies():
                newVisualEffectList.remove(visualEffect)
                visualEffect.cleanup()
        self.visualEffects = newVisualEffectList

        # Ensure each status effect has a visual effect it desires.
        for statusEffect in self.statusEffects:
            for enum in statusEffect.visualEffectEnums + \
                        StatusEffectDefinitions[statusEffect.effectId].getVisualEffectEnums():
                if not self.getVisualEffectOfId(enum):
                    self.addVisualEffect(enum, extraArgs=statusEffect.getTranslatedExtraArgs())

        # Everything should be gucci.
        return True

    """
    Movie Functionality
    """

    def neutralAvatar(self):
        """
        Tells our Avatar to loop neutral.
        Client-sided.
        """
        for ve in self.getVisualEffects()[::-1]:
            # Check with all of our visual effects in priority order,
            # and see if any of them happens to override neutral.
            if ve.overridesNeutral:
                return ve.handleNeutral()
        self.loop('neutral')  # Otherwise, do the generic one.

    def getAnim(self, animationKey, *ignoreEnums):
        """
        Checks to see if the given animation is being overridden by a visual effect, otherwise returns the input.
        Client-sided.
        """
        for ve in self.getVisualEffects()[::-1]:
            if ve.effectEnum in ignoreEnums:
                # Ignore certain visual effect enums if we don't care about them
                # Namely, currently used to ignore lure for attack seqs
                continue
            # Check with all of our visual effects in priority order,
            # and see if any of them happens to override the given animation.
            if animationKey in ve.animationOverrides:
                return ve.animationOverrides[animationKey]
        return animationKey

    def getHpTextOverride(self, *args, **kwargs):
        """
        Checks to see if the given hp text func is being overriden by a visual effect.
        Client-sided.
        """
        for ve in self.getVisualEffects()[::-1]:
            result = ve.doHpTextOverride(*args, **kwargs)
            if result:
                return result
        return False

    """
    Various properties
    """

    @staticmethod
    def isClientSided() -> bool:
        return ProcessGlobals.getCurrentProcess() == ProcessGlobals.Process.Client

    @staticmethod
    def isServerSided() -> bool:
        return not BattleAvatar.isClientSided()
    
    def canBeAttacked(self) -> bool:
        return self.getHp() > 0 and not bool(self.getStatusEffectOfType(StatusEffects.UntouchableStatusEffect))

    def isToon(self) -> bool:
        if self.isServerSided():
            from toontown.toon.DistributedToonAI import DistributedToonAI
            return isinstance(self, DistributedToonAI)
        else:
            from toontown.toon.DistributedToon import DistributedToon
            return isinstance(self, DistributedToon)

    def isSuit(self) -> bool:
        if self.isServerSided():
            from toontown.clashsuit.suit.DistributedSuitAI import DistributedSuitAI
            return isinstance(self, DistributedSuitAI)
        else:
            from toontown.clashsuit.suit.DistributedSuit import DistributedSuit
            return isinstance(self, DistributedSuit)
