import math
import random
from typing import List, Optional, Union

from toontown.toonbase import ToontownGlobals
from toontown.clashbattle.battle import BattleGlobals
from toontown.clashbattle.battle.BattleAvatar import BattleAvatar
from toontown.clashbattle.battle.BattleEventGlobals import BEG
from toontown.clashbattle.battle.BattleGlobals import BattleOrderPriority
from toontown.clashbattle.battle.BattleListenerObject import BattleListenerObject
from toontown.clashbattle.battle.attacks.base.AttackEnum import AttackEnum
from toontown.clashbattle.battle.environmental.base.EnvironmentalEnum import ENV_ENUM, EnvironmentalEnum,\
     PlutocratWeather, RainmakerWeather
from toontown.clashbattle.battle.environmental.server.EnvironmentalRepository import EnvironmentalClass
from toontown.clashbattle.battle.statuses.StatusEffectEnums import SEE
from toontown.clashbattle.battle.statuses.StatusEffects import DrenchStatusEffect, SoakStatusEffect, StatusEffectBase, \
    CogStatusEffect
from toontown.clashbattle.battle.visuals.VisualEffectEnums import VisualEffectEnum
from toontown.events.apriltoons.findthefamily import FindTheFamilyGlobals
from toontown.modifiers.contentsync.ContentSyncEnums import ContentSyncType
from toontown.clashsuit.suit.DistributedSuitAI import DistributedSuitAI
from toontown.clashsuit.suit.DistributedSuitBaseAI import DistributedSuitBaseAI
from toontown.clashsuit.suit import SuitDNA
from toontown.toon.DistributedToonBaseAI import DistributedToonBaseAI

from typing import TYPE_CHECKING

from toontown.utils import AIUtil

if TYPE_CHECKING:
    from toontown.clashbattle.battle.distributed.DistributedBattleBaseAI import DistributedBattleBaseAI
    from toontown.clashbattle.battle.BattleListenerAI import BattleListenerAI


NORMAL = 0
OVERCLOCKED = 1


class EnvironmentalBase(BattleListenerObject):
    """
    EnvironmentalBase: The base class for all environmental functionality.

    :param rounds: The amount of rounds the environmental should last
    for before it expires.
    :param extraArgs: Extra arguments for the environmental to use.
    """

    __slots__ = (
        # General parameters.
        "environmentalType", "rounds", "battleListener",
        "cleanedUp", "battle",
    )

    def __init__(self, battle, battleListener, rounds: int = -1, **kwargs) -> None:
        self.environmentalType = self.environmentalType or tuple()
        self.setRounds(rounds, adjust=True)

        # Inherited battle event definitions.
        self.inheritedEventDefinitions = [ENV_ENUM.BASE]

        # Variables set by the battle.
        self.battle = battle  # type: DistributedBattleBaseAI
        self.battleListener = battleListener  # type: BattleListenerAI
        self.setParticipants([], [])

        self.cleanedUp = False
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(environmentalType={self.environmentalType})"
    
    def setParticipants(self, toons: list, suits: list) -> None:
        self.toons = toons  # type: List[DistributedToonBaseAI]
        self.suits = suits  # type: List[DistributedSuitBaseAI]
    
    def setRounds(self, rounds: int, adjust: bool = False) -> None:
        self.rounds = rounds
        if rounds != -1 and adjust:
            self.rounds += 1
        
    def getRounds(self) -> int:
        return self.rounds
    
    def decrement(self, amount: int = 1) -> None:
        if self.rounds == -1:
            return

        self.rounds -= amount
        if self.rounds == -1:
            self.destroy()
    
    def cleanup(self) -> None:
        if self.cleanedUp:
            return
        
        self.cleanedUp = True

        del self.battleListener
        del self.environmentalType
        del self.inheritedEventDefinitions
        del self.battle
    
    def destroy(self) -> None:
        self.sendEvent(BEG.EVENT_DESTROY_ENVIRONMENTAL, [self])
        self.cleanup()
    
    """
    Various methods which allow environmentals to interact with the battle.

    These methods will do nothing by default, and any special functionality
    should be defined in children classes.
    """

    def handleBaseDamage(self, attackType: AttackEnum, damageAmount: int, target: BattleAvatar, attack):
        return damageAmount

    def handleComboDamage(self, attackType: AttackEnum, damageAmount: int, target: BattleAvatar, attack):
        return damageAmount

    def handleKnockbackDamage(self, attackType: AttackEnum, damageAmount: int, target: BattleAvatar, attack):
        return damageAmount

    def handleDamageTaken(self, target: BattleAvatar, invoker: BattleAvatar, 
                          damageAmount: int, attackType: AttackEnum):
        return damageAmount

    """
    Other useful events that we listen to
    """

    def handleToonAddedToBattle(self, toon: DistributedToonBaseAI):
        if toon not in self.toons:
            self.toons.append(toon)

    def handleSuitAddedToBattle(self, suit: DistributedSuitBaseAI):
        if suit not in self.suits:
            self.suits.append(suit)

    def handleToonRemovedFromBattle(self, toon: DistributedToonBaseAI):
        if toon in self.toons:
            self.toons.remove(toon)

    def handleSuitRemovedFromBattle(self, suit: DistributedSuitBaseAI):
        # Let subclasses override this function.
        pass

    def handleBattleEnd(self):
        pass
    
    """
    Utility methods
    """

    def getBattleListener(self):
        return self.battleListener

    def createAttack(self, attackType: AttackEnum=None, attackKwargs: dict=None,
                     insertKwargs: dict=None) -> None:
        attackKwargs = attackKwargs or {}
        insertKwargs = insertKwargs or {}

        self.sendEvent(BEG.EVENT_CREATE_INSERT_ATTACK, [
            attackType, attackKwargs, insertKwargs
        ])


@EnvironmentalClass(EnvironmentalEnum.PERSISTENT_STATUS_EFFECTS)
class PersistentStatusEffectEnvironmental(EnvironmentalBase):
    """
    A base class to make it easier to deal with applying
    persistent status effects in battle.

    Effects are constantly managed by the environmental effect.
    This allows for persistent status effects on Toons and Suits that
    entirely depend on the existence of this environmental effect.
    """

    __slots__ = 'cleanupEffectsOnDelete', 'managedEffects'

    def __init__(self, cleanupEffectsOnDelete: bool = True, **kwargs) -> None:
        """
        Initializes the persistent status effect environmental effect.
        """
        self.cleanupEffectsOnDelete = cleanupEffectsOnDelete
        self.managedEffects: List[StatusEffectBase] = []
        super().__init__(**kwargs)

    def destroy(self) -> None:
        """
        Cleans up the environmental effect.
        """
        # Delete all managed effects, should we desire.
        if self.cleanupEffectsOnDelete:
            self.cleanupManagedEffects()
        del self.managedEffects

        # Ensure complete destruction.
        super().destroy()

    """
    Updates
    """

    def setParticipants(self, toons: list, suits: list) -> None:
        """
        Whenever the battle participants are set for the turn,
        let's make sure that they have all the effects applied as well.
        """
        super().setParticipants(toons, suits)
        self.updateAppliedEffects()

    def handleToonAddedToBattle(self, toon: DistributedToonBaseAI) -> None:
        """
        A new battle member being added -> refresh the active effects.
        :param toon: The Toon being added into battle.
        """
        super().handleToonAddedToBattle(toon)
        self.updateAppliedEffects()

    def handleSuitAddedToBattle(self, suit: DistributedSuitBaseAI) -> None:
        """
        A new battle member being added -> refresh the active effects.
        :param suit: The Suit being added into battle.
        """
        super().handleSuitAddedToBattle(suit)
        self.updateAppliedEffects()

    """
    Effect application
    """

    def cleanupManagedEffects(self) -> None:
        """
        Cleanup all applied effects.
        """
        for effect in self.managedEffects:
            effect.delete()

    def updateAppliedEffects(self) -> None:
        """
        Updates all applied effects.
        Clean up all managed effects, and then re-apply them onto Toons and Suits accordingly.
        """
        self.cleanupManagedEffects()

        # Apply buffs/debuffs to Toons/Suits here.
        pass

    def applyStatusEffectToToons(self, effectId: SEE, extraArgs: list = None, rounds: Optional[int] = -1,
                                 manageEffect: bool = True, exceptions: List[DistributedToonBaseAI] = None,
                                 effectExceptions: Optional[List[SEE]] = None) -> None:
        """
        Applies a Status Effect onto all Toons in battle.

        :param effectId:         The status effect definition.
        :param extraArgs:        The extra arguments for the status effect.
        :param rounds:           How many rounds should the status effect last for? If set to None, default is used.
        :param manageEffect:     Should this effect be "managed" by the Environmental Effect?
                                 Managed Effects will be cleaned up constantly.
        :param exceptions:       A list of Toons that should not have the effect applied.
        :param effectExceptions: If the Suit has any effect from this list, do not apply the effect.
        """
        if exceptions is None:
            exceptions = []
        if effectExceptions is None:
            effectExceptions = []
        for avId in self.battle.toons:
            toon = self.battle.getToon(avId)
            if not toon:
                continue
            if toon in exceptions:
                continue
            success = True
            for exceptedEffectId in effectExceptions:
                if toon.getStatusEffectOfId(exceptedEffectId) is not None:
                    success = False
                    break
            if success:
                self.applyStatusEffectToToon(toon, effectId, extraArgs, rounds, manageEffect)

    def applyStatusEffectToSuits(self, effectId: SEE, extraArgs: list = None, rounds: Optional[int] = -1,
                                 manageEffect: bool = True, exceptions: List[DistributedSuitBaseAI] = None,
                                 effectExceptions: Optional[List[SEE]] = None) -> None:
        """
        Applies a Status Effect onto all Suits in battle.

        :param effectId:         The status effect definition.
        :param extraArgs:        The extra arguments for the status effect.
        :param rounds:           How many rounds should the status effect last for? If set to None, default is used.
        :param manageEffect:     Should this effect be "managed" by the Environmental Effect?
                                 Managed Effects will be cleaned up constantly.
        :param exceptions:       A list of Suits that should not have the effect applied.
        :param effectExceptions: If the Suit has any effect from this list, do not apply the effect.
        """
        if exceptions is None:
            exceptions = []
        if effectExceptions is None:
            effectExceptions = []
        for suit in self.battle.suits:
            if suit in exceptions:
                continue
            success = True
            for exceptedEffectId in effectExceptions:
                if suit.getStatusEffectOfId(exceptedEffectId) is not None:
                    success = False
                    break
            if success:
                self.applyStatusEffectToSuit(suit, effectId, extraArgs, rounds, manageEffect)

    def applyStatusEffectToToon(self, toon: DistributedToonBaseAI,
                                effectId: SEE, extraArgs: list = None, rounds: Optional[int] = -1,
                                manageEffect: bool = True) -> None:
        """
        Applies a Status Effect onto a singular Toon.

        :param toon:         The Toon to apply the effect onto.
        :param effectId:     The status effect definition.
        :param extraArgs:    The extra arguments for the status effect.
        :param rounds:       How many rounds should the status effect last for? If set to None, default is used.
        :param manageEffect: Should this effect be "managed" by the Environmental Effect?
                             Managed Effects will be cleaned up constantly.
        """
        effect, combined = toon.addStatusEffect(effectId, extraArgs=extraArgs)
        if rounds is not None:
            effect.setRounds(rounds, adjust=False)
        if manageEffect and not combined:
            self.managedEffects.append(effect)

    def applyStatusEffectToSuit(self, suit: DistributedSuitBaseAI,
                                effectId: SEE, extraArgs: list = None, rounds: Optional[int] = -1,
                                manageEffect: bool = True) -> None:
        """
        Applies a Status Effect onto a singular Suit.

        :param suit:         The Toon to apply the effect onto.
        :param effectId:     The status effect definition.
        :param extraArgs:    The extra arguments for the status effect.
        :param rounds:       How many rounds should the status effect last for? If set to None, default is used.
        :param manageEffect: Should this effect be "managed" by the Environmental Effect?
                             Managed Effects will be cleaned up constantly.
        """
        effect, combined = suit.addStatusEffect(effectId, extraArgs=extraArgs)
        if rounds is not None:
            effect.setRounds(rounds, adjust=False)
        if manageEffect and not combined:
            self.managedEffects.append(effect)


