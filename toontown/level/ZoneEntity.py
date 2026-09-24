from toontown.level import ZoneEntityBase
from toontown.level import BasicEntities
from toontown.level.editor import EditorGlobals
from panda3d.core import ModelNode


class ZoneEntity(ZoneEntityBase.ZoneEntityBase, BasicEntities.NodePathAttribs):
    def __init__(self, level, entId):
        ZoneEntityBase.ZoneEntityBase.__init__(self, level, entId)
        self.nodePath = self.level.getZoneNode(self.entId)
        if self.nodePath is None:
            if EditorGlobals.wantLevelEditor():
                self.level.reportModelSpecSyncError('unknown zoneNum %s; zone was removed from model?' % self.entId)
            else:
                self.notify.error('zone %s not found in level model' % self.entId)

        if self.nodePath.node().isOfType(ModelNode.getClassType()) and getattr(self, 'wantFlatten', 1):
            self.nodePath.flattenMedium()

        BasicEntities.NodePathAttribs.initNodePathAttribs(self, doReparent=0)
        self.visibleZoneNums = {}
        self.incrementRefCounts(self.visibility)

    def destroy(self):
        BasicEntities.NodePathAttribs.destroy(self)
        ZoneEntityBase.ZoneEntityBase.destroy(self)

    def getNodePath(self):
        return self.nodePath

    def getVisibleZoneNums(self):
        return list(self.visibleZoneNums.keys())

    def incrementRefCounts(self, zoneNumList):
        for zoneNum in zoneNumList:
            self.visibleZoneNums.setdefault(zoneNum, 0)
            self.visibleZoneNums[zoneNum] += 1

    def decrementRefCounts(self, zoneNumList):
        for zoneNum in zoneNumList:
            self.visibleZoneNums[zoneNum] -= 1
            if self.visibleZoneNums[zoneNum] == 0:
                del self.visibleZoneNums[zoneNum]

    if EditorGlobals.wantLevelEditor():
        def setVisibility(self, visibility):
            self.decrementRefCounts(self.visibility)
            self.visibility = visibility
            self.incrementRefCounts(self.visibility)
            self.level.handleVisChange()
