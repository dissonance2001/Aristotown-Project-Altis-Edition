import random

from toontown.building import DistributedElevator
from toontown.instances.elevators import DistributedInstanceElevator
from toontown.building.ElevatorConstants import *

#from toontown.quest3.QuestLocalizer import InstanceNotAvailable
from toontown.toonbase import TTLocalizer
from toontown.instances.mercs.InstanceMercGlobals import MercDefinitions, MercIdToQuestINADenial
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class DistributedInstanceMercElevator(DistributedInstanceElevator.DistributedInstanceElevator):
    MercElevatorModels = {
        'mplayer': 'phase_11/models/lawbotHQ/lawbotElevator',
        'psetter': 'phase_8/models/modules/ttcc_psetter_elevator'
    }
    DefaultElevatorFilePath = 'phase_5/models/cogdominium/tt_m_ara_csa_elevatorB'

    def __init__(self, cr):
        DistributedInstanceElevator.DistributedInstanceElevator.__init__(self, cr)
        self.type = ELEVATOR_INSTANCE_MERC
        self.elevatorModel = None
        self.countdownTime = ElevatorData[self.type]['countdown']
        self.mercDef = None
        self.mercDefEnum = None
        self.suitDisplay = None

    def disable(self):
        taskMgr.remove('setupInstanceMercElevatorDelay')
        DistributedInstanceElevator.DistributedInstanceElevator.disable(self)

    def delete(self):
        taskMgr.remove('setupInstanceMercElevatorDelay')
        DistributedInstanceElevator.DistributedInstanceElevator.delete(self)

    def setMercDefEnum(self, enum):
        self.mercDefEnum = enum
        self.mercDef = MercDefinitions[self.mercDefEnum]

    def setupElevator(self, _=None):
        geom = base.cr.playGame.hood.loader.geom
        if geom.isEmpty() or self.mercDef is None:
            taskMgr.doMethodLater(0.1, self.setupElevator, 'setupInstanceMercElevatorDelay')
            return

        # Load the elevator model.
        modelPath = self.MercElevatorModels.get(self.mercDef.cogName, self.DefaultElevatorFilePath)
        self.elevatorModel = loader.loadModel(modelPath)

        if self.zoneId != 19000:
            # normal load
            self.elevatorModel.reparentTo(render)
            origin = render.find('**/elevator_origin')
            if origin:
                self.elevatorModel.reparentTo(origin)
                origin.setH(180)
            if self.mercDef.cogName == 'chainsaw':
                self.elevatorModel.setPos(0, 10, 0)
            elif self.mercDef.cogName in ('mplayer', 'psetter'):
                origin.setH(0)
            self.leftDoor = self.elevatorModel.find('**/left_door')
            self.rightDoor = self.elevatorModel.find('**/right_door')
            DistributedElevator.DistributedElevator.setupElevator(self)
            self.elevatorSphereNodePath.setY(-1.42)
        else:
            # debug load in sky clan
            from toontown.instances.mercs.InstanceMercGlobals import mercDefinitionToEnum
            spawnPositions = (
                (12.712, -5.671, 2.663, 94.299),
                (26.498, -28.196, 5.684, 128.980),
                (10.864, -68.131, 5.020, -10.755),
                (-18.053, -76.354, 2.539, 41.657),
                (-80.263, -59.180, 0.075, -127.723),
                (-147.347, -7.564, 3.943, -60.219),
                (-118.503, 30.604, 4.643, -137.397),
                (24.981, 35.518, 0.624, 126.464),
                (40.498, -45.196, 10.141, 128.980),
            )
            x, y, z, h = spawnPositions[mercDefinitionToEnum(self.mercDef) - 1]
            self.elevatorModel.reparentTo(render)
            self.leftDoor = self.elevatorModel.find('**/left_door')
            self.rightDoor = self.elevatorModel.find('**/right_door')
            DistributedElevator.DistributedElevator.setupElevator(self)
            self.elevatorModel.setPos(x, y, z)
            self.elevatorModel.setH(h + 180)
            self.elevatorSphereNodePath.setY(-1.42)

            # put a suit head on top for the funny
            from toontown.suit import SuitDNA
            from toontown.suit import Suit
            s = Suit.Suit()
            d = SuitDNA.SuitDNA()
            d.newSuit(self.mercDef.cogName)
            s.setDNA(d)
            s.reparentTo(self.elevatorModel)
            s.setPos(0, 0, 12)
            s.setH(180)
            if self.mercDef.cogName == 'psetter':
                s.loop('neutral')
            else:
                s.loop(random.choice(['walk', 'run', 'neutral', 'victory', 'flail', 'tug-o-war', 'hypnotized', 'reach', 'landing', 'lured', 'sit-angry', 'sit-hungry-right', 'tray-walk', 'tray-neutral']))

    def getDestName(self):
        outputNames = []
        prefix = TTLocalizer.InstanceDifficultyPrefix % TTLocalizer.suitName(self.mercDef.cogName)
        for diffEnum in self.mercDef.makeDifficultyRange():
            outputNames.append(prefix + TTLocalizer.InstanceDifficultyToName[diffEnum])
        return outputNames

    #def getQuestRejectDialogue(self):
     #   return InstanceNotAvailable.get(MercIdToQuestINADenial.get(self.mercDefEnum))