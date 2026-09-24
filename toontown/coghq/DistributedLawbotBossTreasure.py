from panda3d.core import Point3
from direct.interval.IntervalGlobal import *

from toontown.safezone import DistributedTreasure
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from toontown.distributed.ToontownClientRepository import ToontownClientRepository


@DirectNotifyCategory()
class DistributedLawbotBossTreasure(DistributedTreasure.DistributedTreasure):
    """
    DistributedLawbotBossTreasure(DistributedTreasure)
    """

    def __init__(self, cr):
        """
        :param ToontownClientRepository cr: The client repository which maintains all client-side distributed objects.
        """
        DistributedTreasure.DistributedTreasure.__init__(self, cr)
        self.grabSoundPath = 'phase_4/audio/sfx/SZ_DD_treasure.ogg'
        self.style = None

    def setStyle(self, hoodId):
        self.style = hoodId

    def setLawyerId(self, lawyerId):
        self.lawyerId = lawyerId

    def setStartPosition(self, x, y, z):
        """
        :type x: float
        :type y: float
        :type z: float
        """
        self.startPosition = (x, y, z)

    def setFinalPosition(self, x, y, z):
        """
        :type x: float
        :type y: float
        :type z: float
        """
        if not self.nodePath:
            self.makeNodePath()
        if self.treasureFlyTrack:
            self.treasureFlyTrack.finish()
            self.treasureFlyTrack = None
        startPos = None
        lawyer = self.cr.doId2do.get(self.lawyerId)
        if lawyer:
            startPos = lawyer.getPos()
        else:
            if hasattr(self, 'startPosition') and self.startPosition:
                startPos = self.startPosition
        lerpTime = 1
        self.treasureFlyTrack = Sequence(
            Func(self.collNodePath.stash),
            Parallel(
                ProjectileInterval(
                    self.treasure,
                    startPos = Point3(0, 0, 0),
                    endPos = Point3(0, 0, 0),
                    duration = lerpTime,
                    gravityMult = 2.0),
                LerpPosInterval(self.nodePath, lerpTime, Point3(x, y, z), startPos = startPos)
            ),
            Func(self.collNodePath.unstash)
        )
        self.treasureFlyTrack.start()
