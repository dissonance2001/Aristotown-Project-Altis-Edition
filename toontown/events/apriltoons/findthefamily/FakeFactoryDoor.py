"""
DistributedEntityDoor module: contains the DistributedCogHqDoor
class, the client side representation of a DistributedCogHqDoorAI.
"""

from panda3d.core import *
from direct.interval.IntervalGlobal import *
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from direct.fsm import FourState
from toontown.coghq.entities import DistributedDoorEntityBase


@DirectNotifyCategory()
class FakeFactoryDoor(DistributedDoorEntityBase.DistributedDoorEntityBase, NodePath, FourState.FourState):
    """
    FakeFactoryDoor

    A fake client side representation of a Cog HQ door.

    For the actual object that this is based off of, visit toontown.coghq.DistributedDoorEntity
    """
    stateDurations = [None, 3.0, 3.0, 3.0, None]

    def __init__(self, wantVoid=False):
        self.innerDoorsTrack = None
        self.isOuterDoorOpen = 0
        self.stateIndex = 0
        self.pos = (0, 0, 0)
        self.hpr = (0, 0, 0)
        self.wantVoid = wantVoid
        self.void = None

        FourState.FourState.__init__(self, self.stateNames, self.stateDurations)
        NodePath.__init__(self, f'fakeFactoryDoor-main-{id(self)}')
        # self.generate will be called automatically.
        self.setup()

    def cleanup(self):
        self.debugPrint("cleanup()")
        self.takedown()
        self.removeNode()

    def setup(self):
        self.setupDoor()

    def takedown(self):
        if self.track is not None:
            self.track.finish()
        self.track = None
        if self.innerDoorsTrack is not None:
            self.innerDoorsTrack.finish()
        self.innerDoorsTrack = None

        self.fsm = None
        for i in list(self.states.keys()):
            del self.states[i]

        self.states = []

        if self.void:
            self.void.removeNode()
            self.void = None

    def setupDoor(self):
        self.debugPrint("setupDoor()")
        model = loader.loadModel('phase_9/models/cogHQ/CogDoorHandShake')
        if model:
            doorway = model.find('**/Doorway1')

            rootNode = self.attachNewNode(self.getName() + '-root')
            change = rootNode.attachNewNode('changePos')
            # change.setPos(0.0, 0.0, 0.0)
            # change.setHpr(0.0, 0.0, 0.0)
            # change.setScale(0.5, 0.5, 0.5)
            # change.setColor(Vec4(1.0, 1.0, 1.0, 1.0))
            doorway.reparentTo(change)

            self.rootNode = rootNode
            self.rootNode.show()

            # Top Door:
            door = doorway.find('doortop')
            if door.isEmpty():  # Hack#*#
                self.debugPrint('doortop hack')
                door = doorway.attachNewNode('doortop')
                doorway.find('doortop1').reparentTo(door)
                doorway.find('doortop2').reparentTo(door)

            rootNode = self.attachNewNode(self.getName() + '-topDoor')

            change = rootNode.attachNewNode('changePos')
            # change.setPos(0.0, 0.0, 0.0)
            # change.setHpr(0.0, 0.0, 0.0)
            # change.setScale(1.0, 0.8, 1.0)
            # change.setColor(Vec4(0.9, 0.9, 0.9, 1.0))

            door.reparentTo(change)
            self.doorTop = rootNode
            self.doorTop.show()

            # Left Door:
            rootNode = self.doorTop.getParent().attachNewNode(self.getName() + '-leftDoor')
            change = rootNode.attachNewNode('change')
            door = doorway.find('**/doorLeft')
            door = door.reparentTo(change)

            self.doorLeft = rootNode
            self.doorLeft.show()

            # Bottom Door:
            door = doorway.find('doorbottom')
            if door.isEmpty():
                self.debugPrint('doorbottom hack')
                door = doorway.attachNewNode('doorbottom')
                doorway.find('doorbottom1').reparentTo(door)
                doorway.find('doorbottom2').reparentTo(door)

            change = render.attachNewNode('changePos')
            # change.setPos(0.0, 0.0, 0.0)
            # change.setHpr(0.0, 0.0, 0.0)
            # change.setScale(1.0, 0.8, 1.0)
            # change.setColor(Vec4(0.9, 0.9, 0.9, 1.0))

            door.reparentTo(change)

            rootNode = self.attachNewNode(self.getName() + '-bottomDoor')
            change.reparentTo(rootNode)

            self.doorBottom = rootNode
            self.doorBottom.show()

            # Right Door:
            rootNode = self.doorTop.getParent().attachNewNode(self.getName() + '-rightDoor')
            change = rootNode.attachNewNode('change')
            door = doorway.find('**/doorRight')
            door.reparentTo(change)

            self.doorRight = rootNode
            self.doorRight.show()

            # Name Collisions:
            collision = self.doorLeft.find('**/doorLeft_collision1')
            collision.setName(self.getName())
            collision = self.doorLeft.find('**/doorLeft_collision2')
            collision.setName(self.getName())
            collision = self.doorRight.find('**/doorRight_collision1')
            collision.setName(self.getName())
            collision = self.doorRight.find('**/doorRight_collision2')
            collision.setName(self.getName())
            collision = self.doorLeft.find('**/doorLeft_innerCollision')
            collision.setName(self.getName())
            self.leftInnerCollision = collision
            collision = self.doorRight.find('**/doorRight_innerCollision')
            collision.setName(self.getName())
            self.rightInnerCollision = collision

            """
            # Add Collision Flat:
            size = 15,.0
            cSphere = CollisionPolygon(
                Point3(-7.5,-3,15.0),
                Point3(7.5,-3,15.0),
                Point3(7.5,-3,0),
                Point3(-7.5,-3,0))
            cSphere.setTangible(0)
            cSphereNode = CollisionNode(self.getName())
            cSphereNode.addSolid(cSphere)
            cSphereNode.setFromCollideMask(BitMask32.allOff())
            cSphereNode.setIntoCollideMask(ToontownGlobals.WallBitmask)
            self.cSphereNodePath = self.rootNode.attachNewNode(cSphereNode)
            self.cSphereNodePath.show()
            """

            """
            radius = 8.0
            cSphere = CollisionSphere(0.0, 0.0, 0.0, radius)
            cSphere.setTangible(0)
            cSphereNode = CollisionNode(self.getName())
            cSphereNode.addSolid(cSphere)
            cSphereNode.setFromCollideMask(BitMask32.allOff())
            cSphereNode.setIntoCollideMask(ToontownGlobals.WallBitmask)
            self.cSphereNodePath = self.rootNode.attachNewNode(cSphereNode)
            """

            nodeList = (
                'Slide_One_Closed', 'Slide_One_Left_Open', 'Slide_One_Right_Open',
                'Slide_Two_Closed', 'Slide_Two_Left_Open', 'Slide_Two_Right_Open',
                'Slide_Three_Closed', 'Slide_Three_Left_Open', 'Slide_Three_Right_Open',
            )

            # We don't need the locks here so we can just go ahead and remove them
            for doorNode in nodeList:
                lockPiece = self.rootNode.find(f'**/{doorNode}')
                if lockPiece and not lockPiece.isEmpty():
                    lockPiece.removeNode()

            # Flatten for speed and to avoid scale changes when reparenting:
            self.rootNode.flattenMedium()
            self.doorTop.flattenMedium()
            self.doorBottom.flattenMedium()
            self.doorLeft.flattenMedium()
            self.doorRight.flattenMedium()

            if self.wantVoid:
                self.void = loader.loadModel('phase_9/models/cogHQ/cube_tenfoot')
                self.void.reparentTo(self.rootNode)
                self.void.setScale(1.4, 1.0, 1.425)
                self.void.setPos(-7, -10, 0)
                self.void.setColorScale(0, 0, 0, 1)

    def setInnerDoorsTrack(self, track):
        if self.innerDoorsTrack is not None:
            self.innerDoorsTrack.pause()
            self.innerDoorsTrack = None
        if track is not None:
            # The inner doors are local, so they start at 0.0.
            track.start(0.0)
            self.innerDoorsTrack = track
        return

    def openInnerDoors(self):
        """
        Animate the door opening.
        """
        if self.isOuterDoorOpen:
            self.debugPrint("openInnerDoors stage Two")
            duration = self.duration
            slideSfx = base.loader.loadSfx('phase_9/audio/sfx/CHQ_FACT_door_open_sliding.ogg')
            finalSfx = base.loader.loadSfx('phase_9/audio/sfx/CHQ_FACT_door_open_final.ogg')

            # Each door is 7.5 high, we move them a bit more and then hide them:
            moveDistance = 8.0
            self.setInnerDoorsTrack(
                Sequence(
                    Func(self.leftInnerCollision.unstash),
                    Func(self.rightInnerCollision.unstash),
                    Parallel(
                        SoundInterval(
                            slideSfx,
                            node=self.rootNode,
                            duration=duration * 0.4,
                            volume=0.8
                        ),
                        LerpPosInterval(
                            nodePath=self.doorLeft,
                            duration=duration * 0.4,
                            pos=Vec3(-moveDistance, 0.0, 0.0),
                            blendType='easeOut'
                        ),
                        LerpPosInterval(
                            nodePath=self.doorRight,
                            duration=duration * 0.4,
                            pos=Vec3(moveDistance, 0.0, 0.0),
                            blendType='easeOut'
                        ),
                        Sequence(
                            Wait(duration * 0.325),
                            SoundInterval(
                                finalSfx,
                                node=self.rootNode,
                                duration=0.6,
                                volume=0.8
                            )
                        )
                    ),
                    Func(self.doorLeft.stash),
                    Func(self.doorRight.stash)
                    # fyi: Wait(duration*.6),
                )
            )

    def closeInnerDoors(self):
        """
        Animate the door opening.
        """
        duration = self.duration
        slideSfx = base.loader.loadSfx('phase_9/audio/sfx/CHQ_FACT_door_open_sliding.ogg')
        finalSfx = base.loader.loadSfx('phase_9/audio/sfx/CHQ_FACT_door_open_final.ogg')

        # Each door is 7.5 high, we move them a bit more and then hide them:
        moveDistance = 8.0
        self.setInnerDoorsTrack(
            Sequence(
                Func(self.doorLeft.unstash),
                Func(self.doorRight.unstash),
                Parallel(
                    SoundInterval(
                        slideSfx,
                        node=self.rootNode,
                        duration=duration * 0.4,
                        volume=0.8
                    ),
                    LerpPosInterval(
                        nodePath=self.doorLeft,
                        duration=duration * 0.4,
                        pos=Vec3(0.0),
                        blendType='easeIn'
                    ),
                    LerpPosInterval(
                        nodePath=self.doorRight,
                        duration=duration * 0.4,
                        pos=Vec3(0.0),
                        blendType='easeIn'
                    ),
                    Sequence(
                        Wait(duration * 0.325),
                        SoundInterval(
                            finalSfx,
                            node=self.rootNode,
                            duration=0.6,
                            volume=0.8
                        )
                    )
                ),
                Func(self.leftInnerCollision.stash),
                Func(self.rightInnerCollision.stash)
                # fyi: Wait(duration*.6),
            )
        )

    def setisOuterDoorOpen(self, isOpen):
        """
        :type isOpen: bool
        """
        self.isOuterDoorOpen = isOpen

    def enterState1(self):
        """
        Animate the outer door opening.
        """
        self.debugPrint("enterState1(openingTrack)")
        FourState.FourState.enterState1(self)

        self.isOuterDoorOpen = 0
        duration = self.duration
        slideSfx = base.loader.loadSfx('phase_9/audio/sfx/CHQ_FACT_door_open_sliding.ogg')
        finalSfx = base.loader.loadSfx('phase_9/audio/sfx/CHQ_FACT_door_open_final.ogg')

        # Each door is 7.5 high, we move them a bit more and then hide them:
        moveDistance = 8.0

        self.setTrack(
            Sequence(
                Wait(duration * 0.1),
                Parallel(
                    SoundInterval(
                        slideSfx,
                        node=self.rootNode,
                        duration=duration * 0.4,
                        volume=0.8
                    ),
                    LerpPosInterval(
                        nodePath=self.doorTop,
                        duration=duration * 0.4,
                        pos=Vec3(0.0, 0.0, moveDistance),
                        blendType='easeOut'
                    ),
                    LerpPosInterval(
                        nodePath=self.doorBottom,
                        duration=duration * 0.4,
                        pos=Vec3(0.0, 0.0, -moveDistance),
                        blendType='easeOut'
                    ),
                    Sequence(
                        Wait(duration * 0.325),
                        SoundInterval(
                            finalSfx,
                            node=self.rootNode,
                            duration=0.6,
                            volume=0.8
                        )
                    )
                ),
                Func(self.doorTop.stash),
                Func(self.doorBottom.stash),
                Func(self.setisOuterDoorOpen, 1),
                Func(self.openInnerDoors)
                # fyi: Wait(duration*.5),
            )
        )

    def enterState2(self):
        """
        Setup the animation in the open position.
        """
        self.debugPrint("enterState2(openTrack)")
        FourState.FourState.enterState2(self)
        self.isOuterDoorOpen = 1
        self.setTrack(None)
        moveDistance = 7.5
        self.doorTop.setPos(Vec3(0.0, 0.0, moveDistance)),
        self.doorBottom.setPos(Vec3(0.0, 0.0, -moveDistance)),
        self.doorTop.stash()
        self.doorBottom.stash()
        self.setInnerDoorsTrack(None)
        self.doorLeft.setPos(Vec3(-moveDistance, 0.0, 0.0))
        self.doorRight.setPos(Vec3(moveDistance, 0.0, 0.0))
        self.doorLeft.stash()
        self.doorRight.stash()
        # else: let the pending unblock handle the doors.

    def exitState2(self):
        self.debugPrint("exitState2(exitOpenTrack)")
        FourState.FourState.exitState2(self)

    def enterState3(self):
        """
        Animate the door closing.
        """
        self.debugPrint("enterState3(closingTrack)")
        FourState.FourState.enterState3(self)
        duration = self.duration
        slideSfx = base.loader.loadSfx('phase_9/audio/sfx/CHQ_FACT_door_open_sliding.ogg')
        finalSfx = base.loader.loadSfx('phase_9/audio/sfx/CHQ_FACT_door_open_final.ogg')
        self.setTrack(
            Sequence(
                Wait(duration * 0.1),
                Func(self.closeInnerDoors),
                Wait(duration * 0.4),
                Func(self.doorTop.unstash),
                Func(self.doorBottom.unstash),
                Parallel(
                    SoundInterval(
                        slideSfx,
                        node=self.rootNode,
                        duration=duration * 0.4,
                        volume=0.8
                    ),
                    LerpPosInterval(
                        nodePath=self.doorTop,
                        duration=duration * 0.4,
                        pos=Vec3(0.0),
                        blendType='easeIn'
                    ),
                    LerpPosInterval(
                        nodePath=self.doorBottom,
                        duration=duration * 0.4,
                        pos=Vec3(0.0),
                        blendType='easeIn'
                    ),
                    Sequence(
                        Wait(duration * 0.325),
                        SoundInterval(
                            finalSfx,
                            node=self.rootNode,
                            duration=0.6,
                            volume=0.8)
                    )
                ),
                Func(self.setisOuterDoorOpen, 0)
                # fyi: Wait(duration*.1), # remaining time
            )
        )

    def enterState4(self):
        """
        Setup the animation in the closed position.
        """
        self.debugPrint("enterState4(closedTrack)")
        FourState.FourState.enterState4(self)
        self.setisOuterDoorOpen(0)
        self.setTrack(None)
        self.doorTop.unstash()
        self.doorBottom.unstash()
        self.doorTop.setPos(Vec3(0.0))
        self.doorBottom.setPos(Vec3(0.0))
        self.setInnerDoorsTrack(None)
        self.leftInnerCollision.stash()
        self.rightInnerCollision.stash()
        self.doorLeft.unstash()
        self.doorRight.unstash()
        self.doorLeft.setPos(Vec3(0.0))
        self.doorRight.setPos(Vec3(0.0))

    def debugPrint(self, message):
        """
        for debugging
        """
        if __debug__:
            self.notify.debug(str(self.__dict__.get('entId', '?')) + ' ' + message)
        return
