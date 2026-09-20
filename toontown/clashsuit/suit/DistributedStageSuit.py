from toontown.clashsuit.suit import DistributedFactorySuit
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class DistributedStageSuit(DistributedFactorySuit.DistributedFactorySuit):
    

    def setCogSpec(self, spec):
        self.spec = spec
        self.setPos(spec['pos'])
        self.setH(spec['h'])
        self.originalPos = spec['pos']
        self.escapePos = spec['pos']
        self.pathEntId = spec['path']
        self.behavior = spec['behavior']
        self.skeleton = spec['skeleton']
        self.boss = spec['boss']
        self.revives = spec.get('revives')
        if self.reserve:
            self.reparentTo(hidden)
        else:
            self.doReparent()
        if self.boss:
            self.renameBoss()

    def renameBoss(self):
        nameInfo = self.createNameInfo()
        self.setDisplayName(nameInfo)
