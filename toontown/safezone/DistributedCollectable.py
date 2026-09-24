from panda3d.core import *
from panda3d.direct import *
from direct.interval.IntervalGlobal import *
from toontown.toonbase.ToontownGlobals import *
from direct.distributed import DistributedObject
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from toontown.safezone import CollectableGlobals



@DirectNotifyCategory()
class DistributedCollectable(DistributedObject.DistributedObject):
    

    def __init__(self, cr):
        DistributedObject.DistributedObject.__init__(self, cr)
        self.av = None
        self.treasureFlyTrack = None
        self.nodePath = None
        self.dropShadow = None
        self.rejectSoundPath = 'phase_4/audio/sfx/ring_miss.ogg'
        self.playSoundForRemoteToons = 1
        self.scale = 1.0
        self.shadow = 1
        self.fly = 1
        self.zOffset = 0.0
        self.billboard = 0
        self.treasureStyle = None
        self.bounceSequence = None

    def disable(self):
        self.ignoreAll()
        self.nodePath.detachNode()
        DistributedObject.DistributedObject.disable(self)

    def delete(self):
        self.stopAnimation()
        if self.treasureFlyTrack:
            self.treasureFlyTrack.finish()
            self.treasureFlyTrack = None
        DistributedObject.DistributedObject.delete(self)
        self.nodePath.removeNode()

    def announceGenerate(self):
        DistributedObject.DistributedObject.announceGenerate(self)
        self.loadModel()
        self.startAnimation()
        self.nodePath.wrtReparentTo(render)
        self.accept(self.uniqueName('entertreasureSphere'), self.handleEnterSphere)

    def handleEnterSphere(self, collEntry = None):
        localAvId = base.localAvatar.getDoId()
        if not self.fly:
            self.handleGrab(localAvId)

        self.d_requestGrab()

    def d_requestGrab(self):
        self.sendUpdate('requestGrab', [])

    def getSphereRadius(self):
        return 2.0

    def loadModel(self):
        infoTuple = None
        for key, val in CollectableGlobals.TreasureModels.items():
            if type(key) is tuple:
                if self.treasureStyle in key:
                    infoTuple = val
                    break
            elif key == self.treasureStyle:
                infoTuple = val
                break
        if infoTuple is None:
            raise KeyError("CollectableGlobals did not define a TreasureModel for the QuestColelctable")
        modelPath, grabSoundPath, scale, partToRemove, visible = infoTuple

        self.grabSound = base.loader.loadSfx(grabSoundPath)
        self.rejectSound = base.loader.loadSfx(self.rejectSoundPath)
        if self.nodePath is None:
            self.makeNodePath()
        else:
            self.treasure.getChildren().detach()
        model = loader.loadModel(modelPath)
        if partToRemove:
            model.find(partToRemove).removeNode()
        model.setScale(scale)
        model.reparentTo(self.treasure)
        if not visible:
            model.hide()

    def makeNodePath(self):
        self.nodePath = NodePath(self.uniqueName('treasure'))
        self.nodePath.setScale(0.9 * self.scale)
        self.treasure = self.nodePath.attachNewNode('treasure')
        if self.shadow:
            if not self.dropShadow:
                self.dropShadow = loader.loadModel('phase_3/models/props/drop_shadow')
                self.dropShadow.setColor(0, 0, 0, 0.5)
                self.dropShadow.setPos(0, 0, 0.025)
                self.dropShadow.setScale(0.4 * self.scale)
                self.dropShadow.flattenLight()
            self.dropShadow.reparentTo(self.nodePath)
        collSphere = CollisionSphere(0, 0, 0, self.getSphereRadius())
        collSphere.setTangible(0)
        collNode = CollisionNode(self.uniqueName('treasureSphere'))
        collNode.setIntoCollideMask(WallBitmask)
        collNode.addSolid(collSphere)
        self.collNodePath = self.nodePath.attachNewNode(collNode)
        self.collNodePath.stash()

    def getParentNodePath(self):
        return render

    def setTreasureStyle(self, treasureStyle):
        self.treasureStyle = treasureStyle

    def setPosition(self, x, y, z):
        if not self.nodePath:
            self.makeNodePath()
        self.nodePath.reparentTo(self.getParentNodePath())
        self.nodePath.setPos(x, y, z + self.zOffset)
        self.collNodePath.unstash()

    def setGrab(self, avId):
        if avId == 0:
            return
        if self.fly or avId != base.localAvatar.getDoId():
            self.handleGrab(avId)

    def setReject(self, avId):
        if avId == 0:
            return
        if avId != base.localAvatar.getDoId():
            return

        if self.treasureFlyTrack:
            self.treasureFlyTrack.finish()
            self.treasureFlyTrack = None
        base.playSfx(self.rejectSound, node = self.nodePath)
        self.treasureFlyTrack = Sequence(LerpColorScaleInterval(self.nodePath, 0.8, colorScale = VBase4(0, 0, 0, 0),
                                                                startColorScale = VBase4(1, 1, 1, 1),
                                                                blendType = 'easeIn'),
                                         LerpColorScaleInterval(self.nodePath, 0.2, colorScale = VBase4(1, 1, 1, 1),
                                                                startColorScale = VBase4(0, 0, 0, 0),
                                                                blendType = 'easeOut'),
                                         name = self.uniqueName('treasureFlyTrack'))
        self.treasureFlyTrack.start()

    def handleGrab(self, avId):
        self.collNodePath.stash()
        self.avId = avId
        if avId in self.cr.doId2do:
            av = self.cr.doId2do[avId]
            self.av = av
        else:
            self.nodePath.detachNode()
            return
        if self.playSoundForRemoteToons or self.avId == base.localAvatar.getDoId():
            base.playSfx(self.grabSound, node = self.nodePath)
        if not self.fly:
            self.nodePath.detachNode()
            return
        self.nodePath.wrtReparentTo(av)
        if self.treasureFlyTrack:
            self.treasureFlyTrack.finish()
            self.treasureFlyTrack = None
        avatarGoneName = self.av.uniqueName('disable')
        self.accept(avatarGoneName, self.handleUnexpectedExit)
        flytime = 0.8
        track = Sequence(
            LerpPosInterval(self.nodePath, flytime, pos = Point3(0, 0, 3),
                            startPos = self.nodePath.getPos(), blendType = 'easeInOut'),
            LerpColorScaleInterval(self.nodePath, 0.2, (1, 1, 1, 0), blendType='easeInOut'),
            Func(self.nodePath.detachNode),
            Func(self.ignore, avatarGoneName)
        )
        if self.shadow:
            self.treasureFlyTrack = Sequence(HideInterval(self.dropShadow), track, ShowInterval(self.dropShadow),
                                             name = self.uniqueName('treasureFlyTrack'))
        else:
            self.treasureFlyTrack = Sequence(track, name = self.uniqueName('treasureFlyTrack'))
        self.stopAnimation()
        self.treasureFlyTrack.start()

    def handleUnexpectedExit(self):
        self.notify.warning('While getting treasure, ' + str(self.avId) + ' disconnected.')
        self.stopAnimation()
        if self.treasureFlyTrack:
            self.treasureFlyTrack.finish()
            self.treasureFlyTrack = None

    def getStareAtNodeAndOffset(self):
        return (self.nodePath, Point3())

    def startAnimation(self):
        initialPos = self.nodePath.getPos()
        if not self.bounceSequence:
            self.bounceSequence = Sequence(
                Parallel(
                    Sequence(
                        self.treasure.posInterval(1, (0, 0, 0.5), blendType = "easeInOut"),
                        self.treasure.posInterval(1, (0, 0, 0), blendType = "easeInOut"),
                        self.treasure.posInterval(1, (0, 0, 0.5), blendType = "easeInOut"),
                        self.treasure.posInterval(1, (0, 0, 0), blendType = "easeInOut"),
                    ),
                    self.treasure.hprInterval(4, (360, 0, 0))
                ),
            )
        self.bounceSequence.loop()

    def stopAnimation(self):
        if self.bounceSequence:
            self.bounceSequence.finish()
            self.bounceSequence = None
