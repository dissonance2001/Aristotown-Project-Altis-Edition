"""EditMgrBase module: Contains the EditMgrBase class"""

from toontown.level import Entity
from toontown.level.editor import EditorGlobals
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class EditMgrBase(Entity.Entity):
    """This class contains EditMgr code shared between AI and client"""

    def __init__(self, level, entId):
        Entity.Entity.__init__(self, level, entId)

    def destroy(self):
        Entity.Entity.destroy(self)
        self.ignoreAll()

    if EditorGlobals.wantLevelEditor():
        def setInsertEntity(self, data):
            # tell the level who created this entity
            self.level.setEntityCreatorUsername(data['entId'], data['username'])
            # create the entity
            self.level.levelSpec.insertEntity(data['entId'], data['entType'], data['parentEntId'])
            # clear out the attrib, it shouldn't bekept in the spec
            self.level.levelSpec.doSetAttrib(self.entId, 'insertEntity', None)

        def setRemoveEntity(self, data):
            # clear out the attrib, it shouldn't be kept in the spec
            self.level.levelSpec.removeEntity(data['entId'])
            self.level.levelSpec.doSetAttrib(self.entId, 'removeEntity', None)
