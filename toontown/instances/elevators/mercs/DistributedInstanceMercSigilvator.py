import random

from toontown.building import DistributedElevator
from toontown.building.DistributedSigilvator import DistributedSigilvator
from toontown.building.ElevatorConstants import *

from toontown.toonbase import TTLocalizer
from toontown.instances.mercs.InstanceMercGlobals import MercDefinitions
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class DistributedInstanceMercSigilvator(DistributedSigilvator):
    def __init__(self, cr):
        DistributedSigilvator.__init__(self, cr)
        self.type = ELEVATOR_INSTANCE_MERC_SIGIL
        self.countdownTime = ElevatorData[self.type]['countdown']
        self.mercDef = None
        self.mercDefEnum = None

    def setMercDefEnum(self, enum):
        self.mercDefEnum = enum
        self.mercDef = MercDefinitions[self.mercDefEnum]

    def getDestName(self):
        outputNames = []
        prefix = TTLocalizer.InstanceDifficultyPrefix % TTLocalizer.suitName(self.mercDef.cogName)
        for diffEnum in self.mercDef.makeDifficultyRange():
            outputNames.append(prefix + TTLocalizer.InstanceDifficultyToName[diffEnum])
        return outputNames
