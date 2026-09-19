"""
Defines the modifiers that are applied onto Toons for each type of Content Sync.

The general container/data classes are at the top.
The actual definitions are listed at the bottom of the module.
"""
from toontown.battle import BattleGlobals
from toontown.modifiers.Modifier import Modifier
from toontown.modifiers.classes.GagsContentSyncModifier import GagsContentSyncModifier
from toontown.modifiers.classes.LaffContentSyncModifier import LaffContentSyncModifier
from toontown.modifiers.classes.RewardContentSyncModifier import RewardContentSyncModifier
from toontown.modifiers.contentsync.ContentSyncEnums import ContentSyncType
from typing import Dict, List, Optional
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from toontown.toon.DistributedToon import DistributedToon


class __ContentSyncDefinitions:
    """
    Container class for content sync definitions.
    """

    def __init__(self, defs: Dict[ContentSyncType, '__CSDef']) -> None:
        self._defs = defs

    def getModifiersOfSyncType(self, syncType: ContentSyncType) -> List[Modifier]:
        """
        A general accessor method to get all modifiers of a certain content sync level.
        :param syncType: The content sync type.
        """
        csDef = self._defs.get(syncType, None)
        if csDef is None:
            # The content sync definition does not exist... probably a dev error.
            # Let's not miss it -- this absolutely shouldn't have been called.
            raise KeyError(f"Content Sync definition for {syncType} does not exist.")

        # OK, ask the sync definition for its modifiers. 24hr ban for Personally Identifiable Information
        return csDef.makeModifiers()

    def getDefinition(self, syncType: ContentSyncType) -> '__CSDef':
        return self._defs.get(syncType)


