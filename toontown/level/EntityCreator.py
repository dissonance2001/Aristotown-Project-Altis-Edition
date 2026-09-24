"""EntityCreator module: contains the EntityCreator class"""
from toontown.level import EntityCreatorBase

from toontown.level import CutScene
from toontown.level import BasicEntities
from toontown.level.editor import EditMgr
from toontown.level import EntrancePoint
from toontown.level import LevelMgr
from toontown.level import LogicGate
from toontown.level import ZoneEntity
from toontown.level import ModelEntity
from toontown.level import PathEntity
from toontown.level import VisibilityExtender
from toontown.level import PropSpinner
from toontown.level import AmbientSound
from toontown.level import LocatorEntity
from toontown.level import CollisionSolidEntity
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


# some useful constructor functions
# ctor functions must take (level, entId)
# and they must return the entity that was created, or 'nothing'
def nothing(*args):
    """For entities that don't exist on the client at all"""
    return 'nothing'


def eNonLocal(*args):
    """For entities that don't need to be created by the client and will
    show up independently (they're distributed and created by the AI)"""
    return 'nonlocal'


@DirectNotifyCategory()
class EntityCreator(EntityCreatorBase.EntityCreatorBase):
    """
    This class is responsible for creating instances of Entities on the
    client. It can be subclassed to handle more Entity types.
    """

    def __init__(self, level):
        EntityCreatorBase.EntityCreatorBase.__init__(self, level)
        self.level = level
        self.privRegisterTypes({'attribModifier': nothing,
                                'ambientSound': AmbientSound.AmbientSound,
                                'collisionSolid': CollisionSolidEntity.CollisionSolidEntity,
                                'cutScene': CutScene.CutScene,
                                'editMgr': EditMgr.EditMgr,
                                'entityGroup': nothing,
                                'entrancePoint': EntrancePoint.EntrancePoint,
                                'levelMgr': LevelMgr.LevelMgr,
                                'locator': LocatorEntity.LocatorEntity,
                                'logicGate': LogicGate.LogicGate,
                                'model': ModelEntity.ModelEntity,
                                'nodepath': BasicEntities.NodePathEntity,
                                'path': PathEntity.PathEntity,
                                'propSpinner': PropSpinner.PropSpinner,
                                'visibilityExtender': VisibilityExtender.VisibilityExtender,
                                'zone': ZoneEntity.ZoneEntity})

    def doCreateEntity(self, ctor, entId):
        return ctor(self.level, entId)
