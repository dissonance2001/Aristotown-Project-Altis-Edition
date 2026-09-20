"""PersistentLevelEntityCreator module: contains the PersistentLevelEntityCreator class"""
from toontown.coghq.entities.PlatformEntity import PlatformEntity
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from toontown.level import EntityCreator
from toontown.zone.base.PersistentLevelMgr import PersistentLevelMgr
from toontown.zone.entities.types.TextEntity import TextEntity
from toontown.zone.entities.types.SuitPathPoint import SuitPathPoint
from toontown.zone.entities.types.SuitBattleCell import SuitBattleCell
from toontown.zone.entities.types.TunnelEntity import TunnelEntity
from toontown.zone.entities.quest.QuestModelEntity import QuestModelEntity
from toontown.zone.entities.quest.QuestAnimatedEntity import QuestAnimatedEntity
from toontown.zone.entities.quest.QuestInteractibleEntity import QuestInteractibleEntity


@DirectNotifyCategory()
class PersistentLevelEntityCreator(EntityCreator.EntityCreator):
    """
    PersistentLevelEntityCreator(EntityCreator)
    """

    def __init__(self, level):
        self.notify.debug('init level %s' % level)
        EntityCreator.EntityCreator.__init__(self, level)

        # create short aliases for EntityCreator create funcs
        nothing = EntityCreator.nothing
        fNonLocal = EntityCreator.eNonLocal

        self.privRegisterTypes({
            'levelMgr': PersistentLevelMgr,
            'crate': fNonLocal,
            'grid': fNonLocal,
            'tunnel': TunnelEntity,
            'suitPathPoint': SuitPathPoint,
            'suitPathCollection': fNonLocal,
            'suitBattleCell': SuitBattleCell,
            'building': fNonLocal,
            'buildingMgr': nothing,
            'textNode': TextEntity,
            'mover': fNonLocal,
            'platform': PlatformEntity,
            'quickElevator': fNonLocal,
            'questModel': QuestModelEntity,
            'questAnimated': QuestAnimatedEntity,
            'questInteractible': QuestInteractibleEntity,
            # TODO: Fill this in when it is implemented
            'questCollectible': nothing,
        })