@EnvironmentalClass(EnvironmentalEnum.CONTENT_SYNC)
class ContentSyncEnvironmental(EnvironmentalBase):
    """
    This class Content Syncs all Toons in battle.
    """

    def __init__(self, contentSyncType: ContentSyncType, **kwargs):
        super().__init__(**kwargs)
        self.contentSyncType = contentSyncType

        # All Toons in battle need to be content synced now.
        self.applyContentSyncToToon(AIUtil.avIds2Avs(self.battle.toons))

    def applyContentSyncToToon(self, toons: Union[DistributedToonBaseAI, List[DistributedToonBaseAI]]):
        self.battle.air.contentSyncManager.applyContentSync(
            syncType=self.contentSyncType,
            toons=toons,
            listenForZone=False,
        )

    def removeContentSyncFromToon(self, toons: Union[DistributedToonBaseAI, List[DistributedToonBaseAI]]):
        self.battle.air.contentSyncManager.removeContentSync(toons)

    """
    Event hooks    
    """

    def handleToonAddedToBattle(self, toon: DistributedToonBaseAI):
        super().handleToonAddedToBattle(toon)
        self.applyContentSyncToToon(toon)

    def handleToonRemovedFromBattle(self, toon: DistributedToonBaseAI):
        super().handleToonRemovedFromBattle(toon)
        self.removeContentSyncFromToon(toon)

    def handleBattleEnd(self):
        super().handleBattleEnd()
        self.removeContentSyncFromToon(AIUtil.avIds2Avs(self.battle.toons))


@EnvironmentalClass(EnvironmentalEnum.OVERCHARGE_ALL)
class OverchargedSuitsEnvironmental(PersistentStatusEffectEnvironmental):
    """
    This Environmental Effect makes sure that all active Suits have an Overcharged effect.
    Cleaning this effect up will cause the Suits to no longer have the Overcharged effect.
    """

    def updateAppliedEffects(self):
        # Overwrite this to apply effect management ourselves.
        # We also won't manually clean them up every time --
        # we will just add a new fresh one each time.
        for suit in self.suits:
            if not suit.getStatusEffectOfId(SEE.EFFECT_OVERCHARGED):
                self.applyStatusEffectToSuit(
                    suit=suit,
                    effectId=SEE.EFFECT_OVERCHARGED,
                )
            if not suit.getVisualEffectOfId(VisualEffectEnum.OVERCHARGED):
                effect = suit.getStatusEffectOfId(SEE.EFFECT_OVERCHARGED)
                suit.addVisualEffect(VisualEffectEnum.OVERCHARGED, extraArgs=effect.getTranslatedExtraArgs())


