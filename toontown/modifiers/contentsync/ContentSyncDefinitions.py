from toontown.battle import BattleGlobals
from toontown.groups.GroupClasses import GroupCreation
from toontown.groups.GroupEnums import GroupType, Options
from toontown.modifiers.Modifier import Modifier
from toontown.modifiers.classes.GagsContentSyncModifier import GagsContentSyncModifier
from toontown.modifiers.classes.LaffContentSyncModifier import LaffContentSyncModifier
from toontown.modifiers.classes.RewardContentSyncModifier import RewardContentSyncModifier
from toontown.modifiers.contentsync.ContentSyncEnums import ContentSyncType


class __ContentSyncDefinitions:

    def __init__(self, defs):
        self._defs = defs

    def getModifiersOfSyncType(self, syncType):
        csDef = self._defs.get(syncType, None)
        if csDef is None:
            raise KeyError("Content Sync definition for %s does not exist." % syncType)
        return csDef.makeModifiers()

    def getDefinition(self, syncType):
        return self._defs.get(syncType)


class __CSDef:

    def __init__(self, laffCap=None, laffSoftness=1.0, maxGagLevel=None,
                 rewardAccess=None, trackAccCap=None, forceLaff=False,
                 forceMaxed=False, clearGags=False):
        self.laffCap = laffCap
        self.laffSoftness = laffSoftness
        self.maxGagLevel = maxGagLevel
        self.rewardAccess = rewardAccess
        self.trackAccCap = trackAccCap
        self.forceLaff = forceLaff
        self.forceMaxed = forceMaxed
        self.clearGags = clearGags

    def makeModifiers(self):
        retModifiers = []
        if self.laffCap is not None:
            retModifiers.append(self._getLaffModifier())
        if self.maxGagLevel is not None:
            retModifiers.append(self._getGagModifier())
        if self.rewardAccess is not None:
            retModifiers.append(self._getRewardModifier())
        return retModifiers

    def _getLaffModifier(self):
        return LaffContentSyncModifier(laffCap=self.laffCap, softness=self.laffSoftness, forceLaff=self.forceLaff)

    def _getGagModifier(self):
        return GagsContentSyncModifier(maxGagLevel=self.maxGagLevel, maxTrackAccLevel=self.trackAccCap,
                                       forceMaxed=self.forceMaxed, clearInventory=self.clearGags)

    def _getRewardModifier(self):
        return RewardContentSyncModifier(
            iousAllowed=self.rewardAccess >= 1,
            counterfeitsAllowed=self.rewardAccess >= 2,
            cndsAllowed=self.rewardAccess >= 3,
            slipsAllowed=self.rewardAccess >= 4,
            unitesAllowed=self.rewardAccess >= 1,
        )

    def checkSyncActive(self, av):
        return (self.checkLaffSyncActive(av) or
                self.checkGagSyncActive(av) or
                self.checkIOUSyncActive(av) or
                self.checkUniteSyncActive(av) or
                self.checkCNDSyncActive(av) or
                self.checkPinkSlipSyncActive(av))

    def checkLaffSyncActive(self, av):
        return av.maxHp != self.getConstrainedLaff(av)

    def getConstrainedLaff(self, av=None, hp=None):
        assert av or hp
        if hp is None:
            hp = av.maxHp
        if self.laffCap is None:
            return hp
        laffModifier = self._getLaffModifier()
        return laffModifier.modify(value=hp, do=av)

    def checkGagSyncActive(self, av):
        if self.maxGagLevel is None:
            return False
        for track in BattleGlobals.ATTACK_TRACKS:
            gagLevel = av.experience.getExpLevel(track)
            if gagLevel > self.maxGagLevel:
                return True
        return False

    def getMaxGagLevel(self):
        return self.maxGagLevel

    def checkIOUSyncActive(self, av):
        if self.rewardAccess is None or self.rewardAccess >= 1:
            return False
        return bool(av.getIOUs())

    def checkUniteSyncActive(self, av):
        if self.rewardAccess is None or self.rewardAccess >= 1:
            return False
        return bool(av.getUnites)

    def checkCounterfeitSyncActive(self, av):
        if self.rewardAccess is None or self.rewardAccess >= 2:
            return False
        return bool(av.getCounterfeits())

    def checkCNDSyncActive(self, av):
        if self.rewardAccess is None or self.rewardAccess >= 3:
            return False
        return bool(av.getCeaseDesists())

    def checkPinkSlipSyncActive(self, av):
        if self.rewardAccess is None or self.rewardAccess >= 4:
            return False
        return bool(av.getPinkSlips())


