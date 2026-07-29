from direct.directnotify import DirectNotifyGlobal
from toontown.building.DistributedToonInteriorAI import DistributedToonInteriorAI
from toontown.building.DistributedPaceElevatorAI import DistributedPaceElevatorAI
from toontown.coghq.LobbyManagerAI import LobbyManagerAI
from toontown.suit import DistributedPacesetterBossAI
from toontown.toonbase import ToontownGlobals
from toontown.toon import NPCToons


class DistributedPaceLobbyInteriorAI(DistributedToonInteriorAI):
    notify = DirectNotifyGlobal.directNotify.newCategory(
        'DistributedPaceLobbyInteriorAI'
    )

    def __init__(self, blockNumber, air, zoneId, building):
        DistributedToonInteriorAI.__init__(
            self,
            blockNumber,
            air,
            zoneId,
            building
        )

        self.paceElevator = None
        self.paceCat = None
        self.createdPaceLobbyManager = False

        # Only create one manager.
        self.paceLobbyManager = getattr(
            self.air,
            'paceLobbyManager',
            None
        )

        if self.paceLobbyManager is None:
            self.paceLobbyManager = LobbyManagerAI(
                self.air,
                DistributedPacesetterBossAI.DistributedPacesetterBossAI,
                ToontownGlobals.PacesetterLobby
            )

            self.paceLobbyManager.generateWithRequired(
                ToontownGlobals.PacesetterLobby
            )

            self.air.paceLobbyManager = self.paceLobbyManager
            self.createdPaceLobbyManager = True

    def generate(self):
        DistributedToonInteriorAI.generate(self)
        self.createPaceElevator()
        self.createPaceCat()

    def createPaceCat(self):
        if self.paceCat:
            return

        npcId = 91999
        bodyColor = (0.298039, 0.298039, 0.349020, 1.0)
        white = (1.0, 1.0, 1.0, 1.0)
        gloves = white

        dna = (
            'css',
            'md',
            'm',
            'f',
            bodyColor,
            gloves,
            white,
            bodyColor,
            0,
            0,
            0,
            0,
            72,
            0
        )

        desc = (
            -1,
            'Sakamoreo',
            dna,
            'f',
            0,
            NPCToons.NPC_REGULAR
        )

        self.paceCat = NPCToons.createNPC(
            self.air,
            npcId,
            desc,
            self.zoneId
        )

        self.paceCat.b_setBackpack(111, 0, 0)
        self.paceCat.b_setHat(136, 0, 0)
        self.paceCat.b_setGlasses(50, 0, 0)

        self.paceCat.setPosHpr(
            -34.937,
            35.900,
            0.025,
            226.267,
            0,
            0
        )

        if hasattr(self.paceCat, 'd_setPosHpr'):
            self.paceCat.d_setPosHpr(
                -34.937,
                35.900,
                0.025,
                226.267,
                0,
                0
            )

    def createPaceElevator(self):
        if self.paceElevator:
            return

        self.paceElevator = DistributedPaceElevatorAI(
            self.air,
            self,
            ToontownGlobals.PacesetterLobby
        )

        self.paceElevator.generateWithRequired(self.zoneId)

    def createBossOffice(self, avIdList):
        if not self.paceLobbyManager:
            self.notify.warning(
                'createBossOffice: paceLobbyManager does not exist.'
            )
            return 0

        return self.paceLobbyManager.createBossOffice(avIdList)

    def delete(self):
        if self.paceCat:
            self.paceCat.requestDelete()
            self.paceCat = None

        if self.paceElevator:
            self.paceElevator.requestDelete()
            self.paceElevator = None

        if self.createdPaceLobbyManager and self.paceLobbyManager:
            self.paceLobbyManager.requestDelete()

            if getattr(self.air, 'paceLobbyManager', None) is self.paceLobbyManager:
                del self.air.paceLobbyManager

            self.paceLobbyManager = None

        DistributedToonInteriorAI.delete(self)