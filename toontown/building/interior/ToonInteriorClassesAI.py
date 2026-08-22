import math

from toontown.building.DistributedToonInteriorAI import DistributedToonInteriorAI
from toontown.instances.elevators.mercs.DistributedInstanceMercElevatorAI import DistributedInstanceMercElevatorAI
from toontown.instances.mercs import InstanceMercGlobals as IMG
from toontown.safezone.ChairConstants import ChairTypeEnum, MusicTypeEnum
from toontown.toonbase import ToontownGlobals

CustomToonInteriors = {}


def ToonInteriorAICls(cls):
    zoneIds = cls.ZONE_ID
    if type(zoneIds) not in (tuple, list):
        zoneIds = [zoneIds]

    for zoneId in zoneIds:
        if zoneId is None:
            continue
        if zoneId <= 0:
            raise AttributeError('%s has an invalid Zone ID! (%s)' % (cls.__name__, zoneId))
        if zoneId in CustomToonInteriors:
            raise AttributeError('%s tried to define Zone ID %s twice!' % (cls.__name__, zoneId))
        CustomToonInteriors[zoneId] = cls

    return cls


class DistributedCustomInteriorBaseAI(DistributedToonInteriorAI):
    ZONE_ID = 0
    UNCAPTURABLE = False
    WANT_INTERIOR_CHAIRS = False
    DOOR_DATA = None

    def __init__(self, *args, **kwargs):
        DistributedToonInteriorAI.__init__(self, *args, **kwargs)
        if not self.ZONE_ID:
            raise AttributeError("%s has no ZONE_ID!" % self.__class__.__name__)
        self.interiorObjects = []

    def announceGenerate(self):
        DistributedToonInteriorAI.announceGenerate(self)
        self.setupObjects()

    def setupObjects(self):
        pass

    def cleanupObjects(self):
        for obj in self.interiorObjects:
            obj.requestDelete()
        self.interiorObjects = []

    def delete(self):
        self.cleanupObjects()
        DistributedToonInteriorAI.delete(self)


class DistributedInteriorWithElevatorAI(DistributedCustomInteriorBaseAI):
    ElevatorClass = None

    def __init__(self, *args, **kwargs):
        DistributedCustomInteriorBaseAI.__init__(self, *args, **kwargs)
        self.elevator = None

    def setupObjects(self):
        DistributedCustomInteriorBaseAI.setupObjects(self)
        self.setupElevator()

    def elevatorExtraKwargs(self):
        return {}

    elevatorExtraKwargs = property(elevatorExtraKwargs)

    def setupElevator(self):
        if self.ElevatorClass is None:
            return
        self.elevator = self.ElevatorClass(
            self.air, self.air.instanceZoneManager, self.zoneId,
            **self.elevatorExtraKwargs
        )
        self.elevator.generateWithRequired(self.zoneId)
        self.interiorObjects.append(self.elevator)

    def cleanupObjects(self):
        DistributedCustomInteriorBaseAI.cleanupObjects(self)
        if hasattr(self, 'elevator'):
            del self.elevator


@ToonInteriorAICls
class DistributedPacesetterLobbyAI(DistributedInteriorWithElevatorAI):
    ZONE_ID = 9613
    WANT_INTERIOR_CHAIRS = True
    UNCAPTURABLE = True
    ElevatorClass = DistributedInstanceMercElevatorAI

    def elevatorExtraKwargs(self):
        return {'mercDef': IMG.MercDefinitions[IMG.MERC_PACESETTER]}

    elevatorExtraKwargs = property(elevatorExtraKwargs)