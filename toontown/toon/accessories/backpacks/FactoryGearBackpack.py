from toontown.toon.accessories.ToonAccessory import ToonAccessory
from toontown.toon import ToonDNA
from direct.interval.IntervalGlobal import *
from panda3d.core import *


class FactoryGearBackpack(ToonAccessory):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sequence = None

    def load(self):
        super().load()
        self.async_addLoadCallback(self._openEvents)

    def _openEvents(self):
        if self.toon.isLocal():
            self.accept(base.localAvatar.SprintStartMessage, self.__localToonStartSprint)
            self.accept(base.localAvatar.SprintStopMessage, self.__localToonStopSprint)

    def __localToonStartSprint(self):
        place = base.localAvatar.getPlace()
        if not place:
            return
        state = place.getState()
        if state not in ('Walk', 'FinalBattle'):
            return

        if self.sequence and self.sequence.isPlaying():
            self.sequence.setPlayRate(3.0)

    def __localToonStopSprint(self):
        if self.sequence and self.sequence.isPlaying():
            self.sequence.setPlayRate(1.0)

    def _loadModel(self):
        """Loads the accessory model"""
        itemDef = self.item.getItemDefinition()
        modelPath = itemDef.getModelPath()
        loadReq = base.asyncRequestMgr.loadModel(modelPath, callback=self.load_postModelLoad)
        self.async_loadRequests.append(loadReq)

    def load_postModelLoad(self, model):
        for nodePiece in model.findAllMatches('**/+CollisionNode'):
            nodePiece.removeNode()
        self.gearGeom = model

        self.accessoryGeom = NodePath('FactoryGearBackpack-modelHolder')
        self.gearGeom.reparentTo(self.accessoryGeom)

        self._loadTexture()
        self._positionAccessory()
        self._attachAccessory()

        self.fixupAccessoryGeom()
        self.async_loadDone()

    def start(self):
        if self.sequence:
            return

        self.sequence = Sequence(
            self.gearGeom.hprInterval(5, (-360, 0, 0)),
            Func(self.gearGeom.setH, 0),
        )
        self.sequence.loop()

    def stop(self):
        if self.sequence:
            self.sequence.finish()
            self.sequence = None

    def unload(self):
        super().unload()
        self.ignoreAll()
        if getattr(self, 'gearGeom', None) and not self.gearGeom.isEmpty():
            self.gearGeom.removeNode()
        self.gearGeom = None
