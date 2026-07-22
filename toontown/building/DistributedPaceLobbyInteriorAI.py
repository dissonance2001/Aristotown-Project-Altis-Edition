from direct.directnotify import DirectNotifyGlobal
from toontown.building.DistributedToonInteriorAI import DistributedToonInteriorAI
from toontown.building.DistributedPaceElevatorAI import DistributedPaceElevatorAI
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

    def generate(self):
        DistributedToonInteriorAI.generate(self)
        self.createPaceElevator()
        self.createPaceCat()

    def createPaceElevator(self):
        if self.paceElevator:
            return

        self.paceElevator = DistributedPaceElevatorAI(
            self.air,
            self,
            ToontownGlobals.PacesetterLobby
        )
        self.paceElevator.generateWithRequired(self.zoneId)

    def createPaceCat(self):
        if self.paceCat:
            return

        npcId = 91999
        bodyColor = (0.298039, 0.298039, 0.349020, 1.0)
        white = (1.0, 1.0, 1.0, 1.0)
        gloves = (133.0/255.0, 26.0/255.0, 94.0/255.0, 1.0)

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

        self.paceCat.b_setBackpack(1, 0, 0)

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

    def createBossOffice(self, avIdList):
        return self.building.createBossOffice(avIdList)

    def delete(self):
        if self.paceCat:
            self.paceCat.requestDelete()
            self.paceCat = None

        if self.paceElevator:
            self.paceElevator.requestDelete()
            self.paceElevator = None

        DistributedToonInteriorAI.delete(self)