@EnvironmentalClass(EnvironmentalEnum.RAINMAKER_WEATHER)
class RainmakerEnvironmental(PersistentStatusEffectEnvironmental):
    """
    Rainmaker's Environmental effect is responsible for managing
    the passive status effects applied to Toons and Suits over the battle.
    """

    __slots__ = 'currentWeather', 'weatherJustChanged'

    oil_rain_hot = 50              # How much to heal each suit for?
    oil_rain_cap = 1.50            # The health cap of Oil Rain.
    oil_rain_dot = 10              # How much to damage each toon by?
    heavy_rain_damage_down = 0.50  # How much damage reduction does Heavy Rain give?
    heavy_rain_damage_mult = 120   # What is the dmg-back mult of Heavy Rain?
    storm_cell_stacks      = 36    # The stacks of Storm Cell Rainmaker starts with

    # All weather where Cogs will be perma-soaked within.
    WET_WEATHER = tuple()  # (RainmakerWeather.HEAVY_RAIN, RainmakerWeather.STORM_CELL)

    def __init__(self, **kwargs) -> None:
        self.currentWeather = RainmakerWeather.NORMAL
        self.lastWeather = RainmakerWeather.NORMAL
        super().__init__(**kwargs)

        self.weatherJustChanged = True
        self.cleanupEffectsOnDelete = False
        self.needMonsoonToonEffect = False
        self.inheritedEventDefinitions.append(ENV_ENUM.RAINMAKER_WEATHER)

    def getWeather(self) -> RainmakerWeather:
        """
        Returns the current weather of the environmental effect.
        """
        return self.currentWeather

    def getRainmaker(self) -> Optional[DistributedSuitBaseAI]:
        """
        Returns the boss suit, aka Rainmaker.
        """
        for suit in self.suits:
            if suit.getStyleName(doException=False) == 'rainmake':
                return suit
        return None

    """
    Weather updates
    """

    def setWeather(self, weather: RainmakerWeather) -> None:
        """
        Sets the current weather phase, and updates applied effects.
        :param weather: The new weather cycle.
        """
        if weather != self.currentWeather:
            self.weatherJustChanged = True
        self.lastWeather = self.currentWeather
        self.currentWeather = weather
        self.updateAppliedEffects()

    """
    Effect application
    """

    def handleSuitAddedToBattle(self, suit: DistributedSuitBaseAI) -> None:
        """
        Whenever we add a suit into battle, we also
        add some special effects onto Suits that arrive in certain phases.
        """
        # If the Suit is arriving in certain weathers, they can arrive drenched lol.
        if self.getWeather() in self.WET_WEATHER:
            self.applyStatusEffectToSuit(
                suit=suit,
                effectId=SEE.EFFECT_SUIT_DRENCHED,
                rounds=3,
                manageEffect=False,
            )

        # Apply all other effects now.
        super().handleSuitAddedToBattle(suit)

    def handleDrenchedExpire(self, suit: DistributedSuitBaseAI):
        """
        When Drenched expires on a suit, we re-apply perma soak as necessary.
        """
        if self.getWeather() not in self.WET_WEATHER:
            return
        self.applyStatusEffectToSuit(
            suit=suit,
            effectId=SEE.EFFECT_SUIT_SOAKED,
        )

    def updateAppliedEffects(self):
        super().updateAppliedEffects()

        # In Oil Rain, the Toons get a DOT, and the Suits get a HOT.
        if self.getWeather() == RainmakerWeather.OIL_RAIN:
            self.applyStatusEffectToToons(
                effectId=SEE.EFFECT_OIL_RAIN_DOT,
                extraArgs=[self.oil_rain_dot],
            )
            self.applyStatusEffectToSuits(
                effectId=SEE.EFFECT_OIL_RAIN_HOT,
                extraArgs=[self.oil_rain_hot, 1, self.oil_rain_cap],
            )

        # In Fog, Toons will get a persistent accuracy down debuff.
        elif self.getWeather() == RainmakerWeather.FOG:
            self.applyStatusEffectToToons(effectId=SEE.EFFECT_FOG)

        # In Heavy Rain, the Suits will become more powerful.
        # Rainmaker is given a unique effect for them in particular.
        elif self.getWeather() == RainmakerWeather.HEAVY_RAIN and self.getRainmaker():
            # Apply heavy rain effect.
            self.applyStatusEffectToSuits(
                effectId=SEE.EFFECT_HEAVY_RAIN,
                effectExceptions=[SEE.EFFECT_HEAVY_RAIN],
                extraArgs=[self.heavy_rain_damage_down, self.heavy_rain_damage_mult],
                manageEffect=False,
            )
            self.applyStatusEffectToToons(
                effectId=SEE.EFFECT_HEAVY_RAIN,
                effectExceptions=[SEE.EFFECT_HEAVY_RAIN],
                extraArgs=[self.heavy_rain_damage_down, self.heavy_rain_damage_mult],
                manageEffect=False,
            )

        # In Storm Cell, we give Rainmaker a stacking, permanent damage boost.
        elif self.getWeather() == RainmakerWeather.STORM_CELL and self.getRainmaker():
            # Give Rainmaker storm cell ONCE upon transition.
            if self.weatherJustChanged:
                self.applyStatusEffectToSuit(
                    suit=self.getRainmaker(),
                    effectId=SEE.EFFECT_STORM_CELL,
                    rounds=self.storm_cell_stacks,
                    manageEffect=False,
                )

        # In Monsoon, the Suits become Invisible, and cannot attack.
        elif self.getWeather() == RainmakerWeather.MONSOON:
            if self.weatherJustChanged:
                # Give the Toons the Monsoon effect, after the movie for this round has finished.
                self.needMonsoonToonEffect = True
                self.applyStatusEffectToSuit(suit=self.getRainmaker(), effectId=SEE.EFFECT_MONSOON_DEFENSE, rounds=4, manageEffect=False)

                # Remove the unnecessary cogs in battle.
                killAvatars = [suit for suit in self.suits if suit is not self.getRainmaker()]
                if killAvatars:
                    self.createAttack(
                        attackType=AttackEnum.AVATAR_INSTAKILL,
                        attackKwargs={
                            'invoker': self.getRainmaker(),
                            'targets': killAvatars,
                            'unlure': True,
                        },
                    )

                # Create the doom pattern.
                self.battle.maxSuits = 5
                instance = self.battle.instance
                for suit in self.spawnCogPattern():
                    instance.reserveSuits.append(suit)
                    suit.setBattleOrderPriority(BattleOrderPriority.BEGINNING)

            # Make sure that Cogs cannot attack.
            for suit in self.suits:
                cogEffect = suit.getStatusEffectOfType(CogStatusEffect)
                if cogEffect:
                    cogEffect.disableAttackGeneration()

        # If in wet weather, apply perma soak.
        if self.getWeather() in self.WET_WEATHER:
            self.applyStatusEffectToSuits(effectId=SEE.EFFECT_SUIT_SOAKED, effectExceptions=[SEE.EFFECT_SUIT_DRENCHED])

        # If we just came out of Monsoon, make sure cogs can attack again
        if self.lastWeather == RainmakerWeather.MONSOON and self.weatherJustChanged:
            for suit in self.suits:
                cogEffect = suit.getStatusEffectOfType(CogStatusEffect)
                if cogEffect:
                    cogEffect.enableAttackGeneration()

        # The weather has no longer just changed.
        self.weatherJustChanged = False

    def checkToonMonsoonEffect(self):
        if self.needMonsoonToonEffect:
            self.applyStatusEffectToToons(effectId=SEE.EFFECT_MONSOON, rounds=2, manageEffect=False)
        self.needMonsoonToonEffect = False

    """
    Monsoon Functionality
    """

    class CogPattern:
        def __init__(self, name: str, level: int, elite: bool = False, statusEffects: list = None):
            self.name = name
            self.level = level
            self.elite = elite
            self.statusEffects = statusEffects or []

    suitPatternBible = [
        [
            CogPattern('nn', 9, True,
                       [
                           [SEE.EFFECT_LURE_RESISTANCE, -1, [1]],
                           [SEE.EFFECT_SUIT_NODODGE, -1, None],
                           [SEE.EFFECT_DAMAGE_TAKEN_DOWN, -1, [0.8]],
                       ]),
            CogPattern('mh', 14, False,
                       [
                           [SEE.EFFECT_LURE_RESISTANCE, -1, [1]],
                           [SEE.EFFECT_SUIT_NODODGE, -1, None],
                           [SEE.EFFECT_COGS_DAMAGE_ABSORB_INSTANT, 0, [0.7, 0]],
                       ]),
            CogPattern('ls', 12, True,
                       [
                           [SEE.EFFECT_LURE_RESISTANCE, -1, [1]],
                           [SEE.EFFECT_SUIT_NODODGE, -1, None],
                           [SEE.EFFECT_SUIT_DAMAGE_BOOST, -1, [1.2, 2]]
                       ]),
            CogPattern('bw', 14, True,
                       [
                           [SEE.EFFECT_LURE_RESISTANCE, -1, [1]],
                           [SEE.EFFECT_SUIT_NODODGE, -1, None],
                           [SEE.EFFECT_HYDRATED, 2, [15, -1]],
                       ]),
        ],
        [
            CogPattern('hh', 11, False,
                       [
                           [SEE.EFFECT_LURE_RESISTANCE, -1, [1]],
                           [SEE.EFFECT_SUIT_NODODGE, -1, None],
                           [SEE.EFFECT_SUIT_SOAKED, 1, None, ]
                       ]),
            CogPattern('bw', 14, True,
                       [
                           [SEE.EFFECT_LURE_RESISTANCE, -1, [1]],
                           [SEE.EFFECT_SUIT_NODODGE, -1, None],
                           [SEE.EFFECT_SUIT_DAMAGE_BOOST, -1, [1.2, 2]],
                       ]),
            CogPattern('bw', 14, True,
                       [
                           [SEE.EFFECT_LURE_RESISTANCE, -1, [1]],
                           [SEE.EFFECT_SUIT_NODODGE, -1, None],
                           [SEE.EFFECT_SUIT_DAMAGE_BOOST, -1, [1.2, 2]],
                       ]),
            CogPattern('ad', 10, False,
                       [
                           [SEE.EFFECT_LURE_RESISTANCE, -1, [1]],
                           [SEE.EFFECT_SUIT_NODODGE, -1, None],
                           [SEE.EFFECT_COGS_DAMAGE_ABSORB_INSTANT, 0, [0.5, 0]],
                       ]),
        ],
    ]

    def spawnCogPattern(self) -> List[DistributedSuitAI]:
        suitPatternList = random.choice(self.suitPatternBible)
        suits = []
        for suitPattern in suitPatternList:
            newSuit = DistributedSuitAI(self.battle.air, None)
            dna = SuitDNA.SuitDNA()
            suitName = suitPattern.name
            dna.newSuit(suitName)
            newSuit.dna = dna
            newSuit.setLevel(suitPattern.level)
            newSuit.setElite(suitPattern.elite)
            for statusEffect in suitPattern.statusEffects:
                effectId, rounds, extraArgs = statusEffect
                newSuit.addStartingStatusEffect(effectId, rounds, extraArgs)
            newSuit.generateWithRequired(self.battle.zoneId)
            newSuit.node().setName('suit-%s' % newSuit.doId)
            suits.append(newSuit)
        return suits


