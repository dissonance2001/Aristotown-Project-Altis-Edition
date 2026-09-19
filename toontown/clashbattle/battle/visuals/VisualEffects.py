import builtins
import itertools
from typing import Optional

from direct.interval.IntervalGlobal import *
from direct.showbase.DirectObject import DirectObject
from direct.showbase.MessengerGlobal import messenger
from direct.showbase.PythonUtil import lerp
from direct.showutil.Rope import Rope
from direct.task.TaskManagerGlobal import taskMgr

from toontown.battle import BattleGlobals
from toontown.battle.BattleBase import *
from toontown.battle.movielistener.BattleMovieListenerEnum import BMLE
from toontown.battle.statuses.StatusEffectEnums import *
from toontown.battle.statuses.StatusEffects import StatusEffectBase, IgnoreVisualEffectMovieUnapplyEffect
from toontown.battle.visuals.VisualEffectEnums import VisualEffectEnum
from toontown.cutscene.repository.CutsceneKeyEnum import CutsceneKeyEnum
from toontown.effects import DustCloud
from toontown.inventory.base.InventoryItem import InventoryItem
from toontown.inventory.enums.ItemEnums import HatItemType
from toontown.suit.SuitDNA import getSuitBodyType
from toontown.toon import ToonDNA
from toontown.toonbase import ToontownGlobals
from toontown.utils.AstronStruct import AstronStruct

# from typing import TYPE_CHECKING, Tuple

# if TYPE_CHECKING:
#     from toontown.battle.BattleAvatar import BattleAvatar


IGNORE = 0
WANT_ONE = 1
WANT_ALL = 2


class VisualEffectStruct(AstronStruct):

    def __init__(self, effectEnum, extraArgs):
        self.effectEnum = effectEnum  # type: VisualEffectEnum
        self.extraArgs = extraArgs

    def toStruct(self) -> list:
        return [self.effectEnum.value, self.extraArgs]

    @classmethod
    def fromStruct(cls, struct: list):
        effectEnum, extraArgs = struct
        return cls(VisualEffectEnum(effectEnum), extraArgs)


class VisualEffectRemoved(AstronStruct):

    def __init__(self, avId, effectEnum):
        self.avId = avId
        self.effectEnum = effectEnum

    def __eq__(self, other):
        return (self.avId == other.avId) and (self.effectEnum == other.effectEnum)

    def toStruct(self) -> list:
        return [self.avId, self.effectEnum.value]

    @classmethod
    def fromStruct(cls, struct: list):
        avId, effectEnum = struct
        return cls(avId, VisualEffectEnum(effectEnum))


"""
Visual Effect Base Classes
"""


class VisualEffectBase(DirectObject):
    """
    The base class for all Visual Effects.
    """

    alwaysRemoveDuringMovie = False  # Should this effect always be removed during the movie?

    def __init__(self, avProfile, effectEnum, extraArgs) -> None:
        """Attributes to set on load."""
        self.avProfile = avProfile      # type: 'BattleAvatar'
        self.effectEnum = effectEnum    # type: VisualEffectEnum
        self.extraArgs = extraArgs      # type: list

        # Attributes which can be defined by subclasses.
        self.associatedStatusEffectIds = []     # What status effect IDs is this associated with?
                                                # (If this status effect ID weren't to exist on the battle profile,
                                                # then should this visual effect clean up?)
        self.statusEffectMode = IGNORE          # IGNORE = Ignores the status effect list.
                                                # WANT_ONE = Requires one ID from the list to keep the visual effect.
                                                # WANT_ALL = Requires all IDs present to maintain the visual effect.
        self.applyDuringMovie = False           # Does this effect get applied during the battle movie?
        self.removeDuringMovie = False          # Should this effect get cleaned up after all attacks?
        self.priority = 0                       # Priority determines render/cleanup order.
                                                # Higher priority: Cleans up first, applies effect last.
                                                # Lower priority: Cleans up last, applies effect first.
        self.overridesNeutral = False           # Does this VE affect an Avatar's neutral anim? (Affected by priority)
        self.animationOverrides = {}            # Which animations does this visual effect override? (Affected by priority)
                                                # type: dict[string, string]
                                                # example: {'neutral', 'rolled'} replaces 'neutral' with 'rolled'.
                                                # todo: apply this to all battle avatar animations as needed.
                                                # current functionality:
                                                # all loop calls
        self.neutralHeadAnim = None             # Replaces their head animation with the given animation
        self.animBlendNeutralData = None        # How long, if an override anim is set, to blend to/from neutral
        self.wantBeginAttackNeutral = None      # Does the suit want the neutral at the beginning of attacks
        self.wantEndAttackNeutral = None        # Does the suit want the neutral at the end of attacks

        # Values that can be set from the visual effect.
        self.lockApply = False      # Prevent application of the visual effect.
        self.lockUnapply = False    # Prevent unapplication of the visual effect.

        # Effects related to the effect itself. Don't adjust these.
        self.hasApplied = False
        self.hasCleanedUp = False
        self.wantReapply = False
        self.preventClear = False

    def cleanup(self, tellClientToExpire=True) -> None:
        # Cleans up this visual effect object.
        if self.hasCleanedUp:
            return

        self.ignoreAll()

        # Make sure we unapply the effect on the client.
        if self.avProfile.isClientSided():
            self._unapplyEffect()
        self.hasCleanedUp = True

        # If we're on the server... my dying wish...
        # ...tell DistributedBattleBaseAI that we've been removed...
        if self.avProfile.isServerSided() and tellClientToExpire and self.shouldAddExpired() and self.battle:
            self.avProfile.battle.addExpiredVisualEffect(self)
        self.avProfile = None

    def shouldAddExpired(self):
        """Check whether or not this effect should add itself to the expired list for the client."""
        return not self.av.getStatusEffectOfType(IgnoreVisualEffectMovieUnapplyEffect)

    """
    Part functions
    """

    def getHead(self):
        return self.av.getHeadParts()[0]

    def getLeftHand(self):
        return self.av.getLeftHand()

    def getRightHand(self):
        return self.av.getRightHand()

    """
    Access functions
    """

    def requestApply(self) -> None:
        # Requests this visual effect to apply.
        self._applyEffect()

    def requestUnapply(self, wantApplyLock: bool = False) -> None:
        # Requests this visual effect to unapply.
        self._unapplyEffect()
        if wantApplyLock:
            self.setApplyLock(True)

    def getApplyMovie(self):
        # Gets the battle movie sequence which applies this effect.
        if not self.applyDuringMovie or self.hasApplied or not self.av or self.avProfile.getHp() <= 0:
            return Sequence(), Sequence()
        applySeq, cameraSeq = self._doApplyMovie()
        return Sequence(applySeq, Func(self.setAppliedState, True)), cameraSeq

    def getUnapplyMovie(self):
        # Gets the battle movie sequence which removes this effect.
        # - Must be able to remove during the movie.
        # - Must be currently applied OR must force remove it regardless,
        # - Avatar must exist and be alive.
        if not self.removeDuringMovie:
            return Sequence(), Sequence()
        if not self.av or self.avProfile.getHp() <= 0:
            return Sequence(), Sequence()
        if not self.alwaysRemoveDuringMovie:
            if not self.hasApplied:
                return Sequence(), Sequence()
        unapplySeq, cameraSeq = self._doUnapplyMovie()
        return Sequence(unapplySeq, Func(self.setAppliedState, False)), cameraSeq

    def setAppliedState(self, state: bool):
        """Sets the state of self.hasApplied."""
        self.hasApplied = state

    """
    Combination logic
    """

    def wantCombine(self, otherEffect) -> bool:
        """Does this effect want to combine with an other effect?"""
        return False

    def combine(self, otherEffect) -> None:
        """If so, functionality goes here."""
        self.wantReapply = True

    """
    Visual Effect Apply Medium
    """

    def _applyEffect(self) -> None:
        # Applies the visual effect.
        if self.lockApply:
            return
        if self.hasCleanedUp:
            return
        if self.hasApplied or self.wantReapply:
            self._unapplyEffect()
            self.wantReapply = False
        self.hasApplied = True
        if self.client and self.avProfile is not None:
            self._doApply()

    def _unapplyEffect(self) -> None:
        # Unapplies the visual effect.
        if self.lockUnapply:
            return
        if not self.hasApplied:
            return
        self.hasApplied = False
        if self.client and self.avProfile is not None:
            self._doUnapply()

    """
    Visual Effect Actual Application
    """

    def _doApply(self) -> None:
        """Applies the visual effect to the avatar."""
        raise NotImplementedError

    def _doUnapply(self) -> None:
        """Unapplies the visual effect from the avatar."""
        raise NotImplementedError

    """
    Locks
    """

    def setApplyLock(self, mode: bool):
        """Sets the apply lock."""
        self.lockApply = mode

    def setUnapplyLock(self, mode: bool):
        """Sets the unapply lock."""
        self.lockUnapply = mode

    """
    Movie-Related Functions
    """

    def onMovieAdd(self, extraArgs: list):
        """
        This method gets called when the VisualEffect is applied during a movie.

        :return: None.
        """
        pass

    def _doApplyMovie(self):
        """
        Returns a sequence where this visual effect gets applied.
        To be played during the Battle Movie, if
        the self.applyDuringMovie is set to be True.
        """
        if not self.battle:
            return Sequence(), Sequence()
        appSeq = Sequence(Func(self._doApply))
        camSeq = self.avProfile.battle.camera.allGroupOverheadShot(duration=80.0 / 24.0)
        return appSeq, camSeq

    def _doUnapplyMovie(self):
        """
        Returns a sequence where this visual effect gets unapplied.
        To be played during the Battle Movie, if
        the self.removeDuringMovie is set to be True.
        """
        if not self.battle:
            return Sequence(), Sequence()
        appSeq = Sequence(Func(self._doUnapply))
        camSeq = self.avProfile.battle.camera.allGroupOverheadShot(duration=80.0 / 24.0)
        return appSeq, camSeq

    def onSuitAttackBegin(self):
        """
        Do whatever you want when a suit attack begins here.
        """
        return

    def onSuitAttackEnd(self):
        """
        Do whatever you want when a suit attack ends here.
        """
        return

    def doHpTextOverride(self, *args, **kwargs):
        # Certain visual effects may want to override the hp text of a cog.
        # We can go ahead and handle that here in subclasses.
        return

    def getPreAttackSequence(self):
        # Certain visual effects can return a sequence that the cog should do before an attack animation plays
        return None

    def getPostAttackSequence(self):
        # Certain visual effects can return a sequence that the cog should do after an attack animation plays
        return None

    """
    Other timing methods
    """

    def roundStart(self):
        """
        This method is always called at the start of a battle round.
        :return: None.
        """
        pass

    """
    Logic for this Visual Effect
    """

    def requestDestroy(self) -> bool:
        """
        Requests this visual effect to destroy.
        This is called on the AI after the battle rounds are
        calculated, in order to determine if this effect
        needs to get destroyed.
        """
        if self.missingStatusEffectDependencies():
            self.forceDestroy()
            return True
        return False

    def forceDestroy(self):
        """
        Causes this visual effect to be removed,
        effective immediately.
        """
        self.avProfile.removeVisualEffect(self)
        self.cleanup()

    def missingStatusEffectDependencies(self):
        """
        Is this visual effect missing the status
        effects of which it depends on?
        """
        if self.statusEffectMode == IGNORE:
            return False  # nah, we're fine.
        if self.preventClear:
            return False  # we're protected
        listedIds = []
        for statusEffect in self.avProfile.getStatusEffects():
            statusEffect: StatusEffectBase
            listedIds.append(statusEffect.effectId)
        # Do logic depending on what mode we have set.
        if self.statusEffectMode == WANT_ONE:
            for requiredId in self.associatedStatusEffectIds:
                if requiredId in listedIds:
                    return False  # nope, we got what we're looking for
            return True  # we are missing a status effect dependency
        elif self.statusEffectMode == WANT_ALL:
            for requiredId in self.associatedStatusEffectIds:
                if requiredId not in listedIds:
                    return True  # we missed a crucial status effect
            return False  # we have them all
        else:
            raise AttributeError("VisualEffect defined with inappropriate statusEffectMode.")

    """
    Various properties and helper methods
    """

    def refreshAvatarVisualEffects(self):
        """
        Refreshes the visual effects on the battle avatar.

        Useful for unapply movies to ensure the visual effect is cleaned up properly.

        Be sure NOT to put this in any unapply or apply functions,
        lest you cause an infinite loop!
        """
        self.avProfile.reapplyAllVisualEffects()

    def preventRemoval(self) -> None:
        """
        On the Client, this will prevent the visual effect
        from being removed for only this turn.

        On the AI, this does nothing.
        """
        self.preventClear = True

    def handleNeutral(self) -> None:
        """
        This gets called on a visual effect when it
        affects how its target handles a neutral animation.
        This is off by default (see self.overridesNeutral)
        """
        self.av.loop('neutral')

    @property
    def client(self):
        """Is this visual effect on the client?"""
        return self.avProfile.isClientSided()

    @property
    def av(self):
        return self.avProfile

    @property
    def battle(self):
        return getattr(self.avProfile, "battle", None)


class BlankVisualEffect(VisualEffectBase):
    """
    A blank visual effect.
    """

    def _doUnapply(self) -> None:
        pass

    def _doApply(self) -> None:
        pass


class ParticleVisualEffect(VisualEffectBase):
    """
    Base class for a single particle effect on an avatar.
    """

    particleName = 'snap'
    cleanup_duration = 3.0
    cleanup_instant = False
    wantEnum = None

    def __init__(self, avProfile, effectEnum, extraArgs) -> None:
        super().__init__(avProfile, effectEnum, extraArgs)
        self.particleSystem = None
        if self.wantEnum:
            self.associatedStatusEffectIds = [self.wantEnum]
            self.statusEffectMode = WANT_ONE

    def getParticleParent(self):
        return self.av

    def getParticleRenderParent(self):
        return self.av

    def _doApply(self) -> None:
        """Applies the visual effect to the avatar."""
        from toontown.battle import BattleParticles
        self.particleSystem = BattleParticles.createParticleEffect(file=self.particleName)
        self.particleSystem.start(parent=self.getParticleParent(), renderParent=self.getParticleRenderParent())

    def _doUnapply(self) -> None:
        """Unapplies the visual effect from the avatar."""
        if self.particleSystem:
            from toontown.battle import BattleParticles
            BattleParticles.cleanupSystem(self.particleSystem,
                                          duration=self.cleanup_duration,
                                          instant=self.cleanup_instant or self.hasCleanedUp)
            self.particleSystem = None


class MultiParticleVisualEffect(ParticleVisualEffect):
    """
    Expanded class for multiple particle effects on an avatar.
    """

    particleNames = ['snap', 'burn']
    cleanup_duration = 3.0
    cleanup_instant = False
    wantEnum = None

    def __init__(self, avProfile, effectEnum, extraArgs) -> None:
        super().__init__(avProfile, effectEnum, extraArgs)
        self.particleSystems = []
        if self.wantEnum:
            self.associatedStatusEffectIds = [self.wantEnum]
            self.statusEffectMode = WANT_ONE

    def getParticleParent(self):
        return self.av

    def _doApply(self) -> None:
        """Applies the visual effect to the avatar."""
        from toontown.battle import BattleParticles
        for particleName in self.particleNames:
            particleSystem = BattleParticles.createParticleEffect(file=particleName)
            particleSystem.start(parent=self.getParticleParent(), renderParent=self.av)
            self.particleSystems.append(particleSystem)

    def _doUnapply(self) -> None:
        """Unapplies the visual effect from the avatar."""
        from toontown.battle import BattleParticles
        for particleSystem in self.particleSystems:
            BattleParticles.cleanupSystem(particleSystem,
                                          duration=self.cleanup_duration,
                                          instant=self.cleanup_instant or self.hasCleanedUp)
        self.particleSystems = []


"""
Visual Effect Debug
"""


debugToonVisualEffectEnums = [
    # VisualEffectStruct(VisualEffectEnum.GAG_DOWN, []),
]
debugSuitVisualEffectEnums = [
    # VisualEffectStruct(VisualEffectEnum.SCAPEGOAT_ENRAGED, []),
]

if not __debug__:
    debugToonVisualEffectEnums = []
    debugSuitVisualEffectEnums = []


"""
Defined Visual Effects
"""


class SuitLuredVisualEffect(VisualEffectBase):
    """
    The visual effect for a Suit being lured.
    """

    alwaysRemoveDuringMovie = True

    def __init__(self, avProfile, effectEnum, extraArgs) -> None:
        super().__init__(avProfile, effectEnum, extraArgs)
        self.associatedStatusEffectIds = [SEE.EFFECT_SUIT_LURED]
        self.animationOverrides = {
            'neutral': 'lured',
        }
        self.neutralHeadAnim = 'neutral-lured'
        self.statusEffectMode = WANT_ONE
        self.applyDuringMovie = False
        self.removeDuringMovie = True
        self.priority = 60

    def _doApply(self) -> None:
        pass

    def _doUnapply(self) -> None:
        pass

    def _doUnapplyMovie(self):
        # Something else has already unlured them, don't do anything
        if not self.av.isLured or not self.battle:
            return Sequence(), Sequence()

        from toontown.battle import MovieLure, MovieUtil
        # This is the end of the round, we need to unlure them ourselves
        seq = Sequence(
            MovieUtil.unlureSuit(self.av, self.battle), 
            MovieLure.createSuitResetPosTrack(self.av, self.battle)
        )
        camSeq = self.avProfile.battle.camera.allGroupOverheadShot(duration=seq.getDuration())
        return seq, camSeq