ContentSyncDefinitions = __ContentSyncDefinitions({
    ContentSyncType.SBHQ: __CSDef(laffCap=75,  laffSoftness=0.80, maxGagLevel=5, rewardAccess=5, trackAccCap=7),
    ContentSyncType.CBHQ: __CSDef(laffCap=85,  laffSoftness=0.80, maxGagLevel=6, rewardAccess=5, trackAccCap=7),
    ContentSyncType.LBHQ: __CSDef(laffCap=95,  laffSoftness=0.80, maxGagLevel=7, rewardAccess=5),
    ContentSyncType.BBHQ: __CSDef(laffCap=105, laffSoftness=0.80, maxGagLevel=7, rewardAccess=5),
    ContentSyncType.BDHQ: __CSDef(laffCap=115, laffSoftness=0.80, maxGagLevel=7, rewardAccess=5),

    ContentSyncType.TASKLINE_TTC:  __CSDef(laffCap=30,  laffSoftness=0.50, maxGagLevel=2, rewardAccess=0),
    ContentSyncType.TASKLINE_BB:   __CSDef(laffCap=40,  laffSoftness=0.50, maxGagLevel=3, rewardAccess=0),
    ContentSyncType.TASKLINE_YOTT: __CSDef(laffCap=50,  laffSoftness=0.50, maxGagLevel=4, rewardAccess=0),
    ContentSyncType.TASKLINE_DG:   __CSDef(laffCap=60,  laffSoftness=0.50, maxGagLevel=5, rewardAccess=1),
    ContentSyncType.TASKLINE_MML:  __CSDef(laffCap=70,  laffSoftness=0.50, maxGagLevel=6, rewardAccess=2),
    ContentSyncType.TASKLINE_TB:   __CSDef(laffCap=80,  laffSoftness=0.50, maxGagLevel=7, rewardAccess=3),
    ContentSyncType.TASKLINE_AA:   __CSDef(laffCap=90,  laffSoftness=0.50, maxGagLevel=7, rewardAccess=4),
    ContentSyncType.TASKLINE_DDL:  __CSDef(laffCap=100, laffSoftness=0.50, maxGagLevel=7, rewardAccess=4),

    ContentSyncType.STREET_TTC:  __CSDef(laffCap=20,  laffSoftness=0.40, maxGagLevel=1, rewardAccess=0),
    ContentSyncType.STREET_BB:   __CSDef(laffCap=30,  laffSoftness=0.40, maxGagLevel=2, rewardAccess=0),
    ContentSyncType.STREET_YOTT: __CSDef(laffCap=40,  laffSoftness=0.40, maxGagLevel=3, rewardAccess=0),
    ContentSyncType.STREET_DG:   __CSDef(laffCap=50,  laffSoftness=0.40, maxGagLevel=4, rewardAccess=1),
    ContentSyncType.STREET_MML:  __CSDef(laffCap=60,  laffSoftness=0.40, maxGagLevel=5, rewardAccess=2),
    ContentSyncType.STREET_TB:   __CSDef(laffCap=75,  laffSoftness=0.40, maxGagLevel=6, rewardAccess=3),
    ContentSyncType.STREET_AA:   __CSDef(laffCap=90,  laffSoftness=0.40, maxGagLevel=7, rewardAccess=4),
    ContentSyncType.STREET_DDL:  __CSDef(laffCap=105, laffSoftness=0.40, maxGagLevel=7, rewardAccess=5),

    ContentSyncType.KUDOS_TTC:  __CSDef(laffCap=50,  laffSoftness=0.45, maxGagLevel=3, rewardAccess=0),
    ContentSyncType.KUDOS_BB:   __CSDef(laffCap=60,  laffSoftness=0.45, maxGagLevel=4, rewardAccess=1),
    ContentSyncType.KUDOS_YOTT: __CSDef(laffCap=75,  laffSoftness=0.45, maxGagLevel=5, rewardAccess=2),
    ContentSyncType.KUDOS_DG:   __CSDef(laffCap=90,  laffSoftness=0.45, maxGagLevel=6, rewardAccess=3),
    ContentSyncType.KUDOS_MML:  __CSDef(laffCap=105, laffSoftness=0.45, maxGagLevel=7, rewardAccess=4),
    ContentSyncType.KUDOS_TB:   __CSDef(laffCap=120, laffSoftness=0.45, maxGagLevel=7, rewardAccess=5),
    ContentSyncType.KUDOS_AA:   __CSDef(laffCap=140, laffSoftness=0.45, maxGagLevel=7, rewardAccess=5),
    ContentSyncType.KUDOS_DDL:  __CSDef(laffCap=150, laffSoftness=0.45, maxGagLevel=7, rewardAccess=5),

    ContentSyncType.OCLO: __CSDef(laffCap=150, laffSoftness=0.30, maxGagLevel=7, rewardAccess=5),
    ContentSyncType.EVENT_HIGH_ROLLER: __CSDef(laffCap=None, maxGagLevel=7, rewardAccess=0,
                                               forceLaff=False, forceMaxed=True, clearGags=True),
})

