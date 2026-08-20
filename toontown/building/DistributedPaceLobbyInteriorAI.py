from __future__ import absolute_import
from direct.directnotify import DirectNotifyGlobal
from toontown.building.DistributedToonInteriorAI import DistributedToonInteriorAI
from toontown.building.DistributedPaceElevatorAI import DistributedPaceElevatorAI
from toontown.building.DistributedHighRollerSigilvatorAI import DistributedHighRollerSigilvatorAI
from toontown.toonbase import ToontownGlobals
from toontown.toon import NPCToons
from toontown.instances import InstanceGlobals


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
        self.motoroomSigilvator = None
        self.paceCat = None
        self.paceLobbyManager = getattr(
            self.air, 'instanceZoneManager', None)

    def generate(self):
        DistributedToonInteriorAI.generate(self)
        self.createPaceElevator()
        self.createMotoroomSigilvator()
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

    def createMotoroomSigilvator(self):
        if self.motoroomSigilvator:
            return

        self.motoroomSigilvator = DistributedHighRollerSigilvatorAI(
            self.air,
            self,
            ToontownGlobals.PacesetterLobby,
            2
        )
        self.motoroomSigilvator.generateWithRequired(self.zoneId)

    def createBossOffice(self, avIdList, instanceId=None):
        manager = getattr(self.air, 'instanceZoneManager', None)
        if manager is None:
            self.notify.warning(
                'createBossOffice: InstanceZoneManagerAI is unavailable.'
            )
            return 0

        if instanceId is None:
            instanceId = InstanceGlobals.PACESETTER

        return manager.createInstance(avIdList, instanceId)

    def delete(self):
        if self.paceCat:
            self.paceCat.requestDelete()
            self.paceCat = None

        if self.motoroomSigilvator:
            self.motoroomSigilvator.requestDelete()
            self.motoroomSigilvator = None

        if self.paceElevator:
            self.paceElevator.requestDelete()
            self.paceElevator = None

        self.paceLobbyManager = None
        DistributedToonInteriorAI.delete(self)