class __CSDef:
    """
    Dataclass that defines content sync data more refinely.
    """

    def __init__(self,
                 laffCap: Optional[int] = None, laffSoftness: float = 1.0,
                 maxGagLevel: int = None,
                 rewardAccess: Optional[int] = None,
                 trackAccCap: Optional[int] = None,
                 forceLaff: bool = False,
                 forceMaxed: bool = False,
                 clearGags: bool = False) -> None:
        """
        Defines some ContentSync variables.
        :param laffCap:      Defines a soft laff cap. Optional.
        :param laffSoftness: Defines the "softness" of the laff cap. Constrained from 0.0 (hard cap) to 1.0 (no cap).
        :param maxGagLevel:  Defines the max gag level the player has access to. Indexed at 0 (for level 1 gags).
        :param rewardAccess: Defines what rewards the player has access to, in a list format.
                             0: No access
                             1: IOUs only
                             2: IOUs + Counterfeits only
                             3: IOUs + Counterfeits + C&Ds only
                             None: All rewards are available
                             If any reward is allowed, Unites will also be allowed
        :param trackAccCap: Defines the max "track accuracy" cap for this content sync definition.
                            If it's not defined, it will use whatever the standard gag level
                            for that boss would suggest.
        :param forceLaff: Should their max laff be forced to what is defined by the sync?
        :param forceMaxed: Should their gags be maxed?
        :param clearGags: Should their Gags be cleared entering this sync?
        """
        self.laffCap = laffCap
        self.laffSoftness = laffSoftness
        self.maxGagLevel = maxGagLevel
        self.rewardAccess = rewardAccess
        self.trackAccCap = trackAccCap
        self.forceLaff = forceLaff
        self.forceMaxed = forceMaxed
        self.clearGags = clearGags

    def makeModifiers(self) -> List[Modifier]:
        """
        Returns all modifiers that this definition fulfills.
        """
        # Start with an empty modifier list.
        retModifiers: List[Modifier] = []

        # Make laff sync modifiers if necessary.
        if self.laffCap is not None:
            retModifiers.append(self._getLaffModifier())
        if self.maxGagLevel is not None:
            retModifiers.append(self._getGagModifier())
        if self.rewardAccess is not None:
            retModifiers.append(self._getRewardModifier())

        # Return our modifiers.
        return retModifiers

    def _getLaffModifier(self) -> LaffContentSyncModifier:
        return LaffContentSyncModifier(laffCap=self.laffCap, softness=self.laffSoftness, forceLaff=self.forceLaff)

    def _getGagModifier(self) -> GagsContentSyncModifier:
        return GagsContentSyncModifier(maxGagLevel=self.maxGagLevel, maxTrackAccLevel=self.trackAccCap,
                                       forceMaxed=self.forceMaxed, clearInventory=self.clearGags)

    def _getRewardModifier(self) -> RewardContentSyncModifier:
        return RewardContentSyncModifier(
            iousAllowed=self.rewardAccess >= 1,
            counterfeitsAllowed=self.rewardAccess >= 2,
            cndsAllowed=self.rewardAccess >= 3,
            slipsAllowed=self.rewardAccess >= 4,
            unitesAllowed=self.rewardAccess >= 1,
        )

    """
    Sync check status
    """

    def checkSyncActive(self, av) -> bool:
        """
        Determines if this content sync will restrict the Toon.
        :type av: DistributedToon
        """
        return self.checkLaffSyncActive(av)  \
            or self.checkGagSyncActive(av)   \
            or self.checkIOUSyncActive(av)   \
            or self.checkUniteSyncActive(av) \
            or self.checkCNDSyncActive(av)   \
            or self.checkPinkSlipSyncActive(av)

    """Checks for Laff Sync"""

    def checkLaffSyncActive(self, av) -> bool:
        """
        Determines if laff is actively being constrained.
        :type av: DistributedToon
        """
        return av.maxHp != self.getConstrainedLaff(av)

    def getConstrainedLaff(self, av=None, hp=None) -> int:
        assert av or hp
        if hp is None:
            hp = av.maxHp
        if self.laffCap is None:
            return hp
        laffModifier = self._getLaffModifier()
        return laffModifier.modify(value=hp, do=av)

    """Checks for Gag Sync"""

    def checkGagSyncActive(self, av) -> bool:
        """
        Determines if the Gag content sync is active.
        :type av: DistributedToon
        """
        if self.maxGagLevel is None:
            return False
        for track in BattleGlobals.ATTACK_TRACKS:
            gagLevel = av.experience.getExpLevel(track)
            if gagLevel > self.maxGagLevel:
                return True
        return False

    def getMaxGagLevel(self) -> int:
        return self.maxGagLevel

    """Checks for Reward Sync"""

    def checkIOUSyncActive(self, av) -> bool:
        """
        Determines if IOUs are being blocked by this sync definition.
        :type av: DistributedToon
        """
        # Reward access must be defined. IOUs are guaranteed on access 1+.
        if self.rewardAccess is None or self.rewardAccess >= 1:
            return False

        # Return True if the player has any IOUs.
        return bool(av.getIOUs())

    def checkUniteSyncActive(self, av) -> bool:
        """
        Determines if unites are being blocked by this sync definition.
        :type av: DistributedToon
        """
        # Reward access must be defined. Unites are guaranteed if any other reward is available, so we check IOUs.
        if self.rewardAccess is None or self.rewardAccess >= 1:
            return False

        # Return True if the player has any unites.
        return bool(av.getUnites)

    def checkCounterfeitSyncActive(self, av) -> bool:
        """
        Determines if Counterfeits are being blocked by this sync definition.
        :type av: DistributedToon
        """
        # Reward access must be defined. Counterfeits are guaranteed on access 2+.
        if self.rewardAccess is None or self.rewardAccess >= 2:
            return False

        # Return True if the player has any counterfeits.
        return bool(av.getCounterfeits())

    def checkCNDSyncActive(self, av) -> bool:
        """
        Determines if C&Ds are being blocked by this sync definition.
        :type av: DistributedToon
        """
        # Reward access must be defined. C&Ds are guaranteed on access 2+.
        if self.rewardAccess is None or self.rewardAccess >= 3:
            return False

        # Return True if the player has any C&Ds.
        return bool(av.getCeaseDesists())

    def checkPinkSlipSyncActive(self, av) -> bool:
        """
        Determines if Pink Slips are being blocked by this sync definition.
        :type av: DistributedToon
        """
        # Reward access must be defined. Pink Slips are guaranteed on access 2+.
        if self.rewardAccess is None or self.rewardAccess >= 4:
            return False

        # Return True if the player has any pink slips.
        return bool(av.getPinkSlips())


