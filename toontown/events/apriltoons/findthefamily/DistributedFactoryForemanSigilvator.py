from direct.interval.IntervalGlobal import *
from toontown.events.apriltoons.findthefamily.FakeFactoryDoor import FakeFactoryDoor
from toontown.instances.elevators.DistributedSigilvator import DistributedSigilvator
from toontown.groups import GroupGlobals
from toontown.toonbase import TTLocalizer, ToontownGlobals
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from toontown.distributed.ToontownClientRepository import ToontownClientRepository


EntranceId2IntId = {
    2: ToontownGlobals.SellbotFindForemanInt,
    4: ToontownGlobals.SellbotOcFindFamilyInt,
}


class DistributedFactoryForemanSigilvator(DistributedSigilvator):
    """
    DistributedFactoryForemanSigilvator(DistributedSigilvator)
    """

    def __init__(self, cr):
        super().__init__(cr)
        self.__initializeLevel = 0
        self.factoryDoor = FakeFactoryDoor(wantVoid=True)

    def disable(self):
        super().disable()
        if self.factoryDoor:
            self.factoryDoor.cleanup()
            self.factoryDoor = None

    @property
    def closeTime(self):
        return 7.5

    def setEntranceId(self, entranceId):
        self.entranceId = entranceId
        self.checkInitialized()

    def getElevatorEntranceType(self):
        return GroupGlobals.facilityZone2EntranceType.get(EntranceId2IntId[self.entranceId], ToontownGlobals.SellbotFactoryInt)

    def setBldgDoId(self, bldgDoId):
        """
        The doId is junk, there is no building object for the factory exterior elevators.

        Do the appropriate things that DistributedElevator.gotBldg does.
        """
        self.bldg = None
        self.checkInitialized()

    def checkInitialized(self):
        self.__initializeLevel += 1
        if self.__initializeLevel >= 2:
            self.onFullInitialize()

    def onFullInitialize(self):
        self.setupElevator()

    def finishSetup(self):
        super().finishSetup()
        self.factoryDoor.reparentTo(self.getElevatorModel().getParent())
        self.factoryDoor.setPos(0, -10, 0)
        self.factoryDoor.setHpr(0, -4, 0)
        self.factoryDoor.fsm.request('closed')

    @property
    def ourElevatorOrigin(self):
        return f'sigilvator_origin_{self.entranceId}'

    def getZoneId(self):
        """
        :returns: the current zone ID.
        :rtype: int
        """
        return 0

    def __doorsClosed(self, zoneId):
        """
        :type zoneId: int
        """
        pass

    def setFactoryInteriorZone(self, zoneId):
        """
        :type zoneId: int
        """
        if self.localToonOnBoard:
            hoodId = self.cr.playGame.hood.hoodId
            doneStatus = {
                'loader': 'cogHQLoader',
                'where': 'factoryInterior',
                'how': 'TeleportIn',
                'zoneId': zoneId,
                'hoodId': hoodId,
                'entranceId': self.entranceId,
            }
            self.cr.playGame.getPlace().elevator.signalDone(doneStatus)

    def setFactoryInteriorZoneForce(self, zoneId):
        """
        :type zoneId: int
        """
        place = self.cr.playGame.getPlace()
        if place:
            place.request('Elevator', self, 1)
            hoodId = self.cr.playGame.hood.hoodId
            doneStatus = {
                'loader': 'cogHQLoader',
                'where': 'factoryInterior',
                'how': 'TeleportIn',
                'zoneId': zoneId,
                'hoodId': hoodId,
                'entranceId': self.entranceId
            }
            if hasattr(place, 'elevator') and place.elevator:
                place.elevator.signalDone(doneStatus)
            else:
                self.notify.warning("setMintInteriorZoneForce: Couldn't find playGame.getPlace().elevator, zoneId: %s" % zoneId)
        else:
            self.notify.warning("setFactoryInteriorZoneForce: Couldn't find playGame.getPlace(), zoneId: %s" % zoneId)

    def getDestName(self):
        if self.entranceId == 2:
            return TTLocalizer.ElevatorSellBotFactory2
        elif self.entranceId == 4:
            return TTLocalizer.ElevatorSellBotFactory4

    def sigilPlacementFailed(self):
        # Run it back!!!
        taskMgr.doMethodLater(0.1, self.setupElevator, 'setupSigilvatorDelay', extraArgs=[])

    def getPortInterval(self):
        toons = []
        for avId in list(self.boardedAvIds.keys()):
            av = base.cr.doId2do.get(avId)
            if av:
                toons.append(av)

        ival = Sequence()
        teleportTrack = Parallel()

        for i, toon in enumerate(toons):
            toon.setPlayRate(1.0, 'walk')
            fooNode = toon.attachNewNode('foo-sigilvator')
            fooNode.wrtReparentTo(self.getElevatorModel().getParent())
            toonPos = fooNode.getPos()
            toonPos[1] = toonPos[1] - 20.0
            if i == 0:
                toonPos[0] = toonPos[0] + 0.8
            elif i == 3:
                toonPos[0] = toonPos[0] - 0.8
            track = Sequence(
                Wait(1.5),
                Parallel(
                    Func(toon.headsUp, self.getElevatorModel().getParent(), toonPos),
                    Func(toon.loop, 'walk'),
                    LerpPosInterval(toon, 5.5, toonPos, other=self.getElevatorModel().getParent()),
                ),
                Func(fooNode.removeNode),
            )
            track.append(Func(toon.loop, 'neutral'))
            teleportTrack.append(track)
        ival.append(Parallel(
            teleportTrack,
            Sequence(
                Func(self.factoryDoor.fsm.request, 'opening'),
                Wait(3.0),
                Func(self.factoryDoor.fsm.request, 'open'),
                Wait(1.5),
                Func(self.factoryDoor.fsm.request, 'closing'),
                Wait(3.0),
                Func(self.factoryDoor.fsm.request, 'closed'),
            )
        ))
        return ival