class AvatarSoakedVisualEffect(ParticleVisualEffect):
    """
    The visual effect for a Suit being soaked.
    """

    tint = (0.75, 0.75, 1.0, 1.0)
    particleName = 'suitSoaked'
    birthRate = 0.5
    cleanup_duration = 1.2

    # some particle defs

    baseXScale = 0.25
    baseYScale = 0.30
    endSizeRatio = 0.5
    suitSizeBaseline = 1.00

    suitARingScale = 1.1
    suitBRingScale = 0.8
    suitCRingScale = 1.4
    suitCSkeletonRingScale = 1.0

    def __init__(self, avProfile, effectEnum, extraArgs) -> None:
        super().__init__(avProfile, effectEnum, extraArgs)
        self.associatedStatusEffectIds = [SEE.EFFECT_SUIT_SOAKED]
        self.statusEffectMode = WANT_ONE
        self.applyDuringMovie = False
        self.removeDuringMovie = True
        self.priority = 45
        self.particleNode = None

    def shouldAddExpired(self):
        """Check whether or not this effect should add itself to the expired list for the client."""
        return VisualEffectBase.shouldAddExpired(self) and not self.av.getStatusEffectOfId(StatusEffectEnum.EFFECT_SUIT_DRENCHED)

    def getParticleParent(self):
        if self.particleNode:
            return self.particleNode

        return self.av

    def _doApply(self) -> None:
        if not self.av.isSkeleton:
            self.particleNode = self.av.find('**/joint_head').attachNewNode('particleNode')
        else:
            actorNode = self.av.find('**/__Actor_modelRoot')
            self.particleNode = actorNode.find('**/joint_head').attachNewNode('particleNode')
        # self.particleNode.setZ(self.av.height * 0.7)
        super()._doApply()

        # scale the particles accordingly
        particles = self.particleSystem.getParticlesList()[0]
        scaleMult = self.av.scale / self.suitSizeBaseline

        particles.setBirthRate(self.birthRate)
        particles.renderer.setInitialXScale(self.baseXScale * scaleMult)
        particles.renderer.setInitialYScale(self.baseYScale * scaleMult)
        particles.renderer.setFinalXScale(self.baseXScale * self.endSizeRatio * scaleMult)
        particles.renderer.setFinalYScale(self.baseYScale * self.endSizeRatio * scaleMult)

        # set the ring scale emitter on the particles
        bodyType = getSuitBodyType(self.av.style.name)
        emitterScaleMult = {
            'a': self.suitARingScale,
            'b': self.suitBRingScale,
            'c': self.suitCRingScale,
        }.get(bodyType)
        if bodyType == 'c' and self.av.isSkeleton:
            emitterScaleMult = self.suitCSkeletonRingScale
        particles.emitter.setRadius(emitterScaleMult)

        # add tints
        self.av.addTint(self.tint)
        self.av.isSoaked = SOAKED
        messenger.send('suitSoaked', [self.av])

    def _doUnapply(self) -> None:
        super()._doUnapply()
        if self.particleNode:
            self.particleNode.removeNode()
            self.particleNode = None
        if self.av:
            self.av.removeTint(self.tint)
            self.av.isSoaked = DRY
        messenger.send('suitUnsoaked', [self.av])

    def _doUnapplyMovie(self):
        if not self.av or not self.battle:
            self.setApplyLock(True)
            return Sequence(), Sequence()

        unsoakTrack = Sequence(
            Parallel(
                Sequence(
                    Wait(1),
                    Func(self._doUnapply),
                    # Lock this effect from being re-applied, then update the avatar's visual effects.
                    Func(self.setApplyLock, True),
                ),
                Sequence(
                    Func(self.av.setPlayRate, self.battle.timescale, 'soak'),
                    Func(self.av.play, 'soak', fromFrame=83, toFrame=163),
                    Wait(self.av.getDuration('soak', fromFrame=83, toFrame=163)),
                    Func(self.av.loop, 'neutral'),
                    Func(self.av.setPlayRate, 1.0, 'soak'),
                )
            )
        )
        unsoakCamTrack = self.avProfile.battle.camera.allGroupOverheadShot(duration=80.0 / 24.0)
        return unsoakTrack, unsoakCamTrack


class AvatarDrenchedVisualEffect(AvatarSoakedVisualEffect):
    """
    The viusal effect for a drenched Suit.
    Similar to soak, but with more particles.
    """
    birthRate = 0.25

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.associatedStatusEffectIds = [SEE.EFFECT_SUIT_DRENCHED]

    def shouldAddExpired(self):
        return VisualEffectBase.shouldAddExpired(self)


class AvatarFrozenVisualEffect(ParticleVisualEffect):
    """
    The visual effect for a Suit being frozen.
    Fairly similar to Soak, but looks slightly different.
    """

    tint = (0.6, 0.851, 1.218, 1.0)
    particleName = 'suitFrozen'
    suitAScale = 1.2
    suitBScale = 0.9
    suitCScale = 1.5

    def __init__(self, avProfile, effectEnum, extraArgs) -> None:
        super().__init__(avProfile, effectEnum, extraArgs)
        self.associatedStatusEffectIds = [SEE.EFFECT_SUIT_FROZEN]
        self.statusEffectMode = WANT_ONE
        self.applyDuringMovie = False
        self.removeDuringMovie = True
        self.priority = 55
        self.particleNode = None

    def getParticleParent(self):
        if self.particleNode:
            return self.particleNode
        return self.av

    def _doApply(self) -> None:
        # create and configure a special node for holding particles
        self.particleNode = self.av.attachNewNode('particleNode')
        self.particleNode.setDepthWrite(False)
        self.particleNode.setBin('fixed', 1)
        self.particleNode.setTransparency(TransparencyAttrib.MDual)
        self.particleNode.setZ(self.av.height * 0.4)
        super()._doApply()

        bodyType = getSuitBodyType(self.av.style.name)
        particleScaling = {
            'a': self.suitAScale,
            'b': self.suitBScale,
            'c': self.suitCScale,
        }.get(bodyType)

        particles = self.particleSystem.getParticlesList()[0]
        particles.emitter.setRadius(particleScaling)
        adjustedScale = particleScaling * self.av.scale

        self.particleNode.setScale(adjustedScale, adjustedScale, self.av.height * 0.3)

        # add tints
        self.av.addTint(self.tint)
        self.av.isSoaked = SOAKED
        messenger.send('suitSoaked', [self.av])

    def _doUnapply(self) -> None:
        super()._doUnapply()
        if self.particleNode:
            self.particleNode.removeNode()
        if self.av:
            self.av.removeTint(self.tint)
            self.av.isSoaked = DRY
        messenger.send('suitUnsoaked', [self.av])

    def _doUnapplyMovie(self):
        if not self.av or not self.battle:
            self.setApplyLock(True)
            return Sequence(), Sequence()

        unsoakTrack = Sequence(
            Parallel(
                Sequence(
                    Wait(1),
                    Func(self._doUnapply),
                    # Lock this effect from being re-applied, then update the avatar's visual effects.
                    Func(self.setApplyLock, True),
                ),
                Sequence(
                    Func(self.av.setPlayRate, self.battle.timescale, 'soak'),
                    Func(self.av.play, 'soak', fromFrame=83, toFrame=163),
                    Wait(self.av.getDuration('soak', fromFrame=83, toFrame=163)),
                    Func(self.av.loop, 'neutral'),
                    Func(self.av.setPlayRate, 1.0, 'soak'),
                )
            )
        )
        unsoakCamTrack = self.avProfile.battle.camera.allGroupOverheadShot(duration=80.0 / 24.0)
        return unsoakTrack, unsoakCamTrack

    def shouldAddExpired(self):
        # don't expire if snow squall is active
        snowSquall = False
        try:
            snowSquall = self.battle.bossCog.inSnowSquall
        except AttributeError:
            pass
        return super().shouldAddExpired() and not snowSquall


class ErfitReviveVisualEffect(VisualEffectBase):
    """
    Erfit gets Very Red upon revive.
    """

    tint = (1, 0.2, 0.2, 1)
    scale = 1.1
    numImages = 3

    def __init__(self, avProfile, effectEnum, extraArgs) -> None:
        super().__init__(avProfile, effectEnum, extraArgs)
        self.priority = 250
        # What will house the stream of fake suits that are copied during the sequence
        self.displayNodes = []
        # The fake suit in question. Will be shuffling out of fake suits over time
        self.displaySuits = [None] * self.numImages
        # The sequence that displays of the fake suit growing/becoming transparent
        self.displaySeqs = []

    def _doApply(self) -> None:
        """Applies the visual effect to the avatar."""
        self.av.getGeomNode().setColorScale(self.tint)
        self.av.addScale(self.scale)

        # Don't do any displaynode stuff if accessibility is active
        if settings['reduce-battle-effects']:
            return

        self.displayNodes = []
        for i in range(self.numImages):
            displayNode = render.attachNewNode(f'{self.av.style.name}-displayNode{i}')
            self.displayNodes.append(displayNode)

        for displayNode in self.displayNodes:
            # Make it support transparency, and colorscale it to orange
            displayNode.setTransparency(1)
            displayNode.setColorScale(1.0, 0.0, 0.0, 0.6)

        def updateDisplaySuit(index=0):
            if index > len(self.displaySuits) - 1:
                return

            if self.displaySuits[index] is not None:
                self.displaySuits[index].removeNode()
            # This is the cleanest solution I could find to get the animation state to transfer.
            self.displaySuits[index] = self.av.getGeomNode().copyTo(self.displayNodes[index])
            for removePart in ('**/joint_attachMeter', '**/to_head', '**/joint_head', '**/joint_shadow'):
                self.displaySuits[index].find(removePart).removeNode()
            self.displayNodes[index].setPos(self.av.getPos(render))
            self.displayNodes[index].setHpr(self.av.getHpr(render))
            self.displayNodes[index].setScale(self.av.getScale(render) * .999)

        # Silhouette sequence that shows it growing and then fading away
        for i in range(self.numImages):
            displaySeq = Sequence(
                Func(updateDisplaySuit, i),
                Func(self.displayNodes[i].setColorScale, (1.0, 0.0, 0.0, 0.6)),
                Parallel(
                    LerpColorScaleInterval(self.displayNodes[i], 0.6, (1.0, 0.0, 0.0, 0.0), blendType='easeOut')
                ),
            )
            displaySeq.loop()
            displaySeq.setT(0.2 * i)
            self.displaySeqs.append(displaySeq)

    def _doUnapply(self) -> None:
        """Unapplies the visual effect from the avatar."""

        self.av.getGeomNode().setColorScale(1, 1, 1, 1)
        self.av.removeScale(self.scale)

        self.stopDisplaySeqs()

    def stopDisplaySeqs(self):
        for displaySeq in self.displaySeqs:
            displaySeq.pause()
        self.displaySeqs = []

        for displayNode in self.displayNodes:
            displayNode.removeNode()
        self.displayNodes = []

        self.displaySuits = [None] * self.numImages

    def getApplyMovie(self):
        if not self.battle:
            return Sequence(), Sequence()
        suit = self.av
        battle = self.avProfile.battle

        suitPos, suitHpr = battle.getActorPosHpr(suit)
        explosionPoint = Point3(suitPos.getX(), suitPos.getY(), suitPos.getZ() + suit.height/3)

        explodeSound = base.loader.loadSfx('phase_3.5/audio/sfx/ENC_cogfall_apart.ogg')
        explodeSoundTrack = Sequence(SoundInterval(explodeSound, volume=1.0))

        from toontown.battle.MovieUtil import createKapowExplosionTrack
        explosionTrack = Sequence()
        explosionTrack.append(createKapowExplosionTrack(battle, explosionPoint=explosionPoint, scale=5))

        erfitSwoleTrack = Parallel(
            Sequence(
                LerpScaleInterval(suit, 0.5, self.scale, blendType='easeIn'),
            )
        )

        erfitSwoleTrack.append(LerpColorScaleInterval(suit.getGeomNode(), 0.5, self.tint, blendType='easeIn'))
        # Make sure the HP meter doesn't inherit the red color
        erfitSwoleTrack.append(Func(suit.healthBar.setColorScaleOff, 1))

        return Parallel(
            Parallel(explodeSoundTrack, explosionTrack, erfitSwoleTrack),
            Sequence(
                Wait(0.55),
                Func(suit.loop, 'neutral'),
            ),
        ), Sequence(Func(base.camera.setPosHpr, suit, 0, 22, 12, 180, -18, 0))


class AfterimageVisualEffect(VisualEffectBase):
    """
    Suit spawns afterimages.
    """

    numImages = 5
    rate = 0.1

    def __init__(self, avProfile, effectEnum, extraArgs) -> None:
        super().__init__(avProfile, effectEnum, extraArgs)
        self.priority = 250
        # What will house the stream of fake suits that are copied during the sequence
        self.displayNodes = []
        # The fake suit in question. Will be shuffling out of fake suits over time
        self.displaySuits = [None] * self.numImages
        # The sequence that displays of the fake suit growing/becoming transparent
        self.displaySeqs = []

    def _doApply(self) -> None:
        """Applies the visual effect to the avatar."""
        # Don't do any displaynode stuff if accessibility is active
        if settings['reduce-battle-effects']:
            return

        self.displayNodes = []
        for i in range(self.numImages):
            displayNode = render.attachNewNode(f'{self.av.style.name}-displayNode{i}')
            self.displayNodes.append(displayNode)

        for displayNode in self.displayNodes:
            # Make it support transparency, and colorscale it to orange
            displayNode.setTransparency(TransparencyAttrib.MDual)
            displayNode.setColorScale(1.0, 1.0, 1.0, 0.6)

        def updateDisplaySuit(index=0):
            if index > len(self.displaySuits) - 1:
                return

            if self.displaySuits[index] is not None:
                self.displaySuits[index].removeNode()
            # This is the cleanest solution I could find to get the animation state to transfer.
            if not self.av.getGeomNode():
                return
            self.displaySuits[index] = self.av.getGeomNode().copyTo(self.displayNodes[index])
            for removePart in ('**/joint_attachMeter', '**/to_head', '**/joint_shadow'):
                self.displaySuits[index].find(removePart).removeNode()
            self.displayNodes[index].setPos(self.av.getPos(render))
            self.displayNodes[index].setHpr(self.av.getHpr(render))
            self.displayNodes[index].setScale(self.av.getScale(render) * .999)

        # Silhouette sequence that shows it growing and then fading away
        for i in range(self.numImages):
            displaySeq = Sequence(
                Func(updateDisplaySuit, i),
                Func(self.displayNodes[i].setColorScale, (1.0, 1.0, 1.0, 0.6)),
                Parallel(
                    LerpColorScaleInterval(self.displayNodes[i], self.numImages * self.rate, (1.0, 1.0, 1.0, 0.0), blendType='easeOut')
                ),
            )
            displaySeq.loop()
            displaySeq.setT(self.rate * i)
            self.displaySeqs.append(displaySeq)

    def _doUnapply(self) -> None:
        """Unapplies the visual effect from the avatar."""
        self.stopDisplaySeqs()

    def stopDisplaySeqs(self):
        for displaySeq in self.displaySeqs:
            displaySeq.pause()
        self.displaySeqs = []

        for displayNode in self.displayNodes:
            displayNode.removeNode()
        self.displayNodes = []

        self.displaySuits = [None] * self.numImages


class AvatarSplatVisualEffect(VisualEffectBase):
    """
    The visual effect for an Avatar receiving pie splat.

    We have to do some overriding of things to make sure we
    apply several splats correctly, and make sure that they
    don't constantly re-update upon battle movie restart.

    And, of course, they don't naturally clean up every round.
    """

    def __init__(self, avProfile, effectEnum, extraArgs) -> None:
        super().__init__(avProfile, effectEnum, extraArgs)
        if self.avProfile.battleListener:
            # The AI just added this status effect.
            # We have the same extraArgs as Marked For Laugh
            # (aka, [damageMult, gagLevel, prestige]),
            # but we just want the gagLevel.
            self.extraArgs = [self.extraArgs[1]]
        self.associatedStatusEffectIds = [SEE.EFFECT_MARKED_FOR_LAUGH]
        self.statusEffectMode = WANT_ONE
        self.applyDuringMovie = False
        self.removeDuringMovie = True
        self.priority = 50

    def wantCombine(self, otherEffect) -> bool:
        """Does this effect want to combine with an other effect?"""
        return True

    def combine(self, otherEffect) -> None:
        """If so, functionality goes here."""
        newSplat = otherEffect.extraArgs[0]
        self.extraArgs.append(newSplat)
        self.hasApplied = False
        self._applyEffect()

    def _doApply(self) -> None:
        while self.av.splatCount < len(self.extraArgs):
            pieIndex = round(self.extraArgs[self.av.splatCount])
            self.av.splatCount += 1
            def partSplat(*partNames):
                if type(partNames) != tuple:
                    partNames = (partNames,)
                for partName in partNames:
                    u = random.random()
                    v = random.random()
                    from toontown.battle import BattleProps
                    pieName = list(BattleProps.Splats.keys())[pieIndex]
                    self.av.applySplat([pieName, partName, u, v])
            try:
                # headPartNames = [part.getName() for part in self.av.getHeadParts()]
                # partSplat(headPartNames)
                partSplat('body')
            except:
                # presumably called when we're dealing with a skelecog
                actorNode = self.av.find('**/__Actor_modelRoot')
                actorCollection = actorNode.findAllMatches('*')
                for thing in actorCollection:
                    if thing.getName() not in (
                    'joint_attachMeter', 'joint_nameTag', 'def_nameTag', 'joint_Rhold', 'joint_Lhold', 'joint_shadow'):
                        partSplat(thing.getName())

    def _unapplyEffect(self) -> None:
        """We override this so that we are in full control of when and how to unapply the splats."""
        return

    def _doUnapply(self) -> None:
        try:
            self.av.clearSplats()
        except AttributeError:  # in case this is an AI object instead
            pass

    def _doUnapplyMovie(self):
        if not self.battle:
            return Sequence(), Sequence()
        unsoakTrack = Sequence(
            Parallel(
                Sequence(
                    Wait(1),
                    Func(self._doUnapply),
                ),
                Sequence(
                    ActorInterval(self.av, 'squirt-small-react', startTime=2.2),
                    Func(self.av.loop, 'neutral')
                )
            )
        )
        unsoakCamTrack = self.avProfile.battle.camera.allGroupOverheadShot(duration=80.0 / 24.0)
        return unsoakTrack, unsoakCamTrack