@EnvironmentalClass(EnvironmentalEnum.PLUTOCRAT_WEATHER)
class PlutocratEnvironmental(PersistentStatusEffectEnvironmental):
    __slots__ = ("currentWeather", "cleanupEffectsOnDelete")
    
    def __init__(self, **kwargs) -> None:
        self.currentWeather = PlutocratWeather.NORMAL
        super().__init__(**kwargs)

        self.cleanupEffectsOnDelete = False

    def getWeather(self) -> PlutocratWeather:
        """
        Returns the current weather of the environmental effect.
        """
        return self.currentWeather

    def setWeather(self, weather: PlutocratWeather) -> None:
        """
        Sets the current weather phase, and updates applied effects.
        :param weather: The new weather cycle.
        """
        self.currentWeather = weather
        self.updateAppliedEffects()
    
    def updateAppliedEffects(self) -> None:
        super().updateAppliedEffects()

        # Add Frozen to every suit while in Snow Squall.
        if self.getWeather() == PlutocratWeather.SNOW_SQUALL:
            # Make sure nobody has soak/drench.
            for suit in self.suits:
                for effectId in (SEE.EFFECT_SUIT_SOAKED, SEE.EFFECT_SUIT_DRENCHED):
                    suit.removeStatusEffectOfId(effectId)

            self.applyStatusEffectToSuits(SEE.EFFECT_SUIT_FROZEN)

    def hurtToons(self) -> None:
        """The Toons take passive damage during snow squall."""
        if self.getWeather() != PlutocratWeather.SNOW_SQUALL:
            return

        self.createAttack(
            AttackEnum.SNOW_SQUALL_DAMAGE, 
            {"extraArgs": [-15]},
            {"mode": "end", 'respectPreviousAdditions': True},
        )
    
    def attemptShatter(self, suit: DistributedSuitBaseAI, attackType: AttackEnum) -> None:
        # Some attack types are blacklisted from shattering cogs.
        if attackType in (AttackEnum.TOON_FIRE,):
            return

        # Only shatter if the suit is frozen.
        if not suit.getStatusEffectOfId(SEE.EFFECT_SUIT_FROZEN):
            return

        # Immediately hurt the nearby cogs with the shatter.
        self.createAttack(
            AttackEnum.SHATTER_DAMAGE, 
            {"extraArgs": [suit]}, 
            {"mode": "insert"},
        )

    def handleSuitAddedToBattle(self, suit: DistributedSuitBaseAI) -> None:
        """If a new suit is added to the battle while snow squall is ongoing,
        ensure that they are cold.
        """
        if self.getWeather() == PlutocratWeather.SNOW_SQUALL:
            self.applyStatusEffectToSuit(suit, SEE.EFFECT_SUIT_FROZEN)
        
        super().handleSuitAddedToBattle(suit)
    
    def freezeSuit(self, suit: DistributedSuitBaseAI, effect: Union[SoakStatusEffect, DrenchStatusEffect]) -> None:
        """When a Suit is applied with either the soaked or drenched effect, remove it
        and replace it with frozen.
        """
        # Get the rounds which the soak/drench would have lasted for.
        rounds = effect.getRounds()

        # Remove soak/drench.
        effect.delete()

        # Apply frozen without tracking it.
        self.applyStatusEffectToSuit(suit, SEE.EFFECT_SUIT_FROZEN, rounds=rounds, manageEffect=False)

        # Update effects.
        self.updateAppliedEffects()


@EnvironmentalClass(EnvironmentalEnum.MAJOR_PLAYER_REVIVE_HANDLER)
class MajorPlayerReviveHandler(EnvironmentalBase):
    """
    While not technically an "environmental" effect, this persistent effect helps
    to manage the revive effect of Major Player.

    Once Major Player DIES normally, this effect will re-summon him once all Cogs are ded.
    """
    reviveHealthMultiplier = 1.0
    audienceSpawnCount = 3

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Has Major Player been revived already?
        self.hasRevived = False

    def handleSuitRemovedFromBattle(self, suit: DistributedSuitBaseAI):
        # Revive check
        if self.hasRevived:
            return

        # If the battle is empty, revive Major Player.
        aliveSuits = len(self.battle.aliveSuits)
        if aliveSuits == 0:
            # Will you not revive us again,
            # that your people may rejoice in you?
            # Psalm 85:6
            self.hasRevived = True
            instance = self.battle.instance
            god = instance.genMercBoss()
            god.b_setMaxHp(math.ceil(god.getMaxHp() * self.reviveHealthMultiplier))
            god.setStashed(True)
            setattr(god, 'anAbsoluteLegendReally', True)
            instance.reserveSuits.append(god)

            # god is hungry
            god.addStartingStatusEffect(SEE.EFFECT_LAST_TAP)

            # Add the crazy reserves
            sootList = [god]
            for _ in range(3):
                suitName = 'mh'
                suitIndex, newSuit = instance.createAudienceSuit(cogType=suitName, setLevel=12, elite=True, pullFromAudience=False)
                if newSuit:
                    instance.reserveSuits.append(newSuit)
                    newSuit.addStartingStatusEffect(SEE.EFFECT_STAR_OF_THE_SHOW, extraArgs=[10, 1])
                    # Add an attack down effect on these guys.
                    newSuit.addStartingStatusEffect(SEE.EFFECT_MP_COGS_DAMAGE_DOWN)
                    sootList.append(newSuit)

            # Let's use our handy dandy buff-applying function here on our new friends.
            instance.oopsAllBuffs(
                [soot for soot in sootList if soot is not god],
                reviveOverride=True,
                isActive=False
            )

            # Assign partners because WE'RE CRAZY.
            # Same logic from the DancePartners attack!!!
            activeToonObjs = self.battle.activeToonObjs
            partnerableToons = [toon for toon in activeToonObjs if toon.getHp() > 0]
            validEffectIndices = list(range(8))  # just obligatory number idk lol

            # Clear the status effects from all Toons when we enter the second phase to prevent buff stacking.
            for toon in activeToonObjs:
                toon.clearStatusEffects()

            # Assign soulmates.
            toonList = partnerableToons[:]
            random.shuffle(toonList)
            random.shuffle(sootList)
            for silyLilCritter, genericAntagonist in zip(toonList, sootList):
                effectIndex = validEffectIndices.pop(0)
                avId_A = silyLilCritter.getDoId()
                avId_B = genericAntagonist.getDoId()
                silyLilCritter.addStatusEffect(
                    effectId=SEE.EFFECT_DANCE_PARTNER,
                    extraArgs=[effectIndex, avId_A, avId_B],
                )
                genericAntagonist.addStartingStatusEffect(
                    effectId=SEE.EFFECT_DANCE_PARTNER,
                    extraArgs=[effectIndex, avId_A, avId_B],
                )


@EnvironmentalClass(EnvironmentalEnum.MAJOR_PLAYER_SHUFFLE_HANDLER)
class MajorPlayerShuffleHandler(EnvironmentalBase):

    def __init__(self, battle, battleListener, rounds: int = -1, **kwargs) -> None:
        super().__init__(battle, battleListener, rounds, **kwargs)
        self.inheritedEventDefinitions.append(ENV_ENUM.MAJOR_PLAYER_SHUFFLE_HANDLER)

    def handleRevivedDancePartners(self) -> None:
        mplayer = [suit for suit in self.suits if suit.dna.name == "mplayer"]
        if not mplayer:
            return
        mplayer = mplayer[0]

        toons = [toon for toon in [simbase.air.getDo(toonId) for toonId in self.toons] if toon]
        lonelyToons = [toon for toon in toons if not toon.getStatusEffectOfId(SEE.EFFECT_DANCE_PARTNER)]

        if lonelyToons:
            # Figure out which indices are OK.
            # This logic is the same in Environmentals.py for the major player revive.
            validEffectIndices = list(range(8))  # just obligatory number idk lol
            for toon in toons:
                existingPartnerEffect = toon.getStatusEffectOfId(SEE.EFFECT_DANCE_PARTNER)
                if existingPartnerEffect:
                    effectIndex = existingPartnerEffect.getEffectIndex()
                    if effectIndex in validEffectIndices:
                        validEffectIndices.remove(effectIndex)

            # Get the existing effect from God.
            godEffect = mplayer.getStatusEffectOfId(SEE.EFFECT_DANCE_PARTNER)
            if godEffect:
                # If the toon is in the battle, remove their effect.
                toon = [toon for toon in toons if toon.doId == godEffect.avId_A]
                if toon:
                    toon[0].removeStatusEffectOfId(SEE.EFFECT_DANCE_PARTNER)
                # Remove the God effect.
                godEffect.delete()

            newPartner = random.choice(lonelyToons)
            effectIndex = validEffectIndices.pop(0)

            mplayer.addStatusEffect(
                SEE.EFFECT_DANCE_PARTNER, 
                extraArgs=[effectIndex, newPartner.doId, mplayer.doId]
            )
            newPartner.addStatusEffect(
                SEE.EFFECT_DANCE_PARTNER,
                extraArgs=[effectIndex, newPartner.doId, mplayer.doId]
            )


@EnvironmentalClass(EnvironmentalEnum.HECK_YOUR_GAG_ORDER)
class GagOrderOverwriteEnvironmental(EnvironmentalBase):
    """
    An environmental effect that adds support for overwriting the gag order.
    """
    defaultGagOrder = BattleGlobals.GAG_TRACK_ORDER

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.inheritedEventDefinitions.append(ENV_ENUM.HECK_YOUR_GAG_ORDER)

        # Upon application, update gag order.
        self.battleEnded = False

    def destroy(self) -> None:
        """When the effect is cleaned up, reset the gag order"""
        self.updateGagOrder(override=self.defaultGagOrder)
        super().destroy()

    def getNewGagOrder(self) -> List[AttackEnum]:
        """Returns our cool awesome gag order to use everyone loves this game"""
        return self.defaultGagOrder

    def handleTurnEnd(self):
        """When the turn ends, automagically request the gag order to update."""
        self.updateGagOrder()

    def handleBattleEnd(self):
        self.updateGagOrder(override=self.defaultGagOrder)
        self.battleEnded = True

    def updateGagOrder(self, override: Optional[List[AttackEnum]] = None):
        if not self.battleEnded:
            self.battle.b_setGagOrder(override or self.getNewGagOrder())


