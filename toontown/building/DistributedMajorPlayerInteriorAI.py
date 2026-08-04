from direct.directnotify import DirectNotifyGlobal
from toontown.building.DistributedToonInteriorAI import DistributedToonInteriorAI
from toontown.building.DistributedHighRollerSigilvatorAI import DistributedHighRollerSigilvatorAI
from toontown.coghq.LobbyManagerAI import LobbyManagerAI
from toontown.suit import DistributedCashbotBossAI
from toontown.toonbase import ToontownGlobals


class DistributedMajorPlayerInteriorAI(DistributedToonInteriorAI):
    notify = DirectNotifyGlobal.directNotify.newCategory(
        'DistributedMajorPlayerInteriorAI')

    def __init__(self, block, air, zoneId, building):
        DistributedToonInteriorAI.__init__(
            self, block, air, zoneId, building)
        self.sigilvator = None
        self.createdMajorPlayerLobbyManager = False
        self.majorPlayerLobbyManager = getattr(
            self.air, 'majorPlayerLobbyManager', None)
        if self.majorPlayerLobbyManager is None:
            self.majorPlayerLobbyManager = LobbyManagerAI(
                self.air,
                DistributedCashbotBossAI.DistributedCashbotBossAI,
                ToontownGlobals.MajorPlayerLobby)
            self.majorPlayerLobbyManager.generateWithRequired(
                ToontownGlobals.MajorPlayerLobby)
            self.air.majorPlayerLobbyManager = self.majorPlayerLobbyManager
            self.createdMajorPlayerLobbyManager = True

    def generate(self):
        DistributedToonInteriorAI.generate(self)
        self.createSigilvator()

    def createSigilvator(self):
        if self.sigilvator:
            return
        self.sigilvator = DistributedHighRollerSigilvatorAI(
            self.air, self, ToontownGlobals.MajorPlayerLobby)
        self.sigilvator.generateWithRequired(self.zoneId)

    def createBossOffice(self, avIdList):
        if not self.majorPlayerLobbyManager:
            self.notify.warning(
                'createBossOffice: majorPlayerLobbyManager does not exist.')
            return 0
        return self.majorPlayerLobbyManager.createBossOffice(avIdList)

    def delete(self):
        if self.sigilvator:
            self.sigilvator.requestDelete()
            self.sigilvator = None
        if (self.createdMajorPlayerLobbyManager and
                self.majorPlayerLobbyManager):
            self.majorPlayerLobbyManager.requestDelete()
            if getattr(self.air, 'majorPlayerLobbyManager', None) is \
                    self.majorPlayerLobbyManager:
                del self.air.majorPlayerLobbyManager
            self.majorPlayerLobbyManager = None
        DistributedToonInteriorAI.delete(self)
