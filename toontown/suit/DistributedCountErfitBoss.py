from __future__ import absolute_import
from direct.directnotify import DirectNotifyGlobal
from direct.interval.IntervalGlobal import Sequence, Func

from toontown.suit import DistributedBossCog
from toontown.suit import DistributedCountErclaimBoss as CountErclaimBossModule
from toontown.suit.DistributedCountErclaimBoss import DistributedCountErclaimBoss
from toontown.building import ElevatorConstants
from toontown.building import ElevatorUtils
from toontown.toonbase import ToontownGlobals


OneBossCog = None


class DistributedCountErfitBoss(DistributedCountErclaimBoss):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedCountErfitBoss')

    def __init__(self, cr):
        DistributedCountErclaimBoss.__init__(self, cr)
        self.elevatorType = ElevatorConstants.ELEVATOR_ERFIT

    def announceGenerate(self):
        global OneBossCog
        DistributedCountErclaimBoss.announceGenerate(self)
        try:
            base.localAvatar.chatMgr.chatInputSpeedChat.removeCJMenu()
        except:
            pass
        self.setName('Count Erfit')
        self.setDisplayName('Count Erfit')
        self.elevatorMusic = base.loader.loadMusic('phase_13/audio/bgm/april_toons/erfit/elevator_countErfit_1.ogg')
        OneBossCog = self

    def disable(self):
        global OneBossCog
        if OneBossCog == self:
            OneBossCog = None
        DistributedCountErclaimBoss.disable(self)

    def placeToonInElevator(self, toon):
        toon.setCogIndex(-1)
        toonIndex = self.involvedToons.index(toon.doId)
        toon.reparentTo(self.elevatorModel)
        toon.setPos(*ElevatorConstants.ElevatorPoints[toonIndex])
        toon.setHpr(180, 0, 0)
        toon.loop('neutral')

    def enterElevator(self):
        for toonId in self.involvedToons:
            toon = self.cr.doId2do.get(toonId)
            if toon:
                toon.setCogIndex(-1)
                toon.stopLookAround()
                toon.stopSmooth()
                self.placeToonInElevator(toon)

        self.toMovieMode()
        camera.reparentTo(self.elevatorModel)
        camera.setPosHpr(0, 14, 4, 180, 0, 0)
        base.camLens.setMinFov(ToontownGlobals.CBElevatorFov / (4.0 / 3.0))
        base.playMusic(self.elevatorMusic, looping=1, volume=1.0)
        try:
            base.transitions.fadeIn(0.8)
        except:
            pass
        ival = Sequence(
            ElevatorUtils.getRideElevatorInterval(self.elevatorType),
            ElevatorUtils.getRideElevatorInterval(self.elevatorType),
            self.openDoors,
            Func(camera.wrtReparentTo, render),
            Func(self._doneErfitElevator))
        intervalName = 'ElevatorMovie'
        ival.start()
        self.storeInterval(ival, intervalName)

    def _doneErfitElevator(self):
        self.doneBarrier('Elevator')

    def exitElevator(self):
        intervalName = 'ElevatorMovie'
        self.clearInterval(intervalName)
        self.elevatorMusic.stop()
        ElevatorUtils.closeDoors(self.leftDoor, self.rightDoor, self.elevatorType)

    def loseSuits(self):
        return Sequence()