@EnvironmentalClass(EnvironmentalEnum.PACESETTER_GAG_ORDER)
class PacesetterGagOrderEnvironmental(GagOrderOverwriteEnvironmental):
    """
    Pacesetter will grotesquely annihilate the gag order every so often like a boss
    """
    potentialHorribleOrderings = [
        [
            AttackEnum.TOON_THROW,
            AttackEnum.TOON_SOUND,
            AttackEnum.TOON_DROP,
            AttackEnum.TOON_TRAP,
            AttackEnum.TOON_SQUIRT,
            AttackEnum.TOON_HEAL,
            AttackEnum.TOON_LURE,
            AttackEnum.TOON_ZAP,
        ],
        [
            AttackEnum.TOON_SOUND,
            AttackEnum.TOON_DROP,
            AttackEnum.TOON_SQUIRT,
            AttackEnum.TOON_HEAL,
            AttackEnum.TOON_ZAP,
            AttackEnum.TOON_TRAP,
            AttackEnum.TOON_LURE,
            AttackEnum.TOON_THROW,
        ],
        [
            AttackEnum.TOON_SQUIRT,
            AttackEnum.TOON_SOUND,
            AttackEnum.TOON_HEAL,
            AttackEnum.TOON_TRAP,
            AttackEnum.TOON_THROW,
            AttackEnum.TOON_ZAP,
            AttackEnum.TOON_LURE,
            AttackEnum.TOON_DROP,
        ],
        [
            AttackEnum.TOON_THROW,
            AttackEnum.TOON_SQUIRT,
            AttackEnum.TOON_ZAP,
            AttackEnum.TOON_SOUND,
            AttackEnum.TOON_TRAP,
            AttackEnum.TOON_LURE,
            AttackEnum.TOON_DROP,
            AttackEnum.TOON_HEAL,
        ],
        [
            AttackEnum.TOON_SQUIRT,
            AttackEnum.TOON_TRAP,
            AttackEnum.TOON_LURE,
            AttackEnum.TOON_DROP,
            AttackEnum.TOON_HEAL,
            AttackEnum.TOON_ZAP,
            AttackEnum.TOON_SOUND,
            AttackEnum.TOON_THROW,
        ],
        [
            AttackEnum.TOON_TRAP,
            AttackEnum.TOON_SQUIRT,
            AttackEnum.TOON_DROP,
            AttackEnum.TOON_THROW,
            AttackEnum.TOON_ZAP,
            AttackEnum.TOON_LURE,
            AttackEnum.TOON_HEAL,
            AttackEnum.TOON_SOUND,
        ],
        [
            AttackEnum.TOON_DROP,
            AttackEnum.TOON_SQUIRT,
            AttackEnum.TOON_ZAP,
            AttackEnum.TOON_TRAP,
            AttackEnum.TOON_THROW,
            AttackEnum.TOON_LURE,
            AttackEnum.TOON_SOUND,
            AttackEnum.TOON_HEAL,
        ],
        [
            AttackEnum.TOON_TRAP,
            AttackEnum.TOON_DROP,
            AttackEnum.TOON_SQUIRT,
            AttackEnum.TOON_SOUND,
            AttackEnum.TOON_THROW,
            AttackEnum.TOON_ZAP,
            AttackEnum.TOON_LURE,
            AttackEnum.TOON_HEAL,
        ],
        [
            AttackEnum.TOON_TRAP,
            AttackEnum.TOON_DROP,
            AttackEnum.TOON_SQUIRT,
            AttackEnum.TOON_SOUND,
            AttackEnum.TOON_THROW,
            AttackEnum.TOON_ZAP,
            AttackEnum.TOON_LURE,
            AttackEnum.TOON_HEAL,
        ],
    ]

    def __init__(self, *args, **kwargs):
        # Set the base gag order.
        self.currentGagOrder = self.defaultGagOrder

        # Fully initialize.
        super().__init__(*args, **kwargs)

    def handleSuitRemovedFromBattle(self, suit: DistributedSuitBaseAI):
        super().handleSuitRemovedFromBattle(suit)
        if suit.getStyleName(False) == 'psetter':
            self.destroy()

    def getNewGagOrder(self) -> List[AttackEnum]:
        return self.currentGagOrder

    def randomizeOrder(self):
        potentialOrderings = self.potentialHorribleOrderings[:]
        if self.currentGagOrder in potentialOrderings:
            potentialOrderings.remove(self.currentGagOrder)
        self.currentGagOrder = random.choice(potentialOrderings)