class SuitSuedVisualEffect(VisualEffectBase):
    """
    The visual effect for a Suit's cease and desist.
    """

    def __init__(self, avProfile, effectEnum, extraArgs) -> None:
        super().__init__(avProfile, effectEnum, extraArgs)
        self.associatedStatusEffectIds = [SEE.EFFECT_SUIT_SUED]
        self.statusEffectMode = WANT_ONE
        self.applyDuringMovie = False
        self.removeDuringMovie = True
        self.suedEffect = None
        self.priority = -10

    def _doApply(self) -> None:
        p1 = Point3(0)
        p2 = Point3(0)
        from toontown.battle.BattleProps import globalPropPool
        stars = globalPropPool.getProp('stun')
        # We must use jpg+rgb here because of the ColorBlendAttrib.MAdd that is applied to skelecogs, which breaks PNG.
        tex = loader.loadTexture(
            'phase_5/maps/battle/ttcc_fx_battleParticles_palette_2.jpg',
            'phase_5/maps/battle/ttcc_fx_battleParticles_palette_2_a.rgb'
        )
        tex.setMinfilter(Texture.FTLinearMipmapLinear)
        tex.setMagfilter(Texture.FTLinear)
        stars.setTexture(tex, 1)
        stars.setScale(1.5)
        stars.setColor(1, 1, 1, 1)
        stars.adjustAllPriorities(100)
        bodyStyle = self.av.style.body
        if self.av.isSkeleton:
            actorNode = self.av.find('**/__Actor_modelRoot')
            head = actorNode.find('**/joint_head')
            zVal = max(0.0, p2[2] + (0.8 if bodyStyle == 'a' else 0))
        else:
            head = self.av.find('**/joint_head')
            zVal = max(0.0, p2[2] + (0.4 if bodyStyle == 'c' else 0.8))
        head.calcTightBounds(p1, p2)
        stars.reparentTo(head)
        stars.setZ(zVal)
        stars.loop('stun')
        stars.setPlayRate(0.75, 'stun')
        self.suedEffect = stars

    def _doUnapply(self) -> None:
        if self.suedEffect is None:
            return
        self.suedEffect.setColor(1, 1, 1, 0)
        self.suedEffect.cleanup()
        self.suedEffect.removeNode()
        self.suedEffect = None

    def _doUnapplyMovie(self):
        if not self.battle:
            return Sequence(), Sequence()

        unsoakTrack = Sequence(
            Parallel(
                Sequence(
                    Wait(1),
                    Func(self._doUnapply),
                    # Lock this effect from being re-applied, then update the avatar's visual effects.
                    Func(self.setApplyLock, True),
                ),
                Sequence(
                    Func(self.av.setPlayRate, self.battle.timescale, 'soak'),
                    Func(self.av.play, 'soak', fromFrame=83, toFrame=163),
                    Wait(self.av.getDuration('soak', fromFrame=83, toFrame=163)),
                    Func(self.av.loop, 'neutral'),
                    Func(self.av.setPlayRate, 1.0, 'soak'),
                )
            )
        )
        unsoakCamTrack = self.avProfile.battle.camera.allGroupOverheadShot(duration=80.0 / 24.0)
        return unsoakTrack, unsoakCamTrack


class SkelecogVisualEffect(VisualEffectBase):
    """
    The visual effect, which guarantees that Suit is a skelecog.
    """

    def __init__(self, avProfile, effectEnum, extraArgs) -> None:
        super().__init__(avProfile, effectEnum, extraArgs)
        self.priority = 30

    def _doApply(self) -> None:
        self.av.setSkelecog(1)

    def _doUnapply(self) -> None:
        """
        Skelecog is a one-way transformation atm.
        """
        pass


class ToonBoostVisualEffect(VisualEffectBase):
    """
    The visual effect for a Toon with a Gag boost.

    extraArgs, by default:
    - [damageMult, gagTrackIndex]
    """
    ParticleScales = {1: 1.05, 2: 0.9, 3: 0.75}  # Based on number of uses

    def __init__(self, avProfile, effectEnum, extraArgs) -> None:
        super().__init__(avProfile, effectEnum, extraArgs)
        self.associatedStatusEffectIds = [SEE.EFFECT_TOON_DAMAGE_UP]
        self.statusEffectMode = WANT_ONE
        self.gagTracks = []
        self.damageMults = []
        self.particleSystems = []
        self.resetVisual()
        self.priority = -100

    def wantCombine(self, otherEffect) -> bool:
        """Does this effect want to combine with an other effect?"""
        return True

    def combine(self, otherEffect) -> None:
        """If so, functionality goes here."""
        self.resetVisual()
        self.wantReapply = True
        self.requestApply()

    def resetVisual(self):
        if self.avProfile:
            boostEffects = self.avProfile.getStatusEffectsOfId(SEE.EFFECT_TOON_DAMAGE_UP)
            for effect in boostEffects:
                if effect.gagTrack not in self.gagTracks:
                    self.gagTracks.append(effect.gagTrack)
                    self.damageMults.append(effect.maxUses)
            self.extraArgs = self.damageMults + self.gagTracks

    def onMovieAdd(self, extraArgs: list):
        if extraArgs[1] not in self.gagTracks:
            self.damageMults.append(extraArgs[0])
            self.gagTracks.append(extraArgs[1])

    def _doApply(self) -> None:
        """Applies the visual effect to the avatar."""
        for i in range(len(self.gagTracks)):
            gagTrack = self.gagTracks[i]
            damageMult = self.damageMults[i]
            from toontown.battle.BattleGlobals import TrackColors
            from toontown.battle import BattleParticles
            particleSystem = BattleParticles.createParticleEffect(file='toonBoost')
            particles = particleSystem.getParticlesList()[0]
            if 0 <= gagTrack < len(TrackColors):
                r, g, b = TrackColors[int(gagTrack)]
            else:
                r, g, b = (1.0, 1.0, 1.0)
            particles.renderer.setColor(LVecBase4f(r, g, b, 1.0))
            particleScale = self.ParticleScales.get(int(damageMult), 1.0)
            particles.renderer.setInitialXScale(particleScale)
            particles.renderer.setInitialYScale(particleScale)

            def startSystem(ps):
                if getattr(self, 'avProfile', None):  # helpful check because skipmovies
                    ps.start(parent=self.av, renderParent=render)
            taskMgr.doMethodLater(random.random() * 0.5, startSystem,
                                  f'toon-boost-enable-{i}-avid-{self.av.doId}', extraArgs=[particleSystem])
            self.particleSystems.append(particleSystem)

    def _doUnapply(self) -> None:
        """Unapplies the visual effect from the avatar."""
        from toontown.battle import BattleParticles
        for system in self.particleSystems:
            BattleParticles.cleanupSystem(system, duration=1.5, instant=self.hasCleanedUp)
        self.particleSystems = []


class CogDamageDownVisualEffect(ParticleVisualEffect):
    particleName = 'cogsDamageDown'
    cleanup_duration = 1.1
    wantEnum = SEE.EFFECT_COGS_DAMAGE_DOWN

    def _doApply(self):
        super()._doApply()
        # Slightly increase the particle radius if we suit C cogs.
        # They're too fat for them to show well otherwise
        if getSuitBodyType(self.av.style.name) == 'c':
            self.particleSystem.getParticlesList()[0].emitter.setRadius(1.4 * (self.av.scale / 0.845))


class VulnerableVisualEffect(VisualEffectBase):
    """
    The visual effect for a Toon that has received Snap (Vulnerable).
    """

    teethScale = 5.0

    def __init__(self, avProfile, effectEnum, extraArgs) -> None:
        super().__init__(avProfile, effectEnum, extraArgs)
        self.associatedStatusEffectIds = [SEE.EFFECT_VULNERABLE]
        self.statusEffectMode = WANT_ONE
        self.teeth = None

    def _doApply(self) -> None:
        """Applies the visual effect to the avatar."""
        from toontown.battle.BattleProps import globalPropPool
        self.teeth = globalPropPool.getProp('litigator_teeth')
        LerpScaleInterval(self.teeth, 0.3, 1.0 * self.teethScale, startScale=0.01).start()
        self.teeth.reparentTo(self.getLeftHand())
        self.teeth.setPos(-0.2, 0.03, 0.35)
        self.teeth.setHpr(80, -10, 170)

    def _doUnapply(self) -> None:
        """Unapplies the visual effect from the avatar."""
        Sequence(
            LerpScaleInterval(self.teeth, 0.3, 0.01),
            Func(self.teeth.cleanup),
        ).start()


class OldVulnerableVisualEffect(VisualEffectBase):
    """
    The visual effect for a Toon that has received Snap (Vulnerable).
    This is deprecated since it's kinda cringe.
    The effect is a snap texture orbiting around the toon.
    """

    def __init__(self, avProfile, effectEnum, extraArgs) -> None:
        super().__init__(avProfile, effectEnum, extraArgs)
        self.associatedStatusEffectIds = [SEE.EFFECT_VULNERABLE]
        self.statusEffectMode = WANT_ONE
        self.particleSystem = None

    def _doApply(self) -> None:
        """Applies the visual effect to the avatar."""
        from toontown.battle import BattleParticles
        self.particleSystem = BattleParticles.createParticleEffect(file='snap')
        self.particleSystem.start(parent=self.av, renderParent=self.av)
        renderer = self.particleSystem.getParticlesList()[0].renderer
        def changeSystemAlpha(a):
            renderer.setColor(LVecBase4f(1.0, 1.0, 1.0, a))
        LerpFunctionInterval(changeSystemAlpha, duration=1.0, fromData=0.0, toData=1.0).start()
        self.fadeIn = False

    def _doUnapply(self) -> None:
        """Unapplies the visual effect from the avatar."""
        from toontown.battle import BattleParticles
        BattleParticles.cleanupSystem(self.particleSystem, duration=1.0, instant=self.hasCleanedUp)
        renderer = self.particleSystem.getParticlesList()[0].renderer

        def changeSystemAlpha(a):
            renderer.setColor(LVecBase4f(1.0, 1.0, 1.0, a))

        if not self.hasCleanedUp:
            LerpFunctionInterval(changeSystemAlpha, duration=1.0, fromData=1.0, toData=0.0).start()
        else:
            changeSystemAlpha(0)
        self.particleSystem = None


class AdvancedOverrideIdleVisualEffect(VisualEffectBase):
    """
    An abstraction to allow for more fancy custom idles that can have more extreme poses.
    When they need to return to the actual neutral to do an attack, they use a custom "return" anim.
    """
    NewNeutral = ''
    NewNeutralReturn = ''

    def __init__(self, *args, **kwargs):
        assert self.NewNeutral, 'No new neutral animation present!'
        assert self.NewNeutralReturn, 'No new neutral return animation present!'
        super().__init__(*args, **kwargs)
        self.setWantPostAttackSeq(True)

    def _doApply(self):
        self.setAdvancedAnimOverride()
        # Override w/ no blend data cuz its stinky
        self.animBlendNeutralData = {}

    def _doUnapply(self):
        self.setAdvancedAnimNormal()
        # No DEFINED blend data which means it uses the default
        self.animBlendNeutralData = None

    def getPreAttackSequence(self):
        if self.av.isLured:
            return None
        return Sequence(
            Func(self.setAdvancedAnimNormal),
            ActorInterval(self.av, self.NewNeutralReturn)
        )

    def getPostAttackSequence(self):
        if not self.wantPostAttackSeq:
            return None
        return Sequence(
            ActorInterval(self.av, self.NewNeutralReturn, playRate=-1),
            Func(self.av.loop, self.NewNeutral),
            Func(self.setAdvancedAnimOverride),
        )

    def setAdvancedAnimNormal(self):
        self.animationOverrides = {}

    def setAdvancedAnimOverride(self):
        self.animationOverrides = {
            'neutral': self.NewNeutral,
            'true-neutral': 'neutral',
        }

    def setWantPostAttackSeq(self, value: bool):
        # If we want the post attack seq, we do NOT want the begin or end of attack default neutral
        self.wantPostAttackSeq = value
        self.wantBeginAttackNeutral = not value


class ScapegoatEnragedVisualEffect(ParticleVisualEffect, AdvancedOverrideIdleVisualEffect):
    particleName = 'scapegoatEnraged'
    cleanup_duration = 1.8
    NewNeutral = 'neutral-enraged'
    NewNeutralReturn = 'neutral-enraged-return'

    def __init__(self, *args, **kwargs):
        ParticleVisualEffect.__init__(self, *args, **kwargs)
        AdvancedOverrideIdleVisualEffect.__init__(self, *args, **kwargs)

    def _doApply(self):
        ParticleVisualEffect._doApply(self)
        AdvancedOverrideIdleVisualEffect._doApply(self)

    def _doUnapply(self):
        ParticleVisualEffect._doUnapply(self)
        AdvancedOverrideIdleVisualEffect._doUnapply(self)


class CaseManagerHotVisualEffect(ParticleVisualEffect):
    """smiles"""
    particleName = 'insured'
    cleanup_duration = 1.2
    wantEnum = SEE.EFFECT_CASE_MANAGER_HOT


class CaseManagerDotVisualEffect(VisualEffectBase):
    """
    The visual effect for a Toon that Is Legally Bound.
    """

    def __init__(self, avProfile, effectEnum, extraArgs) -> None:
        super().__init__(avProfile, effectEnum, extraArgs)
        self.associatedStatusEffectIds = [SEE.EFFECT_CASE_MANAGER_DOT]
        self.statusEffectMode = WANT_ONE
        self.tube = None

    def _doApply(self) -> None:
        """Applies the visual effect to the avatar."""
        from toontown.battle.BattleProps import globalPropPool
        if self.tube is None:
            self.tube = globalPropPool.getProp('redtape-tube')
            self.tube.setColorScale(0.25, 0.25, 1.0, 1.0)
            LerpScaleInterval(self.tube, 0.3, (0.3, 0.3, 0.09), (0.01, 0.01, 0.003)).start()
            self.tube.reparentTo(self.getRightHand())
            self.tube.setPos(0.3, 0.04, 0)
            self.tube.setHpr(0, 100, 90)
            self.tube.setScale(0.3, 0.3, 0.09)

    def _doUnapply(self) -> None:
        """Unapplies the visual effect from the avatar."""
        if self.tube:
            Sequence(
                LerpScaleInterval(self.tube, 0.3, (0.01, 0.01, 0.003)),
                Func(self.tube.removeNode),
            ).start()
            self.tube = None


class GagDownVisualEffect(ParticleVisualEffect):
    particleName = 'reducedGagPower'
    cleanup_duration = 1.1
    wantEnum = SEE.EFFECT_SANCTIONED


class UniteCooldownVisualEffect(ParticleVisualEffect):
    particleName = 'uniteCooldown'
    cleanup_duration = 1.1
    wantEnum = None

    def __init__(self, avProfile, effectEnum, extraArgs) -> None:
        super().__init__(avProfile, effectEnum, extraArgs)
        self.associatedStatusEffectIds = [SEE.EFFECT_UNITE_COOLDOWN, SEE.EFFECT_OVERWHELMING_AUTHORITY, SEE.EFFECT_REWARD_COOLDOWN, SEE.EFFECT_DEEP_FREEZE]
        self.statusEffectMode = WANT_ONE

    def _doApply(self):
        super()._doApply()
        # Ask Main
        if self.av.isLocal() and getattr(self.av, "battle", None):
            self.av.battle.addUniteDisabledFlag('unite-cooldown-visual-effect')

    def _doUnapply(self):
        super()._doUnapply()
        if self.av.isLocal() and getattr(self.av, "battle", None):
            self.av.battle.removeUniteDisabledFlag('unite-cooldown-visual-effect')


