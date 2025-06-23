from toontown.building.DistributedToonInteriorAI import *
from toontown.toonbase import ToontownGlobals


class DistributedPaceLobbyInteriorAI(DistributedToonInteriorAI):
    notify = DirectNotifyGlobal.directNotify.newCategory("DistributedPaceLobbyInteriorAI")

    def createPaceElevator(self):
        PaceElevator = DistributedPaceElevatorAI(self.air, ToontownGlobals.PacesetterLobby)
        PaceElevator.generateWithRequired(ToontownGlobals.PacesetterLobby)
        self.PaceElevator.append(PaceElevator)
        PaceElevatorOrigin = render.find('**/elevator_origin')
        PaceElevator.reparentTo(PaceElevatorOrigin)