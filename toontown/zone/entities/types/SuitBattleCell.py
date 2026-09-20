from toontown.level import BasicEntities
from toontown.level.editor import EditorGlobals


class SuitBattleCell(BasicEntities.NodePathEntity):
    """
    SuitBattleCell(BasicEntities.NodePathEntity)

    A battle cell for a suit battle take place in
    """

    def __init__(self, level, entId):
        BasicEntities.NodePathEntity.__init__(self, level, entId)
        self.model = None
        if EditorGlobals.wantLevelEditor():
            self.model = loader.loadModel('phase_3/models/misc/sphere')
            self.model.setTransparency(1)
            self.model.setColorScale(1, 0.5, 0.0, 0.3)
            self.model.setScale(10, 10, 0.03)
            self.model.reparentTo(self)

    def destroy(self):
        if self.model:
            self.model.removeNode()
            self.model = None
        BasicEntities.NodePathEntity.destroy(self)
