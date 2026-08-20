from toontown.building import DistributedBuildingMgrAI
from toontown.toonbase import ToontownGlobals

class CountErfitBuildingMgrAI(DistributedBuildingMgrAI.DistributedBuildingMgrAI):
    def getDNABlockLists(self):
        blockLists = DistributedBuildingMgrAI.DistributedBuildingMgrAI.getDNABlockLists(self)
        if self.canonicalBranchId == ToontownGlobals.PolarPlace:
            blocks = blockLists[0]
            if 33 in blocks:
                blocks.remove(33)
        return blockLists
