from pandac.PandaModules import *
from direct.directnotify import DirectNotifyGlobal
from direct.interval.IntervalGlobal import *

from toontown.building.DistributedSigilvator import DistributedSigilvator
from toontown.instances import InstanceGlobals
from toontown.toonbase import ToontownGlobals
from toontown.building import ChainsawInstanceGlobals
from toontown.building.ElevatorConstants import SigilvatorPoints, SigilJumpOutOffsets


class DistributedChainsawSigilvator(DistributedSigilvator):
    notify = DirectNotifyGlobal.directNotify.newCategory(
        'DistributedChainsawSigilvator')
    OriginName = 'sigilvator_origin'
    JumpOutOffsets = SigilJumpOutOffsets

    def __init__(self, cr):
        DistributedSigilvator.__init__(self, cr)
        self.elevatorPoints = SigilvatorPoints
        self.doorOpenSfx = loader.loadSfx(
            'phase_9/audio/sfx/CHQ_door_open.ogg')
        self.doorCloseSfx = loader.loadSfx(
            'phase_9/audio/sfx/CHQ_door_close.ogg')

    def getInstanceId(self):
        return InstanceGlobals.CHAINSAW

    def setupElevator(self, task=None):
        result = DistributedSigilvator.setupElevator(self, task)
        if self.elevatorModel is not None and not self.elevatorModel.isEmpty():
            self.elevatorModel.setHpr(180, 0, 0)
        return result

    def getDestinationWhere(self):
        return ChainsawInstanceGlobals.BOSS_BATTLE_STATE

    def getPortInterval(self):
        door = render.find('**/bossbot_door')
        if door.isEmpty():
            self.notify.warning(
                'Chainsaw bossbot door was not found; using safe fallback.')
            return DistributedSigilvator.getPortInterval(self)

        left = door.find('**/door_0')
        right = door.find('**/door_1')
        if left.isEmpty() or right.isEmpty():
            self.notify.warning(
                'Chainsaw boss door leaves were not found; using safe fallback.')
            return DistributedSigilvator.getPortInterval(self)

        toons = []
        for avId in sorted(list(self.boardedAvIds.keys()), key=lambda item: self.boardedAvIds[item]):
            av = base.cr.doId2do.get(avId)
            if av:
                toons.append(av)

        teleportTrack = Parallel()
        for index, toon in enumerate(toons):
            toonPos = toon.getPos(render)
            target = Point3(
                2 * (-1 if index < 2 else 1),
                toonPos[1] + 7.8 + (1.5 if index in (0, 3) else 0.0),
                toonPos[2])
            teleportTrack.append(Sequence(
                Wait(1.0),
                Parallel(
                    Func(toon.headsUp, target),
                    Func(toon.loop, 'walk'),
                    LerpPosInterval(toon, 2.0, target, other=render)),
                Func(toon.loop, 'neutral')))

        return Parallel(
            teleportTrack,
            Sequence(
                Parallel(
                    Func(base.playSfx, self.doorOpenSfx, node=door),
                    LerpHprInterval(
                        left, 0.6, (-127.45104, 0, 0),
                        blendType='easeIn'),
                    LerpHprInterval(
                        right, 0.6, (127.45104, 0, 0),
                        blendType='easeIn')),
                Parallel(
                    LerpHprInterval(
                        left, 0.3, (-118, 0, 0), blendType='easeOut'),
                    LerpHprInterval(
                        right, 0.3, (118, 0, 0), blendType='easeOut')),
                Wait(1.6),
                Parallel(
                    Sequence(
                        Wait(0.5),
                        Func(base.playSfx, self.doorCloseSfx, node=door)),
                    LerpHprInterval(
                        left, 0.8, (0, 0, 0), blendType='easeIn'),
                    LerpHprInterval(
                        right, 0.8, (0, 0, 0), blendType='easeIn'))))

    def _goToChainsawInstance(self, zoneId):
        playGame = self.cr.playGame
        if not playGame:
            self.notify.warning(
                'Cannot enter Chainsaw instance %s: PlayGame unavailable.' %
                zoneId)
            self._restoreFailedInstanceTransition()
            return

        hood = getattr(playGame, 'hood', None)
        townLoader = getattr(hood, 'loader', None)
        if (hood is None or
                getattr(hood, 'hoodId', None) != ToontownGlobals.OutdoorZone or
                townLoader is None or
                not hasattr(townLoader, 'fsm')):
            self.notify.warning(
                'Cannot enter Chainsaw instance outside Acorn Acres.')
            self._restoreFailedInstanceTransition()
            return

        requestStatus = {
            'loader': ChainsawInstanceGlobals.INSTANCE_LOADER,
            'where': ChainsawInstanceGlobals.BOSS_BATTLE_STATE,
            'how': 'teleportIn',
            'hoodId': ToontownGlobals.OutdoorZone,
            'zoneId': zoneId,
            'shardId': None,
            'avId': -1,
            'minibossId': InstanceGlobals.CHAINSAW,
            'chainsawInstance': 1,
        }
        if not townLoader.fsm.request('quietZone', [requestStatus]):
            self.notify.warning(
                'Acorn Acres town loader rejected Chainsaw instance %s.' %
                zoneId)
            self._restoreFailedInstanceTransition()

    def setBossOfficeZone(self, zoneId):
        if self.localToonOnBoard:
            self._goToChainsawInstance(zoneId)

    def setBossOfficeZoneForce(self, zoneId):
        self._goToChainsawInstance(zoneId)

    def getDestName(self):
        return 'Chainsaw Consultant'

    @property
    def closeTime(self):
        return 4.0

    def delete(self):
        if self.doorOpenSfx:
            self.doorOpenSfx.stop()
            self.doorOpenSfx = None
        if self.doorCloseSfx:
            self.doorCloseSfx.stop()
            self.doorCloseSfx = None
        DistributedSigilvator.delete(self)
