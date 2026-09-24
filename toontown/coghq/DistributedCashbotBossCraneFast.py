from direct.distributed.ClockDelta import *
from direct.fsm import FSM
from direct.interval.IntervalGlobal import *
from toontown.coghq.cashbothq import DistributedCashbotBossCrane
from toontown.coghq.cashbothq import DistributedCashbotBossSafe
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from toontown.distributed.ToontownClientRepository import ToontownClientRepository


@DirectNotifyCategory()
class DistributedCashbotBossCraneFast(DistributedCashbotBossCrane.DistributedCashbotBossCrane, FSM.FSM):
    """
    DistributedCashbotBossCraneFast(DistributedCashbotBossCrane, FSM)

    This class represents a (side) crane holding a magnet on a cable.

    Controls the smaller cranes that are hypotenuse to the normal cranes.

    The DistributedCashbotBoss creates four of these for the CFO battle scene.
    """

    firstMagnetBit = 21

    craneMinY = 8
    craneMaxY = 30

    armMinH = -12.5
    armMaxH = 12.5

    # How high to place the shadows.  We can put these pretty high
    # because we play that trick with the bins to make them render
    # after other stuff.
    shadowOffset = 1

    # The properties when the magnet is unencumbered.
    emptyFrictionCoef = 0.1
    emptySlideSpeed = 15  # feet per second
    emptyRotateSpeed = 20  # degrees per second

    # These points will be useful for sticking the control stick into the toon's hands.
    lookAtPoint = Point3(0.3, 0, 0.1)
    lookAtUp = Vec3(0, -1, 0)

    neutralStickHinge = VBase3(0, 90, 0)

    magnetModel = loader.loadModel('phase_10/models/cogHQ/CBMagnetRed.bam')

    def __init__(self, cr):
        """
        :param ToontownClientRepository cr: The client repository which maintains all client-side distributed objects.
        """
        DistributedCashbotBossCrane.DistributedCashbotBossCrane.__init__(self, cr)
        FSM.FSM.__init__(self, 'DistributedCashbotBossCraneFast')

        self.magnetOnSfx = base.loader.loadSfx('phase_10/audio/sfx/CBHQ_CFO_red_magnet_on.ogg')
        self.magnetLoopSfx = base.loader.loadSfx('phase_10/audio/sfx/CBHQ_CFO_red_magnet_loop.ogg')
        self.magnetSoundInterval = Parallel(
            SoundInterval(self.magnetOnSfx),
            Sequence(
                Wait(0.5),
                Func(base.playSfx, self.magnetLoopSfx, looping = 1)
            )
        )

    def grabObject(self, obj):
        """
        Responsible for the pushing simulation of red cranes.
        """
        if isinstance(obj, DistributedCashbotBossSafe.DistributedCashbotBossSafe):
            return
        else:
            DistributedCashbotBossCrane.DistributedCashbotBossCrane.grabObject(self, obj)

    @property
    def craneType(self):
        return 'Fast'
