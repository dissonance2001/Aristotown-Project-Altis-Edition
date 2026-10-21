from direct.distributed import DistributedObjectAI
from direct.directnotify import DirectNotifyGlobal
from toontown.toonbase import ToontownGlobals

class LobbyManagerAI(DistributedObjectAI.DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('LobbyManagerAI')

    def __init__(self, air, bossConstructor, zoneIdr, bossCtors=None):
        """
        :type air: ToontownAIRepository
        """
        self.notify.debug("init")
        DistributedObjectAI.DistributedObjectAI.__init__(self, air)
        self.air = air  # type: ToontownAIRepository
        self.bossConstructor = bossConstructor
        self.zoneIdr = zoneIdr
        # Optional {bossType: constructor} table used by the boss-selection elevator.
        self.bossCtors = dict(bossCtors) if bossCtors else {}

    def getBossOptions(self):
        """Selectable boss types for this lobby ([] when there is nothing to choose)."""
        if len(self.bossCtors) < 2:
            return []
        return sorted(self.bossCtors.keys())

    def generate(self):
        DistributedObjectAI.DistributedObjectAI.generate(self)
        self.notify.debug('generate')

    def delete(self):
        self.notify.debug('delete')
        self.ignoreAll()
        DistributedObjectAI.DistributedObjectAI.delete(self)

    def createBossOffice(self, avIdList, hardmode = 0, bossType = None):
        bossZone = self.air.allocateZone()
        self.notify.debug('createBossOffice: %s' % bossZone)
        bossCtor = self.bossCtors.get(bossType, self.bossConstructor) if bossType is not None else self.bossConstructor
        bossCog = bossCtor(self.air)
        bossCog.generateWithRequired(bossZone)
        self.acceptOnce(bossCog.uniqueName('BossDone'), self.destroyBossOffice, extraArgs = [bossCog])

        # Tell the boss about the toons coming.
        for avId in avIdList:
            if avId:
                bossCog.addToon(avId)

        bossCog.b_setState('WaitForToons')
        return bossZone

    def destroyBossOffice(self, bossCog):
        bossZone = bossCog.zoneId
        self.notify.info('destroyBossOffice: %s' % bossZone)
        bossCog.requestDelete()
        self.air.deallocateZone(bossZone)
