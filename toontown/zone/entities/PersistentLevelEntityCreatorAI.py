"""PersistentLevelEntityCreatorAI module: contains the PersistentLevelEntityCreatorAI class"""
from toontown.coghq.entities.DistributedMoverAI import DistributedMoverAI
from toontown.level import EntityCreatorAI
from direct.showbase.PythonUtil import Functor
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory

from toontown.coghq.entities import DistributedCrateAI, DistributedGridAI
from toontown.zone.entities.types.DistributedBuildingEntityAI import DistributedBuildingEntityAI
from toontown.zone.entities.types.DistributedSuitPathCollectionAI import DistributedSuitPathCollectionAI
from toontown.zone.entities.types.SuitPathPointAI import SuitPathPointAI
from toontown.zone.entities.types.SuitBattleCellAI import SuitBattleCellAI
from toontown.zone.entities.types.BuildingMgrAI import BuildingMgrAI
from toontown.zone.entities.types.DistributedQuickElevatorEntityAI import DistributedQuickElevatorEntityAI
from toontown.zone.entities.quest.QuestInteractibleEntityAI import QuestInteractibleEntityAI


@DirectNotifyCategory()
class PersistentLevelEntityCreatorAI(EntityCreatorAI.EntityCreatorAI):
    """
    PersistentLevelEntityCreatorAI(EntityCreatorAI)
    """

    def __init__(self, level):
        self.notify.debug('init level %s' % level)
        EntityCreatorAI.EntityCreatorAI.__init__(self, level)

        # create short aliases for EntityCreatorAI create funcs
        cDE = EntityCreatorAI.createDistributedEntity
        cLE = EntityCreatorAI.createLocalEntity
        nothing = EntityCreatorAI.nothing

        # We may need a custom level manager AI version later, but for now we don't
        self.privRegisterTypes({
            'crate': Functor(cDE, DistributedCrateAI.DistributedCrateAI),
            'grid': Functor(cDE, DistributedGridAI.DistributedGridAI),
            'tunnel': nothing,
            'suitPathPoint': Functor(cLE, SuitPathPointAI),
            'suitPathCollection': Functor(cDE, DistributedSuitPathCollectionAI),
            'suitBattleCell': Functor(cLE, SuitBattleCellAI),
            'building': Functor(cDE, DistributedBuildingEntityAI),
            'buildingMgr': Functor(cLE, BuildingMgrAI),
            'textNode': nothing,
            'mover': Functor(cDE, DistributedMoverAI),
            'platform': nothing,
            'quickElevator': Functor(cDE, DistributedQuickElevatorEntityAI),
            'questModel': nothing,
            'questAnimated': nothing,
            'questInteractible': Functor(cLE, QuestInteractibleEntityAI),
            'questCollectible': nothing,
        })