class OverchargedVisualEffect(VisualEffectBase):
    """
    The Overcharged buff.
    When the suit has hit their overheal HP cap, they gain
    the Overcharge perk, updating their health meter.
    """

    def __init__(self, avProfile, effectEnum, extraArgs) -> None:
        super().__init__(avProfile, effectEnum, extraArgs)
        self.associatedStatusEffectIds = [SEE.EFFECT_OVERCHARGED]
        self.statusEffectMode = WANT_ONE
        self.hpRatio = 1.5
        if len(extraArgs) > 1:
            self.hpRatio = extraArgs[3]
            self.extraArgs = [self.hpRatio]
        elif len(extraArgs) == 1:
            self.hpRatio = self.extraArgs[0]

    def _doUnapply(self) -> None:
        self.av.resetSuperchargeState()
        self.av.updateHealthBar(0)

    def _doApply(self) -> None:
        self.av.setSuperchargeRatio(self.hpRatio)
        self.av.updateHealthBar(0)


class OcForemanVisualEffect(ParticleVisualEffect):
    """smiles"""
    particleName = 'ocforeman'
    cleanup_duration = 1.2

    type2Col = {
        # Copied from StatusEffectGlobals.
        # Bellow - Violet
        0: Vec4(0.322, 0.086, 0.753, 1.0),
        # Antergy - Orange
        1: Vec4(0.925, 0.635, 0.2, 1.0),
        # Steadfast - Green
        2: Vec4(0.294, 0.918, 0.208, 1.0),
        # Compensation - Cyan
        3: Vec4(0.271, 0.886, 0.859, 1.0),
        # Destruction - Black
        4: Vec4(0.114, 0.02, 0.02, 1.0),
        # Prethinking - Pink
        5: Vec4(0.871, 0.384, 0.91, 1.0),
        # Rebalance - Yellow
        6: Vec4(0.929, 0.945, 0.212, 1.0),
        # Sacrifice - Red
        7: Vec4(0.792, 0.051, 0.051, 1.0),
        # Prismatic - White
        8: Vec4(1, 1, 1, 1),
    }

    def _doApply(self) -> None:
        """
        Applies the visual effect to the avatar.
        Override to set color on it.
        """
        from toontown.battle import BattleParticles
        if not self.isPrismatic():
            self.particleSystem = BattleParticles.createParticleEffect(file=self.particleName)
            self.setPsColor(self.particleSystem)
            self.particleSystem.start(parent=self.av, renderParent=self.av)
        else:
            cols = (
                Vec4(0.918, 0.169, 0.082, 1.0),
                Vec4(0.918, 0.502, 0.082, 1.0),
                Vec4(0.918, 0.918, 0.082, 1.0),
                Vec4(0.345, 0.882, 0.118, 1.0),
                Vec4(0.149, 0.851, 0.851, 1.0),
                Vec4(0.149, 0.149, 0.851, 1.0),
                Vec4(0.624, 0.184, 0.816, 1.0),
            )
            self.particleSystem = []
            for col in cols:
                system = BattleParticles.createParticleEffect(file=self.particleName)
                self.setPsColor(system, override=col)
                system.start(parent=self.av, renderParent=self.av)
                self.particleSystem.append(system)

    def _doUnapply(self) -> None:
        """Unapplies the visual effect from the avatar."""
        from toontown.battle import BattleParticles
        if not self.isPrismatic():
            BattleParticles.cleanupSystem(self.particleSystem,
                                          duration=self.cleanup_duration,
                                          instant=self.cleanup_instant or self.hasCleanedUp)
            self.particleSystem = None
        else:
            for system in self.particleSystem:
                BattleParticles.cleanupSystem(system,
                                              duration=self.cleanup_duration,
                                              instant=self.cleanup_instant or self.hasCleanedUp)
            self.particleSystem = []

    def setPsColor(self, particleSystem, override=None):
        """Attunes the color of the particles."""
        particles = particleSystem.getParticlesList()[0]
        col = override if override else self.type2Col[self.getType()]
        particles.renderer.set_center_color(col)
        particles.renderer.set_edge_color(col)

    def isPrismatic(self):
        return self.getType() == 8

    def getType(self):
        return self.extraArgs[0]


class DisruptiveAdvertisementVisualEffect(VisualEffectBase):
    """
    The visual effect for the DOPA when he has Disruptive Advertisement active.
    """

    def __init__(self, avProfile, effectEnum, extraArgs) -> None:
        super().__init__(avProfile, effectEnum, extraArgs)
        self.associatedStatusEffectIds = [SEE.EFFECT_DISRUPTIVE_ADVERTISEMENT]
        self.statusEffectMode = WANT_ONE
        # What will house the stream of fake suits that are copied during the sequence
        self.displayNode = None
        # The fake suit in question. Will be shuffling out of fake suits over time
        self.displaySuit = None
        # The sequence that displays of the fake suit growing/becoming transparent
        self.displaySeq = None

    def _doApply(self) -> None:
        """Applies the visual effect to the avatar."""

        # don't reduce battle effects if accessibility is active
        if settings['reduce-battle-effects']:
            return

        self.displayNode = self.av.attachNewNode('displayNode')

        # Make it support transparency, and colorscale it to orange
        self.displayNode.setTransparency(1)
        self.displayNode.setColorScale(1.0, 0.5, 0.0, 0.6)
        # Turn off depth writing so that it always is shown above
        self.displayNode.setDepthWrite(False)
        self.displayNode.setDepthTest(False)

        def updateDisplaySuit():
            if self.displaySuit:
                self.displaySuit.removeNode()
            # This is the cleanest solution I could find to get the animation state to transfer.
            self.displaySuit = self.av.getGeomNode().copyTo(self.displayNode)

        # Silhouette sequence that shows it growing and then fading away
        self.displaySeq = Sequence(
            Func(self.displayNode.setScale, 1.0),
            Func(self.displayNode.setColorScale, (1.0, 0.5, 0.0, 0.6)),
            Func(updateDisplaySuit),
            Parallel(
                LerpScaleInterval(self.displayNode, 0.6, 1.25, blendType='easeOut'),
                LerpColorScaleInterval(self.displayNode, 0.6, (1.0, 0.5, 0.0, 0.0), blendType='easeOut')
            ),
            Wait(0.7),
        )
        self.displaySeq.loop()

    def _doUnapply(self) -> None:
        """Unapplies the visual effect from the avatar."""
        if self.displaySeq:
            self.displaySeq.finish()
            self.displaySeq = None

        if self.displayNode:
            self.displayNode.removeNode()
            self.displayNode = None
        self.displaySuit = None


class ExtraGlowerPowersVisualEffect(VisualEffectBase):
    """
    The visual effect for the DOPA/DOPR when he has extra glower powers.
    """

    def __init__(self, avProfile, effectEnum, extraArgs) -> None:
        super().__init__(avProfile, effectEnum, extraArgs)
        self.associatedStatusEffectIds = [SEE.EFFECT_AMBUSH_MARKETING, SEE.EFFECT_MULTI_LEVEL_MARKETING]
        self.statusEffectMode = WANT_ONE
        self.rotateNode = None
        self.rotateSeq = None
        self.knives = []

    def _doApply(self) -> None:
        """Applies the visual effect to the avatar."""
        from toontown.battle.BattleProps import globalPropPool
        from toontown.battle import MovieUtil

        # Set up a new rotate node to rotate knives around
        self.rotateNode = self.av.attachNewNode('knifeRotateNode')
        self.rotateNode.setZ(self.av.height - 1.0)

        # Start at 0 H, increase with each new knife
        startH = 0
        self.rotateSeq = Parallel()

        # Grab the actual data of number of extra attacks from the "owner" effect
        # This will either be Ambush Marketing or Multi Level Marketing
        ownerEffect = self.avProfile.getStatusEffectOfId(SEE.EFFECT_AMBUSH_MARKETING) or self.avProfile.getStatusEffectOfId(SEE.EFFECT_MULTI_LEVEL_MARKETING)
        if ownerEffect:
            totalExtraAttacks = int(ownerEffect.numExtraAttacks)
        else:
            # Fallback, no owner effect so grab our original extra attack num
            totalExtraAttacks = int(self.extraArgs[0])

        # Increase the H value by the given amount per new knife
        hIncreasePerKnife = 45
        # How many knives are in one circle around the avatar before it creates a new further out circle
        numPerCircle = int(math.floor(360 / hIncreasePerKnife))

        # Generic dagger we will copy
        knife = globalPropPool.getProp('dagger')
        for attackNum in range(totalExtraAttacks):
            # New knife copy
            newKnife = MovieUtil.copyProp(knife)
            newKnife.setHpr(180, 270, 90)
            newKnife.setScale(0.5)
            newKnife.setColorScale(1.0, 1.0, 1.0, 0.5)
            self.knives.append(newKnife)

            # The node that will actually be rotating
            knifeNode = self.rotateNode.attachNewNode(f'newKnife-{attackNum}')

            newKnife.reparentTo(knifeNode)
            newKnife.setY(2)

            increaseH = True
            # Num outside first circle. If this is greater than 1, then the knives will begin to circle
            # further outwards, creating extra circles surrounding them.
            numOutsideFirstCircle = (attackNum + 1) / numPerCircle
            if numOutsideFirstCircle > 1:
                # If a number is right on the dot of an integer, i.e. 4.0, it has just finished that circle.
                endOfCircle = numOutsideFirstCircle == int(numOutsideFirstCircle)
                # Give the knife a Y increase based on which outwards circle it is a part of
                # This will create multiple spinning circles
                yIncrease = math.floor(numOutsideFirstCircle)
                if endOfCircle:
                    # "End of circle" knives need to be manually adjusted to be where they should be
                    yIncrease -= 1
                newKnife.setY(newKnife.getY() + yIncrease)

                # Increase the H value of the knives if this is an odd numbered knife group
                # Increase H True means that the knives will be spinning one way, while
                # Increase H False means that the knives will be spinning the other way
                increaseH = int(numOutsideFirstCircle) % 2 != 1
                if endOfCircle:
                    # Again, manually adjust end of circle knives to be where they should
                    increaseH = not increaseH

            # Backwards knife rotation if the H is not increasing
            startHpr = (startH, 0, 0) if increaseH else (360 + startH, 0, 0)
            endHpr = (360 + startH, 0, 0) if increaseH else (startH, 0, 0)

            # Add the knife to the sequence now that everything has been established
            self.rotateSeq.append(
                Sequence(
                    LerpHprInterval(knifeNode, 3.0, endHpr, startHpr=startHpr),
                )
            )
            # Modify the start H value for the next knives in the list
            startH += (hIncreasePerKnife if increaseH else -hIncreasePerKnife)

        # Everything is done now, so go ahead and loop the sequence of knife rotations
        self.rotateSeq.loop()
        MovieUtil.removeProp(knife)

    def _doUnapply(self) -> None:
        """Unapplies the visual effect from the avatar."""
        from toontown.battle import MovieUtil
        if self.rotateSeq:
            self.rotateSeq.finish()
            self.rotateSeq = None

        for knife in self.knives:
            MovieUtil.removeProp(knife)
        self.knives = []

        if self.rotateNode:
            self.rotateNode.removeNode()
            self.rotateNode = None


class InkDrainVisualEffect(VisualEffectBase):
    """
    The visual effect for Ink Drain.
    """

    def __init__(self, avProfile, effectEnum, extraArgs) -> None:
        super().__init__(avProfile, effectEnum, extraArgs)
        self.associatedStatusEffectIds = [SEE.EFFECT_INK_DRAIN]
        self.statusEffectMode = WANT_ONE
        self.applyDuringMovie = False
        self.removeDuringMovie = True
        self.priority = 150
        self.seq = None

    @property
    def taskName(self):
        return self.av.uniqueName('ink-drain-ve-seq')

    def _doApply(self) -> None:
        self.seq = self.av.colorEntireToon(self._makeColor())
        messenger.send(
            self.av.uniqueName('set-laff-meter-color'), [self._makeColor()]
        )
        taskMgr.remove(self.taskName)
        taskMgr.doMethodLater(0.1, self.doToonColor, self.taskName)

    def _doUnapply(self) -> None:
        self.seq = self.av.colorEntireToon()
        messenger.send(
            self.av.uniqueName('set-laff-meter-color')
        )
        taskMgr.remove(self.taskName)
        taskMgr.doMethodLater(0.1, self.doToonColor, self.taskName)

    def resetToonColors(self):
        if self.hasCleanedUp:
            return
        headParts = self.av.getHeadParts()
        torsoParts = self.av.getTorsoParts()
        legsParts = self.av.getLegsParts()
        parts = headParts + torsoParts + legsParts
        for nextPart in parts:
            nextPart.clearColorScale()

    def doToonColor(self, task):
        if self.seq:
            self.resetToonColors()
            self.seq.start()
        return task.done

    def _doUnapplyMovie(self):
        if not self.battle:
            return Sequence(), Sequence()
        unapplyTrack = Sequence(
            self.av.colorEntireToon(lerpTime=1.0),
            Func(self._doUnapply),
        )
        unapplyCamTrack = self.avProfile.battle.camera.toonGroupShot(duration=unapplyTrack.getDuration())
        return unapplyTrack, unapplyCamTrack

    def roundStart(self):
        messenger.send(
            self.av.uniqueName('set-laff-meter-color'), [self._makeColor() if self.hasApplied else None]
        )

    def _makeColor(self):
        """Builds the average color of the entire toon."""
        style = self.av.style
        averageCol = sum([*style.getArmColor()] + [*style.getLegColor()] + [*style.getHeadColor()]) / 12.0
        return Vec4(averageCol, averageCol, averageCol, 1.0)


class PeeledVisualEffect(VisualEffectBase):
    """
    The visual effect for Peeled (Tree killer).
    """

    def __init__(self, avProfile, effectEnum, extraArgs) -> None:
        super().__init__(avProfile, effectEnum, extraArgs)
        self.associatedStatusEffectIds = [SEE.EFFECT_PEELING_THE_BARK]
        self.statusEffectMode = WANT_ONE
        self.applyDuringMovie = False
        self.removeDuringMovie = True
        self.priority = 150
        self.seq = None

    @property
    def taskName(self):
        return self.av.uniqueName('peeled-ve-seq')

    def _doApply(self) -> None:
        self.seq = self.av.colorEntireToon(self._makeColor())
        messenger.send(
            self.av.uniqueName('set-laff-meter-color'), [self._makeColor()]
        )
        taskMgr.remove(self.taskName)
        taskMgr.doMethodLater(0.1, self.doToonColor, self.taskName)

    def _doUnapply(self) -> None:
        self.seq = self.av.colorEntireToon()
        messenger.send(
            self.av.uniqueName('set-laff-meter-color')
        )
        taskMgr.remove(self.taskName)
        taskMgr.doMethodLater(0.1, self.doToonColor, self.taskName)

    def resetToonColors(self):
        if self.hasCleanedUp:
            return
        headParts = self.av.getHeadParts()
        torsoParts = self.av.getTorsoParts()
        legsParts = self.av.getLegsParts()
        earParts = self.av.getEarParts()
        parts = headParts + torsoParts + legsParts + earParts
        for nextPart in parts:
            nextPart.clearColorScale()

    def doToonColor(self, task):
        if self.seq:
            self.resetToonColors()
            self.seq.start()
        return task.done

    def _doUnapplyMovie(self):
        if not self.battle:
            return Sequence(), Sequence()
        unapplyTrack = Sequence(
            self.av.colorEntireToon(lerpTime=1.0),
            Func(self._doUnapply),
        )
        unapplyCamTrack = self.avProfile.battle.camera.toonGroupShot(duration=unapplyTrack.getDuration())
        return unapplyTrack, unapplyCamTrack

    def roundStart(self):
        messenger.send(
            self.av.uniqueName('set-laff-meter-color'), [self._makeColor() if self.hasApplied else None]
        )

    def _makeColor(self):
        """Bingus peeled epic."""
        return Vec4(0.816, 0.62, 0.631, 1.0)


class ToonsAccuracyUpVisualEffect(VisualEffectBase):
    """
    The visual effect for Toons Accuracy Up.
    """

    def __init__(self, avProfile, effectEnum, extraArgs) -> None:
        super().__init__(avProfile, effectEnum, extraArgs)
        self.associatedStatusEffectIds = [SEE.EFFECT_TOONS_ACCURACY_UP]
        self.statusEffectMode = WANT_ONE
        self.seq = None

    def _doApply(self) -> None:
        self.seq = Parallel()

        glovePieces = self.av.getPieces(('torso', '*hands*'))
        for piece in glovePieces:
            glowSeq = Sequence(
                LerpColorInterval(piece, 1.0, (0.2, 1.0, 0.2, 1.0), blendType='easeIn'),
                LerpColorInterval(piece, 1.0, (1.0, 1.0, 1.0, 1.0), blendType='easeOut'),
                Wait(1.0),
            )
            self.seq.append(glowSeq)

        self.seq.loop()

    def _doUnapply(self) -> None:
        from toontown.inventory.enums.ItemEnums import CheesyEffectItemType

        if self.seq:
            self.seq.finish()
        self.seq = None

        glovePieces = self.av.getPieces(('torso', '*hands*'))
        for piece in glovePieces:
            piece.setColor(self.av.style.gloveColor)
            # TODO: Add white/big white toon support if you want
            if self.av.cheesyEffect == CheesyEffectItemType.GreenToon:
                piece.setColor(VBase4(14 / 255.0, 173 / 255.0, 40 / 255.0, 1))