@EnvironmentalClass(EnvironmentalEnum.FTF_ATTORNEY_OVERSEER)
class FTFAttorneyOverseer(EnvironmentalBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def createHealingAttack(self, target, damage):
        self.sendEvent(BEG.EVENT_CREATE_INSERT_ATTACK, [
            AttackEnum.SUIT_HEAL,
            {"targets": [target], "extraArgs": [damage * -2, True, 10.0]},
            {"mode": "insert"},
        ])

    def handleComboDamage(self, attackType: AttackEnum, damageAmount: int, target: BattleAvatar, attack):
        self.createHealingAttack(target, damageAmount)
        # This has to be 1 or the animations will break
        return -1

    def handleKnockbackDamage(self, attackType: AttackEnum, damageAmount: int, target: BattleAvatar, attack):
        self.createHealingAttack(target, damageAmount)
        # This has to be 1 or the animations will break
        return -1


@EnvironmentalClass(EnvironmentalEnum.FTF_GENERAL_RUSHJOB_TRACKER)
class FTFRushJobTracker(EnvironmentalBase):
    """
    This Environmental acts as a tracker for the Laborious Attorney's Rush Jobs.
    We can't really rely on him being around to Kill people, because
    nuclear cogs transform constantly
    """

    def handleRushJobFail(self):
        # We need to find ourselves an invoker to work with here.
        # We will first prioritize any rush job attorneys.
        allSuits = [suit for suit in self.suits if suit.getHp() > 0 and suit.dna.name.find('ftf') != -1]
        if len(allSuits) <= 0:
            return

        allAttorneys = [suit for suit in allSuits if suit.dna.name == 'ftf_l']
        allLaboriousAttorneys = [suit for suit in allAttorneys if suit.specialContainerId == FindTheFamilyGlobals.AbilityEnum.Attorney_RushJob]

        # Let's find the base pool we want to work with.
        if len(allLaboriousAttorneys):
            # First prefer laborious attorneys
            basePool = allLaboriousAttorneys
        elif len(allAttorneys):
            # We don't have any laborious attorneys, check for just *any* attorneys
            basePool = allAttorneys
        else:
            # OK, we don't have any attorneys, just pick literally any suit
            basePool = allSuits

        # Now, we should try to first prefer unlured suits.
        unluredFromPool = [suit for suit in basePool if not suit.hasStatusEffectOfId(SEE.EFFECT_SUIT_LURED)]
        # If we have any unlured cogs, pick a random invoker from that crowd.
        if len(unluredFromPool) > 0:
            invoker = random.choice(unluredFromPool)
        # No unlured cogs, take any from our pool
        else:
            invoker = random.choice(basePool)

        # We can finally go and add the hurry sickness attack to whatever invoker we ended up choosing.
        self.sendEvent(BEG.EVENT_CREATE_INSERT_ATTACK, [
            AttackEnum.HURRY_SICKNESS, {"invoker": invoker, "extraArgs": [0.6, NORMAL, 0, True], "unlure": True},
            {"priority": -100},
        ])


@EnvironmentalClass(EnvironmentalEnum.ADAPTIVE_LAFF)
class AdaptiveLaffEnvironmental(EnvironmentalBase):
    """
    This class applies an adaptive laff modifier on all toons in the battle.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Keep track of everyone's modifiers so we can modify the modifiers.
        self.modifierDict = {}

        # Keep track of what kind of laff we're giving everyone so we can update it at the right time.
        self.updateDict = {}

        # All Toons in battle need to be given adaptive laff.
        self.applyAdaptiveLaffToToon(AIUtil.avIds2Avs(self.battle.toons))

        # Amount for addToCap that toons are capped at, default is 150.
        self.hpCap = 150

    def applyAdaptiveLaffToToon(self, toons):
        for toon in toons:
            from toontown.modifiers.classes.LaffAdaptiveModifier import LaffAdaptiveModifier
            self.modifierDict[toon] = LaffAdaptiveModifier(laffCap=15)
            toon.addModifier(modifier=self.modifierDict[toon])

    def removeAdaptiveLaffFromToon(self, toons):
        for toon in toons:
            if not toon:
                continue

            # Remove the laff multiplier
            from toontown.modifiers.ModifierEnums import ModifierType
            toon.removeModifierOfType(ModifierType.LaffAdaptive)
            self.modifierDict.pop(toon, None)

    def requestAdaptiveLaff(self, toon, amount, modifyType):
        if modifyType == 'set':
            self.updateDict[toon] = amount
        elif modifyType == 'add':
            if toon in self.updateDict:
                self.updateDict[toon] += amount
            else:
                self.updateDict[toon] = toon.getMaxHp() + amount
        elif modifyType == 'addToCap':
            if toon in self.updateDict:
                self.updateDict[toon] += max(min(self.hpCap - self.updateDict[toon], amount), 0)
            else:
                self.updateDict[toon] = toon.getMaxHp() + max(min(self.hpCap - toon.getMaxHp(), amount), 0)

    def updateAdaptiveLaff(self):
        for toon in self.updateDict.keys():
            if toon in self.modifierDict:
                self.modifierDict[toon].updateLaffCap(toon, self.updateDict[toon])
        self.updateDict = {}

    """
    Event hooks    
    """

    def handleToonAddedToBattle(self, toon: DistributedToonBaseAI):
        super().handleToonAddedToBattle(toon)
        self.applyAdaptiveLaffToToon([toon])

    def handleToonRemovedFromBattle(self, toon: DistributedToonBaseAI):
        super().handleToonRemovedFromBattle(toon)
        self.removeAdaptiveLaffFromToon([toon])

    def handleBattleEnd(self):
        super().handleBattleEnd()
        self.removeAdaptiveLaffFromToon(AIUtil.avIds2Avs(self.battle.toons))


@EnvironmentalClass(EnvironmentalEnum.HIGH_ROLLER_CLONE_HANDLER)
class HighRollerCloneHandler(PersistentStatusEffectEnvironmental):
    TOONUP = 0
    TRAP = 1
    LURE = 2
    THROW = 3
    SQUIRT = 4
    ZAP = 5
    SOUND = 6
    DROP = 7

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.inheritedEventDefinitions.append(ENV_ENUM.HIGH_ROLLER_CLONE_HANDLER)
        self.epicCurrentCloneList = [None for _ in range(8)]
        self.currentAttackOrder = None
        self.luckyDropList = []
        self.niceComboList = []
        self.powerTripUser = -1

    def refreshCurrentClones(self):
        for suit in self.battle.suits:
            cloneEffect = suit.getStatusEffectOfId(SEE.EFFECT_HIGHROLLER_CLONE)
            if not cloneEffect:
                continue
            self.epicCurrentCloneList[cloneEffect.getType()] = suit

    def killClone(self, cloneId):
        if cloneId == self.SOUND:
            self.clearWinded()
        self.epicCurrentCloneList[cloneId] = None
        if cloneId == self.powerTripUser:
            self.attemptPowerTrip()

    def onBeginSuitAttacks(self):
        if self.powerTripUser == -1:
            self.attemptPowerTrip()

    def clearWinded(self):
        toons = [toon for toon in [simbase.air.getDo(toonId) for toonId in self.toons] if toon]
        for toon in toons:
            toon.removeStatusEffectOfId(SEE.EFFECT_WINDED)

    """
    Active listeners
    """

    def onClonesJoin(self):
        """
        Called once when the cogs join.
        """
        if len(self.battle.suits) != 5:
            return

        self.refreshCurrentClones()
        if self.epicCurrentCloneList[self.SOUND]:
            self.clearWinded()
        self.updateStatusEffects(1)

    def onRoundEnd(self):
        """
        Called at the end of each round.
        """
        self.luckyDropList = []
        self.niceComboList = []
        self.powerTripUser = -1
        self.updateStatusEffects(2)

    def updateStatusEffects(self, rounds):
        for suit in self.battle.suits:
            cloneEffect = suit.getStatusEffectOfId(SEE.EFFECT_HIGHROLLER_CLONE)
            if not cloneEffect:
                continue
            # We'll remove the virtual effects from each Cog here; if the lure guy is still present, we'll be adding it back.
            if cloneEffect.getType() != self.LURE:
                suit.removeStatusEffectOfId(SEE.EFFECT_LURE_RESISTANCE)
                self.applyStatusEffectToSuit(suit, SEE.EFFECT_LURE_RESISTANCE, extraArgs=[2], manageEffect=False)
                suit.removeStatusEffectOfId(SEE.EFFECT_VIRTUAL_COG)

        # This resets everyone's Soak-powered resistance, then sets it again for soaked suits if Pink Guy is alive.
        self.handleSoakPoweredResistance()

        if self.epicCurrentCloneList[self.LURE]:
            self.abilityLure(rounds)

        if self.epicCurrentCloneList[self.SOUND]:
            self.abilitySound()

    def onEndToonTrack(self, attackTrack, attackList):
        """
        Called on the end of every Toon Track calculation.
        :param attackTrack: The track that was used.
        :param attackList: A list of each attack in the track.
        """
        if attackTrack == AttackEnum.TOON_HEAL and self.epicCurrentCloneList[self.TOONUP]:
            # Punish for toon-up usage.
            self.abilityToonup(attackTrack, attackList)
        elif attackTrack == AttackEnum.TOON_SQUIRT and self.epicCurrentCloneList[self.SQUIRT]:
            # Punish for squirt usage.
            self.abilitySquirt(attackTrack, attackList)

    def onAttackOrder(self, attackOrder):
        """
        Called upon the creation of the attack order.
        """

        # For some reason, the environmental doesn't get attached to attacks, so we'll just do that here.
        # Let's create a list of attacks that are pertinent to modify using environmental effects.
        # (zap needs its jumps affected, gags with combo damage need to be affected)
        importantAttacks = (
            AttackEnum.TOON_TRAP,
            AttackEnum.TOON_LURE,
            AttackEnum.TOON_THROW,
            AttackEnum.TOON_SQUIRT,
            AttackEnum.TOON_ZAP,
            AttackEnum.TOON_SOUND,
            AttackEnum.TOON_DROP,
        )

        callbackDict = {
            self.TRAP: self.abilityTrap,
            self.ZAP: self.abilityZap,
            self.DROP: self.abilityDrop,
        }

        for cloneType in callbackDict.keys():
            if self.epicCurrentCloneList[cloneType]:
                callback = callbackDict[cloneType]
                callback(attackOrder)

    """
    Initiation Methods
    """

    def attemptPowerTrip(self):
        possibleAttackers = []
        for clone in self.epicCurrentCloneList:
            clone: DistributedSuitAI
            if clone:
                if not clone.hasStatusEffectOfId(SEE.EFFECT_SUIT_LURED) and clone in self.battle.aliveSuits:
                    possibleAttackers.append(clone)
        if possibleAttackers:
            powerTripUser = random.choice(possibleAttackers)
            self.createAttack(attackType=AttackEnum.POWER_TRIP, insertKwargs=dict(priority=88888), attackKwargs={'invoker': powerTripUser})
            self.powerTripUser = self.epicCurrentCloneList.index(powerTripUser)

    def abilityToonup(self, attackTrack, attackList):
        """
        Runs the Toon-Up ability.
        Damages all toons who were healed by toon-up for 50% of the healing.
        Only called after toon-up usage.
        """
        if not attackList:
            return

        # Set variables in advance for loop.
        attack = None
        toons = [toon for toon in [simbase.air.getDo(toonId) for toonId in self.toons] if toon]
        damageDict = {toon: 0 for toon in toons}

        from toontown.clashbattle.battle.attacks.server.toon.ToonAttackAI import \
            ToonAttackAI

        # Get the arguments for the attack.
        for attack in attackList:
            attack: ToonAttackAI

            for toon in attack.targets:
                if toon != attack.invoker:
                    healingDone = attack.getDamage() / (len(attack.targets) - 1)
                    damageDict[toon] += (healingDone / 2) * 10

        # Now create the attack.
        if attack:
            from toontown.clashbattle.battle.attacks.server.AttackRepositoryAI import createAttack
            attack = createAttack(
                AttackEnum.HIGHROLLER_CLONE_TOONUP,
                extraArgs=[damageDict],
                invoker=self.epicCurrentCloneList[self.TOONUP]
            )
            self.battle.battleCalc.insertAttack(attack, adjust=True)

    def abilityTrap(self, attackOrder):
        damageMult = 1
        unluring = False
        for attack in attackOrder.getAttacks():
            if attack.attackType == AttackEnum.TOON_TRAP:
                damageMult += 1
                unluring = True

        self.createAttack(
            attackType=AttackEnum.HIGHROLLER_CLONE_TRAP,
            attackKwargs={
                'invoker': self.epicCurrentCloneList[self.TRAP],
                'damageMult': damageMult,
                'unlure': unluring
            },
            insertKwargs=dict(mode="end")
        )

    def abilityLure(self, rounds):
        # This function needs to account for a call at the end of a round, AND a call when the cogs spawn.

        # First, we create a list to keep track of cogs we want to choose from to apply lure resistance.
        otherClones = []

        for suit in self.battle.suits:
            # We only want to affect cogs that are clones, not High Roller.
            cloneEffect = suit.getStatusEffectOfId(SEE.EFFECT_HIGHROLLER_CLONE)
            if not cloneEffect:
                continue
            # Handling the lure cog vs non-lure
            if cloneEffect.getType() == self.LURE:
                # Lure cog should have the effect, and if he doesn't then it's our time to apply the effect.
                suit.removeStatusEffectOfId(SEE.EFFECT_LURE_RESISTANCE)
                self.applyStatusEffectToSuit(suit, SEE.EFFECT_VIRTUAL_COG, manageEffect=False)
                self.applyStatusEffectToSuit(suit, SEE.EFFECT_LURE_RESISTANCE, extraArgs=[-1], manageEffect=False)
            else:
                if rounds == 1 and suit.getStatusEffectOfId(SEE.EFFECT_VIRTUAL_COG):
                    # If rounds is 1, that means we're applying the attack at the start when the cogs spawn.
                    # In other words, we only want this to happen once. Therefore, return.
                    # (this is because the cog spawning event triggers multiple times)
                    return
                else:
                    otherClones.append(suit)
                    self.applyStatusEffectToSuit(suit, SEE.EFFECT_VIRTUAL_COG, manageEffect=False)

        if len(otherClones) == 0:
            return

        luckyClone = random.choice(otherClones)

        # If the cog we picked was lured...
        # ...no
        luckyClone.removeStatusEffectOfId(SEE.EFFECT_SUIT_LURED)
        luckyClone.removeStatusEffectOfId(SEE.EFFECT_LURE_RESISTANCE)

        # Enjoy the suffering of having another lure immune cog!
        self.applyStatusEffectToSuit(
            luckyClone,
            SEE.EFFECT_LURE_RESISTANCE,
            rounds=rounds,
            extraArgs=[-1],
            manageEffect=False
        )

    def handleComboDamage(self, attackType: AttackEnum, damageAmount: int, target: BattleAvatar, attack):
        if self.epicCurrentCloneList[self.THROW]:
            # We only want Nice Combo! to display once for each combo'd track per turn.
            if attackType in self.niceComboList:
                return 0
            self.niceComboList.append(attackType)
            from toontown.toonbase import TTLocalizer
            self.battle.battleCalc.createAndInsertAttack(
                AttackEnum.SHOW_HP_TEXT,
                attackKwargs={
                    "targets": [self.epicCurrentCloneList[self.THROW]],
                    "extraArgs": [TTLocalizer.HP_TEXT_CLONE_TAUNT],
                },
                insertKwargs={"mode": "insert"},
            )
            return 0
        else:
            return damageAmount

    def abilitySquirt(self, attackTrack, attackList):
        """
        Runs the Squirt ability.
        Damages all toons who used squirt by 50% of the main target damage.
        Only called after squirt usage.
        Applies soaked to the toon because it's funny.
        """
        if not attackList:
            return

        # Set variables in advance for loop.
        attack = None
        toons = [toon for toon in [simbase.air.getDo(toonId) for toonId in self.toons] if toon]
        damageDict = {toon: 0 for toon in toons}

        from toontown.clashbattle.battle.attacks.server.toon.ToonAttackAI import \
            ToonAttackAI

        # Get the arguments for the attack.
        for attack in attackList:
            attack: ToonAttackAI
            toon = attack.invoker
            damageDict[toon] += attack.getDamage() * 5

        # Now create the attack.
        if attack:
            self.createAttack(
                AttackEnum.HIGHROLLER_CLONE_SQUIRT,
                attackKwargs={
                    "extraArgs": [damageDict],
                },
            )

        # Reset soak powered resistance here as well.
        self.handleSoakPoweredResistance()

    def abilityZap(self, attackOrder):
        self.currentAttackOrder = attackOrder

    def handleDamageTaken(self, target: BattleAvatar, invoker: BattleAvatar,
                          damageAmount: int, attackType: AttackEnum):
        newDamage = damageAmount
        for attack in self.luckyDropList:
            # We're gonna check to be sure the drop was actually a lucky drop, and double its damage if it was.
            if attack.invoker == invoker:
                self.luckyDropList.remove(attack)
                newDamage *= 2
                break

        # We may be done, if this wasn't a zap there's no more modifications to make.
        if attackType != AttackEnum.TOON_ZAP or not self.epicCurrentCloneList[self.ZAP]:
            return newDamage

        # At this point, we're modifying zap.
        # We'll have to find the attack of interest first in our attack order.
        for attack in self.currentAttackOrder.getAttacks():
            if attack.invoker == invoker and attack.attackType == AttackEnum.TOON_ZAP:
                # We know this is the correct attack, since toons can only attack once per turn.
                # Return a value depending on whether the target of this function call was the primary, non-jump target.
                if attack.target == target.doId:
                    return newDamage
                else:
                    return 1

    def abilitySound(self):
        toons = [toon for toon in [simbase.air.getDo(toonId) for toonId in self.toons] if toon]
        for toon in toons:
            if not toon.getStatusEffectOfId(SEE.EFFECT_WINDED):
                self.applyStatusEffectToToon(
                    toon,
                    SEE.EFFECT_WINDED,
                    rounds=500,
                    manageEffect=False
                )

    def abilityDrop(self, attackOrder):
        # Basically it's the really cool pip text code but with some nice extra bits about changing levels 'n' stuff.
        trackDict: dict = {}

        # Part one: Create an attack upgrade dictionary (discarding cases where no upgrade occurred).
        for i, attack in enumerate(attackOrder.getAttacks()):
            if attack.attackType != AttackEnum.TOON_DROP and \
               (attack.attackType not in BattleGlobals.ATTACK_TRACKS or random.randint(1, 10) != 1):
                continue
            # Someone used drop or got really unlucky. Time to pull a gamer move and change their attack mid-turn.
            # Generate a level based on the rng function. A value of >7 will increase damage instead of level.
            if attack.attackType in [AttackEnum.TOON_HEAL, AttackEnum.TOON_LURE]:
                newLevel = self.generateNewParityLevel(attack.level)
            else:
                newLevel = self.generateNewLevel(attack.level)
            if attack.level == newLevel:
                continue

            oldLevel = attack.level

            # Special case
            if newLevel > 7 and attack.attackType not in [AttackEnum.TOON_HEAL, AttackEnum.TOON_LURE, AttackEnum.TOON_TRAP]:
                self.luckyDropList.append(attack)
            # Prevents x2 damage of lure, since lure is based on knockback not damage
            elif newLevel > 7:
                continue
            else:
                # Sorry, you didn't actually use that level! You used this level instead.
                attack.level = newLevel

            # At this point, we know we have to prepare the attack for its promotion text to appear.
            if attack.track not in trackDict:
                trackDict[attack.track] = []
            trackDict[attack.track].append((attack, int(oldLevel), int(newLevel)))

        # Now that we have changed the levels of gags, we need to re-sort them into level order.
        for track in BattleGlobals.ATTACK_TRACKS:
            self.battle.battleCalc.sortTrackByLevel(track)

        # Part two: Give our promotion text function some nice text to display.
        for attackInfo in trackDict.values():
            # Subtract 1 from the index to get the text to go *before* the spending pip text
            idx = self.battle.battleCalc.attackOrder.getNextIndexOfTrack(attackInfo[0][0].attackType)
            # If the attack just before us is a pip text attack, move our promote/demote text down 1
            # This will keep the pip text attack in the right spot corresponding with the toon attack
            if idx != 0 and self.battle.battleCalc.attackOrder.getAttacks()[idx - 1].attackType == AttackEnum.SHOW_PIP_TEXT:
                idx -= 1
            # Creates a text attack to show the toon what happened to their gag track if it was altered.
            self.doPromoteTextAttacks(attackInfo, idx)

    def generateNewLevel(self, oldLevel) -> int:
        # Generates a new level for a track, over-leveling in certain weird cases for extra fun!
        wackyRng = random.randint(1, 100)

        if wackyRng > 85:
            return oldLevel + 1
        elif wackyRng > 50:
            return oldLevel
        else:
            oldLevel -= 1
            while random.randint(1, 4) != 1 and oldLevel > 0:
                oldLevel -= 1
        return max(oldLevel, 0)  # Just to be extra sure we don't kill the game.

    def generateNewParityLevel(self, oldLevel) -> int:
        # Generates a new level for a track that needs to keep its group or single target parity.
        wackyRng = random.randint(1, 2)

        if wackyRng == 2:
            # Hooray! Time to promote their gag.
            return oldLevel + 2
        else:
            # Uh oh! Time to demote with respect to parity.
            while wackyRng == 1 and oldLevel > 1:
                oldLevel -= 2
                wackyRng = random.randint(1, 2)
        return max(oldLevel, 0)  # Just to be extra sure we don't kill the game.

    def doPromoteTextAttacks(self, attackInfo, attackIndex):
        from toontown.toonbase import TTLocalizer
        targets = []
        textList = []
        for i in range(len(attackInfo)):
            oldLevel = attackInfo[i][1]
            newLevel = attackInfo[i][2]
            diff = newLevel - oldLevel
            if diff == 0:
                promotionText = ""
            elif newLevel > 7:       # BIG WIN!!
                promotionText = TTLocalizer.HP_TEXT_BIG_WIN
            elif diff > 1:           # WIN!!
                promotionText = TTLocalizer.HP_TEXT_SMALL_WIN
            elif diff < -1:          # BIG LOSS!!
                promotionText = TTLocalizer.HP_TEXT_BIG_LOSS
            elif diff == -1:         # LOSS!!
                promotionText = TTLocalizer.HP_TEXT_SMALL_LOSS
            else:                    # Default (error prevention)
                promotionText = TTLocalizer.HP_TEXT_SMALL_WIN
            targets.append(attackInfo[i][0].invoker)
            textList.append(promotionText)

        self.battle.battleCalc.createAndInsertAttack(
            AttackEnum.SHOW_HP_TEXT,
            attackKwargs={
                "targets": targets,
                "extraArgs": textList,
            },
            insertKwargs=dict(index=attackIndex, adjust=False, respectPreviousAdditions=False)
        )

    def handleSoakPoweredResistance(self):
        for suit in self.battle.suits:
            # We only want to affect cogs that are clones, not High Roller.
            cloneEffect = suit.getStatusEffectOfId(SEE.EFFECT_HIGHROLLER_CLONE)
            if not cloneEffect:
                continue
            suit.removeStatusEffectOfId(SEE.EFFECT_SOAK_POWERED_RESISTANCE)  # Reset them
            if suit.getStatusEffectOfId(SEE.EFFECT_SUIT_SOAKED) and self.epicCurrentCloneList[self.SQUIRT]:
                suit.addStatusEffect(SEE.EFFECT_SOAK_POWERED_RESISTANCE)


@EnvironmentalClass(EnvironmentalEnum.FTF_SUPERVISOR_CONTROLLING)
class FTFSupervisorControlling(EnvironmentalBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def handleBaseDamage(self, attackType: AttackEnum, damageAmount: int, target: BattleAvatar, attack):
        if attackType in (AttackEnum.TOON_SOUND, AttackEnum.TOON_SQUIRT, AttackEnum.TOON_ZAP) or \
                (attackType in (AttackEnum.TOON_HEAL, AttackEnum.TOON_LURE) and attack.isGroup):
            return int(round(damageAmount * 0.5))

        return damageAmount


@EnvironmentalClass(EnvironmentalEnum.FTF_PRESIDENT_SHIVERING)
class FTFPresidentShivering(EnvironmentalBase):
    def suitIsUs(self, suit):
        return bool(suit.getStatusEffectOfId(SEE.EFFECT_FTF_PRESIDENT_SHIVERING))

    def attemptShatter(self, suit: DistributedSuitBaseAI, attackType: AttackEnum) -> None:
        # Some attack types are blacklisted from shattering cogs.
        if attackType in (AttackEnum.TOON_FIRE,):
            return

        # Only shatter if the suit is frozen.
        if not suit.getStatusEffectOfId(SEE.EFFECT_SUIT_FROZEN):
            return

        # Immediately hurt the nearby cogs with the shatter.
        self.createAttack(
            AttackEnum.FTF_PRESIDENT_SHATTER_DAMAGE,
            {"extraArgs": [suit]},
            {"mode": "insert"},
        )


@EnvironmentalClass(EnvironmentalEnum.FTF_PRESIDENT_HIGHSTAKES)
class FTFPresidentHighStakes(EnvironmentalBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.luckyDropList = []

    def onRoundEnd(self):
        """
        Called at the end of each round.
        """
        self.luckyDropList = []

    def handleDamageTaken(self, target: BattleAvatar, invoker: BattleAvatar,
                          damageAmount: int, attackType: AttackEnum):
        newDamage = damageAmount
        for attack in self.luckyDropList:
            # We're gonna check to be sure the drop was actually a lucky drop, and double its damage if it was.
            if attack.invoker == invoker:
                self.luckyDropList.remove(attack)
                newDamage *= 2
                break

        return newDamage

    def onAttackOrder(self, attackOrder):
        # Basically it's the really cool pip text code but with some nice extra bits about changing levels 'n' stuff.
        trackDict: dict = {}

        # Part one: Create an attack upgrade dictionary (discarding cases where no upgrade occurred).
        for i, attack in enumerate(attackOrder.getAttacks()):
            from toontown.clashbattle.battle.attacks.server.toon.ToonAttackAI import ToonAttackAI
            if (not isinstance(attack, ToonAttackAI)) or attack.attackType in (AttackEnum.TOON_NPC, AttackEnum.TOON_FIRE, AttackEnum.TOON_SUE):
                continue
            attack: ToonAttackAI
            # Someone got unlucky. Time to pull a gamer move and change their attack mid-turn.
            # Generate a level based on the rng function. A value of >7 will increase damage instead of level.
            if attack.attackType in [AttackEnum.TOON_HEAL, AttackEnum.TOON_LURE]:
                newLevel = self.generateNewLevel(attack.level, parity=True)
            else:
                newLevel = self.generateNewLevel(attack.level)
            if attack.level == newLevel:
                continue

            oldLevel = attack.level

            # Special case
            if newLevel > 7 and attack.attackType not in [AttackEnum.TOON_HEAL, AttackEnum.TOON_LURE, AttackEnum.TOON_TRAP]:
                self.luckyDropList.append(attack)
            # Prevents x2 damage of lure, since lure is based on knockback not damage
            elif newLevel > 7:
                continue
            else:
                # Sorry, you didn't actually use that level! You used this level instead.
                attack.level = newLevel

            # At this point, we know we have to prepare the attack for its promotion text to appear.
            if attack.track not in trackDict:
                trackDict[attack.track] = []
            trackDict[attack.track].append((attack, int(oldLevel), int(newLevel)))

        # Now that we have changed the levels of gags, we need to re-sort them into level order.
        for track in BattleGlobals.ATTACK_TRACKS:
            self.battle.battleCalc.sortTrackByLevel(track)

        # Part two: Give our promotion text function some nice text to display.
        for attackInfo in trackDict.values():
            # Subtract 1 from the index to get the text to go *before* the spending pip text
            idx = self.battle.battleCalc.attackOrder.getNextIndexOfTrack(attackInfo[0][0].attackType)
            # Creates a text attack to show the toon what happened to their gag track if it was altered.
            self.doPromoteTextAttacks(attackInfo, idx)

    def generateNewLevel(self, oldLevel, parity=False) -> int:
        # Generates a new level for a track, over-leveling in certain weird cases for extra fun!
        wackyRng = random.randint(1, 100)

        if wackyRng > 85:
            return oldLevel + (2 if parity else 1)
        elif wackyRng > 30:
            return oldLevel
        else:
            oldLevel -= (2 if parity else 1)
            downgradeChance = 0.25 if parity else 0.5
            while oldLevel > 0:
                if random.random() > downgradeChance:
                    break

                oldLevel -= (2 if parity else 1)
                # Progressively decreasing chance to downgrade levels
                downgradeChance *= 0.75
        return max(oldLevel, 1 if (parity and oldLevel % 2 == 1) else 0)  # Just to be extra sure we don't kill the game.

    def doPromoteTextAttacks(self, attackInfo, attackIndex):
        from toontown.toonbase import TTLocalizer
        targets = []
        textList = []
        for i in range(len(attackInfo)):
            oldLevel = attackInfo[i][1]
            newLevel = attackInfo[i][2]
            diff = newLevel - oldLevel
            if diff == 0:
                promotionText = ""
            elif newLevel > 7:       # BIG WIN!!
                promotionText = TTLocalizer.HP_TEXT_BIG_WIN
            elif diff > 1:           # WIN!!
                promotionText = TTLocalizer.HP_TEXT_SMALL_WIN
            elif diff < -1:          # BIG LOSS!!
                promotionText = TTLocalizer.HP_TEXT_BIG_LOSS
            elif diff == -1:         # LOSS!!
                promotionText = TTLocalizer.HP_TEXT_SMALL_LOSS
            else:                    # Default (error prevention)
                promotionText = TTLocalizer.HP_TEXT_SMALL_WIN
            targets.append(attackInfo[i][0].invoker)
            textList.append(promotionText)

        self.battle.battleCalc.createAndInsertAttack(
            AttackEnum.SHOW_HP_TEXT,
            attackKwargs={
                "targets": targets,
                "extraArgs": textList,
            },
            insertKwargs=dict(index=attackIndex, adjust=False, respectPreviousAdditions=False)
        )


@EnvironmentalClass(EnvironmentalEnum.FTF_SUPERVISOR_CONFUSED_GAG_ORDER)
class FTFSupervisorConfusedGagOrder(PacesetterGagOrderEnvironmental):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.inheritedEventDefinitions.append(ENV_ENUM.PACESETTER_GAG_ORDER)

    def handleSuitRemovedFromBattle(self, suit: DistributedSuitBaseAI):
        # Overwrite the pacesetter version of this func that destroys itself when pacesetter dies
        EnvironmentalBase.handleSuitRemovedFromBattle(self, suit)
