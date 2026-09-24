from toontown.quest3.QuestEnums import QuestCollectable
from toontown.quest3.objectives.QuestCollectableObjective import QuestCollectableObjective
from toontown.safezone import DistributedCollectable, CollectableGlobals
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory



@DirectNotifyCategory()
class DistributedQuestCollectable(DistributedCollectable.DistributedCollectable):
    

    def __init__(self, cr):
        DistributedCollectable.DistributedCollectable.__init__(self, cr)
        self.treasureStyle = QuestCollectable.SwingsetA
        self.grabSound = None

    def announceGenerate(self):
        self.setupCollectable()

    def setupCollectable(self):
        fittingObjectives = base.localAvatar.getQuestObjectivesOfType(QuestCollectableObjective)
        if any(objective
               for objective in fittingObjectives
               if objective.collectable == self.treasureStyle):
            data = CollectableGlobals.TreasureModels.get(self.treasureStyle)
            if data is None:
                for thing in CollectableGlobals.TreasureModels.keys():
                    if isinstance(thing, tuple) and self.treasureStyle in thing:
                        data = CollectableGlobals.TreasureModels.get(thing)
                        break
            modelPath, grabSoundPath, scale, partToRemove, visible = data
            self.ignore('questsChanged')

            self.loadModel()
            self.startAnimation()
            self.nodePath.wrtReparentTo(render)
            self.accept(self.uniqueName('entertreasureSphere'), self.handleEnterSphere)

            if visible:
                self.dropShadow.show()
            else:
                self.dropShadow.hide()
        else:
            self.dropShadow.hide()
            self.accept('questsChanged', self.setupCollectable, extraArgs=[])

    def disable(self):
        self.ignore('questsChanged')
        DistributedCollectable.DistributedCollectable.disable(self)
