from toontown.events.apriltoons.findthefamily import FindTheFamilyGlobals
from toontown.clashsuit.suit.DistributedFactorySuit import DistributedFactorySuit
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class DistributedFindTheFamilySuit(DistributedFactorySuit):
    DualCoreUpdateNametagTask = 'DistributedFindTheFamilySuit-DualCoreUpdateNametagTask'

    def __init__(self, cr):
        super().__init__(cr)
        self.isSkeleton = 0
        self.overriddenName = None
        self.isNuclear = 0
        self.specialContainerId = -1
        self.specialContainer = None
        self.startedFreakout = False

    def startHeadFreakout(self):
        if self.startedFreakout:
            return
        if not (self.specialHead and self.isNuclear):
            return

        self.startedFreakout = True
        self.specialHead.startFreakout()
        self.specialHead.listenForEvents()

    def stopHeadFreakout(self):
        self.startedFreakout = False
        self.specialHead.stopAllFreakout()

    def setNuclear(self, isNuclear):
        self.isNuclear = isNuclear
        self.startHeadFreakout()
        if isNuclear == 2:
            self.__startUpdateNametagTask()

    def isFinalNuclear(self):
        # Used for the BML
        return self.isNuclear == 2

    def __startUpdateNametagTask(self):
        self.removeTask(self.uniqueName(self.DualCoreUpdateNametagTask))
        self.doMethodLater(0.06, self.__updateNametagTask, name=self.uniqueName(self.DualCoreUpdateNametagTask))

    def __updateNametagTask(self, task=None):
        self.overrideDisplayName(self.specialContainer.suitName)
        return task.again

    def generateCustomHead(self, headType, skeleton=False):
        super().generateCustomHead(headType, skeleton=skeleton)
        self.startHeadFreakout()

    def setSpecialContainerId(self, specialContainerId):
        self.specialContainerId = specialContainerId
        self.specialContainer = FindTheFamilyGlobals.FamilyRegistry[specialContainerId]
        self.overrideDisplayName(self.specialContainer.suitName)
        self.startHeadFreakout()

    def overrideDisplayName(self, displayName):
        self.overriddenName = displayName
        self.setName(self.overriddenName)
        nameInfo = self.createNameInfo()
        self.setDisplayName(nameInfo)

    def createNameInfo(self, wantDept=True):
        nameInfo = super().createNameInfo(wantDept=wantDept)
        if self.isNuclear == 1:
            nameInfo = f'{nameInfo}\n\1white\1\5icon_greenCircle\5\2 Unstable \1white\1\5icon_greenCircle\5\2'
        elif self.isNuclear == 2:
            nameInfo = f'{nameInfo}\n\1ftf_dualCoreColor\1\5icon_clubTriangleWhite\5\2 Nuclear \1ftf_dualCoreColor\1\5icon_clubTriangleWhite\5\2'
        return nameInfo

    def delete(self):
        self.removeTask(self.uniqueName(self.DualCoreUpdateNametagTask))
        super().delete()
        self.overriddenName = None
        self.specialContainer = None
