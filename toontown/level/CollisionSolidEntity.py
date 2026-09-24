from panda3d.core import *
from toontown.toonbase import ToontownGlobals
from toontown.level import BasicEntities
from toontown.level.editor import EditorGlobals
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class CollisionSolidEntity(BasicEntities.NodePathEntity):
    def __init__(self, level, entId):
        self.collNodePath = None
        BasicEntities.NodePathEntity.__init__(self, level, entId)
        self.initSolid()

    def destroy(self):
        self.destroySolid()
        BasicEntities.NodePathEntity.destroy(self)

    def initSolid(self):
        self.destroySolid()
        if self.solidType == 'sphere':
            solid = CollisionSphere(0, 0, 0, self.radius)
        else:
            solid = CollisionTube(0, 0, 0, 0, 0, self.length, self.radius)
        node = CollisionNode(self.getUniqueName(self.__class__.__name__))
        node.addSolid(solid)
        node.setCollideMask(ToontownGlobals.WallBitmask)
        self.collNodePath = self.attachNewNode(node)
        if EditorGlobals.wantLevelEditor():
            if self.showSolid:
                self.showCS()
            else:
                self.hideCS()

    def destroySolid(self):
        if self.collNodePath is not None:
            self.collNodePath.removeNode()
            self.collNodePath = None

    if EditorGlobals.wantLevelEditor():
        def attribChanged(self, attrib, value):
            print('attribChanged')
            self.initSolid()