ContentSyncDefinitions = __ContentSyncDefinitions({
    # Generic Cog HQ definitions
    # this means that only level 1-6 gags are allowed
    # Track acc cap is set to 7, meaning that toons can still get track accuracy bonuses up to +70 if they're maxed
    ContentSyncType.SBHQ: __CSDef(laffCap=75,  laffSoftness=0.80, maxGagLevel=5, rewardAccess=5, trackAccCap=7),
    ContentSyncType.CBHQ: __CSDef(laffCap=85,  laffSoftness=0.80, maxGagLevel=6, rewardAccess=5, trackAccCap=7),
    ContentSyncType.LBHQ: __CSDef(laffCap=95,  laffSoftness=0.80, maxGagLevel=7, rewardAccess=5),
    ContentSyncType.BBHQ: __CSDef(laffCap=105, laffSoftness=0.80, maxGagLevel=7, rewardAccess=5),
    ContentSyncType.BDHQ: __CSDef(laffCap=115, laffSoftness=0.80, maxGagLevel=7, rewardAccess=5),

    # Taskline progression
    ContentSyncType.TASKLINE_TTC:  __CSDef(laffCap=30,  laffSoftness=0.50, maxGagLevel=2, rewardAccess=0),  # 'taskline' related progression
    ContentSyncType.TASKLINE_BB:   __CSDef(laffCap=40,  laffSoftness=0.50, maxGagLevel=3, rewardAccess=0),  # 'taskline' related progression
    ContentSyncType.TASKLINE_YOTT: __CSDef(laffCap=50,  laffSoftness=0.50, maxGagLevel=4, rewardAccess=0),  # 'taskline' related progression
    ContentSyncType.TASKLINE_DG:   __CSDef(laffCap=60,  laffSoftness=0.50, maxGagLevel=5, rewardAccess=1),  # 'taskline' related progression
    ContentSyncType.TASKLINE_MML:  __CSDef(laffCap=70,  laffSoftness=0.50, maxGagLevel=6, rewardAccess=2),  # 'taskline' related progression
    ContentSyncType.TASKLINE_TB:   __CSDef(laffCap=80,  laffSoftness=0.50, maxGagLevel=7, rewardAccess=3),  # 'taskline' related progression
    ContentSyncType.TASKLINE_AA:   __CSDef(laffCap=90,  laffSoftness=0.50, maxGagLevel=7, rewardAccess=4),  # 'taskline' related progression
    ContentSyncType.TASKLINE_DDL:  __CSDef(laffCap=100, laffSoftness=0.50, maxGagLevel=7, rewardAccess=4),  # 'taskline' related progression

    ContentSyncType.STREET_TTC:  __CSDef(laffCap=20,  laffSoftness=0.40, maxGagLevel=1, rewardAccess=0),  # street merc stuff
    ContentSyncType.STREET_BB:   __CSDef(laffCap=30,  laffSoftness=0.40, maxGagLevel=2, rewardAccess=0),  # street merc stuff
    ContentSyncType.STREET_YOTT: __CSDef(laffCap=40,  laffSoftness=0.40, maxGagLevel=3, rewardAccess=0),  # street merc stuff
    ContentSyncType.STREET_DG:   __CSDef(laffCap=50,  laffSoftness=0.40, maxGagLevel=4, rewardAccess=1),  # street merc stuff
    ContentSyncType.STREET_MML:  __CSDef(laffCap=60,  laffSoftness=0.40, maxGagLevel=5, rewardAccess=2),  # street merc stuff
    ContentSyncType.STREET_TB:   __CSDef(laffCap=75,  laffSoftness=0.40, maxGagLevel=6, rewardAccess=3),  # street merc stuff
    ContentSyncType.STREET_AA:   __CSDef(laffCap=90,  laffSoftness=0.40, maxGagLevel=7, rewardAccess=4),  # street merc stuff
    ContentSyncType.STREET_DDL:  __CSDef(laffCap=105,  laffSoftness=0.40, maxGagLevel=7, rewardAccess=5),  # street merc stuff

    ContentSyncType.KUDOS_TTC:  __CSDef(laffCap=50,  laffSoftness=0.45, maxGagLevel=3, rewardAccess=0),
    ContentSyncType.KUDOS_BB:   __CSDef(laffCap=60,  laffSoftness=0.45, maxGagLevel=4, rewardAccess=1),
    ContentSyncType.KUDOS_YOTT: __CSDef(laffCap=75,  laffSoftness=0.45, maxGagLevel=5, rewardAccess=2),
    ContentSyncType.KUDOS_DG:   __CSDef(laffCap=90,  laffSoftness=0.45, maxGagLevel=6, rewardAccess=3),
    ContentSyncType.KUDOS_MML:  __CSDef(laffCap=105, laffSoftness=0.45, maxGagLevel=7, rewardAccess=4),
    ContentSyncType.KUDOS_TB:   __CSDef(laffCap=120, laffSoftness=0.45, maxGagLevel=7, rewardAccess=5),
    ContentSyncType.KUDOS_AA:   __CSDef(laffCap=140, laffSoftness=0.45, maxGagLevel=7, rewardAccess=5),
    ContentSyncType.KUDOS_DDL:  __CSDef(laffCap=150, laffSoftness=0.45, maxGagLevel=7, rewardAccess=5),

    # Other
    ContentSyncType.OCLO: __CSDef(laffCap=150, laffSoftness=0.30, maxGagLevel=7, rewardAccess=5),
    ContentSyncType.EVENT_HIGH_ROLLER: __CSDef(laffCap=None, maxGagLevel=7, rewardAccess=0,
                                               forceLaff=False, forceMaxed=True, clearGags=True),
})

# Suits that apply a Content Sync environmental effect when they are in a battle.
SuitToContentSyncType: Dict[str, ContentSyncType] = {
    'duckshfl': ContentSyncType.STREET_TTC,
    'ddiver':   ContentSyncType.STREET_BB,
    'gatekeep': ContentSyncType.STREET_YOTT,
    'bellring': ContentSyncType.STREET_DG,
    'mouthp':   ContentSyncType.STREET_MML,
    'fires':    ContentSyncType.STREET_TB,
    'treek':    ContentSyncType.STREET_AA,
    'fbed':     ContentSyncType.STREET_DDL,
}