SuitToContentSyncType = {
    'duckshfl': ContentSyncType.STREET_TTC,
    'ddiver':   ContentSyncType.STREET_BB,
    'gatekeep': ContentSyncType.STREET_YOTT,
    'bellring': ContentSyncType.STREET_DG,
    'mouthp':   ContentSyncType.STREET_MML,
    'fires':    ContentSyncType.STREET_TB,
    'treek':    ContentSyncType.STREET_AA,
    'fbed':     ContentSyncType.STREET_DDL,
}


class __GroupTypeToGTSDef:

    def __init__(self, definitionDict):
        self.definitionDict = definitionDict

    def getSyncType(self, groupCreation):
        groupTypeSync = self.definitionDict.get(groupCreation.getGroupType(), None)
        if groupTypeSync is None:
            return None
        return groupTypeSync.getSyncType(groupCreation)


class __GroupTypeSync:

    def __init__(self, defaultSyncType, optionToSyncType=None):
        self.defaultSyncType = defaultSyncType
        self.optionToSyncType = optionToSyncType or {}

    def getSyncType(self, groupCreation):
        for option in groupCreation.getOptions():
            if option in self.optionToSyncType:
                return self.optionToSyncType.get(option)
        return self.defaultSyncType


GroupTypeToGTSDef = __GroupTypeToGTSDef({
    GroupType.VP: __GroupTypeSync(defaultSyncType=ContentSyncType.SBHQ),
    GroupType.CFO: __GroupTypeSync(defaultSyncType=ContentSyncType.CBHQ),
    GroupType.CLO: __GroupTypeSync(defaultSyncType=ContentSyncType.LBHQ),
    GroupType.CEO: __GroupTypeSync(defaultSyncType=ContentSyncType.BBHQ),

    GroupType.DM:           __GroupTypeSync(defaultSyncType=ContentSyncType.TASKLINE_TTC),
    GroupType.DOLA:         __GroupTypeSync(defaultSyncType=ContentSyncType.TASKLINE_BB),
    GroupType.DOPR:         __GroupTypeSync(defaultSyncType=ContentSyncType.TASKLINE_YOTT),
    GroupType.DOPA:         __GroupTypeSync(defaultSyncType=ContentSyncType.TASKLINE_DDL),

    GroupType.DuckShuffler:  __GroupTypeSync(defaultSyncType=ContentSyncType.STREET_TTC),
    GroupType.DeepDiver:     __GroupTypeSync(defaultSyncType=ContentSyncType.STREET_BB),
    GroupType.Gatekeeper:    __GroupTypeSync(defaultSyncType=ContentSyncType.STREET_YOTT),
    GroupType.Bellringer:    __GroupTypeSync(defaultSyncType=ContentSyncType.STREET_DG),
    GroupType.Mouthpiece:    __GroupTypeSync(defaultSyncType=ContentSyncType.STREET_MML),
    GroupType.Firestarter:   __GroupTypeSync(defaultSyncType=ContentSyncType.STREET_TB),
    GroupType.Treekiller:    __GroupTypeSync(defaultSyncType=ContentSyncType.STREET_AA),
    GroupType.Featherbedder: __GroupTypeSync(defaultSyncType=ContentSyncType.STREET_DDL),

    GroupType.Prethinker:   __GroupTypeSync(defaultSyncType=ContentSyncType.KUDOS_TTC),
    GroupType.Rainmaker:    __GroupTypeSync(defaultSyncType=ContentSyncType.KUDOS_BB),
    GroupType.Witchhunter:  __GroupTypeSync(defaultSyncType=ContentSyncType.KUDOS_YOTT),
    GroupType.Multislacker: __GroupTypeSync(defaultSyncType=ContentSyncType.KUDOS_DG),
    GroupType.Majorplayer:  __GroupTypeSync(defaultSyncType=ContentSyncType.KUDOS_MML),
    GroupType.Plutocrat:    __GroupTypeSync(defaultSyncType=ContentSyncType.KUDOS_TB),
    GroupType.Chainsaw:     __GroupTypeSync(defaultSyncType=ContentSyncType.KUDOS_AA),
    GroupType.Pacesetter:   __GroupTypeSync(defaultSyncType=ContentSyncType.KUDOS_DDL),

    GroupType.OCLO:         __GroupTypeSync(defaultSyncType=ContentSyncType.OCLO),
    GroupType.Highroller:   __GroupTypeSync(defaultSyncType=ContentSyncType.EVENT_HIGH_ROLLER),
})