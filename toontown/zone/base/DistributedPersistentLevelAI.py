from direct.distributed.DistributedObjectAI import DistributedObjectAI

from toontown.level import LevelSpec
from toontown.level.editor import EditorGlobals
from toontown.level.Level import Level
from toontown.level.DistributedLevelAI import DistributedLevelAI
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from toontown.utils.RateLimiter import IdRateLimiter
from toontown.quest3.context.InteractibleEntityContext import InteractibleEntityContext
from toontown.zone.ZoneSpecRegistry import ZoneSpecRegistry
from toontown.zone.base.PersistentLevelBase import PersistentLevelBase
from toontown.zone.entities.PersistentLevelEntityCreatorAI import PersistentLevelEntityCreatorAI
from toontown.zone.base.PersistentLevelSuitPlannerAI import PersistentLevelSuitPlannerAI
from toontown.zone.base.DistributedPersistentLevelBattleAI import DistributedPersistentLevelBattleAI
from toontown.zone.entities.standalone.DistributedPersistentLevelSuitAI import DistributedPersistentLevelSuitAI


@DirectNotifyCategory()
class DistributedPersistentLevelAI(DistributedLevelAI, PersistentLevelBase):
    """
    A variant of DistributedLevel that can be accessed by many players at a time,
    and is persistent in the world.
    """
    EntityPriorityTypes = ['levelMgr', 'zone', 'propSpinner', 'buildingMgr']

    def __init__(self, air, zoneId):
        DistributedObjectAI.__init__(self, air)
        Level.__init__(self)
        self.zoneId = zoneId
        self.entranceId = 0
        self.avIdList = []
        self.maxMerits = 0
        self.merits = 0
        self.planner = None
        self.ratelimiter = IdRateLimiter(3, 1)
        if EditorGlobals.wantLevelEditor():
            self.modified = 0

    def createEntityCreator(self):
        return PersistentLevelEntityCreatorAI(level=self)

    def generate(self):
        """
        Called when the DistributedObject is reintroduced to the world, either for the first time or from the cache.
        """
        self.notify.debug('generate')
        self.notify.debug(
            'start persistent level %s %s creation, frame=%s' % (self.zoneId, self.doId, globalClock.getFrameCount())
        )
        self.notify.debug('loading spec')
        if self.zoneId not in ZoneSpecRegistry:
            raise KeyError(f"zoneId {self.zoneId} does not have a persistent level definition!!")
        specFilePath = ZoneSpecRegistry[self.zoneId]
        levelSpec = LevelSpec.LevelSpec(specFilePath)
        if EditorGlobals.wantLevelEditor():
            self.notify.debug('creating entity type registry')
            typeReg = self.getEntityTypeReg()
            levelSpec.setEntityTypeReg(typeReg)

        self.notify.debug('creating entities')
        DistributedLevelAI.generate(self, levelSpec)

    def initializeLevel(self, levelSpec):
        DistributedLevelAI.initializeLevel(self, levelSpec)
        self.planner = PersistentLevelSuitPlannerAI(self.air, self, DistributedPersistentLevelSuitAI,
                                                    DistributedPersistentLevelBattleAI)

    def delete(self, deAllocZone=True):
        if self.planner:
            self.planner.destroy()
            self.planner = None
        super().delete(deAllocZone)

    def initializeLevelToonHooks(self):
        pass

    def handleAvatarDisconnect(self, avId):
        pass

    def handleAvatarLeft(self, avId, oldZoneId):
        pass

    def allToonsGone(self, toonsThatCleared):
        pass

    def requestQuestEntityInteract(self, entId):
        # It would be much more painful to make quest entities distributed,
        # so I am placing this here instead.
        avId = self.air.getAvatarIdFromSender()
        if self.ratelimiter.userBlocked(avId):
            return

        av = self.air.getDo(avId)
        if not av:
            return

        entity = self.getEntity(entId)
        if not entity:
            return
        if self.getEntityType(entId) != 'questInteractible':
            return

        self.air.quest3Manager.progressObjective(quester=av, context=InteractibleEntityContext(
            interactibleType=entity.interactibleType,
            zoneId=self.zoneId,
        ))