class ChangeSpeciesVisualEffect(VisualEffectBase):
    """
    A visual effect that changes the species of the Toons who have it
    """

    def __init__(self, avProfile, effectEnum, extraArgs) -> None:
        super().__init__(avProfile, effectEnum, extraArgs)
        self.applyDuringMovie = True
        self.removeDuringMovie = True
        self.priority = 150

    @property
    def species(self):
        from toontown.toon import ToonDNA
        # This extra argument is a numerical index of the head type
        return ToonDNA.toonSpeciesTypes[int(self.extraArgs[0])]

    @property
    def oldSpecies(self):
        from toontown.toon import ToonDNA
        # This extra argument is a numerical index of their old, correct head type
        return ToonDNA.toonSpeciesTypes[int(self.extraArgs[1])]

    def _doSpeciesChange(self, species):
        messenger.send(
            self.av.uniqueName('set-laff-meter-species'), [species])

        self.av.style.head = f'{species}{self.av.style.head[1:]}'
        self.av.updateToonDNA(self.av.style, fForce=1)
        self.av.setBlend(frameBlend=base.wantSmoothAnims)
        self.av.setLODAnimation(base.lodMaxRange, base.lodMinRange, base.lodDelayFactor)
        self.av.initializeDropShadow()
        self.av.stopLookAround()
        self.av.loop('neutral')
        self.av.regenerateAccessories()

    def _doApply(self) -> None:
        if self.av is None:
            return

        self._doSpeciesChange(self.species)

    def _doUnapply(self) -> None:
        if self.av is None:
            return

        self._doSpeciesChange(self.oldSpecies)

    def _doApplyMovie(self):
        """
        Returns a sequence where this visual effect gets applied.
        To be played during the Battle Movie, if
        the self.applyDuringMovie is set to be True.
        """
        if not self.battle:
            return Sequence(), Sequence()
        appSeq = Sequence(Func(self.av.doDustCloud), Wait(0.37), Func(self._doApply))
        camSeq = self.avProfile.battle.camera.allGroupOverheadShot(duration=80.0 / 24.0)
        return appSeq, camSeq

    def _doUnapplyMovie(self):
        """
        Returns a sequence where this visual effect gets unapplied.
        To be played during the Battle Movie, if
        the self.removeDuringMovie is set to be True.
        """
        if not self.battle:
            return Sequence(), Sequence()
        appSeq = Sequence(Func(self.av.doDustCloud), Wait(0.37), Func(self._doUnapply))
        camSeq = self.avProfile.battle.camera.allGroupOverheadShot(duration=80.0 / 24.0)
        return appSeq, camSeq

    def roundStart(self):
        messenger.send(
            self.av.uniqueName('set-laff-meter-species'), [self.species]
        )


class DivingVisualEffect(MultiParticleVisualEffect):
    particleNames = ['underwaterRipples', 'underwaterBubbles']
    cleanup_duration = 1.0
    wantEnum = SEE.EFFECT_DIVING

    def __init__(self, avProfile, effectEnum, extraArgs) -> None:
        super().__init__(avProfile, effectEnum, extraArgs)
        self.associatedStatusEffectIds = [SEE.EFFECT_DIVING]
        self.statusEffectMode = WANT_ONE
        self.particleRenderNode = None

    def getParticleParent(self):
        return self.particleRenderNode

    def _doApply(self) -> None:
        """Applies the visual effect to the avatar."""
        self.particleRenderNode = self.av.attachNewNode('diving-particle-render-node')
        super()._doApply()
        self.animationOverrides = {
            'neutral': 'underwaterHit',
            'walk': 'underwaterHit',
            'sidestep-left': 'underwater-sidestep',
            'sidestep-right': 'underwater-sidestep',
        }
        if self.av.dropShadow:
            self.av.dropShadow.hide()
        # Lower the nametag since we're in the ground
        if self.av.nametag3d:
            self.av.nametag3d.setPos(0, 0, 4.0)

    def _doUnapply(self) -> None:
        """Unapplies the visual effect from the avatar."""
        super()._doUnapply()
        self.animationOverrides = {}
        if self.av.dropShadow:
            self.av.dropShadow.show()
        # Re-fix the nametag
        if self.av.nametag3d:
            self.av.nametag3d.setPos(0, 0, self.av.height + 1.0)

        self.particleRenderNode.removeNode()


class WoodchippedVisualEffect(ParticleVisualEffect):
    particleName = 'woodchipperDamageLowVisualEffect'
    cleanup_duration = 1.0
    wantEnum = SEE.EFFECT_WOODCHIPPER


class MarkedWoodVisualEffect(WoodchippedVisualEffect):
    wantEnum = SEE.EFFECT_MARKED_WOOD


class OverhireVisualEffect(VisualEffectBase):
    """
    The visual effect for Featherbedder and his Overhire effect.
    """
    BadParts = [
        'joint_shadow',
    ]
    GlowStrength = 0.3

    def __init__(self, avProfile, effectEnum, extraArgs) -> None:
        super().__init__(avProfile, effectEnum, extraArgs)
        self.associatedStatusEffectIds = [SEE.EFFECT_MANAGER_FEATHERBEDDER]
        self.statusEffectMode = WANT_ONE
        self.glowSeq = None
        self.overhireTexture = None
        self.overhireTextureStage = None
        self.resetVisual()

    def resetVisual(self):
        if self.avProfile:
            overhireEffect = self.avProfile.getStatusEffectOfId(SEE.EFFECT_MANAGER_FEATHERBEDDER)
            if overhireEffect:
                self.extraArgs = overhireEffect.extraArgs[:]

    @property
    def attackMult(self):
        return self.extraArgs[0] - 1.0

    @property
    def glowStrengthMax(self):
        return 1.0 - (self.attackMult * self.GlowStrength)

    @property
    def suitParts(self):
        return [part for part in self.av.find('**/__Actor_modelRoot').getChildren() if part.getName() not in self.BadParts]

    @property
    def textureStageName(self):
        return f'overhire-ts-{self.av.doId}'

    def makeTextureStage(self):
        ts = TextureStage(self.textureStageName)
        ts.setMode(TextureStage.MCombine)
        ts.setSort(1)
        ts.setCombineRgb(
            TextureStage.CMInterpolate, TextureStage.CSPrevious, TextureStage.COSrcColor, TextureStage.CSTexture,
            TextureStage.COSrcColor, TextureStage.CSConstant, TextureStage.COSrcColor
        )
        ts.setCombineAlpha(
            TextureStage.CMInterpolate, TextureStage.CSPrevious, TextureStage.COSrcAlpha, TextureStage.CSTexture,
            TextureStage.COSrcAlpha, TextureStage.CSConstant, TextureStage.COSrcAlpha
        )
        return ts

    def getTextureStage(self):
        if not getattr(self, 'avProfile', None):
            return None

        if self.overhireTextureStage:
            return self.overhireTextureStage

        textureStages = self.av.findAllTextureStages()
        glowStage = textureStages.findTextureStage(self.textureStageName)
        if not glowStage:
            glowStage = self.makeTextureStage()
        self.overhireTextureStage = glowStage
        return glowStage

    def setTextureAlphaFunc(self, value):
        ts = self.getTextureStage()
        if ts:
            ts.setColor(Vec4(value, value, value, value))
        else:
            self.glowSeq.pause()
            self.glowSeq = None

    def _doApply(self) -> None:
        """Applies the visual effect to the avatar."""
        ts = self.getTextureStage()
        if not ts:
            return

        if not self.overhireTexture:
            self.overhireTexture = loader.loadTexture('phase_12/maps/ttcc_ene_featherbedder_glow.png')
            self.overhireTexture.setWrapU(Texture.WMRepeat)
            self.overhireTexture.setWrapV(Texture.WMRepeat)

        for suitPart in self.suitParts:
            suitPart.setTexture(ts, self.overhireTexture)

        if self.glowSeq:
            self.glowSeq.finish()
            self.glowSeq = None

        dur = 2.0
        # this sequence is so prone to memory leaks.
        # welcome to visual effect code
        self.glowSeq = Sequence(
            LerpFunctionInterval(self.setTextureAlphaFunc, fromData=1.0, toData=self.glowStrengthMax,
                                 duration=dur / 2.0,
                                 blendType='easeInOut'),
            LerpFunctionInterval(self.setTextureAlphaFunc, fromData=self.glowStrengthMax, toData=1.0,
                                 duration=dur / 2.0,
                                 blendType='easeInOut'),
            Wait(1.0)
        )
        self.glowSeq.loop()

    def _doUnapply(self) -> None:
        """Unapplies the visual effect from the avatar."""
        if self.glowSeq:
            self.glowSeq.finish()
            self.glowSeq = None
        self.overhireTexture = None
        self.overhireTextureStage = None


class TrialByFireVisualEffect(ParticleVisualEffect):
    """
    The Visual Effect used for Trial By Fire. Makes Toons nice and toasty.
    """
    particleName = 'trialByFireVisualEffect'
    cleanup_duration = 1.0
    wantEnum = SEE.EFFECT_TRIAL_BY_FIRE
    applyTime = 0.8

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.associatedStatusEffectIds = [SEE.EFFECT_TRIAL_BY_FIRE, SEE.EFFECT_FTF_FOREMAN_BURNING_SMOKED]
        self.applyDuringMovie = True
        self.removeDuringMovie = True

    def changeColor(self, wantLerp=False):
        if self.av.isSuit():
            return Sequence()

        part = self.av.getGeomNode()
        track = Parallel()
        if wantLerp:
            seq = LerpColorScaleInterval(part, self.applyTime, Vec4(0, 0, 0, 1))
        else:
            seq = Func(part.setColorScale, Vec4(0, 0, 0, 1))
        track.append(seq)

        return track

    def changeColorBack(self, wantLerp=False):
        if self.av.isSuit():
            return Sequence()

        part = self.av.getGeomNode()
        track = Parallel()
        if wantLerp:
            seq = Sequence(
                LerpColorScaleInterval(part, self.applyTime, Vec4(1, 1, 1, 1)),
                Func(part.clearColorScale)
            )
        else:
            seq = Func(part.clearColorScale)
        track.append(seq)

        return track

    def _doApply(self) -> None:
        super()._doApply()
        self.changeColor().finish()

    def _doUnapply(self) -> None:
        super()._doUnapply()
        self.changeColorBack().finish()

    def _doApplyMovie(self):
        """
        Returns a sequence where this visual effect gets applied.
        To be played during the Battle Movie, if
        the self.applyDuringMovie is set to be True.
        """
        appSeq = Parallel()
        appSeq.append(self.changeColor(wantLerp=True))
        appSeq = Parallel(
            appSeq,
            Sequence(
                Wait(self.applyTime),
                Func(self._doApply)
            )
        )
        camSeq = Sequence()
        return appSeq, camSeq

    def _doUnapplyMovie(self):
        """
        Returns a sequence where this visual effect gets applied.
        To be played during the Battle Movie, if
        the self.applyDuringMovie is set to be True.
        """
        if not self.battle:
            return Sequence(), Sequence()
        appSeq = Parallel()
        appSeq.append(self.changeColorBack(wantLerp=True))
        appSeq = Parallel(
            appSeq,
            Sequence(
                Wait(self.applyTime),
                Func(self._doUnapply)
            )
        )
        camSeq = self.avProfile.battle.camera.allGroupOverheadShot(duration=80.0 / 24.0)
        return appSeq, camSeq


class CoreCompetencyVisualEffect(VisualEffectBase):
    """
    The visual effect for Gatekeeper's fodders and their core competency effect.
    """
    BadParts = ['joint_shadow']

    def __init__(self, avProfile, effectEnum, extraArgs) -> None:
        super().__init__(avProfile, effectEnum, extraArgs)
        self.associatedStatusEffectIds = [SEE.EFFECT_GATEKEEPER_FODDER_BONUS]
        self.statusEffectMode = WANT_ONE
        self.glowSeq = None
        self.competencyTexture = None
        self.competencyTextureStage = None
        self.resetVisual()

    def resetVisual(self):
        if self.avProfile:
            frontlineEffect = self.avProfile.getStatusEffectOfId(SEE.EFFECT_GATEKEEPER_FODDER_BONUS)
            if frontlineEffect:
                self.extraArgs = frontlineEffect.extraArgs[:]

    @property
    def attackBonus(self):
        return self.extraArgs[1]

    @property
    def glowStrengthMax(self):
        return 1.0 - (0.5 * min(self.attackBonus/15, 1))

    @property
    def suitParts(self):
        return [part for part in self.av.find('**/__Actor_modelRoot').getChildren() if part.getName() not in self.BadParts]

    @property
    def textureStageName(self):
        return f'competency-ts-{self.av.doId}'

    def makeTextureStage(self):
        ts = TextureStage(self.textureStageName)
        ts.setMode(TextureStage.MCombine)
        ts.setSort(1)
        ts.setCombineRgb(
            TextureStage.CMInterpolate, TextureStage.CSPrevious, TextureStage.COSrcColor, TextureStage.CSTexture,
            TextureStage.COSrcColor, TextureStage.CSConstant, TextureStage.COSrcColor
        )
        ts.setCombineAlpha(
            TextureStage.CMInterpolate, TextureStage.CSPrevious, TextureStage.COSrcAlpha, TextureStage.CSTexture,
            TextureStage.COSrcAlpha, TextureStage.CSConstant, TextureStage.COSrcAlpha
        )
        return ts

    def getTextureStage(self):
        if not getattr(self, 'avProfile', None):
            return None

        if self.competencyTextureStage:
            return self.competencyTextureStage

        textureStages = self.av.findAllTextureStages()
        glowStage = textureStages.findTextureStage(self.textureStageName)
        if not glowStage:
            glowStage = self.makeTextureStage()
        self.competencyTextureStage = glowStage
        return glowStage

    def setTextureAlphaFunc(self, value):
        ts = self.getTextureStage()
        if ts:
            ts.setColor(Vec4(value, value, value, value))
        else:
            self.glowSeq.pause()
            self.glowSeq = None

    def _doApply(self) -> None:
        """Applies the visual effect to the avatar."""
        ts = self.getTextureStage()
        if not ts:
            return

        if not self.competencyTexture:
            self.competencyTexture = loader.loadTexture('phase_14/maps/gatekeeper_glow.png')
            self.competencyTexture.setWrapU(Texture.WMRepeat)
            self.competencyTexture.setWrapV(Texture.WMRepeat)

        for suitPart in self.suitParts:
            suitPart.setTexture(ts, self.competencyTexture)

        if self.glowSeq:
            self.glowSeq.finish()
            self.glowSeq = None

        dur = 2.0
        # Show red if attack bonus is greater than 0. Strength is based on how high the damage mult is, up to 15
        if self.attackBonus > 0:
            self.glowSeq = Sequence(
                LerpFunctionInterval(self.setTextureAlphaFunc, fromData=1.0, toData=self.glowStrengthMax,
                                     duration=dur / 2.0,
                                     blendType='easeInOut'),
                LerpFunctionInterval(self.setTextureAlphaFunc, fromData=self.glowStrengthMax, toData=1.0,
                                     duration=dur / 2.0,
                                     blendType='easeInOut'),
                Wait(1.0)
            )
            self.glowSeq.loop()
        else:
            # Sounds stupid because its 1.0, but this makes the effect not show up
            self.setTextureAlphaFunc(1.0)

    def _doUnapply(self) -> None:
        """Unapplies the visual effect from the avatar."""
        if self.glowSeq:
            self.glowSeq.finish()
            self.glowSeq = None
        self.competencyTexture = None
        self.competencyTextureStage = None


class DeepFreezeVisualEffect(ParticleVisualEffect):
    """
    The visual effect for Plutocrat's Deep Freeze.

    It's so cold.
    """
    particleName = "suitFrozen"

    def __init__(self, avProfile, effectEnum, extraArgs) -> None:
        super().__init__(avProfile, effectEnum, extraArgs)
        self.associatedStatusEffectIds = [SEE.EFFECT_DEEP_FREEZE]
        self.statusEffectMode = WANT_ONE
        self.applyDuringMovie = False
        self.removeDuringMovie = True
        self.priority = 150
        self.seq = None
        self.particleNode = None

    def getParticleParent(self):
        if self.particleNode:
            return self.particleNode
        return self.av

    @property
    def taskName(self):
        return self.av.uniqueName('deep-freeze-ve-seq')
    
    def colorToon(self, colorScale) -> None:
        def changeColor(parts):
            track = Parallel()
            for nextPart in parts:
                track.append(LerpColorScaleInterval(nextPart, duration=0, colorScale=colorScale))

            return track
        
        headParts = self.av.getHeadParts()
        torsoParts = self.av.getTorsoParts()
        legsParts = self.av.getLegsParts()

        return Parallel(changeColor(headParts), changeColor(torsoParts), changeColor(legsParts))
    
    def uncolorToon(self) -> None:
        def resetColor(parts):
            track = Parallel()
            for nextPart in parts:
                track.append(Func(nextPart.clearColorScale))

            return track
        
        headParts = self.av.getHeadParts()
        torsoParts = self.av.getTorsoParts()
        legsParts = self.av.getLegsParts()

        return Parallel(resetColor(headParts), resetColor(torsoParts), resetColor(legsParts))

    def _doApply(self) -> None:
        # create and configure a special node for holding particles
        self.particleNode = self.av.attachNewNode('particleNode')
        self.particleNode.setDepthWrite(False)
        self.particleNode.setBin('fixed', 1)
        self.particleNode.setTransparency(TransparencyAttrib.MDual)
        self.particleNode.setZ(self.av.height * 0.4)
        super()._doApply()
        self.particleNode.setScale(1.0, 1.0, self.av.height * 0.3)
        self.seq = self.colorToon(self._makeColor())
        messenger.send(
            self.av.uniqueName('set-laff-meter-color'), [self._makeColor()]
        )
        taskMgr.remove(self.taskName)
        taskMgr.doMethodLater(0.1, self.doToonColor, self.taskName)

    def _doUnapply(self) -> None:
        super()._doUnapply()
        if self.particleNode:
            self.particleNode.removeNode()
        self.seq = self.uncolorToon()
        messenger.send(
            self.av.uniqueName('set-laff-meter-color')
        )
        taskMgr.remove(self.taskName)
        taskMgr.doMethodLater(0.1, self.doToonColor, self.taskName)

    def resetToonColors(self):
        if self.hasCleanedUp:
            return
        headParts = self.av.getHeadParts()
        torsoParts = self.av.getTorsoParts()
        legsParts = self.av.getLegsParts()
        parts = headParts + torsoParts + legsParts
        for nextPart in parts:
            nextPart.clearColorScale()

    def doToonColor(self, task):
        if self.seq:
            self.resetToonColors()
            self.seq.start()
        return task.done

    def _doUnapplyMovie(self):
        if not self.battle:
            return Sequence(), Sequence()
        unapplyTrack = Sequence(
            self.uncolorToon(),
            Func(self._doUnapply),
        )
        unapplyCamTrack = self.avProfile.battle.camera.toonGroupShot(duration=unapplyTrack.getDuration())
        return unapplyTrack, unapplyCamTrack

    def roundStart(self):
        messenger.send(
            self.av.uniqueName('set-laff-meter-color'), [self._makeColor() if self.hasApplied else None]
        )

    def _makeColor(self):
        """Builds the average color of the entire toon."""
        return Vec4(51/255, 255/255, 255/255, 1.0)


