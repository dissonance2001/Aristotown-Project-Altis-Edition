from __future__ import absolute_import
from pandac.PandaModules import *
from direct.directnotify import DirectNotifyGlobal
from direct.interval.IntervalGlobal import *

from toontown.building.DistributedSigilvator import DistributedSigilvator
from toontown.instances import InstanceGlobals
from toontown.toonbase import ToontownGlobals
from toontown.building import PlutocratInstanceGlobals


class DistributedPlutocratSigilvator(DistributedSigilvator):
    notify = DirectNotifyGlobal.directNotify.newCategory(
        'DistributedPlutocratSigilvator')
    OriginName = 'sigilvator_origin'

    def __init__(self, cr):
        DistributedSigilvator.__init__(self, cr)
        self.doorOpenSfx = loader.loadSfx(
            'phase_9/audio/sfx/CHQ_door_open.ogg')
        self.doorCloseSfx = loader.loadSfx(
            'phase_9/audio/sfx/CHQ_door_close.ogg')

    def getInstanceId(self):
        return InstanceGlobals.PLUTOCRAT

    def setupElevator(self, task=None):
        result = DistributedSigilvator.setupElevator(self, task)
        if self.elevatorModel is not None and not self.elevatorModel.isEmpty():
            self.elevatorModel.setHpr(180, 0, 0)
        return result

    def getPortInterval(self):
        toons = []
        for avId in list(self.boardedAvIds.keys()):
            av = base.cr.doId2do.get(avId)
            if av:
                toons.append(av)

        teleportTrack = Parallel()
        for i, toon in enumerate(toons):
            toonPos = toon.getPos()
            toonPos[1] = toonPos[1] + 20.0
            if i == 0:
                toonPos[0] = toonPos[0] + 0.8
            elif i == 3:
                toonPos[0] = toonPos[0] - 0.8
            teleportTrack.append(Sequence(
                Wait(1.0),
                Parallel(
                    Func(toon.headsUp, toonPos),
                    Func(toon.loop, 'walk'),
                    LerpPosInterval(toon, 3.0, toonPos)),
                Func(toon.loop, 'neutral')))

        left = render.find('**/freezerdoor_L')
        right = render.find('**/freezerdoor_R')
        if left.isEmpty() or right.isEmpty():
            self.notify.warning(
                'Plutocrat freezer doors were not found; using safe fallback.')
            return DistributedSigilvator.getPortInterval(self)

        return Parallel(
            teleportTrack,
            Sequence(
                Parallel(
                    Func(base.playSfx, self.doorOpenSfx, node=right),
                    LerpHprInterval(
                        left, 0.9, (-127.45104, 0, 0),
                        blendType='easeIn'),
                    LerpHprInterval(
                        right, 0.9, (127.45104, 0, 0),
                        blendType='easeIn')),
                Parallel(
                    LerpHprInterval(
                        left, 0.3, (-118, 0, 0), blendType='easeOut'),
                    LerpHprInterval(
                        right, 0.3, (118, 0, 0), blendType='easeOut')),
                Wait(1.0),
                Parallel(
                    Sequence(
                        Wait(0.5),
                        Func(base.playSfx, self.doorCloseSfx, node=right)),
                    LerpHprInterval(
                        left, 1.2, (0, 0, 0), blendType='easeIn'),
                    LerpHprInterval(
                        right, 1.2, (0, 0, 0), blendType='easeIn'))))

    def _goToPlutocratInstance(self, zoneId):
        playGame = self.cr.playGame
        if not playGame:
            self.notify.warning('Cannot enter Plutocrat instance %s: PlayGame unavailable.' % zoneId)
            self._restoreFailedInstanceTransition()
            return
        hood = getattr(playGame, 'hood', None)
        townLoader = getattr(hood, 'loader', None)
        if (hood is None or getattr(hood, 'hoodId', None) != ToontownGlobals.TheBrrrgh or townLoader is None or not hasattr(townLoader, 'fsm')):
            self.notify.warning('Cannot enter Plutocrat instance outside The Brrrgh.')
            self._restoreFailedInstanceTransition()
            return
        requestStatus = {'loader': PlutocratInstanceGlobals.INSTANCE_LOADER, 'where': PlutocratInstanceGlobals.BOSS_BATTLE_STATE, 'how': 'teleportIn', 'hoodId': ToontownGlobals.TheBrrrgh, 'zoneId': zoneId, 'shardId': None, 'avId': -1, 'minibossId': InstanceGlobals.PLUTOCRAT, 'plutocratInstance': 1}
        if not townLoader.fsm.request('quietZone', [requestStatus]):
            self.notify.warning('Brrrgh town loader rejected Plutocrat instance %s.' % zoneId)
            self._restoreFailedInstanceTransition()

    def setBossOfficeZone(self, zoneId):
        if self.localToonOnBoard:
            self._goToPlutocratInstance(zoneId)

    def setBossOfficeZoneForce(self, zoneId):
        self._goToPlutocratInstance(zoneId)

    def enterClosed(self, ts):
        self.forceDoorsClosed()

    def getDestName(self):
        return 'Plutocrat'

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
