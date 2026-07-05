from direct.distributed import DistributedObjectAI
from direct.directnotify import DirectNotifyGlobal
from toontown.toonbase import ToontownGlobals

class LobbyManagerAI(DistributedObjectAI.DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('LobbyManagerAI')

    def __init__(self, air, bossConstructor, zoneIdr):
        """
        :type air: ToontownAIRepository
        """
        self.notify.debug("init")
        DistributedObjectAI.DistributedObjectAI.__init__(self, air)
        self.air = air  # type: ToontownAIRepository
        self.bossConstructor = bossConstructor
        self.zoneIdr = zoneIdr

    def generate(self):
        DistributedObjectAI.DistributedObjectAI.generate(self)
        self.notify.debug('generate')

    def delete(self):
        self.notify.debug('delete')
        self.ignoreAll()
        DistributedObjectAI.DistributedObjectAI.delete(self)

    def createBossOffice(self, avIdList, hardmode = 0):
        bossZone = self.air.allocateZone()
        self.notify.debug('createBossOffice: %s' % bossZone)
        bossCog = self.bossConstructor(self.air)
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