class RushJobVisualEffect(VisualEffectBase):
    def __init__(self, *args):
        super().__init__(*args)
        self.applyDuringMovie = True
        self.statusEffectMode = WANT_ONE
        self.associatedStatusEffectIds = [SEE.EFFECT_RUSH_JOB]
        self.gagTrack = AttackEnum.TOON_HEAL
        self.resetVisual()

        if getattr(builtins, "simbase", None):
            return

        self.arrowSeq: Sequence = None

        self.upPos = Point3(0, 0, self.av.getHeight() + 3)
        self.downPos = Point3(0, 0, self.av.getHeight() + 2.5)

        gui = loader.loadModel('phase_3.5/models/gui/matching_game_gui')
        self.arrow = gui.find("**/minnieArrow")
        self.arrow.reparentTo(self.av)
        self.arrow.setHpr(0, 0, 90)
        self.arrow.setScale(10)
        self.arrow.setBillboardAxis()
        self.arrow.setColorScale(0, 0, 0, 0)
        self.arrow.hide()
        gui.removeNode()
        self.arrow.setPos(self.downPos)

    def cleanup(self, tellClientToExpire=True) -> None:
        super().cleanup(tellClientToExpire)

        if getattr(builtins, "simbase", None):
            return

        if self.arrowSeq:
            self.arrowSeq.finish()
            self.arrowSeq = None
        
        if self.arrow:
            self.arrow.removeNode()
            self.arrow = None

    def _doApply(self) -> None:
        self.fadeInArrow().finish()
        if self.arrow:
            self.arrow.show()
    
    def _doUnapply(self) -> None:
        self.fadeOutArrow().finish()
        if self.arrow:
            self.arrow.hide()

    def _doApplyMovie(self):
        if not self.battle:
            return Sequence(), Sequence()
        appSeq = Parallel(
            self.fadeInArrow(wantLerp=True),
        )
        camSeq = self.avProfile.battle.camera.allGroupOverheadShot(duration=80.0 / 24.0)
        return appSeq, camSeq
    
    def fadeInArrow(self, wantLerp=False):
        if not self.arrow:
            return Sequence()
        def startItLol():
            if not (self.arrow and not self.arrow.isEmpty()):
                return
            self.arrow.show()
            self.startArrowBounce()
            if wantLerp:
                self.lerpArrowColor()
            else:
                self.arrow.setColorScale(Vec4(self.getArrowColor(), 1))

        return Func(startItLol)
    
    def lerpArrowColor(self):
        if not self.arrow:
            return
        color = self.getArrowColor()
        Sequence(
            LerpColorScaleInterval(
                self.arrow, 0.4, Vec4(color, 1), startColorScale=self.arrow.getColorScale()
            ),
        ).start()

    def fadeOutArrow(self, wantLerp=False):
        if not self.arrow:
            return Sequence()
        color = self.getArrowColor()
        track = Parallel(Func(self.startArrowBounce))
        if wantLerp:
            seq = Sequence(
                LerpColorScaleInterval(self.arrow, 0.4, Vec4(color, 0))
            )
        else:
            seq = Func(self.arrow.setColorScale, Vec4(color, 0))
        track.append(seq)

        return track
    
    def startArrowBounce(self):
        if not self.arrow or not self.battle:
            return
        if hasattr(self.avProfile, 'battle'):
            self.arrowSeq = Sequence(
                LerpPosInterval(self.arrow, 2, self.upPos, startPos=self.downPos, blendType='easeInOut', fluid=1),
                LerpPosInterval(self.arrow, 2, self.downPos, startPos=self.upPos, blendType='easeInOut', fluid=1),
            )
            self.arrowSeq.setPlayRate(self.battle.timescale)
            self.accept(self.battle.uniqueName("battle_timeScaleUpdated"), self.updateArrowSeqPlayrate)
            self.arrowSeq.loop()

    def updateArrowSeqPlayrate(self, timescale):
        if self.arrowSeq is None:
            return

        t = self.arrowSeq.pause()
        self.arrowSeq.setPlayRate(timescale)
        self.arrowSeq.loop(t)

    def getArrowColor(self) -> None:
        return TrackColors[self.gagTrack]
    
    def setGagTrack(self, attackType: AttackEnum) -> None:
        self.gagTrack = attackType
    
    def resetVisual(self):
        if self.avProfile:
            rushJob = self.avProfile.getStatusEffectOfId(SEE.EFFECT_RUSH_JOB)
            if rushJob:
                self.gagTrack = int(rushJob.getTrack())


class FakeMultislackerVisualEffect(VisualEffectBase):
    """
    The visual effect for when the multislacker is off to the side going to town on his sandwich.
    """

    def __init__(self, avProfile, effectEnum, extraArgs) -> None:
        super().__init__(avProfile, effectEnum, extraArgs)
        self.associatedStatusEffectIds = [SEE.EFFECT_LUNCH_BREAK_MSLACKER]
        self.statusEffectMode = WANT_ONE
        self.removeDuringMovie = True
        # The fake suit itself that will be doing the funnies
        self.fakeSuit = None
        # Keep track of the funny sandwich that he will be eating
        self.sandwich = None

    def _doApply(self) -> None:
        """Applies the visual effect to the avatar."""
        if self.fakeSuit:
            self.fakeSuit.delete()

        # Create a fake suit that will stand off to the side and do his eating stuff
        from toontown.suit import Suit, SuitDNA, SuitHealthMeter
        self.fakeSuit = Suit.Suit()
        suitDNA = SuitDNA.SuitDNA()
        suitDNA.newSuit('mslacker')

        self.fakeSuit.setDNA(suitDNA)
        self.fakeSuit.addActive()
        self.fakeSuit.loop('lunch-loop')
        self.fakeSuit.specialHead.loop('lunch-loop')
        self.fakeSuit.hp = self.av.getHp()
        self.fakeSuit.maxHp = self.av.getMaxHp()
        self.fakeSuit.getHp = lambda: self.fakeSuit.hp
        self.fakeSuit.getMaxHp = lambda: self.fakeSuit.maxHp
        self.fakeSuit.healthInitialized = True
        self.fakeSuit.healthBar.updateMeterMode(SuitHealthMeter.MODE_BATTLE)
        self.fakeSuit.healthBar.updateHealthBar(forceUpdate=1)
        self.fakeSuit.getActualLevel = lambda: self.av.getActualLevel()
        self.fakeSuit.getStyleDept = lambda: self.av.getStyleDept()
        self.fakeSuit.setDisplayName(self.av.nametag.getDisplayName())
        self.fakeSuit.setPickable(0)

        self.fakeSuit.setPosHpr(-14.09718, -13.12119, 0.0, 157 + 180, 0, 0)
        self.fakeSuit.reparentTo(render)

        if self.sandwich:
            self.sandwich.removeNode()
        self.sandwich = loader.loadModel("phase_6/models/golf/picnic_sandwich.bam")
        self.sandwich.reparentTo(self.fakeSuit.getRightHand())
        self.sandwich.setScale(2)

        self.av.hide()

    def _doUnapplyMovie(self):
        if not self.battle:
            return
        from toontown.cutscene.repository.CutsceneLoader import CutsceneLoader

        # set cutscene dict
        cutsceneLoader = CutsceneLoader.createLoader(
            key=CutsceneKeyEnum.Multislacker_MandatoryLunch_End,
            multislacker=self.av,
            visualEffect=self
        )

        music = base.instance.getPreloadedSong('multislacker_battle')
        musicTrack = Func(
            base.musicMgr.crossfadeIntoMusic, music, 5.0, 0.5, 1, True, 1.0, 'multislacker_battle'
        )

        track = Sequence(
            musicTrack,
            cutsceneLoader.buildCutscene(),
            Func(self._doUnapply)
        )

        camSeq = Sequence(Wait(track.getDuration()))

        if hasattr(self.av, "battle"):
            camSeq.append(Func(base.camera.wrtReparentTo, self.av.battle))
            track.insert(0, Func(self.av.battle.instance.disableCartoon))

        return track, camSeq

    def _doUnapply(self) -> None:
        """Unapplies the visual effect from the avatar."""
        if self.sandwich:
            self.sandwich.removeNode()
            self.sandwich = None

        if self.fakeSuit:
            self.fakeSuit.delete()
            self.fakeSuit = None

        self.av.show()


class PropOrbitVisualEffect(VisualEffectBase):
    """
    Visual effect for orbiting battle props distributed evenly in a circle.
    """
    propScale = 1.0  # the base scale the prop is grown to in the apply movie

    def __init__(self, avProfile, effectEnum, extraArgs):
        super().__init__(avProfile, effectEnum, extraArgs)
        self.applyDuringMovie = True
        self._propNodes = []
        self._rotateNode = None
        self._spinSeq = None
        self._propSeq = None
        self._appearSeq = None
        self.count = 1
        self.orbitDuration = 5
        self.radius = 1
        self.propNames = ['cupcake']
        self.facePropsOutward = True

    def _propInterval(self, i: int, node: NodePath) -> Optional[Interval]:
        """
        Accepts an orbit index and a prop and returns an animation for it.
        """
        return None

    def _appearInterval(self, i: int, node: NodePath) -> Optional[Interval]:
        return None

    def _propPreTransform(self, i: int, node: NodePath) -> None:
        """
        This function should do whatever alignment you need to do to the prop before it's placed in orbit.
        """
        pass

    def __finishSeq(self):
        if self._spinSeq:
            self._spinSeq.finish()
            self._spinSeq = None
        if self._propSeq:
            self._propSeq.finish()
            self._propSeq = None
        if self._appearSeq:
            self._appearSeq.finish()
            self._appearSeq = None

    def __removeProps(self):
        from toontown.battle import MovieUtil
        for prop in self._propNodes:
            MovieUtil.removeProp(prop)
        self._propNodes = []
        if self._rotateNode:
            self._rotateNode.removeNode()
            self._rotateNode = None

    def _doApply(self) -> None:
        """Applies the visual effect to the avatar."""
        from toontown.battle.BattleProps import globalPropPool
        self.__finishSeq()
        self.__removeProps()
        # node that does the orbiting
        self._rotateNode = self.av.attachNewNode('prop-rotate-node')
        self._rotateNode.setZ(self.av.height * .33)
        # generate and position the props as well as their animation functions if provided
        propNamesCyclical = itertools.cycle(self.propNames)
        for i, propName in zip(range(self.count), propNamesCyclical):
            prop = globalPropPool.getProp(propName)
            self._propPreTransform(i, prop)
            self._propNodes.append(prop)
            prop.reparentTo(self._rotateNode)
            theta = math.tau * i / self.count
            x = self.radius * math.cos(theta)
            y = self.radius * math.sin(theta)
            prop.setPos(x, y, 0)
            if self.facePropsOutward:
                prop.setH(180 / math.pi * theta)
            propAnimation = self._propInterval(i, prop)
            if propAnimation is not None:
                if not self._propSeq:
                    self._propSeq = Parallel()
                self._propSeq.append(propAnimation)

            appearSeq = self._appearInterval(i, prop)
            if appearSeq is not None:
                if not self._appearSeq:
                    self._appearSeq = Parallel()
                self._appearSeq.append(appearSeq)

        if self._appearSeq:
            self._appearSeq.start()

        self._spinSeq = LerpHprInterval(
            self._rotateNode,
            self.orbitDuration,
            (360, 0, 0),
            startHpr=(0, 0, 0)
        )
        self._spinSeq.loop()
        if self._propSeq:
            self._propSeq.loop()

    def _doUnapply(self) -> None:
        """Unapplies the visual effect from the avatar."""
        self.__finishSeq()
        self.__removeProps()

    def _doApplyMovie(self):
        """Prop grows into existence."""
        def adjustNodeScale(value):
            if self._propNodes:
                for prop in self._propNodes:
                    prop.setScale(self.propScale * lerp(0.01, 1.0, value))

        appSeq = Sequence(
            Func(self._doApply),
            LerpFunctionInterval(adjustNodeScale, duration=0.3, fromData=0, toData=1, blendType='easeIn')
        )
        camSeq = Sequence()
        return appSeq, camSeq


class EncoreVisualEffect(PropOrbitVisualEffect):
    """
    Visual effect for the encore bonus when Toons use Prestige Sound
    """
    propScale = 0.18

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.statusEffectMode = WANT_ONE
        self.associatedStatusEffectIds = [SEE.EFFECT_ENCORE]
        self.propNames = ['bugle']
        self.orbitDuration = 5.0

    def _propPreTransform(self, _: int, node: NodePath) -> None:
        node.setScale(self.propScale)
        node.setP(30)

    def getDamageBoost(self):
        boost = self.extraArgs[0]
        for i in range(2):
            if boost == BattleGlobals.SoundAtkBonus[i]:
                return BattleGlobals.SoundAtkBonus[i]
        return boost

    def _doApply(self) -> None:
        """Applies the visual effect to the avatar."""
        self.count = 2 if self.getDamageBoost() == BattleGlobals.SoundAtkBonus[1] else 1
        super()._doApply()


class WindedVisualEffect(ParticleVisualEffect):
    particleName = 'reducedGagPower'
    cleanup_duration = 1.1
    wantEnum = SEE.EFFECT_WINDED

    def _doApply(self) -> None:
        """Applies the visual effect to the avatar."""
        from toontown.battle import BattleParticles
        self.particleSystem = BattleParticles.createParticleEffect(file=self.particleName)

        particles = self.particleSystem.getParticlesList()[0]
        r, g, b = BattleGlobals.TrackColors[AttackEnum.TOON_SOUND]
        particles.renderer.setColor(LVecBase4f(r, g, b, 1.0))

        self.particleSystem.start(parent=self.getParticleParent(), renderParent=self.av)


class CheerVisualEffect(ParticleVisualEffect, ToonsAccuracyUpVisualEffect):
    """smiles"""
    particleName = 'insured'
    cleanup_duration = 1.2
    wantEnum = SEE.EFFECT_CHEER

    def __init__(self, avProfile, effectEnum, extraArgs) -> None:
        ToonsAccuracyUpVisualEffect.__init__(self, avProfile, effectEnum, extraArgs)
        super().__init__(avProfile, effectEnum, extraArgs)

    def _doApply(self) -> None:
        super()._doApply()
        ToonsAccuracyUpVisualEffect._doApply(self)
    
    def _doUnapply(self) -> None:
        super()._doUnapply()
        ToonsAccuracyUpVisualEffect._doUnapply(self)


