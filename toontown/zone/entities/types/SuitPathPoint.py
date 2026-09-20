from toontown.level import BasicEntities
from toontown.level.editor import EditorGlobals


class SuitPathPoint(BasicEntities.NodePathEntity):
    """
    SuitPathPoint(BasicEntities.NodePathEntity)

    A point on a suit's path that dictates where they move in a level environment.
    """

    def __init__(self, level, entId):
        BasicEntities.NodePathEntity.__init__(self, level, entId)
        self.suitPathCollection = None
        self.model = None
        if EditorGlobals.wantLevelEditor():
            self.model = loader.loadModel('phase_3/models/misc/sphere')
            self.model.setScale(0.5)
            self.model.reparentTo(self)

    def destroy(self):
        self.suitPathCollection = None
        if self.model:
            self.model.removeNode()
            self.model = None
        BasicEntities.NodePathEntity.destroy(self)

    def setSuitPathCollection(self, suitPathCollection):
        self.suitPathCollection = suitPathCollection
