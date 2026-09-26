from direct.showbase.DirectObject import DirectObject
from direct.interval.IntervalGlobal import Func, LerpFunctionInterval, Sequence
from toontown.gui.GUINode import GUINode
from toontown.gui.game.condition.ConditionGlobals import AddTimedReleaseMsg, ConditionArg, ConditionSide, ConditionState, ConditionStateArgs, SideAnchors
from toontown.gui.game.condition.ScavengeConditionFrame import ScavengeConditionFrame
from toontown.inventory.base.InventoryItem import InventoryItem


class ScavengeConditionUIManager(DirectObject):
    sideAnchorPos = ( -1e-05, 0.0, 0.03528 )
    NODE_IN_SPEED = 0.27
    NODE_OUT_SPEED = 0.27

    def __init__(self):
        super().__init__()
        self.conditionState = ConditionState.GLOBAL
        self.conditionStateArgs = ConditionStateArgs()
        self.nodes = {
            ConditionSide.LEFT: GUINode(parent=SideAnchors[ConditionSide.LEFT], pos=self.sideAnchorPos, name='ConditionLeft')
        }
        self.nodesActive = {ConditionSide.LEFT: True}
        self.nodeActiveSeq = {ConditionSide.LEFT: None}
        self.objectOrder = {ConditionSide.LEFT: []}
        self.objectFrames = {ConditionSide.LEFT: {}}
        self.timedReleaseObjects = {}
        self.accept(AddTimedReleaseMsg, self.addTimedReleaseFrame)
        self.refresh()

    def cleanup(self):
        self.ignoreAll()
        self.removeAllTasks()
        for frame in list(self.objectFrames[ConditionSide.LEFT].values()):
            frame.destroy()
        self.objectFrames = {ConditionSide.LEFT: {}}
        self.objectOrder = {ConditionSide.LEFT: []}
        for seq in self.nodeActiveSeq.values():
            if seq:
                seq.pause()
        for node in self.nodes.values():
            node.destroy()
        self.nodes = {}
        self.timedReleaseObjects = {}

    def getObjects(self):
        return list(self.timedReleaseObjects.keys())

    def refresh(self):
        objects = [obj for obj in self.timedReleaseObjects.keys() if isinstance(obj, InventoryItem)]
        current = self.objectOrder[ConditionSide.LEFT]

        for obj in current[:]:
            if obj not in objects:
                frame = self.objectFrames[ConditionSide.LEFT].pop(obj, None)
                if frame:
                    frame.destroy()

        self.objectOrder[ConditionSide.LEFT] = objects
        frameDict = self.objectFrames[ConditionSide.LEFT]

        for obj in objects:
            if obj not in frameDict:
                frameDict[obj] = ScavengeConditionFrame(
                    parent=self.nodes[ConditionSide.LEFT],
                    obj=obj,
                    conditionState=self.conditionState,
                    conditionStateArgs=self.conditionStateArgs,
                    side=ConditionSide.LEFT,
                )

        for index, obj in enumerate(objects):
            frame = frameDict[obj]
            frame['conditionState'] = self.conditionState
            frame['conditionStateArgs'] = self.conditionStateArgs
            frame['side'] = ConditionSide.LEFT
            frame['index'] = index
            frame.setScale(frame.getFrameScale())
            frame.buildSubframes()

        self.place()

    def place(self):
        side = ConditionSide.LEFT
        objects = self.objectOrder[side]
        biggestDist = 0
        z = 0.4
        for obj in objects:
            frame = self.objectFrames[side][obj]
            z += frame.getEasyPadUp() * frame.getFrameScale()
            frame.setZGoal(z)
            z += frame.getEasyHeight() * frame.getFrameScale()
            frameBounds = frame.frame.getDefinedBounds()
            if frameBounds:
                left, right, *_ = frameBounds
                biggestDist = max(biggestDist, abs(right - left) * 1.1)

        node = self.nodes[side]
        if not objects:
            if not self.nodesActive[side]:
                return
            self.nodesActive[side] = False
            if self.nodeActiveSeq[side]:
                self.nodeActiveSeq[side].pause()
            width = -biggestDist
            def outIval(t=0):
                node.setX(lerp(0, width, t))
            self.nodeActiveSeq[side] = Sequence(
                LerpFunctionInterval(outIval, duration=self.NODE_OUT_SPEED, blendType='easeOut'),
                Func(node.hide),
            )
            self.nodeActiveSeq[side].start()
            return

        if not self.nodesActive[side]:
            self.nodesActive[side] = True
            if self.nodeActiveSeq[side]:
                self.nodeActiveSeq[side].pause()
            width = -biggestDist
            def inIval(t=0):
                node.setX(lerp(width, 0, t))
            self.nodeActiveSeq[side] = Sequence(
                Func(node.show),
                LerpFunctionInterval(inIval, duration=self.NODE_IN_SPEED, blendType='easeOut'),
            )
            self.nodeActiveSeq[side].start()
        else:
            node.show()
            node.setX(0)

    def removeTimedReleaseFrame(self, obj):
        self.timedReleaseObjects.pop(obj, None)
        self.removeTask(f'ConditionUIManager-RemoveTimedReleaseFrame-{id(obj)}')
        self.refresh()

    def addTimedReleaseFrame(self, obj, duration):
        if not isinstance(obj, InventoryItem):
            return
        self.timedReleaseObjects[obj] = duration
        self.removeTask(f'ConditionUIManager-RemoveTimedReleaseFrame-{id(obj)}')
        self.doMethodLater(
            duration,
            self.removeTimedReleaseFrame,
            name=f'ConditionUIManager-RemoveTimedReleaseFrame-{id(obj)}',
            extraArgs=[obj],
        )
        self.refresh()