class PrethinkerBrainStormVisualEffect(VisualEffectBase):
    CloudPosHpr = [
        [(-2.17866, 10.80974, 13.44082), (0, 0, 0)],
        [(-11.2, 7.9, 12.4), (76.95438, 0.0, 0.0)],
        [(2.72331, 9.3573, 13.44081), (0, 0, 0)],
        [(6.89904, 7.36021, 13.25925), (-18.65558, 0.0, 0.0)],
        [(10.71168, 6.99709, 12.4), (-30.31549, 0.0, 0.0)],
        [(-6.89905, 8.99419, 14.53014), (38.31186, 0.0, 0.0)]
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.removeDuringMovie = True
        self.clouds = []
        self.sfxLoop = None

    def _doApply(self) -> None:
        if not self.battle:
            return

        from toontown.cutscene.repository.CutsceneObjects import PrethinkerBrainstormCloud
        self.cleanupClouds()

        if not self.sfxLoop:
            self.sfxLoop = loader.loadSfx('phase_9/audio/sfx/SA_forward_thinking_loop.ogg')
        base.playSfx(self.sfxLoop, looping=1)

        for i in range(len(self.CloudPosHpr)):
            cloud = PrethinkerBrainstormCloud(self.battle, isEditor=False)
            pos, hpr = self.CloudPosHpr[i]
            cloud.reparentTo(self.battle)
            cloud.setPos(pos)
            cloud.setHpr(hpr)
            cloud.geom.setScale(4)
            cloud.show()
            cloud.geom.show()
            cloud.startParticles()
            cloud.geom.loop('stormcloud', fromFrame=1*24)
            self.clouds.append(cloud)

    def softStopParticles(self):
        for cloud in self.clouds:
            for particle in cloud.snowEffects:
                particle.softStop()

    def _doUnapply(self) -> None:
        self.cleanupClouds()
        if self.sfxLoop:
            self.sfxLoop.stop()
            self.sfxLoop = None

    def _doUnapplyMovie(self):
        """
        Returns a sequence where this visual effect gets unapplied.
        To be played during the Battle Movie, if
        the self.removeDuringMovie is set to be True.
        """
        from toontown.battle import MovieUtil

        cloudScaleDown = Parallel()
        for cloud in self.clouds:
            cloudScaleDown.append(LerpScaleInterval(cloud, 1.0, MovieUtil.PNT3_NEARZERO, blendType='easeIn'))

        appSeq = Sequence(Func(self.softStopParticles), Wait(0.8), cloudScaleDown, Func(self._doUnapply))
        camSeq = self.avProfile.battle.camera.allGroupOverheadShot(duration=80.0 / 24.0)
        return appSeq, camSeq

    def cleanupClouds(self):
        for cloud in self.clouds:
            cloud.cleanup()
        self.clouds = []


class PowerNapVisualEffect(VisualEffectBase):
    def __init__(self, avProfile, effectEnum, extraArgs) -> None:
        super().__init__(avProfile, effectEnum, extraArgs)
        self.statusEffectMode = WANT_ONE
        self.associatedStatusEffectIds = [SEE.EFFECT_POWER_NAP, SEE.EFFECT_FTF_FOREMAN_SLEEPY_POWER_NAP]
        self.neutralHeadAnim = 'neutral-lured'
        self.priority = -100

    def makeThemSleep(self):
        from toontown.chat.constants.ChatGlobals import CFThought
        self.av.setChatAbsolute(TTLocalizer.ToonSleepString, CFThought, wantHeadAnim=False)

    def _doApply(self) -> None:
        self.makeThemSleep()

    def _doUnapply(self) -> None:
        self.av.clearChat()

    def onSuitAttackBegin(self):
        self.av.clearChat()

    def onSuitAttackEnd(self):
        self.makeThemSleep()


class BakeryAficionadoVisualEffect(PropOrbitVisualEffect):
    """Highly configurable orbiting cookie. Look upon the Mouthpiece's works."""

    class OrbitStyle:
        def __init__(self, amplitude: float = 0.3, orbitPhase: float = 0, floatyDuration: float = 2.0):
            self.amplitude = amplitude
            self.orbitPhase = orbitPhase
            self.floatyDuration = floatyDuration

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.statusEffectMode = WANT_ONE
        self.associatedStatusEffectIds = [SEE.EFFECT_MANAGER_MOUTHPIECE]
        self.propNames = ['cookie']
        self.orbitDuration = 5.0
        self.count = 8
        self.radius = 2
        self.randomFactor = random.random()
        self.style = self.OrbitStyle(amplitude=0.2, orbitPhase=random.randint(0, 359))
        self.cookieTextureIndices = [random.randint(1, 4) for _ in range(self.count)]

    def _propPreTransform(self, i: int, node: NodePath) -> None:
        # bake a random cookie
        cookieTexture = loader.loadTexture(f"phase_5/maps/battle_props/cc_t_prp_bat_mouthp_cookie_{self.cookieTextureIndices[i]}.png")
        node.setTexture(cookieTexture, 1)
        node.setH(360 * self.randomFactor)
        node.setZ(node, 1)
        node.setR(node, 90)
        node.setScale(.5 + 0.2 * self.randomFactor)

    def _propInterval(self, i: int, node: NodePath) -> Optional[Interval]:
        def hover(t: float):
            theta = math.tau * i / self.count
            z = self.style.amplitude * math.sin(math.tau * t + theta)
            node.setZ(z)
            node.setP(t * 360 + self.style.orbitPhase)
        return LerpFunctionInterval(hover, self.style.floatyDuration)

    def _appearInterval(self, i: int, node: NodePath) -> Optional[Interval]:
        bigScale = node.getScale() * 1.2
        return Sequence(
            Func(node.hide),
            Wait(i * 0.1),
            Func(node.show),
            LerpScaleInterval(node, 0.5, bigScale, 0.01, blendType='easeInOut'),
            LerpScaleInterval(node, 0.2, node.getScale(), bigScale, blendType='easeInOut')
        )

    def _doApply(self) -> None:
        super()._doApply()
        self._rotateNode.setH(self.style.orbitPhase)


class MouthpieceBonusVisualEffect(BakeryAficionadoVisualEffect):
    """
    Visual effect for a powerful confection bonus as delivered by the Mouthpiece.
    """
    def __init__(self, avProfile, effectEnum, extraArgs):
        super().__init__(avProfile, effectEnum, extraArgs)
        self.associatedStatusEffectIds = [SEE.EFFECT_MOUTHPIECE_BONUS]
        self.cookieTextureIndices = [int(extraArgs[0])]  # something is turning it into a float and i dont care to find out what
        self.count = 1


class RedThreadVisualEffect(VisualEffectBase):
    """Visual effect joining two avatars with red thread."""
    def __init__(self, avProfile, effectEnum, extraArgs):
        super().__init__(avProfile, effectEnum, extraArgs)
        self.associatedStatusEffectIds = [SEE.EFFECT_RED_THREAD, SEE.EFFECT_RED_THREAD_TANGLED]
        self.statusEffectMode = WANT_ONE
        if self.extraArgs:
            self.partner = extraArgs[0]
        self.acceptOnce(f'goneSad-{self.av.doId}', self._doUnapply)
        self.applyDuringMovie = True
        self.rope = None

    @property
    def partnerAv(self):
        return base.cr.doId2do.get(self.partner)

    def wantCombine(self, otherEffect) -> bool:
        return True

    def combine(self, otherEffect) -> None:
        # This thread wants whatever the other one's having
        self.partner = otherEffect.partner

    def _doApply(self) -> None:
        if None in (self.av, self.partnerAv):
            return
        if self.partnerAv.getHp() <= 0:
            return
        self.createRope()
        if self.battle:
            self.battle.addMovieHook(self, BMLE.EVENT_SUIT_DIED, self.suitDied)
            self.battle.addMovieHook(self, BMLE.EVENT_SUIT_PREDIED, self.suitAboutToDie)

    def _doUnapply(self) -> None:
        self.destroyRope()
        if self.battle:
            self.battle.removeMovieHooks(self)

    def _doApplyMovie(self):
        avFrom, avTo = random.sample((self.av, self.partnerAv), k=2)
        if None in (self.av, self.partnerAv):
            return Sequence(), Sequence()
        newSuitNode = self.getRopeNode(avTo)
        selfRopeNode = self.getRopeNode(avFrom)
        destPos = newSuitNode.getPos(selfRopeNode)

        def update(t):
            if self.rope is None:
                return

            x = lerp(0, destPos[0], t)
            y = lerp(0, destPos[1], t)
            z = lerp(0, destPos[2], t)
            self.rope.setup(
                2, (
                    (selfRopeNode, (0, 0, 0)),
                    (selfRopeNode, (x, y, z))
                )
            )

        def finalSetupRope():
            if self.rope is None or self.rope.isEmpty():
                return
            if None in (self.av, self.partnerAv):
                return

            self.rope.setup(2, (
                (self.getRopeNode(self.av), (0, 0, 0)),
                (self.getRopeNode(self.partnerAv), (0, 0, 0))
            ))

        return Sequence(
            Func(self._doApply),
            LerpFunctionInterval(update, duration=1.0, blendType='easeIn'),
            Func(finalSetupRope),
        ), Sequence()

    @staticmethod
    def getRopeNode(av):
        if av.isToon():
            return av.getTorsoParts()[0]
        elif av.isSuit():
            return av.find('**/joint_attachMeter') if av.isSkeleton else av.healthBar.hpParts[0]
        return av

    def createRope(self):
        if self.battle is None or None in (self.av, self.partnerAv):
            return
        self.destroyRope()
        self.rope = Rope(name='redThreadRope')
        self.rope.reparentTo(self.av)
        self.rope.setup(
            2,
            (
                (self.getRopeNode(self.av), (0, 0, 0)),
                (self.getRopeNode(self.partnerAv), (0, 0, 0)),
            )
        )
        self.rope.ropeNode.setRenderMode(RopeNode.RMBillboard)
        self.rope.ropeNode.setUvMode(RopeNode.UVDistance)
        self.rope.ropeNode.setUvDirection(0)
        self.rope.ropeNode.setUvScale(.5)
        self.rope.ropeNode.setThickness(.5)
        self.rope.setTexture(loader.loadTexture('phase_5/maps/battle_props/cc_t_ene_mouthpiece_redthread.png'))
        self.rope.setTransparency(1)

    def destroyRope(self):
        if self.rope is None:
            return
        self.rope.removeNode()

    def suitDied(self, seq: Sequence, suit):
        if suit is not self.partnerAv:
            return
        seq.append(Func(self._doUnapply))

    def suitAboutToDie(self, seq: Sequence, suit):
        if self.rope is None:
            return

        def tryHideRope():
            if self.rope is not None and not self.rope.isEmpty():
                self.rope.hide()

        if suit is not self.partnerAv:
            return
        seq.append(Sequence(Func(tryHideRope)))

    def doHpTextOverride(self, *args, **kwargs):
        text, color = TTLocalizer.GeneralAttackHpTexts[TTLocalizer.HP_TEXT_RED_THREAD]
        if kwargs.get('extraText') == text:
            self.av.showHpString(text.format(args[0]), color=color)
            return True
        return False


class BackBurnerVisualEffect(ParticleVisualEffect):
    particleName = 'firestarterBackburnerEffect'
    wantEnum = SEE.EFFECT_BACKBURNER
    cleanup_duration = 1.8

    def _doApply(self) -> None:
        super()._doApply()
        # 1.268 is toxic manager size :)
        if self.av and self.av.style.body == 'c' and self.av.scale > 1.268:
            self.particleSystem.getParticlesNamed('particles-1').emitter.setRadius((self.av.scale / 1.268) * 0.3)


class BewitchmentVisualEffect(ParticleVisualEffect):
    particleName = 'ocforeman'
    wantEnum = SEE.EFFECT_BEWITCHMENT

    def __init__(self, avProfile, effectEnum, extraArgs) -> None:
        super().__init__(avProfile, effectEnum, extraArgs)
        self.applyDuringMovie = True
        self.removeDuringMovie = True
        if self.client:
            self.item = InventoryItem.fromSubtype(HatItemType.Hat_Wizard_Enchanted_Stars_Black)

    def _poof(self) -> Sequence:
        poof = DustCloud.DustCloud()
        poof.setZ(3)
        poof.setScale(.33)
        poof.createTrack()
        return Sequence(Func(poof.reparentTo, self.avProfile),
                        poof.track,
                        Func(poof.destroy))

    def _doApply(self) -> None:
        if self.av is None:
            return

        self.av.addAccessory(self.item)
        super()._doApply()

    def _doUnapply(self) -> None:
        if self.av is None:
            return

        self.av.removeAccessory(self.item)
        super()._doUnapply()

    def _doApplyMovie(self):
        apply = Parallel(self._poof(), Func(self._doApply))
        cam = Sequence()
        return apply, cam

    def _doUnapplyMovie(self):
        apply = Parallel(self._poof(), Func(self._doUnapply))
        cam = Sequence()
        return apply, cam


class SlushFundVisualEffect(AvatarSoakedVisualEffect):
    """
    Lovingly plagiarized from Soaked.
    """
    tint = (1.0, 1.0, 1.0, 1.0)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.associatedStatusEffectIds = [SEE.EFFECT_SLUSH_FUND]
        self.statusEffectMode = WANT_ONE
        self.applyDuringMovie = False
        self.removeDuringMovie = False

    def _doApply(self) -> None:
        super()._doApply()
        from toontown.battle import BattleParticles
        BattleParticles.setEffectTexture(self.particleSystem, 'dollar-sign', color=(.5 * random.random() + .3, .8, 1, 1))


class MarketBubbleVisualEffect(VisualEffectBase):
    """The visual effect for Plutocrat's Market Bubble status.
    Lovingly adapted from Disruptive Advertisement.
    """

    def __init__(self, avProfile, effectEnum, extraArgs) -> None:
        super().__init__(avProfile, effectEnum, extraArgs)
        self.associatedStatusEffectIds = [SEE.EFFECT_MANAGER_PLUTOCRAT]
        self.statusEffectMode = WANT_ONE
        self.displayNode = None
        self.bubble = None
        self.displaySeq = None

    def _doApply(self) -> None:
        if self.displaySeq:
            self.displaySeq.finish()
            self.displaySeq = None

        plutoStatus = self.avProfile.getStatusEffectOfId(SEE.EFFECT_MANAGER_PLUTOCRAT)
        bubbleStacks: int = plutoStatus.marketBubbleStacks
        if bubbleStacks == 0:
            # bubble inactive
            return
        elif bubbleStacks <= -1:
            # bubble popped, vulnerable
            part = self.av.getGeomNode()
            self.displaySeq = Sequence(
                LerpColorScaleInterval(part, 0.5, (1.0, .66, .66, 1.0), blendType='easeInOut'),
                LerpColorScaleInterval(part, 0.5, (1.0, 1.0, 1.0, 1.0), blendType='easeInOut'),
            )
            self.displaySeq.loop()
        else:
            # bubble up
            self.displayNode = self.av.attachNewNode('displayNode')
            self.displayNode.setTransparency(1)
            self.displayNode.setColorScale(0.0, 1.0, 0.0, 0.4)
            self.displayNode.setDepthWrite(False)
            # self.displayNode.setDepthTest(False)

            def updateBubble():
                if self.bubble and not self.bubble.isEmpty():
                    self.bubble.removeNode()
                    self.bubble = None

                from toontown.suit.SuitDefinitionsBase import SuitDefinitions
                plutoHeight = SuitDefinitions['pcrat'].bodyHeight
                sphere = base.loader.loadModel('phase_3/models/misc/sphere')
                self.bubble = sphere.copyTo(self.displayNode)
                self.bubble.setPos(self.av, 0, 0, plutoHeight / 2)

            self.displaySeq = Sequence(
                Func(self.displayNode.setScale, 2.5),
                Func(self.displayNode.setColorScale, (0.0, 1.0, 0.0, 0.2)),
                Func(updateBubble),
                Parallel(
                    LerpScaleInterval(self.displayNode, 1.0, 2.5 + .2 * bubbleStacks, blendType='easeOut'),
                    LerpColorScaleInterval(self.displayNode, 0.7, (0.0, 1.0, 1.0, 0.0), blendType='easeOut')
                ),
                Wait(0.7),
            )
            self.displaySeq.loop()

    def _doUnapply(self) -> None:
        if self.displaySeq:
            self.displaySeq.finish()
            self.displaySeq = None

        if self.displayNode:
            self.displayNode.removeNode()
            self.displayNode = None


class ChainLinkedVisualEffect(VisualEffectBase):
    def __init__(self, avProfile, effectEnum, extraArgs):
        super().__init__(avProfile, effectEnum, extraArgs)
        self.associatedStatusEffectIds = [SEE.EFFECT_CHAIN_LINKED]
        self.statusEffectMode = WANT_ONE
        self.rightSuit = None

    def _doApply(self) -> None:
        self.createRope()
        if self.battle:
            self.battle.addMovieHook(self, BMLE.EVENT_SUIT_DIED, self.changeChainTarget)
            self.battle.addMovieHook(self, BMLE.EVENT_SUIT_PREDIED, self.suitAboutToDie)

    def _doUnapply(self) -> None:
        self.destroyRope()
        if self.battle:
            self.battle.removeMovieHooks(self)

    @staticmethod
    def getRopeNode(suit):
        return suit.find('**/joint_attachMeter') if suit.isSkeleton else suit.healthBar.hpParts[0]

    def createRope(self, suit=None):
        # Don't create the rope for the very right suit.
        if not self.battle:
            return
        suitIndex = self.battle.suits.index(self.av)
        if suitIndex <= 0:
            return

        self.rightSuit = suit or self.battle.suits[suitIndex - 1]
        self.rope = Rope(name='supportChain')
        self.rope.reparentTo(self.av)
        self.rope.setup(
            2,
            (
                (self.getRopeNode(self.av), (0, 0.5, 0)),
                (self.getRopeNode(self.rightSuit), (0, 0.5, 0))
            )
        )
        self.rope.ropeNode.setRenderMode(RopeNode.RMBillboard)
        self.rope.ropeNode.setUvMode(RopeNode.UVDistance)
        self.rope.ropeNode.setUvDirection(0)
        self.rope.ropeNode.setUvScale(2.0)
        self.rope.ropeNode.setThickness(0.5)
        self.rope.setTexture(loader.loadTexture('phase_9/maps/sellbotHQ/ttcc_sellbotHQ_boss_chain.png'))
        self.rope.setTransparency(1)

    def suitAboutToDie(self, seq: Sequence, suit):
        if not hasattr(self, 'rope'):
            return

        def tryHideRope():
            if hasattr(self, 'rope') and not self.rope.isEmpty():
                self.rope.hide()

        if suit and (suit is self.av or suit is self.rightSuit):
            seq.append(Sequence(Func(tryHideRope)))

    def changeChainTarget(self, seq: Sequence, suit):
        if self.av is suit:
            return
        if suit is not self.rightSuit:
            return
        if not self.battle:
            return

        newSuit = None
        indexMod = 2
        while newSuit is None:
            newSuitIndex = self.battle.suits.index(self.av) - indexMod
            if newSuitIndex < 0:
                return

            nextSuit = self.battle.suits[newSuitIndex]
            if getattr(nextSuit, 'deadOrAboutToBe', False):
                indexMod += 1
                continue
            newSuit = nextSuit
            break

        newSuitNode = self.getRopeNode(newSuit)
        selfRopeNode = self.getRopeNode(self.av)
        destPos = newSuitNode.getPos(selfRopeNode)

        def update(t):
            x = lerp(0.01, destPos[0], t)
            y = lerp(0.5, destPos[1], t)
            z = lerp(0, destPos[2], t)
            self.rope.setup(
                2, (
                    (selfRopeNode, (0, 0.5, 0,)),
                    (selfRopeNode, (x, y, z))
                )
            )

        def tryShowRope():
            if hasattr(self, 'rope') and not self.rope.isEmpty():
                self.rope.show()

        def finalSetupRope():
            if hasattr(self, 'rope') and not self.rope.isEmpty():
                self.rope.setup(2, (
                    (self.getRopeNode(self.av), (0, 0.5, 0)),
                    (self.getRopeNode(newSuit), (0, 0.5, 0))
                ))

        chainSfx = loader.loadSfx('phase_5/audio/sfx/CHQ_SOS_cage_lower.ogg')
        seq.append(
            Sequence(
                Func(tryShowRope),
                Func(base.playSfx, chainSfx, looping=1),
                LerpFunctionInterval(update, duration=0.4, blendType='easeIn'),
                Func(finalSetupRope),
                Func(chainSfx.stop),
                Wait(0.5),
            ),
        )

    def destroyRope(self):
        if not hasattr(self, "rope"):
            return
        self.rope.removeNode()
        del self.rope


class SparkPlugVisualEffect(ParticleVisualEffect):
    particleName = 'chainsawSparkPlugEffect'
    wantEnum = SEE.EFFECT_SPARK_PLUG

    def __init__(self, avProfile, effectEnum, extraArgs):
        super().__init__(avProfile, effectEnum, extraArgs)
        self.applyDuringMovie = True

    def getParticleParent(self):
        if self.particleNode:
            return self.particleNode
        return self.av

    def _doApply(self) -> None:
        self.particleNode = self.av.attachNewNode('sparkParticleNode')
        self.particleNode.setZ(self.av.getHeight() / 2)
        super()._doApply()

    def _doUnapply(self) -> None:
        self.particleNode.removeNode()
        self.particleNode = None
        super()._doUnapply()


class JoggingVisualEffect(BlankVisualEffect):
    """
    A visual effect that makes a Suit start jogging.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.animationOverrides = {'neutral': 'pace'}

    def _doUnapply(self) -> None:
        self.animationOverrides = {}
        super()._doUnapply()


class RolledVisualEffect(BlankVisualEffect):
    """
    A visual effect that makes a Suit start dancing like our dear friend Major Player.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.animationOverrides = {'neutral': 'rolled'}

    def _doUnapply(self) -> None:
        self.animationOverrides = {}
        super()._doUnapply()


class FTFAttorneyJoggingEffect(JoggingVisualEffect):
    """
    Jogging visual, but just for the FTF attorney
    """
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.associatedStatusEffectIds = [SEE.EFFECT_FTF_ATTORNEY_CHRONO]


class HighRollerTriviaVisualEffect(VisualEffectBase):
    def __init__(self, avProfile, effectEnum, extraArgs) -> None:
        super().__init__(avProfile, effectEnum, extraArgs)
        self.associatedStatusEffectIds = [SEE.EFFECT_TRIVIA, SEE.EFFECT_SHUFFLE]
        self.statusEffectMode = WANT_ONE

    def _doApply(self) -> None:
        """Applies the visual effect to the avatar."""
        self.av.setDisplayName(self.getName())
        self.av.setPickable(0)

    def _doUnapply(self):
        return

    @property
    def triviaStatus(self):
        return self.avProfile.getStatusEffectOfId(SEE.EFFECT_TRIVIA)

    @property
    def shuffleStatus(self):
        return self.avProfile.getStatusEffectOfId(SEE.EFFECT_SHUFFLE)

    @property
    def isCorrect(self):
        status = self.triviaStatus or self.shuffleStatus
        if not status:
            return False
        return status.isAnswerCorrect()

    def getName(self):
        if not self.triviaStatus:
            return "???"
        return self.triviaStatus.getName()

    def doHpTextOverride(self, *args, **kwargs):
        if 'bonus' in kwargs and kwargs['bonus'] != 0:
            # Don't show any bonus text of any kind on these guys
            return True

        if self.isCorrect:
            self.av.showHpString('CORRECT!', color=(0, 0.9, 0, 1))
        else:
            self.av.showHpString('INCORRECT!', color=(0.9, 0, 0, 1))
        return True


class HighRollerCloneVisualEffect(VisualEffectBase):
    def __init__(self, avProfile, effectEnum, extraArgs) -> None:
        super().__init__(avProfile, effectEnum, extraArgs)
        self.associatedStatusEffectIds = [SEE.EFFECT_HIGHROLLER_CLONE]
        self.statusEffectMode = WANT_ONE
        self.applyDuringMovie = True
        self.setUnapplyLock(True)

    def _doApply(self) -> None:
        """Applies the visual effect to the avatar."""
        from toontown.instances import HighRollerGlobals
        visualDict = HighRollerGlobals.CloneType2Visuals
        actorNode = self.av.find('**/__Actor_modelRoot')
        actorCollection = actorNode.findAllMatches('*')
        for part in self.av.headParts:
            part.setTwoSided(False)

        color = visualDict[self.getType()][0]

        for thing in actorCollection:
            if thing.getName() not in ('joint_attachMeter', 'joint_nameTag', 'def_nameTag'):
                thing.setColorScale(color)
                thing.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd, ColorBlendAttrib.OIncomingAlpha, ColorBlendAttrib.OOne))
                # thing.setAttrib(TransparencyAttrib.make(TransparencyAttrib.MAlpha))
                thing.setDepthWrite(False)
                thing.setBin('fixed', 1)
        self.av.setDisplayName(visualDict[self.getType()][1] + "\nCashbot\nLevel 25.mgr")

    def getType(self):
        if len(self.extraArgs) < 1:
            return random.randint(0, 7)
        return self.extraArgs[0]


class HighRollerCommercialVisualEffect(VisualEffectBase):
    """
    The visual effect for when the multislacker is off to the side going to town on his sandwich.
    """

    def __init__(self, avProfile, effectEnum, extraArgs) -> None:
        super().__init__(avProfile, effectEnum, extraArgs)
        self.associatedStatusEffectIds = [SEE.EFFECT_COMMERCIAL]
        self.statusEffectMode = WANT_ONE
        # The fake suit itself that will be doing the funnies
        self.fakeSuit = None

    def _doApply(self) -> None:
        """Applies the visual effect to the avatar."""
        if self.fakeSuit:
            self.fakeSuit.delete()

        from toontown.suit import DistributedSuitBase, SuitDNA, SuitHealthMeter
        self.fakeSuit = DistributedSuitBase.DistributedSuitBase(base.cr)
        suitDNA = SuitDNA.SuitDNA()
        suitDNA.newSuit('hroller')

        nextLocalDoId = -2450

        self.fakeSuit.setDNA(suitDNA)
        self.fakeSuit.doId = nextLocalDoId
        nextLocalDoId -= 1
        self.fakeSuit.generate()
        self.fakeSuit.addActive()
        self.fakeSuit.loop('neutral')
        self.fakeSuit.specialHead.loop('neutral')
        self.fakeSuit.hp = self.av.getHp()
        self.fakeSuit.maxHp = self.av.getMaxHp()
        self.fakeSuit.getHp = lambda: self.fakeSuit.hp
        self.fakeSuit.getMaxHp = lambda: self.fakeSuit.maxHp
        self.fakeSuit.healthInitialized = True
        self.fakeSuit.healthBar.updateMeterMode(SuitHealthMeter.MODE_BATTLE)
        self.fakeSuit.healthBar.updateHealthBar(forceUpdate=1)
        self.fakeSuit.getActualLevel = lambda: self.av.getActualLevel()
        self.fakeSuit.getStyleDept = lambda: self.av.getStyleDept()
        self.fakeSuit.setDisplayName(self.av.nametag.getDisplayName())
        self.fakeSuit.setPickable(0)

        self.fakeSuit.setPosHpr(16.77753, 26.03724, 4.0, 157, 0, 0)
        self.fakeSuit.reparentTo(render)

        self.av.hide()

    def _doUnapply(self) -> None:
        """Unapplies the visual effect from the avatar."""
        if self.fakeSuit:
            self.fakeSuit.delete()
            self.fakeSuit = None

        self.av.show()


class HRUntouchableVisualEffect(ParticleVisualEffect):
    """
    Fake effect for HR's untouchable effect.
    """
    particleName = 'hr_rainbowfeet'

    OFFSET = Vec3(0, 2.5, 0)

    def __init__(self, avProfile, effectEnum, extraArgs) -> None:
        super().__init__(avProfile, effectEnum, extraArgs)
        self.associatedStatusEffectIds = [SEE.EFFECT_HR_UNTOUCHABLE]
        self.statusEffectMode = WANT_ONE

        self.applyDuringMovie = True

        # The fake suit itself that will be doing the funnies
        self.fakeSuit = None

    def getParticleParent(self):
        memoryLeak = NodePath('not-a-memory-leak')
        memoryLeak.reparentTo(self.battle)
        memoryLeak.setPos(self.av.getPos(self.battle) + self.OFFSET)
        return memoryLeak

    def getParticleRenderParent(self):
        return render

    def _doApplyMovie(self):
        def translateFakeSuit():
            self.fakeSuit.setPlayRate(0.75, 'hr-fusion-shot5')
            Sequence(
                Func(
                    self.fakeSuit.setBlend,
                    frameBlend=base.wantSmoothAnims,
                    animBlend=True,
                ),
                Func(self.fakeSuit.stop),
                Parallel(
                    ActorInterval(
                        self.fakeSuit, 'neutral', duration=1.0,
                    ),
                    ActorInterval(
                        self.fakeSuit, 'hr-fusion-shot5', duration=1.0, endFrame=11, playRate=0.75,
                    ),
                    LerpAnimInterval(
                        self.fakeSuit, 1.0, 'neutral', 'hr-fusion-shot5', blendType='easeOut',
                    ),
                    LerpPosInterval(
                        self.fakeSuit, 1.0, self.av.getPos(self.battle) + Vec3(0, 20, -4) + self.OFFSET, startPos=self.av.getPos(self.battle), blendType='easeOut',
                    )
                ),
                Func(
                    self.fakeSuit.setBlend,
                    frameBlend=base.wantSmoothAnims,
                    animBlend=False,
                ),
                Func(self.fakeSuit.setPlayRate, 0.75, 'hr-fusion-shot5'),
                Func(self.fakeSuit.pingpong, 'hr-fusion-shot5', restart=0, fromFrame=0, toFrame=11),
            ).start()

        seq = Sequence(
            Func(self._doApply),
            Func(translateFakeSuit),
        )
        camSeq = Sequence(Wait(seq.getDuration()))
        return seq, camSeq

    def _doApply(self) -> None:
        """Applies the visual effect to the avatar."""
        if self.fakeSuit:
            self.fakeSuit.delete()

        # Create a fake suit that will become God and do his floating stuff
        from toontown.suit import Suit, SuitDNA, SuitHealthMeter
        self.fakeSuit = Suit.Suit()
        suitDNA = SuitDNA.SuitDNA()
        suitDNA.newSuit('hroller')
        self.fakeSuit.setDNA(suitDNA)

        self.fakeSuit.addActive()
        self.fakeSuit.setPlayRate(0.75, 'hr-fusion-shot5')
        self.fakeSuit.pingpong('hr-fusion-shot5', fromFrame=0, toFrame=11)
        self.fakeSuit.specialHead.loop('neutral')
        self.fakeSuit.hp = self.av.getHp()
        self.fakeSuit.maxHp = self.av.getMaxHp()
        self.fakeSuit.getHp = lambda: self.fakeSuit.hp
        self.fakeSuit.getMaxHp = lambda: self.fakeSuit.maxHp
        self.fakeSuit.healthInitialized = True
        self.fakeSuit.healthBar.updateMeterMode(SuitHealthMeter.MODE_BATTLE)
        self.fakeSuit.healthBar.updateHealthBar(forceUpdate=1)
        self.fakeSuit.getActualLevel = lambda: self.av.getActualLevel()
        self.fakeSuit.getStyleDept = lambda: self.av.getStyleDept()
        self.fakeSuit.setDisplayName(self.av.nametag.getDisplayName())
        self.fakeSuit.setPickable(0)

        bodyTex = loader.loadTexture('phase_12/maps/cc_t_ene_highroller_suit_black.png')
        bodyTex.setMinfilter(Texture.FTLinearMipmapLinear)
        bodyTex.setMagfilter(Texture.FTLinear)

        self.fakeSuit.find('**/body').setTexture(bodyTex, 1)
        self.fakeSuit.find('**/hands').setTexture(bodyTex, 1)

        hrBodyTex = loader.loadTexture('phase_12/maps/cc_t_ene_highroller_body_black.png')
        hrBodyTex.setMinfilter(Texture.FTLinearMipmapLinear)
        hrBodyTex.setMagfilter(Texture.FTLinear)

        self.fakeSuit.find('**/highroller_body').setTexture(hrBodyTex, 1)

        self.fakeSuit.reparentTo(self.battle)
        self.fakeSuit.setPos(self.av.getPos(self.battle) + Vec3(0, 20, -4) + self.OFFSET)
        self.fakeSuit.setHpr(180, 0, 0)

        self.fakeSuit.setPlayRate(0.75, 'hr-fusion-shot5')
        self.fakeSuit.pingpong('hr-fusion-shot5', restart = 0, fromFrame = 0, toFrame = 11)

        self.av.hide()

        super()._doApply()

    def getUnapplyMovie(self):
        track = Sequence(
            Func(super()._doUnapply),
            Func(
                self.fakeSuit.setBlend,
                frameBlend=base.wantSmoothAnims,
                animBlend=True,
            ),
            Func(self.fakeSuit.stop),
            Parallel(
                ActorInterval(
                    self.fakeSuit, 'neutral', duration=1.0,
                ),
                ActorInterval(
                    self.fakeSuit, 'hr-fusion-shot5', duration=1.0, playRate=0.75,
                ),
                LerpAnimInterval(
                    self.fakeSuit, 1.0, 'hr-fusion-shot5', 'neutral', blendType='easeOut',
                ),
                LerpPosInterval(
                    self.fakeSuit, 1.0, self.av.getPos(self.battle), startPos=self.av.getPos(self.battle) + Vec3(0, 20, -4) + self.OFFSET, blendType='easeOut',
                )
            ),
            Func(
                self.fakeSuit.setBlend,
                frameBlend=base.wantSmoothAnims,
                animBlend=False,
            ),
            Func(self.fakeSuit.loop, 'neutral', restart=0),
            Func(self._doUnapply),
        )
        camSeq = self.avProfile.battle.camera.allGroupOverheadShot(duration=80.0 / 24.0)

        return track, camSeq

    def _doUnapply(self) -> None:
        """Unapplies the visual effect from the avatar."""
        if self.fakeSuit:
            self.fakeSuit.delete()
            self.fakeSuit = None

        self.av.show()
        super()._doUnapply()

    def cleanup(self, tellClientToExpire=True) -> None:
        if self.fakeSuit:
            self.fakeSuit.delete()
            self.fakeSuit = None
        super()._doUnapply()


class ConfusionVisualEffect(MultiParticleVisualEffect):
    """smiles"""
    particleNames = ['confusionVisualEffect', 'confusionVisualEffectSilver']
    cleanup_duration = 1.2
    wantEnum = SEE.EFFECT_FTF_PRESIDENT_PUZZLING_CONFUSED

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.particleNode = None

    def getParticleParent(self):
        if self.particleNode:
            return self.particleNode
        return self.av

    def _doApply(self) -> None:
        if not self.particleNode:
            self.particleNode = self.av.attachNewNode('sparkParticleNode')
            self.particleNode.setZ(self.av.getHeight() / 2)
        super()._doApply()

    def _doUnapply(self) -> None:
        super()._doUnapply()
        if self.particleNode:
            self.particleNode.removeNode()
            self.particleNode = None


class ChainsawOverrideVisualEffect(VisualEffectBase):
    def _doApply(self):
        self.animationOverrides = {
            'neutral': 'neutral-override',
            'true-neutral': 'neutral',
        }

    def _doUnapply(self):
        self.animationOverrides = {}


class ChainsawOverrideGlitchedVisualEffect(VisualEffectBase):
    def _doApply(self):
        self.animationOverrides = {
            'neutral': 'neutral-override-glitched',
            'true-neutral': 'neutral',
        }

    def _doUnapply(self):
        self.animationOverrides = {}
